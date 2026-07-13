# create-agent

> 基于 [OpenClaw](https://github.com/openclaw/openclaw) 的 AgentSkill

**让每一个 Agent，从第一天起就值得信赖。**

---

## 为什么需要它

在 OpenClaw 里，注册一个 Agent 只需要几行配置。
但注册一个**真正好用的 Agent**，是另一回事。

好用的 Agent 不只是"能回答问题"——
它知道你不喜欢废话，习惯把方案写成结论优先；
它记得你负责的客户类型，不用每次都解释背景；
它有明确的边界，不会越界做不该做的事。

**这些不是配置出来的，是设计出来的。**

没有标准流程时，创建 Agent 容易踩这些坑：

- workspace 文件繁多，漏写哪个都可能悄悄影响行为
- SOUL.md 写成"我是一个专业高效的 AI 助手"——没有性格，就等于没有灵魂
- 人伴型和功能型 Agent 结构完全不同，混用就是在起点埋雷
- 直接修改 openclaw.json 出错，一堆 Agent 跟着挂

你花两天创建了一个 Agent，用了一周发现它没有"灵魂"——重来。

---

## 它是什么

**一套从零到一的 Agent 创建标准流程。**

把"创建一个好 Agent"这件复杂的事，拆成四个清晰的 Phase。
能自动化的自动化，必须人工判断的有明确引导。

走完四个 Phase，你得到的不是一个空壳：

- ✅ workspace 结构正确，所有必须文件齐全且有实质内容
- ✅ SOUL.md 有具体性格，不是套了名字的通用模板
- ✅ 系统注册安全完成，配置有备份，validate 失败自动回滚
- ✅ 人伴型 Agent 携带 BOOTSTRAP 初始化协议——
  准备好通过第一次真实对话，建立只属于这个人的专属关系

---

## 核心设计理念

> **skill 负责骨架，BOOTSTRAP.md 负责灵魂。**

创建时产出的是可运行的结构。
真正的性格，来自 Agent 与用户第一次对话时的动态初始化——
不是填表，是一段由浅入深的自然对话，
把用户的习惯、厌恶、工作方式，转化成叙事、规则、记忆。

**workspace 不靠创建时决定好坏，靠使用过程中的持续积累决定。**
从第一次对话起，它就在变成更懂你的那个版本。

---

## 功能

自动化完成新 Agent 的全套创建流程：

- **Phase 0** — 安装后配置（一次性，写入组织背景到 `config/org-context.md`）
- **Phase 1** — 信息收集（Agent 类型【第一确认】/ agentId / 工具权限 / 父 Agent）
- **Phase 2** — Workspace 构造（SOUL.md / AGENTS.md / BOOTSTRAP.md 等全套文件，按类型走不同路径）
- **Phase 3** — 系统注册（安全修改 openclaw.json，备份 + 双向绑定 + validate + 回滚；支持 --dry-run）
- **Phase 4** — 重启验证（workspace 文件完整性验证 + 工具可用性验证）

### 两类 Agent

| 维度 | 人伴型（员工型） | 功能型（任务/领域型） |
|---|---|---|
| **面向谁** | 有真人用户直接对话 | 面向任务，可被 Agent 调度或人直接用 |
| **SOUL.md** | 写骨架，BOOTSTRAP 阶段填充 | 直接写完整版，体现专业判断倾向 |
| **BOOTSTRAP.md** | ✅ 需要 | ❌ 不需要 |
| **USER.md** | ✅ 需要 | ❌ 不需要 |
| **脚本参数** | `--type human` | `--type functional` |

- skill 产出可运行的 Agent（系统层 + workspace 骨架）
- BOOTSTRAP.md 通过动态对话（支持断点续接）完成 workspace 内容层定制
- workspace 从真实使用中持续生长（触发式写入 + heartbeat 精炼）

---

## 文件结构

```
create-agent/
├── SKILL.md                          # 触发条件 + 四 Phase 执行流程
├── config/
│   └── org-context.md               # 组织背景预埋（Phase 0 生成，不推送到 repo）
├── references/
│   ├── file-formats.md               # 每个 workspace 文件"写好"的标准
│   ├── soul-writing-guide.md         # SOUL.md 素材→叙事的组织方法
│   ├── evolve-rules.md               # workspace 持续生长规则
│   └── bootstrap-protocol.md        # BOOTSTRAP.md 动态对话协议蓝本（含断点续接）
└── scripts/
    ├── create_workspace.sh           # 创建目录结构（支持 --type human|functional）
    ├── register_agent.py             # 安全注册（备份+双向绑定+validate+回滚+dry-run）
    └── verify_workspace.sh           # workspace 完整性验证（Phase 4 使用）
```

---

## 安装

需要先安装 [OpenClaw](https://github.com/openclaw/openclaw)。

```bash
clawhub install openclaw-create-agent
```

或手动克隆到 `~/.openclaw/skills/create-agent/`。

## 触发

在 OpenClaw 对话中说：
- "创建 agent"
- "新建 agent"
- "新员工配对后创建 agent"
- "新增专业 agent"

## 依赖

- OpenClaw >= 2026.3.0
- `openclaw` CLI（用于 config validate）
- `systemctl --user`（用于 Gateway 重启）
