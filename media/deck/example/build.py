"""Deck template: seven placeholder slides. Replace the copy, keep the helpers.

Usage (from the repo root): make media-build M=deck/<name>   (add CAPTIONS=1 or AUDIO=1)
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "shared"))
from engine import add, ul, esc, build, flags

# ---- Config ----
TITLE = "Research Template"
SUBTITLE = "Placeholder headline"
DATE = "Month YYYY"
AGENDA = ["Introduction", "Approach", "Findings", "Next steps"]
PILLS = {"win": ("Worked", "success"), "mixed": ("Partly", "warning"), "fail": ("Broke", "danger")}


# ---- Helpers ----
def divider(name, part, title, so_far, nxt, nxt_sub, now):
    """Section divider: what is done, what comes next, agenda strip with the current item marked."""
    chips = "".join(
        f'<div class="agenda-item{" is-now" if i == now else (" is-done" if i < now else "")}">{i+1} · {t}</div>'
        for i, t in enumerate(AGENDA))
    add(name, AGENDA[now], 10, f"""
<div class="slide">
  <p class="slide-eyebrow a">Part {part}</p>
  <h2 class="slide-title a" style="margin-top:var(--space-2)">{title}</h2>
  <div class="row grow" style="margin-top:var(--space-4)">
    <div class="col card a stack-3"><p class="card-title">So far</p>{ul(so_far)}</div>
    <div class="col card card-top a" style="--status:var(--accent);display:flex;flex-direction:column;justify-content:center">
      <p class="num-badge">NEXT</p><p class="slide-heading" style="margin-top:var(--space-2)">{nxt}</p>
      <p class="slide-body" style="margin-top:var(--space-3)">{nxt_sub}</p></div>
  </div>
  <div class="agenda a" style="margin-top:var(--space-4)">{chips}</div>
</div>""")


def shot(src, cap, style=""):
    """A screenshot with a caption. Put the image in assets/screens/."""
    return (f'<div class="a" style="display:flex;flex-direction:column;align-items:center;justify-content:center">'
            f'<img class="shot" src="assets/screens/{src}" style="{style}"><p class="shot-cap">{cap}</p></div>')


def flow(nodes):
    """A vertical flow of (title, subtitle, color-token) nodes joined by arrows."""
    parts = []
    for i, (t, s, c) in enumerate(nodes):
        if i:
            parts.append('<div class="flow-arrow">↓</div>')
        parts.append(f'<div class="flow-node" style="--status:var(--{c})"><b>{t}</b><span>{s}</span></div>')
    return '<div class="flow a">' + "".join(parts) + "</div>"


def brief(name, eyebrow, title, asked, learn, visual):
    """Case brief: what was asked for (bullets), the idea to validate, and a visual on the right."""
    items = "".join(f'<li class="a" style="font-size:28px">{x}</li>' for x in asked)
    add(name, "Case", 12, f"""
<div class="slide">
  <p class="slide-eyebrow a">{eyebrow}</p>
  <h2 class="slide-title a" style="margin-top:var(--space-2);font-size:68px">{title}</h2>
  <div class="row grow" style="margin-top:var(--space-4);gap:var(--space-4)">
    <div class="col" style="display:flex;flex-direction:column;gap:var(--space-3)">
      <div class="card card-top a" style="--status:var(--primary);flex:1"><p class="num-badge">WHAT WE ASKED FOR</p>
        <ul class="points" style="margin-top:var(--space-2);--status:var(--primary)">{items}</ul></div>
      <div class="card card-top a" style="--status:var(--highlight)"><p class="num-badge" style="color:var(--highlight)">THE IDEA TO VALIDATE</p>
        <p class="slide-body" style="margin-top:var(--space-1);color:var(--text);font-size:30px">{learn}</p></div>
    </div>
    <div class="col" style="display:flex;flex-direction:column;justify-content:center">{visual}</div>
  </div>
</div>""")


def result(name, eyebrow, title, rows, outcome):
    """Case result: rows of (asked, got, iterations, status) with status in PILLS, plus an outcome line."""
    cols = "grid-template-columns:0.85fr 1.9fr 130px 190px"
    rowstyle = ("display:grid;gap:var(--space-3);align-items:center;background:var(--bg-elevated);"
                "border:1px solid var(--border);border-left:8px solid var(--status);border-radius:16px;"
                "padding:12px 24px;margin-top:10px;" + cols)
    head = ("display:grid;gap:var(--space-3);padding:0 24px 8px 32px;font-size:22px;letter-spacing:.1em;"
            "text-transform:uppercase;color:var(--text-faint);" + cols)
    body = "".join(
        f'<div class="a" style="--status:var(--{PILLS[st][1]});{rowstyle}">'
        f'<div style="font-size:30px;font-weight:650;line-height:1.2">{ask}</div>'
        f'<div style="font-size:28px;color:var(--text-muted);line-height:1.25">{got}</div>'
        f'<div style="font-size:40px;font-weight:800;color:var(--status);text-align:center">{it}</div>'
        f'<div class="status-pill" style="font-size:20px;padding:6px 16px;text-align:center">{PILLS[st][0]}</div></div>'
        for ask, got, it, st in rows)
    add(name, "Case", 12, f"""
<div class="slide">
  <p class="slide-eyebrow a">{eyebrow}</p>
  <h2 class="slide-title a" style="margin-top:var(--space-2);font-size:68px">{title}</h2>
  <div class="grow" style="margin-top:var(--space-3)">
    <div class="a" style="{head}"><span>We asked</span><span>What happened</span><span style="text-align:center">Iterations</span><span style="text-align:center">Result</span></div>
    {body}
  </div>
  <p class="slide-body a" style="margin-top:var(--space-3)">{outcome}</p>
</div>""")


# ---- Slides ----
add("title", "", 7, f"""
<div class="slide slide-center">
  <p class="slide-eyebrow a">{esc(DATE)}</p>
  <h1 class="slide-display a" style="margin-top:var(--space-4)">{esc(TITLE)}</h1>
  <div class="rule a" style="margin-top:var(--space-4)"></div>
  <p class="slide-body a" style="margin-top:var(--space-4)">{esc(SUBTITLE)}</p>
</div>""")

add("agenda", "Agenda", 8, f"""
<div class="slide slide-center">
  <p class="slide-eyebrow a">Agenda</p>
  <h2 class="slide-title a" style="margin-top:var(--space-2)">What we will <span class="text-gradient">cover</span></h2>
  <div class="stack-3" style="margin-top:var(--space-5)">{ul(AGENDA)}</div>
</div>""")

divider("divider", 1, 'Placeholder <span class="text-gradient">section</span>',
        ["Placeholder point one", "Placeholder point two"], "Placeholder next step",
        "One line on what the next part covers.", 0)

add("content", "Introduction", 10, f"""
<div class="slide">
  <p class="slide-eyebrow a">Placeholder eyebrow</p>
  <h2 class="slide-title a" style="margin-top:var(--space-2)">Placeholder <span class="text-gradient">headline</span></h2>
  <div class="row grow" style="margin-top:var(--space-5)">
    <div class="col card a stack-3"><p class="card-title">Key points</p>{ul(["Placeholder point one", "Placeholder point two", "Placeholder point three"])}</div>
    <div class="col card card-top a" style="--status:var(--accent);display:flex;flex-direction:column;justify-content:center">
      <p class="metric metric-sm">42</p><p class="metric-label">Placeholder metric</p></div>
  </div>
</div>""")

brief("case-brief", "Case 1", "Placeholder case",
      ["Placeholder requirement one", "Placeholder requirement two", "Placeholder requirement three"],
      "One sentence on the question this case answers.",
      flow([("Input", "What goes in", "primary"), ("Process", "What happens", "accent"), ("Output", "What comes out", "highlight")]))

result("case-result", "Case 1", "Placeholder case, results",
       [("Requirement one", "What actually happened", "1", "win"),
        ("Requirement two", "What actually happened", "3", "mixed"),
        ("Requirement three", "What actually happened", "5", "fail")],
       "One-line outcome of the case.")

add("closing", "Closing", 8, f"""
<div class="slide slide-center center">
  <p class="slide-eyebrow a">Thank you</p>
  <h2 class="slide-display a" style="margin-top:var(--space-4)">{esc(TITLE)}</h2>
  <div class="rule a" style="margin-top:var(--space-4)"></div>
  <p class="slide-body a" style="margin-top:var(--space-4)">Questions and discussion</p>
</div>""")

build(HERE, **flags())
