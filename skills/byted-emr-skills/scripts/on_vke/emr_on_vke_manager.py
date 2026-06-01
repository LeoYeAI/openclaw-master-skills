import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))  # 添加父目录
import argparse
import logging
from typing import Dict, Any

from scripts.client.volc_open_api_client import request
from scripts.config.config import semi_managed_region_endpoint_map, load_emr_skill_config

logger = logging.getLogger(__name__)

skill_cfg = load_emr_skill_config()

def request_body_convert(action, body: Dict[str, Any]) -> Dict[str, Any]:
    if not body:
        return {}
    # 默认返回100条结果
    if not body.get("MaxResults"):
        body["MaxResults"] = 100

    match action:
        case "ListOperations":
            body["ClusterIds"] = [body.get("ClusterId")]
        case _: pass
    return body

def response_convert(action, response: Dict[str, Any]) -> Any:
    if not response:
        return {}
    match action:
        case "ListConfigs":
            return [
                {
                    "ComponentName": item.get("ComponentName"),
                    "ConfigFileName":item.get("FileName"),
                    "ConfigItemKey":item.get("ConfigKey"),
                    "ConfigItemValue":item.get("ConfigValue"),
                    "Effective":item.get("Effective"),
                } for item in response["Items"]]
        case _: return response


def emr_on_vke_manager(action: str,
                     body: Dict[str, Any] = None):
    body = request_body_convert(action, body)
    region = skill_cfg.region
    endpoint = semi_managed_region_endpoint_map.get(region, None)
    if not endpoint:
        raise ValueError(f"endpoint not found for region: {region}")
    result = request(
        service="emr",
        action=action,
        version="2024-06-13",
        region=region,
        endpoint=endpoint,
        method="POST",
        query={},
        body=body
    )
    logger.info(
        f"emr_on_vke_manager(action={action},region={region}, body={body}) => {result}")

    if not result.get("Result"):
        print(json.dumps(result.get("ResponseMetadata"), indent=2))
        return result.get("ResponseMetadata")
    res = response_convert(action, result.get("Result"))
    print(json.dumps(res, ensure_ascii=False))
    return res

def _main():
    parser = argparse.ArgumentParser(prog="emr_on_vke_manager.py")
    parser.add_argument("--action", required=True)
    parser.add_argument("--body", required=False)
    args = parser.parse_args()
    return emr_on_vke_manager(args.action, json.loads(args.body or "{}"))

if __name__ == "__main__":
    _main()
