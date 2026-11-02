"""出包审计：发行包里不该有的东西逐条列出来，该有的东西一样不许少。

用法：python tools/audit_dist.py [dist 目录]

两条从实测里学到的，别按直觉改：
  1. Ren'Py 的包里有 180 多个 __pycache__ 项——那是引擎自己带的，不是本项目漏的，
     所以只审"项目侧"的条目（剔掉 renpy/ 那一层）。
  2. game/cache/ 里会留下 bytecode-312.rpyb 和 build_info.json 两个文件，这两个
     是 SDK 自己在 00build.rpy 里标成 "all" 的，是发行包的组成部分；本地 cache 里
     另外那几个（py3analysis.rpyb、screens.rpyb、shaders.txt）才是该被排除的。
     所以这里不查"有没有 cache"，查"cache 里除了这两样还有没有别的"。

只查"不该有"会漏掉反方向：build.classify 手抖多排除一张背景图，包里干干净净，
审计照报 all good，玩家进去才看见灰块。所以另一半是从源码树推出 game/ 该有哪些文件，
少一个报一个；README 还要逐字对一遍——包里有 README.md 不等于有的是给玩家那一份。
"""

import os
import sys
import tarfile
import zipfile

DEV_MARKERS = ("tools/", "99_shots", "shots/", "fonts_src", "_prev", "saves/",
               ".bak", ".orig", "glyphs", "docs/")
# 按整个文件名比，不按子串：`log.txt` 当子串会连 "dialog.txt" 一起咬住，
# 而当子串放行又咬不住 market 包里那种没有平台目录前缀的 "log.txt"。
DEV_NAMES = ("log.txt", "traceback.txt", "requirements.txt")
CACHE_OK = ("bytecode-", "build_info.json")
# 包里的 game/ 该有什么，直接从源码树推——写死数字会漂，
# 而"漂了"在这条线上是静默的：少了一个背景图，包照样能开。
GAME_SKIP_PREFIX = ("saves/", "cache/", "__pycache__/", "99_shots")
GAME_SKIP_SUFFIX = (".bak", ".orig", "~")


def entries(path):
    if path.endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            return [n.replace("\\", "/") for n in z.namelist()]
    if path.endswith(".tar.bz2"):
        with tarfile.open(path) as t:
            return [m.name for m in t.getmembers()]
    return None


def read_member(path):
    """发行包里那个 README 的实际内容。要和源码树那份逐字对上，
    不能只看"有个 README.md"——包里躺着带剧透的旧版也是'有'。"""
    if path.endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            for n in z.namelist():
                if n.replace("\\", "/").endswith("/README.md") or n == "README.md":
                    return z.read(n)
        return None
    if path.endswith(".tar.bz2"):
        with tarfile.open(path) as t:
            for m in t.getmembers():
                if m.name.endswith("/README.md") or m.name == "README.md":
                    f = t.extractfile(m)
                    return f.read() if f else None
    return None


def expected_game():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gdir = os.path.join(root, "game")
    out = set()
    for base, _dirs, files in os.walk(gdir):
        for fn in files:
            rel = os.path.relpath(os.path.join(base, fn), gdir).replace("\\", "/")
            if rel.startswith(GAME_SKIP_PREFIX) or rel.endswith(GAME_SKIP_SUFFIX):
                continue
            out.add(rel)
    return out


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join("..", "blackbird-dists")
    want_game = expected_game()
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(here, "README.md"), "rb") as f:
        want_readme = f.read()
    bad_total = 0
    arch = sorted(n for n in os.listdir(root)
                  if n.endswith(".zip") or n.endswith(".tar.bz2"))
    if not arch:
        # 一个包都没扫到就报 all good，是这条闸门最坏的样子：
        # 目录写错、包还没出，看上去全绿。
        print("FAIL %s 里没有任何 .zip/.tar.bz2 可审" % root)
        return 1
    for name in arch:
        path = os.path.join(root, name)
        names = entries(path)
        proj = [n for n in names if "/renpy/" not in n and not n.startswith("renpy/")]
        leaks = [n for n in proj if any(k in n for k in DEV_MARKERS)
                 or os.path.basename(n.rstrip("/")) in DEV_NAMES]
        cache = [n for n in proj if "/game/cache/" in n or n.startswith("game/cache/")]
        leaks += [n for n in cache
                  if not n.endswith("/") and not any(c in n for c in CACHE_OK)]
        game = [n for n in proj if "/game/" in n or n.startswith("game/")]
        wav = [n for n in proj if n.endswith(".wav")]
        lic = [n for n in proj if "LICENSE" in n.upper() or n.endswith(".md")]
        size = os.path.getsize(path) / 1048576.0

        # 下限：game/ 里源码树有什么，包里就得有什么。
        # game/ 在包里的位置有两种：pc/mac/linux 前面套一层平台目录，
        # market 包直接以 game/ 开头——两种都要剥到同一个相对路径上比。
        def rel_game(n):
            if "/game/" in n:
                return n.split("/game/", 1)[1]
            if n.startswith("game/"):
                return n[5:]
            return None
        grels = [r for r in (rel_game(n) for n in game) if r and not r.endswith("/")]
        got_game = set(grels)
        missing = sorted(want_game - got_game)
        readme = read_member(path)
        if readme is None:
            missing.append("README.md（包里根本没有）")
        elif readme != want_readme:
            missing.append("README.md（和源码树那份不一致：包旧于源，或塞了别的版本）")
        fonts = len([r for r in grels
                     if r.startswith("fonts/") and r.lower().endswith((".ttf", ".otf"))])

        print("%-24s %5.1f MB  项目 %4d  game %3d  字体 %d  音频 %d  授权 %d"
              "  漏 %d  缺 %d"
              % (name, size, len(proj), len(game), fonts, len(wav), len(lic),
                 len(leaks), len(missing)))
        for n in leaks:
            print("    LEAK", n)
        for n in missing:
            print("    MISSING", n)
        bad_total += len(leaks) + len(missing)
    print("all good" if bad_total == 0 else "%d 处该排除的没排掉／该带的没带上" % bad_total)
    return 1 if bad_total else 0


if __name__ == "__main__":
    sys.exit(main())
