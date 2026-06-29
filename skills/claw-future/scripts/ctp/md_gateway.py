"""
md_gateway.py

行情网关：封装 md_create / md_poll，提供迭代器接口供 daemon 消费。

用法：
    gw = MdGateway(front="tcp://180.168.146.187:10211")
    gw.connect(broker_id, user_id, password)
    gw.subscribe("IF2505,rb2510")
    for event_type, data in gw.events(timeout_ms=100):
        ...
"""

import json
import ctypes
import logging
import time
from typing import Iterator, Tuple

from . import bridge_loader as _B
from .bridge_loader import b

logger = logging.getLogger("clawtrader.md")

# 事件类型常量（与 ctp_bridge.h 保持一致）
EVT_MD_FRONT_CONNECTED    = 101
EVT_MD_FRONT_DISCONNECTED = 102
EVT_MD_RSP_LOGIN          = 103
EVT_MD_RSP_SUBSCRIBE      = 104
EVT_MD_TICK               = 105
EVT_RSP_ERROR             = 16

_POLL_BUF_SIZE = 8192


class MdGateway:
    def __init__(self, front: str, flow_path: str = "./md_flow/"):
        self._front      = front
        self._flow_path  = flow_path
        self._handle     = None
        self._buf        = ctypes.create_string_buffer(_POLL_BUF_SIZE)
        self._req_id     = 0
        self._connected  = False
        self._logged_in  = False

    # ---------------------------------------------------------------- #

    def connect(self, broker_id: str, user_id: str, password: str) -> None:
        self._broker_id  = broker_id
        self._user_id    = user_id
        self._password   = password

        import os
        os.makedirs(self._flow_path, exist_ok=True)

        self._handle = _B.md_create(b(self._flow_path))
        _B.md_register_front(self._handle, b(self._front))
        _B.md_init(self._handle)

        # 等待 CONNECTED 事件再登录
        logger.info("MdGateway 初始化，等待连接 %s ...", self._front)

    def subscribe(self, instruments: str) -> int:
        """instruments: 逗号分隔，如 'IF2505,rb2510'"""
        if not self._handle:
            raise RuntimeError("未连接")
        return _B.md_subscribe(self._handle, b(instruments))

    def unsubscribe(self, instruments: str) -> int:
        if not self._handle:
            return -1
        return _B.md_unsubscribe(self._handle, b(instruments))

    def release(self) -> None:
        if self._handle:
            _B.md_release(self._handle)
            self._handle = None

    # ---------------------------------------------------------------- #
    #  事件迭代                                                          #
    # ---------------------------------------------------------------- #

    def events(self, timeout_ms: int = 200) -> Iterator[Tuple[int, dict]]:
        """每次调用阻塞最多 timeout_ms 毫秒，yield (evt_type, dict)"""
        if not self._handle:
            return
        evt = _B.md_poll(self._handle, self._buf, _POLL_BUF_SIZE, timeout_ms)
        if evt == 0:
            return
        try:
            data = json.loads(self._buf.value.decode("utf-8", errors="replace"))
        except Exception:
            data = {"raw": self._buf.value.decode("utf-8", errors="replace")}

        # 内部状态维护
        if evt == EVT_MD_FRONT_CONNECTED:
            self._connected = True
            logger.info("行情前置已连接，发起登录")
            self._req_id += 1
            _B.md_login(self._handle,
                        b(self._broker_id), b(self._user_id), b(self._password),
                        self._req_id)
        elif evt == EVT_MD_FRONT_DISCONNECTED:
            self._connected = False
            self._logged_in = False
            logger.warning("行情前置断开: reason=%s", data.get("reason"))
        elif evt == EVT_MD_RSP_LOGIN:
            if data.get("error_id", 0) == 0:
                self._logged_in = True
                logger.info("行情登录成功，交易日 %s", data.get("trading_day"))
            else:
                logger.error("行情登录失败: %s", data.get("error_msg"))

        yield evt, data

    def poll_one(self, timeout_ms: int = 200) -> Tuple[int, dict]:
        """单次轮询，返回 (evt_type, dict)，无事件返回 (0, {})"""
        for item in self.events(timeout_ms):
            return item
        return 0, {}
