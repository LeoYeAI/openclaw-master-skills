#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
证据冲突仲裁器（V4 新增）

当不同来源对同一商品的某个维度评价存在矛盾时，
基于来源可信度、时间权重和非商业属性进行系统化仲裁。

核心逻辑：
- 识别同一商品+同一维度下正面与负面证据的冲突
- 按可信度加权：非商业来源 > 商业来源
- 按时间加权：近期 > 早期
- 输出仲裁结论 + 置信度 + 冲突摘要

用法:
    python conflict_resolver.py scored_results.json \
        --category-profile category_profile.json \
        --output conflicts.json
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime


# ============================================================
# 通用非商业来源标识
# ============================================================

UNIVERSAL_NON_COMMERCIAL_DOMAINS = [
    r"12315", r"黑猫投诉", r"中国质量万里行",
    r"市场监管", r"samr\.gov\.cn",
    r"fda\.gov", r"efsa\.europa\.eu",
    r"cfs\.gov\.hk",
    r"consumer\.org", r"消费者协会",
]

UNIVERSAL_COMMERCIAL_BIAS_PATTERNS = [
    r"(?:优惠券|优惠码|折扣码|返利|领券)",
    r"(?:affiliate|partner|sponsor|赞助|合作)",
    r"(?:旗舰店|官方店|自营)",
    r"(?:带货|种草|推广)",
]


# ============================================================
# 证据分类与冲突检测
# ============================================================

def classify_evidence_sentiment(text):
    """
    判断证据的情感倾向

    Returns:
        "positive" | "negative" | "neutral"
    """
    neg_patterns = [
        r"(?:坏了|后悔|垃圾|不行|差|烂|失望|退货|投诉|问题|翻车)",
        r"(?:异响|塌陷|断裂|发热|降频|卡顿|掉帧|漏|品控差)",
        r"(?:不推荐|避坑|踩坑|智商税|不值|上当|骗人)",
        r"(?:召回|超标|污染|缺陷|故障|维修|返厂)",
    ]
    pos_patterns = [
        r"(?:好用|舒服|推荐|值得|不错|满意|喜欢|完美|优秀|稳定|出色)",
        r"(?:性价比高|手感好|散热好|续航长|充电快|帧率稳)",
        r"(?:长期使用.*满意|用了.*还不错|推荐购买)",
    ]

    neg_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in neg_patterns)
    pos_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in pos_patterns)

    if neg_count > pos_count + 1:
        return "negative"
    elif pos_count > neg_count + 1:
        return "positive"
    return "neutral"


def is_non_commercial_source(url, title, category_profile=None):
    """
    判断来源是否为非商业来源

    Args:
        url: 来源 URL
        title: 来源标题
        category_profile: 品类配置（可选，包含品类特定非商业指标）

    Returns:
        True if non-commercial
    """
    combined = f"{url} {title}".lower()

    # 通用非商业来源
    for pattern in UNIVERSAL_NON_COMMERCIAL_DOMAINS:
        if re.search(pattern, combined, re.IGNORECASE):
            return True

    # 品类特定非商业来源
    if category_profile:
        for indicator in category_profile.get("non_commercial_indicators", []):
            if indicator.lower() in combined:
                return True

    return False


def is_commercial_biased(url, title, category_profile=None):
    """
    判断来源是否存在商业偏见

    Returns:
        True if commercially biased
    """
    combined = f"{url} {title}".lower()

    for pattern in UNIVERSAL_COMMERCIAL_BIAS_PATTERNS:
        if re.search(pattern, combined, re.IGNORECASE):
            return True

    if category_profile:
        for bias_source in category_profile.get("commercial_bias_sources", []):
            if bias_source.lower() in combined:
                return True

    return False


def has_long_term_usage(text):
    """
    判断证据是否包含长期使用反馈

    Returns:
        True if contains long-term usage indicators
    """
    long_term_patterns = [
        r"(?:用了|使用了|买了|入手)\s*(?:\d+\s*(?:年|个月|月))",
        r"(?:半年|一年|两年|三年|几个月)(?:后|了|以来)",
        r"(?:长期使用|持续使用|日常使用)\s*(?:\d+)?",
        r"(?:一开始|刚开始).*?(?:后来|现在|之后)",
    ]
    for p in long_term_patterns:
        if re.search(p, text, re.IGNORECASE):
            return True
    return False


def extract_dimension_relevance(text, dimension):
    """
    判断证据与某个评估维度的相关性

    Args:
        text: 证据文本
        dimension: 维度定义 {"name", "key_parameters", "description"}

    Returns:
        相关性分数 0-1
    """
    match_count = 0
    total_keywords = 0

    keywords = set()
    keywords.add(dimension.get("name", ""))
    for param in dimension.get("key_parameters", []):
        keywords.add(param)
    for word in re.findall(r'[\u4e00-\u9fa5]{2,}', dimension.get("description", "")):
        keywords.add(word)

    total_keywords = len(keywords)
    if total_keywords == 0:
        return 0

    for kw in keywords:
        if kw and kw in text:
            match_count += 1

    return match_count / total_keywords


# ============================================================
# 冲突检测引擎
# ============================================================

def detect_conflicts(search_results, category_profile):
    """
    检测同一商品在不同来源间的评价冲突

    Args:
        search_results: 评分后的搜索结果列表
        category_profile: 品类配置

    Returns:
        冲突列表 [{product, dimension, positive_evidence, negative_evidence, ...}]
    """
    dimensions = category_profile.get("evaluation_dimensions", [])
    conflicts = []

    # 按商品分组
    product_evidence = defaultdict(list)
    for r in search_results:
        product_name = r.get("dive_model", "")
        if not product_name:
            continue
        product_evidence[product_name].append(r)

    for product_name, evidences in product_evidence.items():
        for dim in dimensions:
            dim_name = dim.get("name", "")

            # 筛选与该维度相关的证据
            pos_evidence = []
            neg_evidence = []

            for e in evidences:
                text = " ".join([
                    e.get("title", ""),
                    e.get("snippet", ""),
                    e.get("content", ""),
                ])

                # 检查维度相关性
                relevance = extract_dimension_relevance(text, dim)
                if relevance < 0.1:
                    continue

                sentiment = classify_evidence_sentiment(text)
                credibility = e.get("credibility_score", 50)

                evidence_item = {
                    "url": e.get("url", ""),
                    "title": e.get("title", ""),
                    "platform": e.get("platform_name", ""),
                    "credibility": credibility,
                    "is_recent": e.get("is_recent", False),
                    "is_non_commercial": is_non_commercial_source(
                        e.get("url", ""), e.get("title", ""), category_profile
                    ),
                    "is_commercial_biased": is_commercial_biased(
                        e.get("url", ""), e.get("title", ""), category_profile
                    ),
                    "has_long_term": has_long_term_usage(text),
                    "relevance": round(relevance, 2),
                    "text_preview": text[:150],
                }

                if sentiment == "positive":
                    pos_evidence.append(evidence_item)
                elif sentiment == "negative":
                    neg_evidence.append(evidence_item)

            # 判定是否存在冲突
            if len(pos_evidence) >= 1 and len(neg_evidence) >= 1:
                conflicts.append({
                    "product": product_name,
                    "dimension": dim_name,
                    "positive_count": len(pos_evidence),
                    "negative_count": len(neg_evidence),
                    "positive_evidence": sorted(
                        pos_evidence, key=lambda x: x["credibility"], reverse=True
                    )[:5],
                    "negative_evidence": sorted(
                        neg_evidence, key=lambda x: x["credibility"], reverse=True
                    )[:5],
                })

    return conflicts


# ============================================================
# 仲裁引擎
# ============================================================

def compute_evidence_weight(evidence_item):
    """
    计算单条证据的综合权重

    权重因子：
    - 可信度分数 (0-100) → 基础权重
    - 非商业来源 → ×1.5
    - 商业偏见来源 → ×0.6
    - 长期使用反馈 → ×1.3
    - 近期内容 → ×1.1
    - 维度相关性 → ×(0.5 + relevance)

    Returns:
        综合权重分数
    """
    base = evidence_item.get("credibility", 50)

    # 来源性质调整
    if evidence_item.get("is_non_commercial", False):
        base *= 1.5
    if evidence_item.get("is_commercial_biased", False):
        base *= 0.6

    # 时间深度调整
    if evidence_item.get("has_long_term", False):
        base *= 1.3
    if evidence_item.get("is_recent", False):
        base *= 1.1

    # 维度相关性调整
    relevance = evidence_item.get("relevance", 0.5)
    base *= (0.5 + relevance)

    return round(base, 1)


def arbitrate_conflict(conflict):
    """
    对单个冲突进行仲裁

    仲裁逻辑：
    1. 计算正面/负面证据的加权总分
    2. 比较加权总分，确定倾向
    3. 计算置信度（基于证据强度差异）
    4. 生成仲裁摘要

    Args:
        conflict: 冲突数据字典

    Returns:
        仲裁结果字典
    """
    pos_evidence = conflict.get("positive_evidence", [])
    neg_evidence = conflict.get("negative_evidence", [])

    # 计算加权分
    pos_weights = [compute_evidence_weight(e) for e in pos_evidence]
    neg_weights = [compute_evidence_weight(e) for e in neg_evidence]

    pos_total = sum(pos_weights)
    neg_total = sum(neg_weights)
    total = pos_total + neg_total

    if total == 0:
        return {
            "verdict": "evidence_insufficient",
            "confidence": "low",
            "lean_direction": "neutral",
            "summary": "证据不足，无法仲裁",
        }

    pos_ratio = pos_total / total
    neg_ratio = neg_total / total

    # 判定倾向
    if pos_ratio > 0.65:
        lean = "positive"
        verdict_text = "正面证据显著占优"
    elif neg_ratio > 0.65:
        lean = "negative"
        verdict_text = "负面证据显著占优"
    elif pos_ratio > 0.55:
        lean = "slightly_positive"
        verdict_text = "正面证据略占优，但存在争议"
    elif neg_ratio > 0.55:
        lean = "slightly_negative"
        verdict_text = "负面证据略占优，但存在争议"
    else:
        lean = "contested"
        verdict_text = "正反证据势均力敌，结论存在较大不确定性"

    # 计算置信度
    strength_gap = abs(pos_total - neg_total)
    evidence_count = len(pos_evidence) + len(neg_evidence)

    if strength_gap > total * 0.4 and evidence_count >= 4:
        confidence = "high"
    elif strength_gap > total * 0.2 and evidence_count >= 2:
        confidence = "medium"
    else:
        confidence = "low"

    # 识别关键仲裁因素
    arbitration_factors = []

    # 检查非商业来源是否倾向某一方
    pos_non_commercial = sum(1 for e in pos_evidence if e.get("is_non_commercial"))
    neg_non_commercial = sum(1 for e in neg_evidence if e.get("is_non_commercial"))
    if pos_non_commercial > neg_non_commercial:
        arbitration_factors.append("非商业来源更支持正面评价")
    elif neg_non_commercial > pos_non_commercial:
        arbitration_factors.append("非商业来源更支持负面评价")

    # 检查长期使用反馈是否倾向某一方
    pos_long_term = sum(1 for e in pos_evidence if e.get("has_long_term"))
    neg_long_term = sum(1 for e in neg_evidence if e.get("has_long_term"))
    if pos_long_term > neg_long_term:
        arbitration_factors.append("长期使用反馈更偏正面")
    elif neg_long_term > pos_long_term:
        arbitration_factors.append("长期使用反馈更偏负面")

    # 检查商业偏见来源分布
    pos_biased = sum(1 for e in pos_evidence if e.get("is_commercial_biased"))
    neg_biased = sum(1 for e in neg_evidence if e.get("is_commercial_biased"))
    if pos_biased > len(pos_evidence) * 0.5 and neg_biased < len(neg_evidence) * 0.3:
        arbitration_factors.append("正面评价中商业偏见来源占比较高，可信度打折")

    # 检查高可信度证据的倾向
    pos_high_cred = [e for e in pos_evidence if e.get("credibility", 0) >= 70]
    neg_high_cred = [e for e in neg_evidence if e.get("credibility", 0) >= 70]
    if len(pos_high_cred) > len(neg_high_cred) * 2:
        arbitration_factors.append("高可信度证据更支持正面评价")
    elif len(neg_high_cred) > len(pos_high_cred) * 2:
        arbitration_factors.append("高可信度证据更支持负面评价")

    # 生成摘要
    summary_parts = [verdict_text]
    if arbitration_factors:
        summary_parts.append("仲裁依据：" + "；".join(arbitration_factors))

    return {
        "verdict": lean,
        "confidence": confidence,
        "lean_direction": lean,
        "positive_weighted_score": round(pos_total, 1),
        "negative_weighted_score": round(neg_total, 1),
        "positive_ratio": round(pos_ratio, 3),
        "negative_ratio": round(neg_ratio, 3),
        "arbitration_factors": arbitration_factors,
        "summary": "。".join(summary_parts),
    }


def resolve_all_conflicts(search_results, category_profile):
    """
    主入口：检测所有冲突并逐一仲裁

    Args:
        search_results: 评分后的搜索结果列表
        category_profile: 品类配置

    Returns:
        {
            "total_conflicts": int,
            "conflicts": [
                {
                    "product": str,
                    "dimension": str,
                    "positive_count": int,
                    "negative_count": int,
                    "arbitration": {...},
                    "positive_evidence": [...],
                    "negative_evidence": [...],
                }
            ],
            "product_summaries": {
                "商品名": {
                    "total_conflicts": int,
                    "contested_dimensions": [...],
                    "overall_reliability": "high|medium|low"
                }
            }
        }
    """
    conflicts = detect_conflicts(search_results, category_profile)

    resolved = []
    product_summaries = defaultdict(lambda: {
        "total_conflicts": 0,
        "contested_dimensions": [],
        "arbitration_results": [],
    })

    for conflict in conflicts:
        arbitration = arbitrate_conflict(conflict)

        resolved_conflict = {
            "product": conflict["product"],
            "dimension": conflict["dimension"],
            "positive_count": conflict["positive_count"],
            "negative_count": conflict["negative_count"],
            "arbitration": arbitration,
            "positive_evidence": conflict["positive_evidence"][:3],  # 只保留top 3
            "negative_evidence": conflict["negative_evidence"][:3],
        }
        resolved.append(resolved_conflict)

        # 汇总到商品级别
        ps = product_summaries[conflict["product"]]
        ps["total_conflicts"] += 1
        ps["contested_dimensions"].append(conflict["dimension"])
        ps["arbitration_results"].append({
            "dimension": conflict["dimension"],
            "verdict": arbitration["verdict"],
            "confidence": arbitration["confidence"],
        })

    # 计算商品级别的整体可靠性
    for product_name, ps in product_summaries.items():
        high_conf = sum(1 for ar in ps["arbitration_results"] if ar["confidence"] == "high")
        low_conf = sum(1 for ar in ps["arbitration_results"] if ar["confidence"] == "low")
        total = len(ps["arbitration_results"])

        if total == 0:
            ps["overall_reliability"] = "unknown"
        elif high_conf >= total * 0.6:
            ps["overall_reliability"] = "high"
        elif low_conf >= total * 0.5:
            ps["overall_reliability"] = "low"
        else:
            ps["overall_reliability"] = "medium"

    return {
        "resolution_time": datetime.now().isoformat(),
        "category": category_profile.get("category", "未知"),
        "total_conflicts": len(resolved),
        "conflicts": resolved,
        "product_summaries": dict(product_summaries),
    }


# ============================================================
# 主程序
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="证据冲突仲裁器（V4）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python conflict_resolver.py scored_results.json \\
        --category-profile category_profile.json \\
        --output conflicts.json
        """,
    )

    parser.add_argument(
        "input",
        help="可信度评分后的搜索结果文件（JSON）",
    )
    parser.add_argument(
        "--category-profile",
        required=True,
        help="品类配置文件路径（JSON 格式）",
    )
    parser.add_argument(
        "--dive-results",
        default=None,
        help="深挖搜索结果文件（JSON，可选，会与主结果合并）",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="输出文件路径（JSON）",
    )

    args = parser.parse_args()

    # 加载品类配置
    with open(args.category_profile, "r", encoding="utf-8") as f:
        category_profile = json.load(f)
    print(f"[INFO] 品类: {category_profile.get('category', '未知')}", file=sys.stderr)

    # 加载搜索结果
    with open(args.input, "r", encoding="utf-8") as f:
        input_data = json.load(f)
    search_results = input_data.get("results", [])

    # 合并深挖结果
    if args.dive_results:
        with open(args.dive_results, "r", encoding="utf-8") as f:
            dive_data = json.load(f)
        search_results.extend(dive_data.get("results", []))

    print(f"[INFO] 加载 {len(search_results)} 条搜索结果", file=sys.stderr)

    # 执行冲突检测和仲裁
    result = resolve_all_conflicts(search_results, category_profile)

    print(f"\n[DONE] 检测到 {result['total_conflicts']} 个证据冲突", file=sys.stderr)
    for conflict in result["conflicts"]:
        arb = conflict["arbitration"]
        print(
            f"  - {conflict['product']} / {conflict['dimension']}: "
            f"正面{conflict['positive_count']}条 vs 负面{conflict['negative_count']}条 → "
            f"{arb['verdict']} (置信度: {arb['confidence']})",
            file=sys.stderr,
        )

    if result["product_summaries"]:
        print(f"\n[INFO] 商品级别汇总:", file=sys.stderr)
        for product, summary in result["product_summaries"].items():
            print(
                f"  - {product}: {summary['total_conflicts']}个冲突, "
                f"争议维度: {', '.join(summary['contested_dimensions'])}, "
                f"整体可靠性: {summary['overall_reliability']}",
                file=sys.stderr,
            )

    # 输出
    json_str = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_str)
        print(f"[INFO] 仲裁结果已保存到: {args.output}", file=sys.stderr)
    else:
        print(json_str)


if __name__ == "__main__":
    main()
