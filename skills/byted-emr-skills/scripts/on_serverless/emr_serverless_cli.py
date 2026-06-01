import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

root = Path(__file__).resolve().parents[2]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from scripts.client.volc_open_api_client import request
from scripts.on_serverless.emr_serverless_manager import manage_emr_serverless


def _parse_json(value: Optional[str]) -> Optional[Dict[str, Any]]:
    if value is None or value == "":
        return None
    return json.loads(value)


def _infer_service(action: str, service: Optional[str]) -> Optional[str]:
    if service:
        return service
    if action in [
        "CreateJobDefinition",
        "UpdateJobDefinition",
        "RunJobDefinition",
        "GetJobDefinition",
        "ListJobDefinitions",
    ]:
        return "emr"
    if action == "GetMetricData":
        return "cloudmonitor"
    if action == "CreateOrderInOneStep":
        return "las"
    return None


def _infer_version(action: str, version: Optional[str]) -> str:
    if version:
        return version
    if action in [
        "CreateJobDefinition",
        "UpdateJobDefinition",
        "RunJobDefinition",
        "GetJobDefinition",
        "ListJobDefinitions",
    ]:
        return "2024-06-13"
    if action == "GetMetricData":
        return "2018-01-01"
    if action == "CreateOrderInOneStep":
        return "2024-04-30"
    return "2024-03-25"



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service")
    parser.add_argument("--version")
    parser.add_argument("--action")
    parser.add_argument("--region", default=os.getenv("VOLCENGINE_REGION", "cn-beijing"))
    parser.add_argument("--method", default="POST")
    parser.add_argument("--query", default=None)
    parser.add_argument("--body", default=None)
    parser.add_argument("--endpoint", default=None)
    args = parser.parse_args()

    query = _parse_json(args.query)
    body = _parse_json(args.body)
    service = _infer_service(args.action, args.service)
    version = _infer_version(args.action, args.version)

    if args.endpoint:
        result = request(
            service=service,
            action=args.action,
            version=version,
            region=args.region,
            endpoint=args.endpoint,
            method=args.method,
            query=query or {},
            body=body,
        )
    else:
        result = manage_emr_serverless(
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
