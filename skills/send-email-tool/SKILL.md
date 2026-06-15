---
name: send-email
description: 邮件发送工具。配置 SMTP 发件人后，通过脚本发送纯文本或 HTML 邮件，支持附件、抄送、密送。在需要发送邮件通知、报告、自动化邮件时触发。
---

# Send Email

通过 SMTP 发送邮件的工具，支持 keyring 密钥管理。

## 功能

- ✅ 支持 SMTP 邮件发送（Gmail、QQ 邮箱、163 邮箱等）
- ✅ 支持纯文本和 HTML 格式邮件
- ✅ **支持模板渲染**（使用 `--template` 参数，支持自定义模板）
- ✅ **支持内嵌图片**（图片直接显示在邮件正文中，不是链接）
- ✅ **自动检测 Markdown 格式**（含图片自动嵌入）
- ✅ 支持附件（文档、图片等）
- ✅ 支持抄送（CC）和密送（BCC）
- ✅ 配置持久化，避免重复输入
- ✅ **密钥管理**：支持 keyring 安全存储密码（推荐）

## 密钥管理

### ⚠️ 重要：密码安全

本技能**强制使用 keyring** 管理发件人邮箱和密码，避免敏感信息暴露在命令行或上下文中。

### 安装 keyring

```bash
pip install keyring
```

如果 keyring 未安装，脚本会自动使用备用存储方案（base64 编码的本地文件）。

### 首次使用：保存发件人邮箱

在发送邮件前，必须先保存发件人邮箱到 keyring：

```bash
# 保存发件人邮箱（会提示输入）
python3 send_email.py username --save --email your-email@gd.chinamobile.com

# 或只运行 --save，然后交互输入
python3 send_email.py username --save
```

### 保存密码

```bash
# 保存密码（会提示输入）
python3 send_email.py password --save
```

### 删除密钥

```bash
# 删除发件人邮箱
python3 send_email.py username --delete

# 删除密码
python3 send_email.py password --delete
```

### 查看密钥状态

```bash
# 查看发件人邮箱
python3 send_email.py username

# 查看密码状态
python3 send_email.py password
```

### ⚠️ 安全提醒

- **不要**在命令行参数中传递邮箱或密码
- **不要**使用 `--email` 参数直接指定发件人
- 始终通过 `username --save` 和 `password --save` 命令管理密钥
- 邮箱和密码会自动从 keyring 读取，无需每次输入
- 默认邮箱：user@gd.chinamobile.com

---

## 快速开始

### 0. 安装依赖（可选）

**推荐安装 `markdown` 库以支持 Markdown 自动转换：**

```bash
pip install markdown keyring
```

如果不安装 `markdown` 库，脚本仍可正常发送纯文本和 HTML 邮件，但无法自动转换 Markdown。

### 1. 首次配置

```bash
cd $CLAWD/skills/send-email/scripts

# 配置 SMTP 服务器（中国移动邮箱默认配置）
python3 send_email.py smtp --host smtp.gd.chinamobile.com --port 465 --no-tls

# 配置发件人名称
python3 send_email.py sender --name "Your Name"

# 保存发件人邮箱到 keyring
python3 send_email.py username --save --email your-email@gd.chinamobile.com

# 查看当前配置
python3 send_email.py config
```

**中国移动邮箱默认配置：**

| 配置项 | 值 |
|-------|-----|
| SMTP 服务器 | smtp.gd.chinamobile.com |
| 端口 | 465 (SSL) |
| TLS | ❌ (使用 SSL) |
| 默认邮箱 | user@gd.chinamobile.com |

**重要提示：** 如果使用 Gmail，需要生成「应用专用密码」（App Password），而不是使用账户密码。

---

### 2. 发送邮件

#### 首次使用：保存密码

```bash
python3 send_email.py password --save
# 按提示输入密码
```

#### 基础发送（纯文本）

```bash
python3 send_email.py send \
  --to recipient@example.com \
  --subject "邮件主题" \
  --body "邮件正文内容"
```

#### HTML 邮件

```bash
python3 send_email.py send \
  --to recipient@example.com \
  --subject "HTML 邮件" \
  --body "<h1>标题</h1><p>正文内容</p>" \
  --html
```

#### 带附件的邮件

```bash
python3 send_email.py send \
  --to recipient@example.com \
  --subject "带附件的邮件" \
  --body "请查看附件" \
  --attachments "/path/to/file1.pdf" "/path/to/file2.png"
```

#### 抄送和密送

```bash
python3 send_email.py send \
  --to recipient@example.com \
  --cc cc1@example.com cc2@example.com \
  --bcc bcc@example.com \
  --subject "多人邮件" \
  --body "邮件正文"
```

#### 自动检测 Markdown + 内嵌图片（最强推荐）⭐⭐⭐

**功能：** 自动检测 Markdown 格式，自动提取并内嵌图片，无需手动指定！

```bash
python3 send_email.py send \
  --to recipient@example.com \
  --subject "Markdown 邮件（自动检测图片）" \
  --body "# 标题\n\n![图片说明](/path/to/image.png)\n\n这是正文内容"
```

**工作流程：**
1. 脚本自动检测 Markdown 格式
2. 自动提取 Markdown 中的图片路径（支持 `![alt](path)` 语法）
3. 自动将 Markdown 转换为 HTML
4. 自动将图片转换为 CID 引用（`src="cid:image"`）
5. 图片直接显示在邮件正文中

**示例：发送包含多张图片的 Markdown**

```bash
python3 send_email.py send \
  --to recipient@example.com \
  --subject "产品报告" \
  --body "$(cat report.md)"
```

其中 `report.md` 内容：

```markdown
# 产品更新报告

## 新功能展示

这是第一个功能截图：

![功能1](/path/to/screenshot1.png)

这是第二个功能截图：

![功能2](/path/to/screenshot2.png)

## 总结

如有问题，请联系我们。
```

**结果：** 收件人会收到一封格式美观的 HTML 邮件，图片直接显示在正文中！

---

#### 手动指定内嵌图片

**功能：** 图片直接显示在邮件正文中，不是链接。使用 CID（Content-ID）技术，兼容所有主流邮件客户端。

```bash
python3 send_email.py send \
  --to recipient@example.com \
  --subject "带内嵌图片的邮件" \
  --html \
  --body "<h1>标题</h1><p>正文内容</p><img src='/path/to/image.png'>" \
  --inline-images "/path/to/image.png"
```

**工作原理：**
1. 脚本会自动将 HTML 中的图片路径替换为 CID 引用（`src="cid:filename"`）
2. 图片作为内嵌资源添加到邮件中
3. 邮件客户端会直接显示图片，不需要点击链接

**多张图片示例：**

```bash
python3 send_email.py send \
  --to recipient@example.com \
  --subject "产品截图" \
  --html \
  --body "<h1>产品展示</h1><img src='/path/to/screenshot1.png'><br><img src='/path/to/screenshot2.png'>" \
  --inline-images "/path/to/screenshot1.png" "/path/to/screenshot2.png"
```

**重要提示：**
- `--inline-images` 必须配合 `--html` 参数使用（如未指定，会自动启用）
- 图片路径必须与 HTML 中的 `src` 属性完全一致
- 支持 PNG、JPG、JPEG、GIF、WebP 格式
- CID 会自动使用文件名（去掉扩展名），例如 `image.png` → `cid:image`

---

## 参数说明

### 发送命令 (`send`)

| 参数 | 说明 | 必填 |
|------|------|------|
| `--to` | 收件人邮箱 | ✅ |
| `--to-name` | 收件人名称 | ❌ |
| `--subject` | 邮件主题 | ✅ |
| `--body` | 邮件正文 | ✅ |
| `--html` | 使用 HTML 格式 | ❌ |
| `--template` | 使用指定模板渲染邮件（模板文件名） | ❌ |
| `--title` | 邮件标题（模板中使用，默认："邮件摘要"） | ❌ |
| `--attachments` | 附件路径（可多个） | ❌ |
| `--inline-images` | 内嵌图片路径（可多个，仅 HTML 模式） | ❌ |
| `--cc` | 抄送邮箱（可多个） | ❌ |
| `--bcc` | 密送邮箱（可多个） | ❌ |

### 发件人邮箱管理命令 (`username`)

| 参数 | 说明 |
|------|------|
| `--save` | 保存发件人邮箱到 keyring（会提示输入） |
| `--delete` | 删除保存的发件人邮箱 |

### 密码管理命令 (`password`)

| 参数 | 说明 |
|------|------|
| `--save` | 保存密码到 keyring（会提示输入） |
| `--delete` | 删除保存的密码 |

---

## 配置文件

配置文件保存在：`~/.send_email_config.json`

示例配置：
```json
{
  "smtp": {
    "host": "smtp.gd.chinamobile.com",
    "port": 465,
    "use_tls": false
  },
  "sender": {
    "name": "Your Name"
  }
}
```

**注意：** 发件人邮箱通过 `username --save` 命令存储在 keyring 中，不在配置文件中。

---

## 完整示例

### 示例 1: 发送 Markdown 邮件（自动检测并内嵌图片）⭐

创建一个 Markdown 文件 `newsletter.md`：

```markdown
# 今日新闻摘要

## 科技头条

AI 技术持续突破，以下是最新进展：

![AI 演示](/path/to/ai-demo.png)

## 产品更新

新功能界面展示：

![新功能](/path/to/new-feature.png)

---

如需了解更多，请访问我们的官网。
```

发送邮件（超级简单，无需指定任何图片参数！）：

```bash
python3 send_email.py send \
  --to recipient@example.com \
  --subject "今日新闻摘要" \
  --body "$(cat newsletter.md)"
```

**结果：** 脚本会自动：
1. 检测到 Markdown 格式
2. 提取 2 张图片路径
3. 转换为 HTML 并替换图片为 CID 引用
4. 内嵌图片到邮件中
5. 发送格式美观的 HTML 邮件

---

### 示例 2: 发送带内嵌图片的 HTML 邮件（手动指定）

假设你有两张产品截图：

```bash
cd ~/clawd/skills/send-email/scripts

# 准备 HTML 内容
cat > email_content.html << 'EOF'
<h1>产品更新通知</h1>
<p>大家好！</p>
<p>这是我们最新的产品截图：</p>
<img src="/Users/clark/Pictures/screenshot1.png" style="max-width: 600px; border-radius: 8px;">
<p>第二个功能展示：</p>
<img src="/Users/clark/Pictures/screenshot2.png" style="max-width: 600px; border-radius: 8px;">
<p>如有问题，请随时联系我们！</p>
<p>Best regards,<br>产品团队</p>
EOF

# 发送邮件
python3 send_email.py send \
  --to recipient@example.com \
  --subject "产品更新 - 新功能截图" \
  --html \
  --body "$(cat email_content.html)" \
  --inline-images "/Users/clark/Pictures/screenshot1.png" "/Users/clark/Pictures/screenshot2.png"
```

**结果：** 收件人打开邮件后，图片会直接显示在邮件正文中，不需要点击链接。

---

### 示例 3: 手动指定内嵌图片（HTML 模式）

假设你有现成的 HTML 内容：

```bash
python3 send_email.py send \
  --to recipient@example.com \
  --subject "产品截图" \
  --html \
  --body "<h1>产品展示</h1><img src='/path/to/image.png'>" \
  --inline-images "/path/to/image.png"
```

**何时使用手动指定：**
- 已有现成的 HTML 内容
- 不想使用 Markdown 转换
- 需要精确控制 CID 引用

---

### 示例 4: 结合 X 推文技能（自动工作流）⚡

假设你已经使用 `crawl-from-x` 和 `translate` 技能抓取并翻译了 X 推文，结果保存在 `posts_zh.md`。

现在发送邮件（一键搞定！）：

```bash
python3 send_email.py send \
  --to your-email@example.com \
  --subject "今日 X 推文摘要" \
  --body "$(cat /path/to/posts_zh.md)"
```

**完整工作流：**

```bash
# 步骤 1: 抓取 X 推文
crawl-from-x 抓取

# 步骤 2: 翻译为中文
使用 translate 技能翻译最新的文件

# 步骤 3: 发送邮件（自动检测 Markdown + 图片）
python3 send_email.py send \
  --to your-email@example.com \
  --subject "今日 X 推文摘要" \
  --body "$(cat $CLAWD/skills/crawl-from-x/results/*_zh.md)"
```

**自动化脚本：**

创建 `send-x-news.sh`：

```bash
#!/bin/bash
cd ~/clawd/skills/crawl-from-x/scripts
python3 craw_hot.py crawl

LATEST_MD=$(ls -t ~/clawd/skills/crawl-from-x/results/*.md | head -1)
python3 ~/clawd/skills/send-email/scripts/send_email.py send \
  --to your-email@example.com \
  --subject "$(date +'%Y-%m-%d') X 推文摘要" \
  --body "$(cat $LATEST_MD)"
```

添加到 cron：

```bash
crontab -e
# 添加：每天早上 8:00 执行
0 8 * * * ~/clawd/skills/send-email/scripts/send-x-news.sh
```

---

## 模板功能

### 使用模板渲染邮件

使用 `--template` 参数可以让邮件内容使用指定的模板进行渲染，提供更美观的视觉效果。

```bash
python3 send_email.py send \
  --to recipient@example.com \
  --subject "今日 X 推文摘要" \
  --body "$(cat posts_zh.md)" \
  --template default \
  --title "X 帖子摘要"
```

**参数说明：**
- `--template`：模板文件名（不含 .html 扩展名）
  - 默认模板：`default`（仿照 x.com 样式）
  - 模板位置：`templates/` 目录
- `--title`：邮件标题（模板中使用，默认："邮件摘要"）

### 默认模板（default）

send-email 技能内置了一个名为 `default` 的默认模板，具有以下特点：

- **设计风格**：现代、简约、商务、大气
- **视觉参考**：仿照 x.com 网页样式
- **布局**：卡片式布局，圆角边框
- **配色**：
  - 背景：白色（#ffffff）
  - 主要文字：深色（#0f1419）
  - 次要文字：灰色（#536471）
  - 链接：蓝色（#1d9bf0）
  - 边框：浅灰色（#eff3f4）
- **响应式**：适配移动端和桌面端
- **支持内容**：文字、图片、链接

**模板变量：**
- `{{title}}`：邮件标题（通过 `--title` 参数设置）
- `{{subtitle}}`：副标题（自动生成时间戳）
- `{{content}}`：邮件正文内容

### 自定义模板

如果默认模板不满足需求，可以创建自定义模板：

1. 在 `templates/` 目录下创建新的 HTML 文件
2. 使用 `{{title}}`、`{{subtitle}}`、`{{content}}` 作为变量占位符
3. 使用时指定模板名称：

```bash
python3 send_email.py send \
  --to recipient@example.com \
  --subject "每周报告" \
  --body "$(cat report.md)" \
  --template my-template
```

**模板示例：** `templates/default.html`

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{{title}}</title>
    <style>
        /* 自定义样式 */
        body { font-family: Arial, sans-serif; }
        .container { max-width: 600px; margin: 0 auto; }
        /* ... */
    </style>
</head>
<body>
    <div class="container">
        <h1>{{title}}</h1>
        <p class="subtitle">{{subtitle}}</p>
        <div class="content">
            {{content}}
        </div>
    </div>
</body>
</html>
```

### 模板 + Markdown 自动检测

模板功能与 Markdown 自动检测完全兼容：

```bash
# 检测 Markdown → 转换为 HTML → 应用模板 → 发送
python3 send_email.py send \
  --to recipient@example.com \
  --subject "X 推文摘要" \
  --body "$(cat posts_zh.md)" \
  --template default
```

**处理流程：**
1. 检测 Markdown 格式
2. 提取并内嵌图片
3. 转换为 HTML
4. 应用模板
5. 发送邮件

### 模板目录结构

```
send-email/
├── scripts/
│   └── send_email.py
└── templates/
    ├── default.html       # 默认模板（仿照 x.com）
    ├── my-template.html   # 自定义模板 1
    └── weekly.html       # 自定义模板 2
```

---

## 使用建议

1. **密钥管理（强制）：** 首次使用前必须运行 `python send_email.py username --save` 和 `python send_email.py password --save` 分别保存发件人邮箱和密码。这些信息会安全存储在 keyring 中，不会暴露在命令行或上下文中。

2. **不要传递密钥：** 发送邮件时**不要**使用 `--email` 或 `--password` 参数，这些信息会自动从 keyring 读取。这是为了保护密钥安全。

3. **中国移动邮箱：** 默认配置为 `smtp.gd.chinamobile.com:465`（SSL），默认发件人邮箱为 `user@gd.chinamobile.com`。

4. **Markdown 自动检测（推荐）：**
   - 脚本会自动检测 Markdown 格式（标题、粗体、列表、图片等）
   - 自动提取 Markdown 中的图片并内嵌到邮件中
   - 无需手动指定 `--inline-images` 或 `--html` 参数
   - 如果不想自动转换，使用 `--html` 参数强制指定为纯 HTML 模式

5. **内嵌图片：**
   - 支持 Markdown 语法：`![alt](path/to/image.png)`
   - 支持 HTML 语法：`<img src="path/to/image.png">`
   - 图片会自动转换为 CID 引用，直接显示在邮件正文中
   - 建议压缩图片大小（每张 < 500KB），避免邮件过大被拒收
   - CID 使用文件名（去掉扩展名），例如 `myphoto.png` → `cid:myphoto`

6. **图片路径：**
   - 使用绝对路径（推荐）
   - 确保图片文件存在且可读
   - 跳过 `http://` 和 `https://` 开头的图片链接（外链）

7. **附件路径：** 使用绝对路径或相对于执行目录的路径

8. **测试：** 首次使用时，建议先发送测试邮件给自己

9. **keyring 备用方案：** 如果 keyring 不可用，密钥会保存在 `~/.send_email_password` 和 `~/.send_email_username`（base64 编码），文件权限为 600。注意这不是加密，仅避免明文存储。

## 安全流程

```
1. 首次配置（中国移动邮箱）：
   - python send_email.py smtp --host smtp.gd.chinamobile.com --port 465 --no-tls
   - python send_email.py sender --name "Your Name"
   - python send_email.py username --save --email your-email@gd.chinamobile.com
   - python send_email.py password --save  ← 输入密码

2. 后续发送：
   - python send_email.py send --to to@example.com --subject "..." --body "..."
     邮箱和密码自动从 keyring 读取
```

---

## 技术说明

### Markdown 自动检测

脚本会检测以下 Markdown 语法：
- 标题：`# 标题`
- 粗体：`**粗体**`
- 代码块：` ``` `
- 列表：`- 列表项` 或 `1. 列表项`
- 链接：`[文本](url)`
- **图片：`![alt](path)` ⭐**

检测到以上任一语法，会自动转换为 HTML 格式。

### 图片自动提取

支持两种语法：

**Markdown 语法：**
```
![图片说明](/path/to/image.png)
```

**HTML 语法：**
```html
<img src="/path/to/image.png">
```

脚本会：
1. 自动提取所有图片路径
2. 跳过 `http://` 和 `https://` 开头的链接
3. 将本地图片路径转换为 CID 引用
4. 内嵌到邮件中

### CID 工作原理

1. 图片作为 MIME part 添加到邮件
2. 每张图片分配 Content-ID（例如 `cid:myimage`）
3. HTML 中使用 `<img src="cid:myimage">` 引用
4. 邮件客户端解析并直接显示图片

### 支持的图片格式

- PNG
- JPG / JPEG
- GIF
- WebP

### 依赖项

- **必须：** Python 3.7+
- **推荐：** `keyring`（密钥管理）
- **推荐：** `markdown`（Markdown 自动转换）

安装依赖：

```bash
pip install keyring markdown
```

### 邮件大小限制

- 大多数邮件服务器限制：10-25 MB
- 建议：每张图片 < 500KB
- 建议：总邮件大小 < 5 MB

如果邮件过大，可能被拒收或放入垃圾邮件。
