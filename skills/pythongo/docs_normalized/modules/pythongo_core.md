# pythongo.core

## MarketCenter

数据中心 API 类

提供一些扩展数据，供用户使用

> [!INFO]
> API 调用限制由 **AI** 自动管控，请避免频繁使用这些函数，比如有规律地频繁获取某些数据，就会被 **AI** 检测到。
>
>   由于使用了 **AI** 技术，所以没有具体的次数限制，一切都是 **AI** 决定是否对 IP 进行封禁。

### `get_kline_data()`

获取 K 线数据

> [!WARNING]
> 此 API 有调用限制，请合理使用，否则会永久封禁 IP

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `exchange` | `str` | 交易所代码 | 必填 |
| `instrument_id` | `str` | 合约代码 | 必填 |
| `style` | `KLineStyleType` | K 线周期, KLineStyle 枚举值 | `KLineStyle.M1` |
| `count` | `int` | 查询的 K 线数量（最大 1440），正值获取基准时间戳后的数据，负值为之前 | `-1440` |
| `origin` | `int` | 基准时间戳（毫秒） | `None` |
| `start_time` | `TypeDateTime` | K 线起始时间 | `None` |
| `end_time` | `TypeDateTime` | K 线结束时间 | `None` |
| `simply` | `bool` | 极简 K 线, 只返回带有 OHLC 和时间的 K 线 | `True` |

返回：

| 类型 | 描述 |
|---|---|
| `list[dict |
| ` |
| K |   | 线 | 数 | 据 |

注意：

使用 `start_time` 和 `end_time` 可以获取一个时间区间的 K 线，但同时这样会忽略 `count` 和 `origin` 参数

也就是说要么按时间区间获取，要么按 K 线数量获取 K 线数据

### `get_kline_data_by_day()`

按天数（交易日）获取 K 线数据

> [!WARNING]
> 此 API 有调用限制，请合理使用，否则会永久封禁 IP

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `exchange` | `str` | 交易所代码 | 必填 |
| `instrument_id` | `str` | 合约代码 | 必填 |
| `day_count` | `int` | 查询 N 天的数据，正值获取基准时间戳后的数据，负值为之前 | 必填 |
| `origin` | `int` | 基准时间戳（毫秒） | `None` |
| `style` | `KLineStyleType` | K 线周期，KLineStyle 枚举值，仅支持 M1, M5, M15, M30, H1 | `KLineStyle.M1` |
| `simply` | `bool` | 极简 K 线, 只返回带有 OHLC 和时间的 K 线 | `True` |

返回：

| 类型 | 描述 |
|---|---|
| `list[dict |
| ` |
| K |   | 线 | 数 | 据 |

### `get_dominant_list()`

获取交易所的主连合约列表

> [!WARNING]
> 此 API 有调用限制，请合理使用，否则会永久封禁 IP

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `exchange` | `str` | 交易所代码 | 必填 |

返回：

| 类型 | 描述 |
|---|---|
| `list[str |
| ` |
| 主 | 连 | 合 | 约 | 列 | 表 |

### `get_instrument_trade_time()`

查询带交易日的合约交易时段

> [!WARNING]
> 此 API 有调用限制，请合理使用，否则会永久封禁 IP

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `exchange` | `str` | 交易所代码 | 必填 |
| `instrument_id` | `str` | 合约代码 | 必填 |
| `instant` | `int` | 基准时间戳（毫秒） | `None` |

返回：

| 类型 | 描述 |
|---|---|
| `dict` | 合约交易时段信息 |

### `get_product_trade_time()`

查询品种的交易时段信息

> [!WARNING]
> 此 API 有调用限制，请合理使用，否则会永久封禁 IP

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `exchange` | `str` | 交易所代码 | 必填 |
| `product_id` | `str` | 品种代码，也可填写合约代码 | 必填 |
| `trading_day` | `str` | 品种交易日，格式为 `%Y%m%d`，例如：20240101 | `None` |

返回：

| 类型 | 描述 |
|---|---|
| `dict` | 品种交易时段信息 |

### `get_avl_close_time()`

从缓存中获取合约可使用的收盘时间序列，如无缓存, 则获取不到任何数据

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `instrument_id` | `str` | 合约代码 | 必填 |

返回：

| 类型 | 描述 |
|---|---|
| `list[datetime |
| ` |
| 在 | 当 | 前 | 时 | 间 | 之 | 后 | 的 | 收 | 盘 | 时 | 间 | 序 | 列 |

### `get_next_gen_time()`

根据提供的合约信息、时间和 K 线周期，获取下一根 K 线生成时间

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `exchange` | `str` | 交易所代码 | 必填 |
| `instrument_id` | `str` | 合约代码 | 必填 |
| `tick_time` | `datetime` | tick 时间 | 必填 |
| `style` | `KLineStyleType` | K 线周期, KLineStyle 枚举值 | 必填 |

返回：

| 类型 | 描述 |
|---|---|
| `datetime` | 下一根 K 线生成时间 |

## KLineStyle

K 线周期

枚举类型，分别有以下枚举值

| 风格 | 分钟数 | 备注 |
|---|---|---|
| M1 | 1 | 1 分钟 |
| M2 | 2 | 2 分钟 |
| M3 | 3 | 3 分钟 |
| M4 | 4 | 4 分钟 |
| M5 | 5 | 5 分钟 |
| M10 | 10 | 10 分钟 |
| M15 | 15 | 15 分钟 |
| M30 | 30 | 30 分钟 |
| M45 | 45 | 45 分钟 |
| H1 | 60 | 1 小时 |
| H2 | 120 | 2 小时 |
| H3 | 180 | 3 小时 |
| H4 | 240 | 4 小时 |
| D1 | 1440 | 日线 |

## KLineStyleType

K 线周期类型

`type` 类型，用于类型注释
