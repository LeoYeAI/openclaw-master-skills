# pythongo.types

## `TypeDateTime`

时间类型，等同于 `datetime.datetime`

## `TypeProduct`

品种类型

```python
Literal["1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "h"]
```

对应关系请查看 [数值映射 - ProductClassType](/faq/mapping#productclasstype)

## `TypeInstResult`

合约信息数据类型

```python
dict[TypeProduct, list[InstrumentData | str]]
```

## `TypeOrderDIR`

报单方向

```python
Literal["buy", "sell"]
```

对应关系如下

| 键 | 值 |
|---|---|
| "buy" | 买 |
| "sell" | 卖 |

## `TypeHedgeFlag`

投机套保标志

```python
Literal["1", "2", "3", "4", "5"]
```

对应关系请查看 [数值映射 - HedgeFlagType](/faq/mapping#hedgeflagtype)

## `TypeOrderFlag`

报单指令

```python
Literal["GFD", "FAK", "FOK"]
```

指令解释[看这里](https://infinitrader.quantdo.com.cn/docs/explanation.html)

## `TypeOffsetFlag`

开平标志

```python
Literal["0", "1", "3"]
```

对应关系请查看 [数值映射 - OffsetFlagType](/faq/mapping#offsetflagtype)
