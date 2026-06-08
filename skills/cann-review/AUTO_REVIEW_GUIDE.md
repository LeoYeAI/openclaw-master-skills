# 自动审查配置指南

本指南说明如何配置和启动 CANN 代码审查的自动审查功能。

---

## 🎯 功能说明

自动审查功能采用**单次模式**，每次只审查一个 PR：

- ✅ 定时检查指定仓库的开放 PR
- ✅ 每次只审查一个 PR（避免上下文超限）
- ✅ 自动发布审查报告
- ✅ 支持多个仓库
- ✅ 避免重复审查
- ✅ 记录审查历史

**优势**：
- 🚀 **避免上下文超限**：一次只审查一个 PR
- ⚡ **执行速度快**：每次只需几秒钟
- 🔄 **持续进行**：定时任务会持续审查新 PR

---

## 📦 第一步：配置审查仓库

### 方法 1：使用配置文件（推荐）

```bash
cd ~/.openclaw/workspace/skills/cann-review

# 复制配置模板
cp config/repos.conf.example config/repos.conf

# 编辑配置文件
nano config/repos.conf
```

添加需要审查的仓库（每行一个，格式: `owner/repo`）：

```
cann/runtime
cann/compiler
cann/driver
cann/tools
cann/samples
```

### 方法 2：使用环境变量

```bash
export CANN_REVIEW_REPOS="cann/runtime,cann/compiler,cann/driver"
```

---

## 🚀 第二步：启动自动审查

### 方式 1：手动测试单次审查

```bash
cd ~/.openclaw/workspace/skills/cann-review
./auto-review-single.sh
```

**输出示例**：
```
🤖 CANN 自动审查（单次模式）
================================
开始时间: 2026-03-04 18:26:20

🔍 查找下一个需要审查的 PR...
📋 检查仓库: cann/runtime

📝 找到需要审查的 PR:
  仓库: cann/runtime
  PR: #643
  
  标题: 用例运行完成后，清理桩函数
  作者: zhangsan
  链接: https://gitcode.com/cann/runtime/merge_requests/643

✅ 已标记为待审查

下次定时任务触发时，会自动审查下一个 PR
```

### 方式 2：配置 OpenClaw Cron（推荐）

创建定时任务，每 2 小时审查一个 PR：

#### 步骤 1：创建 Cron 任务

```bash
openclaw cron add
```

或者直接编辑配置（添加到 OpenClaw 配置中）。

#### 步骤 2：配置内容

```yaml
cron:
  - name: "cann-auto-review"
    schedule:
      kind: "every"
      everyMs: 7200000  # 每 2 小时
    payload:
      kind: "agentTurn"
      message: "运行 CANN 自动审查"
    sessionTarget: "isolated"
    enabled: true
```

#### 步骤 3：在技能中处理

当收到 "运行 CANN 自动审查" 消息时，技能会：
1. 读取配置的仓库列表
2. 逐个审查开放的 PR
3. 发布审查报告
4. 发送汇总结果

### 方式 3：使用系统 Cron

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每 2 小时执行一次）
0 */2 * * * cd ~/.openclaw/workspace/skills/cann-review && ./auto-review.sh >> /tmp/cann-review.log 2>&1
```

---

## 📊 配置示例

### 示例 1：审查单个仓库

```bash
# config/repos.conf
cann/runtime
```

### 示例 2：审查多个仓库

```bash
# config/repos.conf
cann/runtime
cann/compiler
cann/driver
```

### 示例 3：使用环境变量

```bash
export CANN_REVIEW_REPOS="cann/runtime,cann/compiler"
./auto-review.sh
```

---

## ⚙️ 高级配置

### 配置审查间隔

修改 cron 配置中的 `everyMs` 值。

```yaml
everyMs: 3600000  # 每 1 小时
everyMs: 7200000  # 每 2 小时（默认）
everyMs: 14400000  # 每 4 小时
```

### 配置审查范围

可以通过环境变量控制：

```bash
# 只审查最近 7 天的 PR
export CANN_REVIEW_DAYS=7

# 只审查没有 lgtm 标签的 PR
export CANN_REVIEW_SKIP_LGTM=true
```

### 配置通知方式

可以配置审查结果的通知方式：

```bash
# 发送到特定频道
export CANN_REVIEW_NOTIFY_CHANNEL="telegram"
export CANN_REVIEW_NOTIFY_TARGET="@mychat"
```

---

## 📝 审查状态管理

自动审查会维护状态文件 `.review-state.json`，避免重复审查：

```json
{
  "cann/runtime": {
    "lastReview": "2026-03-04T12:00:00Z",
    "reviewedPRs": [628, 629, 630]
  },
  "cann/compiler": {
    "lastReview": "2026-03-04T10:00:00Z",
    "reviewedPRs": [123, 124]
  }
}
```

---

## 🔍 监控和日志

### 查看日志

```bash
# 如果使用系统 cron
tail -f /tmp/cann-review.log

# 如果使用 OpenClaw cron
openclaw logs
```

### 查看审查状态

```bash
cd ~/.openclaw/workspace/skills/cann-review
cat .review-state.json
```

---

## 🐛 故障排查

### 问题 1：没有审查任何 PR

**可能原因**：
- 没有配置仓库
- Token 无效
- 没有开放的 PR

**解决方法**：
```bash
# 检查配置
cat config/repos.conf

# 测试 API
./gitcode-api.sh get-pr cann runtime 628

# 检查 PR 列表
./gitcode-api.sh list-prs cann runtime
```

### 问题 2：重复审查相同的 PR

**可能原因**： 状态文件损坏

**解决方法**：
```bash
# 重置状态
rm .review-state.json
./auto-review.sh
```

### 问题 3：审查失败

**可能原因**： API 调用失败

**解决方法**：
```bash
# 检查日志
./auto-review.sh 2>&1 | tee review.log

# 查看错误信息
grep -i "error\|fail" review.log
```

---

## 💡 最佳实践

1. **从少量仓库开始**： 先配置 1-2 个仓库测试
2. **设置合理间隔**： 建议 2-4 小时，避免过于频繁
3. **监控日志**： 定期检查日志，确保正常运行
4. **及时清理状态**： 如果需要重新审查，可以删除状态文件
5. **配置通知**： 将审查结果发送到合适的频道

---

## 📚 相关文档

- **快速开始**: [QUICKSTART.md](QUICKSTART.md)
- **配置指南**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **完整文档**: [README.md](README.md)
- **技能说明**: [SKILL.md](SKILL.md)

---

## 🎯 快速开始

```bash
# 1. 配置仓库
cd ~/.openclaw/workspace/skills/cann-review
cp config/repos.conf.example config/repos.conf
nano config/repos.conf  # 添加你的仓库

# 2. 测试运行
./auto-review.sh

# 3. 配置定时任务（可选）
# 参考 "第二步：启动自动审查" 部分
```

---

**最后更新**: 2026-03-04
**版本**: v3.1.0
