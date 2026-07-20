# GORM 索引定义规范

---

## 1. 基础索引 Tag

```go
type User struct {
    gorm.Model
    Name  string `gorm:"index"`                          // 普通索引
    Email string `gorm:"uniqueIndex"`                    // 唯一索引
    Phone string `gorm:"index:idx_phone,unique"`         // 命名唯一索引
    Age   int    `gorm:"index:idx_age,sort:desc"`        // 降序索引
}
```

---

## 2. 复合索引

```go
type Order struct {
    gorm.Model
    UserID    uint   `gorm:"index:idx_user_status"`       // 复合索引字段1
    Status    string `gorm:"index:idx_user_status"`       // 复合索引字段2
    CreatedAt time.Time
}
// 生成: CREATE INDEX idx_user_status ON orders(user_id, status)
```

> **字段顺序即索引列顺序**，遵循最左前缀原则：`(user_id, status)` 可覆盖 `WHERE user_id=?` 和 `WHERE user_id=? AND status=?`，但不能覆盖单独 `WHERE status=?`。

---

## 3. 覆盖索引（Covering Index）

将查询需要的所有字段都放入索引，避免回表：

```go
// 场景：频繁查询 SELECT id, name, email WHERE status='active'
type User struct {
    gorm.Model
    Status string `gorm:"index:idx_status_cover"`
    Name   string `gorm:"index:idx_status_cover"`  // 覆盖列
    Email  string `gorm:"index:idx_status_cover"`  // 覆盖列
}
// 查询只需扫描索引，无需回表读取主键行
```

---

## 4. 前缀索引（长字符串）

```go
// VARCHAR(512) 建全量索引浪费空间，用前缀索引
type Article struct {
    gorm.Model
    Title   string `gorm:"index:idx_title,length:64"`   // 前64字符建索引
    Content string // 不建索引，用全文索引代替
}
```

---

## 5. 函数索引（MySQL 5.7+ / PG）

GORM Tag 不支持函数索引，需用 AutoMigrate 后手动创建或在 migration 文件中：

```sql
-- MySQL：对 email 小写建索引（不区分大小写查询）
CREATE INDEX idx_email_lower ON users((LOWER(email)));

-- PostgreSQL
CREATE INDEX idx_email_lower ON users(LOWER(email));
```

```go
// GORM 迁移后在 migration 文件中追加
db.Exec("CREATE INDEX idx_email_lower ON users((LOWER(email)))")
```

---

## 6. 全文索引

```go
// GORM Tag 定义全文索引（MySQL）
type Article struct {
    gorm.Model
    Title   string `gorm:"index:idx_fulltext,class:FULLTEXT"`
    Content string `gorm:"index:idx_fulltext,class:FULLTEXT"`
}

// 查询
db.Where("MATCH(title, content) AGAINST(? IN BOOLEAN MODE)", keyword).Find(&articles)
```

---

## 7. 索引失效场景

| 场景 | 原因 | 解决方案 |
|------|------|----------|
| `LIKE '%keyword%'` | 前导通配符 | 改 `LIKE 'keyword%'` 或全文索引 |
| `WHERE YEAR(created_at) = 2024` | 函数包裹索引列 | 改 `WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31'` |
| `WHERE age + 1 = 18` | 表达式计算 | 改 `WHERE age = 17` |
| `OR` 两侧字段不同索引 | 无法走单一索引 | 考虑 UNION 或复合索引 |
| 隐式类型转换 | `WHERE phone = 13800138000`（phone 是字符串） | 加引号 `WHERE phone = '13800138000'` |
| 联合索引跳列 | `(a,b,c)` 索引 WHERE b=? | 补充 a 条件，或建 (b) 单独索引 |

---

## 8. 用 EXPLAIN 验证索引

```go
// DryRun 生成 SQL，再手动 EXPLAIN
stmt := db.Session(&gorm.Session{DryRun: true}).
    Where("user_id = ? AND status = ?", 1, "paid").
    Find(&orders).Statement
sql := stmt.SQL.String()

// 执行 EXPLAIN
db.Raw("EXPLAIN " + sql, stmt.Vars...).Scan(&result)
```

关注 EXPLAIN 输出：
- `type`: 理想为 `ref` / `range`，避免 `ALL`（全表扫描）
- `key`: 实际使用的索引名，NULL 表示未走索引
- `rows`: 预估扫描行数，越小越好
- `Extra`: 出现 `Using filesort` 或 `Using temporary` 需优化
