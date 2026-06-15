# MindsDB MCP 故障排除指南

## 常见问题

### 连接问题

#### 问题1: 无法连接到MindsDB服务器

**症状:**
- Claude Desktop显示"无法连接到MCP服务器"
- 查询时出现连接错误

**可能原因:**
1. MindsDB服务器未启动
2. 配置参数错误
3. 网络连接问题
4. 防火墙阻止连接

**解决方案:**

1. **检查MindsDB服务器状态**
   ```bash
   # 检查MindsDB是否运行
   netstat -an | findstr 47334
   
   # 或使用curl测试
   curl http://localhost:47334/api/health
   ```

2. **验证配置参数**
   - 检查 `claude_desktop_config.json` 中的配置
   - 确认主机地址和端口正确
   - 验证API密钥是否有效

3. **测试网络连接**
   ```bash
   ping localhost
   telnet localhost 47334
   ```

4. **检查防火墙设置**
   - Windows: 允许Node.js通过防火墙
   - macOS/Linux: 检查iptables规则

#### 问题2: API密钥无效

**症状:**
- 认证失败错误
- 401 Unauthorized错误

**解决方案:**

1. **重新生成API密钥**
   - 访问 https://cloud.mindsdb.com
   - 登录并生成新的API密钥

2. **更新配置文件**
   ```json
   {
     "env": {
       "MINDSDB_API_KEY": "new-api-key-here"
     }
   }
   ```

3. **重启Claude Desktop**

### 查询问题

#### 问题3: 查询超时

**症状:**
- 查询执行时间过长
- 出现超时错误

**解决方案:**

1. **优化查询**
   - 添加WHERE条件减少数据量
   - 使用索引
   - 避免SELECT *

2. **增加超时时间**
   ```json
   {
     "env": {
       "QUERY_TIMEOUT": "300"
     }
   }
   ```

3. **分批处理大数据量**
   ```sql
   SELECT * FROM large_table LIMIT 1000 OFFSET 0
   SELECT * FROM large_table LIMIT 1000 OFFSET 1000
   ```

#### 问题4: SQL语法错误

**症状:**
- 语法错误提示
- 查询无法执行

**解决方案:**

1. **检查SQL语法**
   - 使用SQL验证工具
   - 参考SQL文档

2. **使用EXPLAIN分析查询**
   ```sql
   EXPLAIN SELECT * FROM table_name WHERE condition
   ```

3. **逐步构建复杂查询**
   - 先测试子查询
   - 再组合完整查询

#### 问题5: 表或列不存在

**症状:**
- "table does not exist" 错误
- "column does not exist" 错误

**解决方案:**

1. **列出所有表**
   ```sql
   SHOW TABLES
   ```

2. **查看表结构**
   ```sql
   DESCRIBE table_name
   ```

3. **检查数据库名称**
   ```sql
   SHOW DATABASES
   ```

### 数据源问题

#### 问题6: 无法连接到外部数据库

**症状:**
- 连接外部数据库失败
- 认证错误

**解决方案:**

1. **验证连接参数**
   ```sql
   CREATE DATABASE test_connection
   WITH ENGINE = 'mysql',
   PARAMETERS = {
     'host': 'correct-host',
     'port': 3306,
     'database': 'correct-db',
     'user': 'correct-user',
     'password': 'correct-password'
   }
   ```

2. **测试网络连接**
   ```bash
   ping database-host
   telnet database-host 3306
   ```

3. **检查数据库权限**
   - 确保用户有足够的权限
   - 检查数据库用户设置

#### 问题7: 数据导入失败

**症状:**
- CSV/Excel导入错误
- 格式不匹配

**解决方案:**

1. **检查文件格式**
   - 确认文件编码（UTF-8）
   - 验证分隔符
   - 检查列名

2. **使用正确的导入语法**
   ```sql
   IMPORT FROM 'data.csv'
   INTO my_database.table_name
   WITH FORMAT = 'csv',
        DELIMITER = ',',
        HEADER = true
   ```

3. **处理特殊字符**
   - 转义引号
   - 处理换行符
   - 清理数据

### 模型问题

#### 问题8: 模型创建失败

**症状:**
- 模型训练错误
- 内存不足

**解决方案:**

1. **检查数据质量**
   - 处理缺失值
   - 移除异常值
   - 标准化数据

2. **调整模型参数**
   ```sql
   CREATE MODEL model_name
   PREDICT target
   FROM data_source
   USING
     engine = 'lightwood',
     max_epochs = 100,
     batch_size = 32
   ```

3. **使用更简单的模型**
   - 减少特征数量
   - 选择更简单的引擎
   - 减少训练数据量

#### 问题9: 模型预测不准确

**症状:**
- 预测结果偏差大
- 模型性能差

**解决方案:**

1. **增加训练数据**
   - 收集更多数据
   - 使用数据增强

2. **特征工程**
   - 添加相关特征
   - 移除无关特征
   - 特征转换

3. **调整超参数**
   - 尝试不同的引擎
   - 调整学习率
   - 修改模型架构

### 性能问题

#### 问题10: 查询性能慢

**症状:**
- 简单查询也很慢
- 响应时间长

**解决方案:**

1. **添加索引**
   ```sql
   CREATE INDEX idx_column ON table_name(column_name)
   ```

2. **优化查询**
   - 避免全表扫描
   - 使用合适的JOIN类型
   - 减少子查询

3. **增加缓存**
   ```json
   {
     "env": {
       "CACHE_SIZE": "1024"
     }
   }
   ```

4. **升级硬件**
   - 增加内存
   - 使用SSD
   - 升级CPU

## 调试技巧

### 1. 启用调试日志

```json
{
  "env": {
    "DEBUG": "mindsdb:*",
    "LOG_LEVEL": "debug"
  }
}
```

### 2. 查看查询计划

```sql
EXPLAIN SELECT * FROM table_name WHERE condition
```

### 3. 使用测试查询

```sql
-- 测试简单查询
SELECT 1

-- 测试连接
SELECT NOW()

-- 测试表访问
SELECT COUNT(*) FROM table_name
```

### 4. 分步调试

```sql
-- 步骤1: 测试子查询
SELECT * FROM sub_table WHERE condition

-- 步骤2: 测试JOIN
SELECT * FROM table1 JOIN table2 ON table1.id = table2.id

-- 步骤3: 完整查询
SELECT * FROM table1 JOIN table2 ON table1.id = table2.id WHERE condition
```

## 日志分析

### 查看MCP服务器日志

**Windows:**
```powershell
Get-Content "$env:APPDATA\Claude\logs\mcp.log" -Tail 50
```

**macOS/Linux:**
```bash
tail -50 ~/.config/Claude/logs/mcp.log
```

### 常见日志信息

- `INFO`: 正常操作信息
- `WARN`: 警告信息
- `ERROR`: 错误信息
- `DEBUG`: 调试信息

## 获取帮助

### 官方资源

- **MindsDB文档**: https://docs.mindsdb.com
- **MCP协议**: https://modelcontextprotocol.io
- **GitHub Issues**: https://github.com/mindsdb/mcp-server/issues

### 社区支持

- **Discord**: https://discord.gg/mindsdb
- **Stack Overflow**: 使用 `mindsdb` 标签
- **Reddit**: r/mindsdb

### 联系支持

- **Email**: support@mindsdb.com
- **Twitter**: @mindsdb

## 预防措施

1. **定期备份数据**
   - 导出重要数据
   - 备份配置文件

2. **监控性能**
   - 跟踪查询时间
   - 监控资源使用

3. **保持更新**
   - 更新MindsDB版本
   - 更新MCP服务器

4. **安全最佳实践**
   - 使用强密码
   - 限制API访问
   - 定期审计日志
