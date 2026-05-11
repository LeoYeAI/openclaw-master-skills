#!/usr/bin/env python3
"""
流水线执行流程模块
包含 run_pipeline 方法的核心逻辑
"""

import os
from typing import Optional, Dict, Any, List

# 导入工具函数
from .utils import confirm

# 交互模式标志 - 从环境变量读取
def get_interactive_mode():
    return os.getenv('INTERACTIVE_MODE', 'true').lower() == 'true'


class RunPipelineMixin:
    """流水线执行流程混入类"""

    def run_pipeline(
        self,
        pipeline_id: str,
        branch: str = None,
        selected_tasks: List[str] = None,
        run_sources: List[Dict] = None,
        custom_parameters: List[Dict] = None,
        auto_fill_run_config: bool = False,
        re_run_flag: int = 0,
        from_pipeline_log_id: int = None,
        run_remark: str = None,
        task_data_list: List[Dict] = None,
        trigger_info: Dict = None,
        refs_type: str = "BRANCH"
    ) -> Dict[str, Any]:
        """
        手动执行流水线 - OpenAPI触发类型为2

        重要：执行流水线时必须参考 excute-pipeline-logic.md 文档进行 runSources 数据组装和映射：
        - 代码源转换：id, name, shortName, refsType, refsTypeValue, data{sourceType, repoType, branch, refsType, workPath}
        - 制品源转换：id, name, shortName, data{packageType, sourceType, repoType, workPath, imageName/defaultTag 等}
        - 数据顺序调整：按照原始 sources 的 workPath 顺序重排 runSources

        Args:
            pipeline_id: 流水线ID
            branch: 分支名称（可选，用于兼容旧版本）
            selected_tasks: 要执行的任务节点ID列表
            run_sources: 执行流水线源列表（代码源+制品源）
            custom_parameters: 自定义参数列表
            auto_fill_run_config: 是否自动填充上一次运行配置参数
            re_run_flag: 重新执行标志：0-否，1-是
            from_pipeline_log_id: 历史流水线执行记录ID（用于重新执行）
            run_remark: 执行备注
            task_data_list: 任务节点数据列表
            trigger_info: 触发信息
            refs_type: 引用类型（BRANCH/TAG）
        """
        data = {'pipelineId': pipeline_id}

        # 1. 获取流水线配置并组装 run_sources
        # 参考 excute-pipeline-logic.md 中的 doRun 函数逻辑
        # 无论是否传参，都需要组装 runSources
        config_result = self.get_pipeline_detail(pipeline_id)
        inner_code = config_result.get('data', {}).get('code')
        assembled_sources = []
        config_task_data_list = []
        config_trigger_info = None
        config_custom_parameters = []
        latest_selected_values = {}  # 存储最近执行记录

        if inner_code == 0 or inner_code == '0':
            config_data = config_result.get('data', {}).get('data', {})
            pipeline_info = config_data.get('pipeline', {})
            existing_sources = pipeline_info.get('sources', [])

            # 获取配置中的 taskDataList（必填字段）
            config_task_data_list = config_data.get('taskDataList', [])

            # 获取配置中的 triggerInfo
            config_trigger_info = pipeline_info.get('triggerInfo')

            # 获取配置中的自定义参数
            config_custom_parameters = pipeline_info.get('customParameters', [])

            # 用户直接提供了 run_sources
            if run_sources:
                assembled_sources = run_sources
            else:
                # 2. 查询最近执行记录，获取上次使用的分支/标签/版本
                # 参考 excute-pipeline-logic.md 中的 doGetRepoBranchList -> queryLastestSelectedValueByField
                code_source_params = []
                artifact_params = []

                for src in existing_sources:
                    src_data = src.get('data', {})
                    source_type = src_data.get('sourceType', 'code')

                    if source_type == 'code':
                        # 构建代码源查询参数
                        code_source_params.append({
                            "sourceType": "code",
                            "repoType": src_data.get('repoType', ''),
                            "repoUrl": src_data.get('repoUrl', ''),
                            "refsType": src_data.get('refsType', 'BRANCH'),
                            "workPath": src_data.get('workPath', ''),
                            "completeFilterFlag": False
                        })
                    elif source_type == 'package':
                        # 构建制品源查询参数
                        artifact_params.append({
                            "sourceType": "package",
                            "repoType": src_data.get('repoType', ''),
                            "packageType": src_data.get('packageType', 'DOCKER'),
                            "imageName": src_data.get('imageName', ''),
                            "normalArtifactName": src_data.get('normalArtifactName', ''),
                            "normalAddress": src_data.get('normalAddress', ''),
                            "workPath": src_data.get('workPath', ''),
                            "completeFilterFlag": False
                        })

                # 调用接口获取最近执行配置
                if code_source_params or artifact_params:
                    try:
                        latest_result = self.query_latest_selected_value(
                            pipeline_id,
                            code_source_params=code_source_params if code_source_params else None,
                            artifact_params=artifact_params if artifact_params else None
                        )
                        if latest_result.get('code') == 0 or latest_result.get('code') == '0':
                            latest_selected_values = latest_result.get('data', {})
                    except Exception as e:
                        print(f"Warning: Failed to query latest selected values: {e}")

                # 3. 从流水线配置中组装 runSources
                # 参考 excute-pipeline-logic.md 中的 runSources 转换逻辑

                # 交互模式：询问用户是否要交互式选择分支/标签/版本
                if get_interactive_mode() and not branch:
                    print(f"\n{'='*60}")
                    print("流水线执行配置")
                    print(f"{'='*60}")
                    print(f"发现 {len([s for s in existing_sources if s.get('data', {}).get('sourceType') == 'code'])} 个代码源")
                    print(f"发现 {len([s for s in existing_sources if s.get('data', {}).get('sourceType') == 'package'])} 个制品源")
                    print(f"{'='*60}")

                    use_interactive = confirm("\n是否交互式选择分支/标签/版本?", default=False)

                    if use_interactive:
                        # 使用交互式选择
                        assembled_sources = self._interactive_assemble_run_sources(
                            existing_sources=existing_sources,
                            latest_selected_values=latest_selected_values,
                            user_branch=branch,
                            user_refs_type=refs_type
                        )
                        # 按照原始 sources 的 workPath 顺序重排 runSources
                        assembled_sources = self._order_run_sources_by_original(
                            assembled_sources, existing_sources
                        )
                    else:
                        # 非交互式，使用最近执行记录自动填充
                        assembled_sources = self._auto_fill_run_sources(
                            existing_sources=existing_sources,
                            latest_selected_values=latest_selected_values,
                            user_branch=branch,
                            user_refs_type=refs_type
                        )
                        assembled_sources = self._order_run_sources_by_original(
                            assembled_sources, existing_sources
                        )
                else:
                    # 非交互模式，使用最近执行记录自动填充
                    assembled_sources = self._auto_fill_run_sources(
                        existing_sources=existing_sources,
                        latest_selected_values=latest_selected_values,
                        user_branch=branch,
                        user_refs_type=refs_type
                    )
                    assembled_sources = self._order_run_sources_by_original(
                        assembled_sources, existing_sources
                    )

        if assembled_sources:
            data['runSources'] = assembled_sources

        # 2. 任务节点（必填字段）
        if selected_tasks is not None:
            data['taskDataList'] = [
                {"id": task_id} for task_id in selected_tasks
            ]
        elif task_data_list is not None:
            data['taskDataList'] = task_data_list
        elif config_task_data_list:
            # 使用配置中的 taskDataList
            data['taskDataList'] = config_task_data_list

        # 3. 触发信息（从配置获取，设置 triggerType=2 表示 OpenAPI 触发）
        if trigger_info:
            data['triggerInfo'] = trigger_info
        elif config_trigger_info:
            trigger_info_copy = config_trigger_info.copy() if config_trigger_info else {}
            trigger_info_copy['triggerType'] = 2
            data['triggerInfo'] = trigger_info_copy
        else:
            data['triggerInfo'] = {'triggerType': 2, 'triggerParams': {}}

        # 4. 自定义参数
        if custom_parameters is not None:
            data['customParameterRuns'] = custom_parameters
        elif config_custom_parameters:
            data['customParameterRuns'] = config_custom_parameters

        # 5. 自动填充上次运行配置
        data['autoFillRunConfig'] = auto_fill_run_config

        # 6. 重新执行
        if re_run_flag:
            data['reRunFlag'] = re_run_flag

        if from_pipeline_log_id:
            data['fromPipelineLogId'] = from_pipeline_log_id

        # 7. 执行备注
        if run_remark:
            data['runRemark'] = run_remark

        return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/runByManual', data=data)
