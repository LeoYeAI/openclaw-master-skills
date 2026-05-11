#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用多维商品评分引擎（V3 新增）

根据 AI 生成的 category_profile 中定义的评估维度和权重，
对候选商品进行动态多维评分。

核心特点：
- 维度名称、数量、权重全部来自 category_profile（不硬编码）
- 安全封顶规则根据品类类型自适应
- 综合分 = Σ(维度分 × 维度权重)
- 分类阈值品类无关（>=70推荐, 55-69有条件推荐, 40-54谨慎选择, <40避坑）

用法:
    python brand_scorer.py scored_results.json \
        --category-profile category_profile.json \
        --safety-results safety_results.json \
        --output brand_scores.json
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime


# ============================================================
# 安全封顶规则（品类自适应）
# ============================================================

SAFETY_CAPS = {
    "food": {"threshold": 30, "max_score": 54},
    "personal_care": {"threshold": 25, "max_score": 54},
    "electronics": {"threshold": 20, "max_score": 54},
    "durable_goods": {"threshold": 15, "max_score": 54},
    "service": {"threshold": 20, "max_score": 54},
    "other": {"threshold": 20, "max_score": 54},
}

# 分类阈值（通用，品类无关）
VERDICT_THRESHOLDS = [
    (70, "推荐"),
    (55, "有条件推荐"),
    (40, "谨慎选择"),
    (0, "避坑"),
]


def classify_verdict(score):
    """根据综合分判定商品结论"""
    for threshold, verdict in VERDICT_THRESHOLDS:
        if score >= threshold:
            return verdict
    return "避坑"


def apply_safety_cap(overall_score, safety_score, category_type):
    """
    安全风险封顶规则（品类自适应）

    不同品类对安全的容忍度不同：
    - food/personal_care：安全容忍度最低
    - electronics：安全容忍度中等
    - durable_goods：安全容忍度较高

    Args:
        overall_score: 商品综合分
        safety_score: 安全维度分数 (0-100)
        category_type: 品类类型

    Returns:
        封顶后的综合分
    """
    cap = SAFETY_CAPS.get(category_type, SAFETY_CAPS["other"])

    if safety_score < cap["threshold"]:
        return min(overall_score, cap["max_score"])
    return overall_score


# ============================================================
# 证据提取与维度匹配
# ============================================================

def extract_dimension_evidence(results, product_name, dimension):
    """
    从搜索结果中提取与指定维度相关的证据

    使用维度的 key_parameters 和 description 作为匹配依据。

    Args:
        results: 搜索结果列表
        product_name: 商品名称
        dimension: 维度定义字典 {"name", "key_parameters", "description"}

    Returns:
        相关证据列表 [{"text": ..., "credibility": ..., "sentiment": ...}]
    """
    evidence = []
    key_params = dimension.get("key_parameters", [])
    dim_name = dimension.get("name", "")
    dim_desc = dimension.get("description", "")

    # 构建匹配关键词集合
    match_keywords = set()
    match_keywords.add(dim_name)
    for param in key_params:
        match_keywords.add(param)
    # 从 description 中提取关键词（简单分词）
    for word in re.findall(r'[\u4e00-\u9fa5]{2,}', dim_desc):
        match_keywords.add(word)

    for r in results:
        text = " ".join([
            r.get("title", ""),
            r.get("snippet", ""),
            r.get("content", ""),
        ])

        # 检查是否与当前商品相关
        if product_name not in text:
            continue

        # 检查是否与当前维度相关
        matched_keywords = [kw for kw in match_keywords if kw in text]
        if not matched_keywords:
            continue

        # 判断情感倾向
        neg_words = re.findall(
            r"(?:坏了|后悔|垃圾|不行|差|烂|失望|退货|投诉|问题|异响|塌陷|断裂|不好|缺点|不足)",
            text, re.IGNORECASE
        )
        pos_words = re.findall(
            r"(?:好用|舒服|推荐|值得|不错|满意|喜欢|完美|优秀|稳定|出色|扎实)",
            text, re.IGNORECASE
        )

        if len(neg_words) > len(pos_words):
            sentiment = "negative"
        elif len(pos_words) > len(neg_words):
            sentiment = "positive"
        else:
            sentiment = "neutral"

        evidence.append({
            "text_preview": text[:200],
            "credibility": r.get("credibility_score", 50),
            "sentiment": sentiment,
            "matched_keywords": matched_keywords[:5],
            "url": r.get("url", ""),
        })

    return evidence


def compute_dimension_score(evidence, dimension):
    """
    根据证据计算单个维度的得分（V4 升级：五级置信度）

    评分逻辑：
    - 基础分 50 分
    - 高可信度正面证据 +10 分/条（上限3条）
    - 高可信度负面证据 -15 分/条（上限3条，负面权重更高）
    - 中可信度证据按 0.5 系数折算
    - 无证据时给 50 分（中性），但置信度标为"极低"

    置信度五级标注：
    - 极高：≥10条高可信度证据，评分高度可信
    - 高：≥5条高可信度证据
    - 中：≥3条高可信度证据或≥5条中等证据
    - 低：1-2条高可信度证据
    - 极低：无高可信度证据，评分主要基于推断

    Args:
        evidence: 证据列表
        dimension: 维度定义

    Returns:
        (score, confidence, evidence_count, detail) 元组
        detail: {"high_cred_count", "mid_cred_count", "pos_count", "neg_count"}
    """
    if not evidence:
        return 50, "极低", 0, {
            "high_cred_count": 0, "mid_cred_count": 0,
            "pos_count": 0, "neg_count": 0,
        }

    base_score = 50
    delta = 0
    high_cred_count = 0
    mid_cred_count = 0
    pos_count = 0
    neg_count = 0

    for e in evidence:
        cred = e.get("credibility", 50)
        sentiment = e.get("sentiment", "neutral")

        # 可信度系数
        if cred >= 60:
            cred_factor = 1.0
            high_cred_count += 1
        elif cred >= 40:
            cred_factor = 0.5
            mid_cred_count += 1
        else:
            continue  # 低可信度证据不纳入

        if sentiment == "positive":
            delta += 10 * cred_factor
            pos_count += 1
        elif sentiment == "negative":
            delta -= 15 * cred_factor
            neg_count += 1

    # 限制极端值
    delta = max(-50, min(50, delta))
    score = max(0, min(100, base_score + delta))

    # 五级置信度
    total_effective = high_cred_count + mid_cred_count
    if high_cred_count >= 10:
        confidence = "极高"
    elif high_cred_count >= 5:
        confidence = "高"
    elif high_cred_count >= 3 or total_effective >= 5:
        confidence = "中"
    elif high_cred_count >= 1:
        confidence = "低"
    else:
        confidence = "极低"

    detail = {
        "high_cred_count": high_cred_count,
        "mid_cred_count": mid_cred_count,
        "pos_count": pos_count,
        "neg_count": neg_count,
    }

    return round(score, 1), confidence, len(evidence), detail


# ============================================================
# 安全分计算
# ============================================================

def compute_safety_score(safety_events, product_name, category_profile=None):
    """
    计算商品的安全维度分数

    Args:
        safety_events: 安全事件列表
        product_name: 商品名称
        category_profile: 品类配置

    Returns:
        (safety_score, safety_event_count) 元组
    """
    if not safety_events:
        return 80, 0  # 无安全事件，默认 80 分

    relevant_events = [
        e for e in safety_events
        if product_name in e.get("dive_model", "")
        or product_name in e.get("title", "")
    ]

    if not relevant_events:
        return 80, 0

    base_score = 80
    delta = 0

    for event in relevant_events:
        severity = event.get("severity", "INFO")
        source_type = event.get("source_type", "community_discussion")

        # 来源权重
        source_weight = {
            "official_announcement": 2.0,
            "safety_alert": 1.8,
            "news_report": 1.2,
            "community_discussion": 0.8,
            "ecommerce_review": 0.6,
        }.get(source_type, 0.8)

        # 严重级别扣分
        severity_penalty = {
            "CRITICAL": -30,
            "HIGH": -20,
            "MEDIUM": -10,
            "LOW": -5,
            "INFO": -2,
        }.get(severity, -2)

        delta += severity_penalty * source_weight

    score = max(0, min(100, base_score + delta))
    return round(score, 1), len(relevant_events)


# ============================================================
# 核心评分引擎
# ============================================================

def compute_product_scores(category_profile, search_results, safety_events=None):
    """
    通用商品评分引擎

    根据 category_profile 中定义的维度和权重，动态计算每个商品的综合分。
    不依赖任何品类硬编码——维度名称、数量、权重全部来自 AI 生成的配置。

    Args:
        category_profile: AI 生成的品类配置（包含维度定义）
        search_results: 主搜索 + 深挖的可信结果
        safety_events: 安全事件搜索结果

    Returns:
        dict: {商品名: ProductScore}
    """
    dimensions = category_profile.get("evaluation_dimensions", [])
    category_type = category_profile.get("category_type", "other")

    if not dimensions:
        print("[ERROR] category_profile 中未定义评估维度", file=sys.stderr)
        return {}

    # 验证权重约束
    total_weight = sum(d.get("weight", 0) for d in dimensions)
    if abs(total_weight - 1.0) > 0.05:
        print(f"[WARN] 维度权重之和 = {total_weight}，不等于 1.0，将自动归一化", file=sys.stderr)
        for d in dimensions:
            d["weight"] = d.get("weight", 0) / total_weight

    # 从搜索结果中提取所有被提及的商品
    product_mentions = defaultdict(int)
    for r in search_results:
        # 使用 dive_model 字段
        if r.get("dive_model"):
            product_mentions[r["dive_model"]] += 1

    if not product_mentions:
        print("[WARN] 未从搜索结果中识别到商品型号", file=sys.stderr)
        return {}

    # 对每个商品计算多维评分
    product_scores = {}
    for product_name, mention_count in product_mentions.items():
        if mention_count < 2:
            continue  # 忽略提及次数太少的型号

        dim_scores = {}
        dim_confidence = {}
        dim_details = {}
        total_evidence = 0
        overall_score = 0
        confidence_levels = []

        for dim in dimensions:
            # 提取维度相关证据
            evidence = extract_dimension_evidence(search_results, product_name, dim)
            score, confidence, evidence_count, detail = compute_dimension_score(evidence, dim)

            dim_scores[dim["name"]] = score
            dim_confidence[dim["name"]] = confidence
            dim_details[dim["name"]] = detail
            total_evidence += evidence_count
            confidence_levels.append(confidence)

            # 加权累加
            overall_score += score * dim["weight"]

        # 安全分
        safety_score, safety_event_count = compute_safety_score(
            safety_events, product_name, category_profile
        )

        # 安全封顶规则
        overall_score = apply_safety_cap(overall_score, safety_score, category_type)

        # 综合置信度（五级加权计算）
        confidence_weight_map = {"极高": 5, "高": 4, "中": 3, "低": 2, "极低": 1}
        if confidence_levels:
            avg_confidence_weight = sum(
                confidence_weight_map.get(c, 2) for c in confidence_levels
            ) / len(confidence_levels)

            if avg_confidence_weight >= 4.5:
                overall_confidence = "极高"
            elif avg_confidence_weight >= 3.5:
                overall_confidence = "高"
            elif avg_confidence_weight >= 2.5:
                overall_confidence = "中"
            elif avg_confidence_weight >= 1.5:
                overall_confidence = "低"
            else:
                overall_confidence = "极低"
        else:
            overall_confidence = "极低"

        product_scores[product_name] = {
            "overall_score": round(overall_score, 1),
            "dimension_scores": dim_scores,
            "dimension_confidence": dim_confidence,
            "dimension_details": dim_details,
            "safety_score": safety_score,
            "safety_event_count": safety_event_count,
            "confidence": overall_confidence,
            "evidence_count": total_evidence,
            "mention_count": mention_count,
            "verdict": classify_verdict(overall_score),
        }

    # 按综合分排序
    product_scores = dict(
        sorted(product_scores.items(),
               key=lambda x: x[1]["overall_score"],
               reverse=True)
    )

    return product_scores


# ============================================================
# 主程序
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="通用多维商品评分引擎（V3）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python brand_scorer.py scored_results.json \\
        --category-profile category_profile.json \\
        --safety-results safety_results.json \\
        --output brand_scores.json
        """,
    )

    parser.add_argument(
        "input",
        help="可信度评分后的搜索结果文件（JSON）",
    )
    parser.add_argument(
        "--category-profile",
        required=True,
        help="品类配置文件路径（JSON 格式，由 AI 品类自适应分析生成）",
    )
    parser.add_argument(
        "--safety-results",
        default=None,
        help="安全事件搜索结果文件（JSON 格式，可选）",
    )
    parser.add_argument(
        "--dive-results",
        default=None,
        help="深挖搜索评分结果文件（JSON 格式，可选）",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="输出文件路径（JSON 格式）",
    )

    args = parser.parse_args()

    # 加载品类配置
    with open(args.category_profile, "r", encoding="utf-8") as f:
        category_profile = json.load(f)
    print(f"[INFO] 品类: {category_profile.get('category', '未知')}", file=sys.stderr)
    print(f"[INFO] 品类类型: {category_profile.get('category_type', '未知')}", file=sys.stderr)

    dimensions = category_profile.get("evaluation_dimensions", [])
    print(f"[INFO] 评估维度 ({len(dimensions)} 个):", file=sys.stderr)
    for d in dimensions:
        print(f"  - {d['name']} (权重: {d.get('weight', 0)})", file=sys.stderr)

    # 加载搜索结果
    with open(args.input, "r", encoding="utf-8") as f:
        input_data = json.load(f)
    search_results = input_data.get("results", [])

    # 合并深挖结果
    if args.dive_results:
        with open(args.dive_results, "r", encoding="utf-8") as f:
            dive_data = json.load(f)
        search_results.extend(dive_data.get("results", []))

    # 加载安全事件结果
    safety_events = []
    if args.safety_results:
        with open(args.safety_results, "r", encoding="utf-8") as f:
            safety_data = json.load(f)
        safety_events = safety_data.get("safety_results", safety_data.get("results", []))

    print(f"[INFO] 搜索结果: {len(search_results)} 条", file=sys.stderr)
    print(f"[INFO] 安全事件: {len(safety_events)} 条", file=sys.stderr)

    # 执行评分
    product_scores = compute_product_scores(
        category_profile=category_profile,
        search_results=search_results,
        safety_events=safety_events,
    )

    print(f"\n[DONE] 评分完成，共评估 {len(product_scores)} 个商品", file=sys.stderr)
    for name, score in product_scores.items():
        dim_conf_str = " | ".join(
            f"{d}:{score.get('dimension_confidence', {}).get(d, '?')}"
            for d in [d["name"] for d in dimensions]
        )
        print(
            f"  - {name}: 综合 {score['overall_score']} | "
            f"安全 {score['safety_score']} | "
            f"置信 {score['confidence']} | "
            f"结论: {score['verdict']}\n"
            f"    维度置信度: {dim_conf_str}",
            file=sys.stderr,
        )

    # 输出
    output_data = {
        "scoring_time": datetime.now().isoformat(),
        "category": category_profile.get("category", "未知"),
        "category_type": category_profile.get("category_type", "other"),
        "dimensions": [d["name"] for d in dimensions],
        "products": product_scores,
    }

    json_str = json.dumps(output_data, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_str)
        print(f"[INFO] 评分结果已保存到: {args.output}", file=sys.stderr)
    else:
        print(json_str)


if __name__ == "__main__":
    main()
