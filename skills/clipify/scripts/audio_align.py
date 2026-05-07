#!/usr/bin/env python3
"""Find time offset of a short clip within a longer source via FFT cross-correlation.

Usage: audio_align.py CLIP_PCM SRC_PCM SRC_WINDOW_OFFSET_S
Both files must be int16 mono PCM at 8000 Hz.
SRC_WINDOW_OFFSET_S is the absolute time of the start of SRC_PCM in the original source.
Stdout: absolute offset (seconds) of CLIP_PCM start within the original source.
"""
import numpy as np, sys

SR = 8000
clip = np.fromfile(sys.argv[1], dtype=np.int16).astype(np.float32)
src = np.fromfile(sys.argv[2], dtype=np.int16).astype(np.float32)
window_off = float(sys.argv[3])

clip = (clip - clip.mean()) / (clip.std() + 1e-9)
src = (src - src.mean()) / (src.std() + 1e-9)

n = len(src) + len(clip)
p = 1
while p < n: p *= 2
S = np.fft.rfft(src, p)
C = np.fft.rfft(clip[::-1], p)
corr = np.fft.irfft(S * C, p)[:n-1]
peak = int(np.argmax(corr))
offset_in_window = (peak - (len(clip) - 1)) / SR
print(f"{window_off + offset_in_window:.3f}")
