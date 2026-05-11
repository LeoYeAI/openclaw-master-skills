# 🔒 安全说明 (Security Policy)

## OpenClaw 安全扫描提示

如果 OpenClaw 安全扫描提示本 skill 为 **"Suspicious"（可疑）**，这是**正常且预期**的行为。

### 为什么会被标记？

1. **需要外部 API 凭证（GitHub Token）**
   - 本 skill 使用 GitHub API 搜索开发者
   - 需要用户自行申请并配置 GitHub Personal Access Token
   - Token 存储在本地 `.env` 文件中（不会上传到 git）

2. **包含 Prompt 模板**
   - `prompts/jd_parser_prompt.md` - 用于解析招聘需求
   - `prompts/pitch_writer_prompt.md` - 用于生成触达话术
   - 这些是**功能需要**，不是恶意 prompt injection

3. **元数据中省略了凭证配置**
   - 出于安全考虑，skill 不包含预配置的 Token
   - 用户必须自行配置（防止凭证泄露）

---

## 安全保证

### ✅ 我们做到了什么

| 安全措施 | 说明 |
|---------|------|
| **不包含真实凭证** | `.env` 文件为空模板，需用户自行配置 |
| **不自动执行操作** | 所有候选人需人工确认，触达话术需人工审核 |
| **仅使用公开数据** | 只使用 GitHub 公开 API，不爬取私密信息 |
| **Human-in-the-Loop** | 用户逐一确认候选人，不批量发送消息 |
| **本地数据存储** | 搜索结果存储在本地，不上传到任何服务器 |
| **遵循 .gitignore** | 敏感文件（Token、搜索结果）不会被上传 |

### ❌ 我们不会做什么

- ❌ 不购买/爬取私密数据
- ❌ 不绕过 GitHub 反爬机制
- ❌ 不自动发送邮件或消息
- ❌ 不将候选人数据上传到任何服务器
- ❌ 不存储或共享用户的 GitHub Token

---

## GitHub Token 安全配置

### 如何安全地配置 Token

1. **申请 Token**
   - 访问 https://github.com/settings/tokens
   - 创建新 token，只勾选 `read:user` 和 `read:org` 权限（最小权限原则）
   - 复制 token

2. **配置 Token**
   ```bash
   # 方式1: 使用 .env 文件（推荐，持久化）
   echo "GITHUB_TOKEN=your_token_here" > ~/.openclaw/workspace/skills/ai-talent-hunter/.env
   
   # 方式2: 临时环境变量（不持久化）
   export GITHUB_TOKEN=ghp_your_token_here
   ```

3. **验证 .gitignore**
   ```bash
   # 确认 .env 在 .gitignore 中
   grep ".env" ~/.openclaw/workspace/skills/ai-talent-hunter/.gitignore
   ```

### Token 安全红线

| ❌ 绝对不要 | ✅ 应该这样 |
|------------|------------|
| 把 Token 提交到 git | 使用 `.env` 文件（已在 .gitignore 中） |
| 在代码中硬编码 Token | 从环境变量读取 |
| 给予过高权限（如 repo、admin） | 只给 `read:user` 和 `read:org` |
| 分享给他人 | 每人使用自己的 Token |

---

## 数据隐私

### 搜索结果存储位置

- **本地 JSONL 文件**：`~/.openclaw/workspace/skills/ai-talent-hunter/data/candidates.jsonl`
- **不上传到云端**：所有数据存储在本地，不会发送到任何第三方服务器
- **已在 .gitignore**：`data/` 文件夹不会被 git 追踪

### 候选人隐私保护

- ✅ 只使用 GitHub 公开信息（Profile、公开仓库、公开邮箱）
- ✅ 不爬取私密仓库或非公开数据
- ✅ Human-in-the-Loop：用户逐一确认候选人，避免大撒网式骚扰
- ✅ 触达话术仅作草稿，需人工审核后手动发送

---

## 合规说明

本 skill 遵守以下原则：

1. **GitHub API 使用条款**
   - 使用 GitHub 官方 GraphQL API
   - 遵守 Rate Limiting（每次请求间隔 0.5 秒）
   - 不绕过任何反爬机制

2. **反垃圾邮件**
   - 不自动批量发送邮件
   - 用户必须逐一确认每位候选人
   - 生成的话术仅作草稿，需人工审核

3. **数据保护**
   - 不收集用户的 GitHub Token
   - 不上传候选人数据到任何服务器
   - 不与第三方共享搜索结果

---

## 审计与透明

### 代码审计

本 skill 的核心脚本：
- `scripts/github_search.py` - GitHub API 调用和搜索逻辑
- `scripts/candidate_manager.py` - 候选人状态管理
- `scripts/location_data.py` - 地理位置匹配规则

所有代码开源，欢迎审计。

### 报告安全问题

如果你发现任何安全漏洞，请通过以下方式联系：
- 在 ClawHub 上私信作者
- 或在 GitHub 上提交 Security Advisory

---

## 常见问题

### Q: 为什么 OpenClaw 标记为 "Suspicious"？
A: 因为本 skill 需要外部 API 凭证（GitHub Token）并包含 Prompt 模板。这是功能需要，不是安全威胁。

### Q: 我的 GitHub Token 会被上传吗？
A: 不会。Token 存储在 `.env` 文件中，该文件已在 `.gitignore` 中，不会被 git 追踪。

### Q: 搜索结果会被分享给其他人吗？
A: 不会。所有数据存储在本地，不会上传到任何服务器。

### Q: 这个 skill 会自动发送邮件吗？
A: 不会。所有触达话术仅作草稿，需要你人工审核后手动发送。

---

_最后更新：2026-03-26_
