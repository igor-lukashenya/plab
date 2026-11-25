# Git Conventions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enforce conventional branch names and Conventional Commits via a stdlib validator, git hooks, CI and agent instructions.

**Architecture:** One tested script (`scripts/gitcheck.py`) holds all rules; thin shell hooks and a CI job call it; `CLAUDE.md`/README document it. No Node toolchain.

**Tech Stack:** Python 3 stdlib, shell, GitHub Actions, Make.

**Spec:** `docs/superpowers/specs/2026-11-25-git-conventions-design.md`

## Global Constraints

- Types (branch and commit): `feat|fix|docs|refactor|test|chore|ci|build|perf|style|revert`.
- Branch: `main`, or `<type>/<description>` with description matching `[a-z0-9]+(-[a-z0-9]+)*`, at most 50 characters.
- Commit header: `type(scope)!: subject`; scope chars `[a-z0-9._/-]+` optional; `!` optional; subject non-empty, no trailing period; whole header at most 72 characters. Merge commits (`Merge `...), `Revert "` ... and `fixup!`/`squash!`/`amend!` headers pass.
- `SKIP_GITCHECK=1` in the environment makes every subcommand exit 0.
- Scripts follow repo conventions: stdlib only, `run(...)` plus `main()` with argparse, `SystemExit("message")` on user errors, utf-8 IO, tests resolve the repo root from `__file__`, `##` comment above every Make target, no research-specific words (`LLM|PoC|\.NET|meetup|talk|announcement|Opus|GPT|Copilot|SpecKit|ecommerce|fintech`).
- Work on branch `feat/git-conventions` (create it first). Conventional commit messages. No push, no merge into `main`, and no attribution lines in commits (owner setting). Never use `--no-verify`.

## Review Focus

- A `commit-msg` file contains `#` comment lines and a trailing newline: they must be ignored, and an all-comment/empty message is rejected.
- Header exactly 72 vs 73 characters, trailing period, uppercase type, empty subject, `feat!:` and `feat(a/b)!:`.
- PR title and branch name containing quotes, backticks or `$()` must not be executed by CI (passed through `env:`).
- Detached HEAD, `main`, and a brand-new repo with no commits must not break the checks or hooks.
- `fixup!`/`Merge branch`/`Revert "..."` messages pass; `SKIP_GITCHECK=1` bypasses all three subcommands and both hooks.

---

### Task 1: `scripts/gitcheck.py` (TDD)

**Files:**
- Create: `scripts/gitcheck.py`, `tests/test_gitcheck.py`

**Interfaces:**
- Produces: constants `TYPES: tuple[str, ...]`; functions `check_branch(name: str) -> None`, `check_header(text: str) -> None`, `check_message(text: str) -> None` (strips `#` comment lines and surrounding blank lines, checks the first remaining line as header, rejects an empty message), `check_commits(root: Path, rev_range: str) -> int` (runs `git log --format=%s` through `subprocess` with a list argv, checks every header, returns count), `main(argv=None)` with subcommands `branch [NAME]` (default: current branch via `git rev-parse --abbrev-ref HEAD`; `HEAD` or empty = detached/new repo = pass), `message FILE_OR_TEXT` (a path that exists is read, else treated as text), `commits RANGE`, `title TEXT`. Every check raises `SystemExit("<what is wrong>. Expected <rule>. Example: <valid example>")`.

- [ ] **Step 1: Failing tests** in `tests/test_gitcheck.py` (add `scripts/` to `sys.path` from `__file__`): `test_branch_valid` (`main`, `feat/note-search`, `fix/123-init-marker`), `test_branch_invalid` (`feature/x`, `feat/Note`, `feat/`, `feat/` + 51 chars, `Main`, `feat/a--b`, `wip`), `test_header_valid` (`feat: add x`, `fix(scope)!: y`, `feat(a/b): c`, `chore(deps.dev): d`), `test_header_invalid` (`Feat: x`, `feat:x`, `feat: `, `feat: x.`, `feat(): x`, `foo: x`, 73-char header fails while exactly 72 passes), `test_special_headers_pass` (`Merge branch 'x'`, `Revert "feat: x"`, `fixup! feat: x`, `squash! fix: y`), `test_message_ignores_comments_and_blank_lines`, `test_message_empty_or_only_comments_fails`, `test_skip_env_bypasses_all_subcommands` (`SKIP_GITCHECK=1` via `os.environ` patch, each subcommand returns without error on bad input), `test_commits_over_temp_repo` (temp `git init`, set user config inside the temp repo only, one good and one bad commit using `GIT_COMMITTER_*` env and `--no-verify`-free plain `git commit` with `core.hooksPath` unset, check the range raises naming the bad header), `test_branch_default_current_branch_in_temp_repo` (new repo without commits passes), `test_error_message_includes_example`.
- [ ] **Step 2:** `python3 -m unittest tests.test_gitcheck -v`. Expected: ImportError/ModuleNotFoundError.
- [ ] **Step 3:** Implement `scripts/gitcheck.py` per the interfaces; one compiled header regex built from `TYPES`; length check separate from the regex so the error says "header is N characters, maximum 72".
- [ ] **Step 4:** Run `python3 -m unittest discover -s tests` (all existing plus new tests pass, output pristine). Commit: `feat(scripts): add gitcheck validator for branches and commit messages`.

### Task 2: Hooks, `make hooks`, init and doctor integration

**Files:**
- Create: `.githooks/commit-msg`, `.githooks/pre-push`, `tests/test_githooks.py`
- Modify: `Makefile` (target `hooks`; `init` calls it), `scripts/init.py` only if the Makefile route is not enough, `scripts/doctor.py` and `tests/test_doctor.py` (optional check `git hooks` active)

**Interfaces:**
- Consumes: `scripts/gitcheck.py` CLI from Task 1.
- Produces: `.githooks/commit-msg` (executable, `#!/usr/bin/env sh`, locates the repo root with `git rev-parse --show-toplevel`, runs `python3 "$root/scripts/gitcheck.py" message "$1"`; exits 0 when `SKIP_GITCHECK=1`); `.githooks/pre-push` (runs `gitcheck.py branch` for the current branch; skips when pushing a delete or tags only is not required, keep it simple: checks the current branch); Make target `hooks` (`git config core.hooksPath .githooks`, only inside a git work tree; clear message otherwise); `make init` runs `hooks` after the init script succeeds when `.git` exists; doctor optional check `git hooks` ok when `git config core.hooksPath` equals `.githooks`, fix text `make hooks` (probe injectable like the other checks).

- [ ] **Step 1: Failing tests** in `tests/test_githooks.py` using a temp git repo (copy `scripts/gitcheck.py` and `.githooks/` in, `git config core.hooksPath .githooks`, set user config locally): `test_commit_msg_hook_rejects_bad_message`, `test_commit_msg_hook_accepts_good_message`, `test_commit_msg_hook_ignores_git_comment_lines`, `test_skip_env_allows_bad_message`, `test_pre_push_hook_rejects_bad_branch_name` (run the hook script directly on a branch `wip`), `test_hooks_are_executable` (mode bits on the real repo files), `test_make_hooks_sets_hookspath` (copy Makefile? no: run `make hooks` inside a temp git repo copy of the Makefile and `.githooks`, assert config). In `tests/test_doctor.py`: `test_doctor_hooks_check_optional` (missing hooks does not change exit code).
- [ ] **Step 2:** Run them; expected failures (missing files/targets).
- [ ] **Step 3:** Create the two hooks (`chmod +x`, make sure git records the exec bit: `git add --chmod=+x` is the executor's job at commit time) and the `hooks` target, wire `init`, add the doctor check.
- [ ] **Step 4:** Run `python3 -m unittest discover -s tests`; all pass. In a scratch copy: `make hooks`, then `git commit -m "bad message"` is rejected and `git commit -m "feat: ok"` succeeds. Commit: `feat(git): add commit-msg and pre-push hooks with make hooks`.

### Task 3: CI job and documentation

**Files:**
- Modify: `.github/workflows/ci.yml`, `CLAUDE.md` (AGENTS.md is a symlink), `README.md`, `tests/test_agent_docs.py` only if its target-name regex needs extending

**Interfaces:**
- Consumes: `gitcheck.py` subcommands `branch NAME`, `title TEXT`, `commits RANGE`.
- Produces: job `conventions` in `ci.yml` with `if: github.event_name == 'pull_request'`, `actions/checkout@v4` with `fetch-depth: 0`, `actions/setup-python@v5`; PR values passed ONLY through `env:` (`HEAD_REF: ${{ github.head_ref }}`, `PR_TITLE: ${{ github.event.pull_request.title }}`, `BASE_REF: ${{ github.base_ref }}`) and used as quoted shell variables (`"$HEAD_REF"`), commits checked as `origin/$BASE_REF..HEAD`; the existing jobs keep working (no change to their triggers). `CLAUDE.md` section "Git conventions": branch format, commit format with three valid and three invalid examples, squash-merge with PR-title rule, `make hooks`, `SKIP_GITCHECK` is for the owner only, agents never use `--no-verify`, create a conventionally named branch before committing and never commit on `main` unless the owner says so. README: short "Git conventions" section, `make hooks` in the quick start and the command table, and an optional note that a GitHub ruleset can enforce branch names server-side (no command applied automatically).

- [ ] **Step 1:** Edit `ci.yml` and the docs per the interfaces.
- [ ] **Step 2: Verify.** `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"`; `grep -n 'github.head_ref\|pull_request.title' .github/workflows/ci.yml` shows both only under `env:` (never inside a `run:` string); `python3 -m unittest discover -s tests` passes (the doc/target consistency test covers `make hooks`); `mkdocs build --strict` passes; leak grep clean.
- [ ] **Step 3:** Commit: `ci: add conventions job and document git conventions`.
