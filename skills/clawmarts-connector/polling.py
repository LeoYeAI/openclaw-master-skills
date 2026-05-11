#!/usr/bin/env python3
"""
ClawMarts WebSocket Helper Script
WebSocket 长连接保活 + 自动接单（抢单/竞标/赛马）
不执行任务、不调用 LLM —— 任务执行由 Agent 自身完成（参见 SKILL.md）。
用法: python polling.py [--config PATH]
"""
import json
import os
import sys
import time
import argparse
import threading
import requests

try:
    import websocket as ws_lib  # websocket-client
except ImportError:
    ws_lib = None

DEFAULT_CONFIG = os.path.expanduser(
    "~/.openclaw/skills/clawmarts-connector/config.json"
)

# ── 全局状态 ──
ws_connected = threading.Event()
stop_event = threading.Event()


def load_config(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def api(method: str, path: str, cfg: dict, **kwargs):
    """统一 HTTP API 调用"""
    url = f"{cfg['clawnet_api_url']}{path}"
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {cfg['token']}"
    headers.setdefault("Content-Type", "application/json")
    try:
        resp = getattr(requests, method)(url, headers=headers, timeout=30, **kwargs)
        return resp.json()
    except Exception as e:
        print(f"  ⚠️  API error [{method.upper()} {path}]: {e}", file=sys.stderr)
        return None


# ── WebSocket 长连接 ──


def _build_ws_url(cfg: dict) -> str:
    """根据 API URL 构建 WebSocket URL"""
    base = cfg["clawnet_api_url"]
    if base.startswith("https://"):
        ws_base = "wss://" + base[len("https://"):]
    elif base.startswith("http://"):
        ws_base = "ws://" + base[len("http://"):]
    else:
        ws_base = "ws://" + base
    return f"{ws_base}/ws/claw?token={cfg['token']}&claw_id={cfg['claw_id']}"


def _ws_thread(cfg: dict):
    """WebSocket 线程：保持长连接，定期发 ping 保活"""
    url = _build_ws_url(cfg)
    ping_interval = cfg.get("heartbeat_interval", 60)
    reconnect_delay = 5

    while not stop_event.is_set():
        ws = None
        try:
            print(f"  🔌 WebSocket 连接中...")
            ws = ws_lib.create_connection(url, timeout=10)
            ws_connected.set()
            print(f"  ✅ WebSocket 已连接 (ping 间隔 {ping_interval}s)")
            reconnect_delay = 5  # 连接成功，重置重连延迟

            last_ping = time.time()
            ws.settimeout(5)  # recv 超时 5s，用于定期检查 stop_event

            while not stop_event.is_set():
                # 定期发 ping
                now = time.time()
                if now - last_ping >= ping_interval:
                    ws.send("ping")
                    last_ping = now

                # 尝试接收服务端消息
                try:
                    msg = ws.recv()
                    if msg == "pong":
                        pass  # ping 回复，忽略
                    else:
                        _handle_server_message(msg, cfg)
                except ws_lib.WebSocketTimeoutException:
                    pass  # recv 超时，正常，继续循环
                except ws_lib.WebSocketConnectionClosedException:
                    print("  ⚠️  WebSocket 连接被关闭", file=sys.stderr)
                    break

        except Exception as e:
            print(f"  ⚠️  WebSocket 错误: {e}", file=sys.stderr)
        finally:
            ws_connected.clear()
            if ws:
                try:
                    ws.close()
                except Exception:
                    pass

        if not stop_event.is_set():
            print(f"  🔄 {reconnect_delay}s 后重连...")
            stop_event.wait(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, 60)  # 指数退避，最大 60s


def _handle_server_message(raw: str, cfg: dict):
    """处理服务端推送的消息"""
    try:
        msg = json.loads(raw)
    except json.JSONDecodeError:
        return

    msg_type = msg.get("type", "")
    if msg_type == "task_push":
        task = msg.get("task", {})
        task_id = task.get("task_id", "?")
        title = task.get("title", task.get("description", "")[:40])
        print(f"  📥 收到推送任务: {task_id[:8]} - {title}")
    elif msg_type == "task_reclaimed":
        task_id = msg.get("task_id", "?")
        reason = msg.get("reason", "")
        print(f"  ⚠️  任务被收回: {task_id[:8]} - {reason}")
    elif msg_type == "heartbeat_ack":
        pass  # 心跳确认


# ── 自动接单 API 辅助函数 ──


def get_my_tasks(cfg: dict, status: str = "assigned") -> list:
    """查询我的任务"""
    r = api("get", f"/api/tasks?claw_id={cfg['claw_id']}&status={status}", cfg)
    if r and r.get("success"):
        return r.get("tasks", [])
    return []


def get_recommendations(cfg: dict) -> list:
    """获取平台推荐的任务"""
    r = api("get", f"/api/recommendations/{cfg['claw_id']}?status=pending", cfg)
    if r and r.get("success"):
        return r.get("recommendations", [])
    return []


def accept_recommendation(cfg: dict, task_id: str) -> bool:
    """接受推荐任务"""
    r = api("post", f"/api/recommendations/{cfg['claw_id']}/{task_id}/respond",
            cfg, json={"accept": True})
    return bool(r and r.get("success"))


def get_personalized_tasks(cfg: dict) -> list:
    """获取个性化任务列表（按匹配度排序）"""
    r = api("get", f"/api/tasks/personalized/{cfg['claw_id']}", cfg)
    if r and r.get("success"):
        return r.get("tasks", [])
    return []


def grab_task(cfg: dict, task_id: str) -> bool:
    """抢单"""
    r = api("post", f"/api/tasks/{task_id}/grab",
            cfg, json={"claw_id": cfg["claw_id"]})
    return bool(r and r.get("success"))


def bid_task(cfg: dict, task_id: str, bid_amount: float = 0) -> bool:
    """竞标"""
    r = api("post", f"/api/tasks/{task_id}/bid",
            cfg, json={"claw_id": cfg["claw_id"], "bid_amount": bid_amount})
    return bool(r and r.get("success"))


def join_race(cfg: dict, task_id: str) -> bool:
    """加入赛马"""
    r = api("post", f"/api/tasks/{task_id}/race/join",
            cfg, json={"claw_id": cfg["claw_id"]})
    return bool(r and r.get("success"))


# ── 自动接单核心逻辑 ──


def try_accept_tasks(cfg: dict) -> int:
    """尝试自动接单，返回成功接到的任务数"""
    accepted = 0
    max_concurrent = cfg.get("max_concurrent_tasks", 3)

    # 检查当前正在执行的任务数
    my_assigned = get_my_tasks(cfg, "assigned")
    my_in_progress = get_my_tasks(cfg, "in_progress")
    current_count = len(my_assigned) + len(my_in_progress)
    if current_count >= max_concurrent:
        return 0

    slots = max_concurrent - current_count

    # 1. 先处理平台推荐
    recs = get_recommendations(cfg)
    for rec in recs:
        if slots <= 0:
            break
        task_id = rec.get("task_id", "")
        score = rec.get("relevance_score", 0)
        if task_id and accept_recommendation(cfg, task_id):
            print(f"  ✅ 接受推荐: {task_id[:8]} (匹配度 {score:.0%})")
            accepted += 1
            slots -= 1

    # 2. 从个性化任务列表中抢单/竞标/赛马
    if slots > 0:
        tasks = get_personalized_tasks(cfg)
        for t in tasks:
            if slots <= 0:
                break
            task_id = t.get("task_id", "")
            match_mode = t.get("match_mode", "grab")
            score = t.get("relevance_score", 0)
            threshold = cfg.get("auto_delegate_threshold", 0.3)

            # 匹配度太低，跳过
            if score < threshold:
                continue

            ok = False
            if match_mode == "race":
                # 赛马任务默认跳过（可能白干），除非用户配置了 accept_race: true
                if not cfg.get("accept_race", False):
                    continue
                ok = join_race(cfg, task_id)
                mode_label = "赛马"
            elif match_mode == "bid":
                ok = bid_task(cfg, task_id)
                mode_label = "竞标"
            else:
                ok = grab_task(cfg, task_id)
                mode_label = "抢单"

            if ok:
                print(f"  ✅ {mode_label}成功: {task_id[:8]} (匹配度 {score:.0%})")
                accepted += 1
                slots -= 1

    return accepted


# ── 主循环 ──


def main():
    parser = argparse.ArgumentParser(description="ClawMarts WebSocket Helper")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="配置文件路径")
    args = parser.parse_args()

    cfg = load_config(args.config)
    for key in ("clawnet_api_url", "token", "claw_id"):
        if not cfg.get(key):
            print(f"  ❌ 配置缺少 {key}", file=sys.stderr)
            sys.exit(1)

    if ws_lib is None:
        print("  ❌ websocket-client 未安装，请执行: pip3 install websocket-client", file=sys.stderr)
        sys.exit(1)

    check_interval = 30  # 自动接单检查间隔（秒）

    print("=" * 50)
    print(f"  🦀 ClawMarts WebSocket Helper")
    print(f"  Claw: {cfg['claw_id'][:8]}...")
    print(f"  接单检查间隔: {check_interval}s")
    print("=" * 50)

    # 启动 WebSocket 线程
    t = threading.Thread(target=_ws_thread, args=(cfg,), daemon=True)
    t.start()

    # 等待首次连接（最多 10s）
    ws_connected.wait(timeout=10)
    if ws_connected.is_set():
        print("  ✅ WebSocket 长连接已建立")
    else:
        print("  ⚠️  WebSocket 首次连接超时，后台将持续重连...")

    # 主循环：自动接单
    fail_streak = 0
    while not stop_event.is_set():
        try:
            # 自动接单
            accepted = try_accept_tasks(cfg)
            if accepted > 0:
                fail_streak = 0
            else:
                fail_streak += 1

            # 连续无任务时降频
            if fail_streak >= 3:
                wait = check_interval * 2
            else:
                wait = check_interval

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"  ⚠️  接单异常: {e}", file=sys.stderr)
            wait = check_interval

        stop_event.wait(wait)

    print("\n  🛑 已停止")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop_event.set()
        print("\n  🛑 收到中断信号，退出")
