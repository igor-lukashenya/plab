"""Make a fresh copy of this template your own: replace the placeholder title and name."""
import argparse
import json
import os
import re
from pathlib import Path

TITLE_SENTINEL = "Research Template"
NAME_SENTINEL = "research-template"
MARKER = ".template-initialised"
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Files rewritten by init. Templates under media/shared/templates/ are deliberately absent.
FIXED_TARGETS = ("mkdocs.yml", "README.md", "docs/index.md", "media/README.md")
GLOBS = ("media/*/*/build.py", "media/*/*/package.json", "media/*/*/meta.json")


def targets(root):
    found = {p for p in (root / t for t in FIXED_TARGETS) if p.is_file()}
    for pattern in GLOBS:
        found.update(p for p in root.glob(pattern) if p.is_file())
    shared = root / "media" / "shared"
    return sorted(p for p in found if shared not in p.parents)


def title_for(path, title):
    """Title as it must be written so the file stays valid (the replacement stays literal)."""
    if path.suffix == ".py":
        return title.replace("\\", "\\\\").replace('"', '\\"')
    if path.suffix == ".yml":
        return json.dumps(title, ensure_ascii=False)
    return title


def read_marker(root):
    """(name, title) recorded by init, or None when the repo is not initialised."""
    marker = Path(root) / MARKER
    if not marker.is_file():
        return None
    lines = marker.read_text(encoding="utf-8").split("\n")
    name = lines[0].strip()
    title = lines[1].strip() if len(lines) > 1 and lines[1].strip() else name
    return name, title


def run(root, name, title):
    root = Path(root)
    title = title.strip()
    if not SLUG_RE.match(name):
        raise SystemExit(f"Invalid name '{name}': use lowercase letters, digits and single hyphens")
    if not title or "\n" in title or "\r" in title:
        raise SystemExit("Title must be a non-empty single line")
    if (root / MARKER).exists():
        raise SystemExit(f"Already initialised: {MARKER} exists")

    updates = {}
    for path in targets(root):
        text = path.read_text(encoding="utf-8")
        new = text.replace(TITLE_SENTINEL, title_for(path, title)).replace(NAME_SENTINEL, name)
        if new != text:
            updates[path] = new
    for path, text in updates.items():
        path.write_text(text, encoding="utf-8")
    (root / MARKER).write_text(f"{name}\n{title}\n", encoding="utf-8")
    changed = [p.relative_to(root).as_posix() for p in updates] + [MARKER]
    return sorted(changed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", nargs="?", help="project slug (or env INIT_NAME)")
    parser.add_argument("--title", default=None, help="project title (or env INIT_TITLE); defaults to name")
    args = parser.parse_args()
    name = args.name if args.name is not None else os.environ.get("INIT_NAME", "")
    title = args.title if args.title is not None else os.environ.get("INIT_TITLE", "") or name
    root = Path(__file__).resolve().parent.parent
    for rel in run(root, name, title):
        print(f"updated {rel}")


if __name__ == "__main__":
    main()
