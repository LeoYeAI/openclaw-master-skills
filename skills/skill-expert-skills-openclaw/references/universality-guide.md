# Universality Guide (通用性指南)

Skills 必须跨项目可复用。本指南帮助识别和修正非通用内容。

## 核心原则

**通用性测试**：如果一段内容只有在了解特定项目背景后才能理解，它就是非通用的。

## 通用性自检清单

在写/修改 Skill 内容时，对每段文字进行以下检查：

- [ ] 没有具体项目名/仓库名
- [ ] 没有具体文件路径 (如 `/src/services/xxx.ts`)
- [ ] 没有具体字段名/变量名 (如 `userId`, `${keywords}`)
- [ ] 没有具体错误信息 (如 "入参显示不正确")
- [ ] 没有具体数据值 (如 "organic cotton bed sheets")
- [ ] 没有项目特定术语 (如业务领域专有名词)
- [ ] 示例是合成的，可适用于任何项目
- [ ] 不了解项目的人也能理解

## Red Flags 完整列表

### 项目标识类

| 非通用 | 通用替代 |
|--------|----------|
| "接口自动化脚本项目" | 省略或 "the project" |
| "leadong.com" | "example.com" 或省略 |
| "/backend/app/services/" | "service layer" 或省略 |
| "api_test.db" | "database" 或省略 |

### 功能/模块名类

| 非通用 | 通用替代 |
|--------|----------|
| "Excel 批量导入" | "file import" |
| "关键词搜索" | "search functionality" |
| "用户登录/注册" | "authentication flow" |
| "订单管理" | "CRUD operations" |

### 字段/数据类

| 非通用 | 通用替代 |
|--------|----------|
| `${keywords}` | "template syntax like ${...}" |
| `userId`, `orderId` | "identifier field" |
| "organic cotton bed sheets" | "sample value" 或 "user input" |
| `{"code": -1, "message": "操作成功"}` | "response with business status code" |

### 错误信息类

| 非通用 | 通用替代 |
|--------|----------|
| "入参显示不正确" | "input data display issue" |
| "显示成功但实际失败" | "status mismatch between display and reality" |
| "Excel 列名格式错误" | "column name format issue" |

### 技术栈类

| 非通用 | 通用替代 |
|--------|----------|
| "React + FastAPI" | "frontend + backend" |
| "使用 Zustand 管理状态" | "state management" |
| "pandas 解析 Excel" | "file parsing" |

## 抽象化步骤详解

### Step 1: 识别根因模式

从具体 bug/需求中提取通用问题模式：

```
项目案例:
  "导入 Excel 时，列名 ${keywords} 被原样存储和显示，
   应该去掉 ${} 包装只保留 keywords"

抽象问题:
  "用户输入格式与系统预期不符时，需要在解析阶段规范化"

通用模式:
  "User input format mismatch → Normalize at parse time"
```

### Step 2: 剥离项目细节

移除所有具体名称，保留结构：

```
Before:
  "修改 excel_parser.py 的 parse_excel_file 函数，
   添加 normalize_column_name() 处理 ${xxx} 格式"

After:
  "Add normalization logic in parser/importer code
   to handle unexpected input format variants"
```

### Step 3: 合成通用示例

用占位符替代具体值：

```
Before:
  | 假设 | 实际 |
  | Excel 列名是 keywords | 用户用了 ${keywords} |

After:
  | Assumed | Reality |
  | Input follows format X | User used wrapper syntax like ${X} |
```

### Step 4: 验证可迁移性

问自己：

- 一个完全不同领域的项目能用这个描述吗？
- 不了解原项目的开发者能理解要点吗？
- 这个模式在 3 年后的新项目中还适用吗？

## 完整抽象示例

### 原始 Bug 描述 (项目特定)

```
Bug: 导入Excel批量执行时，执行结果只展示了输出内容，
没有展示接口入参，并且显示成功了但实际是失败的。

根因: excel_parser.py 直接使用 ${keywords} 作为列名存储，
request_executor.py 只检查 HTTP 状态码不检查响应体的 code 字段。
```

### 抽象后 (通用)

```
Pattern: External data handling issues

Issue A: Input data not normalized before storage/display
- Parser stores raw input format instead of normalized form
- Solution: Add normalization step at parse time

Issue B: Success/failure status mismatch
- Only checks HTTP status, ignores business status in response body
- Solution: Parse response body for business status codes
```

### 转化为 Skill 内容

```markdown
## Common Assumption Failures

| Assumed | Reality | Better Approach |
|---------|---------|-----------------|
| User input follows expected format | Users may use wrapper syntax, special chars | Add input normalization at parse time |
| HTTP 200 means success | API may return 200 with business error in body | Check response body for business status codes |
```

## 常见错误及修正

### 错误 1: 直接复制项目案例

❌ 不好：
```markdown
如本次 Excel 导入 bug 所示，用户可能用 ${keywords} 作为列名...
```

✅ 好：
```markdown
Users may use unexpected input formats (wrapper syntax, special characters)...
```

### 错误 2: 保留项目术语

❌ 不好：
```markdown
在 request_params 中存储 row_data 而不是 query params...
```

✅ 好：
```markdown
Store original input data, not just derived/processed values...
```

### 错误 3: 过于具体的技术方案

❌ 不好：
```markdown
添加 normalize_column_name() 函数用正则表达式处理 ${xxx} 格式...
```

✅ 好：
```markdown
Add normalization logic in parser to handle format variants...
```

## Definition of Done

优化完成前，确认：

- [ ] 所有内容通过上述自检清单
- [ ] 没有 Red Flags 列表中的模式
- [ ] 项目案例已完全抽象化
- [ ] 不了解项目的人能理解所有内容
- [ ] `universal_validate.py` 通过

