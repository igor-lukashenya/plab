"""Explainer template: one animated scene (client -> service -> data store), ported from a request-flow explainer.

The scene is plain HTML/CSS inside engine.add(); elements marked class "a" animate in one after another.
Add more scenes with more add(...) calls; each gets its own composition and timeline slot.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "shared"))
from engine import add, ul, esc, build, flags

# ---- Config ----
TITLE = "Research Template"
STEPS = "Placeholder step one, placeholder step two, placeholder step three"
CLIENT, SERVICE, STORE = "Client", "Service", "Data store"
LAYERS = ["Layer one", "Layer two", "Layer three"]
ROWS = [("Item one", 40), ("Item two", 75), ("Item three", 55)]

layers = "".join(f'<div class="x-layer" style="top:{34 + 110 * i}px">{esc(t)}</div>' for i, t in enumerate(LAYERS))
rows = "".join(
    f'<div class="x-dbrow" style="top:{96 + 74 * i}px"><i style="width:{w}%"></i><em>{esc(t)}</em></div>'
    for i, (t, w) in enumerate(ROWS))

add("scene", "", 12, f"""
<div class="slide">
  <style>
    .x-grid {{ position:absolute; inset:0; background-image: linear-gradient(rgba(91,140,255,.10) 2px, transparent 2px), linear-gradient(90deg, rgba(91,140,255,.10) 2px, transparent 2px); background-size: 80px 80px; }}
    .x-label {{ position:absolute; font-size:30px; font-weight:700; letter-spacing:.14em; text-transform:uppercase; color:var(--text-muted); text-align:center; }}
    .x-client {{ position:absolute; left:120px; top:260px; width:320px; height:600px; border-radius:44px; background:var(--bg-elevated); border:6px solid var(--border); box-shadow:0 30px 60px rgba(0,0,0,.5); }}
    .x-chip {{ position:absolute; top:40px; height:46px; line-height:46px; padding:0 20px; border-radius:23px; font-size:22px; font-weight:600; background:var(--bg-subtle); color:var(--text-muted); }}
    .x-item {{ position:absolute; left:20px; width:268px; height:84px; border-radius:16px; background:var(--bg-subtle); border:1px solid var(--border); display:flex; align-items:center; gap:14px; padding:0 16px; font-size:24px; font-weight:700; }}
    .x-item i {{ width:48px; height:48px; border-radius:12px; flex:none; background:var(--gradient-brand); }}
    .x-service {{ position:absolute; left:770px; top:380px; width:380px; height:360px; border-radius:28px; background:var(--bg-elevated); border:3px solid var(--border); box-shadow:0 30px 60px rgba(0,0,0,.5); }}
    .x-layer {{ position:absolute; left:28px; right:28px; height:70px; line-height:70px; border-radius:16px; text-align:center; font-size:28px; font-weight:700; background:var(--bg-subtle); color:var(--text-muted); }}
    .x-store {{ position:absolute; left:1470px; top:330px; width:340px; height:460px; border-radius:40px 40px 60px 60px / 36px 36px 50px 50px; background:var(--bg-elevated); border:3px solid var(--border); box-shadow:0 30px 60px rgba(0,0,0,.5); }}
    .x-cap {{ position:absolute; left:-3px; right:-3px; top:-3px; height:72px; border-radius:50%; background:var(--bg-subtle); border:3px solid var(--border); }}
    .x-dbrow {{ position:absolute; left:34px; right:34px; height:56px; border-radius:12px; background:var(--bg-subtle); overflow:hidden; }}
    .x-dbrow i {{ position:absolute; left:0; top:0; bottom:0; border-radius:12px; background:var(--gradient-brand); opacity:.85; }}
    .x-dbrow em {{ position:absolute; left:16px; top:0; line-height:56px; font-style:normal; font-size:22px; font-weight:700; font-family:var(--font-mono); color:#06101f; }}
    .x-wires {{ position:absolute; left:0; top:0; width:1920px; height:1080px; }}
    .x-packet {{ position:absolute; padding:12px 20px; border-radius:14px; font-family:var(--font-mono); font-size:21px; font-weight:700; white-space:nowrap; color:#06101f; box-shadow:0 10px 30px rgba(0,0,0,.45); }}
    .x-head {{ position:absolute; left:120px; top:44px; }}
    .x-head small {{ display:block; font-size:22px; font-weight:600; letter-spacing:.18em; text-transform:uppercase; color:var(--accent); }}
    .x-head h1 {{ font-size:46px; font-weight:800; letter-spacing:-.02em; margin-top:4px; }}
    .x-step {{ position:absolute; left:120px; right:120px; bottom:60px; font-size:40px; font-weight:650; color:var(--text); }}
  </style>
  <div class="x-grid"></div>
  <div class="x-head a"><small>Explainer</small><h1>{esc(TITLE)}</h1></div>
  <svg class="x-wires" viewBox="0 0 1920 1080">
    <line x1="440" y1="470" x2="770" y2="470" stroke="#ffc857" stroke-width="5" stroke-dasharray="14 12" />
    <line x1="1150" y1="470" x2="1470" y2="470" stroke="#5b8cff" stroke-width="5" stroke-dasharray="14 12" />
    <line x1="1470" y1="770" x2="1150" y2="770" stroke="#22d3c5" stroke-width="5" stroke-dasharray="14 12" />
    <line x1="770" y1="770" x2="440" y2="770" stroke="#22d3c5" stroke-width="5" stroke-dasharray="14 12" />
  </svg>
  <div class="x-label a" style="left:120px;top:200px;width:320px">{esc(CLIENT)}</div>
  <div class="x-label a" style="left:770px;top:320px;width:380px">{esc(SERVICE)}</div>
  <div class="x-label a" style="left:1470px;top:250px;width:340px">{esc(STORE)}</div>
  <div class="x-client a">
    <div class="x-chip" style="left:24px">All</div><div class="x-chip" style="left:110px">Popular</div>
    <div class="x-item" style="top:120px"><i></i>Item one</div>
    <div class="x-item" style="top:224px"><i></i>Item two</div>
    <div class="x-item" style="top:328px"><i></i>Item three</div>
  </div>
  <div class="x-service a">{layers}</div>
  <div class="x-store a"><div class="x-cap"></div>{rows}</div>
  <div class="x-packet a" style="left:470px;top:410px;background:var(--highlight)">request</div>
  <div class="x-packet a" style="left:1190px;top:410px;background:var(--primary);color:#fff">query</div>
  <div class="x-packet a" style="left:1190px;top:790px;background:var(--accent)">data</div>
  <div class="x-step a">{esc(STEPS)}</div>
</div>""")

build(HERE, **flags())
