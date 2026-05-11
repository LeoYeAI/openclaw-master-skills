# core.pyi

这是从 `core.pyi` 转换而来的 reference 文件。
当需要判断 PythonGO 的类定义、方法归属、方法签名、返回值类型、参数名时，优先参考这里的内容。

```python
from datetime import datetime
from enum import Enum
from typing import Literal


class KLineStyle(Enum):
    M1 = 1
    M2 = 2
    M3 = 3
    M4 = 4
    M5 = 5
    M10 = 10
    M15 = 15
    M30 = 30
    M45 = 45
    H1 = 60
    H2 = 120
    H3 = 180
    H4 = 240
    D1 = 1440


type KLineStyleType = Literal[
    KLineStyle.M1,
    KLineStyle.M2,
    KLineStyle.M3,
    KLineStyle.M4,
    KLineStyle.M5,
    KLineStyle.M10,
    KLineStyle.M15,
    KLineStyle.M30,
    KLineStyle.M45,
    KLineStyle.H1,
    KLineStyle.H2,
    KLineStyle.H3,
    KLineStyle.H4,
    KLineStyle.D1,
    "M1", "M2", "M3", "M4", "M5", "M10", "M15", "M30", "M45",
    "H1", "H2", "H3", "H4",
    "D1"
]


class MarketCenter(object):
    def __init__(self) -> None:    
        ...

    def get_avl_close_time(self, instrument_id: str) -> list[datetime]:
        """
        从缓存中获取合约可使用的收盘时间序列

        Args:
            instrument_id: 合约代码
        Note:
            如无缓存, 则获取不到任何数据
        """
        ...

    def get_close_time(self, instrument_id: str) -> list[str]:
        """
        从缓存中获取合约的收盘时间序列

        Args:
            instrument_id: 合约代码
        Note:
            如无缓存, 则获取不到任何数据
        """
        ...

    def get_kline_data(
        self,
        exchange: str,
        instrument_id: str,
        style: KLineStyleType = "M1",
        count: int = -1440,
        origin: int = None,
        start_time: datetime = None,
        end_time: datetime = None,
        simply: bool = True
    ) -> list[dict]:
        """
        获取 K 线数据

        Args:
            exchange: 交易所代码
            instrument_id: 合约代码
            style: K 线风格, `KLineStyle` 枚举值
            count: 查询 K 线数量, 正值获取 `origin` 时间后的数量, 负值为之前
            origin: 基准时间戳（毫秒）
            start_time: K 线起始时间
            end_time: K 线结束时间
            simply: 极简 K 线, 只返回带有 `OHLC` 和时间的 K 线
        Note:
            使用 `start_time` 和 `end_time` 可以获取一个时间区间的 K 线
            但同时这样会忽略 `count` 和 `origin` 参数
        """
        ...

    def get_kline_data_by_day(
        self,
        exchange: str,
        instrument_id: str,
        day_count: int,
        origin: int = None,
        style: KLineStyleType | str = "M1",
        simply: bool = True
    ) -> list[dict]:
        """
        按交易日天数获取 K 线数据

        Args:
            exchange: 交易所代码
            instrument_id: 合约代码
            day_count: 查询 N 天的数据, 正值获取 origin 时间后的数量, 负值为之前
            origin: 基准毫秒时间戳
            style: K 线风格, KLineStyle 枚举值, 仅支持 M1, M5, M15, M30, H1
            simply: 极简 K 线, 只返回带有 OHLC 和时间的 K 线
        """
        ...

    def get_dominant_list(self, exchange: str) -> list[str]:
        """
        获取交易所的主连合约列表

        Args:
            exchange: 交易所代码
        """
        ...

    def get_instrument_trade_time(self, exchange: str, instrument_id: str, instant: int = None) -> dict:
        """
        查询带交易日的合约交易时段

        Args:
            exchange: 交易所代码
            instrument_id: 合约代码
            instant: 基准毫秒时间戳
        """
        ...

    def get_product_trade_time(self, exchange: str, product_id: str, trading_day: str = None) -> dict:
        """
        查询品种的交易时段信息

        Args:
            exchange: 交易所代码
            product_id: 品种代码
            trading_day: 品种交易日，格式为 `%Y%m%d`
        """
        ...

    def get_next_gen_time(self, exchange: str, instrument_id: str, tick_time: datetime, style: KLineStyleType) -> datetime:
        """
        获取下一根 K 线生成时间

        Args:
            exchange: 交易所代码
            instrument_id: 合约代码
            tick_time: tick 时间
            style: K 线周期, KLineStyle 枚举值
        """
        ...

```
