# 发布 Python FA Advisor 到 ClawHub 指南

**项目类型：** Python (不是TypeScript!)
**状态：** ✅ Production Ready - 可以立即发布

---

## 🎯 发布前准备清单

### 1. ✅ 必需文件检查

运行以下命令检查：

```bash
# 进入项目目录
cd /home/justin/ai-fa

# 检查必需文件
ls -la SKILL.md          # ✅ 存在
ls -la README.md         # ✅ 存在
ls -la LICENSE           # ✅ 存在
ls -la pyproject.toml    # ✅ 存在
ls -la .clawignore       # ✅ 存在

# 检查Python代码
ls -la fa_advisor/       # ✅ 存在
ls -la example_python.py # ✅ 存在
ls -la test_complete.py  # ✅ 存在
```

### 2. ⚠️ 更新占位符信息

**重要：** 在发布前必须更新以下占位符：

#### A. 更新 pyproject.toml

```bash
# 打开编辑
nano pyproject.toml

# 需要更新的行：
# Line 24: authors = [{name = "Your Name", email = "your.email@example.com"}]
# Line 79-82: GitHub URLs
```

更新为实际信息：
```toml
authors = [
    {name = "你的名字", email = "your.email@example.com"},
]

[project.urls]
Homepage = "https://github.com/你的用户名/ai-fa"
Documentation = "https://github.com/你的用户名/ai-fa/blob/main/README.md"
Repository = "https://github.com/你的用户名/ai-fa"
Issues = "https://github.com/你的用户名/ai-fa/issues"
```

#### B. 更新 SKILL.md

```bash
# 打开编辑
nano SKILL.md

# Line 8: homepage: https://github.com/your-org/openclaw-fa-advisor
```

更新为：
```yaml
homepage: https://github.com/你的用户名/ai-fa
```

### 3. ✅ 运行测试验证

```bash
# 确保所有测试通过
python3 test_complete.py

# 预期输出：
# ✅ 测试 1/6: 项目评估 - PASSED
# ✅ 测试 2/6: 估值分析 - PASSED
# ✅ 测试 3/6: Pitch Deck生成 - PASSED
# ✅ 测试 4/6: 商业计划书生成 - PASSED
# ✅ 测试 5/6: 投资人匹配 - PASSED
# ✅ 测试 6/6: 投资分析 - PASSED
# 🎊 所有测试通过！
```

### 4. 📦 创建发布包

由于ClawHub主要接受文本文件，我们需要确保只上传源代码：

```bash
# 创建发布目录
mkdir -p /tmp/fa-advisor-release
cd /home/justin/ai-fa

# 复制必需文件（排除构建产物和缓存）
rsync -av --exclude-from='.clawignore' \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='.git' \
  . /tmp/fa-advisor-release/

# 查看将要上传的文件
cd /tmp/fa-advisor-release
find . -type f | grep -v '.git' | sort
```

---

## 🚀 方式 1: CLI 命令发布（推荐）⭐

### 前置要求
```bash
# 检查 clawhub CLI 是否已安装
which clawhub

# 如果未安装，安装 OpenClaw CLI
npm install -g @openclaw/cli
# 或
pnpm add -g @openclaw/cli
```

### 发布步骤

```bash
# 1. 登录 ClawHub
clawhub login

# 2. 进入项目目录
cd /home/justin/ai-fa

# 3. 发布 (Python版本)
clawhub publish . \
  --slug fa-advisor-python \
  --name "FA Advisor (Python)" \
  --version 1.0.0 \
  --tags finance,investment,fundraising,valuation,startup,pdf,python,ai \
  --changelog "Initial production release with full PDF processing capabilities"

# 注意：使用 fa-advisor-python 作为slug以区分TypeScript版本
```

### 发布参数说明

| 参数 | 值 | 说明 |
|------|-----|-----|
| --slug | fa-advisor-python | URL标识符（建议加python后缀） |
| --name | FA Advisor (Python) | 显示名称 |
| --version | 1.0.0 | 语义化版本（因为完全实现，直接1.0.0） |
| --tags | finance,investment... | 搜索标签（逗号分隔） |
| --changelog | 说明文字 | 版本更新说明 |

---

## 🌐 方式 2: Web 上传界面

适合不熟悉命令行的用户：

### Step 1: 准备上传包

```bash
cd /home/justin/ai-fa

# 创建ZIP包（自动排除.clawignore中的文件）
zip -r fa-advisor-python-v1.0.0.zip . \
  -x "*/__pycache__/*" \
  -x "*.pyc" \
  -x "*/.git/*" \
  -x "*/dist/*" \
  -x "*/build/*" \
  -x "*/output/*" \
  -x "*.log"

# 查看包大小
du -h fa-advisor-python-v1.0.0.zip
```

### Step 2: 上传

1. 访问 **https://clawhub.ai/upload**
2. 拖放 `fa-advisor-python-v1.0.0.zip` 到上传区域
3. 填写表单：
   - **Name:** FA Advisor (Python)
   - **Slug:** fa-advisor-python
   - **Version:** 1.0.0
   - **Description:** Professional FA skill with PDF processing
   - **Tags:** finance, investment, fundraising, valuation, pdf, python
4. 点击 "Submit" 提交

---

## 🔧 方式 3: GitHub Pull Request

适合开源贡献：

### Step 1: Fork ClawHub 仓库

```bash
# 在GitHub上 Fork: https://github.com/openclaw/clawhub
# 然后克隆你的 fork
git clone https://github.com/你的用户名/clawhub.git
cd clawhub
```

### Step 2: 添加你的技能

```bash
# 创建技能目录
mkdir -p skills/fa-advisor-python

# 复制Python项目文件（排除不需要的）
rsync -av --exclude-from=/home/justin/ai-fa/.clawignore \
  /home/justin/ai-fa/ skills/fa-advisor-python/

# 确保SKILL.md存在
ls skills/fa-advisor-python/SKILL.md
```

### Step 3: 提交 Pull Request

```bash
# 添加文件
git add skills/fa-advisor-python

# 提交
git commit -m "feat: add FA Advisor (Python) skill with PDF processing

- Full Python implementation with 6 core modules
- PDF parsing, OCR, financial statement extraction
- Project assessment, valuation, pitch deck generation
- Investor matching, investment analysis
- Production ready with 100% test coverage"

# 推送
git push origin main

# 在GitHub上创建Pull Request
```

---

## 📋 发布前最终检查

运行这个脚本进行最终检查：

```bash
# 创建检查脚本
cat > /tmp/check_publish.sh << 'SCRIPT'
#!/bin/bash
echo "========================================="
echo "ClawHub 发布前检查"
echo "========================================="

cd /home/justin/ai-fa

echo ""
echo "1. 检查必需文件..."
files=("SKILL.md" "README.md" "LICENSE" "pyproject.toml" ".clawignore")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file 缺失！"
    fi
done

echo ""
echo "2. 检查SKILL.md格式..."
if grep -q "^---$" SKILL.md && grep -q "^name:" SKILL.md; then
    echo "  ✅ SKILL.md格式正确"
else
    echo "  ❌ SKILL.md格式错误"
fi

echo ""
echo "3. 检查占位符..."
if grep -q "your-org" SKILL.md pyproject.toml 2>/dev/null; then
    echo "  ⚠️  发现占位符，需要更新！"
    grep -n "your-org" SKILL.md pyproject.toml 2>/dev/null
else
    echo "  ✅ 没有占位符"
fi

echo ""
echo "4. 检查Python代码..."
if [ -d "fa_advisor" ] && [ -f "fa_advisor/__init__.py" ]; then
    echo "  ✅ Python包结构正确"
    echo "  文件数: $(find fa_advisor -name "*.py" | wc -l) 个Python文件"
else
    echo "  ❌ Python包结构错误"
fi

echo ""
echo "5. 检查测试..."
if [ -f "test_complete.py" ]; then
    echo "  ✅ 测试文件存在"
    echo "  运行: python3 test_complete.py 验证"
else
    echo "  ⚠️  缺少测试文件"
fi

echo ""
echo "6. 估算包大小..."
size=$(du -sh . | cut -f1)
echo "  当前目录大小: $size"
echo "  (注意：上传时会排除 .clawignore 中的文件)"

echo ""
echo "========================================="
echo "检查完成！"
echo "========================================="
SCRIPT

chmod +x /tmp/check_publish.sh
/tmp/check_publish.sh
```

---

## 🎯 发布后验证

### 1. 搜索验证

```bash
# 搜索你的技能
clawhub search fa-advisor-python

# 查看详情
clawhub show fa-advisor-python

# 查看特定版本
clawhub show fa-advisor-python@1.0.0
```

### 2. 安装测试

```bash
# 在新目录测试安装
cd /tmp
openclaw skill add fa-advisor-python

# 或指定版本
openclaw skill add fa-advisor-python@1.0.0

# 验证安装
openclaw skills list
```

### 3. 功能测试

```bash
# 通过OpenClaw测试技能
openclaw agent --message "Help me assess my Series A startup"
```

---

## 📝 版本管理

### 更新版本

```bash
# 更新pyproject.toml中的version
nano pyproject.toml
# version = "1.0.0" -> "1.0.1"

# 或使用脚本更新
python3 -c "
import re
with open('pyproject.toml', 'r') as f:
    content = f.read()
content = re.sub(r'version = \"(.+?)\"', 'version = \"1.0.1\"', content, count=1)
with open('pyproject.toml', 'w') as f:
    f.write(content)
"

# 重新发布
clawhub publish . \
  --slug fa-advisor-python \
  --version 1.0.1 \
  --changelog "Bug fixes and improvements"
```

### 语义化版本

- **1.0.0 → 1.0.1** (PATCH): Bug修复
- **1.0.1 → 1.1.0** (MINOR): 新功能（向后兼容）
- **1.1.0 → 2.0.0** (MAJOR): 破坏性变更

---

## ⚠️ 重要注意事项

### Python项目特殊要求

1. **系统依赖：** 
   - PDF处理需要系统级依赖（tesseract, ghostscript, poppler）
   - 在SKILL.md中已说明安装方法

2. **大文件：**
   - 不要上传大型数据文件或PDF样本
   - 使用`.clawignore`排除

3. **虚拟环境：**
   - 不要上传venv/或.venv/
   - 已在`.clawignore`中排除

### ClawHub限制

- ✅ 文本文件（.py, .md, .txt, .json等）
- ❌ 二进制文件（图片、PDF、视频）
- ❌ node_modules/或虚拟环境
- ⚠️  包大小建议 < 10MB（源代码）

---

## 🆘 常见问题

### Q: GitHub账户年龄要求？
**A:** ClawHub要求GitHub账户至少1周以上才能发布。

### Q: Python vs TypeScript版本冲突？
**A:** 使用不同的slug：
- TypeScript版本: `fa-advisor`
- Python版本: `fa-advisor-python`

### Q: 如何标注这是Python版本？
**A:** 
1. Name中标注: "FA Advisor (Python)"
2. Tags中包含: `python`
3. Description中说明PDF处理优势

### Q: 用户如何安装Python依赖？
**A:** 在SKILL.md中已包含安装说明，用户需要：
```bash
pip install openclaw-skill-fa-advisor
brew install tesseract ghostscript poppler  # macOS
```

### Q: 发布失败怎么办？
**A:** 检查：
1. 是否登录: `clawhub whoami`
2. 包大小是否过大
3. SKILL.md格式是否正确
4. 是否有占位符未更新

---

## 📚 资源链接

- **ClawHub官网:** https://clawhub.ai/
- **OpenClaw文档:** https://docs.openclaw.ai/
- **Python包索引:** https://pypi.org/project/openclaw-skill-fa-advisor/
- **GitHub仓库:** https://github.com/你的用户名/ai-fa

---

## ✅ 快速发布流程（TL;DR）

```bash
# 1. 更新占位符（重要！）
nano pyproject.toml  # 更新 authors 和 URLs
nano SKILL.md        # 更新 homepage

# 2. 运行测试
python3 test_complete.py

# 3. 登录并发布
clawhub login
clawhub publish . \
  --slug fa-advisor-python \
  --name "FA Advisor (Python)" \
  --version 1.0.0 \
  --tags finance,investment,fundraising,valuation,startup,pdf,python,ai

# 4. 验证
clawhub show fa-advisor-python
```

---

🎉 **准备好了吗？开始发布吧！** 

如果遇到问题，查看 https://docs.openclaw.ai/ 或在社区寻求帮助。
