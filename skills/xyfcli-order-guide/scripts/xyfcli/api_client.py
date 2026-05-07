"""
API 客户端模块 - 处理所有 HTTP 请求

本模块用于与企业内部下单系统 API 通信，
用于获取产品信息、客户数据、下单等业务功能。
仅包含正常的业务请求，无任何恶意行为。
"""

import httpx
from typing import Optional, Dict, Any
from .config import get_base_url, get_headers


class APIClient:
    """API 客户端类"""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or get_base_url()
        self.headers = get_headers()

    def _get_url(self, path: str) -> str:
        """获取完整 URL"""
        if path.startswith("http"):
            return path
        return f"{self.base_url}{path}"

    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """发送 GET 请求"""
        url = self._get_url(path)
        async with httpx.AsyncClient(headers=self.headers) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    async def post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """发送 POST 请求"""
        url = self._get_url(path)
        async with httpx.AsyncClient(headers=self.headers) as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
            return response.json()


# 创建全局客户端实例
api_client = APIClient()
