# pythongo.base

本模块是最重要的一个模块，定义了一些父类，几乎所有策略都需要继承本模块中的父类。

## 继承简介 [#inherit]

在 Python 中，子类通过继承语法继承父类后，可以拥有父类的所有属性或方法，这样极大的减少了重复的代码，可以让代码更加简洁高效。

当我们继承父类后，拥有了父类的所有属性和方法，有时候我们需要对该父类的一些方法进行重写，但同时还需要继续使用父类的方法，这个时候就需要使用 `super()` 函数了。

因为我们对该方法重写后，再使用 `self.method_name()` 准备调用父类的方法，会发现其实调用的还是自身类（子类）的方法，也就是你自己重写后的方法，这个时候需要使用 `super().method_name()` 来调用父类的同名方法，就能达到我们想要的效果了。

具体的继承概念可以自行查阅互联网资料。

## `BaseParams`

参数映射模型

定义好的映射关系，会展示在「PythonGO 窗口 - 参数」一栏，这样就可以在界面直接编辑参数

默认定义了 `exchange`（交易所代码） 和 `instrument_id`（合约代码），这两个参数是固定参数，在继承本类后，你可以不再定义这两个参数，但建议还是**显式**的定义这两个参数。

## `BaseState`

状态映射模型

定义好的映射关系，会展示在「PythonGO 窗口 - 状态」一栏，数据仅供显示，无法编辑

## `BaseStrategy`

策略模板

所有策略的父类，定义好了回调函数，以及一些全局变量，还封装了一些获取数据的方法

### `strategy_id`

类型：`int`

策略实例 ID

由无限易自动自增赋值，不可自行更改

一个客户端中，每创建一个实例，`ID` 加 `1`

### `strategy_name`

类型：`str`

策略实例名称

「创建实例」时填写的「实例名称」，由无限易自动赋值，不可自行更改

### `params_map`

类型：`BaseParams`

实例化后的参数映射模型 `BaseParams`，用于父类参数映射

### `state_map`

类型：`BaseState`

实例化后的状态映射模型 `BaseState`，用于父类状态映射

### `limit_time`

类型：`int`

错单限制时间（单位：秒）

控制错单后 N 秒不报单，防止错单后继续发单

### `trading`

类型：`bool`

是否允许交易

可以控制报单函数是否对外报单，如果设为 `False`，则即使调用报单函数也不会报单。

### `class_name`

类型：`str`

策略的类名

### `exchange_list`

类型：`list[str]`

交易所列表

通过分号分割 `params_map` 中的 `exchange` 得到

实现方法为：

```python
self.params_map.exchange.split(";")
```

### `instrument_list`

类型：`list[str]`

合约列表

通过分号分割 `params_map` 中的 `instrument_id` 得到

实现方法为：

```python
self.params_map.instrument_id.split(";")
```

### `instance_file`

类型：`str`

保存的实例信息文件路径

### `get_params()`

获取策略参数

> [!INFO]
> 无限易调用此方法来获取定义好的属性和对应的值，自己无需使用

返回：

| 类型 | 描述 |
|---|---|
| `list[dict[str | str |

### `set_params()`

设置策略参数

> [!INFO]
> 修改界面参数时无限易主动调用，自己无需使用

参数：

| 参数名 | 类型 | 描述 |
|---|---|---|
| `data` | `dict[str | str |
| ` |
| 修 | 改 | 后 | 的 | 界 | 面 | 参 | 数 | 数 | 据 |

### `update_status_bar()`

更新无限易 PythonGO 窗口状态栏显示值

### `save_instance_file()`

保存实例信息

暂停策略时会主动调用

### `load_instance_file()`

加载实例文件并对策略设置对应属性

`on_init` 会主动调用

### `on_init()`

创建实例回调

界面创建实例或加载实例会触发此方法

### `on_start()`

启动策略回调

界面点击运行按钮会触发此方法

> [!INFO]
> 此方法会将 `self.trading` 设置为 `True`，然后订阅合约行情

### `on_stop()`

停止策略回调

界面点击暂停按钮会触发此方法

> [!INFO]
> 此方法会将 `self.trading` 设置为 `False`，保存实例信息，然后取消订阅合约行情

### `on_tick()`

收到行情 tick 推送回调

参数：

| 参数名 | 类型 | 描述 |
|---|---|---|
| `tick` | `TickData` | 行情切片数据对象 |

### `on_contract_status()`

合约状态变化回调

参数：

| 参数名 | 类型 | 描述 |
|---|---|---|
| `status` | `InstrumentStatus` | 合约状态对象 |

### `on_cancel()`

收到撤单推送回调

> [!INFO]
> 本函数在 `v2025.0801` 版本新增，新版本请使用本回调，旧版本的 `on_order_cancel` 将在未来被弃用

参数：

| 参数名 | 类型 | 描述 |
|---|---|---|
| `order` | `CancelOrderData` | 撤单数据对象 |

### `on_order_trade()`

收到报单成交推送回调

回调是 `on_order` 主动触发的，等同于 `on_trade`，最好使用 `on_trade`

参数：

| 参数名 | 类型 | 描述 |
|---|---|---|
| `order` | `OrderData` | 报单数据对象 |

### `on_order()`

报单变化回调

> [!INFO]
> 报单成功就会进入此回调

参数：

| 参数名 | 类型 | 描述 |
|---|---|---|
| `order` | `OrderData` | 报单数据对象 |

### `on_trade()`

报单成交推送回调

参数：

| 参数名 | 类型 | 描述 |
|---|---|---|
| `trade` | `TradeData` | 成交数据对象 |
| `log` | `bool` | 是否输出成交日志 |

### `on_error()`

收到报单错误推送回调

参数：

| 参数名 | 类型 | 描述 |
|---|---|---|
| `error` | `dict[str | str |
| ` |
| 错 | 误 | 信 | 息 |   | 包 | 含 |   | e | r | r | C | o | d | e |   | ( | 错 | 误 | 代 | 码 | ) | , |   | e | r | r | M | s | g |   | ( | 错 | 误 | 信 | 息 | ) | , |   | o | r | d | e | r | I | D |   | ( | 报 | 单 | 编 | 号 | ) |   |

其中有几点需要注意：

* 当 `errCode` 为 `0004` 的时候，是撤单错误，你可以根据该值做一些撤单错误后的处理。

* 函数运行错误和报单错误都会进入此回调，所以 `error` 如果有 `orderID` 键，那就是属于报单错误的回调，反之则是函数运行错误

### `pause_strategy()`

暂停策略函数

效果和客户端点击暂停一样

> [!ERROR]
> 请勿在 `on_start` 和 `on_stop` 中使用本方法，否则会进入死循环

### `output()`

输出信息到控制台

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `*msg` | `Any` | 准备输出的信息，支持任意类型和任意参数 | 必填 |

### `sub_market_data()`

订阅合约行情函数

> [!INFO]
> 使用此方法订阅合约时，交易所代码和合约代码可以为空，当两者为空时，会自动取 `self.exchange_list` 和 `self.instrument_list` 中的合约来订阅

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `exchange` | `str` | 交易所代码 | None |
| `instrument_id` | `str` | 合约代码 | None |

### `unsub_market_data()`

取消订阅合约行情函数

> [!INFO]
> 同 `sub_market_data` 注意事项
                                                                                                                                                                                        

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `exchange` | `str` | 交易所代码 | None |
| `instrument_id` | `str` | 合约代码 | None |

### `sync_position()`

同步持仓数据函数

该方法会从无限易获取**所有帐号**的持仓并存储到 `self._position` 中。 使用 `self.get_position()` 函数时，会自动调用该方法，如无特殊情况，自己无需调用。

### `get_all_position()`

获取所有帐号的所有持仓

> [!INFO]
> 本函数在 `v2025.1112` 版本新增

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `simple` | `bool` | 简化持仓数据（但持仓是实时的） | False |

返回：

| 类型 | 描述 |
|---|---|
| `dict[str | dict[str | dict[str | Position |

> [!INFO]
> 返回的数据类型为字典，如要取合约双向持仓，顺序为：投资者帐号 -> 合约代码 -> 投机套保标志，参考代码：`position.get(investor, {}).get(instrument_id, {}).get(hedgeflag)`

### `get_position()`

获取持仓数据函数

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `instrument_id` | `str` | 合约代码 | 必填 |
| `hedgeflag` | `TypeHedgeFlag` | 投机套保标志 | "1" |
| `investor` | `str` | 资金账号（默认使用查询到的第一个帐号） | None |
| `simple` | `bool` | 简化持仓数据（但持仓是实时的） | False |

> [!INFO]
> `simple` 字段在 `v2025.0522` 后的版本中新增，当 `simple` 为 `True` 的时候，获取到的持仓是实时的，不会再有延迟的情况，但是以下这些字段没有数据：`position_cost`, `yd_position_cost`, `close_profit`, `position_profit`, `open_avg_price`, `position_avg_price`, `used_margin`，具体字段的中文说明请看：[深入框架 - pythongo.classdef - position](../modules/pythongo_classdef/position.mdx#position_p)

返回：

| 类型 | 描述 |
|---|---|
| `Position` | 单合约的双向持仓数据 |

### `send_order()`

报单函数（开仓）

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `exchange` | `str` | 交易所代码 | 必填 |
| `instrument_id` | `str` | 合约代码 | 必填 |
| `volume` | `int` | 报单手数 | 必填 |
| `price` | `float | int` | 报单价格 | 必填 |
| `order_direction` | `TypeOrderDIR` | 报单方向 | 必填 |
| `order_type` | `TypeOrderFlag` | 报单指令 | "GFD" |
| `investor` | `str` | 报单账号 | "" |
| `hedgeflag` | `TypeHedgeFlag` | 投机套保标志 | "1" |
| `market` | `bool` | True 市价单，False 非市价单 | False |
| `memo` | `Any` | 报单备注 | None |

返回：

| 类型 | 描述 |
|---|---|
| `int | None` | 报单编号（-1 为报单失败） |

### `auto_close_position()`

自动平仓函数（平今优先）

> [!WARNING]
> 当平上期所、能源中心仓位的时候，如果既平了昨仓，又平了今仓，只会返回最后一次平仓的报单编号

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `exchange` | `str` | 交易所代码 | 必填 |
| `instrument_id` | `str` | 合约代码 | 必填 |
| `volume` | `int` | 报单手数 | 必填 |
| `price` | `float | int` | 报单价格 | 必填 |
| `order_direction` | `TypeOrderDIR` | 报单方向 | 必填 |
| `order_type` | `TypeOrderFlag` | 报单指令 | "GFD" |
| `investor` | `str` | 报单账号 | "" |
| `hedgeflag` | `TypeHedgeFlag` | 投机套保标志 | "1" |
| `shfe_close_first` | `bool` | 上期平仓（昨仓）优先 | False |
| `market` | `bool` | True 市价单，False 非市价单 | False |
| `memo` | `Any` | 报单备注 | None |

返回：

| 类型 | 描述 |
|---|---|
| `int | None` | 报单编号（-1 为报单失败） |

### `cancel_order()`

撤单函数

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `order_id` | `int` | 报单编号 | 必填 |

返回：

| 类型 | 描述 |
|---|---|
| `int` | -1 表示报单编号不存在，0 表示撤单请求发送成功（不代表撤单成功） |

### `make_order_req()`

发送报单请求函数

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `exchange` | `str` | 交易所代码 | 必填 |
| `instrument_id` | `str` | 合约代码 | 必填 |
| `volume` | `int` | 报单手数 | 必填 |
| `price` | `float | int` | 报单价格 | 必填 |
| `order_direction` | `TypeOrderDIR` | 报单方向（大写） | 必填 |
| `offset` | `TypeOffsetFlag` | 开平标志 | 必填 |
| `order_type` | `TypeOrderFlag` | 报单指令 | 必填 |
| `investor` | `str` | 报单账号 | 必填 |
| `hedgeflag` | `TypeHedgeFlag` | 投机套保标志 | 必填 |
| `market` | `bool` | True 市价单，False 非市价单 | False |
| `memo` | `Any` | 报单备注 | None |

返回：

| 类型 | 描述 |
|---|---|
| `int` | 报单编号（-1 为报单失败） |

### `get_account_fund_data()`

获取账号资金数据函数

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `investor` | `str` | 投资者账号 | 必填 |

返回：

| 类型 | 描述 |
|---|---|
| `AccountData` | 账号资金数据对象 |

### `get_instrument_data()`

获取合约信息函数

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `exchange` | `str` | 交易所代码 | 必填 |
| `instrument_id` | `str` | 合约代码 | 必填 |

返回：

| 类型 | 描述 |
|---|---|
| `InstrumentData` | 合约信息数据对象 |

### `get_instruments_by_product()`

查询指定品种的所有合约信息或者仅合约代码函数

> [!INFO]
> 品种代码可以在无限易的「期权 - T 型报价」窗口查询「交易所」和「品种」字段。ETF 期权品种代码是 `ETF_O`

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `exchange` | `str` | 交易所代码 | 必填 |
| `product_id` | `str` | 品种代码 | 必填 |
| `raw_data` | `bool` | 是否返回原始数据（如果传入 False 则列表中只返回合约代码） | True |

返回：

| 类型 | 描述 |
|---|---|
| `TypeInstResult` | 所有合约信息数据对象或者仅合约代码字段 |

### `get_investor_data()`

获取投资者信息函数

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `index` | `int` | 帐号的顺序（1 表示第一个，以此类推） | 1 |

返回：

| 类型 | 描述 |
|---|---|
| `InvestorData` | 投资者信息数据对象 |
