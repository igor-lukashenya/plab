import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import note  # noqa: E402

NOW = datetime(2026, 1, 2, 3, 4)


def split_frontmatter(text):
    _, fm, body = text.split("---\n", 2)
    return yaml.safe_load(fm), body


def make_root(tmp, cases=()):
    root = Path(tmp)
    for case in cases:
        (root / "cases" / case).mkdir(parents=True)
    return root


class NoteTest(unittest.TestCase):
    def test_note_writes_frontmatter_and_body(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp, ["demo"])
            path = note.run(root, "First Idea!", "question", "demo", ["a", "b"], "Some body", NOW)
            self.assertEqual(path, root / "notes/inbox/2026-01-02-0304-first-idea.md")
            data, body = split_frontmatter(path.read_text(encoding="utf-8"))
            self.assertEqual(data["title"], "First Idea!")
            self.assertEqual(data["type"], "question")
            self.assertEqual(data["case"], "demo")
            self.assertEqual(data["tags"], ["a", "b"])
            self.assertEqual(data["status"], "raw")
            self.assertIs(data["starred"], False)
            self.assertEqual(str(data["date"]), "2026-01-02 03:04")
            self.assertIn("Some body", body)

    def test_note_same_minute_collision_suffix(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            p1 = note.run(root, "Same", now=NOW)
            p2 = note.run(root, "Same", now=NOW)
            p3 = note.run(root, "Same", now=NOW)
            self.assertEqual(p1.name, "2026-01-02-0304-same.md")
            self.assertEqual(p2.name, "2026-01-02-0304-same-2.md")
            self.assertEqual(p3.name, "2026-01-02-0304-same-3.md")

    def test_note_unknown_case_exits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            with self.assertRaises(SystemExit):
                note.run(root, "X", case="nope", now=NOW)
            self.assertFalse((root / "notes").exists())

    def test_note_bad_type_exits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            with self.assertRaises(SystemExit):
                note.run(root, "X", type="rant", now=NOW)
            self.assertFalse((root / "notes").exists())

    def test_note_empty_title_exits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            with self.assertRaises(SystemExit):
                note.run(root, "   ", now=NOW)

    def test_note_title_with_colon_and_quotes_is_valid_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            title = 'He said: "no"'
            path = note.run(root, title, tags=["it's", "x: y"], now=NOW)
            data, _ = split_frontmatter(path.read_text(encoding="utf-8"))
            self.assertEqual(data["title"], title)
            self.assertEqual(data["tags"], ["it's", "x: y"])

    def run_main(self, root, argv, stdin=None, env=None):
        old = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("NOTE_")}
        os.environ.update(env or {})
        try:
            with redirect_stdout(io.StringIO()):
                note.main(argv, root=root, stdin=io.StringIO(stdin) if stdin is not None else None)
        finally:
            for k in [k for k in os.environ if k.startswith("NOTE_")]:
                del os.environ[k]
            os.environ.update(old)
        (path,) = (root / "notes" / "inbox").glob("*.md")
        return split_frontmatter(path.read_text(encoding="utf-8"))

    def test_body_file_reads_multiline_utf8(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            src = root / "body.txt"
            src.write_text("Line one: \u00e9\n\n- item \"two\"\n", encoding="utf-8")
            data, body = self.run_main(root, ["T", "--body-file", str(src)])
            self.assertEqual(data["title"], "T")
            self.assertEqual(body, "\nLine one: \u00e9\n\n- item \"two\"\n")

    def test_body_file_dash_reads_stdin(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            _, body = self.run_main(root, ["T", "--body-file", "-"], stdin="a\nb $HOME `x`\n")
            self.assertEqual(body, "\na\nb $HOME `x`\n")

    def test_body_and_body_file_are_exclusive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            with self.assertRaises(SystemExit):
                self.run_main(root, ["T", "--body", "x", "--body-file", "-"], stdin="y")

    def test_body_file_missing_exits_with_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            with self.assertRaises(SystemExit) as cm:
                note.main(["T", "--body-file", str(root / "nope.txt")], root=root)
            self.assertIn("nope.txt", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
