#!/usr/bin/env python3
"""
模板和工作空间操作模块
包含流水线模板查询、工作空间查询等操作
"""

from typing import Dict, Any, List


class TemplateOpsMixin:
    """模板和工作空间操作混入类"""

    # ==================== 流水线模板 ====================

    def list_pipeline_templates(
        self,
        space_id: int,
        template_name: str = None,
        template_type: str = None,
        template_language: str = None,
        account: str = None,
        page_no: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        分页查询流水线模板

        接口: POST /rest/openapi/pipeline/queryPipelineTemplatePage

        Args:
            space_id: 工作空间ID（必填）
            template_name: 流水线模板名称（模糊搜索）
            template_type: 流水线模板类型
            template_language: 流水线模板语言（java/python/nodejs/go/dotnet/frontend/common）
            account: 当前登录账号
            page_no: 页码（默认1）
            page_size: 每页大小（默认10）

        Returns:
            {
                "code": 0,
                "message": "success",
                "data": {
                    "total": 总记录数,
                    "size": 每页大小,
                    "current": 当前页码,
                    "pages": 总页数,
                    "records": [PipTemplateVO列表]
                }
            }

        PipTemplateVO 字段:
            - id: 模板ID
            - pipelineTemplateName: 模板名称
            - pipelineTemplateLanguage: 模板语言
            - pipelineTemplateParams: 模板参数（JSON字符串）
            - pipelineTemplateType: 模板类型（Integer）
            - status: 状态（1-启用/0-禁用）
            - statusName: 状态名称
            - spaceId: 空间ID
            - description: 描述
            - createTime: 创建时间
            - updateTime: 更新时间
            - pipelineStageInfo: 流水线阶段信息（JSON字符串）
            - creator: 创建人（域账号）
            - updater: 更新人（域账号）
            - deleted: 删除标志
            - creatorName: 创建人中文名
            - updaterName: 更新人中文名
            - stages: 阶段列表
            - pipelineTemplatePermission: 操作权限列表
        """
        data = {
            'spaceId': space_id,
            'pageNo': page_no,
            'pageSize': page_size
        }
        if template_name:
            data['pipelineTemplateName'] = template_name
        if template_type:
            data['pipelineTemplateType'] = template_type
        if template_language:
            data['pipelineTemplateLanguage'] = template_language
        if account:
            data['account'] = account
        return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/queryPipelineTemplatePage', data=data)

    # ==================== 工作空间 ====================

    def query_workspace_page(
        self,
        workspace_name: str = None,
        pomp_project_code: str = None,
        division_name: str = None,
        team_name: str = None,
        division_id_list: List[str] = None,
        page_num: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        分页查询工作空间列表

        API: POST /api/ai-bff/rest/openapi/pipeline/queryWorkspacePage

        Args:
            workspace_name: 工作空间名称（模糊搜索）
            pomp_project_code: 项目编码
            division_name: 一级组织名称
            team_name: 产品线名称
            division_id_list: 一级组织ID集合
            page_num: 页码（默认1）
            page_size: 每页大小（默认10）

        Returns:
            {
                "total": 总记录数,
                "currentPage": 当前页码,
                "pageSize": 每页大小,
                "data": [工作空间列表]
            }
        """
        data = {
            "currentPage": page_num,
            "pageSize": page_size
        }
        if workspace_name:
            data["workSpaceName"] = workspace_name
        if pomp_project_code:
            data["pompProjectCode"] = pomp_project_code
        if division_name:
            data["divisionName"] = division_name
        if team_name:
            data["teamName"] = team_name
        if division_id_list:
            data["divisionIdList"] = division_id_list

        return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/queryWorkspacePage', data=data)
