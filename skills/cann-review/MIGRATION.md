# 迁移指南：从 v2.x 到 v3.0

本文档帮助你从基于浏览器的 v2.x 版本迁移到基于 API 的 v3.0 版本。

## 🎯 为什么要迁移？

v3.0 完全基于 GitCode API，相比浏览器自动化：

- ✅ **更稳定**：不受页面元素变化影响
- ✅ **更快速**：无需等待页面加载和渲染
- ✅ **更可靠**：无浏览器连接问题
- ✅ **更简单**：无需处理元素定位和 ref 管理

## 📋 主要变更

### 1. 配置变更

**v2.x (浏览器模式)**：
```yaml
# 无需特殊配置
# 使用 OpenClaw 内置浏览器
profile: "openclaw"
```

**v3.0 (API 模式)**：
```yaml
# 需要在 TOOLS.md 中配置 API Token
### GitCode
- **Personal Access Token**: `your-token-here`
- **API Base URL**: `https://api.gitcode.com/api/v5`
```

### 2. 调用方式变更

**v2.x**：
```yaml
# 打开浏览器
browser:
  action: open
  profile: "openclaw"
  targetUrl: "https://gitcode.com/cann/runtime/pull/628"
```

**v3.0**：
```bash
# 直接使用 API
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.gitcode.com/api/v5/repos/cann/runtime/pulls/628"
```

### 3. 评论发布变更

**v2.x**：
```yaml
# 1. 获取快照
browser:
  action: snapshot
  refs: "aria"

# 2. 定位输入框
# 3. 输入内容
# 4. 点击发送按钮
```

**v3.0**：
```bash
# 一步完成
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"body":"审查报告内容"}' \
  "https://api.gitcode.com/api/v5/repos/cann/runtime/pulls/628/comments"
```

## 🚀 迁移步骤

### 步骤 1：获取 API Token

1. 访问 https://gitcode.com/setting/token-classic
2. 创建新的 Personal Access Token
3. 选择权限：`api`, `write_repository`
4. 复制生成的 Token

### 步骤 2：配置 Token

**v3.0 使用独立的配置文件（更安全）：**

```bash
cd ~/.openclaw/workspace/skills/cann-review
./gitcode-api.sh setup
```

或手动配置：

```bash
cp config/gitcode.conf.example config/gitcode.conf
nano config/gitcode.conf
# 设置 GITCODE_API_TOKEN=your_token_here
```

**v2.x 使用 TOOLS.md（不推荐）：**

```markdown
### GitCode
- **Personal Access Token**: `your-token-here`
```

**为什么改变？**
- ✅ **更安全**：配置文件权限为 600，仅当前用户可读
- ✅ **更灵活**：每个技能独立配置，不污染全局 TOOLS.md
- ✅ **更简单**：提供配置向导，一键设置

### 步骤 3：更新技能

技能已自动更新到 v3.0，无需手动操作。

### 步骤 4：测试

```bash
# 测试 API 连接
./gitcode-api.sh get-pr cann runtime 628

# 如果返回 PR 信息，说明配置成功
```

## ⚠️ 注意事项

### 已移除的功能

- ❌ 浏览器自动化相关配置
- ❌ ref 编号和元素定位
- ❌ aria refs 和 role refs
- ❌ 浏览器连接管理

### 行为变更

1. **已合并的 PR**：
   - v2.x：可以尝试评论，可能失败
   - v3.0：API 直接返回错误（更明确）

2. **评论格式**：
   - v2.x：Markdown 通过浏览器输入
   - v3.0：Markdown 需要转义为 JSON 字符串

3. **错误处理**：
   - v2.x：浏览器错误（连接丢失、元素未找到）
   - v3.0：API 错误（401, 404, 429 等）

## 🐛 常见问题

### Q: Token 在哪里获取？
A: https://gitcode.com/setting/token-classic

### Q: API 有频率限制吗？
A: 有，50次/分钟，4000次/小时。对于正常使用足够。

### Q: 能同时使用 v2.x 和 v3.0 吗？
A: 不建议。v3.0 已完全替代 v2.x。

### Q: 浏览器模式还有优势吗？
A: 对于代码审查场景，API 模式在所有方面都更优。

## 📚 相关文档

- [README.md](README.md) - 使用指南
- [SKILL.md](SKILL.md) - 技能详细文档
- [CHANGELOG.md](CHANGELOG.md) - 完整变更日志

## 💬 获取帮助

如有问题，请联系维护团队。
