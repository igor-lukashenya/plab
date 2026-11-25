# Research practice guide, design

Date: 2026-11-25
Status: draft, awaiting approval
Size: small change (docs and skill text only, no scripts)

## Intent and why

The template documents the mechanics (`make new-case`, `make note`, note frontmatter, the case
report template) but not the practice: how to frame a question, when to take notes, how to keep
sources, when a case is done. `docs/research-definition.md` and `docs/research-overview.md` are
one-line stubs. Newcomers and agents get the commands but not the habits. This change adds a
practical playbook of industry-standard research habits and makes agents apply it.

## Goals

- One readable guide, `docs/how-to-research.md`, covering the habits below with a worked example of a good note and a good source entry.
- A compact "Research practice" section in `CLAUDE.md` (`AGENTS.md` links to it) with the rules and the agent behaviour.
- `notes/README.md` gains "what makes a good note".
- The `note`, `new-case`, `write-case-report` and `synthesize-notes` skills gain short, concrete nudges.
- Agents prompt gently: suggest a note at a checkpoint, ask for a source link when a claim appears. They never create notes or sources silently.

## Non-goals

- No script, Makefile, note-frontmatter or test-contract changes.
- No `source` note type and no lint checks (see Next step).
- No research-specific content; the guide stays generic to the template.

## Anti-goals

- Advice so heavy that it slows capture; a note should still take seconds.
- Lab-science boilerplate that does not fit case-by-case tool or approach evaluation.
- Agent nagging: at most one suggestion per checkpoint, dropped if declined.

## Constraints

- `make build` is strict (broken links fail), so the guide must be in `mkdocs.yml` nav and its links must resolve.
- `docs/results.md` is generated; do not edit it.
- Never create case or note files by hand; examples show the `make` commands.
- Keep the existing tests (`tests/test_agent_docs.py` and others) passing.
- The guide uses the existing note types (`observation`, `question`, `decision`, `quote`, `result`) and `docs/references.md` for sources.

## Approaches

1. **A. One guide, short agent rules, skill nudges (chosen).** Smallest change, no code risk. Guidance is advice, not enforced.
2. B. Multi-page guide (Framing, Notes, Sources, Cases, Reporting). Easier to link to, but more files to keep consistent than the content needs.
3. C. A plus tooling (`source` note type, checks for cases with no notes or no report). Enforces the habits but touches scripts, tests and the frontmatter contract. Deferred.

The owner chose A.

## The habits the guide covers

1. **Frame first.** Question, scope, success criteria and the comparison baseline go into `docs/research-definition.md` before the first case.
2. **Note at checkpoints.** After each meaningful step: a run, a surprise, a dead end, a decision and its reason, a result with numbers. Record failures too. Rule of thumb: if you would forget it by tomorrow, note it.
3. **Keep sources.** Every claim gets a link saved when found, with the access date, in `docs/references.md`; the note body links to it. Mark what was verified first-hand and what was only read.
4. **Make runs reproducible.** Record versions, models, settings and exact prompts.
5. **Separate evidence from interpretation.** Notes hold what happened; conclusions live only in summaries and reports.
6. **Close each case on purpose.** Set `status`, write the report, synthesize its notes, then start the next case.
7. **Review at the end.** Check findings against the original question; state limits and bias risks.

## Files touched

| File | Change |
|------|--------|
| `docs/how-to-research.md` | New guide |
| `mkdocs.yml` | Add the guide to the Research nav |
| `docs/research-definition.md` | Replace the stub line with a pointer to the guide plus a short fill-in outline (question, scope, success criteria, baseline) |
| `CLAUDE.md` | New "Research practice" section |
| `notes/README.md` | "What makes a good note" |
| `skills/note`, `skills/new-case`, `skills/write-case-report`, `skills/synthesize-notes` (`SKILL.md`) | Short nudges |
| `README.md` | One line linking to the guide |

## Agent behaviour (goes into `CLAUDE.md`)

- At a checkpoint (a result, a decision, a dead end, a surprise), offer to capture a note with the `note` skill, once.
- When a claim rests on an external source, ask for the link and offer to add it to `docs/references.md`.
- Before closing a case, check that it has notes, a status and a report, and say what is missing.
- Keep evidence and interpretation apart when drafting summaries.

## Left to the builder

- Exact wording, headings and the worked examples.
- Whether the guide needs a short "quick checklist" box at the top (my suggestion: yes).
- How to phrase nudges so they stay one or two lines in each skill.

## Next step (not in scope)

Approach C as a follow-up once the guidance has had some use: a `source` note type and a check for cases without notes or reports.
