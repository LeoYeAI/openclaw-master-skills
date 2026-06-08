#!/opt/anaconda3/bin/python3
"""
Khoj 知识库查询工具
"""

import argparse
import json
import sys
import os

try:
    import requests
except ImportError:
    print("错误: requests 未安装")
    print("请运行: pip install requests")
    sys.exit(1)


KHOJ_URL = os.environ.get("KHOJ_URL", "http://localhost:42110")
KHOJ_API_KEY = os.environ.get("KHOJ_API_KEY", "")


def search(query: str, top_k: int = 5):
    """搜索知识库"""
    headers = {}
    if KHOJ_API_KEY:
        headers["Authorization"] = f"Bearer {KHOJ_API_KEY}"
    
    try:
        response = requests.get(
            f"{KHOJ_URL}/api/search",
            params={"q": query, "n": top_k},
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到 Khoj 服务")
        print(f"请确认服务正在运行: {KHOJ_URL}")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"错误: {e}")
        sys.exit(1)


def chat(query: str):
    """对话查询"""
    headers = {}
    if KHOJ_API_KEY:
        headers["Authorization"] = f"Bearer {KHOJ_API_KEY}"
    
    try:
        response = requests.post(
            f"{KHOJ_URL}/api/chat",
            json={"q": query},
            headers=headers,
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到 Khoj 服务")
        print(f"请确认服务正在运行: {KHOJ_URL}")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"错误: {e}")
        sys.exit(1)


def format_search_results(results: list) -> str:
    """格式化搜索结果"""
    if not results:
        return "未找到相关内容"
    
    output = []
    for i, item in enumerate(results, 1):
        # 文件名在 additional.file 或 entry 第一行
        additional = item.get('additional', {})
        file_name = additional.get('file', '')
        if not file_name:
            # 从 entry 第一行提取
            content = item.get('entry', '')
            file_name = content.split('\n')[0] if content else '未知'
        output.append(f"\n[{i}] 文件: {file_name}")
        
        # 尝试提取位置信息（优先检测幻灯片标记）
        content = item.get('entry', '')
        import re
        
        # 先检查 PPT 幻灯片（更具体的标记）
        if '<!-- Slide number:' in content:
            match = re.search(r'<!-- Slide number: (\d+) -->', content)
            if match:
                output.append(f"    📍 幻灯片: 第 {match.group(1)} 页")
        # 再检查 Excel 工作表（确保是真正的表格内容）
        elif '## Sheet' in content and '|' in content:
            match = re.search(r'## (Sheet\d+)', content)
            if match:
                output.append(f"    📍 工作表: {match.group(1)}")
        
        # 显示内容片段
        snippet = content[:200].replace('\n', ' ').strip()
        output.append(f"    内容: {snippet}...")
    
    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Khoj 知识库查询工具"
    )
    parser.add_argument(
        "query",
        help="查询内容"
    )
    parser.add_argument(
        "-n", "--top-k",
        type=int,
        default=5,
        help="返回结果数量 (默认: 5)"
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="对话模式"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出 JSON 格式"
    )
    
    args = parser.parse_args()
    
    if args.chat:
        result = chat(args.query)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result.get("response", "无响应"))
    else:
        results = search(args.query, args.top_k)
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print(format_search_results(results))


if __name__ == "__main__":
    main()