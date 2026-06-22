# Skill 实践示例集

本文档提供三个真实世界的完整 Skill 示例，涵盖不同复杂度和应用场景，帮助快速理解 Skill 的最佳实践。

## 使用前建议（复用优先）

- 先确认是否已有现成 Skill 可复用：`skill-discovery-protocol.md`
- 需求太宽先收敛范围：`task-narrowing-framework.md`
- 技术型任务不确定最佳实践：`learn-from-github-protocol.md`

## 目录

- [示例索引](#示例索引)
- [示例 1: 简单工具型 Skill (文件格式转换)](#示例-1-简单工具型-skill-文件格式转换)
- [示例 2: 中等工作流 Skill (代码审查助手)](#示例-2-中等工作流-skill-代码审查助手)
- [示例 3: 复杂知识型 Skill (API 设计审查)](#示例-3-复杂知识型-skill-api-设计审查)
- [对比分析](#对比分析)
- [选择指南](#选择指南)
- [快速启动模板](#快速启动模板)
- [常见问题](#常见问题)
- [后续学习资源](#后续学习资源)

---

## 示例索引

| 示例 | 类型 | 复杂度 | 适用场景 | 核心特点 |
|------|------|--------|----------|----------|
| [示例 1](#示例-1-简单工具型-skill-文件格式转换) | 工具型 | 低 | 单一确定性任务 | 脚本驱动、最小权限 |
| [示例 2](#示例-2-中等工作流-skill-代码审查助手) | 工作流型 | 中 | 多步骤流程 | 决策树、条件分支 |
| [示例 3](#示例-3-复杂知识型-skill-api-设计审查) | 知识密集型 | 高 | 需要专业知识 | 领域专家化、丰富 references |

---

## 示例 1: 简单工具型 Skill (文件格式转换)

### 场景
创建一个将 Markdown 转换为 HTML 的 Skill，使用 Python 脚本处理。

### 完整 SKILL.md

```markdown
---
name: markdown-to-html-converter
description: |
  Convert Markdown files to HTML with customizable templates and styling.

  Use when:
  - Converting .md files to .html for documentation
  - Generating static HTML from Markdown content
  - Batch processing multiple Markdown files
  - Applying custom CSS templates to Markdown

  Outputs: HTML files with optional CSS styling in output/ directory.
allowed-tools: [read, write, execute]
---

# Markdown to HTML Converter

## Quick Start

```bash
# 1. Convert single file
python scripts/convert.py input.md

# 2. Convert with custom template
python scripts/convert.py input.md --template templates/modern.css

# 3. Batch convert directory
python scripts/batch_convert.py docs/ --output dist/
```

## Workflow

1. **Prepare Input**
   - Ensure Markdown files are UTF-8 encoded
   - Place files in source directory

2. **Run Conversion**
   - Single file: `python scripts/convert.py <file.md>`
   - Batch mode: `python scripts/batch_convert.py <directory>`

3. **Verify Output**
   - Check `output/` directory for HTML files
   - Validate HTML with: `python scripts/validate_html.py output/`

## Output Contract

- **File naming**: `input.md` → `output/input.html`
- **Encoding**: UTF-8
- **Validation**: All HTML files pass W3C validation

## Customization

See `references/template-guide.md` for custom CSS templates.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Unicode errors | Ensure source files are UTF-8 |
| Missing images | Use relative paths in Markdown |
| CSS not applied | Check `--template` path is correct |
```

### 目录结构

```
markdown-to-html-converter/
├── SKILL.md
├── scripts/
│   ├── convert.py          # 单文件转换
│   ├── batch_convert.py    # 批量转换
│   ├── validate_html.py    # HTML 验证
│   └── requirements.txt    # 依赖: markdown, beautifulsoup4
├── references/
│   └── template-guide.md   # CSS 模板说明
└── assets/
    └── templates/
        ├── modern.css
        └── classic.css
```

### 关键设计决策

✅ **使用脚本而非纯指令**: 转换逻辑复杂，脚本更可靠
✅ **最小权限**: `allowed-tools: [read, write, execute]`，不需要 grep/glob
✅ **清晰的输出契约**: 明确文件命名、编码、验证标准
✅ **快速开始优先**: Quick Start 在最前面

---

## 示例 2: 中等工作流 Skill (代码审查助手)

### 场景
创建一个帮助进行代码审查的 Skill，包含多个检查点和决策分支。

### 完整 SKILL.md

```markdown
---
name: code-review-assistant
description: |
  Systematic code review workflow with security, performance, and style checks.

  Use when:
  - Reviewing pull requests or code changes
  - Performing pre-commit code quality checks
  - Conducting security audits on code
  - Identifying performance bottlenecks
  - Enforcing coding standards

  Outputs: Structured review report with findings, severity ratings, and recommendations.
allowed-tools: [read, grep, execute]
---

# Code Review Assistant

## Decision Tree

```
┌─────────────────────────────────────────────────────────┐
│ 代码审查决策树                                           │
├─────────────────────────────────────────────────────────┤
│  新代码 (New Code) → 完整审查流程                        │
│  修改代码 (Modified) → 差异审查 + 影响分析               │
│  删除代码 (Deleted) → 依赖检查 + 影响评估                │
└─────────────────────────────────────────────────────────┘
```

**确定审查类型:**

1. **新增功能/文件?**
   → 执行 [完整审查流程](#完整审查流程)

2. **修改现有代码?**
   → 执行 [差异审查流程](#差异审查流程)

3. **删除代码?**
   → 执行 [删除影响评估](#删除影响评估)

## 完整审查流程

### 阶段 1: 自动检查

```bash
# 运行自动检查套件
python scripts/auto_review.py <file_or_directory>
```

检查项:
- [ ] 语法检查 (linter)
- [ ] 安全扫描 (bandit/semgrep)
- [ ] 性能分析 (profiling)
- [ ] 测试覆盖率 (>80%)

### 阶段 2: 人工审查要点

参考 `references/review-checklist.md`:

**2.1 安全性** (严重性: 高)
- 是否存在 SQL 注入风险?
- 敏感数据是否加密?
- 输入验证是否充分?

**2.2 性能** (严重性: 中)
- 是否存在 N+1 查询?
- 循环中是否有重复计算?
- 是否需要缓存优化?

**2.3 可维护性** (严重性: 低)
- 函数是否过长 (>50行)?
- 是否有重复代码?
- 命名是否清晰?

### 阶段 3: 生成报告

```bash
# 生成结构化报告
python scripts/generate_report.py --format markdown --output review-report.md
```

## 差异审查流程

针对修改代码的快速流程:

1. **识别变更范围**
   ```bash
   git diff main...feature-branch --name-only
   ```

2. **影响分析**
   - 运行: `python scripts/impact_analysis.py <changed_files>`
   - 检查: 哪些模块/函数调用了修改的代码?

3. **回归测试**
   - 运行相关测试: `pytest tests/ -k "<module_name>"`
   - 确认覆盖率未降低

## 删除影响评估

1. **依赖检查**
   ```bash
   python scripts/find_dependencies.py <deleted_function>
   ```

2. **确认安全删除**
   - [ ] 无其他代码引用
   - [ ] 已更新相关文档
   - [ ] 已删除相关测试

## 输出契约

审查报告必须包含:

```markdown
# Code Review Report

## Summary
- Files reviewed: [数量]
- Critical issues: [数量]
- Warnings: [数量]
- Recommendations: [数量]

## Critical Issues (Must Fix)
1. [描述] - Severity: High - Location: file.py:123

## Warnings (Should Fix)
1. [描述] - Severity: Medium - Location: file.py:456

## Recommendations (Nice to Have)
1. [描述] - Severity: Low - Location: file.py:789

## Approval Status
- [ ] Approved
- [ ] Approved with comments
- [ ] Changes requested
```

## References Navigation

| 文件 | 用途 | 何时阅读 |
|------|------|----------|
| `references/review-checklist.md` | 详细检查清单 | 执行人工审查时 |
| `references/security-patterns.md` | 常见安全问题 | 发现可疑代码时 |
| `references/performance-guide.md` | 性能优化建议 | 性能问题分析时 |

## Troubleshooting

| 问题 | 解决方案 |
|------|----------|
| 自动检查失败 | 检查 `scripts/requirements.txt` 依赖是否安装 |
| 报告格式错误 | 使用 `--format json` 或 `--format markdown` |
| 依赖分析超时 | 限制范围: `--max-depth 3` |
```

### 目录结构

```
code-review-assistant/
├── SKILL.md
├── scripts/
│   ├── auto_review.py         # 自动检查套件
│   ├── impact_analysis.py     # 影响分析
│   ├── find_dependencies.py   # 依赖查找
│   ├── generate_report.py     # 报告生成
│   └── requirements.txt       # pylint, bandit, coverage
├── references/
│   ├── review-checklist.md    # 完整检查清单
│   ├── security-patterns.md   # 安全最佳实践
│   └── performance-guide.md   # 性能优化指南
└── assets/
    └── templates/
        ├── report-template.md
        └── report-template.json
```

### 关键设计决策

✅ **决策树优先**: 不同场景走不同流程
✅ **自动化 + 人工结合**: 机器处理重复任务，人工关注高价值判断
✅ **分层严重性**: 关键/警告/建议三级分类
✅ **结构化输出**: 报告格式标准化
✅ **References 按需加载**: 不把所有清单放在主文件

---

## 示例 3: 复杂知识型 Skill (API 设计审查)

### 场景
创建一个需要深厚领域知识的 Skill，用于审查 RESTful API 设计。

### 完整 SKILL.md

```markdown
---
name: api-design-reviewer
description: |
  Expert-level RESTful API design review based on industry best practices.

  Use when:
  - Designing new REST APIs or GraphQL schemas
  - Reviewing API specifications (OpenAPI/Swagger)
  - Evaluating API versioning strategies
  - Auditing API security and authentication
  - Assessing API performance and scalability
  - Checking API documentation completeness

  Requires: OpenAPI/Swagger spec file or API endpoint documentation.
  Outputs: Comprehensive design review with architecture recommendations.
allowed-tools: [read, execute]
---

# API Design Reviewer

## Prerequisites

⚠️ **Before starting, ensure you have:**
- OpenAPI/Swagger specification (YAML or JSON)
- OR documented API endpoints with examples
- Authentication/authorization requirements
- Expected traffic/scaling targets

## Decision Tree

```
┌─────────────────────────────────────────────────────────────┐
│ API 审查决策树                                               │
├─────────────────────────────────────────────────────────────┤
│  有 OpenAPI spec? → 自动化分析 + 专家审查                    │
│  仅有文档?        → 人工审查 + 标准对照                      │
│  新设计?          → 领域专家化研究 + 最佳实践应用            │
└─────────────────────────────────────────────────────────────┘
```

**Step 1: 确定审查路径**

- **有 OpenAPI 规范文件?**
  → 使用 [自动化分析流程](#自动化分析流程)

- **仅有 API 文档/示例?**
  → 使用 [手动审查流程](#手动审查流程)

- **全新 API 设计?**
  → 先完成 [领域专家化准备](#领域专家化准备)

## 领域专家化准备

⚠️ **强制门控**: 在审查新 API 设计前，必须完成以下研究：

### 必须研究的领域 (3-5个)

参考 `references/domain-expertise-protocol.md`，提取并研究:

1. **API 风格与约定**
   - RESTful 设计原则 (Richardson 成熟度模型)
   - HTTP 方法语义 (GET/POST/PUT/PATCH/DELETE)
   - 状态码最佳实践 (2xx/3xx/4xx/5xx)

2. **资源建模**
   - 资源命名约定 (名词复数、层级关系)
   - 关系表达 (嵌套 vs 链接 vs 独立端点)
   - 分页/过滤/排序模式

3. **安全与鉴权**
   - OAuth 2.0 / JWT 最佳实践
   - API Key 管理
   - Rate limiting 策略

4. **版本管理**
   - URL 版本 vs Header 版本
   - 向后兼容性策略
   - 弃用流程

5. **性能与可扩展性**
   - 缓存策略 (ETag, Cache-Control)
   - 批量操作模式
   - 异步处理 (Webhooks, Polling)

### 研究协议

1. **联网检索** (每个领域 ≥2 个来源)
   - 官方: RFC 7231 (HTTP), OpenAPI Spec, OWASP API Security
   - 高质量: Microsoft REST API Guidelines, Google API Design Guide

2. **知识沉淀**
   - 将关键结论写入 `references/api-design-knowledge-base.md`
   - 包含: 结论/适用性/坑点/验证/引用

3. **专家化自检** (见 `references/api-expertise-checklist.md`)

## 自动化分析流程

### Step 1: 规范验证

```bash
# 验证 OpenAPI 规范
python scripts/validate_openapi.py api-spec.yaml
```

检查项:
- [ ] 规范格式正确 (OpenAPI 3.0+)
- [ ] 所有端点有描述
- [ ] 所有参数有类型定义
- [ ] 响应示例完整

### Step 2: 自动化分析

```bash
# 运行自动化审查
python scripts/analyze_api.py api-spec.yaml --output report.json
```

自动检测:
- 命名约定违规
- 缺少错误响应定义
- 不一致的响应结构
- 缺少安全定义

## 手动审查流程

使用结构化清单进行审查 (详见 `references/api-review-checklist.md`):

### 1. 资源设计 (30%)

**1.1 命名约定**
- [ ] 使用名词复数 (`/users` not `/user`)
- [ ] 避免动词 (`/users/123/activate` → `/users/123/status`)
- [ ] 层级清晰 (最多 3 层: `/users/123/posts/456`)

**1.2 HTTP 方法正确性**
- [ ] `GET` 幂等且无副作用
- [ ] `POST` 用于创建
- [ ] `PUT` 完整替换, `PATCH` 部分更新
- [ ] `DELETE` 幂等

参考: `references/http-method-semantics.md`

### 2. 响应设计 (20%)

**2.1 状态码使用**
- [ ] 成功: 200 (OK), 201 (Created), 204 (No Content)
- [ ] 客户端错误: 400 (Bad Request), 401 (Unauthorized), 404 (Not Found)
- [ ] 服务端错误: 500 (Internal Server Error), 503 (Service Unavailable)

**2.2 响应结构一致性**
```json
{
  "data": { ... },         // 成功响应
  "meta": { ... },         // 元数据 (分页等)
  "errors": [ ... ]        // 错误详情 (失败时)
}
```

参考: `references/response-patterns.md`

### 3. 安全性 (25%)

**3.1 认证与授权**
- [ ] 使用标准协议 (OAuth 2.0, JWT)
- [ ] 敏感端点需要认证
- [ ] 实施最小权限原则
- [ ] Token 过期机制

**3.2 数据保护**
- [ ] HTTPS 强制 (所有端点)
- [ ] 敏感数据脱敏 (日志、响应)
- [ ] 输入验证与清理

参考: `references/api-security-checklist.md`

### 4. 性能与可扩展性 (15%)

**4.1 缓存策略**
- [ ] `GET` 请求支持 ETag
- [ ] 适当的 `Cache-Control` 头
- [ ] 条件请求 (If-None-Match)

**4.2 大数据处理**
- [ ] 分页 (limit/offset 或 cursor-based)
- [ ] 批量操作支持
- [ ] 异步处理 (长时间任务)

参考: `references/performance-optimization.md`

### 5. 文档与可维护性 (10%)

- [ ] 每个端点有清晰描述
- [ ] 请求/响应示例完整
- [ ] 错误码文档化
- [ ] 版本策略明确

## 输出契约

审查报告必须包含以下结构:

```markdown
# API Design Review Report

## Executive Summary
- Overall Score: [0-100]
- Critical Issues: [数量]
- Warnings: [数量]
- Best Practices Followed: [百分比]

## Detailed Findings

### Resource Design (Score: X/30)
#### Issues
1. [描述] - Severity: High - Endpoint: GET /user
   - Current: `/user`
   - Recommended: `/users`
   - Reference: REST naming conventions

### Security (Score: X/25)
#### Issues
1. [描述] - Severity: Critical - Endpoint: POST /login
   - Current: No rate limiting
   - Recommended: Implement 5 requests/minute limit
   - Reference: OWASP API Security Top 10

### [其他维度...]

## Architecture Recommendations

1. **版本策略**: 建议使用 URL 版本 (`/v1/users`) 而非 Header 版本
   - 理由: 更易于测试和文档化
   - 迁移路径: [具体步骤]

2. **[其他建议...]**

## Action Items (Prioritized)

### Must Fix (P0)
- [ ] [关键问题 1]
- [ ] [关键问题 2]

### Should Fix (P1)
- [ ] [重要问题 1]
- [ ] [重要问题 2]

### Nice to Have (P2)
- [ ] [优化建议 1]

## Compliance Checklist

- [ ] RESTful 设计原则
- [ ] OWASP API Security Top 10
- [ ] OpenAPI 3.0 规范
- [ ] 行业特定标准 (如 FHIR for healthcare)
```

## 验证

生成报告后，运行验证:

```bash
# 验证报告完整性
python scripts/validate_review_report.py report.md
```

## References Navigation

| 文件 | 用途 | 何时阅读 |
|------|------|----------|
| `references/api-design-knowledge-base.md` | 完整知识库 | 领域专家化准备时 **必读** |
| `references/api-review-checklist.md` | 详细检查清单 | 执行手动审查时 |
| `references/http-method-semantics.md` | HTTP 方法语义 | 审查端点设计时 |
| `references/response-patterns.md` | 响应结构模式 | 设计响应格式时 |
| `references/api-security-checklist.md` | 安全检查清单 | 安全审查时 **必读** |
| `references/performance-optimization.md` | 性能优化指南 | 性能问题分析时 |
| `references/versioning-strategies.md` | 版本管理策略 | 设计版本方案时 |
| `references/api-expertise-checklist.md` | 专家化自检表 | 完成研究后自检时 **必读** |

## Common Pitfalls

| 坑点 | 检测方法 | 规避措施 | 修复方法 |
|------|----------|----------|----------|
| 动词端点 | 搜索 `/create`, `/update`, `/delete` | 使用 HTTP 方法 + 资源名 | 重构为 `POST /users`, `PUT /users/123` |
| 不一致命名 | 检查单复数混用 | 统一使用复数 | 批量重命名端点 |
| 缺少错误处理 | 检查 4xx/5xx 定义 | 定义标准错误响应 | 补充错误响应规范 |
| 过度嵌套 | 层级 >3 | 扁平化设计 | 使用链接而非嵌套 |
| 缺少版本 | 检查 URL/Header | 从 v1 开始 | 添加版本前缀 |

## Advanced Topics

对于复杂场景，参考:
- `references/graphql-vs-rest.md` - 何时选择 GraphQL
- `references/async-patterns.md` - 异步 API 设计
- `references/microservices-api-gateway.md` - 微服务 API 网关模式
```

### 目录结构

```
api-design-reviewer/
├── SKILL.md
├── scripts/
│   ├── validate_openapi.py      # OpenAPI 规范验证
│   ├── analyze_api.py           # 自动化分析
│   ├── validate_review_report.py # 报告验证
│   └── requirements.txt         # openapi-spec-validator, pyyaml
├── references/
│   ├── domain-expertise-protocol.md      # 领域专家化协议 (继承自 skill-expert-skills)
│   ├── api-design-knowledge-base.md      # API 设计知识库 (研究结果沉淀)
│   ├── api-review-checklist.md           # 完整审查清单
│   ├── api-expertise-checklist.md        # 专家化自检表
│   ├── http-method-semantics.md          # HTTP 方法详解
│   ├── response-patterns.md              # 响应结构模式
│   ├── api-security-checklist.md         # 安全清单 (OWASP 等)
│   ├── performance-optimization.md       # 性能优化
│   ├── versioning-strategies.md          # 版本管理
│   ├── graphql-vs-rest.md                # GraphQL vs REST
│   ├── async-patterns.md                 # 异步模式
│   └── microservices-api-gateway.md      # 微服务网关
└── assets/
    └── templates/
        └── review-report-template.md
```

### 关键设计决策

✅ **领域专家化强制门控**: 新设计必须先完成研究
✅ **分层知识库**: 8+ references 文件，按需精准加载
✅ **多路径支持**: OpenAPI 自动化 vs 手动审查
✅ **结构化评分**: 5 个维度独立评分，可量化
✅ **可追溯性**: 每条建议都引用 reference 依据
✅ **坑点清单**: 常见错误预防

---

## 对比分析

### 复杂度对比

| 维度 | 示例 1 (工具型) | 示例 2 (工作流型) | 示例 3 (知识型) |
|------|----------------|------------------|----------------|
| **SKILL.md 行数** | ~80 行 | ~180 行 | ~280 行 |
| **references 文件数** | 1 个 | 3 个 | 8+ 个 |
| **scripts 数量** | 3 个 | 4 个 | 3 个 |
| **决策分支** | 无 (线性流程) | 3 个主分支 | 2 个主分支 + 领域门控 |
| **领域专家化** | 不需要 | 不需要 | **必需** (强制) |
| **允许工具** | read, write, execute | read, grep, execute | read, execute |
| **输出结构化** | 简单 (文件转换) | 中等 (分级报告) | 复杂 (评分+建议+行动项) |
| **适用场景** | 确定性任务 | 多步骤流程 | 需要专业判断 |

### 最佳实践映射

| 最佳实践 | 示例 1 | 示例 2 | 示例 3 |
|---------|--------|--------|--------|
| **精炼性** (SKILL.md < 500行) | ✅ 80 行 | ✅ 180 行 | ✅ 280 行 |
| **渐进式披露** | ✅ 细节在 references | ✅ 清单在 references | ✅ 8+ references 按需加载 |
| **决策树** | ⚠️ 不需要 | ✅ 清晰分支 | ✅ 多层决策 + 门控 |
| **输出契约** | ✅ 明确 | ✅ 结构化模板 | ✅ 评分系统 |
| **自动化脚本** | ✅ 核心逻辑脚本化 | ✅ 检查自动化 | ✅ 验证脚本 |
| **领域专家化** | ⚠️ 不适用 | ⚠️ 不适用 | ✅ 强制门控 |
| **最小权限** | ✅ 仅需 3 工具 | ✅ 仅需 3 工具 | ✅ 仅需 2 工具 |
| **通用性** | ✅ 无项目细节 | ✅ 无项目细节 | ✅ 无项目细节 |

---

## 选择指南

### 何时使用每种模式?

**选择示例 1 (简单工具型) 如果:**
- ✅ 任务是确定性的 (输入 → 处理 → 输出)
- ✅ 核心逻辑可以脚本化
- ✅ 不需要复杂决策
- ✅ 用户只需要"一键执行"

**选择示例 2 (中等工作流型) 如果:**
- ✅ 任务有多个步骤
- ✅ 存在条件分支 (if-then-else)
- ✅ 需要人工判断和机器检查结合
- ✅ 输出需要结构化报告

**选择示例 3 (复杂知识型) 如果:**
- ✅ 任务需要深厚的领域知识
- ✅ 判断标准来自行业最佳实践
- ✅ 需要大量背景知识库
- ✅ 输出需要专家级质量
- ✅ 用户期望学习领域知识

---

## 快速启动模板

### 从示例创建新 Skill

```bash
# 1. 确定复杂度类型
# 简单工具型 → 复制示例 1 结构
# 中等工作流型 → 复制示例 2 结构
# 复杂知识型 → 复制示例 3 结构

# 2. 初始化目录
python scripts/init_skill.py my-new-skill --path .claude/skills

# 3. 参考对应示例，填充内容
# - 修改 description (覆盖触发场景)
# - 调整决策树 (如果需要)
# - 编写核心流程
# - 创建 references/ (按需)
# - 编写 scripts/ (如果需要)

# 4. 验证
python scripts/quick_validate.py .claude/skills/my-new-skill
```

---

## 常见问题

**Q: 我的任务介于两种复杂度之间，怎么选?**
A: 从简单模式开始，按需增加复杂度。过早优化会增加维护成本。

**Q: references/ 应该放多少文件?**
A:
- 简单型: 0-2 个 (可选)
- 中等型: 2-5 个
- 复杂型: 5-10 个 (领域知识库 + 清单)

**Q: 何时需要领域专家化?**
A: 当你的 Skill 需要回答"为什么这样做是最佳实践"时。如果只是"执行步骤"，不需要。

**Q: scripts/ 是必需的吗?**
A: 不是。但对于:
- 重复性高的操作 (示例 1)
- 易错的检查 (示例 2)
- 格式验证 (示例 3)
脚本可以显著提高可靠性。

**Q: 如何避免 SKILL.md 过长?**
A:
1. 决策树 + 流程概览放主文件
2. 详细清单 → `references/*-checklist.md`
3. 知识背景 → `references/*-knowledge-base.md`
4. 边缘案例 → `references/edge-cases.md`

---

## 后续学习资源

- **深入理解 Skills 机制**: `references/skills-knowledge-base.md`
- **领域专家化协议**: `references/domain-expertise-protocol.md`
- **工作流模式库**: `references/workflows.md`
- **输出模式库**: `references/output-patterns.md`
