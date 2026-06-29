"""
state.py

Daemon 运行状态持久化（JSON 文件）。
CLI 通过读取这个文件定位 daemon 的 socket 端口。
"""

import json
import os
from pathlib import Path

_STATE_FILE = Path(__file__).parent / ".clawtrader_state.json"


def read() -> dict:
    if _STATE_FILE.exists():
        try:
            return json.loads(_STATE_FILE.read_text())
        except Exception:
            pass
    return {}


def write(data: dict) -> None:
    _STATE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def clear() -> None:
    if _STATE_FILE.exists():
        _STATE_FILE.unlink()


def get_port() -> int | None:
    return read().get("port")


def is_running() -> bool:
    st = read()
    if not st.get("port"):
        return False
    pid = st.get("pid")
    if not pid:
        return False
    try:
        os.kill(pid, 0)   # 发信号 0 探活
        return True
    except OSError:
        return False
