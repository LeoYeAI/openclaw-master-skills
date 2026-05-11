#!/usr/bin/env python3
"""
TRAE Orchestrator 控制面板
交互式命令行界面，用于控制 TRAE 项目
"""
import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from automation_helper import (
    TRAEController,
    ProjectManager,
    ProgressMonitor,
    quick_start,
    pause_project,
    resume_project,
    stop_project
)


def print_header():
    """打印标题"""
    print("\n" + "=" * 60)
    print("🔥 TRAE Orchestrator 控制面板")
    print("=" * 60)


def print_menu():
    """打印主菜单"""
    print("\n📋 主菜单:")
    print("-" * 40)
    print("[1] 🚀 快速启动新项目")
    print("[2] 📁 创建项目结构")
    print("[3] 🎮 启动 TRAE IDE")
    print("[4] 📊 查看项目进度")
    print("[5] ⏸️  暂停项目")
    print("[6] ▶️  恢复项目")
    print("[7] ⏹️  停止项目")
    print("[8] ⚙️  设置 TRAE 路径")
    print("[0] ❌ 退出")
    print("-" * 40)


def quick_start_project():
    """快速启动项目"""
    print("\n🚀 快速启动新项目")
    print("-" * 40)
    
    project_dir = input("项目目录 (例如 D:\\MyProject): ").strip()
    if not project_dir:
        print("❌ 目录不能为空")
        return
    
    project_name = input("项目名称: ").strip() or "My Project"
    description = input("项目描述: ").strip() or "A cool project"
    
    print("\n功能列表 (用逗号分隔，例如: 登录,注册,聊天):")
    features_input = input("功能: ").strip()
    features = [f.strip() for f in features_input.split(",") if f.strip()]
    
    tech_stack = input("技术栈 (例如: React + Node.js): ").strip() or "HTML + CSS + JS"
    
    print("\n" + "-" * 40)
    print("确认信息:")
    print(f"  目录: {project_dir}")
    print(f"  名称: {project_name}")
    print(f"  描述: {description}")
    print(f"  功能: {', '.join(features)}")
    print(f"  技术: {tech_stack}")
    print("-" * 40)
    
    confirm = input("确认启动? (y/n): ").strip().lower()
    if confirm == 'y':
        try:
            quick_start(
                project_dir=project_dir,
                requirements={
                    'name': project_name,
                    'description': description,
                    'features': features,
                    'tech_stack': tech_stack
                }
            )
            print("\n✅ 项目已启动！")
        except Exception as e:
            print(f"\n❌ 错误: {e}")
    else:
        print("\n已取消")


def create_project_structure():
    """创建项目结构"""
    print("\n📁 创建项目结构")
    print("-" * 40)
    
    project_dir = input("项目目录: ").strip()
    if not project_dir:
        print("❌ 目录不能为空")
        return
    
    project_name = input("项目名称: ").strip() or "My Project"
    
    try:
        ProjectManager.create_project(
            project_dir=project_dir,
            requirements={
                'name': project_name,
                'description': 'Created via control panel'
            }
        )
        print(f"\n✅ 项目结构已创建: {project_dir}")
    except Exception as e:
        print(f"\n❌ 错误: {e}")


def launch_trae_ide():
    """启动 TRAE IDE"""
    print("\n🎮 启动 TRAE IDE")
    print("-" * 40)
    
    project_dir = input("项目目录 (可选，直接回车只启动TRAE): ").strip()
    
    controller = TRAEController()
    
    if not controller.trae_path:
        print("❌ 找不到 TRAE，请先设置路径")
        return
    
    try:
        if project_dir:
            controller.launch(project_dir)
            print(f"\n✅ TRAE 已启动，打开项目: {project_dir}")
        else:
            controller.launch()
            print("\n✅ TRAE 已启动")
    except Exception as e:
        print(f"\n❌ 错误: {e}")


def view_progress():
    """查看项目进度"""
    print("\n📊 查看项目进度")
    print("-" * 40)
    
    project_dir = input("项目目录: ").strip()
    if not project_dir:
        print("❌ 目录不能为空")
        return
    
    if not os.path.exists(project_dir):
        print(f"❌ 目录不存在: {project_dir}")
        return
    
    monitor = ProgressMonitor(project_dir)
    status = monitor.get_status()
    
    print("\n项目状态:")
    print(f"  目录: {status['project_dir']}")
    print(f"\n信号状态:")
    for signal, exists in status['signals'].items():
        icon = "✅" if exists else "❌"
        print(f"  {icon} {signal}")
    
    if status['progress']:
        print(f"\n进度摘要:")
        print(status['progress'][:300] + "...")
    else:
        print("\n暂无进度信息")


def control_project(action):
    """控制项目"""
    print(f"\n{'⏸️ 暂停' if action == 'pause' else '▶️ 恢复' if action == 'resume' else '⏹️ 停止'} 项目")
    print("-" * 40)
    
    project_dir = input("项目目录: ").strip()
    if not project_dir:
        print("❌ 目录不能为空")
        return
    
    try:
        if action == 'pause':
            pause_project(project_dir)
        elif action == 'resume':
            resume_project(project_dir)
        elif action == 'stop':
            stop_project(project_dir)
    except Exception as e:
        print(f"\n❌ 错误: {e}")


def setup_trae_path():
    """设置 TRAE 路径"""
    print("\n⚙️  设置 TRAE 路径")
    print("-" * 40)
    
    print("常见路径:")
    print("  C:\\Users\\<用户名>\\AppData\\Local\\Programs\\Trae CN\\Trae CN.exe")
    print("  E:\\software\\Trae CN\\Trae CN.exe")
    print()
    
    trae_path = input("TRAE 可执行文件路径: ").strip()
    if not trae_path:
        print("❌ 路径不能为空")
        return
    
    if not os.path.exists(trae_path):
        print(f"⚠️  警告: 文件不存在: {trae_path}")
        confirm = input("仍要保存? (y/n): ").strip().lower()
        if confirm != 'y':
            return
    
    try:
        controller = TRAEController()
        controller.setup(trae_path)
        print(f"\n✅ TRAE 路径已设置")
    except Exception as e:
        print(f"\n❌ 错误: {e}")


def main():
    """主函数"""
    print_header()
    
    # 检查 automation_helper 是否可用
    try:
        controller = TRAEController()
        if controller.trae_path:
            print(f"✅ TRAE 路径: {controller.trae_path}")
        else:
            print("⚠️  TRAE 路径未设置，请选择 [8] 进行设置")
    except Exception as e:
        print(f"⚠️  初始化警告: {e}")
    
    while True:
        print_menu()
        choice = input("\n选择操作 (0-8): ").strip()
        
        if choice == '1':
            quick_start_project()
        elif choice == '2':
            create_project_structure()
        elif choice == '3':
            launch_trae_ide()
        elif choice == '4':
            view_progress()
        elif choice == '5':
            control_project('pause')
        elif choice == '6':
            control_project('resume')
        elif choice == '7':
            control_project('stop')
        elif choice == '8':
            setup_trae_path()
        elif choice == '0':
            print("\n👋 再见！")
            break
        else:
            print("\n❌ 无效选择，请重试")
        
        input("\n按 Enter 继续...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 已退出")
        sys.exit(0)
