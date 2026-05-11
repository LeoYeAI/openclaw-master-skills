#!/usr/bin/env python3
"""
创建Notion学习笔记工具（支持图片插入）
使用Notion API直接创建页面和添加内容，支持从Markdown解析图片
"""

import argparse
import json
import os
import re
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path


def upload_file_to_notion(notion_token: str, file_path_str: str) -> Dict[str, Any]:
    """
    上传文件到Notion
    返回文件上传ID
    """
    file_path = Path(file_path_str)
    if not file_path.exists():
        return {"success": False, "error": f"文件不存在: {file_path_str}"}

    # Step 1: Create a file upload object
    create_url = "https://api.notion.com/v1/file_uploads"

    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2026-03-11",
        "Content-Type": "application/json",
    }

    # Determine MIME type based on file extension
    mime_type = "image/jpeg"  # default
    if file_path.suffix.lower() in [".png"]:
        mime_type = "image/png"
    elif file_path.suffix.lower() in [".gif"]:
        mime_type = "image/gif"
    elif file_path.suffix.lower() in [".mp4"]:
        mime_type = "video/mp4"
    elif file_path.suffix.lower() in [".pdf"]:
        mime_type = "application/pdf"

    create_data = {
        "filename": file_path.name,
        "content_type": mime_type,
    }

    response = requests.post(create_url, headers=headers, json=create_data)

    if response.status_code != 200:
        return {
            "success": False,
            "error": f"Failed to create file upload: {response.status_code}",
            "detail": response.text[:200],
        }

    upload_data = response.json()
    upload_url = upload_data.get("upload_url")
    file_upload_id = upload_data.get("id")

    if not upload_url:
        return {
            "success": False,
            "error": "No upload_url returned from create file upload",
        }

    # Step 2: Send the file content to Notion
    headers_upload = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2026-03-11",
    }

    with open(file_path, "rb") as f:
        files = {"file": (file_path.name, f, mime_type)}
        response = requests.post(upload_url, headers=headers_upload, files=files)

    if response.status_code != 200:
        return {
            "success": False,
            "error": f"Failed to upload file content: {response.status_code}",
            "detail": response.text[:200],
        }

    return {
        "success": True,
        "file_upload_id": file_upload_id,
        "message": "File uploaded successfully.",
    }


def parse_markdown_images(
    markdown: str, base_dir: str = "assets"
) -> List[Dict[str, str]]:
    """从Markdown中提取图片链接"""
    # 匹配 ![alt](url) 格式
    pattern = r"!\[(.*?)\]\((.*?)\)"
    matches = re.findall(pattern, markdown)

    images = []
    for alt, url in matches:
        # 如果是相对路径，转换为绝对路径
        if not url.startswith(("http://", "https://")):
            full_path = os.path.join(base_dir, url) if not os.path.isabs(url) else url
        else:
            full_path = url

        images.append({"alt": alt, "url": full_path, "original": f"![{alt}]({url})"})

    return images


def _rt(text: str) -> List[Dict[str, Any]]:
    """Create Notion rich_text array."""
    if not text:
        return []
    return [{"type": "text", "text": {"content": text}}]


def _normalize_image_path(url: str, base_dir: str) -> str:
    if url.startswith(("http://", "https://")):
        return url
    if os.path.isabs(url):
        return url
    return os.path.join(base_dir, url)


def _parse_markdown_to_blocks(
    markdown: str,
    images_base_dir: str,
    notion_token: str,
    upload_local_images: bool = True,
) -> Tuple[List[Dict[str, Any]], int]:
    """Very small Markdown -> Notion blocks parser.

    Supported:
    - #/##/### headings
    - paragraphs
    - unordered list items: '- '
    - ordered list items: '1. '
    - fenced code blocks: ```lang ... ```
    - images: ![alt](url)
      - external url => external image block
      - local path => upload then file_upload image block (if upload_local_images)
    """

    blocks: List[Dict[str, Any]] = []
    images_embedded = 0

    in_code = False
    code_lang = "plain text"
    code_lines: List[str] = []

    para_lines: List[str] = []

    def flush_paragraph():
        nonlocal para_lines
        text = "\n".join([l.rstrip() for l in para_lines]).strip()
        if text:
            blocks.append(
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": _rt(text)},
                }
            )
        para_lines = []

    def flush_code():
        nonlocal code_lines, code_lang
        text = "\n".join(code_lines).rstrip("\n")
        blocks.append(
            {
                "object": "block",
                "type": "code",
                "code": {
                    "rich_text": _rt(text),
                    "language": code_lang,
                },
            }
        )
        code_lines = []
        code_lang = "plain text"

    # Lazy import to keep script standalone
    def _upload_local_image(local_path: str) -> Optional[str]:
        if not upload_local_images:
            return None
        try:
            from upload_file_to_notion import upload_file_to_notion

            res = upload_file_to_notion(notion_token, local_path)
            if res.get("success"):
                return res.get("file_upload_id")
            return None
        except Exception:
            return None

    lines = markdown.splitlines()
    for raw in lines:
        line = raw.rstrip("\n")

        # code fence
        if line.strip().startswith("```"):
            if in_code:
                # close
                flush_code()
                in_code = False
            else:
                flush_paragraph()
                in_code = True
                fence = line.strip()[3:].strip()
                code_lang = fence if fence else "plain text"
            continue

        if in_code:
            code_lines.append(line)
            continue

        # blank line separates paragraphs
        if not line.strip():
            flush_paragraph()
            continue

        # image line (inline images also supported)
        img_match = re.search(r"!\[(.*?)\]\((.*?)\)", line)
        if img_match:
            flush_paragraph()
            alt, url = img_match.group(1), img_match.group(2)
            full = _normalize_image_path(url, images_base_dir)
            if full.startswith(("http://", "https://")):
                blocks.append(
                    {
                        "object": "block",
                        "type": "image",
                        "image": {"type": "external", "external": {"url": full}},
                    }
                )
                images_embedded += 1
            else:
                file_upload_id = _upload_local_image(full)
                if file_upload_id:
                    blocks.append(
                        {
                            "object": "block",
                            "type": "image",
                            "image": {
                                "type": "file_upload",
                                "file_upload": {"id": file_upload_id},
                                "caption": _rt(alt) if alt else [],
                            },
                        }
                    )
                    images_embedded += 1
                else:
                    # fallback to external with file:// (may not render)
                    blocks.append(
                        {
                            "object": "block",
                            "type": "image",
                            "image": {
                                "type": "external",
                                "external": {"url": f"file://{os.path.abspath(full)}"},
                            },
                        }
                    )
            # remove image markdown from line; keep remaining text if any
            remaining = re.sub(r"!\[(.*?)\]\((.*?)\)", "", line).strip()
            if remaining:
                para_lines.append(remaining)
            continue

        # headings
        if line.startswith("### "):
            flush_paragraph()
            blocks.append(
                {
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {"rich_text": _rt(line[4:].strip())},
                }
            )
            continue
        if line.startswith("## "):
            flush_paragraph()
            blocks.append(
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {"rich_text": _rt(line[3:].strip())},
                }
            )
            continue
        if line.startswith("# "):
            flush_paragraph()
            blocks.append(
                {
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {"rich_text": _rt(line[2:].strip())},
                }
            )
            continue

        # unordered list
        if line.startswith("- "):
            flush_paragraph()
            blocks.append(
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": _rt(line[2:].strip())},
                }
            )
            continue

        # ordered list
        ol_match = re.match(r"^(\d+)\.\s+(.*)$", line)
        if ol_match:
            flush_paragraph()
            blocks.append(
                {
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {"rich_text": _rt(ol_match.group(2).strip())},
                }
            )
            continue

        para_lines.append(line)

    # flush end
    if in_code:
        flush_code()
    flush_paragraph()

    return blocks, images_embedded


def create_image_block(
    image_url: str, caption: str = "", file_upload_id: Optional[str] = None
) -> Dict[str, Any]:
    """创建图片块"""
    # 如果有file_upload_id，使用Notion上传的文件
    if file_upload_id:
        return {
            "object": "block",
            "type": "image",
            "image": {
                "type": "file_upload",
                "file_upload": {"id": file_upload_id},
            },
        }
    # 支持外部URL
    elif image_url.startswith(("http://", "https://")):
        return {
            "object": "block",
            "type": "image",
            "image": {"type": "external", "external": {"url": image_url}},
        }
    else:
        # 本地文件需要先上传到Notion
        return {
            "object": "block",
            "type": "image",
            "image": {
                "type": "external",
                "external": {"url": f"file://{os.path.abspath(image_url)}"},
            },
        }


def create_learning_notes(
    notion_token: str,
    database_id: str,
    video_title: str,
    video_url: str,
    segments: List[Dict[str, Any]],
    markdown_content: Optional[str] = None,
    tags: Optional[List[str]] = None,
    images_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """创建Notion学习笔记（支持图片）"""
    try:
        BASE_URL = "https://api.notion.com/v1"
        headers = {
            "Authorization": f"Bearer {notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2026-03-11",
        }

        # 1. 创建页面
        properties = {
            "名称": {"title": [{"text": {"content": video_title}}]},
        }

        url = f"{BASE_URL}/pages"
        data = {"parent": {"database_id": database_id}, "properties": properties}

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        page_id = result["id"]

        # 2. 构建内容块
        blocks: List[Dict[str, Any]] = []

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

        # If markdown_content is provided, prefer it as the main content.
        images_embedded = 0
        if markdown_content:
            md_blocks, images_embedded = _parse_markdown_to_blocks(
                markdown=markdown_content,
                images_base_dir=images_dir or "assets",
                notion_token=notion_token,
                upload_local_images=True,
            )
            blocks.extend(md_blocks)
        else:
            # Fallback to the old segments-based layout.
            images = []

        # 添加学习内容块（fallback）
        if not markdown_content:
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
                                            {
                                                "type": "text",
                                                "text": {"content": content},
                                            }
                                        ]
                                    },
                                }
                            ],
                        },
                    }
                )

        # 如果有图片，添加图片块（fallback）
        if not markdown_content and images:
            blocks.append(
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {"type": "text", "text": {"content": "📷 相关截图"}}
                        ]
                    },
                }
            )

            for img in images:
                # 如果是本地文件，先上传到Notion
                if not img["url"].startswith(("http://", "https://")):
                    upload_result = upload_file_to_notion(notion_token, img["url"])
                    if upload_result["success"]:
                        file_upload_id = upload_result["file_upload_id"]
                        blocks.append(
                            create_image_block(img["url"], img["alt"], file_upload_id)
                        )
                    else:
                        # 如果上传失败，使用外部URL方式（可能无法显示）
                        blocks.append(create_image_block(img["url"], img["alt"]))
                else:
                    # 外部URL直接使用
                    blocks.append(create_image_block(img["url"], img["alt"]))

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

        # 3. 添加内容块到页面 (batch by 100)
        append_url = f"{BASE_URL}/blocks/{page_id}/children"
        for i in range(0, len(blocks), 100):
            append_data = {"children": blocks[i : i + 100]}
            append_response = requests.patch(
                append_url, headers=headers, json=append_data
            )
            append_response.raise_for_status()

        page_url = f"https://www.notion.so/{page_id.replace('-', '')}"

        return {
            "success": True,
            "page_id": page_id,
            "page_url": page_url,
            "segments_processed": len(segments),
            "images_embedded": images_embedded,
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
    parser = argparse.ArgumentParser(description="创建Notion学习笔记（支持图片）")
    parser.add_argument("--token", required=True, help="Notion API token")
    parser.add_argument("--database-id", required=True, help="Notion数据库ID")
    parser.add_argument("--video-title", required=True, help="视频标题")
    parser.add_argument("--video-url", required=True, help="视频URL")
    parser.add_argument("--segments", required=True, help="字幕片段JSON")
    parser.add_argument("--markdown-content", help="Markdown内容（包含图片链接）")
    parser.add_argument("--tags", help="标签（逗号分隔）")
    parser.add_argument("--images-dir", help="图片目录路径")

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
        markdown_content=args.markdown_content,
        tags=tags,
        images_dir=args.images_dir,
    )

    # 输出JSON格式结果
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
