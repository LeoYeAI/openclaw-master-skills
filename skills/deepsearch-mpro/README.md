# Deep Research Mpro

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Research](https://img.shields.io/badge/Focus-Deep%20Research-blue.svg)
![Output](https://img.shields.io/badge/Output-Markdown%20%2B%20HTML-purple.svg)

专业研究报告生成技能，面向企业/产品/行业/市场/AI 厂商等场景，自动产出咨询风格报告（Markdown + HTML）。

**English**: A professional deep-research skill template for market/company/product/AI-vendor analysis, generating consulting-style reports in Markdown and HTML.

## 项目简介

`deepsearch-mpro` 是一个用于深度研究与报告生成的技能模板，核心目标是：

- 将“研究需求”转为“结构化分析框架”
- 基于多源检索收集可追溯数据
- 输出可直接汇报的专业报告

适用场景包括：

- 企业竞争分析（如金蝶、用友、SAP 等）
- 产品竞争分析（定位、功能、用户、竞品）
- 行业与市场分析（趋势、规模、格局）
- AI 大模型与 AI 工具分析

## 核心能力

- **多源搜索整合**：17 个搜索引擎（8 个国内 + 9 个国际），无需 API Key
- **三阶段工作流**：主题确认 → 分析框架生成 → 报告生成
- **咨询模型内置**：PESTEL、SWOT、波特五力、商业模式画布、竞品矩阵等
- **双格式输出**：Markdown 文档 + 深蓝风格 HTML 报告
- **数据真实性约束**：强调来源可追溯与多源交叉验证

## 项目结构

```text
deepsearch-mpro/
├── README.md                     # 项目说明（本文件）
├── SKILL.md                      # 技能主定义与完整流程
├── assets/                       # 报告与 HTML 模板资产
│   ├── report-template.md
│   ├── html-template.html
│   └── templates/
├── references/                   # 方法论、领域框架、模型库、技术指南
│   ├── domains/
│   ├── methodology/
│   ├── models/
│   ├── technical/
│   └── workflow/
└── scripts/                      # 辅助脚本（依赖检查/数据收集）
```

## 快速开始

### 1) 克隆/下载项目

将本仓库放到本地后，确保 `SKILL.md`、`assets/`、`references/` 目录完整。

### 2) 安装脚本依赖（可选）

如果你要使用 `scripts/data_collector.py`：

```bash
pip install requests beautifulsoup4 lxml
```

### 3) 直接使用技能

向 AI 输入研究主题，例如：

- `做下用友 BIP 产品的研究`
- `分析金蝶企业竞争情况`
- `生成 AI 大模型厂商分析报告`

系统会按三阶段流程执行，并输出 Markdown/HTML 报告。

## 与 GitHub 配合的说明

### 仓库简介（About）建议

可直接复制以下文案到 GitHub 仓库的 About：

> 专业深度研究与报告生成技能：支持企业/产品/行业/市场/AI 厂商分析，整合 17 个搜索源，输出咨询级 Markdown + HTML 报告。

### 推荐仓库标签（Topics）

`deep-research` `market-analysis` `competitive-analysis` `report-generation` `ai-research` `consulting`

### 推荐仓库描述（中英双语）

可用于 GitHub 仓库 `Description` 字段：

> 专业深度研究与报告生成技能，支持企业/产品/行业/市场/AI 厂商分析，输出咨询级 Markdown + HTML 报告。  
> Professional deep-research and report-generation skill for company/product/industry/market/AI-vendor analysis, with consulting-grade Markdown + HTML outputs.

## 上传到 GitHub（首次）

在项目根目录执行：

```bash
git init
git add .
git commit -m "init: add deepsearch-mpro skill project"
git branch -M main
git remote add origin <你的仓库地址>
git push -u origin main
```

如果你已在 GitHub 创建空仓库，`<你的仓库地址>` 形如：

- HTTPS: `https://github.com/<用户名>/<仓库名>.git`
- SSH: `git@github.com:<用户名>/<仓库名>.git`

## 注意事项

- 当前仓库以技能与模板为主，脚本能力属于辅助工具
- 报告中的关键数据应标注来源并尽量做交叉验证
- 已提供 `MIT License`，如需企业内治理可进一步补充发布规范

## English Quick Start

### What this project does

- Converts a research topic into a structured analysis framework
- Collects multi-source evidence with traceable references
- Produces presentation-ready Markdown and HTML reports

### How to use

1. Prepare a topic (e.g. "Analyze Kingdee competitive landscape")
2. Run the 3-stage workflow in the skill:
   - Topic confirmation
   - Framework generation
   - Report generation
3. Export report artifacts in Markdown and HTML

### First-time GitHub push

```bash
git init
git add .
git commit -m "init: add deepsearch-mpro skill project"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```
