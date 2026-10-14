"""Step 5c: data/contributions.json -> assets/contrib-heatmap.svg (diagonal slide-in reveal, plays once)

    python scripts/render_heatmap_svg.py          (STATIC=1 for a frozen frame)
"""
import json
import os
from datetime import date, timedelta

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
#          none -> brightest (level 5 = neon top end for your best days)
BG, BAR, BORDER = "#0d1117", "#161b22", "#30363d"
TXT, DIM, KEY = "#c9d1d9", "#8b949e", "#39d353"
CELL, GAP = 12, 3
TITLE_H = 32
LEFT, TOP = 34, TITLE_H + 34
W = 860
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
STATIC = os.environ.get("STATIC") == "1"

with open("data/contributions.json", encoding="utf-8") as f:
    data = json.load(f)
days = data["days"]

# level 5 = level-4 days in the top 10% of non-zero counts
nz = sorted(d["count"] for d in days if d["count"] > 0)
neon = nz[int(len(nz) * 0.9)] if len(nz) >= 10 else float("inf")

first = date.fromisoformat(days[0]["date"])
start = first - timedelta(days=(first.weekday() + 1) % 7)   # back to Sunday
cells, months, last_month = [], [], None
for d in days:
    dt = date.fromisoformat(d["date"])
    week = (dt - start).days // 7
    dow = (dt.weekday() + 1) % 7                               # Sun=0
    lvl = d["level"]
    if lvl == 4 and d["count"] >= neon:
        lvl = 5
    cells.append((week, dow, lvl, d))
    if dt.month != last_month and dow == 0:
        months.append((week, dt.strftime("%b")))
        last_month = dt.month
weeks = max(c[0] for c in cells) + 1
step = CELL + GAP
grid_w = weeks * step
H = TOP + 7 * step + 68

o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
     f'role="img" aria-label="{data["total"]:,} contributions in the last year">',
     f"""<style>
  text {{ font-family: {FONT}; font-size: 11px; fill: {DIM}; }}
  .n {{ fill: {KEY}; font-weight: bold; }}
  .c {{ opacity: 0; transform-box: fill-box; animation: drop .4s ease-out forwards; }}
  @keyframes drop {{ from {{ opacity: 0; transform: translateY(-6px); }} to {{ opacity: 1; transform: none; }} }}
  .f {{ opacity: 0; animation: fade .6s ease-out forwards; }}
  @keyframes fade {{ to {{ opacity: 1; }} }}
  @media (prefers-reduced-motion: reduce) {{ .c, .f {{ animation: none; opacity: 1; }} }}
</style>""",
     '<defs><filter id="glow" x="-50%" y="-50%" width="200%" height="200%">'
     '<feGaussianBlur stdDeviation="2.2" result="b"/>'
     '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>',
     # window + title bar (same chrome as neofetch.svg)
     f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="10" fill="{BG}" stroke="{BORDER}"/>',
     f'<path d="M.5 {TITLE_H}V10.5a10 10 0 0 1 10-10h{W-21}a10 10 0 0 1 10 10V{TITLE_H}z" fill="{BAR}"/>',
     f'<line x1="0" y1="{TITLE_H}" x2="{W}" y2="{TITLE_H}" stroke="{BORDER}"/>',
     '<circle cx="20" cy="16" r="6" fill="#ff5f56"/><circle cx="40" cy="16" r="6" fill="#ffbd2e"/>'
     '<circle cx="60" cy="16" r="6" fill="#27c93f"/>',
     f'<text x="{W/2}" y="21" text-anchor="middle" style="font-size:12px">contributions — jerry@github</text>']

ox = LEFT + (W - LEFT - 16 - grid_w) / 2
for wk, name in months:
    o.append(f'<text x="{ox + wk*step:.1f}" y="{TOP-8}">{name}</text>')
for i, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
    o.append(f'<text x="{ox-30:.1f}" y="{TOP + i*step + 10}">{lab}</text>')
for wk, dow, lvl, d in cells:
    delay = (wk + dow) * 0.018                                  # diagonal sweep
    tip = f'{d["count"]} contribution{"s" if d["count"] != 1 else ""} on {d["date"]}'
    glow = ' filter="url(#glow)"' if lvl == 5 else ""
    o.append(f'<rect class="c" style="animation-delay:{delay:.3f}s" x="{ox + wk*step:.1f}" y="{TOP + dow*step}" '
             f'width="{CELL}" height="{CELL}" rx="3" fill="{PALETTE[lvl]}"{glow}><title>{tip}</title></rect>')

end = (weeks + 7) * 0.018 + 0.3
fy = TOP + 7 * step + 24
best = date.fromisoformat(data["best_day"]["date"]).strftime("%b %d").replace(" 0", " ")
sep = '<tspan dx="6">·</tspan><tspan dx="6">'
stats = (f'<tspan class="n">{data["total"]:,}</tspan> contributions in the last year'
         f'{sep}current streak <tspan class="n">{data["current_streak"]}d</tspan></tspan>'
         f'{sep}longest <tspan class="n">{data["longest_streak"]}d</tspan></tspan>'
         f'{sep}best day <tspan class="n">{data["best_day"]["count"]}</tspan> ({best})</tspan>')
o.append(f'<g class="f" style="animation-delay:{end:.2f}s">')
o.append(f'<text x="{ox:.1f}" y="{fy}" style="fill:{TXT}; font-size:12px">{stats}</text>')
lx = ox + grid_w - len(PALETTE) * step - 64
o.append(f'<text x="{lx:.1f}" y="{fy+26}">Less</text>')
for i, c in enumerate(PALETTE):
    o.append(f'<rect x="{lx + 34 + i*step:.1f}" y="{fy+16}" width="{CELL}" height="{CELL}" rx="3" fill="{c}"/>')
o.append(f'<text x="{lx + 38 + len(PALETTE)*step:.1f}" y="{fy+26}">More</text>')
o.append(f'<text x="{ox:.1f}" y="{fy+26}">updated {data["fetched_at"][:10]}</text>')
o.append("</g></svg>")
if STATIC:
    o = [x.replace(' class="c"', "").replace(' class="f"', "") for x in o]

os.makedirs("assets", exist_ok=True)
with open("assets/contrib-heatmap.svg", "w", encoding="utf-8") as f:
    f.write("\n".join(o))
print(f"wrote assets/contrib-heatmap.svg ({weeks} weeks)")
