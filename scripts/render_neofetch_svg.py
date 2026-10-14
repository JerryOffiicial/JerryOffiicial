"""Step 4: one neofetch-style terminal window -> assets/neofetch.svg

ASCII portrait on the left (data/portrait.json, from make_portrait.py), info on the
right. Lines with {placeholders} are filled from data/github.json and
data/contributions.json, so the daily workflow keeps Uptime / GitHub / Langs fresh.
A line whose data is missing is simply left out.

    python scripts/render_neofetch_svg.py          (STATIC=1 for a frozen frame)

Standard library only, so it runs in the workflow without extra installs.
"""
import json
import os
from calendar import monthrange
from datetime import date

USER = "jerry@github"
CARD = [
    ("Name",     "Gunaseelan Jerryson"),
    ("Role",     "Full Stack Developer"),
    ("Location", "Kandy, Sri Lanka"),
    ("Uptime",   "{uptime}"),
    ("Now",      "Building with Next.js & TypeScript"),
    ("Stack",    "React · Node/Express · MongoDB"),
    ("",         "Next.js · TypeScript · Laravel/PHP"),
    ("Data",     "SQL · MongoDB · Supabase · Firebase"),
    ("Also",     ".NET · REST APIs · Tailwind"),
    ("Projects", "MERN Auth (JWT + OTP reset)"),
    ("",         "MERN movie admin w/ AI descriptions"),
    ("",         "DevEvent — Next.js event hub"),
    ("Achieve",  "Pull Shark x3 · Pair Extraordinaire"),
    ("GitHub",   "{repos} repos · {contributions} contributions"),
    ("Langs",    "{langs}"),
    ("Web",      "jerry-portfolio-sepia.vercel.app"),
]
# markup / template languages left out of the Langs line
HIDE_LANGS = {"HTML", "CSS", "SCSS", "Sass", "Less", "Blade", "EJS", "Handlebars",
              "Jupyter Notebook", "Dockerfile", "Shell", "Batchfile", "PowerShell"}
TOP_LANGS = 3

# colours: GitHub dark + the contribution-graph greens
BG, BAR, BORDER = "#0d1117", "#161b22", "#30363d"
KEY, VAL, DIM, MUTED = "#39d353", "#c9d1d9", "#30363d", "#8b949e"
SWATCH = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0", "#58a6ff", "#c9d1d9"]
TONES = ["#123d26", "#16592f", "#1b783a", "#24a043", "#39d353", "#62e384", "#9af2b4", "#dcffe8"]
LANG_COLORS = {"JavaScript": "#f1e05a", "TypeScript": "#3178c6", "PHP": "#4f5d95", "Java": "#b07219",
               "Python": "#3572a5", "C#": "#178600", "Go": "#00add8", "Kotlin": "#a97bff",
               "Dart": "#00b4ab", "C++": "#f34b7d", "C": "#555555", "Rust": "#dea584"}

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
STATIC = os.environ.get("STATIC") == "1"

W = 860
TITLE_H = 32
PAD = 24
PORTRAIT_W = 316
INFO_X = PAD + PORTRAIT_W + 30
VAL_X = INFO_X + 92
FS, LINE_H = 14, 22
CH = 0.602 * FS                        # monospace advance, for laying out the Langs line


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def uptime(since, today):
    y, m, d = today.year - since.year, today.month - since.month, today.day - since.day
    if d < 0:
        m -= 1
        pm = today.month - 1 or 12
        d += monthrange(today.year if today.month > 1 else today.year - 1, pm)[1]
    if m < 0:
        y -= 1
        m += 12
    parts = [(y, "year"), (m, "month"), (d, "day")]
    return ", ".join(f"{n} {u}{'s' if n != 1 else ''}" for n, u in parts if n) or "0 days"


# --- live values -------------------------------------------------------------------
gh = load("data/github.json") or {}
contrib = load("data/contributions.json") or {}
live, langs = {}, []
if gh.get("created_at"):
    live["uptime"] = uptime(date.fromisoformat(gh["created_at"][:10]), date.today())
if gh.get("public_repos") is not None and contrib.get("total") is not None:
    live["repos"] = gh["public_repos"]
    live["contributions"] = f"{contrib['total']:,}"
if gh.get("languages"):
    shown = {k: v for k, v in gh["languages"].items() if k not in HIDE_LANGS}
    total = sum(shown.values())
    if total:
        langs = [(k, v / total) for k, v in sorted(shown.items(), key=lambda kv: -kv[1])][:TOP_LANGS]
        live["langs"] = "langs"

rows = []
for k, v in CARD:
    if "{" in v:
        try:
            v = v.format(**live)
        except KeyError:
            continue
    rows.append((k, v))

# --- geometry ------------------------------------------------------------------------
HEAD_Y = TITLE_H + 34                  # baseline of "jerry@github"
FIRST_Y = HEAD_Y + 40                  # baseline of the first info row
SWATCH_Y = FIRST_Y + LINE_H * (len(rows) - 1) + 20
PROMPT_Y = SWATCH_Y + 50
H = PROMPT_Y + 26

portrait = load("data/portrait.json")
o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
     f'role="img" aria-label="neofetch: {esc(rows[0][1]) if rows else USER}">']

tone_css = " ".join(f".t{i}{{fill:{c}}}" for i, c in enumerate(TONES))
anim = "" if STATIC else """
  .ln { opacity: 0; animation: in .4s ease-out forwards; }
  @keyframes in { from { opacity: 0; transform: translateX(-6px); } to { opacity: 1; transform: none; } }
  .cur { animation: blink 1.1s step-end infinite; }
  @keyframes blink { 50% { fill-opacity: 0; } }
  @media (prefers-reduced-motion: reduce) { .ln, .cur { animation: none; opacity: 1; } }
"""
o.append(f"<style>text {{ font-family: {FONT}; font-size: {FS}px; }} .p text {{ font-size: inherit; }} "
         f"{tone_css}{anim}</style>")

# window + title bar
o.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="10" fill="{BG}" stroke="{BORDER}"/>')
o.append(f'<path d="M.5 {TITLE_H}V10.5a10 10 0 0 1 10-10h{W-21}a10 10 0 0 1 10 10V{TITLE_H}z" fill="{BAR}"/>')
o.append(f'<line x1="0" y1="{TITLE_H}" x2="{W}" y2="{TITLE_H}" stroke="{BORDER}"/>')
o.append('<circle cx="20" cy="16" r="6" fill="#ff5f56"/><circle cx="40" cy="16" r="6" fill="#ffbd2e"/>'
         '<circle cx="60" cy="16" r="6" fill="#27c93f"/>')
o.append(f'<text x="{W/2}" y="21" text-anchor="middle" fill="{MUTED}" style="font-size:12px">neofetch — {USER}</text>')

# --- portrait (types itself in, row by row) ---------------------------------------
if portrait:
    cols, nrows = portrait["cols"], portrait["rows"]
    box_x, box_y = PAD, TITLE_H + 16
    box_w, box_h = PORTRAIT_W, H - box_y - 16
    cw = min(box_w / cols, box_h / nrows * (0.6 / 1.12))      # glyph advance
    lh = cw * 1.12 / 0.6                                        # line height
    fsz = cw / 0.6
    ox = box_x + (box_w - cols * cw) / 2
    oy = box_y + (box_h - nrows * lh) / 2
    grid_w = cols * cw
    stagger = 2.4 / nrows
    o.append("<defs>")
    for r, line in enumerate(portrait["glyphs"]):
        if line.strip() and not STATIC:
            b = 0.15 + r * stagger
            o.append(f'<clipPath id="r{r}"><rect x="{ox:.1f}" y="{oy + r*lh:.1f}" width="0" height="{lh+1:.1f}">'
                     f'<animate attributeName="width" from="0" to="{grid_w:.1f}" begin="{b:.2f}s" dur=".3s" fill="freeze"/>'
                     f"</rect></clipPath>")
    o.append("</defs>")
    o.append(f'<g class="p" style="font-size:{fsz:.2f}px">')
    for r, (line, tone) in enumerate(zip(portrait["glyphs"], portrait["tones"])):
        if not line.strip():
            continue
        y = oy + r * lh + lh * 0.8
        by_tone = {}
        for c, (ch, t) in enumerate(zip(line, tone)):
            if ch != " ":
                by_tone.setdefault(t, []).append((c, ch))
        clip = "" if STATIC else f' clip-path="url(#r{r})"'
        o.append(f"<g{clip}>")
        for t, cells in sorted(by_tone.items()):
            xs = " ".join(f"{ox + c*cw:.1f}" for c, _ in cells)
            o.append(f'<text class="t{t}" x="{xs}" y="{y:.1f}">{esc("".join(ch for _, ch in cells))}</text>')
        o.append("</g>")
        if not STATIC:
            b = 0.15 + r * stagger
            o.append(f'<rect y="{oy + r*lh + 1:.1f}" width="{cw:.1f}" height="{lh-2:.1f}" fill="{TONES[5]}" opacity="0">'
                     f'<animate attributeName="x" from="{ox:.1f}" to="{ox + grid_w:.1f}" begin="{b:.2f}s" dur=".3s" fill="freeze"/>'
                     f'<set attributeName="opacity" to=".85" begin="{b:.2f}s"/>'
                     f'<set attributeName="opacity" to="0" begin="{b + .3:.2f}s"/></rect>')
    o.append("</g>")

# --- info ----------------------------------------------------------------------------
def line(i, inner):
    d = "" if STATIC else f' style="animation-delay:{0.25 + i*0.11:.2f}s"'
    return f'<g class="ln"{d}>{inner}</g>'


o.append(line(0, f'<text x="{INFO_X}" y="{HEAD_Y}"><tspan fill="{KEY}" font-weight="bold">jerry</tspan>'
                 f'<tspan fill="{VAL}">@</tspan><tspan fill="{KEY}" font-weight="bold">github</tspan></text>'
                 f'<text x="{INFO_X}" y="{HEAD_Y + 16}" fill="{DIM}">{"-" * 12}</text>'))
for i, (k, v) in enumerate(rows, start=1):
    y = FIRST_Y + (i - 1) * LINE_H
    key = (f'<text x="{INFO_X}" y="{y}"><tspan fill="{KEY}" font-weight="bold">{esc(k)}</tspan>'
           f'<tspan fill="{VAL}">:</tspan></text>') if k else ""
    if v == "langs":
        x, parts = VAL_X, []
        for name, share in langs:
            label = f"{name} {share*100:.0f}%"
            parts.append(f'<circle cx="{x + 5:.1f}" cy="{y - 5}" r="5" fill="{LANG_COLORS.get(name, MUTED)}"/>'
                         f'<text x="{x + 15:.1f}" y="{y}" fill="{VAL}">{esc(label)}</text>')
            x += 15 + len(label) * CH + 16
        val = "".join(parts)
    else:
        val = f'<text x="{VAL_X}" y="{y}" fill="{VAL}">{esc(v)}</text>'
    o.append(line(i, key + val))

n = len(rows) + 1
o.append(line(n, "".join(f'<rect x="{INFO_X + j*28}" y="{SWATCH_Y}" width="24" height="16" rx="3" fill="{c}"/>'
                         for j, c in enumerate(SWATCH))))
o.append(line(n + 1, f'<text x="{INFO_X}" y="{PROMPT_Y}"><tspan fill="{KEY}" font-weight="bold">jerry@github</tspan>'
                     f'<tspan fill="{VAL}"> ~ $ </tspan><tspan class="cur" fill="{VAL}">█</tspan></text>'))
o.append("</svg>")

os.makedirs("assets", exist_ok=True)
with open("assets/neofetch.svg", "w", encoding="utf-8") as f:
    f.write("\n".join(o))
print(f"wrote assets/neofetch.svg ({W}x{H}, {len(rows)} info lines"
      f"{', no portrait' if not portrait else ''}{', live: ' + ', '.join(sorted(live)) if live else ''})")
