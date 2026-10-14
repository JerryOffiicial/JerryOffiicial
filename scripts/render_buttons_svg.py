"""Step 6: terminal-style link buttons -> assets/btn-<name>.svg

    python scripts/render_buttons_svg.py

The links themselves live in README.md (an SVG shown as an image can't hold a
clickable link), so each button there is wrapped in <a href="...">.
"""
import os

BUTTONS = ["portfolio", "linkedin", "repositories"]

BG, BORDER, KEY, VAL, DIM = "#0d1117", "#30363d", "#39d353", "#c9d1d9", "#8b949e"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
H, FS = 40, 14
CH = 0.602 * FS

os.makedirs("assets", exist_ok=True)
for name in BUTTONS:
    w = round(16 + 10 + 12 + len(name) * CH + 12 + 10 + 16)
    mid = (16 + 10 + w - 16 - 10) / 2
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {H}" width="{w}" height="{H}" '
           f'role="img" aria-label="{name}">'
           f'<rect x=".5" y=".5" width="{w-1}" height="{H-1}" rx="8" fill="{BG}" stroke="{BORDER}"/>'
           # prompt chevron
           f'<path d="M17 15l5 5-5 5" fill="none" stroke="{KEY}" stroke-width="2.2" '
           f'stroke-linecap="round" stroke-linejoin="round"/>'
           f'<text x="{mid:.1f}" y="25" text-anchor="middle" fill="{VAL}" '
           f'style="font-family:{FONT};font-size:{FS}px">{name}</text>'
           # external-link arrow
           f'<path d="M{w-25} {H/2+4}l7-7m-5 0h5v5" fill="none" stroke="{DIM}" stroke-width="1.6" '
           f'stroke-linecap="round" stroke-linejoin="round"/>'
           "</svg>")
    with open(f"assets/btn-{name}.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote assets/btn-{name}.svg ({w}x{H})")
