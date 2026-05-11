#!/usr/bin/env python3
"""
交互式执行模块
包含交互式执行流水线的完整流程
"""

import json
from typing import Dict, Any, List

from .utils import prompt_choice, prompt_input, confirm


class InteractiveRunMixin:
    """交互式执行混入类"""

    def _interactive_select_branch_tag(
        self,
        source_name: str,
        repo_type: str,
        repo_url: str,
        refs_type: str = "BRANCH",
        default_value: str = None
    ) -> tuple:
        """
        交互式选择分支/标签

        Args:
            source_name: 代码源名称
            repo_type: 仓库类型
            repo_url: 仓库地址
            refs_type: 引用类型 (BRANCH/TAG)
            default_value: 默认值

        Returns:
            (refs_type, refs_type_value) 元组
        """
        print(f"\n{'='*60}")
        print(f"代码源: {source_name}")
        print(f"仓库: {repo_url}")
        print(f"{'='*60}")

        # 1. 选择引用类型（分支/标签）
        type_options = [
            {"label": "分支 (BRANCH)", "value": "BRANCH"},
            {"label": "标签 (TAG)", "value": "TAG"}
        ]
        type_choice = prompt_choice("请选择引用类型:", type_options)
        if not type_choice:
            type_choice = {"value": refs_type or "BRANCH"}
        selected_refs_type = type_choice.get("value", "BRANCH")

        # 2. 获取分支/标签列表
        print(f"\n正在获取{selected_refs_type}列表...")
        try:
            result = self.get_repo_branch_and_tag_list(
                repo_type=repo_type,
                repo_url=repo_url,
                refs_type=selected_refs_type,
                search=default_value,
                page_num=1,
                page_size=50
            )

            # 解析响应
            if result.get('code') == 0 or result.get('code') == '0':
                data_list = result.get('data', [])
                if data_list and len(data_list) > 0:
                    # 响应是列表，取第一个元素
                    first_result = data_list[0] if isinstance(data_list, list) else data_list

                    # 根据类型获取对应的列表
                    if selected_refs_type == "BRANCH":
                        branch_data = first_result.get('branchListVO', {})
                        branch_page = branch_data.get('branchVOPage', {})
                        items = branch_page.get('data', [])
                    else:
                        tag_data = first_result.get('tagListVO', {})
                        tag_page = tag_data.get('tagVOPage', {})
                        items = tag_page.get('data', [])

                    if items:
                        # 构建选项列表
                        options = []
                        for item in items:
                            name = item.get('name', '')
                            commit_msg = item.get('commitMessage', '')[:50] if item.get('commitMessage') else ''
                            options.append({
                                "label": f"{name} - {commit_msg}" if commit_msg else name,
                                "value": name,
                                "commitId": item.get('commitId'),
                                "commitMessage": item.get('commitMessage')
                            })

                        # 查找默认值在列表中的位置
                        default_idx = 0
                        if default_value:
                            for i, opt in enumerate(options):
                                if opt.get("value") == default_value:
                                    default_idx = i
                                    break

                        # 让用户选择
                        choice = prompt_choice(
                            f"请选择{selected_refs_type}:",
                            options
                        )

                        if choice:
                            return selected_refs_type, choice.get("value"), choice.get("commitId"), choice.get("commitMessage")
                    else:
                        print(f"未找到可用的{selected_refs_type}")
        except Exception as e:
            print(f"获取{selected_refs_type}列表失败: {e}")

        # 3. 如果获取失败或没有选项，让用户手动输入
        print(f"\n请手动输入{selected_refs_type}名称:")
        manual_input = input(f"{selected_refs_type}名称 (默认: {default_value or 'master'}): ").strip()
        if not manual_input:
            manual_input = default_value or 'master'

        return selected_refs_type, manual_input, None, None

    def _interactive_select_package_version(
        self,
        source_name: str,
        repo_type: str,
        package_type: str = "DOCKER",
        image_name: str = None,
        normal_artifact_name: str = None,
        full_path: str = None,
        default_tag: str = None
    ) -> str:
        """
        交互式选择制品版本

        Args:
            source_name: 制品源名称
            repo_type: 仓库类型
            package_type: 制品类型 (DOCKER/NORMAL)
            image_name: 镜像名称 (DOCKER类型)
            normal_artifact_name: 制品名称 (NORMAL类型)
            full_path: 完整路径 (NORMAL类型)
            default_tag: 默认标签/版本

        Returns:
            选中的标签/版本
        """
        print(f"\n{'='*60}")
        print(f"制品源: {source_name}")
        print(f"类型: {package_type}")
        print(f"{'='*60}")

        # 获取版本列表
        print(f"\n正在获取版本列表...")
        try:
            if package_type == "DOCKER" or not package_type:
                result = self.query_image_tags(
                    repo_type=repo_type,
                    image_name=image_name,
                    search=default_tag,
                    page_num=1,
                    page_size=50
                )
                items = result.get('data', {}).get('data', [])
            else:
                result = self.query_package_versions(
                    repo_type=repo_type,
                    normal_artifact_name=normal_artifact_name,
                    full_path=full_path,
                    search=default_tag,
                    page_num=1,
                    page_size=50
                )
                items = result.get('data', {}).get('data', [])

            if items:
                # 构建选项列表
                options = []
                for item in items:
                    name = item.get('name', item.get('tagName', ''))
                    options.append({
                        "label": name,
                        "value": name
                    })

                # 查找默认值在列表中的位置
                default_idx = 0
                if default_tag:
                    for i, opt in enumerate(options):
                        if opt.get("value") == default_tag:
                            default_idx = i
                            break

                # 让用户选择
                choice = prompt_choice("请选择版本:", options)
                if choice:
                    return choice.get("value")
            else:
                print("未找到可用的版本")
        except Exception as e:
            print(f"获取版本列表失败: {e}")

        # 让用户手动输入
        print(f"\n请手动输入版本号:")
        manual_input = input(f"版本号 (默认: {default_tag or 'latest'}): ").strip()
        if not manual_input:
            manual_input = default_tag or 'latest'

        return manual_input

    def _interactive_assemble_run_sources(
        self,
        existing_sources: List[Dict],
        latest_selected_values: Dict = None,
        user_branch: str = None,
        user_refs_type: str = None
    ) -> List[Dict]:
        """
        交互式组装 runSources 数据

        Args:
            existing_sources: 流水线配置中的 sources
            latest_selected_values: 最近执行记录
            user_branch: 用户指定的分支（跳过交互）
            user_refs_type: 用户指定的引用类型

        Returns:
            组装好的 runSources 列表
        """
        assembled_sources = []

        for src in existing_sources:
            src_data = src.get('data', {})
            source_type = src_data.get('sourceType', 'code')

            if source_type == 'code':
                # 代码源
                if user_branch:
                    # 用户已指定分支，跳过交互
                    current_branch = user_branch
                    current_refs_type = user_refs_type or src_data.get('refsType', 'BRANCH')
                    commit_id = None
                    commit_msg = None
                else:
                    # 获取最近执行的值作为默认值
                    default_branch = src_data.get('branch', '')
                    default_refs_type = src_data.get('refsType', 'BRANCH')

                    if latest_selected_values and latest_selected_values.get('codeSourceResult'):
                        for code_result in latest_selected_values['codeSourceResult']:
                            code_param = code_result.get('codeSourceParam', {})
                            if (code_param.get('repoType') == src_data.get('repoType') and
                                code_param.get('repoUrl') == src_data.get('repoUrl') and
                                code_param.get('workPath') == src_data.get('workPath')):
                                if code_result.get('branchOrTag'):
                                    default_branch = code_result.get('branchOrTag')
                                if code_result.get('lastestCodeSourceParam', {}).get('refsType'):
                                    default_refs_type = code_result.get('lastestCodeSourceParam', {}).get('refsType')
                                break

                    # 交互式选择
                    print(f"\n>>> 代码源 [{src.get('name')}]")
                    should_interact = confirm("是否选择分支/标签?", default=False)

                    if should_interact:
                        current_refs_type, current_branch, commit_id, commit_msg = self._interactive_select_branch_tag(
                            source_name=src.get('name'),
                            repo_type=src_data.get('repoType'),
                            repo_url=src_data.get('repoUrl'),
                            refs_type=default_refs_type,
                            default_value=default_branch
                        )
                    else:
                        current_branch = default_branch
                        current_refs_type = default_refs_type
                        commit_id = None
                        commit_msg = None

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
                if commit_id:
                    new_src["data"]["commitId"] = commit_id
                if commit_msg:
                    new_src["data"]["commitMessage"] = commit_msg

                assembled_sources.append(new_src)

            elif source_type == 'package':
                # 制品源
                pkg_type = src_data.get('packageType', 'DOCKER')
                default_tag = src_data.get('defaultTag', '')

                # 获取最近执行的值
                if latest_selected_values and latest_selected_values.get('artifactResult'):
                    for artifact_result in latest_selected_values['artifactResult']:
                        artifact_param = artifact_result.get('artifactParam', {})
                        if artifact_param.get('workPath') == src_data.get('workPath'):
                            if artifact_result.get('lastestArtifactVersion'):
                                default_tag = artifact_result.get('lastestArtifactVersion')
                            break

                # 交互式选择
                print(f"\n>>> 制品源 [{src.get('name')}]")
                should_interact = confirm("是否选择版本?", default=False)

                if should_interact:
                    current_tag = self._interactive_select_package_version(
                        source_name=src.get('name'),
                        repo_type=src_data.get('repoType'),
                        package_type=pkg_type,
                        image_name=src_data.get('imageName'),
                        normal_artifact_name=src_data.get('normalArtifactName'),
                        full_path=src_data.get('fullPath'),
                        default_tag=default_tag
                    )
                else:
                    current_tag = default_tag

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

    # ==================== 交互式执行 ====================

    def interactive_run(self, pipeline_id: str) -> Dict[str, Any]:
        """
        交互式执行流水线 - 让用户选择执行方式

        流程:
        1. 选择执行方式：直接执行 / 自动填充上次配置 / 自主选择参数
        2. 如果直接执行：使用默认配置执行
        3. 如果自动填充：使用上次执行的配置
        4. 如果自主选择：逐步引导用户选择任务节点、代码源、制品源、自定义参数
        """
        # 获取流水线执行配置
        print(f"\n正在获取流水线 [{pipeline_id}] 的执行配置...")
        config_result = self.get_pipeline_for_run(pipeline_id)

        # 处理嵌套响应结构: { success, code, data: { code, data: {...} } }
        inner_code = config_result.get('data', {}).get('code')
        if inner_code != 0 and inner_code != '0':
            print(f"获取配置失败: {config_result.get('data', {}).get('message')}")
            return config_result

        config_data = config_result.get('data', {}).get('data', {})
        pipeline_info = config_data.get('pipeline', {})

        # 分离代码源和制品源
        all_sources = config_data.get('sources', [])
        code_sources = [s for s in all_sources if s.get('data', {}).get('sourceType') == 'code']
        package_sources = [s for s in all_sources if s.get('data', {}).get('sourceType') == 'package']

        # 获取最近一次执行配置
        latest_run_config = {}
        latest_pip_work = pipeline_info.get('latestPipWorkVO', {})
        if latest_pip_work:
            try:
                latest_run_config = json.loads(latest_pip_work.get('pipelineParams', '{}'))
            except:
                pass

        # ===== 第1步：选择执行方式 =====
        print("\n" + "=" * 50)
        print("请选择执行方式:")
        print("  1. 直接执行（按照默认配置）")
        print("  2. 自动填充上次配置（使用最近一次执行的分支/标签/版本）")
        print("  3. 自主选择参数（自定义任务节点、代码源、制品源、参数等）")
        print("=" * 50)

        exec_type = input("\n请选择执行方式 [1/2/3]: ").strip()

        # 增量传参数据
        run_sources = None
        selected_tasks = None
        custom_parameters = None
        auto_fill_run_config = False

        if exec_type == "1":
            # ===== 直接执行 =====
            print("\n[模式] 直接执行 - 使用默认配置执行流水线")
            # 不传任何增量参数，使用后端默认配置

        elif exec_type == "2":
            # ===== 自动填充上次配置 =====
            print("\n[模式] 自动填充上次配置")
            auto_fill_run_config = True
            # 后端会自动使用上次执行的配置

        elif exec_type == "3":
            # ===== 自主选择参数 =====
            print("\n[模式] 自主选择参数 - 逐步引导配置")

            # ----- 第2步：选择任务节点 -----
            task_list = config_data.get('taskList', [])
            if task_list:
                print("\n--- 可执行的任务节点 ---")
                for i, task in enumerate(task_list, 1):
                    task_name = task.get('name', task.get('taskId', 'Unknown'))
                    task_path = task.get('data', {}).get('workPath', '')
                    print(f"  {i}. {task_name} [{task_path}]" if task_path else f"  {i}. {task_name}")

                selected = input("\n请选择要执行的任务节点（输入序号，多个用逗号分隔，直接回车执行全部）: ").strip()
                if selected:
                    indices = [int(x.strip()) - 1 for x in selected.split(',') if x.strip().isdigit()]
                    selected_tasks = [task_list[i].get('taskId') for i in indices if 0 <= i < len(task_list)]
                    print(f"已选择任务: {selected_tasks}")

            # ----- 第3步：选择代码源 -----
            if code_sources:
                print("\n--- 代码源列表 ---")
                for i, src in enumerate(code_sources, 1):
                    src_data = src.get('data', {})
                    src_type = src_data.get('sourceType', 'code')
                    repo_type = src_data.get('repoType', 'N/A')
                    refs_type = src_data.get('refsType', 'BRANCH')
                    branch = src_data.get('branch', '')
                    repo_url = src_data.get('repoUrl', '')
                    work_path = src_data.get('workPath', '')
                    # 显示最近使用的值
                    recent_branch = latest_run_config.get('pipeline', {}).get('autoFillRunConfig', {}).get('runSourcesValues', [{}])[i-1].get('refsTypeValue', '') if latest_run_config else ''
                    print(f"  {i}. [{repo_type}] {refs_type}: {branch or '未设置'}")
                    if work_path:
                        print(f"     工作路径: {work_path}")
                    if recent_branch:
                        print(f"     上次使用: {recent_branch}")

                print("\n请为每个代码源选择分支/标签（直接回车使用当前值）:")
                run_sources = []
                for i, src in enumerate(code_sources):
                    src_data = src.copy()
                    data = src_data.get('data', {})

                    refs_type = data.get('refsType', 'BRANCH')
                    current_branch = data.get('branch', '')
                    work_path = data.get('workPath', '')
                    repo_url = data.get('repoUrl', '')
                    repo_type = data.get('repoType', '')

                    # 如果有上次配置，尝试回填
                    if latest_run_config:
                        run_sources_values = latest_run_config.get('pipeline', {}).get('autoFillRunConfig', {}).get('runSourcesValues', [])
                        for rv in run_sources_values:
                            if rv.get('data', {}).get('workPath') == work_path:
                                current_branch = rv.get('refsTypeValue', current_branch)
                                refs_type = rv.get('refsType', refs_type)
                                break

                    prompt = f"  代码源 {i+1} [{work_path or repo_url}]: "
                    default_val = current_branch

                    # 切换分支/标签类型
                    refs_type_prompt = f"    引用类型 (BRANCH/TAG) [{refs_type}]: "
                    user_refs_type = input(refs_type_prompt).strip().upper()
                    if user_refs_type in ('BRANCH', 'TAG'):
                        refs_type = user_refs_type

                    # 输入分支/标签值
                    user_val = input(prompt).strip()
                    refs_type_value = user_val if user_val else default_val

                    if refs_type_value:
                        run_sources.append({
                            "id": src.get('id'),
                            "name": src.get('name'),
                            "refsType": refs_type,
                            "refsTypeValue": refs_type_value,
                            "data": {
                                **data,
                                "branch": refs_type_value,
                                "refsType": refs_type
                            }
                        })
                    else:
                        print(f"    警告: 分支/标签不能为空，跳过此代码源")

                if not run_sources:
                    run_sources = None
                    print("  未设置任何代码源，将使用默认配置")

            # ----- 第4步：选择制品源 -----
            if package_sources:
                print("\n--- 制品源列表 ---")
                for i, pkg in enumerate(package_sources, 1):
                    pkg_data = pkg.get('data', {})
                    pkg_type = pkg_data.get('packageType', 'DOCKER')
                    work_path = pkg_data.get('workPath', '')

                    if pkg_type == 'DOCKER':
                        image_name = pkg_data.get('imageName', '')
                        default_tag = pkg_data.get('defaultTag', '')
                        print(f"  {i}. [Docker] {image_name}:{default_tag}")
                    else:
                        artifact_name = pkg_data.get('normalArtifactName', '')
                        full_path = pkg_data.get('fullPath', '')
                        print(f"  {i}. [制品] {artifact_name} -> {full_path}")

                    if work_path:
                        print(f"     工作路径: {work_path}")

                print("\n请为每个制品源设置版本标签（直接回车使用当前值）:")
                pkg_run_sources = []
                for i, pkg in enumerate(package_sources):
                    pkg_data = pkg.get('data', {})

                    pkg_type = pkg_data.get('packageType', 'DOCKER')
                    work_path = pkg_data.get('workPath', '')
                    current_tag = pkg_data.get('defaultTag', '')

                    # 如果有上次配置，尝试回填
                    if latest_run_config:
                        run_sources_values = latest_run_config.get('pipeline', {}).get('autoFillRunConfig', {}).get('runSourcesValues', [])
                        for rv in run_sources_values:
                            if rv.get('data', {}).get('workPath') == work_path and rv.get('data', {}).get('sourceType') == 'package':
                                current_tag = rv.get('data', {}).get('defaultTag', current_tag)
                                break

                    if pkg_type == 'DOCKER':
                        prompt = f"  制品源 {i+1} 镜像标签: "
                    else:
                        prompt = f"  制品源 {i+1} 版本号: "

                    user_val = input(prompt).strip()
                    default_tag = user_val if user_val else current_tag

                    if default_tag:
                        pkg_run_sources.append({
                            "id": pkg.get('id'),
                            "name": pkg_data.get('imageName') or pkg_data.get('normalArtifactName'),
                            "shortName": pkg_data.get('imageName') or pkg_data.get('normalArtifactName'),
                            "data": {
                                **pkg_data,
                                "defaultTag": default_tag,
                                "sourceType": "package",
                                "packageType": pkg_type
                            }
                        })

                # 合并代码源和制品源
                if run_sources and pkg_run_sources:
                    run_sources.extend(pkg_run_sources)
                elif pkg_run_sources:
                    run_sources = pkg_run_sources

            # ----- 第5步：自定义参数 -----
            custom_params_def = config_data.get('customParameters', [])
            if custom_params_def:
                print("\n--- 自定义参数 ---")
                custom_parameters = []
                for param in custom_params_def:
                    param_name = param.get('name', param.get('key', param.get('paramKey', '')))
                    param_type = param.get('type', 'string')
                    default_val = param.get('defaultValue', param.get('value', ''))
                    enum_value = param.get('enumValue', '')
                    param_desc = param.get('description', '')

                    prompt = f"  {param_name}"
                    if param_desc:
                        prompt += f" ({param_desc})"
                    if enum_value:
                        prompt += f" [可选值: {enum_value}]"
                    prompt += f" [默认值: {default_val}]: "

                    user_val = input(prompt).strip()
                    if user_val:
                        custom_parameters.append({
                            "name": param_name,
                            "type": param_type,
                            "defaultValue": user_val,
                            "runSet": True
                        })
                    elif default_val:
                        custom_parameters.append({
                            "name": param_name,
                            "type": param_type,
                            "defaultValue": default_val,
                            "runSet": param.get('runSet', False)
                        })

                if custom_parameters:
                    print(f"已设置自定义参数: {custom_parameters}")

            # ----- 第6步：确认执行 -----
            print("\n" + "=" * 50)
            print("执行配置汇总:")
            if selected_tasks:
                print(f"  任务节点: {selected_tasks}")
            else:
                print("  任务节点: 全部")
            if run_sources:
                code_srcs = [s for s in run_sources if s.get('data', {}).get('sourceType') != 'package']
                pkg_srcs = [s for s in run_sources if s.get('data', {}).get('sourceType') == 'package']
                if code_srcs:
                    print(f"  代码源: {len(code_srcs)} 个")
                    for s in code_srcs:
                        print(f"    - {s.get('name')}: {s.get('refsType')}={s.get('refsTypeValue')}")
                if pkg_srcs:
                    print(f"  制品源: {len(pkg_srcs)} 个")
                    for s in pkg_srcs:
                        tag = s.get('data', {}).get('defaultTag', '')
                        print(f"    - {s.get('name')}: {tag}")
            else:
                print("  代码源: 默认配置")
            if custom_parameters:
                print(f"  自定义参数: {custom_parameters}")
            else:
                print("  自定义参数: 默认配置")
            print("=" * 50)

            if not confirm("\n确认执行流水线?", default=True):
                print("已取消执行")
                return {"code": 400, "message": "用户取消执行"}

        else:
            print("无效选择，将使用默认配置执行")
            # 默认当作直接执行

        # 执行流水线
        print("\n正在执行流水线...")
        return self.run_pipeline(
            pipeline_id,
            selected_tasks=selected_tasks,
            run_sources=run_sources,
            custom_parameters=custom_parameters,
            auto_fill_run_config=auto_fill_run_config
        )
