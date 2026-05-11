"""
Sandbox — 安全的 Python 代码执行环境

用于执行 YAML 中 code 节点的内联 Python 代码。
提供受限的内置函数，可读写 Context 变量。
"""

import io
import sys
import json
import traceback
from typing import Any, Dict, Optional


# 允许在沙箱中使用的内置函数白名单
SAFE_BUILTINS = {
    # 类型转换
    "str": str, "int": int, "float": float, "bool": bool,
    "list": list, "dict": dict, "tuple": tuple, "set": set,
    "bytes": bytes, "bytearray": bytearray,
    # 序列操作
    "len": len, "range": range, "enumerate": enumerate, "zip": zip,
    "map": map, "filter": filter, "sorted": sorted, "reversed": reversed,
    "sum": sum, "min": min, "max": max, "abs": abs, "round": round,
    "all": all, "any": any,
    # 字符串
    "repr": repr, "format": format, "chr": chr, "ord": ord,
    # 容器
    "isinstance": isinstance, "type": type, "hasattr": hasattr, "getattr": getattr,
    # IO
    "open": open, "id": id,
    # 常量
    "True": True, "False": False, "None": None,
    # 异常
    "Exception": Exception, "ValueError": ValueError, "TypeError": TypeError,
    "KeyError": KeyError, "IndexError": IndexError, "AttributeError": AttributeError,
    "FileNotFoundError": FileNotFoundError, "IOError": IOError,
    "NameError": NameError, "RuntimeError": RuntimeError,
    # 其他
    "print": print,  # 会被重定向
}

# 允许 import 的安全模块
ALLOWED_MODULES = {
    "json", "re", "math", "datetime", "time", "collections",
    "itertools", "functools", "string", "textwrap", "hashlib",
    "base64", "urllib.parse", "pathlib", "csv", "io",
}


def _safe_import(name: str, *args, **kwargs):
    """受限的 import 函数"""
    if name.split('.')[0] not in ALLOWED_MODULES:
        raise ImportError(f"模块 '{name}' 不允许在沙箱中导入。允许: {', '.join(sorted(ALLOWED_MODULES))}")
    return __builtins__.__import__(name, *args, **kwargs) if hasattr(__builtins__, '__import__') else __import__(name, *args, **kwargs)


class SandboxResult:
    """沙箱执行结果"""

    def __init__(self, success: bool, output: str = "", result: Any = None, error: str = ""):
        self.success = success
        self.output = output    # stdout 捕获
        self.result = result    # 最后一个表达式的值 或 ctx_export
        self.error = error      # 异常信息

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "result": self.result,
            "error": self.error,
        }


def execute_code(
    code: str,
    variables: Optional[Dict[str, Any]] = None,
    timeout: int = 30,
) -> SandboxResult:
    """
    在沙箱中执行 Python 代码。

    参数:
        code:      要执行的 Python 代码
        variables: 注入的变量 (可在代码中直接使用)
        timeout:   超时秒数 (预留，当前未强制)

    返回:
        SandboxResult

    代码中可使用:
        - ctx_export(value)   → 将值导出为步骤输出
        - 所有注入的 variables 变量
        - SAFE_BUILTINS 中的内置函数
        - ALLOWED_MODULES 中的模块
    """
    variables = variables or {}

    # 捕获 stdout
    captured = io.StringIO()
    export_box: list = []  # 用 list 包装以允许闭包修改

    def ctx_export(value: Any):
        """在沙箱代码中调用此函数导出结果"""
        export_box.append(value)

    # 构建执行命名空间
    namespace: Dict[str, Any] = dict(variables)
    namespace["ctx_export"] = ctx_export
    namespace["__builtins__"] = dict(SAFE_BUILTINS)
    namespace["__builtins__"]["__import__"] = _safe_import

    old_stdout = sys.stdout
    try:
        sys.stdout = captured
        exec(compile(code, "<openclaw-workflow-sandbox>", "exec"), namespace)
        sys.stdout = old_stdout

        # 优先使用 ctx_export() 的值，其次检查 namespace 中的 result 变量
        if export_box:
            result = export_box[-1]
        elif "result" in namespace and namespace["result"] is not None:
            result = namespace["result"]
        else:
            result = None
        return SandboxResult(
            success=True,
            output=captured.getvalue(),
            result=result,
        )
    except Exception as e:
        sys.stdout = old_stdout
        return SandboxResult(
            success=False,
            output=captured.getvalue(),
            error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}",
        )
