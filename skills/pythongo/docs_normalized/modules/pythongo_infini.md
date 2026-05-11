# pythongo.infini

此模块重新封装了 `INFINIGO` 模块，一方面是为了更好的支持类型注释，另一方面更方便扩展代码

对于编写代码而言，`INFINIGO` 模块已经变得无关紧要，事实上，此模块你也仅需要了解一下即可，除非要进行一些特殊的操作，否则大部分情况下都不会直接用到此模块的方法

## `update_param()`

界面传入参数在实例中更新

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `strategy_id` | `int` | 策略 ID | 必填 |
| `data` | `dict[str | str |
| ` |
| 映 | 射 | 的 | 参 | 数 | 字 | 典 |
| 必 | 填 |

## `update_state()`

更新无限易 PythonGO 窗口状态栏显示值

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `strategy_id` | `int` | 策略 ID | 必填 |
| `data` | `dict[str | str |
| ` |
| 映 | 射 | 的 | 状 | 态 | 字 | 典 |
| 必 | 填 |

## `pause_strategy()`

暂停策略

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `strategy_id` | `int` | 策略 ID | 必填 |

## `write_log()`

输出日志到控制台

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `msg` | `Any` | 需要输出的日志内容 | 必填 |

## `sub_market_data()`

订阅合约行情

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `strategy_obj` | `object` | 策略实例 | 必填 |
| `exchange` | `str` | 交易所代码 | 必填 |
| `instrument_id` | `str` | 合约代码 | 必填 |

## `unsub_market_data()`

取消订阅合约行情

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `strategy_obj` | `object` | 策略实例 | 必填 |
| `exchange` | `str` | 交易所代码 | 必填 |
| `instrument_id` | `str` | 合约代码 | 必填 |

## `send_order()`

发单函数

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `strategy_id` | `int` | 策略实例 ID | 必填 |
| `exchange` | `str` | 交易所代码 | 必填 |
| `instrument_id` | `str` | 合约代码 | 必填 |
| `volume` | `int` | 报单数量 | 必填 |
| `price` | `int | float` | 报单价格 | 必填 |
| `direction` | `Literal["0" | 1 |
| ` |
| 报 | 单 | 方 | 向 | ： | ` | 0 | ` |   | 买 | ， | ` | 1 | ` |   | 卖 |
| 必 | 填 |

返回：

| 类型 | 描述 |
|---|---|
| `int` | 报单编号（-1 为报单失败） |

## `cancel_order()`

撤单函数

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `order_id` | `int` | 报单编号 | 必填 |

返回：

| 类型 | 描述 |
|---|---|
| `int` | -1 表示 order_id 不存在，0 表示撤单请求发送成功（不代表撤单成功） |

## `get_instrument()`

获取合约信息

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `exchange` | `str` | 交易所代码 | 必填 |
| `instrument_id` | `str` | 合约代码 | 必填 |

返回：

| 类型 | 描述 |
|---|---|
| `ObjDataType` | 合约信息 |

## `get_instruments_by_product()`

查询指定品种的所有合约信息

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `exchange` | `str` | 交易所代码 | 必填 |
| `product_id` | `str` | 品种代码 | 必填 |

返回：

| 类型 | 描述 |
|---|---|
| `list[ObjDataType |
| ` |
| 指 | 定 | 品 | 种 | 的 | 所 | 有 | 合 | 约 | 信 | 息 |

## `get_investor_list()`

获取所有的投资者信息

参数：

无

返回：

| 类型 | 描述 |
|---|---|
| `list[ObjDataType |
| ` |
| 当 | 前 | 登 | 录 | 的 | 所 | 有 | 投 | 资 | 者 | 信 | 息 |

## `get_investor_account()`

获取账号资金数据

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `investor` | `str` | 投资者账号 | 必填 |

返回：

| 类型 | 描述 |
|---|---|
| `ObjDataType` | 账号资金数据 |

## `get_investor_position()`

获取账号持仓

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `investor` | `str` | 投资者账号 | 必填 |
| `Simple` | `bool` | 简化持仓数据（但持仓是实时的） | False |

> [!INFO]
> `Simple` 字段在 `v2025.0522` 后的版本中新增，当 `Simple` 为 `True` 的时候，获取到的持仓是实时的，不会再有延迟的情况，但是持仓数据中不会有以下这些字段：`PositionCost`, `YdPositionCost`, `CloseProfit`, `PositionProfit`, `OpenAvgPrice`, `PositionAvgPrice`, `UsedMargin`
   

返回：

| 类型 | 描述 |
|---|---|
| `list[ObjDataType |
| ` |
| 账 | 号 | 持 | 仓 | 数 | 据 |
