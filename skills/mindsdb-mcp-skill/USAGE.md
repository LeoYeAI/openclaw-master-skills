# MindsDB MCP 使用指南

## 快速开始

### 基础查询

```
查询employees表中的所有数据
```

**转换为SQL:**
```sql
SELECT * FROM employees
```

### 条件查询

```
查询工资大于50000的员工
```

**转换为SQL:**
```sql
SELECT * FROM employees WHERE salary > 50000
```

### 排序查询

```
查询员工按工资降序排列
```

**转换为SQL:**
```sql
SELECT * FROM employees ORDER BY salary DESC
```

## 数据分析场景

### 销售分析

```
分析2024年各地区的月度销售额
```

**执行步骤:**
1. 查询2024年销售数据
2. 按地区和月份分组
3. 计算销售总额
4. 生成趋势报告

**SQL示例:**
```sql
SELECT 
  region,
  DATE_TRUNC('month', order_date) as month,
  SUM(amount) as total_sales
FROM orders
WHERE order_date >= '2024-01-01'
GROUP BY region, DATE_TRUNC('month', order_date)
ORDER BY region, month
```

### 客户分析

```
找出最活跃的10个客户
```

**SQL示例:**
```sql
SELECT 
  customer_id,
  customer_name,
  COUNT(*) as order_count,
  SUM(amount) as total_spent
FROM orders
GROUP BY customer_id, customer_name
ORDER BY order_count DESC
LIMIT 10
```

### 产品分析

```
分析产品类别的销售占比
```

**SQL示例:**
```sql
SELECT 
  category,
  COUNT(*) as product_count,
  SUM(quantity) as total_quantity,
  SUM(price * quantity) as total_revenue,
  ROUND(SUM(price * quantity) * 100.0 / 
    (SELECT SUM(price * quantity) FROM orders), 2) as percentage
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY category
ORDER BY total_revenue DESC
```

## AI模型创建

### 销售预测模型

```
创建一个模型来预测下个月的销售额
```

**SQL示例:**
```sql
CREATE MODEL mindsdb.sales_forecast
PREDICT sales_amount
FROM my_database.daily_sales
USING
  engine = 'prophet',
  problem_type = 'time_series',
  target = 'sales_amount',
  time_column = 'date',
  horizon = 30
```

### 客户流失预测

```
预测哪些客户可能会流失
```

**SQL示例:**
```sql
CREATE MODEL mindsdb.churn_predictor
PREDICT churn
FROM my_database.customers
USING
  engine = 'xgboost',
  problem_type = 'classification',
  target = 'churn',
  input_features = [
    'age', 'tenure', 'monthly_charges', 
    'total_charges', 'contract_type', 
    'payment_method', 'support_calls'
  ]
```

### 价格预测模型

```
预测房价
```

**SQL示例:**
```sql
CREATE MODEL mindsdb.house_price_predictor
PREDICT price
FROM my_database.houses
USING
  engine = 'lightwood',
  problem_type = 'regression',
  target = 'price',
  input_features = [
    'area', 'bedrooms', 'bathrooms', 
    'location', 'age', 'condition'
  ]
```

## 数据源连接

### 连接MySQL数据库

```
连接到MySQL数据库，主机是192.168.1.100，端口3306，数据库名是mydb
```

**SQL示例:**
```sql
CREATE DATABASE my_mysql
WITH ENGINE = 'mysql',
PARAMETERS = {
  'host': '192.168.1.100',
  'port': 3306,
  'database': 'mydb',
  'user': 'root',
  'password': 'password'
}
```

### 连接PostgreSQL数据库

```
连接到PostgreSQL数据库
```

**SQL示例:**
```sql
CREATE DATABASE my_postgres
WITH ENGINE = 'postgres',
PARAMETERS = {
  'host': 'localhost',
  'port': 5432,
  'database': 'mydb',
  'user': 'postgres',
  'password': 'password'
}
```

### 连接MongoDB

```
连接到MongoDB数据库
```

**SQL示例:**
```sql
CREATE DATABASE my_mongo
WITH ENGINE = 'mongodb',
PARAMETERS = {
  'host': 'localhost',
  'port': 27017,
  'database': 'mydb',
  'user': 'admin',
  'password': 'password'
}
```

### 导入CSV文件

```
导入CSV文件data.csv到数据库
```

**SQL示例:**
```sql
IMPORT FROM 'data.csv'
INTO my_database.imported_data
WITH FORMAT = 'csv'
```

### 导入Excel文件

```
导入Excel文件sales.xlsx
```

**SQL示例:**
```sql
IMPORT FROM 'sales.xlsx'
INTO my_database.sales_data
WITH FORMAT = 'excel'
```

## 复杂查询示例

### 多表连接

```
查询订单及其对应的客户和产品信息
```

**SQL示例:**
```sql
SELECT 
  o.order_id,
  o.order_date,
  c.customer_name,
  p.product_name,
  oi.quantity,
  oi.price
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
```

### 子查询

```
查询销售额高于平均销售额的产品
```

**SQL示例:**
```sql
SELECT 
  product_name,
  SUM(quantity * price) as total_sales
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY product_name
HAVING SUM(quantity * price) > (
  SELECT AVG(total_sales)
  FROM (
    SELECT SUM(quantity * price) as total_sales
    FROM order_items
    GROUP BY product_id
  ) as avg_sales
)
```

### 窗口函数

```
查询每个客户的订单排名
```

**SQL示例:**
```sql
SELECT 
  customer_id,
  order_id,
  order_date,
  amount,
  RANK() OVER (PARTITION BY customer_id ORDER BY order_date) as order_rank
FROM orders
```

### 递归查询

```
查询组织结构树
```

**SQL示例:**
```sql
WITH RECURSIVE org_tree AS (
  SELECT employee_id, name, manager_id, 1 as level
  FROM employees
  WHERE manager_id IS NULL
  
  UNION ALL
  
  SELECT e.employee_id, e.name, e.manager_id, ot.level + 1
  FROM employees e
  JOIN org_tree ot ON e.manager_id = ot.employee_id
)
SELECT * FROM org_tree ORDER BY level, employee_id
```

## 数据导出

### 导出为CSV

```
将查询结果导出为CSV文件
```

**SQL示例:**
```sql
EXPORT (SELECT * FROM sales WHERE date > '2024-01-01')
TO 'sales_export.csv'
FORMAT 'csv'
```

### 导出为JSON

```
导出为JSON格式
```

**SQL示例:**
```sql
EXPORT (SELECT * FROM customers LIMIT 100)
TO 'customers.json'
FORMAT 'json'
```

## 实用技巧

### 1. 使用LIMIT限制结果

```
查询前10个订单
```

**SQL示例:**
```sql
SELECT * FROM orders ORDER BY order_date DESC LIMIT 10
```

### 2. 使用DISTINCT去重

```
查询所有不同的产品类别
```

**SQL示例:**
```sql
SELECT DISTINCT category FROM products
```

### 3. 使用CASE条件

```
根据销售额给客户分级
```

**SQL示例:**
```sql
SELECT 
  customer_name,
  total_spent,
  CASE 
    WHEN total_spent > 10000 THEN 'VIP'
    WHEN total_spent > 5000 THEN 'Gold'
    WHEN total_spent > 1000 THEN 'Silver'
    ELSE 'Regular'
  END as customer_level
FROM (
  SELECT 
    c.customer_name,
    SUM(o.amount) as total_spent
  FROM customers c
  JOIN orders o ON c.customer_id = o.customer_id
  GROUP BY c.customer_name
) as customer_spending
```

### 4. 使用COALESCE处理NULL

```
查询订单，如果折扣为NULL则显示0
```

**SQL示例:**
```sql
SELECT 
  order_id,
  amount,
  COALESCE(discount, 0) as discount,
  amount - COALESCE(discount, 0) as final_amount
FROM orders
```

## 性能优化建议

1. **使用索引**: 在WHERE和JOIN条件中使用的列上创建索引
2. **限制结果**: 使用LIMIT减少返回的数据量
3. **避免SELECT ***: 只查询需要的列
4. **使用EXISTS代替IN**: 对于子查询，EXISTS通常更高效
5. **批量操作**: 使用批量插入代替单条插入

## 常见错误及解决

### 错误1: 表不存在

**原因**: 表名拼写错误或数据库选择错误

**解决**: 检查表名和数据库连接

### 错误2: 列不存在

**原因**: 列名拼写错误

**解决**: 使用DESCRIBE TABLE查看表结构

### 错误3: 权限不足

**原因**: 用户没有足够的权限

**解决**: 联系管理员授予相应权限

### 错误4: 查询超时

**原因**: 查询过于复杂或数据量过大

**解决**: 优化查询，添加索引，或增加超时时间

## 时序数据库应用

### 重要说明

**本文档中的表名和字段名仅为示例！**

Agent会自动适配你的实际数据库结构：
- 表名可以是任意的（如：`sensor_data`, `monitor_table`, `iot_metrics`等）
- 字段名可以是任意的（如：`temperature`, `pressure`, `flow_rate`等）
- Agent会自动查询数据库元数据，发现你的表结构
- Agent会根据你的实际表名和字段名生成SQL

**使用方式:**
```
用户: "连接到我的TDengine数据库，查询工业设备数据"
Agent会:
1. 连接数据库
2. 查询表结构（SHOW TABLES, DESCRIBE TABLE）
3. 根据你的实际表名和字段名生成SQL
4. 执行查询并返回结果
```

### 工业设备监控

#### 连接TDengine数据库

```
连接到TDengine数据库，监控工业设备数据
```

**SQL示例:**
```sql
CREATE DATABASE industrial_tdengine
WITH ENGINE = 'tdengine',
PARAMETERS = {
  'host': '192.168.1.100',
  'port': 6030,
  'database': 'industrial_plant',
  'user': 'root',
  'password': 'taosdata',
  'timezone': 'Asia/Shanghai'
}
```

#### 查询实时设备数据

```
查询1号车间过去24小时的设备数据
```

**SQL示例:**
```sql
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
FROM industrial_tdengine.sensor_data
WHERE location_id = 'workshop_001'
  AND ts > NOW() - INTERVAL 24 HOUR
ORDER BY ts DESC
```

#### 查询设备运行状态

```
检查所有设备的运行状态，找出异常设备
```

**SQL示例:**
```sql
SELECT 
  ts,
  device_id,
  device_name,
  running_status,
  power_consumption,
  vibration_level,
  temperature,
  alarm_status,
  CASE 
    WHEN alarm_status = 'normal' THEN '正常运行'
    WHEN alarm_status = 'warning' THEN '警告'
    WHEN alarm_status = 'critical' THEN '严重告警'
    ELSE '未知状态'
  END as status_description
FROM industrial_tdengine.device_status
WHERE location_id = 'workshop_001'
  AND ts > NOW() - INTERVAL 1 HOUR
  AND alarm_status != 'normal'
ORDER BY ts DESC
```

#### 统计日运行数据

```
统计过去7天的日运行数据
```

**SQL示例:**
```sql
SELECT 
  _wstart AS date,
  AVG(temperature) AS avg_temp,
  MAX(temperature) AS max_temp,
  MIN(temperature) AS min_temp,
  AVG(power_consumption) AS avg_power,
  AVG(efficiency) AS avg_efficiency
FROM industrial_tdengine.sensor_data
WHERE location_id = 'workshop_001'
  AND ts > NOW() - INTERVAL 7 DAYS
INTERVAL(1d)
```

#### 异常检测查询

```
检测设备参数异常（温度超过80度或压力超过10MPa）
```

**SQL示例:**
```sql
SELECT 
  ts,
  location_id,
  temperature,
  pressure,
  CASE 
    WHEN temperature > 80 THEN '温度过高'
    WHEN pressure > 10 THEN '压力过高'
    ELSE '正常'
  END as abnormal_type,
  CASE 
    WHEN temperature > 80 THEN '温度超过80°C，需要检查冷却系统'
    WHEN pressure > 10 THEN '压力超过10MPa，需要检查压力控制阀'
    ELSE '设备参数正常'
  END as suggestion
FROM industrial_tdengine.sensor_data
WHERE location_id = 'workshop_001'
  AND ts > NOW() - INTERVAL 24 HOUR
  AND (temperature > 80 OR pressure > 10)
ORDER BY ts DESC
```

#### 创建设备故障预测模型

```
创建设备故障预测模型，提前预警设备故障
```

**SQL示例:**
```sql
CREATE MODEL mindsdb.device_failure_predictor
PREDICT will_fail
FROM industrial_tdengine.device_status
USING
  engine = 'xgboost',
  problem_type = 'classification',
  target = 'will_fail',
  input_features = [
    'vibration_level',
    'temperature',
    'power_consumption',
    'running_hours',
    'maintenance_count'
  ],
  training_data = (
    SELECT 
      vibration_level,
      temperature,
      power_consumption,
      running_hours,
      maintenance_count,
      CASE WHEN alarm_status = 'critical' THEN 1 ELSE 0 END as will_fail
    FROM industrial_tdengine.device_status
    WHERE ts > NOW() - INTERVAL 90 DAYS
  )
```

#### 预测性维护查询

```
预测哪些设备可能会在未来7天内发生故障
```

**SQL示例:**
```sql
SELECT 
  device_id,
  device_name,
  will_fail,
  failure_probability,
  CASE 
    WHEN failure_probability > 0.8 THEN '立即维护'
    WHEN failure_probability > 0.5 THEN '计划维护'
    ELSE '正常运行'
  END as maintenance_priority,
  '建议检查设备振动、温度和功耗' as maintenance_suggestion
FROM mindsdb.device_failure_predictor
WHERE will_fail = 1
  AND failure_probability > 0.5
ORDER BY failure_probability DESC
```

### 工业物联网监控

#### 连接InfluxDB

```
连接到InfluxDB，监控工厂生产线
```

**SQL示例:**
```sql
CREATE DATABASE factory_influxdb
WITH ENGINE = 'influxdb',
PARAMETERS = {
  'host': '192.168.1.101',
  'port': 8086,
  'database': 'factory_metrics',
  'user': 'admin',
  'password': 'password'
}
```

#### 查询能耗数据

```
分析生产线的能耗情况
```

**SQL示例:**
```sql
SELECT 
  time,
  production_line,
  machine_id,
  power_consumption,
  energy_cost,
  efficiency_rate
FROM factory_influxdb.energy_metrics
WHERE time > NOW() - INTERVAL 24 HOUR
ORDER BY time DESC
```
