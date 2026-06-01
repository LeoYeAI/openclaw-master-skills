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

def manage_emr_agent(action: str,
                     body: Dict[str, Any] = None):
    body = body or {}
    region = skill_cfg.region
    endpoint = semi_managed_region_endpoint_map.get(region, None)
    if not endpoint:
        raise ValueError(f"endpoint not found for region: {region}")
    result = request(service="emr", action=action,
                     version="2025-10-15", region=region,
                     endpoint=endpoint, method="POST",
                     query={}, body=body)
    logger.info(
        f"manage_emr_agent(action={action},region={region}, body={body}) => {result}")
    if not result.get("Result"):
        print(json.dumps(result.get("ResponseMetadata"), indent=2))
        return result.get("ResponseMetadata")
    print(json.dumps(result.get("Result"), ensure_ascii=False, indent=2))
    return result.get("Result")

def fix_args():
    args = sys.argv
    fix_args = []
    param_with_space = ""
    for arg in args:
        if arg.startswith("--"):
            if param_with_space:
                fix_args.append(param_with_space)
                param_with_space = ""
            fix_args.append(arg)
        else:
            param_with_space = param_with_space + arg
    if param_with_space:
        fix_args.append(param_with_space)
    sys.argv = fix_args

def _main():
    fix_args()
    parser = argparse.ArgumentParser(prog="emr_agent_manager.py")
    parser.add_argument("--action", required=True)
    parser.add_argument("--body", required=True)
    args = parser.parse_args()
    return manage_emr_agent(args.action, json.loads(args.body))

if __name__ == "__main__":
    _main()
