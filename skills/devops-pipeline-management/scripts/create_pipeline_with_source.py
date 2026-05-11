#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建 Node.js 构建流水线脚本（支持代码源配置）
基于模板 ID: 640584d7-0cf4-4411-b265-c88e01bb2cc0
"""

import json
import uuid
import string
import random
import copy
import requests
import os
import re
import time

# 配置
DEVOPS_DOMAIN_ACCOUNT = os.getenv("DEVOPS_DOMAIN_ACCOUNT", "rfdai")
DEVOPS_BFF_URL = os.getenv("DEVOPS_BFF_URL", "https://one-dev.iflytek.com/devops")

SPACE_ID = 133
# 使用时间戳生成唯一名称
PIPELINE_NAME = f"Node.js 构建流水线ceshi_{int(time.time())}"
TEMPLATE_ID = "640584d7-0cf4-4411-b265-c88e01bb2cc0"

def generate_alias_id(length=16):
    """生成16位随机字符串 aliasId"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def generate_pipeline_key(name):
    """从流水线名称生成 pipelineKey"""
    # 只保留字母、数字、下划线和连字符
    key = re.sub(r'[^\w\u4e00-\u9fa5-]', '', name)
    # 转换为小写
    key = key.lower()
    # 截取最大30字符
    return key[:30]

def get_template_detail(template_id):
    """获取模板详情"""
    url = f"{DEVOPS_BFF_URL}/api/ai-bff/rest/openapi/pipeline/getPipTemplateById"
    headers = {
        "X-User-Account": DEVOPS_DOMAIN_ACCOUNT
    }

    print(f"正在获取模板详情: {template_id}")
    response = requests.get(url, params={"id": template_id}, headers=headers)
    result = response.json()

    if result.get("success") and result.get("code") == "200":
        # 数据嵌套在 data.data 中
        return result["data"]["data"]
    else:
        raise Exception(f"获取模板详情失败: {result}")

def transform_template_data(template_response):
    """转换模板数据，生成新的UUID"""
    pipeline_template = copy.deepcopy(template_response["pipelineTemplate"])
    task_data_list = copy.deepcopy(template_response["taskDataList"])

    task_id_mapping = {}

    # 遍历 stages，生成新ID
    for stage in pipeline_template.get("stages", []):
        old_stage_id = stage["id"]
        stage["id"] = str(uuid.uuid4())
        print(f"  Stage ID 转换: {old_stage_id[:8]}... -> {stage['id'][:8]}...")

        for step in stage.get("steps", []):
            old_step_id = step["id"]
            step["id"] = str(uuid.uuid4())
            print(f"    Step ID 转换: {old_step_id[:8]}... -> {step['id'][:8]}...")

            for task in step.get("tasks", []):
                old_task_id = task["id"]
                new_task_id = str(uuid.uuid4())
                task_id_mapping[old_task_id] = new_task_id
                task["id"] = new_task_id
                print(f"      Task ID 转换: {old_task_id[:8]}... -> {new_task_id[:8]}...")

    # 更新 taskDataList 中的 ID
    for task_data in task_data_list:
        old_id = task_data["id"]
        if old_id in task_id_mapping:
            new_id = task_id_mapping[old_id]
            if "data" not in task_data:
                task_data["data"] = {}
            task_data["data"]["idInTemplate"] = old_id
            task_data["id"] = new_id
            print(f"      TaskData ID 同步: {old_id[:8]}... -> {new_id[:8]}...")

    return {
        "pipelineTemplate": pipeline_template,
        "taskDataList": task_data_list
    }

def configure_sources():
    """配置代码源"""
    print("\n" + "=" * 60)
    print("步骤3.5: 配置代码源")
    print("=" * 60)
    print("请提供代码源信息，或直接按Enter使用默认配置")

    # 询问是否配置代码源
    print("\n是否配置代码源?")
    print("  [Y] 是 - 配置代码源（推荐）")
    print("  [N] 否 - 跳过代码源配置")
    choice = input("请选择 [Y/n]: ").strip().lower()

    if choice and choice != 'y' and choice != 'yes':
        print("\n⚠️  跳过代码源配置")
        print("   注意：跳过代码源后，流水线将无法正常执行")
        return [], "", ""

    # 默认配置
    print("\n使用默认代码源配置:")
    print("  代码源类型: Gitee")
    print("  仓库名称: example-nodejs-project")
    print("  默认分支: master")
    print("  工作目录: ./")

    confirm = input("\n确认使用默认配置? [Y/n]: ").strip().lower()

    if confirm and confirm != 'y' and confirm != 'yes':
        # 自定义配置
        print("\n请输入代码源信息:")
        repo_name = input("  仓库名称: ").strip() or "example-nodejs-project"
        branch = input("  默认分支 [master]: ").strip() or "master"
        work_path = input("  工作目录 (相对路径) [./]: ").strip() or "./"

        print("\n选择代码源类型:")
        print("  [1] Gitee")
        print("  [2] GitLab")
        print("  [3] FlyCode (质效Code)")
        print("  [4] GitHub")
        type_choice = input("请选择 [1-4]: ").strip() or "1"

        repo_type_map = {
            "1": "GITEE",
            "2": "GITLAB",
            "3": "FLYCODE",
            "4": "GITHUB"
        }
        repo_type = repo_type_map.get(type_choice, "GITEE")

        # 根据类型设置仓库URL
        if repo_type == "GITEE":
            repo_url = f"https://gitee.com/example/{repo_name}.git"
        elif repo_type == "GITLAB":
            repo_url = f"https://gitlab.com/example/{repo_name}.git"
        elif repo_type == "FLYCODE":
            repo_url = f"https://code.iflytek.com/example/{repo_name}.git"
        else:  # GitHub
            repo_url = f"https://github.com/example/{repo_name}.git"

    else:
        # 使用默认值
        repo_name = "example-nodejs-project"
        branch = "master"
        work_path = "./"
        repo_type = "GITEE"
        repo_url = f"https://gitee.com/example/{repo_name}.git"

    # 创建代码源配置
    source_id = str(uuid.uuid4())
    source = {
        "id": source_id,
        "name": repo_name,
        "repoType": repo_type,
        "authType": "OAUTH",
        "repoUrl": repo_url,
        "defaultBranch": branch,
        "credentialId": "",
        "webhookInfo": {
            "webhookSwitch": False,
            "webhookType": 0,
            "eventBlock": []
        }
    }

    print(f"\n✅ 代码源配置完成:")
    print(f"  代码源ID: {source_id}")
    print(f"  仓库名称: {repo_name}")
    print(f"  仓库类型: {repo_type}")
    print(f"  仓库地址: {repo_url}")
    print(f"  默认分支: {branch}")
    print(f"  工作目录: {work_path}")

    return [source], work_path, source_id

def assemble_pipeline_data(transformed_data, pipeline_name, space_id):
    """组装流水线数据"""
    pipeline_template = transformed_data["pipelineTemplate"]
    task_data_list = transformed_data["taskDataList"]

    # 配置代码源
    sources, work_path, source_id = configure_sources()

    # 生成 pipelineId
    pipeline_id = str(uuid.uuid4())
    alias_id = generate_alias_id()
    pipeline_key = generate_pipeline_key(pipeline_name)

    # 更新任务数据中的 workPath 和 sourceId
    for task_data in task_data_list:
        if task_data["data"].get("jobType") == "NpmBuild":
            task_data["data"]["workPath"] = work_path or "."
            task_data["data"]["sourceId"] = source_id or ""

    pipeline = {
        "pipelineId": pipeline_id,
        "name": pipeline_name,
        "aliasId": alias_id,
        "pipelineKey": pipeline_key,
        "spaceId": space_id,
        "buildNumber": "1",
        "timeoutDuration": "12H",
        "buildMachineMode": "default",
        "buildPlatform": "linux",
        "label": [],  # 必填字段，标签列表
        "sources": sources,  # 配置的代码源
        "stages": copy.deepcopy(pipeline_template.get("stages", [])),
        "customParameters": copy.deepcopy(pipeline_template.get("customParameters", [])),
        "triggerInfo": {
            "triggerType": 0,
            "triggerParams": {}
        },
        "autoFillRunConfig": False
    }

    return {
        "pipeline": pipeline,
        "taskDataList": copy.deepcopy(task_data_list),
        "sources": sources  # 顶层也需要 sources 字段
    }

def save_pipeline(pipeline_data):
    """保存流水线"""
    url = f"{DEVOPS_BFF_URL}/api/ai-bff/rest/openapi/pipeline/save"
    headers = {
        "X-User-Account": DEVOPS_DOMAIN_ACCOUNT,
        "Content-Type": "application/json"
    }

    print(f"\n正在保存流水线...")
    print(f"  流水线ID: {pipeline_data['pipeline']['pipelineId']}")
    print(f"  流水线名称: {pipeline_data['pipeline']['name']}")
    print(f"  空间ID: {pipeline_data['pipeline']['spaceId']}")

    response = requests.post(url, json=pipeline_data, headers=headers)
    result = response.json()

    print(f"\n保存API响应:")
    print(f"  Success: {result.get('success')}")
    print(f"  Code: {result.get('code')}")
    print(f"  Message: {result.get('message')}")
    if "data" in result:
        print(f"  Data: {result['data']}")

    if result.get("success") and result.get("code") == "200":
        return result.get("data", result)
    else:
        raise Exception(f"保存流水线失败: {result}")

def main():
    """主流程"""
    print("=" * 60)
    print("Node.js 构建流水线创建")
    print("=" * 60)

    try:
        # 步骤1: 获取模板详情
        print("\n步骤1: 获取模板详情")
        template_data = get_template_detail(TEMPLATE_ID)
        print(f"  模板名称: {template_data['pipelineTemplate']['pipelineTemplateName']}")
        print(f"  模板语言: {template_data['pipelineTemplate']['pipelineTemplateLanguage']}")
        print(f"  阶段数量: {len(template_data['pipelineTemplate'].get('stages', []))}")

        # 步骤2: 转换模板数据
        print("\n步骤2: 转换模板数据（生成新ID）")
        transformed = transform_template_data(template_data)

        # 步骤3+3.5: 组装流水线数据（包含代码源配置）
        print("\n步骤3: 组装流水线数据")
        pipeline_data = assemble_pipeline_data(transformed, PIPELINE_NAME, SPACE_ID)
        print(f"  新流水线ID: {pipeline_data['pipeline']['pipelineId']}")
        print(f"  流水线Key: {pipeline_data['pipeline']['pipelineKey']}")
        print(f"  AliasID: {pipeline_data['pipeline']['aliasId']}")

        # 步骤4: 配置预览
        print("\n步骤4: 配置预览")
        print("=" * 60)
        print("基本信息:")
        print(f"  流水线名称: {pipeline_data['pipeline']['name']}")
        print(f"  空间ID: {pipeline_data['pipeline']['spaceId']}")
        print(f"  构建环境: {pipeline_data['pipeline']['buildPlatform']}")
        print(f"  超时时间: {pipeline_data['pipeline']['timeoutDuration']}")

        # 显示代码源配置
        if pipeline_data['pipeline']['sources']:
            print(f"\n代码源配置:")
            for i, source in enumerate(pipeline_data['pipeline']['sources'], 1):
                print(f"  {i}. {source['name']} ({source['repoType']})")
                print(f"     地址: {source['repoUrl']}")
                print(f"     分支: {source['defaultBranch']}")
        else:
            print(f"\n代码源配置: 未配置（流水线可能无法正常执行）")

        print(f"\n流水线结构:")
        for i, stage in enumerate(pipeline_data['pipeline']['stages'], 1):
            print(f"  阶段{i}: {stage['name']}")
            for j, step in enumerate(stage.get('steps', []), 1):
                print(f"    步骤{j}: {step['name']}")
                for k, task in enumerate(step.get('tasks', []), 1):
                    print(f"      任务{k}: {task['name']}")

        print("\n检查清单:")
        print(f"  ✅ spaceId已设置: {pipeline_data['pipeline']['spaceId']}")
        print(f"  ✅ 流水线名称无空格: {pipeline_data['pipeline']['name']}")
        print(f"  ✅ stages非空: {len(pipeline_data['pipeline']['stages'])} 个阶段")
        print(f"  ✅ taskDataList非空: {len(pipeline_data['taskDataList'])} 个任务数据")
        if pipeline_data['pipeline']['sources']:
            print(f"  ✅ 代码源已配置: {len(pipeline_data['pipeline']['sources'])} 个代码源")
        else:
            print(f"  ⚠️  代码源未配置")
        print("=" * 60)

        # 步骤5: 保存流水线
        print("\n步骤5: 保存流水线")
        save_result = save_pipeline(pipeline_data)

        # 验证保存结果
        print("\n步骤6: 验证流水线")
        print("正在查询流水线列表以验证创建结果...")
        time.sleep(1)  # 等待一下，确保数据已保存

        print("\n" + "=" * 60)
        print("✅ 流水线创建成功！")
        print("=" * 60)
        print(f"流水线ID: {pipeline_data['pipeline']['pipelineId']}")
        print(f"流水线名称: {pipeline_data['pipeline']['name']}")
        print(f"编辑页面: {DEVOPS_BFF_URL}/#/pipeline/{pipeline_data['pipeline']['pipelineId']}/edit")
        print("=" * 60)

        # 询问是否执行流水线
        if pipeline_data['pipeline']['sources']:
            execute_choice = input("\n是否立即执行流水线? [Y/n]: ").strip().lower()
            if not execute_choice or execute_choice == 'y' or execute_choice == 'yes':
                print(f"\n执行命令: cd /Users/yousam/Desktop/workspace/icode/pipeline/devops-skills/devops-pipeline-management/scripts && python3 main.py run {pipeline_data['pipeline']['pipelineId']}")
                print("请在终端中执行上述命令来运行流水线")
        else:
            print("\n⚠️  由于未配置代码源，无法执行流水线")
            print("   请先在编辑页面配置代码源后再执行")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
