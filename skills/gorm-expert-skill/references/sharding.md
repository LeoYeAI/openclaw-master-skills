# GORM 分库分表（Sharding）

> 使用 `gorm.io/sharding` 插件（基于 Vitess / PlanetScale 分片逻辑）

---

## 1. 基础配置

```go
import (
    "gorm.io/sharding"
    "gorm.io/driver/mysql"
    "gorm.io/gorm"
)

db, _ := gorm.Open(mysql.Open(dsn), &gorm.Config{})

db.Use(sharding.Register(sharding.Config{
    ShardingKey:         "user_id",          // 分片键
    NumberOfShards:      64,                 // 分片数（建议 2 的幂次）
    PrimaryKeyGenerator: sharding.PKSnowflake, // 主键生成策略
}, "orders", "order_items"))                 // 需要分片的表名列表
```

### 支持的主键生成策略

| 策略 | 说明 |
|------|------|
| `sharding.PKSnowflake` | 雪花算法（默认推荐，全局唯一） |
| `sharding.PKPGSequence` | PostgreSQL Sequence |
| `sharding.PKCustom` | 自定义，需实现 `PrimaryKeyGeneratorFn` |

---

## 2. 分片算法

### 2.1 内置取模分片

默认使用 `user_id % NumberOfShards` 确定分片编号：

```
user_id=100, NumberOfShards=64 → 100 % 64 = 36 → 表名: orders_36
```

### 2.2 自定义分片算法

```go
sharding.Register(sharding.Config{
    ShardingKey:    "tenant_id",
    NumberOfShards: 8,
    ShardingAlgorithm: func(value any) (suffix string, err error) {
        // 按 tenant_id 范围分片
        id := value.(int64)
        switch {
        case id < 1000:
            return "_shard_0", nil
        case id < 5000:
            return "_shard_1", nil
        default:
            return "_shard_2", nil
        }
    },
}, "tenant_data")
```

---

## 3. 分片表名规则

分片后表名格式：`{原表名}_{分片编号}`

```
orders     → orders_00, orders_01, ..., orders_63
user_logs  → user_logs_00, ..., user_logs_63
```

> DDL 需要手动为每个分片建表，建议用脚本批量生成。

```bash
# 批量建表示例（Bash）
for i in $(seq -f "%02g" 0 63); do
  mysql -u root -p mydb -e "CREATE TABLE orders_${i} LIKE orders_template;"
done
```

---

## 4. 双写迁移策略

从单表迁移到分片表的安全步骤：

```
阶段 1：双写（写新旧表，读旧表）
阶段 2：数据迁移（全量 + 增量同步历史数据）
阶段 3：读切换（读新分片表，写仍双写）
阶段 4：停止双写（只写分片表）
阶段 5：下线旧表
```

```go
// 阶段 1：双写示例
func createOrder(ctx context.Context, order *Order) error {
    // 写旧表
    if err := legacyDB.WithContext(ctx).Create(order).Error; err != nil {
        return err
    }
    // 写新分片表（异步，容忍失败）
    go func() {
        if err := shardedDB.WithContext(ctx).Create(order).Error; err != nil {
            log.Warn("sharded write failed", "err", err)
        }
    }()
    return nil
}
```

---

## 5. 查询路由

### 5.1 自动路由（携带分片键）

```go
// ✅ 携带分片键 → 自动路由到对应分片，高效
db.Where("user_id = ? AND status = ?", userID, "paid").Find(&orders)

// ✅ 也支持 First / Create / Update / Delete
db.Where("user_id = ?", userID).Delete(&Order{})
```

### 5.2 广播查询（跨分片，慎用）

```go
// ⚠️ 不含分片键 → 广播到所有分片，性能差，仅用于后台任务
db.Where("status = ?", "pending").Find(&orders)
```

> 广播查询会并行查所有分片并合并结果，`NumberOfShards=64` 时产生 64 次查询。生产环境对响应时间敏感的接口禁止广播查询。

### 5.3 跨分片聚合

```go
// ❌ GORM Sharding 不支持跨分片 COUNT/SUM/GROUP BY
// ✅ 替代方案：应用层聚合
var total int64
for i := 0; i < 64; i++ {
    var cnt int64
    db.Table(fmt.Sprintf("orders_%02d", i)).
        Where("status = ?", "paid").Count(&cnt)
    total += cnt
}
```

---

## 6. 分片键选择原则

| 原则 | 说明 |
|------|------|
| **高基数** | user_id、order_id 等，避免数据倾斜 |
| **查询频率高** | 大多数查询条件都带这个字段 |
| **不可变** | 分片后该字段不能修改，否则需要跨分片迁移数据 |
| **避免时间字段** | 按时间分片会导致热点（最新分片承受所有写入） |
| **避免枚举字段** | status 等低基数字段会导致严重倾斜 |

---

## 7. 常见坑与解决方案

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| `sharding key required` 错误 | 查询/写入未携带分片键 | 检查 WHERE 条件是否包含 ShardingKey |
| 主键冲突 | 多个分片使用自增 ID | 改用雪花算法或 UUID |
| 跨分片 JOIN 报错 | Sharding 插件不支持跨分片 JOIN | 在应用层拆分查询，避免跨分片关联 |
| 事务跨分片失败 | 单个事务只能操作同一分片 | 确保事务内所有操作的分片键值相同 |
| 迁移时数据不一致 | 双写期间旧表写入成功但新表失败 | 增加校验补偿任务定期对账 |
