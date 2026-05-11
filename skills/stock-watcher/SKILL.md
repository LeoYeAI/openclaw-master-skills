---
name: stock-watcher
description: Manage and monitor a personal stock watchlist with support for adding, removing, listing stocks, and summarizing their recent performance using data from 10jqka.com.cn. Use when the user wants to track specific stocks, get performance summaries, or manage their watchlist.
---

# Stock Watcher Skill

This skill provides comprehensive stock watchlist management capabilities, allowing users to track their favorite stocks and get performance summaries using real-time data from 同花顺 (10jqka.com.cn).

## 自选股行情查看

当你要求查看自选股行情时，系统会直接显示以下信息：
- 每只股票的代码和名称
- 近期表现指标（涨跌幅等关键数据）
- 详细信息链接（可点击查看）

无需额外命令，直接为你呈现简洁明了的行情概览。

## 管理自选股

### 添加股票
使用股票代码（6位数字）添加到自选股：
- 例如：添加 600053 九鼎投资

### 删除股票  
通过股票代码删除自选股：
- 例如：删除 600053

### 查看自选股列表
显示当前所有自选股的完整列表

### 清空自选股列表
完全清空所有自选股

## 数据来源

主要使用**同花顺 (10jqka.com.cn)** 作为数据源：
- **股票页面**: `https://stockpage.10jqka.com.cn/{stock_code}/`
- 支持沪深A股及科创板市场
- 提供实时行情、技术分析和资金流向数据

## 自选股管理

### 文件格式
自选股存储在 `~/.clawdbot/stock_watcher/watchlist.txt`：
```
600053|九鼎投资
600018|上港集团
688785|恒运昌
```

### 支持操作
1. **添加股票**: 验证股票代码格式并添加到自选股
2. **删除股票**: 按股票代码精确匹配删除
3. **查看列表**: 显示当前自选股
4. **清空列表**: 完全清空自选股
5. **行情总结**: 获取所有股票的最新数据并提供简洁摘要

## 行情摘要特点

- 直接显示关键行情指标，无冗余信息
- 提供股票详情链接便于深入查看
- 自动处理网络错误和数据异常
- 合理控制请求频率（每秒1次）

## 注意事项

- **股票代码格式**: 使用6位数字代码（如 `600053`）
- **数据延迟**: 行情可能有1-3分钟延迟
- **网络依赖**: 需要网络连接获取实时数据
- **市场范围**: 主要支持A股市场（沪市/深市/科创板）

## 安装与卸载

### 安装
运行 `scripts/install.sh` 脚本自动创建必要的目录结构。

### 卸载  
运行 `scripts/uninstall.sh` 脚本完全移除所有相关文件。

## 脚本说明

所有脚本都使用统一的配置文件 `config.py` 来管理存储路径，确保路径一致性：
- `add_stock.py` - 添加股票到自选股
- `remove_stock.py` - 从自选股删除股票
- `list_stocks.py` - 列出所有自选股
- `clear_watchlist.py` - 清空自选股列表
- `summarize_performance.py` - 获取股票行情摘要