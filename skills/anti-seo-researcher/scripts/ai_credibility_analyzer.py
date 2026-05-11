#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 语义分析可信度评分器（V2 新增模块）

基于大语言模型对帖子内容进行多维度语义分析，
弥补正则表达式规则引擎在复杂场景下的识别盲区。

核心能力：
- 5 维度评分：语气真实性、论述逻辑、细节丰富度、情感一致性、利益关联判断
- 伪缺点识别：能识别"唯一缺点是包装不好看"这类高级软文手法
- 灰色地带精判：只对正则分 30-85 的帖子调用 AI，避免浪费
- 本地缓存：相同 URL 不重复分析

用法:
    # 作为模块被 credibility_scorer.py 调用
    from ai_credibility_analyzer import AICredibilityAnalyzer

    analyzer = AICredibilityAnalyzer()
    result = analyzer.analyze_single(title, content, platform)

    # 独立运行：分析单条内容
    python ai_credibility_analyzer.py --title "标题" --content "正文内容" --platform "知乎"

    # 批量分析
    python ai_credibility_analyzer.py --input results.json --output ai_scored.json
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime


# ============================================================
# AI 评分 Prompt 模板
# ============================================================

AI_SCORING_PROMPT = """你是一个专业的互联网内容可信度分析师。你的任务是判断以下帖子是否为真实用户反馈、还是软文/水军内容。

## 待分析帖子
标题：{title}
平台：{platform}
正文：
{content}

## 评估维度

请从以下 5 个维度进行评估，每个维度 0-20 分（总分 0-100）：

### 1. 语气真实性（0-20分）
- 20分：语言自然、有个人情绪波动、口语化、有犹豫和不确定性
- 10分：语言较为正式但有个人色彩
- 0分：语言高度规范化、像模板写作、措辞精准如公关稿

### 2. 论述逻辑（0-20分）
- 20分：叙事自然流畅、有时间线索、有因果逻辑、信息密度适中
- 10分：有一定逻辑但部分段落像拼凑
- 0分：行文结构化、卖点逐一罗列、像产品说明书或测评模板

### 3. 细节丰富度（0-20分）
- 20分：包含具体使用场景、精确时间、独特个人经历、非标准化的细节
- 10分：有一些细节但偏泛化
- 0分：细节缺失或全是公开信息（参数、规格）

### 4. 情感一致性（0-20分）
- 20分：情感表达与描述内容匹配、有真实的纠结和权衡
- 10分：情感较为单一但不算虚假
- 0分：一边倒的情感表达、过度正面或过度负面、缺点部分敷衍

### 5. 利益关联判断（0-20分）
- 20分：无任何商业引导、不含链接/优惠码、无引流行为
- 10分：有轻微的推荐倾向但无明显利益关联
- 0分：包含购买链接、优惠码、引流话术、明显的商业合作

## 特别注意
- "伪缺点"识别：如果缺点描述的是无关痛痒的方面（如"包装一般"、"颜色不够多"、"价格小贵"），而所有核心功能都是满分评价，这可能是高级软文的伪缺点手法，应降低情感一致性得分。
- 如果帖子过短（不足50字），在论述逻辑和细节丰富度上应保守打分。
- 注意区分"真正有用的使用反馈"和"拼凑公开信息的伪原创"。

## 输出格式
严格按以下 JSON 格式输出，不要添加任何额外文字：
{{
    "tone_authenticity": <0-20>,
    "logic_coherence": <0-20>,
    "detail_richness": <0-20>,
    "emotional_consistency": <0-20>,
    "interest_independence": <0-20>,
    "total": <0-100>,
    "verdict": "<真实反馈|疑似软文|难以判断>",
    "reasoning": "<一句话解释判断理由>"
}}"""


# ============================================================
# 缓存管理
# ============================================================

class AnalysisCache:
    """本地 JSON 文件缓存，避免对相同内容重复调用 AI"""

    def __init__(self, cache_dir=None):
        if cache_dir is None:
            # 默认缓存目录在脚本同级的 .cache 下
            script_dir = os.path.dirname(os.path.abspath(__file__))
            cache_dir = os.path.join(script_dir, ".cache")
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "ai_analysis_cache.json")
        self._cache = self._load()

    def _load(self):
        """加载缓存文件"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save(self):
        """保存缓存到文件"""
        os.makedirs(self.cache_dir, exist_ok=True)
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self._cache, f, ensure_ascii=False, indent=2)

    def _make_key(self, url, content):
        """生成缓存键（基于 URL 或内容哈希）"""
        if url:
            return f"url:{url}"
        return f"hash:{hashlib.md5(content.encode()).hexdigest()}"

    def get(self, url="", content=""):
        """获取缓存的分析结果"""
        key = self._make_key(url, content)
        return self._cache.get(key)

    def set(self, result, url="", content=""):
        """设置缓存"""
        key = self._make_key(url, content)
        self._cache[key] = {
            "result": result,
            "cached_at": datetime.now().isoformat(),
        }
        self._save()

    @property
    def size(self):
        return len(self._cache)


# ============================================================
# AI 分析核心
# ============================================================

def _get_default_result():
    """AI 分析失败时返回的中性默认结果"""
    return {
        "tone_authenticity": 10,
        "logic_coherence": 10,
        "detail_richness": 10,
        "emotional_consistency": 10,
        "interest_independence": 10,
        "total": 50,
        "verdict": "难以判断",
        "reasoning": "AI分析响应解析失败，使用默认分数",
        "ai_error": True,
    }


SCORE_DIMENSIONS = [
    "tone_authenticity",
    "logic_coherence",
    "detail_richness",
    "emotional_consistency",
    "interest_independence",
]


def parse_ai_response(response_text):
    """
    解析 AI 模型的 JSON 响应

    Args:
        response_text: AI 返回的文本

    Returns:
        解析后的评分字典，或失败时的默认结果
    """
    try:
        # 尝试直接解析
        result = json.loads(response_text.strip())
    except json.JSONDecodeError:
        # 尝试从文本中提取 JSON 块
        json_match = re.search(r'\{[^{}]*"tone_authenticity"[^{}]*\}', response_text, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
            except json.JSONDecodeError:
                return _get_default_result()
        else:
            return _get_default_result()

    # 校验并修正分数范围
    for key in SCORE_DIMENSIONS:
        if key not in result:
            result[key] = 10  # 缺失维度给中性分
        else:
            result[key] = max(0, min(20, int(result[key])))

    # 重新计算总分（确保一致性）
    result["total"] = sum(result[k] for k in SCORE_DIMENSIONS)

    # 确保 verdict 字段存在
    if "verdict" not in result:
        if result["total"] >= 70:
            result["verdict"] = "真实反馈"
        elif result["total"] <= 35:
            result["verdict"] = "疑似软文"
        else:
            result["verdict"] = "难以判断"

    # 确保 reasoning 字段存在
    if "reasoning" not in result:
        result["reasoning"] = ""

    result["ai_error"] = False
    return result


class AICredibilityAnalyzer:
    """
    AI 语义分析可信度评分器

    使用大语言模型从语气真实性、论述逻辑、细节丰富度、
    情感一致性、利益关联判断五个维度评估内容可信度。
    """

    def __init__(self, max_batch=20, cache_dir=None):
        """
        Args:
            max_batch: 单次调查最多分析的帖子数量（成本控制）
            cache_dir: 缓存目录路径
        """
        self.max_batch = max_batch
        self.cache = AnalysisCache(cache_dir)
        self._analysis_count = 0  # 本次会话的分析计数

    def analyze_single(self, title, content, platform, url=""):
        """
        分析单条帖子的可信度

        Args:
            title: 帖子标题
            content: 帖子正文
            platform: 发布平台名称
            url: 帖子 URL（用于缓存）

        Returns:
            评分结果字典，包含五个维度分数、总分、判定和理由
        """
        # 检查缓存
        cached = self.cache.get(url=url, content=content)
        if cached:
            print(f"[AI] 命中缓存: {url[:60] if url else title[:30]}", file=sys.stderr)
            return cached["result"]

        # 检查批量上限
        if self._analysis_count >= self.max_batch:
            print(f"[AI] 已达批量上限 ({self.max_batch})，跳过分析", file=sys.stderr)
            return _get_default_result()

        # 构建 Prompt
        # 截断过长内容以控制 token 消耗
        truncated_content = content[:3000] if content else ""
        prompt = AI_SCORING_PROMPT.format(
            title=title or "无标题",
            content=truncated_content or "无正文内容",
            platform=platform or "未知平台",
        )

        # 调用 AI 模型
        # 注意：此处的 AI 调用由宿主环境（SKILL.md 工作流中的 AI）代理执行
        # 在独立运行模式下，通过 stdin/stdout 模拟
        print(f"[AI] 分析中: {title[:50]}...", file=sys.stderr)
        self._analysis_count += 1

        # 返回 prompt 供宿主 AI 执行
        # 实际调用由 credibility_scorer.py 的融合层发起
        return {
            "_prompt": prompt,
            "_needs_ai_call": True,
            "_url": url,
            "_title": title,
        }

    def process_ai_response(self, response_text, url="", content=""):
        """
        处理 AI 模型返回的响应文本

        在宿主 AI 执行了 prompt 后，将响应传回此方法进行解析和缓存。

        Args:
            response_text: AI 模型返回的文本
            url: 原始帖子 URL（用于缓存键）
            content: 原始内容（用于缓存键备用）

        Returns:
            解析后的评分结果字典
        """
        result = parse_ai_response(response_text)

        # 写入缓存（非错误结果才缓存）
        if not result.get("ai_error"):
            self.cache.set(result, url=url, content=content)

        return result

    def analyze_batch(self, items):
        """
        批量分析多条帖子

        Args:
            items: 帖子列表，每条应包含 title, content/snippet, platform_name, url 字段

        Returns:
            分析结果列表（与输入一一对应）
        """
        results = []
        batch = items[:self.max_batch]

        for i, item in enumerate(batch):
            content = item.get("content", item.get("snippet", ""))
            result = self.analyze_single(
                title=item.get("title", ""),
                content=content,
                platform=item.get("platform_name", "未知"),
                url=item.get("url", ""),
            )
            results.append(result)
            print(f"[AI] 批量进度: {i+1}/{len(batch)}", file=sys.stderr)

        return results

    def should_analyze(self, regex_score):
        """
        判断是否需要 AI 深度分析（灰色地带过滤）

        不是所有帖子都需要过 AI：
        - 正则分 < 30：明显的软文，不需要 AI 确认
        - 正则分 > 85：明显的真实反馈，不需要 AI 确认
        - 30-85 分：灰色地带，需要 AI 深度判别

        Args:
            regex_score: 正则评分引擎给出的分数

        Returns:
            True 表示需要 AI 分析，False 表示不需要
        """
        return 30 <= regex_score <= 85

    def should_use_advanced_model(self, regex_score):
        """
        判断是否使用高级模型（对高价值灰色帖子）

        对正则分 40-75 的"核心灰色地带"使用更精准的高级模型。

        Args:
            regex_score: 正则评分分数

        Returns:
            True 表示应使用高级模型
        """
        return 40 <= regex_score <= 75

    @property
    def analysis_count(self):
        """本次会话已分析的帖子数"""
        return self._analysis_count

    @property
    def cache_size(self):
        """缓存中的条目数"""
        return self.cache.size

    def get_stats(self):
        """获取分析统计信息"""
        return {
            "session_analysis_count": self._analysis_count,
            "max_batch": self.max_batch,
            "cache_size": self.cache.size,
            "remaining_quota": max(0, self.max_batch - self._analysis_count),
        }


# ============================================================
# 融合评分辅助函数
# ============================================================

def compute_fusion_score(regex_score, ai_score, content_length=0):
    """
    计算正则分数与 AI 分数的融合分

    Args:
        regex_score: 正则评分引擎分数 (0-100)
        ai_score: AI 语义分析分数 (0-100)
        content_length: 分析内容的长度

    Returns:
        (final_score, alpha, beta) 元组
        alpha: 正则权重
        beta: AI 权重
    """
    if ai_score is None:
        # AI 未参与评分，回退到纯正则
        return regex_score, 1.0, 0.0

    if content_length >= 200:
        # 全文场景：更信任 AI（AI 能理解语境）
        alpha, beta = 0.3, 0.7
    else:
        # 摘要场景：更信任正则（AI 信息不足）
        alpha, beta = 0.6, 0.4

    final = regex_score * alpha + ai_score * beta
    final = max(0, min(100, round(final, 1)))

    return final, alpha, beta


def classify_credibility_level(score):
    """
    根据分数判定可信度等级

    Args:
        score: 最终可信度分数

    Returns:
        等级字符串
    """
    if score >= 80:
        return "高可信度"
    elif score >= 60:
        return "中可信度"
    elif score >= 40:
        return "低可信度"
    else:
        return "疑似软文"


# ============================================================
# 主程序（独立运行模式）
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="AI 语义分析可信度评分器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 分析单条内容
    python ai_credibility_analyzer.py --title "用了半年的真实感受" --content "买了半年了..." --platform "知乎"

    # 批量分析（输入为 credibility_scorer.py 输出的 JSON）
    python ai_credibility_analyzer.py --input scored_results.json --output ai_scored.json

    # 查看缓存统计
    python ai_credibility_analyzer.py --cache-stats
        """,
    )

    parser.add_argument("--title", default=None, help="帖子标题（单条分析模式）")
    parser.add_argument("--content", default=None, help="帖子正文（单条分析模式）")
    parser.add_argument("--platform", default="未知", help="发布平台")
    parser.add_argument("--input", "-i", default=None, help="批量分析输入文件（JSON）")
    parser.add_argument("--output", "-o", default=None, help="输出文件路径")
    parser.add_argument("--max-batch", type=int, default=20, help="最大分析条数（默认20）")
    parser.add_argument("--cache-stats", action="store_true", help="显示缓存统计信息")
    parser.add_argument(
        "--gray-zone-only",
        action="store_true",
        help="只分析正则分 30-85 的灰色地带帖子",
    )

    args = parser.parse_args()

    analyzer = AICredibilityAnalyzer(max_batch=args.max_batch)

    if args.cache_stats:
        stats = analyzer.get_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return

    if args.title and args.content:
        # 单条分析模式
        result = analyzer.analyze_single(
            title=args.title,
            content=args.content,
            platform=args.platform,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.input:
        # 批量分析模式
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)

        results_list = data.get("results", [])

        if args.gray_zone_only:
            # 只分析灰色地带
            to_analyze = [
                r for r in results_list
                if analyzer.should_analyze(r.get("credibility_score", 50))
            ]
            print(f"[INFO] 灰色地带过滤: {len(results_list)} -> {len(to_analyze)} 条", file=sys.stderr)
        else:
            to_analyze = results_list

        # 执行批量分析
        ai_results = analyzer.analyze_batch(to_analyze)

        # 输出
        output_data = {
            "analysis_time": datetime.now().isoformat(),
            "stats": analyzer.get_stats(),
            "results": ai_results,
        }

        json_str = json.dumps(output_data, ensure_ascii=False, indent=2)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(json_str)
            print(f"[DONE] 结果已保存到: {args.output}", file=sys.stderr)
        else:
            print(json_str)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
