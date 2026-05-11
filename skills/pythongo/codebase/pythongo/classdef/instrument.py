from pythongo.const import OPTION_MAP, PRODUCT_MAP

from .common import ObjDataType


class InstrumentData(object):
    """合约数据类"""

    def __init__(self, data: ObjDataType = {}) -> None:
        self._exchange = data.get("Exchange", "")
        self._instrument_id = data.get("InstrumentID", "")
        self._instrument_name = data.get("InstrumentName", "")
        self._product_id = data.get("ProductID", "")
        self._product_type = data.get("ProductClass", "")
        self._price_tick = data.get("PriceTick", 0.0)
        self._size = data.get("VolumeMultiple", 0)
        self._strike_price = data.get("StrikePrice", 0.0)
        self._underlying_symbol = data.get("UnderlyingInstrID", "")
        self._options_type = data.get("OptionsType", "")
        self._expire_date = data.get("ExpireDate", "")
        self._min_limit_order_size = data.get("MinLimitOrderVolume", 0)
        self._max_limit_order_size = data.get("MaxLimitOrderVolume", 0)
        self._lower_limit_price = data.get("LowerLimitPrice", 0.0)
        self._upper_limit_price = data.get("UpperLimitPrice", 0.0)

    def __repr__(self) -> str:
        return str(
            {
                "exchange": self._exchange,
                "instrument_id": self._instrument_id,
                "instrument_name": self._instrument_name,
                "product_id": self._product_id,
                "product_type": self.product_type,
                "price_tick": self._price_tick,
                "size": self._size,
                "strike_price": self._strike_price,
                "underlying_symbol": self._underlying_symbol,
                "options_type": self.options_type,
                "expire_date": self._expire_date,
                "min_limit_order_size": self._min_limit_order_size,
                "max_limit_order_size": self._max_limit_order_size,
                "lower_limit_price": self._lower_limit_price,
                "upper_limit_price": self._upper_limit_price,
            }
        )

    @property
    def exchange(self) -> str:
        """交易所代码"""
        return self._exchange

    @property
    def instrument_id(self) -> str:
        """合约代码"""
        return self._instrument_id

    @property
    def instrument_name(self) -> str:
        """合约中文名"""
        return self._instrument_name

    @property
    def product_id(self) -> str:
        """品种代码"""
        return self._product_id

    @property
    def product_type(self) -> str:
        """品种类型"""
        return PRODUCT_MAP.get(self._product_type, "")

    @property
    def price_tick(self) -> float:
        """最小变动价位"""
        return self._price_tick

    @property
    def size(self) -> int:
        """合约大小（合约乘数）"""
        return self._size

    @property
    def strike_price(self) -> float:
        """期权行权价"""
        return self._strike_price

    @property
    def underlying_symbol(self) -> str:
        """标的物代码"""
        return self._underlying_symbol

    @property
    def options_type(self) -> str:
        """期权类型"""
        return OPTION_MAP.get(self._options_type, "")

    @property
    def expire_date(self) -> str:
        """合约到期日"""
        return self._expire_date

    @property
    def min_limit_order_size(self) -> int:
        """最小下单量"""
        return self._min_limit_order_size

    @property
    def max_limit_order_size(self) -> int:
        """最大下单量"""
        return self._max_limit_order_size

    @property
    def lower_limit_price(self) -> float:
        """跌停板价位"""
        return self._lower_limit_price

    @property
    def upper_limit_price(self) -> float:
        """涨停板价位"""
        return self._upper_limit_price


class InstrumentStatus(object):
    """合约状态"""
    def __init__(self, data: ObjDataType = {}) -> None:
        self._exchange = data.get("Exchange", "")
        self._instrument_id = data.get("InstrumentID", "")
        self._status = data.get("Status", "")

    def __repr__(self) -> str:
        return str(
            {
                "exchange": self._exchange,
                "instrument_id": self._instrument_id,
                "status": self._status,
            }
        )

    @property
    def exchange(self) -> str:
        """交易所代码"""
        return self._exchange

    @property
    def instrument_id(self) -> str:
        """合约代码"""
        return self._instrument_id

    @property
    def status(self) -> str:
        """中文状态"""
        return self._status
