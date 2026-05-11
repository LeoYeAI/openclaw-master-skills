#!/usr/bin/env python3
"""
Pipeline 客户端核心模块
包含初始化、HTTP请求等核心功能
"""

import os
import sys
import json
import requests
from typing import Optional, Dict, Any


class PipelineClient:
    """流水线管理客户端"""

    def __init__(self, domain_account: Optional[str] = None, bff_url: Optional[str] = None):
        self.domain_account = domain_account or os.getenv('DEVOPS_DOMAIN_ACCOUNT')
        self.bff_url = bff_url or os.getenv('DEVOPS_BFF_URL')

        if not self.domain_account:
            raise ValueError("Domain account is required. Set DEVOPS_DOMAIN_ACCOUNT.")
        if not self.bff_url:
            raise ValueError("BFF URL is required. Set DEVOPS_BFF_URL environment variable.")

        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None,
                 params: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.bff_url}{endpoint}"

        headers = {
            'X-User-Account': self.domain_account
        }

        # 打印请求信息（调试用）
        print("\n" + "=" * 60)
        print(f"[Request] {method.upper()} {url}")
        print("-" * 60)
        print("Headers:")
        for k, v in headers.items():
            print(f"  {k}: {v}")
        if params:
            print("-" * 60)
            print(f"Query Params: {json.dumps(params, ensure_ascii=False)}")
        if data:
            print("-" * 60)
            print(f"Body: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print("=" * 60 + "\n")

        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            # 打印响应信息（调试用）
            print("=" * 60)
            print(f"[Response] Status: {response.status_code}")
            print("-" * 60)
            print("Response Headers:")
            for k, v in response.headers.items():
                print(f"  {k}: {v}")
            print("-" * 60)
            try:
                resp_json = response.json()
                print(f"Response Body:\n{json.dumps(resp_json, indent=2, ensure_ascii=False)}")
            except Exception:
                print(f"Response Body (text):\n{response.text}")
            print("=" * 60 + "\n")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}", file=sys.stderr)
            raise
