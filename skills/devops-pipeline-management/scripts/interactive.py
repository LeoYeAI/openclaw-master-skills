#!/usr/bin/env python3
"""
交互式操作模块
包含交互式创建、更新、执行流水线等操作
"""

import json
import time
import re
from typing import Optional, Dict, Any, List

# 从顶层导入，避免循环导入
from .utils import prompt_choice, prompt_input, confirm


class InteractiveOpsMixin:
    """交互式操作混入类"""

    # ==================== 辅助方法 ====================

    def _get_trigger_text(self, trigger_info: Dict) -> str:
        """获取触发方式的文本描述"""
        if not trigger_info:
            return "手动触发"
        trigger_type = trigger_info.get('triggerType')
        if trigger_type == 0:
            return "手动触发"
        elif trigger_type == 1:
            cron = trigger_info.get('triggerParams', {}).get('cron', '')
            return f"定时触发 ({cron})"
        elif trigger_type == 2:
            return "Webhook 触发"
        return "未知"

    # ==================== 交互式创建流水线 ====================

    def interactive_create_pipeline(self, user_input: str = None) -> Dict[str, Any]:
        """
        交互式创建流水线 - 6步流程

        流程:
        1. 解析用户输入 -> 获取 spaceId 和技术栈语言
        2. 提示用户补充缺失信息 -> 选择模板
        3. 添加代码源 -> 选择代码源类型、配置 webhook
        4. 配置任务节点 -> 检测必填项，返回待修改数据
        5. 调用保存接口 -> 创建流水线
        6. 执行流水线 -> 复用现有 run_pipeline 流程

        Args:
            user_input: 用户输入的自然语言描述

        Returns:
            创建结果和执行结果
        """
        print("\n" + "=" * 60)
        print("欢迎使用流水线创建向导")
        print("=" * 60)

        # ===== 步骤1: 解析用户输入，获取 spaceId 和技术栈 =====
        print("\n[步骤1] 解析用户输入...")
        parsed_info = self._parse_create_request(user_input)

        # ===== 步骤2: 补充缺失信息 =====
        if not parsed_info.get('space_id'):
            parsed_info['space_id'] = self._prompt_space_id()
        if not parsed_info.get('language'):
            parsed_info['language'] = self._prompt_language()

        # 查询模板列表，让用户选择
        print(f"\n[步骤2] 选择模板 (space_id={parsed_info['space_id']}, language={parsed_info['language']})...")
        template = self._select_template(parsed_info['space_id'], parsed_info['language'])

        if not template:
            print("未选择模板，创建流水线已取消")
            return {'code': -1, 'message': '用户取消操作'}

        # ===== 步骤3: 添加代码源 =====
        print("\n[步骤3] 添加代码源...")
        sources = self._interactive_add_sources()

        if not sources:
            print("未添加任何代码源，创建流水线已取消")
            return {'code': -1, 'message': '用户取消操作'}

        # ===== 步骤4: 配置任务节点（基于模板）=====
        print("\n[步骤4] 配置任务节点...")
        task_data_list = self._prepare_task_data_from_template(template, sources)

        # ===== 步骤5: 保存流水线 =====
        print("\n[步骤5] 保存流水线...")
        pipeline_name = parsed_info.get('name') or template.get('name') or f"新建流水线_{int(time.time())}"

        pipeline_result = self._save_pipeline_with_interaction(
            pipeline_name,
            parsed_info['space_id'],
            sources,
            template,
            task_data_list
        )

        # ===== 步骤6: 执行流水线 =====
        if pipeline_result.get('code') == 0 or pipeline_result.get('code') == '0':
            pipeline_id = pipeline_result.get('data', {}).get('pipelineId')
            if pipeline_id:
                print(f"\n[步骤6] 执行流水线 (ID: {pipeline_id})...")
                return self.run_pipeline(pipeline_id)

        return pipeline_result

    def _parse_create_request(self, user_input: str = None) -> Dict[str, Any]:
        """
        解析用户输入的自然语言，提取 space_id、language 和 name

        Args:
            user_input: 用户输入的自然语言描述

        Returns:
            解析结果: {'space_id': '1001', 'language': 'java', 'name': 'xxx'}
        """
        result = {
            'space_id': None,
            'language': None,
            'name': None
        }

        if not user_input:
            return result

        user_input_lower = user_input.lower()

        # 提取 space_id (支持多种格式: space-001, spaceId: 1001, space_id=1001)
        space_patterns = [
            r'space[_-]?id[=:]?\s*(\d+)',
            r'space[_-]?(\d+)',
            r'空间[_-]?(\d+)',
            r'在[ ]*(\d+)[ ]*创建',  # "在1001创建"
        ]
        for pattern in space_patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                result['space_id'] = int(match.group(1))
                break

        # 提取 language (技术栈语言)
        language_patterns = {
            'java': [r'java', r'jdk', r'maven', r'gradle'],
            'nodejs': [r'nodejs', r'node', r'javascript', r'vue', r'react'],
            'python': [r'python', r'py'],
            'go': [r'go[ ]*lang', r'\bgo\b', r'golang'],
            'cpp': [r'c\+\+', r'cpp', r'c/c\+\+'],
            'general': [r'通用', r'general', r'基础']
        }
        for lang, keywords in language_patterns.items():
            for keyword in keywords:
                if re.search(keyword, user_input_lower):
                    result['language'] = lang
                    break
            if result['language']:
                break

        # 提取 name (流水线名称)
        name_patterns = [
            r'名为[ ]*(.+?)(?:的|$)',
            r'名字[ ]*(.+?)(?:的|$)',
            r'名称[ ]*(.+?)(?:的|$)',
            r'创建[ ]*(.+?)(?:流水线|$)',
            r'name[=:]?\s*(.+?)(?:\s|$)',
        ]
        for pattern in name_patterns:
            match = re.search(pattern, user_input)
            if match:
                result['name'] = match.group(1).strip()
                break

        print(f"解析结果: space_id={result['space_id']}, language={result['language']}, name={result['name']}")
        return result

    def _prompt_space_id(self) -> int:
        """提示用户输入 space_id"""
        while True:
            try:
                space_id_input = input("\n请输入空间ID (space_id): ").strip()
                if space_id_input:
                    return int(space_id_input)
                print("space_id 不能为空")
            except ValueError:
                print("请输入有效的数字")

    def _prompt_language(self) -> str:
        """提示用户选择技术栈语言"""
        languages = [
            {'label': 'Java', 'value': 'java'},
            {'label': 'Node.js', 'value': 'nodejs'},
            {'label': 'Python', 'value': 'python'},
            {'label': 'Go', 'value': 'go'},
            {'label': 'C/C++', 'value': 'cpp'},
            {'label': '通用/其他', 'value': 'general'},
        ]
        result = prompt_choice("请选择技术栈语言:", languages, 'value')
        return result.get('value') if result else 'general'

    def _select_template(self, space_id: int, language: str = None) -> Dict:
        """
        让用户选择流水线模板

        Args:
            space_id: 工作空间ID
            language: 技术栈语言筛选

        Returns:
            选中的模板对象
        """
        print(f"\n查询模板列表 (space_id={space_id}, language={language})...")

        # 调用现有接口查询模板
        result = self.list_pipeline_templates(
            space_id=space_id,
            template_type=language,
            page_no=1,
            page_size=20
        )

        # 处理嵌套响应结构
        inner_code = result.get('data', {}).get('code')
        if inner_code != 0 and inner_code != '0':
            print(f"查询模板失败: {result.get('data', {}).get('message')}")
            return None

        template_list = result.get('data', {}).get('data', {}).get('records', [])

        if not template_list:
            print("当前没有可用模板")
            # 提供默认空模板
            if confirm("是否继续使用空白模板?", default=True):
                return {
                    'name': '空白流水线',
                    'templateId': None,
                    'language': language
                }
            return None

        # 构建选项列表
        options = []
        for tpl in template_list:
            options.append({
                'label': tpl.get('pipelineTemplateName', '未命名模板'),
                'value': tpl,
                'templateId': tpl.get('id'),
                'name': tpl.get('pipelineTemplateName'),
                'language': tpl.get('pipelineTemplateType'),
                'description': tpl.get('description', '')
            })

        print(f"\n找到 {len(options)} 个模板:")
        for i, opt in enumerate(options, 1):
            desc = opt.get('description', '')
            print(f"  {i}. {opt['label']}" + (f" - {desc}" if desc else ""))

        # 添加"不使用模板"选项
        options.append({
            'label': '不使用模板（空白流水线）',
            'value': {
                'name': '空白流水线',
                'templateId': None,
                'language': language
            }
        })

        result = prompt_choice("\n请选择模板:", options, 'value')
        return result if result else None

    def _interactive_add_sources(self) -> List[Dict]:
        """
        交互式添加代码源

        Returns:
            代码源列表
        """
        sources = []

        while True:
            print("\n" + "-" * 40)
            print(f"当前已添加 {len(sources)} 个代码源")

            if sources:
                for i, src in enumerate(sources, 1):
                    src_data = src.get('data', {})
                    src_type = src_data.get('sourceType', 'code')
                    if src_type == 'code':
                        print(f"  {i}. 代码源: {src.get('name')} - {src_data.get('repoType')} - {src_data.get('branch')}")
                    else:
                        print(f"  {i}. 制品源: {src.get('name')} - {src_data.get('packageType')}")

            print("-" * 40)

            # 询问是否添加代码源
            if not confirm("是否添加代码源?", default=True if not sources else False):
                break

            # 选择代码源类型
            source_type = self._prompt_source_type()

            if source_type == 'code':
                # 代码源配置
                source = self._create_code_source_interactive()
            else:
                # 制品源配置
                source = self._create_package_source_interactive()

            if source:
                sources.append(source)
                print(f"✓ 已添加: {source.get('name')}")

        return sources

    def _prompt_source_type(self) -> str:
        """提示用户选择代码源类型"""
        types = [
            {'label': '代码仓库 (GIT)', 'value': 'code'},
            {'label': '制品仓库 (Docker/Maven)', 'value': 'package'},
        ]
        result = prompt_choice("请选择代码源类型:", types, 'value')
        return result.get('value') if result else 'code'

    def _prompt_repo_type(self) -> str:
        """提示用户选择代码仓库类型"""
        repo_types = [
            {'label': 'Gitee', 'value': 'GITEE'},
            {'label': 'GitLab', 'value': 'GITLAB'},
            {'label': 'FlyCode', 'value': 'FLYCODE'},
            {'label': 'GitHub', 'value': 'GITHUB'},
        ]
        result = prompt_choice("请选择代码仓库类型:", repo_types, 'value')
        return result.get('value') if result else 'GITEE'

    def _create_code_source_interactive(self) -> Dict:
        """交互式创建代码源"""
        # 选择仓库类型
        repo_type = self._prompt_repo_type()

        # 输入仓库信息
        print("\n请输入代码仓库信息:")
        repo_url = prompt_input("  仓库URL: ")
        if not repo_url:
            print("仓库URL不能为空")
            return None

        branch = prompt_input("  分支名称 [main]: ", "main")
        work_path = prompt_input("  工作目录 [/.]: ", "/")

        # 是否开启 webhook
        enable_webhook = confirm("是否开启 Webhook 触发?", default=True)

        webhook_events = []
        if enable_webhook:
            print("\n选择 Webhook 触发事件:")
            events = [
                {'label': 'Push 事件', 'value': 'PUSH'},
                {'label': 'Tag 事件', 'value': 'TAG'},
                {'label': 'Merge Request', 'value': 'MR'},
            ]
            for i, evt in enumerate(events, 1):
                if confirm(f"  {evt['label']}?", default=True):
                    webhook_events.append(evt['value'])

        # 构建代码源对象
        source_id = f"src_{int(time.time() * 1000)}"
        source = {
            'id': source_id,
            'name': repo_url.split('/')[-1].replace('.git', '') or '代码源',
            'sourceId': source_id,
            'data': {
                'sourceType': 'code',
                'repoType': repo_type,
                'repoUrl': repo_url,
                'branch': branch,
                'refsType': 'BRANCH',
                'workPath': work_path,
                'enableWebhook': enable_webhook,
                'webhookEvents': webhook_events if webhook_events else None
            }
        }

        return source

    def _create_package_source_interactive(self) -> Dict:
        """交互式创建制品源"""
        # 选择制品类型
        pkg_types = [
            {'label': 'Docker 镜像', 'value': 'DOCKER'},
            {'label': 'Maven 制品', 'value': 'MAVEN'},
            {'label': 'npm 包', 'value': 'NPM'},
        ]
        result = prompt_choice("请选择制品类型:", pkg_types, 'value')
        package_type = result.get('value') if result else 'DOCKER'

        print("\n请输入制品源信息:")
        work_path = prompt_input("  工作目录 [/.]: ", "/")

        if package_type == 'DOCKER':
            image_name = prompt_input("  镜像名称: ")
            if not image_name:
                print("镜像名称不能为空")
                return None
            default_tag = prompt_input("  标签 [latest]: ", "latest")

            source_data = {
                'sourceType': 'package',
                'packageType': 'DOCKER',
                'imageName': image_name,
                'defaultTag': default_tag,
                'workPath': work_path
            }
            source_name = f"{image_name}:{default_tag}"
        elif package_type == 'MAVEN':
            artifact_name = prompt_input(" 制品名称: ")
            if not artifact_name:
                print("制品名称不能为空")
                return None
            version = prompt_input("  版本 [latest]: ", "latest")

            source_data = {
                'sourceType': 'package',
                'packageType': 'MAVEN',
                'normalArtifactName': artifact_name,
                'defaultTag': version,
                'workPath': work_path
            }
            source_name = f"{artifact_name}:{version}"
        else:
            artifact_name = prompt_input("  包名称: ")
            if not artifact_name:
                print("包名称不能为空")
                return None
            version = prompt_input("  版本 [latest]: ", "latest")

            source_data = {
                'sourceType': 'package',
                'packageType': 'NPM',
                'normalArtifactName': artifact_name,
                'defaultTag': version,
                'workPath': work_path
            }
            source_name = f"{artifact_name}@{version}"

        # 构建制品源对象
        source_id = f"pkg_{int(time.time() * 1000)}"
        source = {
            'id': source_id,
            'name': source_name,
            'sourceId': source_id,
            'data': source_data
        }

        return source

    def _prepare_task_data_from_template(self, template: Dict, sources: List[Dict]) -> List[Dict]:
        """
        基于模板准备任务数据

        Args:
            template: 选中的模板
            sources: 代码源列表

        Returns:
            任务数据列表
        """
        # 如果是空白模板，创建默认任务
        if not template.get('templateId'):
            print("创建空白流水线任务...")
            # 为每个代码源创建一个默认任务
            task_data_list = []
            for i, src in enumerate(sources):
                src_data = src.get('data', {})
                work_path = src_data.get('workPath', '/')
                source_type = src_data.get('sourceType', 'code')

                if source_type == 'code':
                    task_data_list.append({
                        'taskId': f"task_{i+1}",
                        'taskName': f"构建任务 {i+1}",
                        'sourceId': src.get('id'),
                        'workPath': work_path,
                        'taskType': 'build',
                        'config': {}
                    })

            return task_data_list

        # 从模板中提取任务数据
        print("从模板加载任务配置...")

        # 查询模板详情
        template_id = template.get('templateId')

        # 尝试从模板中获取 taskDataList
        task_data_list = template.get('taskDataList', [])

        if not task_data_list:
            # 创建默认任务
            task_data_list = []
            for i, src in enumerate(sources):
                src_data = src.get('data', {})
                work_path = src_data.get('workPath', '/')

                task_data_list.append({
                    'taskId': f"task_{i+1}",
                    'taskName': f"构建任务 {i+1}",
                    'sourceId': src.get('id'),
                    'workPath': work_path,
                    'taskType': 'build',
                    'config': {}
                })

        # 关联 sourceId
        for task in task_data_list:
            # 尝试匹配 workPath 相同的 source
            task_work_path = task.get('workPath', '')
            matched_src = None
            for src in sources:
                if src.get('data', {}).get('workPath') == task_work_path:
                    matched_src = src
                    break

            if matched_src:
                task['sourceId'] = matched_src.get('id')

        print(f"已配置 {len(task_data_list)} 个任务")
        return task_data_list

    def _save_pipeline_with_interaction(
        self,
        name: str,
        space_id: int,
        sources: List[Dict],
        template: Dict,
        task_data_list: List[Dict]
    ) -> Dict:
        """
        保存流水线（带交互确认）

        Args:
            name: 流水线名称
            space_id: 空间ID
            sources: 代码源列表
            template: 模板信息
            task_data_list: 任务数据列表

        Returns:
            保存结果
        """
        # 预览流水线配置
        print("\n" + "=" * 60)
        print("流水线配置预览")
        print("=" * 60)
        print(f"  名称: {name}")
        print(f"  空间ID: {space_id}")
        print(f"  代码源数量: {len(sources)}")
        for i, src in enumerate(sources, 1):
            src_data = src.get('data', {})
            print(f"    [{i}] {src.get('name')} - {src_data.get('repoType') or src_data.get('packageType')}")
        print(f"  任务数量: {len(task_data_list)}")
        for i, task in enumerate(task_data_list, 1):
            print(f"    [{i}] {task.get('taskName')} (sourceId: {task.get('sourceId')})")
        print("=" * 60)

        if not confirm("\n确认保存流水线?", default=True):
            print("已取消保存")
            return {'code': -1, 'message': '用户取消操作'}

        # 生成 pipelineKey
        import uuid
        pipeline_key = f"pipeline-{name.lower().replace(' ', '-')}-{int(time.time())}"

        # 组装 pipeline_data
        pipeline_data = {
            'name': name,
            'spaceId': space_id,
            'pipelineKey': pipeline_key,
            'aliasId': f"P{int(time.time()) % 100000}",
            'sources': sources,
            'stages': template.get('stages', []),
            'timeoutDuration': '2H',
            'buildPlatform': 'linux'
        }

        # 调用保存接口
        print("\n正在保存流水线...")
        result = self.save_pipeline(pipeline_data, task_data_list)

        # 处理嵌套响应结构
        inner_code = result.get('data', {}).get('code')
        if inner_code == 0 or inner_code == '0':
            print(f"✓ 流水线创建成功! ID: {result.get('data', {}).get('data', {}).get('pipelineId')}")
        else:
            print(f"✗ 流水线创建失败: {result.get('data', {}).get('message')}")

        return result
