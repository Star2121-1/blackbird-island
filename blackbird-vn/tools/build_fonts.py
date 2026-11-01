# -*- coding: utf-8 -*-
"""把全量中日韩字体裁成《黑鸟岛》用得上的字。

源字体放在 fonts_src/（不进版本库），裁完写到 game/fonts/。
字表 = 全部 .rpy 文本 + 《黑鸟岛-终稿》全文 + 界面/印章/图例用字 + ASCII + 中文标点。
终稿全文进字表是有意的：切片台词只做删节、不做增写，
所以整本书的字形一次裁够，后面加章节不用再裁。

思源宋是一个可变字体，先按字重钉死成两个静态字面再裁。

    python blackbird-vn/tools/build_fonts.py
"""
import glob
import os
import sys

from fontTools import subset

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "fonts_src")
OUT_DIR = os.path.join(ROOT, "game", "fonts")
NOVEL = os.path.join(os.path.dirname(ROOT), "黑鸟岛-终稿.md")

# (源文件, 输出文件, 需要钉死的可变轴)
JOBS = [
    ("NotoSansCJKsc-Regular.otf", "NotoSansCJKsc-Regular.otf", None),
    ("NotoSansCJKsc-Bold.otf", "NotoSansCJKsc-Bold.otf", None),
    ("NotoSerifSC-wght.ttf", "NotoSerifSC-Regular.ttf", 400),
    ("NotoSerifSC-wght.ttf", "NotoSerifSC-Bold.ttf", 700),
    ("MaShanZheng-Regular.ttf", "MaShanZheng-Regular.ttf", None),
]

ALWAYS = (
    "".join(chr(c) for c in range(0x20, 0x7F))
    + "、。，；：？！“”‘’（）《》〈〉【】—…·～-‐‖「」『』"
    + "一二三四五六七八九十百千万〇零①②④⑤⑥⑧⑨⑩"
    + "✓＋/／％℃"
    # 界面符号：圆点、三角、页码引号、全角数字（档案号用）
    + "▶●○‹›＝０１２３４５６７８９Ｂ／─"
    # 界面与印章用字：这些不出现在小说里，但出现在按钮和图例上
    + "静默反问副本未用举起证据调查离开此处开始设置退出返回继续不拼了"
    + "存档读档历史帮助首页关闭下一句结束本轮第遍在听反驳机会大厅"
    + "章抵达书房名单八个名字已找到还有处看走完才能小标准大"
    + "文字速度自动前进跳过转场安全边减动效键位图例规则说明"
    + "页手稿笔记批注卷宗档案编号日期天气雾岛黑鸟筛子"
)


def glyph_text():
    chars = set(ALWAYS)
    paths = glob.glob(os.path.join(ROOT, "game", "*.rpy")) + [NOVEL]
    for p in paths:
        with open(p, encoding="utf-8") as f:
            chars.update(f.read())
    return "".join(sorted(chars))


def instance(src, dst, weight):
    """可变字体 -> 指定字重的静态字体。"""
    from fontTools import ttLib
    from fontTools.varLib import instancer

    f = ttLib.TTFont(src)
    instancer.instantiateVariableFont(
        f, {"wght": weight}, inplace=True)
    f.save(dst)


def main():
    text = glyph_text()
    print("glyphs:", len(text))
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    tmp = os.path.join(SRC_DIR, "glyphs.txt")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)

    for src_name, out_name, weight in JOBS:
        src = os.path.join(SRC_DIR, src_name)
        if not os.path.exists(src):
            print("SKIP (missing source)", src_name)
            continue
        if weight is not None:
            staged = os.path.join(SRC_DIR, "inst_" + out_name)
            if not os.path.exists(staged):
                instance(src, staged, weight)
            src = staged
        dst = os.path.join(OUT_DIR, out_name)
        subset.main([
            src,
            "--text-file=" + tmp,
            "--output-file=" + dst,
            "--layout-features=*",
            "--glyph-names",
            "--desubroutinize",
            "--no-hinting",
        ])
        print("OK  ", out_name, round(os.path.getsize(dst) / 1048576.0, 2), "MB")


if __name__ == "__main__":
    sys.exit(main())
