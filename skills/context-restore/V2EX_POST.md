[分享] 开源一个 OpenClaw Skill：context-restore - 让 AI 对话永不中断

## 🎯 简介

分享一个我开发的 OpenClaw Skill - **context-restore**，帮助用户在 AI 对话中断后快速恢复上下文。

**GitHub 地址：**
https://github.com/openclaw/skills/tree/main/context-restore

---

## 😢 场景痛点

大家在使用 AI 助手时，是否遇到过以下情况：

1. **每天开启新会话**
   - 需要重复解释项目背景
   - 忘记之前讨论到哪了
   - 浪费大量时间在"回忆"上

2. **隔天继续工作**
   - 完全忘记昨天做到哪了
   - 需要翻聊天记录
   - 上下文丢失导致重复劳动

3. **任务切换后回来**
   - 不知道之前在做什么
   - 需要重新建立上下文
   - 工作连续性被打断

---

## 💡 context-restore 解决方案

**context-restore** 专为解决这些痛点而设计！

只需说**"继续之前的工作"**，它会自动：
1. 读取压缩的上下文文件
2. 提取项目进度、待办任务、最近操作
3. 生成结构化的恢复报告
4. 几秒钟内让你恢复到之前的工作状态

---

## ✨ 核心功能

### 1. 自然语言触发
无需记住复杂命令，自然语言即可触发：
- 中文："继续之前的工作"、"恢复上下文"
- 英文："restore context"、"continue previous work"

### 2. 三种恢复级别

| 级别 | 适用场景 | 输出内容 |
|------|---------|---------|
| **极简（minimal）** | 快速确认状态 | 核心状态一句话 |
| **标准（normal）** | 日常继续工作 | 项目+任务列表 |
| **完整（detailed）** | 深度回顾 | 完整时间线+历史 |

### 3. 智能上下文管理
- 自动解析压缩的上下文文件
- 提取关键信息（项目、任务、操作）
- 生成可执行的恢复报告

### 4. 多语言支持
- 🌐 English
- 🇨🇳 中文
- 🇮🇹 Italiano

---

## 🚀 使用示例

### 基础使用
```bash
# 恢复上下文（默认标准模式）
/context-restore

# 指定恢复级别
/context-restore --level detailed
/context-restore -l minimal

# 自然语言触发
"继续之前的工作"
"restore context"
```

### 实际输出示例
```
✅ 上下文已恢复

当前活跃项目：
1. 🏛️ Hermes Plan - 数据分析助手（进度：80%）
2. 🌐 Akasha Plan - 自主新闻系统（进度：45%）

待办任务：
- [高] 编写数据管道测试用例
- [中] 设计 Akasha UI 组件
- [低] 更新 README 文档

最近操作（今天）：
- 完成数据清洗模块
- 添加 3 个新 cron 任务
- 修改配置文件
```

---

## 🔗 与其他技能的集成

context-restore 设计上可以与其他 OpenClaw 技能完美配合：

### 配合 context-safe 使用（推荐）
```markdown
context-save：会话结束时自动保存上下文
context-restore：会话开始时恢复上下文

完美工作流：
1. 用户结束会话 → context-save 自动保存
2. 用户开启新会话 → context-restore 自动/手动触发
3. 用户确认 → 继续工作
```

### 配合 memory_get 使用
```bash
/context-restore --level normal
→ 然后调用 memory_get 获取 MEMORY.md 详情
```

---

## 📦 安装方法

```bash
# 安装 skill
/skill install context-restore

# 立即体验
/context-restore

# 建议同时安装 context-save 实现全自动
/skill install context-save
```

---

## 📊 适用人群

- **开发者**：跨天继续编码工作
- **产品经理**：维护项目进度和需求讨论
- **研究者**：追踪研究进展和发现
- **内容创作者**：保持创作连贯性
- **任何重度 AI 用户**：提升 10x 工作连续性

---

## 🛠️ 技术实现

- **核心语言**：Python 3
- **数据格式**：JSON（压缩上下文文件）
- **输出格式**：Markdown（支持多平台适配）
- **依赖项**：无额外依赖，纯原生实现

---

## 🔮 未来规划

- [ ] 增强 AI 摘要能力
- [ ] 支持多会话并行管理
- [ ] 插件系统扩展
- [ ] 跨设备云同步

---

## 💬 互动话题

大家平时是怎么处理 AI 对话上下文丢失的问题的？有什么好的方法或工具推荐吗？

欢迎在评论区交流讨论！

---

## 🔗 相关链接

- **GitHub**：[https://github.com/openclaw/skills/tree/main/context-restore](https://github.com/openclaw/skills/tree/main/context-restore)
- **官方文档**：skill 内置完整文档
- **配合使用**：建议搭配 context-save 技能

**Tags:** #OpenClaw #AISkills #Productivity #AI #Automation
