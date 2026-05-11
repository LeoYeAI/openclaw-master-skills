#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态深挖搜索工具

根据初始搜索中发现的高频提及型号，自动生成负面长尾关键词搜索，
专门挖掘质量问题、售后纠纷、长期使用后的真实反馈。

用法:
    # 手动指定型号进行深挖
    python deep_dive_search.py "西昊M57" --platforms zhihu,v2ex,tieba --days 730

    # 从初始搜索结果中自动提取高频型号并深挖
    python deep_dive_search.py --auto-extract search_results.json --platforms zhihu,v2ex,tieba --days 730

    # 自定义负面关键词
    python deep_dive_search.py "永艺XY" --negative-keywords "坏了,异响,退货,后悔"
"""

import argparse
import json
import re
import sys
import time
from collections import Counter
from datetime import datetime

# 导入同目录的搜索模块
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from platform_search import search_all_platforms, search_bing, fetch_page_content, PLATFORMS, ALL_PLATFORMS, DEFAULT_PLATFORMS


# ============================================================
# 默认负面长尾关键词
# ============================================================

DEFAULT_NEGATIVE_KEYWORDS = [
    # 质量问题
    "质量问题", "坏了", "异响", "塌陷", "松动", "断裂", "开裂",
    "脱皮", "掉漆", "生锈", "变形", "磨损", "漏气",
    # 售后体验
    "售后", "维修", "退货", "退款", "投诉", "维权", "客服态度",
    # 使用感受（负面）
    "后悔", "踩坑", "避坑", "不推荐", "翻车", "智商税",
    "不值", "失望", "上当", "骗人",
    # 长期使用
    "半年后", "一年后", "两年后", "长期使用", "耐久",
]

# 补充：针对特定品类的负面关键词
CATEGORY_NEGATIVE_KEYWORDS = {
    "椅": ["气压棒", "坐垫塌", "腰靠", "网布松", "扶手松", "头枕", "轮子", "底盘"],
    "显示器": ["漏光", "坏点", "色差", "闪屏", "拖影", "PWM", "接口"],
    "床垫": ["塌陷", "异味", "甲醛", "偏硬", "偏软", "腰疼", "弹簧响"],
    "键盘": ["轴体", "卫星轴", "润滑", "大键", "连击", "掉键帽"],
    "耳机": ["夹耳", "漏音", "断连", "底噪", "头梁", "耳罩"],
    "手机": ["发热", "续航", "信号", "屏幕", "系统", "卡顿"],
    # 【V2 新增】母婴品类
    "奶粉": ["便秘", "上火", "腹泻", "过敏", "拒奶", "吐奶", "湿疹", "绿便", "奶瓣",
            "召回", "污染", "超标", "毒素", "细菌", "重金属", "双标", "特供"],
    "纸尿裤": ["红屁股", "漏尿", "断层", "起坨", "过敏", "荧光剂", "异味"],
    "婴儿": ["便秘", "过敏", "湿疹", "召回", "安全", "毒素", "甲醛", "细菌"],
    "辅食": ["重金属", "农药残留", "添加剂", "过敏", "召回", "超标"],
    # 【V2 新增】食品品类
    "食品": ["添加剂", "防腐剂", "超标", "召回", "变质", "异物", "过期", "虚假宣传"],
    "保健品": ["虚假宣传", "副作用", "无效", "投诉", "夸大", "违规", "禁令"],
    # 【V2 新增】家电品类
    "空调": ["噪音", "制冷差", "漏水", "故障", "维修贵", "售后差"],
    "洗衣机": ["噪音", "漏水", "故障", "不脱水", "异味", "维修"],
    "冰箱": ["噪音", "制冷差", "结霜", "故障", "耗电", "异味"],
    # 【V2 新增】数码品类
    "笔记本": ["散热", "屏幕", "键盘", "续航", "蓝屏", "售后"],
    "平板": ["发热", "续航", "屏幕", "系统", "卡顿", "售后"],
    "路由器": ["断网", "信号差", "发热", "固件", "掉速"],
}


# ============================================================
# 【V2 新增】安全事件专项搜索
# ============================================================

SAFETY_SEARCH_KEYWORDS = [
    # 食品安全
    "召回", "下架", "禁售", "通报", "处罚", "检测不合格", "超标",
    "污染", "毒素", "细菌", "异物", "变质",
    # 产品安全
    "自燃", "爆炸", "漏电", "触电", "起火", "烫伤",
    # 监管动作
    "市场监管", "食药监", "FDA", "EFSA", "海关", "黑名单",
    # 舆论事件
    "曝光", "暴雷", "翻车", "丑闻", "造假", "欺诈",
]

# 安全事件搜索分组（每组一次搜索，减少请求数）
SAFETY_SEARCH_GROUPS = [
    "召回 下架 禁售",
    "污染 毒素 超标 检测不合格",
    "曝光 暴雷 丑闻 翻车",
    "市场监管 通报 处罚",
]

# 信息源类型标注
SOURCE_TYPES = {
    "community_discussion": "社区讨论",      # 知乎/V2EX/NGA等
    "news_report": "新闻报道",              # 新闻网站
    "official_announcement": "官方通告",     # 市场监管/品牌官方
    "ecommerce_review": "电商评论",         # 京东/天猫评论
    "safety_alert": "安全警报",             # 召回通知/食品安全通报
}

# 安全警报来源域名识别
SAFETY_SOURCE_PATTERNS = {
    r"samr\.gov\.cn": "official_announcement",     # 市场监管总局
    r"cfs\.gov\.hk": "official_announcement",      # 香港食安中心
    r"fda\.gov": "official_announcement",          # 美国FDA
    r"efsa\.europa\.eu": "official_announcement",  # 欧盟EFSA
    r"recall|召回": "safety_alert",
    r"news|新闻|报道|sina|sohu|163\.com|qq\.com": "news_report",
    r"jd\.com|taobao|tmall": "ecommerce_review",
}


def classify_source_type(url, title=""):
    """
    【V2 新增】根据 URL 和标题判断信息源类型

    Args:
        url: 结果 URL
        title: 结果标题

    Returns:
        信息源类型字符串
    """
    combined = f"{url} {title}"
    for pattern, source_type in SAFETY_SOURCE_PATTERNS.items():
        if re.search(pattern, combined, re.IGNORECASE):
            return source_type
    return "community_discussion"


# ============================================================
# 【V3 新增】通用安全事件分级（双层架构）
# ============================================================

# 通用安全事件触发词（品类无关）
UNIVERSAL_CRITICAL_PATTERNS = [
    r"全球.*召回", r"紧急.*召回", r"大规模.*召回",
    r"致死", r"死亡", r"致命",
    r"FDA.*warning", r"强制.*下架",
]

UNIVERSAL_HIGH_PATTERNS = [
    r"召回", r"下架", r"禁售",
    r"市场监管.*通报", r"检测不合格",
    r"超标",
]

UNIVERSAL_MEDIUM_PATTERNS = [
    r"整改", r"已.*处理", r"曾.*被",
    r"历史.*问题",
]

UNIVERSAL_LOW_PATTERNS = [
    r"投诉", r"异物", r"异味", r"争议", r"质疑",
]


def classify_severity(title, snippet, source_type, url, category_profile=None):
    """
    【V3 新增】通用安全事件分级（双层逻辑）

    第一层：通用规则（品类无关的严重事件关键词）
    第二层：品类规则（从 category_profile.safety_risk_types 读取）

    Args:
        title: 事件标题
        snippet: 事件摘要
        source_type: 信息源类型（official_announcement/news_report/safety_alert 等）
        url: 事件 URL
        category_profile: AI 生成的品类配置（可选）

    Returns:
        严重等级: "CRITICAL"/"HIGH"/"MEDIUM"/"LOW"/"INFO"
    """
    text = f"{title} {snippet}".lower()

    # 第一层：通用规则
    for p in UNIVERSAL_CRITICAL_PATTERNS:
        if re.search(p, text):
            return "CRITICAL"

    # 第二层：品类特定规则（从 AI 生成的 category_profile 读取）
    if category_profile:
        category_risks = category_profile.get("safety_risk_types", {})

        for keyword in category_risks.get("critical", []):
            if keyword.lower() in text:
                return "CRITICAL"

    # 如果是官方通告/安全警报来源，默认至少 HIGH
    if source_type in ("official_announcement", "safety_alert"):
        return "HIGH"

    # 品类 HIGH 规则
    if category_profile:
        category_risks = category_profile.get("safety_risk_types", {})
        for keyword in category_risks.get("high", []):
            if keyword.lower() in text:
                return "HIGH"

    # 通用 HIGH 规则
    for p in UNIVERSAL_HIGH_PATTERNS:
        if re.search(p, text):
            return "HIGH"

    # 品类 MEDIUM 规则
    if category_profile:
        category_risks = category_profile.get("safety_risk_types", {})
        for keyword in category_risks.get("medium", []):
            if keyword.lower() in text:
                return "MEDIUM"

    for p in UNIVERSAL_MEDIUM_PATTERNS:
        if re.search(p, text):
            return "MEDIUM"

    # 品类 LOW 规则
    if category_profile:
        category_risks = category_profile.get("safety_risk_types", {})
        for keyword in category_risks.get("low", []):
            if keyword.lower() in text:
                return "LOW"

    for p in UNIVERSAL_LOW_PATTERNS:
        if re.search(p, text):
            return "LOW"

    return "INFO"


def apply_safety_cap(overall_score, safety_score, category_type):
    """
    【V3 新增】安全风险封顶规则（品类自适应）

    不同品类对安全的容忍度不同：
    - food/personal_care：安全容忍度最低
    - electronics：安全容忍度中等
    - durable_goods：安全容忍度较高

    Args:
        overall_score: 商品综合分
        safety_score: 安全维度分数
        category_type: 品类类型

    Returns:
        封顶后的综合分
    """
    safety_caps = {
        "food": {"threshold": 30, "max_score": 54},
        "personal_care": {"threshold": 25, "max_score": 54},
        "electronics": {"threshold": 20, "max_score": 54},
        "durable_goods": {"threshold": 15, "max_score": 54},
        "service": {"threshold": 20, "max_score": 54},
        "other": {"threshold": 20, "max_score": 54},
    }
    cap = safety_caps.get(category_type, safety_caps["other"])

    if safety_score < cap["threshold"]:
        return min(overall_score, cap["max_score"])
    return overall_score


def safety_event_search(brand_or_model, days=365, extra_safety_keywords=None, category_profile=None):
    """
    【V3 升级】对单个品牌/型号进行安全事件专项搜索

    不限于特定平台，使用全网搜索（不加 site: 限定），
    因为安全事件通常由新闻媒体、监管机构首先报道。

    V3 升级：支持从 category_profile.safety_risk_types 读取品类特定安全关键词，
    并使用 classify_severity 进行双层安全分级。

    Args:
        brand_or_model: 品牌或型号名称
        days: 搜索时间范围（默认最近1年）
        extra_safety_keywords: AI痛点分析生成的额外安全关键词
        category_profile: 【V3】AI 生成的品类配置

    Returns:
        去重后的安全事件搜索结果列表
    """
    current_year = datetime.now().year
    results = []

    # 策略1：品牌 + 通用安全关键词分组搜索
    for group in SAFETY_SEARCH_GROUPS:
        query = f"{brand_or_model} {group} {current_year}"
        print(f"[SAFETY] 安全事件搜索: {query}", file=sys.stderr)
        group_results = search_bing(query, site=None, count=10, days=days)
        for r in group_results:
            r["search_type"] = "safety_event"
            r["dive_model"] = brand_or_model
            r["source_type"] = classify_source_type(r.get("url", ""), r.get("title", ""))
            # 【V3】使用双层分级
            r["severity"] = classify_severity(
                r.get("title", ""), r.get("snippet", ""),
                r["source_type"], r.get("url", ""),
                category_profile=category_profile,
            )
        results.extend(group_results)
        time.sleep(1.0)

    # 策略2：品类特定安全关键词（从 category_profile 读取，V3 优先级最高）
    if category_profile:
        safety_risks = category_profile.get("safety_risk_types", {})
        category_safety_keywords = []
        for level_keywords in safety_risks.values():
            if isinstance(level_keywords, list):
                category_safety_keywords.extend(level_keywords[:3])  # 每级取前3个
        # 分组搜索
        for i in range(0, len(category_safety_keywords), 3):
            kw_group = " ".join(category_safety_keywords[i:i+3])
            query = f"{brand_or_model} {kw_group} {current_year}"
            print(f"[SAFETY] 品类安全搜索(category_profile): {query}", file=sys.stderr)
            group_results = search_bing(query, site=None, count=5, days=days)
            for r in group_results:
                r["search_type"] = "safety_event"
                r["dive_model"] = brand_or_model
                r["source_type"] = classify_source_type(r.get("url", ""), r.get("title", ""))
                r["severity"] = classify_severity(
                    r.get("title", ""), r.get("snippet", ""),
                    r["source_type"], r.get("url", ""),
                    category_profile=category_profile,
                )
            results.extend(group_results)
            time.sleep(0.8)

    # 策略3：AI 生成的额外品类安全关键词（兼容 V2）
    elif extra_safety_keywords:
        for kw in extra_safety_keywords[:5]:  # 最多5组额外搜索
            query = f"{brand_or_model} {kw} {current_year}"
            print(f"[SAFETY] 品类安全搜索: {query}", file=sys.stderr)
            group_results = search_bing(query, site=None, count=5, days=days)
            for r in group_results:
                r["search_type"] = "safety_event"
                r["dive_model"] = brand_or_model
                r["source_type"] = classify_source_type(r.get("url", ""), r.get("title", ""))
                r["severity"] = classify_severity(
                    r.get("title", ""), r.get("snippet", ""),
                    r["source_type"], r.get("url", ""),
                    category_profile=category_profile,
                )
            results.extend(group_results)
            time.sleep(0.8)

    # 去重
    seen = set()
    unique = []
    for r in results:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique.append(r)

    print(f"[SAFETY] {brand_or_model} 安全事件搜索共获取 {len(unique)} 条结果", file=sys.stderr)
    return unique


# ============================================================
# 型号提取
# ============================================================

def extract_model_mentions(results, min_mentions=2):
    """
    从搜索结果中提取被频繁提及的产品型号

    Args:
        results: 搜索结果列表
        min_mentions: 最少提及次数阈值

    Returns:
        按提及频次排序的型号列表: [(型号名, 频次), ...]
    """
    # 常见的品牌+型号模式
    model_patterns = [
        # 中文品牌 + 英文/数字型号: 西昊M57, 永艺XY, 网易严选S9
        r"([\u4e00-\u9fa5]{2,6}[A-Za-z]+\d*[A-Za-z]*\d*)",
        # 英文品牌 + 型号: Herman Miller Aeron, Steelcase Leap
        r"([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Za-z0-9]+)?)",
        # 纯英文型号（常见于数码产品）: IKEA MARKUS
        r"([A-Z]{2,}\s+[A-Z][A-Za-z0-9]+)",
        # 品牌+系列: 西昊 Doro-C300
        r"([\u4e00-\u9fa5]{2,4}\s*[A-Za-z]+[\-]?[A-Za-z]*\d+[A-Za-z]*\d*)",
    ]

    mention_counter = Counter()

    for r in results:
        text = " ".join([
            r.get("title", ""),
            r.get("snippet", ""),
            r.get("content", ""),
        ])

        for pattern in model_patterns:
            matches = re.findall(pattern, text)
            for m in matches:
                m = m.strip()
                # 过滤过短或过长的匹配
                if 3 <= len(m) <= 30:
                    mention_counter[m] += 1

    # 过滤低频提及
    frequent = [(model, count) for model, count in mention_counter.most_common(20)
                if count >= min_mentions]

    return frequent


def get_category_keywords(query):
    """根据搜索词匹配品类特定的负面关键词"""
    extra_keywords = []
    for category, keywords in CATEGORY_NEGATIVE_KEYWORDS.items():
        if category in query:
            extra_keywords.extend(keywords)
    return extra_keywords


def get_negative_keywords(query, ai_generated_keywords=None, category_profile=None):
    """
    【V3 升级】获取负面搜索关键词（三级优先级）

    优先级：
    1. category_profile 中的 pain_point_keywords（最优，V3 主路径）
    2. AI 实时生成的痛点关键词（次优）
    3. 硬编码字典匹配（兜底 fallback）
    4. 通用负面关键词（最终兜底）

    Args:
        query: 搜索关键词（用于品类匹配）
        ai_generated_keywords: AI 痛点分析步骤生成的关键词列表
        category_profile: 【V3】AI 生成的品类配置

    Returns:
        去重后的负面关键词列表
    """
    keywords = []

    # 优先级1：从 category_profile 读取
    if category_profile:
        pain_points = category_profile.get("pain_point_keywords", {})
        for category_keywords in pain_points.values():
            if isinstance(category_keywords, list):
                keywords.extend(category_keywords)
        if keywords:
            print(f"[INFO] 使用 category_profile 中的 {len(keywords)} 个痛点关键词", file=sys.stderr)
            keywords.extend(DEFAULT_NEGATIVE_KEYWORDS)  # 追加通用词
            return list(dict.fromkeys(keywords))

    # 优先级2：AI 实时生成
    if ai_generated_keywords:
        keywords = ai_generated_keywords + DEFAULT_NEGATIVE_KEYWORDS
        print(f"[INFO] 使用 AI 生成的 {len(ai_generated_keywords)} 个痛点关键词", file=sys.stderr)
        return list(dict.fromkeys(keywords))

    # 优先级3：硬编码字典（兜底 fallback）
    category_kw = get_category_keywords(query)
    if category_kw:
        keywords = category_kw + DEFAULT_NEGATIVE_KEYWORDS
        print(f"[FALLBACK] 使用硬编码品类关键词: {len(category_kw)} 个", file=sys.stderr)
        return list(dict.fromkeys(keywords))

    # 优先级4：纯通用词
    print(f"[FALLBACK] 仅使用通用负面关键词", file=sys.stderr)
    return DEFAULT_NEGATIVE_KEYWORDS.copy()


# ============================================================
# 深挖搜索逻辑
# ============================================================

def deep_dive_single_model(model_name, negative_keywords, platforms, count=10, days=730):
    """
    对单个型号进行负面长尾搜索

    Args:
        model_name: 型号名称
        negative_keywords: 负面关键词列表
        platforms: 搜索平台列表
        count: 每组关键词返回数量
        days: 搜索时间范围

    Returns:
        搜索结果列表
    """
    all_results = []

    # 策略1: 型号 + 每个负面关键词单独搜索（最精准）
    # 为避免过多请求，将关键词分组，每组 2-3 个
    keyword_groups = []
    for i in range(0, len(negative_keywords), 3):
        group = negative_keywords[i:i+3]
        keyword_groups.append(" ".join(group))

    for group_query in keyword_groups[:5]:  # 最多 5 组，避免过度搜索
        query = f"{model_name} {group_query}"
        print(f"[DIVE] 深挖搜索: {query}", file=sys.stderr)
        results = search_all_platforms(
            query=query,
            platforms=platforms,
            count=count,
            days=days,
        )
        for r in results:
            r["dive_query"] = query
            r["dive_model"] = model_name
            r["dive_type"] = "negative_longtail"
        all_results.extend(results)

    # 策略2: 型号 + "长期使用" 类搜索（找长期反馈）
    longtail_queries = [
        f"{model_name} 用了一年",
        f"{model_name} 长期使用感受",
        f"{model_name} 半年 真实",
    ]
    for q in longtail_queries:
        print(f"[DIVE] 长期反馈搜索: {q}", file=sys.stderr)
        results = search_all_platforms(
            query=q,
            platforms=platforms,
            count=max(5, count // 2),
            days=days,
        )
        for r in results:
            r["dive_query"] = q
            r["dive_model"] = model_name
            r["dive_type"] = "longterm_feedback"
        all_results.extend(results)

    # 去重
    seen = set()
    unique = []
    for r in all_results:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique.append(r)

    return unique


# ============================================================
# 【V5 新增】电商追评深挖 & 评论区深挖
# ============================================================

# 电商追评深挖关键词模板
ECOMMERCE_DIVE_TEMPLATES = [
    "{model} 京东 追评 差评 长期使用",
    "{model} 淘宝 追评 后悔 退货 售后",
    "{model} 电商评价 差评合集 真实反馈",
    "{model} 京东评论 一星 质量问题 坏了",
    "{model} 追评 半年后 一年后 问题",
    "{model} 买家真实评价 缺点 不好",
]

# 评论区深挖关键词模板
COMMENT_DIVE_TEMPLATES = [
    "{model} 小红书 评论区 翻车 踩坑",
    "{model} 知乎 评论区 真实体验 和说的不一样",
    "{model} 种草 拔草 买了后悔 真相",
    "{model} 博主推荐 实际 差距大 评论",
]


def ecommerce_dive_single_model(model_name, count=8, days=730, category_profile=None):
    """
    【V5 新增】对单个型号执行电商追评深挖搜索

    通过间接搜索策略获取京东/淘宝/拼多多的真实购买评论。
    重点搜索：追评、差评、长期使用反馈。

    Args:
        model_name: 型号名称
        count: 每组关键词返回数量
        days: 搜索时间范围
        category_profile: 品类配置

    Returns:
        搜索结果列表
    """
    all_results = []

    # 从 category_profile 获取电商搜索模板（如果有）
    templates = ECOMMERCE_DIVE_TEMPLATES.copy()
    if category_profile:
        ecom_strategy = category_profile.get("ecommerce_search_strategy", {})
        if ecom_strategy.get("search_templates"):
            for template_list in ecom_strategy["search_templates"].values():
                for t in template_list:
                    templates.append(t.replace("[商品]", "{model}"))

    # 去重模板
    templates = list(dict.fromkeys(templates))

    for template in templates[:8]:  # 最多8组搜索
        query = template.replace("{model}", model_name)
        print(f"[L1-DIVE] 电商追评深挖: {query}", file=sys.stderr)
        raw_results = search_bing(query, site=None, count=count, days=days)

        for r in raw_results:
            r["source_layer"] = "L1_ecommerce"
            r["search_type"] = "ecommerce_dive"
            r["dive_model"] = model_name
            r["dive_type"] = "ecommerce_review_dive"
            r["base_weight"] = 0.85
            r["platform"] = "ecommerce_indirect"
            r["platform_name"] = "电商评论(间接)"
        all_results.extend(raw_results)
        time.sleep(0.8)

    # 去重
    seen = set()
    unique = []
    for r in all_results:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique.append(r)

    print(f"[L1-DIVE] {model_name} 电商追评深挖获取 {len(unique)} 条结果", file=sys.stderr)
    return unique


def comment_section_dive_single_model(model_name, count=6, days=730, category_profile=None):
    """
    【V5 新增】对单个型号执行评论区深挖搜索

    搜索种草帖评论区的拔草反馈、知乎评论区的实际体验分享。

    Args:
        model_name: 型号名称
        count: 每组关键词返回数量
        days: 搜索时间范围
        category_profile: 品类配置

    Returns:
        搜索结果列表
    """
    all_results = []

    templates = COMMENT_DIVE_TEMPLATES.copy()
    if category_profile:
        comment_strategy = category_profile.get("comment_section_strategy", {})
        if comment_strategy.get("search_templates"):
            for template_list in comment_strategy["search_templates"].values():
                for t in template_list:
                    templates.append(t.replace("[商品]", "{model}"))

    templates = list(dict.fromkeys(templates))

    for template in templates[:6]:
        query = template.replace("{model}", model_name)
        print(f"[L2-DIVE] 评论区深挖: {query}", file=sys.stderr)
        raw_results = search_bing(query, site=None, count=count, days=days)

        for r in raw_results:
            r["source_layer"] = "L2_comment_section"
            r["search_type"] = "comment_section_dive"
            r["dive_model"] = model_name
            r["dive_type"] = "comment_section_dive"
            r["base_weight"] = 0.75
            r["platform"] = "comment_section_indirect"
            r["platform_name"] = "评论区(间接)"
        all_results.extend(raw_results)
        time.sleep(0.8)

    seen = set()
    unique = []
    for r in all_results:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique.append(r)

    print(f"[L2-DIVE] {model_name} 评论区深挖获取 {len(unique)} 条结果", file=sys.stderr)
    return unique


def deep_dive_auto(initial_results_file, platforms, count=10, days=730,
                   negative_keywords=None, extra_keywords=None,
                   ai_generated_keywords=None, run_safety_search=True,
                   extra_safety_keywords=None, category_profile=None,
                   min_mentions=2, max_models=5,
                   ecommerce_dive=True, comment_dive=True):
    """
    从初始搜索结果中自动提取高频型号并执行深挖

    V5 升级：新增 ecommerce_dive 和 comment_dive 参数，
    在传统论坛深挖基础上自动执行电商追评深挖和评论区深挖。

    Args:
        initial_results_file: 初始搜索结果文件路径
        platforms: 搜索平台
        count: 每组搜索返回数
        days: 时间范围
        negative_keywords: 自定义负面关键词
        extra_keywords: 附加关键词
        ai_generated_keywords: AI 痛点分析步骤生成的关键词
        run_safety_search: 是否执行安全事件专项搜索
        extra_safety_keywords: AI 生成的品类安全关键词
        category_profile: 【V3】AI 生成的品类配置
        min_mentions: 最低提及次数
        max_models: 最多深挖型号数
        ecommerce_dive: 【V5】是否执行电商追评深挖（默认True）
        comment_dive: 【V5】是否执行评论区深挖（默认True）
    """
    # 读取初始搜索结果
    with open(initial_results_file, "r", encoding="utf-8") as f:
        initial_data = json.load(f)

    results = initial_data.get("results", [])
    original_query = initial_data.get("query", "")

    print(f"[AUTO] 从 {len(results)} 条初始结果中提取高频型号", file=sys.stderr)

    # 提取高频型号
    frequent_models = extract_model_mentions(results, min_mentions=min_mentions)

    if not frequent_models:
        print("[AUTO] 未发现高频提及的型号，跳过深挖", file=sys.stderr)
        return {"models_found": [], "dive_results": [], "safety_results": []}

    print(f"[AUTO] 发现 {len(frequent_models)} 个高频型号:", file=sys.stderr)
    for model, cnt in frequent_models[:max_models]:
        print(f"  - {model} (提及 {cnt} 次)", file=sys.stderr)

    # 【V3】使用三级优先级关键词获取
    if negative_keywords:
        keywords = negative_keywords
    else:
        keywords = get_negative_keywords(original_query, ai_generated_keywords, category_profile=category_profile)

    if extra_keywords:
        keywords.extend(extra_keywords)

    # 去重
    keywords = list(dict.fromkeys(keywords))

    # 对每个高频型号执行深挖
    all_dive_results = []
    all_safety_results = []
    models_info = []

    for model, mention_count in frequent_models[:max_models]:
        print(f"\n[AUTO] === 开始深挖: {model} (被提及 {mention_count} 次) ===", file=sys.stderr)
        dive_results = deep_dive_single_model(
            model_name=model,
            negative_keywords=keywords,
            platforms=platforms,
            count=count,
            days=days,
        )
        all_dive_results.extend(dive_results)

        # 【V5】电商追评深挖
        ecom_count = 0
        if ecommerce_dive:
            print(f"[AUTO] === 电商追评深挖: {model} ===", file=sys.stderr)
            ecom_results = ecommerce_dive_single_model(
                model_name=model,
                count=count,
                days=days,
                category_profile=category_profile,
            )
            all_dive_results.extend(ecom_results)
            ecom_count = len(ecom_results)

        # 【V5】评论区深挖
        comment_count = 0
        if comment_dive:
            print(f"[AUTO] === 评论区深挖: {model} ===", file=sys.stderr)
            comment_results = comment_section_dive_single_model(
                model_name=model,
                count=max(6, count // 2),
                days=days,
                category_profile=category_profile,
            )
            all_dive_results.extend(comment_results)
            comment_count = len(comment_results)

        # 安全事件专项搜索
        safety_count = 0
        if run_safety_search:
            print(f"[AUTO] === 安全事件搜索: {model} ===", file=sys.stderr)
            safety_results = safety_event_search(
                brand_or_model=model,
                days=365,
                extra_safety_keywords=extra_safety_keywords,
                category_profile=category_profile,
            )
            all_safety_results.extend(safety_results)
            safety_count = len(safety_results)

        models_info.append({
            "model": model,
            "initial_mentions": mention_count,
            "dive_results_count": len(dive_results),
            "ecommerce_dive_count": ecom_count,
            "comment_dive_count": comment_count,
            "safety_results_count": safety_count,
        })
        print(
            f"[AUTO] {model} 深挖获得 {len(dive_results)} 条论坛结果, "
            f"{ecom_count} 条电商评论, {comment_count} 条评论区, "
            f"{safety_count} 条安全事件",
            file=sys.stderr
        )

    return {
        "original_query": original_query,
        "models_found": models_info,
        "dive_results": all_dive_results,
        "safety_results": all_safety_results,
    }


# ============================================================
# 主程序
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="动态深挖搜索工具 - 针对高频型号进行负面长尾搜索",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 手动指定型号深挖
    python deep_dive_search.py "西昊M57" --days 730

    # 从初始搜索结果自动提取型号并深挖
    python deep_dive_search.py --auto-extract results.json --days 730

    # 自定义负面关键词
    python deep_dive_search.py "永艺XY" --negative-keywords "气压棒异响,坐垫塌陷,退货"
        """,
    )

    parser.add_argument(
        "model",
        nargs="?", default=None,
        help="要深挖的产品型号名称",
    )
    parser.add_argument(
        "--auto-extract", "-a",
        default=None,
        help="从初始搜索结果文件中自动提取高频型号进行深挖",
    )
    parser.add_argument(
        "--negative-keywords", "-n",
        default=None,
        help="自定义负面关键词（逗号分隔）。不指定则使用默认列表",
    )
    parser.add_argument(
        "--platforms", "-p",
        default=",".join(DEFAULT_PLATFORMS),
        help=f"搜索平台（逗号分隔）。默认: {','.join(DEFAULT_PLATFORMS)}",
    )
    parser.add_argument(
        "--count", "-c",
        type=int, default=10,
        help="每组关键词返回的结果数（默认 10）",
    )
    parser.add_argument(
        "--days", "-d",
        type=int, default=730,
        help="搜索时间范围，默认最近两年（730天）",
    )
    parser.add_argument(
        "--max-models", "-m",
        type=int, default=5,
        help="自动模式下最多深挖的型号数（默认 5）",
    )
    parser.add_argument(
        "--min-mentions",
        type=int, default=2,
        help="自动模式下型号最低提及次数阈值（默认 2）",
    )
    parser.add_argument(
        "--fetch-content", "-f",
        action="store_true",
        help="抓取每条结果的页面正文",
    )
    parser.add_argument(
        "--limit", "-l",
        type=int, default=None,
        help="抓取正文的数量限制",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="输出文件路径",
    )
    parser.add_argument(
        "--no-safety-search",
        action="store_true",
        help="【V2】禁用安全事件专项搜索",
    )
    parser.add_argument(
        "--ai-keywords",
        default=None,
        help="【V2】AI 生成的痛点关键词（逗号分隔）",
    )
    parser.add_argument(
        "--safety-keywords",
        default=None,
        help="【V2】AI 生成的品类安全关键词（逗号分隔）",
    )
    parser.add_argument(
        "--category-profile",
        default=None,
        help="【V3】品类配置文件路径（JSON 格式，由 AI 品类自适应分析生成）",
    )
    parser.add_argument(
        "--ecommerce-dive",
        action="store_true",
        default=True,
        help="【V5】启用电商追评深挖（默认启用）",
    )
    parser.add_argument(
        "--no-ecommerce-dive",
        action="store_true",
        help="【V5】禁用电商追评深挖",
    )
    parser.add_argument(
        "--comment-dive",
        action="store_true",
        default=True,
        help="【V5】启用评论区深挖（默认启用）",
    )
    parser.add_argument(
        "--no-comment-dive",
        action="store_true",
        help="【V5】禁用评论区深挖",
    )

    args = parser.parse_args()

    # 【V3】加载品类配置
    category_profile = None
    if args.category_profile:
        with open(args.category_profile, "r", encoding="utf-8") as f:
            category_profile = json.load(f)
        print(f"[INFO] 已加载品类配置: {category_profile.get('category', '未知品类')}", file=sys.stderr)

    # 解析平台
    if args.platforms.lower() == "all":
        platforms = ALL_PLATFORMS
    else:
        platforms = [p.strip() for p in args.platforms.split(",")]

    # 解析负面关键词
    if args.negative_keywords:
        neg_keywords = [k.strip() for k in args.negative_keywords.split(",")]
    else:
        neg_keywords = None

    # 【V2】解析 AI 生成的关键词
    ai_keywords = None
    if args.ai_keywords:
        ai_keywords = [k.strip() for k in args.ai_keywords.split(",")]

    safety_keywords = None
    if args.safety_keywords:
        safety_keywords = [k.strip() for k in args.safety_keywords.split(",")]

    run_safety = not args.no_safety_search

    # 【V5】解析电商追评和评论区深挖开关
    run_ecommerce_dive = not args.no_ecommerce_dive
    run_comment_dive = not args.no_comment_dive

    # 执行深挖
    if args.auto_extract:
        # 自动模式
        print(f"[INFO] 自动提取模式: 从 {args.auto_extract} 中提取高频型号", file=sys.stderr)
        if run_ecommerce_dive:
            print(f"[INFO] 电商追评深挖: 已启用", file=sys.stderr)
        if run_comment_dive:
            print(f"[INFO] 评论区深挖: 已启用", file=sys.stderr)
        dive_data = deep_dive_auto(
            initial_results_file=args.auto_extract,
            platforms=platforms,
            count=args.count,
            days=args.days,
            negative_keywords=neg_keywords,
            ai_generated_keywords=ai_keywords,
            run_safety_search=run_safety,
            extra_safety_keywords=safety_keywords,
            category_profile=category_profile,
            min_mentions=args.min_mentions,
            max_models=args.max_models,
            ecommerce_dive=run_ecommerce_dive,
            comment_dive=run_comment_dive,
        )
        all_results = dive_data["dive_results"]
        safety_results = dive_data.get("safety_results", [])
    elif args.model:
        # 手动模式
        keywords = neg_keywords or get_negative_keywords(args.model, ai_keywords, category_profile=category_profile)
        print(f"[INFO] 手动深挖模式: 型号 = {args.model}", file=sys.stderr)
        all_results = deep_dive_single_model(
            model_name=args.model,
            negative_keywords=keywords,
            platforms=platforms,
            count=args.count,
            days=args.days,
        )

        # 【V5】手动模式也执行电商追评深挖
        ecom_count = 0
        if run_ecommerce_dive:
            ecom_results = ecommerce_dive_single_model(
                model_name=args.model,
                count=args.count,
                days=args.days,
                category_profile=category_profile,
            )
            all_results.extend(ecom_results)
            ecom_count = len(ecom_results)

        # 【V5】手动模式也执行评论区深挖
        comment_count = 0
        if run_comment_dive:
            comment_results = comment_section_dive_single_model(
                model_name=args.model,
                count=max(6, args.count // 2),
                days=args.days,
                category_profile=category_profile,
            )
            all_results.extend(comment_results)
            comment_count = len(comment_results)

        # 手动模式也执行安全事件搜索
        safety_results = []
        if run_safety:
            safety_results = safety_event_search(
                brand_or_model=args.model,
                days=365,
                extra_safety_keywords=safety_keywords,
                category_profile=category_profile,
            )

        dive_data = {
            "original_query": args.model,
            "models_found": [{
                "model": args.model,
                "dive_results_count": len(all_results),
                "ecommerce_dive_count": ecom_count,
                "comment_dive_count": comment_count,
                "safety_results_count": len(safety_results),
            }],
            "dive_results": all_results,
            "safety_results": safety_results,
        }
    else:
        print("[ERROR] 请指定型号名称或使用 --auto-extract 从文件提取", file=sys.stderr)
        sys.exit(1)

    # 可选：抓取正文
    if args.fetch_content:
        fetch_limit = args.limit or len(all_results)
        print(f"[INFO] 抓取前 {fetch_limit} 条结果的正文", file=sys.stderr)
        for i, r in enumerate(all_results[:fetch_limit]):
            print(f"[INFO] 抓取 ({i+1}/{fetch_limit}): {r['url']}", file=sys.stderr)
            r["content"] = fetch_page_content(r["url"])
            time.sleep(1.0)

    # 输出
    print(f"\n[DONE] 深挖搜索完成，共获取 {len(all_results)} 条结果", file=sys.stderr)
    if safety_results:
        print(f"[DONE] 安全事件搜索获取 {len(safety_results)} 条结果", file=sys.stderr)

    output_data = {
        "search_type": "deep_dive",
        "search_time": datetime.now().isoformat(),
        "days": args.days,
        "models_found": dive_data.get("models_found", []),
        "total_results": len(all_results),
        "total_safety_results": len(safety_results),
        "results": all_results,
        "safety_results": safety_results,
    }

    json_str = json.dumps(output_data, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_str)
        print(f"[INFO] 结果已保存到: {args.output}", file=sys.stderr)
    else:
        print(json_str)


if __name__ == "__main__":
    main()
