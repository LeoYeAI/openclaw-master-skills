# MindsDB 数据源配置参考

## 关系型数据库

### MySQL

```sql
CREATE DATABASE mysql_connection
WITH ENGINE = 'mysql',
PARAMETERS = {
  'host': 'localhost',
  'port': 3306,
  'database': 'mydb',
  'user': 'root',
  'password': 'password'
}
```

**参数说明:**
- `host`: 数据库主机地址
- `port`: 端口号（默认3306）
- `database`: 数据库名称
- `user`: 用户名
- `password`: 密码
- `ssl`: 是否使用SSL连接（可选）

### PostgreSQL

```sql
CREATE DATABASE postgres_connection
WITH ENGINE = 'postgres',
PARAMETERS = {
  'host': 'localhost',
  'port': 5432,
  'database': 'mydb',
  'user': 'postgres',
  'password': 'password',
  'schema': 'public'
}
```

**参数说明:**
- `host`: 数据库主机地址
- `port`: 端口号（默认5432）
- `database`: 数据库名称
- `user`: 用户名
- `password`: 密码
- `schema`: 模式名称（默认public）

### SQL Server

```sql
CREATE DATABASE sqlserver_connection
WITH ENGINE = 'mssql',
PARAMETERS = {
  'host': 'localhost',
  'port': 1433,
  'database': 'mydb',
  'user': 'sa',
  'password': 'password',
  'driver': 'ODBC Driver 17 for SQL Server'
}
```

### Oracle

```sql
CREATE DATABASE oracle_connection
WITH ENGINE = 'oracle',
PARAMETERS = {
  'host': 'localhost',
  'port': 1521,
  'database': 'ORCL',
  'user': 'system',
  'password': 'password'
}
```

### SQLite

```sql
CREATE DATABASE sqlite_connection
WITH ENGINE = 'sqlite',
PARAMETERS = {
  'file': '/path/to/database.db'
}
```

## 时序数据库

### TDengine

```sql
CREATE DATABASE industrial_connection
WITH ENGINE = 'tdengine',
PARAMETERS = {
  'host': 'localhost',
  'port': 6030,
  'database': 'industrial_plant',
  'user': 'root',
  'password': 'taosdata',
  'timezone': 'Asia/Shanghai'
}
```

**参数说明:**
- `host`: TDengine服务器地址
- `port`: 端口号（默认6030）
- `database`: 数据库名称
- `user`: 用户名（默认root）
- `password`: 密码（默认taosdata）
- `timezone`: 时区设置

**工业设备监控表示例:**

```sql
-- 查询工业设备实时数据
SELECT 
  ts,
  location_id,
  temperature,
  pressure,
  flow_rate,
  vibration,
  power_consumption,
  rpm,
  efficiency,
  status
FROM industrial_connection.sensor_data
WHERE ts > NOW() - INTERVAL 1 HOUR
ORDER BY ts DESC;

-- 查询设备运行状态
SELECT 
  ts,
  device_id,
  device_name,
  running_status,
  power_consumption,
  vibration_level,
  temperature,
  alarm_status
FROM industrial_connection.device_status
WHERE location_id = 'workshop_001'
  AND ts > NOW() - INTERVAL 24 HOUR;

-- 聚合统计日运行数据
SELECT 
  _wstart AS date,
  AVG(temperature) AS avg_temp,
  MAX(temperature) AS max_temp,
  MIN(temperature) AS min_temp,
  AVG(power_consumption) AS avg_power
FROM industrial_connection.sensor_data
WHERE ts > NOW() - INTERVAL 7 DAYS
INTERVAL(1d);
```

### InfluxDB

```sql
CREATE DATABASE influxdb_connection
WITH ENGINE = 'influxdb',
PARAMETERS = {
  'host': 'localhost',
  'port': 8086,
  'database': 'mydb',
  'user': 'admin',
  'password': 'password',
  'ssl': false
}
```

**参数说明:**
- `host`: InfluxDB服务器地址
- `port`: 端口号（默认8086）
- `database`: 数据库名称
- `user`: 用户名
- `password`: 密码
- `ssl`: 是否使用SSL

### TimescaleDB

```sql
CREATE DATABASE timescaledb_connection
WITH ENGINE = 'postgres',
PARAMETERS = {
  'host': 'localhost',
  'port': 5432,
  'database': 'mydb',
  'user': 'postgres',
  'password': 'password',
  'schema': 'public'
}
```

**说明:** TimescaleDB是PostgreSQL的扩展，使用postgres引擎连接

## NoSQL数据库

### MongoDB

```sql
CREATE DATABASE mongo_connection
WITH ENGINE = 'mongodb',
PARAMETERS = {
  'host': 'localhost',
  'port': 27017,
  'database': 'mydb',
  'user': 'admin',
  'password': 'password',
  'authSource': 'admin'
}
```

**参数说明:**
- `host`: MongoDB主机地址
- `port`: 端口号（默认27017）
- `database`: 数据库名称
- `user`: 用户名
- `password`: 密码
- `authSource`: 认证数据库

### Redis

```sql
CREATE DATABASE redis_connection
WITH ENGINE = 'redis',
PARAMETERS = {
  'host': 'localhost',
  'port': 6379,
  'password': 'password',
  'db': 0
}
```

### Elasticsearch

```sql
CREATE DATABASE es_connection
WITH ENGINE = 'elasticsearch',
PARAMETERS = {
  'host': 'localhost',
  'port': 9200,
  'index': 'myindex',
  'user': 'elastic',
  'password': 'password'
}
```

## 云数据库

### AWS RDS (MySQL)

```sql
CREATE DATABASE aws_mysql
WITH ENGINE = 'mysql',
PARAMETERS = {
  'host': 'mydb.xxxx.us-east-1.rds.amazonaws.com',
  'port': 3306,
  'database': 'mydb',
  'user': 'admin',
  'password': 'password',
  'ssl': true
}
```

### Google Cloud SQL

```sql
CREATE DATABASE gcloud_sql
WITH ENGINE = 'postgres',
PARAMETERS = {
  'host': 'mydb:us-central1:myinstance',
  'port': 5432,
  'database': 'mydb',
  'user': 'postgres',
  'password': 'password',
  'ssl': true
}
```

### Azure Database

```sql
CREATE DATABASE azure_sql
WITH ENGINE = 'mysql',
PARAMETERS = {
  'host': 'myserver.mysql.database.azure.com',
  'port': 3306,
  'database': 'mydb',
  'user': 'myadmin@myserver',
  'password': 'password',
  'ssl': true
}
```

### Snowflake

```sql
CREATE DATABASE snowflake_connection
WITH ENGINE = 'snowflake',
PARAMETERS = {
  'account': 'xy12345.us-east-1',
  'user': 'myuser',
  'password': 'password',
  'warehouse': 'mywh',
  'database': 'mydb',
  'schema': 'public'
}
```

### BigQuery

```sql
CREATE DATABASE bigquery_connection
WITH ENGINE = 'bigquery',
PARAMETERS = {
  'project': 'my-project',
  'dataset': 'mydataset',
  'credentials': '/path/to/credentials.json'
}
```

## 文件格式

### CSV文件

```sql
IMPORT FROM 'data.csv'
INTO my_database.imported_data
WITH FORMAT = 'csv',
     DELIMITER = ',',
     HEADER = true,
     EN温度ING = 'UTF-8'
```

**参数说明:**
- `FORMAT`: 文件格式
- `DELIMITER`: 分隔符（默认逗号）
- `HEADER`: 是否有标题行
- `EN温度ING`: 文件编码

### Excel文件

```sql
IMPORT FROM 'data.xlsx'
INTO my_database.imported_data
WITH FORMAT = 'excel',
     SHEET = 'Sheet1'
```

### JSON文件

```sql
IMPORT FROM 'data.json'
INTO my_database.imported_data
WITH FORMAT = 'json',
     JSON_TYPE = 'array'
```

### Parquet文件

```sql
IMPORT FROM 'data.parquet'
INTO my_database.imported_data
WITH FORMAT = 'parquet'
```

## SaaS应用

### Gmail

```sql
CREATE DATABASE gmail_connection
WITH ENGINE = 'gmail',
PARAMETERS = {
  'credentials': '/path/to/credentials.json',
  'email': 'myemail@gmail.com'
}
```

**获取Gmail凭证:**
1. 访问 Google Cloud Console
2. 创建项目并启用Gmail API
3. 创建OAuth 2.0客户端ID
4. 下载凭证JSON文件

### Slack

```sql
CREATE DATABASE slack_connection
WITH ENGINE = 'slack',
PARAMETERS = {
  'token': 'xoxb-your-token-here'
}
```

**获取Slack Token:**
1. 访问 Slack API
2. 创建应用
3. 安装到工作区
4. 获取Bot Token

### Salesforce

```sql
CREATE DATABASE salesforce_connection
WITH ENGINE = 'salesforce',
PARAMETERS = {
  'username': 'myuser@salesforce.com',
  'password': 'password',
  'security_token': 'token',
  'sandbox': false
}
```

### Shopify

```sql
CREATE DATABASE shopify_connection
WITH ENGINE = 'shopify',
PARAMETERS = {
  'api_key': 'your-api-key',
  'password': 'your-password',
  'shop_name': 'myshop.myshopify.com'
}
```

## 其他数据源

### ClickHouse

```sql
CREATE DATABASE clickhouse_connection
WITH ENGINE = 'clickhouse',
PARAMETERS = {
  'host': 'localhost',
  'port': 8123,
  'database': 'mydb',
  'user': 'default',
  'password': ''
}
```

### Apache Hive

```sql
CREATE DATABASE hive_connection
WITH ENGINE = 'hive',
PARAMETERS = {
  'host': 'localhost',
  'port': 10000,
  'database': 'mydb',
  'user': 'hive',
  'auth': 'NOSASL'
}
```

### Presto/Trino

```sql
CREATE DATABASE presto_connection
WITH ENGINE = 'presto',
PARAMETERS = {
  'host': 'localhost',
  'port': 8080,
  'catalog': 'hive',
  'schema': 'mydb',
  'user': 'myuser'
}
```

## 连接池配置

```sql
CREATE DATABASE pooled_connection
WITH ENGINE = 'mysql',
PARAMETERS = {
  'host': 'localhost',
  'port': 3306,
  'database': 'mydb',
  'user': 'root',
  'password': 'password',
  'pool_size': 10,
  'max_overflow': 5,
  'pool_timeout': 30
}
```

**参数说明:**
- `pool_size`: 连接池大小
- `max_overflow`: 最大溢出连接数
- `pool_timeout`: 连接超时时间（秒）

## SSL/TLS配置

```sql
CREATE DATABASE ssl_connection
WITH ENGINE = 'mysql',
PARAMETERS = {
  'host': 'localhost',
  'port': 3306,
  'database': 'mydb',
  'user': 'root',
  'password': 'password',
  'ssl': true,
  'ssl_ca': '/path/to/ca-cert.pem',
  'ssl_cert': '/path/to/client-cert.pem',
  'ssl_key': '/path/to/client-key.pem'
}
```

## 代理配置

```sql
CREATE DATABASE proxy_connection
WITH ENGINE = 'mysql',
PARAMETERS = {
  'host': 'database.example.com',
  'port': 3306,
  'database': 'mydb',
  'user': 'root',
  'password': 'password',
  'proxy_host': 'proxy.example.com',
  'proxy_port': 8080,
  'proxy_user': 'proxyuser',
  'proxy_password': 'proxypassword'
}
```

## 最佳实践

1. **安全性**
   - 使用环境变量存储密码
   - 启用SSL/TLS加密
   - 使用最小权限原则

2. **性能**
   - 使用连接池
   - 合理设置超时时间
   - 监控连接使用情况

3. **可靠性**
   - 配置重连机制
   - 设置心跳检测
   - 实现故障转移

4. **可维护性**
   - 使用有意义的连接名称
   - 记录连接配置
   - 定期更新凭证
