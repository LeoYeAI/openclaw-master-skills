#!/usr/bin/env python3
"""
创建Notion学习笔记工具
使用Notion API直接创建页面和添加内容
"""

import argparse
import json
import os
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional


def create_learning_notes(
    notion_token: str,
    database_id: str,
    video_title: str,
    video_url: str,
    segments: List[Dict[str, Any]],
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """创建Notion学习笔记"""
    try:
        BASE_URL = "https://api.notion.com/v1"
        headers = {
            "Authorization": f"Bearer {notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

        # 1. 创建页面
        # 创建页面属性（根据数据库实际属性调整）
        properties = {
            "名称": {"title": [{"text": {"content": video_title}}]},
        }

        # 创建页面
        url = f"{BASE_URL}/pages"
        data = {"parent": {"database_id": database_id}, "properties": properties}

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        page_id = result["id"]

        # 2. 构建内容块
        blocks = []

        # 视频信息标题
        blocks.append(
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "📹 视频信息"}}]
                },
            }
        )

        blocks.append(
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": f"标题: {video_title}"}}
                    ]
                },
            }
        )

        blocks.append(
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": f"链接: {video_url}"}}
                    ]
                },
            }
        )

        blocks.append(
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                            },
                        }
                    ]
                },
            }
        )

        # 内容概览
        blocks.append(
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "📊 内容概览"}}]
                },
            }
        )

        key_points = [s for s in segments if s.get("is_key_point", False)]
        blocks.append(
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": f"总片段数: {len(segments)}"},
                        }
                    ]
                },
            }
        )

        blocks.append(
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": f"关键知识点: {len(key_points)}"},
                        }
                    ]
                },
            }
        )

        # 学习内容
        blocks.append(
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "📝 学习内容"}}]
                },
            }
        )

        for i, segment in enumerate(segments[:15], 1):
            time_range = f"{segment['start_time']} - {segment['end_time']}"
            is_key = " (关键知识点)" if segment.get("is_key_point", False) else ""

            content = f"片段 {i}: {time_range}{is_key}\n> {segment['text']}"

            if segment.get("concepts"):
                concepts = ", ".join(segment["concepts"][:5])
                content += f"\n\n核心概念: {concepts}"

            # 添加可折叠块
            blocks.append(
                {
                    "object": "block",
                    "type": "toggle",
                    "toggle": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": f"片段 {i}: {time_range}"},
                            }
                        ],
                        "children": [
                            {
                                "object": "block",
                                "type": "paragraph",
                                "paragraph": {
                                    "rich_text": [
                                        {"type": "text", "text": {"content": content}}
                                    ]
                                },
                            }
                        ],
                    },
                }
            )

        # 添加学习建议
        if key_points:
            blocks.append(
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {"type": "text", "text": {"content": "💡 学习建议"}}
                        ]
                    },
                }
            )

            blocks.append(
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": "重点观看标记为'关键知识点'的片段"},
                            }
                        ]
                    },
                }
            )

            blocks.append(
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": "做好笔记，重点记录核心概念"},
                            }
                        ]
                    },
                }
            )

            blocks.append(
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": "课后复习，巩固所学知识"},
                            }
                        ]
                    },
                }
            )

        # 3. 添加内容块到页面
        append_url = f"{BASE_URL}/blocks/{page_id}/children"
        append_data = {"children": blocks}

        append_response = requests.patch(append_url, headers=headers, json=append_data)
        append_response.raise_for_status()

        page_url = f"https://www.notion.so/{page_id.replace('-', '')}"

        return {
            "success": True,
            "page_id": page_id,
            "page_url": page_url,
            "segments_processed": len(segments),
            "method": "api",
        }

    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP错误: {e.response.status_code}"
        if e.response.text:
            try:
                error_detail = json.loads(e.response.text)
                error_msg += f" - {error_detail.get('message', '')}"
            except:
                error_msg += f" - {e.response.text[:200]}"
        return {"success": False, "error": error_msg}

    except Exception as e:
        return {"success": False, "error": f"创建笔记失败: {str(e)}"}


def main():
    parser = argparse.ArgumentParser(description="创建Notion学习笔记")
    parser.add_argument("--token", required=True, help="Notion API token")
    parser.add_argument("--database-id", required=True, help="Notion数据库ID")
    parser.add_argument("--video-title", required=True, help="视频标题")
    parser.add_argument("--video-url", required=True, help="视频URL")
    parser.add_argument("--segments", required=True, help="字幕片段JSON")
    parser.add_argument("--tags", help="标签（逗号分隔）")

    args = parser.parse_args()

    # 解析segments
    try:
        segments = json.loads(args.segments)
    except json.JSONDecodeError:
        print(
            json.dumps(
                {"success": False, "error": "无法解析segments JSON"}, ensure_ascii=False
            )
        )
        return

    # 解析tags
    tags = args.tags.split(",") if args.tags else None

    result = create_learning_notes(
        notion_token=args.token,
        database_id=args.database_id,
        video_title=args.video_title,
        video_url=args.video_url,
        segments=segments,
        tags=tags,
    )

    # 输出JSON格式结果
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
