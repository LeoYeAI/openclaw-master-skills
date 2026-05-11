#!/usr/bin/env python3
"""
认知架构洞察组件 V2 帮助查看器（精简版）
专注于快速查询
"""

import sys
import os

# 添加 scripts 目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from cognitive_insight_help import CognitiveInsightHelp, show_help


def print_menu():
    """打印菜单"""
    print("=" * 80)
    print("认知架构洞察组件 V2 帮助查看器")
    print("=" * 80)
    print()
    print("请选择操作:")
    print("  1. 查看完整帮助")
    print("  2. 查看 API 参考")
    print("  3. 查看常见问题 (FAQ)")
    print("  4. 查看故障排查")
    print("  5. 查看版本信息")
    print("  0. 退出")
    print()


def show_api_reference(helper: CognitiveInsightHelp):
    """显示 API 参考"""
    print("\n" + "=" * 80)
    print("API 参考")
    print("=" * 80 + "\n")
    
    api_ref = helper.get_help()['api_reference']
    
    for class_name, class_info in api_ref.items():
        print(f"【{class_name}】")
        print()
        
        if '描述' in class_info:
            print(f"  {class_info['描述']}")
            print()
        
        if '初始化' in class_info:
            print("  初始化:")
            init_info = class_info['初始化']
            print(f"    方法: {init_info['方法']}")
            print(f"    参数:")
            for param, desc in init_info['参数'].items():
                print(f"      {param}: {desc}")
            print(f"    返回: {init_info['返回']}")
            print()
        
        if '核心方法' in class_info:
            print("  核心方法:")
            for method_info in class_info['核心方法']:
                print(f"    方法: {method_info['方法']}")
                print(f"    描述: {method_info['描述']}")
                if '参数' in method_info:
                    print(f"    参数:")
                    for param, desc in method_info['参数'].items():
                        print(f"      {param}: {desc}")
                if '返回' in method_info:
                    print(f"    返回: {method_info['返回']}")
                print()
        
        print()
    
    input("\n按 Enter 键返回菜单...")


def show_faq(helper: CognitiveInsightHelp):
    """显示常见问题"""
    print("\n" + "=" * 80)
    print("常见问题 (FAQ)")
    print("=" * 80 + "\n")
    
    faq = helper.get_help()['faq']
    
    for item in faq:
        print(item['问题'])
        print(item['回答'])
        print()
    
    input("\n按 Enter 键返回菜单...")


def show_troubleshooting(helper: CognitiveInsightHelp):
    """显示故障排查"""
    print("\n" + "=" * 80)
    print("故障排查")
    print("=" * 80 + "\n")
    
    troubleshooting = helper.get_help()['troubleshooting']
    
    for idx, issue in enumerate(troubleshooting['常见问题'], 1):
        print(f"{idx}. {issue['问题']}")
        print()
        print("  可能原因:")
        for cause in issue['可能原因']:
            print(f"    • {cause}")
        print()
        print("  解决方案:")
        for solution in issue['解决方案']:
            print(f"    • {solution}")
        print()
        print("-" * 80)
        print()
    
    input("\n按 Enter 键返回菜单...")


def show_version_info(helper: CognitiveInsightHelp):
    """显示版本信息"""
    print("\n" + "=" * 80)
    print("版本信息")
    print("=" * 80 + "\n")
    
    help_data = helper.get_help()
    
    print(f"版本: {help_data['version']}")
    print(f"作者: {help_data['author']}")
    print(f"协议: {help_data['license']}")
    print()
    print(help_data['description'])
    
    input("\n按 Enter 键返回菜单...")


def main():
    """主函数"""
    helper = CognitiveInsightHelp()
    
    while True:
        print_menu()
        
        choice = input("请输入选项 (0-5): ").strip()
        
        if choice == '0':
            print("\n感谢使用认知架构洞察组件 V2 帮助查看器！")
            break
        elif choice == '1':
            helper.print_help()
            input("\n按 Enter 键返回菜单...")
        elif choice == '2':
            show_api_reference(helper)
        elif choice == '3':
            show_faq(helper)
        elif choice == '4':
            show_troubleshooting(helper)
        elif choice == '5':
            show_version_info(helper)
        else:
            print("\n无效选项，请重新输入！")
            input("\n按 Enter 键继续...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n感谢使用认知架构洞察组件 V2 帮助查看器！")
    except Exception as e:
        print(f"\n发生错误: {e}")
        sys.exit(1)
