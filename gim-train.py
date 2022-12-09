# -*- coding: utf-8 -*-
import sys
import numpy as np
import json


def get_lines(path):
    with open(path) as f:
        content = f.readlines()
    for line in content:
        if line == "": continue
        yield line.replace('\n', '').replace(' ', '\t').split('\t')


range  = (500, 9000)
limits = (500, 4000)
sample = get_lines(sys.argv[1])
header = next(sample)

values = []
for line in sample:
    obj, val = dict(zip(header, line)), float(line[3])
    if 'fft' in obj: val = float(obj['fft'])
    if 'FFT_dF' in obj: val = float(obj['FFT_dF'])
    if val < limits[0] or val > limits[1]: continue
    values.append(val)

hist = np.histogram(values, bins=400, range=range, density=True)[0]

with open('gim.py') as f:
    content = f.read().split('# TRAINED\n')
    content[1]  = "trained_mean = %f\n" % np.mean(values)
    content[1] += "trained = np.array(%s)\n" % json.dumps(hist.tolist())

with open('gim.py', 'w') as f:
    f.write("# TRAINED\n".join(content))

print("Done!")
