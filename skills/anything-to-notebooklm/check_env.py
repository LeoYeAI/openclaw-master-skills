#!/usr/bin/env python3
"""
环境检查脚本 - 验证 anything-to-notebooklm skill 所有依赖
"""

import sys
import os
import json
from pathlib import Path

# 颜色输出
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

def print_status(status, message):
    """打印状态信息"""
    if status == "ok":
        print(f"{GREEN}✅ {message}{NC}")
    elif status == "warning":
        print(f"{YELLOW}⚠️  {message}{NC}")
    elif status == "error":
        print(f"{RED}❌ {message}{NC}")
    else:
        print(f"{BLUE}ℹ️  {message}{NC}")

def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    if version.major >= 3 and version.minor >= 9:
        print_status("ok", f"Python {version_str}")
        return True
    else:
        print_status("error", f"Python {version_str} (需要 3.9+)")
        return False

def check_module(module_name, import_name=None):
    """检查 Python 模块是否已安装"""
    if import_name is None:
        import_name = module_name

    try:
        __import__(import_name)
        print_status("ok", f"{module_name} 已安装")
        return True
    except ImportError:
        print_status("error", f"{module_name} 未安装")
        return False

def check_command(cmd):
    """检查命令是否可用"""
    import shutil

    if shutil.which(cmd):
        # 尝试获取版本
        import subprocess
        try:
            result = subprocess.run([cmd, "--version"],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)
            version = result.stdout.split('\n')[0] if result.stdout else "unknown"
            print_status("ok", f"{cmd} 已安装 ({version})")
        except:
            print_status("ok", f"{cmd} 已安装")
        return True
    else:
        print_status("error", f"{cmd} 未找到")
        return False

def check_mcp_config():
    """检查 MCP 配置"""
    config_path = Path.home() / ".claude" / "config.json"

    if not config_path.exists():
        print_status("error", f"未找到 Claude 配置文件: {config_path}")
        return False

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        if "mcpServers" in config and "weixin-reader" in config["mcpServers"]:
            print_status("ok", "MCP 服务器已配置")
            return True
        else:
            print_status("warning", "MCP 服务器未配置（需要手动添加）")
            return False
    except Exception as e:
        print_status("error", f"无法读取配置文件: {e}")
        return False

def check_mcp_server():
    """检查 MCP 服务器文件"""
    skill_dir = Path(__file__).parent
    mcp_server = skill_dir / "wexin-read-mcp" / "src" / "server.py"

    if mcp_server.exists():
        print_status("ok", f"MCP 服务器文件存在")
        return True
    else:
        print_status("error", f"MCP 服务器文件不存在: {mcp_server}")
        return False

def check_notebooklm_auth():
    """检查 NotebookLM 认证状态"""
    import subprocess

    try:
        result = subprocess.run(["notebooklm", "list"],
                              capture_output=True,
                              text=True,
                              timeout=10)

        if result.returncode == 0:
            print_status("ok", "NotebookLM 已认证")
            return True
        else:
            print_status("warning", "NotebookLM 未认证（请运行 notebooklm login）")
            return False
    except subprocess.TimeoutExpired:
        print_status("warning", "NotebookLM 认证检查超时")
        return False
    except Exception as e:
        print_status("error", f"NotebookLM 认证检查失败: {e}")
        return False

def main():
    print(f"\n{BLUE}========================================{NC}")
    print(f"{BLUE}  环境检查 - anything-to-notebooklm{NC}")
    print(f"{BLUE}========================================{NC}\n")

    results = []

    # 1. Python 版本
    print(f"{YELLOW}[1/8] Python 版本{NC}")
    results.append(check_python_version())
    print()

    # 2. 核心依赖
    print(f"{YELLOW}[2/9] 核心 Python 依赖{NC}")
    results.append(check_module("fastmcp"))
    results.append(check_module("playwright"))
    results.append(check_module("beautifulsoup4", "bs4"))
    results.append(check_module("lxml"))
    results.append(check_module("markitdown"))
    print()

    # 3. Playwright 浏览器
    print(f"{YELLOW}[3/9] Playwright 可导入性{NC}")
    try:
        from playwright.sync_api import sync_playwright
        print_status("ok", "Playwright 可以正常导入")
        results.append(True)
    except Exception as e:
        print_status("error", f"Playwright 导入失败: {e}")
        results.append(False)
    print()

    # 4. NotebookLM CLI
    print(f"{YELLOW}[4/9] NotebookLM CLI{NC}")
    results.append(check_command("notebooklm"))
    print()

    # 5. markitdown CLI
    print(f"{YELLOW}[5/9] markitdown CLI{NC}")
    results.append(check_command("markitdown"))
    print()

    # 6. Git 命令
    print(f"{YELLOW}[6/9] Git 命令{NC}")
    results.append(check_command("git"))
    print()

    # 7. MCP 服务器文件
    print(f"{YELLOW}[7/9] MCP 服务器文件{NC}")
    results.append(check_mcp_server())
    print()

    # 8. MCP 配置
    print(f"{YELLOW}[8/9] MCP 配置{NC}")
    results.append(check_mcp_config())
    print()

    # 9. NotebookLM 认证
    print(f"{YELLOW}[9/9] NotebookLM 认证{NC}")
    results.append(check_notebooklm_auth())
    print()

    # 总结
    print(f"{BLUE}========================================{NC}")
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"{GREEN}✅ 所有检查通过 ({passed}/{total})！环境配置完整。{NC}")
    elif passed >= total * 0.8:
        print(f"{YELLOW}⚠️  大部分检查通过 ({passed}/{total})，但有些问题需要修复。{NC}")
    else:
        print(f"{RED}❌ 检查失败 ({passed}/{total})，请运行 install.sh 重新安装。{NC}")

    print(f"{BLUE}========================================{NC}\n")

    if passed < total:
        print("💡 修复建议：")
        print("  1. 运行安装脚本：./install.sh")
        print("  2. 配置 MCP：编辑 ~/.claude/config.json")
        print("  3. 认证 NotebookLM：notebooklm login")
        print()

    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
