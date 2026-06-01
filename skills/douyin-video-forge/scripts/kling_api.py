#!/usr/bin/env python3
"""Kling 3.0 API CLI — 视频生成、状态查询、帧提取、连通性检查。

用法:
    python3 kling_api.py generate --prompt "..." --duration 10
    python3 kling_api.py generate-with-image --prompt "..." --image "url"
    python3 kling_api.py check-status --task-id "..."
    python3 kling_api.py extract-frame --video "path" --position last
    python3 kling_api.py check-connectivity

依赖: pyjwt, httpx (pip install pyjwt httpx)
环境变量: KLING_ACCESS_KEY, KLING_SECRET_KEY
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time

try:
    import httpx
except ImportError:
    print("错误: 未安装 httpx，请运行: pip install httpx", file=sys.stderr)
    sys.exit(1)

try:
    import jwt
except ImportError:
    print("错误: 未安装 pyjwt，请运行: pip install pyjwt", file=sys.stderr)
    sys.exit(1)

BASE_URL = "https://api.klingai.com"
TIMEOUT = httpx.Timeout(30.0, connect=10.0)


# --- JWT 认证 ---

def generate_jwt() -> str:
    """使用 HS256 签发 Kling API JWT，有效期 30 分钟。"""
    access_key = os.environ.get("KLING_ACCESS_KEY")
    secret_key = os.environ.get("KLING_SECRET_KEY")
    if not access_key or not secret_key:
        print(
            "错误: 未配置 KLING_ACCESS_KEY 或 KLING_SECRET_KEY 环境变量。\n"
            "获取地址: https://klingai.com",
            file=sys.stderr,
        )
        sys.exit(1)
    now = int(time.time())
    headers = {"alg": "HS256", "typ": "JWT"}
    payload = {"iss": access_key, "exp": now + 1800, "nbf": now - 5}
    return jwt.encode(payload, secret_key, algorithm="HS256", headers=headers)


def get_headers() -> dict[str, str]:
    token = generate_jwt()
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# --- HTTP 请求 ---

def kling_request(method: str, path: str, json_body: dict | None = None) -> dict:
    url = f"{BASE_URL}{path}"
    headers = get_headers()
    with httpx.Client(timeout=TIMEOUT) as client:
        try:
            resp = client.request(method, url, headers=headers, json=json_body)
        except httpx.ConnectError:
            print("错误: 无法连接 Kling API，请检查网络连接或代理设置。", file=sys.stderr)
            sys.exit(1)

        if resp.status_code == 401:
            print("错误: Kling API 认证失败，请检查 KLING_ACCESS_KEY 和 KLING_SECRET_KEY。", file=sys.stderr)
            sys.exit(1)
        if resp.status_code == 403:
            print("错误: Kling API 权限不足，请检查 API Key 的权限。", file=sys.stderr)
            sys.exit(1)
        if resp.status_code == 429:
            retry_after = resp.headers.get("retry-after", "未知")
            print(f"错误: Kling API 请求频率超限，请在 {retry_after} 秒后重试。", file=sys.stderr)
            sys.exit(1)

        resp.raise_for_status()
        data = resp.json()
        return data.get("data", data)


def poll_task(task_id: str, interval: int = 10, timeout: int = 300) -> dict:
    """轮询 Kling 任务直到完成或超时。"""
    elapsed = 0
    while elapsed < timeout:
        data = kling_request("GET", f"/v1/videos/{task_id}")
        status = data.get("status", "")
        if status == "completed":
            return data
        if status == "failed":
            error_msg = data.get("error", {}).get("message", "未知错误")
            print(f"错误: Kling 视频生成失败: {error_msg}", file=sys.stderr)
            sys.exit(1)
        print(f"轮询中... 状态: {status}, 已等待 {elapsed}s", file=sys.stderr)
        time.sleep(interval)
        elapsed += interval

    print(f"错误: 任务 {task_id} 超时（{timeout}秒），请使用 check-status 手动查询。", file=sys.stderr)
    sys.exit(1)


def download_if_url(path_or_url: str) -> str:
    """如果是 URL 则下载到临时文件，否则原样返回路径。"""
    if path_or_url.startswith(("http://", "https://")):
        tmpdir = tempfile.mkdtemp(prefix="kling_")
        local_path = os.path.join(tmpdir, "downloaded.mp4")
        with httpx.Client(timeout=httpx.Timeout(120.0), follow_redirects=True) as client:
            resp = client.get(path_or_url)
            resp.raise_for_status()
            with open(local_path, "wb") as f:
                f.write(resp.content)
        return local_path
    return path_or_url


# --- 子命令 ---

def cmd_generate(args):
    body = {
        "model": "kling-v3",
        "prompt": args.prompt,
        "duration": args.duration,
        "aspect_ratio": args.aspect_ratio,
        "mode": args.mode,
        "motion_has_audio": args.motion_has_audio,
    }
    if args.kling_elements:
        body["kling_elements"] = args.kling_elements

    data = kling_request("POST", "/v1/videos/text2video", json_body=body)
    task_id = data.get("task_id", "")
    if not task_id:
        print("错误: Kling API 未返回 task_id，请检查请求参数。", file=sys.stderr)
        sys.exit(1)

    result = poll_task(task_id)
    output = {
        "task_id": task_id,
        "status": "completed",
        "video_url": result.get("video_url", ""),
        "duration": args.duration,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_generate_with_image(args):
    body = {
        "model": "kling-v3",
        "prompt": args.prompt,
        "image": args.image,
        "duration": args.duration,
        "aspect_ratio": args.aspect_ratio,
        "mode": args.mode,
        "motion_has_audio": args.motion_has_audio,
    }
    if args.kling_elements:
        body["kling_elements"] = args.kling_elements

    data = kling_request("POST", "/v1/videos/image2video", json_body=body)
    task_id = data.get("task_id", "")
    if not task_id:
        print("错误: Kling API 未返回 task_id，请检查请求参数。", file=sys.stderr)
        sys.exit(1)

    result = poll_task(task_id)
    output = {
        "task_id": task_id,
        "status": "completed",
        "video_url": result.get("video_url", ""),
        "duration": args.duration,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_check_status(args):
    data = kling_request("GET", f"/v1/videos/{args.task_id}")
    status = data.get("status", "unknown")
    result = {"task_id": args.task_id, "status": status}
    if status == "completed":
        result["video_url"] = data.get("video_url", "")
    elif status == "failed":
        result["error"] = data.get("error", {}).get("message", "未知错误")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_extract_frame(args):
    local_path = download_if_url(args.video)

    if not os.path.isfile(local_path):
        print(f"错误: 视频文件不存在: {local_path}", file=sys.stderr)
        sys.exit(1)

    tmpdir = tempfile.mkdtemp(prefix="kling_frame_")
    output_path = os.path.join(tmpdir, "frame.png")

    if args.position == "last":
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            local_path,
        ]
        probe = subprocess.run(probe_cmd, capture_output=True, text=True)
        if probe.returncode != 0:
            print(f"错误: 无法读取视频信息: {probe.stderr}", file=sys.stderr)
            sys.exit(1)
        duration = float(probe.stdout.strip())
        seek_time = max(0, duration - 0.1)
        cmd = [
            "ffmpeg", "-ss", str(seek_time),
            "-i", local_path,
            "-frames:v", "1", "-q:v", "2",
            output_path, "-y",
        ]
    else:
        cmd = [
            "ffmpeg", "-ss", args.position,
            "-i", local_path,
            "-frames:v", "1", "-q:v", "2",
            output_path, "-y",
        ]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"错误: 提取视频帧失败: {proc.stderr}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps({"frame_path": output_path}, ensure_ascii=False, indent=2))


def cmd_check_connectivity(_args):
    """检查 Kling API 连通性：验证 JWT 签名和网络连接。"""
    headers = get_headers()
    with httpx.Client(timeout=httpx.Timeout(10.0)) as client:
        try:
            resp = client.get(BASE_URL, headers=headers)
            print(json.dumps({
                "status": "ok",
                "reachable": True,
                "status_code": resp.status_code,
            }, ensure_ascii=False, indent=2))
        except Exception as e:
            print(json.dumps({
                "status": "error",
                "reachable": False,
                "error": str(e),
            }, ensure_ascii=False, indent=2))
            sys.exit(1)


# --- CLI 入口 ---

def main():
    parser = argparse.ArgumentParser(
        description="Kling 3.0 API CLI — 视频生成、状态查询、帧提取",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # generate
    p_gen = sub.add_parser("generate", help="文生视频")
    p_gen.add_argument("--prompt", required=True, help="视频生成 prompt")
    p_gen.add_argument("--duration", type=int, default=10, help="时长秒数 (10/15)")
    p_gen.add_argument("--aspect-ratio", default="9:16", help="画面比例")
    p_gen.add_argument("--mode", default="pro", help="生成模式")
    p_gen.add_argument("--motion-has-audio", type=bool, default=True, help="是否含音频")
    p_gen.add_argument("--kling-elements", nargs="*", help="角色参考图片 URL 列表")
    p_gen.set_defaults(func=cmd_generate)

    # generate-with-image
    p_img = sub.add_parser("generate-with-image", help="图生视频")
    p_img.add_argument("--prompt", required=True, help="视频生成 prompt")
    p_img.add_argument("--image", required=True, help="首帧图片 URL")
    p_img.add_argument("--duration", type=int, default=10, help="时长秒数")
    p_img.add_argument("--aspect-ratio", default="9:16", help="画面比例")
    p_img.add_argument("--mode", default="pro", help="生成模式")
    p_img.add_argument("--motion-has-audio", type=bool, default=True, help="是否含音频")
    p_img.add_argument("--kling-elements", nargs="*", help="角色参考图片 URL 列表")
    p_img.set_defaults(func=cmd_generate_with_image)

    # check-status
    p_chk = sub.add_parser("check-status", help="查询任务状态")
    p_chk.add_argument("--task-id", required=True, help="任务 ID")
    p_chk.set_defaults(func=cmd_check_status)

    # extract-frame
    p_frm = sub.add_parser("extract-frame", help="提取视频帧")
    p_frm.add_argument("--video", required=True, help="视频文件路径或 URL")
    p_frm.add_argument("--position", default="last", help="位置: last 或具体时间如 00:00:05")
    p_frm.set_defaults(func=cmd_extract_frame)

    # check-connectivity
    p_conn = sub.add_parser("check-connectivity", help="检查 API 连通性")
    p_conn.set_defaults(func=cmd_check_connectivity)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
