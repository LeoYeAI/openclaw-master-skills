# Skill 故障排除指南

本文档提供 Skill 开发和使用过程中的常见问题诊断与解决方案。

---

## 问题分类决策树

```
┌─────────────────────────────────────────────────────────────────────┐
│ Skill 故障排除决策树                                                  │
├─────────────────────────────────────────────────────────────────────┤
│  Skill 不被发现?   → 见 [发现问题](#1-skill-不被发现)                 │
│  Skill 不触发?     → 见 [触发问题](#2-skill-不触发)                   │
│  Skill 行为异常?   → 见 [行为问题](#3-skill-行为异常)                 │
│  验证脚本报错?     → 见 [验证问题](#4-验证脚本报错)                   │
│  跨项目使用失败?   → 见 [通用性问题](#5-跨项目使用失败)               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. Skill 不被发现

### 症状
- Claude 不知道 Skill 存在
- `/skills` 命令不显示你的 Skill

### 诊断命令

```bash
# 检查 Skill 目录是否存在
ls $HOME/.claude/skills/skill-name/SKILL.md   # 个人 Skill
ls .claude/skills/skill-name/SKILL.md         # 项目 Skill

# 检查目录结构
tree .claude/skills/skill-name/
```

### 常见原因与解决方案

| 原因 | 诊断方法 | 解决方案 |
|------|----------|----------|
| SKILL.md 不存在 | `ls SKILL.md` 返回空 | 创建 SKILL.md 文件 |
| 文件名大小写错误 | `ls skill.md` 找到文件 | 重命名为 `SKILL.md` (全大写) |
| 目录位置错误 | 不在 `.claude/skills/` 下 | 移动到正确位置 |
| 编码错误 | 文件含非 UTF-8 字符 | 保存为 UTF-8 (可带 BOM) |

### 快速修复

```bash
# 确保目录存在
mkdir -p .claude/skills/my-skill

# 创建最小 SKILL.md
cat > .claude/skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: Brief description of what this skill does and when to use it.
---

# My Skill

Instructions for Claude here.
EOF
```

---

## 2. Skill 不触发

### 症状
- Skill 被发现但不响应用户请求
- 其他 Skill 优先被选中
- 用户问了相关问题但 Claude 没用这个 Skill

### 诊断步骤

1. **检查 description 覆盖度**
   ```bash
   # 查看 description 内容
   head -20 .claude/skills/my-skill/SKILL.md
   ```

2. **对比用户说法与 description**
   - 用户说："帮我转换这个 PDF"
   - description 里有没有 "PDF"、"转换"、"convert" 等关键词？

### 常见原因与解决方案

| 原因 | 示例 | 解决方案 |
|------|------|----------|
| description 太模糊 | `description: Helps with files` | 添加具体触发词和场景 |
| 缺少用户常用说法 | 没有 "帮我"、"我想" 等 | 收集 3-5 条真实用户说法 |
| 缺少文件类型 | 没有 ".pdf"、".xlsx" | 添加具体文件扩展名 |
| 缺少 "Use when" | 只描述做什么，不说何时用 | 添加触发场景说明 |
| 与其他 Skill 冲突 | 多个 Skill 描述重叠 | 细化各自边界，使用 "Not for:" |

### description 优化模板

```yaml
description: |
  [做什么]: Convert PDF files to editable Word documents.

  Use when:
  - Converting .pdf files to .docx format
  - Extracting text from scanned PDFs (OCR)
  - Batch processing multiple PDF files

  Not for: Creating PDFs, merging PDFs (use pdf-merger skill).

  Outputs: Word documents (.docx) in output/ directory.
```

### 触发词检查清单

- [ ] 包含文件扩展名 (.pdf, .xlsx, .json)
- [ ] 包含动作动词 (convert, analyze, generate, create)
- [ ] 包含用户常见说法 ("帮我", "我想", "如何")
- [ ] 包含具体场景 ("when reviewing code", "when processing data")
- [ ] 设定边界 ("Not for:")

---

## 3. Skill 行为异常

### 3.1 特殊字符导致解析错误

### 症状
- Skill 加载时报错：`/usr/bin/bash: line 1: ...: command not found`
- Claude Code 将 SKILL.md 中的内容误解析为 Bash 命令
- 表格或代码块中的特殊字符导致执行失败

### 常见原因

在 SKILL.md 的 Markdown 表格或正文中，使用反引号包裹某些特殊字符时，可能被 Claude Code 错误解析：

| 问题字符 | 错误写法 | 正确写法 |
|----------|----------|----------|
| 感叹号 | `` `!` `` | `non-null assertion` 或 `exclamation mark` |
| 美元符号 | `` `$` `` | `dollar sign` 或 `variable prefix` |
| 井号 | `` `#` `` | `hash` 或 `comment marker` |
| 反引号 | `` ` `` | `backtick` 或用单引号 `'` |
| 管道符 | `` `\|` `` | `pipe` 或 `vertical bar` |

### 解决方案

1. **避免在反引号中使用单个特殊字符**
   ```markdown
   # ❌ 错误
   | any type, ignored Promise, exclamation mark, ts-ignore | **P1+** |

   # ✅ 正确
   | any type, ignored Promise, non-null assertion, ts-ignore | **P1+** |
   ```

2. **使用描述性文本替代符号**
   ```markdown
   # ❌ 错误
   Use exclamation mark for non-null assertion

   # ✅ 正确
   Use the non-null assertion operator (!) for...
   ```

3. **在代码块中使用完整上下文**
   ```markdown
   # ❌ 错误 - 单独的特殊字符
   The `!` operator...

   # ✅ 正确 - 完整表达式
   The `value!` syntax (non-null assertion)...
   ```

### 诊断命令

```bash
# 检查可能有问题的特殊字符
grep -n '`[!$#|]`' .claude/skills/my-skill/SKILL.md
grep -n '`[!$#|]`' .claude/skills/my-skill/references/*.md
```

---

### 3.2 其他行为异常

### 症状
- Skill 触发了但输出不符合预期
- Claude 没有遵循 Skill 中的指令
- 输出格式与预期不同

### 诊断步骤

1. **检查指令清晰度**
   - 指令是否有歧义？
   - 步骤是否明确？
   - 是否有决策分支？

2. **检查输出契约**
   - 有没有定义预期输出格式？
   - 有没有示例？

### 常见原因与解决方案

| 原因 | 诊断信号 | 解决方案 |
|------|----------|----------|
| 指令模糊 | Claude 做了但结果不对 | 添加具体步骤和示例 |
| 缺少决策逻辑 | 不同场景被同样处理 | 添加决策树/条件分支 |
| 无输出契约 | 输出格式不一致 | 定义标准输出格式模板 |
| 依赖未安装 | 脚本执行失败 | 列出依赖并检查安装 |
| 脚本路径错误 | `FileNotFoundError` | 使用相对路径或检查路径 |

### 调试技巧

```bash
# 启用调试模式
claude --debug

# 检查 Skill 加载日志
claude --verbose
```

---

## 4. 验证脚本报错

### quick_validate.py 错误

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `Missing dependency: PyYAML` | PyYAML 未安装 | `pip install -r scripts/requirements.txt` |
| `No YAML frontmatter found` | 文件不以 `---` 开头 | 确保第一行是 `---` |
| `Invalid YAML in frontmatter` | YAML 语法错误 | 检查缩进(用空格)、引号匹配 |
| `Name should be hyphen-case` | name 含大写/下划线 | 改为 `my-skill-name` 格式 |
| `Directory name must match` | 目录名与 name 不一致 | 使目录名与 frontmatter name 相同 |
| `Description cannot contain < or >` | description 含尖括号 | 删除或转义尖括号 |
| `SKILL.md is too long` | 超过 800 行 | 拆分内容到 references/ |

### universal_validate.py 错误

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `Absolute path detected` | 含 `C:\...` 或 `/Users/...` | 使用相对路径或通用占位符 |
| `Project-specific reference` | 含项目特定名称 | 使用通用示例替代 |
| `Hardcoded username` | 含 `/Users/john/...` | 使用 `~` 或通用路径 |

### YAML 常见语法错误

```yaml
# ❌ 错误: 使用 Tab 缩进
name:	my-skill

# ✅ 正确: 使用空格缩进
name: my-skill

# ❌ 错误: 冒号后无空格
name:my-skill

# ✅ 正确: 冒号后有空格
name: my-skill

# ❌ 错误: 多行字符串无 |
description: This is a
multi-line description

# ✅ 正确: 使用 | 表示多行
description: |
  This is a
  multi-line description

# ❌ 错误: 含特殊字符未加引号
description: Use <tag> for markup

# ✅ 正确: 避免尖括号或使用引号
description: "Use tags for markup"
```

---

## 5. 跨项目使用失败

### 症状
- Skill 在原项目工作正常
- 复制到其他项目后失败

### 诊断命令

```bash
# 检查是否有项目特定路径 (使用 universal_validate.py 更可靠)
python scripts/universal_validate.py .claude/skills/my-skill/

# 检查是否有项目特定名称
grep -rn "my-project-name\|my-repo" .claude/skills/my-skill/
```

### 常见原因与解决方案

| 原因 | 示例 | 解决方案 |
|------|------|----------|
| 绝对路径 | `C:\Users\...\project` | 使用相对路径 `./` |
| 硬编码项目名 | `my-company-repo` | 使用通用名称 `<project>` |
| 环境变量依赖 | `$MY_PROJECT_KEY` | 文档化必需环境变量 |
| 特定依赖版本 | `requires nodejs 18.x` | 记录版本要求 |

### 通用性检查清单

- [ ] 无绝对路径 (Windows/Mac/Linux)
- [ ] 无项目特定仓库名
- [ ] 无用户名/主目录路径
- [ ] 依赖已文档化
- [ ] 示例使用通用数据

---

## 6. 性能问题

### Skill 加载慢

| 原因 | 诊断 | 解决方案 |
|------|------|----------|
| SKILL.md 太长 | 检查行数 > 500 | 拆分到 references/ |
| references 太多 | > 10 个文件 | 合并相关文件 |
| 大型 assets | 图片/视频 > 10MB | 压缩或外部链接 |

### 脚本执行慢

```bash
# 测量脚本执行时间
time python scripts/my-script.py

# 分析性能瓶颈
python -m cProfile scripts/my-script.py
```

---

## 7. 调试命令速查

```bash
# 验证 Skill 结构
python .claude/skills/skill-expert-skills/scripts/quick_validate.py .claude/skills/my-skill

# 验证通用性
python .claude/skills/skill-expert-skills/scripts/universal_validate.py .claude/skills/my-skill

# 查看 SKILL.md 行数
wc -l .claude/skills/my-skill/SKILL.md

# 检查 frontmatter
head -20 .claude/skills/my-skill/SKILL.md

# 搜索项目特定内容
grep -rn "TODO\|FIXME\|XXX" .claude/skills/my-skill/

# 检查文件编码
file .claude/skills/my-skill/SKILL.md
```

---

## 8. 获取帮助

如果以上都无法解决问题：

1. **运行完整验证**
   ```bash
   python scripts/quick_validate.py .claude/skills/my-skill --verbose
   ```

2. **检查示例**
   - 对比 `references/examples.md` 中的工作示例

3. **查看知识库**
   - 阅读 `references/skills-knowledge-base.md`

4. **社区资源**
   - Claude Code GitHub Issues
   - Claude Code Discord
