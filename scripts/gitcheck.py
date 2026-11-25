#!/usr/bin/env python3
"""Validate branch names and Conventional Commits headers (stdlib only).

Usage:
  gitcheck.py branch [NAME]        # default: the current branch
  gitcheck.py message FILE_OR_TEXT # a commit message file or literal text
  gitcheck.py commits RANGE        # every commit header in a git range
  gitcheck.py title TEXT           # a PR title (same rule as a commit header)

SKIP_GITCHECK=1 in the environment makes every subcommand pass (owner escape hatch).
"""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

TYPES = ("feat", "fix", "docs", "refactor", "test", "chore", "ci", "build", "perf", "style", "revert")
MAX_HEADER = 72
MAX_BRANCH_DESCRIPTION = 50

_TYPE_ALT = "|".join(TYPES)
BRANCH_RE = re.compile(rf"^(?:{_TYPE_ALT})/(?P<desc>[a-z0-9]+(?:-[a-z0-9]+)*)$")
HEADER_RE = re.compile(rf"^(?:{_TYPE_ALT})(?:\([a-z0-9._/-]+\))?!?: \S.*$")
SPECIAL_PREFIXES = ("Merge ", 'Revert "', "fixup! ", "squash! ", "amend! ")

BRANCH_RULE = f"'main' or '<type>/<kebab-description>' (description at most {MAX_BRANCH_DESCRIPTION} characters), type one of: {', '.join(TYPES)}"
BRANCH_EXAMPLE = "feat/note-search"
HEADER_RULE = f"'<type>(<scope>)!: <subject>' (scope and '!' optional, lowercase type, no trailing period, at most {MAX_HEADER} characters), type one of: {', '.join(TYPES)}"
HEADER_EXAMPLE = "feat(notes): add note search"


def _fail(what, rule, example):
    raise SystemExit(f"{what}. Expected {rule}. Example: {example}")


def check_branch(name):
    if name in ("main", "", "HEAD"):
        return
    m = BRANCH_RE.match(name)
    if not m:
        _fail(f"Branch name '{name}' is not valid", BRANCH_RULE, BRANCH_EXAMPLE)
    if len(m.group("desc")) > MAX_BRANCH_DESCRIPTION:
        _fail(f"Branch description is {len(m.group('desc'))} characters, maximum {MAX_BRANCH_DESCRIPTION}",
              BRANCH_RULE, BRANCH_EXAMPLE)


def check_header(text):
    header = text.strip("\r\n")
    if header.startswith(SPECIAL_PREFIXES):
        return
    if len(header) > MAX_HEADER:
        _fail(f"Commit header is {len(header)} characters, maximum {MAX_HEADER}: '{header}'",
              HEADER_RULE, HEADER_EXAMPLE)
    if header.endswith(".") or not HEADER_RE.match(header):
        _fail(f"Commit header '{header}' is not valid", HEADER_RULE, HEADER_EXAMPLE)


def check_message(text):
    lines = [ln for ln in text.splitlines() if not ln.startswith("#")]
    for ln in lines:
        if ln.strip():
            check_header(ln)
            return
    _fail("Commit message is empty", HEADER_RULE, HEADER_EXAMPLE)


def _git(root, *args):
    proc = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def check_commits(root, rev_range):
    headers = [h for h in _git(root, "log", "--format=%s", rev_range).splitlines() if h]
    for h in headers:
        check_header(h)
    return len(headers)


def current_branch(root):
    proc = subprocess.run(["git", "-C", str(root), "symbolic-ref", "--short", "-q", "HEAD"],
                          capture_output=True, text=True)
    return proc.stdout.strip()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("branch").add_argument("name", nargs="?")
    sub.add_parser("message").add_argument("text_or_file")
    sub.add_parser("commits").add_argument("range")
    sub.add_parser("title").add_argument("text")
    args = ap.parse_args(argv)
    if os.environ.get("SKIP_GITCHECK") == "1":
        return
    if args.cmd == "branch":
        check_branch(args.name if args.name is not None else current_branch(Path.cwd()))
    elif args.cmd == "message":
        p = Path(args.text_or_file)
        check_message(p.read_text(encoding="utf-8") if p.is_file() else args.text_or_file)
    elif args.cmd == "commits":
        n = check_commits(Path.cwd(), args.range)
        print(f"gitcheck: {n} commit header(s) ok")
    elif args.cmd == "title":
        check_header(args.text)


if __name__ == "__main__":
    sys.exit(main())
