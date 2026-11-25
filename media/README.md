# Media

Slides, videos and stills built with [Hyperframes](https://hyperframes.heygen.com). Every project is plain
Python plus HTML, built by one shared engine (`media/shared/`) and one shared theme.

## Formats

A project lives at `media/<format>/<name>/`. The format is the name of the folder it sits in.

| Format      | Size      | Kind   | Use                                 |
|-------------|-----------|--------|-------------------------------------|
| `deck`      | 1920x1080 | slides | Presentation, PDF export            |
| `invite`    | 1920x1080 | video  | Short teaser or invitation          |
| `social`    | 1080x1350 | still  | Portrait image for social feeds     |
| `digest`    | 1920x1080 | video  | Recap of findings                   |
| `shorts`    | 1080x1920 | video  | Vertical short-form video           |
| `explainer` | 1920x1080 | video  | Animated explanation of one concept |

The table is `media/shared/formats.py` (`FORMATS`), the single source of truth.

## How dimensions reach a project

The engine reads the format from the **parent folder name** of the project directory and looks it up in
`formats.FORMATS`. It writes the width and height into `index.html` and every composition, sets
`<html data-format="...">`, and the theme (`styles/theme.css`, copied from `shared/theme.css`) switches
`--w`, `--h`, the type scale and the safe margins with `[data-format="..."]` rules. A project never states
its own size. An unknown parent folder is an error. `build(..., fmt="shorts")` overrides the lookup.

## Project contract

`media/<format>/<name>/build.py`:

```python
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "shared"))
from engine import add, ul, esc, build, flags

add("title", "", 7, '<div class="slide slide-center"><h1 class="slide-display a">Title</h1></div>')
build(HERE, **flags())   # flags(): --captions, --audio
```

- Imports the engine from `../../shared` relative to `__file__`, and writes into its own directory
  (`index.html`, `compositions/`, `styles/`, `notes.html`).
- Accepts `--captions` and `--audio`. Without them the build is clean: no caption layer, no audio elements.
  `build(OUT, notes=True, captions=False, audio=False)`.
- `add(name, section, seconds, body_html)`: one scene. The `a` class marks elements that animate in.
- Optional per-slide inputs, numbered `NN-name`: `narration/NN-name.txt` (script), `assets/audio/NN-name.wav`
  (voiceover, slide length follows it), `assets/captions/NN-name.srt` (cues; derived from the script if absent).
- Hyperframes also needs `hyperframes.json` and `meta.json` in the project directory (the per-format
  templates provide them). Renders go to `renders/`.

## Approved finals: media/kit/

Approved final outputs are committed under `media/kit/`. Renders, audio and captions inside projects
(`renders/`, `assets/audio/`, `assets/captions/`) are git-ignored, so copy a render you approve into `media/kit/`.

## Make targets

All take `M=<format>/<name>`, for example `M=deck/demo`.

| Target | What it does |
|--------|--------------|
| `make media-build M=...` | Build the project (`CAPTIONS=1` adds captions, `AUDIO=1` adds voiceover) |
| `make media-dev M=...` | Build, then open the Hyperframes Studio preview |
| `make media-check M=...` | Build, then lint and validate |
| `make media-render M=...` | Build, then render an MP4 into `renders/` |
| `make media-png M=... [AT=3.5]` | Build, then write one still at `AT` seconds to `renders/<name>.png` |
| `make media-pdf M=deck/...` | Deck only: one still per slide as a PDF in `renders/`. Errors for other formats |
| `make media-audio M=...` | Voiceover for this project only: narration to `assets/audio/*.wav` (Kokoro, via `media/.venv`) |
| `make media-captions M=... [FROM_AUDIO=1]` | Write `assets/captions/*.srt` from script timing, or transcribe the audio with `FROM_AUDIO=1` |
| `make media-check-all` | Check every project that has a `build.py` |
| `make slides-deps` / `slides-venv` / `slides-install` | System libraries, `media/.venv`, warm the pinned CLI |

The Hyperframes version is pinned by `HF_VERSION` in the Makefile. PDF export needs `make slides-venv`.

## Captions and audio (optional tracks)

Both are off by default: a plain build or render has no caption layer and no audio. `CAPTIONS=1` and
`AUDIO=1` count only when given on the command line with a value other than empty or `0`.

```sh
make media-audio M=deck/demo                  # narration/*.txt -> assets/audio/*.wav (this project only)
make media-captions M=deck/demo               # assets/captions/*.srt, timed from the script
make media-captions M=deck/demo FROM_AUDIO=1  # instead transcribe assets/audio/*.wav (Whisper)
make media-build  M=deck/demo CAPTIONS=1 AUDIO=1   # burn captions in, add the voiceover
make media-render M=deck/demo CAPTIONS=1 AUDIO=1   # same, rendered to MP4
make media-render M=deck/demo                      # clean video, plus the sidecar renders/demo.srt
```

- `media-audio` needs the venv (`make slides-venv`, created on demand) and downloads the speech model on
  first use. Slide length then follows the audio. A wav older than its script is treated as stale and ignored.
- Script-timed captions come from `media/shared/captions.py`, which can also run directly:
  `python3 media/shared/captions.py media/deck/demo`. Slide length is the fresh wav length, else a
  words-per-second estimate. Cue times start at 0 for each slide's narration; the engine adds the lead-in.
- `FROM_AUDIO=1` follows the audio exactly, so use it for your own recordings or after `media-audio`.
- Every `media-render` also writes `renders/<name>.srt`, one subtitle file for the whole video, merged from
  the per-slide files (or the script when there are none), with or without `CAPTIONS=1`. Upload it next to the MP4.
- To switch off: omit `CAPTIONS=1` / `AUDIO=1` (or pass `0`). To drop stale tracks, delete `assets/audio/` or
  `assets/captions/` (both git-ignored, as are `renders/`).
