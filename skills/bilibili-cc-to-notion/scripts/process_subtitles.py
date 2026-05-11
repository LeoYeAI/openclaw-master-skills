#!/usr/bin/env python3
"""
处理字幕文件工具
提取关键内容并生成带截图标记的Markdown
"""

import argparse
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional


def parse_srt(srt_content: str) -> List[Dict[str, Any]]:
    """解析SRT格式字幕"""
    subtitles = []
    blocks = srt_content.strip().split("\n\n")

    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) >= 3:
            try:
                index = int(lines[0])
                times = lines[1].split(" --> ")
                start_time = times[0].strip()
                end_time = times[1].strip()
                text = " ".join(lines[2:]).strip()

                # 解析时间戳为秒
                start_seconds = time_to_seconds(start_time)

                subtitles.append(
                    {
                        "index": index,
                        "start_time": start_time,
                        "end_time": end_time,
                        "start_seconds": start_seconds,
                        "text": text,
                    }
                )
            except (ValueError, IndexError):
                continue

    return subtitles


def time_to_seconds(time_str: str) -> int:
    """将SRT时间格式转换为秒"""
    # 格式: 00:00:00,000 或 00:00:00.000
    time_str = time_str.replace(",", ".")
    parts = time_str.split(":")
    if len(parts) == 3:
        hours, minutes, seconds = parts
        seconds_parts = seconds.split(".")
        seconds_int = int(seconds_parts[0])
        return int(hours) * 3600 + int(minutes) * 60 + seconds_int
    return 0


def format_timestamp(seconds: int) -> str:
    """格式化时间戳为hh:mm:ss"""
    hh = seconds // 3600
    mm = (seconds % 3600) // 60
    ss = seconds % 60
    return f"{hh:02d}:{mm:02d}:{ss:02d}"


def extract_key_phrases(text: str) -> List[str]:
    """提取关键词语"""
    keywords = []

    # 检查是否包含代码相关内容
    code_indicators = ["代码", "编程", "函数", "变量", "类", "方法", "API", "接口"]
    for indicator in code_indicators:
        if indicator in text:
            keywords.append(indicator)
            break

    # 检查是否包含UI交互
    ui_indicators = ["点击", "按钮", "菜单", "界面", "操作", "选择"]
    for indicator in ui_indicators:
        if indicator in text:
            keywords.append(indicator)
            break

    # 检查视觉指代词
    visual_indicators = ["这里", "这儿", "那里", "那儿", "这样", "那样"]
    for indicator in visual_indicators:
        if indicator in text:
            keywords.append(indicator)
            break

    # 检查网址/链接
    url_pattern = r"(https?://\S+|www\.\S+|\S+\.(com|cn|org|net))"
    if re.search(url_pattern, text):
        keywords.append("链接")

    return keywords


def should_add_screenshot(text: str) -> bool:
    """判断是否需要添加截图标记"""
    indicators = [
        "代码",
        "编程",
        "函数",
        "变量",
        "类",
        "方法",
        "API",
        "接口",
        "点击",
        "按钮",
        "菜单",
        "界面",
        "操作",
        "选择",
        "这里",
        "这儿",
        "那里",
        "那儿",
        "这样",
        "那样",
        "网址",
        "链接",
        "地址",
        "http",
        "https",
        "www.",
    ]

    for indicator in indicators:
        if indicator in text:
            return True

    # 检查URL
    url_pattern = r"(https?://\S+|www\.\S+|\S+\.(com|cn|org|net))"
    if re.search(url_pattern, text):
        return True

    return False


def process_subtitles(
    subtitle_file: str, min_length: int = 20, max_length: int = 500
) -> Dict[str, Any]:
    """处理字幕文件"""
    try:
        with open(subtitle_file, "r", encoding="utf-8") as f:
            content = f.read()

        subtitles = parse_srt(content)

        if not subtitles:
            return {"success": False, "error": "无法解析字幕文件"}

        # 处理每个字幕段
        segments = []
        for sub in subtitles:
            text = sub["text"]
            if min_length <= len(text) <= max_length:
                segment = {
                    "start_time": sub["start_time"],
                    "end_time": sub["end_time"],
                    "start_seconds": sub["start_seconds"],
                    "text": text,
                    "concepts": extract_key_phrases(text),
                    "should_screenshot": should_add_screenshot(text),
                }
                segments.append(segment)

        # 生成Markdown内容
        markdown_content = generate_markdown(segments)

        return {
            "success": True,
            "segments": segments,
            "markdown_content": markdown_content,
            "total_segments": len(segments),
            "key_points": len(
                [s for s in segments if s.get("should_screenshot", False)]
            ),
        }

    except Exception as e:
        return {"success": False, "error": f"处理字幕失败: {str(e)}"}


def generate_markdown(segments: List[Dict[str, Any]]) -> str:
    """生成Markdown内容"""
    lines = []

    # 标题
    lines.append("# 学习笔记\n")
    lines.append(
        f"> 自动生成于 {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    )

    # 内容概览
    lines.append("\n## 内容概览\n")
    lines.append(f"- 总片段数: {len(segments)}\n")
    lines.append(
        f"- 关键知识点: {len([s for s in segments if s.get('should_screenshot', False)])}\n"
    )

    # 学习内容
    lines.append("\n## 学习内容\n")

    for i, segment in enumerate(segments, 1):
        time_str = format_timestamp(segment["start_seconds"])

        # 添加截图标记（如果需要）
        screenshot_marker = ""
        if segment.get("should_screenshot", False):
            screenshot_marker = f" Screenshot-[{time_str}]"

        lines.append(f"### 片段 {i}: {time_str}\n")
        lines.append(f"{segment['text']}{screenshot_marker}\n")

        if segment.get("concepts"):
            lines.append(f"**关键词语**: {', '.join(segment['concepts'])}\n")

        lines.append("\n")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="处理字幕文件")
    parser.add_argument("--input", required=True, help="字幕文件路径")
    parser.add_argument("--min-length", type=int, default=20, help="最小片段长度")
    parser.add_argument("--max-length", type=int, default=500, help="最大片段长度")

    args = parser.parse_args()

    result = process_subtitles(args.input, args.min_length, args.max_length)

    # 输出JSON格式结果
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
