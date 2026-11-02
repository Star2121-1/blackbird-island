# -*- coding: utf-8 -*-
"""Verbatim check: every spoken line must be findable in the manuscript.

Usage:
    python blackbird-vn/tools/check_verbatim.py

The rule is "no rewriting, only deleting". Eyes can't hold this, so it is a script:
collapse 黑鸟岛-终稿.md into one whitespace-free string and check every line.
House rules checked too: no full-width exclamation marks, no arabic digits in speech,
every chapter has a dated card.

Words written for the interface are not adaptation: narrator lines (N), hotspot
prose, the prologue (story), the coda (epilogue), the inter-day notes (dayN_pass),
and any line carrying a trailing `# 自撰` marker (supported, currently unused).
Lines inside those frames are not compared word by word, so FREE_MAX caps how many
of them can lack a manuscript source — a ceiling, not a rubber stamp.
"""
import ast
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOVEL = os.path.join(os.path.dirname(ROOT), u'黑鸟岛-终稿.md')
GAME = os.path.join(ROOT, 'game')

# 说话人两种写法都要吃到：名单上的角色用变量（ME/SU/…），名单外的用引号当代号
# （"船老大" "到了。"）。早先只认 [A-Z]{1,4}，那一条整句没进过这道门——
# 引号里再写一段编的话，脚本一声不吭。
SPEAK = r'(?:[A-Z]{1,4}|"(?:[^"\\]|\\.)*")'
LINE_RE = re.compile(r'^(\s*)(' + SPEAK + r')\s+"((?:[^"\\]|\\.)*)"\s*(#.*)?$')

# 圆桌发言和对白同级：Statement("谁", "话", ...) 的第二参要逐字可溯
STMT_RE = re.compile(r'Statement\(\s*"([^"]*)"\s*,\s*"((?:[^"\\]|\\.)*)"\s*[,\)]')

# 只留汉字和中文标点：引号是排版不是措辞。终稿 markdown 用直引号 "，界面排成 “”
KEEP = re.compile(u'[^一-鿿，。、；：？！…—–（）()《》〈〉「』『·　-〿]')
SPLIT = re.compile(u'[，。、；：？！…—–（）()《》〉「』『·　-〿]')

FRAME = re.compile(r'^(story|epilogue|day\d_pass|day6_end|spot_)')

# 界面自撰的额度。FRAME 标签里和 N 旁白不进逐字比对，于是往热点里塞一句"角色说的话"
# 也不会报警。56 是逐条核过的现存上限：加了新数，就得回来看一眼是不是把台词写成自撰了。
FREE_MAX = 56
# 台词里的阿拉伯数字只许出现在"抄来的文书"里（日期、警方的 A-001 编号、封装记录、
# 照片背面那行红笔字）。这条原先只打印不判，等于没有闸门；数一多照样静默。
NUM_MAX = 5


def norm(s):
    return KEEP.sub('', s)


def src_text():
    return norm(io.open(NOVEL, encoding='utf-8').read())


def anchors(src, t):
    """起点候选：整串、头 8 字、头 5 字、尾 6 字各去锚，位置全部交出来。
    只取第一个命中会走偏——'我在家' 这种短句正文里到处都是。"""
    for probe in (t, t[:8], t[:5], t[-6:]):
        if len(probe) < 3 or probe not in t:
            continue
        off = t.index(probe)
        hits = []
        i = 0
        while len(hits) < 60:
            i = src.find(probe, i)
            if i < 0:
                break
            hits.append(i - off)
            i += 1
        if hits:
            return hits
    return []


def window_hit(src, t, a):
    """t 是否为 src 在锚点附近那个窗口里的子序列"""
    lo = max(0, a - 40)
    hi = min(len(src), a + len(t) * 2 + 160)
    p = lo
    for c in t:
        q = src.find(c, p, hi)
        if q < 0:
            return False
        p = q + 1
    return True


def frags_hit(src, t, a):
    """窗口对不上时按小句再走一遍：手稿常把一句台词劈开
    "袖口。"他说，"这里有一个绣标。" 台词层抹平说话人拼回一句，整串就锚不上。
    小句要挤在同一段里：隔得太远是拼贴，不是删节。"""
    fr = [f for f in SPLIT.split(t) if len(f) >= 3]
    if not fr:
        return False
    p = a
    for k, f in enumerate(fr):
        q = src.find(f, p)
        if q < 0:
            return False
        if k and q - p > 400:
            return False
        p = q + len(f)
    return True


def verdict(t, src):
    if not t:
        return 'OK'
    if src.find(t) >= 0:
        return 'OK'
    cand = anchors(src, t) or [0]
    for a in cand:
        if window_hit(src, t, a):
            return 'OK'
    for a in cand:
        if frags_hit(src, t, a):
            return 'OK'
    return 'MISS'


def each_line():
    """带着当前 label 一起交出来：界面写的话不算改编正文"""
    for p in sorted(glob.glob(os.path.join(GAME, '*.rpy'))):
        if os.path.basename(p).startswith('99_'):
            continue
        lab = ''
        lines = io.open(p, encoding='utf-8').read().split('\n')
        for i, raw in enumerate(lines, 1):
            lm = re.match(r'^label ([A-Za-z0-9_]+)', raw)
            if lm:
                lab = lm.group(1)
            yield os.path.basename(p), i, raw, lab


def each_statement():
    """hit／miss 是旁白，不查"""
    for p in sorted(glob.glob(os.path.join(GAME, '*.rpy'))):
        if os.path.basename(p).startswith('99_'):
            continue
        body = io.open(p, encoding='utf-8').read()
        for m in STMT_RE.finditer(body):
            ln = body[:m.start()].count('\n') + 1
            text = m.group(2).replace('\\"', '"')
            yield os.path.basename(p), ln, m.group(1), text


def main():
    src = src_text()
    ok = 0
    free = 0
    miss = []
    total = 0
    bang = []
    nums = []
    quoted = 0

    for fn, ln, who, text in each_statement():
        total += 1
        if verdict(norm(text), src) == 'OK':
            ok += 1
        else:
            miss.append('%s:%d %s %s' % (fn, ln, who, text[:48]))

    for fn, ln, raw, lab in each_line():
        m = LINE_RE.match(raw)
        if not m:
            continue
        who = m.group(2)
        if who.startswith('"'):
            quoted += 1
        text = ast.literal_eval('"' + m.group(3) + '"')
        if u'！' in text:
            bang.append('%s:%d %s' % (fn, ln, text[:40]))
        if re.search(r'[0-9]', text):
            nums.append('%s:%d %s' % (fn, ln, text[:40]))
        note = m.group(4) or u''
        is_free = (bool(FRAME.match(lab)) or who == 'N' or u'自撰' in note)
        for piece in text.split('\n'):
            piece = norm(piece)
            if not piece:
                continue
            total += 1
            v = verdict(piece, src)
            if v == 'OK':
                ok += 1
            elif is_free:
                free += 1
            else:
                miss.append('%s:%d %s %s' % (fn, ln, who, piece[:48]))

    cards = 0
    nocard = []
    for p in sorted(glob.glob(os.path.join(GAME, '*.rpy'))):
        if os.path.basename(p).startswith('99_'):
            continue
        body = io.open(p, encoding='utf-8').read()
        for lm in re.finditer(r'^label (ch\d+):', body, re.M):
            seg = body[lm.start():lm.start() + 400]
            if 'bb_card(' not in seg:
                nocard.append(lm.group(1) + u' 没有章节卡片')
                continue
            cards += 1
            if u'十一月' not in seg.split('bb_card(')[1][:220]:
                nocard.append(lm.group(1) + u' 卡片缺日期锚')

    print(u'台词 %d 段：逐字可溯 %d，界面自撰 %d，找不到出处 %d'
          % (total, ok, free, len(miss)))
    for x in miss[:40]:
        print(u'  MISS ' + x)
    # 正则漂了的话，上面那三行会一起变 0 而脚本照样绿——和 test_content 里
    # "容器闸门真的在扫" 一个道理，抓到的量也得验。
    print(u'引号代号台词 %d 行' % quoted)
    print(u'全角叹号 %d 处' % len(bang))
    for x in bang[:10]:
        print(u'  BANG ' + x)
    print(u'台词含阿拉伯数字 %d 处' % len(nums))
    for x in nums[:10]:
        print(u'  NUM ' + x)
    print(u'章节卡片 %d 张' % cards)
    for x in nocard:
        print(u'  CARD ' + x)
    over = []
    if quoted < 1:
        over.append(u'引号代号的台词一行都没扫到——LINE_RE 的 SPEAK 分支失效了')
    if free > FREE_MAX:
        over.append(u'界面自撰 %d 超额度 %d：往热点／旁白里塞的话不再逐字比对'
                    % (free, FREE_MAX))
    if len(nums) > NUM_MAX:
        over.append(u'阿拉伯数字 %d 超额度 %d：只有抄来的文书（日期、编号）许用'
                    % (len(nums), NUM_MAX))
    for x in over:
        print(u'  SCOPE ' + x)
    return 1 if (miss or bang or nocard or over) else 0


if __name__ == '__main__':
    sys.exit(main())
