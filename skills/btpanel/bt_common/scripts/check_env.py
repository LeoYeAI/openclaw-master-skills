#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""
跨平台环境检查脚本
检查 Python 版本和依赖，支持 Windows/Linux/macOS
输出 JSON 结果供 AI 解析
"""

import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

# 宝塔面板最低版本要求
MIN_PANEL_VERSION = "9.0.0"

# 全局配置路径
GLOBAL_CONFIG_PATH = Path.home() / ".openclaw" / "bt-skills.yaml"


def get_platform_info() -> dict:
    """获取平台信息"""
    system = platform.system()
    return {
        "system": system,
        "system_lower": system.lower(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "is_windows": system == "Windows",
        "is_linux": system == "Linux",
        "is_macos": system == "Darwin",
    }


def check_python_version() -> dict:
    """检查 Python 版本"""
    version = sys.version_info
    required_major = 3
    required_minor = 10

    is_valid = version.major > required_major or (
        version.major == required_major and version.minor >= required_minor
    )

    return {
        "version": f"{version.major}.{version.minor}.{version.micro}",
        "required": f"{required_major}.{required_minor}+",
        "is_valid": is_valid,
        "message": (
            f"Python 版本 {'符合要求' if is_valid else '不符合要求'}: "
            f"当前 {version.major}.{version.minor}.{version.micro}, 需要 {required_major}.{required_minor}+"
        ),
    }


def check_module(module_name: str, import_name: str = None) -> dict:
    """检查单个模块"""
    import_name = import_name or module_name
    try:
        module = __import__(import_name)
        version = getattr(module, "__version__", "unknown")
        return {
            "name": module_name,
            "installed": True,
            "version": version,
            "message": f"✓ {module_name} ({version})",
        }
    except ImportError:
        return {
            "name": module_name,
            "installed": False,
            "version": None,
            "message": f"✗ {module_name} 未安装",
        }


def check_dependencies() -> dict:
    """检查依赖"""
    required_modules = [
        ("requests", "requests"),
        ("pyyaml", "yaml"),
        ("rich", "rich"),
    ]

    optional_modules = [
        ("pytest", "pytest"),
    ]

    required_results = []
    required_passed = True

    for module_name, import_name in required_modules:
        result = check_module(module_name, import_name)
        required_results.append(result)
        if not result["installed"]:
            required_passed = False

    optional_results = []
    for module_name, import_name in optional_modules:
        optional_results.append(check_module(module_name, import_name))

    return {
        "required": required_results,
        "required_passed": required_passed,
        "optional": optional_results,
    }


def find_python_executable() -> dict:
    """查找可用的 Python 可执行文件"""
    candidates = ["python3", "python", "py"]
    found = []
    preferred = None

    for cmd in candidates:
        try:
            result = subprocess.run(
                [cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                version_str = result.stdout.strip() or result.stderr.strip()
                found.append(
                    {
                        "command": cmd,
                        "version": version_str,
                        "path": find_executable_path(cmd),
                    }
                )
                if preferred is None and "3." in version_str:
                    preferred = cmd
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            continue

    # 当前 Python 优先
    current = sys.executable

    return {
        "current": current,
        "preferred": preferred or sys.executable,
        "all_found": found,
    }


def find_executable_path(cmd: str) -> str:
    """查找可执行文件路径"""
    try:
        result = subprocess.run(
            ["which" if platform.system() != "Windows" else "where", cmd],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip().split("\n")[0]
    except Exception:
        pass
    return "unknown"


def check_config_file() -> dict:
    """检查配置文件"""
    project_root = Path(__file__).parent.parent
    config_path = project_root / "config"

    results = {
        "global_config_path": str(GLOBAL_CONFIG_PATH),
        "global_config_exists": GLOBAL_CONFIG_PATH.exists(),
        "local_config_dir_exists": config_path.exists(),
        "local_config_exists": (config_path / "servers.local.yaml").exists(),
        "example_config_exists": (config_path / "servers.yaml").exists() or (config_path / "servers.yaml.example").exists(),
        "env_var_set": "BT_CONFIG_PATH" in os.environ,
        "env_var_value": os.environ.get("BT_CONFIG_PATH"),
    }

    # 配置就绪：全局配置存在 或 本地配置存在 或 环境变量设置
    results["config_ready"] = (
        results["global_config_exists"]
        or results["local_config_exists"]
        or results["env_var_set"]
    )

    if results["config_ready"]:
        results["message"] = "配置文件已就绪"
        # 指出使用的配置路径
        if results["env_var_set"]:
            results["active_config"] = results["env_var_value"]
        elif results["global_config_exists"]:
            results["active_config"] = str(GLOBAL_CONFIG_PATH)
        else:
            results["active_config"] = str(config_path / "servers.local.yaml")
    else:
        results["message"] = f"需要创建配置文件: {GLOBAL_CONFIG_PATH} 或 config/servers.local.yaml"
        results["active_config"] = None

    return results


def check_skills_directory() -> dict:
    """检查技能目录结构"""
    project_root = Path(__file__).parent.parent
    skills_dir = project_root / "skills"

    required_skills = [
        "bt_common",
        "bt-system-monitor",
        "bt-security-check",
        "bt-health-check",
    ]

    results = {
        "skills_dir_exists": skills_dir.exists(),
        "skills": {},
    }

    for skill in required_skills:
        skill_path = skills_dir / skill
        results["skills"][skill] = {
            "exists": skill_path.exists(),
            "has_skill_md": (skill_path / "SKILL.md").exists() if skill != "bt_common" else None,
            "has_scripts": (skill_path / "scripts").exists() if skill != "bt_common" else None,
        }

    results["all_skills_present"] = all(
        results["skills"][s]["exists"] for s in required_skills
    )

    return results


def get_install_commands() -> dict:
    """获取安装命令"""
    system = platform.system()

    commands = {
        "pip_install": "pip install -r requirements.txt",
        "pip_install_user": "pip install --user -r requirements.txt",
    }

    if system == "Windows":
        commands.update({
            "winget_python": "winget install Python.Python.3.12",
            "choco_python": "choco install python",
        })
    elif system == "Linux":
        commands.update({
            "apt": "sudo apt install python3 python3-pip python3-yaml python3-requests",
            "dnf": "sudo dnf install python3 python3-pip python3-pyyaml python3-requests",
            "pacman": "sudo pacman -S python python-pip python-yaml python-requests",
        })
    elif system == "Darwin":
        commands.update({
            "brew": "brew install python3 pyyaml",
        })

    return commands


def run_full_check() -> dict:
    """运行完整检查"""
    platform_info = get_platform_info()
    python_check = check_python_version()
    deps_check = check_dependencies()
    python_exe = find_python_executable()
    config_check = check_config_file()
    skills_check = check_skills_directory()
    install_cmds = get_install_commands()

    # 计算总体状态
    all_passed = (
        python_check["is_valid"]
        and deps_check["required_passed"]
        and config_check["config_ready"]
        and skills_check["all_skills_present"]
    )

    return {
        "status": "passed" if all_passed else "failed",
        "passed": all_passed,
        "min_panel_version": MIN_PANEL_VERSION,
        "platform": platform_info,
        "python": python_check,
        "python_executable": python_exe,
        "dependencies": deps_check,
        "config": config_check,
        "skills": skills_check,
        "install_commands": install_cmds,
        "summary": generate_summary(
            python_check, deps_check, config_check, skills_check, all_passed
        ),
    }


def generate_summary(python, deps, config, skills, all_passed) -> dict:
    """生成摘要"""
    issues = []
    suggestions = []

    if not python["is_valid"]:
        issues.append(f"Python 版本过低: {python['version']}，需要 {python['required']}")
        suggestions.append("请升级 Python 到 3.10 或更高版本")

    for dep in deps["required"]:
        if not dep["installed"]:
            issues.append(f"缺少依赖: {dep['name']}")
            suggestions.append(f"运行: pip install {dep['name']}")

    if not config["config_ready"]:
        issues.append("配置文件未就绪")
        suggestions.append(f"创建全局配置: {GLOBAL_CONFIG_PATH}")
        suggestions.append("或创建本地配置: config/servers.local.yaml")

    for skill_name, skill_info in skills["skills"].items():
        if not skill_info["exists"]:
            issues.append(f"缺少技能目录: {skill_name}")

    return {
        "is_ready": all_passed,
        "issues": issues,
        "suggestions": suggestions,
        "min_panel_version": MIN_PANEL_VERSION,
        "message": "环境检查通过，可以开始使用" if all_passed else "环境存在问题，请根据提示修复",
    }


def print_human_readable(result: dict):
    """打印人类可读的输出"""
    print("=" * 60)
    print("宝塔面板日志巡检技能包 - 环境检查")
    print("=" * 60)
    print()

    # 平台信息
    print(f"🖥️  操作系统: {result['platform']['system']} ({result['platform']['machine']})")
    print(f"🐍 Python: {result['python']['version']}")
    print(f"   状态: {'✅ ' + result['python']['message'] if result['python']['is_valid'] else '❌ ' + result['python']['message']}")
    print(f"📋 宝塔面板版本要求: >= {result.get('min_panel_version', MIN_PANEL_VERSION)}")
    print()

    # 依赖检查
    print("📦 依赖检查:")
    for dep in result["dependencies"]["required"]:
        status = "✅" if dep["installed"] else "❌"
        print(f"   {status} {dep['name']}: {dep['version'] or '未安装'}")
    print()

    # 配置检查
    print("⚙️  配置检查:")
    print(f"   全局配置路径: {result['config']['global_config_path']}")
    if result["config"]["global_config_exists"]:
        print("   ✅ 全局配置已存在")
    elif result["config"]["config_ready"]:
        print(f"   ✅ 配置文件已就绪: {result['config'].get('active_config', '未知')}")
    else:
        print("   ❌ 配置文件未就绪")
        print(f"   提示: {result['config']['message']}")
    print()

    # 技能检查
    print("📁 技能目录:")
    for skill_name, skill_info in result["skills"]["skills"].items():
        status = "✅" if skill_info["exists"] else "❌"
        print(f"   {status} {skill_name}")
    print()

    # 摘要
    print("=" * 60)
    if result["passed"]:
        print("✅ 环境检查通过，可以开始使用!")
    else:
        print("❌ 环境检查未通过，请修复以下问题:")
        for issue in result["summary"]["issues"]:
            print(f"   - {issue}")
        print()
        print("💡 建议:")
        for suggestion in result["summary"]["suggestions"]:
            print(f"   - {suggestion}")
    print("=" * 60)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="宝塔面板日志巡检技能包 - 环境检查",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "text"],
        default="text",
        help="输出格式 (json/text)",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="静默模式，只输出结果状态",
    )

    args = parser.parse_args()

    result = run_full_check()

    if args.quiet:
        print("passed" if result["passed"] else "failed")
        sys.exit(0 if result["passed"] else 1)

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_human_readable(result)

    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
