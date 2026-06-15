#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
提供参数解析、测试数据生成、验证等辅助功能
"""

import re
import random
import string
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import uuid


def generate_test_value(param_type: str, constraint: Optional[Dict[str, Any]] = None) -> Any:
    """
    根据参数类型和约束生成测试值

    Args:
        param_type: 参数类型 (string, integer, number, boolean, array, object)
        constraint: 约束条件

    Returns:
        测试值
    """
    constraint = constraint or {}

    if param_type == "string":
        return generate_string_value(constraint)
    elif param_type == "integer":
        return generate_integer_value(constraint)
    elif param_type == "number":
        return generate_number_value(constraint)
    elif param_type == "boolean":
        return generate_boolean_value(constraint)
    elif param_type == "array":
        return generate_array_value(constraint)
    elif param_type == "object":
        return generate_object_value(constraint)
    else:
        return "test_value"


def generate_string_value(constraint: Dict[str, Any]) -> str:
    """
    生成字符串测试值

    Args:
        constraint: 约束条件

    Returns:
        字符串测试值
    """
    min_length = constraint.get("minLength", 1)
    max_length = constraint.get("maxLength", 20)
    pattern = constraint.get("pattern")
    enum_values = constraint.get("enum", [])
    format_type = constraint.get("format")

    # 如果有枚举值，返回第一个
    if enum_values:
        return enum_values[0]

    # 根据format生成特定格式
    if format_type == "email":
        return "test@example.com"
    elif format_type == "phone":
        return "13800138000"
    elif format_type == "date":
        return datetime.now().strftime("%Y-%m-%d")
    elif format_type == "date-time":
        return datetime.now().isoformat()
    elif format_type == "uuid":
        return str(uuid.uuid4())
    elif format_type == "uri":
        return "https://example.com"

    # 根据pattern生成
    if pattern:
        return generate_value_by_pattern(pattern, min_length, max_length)

    # 根据长度生成
    length = min_length if min_length > 0 else min(max_length, 10)
    return "a" * length


def generate_integer_value(constraint: Dict[str, Any]) -> int:
    """
    生成整数测试值

    Args:
        constraint: 约束条件

    Returns:
        整数测试值
    """
    minimum = constraint.get("minimum", 0)
    maximum = constraint.get("maximum", 100)
    enum_values = constraint.get("enum", [])

    if enum_values:
        return enum_values[0]

    # 返回范围内的值
    return (minimum + maximum) // 2


def generate_number_value(constraint: Dict[str, Any]) -> float:
    """
    生成数字测试值

    Args:
        constraint: 约束条件

    Returns:
        数字测试值
    """
    minimum = constraint.get("minimum", 0.0)
    maximum = constraint.get("maximum", 100.0)

    return round((minimum + maximum) / 2, 2)


def generate_boolean_value(constraint: Dict[str, Any]) -> bool:
    """
    生成布尔测试值

    Args:
        constraint: 约束条件

    Returns:
        布尔测试值
    """
    return True


def generate_array_value(constraint: Dict[str, Any]) -> List[Any]:
    """
    生成数组测试值

    Args:
        constraint: 约束条件

    Returns:
        数组测试值
    """
    min_items = constraint.get("minItems", 0)
    max_items = constraint.get("maxItems", 10)
    item_type = constraint.get("items", {}).get("type", "string")

    item_count = min_items if min_items > 0 else min(max_items, 3)

    return [generate_test_value(item_type) for _ in range(item_count)]


def generate_object_value(constraint: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成对象测试值

    Args:
        constraint: 约束条件

    Returns:
        对象测试值
    """
    properties = constraint.get("properties", {})
    result = {}

    for prop_name, prop_spec in properties.items():
        prop_type = prop_spec.get("type", "string")
        result[prop_name] = generate_test_value(prop_type, prop_spec)

    return result


def generate_value_by_pattern(pattern: str, min_length: int = 1, max_length: int = 20) -> str:
    """
    根据正则表达式生成测试值

    Args:
        pattern: 正则表达式
        min_length: 最小长度
        max_length: 最大长度

    Returns:
        符合模式的测试值
    """
    # 简单的正则到测试值映射
    pattern_map = {
        r"^[a-zA-Z0-9_]+$": "test_user_123",
        r"^[a-zA-Z]+$": "test",
        r"^[0-9]+$": "123456",
        r"^[a-zA-Z0-9]+$": "test123",
        r"^\\d{6}$": "123456",
        r"^\\d{11}$": "13800138000",
    }

    for regex, value in pattern_map.items():
        if re.match(regex, pattern):
            return value

    # 默认返回
    return "test_value"


def generate_invalid_value(param_type: str, constraint: Optional[Dict[str, Any]] = None) -> Any:
    """
    生成无效测试值（用于边界和异常测试）

    Args:
        param_type: 参数类型
        constraint: 约束条件

    Returns:
        无效测试值
    """
    constraint = constraint or {}

    if param_type == "string":
        return generate_invalid_string(constraint)
    elif param_type == "integer":
        return generate_invalid_integer(constraint)
    elif param_type == "number":
        return generate_invalid_number(constraint)
    elif param_type == "boolean":
        return "invalid_boolean"
    elif param_type == "array":
        return "invalid_array"
    else:
        return "invalid_value"


def generate_invalid_string(constraint: Dict[str, Any]) -> str:
    """
    生成无效字符串

    Args:
        constraint: 约束条件

    Returns:
        无效字符串
    """
    min_length = constraint.get("minLength", 0)
    max_length = constraint.get("maxLength", 20)
    enum_values = constraint.get("enum", [])
    format_type = constraint.get("format")

    # 如果是最小长度>0，返回空字符串
    if min_length > 0:
        return ""

    # 如果是枚举，返回不在枚举中的值
    if enum_values:
        return "invalid_enum_value"

    # 根据format返回无效值
    if format_type == "email":
        return "invalid-email"
    elif format_type == "phone":
        return "13800"  # 太短

    # 超长字符串
    return "a" * (max_length + 1)


def generate_invalid_integer(constraint: Dict[str, Any]) -> Union[int, str]:
    """
    生成无效整数

    Args:
        constraint: 约束条件

    Returns:
        无效整数值
    """
    minimum = constraint.get("minimum")
    maximum = constraint.get("maximum")
    enum_values = constraint.get("enum", [])

    # 返回小于最小值的数
    if minimum is not None:
        return minimum - 1

    # 返回大于最大值的数
    if maximum is not None:
        return maximum + 1

    # 返回字符串
    return "invalid_integer"


def generate_invalid_number(constraint: Dict[str, Any]) -> Union[float, str]:
    """
    生成无效数字

    Args:
        constraint: 约束条件

    Returns:
        无效数字值
    """
    return generate_invalid_integer(constraint)


def is_sql_injection(value: str) -> bool:
    """
    检测是否为SQL注入攻击

    Args:
        value: 输入值

    Returns:
        是否为SQL注入
    """
    sql_patterns = [
        r".*'.*OR.*'.*=.*'.*",
        r".*;.*DROP\s+.*",
        r".*;.*DELETE\s+.*",
        r".*;.*UPDATE\s+.*",
        r".*UNION\s+SELECT.*",
        r"'.*--.*",
        r"'.*/\*.*\*/.*",
    ]

    for pattern in sql_patterns:
        if re.match(pattern, value, re.IGNORECASE):
            return True

    return False


def is_xss(value: str) -> bool:
    """
    检测是否为XSS攻击

    Args:
        value: 输入值

    Returns:
        是否为XSS
    """
    xss_patterns = [
        r"<script[^>]*>.*</script>",
        r"<[^>]+on\w+\s*=.*>",
        r"javascript:",
        r"vbscript:",
        r"onerror\s*=",
        r"onload\s*=",
        r"onclick\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
    ]

    for pattern in xss_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            return True

    return False


def validate_email(email: str) -> bool:
    """
    验证邮箱格式

    Args:
        email: 邮箱地址

    Returns:
        是否有效
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """
    验证手机号格式

    Args:
        phone: 手机号

    Returns:
        是否有效
    """
    pattern = r"^1[3-9]\d{9}$"
    return re.match(pattern, phone) is not None


def validate_url(url: str) -> bool:
    """
    验证URL格式

    Args:
        url: URL地址

    Returns:
        是否有效
    """
    pattern = r"^https?://[a-zA-Z0-9.-]+(:\d+)?(/.*)?$"
    return re.match(pattern, url) is not None


def validate_uuid(uuid_str: str) -> bool:
    """
    验证UUID格式

    Args:
        uuid_str: UUID字符串

    Returns:
        是否有效
    """
    try:
        uuid.UUID(uuid_str)
        return True
    except ValueError:
        return False


def calculate_boundary_values(min_value: Optional[Union[int, float]] = None,
                              max_value: Optional[Union[int, float]] = None) -> Dict[str, Any]:
    """
    计算边界值

    Args:
        min_value: 最小值
        max_value: 最大值

    Returns:
        边界值字典
    """
    result = {}

    if min_value is not None:
        result["minimum"] = min_value
        result["just_above_minimum"] = min_value + 1 if isinstance(min_value, int) else min_value + 0.1
        result["just_below_minimum"] = min_value - 1 if isinstance(min_value, int) else min_value - 0.1

    if max_value is not None:
        result["maximum"] = max_value
        result["just_below_maximum"] = max_value - 1 if isinstance(max_value, int) else max_value - 0.1
        result["just_above_maximum"] = max_value + 1 if isinstance(max_value, int) else max_value + 0.1

    return result


def format_test_value(value: Any) -> str:
    """
    格式化测试值为可读字符串

    Args:
        value: 测试值

    Returns:
        格式化后的字符串
    """
    if value is None:
        return "null"
    elif isinstance(value, str):
        # 处理特殊字符
        if "<" in value or ">" in value:
            return f'"{value}"'
        elif "'" in value:
            return f'"{value}"'
        else:
            return f'"{value}"'
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, list):
        return str(value)
    elif isinstance(value, dict):
        return str(value)
    else:
        return repr(value)


def get_priority(rule_type: str, config: Optional[Dict[str, Any]] = None) -> str:
    """
    获取测试优先级

    Args:
        rule_type: 规则类型
        config: 配置

    Returns:
        优先级（P0/P1/P2）
    """
    config = config or {}
    priority_rules = config.get("priority_rules", {})

    return priority_rules.get(rule_type, "P1")


def count_test_points(test_points: Dict[str, List[Dict[str, Any]]]) -> Dict[str, int]:
    """
    统计测试点数量

    Args:
        test_points: 测试点字典

    Returns:
        统计结果
    """
    stats = {}
    total = 0

    for category, points in test_points.items():
        count = len(points)
        stats[category] = count
        total += count

    stats["total"] = total
    return stats


def generate_summary(stats: Dict[str, int]) -> str:
    """
    生成统计摘要

    Args:
        stats: 统计数据

    Returns:
        摘要字符串
    """
    lines = []

    category_names = {
        "parameter_tests": "参数校验",
        "business_logic_tests": "业务逻辑",
        "response_tests": "响应验证",
        "security_tests": "安全测试",
        "performance_tests": "性能测试"
    }

    for category, count in stats.items():
        if category == "total":
            continue
        name = category_names.get(category, category)
        lines.append(f"- {name}：{count}个测试点")

    lines.append(f"- **总计：{stats.get('total', 0)}个测试点**")

    return "\n".join(lines)


if __name__ == "__main__":
    # 测试工具函数
    print("=== 测试值生成示例 ===")

    print("字符串:", generate_test_value("string", {"minLength": 3, "maxLength": 20}))
    print("整数:", generate_test_value("integer", {"minimum": 0, "maximum": 100}))
    print("数字:", generate_test_value("number", {"minimum": 0.0, "maximum": 100.0}))
    print("布尔:", generate_test_value("boolean"))
    print("数组:", generate_test_value("array", {"minItems": 1, "maxItems": 5}))

    print("\n=== 无效值生成示例 ===")
    print("无效字符串:", generate_invalid_value("string", {"minLength": 3}))
    print("无效整数:", generate_invalid_value("integer", {"minimum": 0}))

    print("\n=== 安全检测示例 ===")
    print("SQL注入检测:", is_sql_injection("' OR '1'='1"))
    print("XSS检测:", is_xss("<script>alert(1)</script>"))

    print("\n=== 格式验证示例 ===")
    print("邮箱验证:", validate_email("test@example.com"))
    print("手机号验证:", validate_phone("13800138000"))
    print("UUID验证:", validate_uuid(str(uuid.uuid4())))

    print("\n=== 边界值计算示例 ===")
    boundaries = calculate_boundary_values(0, 100)
    print("边界值:", boundaries)
