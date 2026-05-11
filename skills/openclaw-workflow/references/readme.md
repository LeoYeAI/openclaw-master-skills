# 项目名称：OpenClaw Workflow

**定位：** 为 OpenClaw 打造的确定性逻辑编排引擎 (Deterministic Orchestration Engine)

## 1. 项目背景与愿景

OpenClaw 作为一个 LLM Agent 框架，其核心优势在于灵活性。但在处理**固定流程任务**（如发票整理、固件打包、每日简报）时，完全依靠模型推理会导致步骤跳漏、逻辑幻觉等不稳定现象。

**OpenClaw Workflow 的目标：** 在不破坏 OpenClaw 灵活性的前提下，引入一套“剧本化”的执行机制。让 Agent 在特定任务下按照预设的 **判断、循环、脚本** 逻辑执行，实现 100% 的确定性。

---

## 2. 核心设计原则 (不重复造轮子)

* **原生集成：** 严禁重新实现模型调用和基础能力。必须调用 OpenClaw 的 `agent.ask()` 进行对话，调用 `agent.execute_skill()` 驱动现有 Skill。
* **逻辑解耦：** 流程控制（走哪一步）由引擎负责，语义理解（这一步是什么意思）由 LLM 负责。
* **轻量化：** 后端采用纯 Python，前端采用 Streamlit，确保部署简单。

---

## 3. 功能架构模块

### A. 剧本定义 (Workflow Schema)

使用 YAML 定义流程。每个流程是一个节点（Node）组成的有向无环图（DAG）或序列。

* **Skill 节点：** 调用 OpenClaw 已有的原子能力。
* **LLM 节点：** 调用模型进行处理，支持强格式化（JSON Schema）校验。
* **脚本节点 (Script/Code)：**
* **Inline:** 直接在 YAML 中编写 Python 代码段。
* **External:** 调用外部 `.py` 脚本。


* **控制流节点 (Logic)：**
* **Condition (If-Else):** 基于变量判断分支。
* **Loop (For-Each):** 遍历列表执行子任务。
* **Wait:** 固定延时或等待信号。



### B. 执行引擎 (Core Engine)

* **状态机管理器：** 维护流程当前所处的节点，支持“人工介入”模式（在关键步骤暂停并询问用户）。
* **全局上下文 (Context)：** 一个变量管道，负责在节点间传递数据。例如：`{{step_1.output.file_path}}`。
* **沙箱环境：** 一个安全的 Python 环境，用于执行 YAML 中的 `Code` 节点，并能读写 Context 变量。
* **重试与持久化：** 记录每一步的执行快照。若流程中断，支持从断点处重连。

### C. 可视化面板 (Dashboard)

基于 **Streamlit** 构建。

* **剧本管理：** 增删改查 YAML 剧本。
* **流程预览：** 利用 **Mermaid.js** 将 YAML 文本实时渲染为流程图。
* **监控台：** 实时观察流程运行进度，手动干预或输入参数。

---

## 4. 关键技术细节描述

### 变量传递机制

引擎必须实现一个解析器，在每个节点执行前，扫描其参数中的 `{{...}}` 占位符，并从全局 Context 中替换为真实值。

### 循环与作用域

当执行 `For-Each` 循环时，引擎需要为循环内部的节点创建一个“局部作用域”，确保并发或嵌套循环时变量不会冲突。

### 异常处理

YAML 中可配置 `on_error` 策略：

* `retry`: 自动重试 N 次。
* `ask`: 通过对话渠道询问用户如何处理。
* `stop`: 终止流程并保存现场。

---

## 5. 典型应用示例 (YAML 逻辑预览)

```yaml
flow_id: "auto_invoice_archiver"
steps:
  - id: "list_mail"
    type: "skill"
    action: "email.fetch"
    export: "mails"

  - id: "process_loop"
    type: "loop"
    foreach: "{{mails}}"
    do:
      - type: "llm"
        prompt: "分析此邮件是否包含发票: {{item.subject}}"
        export: "is_invoice"
      
      - type: "condition"
        if: "{{is_invoice == True}}"
        then:
          - use_skill: "nas.upload"
            args: { file: "{{item.attachment}}", path: "/invoices" }

```

---

## 6. 开发路径建议 (给 AI 的任务拆解)

1. **Phase 1 (MVP):** 实现 `engine.py`，支持解析简单的顺序 YAML 流程，并能调用 OpenClaw 的 `execute_skill`。
2. **Phase 2 (Logic):** 引入 `Context` 变量池和 `if/loop` 控制逻辑。
3. **Phase 3 (Bridge):** 将 Engine 包装成一个 OpenClaw Skill，实现主模型对工作流的触发。
4. **Phase 4 (UI):** 编写 Streamlit 界面，实现可视化编辑和监控。
