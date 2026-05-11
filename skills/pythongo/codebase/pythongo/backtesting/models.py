import math
import os
from collections import defaultdict
from copy import copy
from datetime import datetime
from typing import ClassVar

import pandas as pd
from pydantic import BaseModel, Field, computed_field

from .logger import logger


class Config(BaseModel):
    """回测配置"""
    access_key: str
    """Access Key"""

    access_secret: str
    """Access Secret"""

    fee_rate: float = 0.0023
    """手续费率"""

    fee_extra: float = 0
    """额外手续费"""

    margin_rate: float = 0.13
    """保证金率"""

    show_progress: bool = False
    """是否展示进度条"""

    save_order_details: bool = False
    """是否保存报单明细"""

    @computed_field
    @property
    def cache_dir(self) -> str:
        """数据缓存文件夹"""
        return os.path.join(os.getenv("APPDATA"), "PythonGO")


class Account(BaseModel):
    """回测账户"""
    initial_capital: int | float
    """初始资金"""

    available: float
    """可用资金"""

    dynamic_rights: float = 0.0
    """动态权益"""

    fee: float = 0.0
    """手续费"""

    margin: float = 0.0
    """保证金"""

    closed_profit: float = 0.0
    """平仓盈亏"""

    position_profit: float = 0.0
    """持仓盈亏"""

    daily_profit: dict[str, float] = {}
    """合约日收益"""

    @computed_field
    @property
    def rate(self) -> float:
        """总收益率"""
        return (self.dynamic_rights - self.initial_capital) / self.initial_capital

    @computed_field
    @property
    def total_profit(self) -> float:
        """总盈亏"""
        return self.dynamic_rights - self.initial_capital


class OrderReq(object):
    """回测报单请求"""
    def __init__(self, data: dict[str, int | float | str]) -> None:
        self.strategy_id: int = data.get("StrategyID", "")
        """策略 ID"""

        self.exchange: str = data.get("Exchange", "")
        """交易所代码"""

        self.instrument_id: str = data.get("InstrumentID", "")
        """合约代码"""

        self.volume: int = data.get("Volume", 0)
        """报单数量"""

        self.price: float = data.get("Price", 0.0)
        """报单价格"""

        self.direction: str = data.get("Direction", "")
        """报单方向"""

        self.order_type: str = data.get("OrderType", "")
        """报单指令"""

        self.investor: str = data.get("Investor", "")
        """投资者帐号"""

        self.hedgeflag: str = data.get("HedgeFlag", "")
        """投机套保标志"""

        self.offset: str = data.get("Offset", "")
        """开平标志"""

        self.market: bool = data.get("Market", False)
        """是否市价单"""

        self.memo: str = data.get("Memo", "")
        """报单备注"""


class Order(BaseModel):
    """单条报单"""
    price: float
    """报单价格"""

    volume: int
    """报单数量"""

    fee: float
    """手续费"""

    margin: float
    """保证金"""

    closed: bool = False
    """是否已平仓"""


class OrderDetail(BaseModel):
    """回测报单明细"""
    investor_id: str
    """投资者帐号"""

    exchange: str
    """交易所代码"""

    instrument_id: str
    """合约代码"""

    direction: str
    """买卖"""
    
    offset: str
    """开平"""

    hedgeflag: str
    """投机套保标志"""

    price: float
    """报单价格"""

    volume: int
    """报单数量"""

    # status: str = "已成交"
    # """报单状态"""

    trade_volume: int
    """成交数量"""

    cancel_volume: int = 0
    """撤单数量"""

    @computed_field
    def remaining_volume(self) -> int:
        """剩余数量"""
        return self.volume - self.trade_volume

    close_available: int
    """可平量"""

    fee: float
    """手续费"""

    margin: float
    """保证金"""

    closed_profit: float = 0.0
    """平仓盈亏"""

    position_profit: float = 0.0
    """持仓盈亏"""

    order_time: datetime = Field(default_factory=lambda: datetime.now())
    """报单时间"""

    trade_time: datetime
    """成交时间"""
    
    trading_day: str
    """成交交易日"""

    closed: bool = False
    """是否已平仓"""

    memo: str = ""
    """备注"""

    order_sys_id: str
    """系统产生报单 ID"""

    orders: list[Order]
    """单条报单明细"""

class InstrumentData(object):
    """回测合约数据"""
    def __init__(self, data: dict[str, int | float | str | None]) -> None:
        self.exchange = data.get("exchange_code", "")
        """交易所代码"""

        self.product_id = data.get("product_code", "")
        """品种代码"""

        self.instrument_id = data.get("instrument_code", "")
        """合约代码"""

        self.instrument_name = data.get("instrument_name", "")
        """合约中文名"""

        self.instrument_type = data.get("instrument_type", "")
        """合约类型"""

        self.open_date = data.get("setup_date", "")
        """上市日期"""

        self.expire_date = data.get("shutdown_date", "")
        """到期日"""

        self.price_tick = data.get("tick_price", 0.0)
        """最小变动价位"""

        self.volume_multiple: int = data.get("volume_multiple", 0)
        """合约乘数"""

        self.upper_limit_price = data.get("upper_limit_price", 0.0)
        """涨停价"""

        self.lower_limit_price = data.get("lower_limit_price", 0.0)
        """跌停价"""

        self.underlying_symbol = data.get("underlying_code", "")
        """标的代码"""

        self.max_market_order_size = data.get("max_market_order_volume", 0)
        """市价单最大下单量"""

        self.min_market_order_size = data.get("min_market_order_volume", 0)
        """市价单最小下单量"""

        self.max_limit_order_size = data.get("max_limit_order_volume", 0)
        """限价单最大下单量"""

        self.min_limit_order_size = data.get("min_limit_order_volume", 0)
        """限价单最小下单量"""

        self.options_type = {"1": "CALL", "2": "PUT"}.get(data.get("options_type", ""), None)
        """期权类型"""

        self.strike_price = data.get("strike_price", 0.0)
        """行权价"""

        self.deliver_year = data.get("delivery_year", "")
        """交割年"""

        self.deliver_month = data.get("delivery_month", "")
        """交割月"""

        self.start_delivery_date = data.get("start_delivery_date", "")
        """开始交割日期"""

        self.end_delivery_date = data.get("end_delivery_date", "")
        """最后交割日期"""

        self.settle_price = data.get("settlement_price", 0.0)
        """结算价"""


class Tick(BaseModel):
    """
    回测 Tick 数据

    Note:
        2024-05-27 之前的数据不带时间戳
    """

    exchange: str = Field("", alias="Exchange")
    instrument_id: str = Field("", alias="InstrumentID")
    last_price: float = Field(0.0, alias="LastPrice")
    open_price: float = Field(0.0, alias="OpenPrice")
    high_price: float = Field(0.0, alias="HighestPrice")
    low_price: float = Field(0.0, alias="LowestPrice")
    volume: int = Field(0, alias="Volume")
    pre_close_price: float = Field(0.0, alias="PreClosePrice")
    pre_settlement_price: float = Field(0.0, alias="PreSettlementPrice")
    open_interest: int = Field(0, alias="OpenInterest")
    upper_limit_price: float = Field(0.0, alias="UpperLimitPrice")
    lower_limit_price: float = Field(0.0, alias="LowerLimitPrice")
    turnover: float = Field(0.0, alias="Turnover")
    bid_price1: float = Field(0.0, alias="BidPrice1")
    bid_price2: float = Field(0.0, alias="BidPrice2")
    bid_price3: float = Field(0.0, alias="BidPrice3")
    bid_price4: float = Field(0.0, alias="BidPrice4")
    bid_price5: float = Field(0.0, alias="BidPrice5")
    ask_price1: float = Field(0.0, alias="AskPrice1")
    ask_price2: float = Field(0.0, alias="AskPrice2")
    ask_price3: float = Field(0.0, alias="AskPrice3")
    ask_price4: float = Field(0.0, alias="AskPrice4")
    ask_price5: float = Field(0.0, alias="AskPrice5")
    bid_volume1: int = Field(0, alias="BidVolume1")
    bid_volume2: int = Field(0, alias="BidVolume2")
    bid_volume3: int = Field(0, alias="BidVolume3")
    bid_volume4: int = Field(0, alias="BidVolume4")
    bid_volume5: int = Field(0, alias="BidVolume5")
    ask_volume1: int = Field(0, alias="AskVolume1")
    ask_volume2: int = Field(0, alias="AskVolume2")
    ask_volume3: int = Field(0, alias="AskVolume3")
    ask_volume4: int = Field(0, alias="AskVolume4")
    ask_volume5: int = Field(0, alias="AskVolume5")
    trading_day: str = Field("", alias="TradingDay")
    timestamp: int = Field(0, alias="Timestamp")

    v1_natural_day: str = Field(alias="NaturalDay")
    v1_update_time: str = Field("", alias="UpdateTime")
    v1_update_millisec: str = Field("", alias="UpdateMillisec")

    _last_total_volume: ClassVar[dict[str, int]] = {}
    last_volume: int = 0
    
    def __init__(self, **data):
        super().__init__(**data)
        
        instrument_id = self.instrument_id
        previous_volume = self._last_total_volume.get(instrument_id, None)
        
        if previous_volume is None:
            self.last_volume = 0
        else:
            self.last_volume = self.volume - previous_volume
            
        self._last_total_volume[instrument_id] = self.volume

    def __str__(self):
        return str(
            {
                "exchange": self.exchange,
                "instrument_id": self.instrument_id,
                "last_price": self.last_price,
                "datetime": self.datetime
            }
        )

    @computed_field
    @property
    def v1_datetime(self) -> datetime:
        time_str = f"{self.v1_natural_day} {self.v1_update_time}.{self.v1_update_millisec or 0}"
        return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")

    @computed_field
    @property
    def datetime(self) -> datetime:
        if self.timestamp:
            return datetime.fromtimestamp(self.timestamp / 1000)
        return self.v1_datetime

    @computed_field
    @property
    def update_time(self) -> str:
        return self.datetime.strftime("%H:%M:%S.%f")

    def copy(self) -> "Tick":
        """浅拷贝自身"""
        return copy(self)


class BacktestingResult(object):
    """
    回测结果
    
    Args:
        account: 回测账户
    """

    def __init__(self, account: Account) -> None:
        self.account: Account = account
        """回测账户"""

        self.turnover: int = 0
        """总成交额"""

        self.total_volume: int = 0
        """总成交笔数"""

        self.trading_days: list[str] = []
        """交易日序列"""

        self.daily_pnl: dict[str, float] = defaultdict(float)
        """每日盈亏"""

        self.trading_days_per_year = 242
        """年交易日"""

        self.df: pd.DataFrame = None

    @property
    def total_trading_days(self) -> int:
        """总交易日"""
        return len(self.trading_days)

    @property
    def pnl_days(self) -> tuple[int, int]:
        """盈亏日分布"""
        profit_days = 0
        loss_days = 0

        for value in self.daily_pnl.values():
            if value < 0:
                loss_days += 1
            else:
                profit_days += 1
        
        return profit_days, loss_days

    def prepare_data(self) -> None:
        """准备计算策略指标所需的数据"""
        self.df = pd.DataFrame(
            data={"PnL": self.daily_pnl.values()},
            index=self.daily_pnl.keys()
        )

    def sharpe_ratio(self, risk_free_rate: float = 0, annualize: bool = True) -> float:
        """
        夏普比率

        Args:
            risk_free_rate: 无风险利率
            annualize: 年化夏普比率
        """

        mean_pnl = self.df["PnL"].mean()

        std_pnl = self.df["PnL"].std()

        sharpe_ratio = (mean_pnl - risk_free_rate) / std_pnl

        if annualize:
            return sharpe_ratio * math.sqrt(self.trading_days_per_year)

        return sharpe_ratio

    def annual_return(self, start_value: float, end_value: float) -> float:
        """
        年化收益率

        Args:
            start_value: 初始金额
            end_value: 结束金额
        Note:
            交易日的年化收益率
        """

        return (
            ((end_value - start_value) / start_value)
            * (self.trading_days_per_year / self.total_trading_days)
        )

    def max_drawdown(self, initial_capital: float) -> float:
        """
        最大回撤

        Args:
            initial_capital: 初始资金
        Note:
            百分比
        """

        self.df["PortfolioValue"] = initial_capital + self.df["PnL"].cumsum()

        self.df["Peak"] = self.df["PortfolioValue"].cummax()

        self.df["Drawdown"] = (self.df["Peak"] - self.df["PortfolioValue"]) / self.df["Peak"]

        return self.df["Drawdown"].max()

    def print(self) -> None:
        """打印策略指标"""
        self.prepare_data()

        logger.info(f"初始资金: {self.account.initial_capital}")
        logger.info(f"结束资金: {self.account.dynamic_rights:.2f}")
        logger.info(f"总盈亏: {self.account.total_profit:.2f}")
        logger.info(f"总收益率: {self.account.rate:.2%}")
        logger.info(f"总手续费: {self.account.fee:.2f}")
        logger.info(f"总成交额: {self.turnover}")
        logger.info(f"总成交笔数: {self.total_volume}")
        logger.info(f"总交易日: {len(self.trading_days)}")
        logger.info(f"年化收益率: {self.annual_return(
            start_value=self.account.initial_capital,
            end_value=self.account.dynamic_rights
        ):.2%}")
        logger.info(f"盈亏交易日（盈&亏）: {self.pnl_days}")
        logger.info(f"夏普比率: {self.sharpe_ratio():.2f}")
        logger.info(f"最大回撤: {self.max_drawdown(self.account.initial_capital):.2%}")
