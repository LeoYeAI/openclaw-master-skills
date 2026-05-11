#!/usr/bin/env python3
"""
Context Restore - 健壮性改进建议代码

此文件包含建议的改进实现，可集成到 restore_context.py 中
"""

import re
from functools import wraps
from typing import Any, Optional, Union


# =============================================================================
# 1. 输入验证装饰器
# =============================================================================

def validate_input(func):
    """
    输入验证装饰器
    
    为所有提取函数提供统一的输入验证：
    - 拒绝 None 输入
    - 拒绝二进制数据
    - 确保字符串输入
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 检查位置参数
        for i, arg in enumerate(args):
            if arg is None:
                raise TypeError(
                    f"{func.__name__}() received None for argument {i}"
                )
            if isinstance(arg, (bytes, bytearray)):
                raise TypeError(
                    f"{func.__name__}() received bytes, expected str"
                )
            if not isinstance(arg, (str, dict, list)) and arg is not None:
                raise TypeError(
                    f"{func.__name__}() received {type(arg).__name__}, expected str"
                )
        
        return func(*args, **kwargs)
    return wrapper


# =============================================================================
# 2. 预编译正则表达式
# =============================================================================

# 预编译的正则表达式，提升解析性能
_METADATA_PATTERNS = {
    'original': re.compile(r'原始消息数:\s*(\d+)'),
    'compressed': re.compile(r'压缩后消息数:\s*(\d+)'),
    'timestamp': re.compile(r'上下文压缩于\s*([\d\-T:.]+)'),
    'checkmark': re.compile(r'✅\s*(.+?)(?:\n|$)'),
    'checkmark_all': re.compile(r'✅\s*(.+?)(?:\n|$)', re.MULTILINE),
    'cron': re.compile(r'(\d+)个?cron任务.*?已转为'),
    'cron_alt': re.compile(r'(\d+)\s*(?:isolated sessions?)|(\d+)\s*(?:isolated mode)', re.IGNORECASE),
    'session': re.compile(r'(\d+)个活跃'),
    'session_alt': re.compile(r'(\d+)\s*(?:isolated sessions?)', re.IGNORECASE),
    'moltbook': re.compile(r'(\d{1,2}):\d{2}\s*(?:Moltbook|学习)'),
}


# =============================================================================
# 3. 改进的验证函数
# =============================================================================

def validate_message_count(value: Any, field_name: str) -> Optional[int]:
    """
    验证消息计数字段
    
    Args:
        value: 输入值
        field_name: 字段名称（用于日志）
    
    Returns:
        验证后的整数值，失败返回 None
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return None  # bool 是 int 的子类，需要排除
    if isinstance(value, (int, str)):
        try:
            num = int(value)
            if num < 0:
                return None  # 负数无效
            if num > 10_000_000:  # 设置合理上限
                return 10_000_000
            return num
        except (ValueError, TypeError):
            return None
    return None


def calculate_compression_ratio_safe(
    original: Any, 
    compressed: Any
) -> Optional[float]:
    """
    安全的压缩率计算
    
    Args:
        original: 原始消息数
        compressed: 压缩后消息数
    
    Returns:
        压缩率百分比，失败返回 None
    """
    original = validate_message_count(original, 'original')
    compressed = validate_message_count(compressed, 'compressed')
    
    if original is None or compressed is None:
        return None
    if original == 0:
        return None  # 避免除零
    
    ratio = (compressed / original) * 100
    return round(ratio, 2)


# =============================================================================
# 4. 改进的提取函数（示例）
# =============================================================================

@validate_input
def extract_recent_operations_safe(content: str, max_count: int = 5) -> list[str]:
    """
    安全版操作提取
    
    改进点：
    - 输入验证
    - 预编译正则
    - 明确的类型注解
    """
    if not content or not isinstance(content, str):
        return []
    
    operations = []
    
    # 使用预编译的正则
    if '✅' in content:
        matches = _METADATA_PATTERNS['checkmark_all'].findall(content)
        for match in matches:
            cleaned = match.strip()
            if cleaned and cleaned not in operations:
                operations.append(cleaned)
    
    # Cron 任务检测
    if 'cron' in content.lower():
        cron_match = _METADATA_PATTERNS['cron'].search(content)
        if cron_match:
            ops_text = f"{cron_match.group(0)} isolated mode"
            if ops_text not in operations:
                operations.append(ops_text)
    
    # 限制返回数量
    return operations[:max_count]


@validate_input
def extract_ongoing_tasks_safe(content: str) -> list[dict]:
    """
    安全版任务提取
    
    改进点：
    - 输入验证
    - 负数检查
    """
    if not content or not isinstance(content, str):
        return []
    
    tasks = []
    
    # Isolated Sessions
    session_match = _METADATA_PATTERNS['session'].search(content)
    if session_match:
        count = int(session_match.group(1))
        if count >= 0:  # 验证非负
            tasks.append({
                'task': 'Isolated Sessions',
                'status': 'Active',
                'detail': f'{count} sessions running in parallel'
            })
    
    # Cron Tasks
    if 'cron' in content.lower():
        cron_match = re.search(r'(\d+)个?cron任务', content)
        if cron_match:
            count = int(cron_match.group(1))
            if count >= 0:
                tasks.append({
                    'task': 'Cron Tasks',
                    'status': 'Running',
                    'detail': f'{count} scheduled tasks (isolated mode)'
                })
    
    return tasks


# =============================================================================
# 5. 统一错误码体系
# =============================================================================

class ContextErrorCode:
    """上下文恢复错误码"""
    SUCCESS = 0
    FILE_NOT_FOUND = 1001
    PERMISSION_DENIED = 1002
    INVALID_JSON = 2001
    EMPTY_CONTENT = 2002
    PARSE_ERROR = 2003
    INVALID_INPUT = 3001
    UNEXPECTED_ERROR = 9001
    
    @classmethod
    def get_message(cls, code: int) -> str:
        """获取错误码对应的消息"""
        messages = {
            0: "Success",
            1001: "File not found",
            1002: "Permission denied",
            2001: "Invalid JSON format",
            2002: "Empty content",
            2003: "Failed to parse content",
            3001: "Invalid input",
            9001: "Unexpected error",
        }
        return messages.get(code, "Unknown error")


class ContextRestoreResult:
    """
    统一的结果类
    
    提供：
    - 错误码
    - 结果数据
    - 错误消息
    - 便捷判断方法
    """
    
    def __init__(
        self,
        success: bool,
        data: Any = None,
        error_code: int = None,
        error_message: str = None
    ):
        self.success = success
        self.data = data
        self.error_code = error_code or (0 if success else ContextErrorCode.UNEXPECTED_ERROR)
        self.error_message = error_message or ContextErrorCode.get_message(self.error_code)
    
    @classmethod
    def ok(cls, data: Any = None) -> 'ContextRestoreResult':
        return cls(success=True, data=data)
    
    @classmethod
    def error(cls, code: int, message: str = None) -> 'ContextRestoreResult':
        return cls(
            success=False,
            error_code=code,
            error_message=message or ContextErrorCode.get_message(code)
        )
    
    def __bool__(self):
        return self.success
    
    def __repr__(self):
        if self.success:
            return f"Result(success=True, data={self.data})"
        return f"Result(success=False, error={self.error_code}: {self.error_message})"


# =============================================================================
# 6. 安全的主函数
# =============================================================================

def restore_context_safe(
    filepath: str, 
    level: str = 'normal'
) -> ContextRestoreResult:
    """
    安全版上下文恢复
    
    Returns:
        ContextRestoreResult 对象
    """
    from restore_context import (
        load_compressed_context,
        format_minimal_report,
        format_normal_report,
        format_detailed_report
    )
    
    # 验证参数
    if not filepath:
        return ContextRestoreResult.error(
            ContextErrorCode.INVALID_INPUT,
            "filepath cannot be empty"
        )
    
    valid_levels = ['minimal', 'normal', 'detailed']
    if level not in valid_levels:
        return ContextRestoreResult.error(
            ContextErrorCode.INVALID_INPUT,
            f"Invalid level: {level}. Must be one of: {', '.join(valid_levels)}"
        )
    
    # 加载文件
    context = load_compressed_context(filepath)
    if context is None:
        return ContextRestoreResult.error(
            ContextErrorCode.EMPTY_CONTENT,
            f"Could not load context file from: {filepath}"
        )
    
    # 处理内容
    try:
        if isinstance(context, dict):
            if 'content' in context:
                content = context['content']
            elif 'text' in context:
                content = context['text']
            elif 'data' in context:
                content = context['data']
            else:
                import json
                content = json.dumps(context, indent=2, ensure_ascii=False)
        else:
            content = str(context)
        
        # 生成报告
        if level == 'minimal':
            report = format_minimal_report(content)
        elif level == 'detailed':
            report = format_detailed_report(content)
        else:
            report = format_normal_report(content)
        
        return ContextRestoreResult.ok(report)
    
    except Exception as e:
        return ContextRestoreResult.error(
            ContextErrorCode.UNEXPECTED_ERROR,
            f"Unexpected error: {str(e)}"
        )


# =============================================================================
# 使用示例
# =============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Context Restore - 健壮性改进示例")
    print("=" * 60)
    print()
    
    # 测试输入验证
    print("1. 测试输入验证:")
    try:
        extract_recent_operations_safe(None)
    except TypeError as e:
        print(f"   ✓ None 输入被拒绝: {e}")
    
    try:
        extract_recent_operations_safe(b'binary')
    except TypeError as e:
        print(f"   ✓ 二进制输入被拒绝: {e}")
    
    # 测试安全压缩率计算
    print()
    print("2. 测试安全压缩率计算:")
    print(f"   正常: {calculate_compression_ratio_safe(100, 25)}%")
    print(f"   零值: {calculate_compression_ratio_safe(0, 10)}")
    print(f"   负数: {calculate_compression_ratio_safe(-100, 50)}")
    print(f"   None: {calculate_compression_ratio_safe(None, 10)}")
    
    # 测试安全恢复
    print()
    print("3. 测试安全上下文恢复:")
    result = restore_context_safe('/nonexistent/path.json')
    print(f"   失败: {result.success}, {result.error_message}")
    
    print()
    print("=" * 60)
