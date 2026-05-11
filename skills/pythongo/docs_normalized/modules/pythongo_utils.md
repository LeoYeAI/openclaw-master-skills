# pythongo.utils

此模块为工具模块，很多重要的工具，例如：K 线合成器、定时器，就定义在这里

## `CustomLogHandler`

自定义日志 Handler

这个类的作用是，当你使用的 Python 库有自己的日志模块，那这个库所打印的消息你是看不到的，因为 PythonGO 的日志是通过传给无限易，然后展示在界面的，最后才存在文件里，并不是普通输出函数的那种标准输入输出模式。所以当遇到这种情况时，可以使用此 `Handler` 来对你使用的库的 `Logger` 新增一个 `Handler`

具体的使用方法可以自行百度，也可以参考定时器（`Scheduler`）的初始化函数中的代码

## `Scheduler()`

简易定时器

通过使用 `apscheduler` 中的 `BackgroundScheduler`（非阻塞定时器），实现一些必要的功能和语法糖，既可以统一定时器的使用规则，还方便用户理解。

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `scheduler_name` | `str` | 定时器名称 | None |

如果传入定时器名称, 则后续实例化同一定时器名称的类时, 都将返回同一内存地址的实例，此为**单例模式**

这样可以让你在不同的策略或实例中管理同一个定时器。

### `add_job()` [#Scheduler-add_job]

添加定时任务

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `func` | `Callable` | 定时任务函数 | 必填 |
| `trigger` | `Literal["date" | interval | cron |
| ` |
| 触 | 发 | 器 |
| 必 | 填 |

触发器 `trigger` 介绍：

* `date`：在某个确定的时间点运行你的任务函数 （只运行一次）

* `interval`：在固定的时间间隔周期性地运行你的任务函数

* `cron`：在一天的某些固定时间点周期性地运行你的任务函数

此方法用法和 `apscheduler` 完全一致，具体使用方法可以[看这里](https://sinhub.cn/2018/11/apscheduler-user-guide/)或者上网搜索，这里就不做过多解释了，因为每个触发器所需要的参数都是不一样的。

这里实现一个最简单的定时器：

```python copy
from datetime import datetime

from pythongo.utils import Scheduler

scheduler = Scheduler()

# 启用定时器
scheduler.start()

def foo():
    """任务函数"""
    print("Amazing PythonGO!")

# 添加定时器任务
scheduler.add_job(
    func=foo,
    trigger="interval",
    id="foo_print",
    seconds=5,
    next_run_time=datetime.now()
)

# 该任务会每隔五秒钟执行一次 foo 函数
# next_run_time 设置为当前时间，表示让定时任务立刻运行，如果没设置，则是五秒后才运行

# 移除定时器
scheduler.remove("foo_print")

# 或者直接停止定时器
# 注意：定时器停止以后，无法再启动，需要重新实例化定时器
scheduler.stop()
```

### `get_job()` [#Scheduler-get_job]

根据 `job_id` 获取对应的定时任务

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `job_id` | `str` | 任务备注 ID | 必填 |

返回：

| 类型 | 描述 |
|---|---|
| `apscheduler.job.Job` | 定时任务 |

### `get_jobs()` [#Scheduler-get_jobs]

返回所有定时任务

返回：

| 类型 | 描述 |
|---|---|
| `list[apscheduler.job.Job |
| ` |
| 所 | 有 | 定 | 时 | 任 | 务 |

### `remove_job()` [#Scheduler-remove_job]

根据 `job_id` 移除定时任务

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `job_id` | `str` | 任务备注 ID | 必填 |

### `start()` [#Scheduler-start]

启动定时器

### `stop()` [#Scheduler-stop]

停止定时器

> [!INFO]
> 如果使用**单例模式**，调用该方法会执行移除所有定时任务操作，并不会停止整个定时器

## `KLineGeneratorSec` [#KLine-Generator-Sec]

秒级 K 线生成器

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `callback` | `Callable[[KLineData |
| N | o | n | e |

### `tick_to_kline()` [#KLine-Generator-Sec-tick_to_kline]

合成秒级 K 线

接收 `tick` 来合成 K 线，当 K 线周期达到设置的周期，则通过上面传入的 `callback` 推送过去

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `tick` | `TickData` | tick 对象 | 必填 |

## `KLineGenerator` [#KLine-Generator]

分钟级 K 线合成

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `exchange` | `str` | 交易所代码 | 必填 |
| `instrument_id` | `str` | 合约代码 | 必填 |
| `callback` | `Callable[[KLineData |
| N | o | n | e |

### `exchange` [#KLine-Generator-exchange]

类型：`str`

交易所代码

### `instrument_id` [#KLine-Generator-instrument_id]

类型：`str`

合约代码

### `style` [#KLine-Generator-style]

类型：`KLineStyleType`

K 线周期

### `producer` [#KLine-Generator-producer]

类型：`KLineProducer`

K 线生产器（内置指标方法），[详细介绍](#kline-producer)

### `push_history_data()` [#KLine-Generator-push_history_data]

推送历史 K 线数据到回调

> [!INFO]
> 如果你不需要历史数据，则不用在实例化 `KLineGenerator` 后调用此方法

### `stop_push_scheduler()` [#KLine-Generator-stop_push_scheduler]

停止推送每个交易时段最后一根 K 线的定时器

> [!INFO]
> 在当前方法中，`self.scheduler` 是单例模式，所以只会移除所有的定时任务，不会停止本类中的定时器（一般用不到本方法）

### `tick_to_kline()` [#KLine-Generator-tick_to_kline]

合成 K 线

接收 `tick` 来合成 K 线，当 K 线周期达到设置的周期，则通过 `callback` 推送过去，如果定义了 `real_time_callback` 回调，则每次 K 线有更新，都会将最新的 K 线通过 `real_time_callback` 推送过去

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `tick` | `TickData` | tick 对象 | 必填 |
| `push` | `bool` | 直接推送 K 线（请不要填写该参数） | False |

## `KLineGeneratorArb`  [#KLine-Generator-Arb]

标准套利合约的分钟级 K 线合成器

所有功能继承自 `KLineGenerator`，重新实现了 `tick_to_kline`，可以接受套利合约的两腿合约 `tick`，然后合成一个新的 `tick`，再传入到父类的 `tick_to_kline`

所有方法和属性以及用法都和 `KLineGenerator` 一样，入参也一样，这里不重复介绍了（可以去看自带的示例套利策略）

> [!INFO]
> 支持套利合约的站点环境才能收到套利合约的行情

## `KLineContainer` [#KLine-Container]

K 线容器

可以自动缓存实例本身, 重复的交易所及合约不再重新获取 K 线

本类很简单，获取 K 线数据后，把数据缓存起来，然后供取用，但是数据不会自己更新（需要配合 `KLineGenerator` 合成 K 线后自动更新数据），所以一般不单独使用，如果只是需要取 K 线的话，可以查阅 [深入框架 - pythongo.core](./pythongo_core.mdx)

实例化本类后会自动调用 `init()` 方法来获取 K 线并缓存

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `exchange` | `str` | 交易所代码 | 必填 |
| `instrument_id` | `str` | 合约代码 | 必填 |
| `style` | `KLineStyleType` | K 线周期 | 必填 |

### `get()`

根据交易所, 合约和 K 线分钟获取缓存的 K 线

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `exchange` | `str` | 交易所代码 | 必填 |
| `instrument_id` | `str` | 合约代码 | 必填 |
| `style` | `KLineStyleType` | K 线周期 | 必填 |

返回：

| 类型 | 描述 |
|---|---|
| `list[dict |
| ` |
| K |   | 线 | 数 | 据 |

### `set()`

根据交易所, 合约和 K 线分钟缓存 K 线

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `exchange` | `str` | 交易所代码 | 必填 |
| `instrument_id` | `str` | 合约代码 | 必填 |
| `style` | `KLineStyleType` | K 线周期 | 必填 |
| `data` | `list[dict |
| ` |
| K |   | 线 | 数 | 据 |
| 必 | 填 |

### `init()`

获取合约 K 线并缓存

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `exchange` | `str` | 交易所代码 | 必填 |
| `instrument_id` | `str` | 合约代码 | 必填 |
| `style` | `KLineStyleType` | K 线周期 | 必填 |

## `KLineProducer` [#KLine-Producer]

K 线生产器

本类继承了 `Indicators`（[技术指标类](./pythongo_indicator.mdx)），所以可以直接使用对应的指标方法

本类可以单独使用，前提是你完全了解本类的用法，且不需要最新的 K 线数据，因为本类的数据一旦获取，不会再更新，除非手动更新

实例化本类会自动实例化 `KLineContainer`

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `exchange` | `str` | 交易所代码 | 必填 |
| `instrument_id` | `str` | 合约代码 | 必填 |
| `style` | `KLineStyleType` | K 线周期 | "M1" |
| `callback` | `Callable[[KLineData |
| N | o | n | e |

### `exchange`

类型：`str`

交易所代码

### `instrument_id`

类型：`str`

合约代码

### `style`

类型：`KLineStyleType`

K 线周期

### `kline_container`

类型：`KLineContainer`

实例化的 K 线容器

### `open`

类型：`list[np.float64]`

开盘价序列

### `close`

类型：`list[np.float64]`

收盘价序列

### `high`

类型：`list[np.float64]`

最高价序列

### `low`

类型：`list[np.float64]`

最低价序列

### `volume`

类型：`list[np.float64]`

成交量序列

### `datetime`

类型：`list[TypeDateTime]`

时间序列

### `update()`

更新数据序列

根据 K 线时间自动添加、插入数据，或者更新最后一根 K 线数据

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `kline` | `KLineData` | K 线对象 | 必填 |

### `append_data()`

添加 K 线数据

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `kline` | `KLineData` | K 线对象 | 必填 |

### `insert_data()`

根据数组下标插入 K 线数据

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `kline` | `KLineData` | K 线对象 | 必填 |
| `index` | `int` | K 线插入的位置 | -1 |

### `update_last_kline()`

更新最后一根 K 线数据

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `kline` | `KLineData` | K 线对象 | 必填 |

### `worker()`

将 K 线数据转成 K 线对象后更新到本实例中的 K 线数据序列，并且推送到 K 线回调中，这部分数据也称 K 线历史数据

## `isdigit()`

判断字符串是否整数或小数

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `value` | `str` | 任意字符串 | 必填 |

返回：

| 类型 | 描述 |
|---|---|
| `bool` | 是否整数或小数 |

## `split_arbitrage_code()`

分割套利合约代码

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `instrument_id` | `str` | 标准套利合约代码 | 必填 |

返回：

| 类型 | 描述 |
|---|---|
| `tuple[Optional[str |
| O | p | t | i | o | n | a | l | [ | s | t | r |
