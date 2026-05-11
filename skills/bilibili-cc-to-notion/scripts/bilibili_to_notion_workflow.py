#!/usr/bin/env python3
"""
Bilibili to Notion 完整工作流程
一键完成：下载字幕 → 处理内容 → 生成截图 → 创建Notion笔记
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description=""):
    """运行命令并返回结果"""
    if description:
        print(f"\n🔍 {description}...")

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败: {e.stderr}")
        return {"success": False, "error": e.stderr}
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        return {"success": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Bilibili to Notion 完整工作流程")
    parser.add_argument("--url", required=True, help="Bilibili视频URL或BV号")
    parser.add_argument("--token", required=True, help="Notion API token")
    parser.add_argument("--database-id", required=True, help="Notion数据库ID")
    parser.add_argument("--output-dir", default="./output", help="输出目录")

    args = parser.parse_args()

    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    subtitles_dir = output_dir / "subtitles"
    subtitles_dir.mkdir(exist_ok=True)

    screenshots_dir = output_dir / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)

    # Step 1: 下载字幕
    download_result = run_command(
        f"python3 download_bilibili_cc.py --url '{args.url}' --output '{subtitles_dir}'",
        "下载B站字幕",
    )

    if not download_result.get("success"):
        print(f"❌ 字幕下载失败: {download_result.get('error')}")
        return

    subtitle_file = download_result.get("subtitle_file")
    video_title = download_result.get("video_title", "Unknown Video")
    video_file = download_result.get("video_file")

    print(f"✅ 字幕下载成功: {subtitle_file}")

    # Step 2: 处理字幕
    process_result = run_command(
        f"python3 process_subtitles.py --input '{subtitle_file}'", "处理字幕内容"
    )

    if not process_result.get("success"):
        print(f"❌ 字幕处理失败: {process_result.get('error')}")
        return

    segments = process_result.get("segments", [])
    markdown_content = process_result.get("markdown_content", "")

    print(
        f"✅ 字幕处理成功: {len(segments)}个片段, {process_result.get('key_points', 0)}个关键点"
    )

    # Step 3: 生成截图
    if video_file and Path(video_file).exists():
        screenshot_result = run_command(
            f"python3 screenshot_tool.py --video '{video_file}' --markdown '{subtitles_dir}/processed.md' --output-dir '{screenshots_dir}'",
            "生成截图",
        )

        if screenshot_result.get("success"):
            print(f"✅ 截图生成成功: {screenshot_result.get('screenshot_count')}张图片")
            # 更新markdown_content为处理后的版本（包含图片链接）
            markdown_file = Path(screenshots_dir) / "processed_with_images.md"
            if markdown_file.exists():
                markdown_content = markdown_file.read_text()
        else:
            print(f"⚠️  截图生成失败: {screenshot_result.get('error')}")

    # Step 4: 创建Notion笔记
    # Build the command without using f-string for the markdown content
    cmd_parts = [
        "python3 create_notion_notes_with_images.py",
        f"--token '{args.token}'",
        f"--database-id '{args.database_id}'",
        f"--video-title '{video_title}'",
        f"--video-url '{args.url}'",
        f"--segments '{json.dumps(segments)}'",
        f"--images-dir '{screenshots_dir}'",
    ]

    # For markdown content, we need to handle quotes carefully
    if markdown_content:
        # Write markdown to a temp file to avoid quote issues
        temp_md_path = output_dir / "temp_markdown.md"
        temp_md_path.write_text(markdown_content)
        cmd_parts.append(f"--markdown-content '{temp_md_path}'")

    cmd = " ".join(cmd_parts)
    create_result = run_command(cmd, "创建Notion笔记")

    if create_result.get("success"):
        print(f"✅ Notion笔记创建成功!")
        print(f"   页面链接: {create_result.get('page_url')}")
        print(f"   处理片段: {create_result.get('segments_processed')}")
        print(f"   嵌入图片: {create_result.get('images_embedded')}")
    else:
        print(f"❌ Notion笔记创建失败: {create_result.get('error')}")


if __name__ == "__main__":
    main()
