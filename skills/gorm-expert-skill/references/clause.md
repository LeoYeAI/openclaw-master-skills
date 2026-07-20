# GORM v2 Clause 系统

> Clause 是 GORM v2 底层 SQL 构建机制，通过组合 Clause 可以生成任意复杂 SQL，
> 同时保持类型安全和可组合性。

---

## 1. OnConflict（Upsert）

```go
import "gorm.io/gorm/clause"

// MySQL / SQLite：INSERT ... ON DUPLICATE KEY UPDATE
db.Clauses(clause.OnConflict{
    Columns:   []clause.Column{{Name: "email"}},          // 冲突判断字段
    DoUpdates: clause.AssignmentColumns([]string{"name", "updated_at"}), // 更新哪些字段
}).Create(&user)

// 冲突时更新所有字段（除主键）
db.Clauses(clause.OnConflict{
    UpdateAll: true,
}).Create(&user)

// 冲突时什么都不做（忽略重复）
db.Clauses(clause.OnConflict{DoNothing: true}).Create(&users)

// PostgreSQL：INSERT ... ON CONFLICT DO UPDATE
db.Clauses(clause.OnConflict{
    Columns:   []clause.Column{{Name: "order_no"}},
    DoUpdates: clause.Assignments(map[string]interface{}{
        "status":     2,
        "updated_at": gorm.Expr("NOW()"),
    }),
}).Create(&order)
```

---

## 2. Returning（PostgreSQL / SQLite）

```go
// INSERT ... RETURNING id, created_at（PostgreSQL 专有）
var result User
db.Clauses(clause.Returning{
    Columns: []clause.Column{{Name: "id"}, {Name: "created_at"}},
}).Create(&result)
fmt.Println(result.ID, result.CreatedAt) // 自动填充

// UPDATE ... RETURNING
db.Model(&user).
    Clauses(clause.Returning{}).
    Updates(map[string]interface{}{"name": "new_name"})
// result 自动填充更新后的值
```

---

## 3. Locking（SELECT ... FOR UPDATE / SHARE）

```go
// SELECT ... FOR UPDATE（排他锁，适合库存扣减、余额扣减）
db.Clauses(clause.Locking{Strength: "UPDATE"}).
    Where("id = ?", productID).
    First(&product)

// SELECT ... FOR UPDATE NOWAIT（不等待，立即失败）
db.Clauses(clause.Locking{
    Strength: "UPDATE",
    Options:  "NOWAIT",
}).First(&product)

// SELECT ... FOR UPDATE SKIP LOCKED（跳过已锁定行，适合任务队列）
db.Clauses(clause.Locking{
    Strength: "UPDATE",
    Options:  "SKIP LOCKED",
}).Limit(10).Find(&tasks) // 抢占式获取未被锁定的任务

// SELECT ... FOR SHARE（共享锁，允许并发读，阻止写）
db.Clauses(clause.Locking{Strength: "SHARE"}).
    Where("id = ?", id).First(&record)
```

### FOR UPDATE 完整事务示例

```go
err := db.Transaction(func(tx *gorm.DB) error {
    var stock Stock
    // 加锁读取
    if err := tx.Clauses(clause.Locking{Strength: "UPDATE"}).
        Where("product_id = ?", productID).
        First(&stock).Error; err != nil {
        return err
    }
    if stock.Qty < qty {
        return errors.New("库存不足")
    }
    // 扣减库存
    return tx.Model(&stock).
        Update("qty", gorm.Expr("qty - ?", qty)).Error
})
```

---

## 4. OrderBy（精确控制排序）

```go
// 多字段排序，精确控制 ASC/DESC
db.Clauses(clause.OrderBy{
    Columns: []clause.OrderByColumn{
        {Column: clause.Column{Name: "priority"}, Desc: true},
        {Column: clause.Column{Name: "created_at"}, Desc: false},
    },
}).Find(&tasks)

// 动态排序（避免 SQL 注入风险）
allowedFields := map[string]bool{"name": true, "created_at": true, "age": true}
sortField := req.SortField
if !allowedFields[sortField] {
    sortField = "created_at" // 默认排序字段
}
db.Clauses(clause.OrderBy{
    Columns: []clause.OrderByColumn{
        {Column: clause.Column{Name: sortField}, Desc: req.SortDesc},
    },
}).Find(&list)
```

---

## 5. Where / Having（复杂条件）

```go
// clause.Where 支持直接传 map / struct / SQL 表达式
db.Clauses(clause.Where{
    Exprs: []clause.Expression{
        clause.Eq{Column: "status", Value: 1},
        clause.Gte{Column: "age", Value: 18},
        clause.Like{Column: "name", Value: "%张%"},
    },
}).Find(&users)

// Having 条件（GROUP BY 后过滤）
db.Model(&Order{}).
    Select("user_id, SUM(amount) as total").
    Group("user_id").
    Having("total > ?", 10000).
    Scan(&results)
```

---

## 6. 自定义 Clause 表达式

```go
// 实现 clause.Expression 接口，生成自定义 SQL 片段
type JSONContains struct {
    Column string
    Key    string
    Value  interface{}
}

func (j JSONContains) Build(builder clause.Builder) {
    builder.WriteString("JSON_CONTAINS(")
    builder.WriteQuoted(j.Column)
    builder.WriteString(", JSON_OBJECT(")
    builder.AddVar(builder, j.Key)
    builder.WriteString(", ")
    builder.AddVar(builder, j.Value)
    builder.WriteString("))")
}

// 使用
db.Clauses(JSONContains{
    Column: "ext_data",
    Key:    "source",
    Value:  "ctrip",
}).Find(&orders)
// 生成: WHERE JSON_CONTAINS(ext_data, JSON_OBJECT('source', 'ctrip'))
```

---

## 7. Clause 组合使用（Upsert + Returning）

```go
// PostgreSQL：INSERT ... ON CONFLICT ... RETURNING
var inserted User
db.Clauses(
    clause.OnConflict{
        Columns:   []clause.Column{{Name: "email"}},
        DoUpdates: clause.AssignmentColumns([]string{"name", "updated_at"}),
    },
    clause.Returning{},
).Create(&inserted)
// inserted 自动填充 INSERT 或 UPDATE 后的值
```

---

## 8. 常用 Clause 速查表

| Clause | 用途 | 关键字段 |
|--------|------|---------|
| `clause.OnConflict` | Upsert | `Columns`, `DoUpdates`, `UpdateAll`, `DoNothing` |
| `clause.Returning` | 返回写入后的值（PG） | `Columns` |
| `clause.Locking` | FOR UPDATE / SHARE | `Strength`, `Options` |
| `clause.OrderBy` | 精确排序 | `Columns[]OrderByColumn` |
| `clause.Where` | 复杂 WHERE | `Exprs[]Expression` |
| `clause.Having` | GROUP BY 过滤 | 配合 Group() 使用 |
| `clause.From` | 自定义 FROM 子句 | 子查询场景 |
| `clause.Select` | 精确控制 SELECT 列 | `Columns` |
