#!/usr/bin/env python3
"""Export a deck as a PDF: one still per slide, no captions, no audio.

Usage: export_pdf.py <deck directory>, after that deck's build.py (make media-pdf does this).
Needs the Hyperframes CLI (npx), ffmpeg, and img2pdf in media/.venv (make slides-venv).
Output: <deck>/renders/<deck>_<timestamp>.pdf
"""
import datetime
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import img2pdf

SLIDES = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else sys.exit("Usage: export_pdf.py <deck directory>")
RENDERS = SLIDES / "renders"
HYPERFRAMES = "hyperframes@" + (os.environ.get("HF_VERSION") or sys.exit("HF_VERSION is not set; run via make media-pdf"))
CLIP = re.compile(
    r'data-composition-src="(compositions/[^"]+)"\s+'
    r'data-start="([\d.]+)"\s+data-duration="([\d.]+)"'
)
CAPTIONS = re.compile(r'\s*<div class="captions">.*?</div>', re.DOTALL)
IGNORE = shutil.ignore_patterns("renders", ".thumbnails", ".waveform-cache", ".hyperframes")


def slide_times(index_html):
    """One capture time per slide: late enough for entrance animations, before the slide ends."""
    times = []
    for _src, start, duration in CLIP.findall(index_html):
        start, duration = float(start), float(duration)
        times.append(start + min(duration - 1.0, 6.0))
    return times


def strip_captions(project):
    """Remove the narration caption boxes from the temporary copy."""
    for html in (project / "compositions").glob("*.html"):
        html.write_text(CAPTIONS.sub("", html.read_text(encoding="utf-8")), encoding="utf-8")


def main():
    index_html = (SLIDES / "index.html").read_text(encoding="utf-8")
    times = slide_times(index_html)
    if not times:
        sys.exit("No slides found in index.html; run build the deck first (make media-build M=deck/<name>).")

    work = Path(tempfile.mkdtemp(prefix="slides-pdf-"))
    try:
        project = work / "project"
        shutil.copytree(SLIDES, project, ignore=IGNORE)
        strip_captions(project)

        shots = work / "shots"
        at = ",".join(f"{t:.2f}" for t in times)
        subprocess.run(
            ["npx", "--yes", HYPERFRAMES, "snapshot", "-o", str(shots), "--at", at,
             "--no-end", "--describe", "false", str(project)],
            check=True,
        )

        pngs = sorted(shots.glob("frame-*.png"))
        if len(pngs) != len(times):
            sys.exit(f"Expected {len(times)} snapshots, got {len(pngs)}.")

        # JPEG keeps the PDF small; img2pdf embeds JPEG without re-encoding.
        jpgs = []
        for png in pngs:
            jpg = png.with_suffix(".jpg")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(png),
                            "-q:v", "2", str(jpg)], check=True)
            jpgs.append(str(jpg))

        # 16:9 widescreen page, matching the 1920x1080 slides.
        layout = img2pdf.get_layout_fun((img2pdf.in_to_pt(13.333), img2pdf.in_to_pt(7.5)))
        RENDERS.mkdir(exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        out = RENDERS / f"{SLIDES.name}_{stamp}.pdf"
        out.write_bytes(img2pdf.convert(jpgs, layout_fun=layout))
        print(f"Wrote {out} ({len(jpgs)} pages)")
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
