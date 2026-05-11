#!/usr/bin/env python3
"""Muse 歌曲生成异步轮询 — 每 5s 查询状态，输出 JSON 进度事件"""

import argparse
import json
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from muse_api import query_song, MuseAPIError, _load_token, _load_task_id


def _emit(event, **kwargs):
    """输出一个 JSON 事件行"""
    obj = {"event": event, "timestamp": time.strftime("%H:%M:%S")}
    obj.update(kwargs)
    print(json.dumps(obj, ensure_ascii=False), flush=True)


def _format_songs(songs):
    """格式化歌曲列表，只保留关键字段"""
    result = []
    for s in songs:
        item = {
            "workId": s.get("workId", s.get("id", "")),
            "title": s.get("title", ""),
            "tags": s.get("tags", ""),
            "duration": s.get("duration", 0),
            "audioUrl": s.get("audioUrl", ""),
            "streamAudioUrl": s.get("streamAudioUrl", ""),
            "coverUrl": s.get("coverUrl", s.get("imageUrl", "")),
            "lyrics": s.get("lyrics", ""),
            "instrumental": s.get("instrumental", False),
        }
        result.append(item)
    return result


def poll(token, task_id, interval=5, timeout=300):
    """轮询歌曲生成状态

    进度事件：
    - started: 开始轮询
    - progress: 生成中（status=0 或 1）
    - stream_ready: streamAudioUrl 可用，可先试听
    - completed: 生成完成（status=2）
    - failed: 生成失败（status=3）
    - timeout: 超时
    - error: API 调用异常
    """
    _emit("started", task_id=task_id, message="开始轮询歌曲生成状态...")

    start_time = time.time()
    stream_notified = False
    poll_count = 0

    while True:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            _emit("timeout", task_id=task_id, elapsed_s=round(elapsed),
                  message=f"轮询超时（{timeout}s），请稍后使用 task_id 查询结果")
            return None

        poll_count += 1
        try:
            data = query_song(token, task_id)
        except MuseAPIError as e:
            # 可重试错误：网络瞬时错误(-1)、服务端 500、超时等
            retryable = e.code in (-1, 502, 503) or "timeout" in str(e.msg).lower()
            if retryable and poll_count <= 5:
                _emit("retry", code=e.code, poll_count=poll_count,
                      message=f"服务暂时异常，{interval}s 后重试 ({poll_count}/5): {e.msg}")
                time.sleep(interval)
                continue
            _emit("error", code=e.code, message=e.msg)
            return None

        # 从 songs 数组推断整体状态（API 无顶层 status 字段）
        songs = data.get("songs") or []

        def _song_status(s):
            """获取单首歌曲状态，兼容 int/str"""
            v = s.get("status", 0)
            return int(v) if isinstance(v, (int, float)) else int(v) if str(v).isdigit() else 0

        if songs and all(_song_status(s) == 2 for s in songs):
            # 所有歌曲生成完成
            formatted = _format_songs(songs)
            _emit("completed", songs=formatted, count=len(formatted),
                  elapsed_s=round(elapsed),
                  message=f"生成完成！共 {len(formatted)} 首歌曲")
            return formatted

        if songs and any(_song_status(s) == 3 for s in songs):
            # 有歌曲生成失败
            desc = ""
            for s in songs:
                if _song_status(s) == 3:
                    desc = s.get("taskStatusDesc", "")
                    break
            hint = "建议：① 简化描述，避免过于抽象的表达 ② 更换风格标签 ③ 缩短歌词长度后重试"
            _emit("failed", task_id=task_id, detail=desc,
                  hint=hint,
                  message="歌曲生成失败，请修改描述后重试")
            return None

        # 也检查是否有 audioUrl 填充（完成的另一指标）
        if songs and all(s.get("audioUrl") for s in songs):
            formatted = _format_songs(songs)
            _emit("completed", songs=formatted, count=len(formatted),
                  elapsed_s=round(elapsed),
                  message=f"生成完成！共 {len(formatted)} 首歌曲")
            return formatted

        # 生成中 — 检查是否有 streamAudioUrl 可用
        if not stream_notified and songs:
            for s in songs:
                if s.get("streamAudioUrl"):
                    stream_notified = True
                    formatted = _format_songs(songs)
                    _emit("stream_ready", songs=formatted, elapsed_s=round(elapsed),
                          message="试听版本就绪，可先试听初版")
                    break

        _emit("progress", poll_count=poll_count,
              elapsed_s=round(elapsed),
              songs_count=len(songs),
              message=f"生成中... ({round(elapsed)}s)")

        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="Muse 歌曲生成异步轮询")
    parser.add_argument("--token", default=None, help="已废弃，token 自动从 ~/.muse/token 读取")
    parser.add_argument("--task-id", default=None, help="任务ID（可选，默认读取最近任务）")
    parser.add_argument("--interval", type=int, default=5, help="轮询间隔秒数（默认5）")
    parser.add_argument("--timeout", type=int, default=300, help="超时秒数（默认300）")
    args = parser.parse_args()

    try:
        token = _load_token()
        task_id = args.task_id if args.task_id else _load_task_id()
    except MuseAPIError as e:
        _emit("error", code=e.code, message=e.msg)
        sys.exit(1)
    result = poll(token, task_id, args.interval, args.timeout)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
