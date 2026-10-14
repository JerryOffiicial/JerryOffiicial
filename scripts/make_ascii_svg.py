"""Step 3b: prepped photo -> monochrome ASCII SVG that types itself in row by row.

Usage:  python scripts/make_ascii_svg.py [source-prepped.png] [jerry-ascii.svg]

The portrait is sized so its height matches info-card.svg when both sit side by side
in the README (370px + 490px columns). Every character is placed at an exact x
position, so the grid stays perfectly aligned whatever font the viewer's browser uses.

Tuning (optional env vars; PowerShell:  $env:ASCII_COLS="70"  ):
  ASCII_COLS   characters per row            default 80   (fewer = bigger, cleaner)
  ASCII_GAMMA  >1 brighter, <1 darker        default 1.2
  ASCII_FOCUS  0 = keep top of photo, 1 = bottom, if it must be cropped   default 0.15
"""
import os
import re
import sys

import numpy as np
from PIL import Image, ImageFilter

SRC = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
OUT = sys.argv[2] if len(sys.argv) > 2 else "jerry-ascii.svg"

COLS = int(os.environ.get("ASCII_COLS", 80))
GAMMA = float(os.environ.get("ASCII_GAMMA", 1.2))
FOCUS = float(os.environ.get("ASCII_FOCUS", 0.15))

RAMP = " .`:-=+*cs#%@"          # bright (sparse) -> dark (dense)
CHAR_W, LINE_H = 6.6, 12.5      # one character cell
FONT_SIZE = 11
PAD = 14
FILL, BG = "#c9d1d9", "#0d1117"
ROW_DUR, ROW_STAGGER = 0.35, 0.07   # seconds: wipe time per row, delay between rows

# README layout: portrait column is 370px wide, info card column 490px wide.
DISPLAY_W = 370
CARD_W, CARD_H = 490, 442
try:
    m = re.search(r'viewBox="0 0 (\d+(?:\.\d+)?) (\d+(?:\.\d+)?)"', open("info-card.svg").read())
    if m:
        CARD_W, CARD_H = float(m.group(1)), float(m.group(2))
except OSError:
    pass

# SVG canvas = same shape as the info card once scaled to DISPLAY_W
W = COLS * CHAR_W + 2 * PAD
H = W * (CARD_H / CARD_W) * (490 / DISPLAY_W)
rows = int((H - 2 * PAD) // LINE_H)
grid_w, grid_h = COLS * CHAR_W, rows * LINE_H
OY = (H - grid_h) / 2

# --- image -> brightness grid -------------------------------------------------
img = Image.open(SRC).convert("L")

# cover-crop the photo to the grid's shape (keeps the head, trims the bottom)
target = grid_w / grid_h
iw, ih = img.size
if iw / ih > target:                       # too wide: trim sides evenly
    nw = int(ih * target)
    x0 = (iw - nw) // 2
    img = img.crop((x0, 0, x0 + nw, ih))
else:                                      # too tall: trim mostly from the bottom
    nh = int(iw / target)
    y0 = int((ih - nh) * FOCUS)
    img = img.crop((0, y0, iw, y0 + nh))

img = img.filter(ImageFilter.GaussianBlur(radius=max(img.width / COLS / 3, 0.5)))  # no aliasing stripes
img = img.resize((COLS, rows), Image.BOX)
img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=60, threshold=2))
a = np.asarray(img, dtype=np.float32) / 255.0

# stretch contrast using the SUBJECT only (the white background would otherwise
# stop the face from ever getting real highlights and shadows)
bg = a > 0.97
subj = a[~bg]
if subj.size > 50:
    lo, hi = np.percentile(subj, 3), np.percentile(subj, 97)
    a = np.clip((a - lo) / max(hi - lo, 1e-3), 0, 1)
a = a ** (1.0 / GAMMA)
a[bg] = 1.0

idx = ((1.0 - a) * (len(RAMP) - 1)).round().astype(int)
lines = ["".join(RAMP[i] for i in r) for r in idx]

# --- SVG ----------------------------------------------------------------------
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.1f} {H:.1f}" width="{W:.0f}" height="{H:.0f}">',
     f'<rect width="100%" height="100%" rx="8" fill="{BG}" stroke="#30363d"/>',
     '<defs>']
for i, line in enumerate(lines):
    if line.strip():
        b = i * ROW_STAGGER
        o.append(f'<clipPath id="r{i}"><rect x="{PAD}" y="{OY + i*LINE_H:.1f}" height="{LINE_H}" width="0">'
                 f'<animate attributeName="width" from="0" to="{grid_w:.1f}" begin="{b:.2f}s" dur="{ROW_DUR}s" fill="freeze"/>'
                 f'</rect></clipPath>')
o.append('</defs>')
o.append(f'<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,\'Liberation Mono\',monospace" '
         f'font-size="{FONT_SIZE}" fill="{FILL}">')
for i, line in enumerate(lines):
    if not line.strip():
        continue
    # one x per character => exact grid; spaces are skipped
    xs = [f"{PAD + j*CHAR_W:.1f}" for j, ch in enumerate(line) if ch != " "]
    txt = esc(line.replace(" ", ""))
    y = OY + i * LINE_H + LINE_H * 0.78
    o.append(f'<text x="{" ".join(xs)}" y="{y:.1f}" clip-path="url(#r{i})">{txt}</text>')
    b = i * ROW_STAGGER
    o.append(f'<rect y="{OY + i*LINE_H + 1:.1f}" width="{CHAR_W}" height="{LINE_H-2}" fill="{FILL}" opacity="0">'
             f'<animate attributeName="x" from="{PAD}" to="{PAD + grid_w:.1f}" begin="{b:.2f}s" dur="{ROW_DUR}s" fill="freeze"/>'
             f'<set attributeName="opacity" to="0.9" begin="{b:.2f}s"/>'
             f'<set attributeName="opacity" to="0" begin="{b+ROW_DUR:.2f}s"/></rect>')
o.append('</g></svg>')

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(o))
shown_h = DISPLAY_W * H / W
print(f"wrote {OUT}: {rows} rows x {COLS} cols, shows at {DISPLAY_W}x{shown_h:.0f}px (info card is {CARD_H:.0f}px tall)")
