#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-platform Real User Feedback Search Tool

Searches consumer communities via search engines (Bing/Google),
bypassing platform recommendation algorithms to get real discussion content.
Supports multiple languages and regions via category_profile configuration.

Usage:
    python platform_search.py "ergonomic chair back pain" --platforms reddit,amazon_reviews --days 365
    python platform_search.py "人体工学椅 腰肌劳损" --platforms zhihu,v2ex,smzdm --days 365 --count 20
"""

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import ssl
from collections import defaultdict
from datetime import datetime, timedelta
from html.parser import HTMLParser


# ============================================================
# Default Platform Configuration (zh-CN fallback)
# When category_profile provides regional_platforms, those take priority.
# ============================================================

PLATFORMS = {
    "zhihu": {
        "name": "Zhihu",
        "site": "zhihu.com",
        "description": "Chinese Q&A community, beware of high-upvote sponsored content",
        "base_weight": 0.55,
        "search_suffix": "",
    },
    "v2ex": {
        "name": "V2EX",
        "site": "v2ex.com",
        "description": "Tech community, low ad density",
        "base_weight": 0.9,
        "search_suffix": "",
    },
    "smzdm": {
        "name": "SMZDM",
        "site": "smzdm.com",
        "description": "Consumer decision community, original long-form content",
        "base_weight": 0.65,
        "search_suffix": "",
    },
    "nga": {
        "name": "NGA",
        "site": "nga.cn",
        "description": "Vertical forum community",
        "base_weight": 0.85,
        "search_suffix": "",
    },
    "tieba": {
        "name": "Baidu Tieba",
        "site": "tieba.baidu.com",
        "description": "Baidu forums, niche sub-forums have real discussions",
        "base_weight": 0.75,
        "search_suffix": "",
    },
    "xiaohongshu": {
        "name": "Xiaohongshu",
        "site": "xiaohongshu.com",
        "description": "Social commerce platform, high baseline ad probability",
        "base_weight": 0.3,
        "search_suffix": "",
    },
    "douban": {
        "name": "Douban",
        "site": "douban.com",
        "description": "Cultural community, relatively authentic consumer discussions",
        "base_weight": 0.8,
        "search_suffix": "",
    },
    "chiphell": {
        "name": "Chiphell",
        "site": "chiphell.com",
        "description": "Hardcore tech forum, highly knowledgeable users",
        "base_weight": 0.9,
        "search_suffix": "",
    },
}

ALL_PLATFORMS = list(PLATFORMS.keys())
DEFAULT_PLATFORMS = ["zhihu", "v2ex", "smzdm", "nga", "tieba"]


def load_platforms_from_profile(category_profile):
    """
    Load region-specific platform configuration from category_profile.
    If regional_platforms is provided, it REPLACES the default PLATFORMS dict.
    """
    global PLATFORMS, ALL_PLATFORMS, DEFAULT_PLATFORMS
    if category_profile and "regional_platforms" in category_profile:
        regional = category_profile["regional_platforms"]
        if regional:
            PLATFORMS = {}
            for key, config in regional.items():
                PLATFORMS[key] = {
                    "name": config.get("name", key),
                    "site": config.get("site", ""),
                    "description": config.get("description", ""),
                    "base_weight": config.get("base_weight", 0.5),
                    "search_suffix": config.get("search_suffix", ""),
                }
            ALL_PLATFORMS = list(PLATFORMS.keys())
            # Use top-weighted platforms as defaults
            sorted_platforms = sorted(PLATFORMS.items(), key=lambda x: x[1]["base_weight"], reverse=True)
            DEFAULT_PLATFORMS = [k for k, v in sorted_platforms[:5]]
            print(f"[INFO] Loaded {len(PLATFORMS)} regional platforms: {ALL_PLATFORMS}", file=sys.stderr)


# ============================================================
# E-commerce Review Indirect Search Config (zh-CN fallback)
# Overridden by category_profile.ecommerce_search_strategy
# ============================================================

ECOMMERCE_SEARCH_TEMPLATES = {
    "review_aggregation": [
        "{product} 京东评论 追评 真实",
        "{product} 淘宝评价 追评 差评",
        "{product} 电商评价 真实评价 买家",
    ],
    "negative_reviews": [
        "{product} 京东差评 一星 退货 原因",
        "{product} 淘宝差评 避坑 后悔 退款",
        "{product} 拼多多 差评 质量问题",
    ],
    "long_term_reviews": [
        "{product} 追评 用了半年 一年 使用感受",
        "{product} 京东追评 长期使用 后来发现",
        "{product} 追评 后悔 补充评价 几个月后",
    ],
}

ECOMMERCE_HIGH_VALUE_INDICATORS = [
    "追评", "用了几个月后", "补充评价", "再来更新",
    "买了半年", "长期使用后", "追加评论", "后续反馈",
]

ECOMMERCE_LOW_VALUE_INDICATORS = [
    "默认好评", "好评返现", "此用户未填写评价",
    "好评返", "五星好评", "系统默认",
]

COMMENT_SECTION_SEARCH_TEMPLATES = {
    "debunk_feedback": [
        "{product} 小红书 评论区 真实 翻车",
        "{product} 种草 买了 后悔 拔草",
        "{product} 博主推荐 评论区 和说的不一样",
    ],
    "experience_sharing": [
        "{product} 知乎 评论区 实际体验 反驳",
        "{product} 买了才知道 实际体验 坑",
        "{product} 评论区 真相 真实反馈 吐槽",
    ],
}

COMMENT_HIGH_VALUE_INDICATORS = [
    "我也买了", "同款翻车", "用了之后发现", "评论区才是真相",
    "不请自来", "买过的来说", "同款用户", "已购来反馈",
]

COMMENT_LOW_VALUE_INDICATORS = [
    "求链接", "已入手", "好种草", "链接在哪",
    "马上下单", "已下单",
]


def load_search_config_from_profile(category_profile):
    """
    Load region-specific search templates and indicators from category_profile.
    Overrides the default zh-CN templates when profile provides alternatives.
    """
    global ECOMMERCE_SEARCH_TEMPLATES, ECOMMERCE_HIGH_VALUE_INDICATORS, ECOMMERCE_LOW_VALUE_INDICATORS
    global COMMENT_SECTION_SEARCH_TEMPLATES, COMMENT_HIGH_VALUE_INDICATORS, COMMENT_LOW_VALUE_INDICATORS

    if not category_profile:
        return

    ecom = category_profile.get("ecommerce_search_strategy", {})
    if ecom.get("search_templates"):
        ECOMMERCE_SEARCH_TEMPLATES = ecom["search_templates"]
    if ecom.get("high_value_indicators"):
        ECOMMERCE_HIGH_VALUE_INDICATORS = ecom["high_value_indicators"]
    if ecom.get("low_value_indicators"):
        ECOMMERCE_LOW_VALUE_INDICATORS = ecom["low_value_indicators"]

    comment = category_profile.get("comment_section_strategy", {})
    if comment.get("search_templates"):
        COMMENT_SECTION_SEARCH_TEMPLATES = comment["search_templates"]
    if comment.get("high_value_indicators"):
        COMMENT_HIGH_VALUE_INDICATORS = comment["high_value_indicators"]
    if comment.get("low_value_indicators"):
        COMMENT_LOW_VALUE_INDICATORS = comment["low_value_indicators"]

    print(f"[INFO] Loaded region-specific search config from category_profile", file=sys.stderr)


# ============================================================
# 【V3 新增】动态平台权重
# ============================================================

def get_platform_weight(platform_key, category_profile=None):
    """
    【V3 新增】获取平台可信度权重（品类自适应）

    优先使用 AI 生成的品类相关权重，没有则回退到默认权重。

    Args:
        platform_key: 平台标识（如 zhihu, v2ex）
        category_profile: AI 生成的品类配置（可选）

    Returns:
        平台可信度权重（0-1）
    """
    # 默认权重（兜底）
    default_weight = PLATFORMS.get(platform_key, {}).get("base_weight", 0.5)

    if category_profile and "platform_relevance" in category_profile:
        return category_profile["platform_relevance"].get(platform_key, default_weight)

    return default_weight


def get_prioritized_platforms(platforms, category_profile=None):
    """
    【V3 新增】根据品类权重对平台排序，跳过权重过低的平台

    Args:
        platforms: 原始平台列表
        category_profile: AI 生成的品类配置（可选）

    Returns:
        按权重降序排列的平台列表（权重 < 0.2 的平台被跳过）
    """
    if not category_profile:
        return platforms

    platform_weights = []
    for p in platforms:
        weight = get_platform_weight(p, category_profile)
        platform_weights.append((p, weight))

    # 按权重降序排列，跳过权重过低的平台
    platform_weights.sort(key=lambda x: x[1], reverse=True)
    prioritized = [p for p, w in platform_weights if w >= 0.2]

    if len(prioritized) < len(platforms):
        skipped = [p for p, w in platform_weights if w < 0.2]
        print(f"[INFO] 根据品类权重跳过平台: {skipped}", file=sys.stderr)

    return prioritized


def generate_balanced_queries(product, category, category_profile=None):
    """
    【V3 新增】为每个商品生成均衡的搜索查询（品类关键词来自 AI）

    搜索均衡策略：40% 中性 + 20% 正面 + 40% 负面

    Args:
        product: 商品/品牌名
        category: 品类名
        category_profile: AI 生成的品类配置

    Returns:
        按搜索意图分类的查询字典 {"neutral": [...], "positive": [...], "negative": [...]}
    """
    pain_points = {}
    key_params = []

    if category_profile:
        pain_points = category_profile.get("pain_point_keywords", {})
        dimensions = category_profile.get("evaluation_dimensions", [])
        for dim in dimensions:
            key_params.extend(dim.get("key_parameters", [])[:2])

    queries = {
        "neutral": [
            f"{product} {category} 评测 对比",
        ],
        "positive": [
            f"{product} {category} 长期使用 满意",
        ],
        "negative": [],
    }

    # 中性搜索：加入关键参数
    if key_params:
        queries["neutral"].append(f"{product} {category} {' '.join(key_params[:4])}")

    # 负面搜索：从 pain_point_keywords 生成
    for pain_type in ["quality", "experience", "trust"]:
        kws = pain_points.get(pain_type, [])
        if kws:
            queries["negative"].append(f"{product} {category} {' '.join(kws[:3])}")

    # 如果没有 category_profile，使用通用负面词
    if not queries["negative"]:
        queries["negative"] = [
            f"{product} {category} 质量问题 售后 投诉",
            f"{product} {category} 后悔 踩坑 避坑",
        ]

    return queries


# ============================================================
# 【V5 新增】电商评论间接搜索
# ============================================================

def generate_ecommerce_queries(product, category_profile=None):
    """
    【V5 新增】生成电商评论间接搜索查询

    通过搜索"评论搬运帖"、"追评汇总"、"差评合集"等间接获取
    电商平台的真实购买评论。

    Args:
        product: 商品/品牌名
        category_profile: AI 生成的品类配置

    Returns:
        查询列表 [{"query": str, "search_type": str, "source_layer": str}]
    """
    queries = []

    # 优先使用 category_profile 中的电商搜索策略
    templates = ECOMMERCE_SEARCH_TEMPLATES
    if category_profile:
        ecom_strategy = category_profile.get("ecommerce_search_strategy", {})
        if ecom_strategy.get("enabled", True) and ecom_strategy.get("search_templates"):
            custom_templates = ecom_strategy["search_templates"]
            # 合并自定义模板（自定义优先）
            templates = {**ECOMMERCE_SEARCH_TEMPLATES, **custom_templates}

    for search_type, template_list in templates.items():
        for template in template_list:
            query = template.replace("{product}", product).replace("[商品]", product)
            queries.append({
                "query": query,
                "search_type": f"ecommerce_{search_type}",
                "source_layer": "L1_ecommerce",
            })

    return queries


def generate_comment_section_queries(product, category_profile=None):
    """
    【V5 新增】生成社交评论区间接搜索查询

    搜索种草帖评论区的"拔草"反馈、知乎评论区的反驳等。

    Args:
        product: 商品/品牌名
        category_profile: AI 生成的品类配置

    Returns:
        查询列表 [{"query": str, "search_type": str, "source_layer": str}]
    """
    queries = []

    # 优先使用 category_profile 中的评论区搜索策略
    templates = COMMENT_SECTION_SEARCH_TEMPLATES
    if category_profile:
        comment_strategy = category_profile.get("comment_section_strategy", {})
        if comment_strategy.get("enabled", True) and comment_strategy.get("search_templates"):
            custom_templates = comment_strategy["search_templates"]
            templates = {**COMMENT_SECTION_SEARCH_TEMPLATES, **custom_templates}

    for search_type, template_list in templates.items():
        for template in template_list:
            query = template.replace("{product}", product).replace("[商品]", product)
            queries.append({
                "query": query,
                "search_type": f"comment_{search_type}",
                "source_layer": "L2_comment_section",
            })

    return queries


def search_ecommerce_reviews(product, count=10, days=730, category_profile=None):
    """
    【V5 新增】执行电商评论间接搜索

    Args:
        product: 商品/品牌名
        count: 每个查询返回的结果数
        days: 搜索时间范围
        category_profile: 品类配置

    Returns:
        搜索结果列表，每条结果带有 source_layer 和 ecommerce 相关标记
    """
    queries = generate_ecommerce_queries(product, category_profile)
    all_results = []

    for q_info in queries:
        query = q_info["query"]
        print(f"[L1-ECOMMERCE] 搜索: {query}", file=sys.stderr)
        raw_results = search_bing(query, site=None, count=count, days=days)

        for r in raw_results:
            r["source_layer"] = q_info["source_layer"]
            r["search_type"] = q_info["search_type"]
            r["base_weight"] = 0.85  # 电商评论层基础权重
            r["platform"] = "ecommerce_indirect"
            r["platform_name"] = "E-commerce Reviews (indirect)"
            r["search_query"] = query
            r["search_time"] = datetime.now().isoformat()

            # 检查是否包含电商高价值指标
            text = f"{r.get('title', '')} {r.get('snippet', '')}"
            high_value_hits = sum(1 for ind in ECOMMERCE_HIGH_VALUE_INDICATORS if ind in text)
            low_value_hits = sum(1 for ind in ECOMMERCE_LOW_VALUE_INDICATORS if ind in text)
            r["ecommerce_quality"] = {
                "high_value_hits": high_value_hits,
                "low_value_hits": low_value_hits,
                "quality_signal": "high" if high_value_hits > 0 and low_value_hits == 0
                                 else "low" if low_value_hits > high_value_hits
                                 else "neutral",
            }

            # 如果包含高价值指标，额外加分
            if high_value_hits > 0:
                r["recency_bonus"] = 15  # 追评类内容额外加分

        all_results.extend(raw_results)
        time.sleep(1.0)

    # 去重
    seen_urls = set()
    unique = []
    for r in all_results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            unique.append(r)

    print(f"[L1-ECOMMERCE] {product} 电商评论搜索获取 {len(unique)} 条结果", file=sys.stderr)
    return unique


def search_comment_sections(product, count=10, days=730, category_profile=None):
    """
    【V5 新增】执行社交评论区间接搜索

    Args:
        product: 商品/品牌名
        count: 每个查询返回的结果数
        days: 搜索时间范围
        category_profile: 品类配置

    Returns:
        搜索结果列表，每条结果带有 source_layer 和 comment_section 相关标记
    """
    queries = generate_comment_section_queries(product, category_profile)
    all_results = []

    for q_info in queries:
        query = q_info["query"]
        print(f"[L2-COMMENT] 搜索: {query}", file=sys.stderr)
        raw_results = search_bing(query, site=None, count=count, days=days)

        for r in raw_results:
            r["source_layer"] = q_info["source_layer"]
            r["search_type"] = q_info["search_type"]
            r["base_weight"] = 0.75  # 评论区层基础权重
            r["platform"] = "comment_section_indirect"
            r["platform_name"] = "Comment Sections (indirect)"
            r["search_query"] = query
            r["search_time"] = datetime.now().isoformat()

            # 检查是否包含评论区高价值指标
            text = f"{r.get('title', '')} {r.get('snippet', '')}"
            high_value_hits = sum(1 for ind in COMMENT_HIGH_VALUE_INDICATORS if ind in text)
            low_value_hits = sum(1 for ind in COMMENT_LOW_VALUE_INDICATORS if ind in text)
            r["comment_quality"] = {
                "high_value_hits": high_value_hits,
                "low_value_hits": low_value_hits,
                "quality_signal": "high" if high_value_hits > 0 and low_value_hits == 0
                                 else "low" if low_value_hits > high_value_hits
                                 else "neutral",
            }

            if high_value_hits > 0:
                r["recency_bonus"] = 10

        all_results.extend(raw_results)
        time.sleep(1.0)

    # 去重
    seen_urls = set()
    unique = []
    for r in all_results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            unique.append(r)

    print(f"[L2-COMMENT] {product} 评论区搜索获取 {len(unique)} 条结果", file=sys.stderr)
    return unique


# ============================================================
# HTML 文本提取
# ============================================================

class HTMLTextExtractor(HTMLParser):
    """从 HTML 中提取纯文本"""

    def __init__(self):
        super().__init__()
        self._result = []
        self._skip = False
        self._skip_tags = {"script", "style", "noscript"}

    def handle_starttag(self, tag, attrs):
        if tag in self._skip_tags:
            self._skip = True

    def handle_endtag(self, tag):
        if tag in self._skip_tags:
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            text = data.strip()
            if text:
                self._result.append(text)

    def get_text(self):
        return " ".join(self._result)


def html_to_text(html_content):
    """将 HTML 转换为纯文本"""
    extractor = HTMLTextExtractor()
    try:
        extractor.feed(html_content)
        return extractor.get_text()
    except Exception:
        # 降级：用正则去标签
        text = re.sub(r"<[^>]+>", " ", html_content)
        text = re.sub(r"\s+", " ", text)
        return text.strip()


# ============================================================
# HTTP 请求
# ============================================================

_SSL_CTX = ssl.create_default_context()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Locale configuration (overridden by category_profile)
_LOCALE_CONFIG = {
    "accept_language": "en-US,en;q=0.9",
    "bing_setlang": "en",
    "bing_cc": "",
}


def configure_locale(category_profile):
    """Configure HTTP headers and search params based on detected locale."""
    global _LOCALE_CONFIG
    if not category_profile:
        return

    locale = category_profile.get("locale", "")
    language = category_profile.get("language", "")

    locale_map = {
        "zh-CN": {"accept_language": "zh-CN,zh;q=0.9,en;q=0.8", "bing_setlang": "zh-Hans", "bing_cc": "CN"},
        "zh-TW": {"accept_language": "zh-TW,zh;q=0.9,en;q=0.8", "bing_setlang": "zh-Hant", "bing_cc": "TW"},
        "en-US": {"accept_language": "en-US,en;q=0.9", "bing_setlang": "en", "bing_cc": "US"},
        "en-GB": {"accept_language": "en-GB,en;q=0.9", "bing_setlang": "en", "bing_cc": "GB"},
        "ja-JP": {"accept_language": "ja-JP,ja;q=0.9,en;q=0.8", "bing_setlang": "ja", "bing_cc": "JP"},
        "ko-KR": {"accept_language": "ko-KR,ko;q=0.9,en;q=0.8", "bing_setlang": "ko", "bing_cc": "KR"},
        "de-DE": {"accept_language": "de-DE,de;q=0.9,en;q=0.8", "bing_setlang": "de", "bing_cc": "DE"},
        "fr-FR": {"accept_language": "fr-FR,fr;q=0.9,en;q=0.8", "bing_setlang": "fr", "bing_cc": "FR"},
    }

    if locale in locale_map:
        _LOCALE_CONFIG = locale_map[locale]
    elif language:
        # Fallback: try language code alone
        for loc, cfg in locale_map.items():
            if loc.startswith(language):
                _LOCALE_CONFIG = cfg
                break

    HEADERS["Accept-Language"] = _LOCALE_CONFIG["accept_language"]
    print(f"[INFO] Locale configured: {locale or language} -> Accept-Language: {_LOCALE_CONFIG['accept_language']}", file=sys.stderr)


def fetch_url(url, timeout=15):
    """发送 HTTP GET 请求，返回响应文本"""
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset, errors="replace")
    except Exception as e:
        print(f"[WARN] 请求失败: {url} -> {e}", file=sys.stderr)
        return ""


# ============================================================
# 搜索引擎解析
# ============================================================

def parse_bing_results(html):
    """从 Bing 搜索结果 HTML 中提取条目"""
    results = []

    # 匹配 Bing 结果条目
    # <li class="b_algo"><h2><a href="URL">TITLE</a></h2><p>SNIPPET</p></li>
    pattern = re.compile(
        r'<li\s+class="b_algo"[^>]*>.*?'
        r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>'
        r'.*?<p[^>]*>(.*?)</p>',
        re.DOTALL,
    )

    for match in pattern.finditer(html):
        url = match.group(1)
        title = html_to_text(match.group(2))
        snippet = html_to_text(match.group(3))
        if url and title:
            results.append({
                "url": url,
                "title": title,
                "snippet": snippet,
            })

    # 备用解析：如果上面没抓到，用更宽松的模式
    if not results:
        url_pattern = re.compile(r'<a\s+href="(https?://[^"]+)"[^>]*>(.*?)</a>', re.DOTALL)
        for match in url_pattern.finditer(html):
            url = match.group(1)
            title = html_to_text(match.group(2))
            # 过滤掉 Bing 自身的链接
            if "bing.com" not in url and "microsoft.com" not in url and title:
                results.append({
                    "url": url,
                    "title": title,
                    "snippet": "",
                })

    return results


def search_bing(query, site=None, count=10, days=None):
    """
    通过搜索引擎搜索指定站点的内容

    Primary: Bing, Fallback: DuckDuckGo (when Bing returns captcha or 0 results).

    Args:
        query: 搜索关键词
        site: 限定搜索的站点域名（如 zhihu.com）
        count: 期望返回的结果数
        days: 搜索最近 N 天的内容（实际启用 Bing 时间过滤）
    """
    # 构造搜索查询
    search_query = query
    if site:
        search_query = f"site:{site} {query}"

    params = {
        "q": search_query,
        "count": min(count, 50),
        "setlang": _LOCALE_CONFIG.get("bing_setlang", "en"),
    }
    # Only add country code if configured
    if _LOCALE_CONFIG.get("bing_cc"):
        params["cc"] = _LOCALE_CONFIG["bing_cc"]

    # 【V2 修复】实际启用 Bing 时间过滤参数
    if days:
        if days <= 1:
            params["filters"] = 'ex1:"ez1"'       # 过去24小时
        elif days <= 7:
            params["filters"] = 'ex1:"ez2"'       # 过去一周
        elif days <= 30:
            params["filters"] = 'ex1:"ez3"'       # 过去一个月
        else:
            # 自定义时间范围
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            end_date = datetime.now().strftime("%Y-%m-%d")
            params["filters"] = f'ex1:"ez5_{start_date}_{end_date}"'

    results = []
    bing_blocked = False
    pages_to_fetch = max(1, (count + 9) // 10)  # 每页约 10 条

    for page in range(pages_to_fetch):
        params["first"] = page * 10 + 1
        url = f"https://www.bing.com/search?{urllib.parse.urlencode(params)}"

        html = fetch_url(url)
        if not html:
            continue

        # 【V6】检测 Bing captcha，自动降级到 DuckDuckGo
        if "captcha" in html.lower() or "are you a robot" in html.lower():
            print(f"[WARN] Bing captcha detected, falling back to DuckDuckGo", file=sys.stderr)
            bing_blocked = True
            break

        page_results = parse_bing_results(html)
        results.extend(page_results)

        if len(results) >= count:
            break

        # 礼貌间隔
        time.sleep(1.0)

    # 【V6】DuckDuckGo 降级：当 Bing 被 captcha 阻断或返回 0 结果时
    if (bing_blocked or not results) and not getattr(search_bing, '_ddg_disabled', False):
        ddg_results = _search_duckduckgo(search_query, count=count)
        if ddg_results:
            print(f"[INFO] DuckDuckGo returned {len(ddg_results)} results as fallback", file=sys.stderr)
            results = ddg_results

    return results[:count]


def _search_duckduckgo(query, count=10):
    """
    【V6】DuckDuckGo HTML 搜索（Bing 降级备选）

    使用 DuckDuckGo 的 HTML 版本搜索，不需要 API key，
    比 Bing 更不容易被 captcha 阻断。
    """
    params = {"q": query}
    url = f"https://html.duckduckgo.com/html/?{urllib.parse.urlencode(params)}"

    print(f"[DDG-FALLBACK] Searching: {url}", file=sys.stderr)
    html = fetch_url(url, timeout=20)
    if not html or len(html) < 500:
        return []

    results = []

    # DuckDuckGo HTML: <a class="result__a" href="URL">TITLE</a>
    # followed by <a class="result__snippet" href="...">SNIPPET</a>
    result_pattern = re.compile(
        r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>'
        r'.*?'
        r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
        re.DOTALL,
    )

    for match in result_pattern.finditer(html):
        raw_url = match.group(1)
        title = html_to_text(match.group(2))
        snippet = html_to_text(match.group(3))
        real_url = _extract_ddg_real_url(raw_url)
        if real_url and title and "duckduckgo.com" not in real_url:
            results.append({
                "url": real_url,
                "title": title,
                "snippet": snippet,
            })

    # Simpler fallback pattern
    if not results:
        simple_pattern = re.compile(
            r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
            re.DOTALL,
        )
        for match in simple_pattern.finditer(html):
            raw_url = match.group(1)
            title = html_to_text(match.group(2))
            real_url = _extract_ddg_real_url(raw_url)
            if real_url and title and "duckduckgo.com" not in real_url:
                results.append({
                    "url": real_url,
                    "title": title,
                    "snippet": "",
                })

    return results[:count]


def _extract_ddg_real_url(raw_url):
    """Extract real URL from DuckDuckGo's redirect wrapper."""
    if not raw_url:
        return ""
    if "uddg=" in raw_url:
        parsed = urllib.parse.urlparse(raw_url)
        qs = urllib.parse.parse_qs(parsed.query)
        if "uddg" in qs:
            return urllib.parse.unquote(qs["uddg"][0])
    if raw_url.startswith("http"):
        return raw_url
    if raw_url.startswith("//"):
        return "https:" + raw_url
    return raw_url


def search_bing_dual_window(query, site=None, count=10):
    """
    【V2 新增】双时间窗搜索策略

    窗口1（即时窗口）：最近 90 天 —— 确保不漏近期事件
    窗口2（历史窗口）：最近 2 年 —— 获取长期使用反馈

    即时窗口的结果会获得额外时效性加分标记。

    Args:
        query: 搜索关键词
        site: 限定站点
        count: 每个窗口返回的结果数

    Returns:
        合并去重后的结果列表，即时窗口结果带有 is_recent=True 标记
    """
    # 窗口1：最近 90 天（即时窗口）
    recent_results = search_bing(query, site=site, count=count, days=90)
    for r in recent_results:
        r["is_recent"] = True
        r["time_window"] = "recent_90d"

    # 窗口2：最近 2 年（历史窗口）
    historical_results = search_bing(query, site=site, count=count, days=730)
    for r in historical_results:
        r["is_recent"] = False
        r["time_window"] = "historical_730d"

    # 合并去重（即时窗口优先）
    seen_urls = set()
    merged = []
    for r in recent_results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            merged.append(r)
    for r in historical_results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            merged.append(r)

    return merged


def append_year_to_query(query_base):
    """
    【V2 新增】在搜索关键词中拼接当前年份和上一年份，提升新内容命中率

    Args:
        query_base: 基础搜索关键词

    Returns:
        包含年份变体的查询列表
    """
    current_year = datetime.now().year
    prev_year = current_year - 1
    return [
        f"{query_base} {current_year}",
        f"{query_base} {prev_year}",
    ]


# ============================================================
# 内容抓取
# ============================================================

def fetch_page_content(url, max_length=5000):
    """
    抓取页面正文内容

    Args:
        url: 页面 URL
        max_length: 最大返回文本长度
    """
    html = fetch_url(url, timeout=20)
    if not html:
        return ""

    # 尝试提取正文区域
    # 知乎回答
    zhihu_match = re.search(
        r'class="RichContent-inner"[^>]*>(.*?)</div>',
        html, re.DOTALL
    )
    if zhihu_match:
        return html_to_text(zhihu_match.group(1))[:max_length]

    # V2EX 帖子
    v2ex_match = re.search(
        r'class="topic_content"[^>]*>(.*?)</div>',
        html, re.DOTALL
    )
    if v2ex_match:
        return html_to_text(v2ex_match.group(1))[:max_length]

    # 什么值得买文章
    smzdm_match = re.search(
        r'class="p-con"[^>]*>(.*?)</div>',
        html, re.DOTALL
    )
    if smzdm_match:
        return html_to_text(smzdm_match.group(1))[:max_length]

    # 通用提取：找最大的文本块
    # 去掉 header/footer/nav/aside
    body = re.sub(r"<(header|footer|nav|aside)[^>]*>.*?</\1>", "", html, flags=re.DOTALL)
    # 提取 <p> 标签内容
    paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", body, re.DOTALL)
    if paragraphs:
        text = " ".join(html_to_text(p) for p in paragraphs)
        return text[:max_length]

    # 最终降级
    return html_to_text(body)[:max_length]


# ============================================================
# 核心搜索逻辑
# ============================================================

def search_platform(query, platform_key, count=10, days=None, use_dual_window=False, category_profile=None):
    """
    搜索指定平台的内容

    Args:
        query: 搜索关键词
        platform_key: 平台标识（如 zhihu, v2ex）
        count: 返回结果数
        days: 搜索最近 N 天
        use_dual_window: 是否使用双时间窗搜索策略
        category_profile: 【V3】AI 生成的品类配置（用于动态平台权重）
    """
    if platform_key not in PLATFORMS:
        print(f"[WARN] 未知平台: {platform_key}", file=sys.stderr)
        return []

    platform = PLATFORMS[platform_key]
    site = platform["site"]
    suffix = platform.get("search_suffix", "")
    full_query = f"{query} {suffix}".strip()

    print(f"[INFO] 搜索 {platform['name']}({site}): {full_query}", file=sys.stderr)

    if use_dual_window:
        # 双时间窗搜索
        print(f"[INFO] 使用双时间窗策略 (90天即时 + 730天历史)", file=sys.stderr)
        raw_results = search_bing_dual_window(full_query, site=site, count=count)
    else:
        raw_results = search_bing(full_query, site=site, count=count, days=days)

    # 【V3】使用动态平台权重
    dynamic_weight = get_platform_weight(platform_key, category_profile)

    # 为每条结果附加平台元数据
    results = []
    for r in raw_results:
        r["platform"] = platform_key
        r["platform_name"] = platform["name"]
        r["base_weight"] = dynamic_weight  # 【V3】使用动态权重
        r["search_query"] = full_query
        r["search_time"] = datetime.now().isoformat()

        # 即时窗口的结果获得时效性加分
        if r.get("is_recent"):
            r["recency_bonus"] = 10
        else:
            r["recency_bonus"] = 0

        results.append(r)

    print(f"[INFO] {platform['name']} 返回 {len(results)} 条结果 (权重={dynamic_weight})", file=sys.stderr)
    return results


def search_all_platforms(query, platforms=None, count=10, days=None,
                        use_dual_window=False, append_year=False, category_profile=None):
    """
    在多个平台同时搜索

    Args:
        query: 搜索关键词
        platforms: 平台列表，None 则使用默认平台
        count: 每个平台返回的结果数
        days: 搜索最近 N 天
        use_dual_window: 是否使用双时间窗搜索
        append_year: 是否自动拼接年份变体查询
        category_profile: 【V3】AI 生成的品类配置
    """
    if platforms is None:
        platforms = DEFAULT_PLATFORMS

    # 【V3】根据品类权重对平台排序和过滤
    platforms = get_prioritized_platforms(platforms, category_profile)

    all_results = []

    # 如果启用年份拼接，生成额外的年份查询
    queries_to_search = [query]
    if append_year:
        year_queries = append_year_to_query(query)
        queries_to_search.extend(year_queries)
        print(f"[INFO] 年份拼接已启用，将搜索: {queries_to_search}", file=sys.stderr)

    for q in queries_to_search:
        for p in platforms:
            results = search_platform(
                q, p, count=count, days=days,
                use_dual_window=use_dual_window,
                category_profile=category_profile,
            )
            all_results.extend(results)
            # 平台间间隔，避免被搜索引擎限流
            time.sleep(1.5)

    # 去重（按 URL）
    seen_urls = set()
    unique_results = []
    for r in all_results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            unique_results.append(r)

    return unique_results


# ============================================================
# 【V4 新增】搜索结果数量自适应
# ============================================================

# 自适应阈值配置
ADAPTIVE_THRESHOLDS = {
    "min_results_per_product": 5,    # 每个候选商品最少需要的有效反馈数
    "min_total_results": 15,         # 最低总结果数
    "max_total_results": 200,        # 最高总结果数（防止热门品类过载）
    "max_results_per_product": 40,   # 每个商品最多保留的结果数
}


def assess_result_sufficiency(results, candidate_products=None, category_profile=None):
    """
    【V4 新增】评估搜索结果是否充分

    检查搜索结果是否满足最低数量要求。如果不满足，返回自适应建议。

    Args:
        results: 当前搜索结果列表
        candidate_products: 候选商品列表（可选）
        category_profile: 品类配置（可选）

    Returns:
        dict: {
            "is_sufficient": bool,
            "total_results": int,
            "product_coverage": {商品名: 结果数},
            "underserved_products": [结果不足的商品列表],
            "recommendations": [自适应建议列表],
            "data_sufficiency_level": "充分|基本充分|不足|严重不足"
        }
    """
    total = len(results)
    min_total = ADAPTIVE_THRESHOLDS["min_total_results"]
    min_per_product = ADAPTIVE_THRESHOLDS["min_results_per_product"]

    # 统计每个商品的结果数
    product_coverage = defaultdict(int)
    for r in results:
        # 从 dive_model 或文本中识别商品
        product = r.get("dive_model", "")
        if product:
            product_coverage[product] += 1

    # 如果提供了候选商品列表，检查覆盖情况
    underserved = []
    if candidate_products:
        for product in candidate_products:
            count = product_coverage.get(product, 0)
            if count < min_per_product:
                underserved.append({
                    "product": product,
                    "current_count": count,
                    "needed": min_per_product - count,
                })

    # 生成建议
    recommendations = []

    if total < min_total:
        recommendations.append({
            "type": "expand_search",
            "reason": f"总结果数({total})低于最低要求({min_total})",
            "actions": [
                "移除 site: 限制，扩大到全网搜索",
                "降低时间窗口要求（从90天扩展到180天或365天）",
                "减少搜索关键词的组合复杂度",
                "增加搜索平台数量",
            ],
        })

    if underserved:
        for item in underserved:
            recommendations.append({
                "type": "targeted_search",
                "reason": f"{item['product']} 仅有 {item['current_count']} 条结果，"
                          f"需要再搜索至少 {item['needed']} 条",
                "actions": [
                    f"针对 {item['product']} 执行额外的全网搜索（不加 site: 限制）",
                    f"搜索 {item['product']} 的型号变体或别名",
                    f"在更多平台搜索 {item['product']}",
                ],
            })

    if total > ADAPTIVE_THRESHOLDS["max_total_results"]:
        recommendations.append({
            "type": "trim_results",
            "reason": f"总结果数({total})超过最大处理限制({ADAPTIVE_THRESHOLDS['max_total_results']})",
            "actions": [
                "按可信度排序，只保留 Top N 条",
                "对每个商品只保留可信度最高的若干条",
                "移除无商品关联的结果",
            ],
        })

    # Data sufficiency level (read labels from profile or use English defaults)
    labels = {}
    if category_profile and "report_labels" in category_profile:
        labels = category_profile["report_labels"]

    if total >= min_total * 2 and not underserved:
        sufficiency_level = labels.get("sufficient", "sufficient")
    elif total >= min_total and len(underserved) <= 1:
        sufficiency_level = labels.get("mostly_sufficient", "mostly sufficient")
    elif total >= min_total // 2:
        sufficiency_level = labels.get("insufficient", "insufficient")
    else:
        sufficiency_level = labels.get("severely_insufficient", "severely insufficient")

    return {
        "is_sufficient": len(recommendations) == 0,
        "total_results": total,
        "product_coverage": dict(product_coverage),
        "underserved_products": underserved,
        "recommendations": recommendations,
        "data_sufficiency_level": sufficiency_level,
    }


def trim_excess_results(results, max_per_product=None):
    """
    【V4 新增】当结果过多时，按可信度裁剪

    对每个商品只保留可信度最高的 max_per_product 条结果。

    Args:
        results: 搜索结果列表
        max_per_product: 每个商品最多保留的条数（默认从阈值配置读取）

    Returns:
        裁剪后的结果列表
    """
    if max_per_product is None:
        max_per_product = ADAPTIVE_THRESHOLDS["max_results_per_product"]

    max_total = ADAPTIVE_THRESHOLDS["max_total_results"]

    if len(results) <= max_total:
        return results

    # 按商品分组
    product_groups = defaultdict(list)
    no_product = []
    for r in results:
        product = r.get("dive_model", "")
        if product:
            product_groups[product].append(r)
        else:
            no_product.append(r)

    # 对每个商品按可信度排序并裁剪
    trimmed = []
    for product, group in product_groups.items():
        group.sort(key=lambda x: x.get("credibility_score", 50), reverse=True)
        trimmed.extend(group[:max_per_product])

    # 加回无商品关联的结果（数量较少时）
    remaining_quota = max_total - len(trimmed)
    if remaining_quota > 0:
        no_product.sort(key=lambda x: x.get("credibility_score", 50), reverse=True)
        trimmed.extend(no_product[:remaining_quota])

    print(
        f"[ADAPTIVE] 裁剪结果: {len(results)} -> {len(trimmed)} 条 "
        f"(max_per_product={max_per_product}, max_total={max_total})",
        file=sys.stderr,
    )

    return trimmed


# ============================================================
# 主程序
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="多平台真实用户反馈搜索工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python platform_search.py "人体工学椅 腰肌劳损"
  python platform_search.py "4K显示器 设计" --platforms zhihu,v2ex,chiphell --count 20
  python platform_search.py "机械键盘 办公" --platforms all --days 180 --fetch-content --limit 5
        """,
    )

    parser.add_argument("query", help="搜索关键词")
    parser.add_argument(
        "--platforms", "-p",
        default=",".join(DEFAULT_PLATFORMS),
        help=f"搜索平台（逗号分隔）。可选: {', '.join(ALL_PLATFORMS)}。'all' 表示所有平台。默认: {','.join(DEFAULT_PLATFORMS)}",
    )
    parser.add_argument(
        "--count", "-c",
        type=int, default=10,
        help="每个平台返回的结果数（默认 10）",
    )
    parser.add_argument(
        "--days", "-d",
        type=int, default=None,
        help="搜索最近 N 天的内容",
    )
    parser.add_argument(
        "--fetch-content", "-f",
        action="store_true",
        help="抓取每条结果的页面正文内容",
    )
    parser.add_argument(
        "--limit", "-l",
        type=int, default=None,
        help="抓取正文的数量限制（配合 --fetch-content 使用）",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="输出文件路径（JSON 格式）。不指定则输出到 stdout",
    )
    parser.add_argument(
        "--no-limit",
        action="store_true",
        help="禁用请求间的限频等待",
    )
    parser.add_argument(
        "--dual-window",
        action="store_true",
        help="【V2】启用双时间窗搜索策略（90天即时 + 730天历史）",
    )
    parser.add_argument(
        "--append-year",
        action="store_true",
        help="【V2】自动在搜索关键词中拼接当前年份和上一年份",
    )
    parser.add_argument(
        "--adaptive",
        action="store_true",
        help="【V4】启用搜索结果数量自适应评估",
    )
    parser.add_argument(
        "--candidate-products",
        default=None,
        help="【V4】候选商品列表（逗号分隔），用于自适应评估每个商品的结果覆盖度",
    )
    parser.add_argument(
        "--category-profile",
        default=None,
        help="【V3】品类配置文件路径（JSON 格式）",
    )
    parser.add_argument(
        "--ecommerce",
        action="store_true",
        help="Enable e-commerce review indirect search (L1 tier)",
    )
    parser.add_argument(
        "--comment-section",
        action="store_true",
        help="Enable social comment section indirect search (L2 tier)",
    )
    parser.add_argument(
        "--ecommerce-products",
        default=None,
        help="【V5】需要搜索电商评论的商品列表（逗号分隔）",
    )

    args = parser.parse_args()

    # Load category profile early for locale/platform configuration
    category_profile_data = None
    if args.category_profile:
        with open(args.category_profile, "r", encoding="utf-8") as f:
            category_profile_data = json.load(f)
        # Configure locale and platforms from profile
        configure_locale(category_profile_data)
        load_platforms_from_profile(category_profile_data)
        load_search_config_from_profile(category_profile_data)
        print(f"[INFO] Loaded category profile: {category_profile_data.get('category', 'unknown')} "
              f"(locale: {category_profile_data.get('locale', 'default')})", file=sys.stderr)

    # Parse platform list (after profile loading, since platforms may be overridden)
    if args.platforms.lower() == "all":
        platforms = ALL_PLATFORMS
    else:
        platforms = [p.strip() for p in args.platforms.split(",")]
        # 验证平台名
        for p in platforms:
            if p not in PLATFORMS:
                print(f"[ERROR] 未知平台: {p}。可选: {', '.join(ALL_PLATFORMS)}", file=sys.stderr)
                sys.exit(1)

    # 执行搜索
    print(f"[INFO] 开始搜索: '{args.query}'", file=sys.stderr)
    print(f"[INFO] 目标平台: {', '.join(platforms)}", file=sys.stderr)
    if args.days:
        print(f"[INFO] 时间范围: 最近 {args.days} 天", file=sys.stderr)
    if args.dual_window:
        print(f"[INFO] 双时间窗策略已启用", file=sys.stderr)
    if args.append_year:
        print(f"[INFO] 年份拼接已启用", file=sys.stderr)

    results = search_all_platforms(
        query=args.query,
        platforms=platforms,
        count=args.count,
        days=args.days,
        use_dual_window=args.dual_window,
        append_year=args.append_year,
    )

    # Category profile already loaded above

    # 【V5】电商评论间接搜索（L1 层）
    ecommerce_results = []
    if args.ecommerce:
        ecom_products = []
        if args.ecommerce_products:
            ecom_products = [p.strip() for p in args.ecommerce_products.split(",")]
        elif args.candidate_products:
            ecom_products = [p.strip() for p in args.candidate_products.split(",")]

        if ecom_products:
            print(f"\n[L1-ECOMMERCE] 开始电商评论间接搜索，目标商品: {ecom_products}", file=sys.stderr)
            for product in ecom_products:
                ecom_res = search_ecommerce_reviews(
                    product, count=args.count, days=args.days or 730,
                    category_profile=category_profile_data,
                )
                ecommerce_results.extend(ecom_res)
            print(f"[L1-ECOMMERCE] 电商评论搜索共获取 {len(ecommerce_results)} 条结果", file=sys.stderr)
        else:
            print(f"[WARN] 启用了电商搜索但未指定商品列表，跳过", file=sys.stderr)

    # 【V5】评论区间接搜索（L2 层）
    comment_results = []
    if args.comment_section:
        comment_products = []
        if args.ecommerce_products:
            comment_products = [p.strip() for p in args.ecommerce_products.split(",")]
        elif args.candidate_products:
            comment_products = [p.strip() for p in args.candidate_products.split(",")]

        if comment_products:
            print(f"\n[L2-COMMENT] 开始评论区间接搜索，目标商品: {comment_products}", file=sys.stderr)
            for product in comment_products:
                comment_res = search_comment_sections(
                    product, count=args.count, days=args.days or 730,
                    category_profile=category_profile_data,
                )
                comment_results.extend(comment_res)
            print(f"[L2-COMMENT] 评论区搜索共获取 {len(comment_results)} 条结果", file=sys.stderr)
        else:
            print(f"[WARN] 启用了评论区搜索但未指定商品列表，跳过", file=sys.stderr)

    # 【V5】合并所有层级的结果
    if ecommerce_results or comment_results:
        # 标注传统搜索结果的层级
        for r in results:
            if "source_layer" not in r:
                r["source_layer"] = "L3_forum_post"

        # 合并去重
        all_results = results + ecommerce_results + comment_results
        seen_urls = set()
        unique_all = []
        for r in all_results:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                unique_all.append(r)
        results = unique_all

        # 统计各层级数据量
        layer_counts = defaultdict(int)
        for r in results:
            layer_counts[r.get("source_layer", "L3_forum_post")] += 1
        print(f"\n[V5] 数据源分层统计:", file=sys.stderr)
        for layer, count in sorted(layer_counts.items()):
            print(f"  - {layer}: {count} 条", file=sys.stderr)

    # 可选：抓取正文内容
    if args.fetch_content:
        fetch_limit = args.limit or len(results)
        print(f"[INFO] 开始抓取前 {fetch_limit} 条结果的正文内容", file=sys.stderr)
        for i, r in enumerate(results[:fetch_limit]):
            print(f"[INFO] 抓取 ({i+1}/{fetch_limit}): {r['url']}", file=sys.stderr)
            r["content"] = fetch_page_content(r["url"])
            if not args.no_limit:
                time.sleep(1.0)

    # 【V4】搜索结果数量自适应评估
    adaptive_assessment = None
    if args.adaptive:
        candidate_products = None
        if args.candidate_products:
            candidate_products = [p.strip() for p in args.candidate_products.split(",")]

        category_profile = None
        if args.category_profile:
            with open(args.category_profile, "r", encoding="utf-8") as f:
                category_profile = json.load(f)

        adaptive_assessment = assess_result_sufficiency(
            results,
            candidate_products=candidate_products,
            category_profile=category_profile,
        )

        print(f"\n[ADAPTIVE] 数据充分度: {adaptive_assessment['data_sufficiency_level']}", file=sys.stderr)
        if not adaptive_assessment["is_sufficient"]:
            print(f"[ADAPTIVE] 搜索结果不足，建议:", file=sys.stderr)
            for rec in adaptive_assessment["recommendations"]:
                print(f"  [{rec['type']}] {rec['reason']}", file=sys.stderr)
                for action in rec["actions"][:2]:
                    print(f"    - {action}", file=sys.stderr)

        if adaptive_assessment.get("underserved_products"):
            print(f"[ADAPTIVE] 结果不足的商品:", file=sys.stderr)
            for item in adaptive_assessment["underserved_products"]:
                print(f"  - {item['product']}: {item['current_count']}条 (还需{item['needed']}条)", file=sys.stderr)

        # 如果结果过多，自动裁剪
        if len(results) > ADAPTIVE_THRESHOLDS["max_total_results"]:
            results = trim_excess_results(results)

    # 输出结果摘要
    print(f"\n[DONE] 共获取 {len(results)} 条去重结果", file=sys.stderr)
    platform_counts = {}
    for r in results:
        pn = r["platform_name"]
        platform_counts[pn] = platform_counts.get(pn, 0) + 1
    for pn, cnt in platform_counts.items():
        print(f"  - {pn}: {cnt} 条", file=sys.stderr)

    # 输出 JSON
    output_data = {
        "query": args.query,
        "platforms": platforms,
        "search_time": datetime.now().isoformat(),
        "days": args.days,
        "total_results": len(results),
        "results": results,
    }

    # 【V5】附加数据源分层统计
    source_layer_stats = defaultdict(int)
    for r in results:
        source_layer_stats[r.get("source_layer", "L3_forum_post")] += 1
    if any(layer != "L3_forum_post" for layer in source_layer_stats):
        output_data["source_layer_stats"] = dict(source_layer_stats)

    # 【V4】附加自适应评估结果
    if adaptive_assessment:
        output_data["adaptive_assessment"] = adaptive_assessment

    json_str = json.dumps(output_data, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_str)
        print(f"[INFO] 结果已保存到: {args.output}", file=sys.stderr)
    else:
        print(json_str)


if __name__ == "__main__":
    main()
