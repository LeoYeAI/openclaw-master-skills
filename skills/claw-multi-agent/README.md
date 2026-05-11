# claw-multi-agent 🐝

**OpenClaw 多智能体编排 Skill**

单个 AI 视角单一、上下文越跑越重。claw-multi-agent 让你组建一支 AI 小队——不同角色、不同模型、各司其职，协作完成复杂任务。

- 🎯 **多样性**：研究员搜索、分析师推理、写作者输出，分工比单打独斗更全面
- 💰 **省 token**：每个子 Agent 独立会话，只返回摘要，主线程上下文不膨胀
- ⚡ **省时间**：并行执行，实测节省 50-78%

---

## 安装

```bash
npx --yes skills add https://github.com/zcyynl/claw-multi-agent
```

装完即用，自动使用你 OpenClaw 里已有的模型，**零配置**。

---

## 快速上手

安装后直接说：

- "多智能体做 xxx"
- "帮我并行调研 LangChain、CrewAI、AutoGen 框架"
- "深度调研一下 xxx，整理成报告"
- "全面分析一下 xxx 的优缺点"

不需要指定模式，skill 自动判断该用哪种。

---

## 三种模式

### 🎯 指挥官模式

多个子 Agent **同时联网搜索**，主 Agent 整合成报告。

- 子 Agent 有完整工具：联网搜索、读写文件、执行代码
- 同一轮批量派发 = 真正并行
- 适合：**需要实时信息的调研、分析任务**

```
sessions_spawn(搜索LangChain) ──┐
sessions_spawn(搜索CrewAI)   ──┤→ 同时跑
sessions_spawn(搜索AutoGen)  ──┘
↓ 全部返回，主 Agent 整合写报告
```

---

### 🔄 流水线模式

多个 Agent **极速并行**，调用模型原生能力，省 token。

- 无工具调用开销，速度最快
- 适合：**多模型对比、多角度分析、不需联网的写作任务**

```bash
cd ~/.openclaw/skills/claw-multi-agent

# 3 个角色同时分析同一问题
python run.py --mode parallel \
  --agents "default:技术专家:分析 LangChain 的优缺点" \
           "default:产品经理:分析 LangChain 的优缺点" \
           "default:初学者:分析 LangChain 的易用性"

# 自动路由：让路由器拆任务、分配模型
python run.py --auto-route --task "对比分析三个框架"

# 预览模式：只看计划，不实际运行
python run.py --dry-run --agents "default:研究员:分析X" "default:写作者:写报告"
```

---

### 🔀 混合模式

先联网搜索，再并行生成多版草稿，你来挑最好的。

- Phase 1（指挥官）：并行联网调研
- Phase 2（流水线）：并行生成 N 版草稿
- 适合：**"帮我搜完资料，给我写几个版本的报告"**

```bash
python run.py --mode hybrid --task "调研主流 AI 框架，给我3个不同风格的对比报告" --num-drafts 3
```

---

## OpenClaw 原生 vs claw-multi-agent

OpenClaw 原生只有 `sessions_spawn`，一次派一个 Agent，等完成再派下一个。

claw-multi-agent 加了什么：

| 能力 | 原生 | claw-multi-agent |
|------|------|-----------------|
| 派子 Agent | ✅ 串行 | ✅ **真并行** |
| 联网搜索 | ✅ | ✅ |
| 结果自动聚合 | ❌ | ✅ |
| 自动路由 | ❌ | ✅ |
| 无工具轻量 Agent | ❌ | ✅ 流水线模式 |
| 多版草稿对比 | ❌ | ✅ 混合模式 |

---

## 自动路由

不用说"用哪个模式"，skill 识别两个信号自动判断：

| 信号 | 触发词示例 | 选择模式 |
|------|----------|---------|
| 需要联网 | 搜索、调研、最新、查找资料 | 指挥官 |
| 需要多版本 | 几个版本、不同角度、让我挑 | 流水线 |
| 两者都有 | 搜完给我几个版本 | 混合 |
| 都没有 | 分析、翻译、写作 | 流水线 |

---

## 实测数据

| 场景 | 模式 | 串行 | 并行 | 节省 |
|------|------|------|------|------|
| 2 个主题同时分析 | 流水线 | ~13s | ~7s | **46%** ⚡ |
| 3 个主题同时调研 | 指挥官 | ~75s | ~25s | **67%** ⚡ |
| 4 Agent 深度调研 | 指挥官 | ~322s | ~96s | **70%** ⚡ |
| 5 个 Agent 对比分析 | 流水线 | ~125s | ~28s | **78%** ⚡ |

---


## 详细文档

见 [SKILL.md](./SKILL.md)，包含：
- 完整的指挥官/流水线/混合模式用法
- 给子 Agent 注入上下文（contextSharing）
- 避坑指南（串行依赖、token 上限等）
- 模型选择指南

---

> 💡 让每个 Agent 只做一件事，主 Agent 负责整合。分工协作，比单打独斗快得多。
