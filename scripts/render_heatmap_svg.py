"""Step 5b: data/contributions.json -> contrib-heatmap.svg (diagonal slide-in reveal, plays once)"""
import json
from datetime import date, timedelta

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
#          none -> brightest (level 5 = neon top end for your best days)
BG, TXT, DIM = "#0d1117", "#c9d1d9", "#8b949e"
CELL, GAP = 12, 3
LEFT, TOP = 34, 30
W = 860

data = json.load(open("data/contributions.json"))
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
H = TOP + 7 * step + 64

o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
     """<style>
  text { font-family: ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size: 11px; fill: #8b949e; }
  .c { opacity: 0; transform-box: fill-box; animation: drop .4s ease-out forwards; }
  @keyframes drop { from { opacity: 0; transform: translateY(-6px); } to { opacity: 1; transform: none; } }
  .f { opacity: 0; animation: fade .6s ease-out forwards; }
  @keyframes fade { to { opacity: 1; } }
</style>""",
     f'<rect width="{W}" height="{H}" rx="8" fill="{BG}" stroke="#30363d"/>']
ox = LEFT + (W - LEFT - 16 - grid_w) / 2
for wk, name in months:
    o.append(f'<text x="{ox + wk*step:.1f}" y="{TOP-8}">{name}</text>')
for i, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
    o.append(f'<text x="{ox-30:.1f}" y="{TOP + i*step + 10}">{lab}</text>')
for wk, dow, lvl, d in cells:
    delay = (wk + dow) * 0.018                                  # diagonal sweep
    tip = f'{d["count"]} contribution{"s" if d["count"] != 1 else ""} on {d["date"]}'
    o.append(f'<rect class="c" style="animation-delay:{delay:.3f}s" x="{ox + wk*step:.1f}" y="{TOP + dow*step}" '
             f'width="{CELL}" height="{CELL}" rx="3" fill="{PALETTE[lvl]}"><title>{tip}</title></rect>')

end = (weeks + 7) * 0.018 + 0.3
fy = TOP + 7 * step + 22
stats = (f'{data["total"]:,} contributions in the last year  ·  current streak {data["current_streak"]}d'
         f'  ·  longest {data["longest_streak"]}d  ·  best day {data["best_day"]["count"]}')
o.append(f'<g class="f" style="animation-delay:{end:.2f}s">')
o.append(f'<text x="{ox:.1f}" y="{fy}" fill="{TXT}" style="fill:{TXT}">{stats}</text>')
lx = ox + grid_w - len(PALETTE) * step - 64
o.append(f'<text x="{lx:.1f}" y="{fy+24}">Less</text>')
for i, c in enumerate(PALETTE):
    o.append(f'<rect x="{lx + 34 + i*step:.1f}" y="{fy+14}" width="{CELL}" height="{CELL}" rx="3" fill="{c}"/>')
o.append(f'<text x="{lx + 38 + len(PALETTE)*step:.1f}" y="{fy+24}">More</text>')
o.append(f'<text x="{ox:.1f}" y="{fy+24}">updated {data["fetched_at"][:10]}</text>')
o.append('</g></svg>')

open("contrib-heatmap.svg", "w").write("\n".join(o))
print(f"wrote contrib-heatmap.svg ({weeks} weeks)")
