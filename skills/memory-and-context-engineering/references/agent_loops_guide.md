# Agent Loops 进阶指导

> 本文档由浅入深讲解 Agent Loop（智能体循环）的核心概念、技术演进与工程实践，帮助开发者理解从简单循环到复杂状态机架构的技术路径。

## 目录

1. [概念起源与演进](#一概念起源与演进)
2. [核心架构：Agent Execution Flow](#二核心架构agent-execution-flow)
3. [架构升级：Cyclic Graph](#三架构升级cyclic-graph)
4. [模块化演进：Skills 与编排](#四模块化演进skills-与编排)
5. [工程化挑战与最佳实践](#五工程化挑战与最佳实践)
6. [总结与展望](#六总结与展望)

---

## 一、概念起源与演进

### 1.1 什么是 Agent Loop？

**Agent Loop（智能体循环）** 是现代 LLM Agent 的核心架构模式，指 Agent 通过"感知-决策-行动-观察"的循环，自主完成复杂任务。

```
┌─────────────────────────────────────────────┐
│                                             │
│    ┌──────────┐                             │
│    │  用户输入  │                            │
│    └────┬─────┘                             │
│         ▼                                   │
│    ┌──────────┐    ┌──────────┐             │
│    │  Thought │───▶│  Action  │             │
│    │  (思考)   │    │  (行动)   │             │
│    └──────────┘    └────┬─────┘             │
│         ▲               │                   │
│         │               ▼                   │
│    ┌────┴─────┐    ┌──────────┐             │
│    │  判断完成  │◀───│Observation│            │
│    │          │    │  (观察)   │             │
│    └────┬─────┘    └──────────┘             │
│         │                                   │
│         ▼                                   │
│    ┌──────────┐                             │
│    │ 最终答案  │                             │
│    └──────────┘                             │
│                                             │
└─────────────────────────────────────────────┘
```

### 1.2 发展时间线

| 阶段 | 时间 | 关键事件 | 技术特征 |
|------|------|----------|----------|
| **理论基础** | 2022年前 | 强化学习、控制论 | 马尔可夫决策过程 |
| **范式确立** | 2022.12 | ReAct 论文发布 | Thought-Action-Observation |
| **概念爆发** | 2023.3-4 | AutoGPT 走红、LangChain 推动 | 自主循环、工具调用 |
| **工程深化** | 2023底-2024 | LangGraph、多智能体 | 状态机、有向循环图 |

### 1.3 关键里程碑：ReAct 范式

**ReAct: Synergizing Reasoning and Acting in Language Models**（2022年12月，普林斯顿大学）

这是现代 Agent Loop 的技术基石，定义了标准的循环结构：

```
Thought（思考）→ Action（行动）→ Observation（观察）→ 重复
```

**核心创新**：
- 将"推理（Reasoning）"和"行动（Acting）"结合
- 让 LLM 能够在执行中反思和调整
- 奠定了可观测、可调试的 Agent 架构基础

---

## 二、核心架构：Agent Execution Flow

### 2.1 本质理解

Agent Execution Flow 的核心是一个**带有状态管理的 `while` 循环**，由 LLM 作为控制器，不断调用工具直到任务完成。

### 2.2 核心伪代码

```python
def agent_execution_flow(user_input, llm, tools, max_iterations=5):
    """Agent Loop 的核心逻辑"""
    
    # 1. 初始化上下文
    chat_history = [f"Human: {user_input}"]
    current_iteration = 0
    
    while current_iteration < max_iterations:
        # 2. 构造 Prompt（历史 + 工具描述 + 当前状态）
        prompt = build_react_prompt(chat_history, tools)
        
        # 3. LLM 推理（生成 Thought & Action）
        llm_output = llm.generate(prompt)
        
        # 4. 解析输出（关键：判断继续还是结束）
        action, action_input, final_answer = parse_llm_output(llm_output)
        
        if final_answer:
            return final_answer  # 任务完成，退出循环
        
        # 5. 执行工具
        try:
            observation = tools[action].run(action_input)
        except Exception as e:
            observation = f"Error: {str(e)}"
        
        # 6. 记录观察，进入下一轮
        chat_history.append(f"AI Thought: {llm_output}")
        chat_history.append(f"Observation: {observation}")
        
        current_iteration += 1
    
    return "Error: Max iterations reached"
```

### 2.3 LangChain 标准实现

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub

# 1. 定义工具
tools = [
    Tool(name="Search", func=search.run, description="搜索当前事件"),
    Tool(name="Calculator", func=calc, description="数学计算")
]

# 2. 构建 Agent
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
prompt = hub.pull("hwchase17/react")  # ReAct 提示词模板
agent = create_react_agent(llm, tools, prompt)

# 3. 执行器（The Loop Engine）
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,           # 打印执行细节
    max_iterations=3,       # 安全熔断
    handle_parsing_errors=True  # 容错处理
)

# 4. 执行
response = agent_executor.invoke({"input": "2024年奥斯卡最佳影片是什么？"})
```

### 2.4 执行流内部细节

```
> Entering new AgentExecutor chain...
--- 第 1 轮循环 ---
Thought: 需要搜索2024年奥斯卡最佳影片信息
Action: Search
Action Input: "2024年奥斯卡最佳影片"
Observation: Oppenheimer (奥本海默)
Thought: 已获得答案，可以回答
Final Answer: 2024年奥斯卡最佳影片是《奥本海默》。

> Finished chain.
```

**关键机制**：
1. **Prompt 动态组装**：每轮拼接 System Prompt + Chat History + Tools + Last Observation
2. **输出解析器**：正则匹配 `Final Answer` 或 `Action`
3. **中间状态存储**：`IntermediateSteps` 列表记录每轮的 Action 和结果

### 2.5 传统 Loop 的局限

| 问题 | 表现 | 影响 |
|------|------|------|
| **控制流线性** | 难以处理复杂分支 | 无法实现条件跳转 |
| **状态管理简单** | 仅维护消息列表 | 无法存储复杂中间结果 |
| **调试困难** | 黑盒循环 | 难以复现问题 |
| **人机协同弱** | 缺乏中断机制 | 敏感操作无法审批 |

---

## 三、架构升级：Cyclic Graph

### 3.1 从循环到状态机

**Cyclic Graph（有向循环图）** 是 Agent Loop 的进化形态，以 LangGraph 为代表。它将"循环"从隐式的 `while` 变成了显式的图结构。

```
传统 Loop (AgentExecutor):
  Start → [黑盒循环] → End

Cyclic Graph (LangGraph):
  Start → Node A → Condition → Node B → Node A (循环)
                      ↓
                     End
```

### 3.2 核心概念映射

| 概念 | 定义 | 作用 |
|------|------|------|
| **State** | 强类型对象（TypedDict/Pydantic） | 贯穿整个执行流的全局状态 |
| **Node** | 执行具体逻辑的函数 | 接收状态，返回状态更新 |
| **Edge** | 节点间跳转逻辑 | 定义控制流 |
| **Conditional Edge** | 条件跳转 | 实现分支逻辑 |
| **Checkpoint** | 状态持久化 | 断点续传、时间旅行 |

### 3.3 代码实现对比

**传统 AgentExecutor（隐式循环）**：
```python
# 黑盒：不知道内部循环了几次，难以打断
response = agent_executor.invoke({"input": "写篇文章"})
```

**Cyclic Graph（显式循环）**：
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

# 1. 定义状态
class State(TypedDict):
    draft: str
    review_passed: bool

# 2. 定义节点
def write_node(state):
    return {"draft": "文章草稿..."}

def review_node(state):
    return {"review_passed": "好" in state['draft']}

# 3. 构建图
workflow = StateGraph(State)
workflow.add_node("writer", write_node)
workflow.add_node("reviewer", review_node)

# 4. 定义边（显式循环）
workflow.set_entry_point("writer")
workflow.add_edge("writer", "reviewer")
workflow.add_conditional_edges(
    "reviewer",
    lambda x: "writer" if not x['review_passed'] else END
)

# 5. 编译并运行（支持检查点）
app = workflow.compile(checkpointer=MemorySaver())
```

### 3.4 Cyclic Graph 核心优势

#### 1. 流程控制确定性
- **代码控制流程，LLM 控制逻辑**
- 降低幻觉导致的流程失控风险

#### 2. 原生人机协同
```python
# 在敏感节点前设置断点
workflow.add_node("send_email", send_email_node)
workflow.interrupt_before = ["send_email"]  # 执行前暂停

# 恢复执行
app.update_state(config, {"approved": True})
app.invoke(None, config)  # 从断点继续
```

#### 3. 复杂状态管理
```python
# 全局状态 Schema
class AgentState(TypedDict):
    messages: list[Message]
    current_task: str
    error_count: int
    user_preferences: dict
```

#### 4. 可调试性与可观测性
- 清晰的执行路径
- 支持时间旅行（从任意检查点恢复）
- 状态差异日志

---

## 四、模块化演进：Skills 与编排

### 4.1 Skills 概念起源

**Skills（技能）** 概念主要由微软 Semantic Kernel 推动，核心思想是将 AI 能力封装为可复用的模块。

| 特性 | Skills 定义 | 局限 |
|------|-------------|------|
| **形态** | 函数、插件、API 封装 | 静态库 |
| **优势** | 可复用、可组合 | 缺乏运行时引擎 |
| **痛点** | 状态管理弱 | 多技能协作困难 |

### 4.2 LangGraph 与 Skills 的关系

**LangGraph 将 Skills 从静态定义提升为动态的、有状态的图节点。**

```
┌─────────────────────────────────────────────────────┐
│                   LangGraph Workflow                │
│                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐      │
│  │  Skill A │───▶│  Skill B │───▶│  Skill C │      │
│  │ (子图)    │    │ (子图)    │    │ (子图)    │      │
│  └──────────┘    └──────────┘    └──────────┘      │
│       ▲                               │            │
│       └───────────────────────────────┘            │
│                   共享 State                        │
└─────────────────────────────────────────────────────┘
```

### 4.3 技术演进程

| 维度 | 早期 Skills | LangGraph 赋能后 |
|------|-------------|------------------|
| **形态** | 函数、API 封装 | **子图（Sub-Graph）**、独立 Agent |
| **调度** | LLM 自主决定（不可控） | **代码定义的条件边**（可控） |
| **状态** | 无状态或简单上下文 | **持久化状态（Checkpoint）** |
| **错误处理** | 抛出异常 | **显式错误边**（失败 → 通知人类） |
| **复用性** | 代码级复用 | **架构级复用** |

### 4.4 未来：Skill Graph

两者结合催生的新架构模式：**Skill Graph**

- **节点即技能**：每个节点是封装好的技能微服务
- **边即逻辑**：连线代表业务逻辑
- **LangGraph 的角色**：Skill 的操作系统

---

## 五、工程化挑战与最佳实践

### 5.1 状态管理

#### 问题
- **状态膨胀**：`messages` 列表无限增长
- **模式冲突**：多节点同时修改同一字段
- **版本演进**：修改 Schema 后旧 Checkpoint 无法加载

#### 解决方案

```python
# 自定义状态归约器
def reduce_messages(left: list, right: list) -> list:
    """只保留最新 5 条消息"""
    return (left + right)[-5:]

# 状态定义
class AgentState(TypedDict):
    messages: Annotated[list, reduce_messages]  # 使用自定义归约
    step_count: Annotated[int, operator.add]    # 累加
```

### 5.2 循环控制

#### 问题
- 逻辑死循环
- LLM 重复生成相同输出
- 递归限制设置不当

#### 解决方案

```python
class AgentState(TypedDict):
    step_count: int
    last_action_hash: str

def should_continue(state):
    # 显式计数器
    if state["step_count"] > 10:
        return END
    
    # 多样性检测
    current_hash = hash(state.get("last_action", ""))
    if current_hash == state.get("last_action_hash"):
        return "fallback"  # 重复则走备用路径
    
    return "continue"
```

### 5.3 LLM 路由可靠性

#### 问题
- LLM 幻觉出不存在的节点名
- 结构化输出格式错误

#### 解决方案

```python
from pydantic import BaseModel

class RouteDecision(BaseModel):
    next_node: str
    reason: str

# 强制结构化输出
router = llm.with_structured_output(RouteDecision)

def route_node(state):
    result = router.invoke(state["messages"])
    
    # 路由白名单验证
    allowed_nodes = ["research", "write", "review", "end"]
    if result.next_node not in allowed_nodes:
        return "fallback"  # 非法路由
    
    return result.next_node
```

### 5.4 持久化与检查点

#### 问题
- 检查点存储爆炸
- 线程隔离泄露
- 恢复后状态不一致

#### 解决方案

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# 使用 TTL 清理旧检查点
checkpointer = SqliteSaver(
    connection=conn,
    ttl_days=7  # 7天后自动清理
)

# 严格线程隔离
config = {
    "configurable": {
        "thread_id": f"user_{user_id}_session_{session_id}"
    }
}
```

### 5.5 人机协同

#### 问题
- 等待超时
- 状态篡改风险
- 上下文丢失

#### 解决方案

```python
# 中断超时监控（应用层实现）
async def check_interrupt_timeout(thread_id: str, timeout_hours: int = 24):
    state = await get_interrupt_state(thread_id)
    if state and state["interrupted_at"]:
        elapsed = datetime.now() - state["interrupted_at"]
        if elapsed > timedelta(hours=timeout_hours):
            await cancel_task(thread_id)
            await notify_user(thread_id, "任务已超时取消")

# 恢复提示词注入
RESUME_PROMPT = """
你之前被用户中断了，这是用户修改后的状态：
{modified_state}

请基于最新状态继续完成任务。
"""
```

### 5.6 可观测性

#### 最佳实践

```python
# 状态差异日志
def log_state_diff(node_name: str, old_state: dict, new_state: dict):
    diff = compute_diff(old_state, new_state)
    logger.info(f"Node {node_name} changed: {diff}")

# 集成 LangSmith（官方推荐）
# 自动追踪每个节点的输入/输出、耗时、Token消耗
```

### 5.7 最佳实践速查表

| 问题领域 | 核心难点 | 解决方案 |
|----------|----------|----------|
| **状态** | 无限增长、冲突 | 自定义 Reducer、定期 Pruning |
| **循环** | 死循环、重复 | Step Counter、多样性检测 |
| **路由** | LLM 幻觉 | Structured Output、白名单验证 |
| **持久化** | 存储爆炸 | Checkpoint TTL、线程隔离 |
| **人机** | 超时、篡改 | 应用层监控、状态验证 |
| **调试** | 黑盒 | LangSmith 追踪、状态 Diff |

---

## 六、总结与展望

### 6.1 架构演进脉络

```
2022年前    2022.12      2023.3-4       2023底-2024
   │           │            │               │
   ▼           ▼            ▼               ▼
控制论    → ReAct范式 → AgentExecutor → Cyclic Graph
  RL        论文         LangChain       LangGraph
```

### 6.2 核心洞察

1. **Agent Loop 本质**：由 LLM 驱动的状态机循环
2. **Cyclic Graph 意义**：将 AI 不确定性封装在确定性图结构中
3. **Skills 定位**：定义能力边界（砖块）
4. **LangGraph 定位**：定义编排逻辑（蓝图与水泥）

### 6.3 设计原则

- **防御性编程**：假设 LLM 会出错、工具会超时、状态会膨胀
- **代码控制流程，LLM 控制逻辑**：在"自由发挥"和"严格控制"间平衡
- **渐进式复杂度**：从简单循环开始，按需升级到状态机

### 6.4 未来趋势

1. **Skill Graph**：节点即技能，边即业务逻辑
2. **多智能体协作**：图节点代表不同 Agent 角色
3. **企业级应用**：从"聊天"到"做事"的自动化工作流
4. **标准化接口**：Skill 定义与编排引擎的解耦

---

## 附录：术语对照表

| 术语 | 英文 | 定义 |
|------|------|------|
| 智能体循环 | Agent Loop | 感知-决策-行动-观察的循环结构 |
| 执行流 | Execution Flow | 循环的代码实现 |
| 有向循环图 | Cyclic Graph | 支持循环的有向图状态机 |
| 检查点 | Checkpoint | 状态快照，用于持久化和恢复 |
| 状态归约 | State Reduction | 定义状态字段如何合并更新 |
| 条件边 | Conditional Edge | 根据条件决定下一个节点 |
| 人机协同 | Human-in-the-Loop | 执行过程中的人工干预 |
| 时间旅行 | Time Travel | 从历史检查点恢复执行 |

---

> **文档版本**：1.0  
> **更新日期**：2024年  
> **适用场景**：Agent 架构设计、LangGraph 开发、智能体工程化
