---
name: futu-trading-bot
description: Use Futu Trade Bot Skills to run account, quote, and trade workflows with real HK market data.
license: MIT-0
metadata:
  openclaw:
    emoji: "📈"
    requires:
      bins: ["python3", "pip"]
---

# Futu Trade Bot Skills 📈

## 🎯 Overview / 概述

**English Version:**
A trading bot skill based on Futu OpenAPI that enables natural language trading. This skill encapsulates Futu's market quote and order execution APIs, allowing agents to perform real-time trading operations through simple commands or scripts. Perfect for implementing natural language trading strategies and automated workflows.

**Important**: Always use the encapsulated functions provided in this skill (e.g., `submit_order`, `get_market_snapshot`). **Never call Futu SDK functions directly** (`ctx.place_order`, `ctx.get_market_snapshot`), as this will bypass connection management, parameter validation, and error handling, leading to unpredictable failures and resource leaks.

**中文版本:**
基于富途牛牛API接口的交易机器人技能，帮助用户用自然语言进行交易。本技能已将富途牛牛的行情报价、下单交易等功能做了完整封装，可供智能助手随时调用。建议通过命令行或脚本来实现自然语言的策略生成和交易执行。

**重要提示**：请始终使用本技能提供的封装函数（如 `submit_order`、`get_market_snapshot`）。**切勿直接调用富途SDK的原始函数**（例如 `ctx.place_order`），否则会绕过连接管理、参数校验和错误处理，导致不可预料的失败和资源泄漏。

---

## When to Use This Skill / 使用场景

Use this skill when the user asks in natural language, for example:

- **账户相关**：“查一下我的账户余额”、“解锁交易”、“锁定账户”、“看看我有哪些账户”
- **行情查询**：“腾讯现在多少钱？”、“查一下港交所的实时报价”、“帮我看看美团今天的K线图”
- **数据拉取**：“获取腾讯的历史K线数据”、“拉取最近10笔成交”
- **订阅与回调**：“实时监控腾讯的报价”、“给我推送腾讯的逐笔成交”
- **下单交易**：“帮我买100股腾讯，限价350”、“卖出200股阿里”、“撤单”、“把订单价格改到355”
- **策略运行**：
  - “帮我写一个区间策略，监控腾讯，低于540买入，高于550卖出”
  - “启动这个策略”
  - “我的策略跑得怎么样了？”
  - “停止我的策略”

**Note to agent**: When the user expresses any of these intents, you should use the encapsulated functions provided in this skill (e.g., `get_account_info`, `get_market_snapshot`, `submit_order`, etc.). **Never call Futu SDK functions directly** – always go through the skill's API.

## Quick Start / 快速开始

**Prerequisites / 前提条件:**
- Ensure Futu OpenD is running and HK quote entitlement is available.
- 确保富途OpenD正在运行且拥有港股行情权限。
- When running inside a restricted agent sandbox (for example OpenClaw/Codex exec), prefer `host` / `elevated` mode.
- The Futu Python SDK may access local OpenD resources during import, including the user log directory under `~/.com.futunn.FutuOpenD/Log`, so restricted sandboxes may fail before business functions are called.
- 如果在受限的 agent 沙箱中运行（例如 OpenClaw/Codex exec），优先使用 `host` / `elevated` 模式。
- 富途 Python SDK 在导入阶段就可能访问本机 OpenD 相关资源，包括 `~/.com.futunn.FutuOpenD/Log` 下的日志目录；因此受限沙箱可能会在业务函数执行前就失败。

**Setup Steps / 安装步骤:**
1. Install this skill via ClawHub (if not installed yet):
   ```bash
   clawhub install futu-trading-bot
   ```

2. Enter the skill folder (default OpenClaw workspace path):
   ```bash
   cd ~/.openclaw/workspace/skills/futu-trading-bot
   ```
   If you installed to a different location, `cd` into that folder instead.

3. Create virtual environment (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install package:
   ```bash
   pip install -e .
   ```

5. Configure credentials:
   ```bash
   cp json/config_example.json json/config.json
   # Edit json/config.json with your Futu credentials
   # 编辑json/config.json填写你的富途账户信息
   ```

## 依赖项

本技能通过 `pip install -e .` 自动安装以下核心 Python 包：
- `futu-api`（富途 SDK）
- `pydantic`（数据校验）

更多依赖请以 `pyproject.toml` / `requirements.txt` 为准。

## Module Map

- **Account**: `account_manager`
  - `get_account_info()`
  - `unlock_trade(password=None, password_md5=None)`
  - `lock_trade()`
- **Quote**: `quote_service`
  - Stage 1: `get_stock_basicinfo`, `get_market_state`
  - Stage 2: `subscribe`, `unsubscribe`, `unsubscribe_all`, `query_subscription`, callbacks
  - Stage 3: `get_market_snapshot`, `get_cur_kline`, `request_history_kline`, `get_rt_ticker`
  - Stage 4: `start_quote_stream`, `start_orderbook_stream`
- **Trade**: `trade_service`
  - `submit_order`, `modify_order`, `cancel_order`, `cancel_all_orders`
- **Strategy Runtime**: `strategy_runtime`
  - `run_strategy`
- **Strategy Helpers**: `strategy`
  - in-memory state
  - trade guard / lock
  - trading window and cooldown helpers

## Standard Workflow

1. Run `preflight_check` first to verify config, OpenD connectivity, and sandbox/runtime readiness.
2. Call `get_account_info()` and select target account (get `acc_id`).
3. Pull quote/snapshot for the target symbol (default HK use case: `HK.00700`).
4. For real trading, call `unlock_trade(...)` (password from config or input).
5. Submit or manage orders with explicit `acc_id` and `trd_env`.
6. After real operation, call `lock_trade()` if needed.

## Connection Lifecycle

- Pull-style quote functions such as `get_market_snapshot`, `get_stock_basicinfo`, `get_market_state`, `get_cur_kline`, `request_history_kline`, and `get_rt_ticker` now close their quote context automatically after returning.
- Trade functions such as `submit_order`, `modify_order`, and `cancel_all_orders` now close their trade/quote contexts automatically after returning.
- Account functions such as `get_account_info`, `unlock_trade`, and `lock_trade` now close their contexts automatically after returning.
- Subscription/callback flows keep the quote context open on purpose. For `subscribe`, `unsubscribe`, `unsubscribe_all`, `query_subscription`, `set_quote_callback`, and `set_orderbook_callback`, call `close_quote_service()` explicitly when you are done with the session.

## Canonical Imports

```python
# Always use these import paths – do not import from futu directly
from preflight_check import run_preflight
from strategy import (
    StrategyState, TradeGuard, in_trading_window,
    trading_window_status, cooldown_elapsed, holding_timeout_exceeded
)
from strategy_runtime import run_strategy
from account_manager import get_account_info, unlock_trade, lock_trade
from quote_service import (
    get_stock_basicinfo, get_market_state, get_market_snapshot,
    get_cur_kline, request_history_kline, get_rt_ticker,
    subscribe, unsubscribe, unsubscribe_all, query_subscription,
    set_quote_callback, set_orderbook_callback,
    start_quote_stream, start_orderbook_stream
)
from trade_service import submit_order, modify_order, cancel_order, cancel_all_orders
```

## Account Usage

### Preflight
```python
preflight = run_preflight()
if not preflight["success"]:
    print(preflight)
    raise SystemExit("Preflight failed")
```

```python
# Get list of accounts
info = get_account_info()
if info['success']:
    accounts = info['accounts']
    print(accounts)

# Unlock trade (uses password from config or provided)
unlock_trade()  # will prompt for password if not configured
# Or with explicit password:
# unlock_trade(password="your_password")

# Lock trade
lock_trade()
```

## Quote Usage

### Basic Info / Market State
```python
get_stock_basicinfo(market="HK", sec_type="STOCK", code_list=["HK.00700"])
get_market_state(["HK.00700"])
```

### Snapshot (no subscription needed)
```python
snap = get_market_snapshot(["HK.00700"])
if snap['success']:
    price = snap['data'][0]['last_price']
```

### K-Line
```python
# Current K-line (requires subscription, will auto-subscribe if needed)
kline = get_cur_kline(code="HK.00700", num=5, ktype="K_DAY", autype="QFQ")

# Historical K-line
hist = request_history_kline(
    code="HK.00700",
    start="2026-02-20",
    end="2026-03-06",
    ktype="K_DAY"
)
```

### Ticker
```python
tickers = get_rt_ticker(code="HK.00700", num=10)
```

### Subscription & Callbacks
```python
def on_quote(payload):
    print(payload)

set_quote_callback(on_quote)
subscribe(["HK.00700"], ["QUOTE"], is_first_push=True, subscribe_push=True)
query_subscription()
unsubscribe(["HK.00700"], ["QUOTE"])
unsubscribe_all()
close_quote_service()
```

### Unified Stream Startup
```python
def on_quote(payload):
    print(payload)

start_quote_stream(["HK.00700"], on_quote)
```

### Strategy Helpers
```python
state = StrategyState()
guard = TradeGuard()

if in_trading_window(start_time="09:30", end_time="16:00"):
    with guard.locked():
        pass
```

## Trade Usage

```python
# Submit an order
result = submit_order(
    code="HK.00700",
    side="BUY",
    qty=200,
    acc_id=6017237,               # from get_account_info
    trd_env="SIMULATE",            # or "REAL"
    price=150,                     # required for LIMIT order
    order_type="NORMAL",
)

# Modify order (change price/quantity)
modify_order(
    op="NORMAL",
    order_id="123456789",
    trd_env="SIMULATE",
    price=151,
    qty=200,
    acc_id=6017237
)

# Cancel a single order
cancel_order(order_id="123456789", trd_env="SIMULATE", acc_id=6017237)

# Cancel all orders
cancel_all_orders(trd_env="SIMULATE", acc_id=6017237)
```

## Running a Background Trading Strategy (Using System Tools)

This skill does not manage long-running processes internally. Instead, you (the agent) should use system tools (e.g., `exec`, `write`, `kill`) to run strategy scripts in the background. This keeps the skill simple and leverages the platform's process management.

### 4.1 Workflow for Background Strategies

1. **Run preflight first** with `PYTHONPATH=src python -m preflight_check`.
2. If preflight reports sandbox/log-directory restrictions, rerun in `host` / `elevated` mode before using quote/trade functions.
3. **Generate a Python script** based on user's natural language request, using the encapsulated functions from this skill (e.g., `start_quote_stream`, `submit_order`, `run_strategy`).
4. **Save the script** to a temporary file (using the `write` tool or similar).
5. **Launch the script as a background process** using the `exec` tool, redirecting output to a log file.
6. **Record the process ID (PID)** and log file path for future monitoring.
7. **Monitor/stop** using system tools (`ps`, `kill`, `cat`).

### 4.2 Natural Language Triggers

| User Request | Agent Action |
|--------------|--------------|
| “Start a strategy to monitor Tencent, buy below 540, sell above 550” | Generate script → save → launch with `exec` → return PID and log path |
| “How is my strategy doing?” | Read log file (e.g., `tail -n 20 logfile`) → summarize |
| “Stop my strategy” | Kill process using PID via `kill` tool |

### 4.3 Script Template (for Agent Reference)

When generating a strategy script, use the following template. It handles signals, logging, and state persistence correctly.

```python
#!/usr/bin/env python3
import sys
import time
import json
import os
import signal
import logging
from pathlib import Path

# If you installed the skill with `pip install -e .`, you can import modules directly.
# Only use sys.path/PYTHONPATH hacks when you didn't install the package.

from trade_service import submit_order
from quote_service import get_market_snapshot

# ===== Strategy parameters – fill by agent =====
# Replace these placeholders with your own strategy settings.
SYMBOL = "HK.00700"
ACC_ID = 0                 # fill from get_account_info()
TRD_ENV = "SIMULATE"       # default to SIMULATE; use REAL only with explicit confirmation
QTY = 0                    # position sizing / order quantity
LOG_FILE = Path("strategy.log")
PID_FILE = Path("strategy.pid")
# ===============================================

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Handle termination signals
def handle_exit(signum, frame):
    logging.info("Received signal, stopping strategy")
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

# Write PID file
with open(PID_FILE, "w") as f:
    f.write(str(os.getpid()))

logging.info(f"Strategy started: {SYMBOL}")

try:
    while True:
        snap = get_market_snapshot([SYMBOL])
        if not snap["success"]:
            logging.error(f"Quote failed: {snap['message']}")
            time.sleep(60)
            continue
        price = snap["data"][0]["last_price"]
        logging.info(f"Current price: {price}")

        # --- Insert your strategy logic here ---
        # Decide whether to trade based on your own signals/logic, then call submit_order(...).

        time.sleep(60)   # check every minute
except Exception as e:
    logging.exception("Strategy crashed")
finally:
    if PID_FILE.exists():
        PID_FILE.unlink()
```

### 4.4 Agent Execution Steps

**User**: “Start a range strategy for Tencent, buy below 540, sell above 550.”

**Agent**:
1. **Get account ID** via `get_account_info()`.
2. **Generate script** using the template above, filling in parameters.
3. **Save script** to a file, e.g., `range_00700.py`, using `write` tool.
4. **Launch background process** using `exec`:
   ```bash
   cd /path/to/workspace
   nohup .venv/bin/python range_00700.py > strategy.out 2>&1 &
   ```
   (Capture the PID from output.)
5. **Record** PID and log path.
6. **Reply**: “Strategy started. PID: 12345, log file: strategy_00700.log. You can check status or stop it anytime.”

### 4.5 Check Status

**User**: “How is my strategy doing?”

**Agent**:
- Read last lines of log: `tail -n 20 strategy_00700.log`.
- Check if process still running: `ps -p 12345`.
- Summarize: “Strategy is running, last price was 542.5 at 10:30.”

### 4.6 Stop Strategy

**User**: “Stop my strategy.”

**Agent**:
- Send SIGTERM: `kill 12345`.
- Verify process ended, clean up PID file if needed.
- Reply: “Strategy stopped.”

---

## Error Handling

- All functions return a dictionary with at least `success` (bool) and `message` (str).
- On success, additional fields like `data` or `order_id` may be present.
- Always check `success` first before using other fields.

Example:
```python
result = submit_order(...)
if result["success"]:
    print(f"Order ID: {result['order_id']}")
else:
    print(f"Error: {result['message']}")
```

If OpenD connection fails, recheck:
- OpenD is running (check port 11111 with `lsof -i :11111`)
- Host/port in `config.json` matches OpenD
- Account has necessary permissions

If the skill fails before quote/trade functions are even called, recheck:
- Whether the current agent/tool is running in a restricted sandbox
- Whether you should rerun in `host` / `elevated` mode
- Whether the runtime can access the local Futu OpenD log directory under `~/.com.futunn.FutuOpenD/Log`
- Run `PYTHONPATH=src python -m preflight_check` first and follow its suggestions

## Configuration

- **Config file**: `json/config.json`
- **Required fields**:
  - `futu_api.host` (default: 127.0.0.1)
  - `futu_api.port` (default: 11111)
  - `futu_api.security_firm` (e.g., `FUTUSECURITIES`)
- **Password handling**:
  - Prefer `trade_password_md5` (32‑char lowercase MD5)
  - Fallback to `trade_password` (will be MD5‑ed at runtime)
- **Account cache**: `json/account_info.json` (auto‑generated after `get_account_info`)

## 📜 License

This skill is licensed under **MIT-0** (MIT No Attribution).

---

**Copyright © 2026 jeffersonling1217-png**
```
