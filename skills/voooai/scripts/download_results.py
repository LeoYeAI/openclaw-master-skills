#!/usr/bin/env python3
"""下载执行结果：从执行状态中提取结果 URL 并下载到本地"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(__file__))
from _common import api_get, json_output, error_exit


def get_execution_status(execution_id: str) -> dict:
    """
    查询执行状态
    
    Args:
        execution_id: 执行 ID
    
    Returns:
        执行状态字典
    """
    resp = api_get(f"/api/node-builder/execution/{execution_id}")
    return resp


def extract_result_urls(execution_data: dict) -> list:
    """
    从执行结果中提取所有结果 URL
    
    Args:
        execution_data: 执行状态数据
    
    Returns:
        结果 URL 列表，每项包含 {url, type, node_id}
    """
    urls = []
    outputs = execution_data.get("outputs", {})
    
    for node_id, output_data in outputs.items():
        if isinstance(output_data, dict):
            url = output_data.get("url") or output_data.get("result_url", "")
            output_type = output_data.get("type", "unknown")
            if url:
                urls.append({
                    "url": url,
                    "type": output_type,
                    "node_id": node_id,
                })
        elif isinstance(output_data, list):
            for idx, item in enumerate(output_data):
                if isinstance(item, dict):
                    url = item.get("url") or item.get("result_url", "")
                    if url:
                        urls.append({
                            "url": url,
                            "type": item.get("type", "unknown"),
                            "node_id": f"{node_id}_{idx}",
                        })
                elif isinstance(item, str) and item.startswith(("http://", "https://")):
                    urls.append({
                        "url": item,
                        "type": "unknown",
                        "node_id": f"{node_id}_{idx}",
                    })
    
    return urls


def download_file(url: str, filepath: str) -> tuple:
    """
    下载单个文件
    
    Args:
        url: 文件 URL
        filepath: 保存路径
    
    Returns:
        (filepath, error) - error 为 None 表示成功
    """
    req = urllib.request.Request(url, headers={"User-Agent": "VoooAI-Skill/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            with open(filepath, "wb") as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
        return filepath, None
    except Exception as e:
        return filepath, str(e)


def get_extension_from_url(url: str, default: str = ".bin") -> str:
    """
    从 URL 中提取文件扩展名
    
    Args:
        url: 文件 URL
        default: 默认扩展名
    
    Returns:
        文件扩展名
    """
    # 移除查询参数
    path = url.split("?")[0]
    # 提取扩展名
    ext = os.path.splitext(path)[-1].lower()
    
    # 验证扩展名
    valid_exts = {
        ".png", ".jpg", ".jpeg", ".webp", ".gif",
        ".mp4", ".mov", ".avi", ".mkv", ".webm",
        ".mp3", ".wav", ".flac", ".m4a", ".ogg",
    }
    
    if ext in valid_exts:
        return ext
    return default


def main():
    parser = argparse.ArgumentParser(
        description="下载 VoooAI 工作流执行结果到本地",
        epilog="""
环境变量:
  VOOOAI_ACCESS_KEY  必填，Bearer 鉴权
  VOOOAI_BASE_URL    可选，默认 https://voooai.com

示例:
  # 下载执行结果到当前目录
  python3 download_results.py exec_abc123

  # 指定输出目录
  python3 download_results.py exec_abc123 --output-dir ~/Downloads/my_project

  # 指定文件名前缀
  python3 download_results.py exec_abc123 --prefix "storyboard"

  # 仅列出 URL 不下载
  python3 download_results.py exec_abc123 --no-download

  # 直接下载指定 URL
  python3 download_results.py --urls https://a.com/1.png https://b.com/2.mp4

  # 完整流程示例
  EXEC_ID=$(python3 execute_workflow.py workflow.json | jq -r '.execution_id')
  python3 get_status.py $EXEC_ID --poll
  python3 download_results.py $EXEC_ID --output-dir ./output

文件命名:
  - 默认: 01.png, 02.mp4, ...
  - 带前缀: storyboard_01.png, storyboard_02.mp4, ...
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "execution_id",
        nargs="?",
        default="",
        help="执行 ID，自动提取该执行的所有结果 URL",
    )
    parser.add_argument(
        "--urls",
        nargs="+",
        default=[],
        help="直接指定要下载的 URL 列表（不需要 execution_id）",
    )
    parser.add_argument(
        "--output-dir",
        default="",
        help="输出目录（默认当前目录）",
    )
    parser.add_argument(
        "--prefix",
        default="",
        help="文件名前缀（如 'storyboard' → storyboard_01.png）",
    )
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="仅输出 URL 列表，不实际下载",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=5,
        help="并行下载线程数（默认 5）",
    )
    args = parser.parse_args()

    # 收集 URL
    download_items = []
    
    if args.urls:
        # 直接指定的 URL
        for url in args.urls:
            download_items.append({
                "url": url,
                "type": "unknown",
                "node_id": "",
            })
    
    if args.execution_id:
        # 从执行结果中提取
        print(f"正在获取执行结果: {args.execution_id}", file=sys.stderr)
        resp = get_execution_status(args.execution_id)
        
        if not resp.get("success"):
            error_exit(f"获取执行状态失败: {resp.get('message', '未知错误')}")
        
        status = resp.get("status", "unknown")
        if status != "completed":
            error_exit(f"执行未完成（当前状态: {status}），无法下载结果")
        
        extracted = extract_result_urls(resp)
        download_items.extend(extracted)
    
    if not download_items:
        out = {
            "success": False,
            "error": "未找到可下载的结果 URL",
            "downloaded_files": [],
        }
        json_output(out)
        sys.exit(1)
    
    # 仅列出 URL 模式
    if args.no_download:
        out = {
            "success": True,
            "result_urls": [item["url"] for item in download_items],
            "total_count": len(download_items),
            "downloaded": False,
        }
        json_output(out)
        return
    
    # 准备输出目录
    output_dir = args.output_dir or os.getcwd()
    os.makedirs(output_dir, exist_ok=True)
    
    # 构建下载任务
    tasks = []
    for i, item in enumerate(download_items, 1):
        url = item["url"]
        ext = get_extension_from_url(url, ".bin")
        
        if args.prefix:
            filename = f"{args.prefix}_{i:02d}{ext}"
        else:
            filename = f"{i:02d}{ext}"
        
        filepath = os.path.join(output_dir, filename)
        tasks.append((url, filepath, item))
    
    # 并行下载
    print(f"开始下载 {len(tasks)} 个文件...", file=sys.stderr)
    
    results = []
    errors = []
    
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(download_file, url, fp): (url, fp, item)
            for url, fp, item in tasks
        }
        
        for future in as_completed(futures):
            url, fp, item = futures[future]
            filepath, err = future.result()
            
            if err:
                errors.append({
                    "file": filepath,
                    "url": url,
                    "error": err,
                })
                print(f"✗ 下载失败: {os.path.basename(filepath)}", file=sys.stderr)
            else:
                results.append({
                    "file": filepath,
                    "url": url,
                    "type": item.get("type", "unknown"),
                    "node_id": item.get("node_id", ""),
                })
                print(f"✓ 已下载: {os.path.basename(filepath)}", file=sys.stderr)
    
    # 按文件名排序
    results.sort(key=lambda x: x["file"])
    
    # 构建输出
    out = {
        "success": len(errors) == 0,
        "output_dir": output_dir,
        "downloaded_files": [r["file"] for r in results],
        "result_urls": [r["url"] for r in results],
        "total_count": len(results),
    }
    
    if errors:
        out["errors"] = errors
        out["error_count"] = len(errors)
    
    json_output(out)
    
    # 如果有错误，返回非零退出码
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
