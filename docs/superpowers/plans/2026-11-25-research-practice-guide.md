# Research Practice Guide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a practical research playbook (guide, agent rules, note advice, skill nudges) so people and agents follow good research habits.

**Architecture:** Docs and skill text only. One guide page in the MkDocs nav, a compact "Research practice" section in `CLAUDE.md`, a "what makes a good note" section in `notes/README.md`, and one short nudge per workflow skill. One new test file keeps the pieces from drifting.

**Tech Stack:** Markdown, MkDocs (strict build), Python `unittest`.

**Spec:** `docs/superpowers/specs/2026-11-25-research-practice-guide-design.md`

## Global Constraints

- No script, Makefile, note-frontmatter or existing-test changes.
- Branch before committing: `docs/research-practice-guide`; never commit on `main`; never `--no-verify`. Commit headers are Conventional Commits, at most 72 characters.
- `make build` is strict: the guide must be in `mkdocs.yml` nav and every link in `docs/` must resolve. Do not link from `docs/` to files outside `docs/`.
- Do not edit `docs/results.md`. Do not create case or note files by hand.
- `CLAUDE.md` is the real file and `AGENTS.md` is a symlink to it: edit `CLAUDE.md` only, never replace the symlink.
- `tests/test_agent_docs.py` fails on any `make <word>` in `CLAUDE.md`, `README.md`, `notes/README.md` or a skill where `<word>` is not a Makefile target. Never write "make sure", "make a note", "make it" and similar; rephrase ("check that", "write a note").
- Use the existing note types (`observation`, `question`, `decision`, `quote`, `result`) and `docs/references.md` for sources. Generic wording only, no research-specific content.
- Agent nudges: at most one suggestion per checkpoint, dropped if declined; never create notes or sources silently.

## Review Focus

- A "make sure" or "make a note" phrase anywhere in `CLAUDE.md`, `notes/README.md` or a skill fails `test_make_targets_named_in_docs_exist`.
- A link from the guide to `notes/README.md` or any non-`docs/` path breaks `make build --strict`.
- Editing `CLAUDE.md` with a tool that rewrites `AGENTS.md` as a regular file breaks `test_agents_md_is_symlink_to_claude_md`.
- `mkdocs.yml` nav edited without keeping the single `# new-case:insert` marker breaks `test_nav_marker_present`.
- The guide mentions `make` targets that do not exist (for example a lint target); only real targets may appear.

---

### Task 1: The guide, nav entry and definition pointer

**Files:**
- Create: `docs/how-to-research.md`, `tests/test_research_guide.py`
- Modify: `mkdocs.yml` (Research nav), `docs/research-definition.md`, `README.md`

**Interfaces:**
- Produces: `docs/how-to-research.md` with H2 headings `Quick checklist`, `1. Frame first`, `2. Note at checkpoints`, `3. Keep sources`, `4. Make runs reproducible`, `5. Separate evidence from interpretation`, `6. Close each case on purpose`, `7. Review at the end`. Task 2 links to it by the path `docs/how-to-research.md`.

- [ ] **Step 1: Create the branch** `docs/research-practice-guide` from `main`.

- [ ] **Step 2: Write the failing test** in `tests/test_research_guide.py`, class `ResearchGuideTests`:
  - `test_guide_has_all_sections`: reads `docs/how-to-research.md` and asserts each of the eight H2 headings above is present.
  - `test_guide_in_nav`: `mkdocs.yml` contains `how-to-research.md`.
  - `test_definition_points_to_guide`: `docs/research-definition.md` contains `how-to-research.md`.
  - `test_readme_links_guide`: `README.md` contains `docs/how-to-research.md`.

- [ ] **Step 3: Run** `python3 -m unittest tests.test_research_guide -v`. Expected: 4 FAIL.

- [ ] **Step 4: Write `docs/how-to-research.md`.** Start with a one-paragraph intro, then `## Quick checklist` (a short checkbox list, one line per habit). Then one H2 per habit using the spec's seven habits ("The habits the guide covers"), each with 2 to 4 sentences of advice. Include:
  - Under habit 2, a worked example of a good note (a `result` note: title, body with the numbers, link to a source) shown as a fenced block, and the command to capture it with `make note TITLE=... TYPE=result CASE=...`. Tell the reader a note should take seconds.
  - Under habit 3, a worked example of a source entry for `docs/references.md` (title, URL, date accessed, one-line takeaway, "verified" or "read only"), and a pointer to `references.md` by relative link `references.md`.
  - Under habit 6, links to `case-report-template.md` and mention `make results`.
  - Under habit 1, point to `research-definition.md` by relative link.

- [ ] **Step 5: Modify** `mkdocs.yml` to add `- How to Research: how-to-research.md` as the first Research nav entry (keep the `# new-case:insert` marker untouched). Replace the stub line in `docs/research-definition.md` with a sentence pointing to `how-to-research.md` plus an outline to fill in: Question, Scope, Success criteria, Baseline, each with an empty bullet prompt. Add one line to `README.md` after the Quick start section linking `docs/how-to-research.md`.

- [ ] **Step 6: Run** `python3 -m unittest discover -s tests` then `make build`. Expected: all tests pass, build succeeds with no warnings.

- [ ] **Step 7: Commit** `docs(research): add how-to-research guide` (stage the five files).

### Task 2: Agent rules, note advice and skill nudges

**Files:**
- Modify: `CLAUDE.md`, `notes/README.md`, `skills/note/SKILL.md`, `skills/new-case/SKILL.md`, `skills/write-case-report/SKILL.md`, `skills/synthesize-notes/SKILL.md`
- Test: `tests/test_research_guide.py`

**Interfaces:**
- Consumes: `docs/how-to-research.md` from Task 1.

- [ ] **Step 1: Add failing tests** to `ResearchGuideTests`:
  - `test_claude_md_has_research_practice`: `CLAUDE.md` contains a `## Research practice` heading and the path `docs/how-to-research.md`.
  - `test_notes_readme_has_good_note_section`: `notes/README.md` contains `## What makes a good note`.
  - `test_skills_carry_nudges`: for each of the four skills, the text contains the word `suggest` (note, new-case) or the phrase `references.md` (write-case-report, synthesize-notes): assert per-skill, using `subTest`. Use these exact expectations: `note` contains `suggest`; `new-case` contains `research-definition.md`; `write-case-report` contains `references.md`; `synthesize-notes` contains `evidence`.

- [ ] **Step 2: Run** `python3 -m unittest tests.test_research_guide -v`. Expected: the 3 new tests FAIL.

- [ ] **Step 3: Edit `CLAUDE.md`** (use Edit, not Write, so the symlink stays valid): add `## Research practice` before `## Git conventions`. It states, in short bullets, the agent behaviour from the spec's "Agent behaviour" section, one bullet each: offer a note once at a checkpoint; ask for the link when a claim rests on an external source and offer to add it to `docs/references.md`; before closing a case check it has notes, a status and a report and say what is missing; keep evidence and interpretation apart in summaries. End with a pointer to `docs/how-to-research.md`.

- [ ] **Step 4: Edit `notes/README.md`:** add `## What makes a good note` after the frontmatter table: one idea per note, a title that states the finding, the numbers or exact text, a link to the source, and why it matters; note failures and decisions with their reason; it should take seconds. Do not link outside `notes/`.

- [ ] **Step 5: Edit the four skills,** one or two lines each, wording of your choice but containing the required token:
  - `note`: at a checkpoint (result, decision, dead end, surprise) suggest a note once; do not create it unless the user agrees.
  - `new-case`: before the first case, check that `docs/research-definition.md` states the question, scope, success criteria and baseline, and suggest filling it if not.
  - `write-case-report`: ask for the link behind any external claim and offer to add it to `docs/references.md`; flag a missing status, baseline or reproducibility detail instead of inventing it.
  - `synthesize-notes`: keep evidence (what the notes record) separate from interpretation in the drafted section.

- [ ] **Step 6: Run** `make test` and `make build`. Expected: all tests pass, strict build succeeds.

- [ ] **Step 7: Commit** `docs(agents): add research practice rules and skill nudges`.

### Task 3: Final check

- [ ] **Step 1: Verify** `AGENTS.md` is still a symlink (`ls -l AGENTS.md`), `git status` shows only the expected files, and `docs/results.md` is unchanged.
- [ ] **Step 2: Run** `make test` and `make build` once more; report the outputs.
