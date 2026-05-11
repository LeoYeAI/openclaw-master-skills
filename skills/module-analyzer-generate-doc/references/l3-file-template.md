# {类名} - 业务逻辑详解

> 文件级业务逻辑文档 - 让非程序开发者能对照源代码了解代码业务内容

---

## 基本信息

| 字段 | 值 |
|------|-----|
| **文件路径** | `{relativePath}` |
| **行数** | {lines} |
| **文件类型** | {Config/Controller/Service/ServiceImpl/Interceptor/Handler/Util} |
| **所属模块** | {moduleName} |
| **关联文件** | {MyBatis 映射的 XML/Java 文件，如有} |

---

## 业务职责

{用自然语言描述这个类的业务职责，200-300 字，非技术人员也能理解}

**写作要点**:
- 这个类是做什么的？解决什么业务问题？
- 在系统中扮演什么角色？
- 谁会在什么时候使用它？
- 它如何与其他组件协作？

**示例**（TokenProvider）:

TokenProvider 是整个认证系统的核心组件，负责 JWT Token 的创建、验证、续期等全生命周期管理。

当用户登录成功后，系统需要生成一个"身份凭证"（Token）返回给用户，用户后续每次请求都携带这个凭证来证明身份。TokenProvider 就是这个凭证的"签发机构"和"验证机构"。

它不仅要生成安全的 Token（包含用户信息、过期时间、数字签名），还要能够验证 Token 的真伪（是否被篡改、是否过期），并且在 Token 即将过期但用户仍在活跃使用时自动续期，提升用户体验。

为了支持"强制退出"功能，TokenProvider 还与 Redis 配合，将 Token 的状态存储在 Redis 中，即使 Token 本身未过期，也可以从 Redis 中将其标记为无效，实现立即踢出用户的效果。

---

## 核心业务逻辑

### {功能点 1：方法/业务场景名称}

**触发条件**: {什么时候会执行这段逻辑？}

**输入数据**: {接收什么数据？数据来源？}

**业务规则**: {需要验证哪些业务规则？}

**处理流程**:
1. {第一步做什么}
2. {第二步做什么}
3. {第三步做什么}
4. ...

**输出结果**: {返回什么数据？数据去向？}

**异常情况**: {可能出现什么异常？如何处理？}

---

**示例**（TokenProvider 的 createToken 方法）:

**触发条件**: 用户登录成功，需要生成 Token 返回给前端

**输入数据**: 
- 用户 ID（Long 类型）
- 用户名（String 类型）
- 用户角色列表（List<String>类型）

**业务规则**:
- Token 必须包含用户身份信息
- Token 必须有明确的过期时间
- Token 必须有数字签名防止篡改
- Token 生成后需要记录到 Redis 用于状态管理

**处理流程**:
1. 创建 JWT 构建器，设置签名算法为 HS512
2. 添加 Token 主题（subject）为用户 ID
3. 添加签发时间为当前时间
4. 添加过期时间为当前时间 + 配置的天数（默认 7 天）
5. 添加自定义 claims：用户名、角色列表
6. 使用密钥进行签名
7. 生成紧凑的 JWT 字符串
8. 将 Token 和用户 ID 的映射关系存入 Redis，设置过期时间
9. 返回生成的 Token 字符串

**输出结果**: 
- JWT Token 字符串（String 类型），格式为 `header.payload.signature`

**异常情况**:
- 密钥为空：抛出配置错误异常
- Redis 连接失败：记录错误日志，Token 仍可生成但无法支持踢出功能

---

### {功能点 2：方法/业务场景名称}

**触发条件**: {...}

**输入数据**: {...}

**业务规则**: {...}

**处理流程**:
1. {...}
2. {...}
3. {...}

**输出结果**: {...}

**异常情况**: {...}

---

**示例**（TokenProvider 的 validateToken 方法）:

**触发条件**: 收到前端请求，需要验证请求头中的 Token 是否有效

**输入数据**: 
- JWT Token 字符串（从 HTTP 请求头 Authorization 中提取）

**业务规则**:
- Token 签名必须正确（未被篡改）
- Token 不能过期
- Token 在 Redis 中必须存在（未被踢出）

**处理流程**:
1. 使用密钥创建 JWT 解析器
2. 解析 Token 字符串，验证签名
3. 如果签名验证失败，抛出 JwtException，返回 false
4. 如果解析成功，获取 Token 中的过期时间 claims
5. 比较过期时间和当前时间，如果已过期，返回 false
6. 从 Redis 中查询该 Token 是否存在
7. 如果 Redis 中不存在（已被踢出或删除），返回 false
8. 所有验证通过，返回 true

**输出结果**: 
- boolean 值，true 表示 Token 有效，false 表示无效

**异常情况**:
- Token 格式错误：捕获 MalformedJwtException，返回 false
- Token 已过期：捕获 ExpiredJwtException，返回 false
- 密钥错误：捕获 SignatureException，返回 false
- Redis 连接失败：记录日志，根据配置决定是拒绝还是放行

---

## 业务流程

{描述该方法/类与其他类之间的调用关系和业务流转过程}

**示例**（TokenProvider 在认证流程中的位置）:

```
用户登录 → AuthorizationController.login()
         ↓
         UserDetailsServiceImpl.loadUserByUsername()
         ↓ (验证成功)
         TokenProvider.createToken()
         ↓
         返回 Token 给前端
         
用户请求 → TokenFilter.doFilter()
         ↓
         TokenProvider.validateToken()
         ↓ (验证成功)
         建立 SecurityContext
         ↓
         放行到 Controller
```

---

## 数据交互

### 数据库交互

{描述与数据库的交互，如查询用户信息、更新 Token 状态等}

**示例**:
- 不直接操作数据库
- 通过 Redis 管理 Token 状态

### Redis 交互

| 操作 | Key 格式 | Value | 过期时间 | 说明 |
|------|----------|-------|----------|------|
| 存储 | token:{tokenValue} | userId | 同 Token 过期时间 | 记录 Token 有效性 |
| 查询 | token:{tokenValue} | - | - | 验证 Token 是否被踢出 |
| 删除 | token:{tokenValue} | - | - | 用户退出时删除 |

### 外部服务交互

{描述与外部服务的交互，如发送短信、调用第三方 API 等}

---

## 依赖关系

### 依赖的类/组件

| 依赖项 | 用途 |
|--------|------|
| LoginProperties | 读取登录配置（Token 过期时间等） |
| SecurityProperties | 读取安全配置（密钥等） |
| RedisTemplate | Redis 操作 |
| Claims | JWT claims 对象 |
| Jwts | JWT 工具类 |

### 被谁依赖

| 依赖方 | 依赖方式 |
|--------|----------|
| AuthorizationController | 调用 createToken() 生成 Token |
| TokenFilter | 调用 validateToken() 验证 Token |
| OnlineUserServiceImpl | 调用 Redis 操作方法踢出用户 |

---

## 设计意图

### 为什么这样设计？

**问题背景**: 
- 传统的 Session 认证需要服务器存储大量 Session 数据
- 在分布式环境下 Session 共享复杂
- 需要支持移动端、多端登录

**解决方案**:
- 使用 JWT 实现无状态认证
- Token 自包含用户信息，减少数据库查询
- 配合 Redis 实现灵活的 Token 管理（续期、踢出）

### 关键设计决策

1. **为什么 Token 要存 Redis？**
   - JWT 本身无法主动失效，一旦签发只能等到过期
   - 存 Redis 后可以随时删除，实现"强制退出"
   - 可以查询在线用户列表

2. **为什么支持 Token 续期？**
   - 提升用户体验，避免频繁登录
   - 用户活跃时自动续期，不活跃时自动过期
   - 平衡安全性和便利性

3. **为什么使用 HS512 签名算法？**
   - 对称加密，性能好
   - 512 位，安全性高
   - 业界标准，广泛支持

---

## 变更历史

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|----------|------|
| 2026-03-07 | 1.0 | 初始生成 | AI Agent |

---

*Generated on {日期} • Module Analyzer Generate Doc Skill*
