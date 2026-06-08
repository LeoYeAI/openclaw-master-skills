# 🎯 配置指南

## 快速配置（3 步完成）

### 1️⃣ 安装技能

```bash
clawhub install cann-review
```

### 2️⃣ 配置 Token

```bash
cd ~/.openclaw/workspace/skills/cann-review
./gitcode-api.sh setup
```

按提示输入你的 GitCode API Token。

<details>
<summary>🔑 获取 Token</summary>

1. 访问 https://gitcode.com/setting/token-classic
2. 点击"生成新令牌"
3. 选择权限：`api`, `write_repository`
4. 复制生成的 Token

</details>

### 3️⃣ 验证配置

```bash
./test-api.sh
```

看到 "✅ 所有测试通过！" 就完成了！

---

## 配置方式对比

| 方式 | 命令 | 优点 | 适用场景 |
|------|------|------|----------|
| **配置向导** | `./gitcode-api.sh setup` | 简单、交互式 | 推荐新手 |
| **手动配置** | 编辑 `config/gitcode.conf` | 灵活 | 自定义配置 |
| **环境变量** | `export GITCODE_API_TOKEN=xxx` | 临时、测试 | CI/CD |

---

## 配置文件详解

### 文件位置

```
~/.openclaw/workspace/skills/cann-review/
├── config/
│   ├── gitcode.conf.example  # 模板
│   └── gitcode.conf         # 你的配置（自动生成）
```

### 文件内容

```bash
# GitCode API 配置

# API Token（必需）
GITCODE_API_TOKEN=your_token_here

# API Base URL（可选，默认值）
GITCODE_API_BASE=https://api.gitcode.com/api/v5
```

### 文件权限

```bash
-rw-------  1 user  staff  123 Mar  4 10:15 config/gitcode.conf
```

权限 `600` 确保只有你可以读取配置文件。

---

## 常见问题

### Q: 配置文件在哪里？

```bash
~/.openclaw/workspace/skills/cann-review/config/gitcode.conf
```

### Q: 如何查看当前配置？

```bash
cat ~/.openclaw/workspace/skills/cann-review/config/gitcode.conf
```

### Q: 如何重新配置？

```bash
cd ~/.openclaw/workspace/skills/cann-review
rm config/gitcode.conf
./gitcode-api.sh setup
```

### Q: Token 会泄露吗？

不会。配置文件：
- ✅ 在 `.gitignore` 中（不会提交到 git）
- ✅ 权限 600（仅你可读）
- ✅ 不在全局 TOOLS.md（隔离性）

### Q: 可以用环境变量吗？

可以，优先级最高：

```bash
export GITCODE_API_TOKEN=your_token_here
```

### Q: 多个技能会冲突吗？

不会。每个技能有独立的配置文件。

---

## 安全建议

### ✅ 推荐做法

- 使用配置向导（`./gitcode-api.sh setup`）
- 定期轮换 Token
- 不要在命令行直接传递 Token（会被记录到 history）

### ❌ 避免的做法

- 不要把 Token 提交到 git
- 不要在共享脚本中硬编码 Token
- 不要在日志中打印 Token

---

## 下一步

配置完成后：

1. **审查 PR**: `审查 PR#626`
2. **自动审查**: 配置定时任务
3. **查看文档**: `README.md`

---

## 获取帮助

如有问题：
- 查看日志：`./test-api.sh`
- 查看文档：`README.md`
- 重新配置：`./gitcode-api.sh setup`
