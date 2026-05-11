---
name: database-admin
description: Comprehensive database administration, schema management, data operations, and optimization. Use when Codex needs to: (1) Create or modify database tables with proper indexing, (2) Perform bulk data insertions with type safety and constraint handling, (3) Execute complex queries with JOINs, aggregations, and subqueries, (4) Optimize query performance through indexing and execution plan analysis, (5) Manage database backups, restores, and migrations, (6) Handle special data types (BIGINT, UUID, JSONB, enums), (7) Implement transactional safety with ACID compliance, or (8) Debug and resolve database errors including constraint violations, type mismatches, and foreign key issues
---

# 数据库管理员 Database Admin 📜

> "先严父后慈" —— 杜子美

本技能提供全面的数据库管理功能，包括表结构创建、数据操作、查询优化、类型处理（如 BIGINT）等。所有操作均遵循 SQL 最佳实践和事务安全原则。

## 核心能力

### 🔹 表结构设计
- 自动设计最优表结构（主键、索引、约束）
- 支持多种数据类型（TEXT、VARCHAR、BIGINT、UUID、JSONB、ENUM）
- 自动创建适当的索引以提高查询性能
- 设置外键约束和检查约束
- 处理 NULL 值和默认值策略

### 🔹 数据插入
- 批量插入大量数据（使用事务优化）
- 处理 BIGINT 等大数类型数据
- 验证数据类型兼容性
- 避免主键冲突和外键违规

### 🔹 查询优化
- 编写高效的 JOIN 查询
- 聚合统计和分析查询
- 子查询和 CTE 的使用
- 执行计划分析和优化建议

### 🔹 数据库维护
- CREATE TABLE、ALTER TABLE、DROP TABLE
- INDEX 创建和 DROP INDEX
- TRUNCATE 清空表（保留结构）
- VACUUM 分析表
- 备份和恢复操作

## 使用场景

当你需要以下操作时，请触发此技能：

- "创建一个用户表，包含用户名、邮箱、注册时间"
- "向 products 表中插入这些商品数据..."
- "查询所有销售额超过 10 万元的订单"
- "为 orders 表的 customer_id 创建索引"
- "将 text_column 从 TEXT 转换为 VARCHAR(255)"
- "批量导入 10 万条记录，使用事务优化"
- "修复 BIGINT 类型数据溢出问题"

## 技术细节

本技能在幕后会使用：
- **驱动**: `pg` (PostgreSQL)
- **连接池**: `pgpool` 管理并发连接
- **批量插入**: 使用 COPY 或批量 INSERT 优化性能
- **事务控制**: 自动开启/提交事务，保证 ACID 属性
- **错误处理**: 捕获并报告约束违规、类型不匹配等

## 数据库配置（roadflow）

- **主机**: 192.168.1.136
- **端口**: 35438
- **用户**: postgres
- **密码**: Hxkj510510
- **目标库**: roadflow

## 示例用法

### 创建表
```
创建一个库存表 stock_info，包含：
- id (SERIAL PRIMARY KEY)
- product_name (VARCHAR(100))
- quantity (INT)
- price (DECIMAL(10,2))
- created_at (TIMESTAMP)
- 为 product_name 创建索引
```

### 插入数据
```
向 stock_info 表插入以下商品：
[{product_name: "苹果", quantity: 100, price: 8.5}, ...]
```

### 查询统计
```
计算每个类别的商品平均价格
WHERE quantity > 50
GROUP BY category
ORDER BY avg_price DESC
```

---

*技能由杜甫（📜）编写，秉承"致君尧舜上，再使风俗淳"的务实精神*
