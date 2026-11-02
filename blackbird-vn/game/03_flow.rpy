# ============================================================
# 流程层：垂直切片
#   2025 杭州（顾言笙） → 第一章 抵达 → 第三章 书房 → 第六章 大厅第一轮 → 结算
# 台词取自《黑鸟岛-终稿》，措辞不改，只删不增。
# ============================================================

# ---------------- 主菜单入口（Ren'Py 会找这个 label） ----------------
label main_menu_screen:
    call screen main_menu
    return


# 冒烟测试开关：BB_AUTOPLAY=1 时，界面一律自己收掉，正文从头跑到尾。
# 为的是让第二十章里的一句错别字级运行时错误也能被抓出来，而不是只截第一屏。
default bb_auto = False
default BB_PREF_SAVED = []
default BB_AMB_AT_START = None

init python:
    def bb_trace(msg):
        # 进度行。Ren'Py 做图像预测时不看 if 的条件，两个分支都走一遍，
        # 所以这里挡掉预测——否则截图跑（bb_auto 是 False）也能打出 [AUTO]。
        if not renpy.predicting():
            print(msg)


label start:
    # 冒烟测试的几只环境变量只认开发脚本在场的时候：99_shots 不打进发行包，
    # 玩家机器上万一有 BB_SHOT／BB_LOAD，跳的 label 和读的档都不存在，一开局就抛错。
    $ bb_dev = renpy.has_label("shot_all")
    if bb_dev and os.environ.get("BB_LOAD"):
        # 存读回归的第二趟：读回上一趟在尾声存的那档，从这里就不再往下走了，
        # 上下文直接跳到存盘点之后（尾声），由那里打一行"读回"再收工。
        $ renpy.load("regress")
    $ have.clear()
    $ bb_auto = bb_dev and bool(os.environ.get("BB_AUTOPLAY"))
    if bb_auto:
        # 界面会自己收掉，台词也得自己翻页，不然第一句就停住等点击。
        # afm_enable 是"允许自动模式"总闸，只开 auto_forward 的话它不认。
        # 这几项存在 persistent 里，跑完不还原的话，下次正常开档就是"无过渡+自动前进"，
        # 而且取消环境变量也回不来——实测过，saves/persistent 里躺着 transitions=False。
        $ BB_PREF_SAVED = [preferences.afm_enable, preferences.auto_forward,
                           preferences.afm_time, preferences.text_cps,
                           preferences.transitions]
        $ preferences.afm_enable = True
        $ preferences.auto_forward = True
        $ preferences.afm_time = 0.01
        $ preferences.text_cps = 100000
        $ preferences.transitions = False
    $ bb_silence_won = 0
    $ bb_silence_possible = 0
    $ round1 = Debate(SEATS, ROUND1)
    # 抵对了不扣机会，`bullets` 数的是"允许判错几次"。
    # 第一夜两处可逼、容错三次，是教学局；往后每夜三处，多给一次容错。
    $ round2 = Debate(SEATS, ROUND2, bullets=4, label="八仙桌 · 第二轮", head="第二夜 · 结算")
    $ round3 = Debate(SEATS, ROUND3, bullets=4, label="大厅 · 第三轮", head="第三夜 · 结算")
    $ round4 = Debate(SEATS, ROUND4, bullets=4, label="大厅 · 第四轮", head="第四夜 · 结算")
    $ round5 = Debate(SEATS, ROUND5, bullets=4, label="东翼门外 · 第五轮", head="第五夜 · 结算")
    if bb_dev and os.environ.get("BB_SHOT"):
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
    # 尾章有一句"封皮上缺掉的“鸟”字"，玩家要在那儿认得它，得先在这儿看见过。
    N "封皮上写的是“黑岛证词”。比“黑鸟岛证词”，少一个字。我找过那个“鸟”字，没有找到。"
    N "它是什么时候没有的，我不知道。也许从来就没有写。"
    GU "读之前，我把规矩说清楚——"
    GU "这本书不许你指认谁。你要做的，是看能不能让说话的人停下来。"
    call screen bb_card("序章", "翻开", "二〇二五年 · 杭州 · 顾言笙的调查笔记", "二〇二五年十一月", BB_SNAP("bg_hangzhou.jpg"))
    jump ch1


# ---------------- 第一章：抵达 ----------------
label ch1:
    call screen bb_card("第一章", "抵达", "我到达黑鸟岛的那天，天是灰的。", "十一月十七日", BB_SNAP("bg_dock.jpg"))
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
    call screen bb_card("第一章", "大厅", "大厅里已经有五个人了。", "十一月十七日", BB_SNAP("bg_hall_long.jpg"))
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
    jump ch2


# ---------------- 探索（取证） ----------------
label bb_search(bg, place, spots):
    $ found = []
    $ leaving = False
    scene expression bg
    if bb_auto:
        # 自动播放要把每一处热点都点掉。以前这里只打一行日志就走 "离开此处"，
        # 于是全六日跑完手里只有正文给的证据——"三十三条收得齐"这件事
        # 只被 test_content 静态查过，从来没被真跑过一遍。
        $ bb_trace("[AUTO] explore " + place + " · 取证 " + str(len(spots)) + " 处")
        $ auto_left = [s["id"] for s in spots]
        while auto_left:
            $ call_id = auto_left.pop(0)
            call expression "spot_" + call_id
        return
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
    # 尾章的"停"里点过"那册倒填年份的日记"。这一格热点只给了封面日期和现在时，
    # 判定那一步没露过面，玩家到尾声才知道有一册日记的年份是填回去的。
    N "纸是旧的，墨是新的。我把那一页对着光看——那四个字的墨色，没有褪过。"
    N "这页笔记不是二〇〇九年写的。是这一次聚会之前，有人照着今天的样子，把年份倒填了回去。"
    $ ev_give("diary_fang")
    $ ev_give("diary_me")
    return


# ---------------- 第三章：书房 ----------------
label ch3:
    call screen bb_card("第三章", "书房", "名单上有八个名字。我辨认了其中七个。", "十一月十七日", BB_SNAP("bg_study.jpg"))
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
    jump ch4


# ---------------- 反谜题：第八个名字 ----------------
label hangman_8:
    $ picked = []
    $ msg = ""
    $ giving_up = False
    $ hz_fails = 0
    while not giving_up:
        call screen bb_hangman(HANGMAN, picked, msg, hz_fails)
        if _return[0] == "giveup":
            $ giving_up = True
        else:
            $ picked.append(_return[1])
            if len(picked) >= HANGMAN["need"]:
                $ msg = HANGMAN["fail"]
                $ picked = []
                $ hz_fails += 1
    $ ev_give("erased8_note")
    N "第八个名字，被墨擦掉了。"
    N "擦的顺序，自下而上。那不是污渍，是一个书写动作。"
    return


# ---------------- 第六章：大厅 · 第一轮 ----------------
label ch6:
    call screen bb_card("第六章", "大厅", "每人只有一次机会——说完就要等下一个人。", "十一月十七日", BB_SNAP("bg_hall_ring.jpg"))
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
    # 规则全文在帮助屏里，可帮助屏只挂在 Esc 菜单上，第一次对质之前没人会去点。
    # 不弹窗、不打断——一条便签，看得见就走。
    $ renpy.notify("怎么举、怎么用方向键选：菜单里的「怎么读这份卷宗」。")
    call bb_debate_run(round1)
    call bb_result_card(round1)
    # 手稿在第一日夜里还有"下一个环节"：第二组照片。省略它，第十三章那句
    # "边角磨得起了毛——比别处那张，更旧"就没有可比的另一张，
    # 而证据栏里"和照片上那人蹲着的袖口一样"讲的近拍也是这一组给的。
    show spr_shen as talker at bb_talk_r
    SHEN "好。下一个环节。"
    N "他站起身，走到墙边，从一幅挂画后面取下一个小盒子。盒子里是一叠照片——比我们在书房看到的那批更旧。"
    SHEN "这是第二组。来自另一个角度。"
    N "他把照片一张一张摊在中央的矮木几上。第一张是临东海大桥的远景。第二张是桥下的礁石。第三张是桥东侧匝道下方的避险车道。"
    N "车道尽头，草丛里有一个蹲着的人。"
    N "和我们在书房看到的那张照片，是同一个人。但角度不同——这张更近，能看清连帽衫的拉链，和袖口处一个小小的绣标。"
    show spr_su as talker at bb_talk_r
    SU "你们看到那个绣标了吗？"
    show spr_me as talker at bb_talk_r
    ME "没看清。"
    show spr_su as talker at bb_talk_r
    SU "我拍下来了。"
    N "沈南舟没有回应。他把最后一张照片放在桌上。"
    N "这张照片上，是一个人的正脸。年轻，大约二十岁，短发，眼睛很亮。他站在一栋建筑前，手里拿着一本打开的书，像刚参加完某场毕业典礼。"
    N "照片背面用红笔写着：陈默，2009年，临海市。"
    show spr_lin as talker at bb_talk_r
    LIN "这是你儿子？"
    N "沈南舟没有回答。她把同一句又问了一遍，声音比第一次大。"
    show spr_lin as talker at bb_talk_r
    LIN "这是你儿子？"
    show spr_shen as talker at bb_talk_r
    SHEN "我不知道你们想知道什么。我只知道，你们需要看到这张照片。"
    show spr_zhou as talker at bb_talk_r
    ZHOU "为什么不直接告诉我们名字？沈南舟，你儿子的名字——陈默？"
    show spr_shen as talker at bb_talk_r
    SHEN "陈先生，您觉得，他应该叫什么？"
    N "我坐在沙发上，没有回答。那张照片上的脸，和我不一样。我知道不一样。"
    N "我不认识这张脸。但我不该不认识。"
    N "我的手开始抖。我不知道为什么。"
    jump day1_pass


# ---------------- 沉默计数 ----------------
label bb_debate_run(rt):
    if bb_auto:
        # 不启界面，把这一轮从头抵到尾：破绽句全部走一遍 rebut()，
        # 让 seat_state／result_lines／grants 这些数据层分支也在冒烟测试里跑到。
        # 要跑两遍——第一夜的死亡时间是听完林晚那句才到手，回头才抵得动王剑。
        $ bb_trace("[AUTO] debate " + rt.label)
        $ _pass = 0
        while _pass < 2:
            $ _n = len(rt.statements)
            $ _k = 0
            while _k < _n:
                $ rt.i = _k
                $ rt.hear_current()
                $ _s = rt.statements[_k]
                if _s.weak_to and _s.weak_to in have:
                    $ rt.select(_s.weak_to)
                    $ rt.rebut()
                $ _k += 1
            $ _pass += 1
        $ rt.i = 0
        $ rt.selected = None
        return
    while not rt.done:
        $ rt.hear_current()
        call screen bb_debate(rt)
        $ act = _return[0]
        $ arg = _return[1]
        if act == "select":
            $ rt.select(arg)
        elif act == "read":
            # 批注读完收起：判词留在纸上会挡住下一句的读法，但它不该被忘记——
            # 句子本身还在原位，收掉的只有这一层。
            $ rt.message = ""
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
    # 六日的账要合到一处算，所以每结算一轮就往总账上记一笔。
    if bb_auto:
        $ bb_trace("[AUTO] result " + rt.head + " " + str(rt.silence) + "/" + str(rt.silence_total))
    $ bb_silence_won += rt.silence
    $ bb_silence_possible += rt.silence_total
    call screen bb_result(rt.silence, rt.silence_total, rt.result_lines(),
                          head=rt.head, sub=rt.sub)
    return


# ---------------- 尾：合上手稿 ----------------
label epilogue:
    if bb_auto:
        $ bb_trace("[AUTO] epilogue")
    scene bg_hangzhou
    $ bb_day = "二〇二五年十一月十五日"
    show spr_gu as talker at bb_talk_r
    N "顾言笙的调查笔记。十一月十五日，夜里。"
    GU "把“我是不是”写成“我不知道”的那个人，藏在一个死掉的陈默后面。"
    GU "他抹掉的，是他自己的名字。"
    GU "无名指那一件，我把它翻了出来。"
    GU "那张二〇〇九年的照片，原件，我从市档案馆借到了。借据，一页。"
    GU "照片里，无名指，是直的。手稿第六章里，那只手，是弯的。"
    GU "一个是二〇〇九，一个是二〇一九。中间，隔着十年。直变弯，十年里，也说得通。"
    GU "另一种，是本来就不是同一只手。"
    GU "两种读法。我倾向哪一种，我没有写下来。"
    GU "那张纸条左角有一个笔画的钩，周亦安那册会徽本子的末页写着“陈是守望者之一”——苏蔓那句“同一只手”，比的是这两处的笔迹。"
    GU "她没有做鉴定，她把两页并排比过，就这样说了。"
    GU "这一步我信，但我只认到“同一只手”为止。我没有拿去问周亦安。"
    GU "一问，我就得先把我这边查到的全交出去。留着“待查”，他不知道我查到哪儿。"
    GU "十一月十二日我写“停”的那三件——封皮上缺掉的“鸟”字、那册倒填年份的日记、庄园里的两名仆从。这三件，我没有再补一个字。"
    GU "停，也是一种答法。"
    $ tally = []
    $ tally.append("手里的证据 " + str(len(have)) + " ／ " + str(len(EVIDENCE)) + " 条。")
    $ tally.append("逼出的沉默 " + str(bb_silence_won) + " ／ " + str(bb_silence_possible) + " 处。")
    $ tally.append("第八个名字，我终究没有写下来。")
    $ tally.append("我没有指认谁。这本书不许我指认谁。")
    if bb_auto:
        $ bb_trace("[AUTO] 收账 证据 " + str(len(have)) + "／" + str(len(EVIDENCE))
                   + " 沉默 " + str(bb_silence_won) + "／" + str(bb_silence_possible))
    call screen bb_result(bb_silence_won, bb_silence_possible, tally,
                          head="收卷", sub="合上的一页")
    if bb_auto:
        # 存读回归的第二趟：档已经在 start 里读回来了，这里的 have／沉默数是档里的数。
        if os.environ.get("BB_LOAD"):
            $ bb_trace("[LOAD] 读回 证据 " + str(len(have)) + " 沉默 " + str(bb_silence_won))
            # 环境音也得跟着档回来：这一行没有 [AMB]，说明读档后这一章是静音的。
            if BB_AMB_AT_START:
                $ bb_trace("[AMB-LOAD] ok " + BB_AMB_AT_START)
            else:
                $ bb_trace("[AMB-LOAD] FAIL 读档后没有认出该放哪一条")
            $ renpy.quit()
        # 第一趟：整本跑完的最后一刻真的存一次，供第二趟读回来。
        # 读档要过的 after_load 回调（环境音那条得重置）、档里的五个 Debate 对象，
        # 只有在这里才被真碰一次——以前只在标题屏上探过"存进去不报错"。
        $ renpy.save("regress")
        $ bb_trace("[LOAD] 存盘 证据 " + str(len(have)) + " 沉默 " + str(bb_silence_won))
        $ renpy.quit()
    return
