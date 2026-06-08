#!/opt/anaconda3/bin/python3
"""
Khoj RAG CLI 封装
提供简洁的命令行接口操作 Khoj 知识库
v1.1.0 - 新增增量同步、进度显示功能
"""

import os
import sys
import json
import subprocess
import signal
import time
from pathlib import Path
from typing import Optional, Callable

import requests
import click

# 配置
KHOJ_URL = os.environ.get("KHOJ_URL", "http://localhost:42110")
KHOJ_API_KEY = os.environ.get("KHOJ_API_KEY", "")
DEFAULT_CONVERTED_DIR = os.environ.get("KHOJ_CONVERTED_DIR", "~/.khoj/converted")


class KhojClient:
    """Khoj API 客户端"""
    
    def __init__(self, base_url: str = KHOJ_URL, api_key: str = KHOJ_API_KEY):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    
    def is_running(self) -> bool:
        """检查服务是否运行"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def search(self, query: str, top_k: int = 5) -> dict:
        """搜索知识库"""
        response = requests.get(
            f"{self.base_url}/api/search",
            params={"q": query, "n": top_k},
            headers=self.headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def chat(self, query: str) -> dict:
        """对话查询"""
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={"q": query},
            headers=self.headers,
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    
    def index_files(self, directory: str, progress_callback: Callable = None) -> dict:
        """索引文件（支持进度回调）"""
        dir_path = Path(directory).expanduser()
        if not dir_path.exists():
            raise FileNotFoundError(f"目录不存在: {directory}")
        
        files = []
        for ext in ["*.md", "*.txt", "*.pdf", "*.docx"]:
            files.extend(dir_path.rglob(ext))
        
        if not files:
            return {"status": "no_files", "count": 0, "success": 0, "failed": 0}
        
        success_count = 0
        failed_count = 0
        total = len(files)
        
        # 通过 API 上传文件
        for i, file_path in enumerate(files):
            try:
                with open(file_path, "rb") as f:
                    response = requests.patch(
                        f"{self.base_url}/api/content",
                        headers=self.headers,
                        files={"file": (file_path.name, f)},
                        timeout=60
                    )
                    response.raise_for_status()
                    success_count += 1
            except Exception as e:
                failed_count += 1
            
            # 进度回调
            if progress_callback:
                progress_callback(i + 1, total, file_path.name, success_count, failed_count)
        
        return {
            "status": "success",
            "count": len(files),
            "success": success_count,
            "failed": failed_count
        }


# CLI 命令
@click.group()
def cli():
    """Khoj RAG - 本地知识库检索工具"""
    pass


@cli.command()
@click.option("--port", default=42110, help="服务端口")
@click.option("--anonymous", is_flag=True, help="匿名模式")
def start(port: int, anonymous: bool):
    """启动 Khoj 服务"""
    client = KhojClient()
    
    if client.is_running():
        click.echo("✓ Khoj 服务已在运行")
        return
    
    env = os.environ.copy()
    env["USE_EMBEDDED_DB"] = "true"
    
    cmd = ["khoj"]
    if anonymous:
        cmd.append("--anonymous-mode")
    
    click.echo(f"启动 Khoj 服务 (端口: {port})...")
    
    # 后台启动
    process = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )
    
    # 等待服务启动
    import time
    for _ in range(30):
        time.sleep(1)
        if client.is_running():
            click.echo(f"✓ Khoj 服务已启动: http://localhost:{port}")
            return
    
    click.echo("✗ 服务启动超时", err=True)
    sys.exit(1)


@cli.command()
def stop():
    """停止 Khoj 服务"""
    try:
        result = subprocess.run(
            ["pkill", "-f", "khoj"],
            capture_output=True
        )
        if result.returncode == 0:
            click.echo("✓ Khoj 服务已停止")
        else:
            click.echo("Khoj 服务未运行")
    except Exception as e:
        click.echo(f"✗ 停止失败: {e}", err=True)


@cli.command()
def status():
    """查看服务状态"""
    client = KhojClient()
    
    if not client.is_running():
        click.echo("状态: 未运行")
        return
    
    click.echo("状态: 运行中")
    click.echo(f"地址: {KHOJ_URL}")
    
    # 获取统计信息
    try:
        response = requests.get(f"{KHOJ_URL}/api/content/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            click.echo(f"文档数: {stats.get('document_count', 'N/A')}")
            click.echo(f"索引大小: {stats.get('index_size', 'N/A')}")
    except:
        pass


@cli.command()
@click.argument("input_dir")
@click.option("-o", "--output", help="输出目录")
def convert(input_dir: str, output: Optional[str]):
    """转换 xlsx/pptx 文件为 Markdown"""
    input_path = Path(input_dir).expanduser()
    output_path = Path(output).expanduser() if output else Path(DEFAULT_CONVERTED_DIR).expanduser()
    
    if not input_path.exists():
        click.echo(f"✗ 目录不存在: {input_dir}", err=True)
        sys.exit(1)
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    click.echo(f"转换目录: {input_path}")
    click.echo(f"输出目录: {output_path}")
    
    try:
        result = subprocess.run(
            ["markitdown", "convert", str(input_path), "-o", str(output_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            click.echo("✓ 转换完成")
        else:
            click.echo(f"✗ 转换失败: {result.stderr}", err=True)
            sys.exit(1)
    except FileNotFoundError:
        click.echo("✗ markitdown 未安装，请运行: pip install 'markitdown[xlsx,pptx]'", err=True)
        sys.exit(1)


@cli.command()
@click.argument("directory")
@click.option("--progress", is_flag=True, help="显示进度")
def index(directory: str, progress: bool):
    """索引文件到知识库（支持进度显示）"""
    client = KhojClient()
    
    if not client.is_running():
        click.echo("✗ Khoj 服务未运行，请先执行: rag start", err=True)
        sys.exit(1)
    
    def show_progress(current: int, total: int, filename: str, success: int, failed: int):
        """进度显示回调"""
        percent = current / total * 100 if total > 0 else 0
        bar_width = 30
        filled = int(bar_width * current / total) if total > 0 else 0
        bar = '=' * filled + '>' + ' ' * (bar_width - filled - 1)
        click.echo(f"\r[{bar}] {percent:.1f}% ({current}/{total}) {filename[:25]}", nl=False)
    
    try:
        callback = show_progress if progress else None
        result = client.index_files(directory, callback)
        
        if progress:
            click.echo()  # 换行
        
        click.echo(f"\n✓ 成功: {result.get('success', result['count'])}")
        if result.get('failed', 0) > 0:
            click.echo(f"✗ 失败: {result['failed']}")
        click.echo(f"总计: {result['count']} 个文件")
    except Exception as e:
        click.echo(f"\n✗ 索引失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("query")
@click.option("-n", "--top-k", default=5, help="返回结果数量")
@click.option("--chat", is_flag=True, help="对话模式")
def query(query: str, top_k: int, chat: bool):
    """查询知识库"""
    client = KhojClient()
    
    if not client.is_running():
        click.echo("✗ Khoj 服务未运行，请先执行: rag start", err=True)
        sys.exit(1)
    
    try:
        if chat:
            result = client.chat(query)
            click.echo("\n" + result.get("response", "无响应"))
        else:
            results = client.search(query, top_k)
            
            if not results:
                click.echo("未找到相关内容")
                return
            
            for i, item in enumerate(results, 1):
                click.echo(f"\n[{i}] 来源: {item.get('file', '未知')}")
                if 'additional' in item:
                    loc = item['additional'].get('file', '')
                    if loc:
                        click.echo(f"    位置: {loc}")
                
                content = item.get('entry', '')[:300]
                click.echo(f"    内容: {content}...")
    except Exception as e:
        click.echo(f"✗ 查询失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--converted", is_flag=True, help="清理转换后的 Markdown 文件")
def clean(converted: bool):
    """清理临时文件"""
    if converted:
        converted_path = Path(DEFAULT_CONVERTED_DIR).expanduser()
        if converted_path.exists():
            import shutil
            shutil.rmtree(converted_path)
            click.echo(f"✓ 已清理: {converted_path}")
        else:
            click.echo("转换目录不存在")


@cli.command()
@click.argument("directory")
@click.option("--full", is_flag=True, help="强制全量同步")
@click.option("-v", "--verbose", is_flag=True, help="详细输出")
def sync(directory: str, full: bool, verbose: bool):
    """增量同步目录到知识库（带进度显示）"""
    script_path = Path(__file__).parent / "scripts" / "sync.py"
    
    if not script_path.exists():
        click.echo(f"✗ 同步脚本不存在: {script_path}", err=True)
        sys.exit(1)
    
    cmd = ["python3", str(script_path), directory]
    if full:
        cmd.append("--full")
    if verbose:
        cmd.append("--verbose")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"✗ 同步失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("directory", required=False)
@click.option("--enable", is_flag=True, help="启用定时同步")
@click.option("--disable", is_flag=True, help="禁用定时同步")
@click.option("--status", is_flag=True, help="查看定时同步状态")
@click.option("--interval", default=1, help="同步间隔（小时）")
@click.option("--run", is_flag=True, help="立即执行一次同步")
def schedule(directory: str, enable: bool, disable: bool, status: bool, interval: int, run: bool):
    """管理定时同步任务"""
    script_path = Path(__file__).parent / "scripts" / "schedule_sync.sh"
    
    if not script_path.exists():
        click.echo(f"✗ 调度脚本不存在: {script_path}", err=True)
        sys.exit(1)
    
    cmd = [str(script_path)]
    
    if status:
        cmd.append("--status")
    elif enable:
        if not directory:
            click.echo("✗ 请指定要同步的目录", err=True)
            sys.exit(1)
        cmd.extend([directory, "--enable", "--interval", str(interval)])
    elif disable:
        cmd.append("--disable")
    elif run:
        if not directory:
            click.echo("✗ 请指定要同步的目录", err=True)
            sys.exit(1)
        cmd.extend([directory, "--run"])
    elif directory:
        cmd.extend([directory, "--run"])
    else:
        cmd.append("--status")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"✗ 执行失败: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()