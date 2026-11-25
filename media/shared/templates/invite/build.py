"""Invite template: a three-slide teaser (title, details, call to action)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "shared"))
from engine import add, ul, esc, build, flags

# ---- Config ----
TITLE = "Research Template"
HEADLINE = "Placeholder headline"
WHEN = "Date and time"
WHERE = "Place or link"
CTA = "Placeholder call to action"

add("title", "", 6, f"""
<div class="slide slide-center">
  <p class="slide-eyebrow a">You are invited</p>
  <h1 class="slide-display a" style="margin-top:var(--space-4)">{esc(TITLE)}</h1>
  <div class="rule a" style="margin-top:var(--space-4)"></div>
  <p class="slide-body a" style="margin-top:var(--space-4)">{esc(HEADLINE)}</p>
</div>""")

add("details", "", 6, f"""
<div class="slide slide-center">
  <p class="slide-eyebrow a">The details</p>
  <h2 class="slide-title a" style="margin-top:var(--space-2)">What to <span class="text-gradient">expect</span></h2>
  <div class="row" style="margin-top:var(--space-5)">
    <div class="col card card-top a" style="--status:var(--primary)"><p class="num-badge">WHEN</p><p class="card-title" style="margin-top:8px">{esc(WHEN)}</p></div>
    <div class="col card card-top a" style="--status:var(--accent)"><p class="num-badge">WHERE</p><p class="card-title" style="margin-top:8px">{esc(WHERE)}</p></div>
    <div class="col card card-top a" style="--status:var(--highlight)"><p class="num-badge">WHAT</p><p class="card-title" style="margin-top:8px">Placeholder topic</p></div>
  </div>
</div>""")

add("cta", "", 6, f"""
<div class="slide slide-center center">
  <p class="slide-eyebrow a">Join us</p>
  <h2 class="slide-display a" style="margin-top:var(--space-4)">{esc(CTA)}</h2>
  <div class="rule a" style="margin-top:var(--space-4)"></div>
  <p class="slide-body a" style="margin-top:var(--space-4)">{esc(TITLE)}</p>
</div>""")

build(HERE, **flags())
