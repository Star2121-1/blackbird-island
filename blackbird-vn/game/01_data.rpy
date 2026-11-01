# ============================================================
# 数据层：证据、圆桌发言、探索热点、拼字谜题
# 全部台词取自《黑鸟岛-终稿》第一章 / 第三章 / 第六章，措辞不改。
# ============================================================

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

    have = set()

    def ev_give(eid):
        if eid not in have:
            have.add(eid)
            renpy.notify("获得证据：" + EVIDENCE[eid].name)

    def ev_list():
        return [EVIDENCE[e] for e in sorted(have, key=lambda x: list(EVIDENCE).index(x))]

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

    SPR_FOR = {
        "沈南舟": "spr_shen", "王剑": "spr_wang", "赵寒": "spr_zhao",
        "方廷": "spr_fang", "周亦安": "spr_zhou", "林晚": "spr_lin",
        "苏蔓": "spr_su", "陈默": "spr_me",
    }

    ROUND1 = [
        Statement("王剑",
                  "我开车经过大桥。撞人的不是我。但我看见了。那辆车是黑色的，跑得很快。",
                  miss="这句话和后来发生的事不矛盾。没有破绽。"),
        Statement("王剑",
                  "我下车看了一眼，那个人还活着。我把他送到我诊所——他在路上就没了。",
                  weak_to="time_window",
                  hit="林晚的手指在膝盖上轻轻叩了几下。\n\n“死亡在十点之前，十点四十七，就不会有呼吸。”\n\n王剑没有说话。",
                  hit_kind="silence"),
        Statement("林晚",
                  "官方记“当场死亡”。王剑的自首书，记“途中死亡”。都是事后的话。我父亲那版，是事前的。",
                  hears=["time_window"],
                  miss="法医把两句话的先后摆得很清楚。没有破绽。"),
        Statement("方廷",
                  "我二〇〇九年代理的是死者家属一方，负责和肇事方谈赔偿协议。",
                  weak_to="diary_fang",
                  hit="方廷停了一下。他没有说那份协议上的签字是谁的。\n\n沈南舟替他记着：是他签的字。",
                  hit_kind="silence"),
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
                  hit_kind="counter"),
    ]

    class Debate(object):

        def __init__(self, seats, statements, bullets=3):
            self.seats = seats
            self.statements = statements
            self.max_bullets = bullets
            self.silence_total = sum(
                1 for s in statements if s.weak_to and s.hit_kind == "silence")
            self.reset()

        def reset(self):
            self.i = 0
            self.passes = 0
            self.silence = 0
            self.counters = 0
            self.bullets = self.max_bullets
            self.selected = None
            self.message = ""
            self.broken = {}
            self.heard = set()
            self.done = False

        def cur(self):
            return self.statements[self.i]

        def seat_state(self, name):
            for k, kind in self.broken.items():
                if self.statements[k].speaker == name:
                    return "broken" if kind == "silence" else "countered"
            if self.done:
                return "idle"
            if self.cur().speaker == name:
                return "active"
            return "idle"

        def select(self, eid):
            self.selected = eid
            self.message = EVIDENCE[eid].name + " —— " + EVIDENCE[eid].brief

        def rebut(self):
            s = self.cur()
            if not self.selected:
                self.message = "手里没有举起任何东西。反驳不成立。"
                return
            if s.weak_to and self.selected == s.weak_to and self.i not in self.broken:
                self.broken[self.i] = s.hit_kind
                if s.hit_kind == "silence":
                    self.silence += 1
                elif s.hit_kind == "counter":
                    self.counters += 1
                for g in s.grants:
                    ev_give(g)
                self.message = s.hit
                self.selected = None
                return
            self.bullets -= 1
            self.selected = None
            self.message = s.miss or "这句话没有对得上任何东西。"
            if self.bullets <= 0:
                self.done = True

        def advance(self):
            """听完一句往下走；走到末尾就回到第一句，重听一轮。
            沉默不是靠一次听完逼出来的。"""
            self.selected = None
            self.message = ""
            if self.i + 1 >= len(self.statements):
                self.passes += 1
                self.i = 0
            else:
                self.i += 1

        def end(self):
            self.done = True

        def hear_current(self):
            """第一次听到这一句，才把跟着它的东西交给我。"""
            if self.i not in self.heard:
                self.heard.add(self.i)
                for g in self.cur().hears:
                    ev_give(g)

        def result_lines(self):
            L = []
            if self.silence == self.silence_total:
                L.append("三处沉默，一处不多。")
                L.append("沈南舟把照片一张一张收回盒子。他说：今天到这里。")
            elif self.silence == 0:
                L.append("没有人停下来。")
                L.append("第一轮结束的时候，我一个字也没有问出来。")
            else:
                L.append(str(self.silence) + " 处沉默。还有 "
                         + str(self.silence_total - self.silence) + " 句话，说完了。")
            if self.counters:
                L.append("主人没有沉默。他把问题推回我手上——那一条不算赢。")
            if self.bullets <= 0:
                L.append("反驳的机会用完了。剩下的话，留到第二天再问。")
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
        "give_on_end": "erased8_note",
    }

    EV("erased8_note", "被擦掉的第八名",
       "名单第八个名字被墨擦掉，擦的顺序自下而上。第三章里，我没有看清。以后也未必看得清。", "第三章")

    # ---------------- 探索热点（x/y 为屏幕比例） ----------------
    DOCK_SPOTS = [
        {"id": "invite", "x": 0.18, "y": 0.66},
        {"id": "hand", "x": 0.63, "y": 0.52},
    ]

    HALL_SPOTS = [
        {"id": "lock", "x": 0.50, "y": 0.74},
    ]

    STUDY_SPOTS = [
        {"id": "note", "x": 0.28, "y": 0.44},
        {"id": "roster", "x": 0.55, "y": 0.58},
        {"id": "diary", "x": 0.78, "y": 0.34},
    ]
