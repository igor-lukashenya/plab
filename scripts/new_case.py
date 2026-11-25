"""Scaffold a new case: cases/<name>/, its report page, and a nav entry."""
import argparse
import datetime
import json
import re
import shutil
from pathlib import Path

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MARKER = "      # new-case:insert"


def run(root, name, title):
    root = Path(root)
    if not SLUG_RE.match(name):
        raise SystemExit(f"Invalid case name '{name}': use lowercase letters, digits and single hyphens")
    title = title.strip()
    if not title or "\n" in title:
        raise SystemExit("Title must be a non-empty single line")
    case_dir = root / "cases" / name
    report = root / "docs" / "cases" / name / "case-report.md"
    if case_dir.exists() or report.parent.exists():
        raise SystemExit(f"Case '{name}' already exists")
    template = root / "docs" / "case-report-template.md"
    if not template.is_file():
        raise SystemExit(f"Missing template: {template}")
    mkdocs = root / "mkdocs.yml"
    if not mkdocs.is_file():
        raise SystemExit(f"Missing file: {mkdocs}")
    lines = mkdocs.read_text(encoding="utf-8").split("\n")
    if lines.count(MARKER) != 1:
        raise SystemExit("mkdocs.yml must contain exactly one '# new-case:insert' marker line")

    case_yaml = (
        f"title: {json.dumps(title, ensure_ascii=False)}\n"
        f"slug: {name}\n"
        "status: planned\n"
        'stack: ""\n'
        "tools: []\n"
        "models: []\n"
        "iterations: 0\n"
        "time_spent_hours: 0\n"
        f"started: {datetime.date.today().isoformat()}\n"
    )
    readme = f"# {title}\n\nWorking notes for this case. The report lives in docs/cases/{name}/case-report.md.\n"
    # Always quoted: bare titles such as Yes or 2024 would parse as a bool or a number.
    nav_line = f"      - {json.dumps(title, ensure_ascii=False)}: cases/{name}/case-report.md"
    lines.insert(lines.index(MARKER), nav_line)

    case_dir.mkdir(parents=True)
    report.parent.mkdir(parents=True)
    (case_dir / "case.yaml").write_text(case_yaml, encoding="utf-8")
    (case_dir / "README.md").write_text(readme, encoding="utf-8")
    shutil.copyfile(template, report)
    mkdocs.write_text("\n".join(lines), encoding="utf-8")
    return [
        f"cases/{name}/case.yaml",
        f"cases/{name}/README.md",
        f"docs/cases/{name}/case-report.md",
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="case slug, e.g. my-case")
    parser.add_argument("--title", help="display title (defaults to the name)")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    for path in run(root, args.name, args.title or args.name):
        print(f"created {path}")


if __name__ == "__main__":
    main()
