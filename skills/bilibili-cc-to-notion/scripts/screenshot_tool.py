#!/usr/bin/env python3
"""
视频截图工具
从视频中提取指定时间点的截图
"""

import argparse
import json
import os
import re
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional


def extract_screenshot_markers(markdown: str) -> List[Tuple[str, int]]:
    """
    从Markdown中提取Screenshot标记
    格式: Screenshot-[hh:mm:ss] 或 Screenshot-hh:mm:ss
    """
    pattern = (
        r"(?:\*?)Screenshot-(?:\[(\d{2}):(\d{2}):(\d{2})\]|(\d{2}):(\d{2}):(\d{2}))"
    )
    results: List[Tuple[str, int]] = []
    for match in re.finditer(pattern, markdown):
        hh = match.group(1) or match.group(4)
        mm = match.group(2) or match.group(5)
        ss = match.group(3) or match.group(6)
        total_seconds = int(hh) * 3600 + int(mm) * 60 + int(ss)
        results.append((match.group(0), total_seconds))
    return results


def generate_screenshot(video_path: Path, output_dir: Path, timestamp: int) -> Path:
    """
    使用ffmpeg从视频中提取截图
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    hh = timestamp // 3600
    mm = (timestamp % 3600) // 60
    ss = timestamp % 60

    filename = f"screenshot_{hh:02d}_{mm:02d}_{ss:02d}.jpg"
    output_path = output_dir / filename

    cmd = [
        "ffmpeg",
        "-ss",
        str(timestamp),
        "-i",
        str(video_path),
        "-frames:v",
        "1",
        "-q:v",
        "2",
        "-y",
        str(output_path),
    ]

    print(f"生成截图: time={hh:02d}:{mm:02d}:{ss:02d}, file={output_path}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"截图失败: {result.stderr}")
        raise Exception(f"FFmpeg错误: {result.stderr}")

    return output_path


def replace_screenshot_markers(
    markdown: str,
    video_path: Optional[Path],
    output_dir: Path,
    image_base_url: str,
) -> str:
    """
    将Screenshot标记替换为实际图片链接
    """
    if not video_path:
        print("未提供视频文件，保留Screenshot标记不变")
        return markdown

    matches = extract_screenshot_markers(markdown)
    print(f"找到 {len(matches)} 个截图标记")

    for idx, (marker, ts) in enumerate(matches):
        try:
            img_path = generate_screenshot(video_path, output_dir, ts)
            # 相对路径用于Notion
            relative_path = f"{image_base_url}/{img_path.name}"
            markdown = markdown.replace(marker, f"![截图]({relative_path})", 1)
            print(f"  [{idx + 1}/{len(matches)}] 替换 {marker} -> {relative_path}")
        except Exception as e:
            print(f"  生成截图失败 ({marker}): {e}")

    return markdown


def main():
    parser = argparse.ArgumentParser(description="视频截图工具")
    parser.add_argument("--video", help="视频文件路径")
    parser.add_argument("--markdown", help="Markdown文件路径")
    parser.add_argument("--output-dir", default="output/assets", help="输出目录")

    args = parser.parse_args()

    # 查找视频文件
    video_path = None
    if args.video:
        video_path = Path(args.video)
    else:
        # 自动查找当前目录的视频文件
        cwd = Path.cwd()
        mp4_files = list(cwd.glob("*.mp4"))
        if mp4_files:
            video_path = mp4_files[0]
            print(f"自动找到视频: {video_path}")

    # 查找Markdown文件
    markdown_path = None
    if args.markdown:
        markdown_path = Path(args.markdown)
    else:
        cwd = Path.cwd()
        md_files = list(cwd.glob("*.md"))
        if md_files:
            markdown_path = md_files[0]
            print(f"自动找到Markdown: {markdown_path}")

    if not markdown_path:
        print("错误: 未找到Markdown文件")
        return

    if not video_path:
        print("警告: 未找到视频文件，将保留Screenshot标记不变")

    # 读取Markdown
    markdown = markdown_path.read_text(encoding="utf-8")

    # 替换Screenshot标记
    output_dir = Path(args.output_dir)
    processed_md = replace_screenshot_markers(
        markdown, video_path, output_dir, "assets"
    )

    # 保存处理后的Markdown
    output_path = markdown_path.parent / f"{markdown_path.stem}_with_screenshots.md"
    output_path.write_text(processed_md, encoding="utf-8")

    print(f"\n处理完成! 保存到: {output_path}")

    # 输出JSON信息
    info = {
        "output": str(output_path),
        "screenshots_dir": str(output_dir),
        "video_used": str(video_path) if video_path else None,
        "screenshot_count": len(extract_screenshot_markers(markdown)),
    }
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
