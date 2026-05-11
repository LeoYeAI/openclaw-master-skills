# 第二个策略

> [!INFO]
> 请注意，本文将不会和前面文章一样写的很详细，一些已经提过的细节将可能不会再提起，如果你对一些代码还有疑惑，建议你仔细阅读「教程」中的全部文档

现在我们已经有了一些编写策略的基础了，准备开始写第二个策略，这个策略我们将使用到 K 线图，并在 K 线图上显示 `MA` 主图指标数据

## 编写代码 [#coding]

#### 定义参数映射 [#def-params]

我们定义以下 5 个参数，方便我们在无限易 PythonGO 窗口控制 K 线的周期，指标周期...

注意 `fast_period`，我们在 `Field` 中用了一个 `ge` 参数，这个参数的意思是大于或者等于（`greater than or equal to`）设置的值，我们设置 `2{:py}`，表示 `fast_period` 只接受大于等于 `2{:py}` 的数字

```py filename="DemoKLine.py" {5}
class Params(BaseParams):
    """参数映射模型"""
    exchange: str = Field(default="", title="交易所代码")
    instrument_id: str = Field(default="", title="合约代码")
    fast_period: int = Field(default=5, title="快均线周期", ge=2)
    slow_period: int = Field(default=20, title="慢均线周期")
    kline_style: KLineStyleType = Field(default="M1", title="K 线周期")
```

#### 定义实例变量 [#def-instance-var]

我们需要实例化参数映射模型，然后定义两个存储快均线和慢均线值的实例变量

```py filename="DemoKLine.py" {8,10-11}
from pythongo.ui import BaseStrategy

class DemoKLine(BaseStrategy):
    """我的第二个策略"""
    def __init__(self) -> None:
        super().__init__()
        self.params_map = Params()

        self.fast_ma = 0.0
        self.slow_ma = 0.0
```

#### 线图指标定义 [#def-ui-indicator]

详细的文档请看 [策略规范 - 线图指标定义](../styleguide/strategy_rules.mdx#def-ui-indicator)

```py filename="DemoKLine.py"
from pythongo.ui import BaseStrategy

class DemoKLine(BaseStrategy):
    ...

    @property
    def main_indicator_data(self) -> dict[str, float]:
        """主图指标"""
        return {
            f"MA{self.params_map.fast_period}": self.fast_ma,
            f"MA{self.params_map.slow_period}": self.slow_ma,
        }
```

#### 定义回调 [#def-pythongo-callback]

##### `on_start()`

我们需要在运行策略的时候定义一个 K 线合成器 `KLineGenerator`，它可以帮助我们获取历史数据，并合成 K 线

`push_history_data` 是推送历史数据的方法，如果不调用，则不会推送历史数据到 `callback` 函数中

这里还需要注意一点，定义 K 线合成器和推送历史数据的代码，要写在 `super().on_start(){:py}` 前面，这是因为父类的 `on_start(){:py}` 会设置 `self.trading{:py}` 为 `True{:py}`，这样一来可能会导致我们推送的历史数据触发交易信号，然后报单，如果我们写在父类的 `on_start(){:py}` 前面，则没有这个问题，这也是比较特殊的一点

```py filename="DemoKLine.py" {2,9-16}
from pythongo.ui import BaseStrategy
from pythongo.utils import KLineGenerator

class DemoKLine(BaseStrategy):
    ...

    def on_start(self) -> None:
        self.kline_generator = KLineGenerator(
            real_time_callback=self.real_time_callback,
            callback=self.callback,
            exchange=self.params_map.exchange,
            instrument_id=self.params_map.instrument_id,
            style=self.params_map.kline_style
        )
        self.kline_generator.push_history_data()
        super().on_start()
```

参考文档：

* [K 线合成器](../modules/pythongo_utils.mdx#kline-generator)

##### `on_tick()`

`on_tick` 是最常用的回调，它可以收到无限易推送过来的行情 tick，有了 tick 数据我们才可以进行一系列操作

在当前例子中，我们需要在 `on_tick` 回调中将 tick 数据传给「K 线合成器」的 `tick_to_kline` 方法（[K 线合成器 - `tick_to_kline`](../modules/pythongo_utils#kline-generator-tick_to_kline)）来合成 K 线

```py filename="DemoKLine.py" {11}
from pythongo.ui import BaseStrategy
from pythongo.classdef import TickData

class DemoKLine(BaseStrategy):
    ...

    def on_tick(self, tick: TickData) -> None:
        """收到行情 tick 推送"""
        super().on_tick(tick)
        self.kline_generator.tick_to_kline(tick)
```

#### 自定义函数 [#def-custom-function]

##### `calc_indicator()`

既然我们想在 K 线图上显示指标数据，那我们就得写一个计算指标的函数，然后对定义好的两个实例变量 `fast_ma`, `slow_ma` 赋值

我们定义的 K 线合成器 `self.kline_generator` 有 `producer`（K 线生产器）属性，而 K 线生产器继承了技术指标类，所以可以写出以下计算指标代码，我们使用 `sma` 指标来计算两个周期的指标

```py filename="DemoKLine.py" {9-11,13-15}
from pythongo.ui import BaseStrategy

class DemoKLine(BaseStrategy):
    ...

    def calc_indicator(self) -> None:
        """计算指标数据"""
        self.slow_ma = self.kline_generator.producer.sma(
            timeperiod=self.params_map.slow_period
        )

        self.fast_ma = self.kline_generator.producer.sma(
            timeperiod=self.params_map.fast_period
        )
```

参考文档：

* 技术指标类：[深入框架 - pythongo.indicator](../modules/pythongo_indicator.mdx)

* K 线生产器：[深入框架 - pythongo.utils - KLineProducer](../modules/pythongo_utils.mdx#klineproducer)

##### `callback()`

推送 K 线回调

在 `on_start(){:py}` 中，我们要把这个函数传给 K 线合成器（`KLineGenerator`）的 `callback` 参数，然后当合成器得到一根我们预设的周期的 K 线时，就会调用这个回调函数，并且把这根 K 线传过来，我们就能得到最新的一根 K 线，当然，历史数据的 K 线也是从这个回调中传入

在这个函数中，因为得到了新的一根 K 线，我们需要调用上面的计算指标数据函数 `self.calc_indicator(){:py}` 来计算最新的指标，然后调用 `self.widget` 的 `recv_kline(){:py}` 方法来接受 K 线和指标数据（`**` 代表解包），将其更新到 K 线图上

是不是很奇怪，这个 `self.widget` 哪来的？

原因很简单，还记得我们之前说，用 K 线图的话，就要从 `pythongo.ui` 中导入基础父类模版吗？我们在 `ui` 模块的父类模版中添加了这些专用于 K 线图的属性，`self.widget` 就来自于那里，所以就不用自己定义了

```py filename="DemoKLine.py" {2,10,12-15}
from pythongo.classdef import KLineData
from pythongo.ui import BaseStrategy

class DemoKLine(BaseStrategy):
    ...

    def callback(self, kline: KLineData) -> None:
        """接受 K 线回调"""
        self.calc_indicator()

        self.widget.recv_kline({
            "kline": kline,
            **self.main_indicator_data
        })
```

参考文档：

* [深入框架 - pythongo.ui](../modules/pythongo_ui.mdx)

* [策略规范 - 导入父类](../styleguide/strategy_rules.mdx#import)

##### `real_time_callback()`

实时推送 K 线回调, 推送频率和 tick 相同

当 K 线有更新，这个回调函数就会被调用，我们可以在里面计算实时指标，或者根据这个频率的 K 线来实现一些高频的操作

在这里，我们仅需计算指标和把 K 线数据更新到线图上，所以我们直接调用 `callback(){:py}`，免得写两份一样的代码了

```py filename="DemoKLine.py" {10}
from pythongo.classdef import KLineData
from pythongo.ui import BaseStrategy

class DemoKLine(BaseStrategy):
    ...

    def real_time_callback(self, kline: KLineData) -> None:
        """使用收到的实时推送 K 线来计算指标并更新线图"""
        self.callback(kline)
```

#### 完整代码 [#complete]

这样，一个简单的带指标的 K 线图策略就完成了

我们可以通过无限易 PythonGO 窗口修改指标周期或者 K 线周期，启动策略后就能看到对应周期的 K 线图了

对了，在我们这个策略中，没有定义状态映射模型（`State`），这是允许的，如果策略不需要在状态栏显示数据，则无需定义该模型

K 线支持的类型，看这里：[深入框架 - pythongo.core - KLineStyle](../modules/pythongo_core.mdx#klinestyle)

```py filename="DemoKLine.py" copy
from pythongo.base import BaseParams, Field
from pythongo.classdef import KLineData, TickData
from pythongo.core import KLineStyleType
from pythongo.ui import BaseStrategy
from pythongo.utils import KLineGenerator

class Params(BaseParams):
    """参数映射模型"""
    exchange: str = Field(default="", title="交易所代码")
    instrument_id: str = Field(default="", title="合约代码")
    fast_period: int = Field(default=5, title="快均线周期", ge=2)
    slow_period: int = Field(default=20, title="慢均线周期")
    kline_style: KLineStyleType = Field(default="M1", title="K 线周期")

class DemoKLine(BaseStrategy):
    """我的第二个策略"""
    def __init__(self) -> None:
        super().__init__()
        self.params_map = Params()

        self.fast_ma = 0.0
        self.slow_ma = 0.0

    @property
    def main_indicator_data(self) -> dict[str, float]:
        """主图指标"""
        return {
            f"MA{self.params_map.fast_period}": self.fast_ma,
            f"MA{self.params_map.slow_period}": self.slow_ma,
        }

    def on_start(self) -> None:
        self.kline_generator = KLineGenerator(
            real_time_callback=self.real_time_callback,
            callback=self.callback,
            exchange=self.params_map.exchange,
            instrument_id=self.params_map.instrument_id,
            style=self.params_map.kline_style
        )
        self.kline_generator.push_history_data()
        super().on_start()

    def on_stop(self) -> None:
        super().on_stop()

    def on_tick(self, tick: TickData) -> None:
        """收到行情 tick 推送"""
        super().on_tick(tick)
        self.kline_generator.tick_to_kline(tick)

    def calc_indicator(self) -> None:
        """计算指标数据"""
        self.slow_ma = self.kline_generator.producer.sma(
            timeperiod=self.params_map.slow_period
        )

        self.fast_ma = self.kline_generator.producer.sma(
            timeperiod=self.params_map.fast_period
        )

    def callback(self, kline: KLineData) -> None:
        """接受 K 线回调"""
        self.calc_indicator()

        self.widget.recv_kline({
            "kline": kline,
            **self.main_indicator_data
        })

    def real_time_callback(self, kline: KLineData) -> None:
        """使用收到的实时推送 K 线来计算指标并更新线图"""
        self.callback(kline)
```
