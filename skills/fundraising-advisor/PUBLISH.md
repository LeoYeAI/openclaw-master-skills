# 发布到 ClawHub 指南

本指南说明如何将 FA Advisor skill 发布到 [ClawHub](https://clawhub.ai/)。

## 前置要求

1. **GitHub 账户**（至少一周以上）
2. **OpenClaw CLI** 已安装
3. **项目已构建** (`pnpm build`)

## 发布方式

ClawHub 支持三种发布方式：

### 方式 1: CLI 命令（推荐）⭐

最快速的发布方式：

```bash
# 1. 登录 ClawHub
clawhub login

# 2. 发布技能
clawhub publish . \
  --slug fa-advisor \
  --name "FA Advisor" \
  --version 0.1.0 \
  --tags finance,investment,fundraising,valuation,startup \
  --changelog "Initial release with project assessment, pitch deck generation, valuation, and investor matching"
```

**可选参数：**
- `--slug`: URL友好的标识符（必需）
- `--name`: 显示名称（必需）
- `--version`: 语义化版本号（必需）
- `--tags`: 逗号分隔的标签
- `--changelog`: 版本更新说明

### 方式 2: Web 上传界面

适合不熟悉命令行的用户：

1. 访问 [clawhub.ai/upload](https://clawhub.ai/upload)
2. 准备技能文件：
   ```bash
   # 创建发布包
   pnpm build

   # 打包（包含 SKILL.md 和必要文件）
   zip -r fa-advisor.zip . \
     -x "node_modules/*" \
     -x ".git/*" \
     -x "dist/*" \
     -x "*.log"
   ```
3. 拖放 ZIP 文件或整个文件夹到上传区域
4. 提交并等待审核

### 方式 3: GitHub Pull Request

适合开源贡献者：

1. Fork [openclaw/clawhub](https://github.com/openclaw/clawhub) 仓库

2. 克隆你的 fork：
   ```bash
   git clone https://github.com/YOUR_USERNAME/clawhub.git
   cd clawhub
   ```

3. 添加你的技能：
   ```bash
   # 创建技能目录
   mkdir -p skills/fa-advisor

   # 复制技能文件
   cp -r /path/to/ai-fa/* skills/fa-advisor/

   # 确保包含 SKILL.md
   ls skills/fa-advisor/SKILL.md
   ```

4. 提交并创建 PR：
   ```bash
   git add skills/fa-advisor
   git commit -m "feat: add FA Advisor skill for investment advisory"
   git push origin main

   # 然后在 GitHub 上创建 Pull Request
   ```

## SKILL.md 检查清单

在发布前，确保 `SKILL.md` 包含：

- [x] **name**: 技能名称
- [x] **description**: 清晰的描述和使用场景
- [x] **version**: 语义化版本（如 0.1.0）
- [x] **metadata.clawdbot**: 元数据部分
  - [x] **emoji**: 代表性emoji（💼）
  - [x] **homepage**: GitHub 仓库链接
  - [x] **tags**: 相关标签数组
  - [x] **requires**: 依赖声明
    - [x] env: 环境变量（我们没有）
    - [x] bins: 二进制依赖（我们没有）
    - [x] config: 配置项（我们没有）
  - [x] **os**: 支持的平台 [darwin, linux, win32]
- [x] **详细说明**: 使用方法、示例、功能说明
- [x] **示例场景**: 实际使用案例

## 文件要求

ClawHub 只接受文本文件。确保包含：

✅ **必需文件：**
- `SKILL.md` - 技能描述和文档
- `package.json` - 依赖和元数据
- `src/**/*.ts` - TypeScript 源代码
- `README.md` - 项目文档

✅ **推荐文件：**
- `CHANGELOG.md` - 版本历史
- `LICENSE` - 许可证
- `examples/` - 使用示例
- `.clawignore` - 忽略文件清单

❌ **排除文件：**
- `node_modules/` - 依赖包
- `dist/` - 构建输出
- `.git/` - Git 历史
- 二进制文件、图片（非文本）

## 发布前检查

运行这个检查清单：

```bash
# 1. 确保 SKILL.md 存在
ls SKILL.md

# 2. 检查 SKILL.md 格式
head -20 SKILL.md  # 查看 frontmatter

# 3. 构建项目
pnpm build

# 4. 运行测试（如果有）
pnpm test

# 5. 检查文件大小
du -sh .

# 6. 预览要发布的文件
find . -type f \
  -not -path "./node_modules/*" \
  -not -path "./dist/*" \
  -not -path "./.git/*"
```

## 版本管理

遵循 [语义化版本](https://semver.org/):

- **MAJOR** (1.0.0): 不兼容的 API 变更
- **MINOR** (0.1.0): 向后兼容的新功能
- **PATCH** (0.0.1): 向后兼容的 bug 修复

### 更新已发布的技能

```bash
# 更新版本号
npm version patch  # 0.1.0 → 0.1.1
# 或
npm version minor  # 0.1.0 → 0.2.0

# 重新发布
clawhub publish . \
  --slug fa-advisor \
  --version $(node -p "require('./package.json').version") \
  --changelog "Fixed valuation calculation bug"
```

## 标签（Tags）管理

每次发布会创建一个新的版本。你可以使用标签指向特定版本：

```bash
# 发布为 latest（默认）
clawhub publish . --slug fa-advisor --version 0.1.0

# 发布为 beta
clawhub publish . --slug fa-advisor --version 0.2.0-beta.1 --tag beta

# 移动 latest 标签（回滚）
clawhub tag fa-advisor latest 0.1.0
```

## 常见问题

### Q: 发布失败，提示 "GitHub account must be at least one week old"
**A:** ClawHub 要求 GitHub 账户至少创建一周以上才能发布，这是为了防止滥用。

### Q: 如何更新已发布的技能？
**A:** 修改代码后，更新 `version` 字段，然后重新运行 `clawhub publish`。

### Q: 可以发布私有技能吗？
**A:** 目前 ClawHub 主要是公开技能市场。如果需要私有技能，可以在本地使用或通过私有 Git 仓库分发。

### Q: 发布需要多久审核？
**A:** 通过 CLI 发布通常是即时的。通过 PR 提交需要等待维护者审核（通常 1-3 天）。

### Q: 如何删除或下架技能？
**A:** 联系 ClawHub 维护团队或在 GitHub 仓库提交 issue。

## 发布后

### 1. 验证发布

```bash
# 搜索你的技能
clawhub search fa-advisor

# 查看详情
clawhub show fa-advisor

# 测试安装
openclaw skill add fa-advisor
```

### 2. 推广

- 在 GitHub README 中添加 ClawHub 徽章
- 在社交媒体分享
- 在 OpenClaw 社区讨论
- 写博客文章介绍使用方法

### 3. 维护

- 响应用户反馈和 issues
- 定期更新依赖
- 改进文档
- 添加新功能

## 资源链接

- [ClawHub 官网](https://clawhub.ai/)
- [OpenClaw 文档](https://docs.openclaw.ai/)
- [ClawHub GitHub](https://github.com/openclaw/clawhub)
- [技能开发指南](https://docs.openclaw.ai/tools/skills)
- [发布清单](https://gist.github.com/adhishthite/0db995ecfe2f23e09d0b2d418491982c)

## 需要帮助？

- GitHub Issues: 技术问题和 bug 报告
- Discord: OpenClaw 社区讨论
- Docs: 查阅官方文档

祝发布顺利！🚀
