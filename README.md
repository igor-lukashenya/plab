# Research Template

A GitHub template for research projects: cases investigated one by one, notes taken along the way, summaries written from those notes, and media produced from the results.

## Use this template

1. In the original repository, open *Settings* and tick *Template repository*.
2. Click *Use this template* on GitHub and create your repository.
3. Clone it, then run `make install` and `make doctor`.
4. Make it yours once: `make init NAME=my-research TITLE="My Research"`.
5. To publish the docs, open *Settings -> Pages -> Source* and choose *GitHub Actions*.

## Quick start

```sh
make install                                   # MkDocs and dependencies
make doctor                                    # check required and optional tools
make init NAME=my-research TITLE="My Research"
make new-case NAME=first-case TITLE="First Case"
make note TITLE="Something I saw" CASE=first-case
make results                                   # refresh docs/results.md
make new-media FORMAT=deck NAME=overview
make serve                                     # docs at http://127.0.0.1:8000
```

- `make init`: replaces the placeholder name and title everywhere (run once).
- `make new-case`: creates `cases/<slug>/` and `docs/cases/<slug>/case-report.md`.
- `make note`: captures a raw note in `notes/inbox/`.
- `make new-media`: creates a media project at `media/<format>/<name>/`.
- `make results`: regenerates `docs/results.md` from `cases/*/case.yaml`.
- `make doctor`: reports missing tools and how to install them.

## Repository structure

```
├── cases/          # One folder per case (make new-case)
├── docs/           # Documentation (MkDocs source)
├── notes/          # Raw notes (make note)
├── prompts/        # Prompt library, one file per prompt
├── media/          # Decks, videos and stills
├── skills/         # Agent skills (also linked from .claude/skills/)
├── scripts/        # Helper scripts used by the Makefile
├── tests/          # Unit tests for the scripts
├── CLAUDE.md       # Agent instructions (AGENTS.md is a link to it)
├── mkdocs.yml
└── Makefile
```

## Requirements

- Required: Python 3, Node.js 22 or newer with `npx`, MkDocs (`make install`).
- Optional, for media rendering: `ffmpeg`, `espeak-ng` and the Chrome libraries (`make slides-deps` on Debian/Ubuntu/WSL).

`make doctor` checks all of them.

## Make targets

Run `make help` for the full, always current list.

| Command | Description |
|---------|-------------|
| `make install` | Install MkDocs and dependencies (uses a local `.venv` if pip is externally managed) |
| `make serve` | Serve docs locally with live reload at http://127.0.0.1:8000 |
| `make build` | Build static site to `site/` |
| `make clean` | Remove built site |
| `make test` | Run the unit tests |
| `make doctor` | Check tools and print how to fix what is missing |
| `make init NAME=... [TITLE=...]` | Make the template yours (once) |
| `make new-case NAME=... [TITLE=...]` | Scaffold a case |
| `make note TITLE=... [TYPE= CASE= TAGS= BODY=]` | Capture a note |
| `make results` | Regenerate `docs/results.md` |
| `make new-media FORMAT=... NAME=...` | Scaffold a media project |
| `make media-build M=<format>/<name>` | Build a media project (also `media-dev`, `media-check`, `media-render`, `media-png`, `media-pdf`, `media-audio`, `media-captions`, `media-check-all`) |
| `make slides-deps` / `slides-venv` / `slides-install` | System libraries, local speech venv, warm the Hyperframes CLI |
| `make help` | Show available targets |

See `media/README.md` for media formats and the project contract.
