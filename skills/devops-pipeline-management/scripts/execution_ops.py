#!/usr/bin/env python3
"""
流水线执行操作模块
包含流水线执行、取消、详情查询等操作
"""

import json
from typing import Optional, Dict, Any, List


class ExecutionOpsMixin:
    """流水线执行操作混入类"""

    # ==================== 流水线执行 ====================

    def query_latest_selected_value(
        self,
        pipeline_id: str,
        code_source_params: List[Dict] = None,
        artifact_params: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        查询最近流水线执行记录
        获取代码源和制品源的最近使用分支/标签/版本

        API: POST /api/ai-bff/rest/openapi/pipeline/queryLastestSelectedValueByField

        Args:
            pipeline_id: 流水线ID
            code_source_params: 代码源参数列表
            artifact_params: 制品源参数列表

        Returns:
            {
                "codeSourceResult": [...],  # 代码源最近执行结果
                "artifactResult": [...]     # 制品源最近执行结果
            }
        """
        data = {'pipelineId': pipeline_id}
        if code_source_params:
            data['codeSourceParams'] = code_source_params
        if artifact_params:
            data['artifactParams'] = artifact_params
        return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/queryLastestSelectedValueByField', data=data)

    def get_repo_branch_and_tag_list(
        self,
        repo_type: str,
        repo_url: str,
        refs_type: str = "BRANCH",
        search: str = None,
        page_num: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        批量获取分支和标签列表

        API: POST /api/ai-bff/rest/openapi/pipeline/getRepoBranchAndTagList

        Args:
            repo_type: 仓库类型 (GITLAB/GITHUB/GITEE/GIT/SVN)
            repo_url: 仓库地址
            refs_type: 引用类型 (BRANCH/TAG)
            search: 搜索关键词
            page_num: 页码
            page_size: 每页数量

        Returns:
            分支/标签列表
        """
        data = {
            "repoType": repo_type,
            "repoUrl": repo_url,
            "refsType": refs_type,
            "currentPage": page_num,
            "pageSize": page_size
        }
        if search:
            data["search"] = search

        # 批量查询需要传入列表
        return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/getRepoBranchAndTagList', data=[data])

    def get_repo_branch_and_tag_list_batch(
        self,
        source_list: List[Dict]
    ) -> Dict[str, Any]:
        """
        批量获取多个代码源的分支和标签列表

        API: POST /api/ai-bff/rest/openapi/pipeline/getRepoBranchAndTagList

        Args:
            source_list: 代码源列表，每个元素包含:
                - repoType: 仓库类型
                - repoUrl: 仓库地址
                - refsType: 引用类型 (BRANCH/TAG)
                - search: 搜索关键词（可选）
                - currentPage: 页码
                - pageSize: 每页数量

        Returns:
            分支/标签列表（按传入顺序返回）
        """
        data = []
        for src in source_list:
            item = {
                "repoType": src.get("repoType"),
                "repoUrl": src.get("repoUrl"),
                "refsType": src.get("refsType", "BRANCH"),
                "currentPage": src.get("currentPage", 1),
                "pageSize": src.get("pageSize", 20)
            }
            if src.get("search"):
                item["search"] = src.get("search")
            data.append(item)

        return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/getRepoBranchAndTagList', data=data)

    def query_commit_detail(
        self,
        repo_type: str,
        repo_url: str,
        commit_id: str
    ) -> Dict[str, Any]:
        """
        获取代码提交详情（用于标签）

        API: POST /api/ai-bff/rest/openapi/pipeline/queryCommitDetail

        Args:
            repo_type: 仓库类型
            repo_url: 仓库地址
            commit_id: 提交ID

        Returns:
            提交详情
        """
        data = {
            "repoType": repo_type,
            "repoUrl": repo_url,
            "commitId": commit_id
        }
        return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/queryCommitDetail', data=data)

    def query_repo_commit_list(
        self,
        repo_type: str,
        repo_url: str,
        refs_type_value: str,
        page_num: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取分支的提交列表

        API: POST /api/ai-bff/rest/openapi/pipeline/queryRepoCommitList

        Args:
            repo_type: 仓库类型
            repo_url: 仓库地址
            refs_type_value: 分支名称
            page_num: 页码
            page_size: 每页数量

        Returns:
            提交列表
        """
        data = {
            "repoType": repo_type,
            "repoUrl": repo_url,
            "refsTypeValue": refs_type_value,
            "currentPage": page_num,
            "pageSize": page_size
        }
        return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/queryRepoCommitList', data=data)

    def query_image_tags(
        self,
        repo_type: str,
        image_name: str,
        search: str = None,
        page_num: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        查询 Docker 镜像标签列表

        API: GET /api/ai-bff/rest/openapi/pipeline/imageTags

        Args:
            repo_type: 仓库类型 (HARBOR 等)
            image_name: 镜像名称
            search: 搜索关键词
            page_num: 页码
            page_size: 每页数量

        Returns:
            镜像标签列表
        """
        params = {
            "repoType": repo_type,
            "imageName": image_name,
            "currentPage": page_num,
            "pageSize": page_size
        }
        if search:
            params["search"] = search

        return self._request('GET', '/api/ai-bff/rest/openapi/pipeline/imageTags', params=params)

    def query_package_versions(
        self,
        repo_type: str,
        normal_artifact_name: str = None,
        full_path: str = None,
        search: str = None,
        page_num: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        查询普通制品版本列表

        API: GET /api/ai-bff/rest/openapi/pipeline/packageVersions

        Args:
            repo_type: 仓库类型 (NEXUS 等)
            normal_artifact_name: 制品名称
            full_path: 完整路径
            search: 搜索关键词
            page_num: 页码
            page_size: 每页数量

        Returns:
            制品版本列表
        """
        params = {
            "repoType": repo_type,
            "currentPage": page_num,
            "pageSize": page_size
        }
        if normal_artifact_name:
            params["normalArtifactName"] = normal_artifact_name
        if full_path:
            params["fullPath"] = full_path
        if search:
            params["search"] = search

        return self._request('GET', '/api/ai-bff/rest/openapi/pipeline/packageVersions', params=params)

    def get_pipeline_for_run(self, pipeline_id: str) -> Dict[str, Any]:
        """
        获取流水线执行前的配置信息（用于展示可选择的选项）
        使用编辑接口获取完整配置
        """
        params = {'pipelineId': pipeline_id}
        return self._request('GET', '/api/ai-bff/rest/openapi/pipeline/edit', params=params)

    def list_available_tasks(self, pipeline_id: str) -> List[Dict]:
        """
        获取流水线中可执行的任务节点列表
        """
        config = self.get_pipeline_for_run(pipeline_id)
        if config.get('code') == 0:
            stages = config.get('data', {}).get('stages', [])
            tasks = []
            for stage in stages:
                for step in stage.get('steps', []):
                    for task in step.get('tasks', []):
                        tasks.append(task)
            return tasks
        return []

    def list_available_sources(self, pipeline_id: str) -> List[Dict]:
        """
        获取流水线中可用的代码源列表
        """
        config = self.get_pipeline_for_run(pipeline_id)
        if config.get('code') == 0:
            return config.get('data', {}).get('sources', [])
        return []

    def list_custom_parameters(self, pipeline_id: str) -> List[Dict]:
        """
        获取流水线的自定义参数列表
        """
        config = self.get_pipeline_for_run(pipeline_id)
        if config.get('code') == 0:
            return config.get('data', {}).get('customParameters', [])
        return []

    def cancel_pipeline(self, pipeline_log_id: int) -> Dict[str, Any]:
        """
        取消正在执行的流水线

        Args:
            pipeline_log_id: 流水线执行记录ID（Long类型）
        """
        data = {'pipelineLogId': pipeline_log_id}
        return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/cancel', data=data)

    def get_run_detail(self, pipeline_log_id: int) -> Dict[str, Any]:
        """
        获取流水线执行详情

        Args:
            pipeline_log_id: 执行记录ID（Long类型）
        """
        params = {'pipelineLogId': pipeline_log_id}
        return self._request('GET', '/api/ai-bff/rest/openapi/pipeline/getPipelineWorkById', params=params)

    # ==================== Run Sources 辅助方法 ====================

    def _order_run_sources_by_original(
        self,
        run_sources: List[Dict],
        original_sources: List[Dict]
    ) -> List[Dict]:
        """
        按照原始 sources 的 workPath 顺序重排 runSources
        参考 excute-pipeline-logic.md 中的 handleRunSource 函数逻辑

        Args:
            run_sources: 转换后的 runSources 列表
            original_sources: 原始流水线配置中的 sources

        Returns:
            按照原始顺序重排后的 runSources
        """
        if not original_sources or not run_sources:
            return run_sources

        # 创建 workPath 到 runSource 的映射
        run_source_map = {}
        for source in run_sources:
            work_path = source.get('data', {}).get('workPath')
            if work_path:
                run_source_map[work_path] = source

        # 按照 original_sources 的原始顺序重新排列
        ordered = []
        for source in original_sources:
            work_path = source.get('data', {}).get('workPath')
            if work_path and work_path in run_source_map:
                ordered.append(run_source_map[work_path])

        return ordered

    def _auto_fill_run_sources(
        self,
        existing_sources: List[Dict],
        latest_selected_values: Dict = None,
        user_branch: str = None,
        user_refs_type: str = None
    ) -> List[Dict]:
        """
        自动填充 runSources 数据（使用最近执行记录或配置默认值）

        Args:
            existing_sources: 流水线配置中的 sources
            latest_selected_values: 最近执行记录
            user_branch: 用户指定的分支
            user_refs_type: 用户指定的引用类型

        Returns:
            组装好的 runSources 列表
        """
        assembled_sources = []

        for src in existing_sources:
            src_data = src.get('data', {})
            source_type = src_data.get('sourceType', 'code')

            if source_type == 'code':
                # 代码源转换
                # 优先使用用户指定的分支，其次从最近执行记录获取，最后使用配置默认值
                current_branch = user_branch if user_branch else src_data.get('branch', '')
                current_refs_type = user_refs_type if user_branch else src_data.get('refsType', 'BRANCH')

                # 从最近执行记录中查找对应的分支/标签
                if not user_branch and latest_selected_values and latest_selected_values.get('codeSourceResult'):
                    for code_result in latest_selected_values['codeSourceResult']:
                        code_param = code_result.get('codeSourceParam', {})
                        if (code_param.get('repoType') == src_data.get('repoType') and
                            code_param.get('repoUrl') == src_data.get('repoUrl') and
                            code_param.get('workPath') == src_data.get('workPath')):
                            if code_result.get('branchOrTag'):
                                current_branch = code_result.get('branchOrTag')
                            if code_result.get('lastestCodeSourceParam', {}).get('refsType'):
                                current_refs_type = code_result.get('lastestCodeSourceParam', {}).get('refsType')
                            break

                new_src = {
                    "id": src.get('id'),
                    "name": src.get('name'),
                    "shortName": src.get('name'),
                    "refsType": current_refs_type,
                    "refsTypeValue": current_branch,
                    "data": {
                        **src_data,
                        "branch": current_branch,
                        "refsType": current_refs_type
                    }
                }
                assembled_sources.append(new_src)

            elif source_type == 'package':
                # 制品源转换
                pkg_type = src_data.get('packageType', 'DOCKER')
                current_tag = src_data.get('defaultTag', '')

                # 从最近执行记录中查找对应的版本
                if latest_selected_values and latest_selected_values.get('artifactResult'):
                    for artifact_result in latest_selected_values['artifactResult']:
                        artifact_param = artifact_result.get('artifactParam', {})
                        if artifact_param.get('workPath') == src_data.get('workPath'):
                            if artifact_result.get('lastestArtifactVersion'):
                                current_tag = artifact_result.get('lastestArtifactVersion')
                            break

                pkg_src = {
                    "id": src.get('id'),
                    "name": src_data.get('imageName') or src_data.get('normalArtifactName'),
                    "shortName": src_data.get('imageName') or src_data.get('normalArtifactName'),
                    "data": {
                        **src_data,
                        "packageType": pkg_type,
                        "sourceType": "package",
                        "defaultTag": current_tag
                    }
                }
                assembled_sources.append(pkg_src)

        return assembled_sources
