# Multi-Agent Workshop

把一个复杂任务拆成标准化的多角色工作坊流程：先澄清交付物，再定角色，再讨论，再产出 `plan.md`，最后按 plan 执行。

## 安装

```bash
clawhub install multi-agent-workshop
```

或手动安装：将整个文件夹复制到你的技能目录中，例如 `~/.openclaw/skills/multi-agent-workshop/`。

## 适用场景

- 需求工作坊
- 多角色评审
- 复杂任务先讨论后执行
- 需要把讨论过程沉淀到 `workshops/<session_id>/`

## 核心能力

- **七阶段流程**：从阶段 0 任务澄清到阶段 6 执行
- **Orchestrator 门禁**：通过 `scripts/orchestrator.py` 强制阶段推进和校验
- **角色可配置**：角色不是固定班子，由任务决定；支持从招聘平台 JD 构建专业角色卡
- **产物标准化**：状态、讨论、计划、交付都落到标准目录
- **宿主环境对齐**：执行阶段可按宿主环境的规则文档、环境说明、各技能 `SKILL.md` 组合落地

## 从招聘 JD 构建角色卡

阶段 3 创建角色卡时，对于垂直/专业领域的角色（如合规法务、供应链经理、临床研究监查员），可以从招聘平台的岗位 JD 提炼立场和边界，比凭经验编写更精准。

```bash
# 搜索 JD 并生成角色卡草稿
python3 scripts/jd_to_role_card.py \
  --role "合规法务" \
  --industry "互联网" \
  --task "评审用户隐私协议改版"
```

脚本通过 Serper API 搜索 BOSS直聘/猎聘等平台的 JD，提取职责→立场、任职要求→发言要求、岗位边界→禁止项，生成带占位符的角色卡草稿。详见 `references/role-card-from-jd.md`。

## 项目结构

```text
multi-agent-workshop/
├── SKILL.md
├── claw.json
├── README.md
├── scripts/
│   ├── orchestrator.py
│   ├── jd_to_role_card.py          # JD→角色卡草稿生成
│   ├── openclaw-subagents-parallel.sh
│   └── phases/
├── references/
│   ├── role-card-skeleton.md        # 角色卡骨架模板
│   ├── role-card-from-jd.md         # JD 构建方法论
│   ├── sample-roles/                # 样例角色（ops/product/tech）
│   └── ...
├── templates/
└── data/
```

## 前置条件

- Python 3.8+
- 支持技能目录的宿主环境
- 可写的会话工作目录（默认可用 `workshops/`）
- JD 角色卡功能需要 `SERPER_API_KEY` 环境变量（可选）

## 使用方式

1. 读取 `SKILL.md`，按阶段 0 起盘
2. 用 `scripts/orchestrator.py` 初始化和推进阶段
3. 在会话工作目录下沉淀 `state.md`、`plan.md`、`deliverables/`
4. 用户确认 `plan.md` 后再进入执行阶段

## 说明

- 这是一个**本地技能包**，不依赖外部注册表即可放入 `clawhub` 目录或手动复制安装
- 标准入口文件是 `SKILL.md`
- 若宿主环境提供 `AGENTS.md`、`TOOLS.md` 或统一技能目录，阶段 6 建议与这些约定保持一致
