---
name: mindsdb-mcp-skill
description: MindsDB MCP服务器交互技能，用于通过自然语言查询和操作200+企业级数据源。当用户需要查询数据库、分析数据、创建AI模型、连接数据源（MySQL、PostgreSQL、MongoDB、Excel、CSV、Gmail、Slack等）、执行SQL查询、进行数据预测、构建知识库（RAG）、智能问答、文档检索或任何与数据库交互的任务时使用此技能。即使没有明确提到MindsDB，只要涉及数据库操作、数据分析、数据查询、知识库构建、AI问答或需要连接多个数据源的场景，都应该使用此技能。
---

# MindsDB MCP 交互技能

## 概述

MindsDB是一个AI大规模数据查询引擎，支持连接200+企业级数据源，通过MCP（Model Context Protocol）协议提供统一的数据库操作接口。本技能帮助你通过自然语言与各种数据库交互。

## 架构说明 / Architecture Overview

### 使用方式 / Usage Pattern

本技能采用 **Agent + MCP** 架构，与直接使用MindsDB有所不同：

This skill uses an **Agent + MCP** architecture, which differs from direct MindsDB usage:

**直接使用MindsDB / Direct MindsDB Usage:**
```
用户 → MindsDB GUI/SQL → 数据源/AI模型
User → MindsDB GUI/SQL → Data Sources/AI Models
```

**本技能方式 / This Skill's Approach:**
```
用户（自然语言）→ Claude Agent → MindsDB MCP Server → 数据源/AI模型
User (Natural Language) → Claude Agent → MindsDB MCP Server → Data Sources/AI Models
```

### 核心优势 / Key Advantages

1. **自然语言交互 / Natural Language Interaction**
   - 无需编写SQL语句 / No SQL knowledge required
   - 用日常语言描述需求 / Describe needs in everyday language
   - Agent自动生成并执行SQL / Agent automatically generates and executes SQL

2. **智能推理 / Intelligent Reasoning**
   - 自动理解用户意图 / Automatically understands user intent
   - 智能选择最优方案 / Intelligently selects optimal approach
   - 提供解释和建议 / Provides explanations and recommendations

3. **多步骤自动化 / Multi-step Automation**
   - 自动完成复杂工作流 / Automatically completes complex workflows
   - 无需手动执行多个步骤 / No need to manually execute multiple steps
   - 端到端任务处理 / End-to-end task processing

### 示例对比 / Example Comparison

**传统方式 / Traditional Approach:**
```sql
-- 需要手动编写SQL / Need to write SQL manually
CREATE DATABASE my_postgres 
WITH ENGINE = 'postgres',
PARAMETERS = {"host": "127.0.0.1", ...};

SELECT * FROM my_postgres.products;
```

**本技能方式 / This Skill's Approach:**
```
用户: "连接到Postgres数据库并查询产品信息"
User: "Connect to Postgres database and query product information"

Agent自动完成:
1. 连接数据库 / Connect to database
2. 生成SQL / Generate SQL
3. 执行查询 / Execute query
4. 返回结果 / Return results
```

### 技术架构 / Technical Architecture

```
Claude Agent (对话界面 / Chat Interface)
    ↓ (自然语言 / Natural Language)
MCP Client (内置 / Built-in)
    ↓ (MCP协议 / MCP Protocol)
MindsDB MCP Server (MindsDB提供的MCP接口 / MindsDB MCP Interface)
    ↓ (SQL/API)
MindsDB Server (核心引擎 / Core Engine)
    ↓ (连接器 / Connectors)
数据源 / Data Sources (MySQL, Postgres, 文件 / Files, etc.)
```

### 适用场景 / Use Cases

- ✅ **适合 / Suitable for**: 非技术人员、快速原型开发、自动化工作流
  Non-technical users, rapid prototyping, automated workflows
  
- ✅ **适合 / Suitable for**: 需要自然语言交互的场景
  Scenarios requiring natural language interaction
  
- ⚠️ **可选 / Optional**: 需要精细控制SQL的高级用户
  Advanced users requiring fine-grained SQL control

## 核心能力

### 1. 数据源连接
MindsDB支持连接多种数据源：
- **关系型数据库**: MySQL, PostgreSQL, SQL Server, Oracle, SQLite
- **NoSQL数据库**: MongoDB, Redis, Cassandra
- **云存储**: AWS S3, Google Cloud Storage, Azure Blob
- **文件格式**: CSV, Excel, JSON, Parquet
- **SaaS应用**: Gmail, Slack, Salesforce, Shopify
- **其他**: ClickHouse, Snowflake, BigQuery, Elasticsearch

### 2. 自然语言查询
将自然语言转换为SQL查询，支持：
- 数据检索和筛选
- 聚合分析（SUM, AVG, COUNT等）
- 多表关联查询
- 复杂条件查询
- 数据排序和分页

### 3. AI模型创建
使用MindsDB创建预测模型：
- 时间序列预测
- 分类任务
- 回归分析
- 异常检测
- 推荐系统

### 4. 知识库构建（RAG）
基于检索增强生成技术构建智能知识库：
- 向量存储和检索
- 文档导入和管理
- 智能问答Agent
- 多模态支持（文本、图像、语音）
- 嵌入模型配置

### 5. 智能分析
MindsDB的AI驱动的智能分析能力：
- **自动数据探索**: 自动发现数据模式、异常和趋势
- **智能洞察生成**: 基于数据自动生成业务洞察和建议
- **预测性分析**: 使用机器学习模型进行预测和趋势分析
- **异常检测**: 自动识别数据中的异常模式和异常值
- **因果分析**: 分析变量之间的因果关系
- **推荐系统**: 基于用户行为和模式生成个性化推荐
- **文本分析**: 自然语言处理、情感分析、主题建模
- **时序分析**: 时间序列预测、趋势分解、周期性分析
- **聚类分析**: 无监督学习，发现数据中的自然分组
- **关联规则挖掘**: 发现数据项之间的关联关系

### 6. 数据库管理
- 创建和管理数据库
- 表结构操作
- 数据导入导出
- 数据转换和清洗

## 工作流程

### 第一步：理解用户需求
当用户提出数据库相关需求时，首先理解：
- 想要查询什么数据
- 数据源类型
- 查询条件或分析目标
- 期望的输出格式

### 第二步：构建查询
根据用户需求，选择合适的操作：
1. **简单查询**: 使用自然语言描述直接查询
2. **复杂查询**: 构建SQL语句
3. **AI预测**: 创建MindsDB模型
4. **数据源操作**: 连接或管理数据源

### 第三步：执行查询
使用MindsDB MCP工具执行操作，处理结果。

### 第四步：结果展示
以清晰易懂的方式展示结果，包括：
- 数据表格
- 统计摘要
- 可视化建议
- 后续操作建议

## 常用操作模式

### 模式1: 自然语言查询
用户输入: "查询上个月销售额最高的产品"
处理:
1. 理解查询意图
2. 转换为MindsDB查询
3. 执行并返回结果

### 模式2: SQL查询
用户输入: "SELECT * FROM orders WHERE date > '2024-01-01'"
处理:
1. 验证SQL语法
2. 执行查询
3. 返回结果集

### 模式3: 创建预测模型
用户输入: "预测下个月的销售额"
处理:
1. 确定目标变量
2. 选择合适的模型引擎
3. 训练模型
4. 生成预测

### 模式4: 连接数据源
用户输入: "连接到MySQL数据库"
处理:
1. 获取连接参数
2. 创建数据源连接
3. 验证连接
4. 返回连接状态

### 模式5: 构建知识库
用户输入: "创建一个技术文档知识库"
处理:
1. 创建RAG数据库
2. 导入文档内容
3. 配置嵌入模型
4. 创建智能Agent

### 模式6: 智能问答
用户输入: "根据技术文档回答设备报错0xE1怎么处理"
处理:
1. 使用Agent查询知识库
2. 检索相关文档
3. 生成回答
4. 返回结果

### 模式7: 智能数据分析
用户输入: "分析销售数据，找出增长趋势和异常"
处理:
1. 自动探索数据
2. 识别模式和趋势
3. 检测异常值
4. 生成洞察报告
5. 提供可视化建议

### 模式8: 预测性分析
用户输入: "预测下季度的销售额"
处理:
1. 选择合适的预测模型
2. 训练模型
3. 生成预测结果
4. 提供置信区间
5. 解释预测依据

### 模式9: 推荐系统
用户输入: "为用户推荐可能感兴趣的产品"
处理:
1. 分析用户行为数据
2. 创建推荐模型
3. 生成个性化推荐
4. 计算推荐得分
5. 返回推荐列表

## 最佳实践

### 1. 查询优化
- 使用索引列进行筛选
- 限制返回的数据量
- 避免全表扫描
- 合理使用聚合函数

### 2. 错误处理
- 捕获并解释错误信息
- 提供修复建议
- 记录错误日志
- 优雅降级

### 3. 安全考虑
- 验证SQL注入风险
- 限制敏感数据访问
- 使用参数化查询
- 审计查询日志

### 4. 性能优化
- 批量操作优于单条操作
- 使用连接池
- 缓存常用查询
- 异步执行长时间任务

## 输出格式

### 查询结果
使用清晰的表格格式展示数据，包括：
- 列名
- 数据类型
- 行数
- 执行时间

### 错误信息
提供详细的错误说明：
- 错误类型
- 错误位置
- 可能原因
- 解决方案

### 操作状态
显示操作进度和状态：
- 进度百分比
- 当前步骤
- 预计剩余时间
- 完成状态

## 示例场景

### 场景1: 销售数据分析
用户: "分析2024年各地区的销售趋势"
操作:
1. 查询2024年销售数据
2. 按地区分组
3. 计算趋势指标
4. 生成分析报告

### 场景2: 客户行为预测
用户: "预测哪些客户可能会流失"
操作:
1. 创建流失预测模型
2. 训练模型
3. 生成预测结果
4. 提供干预建议

### 场景3: 库存管理
用户: "查询库存不足的产品"
操作:
1. 查询当前库存
2. 对比安全库存水平
3. 识别缺货产品
4. 生成补货建议

### 场景4: 技术支持知识库
用户: "创建一个技术文档知识库，用于智能问答"
操作:
1. 创建RAG数据库
2. 导入PDF技术文档
3. 配置嵌入模型
4. 创建技术支持Agent
5. 测试问答功能

### 场景5: 智能客服系统
用户: "根据产品手册回答用户问题"
操作:
1. 查询知识库
2. 检索相关文档
3. 使用Agent生成回答
4. 提供解决方案

### 场景6: 智能销售分析
用户: "分析销售数据，找出增长机会和风险"
操作:
1. 自动探索销售数据
2. 识别增长趋势和模式
3. 检测异常和风险信号
4. 生成业务洞察
5. 提供行动建议

### 场景7: 客户流失预测
用户: "预测哪些客户可能会流失，并提供挽留建议"
操作:
1. 创建流失预测模型
2. 分析客户行为模式
3. 识别高风险客户
4. 生成挽留策略
5. 预测挽留效果

### 场景8: 产品推荐
用户: "为用户推荐他们可能喜欢的产品"
操作:
1. 分析用户历史行为
2. 创建推荐模型
3. 生成个性化推荐
4. 计算推荐置信度
5. 返回推荐列表和理由

### 场景9: 工业设备监控
用户: "获取工业设备的运行情况"
操作:
1. 连接TDengine时序数据库
2. 查询实时监测数据（温度、压力、流量等）
3. 查询设备运行状态（电机、阀门、传感器等）
4. 分析设备效率和运行参数
5. 检测异常指标和告警
6. 生成运行报告和建议

**说明:** 示例中的表名和字段名仅为演示，Agent会自动适配你的实际数据库结构。

**示例查询:**
```
用户: "查询1号车间过去24小时的温度和压力数据"
Agent:
1. 连接TDengine数据库
2. 自动查询表结构，发现实际表名和字段
3. 根据实际结构生成SQL:
   SELECT ts, temperature, pressure 
   FROM your_actual_table_name 
   WHERE location_id = 'workshop_001' 
     AND ts > NOW() - INTERVAL 24 HOUR
4. 返回结果和趋势分析

用户: "检查所有设备的运行状态，找出异常设备"
Agent:
1. 查询设备状态表（自动发现实际表名）
2. 根据实际字段名筛选异常设备
3. 分析异常原因
4. 提供维护建议
```

### 场景10: 工业物联网监控
用户: "分析工厂生产线的能耗情况"
操作:
1. 连接时序数据库（TDengine/InfluxDB）
2. 查询设备能耗数据
3. 计算能耗趋势和峰值
4. 识别能耗异常
5. 生成节能建议

## 注意事项

1. **数据源连接**: 需要用户提供正确的连接参数
2. **权限管理**: 确保有足够的数据库权限
3. **数据安全**: 不要暴露敏感信息
4. **性能考虑**: 大数据量查询可能需要较长时间
5. **模型训练**: AI模型训练需要时间和计算资源

## 实际案例

### 工业设备监控案例

**案例背景**: 使用MindsDB AI Agent分析TDengine时序数据库中的工业设备数据

**数据规模**:
- 约200个不同设备
- 约10,000条小时级数据记录
- 7天的监测数据

**设备类型**:
- 温度监测设备 (TEMP系列)
- 压力监测设备 (PRESS系列)
- 控制阀门设备 (VALVE系列)
- 电机设备 (MOTOR系列)
- 流量监测设备 (FLOW系列)

**Agent执行的操作**:
1. 自动发现表结构 (`sql_db_list_tables`, `sql_db_schema`)
2. 查询设备列表 (约200个设备)
3. 统计设备数据 (数据点数、平均值、标准差)
4. 分析设备相关性
5. 生成综合分析报告

**关键发现**:
- Agent自动适配TDengine特有语法
- 自动处理错误并调整查询策略
- 智能生成分析报告
- 支持自然语言交互

**详细案例**: 参见 [industrial-monitoring-case.md](references/industrial-monitoring-case.md)

## 扩展功能

### 高级查询
- 窗口函数
- 递归查询
- 存储过程调用
- 自定义函数

### 集成能力
- 与其他MCP服务器集成
- API调用
- 数据管道
- 实时流处理

### 可视化
- 图表生成
- 仪表板创建
- 报告导出
- 数据导出

## 故障排除

### 常见问题
1. **连接失败**: 检查连接参数和网络
2. **查询超时**: 优化查询或增加超时时间
3. **权限错误**: 检查数据库权限设置
4. **语法错误**: 验证SQL语法
5. **性能问题**: 分析查询计划，添加索引

### 调试技巧
- 启用查询日志
- 使用EXPLAIN分析查询
- 分步执行复杂查询
- 测试子查询

## 参考资料

### 官方文档
- MindsDB官方文档: https://docs.mindsdb.com
- MCP协议规范: https://modelcontextprotocol.io

### 技能参考文档
详细的技术文档位于 `references/` 目录：

- **mindsdb-tools.md**: MindsDB MCP工具完整参考
  - 可用工具列表和参数说明
  - 支持的数据源
  - 查询示例
  - 模型创建示例
  - 错误处理指南

- **data-sources.md**: 200+数据源配置指南
  - 关系型数据库配置（MySQL、PostgreSQL、Oracle等）
  - NoSQL数据库配置（MongoDB、Redis、Elasticsearch等）
  - 云数据库配置（AWS RDS、Google Cloud SQL、Azure等）
  - 文件格式导入（CSV、Excel、JSON、Parquet）
  - SaaS应用连接（Gmail、Slack、Salesforce等）
  - 连接池、SSL/TLS、代理配置

- **sql-examples.md**: SQL查询示例大全
  - 基础查询（SELECT、WHERE、排序、限制）
  - 聚合查询（COUNT、SUM、AVG、GROUP BY）
  - 连接查询（INNER JOIN、LEFT JOIN、多表连接）
  - 子查询（标量、IN、EXISTS、FROM子查询）
  - 窗口函数（ROW_NUMBER、RANK、LAG/LEAD）
  - CASE表达式和实用函数
  - 性能优化技巧

- **sdk-api.md**: SDK和API参考
  - Python SDK使用（连接、创建模型、查询、异步操作）
  - JavaScript SDK使用（连接、创建模型、查询）
  - REST API调用（认证、创建模型、预测、执行SQL）
  - MySQL协议连接
  - MongoDB协议连接
  - 高级功能（版本管理、监控、批量操作）
  - 错误处理和最佳实践

- **knowledge-base.md**: 知识库（RAG）构建指南
  - RAG核心概念和组件
  - 创建RAG数据库和配置嵌入模型
  - 从PDF、文本、数据库、网页导入知识
  - 创建智能Agent（基础、高级、多知识库）
  - 查询知识库和智能问答
  - 向量存储优化（Chroma、FAISS）
  - 多模态支持（图像、语音）
  - 实际应用场景（技术支持、产品推荐、法律、医疗）
  - 性能优化、安全、监控

- **mlops-advanced.md**: MLOps和高级功能指南
  - 模型部署（基础、批量、实时推理端点）
  - 模型监控（性能、数据漂移、预测质量、资源使用）
  - 模型版本管理（创建、比较、回滚、标签）
  - A/B测试（创建、监控、选择获胜模型）
  - MLflow集成（连接、记录模型、加载模型、注册）
  - dbt集成（配置、宏、数据质量检查）
  - Airflow集成（DAG创建、监控任务）
  - 批处理（批量预测、训练、评估）
  - 模型解释（特征重要性、SHAP值、预测解释）
  - 自动化工作流（自动重训练、模型选择、告警）
  - 性能优化（缓存、批处理、查询优化）
  - 安全和合规（访问控制、数据隐私、审计）

- **streaming-pipelines.md**: 实时流处理和数据管道指南
  - 实时流处理（Kafka、AWS Kinesis、RabbitMQ）
  - 流式数据消费和实时预测
  - 实时聚合分析和统计
  - 数据管道（ETL/ELT、增量管道、事件驱动）
  - 时序数据处理（InfluxDB、时序预测、异常检测）
  - 图数据库集成（Neo4j、图查询、图神经网络）
  - 多租户支持（租户隔离、资源配额、租户监控）
  - 集群管理（节点配置、负载均衡、集群监控）
  - 高可用性（主从复制、故障转移、数据备份）
  - 性能优化（流处理优化、索引优化、查询优化）
  - 监控和告警（流处理监控、管道监控、告警配置）

- **intelligent-analysis.md**: 智能分析指南
  - 自动数据探索（数据概览、质量检查、分布分析、相关性分析）
  - 智能洞察生成（自动洞察发现、趋势分析、模式识别、业务洞察报告）
  - 预测性分析（时间序列预测、回归预测、分类预测、预测结果查询）
  - 异常检测（统计异常检测、时序异常检测、异常分析）
  - 因果分析（因果推断、因果关系发现、反事实分析）
  - 推荐系统（协同过滤、内容推荐、混合推荐、推荐查询）
  - 文本分析（情感分析、主题建模、命名实体识别、文本分类）
  - 时序分析（趋势分解、周期性分析、变点检测）
  - 聚类分析（K-Means、层次聚类、DBSCAN、聚类分析）
  - 关联规则挖掘（Apriori、FP-Growth、关联规则查询）
  - 智能分析工作流（端到端分析、自动化报告）
  - 可视化集成（图表生成、仪表板创建）
  - 性能优化（分析缓存、并行分析、增量分析）

### 其他参考
- SQL参考手册
- 数据源连接指南
- 机器学习最佳实践
- MLOps工作流程
- 实时数据处理指南
- 智能分析最佳实践
