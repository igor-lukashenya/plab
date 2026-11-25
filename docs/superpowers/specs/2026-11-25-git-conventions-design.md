# Git conventions: branch names and Conventional Commits (short design)

Date: 2026-11-25
Status: draft, awaiting approval
Builds on: `2026-11-25-research-template-design.md`

## Intent and why

The template has no git rules. Humans and AI agents both create branches and commits in repos made
from it, so conventions must travel with the template, be enforced automatically and be known to
agents. Goal: readable history and branch lists, and a base for changelogs.

## Goals

- Branch names: `main`, or `<type>/<kebab-description>`, type in `feat|fix|docs|refactor|test|chore|ci|build|perf|style|revert`
  (description `[a-z0-9]+(-[a-z0-9]+)*`, e.g. `feat/note-search`, `fix/123-init-marker`).
- Commit messages: Conventional Commits 1.0: `type(scope)!: subject`, same type list, subject non-empty,
  header at most 72 characters, no trailing period. Merge commits and `fixup!`/`squash!` autosquash commits are allowed.
- Enforcement in three places: local git hooks, CI, and agent instructions.
- PRs are squash-merged and the PR title is the commit message, so the PR title is validated like a commit header.

## Non-goals / anti-goals

- No Node toolchain (no commitlint, husky, package.json).
- No GitHub ruleset in the template (settings do not travel with a template repo). A documented optional
  one-time `gh api` command may be offered in the README; nothing is applied automatically.
- Must not break a first commit in a fresh repo or `git rebase`/`merge` flows, and must not block with
  unclear messages: every rejection says what is wrong and shows a valid example.

## Approaches considered

1. In-repo hooks and CI, stdlib Python (chosen by the owner, with these defaults).
2. commitlint plus husky: rich presets but adds a JS toolchain to a Python/Make template.
3. GitHub rulesets only: server-side, but settings are not inherited by repos made from the template.

## Design

- `scripts/gitcheck.py`, stdlib only, `run(...)` plus `main()` like the other scripts. Subcommands:
  `branch [NAME]` (default current branch), `message FILE_OR_TEXT`, `commits BASE..HEAD` (every commit header
  in the range), `title TEXT` (PR title, same rule as a commit header). Errors are `SystemExit("message")`
  with the rule and an example. `SKIP_GITCHECK=1` in the environment makes every subcommand exit 0 (escape hatch).
  Detached HEAD and `main` pass the branch check. Only `main` is exempt from the type prefix.
- `.githooks/commit-msg` (validates the message file with `gitcheck.py message`) and `.githooks/pre-push`
  (validates the branch being pushed); both are thin shell wrappers that call the script and respect `SKIP_GITCHECK`.
- `make hooks` runs `git config core.hooksPath .githooks`. `make init` calls it; `make doctor` reports whether hooks are active (optional check).
- CI (`ci.yml`): new job `conventions` on pull_request: `gitcheck.py branch "$HEAD_REF"` (PR head branch name),
  `gitcheck.py title "$PR_TITLE"`, and `gitcheck.py commits origin/<base>..HEAD`. On push to `main` no branch check.
  PR values are passed via environment variables, never interpolated into the shell command.
- Docs: `CLAUDE.md` (so `AGENTS.md` too) gets a "Git conventions" section: branch format, commit format with
  examples, squash-merge and PR-title rule, never bypass hooks with `--no-verify` unless the owner asks, and
  one rule for agents: create a conventionally named branch before committing and never commit on `main`
  unless the owner says so. README gets a short "Git conventions" section and `make hooks`.
- Tests (`tests/test_gitcheck.py`): valid and invalid branch names, valid and invalid headers (type, scope,
  `!`, length 72/73, trailing period, empty subject, uppercase type), merge and `fixup!` pass, `SKIP_GITCHECK`,
  `commits` over a temp git repo, hook scripts exit codes via subprocess in a temp repo with `core.hooksPath`.
  `tests/test_agent_docs.py` already checks that documented `make` targets exist (covers `make hooks`).

## Builder decisions (my calls)

- Scope allowed characters: `[a-z0-9._/-]+`. Breaking marker `!` after the scope.
- The `revert` type matches git's default `Revert "..."` messages (allowed as written).
- Branch description length is capped at 50 characters.
- The pre-push hook checks only the branch name; the commit-msg hook handles messages.

## Left to the builder

Exact error wording, shell wrapper details, CI step layout, README wording.

## Verification

Unit tests pass; in a temp repo: a bad branch push and a bad commit message are rejected, a good ones accepted,
`SKIP_GITCHECK=1` bypasses; `make hooks` sets `core.hooksPath`; CI YAML parses; `mkdocs build --strict` and
the existing suite stay green; no research-specific words added.
