# 工业设备监控实际案例

## 案例概述

这是一个使用MindsDB AI Agent分析TDengine时序数据库中工业设备数据的真实案例。

## 数据源配置

### TDengine连接

```sql
-- 数据源名称: demo_datasource
-- 数据库类型: tdengine
-- 表名: sensor_data_table
```

## 数据结构

### 表结构分析

**表名**: `sensor_data_table`  
**数据格式**: TDEngine超级表  
**总记录数**: 约10,000条  
**时间跨度**: 约7天的小时级数据

### 字段说明

| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| `ts` | TIMESTAMP | 数据采样时间点 |
| `device_name` | NCHAR | 设备名称/标识 |
| `_wstart` | TIMESTAMP | 时间窗口起始 |
| `_wend` | TIMESTAMP | 时间窗口结束 |
| `sum_hour` | DOUBLE | 小时累计值 |
| `avg_hour` | DOUBLE | 小时平均值 |
| `min_hour` | DOUBLE | 小时最小值 |
| `max_hour` | DOUBLE | 小时最大值 |
| `count_hour` | BIGINT | 采样点数 |
| `location_id` | VARCHAR | 位置标识 |

## 设备类型

### 设备总数: 约200个不同设备

### 主要设备类型

1. **温度监测设备**
   - TEMP系列设备 (TEMP_01, TEMP_02等)
   - 监测环境温度和设备温度

2. **压力监测设备**
   - PRESS系列设备 (PRESS_01, PRESS_02等)
   - 监测管道和容器压力

3. **控制阀门设备**
   - VALVE系列设备 (VALVE_01, VALVE_02等)
   - 控制流量和压力

4. **电机设备**
   - MOTOR系列设备 (MOTOR_01, MOTOR_02等)
   - 驱动各类机械设备

5. **流量监测设备**
   - FLOW系列设备 (FLOW_01, FLOW_02等)
   - 监测管道流量

## Agent执行的操作

### 1. 列出数据表

```
Action: sql_db_list_tables
```

**结果**: 发现表 `sensor_data_table`

### 2. 获取表结构

```
Action: sql_db_schema
```

**结果**: 获取了完整的字段列表和数据类型

### 3. 查询设备列表

```sql
SELECT DISTINCT device_name 
FROM demo_datasource.sensor_data_table;
```

**结果**: 发现约200个不同设备

### 4. 设备数据统计

```sql
SELECT 
  device_name, 
  COUNT(*) as data_points, 
  AVG(avg_hour) as avg_value, 
  STDDEV(avg_hour) as std_value 
FROM demo_datasource.sensor_data_table 
GROUP BY device_name 
ORDER BY data_points DESC 
LIMIT 20;
```

**示例结果**:
```
设备名称              数据点数  平均值      标准差
TEMP_01              165      27.98      2.33
TEMP_02              165      28.03      2.54
FLOW_01              165      122.75     66.20
PRESS_01             165      2.45       0.53
TEMP_03              165      29.80      4.52
```

## 生成的分析报告

### 1. 表结构分析

- **数据表格式**: TDEngine超级表
- **总记录数**: 约10,000条
- **时间范围**: 约7天的小时级数据

### 2. 设备分布分析

- **设备总数**: 约200个不同设备
- **主要设备类型**:
  - 温度监测设备
  - 压力监测设备
  - 控制阀门设备
  - 电机设备
  - 流量监测设备

### 3. 数据统计特征

- 大部分设备有约165个数据点（约7天的小时数据）
- 温度监测设备数据稳定（标准差2-5度）
- 流量设备数据波动较大
- 压力数据相对稳定

### 4. 设备相关性分析

Agent自动分析设备间的相关性和依赖关系，识别：
- 上游设备与下游设备的关联
- 控制设备与被控设备的关系
- 数据异常的传播路径

## 使用自然语言查询示例

### 示例1: 查询设备列表

```
用户: "列出所有设备"
Agent执行: SELECT DISTINCT device_name FROM sensor_data_table
```

### 示例2: 查询特定设备数据

```
用户: "查询FLOW_01过去24小时的数据"
Agent执行: 
SELECT ts, avg_hour, max_hour, min_hour 
FROM sensor_data_table 
WHERE device_name = 'FLOW_01' 
  AND ts > NOW() - INTERVAL 24 HOUR
```

### 示例3: 异常检测

```
用户: "找出数据异常的设备"
Agent执行:
SELECT device_name, AVG(avg_hour) as avg, STDDEV(avg_hour) as std
FROM sensor_data_table
GROUP BY device_name
HAVING std > 50  -- 标准差过大表示异常
```

### 示例4: 设备相关性分析

```
用户: "分析设备之间的相关性和依赖关系"
Agent执行:
1. 查询所有设备数据
2. 计算设备间的相关系数
3. 识别强相关的设备对
4. 分析上下游依赖关系
5. 生成相关性报告
```

## 关键发现

### 1. Agent自动适配

- Agent自动发现表结构
- 自动识别字段类型
- 自动生成合适的SQL查询
- 自动处理TDengine特有的语法

### 2. 错误处理

当遇到TDengine特有的错误时，Agent会自动调整查询策略，使用兼容的SQL语法。

### 3. 智能分析

Agent能够：
- 自动生成综合分析报告
- 识别数据模式
- 发现异常设备
- 分析设备相关性

## 最佳实践

### 1. 数据源命名

使用清晰的命名规范：
- `demo_datasource` - 明确标识数据源类型
- `sensor_data_table` - 明确标识表用途

### 2. 字段命名

使用描述性字段名：
- `device_name` - 设备名称
- `avg_hour` - 小时平均值
- `count_hour` - 采样点数

### 3. 时间字段

TDengine推荐使用：
- `ts` - 主时间戳字段
- `_wstart`, `_wend` - 时间窗口字段

### 4. 聚合字段

预先计算聚合值：
- `sum_hour` - 小时累计
- `avg_hour` - 小时平均
- `min_hour`, `max_hour` - 小时极值

## 与Skill文档的对应关系

这个实际案例验证了skill文档中的以下内容：

1. ✅ **TDengine连接** - 实际连接成功
2. ✅ **时序数据查询** - 成功查询小时级数据
3. ✅ **设备监控** - 成功监控约200个设备
4. ✅ **数据聚合** - 使用小时级聚合数据
5. ✅ **异常检测** - 通过标准差识别异常
6. ✅ **自然语言交互** - Agent理解自然语言并生成SQL

## 总结

这个案例展示了：
- MindsDB AI Agent能够无缝连接TDengine
- 自动发现和理解表结构
- 智能生成SQL查询
- 自动分析数据并生成报告
- 支持工业设备的监控场景

证明了Agent + MCP架构在实际工业场景中的有效性！
