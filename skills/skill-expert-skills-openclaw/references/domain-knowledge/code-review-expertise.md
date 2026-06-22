# Code Review 领域专业知识库

> 创建日期: 2025-01-17
> 知识来源: 深度研究 + 行业最佳实践
> 适用场景: 优化/创建 code-review 相关 Skills

---

## 目录

1. [核心概念](#1-核心概念)
2. [代码审查心智模型](#2-代码审查心智模型)
3. [审查框架](#3-审查框架)
4. [审查维度](#4-审查维度)
5. [常见陷阱](#5-常见陷阱)
6. [自动化审查](#6-自动化审查)
7. [知识沉淀](#7-知识沉淀)
8. [工具与技术](#8-工具与技术)

---

## 1. 核心概念

### 1.1 代码审查的本质

**代码审查不是代码检查，而是知识传递和风险控制。**

关键洞察：
- 代码审查 = 知识分享 + 风险识别 + 团队建设
- 核心目标：提高代码质量，而非挑错
- 审查者 = 协作者，而非审判者

### 1.2 审查 vs 检查

| 代码审查 (Code Review) | 静态检查 (Linting) |
|------------------|-----------------|
| 人工+工具结合 | 自动化工具 |
| 关注设计意图、可读性、架构 | 关注语法、风格、基本错误 |
| 需要上下文和业务理解 | 无需上下文 |
| 会话式讨论 | 报告式输出 |

---

## 2. 代码审查心智模型

### 2.1 审查者角色定位

来源: [Google Engineering Practices](https://google.github.io/eng-practices/review/)

**核心原则**：审查者是协作者，不是对手。

| 角色 | 负面做法 | 正面做法 |
|------|----------|----------|
| 审查者 | 挑错、指责、炫耀 | 协助、解释、引导 |
| 被审查者 | 防御、抗拒、情绪化 | 接受、讨论、改进 |

### 2.2 审查心态

```
┌─────────────────────────────────────────┐
│  良好的审查心态                     │
├─────────────────────────────────────────┤
│  1. 代码是团队的，不是个人的          │
│  2. 指出问题 = 帮助改进           │
│  3. 讨论技术，不讨论人             │
│  4. 关注重要问题，不纠结琐碎         │
│  5. 提供解决方案，不只是提问题       │
└─────────────────────────────────────────┘
```

---

## 3. 审查框架

### 3.1 三层审查法

来源: [Uber Code Review Guide](https://eng.uber.com/reviews/)

```
┌─────────────────────────────────────────┐
│  Layer 1: 快速扫视 (30 秒)        │
│  ├─ 功能是否完整?                   │
│  ├─ 结构是否清晰?                   │
│  └─ 命名是否合理?                   │
├─────────────────────────────────────────┤
│  Layer 2: 深度检查 (5-10 分钟)     │
│  ├─ 逻辑是否正确?                   │
│  ├─ 边界是否处理?                   │
│  ├─ 性能是否合理?                   │
│  └─ 安全是否考虑?                   │
├─────────────────────────────────────────┤
│  Layer 3: 跨模块影响 (2-5 分钟)      │
│  ├─ API 兼容性                     │
│  ├─ 数据库影响                       │
│  └─ 前后端一致性                   │
└─────────────────────────────────────────┘
```

### 3.2 审查清单模板

```markdown
## Code Review Checklist

### 功能性
- [ ] 需求完整实现
- [ ] 边界情况处理
- [ ] 错误处理充分
- [ ] 单元测试覆盖

### 可读性
- [ ] 命名清晰有意义
- [ ] 函数职责单一
- [ ] 复杂逻辑有注释
- [ ] 避免魔法数字

### 架构与设计
- [ ] 遵循项目架构
- [ ] 代码复用合理
- [ ] 接口设计清晰
- [ ] 依赖关系合理

### 安全性
- [ ] 输入验证
- [ ] SQL 注入防护
- [ ] 敏感数据处理
- [ ] 认证授权正确

### 性能
- [ ] 无明显性能问题
- [ ] 数据库查询优化
- [ ] 缓存策略合理
- [ ] 资源正确释放
```

---

## 4. 审查维度

### 4.1 正确性 (Correctness)

**核心问题**：代码是否正确实现了需求？

检查项：
- 业务逻辑是否符合需求
- 边界情况是否处理
- 错误情况是否考虑
- 数据类型是否正确

示例：
```python
# ❌ 错误：未处理空列表
def sum(numbers):
    result = 0
    for n in numbers:
        result += n
    return result

# ✅ 正确：处理空列表
def sum(numbers):
    if not numbers:
        return 0
    result = 0
    for n in numbers:
        result += n
    return result
```

### 4.2 可读性 (Readability)

**核心问题**：代码是否易于理解？

来源: [Clean Code Principles](https://github.com/ryanmcdermott/clean-code-javascript)

检查项：
- 命名是否自描述
- 函数是否短小（< 50 行）
- 嵌套层级是否过深（< 4 层）
- 注释是否解释"为什么"而非"是什么"

### 4.3 可维护性 (Maintainability)

**核心问题**：代码是否易于修改和扩展？

检查项：
- 函数职责是否单一
- 模块耦合度是否低
- 是否避免代码重复
- 配置是否与代码分离

### 4.4 安全性 (Security)

**核心问题**：代码是否存在安全漏洞？

来源: [OWASP Top 10](https://owasp.org/www-project-top-ten/)

检查项：
- 输入是否验证和清理
- SQL 查询是否参数化
- 敏感数据是否加密
- 认证授权是否正确
- 是否有 XSS/CSRF 防护

### 4.5 性能 (Performance)

**核心问题**：代码性能是否可接受？

检查项：
- 是否有 N+1 查询
- 是否有不必要的循环
- 是否有内存泄漏风险
- 是否利用了缓存

---

## 5. 常见陷阱

### 5.1 审查者陷阱

| 陷阱 | 表现 | 解决 |
|------|------|------|
| 过度挑剔 | 指出太多小问题 | 优先级分类，聚焦重要问题 |
| 只看不说 | 只列问题，不解释 | 提供改进建议和示例 |
| 风格警察 | 纠结代码风格问题 | 使用 linter 自动化风格检查 |
| 拖延审查 | PR 提交后几天才审查 | 设定 SLA，及时反馈 |

### 5.2 被审查者陷阱

| 陷阱 | 表现 | 解决 |
|------|------|------|
| 防御心理 | 反驳每个问题 | 接受建议，讨论而非反驳 |
| 情绪化 | 感到被攻击 | 保持专业，聚焦代码 |
| 解释过多 | 过度解释代码 | 让代码自解释，减少注释 |
| 不修改 | 评论后不更新 | 按优先级修复，及时回复 |

### 5.3 团队陷阱

| 陷阱 | 表现 | 解决 |
|------|------|------|
| 只有少数人审查 | 知识集中在少数人 | 轮换审查者，知识扩散 |
| 审查不深入 | 流于形式 | 设定审查深度要求 |
| 无审查规范 | 每个人审查标准不同 | 建立团队审查清单 |
| 无学习机制 | 同样问题反复出现 | 建立知识库，沉淀经验 |

---

## 6. 自动化审查

### 6.1 静态分析工具

| 类别 | 工具 | 语言 | 检查内容 |
|------|------|------|----------|
| Linter | ESLint, Pylint, gofmt | JS/TS/Python/Go | 代码风格、基本错误 |
| 类型检查 | TypeScript, mypy | TypeScript/Python | 类型错误 |
| 安全扫描 | Bandit, Snyk, SonarQube | 多语言 | 安全漏洞 |
| 依赖检查 | npm audit, Snyk | JS/TS/Python | 依赖漏洞 |

### 6.2 CI/CD 集成

```yaml
# 示例: GitHub Actions 自动审查
name: Code Review Automation

on: [pull_request]

jobs:
  auto-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run linter
        run: npm run lint
      - name: Run type check
        run: npm run type-check
      - name: Security scan
        run: npm audit
      - name: Post comment
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              body: '🤖 Automated review completed'
            })
```

### 6.3 审查工具对比

| 工具 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| GitHub PR Review | 原生集成，易用 | 功能基础 | 小型团队 |
| Gerrit | 强大，细粒度权限 | 复难用 | 大型项目 |
| Phabricator | 功能丰富 | 维护成本高 | 中型团队 |
| Reviewable | 界面友好 | 付费 | 追求体验的团队 |

---

## 7. 知识沉淀

### 7.1 审查知识库价值

- 避免重复讨论
- 提高审查一致性
- 新成员快速上手
- 持续改进标准

### 7.2 审查记录模板

```markdown
## Review ID: REVIEW-XXX

### 概览
- PR: #123
- 审查者: @author
- 日期: 2025-01-17
- 状态: ✅ Approved

### 发现的问题

| 严重性 | 类型 | 描述 | 位置 | 状态 |
|--------|------|------|------|------|
| High | 安全 | SQL 注入风险 | app.py:123 | 已修复 |
| Medium | 性能 | N+1 查询 | models.py:45 | 已优化 |
| Low | 风格 | 缩进不一致 | utils.py:67 | 已修正 |

### 讨论记录

**作者提问**: 为什么要用这种方式？

**审查者回答**: 因为 X 和 Y 的原因。可以考虑替代方案 Z。

**最终决定**: 保持原方案，添加注释说明。

### 经验教训
1. [可复用的教训]
2. [可复用的教训]
```

### 7.3 模式提取

从具体审查中提取通用模式：

| 具体问题 | 通用模式 |
|----------|----------|
| "变量名 `d` 不清晰" | 命名应该有意义，避免单字母 |
| "函数 200 行太长" | 函数应该短小，单一职责 |
| "重复代码在 3 处" | 应该提取公共函数/类 |
| "缺少错误处理" | 所有外部调用应该有 try-catch |

---

## 8. 工具与技术

### 8.1 审查工具

| 类别 | 工具 | 用途 |
|------|------|------|
| Git Diff | `git diff`, `git show` | 查看变更 |
| GitHub/GitLab | PR/MR 功能 | 在线审查 |
| Review Board | 多平台统一 | 大型团队管理 |
| SonarQube | 代码质量分析 | 自动化质量检查 |

### 8.2 审查最佳实践

| 实践 | 说明 |
|------|------|
| 小 PR | 保持 PR 小（< 400 行） |
| 及时反馈 | 24 小时内响应 |
| 面对面讨论 | 复杂问题直接沟通 |
| 代码归属 | 审查者对审查代码负责 |
| 持续学习 | 每周分享审查心得 |

### 8.3 团队文化

来源: [Netflix Culture](https://jobs.netflix.com/culture)

**核心原则**：
- 自由与责任
- 上下文而非控制
- 高绩效环境
- 坦诚与尊重

---

## 参考资料

- [Google Engineering: Code Review](https://google.github.io/eng-practices/review/) - Google 代码审查最佳实践
- [Uber: Code Review Guide](https://eng.uber.com/reviews/) - Uber 代码审查指南
- [OWASP Top 10](https://owasp.org/www-project-top-ten/) - OWASP 安全漏洞
- [Clean Code](https://github.com/ryanmcdermott/clean-code-javascript) - Clean Code 原则
- [Effective Code Review](https://www.cqse.eu/en/publications/downloads/Efficient_code_review_2008.pdf) - 高效代码审查研究
- [SonarQube Documentation](https://docs.sonarqube.org/) - SonarQube 文档
- [Wikipedia: Code Review](https://en.wikipedia.org/wiki/Code_review) - 代码审查维基百科
