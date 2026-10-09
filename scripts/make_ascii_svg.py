"""Step 3b: prepped photo -> monochrome ASCII SVG that types itself in row by row.
Usage: python scripts/make_ascii_svg.py [source-prepped.png] [jerry-ascii.svg]
"""
import sys
import numpy as np
from PIL import Image, ImageOps

SRC = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
OUT = sys.argv[2] if len(sys.argv) > 2 else "jerry-ascii.svg"

RAMP = " .`:-=+*cs#%@"      # bright (sparse) -> dark (dense)
COLS = 100
CHAR_W, LINE_H = 6.0, 11.0  # monospace cell; chars are ~2x taller than wide
FILL = "#c9d1d9"
BG = "#0d1117"
ROW_DUR = 0.35              # seconds to wipe one row
ROW_STAGGER = 0.06          # delay between rows

img = Image.open(SRC).convert("L")
img = ImageOps.autocontrast(img, cutoff=1)
rows = max(1, round(COLS * img.height / img.width * CHAR_W / LINE_H))
a = np.asarray(img.resize((COLS, rows), Image.LANCZOS), dtype=np.float32) / 255.0
idx = ((1.0 - a) * (len(RAMP) - 1)).round().astype(int)
lines = ["".join(RAMP[i] for i in r) for r in idx]

# trim fully blank rows top/bottom
while lines and not lines[0].strip():
    lines.pop(0)
while lines and not lines[-1].strip():
    lines.pop()

PAD = 12
W = COLS * CHAR_W + PAD * 2
H = len(lines) * LINE_H + PAD * 2

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}">',
       f'<rect width="100%" height="100%" rx="8" fill="{BG}"/>',
       '<defs>']
for i, _ in enumerate(lines):
    y = PAD + i * LINE_H
    b = i * ROW_STAGGER
    out.append(f'<clipPath id="r{i}"><rect x="{PAD}" y="{y:.1f}" height="{LINE_H}" width="0">'
               f'<animate attributeName="width" from="0" to="{COLS*CHAR_W}" begin="{b:.2f}s" dur="{ROW_DUR}s" fill="freeze"/>'
               f'</rect></clipPath>')
out.append('</defs>')
out.append(f'<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="10" fill="{FILL}" xml:space="preserve">')
for i, line in enumerate(lines):
    if not line.strip():
        continue
    y = PAD + i * LINE_H + LINE_H * 0.8
    out.append(f'<text x="{PAD}" y="{y:.1f}" textLength="{COLS*CHAR_W}" lengthAdjust="spacingAndGlyphs" clip-path="url(#r{i})">{esc(line)}</text>')
    # block cursor riding the wipe edge, hidden once the row is done
    b = i * ROW_STAGGER
    out.append(f'<rect y="{PAD + i*LINE_H + 1:.1f}" width="{CHAR_W}" height="{LINE_H-2}" fill="{FILL}" opacity="0">'
               f'<animate attributeName="x" from="{PAD}" to="{PAD + COLS*CHAR_W}" begin="{b:.2f}s" dur="{ROW_DUR}s" fill="freeze"/>'
               f'<set attributeName="opacity" to="0.9" begin="{b:.2f}s"/>'
               f'<set attributeName="opacity" to="0" begin="{b+ROW_DUR:.2f}s"/></rect>')
out.append('</g></svg>')

open(OUT, "w").write("\n".join(out))
print(f"wrote {OUT} ({len(lines)} rows x {COLS} cols)")
