#!/usr/bin/env python3
"""
流水线操作模块
包含流水线的创建、查询、更新、删除等CRUD操作
"""

from typing import Optional, Dict, Any, List


class PipelineOpsMixin:
    """流水线CRUD操作混入类"""

    # ==================== 流水线CRUD ====================

    def get_pipeline_list(self, pipeline_id: str, page_num: int = 1, page_size: int = 10,
                          search_type: str = None, keyword: str = None) -> Dict[str, Any]:
        """
        分页查询流水线执行记录

        Args:
            pipeline_id: 流水线ID（必填）
            page_num: 页码
            page_size: 每页大小
            search_type: 搜索数据类型
            keyword: 搜索关键字
        """
        params = {'pipelineId': pipeline_id, 'pageNum': page_num, 'pageSize': page_size}
        if search_type:
            params['type'] = search_type
        if keyword:
            params['keyword'] = keyword
        return self._request('GET', '/api/ai-bff/rest/openapi/pipeline/queryPipelineWorkPage', params=params)

    def get_pipeline_detail(self, pipeline_id: str) -> Dict[str, Any]:
        """获取流水线详情（编辑时获取配置参数）

        接口: GET /rest/openapi/pipeline/edit?pipelineId={pipeline_id}
        """
        params = {'pipelineId': pipeline_id}
        return self._request('GET', '/api/ai-bff/rest/openapi/pipeline/edit', params=params)

    def save_pipeline(self, pipeline_data: Dict, task_data_list: List[Dict] = None) -> Dict[str, Any]:
        """
        保存流水线（创建/编辑）

        Args:
            pipeline_data: 流水线编排内容（PipelineParams）
            task_data_list: 流水线任务的参数

        Note:
            新建流水线时必须包含以下字段：
            - pipelineId: 由 skill 生成 UUID (新建时) 或 实际ID (编辑时)
            - aliasId: 流水线别名ID (可选，后端会自动生成)
            - name: 流水线名称 (必填)
            - spaceId: 空间ID (必填)
            - pipelineKey: 流水线Key (必填)
        """
        # 确保pipelineId字段存在，新建时必须由 skill 生成 UUID
        if 'pipelineId' not in pipeline_data or not pipeline_data['pipelineId']:
            import uuid
            pipeline_data['pipelineId'] = str(uuid.uuid4())

        data = {'pipeline': pipeline_data}
        if task_data_list:
            data['taskDataList'] = task_data_list
        return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/save', data=data)

    def create_pipeline(self, name: str, space_id: int, config: Dict = None) -> Dict[str, Any]:
        """
        创建流水线（简化版）

        Args:
            name: 流水线名称
            space_id: 空间ID（Long类型）
            config: 流水线配置（包含sources、stages等）

        Note:
            会自动生成 pipelineId(UUID)、aliasId、pipelineKey 等必填字段
        """
        import time
        import uuid

        timestamp = int(time.time())

        pipeline_data = {
            'pipelineId': str(uuid.uuid4()),  # 新建时由 skill 生成 UUID
            'name': name,
            'spaceId': space_id,
            'pipelineKey': f'pipeline-{timestamp}',
            'aliasId': f'{uuid.uuid4().hex[:16]}',  # 生成16位aliasId
            'buildPlatform': 'linux',
            'timeoutDuration': '2H'
        }

        if config:
            # 合并配置，但保留必填字段
            for key, value in config.items():
                if key not in ['pipelineId']:  # 不覆盖pipelineId
                    pipeline_data[key] = value

        return self.save_pipeline(pipeline_data)

    def update_pipeline(self, pipeline_id: str, config: Dict = None) -> Dict[str, Any]:
        """
        更新/编辑流水线

        Args:
            pipeline_id: 流水线ID（必填）
            config: 流水线配置（包含name、sources、stages等）
        """
        if not pipeline_id:
            return {'code': -1, 'message': 'pipeline_id不能为空'}

        pipeline_data = {'pipelineId': pipeline_id}
        if config:
            # 确保包含name和spaceId
            if 'name' not in config:
                return {'code': -1, 'message': '更新配置中必须包含name字段'}
            if 'spaceId' not in config:
                return {'code': -1, 'message': '更新配置中必须包含spaceId字段'}
            pipeline_data.update(config)
        else:
            return {'code': -1, 'message': '更新配置不能为空'}

        return self.save_pipeline(pipeline_data)

    def delete_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """
        删除流水线

        接口: POST /pipeline/delete?pipelineId={pipelineId}
        """
        return self._request('POST', f'/api/ai-bff/rest/openapi/pipeline/delete?pipelineId={pipeline_id}')

    # ==================== 流水线列表 ====================

    def list_pipelines(
        self,
        space_id: int,
        pipeline_name: str = None,
        query_flag: int = 0,
        page_num: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        分页查询流水线列表

        接口: POST /pipeline/queryPipelinePage

        Args:
            space_id: 工作空间ID（必填）
            pipeline_name: 流水线名称（模糊搜索）
            query_flag: 查询标识（0-全部/1-我收藏的/2-我创建的/3-最后一次由我执行的）
            page_num: 页码
            page_size: 每页大小
        """
        data = {
            'spaceId': space_id,
            'queryFlag': query_flag,
            'pageNum': page_num,
            'pageSize': page_size
        }
        if pipeline_name:
            data['pipelineName'] = pipeline_name
        return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/queryPipelinePage', data=data)

    # ==================== 新增 API ====================

    def get_jenkins_console_log(self, pipeline_log_id: int) -> Dict[str, Any]:
        """
        查询流水线控制台日志

        接口: GET /rest/openapi/pipeline/getJenkinsConsoleLog?pipelineLogId={pipelineLogId}

        Args:
            pipeline_log_id: 执行记录ID（必填）

        Returns:
            {
                "code": 0,
                "data": {
                    "logContent": "[INFO] Build started...",
                    "hasMore": true,
                    "nextStart": 1024,
                    "isCompleted": false
                }
            }
        """
        params = {'pipelineLogId': pipeline_log_id}
        return self._request('GET', '/api/ai-bff/rest/openapi/pipeline/getJenkinsConsoleLog', params=params)

    def get_pipeline_template(self, template_id: str) -> Dict[str, Any]:
        """
        查询单个流水线模板详情

        接口: GET /rest/openapi/pipeline/getPipTemplateById?id={id}

        Args:
            template_id: 流水线模板ID（必填）

        Returns:
            {
                "code": 0,
                "data": {
                    "id": "template_123456",
                    "templateName": "Java构建模板",
                    "templateType": "java",
                    "description": "Java项目标准构建模板",
                    "stages": [...],
                    "createTime": "2025-01-10T08:00:00",
                    "updateTime": "2025-01-15T10:00:00"
                }
            }
        """
        params = {'id': template_id}
        return self._request('GET', '/api/ai-bff/rest/openapi/pipeline/getPipTemplateById', params=params)

    def save_pipeline_template(
        self,
        template_name: str,
        template_type: str,
        stages: List[Dict],
        template_id: str = None,
        description: str = None,
        task_data_list: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        保存流水线模板（创建/编辑）

        接口: POST /rest/openapi/pipeline/savePipTemplate

        Args:
            template_name: 模板名称（必填）
            template_type: 模板类型（必填）
            stages: 阶段配置列表（必填）
            template_id: 模板ID（为空则新建，编辑时必填）
            description: 模板描述
            task_data_list: 任务参数列表（用于主机部署配置）

        Returns:
            {
                "code": 0,
                "data": "template_123456"  # 保存的模板ID
            }
        """
        data = {
            'templateName': template_name,
            'templateType': template_type,
            'stages': stages
        }
        if template_id:
            data['id'] = template_id
        if description:
            data['description'] = description
        if task_data_list:
            data['taskDataList'] = task_data_list
        return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/savePipTemplate', data=data)

    def check_repo_token(self, repo_type_list: List[str]) -> Dict[str, Any]:
        """
        查询仓库token配置状态

        接口: POST /rest/openapi/pipeline/checkRepoTokenByRepoTypeList

        Args:
            repo_type_list: 仓库类型列表（必填），如 ["gitlab", "github", "gitee"]

        Returns:
            {
                "code": 0,
                "data": {
                    "gitlab": true,
                    "github": false,
                    "gitee": true
                }
            }
        """
        data = {'repoTypeList': repo_type_list}
        return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/checkRepoTokenByRepoTypeList', data=data)

    def get_pipeline_by_id(self, pipeline_id: str) -> Dict[str, Any]:
        """
        查询流水线基本信息

        接口: GET /rest/openapi/pipeline/queryPipelineById?pipelineId={pipelineId}

        Args:
            pipeline_id: 流水线ID（必填）

        Returns:
            PipelineTemplateVO 流水线基本信息，包含：
            - id, pipelineName, pipelineKey, pipelineAliasId
            - pipelineLabel, label, pipelineParams
            - spaceId, createTime, updateTime
            - creator, creatorName, updater, updaterName
            - store, permissionList
            - pipelineOwner, pipelineOwnerName
            - buildNumber, buildNumberHasUsed
            - latestPipWorkVO (最近执行记录)
        """
        params = {'pipelineId': pipeline_id}
        return self._request('GET', '/api/ai-bff/rest/openapi/pipeline/queryPipelineById', params=params)

    def get_image_tags(
        self,
        image_name: str,
        tag: str = None,
        page_no: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        获取镜像tag列表

        接口: GET /rest/openapi/pipeline/imageTags

        Args:
            image_name: 镜像名称（必填）
            tag: 标签名（过滤用）
            page_no: 页码（默认1）
            page_size: 每页大小（默认10）

        Returns:
            {
                "code": 0,
                "data": {
                    "total": 50,
                    "currentPage": 1,
                    "pageSize": 10,
                    "records": ["v1.0.0", "v1.0.1", "latest"]
                }
            }
        """
        params = {'imageName': image_name, 'pageNo': page_no, 'pageSize': page_size}
        if tag:
            params['tag'] = tag
        return self._request('GET', '/api/ai-bff/rest/openapi/pipeline/imageTags', params=params)

    def get_package_versions(
        self,
        repo: str,
        package_path: str,
        package_name: str
    ) -> Dict[str, Any]:
        """
        获取包版本列表

        接口: GET /rest/openapi/pipeline/packageVersions

        Args:
            repo: 仓库名称（必填）
            package_path: 包路径（必填）
            package_name: 包名称（必填）

        Returns:
            {
                "code": 0,
                "data": ["2.0.0", "1.1.0", "1.0.1", "1.0.0"]
            }
        """
        params = {
            'repo': repo,
            'packagePath': package_path,
            'packageName': package_name
        }
        return self._request('GET', '/api/ai-bff/rest/openapi/pipeline/packageVersions', params=params)

    def query_workspaces(
        self,
        workspace_name: str = None,
        division_name: str = None,
        team_name: str = None,
        division_id_list: List[str] = None,
        pomp_project_code: str = None,
        current_page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        分页查询工作空间

        接口: POST /rest/openapi/pipeline/queryWorkspacePage

        Args:
            workspace_name: 工作空间名称（模糊搜索）
            division_name: 一级组织名称
            team_name: 产品线名称
            division_id_list: 一级组织ID集合
            pomp_project_code: 项目编码
            current_page: 页码（默认1）
            page_size: 每页大小（默认10）

        Returns:
            PageResult<WorkSpaceVO> 工作空间分页列表
        """
        data = {
            'currentPage': current_page,
            'pageSize': page_size
        }
        if workspace_name:
            data['workSpaceName'] = workspace_name
        if division_name:
            data['divisionName'] = division_name
        if team_name:
            data['teamName'] = team_name
        if division_id_list:
            data['divisionIdList'] = division_id_list
        if pomp_project_code:
            data['pompProjectCode'] = pomp_project_code
        return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/queryWorkspacePage', data=data)

    def query_repo_list(
        self,
        repo_type: str,
        search: str = None,
        current_page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        分页查询代码仓库

        接口: POST /rest/openapi/pipeline/queryRepoList

        Args:
            repo_type: 仓库类型（必填）
            search: 搜索关键字（仓库名称模糊搜索）
            current_page: 页码（默认1）
            page_size: 每页大小（默认10）

        Returns:
            RepoVOPage 代码仓库分页列表
        """
        data = {
            'repoType': repo_type,
            'currentPage': current_page,
            'pageSize': page_size
        }
        if search:
            data['search'] = search
        return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/queryRepoList', data=data)

    def query_repo_branch_list(
        self,
        repo_type: str,
        repo_url: str,
        search: str = None,
        current_page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        分页获取分支列表

        接口: POST /rest/openapi/pipeline/queryRepoBranchList

        Args:
            repo_type: 仓库类型（必填）
            repo_url: 仓库地址（必填）
            search: 搜索关键字（分支名称模糊搜索）
            current_page: 页码（默认1）
            page_size: 每页大小（默认10）

        Returns:
            BranchListVO 分支列表分页数据
        """
        data = {
            'repoType': repo_type,
            'repoUrl': repo_url,
            'currentPage': current_page,
            'pageSize': page_size
        }
        if search:
            data['search'] = search
        return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/queryRepoBranchList', data=data)
