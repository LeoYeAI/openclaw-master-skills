#!/usr/bin/env python3
"""执行整个工作流：POST /api/node-builder/execute"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from _common import (
    api_post,
    json_output,
    error_exit,
    load_json_arg,
    parse_set_params,
    apply_params_to_workflow,
)


def execute_workflow(workflow_data: dict) -> dict:
    """
    执行工作流
    
    Args:
        workflow_data: 工作流数据（template_data）
    
    Returns:
        执行结果，包含 execution_id
    """
    body = {"workflow": workflow_data}
    resp = api_post("/api/node-builder/execute", body, timeout=120)
    return resp


def main():
    parser = argparse.ArgumentParser(
        description="执行 VoooAI 工作流",
        epilog="""
环境变量:
  VOOOAI_ACCESS_KEY  必填，Bearer 鉴权
  VOOOAI_BASE_URL    可选，默认 https://voooai.com

示例:
  # 从 JSON 字符串执行
  python3 execute_workflow.py '{"nodes": [...], "connections": [...]}'

  # 从文件执行
  python3 execute_workflow.py /path/to/workflow.json

  # 从 stdin 读取（管道传入）
  cat workflow.json | python3 execute_workflow.py --from-stdin

  # 与 generate_workflow 配合使用
  python3 generate_workflow.py "生成一张猫的图片" | \\
    jq -r '.template_data' | python3 execute_workflow.py --from-stdin

  # 修改参数后执行
  python3 execute_workflow.py workflow.json \\
    --set-param node_1.prompt="一只可爱的猫咪" \\
    --set-param node_1.duration=10

参数格式:
  --set-param node_id.param_name=value
  例如: --set-param node_1.prompt="新提示词"
        --set-param node_2.duration=8
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "template_data",
        nargs="?",
        default="",
        help="工作流 JSON 字符串或文件路径（使用 --from-stdin 时可省略）",
    )
    parser.add_argument(
        "--from-stdin",
        action="store_true",
        help="从 stdin 读取 template_data JSON",
    )
    parser.add_argument(
        "--set-param",
        action="append",
        default=[],
        help="设置节点参数（格式：node_id.param_name=value，可多次使用）",
    )
    args = parser.parse_args()

    # 获取工作流数据
    workflow_data = None
    
    if args.from_stdin:
        # 从 stdin 读取
        try:
            stdin_content = sys.stdin.read().strip()
            if not stdin_content:
                error_exit("stdin 为空")
            workflow_data = json.loads(stdin_content)
        except json.JSONDecodeError as e:
            error_exit(f"stdin 内容不是有效的 JSON: {e}")
    elif args.template_data:
        # 从参数读取（支持 JSON 字符串或文件路径）
        workflow_data = load_json_arg(args.template_data)
    else:
        error_exit("请提供 template_data 参数或使用 --from-stdin")
    
    # 验证工作流数据
    if not workflow_data:
        error_exit("工作流数据为空")
    
    if "nodes" not in workflow_data:
        # 可能是 generate_workflow 的完整输出，尝试提取 template_data
        if "template_data" in workflow_data:
            workflow_data = workflow_data["template_data"]
        else:
            error_exit("工作流数据缺少 'nodes' 字段")
    
    # 应用参数修改
    if args.set_param:
        params = parse_set_params(args.set_param)
        workflow_data = apply_params_to_workflow(workflow_data, params)
        print(f"已应用 {len(args.set_param)} 个参数修改", file=sys.stderr)
    
    # 执行工作流
    print("正在提交工作流执行...", file=sys.stderr)
    resp = execute_workflow(workflow_data)
    
    if not resp.get("success"):
        error_msg = resp.get("message") or resp.get("error", "未知错误")
        error_code = resp.get("error_code", "")
        
        # 特殊处理积分不足
        if error_code == "INSUFFICIENT_POINTS":
            details = resp.get("details", {})
            required = details.get("required", 0)
            available = details.get("available", 0)
            print(f"\n⚠️  积分不足:", file=sys.stderr)
            print(f"   需要: {required} 点", file=sys.stderr)
            print(f"   可用: {available} 点", file=sys.stderr)
            print(f"   请充值后重试: https://voooai.com/subscription", file=sys.stderr)
        
        error_exit(f"执行失败: {error_msg}")
    
    # 提取执行信息
    execution_id = resp.get("execution_id") or resp.get("exec_id", "")
    status = resp.get("status", "pending")
    
    out = {
        "success": True,
        "execution_id": execution_id,
        "status": status,
        "message": "工作流已提交执行，请使用 get_status.py 查询进度",
    }
    
    # 如果响应中有额外信息
    if "estimated_time" in resp:
        out["estimated_time_seconds"] = resp["estimated_time"]
    
    if "points_consumed" in resp:
        out["points_consumed"] = resp["points_consumed"]
    
    json_output(out)


if __name__ == "__main__":
    main()
