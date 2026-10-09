"""Step 4: neofetch-style info card SVG. Edit the CARD dict, then run:
python scripts/make_info_card.py        (STATIC=1 for a frozen frame)
"""
import os

USER = "jerry@github"
CARD = [
    ("Name",     "Gunaseelan Jerryson"),
    ("Role",     "Full Stack Developer"),
    ("Location", "Kandy, Sri Lanka"),
    ("Now",      "Building with Next.js & TypeScript"),
    ("Stack",    "React · Node/Express · MongoDB"),
    ("",         "Next.js · TypeScript · Laravel/PHP"),
    ("Data",     "SQL · MongoDB · Supabase · Firebase"),
    ("Also",     ".NET · REST APIs · Tailwind"),
    ("Projects", "MERN Auth (JWT + OTP reset)"),
    ("",         "MERN movie admin w/ AI descriptions"),
    ("",         "DevEvent — Next.js event hub"),
    ("Achieve",  "Pull Shark x3 · Pair Extraordinaire"),
    ("Web",      "jerry-portfolio-sepia.vercel.app"),
]

STATIC = os.environ.get("STATIC") == "1"
W, PAD, LINE_H, TOP = 490, 22, 24, 74
H = TOP + LINE_H * len(CARD) + 56
KEY, VAL, ACC, BG, DIM = "#39d353", "#c9d1d9", "#58a6ff", "#0d1117", "#30363d"
SWATCH = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0", "#58a6ff", "#c9d1d9"]

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

anim = "" if STATIC else """
  .ln { opacity: 0; animation: in .45s ease-out forwards; }
  @keyframes in { from { opacity: 0; transform: translateX(-8px); } to { opacity: 1; transform: none; } }
"""
o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
     f'<style>text {{ font-family: ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size: 14px; }}{anim}</style>',
     f'<rect width="{W}" height="{H}" rx="8" fill="{BG}" stroke="{DIM}"/>',
     # title bar
     f'<rect width="{W}" height="30" rx="8" fill="#161b22"/><rect y="22" width="{W}" height="8" fill="#161b22"/>',
     '<circle cx="18" cy="15" r="5" fill="#ff5f56"/><circle cx="36" cy="15" r="5" fill="#ffbd2e"/><circle cx="54" cy="15" r="5" fill="#27c93f"/>',
     f'<text x="{W/2}" y="20" text-anchor="middle" fill="#8b949e" style="font-size:12px">neofetch — {USER}</text>']

def line(i, inner):
    d = "" if STATIC else f' style="animation-delay:{0.25 + i*0.12:.2f}s"'
    return f'<g class="ln"{d}>{inner}</g>'

o.append(line(0, f'<text x="{PAD}" y="{TOP-18}"><tspan fill="{KEY}" font-weight="bold">jerry</tspan><tspan fill="{VAL}">@</tspan><tspan fill="{KEY}" font-weight="bold">github</tspan></text>'
                 f'<text x="{PAD}" y="{TOP-4}" fill="{DIM}">{"-"*20}</text>'))
for i, (k, v) in enumerate(CARD, start=1):
    y = TOP + 14 + (i-1) * LINE_H
    key = f'<tspan fill="{KEY}" font-weight="bold">{esc(k)}</tspan><tspan fill="{VAL}">:</tspan>' if k else ""
    o.append(line(i, f'<text x="{PAD}" y="{y}">{key}</text><text x="{PAD+92}" y="{y}" fill="{VAL}">{esc(v)}</text>'))
sy = TOP + LINE_H * len(CARD) + 14
o.append(line(len(CARD)+1, "".join(f'<rect x="{PAD + j*26}" y="{sy}" width="22" height="14" rx="2" fill="{c}"/>' for j, c in enumerate(SWATCH))))
o.append('</svg>')

open("info-card.svg", "w").write("\n".join(o))
print("wrote info-card.svg")
