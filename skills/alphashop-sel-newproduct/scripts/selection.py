#!/usr/bin/env python3
"""
1688遨虾AI选品 - 新品报告生成脚本

Usage:
    python3 selection.py report --keyword "phone" --platform "amazon" --country "US"
    python3 selection.py report --keyword "yoga pants" --platform "amazon" --country "US" --listing-time "90" --min-price 15 --max-price 50
"""

import argparse
import json
import sys
import os
import time
import requests
import jwt
from datetime import datetime
from typing import Optional, Dict, Any

# API配置
API_BASE_URL = "https://api.alphashop.cn"
REPORT_ENDPOINT = f"{API_BASE_URL}/opp.selection.newproduct.report/1.0"
KEYWORD_SEARCH_ENDPOINT = f"{API_BASE_URL}/opp.selection.keyword.search/1.0"

# 平台和国家配置
PLATFORMS = ["amazon", "tiktok"]
AMAZON_COUNTRIES = ["US", "UK", "ES", "FR", "DE", "IT", "CA", "JP"]
TIKTOK_COUNTRIES = ["ID", "VN", "MY", "TH", "PH", "US", "SG", "BR", "MX", "GB", "ES", "FR", "DE", "IT", "JP"]


def print_credential_help():
    """打印凭证获取帮助信息"""
    print("\n" + "="*70)
    print("🔐 需要 AlphaShop API 凭证")
    print("="*70)
    print("\n本 skill 需要以下凭证才能使用：")
    print("  • ALPHASHOP_ACCESS_KEY  - API 访问密钥")
    print("  • ALPHASHOP_SECRET_KEY  - API 密钥\n")

    print("📋 如何获取凭证：")
    print("-" * 70)
    print("1. 联系 AlphaShop/遨虾 平台获取 API 凭证")
    print("   - 平台网址：https://www.alphashop.cn （或相关平台）")
    print("   - 如果你是内部用户，请联系平台管理员\n")

    print("2. 获取凭证后，有两种配置方式：\n")

    print("   方式A：通过环境变量配置（临时使用）")
    print("   " + "-" * 66)
    print("   export ALPHASHOP_ACCESS_KEY='你的AccessKey'")
    print("   export ALPHASHOP_SECRET_KEY='你的SecretKey'\n")

    print("   方式B：通过 OpenClaw 配置（推荐）")
    print("   " + "-" * 66)
    print("   编辑 OpenClaw 配置文件，添加：")
    print("   {")
    print("     skills: {")
    print("       entries: {")
    print('         "alphashop-sel-newproduct": {')
    print("           env: {")
    print('             ALPHASHOP_ACCESS_KEY: "你的AccessKey",')
    print('             ALPHASHOP_SECRET_KEY: "你的SecretKey"')
    print("           }")
    print("         }")
    print("       }")
    print("     }")
    print("   }\n")

    print("3. 配置完成后，重新运行命令即可\n")
    print("="*70 + "\n")


def get_jwt_token():
    """生成 JWT token 用于 AlphaShop API 认证"""
    ak = os.environ.get("ALPHASHOP_ACCESS_KEY", "").strip()
    sk = os.environ.get("ALPHASHOP_SECRET_KEY", "").strip()

    if not ak or not sk:
        print_credential_help()

        # 交互式询问用户是否要输入凭证
        print("\n请选择：")
        print("  1) 手动输入凭证（本次有效）")
        print("  2) 退出")
        print()

        try:
            choice = input("请选择 [1-2]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已取消")
            sys.exit(0)

        if choice == "1":
            try:
                if not ak:
                    ak = input("请输入 ALPHASHOP_ACCESS_KEY: ").strip()
                if not sk:
                    sk = input("请输入 ALPHASHOP_SECRET_KEY: ").strip()

                if not ak or not sk:
                    raise ValueError("凭证不能为空")
            except (EOFError, KeyboardInterrupt):
                print("\n已取消")
                sys.exit(0)
        elif choice == "2":
            print("退出")
            sys.exit(0)
        else:
            print("❌ 无效选择")
            sys.exit(1)

    if not ak or not sk:
        missing = []
        if not ak:
            missing.append("ALPHASHOP_ACCESS_KEY")
        if not sk:
            missing.append("ALPHASHOP_SECRET_KEY")
        raise ValueError(f"缺少必需的环境变量: {', '.join(missing)}")

    try:
        current_time = int(time.time())
        expired_at = current_time + 1800  # 30分钟后过期
        not_before = current_time - 5

        token = jwt.encode(
            payload={
                "iss": ak,
                "exp": expired_at,
                "nbf": not_before
            },
            key=sk,
            algorithm="HS256",
            headers={"alg": "HS256"}
        )

        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return token
    except Exception as e:
        raise ValueError(f"生成 JWT token 失败: {e}")


def search_keywords(
    keyword: str,
    platform: str,
    region: str,
    listing_time: Optional[str] = None,
) -> Dict[str, Any]:
    """
    搜索关键词并返回相关关键词列表及市场数据

    Args:
        keyword: 查询关键词（只支持单个关键词）
        platform: 平台（amazon/tiktok）
        region: 国家代码
        listing_time: 商品上架时间范围（"90"或"180"，默认180）

    Returns:
        API响应数据
    """
    # 验证参数
    if platform not in PLATFORMS:
        raise ValueError(f"平台必须是: {', '.join(PLATFORMS)}")

    if platform == "amazon" and region not in AMAZON_COUNTRIES:
        raise ValueError(f"Amazon平台支持的国家: {', '.join(AMAZON_COUNTRIES)}")

    if platform == "tiktok" and region not in TIKTOK_COUNTRIES:
        raise ValueError(f"TikTok平台支持的国家: {', '.join(TIKTOK_COUNTRIES)}")

    if listing_time and listing_time not in ["90", "180"]:
        raise ValueError("listing_time 只能是 '90' 或 '180'")

    # 构建请求体
    payload = {
        "platform": platform,
        "region": region,
        "keyword": keyword,
    }

    # 添加可选参数
    if listing_time:
        payload["listingTime"] = listing_time

    # 发送请求
    try:
        # 获取 JWT token
        token = get_jwt_token()

        print(f"→ 正在搜索关键词: {keyword} @ {platform.upper()} {region}")
        print(f"→ 请求中... (响应时间约10秒内)")

        response = requests.post(
            KEYWORD_SEARCH_ENDPOINT,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            timeout=30
        )
        response.raise_for_status()

        result = response.json()

        # 检查业务错误
        success = result.get("success")
        code = result.get("code")

        # 如果有success字段，优先检查
        if success is not None and not success:
            msg = result.get("msg", "未知错误")
            raise Exception(f"业务错误 [{code}]: {msg}")
        # 否则检查code字段
        elif code and code != "SUCCESS":
            msg = result.get("msg", "未知错误")
            raise Exception(f"业务错误 [{code}]: {msg}")

        return result

    except requests.exceptions.Timeout:
        raise Exception("请求超时，请稍后重试")
    except requests.exceptions.RequestException as e:
        raise Exception(f"网络请求失败: {str(e)}")


def generate_report(
    keyword: str,
    platform: str,
    country: str,
    listing_time: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_volume: Optional[int] = None,
    max_volume: Optional[int] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
) -> Dict[str, Any]:
    """
    生成新品选品报告

    Args:
        keyword: 关键词（必须是关键词查询API返回的关键词）
        platform: 平台（amazon/tiktok）
        country: 国家代码
        listing_time: 商品上架时间范围（"90"或"180"）
        min_price: 最低价格
        max_price: 最高价格
        min_volume: 最低月销量
        max_volume: 最高月销量
        min_rating: 最低评分
        max_rating: 最高评分

    Returns:
        API响应数据
    """
    # 验证参数
    if platform not in PLATFORMS:
        raise ValueError(f"平台必须是: {', '.join(PLATFORMS)}")

    if platform == "amazon" and country not in AMAZON_COUNTRIES:
        raise ValueError(f"Amazon平台支持的国家: {', '.join(AMAZON_COUNTRIES)}")

    if platform == "tiktok" and country not in TIKTOK_COUNTRIES:
        raise ValueError(f"TikTok平台支持的国家: {', '.join(TIKTOK_COUNTRIES)}")

    if listing_time and listing_time not in ["90", "180"]:
        raise ValueError("listing_time 只能是 '90' 或 '180'")

    # 构建请求体
    payload = {
        "productKeyword": keyword,
        "targetPlatform": platform,
        "targetCountry": country,
    }

    # 添加可选参数
    if listing_time:
        payload["listingTime"] = listing_time
    if min_price is not None:
        payload["minPrice"] = min_price
    if max_price is not None:
        payload["maxPrice"] = max_price
    if min_volume is not None:
        payload["minVolume"] = min_volume
    if max_volume is not None:
        payload["maxVolume"] = max_volume
    if min_rating is not None:
        payload["minRating"] = min_rating
    if max_rating is not None:
        payload["maxRating"] = max_rating

    # 发送请求
    try:
        # 获取 JWT token（在打印其他信息前检查凭证）
        token = get_jwt_token()

        print(f"→ 正在生成报告: {keyword} @ {platform.upper()} {country}")
        print(f"→ 请求中... (响应时间约几十秒)")

        response = requests.post(
            REPORT_ENDPOINT,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            timeout=120  # 设置2分钟超时
        )
        response.raise_for_status()

        result = response.json()

        # 检查业务错误（兼容不同的响应格式）
        if "resultCode" in result:
            # 新格式：{"resultCode": "xxx", "result": {...}}
            result_code = result.get("resultCode")
            if result_code != "SUCCESS":
                raise Exception(f"业务错误 [{result_code}]: 接口返回失败")
        elif not result.get("success"):
            # 旧格式：{"success": false, "code": "xxx", "msg": "xxx"}
            code = result.get("code", "UNKNOWN")
            msg = result.get("msg", "未知错误")
            raise Exception(f"业务错误 [{code}]: {msg}")

        return result

    except requests.exceptions.Timeout:
        raise Exception("请求超时，请稍后重试")
    except requests.exceptions.RequestException as e:
        raise Exception(f"网络请求失败: {str(e)}")


def format_number(num_str: str) -> str:
    """格式化数字字符串"""
    if "w+" in num_str:
        return num_str
    try:
        num = float(num_str.replace(",", ""))
        if num >= 10000:
            return f"{num/10000:.1f}w+"
        return f"{num:,.0f}"
    except:
        return num_str


def print_market_summary(data: Dict[str, Any]):
    """打印市场分析摘要"""
    summary_data = data.get("keywordSummary", {})

    print("\n" + "="*60)
    print("市场分析")
    print("="*60)

    # 市场评级
    level_detail = summary_data.get("keywordLevelDetail", {})
    level_emoji = {
        "BEST": "🌟",
        "GOOD": "✅",
        "MEDIUM": "🤔",
        "BAD": "❌"
    }
    level = level_detail.get("valueLevel", "")
    emoji = level_emoji.get(level, "")
    print(f"\n市场评级: {emoji}{level_detail.get('text', '')} ({level})")
    print(f"评级说明: {level_detail.get('valueLevelDesc', '')}")

    # 关键指标
    indexes = summary_data.get("keywordIndexesInfo", {})
    if indexes:
        print(f"\n机会分: {indexes.get('oppScore', '')} ({indexes.get('oppScoreDesc', '')})")

        print("\n📊 关键指标:")

        # 销售数据
        sales_info = indexes.get("salesInfo", {})
        if sales_info:
            sold_cnt = sales_info.get("soldCnt30d", {})
            sold_amt = sales_info.get("soldAmt30d", {})

            cnt_val = sold_cnt.get("value", "")
            cnt_growth = sold_cnt.get("growthRate", {})
            cnt_direction = cnt_growth.get("direction", "")
            cnt_rate = cnt_growth.get("value", "")
            cnt_arrow = "↑" if cnt_direction == "UP" else "↓" if cnt_direction == "DOWN" else ""

            amt_val = sold_amt.get("value", {}).get("amountWithSymbol", "")
            amt_growth = sold_amt.get("growthRate", {})
            amt_direction = amt_growth.get("direction", "")
            amt_rate = amt_growth.get("value", "")
            amt_arrow = "↑" if amt_direction == "UP" else "↓" if amt_direction == "DOWN" else ""

            print(f"- 30天销量: {cnt_val} ({cnt_arrow} {cnt_rate})")
            print(f"- 30天销售额: {amt_val} ({amt_arrow} {amt_rate})")

        # 价格
        profit_info = indexes.get("profitInfo", {})
        if profit_info:
            price_avg = profit_info.get("priceAvg", {})
            price_val = price_avg.get("value", {}).get("amountWithSymbol", "")
            price_level = price_avg.get("valueLevelDetail", {}).get("text", "")
            print(f"- 平均价格: {price_val} ({price_level})")

        # 需求
        demand_info = indexes.get("demandInfo", {})
        if demand_info:
            rank = demand_info.get("searchRank", "")
            rank_level = demand_info.get("searchRankLevel", "")
            print(f"- 搜索排名: {rank} ({rank_level})")

        # 供给
        supply_info = indexes.get("supplyInfo", {})
        if supply_info:
            item_count = supply_info.get("itemCount", {})
            print(f"- 在售商品数: {item_count.get('value', '')} ({item_count.get('valueLevelDetail', {}).get('text', '')})")

            cn_seller = supply_info.get("cnSellerPct", {})
            print(f"- 中国卖家占比: {cn_seller.get('value', '')} ({cn_seller.get('valueLevelDetail', {}).get('text', '')})")

            new_product = supply_info.get("newProductSalesPct", {})
            print(f"- 新品成交占比: {new_product.get('value', '')} ({new_product.get('valueLevelDetail', {}).get('text', '')})")

    # 市场总结
    summary_text = summary_data.get("summary", "")
    if summary_text:
        print("\n" + "-"*60)
        print("详细分析:")
        print("-"*60)
        # 简化输出，只显示前500字符
        if len(summary_text) > 500:
            print(summary_text[:500] + "...")
            print("\n[完整分析请查看JSON输出]")
        else:
            print(summary_text)


def print_keyword_list(data: Dict[str, Any]):
    """打印关键词搜索结果"""
    # 兼容两种响应格式
    result = data.get("result", {})
    result_data = result.get("data", {})
    keyword_list = result_data.get("keywordList", data.get("model", []))

    if not keyword_list:
        print("\n未找到相关关键词")
        return

    print("\n" + "="*60)
    print(f"相关关键词 ({len(keyword_list)})")
    print("="*60)

    for idx, kw in enumerate(keyword_list, 1):
        print(f"\n{idx}. {kw.get('keyword', '')} ({kw.get('keywordCn', '')})")
        print(f"   平台: {kw.get('platform', '').upper()}")
        print(f"   机会分: {kw.get('oppScore', '')} ({kw.get('oppScoreDesc', '')})")

        # 需求信息
        demand_info = kw.get("demandInfo", {})
        if demand_info:
            rank = demand_info.get("searchRank", "")
            rank_desc = demand_info.get("searchRankDesc", "")
            print(f"   {rank_desc}: {rank}")

        # 销售数据
        sales_info = kw.get("salesInfo", {})
        if sales_info:
            sold_cnt = sales_info.get("soldCnt30d", {})
            sold_amt = sales_info.get("soldAmt30d", {})

            cnt_val = sold_cnt.get("value", "")
            cnt_growth = sold_cnt.get("growthRate", {})
            cnt_direction = cnt_growth.get("direction", "")
            cnt_rate = cnt_growth.get("value", "")
            cnt_arrow = "↑" if cnt_direction == "UP" else "↓" if cnt_direction == "DOWN" else ""

            amt_val = sold_amt.get("value", {})
            amt_with_symbol = amt_val.get("amountWithSymbol", "") if isinstance(amt_val, dict) else amt_val
            amt_growth = sold_amt.get("growthRate", {})
            amt_direction = amt_growth.get("direction", "")
            amt_rate = amt_growth.get("value", "")
            amt_arrow = "↑" if amt_direction == "UP" else "↓" if amt_direction == "DOWN" else ""

            print(f"   30天销量: {cnt_val} ({cnt_arrow} {cnt_rate})")
            print(f"   30天销售额: {amt_with_symbol} ({amt_arrow} {amt_rate})")

        # 雷达分（简略显示）
        radar = kw.get("radar", {})
        if radar:
            property_list = radar.get("propertyList", [])
            if property_list:
                radar_str = ", ".join([f"{p.get('name', '')}: {p.get('value', '')}" for p in property_list[:3]])
                print(f"   雷达分: {radar_str}...")


def print_product_list(data: Dict[str, Any]):
    """打印新品列表"""
    products = data.get("productList", [])

    if not products:
        print("\n未找到符合条件的新品")
        return

    print("\n" + "="*60)
    print(f"推荐新品 ({len(products)})")
    print("="*60)

    for idx, product in enumerate(products, 1):
        print(f"\n{idx}. {product.get('title', '')}")
        print(f"   价格: {product.get('priceRange', '')}")
        print(f"   评分: {product.get('ratingRange', '')} ⭐ ({product.get('reviewCnt', 0)}条评论)")
        print(f"   30天销量: {product.get('soldCnt30d', '')}件")
        print(f"   上架: {product.get('onShelfDate', '')} ({product.get('onShelfDays', '')}天)")

        # SPU信息
        sp_info = product.get("spInfo", {})
        if sp_info:
            sp_cnt = sp_info.get("spItmCnt", 0)
            print(f"   同款: {sp_cnt}个商品")

        print(f"   链接: {product.get('productUrl', '')}")

        # 如果需要显示对比分析
        summary = product.get("summary", "")
        if summary and len(summary) < 300:
            print(f"\n   对比分析:")
            print(f"   {summary[:200]}...")


def main():
    parser = argparse.ArgumentParser(description="1688遨虾AI选品 - 关键词搜索和新品报告")

    subparsers = parser.add_subparsers(dest="command", help="命令")

    # search 命令
    search_parser = subparsers.add_parser("search", help="搜索关键词")
    search_parser.add_argument("--keyword", required=True, help="查询关键词")
    search_parser.add_argument("--platform", required=True, choices=PLATFORMS, help="平台")
    search_parser.add_argument("--region", required=True, help="国家代码")
    search_parser.add_argument("--listing-time", choices=["90", "180"], help="商品上架时间范围（天）")
    search_parser.add_argument("--output-json", action="store_true", help="输出完整JSON")

    # report 命令
    report_parser = subparsers.add_parser("report", help="生成新品选品报告")
    report_parser.add_argument("--keyword", required=True, help="关键词")
    report_parser.add_argument("--platform", required=True, choices=PLATFORMS, help="平台")
    report_parser.add_argument("--country", required=True, help="国家代码")
    report_parser.add_argument("--listing-time", choices=["90", "180"], help="商品上架时间范围（天）")
    report_parser.add_argument("--min-price", type=float, help="最低价格")
    report_parser.add_argument("--max-price", type=float, help="最高价格")
    report_parser.add_argument("--min-sales", type=int, help="最低月销量")
    report_parser.add_argument("--max-sales", type=int, help="最高月销量")
    report_parser.add_argument("--min-rating", type=float, help="最低评分")
    report_parser.add_argument("--max-rating", type=float, help="最高评分")
    report_parser.add_argument("--output-json", action="store_true", help="输出完整JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "search":
            result = search_keywords(
                keyword=args.keyword,
                platform=args.platform,
                region=args.region,
                listing_time=args.listing_time,
            )

            # 打印关键词列表
            print_keyword_list(result)

            # 保存JSON
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"output/alphashop-sel-newproduct/keywords-{args.keyword.replace(' ', '-')}-{args.region}-{timestamp}.json"

            import os
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"\n{'='*60}")
            print(f"关键词数据已保存到: {filename}")
            print(f"{'='*60}")

            # 如果需要输出完整JSON
            if args.output_json:
                print("\n完整JSON输出:")
                print(json.dumps(result, ensure_ascii=False, indent=2))

        elif args.command == "report":
            result = generate_report(
                keyword=args.keyword,
                platform=args.platform,
                country=args.country,
                listing_time=args.listing_time,
                min_price=args.min_price,
                max_price=args.max_price,
                min_volume=args.min_sales,
                max_volume=args.max_sales,
                min_rating=args.min_rating,
                max_rating=args.max_rating,
            )

            # 打印摘要
            if result.get("data"):
                print_market_summary(result["data"])
                print_product_list(result["data"])

            # 保存JSON
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"output/alphashop-sel-newproduct/report-{args.keyword.replace(' ', '-')}-{args.country}-{timestamp}.json"

            import os
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"\n{'='*60}")
            print(f"报告已保存到: {filename}")
            print(f"{'='*60}")

            # 如果需要输出完整JSON
            if args.output_json:
                print("\n完整JSON输出:")
                print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
