# ============================================================
# 屏幕层：主菜单 / 对话框 / 探索 / 圆桌对质 / 拼字 / 证据图鉴
# 交互一律用 "call screen -> _return -> 由 label 推进状态" 的模式，
# 不用响应式状态，避免屏幕不刷新。
# 颜色一律 Solid("#rrggbbaa")，不用 alpha= 参数。
# ============================================================

init python:
    import math

    # 八个人排成上半圈的弧形，下半屏留给台词卡——不要有人坐在句子正上方。
    SEAT_POS = []
    for _k in range(len(SEATS)):
        _a = math.pi + math.pi * (_k + 0.5) / len(SEATS)
        SEAT_POS.append((0.50 + 0.330 * math.cos(_a), 0.470 + 0.250 * math.sin(_a)))

    C_DIM = Solid("#0b0d104d")
    C_DIM4 = Solid("#0b0d1066")
    C_PANEL = Solid("#0b0d10e6")
    C_PANEL9 = Solid("#0b0d10f2")
    C_PANEL8 = Solid("#0b0d10d9")
    C_CARD = Solid("#151922eb")
    C_HIT = Solid("#6e1d18e6")
    C_SPOT = Solid("#b5342acc")
    C_SPOT_HOVER = Solid("#c9a227e6")
    C_CHIP = Solid("#151922d9")
    C_CHIP_ON = Solid("#6e1d18e6")
    C_MASK = Solid("#0b0d109e")
    C_BG = Solid("#0b0d10f7")
    C_AVATAR = Solid("#1b202bf2")
    C_AVATAR_BROKEN = Solid("#3a1512f2")
    C_COUNTER = Solid("#1d2b36e6")

    def BB_SEAT_BG(stt):
        if stt == "broken":
            return C_HIT
        if stt == "countered":
            return C_COUNTER
        if stt == "active":
            return C_CARD
        return C_PANEL8


# ---------------- 对话框（覆盖 Ren'Py 内置 say 屏幕） ----------------
screen say(who, what):
    button:
        xfill True
        yfill True
        background Solid("#00000000")
        action Return()
    frame:
        xsize 1880
        xalign 0.5
        yalign 0.975
        yanchor 1.0
        padding (36, 26)
        background C_PANEL
        has vbox
        spacing 10
        if who:
            text who style "say_who"
        text what style "say_what" id "what"


# ---------------- 主菜单 ----------------
screen bb_main_menu():
    tag menu
    add "bg_hall_ring"
    add C_DIM4
    text "黑鸟岛" xalign 0.5 yalign 0.22 style "bb_title"
    text "筛 子" xalign 0.5 yalign 0.325 size 42 color bb_rust
    text "垂直切片 · 第一章 抵达 / 第三章 书房 / 第六章 大厅第一轮" xalign 0.5 yalign 0.372 style "bb_label"
    vbox:
        xalign 0.5
        yalign 0.63
        spacing 16
        use bb_menu_button("开始", Start())
        use bb_menu_button("证据图鉴", ShowMenu("bb_gallery"))
        use bb_menu_button("设置", ShowMenu("bb_settings"))
        use bb_menu_button("退出", Quit(confirm=True))
    text "赢的方式不是指认谁，是逼出多少沉默。" xalign 0.5 yalign 0.95 style "bb_label"


screen bb_menu_button(label, act):
    textbutton label:
        action act
        text_style "bb_button_text"
        background C_CHIP
        hover_background C_CHIP_ON
        padding (46, 16)


# ---------------- 设置（最小） ----------------
screen bb_settings():
    tag menu
    modal True
    add C_BG
    text "设置" xalign 0.5 yalign 0.14 size 48 color bb_fog font "fonts/NotoSansCJKsc-Bold.otf"
    grid 2 2:
        xsize 900
        xalign 0.5
        yalign 0.38
        spacing 18
        text "文字速度" color bb_fog
        bar value Preference("text speed") xfill True
        text "自动前进" color bb_fog
        bar value Preference("auto-forward time") xfill True
    textbutton "返回" xalign 0.5 yalign 0.72 action Return() text_style "bb_button_text" background C_CHIP hover_background C_CHIP_ON padding (40, 14)


# ---------------- 证据图鉴 ----------------
screen bb_gallery():
    tag menu
    modal True
    add C_BG
    text "证据" xalign 0.5 yalign 0.06 size 44 color bb_fog font "fonts/NotoSansCJKsc-Bold.otf"
    if not have:
        text "还没有任何东西。" xalign 0.5 yalign 0.5 style "bb_label"
    vbox:
        xsize 1500
        xalign 0.5
        yalign 0.16
        spacing 16
        for e in ev_list():
            frame:
                padding (24, 16)
                background C_CARD
                has vbox
                spacing 6
                text e.name color bb_gold font "fonts/NotoSansCJKsc-Bold.otf"
                text e.brief size 26 color bb_fog_dim
                text "—— 手稿 · " + e.chapter size 22 color bb_rust

    textbutton "返回" xalign 0.5 yalign 0.96 action Return() text_style "bb_button_text" background C_CHIP hover_background C_CHIP_ON padding (40, 14)


# ---------------- 章节卡 ----------------
screen bb_card(chapter, title, sub):
    zorder 100
    button:
        xfill True
        yfill True
        background Solid("#0b0d10ff")
        action Return()
    text chapter xalign 0.5 yalign 0.40 size 30 color bb_rust
    text title xalign 0.5 yalign 0.50 style "bb_title"
    text sub xalign 0.5 yalign 0.63 style "bb_label"
    text "点击继续" xalign 0.5 yalign 0.80 style "bb_label"


# ---------------- 探索（点击取证） ----------------
screen bb_explore(bg, spots, found, hint):
    zorder 60
    add bg
    add C_DIM
    frame:
        xsize 1880
        yalign 0.975
        yanchor 1.0
        padding (34, 22)
        background C_PANEL
        has vbox
        spacing 8
        text "调查" style "say_who" color bb_rust
        text hint style "say_what" id "what"
    for s in spots:
        if s["id"] in found:
            text "√" pos (s["x"], s["y"]) anchor (0.5, 0.5) color bb_gold size 34
        else:
            button:
                pos (s["x"], s["y"])
                anchor (0.5, 0.5)
                xsize 46
                ysize 46
                padding (0, 0)
                background C_SPOT
                hover_background C_SPOT_HOVER
                text "+" xalign 0.5 yalign 0.5 color bb_ink size 30
                action Return(("spot", s["id"]))
    text "已找到 " + str(len(found)) + " / " + str(len(spots)) xalign 0.985 yalign 0.04 anchor (1.0, 0.0) style "bb_label"
    textbutton "离开此处" xalign 0.985 yalign 0.09 anchor (1.0, 0.0) action Return(("leave", None)) text_style "bb_button_text" background C_CHIP hover_background C_CHIP_ON padding (26, 10) sensitive (len(found) >= len(spots))


# ---------------- 圆桌对质 ----------------
screen bb_debate(d):
    zorder 60
    add "bg_hall_ring"
    add C_DIM
    text "大厅 · 第一轮" xalign 0.03 yalign 0.04 style "bb_label"
    text "第 " + str(d.passes + 1) + " 遍在听" xalign 0.03 yalign 0.085 style "bb_label"
    text "静默 " + str(d.silence) + " ／ " + str(d.silence_total) xalign 0.97 yalign 0.04 anchor (1.0, 0.0) color bb_rust style "bb_label"
    text "反驳机会 " + str(d.bullets) xalign 0.97 yalign 0.085 anchor (1.0, 0.0) style "bb_label"

    for k, name in enumerate(d.seats):
        $ stt = d.seat_state(name)
        $ p = SEAT_POS[k]
        $ astt = "bb_seat_broken" if stt == "broken" else ("bb_seat_countered" if stt == "countered" else ("bb_seat_active" if stt == "active" else "bb_seat_text"))
        frame:
            pos p
            anchor (0.5, 0.5)
            padding (0, 0)
            background Solid("#00000000")
            has vbox
            spacing 6
            frame:
                xsize 96
                ysize 96
                padding (0, 0)
                background (C_AVATAR_BROKEN if stt == "broken" else C_AVATAR)
                text name[0] xalign 0.5 yalign 0.5 size 46 color (bb_rust if stt == "broken" else bb_fog)
            button:
                padding (16, 7)
                background BB_SEAT_BG(stt)
                hover_background C_CHIP_ON
                action Return(("seat", name))
                text name style astt

    if not d.message:
        add SPR_FOR[d.cur().speaker]:
            xalign 0.70
            xanchor 0.5
            yalign 0.855
            yanchor 1.0
            ysize 420

    frame:
        xsize 900
        xalign 0.245
        yalign 0.835
        yanchor 1.0
        padding (30, 22)
        background C_PANEL
        has vbox
        spacing 10
        text d.cur().speaker style "say_who" color bb_rust
        text d.cur().text style "say_what"
        text "第 " + str(d.i + 1) + " ／ " + str(len(d.statements)) + " 句" style "bb_label"

    if d.message:
        frame:
            xsize 800
            xalign 0.755
            yalign 0.835
            yanchor 1.0
            padding (26, 20)
            background C_CARD
            text d.message size 26 color bb_fog

    frame:
        xsize 1920
        yalign 1.0
        yanchor 1.0
        padding (24, 14)
        background C_PANEL9
        has vbox
        spacing 10
        hbox:
            spacing 10
            for e in ev_list():
                textbutton e.name:
                    action Return(("select", e.id))
                    text_style "bb_evidence_text"
                    background (C_CHIP_ON if e.id == d.selected else C_CHIP)
                    padding (22, 10)
        hbox:
            spacing 14
            if d.selected:
                text "举起：" + EVIDENCE[d.selected].name size 24 color bb_fog_dim
            else:
                text "（先举证据，再反驳）" size 24 color bb_fog_dim
            textbutton "反驳" action Return(("rebut", None)) text_style "bb_button_text" background C_CHIP hover_background C_CHIP_ON padding (30, 10)
            textbutton "下一句" action Return(("next", None)) text_style "bb_button_text" background C_CHIP hover_background C_CHIP_ON padding (30, 10)
            textbutton "结束本轮" action Return(("end", None)) text_style "bb_button_text" background C_CHIP hover_background C_CHIP_ON padding (30, 10)


# ---------------- 拼字（第八名被擦） ----------------
screen bb_hangman(hz, picked, msg):
    zorder 60
    add "bg_study"
    add C_MASK
    text "名单 · 第八个名字" xalign 0.5 yalign 0.08 style "bb_label"
    text hz["prompt"] xalign 0.5 yalign 0.15 xsize 1200 text_align 0.5 size 28 color bb_fog
    hbox:
        xalign 0.5
        yalign 0.30
        spacing 16
        for i in range(hz["need"]):
            frame:
                xsize 130
                ysize 130
                padding (0, 0)
                background C_CARD
                if i < len(picked):
                    text picked[i] xalign 0.5 yalign 0.5 size 60 color bb_rust
                else:
                    text "？" xalign 0.5 yalign 0.5 size 44 color bb_fog_dim
    grid 4 3:
        xalign 0.5
        yalign 0.52
        spacing 10
        for c in hz["candidates"]:
            textbutton c:
                action Return(("pick", c))
                text_style "bb_button_text"
                background C_CHIP
                hover_background C_CHIP_ON
                xsize 118
                ysize 84
    if msg:
        text msg xalign 0.5 yalign 0.74 xsize 1300 text_align 0.5 size 26 color bb_fog
    textbutton "不拼了" xalign 0.5 yalign 0.86 action Return(("giveup", None)) text_style "bb_button_text" background C_CHIP hover_background C_CHIP_ON padding (36, 12)


# ---------------- 结算卡 ----------------
screen bb_result(silence, total, lines):
    zorder 70
    add Solid("#0b0d10ff")
    text "第一轮 · 结算" xalign 0.5 yalign 0.16 size 30 color bb_rust
    text str(silence) + " ／ " + str(total) + " 处沉默" xalign 0.5 yalign 0.30 style "bb_title"
    vbox:
        xsize 1400
        xalign 0.5
        yalign 0.46
        spacing 18
        for ln in lines:
            text ln size 28 color bb_fog xalign 0.5 text_align 0.5
    textbutton "继续" xalign 0.5 yalign 0.88 action Return() text_style "bb_button_text" background C_CHIP hover_background C_CHIP_ON padding (40, 14)
