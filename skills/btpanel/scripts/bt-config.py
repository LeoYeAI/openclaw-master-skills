#!/usr/bin/env python3
# /// script
# dependencies = [
#   "pyyaml>=6.0",
# ]
# ///
"""
宝塔面板配置管理工具
支持查看、添加、删除、修改服务器配置
"""

import argparse
import json
import sys
from pathlib import Path

# 兼容开发环境和发布环境的导入
# 发布环境: bt_common/ (脚本在 scripts/)
# 开发环境: src/bt_common/ (脚本在 src/btpanel/scripts/)
_script_root = Path(__file__).parent.parent
if (_script_root / "bt_common").exists():
    # 发布环境: 脚本在 {baseDir}/scripts/，bt_common 在 {baseDir}/bt_common/
    sys.path.insert(0, str(_script_root))
else:
    # 开发环境: 脚本在 src/btpanel/scripts/，bt_common 在 src/bt_common/
    # _script_root = src/btpanel, 需要找 src/bt_common
    dev_src = _script_root.parent  # src/
    if (dev_src / "bt_common").exists():
        sys.path.insert(0, str(dev_src))
    else:
        # 兜底：使用项目根目录的 src
        sys.path.insert(0, str(_script_root.parent.parent / "src"))

from bt_common import (
    GLOBAL_CONFIG_FILE,
    MIN_PANEL_VERSION,
    add_server,
    create_default_global_config,
    find_config_file,
    get_config_info,
    load_config,
    normalize_host,
    remove_server,
    update_thresholds,
    validate_host,
)


def cmd_list(args):
    """列出所有服务器配置"""
    try:
        config_info = get_config_info()

        print("=" * 60)
        print("宝塔面板配置信息")
        print("=" * 60)
        print(f"配置文件: {config_info.get('current_config_path', '未设置')}")
        print(f"全局配置: {config_info.get('global_config_path', '')}")
        print(f"宝塔版本要求: >= {config_info.get('min_panel_version', MIN_PANEL_VERSION)}")
        print()

        servers = config_info.get("servers", [])
        if not servers:
            print("暂无服务器配置")
            print()
            print("使用以下命令添加服务器:")
            print("  bt-config add --name <名称> --host <地址> --token <密钥>")
            return 0

        print(f"服务器列表 ({len(servers)} 个):")
        print("-" * 60)
        for server in servers:
            status = "✓" if server.get("enabled", True) else "✗"
            print(f"  [{status}] {server['name']}")
            print(f"       地址: {server['host']}")
        print()

        thresholds = config_info.get("thresholds", {})
        if thresholds:
            print("告警阈值:")
            print(f"  CPU: {thresholds.get('cpu', 80)}%")
            print(f"  内存: {thresholds.get('memory', 85)}%")
            print(f"  磁盘: {thresholds.get('disk', 90)}%")

        return 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_add(args):
    """添加服务器配置"""
    try:
        # 验证并规范化地址
        is_valid, result = validate_host(args.host)
        if not is_valid:
            print(f"错误: {result}", file=sys.stderr)
            return 1

        normalized_host = result
        if normalized_host != args.host:
            print(f"提示: 地址已规范化为 {normalized_host}")

        # 检查是否已存在
        config_info = get_config_info()
        existing_names = [s["name"] for s in config_info.get("servers", [])]

        if args.name in existing_names and not args.force:
            print(f"错误: 服务器 '{args.name}' 已存在，使用 --force 覆盖")
            return 1

        result = add_server(
            name=args.name,
            host=normalized_host,
            token=args.token,
            timeout=args.timeout,
            enabled=not args.disabled,
        )

        if result:
            print(f"✓ 已添加服务器: {args.name}")
            print(f"  地址: {normalized_host}")
            print(f"  超时: {args.timeout}ms")
            print(f"  状态: {'禁用' if args.disabled else '启用'}")
            print()
            print(f"配置文件: {GLOBAL_CONFIG_FILE}")
            return 0
        else:
            print("添加失败")
            return 1

    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_remove(args):
    """删除服务器配置"""
    try:
        result = remove_server(args.name)

        if result:
            print(f"✓ 已删除服务器: {args.name}")
            print(f"配置文件: {GLOBAL_CONFIG_FILE}")
            return 0
        else:
            print(f"未找到服务器: {args.name}")
            return 1

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_update(args):
    """更新服务器配置"""
    try:
        # 先删除再添加
        config_info = get_config_info()
        existing = None
        for s in config_info.get("servers", []):
            if s["name"] == args.name:
                existing = s
                break

        if not existing:
            print(f"未找到服务器: {args.name}")
            return 1

        # 合并参数
        new_host = args.host if args.host else existing["host"]
        new_token = args.token if args.token else existing.get("token", "")
        new_timeout = args.timeout if args.timeout else existing.get("timeout", 10000)
        new_enabled = not args.disabled if args.disabled is not None else existing.get("enabled", True)

        # 删除旧的，添加新的
        remove_server(args.name)
        add_server(
            name=args.name,
            host=new_host,
            token=new_token,
            timeout=new_timeout,
            enabled=new_enabled,
        )

        print(f"✓ 已更新服务器: {args.name}")
        print(f"  地址: {new_host}")
        print(f"  超时: {new_timeout}ms")
        print(f"  状态: {'禁用' if not new_enabled else '启用'}")
        return 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_threshold(args):
    """设置告警阈值"""
    try:
        result = update_thresholds(
            cpu=args.cpu,
            memory=args.memory,
            disk=args.disk,
        )

        if result:
            print("✓ 已更新告警阈值:")
            if args.cpu:
                print(f"  CPU: {args.cpu}%")
            if args.memory:
                print(f"  内存: {args.memory}%")
            if args.disk:
                print(f"  磁盘: {args.disk}%")
            print(f"配置文件: {GLOBAL_CONFIG_FILE}")
            return 0
        else:
            print("更新失败")
            return 1

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_init(args):
    """初始化配置文件"""
    try:
        config_path = create_default_global_config()
        print(f"✓ 已创建配置文件: {config_path}")
        print()
        print("请编辑配置文件添加服务器信息:")
        print(f"  {config_path}")
        print()
        print("或使用命令添加服务器:")
        print("  bt-config add --name <名称> --host <地址> --token <密钥>")
        return 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_show(args):
    """显示完整配置"""
    try:
        config_path = find_config_file()
        if not config_path:
            print("未找到配置文件")
            print("运行 'bt-config init' 创建配置文件")
            return 1

        config = load_config(config_path)

        if args.format == "json":
            print(json.dumps(config, ensure_ascii=False, indent=2))
        else:
            import yaml
            print(yaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False))

        return 0

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def cmd_path(args):
    """显示配置文件路径"""
    config_path = find_config_file()
    print(f"全局配置: {GLOBAL_CONFIG_FILE}")
    print(f"全局配置存在: {'是' if GLOBAL_CONFIG_FILE.exists() else '否'}")
    if config_path:
        print(f"当前使用: {config_path}")
    else:
        print("当前使用: 未配置")
    print()
    print("配置优先级:")
    print("  1. BT_CONFIG_PATH 环境变量")
    print(f"  2. 全局配置: {GLOBAL_CONFIG_FILE}")
    print("  3. 本地配置: config/servers.local.yaml")
    print("  4. 默认配置: config/servers.yaml")
    return 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="宝塔面板配置管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 初始化配置文件
  bt-config init

  # 列出所有服务器
  bt-config list

  # 添加服务器
  bt-config add --name prod-01 --host https://panel.example.com:8888 --token YOUR_TOKEN

  # 更新服务器
  bt-config update prod-01 --host https://new.example.com:8888

  # 禁用服务器
  bt-config update prod-01 --disabled

  # 删除服务器
  bt-config remove prod-01

  # 设置告警阈值
  bt-config threshold --cpu 75 --memory 80

  # 显示配置文件路径
  bt-config path

  # 显示完整配置
  bt-config show
  bt-config show --format json
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # list 命令
    subparsers.add_parser("list", help="列出所有服务器配置")

    # add 命令
    add_parser = subparsers.add_parser("add", help="添加服务器配置")
    add_parser.add_argument("--name", "-n", required=True, help="服务器名称")
    add_parser.add_argument("--host", "-H", required=True, help="面板地址 (如 https://panel.example.com:8888)")
    add_parser.add_argument("--token", "-t", required=True, help="API Token")
    add_parser.add_argument("--timeout", type=int, default=10000, help="超时时间(毫秒)，默认 10000")
    add_parser.add_argument("--disabled", action="store_true", help="禁用此服务器")
    add_parser.add_argument("--force", "-f", action="store_true", help="强制覆盖已存在的配置")

    # remove 命令
    remove_parser = subparsers.add_parser("remove", help="删除服务器配置")
    remove_parser.add_argument("name", help="服务器名称")

    # update 命令
    update_parser = subparsers.add_parser("update", help="更新服务器配置")
    update_parser.add_argument("name", help="服务器名称")
    update_parser.add_argument("--host", "-H", help="面板地址")
    update_parser.add_argument("--token", "-t", help="API Token")
    update_parser.add_argument("--timeout", type=int, help="超时时间(毫秒)")
    update_parser.add_argument("--disabled", type=lambda x: x.lower() in ("true", "1", "yes"), help="是否禁用 (true/false)")

    # threshold 命令
    threshold_parser = subparsers.add_parser("threshold", help="设置告警阈值")
    threshold_parser.add_argument("--cpu", type=int, help="CPU 使用率阈值(%)")
    threshold_parser.add_argument("--memory", type=int, help="内存使用率阈值(%)")
    threshold_parser.add_argument("--disk", type=int, help="磁盘使用率阈值(%)")

    # init 命令
    subparsers.add_parser("init", help="初始化配置文件")

    # show 命令
    show_parser = subparsers.add_parser("show", help="显示完整配置")
    show_parser.add_argument("--format", "-f", choices=["yaml", "json"], default="yaml", help="输出格式")

    # path 命令
    subparsers.add_parser("path", help="显示配置文件路径")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # 分发命令
    commands = {
        "list": cmd_list,
        "add": cmd_add,
        "remove": cmd_remove,
        "update": cmd_update,
        "threshold": cmd_threshold,
        "init": cmd_init,
        "show": cmd_show,
        "path": cmd_path,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
