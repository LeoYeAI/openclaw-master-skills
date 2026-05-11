#!/usr/bin/env python3
"""
上传文件到Notion
使用Notion Direct Upload API
"""

import argparse
import json
import os
import requests
from pathlib import Path
from typing import Dict, Any


def upload_file_to_notion(notion_token: str, file_path_str: str) -> Dict[str, Any]:
    """
    上传文件到Notion
    返回文件URL
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
    # The upload_url is a POST endpoint that requires authentication
    # It's of the format: https://api.notion.com/v1/file_uploads/{file_upload_id}/send

    headers_upload = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2026-03-11",
    }

    with open(file_path, "rb") as f:
        # Use the file content directly with requests to handle multipart automatically
        response = requests.post(
            upload_url,
            headers=headers_upload,
            files={"file": (file_path.name, f, mime_type)},
        )

    if response.status_code != 200:
        return {
            "success": False,
            "error": f"Failed to upload file content: {response.status_code}",
            "detail": response.text[:200],
        }

    # Step 3: The file is now uploaded, return the file_upload_id
    # To use this file in Notion, you would reference it as:
    # {"type": "file_upload", "file_upload": {"id": file_upload_id}}

    return {
        "success": True,
        "file_upload_id": file_upload_id,
        "message": "File uploaded successfully. Use this file_upload_id to attach the file to Notion content.",
    }


def main():
    parser = argparse.ArgumentParser(description="上传文件到Notion")
    parser.add_argument("--token", required=True, help="Notion API token")
    parser.add_argument("--file", required=True, help="文件路径")

    args = parser.parse_args()

    result = upload_file_to_notion(args.token, args.file)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
