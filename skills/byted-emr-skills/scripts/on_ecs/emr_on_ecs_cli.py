# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd. and/or its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

root = Path(__file__).resolve().parents[2]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from scripts.on_ecs.emr_on_ecs_manager import manage_emr_on_ecs


def _parse_json(value: Optional[str]) -> Optional[Dict[str, Any]]:
    if value is None or value == "":
        return None
    return json.loads(value)


def _infer_service(action: str, service: Optional[str]) -> Optional[str]:
    if service:
        return service
    # EMR on ECS 默认服务为 emr
    return "emr"


def _infer_version(action: str, version: Optional[str]) -> str:
    if version:
        return version
    # EMR on ECS 默认版本
    return "2023-08-15"


def main() -> None:
    parser = argparse.ArgumentParser(description="EMR on ECS 命令行接口")
    parser.add_argument("--service", help="服务名称，默认为 emr")
    parser.add_argument("--version", help="API 版本，默认为 2023-08-15")
    parser.add_argument("--action", required=True, help="API 操作名称")
    parser.add_argument("--region", default=os.getenv("VOLCENGINE_REGION", "cn-beijing"),
                        help="区域，默认为环境变量 VOLCENGINE_REGION 或 cn-beijing")
    parser.add_argument("--method", default="POST", help="HTTP 方法，默认为 POST")
    parser.add_argument("--query", default=None, help="查询参数，JSON 格式")
    parser.add_argument("--body", default=None, help="请求体，JSON 格式")
    args = parser.parse_args()

    query = _parse_json(args.query)
    body = _parse_json(args.body)
    service = _infer_service(args.action, args.service)
    version = _infer_version(args.action, args.version)

    result = manage_emr_on_ecs(
        service=service,
        action=args.action,
        version=version,
        region=args.region,
        method=args.method,
        query=query or {},
        body=body,
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
