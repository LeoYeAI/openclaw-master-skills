# MindsDB SDK 和 API 参考

## 概述

MindsDB提供了多种访问方式：
- **Python SDK**: 原生Python库
- **JavaScript SDK**: Node.js和浏览器支持
- **REST API**: HTTP接口
- **MySQL协议**: 兼容MySQL客户端
- **MongoDB协议**: 兼容MongoDB客户端

## Python SDK

### 安装

```bash
pip install mindsdb
```

### 基础连接

```python
import mindsdb

# 连接到本地MindsDB
mdb = mindsdb.connect()

# 连接到远程MindsDB
mdb = mindsdb.connect(
    host='cloud.mindsdb.com',
    port=47334,
    user='your-email@example.com',
    password='your-password'
)
```

### 创建模型

```python
# 创建预测模型
mdb.create_model(
    name='sales_predictor',
    predict='price',
    select_data='SELECT * FROM houses',
    integration='mysql',
    options={
        'engine': 'lightwood',
        'problem_type': 'regression'
    }
)

# 创建分类模型
mdb.create_model(
    name='churn_predictor',
    predict='churn',
    select_data='SELECT * FROM customers',
    integration='postgres',
    options={
        'engine': 'xgboost',
        'problem_type': 'classification'
    }
)
```

### 查询模型

```python
# 使用模型进行预测
result = mdb.predict(
    model_name='sales_predictor',
    data={
        'area': 1500,
        'bedrooms': 3,
        'bathrooms': 2,
        'location': 'downtown'
    }
)

print(result)
```

### 执行SQL查询

```python
# 执行查询
result = mdb.query('SELECT * FROM houses LIMIT 10')

# 获取结果
for row in result:
    print(row)
```

### 异步操作

```python
import asyncio
from mindsdb import AsyncMindsDB

async def main():
    mdb = AsyncMindsDB()
    await mdb.connect()
    
    # 异步创建模型
    await mdb.create_model(
        name='async_model',
        predict='target',
        select_data='SELECT * FROM data'
    )
    
    await mdb.close()

asyncio.run(main())
```

## JavaScript SDK

### 安装

```bash
npm install mindsdb-js
```

### 基础连接

```javascript
const MindsDB = require('mindsdb-js');

// 连接到本地MindsDB
const mdb = new MindsDB({
  host: 'localhost',
  port: 47334,
  user: 'mindsdb',
  password: ''
});

// 连接到远程MindsDB
const mdb = new MindsDB({
  host: 'cloud.mindsdb.com',
  port: 47334,
  user: 'your-email@example.com',
  password: 'your-password'
});

await mdb.connect();
```

### 创建模型

```javascript
// 创建预测模型
await mdb.createModel({
  name: 'sales_predictor',
  predict: 'price',
  selectData: 'SELECT * FROM houses',
  integration: 'mysql',
  options: {
    engine: 'lightwood',
    problemType: 'regression'
  }
});
```

### 查询模型

```javascript
// 使用模型进行预测
const result = await mdb.predict({
  modelName: 'sales_predictor',
  data: {
    area: 1500,
    bedrooms: 3,
    bathrooms: 2,
    location: 'downtown'
  }
});

console.log(result);
```

### 执行SQL查询

```javascript
// 执行查询
const result = await mdb.query('SELECT * FROM houses LIMIT 10');

// 获取结果
for (const row of result) {
  console.log(row);
}
```

## REST API

### 基础URL

```
本地: http://localhost:47334/api
云端: https://cloud.mindsdb.com/api
```

### 认证

```bash
# 使用API密钥
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:47334/api/models
```

### 创建模型

```bash
curl -X POST http://localhost:47334/api/models \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "name": "sales_predictor",
    "predict": "price",
    "select_data": "SELECT * FROM houses",
    "integration": "mysql",
    "options": {
      "engine": "lightwood",
      "problem_type": "regression"
    }
  }'
```

### 查询模型

```bash
# 列出所有模型
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:47334/api/models

# 获取特定模型
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:47334/api/models/sales_predictor
```

### 预测

```bash
curl -X POST http://localhost:47334/api/models/sales_predictor/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "data": {
      "area": 1500,
      "bedrooms": 3,
      "bathrooms": 2,
      "location": "downtown"
    }
  }'
```

### 执行SQL查询

```bash
curl -X POST http://localhost:47334/api/sql/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "query": "SELECT * FROM houses LIMIT 10"
  }'
```

## MySQL协议

### 连接

```python
import mysql.connector

# 使用MySQL协议连接MindsDB
conn = mysql.connector.connect(
    host='localhost',
    port=47334,
    user='mindsdb',
    password='',
    database='mindsdb'
)

cursor = conn.cursor()
```

### 创建模型

```python
# 通过MySQL协议创建模型
cursor.execute("""
    CREATE MODEL mindsdb.sales_predictor
    PREDICT price
    FROM mysql.houses
    USING engine='lightwood'
""")
```

### 查询

```python
# 执行查询
cursor.execute("SELECT * FROM mindsdb.sales_predictor LIMIT 10")

# 获取结果
results = cursor.fetchall()
for row in results:
    print(row)
```

## MongoDB协议

### 连接

```python
from pymongo import MongoClient

# 使用MongoDB协议连接MindsDB
client = MongoClient('mongodb://localhost:47335/')
db = client['mindsdb']
```

### 创建模型

```python
# 通过MongoDB协议创建模型
db.models.insert_one({
    'name': 'sales_predictor',
    'predict': 'price',
    'select_data': 'SELECT * FROM houses',
    'integration': 'mysql',
    'options': {
        'engine': 'lightwood'
    }
})
```

### 查询

```python
# 执行查询
results = db.models.find({'name': 'sales_predictor'})
for doc in results:
    print(doc)
```

## 高级功能

### 模型版本管理

```python
# 创建模型版本
mdb.create_model(
    name='sales_predictor',
    version='v2',
    predict='price',
    select_data='SELECT * FROM houses'
)

# 列出模型版本
versions = mdb.list_model_versions('sales_predictor')

# 回滚到特定版本
mdb.rollback_model('sales_predictor', 'v1')
```

### 模型监控

```python
# 获取模型状态
status = mdb.get_model_status('sales_predictor')
print(status)

# 获取模型指标
metrics = mdb.get_model_metrics('sales_predictor')
print(metrics)
```

### 批量预测

```python
# 批量预测
data = [
    {'area': 1500, 'bedrooms': 3, 'bathrooms': 2},
    {'area': 2000, 'bedrooms': 4, 'bathrooms': 3},
    {'area': 1200, 'bedrooms': 2, 'bathrooms': 1}
]

results = mdb.batch_predict('sales_predictor', data)
for result in results:
    print(result)
```

### 模型导出和导入

```python
# 导出模型
mdb.export_model('sales_predictor', 'sales_predictor.zip')

# 导入模型
mdb.import_model('sales_predictor.zip')
```

## 错误处理

### Python SDK

```python
import mindsdb
from mindsdb.exceptions import MindsDBError

try:
    mdb = mindsdb.connect()
    result = mdb.query('SELECT * FROM invalid_table')
except MindsDBError as e:
    print(f"MindsDB错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
```

### JavaScript SDK

```javascript
try {
  const result = await mdb.query('SELECT * FROM invalid_table');
} catch (error) {
  if (error instanceof MindsDBError) {
    console.error('MindsDB错误:', error.message);
  } else {
    console.error('其他错误:', error);
  }
}
```

### REST API

```bash
# 错误响应示例
{
  "error": {
    "code": "MODEL_NOT_FOUND",
    "message": "Model 'sales_predictor' not found",
    "details": {}
  }
}
```

## 最佳实践

### 1. 连接池

```python
# 使用连接池
from mindsdb import MindsDBPool

pool = MindsDBPool(
    host='localhost',
    port=47334,
    max_connections=10
)

# 获取连接
with pool.get_connection() as mdb:
    result = mdb.query('SELECT * FROM houses')
```

### 2. 重试机制

```python
import time
from mindsdb.exceptions import ConnectionError

def execute_with_retry(mdb, query, max_retries=3):
    for attempt in range(max_retries):
        try:
            return mdb.query(query)
        except ConnectionError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise
```

### 3. 日志记录

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mindsdb')

mdb = mindsdb.connect()
logger.info('连接到MindsDB成功')
```

### 4. 性能优化

```python
# 使用批量操作
data = [{'feature1': x, 'feature2': y} for x, y in zip(range(100), range(100))]
results = mdb.batch_predict('model_name', data)

# 使用缓存
mdb.enable_cache()
result = mdb.query('SELECT * FROM large_table')
```

## 安全考虑

### 1. API密钥管理

```python
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('MINDSDB_API_KEY')
mdb = mindsdb.connect(api_key=API_KEY)
```

### 2. SSL/TLS

```python
mdb = mindsdb.connect(
    host='cloud.mindsdb.com',
    port=47334,
    ssl=True,
    ssl_ca_cert='/path/to/ca-cert.pem'
)
```

### 3. 权限控制

```python
# 使用最小权限原则
mdb = mindsdb.connect(
    user='readonly_user',
    password='readonly_password',
    database='readonly_db'
)
```

## 参考资源

- **官方文档**: https://docs.mindsdb.com
- **Python SDK**: https://github.com/mindsdb/mindsdb-python
- **JavaScript SDK**: https://github.com/mindsdb/mindsdb-js
- **REST API**: https://docs.mindsdb.com/api
- **GitHub**: https://github.com/mindsdb/mindsdb
