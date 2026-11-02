# 临时：截图自检。跑完就删。
# 触发：RENPY_SKIP_MAIN_MENU=1 BB_SHOT=1，start 会跳到这里。
# 全程只用 show/hide + pause，不产生需要点击的交互。
# 抓出来的图拼在 shots/contact.png，用 tools/make_contact.py 生成。

label shot_all:
    show screen main_menu
    pause 2.4
    $ _shot("01_menu")
    hide screen main_menu

    scene bg_dock
    show spr_shen as talker at bb_talk_r
    show screen say("沈南舟", "我是沈南舟，这栋庄园的主人。欢迎你来。")
    pause 2.4
    $ _shot("02_say")
    hide screen say

    $ ev_give("invite")
    $ ev_give("hand")
    $ ev_give("lock")
    $ ev_give("note")
    $ ev_give("roster")
    $ ev_give("diary_fang")
    $ ev_give("diary_me")
    $ ev_give("time_window")

    show screen bb_card("第一章", "抵达", "我到达黑鸟岛的那天，天是灰的。", "十一月十七日", BB_SNAP("bg_dock.jpg"))
    pause 2.4
    $ _shot("03_card")
    hide screen bb_card

    # 水印的字数那一格：第一章只印一个"一"，看不出问题；第二十四章要印三个字，
    # 字号按字数除以后整块宽度必须还和单字那版一样，不然顶出右边界。
    show screen bb_card("第二十四章", "合上", "手稿到这里就没有了。", "十一月十五日", BB_SNAP("bg_dock.jpg"))
    pause 2.4
    $ _shot("03b_card_num")
    hide screen bb_card

    show screen bb_explore("bg_dock", DOCK_SPOTS, ["invite"],
                           "码头 · 下船之前 —— 还有 1 处没有看过。看完才能走。")
    pause 2.4
    $ _shot("04_explore")
    hide screen bb_explore

    $ round1.i = 1
    $ round1.hear_current()
    $ round1.select("time_window")
    $ round1.message = ""
    show screen bb_debate(round1)
    pause 2.4
    $ _shot("05_debate")
    $ round1.rebut()
    pause 2.4
    $ _shot("06_debate_hit")
    hide screen bb_debate

    show screen bb_hangman(HANGMAN, ["陈"], "")
    pause 2.4
    $ _shot("07_hangman")
    hide screen bb_hangman

    show screen bb_result(round1.silence, round1.silence_total, round1.result_lines())
    pause 2.4
    $ _shot("08_result")
    hide screen bb_result

    # 图鉴这张要拍成"集齐"的样子：截图脚本只走了第一夜，手里 8 条，
    # 而玩家真正会看到的页面是三十几条排下来第一屏只剩三张的样子。
    # 不灌满就永远不知道这一页要不要翻页提示、行高够不够。
    $ have.update(EVIDENCE.keys())
    show screen bb_gallery
    pause 2.4
    $ _shot("09_gallery")
    hide screen bb_gallery

    show screen navigation
    pause 2.4
    $ _shot("10_navigation")
    hide screen navigation

    show screen bb_card("过　夜", "十一月十八日", "雾比夜里更厚。东翼那扇门，是凌晨开的。", "十一月十八日", BB_SNAP("bg_hall_long.jpg"))
    pause 2.4
    $ _shot("15_daypass")
    hide screen bb_card

    # 回放页要有东西可看。headless 里没人点击，直接往 _history_list 里塞。
    $ _history_list[:] = [_FakeHist(w, t) for (w, t) in HIST_SEED]
    show screen history
    pause 2.4
    $ _shot("14_history")
    hide screen history

    show screen preferences
    pause 2.4
    $ _shot("11_preferences")
    hide screen preferences

    show screen help
    pause 2.4
    $ _shot("12_help")
    hide screen help

    show screen bb_legend
    pause 2.4
    $ _shot("16_legend")
    hide screen bb_legend

    show screen file_slots("存档")
    pause 2.4
    $ _shot("13_save")
    hide screen file_slots

    # 收卷那一屏是玩家看到的最后一页，单独截一张。
    # 分母从发言表里现算：动了破绽表而这一屏还写着旧数字，截图就是在演一场没发生的戏。
    $ _sil_all = sum(len([s for s in r if s.weak_to and s.hit_kind == "silence"])
                     for r in (ROUND1, ROUND2, ROUND3, ROUND4, ROUND5))
    $ _final = ["手里的证据 8 ／ %d 条。" % len(EVIDENCE),
                "逼出的沉默 %d ／ %d 处。" % (_sil_all, _sil_all),
                "第八个名字，我终究没有写下来。", "我没有指认谁。这本书不许我指认谁。"]
    show screen bb_result(_sil_all, _sil_all, _final, head="收卷", sub="合上的一页")
    pause 2.4
    $ _shot("17_final")
    hide screen bb_result

    # 往后的三张：都是这一轮补的交互，不在正文里点得到，只能摆出来看。
    # ① 带"六日总账"那一行的结算页（第一夜不显示它，17 也不显示）。
    $ bb_silence_won = 10
    $ bb_silence_possible = 20
    show screen bb_result(4, 6, ["他说的每一句都对得上他自己那一趟。这一句没有对得上任何东西。\n\n机会用尽了，这一轮收在这里。还有 3 句没有听过。",
                                 "四处沉默。还有两句话，说完了。", "主人没有沉默。他把问题推回我手上——那一条不算赢。"],
                          head="第三夜 · 结算", sub="逼出来的停顿")
    pause 2.4
    $ _shot("18_result_cum")
    hide screen bb_result

    # ② 收轮前的确认框：bb_debate 那个按钮现在走 Confirm。
    #    截的是 bb_confirm_panel（modal 的 confirm 会把 pause 卡住），底下垫真的桌子。
    show screen bb_debate(round1)
    pause 0.4
    show screen bb_confirm_panel("还有 3 句没有听过，听过才会有新东西到手。沉默按现在的数目记账。",
                                 Return(), Return())
    pause 2.4
    $ _shot("19_confirm")
    hide screen bb_confirm_panel
    hide screen bb_debate

    # ③ 全停下来那一局的动作栏：要看得见"都停下来了"。
    $ round1.silence = round1.silence_total
    $ round1.message = ""
    $ round1.selected = None
    # 抵过的证据要在图上看得见装订孔。真的那一格（死亡时间）排在 EVIDENCE 表尾，
    # 视口只装得下前七条——不点名摆两条靠前的，这个记号画没画谁也看不出来。
    $ round1.spent = {"invite", "lock"}
    show screen bb_debate(round1)
    pause 2.4
    $ _shot("20_debate_done")
    hide screen bb_debate

    $ renpy.end_replay()
    $ renpy.quit()
    return


init python:
    import os

    class _FakeHist(object):
        def __init__(self, who, what):
            self.who = who
            self.what = what

    HIST_SEED = [
        ("沈南舟", "各位都是聪明人，我相信你们收到了我的邀请函。"),
        ("沈南舟", "十年前，我的儿子死于一起交通事故。肇事者逃逸，案件至今未破。"),
        ("周亦安", "陈默？"),
        ("陈默", "我没事。继续。"),
        ("王剑", "我开车经过大桥。撞人的不是我。但我看见了。"),
        ("林晚", "官方记“当场死亡”。王剑的自首书，记“途中死亡”。都是事后的话。"),
        ("方廷", "我二〇〇九年代理的是死者家属一方，负责和肇事方谈赔偿协议。"),
        ("赵寒", "那晚我值班。经过大桥，站在桥上看了很久。没下车。"),
        ("陈默", "名单上有八个名字。岛上七个。第八个，我没有看清。"),
    ]

    def _shot(tag):
        d = os.environ.get("BB_SHOT_DIR", "shots")
        if not os.path.isabs(d):
            d = os.path.join(renpy.config.basedir, d)
        if not os.path.isdir(d):
            os.makedirs(d)
        ok = renpy.screenshot(os.path.join(d, tag + ".png"))
        renpy.notify("shot " + tag + " " + str(ok))

# 封面自己抓一张。上面那批图是从 start 之后跑的，那时 main_menu 已经是 False，
# 所以 01_menu 拍到的其实是暂停菜单——标题屏上"从第一日读起／接着上次读"那两条
# 从来没有进过任何一张图。BB_SHOT_TITLE=1 时不跳主菜单，等屏幕亮定再截。
init python:
    if os.environ.get("BB_SHOT_TITLE"):
        _bb_title_frames = [0]

        def _bb_shot_title():
            if not main_menu or not renpy.get_screen("main_menu"):
                return
            _bb_title_frames[0] += 1
            if _bb_title_frames[0] < 20:
                return
            d = os.environ.get("BB_SHOT_DIR", "shots")
            if not os.path.isabs(d):
                d = os.path.join(renpy.config.basedir, d)
            if not os.path.isdir(d):
                os.makedirs(d)
            renpy.screenshot(os.path.join(d, "00_title.png"))
            renpy.quit()

        config.periodic_callback = _bb_shot_title
