from typing import Any, Literal

try:
    import INFINIGO # type: ignore
except ImportError:
    from pythongo.backtesting.fake_class import INFINIGO

from pythongo.classdef.common import ObjDataType
from pythongo.types import TypeHedgeFlag, TypeOffsetFlag, TypeOrderFlag


def update_param(strategy_id: int, data: dict[str, str]) -> None:
    """
    界面传入参数在实例中更新

    Args:
        strategy_id: 策略实例 ID
        data: 映射的参数字典
    """

    return INFINIGO.updateParam(StrategyID=strategy_id, Data=data)

def update_state(strategy_id: int, data: dict[str, str]) -> None:
    """
    更新无限易 PythonGO 窗口状态栏显示值

    Args:
        strategy_id: 策略实例 ID
        data: 状态栏显示值的映射字典
    """

    return INFINIGO.updateState(StrategyID=strategy_id, Data=data)

def pause_strategy(strategy_id: int) -> None:
    """
    暂停策略

    Args:
        strategy_id: 策略实例 ID
    """

    return INFINIGO.pauseStrategy(StrategyID=strategy_id)

def write_log(msg: Any) -> None:
    """
    输出日志到控制台

    Args:
        msg: 需要输出的日志内容
    """

    return INFINIGO.writeLog(msg=msg)

def sub_market_data(strategy_obj: object, exchange: str, instrument_id: str) -> None:
    """
    订阅合约行情

    Args:
        strategy_obj: 策略实例
        exchange: 交易所代码
        instrument_id: 合约代码
    """

    return INFINIGO.subMarketData(
        StrategyObj=strategy_obj,
        ExchangeID=exchange,
        InstrumentID=instrument_id
    )

def unsub_market_data(strategy_obj: object, exchange: str, instrument_id: str) -> None:
    """
    取消订阅合约行情

    Args:
        strategy_obj: 策略实例
        exchange: 交易所代码
        instrument_id: 合约代码
    """

    return INFINIGO.unsubMarketData(
        StrategyObj=strategy_obj,
        ExchangeID=exchange,
        InstrumentID=instrument_id
    )

def send_order(
    strategy_id: int,
    exchange: str,
    instrument_id: str,
    volume: int,
    price: int | float,
    direction: Literal["0", "1"],
    order_type: TypeOrderFlag,
    investor: str,
    hedgeflag: TypeHedgeFlag,
    offset: TypeOffsetFlag,
    market: bool = False,
    memo: Any = None
) -> int:
    """
    发单

    Args:
        strategy_id: 策略实例 ID
        exchange: 交易所代码
        instrument_id: 合约代码
        volume: 报单数量
        price: 报单价格
        direction: 报单方向
        order_type: 报单指令
        investor: 投资者账号
        hedgeflag: 投机套保方向
        offset: 开平标志
        market: 是否市价单
        memo: 报单备注
    Returns:
        order_id: 报单 ID, -1 报单失败
    """

    return INFINIGO.sendOrder(
        StrategyID=strategy_id,
        Exchange=exchange,
        InstrumentID=instrument_id,
        Volume=volume,
        Price=price,
        Direction=direction,
        OrderType=order_type,
        Investor=investor,
        HedgeFlag=hedgeflag,
        Offset=offset,
        Market=market,
        Memo=memo
    )

def cancel_order(order_id: int) -> int:
    """
    撤单

    Args:
        order_id: 报单编号
    """

    return INFINIGO.cancelOrder(OrderID=order_id)

def get_instrument(exchange: str, instrument_id: str) -> ObjDataType:
    """
    获取合约信息

    Args:
        exchange: 交易所代码
        instrument_id: 合约代码
    """

    return INFINIGO.getInstrument(
        Exchange=exchange,
        InstrumentID=instrument_id
    )

def get_instruments_by_product(exchange: str, product_id: str) -> list[ObjDataType]:
    """
    查询指定品种的所有合约信息

    Args:
        exchange: 交易所代码
        product_id: 品种代码
    """

    return INFINIGO.getInstListByExchAndProduct(
        Exchange=exchange,
        ProductID=product_id
    )

def get_investor_list() -> list[ObjDataType]:
    """获取所有的投资者信息"""
    return INFINIGO.getInvestorList()

def get_investor_account(investor: str) -> ObjDataType:
    """
    获取账号资金数据

    Args:
        investor: 投资者账号
    """

    return INFINIGO.getInvestorAccount(investor)

def get_investor_position(investor: str, simple: bool = False) -> list[ObjDataType]:
    """
    获取账号持仓

    Args:
        investor: 投资者账号
        simple: 简化持仓数据（但持仓是实时的）
    """

    return INFINIGO.getInvestorPosition(investor, Simple=simple)
