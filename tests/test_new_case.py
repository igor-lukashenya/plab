import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import new_case  # noqa: E402

MKDOCS = """nav:
  - Case Reports:
      - Cases Index: cases/index.md
      # new-case:insert
"""


def make_tree(tmp, mkdocs=MKDOCS):
    root = Path(tmp)
    (root / "docs").mkdir()
    (root / "docs" / "case-report-template.md").write_text("# Case Report: [Case Name]\n")
    (root / "mkdocs.yml").write_text(mkdocs)
    return root


class NewCaseTest(unittest.TestCase):
    def test_new_case_creates_files_and_nav(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_tree(tmp)
            created = new_case.run(root, "demo", "Demo")
            self.assertEqual(
                sorted(created),
                ["cases/demo/README.md", "cases/demo/case.yaml", "docs/cases/demo/case-report.md"],
            )
            yaml_text = (root / "cases/demo/case.yaml").read_text()
            self.assertIn("slug: demo", yaml_text)
            self.assertIn("status: planned", yaml_text)
            self.assertEqual(
                (root / "docs/cases/demo/case-report.md").read_text(),
                "# Case Report: [Case Name]\n",
            )
            lines = (root / "mkdocs.yml").read_text().splitlines()
            nav = '      - "Demo": cases/demo/case-report.md'
            marker = "      # new-case:insert"
            self.assertIn(nav, lines)
            self.assertEqual(lines.index(nav) + 1, lines.index(marker))
            self.assertLess(lines.index("      - Cases Index: cases/index.md"), lines.index(nav))

    def test_nav_title_stays_a_string(self):
        for title in ("Yes", "2024", "No"):
            with self.subTest(title=title), tempfile.TemporaryDirectory() as tmp:
                root = make_tree(tmp)
                new_case.run(root, "demo", title)
                nav = yaml.safe_load((root / "mkdocs.yml").read_text(encoding="utf-8"))["nav"][0]["Case Reports"]
                key = list(nav[1])[0]
                self.assertIsInstance(key, str)
                self.assertEqual(key, title)

    def test_new_case_duplicate_exits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_tree(tmp)
            new_case.run(root, "demo", "Demo")
            before = (root / "mkdocs.yml").read_text()
            with self.assertRaises(SystemExit):
                new_case.run(root, "demo", "Demo")
            self.assertEqual((root / "mkdocs.yml").read_text(), before)

    def test_new_case_bad_slug_exits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_tree(tmp)
            with self.assertRaises(SystemExit):
                new_case.run(root, "My Case", "My Case")
            self.assertFalse((root / "cases").exists())

    def test_new_case_missing_marker_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_tree(tmp, mkdocs="nav:\n  - Home: index.md\n")
            with self.assertRaises(SystemExit):
                new_case.run(root, "demo", "Demo")
            self.assertFalse((root / "cases").exists())
            self.assertFalse((root / "docs" / "cases").exists())
            self.assertEqual((root / "mkdocs.yml").read_text(), "nav:\n  - Home: index.md\n")


if __name__ == "__main__":
    unittest.main()
