"""
港股行情服务模块

第一阶段：
- 行情连接管理（延迟初始化）
- 基础数据获取（stock basic info / market state）

第二阶段：
- 订阅管理（subscribe / unsubscribe / unsubscribe_all / query_subscription）
- 实时报价与摆盘回调（StockQuote / OrderBook）
"""

from typing import Any, Callable, Dict, List, Optional

try:
    from futu import (
        AuType,
        KLType,
        Market,
        OpenQuoteContext,
        OrderBookHandlerBase,
        RET_ERROR,
        RET_OK,
        SecurityType,
        Session,
        StockQuoteHandlerBase,
        SubType,
    )
except Exception as e:
    raise RuntimeError(
        "加载 futu SDK 失败。若你在 OpenClaw/Codex 或其他受限沙箱中运行，请改用 host/elevated 模式。"
        "Futu SDK 在导入阶段可能需要访问本机 OpenD 资源并写入 ~/.com.futunn.FutuOpenD/Log。"
    ) from e

from config_manager import get_host, get_port


class _StockQuotePushHandler(StockQuoteHandlerBase):
    def __init__(self, callback: Callable[[Dict[str, Any]], None]):
        super().__init__()
        self._callback = callback

    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super().on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            self._callback({"success": False, "type": "QUOTE", "error": str(data)})
            return RET_ERROR, data

        rows = data.to_dict(orient="records") if hasattr(data, "to_dict") else data
        self._callback({"success": True, "type": "QUOTE", "data": rows})
        return RET_OK, data


class _OrderBookPushHandler(OrderBookHandlerBase):
    def __init__(self, callback: Callable[[Dict[str, Any]], None]):
        super().__init__()
        self._callback = callback

    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super().on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            self._callback({"success": False, "type": "ORDER_BOOK", "error": str(data)})
            return RET_ERROR, data

        self._callback({"success": True, "type": "ORDER_BOOK", "data": data})
        return RET_OK, data


class _HKQuoteService:
    def __init__(self):
        self._ctx: Optional[OpenQuoteContext] = None
        self._quote_handler: Optional[_StockQuotePushHandler] = None
        self._orderbook_handler: Optional[_OrderBookPushHandler] = None

    def _ensure_context_initialized(self):
        if self._ctx is None:
            self._ctx = OpenQuoteContext(host=get_host(), port=get_port())
            print("[初始化] 行情上下文已创建")

    def _reset_context(self):
        self.close()
        self._ensure_context_initialized()

    def _with_retry(self, fn: Callable[[], Dict[str, Any]]) -> Dict[str, Any]:
        result = fn()
        msg = str(result.get("message", ""))
        if result.get("success") is False and "网络中断" in msg:
            print("[重试] 检测到网络中断，重连后重试一次")
            self._reset_context()
            result = fn()
        return result

    def _ensure_subscribed_for_pull(self, code: str, subtype: SubType) -> Dict[str, Any]:
        self._ensure_context_initialized()
        try:
            ret, data = self._ctx.subscribe(
                code_list=[code],
                subtype_list=[subtype],
                is_first_push=False,
                subscribe_push=False,
                is_detailed_orderbook=False,
                extended_time=False,
                session=Session.NONE,
            )
            if ret != RET_OK:
                return {"success": False, "message": f"自动订阅失败: {data}"}
            return {"success": True, "message": "自动订阅成功"}
        except Exception as e:
            return {"success": False, "message": f"自动订阅异常: {str(e)}"}

    def close(self):
        try:
            if self._ctx is not None:
                self._ctx.close()
                self._ctx = None
                print("[清理] 行情上下文已关闭")
        except Exception as e:
            print(f"[警告] 关闭行情上下文时出错: {str(e)}")

    def get_stock_basicinfo(
        self,
        market: Market = Market.HK,
        stock_type: SecurityType = SecurityType.STOCK,
        code_list: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        self._ensure_context_initialized()
        def _run():
            try:
                ret, data = self._ctx.get_stock_basicinfo(market=market, stock_type=stock_type, code_list=code_list)
                if ret != RET_OK:
                    return {"success": False, "message": f"获取基础信息失败: {data}", "data": None}
                rows = data.to_dict(orient="records") if hasattr(data, "to_dict") else data
                return {"success": True, "message": "获取基础信息成功", "data": rows}
            except Exception as e:
                return {"success": False, "message": f"获取基础信息异常: {str(e)}", "data": None}
        return self._with_retry(_run)

    def get_market_state(self, code_list: List[str]) -> Dict[str, Any]:
        self._ensure_context_initialized()
        def _run():
            try:
                ret, data = self._ctx.get_market_state(code_list)
                if ret != RET_OK:
                    return {"success": False, "message": f"获取市场状态失败: {data}", "data": None}
                rows = data.to_dict(orient="records") if hasattr(data, "to_dict") else data
                return {"success": True, "message": "获取市场状态成功", "data": rows}
            except Exception as e:
                return {"success": False, "message": f"获取市场状态异常: {str(e)}", "data": None}
        return self._with_retry(_run)

    def query_subscription(self) -> Dict[str, Any]:
        self._ensure_context_initialized()
        def _run():
            try:
                ret, data = self._ctx.query_subscription()
                if ret != RET_OK:
                    return {"success": False, "message": f"查询订阅失败: {data}", "data": None}
                return {"success": True, "message": "查询订阅成功", "data": data}
            except Exception as e:
                return {"success": False, "message": f"查询订阅异常: {str(e)}", "data": None}
        return self._with_retry(_run)

    def subscribe(
        self,
        code_list: List[str],
        subtype_list: List[SubType],
        is_first_push: bool = True,
        subscribe_push: bool = True,
        is_detailed_orderbook: bool = False,
        extended_time: bool = False,
        session: Session = Session.NONE,
    ) -> Dict[str, Any]:
        self._ensure_context_initialized()
        def _run():
            try:
                ret, data = self._ctx.subscribe(
                    code_list=code_list,
                    subtype_list=subtype_list,
                    is_first_push=is_first_push,
                    subscribe_push=subscribe_push,
                    is_detailed_orderbook=is_detailed_orderbook,
                    extended_time=extended_time,
                    session=session,
                )
                if ret != RET_OK:
                    return {"success": False, "message": f"订阅失败: {data}"}
                return {"success": True, "message": "订阅成功"}
            except Exception as e:
                return {"success": False, "message": f"订阅异常: {str(e)}"}
        return self._with_retry(_run)

    def unsubscribe(self, code_list: List[str], subtype_list: List[SubType], unsubscribe_all: bool = False) -> Dict[str, Any]:
        self._ensure_context_initialized()
        def _run():
            try:
                ret, data = self._ctx.unsubscribe(
                    code_list=code_list, subtype_list=subtype_list, unsubscribe_all=unsubscribe_all
                )
                if ret != RET_OK:
                    return {"success": False, "message": f"取消订阅失败: {data}"}
                return {"success": True, "message": "取消订阅成功"}
            except Exception as e:
                return {"success": False, "message": f"取消订阅异常: {str(e)}"}
        return self._with_retry(_run)

    def unsubscribe_all(self) -> Dict[str, Any]:
        self._ensure_context_initialized()
        def _run():
            try:
                ret, data = self._ctx.unsubscribe_all()
                if ret != RET_OK:
                    return {"success": False, "message": f"取消全部订阅失败: {data}"}
                return {"success": True, "message": "取消全部订阅成功"}
            except Exception as e:
                return {"success": False, "message": f"取消全部订阅异常: {str(e)}"}
        return self._with_retry(_run)

    def set_quote_callback(self, callback: Callable[[Dict[str, Any]], None]) -> Dict[str, Any]:
        self._ensure_context_initialized()
        try:
            self._quote_handler = _StockQuotePushHandler(callback=callback)
            self._ctx.set_handler(self._quote_handler)
            return {"success": True, "message": "实时报价回调已设置"}
        except Exception as e:
            return {"success": False, "message": f"设置实时报价回调异常: {str(e)}"}

    def set_orderbook_callback(self, callback: Callable[[Dict[str, Any]], None]) -> Dict[str, Any]:
        self._ensure_context_initialized()
        try:
            self._orderbook_handler = _OrderBookPushHandler(callback=callback)
            self._ctx.set_handler(self._orderbook_handler)
            return {"success": True, "message": "实时摆盘回调已设置"}
        except Exception as e:
            return {"success": False, "message": f"设置实时摆盘回调异常: {str(e)}"}

    def get_market_snapshot(self, code_list: List[str]) -> Dict[str, Any]:
        self._ensure_context_initialized()
        def _run():
            try:
                ret, data = self._ctx.get_market_snapshot(code_list)
                if ret != RET_OK:
                    return {"success": False, "message": f"获取市场快照失败: {data}", "data": None}
                rows = data.to_dict(orient="records") if hasattr(data, "to_dict") else data
                return {"success": True, "message": "获取市场快照成功", "data": rows}
            except Exception as e:
                return {"success": False, "message": f"获取市场快照异常: {str(e)}", "data": None}
        return self._with_retry(_run)

    def get_cur_kline(
        self, code: str, num: int = 100, ktype: KLType = KLType.K_DAY, autype: AuType = AuType.QFQ
    ) -> Dict[str, Any]:
        self._ensure_context_initialized()
        def _run():
            try:
                ret, data = self._ctx.get_cur_kline(code=code, num=num, ktype=ktype, autype=autype)
                if ret != RET_OK:
                    return {"success": False, "message": f"获取当前K线失败: {data}", "data": None}
                rows = data.to_dict(orient="records") if hasattr(data, "to_dict") else data
                return {"success": True, "message": "获取当前K线成功", "data": rows}
            except Exception as e:
                return {"success": False, "message": f"获取当前K线异常: {str(e)}", "data": None}
        result = self._with_retry(_run)
        if result.get("success") is False and "请先订阅" in str(result.get("message", "")):
            subtype_name = ktype.name if hasattr(ktype, "name") else str(ktype).upper()
            subtype = getattr(SubType, subtype_name, None)
            if subtype is None:
                return result
            sub_result = self._ensure_subscribed_for_pull(code, subtype)
            if sub_result.get("success"):
                subtype_display = subtype.name if hasattr(subtype, "name") else str(subtype)
                print(f"[自动订阅] 已自动订阅 {code} {subtype_display}，重试获取当前K线")
                result = self._with_retry(_run)
        return result

    def request_history_kline(
        self,
        code: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        ktype: KLType = KLType.K_DAY,
        autype: AuType = AuType.QFQ,
        max_count: int = 100,
    ) -> Dict[str, Any]:
        self._ensure_context_initialized()
        def _run():
            try:
                ret, data, page_req_key = self._ctx.request_history_kline(
                    code=code, start=start, end=end, ktype=ktype, autype=autype, max_count=max_count
                )
                if ret != RET_OK:
                    return {"success": False, "message": f"获取历史K线失败: {data}", "data": None}
                rows = data.to_dict(orient="records") if hasattr(data, "to_dict") else data
                return {"success": True, "message": "获取历史K线成功", "data": rows, "page_req_key": page_req_key}
            except Exception as e:
                return {"success": False, "message": f"获取历史K线异常: {str(e)}", "data": None}
        return self._with_retry(_run)

    def get_rt_ticker(self, code: str, num: int = 100) -> Dict[str, Any]:
        self._ensure_context_initialized()
        def _run():
            try:
                ret, data = self._ctx.get_rt_ticker(code=code, num=num)
                if ret != RET_OK:
                    return {"success": False, "message": f"获取实时逐笔失败: {data}", "data": None}
                rows = data.to_dict(orient="records") if hasattr(data, "to_dict") else data
                return {"success": True, "message": "获取实时逐笔成功", "data": rows}
            except Exception as e:
                return {"success": False, "message": f"获取实时逐笔异常: {str(e)}", "data": None}
        result = self._with_retry(_run)
        if result.get("success") is False and "请先订阅" in str(result.get("message", "")):
            sub_result = self._ensure_subscribed_for_pull(code, SubType.TICKER)
            if sub_result.get("success"):
                print(f"[自动订阅] 已自动订阅 {code} TICKER，重试获取实时逐笔")
                result = self._with_retry(_run)
        return result


_quote_service = _HKQuoteService()


def _to_market(market: str) -> Market:
    return getattr(Market, market.upper())


def _to_security_type(sec_type: str) -> SecurityType:
    return getattr(SecurityType, sec_type.upper())


def _to_subtypes(subtype_list: List[str]) -> List[SubType]:
    return [getattr(SubType, s.upper()) for s in subtype_list]


def _to_session(session: str) -> Session:
    return getattr(Session, session.upper())


def _to_ktype(ktype: str) -> KLType:
    return getattr(KLType, ktype.upper())


def _to_autype(autype: str) -> AuType:
    return getattr(AuType, autype.upper())


def get_stock_basicinfo(
    market: str = "HK", sec_type: str = "STOCK", code_list: Optional[List[str]] = None
) -> Dict[str, Any]:
    try:
        return _quote_service.get_stock_basicinfo(
            market=_to_market(market), stock_type=_to_security_type(sec_type), code_list=code_list
        )
    except Exception as e:
        return {"success": False, "message": f"参数错误: {str(e)}", "data": None}
    finally:
        _quote_service.close()


def get_market_state(code_list: List[str]) -> Dict[str, Any]:
    try:
        return _quote_service.get_market_state(code_list)
    finally:
        _quote_service.close()


def query_subscription() -> Dict[str, Any]:
    return _quote_service.query_subscription()


def subscribe(
    code_list: List[str],
    subtype_list: List[str],
    is_first_push: bool = True,
    subscribe_push: bool = True,
    is_detailed_orderbook: bool = False,
    extended_time: bool = False,
    session: str = "NONE",
) -> Dict[str, Any]:
    try:
        return _quote_service.subscribe(
            code_list=code_list,
            subtype_list=_to_subtypes(subtype_list),
            is_first_push=is_first_push,
            subscribe_push=subscribe_push,
            is_detailed_orderbook=is_detailed_orderbook,
            extended_time=extended_time,
            session=_to_session(session),
        )
    except Exception as e:
        return {"success": False, "message": f"参数错误: {str(e)}"}


def unsubscribe(code_list: List[str], subtype_list: List[str], unsubscribe_all: bool = False) -> Dict[str, Any]:
    try:
        return _quote_service.unsubscribe(
            code_list=code_list, subtype_list=_to_subtypes(subtype_list), unsubscribe_all=unsubscribe_all
        )
    except Exception as e:
        return {"success": False, "message": f"参数错误: {str(e)}"}


def unsubscribe_all() -> Dict[str, Any]:
    return _quote_service.unsubscribe_all()


def set_quote_callback(callback: Callable[[Dict[str, Any]], None]) -> Dict[str, Any]:
    return _quote_service.set_quote_callback(callback)


def set_orderbook_callback(callback: Callable[[Dict[str, Any]], None]) -> Dict[str, Any]:
    return _quote_service.set_orderbook_callback(callback)


def start_quote_stream(
    code_list: List[str],
    callback: Callable[[Dict[str, Any]], None],
    is_first_push: bool = True,
    extended_time: bool = False,
    session: str = "NONE",
) -> Dict[str, Any]:
    callback_result = set_quote_callback(callback)
    if not callback_result.get("success"):
        return callback_result
    subscribe_result = subscribe(
        code_list=code_list,
        subtype_list=["QUOTE"],
        is_first_push=is_first_push,
        subscribe_push=True,
        extended_time=extended_time,
        session=session,
    )
    if not subscribe_result.get("success"):
        return {
            "success": False,
            "message": f"行情流启动失败: {subscribe_result.get('message')}",
            "callback_result": callback_result,
            "subscribe_result": subscribe_result,
        }
    return {
        "success": True,
        "message": "实时报价监听已启动",
        "code_list": code_list,
        "subtype": "QUOTE",
        "callback_result": callback_result,
        "subscribe_result": subscribe_result,
    }


def start_orderbook_stream(
    code_list: List[str],
    callback: Callable[[Dict[str, Any]], None],
    is_first_push: bool = True,
    is_detailed_orderbook: bool = False,
    extended_time: bool = False,
    session: str = "NONE",
) -> Dict[str, Any]:
    callback_result = set_orderbook_callback(callback)
    if not callback_result.get("success"):
        return callback_result
    subscribe_result = subscribe(
        code_list=code_list,
        subtype_list=["ORDER_BOOK"],
        is_first_push=is_first_push,
        subscribe_push=True,
        is_detailed_orderbook=is_detailed_orderbook,
        extended_time=extended_time,
        session=session,
    )
    if not subscribe_result.get("success"):
        return {
            "success": False,
            "message": f"摆盘流启动失败: {subscribe_result.get('message')}",
            "callback_result": callback_result,
            "subscribe_result": subscribe_result,
        }
    return {
        "success": True,
        "message": "实时摆盘监听已启动",
        "code_list": code_list,
        "subtype": "ORDER_BOOK",
        "callback_result": callback_result,
        "subscribe_result": subscribe_result,
    }


def get_market_snapshot(code_list: List[str]) -> Dict[str, Any]:
    try:
        return _quote_service.get_market_snapshot(code_list)
    finally:
        _quote_service.close()


def get_cur_kline(code: str, num: int = 100, ktype: str = "K_DAY", autype: str = "QFQ") -> Dict[str, Any]:
    try:
        return _quote_service.get_cur_kline(code=code, num=num, ktype=_to_ktype(ktype), autype=_to_autype(autype))
    except Exception as e:
        return {"success": False, "message": f"参数错误: {str(e)}", "data": None}
    finally:
        _quote_service.close()


def request_history_kline(
    code: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    ktype: str = "K_DAY",
    autype: str = "QFQ",
    max_count: int = 100,
) -> Dict[str, Any]:
    try:
        return _quote_service.request_history_kline(
            code=code, start=start, end=end, ktype=_to_ktype(ktype), autype=_to_autype(autype), max_count=max_count
        )
    except Exception as e:
        return {"success": False, "message": f"参数错误: {str(e)}", "data": None}
    finally:
        _quote_service.close()


def get_rt_ticker(code: str, num: int = 100) -> Dict[str, Any]:
    try:
        return _quote_service.get_rt_ticker(code=code, num=num)
    finally:
        _quote_service.close()


def close_quote_service():
    _quote_service.close()
