# Changelog

All notable changes to `module-analyzer-generate-doc` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-03-07

### 🎉 Added / 新增功能

#### Single Module Deep Analysis / 单模块深度分析
- **Focused module scanning** - Deep analysis of single Java/Maven module (not entire project)
  - **专注模块扫描** - 深度分析单个 Java/Maven 模块（而非整个项目）
- **L3 file-level documentation** - Detailed business logic explanation for each class with business logic
  - **L3 文件级文档** - 为每个包含业务逻辑的类生成详细业务解释
- **L2 module-level documentation** - Module architecture index, core business flows, dependency summary
  - **L2 模块级文档** - 模块架构索引、核心业务流程、依赖关系汇总

#### Intelligent Task Execution / 智能任务执行
- **Multi-subagent parallel processing** - Default 5 parallel subagents, 10-16 files per chunk
  - **多子代理并行处理** - 默认 5 个并行子代理，每片 10-16 个文件
- **Automatic context compression** - Compress every 2-3 files to prevent overflow
  - **自动上下文压缩** - 每 2-3 个文件压缩一次防止溢出
- **Automatic retry with exponential backoff** - Max 3 retries, 30s→60s→120s delay
  - **自动重试带指数退避** - 最多 3 次重试，30 秒→60 秒→120 秒延迟
- **Checkpoint & resume support** - State file tracks progress for crash recovery
  - **断点续传支持** - 状态文件跟踪进度用于崩溃恢复
- **Scheduled progress reporting** - Report every 20 minutes
  - **定时进度汇报** - 每 20 分钟汇报进度

#### Smart Skip Mechanism / 智能跳过机制
- **Pure data objects skip** - Entity/DTO/VO with only getters/setters
  - **纯数据对象跳过** - 仅 getter/setter 的 Entity/DTO/VO
- **Enum definitions skip** - Enums without complex methods
  - **枚举定义跳过** - 无复杂方法的枚举
- **Simple parameter objects skip** - Basic parameter objects
  - **简单参数对象跳过** - 基础参数对象
- **Test classes skip** - Classes with @Test annotations
  - **测试类跳过** - 包含@Test 注解的类
- **Interface definitions skip** - Interfaces with implementations in Impl
  - **接口定义跳过** - 实现位于 Impl 中的接口

#### Documentation Quality Assurance / 文档质量保证
- **Natural language business description** - No code snippets, accessible to non-programmers
  - **自然语言业务描述** - 无代码片段，非程序员也可理解
- **Method-level flow analysis** - Trigger conditions, data processing, business rules, exception handling
  - **方法级流程分析** - 触发条件、数据处理、业务规则、异常处理
- **Domain knowledge explanation** - Business concepts and terminology
  - **领域知识解释** - 业务概念和术语说明
- **Design intent documentation** - Why designed this way, what problems solved
  - **设计意图文档** - 为什么这样设计，解决了什么问题

### 🔧 Changed / 变更

#### Configuration / 配置
- **Default chunk size** - 10-16 files per subagent (optimized for context limits)
  - **默认分片大小** - 每个子代理 10-16 个文件（针对上下文限制优化）
- **Max parallel subagents** - 5 (balanced for performance and stability)
  - **最大并行子代理数** - 5 个（性能和稳定性平衡）
- **Context threshold** - 40% warning, 50% force compression
  - **上下文阈值** - 40% 预警，50% 强制压缩
- **Compression frequency** - Every 2-3 files
  - **压缩频率** - 每 2-3 个文件
- **Simple file threshold** - 50 lines (files below skipped)
  - **简单文件阈值** - 50 行（低于此值跳过）
- **Timeout** - 300-900 seconds based on chunk size
  - **超时时间** - 根据分片大小 300-900 秒

#### Documentation Templates / 文档模板
- **L3 file template** - Comprehensive business logic explanation format
  - **L3 文件模板** - 全面的业务逻辑解释格式
- **L2 module template** - Module architecture and business flow index
  - **L2 模块模板** - 模块架构和业务流程索引
- **Task execution guide** - Detailed subagent workflow documentation
  - **任务执行指南** - 详细的子代理工作流程文档

### 📚 Documentation / 文档

- **SKILL.md** - Complete skill documentation with workflow examples
  - **SKILL.md** - 完整技能文档含工作流程示例
- **references/l2-module-template.md** - L2 module documentation template
  - **references/l2-module-template.md** - L2 模块文档模板
- **references/l3-file-template.md** - L3 file documentation template
  - **references/l3-file-template.md** - L3 文件文档模板
- **references/task-execution-guide.md** - Multi-subagent execution guide
  - **references/task-execution-guide.md** - 多子代理执行指南

### ⚙️ Technical Details / 技术细节

#### Performance Benchmarks / 性能基准

| Module Size | L3 Generation | L2 Generation | Total |
|-------------|---------------|---------------|-------|
| 20 files | ~5 min | ~2 min | ~7 min |
| 50 files | ~12 min | ~4 min | ~16 min |
| 80 files | ~20 min | ~5 min | ~25 min |
| 150 files | ~40 min | ~8 min | ~48 min |

#### Token Consumption / Token 消耗

| Phase | Per File/Module | Total (80 files) |
|-------|-----------------|------------------|
| L3 Generation | 200k tokens/file | 16M tokens |
| L2 Generation | 350k tokens/module | 350k tokens |

### 🎯 Use Cases / 使用场景

- **Single module deep dive** - Understand a specific module's business logic
  - **单模块深度理解** - 理解特定模块的业务逻辑
- **New team member onboarding** - Quick ramp-up on module responsibilities
  - **新成员入职** - 快速了解模块职责
- **Code review preparation** - Generate documentation before review
  - **代码评审准备** - 评审前生成文档
- **Legacy code understanding** - Decode complex business logic in existing modules
  - **遗留代码理解** - 解码现有模块中的复杂业务逻辑
- **Incremental updates** - Update docs when module code changes
  - **增量更新** - 模块代码变更时更新文档

---

## Version History / 版本历史

| Version | Release Date | Key Feature / 核心特性 |
|---------|-------------|----------------------|
| 1.0.0 | 2026-03-07 | Initial Release / 初始版本 |

---

## Migration Guide / 迁移指南

### First Time Use / 首次使用

1. Ensure Python 3.x and PowerShell 5.1+ are installed
   确保已安装 Python 3.x 和 PowerShell 5.1+

2. Configure module path in TOOLS.md:
   在 TOOLS.md 中配置模块路径：

```markdown
### Module Analyzer - Java 单模块深度文档生成器

- 默认分片大小：10-16 文件/子代理
- 最大并行：5 个子代理
- 上下文阈值：40% 预警，50% 强制压缩
- 简单文件阈值：50 行
- 超时时间：300-900 秒
```

3. Run the skill with module path:
   使用模块路径运行技能：

```
分析 E:\projects\mgmt-api-cp 的 admin-api 模块，生成业务逻辑文档
```

---

## Contributing / 贡献

We welcome contributions! Please see our contributing guidelines for more details.

我们欢迎贡献！详情请查看我们的贡献指南。

---

## License / 许可证

MIT License - See [LICENSE](LICENSE) for details.

MIT 许可证 - 详情见 [LICENSE](LICENSE) 文件。
