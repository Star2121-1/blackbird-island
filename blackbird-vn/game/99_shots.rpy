# 临时：截图自检。跑完就删。
# 触发：RENPY_SKIP_MAIN_MENU=1 BB_SHOT=1，start 会跳到这里。
# 全程只用 show/hide + pause，不产生需要点击的交互。

label shot_all:
    show screen bb_main_menu
    pause 1.2
    $ _shot("01_menu")
    hide screen bb_main_menu

    scene bg_dock
    show spr_shen as talker at bb_talk_r
    show screen say("沈南舟", "我是沈南舟，这栋庄园的主人。欢迎你来。")
    pause 1.0
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

    show screen bb_card("第一章", "抵达", "我到达黑鸟岛的那天，天是灰的。")
    pause 1.0
    $ _shot("03_card")
    hide screen bb_card

    show screen bb_explore("bg_dock", DOCK_SPOTS, ["invite"],
                           "码头 · 下船之前 —— 还有 1 处没有看过。看完才能走。")
    pause 1.0
    $ _shot("04_explore")
    hide screen bb_explore

    $ round1.i = 1
    $ round1.hear_current()
    $ round1.select("time_window")
    $ round1.message = ""
    show screen bb_debate(round1)
    pause 1.0
    $ _shot("05_debate")
    $ round1.rebut()
    pause 0.8
    $ _shot("06_debate_hit")
    hide screen bb_debate

    show screen bb_hangman(HANGMAN, ["陈"], "")
    pause 1.0
    $ _shot("07_hangman")
    hide screen bb_hangman

    show screen bb_result(round1.silence, round1.silence_total, round1.result_lines())
    pause 1.0
    $ _shot("08_result")
    hide screen bb_result

    # bb_gallery / bb_settings 是 modal 屏幕，show screen + pause 会互锁，
    # 这里抓不到；这两个面板只能手工开一次看。
    $ renpy.end_replay()
    $ renpy.quit()
    return


init python:
    import os

    def _shot(tag):
        d = os.environ.get("BB_SHOT_DIR", "shots")
        if not os.path.isabs(d):
            d = os.path.join(renpy.config.basedir, d)
        if not os.path.isdir(d):
            os.makedirs(d)
        ok = renpy.screenshot(os.path.join(d, tag + ".png"))
        renpy.notify("shot " + tag + " " + str(ok))
