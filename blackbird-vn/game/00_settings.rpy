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
    config.has_sound = True
    config.has_music = True
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
    # 环境音是压在意识下面的那条线，默认给得低；音效比它响一档，不然盖不过海浪。
    # 变量名跟着混音器走：音效那条 mixer 叫 sfx，不叫 sound。
    config.default_music_volume = 0.5
    config.default_sfx_volume = 0.8
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
    # 菜单里的"选中"不走金：图例说金细边＝正在说话的那一位，而 ShowMenu／Preference
    # 这类动作一命中就把按钮标成 selected，设置页和侧栏会满屏发金。
    # 双细线是它自己的形状（悬停＝单粗线）。金只留给发言席和手里的证据。
    selected_background Frame("images/ui/frame_chip_sel_ink.png", 14, 14)
    insensitive_background Frame("images/ui/frame_chip.png", 14, 14)
    hover_xoffset 6
    selected_xoffset 6
    insensitive_xoffset 0

style bb_btn_text is bold:
    font bb_sans
    size BB_T_CTRL
    color bb_ink
    hover_underline True
    selected_color bb_ink   # 同上：菜单按钮的选中态靠框形，不靠金
    insensitive_color bb_edge_txt

style bb_tab is button:
    xsize 300
    padding (26, 14)
    background Frame("images/ui/frame_chip.png", 14, 14)
    hover_background Frame("images/ui/frame_chip_hover.png", 14, 14)
    selected_background Frame("images/ui/frame_chip_sel_ink.png", 14, 14)
    insensitive_background Frame("images/ui/frame_chip.png", 14, 14)
    hover_xoffset 14
    selected_xoffset 14

style bb_tab_text is bb_btn_text:
    size BB_T_SUB

# Esc 那一页的侧栏有十一个标签：760 高的区域按默认内边距排到第十一个就出屏，
# "退出游戏"落在玩家够不着的地方。这一列单独收紧，其余菜单照旧。
style bb_tab_nav is bb_tab:
    padding (26, 7)

style bb_tab_nav_text is bb_tab_text:
    size BB_T_LABEL

style bb_slot is button:
    padding (10, 10)
    background Frame("images/ui/frame_chip.png", 14, 14)
    hover_background Frame("images/ui/frame_chip_hover.png", 14, 14)
    selected_background Frame("images/ui/frame_chip_sel_ink.png", 14, 14)
    # 悬停不能只靠"描边变粗"——存档格里挨着的十二格，谁被选中要一眼分得出，
    # 所以给它挪位。网格间距 12，只挪 6，永远碰不到邻格。
    hover_xoffset 6
    hover_yoffset -6

style bb_ev is button:
    padding (20, 9)
    background Frame("images/ui/frame_chip.png", 14, 14)
    hover_background Frame("images/ui/frame_chip_hover.png", 14, 14)
    selected_background Frame("images/ui/frame_chip_sel.png", 14, 14)
    insensitive_background Frame("images/ui/frame_chip.png", 14, 14)
    # 证据栏右界压在安全区边界（xalign 0.95 anchor 1.0 = 1824），往右挪就出界，朝左挪。
    hover_xoffset -10

style bb_ev_text is bb_btn_text:
    size BB_T_LABEL
    # 证据条和发言席走的是 bb_ev／frame_chip_sel，那两处金是有账的：
    # 图例承诺"金细边＝正在说话的那一位"、"纸片：手里的证据，举起来才变金"。
    # 菜单侧刚被改成双细线，这里得把金要回来。
    selected_color bb_gold_dark

# 右上角那排快捷芯片借过 bb_ev 的皮，于是也借走了它的金：开了设置页，"设置"
# 芯片变金；一按"自动"，芯片也变金——可金在这份卷宗里记的是"正在说话的那一位"
# 和"你手里举着的那条"。快捷栏既不是席位也不是证据，选中只该换形状（双细线），
# 不该抢一个有含义的色相。
style bb_qk is bb_ev:
    selected_background Frame("images/ui/frame_chip_sel_ink.png", 14, 14)

style bb_qk_text is bb_ev_text:
    selected_color bb_ink

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


# ---------- 声音 ----------
# 这本子本来没有声音：config.has_sound 一直关着，设置里也不会有音量条。
# 加这一层的理由不是"热闹"，是正文一直在写声音——
#   "窗外传来海浪撞击礁石的声音，规律而沉闷，像某种缓慢的心跳。"（第五章）
#   "大厅里，静得能听见茶凉了、又倒进杯里的声音。"（第四轮）
# 文字把耳朵叫起来了，画面却是干的。环境音压得很低（峰值 -14dBFS，音乐槽默认
# 0.5），它要在意识下面走，一抬就变成风光片。
#
# 这两只"响过没有"的记忆必须是 default，不能在 init python 里赋值。
# init 里造出来的对象，Ren'Py 存档时按"还是 init 那个对象"处理，不当内容写进档——
# 于是 BB_AMB_NOW["file"] 记到哪儿，档里也永远是 None。读档回调拿不到那一首，
# 环境音就只能等下一章的扉页再钉回来，而章节卡不会重画：读档后这一章是静音的。
default BB_AMB_NOW = {"file": None}
default BB_PAGE_NOW = {"key": None}

# 素材一条录音都没有，全由 tools/build_audio.py 合成：网上找的"海浪"十有八九
# 是纪录片片头，一放就把推理压成旅游宣传片。循环做在文件里（频谱法，包络只用
# 整数个周期），Ren'Py 的 loop 是接着重排队列，文件本身接不上的话一听就知道。
init python:
    import os as _os

    # 章节卡钉的那张翻拍就是这一章的地点，环境音直接由它取——
    # 28 张卡各写一个参数，不如在这里查一次表。
    BB_AMB_BY_BG = {
        "bg_dock": "amb_sea", "bg_shore": "amb_sea",
        "bg_corridor": "amb_wind",
        "bg_east_wing": "amb_rain",
        "bg_hall_long": "amb_room", "bg_hall_ring": "amb_room",
        "bg_dining": "amb_room", "bg_study": "amb_room",
        "bg_hangzhou": "amb_room",
    }
    BB_AMB_FILE = {
        "amb_sea": "audio/amb_sea.wav",
        "amb_wind": "audio/amb_wind.wav",
        "amb_rain": "audio/amb_rain.wav",
        "amb_room": "audio/amb_room.wav",
    }

    renpy.music.register_channel("ambience", "music", True)

    # 当前那一首要自己记着，别问引擎：renpy.music.get_playing() 在淡入还没起播、
    # 或者自动播放那样一秒翻三张卡的时候会说"没在放"，于是同一首被反复排进队列，
    # 听着就是一阵抽气。实测第一日连播了 12 次同一条 room。容器本身见上面的 default。
    def bb_is_auto():
        """问的是 store 那个标志，但要经得起"还没开局"：quit 回调会在 start 之前跑
        ——打包器的 compile 子进程就是这么收场的，那时 default 还没落地。"""
        return getattr(store, "bb_auto", False)

    def bb_amb_play(f):
        if BB_AMB_NOW["file"] == f:
            return
        BB_AMB_NOW["file"] = f
        # 自动播放的冒烟测试要能看见这条线走没走：图上看不出海浪。
        if bb_is_auto():
            bb_trace("[AMB] " + f)
        renpy.music.play(f, channel="ambience", fadein=2.0, fadeout=1.2, loop=True)

    def bb_amb_for(snap):
        """按地点换环境音。同一首不重起——卡片一章一张，重起会听出接缝。"""
        if not snap:
            return
        key = BB_AMB_BY_BG.get(_os.path.splitext(_os.path.basename(snap))[0])
        if key:
            bb_amb_play(BB_AMB_FILE[key])

    def bb_amb_after_load():
        """读档时声道是静音的，但记住的那首还在——先清掉再重放，不然这一章没有声音。"""
        f = BB_AMB_NOW["file"]
        BB_AMB_NOW["file"] = None
        if f:
            # 给存读回归留个凭据：这一趟是"从档里认出来的那一首"，不是后面卡片钉上的。
            store.BB_AMB_AT_START = f
            bb_amb_play(f)

    config.after_load_callbacks.append(bb_amb_after_load)

    def bb_amb_at_start():
        """回主菜单会走 full_restart，而引擎在这条路上不 fadeout 任何声道
        （main.py 只在 QuitException 和普通异常两支里停音）——海浪就这么压在封面下。
        start_callbacks 每次重启跑一遍，正好在这儿收掉；读档时它先于 after_load 跑，
        所以不会把上面那条重放抢掉。"""
        if renpy.context()._main_menu:
            renpy.music.stop(channel="ambience", fadeout=1.2)
            BB_AMB_NOW["file"] = None

    config.start_callbacks.append(bb_amb_at_start)

    def bb_restore_prefs():
        """冒烟测试改过 preferences 就得还回去，而且不能等到尾声才还——
        中途崩了、玩家手动退出，那几项已经写进 persistent 了。挂在 quit_callbacks 上。"""
        saved = getattr(store, "BB_PREF_SAVED", None)
        if bb_is_auto() and saved:
            for name, val in zip(["afm_enable", "auto_forward", "afm_time",
                                  "text_cps", "transitions"], saved):
                setattr(preferences, name, val)

    config.quit_callbacks.append(bb_restore_prefs)

    def bb_sfx(name):
        renpy.sound.play("audio/sfx_" + name + ".wav", channel="sound")

    # 翻页声。屏体里的 $ 在重绘时会再执行一次（预测也算一次），所以按卡片去重：
    # 同一张扉页只响一次，换下一章再响。环境音那条踩过同样的坑，见 BB_AMB_NOW。
    def bb_page_sound(key):
        if BB_PAGE_NOW["key"] == key:
            return
        BB_PAGE_NOW["key"] = key
        if bb_is_auto():
            bb_trace("[PAGE] " + key)
        bb_sfx("page")

    def bb_page_after_load():
        """和 BB_AMB_NOW 同一只坑：读档后卡片会重画，但"这一张已经响过"的记忆还在，
        落在哪一章就少哪一章那一记翻页声。"""
        BB_PAGE_NOW["key"] = None

    config.after_load_callbacks.append(bb_page_after_load)


# ---------- 标题屏的一条判据 ----------
# 引擎里没有 FileAvailable() 这种屏函数（试过，报错），所以"有没有档"要自己问
# loadsave。list_slots() 返回非空档位——但它把引擎自己的槽也算进来：
# 一次实测（全新存档目录）里它给了 18 条，全是 _tracesave-* 和 auto-*，
# 一条玩家存的都没有。照搬 bool() 就等于"接着上次读"永远挂在标题屏上，
# 点进去读档页却是十二个空格子。只认玩家那一种名字：纯数字，或"页-号"。
init python:
    from renpy.loadsave import list_slots as _list_slots

    def bb_is_user_slot(name):
        return all(part.isdigit() for part in name.split("-"))

    def bb_has_save():
        return any(bb_is_user_slot(n) for n in _list_slots())
