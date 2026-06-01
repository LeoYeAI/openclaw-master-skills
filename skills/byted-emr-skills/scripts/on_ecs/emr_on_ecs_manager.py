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

import logging
from typing import Dict, Any

from scripts.client.volc_open_api_client import request
from scripts.config.config import semi_managed_region_endpoint_map, load_emr_skill_config

logger = logging.getLogger(__name__)

skill_cfg = load_emr_skill_config()


def manage_emr_on_ecs(service: str, action: str,
                      version: str, region: str,
                      method: str = "POST",
                      query: Dict[str, Any] = {},
                      body: Dict[str, Any] = None):
    if region is None:
        region = skill_cfg.region

    endpoint = semi_managed_region_endpoint_map.get(region, None)
    if service is None:
        service = "emr"
    if not endpoint:
        raise ValueError(f"endpoint not found for region: {region}")
    result = request(service=service, action=action,
                     version=version, region=region,
                     endpoint=endpoint, method=method,
                     query=query, body=body)
    logger.info(
        f"manage_emr_on_ecs(service={service}, action={action}, version={version}, region={region}, method={method}, query={query}, body={body}) => {result}")
    return result
