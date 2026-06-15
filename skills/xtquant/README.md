# XtQuant QMT SDK Skill

[![Version](https://img.shields.io/badge/version-1.3.0-blue.svg)](http://dict.thinktrader.net/nativeApi/start_now.html)
[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](LICENSE)
[![ClawHub](https://img.shields.io/badge/ClawHub-BossQuant-purple.svg)](https://clawhub.com)

XtQuant QMT Python SDK，集成行情(xtdata)和交易(xttrade)接口。

## ✨ 特性

- 🔗 **行情+交易一体** - 统一SDK集成行情数据和交易执行
- 📊 **全品种支持** - 股票、ETF、可转债、期货、期权
- 📈 **Level2数据** - 逐笔成交、逐笔委托、十档行情
- 🤖 **智能算法交易** - 内置TWAP/VWAP等算法交易策略

## 📥 安装

```bash
pip install xtquant
```

## ⚙️ 配置

需 miniQMT 客户端运行：

```python
from xtquant import xtdata, xttrader

# 连接行情服务
xtdata.connect()

# 创建交易实例
xt_trader = xttrader.XtQuantTrader(r'D:\国金QMT\userdata_mini', session_id)
```

## 🚀 快速开始

```python
from xtquant import xtdata
from xtquant.xttrader import XtQuantTrader
from xtquant.xttype import StockAccount

# 行情：获取K线数据
xtdata.connect()
data = xtdata.get_market_data_ex([], ['000001.SZ'], period='1d', start_time='20240101')
print(data['000001.SZ'].head())

# 交易：下单
xt_trader = XtQuantTrader(r'D:\国金QMT\userdata_mini', 123456)
acc = StockAccount('your_account_id')
xt_trader.connect()
xt_trader.order_stock(acc, '000001.SZ', 1, 100, 0, 10.5)
```

## 📊 支持的功能模块

| 模块 | 说明 | 核心接口 |
|------|------|----------|
| 行情连接 | 连接行情服务 | `xtdata.connect()` |
| K线数据 | 多周期K线 | `xtdata.get_market_data_ex()` |
| 交易实例 | 创建交易连接 | `XtQuantTrader()` |
| 下单交易 | 买入/卖出 | `xt_trader.order_stock()` |
| 持仓查询 | 查询持仓 | `xt_trader.query_stock_positions()` |
| 资产查询 | 查询资产 | `xt_trader.query_stock_asset()` |
| 账户类型 | 股票/信用账户 | `StockAccount()` |

## 📖 更多示例

```python
from xtquant import xtdata
from xtquant.xttrader import XtQuantTrader
from xtquant.xttype import StockAccount

acc = StockAccount('your_account_id')

# 查询持仓
positions = xt_trader.query_stock_positions(acc)

# 查询资产
asset = xt_trader.query_stock_asset(acc)

# 订阅实时行情
xtdata.subscribe_quote('000001.SZ', period='tick', callback=on_data)
```

## 📄 许可证

Apache License 2.0

## 📊 更新日志

### v1.3.0 (2026-03-23)
- 🎉 增加更丰富的AI Agent演示和高阶使用指南
- 🔄 更新版本号并清理失效链接


### v1.2.0 (2026-03-15)
- 🎉 初始版本发布
- 📊 集成行情(xtdata)和交易(xttrade)接口

---

## 🤝 社区与支持

- **维护者**：大佬量化 (Boss Quant)
- **主页**：http://dict.thinktrader.net/nativeApi/start_now.html
- **ClawHub**：https://clawhub.com
