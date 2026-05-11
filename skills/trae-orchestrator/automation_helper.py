#!/usr/bin/env python3
"""
TRAE 自动化助手 - 实用的自动化控制函数
"""
import os
import subprocess
import time
import json
from datetime import datetime

# 可选依赖，如果未安装会给出友好提示
try:
    import pyautogui
    import pyperclip
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

class TRAEController:
    """TRAE IDE 控制器"""
    
    def __init__(self, trae_path=None):
        self.trae_path = trae_path or self._find_trae()
        self.config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        self.config = self._load_config()
        
    def _find_trae(self):
        """自动查找 TRAE 安装路径"""
        possible_paths = [
            r"C:\Users\{}\AppData\Local\Programs\Trae CN\Trae CN.exe",
            r"C:\Program Files\Trae\Trae.exe",
            r"E:\software\Trae CN\Trae CN.exe",
            r"D:\Program Files\Trae\Trae.exe",
        ]
        
        username = os.environ.get('USERNAME', os.environ.get('USER', ''))
        
        for path_template in possible_paths:
            path = path_template.format(username)
            if os.path.exists(path):
                return path
                
        return None
    
    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_config(self, config):
        """保存配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def setup(self, trae_path=None):
        """首次设置 TRAE 路径"""
        if trae_path:
            self.trae_path = trae_path
        
        if not self.trae_path:
            print("❌ 找不到 TRAE，请提供安装路径")
            print("例如: E:\\software\\Trae CN\\Trae CN.exe")
            return False
            
        if not os.path.exists(self.trae_path):
            print(f"❌ 路径不存在: {self.trae_path}")
            return False
            
        # 保存配置
        self.config['trae_path'] = self.trae_path
        self.save_config(self.config)
        
        print(f"✅ TRAE 路径已设置: {self.trae_path}")
        return True
    
    def launch(self, project_path=None):
        """启动 TRAE"""
        if not self.trae_path:
            print("❌ TRAE 路径未设置，请先运行 setup()")
            return False
            
        if not os.path.exists(self.trae_path):
            print(f"❌ 找不到 TRAE: {self.trae_path}")
            return False
        
        cmd = [self.trae_path]
        if project_path:
            cmd.append(project_path)
            
        print(f"🚀 启动 TRAE...")
        if project_path:
            print(f"   项目: {project_path}")
            
        subprocess.Popen(cmd)
        return True
    
    def send_prompt(self, prompt_text, delay=5):
        """
        发送提示到 TRAE
        需要 pyautogui 和 pyperclip
        """
        if not PYAUTOGUI_AVAILABLE:
            print("❌ 需要安装 pyautogui 和 pyperclip")
            print("   运行: pip install pyautogui pyperclip")
            return False
        
        print(f"⏳ 等待 {delay} 秒让 TRAE 启动...")
        time.sleep(delay)
        
        # 复制提示到剪贴板
        pyperclip.copy(prompt_text)
        print("📋 提示已复制到剪贴板")
        
        # 粘贴并发送
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        pyautogui.press('enter')
        print("📤 提示已发送给 TRAE")
        
        return True


class ProjectManager:
    """项目管理器"""
    
    @staticmethod
    def create_project(project_dir, requirements=None):
        """
        创建项目结构和初始文档
        
        Args:
            project_dir: 项目目录路径
            requirements: 需求描述（字符串或字典）
        """
        # 创建目录
        docs_dir = os.path.join(project_dir, '.trae-docs')
        os.makedirs(docs_dir, exist_ok=True)
        
        # 创建 requirements.md
        req_file = os.path.join(docs_dir, 'requirements.md')
        if isinstance(requirements, dict):
            content = ProjectManager._format_requirements_md(requirements)
        else:
            content = requirements or "# 项目需求\n\n请补充需求描述。"
            
        with open(req_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 项目已创建: {project_dir}")
        print(f"✅ 需求文档: {req_file}")
        
        return docs_dir
    
    @staticmethod
    def _format_requirements_md(req):
        """格式化需求为 Markdown"""
        md = f"# {req.get('name', '项目需求')}\n\n"
        md += f"## 项目描述\n{req.get('description', '')}\n\n"
        
        if 'features' in req:
            md += "## 功能需求\n"
            for feature in req['features']:
                md += f"- {feature}\n"
            md += "\n"
        
        if 'tech_stack' in req:
            md += f"## 技术栈\n{req['tech_stack']}\n\n"
            
        return md
    
    @staticmethod
    def create_prompt(project_dir, prompt_text=None):
        """创建给 TRAE 的提示文件"""
        docs_dir = os.path.join(project_dir, '.trae-docs')
        prompt_file = os.path.join(docs_dir, 'prompt_to_trape.md')
        
        if not prompt_text:
            # 读取 requirements 生成默认提示
            req_file = os.path.join(docs_dir, 'requirements.md')
            if os.path.exists(req_file):
                with open(req_file, 'r', encoding='utf-8') as f:
                    requirements = f.read()
            else:
                requirements = "请完成项目开发。"
            
            prompt_text = f"""# TRAE 开发任务

{requirements}

## 工作流程

### Phase 1: 规划
1. 阅读 .trae-docs/requirements.md
2. 创建 .trae-docs/architecture.md - 系统架构设计
3. 创建 .trae-docs/task_plan.md - 详细任务分解
4. 创建 .trae-docs/progress.md - 初始进度状态

### Phase 2: 实现
按照 task_plan.md 中的任务逐步实现代码。

### Phase 3: 完成信号
当所有任务完成后：
1. 创建空文件：.trae-docs/.signal_project_done
2. 更新 progress.md 状态为 COMPLETE

## 重要提示
- 使用 SOLO 模式工作
- 自主完成任务，不需要用户确认
- 确保代码可以直接运行
- 包含完整的 README.md 说明如何启动项目

请开始工作！
"""
        
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt_text)
            
        print(f"✅ 提示文件已创建: {prompt_file}")
        return prompt_file


class ProgressMonitor:
    """进度监控器"""
    
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.docs_dir = os.path.join(project_dir, '.trae-docs')
        
    def check_signal(self, signal_name):
        """检查信号文件"""
        signal_path = os.path.join(self.docs_dir, f".signal_{signal_name}")
        return os.path.exists(signal_path)
    
    def read_progress(self):
        """读取进度文件"""
        progress_path = os.path.join(self.docs_dir, "progress.md")
        if os.path.exists(progress_path):
            with open(progress_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    
    def get_status(self):
        """获取当前状态摘要"""
        status = {
            'project_dir': self.project_dir,
            'signals': {},
            'progress': None
        }
        
        # 检查各种信号
        signal_types = ['planning_done', 'batch_1_done', 'review_done', 
                       'project_done', 'blocked', 'error_loop']
        for sig in signal_types:
            status['signals'][sig] = self.check_signal(sig)
        
        # 读取进度
        progress = self.read_progress()
        if progress:
            status['progress'] = progress[:500]  # 前500字符
            
        return status
    
    def wait_for_completion(self, timeout=None, interval=10):
        """
        等待项目完成
        
        Args:
            timeout: 超时时间（秒），None表示无限等待
            interval: 检查间隔（秒）
        """
        print(f"⏳ 监控项目进度: {self.project_dir}")
        print(f"   检查间隔: {interval}秒")
        if timeout:
            print(f"   超时时间: {timeout}秒")
        print()
        
        start_time = time.time()
        last_file_count = 0
        
        while True:
            # 检查完成信号
            if self.check_signal('project_done'):
                print("\n✅ 项目开发完成！")
                return True
            
            # 检查阻塞信号
            if self.check_signal('blocked'):
                print("\n⚠️  TRAE 遇到阻塞，需要干预")
                return False
            
            # 显示进度
            progress = self.read_progress()
            if progress:
                # 提取状态行
                for line in progress.split('\n'):
                    if 'status:' in line.lower() or '状态:' in line:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] {line.strip()}")
                        break
            
            # 检查文件数量变化
            src_dir = os.path.join(self.project_dir, 'src')
            public_dir = os.path.join(self.project_dir, 'public')
            file_count = 0
            for d in [src_dir, public_dir]:
                if os.path.exists(d):
                    for root, dirs, files in os.walk(d):
                        file_count += len(files)
            
            if file_count != last_file_count:
                print(f"   源代码文件数: {file_count}")
                last_file_count = file_count
            
            # 检查超时
            if timeout and (time.time() - start_time) > timeout:
                print(f"\n⏰ 超时 ({timeout}秒)")
                return False
            
            time.sleep(interval)


# 便捷函数
def quick_start(project_dir, requirements, trae_path=None):
    """
    快速启动 TRAE 开发项目
    
    一键完成：创建项目 → 启动 TRAE → 发送提示
    
    Args:
        project_dir: 项目目录
        requirements: 需求描述（字符串或字典）
        trae_path: TRAE 安装路径（可选，自动查找）
    """
    print("=" * 60)
    print("🚀 TRAE 快速启动")
    print("=" * 60)
    
    # 1. 创建项目
    print("\n📁 步骤 1: 创建项目结构")
    ProjectManager.create_project(project_dir, requirements)
    
    # 2. 创建提示
    print("\n📝 步骤 2: 创建提示文件")
    prompt_file = ProjectManager.create_prompt(project_dir)
    
    # 读取提示内容
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt_text = f.read()
    
    # 3. 启动 TRAE
    print("\n🎮 步骤 3: 启动 TRAE")
    controller = TRAEController(trae_path)
    
    if not controller.trae_path:
        print("❌ 找不到 TRAE，请手动指定路径:")
        print("   controller.setup('E:\\software\\Trae CN\\Trae CN.exe')")
        return False
    
    controller.launch(project_dir)
    
    # 4. 发送提示
    print("\n📤 步骤 4: 发送开发任务")
    controller.send_prompt(prompt_text, delay=5)
    
    print("\n" + "=" * 60)
    print("✅ TRAE 已启动并开始开发！")
    print(f"📂 项目目录: {project_dir}")
    print("=" * 60)
    
    return True


# 用户控制函数
def pause_project(project_dir):
    """暂停项目"""
    signal_path = os.path.join(project_dir, '.trae-docs', '.signal_pause')
    open(signal_path, 'w').close()
    print(f"⏸️  项目已暂停: {project_dir}")

def resume_project(project_dir):
    """恢复项目"""
    signal_path = os.path.join(project_dir, '.trae-docs', '.signal_resume')
    open(signal_path, 'w').close()
    print(f"▶️  项目已恢复: {project_dir}")

def stop_project(project_dir):
    """停止项目"""
    signal_path = os.path.join(project_dir, '.trae-docs', '.signal_stop')
    open(signal_path, 'w').close()
    print(f"⏹️  项目已停止: {project_dir}")


if __name__ == '__main__':
    # 示例用法
    print("TRAE 自动化助手")
    print("\n示例用法:")
    print("```python")
    print("from automation_helper import quick_start, ProgressMonitor")
    print("")
    print("# 快速启动项目")
    print("quick_start(")
    print("    project_dir='D:\\\MyGame',")
    print("    requirements={'name': '我的游戏', 'description': '一个有趣的游戏'}")
    print(")")
    print("")
    print("# 监控进度")
    print("monitor = ProgressMonitor('D:\\\MyGame')")
    print("monitor.wait_for_completion()")
    print("```")
