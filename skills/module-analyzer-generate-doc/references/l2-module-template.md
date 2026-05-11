# {模块名} - 模块详解

> 模块级业务逻辑索引 - 让非技术人员也能理解模块的核心职责和业务流程

---

## 模块职责

{200-300 字概述模块的业务定位和核心价值}

**示例**（admin-api 模块）:

admin-api 模块是整个管理后台系统的核心 API 服务层，承担着用户认证授权、系统资源配置、组织架构管理、业务数据隔离等关键职责。

作为多租户 SaaS 平台的管控中枢，该模块实现了三层数据隔离机制（运营商→组织→站点），确保不同租户间的数据完全隔离。通过集成 Spring Security + JWT 实现无状态认证，支持 Token 自动续期、并发登录控制、强制踢出等安全特性。

模块提供完整的系统管理功能，包括用户管理、角色授权、菜单配置、字典管理、岗位管理等，支撑平台的日常运维。同时集成 XXL-Job 分布式任务调度、RabbitMQ 消息队列、Apollo 配置中心等中间件，保障系统的可靠性和可扩展性。

---

## 文件索引表

| 文件路径 | 职责简述 | 类型 | 行数 |
|----------|----------|------|------|
| src/main/java/com/.../AuthorizationController.java | 登录认证核心控制器，处理登录、Token 登录、验证码、用户信息、退出等完整认证流程 | Controller | 312 |
| src/main/java/com/.../UserController.java | 系统用户管理控制器，提供用户 CRUD、密码管理、头像上传、邮箱修改等功能 | Controller | 280 |
| src/main/java/com/.../RoleController.java | 系统角色管理控制器，提供角色 CRUD、菜单授权、级别管理、站点授权等功能 | Controller | 210 |
| src/main/java/com/.../DeptServiceImpl.java | 机构管理服务实现，维护树形组织结构，支持增删改查和递归子机构查询 | ServiceImpl | 280 |
| src/main/java/com/.../SpringSecurityConfig.java | Spring Security 核心配置，扫描匿名接口，配置认证授权规则、密码编码器、Token 过滤器 | Config | 156 |
| src/main/java/com/.../TokenProvider.java | JWT Token 生成、验证、续期核心组件，通过 Redis 维护 Token 有效性状态 | Util | 132 |
| ... | ... | ... | ... |

{列出所有已生成 L3 文档的文件，按功能分组排序}

---

## 核心业务流程

### 1. 用户认证授权流程

**参与组件**: AuthorizationController, TokenProvider, TokenFilter, UserDetailsServiceImpl, JwtUserDto

**流程描述**:

1. **登录请求**: 用户在前端输入账号密码，发送 POST 请求到 `/auth/login` 接口

2. **凭证验证**: AuthorizationController 接收请求，调用 UserDetailsServiceImpl 加载用户详情
   - 查询数据库获取用户基本信息
   - 验证密码（使用 PwdUtil 的多轮 SHA-256 加密）
   - 检查用户状态（是否被禁用、过期）

3. **生成 Token**: 验证通过后，TokenProvider 生成 JWT Token
   - 包含用户 ID、用户名、过期时间等 claims
   - 使用密钥签名
   - 将 Token 存入 Redis，设置过期时间

4. **返回响应**: 返回 Token 和用户信息给前端

5. **后续请求认证**: 前端在请求头中携带 Token
   - TokenFilter 拦截请求，解析 Token
   - 验证 Token 有效性（签名、过期时间）
   - 从 Redis 查询 Token 状态（是否被踢出）
   - 建立 Spring Security 认证上下文

6. **Token 续期**: 如果 Token 即将过期但用户仍在活跃使用，自动续期

7. **退出登录**: 用户退出时，从 Redis 删除 Token，使其失效

---

### 2. 数据权限隔离流程（三层隔离）

**参与组件**: MybatisPlusConfig, OrgPermissionHandler, OrgPermissionInterceptor, StationPermissionHandler, StationPermissionInterceptor

**隔离层级**:

```
运营商 (Tenant) → 组织 (Organization) → 站点 (Station)
```

**流程描述**:

1. **运营商级别隔离**:
   - 每个运营商有独立的 tenant_id
   - 所有查询自动添加 `WHERE tenant_id = ?` 过滤
   - 通过 MyBatis-Plus 多租户插件实现

2. **组织级别隔离**:
   - 运营商下可创建多个组织（部门、分公司等）
   - OrgPermissionInterceptor 拦截 SQL 查询
   - OrgPermissionHandler 动态注入 `org_id IN (...)` 过滤条件
   - 用户只能查看所属组织及下级组织的数据

3. **站点级别隔离**:
   - 组织下可管理多个充电站点
   - StationPermissionInterceptor 拦截 SQL 查询
   - StationPermissionHandler 动态注入 `station_id = ?` 过滤条件
   - 站点管理员只能查看该站点的数据

**实现机制**:
- 使用 MyBatis-Plus 的拦截器机制
- 在 SQL 执行前动态修改 WHERE 条件
- 无需在业务代码中手动添加过滤逻辑
- 保证数据隔离的一致性和安全性

---

### 3. 系统管理功能流程

**参与模块**:
- 用户管理：UserController, UserDetailsServiceImpl
- 角色管理：RoleController, RoleServiceImpl
- 菜单管理：MenuController, MenuServiceImpl
- 字典管理：DictController, DictDetailController
- 机构管理：DeptController, DeptServiceImpl

**典型流程 - 创建用户**:

1. 管理员在前端填写用户信息（用户名、密码、所属组织、角色等）
2. 调用 `POST /api/user` 接口
3. UserController 接收请求，验证数据合法性
   - 检查用户名是否重复
   - 验证密码强度
   - 确认所属组织存在
   - 验证角色 ID 有效
4. 调用 UserService 创建用户
   - 密码加密（PwdUtil）
   - 生成用户 ID
   - 插入数据库
   - 记录操作日志
5. 返回创建结果

---

## MyBatis 映射关系

### 核心表映射

| 表名 | 对应 Mapper | 主要操作 |
|------|-------------|----------|
| sys_user | UserMapper | 用户 CRUD、登录查询、组织过滤 |
| sys_role | RoleMapper | 角色 CRUD、菜单授权、用户关联 |
| sys_menu | MenuMapper | 菜单 CRUD、树形查询、角色授权 |
| sys_dept | DeptMapper | 机构 CRUD、树形查询、递归子机构 |
| sys_dict | DictMapper | 字典类型 CRUD、全量查询 |
| sys_dict_detail | DictDetailMapper | 字典子项 CRUD、批量查询 |
| sys_job | JobMapper | 岗位 CRUD、用户关联查询 |
| sys_log | LogMapper | 操作日志记录、查询、导出 |

### MyBatis-Plus 特性使用

- **自动填充**: MybatisPlusFillMetaObjectHandler 自动填充 createTime、createBy、updateTime
- **逻辑删除**: 使用 deleted 字段标记删除，查询自动过滤
- **乐观锁**: 使用 version 字段实现乐观锁
- **分页插件**: 自动处理分页查询

---

## 模块依赖

### 内部依赖

| 依赖模块 | 依赖关系 | 说明 |
|----------|----------|------|
| ces-domain | 被依赖 | 核心领域模型定义 |
| common-util | 被依赖 | 通用工具类 |
| common-security | 被依赖 | 安全认证基础组件 |

### 外部服务

| 服务 | 用途 | 配置项 |
|------|------|--------|
| MySQL | 主数据库，存储业务数据 | spring.datasource |
| Redis | 缓存用户会话、Token、验证码 | spring.redis |
| Apollo | 配置中心，动态管理配置 | app.id, apollo.meta |
| RabbitMQ | 消息队列，异步处理标签、保险通知 | spring.rabbitmq |
| XXL-Job | 分布式任务调度 | xxl.job.admin.addresses |

### 框架依赖

| 框架 | 版本 | 用途 |
|------|------|------|
| Spring Boot | 2.x | 基础框架 |
| Spring Security | 5.x | 认证授权 |
| MyBatis-Plus | 3.4.x | ORM 框架 |
| JWT (jjwt) | 0.9.x | Token 生成验证 |
| Lombok | 1.18.x | 简化代码 |

---

## 配置项汇总

### JWT 配置 (jwt)

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| jwt.header | Authorization | Token 请求头名称 |
| jwt.secret | xxx | JWT 签名密钥 |
| jwt.tokenHead | Bearer | Token 前缀 |
| jwt.tokenExpireTime | 7 天 | Token 过期时间 |
| jwt.tokenRenewTime | 24 小时 | Token 续期间隔 |

### 登录配置 (login)

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| login.code | true | 是否启用验证码 |
| login.codeType | png | 验证码图片类型 |
| login.loginType | username | 登录方式（username/sms） |
| login.cacheTime | 5 分钟 | 验证码有效期 |

### MyBatis-Plus 配置

| 配置项 | 说明 |
|--------|------|
| mapper-locations | Mapper XML 文件路径 |
| type-aliases-package | 实体类包路径 |
| global-config.db-config | 全局数据库配置（逻辑删除、主键策略等） |

### XXL-Job 配置

| 配置项 | 说明 |
|--------|------|
| xxl.job.admin.addresses | 调度中心地址 |
| xxl.job.executor.appname | 执行器名称 |
| xxl.job.executor.port | 执行器端口 |

### RabbitMQ 配置

| 配置项 | 说明 |
|--------|------|
| spring.rabbitmq.host | RabbitMQ 服务器地址 |
| spring.rabbitmq.port | 端口 |
| spring.rabbitmq.username/password | 认证信息 |
| spring.rabbitmq.listener.simple | 消费者配置 |

---

## 技术栈

### 后端框架

- Spring Boot 2.x - 快速开发框架
- Spring MVC - Web 框架
- Spring Security - 安全认证
- Spring AOP - 切面编程（日志记录）

### 持久层

- MyBatis-Plus 3.4.x - ORM 框架
- MySQL 8.0 - 关系型数据库
- Redis - 缓存、会话管理

### 认证授权

- JWT (jjwt) - Token 认证
- Spring Security - 权限控制
- BCrypt/SHA-256 - 密码加密

### 微服务组件

- Apollo - 配置中心
- Dubbo - RPC 框架
- OpenFeign - 声明式 HTTP 客户端
- Nacos/Eureka - 服务发现（可选）

### 消息队列

- RabbitMQ - 异步消息处理

### 任务调度

- XXL-Job - 分布式任务调度

### 工具库

- Lombok - 简化代码
- Hutool - 通用工具类
- FastJSON/Jackson - JSON 处理
- Swagger/Knife4j - API 文档

---

## 文档覆盖状态

| 类型 | 总数 | 已生成文档 | 覆盖率 |
|------|------|------------|--------|
| Controller | 15 | 15 | 100% |
| Service/ServiceImpl | 18 | 11 | 61% |
| Config | 14 | 14 | 100% |
| Handler/Interceptor | 8 | 8 | 100% |
| Util | 4 | 4 | 100% |
| DTO/Entity | 21 | 0 | 0% (按规则跳过) |
| **总计** | **80** | **52** | **65%** |

**说明**: DTO/Entity 类按规则跳过（纯数据对象，无业务逻辑）

---

*Generated on {日期}*
