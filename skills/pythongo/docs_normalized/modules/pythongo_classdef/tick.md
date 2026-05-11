# `TickData`

## `TickData`

行情切片数据类

| 属性名 | 类型 | 说明 |
|---|---|---|
| `exchange` | `str` | 交易所代码 |
| `instrument_id` | `str` | 合约代码 |
| `last_price` | `float` | 最新价 |
| `open_price` | `float` | 今开盘价 |
| `high_price` | `float` | 最高价 |
| `low_price` | `float` | 最低价 |
| `volume` | `int` | 总成交量 |
| `last_volume` | `int` | 最新成交量 |
| `pre_close_price` | `float` | 昨收盘价 |
| `pre_settlement_price` | `float` | 昨结算价 |
| `open_interest` | `int` | 总持仓量 |
| `upper_limit_price` | `float` | 涨停板价 |
| `lower_limit_price` | `float` | 跌停板价 |
| `turnover` | `float` | 总成交金额 |
| `bid_price1` | `float` | 申买价一 |
| `bid_price2` | `float` | 申买价二 |
| `bid_price3` | `float` | 申买价三 |
| `bid_price4` | `float` | 申买价四 |
| `bid_price5` | `float` | 申买价五 |
| `ask_price1` | `float` | 申卖价一 |
| `ask_price2` | `float` | 申卖价二 |
| `ask_price3` | `float` | 申卖价三 |
| `ask_price4` | `float` | 申卖价四 |
| `ask_price5` | `float` | 申卖价五 |
| `bid_volume1` | `int` | 申买量一 |
| `bid_volume2` | `int` | 申买量二 |
| `bid_volume3` | `int` | 申买量三 |
| `bid_volume4` | `int` | 申买量四 |
| `bid_volume5` | `int` | 申买量五 |
| `ask_volume1` | `int` | 申卖量一 |
| `ask_volume2` | `int` | 申卖量二 |
| `ask_volume3` | `int` | 申卖量三 |
| `ask_volume4` | `int` | 申卖量四 |
| `ask_volume5` | `int` | 申卖量五 |
| `trading_day` | `str` | 交易日 |
| `update_time` | `str` | 更新时间 |
| `datetime` | `TypeDateTime` | 时间 |

### `copy()`

浅拷贝自身

返回：

| 类型 | 描述 |
|---|---|
| `TickData` | 浅拷贝后的 TickData |

### `update()`

更新属性（正常情况下使用不到）

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `**kwargs` | 键值对 | tick 的属性与值 | 必填 |
