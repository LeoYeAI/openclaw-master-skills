# ClawHub 发布指南

**日期：** 2026-03-06
**项目：** FA Advisor (Financial Analyst)
**状态：** 准备发布

---

## 🔍 当前问题

### 遇到的错误
1. **"SKILL.md required"** - clawhub 无法找到 SKILL.md 文件
2. **"financial-analyst" slug 已被占用** - 需要使用不同的 slug

### 已验证信息
- ✅ SKILL.md 文件存在且格式正确
- ✅ ClawHub CLI 已安装 (v0.7.0)
- ✅ 已登录为 ZhenStaff
- ✅ 所有文件准备就绪

---

## 📋 发布前检查清单

### 1. SKILL.md 格式验证

你的 SKILL.md frontmatter：
```yaml
---
name: FA Advisor
description: Professional Financial Advisor (FA) skill for primary market financing - replaces traditional investment advisory services with AI-powered project assessment, pitch deck generation, valuation analysis, and investor matching
version: 0.1.0
homepage: https://github.com/ZhenRobotics/openclaw-financial-analyst
metadata: {"clawdbot":{"emoji":"💼","tags":["finance","investment","fundraising","valuation","pitch-deck","venture-capital","startup","fa","advisor"],"requires":{"bins":["python3"],"env":[],"config":[]},"install":["pip install -e ."],"os":["darwin","linux","win32"]}}
---
```

**状态：** ✅ 格式正确

### 2. 必需文件

```bash
✅ SKILL.md (18,331 bytes, 649 lines)
✅ README.md (15,859 bytes)
✅ .clawignore (764 bytes)
✅ LICENSE (MIT)
✅ pyproject.toml
✅ requirements.txt
✅ fa_advisor/ (Python 包)
```

### 3. 可用的 Slug 选项

由于 "financial-analyst" 已被占用，可使用：
- `fa-advisor` ⭐ 推荐
- `zhen-fa-advisor`
- `financial-advisory`
- `startup-fa-advisor`

---

## 🚀 方法1：使用 ClawHub CLI（命令行）

### 选项 A：基本发布命令

```bash
cd /home/justin/openclaw-financial-analyst

# 尝试发布
clawhub publish . \
  --slug fa-advisor \
  --version 0.1.0 \
  --name "FA Advisor" \
  --tags finance,investment,fundraising,valuation,startup \
  --changelog "Initial release: Complete FA implementation with 6 core modules"
```

### 选项 B：使用绝对路径

```bash
clawhub publish /home/justin/openclaw-financial-analyst \
  --slug fa-advisor \
  --version 0.1.0 \
  --name "FA Advisor" \
  --tags finance,investment,fundraising,valuation
```

### 选项 C：最简化命令

```bash
cd /home/justin/openclaw-financial-analyst
clawhub publish . --slug fa-advisor --version 0.1.0
```

---

## 🌐 方法2：通过 Web 界面发布

如果 CLI 持续出现问题，可以使用 ClawHub 网页界面：

### 步骤：

1. **访问 ClawHub 网站**
   ```
   打开浏览器访问 ClawHub 网站
   使用 ZhenStaff 账号登录
   ```

2. **创建新 Skill**
   - 点击 "Publish Skill" 或 "Create New Skill"
   - 选择从 GitHub 导入

3. **连接 GitHub 仓库**
   ```
   仓库 URL: https://github.com/ZhenRobotics/openclaw-financial-analyst
   分支: main
   ```

4. **填写 Skill 信息**
   ```
   Slug: fa-advisor
   Name: FA Advisor
   Version: 0.1.0
   Tags: finance, investment, fundraising, valuation, startup
   ```

5. **验证并发布**
   - ClawHub 会自动读取 SKILL.md
   - 检查格式
   - 点击 "Publish"

---

## 🔧 方法3：手动打包上传

### 创建发布包：

```bash
cd /home/justin/openclaw-financial-analyst

# 创建发布目录
mkdir -p /tmp/fa-advisor-release
rsync -av --exclude='__pycache__' --exclude='*.pyc' --exclude='.git' \
  ./ /tmp/fa-advisor-release/

# 打包
cd /tmp
tar -czf fa-advisor-0.1.0.tar.gz fa-advisor-release/

echo "✅ Release package created: /tmp/fa-advisor-0.1.0.tar.gz"
ls -lh /tmp/fa-advisor-0.1.0.tar.gz
```

然后通过 ClawHub 网页上传这个压缩包。

---

## 🐛 故障排除

### 问题 1: "SKILL.md required"

**可能原因：**
- ClawHub working directory 配置问题
- 文件权限问题
- 路径解析问题

**解决方案：**
```bash
# 1. 确保在正确的目录
cd /home/justin/openclaw-financial-analyst
pwd

# 2. 检查文件存在
ls -la SKILL.md

# 3. 尝试使用绝对路径
clawhub publish $(pwd) --slug fa-advisor --version 0.1.0

# 4. 检查 clawhub 配置
echo $CLAWHUB_WORKDIR
clawhub --help
```

### 问题 2: "Rate limit exceeded"

**解决方案：**
```bash
# 等待几分钟后重试
sleep 60
clawhub publish . --slug fa-advisor --version 0.1.0
```

### 问题 3: "Timeout"

**解决方案：**
```bash
# 检查网络连接
ping clawhub.com

# 或使用 GitHub 导入方式（通过 web 界面）
```

### 问题 4: Slug 已被占用

**解决方案：**
```bash
# 使用不同的 slug
clawhub search "fa" --limit 10  # 检查哪些 slug 可用

# 尝试：
# - fa-advisor
# - zhen-financial-analyst
# - startup-fa
```

---

## 📝 发布信息总结

### 基本信息
```yaml
Slug: fa-advisor (推荐) 或 zhen-fa-advisor
Name: FA Advisor
Version: 0.1.0
Description: Professional Financial Advisor (FA) skill for primary market financing
Homepage: https://github.com/ZhenRobotics/openclaw-financial-analyst
```

### Tags（标签）
```
finance, investment, fundraising, valuation, pitch-deck,
venture-capital, startup, fa, advisor
```

### Changelog（更新日志）
```
Initial release: Complete FA Advisor implementation with 6 core modules

Features:
- Project assessment with 5-dimension scoring
- Multi-method valuation (Scorecard, Berkus, Risk Factor, Comparables)
- Pitch deck generation (12-slide structure)
- Business plan generation
- Investor matching with intelligent algorithm
- Investment analysis with DD checklist
- Advanced PDF processing (parsing, OCR, report generation)

Technical:
- Python 3.10+ implementation
- 4,471 lines of code across 21 files
- All tests passing (6/6 modules)
- Complete documentation (2,482 lines)
```

### 系统要求
```yaml
requires:
  bins: [python3]
  env: []
  config: []
install: [pip install -e .]
os: [darwin, linux, win32]
```

---

## 🎯 推荐的发布流程

### 最简单的方法（推荐）：

1. **确认登录状态**
   ```bash
   clawhub whoami
   # 应该显示: ZhenStaff
   ```

2. **执行发布命令**
   ```bash
   cd /home/justin/openclaw-financial-analyst

   clawhub publish . \
     --slug fa-advisor \
     --version 0.1.0 \
     --name "FA Advisor" \
     --changelog "Initial release with complete Python implementation"
   ```

3. **如果 CLI 失败，使用 Web 界面**
   - 访问 ClawHub 网站
   - 选择 "Import from GitHub"
   - 输入: `https://github.com/ZhenRobotics/openclaw-financial-analyst`
   - 填写 slug: `fa-advisor`
   - 点击发布

4. **验证发布**
   ```bash
   # 搜索你的 skill
   clawhub search "fa advisor"

   # 或
   clawhub inspect fa-advisor
   ```

---

## 📞 需要帮助？

如果遇到问题：

1. **检查 ClawHub 状态**
   ```bash
   clawhub whoami  # 确认登录
   clawhub explore --limit 1  # 测试连接
   ```

2. **查看详细日志**
   ```bash
   clawhub publish . --slug fa-advisor --version 0.1.0 2>&1 | tee publish.log
   ```

3. **联系 ClawHub 支持**
   - 提供 publish.log
   - 说明你的 slug (fa-advisor)
   - 提供 GitHub 仓库链接

---

## ✅ 发布后验证

发布成功后，运行：

```bash
# 1. 搜索你的 skill
clawhub search "fa advisor"

# 2. 查看详情
clawhub inspect fa-advisor

# 3. 测试安装
cd /tmp
clawhub install fa-advisor
```

---

**创建日期：** 2026-03-06
**更新日期：** 2026-03-06
**版本：** 1.0
