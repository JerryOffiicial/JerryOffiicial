"""Step 3b: prepped photo -> data/portrait.json (an ASCII glyph grid + tone per cell).

Usage:  python scripts/make_portrait.py [source-prepped.png]

Run it once after prep_photo.py. render_neofetch_svg.py turns the grid into the
coloured, self-typing portrait inside neofetch.svg, so the daily workflow never
needs Pillow or numpy.

Tones are mapped for a DARK terminal: bright skin and shirt get dense, bright
glyphs; the dark suit and hair fade into the background with sparse, dim ones.

Tuning (optional env vars; PowerShell:  $env:PORTRAIT_COLS="60"  ):
  PORTRAIT_COLS    characters per row                      default 80
  PORTRAIT_ROWS    rows (80 cols x 64 rows fills the pane) default 64
  PORTRAIT_SPAN    how much of the body to show, 0.3 = head only, 1 = whole photo
                                                           default 0.5
  PORTRAIT_GAMMA   >1 brighter mid-tones, <1 darker        default 1.0
"""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageFilter

SRC = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
OUT = "data/portrait.json"

COLS = int(os.environ.get("PORTRAIT_COLS", 80))
ROWS = int(os.environ.get("PORTRAIT_ROWS", 64))
SPAN = float(os.environ.get("PORTRAIT_SPAN", 0.5))
GAMMA = float(os.environ.get("PORTRAIT_GAMMA", 1.0))
CELL_ASPECT = 0.6 / 1.12        # glyph width / line height used by the renderer

FLOOR = 0.07                    # minimum tone for subject cells
FADE = 0.45                     # how much the bottom of the portrait dims (0 = none)
RAMP = ".:-=+*cs#%@"            # sparse/dim -> dense/bright (dark background)
LEVELS = 8                      # tone classes, coloured by the renderer

# --- load + subject mask ---------------------------------------------------------
im = Image.open(SRC)
if im.mode in ("LA", "RGBA"):
    alpha = np.asarray(im.getchannel("A")) > 20
    gray = np.asarray(im.convert("L"))
else:
    # white background from prep_photo.py: near-white regions touching the border.
    # (Flood-filling from the edge keeps the white shirt from being mistaken for it.)
    gray = np.asarray(im.convert("L"))
    white = (gray >= 245).astype(np.uint8)
    n, labels = cv2.connectedComponents(white, connectivity=4)
    border = np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))
    bg = np.isin(labels, border[border > 0])
    alpha = ~bg
alpha = cv2.morphologyEx(alpha.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
# shave the light halo the background removal leaves around hair and shoulders
k = max(3, int(gray.shape[1] * 0.008)) | 1
alpha = cv2.erode(alpha, np.ones((k, k), np.uint8)).astype(bool)

ys, xs = np.nonzero(alpha)
if not len(ys):
    sys.exit("No subject found in the photo.")
top, bottom = ys.min(), ys.max()
subj_h = bottom - top

# horizontal centre = centre of the head (top 18% of the subject)
head = alpha[top: top + int(subj_h * 0.18)]
hx = np.nonzero(head)[1]
cx = hx.mean() if len(hx) else xs.mean()

# --- crop a box of the grid's shape around head + shoulders ----------------------
target = (COLS * CELL_ASPECT) / ROWS             # width / height of the grid
crop_h = subj_h * SPAN
crop_w = crop_h * target
y0 = top - subj_h * 0.035
x0 = cx - crop_w / 2

canvas = np.zeros((int(crop_h), int(crop_w)), np.uint8)
cmask = np.zeros_like(canvas, dtype=bool)
sy0, sx0 = int(round(y0)), int(round(x0))
iy0, ix0 = max(sy0, 0), max(sx0, 0)
iy1, ix1 = min(sy0 + canvas.shape[0], gray.shape[0]), min(sx0 + canvas.shape[1], gray.shape[1])
canvas[iy0 - sy0: iy1 - sy0, ix0 - sx0: ix1 - sx0] = gray[iy0:iy1, ix0:ix1]
cmask[iy0 - sy0: iy1 - sy0, ix0 - sx0: ix1 - sx0] = alpha[iy0:iy1, ix0:ix1]
canvas[~cmask] = 0          # background -> black, so edge cells darken instead of glowing

# --- downsample to the character grid -------------------------------------------
# average only subject pixels in each cell, so edges neither glow nor go muddy
def shrink(x):
    return np.asarray(Image.fromarray(x).resize((COLS, ROWS), Image.BOX), dtype=np.float32)

m = cmask.astype(np.float32)
cov = shrink(m)
a = shrink(canvas.astype(np.float32) * m) / np.maximum(cov, 1e-3) / 255.0
a = np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
               .filter(ImageFilter.UnsharpMask(radius=1, percent=70, threshold=1)), dtype=np.float32) / 255.0
subj = cov > 0.4

# stretch contrast using the FACE (top of the subject): it's what people look at,
# so its highlights and shadows get the full ramp; suit and shirt simply clip
head_rows = max(4, int(ROWS * 0.24 / SPAN))
first = int(np.argmax(subj.any(axis=1)))
face = subj.copy()
face[:first] = False
face[first + head_rows:] = False
vals = a[face] if face.sum() > 20 else a[subj]
lo, hi = np.percentile(vals, 3), np.percentile(vals, 98)
t = np.clip((a - lo) / max(hi - lo, 1e-3), 0, 1) ** (1.0 / GAMMA)

# fade everything below the face toward the bottom edge, so the eye lands on the face
# (the white shirt would otherwise be the brightest thing in the picture)
fade_from = first + head_rows
r = np.arange(ROWS, dtype=np.float32)[:, None]
t = t * np.clip(1 - FADE * (r - fade_from) / max(ROWS - fade_from, 1), 1 - FADE, 1)

# even the darkest suit pixels keep a faint glyph so the silhouette stays readable
t = FLOOR + (1 - FLOOR) * t

glyphs, tones = [], []
for r in range(ROWS):
    g, k = [], []
    for c in range(COLS):
        if not subj[r, c]:
            g.append(" ")
            k.append(" ")
            continue
        v = float(t[r, c])
        g.append(RAMP[min(int(v * len(RAMP)), len(RAMP) - 1)])
        k.append(str(min(int(v * LEVELS), LEVELS - 1)))
    glyphs.append("".join(g).rstrip())
    tones.append("".join(k).rstrip())

os.makedirs("data", exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"cols": COLS, "rows": ROWS, "levels": LEVELS, "glyphs": glyphs, "tones": tones}, f, indent=1)

print(f"wrote {OUT}: {COLS} x {ROWS}")
for line in glyphs:
    print(line)
