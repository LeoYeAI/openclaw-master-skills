# Backtrader 回测框架 Skill

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/mementum/backtrader)
[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](LICENSE)
[![ClawHub](https://img.shields.io/badge/ClawHub-BossQuant-purple.svg)](https://clawhub.com)

开源量化回测框架，支持多数据源、多策略、多周期回测与实盘。

## ✨ 特性

- 🐍 **纯 Python 实现** - 无需外部依赖，易于扩展
- ⚡ **事件驱动架构** - 逐 Bar 回测，贴近真实交易
- 📊 **100+ 内置指标** - SMA、EMA、MACD、RSI、布林带等
- 🔧 **参数优化** - 内置网格搜索参数优化
- 📈 **多股票支持** - 同时回测多只股票组合

## 📥 安装

```bash
pip install backtrader[plotting]
```

## 🚀 快速开始

```python
import backtrader as bt

class MyStrategy(bt.Strategy):
    params = (('sma_period', 20),)

    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=self.params.sma_period)

    def next(self):
        if self.data.close[0] > self.sma[0] and not self.position:
            self.buy()
        elif self.data.close[0] < self.sma[0] and self.position:
            self.sell()

# 创建引擎
cerebro = bt.Cerebro()
cerebro.addstrategy(MyStrategy)

# 加载数据
data = bt.feeds.PandasData(dataname=df)
cerebro.adddata(data)

# 设置初始资金
cerebro.broker.setcash(100000)

# 运行回测
results = cerebro.run()
cerebro.plot()
```

## 📊 核心组件

| 组件 | 说明 | 示例 |
|------|------|------|
| Cerebro | 回测引擎 | `bt.Cerebro()` |
| Strategy | 策略基类 | `class MyStrategy(bt.Strategy)` |
| Data Feed | 数据源 | `bt.feeds.PandasData()` |
| Indicator | 技术指标 | `bt.indicators.SMA()` |
| Analyzer | 分析器 | `bt.analyzers.SharpeRatio` |
| Observer | 观察器 | `bt.observers.DrawDown` |
| Broker | 模拟经纪商 | `cerebro.broker.setcash()` |

## 📖 常用指标

```python
# 均线
sma = bt.indicators.SMA(self.data.close, period=20)
ema = bt.indicators.EMA(self.data.close, period=12)

# MACD
macd = bt.indicators.MACD(self.data.close)

# RSI
rsi = bt.indicators.RSI(self.data.close, period=14)

# 布林带
bb = bt.indicators.BollingerBands(self.data.close, period=20)
```

## 📄 许可证

Apache License 2.0

## 📊 更新日志

### v1.2.0 (2026-03-23)
- 🎉 增加更丰富的AI Agent演示和高阶使用指南
- 🔄 更新版本号并清理失效链接


### v1.1.0 (2026-03-15)
- 🎉 初始版本发布
- 📊 支持完整回测框架功能

---

## 🤝 社区与支持

- **维护者**：大佬量化 (Boss Quant)
- **主页**：https://github.com/mementum/backtrader
- **ClawHub**：https://clawhub.com
