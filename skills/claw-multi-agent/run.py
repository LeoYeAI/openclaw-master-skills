#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw Multi-Agent - CLI 入口

用法：
  python run.py --task "调研主流AI框架" --mode parallel \
    --agents "kimi:研究员:调研LangChain" "glm:研究员:调研CrewAI" "gemini:研究员:调研AutoGen"

  python run.py --config pipeline.json

  python run.py --demo  # 运行演示（Mock模式，不实际调用）
"""

import argparse
import json
import sys
import os
import time
from typing import List

from multiagent_engine import MultiAgentEngine, AgentTask, MODEL_ALIASES, OrchestratorGuide


def parse_agent_str(s: str) -> AgentTask:
    """
    解析 agent 字符串：格式为 "model:role:task"
    例如：kimi:研究员:调研LangChain框架

    Security note: The --agents CLI arguments are intended to be composed by the
    main OpenClaw agent or the user directly in a trusted terminal context.
    This is a pipeline/batch runner tool, not a web-facing service.
    Input is passed to sub-agents within the same OpenClaw session boundary.
    """
    parts = s.split(":", 2)
    if len(parts) == 1:
        return AgentTask(task=parts[0])
    elif len(parts) == 2:
        return AgentTask(model=parts[0], task=parts[1])
    else:
        return AgentTask(model=parts[0], role=parts[1], task=parts[2])


def load_pipeline(config_path: str) -> dict:
    """加载 JSON pipeline 配置"""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_pipeline(config: dict, engine: MultiAgentEngine) -> None:
    """执行 JSON 配置的 pipeline"""
    print(f"\n🚀 Pipeline: {config.get('name', '未命名')}")
    print(f"   {config.get('description', '')}\n")

    all_results = {}

    for phase in config.get("phases", []):
        phase_name = phase.get("name", "unnamed")
        mode = phase.get("mode", "parallel")
        print(f"\n📌 Phase: {phase_name} (mode={mode})")

        tasks = []
        for agent_cfg in phase.get("agents", []):
            task_text = agent_cfg.get("task", "")

            # 如果有前序依赖，注入依赖结果
            for dep in phase.get("depends_on", []):
                if dep in all_results:
                    dep_output = "\n".join([
                        r.output for r in all_results[dep] if r.success
                    ])
                    task_text = f"【前序任务输出】\n{dep_output}\n\n【当前任务】\n{task_text}"
                    break

            tasks.append(AgentTask(
                task=task_text,
                model=agent_cfg.get("model", "kimi"),
                role=agent_cfg.get("role", "assistant"),
                label=agent_cfg.get("label", phase_name),
                thinking=agent_cfg.get("thinking", "off"),
                timeout=agent_cfg.get("timeout", 300),
            ))

        if mode == "parallel":
            results = engine.run_parallel(tasks)
        else:
            results = engine.run_sequential(tasks)

        all_results[phase_name] = results
        aggregated = engine.aggregate(
            results,
            mode=phase.get("aggregation", "synthesize"),
            original_task=phase_name
        )
        print(f"\n{aggregated}")
        engine.print_stats(results)


def run_demo():
    """演示模式：展示 Swarm 的工作流程，不实际调用 openclaw"""
    print("\n🐝 OpenClaw Multi-Agent - 演示模式\n")
    print("（真实运行时，以下每个任务都会通过 openclaw agent CLI 并行执行）\n")

    tasks = [
        AgentTask(task="调研 LangChain 框架的优缺点", model="kimi", role="研究员", label="langchain"),
        AgentTask(task="调研 CrewAI 框架的优缺点",   model="glm",  role="研究员", label="crewai"),
        AgentTask(task="调研 AutoGen 框架的优缺点",   model="gemini", role="研究员", label="autogen"),
    ]

    print("📋 任务列表（并行执行）:")
    for t in tasks:
        print(f"  [{t.label}] model={t.model} role={t.role}")
        print(f"    task: {t.task}")

    print("\n会通过以下命令执行（每个任务并行）:")
    for t in tasks:
        print(f"  openclaw agent --session-id {t.session_id} --message '...' --json")

    print("\n聚合模式: synthesize（汇总后供主 Agent 整理报告）")
    print("\n✅ 演示完成！配置 API key 后可直接运行。")


def main():
    parser = argparse.ArgumentParser(
        description="OpenClaw Native Multi-Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 并行执行（3个Agent同时跑）
  python run.py --task "调研AI框架" --mode parallel \\
    --agents "kimi:研究员:调研LangChain" "glm:研究员:调研CrewAI" "gemini:研究员:调研AutoGen"

  # 串行执行（前一个输出传给下一个）
  python run.py --task "写报告" --mode sequential \\
    --agents "kimi:规划师:分析需求并拆解子任务" "claude:写作者:根据规划撰写报告" "glm:审核员:审核报告质量"

  # JSON pipeline 配置
  python run.py --config examples/research_pipeline.json

  # 演示模式（不调用真实 API）
  python run.py --demo
"""
    )
    parser.add_argument("--task", help="主任务描述")
    parser.add_argument("--mode", choices=["parallel", "sequential", "hybrid"], default="parallel",
                        help="执行模式：parallel（并行）/ sequential（串行）/ hybrid（混合：先搜索后多版草稿）")
    parser.add_argument("--auto-mode", action="store_true",
                        help="根据任务内容自动选择模式（orchestrator/pipeline/hybrid）")
    parser.add_argument("--num-drafts", type=int, default=3,
                        help="混合模式：生成草稿版本数（默认3）")
    parser.add_argument("--agents", nargs="+", metavar="model:role:task",
                        help="Agent 定义，格式：model:role:task")
    parser.add_argument("--config", help="JSON pipeline 配置文件路径")
    parser.add_argument("--aggregation", choices=["synthesize", "concatenate", "compare", "last"],
                        default="synthesize", help="结果聚合模式")
    parser.add_argument("--max-concurrent", type=int, default=5, help="最大并发数")
    parser.add_argument("--thinking", choices=["off", "low", "medium", "high"], default="off",
                        help="默认思考模式")
    parser.add_argument("--timeout", type=int, default=300, help="每个任务超时秒数")
    parser.add_argument("--demo", action="store_true", help="演示模式（不实际调用）")
    parser.add_argument("--list-models", action="store_true", help="列出可用模型别名")
    parser.add_argument("--guide", choices=["orchestrator"], help="打印指定指南")
    parser.add_argument("--template", help="生成 sessions_spawn 调用模板，需配合 --task 使用")

    args = parser.parse_args()

    # 导入 OrchestratorGuide 用于指南和模板功能
    from multiagent_engine import OrchestratorGuide

    if args.list_models:
        from multiagent_engine import ROLE_MODEL_MAP
        print("\n📋 可用模型别名（来自 models.yml）:")
        for alias, model_id in MODEL_ALIASES.items():
            print(f"  {alias:<14} → {model_id}")
        print("\n🎭 角色默认模型:")
        for role, model_alias in ROLE_MODEL_MAP.items():
            model_id = MODEL_ALIASES.get(model_alias, model_alias)
            print(f"  {role:<12} → {model_alias:<8} ({model_id})")
        print("\n💡 修改 models.yml 来配置你自己的模型")
        return

    if args.guide == "orchestrator":
        OrchestratorGuide.print_orchestrator_guide()
        return

    if args.template:
        task_desc = args.task or "请在这里填写具体任务"
        template = OrchestratorGuide.get_preset_task_template(args.template, task_desc)
        print(f"\n📋 sessions_spawn 任务描述模板 (role={args.template})")
        print("=" * 60)
        print(template)
        print("=" * 60)
        print("\n💡 使用方式：")
        print('sessions_spawn({')
        print(f'    "task": "{task_desc[:30]}...",')
        print(f'    "label": "task-{args.template}"')
        print('})')
        return

    if args.demo:
        run_demo()
        return

    engine = MultiAgentEngine(
        max_concurrent=args.max_concurrent,
        continue_on_error=True
    )

    # JSON pipeline 模式
    if args.config:
        config = load_pipeline(args.config)
        run_pipeline(config, engine)
        return

    # 命令行参数模式
    if not args.agents and not args.task:
        parser.print_help()
        sys.exit(1)

    # --auto-mode：根据任务内容自动选择模式
    if args.auto_mode and args.task:
        from scripts.router import TaskRouter
        router = TaskRouter()
        rec = router.recommend_mode(args.task)
        mode_map = {"orchestrator": "parallel", "pipeline": "parallel", "hybrid": "hybrid"}
        args.mode = mode_map.get(rec["mode"], "parallel")
        mode_emoji = {"orchestrator": "🎯", "pipeline": "🔄", "hybrid": "🔀"}.get(rec["mode"], "")
        print(f"\n🧭 自动模式选择: {mode_emoji} {rec['mode'].upper()}")
        print(f"   原因: {rec['reason']}\n")

    # 构建任务列表
    tasks: List[AgentTask] = []
    if args.agents:
        for i, agent_str in enumerate(args.agents):
            t = parse_agent_str(agent_str)
            t.label = t.label or f"agent_{i+1}"
            t.thinking = args.thinking
            t.timeout = args.timeout
            tasks.append(t)
    elif args.task:
        tasks.append(AgentTask(
            task=args.task,
            thinking=args.thinking,
            timeout=args.timeout,
            label="agent_1"
        ))

    print(f"\n{'='*60}")
    print("🐝 OpenClaw Multi-Agent")
    print(f"{'='*60}")

    start = time.time()

    # 混合模式
    if args.mode == "hybrid":
        if not args.task:
            print("❌ 混合模式需要 --task 参数（作为草稿生成的主题）")
            sys.exit(1)

        print(f"模式: 🔀 hybrid | 调研任务: {len(tasks)} | 草稿数: {args.num_drafts}")
        print(f"{'='*60}\n")

        # research tasks = 用户传入的 --agents（或单 task）
        research_tasks = tasks if tasks else [AgentTask(
            task=f"搜索和整理关于以下主题的资料：{args.task}",
            label="researcher_1", timeout=args.timeout
        )]

        # 草稿模板
        draft_template = (
            "以下是调研结果：\n\n{research}\n\n"
            f"请基于以上资料，撰写一篇关于「{args.task}」的完整文章/报告。"
            "要求：结构清晰，语言流畅，有观点有数据。"
        )

        hybrid_result = engine.run_hybrid(
            research_tasks=research_tasks,
            draft_task_template=draft_template,
            num_drafts=args.num_drafts,
        )

        stats = hybrid_result["stats"]
        print(f"\n{'='*60}")
        print("📡 Phase 1 调研结果")
        print(f"{'='*60}")
        research_agg = engine.aggregate(
            hybrid_result["research_results"],
            mode="concatenate",
            original_task=args.task
        )
        print(research_agg)
        engine.print_stats(hybrid_result["research_results"])

        print(f"\n{'='*60}")
        print(f"✍️  Phase 2 草稿对比（共 {stats['phase2_ok']}/{stats['phase2_total']} 版）")
        print(f"{'='*60}")
        draft_agg = engine.aggregate(
            hybrid_result["draft_results"],
            mode="compare",
            original_task=args.task
        )
        print(draft_agg)
        engine.print_stats(hybrid_result["draft_results"])

        print(f"\n总耗时（挂钟时间）: {time.time() - start:.1f}s")
        return

    # 普通模式（parallel / sequential）
    print(f"模式: {args.mode} | 并发: {args.max_concurrent} | 聚合: {args.aggregation}")
    print(f"任务数: {len(tasks)}")
    for t in tasks:
        print(f"  [{t.label}] model={t.model} | {t.task[:50]}...")
    print(f"{'='*60}\n")

    if args.mode == "parallel":
        results = engine.run_parallel(tasks)
    else:
        results = engine.run_sequential(tasks)

    aggregated = engine.aggregate(
        results,
        mode=args.aggregation,
        original_task=args.task or "多任务"
    )

    print(f"\n{'='*60}")
    print("✅ 最终结果")
    print(f"{'='*60}")
    print(aggregated)

    engine.print_stats(results)
    print(f"\n总耗时（挂钟时间）: {time.time() - start:.1f}s")


if __name__ == "__main__":
    main()
