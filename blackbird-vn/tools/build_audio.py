# -*- coding: utf-8 -*-
"""给《黑鸟岛》合成一层环境音和几个音效，全部程序生成，不找素材。

为什么不用现成的录音：这本子要的是"很安静的岛"——海浪压得很低，风只在大厅
外面，雨只在窗外。这种素材在网上找十有八九是"海洋纪录片片头"，一放就把
推理氛围压成风光片。自己合成能把频谱和包络都钉死在想要的程度上。

生成方法：色噪声用频谱法（随机相位 × 目标功率谱），这样出来的序列天生按整
个缓冲区周期，接头就是无缝循环——滤波器如果直接在时域做，两头必然甩出接缝。
雨点和纸响这类瞬态用指数衰减的小段噪声铺上去，铺的时候避开首尾，接缝附近
少两滴听不出来。

**shape(f) 一律收赫兹。** 2026-11-02 之前这里传的是 `freqs / sr`（归一化，0–0.5），
而 lowpass_shape 里的截止是 320 这种赫兹数——0.5/320 ≈ 0.0016，任何斜率的幂都还是
0，四条"色噪声"于是全是白噪声；bandpass 那一支更糟，`lo/f` 变成 900/0.25=3600，
低截止项退化成正比 f^6 的爬升，把高频一路顶上去。实测当时的频谱质心 5.5k–9.8kHz、
1.2k 以上占 90–99% 的能量，玩家听到的就是"沙沙"。现在 main() 末尾按张验质心和
电平，改坏了直接红，不会再静默退化。

    python blackbird-vn/tools/build_audio.py

产出 game/audio/：四条环境循环（sea/wind/rain/room）+ 三条音乐床（hall/sea/room）
+ 四个音效（page/pick/stamp/silence）。
"""
import os
import sys

import numpy as np
from scipy import signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "game", "audio")

SR_LOOP = 22050          # 环境音用 22k：内容全是低频噪声，省一半体积
SR_SFX = 44100           # 音效保留高频，纸响的质感在 4k 以上

RNG = np.random.default_rng(20091117)


def colored_loop(n, sr, shape, channels=2):
    """按目标功率谱生成一段严格周期（接得上头）的色噪声。

    shape(f) 是相对幅度，f 用 Hz。频谱法出来的序列是循环的，因为每个频率
    分量都是整数个周期——不需要再做循环延拓滤波。
    """
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    mag = shape(freqs)
    out = []
    for _ in range(channels):
        phase = np.exp(2j * np.pi * RNG.random(len(freqs)))
        spec = mag * phase
        spec[0] = 0.0                       # 直流去掉，不然接头有台阶
        x = np.fft.irfft(spec, n)
        x = x / (np.sqrt(np.mean(x * x)) + 1e-12)
        out.append(x)
    return np.stack(out, axis=1)


def swell(n, sr, periods, depth, base=1.0):
    """周期包络：只允许整数个周期，保证循环处不跳。"""
    t = np.arange(n) / float(n)
    e = np.full(n, base)
    for p, w in periods:
        e = e + w * np.cos(2 * np.pi * p * t + RNG.random() * 2 * np.pi)
    e = np.clip(base + depth * (e - base), 0.05, None)
    return e


def lowpass_shape(cut_hz, slope=2.0):
    def shape(f):
        return 1.0 / (1.0 + (np.maximum(f, 1e-6) / cut_hz) ** slope)
    return shape


def bandpass_shape(lo_hz, hi_hz, slope=2.0):
    def shape(f):
        ff = np.maximum(f, 1e-6)
        return (1.0 / (1.0 + (lo_hz / ff) ** (2 * slope))) * \
            (1.0 / (1.0 + (ff / hi_hz) ** (2 * slope)))
    return shape


def add_bursts(x, sr, rate, decay_s, band, level):
    """铺瞬态：rate 个/秒的稀疏点位，每个点是一段带限衰减噪声。

    点位避开首尾各 pad 个样本——循环接缝附近少两滴雨、少一声木头响，
    比在接缝上硬生生截断一段衰减要好得多。
    """
    n = x.shape[0]
    bursts = np.zeros((n, x.shape[1]))
    count = int(rate * n / float(sr))
    pad = int(decay_s * 10 * sr) + 8
    lo, hi = band
    for _ in range(count):
        pos = RNG.integers(pad, n - pad)
        d = int(decay_s * sr * RNG.uniform(0.5, 1.6))
        if d < 4:
            continue
        seg = RNG.standard_normal(d)
        # 三点均值抹掉最尖的高频，再叠一个带内正弦：听着像一滴水落在木头上
        seg = np.convolve(seg, np.ones(3) / 3.0, mode="same")
        t = np.arange(d) / float(sr)
        tone = np.sin(2 * np.pi * RNG.uniform(lo, hi) * t)
        env = np.exp(-t / (decay_s / 3.0))
        bursts[pos:pos + d] += (0.55 * seg + 0.45 * tone)[:, None] * env[:, None] * level
    return x + bursts


def finalize(x, peak_db):
    """归一化到目标峰值，双声道各自去相关，再写 int16。"""
    target = 10.0 ** (peak_db / 20.0)
    m = np.max(np.abs(x))
    if m > 0:
        x = x * (target / m)
    x = np.tanh(1.5 * x) / np.tanh(1.5)     # 软削波，别硬顶
    x = np.clip(x, -1.0, 1.0)
    dither = RNG.uniform(-1, 1, x.shape) / 32767.0
    return np.round((x + dither) * 32767.0).astype(np.int16)


def finalize_loud(x, rms_db):
    """按"有多响"定电平，不按峰值。

    环境音和音乐床的峰均比有 14–19dB（慢涌把包络压得很扁），照峰值定出来的
    RMS 每条都差一截——sea 和 room 同样写 -26dBFS 峰值，实际响度差 6dB。
    音效不一样：那是一下，峰值就是它该被听见的那一下，仍走 finalize。

    这里**不**过 finalize：它那步 `tanh(1.5x)/tanh(1.5)` 是给接近满幅的音效防
    硬削的，对小信号近似 1.5/0.905 = 1.66 倍增益。老的四条环境音写着 -14dBFS
    峰值、量出来 -9.9，就是被这一步偷偷抬了 4dB。
    """
    x = np.asarray(x, dtype=np.float64)
    cur = np.sqrt(np.mean(x * x))
    if cur > 0:
        x = x * (10.0 ** (rms_db / 20.0) / cur)
    m = np.max(np.abs(x))
    if m > 0.99:                      # 顶到天花板就整体让路：宁可偏轻，不要削波
        x = x * (0.99 / m)
    dither = RNG.uniform(-1, 1, x.shape) / 32767.0
    return np.round((x + dither) * 32767.0).astype(np.int16)



def write_wav(path, x, sr):
    from scipy.io import wavfile
    wavfile.write(path, sr, x)
    return os.path.getsize(path)


# ---------------- 四条环境循环 ----------------
# 每条的相对电平都按"整形真的生效了"来定：colored_loop 出来的每一路都被归一化成
# 单位 RMS，所以写 0.16 就是比底噪低 16 dB。改这些数之前先跑一遍看 main() 打的
# 质心和 RMS——上一版就是没人看，白噪声顶着 -14dBFS 的峰值响了半年。

def sea(sr=SR_LOOP, secs=24.0):
    """碎浪：棕色噪声打底 + 一道慢涌 + 一点高频泡沫。"""
    n = int(sr * secs)
    bed = colored_loop(n, sr, lowpass_shape(320, 2.5))
    foam = colored_loop(n, sr, bandpass_shape(1200, 4500, 1.5))
    surge = swell(n, sr, [(1, 1.0), (2, 0.45), (5, 0.22)], 0.85, base=1.0)
    y = bed * surge[:, None] * 0.9 + foam * (surge[:, None] ** 3) * 0.16
    return add_bursts(y, sr, 1.1, 0.22, (900, 2600), 0.05), secs


def wind(sr=SR_LOOP, secs=22.0):
    """穿堂风：带通噪声，阵风用整数周期包络，两声道错开一点。"""
    n = int(sr * secs)
    body = colored_loop(n, sr, bandpass_shape(140, 760, 1.8))
    hiss = colored_loop(n, sr, bandpass_shape(700, 2200, 2.0))
    g1 = swell(n, sr, [(1, 1.0), (3, 0.55), (7, 0.2)], 0.8, base=0.75)
    g2 = swell(n, sr, [(2, 1.0), (4, 0.4), (9, 0.15)], 0.7, base=0.75)
    y = body * g1[:, None] * 0.85
    y[:, 1] = (body * g2[:, None])[:, 1] * 0.85
    # 沙那一层跟 body 的右声道用同一条阵风（g2）：两声道共用 g1 的话，
    # 高频那层在左右耳是完全一样的，风就粘在头顶不动了。
    y = y + hiss * (g2[:, None] ** 2) * 0.07
    return y, secs


def rain(sr=SR_LOOP, secs=20.0):
    """窗外雨：沙沙的高频 + 滴答 + 极低频的湖面底。
    顶到 6k 那一档是当初照着"雨声素材"给的，压到 4.2k：这本子的雨在窗纸外面，
    不是打在铁皮上。再压到 3.4k 是 2026-11-02 实测之后：4.2k 顶时 1.2k 以上
    还占 65% 的能量，是全篇最亮的一条，玩家报的"沙沙"最容易落在它身上。"""
    n = int(sr * secs)
    hiss = colored_loop(n, sr, bandpass_shape(600, 3400, 1.6))
    low = colored_loop(n, sr, lowpass_shape(160, 3.0))
    e = swell(n, sr, [(2, 1.0), (5, 0.5), (11, 0.25)], 0.25, base=1.0)
    y = hiss * e[:, None] * 0.62 + low * 0.35
    return add_bursts(y, sr, 7.0, 0.05, (1400, 3400), 0.07), secs


def room(sr=SR_LOOP, secs=26.0):
    """静场底：阅览室与大厅。压得很低的空调嗡鸣加一点点木头的响动。"""
    n = int(sr * secs)
    bed = colored_loop(n, sr, lowpass_shape(220, 3.5))
    air = colored_loop(n, sr, bandpass_shape(300, 1200, 1.5))
    e = swell(n, sr, [(1, 1.0), (4, 0.3)], 0.10, base=1.0)
    y = bed * e[:, None] * 0.5 + air * 0.06
    return add_bursts(y, sr, 0.35, 0.10, (260, 900), 0.05), secs


def night(sr=SR_LOOP, secs=28.0):
    """夜里的海：同一片水，隔着一层窗。比 amb_sea 低一档、慢一档——
    白天那条的泡沫（涌的三次方）在夜里几乎没有了，剩下远处那阵风。"""
    n = int(sr * secs)
    bed = colored_loop(n, sr, lowpass_shape(240, 2.5))
    far = colored_loop(n, sr, bandpass_shape(120, 520, 1.8))
    surge = swell(n, sr, [(1, 1.0), (2, 0.4), (4, 0.18)], 0.6, base=1.0)
    return bed * surge[:, None] * 0.8 + (far * (surge[:, None] ** 2)) * 0.25, secs


def dust(sr=SR_LOOP, secs=30.0):
    """封存的房间：东翼那一间，没人住、空气是停的。
    比 amb_room 更低更干——木头偶尔响一声，远处隔很久滴一滴。"""
    n = int(sr * secs)
    bed = colored_loop(n, sr, lowpass_shape(140, 3.0))
    air = colored_loop(n, sr, bandpass_shape(240, 900, 1.6))
    e = swell(n, sr, [(1, 1.0), (3, 0.25)], 0.06, base=1.0)
    y = bed * e[:, None] * 0.55 + air * 0.035
    y = add_bursts(y, sr, 0.16, 0.16, (180, 620), 0.05)
    y = add_bursts(y, sr, 0.05, 0.05, (1200, 2200), 0.02)
    return y, secs


# ---------------- 三条音乐床 ----------------
# 为什么不找现成的曲子：要的是"有人在很远的地方弹，隔了一堵墙"——网上那种
# 悬疑片钢琴 loop 一进来就把推理变成广告。自己合成能把音高、密度和混响长度
# 都钉在"压在对白底下"那一档。三床按地点分，和环境音用同一套查表法。
#
# 无缝循环靠三条纪律：和声只按小节网格摆放（每地两小节长，相邻两地叠一整小节）、
# 拨弦只落在 1/4 拍的网格上、尾巴超出循环点的部分圆周绕回开头，混响用圆周卷积。
# 只要每样东西的落点都在网格上、长度固定，绕回来就还是同一张图。任何一条改成
# 时域随机，接缝就露。

SR_MUS = 22050


def place(buf, sig, pos):
    """圆周摆放：sig 比 buf 短，超出末尾的样本绕回开头，循环点因此接得上。"""
    n = len(buf)
    if len(sig) > n:
        sig = sig[:n]
    buf[(np.arange(pos, pos + len(sig))) % n] += sig


def note_sig(f, dur, sr, bright=1.0, level=1.0):
    """一下拨弦：基音加四点泛音，泛音逐阶失谐——理想的正弦是音叉，
    这本子要的是大厅那架走音的旧琴。"""
    n = int(dur * sr)
    t = np.arange(n) / float(sr)
    env = np.minimum(t / 0.012, 1.0) * np.exp(-t / (dur / 3.5))
    y = np.zeros(n)
    for k, a in enumerate((1.0, 0.40, 0.17, 0.07, 0.03), start=1):
        y += a * (bright ** (k - 1)) * np.sin(
            2 * np.pi * f * k * (1 + 0.0007 * k * k) * t + RNG.random() * 2 * np.pi)
    return y * env * level


def pad_sig(fs, dur, sr, level=1.0):
    """一地持续和声：每个音两股微失谐的板，包络用汉宁窗——两头都到零，
    接在循环点上不会跳。"""
    n = int(dur * sr)
    t = np.arange(n) / float(sr)
    e = np.hanning(n) ** 0.5
    y = np.zeros(n)
    for f in fs:
        for det in (-0.0015, 0.0015):
            y += np.sin(2 * np.pi * f * (1 + det) * t + RNG.random() * 2 * np.pi)
    return y / (2.0 * max(1.0, len(fs))) * e * level


def circular_reverb(x, sr, tail_s, decay_s, mix, cut_hz=2200.0):
    """圆周卷积混响：普通卷积会把尾巴甩到缓冲区外面，循环点上就断；
    圆周的那条尾巴绕回开头，听着像这间屋子本来就这么大。"""
    n = len(x)
    m = max(8, int(tail_s * sr))
    ir = colored_loop(m, sr, lowpass_shape(cut_hz, 2.0), channels=1)[:, 0]
    ir = ir * np.exp(-np.arange(m) / float(sr) / decay_s)
    # 头 5ms 拉掉：噪声 IR 的第一格是个随机大幅值，留着它等于把干声按一个
    # 没道理的量加进湿声里，接缝处像回声打在玻璃上。压成一小段预延迟更干净。
    ramp = max(2, int(0.005 * sr))
    ir[:ramp] *= np.linspace(0.0, 1.0, ramp)
    ir = ir / (np.sqrt(np.sum(ir * ir)) + 1e-12)
    X = np.fft.rfft(x)
    wet = np.fft.irfft(X * np.fft.rfft(ir, n), n)
    return (1 - mix) * x + mix * wet


def music_bed(root, chords, bar=8.0, density=1.6, bright=0.9,
              pad_level=0.34, note_level=0.5, tail_s=2.6, decay_s=1.1,
              mix=0.42, pad_over=2.0, clash=None, sr=SR_MUS):
    """一床：每小节一地持续和声，上面按 1/4 拍网格撒稀疏的拨弦，左右声道各撒一遍。

    root 是根音赫兹，chords 是 (相对半音, 和弦内音) 的序列——自然小调，
    因为这本子没有大调的段落。

    pad_over 是每地和声铺到几倍小节长。原本一地正好一小节，汉宁窗两头归零，
    小节接缝处只有"正在起音的那一地"在响——实测单独把和声层拎出来量（拨弦关掉、
    300Hz 以下包络），每小节掉 22.9dB，等于整床响度在九秒一换气。铺到两倍小节、
    相邻两地叠一整小节，接缝处总有一地在窗中间，同一个量法只剩 8.1dB 的起伏
    （那点起伏来自和弦本身的音区差，是要的）。1.5 倍是 11.4dB。
    电平按 sqrt(重叠数) 折回来，免得和声把拨弦盖掉。
    """
    scale = (0, 2, 3, 5, 7, 8, 10)
    loop_s = bar * len(chords)
    n = int(sr * loop_s)
    L = np.zeros(n)
    R = np.zeros(n)
    for i, (base, tones) in enumerate(chords):
        f0 = root * 2.0 ** (base / 12.0)
        fs = [f0 * 2.0 ** (s / 12.0) for s in tones]
        pad = pad_sig(fs, bar * pad_over, sr, pad_level / (pad_over ** 0.5))
        place(L, pad, int(i * bar * sr))
        place(R, pad, int(i * bar * sr))
        if clash is not None:
            # 再压一地、差 clash 个半音：两股差半音的持续音叠在一起，拍音慢到
            # 听不出是两个人在弹，只觉得这间屋子的空气不干净。东翼那一床用。
            off = pad_sig([f * 2.0 ** (clash / 12.0) for f in fs],
                          bar * pad_over, sr, pad_level / (pad_over ** 0.5) * 0.7)
            place(L, off, int(i * bar * sr))
            place(R, off, int((i + 0.5) * bar * sr))
    step = 0.25
    for chan in (L, R):
        pos = 0.0
        while pos < loop_s:
            if RNG.random() < density * step:
                f = root * 2.0 ** (int(RNG.integers(1, 4)) + scale[int(RNG.integers(0, 7))] / 12.0)
                sig = note_sig(f, RNG.uniform(2.2, 4.5), sr, bright,
                               note_level * RNG.uniform(0.55, 1.0))
                place(chan, sig, int(pos * sr))
            pos += step
    y = np.stack([circular_reverb(c, sr, tail_s, decay_s, mix) for c in (L, R)], axis=1)
    return y, loop_s


# 七床的差别只有调、速度、密度、屋子大小和（东翼那一床）一地不谐和的持续音——
# 同一件乐器，换的是这一程走到哪儿了。
def mus_hall():
    """大厅与书房：人都在一张桌子边上，琴也走音得最明显。"""
    return music_bed(110.0, [(0, (0, 3, 7)), (-4, (0, 4, 7)),
                             (-2, (0, 3, 7)), (3, (0, 4, 7))],
                     bar=8.0, density=1.7, bright=0.85)


def mus_sea():
    """码头、礁石、从海上看宅子：外头没有墙，混响收短、音少留白多。"""
    return music_bed(98.0, [(0, (0, 3, 7)), (5, (0, 3, 7)),
                            (-2, (0, 4, 7)), (3, (0, 3, 7))],
                     bar=9.0, density=1.0, bright=0.7,
                     pad_level=0.30, tail_s=1.8, decay_s=0.8, mix=0.34)


def mus_room():
    """走廊、客房：最小的屋子。根音比大厅抬高二半音（123.5 对 110）——墙离人近，
    屋子小，琴反而往上走，不是往下。"""
    return music_bed(123.5, [(0, (0, 3, 7)), (-3, (0, 4, 7)),
                             (4, (0, 3, 7)), (-5, (0, 4, 7))],
                     bar=7.0, density=1.3, bright=0.8,
                     pad_level=0.30, tail_s=3.2, decay_s=1.4, mix=0.5)


# 另外四床按"这一程走到哪儿了"分，不按地点：同一面大厅墙，第六章坐着对质和第一夜
# 那张过夜卡不是一床。挂在哪张卡上由剧本的 mood 参数说，整段回到二〇二五年时由
# 剧本直接 $ bb_mood("dust")。

def mus_night():
    """过夜：一整个夜里没有人说话。音区压到最低、拨弦最稀、混响最长。"""
    return music_bed(87.3, [(0, (0, 3, 7)), (-5, (0, 3, 7)),
                            (3, (0, 4, 7)), (-2, (0, 3, 7))],
                     bar=11.0, density=0.7, bright=0.65,
                     pad_level=0.26, tail_s=4.2, decay_s=1.9, mix=0.52)


def mus_dread():
    """东翼、真相逼近那一档：多压一地差一个半音的持续音，拍音很慢。
    还是不敲打击乐——一敲就成了恐怖片配乐，这本子的怕来自"有人在说真话"。"""
    return music_bed(103.8, [(0, (0, 3, 7)), (1, (0, 3, 7)),
                             (-4, (0, 4, 7)), (6, (0, 3, 7))],
                     bar=10.0, density=0.6, bright=0.75,
                     pad_level=0.27, tail_s=3.6, decay_s=1.6, mix=0.5,
                     clash=1.0)


def mus_dust():
    """二〇二五年那一头：杭州阅览室翻手稿。屋子是干的——混响最短，
    拨弦密一点、亮一点，近得像贴在纸面上。"""
    return music_bed(146.8, [(0, (0, 3, 7)), (2, (0, 4, 7)),
                             (-3, (0, 3, 7)), (5, (0, 4, 7))],
                     bar=6.0, density=2.0, bright=1.05,
                     pad_level=0.26, tail_s=1.0, decay_s=0.5, mix=0.28)


def mus_end():
    """终章（第二十四章那张卡）：只剩高音区几个孤立的音，尾巴留满。
    不给结论——这本子的结局问题在这份手稿里同样没有答案。"""
    return music_bed(196.0, [(0, (0, 3, 7)), (7, (0, 3, 7)),
                             (3, (0, 4, 7)), (7, (0, 3, 7))],
                     bar=12.0, density=0.45, bright=0.6,
                     pad_level=0.22, note_level=0.42,
                     tail_s=4.8, decay_s=2.4, mix=0.56)


# ---------------- 四个音效 ----------------

def sfx_page(sr=SR_SFX, secs=0.34):
    """翻纸：一段下扫的带通噪声加两粒脆响。"""
    n = int(sr * secs)
    t = np.arange(n) / float(sr)
    x = RNG.standard_normal(n)
    x = np.convolve(x, np.ones(2) / 2.0, mode="same")
    env = np.exp(-t / 0.06) * (1 - np.exp(-t / 0.004))
    y = x * env * 0.9
    for pos, f in ((int(0.05 * sr), 3200), (int(0.17 * sr), 2400)):
        d = int(0.02 * sr)
        tt = np.arange(d) / float(sr)
        y[pos:pos + d] += np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.004) * 0.25
    return finalize(np.stack([y, y * 0.94], axis=1), -11)


def sfx_pick(sr=SR_SFX, secs=0.13):
    """拿起证据：一粒短促的木质敲点。"""
    n = int(sr * secs)
    tt = np.arange(n) / float(sr)
    body = np.sin(2 * np.pi * 780 * tt) * np.exp(-tt / 0.012)
    tick = RNG.standard_normal(n) * np.exp(-tt / 0.003)
    y = body * 0.7 + tick * 0.35
    return finalize(np.stack([y, y], axis=1), -9)


def sfx_stamp(sr=SR_SFX, secs=0.55):
    """盖章：低频一闷，带一点桌面的回响。这是"话说完了"的声音。"""
    n = int(sr * secs)
    tt = np.arange(n) / float(sr)
    thud = np.sin(2 * np.pi * 74 * tt) * np.exp(-tt / 0.10)
    knock = np.sin(2 * np.pi * 300 * tt) * np.exp(-tt / 0.022) * 0.5
    air = np.convolve(RNG.standard_normal(n), np.ones(6) / 6.0, mode="same") \
        * np.exp(-tt / 0.008) * 0.4
    y = thud * 0.85 + knock + air
    return finalize(np.stack([y, y * 0.97], axis=1), -7)


def sfx_silence(sr=SR_SFX, secs=0.7):
    """逼出一处沉默：盖章之后压下去的那口风。"""
    n = int(sr * secs)
    tt = np.arange(n) / float(sr)
    glide = 2 * np.pi * np.cumsum(190 - 100 * tt) / float(sr)
    tone = np.sin(glide) * np.exp(-tt / 0.22) * 0.8
    damp = np.convolve(RNG.standard_normal(n), np.ones(12) / 12.0, mode="same") \
        * np.exp(-tt / 0.05) * 0.35
    y = tone + damp
    return finalize(np.stack([y, y * 0.98], axis=1), -9)


LOOPS = {"amb_sea": sea, "amb_wind": wind, "amb_rain": rain, "amb_room": room,
         "amb_night": night, "amb_dust": dust}
MUS = {"mus_hall": mus_hall, "mus_sea": mus_sea, "mus_room": mus_room,
       "mus_night": mus_night, "mus_dread": mus_dread,
       "mus_dust": mus_dust, "mus_end": mus_end}
SFX = {"sfx_page": sfx_page, "sfx_pick": sfx_pick,
       "sfx_stamp": sfx_stamp, "sfx_silence": sfx_silence}

# 目标响度（RMS，dBFS）。定这几个数的理由是"在对白底下"：人声那一路的 mp3
# 大致在 -18dBFS，音乐槽默认还压到 0.5（-6dB），所以 -30 上下的床翻出来是
# 比人声低三十档，听得到、压不住话。room 最轻——静场那一章要的就是"静得
# 能听见茶凉了"；sea 最响，因为正文里那句"海浪撞击礁石"是明写在纸上的。
AMB_RMS_DB = {"amb_sea": -32.0, "amb_wind": -33.0, "amb_rain": -34.0,
              "amb_room": -37.0, "amb_night": -33.0, "amb_dust": -36.0}
MUS_RMS_DB = {"mus_hall": -30.0, "mus_sea": -32.0, "mus_room": -32.0,
              "mus_night": -32.0, "mus_dread": -31.0, "mus_dust": -32.0,
              "mus_end": -31.0}

_trap = getattr(np, "trapezoid", None) or np.trapz

# 质心上限。十三条的上限留在各自实测值的 1.4–2.5 倍——够松，改一改泡沫的多少
# 不至于天天红；够紧，单位一退化就撞线：白噪声在 22k 采样下质心 5.5k，比最松的
# rain（2600）还高 2.1 倍，比最紧的 dust（180）高 31 倍。
# 它防的是"退化成白噪声"这一档，防不住"只是偏亮了一点"——那一档归耳朵。
CEN_MAX = {"amb_sea": 1400.0, "amb_wind": 800.0, "amb_rain": 2600.0,
           "amb_room": 300.0, "amb_night": 400.0, "amb_dust": 180.0,
           "mus_hall": 1200.0, "mus_sea": 1200.0,
           "mus_room": 1200.0, "mus_night": 1000.0, "mus_dread": 1100.0,
           "mus_dust": 1600.0, "mus_end": 1500.0}


def analyze(x, sr):
    """响不响（rms/peak，dBFS）和亮不亮（频谱质心，Hz）。

    质心是这一版新加的那道闸：22k 采样下的白噪声质心就是 5.5k（奈奎斯特的一半），
    而"很安静的岛"应当在几百赫兹。上一版频谱整形传错了单位，四条全退化成白噪声，
    盘上、lint 上、截图上全都看不出来——只有耳朵听得出来，于是半年没人抓到。
    """
    from scipy import signal
    a = np.asarray(x, dtype=np.float64)
    rms = float(np.sqrt(np.mean(a ** 2)))
    pk = float(np.max(np.abs(a)))
    f, P = signal.welch(a.mean(axis=1) if a.ndim > 1 else a, sr, nperseg=2048)
    cen = float(_trap(P * f, f) / (_trap(P, f) + 1e-20))
    return 20 * np.log10(rms + 1e-20), 20 * np.log10(pk + 1e-20), cen


def check_bed(name, x, sr, target_db):
    """一床循环合格不合格：不能太响、不能太轻、更不能是白噪声。

    这里**没有**接缝闸门，是量过之后撤的，不是没顾上。两种候选都试过：
      · 跨接缝那一步的斜率 / 其余部分 99.9 分位——十三床实测 0.02–0.41，而故意
        做的"后半整体降 3dB"（循环点一个台阶）只有 0.12，"中间抠六个样本"0.11。
        做坏的那两条比最干净的好床还低：噪声本来就逐点乱跳，台阶藏在分布里，量不出来。
      · 首尾窗口的功率差 / 全条平均——窗口取 1s/2s/4s/6s 都试过：amb_sea 自己
        就有 2.32（慢涌的三次方让泡沫成团，那是浪，不是缝），故意做坏的那条才
        1.46。分不开好坏的数不能当闸，只会给人假安全感。
    无缝是**构造**保证的：包络只用整数周期、拨弦落在 1/4 拍网格上、尾巴圆周绕回、
    混响圆周卷积。改坏这四条里的任何一条，接缝是耳朵听得见的——那就由耳朵管。
    """
    rms, _, cen = analyze(x, sr)
    bad = []
    if cen > CEN_MAX[name]:
        bad.append("质心 %.0fHz 高于 %.0fHz（听着就是沙沙，不是环境）" % (cen, CEN_MAX[name]))
    if rms > target_db + 3.0:
        bad.append("RMS %.1fdBFS 比目标 %.1f 响了 %.1f，会盖对白"
                   % (rms, target_db, rms - target_db))
    if rms < target_db - 6.0:
        bad.append("RMS %.1fdBFS 比目标 %.1f 轻了 %.1f，等于没有"
                   % (rms, target_db, target_db - rms))
    if bad:
        raise SystemExit("%s 不合格：" % name + "；".join(bad))
    return rms, cen



def main():
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    total = 0
    for tag, table, sr, targets in (("LOOP", LOOPS, SR_LOOP, AMB_RMS_DB),
                                    ("MUS", MUS, SR_MUS, MUS_RMS_DB)):
        for name, fn in table.items():
            y, secs = fn()
            wav = finalize_loud(y, targets[name])
            rms, cen = check_bed(name, wav.astype(np.float64) / 32767.0, sr,
                                 targets[name])
            path = os.path.join(OUT, name + ".wav")
            size = write_wav(path, wav, sr)
            total += size
            print("%s  %-9s %4.1fs  %6.2f MB  rms %5.1f dB  质心 %5.0f Hz"
                  % (tag, name, secs, size / 1048576.0, rms, cen))
    for name, fn in SFX.items():
        y = fn()
        path = os.path.join(OUT, name + ".wav")
        size = write_wav(path, y, SR_SFX)
        total += size
        print("SFX  %-9s %4.2fs  %6.1f KB" % (name, len(y) / float(SR_SFX),
                                              size / 1024.0))
    print("total %.2f MB" % (total / 1048576.0))


if __name__ == "__main__":
    sys.exit(main())
