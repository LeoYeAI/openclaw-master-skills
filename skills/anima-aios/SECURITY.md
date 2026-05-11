# Anima AIOS — 安全与隐私说明

> v6.2.2 | 最后更新：2026-03-26

---

## 📁 文件访问范围

本 Skill 会访问以下目录（均为**本地文件系统**）：

| 路径 | 用途 | 读写 |
|------|------|------|
| `~/.openclaw/workspace-{agent}/memory/` | 读取/同步 OpenClaw 原生记忆 | 读 |
| `~/.openclaw/agents/{agent}/sessions/` | 读取 session 历史（v6.2 记忆导入） | 读 |
| `{facts_base}/{agent}/facts/` | 写入 Anima 事实数据 | 写 |
| `{facts_base}/shared/` | 团队知识共享目录 | 读/写 |
| `{facts_base}/*/cognitive_profile.json` | 团队排行时读取其他 Agent 画像 | 读 |

**默认 `facts_base`：** `/home/画像`（可通过 `ANIMA_FACTS_BASE` 环境变量覆盖）

**不会访问：** 用户主目录其他位置、系统文件、网络资源

---

## 🔐 环境变量（可选）

| 变量名 | 用途 | 默认值 |
|--------|------|--------|
| `ANIMA_FACTS_BASE` | Facts 数据存储基础路径 | `/home/画像` |
| `ANIMA_WORKSPACE` | OpenClaw workspace 路径（用于 agent 名称解析） | 自动检测 |
| `ANIMA_AGENT_NAME` | Agent 中文名（用于覆盖自动检测） | 自动检测 |

---

## ⚙️ 后台行为

| 功能 | 说明 | 触发条件 | 关闭方法 |
|------|------|----------|----------|
| **memory_watcher** | 基于 watchdog 的文件系统监听 | 安装后手动启用 | `anima_config.json` 中设置 `memory_watcher: false` |
| **每日进化** | 凌晨 3:00 自动提炼 L2→L3 记忆 | cron 定时任务 | 不配置 cron 或设置 `auto_evolution: false` |
| **团队排行** | 扫描其他 Agent 的 `cognitive_profile.json` | `team_mode: true` 时 | `anima_config.json` 中设置 `team_mode: false` |

---

## 🚫 关闭敏感功能

在 `~/.anima/{agent}/anima_config.json` 中设置：

```json
{
  "team_mode": false,
  "memory_watcher": false,
  "auto_evolution": false
}
```

---

## 🧪 安装前测试建议

1. **在沙箱环境运行**：
   ```bash
   # 设置独立的 facts_base
   export ANIMA_FACTS_BASE=/tmp/anima-test
   ```

2. **运行集成测试**：
   ```bash
   pip install watchdog
   python3 tests/test_integration_v6.py
   ```

3. **检查 post-install.sh**：
   ```bash
   cat post-install.sh
   ```

---

## 📋 ClawHub 审查响应

| 审查项 | 状态 | 说明 |
|--------|------|------|
| 目的与能力匹配 | ✅ | 代码实现与描述一致 |
| 指令范围 | ✅ | SKILL.md + SECURITY.md 明确说明 |
| 安装机制 | ✅ | 无外部下载，仅 pip install watchdog |
| 凭证声明 | ✅ | _meta.json 已声明环境变量 |
| 持久化与权限 | ✅ | 非 always:true，后台行为可关闭 |

---

_如有疑问，请提 Issue 或联系作者_
