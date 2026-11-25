import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import results  # noqa: E402


def write_case(root, slug, **overrides):
    data = {
        "title": slug.title(),
        "slug": slug,
        "status": "planned",
        "stack": "",
        "tools": [],
        "models": [],
        "iterations": 0,
        "time_spent_hours": 0,
    }
    data.update(overrides)
    d = Path(root) / "cases" / slug
    d.mkdir(parents=True)
    lines = []
    for k, v in data.items():
        if v is None:
            continue
        lines.append(f"{k}: {v!r}" if isinstance(v, (list, str)) else f"{k}: {v}")
    (d / "case.yaml").write_text("\n".join(lines) + "\n")


class ResultsTest(unittest.TestCase):
    def test_results_empty_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "docs").mkdir()
            text = results.run(Path(tmp))
            self.assertIn("| Case |", text)
            self.assertEqual((Path(tmp) / "docs/results.md").read_text(), text)

    def test_results_table_sorted_and_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "docs").mkdir()
            write_case(tmp, "zeta", title="Zeta", status="win", models=["m1", "m2"], iterations=3, time_spent_hours=2.5)
            write_case(tmp, "alpha", title="Alpha", status="win", stack="py")
            write_case(tmp, "mid", title="Mid", status="fail")
            text = results.run(Path(tmp))
            self.assertLess(text.index("[Alpha]"), text.index("[Mid]"))
            self.assertLess(text.index("[Mid]"), text.index("[Zeta]"))
            self.assertIn("(cases/zeta/case-report.md)", text)
            self.assertIn("| m1, m2 |", text)
            self.assertIn("win: 2", text)
            self.assertIn("fail: 1", text)

    def test_results_bad_status_exits(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "docs").mkdir()
            write_case(tmp, "demo", status="great")
            with self.assertRaises(SystemExit):
                results.run(Path(tmp))
            self.assertFalse((Path(tmp) / "docs/results.md").exists())

    def test_results_missing_field_exits(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "docs").mkdir()
            write_case(tmp, "demo", stack=None)
            with self.assertRaises(SystemExit):
                results.run(Path(tmp))


if __name__ == "__main__":
    unittest.main()
