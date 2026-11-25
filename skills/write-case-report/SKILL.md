---
name: write-case-report
description: Use when the user wants the report for a finished or ongoing case written from its metadata and notes.
---

# Write a case report

1. Read `cases/<slug>/case.yaml` for `title`, `status`, `stack`, `tools`, `models`, `iterations`, `time_spent_hours` and `started`.
2. Read every note in `notes/inbox/` whose `case` equals the slug.
3. Open `docs/cases/<slug>/case-report.md`. If it does not exist, run `make new-case NAME=<slug> TITLE="<title>"` first; if that fails because `cases/<slug>` already exists, stop and ask the user instead of retrying. Follow the sections of `docs/case-report-template.md`.
4. Fill the report from the metadata and the notes. State only what the notes and `case.yaml` support, and mark gaps for the user instead of inventing them.
5. Set `status: used` on the notes that fed the report. Never modify `starred`.
6. Run `make results` and `make build`, then tell the user what is still missing.
