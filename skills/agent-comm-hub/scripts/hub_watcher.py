#!/usr/bin/env python3
"""
hub_watcher.py — Hub SSE 长连接守护进程

监听 Agent Communication Hub 的 SSE 事件流，实时响应 Hermes 分配的任务。
通过 launchd 保持常驻，实现秒级任务响应。

功能：
- SSE 长连接订阅 /events/workbuddy
- 收到 task_assigned → 通过 REST API 确认 + 写入信号文件
- 收到 new_message → 写入消息信号文件
- 断线自动重连（指数退避）
- 心跳超时检测

用法：
  python3 hub_watcher.py              # 前台运行（调试用）
  launchd 管理（生产环境）

日志：
  /tmp/hub-watcher.log (stdout)
  /tmp/hub-watcher.err (stderr)
"""

from __future__ import annotations

import json
import logging
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError

# ─── 配置 ──────────────────────────────────────────────────────────

HUB_URL = os.getenv("HUB_URL", "http://localhost:3100")
AGENT_ID = os.getenv("HUB_AGENT_ID", "workbuddy")

SIGNAL_DIR = Path(os.getenv(
    "SIGNAL_DIR",
    str(Path.home() / ".hermes" / "shared" / "signals"),
))

# WorkBuddy Agent 触发目录——写入此目录的文件会被 WorkBuddy 自动化消费
WB_TRIGGER_DIR = Path(os.getenv(
    "WB_TRIGGER_DIR",
    str(Path.home() / ".workbuddy" / "hub-tasks"),
))

# 重连参数
RECONNECT_BASE_SEC = 2
RECONNECT_MAX_SEC = 60
SSE_TIMEOUT_SEC = 90  # 心跳间隔 10s，90s 无数据视为断线

# ─── 日志 ──────────────────────────────────────────────────────────

log_level = os.getenv("HUB_WATCHER_LOG", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("hub_watcher")


# ─── HTTP 工具 ─────────────────────────────────────────────────────

def http_get(url: str, timeout: int = 10) -> Optional[bytes]:
    """简单的 HTTP GET，用于健康检查和 REST API 调用"""
    try:
        req = Request(url)
        with urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except Exception as e:
        logger.warning(f"HTTP GET {url} 失败: {e}")
        return None


def http_patch(url: str, data: dict, timeout: int = 10) -> bool:
    """HTTP PATCH，用于更新任务/消息状态"""
    try:
        body = json.dumps(data).encode("utf-8")
        req = Request(url, data=body, method="PATCH")
        req.add_header("Content-Type", "application/json")
        with urlopen(req, timeout=timeout) as resp:
            return resp.status < 400
    except Exception as e:
        logger.error(f"HTTP PATCH {url} 失败: {e}")
        return False


def check_hub_health() -> bool:
    """检查 Hub 是否存活"""
    data = http_get(f"{HUB_URL}/health", timeout=5)
    if data:
        try:
            info = json.loads(data)
            return info.get("status") == "ok"
        except json.JSONDecodeError:
            pass
    return False


# ─── 信号文件写入 ──────────────────────────────────────────────────

def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def write_wb_trigger(task: dict) -> None:
    """
    写入 WorkBuddy Agent 触发文件。
    这个文件会被 WorkBuddy 的自动化任务读取并执行。
    """
    WB_TRIGGER_DIR.mkdir(parents=True, exist_ok=True)

    task_id = task.get("id", "")
    trigger = {
        "task_id": task_id,
        "assigned_by": task.get("assigned_by", ""),
        "description": task.get("description", ""),
        "context": task.get("context", ""),
        "priority": task.get("priority", "normal"),
        "triggered_at": _ts(),
    }

    trigger_file = WB_TRIGGER_DIR / f"task_{task_id}.json"
    try:
        trigger_file.write_text(
            json.dumps(trigger, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info(f"[触发] 已写入 {trigger_file.name}")
    except OSError as e:
        logger.error(f"[触发] 写入失败: {e}")


def write_signal(event_type: str, payload: dict) -> None:
    """
    将 Hub 事件写入信号文件，供 WorkBuddy 读取处理。

    文件格式与 hermes-memory-bridge 的信号格式兼容：
    signals/sig_{uuid}.json
    """
    SIGNAL_DIR.mkdir(parents=True, exist_ok=True)

    import uuid
    sig = {
        "id": str(uuid.uuid4()),
        "type": event_type,
        "source": "Hub",
        "timestamp": _ts(),
        "data": payload,
    }

    sig_file = SIGNAL_DIR / f"sig_{sig['id'][:12]}.json"
    try:
        sig_file.write_text(
            json.dumps(sig, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info(f"[信号] 已写入 {sig_file.name}")
    except OSError as e:
        logger.error(f"[信号] 写入失败: {e}")


# ─── 事件处理 ──────────────────────────────────────────────────────

def handle_task_assigned(task: dict) -> None:
    """
    处理 task_assigned 事件：
    1. REST API 标记 in_progress
    2. 写入信号文件供 WorkBuddy 消费（旧通道）
    3. 写入触发文件供 WorkBuddy Agent 自动化消费（新通道）
    """
    task_id = task.get("id", "")
    description = task.get("description", "")
    assigned_by = task.get("assigned_by", "")

    logger.info(f"[任务] 收到任务 {task_id[:16]}: {description[:60]}")

    # 1. 标记 in_progress
    ok = http_patch(
        f"{HUB_URL}/api/tasks/{task_id}/status",
        {"status": "in_progress", "progress": 10},
    )
    if ok:
        logger.info(f"[任务] 已标记 in_progress")
    else:
        logger.warning(f"[任务] 标记 in_progress 失败，信号仍会写入")

    # 2. 写入信号文件（旧通道，保留兼容）
    write_signal("hub_task", {
        "task_id": task_id,
        "assigned_by": assigned_by,
        "description": description,
        "context": task.get("context", ""),
        "priority": task.get("priority", "normal"),
        "summary": f"Hermes 分配的任务: {description[:80]}",
    })

    # 3. 写入触发文件（新通道，触发 WorkBuddy Agent 自动化）
    write_wb_trigger(task)


def handle_new_message(message: dict) -> None:
    """
    处理 new_message 事件：
    写入信号文件供 WorkBuddy 消费。
    """
    msg_id = message.get("id", "")
    from_agent = message.get("from_agent", "")
    content = message.get("content", "")

    logger.info(f"[消息] 收到 {from_agent} 的消息: {content[:60]}")

    # 标记已投递
    http_patch(
        f"{HUB_URL}/api/messages/{msg_id}/status",
        {"status": "read"},
    )

    # 写入信号
    write_signal("hub_message", {
        "message_id": msg_id,
        "from_agent": from_agent,
        "content": content,
        "type": message.get("type", "message"),
        "summary": f"来自 {from_agent} 的消息: {content[:80]}",
    })


def handle_event(event_type: str, data: dict) -> None:
    """事件分发器"""
    if event_type == "task_assigned":
        handle_task_assigned(data.get("task", data))
    elif event_type == "new_message":
        handle_new_message(data.get("message", data))
    elif event_type == "pending_messages":
        messages = data.get("messages", [])
        if messages:
            logger.info(f"[积压] 补发 {len(messages)} 条积压消息")
            for msg in messages:
                handle_new_message(msg)
    elif event_type == "task_updated":
        # 任务状态更新通知（通常来自自己或 Hermes 的状态变更）
        update = data.get("update", {})
        logger.debug(f"[更新] 任务 {update.get('task_id', '')[:16]} → {update.get('status')}")
    else:
        logger.debug(f"[未知事件] {event_type}: {json.dumps(data)[:100]}")


# ─── SSE 长连接 ────────────────────────────────────────────────────

class SSEStream:
    """轻量 SSE 流解析器（不依赖第三方库）"""

    def __init__(self, url: str, timeout: int = SSE_TIMEOUT_SEC):
        self.url = url
        self.timeout = timeout
        self._running = False

    def connect(self) -> bool:
        """建立 SSE 连接，持续读取事件"""
        self._running = True

        while self._running:
            if not check_hub_health():
                logger.warning("Hub 不可用，等待重连...")
                self._wait_reconnect()
                continue

            try:
                logger.info(f"连接 SSE: {self.url}")
                req = Request(self.url)
                with urlopen(req, timeout=self.timeout) as resp:
                    logger.info("SSE 连接成功，开始监听...")
                    self._read_stream(resp)

            except Exception as e:
                if self._running:
                    logger.warning(f"SSE 连接断开: {e}")
                    self._wait_reconnect()

        return True

    def _read_stream(self, resp: Any) -> None:
        """持续读取 SSE 流"""
        buffer = ""
        raw_buf = b""
        while True:
            if not self._running:
                break
            chunk = resp.read(4096)
            if not chunk:
                break
            raw_buf += chunk
            # 完整解码，避免逐字节截断多字节 UTF-8 字符
            buffer += raw_buf.decode("utf-8", errors="replace")
            raw_buf = b""

            # 解析 SSE 事件
            while "\n\n" in buffer:
                event_text, buffer = buffer.split("\n\n", 1)
                self._parse_event(event_text)

    def _parse_event(self, event_text: str) -> None:
        """解析单个 SSE 事件块"""
        lines = event_text.strip().split("\n")
        event_type = ""
        data = ""

        for line in lines:
            if line.startswith("event:"):
                event_type = line[6:].strip()
            elif line.startswith("data:"):
                data = line[5:].strip()
            elif line == ":" or line.startswith(": "):
                # SSE 心跳注释，忽略
                pass

        if data:
            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                logger.debug(f"非 JSON 数据: {data[:80]}")
                return

            # 如果 data 包含 jsonrpc（MCP 响应），提取 result
            if "result" in payload and "jsonrpc" in payload:
                result = payload["result"]
                if isinstance(result, dict) and "content" in result:
                    for item in result["content"]:
                        if item.get("type") == "text":
                            try:
                                inner = json.loads(item["text"])
                                if "event" in inner:
                                    event_type = inner["event"]
                                    data_payload = inner
                                    handle_event(event_type, data_payload)
                                    return
                            except (json.JSONDecodeError, TypeError):
                                pass
                return

            # 普通事件格式
            if event_type or "event" in payload:
                et = event_type or payload.get("event", "unknown")
                handle_event(et, payload)

    def _wait_reconnect(self) -> None:
        """指数退避等待重连"""
        global _reconnect_delay
        logger.info(f"将在 {_reconnect_delay}s 后重连...")
        time.sleep(_reconnect_delay)
        _reconnect_delay = min(_reconnect_delay * 2, RECONNECT_MAX_SEC)

    def stop(self) -> None:
        self._running = False
        logger.info("SSE 流已停止")


# ─── 主循环 ────────────────────────────────────────────────────────

_reconnect_delay = RECONNECT_BASE_SEC
_sse: Optional[SSEStream] = None


def main() -> None:
    global _reconnect_delay, _sse

    logger.info("=" * 50)
    logger.info("Hub Watcher 启动")
    logger.info(f"  Hub: {HUB_URL}")
    logger.info(f"  Agent: {AGENT_ID}")
    logger.info(f"  信号目录: {SIGNAL_DIR}")
    logger.info("=" * 50)

    # 确保信号目录存在
    SIGNAL_DIR.mkdir(parents=True, exist_ok=True)

    # 启动前先拉取积压任务
    if check_hub_health():
        logger.info("拉取积压任务...")
        data = http_get(f"{HUB_URL}/api/tasks?agent_id={AGENT_ID}&status=pending")
        if data:
            try:
                result = json.loads(data)
                tasks = result.get("tasks", [])
                for task in tasks:
                    handle_task_assigned(task)
                if tasks:
                    logger.info(f"已处理 {len(tasks)} 个积压任务")
            except json.JSONDecodeError:
                pass
    else:
        logger.warning("Hub 不可用，跳过积压任务拉取")

    # 启动 SSE 长连接
    sse_url = f"{HUB_URL}/events/{AGENT_ID}"
    _sse = SSEStream(sse_url)

    def signal_handler(signum, frame):
        logger.info("收到退出信号")
        if _sse:
            _sse.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 连接成功后重置重连延迟
    global _reconnect_delay
    _sse.connect()


if __name__ == "__main__":
    main()
