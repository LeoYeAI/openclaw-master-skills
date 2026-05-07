#!/usr/bin/env python3
"""Build ffmpeg crop x-expression for hard-cut speaker pan.

Usage: build_pan.py SEGMENTS.json LEFT_X RIGHT_X
Stdout: ffmpeg expression suitable for crop=W:H:x='EXPR':y=0
"""
import json, sys

segs = json.load(open(sys.argv[1]))
LEFT_X = int(sys.argv[2])
RIGHT_X = int(sys.argv[3])

def x_for(s): return LEFT_X if s == "left" else RIGHT_X

expr = str(x_for(segs[-1]["speaker"]))
for seg in reversed(segs[:-1]):
    expr = f"if(lt(t\\,{seg['end']:.4f})\\,{x_for(seg['speaker'])}\\,{expr})"
print(expr)
