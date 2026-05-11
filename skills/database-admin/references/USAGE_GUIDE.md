# 数据库管理员使用指南 Usage Guide 📜

## 快速开始 Quick Start

### 🔹 安装与配置 Installation

```bash
# 设置连接参数（或直接在脚本中修改）
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=mydb
export DB_USER=postgres
export DB_PASSWORD=your_password

# 导出到路径（可选）
export BACKUP_DIR=/tmp/backup
```

### 🔹 环境检查 Environment Check

运行前确保：
- ✅ PostgreSQL >= 10.0
- ✅ Node.js >= 14.0
- ✅ `pg` npm 包已安装

---

## 核心脚本功能 Core Scripts

### 1. create_table.js - 建表工具

```bash
# 用法
node scripts/create_table.js --help

# 示例：创建用户表
node scripts/create_table.js users \
  "id:SERIAL PRIMARY KEY" \
  "email:VARCHAR(255) UNIQUE" \
  "username:TEXT NOT NULL" \
  "age:INT" \
  "created_at:TIMESTAMP DEFAULT CURRENT_TIMESTAMP"

# 添加索引
--index email --index username
```

### 2. insert_bulk.js - 批量插入

```bash
# 从 JSON 文件插入
node scripts/insert_bulk.js \
  --table products \
  --file /tmp/products.json \
  --batch 1000

# 使用 COPY 协议（更快）
node scripts/insert_bulk.js \
  --table orders \
  --copy true
```

### 3. query_optimizer.js - 查询优化

```bash
# 分析查询性能
node scripts/query_optimizer.js \
  --analyze "SELECT * FROM orders WHERE user_id=123"

# 生成索引报告
node scripts/query_optimizer.js \
  --index users

# 性能测试
node scripts/query_optimizer.js \
  --benchmark "SELECT count(*) FROM orders WHERE status='pending'" --iterations 50
```

### 4. backup_restore.js - 备份恢复

```bash
# 备份数据库
node scripts/backup_restore.js \
  --backup mydb \
  --dir /tmp/backup

# 导出 Schema（权限、表结构）
node scripts/backup_restore.js --schema > schema_backup.sql

# 恢复数据库
node scripts/backup_restore.js \
  --restore /tmp/mydb_20260315.sql

# 清理旧备份
node scripts/backup_restore.js \
  --cleanup --days 30
```

### 5. schema_migrate.js - Schema 迁移

```bash
# 添加列
node scripts/schema_migrate.js \
  add-column users profile JSONB

# 修改数据类型
node scripts/schema_migrate.js \
  modify-type products price NUMERIC(12,2)

# 创建索引
node scripts/schema_migrate.js \
  add-index orders user_idx user_id

# 迁移数据
node scripts/schema_migrate.js \
  migrate old_users new_users \
  --filter "is_active=true"
```

---

## 使用场景 Examples

### 🔹 场景 1：搭建新数据库 New Database Setup

```bash
# 1. 创建表结构
node scripts/create_table.js products ...
node scripts/create_table.js orders ...

# 2. 初始化索引
node scripts/query_optimizer.js --index products

# 3. 插入种子数据
node scripts/insert_bulk.js \
  --table products \
  --file initial_products.json
```

### 🔹 场景 2：性能调优 Performance Tuning

```bash
# 1. 分析慢查询
node scripts/query_optimizer.js \
  --analyze "SELECT * FROM orders WHERE status='pending'"

# 2. 基于建议创建索引
node scripts/schema_migrate.js \
  add-index orders status_idx status

# 3. 重新测试性能
node scripts/query_optimizer.js \
  --benchmark ...
```

### 🔹 场景 3：Schema 升级 Schema Upgrade

```bash
# 1. 备份当前状态
node scripts/backup_restore.js --schema > before_upgrade.sql

# 2. 添加新列
node scripts/schema_migrate.js \
  add-column users verification_token TEXT

# 3. 修改列类型（如果需要）
node scripts/schema_migrate.js \
  modify-type orders total_amount NUMERIC(15,4)

# 4. 记录变更
node schema_migrate.js log-migration users upgrade-v2

# 5. 清理旧备份
node scripts/backup_restore.js --cleanup --days 7
```

### 🔹 场景 4：生产环境备份 Production Backup

```bash
#!/bin/bash
# 定时脚本示例：daily_backup.sh

DATABASE=mydb
BACKUP_DIR=/data/backups/mydb

# 1. 导出 Schema
node scripts/backup_restore.js --schema > "$BACKUP_DIR/schema.sql"

# 2. 完整备份（使用 pg_dump）
pg_dump -U postgres $DATABASE > "$BACKUP_DIR/full_$DATE.sql"

# 3. 压缩
gzip "$BACKUP_DIR/full_$DATE.sql"

# 4. 上传到远程存储（s3/cos/gcs等）
# aws s3 cp local_file s3://bucket/...

# 5. 清理旧备份
node scripts/backup_restore.js --cleanup --days 30
```

---

## 常见问题 FAQ

### ❓ Q1: COPY 失败如何处理？

**A**: 检查数据格式：
- 字符串必须用单引号包裹
- NULL 值直接使用 `NULL`
- 数字不要加引号
- 布尔值转换为 TRUE/FALSE

### ❓ Q2: 索引创建很慢怎么办？

**A**: 
- 先分析表分布 `ANALYZE table_name;`
- 使用并发索引创建（PostgreSQL 12+）
- 分批次创建多个小索引

### ❓ Q3: 大批量插入性能问题？

**A**: 
- 使用 COPY 协议（最快，比 INSERT VALUES 快 10 倍）
- 调整 `work_mem` 参数
- 分批插入（每批不超过 5000 条）

### ❓ Q4: 如何验证备份完整性？

**A**: 
```bash
# 方式 1：导入测试
psql -f backup.sql -l

# 方式 2：计算校验和
md5sum backup.sql.gz
```

---

## 最佳实践 Best Practices

### 🔹 建表规范
- 主键用 SERIAL/BIGSERIAL（自动增长）
- 金额字段使用 NUMERIC(p,s) 而非 FLOAT/DOUBLE
- TEXT 类型避免用于短文本（建议 VARCHAR(n)）
- NULL 默认值慎用，尽量设 DEFAULT

### 🔹 索引策略
- WHERE 条件列优先创建索引
- JOIN 外键列必须建索引
- 多列索引遵循 WHERE 条件的列顺序
- 低基数列避免建索引

### 🔹 批量操作
- 大批量数据使用 COPY 而非 INSERT
- 事务包裹多个操作（BEGIN/COMMIT）
- 每批控制在 1000-5000 条之间

### 🔹 备份策略
- 定期全量备份（每天或每周）
- 增量备份（WAL 日志归档）
- 至少保留最近 30 天的备份
- 异地存储重要数据副本

---

*杜子美诗曰："工欲善其事，必先利其器" —— 数据库管理工具，助您高效行事*

📜 **杜甫 · database-admin**
