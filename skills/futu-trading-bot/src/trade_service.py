"""
港股下单工具模块

对外只提供一个安全的下单函数 submit_order，内部封装了所有校验逻辑和富途 API 调用。
使用方式：
    from trade_service import submit_order
    result = submit_order(code='HK.00700', side='BUY', qty=200, price=350.0, acc_id=123456, trd_env='SIMULATE')
"""

from typing import Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, model_validator

# 导入富途 SDK
try:
    from futu import (
        OpenSecTradeContext,
        OpenQuoteContext,
        TrdMarket,
        SecurityFirm,
        RET_OK,
        TrdEnv as FutuTrdEnv,
        OrderType as FutuOrderType,
        TimeInForce as FutuTimeInForce,
        TrdSide as FutuTrdSide,
        ModifyOrderOp as FutuModifyOrderOp,
        Session
    )
except Exception as e:
    raise RuntimeError(
        "加载 futu SDK 失败。若你在 OpenClaw/Codex 或其他受限沙箱中运行，请改用 host/elevated 模式。"
        "Futu SDK 在导入阶段可能需要访问本机 OpenD 资源并写入 ~/.com.futunn.FutuOpenD/Log。"
    ) from e

# 导入配置管理模块
from config_manager import get_host, get_port, get_security_firm


# ---------- 枚举定义 ----------
class OrderType(str, Enum):
    """订单类型，与富途API保持一致"""
    UNKNOWN = "UNKNOWN"            # 未知类型
    NORMAL = "NORMAL"              # 限价单
    MARKET = "MARKET"              # 市价单
    ABSOLUTE_LIMIT = "ABSOLUTE_LIMIT"  # 绝对限价订单（仅港股）
    AUCTION = "AUCTION"            # 竞价订单（仅港股）
    AUCTION_LIMIT = "AUCTION_LIMIT"  # 竞价限价订单（仅港股）
    SPECIAL_LIMIT = "SPECIAL_LIMIT"  # 特别限价订单（仅港股）
    SPECIAL_LIMIT_ALL = "SPECIAL_LIMIT_ALL"  # 特别限价且要求全部成交订单（仅港股）
    STOP = "STOP"                  # 止损市价单
    STOP_LIMIT = "STOP_LIMIT"      # 止损限价单
    MARKET_IF_TOUCHED = "MARKET_IF_TOUCHED"  # 触及市价单（止盈）
    LIMIT_IF_TOUCHED = "LIMIT_IF_TOUCHED"  # 触及限价单（止盈）
    TRAILING_STOP = "TRAILING_STOP"  # 跟踪止损市价单
    TRAILING_STOP_LIMIT = "TRAILING_STOP_LIMIT"  # 跟踪止损限价单
    TWAP = "TWAP"                  # 时间加权市价算法单（仅美股）
    TWAP_LIMIT = "TWAP_LIMIT"      # 时间加权限价算法单（港股和美股）
    VWAP = "VWAP"                  # 成交量加权市价算法单（仅美股）
    VWAP_LIMIT = "VWAP_LIMIT"      # 成交量加权限价算法单（港股和美股）


class TrdSide(str, Enum):
    """交易方向"""
    BUY = "BUY"
    SELL = "SELL"


class TrdEnv(str, Enum):
    """交易环境"""
    REAL = "REAL"
    SIMULATE = "SIMULATE"


class TimeInForce(str, Enum):
    """订单有效期"""
    DAY = "DAY"                    # 当日有效
    GTC = "GTC"                    # 撤销前有效
    # 可根据富途文档补充

class ModifyOrderOp(str, Enum):
    """改单操作类型，与富途API保持一致"""
    UNKNOWN = "UNKNOWN"          # 未知
    NORMAL = "NORMAL"            # 修改订单（改价/改量）
    CANCEL = "CANCEL"            # 撤单
    DISABLE = "DISABLE"          # 使失效
    ENABLE = "ENABLE"            # 使生效
    DELETE = "DELETE"            # 删除

# ---------- 订单数据模型 ----------
class Order(BaseModel):
    """
    订单数据模型，与富途 place_order 参数基本一致。
    通过 Pydantic 验证器确保不同订单类型参数的正确性。
    """
    # 必填字段
    code: str                                               # 股票代码，如 "HK.00700"
    trd_side: TrdSide                                       # 交易方向
    qty: int                                                # 股数
    price: Optional[float] = None                           # 价格（限价单必须提供）
    order_type: OrderType = OrderType.NORMAL                # 订单类型，默认为限价单

    # 可选字段（提供默认值，与富途 place_order 参数对应）
    trd_env: TrdEnv                                          # 交易环境（必须显式传入）
    adjust_limit: int = 0                                    # 调整限价类型
    acc_id: int = 0                                          # 账户 ID，0 表示默认账户
    acc_index: int = 0                                       # 账户索引
    remark: Optional[str] = None                             # 备注
    time_in_force: TimeInForce = TimeInForce.DAY             # 订单有效期
    fill_outside_rth: bool = False                           # 是否允许盘后成交
    aux_price: Optional[float] = None                        # 触发价（止损单必须）
    trail_type: Optional[str] = None                         # 跟踪止损类型
    trail_value: Optional[float] = None                      # 跟踪止损值
    trail_spread: Optional[float] = None                     # 跟踪止损价差
    session: str = "NONE"                                    # 交易时段

    @model_validator(mode='after')
    def validate_order_type_requirements(self):
        """根据订单类型校验必要参数（根据用户提供的正确列表修正）"""
        # 需要价格的订单类型（根据用户提供的正确列表）
        price_required_types = [
            OrderType.NORMAL,           # 限价单 ✓
            OrderType.MARKET,           # 市价单 ✓（可以传任意值）
            OrderType.AUCTION,          # 竞价市价单 ✓
            OrderType.AUCTION_LIMIT,    # 竞价限价单 ✓
            OrderType.ABSOLUTE_LIMIT,   # 绝对限价单 ✓
            OrderType.SPECIAL_LIMIT,    # 特别限价单 ✓
            OrderType.SPECIAL_LIMIT_ALL, # 特别限价且要求全部成交订单 ✓
            OrderType.STOP,             # 止损市价单 ✓（可以传任意值）
            OrderType.STOP_LIMIT,       # 止损限价单 ✓
            OrderType.MARKET_IF_TOUCHED, # 触及市价单 ✓（可以传任意值）
            OrderType.LIMIT_IF_TOUCHED, # 触及限价单 ✓
            # 注意：TRAILING_STOP和TRAILING_STOP_LIMIT不需要price
            OrderType.TWAP,             # 时间加权市价算法单（仅美股）
            OrderType.TWAP_LIMIT,       # 时间加权限价算法单（港股和美股）
            OrderType.VWAP,             # 成交量加权市价算法单（仅美股）
            OrderType.VWAP_LIMIT        # 成交量加权限价算法单（港股和美股）
        ]
        
        # 需要触发价格的订单类型（根据用户提供的正确列表）
        aux_price_required_types = [
            OrderType.STOP,             # 止损市价单 ✓
            OrderType.STOP_LIMIT,       # 止损限价单 ✓
            OrderType.MARKET_IF_TOUCHED, # 触及市价单 ✓
            OrderType.LIMIT_IF_TOUCHED, # 触及限价单 ✓
            # 注意：TRAILING_STOP和TRAILING_STOP_LIMIT不需要aux_price
        ]
        
        # 需要跟踪类型的订单类型（根据用户提供的正确列表）
        trail_required_types = [
            OrderType.TRAILING_STOP,    # 跟踪止损市价单 ✓
            OrderType.TRAILING_STOP_LIMIT # 跟踪止损限价单 ✓
        ]
        
        # 检查价格要求
        if self.order_type in price_required_types and self.price is None:
            raise ValueError(f"{self.order_type.value}订单必须提供 price")
        
        # 检查触发价格要求
        if self.order_type in aux_price_required_types and self.aux_price is None:
            raise ValueError(f"{self.order_type.value}订单必须提供 aux_price")
        
        # 检查跟踪类型要求
        if self.order_type in trail_required_types:
            if self.trail_type is None or self.trail_value is None:
                raise ValueError(f"{self.order_type.value}订单必须提供 trail_type 和 trail_value")
            # 只有跟踪止损限价单需要trail_spread
            if self.order_type == OrderType.TRAILING_STOP_LIMIT and self.trail_spread is None:
                raise ValueError(f"{self.order_type.value}订单必须提供 trail_spread")
            
        return self

    @model_validator(mode='after')
    def validate_mutually_exclusive_fields(self):
        """检查互斥字段，根据富途API文档修正"""
        # 检查跟踪止损相关字段
        if self.order_type in [OrderType.TRAILING_STOP, OrderType.TRAILING_STOP_LIMIT]:
            # 跟踪止损订单必须提供 trail_type 和 trail_value
            if self.trail_type is None or self.trail_value is None:
                raise ValueError(f"{self.order_type.value}订单必须提供 trail_type 和 trail_value")
            
            # 只有跟踪止损限价单需要 trail_spread
            if self.order_type == OrderType.TRAILING_STOP_LIMIT and self.trail_spread is None:
                raise ValueError(f"{self.order_type.value}订单必须提供 trail_spread")
            
            # 跟踪止损市价单不应该有 trail_spread
            if self.order_type == OrderType.TRAILING_STOP and self.trail_spread is not None:
                raise ValueError(f"{self.order_type.value}订单不应提供 trail_spread")
        else:
            # 非跟踪止损订单不应该提供任何 trail 相关字段
            if self.trail_type is not None or self.trail_value is not None or self.trail_spread is not None:
                raise ValueError("非跟踪止损订单不应提供 trail_type、trail_value 或 trail_spread")
        
        return self


# ---------- 核心交易服务类（内部使用，不对外暴露）----------
class _HKTradeService:
    """
    内部交易服务类，封装富途上下文与校验逻辑。
    不对外暴露，防止绕过校验。
    """

    def __init__(self):
        """
        初始化交易服务
        """
        self._lot_size_cache: Dict[str, int] = {}     # 股票每手股数缓存
        
        # 延迟初始化上下文，避免在__init__中立即创建连接
        self._ctx = None
        self._quote_ctx = None

    def _ensure_contexts_initialized(self):
        """确保上下文已初始化（延迟初始化）"""
        print(f"[DEBUG] _ensure_contexts_initialized start: trade_ctx_ready={self._ctx is not None}, quote_ctx_ready={self._quote_ctx is not None}")
        if self._ctx is None or self._quote_ctx is None:
            # 从配置文件获取连接参数
            host = get_host()
            port = get_port()
            security_firm = get_security_firm()
            print(f"[DEBUG] Creating trade/quote contexts with host={host}, port={port}, security_firm={security_firm}")
            
            # 创建真实的富途交易上下文
            self._ctx = OpenSecTradeContext(
                filter_trdmarket=TrdMarket.HK,
                host=host,
                port=port,
                security_firm=security_firm
            )
            
            # 创建行情上下文，用于获取股票基本信息（如每手股数）
            self._quote_ctx = OpenQuoteContext(host=host, port=port)
            
            print(f"[初始化] 交易上下文和行情上下文已创建")
        print(f"[DEBUG] _ensure_contexts_initialized end: trade_ctx_ready={self._ctx is not None}, quote_ctx_ready={self._quote_ctx is not None}")

    def close(self):
        """关闭所有上下文连接"""
        try:
            if self._ctx is not None:
                self._ctx.close()
                self._ctx = None
                print(f"[清理] 交易上下文已关闭")
        except Exception as e:
            print(f"[警告] 关闭交易上下文时出错: {str(e)}")
        
        try:
            if self._quote_ctx is not None:
                self._quote_ctx.close()
                self._quote_ctx = None
                print(f"[清理] 行情上下文已关闭")
        except Exception as e:
            print(f"[警告] 关闭行情上下文时出错: {str(e)}")
    
    def __del__(self):
        """析构函数，确保连接被关闭"""
        self.close()
    
    def _reconnect_if_needed(self):
        """如果需要，重新连接"""
        if self._ctx is None or self._quote_ctx is None:
            self._ensure_contexts_initialized()

    def place_order(self, order: Order) -> Dict[str, Any]:
        """
        统一下单入口，包含完整的校验逻辑
        每次增加校验逻辑后都会调用真实API进行验证
        :return: 统一格式的结果字典
        """
        print(
            f"[DEBUG] place_order start: code={order.code}, side={order.trd_side.value}, qty={order.qty}, "
            f"price={order.price}, trd_env={order.trd_env.value}, order_type={order.order_type.value}, acc_id={order.acc_id}"
        )
        # 1. 基础参数校验（使用Pydantic模型已自动完成）
        # Order模型已经通过Pydantic验证器完成了基础校验
        
        # 2. 股票代码格式校验
        if not order.code.startswith("HK."):
            return {
                "success": False,
                "message": f"股票代码格式错误: {order.code}，港股代码应以'HK.'开头"
            }
        
        # 3. 数量校验（每手股数整数倍）
        try:
            lot_size = self._get_lot_size(order.code)
            print(f"[校验] 股票 {order.code} 每手股数: {lot_size}")
        except Exception as e:
            return {
                "success": False,
                "message": f"获取股票每手股数失败: {str(e)}"
            }

        if order.qty % lot_size != 0:
            return {
                "success": False,
                "message": f"下单数量 {order.qty} 必须是每手股数 {lot_size} 的整数倍"
            }
        
        # 4. 价格校验（限价单价格必须为正数）
        if order.price is not None and order.price <= 0:
            return {
                "success": False,
                "message": f"价格必须大于0: {order.price}"
            }
        
        # 5. 数量范围校验（不能为0或负数）
        if order.qty <= 0:
            return {
                "success": False,
                "message": f"下单数量必须大于0: {order.qty}"
            }
        
        # 6. 触发价格校验（止损单触发价格必须合理）
        if order.aux_price is not None and order.aux_price <= 0:
            return {
                "success": False,
                "message": f"触发价格必须大于0: {order.aux_price}"
            }
        
        # 7. 市价单特殊校验（市价单可以没有价格或价格可以为0）
        if order.order_type == OrderType.MARKET:
            print(f"[校验] 市价单，价格参数将被忽略")
            # 市价单可以没有价格或价格可以为0
        
        # 8. 模拟环境特殊校验（某些订单类型在模拟环境可能不支持）
        if order.trd_env == TrdEnv.SIMULATE and order.order_type not in [OrderType.NORMAL, OrderType.MARKET]:
            print(f"[警告] 模拟环境可能不支持 {order.order_type.value} 订单类型")
        
        # 9. 执行下单前最后校验 - 调用真实API获取市场快照验证股票存在
        try:
            print(f"[DEBUG] place_order validating market snapshot for {order.code}")
            ret, snapshot = self._quote_ctx.get_market_snapshot([order.code])
            if ret != RET_OK:
                return {
                    "success": False,
                    "message": f"验证股票存在失败: {snapshot}"
                }
            print(f"[校验] 股票 {order.code} 验证通过，最新价: {snapshot.iloc[0]['last_price'] if 'last_price' in snapshot.columns else 'N/A'}")
        except Exception as e:
            return {
                "success": False,
                "message": f"验证股票市场数据失败: {str(e)}"
            }
        
        # 10. 执行下单
        try:
            print(f"[执行] 开始执行下单，订单类型: {order.order_type.value}, 环境: {order.trd_env.value}")
            order_id = self._execute_order(order)
            print(f"[DEBUG] place_order finished: order_id={order_id}")
            return {
                "success": True,
                "order_id": order_id,
                "message": "下单成功",
                "lot_size": lot_size,
                "trd_env": order.trd_env.value
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"下单失败: {str(e)}"
            }

    def _get_lot_size(self, code: str) -> int:
        """获取股票每手股数（带缓存）"""
        print(f"[DEBUG] _get_lot_size start: code={code}, cache_hit={code in self._lot_size_cache}")
        # 确保上下文已初始化
        self._ensure_contexts_initialized()
        
        if code not in self._lot_size_cache:
            # 调用富途行情API获取股票基本信息
            try:
                # 使用quote context的get_market_snapshot方法获取股票信息
                print(f"[DEBUG] _get_lot_size fetching snapshot for {code}")
                ret, data = self._quote_ctx.get_market_snapshot([code])
                if ret != RET_OK:
                    raise Exception(f"获取股票市场快照失败: {data}")
                
                if len(data) == 0:
                    raise Exception(f"未找到股票 {code} 的市场快照信息")
                
                # 提取每手股数
                lot_size = data.iloc[0]['lot_size']
                self._lot_size_cache[code] = lot_size
                print(f"[DEBUG] _get_lot_size fetched: code={code}, lot_size={lot_size}")
                
            except Exception as e:
                raise Exception(f"无法获取股票 {code} 的每手股数: {str(e)}")
        
        print(f"[DEBUG] _get_lot_size end: code={code}, lot_size={self._lot_size_cache[code]}")
        return self._lot_size_cache[code]

    def _execute_order(self, order: Order) -> str:
        """
        实际调用富途 API 下单，返回订单号
        根据富途API文档，place_order方法接受以下参数：
        - price: 价格（限价单必须）
        - qty: 数量
        - code: 股票代码
        - trd_side: 交易方向
        - order_type: 订单类型
        - trd_env: 交易环境
        - time_in_force: 订单有效期
        - fill_outside_rth: 是否允许盘后成交
        - remark: 备注
        - adjust_limit: 调整限价类型
        - aux_price: 触发价格（止损单需要）
        - trail_type: 跟踪类型
        - trail_value: 跟踪值
        - trail_spread: 跟踪价差
        - session: 交易时段
        """
        
        # 转换枚举值为富途的枚举值
        trd_side = FutuTrdSide.BUY if order.trd_side == TrdSide.BUY else FutuTrdSide.SELL
        trd_env = FutuTrdEnv.REAL if order.trd_env == TrdEnv.REAL else FutuTrdEnv.SIMULATE
        order_type = getattr(FutuOrderType, order.order_type.value)
        time_in_force = getattr(FutuTimeInForce, order.time_in_force.value)
        
        # 转换session字符串为Session枚举
        if order.session == "NONE":
            session_enum = Session.NONE
        elif order.session == "NORMAL":
            session_enum = Session.NORMAL
        elif order.session == "AM":
            session_enum = Session.AM
        elif order.session == "PM":
            session_enum = Session.PM
        else:
            session_enum = Session.NONE
        
        # 构建参数字典，根据富途API文档传递所有必要参数
        params = {
            'price': order.price,
            'qty': order.qty,
            'code': order.code,
            'trd_side': trd_side,
            'order_type': order_type,
            'trd_env': trd_env,
            'time_in_force': time_in_force,
            'fill_outside_rth': order.fill_outside_rth,
            'session': session_enum,
            'adjust_limit': order.adjust_limit,
            'acc_id': order.acc_id,
            'acc_index': order.acc_index,
        }
        
        # 添加可选参数（仅当不为None时传入）
        if order.remark is not None:
            params['remark'] = order.remark
        if order.aux_price is not None:
            params['aux_price'] = order.aux_price
        if order.trail_type is not None:
            params['trail_type'] = order.trail_type
        if order.trail_value is not None:
            params['trail_value'] = order.trail_value
        if order.trail_spread is not None:
            params['trail_spread'] = order.trail_spread
        
        # 调试：打印参数
        print(f"[DEBUG] 调用place_order参数:")
        for key, value in params.items():
            print(f"  {key}: {value} ({type(value).__name__})")
        
        # 调用真实的富途API
        print("[DEBUG] calling self._ctx.place_order(...)")
        ret, data = self._ctx.place_order(**params)
        print(f"[DEBUG] self._ctx.place_order returned: ret={ret}, data_type={type(data).__name__}")
        
        # 检查返回结果
        if ret != RET_OK:
            raise Exception(f"下单失败: {data}")
        
        # 从返回的DataFrame中提取订单号
        if hasattr(data, 'iloc'):
            order_id = data['order_id'][0] if len(data) > 0 else None
        else:
            order_id = data.get('order_id') if isinstance(data, dict) else None
            
        if not order_id:
            raise Exception("下单成功但未获取到订单号")
            
        print(f"[DEBUG] 下单成功，订单号: {order_id}")
        return order_id

        # ----- 新增：改单撤单功能 -----
    def modify_order(self, modify_op: 'ModifyOrderOp', order_id: str,
                     trd_env: TrdEnv,
                     qty: Optional[float] = None, price: Optional[float] = None,
                     acc_id: int = 0,
                     adjust_limit: float = 0.0, aux_price: Optional[float] = None,
                     trail_type: Optional[str] = None, trail_value: Optional[float] = None,
                     trail_spread: Optional[float] = None) -> Dict[str, Any]:
        """
        修改订单（包括改价、改量、撤单、生效/失效、删除）
        :param modify_op: 改单操作类型，如 ModifyOrderOp.CANCEL
        :param order_id: 订单号
        :param qty: 修改后的数量（改单时需要，撤单时可传0或None）
        :param price: 修改后的价格（改单时需要，撤单时可传0或None）
        :param acc_id: 账户ID，0表示默认账户
        :param trd_env: 交易环境，REAL 或 SIMULATE
        :param adjust_limit: 价格微调幅度，默认0
        :param aux_price: 触发价格（特定订单类型需要）
        :param trail_type: 跟踪类型
        :param trail_value: 跟踪金额/百分比
        :param trail_spread: 指定价差（跟踪止损限价单需要）
        :return: 统一格式的结果字典
        """
        self._ensure_contexts_initialized()

        # 转换枚举值为富途的枚举值
        futu_modify_op = getattr(FutuModifyOrderOp, modify_op.value)
        futu_trd_env = FutuTrdEnv.REAL if trd_env == TrdEnv.REAL else FutuTrdEnv.SIMULATE
        
        # 2. 构建参数（撤单时 qty/price 传0，与API要求一致）
        params = {
            "modify_order_op": futu_modify_op,
            "order_id": order_id,
            "qty": qty if qty is not None else 0,
            "price": price if price is not None else 0,
            "trd_env": futu_trd_env,
            "acc_id": acc_id,
            "adjust_limit": adjust_limit,
        }
        # 添加可选参数（仅当不为None时传入）
        if aux_price is not None:
            params["aux_price"] = aux_price
        if trail_type is not None:
            params["trail_type"] = trail_type
        if trail_value is not None:
            params["trail_value"] = trail_value
        if trail_spread is not None:
            params["trail_spread"] = trail_spread

        # 3. 调用富途 API
        try:
            ret, data = self._ctx.modify_order(**params)
            if ret != RET_OK:
                raise Exception(f"改单失败: {data}")
            # 处理返回的 DataFrame，提取订单号
            order_id_result = data['order_id'][0] if hasattr(data, 'iloc') else data
            return {
                "success": True,
                "order_id": order_id_result,
                "data": data.to_dict(orient='records') if hasattr(data, 'to_dict') else data,
                "message": "操作成功"
            }
        except Exception as e:
            return {"success": False, "message": f"改单撤单失败: {str(e)}"}

    def cancel_all_orders(self, trd_env: TrdEnv,
                          acc_id: int = 0,
                          trdmarket: Optional[str] = None) -> Dict[str, Any]:
        """
        撤销指定账户的全部订单（注意：模拟交易和A股通不支持）
        :param acc_id: 账户ID，0表示默认账户
        :param trd_env: 交易环境，REAL 或 SIMULATE
        :param trdmarket: 指定交易市场，如 TrdMarket.HK，不传则撤销全部市场
        :return: 统一格式的结果字典
        """
        self._ensure_contexts_initialized()

        # 转换枚举值为富途的枚举值
        futu_trd_env = FutuTrdEnv.REAL if trd_env == TrdEnv.REAL else FutuTrdEnv.SIMULATE

        params = {
            "trd_env": futu_trd_env,
            "acc_id": acc_id,
        }
        if trdmarket:
            params["trdmarket"] = trdmarket

        try:
            ret, data = self._ctx.cancel_all_order(**params)
            if ret != RET_OK:
                raise Exception(f"全部撤单失败: {data}")
            return {"success": True, "message": "全部撤单成功", "data": data}
        except Exception as e:
            return {"success": False, "message": f"全部撤单失败: {str(e)}"}
            
# ---------- 创建内部服务实例（全局唯一，可根据需要配置）----------
# 如果使用 Redis，可以传入 redis_client
# redis_client = redis.Redis(host='localhost', port=6379, db=0)
# _trade_service = _HKTradeService(env=TrdEnv.SIMULATE, redis_client=redis_client)

_trade_service = _HKTradeService()


# ---------- 对外暴露的安全函数 ----------
def submit_order(
    code: str,
    side: str,
    qty: int,
    acc_id: int,
    trd_env: str,
    price: Optional[float] = None,
    order_type: str = "NORMAL",
    aux_price: Optional[float] = None,
    remark: Optional[str] = None,
    time_in_force: str = "DAY",
    # 可根据需要添加其他常用参数，但建议保持简洁
) -> Dict[str, Any]:
    """
    安全的下单函数（供 LLM 或脚本调用）

    参数说明：
        code (str): 股票代码，如 "HK.00700"
        side (str): 交易方向，"BUY" 或 "SELL"
        qty (int): 股数
        acc_id (int): 账户ID
        trd_env (str): 交易环境，"REAL" 或 "SIMULATE"
        price (float, optional): 价格（限价单必须提供）
        order_type (str): 订单类型，可选值：
            - "NORMAL": 限价单
            - "MARKET": 市价单
            - "ABSOLUTE_LIMIT": 绝对限价订单（仅港股）
            - "AUCTION": 竞价订单（仅港股）
            - "AUCTION_LIMIT": 竞价限价订单（仅港股）
            - "SPECIAL_LIMIT": 特别限价订单（仅港股）
            - "SPECIAL_LIMIT_ALL": 特别限价且要求全部成交订单（仅港股）
            - "STOP": 止损市价单
            - "STOP_LIMIT": 止损限价单
            - "MARKET_IF_TOUCHED": 触及市价单（止盈）
            - "LIMIT_IF_TOUCHED": 触及限价单（止盈）
            - "TRAILING_STOP": 跟踪止损市价单
            - "TRAILING_STOP_LIMIT": 跟踪止损限价单
            - "TWAP": 时间加权市价算法单（仅美股）
            - "TWAP_LIMIT": 时间加权限价算法单（港股和美股）
            - "VWAP": 成交量加权市价算法单（仅美股）
            - "VWAP_LIMIT": 成交量加权限价算法单（港股和美股）
        aux_price (float, optional): 触发价（止损单必须提供）
        remark (str, optional): 备注
        time_in_force (str): 订单有效期，默认 "DAY"
    返回：
        dict: 包含以下字段的字典
            - success (bool): 是否成功
            - order_id (str, optional): 订单号（成功时）
            - message (str): 结果描述
    """
    # 构造 Order 对象
    try:
        order = Order(
            code=code,
            trd_side=TrdSide(side.upper()),  # 转为枚举
            qty=qty,
            acc_id=acc_id,
            trd_env=TrdEnv(trd_env.upper()),
            price=price,
            order_type=OrderType(order_type.upper()),
            aux_price=aux_price,
            remark=remark,
            time_in_force=TimeInForce(time_in_force.upper())
        )
    except ValueError as e:
        # 枚举转换失败或模型验证失败
        return {
            "success": False,
            "message": f"订单参数错误: {str(e)}"
        }

    try:
        return _trade_service.place_order(order)
    finally:
        _trade_service.close()

def modify_order(
    op: str,
    order_id: str,
    trd_env: str,
    qty: Optional[float] = None,
    price: Optional[float] = None,
    acc_id: int = 0,
    **kwargs
) -> Dict[str, Any]:
    """
    修改订单（供 LLM 或脚本调用）

    参数说明：
        op (str): 操作类型，可选值：
            - "CANCEL": 撤单
            - "NORMAL": 修改订单（需提供新的 qty/price）
            - "DISABLE": 使失效
            - "ENABLE": 使生效
            - "DELETE": 删除
        order_id (str): 订单号
        qty (float, optional): 修改后的数量（改单时需要）
        price (float, optional): 修改后的价格（改单时需要）
        acc_id (int): 账户ID，0表示默认账户
        trd_env (str): 交易环境，"REAL" 或 "SIMULATE"
        **kwargs: 其他可选参数，如 aux_price, trail_type 等

    返回：
        dict: 包含 success、message、order_id 等字段
    """
    try:
        op_enum = ModifyOrderOp(op.upper())
    except ValueError:
        return {"success": False, "message": f"无效的操作类型: {op}"}
    try:
        trd_env_enum = TrdEnv(trd_env.upper())
    except ValueError:
        return {"success": False, "message": f"无效的交易环境: {trd_env}"}

    try:
        return _trade_service.modify_order(
            modify_op=op_enum,
            order_id=order_id,
            qty=qty,
            price=price,
            acc_id=acc_id,
            trd_env=trd_env_enum,
            **kwargs
        )
    finally:
        _trade_service.close()

def cancel_order(order_id: str, trd_env: str, acc_id: int = 0) -> Dict[str, Any]:
    """简化撤单函数"""
    return modify_order(op="CANCEL", order_id=order_id, trd_env=trd_env, acc_id=acc_id)

def cancel_all_orders(trd_env: str, acc_id: int = 0, trdmarket: Optional[str] = None) -> Dict[str, Any]:
    """撤销全部订单"""
    try:
        trd_env_enum = TrdEnv(trd_env.upper())
    except ValueError:
        return {"success": False, "message": f"无效的交易环境: {trd_env}"}
    try:
        return _trade_service.cancel_all_orders(acc_id=acc_id, trd_env=trd_env_enum, trdmarket=trdmarket)
    finally:
        _trade_service.close()


def close_trade_service() -> None:
    _trade_service.close()

# 可选：如果希望命令行直接调用，可以添加以下代码
if __name__ == "__main__":
    # 简单的命令行测试
    import argparse
    parser = argparse.ArgumentParser(description="港股下单工具")
    parser.add_argument("--code", required=True, help="股票代码，如 HK.00700")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL"], help="交易方向")
    parser.add_argument("--qty", type=int, required=True, help="股数")
    parser.add_argument("--acc_id", type=int, required=True, help="账户ID")
    parser.add_argument("--trd_env", required=True, choices=["REAL", "SIMULATE"], help="交易环境")
    parser.add_argument("--price", type=float, help="价格（限价单需要）")
    parser.add_argument("--order_type", default="NORMAL", 
                       choices=["NORMAL", "MARKET", "ABSOLUTE_LIMIT", "AUCTION", "AUCTION_LIMIT", 
                               "SPECIAL_LIMIT", "SPECIAL_LIMIT_ALL", "STOP", "STOP_LIMIT",
                               "MARKET_IF_TOUCHED", "LIMIT_IF_TOUCHED", "TRAILING_STOP", 
                               "TRAILING_STOP_LIMIT", "TWAP", "TWAP_LIMIT", "VWAP", "VWAP_LIMIT"], 
                       help="订单类型")
    parser.add_argument("--aux_price", type=float, help="触发价（止损单需要）")
    args = parser.parse_args()

    result = submit_order(
        code=args.code,
        side=args.side,
        qty=args.qty,
        acc_id=args.acc_id,
        trd_env=args.trd_env,
        price=args.price,
        order_type=args.order_type,
        aux_price=args.aux_price
    )
    print(result)
