# ============================================================
# 图像注册：素材在 blackbird-vn/game/images/ 里就用真图，
# 缺图时退回纯色占位，保证切片在任何机器上都能跑。
# 生成管线：python blackbird-vn/tools/build_assets.py
# ============================================================

init python:
    import os

    def BB_IMG(fname, placeholder):
        if os.path.exists(os.path.join(config.gamedir, "images", fname)):
            return "images/" + fname
        return placeholder

    def BB_BG(hexcolor, label):
        return Composite((config.screen_width, config.screen_height),
                         (0, 0), Solid(hexcolor),
                         (0.5, 0.5), Text(label, size=44, color="#8f8c8588"))

    def BB_SPRITE(hexcolor, glyph):
        return Composite((430, 640),
                         (0, 0), Solid(hexcolor),
                         (0.5, 0.5), Text(glyph, size=160, color="#0b0d1066"))


image bg_hangzhou = BB_IMG("bg_hangzhou.jpg", BB_BG("#101520", "杭州 · 档案馆阅览室"))
image bg_dock = BB_IMG("bg_dock.jpg", BB_BG("#141a22", "黑鸟岛 · 码头"))
image bg_hall_long = BB_IMG("bg_hall_long.jpg", BB_BG("#151922", "大厅 · 长桌"))
image bg_hall_ring = BB_IMG("bg_hall_ring.jpg", BB_BG("#0f131b", "大厅 · 环形沙发"))
image bg_study = BB_IMG("bg_study.jpg", BB_BG("#161420", "书房 · 档案"))

image spr_shen = BB_IMG("spr_shen.png", BB_SPRITE("#b5342a", "沈"))
image spr_wang = BB_IMG("spr_wang.png", BB_SPRITE("#c96a4a", "王"))
image spr_zhao = BB_IMG("spr_zhao.png", BB_SPRITE("#9aa3ad", "赵"))
image spr_fang = BB_IMG("spr_fang.png", BB_SPRITE("#a08bb5", "方"))
image spr_zhou = BB_IMG("spr_zhou.png", BB_SPRITE("#5f7f97", "周"))
image spr_lin = BB_IMG("spr_lin.png", BB_SPRITE("#8fae8b", "林"))
image spr_su = BB_IMG("spr_su.png", BB_SPRITE("#c9a227", "苏"))
image spr_me = BB_IMG("spr_me.png", BB_SPRITE("#e6e2d8", "默"))
image spr_gu = BB_IMG("spr_gu.png", BB_SPRITE("#79b7c6", "顾"))
