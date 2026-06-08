# 单次审查模式使用指南

## 🎯 为什么要单次审查？

**问题**：一次性审查多个 PR 会导致上下文窗口超限

**解决方案**：每次只审查一个 PR

---

## 📋 工作流程

### 自动模式（推荐）

定时任务每 2 小时自动执行：

```
1. 扫描配置的仓库
2. 找到第一个未审查的 PR
3. 审查这一个 PR
4. 标记为已审查
5. 发送通知
6. 等待下次触发
```

### 手动模式

```bash
cd ~/.openclaw/workspace/skills/cann-review

# 查找下一个需要审查的 PR
./auto-review-single.sh

# 输出示例：
# 🤖 CANN 自动审查（单次模式）
# ================================
# 找到需要审查的 PR:
#   仓库: cann/runtime
#   PR: #643
#   标题: 用例运行完成后，清理桩函数
#   链接: https://gitcode.com/cann/runtime/merge_requests/643
#
# 💡 请使用以下命令审查:
#   审查这个 PR: https://gitcode.com/cann/runtime/merge_requests/643
```

---

## 🚀 快速开始

### 1. 配置 Token（首次）

```bash
cd ~/.openclaw/workspace/skills/cann-review
./gitcode-api.sh setup
```

### 2. 配置仓库

```bash
cp config/repos.conf.example config/repos.conf
nano config/repos.conf
```

添加：
```
cann/runtime
cann/compiler
```

### 3. 测试单次审查

```bash
./auto-review-single.sh
```

### 4. 启用定时任务

```bash
cron action=list  # 查看已有的定时任务
```

---

## 📊 审查状态

### 查看已审查的 PR

```bash
cat ~/.openclaw/workspace/skills/cann-review/.review-state.json
```

### 重置审查状态

```bash
rm ~/.openclaw/workspace/skills/cann-review/.review-state.json
```

---

## 💡 使用建议

### 场景 1：自动审查

- 配置 cron 定时任务（每 2 小时）
- 系统自动审查一个 PR
- 完成后发送通知

### 场景 2：手动审查

- 运行 `./auto-review-single.sh` 找到下一个 PR
- 手动审查：`审查这个 PR: <链接>`
- 审查完成后自动标记

### 场景 3：批量查找

- 运行 `./simple-review.sh` 扫描所有仓库
- 查看所有开放的 PR
- 选择感兴趣的 PR 手动审查

---

## 🎯 优势对比

| 方式 | 上下文使用 | 速度 | 可靠性 |
|------|----------|------|--------|
| **单次审查** | ✅ 低 | ✅ 快 | ✅ 高 |
| 批量审查 | ❌ 高 | ⚠️ 慢 | ❌ 易超限 |

---

## 📝 示例输出

```bash
$ ./auto-review-single.sh

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

💡 提示: 这个 PR 已加入审查队列
   链接: https://gitcode.com/cann/runtime/merge_requests/643

下次定时任务触发时，会自动审查下一个 PR

================================
结束时间: 2026-03-04 18:26:22
```

---

## 🐛 常见问题

### Q: 如何查看下一个要审查的 PR？

```bash
./auto-review-single.sh
```

### Q: 如何跳过某个 PR？

手动标记为已审查：
```bash
echo '{"reviewed": ["cann/runtime#643"]}' > .review-state.json
```

### Q: 如何重新审查所有 PR？

```bash
rm .review-state.json
```

---

## 📚 相关文档

- [自动审查指南](AUTO_REVIEW_GUIDE.md)
- [快速开始](QUICKSTART.md)
- [配置指南](SETUP_GUIDE.md)

---

**更新时间**: 2026-03-04
**版本**: v3.2.0
