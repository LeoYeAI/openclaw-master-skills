<p align="center">
  <strong>🎨 shadcn/ui</strong>
</p>

<h1 align="center">shadcn-ui-skills</h1>

<p align="center">
  <strong>让 AI 设计前端，提升 8 个档次的 UI 视觉</strong>
</p>

<p align="center">
  <a href="#-简介"><img src="https://img.shields.io/badge/文档-完整-blue?style=flat-square" alt="文档" /></a>
  <a href="#-快速开始"><img src="https://img.shields.io/badge/快速开始-5分钟-green?style=flat-square" alt="快速开始" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="License" /></a>
</p>

<p align="center">
  <a href="#-简介">简介</a> •
  <a href="#-八个档次的提升">八个档次</a> •
  <a href="#-安装">安装</a> •
  <a href="#-快速开始">快速开始</a> •
  <a href="#-项目结构">项目结构</a> •
  <a href="#-发布到-github">发布</a> •
  <a href="#-许可证">许可证</a>
</p>

---

## ✨ 简介

**shadcn-ui-skills** 是一套面向 AI 助手的专业技能包，让 AI 能够像资深前端工程师一样，正确、高效地使用 [shadcn/ui](https://ui.shadcn.com) 构建生产级界面。

当 AI 缺乏 shadcn/ui 的规范知识时，生成的代码往往存在：

- 错误的布局方式（`space-y-*` 而非 `gap-*`）
- 随意的颜色使用（`bg-blue-500` 而非语义化 token）
- 不完整的组件组合（缺少 `AvatarFallback`、`DialogTitle` 等）
- 表单结构混乱（`div` + `Label` 而非 `FieldGroup` + `Field`）
- 图标与按钮搭配不当（缺少 `data-icon`、手动设置尺寸）

本技能包通过 **SKILL.md**、**规则文件**、**CLI 文档**、**MCP 集成** 等，为 AI 提供完整的上下文与约束，使其产出 **符合 shadcn/ui 最佳实践** 的代码，从而让 AI 设计的前端在视觉与质量上实现 **质的飞跃**。

---

## 📈 八个档次的提升

| 档次 | 无技能时 | 有技能后 |
|:---:|----------|----------|
| **1** | 随意使用 `space-x` / `space-y` | 统一使用 `flex` + `gap-*`，布局更稳定 |
| **2** | 硬编码颜色 `text-red-600` | 语义化 token `text-destructive`，支持主题 |
| **3** | 手动 `dark:` 覆盖 | 语义化变量自动适配深色模式 |
| **4** | 表单用 `div` 堆叠 | `FieldGroup` + `Field` + `data-invalid` 规范表单 |
| **5** | 自定义空状态、提示框 | 使用 `Empty`、`Alert`、`Badge` 等标准组件 |
| **6** | 图标尺寸混乱、按钮结构随意 | `data-icon`、`AvatarFallback`、完整 Card 结构 |
| **7** | 猜测组件 API、重复造轮子 | 先 `search` 再 `add`，优先复用现有组件 |
| **8** | 风格零散、难以维护 | 统一规范 + 主题变量，可扩展的设计系统 |

---

## 🚀 安装

### 作为 Cursor / Claude Code 技能

将本仓库克隆到技能目录：

```bash
# Cursor
git clone https://github.com/lumacoder/shadcn-ui-skills.git ~/.cursor/skills/shadcn-ui-skills

# 或在项目内引用
git clone https://github.com/lumacoder/shadcn-ui-skills.git .cursor/skills/shadcn-ui-skills
```

确保 AI 助手能访问 `SKILL.md` 及 `rules/`、`cli.md`、`mcp.md` 等文档。

### 作为 MCP 服务器（可选）

若需 AI 直接搜索、浏览、安装 shadcn 组件，可启用 shadcn CLI 内置的 MCP 服务：

```bash
shadcn mcp        # 启动 MCP 服务
shadcn mcp init   # 生成编辑器配置
```

详见 [mcp.md](./mcp.md)。

---

## ⚡ 快速开始

### 1. 初始化项目

```bash
npx shadcn@latest init --preset base-nova
# 或
npx shadcn@latest init --preset radix-nova --template next
```

### 2. 添加组件

```bash
npx shadcn@latest add button card dialog
npx shadcn@latest add @magicui/shimmer-button
```

### 3. 搜索与预览

```bash
npx shadcn@latest search @shadcn -q "sidebar"
npx shadcn@latest add button --dry-run --diff
```

### 4. 获取组件文档

```bash
npx shadcn@latest docs button dialog select
```

---

## 📁 项目结构

```
shadcn-ui-skills/
├── SKILL.md          # 核心技能文档
├── cli.md            # CLI 命令参考
├── mcp.md            # MCP 服务说明
├── customization.md  # 主题与自定义
├── rules/            # 规则与示例
│   ├── styling.md    # 样式与 Tailwind
│   ├── forms.md     # 表单与输入
│   ├── composition.md # 组件组合
│   ├── icons.md     # 图标
│   └── base-vs-radix.md
├── agents/           # 代理配置
├── evals/            # 评估用例
└── assets/           # 资源
```

---

## 📚 核心文档

| 文档 | 说明 |
|------|------|
| [SKILL.md](./SKILL.md) | 技能主文档：原则、规则、组件选择、工作流 |
| [cli.md](./cli.md) | 命令、模板、预设、标志 |
| [mcp.md](./mcp.md) | MCP 工具与配置 |
| [customization.md](./customization.md) | 主题、CSS 变量、组件定制 |
| [rules/styling.md](./rules/styling.md) | 语义化颜色、布局、间距 |
| [rules/forms.md](./rules/forms.md) | FieldGroup、Field、InputGroup、验证 |
| [rules/composition.md](./rules/composition.md) | Group、Card、Dialog、Empty 等 |

---


## 🎯 适用场景

- 使用 **shadcn/ui** 构建 React / Next.js / Vite 项目
- 使用 **components.json** 或 `npx shadcn@latest init --preset`
- 需要 AI 协助添加、修改、调试 shadcn 组件
- 需要 AI 遵循设计系统规范，避免「AI 风格」的随意代码

---

## 📄 许可证

本项目采用 [MIT 许可证](./LICENSE)。详见 [LICENSE](./LICENSE) 文件。

---

<p align="center">
  Powered by <a href="https://ui.shadcn.com">shadcn/ui</a>
</p>
