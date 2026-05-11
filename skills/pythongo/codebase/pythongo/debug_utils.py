import os
import sys

from .infini import write_log


def start_remote_debug(port: int = 5678, wait_for_client: bool = True) -> None:
    """
    启动远程调试服务

    Args:
        port: 监听端口
        wait_for_client: 是否等待客户端连接
    Note:
        - 当 `wait_for_client` 为 `True` 时，会一直阻塞直到客户端连接
        - 如果不想阻塞后续代码执行，请将 `wait_for_client` 设置为 `False`
    """

    try:
        # 自动推断 Python 解释器路径
        # 如果是虚拟环境，sys.exec_prefix 通常指向 venv 根目录
        # 优先尝试 venv/Scripts/python.exe
        candidate = os.path.join(sys.exec_prefix, "Scripts", "python.exe")
        if not os.path.exists(candidate):
            # 其次尝试 python.exe (标准安装)
            candidate = os.path.join(sys.exec_prefix, "python.exe")

        if os.path.exists(candidate):
            sys.executable = candidate
        else:
            # 兜底：如果找不到，保持原样或打印警告
            write_log(f"[DebugUtils] 警告: 未找到 python.exe，sys.executable 仍为: {sys.executable}")

        import debugpy

        # 防止重复监听（比如策略被 Reload 时）
        try:
            debugpy.listen(("127.0.0.1", port))
            write_log(f"[Debug] 服务监听中 (端口 {port})...")
        except RuntimeError:
            write_log(f"[Debug] 端口 {port} 已被占用 (可能是调试器已在运行)，跳过监听。")
            return

        if wait_for_client:
            write_log("[Debug] 等待 VS Code 连接...")
            debugpy.wait_for_client()
            write_log("[Debug] 连接成功！")

    except ImportError as e:
        write_log(f"[Debug] 启动失败: {e}")
        write_log(f"[Debug] 启动失败: 未安装 debugpy 库，请执行 pip install debugpy 命令安装后重试")

    except Exception as e:
        write_log(f"[Debug] 启动失败: {e}")
