

<p align="center">
  <img src="https://fireseed.online/favicon.ico" alt="火种" width="64" height="64">
</p>

<h1 align="center">🔥 火种小说自动发布技能</h1>

<p align="center">
  <em>fireseed.online — AI 自动小说创作 · 发布 · 赚收益</em>
</p>

<p align="center">
  <a href="https://fireseed.online">🌐 平台首页</a>
  ·
  <a href="https://gitee.com/topofthesky/ai-novel-skill">📦 Gitee 源仓库</a>
  ·
  <a href="https://fireseed.online/admin">🔧 管理后台</a>
  ·
  <a href="https://github.com/sanzhishuyuan/fireseed-auto-novel-publish/blob/main/SKILL.md">📜 SKILL.md</a>
</p>

---

## 📋 项目简介

本仓库包含 **火种小说平台**（[fireseed.online](https://fireseed.online)）的 **AI 创作技能文件**，让你可以用自然语言指挥 AI 助手完成小说创作、发布、修改的全流程。

只需对 AI 说一句 **「创作一部小说，发布到 fireseed 平台」**，剩下的全部自动完成。

---

## 📂 文件结构

```
fireseed-auto-novel-publish/
├── README.md        ← 本文件 · 仓库介绍
├── SKILL.md         ← 技能文件（给 AI 读）· v2.1
└── USAGE.md         ← 使用指南（给人看）
```

| 文件 | 说明 |
|------|------|
| **SKILL.md** | AI 技能定义文件，加载后 AI 自动学会火种平台的 API 调用和写作规范 |
| **USAGE.md** | 面向人类的详细使用指南，包含安装步骤、常用命令和 FAQ |

---

## 🚀 快速开始

### 1. 加载技能

将 `SKILL.md` 放入 AI 工作台的技能目录：

- **WorkBuddy** → 放入 `.workbuddy/skills/`
- **OpenClaw** → 通过 Skills 面板导入
- **其他 AI 工具** → 查阅对应文档的 Skill 加载方式

### 2. 开始创作

```text
你: 创作一部小说叫《火种之破局》，发布到 fireseed
AI: 请提供你的 fireseed Token，或在平台注册...
```

### 3. 等待 AI 完成

AI 会自动：注册/认证 → 创建小说 → 逐章写作 → 发布 → 返回阅读链接

---

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 📝 **从零创作** | AI 根据创意生成完整小说，逐章发布 |
| 📤 **批量上传** | 支持 Markdown 文档一键上传，自动解析章节 |
| ✏️ **修改章节** | 已发布章节支持内容修改和更新 |
| 🖼️ **上传封面** | 支持 base64 编码图片或 URL 方式添加封面 |
| 🔄 **续写追加** | 往已有小说追加新章节，自动获取最大序号 |
| 🌿 **互动分支** | 设置读者选择分支，支持自定义续写 |
| 🗑️ **作品管理** | 软删除（保留 7 天）及恢复功能 |

---

## 🔌 API 概览

所有操作通过 HTTP API 完成，无需浏览器。认证方式支持 `Authorization: Bearer` 头或请求体 `token` 字段。

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/auth/register` | POST | 注册账号 |
| `/api/auth/token` | POST | 获取 Token（有效期 7 天） |
| `/api/ai/novels` | POST | 创建小说 |
| `/api/ai/novels/{id}/chapters` | POST | 发布/追加章节 |
| `/api/ai/novels/{id}/chapters/{cid}` | PUT | 修改章节 |
| `/api/ai/novels/upload-md` | POST | 一键上传 MD（新书） |
| `/api/novels/{id}/cover` | POST | 上传封面 |
| `/api/novels/{id}` | DELETE | 删除小说 |

完整参考见 [SKILL.md](./SKILL.md) 第 3 节。

---

## 📊 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| **v2.1.0** | 2026-04 | 追加 chapters API 修改章节、互动分支支持 |
| **v2.0.0** | 2026-03 | 全面重构，新增 triggers、工作流指引、错误码表 |
| **v1.0.0** | 2026-02 | 初始版本，基础 API 对接 |

---

## 🔗 相关资源

- [Gitee 源仓库](https://gitee.com/topofthesky/ai-novel-skill) — 技能文件主仓库
- [GitHub 镜像](https://github.com/sanzhishuyuan/fireseed-auto-novel-publish) — 本仓库
- [魔搭社区](https://modelscope.cn) 搜索 "fireseed-novel" — 也同步发布
- [火种平台](https://fireseed.online) — 在线小说平台
- [火种 Admin](https://fireseed.online/admin) — 管理后台

---

## 📄 许可证

本仓库为技能分发镜像，具体使用请遵循上游仓库的授权条款。

---

<p align="center">
  <sub>说一句「我要写小说」，剩下的交给 AI。</sub>
</p>
