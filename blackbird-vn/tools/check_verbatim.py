# -*- coding: utf-8 -*-
"""Verbatim check: every spoken line must be findable in the manuscript.

Usage:
    python blackbird-vn/tools/check_verbatim.py

The rule is "no rewriting, only deleting". Eyes can't hold this, so it is a script:
collapse 黑鸟岛-终稿.md into one whitespace-free string and check every line.
Deleting is allowed clause by clause, never from the middle of a clause — that half of
the rule is `clause_cut` below. House rules checked too: no full-width exclamation
marks, no arabic digits in speech, every chapter has a dated card.

Words written for the interface are not adaptation: narrator lines (N), hotspot
prose, the prologue (story), the coda (epilogue), the inter-day notes (dayN_pass),
and any line carrying a trailing `# 自撰` marker (supported, currently unused).
Lines inside those frames are not compared word by word, so FREE_MAX caps how many
of them can lack a manuscript source — a ceiling, not a rubber stamp.

Third gate, added after the first two were found to leak: quoted speech. A
`hit=`／`miss=` string is narration and is exempt above — but a Chinese quote pair
inside it is some named person talking, and neither LINE_RE nor STMT_RE sees it.
Every such pair must be in the manuscript or echo a line this script already
verified; short ones are button labels, not speech.

Fourth gate: the 并排 desk. Its middle line is data (`PA("a","b",line)`), sits
outside every label, and LINE_RE will never reach it. So it gets a stricter rule
than speech: the whole run must appear *contiguously* in the manuscript — no
subsequence, no stitching one clause from chapter 13 to one from chapter 19.
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


# ---------------- 拆句删 ----------------
# verdict 走的是"子序列"，于是它只保证词都在，不保证它们原来挨在一起。
# 把一句台词从中间挖掉两个字，它照样绿——上一次批量改引号体例就这么挖坏了四句：
# "被标注为'C'"成了"被“C”"，"第三天提交了自首书"没了谓语，读起来是病句。
# 这条补的是同一只门的另一半：删只能按小句删。每个小句要在正文里整段连着出现，
# 小句与小句之间隔掉的那段必须含标点（＝原来就是两个小句）。
# 只管 verdict 认下来的行：自撰的话整句都不在正文里，不归它比。
# 它看不见句首丢一两个字那一种（"对'陈默'这个名字"丢了"对"）——那类旁白走 N，
# 本来就不逐字比对；真要防，得连"前一个字是不是标点"一起管，代价是误伤连接词。
CLAUSE_PUNCT = set(u'，。、；：？！…—–（）()《》〉「』【】')
DROP = re.compile(u'[\\s*`>"\'“”‘’\\[\\]『』]')


def keep_punct(s):
    return DROP.sub('', s)


def clauses(t):
    out, buf = [], u''
    for c in t:
        if c in CLAUSE_PUNCT:
            if len(buf) >= 2:
                out.append(buf)
            buf = u''
        else:
            buf += c
    if len(buf) >= 2:
        out.append(buf)
    return out


def _chain(fr, src_k, start, pos):
    """从 pos 起给 fr[start] 挑一个位置，往后逐个小句连着走。
    只认第一次出现会走偏：同一句短话正文里到处有，链条要试到走通为止。"""
    if start >= len(fr):
        return True
    i = src_k.find(fr[start], pos)
    if i < 0:
        return False
    if start > 0 and not any(c in CLAUSE_PUNCT for c in src_k[pos:i]):
        return False
    return _chain(fr, src_k, start + 1, i + len(fr[start]))


def clause_cut(text, src_k):
    """True ＝"整句照搬或按小句删"；False ＝有小句被从中间挖过。"""
    fr = clauses(keep_punct(text))
    if not fr:
        return True
    return _chain(fr, src_k, 0, 0)


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
    """Statement 的正文台词。hit／miss 是旁白，这里不查——
    但旁白里引号包住的那一段照样查，见 each_quote。"""
    for p in sorted(glob.glob(os.path.join(GAME, '*.rpy'))):
        if os.path.basename(p).startswith('99_'):
            continue
        body = io.open(p, encoding='utf-8').read()
        for m in STMT_RE.finditer(body):
            ln = body[:m.start()].count('\n') + 1
            text = m.group(2).replace('\\"', '"')
            yield os.path.basename(p), ln, m.group(1), text


# ---------------- 引号里不许长出新台词 ----------------
# "hit／miss 是旁白，不查" 这句注释只对一半：旁白确实可以自撰，但旁白里一旦有
# 中文引号，那一段就是某个具体的人说的话——它落在字符串参数里，LINE_RE 和
# STMT_RE 都吃不到，于是界面给人物代笔，脚本一声不吭。2026-11-03 清点时就是这么
# 漏着三句（方廷"它进过"、主人"你替我数一遍"、主人"缝在哪一册上的"），README 那句
# "不增写一句台词"当时是假的。
# 规则：任何一对中文引号里的话，要么在终稿里，要么是本作已经验过的台词的回声
# （界面复述人物刚说过的那几个字，比如"他不接“不在场”那三个字"）。
# 短于三个字的当按钮名放行——帮助页写"再选“反　驳”"不是台词。
BARE = re.compile(u'[^一-鿿0-9a-zA-Z]')
CQuote = re.compile(u'“([^“”]*)”')
STR_RE = re.compile(r'"((?:[^"\\]|\\.)+)"')


def bare(s):
    return BARE.sub('', s)


def game_speech():
    """本作自己已经逐字验过的台词，拿去当回声的语料。"""
    out = []
    for p in sorted(glob.glob(os.path.join(GAME, '*.rpy'))):
        if os.path.basename(p).startswith('99_'):
            continue
        body = io.open(p, encoding='utf-8').read()
        for m in STMT_RE.finditer(body):
            out.append(m.group(2))
        for line in body.split('\n'):
            lm = LINE_RE.match(line)
            if lm:
                out.append(lm.group(3))
    return bare('|'.join(out))


def each_quote():
    """串里套引号的行都交出来；整行注释不算（帮助页的说明文字会引按钮名）。"""
    for p in sorted(glob.glob(os.path.join(GAME, '*.rpy'))):
        if os.path.basename(p).startswith('99_'):
            continue
        for i, raw in enumerate(io.open(p, encoding='utf-8').read().split('\n'), 1):
            if raw.strip().startswith('#'):
                continue
            for sm in STR_RE.finditer(raw):
                body = sm.group(1).replace('\\"', '"')
                for q in CQuote.finditer(body):
                    yield os.path.basename(p), i, q.group(1)


# ---------------- 数据层里给玩家读的那一行 ----------------
# 并排那一屏的中间行是玩家在那个界面上唯一读到的"内容"。它写成 PA() 的数据，
# 不在任何 label 里，LINE_RE 一辈子看不见——所以它得有自己的门，而且比台词那道
# 更严：整段必须在正文里*连着*出现（norm 之后是子串）。子序列不算，跨小句拼贴
# 不算。把第十三章的一句和第十九章的一句缝成一屏"新证据"，正是这道门要挡的。
PAIR_RE = re.compile(r'PA\(\s*"([a-z0-9_]+)"\s*,\s*"([a-z0-9_]+)"\s*,\s*'
                     r'"((?:[^"\\]|\\.)*)"')


def each_pair():
    for p in sorted(glob.glob(os.path.join(GAME, '*.rpy'))):
        body = io.open(p, encoding='utf-8').read()
        for m in PAIR_RE.finditer(body):
            ln = body[:m.start()].count('\n') + 1
            yield os.path.basename(p), ln, m.group(1), m.group(2), \
                ast.literal_eval('"' + m.group(3) + '"')


def main():
    src = src_text()
    src_k = keep_punct(io.open(NOVEL, encoding='utf-8').read())
    ok = 0
    free = 0
    miss = []
    total = 0
    bang = []
    nums = []
    quoted = 0
    cut = []        # 拆句删：verdict 认了出处、小句却被从中间挖过
    stricted = 0

    for fn, ln, who, text in each_statement():
        total += 1
        if verdict(norm(text), src) == 'OK':
            ok += 1
            stricted += 1
            if not clause_cut(text, src_k):
                cut.append('%s:%d %s %s' % (fn, ln, who, text[:48]))
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
            spoken = piece
            piece = norm(piece)
            if not piece:
                continue
            total += 1
            v = verdict(piece, src)
            if v == 'OK':
                ok += 1
                if not is_free:
                    stricted += 1
                    if not clause_cut(spoken, src_k):
                        cut.append('%s:%d %s %s' % (fn, ln, who, spoken[:48]))
            elif is_free:
                free += 1
            else:
                miss.append('%s:%d %s %s' % (fn, ln, who, piece[:48]))

    own_bare = game_speech()
    qtot = 0
    invented = []
    for fn, ln, frag in each_quote():
        f = bare(frag)
        if len(f) < 3:
            continue
        qtot += 1
        if verdict(norm(frag), src) == 'OK' or f in own_bare:
            continue
        invented.append(u'%s:%d “%s”' % (fn, ln, frag[:48]))

    ptot = 0
    pmiss = []
    for fn, ln, a, b, line in each_pair():
        ptot += 1
        if norm(line) not in src:
            pmiss.append(u'%s:%d %s×%s “%s”' % (fn, ln, a, b, line[:48]))

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
    print(u'拆句删（小句被从中间挖过） %d 处' % len(cut))
    for x in cut[:20]:
        print(u'  CUT ' + x)
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
    print(u'引号里的话 %d 段（旁白中代人物说的：%d）' % (qtot, len(invented)))
    for x in invented[:20]:
        print(u'  VOICE ' + x)
    print(u'并排句 %d 条（不在正文里连着的：%d）' % (ptot, len(pmiss)))
    for x in pmiss[:20]:
        print(u'  PAIR ' + x)
    over = []
    if quoted < 1:
        over.append(u'引号代号的台词一行都没扫到——LINE_RE 的 SPEAK 分支失效了')
    if qtot < 40:
        over.append(u'只扫到 %d 段引号里的话——STR_RE／CQuote 没吃到行，回声闸门在空转' % qtot)
    if ptot < 8:
        over.append(u'只扫到 %d 条并排句——PAIR_RE 没吃到 PA()，数据层那道门在空转' % ptot)
    if stricted < 400:
        over.append(u'拆句删只比对了 %d 段——keep_punct／clauses 没吃到行，闸门在空转' % stricted)
    if free > FREE_MAX:
        over.append(u'界面自撰 %d 超额度 %d：往热点／旁白里塞的话不再逐字比对'
                    % (free, FREE_MAX))
    if len(nums) > NUM_MAX:
        over.append(u'阿拉伯数字 %d 超额度 %d：只有抄来的文书（日期、编号）许用'
                    % (len(nums), NUM_MAX))
    for x in over:
        print(u'  SCOPE ' + x)
    return 1 if (miss or bang or nocard or cut or over or invented or pmiss) else 0


if __name__ == '__main__':
    sys.exit(main())
