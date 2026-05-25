#!/usr/bin/env python3
"""生成工作流：先分析意图再生成（内部两步对用户透明）"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from _common import api_post, json_output, error_exit


def analyze_intent(description: str, language: str = "auto") -> dict:
    """
    分析用户意图（Step 2）
    
    Args:
        description: 用户的自然语言描述
        language: 语言代码（auto 自动检测）
    
    Returns:
        分析结果
    """
    body = {"description": description}
    if language and language != "auto":
        body["language"] = language
    
    resp = api_post("/api/agent/nl2workflow/analyze", body)
    return resp


def generate_workflow_from_description(
    description: str,
    reference_urls: list = None,
    skill_id: str = None,
    plan_id: str = None,
) -> dict:
    """
    生成工作流（Step 3）
    
    Args:
        description: 用户的自然语言描述
        reference_urls: 参考文件 URL 列表
        skill_id: 指定的 Skill ID
        plan_id: 从分析结果中选择的 plan_id
    
    Returns:
        生成的工作流数据
    """
    body = {"description": description}
    
    if reference_urls:
        body["reference_urls"] = reference_urls
    
    if skill_id:
        body["skill_id"] = skill_id
    
    if plan_id:
        body["plan_id"] = plan_id
    
    resp = api_post("/api/agent/nl2workflow/generate", body, timeout=120)
    return resp


def main():
    parser = argparse.ArgumentParser(
        description="从自然语言描述生成 VoooAI 工作流（合并意图分析+工作流生成）",
        epilog="""
环境变量:
  VOOOAI_ACCESS_KEY  必填，Bearer 鉴权
  VOOOAI_BASE_URL    可选，默认 https://voooai.com

示例:
  # 基本用法：生成一个产品宣传视频
  python3 generate_workflow.py "帮我生成一个咖啡产品宣传视频，要有背景音乐"

  # 带参考图片
  python3 generate_workflow.py "基于这张图片生成一个视频" \\
    --reference-urls https://example.com/image.jpg

  # 指定技能
  python3 generate_workflow.py "生成一组分镜图" --skill-id storyboard-basic

  # 多个参考文件
  python3 generate_workflow.py "使用这些素材制作视频" \\
    --reference-urls https://a.com/1.jpg https://b.com/2.mp4

工作流程:
  1. 调用 POST /api/agent/nl2workflow/analyze 分析意图
  2. 调用 POST /api/agent/nl2workflow/generate 生成工作流
  3. 返回 template_data（用于后续执行）

注意:
  - 保持用户描述原文，不要添加或修改
  - 如果有 points_warning，表示积分可能不足
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "description",
        help="用户的自然语言描述（会原样传递给 API）",
    )
    parser.add_argument(
        "--reference-urls",
        nargs="+",
        default=[],
        help="参考文件 URL 列表（图片/视频/音频）",
    )
    parser.add_argument(
        "--skill-id",
        default="",
        help="指定使用的 Skill ID（可选，留空则自动选择）",
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="仅分析意图，不生成工作流",
    )
    parser.add_argument(
        "--language",
        default="auto",
        help="语言代码（auto=自动检测，zh=中文，en=英文）",
    )
    args = parser.parse_args()

    description = args.description.strip()
    if not description:
        error_exit("描述不能为空")
    
    # Step 1: 分析意图
    print("正在分析意图...", file=sys.stderr)
    analyze_resp = analyze_intent(description, args.language)
    
    if not analyze_resp.get("success"):
        error_exit(f"意图分析失败: {analyze_resp.get('message', '未知错误')}")
    
    # 如果只需要分析
    if args.analyze_only:
        out = {
            "success": True,
            "analysis": analyze_resp,
        }
        json_output(out)
        return
    
    # 从分析结果中提取 plan_id（如果有）
    plan_id = None
    if "plans" in analyze_resp and analyze_resp["plans"]:
        # 默认选择第一个推荐的计划
        plan_id = analyze_resp["plans"][0].get("plan_id")
    
    # Step 2: 生成工作流
    print("正在生成工作流...", file=sys.stderr)
    generate_resp = generate_workflow_from_description(
        description=description,
        reference_urls=args.reference_urls or None,
        skill_id=args.skill_id or None,
        plan_id=plan_id,
    )
    
    if not generate_resp.get("success"):
        error_exit(f"工作流生成失败: {generate_resp.get('message', '未知错误')}")
    
    # 提取关键信息
    template_data = generate_resp.get("template_data", {})
    metadata = generate_resp.get("metadata", {})
    explanation = generate_resp.get("explanation", "")
    
    # 构建输出
    out = {
        "success": True,
        "template_data": template_data,
        "explanation": explanation,
        "metadata": {
            "node_count": metadata.get("node_count", 0),
            "engine_nodes": metadata.get("engine_nodes", []),
            "estimated_points": metadata.get("estimated_points", 0),
        },
    }
    
    # 检查积分警告
    points_warning = metadata.get("points_warning")
    if points_warning:
        out["points_warning"] = points_warning
        # 输出警告到 stderr
        warning_msg = points_warning.get("message_key", "")
        estimated = points_warning.get("estimated", 0)
        available = points_warning.get("available", 0)
        suggestion = points_warning.get("suggestion", "")
        
        print(f"\n⚠️  积分警告:", file=sys.stderr)
        print(f"   预估消耗: {estimated} 点", file=sys.stderr)
        print(f"   可用余额: {available} 点", file=sys.stderr)
        if suggestion:
            print(f"   建议: {suggestion}", file=sys.stderr)
        print("", file=sys.stderr)
    
    # 分析摘要（如果有）
    if "analysis" in analyze_resp:
        out["analysis_summary"] = analyze_resp.get("analysis", {})
    
    json_output(out)


if __name__ == "__main__":
    main()
