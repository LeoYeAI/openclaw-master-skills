#!/usr/bin/env python3
import argparse
import json
import re
from typing import Dict, Iterable, List

CATEGORY_MODIFIERS: Dict[str, List[str]] = {
    "education": [
        "评价", "口碑", "避雷", "靠不靠谱", "真实体验", "投诉", "退费",
        "虚假宣传", "课程质量", "师资", "就业", "offer", "录取", "学费", "合同",
        "隐形消费", "霸王条款", "维权", "中介", "保录", "保offer"
    ],
    "policy": [
        "政策", "新规", "通知", "官方回应", "执行", "解读", "影响", "整改",
        "监管", "实施", "变化", "风向"
    ],
    "gossip": [
        "八卦", "爆料", "热议", "争议", "翻车", "塌房", "后续", "回应",
        "聊天记录", "是真的吗", "真假", "瓜", "避雷"
    ],
    "local": [
        "推荐", "探店", "评价", "口碑", "避雷", "值得去吗", "排队", "菜品",
        "价格", "服务", "环境", "打卡", "攻略", "值不值"
    ],
    "general": [
        "评价", "口碑", "避雷", "体验", "投诉", "靠谱吗", "真实反馈",
        "最近", "热议", "怎么样", "值不值"
    ],
}

FAMILY_MODIFIERS: Dict[str, List[str]] = {
    "overview": ["小红书", "怎么样", "评价", "口碑"],
    "latest": ["最新", "最近", "近况", "本周", "本月"],
    "trending": ["热议", "爆了", "上热搜", "讨论", "风向", "后续"],
    "comment": ["评论", "评论区", "大家怎么说", "反馈", "吐槽"],
    "review": ["避雷", "体验", "值得吗", "投诉", "真实体验"],
    "recommendation": ["推荐", "值得去吗", "值不值", "攻略", "对比"],
    "verification": ["官方回应", "通知", "声明", "注册", "资质", "处罚", "法院", "备案"],
    "image": ["截图", "图片", "配图", "海报", "菜单", "聊天记录", "通知图"],
    "video": ["视频", "片段", "录像", "监控", "vlog", "gif", "动图"],
    "subtitle": ["字幕", "文案", "台词", "画面文字", "字幕截图"],
    "audio": ["录音", "语音", "音频", "直播录屏", "说了什么"],
}

SOURCE_PATTERNS = [
    "site:xiaohongshu.com {entity} {modifier}",
    "site:www.xiaohongshu.com {entity} {modifier}",
    "{entity} 小红书 {modifier}",
    "{entity} {modifier}",
]

CLAIM_LOG_TEMPLATE = {
    "claims": [
        {
            "claim_id": "c1",
            "claim_text": "...",
            "claim_type": "fact|allegation|praise|complaint|rumor|official statement|recommendation",
            "theme": ["pricing|service|policy|controversy|quality|fraud-risk|taste|queue|image-text|video|audio"],
            "entity": "",
            "time_scope": "",
            "geography": "",
            "status": "supported|mixed|weak|contradicted|unresolved",
            "confidence": "low|medium|high",
            "notes": ""
        }
    ],
    "evidence": [
        {
            "evidence_id": "e1",
            "claim_id": "c1",
            "source_url": "",
            "source_class": "official|media|first-hand|community|low-trust",
            "modality": "text-page|image|screenshot|video|gif|audio|mixed",
            "access_level": "direct file|fetched page|search snippet|quoted relay",
            "visible_date": "",
            "extract": "",
            "summary": "",
            "credibility": 0,
            "score": 0,
            "supports": "supports|partially-supports|contradicts|contextual-only"
        }
    ]
}

REPORT_TEMPLATE = {
    "snapshot": {
        "subject": "",
        "category": "education|policy|gossip|local|general",
        "time_scope": "",
        "overall_signal": "positive|mixed|caution|high risk|inconclusive",
        "confidence": "low|medium|high",
    },
    "main_findings": [
        "finding 1",
        "finding 2",
    ],
    "discussion_clusters": [
        {
            "theme": "pricing|quality|service|fraud risk|policy impact|taste|queue|environment|controversy|support",
            "summary": "",
            "repetition_count": 0,
            "sentiment": "positive|mixed|negative|split",
            "confidence": "low|medium|high",
        }
    ],
    "evidence": [
        {
            "credibility": 0,
            "score": 0,
            "theme": "refund|teaching|outcomes|pricing|support|legal|credentials|policy|controversy|taste|service|environment|image-text|video|audio",
            "summary": "",
            "source_class": "official|media|first-hand|community|low-trust",
            "modality": "text-page|image|screenshot|video|gif|audio|mixed",
            "access_level": "direct file|fetched page|search snippet|quoted relay",
            "url": "",
            "date": "",
        }
    ],
    "unverified": [""],
    "next_checks": [""],
}


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def split_csv(values: Iterable[str]) -> List[str]:
    out: List[str] = []
    for value in values:
        for item in value.split(","):
            item = clean_text(item)
            if item:
                out.append(item)
    return out


def dedupe(items: Iterable[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in items:
        normalized = clean_text(item)
        if normalized and normalized not in seen:
            seen.add(normalized)
            out.append(normalized)
    return out


def combined_modifiers(category: str, families: List[str]) -> List[str]:
    base = ["小红书"] + CATEGORY_MODIFIERS.get(category, CATEGORY_MODIFIERS["general"])
    family_terms: List[str] = []
    for family in families:
        family_terms.extend(FAMILY_MODIFIERS.get(family, []))
    return dedupe(base + family_terms)


def validate_families(families: List[str]) -> List[str]:
    allowed = set(FAMILY_MODIFIERS)
    invalid = [family for family in families if family not in allowed]
    if invalid:
        raise SystemExit(
            "Invalid family value(s): "
            + ", ".join(invalid)
            + ". Allowed values: "
            + ", ".join(sorted(allowed))
        )
    return families


def apply_time_scope(terms: Iterable[str], time_scope: str) -> List[str]:
    scope = clean_text(time_scope)
    if not scope:
        return list(terms)
    return dedupe(list(terms) + [scope])


def build_queries(
    entity: str,
    category: str,
    families: List[str],
    aliases: List[str],
    peers: List[str],
    geography: List[str],
    time_scope: str,
    limit: int,
) -> List[str]:
    modifiers = apply_time_scope(combined_modifiers(category, families), time_scope)
    names = dedupe([entity] + aliases)
    places = dedupe(geography)
    queries: List[str] = []

    for name in names:
        for modifier in modifiers:
            for pattern in SOURCE_PATTERNS:
                queries.append(pattern.format(entity=name, modifier=modifier).replace("小红书 小红书", "小红书"))
            for place in places:
                geo_modifier = modifier.replace("小红书", "").strip() or "小红书"
                queries.append(f"{place} {name} 小红书 {geo_modifier}".replace("小红书 小红书", "小红书"))
                queries.append(f"{name} {place} {geo_modifier}".replace("小红书 小红书", "小红书"))

    for name in names:
        for family in families:
            if family == "latest":
                queries.extend([
                    f"{name} 最新",
                    f"{name} 最近",
                    f"{name} 最新消息",
                    f"{name} 官方回应",
                ])
            elif family == "trending":
                queries.extend([
                    f"{name} 热议",
                    f"{name} 爆料",
                    f"{name} 后续",
                    f"{name} 争议",
                ])
            elif family == "comment":
                queries.extend([
                    f"{name} 评论区",
                    f"{name} 评论 怎么说",
                    f"{name} 吐槽",
                    f"{name} 反馈",
                ])
            elif family == "review":
                queries.extend([
                    f"{name} 真实体验",
                    f"{name} 避雷",
                    f"{name} 值不值",
                    f"{name} 怎么样",
                ])
            elif family == "recommendation":
                queries.extend([
                    f"{name} 推荐吗",
                    f"{name} 攻略",
                    f"{name} 对比",
                    f"{name} 值得去吗",
                ])
            elif family == "verification":
                queries.extend([
                    f"{name} 官方回应",
                    f"{name} 声明",
                    f"{name} 注册",
                    f"{name} 资质",
                    f"{name} 处罚",
                ])
            elif family == "image":
                queries.extend([
                    f"{name} 截图",
                    f"{name} 图片",
                    f"{name} 聊天记录",
                    f"{name} 菜单 图",
                ])
            elif family == "video":
                queries.extend([
                    f"{name} 视频",
                    f"{name} 片段",
                    f"{name} 录屏",
                    f"{name} gif",
                ])
            elif family == "subtitle":
                queries.extend([
                    f"{name} 字幕",
                    f"{name} 台词",
                    f"{name} 画面文字",
                    f"{name} 字幕截图",
                ])
            elif family == "audio":
                queries.extend([
                    f"{name} 录音",
                    f"{name} 语音",
                    f"{name} 音频",
                    f"{name} 说了什么",
                ])

    for name in names:
        for peer in peers:
            queries.append(f"{name} vs {peer}")
            queries.append(f"{name} {peer} 对比")
            queries.append(f"{name} 和 {peer} 怎么选")

    if time_scope:
        queries = [f"{query} {time_scope}" if time_scope not in query else query for query in queries]

    return dedupe(queries)[:limit]


def to_markdown(payload: Dict[str, object], include_claim_log: bool) -> str:
    lines = [f"# Research starter: {payload['entity']}", ""]
    lines.append(f"- Category: {payload['category']}")
    lines.append(f"- Families: {', '.join(payload['families'])}")
    if payload["aliases"]:
        lines.append(f"- Aliases: {', '.join(payload['aliases'])}")
    if payload["geography"]:
        lines.append(f"- Geography: {', '.join(payload['geography'])}")
    if payload["time_scope"]:
        lines.append(f"- Time scope hint: {payload['time_scope']}")
    if payload["peers"]:
        lines.append(f"- Comparison targets: {', '.join(payload['peers'])}")
    lines.extend(["", "## Recommended queries"])
    for idx, query in enumerate(payload["recommended_queries"], start=1):
        lines.append(f"{idx}. {query}")
    lines.extend([
        "",
        "## Suggested search order",
        "1. Run 3-5 overview/review queries to map the topic.",
        "2. Run 2-4 verification queries before trusting viral claims.",
        "3. If media matters, run image/video/subtitle/audio queries before concluding.",
        "4. Turn the strongest claims into a claim log before writing the final summary.",
        "",
        "## Normalized report template",
        "```json",
        json.dumps(REPORT_TEMPLATE, ensure_ascii=False, indent=2),
        "```",
    ])
    if include_claim_log:
        lines.extend([
            "",
            "## Structured claim log template",
            "```json",
            json.dumps(CLAIM_LOG_TEMPLATE, ensure_ascii=False, indent=2),
            "```",
        ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build RedNote/Xiaohongshu public-web research queries and normalized evidence templates.")
    parser.add_argument("keyword", help="Entity or topic to research")
    parser.add_argument("--category", default="general", choices=["education", "policy", "gossip", "local", "general"], help="Choose the topic category")
    parser.add_argument("--family", action="append", default=[], help="Query family to emphasize; repeatable or comma-separated")
    parser.add_argument("--alias", action="append", default=[], help="Alias or alternate name; repeatable or comma-separated")
    parser.add_argument("--peer", action="append", default=[], help="Optional comparison target; repeatable or comma-separated")
    parser.add_argument("--geo", action="append", default=[], help="City, district, mall, campus, or market; repeatable or comma-separated")
    parser.add_argument("--time-scope", default="", help="Optional time hint such as '近7天' or '2026' to append to queries")
    parser.add_argument("--limit", type=int, default=18, help="Maximum query count")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of markdown")
    parser.add_argument("--claim-log", action="store_true", help="Include the structured claim log template in the output")
    args = parser.parse_args()

    entity = clean_text(args.keyword)
    default_families = ["overview", "review", "verification"]
    families = validate_families(dedupe(split_csv(args.family)) or default_families)
    aliases = dedupe(split_csv(args.alias))
    peers = dedupe(split_csv(args.peer))
    geography = dedupe(split_csv(args.geo))

    queries = build_queries(
        entity=entity,
        category=args.category,
        families=families,
        aliases=aliases,
        peers=peers,
        geography=geography,
        time_scope=args.time_scope,
        limit=args.limit,
    )

    payload = {
        "entity": entity,
        "category": args.category,
        "families": families,
        "aliases": aliases,
        "peers": peers,
        "geography": geography,
        "time_scope": clean_text(args.time_scope),
        "recommended_queries": queries,
        "normalized_report_template": REPORT_TEMPLATE,
    }
    if args.claim_log:
        payload["claim_log_template"] = CLAIM_LOG_TEMPLATE

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print(to_markdown(payload, include_claim_log=args.claim_log))


if __name__ == "__main__":
    main()
