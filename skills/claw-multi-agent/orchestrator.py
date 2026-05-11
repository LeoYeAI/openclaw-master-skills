#!/usr/bin/env python3
"""
指挥官模式工具函数
帮助主 Agent 生成正确的 sessions_spawn task 描述

功能：
1. generate_task(role, task, context, output_path) → 返回标准化 task 描述字符串
2. suggest_model(role) → 返回推荐模型别名
3. suggest_mode(task_description) → 根据任务描述建议用哪种模式（orchestrator/pipeline）
4. print_quick_reference() → 打印快速参考卡

CLI 用法：
    python orchestrator.py generate --role researcher --task "调研 XXX"
    python orchestrator.py suggest-mode --task "帮我搜索并分析..."
    python orchestrator.py quick-ref
"""

import argparse
from typing import Optional


# 预设角色定义（与 multiagent_engine.py 中的 OrchestratorGuide 保持一致）
PRESETS = {
    "planner": {
        "model": "glm",
        "description": "规划者：需求分析、任务拆解、优先级排序",
        "system_hint": "你是一个项目规划专家，擅长将复杂需求拆解为清晰的执行步骤。"
    },
    "researcher": {
        "model": "glm",
        "description": "信息猎手：广度搜索、交叉验证、结构化输出（有 web_search 工具）",
        "system_hint": "你是一个专业研究员，擅长搜索和整理信息，输出结构化报告。"
    },
    "coder": {
        "model": "kimi",
        "description": "代码工匠：编码、调试、测试、重构（有 exec 工具）",
        "system_hint": "你是一个资深工程师，擅长编写高质量、可维护的代码。"
    },
    "writer": {
        "model": "gemini",
        "description": "文字工匠：文档、报告、文案、整理（有 write 工具）",
        "system_hint": "你是一个专业写作者，擅长将信息组织成清晰、有价值的文档。"
    },
    "reviewer": {
        "model": "glm",
        "description": "质量守门人：代码审查、内容审核、合规检查",
        "system_hint": "你是一个严格的审查员，客观指出问题并给出建设性改进意见。"
    },
    "analyst": {
        "model": "kimi",
        "description": "数据侦探：数据处理、统计分析、趋势预测（有 exec 工具）",
        "system_hint": "你是一个数据分析专家，擅长从数据中发现规律和洞察。"
    }
}

# 触发词 - 用于判断使用哪种模式
ORCHESTRATOR_KEYWORDS = [
    # 需要联网搜索的关键词
    "搜索", "调研", "查找", "查询", "最新", "2024", "2025", "资料", "信息",
    "web_search", "search", "research", "find", "look up",
    # 需要文件操作的关键词
    "保存", "写入", "读取", "修改", "编辑", "删除", "创建文件",
    "save", "write", "read", "edit", "modify", "create file",
    # 需要代码执行的关键词
    "运行", "执行", "测试", "调试", "安装", "部署",
    "run", "execute", "test", "debug", "install", "deploy",
    # 需要浏览器操作的关键词
    "打开网页", "截图", "点击", "填写表单",
    "browser", "screenshot", "click", "navigate",
]


def generate_task(
    role: str,
    task: str,
    context: str = "",
    output_path: str = "",
    format_requirements: str = "Markdown"
) -> str:
    """
    生成适合 sessions_spawn 的标准化 task 描述字符串

    Args:
        role: 预设角色 (planner/researcher/coder/writer/reviewer/analyst)
        task: 具体任务描述
        context: 可选的上下文信息
        output_path: 可选的输出文件路径
        format_requirements: 输出格式要求

    Returns:
        标准化的 task 描述字符串
    """
    preset = PRESETS.get(role, {})
    hint = preset.get("system_hint", "")

    parts = [hint]

    if context:
        parts.append(f"\n【上下文】\n{context}")

    parts.append(f"\n【你的任务】\n{task}")

    output_parts = []
    if format_requirements:
        output_parts.append(f"格式：{format_requirements}")
    if output_path:
        output_parts.append(f"保存到：{output_path}")
    output_parts.append("完成后简短总结做了什么")

    if output_parts:
        parts.append(f"\n【输出要求】\n- " + "\n- ".join(output_parts))

    return "\n".join(parts)


def suggest_model(role: str) -> str:
    """
    根据角色返回推荐的模型别名

    Args:
        role: 预设角色名称

    Returns:
        推荐的模型别名 (glm/kimi/gemini/claude/opus)
    """
    preset = PRESETS.get(role, {})
    return preset.get("model", "kimi")


def suggest_mode(task_description: str) -> tuple[str, str]:
    """
    根据任务描述建议使用哪种模式

    Args:
        task_description: 任务描述文本

    Returns:
        (推荐模式, 原因说明)
        模式值: "orchestrator" 或 "pipeline"
    """
    task_lower = task_description.lower()

    # 检查是否包含指挥官模式关键词
    for keyword in ORCHESTRATOR_KEYWORDS:
        if keyword.lower() in task_lower:
            return (
                "orchestrator",
                f"检测到关键词 '{keyword}'，任务需要工具操作能力，建议使用指挥官模式"
            )

    # 默认推荐流水线模式
    return (
        "pipeline",
        "纯文本生成任务，建议使用流水线模式以获得更好的性能和成本效益"
    )


def print_quick_reference():
    """打印快速参考卡"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                    🐝 claw-multi-agent 快速参考卡                       ║
╠══════════════════════════════════════════════════════════════════╣
║  【模式选择】                                                      ║
║  ┌─────────────────────────────────────────────────────────────┐ ║
║  │ 需要联网/文件/执行命令?  →  指挥官模式 (sessions_spawn)      │ ║
║  │ 只需纯文本生成?          →  流水线模式 (python run.py)       │ ║
║  └─────────────────────────────────────────────────────────────┘ ║
║                                                                   ║
║  【预设角色】                                                      ║
║  ┌────────────┬────────┬──────────────────────────────────────┐ ║
║  │ planner    │ glm    │ 📋 规划者 - 需求分析、任务拆解         │ ║
║  │ researcher │ glm    │ 🔍 研究员 - 搜索、整理、结构化输出     │ ║
║  │ coder      │ kimi   │ 💻 程序员 - 编码、调试、测试           │ ║
║  │ writer     │ gemini │ ✍️ 写作者 - 文档、报告、文案           │ ║
║  │ reviewer   │ glm    │ 🔎 审核员 - 代码审查、内容审核         │ ║
║  │ analyst    │ kimi   │ 📊 分析师 - 数据处理、统计分析         │ ║
║  └────────────┴────────┴──────────────────────────────────────┘ ║
║                                                                   ║
║  【常用 CLI】                                                      ║
║  ┌─────────────────────────────────────────────────────────────┐ ║
║  │ python run.py --guide orchestrator                          │ ║
║  │ python run.py --template researcher --task "调研 XXX"       │ ║
║  │ python orchestrator.py generate --role coder --task "..."   │ ║
║  │ python orchestrator.py suggest-mode --task "搜索..."        │ ║
║  └─────────────────────────────────────────────────────────────┘ ║
╚══════════════════════════════════════════════════════════════════╝
""")


def print_orchestrator_guide():
    """打印指挥官模式详细指南"""
    print("""
📋 指挥官模式 (Orchestrator Mode) 使用指南
═══════════════════════════════════════════════════════════════

【核心概念】
主 Agent 使用 sessions_spawn 工具直接调度子 Agent。
子 Agent 拥有完整的 OpenClaw 工具能力（web_search、exec、read/write 等）。

【预设角色速览】
""")
    for role, info in PRESETS.items():
        print(f"  {role:<12} (模型: {info['model']})")
        print(f"               {info['description']}")
        print()

    print("""【并行执行示例】
```python
# 同时派发多个任务，它们会并行执行
sessions_spawn({
    "task": "搜索 LangChain 框架资料，整理到 /workspace/research/langchain.md",
    "label": "r1"
})
sessions_spawn({
    "task": "搜索 CrewAI 框架资料，整理到 /workspace/research/crewai.md",
    "label": "r2"
})
```

【串行执行示例】
```python
# Step 1: 先调研
sessions_spawn({"task": "调研 AI 框架...", "label": "research"})
# 等待回报...

# Step 2: 再写作
sessions_spawn({"task": "基于调研结果撰写报告...", "label": "write"})
```

【Task 描述最佳实践】
1. 明确目标：要做什么
2. 提供上下文：背景信息
3. 指定输出：格式、保存路径
4. 设置约束：字数、语言等限制

═══════════════════════════════════════════════════════════════
""")


def main():
    parser = argparse.ArgumentParser(
        description="指挥官模式工具 - 生成 sessions_spawn 任务模板",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 生成 researcher 的任务描述
    python orchestrator.py generate --role researcher --task "调研 LangChain"

    # 带上下文和输出路径
    python orchestrator.py generate --role writer \
        --task "撰写技术报告" \
        --context "已收集到三个框架的资料" \
        --output /workspace/report.md

    # 建议使用哪种模式
    python orchestrator.py suggest-mode --task "搜索最新的 AI 论文"

    # 打印快速参考
    python orchestrator.py quick-ref
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # generate 子命令
    gen_parser = subparsers.add_parser("generate", help="生成标准化 task 描述")
    gen_parser.add_argument("--role", required=True,
                           choices=list(PRESETS.keys()),
                           help="预设角色")
    gen_parser.add_argument("--task", required=True,
                           help="具体任务描述")
    gen_parser.add_argument("--context", default="",
                           help="可选的上下文信息")
    gen_parser.add_argument("--output", default="",
                           help="可选的输出文件路径")
    gen_parser.add_argument("--format", default="Markdown",
                           help="输出格式要求 (默认: Markdown)")

    # suggest-mode 子命令
    mode_parser = subparsers.add_parser("suggest-mode",
                                        help="根据任务描述建议模式")
    mode_parser.add_argument("--task", required=True,
                            help="任务描述文本")

    # quick-ref 子命令
    subparsers.add_parser("quick-ref", help="打印快速参考卡")

    args = parser.parse_args()

    if args.command == "generate":
        result = generate_task(
            role=args.role,
            task=args.task,
            context=args.context,
            output_path=args.output,
            format_requirements=args.format
        )
        print(result)

    elif args.command == "suggest-mode":
        mode, reason = suggest_mode(args.task)
        print(f"推荐模式: {mode}")
        print(f"原因: {reason}")

    elif args.command == "quick-ref":
        print_quick_reference()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
