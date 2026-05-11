# team-builder

## 这是什么
`team-builder` 用于在 OpenClaw 上生成一套面向 SaaS / 产品矩阵场景的多 Agent 团队工作区与配套脚本。

它负责输出：
- 团队工作区目录
- Agent 基础文件
- shared 协作文件
- `apply-config.js`
- `create-crons.ps1` / `create-crons.sh`
- 角色与协作模板

当前默认采用一套**可复用的双开发轨参考架构**：
- `devops`：交付、部署、环境、验收、交付向 Deep Dive
- `fullstack-dev`：项目内实现、模块深挖、代码链连续开发

注意：这是一类多 agent 团队模板，不要求你的团队必须由 team-builder 创建后才成立。

## 适用范围
适用于：
- 新建 OpenClaw 团队工作区
- 升级现有 SaaS 多 Agent 团队模板
- 为已经存在的多 agent 团队抽取或对齐一套标准化模板
- 需要内置信箱协作、dashboard、产品知识目录、Deep Dive 流程的团队

不适用于：
- 直接替你修改线上环境
- 自动执行 gateway 重启、cron 创建、openclaw.json 写入（这些由你确认后手动执行生成脚本）

## 核心能力

它识别和生成的是“此类多 agent 协作团队模板”，不是“唯一正确的团队来源”。如果你已经有多 agent 团队，只要结构接近，也可以直接吸收它的工作流规则。


### 1. 一次生成团队骨架
生成共享工作区与角色目录，包括：
- `AGENTS.md`
- `SOUL.md`
- `USER.md`
- `shared/`
- `agents/`
- 配置 / cron 脚本

### 2. 双开发轨模板
内置：
- `product-lead` 负责澄清 / PRD / 验收 / 路由
- `devops` 负责交付 / QA gate / delivery-oriented Deep Dive
- `fullstack-dev` 负责实现 / 模块级 deep dive follow-up / 编码执行

### 3. Deep Dive 产品知识目录
生成适合沉淀产品知识的共享目录结构，并支持 manifest 驱动的延迟阅读模式。

### 4. 非交互 + verify
支持：
- 交互式部署
- `--config` 非交互部署
- `--verify` 校验生成结果

当前 `--verify` 会输出**结构化 JSON 检查报告**，覆盖：
- core
- roles
- fallback
- workflow
- hygiene
- cron

### 5. fallback 与上下文治理同步
已对齐当前编码执行口径：
- Claude-only ACP 默认口径
- context active cap：**60**
- lifecycle window：**100**
- done 前 verify
- 写入 / spawn 前确认 `cwd`

## 初始化
本技能**无需单独初始化**，但第一次使用前建议确认：
- OpenClaw 已正确安装
- Node.js 可用
- 你有权查看并手动执行生成出来的脚本

## 使用方法

### 1. 交互式生成
```bash
node <skill-dir>/scripts/deploy.js
```
适合首次搭团队。

### 2. 非交互生成
准备一个 JSON 配置文件，再执行：
```bash
node <skill-dir>/scripts/deploy.js --config team-builder.json
```

### 3. 验证生成结果
```bash
node <skill-dir>/scripts/deploy.js --verify --config team-builder.json
```
输出结构化 JSON 检查报告；若失败，进程以非 0 退出。

### 4. 应用生成结果
生成完成后，按顺序手动执行：
1. `node <workspace-dir>/apply-config.js`
2. `powershell <workspace-dir>/create-crons.ps1` 或 `bash <workspace-dir>/create-crons.sh`
3. `openclaw gateway restart`

## 配置说明

### 必填项
- teamName
- workspaceDir
- timezone
- morningHour
- eveningHour
- thinkingModel
- executionModel
- ceoTitle

### 可选项
- roles
- roleNames
- `--team` 前缀
- Telegram 相关输入（如果你准备接入 Telegram）

## 输出物说明

### 1. 工作区
输出团队工作区，包含：
- 角色目录
- inbox / briefings / dashboard
- products / knowledge / kanban
- 团队工作流默认规则（任务入口、done 链、最小读取顺序、角色记忆边界）

### 2. `apply-config.js`
用于把生成的 Agent 写入 `openclaw.json`。
**注意：不是自动执行，而是生成后由你手动执行。**

### 3. `create-crons.*`
用于生成 cron 任务。
**注意：不是自动执行，而是生成后由你手动执行。**

### 4. references/fallback 文件
生成的团队工作区内现在会包含：
- `references/coding-behavior-fallback.md`

供 `fullstack-dev` 在 `coding-lead` 未加载时使用。

## 已明确删除或纠正的旧描述
以下说法不再准确：
- “team-builder 会自动修改 openclaw.json” → **不对，它是生成 `apply-config.js`，由你手动执行**
- “team-builder 会自动创建 cron 并重启 gateway” → **不对，这些也是手动执行生成脚本后完成**
- “fullstack-dev 的正式复杂任务主路径是 IM 线程里的 ACP session 持久化” → **不对，当前正式口径是现有连续会话 + context 文件**
- “当前编码代理是多代理并行任选” → **不对，正式 ACP 编码口径仍是 Claude-only**

## 验证建议
改动本技能时，至少确认：
- `deploy.js --verify` 仍输出结构化 JSON 报告
- 生成物里仍包含 fallback 文件
- README / SKILL / templates / deploy.js 文案一致
- 双开发轨边界没有被写乱
- context 规则仍是 **60 / 100**

## 相关文件
- `SKILL.md`
- `scripts/deploy.js`
- `references/shared-templates.md`
- `references/soul-templates.md`
- `references/coding-behavior-fallback.md`

## 最近一次修改（中文）
- **2026-03-29 / 2f1799e**
- 变更摘要：
  - 将 `deploy.js --verify` 扩展为**结构化 JSON 检查报告**
  - 报告按 `core / roles / fallback / hygiene / cron` 分组
  - 每条检查项都输出文件、标签、期望文本与通过状态
  - 校验失败仍会返回非 0 退出码，便于自动化使用
