#!/usr/bin/env python3
"""单节点执行/重试：POST /api/node-builder/execute_single_node"""

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


def execute_single_node(workflow_data: dict, node_id: str) -> dict:
    """
    执行工作流中的单个节点
    
    Args:
        workflow_data: 工作流数据（template_data）
        node_id: 要执行的节点 ID
    
    Returns:
        执行结果，包含 execution_id
    """
    body = {
        "workflow": workflow_data,
        "node_id": node_id,
    }
    resp = api_post("/api/node-builder/execute_single_node", body, timeout=120)
    return resp


def main():
    parser = argparse.ArgumentParser(
        description="执行 VoooAI 工作流中的单个节点（用于调试或重试）",
        epilog="""
环境变量:
  VOOOAI_ACCESS_KEY  必填，Bearer 鉴权
  VOOOAI_BASE_URL    可选，默认 https://voooai.com

示例:
  # 执行指定节点
  python3 execute_single_node.py workflow.json --node-id node_1

  # 从 stdin 读取工作流
  cat workflow.json | python3 execute_single_node.py --from-stdin --node-id node_2

  # 修改参数后执行
  python3 execute_single_node.py workflow.json \\
    --node-id node_1 \\
    --set-param node_1.prompt="新的提示词"

  # 重试失败的节点
  python3 execute_single_node.py workflow.json --node-id failed_node_id

使用场景:
  - 调试：预览单个节点的输出
  - 重试：某个节点失败后单独重新执行
  - 测试：验证参数修改的效果

参数格式:
  --set-param node_id.param_name=value
  例如: --set-param node_1.prompt="测试提示词"
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
        "--node-id",
        required=True,
        help="要执行的节点 ID（必填）",
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
    
    # 验证节点 ID 存在
    node_ids = [n.get("id", "") for n in workflow_data.get("nodes", [])]
    if args.node_id not in node_ids:
        print(f"警告：节点 '{args.node_id}' 不在工作流中", file=sys.stderr)
        print(f"可用节点: {', '.join(node_ids)}", file=sys.stderr)
    
    # 应用参数修改
    if args.set_param:
        params = parse_set_params(args.set_param)
        workflow_data = apply_params_to_workflow(workflow_data, params)
        print(f"已应用 {len(args.set_param)} 个参数修改", file=sys.stderr)
    
    # 执行单节点
    print(f"正在执行节点: {args.node_id}...", file=sys.stderr)
    resp = execute_single_node(workflow_data, args.node_id)
    
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
        "node_id": args.node_id,
        "status": status,
        "message": f"节点 {args.node_id} 已提交执行，请使用 get_status.py 查询进度",
    }
    
    # 如果响应中有额外信息
    if "node_result" in resp:
        out["node_result"] = resp["node_result"]
    
    if "points_consumed" in resp:
        out["points_consumed"] = resp["points_consumed"]
    
    json_output(out)


if __name__ == "__main__":
    main()
