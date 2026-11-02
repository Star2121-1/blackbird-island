# -*- coding: utf-8 -*-
"""内容完整性与公平性自检：不启 Ren'Py，跨文件静态扫一遍全本。

test_logic.py 验的是"一条发言链算得对不对"，这里验的是"整本摊开能不能走通"：

- 证据表里每一条都要有地方拿得到（图鉴写着 33 条，拿不满就是骗人）。
- 每一轮的破绽句，所用证据必须在那一夜之前就已经可拿到（拿不到就打不破，是坑玩家）。
- 热点表里的每个 id 都要有对应的 spot_ 标签；定义了没人调的 spot_ 标签是死内容。
- 五轮的沉默总数、句数、破绽数打出来，README 里那些数字要对着它。

    python blackbird-vn/tools/test_content.py
"""
import glob
import io
import os
import re
import sys
import types

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

for p in sorted(glob.glob(os.path.join(GAME, "*.rpy"))):
    fname = os.path.basename(p)
    if fname.startswith(("00_", "02_", "04_", "99_")):
        continue          # 样式／界面／图像注册／截图自检：不取证
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
info("五轮合计：%s 句 / 破绽 %s 处" % (
    "、".join(str(len(r)) for _, r in ROUNDS),
    "、".join(str(len([s for s in r if s.weak_to and s.hit_kind == "silence"]))
              for _, r in ROUNDS)))
check("全六日沉默总数 %d 处（>0 且每夜至少 2 处）" % total,
      total > 0 and all(len([s for s in r if s.weak_to and s.hit_kind == "silence"]) >= 2
                        for _, r in ROUNDS))
check("每条破绽句的 hit／miss 文案齐（由 test_logic 细验，这里只查总数）",
      all(s.hit and s.miss for _, rows in ROUNDS for s in rows if s.weak_to))


# ---------------- 4) 两套日历 ----------------
# 菜单里的"日期"读 bb_day，而只有扉页会写它。岛上的日子（十一月十七日起）和
# 顾言笙写笔记的日子（二〇二五年十一月四日起）是两套日历，一夜之间来回切。
# 扉页刚把日期盖成岛上的十一月十八日，下一段笔记念的却是十一月六日——
# 少了重盖的那一行，玩家看到的就是一个记错日子的本子。
HANGZHOU = "scene bg_hangzhou"
NOTE_DATE = re.compile(r'^\s*N "[^"]*十一月([一二三四五六七八九十]+)日')
STAMP = re.compile(r'\$ bb_day = "二〇二五年十一月([一二三四五六七八九十]+)日"')

hangzhou = 0
no_stamp = []
for p in sorted(glob.glob(os.path.join(GAME, "*.rpy"))):
    fname = os.path.basename(p)
    if fname.startswith(("00_", "01_", "02_", "04_", "13_", "14_", "99_")):
        continue
    lines = io.open(p, encoding="utf-8").read().split("\n")
    for i, line in enumerate(lines):
        if HANGZHOU not in line:
            continue
        hangzhou += 1
        narr = next((m.group(1) for j in range(i, min(len(lines), i + 5))
                     for m in [NOTE_DATE.match(lines[j])] if m), None)
        if narr is None:
            continue            # 这段没报日子（岛上人插进来的一句笔记），不比
        got = next((m.group(1) for j in range(max(0, i - 3), min(len(lines), i + 4))
                    for m in [STAMP.search(lines[j])] if m), None)
        if got != narr:
            no_stamp.append("%s:%d 笔记念十一月%s日，HUD 盖的是%s"
                            % (fname, i + 1, narr,
                               "十一月" + got + "日" if got else "岛上那天"))

check("每段报了日期的杭州笔记都重盖了 HUD 日期（杭州景 %d 处，漏 %d 段）"
      % (hangzhou, len(no_stamp)), not no_stamp)
for b in no_stamp:
    info(b)

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

print("")
if fails:
    print("FAILED: %d" % len(fails))
    sys.exit(1)
print("all good")
