#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可信度评分引擎

对搜索结果进行软文/水军/真实反馈的可信度评分。
基于文本特征、平台权重和行为信号进行综合评判。

用法:
    python credibility_scorer.py results.json --output scored_results.json
    python credibility_scorer.py results.json --threshold 60
    cat results.json | python credibility_scorer.py - --output scored.json
"""

import argparse
import json
import re
import sys
from datetime import datetime


# ============================================================
# 软文/水军负面特征规则
# ============================================================

# 高权重负面信号 (每命中 -25 分)
HIGH_NEG_PATTERNS = {
    "purchase_links": {
        "patterns": [
            r"https?://[^\s]*(?:item|product|detail|buy|shop|s\.click|union|goto)\.[^\s]*",
            r"(?:优惠券|优惠码|折扣码|返利|领券|下单|购买链接)",
            r"(?:复制|打开|淘宝|京东|拼多多).*?(?:搜索|领取|下单)",
            r"(?:\$|¥)\s*\d+.*?(?:券|优惠|立减)",
        ],
        "score": -25,
        "label": "包含购买链接或优惠码",
    },
    "brand_first_line": {
        "patterns": [
            r"^.{0,20}(?:品牌|型号).{0,5}[A-Za-z\u4e00-\u9fa5]+\s*[A-Za-z0-9\-]+\s*[A-Za-z0-9\-]*",
        ],
        "score": -20,
        "label": "首段即精确品牌型号",
    },
    "zero_drawbacks": {
        "patterns": [],  # 需要语义分析，通过专用函数处理
        "score": -25,
        "label": "全文零缺点",
    },
    "marketing_buzzwords": {
        "patterns": [
            r"(?:颠覆性|黑科技|业界天花板|强烈推荐|必入|爆款|断货王|良心推荐|闭眼入)",
            r"(?:吊打|秒杀|碾压|完胜|无敌|逆天|封神|天花板级)",
            r"(?:不买后悔|后悔没早买|相见恨晚|yyds|绝绝子|太香了)",
            r"(?:真的绝了|好用到哭|回购无数次|一生推|安利给所有人)",
        ],
        "score": -20,
        "label": "大量营销话术",
    },
    # 【V2 新增】新兴营销话术变种
    "marketing_buzzwords_v2": {
        "patterns": [
            r"(?:遥遥领先|泰裤辣|拿捏了|绝了家人们|姐妹们冲|蹲一个)",
            r"(?:看过来|不允许你不知道|码住|先马后看|速看)",
            r"(?:全网最低|独家优惠|粉丝专属|限时特价|今日特惠)",
            r"(?:赶紧冲|手慢无|库存紧张|即将售罄|限量发售)",
        ],
        "score": -20,
        "label": "新兴营销话术",
    },
}

# 中权重负面信号 (每命中 -12 分)
MID_NEG_PATTERNS = {
    "structured_writing": {
        "patterns": [
            r"(?:一、|二、|三、|四、|五、).*\n",
            r"(?:优点[:：]|缺点[:：]|总结[:：]|推荐理由[:：])",
        ],
        "score": -12,
        "label": "行文过于规整（公关稿特征）",
    },
    "brand_echo": {
        "patterns": [
            r"(?:官方介绍|据官方|品牌方表示|官网显示)",
            r"(?:荣获|获得.*?奖|入选.*?榜单|获得.*?认证)",
        ],
        "score": -10,
        "label": "与品牌官方话术高度重合",
    },
    "astrotuf_comments": {
        "patterns": [
            r"(?:已入手|已下单|种草了|求链接|链接在哪|哪里买)",
        ],
        "score": -10,
        "label": "评论区雷同回复特征",
    },
}

# 低权重负面信号 (每命中 -5 分)
LOW_NEG_PATTERNS = {
    "clickbait_title": {
        "patterns": [
            r"(?:测评|推荐|必买|不踩雷|避坑指南|购买攻略|选购指南|好物分享)",
        ],
        "score": -5,
        "label": "标题含引流词",
    },
    "follow_bait": {
        "patterns": [
            r"(?:关注我|点赞收藏|喜欢就关注|更多好物|持续更新|下期预告)",
        ],
        "score": -5,
        "label": "文末引流话术",
    },
}


# ============================================================
# 真实用户正面特征规则
# ============================================================

# 高权重正面信号 (每命中 +25 分)
HIGH_POS_PATTERNS = {
    "usage_duration": {
        "patterns": [
            r"(?:用了|使用了|买了|入手)\s*(?:\d+\s*(?:年|个月|月|天|周))",
            r"(?:半年|一年|两年|三年|几个月)(?:后|了|以来)",
            r"(?:长期使用|持续使用|日常使用)\s*(?:\d+)?",
        ],
        "score": 25,
        "label": "明确使用时长",
    },
    "specific_defects": {
        "patterns": [
            r"(?:缺点是|不足是|问题是|毛病是|槽点是)",
            r"(?:但是|不过|唯一的问题|美中不足)",
            r"(?:异响|松动|脱皮|掉漆|生锈|塌陷|开裂|磨损|漏气|断裂)",
            r"(?:坏了|修了|换了|退了|投诉|售后|维修|返厂)",
        ],
        "score": 25,
        "label": "具体缺点描述",
    },
    "comparison_experience": {
        "patterns": [
            r"(?:之前用的|以前用|换了.*?之后|从.*?换到|对比.*?来说)",
            r"(?:第一把|第二把|换过.*?把|试过.*?款)",
        ],
        "score": 20,
        "label": "使用前后对比",
    },
    "after_sales_experience": {
        "patterns": [
            r"(?:客服|售后|退换货|保修|质保|维修|返厂|退款)",
            r"(?:打电话|联系.*?客服|协商|投诉|12315)",
        ],
        "score": 20,
        "label": "售后经历描述",
    },
}

# 中权重正面信号 (每命中 +12 分)
MID_POS_PATTERNS = {
    "colloquial_language": {
        "patterns": [
            r"(?:哈哈|emmm|额|嗯|吧|啊|呢|哦|嘿|唉|草)",
            r"(?:说实话|讲真|不吹不黑|客观来说|个人感受)",
            r"(?:。。。|！！|？？|……|~~)",
        ],
        "score": 12,
        "label": "语言口语化自然",
    },
    "purchase_details": {
        "patterns": [
            r"(?:买的时候|入手价|到手价|活动价|打折|促销|双十一|618|黑五)",
            r"(?:花了|¥|元|块钱)\s*\d+",
            r"(?:京东|淘宝|拼多多|线下|实体店).*?(?:买的|入的|下的单)",
        ],
        "score": 12,
        "label": "具体购买信息",
    },
    "reply_to_questions": {
        "patterns": [
            r"(?:回复|回答|补充一下|更新一下|追加评价)",
            r"(?:有人问|有朋友问|评论区|私信问)",
        ],
        "score": 10,
        "label": "回复追问",
    },
}

# 低权重正面信号 (每命中 +5 分)
LOW_POS_PATTERNS = {
    "small_account": {
        "patterns": [],  # 需要外部数据，暂留接口
        "score": 5,
        "label": "普通小号用户",
    },
    "niche_forum": {
        "patterns": [],  # 通过平台权重处理
        "score": 5,
        "label": "在小众论坛发布",
    },
}


# ============================================================
# 【V5 新增】电商评论层可信度信号
# ============================================================

# 电商追评高价值正面信号（每命中 +20 分）
ECOMMERCE_POS_PATTERNS = {
    "follow_up_review": {
        "patterns": [
            r"(?:追评|追加评价|补充评价|再来更新|后续反馈)",
            r"(?:用了\d+个月|买了半年|使用一年|入手\d+天)(?:后|了)",
            r"(?:第二次追评|再次追评|三个月后来追评)",
        ],
        "score": 20,
        "label": "电商追评（高价值长期反馈）",
    },
    "verified_purchase": {
        "patterns": [
            r"(?:已购买|已入手|实际到手|收到货后|开箱后发现)",
            r"(?:京东买的|淘宝入的|天猫旗舰店|拼多多下单)",
            r"(?:到手价|实付|活动价买的|双十一入的|618买的)",
        ],
        "score": 15,
        "label": "确认购买行为",
    },
    "product_aging": {
        "patterns": [
            r"(?:用了几个月后|半年后|一年后).*?(?:开始|出现|发现)",
            r"(?:新买的时候很好|刚开始还行).*?(?:后来|现在|但是)",
            r"(?:老化|磨损|松动|褪色|起皮|塌陷|异响).*?(?:了|开始)",
        ],
        "score": 20,
        "label": "产品老化时间线描述",
    },
}

# 电商评论低价值负面信号（每命中 -15 分）
ECOMMERCE_NEG_PATTERNS = {
    "fake_review_signals": {
        "patterns": [
            r"(?:好评返现|返\d+元|好评截图|晒图返|评价有礼)",
            r"(?:默认好评|系统默认|未填写评价)",
            r"(?:此用户没有填写|自动评价)",
        ],
        "score": -15,
        "label": "电商刷单/返现好评特征",
    },
    "template_review": {
        "patterns": [
            r"(?:物流很快|包装完好|卖家态度好|五星好评|好评！)",
            r"(?:还没用|还没打开|先给好评|后续追评)",
            r"(?:不错不错|很好很好|满意满意|推荐推荐)",
        ],
        "score": -10,
        "label": "模板化好评",
    },
}

# 评论区层可信度信号
COMMENT_SECTION_POS_PATTERNS = {
    "debunk_signal": {
        "patterns": [
            r"(?:我也买了|同款翻车|我买的也是|买过的来说)",
            r"(?:评论区才是真相|别看正文|帖子是广告|正文别信)",
            r"(?:不请自来|实际用过|亲测|真实体验)",
        ],
        "score": 18,
        "label": "评论区拔草/实测反馈",
    },
    "counter_opinion": {
        "patterns": [
            r"(?:和博主说的不一样|实际没那么好|别被种草|踩坑了)",
            r"(?:反驳一下|来说说真实的|我的体验相反|不同意楼主)",
        ],
        "score": 15,
        "label": "评论区反驳/不同意见",
    },
}

COMMENT_SECTION_NEG_PATTERNS = {
    "engagement_bait": {
        "patterns": [
            r"(?:求链接|哪里买|什么价|多少钱入的|求推荐)",
            r"(?:已种草|好想买|马上下单|冲冲冲|已加购物车)",
        ],
        "score": -8,
        "label": "评论区引流/求购特征",
    },
}

# 【V2】品类特定正面信号（V3 中降级为 fallback，优先使用 category_profile）
CATEGORY_POS_PATTERNS_FALLBACK = {
    # 母婴/食品品类的真实喂养体验信号（仅在 category_profile 未提供时生效）
    "feeding_experience": {
        "patterns": [
            r"(?:吃了|喝了|转奶|混合喂养|母乳转|亲喂|瓶喂)",
            r"(?:宝宝|孩子|娃|闺女|儿子|老二|二胎)",
            r"(?:月龄|个月大|几个月|断奶|加辅食)",
            r"(?:便便|大便|排便|拉肚子|绿便|奶瓣)",
        ],
        "score": 20,
        "label": "真实喂养经历描述",
    },
    # 长期使用变化描述（通用，保留）
    "long_term_change": {
        "patterns": [
            r"(?:一开始|刚开始|最初).*?(?:后来|现在|之后|最后)",
            r"(?:第一周|第一个月|前几天).*?(?:现在|目前|到现在)",
            r"(?:逐渐|慢慢|渐渐).*?(?:习惯|适应|好转|恶化)",
        ],
        "score": 15,
        "label": "长期使用变化描述",
    },
}

# 向后兼容：保留旧名称
CATEGORY_POS_PATTERNS = CATEGORY_POS_PATTERNS_FALLBACK


# ============================================================
# 【V3 新增】品类信号动态加载
# ============================================================

def load_category_signals(category_profile):
    """
    【V3 新增】从 AI 品类配置中加载品类专属的可信度正面信号

    替代硬编码的 CATEGORY_POS_PATTERNS。
    category_profile 中的 category_positive_signals 格式:
    [
        {
            "pattern_description": "提到具体的身高体重和坐感匹配",
            "regex_hint": "(?:身高|体重|\\d+cm|\\d+kg).*?(?:坐感|合适|偏大|偏小)",
            "score": 15,
            "label": "身体参数匹配描述"
        }
    ]
    """
    signals = category_profile.get("category_positive_signals", [])
    patterns = {}

    for i, signal in enumerate(signals):
        regex_hint = signal.get("regex_hint", "")
        # 验证正则表达式是否合法
        valid_patterns = []
        if regex_hint:
            try:
                re.compile(regex_hint)
                valid_patterns.append(regex_hint)
            except re.error:
                print(f"[WARN] category_positive_signals[{i}] 的 regex_hint 不合法，跳过: {regex_hint}",
                      file=sys.stderr)

        patterns[f"category_signal_{i}"] = {
            "patterns": valid_patterns,
            "score": signal.get("score", 15),
            "label": signal.get("label", f"品类相关信号{i+1}"),
        }

    return patterns


# ============================================================
# 评分引擎
# ============================================================

def count_pattern_matches(text, patterns):
    """统计文本中匹配指定正则模式的次数"""
    total = 0
    for p in patterns:
        matches = re.findall(p, text, re.IGNORECASE | re.MULTILINE)
        total += len(matches)
    return total


def check_zero_drawbacks(text):
    """
    检查文本是否全文零缺点。
    如果文本超过 200 字但没有任何负面/中性表述，判定为可疑。
    """
    if len(text) < 200:
        return False

    negative_indicators = [
        r"(?:缺点|不足|问题|毛病|槽点|遗憾|可惜|不好|不行|差|烂)",
        r"(?:但是|不过|然而|可是|就是|唯一)",
        r"(?:希望改进|有待提升|需要改善|建议|期待)",
    ]

    for pattern in negative_indicators:
        if re.search(pattern, text, re.IGNORECASE):
            return False

    return True  # 超过 200 字但没有任何负面表述 -> 可疑


def score_single_result_regex(result, category_profile=None):
    """
    【V3 升级】对单条搜索结果进行纯正则可信度评分（第一层）

    V3 新增：支持 category_profile 动态品类信号注入。
    当 category_profile 提供时，品类正面信号从 category_profile.category_positive_signals 加载；
    未提供时，回退到硬编码的 CATEGORY_POS_PATTERNS_FALLBACK。

    Args:
        result: 包含 title, snippet, content(可选), platform, base_weight 的字典
        category_profile: 【V3】AI 生成的品类配置（可选）

    Returns:
        评分后的结果字典，附加 credibility_score, credibility_level, signals 字段
    """
    # 合并可用文本
    text_parts = [
        result.get("title", ""),
        result.get("snippet", ""),
        result.get("content", ""),
    ]
    full_text = " ".join(t for t in text_parts if t)

    if not full_text.strip():
        result["credibility_score"] = 0
        result["credibility_level"] = "无内容"
        result["signals"] = []
        return result

    # 基础分 = 平台权重 × 100
    # 【V3】支持 category_profile 动态平台权重
    base_weight = result.get("base_weight", 0.5)
    if category_profile and "platform_relevance" in category_profile:
        platform_key = result.get("platform", "")
        if platform_key in category_profile["platform_relevance"]:
            base_weight = category_profile["platform_relevance"][platform_key]
    base_score = base_weight * 100

    signals = []
    score_delta = 0

    # ---- 负面信号检测 ----
    for name, rule in HIGH_NEG_PATTERNS.items():
        if name == "zero_drawbacks":
            if check_zero_drawbacks(full_text):
                score_delta += rule["score"]
                signals.append({"type": "negative", "weight": "high", "label": rule["label"], "score": rule["score"]})
        elif rule["patterns"]:
            hits = count_pattern_matches(full_text, rule["patterns"])
            if hits > 0:
                penalty = rule["score"] * min(hits, 3)  # 最多计 3 次
                score_delta += penalty
                signals.append({"type": "negative", "weight": "high", "label": rule["label"], "hits": hits, "score": penalty})

    for name, rule in MID_NEG_PATTERNS.items():
        if rule["patterns"]:
            hits = count_pattern_matches(full_text, rule["patterns"])
            if hits > 0:
                penalty = rule["score"] * min(hits, 2)
                score_delta += penalty
                signals.append({"type": "negative", "weight": "mid", "label": rule["label"], "hits": hits, "score": penalty})

    for name, rule in LOW_NEG_PATTERNS.items():
        if rule["patterns"]:
            hits = count_pattern_matches(full_text, rule["patterns"])
            if hits > 0:
                penalty = rule["score"] * min(hits, 2)
                score_delta += penalty
                signals.append({"type": "negative", "weight": "low", "label": rule["label"], "hits": hits, "score": penalty})

    # ---- 正面信号检测 ----
    for name, rule in HIGH_POS_PATTERNS.items():
        if rule["patterns"]:
            hits = count_pattern_matches(full_text, rule["patterns"])
            if hits > 0:
                bonus = rule["score"] * min(hits, 3)
                score_delta += bonus
                signals.append({"type": "positive", "weight": "high", "label": rule["label"], "hits": hits, "score": bonus})

    for name, rule in MID_POS_PATTERNS.items():
        if rule["patterns"]:
            hits = count_pattern_matches(full_text, rule["patterns"])
            if hits > 0:
                bonus = rule["score"] * min(hits, 2)
                score_delta += bonus
                signals.append({"type": "positive", "weight": "mid", "label": rule["label"], "hits": hits, "score": bonus})

    # 【V3 升级】品类特定正面信号检测——优先使用 category_profile 动态信号
    if category_profile:
        # V3 路径：从 category_profile 动态加载品类信号
        dynamic_signals = load_category_signals(category_profile)
        for name, rule in dynamic_signals.items():
            if rule["patterns"]:
                hits = count_pattern_matches(full_text, rule["patterns"])
                if hits > 0:
                    bonus = rule["score"] * min(hits, 2)
                    score_delta += bonus
                    signals.append({
                        "type": "positive", "weight": "mid",
                        "label": rule["label"], "hits": hits, "score": bonus
                    })
    else:
        # Fallback 路径：使用硬编码的品类正面信号（V2 兼容）
        for name, rule in CATEGORY_POS_PATTERNS_FALLBACK.items():
            if rule["patterns"]:
                hits = count_pattern_matches(full_text, rule["patterns"])
                if hits > 0:
                    bonus = rule["score"] * min(hits, 2)
                    score_delta += bonus
                    signals.append({"type": "positive", "weight": "mid", "label": rule["label"], "hits": hits, "score": bonus})

    # 【V5 新增】电商评论层信号检测
    source_layer = result.get("source_layer", "")
    if source_layer == "L1_ecommerce" or result.get("platform") == "ecommerce_indirect":
        # 电商追评正面信号
        for name, rule in ECOMMERCE_POS_PATTERNS.items():
            if rule["patterns"]:
                hits = count_pattern_matches(full_text, rule["patterns"])
                if hits > 0:
                    bonus = rule["score"] * min(hits, 2)
                    score_delta += bonus
                    signals.append({
                        "type": "positive", "weight": "high",
                        "label": rule["label"], "hits": hits, "score": bonus
                    })
        # 电商低价值负面信号
        for name, rule in ECOMMERCE_NEG_PATTERNS.items():
            if rule["patterns"]:
                hits = count_pattern_matches(full_text, rule["patterns"])
                if hits > 0:
                    penalty = rule["score"] * min(hits, 2)
                    score_delta += penalty
                    signals.append({
                        "type": "negative", "weight": "mid",
                        "label": rule["label"], "hits": hits, "score": penalty
                    })

    # 【V5 新增】评论区层信号检测
    if source_layer == "L2_comment_section" or result.get("platform") == "comment_section_indirect":
        for name, rule in COMMENT_SECTION_POS_PATTERNS.items():
            if rule["patterns"]:
                hits = count_pattern_matches(full_text, rule["patterns"])
                if hits > 0:
                    bonus = rule["score"] * min(hits, 2)
                    score_delta += bonus
                    signals.append({
                        "type": "positive", "weight": "high",
                        "label": rule["label"], "hits": hits, "score": bonus
                    })
        for name, rule in COMMENT_SECTION_NEG_PATTERNS.items():
            if rule["patterns"]:
                hits = count_pattern_matches(full_text, rule["patterns"])
                if hits > 0:
                    penalty = rule["score"] * min(hits, 2)
                    score_delta += penalty
                    signals.append({
                        "type": "negative", "weight": "low",
                        "label": rule["label"], "hits": hits, "score": penalty
                    })

    # 【V5 新增】非层级标注的内容也检测电商评论特征（全局检测）
    if source_layer not in ("L1_ecommerce", "L2_comment_section"):
        # 任何来源中如果包含电商追评特征，给予加分
        for name, rule in ECOMMERCE_POS_PATTERNS.items():
            if rule["patterns"]:
                hits = count_pattern_matches(full_text, rule["patterns"])
                if hits > 0:
                    # 非电商层级的结果中发现电商特征，按0.5系数加分
                    bonus = int(rule["score"] * 0.5) * min(hits, 2)
                    score_delta += bonus
                    signals.append({
                        "type": "positive", "weight": "mid",
                        "label": f"{rule['label']}(跨层级)", "hits": hits, "score": bonus
                    })

    # 知乎高赞惩罚（如果标题/URL 暗示高赞）
    if result.get("platform") == "zhihu":
        zhihu_hot = re.search(r"(?:\d+\s*(?:赞同|赞|个赞|万赞|k\s*赞))", full_text, re.IGNORECASE)
        if zhihu_hot:
            score_delta -= 15
            signals.append({"type": "negative", "weight": "mid", "label": "知乎高赞回答（软文概率高）", "score": -15})

    # 即时窗口时效性加分
    recency_bonus = result.get("recency_bonus", 0)
    if recency_bonus > 0:
        score_delta += recency_bonus
        signals.append({"type": "positive", "weight": "low", "label": "近期内容（时效性加分）", "score": recency_bonus})

    # 计算最终分数
    final_score = max(0, min(100, base_score + score_delta))

    # 评定等级
    if final_score >= 80:
        level = "高可信度"
    elif final_score >= 60:
        level = "中可信度"
    elif final_score >= 40:
        level = "低可信度"
    else:
        level = "疑似软文"

    result["credibility_score"] = round(final_score, 1)
    result["credibility_level"] = level
    result["signals"] = signals
    result["base_score"] = round(base_score, 1)
    result["score_delta"] = round(score_delta, 1)

    return result


# 保持向后兼容：原函数名指向正则版本
def score_single_result(result, category_profile=None):
    """向后兼容接口，调用正则评分"""
    return score_single_result_regex(result, category_profile=category_profile)


def score_single_result_v2(result, ai_analyzer=None, category_profile=None):
    """
    【V3 升级】双层融合评分：正则 + AI 语义分析 + 品类信号动态注入

    第一层：正则快速粗筛（成本为零）+ 品类信号动态注入
    第二层：AI 语义深度分析（灰色地带精判）
    融合层：加权合并两层分数

    Args:
        result: 搜索结果字典
        ai_analyzer: AICredibilityAnalyzer 实例（None 则退化为纯正则）
        category_profile: 【V3】AI 生成的品类配置（可选）

    Returns:
        评分后的结果字典，包含正则分、AI分、融合分和详细分析
    """
    # 导入融合函数（延迟导入避免循环依赖）
    from ai_credibility_analyzer import compute_fusion_score, classify_credibility_level

    # 第一层：正则评分（V3：支持 category_profile）
    result = score_single_result_regex(result, category_profile=category_profile)
    regex_score = result["credibility_score"]

    # 初始化 AI 相关字段
    ai_score = None
    ai_detail = None
    ai_pending_prompt = None

    # 第二层：判断是否需要 AI 深度分析
    if ai_analyzer and ai_analyzer.should_analyze(regex_score):
        content = result.get("content", result.get("snippet", ""))
        if content and len(content) >= 50:  # 内容至少 50 字才值得分析
            ai_result = ai_analyzer.analyze_single(
                title=result.get("title", ""),
                content=content,
                platform=result.get("platform_name", ""),
                url=result.get("url", ""),
            )

            if ai_result.get("_needs_ai_call"):
                # AI 分析需要宿主 AI 执行 prompt
                ai_pending_prompt = ai_result["_prompt"]
                result["_ai_pending"] = True
                result["_ai_prompt"] = ai_pending_prompt
            elif not ai_result.get("ai_error"):
                # 已有缓存结果
                ai_score = ai_result["total"]
                ai_detail = ai_result

    # 融合层
    content_length = len(result.get("content", ""))
    final_score, alpha, beta = compute_fusion_score(regex_score, ai_score, content_length)

    # 更新结果
    result["credibility_score"] = final_score
    result["regex_score"] = regex_score
    result["ai_score"] = ai_score
    result["ai_detail"] = ai_detail
    result["fusion_weights"] = {"alpha": alpha, "beta": beta}
    result["scoring_version"] = "v2"
    result["credibility_level"] = classify_credibility_level(final_score)

    return result


def score_all_results(results, category_profile=None):
    """对所有结果进行评分并按可信度排序（纯正则模式）"""
    scored = [score_single_result_regex(r, category_profile=category_profile) for r in results]
    scored.sort(key=lambda x: x["credibility_score"], reverse=True)
    return scored


def score_all_results_v2(results, ai_analyzer=None, category_profile=None):
    """
    【V3 升级】对所有结果进行双层融合评分

    Args:
        results: 搜索结果列表
        ai_analyzer: AICredibilityAnalyzer 实例
        category_profile: 【V3】AI 生成的品类配置（可选）

    Returns:
        评分后按可信度排序的结果列表
    """
    scored = []
    for r in results:
        scored_r = score_single_result_v2(r, ai_analyzer=ai_analyzer, category_profile=category_profile)
        scored.append(scored_r)
    scored.sort(key=lambda x: x["credibility_score"], reverse=True)
    return scored


# ============================================================
# 统计与摘要
# ============================================================

def generate_summary(scored_results):
    """生成评分统计摘要（兼容 V1 和 V2）"""
    total = len(scored_results)
    if total == 0:
        return {"total": 0, "message": "无结果"}

    levels = {"高可信度": 0, "中可信度": 0, "低可信度": 0, "疑似软文": 0, "无内容": 0}
    platform_stats = {}
    ai_analyzed_count = 0
    v2_count = 0

    for r in scored_results:
        lvl = r.get("credibility_level", "无内容")
        levels[lvl] = levels.get(lvl, 0) + 1

        pn = r.get("platform_name", "未知")
        if pn not in platform_stats:
            platform_stats[pn] = {"total": 0, "avg_score": 0, "scores": []}
        platform_stats[pn]["total"] += 1
        platform_stats[pn]["scores"].append(r.get("credibility_score", 0))

        # 【V2】统计 AI 分析覆盖率
        if r.get("ai_score") is not None:
            ai_analyzed_count += 1
        if r.get("scoring_version") == "v2":
            v2_count += 1

    # 【V5 新增】数据源分层统计
    source_layer_stats = {}
    for r in scored_results:
        layer = r.get("source_layer", "L3_forum_post")
        if layer not in source_layer_stats:
            source_layer_stats[layer] = {"total": 0, "avg_score": 0, "scores": []}
        source_layer_stats[layer]["total"] += 1
        source_layer_stats[layer]["scores"].append(r.get("credibility_score", 0))

    for layer, stats in source_layer_stats.items():
        if stats["scores"]:
            stats["avg_score"] = round(sum(stats["scores"]) / len(stats["scores"]), 1)
        del stats["scores"]

    # 计算平台平均分
    for pn, stats in platform_stats.items():
        if stats["scores"]:
            stats["avg_score"] = round(sum(stats["scores"]) / len(stats["scores"]), 1)
        del stats["scores"]

    summary = {
        "total": total,
        "credibility_distribution": levels,
        "platform_stats": platform_stats,
        "reliable_count": levels["高可信度"] + levels["中可信度"],
        "suspicious_count": levels["低可信度"] + levels["疑似软文"],
        "reliable_ratio": round((levels["高可信度"] + levels["中可信度"]) / total * 100, 1) if total > 0 else 0,
    }

    # 【V5 新增】数据源分层统计
    if source_layer_stats and len(source_layer_stats) > 1:
        summary["source_layer_stats"] = source_layer_stats

    # 【V2】添加 AI 分析统计
    if v2_count > 0:
        summary["scoring_version"] = "v2"
        summary["ai_analyzed_count"] = ai_analyzed_count
        summary["ai_coverage_ratio"] = round(ai_analyzed_count / total * 100, 1) if total > 0 else 0

    return summary


# ============================================================
# 主程序
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="可信度评分引擎 - 过滤软文和水军",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python credibility_scorer.py search_results.json --output scored.json
    python credibility_scorer.py search_results.json --threshold 60
    python credibility_scorer.py search_results.json --summary-only
    python credibility_scorer.py search_results.json --v2 --output scored_v2.json
        """,
    )

    parser.add_argument(
        "input",
        help="输入文件路径（JSON 格式，由 platform_search.py 生成）。用 '-' 表示 stdin",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="输出文件路径。不指定则输出到 stdout",
    )
    parser.add_argument(
        "--threshold", "-t",
        type=float, default=0,
        help="只输出可信度高于此阈值的结果（默认 0，即全部输出）",
    )
    parser.add_argument(
        "--summary-only", "-s",
        action="store_true",
        help="只输出统计摘要，不输出详细结果",
    )
    parser.add_argument(
        "--v2",
        action="store_true",
        help="【V2】启用双层融合评分（正则 + AI 语义分析）",
    )
    parser.add_argument(
        "--max-ai-batch",
        type=int, default=20,
        help="【V2】AI 分析的最大批量数（默认 20）",
    )
    parser.add_argument(
        "--category-profile",
        default=None,
        help="【V3】品类配置文件路径（JSON 格式，由 AI 品类自适应分析生成）",
    )

    args = parser.parse_args()

    # 【V3】加载品类配置
    category_profile = None
    if args.category_profile:
        with open(args.category_profile, "r", encoding="utf-8") as f:
            category_profile = json.load(f)
        print(f"[INFO] 已加载品类配置: {category_profile.get('category', '未知品类')}", file=sys.stderr)

    # 读取输入
    if args.input == "-":
        input_data = json.load(sys.stdin)
    else:
        with open(args.input, "r", encoding="utf-8") as f:
            input_data = json.load(f)

    results = input_data.get("results", [])
    if not results:
        print("[WARN] 输入数据中无结果", file=sys.stderr)
        sys.exit(0)

    print(f"[INFO] 开始对 {len(results)} 条结果进行可信度评分", file=sys.stderr)

    # 评分
    if args.v2:
        print(f"[INFO] 使用 V2 双层融合评分模式", file=sys.stderr)
        from ai_credibility_analyzer import AICredibilityAnalyzer
        ai_analyzer = AICredibilityAnalyzer(max_batch=args.max_ai_batch)
        scored = score_all_results_v2(results, ai_analyzer=ai_analyzer, category_profile=category_profile)
        ai_stats = ai_analyzer.get_stats()
        print(f"[INFO] AI 分析统计: {json.dumps(ai_stats, ensure_ascii=False)}", file=sys.stderr)
    else:
        scored = score_all_results(results, category_profile=category_profile)

    # 按阈值过滤
    if args.threshold > 0:
        scored = [r for r in scored if r.get("credibility_score", 0) >= args.threshold]
        print(f"[INFO] 阈值 {args.threshold} 过滤后剩余 {len(scored)} 条", file=sys.stderr)

    # 生成摘要
    summary = generate_summary(scored)

    print(f"\n[DONE] 评分完成", file=sys.stderr)
    print(f"  - 总计: {summary['total']} 条", file=sys.stderr)
    print(f"  - 可信内容: {summary['reliable_count']} 条 ({summary['reliable_ratio']}%)", file=sys.stderr)
    print(f"  - 可疑内容: {summary['suspicious_count']} 条", file=sys.stderr)
    for level, count in summary["credibility_distribution"].items():
        if count > 0:
            print(f"    [{level}]: {count} 条", file=sys.stderr)

    if args.summary_only:
        output_data = {"summary": summary}
    else:
        output_data = {
            "query": input_data.get("query", ""),
            "search_time": input_data.get("search_time", ""),
            "scoring_time": datetime.now().isoformat(),
            "summary": summary,
            "results": scored,
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
