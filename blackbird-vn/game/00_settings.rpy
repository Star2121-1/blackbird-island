# ============================================================
# 样式层：档案／卷宗
# 界面就是那份文件，岛是夹进文件的翻拍。所以浅纸压在深照片上，
# 不是深色面板浮在深色照片上——后者是全片最大的败笔。
#
# 颜色的分工是硬的：
#   纸 = 一切承载文字的面    墨 = 正文与细线，永远不做大块填充
#   锈 = 只给"逼出的沉默"和红头栏线    冷 = 只给"反问"
#   金 = 只给证据，且只在举起来的时候    铅笔 = 只给顾言笙的批注
# 身份不靠每人一个色相，靠姓氏和席次。
# ============================================================

init -1 python:
    import os

    config.screen_width = 1920
    config.screen_height = 1080
    config.has_sound = False
    config.has_music = False
    config.has_voice = False
    config.allow_skipping = True
    config.enter_transition = dissolve
    config.exit_transition = dissolve
    config.after_load_transition = None
    config.window_show_transition = None
    config.window_hide_transition = None
    preferences.text_cps = 32
    preferences.afm_time = 15
    config.default_afm_enable = True
    config.thumbnail_width = 232
    config.thumbnail_height = 122
    # 窗口图标：一枚压在纸上的静默章，由 tools/build_icon.py 从现成素材拼出来，
    # 不是一张独立的美术图——语义要和名牌上的角章是同一枚。
    # 用 png 不用 ico：pygame 的 ico 解码读不了 256 那一条 PNG 压缩的目录项
    # （"Unsupported ICO bitmap format"），整个建窗流程会挂在 GL 性能测试上。
    # icon.ico 仍然生成，那是发行包里 Windows 可图标的料。
    config.window_icon = "icon.png"
    # 回放的容量：一屏一句，六日读下来要能翻回第一日。
    config.history_length = 600


# ---------- 令牌：色 ----------
define bb_paper_3 = "#d3ccbb"   # 滑杆的未走段：比纸深一档，仍在纸族里
define bb_kraft = "#c3b393"
define bb_edge_txt = "#655f52"   # 不可点文字的灰：纸底 5.0:1。原来的 #c6bfaf 只有 1.5:1，已废弃
define bb_ink = "#0b0d10"
define bb_ink_6 = "#0b0d1099"
define bb_rust = "#b5342a"
define bb_rust_dark = "#6e1d18"
define bb_cold_dark = "#33505f"
define bb_gold_dark = "#7a5f0e"   # 纸底 4.8:1，仍读得出金色
define bb_pencil = "#4a4a47"   # 铅笔灰。原来 #5c5c59 在标称纸面上是 4.6:1，
                               # 可微标最常落在牛皮区（实测 #cfbfad）——那里只剩 3.8。
                               # 压到 #4a4a47：牛皮 4.8、纸面 6.9，两边都过 AA。
# 语义锁死：锈＝有人停下来；金＝证据拿在手里／正在说话；冷蓝＝反问；铅笔灰＝顾言笙。
# 其余一律墨色，不给每个角色配一个色相。


# ---------- 令牌：字型 ----------
define bb_serif = "fonts/NotoSerifSC-Regular.ttf"
define bb_serif_b = "fonts/NotoSerifSC-Bold.ttf"
define bb_sans = "fonts/NotoSansCJKsc-Bold.otf"
define bb_hand = "fonts/MaShanZheng-Regular.ttf"
# 手写体只有它自己收的那批字。符号与全角数字一律走 bb_label/bb_micro（黑体），
# bb_note 和 bb_hand 上不出现它们。


# ---------- 令牌：字号 / 间距 / 线宽 ----------
# 七档，别处不许再写裸数字。正文比对白大、对白比按钮大，读的顺序就是排的顺序。
define BB_T_MICRO = 20
define BB_T_LABEL = 24
define BB_T_CTRL = 26
define BB_T_SUB = 28
define BB_T_BODY = 34
define BB_T_TITLE = 56
define BB_T_HERO = 88
define BB_T_COVER = 40   # 只有封面副题用这一档，别处不许

# 三层容器三档内边距，别处不许再自定数字。
define BB_PAD_PAGE = (44, 26)   # 整页纸（对白、发言、结算）
define BB_PAD_SLIP = (22, 16)   # 便签条（提示、批注、图鉴行）
define BB_PAD_CHIP = (12, 8)    # 芯片按钮（证据行、快捷菜单）


# ---------- 令牌：九宫格面 ----------
define BB_PAGE = Frame("images/ui/frame_paper.png", 44, 44)
define BB_SLIP = Frame("images/ui/frame_chip.png", 14, 14)
define bb_slot_cols = 4
define bb_slot_rows = 3
define BB_PLATE = Frame("images/ui/photo_border.png", 26, 26)


# ---------- 基础样式 ----------
style default:
    font bb_serif
    size BB_T_BODY
    color bb_ink

style bold:
    font bb_serif_b

style italic:
    font bb_serif

style say_who is bold:
    size BB_T_SUB
    color bb_ink   # 名字不给锈：锈只说"停下来的人"

style say_what:
    font bb_serif
    size BB_T_BODY
    color bb_ink
    line_spacing 14
    line_leading 2

style bb_label is bold:
    font bb_sans
    size BB_T_LABEL
    color bb_pencil

style bb_micro is bb_label:
    size BB_T_MICRO

style bb_title is bold:
    font bb_serif_b
    size BB_T_TITLE
    color bb_ink

style bb_hero is bold:
    font bb_serif_b
    size BB_T_HERO
    color bb_ink

style bb_body:
    font bb_serif
    size BB_T_BODY
    color bb_ink
    line_spacing 14

style bb_body_sub is bb_body:
    size BB_T_SUB

style bb_hand:
    font bb_hand
    size BB_T_BODY
    color bb_pencil

style bb_note is bb_hand:
    size BB_T_SUB
    color bb_ink   # 手写批注不给锈：锈整本只说一件事

style bb_button_text is bold:
    font bb_sans
    size BB_T_CTRL
    color bb_ink
    hover_underline True
    insensitive_color bb_edge_txt

style bb_seat_text is bold:
    font bb_serif_b
    size BB_T_CTRL
    color bb_ink

style bb_seat_active is bb_seat_text:
    color bb_gold_dark   # 图例说的是"金细边＋发言＝正在说话"，名牌字跟着走

style bb_seat_countered is bb_seat_text:
    color bb_cold_dark

style choice_button is button
style choice_button_text is bb_button_text

# ---------- 按钮：纸片 + 12px 位移，不放大不发光 ----------
style bb_btn is button:
    padding (34, 14)
    background Frame("images/ui/frame_chip.png", 14, 14)
    hover_background Frame("images/ui/frame_chip_hover.png", 14, 14)
    selected_background Frame("images/ui/frame_chip_sel.png", 14, 14)
    insensitive_background Frame("images/ui/frame_chip.png", 14, 14)
    hover_xoffset 6
    selected_xoffset 6
    insensitive_xoffset 0

style bb_btn_text is bold:
    font bb_sans
    size BB_T_CTRL
    color bb_ink
    hover_underline True
    selected_color bb_gold_dark   # 只有"举起来的证据"配得上金
    insensitive_color bb_edge_txt

style bb_tab is button:
    xsize 300
    padding (26, 14)
    background Frame("images/ui/frame_chip.png", 14, 14)
    hover_background Frame("images/ui/frame_chip_hover.png", 14, 14)
    selected_background Frame("images/ui/frame_chip_sel.png", 14, 14)
    insensitive_background Frame("images/ui/frame_chip.png", 14, 14)
    hover_xoffset 14
    selected_xoffset 14

style bb_tab_text is bb_btn_text:
    size BB_T_SUB

style bb_slot is button:
    padding (10, 10)
    background Frame("images/ui/frame_chip.png", 14, 14)
    hover_background Frame("images/ui/frame_chip_hover.png", 14, 14)
    selected_background Frame("images/ui/frame_chip_sel.png", 14, 14)

style bb_ev is button:
    padding (20, 9)
    background Frame("images/ui/frame_chip.png", 14, 14)
    hover_background Frame("images/ui/frame_chip_hover.png", 14, 14)
    selected_background Frame("images/ui/frame_chip_sel.png", 14, 14)
    insensitive_background Frame("images/ui/frame_chip.png", 14, 14)

style bb_ev_text is bb_btn_text:
    size BB_T_LABEL

style bb_bar is bar:
    left_bar bb_ink
    right_bar bb_paper_3
    left_gutter 0
    right_gutter 0
    ysize 14


# ---------- 立绘位置 ----------
# 台词页占下 28%，立绘的脚要站在页面上沿，不然句子正好盖住它说的那只手。
transform bb_talk_r:
    xalign 0.16
    yalign 0.735
    yanchor 1.0
    ysize 760

transform bb_talk_l:
    xalign 0.84
    yalign 0.735
    yanchor 1.0
    ysize 760

transform bb_talk_c:
    xalign 0.5
    yalign 0.735
    yanchor 1.0
    ysize 760


# ---------- 动效 ----------
# 关掉"过渡动画"时，探索的呼吸点退化成常亮，不再动。
transform bb_pulse:
    alpha 0.55
    linear 0.9 alpha 1.0
    linear 0.9 alpha 0.55
    repeat

transform bb_still:
    alpha 0.92


# ---------- 角色 ----------
# who_color 一律墨色：说话人的身份由姓氏 + 席次承担，不由色相承担。
# 锈红整本只说一件事——有人被证据抵住了，停了下来。
define N = Character(None, what_color=bb_ink, what_font=bb_serif)
define SHEN = Character("沈南舟", who_color=bb_ink, what_color=bb_ink, what_font=bb_serif)
define ZHOU = Character("周亦安", who_color=bb_ink, what_color=bb_ink, what_font=bb_serif)
define LIN = Character("林晚", who_color=bb_ink, what_color=bb_ink, what_font=bb_serif)
define SU = Character("苏蔓", who_color=bb_ink, what_color=bb_ink, what_font=bb_serif)
define ZHAO = Character("赵寒", who_color=bb_ink, what_color=bb_ink, what_font=bb_serif)
define FANG = Character("方廷", who_color=bb_ink, what_color=bb_ink, what_font=bb_serif)
define WANG = Character("王剑", who_color=bb_ink, what_color=bb_ink, what_font=bb_serif)
define ME = Character("陈默", who_color=bb_ink, what_color=bb_ink, what_font=bb_serif)
define GU = Character("顾言笙", who_color=bb_pencil, what_color=bb_ink, what_font=bb_serif)
define BB = Character("黑鸟", who_color=bb_ink, what_color=bb_ink, what_font=bb_serif)
