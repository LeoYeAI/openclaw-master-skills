# 数值映射

PythonGO 中有很多值是在无限易里定义好的常量，在 PythonGO 中只能看到一些数字或字母，为了防止你一头雾水，这里列举了一些单个数字或字母所代表的的含义，可以帮助你更快的理解 PythonGO

> [!NOTE]
> 你只需要关注值与其对应的含义即可，变量名是体现在无限易中的，仅供你了解。

> [!NOTE]
> 所有的值都是字符串类型

## `ProductClassType`

产品类型

| 变量名 | 值 | 含义 |
|---|---|---|
| Futures | `1` | 期货 |
| Options | `2` | 期权 |
| Combination | `3` | 组合 |
| Spot | `4` | 即期 |
| EFP | `5` | 期转现 |
| Unknown | `6` | 未知类型 |
| Stocks | `7` | 证券 |
| StockOptions | `8` | 股票期权 |
| SGE_SPOT | `9` | 金交所现货 |
| SGE_DEFER | `a` | 金交所递延 |
| SGE_FOWARD | `b` | 金交所远期 |
| FX | `c` | 外汇 |
| TAS | `d` | TAS 合约 |
| MI | `e` | 金属指数 |
| SpotOption | `h` | 现货期权 |

## `OptionsType`

期权类型

| 变量名 | 值 | 含义 |
|---|---|---|
| NotOptions | `0` | 非期权 |
| CallOptions | `1` | 看涨 |
| PutOptions | `2` | 看跌 |

## `HedgeFlagType`

投机套保标志类型

| 变量名 | 值 | 含义 |
|---|---|---|
| Speculation | `1` | 投机 |
| Arbitrage | `2` | 套利 |
| Hedge | `3` | 套保 |
| MarketMaker | `4` | 做市商 |
| CoveredOption | `5` | 备兑 |

## `OrderPriceType`

报单价格条件类型

| 变量名 | 值 | 含义 |
|---|---|---|
| AnyPrice | `1` | 任意价 |
| LimitPrice | `2` | 限价 |
| BestPrice | `3` | 最优价 |
| FiveLevelPrice | `4` | 五档价 |

## `OrderType`

报单类型

| 变量名 | 值 | 含义 |
|---|---|---|
| Gfd | `0` | GFD 下单 |
| Fak | `1` | FAK 下单 |
| Fok | `2` | FOK 下单 |

## `DirectionType`

买卖方向类型

| 变量名 | 值 | 含义 |
|---|---|---|
| Buy | `0` | 多 |
| Sell | `1` | 空 |

## `OffsetFlagType`

开平标志类型

| 变量名 | 值 | 含义 |
|---|---|---|
| Open | `0` | 开仓 |
| Close | `1` | 平仓 |
| ForceClose | `2` | 强平 |
| CloseToday | `3` | 平今 |
| CloseYesterday | `4` | 平昨 |

## `InstrumentStatus`

合约状态（纯文字）

| 值 |
|---|
| 开盘前 |
| 非交易 |
| 连续交易 |
| 集合竞价报单 |
| 集合竞价价格平衡 |
| 集合竞价撮合 |
| 收盘 |
| 开盘集合竞价 |
| 收盘集合竞价 |
| 停牌 |
| 临时停牌 |
| 盘后交易 |
| 波动性中断 |
| 休市 |
| 未上市 |
| 金交所交割申报 |
| 金交所交割申报结束 |
| 金交所中立仓申报 |
| 金交所交割申报撮合 |

## `OrderStatus`

报单状态（纯文字）

| 值 |
|---|
| 未知 |
| 未成交 |
| 全部成交 |
| 部分成交 |
| 部成部撤 |
| 已撤销 |
| 已报入未应答 |
| 部分撤单还在队列 |
| 部成部撤还在队列中 |
| 待报入 |
| 投顾报单 |
| 投资经理驳回 |
| 投资经理通过 |
| 交易员己报入 |
| 交易员驳回 |
| 投顾经理保 |
