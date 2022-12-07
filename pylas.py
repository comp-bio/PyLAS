# -*- coding: utf-8 -*-
import sys, os, itertools
import numpy as np
import pywt

# 2^14 constants:
fft_trd = 10
fft_std = 289.49012689247957
fft_Q95 = 3510.6100249999977
dtt_grid = [8.1858,8.8536,8.8958,8.9203,8.938,8.9518,8.9629,8.972,8.98,8.9872,8.9935,8.9991,9.0044,9.0092,9.0137,9.018,9.0219,9.0257,9.0293,9.0327,9.0359,9.039,9.0419,9.0447,9.0474,9.05,9.0526,9.055,9.0573,9.0595,9.0618,9.0639,9.066,9.068,9.0701,9.072,9.0739,9.0758,9.0776,9.0794,9.0812,9.0829,9.0846,9.0862,9.0878,9.0894,9.091,9.0925,9.094,9.0956,9.097,9.0985,9.0999,9.1014,9.1028,9.1041,9.1055,9.1069,9.1083,9.1097,9.111,9.1123,9.1137,9.115,9.1163,9.1176,9.119,9.1203,9.1216,9.123,9.1244,9.1257,9.1271,9.1286,9.13,9.1316,9.1332,9.1348,9.1365,9.1383,9.1403,9.1424,9.1447,9.1474,9.1507,9.1549,9.1608,9.1688,9.1775,9.1859,9.1943,9.2024,9.2103,9.2183,9.2261,9.2334,9.2403,9.2468,9.2529,9.2595]

def normal(v):
    if v < dtt_grid[0]: return fft_trd
    if v > dtt_grid[-1]: return 0
    for i in range(len(dtt_grid) - 1):
        if dtt_grid[i] > v or v > dtt_grid[i+1]: continue
        return (1 - (i + (v - dtt_grid[i])/(dtt_grid[i+1] - dtt_grid[i]))/(len(dtt_grid) - 1)) * fft_trd

def join(fft_v, dtt_v):
    if fft_v < fft_Q95: return normal(dtt_v)
    return (fft_v - fft_Q95)/fft_std + fft_trd


Faf = np.array([[
    [ 0.00000000,  0.00000000], [-0.08838835, -0.01122679], [ 0.08838835,  0.01122679], [ 0.69587999,  0.08838835], [ 0.69587999,  0.08838835],
    [ 0.08838835, -0.69587999], [-0.08838835,  0.69587999], [ 0.01122679, -0.08838835], [ 0.01122679, -0.08838835], [ 0.00000000,  0.00000000]
],[
    [ 0.01122679,  0.00000000], [ 0.01122679,  0.00000000], [-0.08838835, -0.08838835], [ 0.08838835, -0.08838835], [ 0.69587999,  0.69587999],
    [ 0.69587999, -0.69587999], [ 0.08838835,  0.08838835], [-0.08838835,  0.08838835], [ 0.00000000,  0.01122679], [ 0.00000000, -0.01122679]
]])

af = np.array([[
    [ 0.03516384,  0.00000000], [ 0.00000000,  0.00000000], [-0.08832942, -0.11430184], [ 0.23389032,  0.00000000], [ 0.76027237,  0.58751830],
    [ 0.58751830, -0.76027237], [ 0.00000000,  0.23389032], [-0.11430184,  0.08832942], [ 0.00000000,  0.00000000], [ 0.00000000, -0.03516384],
],[
    [ 0.00000000, -0.03516384], [ 0.00000000,  0.00000000], [-0.11430184,  0.08832942], [ 0.00000000,  0.23389032], [ 0.58751830, -0.76027237],
    [ 0.76027237,  0.58751830], [ 0.23389032,  0.00000000], [-0.08832942, -0.11430184], [ 0.00000000,  0.00000000], [ 0.03516384,  0.00000000]
]])


def convolve(x, y):
    nx, ny = (len(x), len(y))
    X, Y = (np.pad(x, [ny - 1, 0]), np.pad(y, [0, nx - 1]))
    return np.fft.ifft(np.fft.fft(X) * np.fft.fft(Y)).real # Normalization is already built in np.fft.ifft


def afb_(x, af_i, N, L):
    lo = convolve(x, af_i)
    lo = np.roll(lo, -(2 * L - 1))
    lo = lo[range(0, len(lo), 2)]
    lo[np.arange(L)] = lo[int(N/2) + np.arange(L)] + lo[np.arange(L)]
    return lo[np.arange(int(N/2))]


def afb(x, af):
    N, L = (len(x), int(len(af)/2))
    x = np.roll(x, -L)
    return (afb_(x, af[:,0], N, L), afb_(x, af[:, 1], N, L)) # (lo, hi)


def dualtree(x, J, Faf, af):
    x = x/np.sqrt(2)
    w = [[None, None] for i in range(J + 1)]
    for k in [0, 1]:
        lo, hi = afb(x, Faf[k])
        w[0][k] = hi
        for j in range(1, J):
            lo, w[j][k] = afb(lo, af[k])
        w[J][k] = lo
    return w


def shannon_entropy(v):
    s = v.sum()
    if s > 0: v = v/sum(v)
    if v.sum() < 1e-300: return 0
    v[v == 0] = 1
    return -(v * np.log(v)).sum()


def echo(text, color='37'):
    sys.stdout.write("\033[1;%sm%s\033[m" % (color, text))


def err(text, color='37'):
    sys.stderr.write("\033[1;%sm%s\033[m" % (color, text))


def bcov(file, start=0):
    with open(file, 'rb') as f:
        f.seek(start * 2)
        while True:
            value = f.read(2)
            if not value: break
            yield value[0] * 256 + value[1]


def DWT_Energy_Entropy(x):
    RE_wd = np.array([sum(i**2) for i in pywt.wavedec(x, 'haar')[1:]])
    return shannon_entropy(RE_wd)


def DWT_L(x, l=4):
    RE_wd = np.array([sum(i**2) for i in pywt.wavedec(x, 'haar', level=l)[1:]])
    return shannon_entropy(RE_wd)


def DTCWT_Entropy(x, J=4):
    obj = dualtree(x, J, Faf, af)
    M = [np.sqrt(l[0] ** 2 + l[1] ** 2) for l in obj[0:J]]
    return shannon_entropy(np.array([item for sublist in M for item in sublist]))


def FFT_dF(x):
    G = abs(np.fft.fft(x)) ** 2
    E = G.sum()
    F0 = sum(np.arange(len(G)) * G / E)
    dF = np.sqrt(((np.arange(len(G)) - F0)**2 * G / E).sum())
    return (dF, dF/F0)


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    if len(sys.argv) < 2:
        err('Usage:\n')
        err('  python3 %s [chromosome.bcov]\n' % sys.argv[0])
        err('Example:\n')
        err('  python3 %s chr11.bcov\n' % sys.argv[0])
        err('Output columns:\n')
        err('  Chromosome_name Start End FFT_dF DTCWT_Entropy LAS Description\n\n')
        sys.exit(1)

    line = 1
    src, cnt = (bcov(sys.argv[1]), 2**int(sys.argv[2]))
    chr_name = os.path.basename(sys.argv[1]).replace('.bcov', '')

    while True:
        block = list(itertools.islice(src, cnt))
        if not block: break
        x = np.array(block)
        sys.stdout.write("%s %d %d " % (chr_name, line, line + cnt - 1))
        line += cnt
        if x.sum() == 0:
            sys.stdout.write("-1 -1 -1 no_coverage\n")
        else:
            fft_in, fft_in_n = FFT_dF(x)
            dt_in = DTCWT_Entropy(x)
            j = join(fft_in, dt_in)
            txt = 'aberrant' if j > fft_trd else 'good'
            sys.stdout.write("%.6f %.6f %.6f %s\n" % (fft_in, dt_in, j, txt))
