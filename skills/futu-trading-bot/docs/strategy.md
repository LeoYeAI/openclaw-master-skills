# Strategy Helpers 文档

所属项目：**Futu Trade Bot Skills**

## 模块位置
- `src/strategy.py`
- `src/strategy_runtime.py`

## 目标
为策略脚本提供轻量辅助，而不是复杂框架。

## `strategy.py`
提供三类能力：

1. 运行状态
- `StrategyState`

2. 并发保护
- `TradeGuard`

3. 运行辅助判断
- `in_trading_window(...)`
- `trading_window_status(...)`
- `cooldown_elapsed(...)`
- `holding_timeout_exceeded(...)`

4. 回调 payload 解析
- `extract_callback_rows(payload)`
- `filter_rows_by_code(rows, code)`
- `extract_latest_price(payload, code=None, field="last_price")`

## `strategy_runtime.py`
提供：
- `run_strategy(...)`

职责只包括：
- PID 文件管理
- 防重复启动
- `SIGINT` / `SIGTERM` 清理
- 保持进程运行

## 推荐使用方式
1. 先用 `start_quote_stream(...)` 或 `start_orderbook_stream(...)` 建立订阅
2. 在回调中用 `extract_latest_price(...)` 等辅助解析行情
3. 用 `StrategyState` 和 `TradeGuard` 管理策略状态
4. 最后调用 `run_strategy(...)` 保持进程运行并处理退出清理
