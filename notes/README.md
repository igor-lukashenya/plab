# Notes

Notes are short raw captures made while working: an observation, a question, a decision, a quote or a result. They are not published. Summaries built from them go into `docs/`.

Notes live in `notes/inbox/` as `YYYY-MM-DD-HHMM-slug.md`. See `_template.md` for the shape.

## Frontmatter

| Field | Meaning |
|-------|---------|
| `title` | Short title (quoted in YAML) |
| `date` | Capture time, `YYYY-MM-DD HH:MM` |
| `type` | `observation`, `question`, `decision`, `quote` or `result` |
| `case` | Optional case slug; must match a directory under `cases/` |
| `tags` | List of free-form tags |
| `status` | `raw` until used in a summary, then `used` |
| `starred` | `true` to mark a note as especially important (default `false`) |

## What makes a good note

- One idea per note, so it can be filed, found and reused on its own.
- A title that states the finding ("Second prompt cut retries from 5 to 1"), not a topic ("Prompts").
- The exact numbers, error text or quote, not a paraphrase.
- A link to the source or the run log, saved when you found it.
- Why it matters, in a sentence, and the reason behind any decision.
- Failures and dead ends too. Keep it rough: a note should take seconds.

## Capturing

- Make: `make note TITLE="Short title" [TYPE=observation] [CASE=my-case] [TAGS=a,b] [BODY="text"]`
- Multi-line body: `python3 scripts/note.py "Short title" --type observation --body-file - <<'EOF' ... EOF` (`--body-file PATH` reads a file, `-` reads stdin)
- The `note` skill captures a note from chat using `scripts/note.py`.
- By hand: copy `_template.md` into `notes/inbox/` and fill it in.

## How notes feed summaries

The `synthesize-notes` skill reads notes filtered by case or tag (all by default, only starred on request), drafts a section into the matching file in `docs/`, and sets the notes it used to `status: used`.
