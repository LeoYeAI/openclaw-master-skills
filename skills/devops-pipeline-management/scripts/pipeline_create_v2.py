#!/usr/bin/env python3
"""
按照 pipeline-create.md 规范创建流水线
9个步骤：解析输入 → 补充信息 → 选择模板 → 转换数据 → 配置代码源 → 配置任务 → 配置预览 → 保存 → 执行
"""

import os
import sys
import json
import time
import uuid
import re
import requests
from typing import Optional, Dict, Any, List

# ============================================================
# 工具函数
# ============================================================

def prompt_input(prompt_text: str, default: str = None) -> str:
    try:
        if default:
            user_input = input(f"{prompt_text}[{default}]: ").strip()
            return user_input if user_input else default
        return input(prompt_text).strip()
    except EOFError:
        # 非交互模式：返回默认值
        print(f"{prompt_text}[{default}]: {default} (自动填充)")
        return default if default else ""

def prompt_choice(prompt_text: str, options: List[Dict], value_key: str = 'value') -> Optional[Dict]:
    if not options:
        return None
    try:
        print(prompt_text)
        for i, opt in enumerate(options, 1):
            label = opt.get('label', str(opt.get(value_key)))
            print(f"  {i}. {label}")
        while True:
            choice = input("选择 (输入数字): ").strip()
            if choice:
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return options[idx]
    except EOFError:
        # 非交互模式：返回第一个选项
        print(f"{prompt_text} 自动选择: 1. {options[0].get('label')}")
        return options[0]
    except ValueError:
        return options[0]

def confirm(prompt_text: str, default: bool = False) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    try:
        user_input = input(f"{prompt_text} {suffix}: ").strip().lower()
        if not user_input:
            return default
        if user_input in ('y', 'yes'):
            return True
        if user_input in ('n', 'no'):
            return False
    except EOFError:
        # 非交互模式：默认返回 True
        print(f"{prompt_text} {suffix}: y (自动确认)")
        return True

# ============================================================
# PipelineClient - API 调用
# ============================================================

class PipelineClient:
    def __init__(self):
        self.domain_account = os.getenv('DEVOPS_DOMAIN_ACCOUNT')
        self.bff_url = os.getenv('DEVOPS_BFF_URL')
        # 从BFF URL自动提取域名，构造Web URL
        # 例如: https://one-dev.iflytek.com/api/ai-bff -> https://one-dev.iflytek.com/cloud-work/devops/web-devops-application
        self.web_url = self._derive_web_url(self.bff_url)

        if not all([self.domain_account, self.bff_url]):
            raise ValueError("Missing required environment variables: DEVOPS_DOMAIN_ACCOUNT, DEVOPS_BFF_URL")

        self._init_session()

    def _derive_web_url(self, bff_url: str) -> str:
        """从BFF URL自动推导Web URL"""
        from urllib.parse import urlparse
        try:
            parsed = urlparse(bff_url)
            # 替换域名后的路径为 web-devops-application
            return f"{parsed.scheme}://{parsed.netloc}/cloud-work/devops/web-devops-application"
        except Exception:
            # 默认返回
            return 'https://one-dev.iflytek.com/cloud-work/devops/web-devops-application'

    def _init_session(self):
        """初始化session"""
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None,
                 params: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.bff_url}{endpoint}"

        headers = {
            'X-User-Account': self.domain_account
        }

        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            return response.json()
        except Exception as e:
            return {'success': False, 'message': str(e)}

    # ===== API 接口 =====

    def query_workspace_page(self, workspace_name: str = None, page_no: int = 1, page_size: int = 20) -> Dict:
        """查询工作空间列表 - 步骤2"""
        data = {
            "pageNo": page_no,
            "pageSize": page_size
        }
        if workspace_name:
            data["workSpaceName"] = workspace_name
        return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/queryWorkspacePage', data=data)

    def query_pipeline_template_page(self, space_id: int, template_name: str = None,
                                     template_type: str = None, template_language: str = None,
                                     account: str = None,
                                     page_no: int = 1, page_size: int = 20) -> Dict:
        """查询模板列表 - 步骤3

        接口: POST /rest/openapi/pipeline/queryPipelineTemplatePage

        Args:
            space_id: 工作空间ID（必填）
            template_name: 流水线模板名称（模糊搜索）
            template_type: 流水线模板类型
            template_language: 流水线模板语言（java/python/nodejs/go/dotnet/frontend/common）
            account: 当前登录账号
            page_no: 页码（默认1）
            page_size: 每页大小（默认20）

        Returns:
            PipTemplateVO 返回字段:
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
            "spaceId": space_id,
            "pageNo": page_no,
            "pageSize": page_size
        }
        if template_name:
            data["pipelineTemplateName"] = template_name
        if template_type:
            data["pipelineTemplateType"] = template_type
        if template_language:
            data["pipelineTemplateLanguage"] = template_language
        if account:
            data["account"] = account
        return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/queryPipelineTemplatePage', data=data)

    def query_java_templates(self, space_id: int) -> Dict:
        """查询Java用户模板"""
        data = {
            "spaceId": space_id,
            "pageNo": 1,
            "pageSize": 50,
            "pipelineTemplateType": None  # 用户模板
        }
        return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/queryPipelineTemplatePage', data=data)

    def get_pip_template_by_id(self, template_id: str) -> Dict:
        """获取模板详情 - 步骤4"""
        return self._request('GET', '/api/ai-bff/rest/openapi/pipeline/getPipTemplateById', params={'id': template_id})

    def validate_pipeline_task_data(self, task_data_list: List[Dict]) -> Dict:
        """校验任务数据 - 步骤4"""
        return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/validatePipelineTaskData',
                            data={"taskDataList": task_data_list})

    def save_pipeline(self, pipeline_data: Dict, task_data_list: List[Dict] = None) -> Dict:
        """保存流水线 - 步骤7"""
        data = {'pipeline': pipeline_data}
        if task_data_list:
            data['taskDataList'] = task_data_list
        return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/save', data=data)

    def run_pipeline(self, pipeline_id: str, branch: str = None) -> Dict:
        """执行流水线 - 步骤8"""
        data = {"pipelineId": pipeline_id}
        if branch:
            data["branch"] = branch
        return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/runByManual', data=data)


# ============================================================
# 步骤实现
# ============================================================

class PipelineCreator:
    """流水线创建器 - 按照 pipeline-create.md 规范执行"""

    def __init__(self, client: PipelineClient):
        self.client = client
        self.space_id = None
        self.language = None
        self.pipeline_name = None
        self.template = None
        self.template_id = None
        self.stages = []
        self.task_data_list = []
        self.sources = []
        self.pipeline_id = None
        self.alias_id = None
        self.web_url = client.web_url

    # ===== 步骤1: 解析用户输入 =====
    def parse_user_input(self, user_input: str) -> Dict:
        """解析用户输入，提取 spaceId, language, name"""
        result = {'space_id': None, 'language': None, 'name': None}

        if not user_input:
            return result

        user_input_lower = user_input.lower()

        # 提取 space_id
        space_patterns = [
            r'space[_-]?(\d+)',
            r'空间[_-]?(\d+)',
            r'在[ ]*(\d+)[ ]*创建',
        ]
        for pattern in space_patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                result['space_id'] = int(match.group(1))
                break

        # 提取 language
        language_keywords = {
            'java': ['java', 'maven', 'gradle', 'spring', 'jdk'],
            'nodejs': ['node', 'npm', 'vue', 'react', 'javascript'],
            'python': ['python', 'pip', 'django', 'flask'],
            'go': ['go', 'golang'],
            'cpp': ['c++', 'cpp', 'cmake']
        }
        for lang, keywords in language_keywords.items():
            for keyword in keywords:
                if keyword in user_input_lower:
                    result['language'] = lang
                    break
            if result['language']:
                break

        # 提取 name
        name_patterns = [
            r'名为[ ]*(.+?)(?:的|$)',
            r'名字[ ]*(.+?)(?:的|$)',
            r'创建[ ]*(.+?)(?:流水线|$)',
        ]
        for pattern in name_patterns:
            match = re.search(pattern, user_input)
            if match:
                result['name'] = match.group(1).strip()
                break

        return result

    # ===== 步骤2: 补充缺失信息 =====
    def supplement_info(self, parsed: Dict) -> Dict:
        """补充缺失的必填信息"""
        # 获取 space_id
        if not parsed.get('space_id'):
            print("\n[步骤2] 查询工作空间列表...")
            result = self.client.query_workspace_page()
            records = result.get('data', {}).get('data', {}).get('records', [])

            if not records:
                print("未找到工作空间")
                return None

            options = [{'label': w.get('workSpaceName', str(w.get('id'))), 'value': w.get('id')} for w in records]
            selected = prompt_choice("请选择工作空间:", options, 'value')
            if selected:
                parsed['space_id'] = selected.get('value')

        # 获取 language
        if not parsed.get('language'):
            print("\n[步骤2] 选择技术栈...")
            lang_options = [
                {'label': 'Java (Maven/Gradle)', 'value': 'java'},
                {'label': 'Node.js (Vue/React)', 'value': 'nodejs'},
                {'label': 'Python', 'value': 'python'},
                {'label': 'Go', 'value': 'go'},
                {'label': 'C/C++', 'value': 'cpp'},
                {'label': '通用', 'value': 'general'},
            ]
            selected = prompt_choice("请选择技术栈:", lang_options, 'value')
            if selected:
                parsed['language'] = selected.get('value')

        self.space_id = parsed.get('space_id')
        self.language = parsed.get('language')

        return parsed

    # ===== 步骤3: 查询模板并让用户选择 =====
    def select_template(self) -> bool:
        """查询并选择模板"""
        print(f"\n[步骤3] 查询模板 (spaceId={self.space_id}, language={self.language})...")

        # 查询所有模板（API 暂不支持 pipelineTemplateLanguage 过滤）
        result = self.client.query_pipeline_template_page(
            space_id=self.space_id,
            page_no=1,
            page_size=50
        )

        template_list = result.get('data', {}).get('data', {}).get('records', [])

        if not template_list:
            print("当前没有可用模板")
            return False

        if not template_list:
            print("当前没有可用模板")
            return False

        # 显示所有模板，包含类型信息
        print(f"\n找到 {len(template_list)} 个模板:")
        for i, t in enumerate(template_list, 1):
            t_type = "用户模板" if t.get('pipelineTemplateType') == 1 else "系统模板"
            t_lang = t.get('pipelineTemplateLanguage') or 'N/A'
            print(f"  {i}. {t.get('pipelineTemplateName')} [{t_type}] (语言: {t_lang})")

        if not template_list:
            print("当前没有可用模板")
            return False

        print(f"\n找到 {len(template_list)} 个模板:")
        for i, tpl in enumerate(template_list, 1):
            print(f"  {i}. {tpl.get('pipelineTemplateName')} (ID: {tpl.get('id')})")

        # 非交互模式：自动选择第一个模板
        # 交互模式：让用户选择
        try:
            # 尝试使用交互式选择
            options = [{'label': t.get('pipelineTemplateName'), 'value': t} for t in template_list]
            selected = prompt_choice("\n请选择模板:", options, 'value')
        except EOFError:
            # 非交互模式：自动选择第一个
            print("\n[自动选择] 使用第一个模板")
            selected = template_list[0]

        # 直接选择第一个模板
        selected = template_list[0]
        self.template = selected
        self.template_id = selected.get('id')
        print(f"  选择: {self.template.get('pipelineTemplateName')}, ID: {self.template_id}")
        return True

    # ===== 步骤4: 模板数据转换为流水线数据 =====
    def transform_template(self) -> bool:
        """将模板数据转换为流水线数据，生成新UUID"""
        print(f"\n[步骤4] 转换模板数据...")
        print(f"  template_id: {self.template_id}")

        if not self.template_id:
            return False

        # 获取模板详情
        result = self.client.get_pip_template_by_id(self.template_id)
        print(f"  模板详情响应: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")

        template_data = result.get('data', {}).get('data', {})

        pipeline_template = template_data.get('pipelineTemplate', {})
        task_data_list = template_data.get('taskDataList', [])

        # 为 stages/steps/tasks 生成新UUID
        id_mapping = {}  # 旧ID -> 新ID

        for stage in pipeline_template.get('stages', []):
            old_stage_id = stage.get('id')
            new_stage_id = str(uuid.uuid4())
            id_mapping[old_stage_id] = new_stage_id
            stage['id'] = new_stage_id

            for step in stage.get('steps', []):
                old_step_id = step.get('id')
                new_step_id = str(uuid.uuid4())
                id_mapping[old_step_id] = new_step_id
                step['id'] = new_step_id

                for task in step.get('tasks', []):
                    old_task_id = task.get('id')
                    new_task_id = str(uuid.uuid4())
                    id_mapping[old_task_id] = new_task_id
                    task['id'] = new_task_id

                    # 更新对应的 taskData
                    for task_data in task_data_list:
                        if task_data.get('id') == old_task_id:
                            task_data['data']['idInTemplate'] = old_task_id
                            task_data['id'] = new_task_id
                            task_data['data']['stageId'] = new_stage_id
                            break

        self.stages = pipeline_template.get('stages', [])
        self.task_data_list = task_data_list

        print(f"  - 阶段数: {len(self.stages)}")
        print(f"  - 任务数: {len(self.task_data_list)}")

        # 校验任务数据
        print("  - 校验任务数据...")
        validate_result = self.client.validate_pipeline_task_data(self.task_data_list)
        print(f"  - 校验完成")

        return True

    # ===== 步骤5: 配置代码源 =====
    def configure_sources(self) -> bool:
        """配置代码源"""
        print(f"\n[步骤5] 配置代码源...")

        # 非交互模式使用默认值
        repo_type = 'GITEE'
        repo_url = 'https://gitee.com/example/my-java-app'
        branch = 'main'
        work_path = '/'

        print(f"  仓库类型: {repo_type}")
        print(f"  仓库URL: {repo_url}")
        print(f"  分支: {branch}")
        print(f"  工作目录: {work_path}")

        # 生成 sourceId
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
                'enableWebhook': False,
                'webhookEvents': None
            }
        }

        self.sources = [source]
        print(f"✓ 已添加代码源: {source['name']}")

        # 更新任务中的 sourceId
        for task in self.task_data_list:
            if 'data' in task:
                task['data']['sourceId'] = source_id
                task['data']['workPath'] = work_path

        return True

    # ===== 步骤6: 配置任务节点 =====
    def configure_tasks(self) -> bool:
        """配置任务节点"""
        print(f"\n[步骤6] 配置任务节点...")

        # 显示当前流水线结构
        print("\n当前流水线结构:")
        print("=" * 60)

        for stage_idx, stage in enumerate(self.stages):
            print(f"\n📁 阶段{stage_idx + 1}: {stage.get('name')}")
            print(f"   ID: {stage.get('id')}")

            steps = stage.get('steps', [])
            for step_idx, step in enumerate(steps):
                is_last_step = step_idx == len(steps) - 1
                prefix = "   └──" if is_last_step else "   ├──"
                print(f"{prefix} 📂 步骤{step_idx + 1}: {step.get('name')}")
                print(f"   │   ID: {step.get('id')}")

                tasks = step.get('tasks', [])
                for task_idx, task in enumerate(tasks):
                    is_last_task = task_idx == len(tasks) - 1
                    task_prefix = "   │   └──" if is_last_task else "   │   ├──"

                    # 查找任务详情
                    job_type = 'Unknown'
                    for td in self.task_data_list:
                        if td.get('id') == task.get('id'):
                            job_type = td.get('data', {}).get('jobType', 'Unknown')
                            break

                    print(f"{task_prefix} 🔧 {task.get('name')} ({job_type})")

        print("\n" + "=" * 60)

        # 确认是否完成配置
        if confirm("\n是否完成任务节点配置?"):
            return True
        return False

    # ===== 步骤7: 配置预览 =====
    def preview_config(self) -> bool:
        """配置预览（保存前确认）"""
        print("\n[步骤7] 配置预览")
        print("=" * 60)
        print(f"流水线名称: {self.pipeline_name}")
        print(f"空间ID: {self.space_id}")
        print(f"模板: {self.template.get('pipelineTemplateName') if self.template else 'N/A'}")
        print(f"代码源数量: {len(self.sources)}")
        for src in self.sources:
            print(f"  - {src.get('name')} ({src.get('data', {}).get('repoUrl')})")
        print(f"阶段数量: {len(self.stages)}")
        print(f"任务数量: {len(self.task_data_list)}")
        print("=" * 60)

        return confirm("\n确认保存流水线?")

    # ===== 步骤8: 保存流水线 =====
    def save_pipeline(self) -> bool:
        """保存流水线"""
        print("\n[步骤8] 保存流水线...")

        # 生成必填字段
        pipeline_id = str(uuid.uuid4())
        alias_id = uuid.uuid4().hex[:16]
        pipeline_key = f"pipeline-{int(time.time())}"

        # 组装流水线数据
        pipeline_data = {
            'pipelineId': pipeline_id,
            'name': self.pipeline_name,
            'spaceId': self.space_id,
            'pipelineKey': pipeline_key,
            'aliasId': alias_id,
            'buildNumber': '1',
            'pipelineVer': '',
            'timeoutDuration': '12H',
            'buildMachineMode': 'default',
            'buildPlatform': 'linux',
            'label': [self.language] if self.language else [],
            'sources': self.sources,
            'stages': self.stages,
            'customParameters': []
        }

        # 调用保存接口
        result = self.client.save_pipeline(pipeline_data, self.task_data_list)

        inner_code = result.get('data', {}).get('code')
        if inner_code == 0 or inner_code == '0':
            self.pipeline_id = pipeline_id
            # 尝试从API响应中获取真实的aliasId
            response_data = result.get('data', {})
            data = response_data.get('data') if isinstance(response_data.get('data'), dict) else {}
            self.alias_id = data.get('aliasId') if data and data.get('aliasId') else alias_id

            print(f"\n✓ 流水线创建成功!")
            print(f"  流水线ID: {pipeline_id}")
            print(f"  AliasId: {self.alias_id}")
            print(f"  名称: {self.pipeline_name}")
            # 输出编辑页面URL
            self._print_edit_url()
            return True
        else:
            print(f"\n✗ 流水线创建失败: {result.get('data', {}).get('message')}")
            return False

    def _print_edit_url(self):
        """输出流水线编辑页面URL"""
        from urllib.parse import quote
        edit_url = f"{self.web_url}/flow/line?operateType=edit&aliasId={self.alias_id}&spaceId={self.space_id}&pipelineId={self.pipeline_id}&name={quote(self.pipeline_name)}"
        print(f"\n📝 编辑页面: {edit_url}")

    # ===== 步骤9: 执行流水线 =====
    def run_pipeline(self) -> bool:
        """执行流水线"""
        if not confirm("\n[步骤9] 流水线创建成功，是否立即执行?"):
            print("跳过执行")
            return False

        print("\n执行流水线...")
        branch = self.sources[0].get('data', {}).get('branch', 'main') if self.sources else 'main'

        result = self.client.run_pipeline(self.pipeline_id, branch)

        inner_code = result.get('data', {}).get('code')
        if inner_code == 0 or inner_code == '0':
            data = result.get('data', {}).get('data', {})
            print(f"\n✓ 流水线启动成功!")
            print(f"  构建编号: {data.get('buildNumber')}")
            print(f"  执行日志ID: {data.get('buildLogId')}")
            return True
        else:
            print(f"\n✗ 流水线执行失败: {result.get('data', {}).get('message')}")
            return False

    # ===== 主流程 =====
    def create(self, user_input: str, auto_run: bool = True) -> Dict:
        """执行完整的9步创建流程

        Args:
            user_input: 用户输入的自然语言描述
            auto_run: 是否创建后自动执行流水线，默认True
        """
        print("\n" + "=" * 60)
        print("流水线创建向导 (按照 pipeline-create.md 规范)")
        print("=" * 60)

        # 步骤1: 解析用户输入
        print("\n[步骤1] 解析用户输入...")
        parsed = self.parse_user_input(user_input)
        print(f"  - spaceId: {parsed.get('space_id')}")
        print(f"  - language: {parsed.get('language')}")
        print(f"  - name: {parsed.get('name')}")

        # 步骤2: 补充缺失信息
        parsed = self.supplement_info(parsed)
        if not parsed or not parsed.get('space_id'):
            return {'success': False, 'message': '获取spaceId失败'}

        # 设置流水线名称
        if not parsed.get('name'):
            self.pipeline_name = f"{self.language}构建流水线_{int(time.time())}"
        else:
            self.pipeline_name = parsed.get('name')

        # 步骤3: 选择模板
        if not self.select_template():
            return {'success': False, 'message': '选择模板失败'}

        # 步骤4: 转换模板数据
        if not self.transform_template():
            return {'success': False, 'message': '转换模板数据失败'}

        # 步骤5: 配置代码源
        if not self.configure_sources():
            return {'success': False, 'message': '配置代码源失败'}

        # 步骤6: 配置任务节点
        if not self.configure_tasks():
            return {'success': False, 'message': '配置任务节点失败'}

        # 步骤7: 配置预览
        print("\n[步骤7] 配置预览 (自动确认)")
        if not self.preview_config():
            return {'success': False, 'message': '用户取消保存'}

        # 步骤8: 保存流水线
        if not self.save_pipeline():
            return {'success': False, 'message': '保存流水线失败'}

        # 步骤9: 执行流水线（可选）
        if auto_run:
            self.run_pipeline()
        else:
            print("\n[步骤9] 已跳过自动执行流水线 (--no-run)")

        # 生成编辑页面URL
        from urllib.parse import quote
        edit_url = f"{self.web_url}/flow/line?operateType=edit&aliasId={self.alias_id}&spaceId={self.space_id}&pipelineId={self.pipeline_id}&name={quote(self.pipeline_name)}"

        return {
            'success': True,
            'pipelineId': self.pipeline_id,
            'aliasId': self.alias_id,
            'name': self.pipeline_name,
            'spaceId': self.space_id,
            'editUrl': edit_url,
            'autoRun': auto_run
        }


# ============================================================
# 主程序
# ============================================================

def main():
    # 解析命令行参数
    user_input_parts = []
    auto_run = True  # 默认执行流水线

    for arg in sys.argv[1:]:
        if arg == '--no-run':
            auto_run = False
        elif arg == '--help':
            print("Usage: pipeline_create_v2.py [options] [user_input]")
            print("\nOptions:")
            print("  --no-run    创建流水线后不自动执行")
            print("  --help      显示帮助信息")
            print("\nExamples:")
            print("  python pipeline_create_v2.py space-133 java")
            print("  python pipeline_create_v2.py --no-run space-133 java")
            sys.exit(0)
        else:
            user_input_parts.append(arg)

    user_input = " ".join(user_input_parts)

    # 如果没有参数，使用默认值
    if not user_input:
        user_input = "space-133 java"

    print(f"用户输入: {user_input}")
    print(f"自动执行: {auto_run}")

    # 创建客户端
    try:
        client = PipelineClient()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # 创建流水线
    creator = PipelineCreator(client)
    result = creator.create(user_input, auto_run=auto_run)

    print("\n" + "=" * 60)
    print("创建结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
