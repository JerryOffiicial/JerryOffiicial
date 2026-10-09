"""Step 3a: remove background, boost contrast (CLAHE), composite on white.
Usage: python scripts/prep_photo.py source-photo.jpg  -> source-prepped.png
"""
import os
import sys
import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

src = sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg"
out = sys.argv[2] if len(sys.argv) > 2 else "source-prepped.png"

# u2net_human_seg (~170 MB) is trained on people. Newer rembg defaults to a 1 GB model.
# On a slow connection, set REMBG_MODEL=u2netp first (~5 MB, slightly rougher edges).
MODEL = os.environ.get("REMBG_MODEL", "u2net_human_seg")

img = Image.open(src).convert("RGBA")
cut = remove(img, session=new_session(MODEL))       # isolate subject
white = Image.new("RGBA", cut.size, (255, 255, 255, 255))
comp = Image.alpha_composite(white, cut).convert("L")  # background -> white

gray = np.array(comp)
mask = np.array(cut.split()[-1]) > 20               # subject pixels only
clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
boosted = clahe.apply(gray)
gray = np.where(mask, boosted, 255).astype(np.uint8)

# crop to subject bounding box with a little padding
ys, xs = np.where(mask)
if len(xs):
    pad = int(0.05 * max(gray.shape))
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, gray.shape[0])
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, gray.shape[1])
    gray = gray[y0:y1, x0:x1]

Image.fromarray(gray).save(out)
print(f"wrote {out} ({gray.shape[1]}x{gray.shape[0]})")
