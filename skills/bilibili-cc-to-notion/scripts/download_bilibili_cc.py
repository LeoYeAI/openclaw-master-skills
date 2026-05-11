#!/usr/bin/env python3
"""
下载B站视频CC字幕工具
使用BBDown下载字幕

核心原理：
1. 使用BBDown的--sub-only选项只下载字幕
2. BBDown会自动处理B站的反爬虫检测
3. 下载的字幕文件为SRT格式
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any


def check_bbdown():
    """检查BBDown是否可用"""
    try:
        # 尝试多种BBDown路径
        bbdown_paths = [
            "/tmp/BBDown",
            "./BBDown",
            "BBDown",
            "/usr/local/bin/BBDown",
            "/usr/bin/BBDown",
        ]

        for path in bbdown_paths:
            try:
                result = subprocess.run(
                    [path, "--help"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return path
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

        print("BBDown未找到，请下载并放置到以下位置之一：")
        print("- /tmp/BBDown")
        print("- 当前目录")
        print("- /usr/local/bin/")
        print("\n下载地址：https://github.com/nilaoda/BBDown/releases")
        return None

    except Exception as e:
        print(f"检查BBDown时出错: {e}")
        return None


def get_video_info(bbdown_path: str, url: str) -> Dict[str, Any]:
    """获取视频信息"""
    try:
        cmd = [bbdown_path, url, "-info"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            return {}

        return {"success": True, "raw_output": result.stdout}

    except Exception as e:
        print(f"获取视频信息失败: {e}")
        return {"success": False}


def download_subtitles(bbdown_path: str, url: str, output_dir: str) -> Dict[str, Any]:
    """使用BBDown下载字幕"""
    try:
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # BBDown命令：只下载字幕
        # 注意：必须使用 --skip-ai false，否则会跳过AI字幕下载
        cmd = [
            bbdown_path,
            url,
            "--sub-only",  # 只下载字幕
            "--skip-ai",  # 不禁用AI字幕下载
            "false",
            "--work-dir",
            str(output_path),  # 工作目录
        ]

        print(f"执行命令: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        # 检查输出，看看是否有字幕信息
        if "字幕" in result.stdout or "subtitle" in result.stdout.lower():
            print("检测到字幕相关信息")

        # 查找下载的字幕文件
        subtitle_files = list(output_path.glob("*.srt"))
        if not subtitle_files:
            subtitle_files = list(output_path.glob("*.ass"))

        if not subtitle_files:
            # 检查是否有子目录
            for subdir in output_path.iterdir():
                if subdir.is_dir():
                    subtitle_files.extend(subdir.glob("*.srt"))
                    subtitle_files.extend(subdir.glob("*.ass"))

        if subtitle_files:
            return {
                "success": True,
                "subtitle_files": [str(f) for f in subtitle_files],
                "output_dir": str(output_path),
                "stdout": result.stdout,
                "message": "字幕下载成功",
            }
        else:
            # 检查是否是因为视频没有字幕
            if "尚未登录" in result.stdout:
                return {
                    "success": False,
                    "error": "需要登录B站账号才能下载字幕",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "message": "请登录B站账号后再试，或者使用公开视频",
                }
            elif "没有字幕" in result.stdout or "找不到字幕" in result.stdout:
                return {
                    "success": False,
                    "error": "视频没有字幕",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "message": "该视频没有可用的字幕",
                }
            else:
                return {
                    "success": False,
                    "error": "未找到下载的字幕文件",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "message": "可能视频没有字幕，或下载过程中出现问题",
                }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "BBDown执行超时"}
    except Exception as e:
        return {"success": False, "error": f"下载过程出错: {str(e)}"}


def main():
    parser = argparse.ArgumentParser(description="下载B站视频CC字幕")
    parser.add_argument("--url", required=True, help="B站视频URL或BV号")
    parser.add_argument(
        "--output", default="/tmp/bilibili_subtitle", help="输出目录路径"
    )
    parser.add_argument(
        "--language", default="zh-CN", help="字幕语言（BBDown会自动处理）"
    )

    args = parser.parse_args()

    # 检查BBDown
    bbdown_path = check_bbdown()
    if not bbdown_path:
        sys.exit(1)

    # 下载字幕
    result = download_subtitles(bbdown_path, args.url, args.output)

    # 输出JSON格式结果供模型使用
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
