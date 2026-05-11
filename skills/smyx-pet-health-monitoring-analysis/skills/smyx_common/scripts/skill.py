#!/usr/bin/env python3
import os
import sys
import subprocess

from .config import ApiEnum as ApiEnumBase, ConstantEnum
from .base import BaseSkill
from skills.smyx_common.scripts.api_service import ApiService as ApiServiceBase
from .util import FileUtil

from .api_service import ApiService

class Skill(BaseSkill, ApiService):

    def __init__(self):
        super().__init__()

class AgentSkill(BaseSkill, ApiService):

    def __init__(self):
        super().__init__()

    def ai_chat(self, prompt: str, session_id: str = None, timeout: int = 120):
        """
        通过 subprocess 调用 openclaw agent 命令

        Args:
            prompt: 分析提示
            session_id: 会话 ID（可选）
            timeout: 超时时间（秒）

        Returns:
            分析结果或会话 ID
        """
        import uuid

        # 生成唯一会话 ID
        if not session_id:
            entry_script = sys.argv[0]
            abs_entry_script = os.path.abspath(entry_script)
            main_name = FileUtil.get_name(abs_entry_script)
            session_id = f"{main_name}--{uuid.uuid4()}"

        ConstantEnum.is_debug() and print(f"🤖 正在调用 openclaw agent (会话：{session_id})..., prompt:{prompt}")

        # 构建命令
        cmd = [
            "openclaw",
            "agent",
            "-m", str(prompt),
            "--session-id", session_id,
            "--thinking", "minimal",
            "--timeout", str(timeout)
        ]

        ConstantEnum.is_debug() and print(f"🤖 正在调用 openclaw agent 执行命令{' '.join(cmd)}")

        try:
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 10
            )

            if result.stderr:
                ConstantEnum.is_debug() and print(f"🤖 正在调用 openclaw agent 执行错误:{result.stderr}")
                return

            output = result.stdout
            ConstantEnum.is_debug() and print(f"🤖 正在调用 openclaw agent 执行成功:{output}")

            return output

        except subprocess.TimeoutExpired as e:
            ConstantEnum.is_debug() and print(f"🤖 正在调用 openclaw agent 超时（{timeout}秒），任务可能仍在后台运行:{e}")
        except Exception as e:
            ConstantEnum.is_debug() and print(f"🤖 正在调用 openclaw agent 执行错误:{e}")


skill = Skill()
