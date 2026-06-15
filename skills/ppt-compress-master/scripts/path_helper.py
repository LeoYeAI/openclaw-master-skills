#!/usr/bin/env python3
"""
Path Helper for PPT Compressor (Cross-Platform)
Helps validate and normalize user-provided file paths on Windows, macOS, and Linux.

Usage:
    python path_helper.py <path_or_user_input>
    python path_helper.py --extract "用户的完整消息，其中包含路径"

Functions:
    validate_path(path) -> dict with status, normalized_path, error
    extract_pptx_paths(text) -> list of found .pptx paths
    normalize_path(path) -> cleaned path string
    get_platform() -> 'windows' | 'darwin' | 'linux'
"""

import os
import re
import sys
import platform
from pathlib import Path


def get_platform() -> str:
    """Get the current platform name."""
    system = platform.system().lower()
    if system == 'windows':
        return 'windows'
    elif system == 'darwin':
        return 'darwin'  # macOS
    else:
        return 'linux'


def normalize_path(path: str) -> str:
    """
    Normalize a file path for cross-platform compatibility.
    
    - Removes surrounding quotes
    - On Windows: preserves drive letter, converts to forward slashes
    - On Unix: keeps forward slashes
    - Expands ~ to user home directory
    - Resolves relative paths
    
    Args:
        path: Raw path string from user input
        
    Returns:
        Normalized path string
    """
    if not path:
        return ""
    
    # Remove surrounding quotes (single or double)
    path = path.strip()
    if (path.startswith('"') and path.endswith('"')) or \
       (path.startswith("'") and path.endswith("'")):
        path = path[1:-1]
    
    # Expand user home directory (~)
    path = os.path.expanduser(path)
    
    # Convert to Path object for normalization
    try:
        p = Path(path)
        # Try to resolve if it's a valid path
        if p.exists():
            path = str(p.resolve())
        else:
            # Just normalize the path string
            path = str(p)
    except Exception:
        pass
    
    # Convert backslashes to forward slashes (Python handles both on Windows)
    path = path.replace('\\', '/')
    
    return path


def extract_pptx_paths(text: str) -> list:
    """
    Extract potential .pptx file paths from user text.
    
    Handles cross-platform paths:
    - Windows: C:/Users/name/file.pptx or C:\\Users\\name\\file.pptx
    - macOS/Linux: /Users/name/file.pptx or ~/Documents/file.pptx
    - Quoted paths: "path with spaces.pptx" or 'path.pptx'
    - Chinese and other unicode characters in paths
    
    Args:
        text: User's message that may contain file paths
        
    Returns:
        List of extracted paths (may be empty)
    """
    paths = []
    current_platform = get_platform()
    
    # Pattern 1: Quoted paths (highest priority - handles spaces and special chars)
    # Works on all platforms
    quoted_pattern = r'["\']([^"\']+\.pptx)["\']'
    for match in re.finditer(quoted_pattern, text, re.IGNORECASE):
        paths.append(match.group(1))
    
    # Pattern 2: Windows absolute paths (drive letter)
    # Handles both forward and back slashes, Chinese chars
    # Stop at whitespace, Chinese punctuation, or common delimiters
    win_pattern = r'[A-Za-z]:[/\\](?:[^<>:"|?*\n\s，。！？、；：]+[/\\])*[^<>:"|?*\n\s，。！？、；：]+\.pptx'
    for match in re.finditer(win_pattern, text, re.IGNORECASE):
        path = match.group(0)
        if path not in paths:
            paths.append(path)
    
    # Pattern 3: Home directory paths: ~/something.pptx (for macOS/Linux)
    # Only match if not already found Windows paths (to avoid false positives on Windows)
    if not paths or current_platform != 'windows':
        home_pattern = r'~[/][^\s<>:"|?*\n，。！？、；：]+\.pptx'
        for match in re.finditer(home_pattern, text, re.IGNORECASE):
            path = match.group(0)
            if path not in paths:
                paths.append(path)
    
    # Pattern 4: Unix absolute paths: /path/to/file.pptx (for macOS/Linux)
    # Must start with / and not be preceded by drive letter
    # Only match on non-Windows platforms OR if no Windows paths found
    if not paths or current_platform != 'windows':
        # Match absolute paths that start with /
        # Exclude paths that might be part of a Windows path
        unix_pattern = r'(?<![A-Za-z]:)(?<![~/\w])/(?:[^\s<>:"|?*\n，。！？、；：]+/)*[^\s<>:"|?*\n，。！？、；：]+\.pptx'
        for match in re.finditer(unix_pattern, text, re.IGNORECASE):
            path = match.group(0)
            # Verify it starts with / and is a valid absolute path
            if path.startswith('/') and path not in paths:
                paths.append(path)
    
    # Normalize all found paths
    normalized = [normalize_path(p) for p in paths]
    
    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for p in normalized:
        key = p.lower() if current_platform == 'windows' else p
        if key not in seen:
            seen.add(key)
            unique.append(p)
    
    return unique


def validate_path(path: str) -> dict:
    """
    Validate a file path and return detailed status.
    
    Args:
        path: File path to validate
        
    Returns:
        Dictionary with:
        - valid (bool): Whether the path is valid and file exists
        - normalized_path (str): Cleaned path
        - exists (bool): Whether file exists
        - is_pptx (bool): Whether file has .pptx extension
        - size_mb (float): File size in MB (if exists)
        - error (str): Error message (if any)
        - suggestion (str): Helpful suggestion for the user
    """
    result = {
        'valid': False,
        'normalized_path': '',
        'exists': False,
        'is_pptx': False,
        'size_mb': 0,
        'error': '',
        'suggestion': ''
    }
    
    if not path:
        result['error'] = '路径为空'
        result['suggestion'] = '请提供 PPT 文件的完整路径'
        return result
    
    # Normalize the path
    normalized = normalize_path(path)
    result['normalized_path'] = normalized
    
    # Check extension
    if not normalized.lower().endswith('.pptx'):
        result['error'] = f'文件扩展名不是 .pptx（当前: {Path(normalized).suffix}）'
        result['suggestion'] = '此工具只支持 .pptx 格式的 PowerPoint 文件'
        return result
    
    result['is_pptx'] = True
    
    # Check if file exists
    try:
        p = Path(normalized)
        if not p.exists():
            # Try with backslashes (Windows)
            p = Path(path)
            if not p.exists():
                result['error'] = '文件不存在'
                result['suggestion'] = f'请检查路径是否正确: {normalized}'
                return result
            else:
                normalized = str(p.resolve()).replace('\\', '/')
                result['normalized_path'] = normalized
        
        result['exists'] = True
        result['size_mb'] = round(p.stat().st_size / (1024 * 1024), 2)
        result['valid'] = True
        
    except Exception as e:
        result['error'] = f'路径解析错误: {str(e)}'
        result['suggestion'] = '路径可能包含无效字符，请尝试用引号包裹路径'
        return result
    
    return result


def format_validation_result(result: dict) -> str:
    """Format validation result for display."""
    if result['valid']:
        return f"""✅ 文件验证通过
📁 路径: {result['normalized_path']}
📊 大小: {result['size_mb']} MB
"""
    else:
        return f"""❌ 文件验证失败
原因: {result['error']}
💡 建议: {result['suggestion']}
"""


def main():
    """Command-line interface for path helper."""
    if len(sys.argv) < 2:
        print("""
PPT 路径助手 - 帮助验证和提取 PPT 文件路径

用法:
  python path_helper.py <文件路径>           验证指定路径
  python path_helper.py --extract "文本"    从文本中提取 .pptx 路径
  python path_helper.py --help              显示此帮助

示例:
  python path_helper.py "C:/Users/user/Desktop/报告.pptx"
  python path_helper.py --extract "帮我压缩 C:\\Users\\test\\文件.pptx 这个PPT"
""")
        return
    
    if sys.argv[1] == '--extract':
        if len(sys.argv) < 3:
            print("错误: --extract 需要提供文本参数")
            return
        text = ' '.join(sys.argv[2:])
        paths = extract_pptx_paths(text)
        if paths:
            print(f"找到 {len(paths)} 个 .pptx 路径:")
            for i, p in enumerate(paths, 1):
                print(f"  {i}. {p}")
                result = validate_path(p)
                if result['exists']:
                    print(f"     ✓ 文件存在 ({result['size_mb']} MB)")
                else:
                    print(f"     ✗ {result['error']}")
        else:
            print("未在文本中找到 .pptx 文件路径")
            print("💡 提示: 请确保路径包含完整的盘符（如 C:/）或使用引号包裹")
    
    elif sys.argv[1] == '--help':
        main.__doc__ and print(main.__doc__)
    
    else:
        # Validate provided path
        path = ' '.join(sys.argv[1:])
        result = validate_path(path)
        print(format_validation_result(result))
        
        if result['valid']:
            print(f"可以使用以下命令压缩:")
            print(f'python -c "import sys; sys.path.insert(0, r\'{os.path.dirname(os.path.abspath(__file__))}\'); from compress_ppt_videos import run; run(r\'{result["normalized_path"]}\')"')


if __name__ == '__main__':
    main()
