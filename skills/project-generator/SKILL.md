---
name: project-generator
description: Automatically transform requirement documents or natural language descriptions into complete full-stack projects (Java backend + Vue frontend) with MANDATORY interactive tech stack selection. Supports database schema design, REST API generation, CRUD operations, user authentication, and project scaffolding. ⚠️ TECH STACK SELECTION IS MANDATORY - Users MUST explicitly select or confirm each option, cannot skip by pressing Enter. Use when: (1) Converting PRD/requirements into working code, (2) Rapid prototyping of web applications, (3) Generating boilerplate projects from descriptions, (4) Bootstrapping CRUD applications, (5) Creating MVP projects from text specifications.
---

# Project Generator Skill

Transform requirement documents or natural language descriptions into complete, production-ready full-stack applications with **MANDATORY** customizable tech stack selection.

⚠️ **IMPORTANT: Tech stack selection is MANDATORY. Users cannot skip this step by pressing Enter. Each option must be explicitly selected or confirmed.**

## Capabilities

This skill generates:
- **Backend**: Java Spring Boot with proper layering (Controller, Service, Repository, Entity)
- **Frontend**: Vue 3 + TypeScript + UI component library
- **Database**: Entities with relationships, migration scripts
- **API**: RESTful endpoints with OpenAPI/Swagger docs
- **Authentication**: JWT-based auth (optional)
- **Documentation**: README, API docs, setup instructions

## Interactive Tech Stack Selection

Before generating the project, the skill will guide you through selecting your preferred technology stack.

### Selection Modes

#### Mode 1: Quick Selection (Mandatory)

⚠️ **此模式为强制模式，用户必须输入选择，不能回车跳过。**

Use numbered options for rapid selection:
```
【后端】
1. Java:      [1]8 [2]11 [3]17 [4]21
2. SpringBoot:[1]2.7 [2]3.0 [3]3.2
3. Build:     [1]Maven [2]Gradle
4. Database:  [1]MySQL5.7 [2]MySQL8.0 [3]PostgreSQL [4]H2
5. ORM:       [1]JPA [2]MyBatis [3]MyBatis-Plus
...

【前端】
1. Vue:       [1]2 [2]3
2. UI:        [1]ElementUI(Vue2) [2]ElementPlus(Vue3) [3]AntDV [4]NaiveUI
3. State:     [1]Pinia(Vue3) [2]Vuex
...

⚠️ 必须输入完整选择，格式: 1,1,1,1,3,1,2,2,1
```
```

#### Mode 2: Free-form Text Input

Directly specify technology and version in natural language:

**Examples:**
> "Java 8, Spring Boot 2.7, MySQL 5.7, MyBatis-Plus, Redis"

> "JDK17 + SpringBoot 3.2 + PostgreSQL 15 + JPA + RabbitMQ"

> "Vue3 + TypeScript + Element Plus + Pinia + Tailwind"

> "React 18 + JavaScript + Ant Design + Zustand"

⚠️ **注意:** 如果自由格式输入未包含所有必要选项，系统仍会**强制提示**用户补充选择剩余选项。

**Supported Input Formats:**
- Technology name + version: `Java 8`, `Vue 3`, `MySQL 5.7`
- Short names: `JDK8`, `SB2.7`, `Vue2`, `React18`, `TS`
- With connectors: `+`, `,`, `/`, `and`
- Multiple lines or bullet points

### Selection Flow (Mandatory)

⚠️ **技术栈选择是强制性的，不能跳过。**

```
1. Requirement Description (REQUIRED)
   ├─ User describes project requirements
   ├─ Skill analyzes and understands the needs
   └─ Summarizes core features
        ↓
2. Present Tech Stack Options (MANDATORY)
   ├─ Display all options with recommendations
   ├─ Provide suggestions based on requirements
   └─ Wait for user input
        ↓
3. User Selects Preferences (REQUIRED)
   ├─ User enters selection numbers
   ├─ Or confirms recommendations
   └─ Re-prompt if input is empty
        ↓
4. Generate Project with Selected Stack
```

### Phase 1: Requirement Description

⚠️ **用户必须首先描述项目需求。**

**Acceptable Inputs:**
- 自然语言描述: "创建一个电商订单管理系统"
- 功能列表: "用户管理、商品管理、订单管理"
- PRD文档: 上传需求文档
- 简要描述: "一个简单的博客系统"

**Requirements for Description:**
- 项目名称（可选）
- 核心功能模块
- 业务场景描述
- 技术偏好（可选，如已知）

**Example:**
> "创建一个用户管理系统，包含用户注册登录、用户信息管理、角色权限分配功能。使用Java开发，前端用Vue。"

### Backend Options

#### 1. Java Version
| # | Version | Description |
|---|---------|-------------|
| 1 | Java 8 | Legacy support, widely used |
| 2 | Java 11 | LTS version |
| 3 | Java 17 | Default LTS version, stable |
| 4 | Java 21 | Latest LTS, virtual threads |

#### 2. Spring Boot Version
| # | Version | Description |
|---|---------|-------------|
| 1 | 2.7.x | Compatible with Java 8/11 |
| 2 | 3.0.x | Requires Java 17+ |
| 3 | 3.2.x | Default, latest features |

#### 3. Build Tool
| # | Tool | Description |
|---|------|-------------|
| 1 | Maven | Default, widely used |
| 2 | Gradle | Faster builds, flexible |

#### 4. Database
| # | Database | Description |
|---|----------|-------------|
| 1 | MySQL 5.7 | Legacy stable version |
| 2 | MySQL 8.0 | Default, latest features |
| 3 | PostgreSQL | Advanced features, robust |
| 4 | H2 | In-memory, for development |

#### 5. Data Access
| # | Framework | Description |
|---|-----------|-------------|
| 1 | JPA/Hibernate | Default, rapid development |
| 2 | MyBatis | SQL control, complex queries |
| 3 | MyBatis-Plus | Enhanced MyBatis, CRUD shortcuts |

#### 5. Additional Features (Multi-select)
| # | Feature | Description |
|---|---------|-------------|
| 1 | JWT Authentication | Token-based security |
| 2 | Redis Cache | Performance caching |
| 3 | Audit Logging | Track data changes |
| 4 | Soft Delete | Logical deletion |
| 5 | Multi-tenant | Multiple organizations |
| 6 | File Upload | File storage support |
| 7 | Excel Export | Data export functionality |

### Frontend Options

#### 1. Vue Version
| # | Version | Description |
|---|---------|-------------|
| 1 | Vue 2 | Legacy, stable |
| 2 | Vue 3 | Default, latest features, Composition API |

#### 2. UI Component Library
| # | Library | Description |
|---|---------|-------------|
| 1 | Element UI | For Vue 2, mature |
| 2 | Element Plus | For Vue 3, default, rich components |
| 3 | Ant Design Vue | Enterprise UI design |
| 4 | Naive UI | Modern, TypeScript friendly |

#### 3. State Management
| # | Tool | Description |
|---|------|-------------|
| 1 | Pinia | For Vue 3, default |
| 2 | Vuex | For Vue 2/Vue 3, legacy style |

#### 4. Additional Features (Multi-select)
| # | Feature | Description |
|---|---------|-------------|
| 1 | Dark Mode | Theme switching |
| 2 | i18n | Internationalization |
| 3 | PWA | Progressive Web App |
| 4 | Responsive Design | Mobile adaptation |

## Input Formats

Accepted inputs:
- Natural language description (e.g., "创建一个用户管理系统")
- PRD (Product Requirements Document)
- Markdown requirements
- Feature list
- User stories

⚠️ **IMPORTANT:** After requirement input, the skill WILL ALWAYS prompt for tech stack selection. This step is MANDATORY and cannot be skipped.

## Workflow

### Phase 1: Requirement Description (REQUIRED)

⚠️ **第一步：用户必须首先描述项目需求。**

**输入要求:**
- 项目名称（可选）
- 核心功能模块描述
- 业务场景说明
- 技术偏好（如有）

**示例:**
```
👤 用户: 创建一个用户管理系统

🤖 系统: 收到需求！分析结果：
   📋 项目类型: 用户管理系统
   🔧 核心功能: 用户注册/登录、用户信息管理、角色权限分配
   💡 推荐技术栈: Java + Spring Boot + Vue3
   
   接下来请配置具体的技术栈...
```

### Phase 2: Tech Stack Selection (MANDATORY)

⚠️ **第二步：根据需求选择技术栈（强制性，不能跳过）**

根据需求分析结果，呈现技术栈选项：

Example interaction:
```
🛠️ 请根据您的需求选择技术栈:

【后端配置 - 请选择】
1. Java 版本: [1]8  [2]11  [3]17  [4]21 → 请输入: ___
2. Spring Boot: [1]2.7  [2]3.0  [3]3.2 → 请输入: ___
3. 构建工具: [1]Maven  [2]Gradle → 请输入: ___
4. 数据库: [1]MySQL5.7  [2]MySQL8.0  [3]PostgreSQL  [4]H2 → 请输入: ___
5. 数据访问: [1]JPA  [2]MyBatis  [3]MyBatis-Plus → 请输入: ___
6. 附加功能 (多选): [1]JWT [2]Redis [3]审计日志 [4]软删除 → 请输入: ___

【前端配置 - 请选择】
1. Vue 版本: [1]Vue2  [2]Vue3 → 请输入: ___
2. UI 组件库: [1]Element UI(Vue2) [2]Element Plus(Vue3) [3]Ant Design Vue [4]Naive UI → 请输入: ___
3. 状态管理: [1]Pinia(Vue3) [2]Vuex → 请输入: ___
4. 附加功能 (多选): [1]暗黑模式 [2]国际化 [3]PWA → 请输入: ___

⚠️ 请完整输入所有选项 (如: 1,1,1,1,3,1,2,2,1,12)
```
3. 构建工具: [1]Maven  [2]Gradle → 请输入: ___
4. 数据库: [1]MySQL5.7  [2]MySQL8.0  [3]PostgreSQL  [4]H2 → 请输入: ___
5. 数据访问: [1]JPA  [2]MyBatis  [3]MyBatis-Plus → 请输入: ___
6. 附加功能 (多选，如: 12): [1]JWT [2]Redis [3]审计日志 [4]软删除 → 请输入: ___

【前端配置 - 请选择】
1. Vue 版本: [1]Vue2  [2]Vue3 → 请输入: ___
2. UI 组件库: [1]Element UI(Vue2) [2]Element Plus(Vue3) [3]Ant Design Vue [4]Naive UI → 请输入: ___
3. 状态管理: [1]Pinia(Vue3) [2]Vuex → 请输入: ___
4. 附加功能 (多选，如: 12): [1]暗黑模式 [2]国际化 [3]PWA → 请输入: ___

⚠️ 请完整输入所有选项 (如: 1,1,1,1,3,1,2,2,1,12)
```

### Phase 3: Database Design
1. Design entity-relationship model based on requirements
2. Generate appropriate DDL/scripts based on selected database
3. Create migration scripts (Flyway for JPA, or custom for MyBatis)

### Phase 4: Backend Generation
1. Generate build configuration (pom.xml or build.gradle) with selected stack
2. Create application.yml with correct database settings
3. Generate entity classes (JPA annotations or MyBatis mappers)
4. Create DTOs and mappers
5. Implement service layer with business logic
6. Build REST controllers
7. Add selected features (JWT, Redis, audit, etc.)

### Phase 5: Frontend Generation
1. Generate package.json with selected UI library
2. Configure Vite and project setup
3. Generate API client from backend
4. Create Vue components with selected UI library
5. Build routing configuration
6. Implement state management
7. Add selected features (dark mode, i18n, etc.)

### Phase 6: Project Setup
1. Generate Docker configurations
2. Create docker-compose.yml with selected database
3. Write CI/CD templates
4. Create setup documentation

## Project Structure Output

```
generated-project/
├── backend/                    # Spring Boot application
│   ├── src/main/java/
│   │   └── com/example/
│   │       ├── config/         # Configurations (CORS, Security, etc.)
│   │       ├── controller/     # REST controllers
│   │       ├── service/        # Business logic
│   │       ├── repository/     # Data access (JPA/MyBatis/MyBatis-Plus)
│   │       ├── entity/         # Entity classes
│   │       ├── dto/            # Data transfer objects
│   │       ├── mapper/         # Entity-DTO mappers
│   │       ├── security/       # JWT/auth (if selected)
│   │       └── aspect/         # Audit logging (if selected)
│   ├── src/main/resources/
│   │   ├── db/migration/       # Flyway scripts
│   │   ├── mapper/             # MyBatis XML (if selected)
│   │   └── application.yml     # Configured for selected database
│   └── pom.xml / build.gradle  # Based on selected build tool
├── frontend/                   # Vue application
│   ├── src/
│   │   ├── api/                # API client
│   │   ├── components/         # Reusable components
│   │   ├── views/              # Page views
│   │   ├── stores/             # Pinia/Vuex stores
│   │   ├── router/             # Vue Router
│   │   ├── locales/            # i18n files (if selected)
│   │   ├── types/              # TypeScript types (Vue 3)
│   │   └── App.vue             # Root component
│   ├── package.json            # Vue 2 or Vue 3 with selected UI library
│   └── vite.config.ts / vue.config.js  # Vite (Vue 3) or Vue CLI (Vue 2)
├── docker-compose.yml          # With selected database (MySQL 5.7/8.0/PostgreSQL)
└── README.md                   # Setup instructions for selected stack
```

## Usage Examples

### Example 1: Standard Flow - Describe then Select

**Step 1: 描述需求**
```
👤 用户: 创建一个用户管理系统

🤖 系统: 收到需求！分析结果：
   📋 项目类型: 用户管理系统
   🔧 核心功能: 用户注册/登录、用户信息管理、角色权限控制
   💡 推荐技术栈: Java + Spring Boot + Vue3
   
   接下来请配置具体的技术栈...
```

**Step 2: 选择技术栈（强制）**
```
👤 用户: 1,1,1,1,3,1,2,2,1,1
        (Java8+SpringBoot2.7+MySQL5.7+MyBatis-Plus+JWT / Vue3+ElementPlus+Pinia+暗黑模式)

🤖 系统: 配置确认完成，正在生成项目...
```

**Process:**
1. 用户提供需求描述（**必须先描述**）
2. 系统分析需求并推荐技术栈
3. 用户必须选择技术栈（**强制，不能跳过**）
4. 根据需求+技术栈生成项目

### Example 2: Custom Tech Stack

**Input:**
> "创建一个电商管理系统，Java 21，Gradle，PostgreSQL"

**Process:**
1. Skill detects preferences from description
2. Presents remaining options
3. Generates with specified stack

### Example 3: Upload PRD

**Input:**
> "读取这个需求文档并生成项目"

**Process:**
1. Parse uploaded PRD
2. Present tech stack options
3. Generate based on requirements + selected stack

### Example 4: Free-form Tech Stack Input (NEW)

**Input:**
> "用 Java 8 + Spring Boot 2.7 + MySQL 5.7 + MyBatis-Plus + Redis"

**Or:**
> "后端：JDK17, SpringBoot3.2, PostgreSQL, JPA, Kafka\n前端：Vue3, TS, ElementPlus, Pinia, Tailwind"

**Or:**
> "Vue2 + Element UI + JavaScript + Vuex，后端用 Java11 + SpringBoot2.7 + MyBatis"

**Process:**
1. Parse free-form text to extract technologies and versions
2. Map to available options or use custom versions
3. Confirm parsed selection
4. Generate with specified stack

**Supported Keywords:**
- **Java**: `Java 8`, `Java 11`, `JDK11`, `Java17`, `JDK 21`
- **Spring Boot**: `SpringBoot 2.7`, `SB 2.7`, `SB 3.2`, `Spring Boot 3.x`
- **Database**: `MySQL 5.7`, `MySQL8`, `PostgreSQL 15`, `Oracle`, `SQL Server`
- **ORM**: `JPA`, `Hibernate`, `MyBatis`, `MyBatis-Plus`, `MP`
- **Cache**: `Redis`, `Caffeine`, `Ehcache`
- **MQ**: `RabbitMQ`, `Kafka`, `RocketMQ`
- **Frontend**: `Vue2`, `Vue 3`, `React 18`, `Angular`
- **UI**: `Element UI`, `Element Plus`, `Ant Design Vue`, `AntDV`, `Naive UI`, `Vuetify`
- **State**: `Pinia`, `Vuex`, `Redux`, `Zustand`
- **CSS**: `Tailwind`, `SCSS`, `Less`, `CSS`
- **Language**: `TypeScript`, `TS`, `JavaScript`, `JS`

## Generated Configurations by Stack

### Backend Configurations

#### MySQL + JPA (application-mysql.txt → rename to application.yml)
```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/${projectName}?useSSL=false&serverTimezone=UTC
    username: root
    password: password
    driver-class-name: com.mysql.cj.jdbc.Driver
  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: true
  flyway:
    enabled: true
    locations: classpath:db/migration
```

#### PostgreSQL + JPA (application-postgres.txt → rename to application.yml)
```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/${projectName}
    username: postgres
    password: password
    driver-class-name: org.postgresql.Driver
  jpa:
    database-platform: org.hibernate.dialect.PostgreSQLDialect
```

#### MyBatis Configuration
```yaml
mybatis:
  mapper-locations: classpath:mapper/*.xml
  type-aliases-package: com.example.entity
```

### Frontend Configurations

#### Element Plus (package-element.txt → rename to package.json)
```json
{
  "dependencies": {
    "element-plus": "^2.5.0",
    "@element-plus/icons-vue": "^2.3.0"
  }
}
```

#### Ant Design Vue (package-antd.txt → rename to package.json)
```json
{
  "dependencies": {
    "ant-design-vue": "^4.0.0",
    "@ant-design/icons-vue": "^7.0.0"
  }
}
```

### Build Tool Configurations

#### Maven (pom.txt → rename to pom.xml) - Java 17 vs 21
```xml
<!-- Java 17 -->
<properties>
    <java.version>17</java.version>
    <maven.compiler.source>17</maven.compiler.source>
    <maven.compiler.target>17</maven.compiler.target>
</properties>

<!-- Java 21 -->
<properties>
    <java.version>21</java.version>
    <maven.compiler.source>21</maven.compiler.source>
    <maven.compiler.target>21</maven.compiler.target>
</properties>
```

#### Gradle (build.txt → rename to build.gradle) - Java 17 vs 21
```groovy
// Java 17
sourceCompatibility = '17'
targetCompatibility = '17'

// Java 21
sourceCompatibility = '21'
targetCompatibility = '21'
```

## Assets Reference

### Project Templates

- `assets/templates/spring-boot/` - Spring Boot templates
  - `pom-java8.txt` / `pom-java11.txt` / `pom-java17.txt` / `pom-java21.txt` (rename to pom.xml when using)
  - `build-java8.txt` / `build-java11.txt` / `build-java17.txt` / `build-java21.txt` (rename to build.gradle when using)
  - `application-mysql57.txt` / `application-mysql8.txt` / `application-postgres.txt` (rename to .yml when using)
  - `mybatis-plus-config.txt` (MyBatis-Plus configuration)
  - `application-h2.txt`
- `assets/templates/vue-vite/` - Vue 3 + Vite templates
  - `package-element.txt` (rename to package.json when using) - Element Plus
  - `package-antd.txt` (rename to package.json when using) - Ant Design Vue
  - `package-naive.txt` (rename to package.json when using) - Naive UI
- `assets/templates/vue-cli/` - Vue 2 + Vue CLI templates
  - `package-element-ui-vue2.txt` (rename to package.json when using) - Element UI
- `assets/templates/docker/` - Docker configurations
  - `docker-compose-mysql57.txt` (rename to .yml when using) - MySQL 5.7
  - `docker-compose-mysql8.txt` (rename to .yml when using) - MySQL 8.0
  - `docker-compose-postgres.txt` (rename to .yml when using)

### Code Generators

- `scripts/generate-backend.py` - Generate Java backend with stack options
- `scripts/generate-frontend.py` - Generate Vue frontend with UI library selection
- `scripts/generate-database.py` - Generate schema for selected database

### Component Library Presets

- `assets/ui-presets/element-plus.json` - Element Plus component templates
- `assets/ui-presets/ant-design.json` - Ant Design Vue component templates
- `assets/ui-presets/naive-ui.json` - Naive UI component templates

## Best Practices

1. **Review tech stack choices** - Consider team expertise and project requirements
2. **Start with defaults** - Use proven combinations for quick prototyping
3. **Database choice matters** - MySQL for simple apps, PostgreSQL for complex queries
4. **ORM selection** - JPA for rapid dev, MyBatis for SQL control
5. **Security** - Enable JWT for production applications
6. **Test locally** - Use docker-compose for immediate testing

## Troubleshooting

### Database Connection Issues
- Verify selected database is running
- Check credentials in application.yml
- For H2: ensure `spring.datasource.url` uses correct mem/file path

### Build Failures
- Ensure correct Java version is installed (17 or 21)
- For Gradle: check gradle wrapper version compatibility
- Verify Maven/Gradle can access dependencies

### Frontend UI Issues
- Ensure selected UI library version is compatible with Vue 3
- Check if component imports match selected library
- Verify CSS preprocessor settings if using custom themes

## References

- [Spring Boot Documentation](https://docs.spring.io/spring-boot/docs/current/reference/html/)
- [Vue 3 Guide](https://vuejs.org/guide/)
- [Element Plus](https://element-plus.org/)
- [Ant Design Vue](https://antdv.com/)
- [Naive UI](https://www.naiveui.com/)
- [MyBatis Spring Boot](https://mybatis.org/spring-boot-starter/)
- [Flyway Documentation](https://documentation.red-gate.com/flyway/)
