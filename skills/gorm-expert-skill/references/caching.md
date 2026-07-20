# GORM 缓存集成（Cache-Aside with Redis）

> 缓存层是 GORM 性能优化的重要一环。本文覆盖 Cache-Aside 模式、防击穿、防雪崩、缓存一致性。

---

## 1. Cache-Aside 标准模式

```
读：先查 Redis → 未命中 → 查 DB → 写 Redis → 返回
写：更新 DB → 删除 Redis 缓存（不更新，避免并发不一致）
```

```go
type UserRepo struct {
    db  *gorm.DB
    rdb *redis.Client
}

func (r *UserRepo) GetUser(ctx context.Context, id uint) (*User, error) {
    cacheKey := fmt.Sprintf("user:%d", id)

    // 1. 读缓存
    val, err := r.rdb.Get(ctx, cacheKey).Bytes()
    if err == nil {
        var user User
        if err := json.Unmarshal(val, &user); err == nil {
            return &user, nil
        }
    }

    // 2. 缓存未命中，查 DB
    var user User
    if err := r.db.WithContext(ctx).First(&user, id).Error; err != nil {
        if errors.Is(err, gorm.ErrRecordNotFound) {
            // 防缓存穿透：缓存空值，短 TTL
            r.rdb.Set(ctx, cacheKey, "null", 1*time.Minute)
            return nil, ErrNotFound
        }
        return nil, err
    }

    // 3. 写缓存
    if data, err := json.Marshal(user); err == nil {
        r.rdb.Set(ctx, cacheKey, data, 30*time.Minute)
    }
    return &user, nil
}

func (r *UserRepo) UpdateUser(ctx context.Context, user *User) error {
    // 先更新 DB
    if err := r.db.WithContext(ctx).Save(user).Error; err != nil {
        return err
    }
    // 删除缓存（写后删除，不更新）
    cacheKey := fmt.Sprintf("user:%d", user.ID)
    r.rdb.Del(ctx, cacheKey)
    return nil
}
```

---

## 2. 防缓存击穿（单个热点 Key）

```go
import "golang.org/x/sync/singleflight"

type UserRepo struct {
    db    *gorm.DB
    rdb   *redis.Client
    group singleflight.Group
}

func (r *UserRepo) GetUser(ctx context.Context, id uint) (*User, error) {
    cacheKey := fmt.Sprintf("user:%d", id)

    // 先查 Redis（快路径）
    if val, err := r.rdb.Get(ctx, cacheKey).Bytes(); err == nil {
        var user User
        json.Unmarshal(val, &user)
        return &user, nil
    }

    // singleflight：同一 key 并发请求只打一次 DB
    result, err, _ := r.group.Do(cacheKey, func() (any, error) {
        var user User
        if err := r.db.WithContext(ctx).First(&user, id).Error; err != nil {
            return nil, err
        }
        data, _ := json.Marshal(user)
        r.rdb.Set(ctx, cacheKey, data, 30*time.Minute)
        return &user, nil
    })
    if err != nil {
        return nil, err
    }
    return result.(*User), nil
}
```

---

## 3. 防缓存雪崩（TTL 随机抖动）

```go
// 固定 TTL 会导致大量 key 同时失效，引发 DB 压力峰值
// ❌ 所有 key 相同 TTL
r.rdb.Set(ctx, key, data, 30*time.Minute)

// ✅ 基础 TTL + 随机抖动（±20%）
func cacheSetWithJitter(rdb *redis.Client, ctx context.Context,
    key string, val []byte, baseTTL time.Duration) {
    jitter := time.Duration(rand.Int63n(int64(baseTTL) / 5)) // ±20%
    ttl := baseTTL + jitter
    rdb.Set(ctx, key, val, ttl)
}
```

---

## 4. 防缓存穿透（布隆过滤器）

```go
import "github.com/bits-and-blooms/bloom/v3"

// 启动时将所有有效 ID 加载到布隆过滤器
var bf *bloom.BloomFilter

func InitBloomFilter(db *gorm.DB) {
    bf = bloom.NewWithEstimates(1_000_000, 0.01) // 100万条，误判率1%
    var ids []uint64
    db.Model(&User{}).Pluck("id", &ids)
    for _, id := range ids {
        bf.Add([]byte(fmt.Sprintf("%d", id)))
    }
}

func (r *UserRepo) GetUser(ctx context.Context, id uint) (*User, error) {
    // 布隆过滤器快速拦截不存在的 ID
    if !bf.Test([]byte(fmt.Sprintf("%d", id))) {
        return nil, ErrNotFound
    }
    // ... 正常查询流程
}
```

---

## 5. 缓存一致性：延迟双删

```go
// 更新 DB 后，先删缓存 → 等一段时间 → 再删一次（防并发读写不一致）
func (r *UserRepo) UpdateUser(ctx context.Context, user *User) error {
    cacheKey := fmt.Sprintf("user:%d", user.ID)

    // 第一次删除
    r.rdb.Del(ctx, cacheKey)

    if err := r.db.WithContext(ctx).Save(user).Error; err != nil {
        return err
    }

    // 延迟第二次删除（异步，覆盖并发读写期间写入的旧缓存）
    go func() {
        time.Sleep(500 * time.Millisecond)
        r.rdb.Del(context.Background(), cacheKey)
    }()
    return nil
}
```

---

## 6. 列表缓存（带版本号失效）

```go
// 列表缓存用版本号控制失效，避免逐条删除
func (r *OrderRepo) GetUserOrders(ctx context.Context, userID uint) ([]Order, error) {
    // 获取当前版本号
    version, _ := r.rdb.Get(ctx, fmt.Sprintf("orders:version:%d", userID)).Int()
    cacheKey := fmt.Sprintf("orders:%d:v%d", userID, version)

    if val, err := r.rdb.Get(ctx, cacheKey).Bytes(); err == nil {
        var orders []Order
        json.Unmarshal(val, &orders)
        return orders, nil
    }

    var orders []Order
    r.db.WithContext(ctx).Where("user_id = ?", userID).Find(&orders)
    data, _ := json.Marshal(orders)
    r.rdb.Set(ctx, cacheKey, data, 10*time.Minute)
    return orders, nil
}

// 写操作时递增版本号，旧 key 自然失效（不需要逐条删除）
func (r *OrderRepo) CreateOrder(ctx context.Context, order *Order) error {
    if err := r.db.WithContext(ctx).Create(order).Error; err != nil {
        return err
    }
    r.rdb.Incr(ctx, fmt.Sprintf("orders:version:%d", order.UserID))
    return nil
}
```

---

## 7. 软删除与缓存

```go
// 软删除后缓存可能仍返回"已删除"记录
// 删除时需同步清除缓存
func (r *UserRepo) SoftDeleteUser(ctx context.Context, id uint) error {
    if err := r.db.WithContext(ctx).Delete(&User{}, id).Error; err != nil {
        return err
    }
    // 软删除也要清缓存
    r.rdb.Del(ctx, fmt.Sprintf("user:%d", id))
    return nil
}
```
