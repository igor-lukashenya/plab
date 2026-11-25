---
name: note
description: Use when the user wants to capture an observation, question, decision, quote or result as a raw note while working.
---

# Capture a note

1. Pick a short single-line title and a type: `observation`, `question`, `decision`, `quote` or `result`.
2. If the note belongs to a case, check that `cases/<slug>/` exists. Use `make new-case` first if it does not.
3. Send the note with the script, passing the body on stdin so multi-line text, quotes and special characters arrive intact:

   ```sh
   python3 scripts/note.py "<title>" --type <type> [--case <slug>] [--tags a,b] --body-file - <<'EOF'
   <body, any number of lines>
   EOF
   ```

   `--type`, `--case`, `--tags` and the body are optional. For a one-line body, `make note TITLE="<title>" [TYPE=<type>] [CASE=<slug>] [TAGS=<a,b>] [BODY="<text>"]` also works.
4. Report the path of the file that was created in `notes/inbox/`.

Never create files in `notes/inbox/` by hand. Add `starred: true` to the frontmatter only when the user says the note is especially important.
