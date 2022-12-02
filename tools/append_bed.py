# -*- coding: utf-8 -*-
import sys, os, math
from statistics import mean, variance


def echo(text, color='37'):
    sys.stdout.write("\033[1;%sm%s\033[m" % (color, text))


def err(text, color='37'):
    sys.stderr.write("\033[1;%sm%s\033[m" % (color, text))


def get_lines(path):
    with open(path) as f:
        content = f.readlines()
    for line in content:
        if line == "": continue
        yield line.replace('\n', '').replace(' ', '\t').split('\t')


def bed_data(path):
    data = {}
    for cols in get_lines(path):
        if cols[0][0] == '#': continue
        chr = cols[0].replace('"', '', 2).replace('MT', 'M')
        if chr not in data: data[chr] = {'index': 0, 'items': []}
        data[chr]['items'].append([int(v) for v in cols[1:]])
    return data


def bcov(file, start=0, default=None):
    with open(file, 'rb') as f:
        f.seek(start * 2)
        while True:
            v = f.read(2)
            if not v or len(v) == 0:
                yield default
                continue
            yield v[0] * 256 + v[1]


def moments(block):
    cb = (len(block) - block.count(0)) / len(block)
    m = mean(block)
    vr = variance(block)
    m3 = mean([(x - m) ** 3 for x in block])
    s3 = math.sqrt(mean([(x - m) ** 2 for x in block]) ** 3)
    sk = (0 if s3 == 0 else m3 / s3)
    return [cb, m, vr, sk]


def intersection(beg_top, end_top, beg_bottom, end_bottom):
    if end_top < beg_bottom: return 'L', 0
    if beg_top > end_bottom: return 'R', 0
    return 'I', (min(end_top, end_bottom) - max(beg_top, beg_bottom) + 1)


def intersect(chrdata, start, stop):
    i = chrdata['index']
    bases = 0
    while i < len(chrdata['items']):
        cls, value = intersection(chrdata['items'][i][0], chrdata['items'][i][1], start, stop)
        if cls == 'R': break
        if cls == 'L': chrdata['index'] = i
        bases += value
        i += 1
    return bases/(stop - start + 1)


# --------------------------------------------------------------------------- #
bed = {}
options = {'las': None, 'cov': None}
for inp in sys.argv[1:]:
    k, v = inp.split(':')
    if k in options:
        options[k] = v
    else:
        bed[k] = bed_data(v)

# --------------------------------------------------------------------------- #
if options['cov'] is None or options['las'] is None:
    echo('Usage:   python3 %s \\\n' % sys.argv[0])
    echo('         cov:[binary coverage root dir] \\\n')
    echo('         las:[calculated LAS score] \\\n')
    echo('         [col_name]:[bed_file]\n')
    echo('Example: python3 %s cov:./coverage las:HG001.las\n\n' % sys.argv[0])
    sys.exit(1)

cov_files = {}
src = get_lines(options['las'])
head = next(src)

print(" ".join(head + ['covered_bases', 'mean', 'variance', 'skewness'] + [name for name in bed]))
for line in src:
    obj = dict(zip(head, line))
    l, r = (int(obj['start']), int(obj['end']))
    bc = bcov(f"{options['cov']}/{obj['#chr']}.bcov", l-1, 0)
    block = [next(bc) for i in range(r - l + 1)]
    data = ['{:.4f}'.format(v) for v in moments(block)]
    for name in bed:
        inter = 'NA'
        if obj['#chr'] in bed[name]:
            v = intersect(bed[name][obj['#chr']], l-1, r)
            inter = '{:.4f}'.format(v)
        data.append(inter)
    print(" ".join(line + data))
