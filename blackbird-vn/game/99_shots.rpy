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
