#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调查报告生成工具

将经过可信度评分的搜索结果合成为一份有立场的调查报告。
报告包含：推荐型号、避坑型号、数据透明度、真实讨论来源。

用法:
    python generate_report.py scored_results.json --query "人体工学椅" --budget 3000 --pain-point "腰肌劳损"
    python generate_report.py scored.json --dive-results dive_scored.json --output report.md
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime


# ============================================================
# 型号提取与聚合
# ============================================================

def extract_models_from_results(results):
    """从评分后的结果中提取各型号的信息聚合"""

    model_patterns = [
        r"([\u4e00-\u9fa5]{2,6}[A-Za-z]+[\-]?[A-Za-z]*\d+[A-Za-z]*\d*)",
        r"([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Za-z0-9]+)?)",
        r"([\u4e00-\u9fa5]{2,4}\s*[A-Za-z]+[\-][A-Za-z]*\d+)",
    ]

    model_data = defaultdict(lambda: {
        "mentions": 0,
        "positive_mentions": 0,
        "negative_mentions": 0,
        "avg_credibility": 0,
        "credibility_scores": [],
        "positive_signals": [],
        "negative_signals": [],
        "sources": [],
        "key_quotes": [],
    })

    for r in results:
        text = " ".join([
            r.get("title", ""),
            r.get("snippet", ""),
            r.get("content", ""),
        ])

        # 获取该结果中提到的型号
        found_models = set()
        for pattern in model_patterns:
            matches = re.findall(pattern, text)
            for m in matches:
                m = m.strip()
                if 3 <= len(m) <= 30:
                    found_models.add(m)

        # 使用 dive_model 字段（如果存在）
        if r.get("dive_model"):
            found_models.add(r["dive_model"])

        credibility = r.get("credibility_score", 50)
        level = r.get("credibility_level", "中可信度")
        signals = r.get("signals", [])

        for model in found_models:
            md = model_data[model]
            md["mentions"] += 1
            md["credibility_scores"].append(credibility)

            # 分析情感倾向
            has_positive = any(s["type"] == "positive" for s in signals)
            has_negative = any(
                s["type"] == "positive" and "缺点" in s.get("label", "")
                for s in signals
            )

            # 简单情感判断
            neg_words = re.findall(
                r"(?:坏了|后悔|垃圾|不行|差|烂|失望|退货|投诉|问题|异响|塌陷|断裂)",
                text, re.IGNORECASE
            )
            pos_words = re.findall(
                r"(?:好用|舒服|推荐|值得|不错|满意|喜欢|完美|优秀)",
                text, re.IGNORECASE
            )

            if len(neg_words) > len(pos_words):
                md["negative_mentions"] += 1
            elif len(pos_words) > 0:
                md["positive_mentions"] += 1

            # 收集来源
            if level in ("高可信度", "中可信度"):
                source = {
                    "url": r.get("url", ""),
                    "title": r.get("title", ""),
                    "platform": r.get("platform_name", ""),
                    "credibility": credibility,
                    "level": level,
                }
                md["sources"].append(source)

            # 提取关键引用（有使用时长或具体缺点的文本片段）
            duration_match = re.search(
                r"[^。！？\n]{0,50}(?:用了|买了|入手)\s*\d+\s*(?:年|个月|月|天)[^。！？\n]{0,100}",
                text
            )
            if duration_match and credibility >= 60:
                md["key_quotes"].append({
                    "quote": duration_match.group().strip(),
                    "source_url": r.get("url", ""),
                    "credibility": credibility,
                })

            defect_match = re.search(
                r"[^。！？\n]{0,50}(?:缺点|问题|毛病|不足|异响|塌陷|坏|断)[^。！？\n]{0,100}",
                text
            )
            if defect_match and credibility >= 50:
                md["key_quotes"].append({
                    "quote": defect_match.group().strip(),
                    "source_url": r.get("url", ""),
                    "credibility": credibility,
                })

    # 计算平均可信度
    for model, md in model_data.items():
        scores = md["credibility_scores"]
        if scores:
            md["avg_credibility"] = round(sum(scores) / len(scores), 1)
        # 去重引用
        seen_quotes = set()
        unique_quotes = []
        for q in md["key_quotes"]:
            if q["quote"] not in seen_quotes:
                seen_quotes.add(q["quote"])
                unique_quotes.append(q)
        md["key_quotes"] = unique_quotes[:5]  # 最多保留 5 条

    return dict(model_data)


# ============================================================
# 报告生成
# ============================================================

def generate_markdown_report(model_data, query, budget=None, pain_point=None,
                              total_results=0, filtered_count=0, reliable_count=0,
                              safety_events=None, ai_stats=None,
                              category_profile=None, brand_scores=None):
    """
    生成 Markdown 格式的调查报告

    Args:
        model_data: 型号聚合数据
        query: 原始搜索需求
        budget: 预算
        pain_point: 痛点
        total_results: 总搜索结果数
        filtered_count: 被过滤的疑似软文数
        reliable_count: 可信结果数
        safety_events: 安全事件搜索结果
        ai_stats: AI 分析统计信息
        category_profile: 【V3】AI 生成的品类配置（用于动态表头）
        brand_scores: 【V3】多维评分结果（来自 brand_scorer.py）
    """
    lines = []

    # 标题
    lines.append(f"# {query} 深度调查报告")
    lines.append("")
    lines.append(f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    lines.append("")

    # 需求回顾
    if budget or pain_point:
        lines.append("## 你的需求")
        lines.append("")
        parts = [f"**品类**: {query}"]
        if budget:
            parts.append(f"**预算**: {budget}元以内")
        if pain_point:
            parts.append(f"**核心痛点**: {pain_point}")
        lines.append(" | ".join(parts))
        lines.append("")

    # 【V2 新增】安全风险警告（如果存在安全事件）
    if safety_events:
        safety_by_model = defaultdict(list)
        for event in safety_events:
            model = event.get("dive_model", "未知品牌")
            safety_by_model[model].append(event)

        if safety_by_model:
            lines.append("## 安全风险警告")
            lines.append("")
            lines.append("> 以下品牌/型号在安全事件专项搜索中发现了潜在风险信息，请特别注意。")
            lines.append("")

            for model, events in safety_by_model.items():
                lines.append(f"### {model}")
                lines.append("")

                # 按信息源类型分组
                official = [e for e in events if e.get("source_type") == "official_announcement"]
                news = [e for e in events if e.get("source_type") == "news_report"]
                alerts = [e for e in events if e.get("source_type") == "safety_alert"]
                other = [e for e in events if e.get("source_type") not in
                         ("official_announcement", "news_report", "safety_alert")]

                if official or alerts:
                    lines.append("**官方通告/安全警报:**")
                    lines.append("")
                    for e in (official + alerts)[:3]:
                        lines.append(f'- [{e.get("title", "无标题")[:60]}]({e.get("url", "")})')
                    lines.append("")

                if news:
                    lines.append("**新闻报道:**")
                    lines.append("")
                    for e in news[:3]:
                        lines.append(f'- [{e.get("title", "无标题")[:60]}]({e.get("url", "")})')
                    lines.append("")

                if other and not (official or alerts or news):
                    lines.append("**相关信息:**")
                    lines.append("")
                    for e in other[:3]:
                        lines.append(f'- [{e.get("title", "无标题")[:60]}]({e.get("url", "")})')
                    lines.append("")

    # 【V3 新增】商品综合评分表（动态表头，来自 category_profile）
    if brand_scores and category_profile:
        dimensions = category_profile.get("evaluation_dimensions", [])
        dim_names = [d["name"] for d in dimensions]

        lines.append("## 商品综合评分")
        lines.append("")

        # 动态生成表头
        header_cols = ["商品型号"] + dim_names + ["安全分", "综合分", "置信度", "结论"]
        lines.append("| " + " | ".join(header_cols) + " |")
        lines.append("|" + "|".join(["------"] * len(header_cols)) + "|")

        # 填充数据行
        for product_name, score_data in brand_scores.items():
            dim_scores = score_data.get("dimension_scores", {})
            row = [product_name]
            for d_name in dim_names:
                row.append(str(dim_scores.get(d_name, "-")))
            row.append(str(score_data.get("safety_score", "-")))
            row.append(str(score_data.get("overall_score", "-")))
            row.append(score_data.get("confidence", "-"))
            row.append(score_data.get("verdict", "-"))
            lines.append("| " + " | ".join(row) + " |")

        lines.append("")

    # 排序型号：按正面提及比例和可信度综合排序
    sorted_models = sorted(
        model_data.items(),
        key=lambda x: (
            x[1]["positive_mentions"] / max(x[1]["mentions"], 1),
            x[1]["avg_credibility"],
        ),
        reverse=True,
    )

    # 过滤掉提及次数太少的型号
    significant_models = [(m, d) for m, d in sorted_models if d["mentions"] >= 2]

    if not significant_models:
        lines.append("## 调查结论")
        lines.append("")
        lines.append("本次搜索未发现足够多被真实用户频繁提及的具体型号。")
        lines.append("建议扩大搜索范围或调整关键词后重试。")
        lines.append("")
    else:
        # 分类：推荐 vs 避坑
        recommended = []
        avoid = []
        neutral = []

        # 【V2】收集有安全事件的品牌
        safety_flagged_models = set()
        if safety_events:
            for event in safety_events:
                m = event.get("dive_model", "")
                if m:
                    safety_flagged_models.add(m)

        for model, data in significant_models:
            pos_ratio = data["positive_mentions"] / max(data["mentions"], 1)
            neg_ratio = data["negative_mentions"] / max(data["mentions"], 1)

            # 【V2】有安全事件的品牌直接归入避坑
            if model in safety_flagged_models:
                avoid.append((model, data))
            elif pos_ratio >= 0.5 and data["avg_credibility"] >= 55:
                recommended.append((model, data))
            elif neg_ratio >= 0.4 or data["avg_credibility"] < 45:
                avoid.append((model, data))
            else:
                neutral.append((model, data))

        # 调查结论
        lines.append("## 调查结论")
        lines.append("")
        lines.append(
            f"在排除了 **{filtered_count}** 篇疑似软文后，"
            f"基于 **{reliable_count}** 条真实用户反馈，分析如下："
        )
        lines.append("")

        # 推荐型号
        if recommended:
            lines.append("---")
            lines.append("")
            for model, data in recommended[:3]:
                lines.append(f"### 推荐: {model}")
                lines.append("")
                lines.append(
                    f"真实用户提及 **{data['mentions']}** 次，"
                    f"其中正面 {data['positive_mentions']} 次，负面 {data['negative_mentions']} 次，"
                    f"平均可信度 **{data['avg_credibility']}** 分。"
                )
                lines.append("")

                # 关键引用
                pos_quotes = [q for q in data["key_quotes"]
                              if not re.search(r"(?:缺点|问题|坏|差)", q["quote"])]
                if pos_quotes:
                    lines.append("**真实用户说:**")
                    lines.append("")
                    for q in pos_quotes[:2]:
                        lines.append(f'> "{q["quote"]}"')
                        if q.get("source_url"):
                            lines.append(f'> *来源: [{q["source_url"][:60]}...]({q["source_url"]})*')
                        lines.append("")

                # 已知缺点
                neg_quotes = [q for q in data["key_quotes"]
                              if re.search(r"(?:缺点|问题|坏|差|异响|塌|断)", q["quote"])]
                if neg_quotes:
                    lines.append("**已知缺点:**")
                    lines.append("")
                    for q in neg_quotes[:2]:
                        lines.append(f'> "{q["quote"]}"')
                        lines.append("")

                # 来源链接
                credible_sources = sorted(data["sources"],
                                          key=lambda s: s["credibility"], reverse=True)[:3]
                if credible_sources:
                    lines.append("**真实讨论来源:**")
                    lines.append("")
                    for s in credible_sources:
                        lines.append(f'- [{s["title"][:50]}]({s["url"]}) ({s["platform"]}, 可信度{s["credibility"]})')
                    lines.append("")

        # 避坑型号
        if avoid:
            lines.append("---")
            lines.append("")
            for model, data in avoid[:3]:
                lines.append(f"### 避坑: {model}")
                lines.append("")

                neg_ratio = round(data["negative_mentions"] / max(data["mentions"], 1) * 100)
                lines.append(
                    f"真实用户提及 **{data['mentions']}** 次，"
                    f"其中 **{neg_ratio}%** 为负面反馈，"
                    f"平均可信度 **{data['avg_credibility']}** 分。"
                )
                lines.append("")

                # 负面引用
                neg_quotes = [q for q in data["key_quotes"]
                              if re.search(r"(?:缺点|问题|坏|差|异响|塌|断|后悔|退)", q["quote"])]
                if neg_quotes:
                    lines.append("**真实投诉:**")
                    lines.append("")
                    for q in neg_quotes[:3]:
                        lines.append(f'> "{q["quote"]}"')
                        if q.get("source_url"):
                            lines.append(f'> *来源: [{q["source_url"][:60]}...]({q["source_url"]})*')
                        lines.append("")

                # 来源
                sources = sorted(data["sources"],
                                 key=lambda s: s["credibility"], reverse=True)[:3]
                if sources:
                    lines.append("**真实讨论来源:**")
                    lines.append("")
                    for s in sources:
                        lines.append(f'- [{s["title"][:50]}]({s["url"]}) ({s["platform"]})')
                    lines.append("")

        # 中性/待定型号
        if neutral:
            lines.append("---")
            lines.append("")
            lines.append("### 其他提及较多的型号")
            lines.append("")
            lines.append("| 型号 | 提及次数 | 正面 | 负面 | 平均可信度 |")
            lines.append("|------|----------|------|------|------------|")
            for model, data in neutral[:5]:
                lines.append(
                    f"| {model} | {data['mentions']} | "
                    f"{data['positive_mentions']} | {data['negative_mentions']} | "
                    f"{data['avg_credibility']} |"
                )
            lines.append("")

    # 数据透明度
    lines.append("---")
    lines.append("")
    lines.append("## 数据透明度")
    lines.append("")
    lines.append(f"- 共搜索结果: **{total_results}** 条")
    lines.append(f"- 过滤疑似软文: **{filtered_count}** 条")
    lines.append(f"- 最终纳入分析: **{reliable_count}** 条真实反馈")

    # 【V5 新增】数据源分层统计
    source_layer_counts = defaultdict(int)
    for model, data in model_data.items():
        for s in data["sources"]:
            source_layer_counts["sources_total"] += 1
    # 从所有结果中统计层级分布
    all_model_results = []
    for model, data in model_data.items():
        all_model_results.extend(data.get("sources", []))

    # 检查是否有多层级数据
    has_multilayer = False
    layer_names = {
        "L1_ecommerce": "电商评论(间接)",
        "L2_comment_section": "评论区(间接)",
        "L3_forum_post": "论坛帖子",
        "L4_independent_post": "独立帖/评测",
    }
    # 统计平台中包含的层级信息
    ecom_count = sum(1 for s in all_model_results if s.get("platform", "") in ["电商评论(间接)"])
    comment_count = sum(1 for s in all_model_results if s.get("platform", "") in ["评论区(间接)"])
    if ecom_count > 0 or comment_count > 0:
        has_multilayer = True
        lines.append("")
        lines.append("**数据源分层覆盖:**")
        lines.append("")
        lines.append("| 数据源层级 | 数据量 | 说明 |")
        lines.append("|-----------|--------|------|")
        if ecom_count > 0:
            lines.append(f"| L1 电商评论(间接) | {ecom_count} 条 | 京东/淘宝/拼多多追评、差评汇总帖 |")
        if comment_count > 0:
            lines.append(f"| L2 评论区(间接) | {comment_count} 条 | 小红书/知乎种草帖评论区拔草反馈 |")
        forum_count = len(all_model_results) - ecom_count - comment_count
        if forum_count > 0:
            lines.append(f"| L3/L4 论坛帖+独立帖 | {forum_count} 条 | V2EX/Chiphell/NGA/什么值得买等 |")
        lines.append("")

    # 【V2 新增】安全事件搜索统计
    if safety_events:
        lines.append(f"- 安全事件搜索: **{len(safety_events)}** 条相关结果")

    # 【V2 新增】AI 分析覆盖率
    if ai_stats:
        lines.append(f"- AI 深度分析: **{ai_stats.get('session_analysis_count', 0)}** 条帖子")
        lines.append(f"- AI 分析缓存: **{ai_stats.get('cache_size', 0)}** 条")

    # 平台分布
    platform_counts = Counter()
    for model, data in model_data.items():
        for s in data["sources"]:
            platform_counts[s["platform"]] += 1
    if platform_counts:
        lines.append(f"- 覆盖平台: {', '.join(f'{p}({c}条)' for p, c in platform_counts.most_common())}")
    lines.append("")

    # 免责声明
    lines.append("---")
    lines.append("")
    lines.append("*本报告由 AI 深度调查工具自动生成。所有结论基于公开可访问的社区讨论内容，")
    lines.append("经过软文过滤和可信度评分后得出。建议结合个人实际情况做最终决策。*")

    return "\n".join(lines)


# ============================================================
# 主程序
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="调查报告生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python generate_report.py scored.json --query "人体工学椅" --budget 3000 --pain-point "腰肌劳损"
    python generate_report.py scored.json --dive-results dive_scored.json --output report.md
        """,
    )

    parser.add_argument("input", help="可信度评分后的结果文件（JSON）")
    parser.add_argument("--dive-results", default=None, help="深挖搜索的评分结果文件（可选）")
    parser.add_argument("--query", "-q", default="产品", help="搜索品类名称")
    parser.add_argument("--budget", "-b", type=int, default=None, help="预算（元）")
    parser.add_argument("--pain-point", "-pp", default=None, help="核心痛点")
    parser.add_argument("--output", "-o", default=None, help="输出文件路径")
    parser.add_argument("--safety-results", default=None, help="安全事件搜索结果文件（可选）")
    parser.add_argument("--category-profile", default=None, help="【V3】品类配置文件路径（JSON 格式）")
    parser.add_argument("--brand-scores", default=None, help="【V3】多维评分结果文件路径（JSON 格式）")

    args = parser.parse_args()

    # 【V3】加载品类配置
    category_profile = None
    if args.category_profile:
        with open(args.category_profile, "r", encoding="utf-8") as f:
            category_profile = json.load(f)
        print(f"[INFO] 已加载品类配置: {category_profile.get('category', '未知品类')}", file=sys.stderr)

    # 【V3】加载多维评分结果
    brand_scores = None
    if args.brand_scores:
        with open(args.brand_scores, "r", encoding="utf-8") as f:
            brand_scores = json.load(f)
        print(f"[INFO] 已加载多维评分结果: {len(brand_scores)} 个商品", file=sys.stderr)

    # 读取主搜索结果
    with open(args.input, "r", encoding="utf-8") as f:
        main_data = json.load(f)

    all_results = main_data.get("results", [])
    summary = main_data.get("summary", {})

    # 读取深挖结果（如果有）
    if args.dive_results:
        with open(args.dive_results, "r", encoding="utf-8") as f:
            dive_data = json.load(f)
        all_results.extend(dive_data.get("results", []))

    total_results = len(all_results)
    reliable_results = [r for r in all_results if r.get("credibility_score", 0) >= 40]
    filtered_count = total_results - len(reliable_results)
    reliable_count = len(reliable_results)

    print(f"[INFO] 总结果: {total_results}, 可信: {reliable_count}, 过滤: {filtered_count}", file=sys.stderr)

    # 提取型号数据
    model_data = extract_models_from_results(reliable_results)
    print(f"[INFO] 识别到 {len(model_data)} 个不同型号", file=sys.stderr)

    # 【V2】读取安全事件结果（如果有）
    safety_events = []
    if args.safety_results:
        with open(args.safety_results, "r", encoding="utf-8") as f:
            safety_data = json.load(f)
        safety_events = safety_data.get("safety_results", safety_data.get("results", []))
        print(f"[INFO] 加载安全事件结果: {len(safety_events)} 条", file=sys.stderr)

    # 【V2】从深挖结果中也提取安全事件
    if args.dive_results and not safety_events:
        with open(args.dive_results, "r", encoding="utf-8") as f:
            dive_data_raw = json.load(f)
        safety_events = dive_data_raw.get("safety_results", [])
        if safety_events:
            print(f"[INFO] 从深挖结果中提取安全事件: {len(safety_events)} 条", file=sys.stderr)

    # 提取 AI 统计（如果有）
    ai_stats = main_data.get("summary", {}).get("ai_analyzed_count")
    ai_stats_dict = None
    if ai_stats is not None:
        ai_stats_dict = {
            "session_analysis_count": main_data["summary"].get("ai_analyzed_count", 0),
            "cache_size": 0,
        }

    # 生成报告
    report = generate_markdown_report(
        model_data=model_data,
        query=args.query,
        budget=args.budget,
        pain_point=args.pain_point,
        total_results=total_results,
        filtered_count=filtered_count,
        reliable_count=reliable_count,
        safety_events=safety_events,
        ai_stats=ai_stats_dict,
        category_profile=category_profile,
        brand_scores=brand_scores,
    )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"[DONE] 报告已保存到: {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
