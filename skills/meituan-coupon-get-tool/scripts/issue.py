"""
美团优惠领取工具（meituan-coupon-get-tool）- 权益包发放脚本
接口：POST /eds/standard/equity/pkg/issue/claw
用法：python issue.py --token <user_token> --phone-masked <phone_masked>
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ── 常量 ──────────────────────────────────────────────────────────────
BASE_URL   = "https://peppermall.meituan.com"
ISSUE_PATH = "/eds/standard/equity/pkg/issue/claw"
# 任务类型 key（一期固定为 coupon，二期扩展时新增）
TASK_TYPE  = "coupon"

# subChannelCode 存放在独立配置文件中，不硬编码在此脚本
CONFIG_FILE = Path(__file__).parent / "config.json"


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


# 兑换码历史存储文件（文件名独立，避免与其他应用冲突）
HISTORY_FILE = _resolve_history_file()


def load_config() -> dict:
    """加载 config.json，读取 subChannelCode 等敏感配置"""
    if not CONFIG_FILE.exists():
        print(json.dumps({
            "success": False,
            "error": "CONFIG_NOT_FOUND",
            "message": f"配置文件不存在：{CONFIG_FILE}，请联系管理员初始化"
        }, ensure_ascii=False))
        sys.exit(1)
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_history() -> dict:
    """加载本地兑换码历史文件"""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_history(data: dict):
    """保存兑换码历史文件"""
    import stat
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # 仅当前用户可读写（0600），防止其他用户读取领券历史
    try:
        os.chmod(HISTORY_FILE, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass  # Windows 不支持 chmod，静默跳过


def gen_redeem_code(user_token: str, phone_masked: str, date_str: str) -> str:
    """
    生成当天领券唯一键
    规则：MD5(user_token + "_" + phone_masked + "_" + YYYYMMDD)

    说明：phone_masked 是脱敏手机号（如 152****0460），不同用户去掉中间4位后
    可能产生碰撞，因此在 MD5 原始串中额外加入 user_token 以保证唯一性。
    """
    raw = f"{user_token}_{phone_masked}_{date_str}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def save_redeem_code(sub_channel_code: str, user_token: str, date_str: str, redeem_code: str):
    """
    将兑换码写入历史文件。
    结构：
    {
      "<subChannelCode>": {
        "<user_token>": {
          "<YYYYMMDD>": {
            "coupon": ["code1", "code2"],   ← 一期；二期可新增其他 task_type key
            ...
          }
        }
      }
    }
    每次写入前检查是否已存在，避免重复追加。
    """
    history = load_history()
    channel_data = history.setdefault(sub_channel_code, {})
    token_data = channel_data.setdefault(user_token, {})
    date_data = token_data.setdefault(date_str, {})
    codes = date_data.setdefault(TASK_TYPE, [])
    if redeem_code not in codes:
        codes.append(redeem_code)
    save_history(history)


def format_timestamp_ms(ts_ms: int) -> str:
    """毫秒时间戳转可读日期"""
    if not ts_ms:
        return "-"
    try:
        return datetime.fromtimestamp(ts_ms / 1000).strftime("%Y-%m-%d")
    except Exception:
        return str(ts_ms)


def format_coupon(equity: dict) -> dict:
    """格式化单张券信息"""
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
    parser = argparse.ArgumentParser(description="美团权益包发放")
    parser.add_argument("--token", required=True, help="用户 user_token")
    parser.add_argument("--phone-masked", required=True, help="脱敏手机号（用于生成 redeem_code）")
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

    # 获取当天领券唯一键：优先复用历史记录，无则新生成（不提前写入，发券成功后再写）
    today = datetime.now().strftime("%Y%m%d")
    history = load_history()
    existing_codes = (
        history.get(sub_channel_code, {})
               .get(args.token, {})
               .get(today, {})
               .get(TASK_TYPE, [])
    )
    if existing_codes:
        # 当天已有领取记录，复用最后一个 equityPkgRedeemCode（避免重复生成）
        redeem_code = existing_codes[-1]
    else:
        # 当天首次领取，生成新的 equityPkgRedeemCode（发券成功后再写入历史文件）
        redeem_code = gen_redeem_code(args.token, args.phone_masked, today)

    # 构造请求
    body = {
        "subChannelCode": sub_channel_code,
        "token": args.token,
        "equityPkgRedeemCode": redeem_code
    }

    try:
        resp = httpx.post(
            BASE_URL + ISSUE_PATH,
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
    data = resp_data.get("data")

    # 错误码映射
    ERROR_MAP = {
        4009: ("ACTIVITY_ENDED", "活动已结束，暂时无法领取"),
        4010: ("ALREADY_RECEIVED", "你今天已经通过小美领取过美团权益了，明天再来哦～"),
        4011: ("QUOTA_EXHAUSTED", "抱歉，本次活动权益已发放完毕，下次早点来哦～"),
    }

    if code == 0:
        # 发券成功（code=0），保存兑换码到历史文件（首次领取时才写，复用历史 code 不重复写）
        is_first_issue = not bool(existing_codes)
        if is_first_issue:
            save_redeem_code(sub_channel_code, args.token, today, redeem_code)

        success_list = data.get("successEquityList", [])
        formatted_coupons = [format_coupon(e) for e in success_list]

        print(json.dumps({
            "success": True,
            "code": 0,
            "is_first_issue": is_first_issue,
            # is_first_issue=true  → 本次首次领取成功，向用户展示"🎉 领取成功！"
            # is_first_issue=false → 今日已领取过，不可重复领取，向用户展示：
            #   "⚠️ 今天已经领取过了，不能重复领取。以下是上次领取的券信息：" + coupons
            "redeem_code": redeem_code,
            "request_id": data.get("requestId", ""),
            "issue_status": data.get("equityPkgIssueStatus"),
            "coupon_count": len(formatted_coupons),
            "coupons": formatted_coupons
        }, ensure_ascii=False))

    elif code in ERROR_MAP:
        err_key, err_msg = ERROR_MAP[code]
        print(json.dumps({
            "success": False,
            "code": code,
            "error": err_key,
            "message": err_msg
        }, ensure_ascii=False))

    else:
        print(json.dumps({
            "success": False,
            "code": code,
            "error": "SYSTEM_ERROR",
            "message": f"系统繁忙，请稍后重试（错误码：{code}，{message}）"
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
