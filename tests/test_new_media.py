import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "media" / "shared"))

import init  # noqa: E402
import new_media  # noqa: E402
from formats import FORMATS  # noqa: E402


def make_tree(tmp):
    root = Path(tmp)
    for fmt in FORMATS:
        t = root / "media" / "shared" / "templates" / fmt
        (t / "narration").mkdir(parents=True)
        (t / "build.py").write_text('TITLE = "Research Template"\n', encoding="utf-8")
        (t / "meta.json").write_text(json.dumps({"id": "research-template-" + fmt}) + "\n", encoding="utf-8")
        (t / "narration" / "01-a.txt").write_text("Hello.\n", encoding="utf-8")
        (t / "package.json").write_text(
            json.dumps({"name": "research-template-<fmt>-<name>", "private": True}, indent=2) + "\n",
            encoding="utf-8")
    return root


def rel_files(base):
    return sorted(p.relative_to(base).as_posix() for p in base.rglob("*")
                  if p.is_file() and not new_media.is_generated(p.relative_to(base)))


def add_generated(project):
    for rel in ("index.html", "notes.html", "compositions/01-a.html", "styles/theme.css",
                "renders/x.mp4", "assets/audio/01-a.wav", "assets/captions/01-a.srt", "__pycache__/b.pyc"):
        f = project / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("generated", encoding="utf-8")


def make_example_tree(tmp):
    root = make_tree(tmp)
    for fmt in ("deck",):
        new_media.run(root, fmt, "example")
    for fmt in list(FORMATS):
        if fmt != "deck":
            shutil.rmtree(root / "media" / "shared" / "templates" / fmt)
    return root


def check_examples(case, root):
    """Every example matches its template (generated artifacts ignored), with <fmt>/<name>
    substituted in package.json. Once the repo is initialised (`.template-initialised`) nothing is
    checked: editing, adding or deleting examples is normal in a derived repo."""
    if (root / ".template-initialised").exists():
        return
    for tpl in sorted((root / "media" / "shared" / "templates").iterdir()):
        fmt = tpl.name
        ex = root / "media" / fmt / "example"
        case.assertTrue(tpl.is_dir() and ex.is_dir(), fmt)
        case.assertEqual(rel_files(tpl), rel_files(ex), fmt)
        for rel in rel_files(tpl):
            a = (tpl / rel).read_text(encoding="utf-8")
            if rel == "package.json":
                a = a.replace("<fmt>", fmt).replace("<name>", "example")
            case.assertEqual(a, (ex / rel).read_text(encoding="utf-8"), f"{fmt}/{rel}")


class NewMediaTest(unittest.TestCase):
    def test_new_media_copies_template(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_tree(tmp)
            out = new_media.run(root, "deck", "demo")
            self.assertEqual(out, root / "media" / "deck" / "demo")
            self.assertEqual((out / "build.py").read_text(encoding="utf-8"), 'TITLE = "Research Template"\n')
            self.assertTrue((out / "narration" / "01-a.txt").is_file())
            pkg = json.loads((out / "package.json").read_text(encoding="utf-8"))
            self.assertEqual(pkg["name"], "research-template-deck-demo")

    def test_new_media_after_init_uses_name_and_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_tree(tmp)
            (root / "mkdocs.yml").write_text("site_name: Research Template\n", encoding="utf-8")
            init.run(root, "demo-lab", 'Demo & "Q"')
            out = new_media.run(root, "deck", "main")
            self.assertEqual((out / "build.py").read_text(encoding="utf-8"), 'TITLE = "Demo & \\"Q\\""\n')
            self.assertEqual(json.loads((out / "package.json").read_text(encoding="utf-8"))["name"], "demo-lab-deck-main")
            self.assertEqual(json.loads((out / "meta.json").read_text(encoding="utf-8"))["id"], "demo-lab-deck")

    def test_new_media_before_init_keeps_sentinels(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_tree(tmp)
            out = new_media.run(root, "deck", "main")
            self.assertIn("Research Template", (out / "build.py").read_text(encoding="utf-8"))
            self.assertIn("research-template", (out / "meta.json").read_text(encoding="utf-8"))

    def test_new_media_unknown_format_exits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_tree(tmp)
            with self.assertRaises(SystemExit) as cm:
                new_media.run(root, "poster", "demo")
            self.assertIn("deck", str(cm.exception))
            self.assertFalse((root / "media" / "poster").exists())

    def test_new_media_existing_exits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_tree(tmp)
            new_media.run(root, "social", "demo")
            with self.assertRaises(SystemExit):
                new_media.run(root, "social", "demo")

    def test_new_media_bad_slug_exits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_tree(tmp)
            for bad in ("Bad", "a_b", "-a", "a--b", "", "../x"):
                with self.assertRaises(SystemExit):
                    new_media.run(root, "deck", bad)
            self.assertFalse((root / "media" / "deck").exists())

    def test_examples_match_templates(self):
        check_examples(self, ROOT)
        for fmt in FORMATS:
            tpl = ROOT / "media" / "shared" / "templates" / fmt
            self.assertTrue((tpl / "assets" / ".gitkeep").is_file(), fmt)
            self.assertTrue(list((tpl / "narration").glob("*.txt")), fmt)

    def test_new_media_skips_generated_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_tree(tmp)
            t = root / "media" / "shared" / "templates" / "deck"
            add_generated(t)
            out = new_media.run(root, "deck", "demo")
            self.assertEqual(rel_files(out), ["build.py", "meta.json", "narration/01-a.txt", "package.json"])

    def test_check_ignores_generated_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_example_tree(tmp)
            add_generated(root / "media" / "deck" / "example")
            check_examples(self, root)

    def test_check_initialised_checks_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_example_tree(tmp)
            (root / ".template-initialised").write_text("demo\nDemo\n", encoding="utf-8")
            ex = root / "media" / "deck" / "example"
            (ex / "build.py").write_text('TITLE = "Renamed"\n', encoding="utf-8")
            (ex / "narration" / "08-extra.txt").write_text("x", encoding="utf-8")
            check_examples(self, root)
            (ex / "narration" / "01-a.txt").unlink()
            check_examples(self, root)
            shutil.rmtree(ex)
            check_examples(self, root)

    def test_check_strict_without_marker_detects_divergence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_example_tree(tmp)
            (root / "media" / "deck" / "example" / "build.py").write_text("x", encoding="utf-8")
            with self.assertRaises(AssertionError):
                check_examples(self, root)


if __name__ == "__main__":
    unittest.main()
