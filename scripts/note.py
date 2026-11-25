"""Capture a raw note into notes/inbox/ with YAML frontmatter."""
import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

TYPES = ("observation", "question", "decision", "quote", "result")
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def slugify(title):
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:60].strip("-") or "note"


def run(root, title, type="observation", case="", tags=(), body="", now=None):
    root = Path(root)
    title = title.strip()
    if not title or "\n" in title:
        raise SystemExit("Title must be a non-empty single line")
    if type not in TYPES:
        raise SystemExit(f"Invalid type '{type}': use one of {', '.join(TYPES)}")
    case = case.strip()
    if case and (not SLUG_RE.match(case) or not (root / "cases" / case).is_dir()):
        raise SystemExit(f"Unknown case '{case}': no directory cases/{case}/")
    tags = [t.strip() for t in tags if t.strip()]
    now = now or datetime.now()

    # json.dumps output is valid YAML (double-quoted scalars, flow sequences).
    frontmatter = (
        "---\n"
        f"title: {json.dumps(title, ensure_ascii=False)}\n"
        f"date: {json.dumps(now.strftime('%Y-%m-%d %H:%M'))}\n"
        f"type: {type}\n"
        f"case: {json.dumps(case)}\n"
        f"tags: {json.dumps(tags, ensure_ascii=False)}\n"
        "status: raw\n"
        "starred: false\n"
        "---\n\n"
    )
    inbox = root / "notes" / "inbox"
    base = f"{now.strftime('%Y-%m-%d-%H%M')}-{slugify(title)}"
    path = inbox / f"{base}.md"
    n = 2
    while path.exists():
        path = inbox / f"{base}-{n}.md"
        n += 1
    inbox.mkdir(parents=True, exist_ok=True)
    text = frontmatter + (body.strip() + "\n" if body.strip() else "")
    path.write_text(text, encoding="utf-8")
    return path


def read_body(path, stdin):
    """Body text from a file, or from stdin when path is '-' (utf-8)."""
    if path == "-":
        return stdin.read()
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise SystemExit(f"Cannot read body file '{path}': {exc}")


def main(argv=None, root=None, stdin=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("title", nargs="?", help="note title (or env NOTE_TITLE)")
    parser.add_argument("--type", default=None, help=f"one of: {', '.join(TYPES)}")
    parser.add_argument("--case", default=None, help="case slug (must exist under cases/)")
    parser.add_argument("--tags", default=None, help="comma-separated tags")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--body", default=None, help="note body")
    group.add_argument("--body-file", default=None, metavar="PATH", help="read the body from PATH ('-' = stdin), for multi-line notes")
    args = parser.parse_args(argv)
    env = os.environ.get
    title = args.title if args.title is not None else env("NOTE_TITLE", "")
    type_ = args.type or env("NOTE_TYPE") or "observation"
    case = args.case if args.case is not None else env("NOTE_CASE", "")
    tags = args.tags if args.tags is not None else env("NOTE_TAGS", "")
    if args.body_file is not None:
        body = read_body(args.body_file, stdin or sys.stdin)
    else:
        body = args.body if args.body is not None else env("NOTE_BODY", "")
    root = Path(root) if root else Path(__file__).resolve().parent.parent
    path = run(root, title, type_, case, tags.split(","), body)
    print(f"created {path.relative_to(root)}")


if __name__ == "__main__":
    main()
