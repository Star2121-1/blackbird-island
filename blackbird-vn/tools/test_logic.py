# -*- coding: utf-8 -*-
"""把 01_data.rpy 的 init -1 python 块抽出来，用纯 Python 跑一遍逻辑。
屏幕和交互要靠 Ren'Py 才能验，这里只验数据层：证据、发言链、沉默计数、拼字。"""
import io
import os
import re
import sys
import types

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "game", "01_data.rpy")

src = io.open(DATA, encoding="utf-8").read()
m = re.search(r"^init -1 python:\n((?:(?:    .*)?\n)*)", src, re.M)
body = "\n".join(l[4:] if l.startswith("    ") else l
                 for l in m.group(1).split("\n"))

fake = types.ModuleType("renpy")
fake.notify = lambda *a, **k: None
fake.store = None
sys.modules.setdefault("renpy", fake)

g = {"renpy": fake}
exec(compile(body, DATA, "exec"), g)

fails = []


def check(name, cond):
    if not cond:
        fails.append(name)
    print(("PASS " if cond else "FAIL ") + name)


ev_give = g["ev_give"]
EVIDENCE = g["EVIDENCE"]
ROUND1 = g["ROUND1"]
SEATS = g["SEATS"]
Debate = g["Debate"]
HANGMAN = g["HANGMAN"]

check("证据表每条都有名字和正文",
      all(e.name and e.brief and e.chapter for e in EVIDENCE.values()))
check("座位 8 个 = 7 受邀 + 沈南舟", len(SEATS) == 8 and SEATS[0] == "沈南舟")

d = Debate(SEATS, ROUND1)
check("本轮沉默上限 2", d.silence_total == 2)
check("反驳机会 3", d.bullets == 3)

# 1) 没举证据就反驳
d.rebut()
check("空手反驳不掉血", d.bullets == 3 and d.message)

# 2) 举错证据
ev_give("lock")
d.select("lock")
d.rebut()
check("举错证据掉一次机会", d.bullets == 2 and d.silence == 0)

# 3) 听完林晚那一句才拿到死亡时间
while d.i != 2:
    d.advance()
d.hear_current()
check("听到林晚那句才拿到两版死亡时间", "time_window" in g["have"])

# 4) 回到王剑那一句，用死亡时间打破
d.jump_to("王剑")
check("点座位能回到未破的那一句", d.i == 1)
d.select("time_window")
d.rebut()
check("王剑沉默", d.silence == 1 and d.seat_state("王剑") == "broken")
check("打破不扣反驳机会", d.bullets == 2)
d.select("time_window")
d.rebut()
check("同一句不能重复打破，也不白扣机会", d.silence == 1 and d.bullets == 2)

# 5) 方廷
while d.i != 3:
    d.advance()
ev_give("diary_fang")
d.select("diary_fang")
d.rebut()
check("方廷沉默", d.silence == 2 and d.silence_total == d.silence)

# 6) 沈南舟是反问，不算赢
while d.i != 6:
    d.advance()
ev_give("invite")
d.select("invite")
d.rebut()
check("主人反问不计入沉默", d.silence == 2 and d.counters == 1)
check("反问换来一条新证据", "phrase" in g["have"])
check("沈南舟座位标成 countered", d.seat_state("沈南舟") == "countered")

# 7) 循环听第二遍
d.advance()
check("听完一轮回到第一句", d.i == 0 and d.passes == 1)

# 8) 打完机会进结算
while d.bullets > 0 and not d.done:
    ev_give("roster")
    d.select("roster")
    d.rebut()
check("反驳机会用尽即结算", d.done)
lines = d.result_lines()
check("结算文案有内容", len(lines) >= 3)
check("结算不点名", not any("凶手" in l for l in lines))

# 9) 拼字：任何组合都拿不到名字
check("拼字候选 12 个", len(HANGMAN["candidates"]) == 12)
check("拼字是锁死的", HANGMAN["locked"] is True)

# 10) 每条 breakable 发言的证据，切片里都拿得到
need = {s.weak_to for s in ROUND1 if s.weak_to}
check("破绽所需证据都在证据表里", need <= set(EVIDENCE))

# 11) 后四夜的发言表：证据引用得存在，沉默数不得超过反驳机会
def load_init(fname):
    """把某个 .rpy 的 init python 块抽出来，接进同一个命名空间。"""
    p = os.path.join(HERE, "game", fname)
    s = io.open(p, encoding="utf-8").read()
    m = re.search(r"^init (?:-1 )?python:\n((?:(?:    .*)?\n)*)", s, re.M)
    body = "\n".join(l[4:] if l.startswith("    ") else l
                     for l in m.group(1).split("\n"))
    exec(compile(body, p, "exec"), g)


for f in ("13_rounds_ab.rpy", "14_rounds_cd.rpy"):
    load_init(f)

ROUNDS = [("第二轮", g["ROUND2"], 4), ("第三轮", g["ROUND3"], 4),
          ("第四轮", g["ROUND4"], 4), ("第五轮", g["ROUND5"], 4)]

for nm, rows, bullets in ROUNDS:
    ref = set()
    for s in rows:
        ref |= set([s.weak_to] if s.weak_to else [])
        ref |= set(s.hears or [])
        ref |= set(s.grants or [])
    check(nm + "引用的证据都在证据表里", ref <= set(EVIDENCE))
    sil = len([s for s in rows if s.weak_to and s.hit_kind == "silence"])
    check(nm + "沉默数 " + str(sil) + " 不超过反驳机会", 0 < sil <= bullets)
    check(nm + "每句都有落空时的话", all(s.miss for s in rows))
    check(nm + "主人不被写成沉默",
          not [s for s in rows if s.speaker == "沈南舟" and s.weak_to
               and s.hit_kind == "silence"])
    check(nm + "破绽句都配了打破后的话",
          all(s.hit for s in rows if s.weak_to and s.hit_kind))

print("")
if fails:
    print("FAILED: %d" % len(fails))
    sys.exit(1)
print("all good")
