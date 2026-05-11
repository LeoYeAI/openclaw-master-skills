---
name: module-analyzer-generate-doc
description: Java/Maven single-module deep documentation generator. Generates L3(file-level) to L2(module-level) business logic docs for specified module. Supports multi-subagent parallel processing, context compression, checkpoint resume, and auto-retry.
---

# Module Analyzer Generate Doc - Java 单模块深度文档生成器

> 专注于单个 Java/Maven 模块的深度业务逻辑分析 - 让 AI 全面理解模块的每个细节

## 核心特性

**单模块深度分析**:
- 专注于单个模块的完整扫描（而非整个项目）
- L3 文件级文档：每个包含业务逻辑的类生成详细业务解释
- L2 模块级文档：模块架构索引、核心业务流程、依赖关系汇总

**智能任务执行**:
- 多子代理并行分片处理（默认 5 个并行，每片 10-16 个文件）
- 上下文自动压缩（每处理 2-3 个文件压缩一次）
- 失败自动重试（最多 3 次，指数退避）
- 断点续传支持（状态文件记录进度）
- 进度定时汇报（每 20 分钟）

**文档质量保证**:
- 纯自然语言业务描述（无代码片段）
- 方法级别流程分析（触发条件、数据处理、业务规则、异常处理）
- 领域知识解释（业务概念、术语说明）
- 设计意图说明（为什么这样设计，解决什么问题）

**智能跳过机制**:
- 纯数据对象（Entity/DTO/VO，仅 getter/setter）→ 跳过
- 枚举定义（无复杂逻辑）→ 跳过
- 简单参数对象 → 跳过
- 测试类 → 跳过
- 接口定义（业务逻辑在 Impl 中）→ 跳过

---

## 激活条件

当用户提到以下关键词时激活：
- "分析这个模块"
- "生成模块文档"
- "扫描 admin-api 模块"
- "为 xxx 模块生成源码解析"
- "理解这个模块的业务逻辑"
- "模块级文档索引"
- "Java 模块分析"
- "单模块深度分析"

**与 project-analyzer-generate-doc 的区别**:
- `project-analyzer-generate-doc`：全项目多模块扫描，生成 L3→L2→L1 三层文档
- `module-analyzer-generate-doc`：单模块深度扫描，生成 L3→L2 两层文档（更详细、更快速）

---

## 完整工作流程

### Step 0: 模块扫描与规划

```powershell
# 1. 扫描模块目录结构
Get-ChildItem "<模块路径>" -Directory -Recurse | Where-Object { $_.Name -notmatch 'target|\.git|build' }

# 2. 统计 Java 文件
$javaFiles = Get-ChildItem "<模块路径>/src/main/java" -Include *.java -Recurse | Where-Object { $_.FullName -notmatch '\\test\\' }

# 3. 统计 XML 文件（MyBatis Mapper）
$xmlFiles = Get-ChildItem "<模块路径>/src/main/resources" -Include *.xml -Recurse | Where-Object { $_.Name -match 'mapper|Mapper' }

# 4. 检查已存在文档
$existingDocs = Get-ChildItem "<项目根目录>/.ai-doc/<模块名>" -Include *.md -Recurse 2>$null

# 5. 制定分片计划
# - <20 文件：单子代理
# - 20-50 文件：3-4 个子代理分片
# - >50 文件：5-6 个子代理分片，每片 10-16 个文件
```

**输出**: 文件列表 + 分片计划 + 已存在文档检查

---

### Step 0.5: 已存在文档处理

**目的**: 检查已存在的文档是否符合要求，按需迁移或更新

```markdown
检查规则:
1. 文档路径是否符合 `.ai-doc/模块名/src/main/java/包路径/类名.java.md` 规则
2. 文档内容是否包含详细业务逻辑描述（非简单解释）
3. 文档是否包含代码片段（应全部为自然语言）

处理策略:
- 路径不符合 → 迁移到正确位置
- 内容过于简单 → 重新生成
- 内容符合要求 → 保留，不重复生成
- 源码已变更 → 更新文档
```

---

### Step 0.6: 识别低质量文档（仅报告，需用户确认）

**目的**: 识别不符合要求的文档，**仅生成报告，不自动删除**

```powershell
# 1. 识别低质量文档（只有模板框架，无实际业务内容）
$lowQualityDocs = Get-ChildItem "<项目根目录>/.ai-doc/<模块名>" -Include *.md -Recurse | Where-Object {
    $content = Get-Content $_.FullName -Raw
    $lineCount = (Get-Content $_.FullName).Count
    # 行数少于 20 行
    $lineCount -lt 20 -or
    # 只包含模板框架文字
    $content -match 'Business component - participates in system business processing' -or
    $content -match 'Executes business logic based on specific scenario' -or
    $content -match 'Simple data object' -or
    $content -match 'Interface definition - declares contract specification'
}
# 输出报告，供用户决定是否处理
foreach ($doc in $lowQualityDocs) {
    Write-Host "低质量文档：$($doc.FullName)"
}

# 2. 识别空文件夹（供用户参考）
Get-ChildItem "<项目根目录>/.ai-doc/<模块名>" -Directory -Recurse | ForEach-Object {
    if ((Get-ChildItem $_.FullName -Force).Count -eq 0) {
        Write-Host "空目录：$($_.FullName)"
    }
}
```

**⚠️ 重要安全约束**:
- 此步骤**仅生成报告**，绝不自动删除任何文件
- 如需处理低质量文档，必须**明确询问用户并获得确认**
- 删除操作示例（仅当用户明确同意时执行）:
  ```powershell
  # 询问用户确认
  $confirm = Read-Host "是否删除 $($lowQualityDocs.Count) 个低质量文档？(y/n)"
  if ($confirm -eq "y") {
      # 移动到回收站而非直接删除（如果可能）
      foreach ($doc in $lowQualityDocs) {
          Write-Host "将移动到回收站：$($doc.FullName)"
      }
  }
  ```

---

### Step 1: 生成 L3 文件级文档（核心阶段）

**子代理分片策略**:

| 文件总数 | 子代理数 | 每片文件数 | 超时时间 |
|----------|----------|------------|----------|
| <20 | 1 | 全部 | 300 秒 |
| 20-50 | 3-4 | 10-16 | 600 秒 |
| 50-80 | 5 | 12-18 | 900 秒 |
| >80 | 6-8 | 10-14 | 900 秒 |

**子代理任务模板**:

```markdown
# 任务：为 <模块名> 模块生成 L3 文档（分片 X/Y）

## 项目路径
<绝对路径>

## 源码根目录
<模块路径>/src/main/java

## 输出目录
<项目根目录>/.ai-doc/<模块名>/

## 本分片文件列表
<文件列表，10-16 个>

## 核心要求

### 1. 文档内容要求
- **详细业务逻辑描述**：将代码逻辑转换为自然语言，非程序员也能理解
- **不包含代码片段**：MD 文件中不要出现任何原代码
- **方法级别分析**：每个有业务逻辑的方法都要描述其执行流程、业务语义
- **领域知识**：解释涉及的业务概念、领域术语
- **流程上下文**：方法间的调用关系、数据流转
- **设计意图**：为什么这样设计，解决什么问题

### 2. 文档路径规则（⚠️ 重要！）
- 源文件：`<模块路径>/src/main/java/包路径/类名.java`
- 文档：`<项目根目录>/.ai-doc/<模块名>/src/main/java/包路径/类名.java.md`
- **⚠️ 必须包含 `src/main/java/` 完整路径！**
- **❌ 错误示例**：`.ai-doc/app-api/com/infypower/...`（缺少 src/main/java）
- **✅ 正确示例**：`.ai-doc/app-api/src/main/java/com/infypower/...`
- 生成文档前必须检查路径是否正确，错误路径的文档会被视为无效

### 3. 跳过规则（⚠️ 严格执行！）

**必须跳过的文件类型**（满足任一条件即跳过）：

| 类型 | 判断标准 | 示例 |
|------|----------|------|
| **DTO/VO/Param** | 类名以 DTO/VO/Param/BO 结尾，且行数<50，且不包含方法（除 getter/setter） | UserDTO.java, LoginVO.java |
| **枚举** | 包含 `enum` 关键字，且不包含复杂方法 | PaymentStatus.java |
| **常量类** | 类名包含 Constant，且只包含 `public static final` 字段 | AppApiConstant.java |
| **接口** | 包含 `public interface`，且无方法实现 | UserService.java |
| **MapStruct Converter** | 包含 `@Mapper` 注解，或接口名包含 Converter | UserConverter.java |
| **抽象基类** | 包含 `public abstract class`，且方法都是抽象的 | AbstractHandler.java |
| **测试类** | 类名包含 Test，或包含 `@Test` 注解 | UserServiceTest.java |

**代码特征检查**（满足任一条件即跳过）：
```
1. 文件行数 < 30 行
2. 不包含以下关键字：if, for, while, switch, try, catch, return（getter/setter 除外）
3. 只包含字段定义和 @ 注解
4. 方法体都是空的（只有分号或 throw new UnsupportedOperationException）
```

**⚠️ 必须生成文档的情况**（满足任一条件）：
- Controller 类（包含 API 接口）
- Service/ServiceImpl 类
- Helper/Util 类（包含业务方法）
- Consumer/Listener 类（消息处理）
- Job/Task 类（定时任务）
- Config 配置类（包含 Bean 定义）
- Interceptor/Filter/Aspect 类
- 任何包含实际业务逻辑的类

### 4. 文档质量自检（⚠️ 生成后必须检查！）

**生成每个文档后自检**，确保文档合格：

**✅ 合格文档检查清单**（必须全部满足）：
- [ ] 文档行数 > 30 行
- [ ] 包含"触发条件"或类似描述（什么时候执行）
- [ ] 包含"输入数据"或"处理流程"描述（如何处理）
- [ ] 包含"业务规则"或"判断逻辑"描述（判断条件）
- [ ] 包含"输出结果"或"数据流转"描述（结果去向）
- [ ] 不包含原代码片段（`public class`, `if ()`, `return` 等关键字）

**❌ 低质量文档特征**（出现任一需重新生成，不建议使用）：
- [ ] 文档行数 < 20 行
- [ ] 只包含模板框架（"Business component", "Interface definition", "Simple data object"）
- [ ] 只重复类名和包名，无实际业务解释
- [ ] 核心业务逻辑部分只有"Executes business logic based on specific scenario"

**自检示例**：
```markdown
# ❌ 低质量文档（需要重新生成）
## Business Responsibility
Business component - participates in system business processing

## Core Business Logic
Executes business logic based on specific scenario

# ✅ 合格文档（正确示例）
## 业务职责
AuthService 是认证服务核心类，处理用户账户的创建、更新、查询，
以及支付宝授权码验证和加密手机号解密。当用户通过小程序授权登录时，
该类负责从微信/支付宝获取用户信息，创建或更新本地用户账户...

## 核心业务逻辑
### 支付宝授权码验证
触发条件：用户在小程序点击授权登录，前端传入 auth_code
处理流程：
1. 调用支付宝 API 换取用户 open_id
2. 验证返回的 open_id 是否有效
3. 根据 open_id 查询本地用户...
```

### 5. 上下文管理
- Config 配置类（包含业务配置逻辑）
- 工具类（包含业务相关工具方法）
- 拦截器/过滤器（包含业务逻辑）
- 异常处理器
- MyBatis Mapper XML 文件
- 任何包含业务逻辑的类

### 5. 上下文管理
- 每处理完 2-3 个文件，压缩已处理内容
- 只保留：文件路径 + 1 行摘要
- 丢弃：完整文档内容、中间思考过程

### 6. 文件读取失败处理
- 如文件读取失败，记录该文件到失败列表
- 在最终报告中标注无法读取的文件
- 请求用户确认文件访问权限
- ⚠️ 禁止尝试提权或使用替代读取工具

## L3 文档模板

```markdown
# {类名} - 业务逻辑详解

## 基本信息
- **文件路径**: {relativePath}
- **行数**: {lines}
- **文件类型**: {Config/Controller/Service/ServiceImpl/Interceptor/Handler/Util}
- **所属模块**: {moduleName}

## 业务职责
{用自然语言描述这个类的业务职责，200-300 字}

## 核心业务逻辑

### {方法/功能点 1}
{详细描述该功能的业务逻辑流程，包括：
- 触发条件
- 输入数据处理
- 业务规则判断
- 数据流转过程
- 输出结果
- 异常情况处理
}

### {方法/功能点 2}
{同上}

## 业务流程
{描述方法间的调用关系和业务流转过程}

## 数据交互
{描述与数据库、外部服务、Redis、MQ 等的交互}

## 依赖关系
{该类依赖的其他组件和服务}

## 设计意图
{解释为什么这样设计，解决了什么业务问题}
```

## 返回格式

```json
{
  "chunk": "X/Y",
  "status": "completed|partial",
  "processed": ["File1.java", ...],
  "skipped": ["SimpleClass.java", ...],
  "failed": [],
  "summaries": [
    {"file": "File1.java", "lines": 150, "type": "Controller", "summary": "一句话业务摘要"}
  ]
}
```
```

**上下文压缩策略**:

```
每处理 2-3 个文件后：
保留：
- 文件路径列表
- 每文件 1 行摘要
- 当前任务描述
- 输出路径
- 进度统计

丢弃：
- 已生成文档的完整内容
- 中间思考过程
- 详细示例
- 完整函数体
```

---

### Step 2: 生成 L2 模块级文档

**触发条件**: 所有 L3 文档生成完成

**核心策略**:
- spawn 一个子代理
- 读取该模块所有 L3 文档的摘要信息
- 汇总生成 module.md
- 包含模块架构、核心业务流程、依赖关系

**L2 文档模板**:

详见 [references/l2-module-template.md](references/l2-module-template.md)

**核心章节**:

```markdown
# {模块名} - 模块详解

## 模块职责
{200-300 字概述模块的业务定位和核心价值}

## 文件索引表
| 文件路径 | 职责简述 | 类型 | 行数 |
|----------|----------|------|------|
{列出所有已生成 L3 文档的文件}

## 核心业务流程

### 1. {核心流程 1}
{详细描述跨类的业务流程，如用户认证授权流程}

### 2. {核心流程 2}
{如数据权限隔离流程}

### 3. {核心流程 3}
{如系统管理功能流程}

## MyBatis 映射关系
{SQL 与 Java 方法的映射关系，核心表说明}

## 模块依赖
- **内部依赖**: 依赖的其他模块
- **外部服务**: Redis/MySQL/Apollo/RabbitMQ/XXL-Job 等
- **框架依赖**: Spring Boot/MyBatis-Plus/Spring Security 等

## 配置项汇总
{application 配置文件的主要设置，按功能分类}

## 技术栈
{使用的框架和技术组件清单}
```

---

## 任务监控与重试机制

### 状态文件

**路径**: `<项目根目录>/.ai-doc/.generate-state.json`

**内容**:
```json
{
  "version": "1.0.0",
  "projectPath": "<项目根目录>",
  "targetModule": "<模块名>",
  "startTime": "2026-03-07T10:17:00+08:00",
  "currentPhase": "L3",
  "overallProgress": 76.5,
  "phases": {
    "L3": {
      "status": "completed|in_progress|pending",
      "totalFiles": 81,
      "processedFiles": 62,
      "skippedFiles": 19,
      "failedFiles": 0,
      "chunks": {
        "total": 5,
        "completed": 5,
        "inProgress": 0,
        "pending": 0,
        "failed": 0
      }
    },
    "L2": {
      "status": "completed|in_progress|pending",
      "totalModules": 1,
      "completedModules": 0
    }
  },
  "subagents": [
    {
      "label": "L3-chunk1",
      "status": "completed|running|failed|timeout",
      "files": 16,
      "startTime": "...",
      "endTime": "..."
    }
  ],
  "lastCheckpoint": "2026-03-07T10:40:00+08:00",
  "canResume": true
}
```

### 重试策略

```yaml
retry_policy:
  max_retries: 3                    # 最大重试次数
  initial_delay: 30                 # 初始延迟（秒）
  backoff_multiplier: 2             # 延迟倍增因子
  max_delay: 300                    # 最大延迟（秒）
  retryable_errors:
    - "timeout"
    - "context_overflow"
    - "file_access_error"
    - "subagent_crash"
```

### 进度汇报

**频率**: 每 20 分钟或每完成一个分片

**内容**:
```markdown
## 📊 文档生成进度报告

**模块**: admin-api
**开始时间**: 2026-03-07 10:17:00
**当前时间**: 2026-03-07 10:40:00
**已用时间**: 23 分钟

### 总体进度：76.5%

### 当前阶段：L3 文件级文档生成

| 分片 | 状态 | 已处理 | 已跳过 |
|------|------|--------|--------|
| chunk1 | ✅ | 16 | 0 |
| chunk2 | ✅ | 6 | 10 |
| chunk3 | ✅ | 16 | 0 |
| chunk4 | ✅ | 13 | 4 |
| chunk5 | ✅ | 11 | 7 |

### 统计
- 已处理文件：62
- 已跳过文件：19（纯定义类）
- 失败文件：0
```

---

## 二次扫描查漏

**目的**: 确保所有包含业务逻辑的源码都有文档可依

**流程**:
```powershell
# 1. 扫描所有 Java 文件
$javaFiles = Get-ChildItem "<模块路径>/src/main/java" -Include *.java -Recurse

# 2. 扫描所有已生成文档
$docFiles = Get-ChildItem "<项目根目录>/.ai-doc/<模块名>" -Include *.md -Recurse

# 3. 对比找出缺失文档的文件
foreach ($java in $javaFiles) {
    $relative = $java.FullName.Replace("<模块路径>/src/main/java/", "")
    $expectedDoc = "<项目根目录>/.ai-doc/<模块名>/$relative.md"
    if (!(Test-Path $expectedDoc)) {
        # 检查是否应该跳过
        $content = Get-Content $java.FullName -Raw
        if (ShouldSkip $content) {
            Write-Host "跳过 (简单类): $relative"
        } else {
            Write-Host "缺失文档: $relative"
            $missing += $relative
        }
    }
}

# 4. 对缺失文档的文件 spawn 补充任务
if ($missing.Count -gt 0) {
    Spawn subagent to process missing files
}
```

---

## 错误处理

### 子代理超时

```
问题：子代理处理大模块时超时

解决:
1. 检查已生成的文件
2. 将剩余文件拆分为更小的分片（每片 5-7 个文件）
3. 增加超时时间到 15 分钟
4. 重新 spawn 子代理，传递已完成进度
```

### 上下文爆炸

```
问题：子代理上下文使用率超过 60%

解决:
1. 立即触发强制压缩
2. 如果仍超过 60%，停止当前子代理
3. 将剩余文件拆分为更小的分片
4. 为新分片 spawn 新的子代理
5. 增加压缩频率（每 1 个文件就压缩）
```

### 文件访问权限问题

```
问题：文件因权限限制无法读取

解决:
1. 记录无法访问的文件到日志
2. 请求用户确认文件访问权限
3. 在最终报告中标注无法访问的文件
4. ⚠️ 禁止尝试提权、bash 工具或其他替代读取方式
5. 如果重试 3 次仍失败，跳过该文件
```

---

## 配置项

在 `TOOLS.md` 中添加：

```markdown
### Module Analyzer - Java 单模块深度文档生成器

- 默认分片大小：10-16 文件/子代理
- 最大并行：5-6 子代理
- 上下文阈值：40% 预警，50% 强制压缩
- 压缩频率：每处理 2-3 个文件
- 简单文件阈值：50 行
- 超时时间：300-900 秒（根据分片大小）
- 重试策略：最多 3 次，指数退避
- 进度汇报：每 20 分钟
- 断点续传：自动保存状态
- 文件读取失败处理：记录并重试
- 二次扫描：自动查漏补充
```

---

## 使用示例

### 基础用法

```
用户：分析 E:\projects\mgmt-api-cp 的 admin-api 模块，生成业务逻辑文档

AI: 收到！开始执行单模块深度分析流程：

Step 0: 扫描 admin-api 模块结构...
  📊 发现 81 个 Java 文件，1 个 XML 文件

Step 0.5: 检查已存在文档...
  ✅ 发现 20 个已有文档，检查内容质量

Step 1: 生成 L3 文件级文档（5 个子代理并行）...
  📊 进度：62/81 文件已处理
  🔄 活跃子代理：5/5
  ⏱️ 预计剩余时间：15 分钟

Step 2: 生成 L2 模块级文档...
  ✅ admin-api.md 生成完成（26KB）

二次扫描：查漏补充...
  ✅ 所有业务类都有文档可依

✅ 完成！生成 62 个 L3 文档 + 1 个 L2 模块文档
```

### 带已有文档的增量更新

```
用户：ces-domain 模块有代码变更，更新文档

AI: 收到！执行增量更新流程：

1. 检测变更文件（git diff 或时间戳比较）
2. 检查已存在文档质量
3. 只更新变更文件的 L3 文档
4. 重新汇总生成 ces-domain.md (L2)

注意：保持文档路径与源码路径一致
```

### 断点续传

```
用户：继续之前的文档生成任务

AI: 检测到未完成的生成任务...

## 上次任务状态
- 模块：admin-api
- 中断时间：2026-03-07 10:30:00
- 完成进度：L3 阶段 76.5% (62/81 文件)
- 失败分片：1 个（已重试 2 次）

是否从断点继续？(y/n)

用户：y

AI: 恢复任务...
- 跳过已完成的 62 个文件
- 重新处理 1 个失败分片
- 继续生成剩余 19 个文件的 L3 文档
```

---

## 性能参考

### 生成时间估算

| 模块规模 | L3 生成 | L2 生成 | 总计 |
|----------|---------|---------|------|
| 20 文件 | ~5 分钟 | ~2 分钟 | ~7 分钟 |
| 50 文件 | ~12 分钟 | ~4 分钟 | ~16 分钟 |
| 80 文件 | ~20 分钟 | ~5 分钟 | ~25 分钟 |
| 150 文件 | ~40 分钟 | ~8 分钟 | ~48 分钟 |

### Token 消耗估算

| 阶段 | 每文件/模块 | 总计 (80 文件) |
|------|-------------|---------------|
| L3 生成 | 200k tokens/文件 | 16M tokens |
| L2 生成 | 350k tokens/模块 | 350k tokens |

---

## 相关文件

- L2 模块文档模板：[references/l2-module-template.md](references/l2-module-template.md)
- L3 文档模板：[references/l3-file-template.md](references/l3-file-template.md)
- 上下文压缩指南：[references/context-compression.md](references/context-compression.md)
- 任务监控指南：[references/task-monitoring.md](references/task-monitoring.md)
- 重试机制指南：[references/retry-mechanism.md](references/retry-mechanism.md)
- 二次扫描流程：[references/secondary-scan.md](references/secondary-scan.md)

---

## 版本

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.3 | 2026-03-10 | **安全修复 (最终)**：移除 python 代码块引用、移除"必须执行"强制指令、完整清理所有风险关键词 |
| 1.0.2 | 2026-03-10 | **安全修复 (完整)**：移除所有 bash/external tool 引用、移除 elevated 权限引用、明确要求用户确认删除/迁移操作 |
| 1.0.1 | 2026-03-10 | **安全修复**：移除提权/bash 引用、明确要求用户确认删除操作 |
| 1.0.0 | 2026-03-07 | 初始版本，基于 admin-api 模块实战经验 |
