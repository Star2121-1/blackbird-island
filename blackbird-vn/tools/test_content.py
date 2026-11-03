# -*- coding: utf-8 -*-
"""内容完整性与公平性自检：不启 Ren'Py，跨文件静态扫一遍全本。

test_logic.py 验的是"一条发言链算得对不对"，这里验的是"整本摊开能不能走通"：

- 证据表里每一条都要有地方拿得到（图鉴写着 33 条，拿不满就是骗人）。
- 每一轮的破绽句，所用证据必须在那一夜之前就已经可拿到（拿不到就打不破，是坑玩家）。
- 热点表里的每个 id 都要有对应的 spot_ 标签；定义了没人调的 spot_ 标签是死内容。
- 五轮的沉默总数、句数、破绽数打出来，README 里那些数字要对着它。
- 键位三方对齐：引擎真正生效的 config.keymap（截图脚本落的档）、游戏内帮助页、README。
- 配音对齐：对质每一句发言都要有映射 + 落地的 mp3，键不许过期、文件不许错挂；README
  里那句"配了几句、什么音色"要对着发言表，不对就是宣传。
- 图对齐：每张注册的背景／立绘要在洗图清单里、盘上要有文件、剧本里要有人引用、
  章节卡钉的翻拍要存在、而且每张背景都得有环境音。

    python blackbird-vn/tools/test_content.py
"""
import glob
import io
import json
import os
import re
import sys
import types

import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(HERE, "game")

CN_DAY = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6}

# 文件级默认日序：正文文件各管一天。
FILE_DAY = {
    "03_flow.rpy": 1,
    "05_day1_gap.rpy": 1,
    "06_day2.rpy": 2,
    "07_day3.rpy": 3,
    "08_day4.rpy": 4,
    "09_day5.rpy": 5,
    "10_spots.rpy": 1,
    "11_day6.rpy": 6,
    "12_days.rpy": 1,
}

# 分节标题：# ---------------- 第三日 ---------------- / 第二夜
HDR = re.compile(r"^#\s*-{2,}\s*第([一二三四五六])\s*[日夜]")
GIVE = re.compile(r"ev_give\(\s*[\"']([a-z0-9_]+)[\"']\s*\)")
SPOT_LABEL = re.compile(r"^label spot_([a-z0-9_]+)\s*:")
SPOT_REF = re.compile(r"\{\"id\":\s*[\"']([a-z0-9_]+)[\"']")

fails = []


def check(name, cond):
    if not cond:
        fails.append(name)
    print(("PASS " if cond else "FAIL ") + name)


def info(msg):
    print("     " + msg)


# ---------------- 1) 把数据层的 init 块接进命名空间 ----------------
def load_init(fname, g):
    p = os.path.join(GAME, fname)
    s = io.open(p, encoding="utf-8").read()
    m = re.search(r"^init (?:-1 )?python:\n((?:(?:    .*)?\n)*)", s, re.M)
    body = "\n".join(l[4:] if l.startswith("    ") else l
                     for l in m.group(1).split("\n"))
    exec(compile(body, p, "exec"), g)


fake = types.ModuleType("renpy")
fake.notify = lambda *a, **k: None
fake.store = None
# 同 test_logic：数据层会调用 bb_sfx／renpy.sound，静态自检里没有声音可放。
fake.sound = types.SimpleNamespace(play=lambda *a, **k: None)
fake.music = types.SimpleNamespace(play=lambda *a, **k: None,
                                   get_playing=lambda *a, **k: None,
                                   register_channel=lambda *a, **k: None)
sys.modules.setdefault("renpy", fake)
g = {"renpy": fake, "bb_sfx": lambda *a, **k: None}
for f in ("01_data.rpy", "13_rounds_ab.rpy", "14_rounds_cd.rpy"):
    load_init(f, g)

EVIDENCE = g["EVIDENCE"]
ROUNDS = [("第一夜", g["ROUND1"]), ("第二夜", g["ROUND2"]), ("第三夜", g["ROUND3"]),
          ("第四夜", g["ROUND4"]), ("第五夜", g["ROUND5"])]

# ---------------- 2) 静态扫全部 .rpy：取证点落在哪一天 ----------------
# sites[eid] = 最早可拿到的那一天
sites = {}
spot_days = {}   # spot_<id> 定义在哪一天
cur_label = None
# 正文文件必须在 FILE_DAY 里登记过。早先漏登记只当第 0 天，于是新增一天
# （比如第七日）时，那条 ev_give 会被算成"最早到手"，而它其实排在破绽句之后——
# 一个能骗过"证据当夜之前可拿到"的洞。
unregistered = set()

for p in sorted(glob.glob(os.path.join(GAME, "*.rpy"))):
    fname = os.path.basename(p)
    if fname.startswith(("00_", "02_", "04_", "99_")):
        continue          # 样式／界面／图像注册／截图自检：不取证
    src_txt = io.open(p, encoding="utf-8").read()
    if fname not in FILE_DAY and (GIVE.search(src_txt) or HDR.search(src_txt)):
        unregistered.add(fname)
    day = FILE_DAY.get(fname, 0)
    with io.open(p, encoding="utf-8") as f:
        for line in f:
            m = HDR.match(line)
            if m:
                day = CN_DAY[m.group(1)]
                continue
            m = SPOT_LABEL.match(line)
            if m:
                cur_label = m.group(1)
                spot_days.setdefault(cur_label, day)
                continue
            for eid in GIVE.findall(line):
                if eid not in sites or day < sites[eid]:
                    sites[eid] = day

# 发言表里的 hears／grants：听那句的当夜就到手；拼字收场的纸条同理。
for idx, (nm, rows) in enumerate(ROUNDS, start=1):
    for s in rows:
        for eid in list(s.hears or []) + list(s.grants or []):
            if eid not in sites or idx < sites[eid]:
                sites[eid] = idx
for eid in [v for v in (g.get("HANGMAN") or {}).get("give_on_end", "").split(",") if v]:
    sites.setdefault(eid, 3)   # 第三章的拼字，第一夜之前就到

# 热点表里引用的 id（spot_x 由 bb_search 调起）
refs = set()
for p in sorted(glob.glob(os.path.join(GAME, "*.rpy"))):
    with io.open(p, encoding="utf-8") as f:
        refs.update(SPOT_REF.findall(f.read()))

# ---------------- 3) 断言 ----------------
check("证据表非空（%d 条）" % len(EVIDENCE), len(EVIDENCE) >= 30)

# 图鉴按章报"缺几条"的那几行，读的是 BB_CH_ORDER。它先被建出来、又被下面
# 一句"顺手重置"清空过一次——空表让 ev_chapter_counts() 永远返回 []，
# 图鉴上承诺的分组行就一行都不画，而游戏照开、lint 照绿。
ch_order = g["BB_CH_ORDER"]
check("图鉴的章节表非空（%d 章）" % len(ch_order), bool(ch_order))
check("章节表覆盖每一条证据（漏 %d 章）" % len(
    set(EVIDENCE[k].chapter for k in EVIDENCE) - set(ch_order)),
    set(EVIDENCE[k].chapter for k in EVIDENCE) <= set(ch_order))
g["have"] = set(EVIDENCE)      # have 是 `default`，引擎才造得出来，这里当"全收齐"来算
counts = g["ev_chapter_counts"]()
check("按章计数真的能算出行（%d 行）" % len(counts), bool(counts))
check("按章加起来的总数等于证据条数（算成 %d）" % sum(c[2] for c in counts),
      sum(c[2] for c in counts) == len(EVIDENCE))
check("全收齐时每章都显示收满（没满的 %d 章）"
      % len([c for c in counts if c[1] != c[2]]),
      all(c[1] == c[2] for c in counts))

check("正文文件都在 FILE_DAY 登记了日序（漏 %d 个）" % len(unregistered),
      not unregistered)
for n in sorted(unregistered):
    info("%s 里有取证点/分节日，但没登记日序——它会被当成第 0 天" % n)

orphan = sorted(set(EVIDENCE) - set(sites))
check("每一条证据都有拿得到的地方，无孤儿（缺 %d 条）" % len(orphan), not orphan)
if orphan:
    info("拿不到：" + "、".join(EVIDENCE[i].name + "(" + i + ")" for i in orphan))

bogus = sorted(set(sites) - set(EVIDENCE))
check("ev_give 没有发不存在的证据（多 %d 条）" % len(bogus), not bogus)
if bogus:
    info("表外：" + " ".join(bogus))

# 破绽句用的证据，那一夜之前必须已经可拿到
late = []
for idx, (nm, rows) in enumerate(ROUNDS, start=1):
    for s in rows:
        if s.weak_to and sites.get(s.weak_to, 99) > idx:
            late.append("%s：%s 要用 %s（第 %s 天才拿得到）"
                        % (nm, s.speaker, EVIDENCE[s.weak_to].name, sites.get(s.weak_to)))
check("每一轮的破绽句，所用证据当夜之前就已可拿到", not late)
for x in late:
    info(x)

# 反问句不许用还没到手的证据
late2 = [s for idx, (nm, rows) in enumerate(ROUNDS, start=1) for s in rows
         if s.hit_kind == "counter" and s.weak_to and sites.get(s.weak_to, 99) > idx]
check("主人的反问同样不吃未来的证据", not late2)

dead = sorted(set(spot_days) - refs)
check("没有定义了却没人调的热点（死内容 %d 个）" % len(dead), not dead)
if dead:
    info("死热点：" + " ".join(dead))

missing = sorted(refs - set(spot_days))
check("热点表里每个 id 都有对应的 spot_ 标签（缺 %d 个）" % len(missing), not missing)
if missing:
    info("缺标签：" + " ".join(missing))

total = sum(len([s for s in rows if s.weak_to and s.hit_kind == "silence"])
            for _, rows in ROUNDS)
weak_total = sum(len([s for s in rows if s.weak_to]) for _, rows in ROUNDS)
info("五轮合计：%s 句 / 破绽 %s 处（其中沉默 %s 处，剩下的是翻页与反问）" % (
    "、".join(str(len(r)) for _, r in ROUNDS),
    weak_total, total))
info("每轮沉默：%s" % "、".join(
    str(len([s for s in r if s.weak_to and s.hit_kind == "silence"])) for _, r in ROUNDS))
check("全六日沉默总数 %d 处（文档与截图按这个数写死，动了要一起改）" % total,
      total == 11 and all(len([s for s in r if s.weak_to and s.hit_kind == "silence"]) >= 2
                          for _, r in ROUNDS))
check("每条破绽句的 hit／miss 文案齐（由 test_logic 细验，这里只查总数）",
      all(s.hit and s.miss for _, rows in ROUNDS for s in rows if s.weak_to))

# 三类破绽在文案上必须分得开：沉默＝有人停下来；翻页＝没人停，卷宗多翻开一页；
# 反问＝主人不停，把问题推回来。混了，玩家就分不出自己赢没赢。
REVEAL_TAIL = "这不是谁停下来。是卷宗里多翻开的一页。"
STOP_WORDS = ("没有再说", "没有再往下说", "没有再讲", "没有说话", "没有再动",
              "停了停", "停了一下", "静了很久", "收了回去")
bad_reveal = [s.speaker for _, rows in ROUNDS for s in rows
              if s.weak_to and s.hit_kind == "reveal"
              and not (s.hit or "").endswith(REVEAL_TAIL)]
bad_silence = ["%s：%s" % (s.speaker, s.text[:12])
               for _, rows in ROUNDS for s in rows
               if s.weak_to and s.hit_kind == "silence"
               and not any(w in (s.hit or "") for w in STOP_WORDS)]
bad_counter = [s.speaker for _, rows in ROUNDS for s in rows
               if s.weak_to and s.hit_kind == "counter"
               and REVEAL_TAIL in (s.hit or "")]
check("翻页句都以那句收尾（漏 %d 句）" % len(bad_reveal), not bad_reveal)
check("沉默句都真的写了一个人停下（漏 %d 句）" % len(bad_silence), not bad_silence)
if bad_silence:
    info("没写出停下的沉默句：" + " ".join(bad_silence))
check("反问句不写成沉默也不借用翻页收尾（违 %d 句）" % len(bad_counter), not bad_counter)


# ---------------- 4) 两套日历 ----------------
# 菜单里的"日期"读 bb_day，而只有扉页会写它。岛上的日子（十一月十七日起）和
# 顾言笙写笔记的日子（二〇二五年十一月四日起）是两套日历，一夜之间来回切。
# 扉页刚把日期盖成岛上的十一月十八日，下一段笔记念的却是十一月六日——
# 少了重盖的那一行，玩家看到的就是一个记错日子的本子。
# 比的是"每一个报了日期的抬头"，不是"每一段杭州景的第一个抬头"：六夜只给六段笔记，
# 于是终稿同一天的两条笔记会并进同一个 scene 里（十一日白天＋十二日清晨），
# 只看第一个的话，后面那几条换日子的抬头就没人管了。
HANGZHOU = "scene bg_hangzhou"
NOTE_DATE = re.compile(r'^\s*N "[^"]*十一月([一二三四五六七八九十]+)日')
STAMP = re.compile(r'\$ bb_day = "二〇二五年十一月([一二三四五六七八九十]+)日"')
LOOKBACK = 40

hangzhou = 0
no_stamp = []
for p in sorted(glob.glob(os.path.join(GAME, "*.rpy"))):
    fname = os.path.basename(p)
    if fname.startswith(("00_", "01_", "02_", "04_", "13_", "14_", "99_")):
        continue
    lines = io.open(p, encoding="utf-8").read().split("\n")
    for i, line in enumerate(lines):
        m = NOTE_DATE.match(line)
        if not m:
            continue
        # 只比杭州那间书房里的笔记：往上找最近的一条 scene，不是 bg_hangzhou 就跳过
        # （岛上正文里也有"十一月十七日"这样的旁白，那用的是另一套日历）。
        above = [lines[j].strip() for j in range(i - 1, max(-1, i - LOOKBACK), -1)]
        near = next((s for s in above if s.startswith("scene ")), None)
        if near is None or HANGZHOU not in near:
            continue
        hangzhou += 1
        got = next((g.group(1) for s in above for g in [STAMP.search(s)] if g), None)
        if got != m.group(1):
            no_stamp.append("%s:%d 笔记念十一月%s日，HUD 盖的是%s"
                            % (fname, i + 1, m.group(1),
                               "十一月" + got + "日" if got else "岛上那天"))

check("每个报了日期的杭州笔记抬头都重盖了 HUD 日期（抬头 %d 处，漏 %d 段）"
      % (hangzhou, len(no_stamp)), not no_stamp)
for b in no_stamp:
    info(b)

# ---------------- 4b) 一条证据只有一个来处 ----------------
# 同一件东西从两个地方被"第一次捡到"，玩家手里那条证据就有两个出处；
# 而引用它的那句台词（第十八章"从她口袋里取出来的"）会跟着一起悬空。
# 这一条抓过两次：书房门口的纸条（热点写成第二个来处）和守望者的绣标
# （第八章从周亦安册子里已经拿到，东翼那一格又发了一次）。
GIVE = re.compile(r'\$ ev_give\("([a-z_0-9]+)"\)')
grants = {}
for p in sorted(glob.glob(os.path.join(GAME, "*.rpy"))):
    fname = os.path.basename(p)
    if fname.startswith(("00_", "01_", "02_", "99_")):
        continue        # 99_shots 是给截图预填状态的，不算剧情里的来处
    for i, line in enumerate(io.open(p, encoding="utf-8").read().split("\n")):
        for eid in GIVE.findall(line):
            grants.setdefault(eid, []).append("%s:%d" % (fname, i + 1))
twice = dict((k, v) for k, v in grants.items() if len(v) > 1)
check("每条证据在剧情里只有一个来处（重复发放 %d 条）" % len(twice), not twice)
for k in sorted(twice):
    info("%s ← %s" % (k, "　".join(twice[k])))

# ---------------- 5) 热点不复述正文 ----------------
# bb_search 的出口是"看完了才能走"，所以每个热点玩家都必须点开。热点里若整句抄回
# 正文刚念过的那一句，就不是补充细节，是逼着人重读一遍——实测四处中招（空杯、水渍、
# 照片袋、木匣那张脸），最长的一个热点只有一处可点，点下去全是重复。
NARR = re.compile(r'^\s*N "((?:[^"\\]|\\.)+)"')
NARR_UNESC = lambda t: t.replace("\\", "")


def narr_lines(path):
    out = []
    for line in io.open(path, encoding="utf-8").read().split("\n"):
        m = NARR.match(line)
        if m:
            out.append(NARR_UNESC(m.group(1)))
    return out


body = set()
for p in sorted(glob.glob(os.path.join(GAME, "*.rpy"))):
    if os.path.basename(p) != "10_spots.rpy":
        body.update(narr_lines(p))

dupes = ["热点复述正文：" + t for t in narr_lines(os.path.join(GAME, "10_spots.rpy"))
         if len(t) >= 10 and t in body]   # 短句（"我认得它。"）是回声，不是复述
check("热点不整句复述正文旁白（复述 %d 句）" % len(dupes), not dupes)
for d in dupes:
    info(d)


# ---------------- 存档带得走的容器必须是 default ----------------
# 实测来的：have 早先是 `init python:` 里 `have = set()`，运行时往里 add。
# 引擎把 init 造出来的对象按"还是 init 那一个"处理，不把它的内容写进档——
# 于是全六日跑完存一档，重开游戏只读档：沉默 14 条回来了（标量是重新赋值的），
# 证据 0 条。玩家视角就是"读档把手里的证据读没了"。
# 第二只坑是同一只：BB_AMB_NOW／BB_PAGE_NOW 在 init 里 = {}，运行时按下标写。
# 只盯 .add／.append 抓不到它——所以三种写法都查，且扫全部 .rpy。
# 判据：init 块里"构造期"跑的写 → 安全；其余（label 的 $、screen 的 $、
# 运行时才叫的函数体）→ 容器必须是 default。
# EV() 和 bb_amb_play() 都写在 init 块的 def 体里，静态上长一样，区别只在
# "调用点在不在构造期"。所以两趟扫：先收集构造期（init 块正文那一层）叫过的名字，
# 再据此判每一处写是构造还是运行时。
# 99_shots 是开发脚本，不打进包，不参与存读，跳过。
# 非空字面量也算：BB_AMB_NOW = {"file": None} 就是带内容造的，
# 早先只认 `{}`/`[]`/`set()` 这三种空壳，正好让它从指缝里漏过去。
CREATED = re.compile(r"^(\w+) = (?:[\[{(]|set\(\)|dict\()")
# 等号必须紧跟下标：早先写成 `\] =` 会把屏体里的
# `text EVIDENCE[d.selected].name style "bb_micro" color bb_gold_dark` 一路松到后面的
# 某个等号上，读一次也当成写。
MUT = re.compile(r"^\s+(\w+)(?:\.(?:add|append|update|clear|discard)\b|\[[^\]]+\]\s*=(?!=))")
CALL = re.compile(r"^\s*(\w+)\s*\(")
DEFHEAD = re.compile(r"^(?:async )?def ")
INITHEAD = re.compile(r"^init[^\n:]*python[^\n:]*:$")


def blocks(src):
    """逐行给出 (原文行, 去空白, 缩进, 当时的 def 名栈, 是否在 init 块, 块正文缩进)。
    栈里只放 def，不放 class：class 只是命名空间，它自己不改任何容器；
    把 class 也压进去的话，类里的方法缩进比"块正文"深，栈就永远清不干净了。"""
    init_ind, stack = None, []
    for ln in src.split("\n"):
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        ind = len(ln) - len(ln.lstrip())
        if ind == 0:
            init_ind, stack = None, []
            if INITHEAD.match(s):
                init_ind = -1
        elif init_ind is not None and init_ind < 0:
            init_ind = ind
        while stack and ind <= stack[-1][0]:
            stack.pop()
        if init_ind is not None and DEFHEAD.match(s):
            stack.append((ind, re.sub(DEFHEAD, "", s).split("(")[0]))
        yield ln, s, ind, [n for _, n in stack], init_ind is not None, init_ind


at_runtime, created, declared = set(), set(), set()
for fn in sorted(os.listdir(GAME)):
    if not fn.endswith(".rpy") or fn == "99_shots.rpy":
        continue
    src = io.open(os.path.join(GAME, fn), encoding="utf-8").read()
    ctor_calls = set()
    for ln, s, ind, stack, in_init, init_ind in blocks(src):
        # 只认"正文那一层缩进"上的整句调用：EV("invite", ...) 这种。
        # 函数体内的调用（result_lines 里那句 bb_cn(...)）不算——它是运行时才叫的，
        # 混进来的话会把方法误判成构造器，方法里的局部变量就逃过检查了。
        if in_init and not stack and ind == init_ind:
            ctor_calls |= set(CALL.findall(ln))
    for ln, s, ind, stack, in_init, init_ind in blocks(src):
        hit = MUT.match(ln)
        if hit and not (in_init and set(stack) <= ctor_calls):
            at_runtime.add(hit.group(1))
        # 只统计"块正文那一层"造的容器：函数体里的 `L = []` 是局部变量，
        # 跟着调用它的函数一起判就行，本身不是模块级状态。
        if in_init and not stack:
            c = CREATED.match(s)
            if c:
                created.add(c.group(1))
    declared |= set(re.findall(r"^default (\w+) = ", src, re.M))
# 正则一漂，这条闸门就会静默变绿。init 直接构造的容器至少有 EVIDENCE／SEAT_POS，
# 一个都没抓到就说明匹配本身失效了，直接报错而不是放行。
check("容器闸门真的在扫（init 造出的容器抓到 %d 个）" % len(created),
      {"EVIDENCE", "SEAT_POS"} <= created)
unsaveable = sorted(n for n in at_runtime & (created - declared) if n not in declared)
check("运行时被改动的容器都声明成了 default（漏 %d 个）" % len(unsaveable),
      not unsaveable)
for n in unsaveable:
    info("%s 在 init 里赋值、运行时改动内容，但没声明 default——存档带不走" % n)

# ---------------- 6) 引号体例 ----------------
# 终稿那份 markdown 用的是打字机引号，界面排成了中文弯引号（全项目 82 对）。
# 两边混着的后果不是难看，是同一句话在项目里有好几种写法：
# "陈是守望者之一"这一行出现过弯双、弯单、直单三种，而帮助页上「日志」和"图例"
# 是同一个快捷栏里的两个按钮名，一个折一个直——玩家会以为它们在指两种东西。
# 规则：玩家看得见的字符串里不许有 ASCII 直引号；『』只用错过一次，一并禁掉。
# 「」留着，但它只指界面元素名，不掺进台词。
CJK = re.compile(u"[一-鿿]")


def visible_literals(line):
    """吐出一行代码里所有双引号字符串（反转义后的内容），并摘掉行尾注释。
    逐字符走是有必要的：`# 他写了"停"两个字` 这种注释里的引号玩家看不见，
    而 `color "#0b0d1012"` 里的 # 在字符串里，不能当注释切。"""
    out, buf, instr = [], [], False
    i = 0
    while i < len(line):
        c = line[i]
        if instr:
            if c == "\\" and i + 1 < len(line):
                buf.append(line[i + 1])
                i += 2
                continue
            if c == '"':
                out.append("".join(buf))
                buf, instr = [], False
                i += 1
                continue
            buf.append(c)
        elif c == '"':
            instr = True
        elif c == "#":
            break
        i += 1
    return out


bad_quote = []
# 只认"贴着汉字的引号"：Ren'Py 的撇号、英文缩写里的撇号不是中文引号用错，
# 而 `don't` 这种整串英文也不该被这条闸门咬——判据是撇号紧挨着汉字才算引号。
QUOTE_NEXT_TO_CJK = re.compile(u"(['\"])\\s*(?=[一-鿿])|(?<=[一-鿿])\\s*(['\"])")
for fn in sorted(os.listdir(GAME)):
    if not fn.endswith(".rpy") or fn == "99_shots.rpy":
        continue
    src = io.open(os.path.join(GAME, fn), encoding="utf-8").read()
    for i, line in enumerate(src.split("\n"), 1):
        if not line.strip() or line.strip().startswith("#"):
            continue
        for lit in visible_literals(line):
            # 只管混着中文的那些：字体名、颜色、路径里的 # 和 ' 不该被这条咬住。
            if not CJK.search(lit):
                continue
            if QUOTE_NEXT_TO_CJK.search(lit) or u"『" in lit or u"』" in lit:
                bad_quote.append((fn, i, lit))
check("玩家可见文本没有直引号／『』（发现 %d 处）" % len(bad_quote), not bad_quote)
for fn, i, lit in bad_quote[:12]:
    info("%s:%d %s" % (fn, i, lit[:40]))


# ---------------- 键位诚实 ----------------
# 帮助页和 README 各写一份键位，引擎里还有一份 config.keymap。三方对不上，
# 玩家照着按就按出错事——这一轮之前 g 换渲染器、h 半张界面就没人知道。
# config.keymap 只有跑起来才有，所以料由截图脚本（99_shots.rpy）落一份
# shots/_keymap.json 出来；没有这份档就 FAIL，别拿过期包对着旧事实盖章。
KEYMAP_DUMP = os.path.join(HERE, "shots", "_keymap.json")
if not os.path.exists(KEYMAP_DUMP):
    check("有 shots/_keymap.json（先跑一遍截图脚本）", False)
else:
    km = json.load(io.open(KEYMAP_DUMP, encoding="utf-8"))
    check("键位表抄全了（%d 张）" % len(km), len(km) >= 15)
    for act in ("choose_renderer", "hide_windows"):
        check("%s 已废掉（还绑在 %s 上）" % (act, km.get(act)), not km.get(act))
    for act in ("dismiss", "game_menu", "toggle_skip", "skip", "rollback",
                "rollforward", "help", "screenshot", "self_voicing"):
        check("%s 还活着" % act, bool(km.get(act)))

    help_src = io.open(os.path.join(GAME, "02_screens.rpy"), encoding="utf-8").read()
    # 两栏都算：PageDown、"截图" 这类写在说明里而不是键名里的，也要两边对齐。
    keys_on_help = "".join(a + b for a, b in
                           re.findall(r'use bb_key\("([^"]*)", "([^"]*)"\)', help_src))
    readme = io.open(os.path.join(HERE, "README.md"), encoding="utf-8").read()
    tbl = readme.split("## 键位")[1].split("\n##")[0] if "## 键位" in readme else ""
    check("README 有键位表", len(tbl) > 40)
    # 两边都得写到的那些键。用中文词而不是字母，免得 "S" 到处都能匹配上。
    for word in ("Esc", "Tab", "Ctrl", "F1", "PageUp", "PageDown", "句点", "截图"):
        check("「%s」帮助页和 README 都写了" % word,
              word in keys_on_help and word in tbl)

# ---------------- 空格真能翻页，翻过的热点还能再点 ----------------
# "空格 ／ 点击 继续"那行字写在每句对白下面，可按的是运行时状态：键盘焦点在谁手上。
# 引擎那句对白自己的 SayBehavior 只在自己拿着焦点时才认 dismiss，而玩家照界面说的
# 点一下之后，焦点就归了对白页那张全屏按钮——空格从此没人接（2026-11-03 玩家实测报的
# 就是这一条，修之前 space_warm 那趟 at=None，一直卡到闸门自己收档）。
# 静态读代码量不出焦点，所以料只能真起窗口投真按键：99_shots.rpy 的 keytest 落
# shots/_keytest.json，每趟记 {"focus": 焦点在谁, "at": 翻页发生在第几拍, "shots": [投了几次]}。
# 五件事分开钉，各管一种"看起来过了其实没过"：
#   ① 翻页必须发生在注入之后（自动前进／语音自己走了，不算这一格的本事）；
#   ② click_arm 那趟的焦点必须真的落在 Button 上——不然 space_warm 是在白过，
#      它验的还是"焦点没被抢走"那个假世界；
#   ③ space_slow 的第一下不许翻页（打字吞掉那一口），第二下才翻：补了 unfocused
#      之后最容易被顶掉的就是"先打完再翻"；
#   ④ card_space／result_space 的焦点也得是 Button，而且同样被空格收掉——扉页和结算页
#      没有 SayBehavior，dismiss_unfocused 那一格管不到它们，只在对白上修好等于修了一半
#      （本作 25 张卡，每章开头都要撞一次那堵墙）；
#   ⑤ spot_reclick 那两下点的是同一个真坐标，两次都得交回 ("spot", id)，而 found
#      只记一条——只看第一下有没有效，等于没测"翻过的还能再点"这件事。
KEYTEST_DUMP = os.path.join(HERE, "shots", "_keytest.json")
KT_PHASES = ("space_cold", "click", "click_arm", "space_warm", "space_slow",
             "card_space", "result_space", "spot_reclick")
_kt = {}
if not os.path.exists(KEYTEST_DUMP):
    check("有 shots/_keytest.json（先跑 BB_KEYTEST=1 那一趟，见 docs/development.md 的自检一节）", False)
else:
    with io.open(KEYTEST_DUMP, encoding="utf-8") as f:
        _kt = json.load(f)
    check("键盘闸门八趟全在（缺哪趟＝keytest 卡在哪句：%s）" % ",".join(sorted(_kt)),
          set(_kt) == set(KT_PHASES))
    for _p in KT_PHASES:
        _r = _kt.get(_p) or {}
        _at = _r.get("at")
        _shots = _r.get("shots") or []
        # 最后一拍注入、注入后 8 拍（约 0.4 秒）内必须翻掉；再晚就是在演别的戏。
        check("%s 翻页发生在注入的那一下（at=%s shots=%s）" % (_p, _at, _shots),
              bool(_shots) and _at is not None and _shots[-1] <= _at <= _shots[-1] + 8)
    _arm = (_kt.get("click_arm") or {}).get("focus")
    check("那一按点真把键盘焦点交给了全屏按钮（focus=%s）" % _arm, _arm == "Button")
    _cardf = (_kt.get("card_space") or {}).get("focus")
    check("那一趟真停在扉页上（focus=%s，不是对白页）" % _cardf, _cardf == "Button")
    _resf = (_kt.get("result_space") or {}).get("focus")
    check("结算那一趟真停在结算页上（focus=%s，不是对白页）" % _resf, _resf == "Button")
    # 玩家报的第二件：热点看完就点不动。同一个坐标投两次，两次都得把 ("spot", id)
    # 交回来；found 只许记一条——"看过 N ／ M"那格直接数它的长度，
    # 重看一次就报成 5／4，而"看完才能走"那道闸门也会提前开。
    _rc = _kt.get("spot_reclick") or {}
    check("翻过的热点还能再点（两次都交回 spot：%s）" % _rc.get("returns"),
          _rc.get("returns") == [["spot", "invite"], ["spot", "invite"]])
    check("重看不把 found 记成两条（%s）" % _rc.get("found"), _rc.get("found") == 1)
    # 键位表那一半：白页写"空格"，表里就得真有空格——两处都得有，
    # 只挂 dismiss 的话焦点一被抢走就又哑了（这正是本轮修的东西）。
    if os.path.exists(KEYMAP_DUMP):
        with io.open(KEYMAP_DUMP, encoding="utf-8") as f:
            _km = json.load(f)
        check("K_SPACE 在 dismiss 里", "K_SPACE" in (_km.get("dismiss") or []))
        check("K_SPACE 也在 dismiss_unfocused 里（%s）" % _km.get("dismiss_unfocused"),
              "K_SPACE" in (_km.get("dismiss_unfocused") or []))
    else:
        check("K_SPACE 的焦点无关那一格没法查（没有 shots/_keymap.json）", False)

# ---------------- 配音诚实 ----------------
# 对质整桌发言都进 voice 通道，台词原文当键。这件事有三个地方会烂：
#   台词改了没重跑 build_voice → 键和发言表对不上，那一句静悄悄没有声音；
#   mp3 没生成／被误删 → 映射在、文件不在，玩家按到就是静音；
#   文档写"配了哪几句／几副嗓子" → 和引擎不一致就是宣传。
# 料还是那份 shots/_statements.json（引擎里摊平的五轮发言表）。
STMT_DUMP = os.path.join(HERE, "shots", "_statements.json")
VOICE_RPY = os.path.join(GAME, "15_voice.rpy")
VOICEDIR = os.path.join(GAME, "voice")
if not os.path.exists(STMT_DUMP):
    check("有 shots/_statements.json（先跑一遍截图脚本）", False)
elif not os.path.exists(VOICE_RPY):
    check("有 game/15_voice.rpy（跑 tools/build_voice.py）", False)
else:
    with io.open(STMT_DUMP, encoding="utf-8") as f:
        _rows = json.load(f)
    check("发言表非空（%d 句）" % len(_rows), len(_rows) > 0)
    # 键是原文：两句撞在一起就只有一条声音，后一句永远静着。
    check("对质台词不重样（重样＝共用一条 mp3，另一句静掉）",
          len(set(r["text"] for r in _rows)) == len(_rows))

    vsrc = io.open(VOICE_RPY, encoding="utf-8").read()
    pairs = re.findall(r'^\s*("(?:[^"\\]|\\.)*")\s*:\s*"(voice/[^"]+)",\s*$', vsrc, re.M)
    voice_map = {}
    for k, v in pairs:
        voice_map[json.loads(k)] = v
    check("映射表非空（%d 条）" % len(voice_map), len(voice_map) > 0)

    want = dict((r["text"], "voice/%s.mp3" % r["id"]) for r in _rows)
    missing = sorted(set(want) - set(voice_map))
    stale = sorted(set(voice_map) - set(want))
    check("整桌发言都在映射里（漏 %d 条）" % len(missing), not missing)
    for m in missing:
        info("漏配：" + m[:24])
    check("映射里没有过期键（%d 条：台词改过就要重跑 build_voice）" % len(stale), not stale)
    for m in stale:
        info("过期键：" + m[:24])
    # 文件名也要对上 id：只查"有没有文件"的话，r1_1 的内容挂到 r5_7 上照样过。
    wrong = sorted(t for t, f in voice_map.items() if want.get(t) != f)
    check("每一条都落在自己的文件上（错位的 %d 条）" % len(wrong), not wrong)
    for t in wrong:
        info("错位：" + t[:24] + " → " + voice_map[t])

    for f in sorted(set(voice_map.values())):
        p = os.path.join(GAME, f.replace("/", os.sep))
        if not os.path.exists(p):
            check("文件在场 %s" % f, False)
        elif os.path.getsize(p) < 2000:
            check("%s 小得不像一条语音（%d 字节）" % (f, os.path.getsize(p)), False)
    check("语音文件全在（%d 条）" % len(voice_map),
          all(os.path.exists(os.path.join(GAME, f.replace("/", os.sep)))
              for f in voice_map.values()))
    # 孤声：目录里躺着没人引用的文件，包白背一份。
    onfile = set("voice/" + n for n in os.listdir(VOICEDIR) if n.endswith(".mp3"))
    check("voice/ 里没有没人引用的文件（多 %d 个）" % len(onfile - set(voice_map.values())),
          not (onfile - set(voice_map.values())))

    # 引擎侧：mixer 没注册的话，人声跟着"音效音量"走，设置页那一格是假的。
    settings = io.open(os.path.join(GAME, "00_settings.rpy"), encoding="utf-8").read()
    check("config.has_voice 打开了", "config.has_voice = True" in settings)
    screens = io.open(os.path.join(GAME, "02_screens.rpy"), encoding="utf-8").read()
    check('设置页有人声音量那一格', 'Preference("voice volume")' in screens)
    # 自动播放的回归不能带人声：一秒三屏，念的永远是上一句。
    _vl = settings[settings.find("def bb_voice_line"):settings.find("def bb_voice_line") + 400]
    check("自动播放不起人声", "if bb_is_auto():" in _vl)
    # 收轮要掐断：结算页接着说话，桌上还挂着上一句的尾巴不像话。
    flow = io.open(os.path.join(GAME, "03_flow.rpy"), encoding="utf-8").read()
    check("对质收轮时掐断人声", "bb_voice_stop()" in flow)

    # 引擎侧的凭据：文件在场不等于起得了播——mixer 没注册、路径写错，
    # 玩家那边就是一句话没有声音。这份档由截图脚本喂两句原文探出来。
    VPROBE = os.path.join(HERE, "shots", "_voice.json")
    if not os.path.exists(VPROBE):
        check("有 shots/_voice.json（人声起播的凭据，重跑截图脚本）", False)
    else:
        with io.open(VPROBE, encoding="utf-8") as f:
            vp = json.load(f)
        plays = [x for x in vp if "playing" in x]
        check("探针句数对得上（%d 句）" % len(plays), len(plays) == 2)
        for x in plays:
            check("「%s」挂上了 voice 声道" % x["text"], x.get("playing") == x.get("want"))
        # 对质循环走的是 Debate.hear_current 那条线，不是直接调函数——接线断在这里
        # 上面两条照样全过，所以这份档里必须有一条经过 hear_current 的探针。
        hc = [x for x in vp if "hear_current" in x]
        check("hear_current 那条路也起得了播", bool(hc) and hc[0]["hear_current"] == hc[0]["want"])
        stops = [x for x in vp if "stop" in x]
        check("bb_voice_stop 收得干净", bool(stops) and stops[-1]["stop"] is None)

    _rd = io.open(os.path.join(HERE, "README.md"), encoding="utf-8").read()
    sec = _rd.split("## 配音")[1].split("\n##")[0] if "## 配音" in _rd else ""
    check("README 有配音这一节", len(sec) > 40)
    check("README 写的句数和发言表一致（%d 句）" % len(_rows),
          ("%d 句" % len(_rows)) in sec)
    check("README 说清了是 edge-tts 神经音色", "edge-tts" in sec)
    check("README 说了共用几副嗓子", ("副嗓子" in sec) or ("副音色" in sec))
    check("README 说了整桌都配、人声不标记破绽", "不标记" in sec or "一句不漏" in sec)

# ---------------- 图 ----------------
# 一张背景有五条命：原图在、被管线洗过、注册在、有人引用、章节卡钉它时有环境音。
# 断在哪一条都是静默的：
#   漏在 BG_KEYS 里 → 删空 game/images/ 重跑管线就少一块，那一屏退成纯色占位；
#   注册了没人引用 → 包里白背一张图（lint 也不报，因为 image 语句本身就是"用到"）；
#   卡片翻拍不在 BB_AMB_BY_BG 里 → 那一章没有海浪也没有风声，卡片照开。
imgs_src = io.open(os.path.join(GAME, "04_images.rpy"), encoding="utf-8").read()
BG_REG = dict(re.findall(r'^image (bg_[a-z0-9_]+) = BB_IMG\("([a-z0-9_]+)\.jpg"',
                         imgs_src, re.M))
SPR_REG = dict(re.findall(r'^image (spr_[a-z0-9_]+) = BB_PLAIN\("([a-z0-9_]+)\.png"',
                          imgs_src, re.M))
# 下限防的是"注册表悄悄缩水到没有"。13 不是凑出来的：原著没有餐厅，也没有船库
# （晚餐就在大厅那张长桌上，终稿 119），那两张是凭空造的房间，第六轮删掉的。
check("注册了背景（%d 张）" % len(BG_REG), len(BG_REG) >= 13)
check("注册了立绘（%d 张）" % len(SPR_REG), len(SPR_REG) >= 9)

assets = io.open(os.path.join(HERE, "tools", "build_assets.py"), encoding="utf-8").read()
def _list(name):
    m = re.search(name + r" = \[(.*?)\]", assets, re.S)
    return re.findall(r'"([a-z0-9_]+)"', m.group(1)) if m else []

# 夜版那张表从管线 import，不在这里抄一份：抄的那份会在某次改参数之后过期，
# 然后这条闸就开始拿旧表验新图，验的还是"上次那张图长什么样"。
sys.path.insert(0, os.path.join(HERE, "tools"))
import build_assets as BA
NIGHT = BA.BG_NIGHT
WASHED = set(_list("BG_KEYS")) | set(NIGHT)

check("每张注册的背景都在洗图清单里（漏 %d 张）"
      % (len(set(BG_REG.values())) - len(set(BG_REG.values()) & WASHED)),
      set(BG_REG.values()) <= WASHED)
check("洗图清单里没有没注册的背景（多 %d 张）"
      % (len(WASHED) - len(set(BG_REG.values()))),
      WASHED <= set(BG_REG.values()))
check("每张注册的立绘都在洗图清单里",
      set(SPR_REG.values()) <= set(_list("SPR_KEYS")))

# 素材真在盘上：BB_IMG 缺图就换占位，不报错，所以只能自己问文件系统。
for key, fname in sorted(BG_REG.items()):
    check("盘上有 images/%s.jpg" % fname,
          os.path.exists(os.path.join(GAME, "images", fname + ".jpg")))
for key, fname in sorted(SPR_REG.items()):
    check("盘上有 images/%s.png" % fname,
          os.path.exists(os.path.join(GAME, "images", fname + ".png")))

# ---------------- 夜版底图 ----------------
# 夜版不另画一张原图，是从白天那张派生的。这条链有三处会静悄悄断：
#   表里换了源图 → 两张不是同一间房，玩家读到的是"他们挪去了另一间房"；
#   改了参数没重跑管线（或手改过图）→ 盘上那张和剧本指向的名字对不上；
#   参数跑偏 → 夜版比白天还亮，或者整片压成死黑。
# 前两条用"重算一遍、逐字节对上"管住（派生是纯函数，重算必须一模一样）；
# 第三条只能问像素。
def _lum(fname):
    from PIL import Image
    a = np.asarray(Image.open(os.path.join(GAME, "images", fname + ".jpg")).convert("RGB"),
                   dtype=np.float32)
    return a @ np.array([0.2126, 0.7152, 0.0722])


def _rebuild_night(key):
    """把这一张按管线重算到临时目录，回字节。换 DST 是因为 build_bg_night 读写都走它。"""
    import contextlib
    import shutil
    import tempfile
    tmp = tempfile.mkdtemp()
    shutil.copy(os.path.join(GAME, "images", NIGHT[key]["day"] + ".jpg"), tmp)
    old, BA.DST = BA.DST, tmp
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            ok = BA.build_bg_night(key)
    finally:
        BA.DST = old
    p = os.path.join(tmp, key + ".jpg")
    data = io.open(p, "rb").read() if ok and os.path.exists(p) else None
    shutil.rmtree(tmp, ignore_errors=True)
    return data


check("夜版表里的每一张都注册了（漏注册＝剧本引用未注册的那一片纯色）",
      set(NIGHT) <= set(BG_REG))
check("夜版都从洗好的白天底图派生（不许拿夜图再派生，也不许指一个没洗过的名）",
      all(c["day"] in set(_list("BG_KEYS")) and c["day"] in set(BG_REG.values())
          for c in NIGHT.values()),
      )
for key in sorted(NIGHT):
    cfg = NIGHT[key]
    shipped = io.open(os.path.join(GAME, "images", key + ".jpg"), "rb").read() \
        if os.path.exists(os.path.join(GAME, "images", key + ".jpg")) else None
    check("夜版和管线重算出来的一模一样（改过表没重跑、或者图被手改过）：%s" % key,
          shipped is not None and shipped == _rebuild_night(key))
    day_l, night_l = _lum(cfg["day"]), _lum(key)
    check("夜版比白天那张暗（%.0f → %.0f）：%s" % (day_l.mean(), night_l.mean(), key),
          night_l.mean() < day_l.mean() * 0.85)
    check("夜版没压成一片死黑（中位 %.1f、最亮一档 %.1f、反差 %.1f）：%s"
          % (np.percentile(night_l, 50), np.percentile(night_l, 95), night_l.std(), key),
          np.percentile(night_l, 50) >= 4.0 and np.percentile(night_l, 95) >= 30.0
          and night_l.std() >= 12.0)
# 图和字得对得上：夜版底图只能落在写着夜的那一段。
# 防的是"顺手给一间房配了夜版，而剧本里那一幕发生在下午"——玩家不会报这个错，
# 只会以为自己漏读了。窗口取上下各 12 行，但只算玩家看得见的两样：台词和章节卡。
# 整段扫不行——`$ round3 = Debate(..., head="第三夜 · 结算")` 这种代码里的"夜"
# 会把序章那一段白天也判成夜里，闸门就成了摆设。
NIGHT_WORD = re.compile(r"夜|傍晚|黄昏|台灯|凌晨|天黑|停电|熄")
ON_SCREEN = re.compile(r'^\s*(?:[A-Z]+ "|call screen bb_card\()')
for _p in sorted(glob.glob(os.path.join(GAME, "*.rpy"))):
    _ls = io.open(_p, encoding="utf-8").read().split("\n")
    for _i, _ln in enumerate(_ls):
        _m = re.match(r"\s*scene (bg_[a-z0-9_]+)\s*$", _ln)
        if not _m or _m.group(1) not in NIGHT:
            continue
        _near = "\n".join(l for l in _ls[max(0, _i - 12):_i + 13] if ON_SCREEN.match(l))
        check("夜版底图落在写着夜的段落里：%s（%s:%d）"
              % (_m.group(1), os.path.basename(_p), _i + 1), bool(NIGHT_WORD.search(_near)))

used = set()
for p in sorted(glob.glob(os.path.join(GAME, "*.rpy"))):
    if os.path.basename(p) in ("04_images.rpy", "00_settings.rpy"):
        continue          # 注册表自己、环境音表——都不算"这一屏用了它"
    used |= set(re.findall(r"\b(bg_[a-z0-9_]+|spr_[a-z0-9_]+)\b",
                           io.open(p, encoding="utf-8").read()))
dead = sorted(k for k in list(BG_REG) + list(SPR_REG)
              if k not in used and k not in {c["day"] for c in NIGHT.values()})
# 豁免只给"夜版的白天底图"，而且只有一张真的用得上：东翼那间房只在夜里进（第十三章
# 和第三夜那张卡），白天那张不上屏。它仍然必须注册、必须在盘上——vibe_images/ 不进 git，
# 洗好的白天 jpg 就是派生的唯一输入，删了它，别人从克隆里重跑管线拼不出那一夜。
check("注册的图全被引用（没人用的 %d 张）" % len(dead), not dead)
for k in dead:
    info("没人引用：" + k)
orphan = sorted(k for k in used if k not in BG_REG and k not in SPR_REG)
check("剧本里没有未注册的图（%d 个：写错名就是一片纯色）" % len(orphan), not orphan)
for k in orphan:
    info("未注册：" + k)

amb_src = io.open(os.path.join(GAME, "00_settings.rpy"), encoding="utf-8").read()
amb = dict(re.findall(r'"(bg_[a-z0-9_]+)":\s*"(amb_[a-z0-9_]+)"',
                      amb_src[amb_src.find("BB_AMB_BY_BG"):]))
noamb = sorted(k for k in BG_REG if k not in amb)
check("每张背景有环境音（漏 %d 张：钉它的那一章静音）" % len(noamb), not noamb)
for k in noamb:
    info("没有环境音：" + k)
check("环境音表里没有多余的名（%d 个）"
      % (len(amb) - len(set(amb) & set(BG_REG))), set(amb) <= set(BG_REG))
# 音乐床和环境音同一条命：查表漏一个名，那一章就只有浪没有琴，谁也不报。
mus = dict(re.findall(r'"(bg_[a-z0-9_]+)":\s*"(mus_[a-z0-9_]+)"',
                      amb_src[amb_src.find("BB_MUS_BY_BG"):]))
nomus = sorted(k for k in BG_REG if k not in mus)
check("每张背景有音乐床（漏 %d 张：钉它的那一章没有配乐）" % len(nomus), not nomus)
for k in nomus:
    info("没有音乐床：" + k)
check("音乐床表里没有多余的名（%d 个）"
      % (len(mus) - len(set(mus) & set(BG_REG))), set(mus) <= set(BG_REG))
# 表里点到的每一条，盘上得真有其文件——查表命中、文件缺失，renpy.music.play 只
# 会在运行时抛，而自动播放那趟根本不检查声道响没响。
for _name, _tbl in (("BB_AMB_FILE", amb), ("BB_MUS_FILE", mus)):
    _files = dict(re.findall(r'"([a-z_0-9]+)":\s*"(audio/[a-z_0-9]+\.wav)"',
                             amb_src[amb_src.find(_name):]))
    for _k in set(_tbl.values()):
        check("%s 点到的那条在盘上：%s" % (_name, _k),
              _k in _files and os.path.exists(os.path.join(GAME, _files[_k])))
# 情绪档：章节卡上写 mood="night"，表里查不到就是静悄悄回落到地点表——那一章
# 听起来跟别的夜里一模一样，谁也不报。两头都查：卡上不许有表里没有的名，
# 表里不许有卡上从没用过的名（白合成一床，还骗人说有七档）。
mood_tbl = dict((k, (a, u)) for k, a, u in re.findall(
    r'"([a-z]+)":\s*\("(amb_[a-z0-9_]+)",\s*"(mus_[a-z0-9_]+)"\)',
    amb_src[amb_src.find("BB_MOOD"):amb_src.find("renpy.music.register_channel")]))
used_mood = set(re.findall(r'(?:mood="|bb_mood\(")([a-z_]+)"',
                           "".join(io.open(p, encoding="utf-8").read()
                                   for p in glob.glob(os.path.join(GAME, "*.rpy")))))
unknown = sorted(used_mood - set(mood_tbl))
check("卡上和剧本里点的每一档在表里（写错一档：%d 处，它会静悄悄回落到地点表）"
      % len(unknown), not unknown)
for k in unknown:
    info("表里没有这一档：" + k)
dead = sorted(set(mood_tbl) - used_mood)
check("表里每一档都有卡在用（没人用的：%d 档）" % len(dead), not dead)
for k in dead:
    info("没有章节卡用这一档：" + k)
amb_files = dict(re.findall(r'"(amb_[a-z0-9_]+)":\s*"(audio/[a-z0-9_]+\.wav)"', amb_src))
mus_files = dict(re.findall(r'"(mus_[a-z0-9_]+)":\s*"(audio/[a-z0-9_]+\.wav)"', amb_src))
for _m, (_a, _u) in sorted(mood_tbl.items()):
    check("情绪档 %s 点到的环境音在盘上：%s" % (_m, _a),
          _a in amb_files and os.path.exists(os.path.join(GAME, amb_files[_a])))
    check("情绪档 %s 点到的音乐床在盘上：%s" % (_m, _u),
          _u in mus_files and os.path.exists(os.path.join(GAME, mus_files[_u])))
# 盘上躺着、但没有任何表指向的循环：白占发行包（一条两三兆），而且它多半是
# 改名改了一半——表里换了名、旧文件还留在原地。
_pointed = (set(amb.values()) | set(mus.values())
            | {a for a, _ in mood_tbl.values()} | {u for _, u in mood_tbl.values()})
_on_disk = {os.path.splitext(f)[0] for f in os.listdir(os.path.join(GAME, "audio"))
            if f.startswith(("amb_", "mus_")) and f.endswith(".wav")}
_unused = sorted(_on_disk - _pointed)
check("盘上每一条循环都有表指向它（没人用的 %d 条）" % len(_unused), not _unused)
for k in _unused:
    info("没有表指向这条 wav：" + k)
_missing = sorted(_pointed - _on_disk)
check("表里点到的每一条都在盘上（缺 %d 条）" % len(_missing), not _missing)
for k in _missing:
    info("表里点了但盘上没有：" + k)
# 章节卡钉的翻拍：文件名写错，BB_SNAP 判缺图就不钉——卡片少一张照片，谁也不说。
_all_rpy = "".join(io.open(p, encoding="utf-8").read()
                   for p in glob.glob(os.path.join(GAME, "*.rpy")))
for snap in sorted(set(re.findall(r'BB_SNAP\("([a-z0-9_]+)\.jpg"\)', _all_rpy))):
    check("卡片翻拍在盘上：%s.jpg" % snap,
          os.path.exists(os.path.join(GAME, "images", snap + ".jpg")))

# 落屏凭据：截图脚本会把每张注册背景单独拍一张（30_bg_*.png）。
# 上面那一条只证明 jpg 在盘上；BB_IMG 里那条 loadable 判定、纱和颗粒的合成次序，
# 都要引擎跑一遍才算数——缺图是静默退化，不报错，只是那一屏变成纯色。
_plates = glob.glob(os.path.join(HERE, "shots", "30_bg_*.png"))
if not _plates:
    check("有 shots/30_bg_*.png（每张背景的落屏凭据，重跑截图脚本）", False)
else:
    on_screen = set(os.path.basename(p)[3:-4] for p in _plates)
    noshot = sorted(set(BG_REG) - on_screen)
    check("每张注册背景都真的落了屏（缺 %d 张）" % len(noshot), not noshot)
    for k in noshot:
        info("没落屏：" + k)
    stale_shot = sorted(on_screen - set(BG_REG))
    check("落屏图里没有没注册的名（%d 张）" % len(stale_shot), not stale_shot)
    for k in stale_shot:
        info("多出来：" + k)

# 证据图标：EV_ICON 的值就是文件名，写错一个，图鉴开到那一条就当场异常。
_screens = io.open(os.path.join(GAME, "02_screens.rpy"), encoding="utf-8").read()
_ev_icon = dict(re.findall(r'^\s*"([a-z0-9_]+)":\s*"([a-z_]+)",',
                           _screens[_screens.find("EV_ICON = {"):
                                    _screens.find("EV_ICON = {") + 2000], re.M))
check("证据图标表非空（%d 条）" % len(_ev_icon), len(_ev_icon) >= 20)
_ui = os.path.join(GAME, "images", "ui")
noic = sorted(v for v in set(_ev_icon.values())
              if not os.path.exists(os.path.join(_ui, "ic_%s.png" % v)))
check("每一条证据的图标都在盘上（缺 %d 种）" % len(noic), not noic)
for v in noic:
    info("缺图标：ic_%s.png" % v)

# ---------------- 并排：两件之间（终章那张桌） ----------------
# 这一屏是第十轮新加的，它的规矩跟对质那几屏相反：不打分。所以闸也朝反方向咬——
# 不许发证据、不许记数、不许出现裁决词，中间那一行只能从 PAIRS 来。
# 逐字那一道在 check_verbatim 的 each_pair（整段必须在正文里连着出现），
# 这里管的是"这一屏不可能被赢"。
PAIRS = g.get("PAIRS") or {}
pair_line = g["pair_line"]
check("并排表非空（%d 对）" % len(PAIRS), len(PAIRS) >= 8)
bad_pair_id = sorted(i for k in PAIRS for i in k if i not in EVIDENCE)
check("并排的每一条都在证据表里（写错一个名，那一对就永远摆不出来：%d 条）"
      % len(bad_pair_id), not bad_pair_id)
for i in bad_pair_id:
    info("表里没有：" + i)

# 摆上桌的两件，必须在叫起这张桌之前就已经到手。第十轮之后若有人拿尾声里才
# 翻出来的那一条去配对，屏上会画一张玩家永远凑不齐的对。
# 日序只能算到天，天里还得比行号——第六日的桌排在第二十四章，而唯一一条
# 同日到手的信封出自第二十三章，只看"第六日"是放过的。
_d6 = io.open(os.path.join(GAME, "11_day6.rpy"), encoding="utf-8").read()
_desk_at = _d6.find("call bb_pair_desk")
check("终章那张桌真的被 ch24 叫起（找不到 call＝挂了个没人调的屏）", _desk_at > 0)
# 这里的 GIVE 是被窄化过的那一条（只认 `$ ev_give("…")`），拿去比偏移会把
# python: 块里的到手看成"没在这天到手过"，偏移那道判据就悄悄放行。
_first_give = {}
for _m in re.finditer(r"ev_give\(\s*[\"']([a-z0-9_]+)[\"']\s*\)", _d6):
    _first_give.setdefault(_m.group(1), _m.start())
# 第六日目前只有一个脚本文件，所以偏移可以只在 11_day6 里比；多了第二个，
# 这条判据就得改成跨文件排序——先把它钉成闸，别让它悄悄失真。
_d6files = sorted(f for f, d in FILE_DAY.items() if d == 6)
check("第六日只有一个脚本文件（%s）" % "／".join(_d6files), _d6files == ["11_day6.rpy"])
late_pair = []
for k in PAIRS:
    for eid in k:
        if eid not in sites:
            late_pair.append(eid + " 没有来处")
        elif sites[eid] > 6:
            late_pair.append(eid + " 到手晚于第六日")
        elif sites[eid] == 6 and _first_give.get(eid, 0) >= _desk_at:
            late_pair.append(eid + " 在这张桌叫起之后才到手")
check("每一对的两件，摆桌之前都已到手（迟 %d 处）" % len(late_pair), not late_pair)
for x in sorted(set(late_pair)):
    info(x)

# 中间那一行只能来自数据层。屏上的**字符串字面量**里出现句号＝有人把正文
# 写进了界面——那种句子 LINE_RE 看不见，正是上一轮堵掉的那道后门。
# 只剥注释和 docstring：那是写给维护者的话，玩家看不到，拿它咬人是误报。
_flow = io.open(os.path.join(GAME, "03_flow.rpy"), encoding="utf-8").read()
_s0, _s1 = _screens.find("screen bb_pair("), _screens.find("screen bb_result(")
_pair_body = _screens[_s0:_s1]


def screen_lits(body):
    body = re.sub(r'""".*?"""', "", body, flags=re.S)
    body = "\n".join(l for l in body.split("\n") if not l.strip().startswith("#"))
    return [m.group(1) for m in re.finditer(r'"((?:[^"\\]|\\.)+)"', body)
            if m.group(1).strip()]


_pstrings = screen_lits(_pair_body)
check("并排屏真的在画界面（切到的字面量 %d 个，太少＝切片切歪，闸在空转）"
      % len(_pstrings), len(_pstrings) >= 10)
dots = [s for s in _pstrings if u"。" in s]
check("并排屏上没有整句正文（带句号的字面量 %d 个）" % len(dots), not dots)
for s in dots:
    info("这句该回数据层：" + s[:40])
check("并排屏只画 pair_line() 交来的那一行（弯引号包着的变量，不是屏上攒的句子）",
      re.search(r'text\s+"“"\s*\+\s*line\s*\+\s+"”"', _pair_body) is not None
      and "pair_line(" in _flow)
# 自动播放必须自己走得出这一屏：少了那一句 timer，六日回归会挂死在桌上。
check("并排屏给自动播放留了出口（bb_auto＋timer＋两件都点得出来）",
      "if store.bb_auto" in _pair_body and "timer 0.05 action Return(" in _pair_body
      and "BB_AUTO_PAIR" in _pair_body)
# 攒 sel 的那一层和画界面的一层一样不能碰成绩：只查屏体，往 label 里塞一句
# ev_give 就能绕过整道闸。
_l0 = _flow.find("label bb_pair_desk")
_pair_flow = _flow[_l0:_flow.find("\n# ----------------", _l0)]
check("并排那一层真的被切进来了（截到的 label 太短＝切片切歪）", len(_pair_flow) > 200)
smuggle = [w for w in ("ev_give", "have.add", "bb_silence", ".silence", "bullets",
                       "persistent", "bb_silence_won", "renpy.save")
           if w in _pair_body or w in _pair_flow]
check("并排屏和它那一层不发证据、不动沉默数、不写存档（违 %d 处）" % len(smuggle), not smuggle)
for w in smuggle:
    info("这一屏不该碰：" + w)
# 裁决词：这一屏不给答案，所以连判输赢的词都不许出现在玩家看到的那几行里。
JUDGE = ("答对", "答错", "正确", "错误", "赢了", "输了", "得分", "分数",
         "通过", "失败", "真相大白", "破案", "指认")
_said_lit = set(_pstrings) | set(screen_lits(_pair_flow))
said = [w for w in JUDGE if w in _said_lit or any(w in v for v in PAIRS.values())]
check("并排表和并排屏里没有裁决词（出现 %d 个）" % len(said), not said)
for w in said:
    info("裁决词：" + w)

# 行为：没写过的就是空；同一件不叫并排；写过的那一对真的有话。
check("正文没并排写过的一对，中间是空", pair_line("invite", "lock") == "")
check("同一件证据摆不成并排", pair_line("seal_rec", "seal_rec") == "")
check("空槽位不吐句子", pair_line(None, "seal_rec") == "" and pair_line("seal_rec", "") == "")
check("第二十三章那一并排真的有句子", bool(pair_line("seal_rec", "face_photo")))
check("并排是双向的（摆的顺序不能影响结果）",
      pair_line("face_photo", "seal_rec") == pair_line("seal_rec", "face_photo"))
# 咬合：把一条并排句换成界面上随手写的话，上面那道句号闸必须 FAIL——
# 不在这里改文件，只验"闸认得屏体"这件事：截到的屏体必须真的含两张便签的代码。
check("并排屏真的画了两张便签（截空了＝切片切错，闸在空转）",
      "EVIDENCE[_id].brief" in _pair_body and _pair_body.count("xsize 640") >= 2)

# ---------------- 立绘几何与说话人 ----------------
# 玩家的眼睛报了两件事："人有点宽"、"换个人说话人跳一截"。都能量，量不开好坏
# 的不配当闸：
#   头宽不齐——九张生成图人头本来就差到 1.3 倍。第五轮那道锚点收的是肩线，
#     带立领和披发的那几张上它从 33% 飘到 58%，等于没定标。
#   头顶不齐——只定头宽不够：生成图从头顶往下截到的位置本来就不一样（实测身长
#     614 对 929），底边一对齐，头顶就从第 137 行飘到第 452 行——换个人说两句，
#     人在屏幕上跳一小截。
#   画布过宽——900×1080 那一版人最宽那张只占 59%，两侧各空 170px 透明；台词页
#     把画布顶到屏幕边，玩家看到的就是"人又小又飘，框还特别宽"。
# 横向拉宽这条管线出不了：build_sprite 只算一个缩放数 s，x 和 y 同乘它
# （tools/build_assets.py 的 build_sprite），PIL 收到的是同一个比例。源图在
# vibe_images/ 且不进 git，夜版底图那种"重算一遍逐字节对上"在这儿走不通，
# 所以下面查的是盘上这张图的状态，不是管线的过程。
from PIL import Image

CW, CH = BA.SPR_CANVAS
SPR_FOR = g["SPR_FOR"]   # 从数据层那份读，不在这里抄一张
# 带宽是量出来的，不是拍的：九张实测头宽 215～228（定标 230，最差的方廷 93.5%）、
# 头顶第 59～65 行（定标 60）、剪影高占画布高 0.884～0.891、
# 最宽那张（赵寒）占画布宽 0.868。旧版拿这三个带宽一一验过，九张里七张出界。
HEAD_TOL, CROWN_TOL = 0.08, 6


def _silh(png):
    im = Image.open(png)
    a = np.asarray(im.convert("RGBA").split()[-1], dtype=np.uint8)
    m = a > 40
    rows = np.nonzero(m.sum(axis=1))[0]
    cols = np.nonzero(m.sum(axis=0))[0]
    cy, hw, _cx = BA.measure_head(a)
    return (im.size, int(cols[-1]) - int(cols[0]) + 1,
            int(rows[-1]) - int(rows[0]) + 1, float(hw), int(cy))


_sil = dict((k, _silh(os.path.join(GAME, "images", k + ".png"))) for k in BA.SPR_KEYS)
check("立绘画布就是管线钉的那一格（%d×%d）" % (CW, CH),
      all(v[0] == (CW, CH) for v in _sil.values()))
_w = sorted((v[3] / BA.SPR_HEAD_W, k) for k, v in _sil.items())
check("九张头宽对得上定标（实测 %.0f%%～%.0f%%，容 ±%.0f%%）"
      % (100 * _w[0][0], 100 * _w[-1][0], 100 * HEAD_TOL),
      _w[0][0] >= 1 - HEAD_TOL and _w[-1][0] <= 1 + HEAD_TOL)
_c = sorted(v[4] for v in _sil.values())
check("九张头顶在同一行（实测第 %d～%d 行，定标 %d±%d）"
      % (_c[0], _c[-1], BA.SPR_CROWN_Y, CROWN_TOL),
      _c[0] >= BA.SPR_CROWN_Y - CROWN_TOL and _c[-1] <= BA.SPR_CROWN_Y + CROWN_TOL)
# 分母用每张图自己的画布，不用 SPR_CANVAS 那个常数：拿常数去量，把画布改宽回
# 900 那一版，比值一动不动（625/720 还是 0.868），闸就成了一张贴在墙上的尺子。
_fillh = sorted(v[2] / float(v[0][1]) for v in _sil.values())
check("身子把画布接满（实测 %.3f～%.3f）" % (_fillh[0], _fillh[-1]),
      _fillh[0] >= 0.85 and _fillh[-1] <= 0.92)
_widest = max(v[1] / float(v[0][0]) for v in _sil.values())
check("画布不宽过人（最宽那张只占 %.3f，旧版 900 宽时是 0.59）" % _widest, _widest >= 0.75)
# 头像那一格不许被压扁：对质页的名牌位是 xysize 硬塞的，格子和图片比例不一致
# 就是横向变形——玩家说的"有点宽"如果是真的，就在这儿。
_chip = re.search(r"bb_face\([^\n]*?\):\s*\n\s*xysize \((\d+),\s*(\d+)\)",
                  io.open(os.path.join(GAME, "02_screens.rpy"), encoding="utf-8").read())
check("头像切出来就是名牌位那一格（%d×%d）" % BA.SPR_FACE,
      all(Image.open(os.path.join(GAME, "images", "faces", k[4:] + "_face.png")).size
          == BA.SPR_FACE for k in BA.SPR_KEYS))
_chip_skew = -1.0 if _chip is None else abs(
    int(_chip.group(1)) / float(int(_chip.group(2))) /
    (BA.SPR_FACE[0] / float(BA.SPR_FACE[1])) - 1) * 100
check("头像格和对质页的 xysize 同比例（差 %.2f%%，超 1%% 就是拿名牌位横向压扁）"
      % _chip_skew, _chip is not None and _chip_skew <= 1.0)

# 说话人上台只有一条路：角色自己那句 bb_stage。剧本里再手写 show 就等于两个人
# 抢一个台——手写那条只在这个人第一次开口时写，下一句换了人，台上还站着上一个。
# 连 `as talker` 一起禁：现在标签就是人名，多挂一个 talker 槽不会被 bb_stage 摘掉，
# 症状变成两张脸并排站着。
_hand = []
for _p in sorted(glob.glob(os.path.join(GAME, "*.rpy"))):
    if os.path.basename(_p).startswith("99_"):
        continue          # 截图台架不走 Character（直接 show screen say），得手写
    for _i, _ln in enumerate(io.open(_p, encoding="utf-8").read().split("\n"), 1):
        if re.match(r"\s*show\s+spr_[a-z0-9_]+\b", _ln):
            _hand.append("%s:%d" % (os.path.basename(_p), _i))
check("剧本里不联手写台上那位（剩 %d 处：%s）" % (len(_hand), ",".join(_hand[:3])),
      not _hand)
# 每个 BBChar 都得有脸，没脸的（黑鸟）要在这里点名——新增一个说话人而忘了立绘，
# 症状是"他说话时台上站着别人"，玩家不会报，只会以为自己看错了。
_set_src = io.open(os.path.join(GAME, "00_settings.rpy"), encoding="utf-8").read()
_speakers = set(re.findall(r'BBChar\("([^"]+)"', _set_src))
_noart = sorted(_speakers - set(SPR_FOR))
check("开口的每一个人都在名字→立绘表里（漏 %d 个：%s）"
      % (len(_noart), ",".join(_noart)), _noart == ["黑鸟"])
check("名字→立绘表里没有一个查无此人（多 %d 个）"
      % len(set(SPR_FOR) - _speakers), set(SPR_FOR) <= _speakers)
check("表里点的每张脸都注册了（漏 %d 张）"
      % len(set(SPR_FOR.values()) - set(SPR_REG.values())),
      set(SPR_FOR.values()) <= set(SPR_REG.values()))
check("旁白挂陈默的脸（bb_stage 里 who=None 走 spr_me）",
      '"spr_me" if who is None' in _set_src)

# 台上到底站着谁，还得运行时量一次：静态只能证明"剧本里没手写 show"，证不了
# bb_stage 真的跑、真的换脸。keytest 每一趟都从引擎的 master 层读回 stage，
# 期望值不在这里另立一张表——从 99_shots.rpy 里那一趟后面紧跟的那句 say 现算，
# 再顺着 define … = BBChar("名字") 和 SPR_FOR 落到立绘名。多立一张表，
# 表改了剧本没改，闸还是绿的。
_who_of = {}
for _m in re.finditer(r'define (\w+) = BBChar\((None|"[^"]*")', _set_src):
    _who_of[_m.group(1)] = None if _m.group(2) == "None" else _m.group(2).strip('"')
_want = {}
_cur = None
for _ln in io.open(os.path.join(GAME, "99_shots.rpy"), encoding="utf-8").read().split("\n"):
    _m = re.search(r'_kt_phase\("([^"]+)"\)', _ln)
    if _m:
        _cur = _m.group(1)
        continue
    _s = re.match(r'\s*([A-Z][A-Z_]*)\s+"', _ln)
    if _cur is not None and _s:
        _want[_cur] = _s.group(1)
        _cur = None
check("台架里每一趟都说了一句能查说话人的话（查到 %d／%d 趟）"
      % (len(_want), len(KT_PHASES)), len(_want) >= 4)
if not _kt:
    check("台上站着谁没法查（没有 shots/_keytest.json，先跑 BB_KEYTEST=1）", False)
else:
    for _p in KT_PHASES:
        _got = (_kt.get(_p) or {}).get("stage")
        _w = _want.get(_p)
        if _w is None:      # 扉页／结算／热点那几趟没有 say，只查"台上还有一张脸"
            check("%s 台上仍站着一张注册过的脸（stage=%s）" % (_p, _got),
                  _got in list(SPR_FOR.values()) + ["spr_me"])
        else:
            check("%s 那一句把 %s（%s）摆上台（stage=%s）"
                  % (_p, _w, _who_of.get(_w) or "旁白＝陈默", _got),
                  _got == SPR_FOR.get(_who_of.get(_w), "spr_me"))

print("")
if fails:
    print("FAILED: %d" % len(fails))
    sys.exit(1)
print("all good")