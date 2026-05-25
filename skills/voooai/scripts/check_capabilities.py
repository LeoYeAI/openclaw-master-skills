#!/usr/bin/env python3
"""探测 VoooAI 平台能力和积分余额：GET /api/agent/capabilities"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from _common import api_get, json_output


def check_capabilities() -> dict:
    """
    调用能力发现端点，获取可用引擎、Skills 和积分余额。
    
    Returns:
        能力信息字典
    """
    resp = api_get("/api/agent/capabilities")
    return resp


def main():
    parser = argparse.ArgumentParser(
        description="探测 VoooAI 平台能力和积分余额",
        epilog="""
环境变量:
  VOOOAI_ACCESS_KEY  必填，Bearer 鉴权
  VOOOAI_BASE_URL    可选，默认 https://voooai.com

示例:
  # 查看平台能力和积分余额
  python3 check_capabilities.py

  # 使用自定义服务器
  VOOOAI_BASE_URL=https://dev.voooai.com python3 check_capabilities.py
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="仅输出摘要信息（积分、引擎数量、技能数量）",
    )
    args = parser.parse_args()

    data = check_capabilities()
    
    if not data.get("success"):
        print(f"错误：{data.get('message', '未知错误')}", file=sys.stderr)
        sys.exit(1)
    
    # 提取关键信息
    constraints = data.get("constraints", {})
    user_status = constraints.get("user_status", {})
    points_balance = user_status.get("points_balance", 0)
    membership_level = user_status.get("membership_level", 0)
    
    engines = data.get("engines", {})
    skills = data.get("skills", [])
    trust_level = data.get("trust_level", "unknown")
    
    # 判断积分是否不足（低于 10 点警告）
    points_warning = points_balance < 10
    
    if args.summary:
        # 简洁摘要输出
        out = {
            "trust_level": trust_level,
            "points_balance": points_balance,
            "membership_level": membership_level,
            "points_warning": points_warning,
            "available_engines": len(engines),
            "available_skills": len(skills),
        }
        if points_warning:
            out["warning_message"] = f"积分余额较低（{points_balance}点），部分功能可能无法使用"
    else:
        # 完整输出
        out = {
            "success": True,
            "trust_level": trust_level,
            "points_balance": points_balance,
            "membership_level": membership_level,
            "points_warning": points_warning,
            "rate_limit": data.get("rate_limit", {}),
            "engines": engines,
            "skills": skills,
            "constraints": constraints,
        }
        
        # 如果有成本指南（trusted_agent 可见）
        if "cost_guide" in data:
            out["cost_guide"] = data["cost_guide"]
        
        # 如果有工作流指南
        if "workflow_guide" in data:
            out["workflow_guide"] = data["workflow_guide"]
        
        # 如果有数据警告
        if "data_warnings" in data:
            out["data_warnings"] = data["data_warnings"]
        
        if points_warning:
            out["warning_message"] = f"积分余额较低（{points_balance}点），建议充值后再使用"
    
    json_output(out)


if __name__ == "__main__":
    main()
