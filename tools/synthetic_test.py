import sys, json
import numpy as np
from pylas import *


good = sys.argv[1] # data/GIAB/the_best_of_the_best_regions.json
size = int(sys.argv[2])
outp = sys.argv[3] # data/GIAB/filename.json

fft_m, fft_s = (1783.7347186000002, 263.58889402976223)
dtt_m, dtt_s = (9.111856, 0.06325841730085836)
(dx, dy, scale) = (-1.232, 0.324, 0.072)

with open(good, 'r') as f:
    sig = json.load(f)
with open('../results/_matrix.n1b.json', 'r') as f:
    mat, xar, yar = [np.array(e) for e in json.load(f)]


def modify(s, size, position):
    l, r = (position - size/2, position + size/2)
    xx = np.arange(0, len(s), 1)
    yy = [1 - (np.arctan(i-l)/(np.pi) + 0.5) * (np.arctan(-(i-r))/(np.pi) + 0.5) * 0.75 for i in xx]
    return s * np.array(yy)


def m_index(obj, v):
    if obj[0]  > v: return -2
    if obj[-1] < v: return -1
    return np.where(obj <= v)[0][-1]


def matrix(x, y):
    i, j = (m_index(xar, x), m_index(yar, y))
    if i == -2 or j == -2: return np.max(mat)
    if i == -1 or j == -1: return np.min(mat)
    return float(mat[i][j])  


def LC(x, y):
    return (scale * (x + dx)**2 + (y + dy)**2)


res = []
step = 256                 # Шаг скользящего окна
mean = 272                 # Нормировка покрытия на среднее
# 'size', 'index', 'position', 'FFT_dF', 'DTCWT_Entropy', 'matrix', 'LC'
for i, s in enumerate(sig):
    sys.stderr.write("\033[1;%sm%s\033[m" % (37, f"{i+1}/{len(sig)}\r"))
    for position in np.arange(0, 2**14, step):
        s_mod = modify(np.array(s)/mean, size, position)
        fft, dtt = ((FFT_dF(s_mod) - fft_m)/fft_s, -(DTCWT_Entropy(s_mod) - dtt_m)/dtt_s)
        res.append([np.std(s_mod), fft, dtt, matrix(fft, dtt), LC(fft, dtt)])

with open(outp, 'w') as f:
    json.dump(res, f)
print("\nDone")