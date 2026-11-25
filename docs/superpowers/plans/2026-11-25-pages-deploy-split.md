# Pages Deploy Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the upload-to-deploy artifact race by splitting `pages.yml` into separate `build` and `deploy` jobs.

**Architecture:** `build` runs mkdocs and uploads the `github-pages` artifact; `deploy` (`needs: build`) only runs `actions/deploy-pages@v4`. Permissions are narrowed per job.

**Tech Stack:** GitHub Actions, MkDocs.

**Spec:** `docs/superpowers/specs/2026-11-25-pages-deploy-split-design.md`

## Global Constraints

- Trigger stays `push` to `main` only.
- Keep top-level `concurrency: group: pages`, `cancel-in-progress: true`.
- No retry logic.
- Branch `fix/pages-deploy-race`; Conventional Commit header of at most 72 chars; never commit on `main`; never use `--no-verify`.

## Review Focus

- Deploy job missing `id-token: write` or `pages: write` fails with an OIDC/permission error: the deploy job must carry both.
- Build job lacking `contents: read` cannot checkout: build must carry it.
- Page URL output must still come from the `deployment` step id, now inside the deploy job.

---

### Task 1: Split the workflow

**Files:**
- Modify: `.github/workflows/pages.yml`

**Interfaces:**
- Produces: jobs `build` and `deploy`; `deploy` has `needs: build`, `environment: {name: github-pages, url: ${{ steps.deployment.outputs.page_url }}}`, and a step `id: deployment` using `actions/deploy-pages@v4`.

- [ ] **Step 1: Create the branch from current HEAD**

Run: `git switch -c fix/pages-deploy-race`
Expected: `Switched to a new branch 'fix/pages-deploy-race'`. (Note: `main` may be ahead of the current branch; if the spec and plan commits are wanted in the PR, that is intended.)

- [ ] **Step 2: Edit `pages.yml`**

Remove the workflow-level `permissions`. Define `build` with `permissions: contents: read` and the existing steps from checkout through `upload-pages-artifact` (unchanged). Define `deploy` with `needs: build`, `permissions: {pages: write, id-token: write}`, the `environment` block moved from the old job, and a single `actions/deploy-pages@v4` step with `id: deployment`. Both jobs `runs-on: ubuntu-latest`.

- [ ] **Step 3: Validate the YAML**

Run: `python3 -c "import yaml,sys; d=yaml.safe_load(open('.github/workflows/pages.yml')); print(list(d['jobs']), d['jobs']['deploy']['needs'])"`
Expected: `['build', 'deploy'] build`

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/pages.yml docs/superpowers/specs/2026-11-25-pages-deploy-split-design.md docs/superpowers/plans/2026-11-25-pages-deploy-split.md
git commit -m "fix(ci): split pages build and deploy into separate jobs"
```
Expected: commit hooks pass.

- [ ] **Step 5: Verify after merge**

After the PR is squash-merged, run `gh run list --workflow=pages.yml --limit 3` and expect the new run to show `success`. Local verification is not possible.
