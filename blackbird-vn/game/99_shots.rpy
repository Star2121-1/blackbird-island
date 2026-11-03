# 临时：截图自检。跑完就删。
# 触发：RENPY_SKIP_MAIN_MENU=1 BB_SHOT=1，start 会跳到这里。
# 全程只用 show/hide + pause，不产生需要点击的交互。
# 抓出来的图拼在 shots/contact.png，用 tools/make_contact.py 生成。

# 确认框在真玩法里由 confirm 内联，那一层自带 modal＋压暗；截图为了绕开 modal
# 与 pause 互锁，只截 bb_confirm_panel，于是背景是亮的——审图的人据此报过一轮
# "弹窗没压暗，底下的 1／2 和正文撞在一起"。补一层假的压暗，让这张图说实话。
screen bb_shot_dim():
    zorder 150
    add "#0b0d1099"


label shot_all:
    # 键位诚实闸门的料：把引擎真正生效的那几张表抄出来，给 tools/test_content.py 对。
    # 闸门跑在纯 python 里，读不到运行中的 config.keymap——没有这份档，
    # "g 已经废掉"这句话就只能靠人记住。
    python:
        import json as _json
        import os as _os
        _want = ["choose_renderer", "hide_windows", "dismiss", "dismiss_unfocused", "game_menu",
                 "toggle_skip",
                 "skip", "fast_skip", "rollback", "rollforward", "help", "screenshot",
                 "self_voicing", "focus_left", "focus_right", "button_select"]
        _dump = dict((k, sorted(config.keymap.get(k, []))) for k in _want)
        with open(_os.path.join(config.basedir, "shots", "_keymap.json"), "w", encoding="utf-8") as _f:
            _json.dump(_dump, _f, ensure_ascii=False, sort_keys=True, indent=1)

    # 配音管线的料：五轮发言表摊平出来，一句一条。
    # tools/build_voice.py 按这份档整桌合成，闸门拿同一份档对账。
    # 在这里抄，是因为发言表写在 init python 里，纯 python 的脚本读不到成品对象。
    python:
        import json as _json2
        _lines = []
        for _rn, _round in enumerate([ROUND1, ROUND2, ROUND3, ROUND4, ROUND5], start=1):
            for _i, _s in enumerate(_round):
                _lines.append({"id": "r%d_%d" % (_rn, _i), "round": _rn, "i": _i,
                               "speaker": _s.speaker, "text": _s.text,
                               "weak_to": _s.weak_to, "hit_kind": _s.hit_kind})
        with open(_os.path.join(config.basedir, "shots", "_statements.json"), "w", encoding="utf-8") as _f:
            _json2.dump(_lines, _f, ensure_ascii=False, indent=1)

    # 人声这一路要真起播，不能只看文件在不在：
    # 喂两句原文给 bb_voice_line，再问引擎 voice 声道上挂着什么。
    # mixer 没注册、映射键和台词差一个字、mp3 路径写错——这里都是 None。
    python:
        import json as _json3
        _vprobe = []
        for _t in (ROUND1[0].text, ROUND5[len(ROUND5) - 1].text):
            BB_VOICE_NOW["file"] = None
            bb_voice_line(_t)
            _vprobe.append({"text": _t[:18], "want": BB_VOICE.get(_t),
                            "playing": renpy.music.get_playing(channel="voice")})
        # 对质循环真正调用的是 Debate.hear_current，不是这个函数——
        # 接线断了上面两行照样全过。用一只临时 Debate 走一遍那条路，
        # 只塞台词、不带 grants/hears，免得把证据总账搅脏。
        _d = Debate(SEATS, [Statement("王剑", ROUND1[0].text)])
        BB_VOICE_NOW["file"] = None
        _d.hear_current()
        _vprobe.append({"hear_current": renpy.music.get_playing(channel="voice"),
                        "want": BB_VOICE.get(ROUND1[0].text)})
        bb_voice_stop()
        _vprobe.append({"stop": renpy.music.get_playing(channel="voice")})
        with open(_os.path.join(config.basedir, "shots", "_voice.json"), "w", encoding="utf-8") as _f:
            _json3.dump(_vprobe, _f, ensure_ascii=False, indent=1)

    show screen main_menu
    pause 2.4
    $ _shot("01_menu")
    hide screen main_menu

    scene bg_dock
    show spr_shen at bb_talk_r
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
    show screen bb_result(4, 6, ["他说的每一句都对得上他自己那一趟。这一句没有对得上任何东西。\n\n机会用尽了，这一轮收在这里。还有三句没有听过。",
                                 "四处沉默。还有两句话，说完了。", "主人没有沉默。他把问题推回我手上——那一条不算赢。"],
                          head="第三夜 · 结算", sub="逼出来的停顿")
    pause 2.4
    $ _shot("18_result_cum")
    hide screen bb_result

    # ② 收轮前的确认框：bb_debate 那个按钮现在走 Confirm。
    #    截的是 bb_confirm_panel（modal 的 confirm 会把 pause 卡住），底下垫真的桌子。
    show screen bb_debate(round1)
    pause 0.4
    show screen bb_shot_dim
    show screen bb_confirm_panel("还有三句没有听过，听过才会有新东西到手。沉默按现在的数目记账。",
                                 Return(), Return())
    pause 2.4
    $ _shot("19_confirm")
    hide screen bb_confirm_panel
    hide screen bb_shot_dim
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

    # ④ 机会用完、话没说完：这一格要说"只能听"，还要看得见"反　驳"按不动。
    #    旧规则里三次用尽当场收轮，界面从来没有机会画这个状态——改了规则就得补一张，
    #    不然"用尽之后还在读正文"只是注释里的一句话。
    $ round1.bullets = 0
    $ round1.silence = 1
    $ round1.message = ""
    $ round1.selected = "invite"
    show screen bb_debate(round1)
    pause 2.4
    $ _shot("21_debate_spent")
    hide screen bb_debate

    # ⑤ 终章那张桌，两格：正文连着写过的那一对（中间有一行），和没写过的那一对（中间空着）。
    #    空着那一格必须留图——它是这一屏最容易被读成"我摆错了"的状态；
    #    没有这张图，"那一屏不评分"就只是 test_content 里的一句话。
    show screen bb_pair(["seal_rec", "face_photo"], pair_line("seal_rec", "face_photo"))
    pause 2.4
    $ _shot("22_pair")
    hide screen bb_pair

    show screen bb_pair(["invite", "lock"], pair_line("invite", "lock"))
    pause 2.4
    $ _shot("22b_pair_blank")
    hide screen bb_pair

    # 每张背景单独钉一张。BB_IMG 缺图不报错，只是悄悄换成纯色占位，
    # 光查盘上有没有 jpg 还不够——得看引擎真把那一层画上了屏。
    # 名单向引擎要：新增一张背景不用改这里。
    python:
        for _b in sorted(_n for _n in renpy.list_images() if _n.startswith("bg_")):
            renpy.scene()
            renpy.show(_b)
            renpy.pause(0.4, hard=True)
            _shot("30_" + _b)
        renpy.scene()

    $ renpy.end_replay()
    $ renpy.quit()
    return


# ---------------- 键盘闸门 ----------------
# 玩家报"按空格不能到下一句，点击才行"。键位表是好的（shots/_keymap.json 里 K_SPACE
# 就挂在 dismiss 那一格），坏的是"投进去没人接"那一半：引擎那句对白自己的 SayBehavior
# 走 `if check_focus and not self.is_focused(): continue`，而键盘焦点只在交互开始时
# 默认落在它身上——**点过一下之后**，焦点归对白页那张全屏"点任意处"按钮，空格就没人接了。
# 焦点是个运行时状态，静态读代码看不出来，所以这八趟都往真窗口的事件队列里投真事件：
#   ① space_cold：没点过，直接投 KSPACE → 该翻页
#   ② click：投真鼠标按下抬起 → 该翻页（"点任意处"不能因为修空格被牺牲）
#   ③ click_arm：再点一下，作用是把键盘焦点交到那张全屏按钮手上（玩家的真实动作序列）
#   ④ space_warm：就在③之后按空格 → 该翻页。这一趟才是玩家报的那件事。
#   ⑤ space_slow：按本作默认的 32 字/秒打字，打到一半投第一下空格——这一下只许"打完"，
#      第二下才翻页。补了 dismiss_unfocused 之后最容易顶掉的就是这条。
#   ⑥ card_space：扉页那一屏（没有 SayBehavior，dismiss_unfocused 管不到）投空格 →
#      该收掉。玩家报的是"空格不能到下一句"，而"下一句"在这本作里出现 25 次扉页、
#      若干次结算——只在对白上修好，等于修了一半。
#   ⑦ result_space：结算页同样投一次。它和扉页的差别是焦点默认落在"继续"那颗按钮上，
#      全屏按钮只是垫底——两种现场都得各自量一遍。
#   ⑧ spot_reclick：热点翻过一遍之后那颗装订孔还接不接点击（玩家报的第二件）。
#      同一个坐标投两次，两次都该把 ("spot", id) 交回来，而 found 只记一条。
# 投的是真按键（KSPACE）而不是 queue_event("dismiss")：前者把键位表翻译那一半也一起验了。
# 五句都用真角色走 script，不用 show screen say——后者不经过 Character，
# SayBehavior 根本不在树上，测出来永远是"过"。
# 翻页必须发生在注入之后：没投之前自己走了（自动前进／语音），闸门就是在给自己发证书。
# 计数走 config.periodic_callbacks（不是 periodic_callback：那一个只在建窗时被抄进表里，
# 运行时再赋值等于没挂），一拍约 50 毫秒，所以下面的数目是"拍"不是"帧"。
label keytest:
    python:
        import json as _kt_json
        import os as _kt_os
        import pygame as _kt_pg
        import renpy.test.testmouse as _kt_tm
        _kt = {"ticks": 0, "phase": None, "out": {}}
        _kt_plan = {
            "space_cold": [(60, "space")],
            "click": [(60, "click")],
            "click_arm": [(60, "click")],
            "space_warm": [(60, "space")],
            "space_slow": [(6, "space"), (60, "space")],
            "card_space": [(60, "space")],
            "result_space": [(60, "space")],
            "spot_reclick": [(60, "spot"), (120, "spot")],
        }
        # 这几项存在 persistent 里，跑完不还原就等于把玩家的下一次开档改成"无声＋无过渡"。
        _kt_pref = [preferences.afm_enable, preferences.auto_forward, preferences.text_cps,
                    preferences.transitions, preferences.self_voicing]
        preferences.afm_enable = False      # 自动前进会让"注入之后才翻页"这条白过
        preferences.auto_forward = False
        preferences.text_cps = 0            # 只有 space_slow 那一趟要打字，别的全走快路
        preferences.transitions = False
        preferences.self_voicing = False

        def _kt_space():
            _kt_pg.event.post(_kt_pg.event.Event(_kt_pg.KEYDOWN, unicode=u" ", key=_kt_pg.K_SPACE,
                                                 scancode=0, mod=0, repeat=False))
            _kt_pg.event.post(_kt_pg.event.Event(_kt_pg.KEYUP, key=_kt_pg.K_SPACE,
                                                 scancode=0, mod=0, repeat=False))

        def _kt_click():
            _kt_pg.event.post(_kt_pg.event.Event(_kt_pg.MOUSEBUTTONDOWN, button=1, pos=(30, 30)))
            _kt_pg.event.post(_kt_pg.event.Event(_kt_pg.MOUSEBUTTONUP, button=1, pos=(30, 30)))

        def _kt_spot():
            # 点在真热点的格子上。用的不是自己算出来的像素，而是引擎自带的虚拟鼠标
            # （renpy.test.testmouse）：`draw.mouse_event` 之后紧跟的一句
            # `testmouse.get_mouse_pos(x, y)` 会把位置整个覆盖掉，而它收的就是游戏
            # 坐标——窗口大小／DPI／信箱化这三层换算一概不用自己做。
            # 两条试过的死路：① 拿 `get_physical_size()` 换算——它对这一档窗口缩放
            # 是错的，点到的位置离那颗坑差了小半个屏幕，两下全空；② 投一条合成
            # MOUSEMOTION 再用 `renpy.get_mouse_pos()` 反量——那只读真实指针，
            # 合成的 MOTION 它不看，量回来永远 (0,0)。（点击事件本身吃的还是 ev.pos，
            # 所以别处那几下 (30,30) 照常有效。）
            _gx = int(round(_kt["spot_xy"][0] * config.screen_width))
            _gy = int(round(_kt["spot_xy"][1] * config.screen_height))
            _rec = _kt["out"][_kt["phase"]]
            _rec["game"] = [_gx, _gy]
            _kt_tm.click_mouse(1, _gx, _gy)

        def _kt_dump():
            d = _kt_os.path.join(config.basedir, "shots")
            if not _kt_os.path.isdir(d):
                _kt_os.makedirs(d)
            with open(_kt_os.path.join(d, "_keytest.json"), "w", encoding="utf-8") as f:
                _kt_json.dump(_kt["out"], f, ensure_ascii=False, indent=1, sort_keys=True)
            for k in sorted(_kt["out"]):
                v = _kt["out"][k]
                _x = ""
                if "returns" in v:
                    _x = " returns=%s found=%s game=%s" % (
                        v["returns"], v["found"], v.get("game"))
                print("[KEY] %s focus=%s at=%s stage=%s shots=%s%s" % (
                    k, v["focus"], v["at"], v.get("stage") or "-", v["shots"], _x))

        def _kt_cb():
            _kt["ticks"] += 1
            f = _kt["ticks"]
            p = _kt["phase"]
            if p is None:
                return
            rec = _kt["out"][p]
            if f in (2, 6, 20):        # 焦点是渲染完才落定的，多量几次取最后一个非空
                _d = renpy.display.focus.get_focused()
                if _d is not None:
                    rec["focus"] = type(_d).__name__
                # 台上站的是谁：这一拍 say 语句已经跑过，角色那句 bb_stage 也该跑过了。
                rec["stage"] = rec.get("stage") or bb_stage_probe()
            for (_t, _what) in _kt_plan[p]:
                if f == _t:
                    rec["shots"].append(f)
                    if _what == "space":
                        _kt_space()
                    elif _what == "spot":
                        _kt_spot()
                    else:
                        _kt_click()
            if f == 260:
                # 注入没接住就一直卡在这一句。到此收档：把"没翻页"这件事写盘，然后退。
                # 逃逸走 renpy.quit() 而不是再投一个键——焦点在谁手上正是要测的未知量。
                rec["at"] = None
                _kt_dump()
                preferences.afm_enable, preferences.auto_forward, preferences.text_cps, \
                    preferences.transitions, preferences.self_voicing = _kt_pref
                renpy.quit()

        config.periodic_callbacks.append(_kt_cb)

    python:
        def _kt_phase(name):
            _kt["out"][name] = {"focus": None, "at": None, "shots": [], "stage": ""}
            _kt["phase"] = name
            _kt["ticks"] = 0
        _kt_phase("space_cold")
    N "没点过之前，空格该把这一句推走。"
    $ _kt["out"]["space_cold"]["at"] = _kt["ticks"]

    $ _kt_phase("click")
    SHEN "这一句该被投进来的那一下点击推走。"
    $ _kt["out"]["click"]["at"] = _kt["ticks"]

    $ _kt_phase("click_arm")
    N "点这一下，是为了下一句能按空格。"
    $ _kt["out"]["click_arm"]["at"] = _kt["ticks"]

    $ _kt_phase("space_warm")
    ME "点过一下之后，这一句还得能被空格推走。"
    $ _kt["out"]["space_warm"]["at"] = _kt["ticks"]

    python:
        _kt_phase("space_slow")
        # 本作默认就是这个速度（00_settings 里 preferences.text_cps = 32）。
        # 第 6 拍约 0.3 秒、才打出九个字，所以这一拍投下去时空着半句没打完。
        preferences.text_cps = 32
    N "打到一半时按下的第一下空格，只该把剩下的字摆齐，不该把这一句翻过去。"
    $ _kt["out"]["space_slow"]["at"] = _kt["ticks"]

    $ preferences.text_cps = 0
    $ _kt_phase("card_space")
    # 同一件事还有两处落点：扉页和结算页垫的也是"点任意处"全屏按钮，可那一屏
    # 根本没有 SayBehavior，dismiss_unfocused 管不到——空格得由这两屏自己接。
    # 两屏分开投：结算页另外挂着一颗 default True 的"继续"，焦点在它手上，
    # 和扉页不是同一种现场（"写法一样"是猜测，不是实测）。
    call screen bb_card("第一章", "空格闸门", "这一屏没有那句对白，空格也得把页面收掉。", "")
    $ _kt["out"]["card_space"]["at"] = _kt["ticks"]

    $ _kt_phase("result_space")
    call screen bb_result(3, 8, ["空格也得把这一页收掉。"])
    $ _kt["out"]["result_space"]["at"] = _kt["ticks"]

    # 玩家报的第二件：热点看完就点不动了。这一趟不看键位，看那颗"翻过的装订孔"
    # 到底还接不接点击——第 60 拍点一次（还没看过，亮着的 92 坑），第 120 拍点
    # 同一个坐标（已经翻过，换成 46 的孔）。两次都该把 ("spot", id) 交回来，
    # 而 found 只该记一条：那一格直接数 len(found)，重复一条就报成 5／4。
    python:
        _kt_phase("spot_reclick")
        _kt["spot_xy"] = (0.18, 0.58)          # 就是 DOCK_SPOTS 第一坑的真坐标
        _kt["out"]["spot_reclick"]["returns"] = []
        _kt["out"]["spot_reclick"]["found"] = 0
    $ _kt_spots = [dict(id="invite", x=0.18, y=0.58)]
    $ _kt_found = []
    $ _kt_i = 0
    while _kt_i < 2:
        call screen bb_explore("bg_dock", _kt_spots, _kt_found, "重看闸门")
        $ _kt_r = _return
        $ _kt["out"]["spot_reclick"]["returns"].append(list(_kt_r))
        if _kt_r[0] == "spot" and _kt_r[1] not in _kt_found:
            $ _kt_found.append(_kt_r[1])
        $ _kt_i = _kt_i + 1
    $ _kt["out"]["spot_reclick"]["found"] = len(_kt_found)
    $ _kt["out"]["spot_reclick"]["at"] = _kt["ticks"]

    $ _kt["phase"] = None
    $ config.periodic_callbacks.remove(_kt_cb)
    $ _kt_dump()
    python:
        preferences.afm_enable, preferences.auto_forward, preferences.text_cps, \
            preferences.transitions, preferences.self_voicing = _kt_pref
        renpy.quit()
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
