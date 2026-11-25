# Tools prefer the repo-local .venv when it exists (created by make install).
MKDOCS := $(if $(wildcard .venv/bin/mkdocs),.venv/bin/mkdocs,mkdocs)
PYTHON := $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

# Single-quote a value for the shell (escapes embedded single quotes).
shq = '$(subst ','\'',$(1))'

HF_VERSION ?= 0.8.138
SLIDES_VENV := $(abspath media/.venv)

# Media project helpers. M=<format>/<name> names a project at media/<format>/<name>/.
MEDIA_DIR = media/$(M)
MEDIA_FORMAT = $(firstword $(subst /, ,$(M)))
media_require_m = $(if $(filter command line,$(origin M)),,$(error M is required: make $@ M=<format>/<name>, e.g. M=deck/demo))
# CAPTIONS/AUDIO count only when given on the command line with a value other than empty or 0.
media_on = $(if $(filter command line,$(origin $(1))),$(if $(filter-out 0,$($(1))),1))
media_build_cmd = $(PYTHON) $(MEDIA_DIR)/build.py $(if $(call media_on,CAPTIONS),--captions) $(if $(call media_on,AUDIO),--audio)
hf = npx --yes hyperframes@$(HF_VERSION)

.PHONY: install serve build clean test new-case new-media init note results doctor help slides-deps slides-venv slides-install media-audio media-captions media-build media-dev media-check media-render media-png media-pdf media-check-all

## Install MkDocs and dependencies (falls back to a local .venv if pip is externally managed)
install:
	pip install mkdocs mkdocs-material pyyaml || { python3 -m venv .venv && .venv/bin/pip install mkdocs mkdocs-material pyyaml; }

## Serve docs locally with live reload
serve:
	$(MKDOCS) serve

## Build static site to site/ directory
build:
	$(MKDOCS) build --strict

## Remove built site
clean:
	rm -rf site

## Run the unit tests
test:
	$(PYTHON) -m unittest discover -s tests -v

## Scaffold a case: make new-case NAME=my-case [TITLE="My Case"]
new-case:
	$(if $(filter command line,$(origin NAME)),,$(error NAME is required: make new-case NAME=my-case))
	$(PYTHON) scripts/new_case.py $(call shq,$(value NAME)) --title $(call shq,$(if $(filter command line,$(origin TITLE)),$(value TITLE),$(value NAME)))

## Scaffold a media project: make new-media FORMAT=deck NAME=my-deck
new-media:
	$(if $(filter command line,$(origin FORMAT)),,$(error FORMAT is required: make new-media FORMAT=deck NAME=my-deck))
	$(if $(filter command line,$(origin NAME)),,$(error NAME is required: make new-media FORMAT=deck NAME=my-deck))
	$(PYTHON) scripts/new_media.py $(call shq,$(value FORMAT)) $(call shq,$(value NAME))

## Make this template yours (once): make init NAME=my-research [TITLE="My Research"]
init:
	$(if $(filter command line,$(origin NAME)),,$(error NAME is required: make init NAME=my-research))
	INIT_NAME=$(call shq,$(value NAME)) INIT_TITLE=$(call shq,$(if $(filter command line,$(origin TITLE)),$(value TITLE),$(value NAME))) $(PYTHON) scripts/init.py

## Capture a note: make note TITLE="..." [TYPE=observation] [CASE=slug] [TAGS=a,b] [BODY="..."]
note:
	$(if $(filter command line,$(origin TITLE)),,$(error TITLE is required: make note TITLE="..."))
	NOTE_TITLE=$(call shq,$(value TITLE)) $(if $(filter command line,$(origin TYPE)),NOTE_TYPE=$(call shq,$(value TYPE))) $(if $(filter command line,$(origin CASE)),NOTE_CASE=$(call shq,$(value CASE))) $(if $(filter command line,$(origin TAGS)),NOTE_TAGS=$(call shq,$(value TAGS))) $(if $(filter command line,$(origin BODY)),NOTE_BODY=$(call shq,$(value BODY))) $(PYTHON) scripts/note.py

## Regenerate docs/results.md from cases/*/case.yaml
results:
	$(PYTHON) scripts/results.py

## Install system libs for Hyperframes rendering (Debian/Ubuntu/WSL, needs sudo)
slides-deps:
	sudo apt-get update && sudo apt-get install -y ffmpeg espeak-ng libnss3 libnspr4 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libdrm2 libxkbcommon0 libatspi2.0-0t64 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2t64 || sudo apt-get install -y ffmpeg espeak-ng libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libatspi2.0-0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2

## Create the Python venv in media/.venv used for local speech (Kokoro), whisper builds and PDF export
slides-venv:
	python3 -m venv $(SLIDES_VENV)
	$(SLIDES_VENV)/bin/pip install kokoro-onnx soundfile cmake img2pdf

## Warm up the Hyperframes CLI (npx caches the pinned version)
slides-install:
	$(hf) --version

## Build a media project: make media-build M=deck/demo [CAPTIONS=1] [AUDIO=1]
media-build:
	$(media_require_m)
	$(media_build_cmd)

## Hyperframes Studio preview of a media project: make media-dev M=deck/demo [CAPTIONS=1] [AUDIO=1]
media-dev:
	$(media_require_m)
	$(media_build_cmd)
	cd $(MEDIA_DIR) && $(hf) preview

## Build, then lint and validate a media project: make media-check M=deck/demo
media-check:
	$(media_require_m)
	$(media_build_cmd)
	cd $(MEDIA_DIR) && $(hf) check

## Build, render to MP4 in renders/, and always write the sidecar renders/<name>.srt: make media-render M=shorts/demo [CAPTIONS=1] [AUDIO=1]
media-render:
	$(media_require_m)
	$(media_build_cmd)
	cd $(MEDIA_DIR) && mkdir -p renders && $(hf) render -o renders/$(notdir $(M)).mp4
	$(PYTHON) media/shared/captions.py $(MEDIA_DIR) --sidecar $(MEDIA_DIR)/renders/$(notdir $(M)).srt

## Generate voiceover for this project only (Kokoro, needs slides-venv): make media-audio M=deck/demo
media-audio:
	$(media_require_m)
	test -x $(SLIDES_VENV)/bin/python || $(MAKE) slides-venv
	mkdir -p $(MEDIA_DIR)/assets/audio
	cd $(MEDIA_DIR) && for f in narration/*.txt; do [ -e "$$f" ] || { echo "no narration/*.txt in $(MEDIA_DIR)"; exit 0; }; n=$$(basename $$f .txt); \
	  HYPERFRAMES_PYTHON=$(SLIDES_VENV)/bin/python $(hf) tts $$f -o assets/audio/$$n.wav || exit 1; done

## Write assets/captions/*.srt from script timing, or from audio with FROM_AUDIO=1: make media-captions M=deck/demo [FROM_AUDIO=1]
media-captions:
	$(media_require_m)
	$(if $(call media_on,FROM_AUDIO),,$(PYTHON) media/shared/captions.py $(MEDIA_DIR))
	$(if $(call media_on,FROM_AUDIO),test -x $(SLIDES_VENV)/bin/python || $(MAKE) slides-venv)
	$(if $(call media_on,FROM_AUDIO),mkdir -p $(MEDIA_DIR)/assets/captions)
	$(if $(call media_on,FROM_AUDIO),cd $(MEDIA_DIR) && for f in assets/audio/*.wav; do [ -e "$$f" ] || { echo "no assets/audio/*.wav in $(MEDIA_DIR): run make media-audio first"; exit 1; }; n=$$(basename $$f .wav); \
	  PATH=$(SLIDES_VENV)/bin:$$PATH $(hf) transcribe $$f --to srt -o assets/captions/$$n.srt || exit 1; done)

## Build, then write one PNG still to renders/<name>.png: make media-png M=social/demo [AT=3.5]
media-png:
	$(media_require_m)
	$(media_build_cmd)
	cd $(MEDIA_DIR) && mkdir -p renders && $(hf) snapshot --at $(if $(filter command line,$(origin AT)),$(AT),3.5) --no-end --describe false -o renders/_snap && mv renders/_snap/frame-*.png renders/$(notdir $(M)).png && rm -rf renders/_snap

## Build, then export a deck as a PDF, one still per slide (deck format only): make media-pdf M=deck/demo
media-pdf:
	$(media_require_m)
	$(if $(filter deck,$(MEDIA_FORMAT)),,$(error media-pdf supports the deck format only, got "$(MEDIA_FORMAT)"))
	test -x $(SLIDES_VENV)/bin/python || $(MAKE) slides-venv
	$(PYTHON) $(MEDIA_DIR)/build.py
	cd $(MEDIA_DIR) && HF_VERSION=$(HF_VERSION) $(SLIDES_VENV)/bin/python ../../shared/export_pdf.py .

## Check every media project that has a build.py
media-check-all:
	@for b in media/*/*/build.py; do [ -e "$$b" ] || continue; \
	  m=$${b#media/}; m=$${m%/build.py}; echo "== $$m"; \
	  $(MAKE) --no-print-directory media-check M=$$m || exit 1; done

## Check the required and optional tools and print how to fix what is missing
doctor:
	HF_VERSION=$(HF_VERSION) $(PYTHON) scripts/doctor.py

## Show available targets
help:
	@grep -B1 -E '^[a-zA-Z0-9_-]+:' $(MAKEFILE_LIST) | awk '/^## /{d=substr($$0,4)} /^[a-zA-Z0-9_-]+:/{sub(/:.*/,""); if(d!="") printf "  %-20s %s\n", $$0, d; d=""}'
