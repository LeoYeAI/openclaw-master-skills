# GORM 并发控制：乐观锁 / 悲观锁 / CAS

## 1. 乐观锁（推荐，适合读多写少）

### 方案一：version 字段（最常用）

```go
type Product struct {
    gorm.Model
    Name    string
    Stock   int
    Version int `gorm:"default:0"`
}

func DeductStock(db *gorm.DB, productID uint, qty int) error {
    return db.Transaction(func(tx *gorm.DB) error {
        var p Product
        if err := tx.First(&p, productID).Error; err != nil {
            return err
        }

        result := tx.Model(&p).
            Where("version = ?", p.Version). // 版本号守卫
            Updates(map[string]any{
                "stock":   gorm.Expr("stock - ?", qty),
                "version": gorm.Expr("version + 1"),
            })

        if result.Error != nil {
            return result.Error
        }
        if result.RowsAffected == 0 {
            return errors.New("concurrent update conflict, please retry")
        }
        return nil
    })
}
```

### 方案二：GORM 插件 optimisticlock（官方推荐）

```go
import "gorm.io/plugin/optimisticlock"

type Product struct {
    gorm.Model
    Name    string
    Stock   int
    Version optimisticlock.Version // 自动处理版本比对
}

// 直接 Save，冲突时自动返回 optimisticlock.ErrOptimisticLock
if err := db.Save(&product).Error; err != nil {
    if errors.Is(err, optimisticlock.ErrOptimisticLock) {
        // 重新读取并重试
    }
}
```

### 乐观锁重试封装

```go
func WithRetry(maxRetries int, fn func() error) error {
    for i := 0; i < maxRetries; i++ {
        err := fn()
        if err == nil {
            return nil
        }
        if errors.Is(err, optimisticlock.ErrOptimisticLock) ||
           strings.Contains(err.Error(), "conflict") {
            time.Sleep(time.Duration(i*10) * time.Millisecond) // 指数退避
            continue
        }
        return err // 非冲突错误，直接返回
    }
    return fmt.Errorf("max retries (%d) exceeded", maxRetries)
}

// 使用
err := WithRetry(3, func() error {
    return DeductStock(db, productID, qty)
})
```

---

## 2. 悲观锁（适合写多冲突高，或需要强一致）

```go
// FOR UPDATE — 锁住读取的行，事务结束后释放
func TransferBalance(db *gorm.DB, fromID, toID uint, amount int64) error {
    return db.Transaction(func(tx *gorm.DB) error {
        var from, to Account

        // 按固定顺序加锁，防止死锁（始终先锁 ID 小的）
        ids := []uint{fromID, toID}
        sort.Slice(ids, func(i, j int) bool { return ids[i] < ids[j] })

        if err := tx.Set("gorm:query_option", "FOR UPDATE").
            First(&from, ids[0]).Error; err != nil {
            return err
        }
        if err := tx.Set("gorm:query_option", "FOR UPDATE").
            First(&to, ids[1]).Error; err != nil {
            return err
        }

        if from.Balance < amount {
            return errors.New("insufficient balance")
        }

        tx.Model(&from).Update("balance", gorm.Expr("balance - ?", amount))
        tx.Model(&to).Update("balance", gorm.Expr("balance + ?", amount))
        return nil
    })
}

// FOR SHARE — 共享锁（允许其他事务也加共享锁，但阻止排它锁）
tx.Set("gorm:query_option", "LOCK IN SHARE MODE").First(&record, id)
```

---

## 3. CAS 原子更新（无锁，适合计数器/状态流转）

```go
// 状态机流转：只有 pending 状态才能变 processing
result := db.Model(&Order{}).
    Where("id = ? AND status = ?", orderID, "pending").
    Update("status", "processing")

if result.RowsAffected == 0 {
    return errors.New("order not in pending state or already claimed")
}

// 库存扣减（防止超卖，不依赖事务）
result = db.Model(&Product{}).
    Where("id = ? AND stock >= ?", productID, qty).
    Update("stock", gorm.Expr("stock - ?", qty))

if result.RowsAffected == 0 {
    return errors.New("insufficient stock")
}
```

---

## 4. 选型指南

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| 用户信息编辑（冲突少） | 乐观锁 version | 读多写少，无锁性能好 |
| 库存扣减（高并发） | CAS（stock >= qty）| 单条 SQL，无事务开销 |
| 转账/余额操作 | 悲观锁 FOR UPDATE | 强一致，操作复杂 |
| 订单状态流转 | CAS WHERE status = ? | 原子，天然幂等 |
| 分布式场景 | Redis 分布式锁 + DB 乐观锁 | DB 锁不跨实例 |

## 5. 常见坑

- **悲观锁忘记排序加锁** → 死锁，永远按固定顺序（如 ID 升序）加锁
- **乐观锁用 Updates(struct)** → version 字段为 0 被忽略，改用 map
- **事务外执行 FOR UPDATE** → 锁立即释放，毫无意义
- **高并发下乐观锁重试风暴** → 加指数退避 + 最大重试次数限制
