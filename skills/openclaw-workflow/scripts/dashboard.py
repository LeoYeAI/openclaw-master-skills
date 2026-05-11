#!/usr/bin/env python3
"""
OpenClaw Workflow Dashboard — Streamlit 可视化面板

功能:
- 工作流 YAML 编辑器
- Mermaid.js 流程图预览
- 一键运行工作流
- 实时执行监控
- 运行历史记录
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# 确保 engine 包可导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import streamlit as st
    import yaml
except ImportError:
    print("❌ 需要安装依赖: pip install streamlit pyyaml")
    print(f"   运行: pip install -r {Path(__file__).with_name('requirements.txt')}")
    sys.exit(1)

from engine.engine import WorkflowEngine
from engine.schema import validate_workflow

# ── 页面配置 ──────────────────────────────────────────────

st.set_page_config(
    page_title="OpenClaw Workflow Dashboard",
    page_icon="🔀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 常量 ──────────────────────────────────────────────────

SKILL_DIR = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = SKILL_DIR / "references" / "examples"
OPENCLAW_WORKFLOWS_DIR = Path(os.path.expanduser("~/.openclaw/workspace/workflows"))
RUNS_DIR = WorkflowEngine.RUNS_DIR


# ── 工具函数 ──────────────────────────────────────────────

def yaml_to_mermaid(data: dict) -> str:
    """将 YAML 工作流转换为 Mermaid 流程图"""
    lines = ["graph TD"]
    steps = data.get("steps", [])

    for i, step in enumerate(steps):
        step_id = step.get("id") or f"step_{i}"
        step_name = step.get("name") or step_id
        step_type = step.get("type", "log")

        # 节点样式
        if step_type == "condition":
            lines.append(f'    {step_id}{{{{{step_name}}}}}')
        elif step_type == "loop":
            lines.append(f'    {step_id}[["🔁 {step_name}"]]')
        elif step_type == "llm":
            lines.append(f'    {step_id}["🤖 {step_name}"]')
        elif step_type == "skill":
            lines.append(f'    {step_id}["⚡ {step_name}"]')
        elif step_type == "script":
            lines.append(f'    {step_id}["💻 {step_name}"]')
        elif step_type == "http":
            lines.append(f'    {step_id}["🌐 {step_name}"]')
        elif step_type == "code":
            lines.append(f'    {step_id}["🐍 {step_name}"]')
        else:
            lines.append(f'    {step_id}["{step_name}"]')

        # 连线
        if i > 0:
            prev_id = steps[i - 1].get("id") or f"step_{i-1}"
            prev_type = steps[i - 1].get("type", "log")

            if prev_type == "condition":
                # 条件分支的连线在子步骤中处理
                lines.append(f'    {prev_id} -->|"then"| {step_id}')
            else:
                lines.append(f'    {prev_id} --> {step_id}')

        # 条件分支子步骤
        if step_type == "condition":
            for branch in ("then", "else"):
                sub_steps = step.get(branch, [])
                for j, sub in enumerate(sub_steps):
                    sub_id = sub.get("id") or f"{step_id}_{branch}_{j}"
                    sub_name = sub.get("name") or sub_id
                    lines.append(f'    {sub_id}["{sub_name}"]')
                    if j == 0:
                        label = "是" if branch == "then" else "否"
                        lines.append(f'    {step_id} -->|"{label}"| {sub_id}')
                    else:
                        prev_sub_id = sub_steps[j - 1].get("id") or f"{step_id}_{branch}_{j-1}"
                        lines.append(f'    {prev_sub_id} --> {sub_id}')

        # 循环子步骤
        if step_type == "loop":
            do_steps = step.get("do") or step.get("steps", [])
            for j, sub in enumerate(do_steps):
                sub_id = sub.get("id") or f"{step_id}_do_{j}"
                sub_name = sub.get("name") or sub_id
                lines.append(f'    {sub_id}["{sub_name}"]')
                if j == 0:
                    lines.append(f'    {step_id} -->|"每项"| {sub_id}')
                else:
                    prev_sub_id = do_steps[j - 1].get("id") or f"{step_id}_do_{j-1}"
                    lines.append(f'    {prev_sub_id} --> {sub_id}')

    # 样式
    lines.append("")
    lines.append("    classDef condition fill:#fff3cd,stroke:#ffc107")
    lines.append("    classDef loop fill:#d1ecf1,stroke:#17a2b8")
    lines.append("    classDef llm fill:#e2d5f1,stroke:#6f42c1")

    for i, step in enumerate(steps):
        step_id = step.get("id") or f"step_{i}"
        step_type = step.get("type")
        if step_type == "condition":
            lines.append(f"    class {step_id} condition")
        elif step_type == "loop":
            lines.append(f"    class {step_id} loop")
        elif step_type == "llm":
            lines.append(f"    class {step_id} llm")

    return "\n".join(lines)


def load_workflow_files() -> dict:
    """
    加载可在面板中快速选择的工作流文件。

    设计目标:
    - 示例目录: skill/references/examples
    - OpenClaw 默认目录: ~/.openclaw/workspace/workflows
    仅扫描上述固定目录，不扫描整个工作区。
    """
    workflows = {}
    seen_real_paths = set()

    # 1) 示例目录 (优先)
    if EXAMPLES_DIR.exists():
        for ext in ("*.yaml", "*.yml"):
            for f in sorted(EXAMPLES_DIR.glob(ext)):
                real = str(f.resolve())
                if real in seen_real_paths:
                    continue
                seen_real_paths.add(real)
                key = f"示例/{f.stem}"
                workflows[key] = {
                    "content": f.read_text(encoding="utf-8"),
                    "path": str(f),
                    "source": "示例",
                }

    # 2) OpenClaw 工作流目录
    if OPENCLAW_WORKFLOWS_DIR.exists():
        for ext in ("*.yaml", "*.yml"):
            for f in sorted(OPENCLAW_WORKFLOWS_DIR.rglob(ext)):
                real = str(f.resolve())
                if real in seen_real_paths:
                    continue
                seen_real_paths.add(real)
                rel = f.relative_to(OPENCLAW_WORKFLOWS_DIR)
                key = f"工作流/{rel.as_posix()}"
                workflows[key] = {
                    "content": f.read_text(encoding="utf-8"),
                    "path": str(f),
                    "source": "OpenClaw 工作流目录",
                }

    return workflows


# ── 侧边栏 ──────────────────────────────────────────────

with st.sidebar:
    st.title("🔀 OpenClaw Workflow")
    st.caption("确定性工作流编排引擎")

    page = st.radio(
        "导航",
        ["📝 编辑器", "▶️ 运行", "📊 历史", "📚 帮助"],
        label_visibility="collapsed",
    )

    st.divider()

    # 快速加载工作流
    workflows = load_workflow_files()
    selected_workflow = "(选择一个工作流)"
    if workflows:
        st.subheader("📂 工作流")
        selected_workflow = st.selectbox(
            "选择工作流",
            ["(选择一个工作流)"] + list(workflows.keys()),
            label_visibility="collapsed",
        )
        if selected_workflow != "(选择一个工作流)":
            st.caption(workflows[selected_workflow]["path"])

    st.divider()
    st.caption(f"OpenClaw Workflow v1.0.0")


# ── 编辑器页面 ────────────────────────────────────────────

if page == "📝 编辑器":
    st.header("📝 工作流编辑器")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("YAML 定义")

        # 初始化编辑器内容
        if "yaml_content" not in st.session_state:
            default_yaml = "# 在此编写工作流 YAML\nflow_id: my_flow\nsteps:\n  - id: step1\n    type: log\n    message: Hello!"
            for k, v in workflows.items():
                if k.endswith("/basic_test") or k.endswith("/basic_test.yaml"):
                    default_yaml = v["content"]
                    break
            st.session_state.yaml_content = default_yaml

        # 加载示例
        if workflows and selected_workflow != "(选择一个工作流)":
            st.session_state.yaml_content = workflows[selected_workflow]["content"]

        yaml_text = st.text_area(
            "工作流 YAML",
            value=st.session_state.yaml_content,
            height=500,
            label_visibility="collapsed",
        )
        st.session_state.yaml_content = yaml_text

        # 验证按钮
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        with btn_col1:
            if st.button("✅ 验证", use_container_width=True):
                try:
                    data = yaml.safe_load(yaml_text)
                    is_valid, errors = validate_workflow(data)
                    if is_valid:
                        st.success("验证通过!")
                    else:
                        for e in errors:
                            if e.severity == "error":
                                st.error(str(e))
                            else:
                                st.warning(str(e))
                except yaml.YAMLError as e:
                    st.error(f"YAML 语法错误: {e}")

        with btn_col2:
            if st.button("💾 保存", use_container_width=True):
                save_name = st.session_state.get("save_name", "my_workflow")
                save_path = EXAMPLES_DIR / f"{save_name}.yaml"
                EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)
                save_path.write_text(yaml_text, encoding="utf-8")
                st.success(f"已保存: {save_path.name}")

        with btn_col3:
            if st.button("▶️ 运行", use_container_width=True, type="primary"):
                st.session_state.run_yaml = yaml_text
                st.session_state.run_trigger = True

    with col2:
        st.subheader("🔀 流程图预览")

        try:
            data = yaml.safe_load(yaml_text)
            if isinstance(data, dict) and "steps" in data:
                mermaid_code = yaml_to_mermaid(data)
                st.code(mermaid_code, language="mermaid")

                # 工作流信息
                st.divider()
                st.subheader("📋 工作流信息")
                info_cols = st.columns(3)
                with info_cols[0]:
                    st.metric("步骤数", len(data.get("steps", [])))
                with info_cols[1]:
                    types = [s.get("type", "?") for s in data.get("steps", [])]
                    st.metric("节点类型", len(set(types)))
                with info_cols[2]:
                    vars_count = len(data.get("variables", {}))
                    st.metric("变量数", vars_count)

                # 步骤列表
                st.divider()
                for i, step in enumerate(data.get("steps", [])):
                    with st.expander(
                        f"步骤 {i+1}: {step.get('name', step.get('id', f'step_{i}'))} "
                        f"({step.get('type', '?')})"
                    ):
                        st.json(step)
            else:
                st.info("请输入有效的工作流 YAML")
        except yaml.YAMLError:
            st.warning("YAML 语法错误，无法预览")
        except Exception as e:
            st.error(f"预览错误: {e}")


# ── 运行页面 ──────────────────────────────────────────────

elif page == "▶️ 运行":
    st.header("▶️ 运行工作流")

    # 选择工作流来源
    source = st.radio("工作流来源", ["从编辑器", "从文件"], horizontal=True)

    if source == "从文件":
        workflow_file = st.text_input(
            "工作流文件路径",
            placeholder="/path/to/workflow.yaml",
        )

        if st.button("🚀 执行", type="primary") and workflow_file:
            with st.spinner("执行中..."):
                log_container = st.empty()
                logs = []

                def log_cb(msg, level):
                    logs.append(f"[{level}] {msg}")
                    log_container.code("\n".join(logs[-30:]))

                try:
                    engine = WorkflowEngine(
                        workflow_file=workflow_file,
                        log_callback=log_cb,
                    )
                    record = engine.run()

                    if record.status == "success":
                        st.success(f"✅ 工作流执行成功! (共 {len(record.steps)} 步)")
                    else:
                        st.error(f"❌ 工作流执行失败: {record.status}")

                    st.json(record.to_dict())
                except Exception as e:
                    st.error(f"执行错误: {e}")

    else:
        # 从编辑器
        yaml_text = st.session_state.get("yaml_content", "")

        if yaml_text:
            st.code(yaml_text[:500] + ("..." if len(yaml_text) > 500 else ""), language="yaml")

        run_trigger = st.session_state.get("run_trigger", False)

        if st.button("🚀 执行", type="primary") or run_trigger:
            st.session_state.run_trigger = False
            yaml_to_run = st.session_state.get("run_yaml") or yaml_text

            if not yaml_to_run:
                st.warning("请先在编辑器中编写工作流")
            else:
                with st.spinner("执行中..."):
                    log_container = st.empty()
                    logs = []

                    def log_cb(msg, level):
                        logs.append(f"[{level}] {msg}")
                        log_container.code("\n".join(logs[-30:]))

                    try:
                        data = yaml.safe_load(yaml_to_run)
                        engine = WorkflowEngine(
                            workflow_data=data,
                            log_callback=log_cb,
                        )
                        record = engine.run()

                        if record.status == "success":
                            st.success(f"✅ 工作流执行成功! (共 {len(record.steps)} 步)")
                        else:
                            st.error(f"❌ 工作流执行失败: {record.status}")

                        # 步骤详情
                        st.divider()
                        st.subheader("📋 步骤详情")
                        for s in record.steps:
                            icon = {"success": "✅", "failed": "❌", "skipped": "⏭️"}.get(s.status, "❓")
                            with st.expander(f"{icon} {s.step_name} [{s.step_type}] — {s.status}"):
                                st.json(s.to_dict())
                    except Exception as e:
                        st.error(f"执行错误: {e}")


# ── 历史页面 ──────────────────────────────────────────────

elif page == "📊 历史":
    st.header("📊 运行历史")

    runs = WorkflowEngine.list_runs()

    if not runs:
        st.info("暂无运行记录。运行一个工作流后，记录将显示在这里。")
    else:
        for run in runs:
            icon = {"success": "✅", "failed": "❌", "aborted": "⛔"}.get(run["status"], "❓")
            with st.expander(
                f"{icon} {run['flow_id']} — {run['status']} "
                f"({run.get('started_at', 'N/A')[:19]})"
            ):
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("状态", run["status"])
                with col_b:
                    st.metric("步骤数", len(run.get("steps", [])))
                with col_c:
                    st.metric("运行ID", run["run_id"][:8])

                st.json(run)


# ── 帮助页面 ──────────────────────────────────────────────

elif page == "📚 帮助":
    st.header("📚 OpenClaw Workflow 使用指南")

    st.markdown("""
    ## 节点类型

    | 类型 | 说明 | 图标 |
    |------|------|------|
    | `script` | 运行 Shell/Python 脚本 | 💻 |
    | `llm` | 调用 LLM 推理 | 🤖 |
    | `skill` | 调用 OpenClaw Skill | ⚡ |
    | `condition` | If-Else 分支 | 🔀 |
    | `loop` | For-Each 循环 | 🔁 |
    | `wait` | 延时等待 | ⏰ |
    | `set` | 设置变量 | 📌 |
    | `log` | 记录日志 | 📝 |
    | `http` | HTTP 请求 | 🌐 |
    | `code` | 内联 Python | 🐍 |
    | `agent` | 调用 Agent | 🤖 |

    ## 变量语法

    ```
    {{variable}}              普通变量
    {{step_id.output}}        步骤输出
    {{step_id.output.field}}  嵌套字段
    {{env.HOME}}              环境变量
    {{item}}                  循环当前元素
    ```

    ## 错误处理

    ```yaml
    on_error: stop    # 停止工作流
    on_error: skip    # 跳过并继续
    on_error: retry   # 自动重试
    on_error: ask     # 人工介入
    ```

    ## 工作流存放位置

    默认会被自动发现的目录（固定目录）：

    ```
    {baseDir}/references/examples
    ~/.openclaw/workspace/workflows
    ```

    推荐把你自己维护的流程放在：

    ```
    ~/.openclaw/workspace/workflows
    ```

    ## CLI 命令

    ```bash
    python3 {baseDir}/scripts/openclaw_workflow.py execute <file.yaml>   # 运行
    python3 {baseDir}/scripts/openclaw_workflow.py validate <file.yaml>  # 验证
    python3 {baseDir}/scripts/openclaw_workflow.py list                  # 列出
    python3 {baseDir}/scripts/openclaw_workflow.py runs                  # 历史
    python3 {baseDir}/scripts/openclaw_workflow.py dashboard             # 面板
    ```
    """)
