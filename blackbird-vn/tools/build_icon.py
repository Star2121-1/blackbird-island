# -*- coding: utf-8 -*-
"""画窗口图标：一枚压在纸上的静默章。

图标不是美术素材，是从已有素材拼出来的——静默章（game/images/ui/stamp_silence.png）
本来就是这作的胜利条件，拿它当封面最省。改主意要换样式，改这个文件重跑即可。

    python blackbird-vn/tools/build_icon.py
"""
import os

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAMP = os.path.join(ROOT, "game", "images", "ui", "stamp_silence.png")
OUT = os.path.join(ROOT, "game", "icon.ico")
OUT_PNG = os.path.join(ROOT, "game", "icon.png")

SIDE = 256
PAPER = "#eae5da"   # 纸
RUST = "#b5342a"    # 锈：只给"一个人被问到停下来"


def build():
    canvas = Image.new("RGBA", (SIDE, SIDE), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    m = 8
    d.ellipse([m, m, SIDE - m, SIDE - m], fill=PAPER, outline=RUST, width=7)

    stamp = Image.open(STAMP).convert("RGBA").resize((200, 200), Image.LANCZOS)
    # 结算页上那枚章是斜 8° 盖下去的，图标跟着斜，读起来是同一枚。
    stamp = stamp.rotate(8, Image.BICUBIC, expand=True)
    ox = (SIDE - stamp.width) // 2
    oy = (SIDE - stamp.height) // 2
    canvas.alpha_composite(stamp, (ox, oy))

    canvas.save(OUT_PNG)
    canvas.save(OUT, sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print("OK  ", OUT_PNG, round(os.path.getsize(OUT_PNG) / 1024.0, 1), "KB")
    print("OK  ", OUT, round(os.path.getsize(OUT) / 1024.0, 1), "KB")


if __name__ == "__main__":
    build()
