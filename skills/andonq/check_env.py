#!/usr/bin/env python3
"""
AndonQ Skill 环境检测脚本（只读，不修改任何配置）

功能：检测 Python 版本、Skill 版本更新、AK/SK 配置，输出检测结果
注意：本脚本仅做检测，不会修改任何配置

用法:
    python3 check_env.py               # 标准模式：输出详细检测结果
    python3 check_env.py --quiet       # 静默模式：仅输出错误信息
    python3 check_env.py --skip-update # 跳过版本更新检查

返回码:
    0 - 环境就绪
    1 - Python 版本不满足
    2 - AK/SK 未配置或无效
    4 - Skill 版本过旧，需要更新
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# ============== 配置 ==============
SCRIPT_DIR = Path(__file__).resolve().parent
META_FILE = SCRIPT_DIR / "_meta.json"
VERSION_CHECK_TIMEOUT = 15  # 秒

# ============== 命令行参数 ==============
QUIET_MODE = "--quiet" in sys.argv
SKIP_UPDATE = "--skip-update" in sys.argv


# ============== 输出函数 ==============
def log_info(msg: str):
    if not QUIET_MODE:
        print(msg)


def log_ok(msg: str):
    if not QUIET_MODE:
        print(f"  [OK] {msg}")


def log_warn(msg: str):
    if not QUIET_MODE:
        print(f"  [WARN] {msg}")


def log_fail(msg: str):
    print(f"  [FAIL] {msg}")


def log_section(title: str):
    if not QUIET_MODE:
        print(f"\n=== {title} ===")


# ============== 版本检查函数 ==============
def parse_version(version_str):
    """解析语义化版本号字符串为可比较的元组，如 '1.3.0' -> (1, 3, 0)"""
    try:
        parts = version_str.strip().lstrip("v").split(".")
        return tuple(int(p) for p in parts)
    except (ValueError, AttributeError):
        return (0, 0, 0)


def get_local_version():
    """读取本地 _meta.json 中的版本号，返回 (slug, version_str) 或 (None, None)"""
    if not META_FILE.exists():
        return None, None
    try:
        meta = json.loads(META_FILE.read_text(encoding="utf-8"))
        return meta.get("slug"), meta.get("version")
    except (json.JSONDecodeError, IOError):
        return None, None


def get_remote_version(slug):
    """
    从 ClawHub registry 查询指定 slug 的最新版本号。
    使用 `clawhub inspect <slug> --json` 命令获取远端版本信息。
    返回版本字符串或 None。
    """
    try:
        result = subprocess.run(
            ["clawhub", "inspect", slug, "--json"],
            capture_output=True, text=True, timeout=VERSION_CHECK_TIMEOUT,
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        return data.get("latestVersion", {}).get("version")
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError, KeyError):
        return None


def check_version_update():
    """
    检查本地版本与远端版本是否一致。

    返回 dict:
      - status: "up_to_date" | "update_available" | "check_failed" | "no_meta"
      - local_version: 本地版本号（str 或 None）
      - remote_version: 远端版本号（str 或 None）
      - slug: skill 标识符
      - message: 可读的状态说明
    """
    slug, local_ver = get_local_version()
    if not slug or not local_ver:
        return {
            "status": "no_meta",
            "local_version": None,
            "remote_version": None,
            "slug": slug,
            "message": "未找到 _meta.json 或版本信息缺失",
        }

    remote_ver = get_remote_version(slug)
    if remote_ver is None:
        return {
            "status": "check_failed",
            "local_version": local_ver,
            "remote_version": None,
            "slug": slug,
            "message": "无法获取远端版本信息（网络问题或接口不可用）",
        }

    local_parsed = parse_version(local_ver)
    remote_parsed = parse_version(remote_ver)

    if remote_parsed > local_parsed:
        return {
            "status": "update_available",
            "local_version": local_ver,
            "remote_version": remote_ver,
            "slug": slug,
            "message": f"发现新版本: {local_ver} → {remote_ver}",
        }
    else:
        return {
            "status": "up_to_date",
            "local_version": local_ver,
            "remote_version": remote_ver,
            "slug": slug,
            "message": f"当前已是最新版本: {local_ver}",
        }


# ============== 原有检查函数 ==============
def check_python_version(version_info=None):
    """
    Check if Python version is >= 3.7.

    Args:
        version_info: tuple like (major, minor, micro). If None, uses sys.version_info.

    Returns:
        (bool, str): (is_ok, message)
    """
    if version_info is None:
        version_info = sys.version_info[:3]

    major, minor, micro = version_info

    if (major, minor) >= (3, 7):
        return (True, "")
    else:
        return (False, f"Python 3.7+ required, got {major}.{minor}.{micro}")


def check_credentials(env=None):
    """
    Check if TENCENTCLOUD_SECRET_ID and TENCENTCLOUD_SECRET_KEY are set.

    Args:
        env: dict-like object to check (defaults to os.environ).

    Returns:
        (bool, str): (is_ok, message)
    """
    if env is None:
        env = os.environ

    secret_id = env.get("TENCENTCLOUD_SECRET_ID", "").strip()
    secret_key = env.get("TENCENTCLOUD_SECRET_KEY", "").strip()

    if not secret_id or not secret_key:
        missing = []
        if not secret_id:
            missing.append("TENCENTCLOUD_SECRET_ID")
        if not secret_key:
            missing.append("TENCENTCLOUD_SECRET_KEY")
        return (False, f"Missing credentials: {', '.join(missing)}")

    return (True, "")


def mask_credential(value, visible_suffix=4):
    """
    Mask a credential value, showing only the last N characters.

    Args:
        value: the credential string to mask
        visible_suffix: number of characters to show at the end

    Returns:
        str: masked credential like "AKID****xxxx"
    """
    if len(value) <= visible_suffix:
        return "*" * len(value)
    return "*" * (len(value) - visible_suffix) + value[-visible_suffix:]


def main():
    """
    Main CLI entry point. Validates environment and exits with semantic code.
    Exit codes:
    - 0: ready
    - 1: python version too low
    - 2: credentials missing or invalid
    - 4: skill version outdated
    """
    # === 1. 检查 Python 版本 ===
    log_section("1. 检查运行环境")
    py_ok, py_msg = check_python_version()
    if py_ok:
        log_ok(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    else:
        log_fail(py_msg)
        sys.exit(1)

    # === 2. 检查 Skill 版本更新 ===
    log_section("2. 检查 Skill 版本")
    if SKIP_UPDATE:
        log_ok("已跳过版本更新检查（--skip-update）")
    else:
        ver_result = check_version_update()
        status = ver_result["status"]

        if status == "up_to_date":
            log_ok(ver_result["message"])
        elif status == "update_available":
            log_warn(ver_result["message"])
            log_info("")
            log_info(f"  当前版本: {ver_result['local_version']}")
            log_info(f"  最新版本: {ver_result['remote_version']}")
            log_info("")
            log_info("  请前往 SkillHub 或 ClawHub 更新此 Skill 以获取最新功能和修复")
            log_info("")
            log_fail(f"Skill 版本过旧（{ver_result['local_version']} < {ver_result['remote_version']}），请先更新后再使用")
            sys.exit(4)
        elif status == "check_failed":
            log_warn(ver_result["message"])
            log_info("  版本检查跳过，继续后续检测...")
        elif status == "no_meta":
            log_warn(ver_result["message"])
            log_info("  版本检查跳过，继续后续检测...")

    # === 3. 检查 AK/SK 配置 ===
    log_section("3. 检查 AK/SK 配置")
    cred_ok, cred_msg = check_credentials()
    if cred_ok:
        secret_id = os.environ.get("TENCENTCLOUD_SECRET_ID", "")
        secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY", "")
        log_ok(f"TENCENTCLOUD_SECRET_ID: {mask_credential(secret_id)}")
        log_ok(f"TENCENTCLOUD_SECRET_KEY: {mask_credential(secret_key)}")
    else:
        log_fail(cred_msg)
        sys.exit(2)

    log_info("")
    log_ok("Environment validation passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
