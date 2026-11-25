---
name: new-case
description: Use when the user starts investigating a new case and needs its folders and report scaffolded.
---

# Create a case

1. Choose a lowercase hyphenated slug and a human title.
2. Check that `docs/research-definition.md` states the question, scope, success criteria and baseline. If not, suggest filling it in before the first case.
3. Run `make new-case NAME=<slug> TITLE="<title>"`. Never create `cases/<slug>/` or `docs/cases/<slug>/` by hand.
4. Open `cases/<slug>/case.yaml` and fill in `stack`, `tools`, `models`, `iterations`, `time_spent_hours`, `started` and `status` as the user provides them. `status` is one of `planned|win|mixed|fail|manual`.
5. Run `make results` to refresh `docs/results.md`.
6. Tell the user the paths that were created.
