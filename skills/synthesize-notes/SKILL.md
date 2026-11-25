---
name: synthesize-notes
description: Use when the user wants raw notes from notes/inbox turned into a written summary inside a docs/ file.
---

# Synthesize notes into a docs file

1. Ask for, or read from the request, the target file under `docs/` and the filter: a case slug, a tag, or both.
2. List the notes in `notes/inbox/*.md` and read their frontmatter (`case`, `tags`, `status`, `starred`).
3. Select every note matching the filter. Use all matching notes by default; keep only those with `starred: true` when the user asks for starred notes only.
4. Draft the section in the named `docs/` file from the selected notes. Edit the existing file in place and keep its other content. Group related notes, keep the facts, drop duplicates.
5. Set `status: used` in the frontmatter of every note that fed the draft. Never modify `starred`.
6. Run `make build` to confirm the site still builds.
7. Tell the user which notes were used and which file changed.
