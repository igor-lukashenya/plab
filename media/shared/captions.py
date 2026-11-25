"""Subtitle files for a media project, timed from the script.

Library:
  write_srt(narration_dir, durations, out_dir) -> list[Path]
      One <name>.srt per narration/<name>.txt, cues from engine.derive_cues, timestamps start at 0
      (the start of that slide's narration). durations maps <name> to seconds; a missing name falls
      back to the script estimate (words / engine.WORDS_PER_SEC). No narration files: returns [] and
      creates nothing.

Command line (run from the repo root):
  python3 media/shared/captions.py <project_dir>
      Writes <project_dir>/assets/captions/*.srt. Slide length is the fresh assets/audio/<name>.wav
      length when there is one, otherwise the script estimate (the same rule the engine uses).
  python3 media/shared/captions.py <project_dir> --sidecar <file.srt>
      Writes one SRT for the whole video. Slide start times come from the built <project_dir>/index.html
      (data-start of each slide, plus the engine's LEAD); cues come from assets/captions/<name>.srt when
      present (for example transcribed), otherwise from the script. Build the project first.
"""
import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine  # noqa: E402


def fmt_ts(seconds):
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def srt_text(cues):
    return "".join(f"{i}\n{fmt_ts(a)} --> {fmt_ts(b)}\n{text}\n\n" for i, (a, b, text) in enumerate(cues, 1))


def write_srt(narration_dir, durations, out_dir):
    narration_dir, out_dir = Path(narration_dir), Path(out_dir)
    files = sorted(narration_dir.glob("*.txt")) if narration_dir.is_dir() else []
    if not files:
        return []
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        dur = durations.get(f.stem)
        if dur is None:
            dur = len(text.split()) / engine.WORDS_PER_SEC
        path = out_dir / f"{f.stem}.srt"
        path.write_text(srt_text(engine.derive_cues(text, dur)), encoding="utf-8")
        written.append(path)
    return written


def slide_durations(project):
    """Narration length per slide: fresh wav length, else the script estimate."""
    project = Path(project)
    durations = {}
    for f in sorted((project / "narration").glob("*.txt")):
        wav = project / "assets" / "audio" / f"{f.stem}.wav"
        if wav.exists() and wav.stat().st_mtime >= f.stat().st_mtime:
            durations[f.stem] = engine.audio_len(str(wav))
        else:
            durations[f.stem] = len(f.read_text(encoding="utf-8").split()) / engine.WORDS_PER_SEC
    return durations


def slide_starts(project):
    """{NN-name: start seconds} read from the built index.html (host ids look like sNN-name)."""
    index = Path(project) / "index.html"
    if not index.exists():
        raise SystemExit(f"{index} not found: build the project first (make media-build M=...)")
    html = index.read_text(encoding="utf-8")
    return {m.group(1): float(m.group(2))
            for m in re.finditer(r'id="s(\d\d-[^"]+)"[^>]*?data-start="([\d.]+)"', html)}


def write_sidecar(project, out_file):
    project, out_file = Path(project), Path(out_file)
    starts, durations = slide_starts(project), slide_durations(project)
    cues = []
    for name, start in sorted(starts.items(), key=lambda kv: kv[1]):
        script = project / "narration" / f"{name}.txt"
        srt = project / "assets" / "captions" / f"{name}.srt"
        if srt.exists():
            local = engine.parse_srt(str(srt))
        elif script.exists():
            local = engine.derive_cues(script.read_text(encoding="utf-8"), durations[name])
        else:
            continue
        cues += [(start + engine.LEAD + a, start + engine.LEAD + b, t) for a, b, t in local]
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(srt_text(cues), encoding="utf-8")
    return out_file, len(cues)


def run(project, sidecar=None):
    project = Path(project)
    if not project.is_dir():
        raise SystemExit(f"{project}: not a project directory")
    if sidecar:
        path, n = write_sidecar(project, sidecar)
        print(f"{path} ({n} cues)")
        return [path]
    paths = write_srt(project / "narration", slide_durations(project), project / "assets" / "captions")
    for p in paths:
        print(p)
    if not paths:
        print(f"{project}: no narration/*.txt, nothing to write")
    return paths


def main(argv=None):
    ap = argparse.ArgumentParser(description="Write SRT captions for a media project from script timing.")
    ap.add_argument("project", help="project directory, e.g. media/deck/demo")
    ap.add_argument("--sidecar", help="write one merged SRT for the whole video to this path")
    args = ap.parse_args(argv)
    run(args.project, args.sidecar)


if __name__ == "__main__":
    main()
