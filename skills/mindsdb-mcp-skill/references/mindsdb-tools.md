# MindsDB MCP 工具参考

## 可用工具

### 1. execute_query
执行SQL查询语句

**参数:**
- `query` (string): SQL查询语句

**示例:**
```sql
SELECT * FROM employees WHERE department = 'Sales'
```

### 2. create_model
创建AI预测模型

**参数:**
- `model_name` (string): 模型名称
- `target` (string): 目标预测列
- `data_source` (string): 数据源名称
- `engine` (string): 模型引擎（可选）
- `options` (object): 模型参数（可选）

**示例:**
```sql
CREATE MODEL mindsdb.sales_predictor
PREDICT sales_amount
FROM my_database.sales_data
USING engine = 'lightwood'
```

### 3. connect_database
连接到外部数据库

**参数:**
- `database_type` (string): 数据库类型（mysql, postgresql, mongodb等）
- `host` (string): 数据库主机
- `port` (number): 端口号
- `database` (string): 数据库名称
- `username` (string): 用户名
- `password` (string): 密码

**示例:**
```sql
CREATE DATABASE my_mysql
WITH ENGINE = 'mysql',
PARAMETERS = {
  'host': 'localhost',
  'port': 3306,
  'database': 'mydb',
  'user': 'root',
  'password': 'password'
}
```

### 4. list_databases
列出所有可用的数据库

**参数:** 无

**返回:** 数据库列表

### 5. list_tables
列出指定数据库中的所有表

**参数:**
- `database` (string): 数据库名称

**返回:** 表列表

### 6. describe_table
获取表结构信息

**参数:**
- `database` (string): 数据库名称
- `table` (string): 表名

**返回:** 表结构（列名、类型、约束等）

### 7. import_data
导入数据到MindsDB

**参数:**
- `source` (string): 数据源路径或连接
- `target_table` (string): 目标表名
- `format` (string): 数据格式（csv, json, parquet等）

**示例:**
```sql
IMPORT FROM 'data.csv'
INTO my_database.imported_data
```

### 8. export_data
导出数据

**参数:**
- `query` (string): 查询语句
- `destination` (string): 导出路径
- `format` (string): 导出格式

**示例:**
```sql
EXPORT (SELECT * FROM sales WHERE date > '2024-01-01')
TO 'sales_export.csv'
FORMAT 'csv'
```

## 支持的数据源

### 关系型数据库
- MySQL
- PostgreSQL
- SQL Server
- Oracle
- SQLite
- MariaDB

### NoSQL数据库
- MongoDB
- Redis
- Cassandra
- Elasticsearch
- CouchDB

### 云数据库
- Amazon RDS
- Google Cloud SQL
- Azure Database
- Snowflake
- BigQuery
- Redshift

### 文件格式
- CSV
- Excel (.xlsx, .xls)
- JSON
- Parquet
- Avro
- XML

### SaaS应用
- Gmail
- Google Sheets
- Slack
- Salesforce
- Shopify
- HubSpot
- Zendesk

### 其他
- ClickHouse
- Apache Hive
- Apache Drill
- Presto
- Trino

## 查询示例

### 基础查询
```sql
-- 查询所有数据
SELECT * FROM table_name

-- 条件查询
SELECT * FROM table_name WHERE condition

-- 排序
SELECT * FROM table_name ORDER BY column_name DESC

-- 限制结果
SELECT * FROM table_name LIMIT 10
```

### 聚合查询
```sql
-- 计数
SELECT COUNT(*) FROM table_name

-- 求和
SELECT SUM(amount) FROM table_name

-- 平均值
SELECT AVG(price) FROM table_name

-- 分组统计
SELECT category, COUNT(*) as count
FROM table_name
GROUP BY category
```

### 连接查询
```sql
-- 内连接
SELECT a.*, b.*
FROM table_a a
INNER JOIN table_b b ON a.id = b.a_id

-- 左连接
SELECT a.*, b.*
FROM table_a a
LEFT JOIN table_b b ON a.id = b.a_id
```

### 子查询
```sql
-- 子查询
SELECT * FROM table_name
WHERE id IN (SELECT id FROM other_table WHERE condition)

-- EXISTS
SELECT * FROM table_name a
WHERE EXISTS (SELECT 1 FROM other_table b WHERE b.a_id = a.id)
```

## 模型创建示例

### 回归模型
```sql
CREATE MODEL mindsdb.price_predictor
PREDICT price
FROM my_database.houses
USING
  engine = 'lightwood',
  problem_type = 'regression',
  target = 'price',
  input_features = ['area', 'bedrooms', 'bathrooms', 'location']
```

### 分类模型
```sql
CREATE MODEL mindsdb.churn_predictor
PREDICT churn
FROM my_database.customers
USING
  engine = 'xgboost',
  problem_type = 'classification',
  target = 'churn',
  input_features = ['age', 'usage', 'support_calls', 'plan_type']
```

### 时间序列预测
```sql
CREATE MODEL mindsdb.sales_forecast
PREDICT sales
FROM my_database.daily_sales
USING
  engine = 'prophet',
  problem_type = 'time_series',
  target = 'sales',
  time_column = 'date',
  horizon = 30
```

## 错误处理

### 常见错误
1. **连接错误**: 检查连接参数和网络
2. **语法错误**: 验证SQL语法
3. **权限错误**: 检查数据库权限
4. **超时错误**: 优化查询或增加超时时间
5. **内存错误**: 减少数据量或分批处理

### 错误处理建议
- 捕获错误信息
- 提供清晰的错误说明
- 给出修复建议
- 记录错误日志
