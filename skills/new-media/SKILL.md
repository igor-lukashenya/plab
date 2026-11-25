---
name: new-media
description: Use when the user wants a new media project (deck, invite, social, digest, shorts or explainer) scaffolded.
---

# Create a media project

1. Choose the format from `media/README.md` and a lowercase hyphenated name.
2. Run `make new-media FORMAT=<format> NAME=<name>`. Never create `media/<format>/<name>/` by hand.
3. Edit `media/<format>/<name>/build.py` to add scenes. Do not edit generated files (`index.html`, `compositions/`, `styles/theme.css`, `notes.html`).
4. If the `/hyperframes` skill is installed, invoke it before editing compositions.
5. Run `make media-check M=<format>/<name>` and fix every reported problem before calling the project done.
6. Captions and audio are off by default. Add `CAPTIONS=1` or `AUDIO=1` on the command line only when the user asks.
