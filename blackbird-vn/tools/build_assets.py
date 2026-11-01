# -*- coding: utf-8 -*-
"""把 vibe_images/ 里的 AI 素材洗成 blackbird-vn/game/images/ 可用的图。

背景：cover 裁切到 1920x1080，输出 jpg。
立绘：边缘泛洪抠底（自适应品红，不假设纯色）+ 去溢色 + 软边，输出带 alpha 的 png。

用法：python blackbird-vn/tools/build_assets.py
"""
import glob
import os
import sys

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "vibe_images")
DST = os.path.join(ROOT, "blackbird-vn", "game", "images")

BG_TARGET = (1920, 1080)
BG_KEYS = ["bg_hangzhou", "bg_dock", "bg_hall_long", "bg_hall_ring", "bg_study"]
SPR_KEYS = ["spr_shen", "spr_wang", "spr_zhao", "spr_fang", "spr_zhou",
            "spr_lin", "spr_su", "spr_me", "spr_gu"]
SPR_HEIGHT = 1080


def latest(prefix):
    hits = glob.glob(os.path.join(SRC, prefix + "_*.png"))
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


def build_sprite(key):
    src = latest(key)
    if not src:
        print("MISS spr", key)
        return False
    im = key_out(src)
    box = im.getbbox()
    im = im.crop(box) if box else im
    s = SPR_HEIGHT / im.size[1]
    im = im.resize((max(1, int(round(im.size[0] * s))), SPR_HEIGHT), Image.LANCZOS)
    im = fade_bottom(im, 90)
    out = os.path.join(DST, key + ".png")
    im.save(out, "PNG", optimize=True)
    print("OK  ", key, im.size, "%d KB" % (os.path.getsize(out) // 1024))
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
