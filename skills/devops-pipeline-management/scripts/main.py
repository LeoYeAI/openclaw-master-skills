#!/usr/bin/env python3
"""
DevOps Pipeline Management
流水线管理客户端 - AppKey签名认证

功能：
- 流水线列表查询 (list)
- 流水线详情查询 (detail)
- 流水线创建 (create)
- 流水线执行 (run)
- 流水线取消 (cancel)
- 流水线删除 (delete)
- 流水线执行详情 (run-detail)
"""

import os
import sys
import json

# 确保 scripts 目录在 Python 路径中，支持直接运行和模块运行
_script_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_script_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# 交互模式标志
INTERACTIVE_MODE = os.getenv('INTERACTIVE_MODE', 'true').lower() == 'true'

# 导入各功能模块
from scripts.utils import prompt_choice, prompt_input, confirm
from scripts import PipelineClient


def main():
    """CLI入口函数"""
    if len(sys.argv) < 2:
        print("Usage: python -m scripts/main <command> [args]")
        print("\nCommands:")
        print("  list <pipeline_id> [options]       # 查询流水线执行记录")
        print("  detail <pipeline_id>              # 获取流水线详情")
        print("  save [options]                    # 保存流水线（创建或更新）")
        print("  run <pipeline_id> [options]        # 执行流水线")
        print("  cancel <pipeline_log_id>           # 取消流水线（使用执行记录ID）")
        print("  delete <pipeline_id>               # 删除流水线")
        print("  run-detail <pipeline_log_id>      # 获取执行详情（使用执行记录ID）")
        print("  templates <space_id> [options]     # 查询流水线模板")
        print("  pipelines <space_id> [options]     # 查询流水线列表")
        print("  workspaces [options]               # 查询工作空间列表")
        print("\nOpenAPI接口说明:")
        print("  Base URL: /api/ai-bff/openapi/pipeline")
        print("  - POST /api/ai-bff/rest/openapi/pipeline/save                   # 保存流水线")
        print("  - POST /api/ai-bff/rest/openapi/pipeline/runByManual            # 执行流水线")
        print("  - GET  /api/ai-bff/rest/openapi/pipeline/edit?pipelineId=xxx   # 获取流水线配置")
        print("  - POST /api/ai-bff/rest/openapi/pipeline/cancel                # 取消流水线")
        print("  - POST /api/ai-bff/rest/openapi/pipeline/delete                 # 删除流水线")
        print("  - GET  /api/ai-bff/rest/openapi/pipeline/queryPipelineWorkPage  # 查询执行记录")
        print("  - GET  /api/ai-bff/rest/openapi/pipeline/getPipelineWorkById    # 查询执行详情")
        print("  - POST /api/ai-bff/rest/openapi/pipeline/queryPipelinePage      # 查询流水线列表")
        print("  - POST /api/ai-bff/rest/openapi/pipeline/queryPipelineTemplatePage  # 查询流水线模板")
        print("\n保存参数（save命令）:")
        print("  --config <json_string>            # 流水线配置JSON字符串")
        print("  --file <json_file_path>           # 流水线配置JSON文件路径")
        print("  --task-data <json_string>         # 任务数据JSON字符串（可选）")
        print("  --task-data-file <json_file_path> # 任务数据JSON文件路径（可选）")
        print("\n执行参数（run命令）:")
        print("  --branch <branch>                 # 指定分支")
        print("  --tasks <task1,task2,...>         # 指定要执行的任务节点（逗号分隔）")
        print("  --sources <json>                  # 代码源JSON数组")
        print("  --params <json>                   # 自定义参数JSON数组")
        print("  --auto-fill                       # 自动填充上次运行配置")
        print("  --re-run                          # 重新执行")
        print("  --remark <text>                   # 执行备注")
        print("  --interactive                     # 强制进入交互模式")
        print("  --non-interactive                 # 强制使用直接执行模式")
        print("\n执行参数（templates/pipelines命令）:")
        print("  --name <name>                      # 名称搜索关键字")
        print("  --type <type>                      # 模板类型")
        print("  --language <lang>                  # 模板语言（java/python/nodejs/go/dotnet/frontend/common）")
        print("  --account <account>                # 当前登录账号")
        print("  --page <num>                       # 页码")
        print("  --size <size>                      # 每页大小")
        print("\n执行参数（workspaces命令）:")
        print("  --name <name>                      # 工作空间名称（模糊搜索）")
        print("  --division <name>                  # 一级组织名称")
        print("  --team <name>                      # 产品线名称")
        print("  --project-code <code>              # 项目编码")
        print("  --page <num>                       # 页码")
        print("  --size <size>                      # 每页大小")
        print("\n示例:")
        print("  # 查询执行记录")
        print("  python -m scripts/main list pipe-abc123")
        print("  python -m scripts/main list pipe-abc123 --page 1 --size 20")
        print("\n  # 执行流水线")
        print("  python -m scripts/main run pipe-abc123")
        print("  python -m scripts/main run pipe-abc123 --branch main")
        print("  python -m scripts/main run pipe-abc123 --tasks task-1,task-2")
        print("\n  # 取消/查看执行详情（使用pipeline_log_id）")
        print("  python -m scripts/main cancel 10001")
        print("  python -m scripts/main run-detail 10001")
        print("\n  # 查询流水线模板")
        print("  python -m scripts/main templates 1001")
        print("  python -m scripts/main templates 1001 --name Java --language java --page 1 --size 10")
        print("\n  # 查询工作空间列表")
        print("  python -m scripts/main workspaces")
        print("  python -m scripts/main workspaces --name devops")
        print("  python -m scripts/main workspaces --division '研发中心' --page 1 --size 10")
        print("\n  # 保存流水线")
        print("  python -m scripts/main save --config '{\"pipelineId\": \"pipe-abc123\", \"name\": \"my-pipeline\", \"spaceId\": 1001}'")
        print("  python -m scripts/main save --file pipeline-config.json")
        print("\n  # 查询流水线列表")
        print("  python -m scripts/main pipelines 1001")
        print("  python -m scripts/main pipelines 1001 --name 构建")
        print("\n必填环境变量:")
        print("  DEVOPS_DOMAIN_ACCOUNT             # 域账号（用于权限校验）")
        print("  DEVOPS_BFF_URL                    # BFF服务地址")
        print("\n可选环境变量:")
        print("  INTERACTIVE_MODE=false            # 禁用交互模式")
        print("\n配置示例:")
        print("  export DEVOPS_DOMAIN_ACCOUNT=\"your_domain_account\"")
        print("  export DEVOPS_BFF_URL=\"https://one-dev.iflytek.com/devops\"")
        sys.exit(1)

    try:
        client = PipelineClient()
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]

    if command == 'list':
        if len(sys.argv) < 3:
            print("Error: pipeline_id is required", file=sys.stderr)
            sys.exit(1)
        pipeline_id = sys.argv[2]
        page_num = 1
        page_size = 10
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == '--page' and i + 1 < len(sys.argv):
                page_num = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == '--size' and i + 1 < len(sys.argv):
                page_size = int(sys.argv[i + 1])
                i += 2
            else:
                i += 1
        result = client.get_pipeline_list(pipeline_id, page_num, page_size)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == 'detail':
        if len(sys.argv) < 3:
            print("Error: pipeline_id is required", file=sys.stderr)
            sys.exit(1)
        result = client.get_pipeline_detail(sys.argv[2])
        print(json.dumps(result, indent=2, ensure_ascii=False))


    elif command == 'save':
        # 保存流水线命令
        # 用法: save --config <json_string> 或 save --file <json_file_path>
        config_json = None
        task_data_list = None
        i = 2
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == '--config' and i + 1 < len(sys.argv):
                config_json = json.loads(sys.argv[i + 1])
                i += 2
            elif arg == '--file' and i + 1 < len(sys.argv):
                file_path = sys.argv[i + 1]
                with open(file_path, 'r', encoding='utf-8') as f:
                    config_json = json.load(f)
                i += 2
            elif arg == '--task-data' and i + 1 < len(sys.argv):
                task_data_list = json.loads(sys.argv[i + 1])
                i += 2
            elif arg == '--task-data-file' and i + 1 < len(sys.argv):
                task_data_file = sys.argv[i + 1]
                with open(task_data_file, 'r', encoding='utf-8') as f:
                    task_data_list = json.load(f)
                i += 2
            else:
                print(f"Error: unknown argument {arg}", file=sys.stderr)
                sys.exit(1)

        if config_json is None:
            print("Error: either --config or --file must be provided", file=sys.stderr)
            sys.exit(1)

        # 调用save_pipeline方法
        result = client.save_pipeline(config_json, task_data_list)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == 'run':
        if len(sys.argv) < 3:
            print("Error: pipeline_id is required", file=sys.stderr)
            sys.exit(1)

        pipeline_id = sys.argv[2]

        # 解析可选参数
        branch = None
        selected_tasks = None
        run_sources = None
        custom_parameters = None
        auto_fill_run_config = False
        re_run_flag = 0
        run_remark = None

        i = 3
        has_explicit_params = False

        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == '--branch' and i + 1 < len(sys.argv):
                branch = sys.argv[i + 1]
                has_explicit_params = True
                i += 2
            elif arg == '--tasks' and i + 1 < len(sys.argv):
                selected_tasks = sys.argv[i + 1].split(',')
                has_explicit_params = True
                i += 2
            elif arg == '--sources' and i + 1 < len(sys.argv):
                run_sources = json.loads(sys.argv[i + 1])
                has_explicit_params = True
                i += 2
            elif arg == '--params' and i + 1 < len(sys.argv):
                custom_parameters = json.loads(sys.argv[i + 1])
                has_explicit_params = True
                i += 2
            elif arg == '--auto-fill':
                auto_fill_run_config = True
                has_explicit_params = True
                i += 1
            elif arg == '--re-run':
                re_run_flag = 1
                has_explicit_params = True
                i += 1
            elif arg == '--remark' and i + 1 < len(sys.argv):
                run_remark = sys.argv[i + 1]
                has_explicit_params = True
                i += 2
            elif arg == '--interactive':
                has_explicit_params = False
                i += 1
            elif arg == '--non-interactive':
                has_explicit_params = True
                i += 1
            else:
                if i == 3 and not arg.startswith('--'):
                    branch = arg
                    has_explicit_params = True
                i += 1

        if not has_explicit_params and INTERACTIVE_MODE:
            result = client.interactive_run(pipeline_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            result = client.run_pipeline(
                pipeline_id,
                branch=branch,
                selected_tasks=selected_tasks,
                run_sources=run_sources,
                custom_parameters=custom_parameters,
                auto_fill_run_config=auto_fill_run_config,
                re_run_flag=re_run_flag,
                run_remark=run_remark
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == 'cancel':
        if len(sys.argv) < 3:
            print("Error: pipeline_log_id is required", file=sys.stderr)
            sys.exit(1)
        pipeline_log_id = int(sys.argv[2])
        result = client.cancel_pipeline(pipeline_log_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == 'delete':
        if len(sys.argv) < 3:
            print("Error: pipeline_id is required", file=sys.stderr)
            sys.exit(1)
        result = client.delete_pipeline(sys.argv[2])
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == 'run-detail':
        if len(sys.argv) < 3:
            print("Error: pipeline_log_id is required", file=sys.stderr)
            sys.exit(1)
        pipeline_log_id = int(sys.argv[2])
        result = client.get_run_detail(pipeline_log_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == 'templates':
        # 查询流水线模板
        if len(sys.argv) < 3:
            print("Error: space_id is required", file=sys.stderr)
            sys.exit(1)
        space_id = int(sys.argv[2])

        template_name = None
        template_type = None
        template_language = None
        account = None
        page_no = 1
        page_size = 10

        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == '--name' and i + 1 < len(sys.argv):
                template_name = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--type' and i + 1 < len(sys.argv):
                template_type = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--language' and i + 1 < len(sys.argv):
                template_language = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--account' and i + 1 < len(sys.argv):
                account = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--page' and i + 1 < len(sys.argv):
                page_no = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == '--size' and i + 1 < len(sys.argv):
                page_size = int(sys.argv[i + 1])
                i += 2
            else:
                i += 1

        result = client.list_pipeline_templates(
            space_id,
            template_name=template_name,
            template_type=template_type,
            template_language=template_language,
            account=account,
            page_no=page_no,
            page_size=page_size
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == 'pipelines':
        # 查询流水线列表
        if len(sys.argv) < 3:
            print("Error: space_id is required", file=sys.stderr)
            sys.exit(1)
        space_id = int(sys.argv[2])

        pipeline_name = None
        query_flag = 0
        page_num = 1
        page_size = 10

        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == '--name' and i + 1 < len(sys.argv):
                pipeline_name = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--flag' and i + 1 < len(sys.argv):
                query_flag = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == '--page' and i + 1 < len(sys.argv):
                page_num = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == '--size' and i + 1 < len(sys.argv):
                page_size = int(sys.argv[i + 1])
                i += 2
            else:
                i += 1

        result = client.list_pipelines(
            space_id,
            pipeline_name=pipeline_name,
            query_flag=query_flag,
            page_num=page_num,
            page_size=page_size
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == 'workspaces':
        # 分页查询工作空间列表
        workspace_name = None
        pomp_project_code = None
        division_name = None
        team_name = None
        page_num = 1
        page_size = 10

        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == '--name' and i + 1 < len(sys.argv):
                workspace_name = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--project-code' and i + 1 < len(sys.argv):
                pomp_project_code = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--division' and i + 1 < len(sys.argv):
                division_name = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--team' and i + 1 < len(sys.argv):
                team_name = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--page' and i + 1 < len(sys.argv):
                page_num = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == '--size' and i + 1 < len(sys.argv):
                page_size = int(sys.argv[i + 1])
                i += 2
            else:
                i += 1

        result = client.query_workspace_page(
            workspace_name=workspace_name,
            pomp_project_code=pomp_project_code,
            division_name=division_name,
            team_name=team_name,
            page_num=page_num,
            page_size=page_size
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
