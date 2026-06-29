"""
trader_gateway.py

交易网关：封装 td_* 函数，管理认证 → 登录 → 结算确认的完整流程。
"""

import json
import ctypes
import logging
import time
from typing import Iterator, Tuple

from . import bridge_loader as _B
from .bridge_loader import b

logger = logging.getLogger("clawtrader.td")

# 事件类型常量
EVT_FRONT_CONNECTED    = 1
EVT_FRONT_DISCONNECTED = 2
EVT_RSP_AUTHENTICATE   = 3
EVT_RSP_LOGIN          = 4
EVT_RSP_LOGOUT         = 5
EVT_RSP_SETTLE_CONFIRM = 6
EVT_RSP_ORDER_INSERT   = 7
EVT_RTN_ORDER          = 8
EVT_RTN_TRADE          = 9
EVT_ERR_ORDER_INSERT   = 10
EVT_ERR_ORDER_ACTION   = 11
EVT_RSP_QRY_POSITION   = 12
EVT_RSP_QRY_ACCOUNT    = 13
EVT_RSP_QRY_ORDER      = 14
EVT_RSP_QRY_TRADE      = 15
EVT_RSP_ERROR          = 16

# 常用 CTP 字符常量
DIR_BUY    = ord('0')
DIR_SELL   = ord('1')
OFFSET_OPEN      = ord('0')
OFFSET_CLOSE     = ord('1')
OFFSET_CLOSE_TODAY   = ord('3')
OFFSET_CLOSE_YESTERDAY = ord('4')
PRICE_LIMIT  = ord('2')   # 限价  THOST_FTDC_OPT_LimitPrice
PRICE_MARKET = ord('1')   # 任意价（市价）  THOST_FTDC_OPT_AnyPrice
TIME_GFD = ord('3')   # 当日有效
TIME_IOC = ord('1')   # 立即成交剩余撤销
VOL_ANY  = ord('1')   # 任何数量
VOL_ALL  = ord('2')   # 全部成交

_POLL_BUF_SIZE = 8192

# CTP 查询限速：两次查询间隔至少 1 秒
_QRY_INTERVAL = 1.1


class TraderGateway:
    def __init__(self, front: str, flow_path: str = "./td_flow/"):
        self._front      = front
        self._flow_path  = flow_path
        self._handle     = None
        self._buf        = ctypes.create_string_buffer(_POLL_BUF_SIZE)
        self._req_id     = 0
        self._order_ref  = 0         # 客户端报单引用自增
        self._last_qry_time = 0.0    # 限速

        self.connected      = False
        self.authenticated  = False
        self.logged_in      = False
        self.settled        = False

    # ---------------------------------------------------------------- #
    #  连接与认证流程                                                    #
    # ---------------------------------------------------------------- #

    def connect(self, broker_id: str, user_id: str, password: str,
                app_id: str, auth_code: str) -> None:
        self._broker_id  = broker_id
        self._user_id    = user_id
        self._password   = password
        self._app_id     = app_id
        self._auth_code  = auth_code

        import os
        os.makedirs(self._flow_path, exist_ok=True)

        self._handle = _B.td_create(b(self._flow_path))
        _B.td_register_front(self._handle, b(self._front))
        _B.td_init(self._handle)
        logger.info("TraderGateway 初始化，等待连接 %s ...", self._front)

    def release(self) -> None:
        if self._handle:
            _B.td_release(self._handle)
            self._handle = None

    def next_req_id(self) -> int:
        self._req_id += 1
        return self._req_id

    def next_order_ref(self) -> str:
        self._order_ref += 1
        return str(self._order_ref).zfill(12)

    # ---------------------------------------------------------------- #
    #  报单/撤单                                                         #
    # ---------------------------------------------------------------- #

    def send_order(self, exchange: str, instrument: str,
                   direction: str,  # 'buy' | 'sell'
                   offset: str,     # 'open' | 'close' | 'close_today' | 'close_yesterday'
                   price_type: str, # 'limit' | 'market'
                   price: float,
                   volume: int,
                   time_cond: str = 'gfd',  # 'gfd' | 'ioc'
                   vol_cond: str  = 'any',
                   ) -> Tuple[int, str]:
        """
        返回 (ret_code, order_ref)
        ret_code 0 = 发送成功（不代表成交），< 0 = 发送失败
        """
        dir_c   = DIR_BUY   if direction  == 'buy'            else DIR_SELL
        off_c   = {
            'open':             OFFSET_OPEN,
            'close':            OFFSET_CLOSE,
            'close_today':      OFFSET_CLOSE_TODAY,
            'close_yesterday':  OFFSET_CLOSE_YESTERDAY,
        }.get(offset, OFFSET_CLOSE)
        pt_c    = PRICE_MARKET if price_type == 'market' else PRICE_LIMIT
        tc_c    = TIME_IOC if time_cond == 'ioc' else TIME_GFD
        vc_c    = VOL_ALL  if vol_cond  == 'all' else VOL_ANY
        limit_p = 0.0 if price_type == 'market' else price

        order_ref = self.next_order_ref()
        ret = _B.td_order_insert(
            self._handle,
            b(self._broker_id), b(self._user_id),
            b(exchange), b(instrument), b(order_ref),
            dir_c, off_c, pt_c,
            limit_p, volume,
            tc_c, vc_c,
            self.next_req_id()
        )
        return ret, order_ref

    def cancel_order(self, exchange: str, instrument: str,
                     order_sys_id: str = "",
                     order_ref: str = "") -> int:
        rid = self.next_req_id()
        if order_sys_id:
            return _B.td_cancel_by_sysid(
                self._handle,
                b(self._broker_id), b(self._user_id),
                b(exchange), b(instrument), b(order_sys_id),
                rid
            )
        else:
            return _B.td_cancel_by_ref(
                self._handle,
                b(self._broker_id), b(self._user_id),
                b(exchange), b(instrument), b(order_ref),
                _B.td_get_front_id(self._handle),
                _B.td_get_session_id(self._handle),
                rid
            )

    # ---------------------------------------------------------------- #
    #  查询（带限速）                                                    #
    # ---------------------------------------------------------------- #

    def _wait_qry(self) -> None:
        elapsed = time.time() - self._last_qry_time
        if elapsed < _QRY_INTERVAL:
            time.sleep(_QRY_INTERVAL - elapsed)
        self._last_qry_time = time.time()

    def qry_position(self, instrument: str = "") -> int:
        self._wait_qry()
        return _B.td_qry_position(
            self._handle,
            b(self._broker_id), b(self._user_id),
            b(instrument), self.next_req_id()
        )

    def qry_account(self) -> int:
        self._wait_qry()
        return _B.td_qry_account(
            self._handle,
            b(self._broker_id), b(self._user_id),
            self.next_req_id()
        )

    def qry_order(self, instrument: str = "") -> int:
        self._wait_qry()
        return _B.td_qry_order(
            self._handle,
            b(self._broker_id), b(self._user_id),
            b(instrument), self.next_req_id()
        )

    def qry_trade(self, instrument: str = "") -> int:
        self._wait_qry()
        return _B.td_qry_trade(
            self._handle,
            b(self._broker_id), b(self._user_id),
            b(instrument), self.next_req_id()
        )

    def get_trading_day(self) -> str:
        day = _B.td_get_trading_day(self._handle)
        return day.decode() if day else ""

    # ---------------------------------------------------------------- #
    #  事件迭代                                                          #
    # ---------------------------------------------------------------- #

    def events(self, timeout_ms: int = 100) -> Iterator[Tuple[int, dict]]:
        if not self._handle:
            return
        evt = _B.td_poll(self._handle, self._buf, _POLL_BUF_SIZE, timeout_ms)
        if evt == 0:
            return
        try:
            data = json.loads(self._buf.value.decode("utf-8", errors="replace"))
        except Exception:
            data = {"raw": self._buf.value.decode("utf-8", errors="replace")}

        # 内部状态机：自动推进认证 → 登录 → 结算确认
        if evt == EVT_FRONT_CONNECTED:
            self.connected = True
            logger.info("交易前置已连接，发起客户端认证")
            _B.td_authenticate(
                self._handle,
                b(self._broker_id), b(self._user_id),
                b(self._app_id),    b(self._auth_code),
                self.next_req_id()
            )
        elif evt == EVT_FRONT_DISCONNECTED:
            self.connected = self.authenticated = self.logged_in = self.settled = False
            logger.warning("交易前置断开: reason=%s", data.get("reason"))
        elif evt == EVT_RSP_AUTHENTICATE:
            if data.get("error_id", 0) == 0:
                self.authenticated = True
                logger.info("客户端认证成功，发起登录")
                _B.td_login(
                    self._handle,
                    b(self._broker_id), b(self._user_id), b(self._password),
                    self.next_req_id()
                )
            else:
                logger.error("客户端认证失败: %s", data.get("error_msg"))
        elif evt == EVT_RSP_LOGIN:
            if data.get("error_id", 0) == 0:
                self.logged_in = True
                logger.info("交易登录成功，交易日 %s，确认结算单",
                            data.get("trading_day"))
                _B.td_settle_confirm(
                    self._handle,
                    b(self._broker_id), b(self._user_id),
                    self.next_req_id()
                )
            else:
                logger.error("交易登录失败: %s", data.get("error_msg"))
        elif evt == EVT_RSP_SETTLE_CONFIRM:
            if data.get("error_id", 0) == 0:
                self.settled = True
                logger.info("结算确认完成，可以交易")
            else:
                logger.error("结算确认失败: %s", data.get("error_msg"))

        yield evt, data

    def poll_one(self, timeout_ms: int = 100) -> Tuple[int, dict]:
        for item in self.events(timeout_ms):
            return item
        return 0, {}
