#!/usr/bin/env python3
"""XGO播放背景音乐(Dream.mp3)"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
import subprocess
import signal

MUSIC_FILE = "/home/pi/RaspberryPi-CM5/common/music/Dream.mp3"

def main():
    if not os.path.exists(MUSIC_FILE):
        print(f"错误: 音乐文件不存在 {MUSIC_FILE}")
        return
    
    print(f"开始播放音乐: {MUSIC_FILE}")
    print("按 Ctrl+C 停止播放")
    
    try:
        # -really-quiet 抑制日志输出
        proc = subprocess.Popen(
            f"mplayer -really-quiet {MUSIC_FILE}",
            shell=True,
            preexec_fn=os.setsid
        )
        proc.wait()
        print("音乐播放完毕")
    except KeyboardInterrupt:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        print("\n已停止播放")

if __name__ == '__main__':
    main()
