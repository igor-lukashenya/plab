import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
TITLES = ["x `id`", 'He said "hi"', "$HOME", "it's $(echo no) a; b"]


def make_copy(tmp):
    root = Path(tmp)
    shutil.copy(ROOT / "Makefile", root / "Makefile")
    shutil.copytree(ROOT / "scripts", root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    (root / "docs").mkdir()
    shutil.copy(ROOT / "docs" / "case-report-template.md", root / "docs" / "case-report-template.md")
    (root / "mkdocs.yml").write_text(
        "site_name: Research Template\nnav:\n  - Cases:\n      # new-case:insert\n", encoding="utf-8")
    return root


def make(root, *args):
    return subprocess.run(["make", "--no-print-directory", *args], cwd=root, capture_output=True,
                          text=True, timeout=60)


@unittest.skipUnless(shutil.which("make"), "make not installed")
class MakefileQuotingTest(unittest.TestCase):
    def test_new_case_title_arrives_literally(self):
        for i, title in enumerate(TITLES):
            with self.subTest(title=title), tempfile.TemporaryDirectory() as tmp:
                root = make_copy(tmp)
                r = make(root, f"NAME=case-{i}", f"TITLE={title}", "new-case")
                self.assertEqual(r.returncode, 0, r.stderr)
                data = yaml.safe_load((root / "cases" / f"case-{i}" / "case.yaml").read_text(encoding="utf-8"))
                self.assertEqual(data["title"], title)
                nav = yaml.safe_load((root / "mkdocs.yml").read_text(encoding="utf-8"))["nav"][0]["Cases"]
                self.assertEqual(list(nav[0]), [title])

    def test_new_case_title_defaults_to_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_copy(tmp)
            r = make(root, "NAME=plain-case", "new-case")
            self.assertEqual(r.returncode, 0, r.stderr)
            data = yaml.safe_load((root / "cases" / "plain-case" / "case.yaml").read_text(encoding="utf-8"))
            self.assertEqual(data["title"], "plain-case")

    def test_init_title_arrives_literally(self):
        for title in TITLES:
            with self.subTest(title=title), tempfile.TemporaryDirectory() as tmp:
                root = make_copy(tmp)
                r = make(root, "NAME=demo", f"TITLE={title}", "init")
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual(yaml.safe_load((root / "mkdocs.yml").read_text(encoding="utf-8"))["site_name"], title)
                self.assertEqual((root / ".template-initialised").read_text(encoding="utf-8"), f"demo\n{title}\n")

    def test_note_values_arrive_literally(self):
        for title in TITLES:
            with self.subTest(title=title), tempfile.TemporaryDirectory() as tmp:
                root = make_copy(tmp)
                (root / "cases" / "demo").mkdir(parents=True)
                r = make(root, f"TITLE={title}", "TYPE=quote", "CASE=demo", "TAGS=a,b", f"BODY=body {title}", "note")
                self.assertEqual(r.returncode, 0, r.stderr)
                (path,) = (root / "notes" / "inbox").glob("*.md")
                _, fm, body = path.read_text(encoding="utf-8").split("---\n", 2)
                data = yaml.safe_load(fm)
                self.assertEqual(data["title"], title)
                self.assertEqual((data["type"], data["case"], data["tags"]), ("quote", "demo", ["a", "b"]))
                self.assertEqual(body.strip(), f"body {title}")


if __name__ == "__main__":
    unittest.main()
