# GORM Raw SQL / Scan / Row 使用指南

## 何时用 Raw SQL

- 复杂聚合、窗口函数、GORM API 难以表达的 SQL
- 性能极度敏感的热路径（绕过 GORM 反射开销）
- 存储过程调用

## Raw + Scan

```go
// Scan 到自定义 struct（不需要是 Model）
type Result struct {
    UserID int64
    Total  int64
}
var results []Result
db.Raw(`
    SELECT user_id, SUM(amount) AS total
    FROM orders
    WHERE created_at >= ?
    GROUP BY user_id
    HAVING total > ?
`, time.Now().Add(-30*24*time.Hour), 1000).Scan(&results)

// 检查错误
if err := db.Error; err != nil {
    return err
}
```

## Exec（写操作）

```go
db.Exec("UPDATE orders SET status = ? WHERE expired_at < ?", "expired", time.Now())
// 获取影响行数
result := db.Exec("DELETE FROM logs WHERE created_at < ?", cutoff)
fmt.Println(result.RowsAffected)
```

## Row / Rows（流式读取）

```go
// 单行
var name string
row := db.Raw("SELECT name FROM users WHERE id = ?", 1).Row()
row.Scan(&name)

// 多行（大数据量流式处理，不全量加载内存）
rows, err := db.Raw("SELECT id, name FROM users WHERE status = ?", "active").Rows()
defer rows.Close()
for rows.Next() {
    var id int64
    var name string
    rows.Scan(&id, &name)
    // 逐行处理
}
```

## PreparedStatement 与 Raw SQL

开启 `PrepareStmt: true` 后，Raw SQL 同样会被缓存：

```go
// 第一次执行：编译 SQL
// 后续执行：直接复用 prepared statement
db.Raw("SELECT * FROM users WHERE id = ?", id).Scan(&user)
```

手动使用 prepared statement：

```go
stmt, err := db.DB().PrepareContext(ctx, "SELECT * FROM users WHERE id = ?")
defer stmt.Close()
row := stmt.QueryRowContext(ctx, userID)
```

## Named 参数（可读性更好）

```go
db.Where("name = @name OR email = @email", sql.Named("name", "jinzhu"), sql.Named("email", "jinzhu@example.com")).Find(&users)

// Raw 同样支持
db.Raw("SELECT * FROM users WHERE name = @name", map[string]any{"name": "jinzhu"}).Scan(&users)
```

---

## Find / First / Take / Last 行为差异（v2 重要变化）

### 方法对比

| 方法 | 隐式 ORDER BY | 触发 ErrRecordNotFound | 适用场景 |
|------|-------------|----------------------|---------|
| `First` | `ORDER BY id ASC LIMIT 1` | ✅ 是 | 按主键取第一条 |
| `Last` | `ORDER BY id DESC LIMIT 1` | ✅ 是 | 按主键取最后一条 |
| `Take` | 无 | ✅ 是 | 不需要排序的单条查询（推荐） |
| `Find` | 无 | ❌ 否（返回空切片） | 查询列表 |

```go
// First / Last / Take：找不到时返回 gorm.ErrRecordNotFound
var user User
err := db.Where("id = ?", 999).First(&user).Error
if errors.Is(err, gorm.ErrRecordNotFound) {
    // 正常处理：记录不存在
}

// ❌ v1 的旧写法，v2 中已移除
// if gorm.IsRecordNotFoundError(err) { ... }

// Find：找不到时不报错，返回空切片
var users []User
db.Where("status = ?", 99).Find(&users)
// err == nil，len(users) == 0

// ✅ 按主键查单条，用 Take（无 ORDER BY 开销）
db.Where("id = ?", id).Take(&user)

// ✅ 需要有序取第一条，用 First
db.Where("status = ?", "pending").Order("priority DESC").First(&task)
```

### Error 处理规范（v2）

```go
// ✅ v2 正确写法：errors.Is
if errors.Is(err, gorm.ErrRecordNotFound) { }
if errors.Is(err, gorm.ErrInvalidTransaction) { }
if errors.Is(err, gorm.ErrMissingWhereClause) { }

// ✅ 封装辅助函数，统一处理
func IsNotFound(err error) bool {
    return errors.Is(err, gorm.ErrRecordNotFound)
}

func IgnoreNotFound(err error) error {
    if IsNotFound(err) {
        return nil
    }
    return err
}

// 使用
user, err := userModel.Find(ctx, id)
if err != nil {
    if IsNotFound(err) {
        return nil, ErrUserNotFound // 转换为业务错误
    }
    return nil, err
}
```
