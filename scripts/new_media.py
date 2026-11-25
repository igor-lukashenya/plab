"""Scaffold a media project: media/<format>/<name>/ copied from media/shared/templates/<format>/."""
import argparse
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "media" / "shared"))
from formats import FORMATS  # noqa: E402
import init  # noqa: E402

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Generated artifacts (the same set .gitignore ignores for projects), as paths relative to a project.
GENERATED_TOP = {"index.html", "compositions", "styles", "notes.html", "renders"}
GENERATED_ASSETS = {"audio", "captions"}


def is_generated(rel):
    """True when a project-relative path is a build/render artifact, not template content."""
    parts = Path(rel).parts
    if "__pycache__" in parts:
        return True
    if parts and parts[0] in GENERATED_TOP:
        return True
    return len(parts) > 1 and parts[0] == "assets" and parts[1] in GENERATED_ASSETS


def _ignore(template):
    def ignore(directory, names):
        base = Path(directory).relative_to(template)
        return [n for n in names if is_generated(base / n)]
    return ignore


def run(root, fmt, name):
    root = Path(root)
    if fmt not in FORMATS:
        raise SystemExit(f"Unknown format '{fmt}': choose one of {', '.join(FORMATS)}")
    if not SLUG_RE.match(name):
        raise SystemExit(f"Invalid name '{name}': use lowercase letters, digits and single hyphens")
    template = root / "media" / "shared" / "templates" / fmt
    if not template.is_dir():
        raise SystemExit(f"Missing template: {template}")
    dest = root / "media" / fmt / name
    if dest.exists():
        raise SystemExit(f"Project media/{fmt}/{name} already exists")
    shutil.copytree(template, dest, ignore=_ignore(template))
    pkg = dest / "package.json"
    if pkg.is_file():
        text = pkg.read_text(encoding="utf-8").replace("<fmt>", fmt).replace("<name>", name)
        pkg.write_text(text, encoding="utf-8")
    # After `make init`, new projects take the repo's name and title instead of the sentinels.
    marker = init.read_marker(root)
    if marker:
        name_, title = marker
        for rel in ("build.py", "meta.json", "package.json"):
            path = dest / rel
            if path.is_file():
                text = path.read_text(encoding="utf-8")
                new = text.replace(init.TITLE_SENTINEL, init.title_for(path, title)).replace(init.NAME_SENTINEL, name_)
                if new != text:
                    path.write_text(new, encoding="utf-8")
    return dest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("format", help=f"one of: {', '.join(FORMATS)}")
    parser.add_argument("name", help="project slug, e.g. launch-teaser")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    dest = run(root, args.format, args.name)
    print(f"created {dest.relative_to(root)}")


if __name__ == "__main__":
    main()
