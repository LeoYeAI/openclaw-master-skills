import importlib.machinery
import importlib.util
import os
import sys
import traceback
from datetime import date, datetime
from importlib import reload
from typing import Any

from pythongo.infini import write_log

qt_origin_path = os.path.join(
    sys.base_prefix, "Lib", "site-packages", "PyQt5", "Qt5", "plugins"
)

if os.path.exists(qt_origin_path):
    #: 正确设置 QT 路径
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = qt_origin_path


def import_strategy(path: str) -> tuple[str, object | None]:
    """
    导入 Python 策略

    Args:
        path: 策略文件路径
    """

    try:
        file_name: str = os.path.basename(path)
        strategy_name = os.path.splitext(file_name)[0]

        # 按后缀名长度排序，优先匹配最长的后缀，让 .py 优先级最低
        suffixes = sorted(importlib.machinery.all_suffixes(), key=len, reverse=True)

        for suffix in suffixes:
            if file_name.endswith(suffix):
                strategy_name = file_name.removesuffix(suffix)
                break

        spec = importlib.util.spec_from_file_location(strategy_name, path)
        if spec is None or spec.loader is None:
            # path 错误的情况
            return f"无法识别或加载文件: {file_name}", None

        module = importlib.util.module_from_spec(spec)
        sys.modules[strategy_name] = module
        spec.loader.exec_module(module)

        if hasattr(module, strategy_name):
            return "", getattr(module, strategy_name)

        return f"策略文件 {file_name} 中没有 {strategy_name} 类, 请检查", None
    except:
        return traceback.format_exc(), None


def reload_strategy() -> None:
    """重载策略"""
    ignore_modules = {
        "pythongo.ui",
        "pythongo.ui.crosshair",
        "pythongo.ui.drawer",
        "pythongo.ui.widget"
    }

    modules_to_reload = [
        name for name in sys.modules.keys()
        if name.startswith("pythongo") and name not in ignore_modules
    ]

    for name in modules_to_reload:
        module = sys.modules.get(name)
        if module is not None:
            reload(module)


def safe_datetime(time_str: str) -> datetime:
    """无限易使用此函数将时间字符串转为 datetime 对象"""
    __format = "%Y%m%d %H:%M:%S.%f"

    if all(time_str.split(" ")):
        return datetime.strptime(time_str, __format)

    _today = date.today().strftime("%Y%m%d")

    return datetime.strptime(f"{_today}{time_str}", __format)


def safe_call(py_func, py_args=()) -> Any | None:
    """
    无限易安全调用函数

    Args:
        py_func: `on_stop()`, `on_init()` 等各种方法的对象
        py_args: 参数
    """

    try:
        return py_func(*py_args)
    except:
        write_log(traceback.format_exc())
