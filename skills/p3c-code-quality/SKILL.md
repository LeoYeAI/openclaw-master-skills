---
name: "p3c-code-quality"
description: "执行代码质量检查测试，基于阿里巴巴 P3C 规范对代码进行全面检查，包括命名规范、异常处理、并发安全、数据库规范、OOP 规范、安全规约和单元测试规范。Invoke when user needs to verify code quality against P3C standards."
version: "1.0.0"
p3c_version: "《阿里巴巴 Java 开发手册》2022 版"
last_updated: "2026-03-11"
author: "赵辉亮"
---

# P3C代码质量检查测试

本技能基于阿里巴巴Java开发手册P3C规范，对代码进行全面的质量检查测试。

## 测试范围

本测试技能涵盖以下P3C规范领域：

### 1. 代码风格规范 (p3c-coding-style)
- 命名风格：类名、方法名、变量名、常量命名规范
- 代码格式：大括号、缩进、空格、行长度等格式规范
- 常量定义：魔法值、Long类型、常量分类
- 注释规约：Javadoc规范、注释语言、注释同步更新

### 2. 异常与日志规范 (p3c-exception-logging)
- 异常处理：异常捕获原则、异常处理要求、NPE防护
- 日志规约：日志框架、日志保存、日志输出、日志级别

### 3. 高级编程规范 (p3c-advanced-coding)
- 集合处理：hashCode和equals、subList使用、集合转数组、foreach循环
- 并发处理：线程池、锁性能、死锁预防、并发更新
- 控制语句：switch语句、大括号使用、if-else优化

### 4. MySQL数据库规范 (p3c-mysql-database)
- 建表规约：字段要求、表名要求、索引命名
- SQL语句规约：count使用、in操作、分页查询
- 索引规约：唯一索引、join限制、索引长度
- ORM映射规约：查询字段、参数绑定、事务管理

### 5. OOP编程规范 (p3c-oop-standards)
- 方法覆写：@Override注解、equals方法、包装类比较
- 序列化：serialVersionUID、toString方法
- 访问控制：类成员访问控制、final关键字使用

### 6. 安全规约 (p3c-security-rules)
- 权限控制：水平权限校验、数据脱敏
- SQL注入防护：参数绑定、字符串拼接
- XSS/CSRF防护：安全过滤、防重放限制
- 参数验证：有效性验证、防刷策略

### 7. 单元测试规范 (p3c-unit-testing)
- AIR原则：自动化、独立性、可重复性
- 测试粒度：方法级别测试、核心业务测试
- 测试覆盖率：语句覆盖率、分支覆盖率
- BCDE原则：边界值、正确输入、设计文档、错误输入

## 使用时机

- 功能开发完成后
- 需求变更后
- Bug修复后
- 回归测试
- 代码提交前

## 执行方式

本技能使用 Trae IDE 内置工具进行代码质量检查，无需额外脚本：

### 基本测试流程
1. **查找 Java 文件**：使用 `Glob` 工具查找所有 `.java` 文件
2. **读取代码内容**：使用 `Read` 工具读取文件内容
3. **代码结构分析**：使用 `SearchCodebase` 进行代码结构分析
4. **获取编译诊断**：使用 `GetDiagnostics` 获取编译错误和警告
5. **正则匹配检查**：使用 `Grep` 工具配合正则表达式匹配 P3C 规范违规
6. **调用子技能**：调用以下子技能进行详细检查
   - p3c-coding-style
   - p3c-exception-logging
   - p3c-advanced-coding
   - p3c-mysql-database
   - p3c-oop-standards
   - p3c-security-rules
   - p3c-unit-testing
7. **生成测试报告**：使用 `Write` 工具生成 Markdown 格式报告

### 常用 Trae IDE 内置工具

**文件查找工具**
- `Glob` - 查找所有 `.java` 文件
- `LS` - 列出目录结构

**代码读取工具**
- `Read` - 读取文件内容
- `SearchCodebase` - 搜索代码库中的特定模式和结构

**代码分析工具**
- `Grep` - 使用正则表达式搜索代码，匹配 P3C 规则
- `GetDiagnostics` - 获取 Trae IDE 的语言诊断信息（编译错误、警告等）

**报告生成工具**
- `Write` - 生成 Markdown 格式的测试报告

### 子技能说明

本技能是聚合技能，会调用以下子技能进行详细检查：

| 子技能 | 描述 | 检查内容 |
|--------|------|---------|
| p3c-coding-style | 代码风格规范 | 命名风格、代码格式、常量定义、注释规约 |
| p3c-exception-logging | 异常与日志规范 | 异常处理、日志规约、NPE防护 |
| p3c-advanced-coding | 高级编程规范 | 集合处理、并发处理、控制语句 |
| p3c-mysql-database | MySQL数据库规范 | 建表规约、SQL语句、索引规约、ORM映射 |
| p3c-oop-standards | OOP编程规范 | 方法覆写、equals/hashCode、包装类、序列化 |
| p3c-security-rules | 安全规约 | 权限控制、SQL注入防护、XSS/CSRF防护、参数验证 |
| p3c-unit-testing | 单元测试规范 | AIR原则、测试粒度、测试覆盖率、BCDE原则 |

## 测试执行流程

### 步骤1：代码扫描
使用 Trae IDE 内置工具扫描指定的Java源代码文件或目录：
- 使用 `Glob` 查找所有 `.java` 文件
- 使用 `Read` 读取文件内容
- 使用 `SearchCodebase` 进行代码结构分析
- 使用 `GetDiagnostics` 获取编译诊断信息

### 步骤2：规范检查
根据P3C规范对代码进行逐项检查。本技能是聚合技能，会调用以下子技能进行详细检查：

#### 子技能调用
1. **p3c-coding-style** - 代码风格规范
   - 命名风格：类名、方法名、变量名、常量命名规范
   - 代码格式：大括号、缩进、空格、行长度等格式规范
   - 常量定义：魔法值、Long类型、常量分类
   - 注释规约：Javadoc规范、注释语言、注释同步更新

2. **p3c-exception-logging** - 异常与日志规范
   - 异常处理：异常捕获原则、异常处理要求、NPE防护
   - 日志规约：日志框架、日志保存、日志输出、日志级别

3. **p3c-advanced-coding** - 高级编程规范
   - 集合处理：hashCode和equals、subList使用、集合转数组、foreach循环
   - 并发处理：线程池、锁性能、死锁预防、并发更新
   - 控制语句：switch语句、大括号使用、if-else优化

4. **p3c-mysql-database** - MySQL数据库规范
   - 建表规约：字段要求、表名要求、索引命名
   - SQL语句规约：count使用、in操作、分页查询
   - 索引规约：唯一索引、join限制、索引长度
   - ORM映射规约：查询字段、参数绑定、事务管理

5. **p3c-oop-standards** - OOP编程规范
   - 方法覆写：@Override注解、equals方法、包装类比较
   - 序列化：serialVersionUID、toString方法
   - 访问控制：类成员访问控制、final关键字使用

6. **p3c-security-rules** - 安全规约
   - 权限控制：水平权限校验、数据脱敏
   - SQL注入防护：参数绑定、字符串拼接
   - XSS/CSRF防护：安全过滤、防重放限制
   - 参数验证：有效性验证、防刷策略

7. **p3c-unit-testing** - 单元测试规范
   - AIR原则：自动化、独立性、可重复性
   - 测试粒度：方法级别测试、核心业务测试
   - 测试覆盖率：语句覆盖率、分支覆盖率
   - BCDE原则：边界值、正确输入、设计文档、错误输入

#### 检查方法
使用 `Grep` 工具配合正则表达式匹配代码中的P3C规范违规：
- **强制规范**：必须遵守，违反即视为严重问题
- **推荐规范**：建议遵守，违反视为一般问题
- **参考规范**：可选择性遵守，违反视为轻微问题

### 步骤3：问题分类
将检查到的问题按严重程度分类：
- **致命问题**：违反强制规范，可能导致严重后果
- **严重问题**：违反强制规范，影响代码质量
- **一般问题**：违反推荐规范，影响代码可维护性
- **轻微问题**：违反参考规范，属于优化建议

### 步骤4：生成测试报告
使用 `Write` 工具生成详细的测试报告，包含：
- 测试范围和测试时间
- 问题统计（按严重程度和规范类别）
- 问题详情列表
- 改进建议

## 输入参数

执行测试时需要提供以下参数：

1. **代码路径**：要检查的Java源代码文件或目录路径
2. **业务名称**：用于生成报告路径和文件名
3. **测试内容**：描述本次测试的具体内容
4. **测试接口/模块名称**：被测试的接口或模块名称

## 测试报告格式

测试报告将生成到以下路径：
```
doc/{业务名称}/测试报告/{测试内容}/{测试接口名称}_{时间戳}.md
```

报告包含以下内容：

### 报告头部
- 测试时间
- 测试人员
- 测试范围
- 测试工具

### 问题统计
- 问题总数
- 致命问题数量
- 严重问题数量
- 一般问题数量
- 轻微问题数量

### 问题分类统计
按P3C规范类别统计问题分布

### 问题详情列表
每个问题包含：
- 问题编号
- 严重程度
- 规范类别
- 规则描述
- 代码位置（文件名、行号）
- 问题说明
- 修改建议

### 改进建议
- 高优先级改进项
- 中优先级改进项
- 低优先级改进项

### 质量评估
- 代码质量评分
- 符合度百分比
- 风险评估

## 使用示例

### 示例 1：检查单个文件
```
输入：
- 代码路径：src/main/java/com/example/UserService.java
- 业务名称：用户管理
- 测试内容：代码质量检查
- 测试接口名称：UserService

输出：
- 报告路径：doc/用户管理/测试报告/代码质量检查/UserService_20250103143025.md
```

### 示例 2：检查整个模块
```
输入：
- 代码路径：src/main/java/com/example/order/
- 业务名称：订单系统
- 测试内容：代码质量检查
- 测试接口名称：OrderModule

输出：
- 报告路径：doc/订单系统/测试报告/代码质量检查/OrderModule_20250103143025.md
```

### 示例 3：完整测试报告样例
```markdown
# P3C 代码质量检查报告

## 基本信息
- 测试时间：2026-03-11 14:30:25
- 测试人员：AI Assistant
- 测试范围：src/main/java/com/bgyfw/parking/
- P3C 版本：《阿里巴巴 Java 开发手册》2022 版

## 问题统计
- 问题总数：15
- 致命问题：2
- 严重问题：5
- 一般问题：6
- 轻微问题：2

## 问题详情

### 致命问题
【问题编号】P3C-001
【严重程度】致命
【规范类别】p3c-security-rules
【规则描述】SQL 注入防护 - 禁止使用字符串拼接 SQL
【代码位置】RefundOrderController.java:45
【问题说明】发现使用字符串拼接 SQL 语句，存在 SQL 注入风险
【修改建议】使用参数化查询或 MyBatis 的#{param} 方式

### 严重问题
【问题编号】P3C-002
【严重程度】严重
【规范类别】p3c-exception-logging
【规则描述】异常处理 - 禁止捕获 Exception 后不做任何处理
【代码位置】RefundOrderServiceImpl.java:78
【问题说明】catch 块中仅打印日志，未进行异常传播或返回错误状态
【修改建议】抛出运行时异常或返回明确的错误响应

### 一般问题
【问题编号】P3C-003
【严重程度】一般
【规范类别】p3c-coding-style
【规则描述】命名风格 - 方法名应使用动词 + 名词形式
【代码位置】RefundOrder.java:23
【问题说明】方法名"status"不够清晰，无法表达是获取状态还是设置状态
【修改建议】修改为 getStatus() 或 setStatus()

### 轻微问题
【问题编号】P3C-004
【严重程度】轻微
【规范类别】p3c-coding-style
【规则描述】注释规约 - 公共方法应有 Javadoc 注释
【代码位置】RefundOrderMapper.java:15
【问题说明】selectById 方法缺少 Javadoc 注释
【修改建议】添加/** */格式的 Javadoc 注释
```

## 常见违规案例

### 案例 1：魔法值
```java
// ❌ 错误示例
if (status == 1) {
    // ...
}

// ✅ 正确示例
public static final int STATUS_ACTIVE = 1;
if (status == STATUS_ACTIVE) {
    // ...
}
```

### 案例 2：NPE 防护
```java
// ❌ 错误示例
String name = user.getName();
if (name.equals("admin")) {
    // ...
}

// ✅ 正确示例
if ("admin".equals(user.getName())) {
    // ...
}
```

### 案例 3：线程池使用
```java
// ❌ 错误示例
ExecutorService executor = Executors.newCachedThreadPool();

// ✅ 正确示例
ExecutorService executor = new ThreadPoolExecutor(
    corePoolSize,
    maximumPoolSize,
    keepAliveTime,
    TimeUnit.SECONDS,
    new LinkedBlockingQueue<>(capacity),
    new ThreadFactoryBuilder().setNameFormat("custom-%d").build(),
    new ThreadPoolExecutor.CallerRunsPolicy()
);
```

## 检查规则说明

### 强制规范检查（必须遵守）
以下规范违反将导致**致命**或**严重**问题：

#### 1. 安全规约（致命级别）
- 【P3C-SEC-001】禁止使用字符串拼接 SQL 语句，必须使用参数化查询
- 【P3C-SEC-002】涉及用户敏感数据必须进行脱敏处理
- 【P3C-SEC-003】接口必须进行参数有效性验证，防止恶意输入
- 【P3C-SEC-004】禁止硬编码密码、密钥等敏感信息

#### 2. 异常处理（严重级别）
- 【P3C-EXC-001】禁止捕获 Exception 后不做任何处理（空 catch）
- 【P3C-EXC-002】禁止使用 printStackTrace()，必须使用日志框架
- 【P3C-EXC-003】事务方法中必须进行异常传播，不能吞掉异常
- 【P3C-EXC-004】NPE 防护：使用 equals 时常量在前，或使用 Objects.equals()

#### 3. 并发处理（严重级别）
- 【P3C-CON-001】禁止使用 Executors 创建线程池，必须使用 ThreadPoolExecutor
- 【P3C-CON-002】线程池必须指定拒绝策略
- 【P3C-CON-003】SimpleDateFormat 非线程安全，禁止在多线程环境下直接使用
- 【P3C-CON-004】集合类遍历时禁止直接修改集合结构

#### 4. 数据库规范（严重级别）
- 【P3C-DB-001】表必备字段：id（主键）、gmt_create（创建时间）、gmt_modified（修改时间）
- 【P3C-DB-002】禁止使用物理删除，必须使用逻辑删除
- 【P3C-DB-003】SQL 查询必须使用索引优化，禁止全表扫描
- 【P3C-DB-004】count(*) 用于统计行数，count(列名) 用于统计非 NULL 值

#### 5. 代码风格（严重级别）
- 【P3C-STY-001】类名：UpperCamelCase（DO/BO/DTO/VO 等后缀大写）
- 【P3C-STY-002】方法名、变量名：lowerCamelCase
- 【P3C-STY-003】常量名：UPPER_CASE，用下划线分隔
- 【P3C-STY-004】禁止魔法值，必须定义常量

#### 6. OOP 规范（严重级别）
- 【P3C-OOP-001】覆写 equals 必须同时覆写 hashCode
- 【P3C-OOP-002】包装类比较必须使用 equals，禁止使用==
- 【P3C-OOP-003】类必须有访问控制符，成员变量必须是 private
- 【P3C-OOP-004】POJO 类必须实现 Serializable 接口

#### 7. 单元测试（严重级别）
- 【P3C-TST-001】测试方法必须使用@Test注解
- 【P3C-TST-002】测试类必须遵循*Test命名规范
- 【P3C-TST-003】核心业务逻辑必须有单元测试覆盖

### 推荐规范检查（建议遵守）
以下规范违反将导致**一般**问题：

#### 1. 注释完整性
- 【P3C-CMT-001】公共方法应有 Javadoc 注释
- 【P3C-CMT-002】复杂算法、业务逻辑应有详细注释
- 【P3C-CMT-003】注释语言应与项目一致（中文项目用中文）

#### 2. 代码可读性
- 【P3C-RED-001】方法长度不超过 80 行
- 【P3C-RED-002】单行代码不超过 120 个字符
- 【P3C-RED-003】避免过深的嵌套（不超过 4 层）
- 【P3C-RED-004】使用有意义的命名，避免缩写

#### 3. 性能优化
- 【P3C-PER-001】循环体内禁止创建重复对象
- 【P3C-PER-002】大数据量查询必须分页
- 【P3C-PER-003】优先使用 StringBuilder 进行字符串拼接
- 【P3C-PER-004】及时关闭资源，使用 try-with-resources

#### 4. 代码复用
- 【P3C-RUS-001】重复代码超过 3 处应抽取为公共方法
- 【P3C-RUS-002】工具类应设计为私有构造方法的 final 类
- 【P3C-RUS-003】避免过度设计，遵循 KISS 原则

### 参考规范检查（优化建议）
以下规范违反将导致**轻微**问题：

#### 1. 代码风格
- 【P3C-REF-001】import 顺序应按字母序排列
- 【P3C-REF-002】左大括号前应有空格
- 【P3C-REF-003】操作符两侧应有空格
- 【P3C-REF-004】方法调用结束后空行

#### 2. 最佳实践
- 【P3C-BPR-001】优先使用 JDK 动态代理而非 CGLIB
- 【P3C-BPR-002】使用 Optional 处理可能为 null 的值
- 【P3C-BPR-003】接口设计遵循最少知识原则
- 【P3C-BPR-004】异常类应包含详细的错误信息

#### 3. 优化建议
- 【P3C-OPT-001】考虑使用缓存提升性能
- 【P3C-OPT-002】考虑异步处理耗时操作
- 【P3C-OPT-003】考虑添加监控和告警
- 【P3C-OPT-004】考虑国际化支持

### 参考规范检查
- 代码风格：是否符合团队编码风格
- 最佳实践：是否使用了推荐的最佳实践
- 优化建议：是否有进一步优化的空间

## 排除规则与豁免

### 允许豁免的情况
以下情况可以申请豁免检查：

1. **遗留代码**：历史遗留代码逐步改进，可暂时豁免（需标注 TODO）
2. **特殊需求**：因业务特殊性无法满足规范，需技术负责人审批
3. **第三方依赖**：第三方库的类名、方法名不符合规范
4. **性能考量**：某些场景下为性能牺牲规范（需有充分理由）
5. **兼容性要求**：为保持 API 兼容性而无法修改的命名

### 豁免方式
```java
// 方式 1：使用@SuppressNullWarning 注解（针对 NPE 检查）
@SuppressNullWarning
public String getUserInfo() { ... }

// 方式 2：使用注释标注（针对特定规则）
// CHECKSTYLE:OFF - 遗留代码，待后续重构
public void legacyMethod() { ... }
// CHECKSTYLE:ON

// 方式 3：TODO 标记（针对临时豁免）
// TODO [P3C-EXC-001] 待改进：需要完善异常处理
public void needImprove() { ... }
```

### 渐进式改进策略
对于存量代码，建议采用以下策略：

1. **新增代码零容忍**：所有新增代码必须符合 P3C 规范
2. **核心代码优先**：优先改进核心业务模块的代码
3. **分阶段改进**：制定改进计划，按优先级逐步修复
4. **自动化修复**：使用 IDE 插件自动修复格式问题
5. **Code Review**：将 P3C 检查纳入 Code Review 流程

## 注意事项

1. **报告路径**：确保 doc 目录存在且有写入权限
2. **代码编码**：确保源代码文件使用 UTF-8 编码
3. **依赖解析**：对于复杂的依赖关系，可能需要额外的配置
4. **误报处理**：某些规则可能存在误报，需要人工审核
5. **优先级处理**：优先处理致命和严重问题
6. **性能优化**：
   - 对于大型项目，建议按模块分批检查
   - 支持增量检查，仅检查变更文件
   - 检查超时时间默认设置为 300 秒，可通过参数调整
7. **排除目录**：以下目录默认不检查
   - `target/`、`build/`等构建输出目录
   - `.git/`、`.svn/`等版本控制目录
   - `vendor/`、`lib/`等第三方库目录
   - `generated/`等代码生成目录

## 质量评分标准

- **优秀**：90分以上，无致命和严重问题
- **良好**：80-89分，无致命问题，严重问题不超过3个
- **合格**：70-79分，致命问题不超过1个，严重问题不超过5个
- **需改进**：60-69分，致命问题不超过2个，严重问题不超过10个
- **不合格**：60分以下，存在较多严重问题

## 最佳实践

1. **定期检查**：建议在代码提交前进行 P3C 规范检查
2. **持续集成**：将 P3C 检查集成到 CI/CD 流程中
   ```yaml
   # GitLab CI 示例
   p3c_check:
     stage: test
     script:
       - mvn checkstyle:check
       - mvn spotbugs:check
   ```
3. **问题跟踪**：将检查到的问题录入缺陷管理系统
   - 致命问题：24 小时内修复
   - 严重问题：3 个工作日内修复
   - 一般问题：1 周内修复
   - 轻微问题：迭代优化
4. **团队培训**：定期进行 P3C 规范培训，提高团队代码质量意识
5. **规范更新**：及时更新 P3C 规范版本，保持与最新标准一致
6. **工具集成**：
   - IDE 插件：安装 Alibaba Java Coding Guidelines 插件
   - Maven 插件：使用 p3c-maven-plugin 进行构建时检查
   - SonarQube：集成 P3C 规则集
7. **质量门禁**：
   - 新增代码违规数为 0
   - 存量违规数每周递减 10%
   - 单元测试覆盖率不低于 70%

---

**现在，请提供以下信息开始测试：**
1. 代码路径（文件或目录）
2. 业务名称
3. 测试内容描述
4. 测试接口/模块名称
