# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目说明

clawmoney-skill 是 ClawMoney 平台的 OpenClaw/ClawHub skill，供 AI agent 安装后自动注册、浏览任务、赚取奖励。

## API Base URL

**必须使用 `api.bnbot.ai`，不是 `api.clawmoney.ai`**（后者无法解析）。

所有 SKILL.md 和 scripts 中的 API 调用都走 `https://api.bnbot.ai`。

## 发布

```bash
npx clawhub publish /Users/jacklee/Projects/clawmoney-skill \
  --slug clawmoney --name clawmoney --version <ver> --changelog "<text>"
```

## 同步

本项目的 SKILL.md 需与以下文件保持一致：
1. `/Users/jacklee/Projects/clawmoney/.claude/skills/clawmoney/SKILL.md`（项目内部 skill）
2. `/Users/jacklee/Projects/clawmoney/public/skill.md`（网站 clawmoney.ai/skill.md）

三者 body 内容保持一致，仅 metadata 不同。
