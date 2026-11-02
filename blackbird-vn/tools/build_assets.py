# -*- coding: utf-8 -*-
"""把 vibe_images/ 里的 AI 素材洗成 blackbird-vn/game/images/ 可用的图。

背景：cover 裁切到 1920x1080，输出 jpg。
立绘：边缘泛洪抠底（自适应品红，不假设纯色）+ 去溢色 + 软边 + 按头高归一化，输出带 alpha 的 png。

用法：python blackbird-vn/tools/build_assets.py
"""
import glob
import os
import re
import sys

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "vibe_images")
DST = os.path.join(ROOT, "blackbird-vn", "game", "images")

BG_TARGET = (1920, 1080)
# 每一条 image bg_* 都得在这儿有名字，反过来也一样：
# 漏了名的图不会被这条管线重建，删空 game/images/ 再跑一次就缺一块，
# 而游戏里那一屏会静默退化成纯色占位——不报错，只是没人知道。
# 名字反过来也要对得上原著：bg_dining（餐厅）和 bg_boathouse（船库）出过又删了，
# 因为终稿从头到尾没有这两个地方——晚餐就在大厅那张长桌（终稿 119），
# 而那张长桌在第一天夜里被撤走换成环形沙发（终稿 898）。
# 造一个原著没有的房间，代价是同一张长桌在玩家眼里变成两个地点。
BG_KEYS = ["bg_hangzhou", "bg_dock", "bg_hall_long", "bg_hall_ring", "bg_study",
           "bg_east_wing", "bg_corridor", "bg_shore",
           "bg_hall_table", "bg_bridge_night", "bg_east_wing_room",
           "bg_manor_ext", "bg_bedroom_day"]

# 按张给一档曝光，不给全局：这套装进游戏之前还要压一层纸纱，而纱压不住高光。
# 量过十三张的平均亮度（0–255）：其余十二张落在 20–85，杭州阅览室那张是 117.9，
# 整片白墙和落地窗，压完纱仍然读起来像一张没洗过的样片，不像"压在纸下的照片"。
# 0.70 把它带到 82，正好回到那一堆里；全局调暗会把最暗那两张（20、25）一起闷死。
BG_EXPOSURE = {"bg_hangzhou": 0.70}
SPR_KEYS = ["spr_shen", "spr_wang", "spr_zhao", "spr_fang", "spr_zhou",
            "spr_lin", "spr_su", "spr_me", "spr_gu"]
# 立绘统一画布 + 统一头高。头高定标，人站同一条底线；画布定宽，头才落在席次上。
SPR_CANVAS = (900, 1080)
SPR_HEAD_H = 300
# 剪影量不准的那几个：竖领把肩线推低（赵寒）、长发披到胸前（苏蔓），手工收一档。
SPR_HEAD_FIX = {
    "spr_su": 0.76,
    "spr_zhao": 0.88,
    "spr_fang": 1.10,
}


def latest(prefix):
    """按名取原图，必须整段对上：文件名是 `<key>_<时间戳>_<hash>.png`。
    以前是 `prefix + "_*.png"` 一把通配，于是 bg_east_wing 把
    bg_east_wing_room 那张也吞进来，还因为对方更新而赢了——
    走廊那张被那间房悄悄盖掉，图上看不出来，只有并排摆着才看得出两张是同一间房。"""
    pat = re.compile(re.escape(prefix) + r"_\d+_[0-9a-f]+\.png$")
    hits = [p for p in glob.glob(os.path.join(SRC, prefix + "_*.png"))
            if pat.match(os.path.basename(p))]
    if not hits:
        return None
    return max(hits, key=os.path.getmtime)


def cover_resize(im, size):
    w, h = im.size
    tw, th = size
    s = max(tw / w, th / h)
    im = im.resize((int(round(w * s)), int(round(h * s))), Image.LANCZOS)
    left = (im.size[0] - tw) // 2
    top = (im.size[1] - th) // 2
    return im.crop((left, top, left + tw, top + th))


def build_bg(key):
    src = latest(key)
    if not src:
        print("MISS bg", key)
        return False
    im = Image.open(src).convert("RGB")
    w, h = im.size
    # 生成图右下角那行水印贴着底边，切掉底部 8% 再 cover，比事后涂掉干净
    im = im.crop((0, 0, w, int(h * 0.92)))
    im = cover_resize(im, BG_TARGET)
    if key in BG_EXPOSURE:
        im = ImageEnhance.Brightness(im).enhance(BG_EXPOSURE[key])
    im = im.filter(ImageFilter.GaussianBlur(0.4))
    out = os.path.join(DST, key + ".jpg")
    im.save(out, "JPEG", quality=86, optimize=True)
    print("OK  ", key, im.size, "%d KB" % (os.path.getsize(out) // 1024))
    return True


def key_out(src, tol=78.0, soft=2.0, bottom_cut=0.885):
    im = Image.open(src).convert("RGB")
    if bottom_cut:
        # 生成图右下角有半透明水印，落在源图 90% 以下；立绘是半身，直接从腰上截掉
        w, h = im.size
        im = im.crop((0, 0, w, int(h * bottom_cut)))
    a = np.asarray(im, dtype=np.int16)
    h, w, _ = a.shape

    ring = np.concatenate([a[0:2].reshape(-1, 3), a[-2:].reshape(-1, 3),
                           a[:, 0:2].reshape(-1, 3), a[:, -2:].reshape(-1, 3)])
    bg = np.median(ring, axis=0)

    dist = np.sqrt(((a - bg) ** 2).sum(axis=2))
    near = dist < tol

    lab, n = ndimage.label(near)
    border_ids = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    border_ids = border_ids[border_ids > 0]
    bgmask = np.isin(lab, border_ids)

    # 内圈还连着边界的"半品红"像素也一起吃掉，防止留一圈粉边
    grow = ndimage.binary_dilation(bgmask, iterations=int(soft))
    loose = (dist < tol * 1.9) & grow & ~bgmask
    bgmask |= loose

    alpha = np.where(bgmask, 0, 255).astype(np.uint8)
    if soft > 0:
        alpha = np.asarray(
            Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(soft * 0.7)))

    out = a.astype(np.uint8).copy()

    # 抠底留下的品红有两处，规则不一样，不能用一个阈值一起扫：
    # 暖色头发和棕衣服的色相也偏红，宽阈值会把它们抹成邻域色。
    #   A 软边：alpha 被高斯糊开的那一圈，RGB 还是原底色 → 按"离底色多远"判。
    #   B 孤岛：泛洪只吃"连着边界"的背景色，夹在发丝之间的那几团留了下来。
    #     底色不是标准品红（实测中位色约 (185,30,105)），所以按"离中位底色多远"判，
    #     内部再收紧一档，免得把暖色头发和嘴唇一起抹掉。
    fringe = (alpha > 0) & (alpha < 240) & (dist < tol * 1.9)
    pocket = (dist < tol * 1.15) & ~bgmask
    fix = fringe | pocket
    good = (alpha > 240) & ~fix
    if fix.any() and good.any():
        # return_distances=False：默认会把距离矩阵排在第一个返回值前面。
        near = ndimage.distance_transform_edt(
            ~good, return_distances=False, return_indices=True)
        out = np.where(fix[:, :, None], out[near[0], near[1]], out)

    # 去溢色：底色渗进发丝是渐变，不是一整块，泛洪和换色都够不着它。
    # 判据用"B 明显高于 G"——皮肤是 B<G、嘴唇是 B≈G，都不会被误伤；
    # 压的是分量不是 alpha，发丝的明暗结构原样留着，只是不再发粉。
    ro = out[:, :, 0].astype(np.int16)
    go = out[:, :, 1].astype(np.int16)
    bo = out[:, :, 2].astype(np.int16)
    spill = (alpha > 0) & (bo > go + 20) & (ro > go + 30)
    out[:, :, 0] = np.where(spill, np.clip(go + 34, 0, 255), ro).astype(np.uint8)
    out[:, :, 2] = np.where(spill, np.clip(go + 26, 0, 255), bo).astype(np.uint8)

    rgba = np.dstack([out, alpha])
    return Image.fromarray(rgba, "RGBA")


def fade_bottom(im, ramp):
    """底边渐隐：半身像的下沿不该是一条硬切口。"""
    arr = np.asarray(im.convert("RGBA"), dtype=np.uint8).copy()
    h = arr.shape[0]
    ramp = min(ramp, h)
    for i in range(ramp):
        y = h - ramp + i
        arr[y, :, 3] = (arr[y, :, 3] * (1.0 - i / float(ramp))).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def measure_head(alpha, probe_h=512):
    """剪影量头：返回 (头顶 y, 头高, 头心 x)，都在 alpha 的原生像素里。

    原先每张立绘各自裁包围盒再统一拉到 1080 高，等于按"这张图里人占多满"定比例。
    九张生成图的取景本来就不一致（有的到腰、有的只到胸），于是头高从 168 到 295
    差一倍多，并排一站方廷像小孩、顾言笙像巨人。改成按头高定标，人才是同一间屋子里的人。

    肩线取"宽度涨得最快的那一行"：头是细的，肩膀突然铺开，斜率峰值就是颈→肩。
    先在固定 512 高上量再换算回原生——直接按原生高度量，五行的滑动窗和 10%／62% 的
    搜索区间会随分辨率漂移，同一张图换个尺寸能差出一倍。
    领子竖起来（赵寒）和长发披到胸前（苏蔓）会把这条线推低，所以留了 SPR_HEAD_FIX。
    """
    h0 = alpha.shape[0]
    small = np.asarray(
        Image.fromarray(alpha).resize((max(1, int(round(alpha.shape[1] * probe_h / float(h0)))),
                                       probe_h), Image.LANCZOS))
    mask = small > 40
    roww = mask.sum(axis=1).astype(float)
    sm = np.convolve(roww, np.ones(5) / 5.0, mode="same")
    nz = np.nonzero(mask.sum(axis=1))[0]
    if not nz.size:
        return 0, 1, 0
    top, bot = int(nz[0]), int(nz[-1])
    span = max(1, bot - top)
    d = np.diff(sm)
    lo = max(1, top + int(span * 0.10))
    hi = min(len(d) - 1, top + int(span * 0.62))
    shoulder = lo + int(np.argmax(d[lo:hi])) if hi > lo else bot
    band = np.nonzero(mask[top:shoulder + 1])[1]
    cx = int((int(band.min()) + int(band.max())) / 2) if band.size else small.shape[1] // 2
    k = h0 / float(probe_h)
    return int(top * k), max(1, int((shoulder - top) * k)), int(cx * k)


def build_sprite(key):
    src = latest(key)
    if not src:
        print("MISS spr", key)
        return False
    im = key_out(src)
    a = np.asarray(im)[:, :, 3]
    top, head_h, cx = measure_head(a)
    head_h = int(round(head_h * SPR_HEAD_FIX.get(key, 1.0)))
    s = SPR_HEAD_H / float(head_h)
    w = max(1, int(round(im.size[0] * s)))
    h = max(1, int(round(im.size[1] * s)))
    im = im.resize((w, h), Image.LANCZOS)
    canvas = Image.new("RGBA", SPR_CANVAS, (0, 0, 0, 0))
    x = int(round(SPR_CANVAS[0] / 2.0 - cx * s))
    y = SPR_CANVAS[1] - h
    canvas.paste(im, (x, y), im)
    head_top = y + int(round(top * s))
    canvas = fade_bottom(canvas, 90)
    out = os.path.join(DST, key + ".png")
    canvas.save(out, "PNG", optimize=True)
    warn = "  ← 顶出画布" if head_top < 0 else ("  ← 左右被切" if x < 0 or x + w > SPR_CANVAS[0] else "")
    print("OK   ", key, "头高 %d→%d 头顶 y=%-5d 身宽 %d%s" %
          (head_h, SPR_HEAD_H, head_top, w, warn),
          "%d KB" % (os.path.getsize(out) // 1024))
    return True


def main():
    os.makedirs(DST, exist_ok=True)
    bad = []
    for k in BG_KEYS:
        if not build_bg(k):
            bad.append(k)
    for k in SPR_KEYS:
        if not build_sprite(k):
            bad.append(k)
    if bad:
        print("缺素材：", ", ".join(bad))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
