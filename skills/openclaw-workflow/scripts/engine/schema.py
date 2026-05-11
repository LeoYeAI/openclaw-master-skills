"""
Schema — 工作流 YAML Schema 验证

验证工作流定义的正确性，并提供友好的错误提示。
"""

from typing import Any, Dict, List, Optional, Tuple

# 有效的节点类型
VALID_NODE_TYPES = {
    "script", "llm", "skill", "condition", "loop", "wait",
    "set", "log", "http", "code", "agent", "subagent", "message",
    "wait_subagents",
}

# 每种节点类型的必需字段
NODE_REQUIRED_FIELDS = {
    "script": [],       # command / script / file 任一即可
    "llm": ["prompt"],
    "skill": ["action"],
    "condition": ["if"],
    "loop": [],         # foreach 或 times 任一即可
    "wait": [],         # seconds 或 until 任一即可
    "set": ["var", "value"],
    "log": ["message"],
    "http": ["url"],
    "code": ["python"],
    "agent": ["message"],
    "subagent": ["task"],
    "message": ["target"],
    "wait_subagents": ["tracker"],
}

# 有效的 on_error 策略
VALID_ERROR_STRATEGIES = {"retry", "ask", "stop", "skip"}


class ValidationError:
    """单个验证错误"""

    def __init__(self, path: str, message: str, severity: str = "error"):
        self.path = path
        self.message = message
        self.severity = severity  # error | warning

    def __str__(self):
        icon = "❌" if self.severity == "error" else "⚠️"
        return f"{icon} [{self.path}] {self.message}"


def validate_workflow(data: Any) -> Tuple[bool, List[ValidationError]]:
    """
    验证工作流定义。

    返回 (is_valid, errors)
    """
    errors: List[ValidationError] = []

    if not isinstance(data, dict):
        errors.append(ValidationError("root", "工作流必须是一个 YAML 映射 (dict)"))
        return False, errors

    # 检查必需的顶层字段
    if "steps" not in data:
        errors.append(ValidationError("root", "缺少 'steps' 字段"))

    # flow_id 推荐但不强制
    if "flow_id" not in data and "name" not in data:
        errors.append(ValidationError("root", "建议设置 'flow_id' 或 'name'", "warning"))

    # 验证 settings
    settings = data.get("settings", {})
    if isinstance(settings, dict):
        on_error = settings.get("on_error")
        if on_error and on_error not in VALID_ERROR_STRATEGIES:
            errors.append(ValidationError(
                "settings.on_error",
                f"无效的 on_error 策略: '{on_error}'。有效值: {VALID_ERROR_STRATEGIES}"
            ))

    # 验证 variables
    variables = data.get("variables", {})
    if variables and not isinstance(variables, dict):
        errors.append(ValidationError("variables", "variables 必须是一个映射"))

    # 验证 steps
    steps = data.get("steps", [])
    if not isinstance(steps, list):
        errors.append(ValidationError("steps", "steps 必须是一个列表"))
    else:
        seen_ids = set()
        for i, step in enumerate(steps):
            step_path = f"steps[{i}]"
            _validate_step(step, step_path, seen_ids, errors)

    has_errors = any(e.severity == "error" for e in errors)
    return not has_errors, errors


def _validate_step(step: Any, path: str, seen_ids: set, errors: List[ValidationError]):
    """验证单个步骤"""
    if not isinstance(step, dict):
        errors.append(ValidationError(path, "步骤必须是一个映射"))
        return

    # id 唯一性
    step_id = step.get("id")
    if step_id:
        if step_id in seen_ids:
            errors.append(ValidationError(f"{path}.id", f"重复的步骤 ID: '{step_id}'"))
        seen_ids.add(step_id)

    # type 有效性
    node_type = step.get("type")
    if not node_type:
        errors.append(ValidationError(path, "步骤缺少 'type' 字段"))
        return

    if node_type not in VALID_NODE_TYPES:
        errors.append(ValidationError(
            f"{path}.type",
            f"未知的节点类型: '{node_type}'。有效类型: {sorted(VALID_NODE_TYPES)}"
        ))
        return

    # 必需字段
    required = NODE_REQUIRED_FIELDS.get(node_type, [])
    for field in required:
        if field not in step:
            errors.append(ValidationError(f"{path}.{field}", f"'{node_type}' 类型节点必须包含 '{field}' 字段"))

    # 类型特定验证
    if node_type == "script":
        if not any(k in step for k in ("command", "script", "file", "inline")):
            errors.append(ValidationError(path, "script 节点需要 command / script / file / inline 中至少一个"))

    elif node_type == "loop":
        if "foreach" not in step and "times" not in step:
            errors.append(ValidationError(path, "loop 节点需要 foreach 或 times"))
        if "do" not in step and "steps" not in step:
            errors.append(ValidationError(path, "loop 节点需要 do 或 steps 子步骤"))

    elif node_type == "wait":
        if "seconds" not in step and "until" not in step:
            errors.append(ValidationError(path, "wait 节点需要 seconds 或 until"))

    elif node_type == "condition":
        then_steps = step.get("then", [])
        if isinstance(then_steps, list):
            for j, sub in enumerate(then_steps):
                _validate_step(sub, f"{path}.then[{j}]", seen_ids, errors)

        else_steps = step.get("else", [])
        if isinstance(else_steps, list):
            for j, sub in enumerate(else_steps):
                _validate_step(sub, f"{path}.else[{j}]", seen_ids, errors)

    elif node_type == "loop":
        do_steps = step.get("do") or step.get("steps", [])
        if isinstance(do_steps, list):
            for j, sub in enumerate(do_steps):
                _validate_step(sub, f"{path}.do[{j}]", seen_ids, errors)

    # on_error 验证
    on_error = step.get("on_error")
    if on_error and on_error not in VALID_ERROR_STRATEGIES:
        errors.append(ValidationError(
            f"{path}.on_error",
            f"无效的 on_error: '{on_error}'"
        ))

    # retry 验证
    retry = step.get("retry")
    if retry is not None:
        if not isinstance(retry, int) or retry < 0:
            errors.append(ValidationError(f"{path}.retry", "retry 必须是非负整数"))
