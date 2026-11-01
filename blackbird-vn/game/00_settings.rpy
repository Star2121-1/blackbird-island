# ============================================================
# 黑鸟岛：筛子 —— 全局设定（字体 / 配色 / 基础样式 / 角色）
# 垂直切片 v0.1
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
    preferences.text_cps = 38
    preferences.afm_time = 15


# ---------- 配色：雾、墨、锈红（不用弹丸的粉，用岛的颜色） ----------
define bb_ink = "#0b0d10"
define bb_ink2 = "#151922"
define bb_fog = "#d9d5cb"
define bb_fog_dim = "#8f8c85"
define bb_rust = "#b5342a"
define bb_rust_dark = "#6e1d18"
define bb_cold = "#5f7f97"
define bb_gold = "#c9a227"


# ---------- 基础样式 ----------
style default:
    font "fonts/NotoSansCJKsc-Regular.otf"
    size 30
    color bb_fog

style bold:
    font "fonts/NotoSansCJKsc-Bold.otf"

style say_who is bold:
    size 30
    color bb_fog

style say_what:
    size 30
    color bb_fog
    line_spacing 12
    line_leading 2

style bb_label is bold:
    size 22
    color bb_fog_dim

style bb_title is bold:
    size 64
    color bb_fog

style bb_button_text is bold:
    size 26
    color bb_fog
    hover_color bb_rust

style button:
    padding (14, 8)

style bb_evidence_text is bold:
    size 22
    color bb_gold
    hover_color "#f0d77a"

style bb_seat_text is bold:
    size 22
    color bb_fog_dim

style bb_seat_active is bb_seat_text:
    color bb_fog

style bb_seat_broken is bb_seat_text:
    color bb_rust

style bb_seat_countered is bb_seat_text:
    color bb_cold

style choice_button is button
style choice_button_text is bold:
    size 30
    color bb_fog
    hover_color bb_rust


# ---------- 角色 ----------
transform bb_talk_r:
    xalign 0.16
    yalign 1.0
    ysize 940

transform bb_talk_l:
    xalign 0.84
    yalign 1.0
    ysize 940

define N = Character(None, what_color=bb_fog, what_font="fonts/NotoSansCJKsc-Regular.otf")
define SHEN = Character("沈南舟", who_color=bb_rust, what_color=bb_fog)
define ZHOU = Character("周亦安", who_color=bb_cold, what_color=bb_fog)
define LIN = Character("林晚", who_color="#8fae8b", what_color=bb_fog)
define SU = Character("苏蔓", who_color=bb_gold, what_color=bb_fog)
define ZHAO = Character("赵寒", who_color="#9aa3ad", what_color=bb_fog)
define FANG = Character("方廷", who_color="#a08bb5", what_color=bb_fog)
define WANG = Character("王剑", who_color="#c96a4a", what_color=bb_fog)
define ME = Character("陈默", who_color="#e6e2d8", what_color=bb_fog)
define GU = Character("顾言笙", who_color="#79b7c6", what_color=bb_fog)
define BB = Character("黑鸟", who_color=bb_rust, what_color=bb_fog)
