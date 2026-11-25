---
name: new-case
description: Use when the user starts investigating a new case and needs its folders and report scaffolded.
---

# Create a case

1. Choose a lowercase hyphenated slug and a human title.
2. Run `make new-case NAME=<slug> TITLE="<title>"`. Never create `cases/<slug>/` or `docs/cases/<slug>/` by hand.
3. Open `cases/<slug>/case.yaml` and fill in `stack`, `tools`, `models`, `iterations`, `time_spent_hours`, `started` and `status` as the user provides them. `status` is one of `planned|win|mixed|fail|manual`.
4. Run `make results` to refresh `docs/results.md`.
5. Tell the user the paths that were created.
