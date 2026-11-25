# How to Research

A short playbook for running a research with this template. It covers habits that make findings trustworthy and easy to write up later. Follow it by hand, or let an agent follow it with you: the agent instructions in `CLAUDE.md` apply the same rules.

The commands are the easy part (`make new-case`, `make note`, `make results`). The habits below are what make the results worth reading.

## Quick checklist

- [ ] The question, scope, success criteria and baseline are written down before the first case.
- [ ] A note is captured after each meaningful step, failures included.
- [ ] Every external claim has a saved link, an access date and a "verified" or "read only" mark.
- [ ] Versions, models, settings and exact prompts are recorded for each run.
- [ ] Notes hold what happened; conclusions live only in summaries and reports.
- [ ] Each case is closed before the next starts: status set, report written, notes synthesized.
- [ ] Findings are checked against the original question, with limits and bias risks stated.

## 1. Frame first

Before the first case, fill in [Research Definition](research-definition.md):

- **Question:** what you want to find out, in one or two sentences.
- **Scope:** what is in, and what is deliberately out.
- **Success criteria:** how you will know a case worked, written before you see results.
- **Baseline:** what you compare against (a manual approach, a previous tool, a prior result).

Without a baseline, "it was fast" means nothing. Without criteria written in advance, it is easy to judge generously after the fact. Revise the definition when you learn something, and note the change as a `decision`.

## 2. Note at checkpoints

Do not wait for the end of a case to write things down. Capture a note after each meaningful step:

- a run finished, with its outcome (`result`);
- something surprised you (`observation`);
- you chose one option over another, and why (`decision`);
- something is unclear and needs follow-up (`question`);
- a dead end: what you tried, and why it failed.

Failures matter as much as wins; they are often what readers most need. A useful rule: if you would forget it by tomorrow, write a note. A note should take seconds, so keep it rough and specific.

A good `result` note states the finding in the title, gives the numbers, links the source and says why it matters:

```
title: "Second prompt cut retries from 5 to 1"
type: result
case: first-case

Run 3 used the restructured prompt (spec attached). 1 retry instead of 5
over 20 runs. Run log: https://example.com/run-3. Matters because the
first prompt's cost per success was too high to compare fairly.
```

Capture it with `make note TITLE="Second prompt cut retries from 5 to 1" TYPE=result CASE=first-case BODY="..."`. See the notes guide in the repository (`notes/README.md`) for all fields.

## 3. Keep sources

Save a link the moment you find it; finding it again later is slower than copying it now. Add each source to [References](references.md) and link to it from the note that uses it.

A good entry has a title, the URL, the date you accessed it, a one-line takeaway, and whether you verified the claim yourself or only read it:

```
- **Title of the page or paper**: https://example.com/page
  Accessed 2026-11-25. Takeaway: one sentence. Status: read only.
```

Prefer primary sources (documentation, papers, the tool itself) over summaries of them. When a claim matters to your conclusion, try to verify it yourself and mark it "verified".

## 4. Make runs reproducible

Someone else, or you in a month, should be able to repeat a case. For each run record:

- versions of tools, libraries and models;
- settings and parameters that changed behavior;
- the exact prompts or inputs, not a paraphrase;
- the date, because hosted tools change under you.

Put what is stable in `cases/<slug>/case.yaml` (stack, tools, models) and what varies per run in notes.

## 5. Separate evidence from interpretation

Notes record what happened: "the build failed twice with error X". Interpretations come later and live in summaries and reports: "the tool struggles with Y". Keeping them apart lets a reader (or you) check whether a conclusion is actually supported. When a summary draws on a note, the note should still read as plain fact.

## 6. Close each case on purpose

A case is done when you have deliberately closed it, not when you stop working on it:

1. Set `status` in `case.yaml` (`win`, `mixed`, `fail` or `manual`).
2. Write the case report from the [Case Report Template](case-report-template.md).
3. Synthesize the case's notes into the report; they are then marked `used`.
4. Run `make results` so the results table is current.

Then start the next case. Closing in order keeps the notes fresh in your mind and the evidence attached to the right case.

## 7. Review at the end

Before publishing, check the findings against the original question in the [Research Definition](research-definition.md):

- Did you answer the question, or a neighboring one?
- Do the results meet the success criteria you wrote at the start?
- What are the limits: few cases, one environment, one person's judgment?
- Where could bias have crept in (cases picked because they favored one approach, results judged after the fact)?

State the limits plainly in the report. A finding with honest limits is more useful than one that sounds certain.
