# send-email 技能示例

## 示例列表

1. **Markdown 自动检测测试** - 演示自动检测 Markdown 格式并内嵌图片
2. **内嵌图片测试** - 手动指定 HTML 邮件的图片（旧方式）

---

## 示例 1: Markdown 自动检测（推荐）⭐

### 功能说明

这是最新的推荐方式，脚本会：
- 自动检测 Markdown 格式
- 自动提取 Markdown 中的图片
- 自动转换为 HTML
- 自动内嵌图片到邮件中

**无需任何额外参数！**

### 测试步骤

1. **准备测试图片**

```bash
# 准备两张测试图片
# 例如：~/Pictures/test1.png 和 ~/Pictures/test2.png
```

2. **修改测试文件**

编辑 `markdown-auto-test.md`，将图片路径替换为实际路径：

```markdown
# 原来的占位符
![测试图片 1](/path/to/your/test-image1.png)

# 修改为实际路径
![测试图片 1](/Users/clark/Pictures/test1.png)
```

3. **发送测试邮件**

```bash
cd ~/clawd/skills/send-email/scripts

python3 send_email.py send \
  --to your-email@example.com \
  --subject "Markdown 自动检测测试" \
  --body "$(cat ../examples/markdown-auto-test.md)"
```

### 预期结果

打开收到的邮件，你应该看到：
- ✅ 美观的 HTML 格式
- ✅ 标题、列表、代码块都正确渲染
- ✅ 图片直接显示在邮件正文中（不是链接）
- ✅ 图片快速加载（嵌入在邮件中）

---

## 示例 2: 手动指定内嵌图片（HTML 模式）

### 1. 准备测试图片

将一张测试图片放到任意目录，例如：

```bash
# 使用 macOS 截图工具或准备任意图片
# 保存到: ~/Pictures/test-image.png
```

### 2. 修改 HTML 文件

编辑 `inline-image-test.html`，将图片路径替换为实际路径：

```html
<!-- 原来的占位符 -->
<img src="/path/to/your/test-image.png" ...>

<!-- 修改为实际路径 -->
<img src="/Users/clark/Pictures/test-image.png" ...>
```

### 3. 发送测试邮件

```bash
cd ~/clawd/skills/send-email/scripts

python3 send_email.py send \
  --to your-email@example.com \
  --subject "内嵌图片测试" \
  --html \
  --body "$(cat ../examples/inline-image-test.html)" \
  --inline-images "/Users/clark/Pictures/test-image.png"
```

### 4. 验证结果

打开收到的邮件，检查：
- ✅ 图片直接显示在邮件正文中
- ✅ 不需要点击链接
- ✅ 图片加载快速（嵌入在邮件中）

## 高级用法

### 多张图片

```bash
python3 send_email.py send \
  --to your-email@example.com \
  --subject "多图测试" \
  --html \
  --body "<h1>图片1</h1><img src='/path/to/image1.png'><h1>图片2</h1><img src='/path/to/image2.png'>" \
  --inline-images "/path/to/image1.png" "/path/to/image2.png"
```

### 结合 Markdown

如果你有 Markdown 文档（例如 X 推文翻译结果），可以：

```bash
# 1. 转换 Markdown 为 HTML
pandoc input.md -f markdown -t html -o output.html

# 2. 手动调整图片路径后发送
python3 send_email.py send \
  --to your-email@example.com \
  --subject "Markdown 转邮件" \
  --html \
  --body "$(cat output.html)" \
  --inline-images "/path/to/image1.png" "/path/to/image2.png"
```

## 故障排查

### 图片没有显示

1. **检查路径匹配**：确保 HTML 中的 `src` 路径与 `--inline-images` 参数完全一致
2. **检查文件存在**：确认图片文件存在且可读
3. **检查 HTML 格式**：确保使用了 `--html` 参数

### 图片显示为附件

- 这是因为没有使用 `--inline-images` 参数，使用了 `--attachments` 参数
- 请改用 `--inline-images`

### 邮件太大被拒收

- 压缩图片大小（每张 < 500KB）
- 减少图片数量（建议 < 5 张）
- 使用 WebP 格式（体积更小）

## 支持的图片格式

- PNG
- JPG / JPEG
- GIF
- WebP

## 技术说明

内嵌图片使用 **CID（Content-ID）** 技术：

1. 图片作为 MIME part 添加到邮件中
2. 每张图片分配一个唯一的 Content-ID（例如 `cid:myimage`）
3. HTML 中使用 `<img src="cid:myimage">` 引用
4. 邮件客户端解析并直接显示图片

**优点：**
- ✅ 兼容所有主流邮件客户端
- ✅ 图片显示无需网络请求
- ✅ 隐私性好（图片不托管在外部服务器）

**缺点：**
- ❌ 邮件体积较大
- ❌ 部分客户端会自动下载附件

---

需要帮助？查看主文档：`../SKILL.md`
