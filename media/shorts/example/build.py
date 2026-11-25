"""Shorts template: a three-slide vertical video (1080x1920)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "shared"))
from engine import add, ul, esc, build, flags

# ---- Config ----
TITLE = "Research Template"
add("hook", "", 4, f"""
<div class="slide slide-center">
  <p class="slide-eyebrow a">{esc(TITLE)}</p>
  <h1 class="slide-display a" style="margin-top:var(--space-4)">Placeholder <span class="text-gradient">hook</span></h1>
</div>""")

add("point", "", 5, f"""
<div class="slide slide-center">
  <p class="slide-eyebrow a">The point</p>
  <div class="card card-top a" style="--status:var(--accent);margin-top:var(--space-4)">
    <p class="metric metric-sm">42</p><p class="metric-label">Placeholder metric</p></div>
  <div class="stack-3" style="margin-top:var(--space-5)">{ul(["Placeholder point one", "Placeholder point two"])}</div>
</div>""")

add("outro", "", 4, f"""
<div class="slide slide-center center">
  <p class="slide-eyebrow a">Want more?</p>
  <h2 class="slide-title a" style="margin-top:var(--space-4)">Placeholder call to action</h2>
  <div class="rule a" style="margin-top:var(--space-4)"></div>
</div>""")

build(HERE, **flags())
