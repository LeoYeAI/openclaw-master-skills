#!/usr/bin/env python3
"""Build speaker timeline from two ROI motion files.

Usage: analyze.py LEFT_MOTION.txt RIGHT_MOTION.txt [MIN_DUR]
Stdout: JSON segments. Stderr: count summary.
"""
import re, json, sys

def parse(path):
    times, vals = [], []
    cur_t = None
    with open(path) as f:
        for line in f:
            m = re.match(r"frame:\d+\s+pts:\d+\s+pts_time:([0-9.]+)", line)
            if m:
                cur_t = float(m.group(1)); continue
            m = re.match(r"lavfi\.signalstats\.YAVG=([0-9.]+)", line)
            if m and cur_t is not None:
                times.append(cur_t); vals.append(float(m.group(1))); cur_t = None
    return times, vals

LZ = sys.argv[1]
DZ = sys.argv[2]
MIN_DUR = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0

t_l, v_l = parse(LZ)
t_d, v_d = parse(DZ)
assert len(v_l) == len(v_d), f"len mismatch: {len(v_l)} vs {len(v_d)}"

def norm(v):
    m = sum(v) / max(len(v), 1)
    return [x / m if m > 0 else 0 for x in v]

n_l = norm(v_l); n_d = norm(v_d)

WIN = 15
def smooth(v):
    out = []
    for i in range(len(v)):
        a = max(0, i - WIN // 2); b = min(len(v), i + WIN // 2 + 1)
        out.append(sum(v[a:b]) / (b - a))
    return out

s_l = smooth(n_l); s_d = smooth(n_d)

MARGIN = 1.15
speaker = []
cur = 0 if s_l[0] >= s_d[0] else 1
for i in range(len(s_l)):
    if cur == 0 and s_d[i] > s_l[i] * MARGIN: cur = 1
    elif cur == 1 and s_l[i] > s_d[i] * MARGIN: cur = 0
    speaker.append(cur)

fps = 30.0
segments = []
i = 0
while i < len(speaker):
    j = i
    while j + 1 < len(speaker) and speaker[j + 1] == speaker[i]:
        j += 1
    segments.append({"start": i / fps, "end": (j + 1) / fps,
                     "speaker": "left" if speaker[i] == 0 else "right"})
    i = j + 1

merged = []
for seg in segments:
    if merged and (seg["end"] - seg["start"]) < MIN_DUR:
        merged[-1]["end"] = seg["end"]
    else:
        merged.append(seg)

collapsed = []
for seg in merged:
    if collapsed and collapsed[-1]["speaker"] == seg["speaker"]:
        collapsed[-1]["end"] = seg["end"]
    else:
        collapsed.append(seg)

print(json.dumps(collapsed, indent=2))
print(f"{len(collapsed)} segments, total {collapsed[-1]['end']:.2f}s", file=sys.stderr)
