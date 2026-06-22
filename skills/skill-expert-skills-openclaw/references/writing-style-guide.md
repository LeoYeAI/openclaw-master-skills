# Skill 写作风格指南

本文档定义 Skill 内容的写作规范，确保一致性和可读性。

---

## 核心原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **祈使句优先** | 正文使用动词开头的指令 | "Run the script" 而非 "You should run" |
| **第三人称 description** | description 使用 "This skill..." | "This skill should be used when..." |
| **客观语言** | 描述事实，不评价读者 | "Configure X" 而非 "You need to configure" |
| **简洁明确** | 每句话一个动作 | 避免长复合句 |

---

## 1. Frontmatter Description 规范

### 必须使用第三人称

```yaml
# ✅ 正确: 第三人称
description: |
  This skill should be used when the user asks to "create a hook",
  "add validation", or mentions hook events.

# ❌ 错误: 第二人称
description: |
  Use this skill when you want to create hooks.

# ❌ 错误: 祈使句
description: |
  Load this skill when working with hooks.
```

### 必须包含触发短语

```yaml
# ✅ 正确: 具体触发短语
description: |
  This skill should be used when the user asks to "convert PDF",
  "extract text from PDF", "merge PDF files", or mentions .pdf files.

# ❌ 错误: 模糊描述
description: |
  This skill provides PDF functionality.
```

### 推荐结构

```yaml
description: |
  [一句话说明做什么]

  Use when:
  - "trigger phrase 1"
  - "trigger phrase 2"
  - [场景描述]

  Not for: [边界说明]

  Outputs: [输出描述]
```

---

## 2. 正文写作规范

### 使用祈使句 (Imperative Form)

祈使句 = 动词开头的指令，省略主语

```markdown
# ✅ 正确: 祈使句

Run the validation script.
Configure the API endpoint.
Verify the output format.
Create a new configuration file.
```

```markdown
# ❌ 错误: 第二人称

You should run the validation script.
You need to configure the API endpoint.
You can verify the output format.
You must create a new configuration file.
```

```markdown
# ❌ 错误: 第一人称

I will run the validation script.
We need to configure the API endpoint.
Let me verify the output format.
```

### 祈使句转换表

| 原句 (第二人称) | 修正后 (祈使句) |
|-----------------|-----------------|
| You should start by... | Start by... |
| You need to validate... | Validate... |
| You can use grep to... | Use grep to... |
| You must ensure that... | Ensure that... |
| If you want to X, you should... | To X, ... |
| You will need to... | ... |
| Make sure you... | Ensure... / Verify... |

### 条件句写法

```markdown
# ✅ 正确: 客观条件句

To convert a single file, run:
If the validation fails, check the log file.
When processing large files, increase the timeout.

# ❌ 错误: 第二人称条件句

If you want to convert a single file, you should run:
If you see validation errors, you need to check the log.
When you process large files, you should increase the timeout.
```

---

## 3. 标题与章节规范

### 标题层级

```markdown
# Skill Name (H1 - 仅一个)

## Major Section (H2 - 主要章节)

### Subsection (H3 - 子章节)

#### Detail (H4 - 很少使用)
```

### 推荐章节结构

```markdown
# Skill Name

## Overview / Quick Start
[快速开始]

## Decision Tree
[决策树，如果需要]

## Instructions / Workflow
[主要流程]

## Output Contract
[输出规范]

## Troubleshooting
[故障排除]

## References
[参考文档导航]
```

---

## 4. 代码块规范

### 始终指定语言

```markdown
# ✅ 正确
```python
def process():
    pass
```

# ❌ 错误 (无语言标记)
```
def process():
    pass
```
```

### 命令块使用 bash

```markdown
# ✅ 正确
```bash
python scripts/validate.py input.json
```

# ❌ 错误 (使用 shell 或 sh)
```shell
python scripts/validate.py input.json
```
```

### 输出示例使用 text 或特定格式

```markdown
# 纯文本输出
```text
Validation passed: 5 files checked
```

# JSON 输出
```json
{
  "status": "success",
  "count": 5
}
```
```

---

## 5. 表格规范

### 对齐方式

```markdown
# ✅ 正确: 左对齐 (默认)
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |

# ✅ 正确: 居中对齐 (用于数字/状态)
| Task | Status | Score |
|------|:------:|:-----:|
| Validation | ✅ | 95 |
```

### 常见表格类型

**命令参考表**:
```markdown
| Command | Description | Example |
|---------|-------------|---------|
| `--input` | Input file path | `--input data.csv` |
| `--output` | Output directory | `--output results/` |
```

**错误处理表**:
```markdown
| Error | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError` | Missing input | Check file path |
| `ValidationError` | Invalid format | See format guide |
```

**决策表**:
```markdown
| Condition | Action |
|-----------|--------|
| Has OpenAPI spec | Run automated analysis |
| Only documentation | Manual review |
```

---

## 6. 列表规范

### 步骤列表使用数字

```markdown
# ✅ 正确: 有序步骤
1. Prepare input files
2. Run validation
3. Review output

# ❌ 错误: 用点号表示步骤
- Prepare input files
- Run validation
- Review output
```

### 无序项目使用连字符

```markdown
# ✅ 正确: 无序列表
- Feature A
- Feature B
- Feature C

# ❌ 错误: 用星号
* Feature A
* Feature B
```

### 检查清单

```markdown
# 任务清单
- [ ] Task to complete
- [x] Completed task
```

---

## 7. 链接与引用规范

### 内部链接 (references/)

```markdown
# ✅ 正确: 相对路径
See `references/checklist.md` for details.
For patterns, consult `references/patterns.md`.

# ❌ 错误: 绝对路径
See `/home/.../project/.claude/skills/my-skill/references/checklist.md`
```

### 外部链接

```markdown
# ✅ 正确: 描述性链接文本
See the [OpenAPI Specification](https://spec.openapis.org/) for details.

# ❌ 错误: 裸链接
See https://spec.openapis.org/ for details.

# ❌ 错误: "点击这里"
[Click here](https://spec.openapis.org/) for details.
```

---

## 8. 特殊标记规范

### 🔴 特殊字符使用规则 (重要)

在 SKILL.md 中使用反引号包裹某些特殊字符时，可能被 Claude Code 错误解析为 Bash 命令，导致执行失败。

**禁止的写法**：

```markdown
# ❌ 错误 - 单独的特殊字符在反引号中
| any type, ignored Promise, exclamation mark, ts-ignore | **P1+** |
Use dollar sign for variable interpolation.
The hash symbol indicates a comment.
```

**正确的写法**：

```markdown
# ✅ 正确 - 使用描述性文本
| `any`, ignored Promise, non-null assertion, `@ts-ignore` | **P1+** |
Use the dollar sign ($) for variable interpolation.
The hash symbol (#) indicates a comment.

# ✅ 正确 - 在完整表达式中使用
The `value!` syntax (non-null assertion)...
Use `$HOME` for home directory.
```

**特殊字符替代表**：

| 字符 | 禁止写法 | 推荐写法 |
|------|----------|----------|
| `!` | `` `!` `` | `non-null assertion` 或 `(!)` |
| `$` | `` `$` `` | `dollar sign` 或 `($)` |
| `#` | `` `#` `` | `hash` 或 `(#)` |
| `` ` `` | 单独反引号 | `backtick` |
| `\|` | `` `\|` `` | `pipe` 或 `(\|)` |

### 强调

```markdown
# 加粗: 重要术语/关键概念
**SKILL.md** is required.
The **decision tree** guides...

# 斜体: 首次引入的术语
A *skill* is a modular package...

# 代码: 文件名/命令/变量
Run `validate.py` with `--verbose` flag.
```

### 警告与提示

```markdown
# 警告
> ⚠️ **Warning**: This operation is destructive.

# 提示
> 💡 **Tip**: Use `--verbose` for detailed output.

# 重要
> ⚠️ **Important**: Complete this step before proceeding.

# 注意
> 📝 **Note**: This applies only to version 2.0+.
```

---

## 9. 常见错误对照表

### Description 错误

| 错误类型 | 错误示例 | 正确示例 |
|----------|----------|----------|
| 第二人称 | "Use this when you want to..." | "This skill should be used when the user asks to..." |
| 缺少触发词 | "Provides PDF functionality" | "...when user mentions 'convert PDF', 'extract text'" |
| 过于模糊 | "Helps with data" | "Process CSV/JSON files, convert formats, validate schemas" |

### 正文错误

| 错误类型 | 错误示例 | 正确示例 |
|----------|----------|----------|
| 第二人称 | "You should run..." | "Run..." |
| 被动语态过多 | "The file should be validated" | "Validate the file" |
| 冗余词 | "In order to validate..." | "To validate..." |
| 模糊指令 | "Process the data appropriately" | "Convert CSV to JSON using scripts/convert.py" |

---

## 10. 快速检查清单

### Description 检查

- [ ] 以 "This skill..." 开头
- [ ] 包含 3-5 个具体触发短语
- [ ] 包含 "Use when:" 部分
- [ ] 包含 "Outputs:" 说明
- [ ] 无第二人称 ("you", "your")

### 正文检查

- [ ] 指令使用祈使句 (动词开头)
- [ ] 无 "You should/need/must"
- [ ] 代码块有语言标记
- [ ] 步骤使用数字列表
- [ ] 无绝对路径
- [ ] 链接使用描述性文本

### 结构检查

- [ ] 只有一个 H1 标题
- [ ] 章节层级清晰 (H2 → H3)
- [ ] 包含 Quick Start / Overview
- [ ] 包含 Output Contract
- [ ] 详细内容在 references/

---

## 自动检查命令

```bash
# 检查第二人称使用
grep -rn "You should\|You need\|You must\|You can\|you will" .claude/skills/my-skill/

# 检查绝对路径 (推荐使用 universal_validate.py)
python scripts/universal_validate.py .claude/skills/my-skill/

# 检查裸链接
grep -rn "http[s]*://" .claude/skills/my-skill/ | grep -v "\[.*\](http"

# 检查无语言标记的代码块
grep -n "^\`\`\`$" .claude/skills/my-skill/SKILL.md
```
