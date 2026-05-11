#!/usr/bin/env python3
"""
hub_task_runner.py — Hub 任务即时执行器

监听 ~/.workbuddy/hub-tasks/ 目录，检测到新触发文件后：
1. 弹系统通知提醒用户
2. 通过 osascript 激活 WorkBuddy 窗口（如果 WorkBuddy 正在运行）

用法：
  python3 hub_task_runner.py          # 前台运行（调试）
  launchd 管理（生产环境）

日志：
  /tmp/hub-task-runner.log
  /tmp/hub-task-runner.err
"""

from __future__ import annotations

import json
import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

# ─── 配置 ──────────────────────────────────────────────────────────

TRIGGER_DIR = Path(os.getenv(
    "WB_TRIGGER_DIR",
    str(Path.home() / ".workbuddy" / "hub-tasks"),
))

HUB_URL = os.getenv("HUB_URL", "http://localhost:3100")

# 轮询间隔（秒）
POLL_INTERVAL = 5

# ─── 日志 ──────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stderr),
    ],
)
logger = logging.getLogger("hub_task_runner")

# ─── 通知 ──────────────────────────────────────────────────────────

def send_notification(title: str, message: str) -> None:
    """发送 macOS 系统通知"""
    try:
        script = f'display notification "{message}" with title "{title}" sound name "Glass"'
        subprocess.run(
            ["osascript", "-e", script],
            timeout=5,
            capture_output=True,
        )
    except Exception as e:
        logger.warning(f"通知发送失败: {e}")


def activate_workbuddy() -> None:
    """激活 WorkBuddy 窗口（如果正在运行）"""
    try:
        # 检查 WorkBuddy 是否在运行
        result = subprocess.run(
            ["pgrep", "-f", "WorkBuddy.app"],
            capture_output=True,
            timeout=5,
        )
        if result.returncode == 0:
            subprocess.run(
                ["osascript", "-e", 'activate application "WorkBuddy"'],
                timeout=5,
                capture_output=True,
            )
            logger.info("已激活 WorkBuddy 窗口")
    except Exception:
        pass


def update_hub_task(task_id: str, status: str, result: str = "", progress: int = 100) -> bool:
    """更新 Hub 任务状态"""
    try:
        from urllib.request import Request, urlopen
        body = json.dumps({"status": status, "result": result, "progress": progress}).encode()
        req = Request(
            f"{HUB_URL}/api/tasks/{task_id}/status",
            data=body,
            method="PATCH",
        )
        req.add_header("Content-Type", "application/json")
        with urlopen(req, timeout=10) as resp:
            return resp.status < 400
    except Exception as e:
        logger.error(f"更新任务状态失败: {e}")
        return False


# ─── 触发文件处理 ──────────────────────────────────────────────────

def process_trigger(trigger_file: Path) -> None:
    """处理单个触发文件"""
    try:
        data = json.loads(trigger_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"读取触发文件失败 {trigger_file.name}: {e}")
        trigger_file.unlink(missing_ok=True)
        return

    task_id = data.get("task_id", "?")
    description = data.get("description", "")
    assigned_by = data.get("assigned_by", "")

    logger.info(f"[任务] {task_id[:20]} | {assigned_by} | {description[:60]}")

    # 发送系统通知
    send_notification(
        "📬 Hermes → WorkBuddy 任务",
        f"{description[:80]}"
    )

    # 激活 WorkBuddy 窗口
    activate_workbuddy()

    # 不删除触发文件——留给 WorkBuddy 自动化消费
    # 自动化执行后会删除


def check_triggers() -> int:
    """检查并处理所有未消费的触发文件"""
    if not TRIGGER_DIR.exists():
        return 0

    triggers = sorted(TRIGGER_DIR.glob("task_*.json"), key=os.path.getmtime)
    count = 0
    for tf in triggers:
        # 检查是否已经通知过（通过 .notified 后缀标记）
        notified_marker = tf.with_suffix(tf.suffix + ".notified")
        if notified_marker.exists():
            continue

        process_trigger(tf)

        # 标记已通知（不删除原文件，留给自动化消费）
        try:
            notified_marker.touch()
        except OSError:
            pass

        count += 1

    return count


# ─── 主循环 ────────────────────────────────────────────────────────

def main() -> None:
    logger.info("=" * 50)
    logger.info("Hub Task Runner 启动")
    logger.info(f"  触发目录: {TRIGGER_DIR}")
    logger.info(f"  轮询间隔: {POLL_INTERVAL}s")
    logger.info("=" * 50)

    TRIGGER_DIR.mkdir(parents=True, exist_ok=True)

    _running = True

    def signal_handler(signum, frame):
        logger.info("收到退出信号")
        nonlocal _running
        _running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while _running:
        try:
            count = check_triggers()
            if count > 0:
                logger.info(f"已通知 {count} 个新任务")
        except Exception as e:
            logger.error(f"检查触发文件出错: {e}")

        time.sleep(POLL_INTERVAL)

    logger.info("Hub Task Runner 已停止")


if __name__ == "__main__":
    main()
