import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import init  # noqa: E402

TITLE_SENTINEL = "Research Template"
NAME_SENTINEL = "research-template"
MARKER = ".template-initialised"


def write(root, rel, text):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_root(tmp):
    root = Path(tmp)
    write(root, "mkdocs.yml", f"site_name: {TITLE_SENTINEL}\nnav: []\n")
    write(root, "README.md", f"# {TITLE_SENTINEL}\n\nSee {NAME_SENTINEL}.\n")
    write(root, "docs/index.md", f"# {TITLE_SENTINEL}\n")
    write(root, "media/README.md", f"{NAME_SENTINEL} media\n")
    write(root, "media/deck/example/build.py", f'TITLE = "{TITLE_SENTINEL}"\n')
    write(root, "media/deck/example/package.json", json.dumps({"name": f"{NAME_SENTINEL}-deck-example"}) + "\n")
    write(root, "media/deck/example/meta.json", json.dumps({"id": f"{NAME_SENTINEL}-deck"}) + "\n")
    write(root, "media/shared/templates/deck/build.py", f'TITLE = "{TITLE_SENTINEL}"\n')
    write(root, "notes/unlisted.md", f"{TITLE_SENTINEL} {NAME_SENTINEL}\n")
    return root


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


class InitTest(unittest.TestCase):
    def test_init_replaces_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            changed = init.run(root, "demo-research", "Demo Research")
            self.assertEqual(changed, sorted(changed))
            self.assertIn(MARKER, changed)
            self.assertEqual(yaml.safe_load((root / "mkdocs.yml").read_text(encoding="utf-8"))["site_name"], "Demo Research")
            self.assertEqual((root / "README.md").read_text(encoding="utf-8"), "# Demo Research\n\nSee demo-research.\n")
            self.assertEqual((root / "docs/index.md").read_text(encoding="utf-8"), "# Demo Research\n")
            self.assertEqual((root / "media/README.md").read_text(encoding="utf-8"), "demo-research media\n")
            self.assertEqual((root / "media/deck/example/build.py").read_text(encoding="utf-8"), 'TITLE = "Demo Research"\n')
            self.assertEqual(json.loads((root / "media/deck/example/package.json").read_text(encoding="utf-8"))["name"], "demo-research-deck-example")
            self.assertEqual(json.loads((root / "media/deck/example/meta.json").read_text(encoding="utf-8"))["id"], "demo-research-deck")
            self.assertTrue((root / MARKER).is_file())
            self.assertEqual(
                changed,
                sorted(["mkdocs.yml", "README.md", "docs/index.md", "media/README.md", "media/deck/example/build.py",
                        "media/deck/example/package.json", "media/deck/example/meta.json", MARKER]),
            )

    def test_init_marker_records_name_and_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            self.assertIsNone(init.read_marker(root))
            init.run(root, "demo", "Demo Title")
            self.assertEqual((root / MARKER).read_text(encoding="utf-8"), "demo\nDemo Title\n")
            self.assertEqual(init.read_marker(root), ("demo", "Demo Title"))
            with self.assertRaises(SystemExit):
                init.run(root, "other", "Other")

    def test_init_unlisted_files_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            before = snapshot(root)
            init.run(root, "demo", "Demo")
            for rel in ("notes/unlisted.md", "media/shared/templates/deck/build.py"):
                self.assertEqual((root / rel).read_bytes(), before[rel])

    def test_init_second_run_exits_and_changes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            init.run(root, "demo", "Demo")
            before = snapshot(root)
            with self.assertRaises(SystemExit):
                init.run(root, "other", "Other")
            self.assertEqual(snapshot(root), before)

    def test_init_title_with_special_characters_is_literal(self):
        title = 'R&D / "Ops"'
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            init.run(root, "demo", title)
            self.assertEqual((root / "README.md").read_text(encoding="utf-8"), f"# {title}\n\nSee demo.\n")
            self.assertEqual(yaml.safe_load((root / "mkdocs.yml").read_text(encoding="utf-8"))["site_name"], title)
            ns = {}
            exec((root / "media/deck/example/build.py").read_text(encoding="utf-8"), ns)
            self.assertEqual(ns["TITLE"], title)

    def test_init_bad_slug_exits(self):
        for bad in ("", "Bad Name", "UPPER", "-x", "x-", "a--b", "a_b", "a/b"):
            with tempfile.TemporaryDirectory() as tmp:
                root = make_root(tmp)
                before = snapshot(root)
                with self.assertRaises(SystemExit, msg=bad):
                    init.run(root, bad, "Title")
                self.assertEqual(snapshot(root), before)

    def test_init_bad_title_exits(self):
        for bad in ("", "  ", "two\nlines"):
            with tempfile.TemporaryDirectory() as tmp:
                root = make_root(tmp)
                before = snapshot(root)
                with self.assertRaises(SystemExit, msg=repr(bad)):
                    init.run(root, "demo", bad)
                self.assertEqual(snapshot(root), before)


if __name__ == "__main__":
    unittest.main()
