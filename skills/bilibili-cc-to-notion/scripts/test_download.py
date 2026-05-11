#!/usr/bin/env python3
"""
测试字幕下载工具
"""

import subprocess
import json
import sys


def test_download():
    """测试字幕下载"""
    print("测试BBDown字幕下载工具...")
    print("-" * 50)

    # 测试BBDown是否存在
    try:
        result = subprocess.run(
            ["/tmp/BBDown", "--help"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            print("✅ BBDown 已安装")
        else:
            print("❌ BBDown 未正确安装")
            return False
    except Exception as e:
        print(f"❌ 检查BBDown时出错: {e}")
        return False

    # 测试FFmpeg
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            print("✅ FFmpeg 已安装")
        else:
            print("❌ FFmpeg 未正确安装")
            return False
    except Exception as e:
        print(f"❌ 检查FFmpeg时出错: {e}")
        return False

    print("-" * 50)
    print("工具检查完成！")
    print("\n现在可以使用下载脚本：")
    print("python3 download_bilibili_cc.py --url <B站视频URL> --output <输出目录>")
    print("\n示例：")
    print(
        "python3 download_bilibili_cc.py --url https://www.bilibili.com/video/BV1xx411c7mW --output /tmp/subtitles"
    )


if __name__ == "__main__":
    test_download()
