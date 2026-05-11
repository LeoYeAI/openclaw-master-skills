# `InstrumentData`

## `InstrumentData`

合约数据类

| 属性名 | 类型 | 说明 |
|---|---|---|
| `exchange` | `str` | 交易所代码 |
| `instrument_id` | `str` | 合约代码 |
| `instrument_name` | `str` | 合约中文名 |
| `product_id` | `str` | 品种代码 |
| `product_type` | `str` | 品种类型 |
| `price_tick` | `float` | 最小变动价位 |
| `size` | `int` | 合约大小（合约乘数） |
| `strike_price` | `float` | 期权行权价 |
| `underlying_symbol` | `str` | 标的物代码 |
| `options_type` | `str` | 期权类型 |
| `expire_date` | `str` | 合约到期日 |
| `min_limit_order_size` | `int` | 最小下单量 |
| `max_limit_order_size` | `int` | 最大下单量 |
| `lower_limit_price` | `float` | 跌停板价位 |
| `upper_limit_price` | `float` | 涨停板价位 |

品种类型具体信息请查看 [数值映射 - ProductClassType](/faq/mapping#productclasstype)

期权类型具体信息请查看 [数值映射 - OptionsType](/faq/mapping#optionstype)

实际情况下，经过内部数据转换后，期权类型为：

```python
Literal["", "CALL", "PUT"]
```

## `InstrumentStatus`

合约状态类

| 属性名 | 类型 | 说明 |
|---|---|---|
| `exchange` | `str` | 交易所代码 |
| `instrument_id` | `str` | 合约代码 |
| `status` | `str` | 中文状态 |

中文状态具体信息请查看 [数值映射 - InstrumentStatus](/faq/mapping#instrumentstatus)
