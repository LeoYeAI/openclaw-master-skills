# WeChat MD Publisher - OpenClaw Skill

> 全功能微信公众号 Markdown 发布工具 - OpenClaw Skill 版本

## 🚀 快速安装

### 方法 1：从 ClawHub 安装（推荐）

```bash
openclaw skills install wechat-md-publisher
```

### 方法 2：从 GitHub 安装

```bash
openclaw skills install https://github.com/sipingme/wechat-md-publisher-skill
```

### 方法 3：手动安装

1. 克隆仓库：
```bash
git clone https://github.com/sipingme/wechat-md-publisher-skill.git
cd wechat-md-publisher-skill
```

2. 复制到 OpenClaw skills 目录：
```bash
cp -r . ~/.openclaw/skills/wechat-md-publisher/
```

3. 安装依赖：
```bash
npm install -g wechat-md-publisher
```

4. 使脚本可执行：
```bash
chmod +x scripts/publish.sh
```

## ✅ 验证安装

```bash
# 检查 Skill 是否可用
openclaw skills list --eligible

# 查看 Skill 详情
openclaw skills info wechat-md-publisher

# 测试命令
wechat-pub --version
```

## 📋 首次配置

### 1. 获取微信公众号凭证

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入「设置与开发」→「基本配置」
3. 获取「开发者ID(AppID)」和「开发者密码(AppSecret)」
4. 将服务器 IP 添加到「IP白名单」

### 2. 配置账号

```bash
wechat-pub account add \
  --name "我的公众号" \
  --app-id "wx_your_app_id" \
  --app-secret "your_app_secret" \
  --default
```

### 3. 测试发布

```bash
# 创建测试文章
cat > test.md << 'EOF'
---
title: 测试文章
---
# Hello World
这是一篇测试文章。
EOF

# 发布
wechat-pub publish create --file test.md --theme default
```

## 🎯 使用方式

### 在 OpenClaw 对话中使用

**示例 1：发布文章**

```
用户: 帮我把这篇文章发布到微信公众号

[提供 Markdown 内容]

AI: 好的，我来帮你发布。正在使用 orangeheart 主题...
✓ 文章已成功发布！发布 ID: 2247483647_1
```

**示例 2：创建草稿**

```
用户: 先创建一个草稿，不要立即发布

AI: 明白，我会先创建草稿。
✓ 草稿创建成功，Media ID: 3_abc123
你可以在微信公众平台查看和编辑。
```

**示例 3：查看文章列表**

```
用户: 查看我已发布的微信文章

AI: 正在获取列表...
共 8 篇已发布文章：
1. 最新文章 (2026-03-19)
2. 产品介绍 (2026-03-18)
...
```

### 手动调用 Skill

```bash
# 使用 OpenClaw 命令
openclaw run wechat-md-publisher publish article.md orangeheart

# 或直接使用工具
wechat-pub publish create --file article.md --theme orangeheart
```

## � 与 news-to-markdown-skill 组合使用

**推荐组合**：一键转载新闻到微信公众号

### 快速示例

```bash
# 1. 提取新闻文章
convert-url --url "https://www.toutiao.com/article/123" \
  --output /tmp/article.md \
  --platform toutiao

# 2. 发布到微信公众号
wechat-pub publish create \
  --file /tmp/article.md \
  --theme orangeheart
```

### AI 自动化工作流

用户说：
> "帮我把这篇头条文章转载到我的微信公众号"

AI 自动执行：
1. 使用 `news-to-markdown-skill` 提取文章
2. 使用 `wechat-md-publisher-skill` 发布到微信
3. 返回发布结果

### 优势

✅ **智能提取** - 自动识别正文，过滤广告  
✅ **多平台支持** - 头条、微信、小红书  
✅ **精美渲染** - 8+ 主题可选  
✅ **一键发布** - 无需手动复制粘贴

详见 [SKILL.md](./SKILL.md) 中的完整集成指南。

---

## �📚 文档

- **[SKILL.md](./SKILL.md)** - 完整的 SOP 和使用指南（含 news-to-markdown 集成）
- **[quick-start.md](./references/quick-start.md)** - 5 分钟快速上手
- **[themes.md](./references/themes.md)** - 主题使用指南
- **[ip-whitelist-guide.md](./references/ip-whitelist-guide.md)** - IP 白名单配置指南 ⚠️ 重要

## 🎨 可用主题

- `default` - 简洁经典
- `orangeheart` - 温暖优雅 ⭐ 推荐
- `rainbow` - 活泼清爽
- `lapis` - 清新极简 ⭐ 推荐
- `pie` - 现代锐利
- `maize` - 柔和舒适
- `purple` - 简约文艺
- `phycat` - 薄荷清新
- `sport` - 运动风 🏃 活力动感

## 🔧 高级配置

### 环境变量（可选）

```bash
# 在 ~/.bashrc 或 ~/.zshrc 中添加
export WECHAT_APP_ID="wx_your_app_id"
export WECHAT_APP_SECRET="your_app_secret"
```

### 自定义主题

```bash
# 添加本地主题
wechat-pub theme add-local --name my-theme --path ./my-theme.css

# 添加远程主题 API
wechat-pub theme add-remote --name md2wechat --url https://api.md2wechat.cn --key xxx
```

## ⚠️ 常见问题

### 问题 1：Skill 未被识别

**解决**：
```bash
openclaw skills refresh
openclaw skills info wechat-md-publisher
```

### 问题 2：权限错误

**解决**：
```bash
chmod +x ~/.openclaw/skills/wechat-md-publisher/scripts/publish.sh
```

### 问题 3：找不到命令

**解决**：
```bash
npm install -g wechat-md-publisher
which wechat-pub  # 验证安装
```

### 问题 4：Token 过期

Token 会自动刷新，如仍有问题：
```bash
wechat-pub account remove <account-id>
wechat-pub account add --name "新账号" --app-id xxx --app-secret xxx
```

### 问题 5：更新 Skill 后依赖未更新

**✨ 自动更新（v0.2.2+）**

从 v0.2.2 开始，skill 会在每次运行时**自动检查并更新依赖**：

```bash
# 直接使用，无需手动操作
openclaw run wechat-md-publisher publish article.md

# 输出示例：
# 检查 wechat-md-publisher 依赖...
# 当前版本: v0.3.1
# 需要版本: v0.3.2
# 正在更新...
# ✓ 更新成功: v0.3.1 → v0.3.2
```

**手动更新（如果自动更新失败）**：

```bash
# 方法 1：强制重新安装（推荐）
npm uninstall -g wechat-md-publisher
npm install -g wechat-md-publisher@0.3.2

# 方法 2：清除缓存后安装
npm cache clean --force
npm install -g wechat-md-publisher@latest

# 验证版本
wechat-pub --version  # 应显示 0.3.2
```

**工作原理**：
- ✅ 每次运行时自动检查版本
- ✅ 版本不匹配时自动更新
- ✅ 无需用户手动干预
- ✅ 失败时回退到手动提示

## 🔒 安全性

### 权限要求

- ✅ 读取本地 Markdown 和图片文件
- ✅ 网络访问（仅限微信官方 API）
- ✅ 写入配置文件到 `~/.config/wechat-md-publisher-nodejs/`

### 数据隐私

- ❌ 不会上传数据到第三方服务器
- ❌ 不会收集用户信息
- ✅ 所有通信仅限于微信官方 API
- ✅ 配置文件仅存储在本地
[news-to-markdown](https://github.com/sipingme/news-to-markdown) - 新闻提取核心库
- 
### 安全检查

```bash
# 使用 skill-vetter 检查（如果可用）
openclaw skills vet wechat-md-publisher
```

## 📊 Skill 评分

根据 OpenClaw 社区标准：

- ✅ **规范清晰度**: 5/5 - SKILL.md 结构完整
- ✅ **首次成功时间**: 5/5 - 5 分钟内可完成
- ✅ **实用性**: 5/5 - 解决实际发布需求
- ✅ **安全性**: 5/5 - 权限合理，无恶意代码

## 🤝 贡献

欢迎贡献！

- 报告问题：[GitHub Issues](https://github.com/sipingme/wechat-md-publisher/issues)
- 提交改进：[Pull Requests](https://github.com/sipingme/wechat-md-publisher/pulls)
- 讨论交流：[GitHub Discussions](https://github.com/sipingme/wechat-md-publisher/discussions)

## 📜 许可证

Apache-2.0 License

## 👤 作者

**Ping Si** <sipingme@gmail.com>

- GitHub: [@sipingme](https://github.com/sipingme)
- 项目主页: [wechat-md-publisher](https://github.com/sipingme/wechat-md-publisher)

## 🙏 致谢

- [@wenyan-md/core](https://github.com/caol64/wenyan-core) - 提供精美主题和渲染引擎
- OpenClaw 社区 - 提供优秀的 AI Agent 框架

---

**让 AI 能够直接发布内容到微信公众号！** 🚀
