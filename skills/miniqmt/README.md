# miniQMT 量化终端 Skill

[![Version](https://img.shields.io/badge/version-1.3.0-blue.svg)](http://dict.thinktrader.net/nativeApi/start_now.html)
[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](LICENSE)
[![ClawHub](https://img.shields.io/badge/ClawHub-BossQuant-purple.svg)](https://clawhub.com)

miniQMT 极简量化交易终端，支持外接 Python 获取行情和程序化交易。

## ✨ 特性

- 🐍 **外接 Python** - 独立 Python 环境调用，灵活自由
- 🪶 **轻量级** - 无需完整 QMT 客户端，资源占用少
- 📊 **支持 Level2** - 支持 Level2 逐笔行情数据
- 💹 **实盘交易** - 支持股票、ETF 实盘程序化交易
- 🏦 **多券商支持** - 支持多家券商 miniQMT 接入

## 📥 安装

```bash
pip install xtquant
```

## 🔑 配置

需要券商开通 miniQMT 权限，并启动 miniQMT 客户端。

## 🚀 快速开始

```python
from xtquant import xtdata

# 连接行情服务
xtdata.connect()

# 下载历史数据
xtdata.download_history_data("000001.SZ", "1d", start_time="20240101")

# 获取K线数据
data = xtdata.get_market_data_ex([], ["000001.SZ"], period="1d", start_time="20240101", end_time="20241231")
print(data["000001.SZ"].head())
```

## 📊 支持的功能

| 类别 | 说明 | 示例接口 |
|------|------|----------|
| 行情连接 | 连接行情服务 | `xtdata.connect()` |
| 数据下载 | 下载历史数据 | `xtdata.download_history_data()` |
| K线数据 | 获取K线行情 | `xtdata.get_market_data_ex()` |
| 实时行情 | 订阅实时行情 | `xtdata.subscribe_quote()` |
| 财务数据 | 获取财务数据 | `xtdata.get_financial_data()` |
| 股票交易 | 下单/撤单 | `xt_trader.order_stock()` |
| 持仓查询 | 查询持仓 | `xt_trader.query_stock_positions()` |
| 委托查询 | 查询委托 | `xt_trader.query_stock_orders()` |

## 📖 交易示例

```python
from xtquant import xtdata
from xtquant.xttrader import XtQuantTrader
from xtquant.xttype import StockAccount

# 创建交易实例
trader = XtQuantTrader("path_to_userdata", session_id=123456)
account = StockAccount("your_account_id")
trader.start()

# 买入
trader.order_stock(account, "000001.SZ", xtconstant.STOCK_BUY, 100, xtconstant.FIX_PRICE, 10.5)
```

## 📄 许可证

Apache License 2.0

## 📊 更新日志

### v1.3.0 (2026-03-23)
- 🎉 增加更丰富的AI Agent演示和高阶使用指南
- 🔄 更新版本号并清理失效链接


### v1.2.0 (2026-03-15)
- 🎉 初始版本发布
- 📊 支持行情获取与程序化交易

---

## 🤝 社区与支持

- **维护者**：大佬量化 (Boss Quant)
- **主页**：http://dict.thinktrader.net/nativeApi/start_now.html
- **ClawHub**：https://clawhub.com
