# Workwork - 学术综述撰写与格式化工具

这是一个专门用于学术综述撰写的自动化工具集，提供从格式检查到文档生成的全流程支持。

## 📋 功能概览

### 核心功能模块 (9个)

1. **统一检查器** - 一次性完成所有检查（推荐）
2. **参考文献格式规范检查** - 检查引用标注位置、作者格式、编号连续性
3. **文献管理与筛选** - 识别并删除非核心期刊文献
4. **参考文献编号系统** - 自动重新编号、修复重复编号
5. **文字错别字和语法检查** - 检查常见错别字、语法错误、标点符号
6. **文献格式和引用准确性检查** - 验证文献格式、引用准确性、编号连续性
7. **文档格式规范检查** - 检查文档结构、章节编号、段落格式
8. **Word文档生成器** - 生成标准格式的Word文档
9. **上标引用Word生成器** - 生成带右上标引用的Word文档（推荐）

## 🚀 快速开始

### 🎯 推荐: 使用统一检查（一次性完成所有检查）

```bash
cd scripts
python unified_checker.py ../../your_review.md

# 查看统一报告
cat ../../your_review_unified_report.md
```

### 📝 分步检查（按需使用）

如果需要单独运行某个检查:

```bash
cd scripts

# 1. 检查参考文献格式
python reference_formatter.py ../../your_review.md

# 2. 文字错别字和语法检查
python typo_grammar_checker.py ../../your_review.md

# 3. 文献格式和引用准确性检查
python reference_accuracy_checker.py ../../your_review.md

# 4. 文档格式规范检查
python document_format_checker.py ../../your_review.md
```

### 📊 筛选和修复

```bash
cd scripts

# 5. 筛选文献（可选）
# 先编辑 filter_references.py 中的期刊列表
python filter_references.py

# 6. 修复参考文献编号
python extract_and_fix_references.py

# 7. 生成Word文档（标准格式）
node create_word_doc_v3.js

# 或生成上标格式（推荐）
node create_word_with_superscript.js ../../your_review.md
```

## 📁 目录结构

```
workwork/
├── README.md                       # 本文件
├── example_usage.md               # 使用示例
├── package.json                   # Node.js 依赖
├── scripts/                       # 功能脚本目录
│   ├── unified_checker.py         # 统一检查器 ✅
│   ├── reference_formatter.py     # 参考文献格式检查 ✅
│   ├── typo_grammar_checker.py    # 错别字检查 ✅
│   ├── reference_accuracy_checker.py  # 引用准确性检查 ✅
│   ├── document_format_checker.py # 文档格式检查 ✅
│   ├── filter_references.py       # 文献筛选 ✅
│   ├── extract_and_fix_references.py   # 参考文献编号修复 ✅
│   ├── create_word_doc_v3.js      # Word文档生成 ✅
│   ├── create_word_with_superscript.js # 上标引用Word生成 ✅
│   └── simple_verify.py           # 简单验证 ✅
├── templates/                     # 配置文件目录
│   └── ref_format_default.yml     # 默认格式配置 ✅
├── examples/                      # 示例文件目录（空）
└── reports/                       # 报告示例目录（空）
```

## 💡 使用流程

### ⚠️ 重要提示

**避免重复检查**: 为了提高效率，建议使用**统一检查**功能。

### 🎯 推荐工作流程

1. 撰写综述（Markdown格式）
2. 运行统一检查 `unified_checker.py`
3. 查看统一报告
4. 确认修复
5. 筛选文献（可选）
6. 修复编号
7. 最终验证
8. 生成Word文档（推荐上标格式）

### 📝 分步工作流程

1. 撰写综述（Markdown格式）
2. 依次运行各个检查脚本
3. 查看各个检查报告
4. 确认修复
5. 筛选文献（可选）
6. 修复编号
7. 全面验证
8. 生成Word文档

### 🔄 快速修复流程（小修小补）

如果只是修复了小问题，不需要运行所有检查:
- 只运行受影响的检查脚本
- 生成Word文档

## ✨ 上标引用Word生成器特色功能

`create_word_with_superscript.js` 提供以下增强功能：

- **智能字体处理**: 中文宋体 + 英文/数字/标点 Times New Roman
- **物种拉丁文名自动斜体**: 自动识别并斜体化物种学名
- **字号标准化**: 正文和参考文献均为小四 (12pt)
- **自动生成后打开**: 生成完成后自动打开Word文档
- **上标引用格式**: `[1]`、`[2-3]` 显示为右上标

## 🔧 配置

您可以自定义格式规则:

```yaml
# 编辑 templates/ref_format_default.yml
reference_format:
  citation_style: "superscript"
  position_rules:
    before_punctuation: true
  same_source_format: "[{ref}]"
  author_limit: 3
```

## 📖 详细文档

- **example_usage.md** - 详细的使用示例

## 📝 系统要求

- Python 3.7+
- Node.js 14+
- Python依赖: `pyyaml`（可选）
- Node.js依赖: `docx`

安装Node.js依赖:
```bash
npm install docx
```

## 🎯 特色功能

1. **功能完整** - 涵盖学术综述撰写的全流程
2. **配置灵活** - 支持YAML配置文件
3. **模块化** - 可按需使用各功能
4. **上标引用** - 支持中文学术规范的上标引用格式

## 📄 许可

本工具仅供学习和研究使用。

## 🤝 贡献

欢迎提交问题和改进建议!

## 📅 版本历史

### v2.3.0 (2026-03-19)
- ✅ **增强上标Word生成器** - 智能字体处理、自动斜体化物种名、自动生成后打开
- ✅ **字号标准化** - 正文和参考文献统一使用小四 (12pt)

### v2.2.0 (2026-03-19)
- ✅ **新增上标引用Word生成器** - `create_word_with_superscript.js`
- ✅ **上标引用保留方括号** - `[1]`、`[2-3]` 显示为上标格式

### v2.1.0 (2026-03-19)
- ✅ **新增统一检查功能** - `unified_checker.py` 一次性完成所有检查
- ✅ **优化工作流程** - 提供推荐工作流程和快速修复流程
- ✅ **避免重复检查** - 添加使用说明，防止重复运行相同检查

### v2.0.0 (2026-03-19)
- ✅ 新增文字错别字和语法检查功能
- ✅ 新增文献格式和引用准确性检查功能
- ✅ 新增文档格式规范检查功能

### v1.0.0 (2026-03-19)
- ✅ 实现参考文献格式检查功能
- ✅ 实现文献筛选功能
- ✅ 实现参考文献编号修复
- ✅ 实现Word文档生成
- ✅ 实现质量控制检查

---

**创建时间**: 2026-03-19
**当前版本**: v2.3.0
**状态**: ✅ 完成并可投入使用
