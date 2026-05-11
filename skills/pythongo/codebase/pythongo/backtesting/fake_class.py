from datetime import datetime
from typing import TYPE_CHECKING, Any

from ..classdef.common import ObjDataType

if TYPE_CHECKING:
    from .engine import Engine


class FakeBaseEvent(object):
    @staticmethod
    def emit(*args, **kwargs): ...


class FakeQtGuiSupport(object):
    class hide_signal(FakeBaseEvent): ...
    class init_widget_signal(FakeBaseEvent): ...


class FakeWidget(object):
    class load_data_signal(FakeBaseEvent): ...
    class set_xrange_event_signal(FakeBaseEvent): ...

    def recv_kline(self, *args, **kwargs) -> None: ...


class INFINIGO(object):
    engine: "Engine" = None

    @staticmethod
    def updateParam(StrategyID: int, Data: dict[str, str]) -> None:
        return

    @staticmethod
    def updateState(StrategyID: int, Data: dict[str, str]) -> None:
        return

    @staticmethod
    def pauseStrategy(StrategyID: int) -> None:
        return

    @staticmethod
    def writeLog(msg: Any) -> None:
        print(msg)

    @staticmethod
    def subMarketData(StrategyObj: object, ExchangeID: str, InstrumentID: str) -> None:
        INFINIGO.engine.subscribe(exchange=ExchangeID, instrument_id=InstrumentID)

    @staticmethod
    def unsubMarketData(StrategyObj: object, ExchangeID: str, InstrumentID: str) -> None:
        INFINIGO.engine.unsubscribe(exchange=ExchangeID, instrument_id=InstrumentID)

    @staticmethod
    def sendOrder(**kwargs) -> int | None:
        return INFINIGO.engine.make_order(**kwargs)

    @staticmethod
    def cancelOrder(OrderID) -> int:
        return

    @staticmethod
    def _handle_instrument_data(data: dict) -> dict:
        shutdown_date: str = data.get("shutdown_date")

        return {
            "ProductID": data.get("product_code"),
            "Exchange": data.get("exchange_code"),
            "InstrumentID": data.get("instrument_code"),
            "InstrumentName": data.get("instrument_name"),
            "PriceTick": data.get("tick_price"),
            "ProductClass": data.get("instrument_type"),
            "VolumeMultiple": data.get("volume_multiple"),
            "StrikePrice": data.get("strike_price") or 0.0,
            "UnderlyingInstrID": data.get("underlying_code"),
            "OptionsType": data.get("options_type") or "0",
            "UpperLimitPrice": data.get("upper_limit_price"),
            "LowerLimitPrice": data.get("lower_limit_price"),
            "ExpireDate": shutdown_date and datetime.strptime(shutdown_date, '%Y-%m-%d').strftime('%Y%m%d'),
            "MinLimitOrderVolume": data.get("min_limit_order_volume"),
            "MaxLimitOrderVolume": data.get("max_limit_order_volume")
        }

    @staticmethod
    def getInstrument(Exchange: str, InstrumentID: str) -> ObjDataType:
        result = INFINIGO.engine.market_center.get_instrument_data(Exchange, InstrumentID)
        if result["hint"] != "OK":
            return {}

        data: dict = result["data"][0]

        return INFINIGO._handle_instrument_data(data)

    @staticmethod
    def getInstListByExchAndProduct(Exchange: str, ProductID: str) -> list[ObjDataType]:
        result = INFINIGO.engine.market_center.get_product_data(Exchange, ProductID)

        if result["hint"] != "OK":
            return []

        return [INFINIGO._handle_instrument_data(data) for data in result["data"]]

    @staticmethod
    def getInvestorList() -> list[ObjDataType]:
        return [{"BrokerID": "0001", "InvestorID": "0001", "UserID": "0001"}]

    @staticmethod
    def getInvestorAccount(investor: str) -> ObjDataType:
        return {
            "InvestorID": investor,
            "AccountID": investor,
            "Balance": INFINIGO.engine.account.available,
            "PreBalance": INFINIGO.engine.account.initial_capital,
            "Available": INFINIGO.engine.account.available,
            "PreAvailable": INFINIGO.engine.account.available,
            "CloseProfit": INFINIGO.engine.account.closed_profit,
            "PositionProfit": INFINIGO.engine.account.position_profit,
            "DynamicRights": INFINIGO.engine.account.dynamic_rights,
            "Fee": INFINIGO.engine.account.fee,
            "Margin": INFINIGO.engine.account.margin,
            "FrozenMargin": 0.0,
            "Deposit": 0.0,
            "Withdraw": 0.0,
        }

    @staticmethod
    def getInvestorPosition(investor: str, Simple: bool) -> list[ObjDataType]:
        data = []

        for order_details in INFINIGO.engine.order_details:
            if order_details.closed or investor != order_details.investor_id:
                continue

            data.append({
                "BrokerID": "0001",
                "Exchange": order_details.exchange,
                "InvestorID": order_details.investor_id,
                "InstrumentID": order_details.instrument_id,
                "Direction": "多" if order_details.direction == "0" else "空",
                "HedgeFlag": "1",
                "Position": order_details.volume,
                "PositionClose": order_details.volume,
                "FrozenPosition": 0,
                "FrozenClosing": 0,
                "YdFrozenClosing": 0,
                "YdPositionClose": 0,
                "OpenVolume": 0,
                "CloseVolume": 0,
                "StrikeFrozenPosition": 0,
                "AbandonFrozenPosition": 0,
                "PositionCost": 0.0,
                "YdPositionCost": 0.0,
                "CloseProfit": 0.0,
                "PositionProfit": 0.0,
                "OpenAvgPrice": 0.0,
                "PositionAvgPrice": 0.0,
                "CloseAvailable": order_details.volume
            })

        return data
