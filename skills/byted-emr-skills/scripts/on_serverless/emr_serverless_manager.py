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
from scripts.config.config import semi_managed_region_endpoint_map, full_managed_region_endpoint_map, \
    cloud_monitor_endpoint_map, load_emr_skill_config

logger = logging.getLogger(__name__)

skill_cfg = load_emr_skill_config()

def manage_emr_serverless(service: str, action: str,
                          version: str, region: str,
                          method: str = "POST",
                          query: Dict[str, Any] = {},
                          body: Dict[str, Any] = None):
    if region is None:
        region = skill_cfg.region

    endpoint = full_managed_region_endpoint_map.get(region, None)
    if service is None:
        service = "emr_serverless"
    if action in ["CreateJobDefinition", "UpdateJobDefinition", "RunJobDefinition", "GetJobDefinition",
                  "ListJobDefinitions"]:
        service = "emr"
        endpoint = semi_managed_region_endpoint_map.get(region, None)
    elif action in ["GetMetricData"]:
        service = "cloudmonitor"
        endpoint = cloud_monitor_endpoint_map.get(region, None)
    if not endpoint:
        raise ValueError(f"endpoint not found for region: {region}")
    result = request(service=service, action=action,
                     version=version, region=region,
                     endpoint=endpoint, method=method,
                     query=query, body=body)
    logger.info(
        f"manage_emr_serverless(service={service}, action={action}, version={version}, region={region}, method={method}, query={query}, body={body}) => {result}")
    return result


# if __name__ == "__main__":
#     # result1 = manage_emr_serverless(
#     #     service="emr_serverless",
#     #     action="ListQueue",
#     #     version="2024-03-25",
#     #     region="cn-beijing",
#     #     method="GET",
#     #     query={
#     #     }
#     # )
#     # print(result1)
#
#     # result2 = manage_emr_serverless(
#     #     service="emr",
#     #     action="CreateJobDefinition",
#     #     version="2024-06-13",
#     #     region="cn-beijing",
#     #     method="POST",
#     #     query={
#     #     },
#     #     body={
#     #     "JobDefinitionName": "liubin_test123",
#     #     "JobType": "PySpark",
#     #     "ResourceType": "EMR_SERVERLESS",
#     #     "Conf": {},
#     #     "ResourceId": "1238543785583968256-0",
#     #     "ResourceName": "公共队列-Default",
#     #     "DevelopMode": "UI",
#     #     "JobDefinitionContent": {
#     #         "Jars": [],
#     #         "PyFiles": [],
#     #         "Files": [],
#     #         "Archives": [],
#     #         "MainApplicationFile": "tos://amoro-lance-test/archive/",
#     #         "StorageMounts": [],
#     #         "JobType": "PySpark",
#     #         "UseExistingRayCluster": False,
#     #         "Volumes": [],
#     #         "VolumeMounts": []
#     #     },
#     #     "ProjectName": "default",
#     #     "UserLocale": "zh"
#     # })
#     #
#     # print(result2)
#
#     # result3 = manage_emr_serverless(
#     #     service="emr",
#     #     action="ListJobDefinitions",
#     #     version="2024-06-13",
#     #     region="cn-beijing",
#     #     method="POST",
#     #     body={
#     #
#     #     }
#     # )
#     # print(result3)
#
#     # result4 = manage_emr_serverless(
#     #     service="cloudmonitor",
#     #     action="GetMetricsData",
#     #     version="2018-01-01",
#     #     region="cn-beijing",
#     #     method="POST",
#     #     body={
#     #         "MetricNames": [
#     #             "QueueMemoryUsageRate"
#     #         ],
#     #         "StartTime": 1773557406,
#     #         "EndTime": 1773643806,
#     #         "Namespace": "VCM_EMR_Serverless",
#     #         "Instances": [
#     #             {
#     #                 "Dimensions": [
#     #                     {
#     #                         "Name": "ResourceID",
#     #                         "Value": "1481966638772256768"
#     #                     }
#     #                 ],
#     #                 "Metadata": []
#     #             }
#     #         ],
#     #         "GroupBy": [
#     #             "ResourceID"
#     #         ],
#     #         "SubNamespace": "Queue",
#     #         "Region": "cn-beijing"
#     #     }
#     # )
#     # print(result4)
#
#     result5 = manage_emr_serverless(
#         service="emr_serverless",
#         action="ListTagQueue",
#         version="2024-03-25",
#         region="cn-beijing",
#         method="POST",
#         body={
#         "ProjectName": "default",
#         "Project": "default",
#         "QueueName": "",
#         "Limit": 1000,
#         "VolcTags": []
#     })
#     print(result5)
