# MindsDB MCP Skill

一个基于MindsDB MCP服务器的Claude技能，支持通过自然语言操作200+企业级数据源。

A Claude skill based on MindsDB MCP server, supporting natural language operations on 200+ enterprise data sources.

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

| 特性 / Feature | 直接使用MindsDB / Direct Usage | 本技能 / This Skill |
|--------------|---------------------------|-------------------|
| 交互方式 / Interaction | SQL语句 / SQL statements | 自然语言 / Natural language |
| 技能要求 / Skill Required | 需要SQL知识 / SQL knowledge required | 无需SQL / No SQL needed |
| 学习曲线 / Learning Curve | 较陡 / Steep | 平缓 / Gentle |
| 自动化程度 / Automation Level | 手动 / Manual | 自动 / Automatic |
| 适用人群 / Target Users | 技术人员 / Technical users | 所有人 / Everyone |

### 示例对比 / Example Comparison

**传统方式 / Traditional Approach:**
```sql
-- 需要手动编写SQL / Need to write SQL manually
CREATE DATABASE my_postgres 
WITH ENGINE = 'postgres',
PARAMETERS = {"host": "127.0.0.1", "port": 5432, ...};

CREATE MODEL churn_predictor
FROM my_postgres(SELECT * FROM customers)
PREDICT churn;

SELECT * FROM churn_predictor WHERE customer_id = 123;
```

**本技能方式 / This Skill's Approach:**
```
用户: "连接到Postgres数据库，预测客户123是否会流失"
User: "Connect to Postgres database, predict if customer 123 will churn"

Agent自动完成 / Agent automatically:
1. 连接数据库 / Connect to database
2. 创建预测模型 / Create prediction model
3. 执行预测 / Execute prediction
4. 返回结果和解释 / Return results with explanation
```

### 技术架构 / Technical Architecture

```
┌─────────────────────────────────────────────────────────┐
│  用户 / User                                             │
│  (自然语言交互 / Natural Language Interaction)           │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  Claude Agent                                           │
│  (理解意图、生成SQL、执行任务 /                          │
│   Understand intent, generate SQL, execute tasks)       │
└────────────────────┬────────────────────────────────────┘
                     ↓ (MCP Protocol)
┌─────────────────────────────────────────────────────────┐
│  MindsDB MCP Server                                     │
│  (MCP协议接口 / MCP Protocol Interface)                 │
└────────────────────┬────────────────────────────────────┘
                     ↓ (SQL/API)
┌─────────────────────────────────────────────────────────┐
│  MindsDB Server                                         │
│  (核心引擎 / Core Engine)                               │
└────────────────────┬────────────────────────────────────┘
                     ↓ (Connectors)
┌─────────────────────────────────────────────────────────┐
│  数据源 / Data Sources                                  │
│  MySQL • PostgreSQL • MongoDB • Files • SaaS • ...     │
└─────────────────────────────────────────────────────────┘
```

### 适用场景 / Use Cases

**✅ 适合使用本技能的场景 / Scenarios Suitable for This Skill:**

1. **非技术人员 / Non-technical Users**
   - 产品经理需要查询数据 / Product managers need to query data
   - 业务分析师进行数据分析 / Business analysts perform data analysis
   - 运营人员生成报表 / Operations staff generate reports

2. **快速原型开发 / Rapid Prototyping**
   - 快速验证数据假设 / Quickly validate data hypotheses
   - 探索性数据分析 / Exploratory data analysis
   - MVP开发 / MVP development

3. **自动化工作流 / Automated Workflows**
   - 定期数据报告 / Regular data reports
   - 自动化预测任务 / Automated prediction tasks
   - 智能告警系统 / Intelligent alerting systems

**⚠️ 可选直接使用MindsDB的场景 / Scenarios for Direct MindsDB Usage:**

1. **高级SQL需求 / Advanced SQL Requirements**
   - 复杂的SQL优化 / Complex SQL optimization
   - 精细的查询控制 / Fine-grained query control
   - 性能调优 / Performance tuning

2. **批量操作 / Batch Operations**
   - 大规模数据迁移 / Large-scale data migration
   - 批量模型训练 / Batch model training
   - 系统管理任务 / System administration tasks

## 功能特性

- 🔌 **多数据源支持**: 连接MySQL、PostgreSQL、MongoDB、Excel、CSV、Gmail、Slack等200+数据源
- 🤖 **AI模型创建**: 使用MindsDB创建预测和分类模型
- 💬 **自然语言查询**: 将自然语言转换为SQL查询
- 📊 **数据分析**: 执行复杂的数据分析和聚合操作
- 🧠 **知识库构建（RAG）**: 构建智能知识库，支持文档检索和智能问答
- 🔍 **智能问答Agent**: 基于知识库的AI问答系统
- 🚀 **MLOps功能**: 模型部署、监控、版本管理、A/B测试
- 🔄 **CI/CD集成**: 支持MLflow、dbt、Airflow等工具集成
- 🌊 **实时流处理**: 支持Kafka、Kinesis、RabbitMQ等实时数据处理
- 📈 **数据管道**: 完整的ETL/ELT数据管道和事件驱动架构
- 🔒 **安全可靠**: 支持参数化查询和权限管理

## 安装步骤

### 1. 安装MindsDB

MindsDB已内置MCP服务器功能，无需单独安装MCP服务器。

```bash
# 安装MindsDB
pip install mindsdb

# 启动MindsDB
mindsdb
```

### 2. 配置Claude Desktop

编辑Claude Desktop配置文件：

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

添加以下配置：

```json
{
  "mcpServers": {
    "mindsdb": {
      "type": "url",
      "url": "http://localhost:47334/mcp/sse",
      "name": "mindsdb-mcp",
      "authorization_token": "your-mindsdb-token"
    }
  }
}
```

### 3. 重启Claude Desktop

重启Claude Desktop以加载MCP服务器配置。

### 4. 验证安装

在Claude Desktop中测试：

```
列出所有可用的数据库
```

## 使用示例

### 查询数据

```
查询employees表中所有销售部门的员工
```

### 创建预测模型

```
创建一个模型来预测下个月的销售额
```

### 连接数据源

```
连接到我的MySQL数据库，主机是localhost，端口3306
```

### 数据分析

```
分析2024年各地区的销售趋势
```

### 构建知识库

```
创建一个技术文档知识库
```

### 智能问答

```
根据技术文档回答设备报错0xE1怎么处理
```

## 与其他框架集成

### CrewAI集成

CrewAI是一个强大的多Agent协作框架，支持通过MCP协议集成外部工具。以下是使用本技能与CrewAI集成的几种方式：

#### 方法一：使用 MCP DSL（推荐）

```python
from crewai import Agent, Task, Crew, Process
import os

# 创建集成MindsDB MCP的Agent
mindsdb_agent = Agent(
    role="数据库分析师",
    goal="通过自然语言查询和分析数据库",
    backstory="专业的数据库分析师，精通SQL和数据分析",
    
    # 使用MCP DSL直接连接
    mcps=[
        f"https://cloud.mindsdb.com/mcp?api_key={os.getenv('MINDSDB_API_KEY')}"
    ],
    
    verbose=True
)

# 创建任务
task = Task(
    description="查询sensor_data表，分析温度异常",
    expected_output="温度异常分析报告",
    agent=mindsdb_agent
)

# 执行
crew = Crew(agents=[mindsdb_agent], tasks=[task])
result = crew.kickoff()
```

#### 方法二：使用 MCPServerAdapter（本地MindsDB）

```python
from crewai import Agent
from crewai_tools import MCPServerAdapter
import os

# 直接使用MindsDB内置的MCP服务器
# 注意：需要先启动MindsDB服务

# 使用上下文管理器连接
with MCPServerAdapter("http://localhost:47334/mcp/sse") as mcp_tools:
    print(f"可用工具: {[tool.name for tool in mcp_tools]}")
    
    agent = Agent(
        role="数据分析师",
        goal="分析数据库数据",
        backstory="专业的数据分析师",
        tools=mcp_tools,
        verbose=True
    )
```

#### 方法三：筛选特定工具

```python
# 直接使用MindsDB内置的MCP服务器
from crewai import Agent
from crewai_tools import MCPServerAdapter

# 只加载SQL相关工具
with MCPServerAdapter("http://localhost:47334/mcp/sse", "sql_db_query", "sql_db_schema", "sql_db_list_tables") as mcp_tools:
    sql_agent = Agent(
        role="SQL专家",
        goal="执行SQL查询",
        backstory="数据库查询专家",
        tools=mcp_tools,
        verbose=True
    )
```

#### 方法四：与 CrewBase 结合

```python
from crewai import Agent, CrewBase
import os

@CrewBase
class MindsDBCrew:
    """集成MindsDB MCP的Crew"""
    
    # 直接使用MindsDB内置的MCP服务器
    mcp_server_params = ["http://localhost:47334/mcp/sse"]
    
    @agent
    def data_analyst(self):
        return Agent(
            role="数据分析师",
            goal="分析数据库数据",
            backstory="专业的数据分析师",
            tools=self.get_mcp_tools(),
            verbose=True
        )
    
    @agent
    def query_specialist(self):
        return Agent(
            role="查询专家",
            goal="执行SQL查询",
            backstory="SQL查询专家",
            tools=self.get_mcp_tools("sql_db_query", "sql_db_schema"),
            verbose=True
        )
```

#### 完整示例：多Agent协作

```python
from crewai import Agent, Task, Crew, Process

# Agent 1: 数据库连接专家
connection_agent = Agent(
    role="数据库连接专家",
    goal="连接和管理数据库连接",
    backstory="精通各种数据库连接和配置",
    mcps=["http://localhost:47334/mcp/sse"],
    verbose=True
)

# Agent 2: 数据分析专家
analysis_agent = Agent(
    role="数据分析专家",
    goal="分析设备数据并发现异常",
    backstory="资深数据分析师，擅长时序数据分析",
    mcps=["http://localhost:47334/mcp/sse#sql_db_query"],
    verbose=True
)

# Agent 3: 报告生成专家
report_agent = Agent(
    role="报告生成专家",
    goal="生成专业的分析报告",
    backstory="技术文档撰写专家",
    verbose=True
)

# 创建任务
tasks = [
    Task(
        description="连接TDengine数据库，验证sensor_data表是否存在",
        expected_output="连接状态和表结构信息",
        agent=connection_agent
    ),
    Task(
        description="分析sensor_data表，找出温度超过80度的异常设备",
        expected_output="数据分析结果和异常设备列表",
        agent=analysis_agent
    ),
    Task(
        description="生成包含维护建议的专业报告",
        expected_output="结构化的分析报告",
        agent=report_agent
    )
]

# 创建并执行Crew
crew = Crew(
    agents=[connection_agent, analysis_agent, report_agent],
    tasks=tasks,
    process=Process.sequential,
    verbose=True
)

result = crew.kickoff()
print(result)
```

#### 环境配置

```bash
# 安装依赖
pip install crewai crewai-tools[mcp]

# 启动MindsDB服务
mindsdb
```

#### 最佳实践

1. **使用特定工具筛选**: 通过 `#` 语法只加载需要的工具
   ```python
   mcps=["https://cloud.mindsdb.com/mcp?api_key=key#sql_db_query"]
   ```

2. **安全处理密钥**: 使用环境变量，不要硬编码
   ```python
   api_key = os.getenv("MINDSDB_API_KEY")
   ```

3. **配置备用服务器**: 确保任务不会因单点故障失败
   ```python
   mcps=[
       "https://cloud.mindsdb.com/mcp?api_key=primary_key",
       "https://backup.mindsdb.com/mcp?api_key=backup_key"
   ]
   ```

4. **合理设置超时**: CrewAI默认连接超时10秒，执行超时30秒

## 支持的数据源

### 关系型数据库
- MySQL, PostgreSQL, SQL Server, Oracle, SQLite

### NoSQL数据库
- MongoDB, Redis, Cassandra, Elasticsearch

### 云数据库
- AWS RDS, Google Cloud SQL, Azure Database

### 文件格式
- CSV, Excel, JSON, Parquet

### SaaS应用
- Gmail, Slack, Salesforce, Shopify

## 文档结构

```
mindsdb-skill/
├── SKILL.md                    # 主技能文件
├── README.md                   # 项目说明
├── INSTALL.md                  # 安装配置指南
├── USAGE.md                    # 使用示例
├── TROUBLESHOOTING.md          # 故障排除
├── evals/
│   └── evals.json             # 测试用例
└── references/
    ├── mindsdb-tools.md       # 工具参考文档
    ├── data-sources.md        # 数据源配置
    ├── sql-examples.md        # SQL查询示例
    ├── sdk-api.md            # SDK和API参考
    ├── knowledge-base.md     # 知识库构建指南
    ├── mlops-advanced.md     # MLOps和高级功能
    ├── streaming-pipelines.md # 实时流处理和数据管道
    └── intelligent-analysis.md # 智能分析指南 ✨
```

## 常见问题

### Q: 如何获取MindsDB API密钥？
A: 访问 https://cloud.mindsdb.com 注册账号并获取API密钥。

### Q: 支持哪些数据库？
A: 支持200+数据源，包括MySQL、PostgreSQL、MongoDB等主流数据库。

### Q: 如何处理大数据量查询？
A: 使用LIMIT限制结果数量，或使用分页查询。

### Q: 可以创建自定义模型吗？
A: 可以，MindsDB支持多种模型引擎，包括Lightwood、XGBoost等。

## 贡献指南

欢迎提交问题和改进建议！

## 许可证

MIT License

## 联系方式

- MindsDB文档: https://docs.mindsdb.com
- MCP协议: https://modelcontextprotocol.io
