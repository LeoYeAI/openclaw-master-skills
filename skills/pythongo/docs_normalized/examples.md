# 实用例子

本章节提供一些实用例子，为了尽可能的缩减代码，这里会把所有代码尽量放在 `on_start` 函数中，格式类似于

```py {4-5}
def on_start(self) -> None:
    super().on_start()
    """示例代码开始"""
    xxxx
    xxxx
    """示例代码结束"""
```

这里只是提供一些调用方法的例子（所以可能不能直接复制到策略中运行），是为了防止你看了函数的文档还是不清楚实际中应该怎么写

同样我们不会定义不必要的参数，除非有特殊情况，这需要你有举一反三的能力

示例代码放在 `on_start` 是因为这个入口比较简单易懂，实际上这些代码你可以放在任何一个实例方法中，所以还是需要举一反三

始终记住，你是在写「Python」代码，不是在写「PythonGO」代码

## 获取 K 线 [#get_k_kline_data]

利用 `pythongo.core` 获取最近的 10 根 1 分钟 K 线

```py {1,7,12-17}
from pythongo.core import MarketCenter

class Demo(...):
    def __init__(self) -> None:
        super().__init__()
        self.market_center = MarketCenter()

    def on_start(self) -> None:
        super().on_start()

        kline_data = self.market_center.get_kline_data(
            exchange="SHFE",
            instrument_id="ag2406",
            style="M1",
            count=-10
        )
```

----

利用 `pythongo.core` 获取 `2024-01-31 14:30` 到 `2024-01-31 15:00` 的 1 分钟 K 线

```py {1,3,9,18-19}
from datetime import datetime

from pythongo.core import MarketCenter

class Demo(...):
    def __init__(self) -> None:
        super().__init__()
        self.market_center = MarketCenter()

    def on_start(self) -> None:
        super().on_start()

        kline_data = self.market_center.get_kline_data(
            exchange="SHFE",
            instrument_id="ag2406",
            style="M1",
            start_time=datetime(2024, 1, 31, 14, 30),
            end_time=datetime(2024, 1, 31, 15)
        )
```

## 订阅行情 [#sub_market_data]

订阅 `ag2602` 合约行情，并输出行情信息

```py {5-8,19}
class Demo(...):
    def on_start(self) -> None:
        super().on_start()

        self.sub_market_data(
            exchange="SHFE",
            instrument_id="ag2602"
        )

    def on_stop(self):
        super().on_stop()

        self.unsub_market_data(
            exchange="SHFE",
            instrument_id="ag2602"
        )

    def on_tick(self, tick: TickData) -> None:
        self.output(tick)
```

----

订阅多个合约行情，并输出行情信息

```py {4,9-13,25}
class Demo(...):
    def __init__(self):
        ...
        self.my_instruments = {"SHFE": "ag2602", "CZCE": "AP601"}

    def on_start(self) -> None:
        super().on_start()

        for exchange, instrument_id in self.my_instruments.items():
            self.sub_market_data(
                exchange=exchange,
                instrument_id=instrument_id
            )

    def on_stop(self):
        super().on_stop()

        for exchange, instrument_id in self.my_instruments.items():
            self.unsub_market_data(
                exchange=exchange,
                instrument_id=instrument_id
            )

    def on_tick(self, tick: TickData) -> None:
        self.output(tick)
```

## 定时器 [#scheduler]

参考 [深入框架 - pythongo.utils - Scheduler](./modules/pythongo_utils.mdx#scheduler-add_job)

## K 线合成器 [#kline_generator]

需要合成 K 线，但是不需要历史数据

```py {10}
class Demo(...):
    def on_start(self) -> None:
        self.kline_generator = KLineGenerator(
            real_time_callback=...,
            callback=...,
            exchange=...,
            instrument_id=...,
            style=...
        )
        # 不执行 `self.kline_generator.push_history_data()`
        super().on_start()
```

----

不需要合成 K 线，只需要 `KLineProducer`，然后计算历史数据指标

```py {3-12}
class Demo(...):
    def on_start(self) -> None:
        self.kline_producer = KLineProducer(
            exchange=...,
            instrument_id=...,
            style=...,
            callback=...,
        )
        self.kline_producer.worker()

        ma10 = self.kline_producer.sma(10)
        k, d, j = self.kline_producer.kdj()

        super().on_start()
```

---

合成标准套利合约 K 线

用法和 `KLineGenerator` 一致，只是需要手动订阅单腿合约

```py {1,23-28,33-38}
from pythongo.utils import KLineGeneratorArb

class Demo(...):
    def on_tick(self, tick: TickData) -> None:
        """收到行情 tick 推送"""
        super().on_tick(tick)

        self.kline_generator.tick_to_kline(tick)

    def on_start(self) -> None:
        self.kline_generator = KLineGeneratorArb(
            callback=...,
            exchange="CZCE",
            instrument_id="IPS AP405&SA405",
            style=...,
            real_time_callback=...
        )
        self.kline_generator.push_history_data()

        super().on_start()

        for instrument_id in self.kline_generator.instruments:
            """订阅单腿合约"""
            self.sub_market_data(
                exchange="CZCE",
                instrument_id=instrument_id
            )

    def on_stop(self) -> None:
        super().on_stop()

        for instrument_id in self.kline_generator.instruments:
            """取消订阅单腿合约"""
            self.unsub_market_data(
                exchange="CZCE",
                instrument_id=instrument_id
            )
```

----

从 K 线合成器中的 `KLineProducer` 中获取 K 线数据

```py {6,9}
class Demo(...):
    def on_start(self) -> None:
        super().on_start()

        # 获取最后 1 个收盘价
        last_close_price = self.kline_generator.producer.close[-1]

        # 获取最后 10 个开盘价
        last_open_price = self.kline_generator.producer.open[-10:]
```

---

多合约同周期

注意填写交易所和合约代码时候需要按照以下格式（必须按顺序依次对应，且使用英文分号 `;` 分隔）：

交易所：`SHFE;SHFE;CZCE`

合约代码：`ag2406;ag2405;AP405`

注意计算指标的时候使用正确的 `kline_generator`

```py {7,11-18,20,22,29-30,32,38,42}
from pythongo.classdef import TickData
from pythongo.utils import KLineGenerator

class Demo(...):
    def __init__(self) -> None:
        self.kline_generators: dict[str, KLineGenerator] = {}
        """K 线合成器容器"""

    def on_start(self) -> None:
        for exchange, instrument_id in zip(self.exchange_list, self.instrument_list):
            kline_generator = KLineGenerator(
                real_time_callback=self.real_time_callback,
                callback=self.callback,
                exchange=exchange,
                instrument_id=instrument_id,
                style=self.params_map.kline_style
            )

            kline_generator.push_history_data()

            self.kline_generators[instrument_id] = kline_generator

        super().on_start()

    def on_tick(self, tick: TickData) -> None:
        """收到行情 tick 推送"""
        super().on_tick(tick)
        if tick.instrument_id not in self.kline_generators:
            return

        self.kline_generators[tick.instrument_id].tick_to_kline(tick)

    def calc_indicator(self) -> None:
        """计算指标数据"""

        # 指定合约计算指标
        self.kline_generators["ag2406"].producer.sma()

        # 也可以根据合约顺序获取合成器来计算指标
        # 0 代表第一个合约
        self.kline_generators[self.instrument_list[0]].producer.sma()
```

---

多合约不同周期

注意填写交易所、合约代码、K 线周期时候需要按照以下格式（必须按顺序依次对应，且使用英文分号 `;` 分隔）：

交易所：`SHFE;SHFE;CZCE`

合约代码：`ag2406;ag2405;AP405`

K 线周期：`M1;M5;M10`

```python {8,11-14,17-24,26,28,35-36,38,40-41,47,51-52,54}
from pythongo.classdef import TickData
from pythongo.core import KLineStyleType
from pythongo.utils import KLineGenerator

class Demo(...):
    def __init__(self) -> None:
        self.kline_generators: dict[str, dict[KLineStyleType, KLineGenerator]] = {}
        """K 线合成器容器"""

    @property
    def style_list(self) -> list[KLineStyleType]:
        """手动拆分 K 线周期"""
        return self.params_map.kline_style.split(";")

    def on_start(self) -> None:
        for exchange, instrument_id, style in zip(self.exchange_list, self.instrument_list, self.style_list):
            kline_generator = KLineGenerator(
                real_time_callback=self.real_time_callback,
                callback=self.callback,
                exchange=exchange,
                instrument_id=instrument_id,
                style=style
            )

            kline_generator.push_history_data()

            self.kline_generators[instrument_id] = {style: kline_generator}

        super().on_start()

    def on_tick(self, tick: TickData) -> None:
        """收到行情 tick 推送"""
        super().on_tick(tick)
        if tick.instrument_id not in self.kline_generators:
            return

        style_container = self.kline_generators[tick.instrument_id]

        for kline_generator in style_container.values():
            kline_generator.tick_to_kline(tick)

    def calc_indicator(self) -> None:
        """计算指标数据"""

        # 指定合约和周期计算指标
        self.kline_generators["ag2406"]["M1"].producer.sma()

        # 也可以根据合约顺序获取合成器来计算指标
        # 0 代表第一个
        instrument_id = self.instrument_list[0]
        style = self.style_list[0]

        self.kline_generators[instrument_id][style].producer.sma()
```

## 线图 UI [#kline_ui]

自定义副图显示指标

定义 `sub_indicator_data`，然后传参给 `self.widget.recv_kline`

```py {2-9,15}
class Demo(...):
    @property
    def sub_indicator_data(self) -> dict[str, float]:
        """副图指标"""
        return {
            "K": ...,
            "D": ...,
            "J": ...,
        }

    def callback(self, kline: KLineData) -> None:
        """接受 K 线回调"""
        self.widget.recv_kline({
            "kline": ...,
            **self.sub_indicator_data
        })
```

## 查询持仓 [#get_position]

查询 `ag2602` 的持仓

```py
class Demo(...):
    def on_start(self) -> None:
        super().on_start()

        position = self.get_position("ag2602")

        # 总持仓
        position.position

        # 净持仓
        position.net_position

        # 多头总持仓
        position.long.position

        # 空头今持仓
        position.short.td_position_close

        # 空头昨持仓
        position.short.yd_position_close

        # 今日买开数量
        position.long.open_volume

        # 今日买平数量
        position.long.close_volume

        # 使用字符串仅获取空头持仓
        short_position = self.get_position("ag2602").get_single_position("short")
        short_position.position # 空头总持仓

        # 获取套保持仓
        position = self.get_position("ag2602", hedgeflag="3")
        position.long.position # 套保多头总持仓

        # 获取指定帐号持仓
        position = self.get_position("ag2602", investor="888888")
        position.position # 指定帐号总持仓

        # 获取实时的持仓
        position = self.get_position("ag2602", simple=True)
        position.position # 该持仓会在报单成交后立刻更新
```

----

获取全部持仓（仅 `v2025.1112` 之后版本可用）

```py {5-9}
class Demo(...):
    def on_start(self) -> None:
        super().on_start()

        position = self.get_all_position()  # 所有帐号所有合约的所有持仓
        position["888888"]  # 888888 帐号的全部持仓数据
        position["888888"]["ag2602"]  # 888888 帐号下 ag2602 的全部持仓数据
        position["888888"]["ag2602"]["3"]  # 888888 帐号下 ag2602 的套保持仓数据
        position["888888"]["ag2602"]["1"].long  # 888888 帐号下 ag2602 的多头持仓数据
```

## 外部指标 [#external_indicator]

使用**麦语言**，**通达信**和**同花顺**中常见的指标

先下载 [转换指标库文件](https://infinitrader-file.quantdo.com.cn/pythongo/strategy/MyTT.py)，然后把文件放在和无限易安装目录中的 `pyStrategy` 目录中

```text
InfiniTrader_Simulation/
  pyStrategy/
    pythongo/
    MyTT.py
```

```py {1,8-9}
from MyTT import MA

class Demo(...):
    def on_start(self) -> None:
        super().on_start()

        ma5 = MA(self.kline_generator.producer.close, 5) # 获取 5 日均线序列
        ma10 = MA(self.kline_generator.producer.close, 10) # 获取 10 日均线序列
```

别的函数使用方法，请打开该文件自行查看（该指标转换算法来源于开源项目：[MyTT](https://github.com/mpquant/MyTT)，无限易和 PythonGO 不对指标计算差异所导致的任何损失负责！）

持续更新中...
