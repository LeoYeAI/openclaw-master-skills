# Module Analyzer Generate Doc

> Java/Maven 单模块深度文档生成器 - 让 AI 全面理解模块的每个细节

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://clawhub.com/skills/module-analyzer-generate-doc)
[![OpenClaw](https://img.shields.io/badge/OpenClaw->=1.0.0-green.svg)](https://openclaw.ai)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

## 📖 简介 / Introduction

**Module Analyzer Generate Doc** 是一个专注于单个 Java/Maven 模块深度业务逻辑分析的文档生成器。它通过多子代理并行处理，为模块中的每个包含业务逻辑的类生成详细的自然语言文档，帮助开发者和非技术人员快速理解模块的核心职责和业务流程。

**Module Analyzer Generate Doc** is a documentation generator focused on deep business logic analysis of single Java/Maven modules. It generates detailed natural language documentation for each class with business logic through multi-subagent parallel processing, helping developers and non-technical personnel quickly understand the module's core responsibilities and business flows.

---

## ✨ 核心特性 / Core Features

### 🎯 单模块深度分析 / Single Module Deep Analysis

- **专注单个模块** - 与 project-analyzer 不同，本技能专注于单个模块的完整扫描
- **L3 文件级文档** - 为每个包含业务逻辑的类生成详细业务解释（无代码片段）
- **L2 模块级文档** - 模块架构索引、核心业务流程、依赖关系汇总

### 🤖 智能任务执行 / Intelligent Task Execution

- **多子代理并行** - 默认 5 个并行子代理，每片 10-16 个文件
- **上下文自动压缩** - 每处理 2-3 个文件自动压缩，防止上下文溢出
- **失败自动重试** - 最多 3 次重试，指数退避（30s→60s→120s）
- **断点续传** - 状态文件记录进度，支持崩溃后恢复
- **进度定时汇报** - 每 20 分钟自动汇报进度

### 📝 文档质量保证 / Documentation Quality

- **纯自然语言描述** - 不包含任何代码片段，非程序员也能理解
- **方法级别分析** - 每个有业务逻辑的方法都描述其执行流程
- **领域知识解释** - 解释涉及的业务概念、领域术语
- **设计意图说明** - 解释为什么这样设计，解决了什么问题

### ⚡ 智能跳过机制 / Smart Skip Mechanism

自动跳过无业务逻辑的文件：

| 跳过类型 | 判断标准 | 示例 |
|----------|----------|------|
| DTO/VO/Param | 类名以 DTO/VO/Param 结尾，行数<50，无业务方法 | UserDTO.java |
| 枚举 | 包含 enum，无复杂方法 | PaymentStatus.java |
| 常量类 | 类名含 Constant，只有 static final 字段 | AppConstant.java |
| 接口 | public interface，无方法实现 | UserService.java |
| MapStruct Converter | @Mapper 注解或接口名含 Converter | UserConverter.java |
| 测试类 | 类名含 Test 或包含@Test 注解 | UserServiceTest.java |

---

## 🚀 快速开始 / Quick Start

### 前置要求 / Prerequisites

- OpenClaw >= 1.0.0
- Python 3.x（标准库，无需额外依赖）
- PowerShell 5.1+（Windows）或 Bash（Linux/Mac）
- Java/Maven 项目源码

### 安装 / Installation

```bash
# 通过 ClawHub 安装
clawhub install module-analyzer-generate-doc

# 或从本地安装
git clone https://github.com/your-repo/module-analyzer-generate-doc.git
```

### 基本用法 / Basic Usage

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

---

## 📁 文档层级结构 / Documentation Structure

```
项目根目录/
├── .ai-doc/                          # 输出目录
│   ├── .generate-state.json          # 任务状态文件（断点续传）
│   ├── .task-log.md                  # 执行日志
│   ├── admin-api.md                  # L2: 模块级索引
│   └── admin-api/                    # L3: 文件级文档
│       ├── src/main/java/com/.../
│       │   ├── AuthorizationController.java.md
│       │   ├── UserController.java.md
│       │   ├── TokenProvider.java.md
│       │   └── ...
│       └── src/main/resources/.../
│           └── mapper/...
└── src/
    └── ...                           # 源代码
```

---

## 📋 完整工作流程 / Complete Workflow

### Step 0: 模块扫描与规划

```powershell
# 1. 扫描模块目录结构
Get-ChildItem "<模块路径>" -Directory -Recurse

# 2. 统计 Java 文件和 XML 文件
$javaFiles = Get-ChildItem "<模块路径>/src/main/java" -Include *.java -Recurse
$xmlFiles = Get-ChildItem "<模块路径>/src/main/resources" -Include *.xml -Recurse

# 3. 制定分片计划
# - <20 文件：单子代理
# - 20-50 文件：3-4 个子代理分片
# - >50 文件：5-6 个子代理分片，每片 10-16 个文件
```

### Step 1: 生成 L3 文件级文档

**子代理分片策略**:

| 文件总数 | 子代理数 | 每片文件数 | 超时时间 |
|----------|----------|------------|----------|
| <20 | 1 | 全部 | 300 秒 |
| 20-50 | 3-4 | 10-16 | 600 秒 |
| 50-80 | 5 | 12-18 | 900 秒 |
| >80 | 6-8 | 10-14 | 900 秒 |

### Step 2: 生成 L2 模块级文档

**触发条件**: 所有 L3 文档生成完成

**核心内容**:
- 模块职责概述（200-300 字）
- 文件索引表
- 核心业务流程（跨类的业务流转）
- MyBatis 映射关系
- 模块依赖（内部/外部/框架）
- 配置项汇总
- 技术栈清单

### Step 3: 二次扫描查漏

```powershell
# 对比源码和文档，找出缺失文档的文件
foreach ($java in $javaFiles) {
    $expectedDoc = "<项目根目录>/.ai-doc/<模块名>/$relative.md"
    if (!(Test-Path $expectedDoc)) {
        if (!(ShouldSkip $content)) {
            $missing += $relative
        }
    }
}

# 对缺失文件 spawn 补充任务
```

---

## 🔧 配置项 / Configuration

在 `TOOLS.md` 中添加：

```markdown
### Module Analyzer - Java 单模块深度文档生成器

- **默认分片大小**: 10-16 文件/子代理
- **上下文阈值**: 40% (预警), 50% (强制压缩)
- **最大并行**: 5 个子代理
- **简单文件阈值**: 50 行 (纯定义文件不生成 file.md)
- **超时时间**: 300-900 秒（根据分片大小）
- **重试策略**: 最多 3 次，指数退避
- **进度汇报**: 每 20 分钟
- **断点续传**: 自动保存状态
- **二次扫描**: 自动查漏补充
```

---

## 📊 性能参考 / Performance Benchmarks

### 生成时间估算 / Time Estimation

| 模块规模 | L3 生成 | L2 生成 | 总计 |
|----------|---------|---------|------|
| 20 文件 | ~5 分钟 | ~2 分钟 | ~7 分钟 |
| 50 文件 | ~12 分钟 | ~4 分钟 | ~16 分钟 |
| 80 文件 | ~20 分钟 | ~5 分钟 | ~25 分钟 |
| 150 文件 | ~40 分钟 | ~8 分钟 | ~48 分钟 |

### Token 消耗估算 / Token Consumption

| 阶段 | 每文件/模块 | 总计 (80 文件) |
|------|-------------|---------------|
| L3 生成 | 200k tokens/文件 | 16M tokens |
| L2 生成 | 350k tokens/模块 | 350k tokens |

---

## 📚 文档模板 / Documentation Templates

### L3 文件级文档模板

详见 [references/l3-file-template.md](references/l3-file-template.md)

**核心章节**:
- 基本信息（路径、行数、类型）
- 业务职责（200-300 字自然语言描述）
- 核心业务逻辑（方法级别详细流程）
- 业务流程（跨方法调用关系）
- 数据交互（数据库/Redis/外部服务）
- 依赖关系（依赖的类和被谁依赖）
- 设计意图（为什么这样设计）

### L2 模块级文档模板

详见 [references/l2-module-template.md](references/l2-module-template.md)

**核心章节**:
- 模块职责（200-300 字概述）
- 文件索引表
- 核心业务流程（跨类的业务流转）
- MyBatis 映射关系
- 模块依赖（内部/外部/框架）
- 配置项汇总
- 技术栈清单

---

## 🎯 使用场景 / Use Cases

### 新成员入职 / New Member Onboarding

```
场景：新加入团队的开发者需要快速理解负责的模块

用法：为负责的模块生成完整文档
结果：25 分钟内获得 62 个 L3 文档 + 1 个 L2 模块文档
价值：无需阅读源码即可理解模块业务逻辑
```

### 代码评审准备 / Code Review Preparation

```
场景：准备进行模块代码评审，需要全面了解业务逻辑

用法：评审前生成最新文档
结果：获得当前代码的完整业务描述
价值：评审时能快速理解变更影响的业务范围
```

### 遗留代码理解 / Legacy Code Understanding

```
场景：接手遗留系统，文档缺失或过时

用法：为遗留模块生成文档
结果：获得准确的业务逻辑描述
价值：降低维护成本，减少理解偏差
```

### 增量更新 / Incremental Update

```
场景：模块代码有变更，需要更新文档

用法：指定模块进行增量更新
结果：只更新变更文件的文档
价值：保持文档与代码同步
```

---

## 🔍 与 project-analyzer-generate-doc 的区别 / Comparison

| 特性 | module-analyzer | project-analyzer |
|------|-----------------|------------------|
| **分析范围** | 单个模块 | 整个项目（多模块） |
| **文档层级** | L3→L2（两层） | L3→L2→L1（三层） |
| **适用场景** | 深度理解特定模块 | 全面了解项目架构 |
| **生成时间** | 较快（7-48 分钟） | 较慢（1-4 小时） |
| **Token 消耗** | 较少（~16M） | 较多（~40M+） |
| **输出文件** | ~60 个 | ~350+ 个 |

**选择建议**:
- 需要理解**特定模块**的业务逻辑 → 使用 `module-analyzer-generate-doc`
- 需要全面了解**整个项目**的架构 → 使用 `project-analyzer-generate-doc`

---

## 🛠️ 故障排除 / Troubleshooting

### 子代理超时 / Sub-agent Timeout

**问题**: 子代理处理大模块时超时

**解决**:
1. 检查已生成的文件
2. 将剩余文件拆分为更小的分片（每片 5-7 个文件）
3. 增加超时时间到 15 分钟
4. 重新 spawn 子代理，传递已完成进度

### 上下文溢出 / Context Overflow

**问题**: 子代理上下文使用率超过 60%

**解决**:
1. 立即触发强制压缩
2. 如果仍超过 60%，停止当前子代理
3. 将剩余文件拆分为更小的分片
4. 增加压缩频率（每 1 个文件就压缩）

### 安全限制访问 / Security Restrictions

**问题**: 文件被安全软件（天锐绿盾等）限制访问

**解决**:
1. 尝试使用 bash 工具读取文件
2. 使用 PowerShell 的不同命令变体
3. 记录无法访问的文件，最后统一处理
4. 请求用户临时授权访问

---

## 📖 相关文档 / Related Documentation

- [L3 文件模板](references/l3-file-template.md) - L3 文档详细模板
- [L2 模块模板](references/l2-module-template.md) - L2 文档详细模板
- [任务执行指南](references/task-execution-guide.md) - 多子代理执行流程

---

## 🤝 贡献 / Contributing

欢迎贡献！请查看我们的贡献指南了解更多细节。

We welcome contributions! Please see our contributing guidelines for more details.

---

## 📄 许可证 / License

MIT License - 详情见 [LICENSE](LICENSE) 文件。

MIT License - See [LICENSE](LICENSE) for details.

---

## 📞 支持 / Support

- 📧 问题反馈：提交 Issue
- 💬 讨论交流：Discord 社区
- 📖 完整文档：[OpenClaw Docs](https://docs.openclaw.ai)

---

*Last updated: 2026-03-09 • Version 1.0.0*
