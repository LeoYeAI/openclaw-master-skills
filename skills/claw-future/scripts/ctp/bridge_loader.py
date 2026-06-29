"""
bridge_loader.py

ctypes 加载 ctp_bridge 动态库，声明所有导出函数的签名。
支持平台：Windows x64 / macOS / Linux x64

库文件名（均位于 scripts/ 目录下）：
  Windows : ctp_bridge.dll
  macOS   : libctp_bridge.dylib
  Linux   : libctp_bridge.so

首次运行时若库文件不存在，会自动检测平台并调用对应编译脚本。
"""

import ctypes
import os
import platform
import subprocess
import sys
from pathlib import Path

# scripts/ 目录（bridge_loader.py 的上一级）
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
_BRIDGE_DIR  = _SCRIPTS_DIR / "bridge"

_SYSTEM = platform.system()


def _get_lib_path() -> Path:
    if _SYSTEM == "Windows":
        return _SCRIPTS_DIR / "ctp_bridge.dll"
    elif _SYSTEM == "Darwin":
        return _SCRIPTS_DIR / "libctp_bridge.dylib"
    elif _SYSTEM == "Linux":
        return _SCRIPTS_DIR / "libctp_bridge.so"
    else:
        raise RuntimeError(f"不支持的平台: {_SYSTEM}")


_LIB_PATH = _get_lib_path()


def _build_cmd() -> list:
    """返回当前平台对应的编译命令。"""
    if _SYSTEM == "Windows":
        script = _BRIDGE_DIR / "build_windows.py"
        return [sys.executable, str(script)]
    elif _SYSTEM == "Darwin":
        script = _BRIDGE_DIR / "build_macos.sh"
        return ["bash", str(script)]
    elif _SYSTEM == "Linux":
        script = _BRIDGE_DIR / "build_linux.sh"
        return ["bash", str(script)]
    else:
        raise RuntimeError(f"不支持的平台: {_SYSTEM}")


def auto_build(force: bool = False) -> None:
    """
    自动编译 ctp_bridge。

    Parameters
    ----------
    force : 若为 True 则即使库文件已存在也重新编译（用于 setup 命令）。
    """
    if not force and _LIB_PATH.exists():
        return

    cmd = _build_cmd()
    script_path = Path(cmd[-1])
    if not script_path.exists():
        raise FileNotFoundError(
            f"编译脚本未找到: {script_path}\n"
            "请确认项目目录结构完整。"
        )

    tag = "重新编译" if force else "首次运行，自动编译"
    print(f"[ClawTrader] {tag} ctp_bridge ({_SYSTEM})...", flush=True)

    # macOS/Linux: 脚本可能因 Windows 编辑器带来 CRLF，在此原地清除
    if _SYSTEM in ("Darwin", "Linux"):
        raw = script_path.read_bytes()
        if b"\r\n" in raw:
            script_path.write_bytes(raw.replace(b"\r\n", b"\n"))

    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError(
            f"ctp_bridge 编译失败（exit={result.returncode}）。\n"
            "请确认：\n"
            "  • 已安装编译工具\n"
            "    Windows : Visual Studio 2019+（含 C++ 工具集）\n"
            "    macOS   : Xcode Command Line Tools（clang++）\n"
            "    Linux   : build-essential（g++）\n"
            "  • api/ 目录已放置对应平台的 CTP SDK（参见 api/VERSIONS.md）"
        )
    if not _LIB_PATH.exists():
        raise RuntimeError(
            f"编译脚本执行成功但库文件仍未出现: {_LIB_PATH}\n"
            "请检查编译输出。"
        )
    print(f"[ClawTrader] 编译完成 → {_LIB_PATH.name}", flush=True)


def _load() -> ctypes.CDLL:
    # 库不存在时自动编译
    if not _LIB_PATH.exists():
        auto_build()

    if _SYSTEM == "Windows":
        # Windows 需要显式告知 DLL 搜索目录（CTP DLL 与 bridge DLL 同目录）
        os.add_dll_directory(str(_SCRIPTS_DIR))
    return ctypes.CDLL(str(_LIB_PATH))


_lib = _load()

c_void_p = ctypes.c_void_p
c_int    = ctypes.c_int
c_double = ctypes.c_double
c_char_p = ctypes.c_char_p
c_char   = ctypes.c_char


def _fn(name, restype, *argtypes):
    f = getattr(_lib, name)
    f.restype  = restype
    f.argtypes = list(argtypes)
    return f


# ------------------------------------------------------------------ #
#  Market Data API                                                     #
# ------------------------------------------------------------------ #
md_create          = _fn("md_create",          c_void_p, c_char_p)
md_release         = _fn("md_release",         None,     c_void_p)
md_register_front  = _fn("md_register_front",  None,     c_void_p, c_char_p)
md_init            = _fn("md_init",            None,     c_void_p)
md_login           = _fn("md_login",           c_int,    c_void_p, c_char_p, c_char_p, c_char_p, c_int)
md_subscribe       = _fn("md_subscribe",       c_int,    c_void_p, c_char_p)
md_unsubscribe     = _fn("md_unsubscribe",     c_int,    c_void_p, c_char_p)
md_poll            = _fn("md_poll",            c_int,    c_void_p, ctypes.c_char_p, c_int, c_int)
md_get_trading_day = _fn("md_get_trading_day", c_char_p, c_void_p)
md_get_api_version = _fn("md_get_api_version", c_char_p)

# ------------------------------------------------------------------ #
#  Trader API                                                          #
# ------------------------------------------------------------------ #
td_create          = _fn("td_create",          c_void_p, c_char_p)
td_release         = _fn("td_release",         None,     c_void_p)
td_register_front  = _fn("td_register_front",  None,     c_void_p, c_char_p)
td_init            = _fn("td_init",            None,     c_void_p)
td_authenticate    = _fn("td_authenticate",    c_int,    c_void_p,
                          c_char_p, c_char_p, c_char_p, c_char_p, c_int)
td_login           = _fn("td_login",           c_int,    c_void_p,
                          c_char_p, c_char_p, c_char_p, c_int)
td_settle_confirm  = _fn("td_settle_confirm",  c_int,    c_void_p,
                          c_char_p, c_char_p, c_int)
td_order_insert    = _fn("td_order_insert",    c_int,    c_void_p,
                          c_char_p, c_char_p, c_char_p, c_char_p, c_char_p,
                          c_char,   c_char,   c_char,
                          c_double, c_int,    c_char,   c_char,   c_int)
td_cancel_by_sysid = _fn("td_order_cancel_by_sysid", c_int, c_void_p,
                          c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int)
td_cancel_by_ref   = _fn("td_order_cancel_by_ref",   c_int, c_void_p,
                          c_char_p, c_char_p, c_char_p, c_char_p, c_char_p,
                          c_int, c_int, c_int)
td_qry_position    = _fn("td_qry_position",    c_int,    c_void_p,
                          c_char_p, c_char_p, c_char_p, c_int)
td_qry_account     = _fn("td_qry_account",     c_int,    c_void_p,
                          c_char_p, c_char_p, c_int)
td_qry_order       = _fn("td_qry_order",       c_int,    c_void_p,
                          c_char_p, c_char_p, c_char_p, c_int)
td_qry_trade       = _fn("td_qry_trade",       c_int,    c_void_p,
                          c_char_p, c_char_p, c_char_p, c_int)
td_poll            = _fn("td_poll",            c_int,    c_void_p,
                          ctypes.c_char_p, c_int, c_int)
td_get_front_id    = _fn("td_get_front_id",    c_int,    c_void_p)
td_get_session_id  = _fn("td_get_session_id",  c_int,    c_void_p)
td_get_trading_day = _fn("td_get_trading_day", c_char_p, c_void_p)


def b(s: str) -> bytes:
    """str → bytes（UTF-8，适用于 ASCII CTP 字段）"""
    return s.encode() if isinstance(s, str) else s
