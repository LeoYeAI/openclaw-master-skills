# 数据库迁移规范：golang-migrate vs AutoMigrate

## 1. 生产环境原则

| 环境 | 推荐方案 | 原因 |
|------|---------|------|
| 开发/本地 | `AutoMigrate` | 快速迭代，不关心历史 |
| 测试 CI | `AutoMigrate` 或迁移文件 | 一致性即可 |
| **生产** | **golang-migrate + 手写 SQL** | 可审查、可回滚、幂等 |

> ⚠️ **AutoMigrate 绝对不能用于生产**：它只增不减（不删列/索引），无回滚，无历史记录。

---

## 2. golang-migrate 使用规范

```bash
go get -u github.com/golang-migrate/migrate/v4
# CLI 工具
brew install golang-migrate
```

### 目录结构

```
migrations/
├── 000001_create_users.up.sql
├── 000001_create_users.down.sql
├── 000002_add_user_email_index.up.sql
├── 000002_add_user_email_index.down.sql
└── 000003_add_orders_table.up.sql
    000003_add_orders_table.down.sql
```

### 命名规范

```
{version}_{description}.{up|down}.sql
版本号用 6 位数字，单调递增，不能复用
描述用下划线分隔，简洁说明变更内容
```

### 代码集成（程序启动时自动执行）

```go
import (
    "github.com/golang-migrate/migrate/v4"
    _ "github.com/golang-migrate/migrate/v4/database/mysql"
    _ "github.com/golang-migrate/migrate/v4/source/file"
)

func RunMigrations(dsn string) error {
    m, err := migrate.New("file://migrations", "mysql://"+dsn)
    if err != nil {
        return fmt.Errorf("init migrate: %w", err)
    }
    defer m.Close()

    if err := m.Up(); err != nil && !errors.Is(err, migrate.ErrNoChange) {
        return fmt.Errorf("run migrations: %w", err)
    }
    return nil
}
```

---

## 3. 大表在线 DDL 规范（MySQL）

> 大表（>500万行 或 >10GB）直接 ALTER TABLE 会锁表，生产建议使用在线方案。

### MySQL 8.0+ 原生在线 DDL

```sql
-- 加列（INSTANT，瞬间完成，不重建表）
ALTER TABLE orders
    ADD COLUMN extra_info JSON DEFAULT NULL,
    ALGORITHM=INSTANT;

-- 加索引（INPLACE，在线重建，不锁写）
ALTER TABLE orders
    ADD INDEX idx_user_created (user_id, created_at),
    ALGORITHM=INPLACE, LOCK=NONE;

-- 修改列类型（需要 COPY，会锁表，慎用）
-- 建议用 pt-online-schema-change 或 gh-ost
ALTER TABLE orders MODIFY COLUMN amount DECIMAL(12,2) NOT NULL;
```

### 复杂变更用 gh-ost / pt-osc

```bash
# gh-ost（GitHub 开源，推荐）
gh-ost \
  --user="root" --password="xxx" \
  --host=127.0.0.1 --database=mydb --table=orders \
  --alter="ADD COLUMN remark TEXT, ADD INDEX idx_status(status)" \
  --execute

# 特点：基于 binlog 复制，零锁，支持随时暂停/限速
```

---

## 4. 迁移 SQL 编写规范

### 加列建议设置默认值（避免锁表）

```sql
-- ❌ 没有默认值，大表会全量更新每行
ALTER TABLE users ADD COLUMN age INT NOT NULL;

-- ✅ 有默认值，MySQL 8.0 INSTANT 算法
ALTER TABLE users ADD COLUMN age INT NOT NULL DEFAULT 0, ALGORITHM=INSTANT;
```

### down.sql 应可独立执行

```sql
-- 000003_add_orders_table.down.sql
DROP TABLE IF EXISTS orders;  -- IF EXISTS 保证幂等

-- 000002_add_user_email_index.down.sql
DROP INDEX IF EXISTS idx_user_email ON users;
```

### 数据迁移与结构迁移分离

```sql
-- 000004_add_status_column.up.sql  （结构变更）
ALTER TABLE orders ADD COLUMN new_status TINYINT DEFAULT 0;

-- 000005_migrate_status_data.up.sql  （数据迁移，单独版本）
UPDATE orders SET new_status = CASE status
    WHEN 'pending'  THEN 1
    WHEN 'paid'     THEN 2
    WHEN 'shipped'  THEN 3
    ELSE 0
END;

-- 000006_drop_old_status.up.sql  （上线稳定后再删旧列）
ALTER TABLE orders DROP COLUMN status;
```

---

## 5. 常用 CLI 命令

```bash
# 查看当前版本
migrate -path ./migrations -database "mysql://..." version

# 执行到最新
migrate -path ./migrations -database "mysql://..." up

# 回滚一步
migrate -path ./migrations -database "mysql://..." down 1

# 设置版本（慎用，跳过校验）
migrate -path ./migrations -database "mysql://..." force 5
```
