#!/usr/bin/env python3
"""查询执行状态：GET /api/node-builder/execution/{execution_id}（支持轮询）"""

import argparse
import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))
from _common import api_get, json_output, error_exit, PLATFORM_URL

# 轮询配置
DEFAULT_POLL_INTERVAL = 10  # 秒
DEFAULT_TIMEOUT = 300  # 5 分钟


def get_execution_status(execution_id: str) -> dict:
    """
    查询执行状态
    
    Args:
        execution_id: 执行 ID
    
    Returns:
        执行状态字典
    """
    resp = api_get(f"/api/node-builder/execution/{execution_id}")
    return resp


def poll_until_complete(
    execution_id: str,
    timeout: int = DEFAULT_TIMEOUT,
    interval: int = DEFAULT_POLL_INTERVAL,
) -> dict:
    """
    轮询直到执行完成或超时
    
    Args:
        execution_id: 执行 ID
        timeout: 超时秒数
        interval: 轮询间隔秒数
    
    Returns:
        最终状态字典
    """
    start_time = time.time()
    last_progress = -1
    
    while True:
        elapsed = time.time() - start_time
        
        # 超时检查
        if elapsed > timeout:
            return {
                "success": False,
                "status": "timeout",
                "message": f"轮询超时（{timeout}秒），任务可能仍在执行中",
                "execution_id": execution_id,
                "platform_url": f"{PLATFORM_URL}",
            }
        
        # 查询状态
        resp = get_execution_status(execution_id)
        
        if not resp.get("success"):
            # API 错误，重试
            time.sleep(interval)
            continue
        
        status = resp.get("status", "unknown")
        progress = resp.get("progress", 0)
        
        # 显示进度（如果有变化）
        if progress != last_progress:
            print(f"[{int(elapsed)}s] 状态: {status}, 进度: {progress}%", file=sys.stderr)
            last_progress = progress
        
        # 检查完成状态
        if status == "completed":
            return resp
        
        if status == "failed":
            return resp
        
        if status in ("cancelled", "canceled"):
            return resp
        
        # 继续等待
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(
        description="查询 VoooAI 工作流执行状态",
        epilog="""
环境变量:
  VOOOAI_ACCESS_KEY  必填，Bearer 鉴权
  VOOOAI_BASE_URL    可选，默认 https://voooai.com

示例:
  # 单次查询
  python3 get_status.py exec_abc123

  # 轮询直到完成
  python3 get_status.py exec_abc123 --poll

  # 自定义轮询参数
  python3 get_status.py exec_abc123 --poll --timeout 600 --interval 15

  # 与 execute_workflow 配合使用
  EXEC_ID=$(python3 execute_workflow.py workflow.json | jq -r '.execution_id')
  python3 get_status.py $EXEC_ID --poll

轮询模式:
  - 每 10 秒（默认）查询一次状态
  - 状态变为 completed/failed 时停止
  - 超时（默认 5 分钟）后停止并提示手动查看

状态说明:
  - pending: 等待执行
  - running: 正在执行
  - completed: 执行完成
  - failed: 执行失败
  - cancelled: 已取消
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "execution_id",
        help="执行 ID（由 execute_workflow 返回）",
    )
    parser.add_argument(
        "--poll",
        action="store_true",
        help="启用轮询模式，直到完成或超时",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"轮询超时秒数（默认 {DEFAULT_TIMEOUT} 秒）",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=DEFAULT_POLL_INTERVAL,
        help=f"轮询间隔秒数（默认 {DEFAULT_POLL_INTERVAL} 秒）",
    )
    args = parser.parse_args()

    execution_id = args.execution_id.strip()
    if not execution_id:
        error_exit("execution_id 不能为空")
    
    if args.poll:
        # 轮询模式
        print(f"开始轮询执行状态: {execution_id}", file=sys.stderr)
        print(f"超时: {args.timeout}秒, 间隔: {args.interval}秒", file=sys.stderr)
        print("按 Ctrl+C 中断轮询", file=sys.stderr)
        print("", file=sys.stderr)
        
        try:
            resp = poll_until_complete(
                execution_id,
                timeout=args.timeout,
                interval=args.interval,
            )
        except KeyboardInterrupt:
            print("\n轮询已中断", file=sys.stderr)
            resp = get_execution_status(execution_id)
    else:
        # 单次查询
        resp = get_execution_status(execution_id)
    
    if not resp.get("success"):
        error_msg = resp.get("message") or resp.get("error", "查询失败")
        error_exit(error_msg)
    
    # 构建输出
    status = resp.get("status", "unknown")
    progress = resp.get("progress", 0)
    
    out = {
        "success": True,
        "execution_id": execution_id,
        "status": status,
        "progress": progress,
    }
    
    # 如果完成，提取结果 URL
    if status == "completed":
        outputs = resp.get("outputs", {})
        result_urls = []
        
        for node_id, output_data in outputs.items():
            if isinstance(output_data, dict):
                url = output_data.get("url") or output_data.get("result_url", "")
                output_type = output_data.get("type", "unknown")
                if url:
                    result_urls.append({
                        "node_id": node_id,
                        "type": output_type,
                        "url": url,
                    })
            elif isinstance(output_data, list):
                for item in output_data:
                    if isinstance(item, dict):
                        url = item.get("url") or item.get("result_url", "")
                        if url:
                            result_urls.append({
                                "node_id": node_id,
                                "type": item.get("type", "unknown"),
                                "url": url,
                            })
        
        out["result_urls"] = result_urls
        out["total_results"] = len(result_urls)
    
    # 如果失败，包含错误信息
    if status == "failed":
        out["error_message"] = resp.get("error") or resp.get("message", "执行失败")
        out["failed_nodes"] = resp.get("failed_nodes", [])
    
    # 包含节点状态（如果有）
    if "nodes" in resp:
        node_statuses = {}
        for node in resp["nodes"]:
            node_id = node.get("id", "")
            node_statuses[node_id] = {
                "status": node.get("status", "unknown"),
                "progress": node.get("progress", 0),
            }
        out["node_statuses"] = node_statuses
    
    # 如果超时，添加提示
    if status == "timeout":
        out["hint"] = f"任务可能仍在执行中，请稍后在 {PLATFORM_URL} 查看结果"
    
    json_output(out)


if __name__ == "__main__":
    main()
