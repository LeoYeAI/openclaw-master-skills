#!/usr/bin/env python3
"""
DevOps Pipeline Management Package
流水线管理客户端包

模块结构：
- client: PipelineClient 核心类（初始化、签名、HTTP请求）
- pipeline_ops: 流水线CRUD操作
- template_ops: 模板和工作空间操作
- execution_ops: 执行相关操作
- interactive: 交互式创建流水线
- interactive_update: 交互式更新流水线
- interactive_run: 交互式执行流水线
- run_pipeline: 流水线执行流程
- utils: 工具函数
- main: CLI入口
"""

import os

# 交互模式标志
INTERACTIVE_MODE = os.getenv('INTERACTIVE_MODE', 'true').lower() == 'true'

# 导入核心类和混入类
from .client import PipelineClient
from .pipeline_ops import PipelineOpsMixin
from .template_ops import TemplateOpsMixin
from .execution_ops import ExecutionOpsMixin
from .interactive import InteractiveOpsMixin
from .interactive_update import InteractiveUpdateMixin
from .interactive_run import InteractiveRunMixin
from .run_pipeline import RunPipelineMixin
from .utils import prompt_choice, prompt_input, confirm

# 使用多重继承组合所有混入类
class PipelineClient(
    PipelineClient,  # 基础核心类
    PipelineOpsMixin,  # 流水线CRUD
    TemplateOpsMixin,  # 模板和工作空间
    ExecutionOpsMixin,  # 执行操作
    InteractiveOpsMixin,  # 交互式创建
    InteractiveUpdateMixin,  # 交互式更新
    InteractiveRunMixin,  # 交互式执行
    RunPipelineMixin,  # 执行流程
):
    """流水线管理客户端 - 组合所有功能"""
    pass


# 延迟导入 main 函数以避免循环依赖
def _load_main():
    from . import main
    return main


__all__ = [
    'PipelineClient',
    'prompt_choice',
    'prompt_input',
    'confirm',
    'INTERACTIVE_MODE',
]

__version__ = '1.0.0'
