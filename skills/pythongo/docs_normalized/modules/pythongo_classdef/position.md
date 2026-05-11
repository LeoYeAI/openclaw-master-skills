# `Position`

## `Position`

合约持仓数据类

| 属性名 | 类型 | 说明 |
|---|---|---|
| `long` | `Position_p` | 合约多头持仓 |
| `short` | `Position_p` | 合约空头持仓 |
| `net_position` | `int` | 合约净持仓 |
| `position` | `int` | 合约总持仓 |

### `get_single_position()`

获取单边持仓函数

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `direction` | `Literal["long" | short |
| ` |
| 持 | 仓 | 方 | 向 | （ | l | o | n | g |   | 多 | 头 | 持 | 仓 | , |   | s | h | o | r | t |   | 空 | 头 | 持 | 仓 | ） |
| 必 | 填 |

返回：

| 类型 | 描述 |
|---|---|
| `Position_p` | 单向持仓数据类 |

## `Position_p`

单向持仓数据类

| 属性名 | 类型 | 说明 |
|---|---|---|
| `exchange` | `str` | 交易所代码 |
| `instrument_id` | `str` | 合约代码 |
| `position` | `int` | 总持仓量 |
| `position_close` | `int` | 总持仓可平仓数量（包括平仓冻结持仓） |
| `frozen_position` | `int` | 总开仓冻结持仓 |
| `frozen_closing` | `int` | 总平仓冻结持仓 |
| `td_frozen_closing` | `int` | 今持仓平仓冻结持仓 |
| `td_close_available` | `int` | 今持仓可平仓数量 |
| `td_position_close` | `int` | 今持仓可平仓数量（包括平仓冻结持仓） |
| `yd_frozen_closing` | `int` | 昨持仓平仓冻结持仓 |
| `yd_close_available` | `int` | 昨持仓可平仓数量 |
| `yd_position_close` | `int` | 昨持仓可平仓数量（包括平仓冻结持仓） |
| `open_volume` | `int` | 今日开仓数量（不包括冻结） |
| `close_volume` | `int` | 今日平仓数量（包括昨持仓的平仓, 不包括冻结） |
| `strike_frozen_position` | `int` | 执行冻结持仓 |
| `abandon_frozen_position` | `int` | 放弃执行冻结持仓 |
| `position_cost` | `float | int` | 总持仓成本 |
| `yd_position_cost` | `float | int` | 初始昨日持仓成本（当日不变） |
| `close_profit` | `float | int` | 平仓盈亏 |
| `position_profit` | `float | int` | 持仓盈亏 |
| `open_avg_price` | `float | int` | 开仓均价 |
| `position_avg_price` | `float | int` | 持仓均价 |
| `used_margin` | `float | int` | 占用保证金 |
| `close_available` | `int` | 当前总可平持仓数量 |
