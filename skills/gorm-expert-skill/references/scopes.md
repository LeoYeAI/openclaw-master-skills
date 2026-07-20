# GORM Scopes（可复用查询条件）

> Scope 是将常用查询条件封装为函数，通过 `db.Scopes(...)` 组合调用，避免重复代码。

---

## 1. 基础用法

```go
// 定义 Scope 函数：签名固定为 func(*gorm.DB) *gorm.DB
func ActiveUser(db *gorm.DB) *gorm.DB {
    return db.Where("status = ?", "active")
}

func AgeOver(age int) func(*gorm.DB) *gorm.DB {
    return func(db *gorm.DB) *gorm.DB {
        return db.Where("age > ?", age)
    }
}

func OrderByCreatedDesc(db *gorm.DB) *gorm.DB {
    return db.Order("created_at DESC")
}

// 组合使用
db.Scopes(ActiveUser, AgeOver(18), OrderByCreatedDesc).Find(&users)
// 等价于: WHERE status='active' AND age>18 ORDER BY created_at DESC
```

---

## 2. 分页 Scope（高频通用）

```go
type PageQuery struct {
    Page     int // 从 1 开始
    PageSize int
}

func Paginate(q PageQuery) func(*gorm.DB) *gorm.DB {
    return func(db *gorm.DB) *gorm.DB {
        if q.PageSize <= 0 {
            q.PageSize = 20
        }
        if q.PageSize > 100 {
            q.PageSize = 100 // 防止超大分页
        }
        offset := (q.Page - 1) * q.PageSize
        return db.Offset(offset).Limit(q.PageSize)
    }
}

// 使用
db.Scopes(Paginate(PageQuery{Page: 2, PageSize: 20})).Find(&users)
```

> ⚠️ 大表分页仍需注意 OFFSET 性能，超过万级建议切换游标分页。

---

## 3. 时间范围 Scope

```go
func CreatedBetween(start, end time.Time) func(*gorm.DB) *gorm.DB {
    return func(db *gorm.DB) *gorm.DB {
        return db.Where("created_at BETWEEN ? AND ?", start, end)
    }
}

func LastNDays(n int) func(*gorm.DB) *gorm.DB {
    return func(db *gorm.DB) *gorm.DB {
        return db.Where("created_at >= ?", time.Now().AddDate(0, 0, -n))
    }
}

// 查询最近 7 天的活跃用户
db.Scopes(ActiveUser, LastNDays(7)).Find(&users)
```

---

## 4. 多租户行级隔离 Scope

```go
// 从 context 中提取 tenant_id，自动注入所有查询
func TenantScope(ctx context.Context) func(*gorm.DB) *gorm.DB {
    return func(db *gorm.DB) *gorm.DB {
        tenantID, ok := ctx.Value("tenant_id").(uint)
        if !ok || tenantID == 0 {
            // 没有租户信息时，返回空结果（安全默认）
            return db.Where("1 = 0")
        }
        return db.Where("tenant_id = ?", tenantID)
    }
}

// 在 Service 层统一使用
func (s *OrderService) ListOrders(ctx context.Context) ([]Order, error) {
    var orders []Order
    err := s.db.WithContext(ctx).
        Scopes(TenantScope(ctx), ActiveOrder).
        Find(&orders).Error
    return orders, err
}
```

---

## 5. 软删除相关 Scope

```go
// 只查已删除记录
func OnlyDeleted(db *gorm.DB) *gorm.DB {
    return db.Unscoped().Where("deleted_at IS NOT NULL")
}

// 包含已删除记录（用于管理后台）
func WithDeleted(db *gorm.DB) *gorm.DB {
    return db.Unscoped()
}

// 管理后台查所有（包含软删除）
db.Scopes(WithDeleted).Find(&users)
```

---

## 6. Scope 链式注册（Model 方法风格）

```go
// 推荐：在 Model 上定义领域 Scope，让查询意图更清晰
type Order struct {
    gorm.Model
    UserID uint
    Status string
    Amount int64
}

func (Order) Paid() func(*gorm.DB) *gorm.DB {
    return func(db *gorm.DB) *gorm.DB {
        return db.Where("status = ?", "paid")
    }
}

func (Order) ByUser(userID uint) func(*gorm.DB) *gorm.DB {
    return func(db *gorm.DB) *gorm.DB {
        return db.Where("user_id = ?", userID)
    }
}

// 调用
var o Order
db.Scopes(o.Paid(), o.ByUser(42)).Find(&orders)
```

---

## 7. 常见坑

| 问题 | 说明 | 解决方案 |
|------|------|----------|
| Scope 内修改了原 db 实例 | Scope 函数应 return 新 db，不要赋值给外部变量 | 确保只 return db.Where(...) |
| 分页 Scope 与 Count 冲突 | Count 查询不应带 Limit/Offset | Count 前不要调用 Paginate Scope |
| 多租户 Scope 未覆盖写操作 | Create/Update 时忘记注入 tenant_id | 用 BeforeCreate Hook 或 default tag 补充 |
