# ============================================================
# 屏幕层：档案／卷宗
#
# 版式规矩（改界面之前先读这段）：
#   1. 一切承载文字的面都是纸，纸永远 100% 不透明，不加玻璃态、不加模糊。
#   2. 照片只在两种地方出现：整屏的底（压一层纸纱），和钉在纸上的翻拍（白边相纸）。
#   3. 所有静态元素落在 5%–95% 的安全区里，不给电视留切边的机会。
#   4. 状态不只用颜色：沉默＝涂黑条＋"静默"角章；反问＝虚线框＋"反问"角章；
#      进行中＝金细边＋"发言"二字；已用完＝装订孔。
#   5. 交互一律 "call screen -> _return -> 由 label 推进状态"，不做响应式状态。
# ============================================================

init python:
    import math

    # 八个人按"横向等距"排在桌上弧里：等角度排会挤死两端——椭圆在两头是竖着走的，
    # 名牌却要求水平间距，所以拿 x 反解 y，邻座横向间隔固定 156px，绝不相碰。
    # 右端收到 0.775：再往右，第八席的名牌会和证据轨焊在一起。
    SEAT_POS = []
    for _k in range(len(SEATS)):
        _x = 0.205 + 0.570 * _k / max(1, len(SEATS) - 1)
        _t = (_x - 0.500) / 0.285
        _g = max(0.0, 1.0 - _t * _t) ** 0.5
        SEAT_POS.append((_x, 0.470 - 0.200 * _g))

    BB_CN8 = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]

    def bb_seat_no(name):
        """席次号。身份靠姓氏 + 席位承担，不靠每人一个色相。"""
        if name in SEATS:
            return "第" + BB_CN8[SEATS.index(name)] + "席"
        return ""

    def bb_who(name):
        if not name:
            return ""
        no = bb_seat_no(name)
        return name + ("　·　" + no if no else "")

    def bb_face(name):
        """立绘切出来的头像。名牌位只有一张冲印照那么大。"""
        return "images/faces/" + SPR_FOR.get(name, "spr_me")[4:] + "_face.png"

    BB_PAGE_W = 1300
    BB_PAGE_H = 268
    BB_PAGE_Y = 0.95

    # 证据 → 图标。图鉴和证据条都靠它，缺的一律用"页"。
    EV_ICON = {
        "invite": "envelope",
        "lock": "lock",
        "hand": "fingerprint",
        "note": "page",
        "roster": "roster",
        "diary_fang": "diary",
        "diary_me": "diary",
        "time_window": "hourglass",
        "phrase": "quote",
        "erased8_note": "erased",
        "watch_badge": "key",
        "east_wing_records": "roster",
        "cup_empty": "empty",
        "pos_c_sheet": "page",
        "handbook_blank": "diary",
        "door_mark": "pen",
        "plaque_record": "roster",
        "blank_sheet": "empty",
        "face_photo": "fingerprint",
        "seal_rec": "page",
        "erased8_photo": "erased",
        "blank_col": "empty",
        "cable_cut": "warn",
        "bridge_count": "clock",
        "rope_stale": "warn",
        "cup_mark": "empty",
        "note_hand": "pen",
        "lock_half": "lock",
        "wet_trail": "page",
        "photos": "page",
        "cigarette": "warn",
        "plaque_2013": "roster",
        "envelope": "envelope",
    }

    # Esc 的落点。common 里 _game_menu_screen 初值是 None，不设就按不出菜单。
    _game_menu_screen = "navigation"

    # 快捷菜单是覆盖层，不是剧情屏幕；玩家可以在设置里收起来。
    config.overlay_screens.append("quick_menu")

    class BBToggle(Action):
        """开关一个 store 布尔变量。Preference() 里没有的名字用它。"""

        def __init__(self, var):
            self.var = var

        def __call__(self):
            setattr(store, self.var, not getattr(store, self.var))
            renpy.restart_interaction()

        def get_selected(self):
            return bool(getattr(store, self.var))


default quick_menu = True
default bb_day = ""
default round1 = None
default round2 = None
default round3 = None
default round4 = None
default round5 = None
# 六日对质的总账：赢了几处停顿、一共有几处可赢。
default bb_silence_won = 0
default bb_silence_possible = 0


# ---------------- 共用件 ----------------
screen bb_page_bg():
    """整屏的纸：菜单和示意图用它，对白不用（对白要露出照片）。"""
    add Tile("images/ui/paper_scan_1.png"):
        xysize (1920, 1080)
    add "images/ui/grain.png":
        alpha 0.5


screen bb_head(kicker, title, sub=""):
    """红头栏：档号 + 案名 + 一条 3px 锈线。凡是整页的界面都用它开头。"""
    vbox:
        xalign 0.05
        yalign 0.05
        spacing 8
        hbox:
            spacing 14
            text kicker style "bb_label" color bb_rust
            if sub:
                text sub style "bb_micro"
        text title style "bb_title"
    add "images/ui/rule_rust.png":
        # 锈线跟着纸面走：钉在屏幕右沿的话，会从页面右侧溢出去一截。
        xsize BB_PAGE_W
        xalign 0.5
        yalign 0.185


screen bb_tab_item(label, act):
    textbutton label action act style "bb_tab" text_style "bb_tab_text":
        xalign 1.0


# ---------------- 对白页 ----------------
screen say(who, what):
    button:
        xfill True
        yfill True
        background "#00000000"
        action Return()

    frame:
        xsize BB_PAGE_W
        xalign 0.5
        yalign BB_PAGE_Y
        yanchor 1.0
        padding BB_PAD_PAGE
        background BB_PAGE
        has vbox
        spacing 14
        if who:
            # bb_who 已经把席次写在名字里了，再挂一个灰"第N席"是重复。
            text bb_who(who) style "say_who"
            add "images/ui/rule_rust.png":
                xsize BB_PAGE_W - 88
        text what style "say_what" id "what"
        hbox:
            xalign 1.0
            spacing 12
            text "空格 ／ 点击 继续" style "bb_micro"
            text "›" style "bb_label" color bb_ink


# ---------------- 选项 ----------------
screen choice(items):
    use bb_page_bg()
    use bb_head("卷宗", "岔口")
    vbox:
        xsize 1240
        xalign 0.5
        yalign 0.56
        spacing 16
        for i in items:
            textbutton i.caption action i.action style "bb_btn" text_style "bb_btn_text":
                xalign 0.5


# ---------------- 输入 ----------------
screen input(prompt):
    use bb_page_bg()
    text prompt xalign 0.5 yalign 0.40 xsize 1200 text_align 0.5 style "bb_body"
    frame:
        xsize 700
        xalign 0.5
        yalign 0.52
        padding BB_PAD_SLIP
        background BB_PAGE
        text InputValue() style "bb_body" xalign 0.5 id "input"
    textbutton "确定" action Return() style "bb_btn" text_style "bb_btn_text":
        xalign 0.5
        yalign 0.66


# ---------------- 快捷菜单（右上，绝不压住正文） ----------------
screen quick_menu():
    zorder 100
    if quick_menu:
        hbox:
            xalign 0.95
            yalign 0.05
            spacing 8
            textbutton "日志" action ShowMenu("history") style "bb_ev" text_style "bb_ev_text"
            textbutton "自动" action Preference("auto-forward", "toggle") style "bb_ev" text_style "bb_ev_text"
            textbutton "跳过" action Skip() alternate Skip(fast=True, confirm=True) style "bb_ev" text_style "bb_ev_text"
            textbutton "设置" action ShowMenu("preferences") style "bb_ev" text_style "bb_ev_text"
            textbutton "图例" action ShowMenu("bb_legend") style "bb_ev" text_style "bb_ev_text"
            textbutton "存" action ShowMenu("save") style "bb_ev" text_style "bb_ev_text"
            textbutton "菜单" action ShowMenu("navigation") style "bb_ev" text_style "bb_ev_text"


# ---------------- 主菜单：合着的卷宗封面 ----------------
screen main_menu():
    tag menu

    add Tile("images/ui/paper_scan_2.png"):
        xysize (1920, 1080)
        alpha 0.9
    add bb_kraft:
        # 牛皮纸压 0.55 会把纸面上的 20px 小字一起压到 2.5:1。
        # 封面要的是色调，不是遮罩——压到 0.22 就够把纸纹压平。
        alpha 0.22
    add "images/ui/grain.png"
    add "images/ui/vignette.png":
        alpha 0.5

    vbox:
        xalign 0.06
        yalign 0.075
        spacing 10
        text "档　号　ＢＢ─２００９─１１１７" style "bb_label"
        text "密　级　未解密" style "bb_label" color bb_rust_dark
        text "卷　宗　临东海事件 · 黑鸟岛" style "bb_label"

    add "images/ui/rule_rust.png":
        xsize 1728
        xalign 0.5
        yalign 0.225

    text "黑鸟岛" xalign 0.06 yalign 0.30 style "bb_hero"
    text "筛　子" xalign 0.065 yalign 0.435 size BB_T_COVER color bb_rust_dark font bb_serif_b
    text "一份没有结案的手稿。赢的方式不是指认谁，是逼出多少沉默。" xalign 0.065 yalign 0.525 xsize 780 style "bb_note"

    vbox:
        area (1520, 275, 320, 620)
        spacing 12
        if main_menu:
            use bb_tab_item("从第一日读起", Start())
        else:
            use bb_tab_item("回到刚才", Return())
        use bb_tab_item("证据图鉴", ShowMenu("bb_gallery"))
        use bb_tab_item("怎么读这份卷宗", ShowMenu("help"))
        use bb_tab_item("纸上的记号", ShowMenu("bb_legend"))
        use bb_tab_item("设置", ShowMenu("preferences"))
        if not main_menu:
            use bb_tab_item("回到主菜单", ShowMenu("navigation"))
        use bb_tab_item("退出", Quit(confirm=True))

    text "二〇〇九年十一月十七日 · 临东海 · 黑鸟岛" xalign 0.06 yalign 0.925 style "bb_micro"


# ---------------- 游戏内导航（Esc 落点） ----------------
screen navigation():
    tag menu
    use bb_page_bg()
    use bb_head("卷宗", "合上的一页", "暂停")
    vbox:
        area (1520, 250, 320, 780)
        spacing 8
        use bb_tab_item("继续读", Return())
        use bb_tab_item("存档", ShowMenu("save"))
        use bb_tab_item("读档", ShowMenu("load"))
        use bb_tab_item("已读的话", ShowMenu("history"))
        use bb_tab_item("证据图鉴", ShowMenu("bb_gallery"))
        use bb_tab_item("怎么读这份卷宗", ShowMenu("help"))
        use bb_tab_item("纸上的记号", ShowMenu("bb_legend"))
        use bb_tab_item("设置", ShowMenu("preferences"))
        use bb_tab_item("回到主菜单", MainMenu(confirm=True))
        use bb_tab_item("退出游戏", Quit(confirm=True))

    # 停下来时最该看见的是"我读到哪儿了"，所以这块进度摆在左边空页上。
    frame:
        xsize 460
        xalign 0.06
        yalign 0.34
        padding BB_PAD_SLIP
        background BB_PAGE
        has vbox
        spacing 12
        text "读到" style "bb_label"
        use bb_nav_row("日　期", bb_day if bb_day else "尚未翻开")
        use bb_nav_row("手里的证据", str(len(have)) + " ／ " + str(len(EVIDENCE)))
        if bb_silence_possible:
            use bb_nav_row("逼出的沉默", str(bb_silence_won) + " ／ " + str(bb_silence_possible))
        use bb_nav_row("回放的页数", str(len(_history_list)))

    text "这里没有人被指认。沉默也不是证据。" xalign 0.06 yalign 0.925 style "bb_note"


screen bb_nav_row(k, v):
    hbox:
        xfill True
        spacing 14
        text k xsize 170 style "bb_micro"
        text v style "bb_body_sub"


# ---------------- 菜单外框（save/load/preferences/history 共用） ----------------
screen game_menu(title, scroll=None, yinitial=0.0, padding=0):
    tag menu
    use bb_page_bg()
    use bb_head("卷宗", title)
    add "images/ui/rule_bound.png":
        xsize 3
        ysize 680
        xalign 0.315
        yalign 0.575
        yanchor 0.5
    # 侧栏用 area 钉死。xalign/yalign 的写法在这个界面里对不上——
    # 内容自适应高度的容器，yalign 落点会往上跑，第一项顶到红头栏的标题上。
    vbox:
        area (90, 250, 300, 760)
        spacing 12
        use bb_tab_item("继续读", Return())
        use bb_tab_item("存档", ShowMenu("save"))
        use bb_tab_item("读档", ShowMenu("load"))
        use bb_tab_item("已读的话", ShowMenu("history"))
        use bb_tab_item("证据图鉴", ShowMenu("bb_gallery"))
        use bb_tab_item("怎么读这份卷宗", ShowMenu("help"))
        use bb_tab_item("纸上的记号", ShowMenu("bb_legend"))
        use bb_tab_item("设置", ShowMenu("preferences"))

    frame:
        xsize 1200
        xalign 0.62
        xanchor 0.5
        yalign 0.575
        yanchor 0.5
        ysize 680
        padding BB_PAD_PAGE
        background BB_PAGE
        if scroll == "fixed":
            fixed:
                xfill True
                yfill True
                transclude
        else:
            fixed:
                xfill True
                yfill True
                viewport:
                    xsize 1090
                    ysize 628
                    child_size (1090, None)
                    yinitial yinitial
                    mousewheel True
                    draggable True
                    pagekeys True
                    vbox:
                        xsize 1090
                        spacing 18
                        transclude
                # 翻页提示挪到框内的右上角：压在正文最后一行上，读起来像被裁掉的字。
                text "滚轮 ／ 拖动 翻页" xalign 0.985 yalign 0.015 style "bb_micro"


# ---------------- 存 / 读 ----------------
screen save():
    tag menu
    use file_slots("存档")


screen load():
    tag menu
    use file_slots("读档")


screen file_slots(title):
    default page_name_value = FilePageNameInputValue(pattern=_("第 {} 页"), auto=_("自动存档"), quick=_("快速存档"))
    use game_menu(title, scroll="fixed"):
        vbox:
            xfill True
            yfill True
            spacing 20
            hbox:
                xalign 0.0
                spacing 10
                textbutton "‹" action FilePagePrevious() style "bb_ev" text_style "bb_ev_text"
                textbutton str(FileCurrentPage()) action page_name_value.Toggle() style "bb_ev" text_style "bb_ev_text"
                textbutton "›" action FilePageNext() style "bb_ev" text_style "bb_ev_text"
                text "点空格子存，点已存的格子读。" style "bb_micro" yalign 0.5

            grid bb_slot_cols bb_slot_rows:
                xalign 0.5
                yalign 0.5
                spacing 12
                transpose True
                for i in range(1, bb_slot_cols * bb_slot_rows + 1):
                    button:
                        style "bb_slot"
                        action FileAction(i)
                        has vbox
                        spacing 4
                        add FileScreenshot(i):
                            xsize config.thumbnail_width
                            ysize config.thumbnail_height
                        hbox:
                            spacing 12
                            text FileSlotName(i, bb_slot_cols * bb_slot_rows) style "bb_micro"
                            text FileTime(i, empty=_("空位")) style "bb_micro" color bb_pencil


# ---------------- 设置 ----------------
screen preferences():
    tag menu
    use game_menu("设置", scroll="viewport"):
        text "阅　读" style "bb_label"
        use bb_pref_bar("文字速度", Preference("text speed"))
        use bb_pref_bar("自动前进", Preference("auto-forward time"))
        use bb_pref_bar("字号", Preference("font size"))
        use bb_pref_bar("行距", Preference("font line spacing"))
        use bb_pref_toggle("允许跳过", Preference("skip", "toggle"))

        text "演　出" style "bb_label"
        use bb_pref_toggle("过渡动画", Preference("transitions", "toggle"))
        use bb_pref_toggle("空行显示", Preference("show empty window", "toggle"))

        text "界　面" style "bb_label"
        use bb_pref_toggle("快捷菜单", BBToggle("quick_menu"))
        use bb_pref_toggle("系统光标", Preference("system cursor", "toggle"))
        use bb_pref_toggle("点击后继续自动", Preference("auto-forward after click", "toggle"))

        text "辅　助" style "bb_label"
        use bb_pref_toggle("朗读文本", Preference("self voicing", "toggle"))
        text "对质：先按 Tab 或方向键选中证据，回车举起，再选“反　驳”。" style "bb_micro" xsize 1000

        text "界面按 1920×1080 设计，所有元素留在 5% 安全区内；" style "bb_micro" xsize 1000
        text "窗口缩放由 Ren'Py 整体等比处理，不需要额外的边距滑杆。" style "bb_micro" xsize 1000


screen bb_pref_bar(label, val):
    hbox:
        xfill True
        spacing 18
        text label xsize 220 style "bb_body_sub"
        bar value val xfill True style "bb_bar"


screen bb_pref_toggle(label, val):
    hbox:
        xfill True
        spacing 18
        text label xsize 220 style "bb_body_sub"
        button:
            style "bb_ev"
            action val
            has hbox
            spacing 10
            add ("images/ui/check_full.png" if val.get_selected() else "images/ui/check_empty.png"):
                xysize (24, 24)
                yalign 0.5
            text ("已开" if val.get_selected() else "已关") style "bb_ev_text"


# ---------------- 已读 ----------------
screen history():
    tag menu
    predict False
    use game_menu("已读的话", scroll="viewport", yinitial=1.0):
        if not _history_list:
            text "这一页还是空的。" style "bb_note"
        for h in _history_list:
            vbox:
                xsize 1040
                spacing 4
                if h.who:
                    text h.who style "bb_label" color bb_ink
                text renpy.filter_text_tags(h.what, allow=set()) style "bb_body_sub" xsize 1040 substitute False


# ---------------- 关于 ----------------
screen about():
    tag menu
    use game_menu("这份卷宗", scroll="viewport"):
        text "黑鸟岛：筛子" style "bb_title"
        text "改编自同名长篇推理手稿。台词取自终稿，措辞不改，只删不增。" style "bb_body_sub" xsize 1000
        text "界面是卷宗本身：浅纸压在翻拍的照片上。红头栏、装订孔、涂黑条、印章，都是档案的零件。" style "bb_body_sub" xsize 1000
        text "版本 " + str(config.version) style "bb_micro"


# ---------------- 帮助＝图例 ----------------
screen help():
    tag menu
    use game_menu("怎么读这份卷宗", scroll="viewport"):
        text "规　矩" style "bb_label"
        text "这本书不许你指认谁。你要做的，是看能不能让说话的人停下来。" style "bb_body_sub" xsize 1000
        text "举起一条证据，抵在一句话上。抵对了，那个人会停下来——那一段停顿就是这一局的结果。" style "bb_body_sub" xsize 1000
        text "抵错了用掉一次机会。第一夜三次，往后的每一夜四次——破绽越多，给的余地越大。" style "bb_body_sub" xsize 1000
        text "主人不会沉默，他把问题推回你手上，那一条不算赢。" style "bb_body_sub" xsize 1000

        text "操　作" style "bb_label"
        use bb_key("点击 ／ 空格", "继续下一句")
        use bb_key("Ctrl", "快进")
        use bb_key("Tab", "已读")
        use bb_key("Esc", "合上卷宗（菜单）")
        use bb_key("鼠标", "点座位＝跳到那个人身上")
        use bb_key("方向键 ／ 回车", "菜单、证据栏、名牌都能用键盘走")
        text "记号单独开了一页，快捷栏上的\"图例\"直接跳到那里。" style "bb_micro" xsize 1000


# ---------------- 图例：纸上的记号 ----------------
# 记号不靠颜色区分——颜色在这套界面里只有一个意思。所以每一格摆真图：
# 玩家在游戏里看到的和这里是同一张皮，不是对它的文字描述。
screen bb_legend():
    tag menu
    use game_menu("纸上的记号", scroll="viewport"):
        text "名　牌" style "bb_label"
        use bb_legend_row(Frame("images/ui/frame_chip_sel.png", 14, 14), "", "发言",
                          "金细边：正在说话的那一位。")
        use bb_legend_row("images/ui/redaction.png", "images/ui/stamp_silence.png", "",
                          "涂黑条＋角章：逼出来的沉默。锈色只此一处。")
        use bb_legend_row(Frame("images/ui/frame_chip_rebut.png", 14, 14), "images/ui/stamp_rebut.png", "反问",
                          "虚线框：主人把问题推回你手上。冷蓝只此一处。")
        text "纸　片" style "bb_label"
        use bb_legend_row("images/ui/clip.png", "", "",
                          "回形针夹着的纸片：手里的证据，举起来才变色。", True)
        use bb_legend_row("images/ui/hole.png", "", "",
                          "装订孔：这个地方已经翻过了。", True)
        use bb_legend_row("", "", "铅笔字",
                          "铅笔灰是顾言笙的批注，不是手稿原文。")


screen bb_legend_row(mark, stamp, word, note, fit=False):
    # 六格两组标题，行高 74、组间距 18，加起来 618——视口 628，刚好不用滚。
    # 说明文字一律压到一行：两行会顶穿这一格，和下一格叠在一起。
    frame:
        xsize 960
        ysize 74
        padding (10, 8)
        background BB_SLIP
        has hbox
        spacing 24
        # 样张一律关死在这一格里。原图比格子宽的（涂黑条就是）会顶到右边的说明文字上，
        # 看起来像涂黑条压在字上——记号页自己先得干净。
        fixed:
            xsize 250
            ysize 56
            yalign 0.5
            if mark:
                if fit:
                    add mark:
                        xalign 0.5
                        yalign 0.5
                        ysize 50
                else:
                    add mark:
                        xysize (200, 50)
            if word:
                text word:
                    xalign 0.5
                    yalign 0.5
                    style "bb_body_sub"
            if stamp:
                add stamp:
                    xysize (52, 52)
                    xalign 1.0
                    yalign 0.5
                    anchor (1.0, 0.5)
        text note:
            yalign 0.5
            xsize 660
            style "bb_body_sub"


screen bb_key(k, v):
    hbox:
        spacing 16
        text k xsize 240 style "bb_body_sub"
        text v style "bb_body_sub"


# ---------------- 确认框 ----------------
screen confirm(message, yes_action, no_action):
    modal True
    zorder 200
    style_prefix "confirm"
    add "#0b0d1099"
    frame:
        xsize 860
        xalign 0.5
        yalign 0.5
        padding BB_PAD_PAGE
        background BB_PAGE
        has vbox
        spacing 24
        text message style "bb_body" xsize 760
        hbox:
            xalign 0.5
            spacing 18
            textbutton "是" action yes_action style "bb_btn" text_style "bb_btn_text"
            textbutton "否" action no_action style "bb_btn" text_style "bb_btn_text"


# ---------------- 提示 ----------------
screen notify(message):
    zorder 100
    tag notify
    timer 2.0 action Hide("notify")
    frame:
        xalign 0.5
        xanchor 0.5
        yalign 0.24
        yanchor 0.5
        padding BB_PAD_SLIP
        background BB_SLIP
        text message style "bb_btn_text" color bb_gold_dark


screen skip_indicator():
    zorder 100
    frame:
        xalign 0.95
        yalign 0.93
        padding BB_PAD_CHIP
        background BB_SLIP
        text "正在快进 ››" style "bb_label" color bb_ink


# ---------------- 章节卡：卷宗的扉页 ----------------
screen bb_card(chapter, title, sub, day="", snap=None):
    zorder 100
    $ store.bb_day = day if day else store.bb_day
    if store.bb_auto:
        # 扉页是天然的进度标记：卡在这里，就是这一章的界面没被自动收掉。
        $ bb_trace("[AUTO] " + chapter + "·" + title)
        timer 0.05 action Return()
    use bb_page_bg()
    button:
        xfill True
        yfill True
        background "#00000000"
        action Return()

    $ num = chapter[-2] if chapter.endswith("章") and len(chapter) >= 2 else ""

    text num xalign 0.80 xanchor 0.5 yalign 0.46 yanchor 0.5 size 460 color "#0b0d1012" font bb_serif_b

    vbox:
        xalign 0.06
        yalign 0.075
        spacing 8
        text "档　号　ＢＢ─２００９─１１１７" style "bb_micro"
        if day:
            text day style "bb_label"

    text chapter xalign 0.26 yalign 0.30 style "bb_label" color bb_rust
    text title xalign 0.26 yalign 0.375 style "bb_hero"
    add "images/ui/rule_rust.png":
        xsize 620
        xalign 0.26
        yalign 0.515
    text sub xalign 0.26 yalign 0.565 xsize 820 style "bb_note"

    if snap:
        frame:
            xsize 460
            ysize 330
            xalign 0.94
            xanchor 1.0
            yalign 0.93
            yanchor 1.0
            padding (28, 28)
            background Frame("images/ui/photo_border.png", 30, 30)
            add snap:
                xysize (404, 274)

    hbox:
        xalign 0.26
        yalign 0.86
        spacing 12
        text "点击继续" style "bb_micro"
        # 原来这里是一枚 30×46 的回形针，缩到卡片上只读得出一个竖条。
        # 箭头用 → ——▶ 在这套字体里会被渲成彩色表情符号。
        text "→" style "bb_micro"


# ---------------- 探索：现场翻拍 ----------------
screen bb_explore(bg, spots, found, hint):
    zorder 60
    if store.bb_auto:
        # 探索屏不能一把跳过：破绽句要用的证据就埋在这些坑里。
        # 先把没看过的一个个点完，点干净了才离开。
        $ _left = [s["id"] for s in spots if s["id"] not in found]
        timer 0.05 action (Return(("leave", None)) if not _left
                           else Return(("spot", _left[0])))
    add bg

    frame:
        xsize BB_PAGE_W
        xalign 0.5
        yalign BB_PAGE_Y
        yanchor 1.0
        padding BB_PAD_PAGE
        background BB_PAGE
        has vbox
        spacing 12
        hbox:
            spacing 16
            text "调　查" style "say_who"
            text "亮着的地方还没看过" style "bb_micro" yalign 0.5
            text "看过 " + str(len(found)) + " ／ " + str(len(spots)) style "bb_label" yalign 0.5
        add "images/ui/rule_rust.png":
            xsize BB_PAGE_W - 88
        hbox:
            spacing 30
            text hint style "bb_body_sub" xsize BB_PAGE_W - 420
            textbutton ("离开此处" if len(found) >= len(spots) else "还没看完") action Return(("leave", None)) style "bb_btn" text_style "bb_btn_text":
                yalign 0.5
                sensitive (len(found) >= len(spots))

    for s in spots:
        if s["id"] in found:
            # 装订孔要压在一张纸片上：直接落在深照片里，孔就看不见了。
            add Frame("images/ui/frame_chip.png", 14, 14):
                xysize (46, 46)
                pos (s["x"], s["y"])
                anchor (0.5, 0.5)
            add "images/ui/hole.png":
                xysize (28, 28)
                pos (s["x"], s["y"])
                anchor (0.5, 0.5)
        else:
            # 亮着的坑：92px 的点击区（4.8% 屏宽），图标本身比点小一档，
            # 呼吸的 alpha 告诉玩家"这里还没翻过"。关掉过渡动效时不呼吸。
            button:
                pos (s["x"], s["y"])
                anchor (0.5, 0.5)
                xsize 92
                ysize 92
                padding (0, 0)
                background Frame("images/ui/frame_chip.png", 14, 14)
                hover_background Frame("images/ui/frame_chip_hover.png", 14, 14)
                add "images/ui/ic_search.png" at (bb_pulse if preferences.transitions else bb_still):
                    xysize (44, 44)
                    xalign 0.5
                    yalign 0.5
                action Return(("spot", s["id"]))


# ---------------- 圆桌对质：卷宗里的一张示意图 ----------------
screen bb_debate(d):
    zorder 60
    use bb_page_bg()
    add "images/ui/table_ring.png"

    # 状态条走左上，右上角是快捷菜单的地盘，两处不能叠。
    vbox:
        xalign 0.05
        yalign 0.05
        spacing 8
        text d.label style "bb_label"
        hbox:
            spacing 22
            text "第 " + str(d.passes + 1) + " 遍在听" style "bb_micro"
            text "反驳机会 " + "●" * d.bullets + "○" * max(0, d.max_bullets - d.bullets) style "bb_micro"

    # 桌子正中原本全空。这一局真正的成绩只有一件事，就把它摆在这一圈人中间。
    # 0.375 而不是 0.405：再往下，锈线正好压在桌环的墨线上，读起来像一道划掉的痕迹。
    vbox:
        xalign 0.5
        xanchor 0.5
        yalign 0.36
        yanchor 0.5
        spacing 2
        text "逼出的静默" style "bb_micro" xalign 0.5
        text str(d.silence) + " ／ " + str(d.silence_total) style "bb_hero" color bb_rust xalign 0.5
        add "images/ui/rule_rust.png":
            xsize 300
            xalign 0.5

    for k, name in enumerate(d.seats):
        $ stt = d.seat_state(name)
        use bb_seat(d, name, stt, SEAT_POS[k])

    # ---- 右轨：手里的证据。竖排一列，永远不占发言卡的横向空间 ----
    # 底边停在 760：右下动作面板的上沿在 776 左右，轨一长就压到"反　驳"上面。
    frame:
        xsize 240
        xalign 0.95
        xanchor 1.0
        yalign 0.13
        yanchor 0.0
        ysize 620
        padding BB_PAD_CHIP
        background BB_SLIP
        has vbox
        spacing 8
        text "手里的证据 " + str(len(have)) + " ／ " + str(len(EVIDENCE)) style "bb_micro" xalign 0.5
        viewport:
            ysize 540
            mousewheel True
            draggable True
            has vbox
            spacing 6
            for i, e in enumerate(ev_list()):
                button:
                    style "bb_ev"
                    xfill True
                    padding BB_PAD_CHIP
                    action Return(("select", e.id))
                    selected (d.selected == e.id)
                    has hbox
                    spacing 10
                    add "images/ui/ic_" + EV_ICON.get(e.id, "page") + ".png":
                        xysize (22, 22)
                        yalign 0.5
                    text e.name style "bb_ev_text" xsize 150 yalign 0.5

    # ---- 底栏三格：发言页 ／ 钉着的翻拍 ／ 动作 ----
    frame:
        xsize 1080
        xalign 0.05
        yalign 0.95
        yanchor 1.0
        padding BB_PAD_PAGE
        background BB_PAGE
        has vbox
        spacing 10
        if d.selected:
            # 证据抵在句子上，要看得见"抵"这个动作：金边条夹在发言页右上角。
            hbox:
                xalign 1.0
                spacing 8
                # 用这条证据自己的图标，不用通用回形针：回形针缩到 18 像素
                # 只读得出"一个竖条"，读不出举起来的是哪一件。
                add "images/ui/ic_" + EV_ICON.get(d.selected, "page") + ".png":
                    xysize (26, 26)
                    yalign 0.5
                text EVIDENCE[d.selected].name style "bb_micro" color bb_gold_dark
        text bb_who(d.cur().speaker) style "say_who"
        text d.cur().text style "say_what" xsize 1020
        text "第 " + str(d.i + 1) + " ／ " + str(len(d.statements)) + " 句" style "bb_micro"

    frame:
        xsize 210
        ysize 280
        xalign 0.685
        xanchor 0.5
        yalign 0.95
        yanchor 1.0
        padding BB_PAD_CHIP
        background BB_PLATE
        add bb_face(d.cur().speaker):
            xysize (186, 256)
            xalign 0.5
            yalign 0.5

    frame:
        xsize 300
        xalign 0.95
        xanchor 1.0
        yalign 0.95
        yanchor 1.0
        padding BB_PAD_SLIP
        background BB_PAGE
        has vbox
        spacing 12
        if d.selected:
            text "抵上去" style "bb_micro" color bb_gold_dark
        else:
            text "（先举证据，再反驳）" style "bb_micro"
        textbutton "反　驳" action Return(("rebut", None)) style "bb_btn" text_style "bb_btn_text" xfill True:
            sensitive (d.selected is not None)
        textbutton "下一句" action Return(("next", None)) style "bb_btn" text_style "bb_btn_text" xfill True
        textbutton "结束本轮" action Return(("end", None)) style "bb_btn" text_style "bb_btn_text" xfill True

    if d.message:
        # 批注是这一句的判词，摆在发言页原位：读完点一下，句子还在。
        frame:
            xsize 1080
            xalign 0.05
            yalign 0.95
            yanchor 1.0
            padding BB_PAD_PAGE
            background BB_SLIP
            has vbox
            spacing 10
            text "批　注" style "bb_micro" color bb_pencil
            text d.message style "bb_body_sub" xsize 1000


screen bb_seat(d, name, stt, p):
    # 底边钉在席位点上，整块往上长。居中锚的话，一旦挂上静默章，
    # 名牌会被顶得往上跳 29px——桌上的刻度就不再指着它那张牌了。
    vbox:
        pos p
        anchor (0.5, 1.0)
        spacing 6
        text bb_seat_no(name) xalign 0.5 size BB_T_LABEL color bb_ink font bb_sans
        if stt == "broken":
            add "images/ui/stamp_silence.png":
                xysize (64, 64)
                xalign 0.5
        elif stt == "countered":
            add "images/ui/stamp_rebut.png":
                xysize (64, 64)
                xalign 0.5
        elif stt == "active":
            text "发言" xalign 0.5 style "bb_micro" color bb_gold_dark

        button:
            style "bb_ev"
            xalign 0.5
            action Return(("seat", name))
            if stt == "countered":
                background Frame("images/ui/frame_chip_rebut.png", 14, 14)
            elif stt == "active":
                background Frame("images/ui/frame_chip_sel.png", 14, 14)
            has fixed
            xysize (128, 40)
            if stt == "broken":
                # 涂黑只盖名字，姓留住——停下来的是谁，必须读得出来。
                hbox:
                    xalign 0.5
                    yalign 0.5
                    text name[0] style "bb_seat_text"
                    add "images/ui/redaction.png":
                        xysize (max(28, 24 * (len(name) - 1)), 24)
                        yalign 0.5
            else:
                text name style ("bb_seat_active" if stt == "active" else
                                 ("bb_seat_countered" if stt == "countered" else "bb_seat_text")):
                    xalign 0.5
                    yalign 0.5


# ---------------- 拼字：名单上被擦掉的一格 ----------------
screen bb_hangman(hz, picked, msg):
    zorder 60
    if store.bb_auto:
        # 填满一次答案位，让"我没有看清"那条失败文案走一遍。
        # 失败之后剧本会把 picked 清空重来——所以要认 msg，不认就永远拼不完。
        $ bb_trace("[AUTO] hangman " + str(len(picked)))
        timer 0.05 action (Return(("giveup", None)) if (msg or len(picked) >= hz["need"])
                           else Return(("pick", hz["candidates"][len(picked)])))
    use bb_page_bg()
    use bb_head("名单", "第八个名字", "第十四章 · 书房")

    # 三块内容改成一条竖排：提示、答案位、候选格。
    # 各自 yalign 的写法在 1080 和实际渲染之间对不上，答案位的下沿被第一行
    # 候选格压住，写进去的"陈"字缺了半笔。堆起来就不会重叠。
    # 位置用 area 钉死：内容自适应高度的容器，yalign 的落点会往上跑，
    # 答案位正好骑到红头栏那道锈线（205）上。
    vbox:
        area (360, 250, 1200, 620)
        spacing 26
        text hz["prompt"] xalign 0.5 xsize 1200 text_align 0.5 style "bb_body_sub"
        hbox:
            xalign 0.5
            spacing 18
            for i in range(hz["need"]):
                frame:
                    xsize 150
                    ysize 150
                    padding (0, 0)
                    background BB_SLIP
                    if i < len(picked):
                        text picked[i] xalign 0.5 yalign 0.5 size BB_T_HERO color bb_ink font bb_serif_b
                    else:
                        text "？" xalign 0.5 yalign 0.5 size BB_T_TITLE color bb_pencil font bb_serif_b
        grid 4 3:
            xalign 0.5
            spacing 12
            for c in hz["candidates"]:
                # 候选格是一个字，格子有 150 宽：用 label 形式的话字会顶在左边，
                # 和上面居中的答案位对不上。改成显式的子件，自己居中。
                button:
                    action Return(("pick", c))
                    style "bb_slot"
                    xsize 150
                    ysize 104
                    text c xsize 130 text_align 0.5 xalign 0.5 yalign 0.5 style "bb_btn_text"

    if msg:
        frame:
            xsize 1240
            xalign 0.5
            yalign 0.90
            yanchor 1.0
            padding BB_PAD_SLIP
            background BB_SLIP
            text msg style "bb_note" xsize 1180
    textbutton "不拼了" xalign 0.5 yalign 0.955 yanchor 1.0 action Return(("giveup", None)) style "bb_btn" text_style "bb_btn_text"


# ---------------- 结算 ----------------
screen bb_result(silence, total, lines, head="第一轮 · 结算", sub="逼出来的停顿"):
    zorder 70
    if store.bb_auto:
        timer 0.05 action Return()
    use bb_page_bg()
    use bb_head(head, sub)

    text str(silence) + " ／ " + str(total) xalign 0.44 yalign 0.40 xanchor 1.0 style "bb_hero"
    text "处沉默" xalign 0.465 yalign 0.455 style "bb_label" color bb_rust
    add "images/ui/stamp_silence.png":
        xysize (200, 200)
        xalign 0.74
        yalign 0.30
        rotate 8
    add "images/ui/rule_rust.png":
        xsize 1100
        xalign 0.5
        # 结算线要留在计数字和正文之间。贴着 0.535 放，正好压在第一行正文的
        # 起笔上，读成一道删除线；0.485 又去顶"处沉默"的下沿。取中间这一档，
        # 上下各留一行小字的净空。
        yalign 0.50

    vbox:
        xsize 1100
        xalign 0.5
        xanchor 0.5
        yalign 0.60
        spacing 16
        for ln in lines:
            text ln style "bb_body_sub" xsize 1100
    textbutton "继续" xalign 0.5 yalign 0.90 action Return() style "bb_btn" text_style "bb_btn_text"


# ---------------- 证据图鉴 ----------------
screen bb_gallery():
    tag menu
    use game_menu("证据", scroll="viewport"):
        text "手稿里出现过的东西，一件一件夹在这里。" style "bb_micro"
        if not have:
            text "还没有任何东西。" style "bb_body_sub"
        for e in ev_list():
            frame:
                xfill True
                padding BB_PAD_SLIP
                background BB_SLIP
                has hbox
                spacing 20
                add "images/ui/clip.png":
                    xysize (22, 62)
                    yalign 0.5
                add "images/ui/ic_" + EV_ICON.get(e.id, "page") + ".png":
                    xysize (52, 52)
                    yalign 0.5
                vbox:
                    spacing 6
                    text e.name style "bb_body_sub" color bb_gold_dark
                    text e.brief style "bb_body_sub" xsize 820
                    text "—— 手稿 · " + e.chapter style "bb_micro" color bb_pencil
