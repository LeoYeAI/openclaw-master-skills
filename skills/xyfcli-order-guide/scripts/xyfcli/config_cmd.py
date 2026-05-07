"""Config 配置管理命令"""

import typer
from .config import load_config, save_config, get_base_url, get_authorization_token, DEFAULT_CONFIG

config_app = typer.Typer(name="config", help="配置管理命令")


def sync_run(coroutine):
    """同步运行异步函数"""
    import asyncio
    return asyncio.get_event_loop().run_until_complete(coroutine)


def format_output(data, json_output: bool = False):
    """格式化输出为JSON或原始格式"""
    import json
    if json_output:
        typer.echo(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        if isinstance(data, dict):
            for key, value in data.items():
                typer.echo(f"{key}: {value}")
        else:
            typer.echo(data)


def handle_errors(func):
    """错误处理装饰器，提供结构化的错误输出"""
    import functools
    import traceback
    import json as json_module
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 从参数中获取json_output，如果不存在则默认为False
        json_output = kwargs.get('json_output', False)
        
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if json_output:
                error_data = {
                    "error": True,
                    "type": type(e).__name__,
                    "message": str(e),
                    "traceback": traceback.format_exc() if hasattr(e, '__traceback__') else None
                }
                typer.echo(json_module.dumps(error_data, ensure_ascii=False, indent=2))
                # 输出JSON错误后退出，退出码为1
                raise typer.Exit(code=1)
            else:
                # 让Typer处理默认错误输出
                raise
    
    return wrapper


@config_app.command("show")
@handle_errors
def show_config(
    json_output: bool = typer.Option(False, "-j", "--json", help="输出JSON格式")
):
    """显示当前配置"""
    config = load_config()

    if json_output:
        format_output(config, json_output)
    else:
        typer.echo("当前配置:")
        typer.echo(f"  API 基础 URL: {config.get('base_url', DEFAULT_CONFIG['base_url'])}")
        typer.echo(f"  Authorization Token: {config.get('authorization_token', DEFAULT_CONFIG['authorization_token'])[:20]}...")


@config_app.command("set")
def set_config(
    base_url: str = typer.Option(None, "--base-url", "-u", help="API 基础 URL"),
    token: str = typer.Option(None, "--token", "-t", help="授权 Token"),
    json_output: bool = typer.Option(False, "-j", "--json", help="输出JSON格式")
):
    """
    设置配置项

    示例:
    xyfcli config set --base-url http://127.0.0.1:8000
    xyfcli config set --token gateway_token_xxx
    xyfcli config set --base-url http://127.0.0.1:8000 --token gateway_token_xxx
    """
    config = load_config()
    changes = {}

    if base_url:
        config["base_url"] = base_url
        changes["base_url"] = base_url
        if not json_output:
            typer.echo(f"已设置 API 基础 URL: {base_url}")

    if token:
        config["authorization_token"] = token
        changes["authorization_token_set"] = True
        if not json_output:
            typer.echo(f"已设置 Authorization Token")

    save_config(config)
    
    if json_output:
        result = {
            "success": True,
            "message": "配置已保存",
            "changes": changes
        }
        format_output(result, json_output)
    else:
        typer.echo("配置已保存")


@config_app.command("init")
def init_config(
    base_url: str = typer.Option(DEFAULT_CONFIG["base_url"], "--base-url", "-u", help="API 基础 URL"),
    token: str = typer.Option(DEFAULT_CONFIG["authorization_token"], "--token", "-t", help="授权 Token"),
    json_output: bool = typer.Option(False, "-j", "--json", help="输出JSON格式")
):
    """
    初始化配置文件

    示例:
    xyfcli config init
    xyfcli config init --base-url http://192.168.1.100:8000
    xyfcli config init --token my_custom_token
    """
    config = {
        "base_url": base_url,
        "authorization_token": token,
    }
    save_config(config)
    
    if json_output:
        result = {
            "success": True,
            "message": "配置文件已初始化",
            "config": config
        }
        format_output(result, json_output)
    else:
        typer.echo("配置文件已初始化")
        typer.echo(f"  API 基础 URL: {base_url}")
        typer.echo(f"  Authorization Token: {token[:20]}..." if len(token) > 20 else f"  Authorization Token: {token}")


@config_app.command("reset")
def reset_config(
    json_output: bool = typer.Option(False, "-j", "--json", help="输出JSON格式")
):
    """重置为默认配置"""
    save_config(DEFAULT_CONFIG)
    
    if json_output:
        result = {
            "success": True,
            "message": "配置已重置为默认值",
            "config": DEFAULT_CONFIG
        }
        format_output(result, json_output)
    else:
        typer.echo("配置已重置为默认值")
        typer.echo(f"  API 基础 URL: {DEFAULT_CONFIG['base_url']}")
        typer.echo(f"  Authorization Token: {DEFAULT_CONFIG['authorization_token']}")

