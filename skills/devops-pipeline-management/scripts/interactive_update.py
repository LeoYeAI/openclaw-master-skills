#!/usr/bin/env python3
"""
交互式更新模块
包含交互式更新流水线的配置
"""

import json
from typing import Dict, Any, List

from .utils import prompt_choice, prompt_input, confirm


class InteractiveUpdateMixin:
    """交互式更新混入类"""

    def interactive_update(self, pipeline_id: str) -> Dict[str, Any]:
        """
        交互式更新流水线 - 引导用户逐步修改流水线配置

        流程:
        1. 获取当前流水线配置
        2. 展示当前配置
        3. 选择要修改的字段
        4. 逐个修改选中的字段
        5. 预览变更
        6. 确认保存
        """
        # ===== 第1步：获取当前配置 =====
        print(f"\n正在获取流水线 [{pipeline_id}] 的当前配置...")
        config_result = self.get_pipeline_detail(pipeline_id)

        # 处理嵌套响应结构: { success, code, data: { code, data: {...} } }
        inner_code = config_result.get('data', {}).get('code')
        if inner_code != 0 and inner_code != '0':
            print(f"获取配置失败: {config_result.get('data', {}).get('message')}")
            return config_result

        current_config = config_result.get('data', {}).get('data', {})
        pipeline_info = current_config.get('pipeline', {})

        if not pipeline_info:
            print("错误: 流水线配置为空或不存在")
            return {'code': -1, 'message': '流水线不存在或已被删除'}

        # 提取关键信息
        current_name = pipeline_info.get('name', '')
        current_space_id = pipeline_info.get('spaceId', '')
        current_sources = current_config.get('sources', [])
        current_trigger = pipeline_info.get('triggerInfo', {})
        current_timeout = pipeline_info.get('timeoutDuration', '2H')
        current_build_platform = pipeline_info.get('buildPlatform', 'linux')

        # 分离代码源和制品源
        code_sources = [s for s in current_sources if s.get('data', {}).get('sourceType') == 'code']
        package_sources = [s for s in current_sources if s.get('data', {}).get('sourceType') == 'package']

        # ===== 第2步：确认目标流水线 =====
        print("\n" + "=" * 60)
        print(f"已找到流水线: {current_name}")
        print(f"ID: {pipeline_id}")
        print(f"Space ID: {current_space_id}")
        print("=" * 60)

        if not confirm("\n是否确认要修改此流水线?", default=True):
            print("已取消操作")
            return {'code': 0, 'message': '用户取消操作'}

        # 修改记录
        modifications = {}
        # 当前配置快照（用于最终保存）
        new_config = {
            'pipelineId': pipeline_id,
            'name': current_name,
            'spaceId': current_space_id,
            'triggerInfo': current_trigger,
            'timeoutDuration': current_timeout,
            'buildPlatform': current_build_platform,
            'sources': json.loads(json.dumps(current_sources)),  # 深拷贝
            'stages': pipeline_info.get('stages', [])
        }

        # ===== 第3轮：选择要修改的内容 =====
        while True:
            print("\n" + "=" * 60)
            print("当前配置:")
            print("-" * 60)
            print(f"  1. 流水线名称: {new_config.get('name')}")
            print(f"  2. 代码源: {len(code_sources)} 个")
            for i, src in enumerate(code_sources, 1):
                src_data = src.get('data', {})
                branch = src_data.get('branch', '未设置')
                work_path = src_data.get('workPath', '')
                print(f"     [{i}] {src.get('name')} - {branch}" + (f" ({work_path})" if work_path else ""))
            print(f"  3. 制品源: {len(package_sources)} 个")
            for i, pkg in enumerate(package_sources, 1):
                pkg_data = pkg.get('data', {})
                pkg_type = pkg_data.get('packageType', 'DOCKER')
                tag = pkg_data.get('defaultTag', '未设置')
                work_path = pkg_data.get('workPath', '')
                if pkg_type == 'DOCKER':
                    print(f"     [{i}] Docker: {pkg_data.get('imageName')}:{tag}" + (f" ({work_path})" if work_path else ""))
                else:
                    print(f"     [{i}] 制品: {pkg_data.get('normalArtifactName')}:{tag}" + (f" ({work_path})" if work_path else ""))
            print(f"  4. 触发方式: {self._get_trigger_text(current_trigger)}")
            print(f"  5. 超时时间: {new_config.get('timeoutDuration')}")
            print(f"  6. 构建平台: {new_config.get('buildPlatform')}")
            print("-" * 60)
            print("\n请选择要修改的内容:")
            print("  1. 流水线名称")
            print("  2. 代码源（分支/标签）")
            print("  3. 制品源")
            print("  4. 触发方式")
            print("  5. 超时设置")
            print("  6. 构建平台")
            print("  7. 保存并完成")
            print("  8. 取消")
            print("=" * 60)

            choice = input("\n请选择 [1-8]: ").strip()

            if choice == "1":
                # 修改流水线名称
                new_name = input(f"当前名称: {new_config.get('name')}\n请输入新的流水线名称: ").strip()
                if new_name:
                    old_name = new_config.get('name')
                    new_config['name'] = new_name
                    modifications['name'] = {'old': old_name, 'new': new_name}
                    print(f"✓ 流水线名称已更新: {old_name} → {new_name}")

            elif choice == "2":
                # 修改代码源
                new_config['sources'] = self._interactive_update_sources(
                    code_sources, new_config.get('sources', [])
                )
                modifications['sources'] = {'old': '已修改', 'new': '已修改'}

            elif choice == "3":
                # 修改制品源
                new_config['sources'] = self._interactive_update_packages(
                    package_sources, new_config.get('sources', [])
                )
                modifications['packages'] = {'old': '已修改', 'new': '已修改'}

            elif choice == "4":
                # 修改触发方式
                new_trigger = self._interactive_update_trigger(current_trigger)
                new_config['triggerInfo'] = new_trigger
                modifications['trigger'] = {'old': current_trigger, 'new': new_trigger}
                current_trigger = new_trigger

            elif choice == "5":
                # 修改超时时间
                print(f"\n当前超时时间: {new_config.get('timeoutDuration')}")
                print("常用选项: 30M, 1H, 2H, 4H, 8H, 1D")
                new_timeout = input("请输入新的超时时间: ").strip()
                if new_timeout:
                    old_timeout = new_config.get('timeoutDuration')
                    new_config['timeoutDuration'] = new_timeout
                    modifications['timeout'] = {'old': old_timeout, 'new': new_timeout}
                    print(f"✓ 超时时间已更新: {old_timeout} → {new_timeout}")

            elif choice == "6":
                # 修改构建平台
                print(f"\n当前构建平台: {new_config.get('buildPlatform')}")
                print("  1. Linux")
                print("  2. Windows")
                platform_choice = input("请选择 [1-2]: ").strip()
                old_platform = new_config.get('buildPlatform')
                if platform_choice == "1":
                    new_config['buildPlatform'] = 'linux'
                elif platform_choice == "2":
                    new_config['buildPlatform'] = 'windows'
                if old_platform != new_config.get('buildPlatform'):
                    modifications['buildPlatform'] = {'old': old_platform, 'new': new_config.get('buildPlatform')}
                    print(f"✓ 构建平台已更新: {old_platform} → {new_config.get('buildPlatform')}")

            elif choice == "7":
                # 保存并完成
                break

            elif choice == "8":
                print("已取消操作")
                return {'code': 0, 'message': '用户取消操作'}

            else:
                print("无效选择，请重新输入")

        # ===== 第4步：预览变更 =====
        print("\n" + "=" * 60)
        print("变更汇总:")
        print("-" * 60)
        if not modifications:
            print("  无任何修改")
        else:
            for key, change in modifications.items():
                old_val = change.get('old', 'N/A')
                new_val = change.get('new', 'N/A')
                if isinstance(old_val, dict):
                    old_val = str(old_val)[:30] + "..."
                if isinstance(new_val, dict):
                    new_val = str(new_val)[:30] + "..."
                print(f"  {key}: {old_val} → {new_val}")
        print("=" * 60)

        if not confirm("\n是否确认保存?", default=True):
            print("已取消保存")
            return {'code': 0, 'message': '用户取消保存'}

        # ===== 第5步：保存更新 =====
        print("\n正在保存流水线配置...")
        result = self.update_pipeline(pipeline_id, new_config)

        if result.get('code') == 0 or result.get('code') == '0':
            print("\n✓ 流水线更新成功!")
            print(f"Pipeline ID: {pipeline_id}")
        else:
            print(f"\n✗ 更新失败: {result.get('message')}")

        return result

    def _interactive_update_sources(self, code_sources: List, current_sources: List) -> List:
        """交互式修改代码源"""
        if not code_sources:
            print("\n当前没有代码源")
            return current_sources

        while True:
            print("\n--- 代码源列表 ---")
            for i, src in enumerate(code_sources, 1):
                src_data = src.get('data', {})
                branch = src_data.get('branch', '未设置')
                refs_type = src_data.get('refsType', 'BRANCH')
                work_path = src_data.get('workPath', '')
                print(f"  {i}. {src.get('name')} [{refs_type}: {branch}]" + (f" - {work_path}" if work_path else ""))

            print(f"  {len(code_sources) + 1}. 返回上级")

            choice = input("\n请选择要修改的代码源: ").strip()
            if not choice:
                continue

            try:
                idx = int(choice) - 1
                if idx == len(code_sources):
                    break
                if 0 <= idx < len(code_sources):
                    src = code_sources[idx]
                    src_data = src.get('data', {})

                    print(f"\n当前分支: {src_data.get('branch')}")
                    print("提示: 输入空直接回车跳过")

                    # 切换 refsType
                    current_refs_type = src_data.get('refsType', 'BRANCH')
                    refs_input = input(f"引用类型 (BRANCH/TAG) [{current_refs_type}]: ").strip().upper()
                    if refs_input in ('BRANCH', 'TAG'):
                        src_data['refsType'] = refs_input

                    # 输入新分支/标签
                    new_branch = input("请输入新的分支/标签名称: ").strip()
                    if new_branch:
                        src_data['branch'] = new_branch
                        print(f"✓ 已更新: {new_branch}")

                    # 更新 current_sources 中的对应项
                    for i, s in enumerate(current_sources):
                        if s.get('id') == src.get('id'):
                            current_sources[i] = src
                            break
            except ValueError:
                print("请输入有效的数字")

        return current_sources

    def _interactive_update_packages(self, package_sources: List, current_sources: List) -> List:
        """交互式修改制品源"""
        if not package_sources:
            print("\n当前没有制品源")
            return current_sources

        while True:
            print("\n--- 制品源列表 ---")
            for i, pkg in enumerate(package_sources, 1):
                pkg_data = pkg.get('data', {})
                pkg_type = pkg_data.get('packageType', 'DOCKER')
                if pkg_type == 'DOCKER':
                    tag = pkg_data.get('defaultTag', '未设置')
                    print(f"  {i}. Docker: {pkg_data.get('imageName')}:{tag}")
                else:
                    tag = pkg_data.get('defaultTag', '未设置')
                    print(f"  {i}. 制品: {pkg_data.get('normalArtifactName')}:{tag}")

            print(f"  {len(package_sources) + 1}. 返回上级")

            choice = input("\n请选择要修改的制品源: ").strip()
            if not choice:
                continue

            try:
                idx = int(choice) - 1
                if idx == len(package_sources):
                    break
                if 0 <= idx < len(package_sources):
                    pkg = package_sources[idx]
                    pkg_data = pkg.get('data', {})
                    pkg_type = pkg_data.get('packageType', 'DOCKER')

                    print(f"\n当前标签: {pkg_data.get('defaultTag')}")

                    new_tag = input("请输入新的标签/版本: ").strip()
                    if new_tag:
                        pkg_data['defaultTag'] = new_tag
                        print(f"✓ 已更新: {new_tag}")

                    # 更新 current_sources 中的对应项
                    for i, s in enumerate(current_sources):
                        if s.get('id') == pkg.get('id'):
                            current_sources[i] = pkg
                            break
            except ValueError:
                print("请输入有效的数字")

        return current_sources

    def _interactive_update_trigger(self, current_trigger: Dict) -> Dict:
        """交互式修改触发方式"""
        print("\n--- 触发方式 ---")
        print("  1. 手动触发")
        print("  2. 定时触发")
        print("  3. Webhook 触发")

        choice = input("请选择 [1-3]: ").strip()

        if choice == "1":
            return {'triggerType': 0}
        elif choice == "2":
            print("\n当前: 无定时配置")
            cron = input("请输入 Cron 表达式 (如: 0 0 2 * * ?): ").strip()
            if cron:
                return {
                    'triggerType': 1,
                    'triggerParams': {'cron': cron}
                }
            return {'triggerType': 1}
        elif choice == "3":
            return {'triggerType': 2}
        else:
            return current_trigger
