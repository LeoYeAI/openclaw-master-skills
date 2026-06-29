"""
daemon.py

ClawTrader 后台守护进程。

职责：
  1. 连接 CTP 行情（MdGateway）+ 交易（TraderGateway）
  2. 事件循环：持续处理 Tick / 委托回报 / 成交回报
  3. 条件单引擎：Tick 驱动，触发时自动下单或推送告警
  4. 收盘日报定时任务
  5. 监听本地 TCP socket，接受来自 clawtrader.py CLI 的 JSON 指令

启动：
    python daemon.py

停止：
    发送 {"cmd":"stop"} 或 Ctrl-C
"""

import os
import sys
import json
import time
import signal
import socket
import logging
import threading
import datetime
from pathlib import Path

# ---------- 路径 ----------
_SCRIPTS = Path(__file__).parent
sys.path.insert(0, str(_SCRIPTS))

import state
from ctp.md_gateway     import MdGateway,    EVT_MD_TICK
from ctp.trader_gateway import TraderGateway, EVT_RTN_ORDER, EVT_RTN_TRADE, \
                                               EVT_RSP_QRY_POSITION, EVT_RSP_QRY_ACCOUNT, \
                                               EVT_RSP_QRY_ORDER, EVT_RSP_QRY_TRADE, \
                                               EVT_RSP_ERROR, EVT_RSP_SETTLE_CONFIRM

# ---------- 日志 ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(_SCRIPTS / "clawtrader.log", encoding="utf-8"),
    ]
)
logger = logging.getLogger("clawtrader.daemon")

# ---------- 配置 ----------
def _load_config() -> dict:
    cfg_path = _SCRIPTS.parent / "config.json"
    if not cfg_path.exists():
        raise FileNotFoundError(
            f"配置文件未找到: {cfg_path}\n"
            "请复制 config.example.json → config.json 并填写账户信息。"
        )
    return json.loads(cfg_path.read_text(encoding="utf-8"))


# ====================================================================
#  条件单引擎
# ====================================================================

class ConditionEngine:
    """
    条件单列表，每条 Tick 时检查触发。

    条件结构：
    {
        "id": "c1",
        "instrument": "IF2505",
        "cond_type": "price_ge" | "price_le" | "pct_change_ge" | "pct_change_le",
        "threshold": 6000.0,
        "action": "alert" | "order",
        "order_params": {...},   # 仅 action==order 时
        "msg": "IF触及6000点",   # 仅 action==alert 时
        "triggered": false
    }
    """

    def __init__(self):
        self._conditions: dict[str, dict] = {}
        self._pre_close: dict[str, float] = {}

    def add(self, cond: dict) -> str:
        cid = cond.get("id") or f"c{int(time.time()*1000)}"
        cond["id"] = cid
        cond["triggered"] = False
        self._conditions[cid] = cond
        return cid

    def remove(self, cid: str) -> bool:
        return bool(self._conditions.pop(cid, None))

    def list_all(self) -> list:
        return list(self._conditions.values())

    def on_tick(self, tick: dict) -> list:
        """
        传入一条 Tick，返回触发的条件列表（每条只触发一次）。
        """
        inst  = tick.get("instrument", "")
        last  = tick.get("last", 0.0)
        pre_c = tick.get("pre_close", 0.0)
        if pre_c:
            self._pre_close[inst] = pre_c

        triggered = []
        for cid, cond in self._conditions.items():
            if cond["triggered"]:
                continue
            if cond["instrument"] != inst:
                continue

            ct  = cond["cond_type"]
            thr = cond["threshold"]
            hit = False

            if ct == "price_ge"      and last >= thr:
                hit = True
            elif ct == "price_le"    and last <= thr:
                hit = True
            elif ct == "pct_change_ge":
                base = self._pre_close.get(inst, 0)
                if base > 0 and (last - base) / base * 100 >= thr:
                    hit = True
            elif ct == "pct_change_le":
                base = self._pre_close.get(inst, 0)
                if base > 0 and (last - base) / base * 100 <= thr:
                    hit = True

            if hit:
                cond["triggered"] = True
                triggered.append(cond)

        return triggered


# ====================================================================
#  定时任务引擎（分钟级精度）
# ====================================================================

class ScheduleEngine:
    """
    定时任务，每天在指定时间触发一次。

    任务结构：
    {
        "id": "s1",
        "type": "order" | "login",
        "time": "09:25",           # HH:MM 本地时间
        "order_params": {...},     # type==order 时必填
        "triggered_date": ""       # 内部：已触发日期，防当天重复
    }
    """

    def __init__(self):
        self._schedules: dict[str, dict] = {}

    def add(self, sched: dict) -> str:
        sid = sched.get("id") or f"s{int(time.time()*1000)}"
        sched["id"] = sid
        sched.setdefault("triggered_date", "")
        self._schedules[sid] = sched
        return sid

    def remove(self, sid: str) -> bool:
        return bool(self._schedules.pop(sid, None))

    def list_all(self) -> list:
        return list(self._schedules.values())

    def check(self, now: datetime.datetime) -> list:
        """返回当前分钟应触发的任务列表（每天每个任务只触发一次）。"""
        cur_time = now.strftime("%H:%M")
        cur_date = now.strftime("%Y%m%d")
        fired = []
        for sched in self._schedules.values():
            if sched.get("time") != cur_time:
                continue
            if sched.get("triggered_date") == cur_date:
                continue
            sched["triggered_date"] = cur_date
            fired.append(sched)
        return fired


# ====================================================================
#  Pending 查询收集器（收集多条 is_last=false 然后汇总）
# ====================================================================

class QueryCollector:
    def __init__(self):
        self._buffers: dict[str, list] = {}   # qry_id → [rows]
        self._callbacks: dict[str, any] = {}  # qry_id → callback(rows)

    def start(self, qry_id: str, callback) -> None:
        self._buffers[qry_id]   = []
        self._callbacks[qry_id] = callback

    def feed(self, qry_id: str, row: dict) -> None:
        if qry_id not in self._buffers:
            return
        if row:
            self._buffers[qry_id].append(row)
        if row.get("is_last"):
            rows = self._buffers.pop(qry_id)
            cb   = self._callbacks.pop(qry_id)
            cb(rows)


# ====================================================================
#  Daemon 主体
# ====================================================================

class Daemon:
    DAEMON_PORT = 17777

    def __init__(self, cfg: dict):
        self.cfg     = cfg
        self._md     = MdGateway(
            front     = cfg["md_front"],
            flow_path = str(_SCRIPTS / "flow" / "md") + "/",
        )
        self._td     = TraderGateway(
            front     = cfg["td_front"],
            flow_path = str(_SCRIPTS / "flow" / "td") + "/",
        )
        self._cond   = ConditionEngine()
        self._sched  = ScheduleEngine()
        self._qcol   = QueryCollector()

        # 最新 Tick 缓存（instrument → tick dict）
        self._last_tick: dict[str, dict] = {}

        # 内存中的持仓 / 资金快照（由回调实时更新）
        self._positions:  dict[str, dict] = {}
        self._account:    dict            = {}
        self._active_orders: dict[str, dict] = {}   # order_ref → order
        self._today_trades:  list[dict]       = []

        self._running   = False
        self._event_log = []          # 发往 CLI 的待推送事件队列
        self._ev_lock   = threading.Lock()

        # 同步查询等待：socket 线程等待主循环回调完成
        # key: "position" | "account" | "orders" | "trades"
        # value: threading.Event
        self._qry_wait: dict[str, threading.Event] = {}
        self._qry_wait_lock = threading.Lock()
        # 查询结果临时缓冲（主循环写，socket 线程读）
        self._qry_buf_orders: list[dict] = []
        self._qry_buf_trades: list[dict] = []

        # 收盘日报定时标志
        self._reported_today = ""

    # ---------------------------------------------------------------- #
    #  事件推送队列（供 CLI 轮询）                                       #
    # ---------------------------------------------------------------- #

    def _push_event(self, evt: dict) -> None:
        with self._ev_lock:
            self._event_log.append(evt)
            if len(self._event_log) > 500:
                self._event_log.pop(0)

    def _drain_events(self) -> list:
        with self._ev_lock:
            evts = list(self._event_log)
            self._event_log.clear()
        return evts

    # ---------------------------------------------------------------- #
    #  CTP 事件处理                                                      #
    # ---------------------------------------------------------------- #

    def _handle_tick(self, tick: dict) -> None:
        inst = tick.get("instrument", "")

        # 缓存最新 Tick
        self._last_tick[inst] = tick

        # 条件单检查
        for cond in self._cond.on_tick(tick):
            if cond["action"] == "alert":
                msg = cond.get("msg") or f"{inst} 触发条件 {cond['cond_type']}={cond['threshold']}"
                logger.info("[告警] %s", msg)
                self._push_event({"type": "alert", "msg": msg, "tick": tick, "cond_id": cond["id"]})
            elif cond["action"] == "order":
                op = cond.get("order_params", {})
                ret, ref = self._td.send_order(**op)
                logger.info("[条件单触发] cond=%s ret=%d ref=%s", cond["id"], ret, ref)
                self._push_event({"type": "cond_order_sent", "cond_id": cond["id"],
                                  "order_ref": ref, "ret": ret})

    def _handle_order(self, order: dict) -> None:
        ref = order.get("order_ref", "")
        self._active_orders[ref] = order
        self._push_event({"type": "order", **order})
        logger.info("[委托] %s %s %s vol=%s/%s status=%s",
                    order.get("instrument"), order.get("direction"),
                    order.get("offset"), order.get("volume_traded"),
                    order.get("volume_total"), order.get("order_status"))

    def _handle_trade(self, trade: dict) -> None:
        self._today_trades.append(trade)
        self._push_event({"type": "trade", **trade})
        logger.info("[成交] %s %s %s price=%.4f vol=%d",
                    trade.get("instrument"), trade.get("direction"),
                    trade.get("offset"), trade.get("price", 0), trade.get("volume", 0))

    # ---------------------------------------------------------------- #
    #  Socket 命令处理                                                   #
    # ---------------------------------------------------------------- #

    def _handle_cmd(self, cmd: dict) -> dict:
        c = cmd.get("cmd", "")

        if c == "ping":
            return {"ok": True, "trading_day": self._td.get_trading_day()}

        elif c == "stop":
            self._running = False
            return {"ok": True}

        elif c == "subscribe":
            instruments = cmd.get("instruments", "")
            ret = self._md.subscribe(instruments)
            return {"ok": ret == 0, "ret": ret}

        elif c == "unsubscribe":
            instruments = cmd.get("instruments", "")
            ret = self._md.unsubscribe(instruments)
            return {"ok": ret == 0, "ret": ret}

        elif c == "order":
            if not self._td.settled:
                return {"ok": False, "error": "未就绪（结算确认未完成）"}
            ret, ref = self._td.send_order(
                exchange   = cmd["exchange"],
                instrument = cmd["instrument"],
                direction  = cmd["direction"],
                offset     = cmd["offset"],
                price_type = cmd.get("price_type", "limit"),
                price      = cmd.get("price", 0.0),
                volume     = cmd["volume"],
                time_cond  = cmd.get("time_cond", "gfd"),
                vol_cond   = cmd.get("vol_cond", "any"),
            )
            return {"ok": ret == 0, "order_ref": ref, "ret": ret}

        elif c == "cancel":
            ret = self._td.cancel_order(
                exchange     = cmd.get("exchange", ""),
                instrument   = cmd.get("instrument", ""),
                order_sys_id = cmd.get("order_sys_id", ""),
                order_ref    = cmd.get("order_ref", ""),
            )
            return {"ok": ret == 0, "ret": ret}

        elif c == "qry_position":
            inst = cmd.get("instrument", "")
            ev = threading.Event()
            with self._qry_wait_lock:
                self._positions = {}          # 清空旧快照，等交易所回填
                self._qry_wait["position"] = ev
            ret = self._td.qry_position(inst)
            if ret != 0:
                with self._qry_wait_lock:
                    self._qry_wait.pop("position", None)
                return {"ok": False, "error": f"qry_position ret={ret}（流控中，稍后重试）"}
            ev.wait(timeout=5.0)
            if inst:
                rows = [v for v in self._positions.values()
                        if v.get("instrument") == inst]
            else:
                rows = list(self._positions.values())
            return {"ok": True, "positions": rows}

        elif c == "qry_account":
            ev = threading.Event()
            with self._qry_wait_lock:
                self._qry_wait["account"] = ev
            ret = self._td.qry_account()
            if ret != 0:
                with self._qry_wait_lock:
                    self._qry_wait.pop("account", None)
                return {"ok": False, "error": f"qry_account ret={ret}（流控中，稍后重试）"}
            ev.wait(timeout=5.0)
            return {"ok": True, "account": self._account}

        elif c == "qry_orders":
            ev = threading.Event()
            with self._qry_wait_lock:
                self._qry_buf_orders = []
                self._qry_wait["orders"] = ev
            ret = self._td.qry_order(cmd.get("instrument", ""))
            if ret != 0:
                with self._qry_wait_lock:
                    self._qry_wait.pop("orders", None)
                return {"ok": False, "error": f"qry_order ret={ret}（流控中，稍后重试）"}
            ev.wait(timeout=5.0)
            return {"ok": True, "orders": list(self._qry_buf_orders)}

        elif c == "qry_trades":
            ev = threading.Event()
            with self._qry_wait_lock:
                self._qry_buf_trades = []
                self._qry_wait["trades"] = ev
            ret = self._td.qry_trade(cmd.get("instrument", ""))
            if ret != 0:
                with self._qry_wait_lock:
                    self._qry_wait.pop("trades", None)
                return {"ok": False, "error": f"qry_trade ret={ret}（流控中，稍后重试）"}
            ev.wait(timeout=5.0)
            return {"ok": True, "trades": list(self._qry_buf_trades)}

        elif c == "add_alert":
            cid = self._cond.add(cmd["condition"])
            return {"ok": True, "cond_id": cid}

        elif c == "remove_alert":
            ok = self._cond.remove(cmd["cond_id"])
            return {"ok": ok}

        elif c == "list_alerts":
            return {"ok": True, "conditions": self._cond.list_all()}

        elif c == "poll_events":
            return {"ok": True, "events": self._drain_events()}

        elif c == "report":
            self._refresh_for_report()   # 先向交易所刷新资金/持仓/成交
            return {"ok": True, "report": self._gen_report()}

        elif c == "qry_price":
            inst = cmd.get("instrument", "")
            tick = self._last_tick.get(inst)
            if tick:
                return {"ok": True, "tick": tick}
            return {"ok": False, "error": f"暂无 {inst} 行情，请先订阅"}

        elif c == "cancel_all":
            cancelled, failed = 0, 0
            for ref, order in list(self._active_orders.items()):
                status = order.get("order_status", "")
                # 只撤未成交/部分成交的委托
                if status in ("AllTraded", "Canceled"):
                    continue
                ret = self._td.cancel_order(
                    exchange     = order.get("exchange", ""),
                    instrument   = order.get("instrument", ""),
                    order_sys_id = order.get("order_sys_id", ""),
                    order_ref    = ref,
                )
                if ret == 0:
                    cancelled += 1
                else:
                    failed += 1
            return {"ok": True, "cancelled": cancelled, "failed": failed}

        elif c == "add_schedule":
            sid = self._sched.add(cmd["schedule"])
            return {"ok": True, "schedule_id": sid}

        elif c == "list_schedules":
            return {"ok": True, "schedules": self._sched.list_all()}

        elif c == "remove_schedule":
            ok = self._sched.remove(cmd["schedule_id"])
            return {"ok": ok}

        else:
            return {"ok": False, "error": f"未知指令: {c}"}

    def _refresh_for_report(self) -> None:
        """依次向 CTP 查询资金→持仓→成交，等待回调后更新本地缓存。
        必须在非主循环线程中调用（socket 线程或独立线程）。
        三次查询每次间隔 1.1 秒（trader_gateway._wait_qry 强制）。
        """
        # 查资金
        ev = threading.Event()
        with self._qry_wait_lock:
            self._qry_wait["account"] = ev
        if self._td.qry_account() == 0:
            ev.wait(timeout=5.0)

        # 查持仓
        ev = threading.Event()
        with self._qry_wait_lock:
            self._positions = {}
            self._qry_wait["position"] = ev
        if self._td.qry_position("") == 0:
            ev.wait(timeout=5.0)

        # 查成交，结果回填 _today_trades（与 OnRtnTrade 缓存保持一致）
        ev = threading.Event()
        with self._qry_wait_lock:
            self._qry_buf_trades = []
            self._qry_wait["trades"] = ev
        if self._td.qry_trade("") == 0:
            ev.wait(timeout=5.0)
            with self._qry_wait_lock:
                self._today_trades = list(self._qry_buf_trades)

    def _gen_report(self) -> dict:
        """根据当前本地缓存生成日报 dict（调用前请先 _refresh_for_report）。"""
        return {
            "trading_day": self._td.get_trading_day(),
            "account":     self._account,
            "positions":   list(self._positions.values()),
            "trades":      list(self._today_trades),
        }

    # ---------------------------------------------------------------- #
    #  Socket 服务线程                                                   #
    # ---------------------------------------------------------------- #

    def _socket_server(self, port: int) -> None:
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("127.0.0.1", port))
        srv.listen(5)
        srv.settimeout(1.0)
        logger.info("命令监听端口: %d", port)

        while self._running:
            try:
                conn, _ = srv.accept()
            except socket.timeout:
                continue
            threading.Thread(target=self._handle_conn,
                             args=(conn,), daemon=True).start()
        srv.close()

    def _handle_conn(self, conn: socket.socket) -> None:
        try:
            data = b""
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b"\n" in data:
                    break
            cmd = json.loads(data.decode())
            resp = self._handle_cmd(cmd)
            conn.sendall((json.dumps(resp, ensure_ascii=False) + "\n").encode())
        except Exception as e:
            try:
                conn.sendall((json.dumps({"ok": False, "error": str(e)}) + "\n").encode())
            except Exception:
                pass
        finally:
            conn.close()

    # ---------------------------------------------------------------- #
    #  收盘日报定时触发                                                   #
    # ---------------------------------------------------------------- #

    def _check_daily_report(self) -> None:
        now = datetime.datetime.now()
        trading_day = self._td.get_trading_day() or now.strftime("%Y%m%d")

        # 15:20 之后触发，每个交易日只触发一次
        if now.hour == 15 and now.minute >= 20:
            if self._reported_today != trading_day:
                self._reported_today = trading_day  # 先标记，防止主循环重复触发
                def _async_report(td_str):
                    self._refresh_for_report()
                    report = self._gen_report()
                    self._push_event({"type": "daily_report", "report": report})
                    logger.info("[日报] 收盘日报已生成，交易日 %s", td_str)
                threading.Thread(target=_async_report, args=(trading_day,),
                                 daemon=True).start()

    # ---------------------------------------------------------------- #
    #  定时任务检查                                                       #
    # ---------------------------------------------------------------- #

    def _check_schedules(self) -> None:
        now = datetime.datetime.now()
        for sched in self._sched.check(now):
            stype = sched.get("type", "")
            sid   = sched["id"]
            if stype == "order":
                op = sched.get("order_params", {})
                if not self._td.settled:
                    logger.warning("[定时单] %s 跳过：交易网关未就绪", sid)
                    self._push_event({"type": "schedule_skip", "schedule_id": sid,
                                      "reason": "交易网关未就绪"})
                    continue
                ret, ref = self._td.send_order(**op)
                logger.info("[定时单] %s 已触发，ret=%d ref=%s", sid, ret, ref)
                self._push_event({"type": "schedule_order_sent", "schedule_id": sid,
                                  "order_ref": ref, "ret": ret})
            elif stype == "login":
                logger.info("[定时登录] %s 触发，重新连接", sid)
                cfg = self.cfg
                self._td.connect(
                    broker_id = cfg["broker_id"],
                    user_id   = cfg["user_id"],
                    password  = cfg["td_password"],
                    app_id    = cfg["app_id"],
                    auth_code = cfg["auth_code"],
                )
                self._push_event({"type": "schedule_login", "schedule_id": sid})

    # ---------------------------------------------------------------- #
    #  主循环                                                            #
    # ---------------------------------------------------------------- #

    def run(self) -> None:
        cfg = self.cfg

        # 启动 MD
        self._md.connect(cfg["broker_id"], cfg["user_id"], cfg["md_password"])

        # 启动 TD
        self._td.connect(
            broker_id = cfg["broker_id"],
            user_id   = cfg["user_id"],
            password  = cfg["td_password"],
            app_id    = cfg["app_id"],
            auth_code = cfg["auth_code"],
        )

        # 写 state 文件
        self._running = True
        port = cfg.get("daemon_port", self.DAEMON_PORT)
        state.write({"port": port, "pid": os.getpid()})

        # 启动 socket 服务
        sock_thread = threading.Thread(target=self._socket_server,
                                       args=(port,), daemon=True)
        sock_thread.start()

        logger.info("ClawTrader daemon 已启动 (PID=%d)", os.getpid())

        # 初始订阅
        subscribed = set()
        default_instruments = cfg.get("default_instruments", "")

        # ---- 事件主循环 ----
        while self._running:
            # 处理行情事件
            for _ in range(10):     # 每轮最多消费 10 条 MD 事件
                evt, data = self._md.poll_one(timeout_ms=0)
                if evt == 0:
                    break
                if evt == 101 and default_instruments:  # MD_FRONT_CONNECTED 后订阅
                    pass
                elif evt == 103:    # MD_RSP_LOGIN
                    if data.get("error_id", 0) == 0 and default_instruments:
                        self._md.subscribe(default_instruments)
                        for inst in default_instruments.split(","):
                            subscribed.add(inst.strip())
                        logger.info("已订阅默认合约: %s", default_instruments)
                elif evt == EVT_MD_TICK:
                    self._handle_tick(data)

            # 处理交易事件
            for _ in range(20):
                evt, data = self._td.poll_one(timeout_ms=0)
                if evt == 0:
                    break
                if evt == EVT_RTN_ORDER:
                    self._handle_order(data)
                elif evt == EVT_RTN_TRADE:
                    self._handle_trade(data)
                elif evt == EVT_RSP_QRY_POSITION:
                    inst = data.get("instrument", "")
                    if inst:
                        key = f"{inst}_{data.get('direction','')}"
                        self._positions[key] = data
                    if data.get("is_last"):
                        with self._qry_wait_lock:
                            ev = self._qry_wait.pop("position", None)
                        if ev:
                            ev.set()
                elif evt == EVT_RSP_QRY_ACCOUNT:
                    self._account = data
                    with self._qry_wait_lock:
                        ev = self._qry_wait.pop("account", None)
                    if ev:
                        ev.set()
                elif evt == EVT_RSP_QRY_ORDER:
                    if data.get("order_ref") or data.get("instrument"):
                        with self._qry_wait_lock:
                            self._qry_buf_orders.append(data)
                    if data.get("is_last"):
                        with self._qry_wait_lock:
                            ev = self._qry_wait.pop("orders", None)
                        if ev:
                            ev.set()
                elif evt == EVT_RSP_QRY_TRADE:
                    if data.get("trade_id") or data.get("instrument"):
                        with self._qry_wait_lock:
                            self._qry_buf_trades.append(data)
                    if data.get("is_last"):
                        with self._qry_wait_lock:
                            ev = self._qry_wait.pop("trades", None)
                        if ev:
                            ev.set()
                elif evt == EVT_RSP_ERROR:
                    logger.error("[CTP错误] %s", data)
                    self._push_event({"type": "error", **data})

            # 收盘日报检查
            self._check_daily_report()

            # 定时任务检查
            self._check_schedules()

            time.sleep(0.005)   # 避免空转吃 CPU

        # 退出清理
        logger.info("daemon 正在退出...")
        self._md.release()
        self._td.release()
        state.clear()
        logger.info("daemon 已退出")


# ====================================================================
#  入口
# ====================================================================

def main():
    cfg = _load_config()

    daemon = Daemon(cfg)

    def _sig_handler(signum, frame):
        logger.info("收到信号 %d，停止 daemon", signum)
        daemon._running = False

    signal.signal(signal.SIGINT,  _sig_handler)
    signal.signal(signal.SIGTERM, _sig_handler)

    daemon.run()


if __name__ == "__main__":
    main()
