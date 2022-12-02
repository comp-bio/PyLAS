# Usage:
#   python3 synthetic_aberration.py [best_regions.json] [mean coverage] [type] [scale]
# Example:
#   python3 synthetic_aberration.py ../../data/generated/real_good.json 272 DEL 1

import sys, json
import numpy as np
from pylas import *

good = sys.argv[1]        # Good regions .json
mean = float(sys.argv[2]) # Mean coverage for regions
aber = sys.argv[3]        # Aberration type: [DEL, DUP, Noise]
levl = float(sys.argv[4]) # Aberration scale

with open(good, 'r') as f:
    regions = json.load(f)

with open('../../data/generated/real_noise.json', 'r') as f:
    real_noise_sig = json.load(f)

# ---------------------------------------------------------------------------- #
def atans(center, size, T, L=2**14):
    left, right = (center - size/2, center + size/2)
    x = np.arange(0, L, 1)
    return np.array([1 - (np.arctan(i-left)/(np.pi) + 0.5) * (np.arctan(-(i-right))/(np.pi) + 0.5) * T for i in x])

def mNoise(src, noise, center, size):
    t = atans(center, size, 1)
    return t * src + (1 - t) * noise

def mDEL(src, center, size, k=0.8):
    noise = [max(0, int(v)) for v in (src - np.mean(src) * k)]
    return mNoise(src, noise, center, size)

def mDUP(src, center, size, k=-1):
    return atans(center, size, k) * src

def modify(signal, center, size):
    if aber == 'DEL':
        return mDEL(signal, center, size, levl)
    if aber == 'DUP':
        return mDUP(signal, center, size, levl)
    if aber == 'Noise':
        return mNoise(signal, real_noise_sig[np.random.randint(len(real_noise_sig))], center, size)

# ---------------------------------------------------------------------------- #
outp = good.replace('.json', '') + f'_{aber}_{abs(levl)}.json'

step  = 2**10
sizes = 2**np.arange(7, 14)

if aber == "Noise":
    sizes = [32, 64, 96, 128, 192, 256, 384, 512]

res = []
for i, s in enumerate(regions):
    sys.stderr.write("\033[1;%sm%s\033[m" % (37, f"{i+1}/{len(regions)}\r"))
    fft, fft_n = FFT_dF(s)
    dtt = DTCWT_Entropy(s)
    res.append([0, float(fft), float(fft_n), float(dtt)])
    for size in sizes:
        for center in np.arange(0, 2**14, step):
            s_mod = modify(np.array(s)/mean, center, size)
            fft, fft_n = FFT_dF(s_mod)
            dtt = DTCWT_Entropy(s_mod)
            res.append([int(size), float(fft), float(fft_n), float(dtt)])
    with open(outp, 'w') as f:
        json.dump(res, f)

print(f"\nDone: {outp}")
