"""
美团优惠领取工具（meituan-coupon-get-tool）- 用户领券记录查询脚本
接口：POST /eds/standard/equity/pkg/claw/result/query
用法：
  python query.py --token <user_token> --dates 20260323         # 查单天
  python query.py --token <user_token> --dates 20260320,20260323 # 查区间（含首尾）
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ── 常量 ──────────────────────────────────────────────────────────────
BASE_URL    = "https://peppermall.meituan.com"
QUERY_PATH  = "/eds/standard/equity/pkg/claw/result/query"
# 任务类型 key（一期固定为 coupon）
TASK_TYPE   = "coupon"

CONFIG_FILE  = Path(__file__).parent / "config.json"


def _resolve_history_file() -> Path:
    """
    跨平台确定领券历史存储路径，优先级：
    1. 环境变量 XIAOMEI_COUPON_HISTORY_FILE（适合沙箱/其他 Agent 隔离）
    2. ~/.xiaomei-workspace/mt_ods_coupon_history.json（macOS/Linux/Windows 统一路径）
    """
    env_path = os.environ.get("XIAOMEI_COUPON_HISTORY_FILE")
    if env_path:
        return Path(env_path)
    return Path.home() / ".xiaomei-workspace" / "mt_ods_coupon_history.json"


HISTORY_FILE = _resolve_history_file()


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        print(json.dumps({
            "success": False,
            "error": "CONFIG_NOT_FOUND",
            "message": f"配置文件不存在：{CONFIG_FILE}"
        }, ensure_ascii=False))
        sys.exit(1)
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_history() -> dict:
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_date_range(date_str: str) -> list[str]:
    """
    解析日期参数，返回日期列表（YYYYMMDD 格式）
    - 单日期："20260323" → ["20260323"]
    - 区间："20260320,20260323" → ["20260320", "20260321", "20260322", "20260323"]
    """
    parts = [p.strip() for p in date_str.split(",")]
    if len(parts) == 1:
        return [parts[0]]
    elif len(parts) == 2:
        start = datetime.strptime(parts[0], "%Y%m%d")
        end = datetime.strptime(parts[1], "%Y%m%d")
        if start > end:
            start, end = end, start
        result = []
        cur = start
        while cur <= end:
            result.append(cur.strftime("%Y%m%d"))
            cur += timedelta(days=1)
        return result
    else:
        print(json.dumps({
            "success": False,
            "error": "INVALID_DATE_FORMAT",
            "message": f"日期格式错误：{date_str}，请输入单个日期（20260323）或区间（20260320,20260323）"
        }, ensure_ascii=False))
        sys.exit(1)


def get_redeem_codes_by_dates(sub_channel_code: str, user_token: str, dates: list[str]) -> list[str]:
    """
    从历史文件中获取指定渠道、用户、日期范围内的 coupon 兑换码列表。
    路径：history[subChannelCode][user_token][date][TASK_TYPE]
    """
    history = load_history()
    token_data = history.get(sub_channel_code, {}).get(user_token, {})
    codes = []
    for date in dates:
        date_codes = token_data.get(date, {}).get(TASK_TYPE, [])
        codes.extend(date_codes)
    # 去重，保持顺序
    seen = set()
    unique_codes = []
    for c in codes:
        if c not in seen:
            seen.add(c)
            unique_codes.append(c)
    return unique_codes


def format_timestamp_ms(ts_ms: int) -> str:
    if not ts_ms:
        return "-"
    try:
        return datetime.fromtimestamp(ts_ms / 1000).strftime("%Y-%m-%d")
    except Exception:
        return str(ts_ms)


def format_coupon(equity: dict) -> dict:
    price_limit_type = equity.get("priceLimitType", 1)
    price_limit_amount_str = equity.get("priceLimitAmountYuanStr", "")
    discount_amount_str = equity.get("discountAmountYuanStr", "")

    if price_limit_type == 1:
        use_condition = "无门槛"
    elif price_limit_type in (2, 3):
        use_condition = f"满{price_limit_amount_str}元可用"
    else:
        use_condition = f"满{price_limit_amount_str}元可用" if price_limit_amount_str else "-"

    return {
        "name": equity.get("userEquityName", "-"),
        "discount_amount": discount_amount_str,
        "use_condition": use_condition,
        "valid_start": format_timestamp_ms(equity.get("beginTime")),
        "valid_end": format_timestamp_ms(equity.get("endTime")),
        "issue_time": format_timestamp_ms(equity.get("issueTime")),
        "jump_url": equity.get("jumpUrl", ""),
        "user_equity_id": equity.get("userEquityId", "")
    }


def main():
    parser = argparse.ArgumentParser(description="美团权益领取记录查询")
    parser.add_argument("--token", required=True, help="用户 user_token")
    parser.add_argument("--dates", required=True,
                        help="查询日期，单天如 20260323，区间如 20260320,20260323")
    args = parser.parse_args()

    import httpx

    config = load_config()
    sub_channel_code = config.get("subChannelCode")
    if not sub_channel_code:
        print(json.dumps({
            "success": False,
            "error": "CONFIG_INVALID",
            "message": "配置文件缺少 subChannelCode 字段"
        }, ensure_ascii=False))
        sys.exit(1)

    # 解析日期范围
    dates = get_date_range(args.dates)

    # 从历史文件获取兑换码
    redeem_codes = get_redeem_codes_by_dates(sub_channel_code, args.token, dates)

    if not redeem_codes:
        print(json.dumps({
            "success": True,
            "code": 0,
            "query_dates": dates,
            "redeem_code_count": 0,
            "records": [],
            "message": f"在 {dates[0]}{'~' + dates[-1] if len(dates) > 1 else ''} 期间未找到领取记录（本地无兑换码存档）"
        }, ensure_ascii=False))
        return

    # 构造请求
    body = {
        "subChannelCode": sub_channel_code,
        "token": args.token,
        "equityPkgRedeemCodeList": redeem_codes
    }

    try:
        resp = httpx.post(
            BASE_URL + QUERY_PATH,
            json=body,
            headers={"Content-Type": "application/json"},
            timeout=15,
            verify=True
        )
        resp_data = resp.json()
    except httpx.TimeoutException:
        print(json.dumps({
            "success": False,
            "error": "TIMEOUT",
            "message": "请求超时，请稍后重试"
        }, ensure_ascii=False))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": "NETWORK_ERROR",
            "message": f"网络异常：{str(e)}"
        }, ensure_ascii=False))
        sys.exit(1)

    code = resp_data.get("code")
    message = resp_data.get("message", "")
    data = resp_data.get("data", [])

    if code == 0:
        # 格式化每条记录
        records = []
        for item in (data or []):
            redeem_code = item.get("equityRedeemCode", "")
            success_list = item.get("successEquityList", [])
            records.append({
                "redeem_code": redeem_code,
                "coupon_count": len(success_list),
                "coupons": [format_coupon(e) for e in success_list]
            })

        print(json.dumps({
            "success": True,
            "code": 0,
            "query_dates": dates,
            "redeem_code_count": len(redeem_codes),
            "record_count": len(records),
            "records": records
        }, ensure_ascii=False))
    else:
        print(json.dumps({
            "success": False,
            "code": code,
            "error": "API_ERROR",
            "message": f"查询失败（错误码：{code}，{message}）"
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
