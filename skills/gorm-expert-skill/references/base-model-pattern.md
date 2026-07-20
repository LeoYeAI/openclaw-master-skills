# GORM 泛型 BaseModel 设计规范

> 本文档总结在实际项目（`dbcore.BaseModel[T]` 模式）中发现的常见 Bug、性能问题与最佳实践。

---

## 1. QueryBuilder —— args 顺序 Bug（高危）

### 问题

`InStrings` / `InInts` 在循环内边追加 `args` 边构建 `placeholders`，当有多个链式条件时，`args` 的追加顺序与 `conditions` 中占位符的顺序错位：

```go
// ❌ 错误写法：args 在循环内追加，condition 在循环外追加
func (q *QueryBuilder) InStrings(field string, values []string) *QueryBuilder {
    if len(values) > 0 {
        placeholders := make([]string, len(values))
        for i, v := range values {
            placeholders[i] = "?"
            q.args = append(q.args, v)   // ← 先追加 args
        }
        q.conditions = append(q.conditions, ...) // ← 后追加 condition
    }
}
// 对比 In() 是 q.args = append(q.args, values...) 在循环外统一追加
// 不一致导致：链式调用时 args 顺序与占位符不匹配，SQL 参数绑定出错
```

### 修复

```go
// ✅ 正确写法：先构建 placeholders 和 ifaces，再统一追加
func (q *QueryBuilder) InStrings(field string, values []string) *QueryBuilder {
    if len(values) > 0 {
        placeholders := make([]string, len(values))
        ifaces := make([]interface{}, len(values))
        for i, v := range values {
            placeholders[i] = "?"
            ifaces[i] = v
        }
        // condition 和 args 同步追加，顺序一致
        q.conditions = append(q.conditions,
            fmt.Sprintf("%s IN (%s)", field, strings.Join(placeholders, ",")))
        q.args = append(q.args, ifaces...)
    }
    return q
}
```

> `InInts` 同样有此问题，修复方式相同。

---

## 2. 软删除 + 唯一索引冲突

### 问题

`uniqueIndex` 不包含 `deleted_at` 时，软删除后该字段值仍占用唯一约束，重新创建相同值报 `Duplicate entry`：

```go
// ❌ 软删除后 order_no 仍占用唯一约束，同订单号无法重建
OrderNo    string         `gorm:"uniqueIndex"`
DeletedAt  gorm.DeletedAt `gorm:"index"`
```

### 修复

```go
// ✅ 复合唯一索引：order_no + deleted_at
// 软删除后 deleted_at = timestamp（非 NULL），不与新记录的 NULL 冲突
OrderNo    string         `gorm:"column:order_no;uniqueIndex:idx_order_no_del"`
DeletedAt  gorm.DeletedAt `gorm:"index;uniqueIndex:idx_order_no_del"`
```

> 原理：MySQL 唯一索引中多个 NULL 不冲突。软删除前 `deleted_at IS NULL`，软删除后 `deleted_at = 时间戳`，两者不相等，新记录可以正常插入。

---

## 3. AutoMigrate 生产环境风险

### 问题

```go
// ❌ 服务启动时执行 AutoMigrate，大表会锁表，影响线上服务
func NewOrderModel(db *gorm.DB, isMigrate bool) OrderModel {
    if isMigrate {
        db.AutoMigrate(&Order{})  // 100万行以上会触发 ALTER TABLE 锁表
    }
}
```

### 修复

```go
// ✅ 生产环境禁用 AutoMigrate，使用 golang-migrate 脚本管理迁移
func NewOrderModel(db *gorm.DB, isMigrate bool) OrderModel {
    if isMigrate {
        migrateDB := db.Session(&gorm.Session{})
        migrateDB.DisableForeignKeyConstraintWhenMigrating = true // 禁止物理 FK
        if err := migrateDB.AutoMigrate(&Order{}); err != nil {
            panic(err)
        }
    }
    // ...
}
```

**环境策略**：

| 环境 | isMigrate | 迁移方式 |
|------|-----------|----------|
| 本地开发 | `true` | AutoMigrate（快速迭代） |
| 测试环境 | `true` | AutoMigrate |
| 生产环境 | `false` | golang-migrate 脚本（详见 references/migration.md） |

---

## 4. Find() 应使用 Take() 而非 First()

### 问题

```go
// ❌ First() 会隐式追加 ORDER BY id，按主键查单条无需排序
func (m *BaseModel[T]) Find(ctx context.Context, id string) (*T, error) {
    m.GetTxDB(ctx).Where("id = ?", id).First(&v)
    // 实际执行: SELECT * FROM t WHERE id=? ORDER BY id LIMIT 1
}
```

### 修复

```go
// ✅ Take() 不追加 ORDER BY，语义更准确，略微减少排序开销
m.GetTxDB(ctx).Where("id = ?", id).Take(&v)
// 实际执行: SELECT * FROM t WHERE id=? LIMIT 1
```

| 方法 | 语义 | 隐式 ORDER BY |
|------|------|--------------|
| `First()` | 按主键升序取第一条 | `ORDER BY id ASC` |
| `Last()` | 按主键降序取第一条 | `ORDER BY id DESC` |
| `Take()` | 不排序取一条 | 无 |

---

## 5. ListAll() 建议加软上限

### 问题

```go
// ❌ 无行数限制，百万级表直接 OOM
func (m *BaseModel[T]) ListAll(...) ([]*T, error) {
    db.Find(&list) // 全表加载
}
```

### 修复

```go
const maxListAllSize = 10_000

func (m *BaseModel[T]) ListAll(ctx context.Context, orders ...Order) ([]*T, error) {
    var list []*T
    db := applyOrders(m.GetTxDB(ctx), orders)
    return list, db.Limit(maxListAllSize).Find(&list).Error
}
```

> 如需处理超大数据集，使用 `FindInBatches` 替代 `ListAll`：
> ```go
> db.FindInBatches(&batch, 500, func(tx *gorm.DB, batchNum int) error {
>     process(batch)
>     return nil
> })
> ```

---

## 6. Page() 消除重复的 WHERE 条件构建

### 问题

```go
// ❌ COUNT 和数据查询各自重复构建相同的 WHERE 条件
countDB := m.GetTxDB(ctx).Model(new(T))
if query != "" { countDB = countDB.Where(query, args...) }
countDB.Count(&total)

queryDB := m.GetTxDB(ctx).Model(new(T))          // 完全重复
if query != "" { queryDB = queryDB.Where(query, args...) }
queryDB.Offset(offset).Limit(pageSize).Find(&list)
```

### 修复

```go
// ✅ 提取公共 baseDB，两次查询复用，Session() 隔离避免条件累积
baseDB := m.GetTxDB(ctx).Model(new(T))
if query != "" {
    baseDB = baseDB.Where(query, args...)
}

baseDB.Session(&gorm.Session{}).Count(&total)

applyOrders(baseDB.Session(&gorm.Session{}), orders).
    Offset(offset).Limit(pageSize).Find(&list)
```

> **为什么要 `Session(&gorm.Session{})`**：GORM 的 `*gorm.DB` 是值语义，但内部 `Statement` 是指针，直接复用 `baseDB` 做两次查询会导致条件累积（第二次查询携带第一次的 COUNT 相关状态）。`Session` 开启新的独立会话，安全复用条件。

---

## 7. 游标分页（大数据量推荐）

```go
// Page() 的 OFFSET 分页在大页码时性能退化（扫描并丢弃前 N 行）
// page=1000, pageSize=20 → OFFSET=19980 → 扫描近 2 万行

// ✅ 游标分页：无论第几页，只扫描 pageSize 行
func (m *BaseModel[T]) PageAfter(ctx context.Context,
    afterID string, pageSize int,
    query string, orders []Order, args ...interface{}) ([]*T, error) {

    if afterID != "" {
        if query != "" {
            query = "id > ? AND (" + query + ")"
            args = append([]interface{}{afterID}, args...)
        } else {
            query = "id > ?"
            args = []interface{}{afterID}
        }
    }
    // ...
    db.Order("id ASC").Limit(pageSize).Find(&list)
}

// 使用方式
page1, _ := model.PageAfter(ctx, "", 20, "status=?", nil, 1)
lastID := page1[len(page1)-1].ID
page2, _ := model.PageAfter(ctx, lastID, 20, "status=?", nil, 1)
```

---

## 8. 多租户隔离（可开关）

多租户通过 `dbcore.Config` 全局配置，支持开启和关闭：

```go
// ✅ 开启多租户（程序初始化时调用一次）
dbcore.SetConfig(dbcore.Config{
    TenantEnabled: true,            // 开启多租户隔离
    TenantField:   "tenant_id",     // 租户字段名（默认 "tenant_id"）
    TenantStrict:  true,            // 严格模式：无租户时拒绝查询
    TenantExtractor: func(ctx context.Context) string {
        if tid, ok := ctx.Value("tenant_id").(string); ok {
            return tid
        }
        return ""
    },
})

// ✅ 关闭多租户（默认值，无需调用 SetConfig）
// 或显式关闭：
dbcore.SetConfig(dbcore.Config{TenantEnabled: false})
```

**工作原理**：开启后 `BaseModel.GetTxDB()` 自动注入 `WHERE tenant_id = ?`，
所有 CRUD 方法（List/Page/Find/Delete/Update）均自动隔离，无需手动拼接条件。

```go
// 开启多租户后，调用方只需确保 ctx 中携带租户信息
ctx := context.WithValue(ctx, "tenant_id", "tenant_001")
orders, _ := model.List(ctx, "order_status=?", nil, 1)
// 实际执行: WHERE tenant_id = 'tenant_001' AND order_status = 1

// 严格模式下，ctx 无租户信息时自动拒绝查询（WHERE 1=0）
orders, _ := model.List(context.Background(), "", nil)
// 实际执行: WHERE 1=0 → 返回空结果，防止数据越权
```

> **何时开启**：SaaS 多租户系统、需要行级数据隔离的场景。
> **何时关闭**：单租户系统、内部工具、无租户概念的项目。

---

## 9. 扩展 JSON 字段用 datatypes.JSON

```go
// ❌ string 存 JSON：需手动 Marshal/Unmarshal，无法利用 MySQL JSON 函数查询
ExtData string `gorm:"column:ext_data;type:text"`

// ✅ datatypes.JSON：自动序列化，支持 JSONQuery
import "gorm.io/datatypes"

ExtData datatypes.JSON `gorm:"column:ext_data;type:json"`

// 支持 JSON 字段查询
db.Where(datatypes.JSONQuery("ext_data").HasKey("source")).Find(&orders)
db.Where(datatypes.JSONQuery("ext_data").Equals("神州", "source")).Find(&orders)
```

---

## 10. Page / PageAfter 参数校验

### 问题

```go
// ❌ page=0 或 page=-1 会导致负 offset → SQL 报错或返回空
offset := (page - 1) * pageSize  // page=0 → offset=-20

// ❌ pageSize=0 → LIMIT 0 永远返回空
// ❌ pageSize=999999 → 一次查百万行 OOM
```

### 修复

```go
// ✅ Page 方法自动校正参数
if page <= 0 {
    page = 1
}
if pageSize <= 0 {
    pageSize = 20
} else if pageSize > 1000 {
    pageSize = 1000
}
```

> PageAfter 同理，自动校正 `pageSize`。上限 1000 是合理默认，实际业务可按需调整常量。

---

## 11. IN 子句大小限制

### 问题

```go
// ❌ 传入 10 万个 ID，生成的 SQL 可能超过 max_allowed_packet
model.DeleteByIds(ctx, hugeSlice) // WHERE id IN (?, ?, ?, ... 100000 个)
```

### 修复

```go
const maxInSize = 1000

func (m *BaseModel[T]) DeleteByIds(ctx context.Context, ids []string) error {
    if len(ids) > maxInSize {
        return fmt.Errorf("dbcore: DeleteByIds count %d exceeds max %d", len(ids), maxInSize)
    }
    // ...
}
```

> `ListByIds` 同样有此限制。超限场景建议分批处理或改用 `DeleteBy` / `List` + 条件查询。

---

## 12. List 方法 Limit 保护

### 问题

```go
// ❌ List 无条件调用时可能全表扫描
model.List(ctx, "", nil) // 等同于 SELECT * FROM orders → 百万行 OOM
```

### 修复

```go
const maxListSize = 5000

func (m *BaseModel[T]) List(...) ([]*T, error) {
    // ...
    return list, db.Limit(maxListSize).Find(&list).Error
}
```

> 三层保护梯度：
> - `List` → `maxListSize = 5000`（带 WHERE 场景）
> - `ListAll` → `maxListAllSize = 10000`（全量加载场景）
> - 超大数据集 → `FindInBatches` / `PageAfter` 游标分页

---

## 13. QueryBuilder.NotLike 方法

```go
// ✅ 排除包含特定关键词的记录
qb := NewQueryBuilder().
    Eq("status", 1).
    NotLike("name", "测试")  // name NOT LIKE '%测试%'
query, args := qb.Build()
// query: "status = ? AND name NOT LIKE ?"
// args:  [1, "%测试%"]
```

> 与 Like / LikeLeft / LikeRight 对称，同样经过 `safeField()` 校验防注入。

---

## 14. QueryBuilder.OrGroup —— OR 分组支持

```go
// ❌ 原版只能通过 Raw() 手写 OR 条件，容易出错
qb.Raw("(order_status = ? OR order_status = ?)", 4, 5)

// ✅ 使用 OrGroup 组合多个子条件
qb.OrGroup(
    NewQueryBuilder().Eq("order_status", 4),
    NewQueryBuilder().Eq("order_status", 5),
)
// 生成: (order_status = ? OR order_status = ?)  args: [4, 5]

// 复合 OrGroup
qb.Eq("tenant_id", tenantID).
   OrGroup(
       NewQueryBuilder().Eq("pay_status", 2),
       NewQueryBuilder().Eq("pay_status", 3),
   ).
   Gte("create_at", startTime)
// 生成: tenant_id=? AND (pay_status=? OR pay_status=?) AND create_at>=?
```
