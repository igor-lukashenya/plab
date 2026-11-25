"""Social template: one portrait still (1080x1350). Render with: make media-png M=social/<name>"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "shared"))
from engine import add, ul, esc, build, flags

# ---- Config ----
TITLE = "Research Template"
HEADLINE = "Placeholder headline"
STAT = "42"
STAT_LABEL = "Placeholder metric"

add("post", "", 5, f"""
<div class="slide slide-center">
  <p class="slide-eyebrow a">{esc(TITLE)}</p>
  <h1 class="slide-title a" style="margin-top:var(--space-3)">{esc(HEADLINE)}</h1>
  <div class="rule a" style="margin-top:var(--space-4)"></div>
  <div class="card card-top a" style="--status:var(--accent);margin-top:var(--space-5)">
    <p class="metric metric-sm">{esc(STAT)}</p><p class="metric-label">{esc(STAT_LABEL)}</p>
  </div>
  <p class="slide-caption a" style="margin-top:var(--space-4)">Placeholder source or handle</p>
</div>""")

build(HERE, **flags())
