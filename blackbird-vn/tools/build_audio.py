# -*- coding: utf-8 -*-
"""给《黑鸟岛》合成一层环境音和几个音效，全部程序生成，不找素材。

为什么不用现成的录音：这本子要的是"很安静的岛"——海浪压得很低，风只在大厅
外面，雨只在窗外。这种素材在网上找十有八九是"海洋纪录片片头"，一放就把
推理氛围压成风光片。自己合成能把频谱和包络都钉死在想要的程度上。

生成方法：色噪声用频谱法（随机相位 × 目标功率谱），这样出来的序列天生按整
个缓冲区周期，接头就是无缝循环——滤波器如果直接在时域做，两头必然甩出接缝。
雨点和纸响这类瞬态用指数衰减的小段噪声铺上去，铺的时候避开首尾，接缝附近
少两滴听不出来。

    python blackbird-vn/tools/build_audio.py

产出 game/audio/：四条循环（sea/wind/rain/room）+ 四个音效（page/pick/stamp/silence）。
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
    mag = shape(freqs / float(sr))
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


def write_wav(path, x, sr):
    from scipy.io import wavfile
    wavfile.write(path, sr, x)
    return os.path.getsize(path)


# ---------------- 四条环境循环 ----------------

def sea(sr=SR_LOOP, secs=24.0):
    """碎浪：棕色噪声打底 + 一道慢涌 + 一点高频泡沫。"""
    n = int(sr * secs)
    bed = colored_loop(n, sr, lowpass_shape(320, 2.5))
    foam = colored_loop(n, sr, bandpass_shape(1200, 4500, 1.5))
    surge = swell(n, sr, [(1, 1.0), (2, 0.45), (5, 0.22)], 0.85, base=1.0)
    y = bed * surge[:, None] * 0.9 + foam * (surge[:, None] ** 3) * 0.10
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
    y = y + hiss * (g1[:, None] ** 2) * 0.12
    return y, secs


def rain(sr=SR_LOOP, secs=20.0):
    """窗外雨：高频沙沙 + 滴答 + 极低频的湖面底。"""
    n = int(sr * secs)
    hiss = colored_loop(n, sr, bandpass_shape(900, 6000, 1.2))
    low = colored_loop(n, sr, lowpass_shape(160, 3.0))
    e = swell(n, sr, [(2, 1.0), (5, 0.5), (11, 0.25)], 0.25, base=1.0)
    y = hiss * e[:, None] * 0.7 + low * 0.35
    return add_bursts(y, sr, 7.0, 0.05, (1400, 4200), 0.10), secs


def room(sr=SR_LOOP, secs=26.0):
    """静场底：阅览室与大厅。压得很低的空调嗡鸣加一点点木头的响动。"""
    n = int(sr * secs)
    bed = colored_loop(n, sr, lowpass_shape(220, 3.5))
    e = swell(n, sr, [(1, 1.0), (4, 0.3)], 0.10, base=1.0)
    y = bed * e[:, None] * 0.5
    return add_bursts(y, sr, 0.35, 0.10, (260, 900), 0.05), secs


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


LOOPS = {"amb_sea": sea, "amb_wind": wind, "amb_rain": rain, "amb_room": room}
SFX = {"sfx_page": sfx_page, "sfx_pick": sfx_pick,
       "sfx_stamp": sfx_stamp, "sfx_silence": sfx_silence}


def seam(x, sr):
    """接缝检查：循环点两侧的"响度"对不对得上。

    噪声样本本身逐点乱跳，比 x[0] 和 x[-1] 没有意义；有意义的是包络。
    取 0.2 秒窗口的滑动均方根，看首尾两段的差相对于它自己的起伏有多大。
    包络是整数周期的话，这个值应当远小于 1。"""
    w = max(1, int(0.2 * sr))
    power = np.mean(np.asarray(x, dtype=np.float64) ** 2, axis=1)
    env = np.convolve(power, np.ones(w) / float(w), mode="valid")
    k = min(w, len(env) // 2)
    return float(abs(np.mean(env[:k]) - np.mean(env[-k:])) / (np.std(env) + 1e-12))


def main():
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    total = 0
    for name, fn in LOOPS.items():
        y, secs = fn()
        path = os.path.join(OUT, name + ".wav")
        size = write_wav(path, finalize(y, -14), SR_LOOP)
        total += size
        print("LOOP %-9s %4.1fs  %6.2f MB  seam %.3f"
              % (name, secs, size / 1048576.0, seam(y, SR_LOOP)))
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
