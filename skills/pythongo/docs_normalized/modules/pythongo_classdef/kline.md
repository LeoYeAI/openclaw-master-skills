# `KLineData`

## `KLineData`

K 线数据类

| 属性名 | 类型 | 说明 |
|---|---|---|
| `exchange` | `str` | 交易所代码 |
| `instrument_id` | `str` | 合约代码 |
| `open` | `float` | 开盘价 |
| `close` | `float` | 收盘价 |
| `low` | `float` | 最低价 |
| `high` | `float` | 最高价 |
| `volume` | `int` | 成交量 |
| `open_interest` | `int` | 持仓量 |
| `datetime` | `TypeDateTime` | 时间 |

*`exchange` 和 `instrument_id` 两个字段是在 v2025.0424 之后的版本新增的*

### `to_json()`

K 线对象转字典

返回：

| 类型 | 描述 |
|---|---|
| `dict` | K 线数据的字典形式 |

### `update()`

更新 K 线属性

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `**kwargs` | 键值对 | K 线的属性与值 | 必填 |
