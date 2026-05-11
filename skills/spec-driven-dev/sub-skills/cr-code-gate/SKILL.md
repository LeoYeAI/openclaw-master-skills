---
name: cr-code-gate
description: 【Code Review 子 Agent · 门控二】对 git diff 逐项执行代码质量门控检查（运行时异常、性能瓶颈、安全漏洞、权限缺失、破坏性变更等 10 项），按 LOGAF h/m/l 分级输出，h 级清零后方可进入门控三。由 spec-driven-dev 的 code_review 阶段自动调用。
user-invocable: false
metadata: {"openclaw": {"emoji": "🔬", "requires": {"bins": ["git"]}, "calledBy": ["spec-driven-dev"]}}
---

# cr-code-gate

Code Review 流水线的**第二道门控**：代码质量静态门控子 Agent。
由 `spec-driven-dev` 的 `code_review` 阶段在 `cr-commit-check` 通过后调用，
对 diff 进行结构性问题扫描，参照 Sentry 工程实践的必检项分类。

---

## 调用契约

### 输入（由 Orchestrator 注入上下文）

| 字段 | 类型 | 说明 |
|------|------|------|
| `us_id` | string | 用户故事 ID |
| `iter_id` | string | 当前迭代 ID |
| `git_diff` | string | `git diff main...HEAD` 的完整输出 |
| `iter_summary_path` | string | `requirements/{us_id}/docs/iteration_summary/current_iter.md` 路径，用于核查架构变更审批记录 |
| `coding_standards_path` | string | `auxiliary/coding_standards.md` 路径 |

Orchestrator 调用示例（OpenCode Sub-Agent 格式）：
```
invoke_skill: cr-code-gate
with:
  us_id: "US042"
  iter_id: "iter_003"
  git_diff: "<diff output>"
  iter_summary_path: "requirements/US042/docs/iteration_summary/current_iter.md"
  coding_standards_path: "auxiliary/coding_standards.md"
```

### 输出（写回 Orchestrator）

```json
{
  "agent": "cr-code-gate",
  "verdict": "PASS | WARN | FAIL",
  "h_count": 0,
  "m_count": 0,
  "l_count": 0,
  "findings": [
    {
      "id": "GK-01",
      "logaf": "h",
      "result": "PASS | FAIL | WARN",
      "file": "src/foo.py:42",
      "description": "…",
      "suggestion": "…"
    }
  ]
}
```

---

## 执行协议

### Step 0 — 发出启动检查点
```
[AGENT:cr-code-gate] START  us_id={us_id}  iter_id={iter_id}
```

### Step 1 — 读取上下文

1. 解析 `git_diff`，提取所有变更文件和具体行变更。
2. 读取 `current_iter.md`，检索是否有架构/Schema 变更的 senior 确认记录（供 GK-08 使用）。
3. 读取 `coding_standards.md`，获取项目命名与规范约定（供 GK-10 使用）。

### Step 2 — 逐项执行门控检查

对 diff 中每一个变更文件/代码块执行以下 10 项检查：

---

## 门控检查项

### `h` 级（任意一项命中 → 整体 FAIL）

#### GK-01 · 运行时异常
- 数组 / 切片越界访问（未校验长度）
- 空指针 / nil 解引用（未做 nil check）
- 未捕获的异常 / error 被静默丢弃（`_ = err`）
- goroutine / async 中 panic 未 recover

#### GK-02 · 性能瓶颈
- 无界循环内嵌套 DB 查询（N+1 问题）
- 算法复杂度 O(n²) 或更高且 n 无上界
- 大对象（> 1 MB）在请求热路径中进行 JSON 序列化/反序列化
- 无缓存的重复计算

#### GK-03 · 安全漏洞
- SQL / NoSQL 注入（字符串拼接构造查询）
- XSS（未转义的用户输入直接输出到 HTML）
- 硬编码密钥、Token、密码（含正则 `(api_key|secret|password|token)\s*=\s*['"][^'"]+['"]`）
- 不安全的反序列化（`pickle.loads`、`eval`、`exec` 处理用户数据）
- 路径遍历（`../` 未过滤的文件路径拼接）

#### GK-04 · 权限 / 访问控制缺失
- 新增 API 端点缺少鉴权装饰器 / 中间件
- 删除操作未校验资源所有权
- 管理员接口对普通用户可访问

#### GK-05 · API 破坏性变更
- 公开 REST / GraphQL 字段被重命名或删除
- 必填参数的默认值被移除
- 响应 Schema 中字段类型变更（如 `string` → `int`）

#### GK-06 · 意外行为修改
- 变更触及了本次迭代 scope 之外的既有逻辑
- 全局常量 / 配置默认值被修改
- 共享工具函数语义变更（影响其他调用方）

---

### `m` 级（命中 → WARN，记录后可继续）

#### GK-07 · 测试覆盖不足
- 新增的业务逻辑没有对应的单元测试
- 测试用例中存在 if/for 分支，可能掩盖测试本身的缺陷
- 缺少模拟权限场景的测试（正向 + 越权拒绝）

#### GK-08 · 重大架构 / Schema 变更未审批
- 引入新的外部框架或库依赖
- 数据库字段新增 / 删除 / 类型变更
- JSON Schema 或 protobuf 定义变更
- 以上任意情形在 `current_iter.md` 中无 senior 确认记录

---

### `l` 级（命中 → INFO，可选修复）

#### GK-09 · 多余或遗留代码
- 已注释掉的代码块（连续 3 行以上）
- 调试语句（`print()`、`console.log()`、`fmt.Println()`、`System.out.println()`）
- 标注日期超过当前迭代开始日期 30 天的 `TODO` / `FIXME`

#### GK-10 · 命名与规范一致性
- 变量 / 函数 / 文件 / 指标命名与 `coding_standards.md` 约定不一致
- 文件名大小写与现有同目录文件风格不符
- logger / metric 命名不遵循项目既有前缀约定

---

### Step 3 — 输出逐条发现

每条发现使用统一格式：
```
[{logaf}] {GK-ID} | 文件: {path}:{line} | 问题: {描述} | 建议: {可操作方案}
```

示例：
```
[h] GK-03 | 文件: src/auth/handler.py:47 | 问题: API Key 硬编码在源文件 | 建议: 改为 os.getenv("API_KEY")，在 .env.example 添加占位符
[h] GK-01 | 文件: src/db/query.py:83    | 问题: result[0] 访问前未检查列表长度 | 建议: 改为 result[0] if result else None
[m] GK-07 | 文件: tests/test_auth.py     | 问题: 缺少越权访问的拒绝场景测试 | 建议: 新增 test_access_denied_for_non_owner
[l] GK-09 | 文件: src/utils/parser.py:12 | 问题: 注释掉的旧代码块 | 建议: 删除或移至 CHANGELOG
```

### Step 4 — 返回结构化结果

```json
{
  "agent": "cr-code-gate",
  "verdict": "FAIL",
  "h_count": 2,
  "m_count": 1,
  "l_count": 1,
  "findings": [
    {
      "id": "GK-03", "logaf": "h", "result": "FAIL",
      "file": "src/auth/handler.py:47",
      "description": "API Key 硬编码",
      "suggestion": "改为 os.getenv('API_KEY')"
    }
  ]
}
```

### Step 5 — 发出结束检查点

```
[AGENT:cr-code-gate] DONE  verdict=PASS|WARN|FAIL  h={N}  m={N}  l={N}
```

---

## 裁决规则

| 裁决 | 条件 | Orchestrator 行为 |
|------|------|-----------------|
| **PASS** | 所有 `h` 级检查项均无命中（`m`/`l` 可有） | 继续调用 `cr-logaf-review` |
| **WARN** | 无 `h` 级命中，存在 `m`/`l` 级发现 | 继续调用 `cr-logaf-review`，`m`/`l` 发现传入汇总报告 |
| **FAIL** | 任意 `h` 级检查项命中 | 终止流水线，阻塞 `release`，返回修复清单 |

---

## 禁止行为

- 禁止对 `h` 级问题降级为 `m` 或 `l`，即使代码作者附有解释。
- 禁止对 diff 之外的既有代码发起检查（只扫描本次变更行）。
- 禁止在 `git_diff` 为空时静默通过，应报告 `GK-06 INFO（本次无代码变更）`。
- 禁止自动修改任何源文件，只输出建议和修复指引。
