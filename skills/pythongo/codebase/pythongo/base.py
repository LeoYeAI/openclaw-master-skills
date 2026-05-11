import datetime
import json
import os
import sys
from threading import Timer
from typing import Any

from pydantic import BaseModel, Field

from pythongo import infini, utils
from pythongo.classdef import (AccountData, CancelOrderData, InstrumentData,
                               InstrumentStatus, InvestorData, OrderData,
                               Position, TickData, TradeData)
from pythongo.const import ORDER_TYPE_MAP, OrderDirectionEnum, OrderOffsetEnum
from pythongo.types import (TypeHedgeFlag, TypeInstResult, TypeOffsetFlag,
                            TypeOrderDIR, TypeOrderFlag)


class BaseParams(BaseModel, validate_assignment=True):
    """参数映射模型"""
    exchange: str = Field(default="", title="交易所代码")
    instrument_id: str = Field(default="", title="合约代码")


class BaseState(BaseModel, validate_assignment=True):
    """状态映射模型"""
    ...


class BaseStrategy(object):
    """策略模板"""

    def __init__(self) -> None:
        self.strategy_id = 0
        """策略实例 ID"""

        self.strategy_name: str = ""
        """策略实例名称"""

        self.params_map = BaseParams()
        """参数表"""

        self.state_map = BaseState()
        """状态表"""

        self.limit_time = 2
        """错单限制时间（单位：秒）"""

        self.trading: bool = False
        """是否允许交易"""

    @property
    def class_name(self) -> str:
        """策略的类名"""
        return self.__class__.__name__

    @property
    def _strategy_file_extension(self) -> str | None:
        """策略文件扩展名"""
        module_name = self.__class__.__module__
        module = sys.modules.get(module_name)

        if module and getattr(module, '__file__', None):
            file_path: str = module.__file__
            _, extension = os.path.splitext(file_path)
            return extension

        return None

    @property
    def exchange_list(self) -> list[str]:
        """交易所列表"""
        return self.params_map.exchange.split(";")

    @property
    def instrument_list(self) -> list[str]:
        """合约列表"""
        return self.params_map.instrument_id.split(";")

    @property
    def instance_file(self) -> str:
        """实例参数保存文件"""
        base_dir = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(base_dir, "instance_files", f"{self.strategy_name}.json")

    def __package_params(self, key: str, value: Any) -> dict[str, str]:
        """
        包装客户端所需的参数数据

        Args:
            key: 参数英文名
            value: 参数值
        """

        return {
            "name": key,
            "value": str(value),
            "cn_name": self.params_map.model_fields[key].title
        }

    def get_params(self) -> list[dict[str, str]]:
        """
        获取策略参数

        Note:
            无限易调用此方法来获取定义好的属性和对应的值
        """

        return [self.__package_params(key, value) for key, value in self.params_map]

    def set_params(self, data: dict[str, str]) -> None:
        """
        设置策略参数

        Args:
            data: 修改后的界面参数数据
        Note:
            修改界面参数时无限易主动调用
        """

        new_data: list[dict[str, str]] = []

        for key, value in data.items():
            new_data.append(self.__package_params(key, value))
            setattr(self.params_map, key, value)

        infini.update_param(strategy_id=self.strategy_id, data=new_data)

        self.update_status_bar()

    def update_status_bar(self) -> None:
        """更新无限易 PythonGO 窗口状态栏显示值"""
        infini.update_state(
            strategy_id=self.strategy_id,
            data={
                self.state_map.model_fields[key].title: str(value)
                for key, value in self.state_map
            }
        )

    def save_instance_file(self) -> None:
        """保存实例信息"""
        instance_info = {
            **self.params_map.model_dump(),
            "class_name": self.class_name,
            "strategy_name": self.strategy_name,
            "_extension": self._strategy_file_extension
        }

        with open(self.instance_file, "w", encoding="UTF-8") as f:
            json.dump(obj=instance_info, fp=f, ensure_ascii=False)
            f.close()

        self.output("保存实例信息完毕")

    def load_instance_file(self) -> None:
        """加载实例文件并对策略设置对应属性"""
        if os.path.exists(self.instance_file):
            with open(self.instance_file, "r", encoding="UTF-8") as f:
                try:
                    setting: dict[str, Any] = json.load(f)

                    for key, value in setting.items():
                        if hasattr(self.params_map, key):
                            setattr(self.params_map, key, value)

                    self.output("使用保存数据初始化")
                except Exception as e:
                    self.output(f"加载实例文件失败: {e}")
                finally:
                    f.close()

    def on_init(self) -> None:
        """
        创建实例回调

        Note:
            界面创建实例或加载实例会触发此方法
        """

        self.load_instance_file()
        self.update_status_bar()
        self.output("策略初始化完毕")

    def on_start(self) -> None:
        """
        启动策略回调

        Note:
            界面点击运行按钮会触发此方法
        """
        self.trading = True

        self.sub_market_data()
        self.update_status_bar()
        self.output("策略启动")

    def on_stop(self) -> None:
        """
        停止策略回调

        Note:
            界面点击暂停按钮会触发此方法
        """

        self.trading = False

        utils.Scheduler("PythonGO").stop()
        self.save_instance_file()
        self.unsub_market_data()
        self.update_status_bar()
        self.output("策略停止")

    def on_tick(self, tick: TickData) -> None:
        """
        收到行情 tick 推送回调

        Args:
            tick: 行情切片数据对象
        """
        ...

    def on_contract_status(self, status: InstrumentStatus) -> None:
        """
        合约状态变化回调

        Args:
            status: 合约状态对象
        """
        ...

    def on_order_cancel(self, order: OrderData) -> None:
        """
        收到撤单推送回调

        Args:
            order: 报单数据对象
        """
        ...

    def on_order_trade(self, order: OrderData) -> None:
        """
        收到报单成交推送回调

        Args:
            order: 报单数据对象
        """
        ...

    def on_order(self, order: OrderData) -> None:
        """
        报单变化回调

        Args:
            order: 报单数据对象

        Note:
            发单成功也算报单变化
        """

        if order.status == "已撤销":
            self.on_order_cancel(order)
        elif order.status in ["全部成交", "部成部撤"]:
            self.on_order_trade(order)

    def on_cancel(self, order: CancelOrderData) -> None:
        """
        撤单推送回调

        Args:
            order: 撤单数据对象
        """

    def on_trade(self, trade: TradeData, log: bool = False) -> None:
        """
        报单成交推送回调

        Args:
            trade: 成交数据对象
            log: 是否输出成交日志
        """

        if log:
            self.output(
                f"[成交回调] "
                f"合约: {trade.instrument_id}, "
                f"方向: {trade.direction} {trade.offset}, "
                f"价格: {trade.price}, "
                f"手数: {trade.volume}, "
                f"时间: {trade.trade_time}"
            )

    def on_error(self, error: dict[str, str]) -> None:
        """
        收到报单错误推送回调

        Args:
            error: 错误信息字典
                包含 errCode (错误代码) 和 errMsg (错误信息)
        """

        self.trading = False

        def limit_contorl():
            self.trading = True
            self.output("错单流控已关闭")

        if error["errCode"] == "0004":
            self.output(f"错单流控开启，{self.limit_time} 秒后关闭，错单原因：{error["errMsg"]}")
            Timer(self.limit_time, limit_contorl).start()
        else:
            self.output(error)

    def pause_strategy(self) -> None:
        """暂停策略, 效果和客户端点击暂停一样"""
        infini.pause_strategy(self.strategy_id)

    def output(self, *msg: Any) -> None:
        """
        输出信息到控制台

        Args:
            msg: 需要输出的信息, 可以传入任意类型多个参数
        """

        log_time = datetime.datetime.now().replace(microsecond=0)

        infini.write_log(f"[{log_time}] [{self.strategy_name}] {" ".join(map(str, msg))}")

    def sub_market_data(self, exchange: str = None, instrument_id: str = None) -> None:
        """
        订阅合约行情
        
        Args:
            exchange: 交易所代码
            instrument_id: 合约代码
        Note:
            如果不传参, 则会默认订阅所有合约
            若合约为单个时, 会默认订阅该合约
            若合约为多个且用 `;` 号分割, 则自动分割后订阅所有合约
        """

        if exchange and instrument_id:
            infini.sub_market_data(
                strategy_obj=self,
                exchange=exchange,
                instrument_id=instrument_id
            )
            return

        for exchange, instrument_id in zip(self.exchange_list, self.instrument_list):
            infini.sub_market_data(
                strategy_obj=self,
                exchange=exchange,
                instrument_id=instrument_id
            )

    def unsub_market_data(self, exchange: str = None, instrument_id: str = None) -> None:
        """
        取消订阅合约行情

        Args:
            exchange: 交易所代码
            instrument_id: 合约代码
        Note:
            如果不传参, 则会默认取消订阅所有合约
            若合约为单个时, 会默认取消订阅该合约
            若合约为多个且用 `;` 号分割, 则自动分割后取消订阅所有合约
        """

        if exchange and instrument_id:
            infini.unsub_market_data(
                strategy_obj=self,
                exchange=exchange,
                instrument_id=instrument_id
            )
            return

        for exchange, instrument_id in zip(self.exchange_list, self.instrument_list):
            infini.unsub_market_data(
                strategy_obj=self,
                exchange=exchange,
                instrument_id=instrument_id
            )

    def sync_position(self, simple: bool = False) -> None:
        """
        同步持仓
        
        Args:
            simple: 简化持仓数据（但持仓是实时的）
        """

        self._position: dict[str, dict[str, dict[str, Position]]] = {}

        for investor in infini.get_investor_list():
            investor_id: str = investor["InvestorID"]
            investor_position = infini.get_investor_position(investor_id, simple)

            group_position: dict[str, dict[str, list[Position]]] = {}

            for _position in investor_position:
                (
                    group_position
                    .setdefault(_position["InstrumentID"], {})
                    .setdefault(_position["HedgeFlag"], [])
                    .append(_position)
                )

            for instrument_id in group_position:
                for hedge_flag in group_position[instrument_id]:
                    position = Position(group_position[instrument_id][hedge_flag])

                    (
                        self._position
                        .setdefault(investor_id, {})
                        .setdefault(instrument_id, {})
                        .setdefault(hedge_flag, position)
                    )

    def get_position(
        self,
        instrument_id: str,
        hedgeflag: TypeHedgeFlag = "1",
        investor: str = None,
        simple: bool = False
    ) -> Position:
        """
        获取持仓
        
        Args:
            instrument_id: 合约代码
            hedgeflag: 投机套保标志
                1 投机（默认）, 2 套利, 3 套保, 4 做市商, 5 备兑
            investor: 资金账号
            simple: 简化持仓数据（但持仓是实时的）
        """

        self.sync_position(simple)

        if not investor:
            investor = self.get_investor_data().investor_id

        investor_position = self._position.get(investor, {})
        
        if "&" in instrument_id:
            leg1, leg2 = utils.split_arbitrage_code(instrument_id)

            if leg1 is None or leg2 is None:
                raise Exception(f"错误的套利合约代码: {instrument_id}")
            
            leg1_position = investor_position.get(leg1, {}).get(hedgeflag, Position())
            leg2_position = investor_position.get(leg2, {}).get(hedgeflag, Position())

            is_std_stg = instrument_id.startswith("STD ") or instrument_id.startswith("STG ")

        return investor_position.get(instrument_id, {}).get(hedgeflag, Position())

    def get_all_position(
        self,
        simple: bool = False
    ) -> dict[str, dict[str, dict[str, Position]]]:
        """
        获取所有帐号的所有持仓

        Args:
            simple: 简化持仓数据（但持仓是实时的）
        """

        self.sync_position(simple)

        return self._position

    def send_order(
        self,
        exchange: str,
        instrument_id: str,
        volume: int,
        price: float | int,
        order_direction: TypeOrderDIR,
        order_type: TypeOrderFlag = "GFD",
        investor: str = "",
        hedgeflag: TypeHedgeFlag = "1",
        market: bool = False,
        memo: Any = None
    ) -> int | None:
        """
        报单函数

        Args:
            exchange: 交易所代码
            instrument_id: 合约代码
            volume: 报单手数
            price: 报单价格
            order_direction: 报单方向: buy 买, sell 卖
            order_type: 报单指令: GFD, FAK, FOK
            investor: 报单账号
            hedgeflag: 投机套保标志: 1 投机（默认）, 2 套利, 3 套保, 4 做市商, 5 备兑
            market: 是否市价单: False 非市价单, True 市价单
            memo: 报单备注
        """

        order_direction = order_direction.upper()

        if order_direction not in OrderDirectionEnum.__members__:
            self.output(f"[报单函数] 报单方向 {order_direction} 错误")
            return

        return self.make_order_req(
            exchange=exchange,
            instrument_id=instrument_id,
            volume=volume,
            price=price,
            order_direction=order_direction,
            order_type=order_type,
            investor=investor,
            hedgeflag=hedgeflag,
            offset=OrderOffsetEnum.OPEN.value,
            market=market,
            memo=memo
        )

    def cancel_order(self, order_id: int) -> int:
        """
        撤单函数
        
        Args:
            order_id: 报单编号
        """

        if order_id is None:
            return
        
        if self.trading is False:
            return

        return infini.cancel_order(order_id)

    def auto_close_position(
        self,
        exchange: str,
        instrument_id: str,
        volume: int,
        price: float | int,
        order_direction: TypeOrderDIR,
        order_type: TypeOrderFlag = "GFD",
        investor: str = "",
        hedgeflag: TypeHedgeFlag = "1",
        shfe_close_first: bool = False,
        market: bool = False,
        memo: Any = None
    ) -> int | None:
        """
        自动平仓，默认平今优先

        Args:
            exchange: 交易所代码
            instrument_id: 合约代码
            volume: 报单数量
            price: 报单价格
            order_direction: 报单方向: buy 买平, sell 卖平
            order_type: 报单指令: GFD, FAK, FOK
            investor: 报单账号
            hedgeflag: 投机套保标志: 1 投机（默认）, 2 套利, 3 套保, 4 做市商, 5 备兑
            shfe_close_first: 上期平仓优先
            market: 是否市价单: False 非市价单, True 市价单
            memo: 报单备注
        """

        def _send_order(_volume: int, offset: str = None) -> int | None:
            return self.make_order_req(
                exchange=exchange,
                instrument_id=instrument_id,
                volume=_volume,
                price=price,
                order_direction=order_direction,
                offset=offset or OrderOffsetEnum.CLOSE.value,
                order_type=order_type,
                investor=investor,
                hedgeflag=hedgeflag,
                market=market,
                memo=memo
            )

        order_direction = order_direction.upper()

        if order_direction not in OrderDirectionEnum.__members__:
            self.output(f"[自动平仓] 报单方向 {order_direction} 错误")
            return

        position = self.get_position(
            instrument_id=instrument_id,
            hedgeflag=hedgeflag,
            investor=investor,
            simple=True
        ).get_single_position(OrderDirectionEnum[order_direction].match_direction)

        position_t: int = position.td_close_available
        position_y: int = position.yd_close_available

        _order_flag = False

        if exchange in ["SHFE", "INE"]:
            def _shfe_send_order(_position: int, _offset: str = None) -> int | None:
                nonlocal volume

                _volume = _position if volume >= _position else volume
                volume -= _volume

                if (order_id := _send_order(_volume, offset=_offset)) is not None:
                    self.output(f"[自动平仓] {order_direction} {_volume} 手, {order_id=}")

                if volume == 0:
                    #: 仓全部平完
                    return order_id

            if shfe_close_first and position_y > 0:
                #: 上期所或能源中心优先平昨
                if (order_id := _shfe_send_order(position_y)) or volume == 0:
                    return order_id

                position_y = 0
                _order_flag = True

            if position_t > 0:
                #: 上期所或能源中心平今
                offset = OrderOffsetEnum.CLOSE_TODAY.value

                if (order_id := _shfe_send_order(position_t, offset)) or volume == 0:
                    return order_id

                position_t = 0
                _order_flag = True

        close_available = position_t + position_y

        if close_available == 0:
            if _order_flag is False and self.trading:
                self.output("[自动平仓] 可平仓量为 0")
            return

        if close_available < volume:
            if self.trading:
                self.output("[自动平仓] 可平仓量小于报单数，将使用可平仓量报单")

            volume = close_available

        return _send_order(volume)

    def make_order_req(
        self,
        exchange: str,
        instrument_id: str,
        volume: int,
        price: int | float,
        order_direction: TypeOrderDIR,
        offset: TypeOffsetFlag,
        order_type: TypeOrderFlag,
        investor: str,
        hedgeflag: TypeHedgeFlag,
        market: bool = False,
        memo: Any = None
    ) -> int | None:
        """
        发送报单请求

        Args:
            exchange: 交易所代码
            instrument_id: 合约代码
            volume: 报单数量
            price: 报单价格
            order_direction: 报单方向: buy 买, sell 卖
            offset: 开平标志: 0 开, 1 平, 3 平今
            order_type: 报单指令: GFD, FAK, FOK
            investor: 报单账号
            hedgeflag: 投机套保标志: 1 投机（默认）, 2 套利, 3 套保, 4 做市商, 5 备兑
            market: 是否市价单: False 非市价单, True 市价单
            memo: 报单备注
        Returns:
            order_id(int): 编号
        """

        if self.trading is False:
            return

        return infini.send_order(
            strategy_id=self.strategy_id,
            exchange=exchange,
            instrument_id=instrument_id,
            volume=volume,
            price=price,
            direction=OrderDirectionEnum[order_direction.upper()].flag,
            order_type=ORDER_TYPE_MAP.get(order_type, "GFD"),
            investor=investor,
            hedgeflag=hedgeflag,
            offset=offset,
            market=market,
            memo=memo
        )

    def get_account_fund_data(self, investor: str) -> AccountData:
        """
        获取账号资金数据

        Args:
            investor: 投资者账号
        """

        return AccountData(infini.get_investor_account(investor))

    def get_instrument_data(self, exchange: str, instrument_id: str) -> InstrumentData:
        """
        获取合约信息

        Args:
            exchange: 交易所代码
            instrument_id: 合约代码
        """

        return InstrumentData(infini.get_instrument(exchange, instrument_id))

    def get_instruments_by_product(
        self,
        exchange: str,
        product_id: str,
        raw_data: bool = True
    ) -> TypeInstResult:
        """
        查询指定品种的所有合约信息或者仅合约代码

        Args:
            exchange: 交易所代码
            product_id: 品种代码
            raw_data: 是否返回原始数据
                如果传入 False 则列表中只返回合约代码
        """

        instruments: list[dict] = infini.get_instruments_by_product(
            exchange=exchange,
            product_id=product_id
        )

        result: TypeInstResult = {}

        for instrument in instruments:
            instrument_data = InstrumentData(instrument)

            result.setdefault(instrument["ProductClass"], []).append(
                instrument_data if raw_data else instrument_data.instrument_id
            )

        return result

    def get_investor_data(self, index: int = 1) -> InvestorData:
        """
        获取投资者信息

        Args:
            index: 数组下标, 从 1 开始
        """

        investor_list = infini.get_investor_list()

        index = 0 if index > len(investor_list) else index - 1

        return InvestorData(investor_list[index])
