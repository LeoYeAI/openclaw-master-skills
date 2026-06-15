# Send Email 模板

## 目录结构

```
templates/
├── README.md          # 本文件
└── default.html       # 默认模板（仿照 x.com 样式）
```

## 使用方法

### 基本用法

```bash
python3 send_email.py send \
  --to recipient@example.com \
  --subject "邮件主题" \
  --body "邮件正文内容" \
  --template default \
  --title "邮件标题"
```

### 与 Markdown 结合使用

```bash
# 自动检测 Markdown → 转换为 HTML → 应用模板
python3 send_email.py send \
  --to recipient@example.com \
  --subject "X 推文摘要" \
  --body "$(cat posts_zh.md)" \
  --template default
```

## 默认模板（default.html）

### 设计特点

- **风格**：现代、简约、商务、大气
- **参考**：仿照 x.com 网页样式
- **布局**：卡片式设计，圆角边框
- **响应式**：适配移动端和桌面端

### 配色方案

| 元素 | 颜色 | 用途 |
|------|------|------|
| 背景色 | #ffffff | 整体背景 |
| 主要文字 | #0f1419 | 标题、正文 |
| 次要文字 | #536471 | 副标题、元数据 |
| 链接颜色 | #1d9bf0 | 链接、按钮 |
| 边框颜色 | #eff3f4 | 卡片边框、分隔线 |

### 模板变量

- `{{title}}`：邮件标题（通过 `--title` 参数设置）
- `{{subtitle}}`：副标题（自动生成时间戳）
- `{{content}}`：邮件正文内容

## 自定义模板

### 创建新模板

1. 在 `templates/` 目录下创建新的 HTML 文件
2. 使用 `{{title}}`、`{{subtitle}}`、`{{content}}` 作为变量占位符
3. 编写自定义样式

### 模板示例

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{{title}}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
        }
        h1 {
            color: #333;
            font-size: 24px;
        }
        .subtitle {
            color: #666;
            font-size: 14px;
            margin-bottom: 20px;
        }
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

### 使用自定义模板

```bash
python3 send_email.py send \
  --to recipient@example.com \
  --subject "每周报告" \
  --body "$(cat report.md)" \
  --template my-template \
  --title "每周工作总结"
```

## 注意事项

1. **图片支持**：模板自动支持内嵌图片（使用 Markdown 格式或 HTML）
2. **CSS 兼容性**：建议使用基础 CSS，避免使用高级特性（部分邮件客户端不支持）
3. **响应式设计**：建议使用 max-width 限制宽度，确保移动端显示正常
4. **变量替换**：确保模板中包含所有必需的变量（`{{title}}`、`{{subtitle}}`、`{{content}}`）

## 邮件客户端兼容性

### 兼容的客户端

- Gmail
- Outlook（桌面版 + 网页版）
- Apple Mail
- QQ 邮箱
- 163 邮箱
- 大多数现代邮件客户端

### 不支持的客户端

- 纯文本邮件客户端（会显示 HTML 源码）

## 测试建议

发送重要邮件前，建议先发送测试邮件到自己的邮箱，检查：

1. 模板渲染是否正常
2. 图片是否正确显示
3. 链接是否可点击
4. 在不同邮件客户端中的显示效果
