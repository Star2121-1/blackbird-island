# ============================================================
# 数据层：证据、圆桌发言、探索热点、拼字谜题
# 全部台词取自《黑鸟岛-终稿》第一章 / 第三章 / 第六章，措辞不改。
# ============================================================

# have 必须是 default，不能在 init python 里赋值。
# init 里造出来的对象，Ren'Py 存档时按"还是 init 那个对象"处理，不当内容写进档；
# 于是 `have.add(...)` 再多，重开游戏读档回来也是一套空的——实测过：
# 全六日跑完存一档，第二趟只读档，沉默 14 条回来了，证据 0 条。
default have = set()

init -1 python:

    # ---------------- 证据 ----------------
    class Evidence(object):
        def __init__(self, eid, name, brief, chapter):
            self.id = eid
            self.name = name
            self.brief = brief
            self.chapter = chapter

    EVIDENCE = {}

    def EV(eid, name, brief, chapter):
        EVIDENCE[eid] = Evidence(eid, name, brief, chapter)

    EV("invite", "烫金请柬",
       "三天前出现在公寓门缝下。邀请函上只写了五个字：临东海事件。没有落款，没有解释。", "第一章")
    EV("lock", "大厅的新锁",
       "锁是新换的。钥匙只有一把，在沈南舟那里。傍晚六点以后渡轮不再返回。", "第一章")
    EV("hand", "握手的那只手",
       "很凉，像刚从水里捞出来。有一根指头抵着掌心，弯的。我没有多想。", "第一章")
    EV("note", "书房门口的纸条",
       "苏蔓说：这不是沈南舟的字迹。他的字工整，有书法底子。这行字是匆忙中写的。", "第三章")
    EV("roster", "临东海案相关人员名单",
       "名单上有八个名字。岛上七个。第八个，我没有看清。", "第三章")
    EV("diary_fang", "沈南舟日记 · 方廷",
       "方廷——当年那份赔偿协议，是他签的字。", "第三章")
    EV("diary_me", "沈南舟日记 · 陈默",
       "陈默——他在说谎。没有句号，没有解释。用的是现在时。", "第三章")
    EV("time_window", "两版死亡时间",
       "官方：晚间十时至十一时，当场死亡。林建国尸检初稿：九时至十时。估的，不是测的。", "第六章")
    EV("phrase", "先杀后撞",
       "词是周亦安替沈南舟挑的。可邀请函上的五个字，是沈南舟自己写的。", "第六章")

    # ---- 第二日至第五日陆续到手的 ----
    EV("watch_badge", "守望者的绣标",
       "盾形徽章，交叉钥匙加一条波浪线。缝在周亦安早年手抄册子的封皮内页，和照片上那人蹲着的袖口一样。", "第七章")
    EV("east_wing_records", "东翼那一纸袋",
       "赵寒撬开东翼取出的一牛皮纸袋：一年一叠的立牌记录。一个名字，一个现场，一个记号。", "第八章")
    EV("cup_empty", "倒扣的空杯",
       "八仙桌上八只杯，一人一只。七只满着正放；空的那只倒扣在正对门的位置，从来没有续过水。", "第九章")
    EV("pos_c_sheet", "位置C的勘查页",
       "从原卷宗抽出、边缘磨起毛的一页，折成四折。散场前收进桌下抽屉，第二天回到了桌上。", "第九章")
    EV("handbook_blank", "手账的空白页",
       "我这一夜，没有记一个字。那几页我又看了一遍。空白。", "第十章")
    EV("door_mark", "门楣上的记号",
       "一张便签，没有字。盾形，交叉的钥匙，盾底下一道波浪线。留给会认得它的人。", "第十章")
    EV("plaque_record", "立牌的记录",
       "一个名字，一个现场，一个记号。落款只有一个字：陈。", "第十一章")
    EV("blank_sheet", "空白那张纸",
       "背面一个字也没有。留下这一张的人，把名字空掉了。", "第十二章")
    EV("face_photo", "木匣里的照片",
       "黑白的。一个男人的脸，边角磨得起了毛。背面写着：陈默。", "第十三章")
    EV("seal_rec", "封装记录",
       "位置C的异物，只记了三条：发现、位置、封装人。没有第四条。", "第十四章")
    EV("erased8_photo", "苏蔓拍的名单照片",
       "墨擦的痕迹在照片里。她比我们更早看见了这件事。", "第十四章")
    EV("blank_col", "空着的复核人一栏",
       "二〇〇九年，这一栏是空的。没有填。", "第十五章")
    EV("cable_cut", "断掉的信号缆",
       "沿礁石埋着，线皮磨毛，一绞就断。从那天起，黑鸟岛和大陆再无连接。", "第十五章")
    EV("bridge_count", "十二米，十八步",
       "摆一具尸体要三十秒。剩下的至少四十六分半，他没有离开桥。", "第十六章")
    EV("rope_stale", "旧缆桩的缆绳",
       "小艇的缆绳是从旧缆桩上解开的。他没有出岛，傍晚缆绳还是解开的样子。", "第十七章")
    EV("cup_mark", "压出杯印的浅纸",
       "杯收走了，桌上多了一截浅白的纸。纸没有写字，只压出一个浅淡的杯印。", "第十八章")
    EV("note_hand", "同一只手",
       "那张纸条与“陈是守望者之一”那一行，同一只手——左角一个笔画的钩。", "第十八章")
    EV("lock_half", "移了半寸的新锁",
       "后半夜停电，林晚去东翼换保险丝。赵寒撬开的那道新锁向左移了半寸。柄是凉的。", "第十九章")

    # ---- 第一日的纸袋，与终章摊开的旧物 ----
    EV("wet_trail", "走廊的水渍",
       "从书房方向延伸过来，尽头是一张被踩了一半的纸片。纸上只有一行字：他不是沈南舟。", "第二章")
    EV("photos", "四张照片",
       "桥、礁石、草丛，和一个蹲在草丛里挖东西的人。背面：位置C，距撞击点12米，发现异物。", "第四章")
    EV("cigarette", "袖口那一截烟灰",
       "他又吸了一口，烟灰落在袖口上，他没有管。后来他把烟灰弹掉，把烟掐灭。", "第五章")
    EV("plaque_2013", "二〇一三那块牌",
       "二〇一三年，王剑回到黑鸟岛，给那一块立过牌。到场是二〇一三，不是二〇〇九。", "第八章")
    EV("envelope", "一只信封",
       "照片和封装记录并折进去。沈南舟说：这个，留给该留的人。他没有递给谁。", "第二十三章")

    EV_ORDER = list(EVIDENCE)
    BB_CH_ORDER = []
    for _e in EVIDENCE.values():
        if _e.chapter not in BB_CH_ORDER:
            BB_CH_ORDER.append(_e.chapter)

    BB_CN = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]

    def bb_cn(n):
        """结算的散文行用汉字数，界面读数用阿拉伯数字——两套不能串。"""
        if 0 <= n <= 10:
            return BB_CN[n]
        if n < 20:
            return "十" + BB_CN[n - 10]
        return str(n)

    def ev_give(eid):
        if eid not in have:
            have.add(eid)
            bb_sfx("pick")
            renpy.notify("获得证据：" + EVIDENCE[eid].name)

    def ev_list():
        # EV_ORDER 在 init 里算一次。原先每排一个元素就 list(EVIDENCE).index(x) 一遍，
        # 33 条是 O(n²)，而它在对质屏和图鉴屏上每帧都调。
        return [EVIDENCE[e] for e in EV_ORDER if e in have]

    # 图鉴按章节报"缺几条"，章节顺序就是证据表的出现顺序。
    def ev_chapter_counts():
        """返回 [(章节, 已收, 总数)]，只含真的有证据的章节。"""
        out = []
        for ch in BB_CH_ORDER:
            ids = [k for k, v in EVIDENCE.items() if v.chapter == ch]
            if ids:
                out.append((ch, sum(1 for k in ids if k in have), len(ids)))
        return out

    # ---------------- 并排：两件之间的那一行 ----------------
    # 终章把筛子交到玩家手里之后，桌上多一个动作：挑两条证据并排放下。
    # 中间那一行只在手稿自己把这两件并排写过的地方出现。规矩比台词那道更严：
    # 整段必须连着抄，不许改一个字，也不许把两个小句从不同的章里拼起来
    # （check_verbatim 的 each_pair 走的是"norm 之后是正文子串"，不是子序列）。
    # 没并排写过的，中间空着——这一屏不打分，也不许把空读成"错了"。
    PAIRS = {}

    def PA(a, b, line):
        PAIRS[frozenset((a, b))] = line

    PA("seal_rec", "face_photo",
       "他把二〇〇九那张封装记录，和那张黑白照片，并排摊在桌上。")
    PA("envelope", "seal_rec",
       "沈南舟收起那张照片。他把它和那张封装记录，并折进一只信封。")
    PA("envelope", "face_photo",
       "沈南舟收起那张照片。他把它和那张封装记录，并折进一只信封。")
    PA("seal_rec", "blank_col",
       "他把二〇〇九那张封装记录，重新摊在八仙桌上。那一栏，空的，复核人。")
    PA("roster", "cup_empty",
       "桌上摆着八只杯。名单上，八个名字，一人一只。")
    PA("face_photo", "cup_empty",
       "他把照片放在八仙桌上，正对着那只空杯。")
    PA("cup_empty", "cup_mark",
       "桌上多了一截浅白的纸。纸没有写字，只压出一个浅淡的杯印。")
    PA("wet_trail", "note",
       "但地上有一滴水渍——从书房方向延伸过来，在水渍的尽头，有一张被踩了一半的纸片。")
    PA("note", "watch_badge",
       "那张纸条左角有一个笔画的钩，周亦安那册会徽本子的末页写着“陈是守望者之一”——苏蔓那句“同一只手”，比的是这两处的笔迹。")
    PA("photos", "watch_badge",
       "这张更近，能看清连帽衫的拉链，和袖口处一个小小的绣标。")
    PA("erased8_photo", "watch_badge",
       "名单。还有那个绣标——周亦安补拍的那一张，我存过。")
    PA("pos_c_sheet", "plaque_record",
       "左边，位置C的勘查页。中间，那张立牌的记录。右边，一张空白的纸。")
    PA("pos_c_sheet", "blank_sheet",
       "左边，位置C的勘查页。中间，那张立牌的记录。右边，一张空白的纸。")
    PA("plaque_record", "blank_sheet",
       "左边，位置C的勘查页。中间，那张立牌的记录。右边，一张空白的纸。")
    PA("pos_c_sheet", "bridge_count",
       "二〇〇九年，有人把一具尸体摆到位置C。十二米。让它看起来，属于那场车祸。")
    PA("time_window", "pos_c_sheet",
       "二〇〇九年。位置C那具尸体，九到十时已经死了。撞车，十点四十七。")
    PA("bridge_count", "plaque_record",
       "四十七分钟，够一个人做三件事。摆。立牌。签上自己的名字。")
    PA("east_wing_records", "plaque_record",
       "是立牌的记录。一张纸上，一个名字，一个现场，一个记号。一年一叠，摞了一摞。")
    PA("invite", "phrase",
       "可按林晚刚才的说法，九点死的人，十点四十七才被撞——那不叫交通事故，那叫先杀后撞。")

    # 自动播放摆上去的那一对：第二十三章桌上真的并排过的两件（这一屏挂在第二十四章，
    # 引用的是上一章那一拍）。
    BB_AUTO_PAIR = ("seal_rec", "face_photo")

    def pair_line(a, b):
        """两件都放下才有中间那一行。同一件不算并排。"""
        if not a or not b or a == b:
            return ""
        return PAIRS.get(frozenset((a, b)), "")

    # ---------------- 圆桌发言 ----------------
    class Statement(object):
        """weak_to=None 表示这句话本轮没有破绽。
        hit_kind: silence=逼出沉默 / counter=主人反问 / reveal=只翻开一条信息
        hears: 听到这句话（第一次显示）时到手的证据"""

        def __init__(self, speaker, text, weak_to=None, hit="", hit_kind="silence",
                     miss="", grants=None, hears=None):
            self.speaker = speaker
            self.text = text
            self.weak_to = weak_to
            self.hit = hit
            self.hit_kind = hit_kind
            self.miss = miss
            self.grants = grants or []
            self.hears = hears or []

    SEATS = ["沈南舟", "王剑", "赵寒", "方廷", "周亦安", "林晚", "苏蔓", "陈默"]

    # 名字 → 立绘。这里管的是"这个人有没有脸"，不是"谁坐在桌边"（那是 SEATS）：
    # 顾言笙不上桌，但她在第一夜和杭州那几屏里说了一百多句，台上得有她。
    SPR_FOR = {
        "沈南舟": "spr_shen", "王剑": "spr_wang", "赵寒": "spr_zhao",
        "方廷": "spr_fang", "周亦安": "spr_zhou", "林晚": "spr_lin",
        "苏蔓": "spr_su", "陈默": "spr_me", "顾言笙": "spr_gu",
    }

    ROUND1 = [
        Statement("王剑",
                  "我开车经过大桥。撞人的不是我。但我看见了。那辆车是黑色的，跑得很快。",
                  miss="这句话和后来发生的事不矛盾。没有破绽。"),
        Statement("王剑",
                  "我下车看了一眼，那个人还活着。我把他送到我诊所——他在路上就没了。",
                  weak_to="time_window",
                  hit="林晚的手指在膝盖上轻轻叩了几下。\n\n“死亡在十点之前，十点四十七，就不会有呼吸。”\n\n王剑没有说话。",
                  hit_kind="silence",
                  miss="王剑把同一句又说了一遍，一个字没有改。这一句，自首书对得上。"),
        Statement("林晚",
                  "官方记“当场死亡”。王剑的自首书，记“途中死亡”。都是事后的话。我父亲那版，是事前的。",
                  hears=["time_window"],
                  miss="法医把两句话的先后摆得很清楚。没有破绽。"),
        # 终稿第六章，就在她那句"事前／事后"后面：原尸斑是她父亲当年在原地量下的，
        # 挪不动。这一条是"摆尸"在原著里唯一的物理来源——第二日那句"是被摆在那里的"
        # 在终稿 1587 没有署名、游戏里也是旁白，方廷那一轮说"死后被移动"，
        # 玩家得先在这一夜听见过原尸斑，才不是在接一句空话。
        Statement("林晚",
                  "尸体被挪动过。我父亲是先在原地，把原尸斑固定了。原尸斑固定在哪里，身体当时就在哪里。后来怎么挪，都不影响它。移动尸体的，是把死者送进诊所的那一个——你们已经听过了。",
                  miss="原尸斑固定在哪儿，人就躺在哪儿——那是她父亲当年在原地量下来的一件，挪不走。她报的是尸检里最硬的一条，没有破绽。"),
        Statement("方廷",
                  "我二〇〇九年代理的是死者家属一方，负责和肇事方谈赔偿协议。",
                  weak_to="diary_fang",
                  hit="方廷停了一下。他没有说那份协议上的签字是谁的。\n\n沈南舟替他记着：是他签的字。",
                  hit_kind="silence",
                  miss="委托函摆在协议前面。他说的这一句，是一个律师的本分。"),
        Statement("赵寒",
                  "那晚我值班。经过大桥，站在桥上看了很久。没下车。",
                  miss="赵寒的烟盒还握在手里，没有点燃。他说的每一句都像已经称过分量。"),
        Statement("周亦安",
                  "你故意的。",
                  miss="周亦安是对主人说的。这一句不是留给我的。"),
        Statement("沈南舟",
                  "词是周先生替我挑的。我写的就是“临东海事件”。我没有写下“先杀后撞”，但我也没有把那几个字从你们脑子里抹掉。",
                  weak_to="invite",
                  grants=["phrase"],
                  hit="“需要听出这句话的人，自然会听出来。”\n\n主人不会沉默。他只是把问题推回到你手上。",
                  hit_kind="counter",
                  miss="主人不接我手里这一条。他把目光移到下一个人身上。"),
    ]

    class Debate(object):
        """label 是这一局摆在桌角的名目：哪一晚、第几轮。界面不自己猜。"""

        # 存档里躺着的是这个对象本身（round1..5 是 default 全局），标准 pickle 只
        # __dict__.update，后加的字段不会自己长出来。__version__ 由 __getstate__ 写进档，
        # 旧档没这一行就按 0 算，走 after_upgrade 补齐。
        __version__ = 1

        def __init__(self, seats, statements, bullets=3, label="大厅 · 第一轮",
                     head="第一轮 · 结算", sub="逼出来的停顿"):
            self.seats = seats
            self.statements = statements
            self.max_bullets = bullets
            self.label = label
            self.head = head
            self.sub = sub
            self.silence_total = sum(
                1 for s in statements if s.weak_to and s.hit_kind == "silence")
            self.reset()

        def __getstate__(self):
            st = dict(vars(self))
            st["__version__"] = self.__version__
            return st

        def __setstate__(self, state):
            version = state.pop("__version__", 0)
            self.__dict__.update(state)
            self.after_upgrade(version)

        def after_upgrade(self, version):
            """补旧档缺的字段，别指望玩家重开。
            早先这里只有 after_upgrade 没有 __setstate__——那个名字是
            renpy.object.Object 的钩子，普通 object 子类存档时没人会调它，
            整段是看着安心、实际从不执行死代码。"""
            if version < 1:
                for k, v in (("max_bullets", 3), ("head", "第一轮 · 结算"),
                             ("sub", "逼出来的停顿"), ("spent", set()),
                             ("heard", set()), ("broken", {}), ("counters", 0),
                             ("passes", 0), ("done", False), ("message", ""),
                             ("selected", None), ("i", 0), ("silence", 0)):
                    if not hasattr(self, k):
                        setattr(self, k, v)
                if not hasattr(self, "silence_total"):
                    self.silence_total = sum(
                        1 for s in self.statements
                        if s.weak_to and s.hit_kind == "silence")

        def reset(self):
            self.i = 0
            self.passes = 0
            self.silence = 0
            self.counters = 0
            self.bullets = self.max_bullets
            self.selected = None
            self.message = ""
            self.broken = {}
            self.spent = set()
            self.heard = set()
            self.done = False

        def cur(self):
            return self.statements[self.i]

        def seat_state(self, name):
            for k, kind in self.broken.items():
                if self.statements[k].speaker == name:
                    # reveal 只是翻开一条信息，不是谁停下来，也不是主人反问——不给章。
                    if kind == "silence":
                        return "broken"
                    if kind == "counter":
                        return "countered"
            if self.done:
                return "idle"
            if self.cur().speaker == name:
                return "active"
            return "idle"

        def select(self, eid):
            # 举起证据不写批注：批注框压在发言页原位，一写就把正在抵的那句话盖掉，
            # 玩家只能凭记忆按"反驳"。正文改由发言页右下角那行供读。
            self.selected = eid

        def rebut(self):
            s = self.cur()
            if self.bullets <= 0:
                # 机会用尽之后这扇门是关着的，界面上"反　驳"已经按不动；
                # 这一格是给回滚／自动播放那类不经过界面的路兜底。
                self.message = "反驳的机会已经用完。这一轮只能往下听。"
                return
            if not self.selected:
                self.message = "手里没有举起任何东西。反驳不成立。"
                return
            if self.i in self.broken:
                # 这一句已经停过一次了。重听时再举一次不该扣机会——
                # 名牌上的静默章是"这个人停过一次"，不是"他这一句也停过了"。
                self.message = "这一句已经停过了。"
                self.selected = None
                return
            if s.weak_to and self.selected == s.weak_to and self.i not in self.broken:
                self.broken[self.i] = s.hit_kind
                # 抵中了要响，而且两种抵法两种响法：沉默是压下去的一声闷，
                # 反问是章子落在纸上的一记。屏幕上的角章是看不见的动作，得有个声音对上。
                bb_sfx("silence" if s.hit_kind == "silence" else "stamp")
                if s.hit_kind == "silence":
                    self.silence += 1
                elif s.hit_kind == "counter":
                    self.counters += 1
                for g in s.grants:
                    ev_give(g)
                self.message = s.hit
                self.spent.add(self.selected)
                self.selected = None
                return
            self.bullets -= 1
            self.selected = None
            self.message = s.miss or "这句话没有对得上任何东西。"
            if self.bullets <= 0:
                # 用尽的是"判错几次"，不是桌上还剩几句话。早先这里一并置 done，
                # 三次误按就把没读到的正文连同"只在第一次听到时才到手"的证据一起
                # 锁死——第一夜的死亡时间挂在第三句上，手快的人开局就把自己打死，
                # 而图鉴永远挂着缺一条。句子还得读完：收轮是玩家按的，代价写在他眼前。
                self.bullets = 0
                _left = len(self.statements) - len(self.heard)
                self.message += ("机会用完，剩下的只能听。"
                                 + ("还有 " + bb_cn(_left) + " 句没有听过。" if _left else ""))

        def advance(self):
            """听完一句往下走；走到末尾就回到第一句，重听一轮。
            沉默不是靠一次听完逼出来的。"""
            self.selected = None
            self.message = ""
            if self.i + 1 >= len(self.statements):
                self.passes += 1
                self.i = 0
                # 死亡时间在第一夜的第三节才到手，要用在第二节上——不回头就破不了。
                # 桌上只写"第 2 遍在听"，第一次循环的人读不出那是给他的出口。
                if self.passes == 1:
                    self.message = ("一圈说完了。再听一遍——"
                                    "有些句子要先听到后面，才知道前面缺什么。")
            else:
                self.i += 1

        def end(self):
            self.done = True

        def hear_current(self):
            """第一次听到这一句，才把跟着它的东西交给我。"""
            if self.i not in self.heard:
                self.heard.add(self.i)
                # 第一次听到这一句，说话的人才开口；重听不重播。
                bb_voice_line(self.cur().text)
                for g in self.cur().hears:
                    ev_give(g)

        def result_lines(self):
            L = []
            if self.silence == self.silence_total:
                L.append(bb_cn(self.silence_total) + "处沉默，一处不多。")
                # 不写具体场景：木匣照片要到第十三章才摊开，"今天到这里"是第九章的话。
                # 这一条五轮通用，写死任何一个动作都会和正文撞车。
                L.append("该停的都停了。没有人再添一句话。")
            elif self.silence == 0:
                L.append("没有人停下来。")
                L.append("这一轮结束的时候，我一个字也没有问出来。")
            else:
                L.append(bb_cn(self.silence) + "处沉默。还有"
                         + bb_cn(self.silence_total - self.silence) + "句话，说完了。")
            if self.counters:
                L.append("主人没有沉默。他把问题推回我手上——那一条不算赢。")
            if self.bullets <= 0:
                L.append("反驳的机会用完了。")
                # 机会用尽不再收轮，所以"还有没听过的"这件事只有真没听过才说得上。
                if len(self.statements) - len(self.heard):
                    L.append("剩下的话，留到第二天再问。")
            L.append("没有人被指认。沉默也不是证据。")
            return L

        def jump_to(self, name):
            """点座位 = 回到这个人身上。优先落到他还没被打破、而且真有破绽的那一句。"""
            order = [k for k, s in enumerate(self.statements) if s.speaker == name]
            pick = None
            for k in order:
                if k not in self.broken and self.statements[k].weak_to:
                    pick = k
                    break
            if pick is None:
                for k in order:
                    if k not in self.broken:
                        pick = k
                        break
            if pick is None and order:
                pick = order[0]
            if pick is not None:
                self.i = pick
                self.selected = None
                self.message = ""

    # ---------------- 拼字（第八名被擦） ----------------
    # 这一版是"反谜题"：任何组合都拿不到名字。手稿第三章只写到"我没有看清"。
    HANGMAN = {
        "prompt": "名单上八个名字。第七个是陈默。第八个，被墨擦掉了。",
        "candidates": ["陈", "沈", "王", "林", "周", "方", "赵", "苏", "剑", "亦", "晚", "蔓"],
        "need": 2,
        "locked": True,
        "fail": "擦的顺序，自下而上。那不是污渍，是一个书写动作。\n\n我没有看清。",
    }

    EV("erased8_note", "被擦掉的第八名",
       "名单第八个名字被墨擦掉，擦的顺序自下而上。第三章里，我没有看清。以后也未必看得清。", "第三章")

    # ---------------- 探索热点（x/y 为屏幕比例） ----------------
    DOCK_SPOTS = [
        {"id": "invite", "x": 0.18, "y": 0.58},
        {"id": "hand", "x": 0.63, "y": 0.52},
    ]

    HALL_SPOTS = [
        {"id": "lock", "x": 0.50, "y": 0.62},
    ]

    STUDY_SPOTS = [
        {"id": "note", "x": 0.28, "y": 0.44},
        {"id": "roster", "x": 0.55, "y": 0.58},
        {"id": "diary", "x": 0.78, "y": 0.34},
    ]

    # ---- 第一日至第五日的取证点 ----
    HALL_SPOTS_D1 = [
        {"id": "wettrail", "x": 0.36, "y": 0.56},
    ]

    STUDY_SPOTS_D1 = [
        {"id": "photos", "x": 0.44, "y": 0.46},
        {"id": "cigarette", "x": 0.68, "y": 0.56},
    ]

    TABLE_SPOTS_D2 = [
        {"id": "records", "x": 0.26, "y": 0.56},
        {"id": "cups", "x": 0.46, "y": 0.48},
        {"id": "sheet", "x": 0.68, "y": 0.42},
    ]

    CORRIDOR_SPOTS_D3 = [
        {"id": "mark", "x": 0.30, "y": 0.34},
        {"id": "handbook", "x": 0.68, "y": 0.52},
    ]

    TABLE_SPOTS_D3 = [
        {"id": "plaque", "x": 0.36, "y": 0.50},
        {"id": "blank", "x": 0.60, "y": 0.42},
    ]

    FACE_SPOT = [
        {"id": "face", "x": 0.50, "y": 0.48},
    ]

    STUDY_SPOTS_D4 = [
        {"id": "erased", "x": 0.48, "y": 0.46},
    ]

    TABLE_SPOTS_D4 = [
        {"id": "blankcol", "x": 0.46, "y": 0.48},
    ]

    SHORE_SPOTS_D4 = [
        {"id": "cable", "x": 0.36, "y": 0.58},
    ]

    DOCK_SPOTS_D5 = [
        {"id": "rope", "x": 0.34, "y": 0.54},
    ]

    TABLE_SPOTS_D5 = [
        {"id": "cupmark", "x": 0.42, "y": 0.48},
        {"id": "notehand", "x": 0.66, "y": 0.42},
    ]

    WING_SPOTS_D5 = [
        {"id": "lockhalf", "x": 0.52, "y": 0.44},
    ]
