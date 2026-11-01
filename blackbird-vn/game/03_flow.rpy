# ============================================================
# 流程层：垂直切片
#   2025 杭州（顾言笙） → 第一章 抵达 → 第三章 书房 → 第六章 大厅第一轮 → 结算
# 台词取自《黑鸟岛-终稿》，措辞不改，只删不增。
# ============================================================

# ---------------- 主菜单入口（Ren'Py 会找这个 label） ----------------
label main_menu_screen:
    call screen bb_main_menu
    return


label start:
    $ have.clear()
    $ round1 = Debate(SEATS, ROUND1)
    if os.environ.get("BB_SHOT"):
        jump shot_all
    jump story


# ---------------- 序：2025 · 杭州 ----------------
label story:
    scene bg_hangzhou
    N "二〇二五年，十一月。市档案馆的阅览室。"
    show spr_gu as talker at bb_talk_r
    GU "我两年前在旧货市场淘到这本手稿。它记录的岛事，在二〇一九年的深秋。"
    GU "手稿的每一页，我都编了号。笔记里引用手稿原文的地方，我都标了页码。"
    GU "今天我要读的那几页，是第一日。"
    N "《黑岛证词》。作者自称陈默。"
    GU "读之前，我把规矩说清楚——"
    GU "这本书不许你指认谁。你要做的，是看能不能让说话的人停下来。"
    call screen bb_card("序章", "翻开", "二〇二五年 · 杭州 · 顾言笙的调查笔记")
    jump ch1


# ---------------- 第一章：抵达 ----------------
label ch1:
    call screen bb_card("第一章", "抵达", "我到达黑鸟岛的那天，天是灰的。")
    scene bg_dock
    N "渡轮从舟山港出发，在海上颠簸了将近四个小时。甲板上只有我一个人——不，还有船老大。"
    N "他抽着烟，烟头在风中明灭，偶尔看我一眼，又迅速移开目光。"
    "船老大" "到了。"
    N "我没问为什么我会在这趟船上。信封是在三天前出现的，放在我公寓门缝下面。"
    N "没有落款，没有解释，只有一行手写的小字："
    N "如果您想知道当年真相的碎片，请于十一月十七日上午九点整，乘渡轮抵达黑鸟岛。那天上午只有这一班船。"
    ME "当年真相。"
    N "这个词像一根细小的钩子，拽住了我的某种记忆。不是具体的画面，而是一种模糊的、几乎被时间磨平的痛感。"
    ME "我是陈默。自由撰稿人。三十一岁，单身，独居杭州。"
    N "渡轮靠岸时，我看见一座白色的建筑物矗立在礁石之上。此刻它灯火通明，像黑暗中一只睁开的眼睛。"
    N "庄园门口站着一个人。"
    show spr_shen as talker at bb_talk_r
    SHEN "你就是陈默？"
    ME "是。"
    SHEN "我是沈南舟，这栋庄园的主人。欢迎你来。"
    N "他伸出手，我握住。"
    call bb_search("bg_dock", "码头 · 下船之前", DOCK_SPOTS)
    ME "其他人呢？"
    SHEN "都在里面。请进。我简要介绍一下——今晚到场的，一共八个人。你们七个，加上我。"
    SHEN "我们都是老朋友，虽然……有些已经很多年没见了。"
    ME "老朋友。"
    N "我和沈南舟从未见过面，我也不认识这庄园里其他任何人。但这念头只是闪过，就被某种更深的东西压了下去。"
    jump ch1_hall


label ch1_hall:
    call screen bb_card("第一章", "大厅", "大厅里已经有五个人了。")
    scene bg_hall_long
    N "靠窗的位置坐着一个男人，穿黑色风衣，正在看手机。他抬头看了我一眼，眼神锐利得像刀。"
    show spr_zhao as talker at bb_talk_r
    ZHAO "赵寒。"
    N "然后他低下头继续看手机。"
    show spr_su as talker at bb_talk_r
    SU "苏蔓，记者。"
    N "壁炉旁边站着一个年轻女人，手里拿着一个笔记本，正在快速记录着什么。她抬头，对我微微一笑。"
    show spr_zhou as talker at bb_talk_r
    ZHOU "周亦安，犯罪心理学。方廷。"
    N "沙发上有两个人正在低声交谈。白色衬衫的中年男人点点头，算是打招呼。"
    show spr_lin as talker at bb_talk_r
    LIN "林晚，法医。"
    LIN "你好。"
    N "她的声音平淡，像在读一份尸检报告。目光在我身上停留了一秒。"
    ME "大厅里五个人，加上我和沈南舟，七个。"
    call bb_search("bg_hall_long", "大厅 · 落座之前", HALL_SPOTS)
    ME "还有一个人没到？"
    SHEN "王剑在花园里。他说要感受一下岛屿的氛围。"
    N "王剑。这个名字让我心头一跳。这两个字出现在了我梦里——一辆车，雨夜，一声沉闷的撞击。"
    N "潮汐变化很快，傍晚六点以后渡轮就不再返回了。"
    ME "意思是：我们被困在这里了。"
    N "我去了一楼唯一的空房间放下行李，回到大厅时，王剑也回来了。"
    show spr_wang as talker at bb_talk_r
    WANG "都到齐了。沈先生，你把我们叫到这里，到底有什么事？"
    show spr_shen as talker at bb_talk_r
    SHEN "各位都是聪明人，我相信你们收到了我的邀请函。我也相信你们和我一样，对十年前的临东海事件有所耳闻。"
    N "这五个字像一道闪电，劈开了我记忆深处某种淤塞的东西。"
    ZHOU "陈默？"
    ME "我没事。继续。"
    SHEN "十年前，我的儿子死于一起交通事故。肇事者逃逸，案件至今未破。"
    SHEN "而你们七个人，每一个，都与那起案件有着千丝万缕的联系。我不知道你们是否记得那些联系，但我想……你们会想起来的。"
    SHEN "晚餐后，我们来玩一个游戏。"
    jump ch3


# ---------------- 探索（取证） ----------------
label bb_search(bg, place, spots):
    $ found = []
    $ leaving = False
    scene expression bg
    while not leaving:
        $ hint = place + " —— 还有 " + str(len(spots) - len(found)) + " 处没有看过。看完才能走。" if len(found) < len(spots) else place + " —— 看完了。可以走了。"
        call screen bb_explore(bg, spots, found, hint)
        if _return[0] == "leave":
            $ leaving = True
        else:
            $ found.append(_return[1])
            call expression "spot_" + _return[1]
    scene expression bg
    return


# ---------------- 热点内容 ----------------
label spot_invite:
    N "我把请柬又从口袋里摸出来。烫金的边，字是打印的，只有一行手写的小字。"
    N "没有落款，没有解释。三天前出现在公寓门缝下面。"
    $ ev_give("invite")
    return

label spot_hand:
    N "我低头看自己的右手。"
    N "他握手的时候，有一根指头抵着我的掌心，弯的。我没有多想。"
    N "现在我想了一下。那只手的凉，像是刚从水里捞出来。"
    $ ev_give("hand")
    return

label spot_lock:
    N "大厅的门锁是新的。锁体上还有出厂的油。钥匙只有一把，在沈南舟那里。"
    N "傍晚六点以后渡轮不再返回。东翼封着。小艇是旧的，没有人乘它出过岛。"
    $ ev_give("lock")
    return

label spot_note:
    N "书桌角上一张纸。折了两折，压在一叠档案下面，像是随手放上去的。"
    SU "我再确认一遍——这不是沈南舟的字迹。"
    $ ev_give("note")
    return

label spot_roster:
    N "最上面是一份打印的文件。标题写着：临东海案相关人员档案。"
    N "名单上有八个名字。王剑、赵寒、方廷、周亦安、林晚、苏蔓——还有陈默。"
    N "最后一个名字，我没看清。"
    N "名单下方有一行手写的小字，笔迹工整，与那张纸条完全不同："
    N "以上八人，皆为当日在场者。真相不在其中任何一人身上。"
    $ ev_give("roster")
    return

label spot_diary:
    N "我抽出最近的一本。封面上写着一个日期：2009年11月18日。"
    N "第一日。他们来了。"
    N "方廷——当年那份赔偿协议，是他签的字。"
    N "周亦安——他对人性黑暗的兴趣，也许不止是学术。"
    N "林晚——她对真相的追求是纯粹的，但这正是她的弱点。"
    SU "……你在看什么？"
    N "我把那一页翻过去。末尾只有四个字，用的是现在时："
    N "陈默——他在说谎。"
    $ ev_give("diary_fang")
    $ ev_give("diary_me")
    return


# ---------------- 第三章：书房 ----------------
label ch3:
    call screen bb_card("第三章", "书房", "名单上有八个名字。我辨认了其中七个。")
    scene bg_hall_long
    N "我在庄园里走了大约二十分钟。我把客人数了一遍。受邀的七位，来了七位。没有人缺席。"
    N "我把这个数先放一放。暂时，我没有对这一个数发问。"
    scene bg_study
    show spr_su as talker at bb_talk_r
    SU "你刚才去哪了？"
    ME "找沈南舟。有人留了张纸条。"
    SU "这不是沈南舟的字迹。"
    ME "你怎么知道？"
    SU "他的字很工整，带一点书法的底子。这行字……这是匆忙中写的。像是在极短时间内，来不及控制笔迹的情况下写的。"
    SU "我想问的是，你捡到这个之前，有没有看到任何人进出书房？"
    ME "没有。但我听到走廊里有脚步声。很规律，像是有节奏的走路。不像是慌乱中踩出来的。"
    SU "要不要进去看看？"
    ME "沈南舟说过，书房是他私人使用的区域。但……"
    SU "但他也说过，任何人都可以参观。规矩是给人遵守的。也是给人打破的。"
    N "门没有锁。"
    call bb_search("bg_study", "书房 · 苏蔓在场", STUDY_SPOTS)
    jump hangman_8


# ---------------- 反谜题：第八个名字 ----------------
label hangman_8:
    call screen bb_card("名单", "第八个名字", "最后一个名字，我没看清。")
    $ picked = []
    $ msg = ""
    $ giving_up = False
    while not giving_up:
        call screen bb_hangman(HANGMAN, picked, msg)
        if _return[0] == "giveup":
            $ giving_up = True
        else:
            $ picked.append(_return[1])
            if len(picked) >= HANGMAN["need"]:
                $ msg = HANGMAN["fail"]
                $ picked = []
    $ ev_give("erased8_note")
    N "名单上的八个名字。岛上七个。"
    N "第八个，我没有看清。这一句我写得很慢——今天的第一遍，它就是这个样子。"
    jump ch6


# ---------------- 第六章：大厅 · 第一轮 ----------------
label ch6:
    call screen bb_card("第六章", "大厅", "每人只有一次机会——说完就要等下一个人。")
    scene bg_hall_ring
    N "九点的钟声敲响时，大厅里已经坐满了人。长桌被撤走，换成了环形沙发。八个人围坐，中间留着一张矮木几，几面空着。"
    show spr_shen as talker at bb_talk_r
    SHEN "各位，感谢配合。我知道你们各自都有事要做，但今晚只有一个目的——让每个人都亲口说出，二〇〇九年十一月十七日那晚，你做了什么。"
    SHEN "顺序随便。谁先说，谁后说。但每人只有一次机会——说完就要等下一个人。中途不能反悔。"
    N "我注意到：沈南舟的无名指微微弯曲。旧骨折。"
    N "沈南舟看向我的位置。"
    SHEN "陈默先生。你的回合。"
    ME "二〇〇九年十一月十七日晚，我在家。我写稿，等凌晨的球赛。"
    SU "你记得吗？"
    ME "我记不清了。"
    SU "你确定？"
    ME "我不确定。"
    N "所有人说完之后，游戏才开始。规则是：举起一条证据，抵在一句话上。"
    call bb_debate_run(round1)
    call bb_result_card(round1)
    jump epilogue


# ---------------- 沉默计数 ----------------
label bb_debate_run(rt):
    while not rt.done:
        $ rt.hear_current()
        call screen bb_debate(rt)
        $ act = _return[0]
        $ arg = _return[1]
        if act == "select":
            $ rt.select(arg)
        elif act == "rebut":
            $ rt.rebut()
        elif act == "next":
            $ rt.advance()
        elif act == "seat":
            $ rt.jump_to(arg)
        elif act == "end":
            $ rt.end()
    return


label bb_result_card(rt):
    call screen bb_result(rt.silence, rt.silence_total, rt.result_lines())
    return


# ---------------- 尾：合上手稿 ----------------
label epilogue:
    scene bg_hangzhou
    show spr_gu as talker at bb_talk_r
    GU "第一日读到这里。"
    GU "我没有拿到名字。我拿到的是几段停顿——谁在什么地方停下来，停多久。"
    GU "手稿里写着：真相不在其中任何一人身上。"
    GU "我原以为这是一句故弄玄虚的话。现在我怀疑它是这本书的规矩。"
    call screen bb_card("切片结束", "筛子", "第八章以后，第八个名字仍然没有出现。")
    return
