# -*- coding: utf-8 -*-
"""把五轮对质的发言整本合成神经语音，一句一条 mp3。

料不从本文件里抄，从 shots/_statements.json 读——那份档由 99_shots.rpy 在
引擎里把 ROUND1..5 摊平落盘，是唯一一份和运行时同源的发言表。台词改了没重跑
截图，这里念到的还是旧词，闸门会叫。

为什么是 41 句全配、而不是只配"关键的那几句"：本子的胜负写在"哪句话能被打断"
上。只给有破绽的 21 句配音，等于在解出来的那几句头顶挂一盏灯——玩家不用懂案情，
听哪句有人开口就抵哪句，四下机会够用，推理这一关直接空转。所以整桌都出声，
人声不携带任何"这句可破"的信息。为什么不配全本：这一轮要的是"圆桌边有人说话"，
正文是卷宗，念出来是广播剧，跟阅读的节奏打架；而且改稿一次就要整本重合成。

音色用的是微软 edge-tts 的神经音色（联网合成一次，产出 mp3，游戏里不联网、
不装语音库）。六个人共用五副嗓子：方廷和王剑同为 Yunyang，靠音高与语速分开。
这一句不藏，README 的配音一节照抄。

    python blackbird-vn/tools/build_voice.py [--force]

产出 game/voice/*.mp3 与 game/15_voice.rpy（台词原文 → 文件的映射）。
"""
import asyncio
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(HERE, "game")
DUMP = os.path.join(HERE, "shots", "_statements.json")
OUTDIR = os.path.join(GAME, "voice")
MAP_RPY = os.path.join(GAME, "15_voice.rpy")
# 合成缓存放在 shots/（不进包、不进 git），别落在 game/voice/ 里：
# 那是发行树，一条 json 也要跟着打包走一遍。
MANIFEST = os.path.join(HERE, "shots", "_voice_manifest.json")

# 说话人 → (edge-tts 音色, 语速, 音高, 这一副嗓子的理由)
CAST = {
    "沈南舟": ("zh-CN-YunjianNeural", "-12%", "-28Hz", "主人：压低的慢，不催任何人"),
    "赵寒":   ("zh-CN-YunxiNeural", "-14%", "-32Hz", "退伍的硬，比王剑低一档"),
    "王剑":   ("zh-CN-YunyangNeural", "-6%", "-8Hz", "医生：稳，收着说"),
    "方廷":   ("zh-CN-YunyangNeural", "+8%", "+10Hz", "律师：同一副嗓子，抬高一档说快"),
    "周亦安": ("zh-CN-YunxiaNeural", "-4%", "+0Hz", "抄卷宗的人，声音软"),
    "林晚":   ("zh-CN-XiaoxiaoNeural", "-4%", "+0Hz", ""),
    "苏蔓":   ("zh-CN-XiaoyiNeural", "-6%", "-5Hz", "年轻一档的女声"),
    "陈默":   ("zh-CN-YunxiNeural", "-10%", "-14Hz", "本轮没有他的破绽句"),
}


def load_lines():
    if not os.path.exists(DUMP):
        sys.exit("缺 shots/_statements.json——先跑一遍截图脚本（见 README 的截图命令）。")
    with io.open(DUMP, encoding="utf-8") as f:
        rows = json.load(f)
    # 整桌都配，见文件头：只配破绽句等于给可破的句子挂灯。
    return rows


def synth(text, voice, rate, pitch, dest):
    import edge_tts
    com = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    asyncio.run(com.save(dest))


def main():
    force = "--force" in sys.argv
    lines = load_lines()
    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)
    if not os.path.isdir(os.path.dirname(MANIFEST)):
        os.makedirs(os.path.dirname(MANIFEST))
    old = {}
    if os.path.exists(MANIFEST):
        with io.open(MANIFEST, encoding="utf-8") as f:
            old = json.load(f)

    fresh = {}
    made = skipped = 0
    for r in lines:
        voice, rate, pitch, _why = CAST[r["speaker"]]
        token = hashlib.sha1((voice + rate + pitch + r["text"]).encode("utf-8")).hexdigest()[:12]
        dest = os.path.join(OUTDIR, r["id"] + ".mp3")
        if not force and old.get(r["id"]) == token and os.path.exists(dest):
            skipped += 1
        else:
            synth(r["text"], voice, rate, pitch, dest)
            size = os.path.getsize(dest)
            if size < 2000:
                sys.exit("%s 只有 %d 字节，合成八成没成功（%s）" % (r["id"], size, r["text"]))
            made += 1
            print("OK  %-6s %-4s %6d  %s" % (r["id"], r["speaker"], size, r["text"][:24]))
        fresh[r["id"]] = token

    with io.open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(fresh, f, indent=1, sort_keys=True)

    emit_map(lines)
    print("合成 %d 条，复用 %d 条；映射写入 15_voice.rpy" % (made, skipped))


def emit_map(lines):
    """写 game/15_voice.rpy：台词原文 → mp3。

    用原文当键而不是 (轮, 序号)：对质运行时手里只有 Statement 对象，
    取到 text 就能查；而 id 需要 round 在场时才知道，读档重进还得重建。
    代价是台词一字不能改——改了就是漏白，闸门（test_content.py 配音段）盯着。
    """
    rows = []
    for r in lines:
        rows.append("        %s: \"voice/%s.mp3\"," % (json.dumps(r["text"], ensure_ascii=False), r["id"]))
    with io.open(MAP_RPY, "w", encoding="utf-8") as f:
        f.write(u"""# ============================================================
# 对质发言的配音映射表：台词原文 → voice 通道上的文件。
# 这份文件由 tools/build_voice.py 生成，不要手改；台词一改就要重跑它。
#   合成引擎：微软 edge-tts 神经音色（联网合成一次，游戏里离线播放 mp3）。
#   配的是五轮对质的整桌发言，一句不漏——只配破绽句的话，
#   "哪句有人开口"本身就漏了答案。正文（说书那一路）刻意不配音。
# 音色分配写在 tools/build_voice.py 的 CAST 里，六个人共用五副嗓子。
# ============================================================

init python:

    BB_VOICE = {
%s
    }
""" % u"\n".join(rows))


if __name__ == "__main__":
    main()
