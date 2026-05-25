"""曲线救国 CLI 入口 - 机票模糊搜索工具

支持平台：去哪儿、携程、飞猪、同程
输出: JSON（ensure_ascii=False）
退出码: 0=成功, 1=错误
"""

from __future__ import annotations

import argparse
import json
import logging
import sys

# Windows 控制台默认编码不支持中文，强制 UTF-8
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("qvxian-cli")


def _output(data: dict, exit_code: int = 0) -> None:
    """输出 JSON 并退出。"""
    print(json.dumps(data, ensure_ascii=False, indent=2))
    sys.exit(exit_code)


# ========== 机票命令 ==========


def cmd_flight_lookup(args: argparse.Namespace) -> None:
    """查询机场信息。"""
    from qvxianjiuguo.flight.search import lookup_airport

    airport = lookup_airport(args.city)
    if airport:
        _output({
            "success": True,
            "airports": [{
                "code": airport.code,
                "name": airport.name,
                "city": airport.city,
                "province": airport.province,
                "region": airport.region,
            }]
        })
    else:
        _output({"success": False, "error": f"未找到机场: {args.city}"})


def cmd_flight_nearby(args: argparse.Namespace) -> None:
    """查询附近机场。"""
    from qvxianjiuguo.flight.search import get_nearby_airports, lookup_airport

    airport = lookup_airport(args.airport)
    if not airport:
        _output({"success": False, "error": f"未找到机场: {args.airport}"})
        return

    nearby = get_nearby_airports(airport.code, args.range)
    _output({
        "success": True,
        "airport": airport.code,
        "range_km": args.range,
        "airports": nearby
    })


def cmd_flight_search(args: argparse.Namespace) -> None:
    """机票模糊搜索。"""
    from qvxianjiuguo.chrome_launcher import ensure_chrome, has_display
    from qvxianjiuguo.xhs.cdp import Browser
    from qvxianjiuguo.flight.search import (
        search_flights,
        smart_route_planning,
        SearchParams,
    )
    from qvxianjiuguo.flight.platforms import get_platform_handler

    # 确保 Chrome 运行
    if not ensure_chrome(port=args.port, headless=not has_display()):
        _output({"success": False, "error": "无法启动 Chrome"}, exit_code=2)
        return

    browser = Browser(host=args.host, port=args.port)
    browser.connect()
    page = browser.get_or_create_page()

    try:
        skip_first_nav = False
        
        # 默认使用去哪儿平台，检查登录状态
        if args.platform == "qunar":
            handler = get_platform_handler(args.platform)
            if handler:
                # 导航到平台首页检查登录
                page.navigate(handler.url)
                page.wait_for_load()
                import time
                time.sleep(2)  # 等待动态内容加载
                logged_in = handler.check_login(page)
                if not logged_in:
                    _output({
                        "success": False,
                        "error": "去哪儿平台未登录",
                        "login_required": True,
                        "login_method": "cookie",
                        "login_url": handler.login_url,
                        "message": "需要登录去哪儿平台才能搜索",
                        "next_action": "save_cookie",
                        "workflow": [
                            "1. 在打开的 Chrome 浏览器中手动登录去哪儿",
                            "2. 执行: qvxian flight-save-cookie --platform qunar",
                            "3. 重新执行搜索命令"
                        ],
                        "hint": "推荐使用小号登录，避免主账号被封"
                    }, exit_code=1)
                    return
                # 已登录，跳过后续第一次导航
                skip_first_nav = True

        params = SearchParams(
            departure=args.departure,
            destination=args.destination,
            date=args.date,
            date_end=args.date_end,
            platform=args.platform,
            departure_range=args.departure_range,
            destination_range=args.destination_range,
            top_n=args.top_n,
            direct_only=args.direct_only,
        )

        result = search_flights(page, params, skip_first_navigation=skip_first_nav)

        if result.success:
            # 计算智能路线规划
            planning = smart_route_planning(result, args.departure, args.destination)

            # 构建航班列表，添加排序序号和辅助字段
            flights_output = []
            for i, f in enumerate(result.flights, 1):
                flight_dict = f.__dict__
                flight_dict["rank"] = i  # 添加排名
                
                # 生成航班类型文本
                if f.is_direct:
                    flight_dict["flight_type"] = "直飞"
                    flight_dict["is_direct_text"] = "直飞"
                else:
                    transfer = f.transfer_info if f.transfer_info else "需中转"
                    flight_dict["flight_type"] = f"中转({transfer})"
                    flight_dict["is_direct_text"] = f"中转({transfer})"
                
                # 添加完整航线信息
                flight_dict["route"] = f"{f.departure_code}→{f.arrival_code}"
                flight_dict["time_range"] = f"{f.departure_time}-{f.arrival_time}"
                
                flights_output.append(flight_dict)

            output = {
                "success": True,
                "flights": flights_output,
                "departure_airports": result.departure_airports,
                "arrival_airports": result.arrival_airports,
                "total_combinations": result.total_combinations,
                "searched_combinations": result.searched_combinations,
                "platform": result.platform,
                "direct_only": params.direct_only,  # 添加是否只搜索直飞
                "total_flights_found": len(result.flights),
                "sort_rule": "直飞优先，然后按价格从低到高",
                "smart_planning": {
                    "success": planning.get("success", False),
                    "cheapest_total_cost": planning.get("cheapest", {}).get("total_cost", 0) if planning.get("cheapest") else 0,
                } if planning.get("success") else {}
            }
            _output(output)
        else:
            _output({"success": False, "error": result.error})
    finally:
        browser.close_page(page)
        browser.close()


def cmd_flight_check_login(args: argparse.Namespace) -> None:
    """检查机票平台登录状态。"""
    from qvxianjiuguo.chrome_launcher import ensure_chrome, has_display
    from qvxianjiuguo.xhs.cdp import Browser
    from qvxianjiuguo.flight.platforms import get_platform_handler

    handler = get_platform_handler(args.platform)
    if not handler:
        _output({"success": False, "error": f"未知平台: {args.platform}"})
        return

    if not ensure_chrome(port=args.port, headless=not has_display()):
        _output({"success": False, "error": "无法启动 Chrome"}, exit_code=2)
        return

    browser = Browser(host=args.host, port=args.port)
    browser.connect()
    page = browser.get_or_create_page()

    try:
        page.navigate(handler.url)
        import time
        time.sleep(2)
        logged_in = handler.check_login(page)
        _output({
            "success": True, 
            "platform": args.platform, 
            "platform_name": handler.name,
            "logged_in": logged_in,
            "login_url": handler.login_url if not logged_in else None
        })
    finally:
        browser.close_page(page)
        browser.close()


def get_cookie_file_path(platform: str) -> str:
    """获取 cookie 文件路径"""
    import os
    # 存储在用户主目录下的 .qvxian 文件夹
    cookie_dir = os.path.join(os.path.expanduser("~"), ".qvxian")
    os.makedirs(cookie_dir, exist_ok=True)
    return os.path.join(cookie_dir, f"{platform}_cookies.json")


def cmd_flight_save_cookie(args: argparse.Namespace) -> None:
    """从当前浏览器保存 cookie 到本地文件。
    
    使用方法：
    1. 启动 Chrome: python -m qvxianjiuguo.chrome_launcher
    2. 在 Chrome 中手动登录去哪儿（处理滑块验证等）
    3. 运行: qvxian flight-save-cookie --platform qunar
    """
    from qvxianjiuguo.chrome_launcher import ensure_chrome, has_display
    from qvxianjiuguo.xhs.cdp import Browser
    from qvxianjiuguo.flight.platforms import get_platform_handler
    import time

    handler = get_platform_handler(args.platform)
    if not handler:
        _output({"success": False, "error": f"未知平台: {args.platform}"})
        return

    if not ensure_chrome(port=args.port, headless=not has_display()):
        _output({"success": False, "error": "无法启动 Chrome"}, exit_code=2)
        return

    browser = Browser(host=args.host, port=args.port)
    browser.connect()
    page = browser.get_or_create_page()

    try:
        # 先检查登录状态
        page.navigate(handler.url)
        time.sleep(2)
        
        logged_in = handler.check_login(page)
        if not logged_in:
            _output({
                "success": False,
                "error": "未检测到登录状态",
                "message": "请先在浏览器中手动登录，然后重新运行此命令",
                "login_url": handler.login_url
            }, exit_code=1)
            return

        # 提取 cookie
        cookies = page.evaluate(
            """(() => {
                const cookies = document.cookie.split(';').map(c => c.trim()).filter(c => c);
                const cookieObj = {};
                cookies.forEach(c => {
                    const [name, ...valueParts] = c.split('=');
                    cookieObj[name] = valueParts.join('=');
                });
                return cookieObj;
            })()"""
        )
        
        if not cookies:
            _output({
                "success": False,
                "error": "未找到 cookie"
            }, exit_code=1)
            return

        # 保存到文件
        import json
        cookie_file = get_cookie_file_path(args.platform)
        
        cookie_data = {
            "platform": args.platform,
            "platform_name": handler.name,
            "cookies": cookies,
            "saved_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(cookie_file, 'w', encoding='utf-8') as f:
            json.dump(cookie_data, f, ensure_ascii=False, indent=2)
        
        # 显示关键 cookie 名称
        key_cookies = ['QN1', 'QN2', 'QN5', 'QN277', '_vi', '_q', '_t']
        found_keys = [k for k in key_cookies if k in cookies]
        
        _output({
            "success": True,
            "message": f"Cookie 已保存到: {cookie_file}",
            "platform": args.platform,
            "platform_name": handler.name,
            "cookie_count": len(cookies),
            "key_cookies_found": found_keys,
            "file_path": cookie_file
        })
        
    except Exception as e:
        _output({"success": False, "error": str(e)}, exit_code=1)
    finally:
        browser.close_page(page)
        browser.close()


def cmd_flight_load_cookie(args: argparse.Namespace) -> None:
    """从本地文件加载 cookie 到浏览器。
    
    使用方法：
    qvxian flight-load-cookie --platform qunar
    """
    from qvxianjiuguo.chrome_launcher import ensure_chrome, has_display
    from qvxianjiuguo.xhs.cdp import Browser
    from qvxianjiuguo.flight.platforms import get_platform_handler
    import time
    import os

    handler = get_platform_handler(args.platform)
    if not handler:
        _output({"success": False, "error": f"未知平台: {args.platform}"})
        return

    # 读取 cookie 文件
    cookie_file = get_cookie_file_path(args.platform)
    if not os.path.exists(cookie_file):
        _output({
            "success": False,
            "error": f"Cookie 文件不存在: {cookie_file}",
            "message": "请先运行 flight-save-cookie 命令保存 cookie"
        }, exit_code=1)
        return

    try:
        import json
        with open(cookie_file, 'r', encoding='utf-8') as f:
            cookie_data = json.load(f)
    except Exception as e:
        _output({
            "success": False,
            "error": f"读取 cookie 文件失败: {e}"
        }, exit_code=1)
        return

    cookies = cookie_data.get("cookies", {})
    if not cookies:
        _output({
            "success": False,
            "error": "Cookie 文件中没有有效的 cookie"
        }, exit_code=1)
        return

    if not ensure_chrome(port=args.port, headless=not has_display()):
        _output({"success": False, "error": "无法启动 Chrome"}, exit_code=2)
        return

    browser = Browser(host=args.host, port=args.port)
    browser.connect()
    page = browser.get_or_create_page()

    try:
        # 先导航到目标网站（设置 cookie 需要在同域下）
        page.navigate(handler.url)
        time.sleep(1)
        
        # 设置 cookie
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
        
        result = page.evaluate(
            f"""(() => {{
                document.cookie = {json.dumps(cookie_str)};
                return {{ success: true, set_count: {len(cookies)} }};
            }})()"""
        )
        
        time.sleep(1)
        
        # 验证登录状态
        logged_in = handler.check_login(page)
        
        _output({
            "success": True,
            "message": "Cookie 已加载" + ("，登录成功" if logged_in else "，但未检测到登录状态"),
            "platform": args.platform,
            "logged_in": logged_in,
            "cookie_count": len(cookies),
            "saved_at": cookie_data.get("saved_at")
        })
        
    except Exception as e:
        _output({"success": False, "error": str(e)}, exit_code=1)
    finally:
        browser.close_page(page)
        browser.close()


# ========== 参数解析 ==========


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qvxian",
        description="曲线救国 - 机票模糊搜索工具",
    )

    # 全局选项
    parser.add_argument("--host", default="127.0.0.1", help="Chrome 调试主机")
    parser.add_argument("--port", type=int, default=9222, help="Chrome 调试端口")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # flight-lookup
    sub = subparsers.add_parser("flight-lookup", help="查询机场信息（城市名或机场代码）")
    sub.add_argument("--city", required=True, help="城市名或机场代码")
    sub.set_defaults(func=cmd_flight_lookup)

    # flight-nearby
    sub = subparsers.add_parser("flight-nearby", help="查询机场周围一定范围内的机场")
    sub.add_argument("--airport", required=True, help="机场代码（如 CKG）")
    sub.add_argument("--range", type=int, default=300, help="搜索范围（km），默认 300")
    sub.set_defaults(func=cmd_flight_nearby)

    # flight-search
    sub = subparsers.add_parser("flight-search", help="机票模糊搜索（支持附近机场组合）")
    sub.add_argument("--departure", required=True, help="出发地（城市或机场代码）")
    sub.add_argument("--destination", required=True, help="目的地（城市或机场代码）")
    sub.add_argument("--date", required=True, help="出发日期（YYYY-MM-DD）")
    sub.add_argument("--date-end", help="结束日期（日期范围搜索）")
    sub.add_argument("--platform", default="qunar", 
                     choices=["qunar", "ctrip", "fliggy", "ly", "all"],
                     help="搜索平台，默认去哪儿（qunar）")
    sub.add_argument("--departure-range", type=int, default=300, 
                     help="出发地搜索范围（km），0=仅本城市，可选：0/200/250/300/350/500，默认300")
    sub.add_argument("--destination-range", type=int, default=300, 
                     help="目的地搜索范围（km），0=仅本城市，可选：0/200/250/300/350/500，默认300")
    sub.add_argument("--top-n", type=int, default=10, help="每个组合返回的航班数量")
    sub.add_argument("--direct-only", action="store_true", default=True, help="只搜索直飞航班（默认启用）")
    sub.add_argument("--no-direct-only", dest="direct_only", action="store_false", help="包含中转航班")
    sub.set_defaults(func=cmd_flight_search)

    # flight-check-login
    sub = subparsers.add_parser("flight-check-login", help="检查机票平台登录状态")
    sub.add_argument("--platform", required=True,
                     choices=["qunar", "ctrip", "fliggy", "ly"],
                     help="平台：qunar/ctrip/fliggy/ly")
    sub.set_defaults(func=cmd_flight_check_login)

    # flight-save-cookie
    sub = subparsers.add_parser("flight-save-cookie", 
                                help="从当前浏览器保存 cookie 到本地（推荐使用此方式登录）")
    sub.add_argument("--platform", required=True,
                     choices=["qunar", "ctrip", "fliggy", "ly"],
                     help="平台：qunar/ctrip/fliggy/ly")
    sub.set_defaults(func=cmd_flight_save_cookie)

    # flight-load-cookie
    sub = subparsers.add_parser("flight-load-cookie", 
                                help="从本地加载 cookie 到浏览器")
    sub.add_argument("--platform", required=True,
                     choices=["qunar", "ctrip", "fliggy", "ly"],
                     help="平台：qunar/ctrip/fliggy/ly")
    sub.set_defaults(func=cmd_flight_load_cookie)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()