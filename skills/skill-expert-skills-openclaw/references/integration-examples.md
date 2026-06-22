# Skill 集成示例 (Integration Examples)

> 最后更新: 2025-01-17
> 用途: 提供 Skill 集成的完整示例和最佳实践
> 适用于: 多个 Skill 协同工作、Skill 作为依赖项使用

---

## 目录

1. [示例索引](#1-示例索引)
2. [示例 1: 前端 + 后端协作](#2-示例-1-前端--后端协作)
3. [示例 2: Skill 链式工作流](#3-示例-2-skill-链式工作流)
4. [示例 3: 全栈 Skill 集成](#4-示例-3-全栈-skill-集成)
5. [Skill 依赖管理](#5-skill-依赖管理)
6. [最佳实践](#6-最佳实践)

---

## 1. 示例索引

| 示例 | 涉及 Skills | 复杂度 | 使用场景 |
|------|------------|--------|----------|
| [示例 1](#2-示例-1-前端--后端协作) | frontend-expertise + backend-expertise | 中 | 前后端团队协作 |
| [示例 2](#3-示例-2-skill-链式工作流) | bug-fixing + code-review + testing-patterns | 高 | 端到端开发流程 |
| [示例 3](#4-示例-3-全栈-skill-集成) | 所有核心 Skills | 高 | 大型项目完整开发 |
| [依赖管理](#5-skill-依赖管理) | - | - | Skill 作为依赖项 |

---

## 2. 示例 1: 前端 + 后端协作

### 2.1 场景

用户需要创建一个完整的 API 功能，涉及：
- 后端 API 设计和实现
- 前端组件开发和集成
- 前后端联调

### 2.2 涉及的 Skills

| Skill | 角色 | 关键产出 |
|--------|------|----------|
| `backend-expertise` | 后端架构、API 设计 | API 文档、接口实现 |
| `frontend-expertise` | 前端组件、状态管理 | React 组件、状态逻辑 |
| `api-design-reviewer` | API 质量审查 | 审查报告、改进建议 |

### 2.3 协作流程

```
┌─────────────────────────────────────────┐
│  前后端协作流程                    │
├─────────────────────────────────────────┤
│                                        │
│  Step 1: 后端设计                    │
│  ├─ backend-expertise: API 设计        │
│  ├─ api-design-reviewer: 设计审查      │
│  └─ 后端实现代码                      │
│                                        │
│  Step 2: 前端开发                    │
│  ├─ frontend-expertise: 组件设计        │
│  ├─ frontend-expertise: 状态管理       │
│  └─ 前端实现组件                      │
│                                        │
│  Step 3: 联调测试                    │
│  ├─ frontend-expertise: 联调策略      │
│  ├─ backend-expertise: 错误处理        │
│  └─ 代码审查                        │
│                                        │
└─────────────────────────────────────────┘
```

### 2.4 示例：RESTful API + React 前端

#### 后端 SKILL.md 片段

```markdown
## API 端点设计

### 设计阶段
使用 backend-expertise 和 api-design-reviewer:
1. 设计资源模型
2. 规划 RESTful 端点
3. 定义错误响应格式
4. 审查设计质量

### 实现阶段
1. 实现数据访问层
2. 实现 API 端点
3. 添加输入验证
4. 编写 API 文档
```

#### 前端 SKILL.md 片段

```markdown
## API 集成

### 组件设计
使用 frontend-expertise:
1. 设计数据获取层 (React Query/SWR)
2. 创建 API 客户端
3. 设计错误处理和重试逻辑
4. 实现加载状态

### 状态管理
使用 frontend-expertise:
1. 设计全局状态结构
2. 实现缓存策略
3. 处理乐观更新
4. 管理错误状态
```

### 2.5 协作示例

```javascript
// 前端：使用 React Query + 后端 API

// 1. API 客户端 (由 backend-expertise 设计)
import { useQuery, useMutation } from '@tanstack/react-query';

const useUsers = () => {
  return useQuery(
    ['users'],
    () => fetch('/api/v1/users').then(r => r.json())
  );
};

// 2. 优化策略 (由 frontend-expertise 优化)
const useUsers = () => {
  return useQuery(
    ['users'],
    () => fetch('/api/v1/users').then(r => r.json()),
    {
      staleTime: 5 * 60 * 1000,  // 5 分钟缓存
      retry: 3,  // 失败重试 3 次
    }
  );
};
```

---

## 3. 示例 2: Skill 链式工作流

### 3.1 场景

用户需要修复一个复杂的 Bug，涉及：
- Bug 定位和根因分析
- 修复方案设计和实现
- 代码审查和质量检查
- 测试用例编写和验证

### 3.2 涉及的 Skills

| Skill | 角色 | 关键产出 |
|--------|------|----------|
| `bug-fixing-expertise` | 根因分析、修复实现 | 5 Why 分析、修复方案 |
| `code-review-expertise` | 修复代码审查 | 审查报告、改进建议 |
| `frontend-expertise` | 前端测试 | 测试用例、自动化测试 |
| `backend-expertise` | 后端测试 | 测试用例、集成测试 |

### 3.3 Skill 链流程

```
┌─────────────────────────────────────────┐
│  Bug 修复 Skill 链                    │
├─────────────────────────────────────────┤
│                                        │
│  Step 1: Bug 分析                     │
│  └─ bug-fixing-expertise                │
│       ├─ 5 Why 根因分析             │
│       ├─ 修复方案设计                 │
│       └─ 影响分析                    │
│                                        │
│  Step 2: 修复实现                     │
│  └─ bug-fixing-expertise                │
│       ├─ 实施修复代码                 │
│       ├─ 添加回归测试                   │
│       └─ 更新文档                      │
│                                        │
│  Step 3: 代码审查                     │
│  └─ code-review-expertise              │
│       ├─ 审查修复质量                   │
│       ├─ 检查安全性                     │
│       └─ 验证测试覆盖                   │
│                                        │
│  Step 4: 测试验证                     │
│   ├─ frontend-expertise (前端测试)    │
│   └─ backend-expertise (后端测试)     │
│                                        │
│  Step 5: 知识沉淀                     │
│   └─ bug-fixing-expertise              │
│       ├─ 更新 Bug 知识库               │
│       └─ 提炼通用模式                 │
│                                        │
└─────────────────────────────────────────┘
```

### 3.4 完整示例：API Bug 修复

#### Step 1: Bug 分析 (bug-fixing-expertise)

```
📝 Bug 报告：
用户反馈：分页数据不一致

🔍 5 Why 根因分析：
Why 1: 为什么显示数据不一致？
  → 前端和后端返回的数据格式不同

Why 2: 为什么格式不同？
  → 后端 API 返回嵌套结构，前端期望扁平

Why 3: 为什么后端返回嵌套？
  → 代码中使用了 ORM 的序列化方法

Why 4: 为什么使用了错误方法？
  → 开发者没有阅读 API 设计文档

Why 5: 如何根本解决？
  → 统一 API 响应格式，更新 API 文档，培训团队

📊 影响分析：
- 受影响的用户：所有使用该 API 的前端页面
- 影响范围：3 个主要功能模块
- 优先级：P0 (高优先级)
```

#### Step 2: 修复实现 (bug-fixing-expertise)

```python
# 后端修复：统一 API 响应格式

# 修复前 (错误的嵌套格式)
@router.get("/api/v1/users")
async def get_users():
    users = db.query(User).all()
    return {"data": {"users": users}}  # 错误的嵌套

# 修复后 (扁平格式)
@router.get("/api/v1/users")
async def get_users():
    users = db.query(User).all()
    return {
        "data": users,  # 扁平数组
        "meta": {
            "total": len(users),
            "page": 1
        }
    }
```

#### Step 3: 前端适配 (frontend-expertise)

```javascript
// 前端：使用新的扁平格式

import { useQuery } from '@tanstack/react-query';

const useUsers = () => {
  return useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const response = await fetch('/api/v1/users').then(r => r.json());
      return response.data;  // 直接使用 data
    }
  });
};

// 组件中使用
function UserList() {
  const { data: users, isLoading, error } = useUsers();

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  
  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

#### Step 4: 代码审查 (code-review-expertise)

```
📋 代码审查报告：

后端代码：
- ✅ API 响应格式统一
- ✅ 错误处理完善
- ⚠️ 建议添加分页参数验证
- ⚠️ 建议添加速率限制

前端代码：
- ✅ 正确使用新的 API 格式
- ✅ 错误处理完善
- ⚠️ 建议添加虚拟列表优化
- ⚠️ 建议添加分页组件

安全性检查：
- ✅ 无 SQL 注入风险
- ✅ 输入验证充分
- ✅ 错误信息不泄露敏感数据
```

#### Step 5: 测试验证 (frontend-expertise + backend-expertise)

```python
# 后端测试
def test_api_response_format():
    response = client.get("/api/v1/users")
    assert "data" in response.json()
    assert isinstance(response.json()["data"], list)
    assert "meta" in response.json()
```

```javascript
// 前端测试
describe('User API Integration', () => {
  it('should fetch and display users', async () => {
    render(<UserList />);
    await waitFor(() => screen.getAllByText(/User \d+/));
    expect(screen.getAllByText(/User \d+/)).toHaveLength(10);
  });

  it('should handle loading state', async () => {
    const { result } = renderHook(() => useUsers());
    expect(result.current.isLoading).toBe(true);
  });
});
```

---

## 4. 示例 3: 全栈 Skill 集成

### 4.1 场景

从零开始开发一个完整的用户认证系统，涉及：
- 需求分析和设计
- 后端 API 开发
- 前端界面开发
- 安全实现
- 测试和部署

### 4.2 Skill 依赖图

```
                    ┌─────────────┐
                    │  项目启动    │
                    └──────┬──────┘
                           ↓
              ┌────────────────┐
              │  领域专家化   │
              │  (Step 0)     │
              └──────┬─────────┘
                     ↓
        ┌────────────────────────┐
        │  技术架构设计      │
        │  backend-expertise │
        └──────┬─────────────┘
               ↓
       ┌───────────┬──────────┬────────┐
       ↓           ↓          ↓        ↓
┌──────┐  ┌──────┐  ┌──────┐ ┌──────┐
│ 数据库 │  │  API   │  │前端  │  │安全  │
│ 设计   │  │  开发 │  │开发  │  │实现  │
└──────┘  └──────┘  └──────┘ └──────┘
       ↓
┌─────────────────────────────────────────┐
│  集成测试与代码审查               │
│  (frontend + backend + security)   │
└─────────────────────────────────────────┘
```

### 4.3 完整工作流

#### 阶段 1: 需求分析 (30 分钟)

```
使用 Skills: product-requirements, domain-expertise-protocol

1. 收集需求
   - 用户注册、登录、密码重置
   - OAuth 集成（Google, GitHub）
   - JWT Token 管理

2. 设计系统架构
   - 使用 backend-expertise 设计 API 架构
   - 使用 frontend-expertise 设计前端架构
   - 使用 security-expertise 设计安全策略

3. 输出产物
   - 需求文档
   - API 设计文档
   - 安全需求文档
```

#### 阶段 2: 后端开发 (2 小时)

```
使用 Skills: backend-expertise, api-design-reviewer, security-expertise

1. 数据库设计
   - Users 表（包含 OAuth 信息）
   - Sessions 表（Token 管理）
   - 使用 database-expertise 优化索引

2. API 实现
   - 注册、登录、注销端点
   - OAuth 回调处理
   - JWT Token 生成和验证

3. 安全实现
   - 密码哈希（bcrypt/argon2）
   - JWT 签名和验证
   - Rate Limiting 防暴力破解
   - HTTPS 强制

4. API 文档编写
   - OpenAPI/Swagger 规范
   - 使用 api-design-reviewer 审查
```

#### 阶段 3: 前端开发 (3 小时)

```
使用 Skills: frontend-expertise, backend-expertise (用于理解 API)

1. 认证组件开发
   - 登录表单
   - 注册表单
   - 密码重置表单
   - OAuth 按钮集成

2. 状态管理
   - 认证状态（已登录/未登录）
   - 用户信息状态
   - Token 管理状态

3. API 集成
   - API 客户端封装
   - 错误处理和重试
   - Token 自动刷新

4. 路由和导航
   - 受保护路由配置
   - 重定向逻辑
```

#### 阶段 4: 测试与审查 (1 小时)

```
使用 Skills: testing-patterns, code-review-expertise, security-expertise

1. 安全测试
   - SQL 注入测试
   - XSS 攻击测试
   - CSRF 防护测试
   - Rate Limiting 验证

2. 功能测试
   - 登录流程端到端测试
   - Token 刷新测试
   - OAuth 回调测试

3. 性能测试
   - API 响应时间
   - 前端渲染性能

4. 代码审查
   - 后端代码审查 (backend-expertise + code-review)
   - 前端代码审查 (frontend-expertise + code-review)
   - 安全代码审查 (security-expertise)
```

### 4.4 技术栈推荐

| 层级 | 推荐技术 | 对应 Skill |
|------|----------|------------|
| 后端框架 | FastAPI, Django | backend-expertise |
| 数据库 | PostgreSQL | database-expertise |
| 认证 | JWT, OAuth 2.0 | security-expertise |
| 前端框架 | React, Next.js | frontend-expertise |
| 状态管理 | Zustand, TanStack Query | frontend-expertise |
| 表单 | React Hook Form, Zod | frontend-expertise |
| 测试 | Jest, Playwright, pytest | testing-patterns |

---

## 5. Skill 依赖管理

### 5.1 依赖声明

在 SKILL.md frontmatter 中声明依赖：

```yaml
---
name: my-complex-skill
description: |
  Complex skill that depends on backend-expertise and frontend-expertise.
  
  Use when building full-stack features requiring both backend and frontend expertise.
  
  Dependencies: backend-expertise, frontend-expertise
  
required-skills:
  - backend-expertise
  - frontend-expertise
---
```

### 5.2 依赖检查

在 Skill 执行前检查依赖是否可用：

```python
def check_skill_dependencies(required_skills: List[str]) -> bool:
    """检查依赖 Skill 是否可用"""
    for skill in required_skills:
        skill_path = Path(f".claude/skills/{skill}/SKILL.md")
        if not skill_path.exists():
            print(f"❌ Missing dependency: {skill}")
            return False
    return True
```

### 5.3 依赖调用示例

```python
# 在 Skill 中调用其他 Skill

def my_complex_skill():
    # 检查依赖
    if not check_skill_dependencies(["backend-expertise", "frontend-expertise"]):
        return {"error": "Missing dependencies"}
    
    # 调用 backend-expertise
    backend_advice = use_backend_expertise_for_api_design()
    
    # 调用 frontend-expertise
    frontend_advice = use_frontend_expertise_for_integration()
    
    # 结合两个 Skill 的建议
    return {
        "backend": backend_advice,
        "frontend": frontend_advice,
        "integrated_plan": merge_advices(backend_advice, frontend_advice)
    }
```

---

## 6. 最佳实践

### 6.1 Skill 组合原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **单一职责** | 每个 Skill 专注一个领域 | `backend-expertise` 负责后端，不涉及前端 |
| **高内聚低耦合** | 相关 Skill 之间协作紧密 | `bug-fixing` 和 `code-review` 可以结合使用 |
| **避免循环依赖** | A → B → A 会造成循环 | 避免 `skill-a` 依赖 `skill-b`，`skill-b` 依赖 `skill-a` |
| **接口清晰** | Skill 之间通过明确的接口交互 | 使用标准的 API 响应格式 |

### 6.2 工作流设计

```
良好的 Skill 组合工作流：

1. 明确主 Skill 和辅助 Skill
   - 主 Skill: 负责主要流程
   - 辅助 Skill: 提供特定领域的专业知识

2. 定义清晰的输入输出接口
   - 主 Skill 提供领域信息给辅助 Skill
   - 辅助 Skill 返回专业建议给主 Skill

3. 使用渐进式披露
   - 主 SKILL.md 简洁描述主要流程
   - 详细专业知识在 references/

4. 添加知识共享机制
   - 使用共享的领域知识库
   - 更新共同的 references 文档
```

### 6.3 错误处理

```python
# Skill 调用失败时的优雅降级

def execute_with_fallback(primary_skill: str, fallback_skill: str, context: dict):
    """主要 Skill 失败时使用备用 Skill"""
    try:
        result = execute_primary_skill(primary_skill, context)
        return {"source": primary_skill, "result": result}
    except Exception as e:
        print(f"⚠️ Primary skill {primary_skill} failed: {e}")
        result = execute_fallback_skill(fallback_skill, context)
        return {"source": fallback_skill, "result": result, "warning": "Used fallback"}
```

### 6.4 文档管理

```
推荐的项目文档结构：

project/
├── .claude/skills/
│   ├── my-complex-skill/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   ├── backend-advice.md (从 backend-expertise 提取)
│   │   │   ├── frontend-advice.md (从 frontend-expertise 提取)
│   │   │   └── integration-notes.md
│   ├── backend-expertise/ (依赖 Skill)
│   └── frontend-expertise/ (依赖 Skill)
```
```

---

## 7. 总结

### 7.1 关键要点

1. **Skill 组合可以解决复杂问题** - 前后端协作、全栈开发等
2. **需要清晰的接口和责任分工** - 每个 Skill 负责特定领域
3. **共享领域知识库提高效率** - 避免重复研究
4. **渐进式披露保持简洁性** - 主 SKILL.md 简洁，详细信息在 references/
5. **优雅的错误处理和回退机制** - 一个 Skill 失败不影响整体流程

### 7.2 适用场景

| 场景 | 推荐的 Skill 组合 |
|------|----------------------|
| 前端 + 后端开发 | `frontend-expertise` + `backend-expertise` + `api-design-reviewer` |
| Bug 修复流程 | `bug-fixing-expertise` + `code-review-expertise` + `testing-patterns` |
| 全栈功能开发 | `product-requirements` + 所有领域专家 Skills |
| 代码质量改进 | `code-review-expertise` + `testing-patterns` + 具体领域 Skills |
| 安全审计 | `security-expertise` + `code-review-expertise` |

---

## 参考资料

- [Domain Expertise Protocol](domain-expertise-protocol.md) - 领域专家化流程
- [Skill Knowledge Base](skills-knowledge-base.md) - Skill 知识库
- [Skill Templates](skill-templates.md) - Skill 模板
- [Official Best Practices](official-best-practices.md) - 官方最佳实践
