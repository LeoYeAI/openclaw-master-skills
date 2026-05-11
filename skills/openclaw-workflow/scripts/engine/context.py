"""
Context Manager — 全局上下文变量管道

负责在节点间传递数据，支持:
- 全局变量
- 步骤输出引用 ({{step_id.output}})
- 循环局部作用域
- 环境变量 ({{env.VAR}})
- 嵌套字段访问 ({{step.output.field.subfield}})
"""

import os
import re
import copy
import json
from typing import Any, Dict, Optional


class Context:
    """工作流执行上下文 — 管理变量、步骤输出和作用域"""

    def __init__(self, variables: Optional[Dict[str, Any]] = None):
        self._globals: Dict[str, Any] = dict(variables or {})
        self._step_outputs: Dict[str, Any] = {}
        self._scopes: list[Dict[str, Any]] = []  # 局部作用域栈

    # ── 变量操作 ──────────────────────────────────────────

    def set(self, key: str, value: Any) -> None:
        """设置全局变量"""
        if self._scopes:
            self._scopes[-1][key] = value
        else:
            self._globals[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """获取变量，优先从局部作用域查找"""
        # 从内到外搜索作用域
        for scope in reversed(self._scopes):
            if key in scope:
                return scope[key]
        return self._globals.get(key, default)

    def set_global(self, key: str, value: Any) -> None:
        """强制设置全局变量"""
        self._globals[key] = value

    # ── 步骤输出 ──────────────────────────────────────────

    def set_output(self, step_id: str, output: Any) -> None:
        """保存步骤输出"""
        self._step_outputs[step_id] = output

    def get_output(self, step_id: str) -> Any:
        """获取步骤输出"""
        return self._step_outputs.get(step_id)

    # ── 作用域管理 (用于循环) ─────────────────────────────

    def push_scope(self, initial: Optional[Dict[str, Any]] = None) -> None:
        """创建新的局部作用域"""
        self._scopes.append(dict(initial or {}))

    def pop_scope(self) -> Dict[str, Any]:
        """弹出当前局部作用域"""
        if self._scopes:
            return self._scopes.pop()
        return {}

    def create_child_context(self, scope_vars: Optional[Dict[str, Any]] = None) -> "Context":
        """
        创建子上下文 (用于并行循环)。

        共享 _globals 和 _step_outputs 引用 (Python GIL 保证 dict/list 原子操作安全),
        拥有独立的 _scopes 栈，互不干扰。
        """
        child = Context.__new__(Context)
        child._globals = self._globals          # 共享引用
        child._step_outputs = self._step_outputs  # 共享引用
        child._scopes = [dict(scope_vars or {})]  # 独立作用域栈
        return child

    # ── 模板插值 ──────────────────────────────────────────

    def resolve(self, text: Any) -> Any:
        """
        递归解析模板中的 {{...}} 占位符。

        支持:
          {{var}}                  → 全局/局部变量
          {{step_id.output}}      → 步骤输出
          {{step_id.output.key}}  → 步骤输出的嵌套字段
          {{env.HOME}}            → 环境变量
          {{item}}                → 循环当前元素 (局部)
          {{item.field}}          → 循环元素字段
        """
        if text is None:
            return None

        # 对 dict 和 list 递归处理
        if isinstance(text, dict):
            return {k: self.resolve(v) for k, v in text.items()}
        if isinstance(text, list):
            return [self.resolve(item) for item in text]

        # 非字符串直接返回
        if not isinstance(text, str):
            return text

        # 如果整个字符串就是一个占位符, 保留原始类型
        single_match = re.fullmatch(r'\{\{\s*(.+?)\s*\}\}', text)
        if single_match:
            resolved = self._resolve_path(single_match.group(1))
            if resolved is not None:
                return resolved

        # 多个占位符或混合文本 → 全部替换为字符串
        def _replacer(m: re.Match) -> str:
            path = m.group(1).strip()
            val = self._resolve_path(path)
            if val is None:
                return m.group(0)  # 保留未解析的占位符
            if isinstance(val, (dict, list)):
                return json.dumps(val, ensure_ascii=False)
            return str(val)

        return re.sub(r'\{\{\s*(.+?)\s*\}\}', _replacer, text)

    def _resolve_path(self, path: str) -> Any:
        """解析一个点分路径"""
        parts = path.split('.')

        # 1. 环境变量: env.VAR
        if parts[0] == 'env' and len(parts) >= 2:
            return os.environ.get(parts[1])

        # 2. 步骤输出: step_id / step_id.output / step_id.output.field
        if parts[0] in self._step_outputs:
            obj = self._step_outputs[parts[0]]
            rest = parts[1:]
            # 兼容 {{step_id.output}} 和 {{step_id.output.field}} 写法
            # "output" 是虚拟前缀，跳过它直接访问值
            if rest and rest[0] == 'output':
                rest = rest[1:]
            return self._drill(obj, rest)

        # 3. 局部/全局变量
        val = self.get(parts[0])
        if val is not None:
            return self._drill(val, parts[1:])

        return None

    @staticmethod
    def _drill(obj: Any, keys: list[str]) -> Any:
        """沿着 keys 路径深入对象"""
        for k in keys:
            if obj is None:
                return None
            if isinstance(obj, dict):
                obj = obj.get(k)
            elif isinstance(obj, list):
                try:
                    obj = obj[int(k)]
                except (ValueError, IndexError):
                    return None
            elif hasattr(obj, k):
                obj = getattr(obj, k)
            else:
                return None
        return obj

    # ── 条件评估 ──────────────────────────────────────────

    def eval_condition(self, expr: str) -> bool:
        """
        安全地评估条件表达式。
        先做模板插值，再用受限环境求值。
        """
        resolved = self.resolve(expr)
        if isinstance(resolved, bool):
            return resolved

        resolved_str = str(resolved)

        # 构建安全的变量命名空间
        namespace: Dict[str, Any] = {}
        namespace.update(self._globals)
        for scope in self._scopes:
            namespace.update(scope)
        for k, v in self._step_outputs.items():
            namespace[k] = v

        safe_builtins = {
            "len": len, "str": str, "int": int, "float": float,
            "bool": bool, "list": list, "dict": dict,
            "range": range, "sum": sum, "min": min, "max": max,
            "abs": abs, "True": True, "False": False, "None": None,
            "isinstance": isinstance, "type": type,
        }

        try:
            return bool(eval(resolved_str, {"__builtins__": safe_builtins}, namespace))
        except Exception:
            return False

    # ── 快照 (用于断点恢复) ───────────────────────────────

    def snapshot(self) -> Dict[str, Any]:
        """导出可序列化的上下文快照"""
        return {
            "globals": copy.deepcopy(self._globals),
            "step_outputs": copy.deepcopy(self._step_outputs),
            "scopes": copy.deepcopy(self._scopes),
        }

    def restore(self, snap: Dict[str, Any]) -> None:
        """从快照恢复上下文"""
        self._globals = snap.get("globals", {})
        self._step_outputs = snap.get("step_outputs", {})
        self._scopes = snap.get("scopes", [])

    # ── 调试 ──────────────────────────────────────────────

    def dump(self) -> Dict[str, Any]:
        """返回当前所有变量 (用于调试)"""
        merged = dict(self._globals)
        for scope in self._scopes:
            merged.update(scope)
        return {
            "variables": merged,
            "step_outputs": dict(self._step_outputs),
        }
