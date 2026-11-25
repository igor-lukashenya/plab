# Pages deploy: split build and deploy jobs

## Intent and why

`.github/workflows/pages.yml` fails intermittently at `actions/deploy-pages@v4`. In run 45652949090 the artifact was finalized at 16:22:39.61 and deploy-pages listed artifacts at 16:22:40.01 and found 0, so the failure is a race between upload and lookup. The workflow builds, uploads and deploys as steps in a single job, so deploy asks for the artifact immediately after upload. Putting deploy in its own job gives the artifact time to become visible.

## Goals

- Remove the artifact-not-found race by splitting into a `build` job and a `deploy` job with `needs: build`.
- Follow GitHub's standard Pages workflow layout.

## Non-goals

- No retry logic. The separate "Deployment failed, try again later" error is a different, transient platform failure; it is left for now and may be revisited.
- No changes to triggers, concurrency, mkdocs build, or the Pages settings.

## Anti-goals

- Must not change what gets published or when (still push to `main` only).

## Constraints

- Branch and commit conventions from `CLAUDE.md`: a new branch such as `fix/pages-deploy-race`, Conventional Commit header, never on `main`.

## Approaches considered

1. Split jobs (chosen by the owner).
2. Split jobs plus a retry on deploy: more YAML, covers the transient error too. Deferred by the owner.
3. Do nothing and re-run by hand: fails most of the time on current evidence.

## Design

- `build` job: `permissions: contents: read`; checkout, setup-python, pip install, `mkdocs build --strict`, `configure-pages`, `upload-pages-artifact` (path `site`).
- `deploy` job: `needs: build`; `permissions: pages: write, id-token: write`; `environment: github-pages` with the page URL output; a single `actions/deploy-pages@v4` step.
- Keep the top-level `concurrency` group `pages` with `cancel-in-progress: true`.
- Narrow permissions per job as above instead of workflow-wide (my call; matches the standard template).

## Left to the builder

- Verification: after merge, watch the next Pages run on `main`; a local run is not possible. Check YAML validity with a linter or `gh workflow view`.
