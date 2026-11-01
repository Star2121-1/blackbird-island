# -*- coding: utf-8 -*-
"""把全量 Noto Sans CJK 裁成《黑鸟岛》用到的字。

源字体放在 fonts_src/（不进版本库），裁完写到 game/fonts/。
字表 = 全部 .rpy 文本 + 《黑鸟岛-终稿》全文 + ASCII + 中文标点。
终稿全文进字表是有意的：切片台词只做删节、不做增写，
所以整本书的字形一次裁够，后面加章节不用再裁。

    python tools/build_fonts.py
"""
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "fonts_src")
OUT_DIR = os.path.join(ROOT, "game", "fonts")
NOVEL = os.path.join(os.path.dirname(ROOT), "黑鸟岛-终稿.md")

FONTS = ["NotoSansCJKsc-Regular.otf", "NotoSansCJKsc-Bold.otf"]

ALWAYS = (
    "".join(chr(c) for c in range(0x20, 0x7F))
    + "、。，；：？！“”‘’（）《》〈〉【】—…·～-‐‖"
    + "一二三四五六七八九十百千万〇零①②④⑤⑥⑧⑨⑩"
    + "✓＋＋/／％℃"
)


def glyph_text():
    chars = set(ALWAYS)
    paths = glob.glob(os.path.join(ROOT, "game", "*.rpy")) + [NOVEL]
    for p in paths:
        with open(p, encoding="utf-8") as f:
            chars.update(f.read())
    return "".join(sorted(chars))


def main():
    from fontTools import subset

    text = glyph_text()
    print("glyphs:", len(text))
    tmp = os.path.join(SRC_DIR, "glyphs.txt")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    for name in FONTS:
        src = os.path.join(SRC_DIR, name)
        dst = os.path.join(OUT_DIR, name)
        if not os.path.exists(src):
            print("missing", src)
            sys.exit(1)
        subset.main([
            src,
            "--text-file=" + tmp,
            "--output-file=" + dst,
            "--layout-features=*",
            "--glyph-names",
            "--desubroutinize",
            "--no-hinting",
        ])
        print(name, round(os.path.getsize(dst) / 1048576.0, 2), "MB")


if __name__ == "__main__":
    main()
