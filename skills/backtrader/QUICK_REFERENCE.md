# Backtrader 快速参考

本文档提供最常用的 Backtrader 接口和代码示例。

**维护者**: 大佬量化 (Boss Quant)

## 创建引擎

```python
import backtrader as bt

cerebro = bt.Cerebro()
cerebro.broker.setcash(100000)        # 设置初始资金
cerebro.broker.setcommission(0.001)   # 设置手续费
```

## 添加策略

```python
class MyStrategy(bt.Strategy):
    params = (('period', 20),)

    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=self.params.period)

    def next(self):
        if not self.position:
            if self.data.close[0] > self.sma[0]:
                self.buy()
        else:
            if self.data.close[0] < self.sma[0]:
                self.sell()

cerebro.addstrategy(MyStrategy, period=20)
```

## 加载数据

```python
# 从 Pandas DataFrame 加载
data = bt.feeds.PandasData(dataname=df, datetime='date', open='open', high='high', low='low', close='close', volume='volume')
cerebro.adddata(data)

# 从 CSV 文件加载
data = bt.feeds.GenericCSVData(dataname='data.csv', dtformat='%Y-%m-%d', datetime=0, open=1, high=2, low=3, close=4, volume=5)
cerebro.adddata(data)
```

## 常用指标

```python
# 均线
sma = bt.indicators.SMA(self.data.close, period=20)
ema = bt.indicators.EMA(self.data.close, period=12)

# MACD
macd = bt.indicators.MACD(self.data.close, period_me1=12, period_me2=26, period_signal=9)

# RSI
rsi = bt.indicators.RSI(self.data.close, period=14)

# 布林带
bb = bt.indicators.BollingerBands(self.data.close, period=20, devfactor=2.0)

# ATR
atr = bt.indicators.ATR(self.data, period=14)
```

## 下单操作

```python
# 市价买入
self.buy(size=100)

# 市价卖出
self.sell(size=100)

# 限价单
self.buy(size=100, price=10.5, exectype=bt.Order.Limit)

# 目标仓位
self.order_target_percent(target=0.5)  # 50%仓位
```

## 添加分析器

```python
# 夏普比率
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')

# 最大回撤
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

# 交易统计
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

# 运行并获取结果
results = cerebro.run()
strat = results[0]
print(f"夏普比率: {strat.analyzers.sharpe.get_analysis()}")
print(f"最大回撤: {strat.analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%")
```

## 更多资源

- [Backtrader 官方文档](https://www.backtrader.com/docu/)
- [GitHub](https://github.com/mementum/backtrader)
