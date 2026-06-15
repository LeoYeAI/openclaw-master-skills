# 🚀 Team Dispatch

**多 Agent 工作流编排系统**

> 一句需求 → 自动分析 → 智能拆解 → DAG 派发 → 故障重试 → 自动交付。

[![Version](https://img.shields.io/badge/version-1.0.5-blue.svg)](https://github.com/vvusu/team-dispatch/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 🌍 语言 / Language

**默认：中文** | Default: Chinese

在 `~/.openclaw/configs/team-dispatch.json` 中切换：

```json
{
  "language": "zh"
}
```

---

## 📖 概述

Team Dispatch 是一个轻量级多 Agent 协作调度系统，让主 Agent 能够：

1. **自动分析** 需求复杂度（S/M/L/XL 四级）
2. **智能拆解** 为多个子任务并声明依赖关系
3. **构建 DAG** 自动生成项目追踪文件
4. **并行派发** 通过 `sessions_spawn` 调度团队 Agent
5. **自动推进** Agent 完成后自动解锁并派发下游任务
6. **故障处理** 超时重试、模型修复、降级策略
7. **结果注入** 下游 Agent 自动获得上游输出
8. **自动通知** 项目完成时自动发送最终交付清单 + 预览方式

---

## 🎯 特性

- ✅ 自动需求分析（S/M/L/XL 四级复杂度）
- ✅ 智能任务拆解（5 种模板：开发/研究/全栈/分析/内容）
- ✅ DAG 依赖图（线性/扇出/扇入/菱形）
- ✅ 并行派发（并发上限可配置：默认 5，建议 10）
- ✅ 结果自动注入下游 Agent
- ✅ 故障处理（超时重试 + 模型修复 + 降级策略）
- ✅ 任务状态持久化（JSON 文件，compact 不丢失）
- ✅ 用户确认点（XL 级项目关键节点暂停审核）
- ✅ 双语支持（中英文）

---

## 👥 团队成员

| agentId | 职能 | 工具集 | 默认超时 |
|---------|------|--------|---------|
| `coder` | 编码开发 | coding | 180s |
| `product` | 产品规划 | full | 60s |
| `tester` | 测试验证 | coding | 90s |
| `research` | 调研搜索 | full | 90s |
| `trader` | 投资分析 | full | 60s |
| `writer` | 内容写作 | full | 60s |

---

## 📦 安装

```bash
# 1. 克隆到技能目录
cd ~/skills
git clone git@github-vvusu:vvusu/team-dispatch.git

# 2. 创建软连接
ln -s ~/skills/team-dispatch/ ~/.openclaw/skills/team-dispatch

# 3. 初始化任务目录
mkdir -p ~/.openclaw/workspace/tasks/{active,done,templates}

# 4. 复制模板
cp ~/skills/team-dispatch/assets/templates/project.json \
   ~/.openclaw/workspace/tasks/templates/

# 5. 验证
ls -la ~/.openclaw/skills/team-dispatch
```

---

## ⚙️ 配置

### 语言设置

编辑 `~/.openclaw/configs/team-dispatch.json`：

```json
{
  "version": "1.0.5",
  "language": "zh",
  "notifyPolicy": "failures-only",
  "team": {
    "agents": {
      "coder": {
        "displayName": "闪电",
        "username": "",
        "notify": {
          "telegram": {
            "enabled": false,
            "chatId": ""
          }
        }
      }
    }
  }
}
```

### Agent 配置

在 `openclaw.json` 中配置 6 个 Agent，或运行：

```bash
bash ~/skills/team-dispatch/scripts/setup.sh
```

---

## 🚀 使用

直接向主 Agent 发送需求即可：

```
"帮我做一个博客系统"
"调研 AI Agent 市场并写分析报告"
"帮我分析并修复这段代码的问题"
```

Agent 会自动分析、拆解、派发、收集结果，并发送最终交付通知。

### 示例

#### 开发任务
```
"创建一个暗色主题 + 毛玻璃效果的登录页面"
```
→ product(PRD) → coder(编码) → tester(测试) → writer(文档)

#### 研究任务
```
"调研 AI Agent 市场并写分析报告"
```
→ research(调研) → product(分析框架) → writer(成文)

#### 全栈任务
```
"构建一个完整的 SaaS 落地页，带数据分析功能"
```
→ research → product → coder → tester → writer

---

## 📊 任务复杂度分级

| 级别 | 判断标准 | 处理方式 |
|------|---------|---------|
| **S** | 单 Agent 可完成 | 直接 spawn，不建文件 |
| **M** | 2-3 个 Agent，线性依赖 | 自动建 DAG + 追踪 |
| **L** | 4+ Agent，有并行分支 | 自动建 DAG + 追踪 + 进度汇报 |
| **XL** | 跨多领域，需多轮迭代 | DAG + 分阶段交付 + 用户确认点 |

---

## 🔄 拆解模板

### 开发类
```
product(PRD) → coder(编码) → tester(测试)
                            → writer(文档)
```

### 研究类
```
research(调研) → product(分析) → writer(报告)
```

### 全栈类
```
research → product → coder → tester → writer
```

### 分析类
```
research(数据收集) → trader(分析) → writer(报告)
                  → product(策略建议)
```

### 内容类
```
research(素材收集) → writer(初稿) → product(审核优化)
```

---

## ⚡ 故障处理

### 故障类型

| 类型 | 触发条件 | 检测方式 |
|------|---------|---------|
| 超时 | 超过 timeoutSeconds | runTimeoutSeconds 触发 |
| 失败 | Agent 返回 failed | completion event status |
| 拒绝 | 并发上限 5/5 | spawn 返回 forbidden |
| 模型错误 | 模型不可用 (404 等) | completion event error |

### 自动恢复策略

| 策略 | onFailure 值 | 行为 |
|------|-------------|------|
| 阻塞 | `"block"` | 中止项目，通知用户（默认） |
| 跳过 | `"skip"` | 标记 skipped，下游继续 |
| 降级 | `"fallback"` | 换备选 Agent 重试 |
| 人工 | `"manual"` | 暂停，等用户提供结果 |

---

## 📁 项目文件结构

```
tasks/
├── active/          # 进行中项目
│   └── <project>.json
├── done/            # 已完成项目
│   └── <project>.json
└── templates/
    └── project.json
```

---

## 🔧 脚本

| 脚本 | 说明 |
|------|------|
| `scripts/setup.sh` | 初始化 Agent 配置 |
| `scripts/setup-config.sh` | 创建用户配置文件 |
| `scripts/doctor.sh` | 检查系统健康状态 |
| `scripts/watch.sh` | 低频扫描器，检测卡死任务 |

### 扫描器（推荐）

```bash
# 每 60 秒扫描一次（带抖动），检测超时任务
bash ~/skills/team-dispatch/scripts/watch.sh

# 自定义频率
INTERVAL=300 GRACE=20 bash ~/skills/team-dispatch/scripts/watch.sh
```

---

## 📝 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本历史。

### 最新：v0.0.1
- 🌍 添加国际化支持（中英文双语）
- 添加低频扫描器（事件 + 扫描兜底）
- 添加 per-Agent 可配置显示名/用户名 + Telegram 通知
- 添加复盘模板 + 故障排查文档
- 推荐并发上限提升至 10

---

## 🤝 贡献

1. Fork 仓库
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 提交 Pull Request

---

## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 详情。

---

## 👤 作者

**VVUSU** 🐟

为 OpenClaw 打造的多 Agent 编排系统。

---

<div align="center">

**Made with ❤️ for OpenClaw Community**

[报告问题](https://github.com/vvusu/team-dispatch/issues) • [请求功能](https://github.com/vvusu/team-dispatch/issues)

</div>
