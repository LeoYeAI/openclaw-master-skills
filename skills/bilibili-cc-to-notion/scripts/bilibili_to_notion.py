#!/usr/bin/env python3
"""
B站视频字幕到Notion学习笔记的完整流程
整合了字幕下载、内容处理和Notion笔记创建
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List


def check_tool(tool_name: str, check_cmd: List[str]) -> bool:
    """检查工具是否可用"""
    try:
        result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False


def download_subtitles(bbdown_path: str, url: str, output_dir: str) -> Dict[str, Any]:
    """下载B站字幕"""
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        cmd = [
            bbdown_path,
            url,
            "--sub-only",
            "--work-dir",
            str(output_path),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        # 查找字幕文件
        subtitle_files = list(output_path.glob("*.srt"))
        if not subtitle_files:
            subtitle_files = list(output_path.glob("*.ass"))

        if not subtitle_files:
            for subdir in output_path.iterdir():
                if subdir.is_dir():
                    subtitle_files.extend(subdir.glob("*.srt"))
                    subtitle_files.extend(subdir.glob("*.ass"))

        if subtitle_files:
            return {
                "success": True,
                "subtitle_file": str(subtitle_files[0]),
                "output_dir": str(output_path),
            }
        else:
            return {
                "success": False,
                "error": "未找到字幕文件",
                "stdout": result.stdout,
            }
    except Exception as e:
        return {"success": False, "error": f"下载失败: {str(e)}"}


def process_subtitles(subtitle_file: str) -> Dict[str, Any]:
    """处理字幕文件"""
    try:
        cmd = [sys.executable, "process_subtitles.py", "--input", subtitle_file]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            return {"success": False, "error": result.stderr}

        return json.loads(result.stdout)
    except Exception as e:
        return {"success": False, "error": f"处理失败: {str(e)}"}


def create_notion_notes(
    database_id: str,
    video_title: str,
    video_url: str,
    segments: List[Dict[str, Any]],
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """创建Notion笔记"""
    try:
        cmd = [
            sys.executable,
            "create_notion_notes.py",
            "--database-id",
            database_id,
            "--video-title",
            video_title,
            "--video-url",
            video_url,
            "--segments",
            json.dumps(segments, ensure_ascii=False),
        ]

        if tags:
            cmd.extend(["--tags", ",".join(tags)])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            return {"success": False, "error": result.stderr}

        return json.loads(result.stdout)
    except Exception as e:
        return {"success": False, "error": f"创建笔记失败: {str(e)}"}


def main():
    parser = argparse.ArgumentParser(description="B站视频字幕到Notion学习笔记")
    parser.add_argument("--url", required=True, help="B站视频URL或BV号")
    parser.add_argument("--database-id", required=True, help="Notion数据库ID")
    parser.add_argument("--tags", help="标签（逗号分隔）")
    parser.add_argument("--bbdown-path", default="/tmp/BBDown", help="BBDown路径")
    parser.add_argument(
        "--work-dir", default="/tmp/bilibili_to_notion", help="工作目录"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("B站视频字幕到Notion学习笔记")
    print("=" * 60)

    # 检查工具
    print("\n[1/4] 检查工具...")
    if not check_tool("BBDown", [args.bbdown_path, "--help"]):
        print("❌ BBDown未找到，请下载并放置到 /tmp/BBDown")
        return

    if not check_tool("FFmpeg", ["ffmpeg", "-version"]):
        print("❌ FFmpeg未安装，请运行: apt-get install ffmpeg")
        return

    print("✅ 工具检查通过")

    # 下载字幕
    print("\n[2/4] 下载字幕...")
    download_result = download_subtitles(args.bbdown_path, args.url, args.work_dir)

    if not download_result["success"]:
        print(f"❌ 下载失败: {download_result.get('error')}")
        if "尚未登录" in download_result.get("stdout", ""):
            print("提示: 部分视频需要登录B站账号才能下载字幕")
        return

    print(f"✅ 字幕下载成功: {download_result['subtitle_file']}")

    # 处理字幕
    print("\n[3/4] 处理字幕内容...")
    process_result = process_subtitles(download_result["subtitle_file"])

    if not process_result["success"]:
        print(f"❌ 处理失败: {process_result.get('error')}")
        return

    print(
        f"✅ 处理成功: {process_result['total_segments']}个片段, {process_result['key_points']}个关键点"
    )

    # 创建Notion笔记
    print("\n[4/4] 创建Notion笔记...")

    # 获取视频标题（从字幕文件名或URL）
    video_title = Path(download_result["subtitle_file"]).stem

    tags = args.tags.split(",") if args.tags else None

    notion_result = create_notion_notes(
        database_id=args.database_id,
        video_title=video_title,
        video_url=args.url,
        segments=process_result["segments"],
        tags=tags,
    )

    if not notion_result["success"]:
        print(f"❌ 创建笔记失败: {notion_result.get('error')}")
        print(f"提示: {notion_result.get('solution', '')}")
        return

    print(f"✅ Notion笔记创建成功!")
    print(f"   页面URL: {notion_result['page_url']}")
    print(f"   使用方法: {notion_result.get('method', 'unknown')}")

    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
