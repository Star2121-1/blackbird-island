"""把 shots/*.png 拼成一张联络表，方便一眼看完所有界面。

用法：python blackbird-vn/tools/make_contact.py [每行列数，默认 4]
输出：blackbird-vn/shots/_contact.png
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(ROOT, "shots")
FONT = os.path.join(ROOT, "game", "fonts", "NotoSansCJKsc-Bold.otf")

cols = int(sys.argv[1]) if len(sys.argv) > 1 else 4
files = sorted(f for f in os.listdir(SHOTS)
               if f.endswith(".png") and not f.startswith("_"))
if not files:
    sys.exit("no shots yet — run the BB_SHOT pass first")

scale = 1.0 / cols
cell_w = int(1920 * scale)
cell_h = int(1080 * scale)
pad_t = 34
rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cell_w, rows * (cell_h + pad_t)), (24, 24, 26))
d = ImageDraw.Draw(sheet)
try:
    f = ImageFont.truetype(FONT, 22)
except OSError:
    f = ImageFont.load_default()

for i, name in enumerate(files):
    im = Image.open(os.path.join(SHOTS, name)).convert("RGB")
    im = im.resize((cell_w, cell_h), Image.LANCZOS)
    x = (i % cols) * cell_w
    y = (i // cols) * (cell_h + pad_t)
    d.text((x + 6, y + 4), name, font=f, fill=(230, 226, 216))
    sheet.paste(im, (x, y + pad_t))

out = os.path.join(SHOTS, "_contact.png")
sheet.save(out)
print(out, sheet.size, len(files), "shots")
