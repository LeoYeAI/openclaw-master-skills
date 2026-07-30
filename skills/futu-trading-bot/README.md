# Futu Trading Bot Skills

这是一个为 AI Agent 打造的自然语言交易执行工具。它将富途 OpenAPI 的底层逻辑封装为语义能力，支持通过自然语言驱动账户解锁、下单及风控管理。系统支持（模拟/实盘）环境隔离，能够将“帮我买 200 股腾讯”或“清仓一半持仓”这类模糊意图，转化为符合金融规范的执行动作。

A robust trade execution tool designed for AI Agents. It abstracts Futu OpenAPI logic into high-level semantic capabilities, enabling natural language control over account unlocking, order placement, and risk management. With native support for MD5 credential handling and environment isolation (Simulated/Real), it accurately translates vague intents—such as "buy 200 shares of Tencent" or "close half of my positions"—into execution actions that comply with financial standards.

适用对象：配合 OpenClaw 使用，或任何能通过命令行调用工具并能编写 Python 脚本的 Agent/LLM。

核心代码在 `src/`，配置与运行数据在 `json/`。

## 功能
- 账户查询：`get_account_info()`
- 交易解锁：`unlock_trade(password=None, password_md5=None)`
- 交易锁定：`lock_trade(password=None, password_md5=None)`
- 预检：`run_preflight()`
- 行情拉取：`get_stock_basicinfo()`、`get_market_state()`、`get_market_snapshot()`、`get_cur_kline()`、`request_history_kline()`、`get_rt_ticker()`
- 行情统一启动：`start_quote_stream()`、`start_orderbook_stream()`
- 下单：`submit_order(...)`
- 改单/撤单：`modify_order(...)`、`cancel_order(...)`、`cancel_all_orders(...)`
- 策略运行：`run_strategy(...)`
- 策略辅助：状态、交易锁、交易时段判断、回调 payload 解析

## 当前行为说明
- `submit_order` 必须显式传入 `acc_id` 和 `trd_env`（`REAL` / `SIMULATE`）。
- `get_account_info` 每次调用都会覆盖写入 `json/account_info.json`。
- `unlock_trade` / `lock_trade` 支持 MD5 密码：
  - 优先使用 `password_md5`
  - 若仅提供明文 `password`，会在运行时自动转 MD5 后调用富途接口
- 拉取型 quote 函数会在返回后自动关闭 quote context。
- trade/account 对外函数会在返回后自动关闭各自 context。
- 订阅/回调模式不会自动关闭 quote context，调用方结束时应显式 `close_quote_service()`。
- `modify_order` / `cancel_order` / `cancel_all_orders` 会自行重新初始化交易 context，不依赖上一次调用留下的连接。

## 安装
### 方式 A：作为 ClawHub Skill 安装（推荐给 Agent 用户）
不需要手动下载整个仓库，直接安装 skill 文件夹即可：
```bash
clawhub install futu-trading-bot
```

安装完成后，在该 skill 目录中创建虚拟环境并安装依赖（否则无法 `import` / 调用）：
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### 方式 B：从 GitHub 源码安装（推荐给开发者）
如果你是要开发/改代码，直接 clone 本仓库后：
```bash
pip install -r requirements.txt
```

推荐（开发环境）：
```bash
pip install -e .
```
安装后可直接 `import quote_service/trade_service/account_manager/config_manager`，
无需再手动设置 `PYTHONPATH` 或在脚本里写 `sys.path`。

额外可直接导入：
- `preflight_check`
- `strategy_runtime`
- `strategy`

## 配置
配置文件路径：`json/config.json`

最小模板：
```json
{
  "futu_api": {
    "host": "127.0.0.1",
    "port": 11111,
    "security_firm": "FUTUSECURITIES",
    "trade_password": "",
    "trade_password_md5": "",
    "default_env": "SIMULATE"
  }
}
```

说明：
- `trade_password_md5` 优先级高于 `trade_password`
- `json/config.json` 含敏感信息，已建议加入 `.gitignore`
- 若 `json/config.json` 不存在，代码会优先回退到 `json/config_example.json`，也兼容旧命名 `json/config.example.json`

## 示例
```python
from preflight_check import run_preflight
from account_manager import get_account_info, unlock_trade, lock_trade
from trade_service import submit_order

print(run_preflight())
print(get_account_info())
print(unlock_trade())  # 使用配置密码（支持MD5）

print(submit_order(
    code="HK.00700",
    side="BUY",
    qty=200,
    price=150,
    order_type="NORMAL",
    acc_id=6017237,
    trd_env="SIMULATE"
))

print(lock_trade())  # 用完建议锁回去
```

## 实时行情回调示例
```python
from quote_service import start_quote_stream, unsubscribe_all, close_quote_service
from strategy_runtime import run_strategy
from strategy import StrategyState, TradeGuard, extract_latest_price

state = StrategyState()
guard = TradeGuard()

def on_quote(payload):
    price = extract_latest_price(payload, code="HK.00700")
    if price is None:
        return
    with guard.locked():
        state.current_price = price
        print("latest price:", price)

start_quote_stream(["HK.00700"], on_quote)
run_strategy(
    pid_file="/tmp/futu_strategy.pid",
    cleanup_callbacks=[unsubscribe_all, close_quote_service],
)
```

## 运行要求
- 本机已安装并运行 Futu OpenD
- OpenD 地址与 `json/config.json` 一致（默认 `127.0.0.1:11111`）
- 真实交易前先确认账户已解锁且参数正确
- 若在 OpenClaw/Codex 等受限环境中运行，建议先执行 `PYTHONPATH=src python -m preflight_check`
- 若预检提示日志目录或 OpenD 访问受限，请改用 `host/elevated` 模式
