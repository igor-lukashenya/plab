"""Digest template: a four-slide recap of findings."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "shared"))
from engine import add, ul, esc, build, flags

# ---- Config ----
TITLE = "Research Template"
FINDINGS = [("Placeholder finding one", "Short supporting detail", "primary"),
            ("Placeholder finding two", "Short supporting detail", "accent"),
            ("Placeholder finding three", "Short supporting detail", "highlight")]

add("title", "", 6, f"""
<div class="slide slide-center">
  <p class="slide-eyebrow a">Digest</p>
  <h1 class="slide-display a" style="margin-top:var(--space-4)">{esc(TITLE)}</h1>
  <div class="rule a" style="margin-top:var(--space-4)"></div>
  <p class="slide-body a" style="margin-top:var(--space-4)">Placeholder headline</p>
</div>""")

cards = "".join(
    f'<div class="card card-top a" style="--status:var(--{c})"><p class="num-badge">FINDING {i+1}</p>'
    f'<p class="card-title" style="margin-top:8px">{esc(t)}</p><p class="card-meta" style="margin-top:8px">{esc(s)}</p></div>'
    for i, (t, s, c) in enumerate(FINDINGS))
add("findings", "Findings", 8, f"""
<div class="slide">
  <p class="slide-eyebrow a">Key findings</p>
  <h2 class="slide-title a" style="margin-top:var(--space-2)">What we <span class="text-gradient">found</span></h2>
  <div class="grid-3 grow" style="margin-top:var(--space-5)">{cards}</div>
</div>""")

add("numbers", "Numbers", 6, """
<div class="slide slide-center">
  <p class="slide-eyebrow a">By the numbers</p>
  <div class="row" style="margin-top:var(--space-5)">
    <div class="col a is-win"><p class="metric">42</p><p class="metric-label">Placeholder metric one</p></div>
    <div class="col a is-mixed"><p class="metric">7</p><p class="metric-label">Placeholder metric two</p></div>
  </div>
</div>""")

add("takeaway", "Takeaway", 6, f"""
<div class="slide slide-center">
  <p class="slide-eyebrow a">Takeaway</p>
  <div class="quote a" style="margin-top:var(--space-4)"><p class="callout">Placeholder one-sentence takeaway.</p></div>
  <p class="slide-caption a" style="margin-top:var(--space-5)">{esc(TITLE)}</p>
</div>""")

build(HERE, **flags())
