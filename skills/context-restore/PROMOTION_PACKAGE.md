# context-restore Skill 推广内容包

## 简短描述（50字内）
智能对话上下文恢复技能，支持中英文，自动保存/恢复对话状态，让 AI 对话永不中断。

## 中等描述（150字内）
context-restore 是一款创新的 OpenClaw 技能，让 AI 助手能够自动保存和恢复对话上下文。无论您离开多久回来，都能无缝继续之前的工作。支持三种恢复级别，完美集成 memory_get、cron 等技能。

## 完整介绍（500字内）
context-restore 是 OpenClaw 生态中的智能上下文管理技能，专为解决 AI 对话中断后上下文丢失的痛点而设计。

当您开启新会话或隔天回来工作时，只需说"继续之前的工作"，context-restore 会自动读取压缩的上下文文件，提取项目进度、待办任务、最近操作等关键信息，帮助您在几秒钟内恢复到之前的工作状态。

支持三种恢复级别：极简模式（核心状态一句话）、标准模式（项目+任务列表）、完整模式（完整时间线和历史记录）。完美集成 context-save、memory_get 等技能，配合使用可实现全自动的上下文保存与恢复流程。

## 功能亮点
- 🔄 **智能上下文保存和恢复** - 自然语言触发，无感恢复
- 🌐 **三语言支持** - 中文、英文、意大利语
- 📊 **三级恢复模式** - minimal/normal/detailed 自由选择
- 🤝 **与 OpenClaw 技能生态完美集成** - 支持 context-save、memory_get 等
- 🚀 **提升 10x 工作连续性** - 秒级恢复，无需重复解释背景

## 标签
#OpenClaw #AISkills #Productivity #ChatGPT #Automation #AIAssistant

## Medium 文章大纲

### 标题
Introducing context-restore: The Smart Way to Never Lose Your AI Conversation Context

### 大纲
1. **痛点分析**：AI 对话上下文的丢失问题
   - 每天开启新会话的困扰
   - 跨天继续工作的痛点
   - 任务切换后的上下文丢失

2. **解决方案**：context-restore 介绍
   - 什么是 context-restore
   - 核心设计理念
   - 与传统方法的对比

3. **核心功能详解**
   - 三种恢复级别介绍
   - 自然语言触发机制
   - 多语言支持

4. **使用示例演示**
   - 快速开始指南
   - 实际使用场景演示
   - 代码示例

5. **与其他技能的集成**
   - context-save 配合使用
   - memory_get 集成
   - cron 定时保存

6. **未来展望**
   - 路线图规划
   - 社区贡献指南

## V2EX 帖子

### 标题
[分享] 开源一个 OpenClaw Skill：context-restore - 让 AI 对话永不中断

### 正文
分享一个我开发的 OpenClaw Skill - context-restore，帮助用户在 AI 对话中断后快速恢复上下文。

**场景痛点：**
- 每天开启新会话，需要重复解释背景
- 隔天回来忘记昨天做到哪了
- 任务切换后丢失上下文

**context-restore 解决方案：**
只需说"继续之前的工作"，它会自动读取压缩的上下文文件，提取项目进度、待办任务、最近操作等信息，让你在几秒钟内恢复到之前的工作状态。

**核心功能：**
- 🔄 自动恢复对话上下文
- 📊 三种恢复级别（极简/标准/完整）
- 🌐 支持中文、英文、意大利语
- 🤝 与 OpenClaw 技能生态集成

**使用示例：**
```bash
# 基础使用 - 恢复上下文
/context-restore

# 指定恢复级别
/context-restore --level detailed
```

**项目地址：** https://github.com/openclaw/skills/tree/main/context-restore

**相关 Skill：** 建议配合 context-save 使用，实现全自动的上下文保存与恢复。

## Twitter/X 推广文案

**文案1（简短）：**
🔄 Introducing context-restore - The smart way to never lose your AI conversation context! Seamlessly restore your work state across sessions. #OpenClaw #AISkills #Productivity

**文案2（功能强调）：**
Never lose your AI conversation context again! 🧠 context-restore supports 3 restoration levels, multilingual support, and integrates with @OpenClaw skills ecosystem. Try it now!

**文案3（痛点共鸣）：**
💡 "Where did we leave off?" - with context-restore, this question is history. Auto-save and restore your AI conversation context effortlessly. #AI #Automation

## Reddit 推广文案

**r/OpenAI：**
Just released context-restore - an OpenClaw skill that automatically saves and restores your AI conversation context. Perfect for continuing work across sessions without repeating background info. Supports 3 restoration levels and multilingual triggers.

**r/AItool：**
Found this super useful OpenClaw skill - context-restore. It helps you seamlessly continue AI conversations by restoring previous context. Great for:
- Daily work continuation
- Task switching recovery
- Cross-session context preservation

## Discord 推广文案

**消息内容：**
🎉 New skill release: **context-restore**!

Never lose your AI conversation context again! 

✨ Features:
- Auto-restore conversation context with natural language
- 3 restoration levels: minimal/normal/detailed
- Multilingual support (EN/ZH/IT)
- Perfect integration with OpenClaw skills

🚀 Try it: `/context-restore` or say "continue previous work"

## 技术博客文章

### 标题
如何在 OpenClaw 中实现对话上下文的智能恢复

### 摘要
本文介绍了 context-restore 技能的设计理念、核心功能和实现细节，帮助开发者理解如何利用上下文管理提升 AI 助手的工作连续性。

### 正文大纲
1. 引言：AI 对话上下文管理的挑战
2. context-restore 核心设计
3. 三种恢复级别的实现原理
4. 与其他技能的集成方式
5. 最佳实践和使用建议
6. 总结与展望

## 发布清单

- [ ] GitHub README 更新
- [ ] Medium 文章发布
- [ ] V2EX 帖子发布
- [ ] Twitter/X 推文发布
- [ ] Reddit 帖子发布
- [ ] Discord 社区公告
- [ ] 技术博客发布

## 验证指标

- 发布平台列表
- 获得的关注/点赞数
- 网站流量数据
- GitHub Star 增长
- 技能安装量

## 后续推广计划

1. **第1周**：监控各平台数据，收集用户反馈
2. **第2周**：根据反馈优化推广文案
3. **第3周**：发布使用教程视频
4. **第4周**：收集成功案例，准备下一轮推广
