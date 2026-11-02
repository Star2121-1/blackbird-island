"""出包审计：发行包里不该有的东西，逐条列出来。

用法：python tools/audit_dist.py [dist 目录]

两条从实测里学到的，别按直觉改：
  1. Ren'Py 的包里有 180 多个 __pycache__ 项——那是引擎自己带的，不是本项目漏的，
     所以只审"项目侧"的条目（剔掉 renpy/ 那一层）。
  2. game/cache/ 里会留下 bytecode-312.rpyb 和 build_info.json 两个文件，这两个
     是 SDK 自己在 00build.rpy 里标成 "all" 的，是发行包的组成部分；本地 cache 里
     另外那几个（py3analysis.rpyb、screens.rpyb、shaders.txt）才是该被排除的。
     所以这里不查"有没有 cache"，查"cache 里除了这两样还有没有别的"。
"""

import os
import sys
import tarfile
import zipfile

DEV_MARKERS = ("tools/", "99_shots", "shots/", "fonts_src", "_prev", "saves/",
               ".bak", ".orig", "glyphs")
CACHE_OK = ("bytecode-", "build_info.json")


def entries(path):
    if path.endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            return [n.replace("\\", "/") for n in z.namelist()]
    if path.endswith(".tar.bz2"):
        with tarfile.open(path) as t:
            return [m.name for m in t.getmembers()]
    return None


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join("..", "blackbird-dists")
    bad_total = 0
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        names = entries(path)
        if names is None:
            continue
        proj = [n for n in names if "/renpy/" not in n and not n.startswith("renpy/")]
        leaks = [n for n in proj if any(k in n for k in DEV_MARKERS)]
        cache = [n for n in proj if "/game/cache/" in n or n.startswith("game/cache/")]
        leaks += [n for n in cache
                  if not n.endswith("/") and not any(c in n for c in CACHE_OK)]
        game = [n for n in proj if "/game/" in n or n.startswith("game/")]
        wav = [n for n in proj if n.endswith(".wav")]
        lic = [n for n in proj if "LICENSE" in n.upper() or n.endswith(".md")]
        size = os.path.getsize(path) / 1048576.0
        print("%-24s %5.1f MB  项目 %4d  game %3d  音频 %d  授权 %d  漏 %d"
              % (name, size, len(proj), len(game), len(wav), len(lic), len(leaks)))
        for n in leaks:
            print("    LEAK", n)
        bad_total += len(leaks)
    print("all good" if bad_total == 0 else "%d 处该排除的没排掉" % bad_total)
    return 1 if bad_total else 0


if __name__ == "__main__":
    sys.exit(main())
