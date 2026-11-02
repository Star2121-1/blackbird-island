# ============================================================
# 图像注册：素材在 blackbird-vn/game/images/ 里就用真图，
# 缺图时退回纯色占位，保证在任何机器上都能跑。
# 生成管线：python blackbird-vn/tools/build_assets.py
#
# 场景一律压一层纸纱 + 颗粒：岛是夹进卷宗的翻拍，不是实景。
# 纱做在图里而不是做在屏幕上，换场景、读档、截图都不会漏。
# ============================================================

init python:
    import os

    W, H = config.screen_width, config.screen_height

    def BB_VEILED(what):
        return Composite((W, H),
                         (0, 0), what,
                         (0, 0), Image("images/ui/veil_paper.png"),
                         (0, 0), Image("images/ui/grain.png"))

    def BB_HAS(fname):
        """问引擎，别问文件系统：os.path.exists 只认散文件，
        一旦素材归档（.rpa）或出 Android/iOS/Web 包，全部判 False，
        整屏静默退化成纯色占位——不报错，只是没人知道。"""
        return renpy.loadable("images/" + fname)

    def BB_IMG(fname, placeholder):
        if BB_HAS(fname):
            return BB_VEILED("images/" + fname)
        return BB_VEILED(placeholder)

    def BB_PLAIN(fname, placeholder):
        """立绘不压纱：纸上的人要比纸上的照片亮一档。"""
        return "images/" + fname if BB_HAS(fname) else placeholder

    def BB_SNAP(fname):
        """章节卡上钉的那张翻拍——不压纱的原图。缺图就不钉，卡片照样成版式。"""
        return "images/" + fname if BB_HAS(fname) else None

    def BB_BG(hexcolor, label):
        return Composite((W, H),
                         (0, 0), Solid(hexcolor),
                         (0.5, 0.5), Text(label, size=44, color="#8f8c8588"))

    def BB_SPRITE(hexcolor, glyph):
        return Composite((430, 640),
                         (0, 0), Solid(hexcolor),
                         (0.5, 0.5), Text(glyph, size=160, color="#0b0d1066"))


image bg_hangzhou = BB_IMG("bg_hangzhou.jpg", BB_BG("#101520", "杭州 · 档案馆阅览室"))
image bg_hangzhou_night = BB_IMG("bg_hangzhou_night.jpg", BB_BG("#0a0d14", "杭州 · 夜里的阅览室"))
image bg_dock = BB_IMG("bg_dock.jpg", BB_BG("#141a22", "黑鸟岛 · 码头"))
image bg_hall_long = BB_IMG("bg_hall_long.jpg", BB_BG("#151922", "大厅 · 长桌"))
image bg_hall_ring = BB_IMG("bg_hall_ring.jpg", BB_BG("#0f131b", "大厅 · 环形沙发"))
image bg_hall_table = BB_IMG("bg_hall_table.jpg", BB_BG("#0f131b", "大厅 · 八仙桌"))
image bg_study = BB_IMG("bg_study.jpg", BB_BG("#161420", "书房 · 档案"))
image bg_study_night = BB_IMG("bg_study_night.jpg", BB_BG("#0d0b14", "书房 · 夜"))

image bg_east_wing = BB_IMG("bg_east_wing.jpg", BB_BG("#141821", "东翼 · 封着的走廊"))
image bg_east_wing_room = BB_IMG("bg_east_wing_room.jpg", BB_BG("#12151c", "东翼 · 那一间房"))
image bg_east_wing_room_night = BB_IMG("bg_east_wing_room_night.jpg",
                                       BB_BG("#080a10", "东翼 · 那间房，夜里"))
image bg_corridor = BB_IMG("bg_corridor.jpg", BB_BG("#151a22", "一楼 · 走廊与楼梯"))
image bg_shore = BB_IMG("bg_shore.jpg", BB_BG("#0d1116", "礁石 · 退潮"))
image bg_manor_ext = BB_IMG("bg_manor_ext.jpg", BB_BG("#0e1420", "黑鸟岛 · 从海上看"))
image bg_bedroom_day = BB_IMG("bg_bedroom_day.jpg", BB_BG("#1a1a1e", "客房 · 白昼"))
image bg_bedroom_dusk = BB_IMG("bg_bedroom_dusk.jpg", BB_BG("#141014", "客房 · 傍晚"))
image bg_bridge_night = BB_IMG("bg_bridge_night.jpg", BB_BG("#0a0f16", "临东海大桥 · 雨夜"))

image spr_shen = BB_PLAIN("spr_shen.png", BB_SPRITE("#b5342a", "沈"))
image spr_wang = BB_PLAIN("spr_wang.png", BB_SPRITE("#c96a4a", "王"))
image spr_zhao = BB_PLAIN("spr_zhao.png", BB_SPRITE("#9aa3ad", "赵"))
image spr_fang = BB_PLAIN("spr_fang.png", BB_SPRITE("#a08bb5", "方"))
image spr_zhou = BB_PLAIN("spr_zhou.png", BB_SPRITE("#5f7f97", "周"))
image spr_lin = BB_PLAIN("spr_lin.png", BB_SPRITE("#8fae8b", "林"))
image spr_su = BB_PLAIN("spr_su.png", BB_SPRITE("#c9a227", "苏"))
image spr_me = BB_PLAIN("spr_me.png", BB_SPRITE("#e6e2d8", "默"))
image spr_gu = BB_PLAIN("spr_gu.png", BB_SPRITE("#79b7c6", "顾"))
