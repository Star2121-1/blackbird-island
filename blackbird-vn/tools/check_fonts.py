# -*- coding: utf-8 -*-
"""字体覆盖率自检：game/fonts/ 里的子集必须认得 game/*.rpy 里的每一个字。

为什么会写这个：字表是 build_fonts.py 一次性裁的，之后新增的台词和界面文案
不会自动进字体。缺的字不报错，只是渲染成空白——"破绽越多"在页面上读成
"破绽  多"，截图里根本看不出少了东西。

    python blackbird-vn/tools/check_fonts.py

缺字时退出码 1，并列出缺哪些。修法：重跑 tools/build_fonts.py。
若重跑后仍缺，说明源字体本身没有这个字（fonts_src/ 不进版本库）。
"""
import glob
import os
import sys

from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "game", "fonts")

# 手写体只收它自己有的那批汉字，符号与全角数字一律走黑体（见 00_settings 字型段）。
# 所以对手写体只要求"汉字必须在"，符号缺席是设计而不是事故。
HAND = "MaShanZheng-Regular.ttf"


def corpus():
    chars = set()
    for p in glob.glob(os.path.join(ROOT, "game", "*.rpy")):
        with open(p, encoding="utf-8") as f:
            chars.update(f.read())
    # 空白与换行不是字形，不参与比对。
    return {c for c in chars if not c.isspace()}


def cmap_of(path):
    f = TTFont(path, fontNumber=0)
    out = set()
    for t in f["cmap"].tables:
        out.update(t.cmap.keys())
    f.close()
    return {chr(c) for c in out}


def main():
    text = corpus()
    bad = 0
    for fn in sorted(os.listdir(FONTS)):
        if not fn.lower().endswith((".ttf", ".otf")):
            continue
        have = cmap_of(os.path.join(FONTS, fn))
        if fn == HAND:
            miss = {c for c in text if ord(c) >= 0x4E00 and c not in have}
        else:
            miss = text - have
        if miss:
            bad += 1
            print("MISS %s  %d 个字渲染不出来：%s" % (fn, len(miss), "".join(sorted(miss))))
        else:
            print("ok   %s  (%d 个字形)" % (fn, len(have)))
    if bad:
        print("\n重跑：python blackbird-vn/tools/build_fonts.py")
        return 1
    print("\nall good")
    return 0


if __name__ == "__main__":
    sys.exit(main())
