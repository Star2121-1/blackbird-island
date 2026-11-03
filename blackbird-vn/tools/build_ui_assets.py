# -*- coding: utf-8 -*-
"""生成《黑鸟岛：筛子》的界面素材。全部程序化绘制，可重建，无第三方授权。

基调：档案／卷宗。浅纸压在深照片之上，界面是那份文件，岛是夹进文件的翻拍。
所以这里只画两类东西——纸（带 1px 硬边的九宫格、涂黑条、胶带、装订孔、印章）
和线宽统一的线性图标（48 格、2px 描边、不填充）。

    python blackbird-vn/tools/build_ui_assets.py

"可重建"要说准：随机数是钉死的（random.seed(20091117)），但纸面颗粒、字体描边
这些像素是 Pillow 出的，换一个大版本就会整批重排——实测在这台机器上原样跑一遍
会重写 17 张已经入库的素材，而入库那批是游戏截图与视觉基线比对过的。
所以改一张图时不要整跑，点名只画要改的那一张：

    python - <<'PY'
    import importlib.util, os, sys
    spec = importlib.util.spec_from_file_location('bua', 'tools/build_ui_assets.py')
    m = importlib.util.module_from_spec(spec); sys.argv = ['x']; spec.loader.exec_module(m)
    im, d = m.canvas(44, 44); ...; m.save(im, 'check_full.png')
    PY

跑完用 `git status blackbird-vn/game/images/` 数一下改了几张——多出来的就是顺手换的。
九宫格用整幅纸当源图（Frame 会缩放中区，不会拉出条纹），
所以边框必须是直线——任何撕纸边之类的非均匀轮廓都不能进九宫格。
"""
import glob
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "game", "images", "ui")
FONTS = os.path.join(ROOT, "game", "fonts")
SCAN_SRC = os.path.join(os.path.dirname(ROOT), "vibe_images")


def newest(prefix):
    hits = glob.glob(os.path.join(SCAN_SRC, prefix + "_*.png"))
    return max(hits, key=os.path.getmtime) if hits else None


# ---------- 令牌 ----------
INK = (11, 13, 16)
INK_SOFT = (30, 34, 41)
PAPER = (234, 229, 218)
PAPER_2 = (222, 216, 202)
PAPER_EDGE = (198, 191, 175)
RUST = (181, 52, 42)
RUST_DARK = (110, 29, 24)
GOLD = (201, 162, 39)
COLD = (95, 127, 151)
PENCIL = (122, 122, 118)
WIRE = (104, 104, 100)
WIRE_HI = (186, 186, 180)

def _pick(*names):
    for n in names:
        p = os.path.join(FONTS, n)
        if os.path.exists(p):
            return p
    raise SystemExit("先跑 tools/build_fonts.py，game/fonts/ 还缺字型：" + ", ".join(names))


SERIF = _pick("NotoSerifSC-Regular.ttf", "NotoSansCJKsc-Regular.otf")
SERIF_B = _pick("NotoSerifSC-Bold.ttf", "NotoSerifSC-Regular.ttf", "NotoSansCJKsc-Bold.otf")
HAND = _pick("MaShanZheng-Regular.ttf", "NotoSerifSC-Regular.ttf", "NotoSansCJKsc-Regular.otf")

PAPER_SCAN = None

random.seed(20091117)


def font(path, size):
    return ImageFont.truetype(path, size)


def canvas(w, h, rgba=(0, 0, 0, 0)):
    im = Image.new("RGBA", (w, h), rgba)
    return im, ImageDraw.Draw(im)


def save(im, name):
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    p = os.path.join(OUT, name)
    im.save(p, "PNG", optimize=True)
    print("OK  ", name, im.size)


def speckle(im, amount=10, radius=0.6):
    """纸纤维噪声：先画随机短纤维，再轻微模糊，避免纯随机点状的数码味。"""
    d = ImageDraw.Draw(im)
    w, h = im.size
    for _ in range(int(w * h / 900.0 * amount / 10)):
        x = random.randrange(w)
        y = random.randrange(h)
        ln = random.randrange(2, 9)
        a = random.randrange(360)
        dx = int(ln * math.cos(math.radians(a)) / 2)
        dy = int(ln * math.sin(math.radians(a)) / 2)
        d.line([x - dx, y - dy, x + dx, y + dy], fill=(140, 132, 116, 26), width=1)
    return im.filter(ImageFilter.GaussianBlur(radius))


def blotches(im, n=7):
    """霉斑／水渍：大半径低透明的暖灰团。"""
    w, h = im.size
    ov, d = canvas(w, h)
    for _ in range(n):
        cx = random.randrange(w)
        cy = random.randrange(h)
        r = random.randrange(int(min(w, h) * 0.06), int(min(w, h) * 0.22))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 136, 110, random.randrange(8, 20)))
    ov = ov.filter(ImageFilter.GaussianBlur(r / 2.2))
    im.alpha_composite(ov)
    return im


def paper_sheet(w, h, base=PAPER, edge=True):
    scan = PAPER_SCAN
    if scan is not None:
        im = scan.copy()
        if im.size != (w, h):
            im = im.resize((w, h), Image.LANCZOS)
        im = im.convert("RGBA")
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, w - 1, h - 1], outline=INK + (255,), width=1)
        return im
    im, d = canvas(w, h, base + (255,))
    blotches(im, n=max(4, w // 260))
    speckle(im, amount=10)
    # 四周压暗一点，读作出库时蹭脏
    sh, ds = canvas(w, h)
    for i in range(26):
        a = int(16 * (1 - i / 26.0) ** 2)
        ds.rectangle([i, i, w - 1 - i, h - 1 - i], outline=(120, 112, 96, a), width=1)
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3)))
    if edge:
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, w - 1, h - 1], outline=INK + (255,), width=1)
    return im


# ---------------- 纸框（九宫格源图） ----------------
def build_frames():
    # 主面板：整幅纸 + 2px 硬边 + 内侧 1px 亮线。中区大，缩放到任何尺寸都不出条纹。
    im = paper_sheet(1400, 900)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 1399, 899], outline=INK + (255,), width=2)
    d.rectangle([5, 5, 1394, 894], outline=(255, 255, 255, 60), width=1)
    save(im, "frame_paper.png")

    # 小条（标签／按钮／证据片）：够窄，边缘带只 12px
    im = paper_sheet(180, 64, PAPER_2, edge=False)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 179, 63], outline=INK + (255,), width=2)
    save(im, "frame_chip.png")

    # 悬停不给锈：锈已经留给"静默"，满屏的悬停金边会把语义洗掉。
    # 悬停＝同一种墨，描粗一档、纸面提一档，靠重量与明度区分。
    im = paper_sheet(180, 64, PAPER, edge=False)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 179, 63], outline=INK + (255,), width=3)
    save(im, "frame_chip_hover.png")

    # 选中＝金边，只给"证据拿在手里"。
    im = paper_sheet(180, 64, PAPER, edge=False)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 179, 63], outline=GOLD + (255,), width=3)
    save(im, "frame_chip_sel.png")

    # 反问：冷蓝虚线框。形状也变了，色盲玩家不必靠颜色分辨状态。
    im = paper_sheet(180, 64, PAPER, edge=False)
    d = ImageDraw.Draw(im)
    for x in range(0, 180, 12):
        d.line([x, 1, min(x + 7, 179), 1], fill=COLD + (255,), width=3)
        d.line([x, 62, min(x + 7, 179), 62], fill=COLD + (255,), width=3)
    for y in range(0, 64, 12):
        d.line([1, y, 1, min(y + 7, 63)], fill=COLD + (255,), width=3)
        d.line([178, y, 178, min(y + 7, 63)], fill=COLD + (255,), width=3)
    save(im, "frame_chip_rebut.png")

    # 深色纸面（frame_dark）已经没人用了，别再产出。


# ---------------- 涂黑条（沉默） ----------------
def build_redaction():
    w, h = 400, 64
    im, d = canvas(w, h)
    d.rectangle([0, 14, w, h - 14], fill=(9, 9, 11, 246))
    # 毛边：沿上下沿随机啃几口
    for x in range(0, w, 3):
        if random.random() < 0.42:
            d.rectangle([x, 14 - random.randrange(0, 4), x + 3, 14], fill=(9, 9, 11, random.randrange(90, 200)))
        if random.random() < 0.42:
            y0 = h - 14
            d.rectangle([x, y0, x + 3, y0 + random.randrange(0, 4)], fill=(9, 9, 11, random.randrange(90, 200)))
    im = im.filter(ImageFilter.GaussianBlur(0.5))
    save(im, "redaction.png")


# ---------------- 印章 ----------------
def stamp_base(size, text, color, shape="circle", angle=-7, weight=3):
    im, d = canvas(size, size)
    c = color + (255,)
    m = weight + 5
    if shape == "circle":
        d.ellipse([m, m, size - m, size - m], outline=c, width=weight)
        d.ellipse([m + 9, m + 9, size - m - 9, size - m - 9], outline=c, width=1)
    else:
        d.rectangle([m, m + size // 6, size - m, size - m - size // 6], outline=c, width=weight)
    fs = int(size * (0.34 if len(text) <= 2 else 0.26))
    f = font(SERIF_B, fs)
    tw = d.textbbox((0, 0), text, font=f)
    d.text(((size - (tw[2] - tw[0])) / 2 - tw[0], (size - (tw[3] - tw[1])) / 2 - tw[1]),
           text, font=f, fill=c)
    # 墨不匀：拿噪声当蒙版啃掉一部分
    mask = Image.effect_noise((size, size), 118).convert("L")
    mask = mask.point(lambda v: 255 if v > 96 else 0)
    ink = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ink.paste(im, (0, 0), im)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(ink, (0, 0), Image.composite(mask, Image.new("L", (size, size), 0), mask))
    out = out.rotate(angle, resample=Image.BICUBIC, expand=False)
    return out


def build_stamps():
    save(stamp_base(200, "静默", RUST, "circle", -8, 4), "stamp_silence.png")
    save(stamp_base(200, "反问", COLD, "circle", 6, 4), "stamp_rebut.png")
    save(stamp_base(220, "副本", RUST_DARK, "rect", -5, 3), "stamp_copy.png")
    save(stamp_base(160, "举", GOLD, "circle", -10, 3), "stamp_hold.png")
    save(stamp_base(200, "未用", PENCIL, "rect", 4, 2), "stamp_unused.png")


# ---------------- 五金 ----------------
def build_hardware():
    # 回形针：金属丝要有明暗，纯纸色压在浅纸上等于看不见
    im, d = canvas(56, 150)
    w = 3
    d.line([14, 26, 14, 116], fill=WIRE + (255,), width=w)
    d.arc([14, 104, 42, 132], 0, 180, fill=WIRE + (255,), width=w)
    d.line([42, 118, 42, 34], fill=WIRE + (255,), width=w)
    d.arc([18, 12, 38, 32], 180, 360, fill=WIRE + (255,), width=w)
    d.line([18, 22, 18, 96], fill=WIRE + (235,), width=w)
    for x, y0, y1 in ((14, 30, 112), (42, 114, 38), (18, 26, 92)):
        d.line([x - 1, y0, x - 1, y1], fill=WIRE_HI + (235,), width=1)
    save(im.filter(ImageFilter.GaussianBlur(0.3)), "clip.png")

    # 装订孔：小一圈，带毛边——太大了就成了一坨黑点。
    # 外圈描一道纸色：孔要落在深照片上，没有这一圈就只剩一个看不见的黑点。
    im, d = canvas(30, 30)
    d.ellipse([3, 3, 27, 27], outline=PAPER + (255,), width=2)
    d.ellipse([5, 5, 25, 25], fill=(16, 15, 14, 235))
    d.ellipse([6, 6, 24, 24], outline=(255, 255, 255, 80), width=1)
    for a in range(0, 360, 17):
        r1 = 10 + random.randrange(2, 5)
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        d.line([15 + 10 * ca, 15 + 10 * sa, 15 + r1 * ca, 15 + r1 * sa],
               fill=PAPER_EDGE + (215,), width=1)
    save(im, "hole.png")

    # 胶带：压在照片角上的，透明度要够；两端斜切，上沿亮线下沿暗
    im, d = canvas(300, 62)
    d.polygon([(10, 4), (292, 0), (290, 58), (4, 62)], fill=(226, 224, 198, 165))
    d.line([10, 4, 292, 0], fill=(255, 255, 255, 190), width=2)
    d.line([4, 62, 290, 58], fill=(120, 116, 92, 160), width=2)
    for x in range(14, 288, 7):
        d.line([x, 8, x - 3, 54], fill=(255, 255, 255, 34), width=2)
    save(im, "tape.png")

    # 清单框：空 / 勾 / 划线（已取）
    # 勾用墨，不用锈——锈在这套界面里只有一个意思："被问到停下来"。
    # 一个"开关打开了"的勾不是沉默；有勾／没勾本身就是形状差别，不需要再加一种颜色。
    for name, tick in (("check_empty", False), ("check_full", True)):
        im, d = canvas(44, 44)
        d.rectangle([5, 5, 39, 39], outline=INK + (255,), width=2)
        if tick:
            d.line([9, 24, 18, 34], fill=INK + (255,), width=4)
            d.line([18, 34, 38, 8], fill=INK + (255,), width=4)
        save(im, name + ".png")


# ---------------- 线性图标 ----------------
IC = 48
STROKE = 3


def ic():
    im, d = canvas(IC, IC)
    return im, d


def finish(im, name):
    save(im.filter(ImageFilter.GaussianBlur(0.25)), name)


def line(d, pts, col=INK, w=STROKE):
    d.line(pts, fill=col + (255,), width=w, joint="curve")


def build_icons():
    col = INK

    # 放大镜
    im, d = ic()
    d.ellipse([9, 9, 31, 31], outline=col + (255,), width=STROKE)
    line(d, [28, 28, 40, 40], col)
    finish(im, "ic_search.png")

    # 纸页（证据通用）
    im, d = ic()
    line(d, [12, 8, 30, 8], col)
    line(d, [30, 8, 38, 16], col)
    line(d, [38, 16, 38, 40], col)
    line(d, [38, 40, 12, 40], col)
    line(d, [12, 40, 12, 8], col)
    line(d, [30, 8, 30, 16, 38, 16], col)
    finish(im, "ic_page.png")

    # 时钟
    im, d = ic()
    d.ellipse([8, 8, 40, 40], outline=col + (255,), width=STROKE)
    line(d, [24, 24, 24, 14], col, 2)
    line(d, [24, 24, 32, 28], col, 2)
    finish(im, "ic_clock.png")

    # 信封（邀请函）
    im, d = ic()
    line(d, [8, 14, 40, 14, 40, 34, 8, 34, 8, 14], col)
    line(d, [8, 15, 24, 27, 40, 15], col)
    finish(im, "ic_envelope.png")

    # 钥匙
    im, d = ic()
    d.ellipse([8, 24, 24, 40], outline=col + (255,), width=STROKE)
    line(d, [22, 28, 40, 10], col)
    line(d, [33, 17, 38, 22], col)
    line(d, [28, 22, 33, 27], col)
    finish(im, "ic_key.png")

    # 锁：梁要明显高出锁体，不然读成文件夹
    im, d = ic()
    d.arc([15, 6, 33, 24], 180, 360, fill=col + (255,), width=STROKE)
    line(d, [15, 15, 15, 24], col)
    line(d, [33, 15, 33, 24], col)
    line(d, [10, 23, 38, 23, 38, 41, 10, 41, 10, 23], col)
    d.ellipse([22, 29, 26, 33], fill=col + (255,))
    line(d, [24, 32, 24, 37], col, 2)
    finish(im, "ic_lock.png")

    # 指纹：外廓是拱加两条直边，里面三道脊和一个中心卷
    im, d = ic()
    d.arc([8, 6, 40, 38], 180, 360, fill=col + (255,), width=STROKE)
    line(d, [8, 22, 8, 40], col)
    line(d, [40, 22, 40, 40], col)
    for r in (6, 11):
        d.arc([24 - r, 22 - r, 24 + r, 22 + r], 190, 350, fill=col + (255,), width=2)
    d.arc([20, 18, 28, 26], 200, 20, fill=col + (255,), width=2)
    finish(im, "ic_fingerprint.png")

    # 日记本
    im, d = ic()
    line(d, [12, 8, 38, 8, 38, 40, 12, 40, 12, 8], col)
    line(d, [18, 8, 18, 40], col)
    line(d, [24, 16, 33, 16], col, 2)
    line(d, [24, 23, 33, 23], col, 2)
    finish(im, "ic_diary.png")

    # 名单（两列）
    im, d = ic()
    line(d, [8, 8, 40, 8, 40, 40, 8, 40, 8, 8], col)
    for y in (16, 23, 30, 37):
        line(d, [13, y, 21, y], col, 2)
        line(d, [26, y, 35, y], col, 2)
    finish(im, "ic_roster.png")

    # 沙漏（时间窗）
    im, d = ic()
    line(d, [14, 8, 34, 8], col)
    line(d, [14, 40, 34, 40], col)
    line(d, [16, 8, 24, 24, 32, 8], col, 2)
    line(d, [16, 40, 24, 24, 32, 40], col, 2)
    finish(im, "ic_hourglass.png")

    # 引号（一句话）
    im, d = ic()
    for x in (10, 26):
        d.arc([x, 12, x + 14, 26], 90, 300, fill=col + (255,), width=STROKE)
        line(d, [x + 2, 24, x + 2, 34], col, STROKE)
    finish(im, "ic_quote.png")

    # 橡皮擦（被擦掉的名字）
    im, d = ic()
    d.polygon([(10, 34), (28, 10), (40, 18), (22, 42)], outline=col + (255,), width=STROKE)
    line(d, [10, 34, 22, 42], col)
    finish(im, "ic_erased.png")

    # 批注：一支笔尖朝下的钢笔，斜线读起来像被划掉
    im, d = ic()
    line(d, [30, 8, 40, 18], col)
    line(d, [12, 26, 30, 8, 40, 18, 22, 36, 12, 26, 12, 26], col)
    line(d, [12, 26, 8, 40, 22, 36], col, 2)
    line(d, [17, 31, 27, 41], col, 2)
    finish(im, "ic_pen.png")

    # 涂黑（静默图例）
    im, d = ic()
    d.rectangle([6, 20, 42, 30], fill=col + (255,))
    finish(im, "ic_silence.png")

    # 反问图例：一个真正的问号（拱 + 斜收 + 点）
    im, d = ic()
    d.arc([14, 8, 34, 26], 160, 20, fill=col + (255,), width=STROKE)
    line(d, [33, 21, 24, 27, 24, 33], col)
    d.rectangle([21, 38, 27, 44], fill=col + (255,))
    finish(im, "ic_rebut.png")

    # 对勾 / 叉 / 箭头
    im, d = ic()
    line(d, [10, 26, 20, 36, 38, 12], col, 4)
    finish(im, "ic_check.png")

    im, d = ic()
    line(d, [12, 12, 36, 36], col, 4)
    line(d, [36, 12, 12, 36], col, 4)
    finish(im, "ic_close.png")

    im, d = ic()
    line(d, [10, 24, 34, 24], col, 3)
    line(d, [26, 14, 38, 24, 26, 34], col, 3)
    finish(im, "ic_next.png")

    # 存 / 读
    im, d = ic()
    line(d, [10, 10, 32, 10, 38, 16, 38, 38, 10, 38, 10, 10], col)
    line(d, [16, 10, 16, 20, 32, 20, 32, 10], col, 2)
    d.rectangle([16, 26, 32, 38], outline=col + (255,), width=2)
    finish(im, "ic_save.png")

    im, d = ic()
    line(d, [10, 14, 20, 14, 24, 10, 38, 10, 38, 38, 10, 38, 10, 14], col)
    line(d, [24, 30, 24, 18], col, 3)
    line(d, [18, 24, 24, 18, 30, 24], col, 3)
    finish(im, "ic_load.png")

    # 设置 / 家 / 历史 / 自动 / 跳过 / 警告
    # 设置：推子（三条横线各带一个环），齿轮画出来像太阳
    im, d = ic()
    for y, kx in ((13, 30), (24, 15), (35, 33)):
        line(d, [7, y, kx - 6, y], col, 2)
        line(d, [kx + 6, y, 41, y], col, 2)
        d.ellipse([kx - 6, y - 6, kx + 6, y + 6], outline=col + (255,), width=2)
    finish(im, "ic_gear.png")

    im, d = ic()
    line(d, [8, 24, 24, 8, 40, 24], col)
    line(d, [13, 24, 13, 40, 35, 40, 35, 24], col)
    finish(im, "ic_home.png")

    # 历史：表盘 + 左侧一段回拨箭头，别和 ic_clock 撞
    im, d = ic()
    d.arc([12, 10, 40, 38], 120, 60, fill=col + (255,), width=STROKE)
    line(d, [26, 26, 26, 17], col, 2)
    line(d, [26, 26, 33, 30], col, 2)
    line(d, [12, 12, 8, 20, 17, 21], col, 2)
    finish(im, "ic_history.png")

    im, d = ic()
    line(d, [8, 12, 22, 24, 8, 36], col, 4)
    line(d, [26, 12, 40, 24, 26, 36], col, 4)
    finish(im, "ic_auto.png")

    im, d = ic()
    line(d, [8, 12, 22, 24, 8, 36], col, 4)
    line(d, [24, 12, 38, 24, 24, 36], col, 4)
    d.line([42, 10, 42, 38], fill=col + (255,), width=3)
    finish(im, "ic_skip.png")

    im, d = ic()
    line(d, [24, 8, 42, 38, 6, 38, 24, 8], col)
    line(d, [24, 18, 24, 28], col, 3)
    d.rectangle([22, 32, 27, 36], fill=col + (255,))
    finish(im, "ic_warn.png")

    # 存档位上的“空”
    im, d = ic()
    d.ellipse([10, 10, 38, 38], outline=PENCIL + (255,), width=2)
    finish(im, "ic_empty.png")

    # ---- 证据专用：这四件原来都借通用图标，图鉴上八条里四条长一个样 ----
    # 缆绳：盘一圈，绳头从圈里挑出来（旧缆桩上解开的那根）
    im, d = ic()
    d.ellipse([12, 24, 34, 40], outline=col + (255,), width=STROKE)
    line(d, [16, 27, 12, 16, 20, 8], col)
    finish(im, "ic_rope.png")

    # 水渍：地上一摊，上面两滴还在落
    im, d = ic()
    d.ellipse([8, 28, 40, 41], outline=col + (255,), width=STROKE)
    line(d, [19, 9, 16, 17], col, 2)
    line(d, [30, 13, 27, 21], col, 2)
    finish(im, "ic_stain.png")

    # 照片：白边相框里一座山一轮日（书房那四张）
    im, d = ic()
    line(d, [8, 12, 40, 12, 40, 36, 8, 36, 8, 12], col)
    d.ellipse([14, 17, 21, 24], outline=col + (255,), width=2)
    line(d, [11, 33, 21, 23, 27, 29, 33, 22, 38, 33], col, 2)
    finish(im, "ic_photo.png")

    # 烟灰：半截烟横搁、滤口一道圈，下面三粒灰（袖口那一截）
    im, d = ic()
    line(d, [8, 20, 34, 20], col, 4)
    line(d, [27, 16, 27, 24], col, 2)
    for x, y in [(13, 30), (22, 36), (30, 31)]:
        d.rectangle([x, y, x + 3, y + 3], fill=col + (255,))
    finish(im, "ic_ash.png")


# ---------------- 席位图 ----------------
def seat_positions(n=8, cx=0.5, cy=0.47, rx=0.285, ry=0.200):
    """与 02_screens.rpy 的 SEAT_POS 同一套算法：横向等距，y 由椭圆反解。
    等角度排会在两端把名牌挤叠，横向等距才保证邻座不碰。
    右端收在 0.775：再往外，第八席要和证据轨重叠 36px。"""
    out = []
    for k in range(n):
        x = 0.205 + 0.570 * k / max(1, n - 1)
        g = max(0.0, 1.0 - ((x - cx) / rx) ** 2) ** 0.5
        out.append((x, cy - ry * g))
    return out


def build_table(cx=0.5, cy=0.47, rx=0.258, ry=0.205, n=8):
    """墨线画的椭圆桌 + 八条席位线。席位线对准 SEAT_POS 的真实名牌位。
    对质是卷宗里的一张示意图，所以线是墨色，压在纸上而不是压在照片上。
    席次号只写在名牌上；桌子里侧再印一遍是重复，椅子方框会被名牌整个盖住。
    """
    W, H = 1920, 1080
    im, d = canvas(W, H)
    cx, cy = int(cx * W), int(cy * H)
    rxp, ryp = int(rx * W), int(ry * H)
    d.ellipse([cx - rxp, cy - ryp, cx + rxp, cy + ryp], fill=(198, 191, 175, 86),
              outline=INK + (235,), width=2)
    d.ellipse([cx - rxp + 26, cy - ryp + 20, cx + rxp - 26, cy + ryp - 20],
              outline=INK + (95,), width=1)
    for sx, sy in seat_positions(n):
        dx, dy = sx * W - cx, sy * H - cy
        ln = math.hypot(dx, dy)
        if ln < 1:
            continue
        ux, uy = dx / ln, dy / ln
        # 桌沿在该方向上的交点：椭圆参数化解出 s，席位线从桌沿往内 26px
        s = 1.0 / math.sqrt((ux * W / rxp) ** 2 + (uy * H / ryp) ** 2)
        d.line([cx + ux * s - ux * 4, cy + uy * s - uy * 4,
                cx + ux * s - ux * 30, cy + uy * s - uy * 30], fill=INK + (170,), width=2)
    save(im, "table_ring.png")


# ---------------- 照片纱 / 颗粒 / 暗角 ----------------
def build_veils():
    W, H = 1920, 1080
    # 贴在卷宗里的翻拍：整幅压一层 55% 纸色纱
    im, d = canvas(W, H)
    d.rectangle([0, 0, W, H], fill=PAPER + (int(255 * 0.30),))
    save(im, "veil_paper.png")

    im, d = canvas(W, H)
    for _ in range(240000):
        x = random.randrange(W)
        y = random.randrange(H)
        v = random.randrange(255)
        d.point((x, y), fill=(v, v, v, 16))
    save(im, "grain.png")

    im, d = canvas(W, H)
    for i in range(90):
        a = int(70 * (1 - i / 90.0) ** 2)
        d.rectangle([-i * 3, -i * 2, W + i * 3, H + i * 2], outline=(6, 7, 9, a), width=3)
    save(im.filter(ImageFilter.GaussianBlur(18)), "vignette.png")

    # 红头栏：3px 锈线，压在纸顶
    im, d = canvas(1200, 6)
    d.rectangle([0, 0, 1200, 6], fill=RUST + (255,))
    save(im, "rule_rust.png")

    # 装订红线：竖 1px
    im, d = canvas(4, 900)
    d.line([2, 0, 2, 900], fill=RUST + (150,), width=2)
    save(im, "rule_bound.png")


# ---------------- 照片白边（把岛压在卷宗里） ----------------
def build_photo_border():
    """相纸冲印边：外 1px 墨线 + 22px 亮边 + 内侧压暗，作九宫格用。"""
    W, H, m = 220, 160, 26
    im, d = canvas(W, H)
    d.rectangle([0, 0, W - 1, H - 1], fill=(246, 244, 238, 255))
    d.rectangle([0, 0, W - 1, H - 1], outline=INK + (255,), width=1)
    d.rectangle([m - 1, m - 1, W - m, H - m], outline=(120, 116, 106, 150), width=1)
    for i in range(4):  # 照片凹进去的一点阴影，只朝内
        a = 46 - i * 11
        d.rectangle([m + i, m + i, W - m - i, H - m - i], outline=(40, 38, 34, a), width=1)
    save(im, "photo_border.png")


# ---------------- 预览拼版 ----------------
def build_preview():
    """把所有素材铺在真纸底上看一遍——图标和印章只有在纸色上才看得出成不成。"""
    names = ["frame_paper", "frame_chip", "redaction", "stamp_silence", "stamp_rebut",
             "stamp_copy", "stamp_hold", "stamp_unused", "clip", "hole", "tape",
             "check_full", "photo_border", "paper_scan_1", "paper_scan_2",
             "abrasion_erase", "ink_blot", "thumbprint", "scratch"]
    cols, cw, chh, pad = 6, 250, 150, 8
    icons = sorted(glob.glob(os.path.join(OUT, "ic_*.png")))
    rows = -(-len(names) // cols) + 1
    H = rows * (chh + 34) + -(-len(icons) // cols) * 66 + 60
    sheet = paper_sheet(1920, H)
    d = ImageDraw.Draw(sheet)
    hf = font(SERIF, 18)
    for i, n in enumerate(names):
        p = os.path.join(OUT, n + ".png")
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert("RGBA")
        im.thumbnail((cw - 10, chh - 10), Image.LANCZOS)
        x = pad + (i % cols) * (cw + pad)
        y = pad + (i // cols) * (chh + 34)
        d.rectangle([x, y, x + cw, y + chh], fill=(246, 244, 238, 255), outline=INK + (90,))
        sheet.alpha_composite(im, (x + (cw - im.size[0]) // 2, y + (chh - im.size[1]) // 2))
        d.text((x + 4, y + chh + 6), n, font=hf, fill=INK + (255,))
    y0 = pad + ((len(names) + cols - 1) // cols) * (chh + 34)
    for i, p in enumerate(icons):
        x = pad + (i % cols) * (cw + pad)
        y = y0 + (i // cols) * 66
        d.rectangle([x, y, x + 56, y + 56], fill=(246, 244, 238, 255), outline=INK + (60,))
        sheet.alpha_composite(Image.open(p).convert("RGBA"), (x + 4, y + 4))
        d.text((x + 64, y + 18), os.path.basename(p), font=hf, fill=INK + (220,))
    out = os.path.join(ROOT, "shots")
    if not os.path.isdir(out):
        os.makedirs(out)
    sheet.save(os.path.join(out, "_ui_assets.png"))
    print("OK   shots/_ui_assets.png", sheet.size)


def build_scans():
    """把生成图里那几张纸和几处墨伤切出来，染成本项目的纸色。

    生成图只当"纹理底片"用：边框、图标、印章一律不靠它。
    找不到生成图就退回程序化纸纹，界面照样能重建。
    """
    global PAPER_SCAN
    import numpy as np
    from scipy import ndimage

    bed = newest("paper-sheets-4")
    if bed:
        im = Image.open(bed).convert("RGB")
        g = np.asarray(im.convert("L"))
        lab, n = ndimage.label(g > 168)
        boxes = []
        for i in range(1, n + 1):
            ys, xs = np.where(lab == i)
            if len(ys) < 60000:
                continue
            boxes.append((int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())))
        boxes.sort(key=lambda b: (b[1] // 100, b[0]))
        print("paper sheets found:", len(boxes))
        for i, b in enumerate(boxes[:4]):
            sh = im.crop(b)
            a = np.asarray(sh.convert("L"), dtype=np.float32) / 255.0
            # 统一到纸色：亮度做底，暖偏按令牌来
            out = np.stack([a * PAPER[0] * 1.06, a * PAPER[1] * 1.0,
                            a * PAPER[2] * 0.93], axis=2).clip(0, 255).astype("uint8")
            o = Image.fromarray(out, "RGB")
            save(o.convert("RGBA"), "paper_scan_%d.png" % (i + 1))
            if i == 0:
                PAPER_SCAN = o.convert("RGBA")
    else:
        print("MISS paper-sheets-4，用程序化纸纹")

    ink = newest("ink-abrasion-4")
    if ink:
        im = Image.open(ink).convert("RGB")
        g = np.asarray(im.convert("L"))
        lab, n = ndimage.label(g < 200)
        parts = []
        for i in range(1, n + 1):
            ys, xs = np.where(lab == i)
            if len(ys) < 8000:
                continue
            parts.append((int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()), len(ys)))
        parts.sort(key=lambda p: -(p[4]))
        names = ["abrasion_erase", "ink_blot", "thumbprint", "scratch"]
        for i, b in enumerate(parts[:4]):
            sh = im.crop(b[:4])
            a = 255 - np.asarray(sh.convert("L"))
            a = (a.astype(np.float32) * (255.0 / max(1.0, a.max()))).clip(0, 255).astype("uint8")
            rgba = np.dstack([np.asarray(sh), a])
            nm = names[i] if i < len(names) else "ink_%d" % i
            save(Image.fromarray(rgba, "RGBA"), nm + ".png")
    else:
        print("MISS ink-abrasion-4")


def build_sel_ink():
    """菜单侧的"选中"（当前页、开着的子菜单）不能借用金框：图例写的是
    "金细边＝正在说话的那一位"，而 ShowMenu／Preference 一命中就把按钮标成
    selected，设置页和侧栏会满屏发金。给它一种自己的形状——双细线：
    悬停是单粗线，选中是双细线，两者都是墨，靠线数分开，不新增色相。

    放在整条流水线的最后、且不在预览表里出现：paper_sheet 会吃随机数，
    插在中间会把后面每一个素材的颗粒噪声换一批。"""
    im = paper_sheet(180, 64, PAPER, edge=False)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 179, 63], outline=INK + (255,), width=2)
    d.rectangle([6, 6, 173, 57], outline=INK + (255,), width=1)
    save(im, "frame_chip_sel_ink.png")


def main():
    build_scans()
    build_frames()
    build_redaction()
    build_stamps()
    build_hardware()
    build_icons()
    build_table()
    build_veils()
    build_photo_border()
    build_preview()
    build_sel_ink()


if __name__ == "__main__":
    main()
