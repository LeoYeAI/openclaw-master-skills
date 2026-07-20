#!/usr/bin/env python3
"""
Ozon商品上传任务状态查询器
专门用于查询通过Ozon API上传商品的任务状态
"""

import os
import json
import sys
import requests
from typing import Dict, Any, Optional


class OzonTaskStatusChecker:
    def __init__(self, client_id: str, api_key: str):
        """
        初始化Ozon任务状态查询器

        Args:
            client_id: Ozon API Client ID
            api_key: Ozon API Key
        """
        self.client_id = client_id
        self.api_key = api_key
        self.base_url = "https://api-seller.ozon.ru"

    def create_headers(self) -> Dict[str, str]:
        """
        创建API请求头

        Returns:
            Dict[str, str]: 请求头字典
        """
        return {
            'Client-Id': self.client_id,
            'Api-Key': self.api_key,
            'Content-Type': 'application/json'
        }

    def check_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        查询任务状态

        Args:
            task_id: 任务ID

        Returns:
            Dict[str, Any]: 任务状态信息
        """
        url = f"{self.base_url}/v1/product/import/info"

        payload = {
            "task_id": task_id
        }

        try:
            response = requests.post(
                url,
                headers=self.create_headers(),
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result
            else:
                print(f"❌ 查询任务状态失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                return {"error": f"HTTP {response.status_code}"}

        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求错误: {e}")
            return {"error": str(e)}


def load_config() -> tuple:
    """从环境变量加载配置"""
    client_id = os.getenv('OZON_CLIENT_ID')
    api_key = os.getenv('OZON_API_KEY')

    if not client_id or not api_key:
        print("❌ 请设置环境变量 OZON_CLIENT_ID 和 OZON_API_KEY")
        sys.exit(1)

    return client_id, api_key


def main():
    """主函数"""
    print("🔍 Ozon任务状态查询器启动")

    # 检查命令行参数
    if len(sys.argv) != 2:
        print("❌ 用法: python check_status.py <task_id>")
        print("   或: echo '<task_id>' | python check_status.py")
        sys.exit(1)

    task_id = sys.argv[1].strip()

    if not task_id:
        print("❌ 任务ID不能为空")
        sys.exit(1)

    # 加载配置
    client_id, api_key = load_config()

    # 创建查询器实例
    checker = OzonTaskStatusChecker(client_id, api_key)

    # 查询任务状态
    print(f"⏳ 正在查询任务ID {task_id} 的状态...")
    status_info = checker.check_task_status(task_id)

    if "error" in status_info:
        print(f"❌ 任务状态查询失败: {status_info['error']}")
        sys.exit(1)

    # 输出结果
    print("✅ 任务状态查询成功:")
    print(json.dumps(status_info, indent=2, ensure_ascii=False))

    # 解析任务结果
    result = status_info.get('result', {})
    items = result.get('items', [])

    if items:
        print(f"\n📊 处理了 {len(items)} 个商品:")
        for i, item in enumerate(items, 1):
            offer_id = item.get('offer_id', 'N/A')
            product_id = item.get('product_id', 'N/A')
            errors = item.get('errors', [])

            if errors:
                print(f"  {i}. offer_id: {offer_id} - ❌ 失败")
                for error in errors:
                    print(f"      错误: {error}")
            else:
                print(f"  {i}. offer_id: {offer_id} - ✅ 成功 (商品ID: {product_id})")

    sys.exit(0)


if __name__ == "__main__":
    main()