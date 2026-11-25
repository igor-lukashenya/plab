"""Shared build engine for Hyperframes media projects.

A project's build.py (media/<format>/<name>/build.py) defines slides with add(...) and calls
build(project_dir, **flags()). build() writes <project>/index.html and <project>/compositions/,
copies shared/theme.css to <project>/styles/ and, unless notes=False, writes notes.html.

Canvas size comes from formats.FORMATS[<format>], where <format> is the name of the project
folder's parent (media/shorts/teaser -> "shorts"). Pass fmt= to override.

Optional inputs per slide, picked up when present:
  narration/NN-name.txt      script (also used for generated captions)
  assets/audio/NN-name.wav   voiceover; slide length follows the audio. Ignored when older than the
                             script (stale); the slide then uses an estimated length
  assets/captions/NN-name.srt  subtitle cues; without it, cues are derived from the script
Flags: --captions adds the caption layer, --audio adds the voiceover elements. Default is clean.
"""
import math, os, re, shutil, sys, wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from formats import FORMATS

LEAD, TAIL = 0.6, 1.5  # seconds before narration starts / after it ends
WORDS_PER_SEC = 1.8    # used when a slide has a script but no fresh audio


def flags(argv=None):
    """The build.py command-line flags as build() keyword arguments."""
    argv = sys.argv if argv is None else argv
    return dict(captions="--captions" in argv, audio="--audio" in argv)


def audio_len(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()

def parse_srt(path):
    cues = []
    for block in re.split(r"\n\s*\n", open(path, encoding="utf-8").read().strip()):
        lines = block.strip().splitlines()
        m = next((re.match(r"(\d+):(\d+):(\d+)[,.](\d+) --> (\d+):(\d+):(\d+)[,.](\d+)", l) for l in lines if "-->" in l), None)
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        a = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        b = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        text = " ".join(l for l in lines if "-->" not in l and not l.strip().isdigit())
        cues.append((a, b, text))
    return cues

def derive_cues(text, duration, limit=80):
    """Split script into short chunks; time them proportionally to character count."""
    chunks = []
    for sent in re.split(r"(?<=[.!?])\s+", text.strip()):
        parts, cur = [], ""
        for piece in re.split(r"(?<=,)\s+", sent):
            if cur and len(cur) + len(piece) > limit:
                parts.append(cur); cur = piece
            else:
                cur = f"{cur} {piece}".strip()
        if cur:
            parts.append(cur)
        chunks += parts
    total = sum(len(c) for c in chunks) or 1
    t, cues = 0.0, []
    for c in chunks:
        d = duration * len(c) / total
        cues.append((t, t + d, c))
        t += d
    return cues

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

slides = []  # dict(name, section, dur, body, status)

def add(name, section, dur, body, status=""):
    slides.append(dict(name=name, section=section, dur=dur, body=body, status=status))

def ul(items):
    return '<ul class="points">' + "".join(f'<li class="a">{i}</li>' for i in items) + "</ul>"


def format_for(OUT, fmt=None):
    name = fmt or os.path.basename(os.path.dirname(os.path.abspath(OUT)))
    if name not in FORMATS:
        raise ValueError(f"Unknown format {name!r} for {OUT}; projects live in media/<format>/<name>/, "
                         f"formats: {', '.join(FORMATS)}")
    return FORMATS[name]


def build(OUT, notes=True, captions=False, audio=False, fmt=None):
    f = format_for(OUT, fmt)
    W, H = f.width, f.height
    os.makedirs(f"{OUT}/compositions", exist_ok=True)
    os.makedirs(f"{OUT}/styles", exist_ok=True)
    for old in os.listdir(f"{OUT}/compositions"):
        os.remove(f"{OUT}/compositions/{old}")
    shutil.copyfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "theme.css"), f"{OUT}/styles/theme.css")

    N = len(slides)
    t = 0
    hosts = []
    for i, s in enumerate(slides, 1):
        fid = f"{i:02d}-{s['name']}"
        cid = f"s{i:02d}-{s['name']}"
        fname = f"{fid}.html"
        wav = f"{OUT}/assets/audio/{fid}.wav"
        script = f"{OUT}/narration/{fid}.txt"
        srt = f"{OUT}/assets/captions/{fid}.srt"
        body, dur, caption_html, cue_js = s["body"], s["dur"], "", ""
        has_script = os.path.exists(script)
        fresh = os.path.exists(wav) and (not has_script or os.path.getmtime(wav) >= os.path.getmtime(script))
        text = open(script, encoding="utf-8").read() if has_script else ""
        adur = audio_len(wav) if fresh else (len(text.split()) / WORDS_PER_SEC if text else None)
        if adur:
            dur = math.ceil(LEAD + adur + TAIL)
        if adur and captions:
            cues = parse_srt(srt) if os.path.exists(srt) else (
                derive_cues(text, adur) if text else [])
            body = body.replace('class="slide', 'class="slide with-captions', 1)
            caption_html = '<div class="captions">' + "".join(f'<span class="cap">{esc(c[2])}</span>' for c in cues) + "</div>"
            cue_js = "".join(
                f'      tl.set(caps[{k}], {{ opacity: 1 }}, {LEAD + c[0]:.3f}).set(caps[{k}], {{ opacity: 0 }}, {LEAD + c[1]:.3f});\n'
                for k, c in enumerate(cues))
            cue_js = f'      const caps = gsap.utils.toArray("[data-composition-id=\\"{cid}\\"] .cap");\n' + cue_js
        footer = ""
        if s["section"]:
            footer = f'<div class="slide-footer"><span>{s["section"]}</span><span>{i} / {N}</span></div><div class="progress" style="width:{i/N*100:.1f}%"></div>'
        sel = f'[data-composition-id=\\"{cid}\\"] .a'
        html = f"""<template id="{cid}-template">
      <div data-composition-id="{cid}" data-width="{W}" data-height="{H}">
    {body}
        {footer}
        {caption_html}
        <script>
          window.__timelines = window.__timelines || {{}};
          const tl = gsap.timeline({{ paused: true }});
          tl.from("{sel}", {{ opacity: 0, y: 30, duration: 0.6, ease: "power3.out", stagger: 0.18 }}, 0.2);
    {cue_js}      window.__timelines["{cid}"] = tl;
        </script>
      </div>
    </template>
"""
        open(f"{OUT}/compositions/{fname}", "w", encoding="utf-8").write(html)
        hosts.append(
            f'      <div id="{cid}" data-composition-id="{cid}" class="clip" data-composition-src="compositions/{fname}"'
            f' data-start="{t}" data-duration="{dur}" data-track-index="0"></div>')
        if fresh and audio:
            hosts.append(
                f'      <audio id="audio-{cid}" src="assets/audio/{fid}.wav" data-start="{t + LEAD}"'
                f' data-duration="{adur:.3f}" data-track-index="1" data-volume="1"></audio>')
        t += dur

    idx = f"""<!doctype html>
    <html lang="en" data-resolution="{f.orientation}" data-format="{f.name}">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width={W}, height={H}" />
        <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
        <link rel="stylesheet" href="styles/theme.css" />
      </head>
      <body>
        <div
          id="root"
          data-composition-id="main"
          data-start="0"
          data-duration="{t}"
          data-width="{W}"
          data-height="{H}"
        >
""" + "\n".join(hosts) + """
        </div>
        <script>
          window.__timelines = window.__timelines || {};
          const tl = gsap.timeline({ paused: true });
          window.__timelines["main"] = tl;
          tl.seek(0);
        </script>
      </body>
    </html>
"""
    open(f"{OUT}/index.html", "w", encoding="utf-8").write(idx)

    mode = "+".join(m for m, on in (("captions", captions), ("audio", audio)) if on) or "clean"
    summary = f"{os.path.basename(os.path.abspath(OUT))} [{f.name} {W}x{H}] {N} slides, {t} seconds, {mode} build"
    if not notes:
        print(summary)
        return

    # ---- notes.html: the script, kept out of the slides ----
    def slide_title(body):
        m = re.search(r"<h[12][^>]*>(.*?)</h[12]>", body, re.DOTALL)
        return re.sub(r"<[^>]+>", "", m.group(1)).replace("&amp;", "&").strip() if m else ""

    blocks, clock = [], 0
    for i, s in enumerate(slides, 1):
        fid = f"{i:02d}-{s['name']}"
        script = f"{OUT}/narration/{fid}.txt"
        text = open(script, encoding="utf-8").read().strip() if os.path.exists(script) else ""
        words = len(text.split())
        mins = f"{int(clock // 60)}:{int(clock % 60):02d}"
        blocks.append(
            f'<section><div class="meta"><span class="n">{i}</span><span>{esc(s["section"] or "·")}</span><span>{mins}</span><span>{words} words</span></div>'
            f'<h2>{esc(slide_title(s["body"]) or s["name"])}</h2><p>{esc(text) or "<i>No script for this slide.</i>"}</p></section>')
        clock += (LEAD + words / WORDS_PER_SEC + TAIL) if text else s["dur"]
    open(f"{OUT}/notes.html", "w", encoding="utf-8").write(f"""<!doctype html>
    <html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Speaker notes</title>
    <style>
    body {{ margin: 0; background: #0b1020; color: #f1f4ff; font: 20px/1.55 Inter, "Segoe UI", system-ui, sans-serif; }}
    main {{ max-width: 900px; margin: 0 auto; padding: 32px 20px 80px; }}
    h1 {{ font-size: 28px; margin: 0 0 4px; }} .sub {{ color: #a9b4d6; margin-bottom: 32px; font-size: 16px; }}
    section {{ border: 1px solid #2a3560; background: #131a31; border-radius: 14px; padding: 18px 24px; margin-top: 16px; }}
    .meta {{ display: flex; gap: 16px; font-size: 13px; letter-spacing: .08em; text-transform: uppercase; color: #8d98bd; }}
    .n {{ color: #22d3c5; font-weight: 700; }} h2 {{ font-size: 22px; margin: 6px 0 8px; }} p {{ margin: 0; color: #dbe2fb; }}
    @media print {{ body {{ background: #fff; color: #000; }} section {{ background: #fff; border-color: #bbb; break-inside: avoid; }} p {{ color: #000; }} }}
    </style></head><body><main>
    <h1>Speaker notes</h1><p class="sub">{N} slides · about {int(clock // 60)} min at speaking pace · timestamps are estimates</p>
    {"".join(blocks)}
    </main></body></html>""")
    print(summary)
