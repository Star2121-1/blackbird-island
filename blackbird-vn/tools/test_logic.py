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
# 数据层里的 default 变量（have 就是）在 init 块外面，抽出 body 时带不到，
# 但 ev_give 要用它。引擎的顺序是 init 先、default 在上下文开始时求值，这里照抄。
defaults = re.findall(r"^default\s+(\w+)\s*=\s*(.+?)\s*$", src, re.M)

fake = types.ModuleType("renpy")
fake.notify = lambda *a, **k: None
fake.store = None
# 数据层里那几个发声的调用（获得证据、抵中一句）在这里必须是哑的：
# 静态自检没有音频设备，也不该因为"响了"而失败。
fake.sound = types.SimpleNamespace(play=lambda *a, **k: None)
fake.music = types.SimpleNamespace(play=lambda *a, **k: None,
                                   get_playing=lambda *a, **k: None,
                                   register_channel=lambda *a, **k: None)
sys.modules.setdefault("renpy", fake)

_noop = lambda *a, **k: None
g = {"renpy": fake, "bb_sfx": _noop,
     # 同上：hear_current 现在会顺手起一条人声，静态自检里它必须是哑的。
     # 接线对不对不在这里查，在 test_content 的人声那一节（有引擎探针）。
     "bb_voice_line": _noop, "bb_voice_stop": _noop}
exec(compile(body, DATA, "exec"), g)
for _n, _e in defaults:
    g[_n] = eval(_e, g)

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

# ---------------- 回合参数从 03_flow 读，不在这里抄一份 ----------------
# 反驳机会是剧本里 $ roundN = Debate(...) 那几行的实参。早先在自检里写死 3/4，
# 剧本把 bullets 改成 5，自检照样绿——而"沉默数不得超过反驳机会"这条
# 公平性判据守的其实是剧本里那个数。所以解析出来用。
FLOW = os.path.join(HERE, "game", "03_flow.rpy")
flow_src = io.open(FLOW, encoding="utf-8").read()
# 不写 bullets= 时用的是 Debate 形参上的默认值，这里也照那个值判，别写死 3。
DEF_BULLETS = Debate.__init__.__defaults__[0]
DEBATE_CALL = re.compile(r"^\s*\$\s+(round\d)\s*=\s*Debate\(([^)]*)\)", re.M)
round_cfg = {}
for _name, _args in DEBATE_CALL.findall(flow_src):
    _pos = [a.strip() for a in _args.split(",") if "=" not in a]
    _kw = dict(re.findall(r"(\w+)=([^,]+)", _args))
    round_cfg[_name] = {"stmts": _pos[1] if len(_pos) > 1 else None,
                        "bullets": int(_kw["bullets"]) if "bullets" in _kw
                        else DEF_BULLETS}

check("03_flow 里五轮都建了 Debate（抓到 %d 个）" % len(round_cfg),
      set(round_cfg) == {"round1", "round2", "round3", "round4", "round5"})
check("03_flow 的每轮都传了一个发言表常量进去",
      all(re.match(r"^ROUND\d$", v["stmts"] or "") for v in round_cfg.values()))

check("证据表每条都有名字和正文",
      all(e.name and e.brief and e.chapter for e in EVIDENCE.values()))
check("座位 8 个 = 7 受邀 + 沈南舟", len(SEATS) == 8 and SEATS[0] == "沈南舟")

r1_bullets = round_cfg.get("round1", {}).get("bullets") or DEF_BULLETS
d = Debate(SEATS, ROUND1, bullets=r1_bullets)
check("本轮沉默上限 = 发言表里的沉默句数",
      d.silence_total == len([s for s in ROUND1
                              if s.weak_to and s.hit_kind == "silence"]))
check("反驳机会与 03_flow 一致（%d）" % r1_bullets, d.bullets == r1_bullets)

# 1) 没举证据就反驳
d.rebut()
check("空手反驳不掉血", d.bullets == r1_bullets and d.message)

# 2) 举错证据
ev_give("lock")
d.select("lock")
d.rebut()
check("举错证据掉一次机会", d.bullets == r1_bullets - 1 and d.silence == 0)

# 3) 听完林晚那一句才拿到死亡时间
# 定位一律按内容找，不按序号写死：往发言表中间插一句（第一轮就这么加过林晚的
# 尸斑那句），序号版本会静默地测到别人身上去。
while ROUND1[d.i].speaker != "林晚":
    d.advance()
d.hear_current()
check("听到林晚那句才拿到两版死亡时间", "time_window" in g["have"])

# 4) 回到王剑那一句，用死亡时间打破
d.jump_to("王剑")
check("点座位能回到未破的那一句", d.i == 1)
d.select("time_window")
d.rebut()
check("王剑沉默", d.silence == 1 and d.seat_state("王剑") == "broken")
check("打破不扣反驳机会", d.bullets == r1_bullets - 1)
d.select("time_window")
d.rebut()
check("同一句不能重复打破，也不白扣机会",
      d.silence == 1 and d.bullets == r1_bullets - 1)

# 5) 方廷
while ROUND1[d.i].weak_to != "diary_fang":
    d.advance()
ev_give("diary_fang")
d.select("diary_fang")
d.rebut()
check("方廷沉默", d.silence == 2 and d.silence_total == d.silence)

# 6) 沈南舟是反问，不算赢
while ROUND1[d.i].speaker != "沈南舟":
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

# 后四夜的发言表要等 13/14 两个文件 exec 进来才存在，所以这张表排在这儿。
# bullets 一律取自 03_flow 那几行实参（见上面 round_cfg），不在这儿重写数字。
ROUNDS = [(nm, g[round_cfg[key]["stmts"]], round_cfg[key]["bullets"])
          for key, nm in (("round2", "第二轮"), ("round3", "第三轮"),
                          ("round4", "第四轮"), ("round5", "第五轮"))]

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

# ---------------- 旧档补齐真的会跑 ----------------
# 对质状态是 default round1..5 这几个全局，存档时被原样 pickle。字段是后加的，
# 而早先这里只写了 after_upgrade、没写 __setstate__——那个名字是 renpy.object.Object
# 的钩子，普通 object 子类存档时没人会调它，整段安心代码其实一次都没执行过。
full = Debate(SEATS, ROUND1, bullets=3)
back = Debate.__new__(Debate)
if hasattr(back, "__setstate__"):
    back.__setstate__(full.__getstate__())
else:
    back.__dict__.update(full.__getstate__())
check("对质对象存一轮再取，字段一个不多一个不少",
      set(vars(back)) == set(vars(full)) and "__version__" not in vars(back))
check("取回来的这一局和存进去的是同一本账",
      back.max_bullets == full.max_bullets and back.silence_total == full.silence_total
      and back.label == full.label)

# 手搓一份"旧档"：把后加的字段和 __version__ 一起抹掉，再走恢复时走的同一条路。
# 不用 pickle.dumps：这里的 Debate 是 exec 进临时命名空间的，标准 pickle 按
# __module__ 找不回来；而引擎存档时用的正是 __getstate__／__setstate__ 这一对。
stale = dict(full.__getstate__())
for k in ("__version__", "max_bullets", "head", "sub", "spent", "heard", "broken",
          "counters", "passes", "done", "message", "selected", "i", "silence",
          "silence_total"):
    stale.pop(k, None)
zombie = Debate.__new__(Debate)
if hasattr(zombie, "__setstate__"):
    zombie.__setstate__(stale)
else:
    # 没有 __setstate__ 时，pickle 恢复只做这一件事——那正是旧写法踩的坑：
    # 字段一个都补不出来，进界面读第一格就 AttributeError。
    zombie.__dict__.update(stale)
need = ("spent", "heard", "broken", "counters", "passes", "done", "message",
        "selected", "i", "silence", "silence_total", "max_bullets", "head", "sub")
lacking = [k for k in need if not hasattr(zombie, k)]
check("旧档缺的 14 个字段被补齐（缺 %d 个）" % len(lacking), not lacking)
check("补齐之后的沉默总数算得对", zombie.silence_total == full.silence_total)
# 补齐之后还能真的打一局：进界面第一件事就是 seat_state()，它读 broken/done。
zombie.i = 0
check("补过旧档的对质能立刻算席位状态",
      zombie.seat_state(ROUND1[0].speaker) in ("active", "idle", "broken", "countered"))

print("")
if fails:
    print("FAILED: %d" % len(fails))
    sys.exit(1)
print("all good")
