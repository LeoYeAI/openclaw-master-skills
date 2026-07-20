---
name: gorm-expert
description: >
  GORM v2 最佳实践与性能优化。适用于：代码审查、慢查询优化、N+1、连接池、
  事务管理、分库分表、Prometheus/OTel监控、Session安全、Clause/Upsert、
  缓存集成、BaseModel脚手架、SQL→struct生成、多租户隔离。
  触发词：GORM、数据库慢、加索引、写struct、分库分表、Preload、FOR UPDATE、
  Session累积、goroutine db、缓存、多租户、迁移。
---

# GORM 使用与性能优化 Skill

## 脚本工具（优先用脚本，减少 token 消耗）

> 用户提供代码/SQL/参数时，**先跑脚本**，只输出脚本结果 + 针对性说明。
> 所有脚本仅依赖 Python 3.8+，不调用任何外部 API 或凭证。

| 场景 | 脚本 | 用法示例 |
|------|------|---------|
| Go 代码审查 | `scripts/analyze_gorm.py` | `python3 scripts/analyze_gorm.py - <<< "代码"`（R1–R27；CI 用 `--format json`） |
| CREATE TABLE → struct | `scripts/gen_model.py` | `echo "CREATE TABLE..." \| python3 scripts/gen_model.py -`（PG 加 `--dialect pg`） |
| 连接池计算 | `scripts/pool_advisor.py` | `python3 scripts/pool_advisor.py --qps 500 --avg-latency-ms 20 --app-instances 4` |
| SQL 性能分析 | `scripts/query_explain.py` | `python3 scripts/query_explain.py "SELECT * FROM ..."` |
| 迁移 SQL 生成 | `scripts/migration_gen.py` | `python3 scripts/migration_gen.py old.go new.go --table users` |
| Scope 生成 | `scripts/scope_gen.py` | `python3 scripts/scope_gen.py model.go --tenant --paginate` |
| Benchmark 模板 | `scripts/bench_template.py` | 默认 stdout；写文件加 `--output bench_test.go` |
| 项目初始化 | `scripts/init_project.py` | 先 `--dry-run` 预览，再 `--output ./internal/dbcore` 写入 |

---

## 核心原则

1. **禁止物理外键，必须使用逻辑外键** — 所有关联字段只建索引，不建 FK CONSTRAINT；`gorm.Config` 必须设置 `DisableForeignKeyConstraintWhenMigrating: true`；若已有 `foreignKey` tag 必须加 `constraint:false`
2. **先测量，再优化** — `db.Debug()` 或自定义 Logger 定位慢 SQL
3. **最小数据传输** — 只 Select 需要的字段，只查需要的行
4. **减少 Round-trip** — 批量操作、Preload vs 懒加载权衡
5. **连接复用** — 正确配置连接池，避免频繁开关连接

---

## 1. 初始化与连接池

```go
db, _ := gorm.Open(mysql.Open(dsn), &gorm.Config{
    SkipDefaultTransaction:                   true,  // 写性能 +30%
    PrepareStmt:                              true,  // SQL 编译缓存
    DisableForeignKeyConstraintWhenMigrating: true,  // 禁物理 FK
    Logger: logger.New(writer, logger.Config{
        SlowThreshold: 200 * time.Millisecond,
        LogLevel:      logger.Warn,
    }),
})
sqlDB, _ := db.DB()
sqlDB.SetMaxOpenConns(100)
sqlDB.SetMaxIdleConns(20)            // MaxOpen 的 20%
sqlDB.SetConnMaxLifetime(time.Hour)
sqlDB.SetConnMaxIdleTime(10 * time.Minute)
```

> 连接池参数建议：`python3 scripts/pool_advisor.py --qps 500 --avg-latency-ms 20`

**ID 生成策略**（使用 dbcore 脚手架时配置）：

```go
// Snowflake（默认，零依赖）
dbcore.SetIDGenerator(dbcore.NewSnowflakeGenerator(nodeID))
// Leaf-Segment（高并发推荐，严格递增，需 MySQL 号段表）
dbcore.SetIDGenerator(dbcore.NewLeafSegmentGenerator(db, "order"))
// UUID（无需协调，不可排序）
dbcore.SetIDGenerator(dbcore.NewUUIDGenerator())
```

> 策略选型、时钟回拨保护、K8s nodeID 管理详见 `references/id-generation.md`

**多租户配置**（按需开启，默认关闭）：

```go
dbcore.SetConfig(dbcore.Config{
    TenantEnabled: true,            // 开启多租户隔离
    TenantField:   "tenant_id",     // 租户字段名
    TenantStrict:  true,            // 严格模式：无租户时拒绝查询
    TenantExtractor: func(ctx context.Context) string {
        if tid, ok := ctx.Value("tenant_id").(string); ok { return tid }
        return ""
    },
})
// 开启后所有 BaseModel CRUD 自动注入 tenant_id 条件，无需手动拼接
// 不需要多租户时，不调用 SetConfig 即可（TenantEnabled 默认 false）
```

**脚手架初始化**：

```bash
python3 scripts/init_project.py --output ./internal/dbcore          # 写入
python3 scripts/init_project.py --output ./internal/dbcore --dry-run # 仅预览
python3 scripts/init_project.py --output ./internal/dbcore --example # 含示例
```

---

## 2. 查询优化

### 2.1 只查需要的字段

```go
// ❌ SELECT *
db.Find(&users)
// ✅ SELECT id, name, email
db.Select("id", "name", "email").Find(&users)
// ✅ 投影到小 struct
db.Model(&User{}).Select("id", "name").Scan(&dtos)
```

### 2.2 避免 N+1 查询

```go
// ❌ N+1：循环内查 DB
for _, u := range users { db.Where("user_id=?", u.ID).Find(&u.Orders) }
// ✅ Preload：两次查询
db.Preload("Orders").Find(&users)
// ✅ Joins：一次 JOIN，按关联字段过滤
db.Joins("JOIN orders ON orders.user_id=users.id AND orders.status=?","paid").Find(&users)
// ✅ 带条件 Preload
db.Preload("Orders", "status=?", "paid").Preload("Orders.Items").Find(&users)
```

> Preload vs Joins 选型详见 `references/association.md`

### 2.3 分批处理大数据集

```go
// ✅ FindInBatches：每批 500 条
db.Model(&User{}).FindInBatches(&batch, 500, func(tx *gorm.DB, n int) error {
    process(batch); return nil
})
// ✅ 游标分页（大表推荐，避免 OFFSET 退化）
var lastID uint
for {
    var users []User
    db.Where("id > ?", lastID).Order("id").Limit(500).Find(&users)
    if len(users) == 0 { break }
    lastID = users[len(users)-1].ID
}
```

### 2.4 聚合与子查询

```go
// 分组统计
db.Model(&Order{}).Select("user_id, SUM(amount) as total").
    Group("user_id").Having("SUM(amount) > ?", 1000).Scan(&results)
// 去重
db.Distinct("status").Model(&Order{}).Pluck("status", &statuses)
// 子查询
subQuery := db.Model(&Order{}).Select("user_id").Where("amount > ?", 1000)
db.Where("id IN (?)", subQuery).Find(&users)
```

### 2.5 流式读取与索引提示

```go
// 流式读取（超大数据集，逐行处理）
rows, _ := db.Model(&User{}).Where("status = ?", "active").Rows()
defer rows.Close()
for rows.Next() { var u User; db.ScanRows(rows, &u); process(u) }

// 索引提示
db.Clauses(hints.UseIndex("idx_user_name")).Find(&users)
db.Clauses(hints.ForceIndex("idx_created_at").ForOrderBy()).Find(&orders)
```

---

## 3. 写操作优化

### 3.1 批量插入

```go
// ❌ 逐条 INSERT（N 次 Round-trip）
for _, u := range users { db.Create(&u) }
// ✅ 批量插入
db.CreateInBatches(&users, 200)
```

### 3.2 按需更新，不更新零值

```go
// ❌ struct Updates 忽略零值（int=0, bool=false）
db.Model(&user).Updates(User{Name: "new", Age: 0}) // Age=0 被忽略！
// ✅ map 明确指定字段
db.Model(&user).Updates(map[string]any{"name": "new", "age": 0})
// ✅ Select 限制 / Omit 排除
db.Model(&user).Select("name", "email").Updates(&user)
db.Model(&user).Omit("password").Updates(&user)
```

### 3.3 检查 RowsAffected

```go
result := db.Model(&User{}).Where("id = ?", id).Update("status", "banned")
if result.Error != nil { return result.Error }
if result.RowsAffected == 0 { return fmt.Errorf("user %d not found", id) }
```

### 3.4 Upsert

```go
db.Clauses(clause.OnConflict{
    Columns:   []clause.Column{{Name: "email"}},
    DoUpdates: clause.AssignmentColumns([]string{"name", "updated_at"}),
}).Create(&user)
db.Clauses(clause.OnConflict{DoNothing: true}).Create(&users) // 忽略冲突
```

---

## 4. 事务管理

```go
// 标准事务
err := db.Transaction(func(tx *gorm.DB) error {
    if err := tx.Create(&order).Error; err != nil { return err }
    return tx.Model(&stock).Update("qty", gorm.Expr("qty - ?", 1)).Error
})
// 嵌套事务（GORM 自动 SavePoint）
tx.Transaction(func(tx2 *gorm.DB) error { return tx2.Create(&log).Error })
// 悲观锁（FOR UPDATE）
db.Clauses(clause.Locking{Strength: "UPDATE"}).Where("id=?", id).First(&stock)
```

> 乐观锁、CAS、Savepoint、事务陷阱详见 `references/concurrency.md`

---

## 5. 读写分离

```go
db.Use(dbresolver.Register(dbresolver.Config{
    Sources:  []gorm.Dialector{mysql.Open(writeDSN)},
    Replicas: []gorm.Dialector{mysql.Open(read1DSN), mysql.Open(read2DSN)},
    Policy:   dbresolver.RandomPolicy{},
}).SetMaxOpenConns(50).SetMaxIdleConns(10))
// GORM 自动路由：Find/First → Replica；Create/Update/Delete → Source
db.Clauses(dbresolver.Write).Find(&user) // 强制走主库
```

---

## 6. Scopes 与多租户

```go
// 可复用 Scope
func ActiveUser(db *gorm.DB) *gorm.DB { return db.Where("status = ?", "active") }
func AgeOver(age int) func(*gorm.DB) *gorm.DB {
    return func(db *gorm.DB) *gorm.DB { return db.Where("age > ?", age) }
}
db.Scopes(ActiveUser, AgeOver(18)).Find(&users)
```

**多租户隔离**（两种方式，按需选择）：

```go
// 方式 1（推荐）：通过 dbcore.Config 全局开关，BaseModel 自动注入
// 开启：dbcore.SetConfig(dbcore.Config{TenantEnabled: true, ...})
// 关闭：不调用 SetConfig 或 TenantEnabled: false（默认）
// 详见 §1 初始化配置

// 方式 2：手动 Scope（不使用 dbcore 时适用）
func TenantScope(ctx context.Context) func(*gorm.DB) *gorm.DB {
    return func(db *gorm.DB) *gorm.DB {
        if tid, ok := ctx.Value("tenant_id").(string); ok && tid != "" {
            return db.Where("tenant_id = ?", tid)
        }
        return db.Where("1 = 0")
    }
}
```

> 自动生成：`python3 scripts/scope_gen.py model.go --tenant --paginate`
> 完整示例详见 `references/scopes.md`

---

## 7. Model 设计规范

```go
type Order struct {
    gorm.Model
    UserID uint   `gorm:"not null;index"`        // 逻辑外键：只加索引，不建 FK
    Status string `gorm:"type:varchar(20);index"`
    Amount int64  `gorm:"not null;default:0"`
}
```

**逻辑外键规范**（核心原则 #1）：

```go
// ❌ 物理外键：会在 AutoMigrate 时创建 FK CONSTRAINT
User User `gorm:"foreignKey:UserID"`
// ❌ 有 references 但没有 constraint:false
User User `gorm:"foreignKey:UserID;references:ID"`

// ✅ 逻辑外键：显式禁止约束
User User `gorm:"foreignKey:UserID;constraint:false"`
// ✅ 全局禁止（必须写在 gorm.Config 中）
db, _ := gorm.Open(dsn, &gorm.Config{
    DisableForeignKeyConstraintWhenMigrating: true,
})
```

> 物理外键的问题：分库分表不兼容、级联不可控、高并发性能瓶颈、导入迁移困难。
> 详见 `references/base-model-pattern.md`

---

## 8. 调试与性能分析

```go
db.Debug().Find(&users)  // 单次打印 SQL
// ToSQL（不执行，只生成 SQL）
sql := db.ToSQL(func(tx *gorm.DB) *gorm.DB {
    return tx.Where("id > ?", 100).Limit(10).Find(&users)
})
```

> pprof / Benchmark 详见 `references/observability.md`

---

## 9. 常见坑与反模式

| 问题 | 错误写法 | 正确做法 |
|------|----------|----------|
| 忘记传 Context | `db.Find(&u)` | `db.WithContext(ctx).Find(&u)` |
| struct Updates 丢零值 | `db.Updates(User{Age:0})` | `db.Updates(map[string]any{"age":0})` |
| 大 OFFSET 分页 | `db.Offset(100000).Limit(20)` | 游标分页 `WHERE id > lastID` |
| 前导通配 Like | `LIKE '%foo%'` | 前缀匹配 `LIKE 'foo%'` 或全文索引 |
| 事务内耗时操作 | 事务 + HTTP 调用 | HTTP 移到事务外 |
| 未检查 Error | `db.Find(&u); use u` | `if err := db.Find(&u).Error; err != nil` |
| 物理外键 | 未加 `constraint:false` | 加 `constraint:false` 或全局禁止 |
| Save 全量更新 | `db.Save(&user)` | `db.Model(&u).Updates(map[string]any{...})` |
| 忽略 RowsAffected | 不检查影响行数 | `if result.RowsAffected == 0 { ... }` |

---

## 10. 缓存集成（Cache-Aside）

```go
func (r *UserRepo) GetUser(ctx context.Context, id uint) (*User, error) {
    key := fmt.Sprintf("user:%d", id)
    if val, err := r.rdb.Get(ctx, key).Bytes(); err == nil {
        var u User; json.Unmarshal(val, &u); return &u, nil
    }
    // singleflight 防击穿
    res, err, _ := r.group.Do(key, func() (any, error) {
        var u User
        if err := r.db.WithContext(ctx).First(&u, id).Error; err != nil {
            if errors.Is(err, gorm.ErrRecordNotFound) {
                r.rdb.Set(ctx, key, "null", time.Minute) // 防穿透
            }
            return nil, err
        }
        ttl := 30*time.Minute + time.Duration(rand.Int63n(int64(6*time.Minute))) // 抖动防雪崩
        data, _ := json.Marshal(u)
        r.rdb.Set(ctx, key, data, ttl)
        return &u, nil
    })
    // 写操作：更新 DB → 删缓存（不更新缓存）
}
```

> 布隆过滤器防穿透、延迟双删、列表缓存详见 `references/caching.md`

---

## 11. 分库分表（Sharding）

```go
db.Use(sharding.Register(sharding.Config{
    ShardingKey: "user_id", NumberOfShards: 64,
    PrimaryKeyGenerator: sharding.PKSnowflake,
}, "orders"))
db.Where("user_id = ?", userID).Find(&orders) // 携带分片键 → 自动路由
```

> 分片算法、双写迁移、跨分片查询详见 `references/sharding.md`

---

## 12. 监控与可观测性

```go
db.Use(prometheus.New(prometheus.Config{DBName: "myapp", RefreshInterval: 15}))
db.Use(otelgorm.NewPlugin(otelgorm.WithDBName("myapp"))) // OpenTelemetry
```

> Prometheus 告警、Grafana 仪表盘、pprof 详见 `references/observability.md`

---

## 13. GORM v2 核心机制

### 13.1 Session 与 goroutine 安全

```go
// ❌ 条件累积 + goroutine 数据竞争
base := db.Where("tenant_id = ?", tid)
go func() { base.Find(&list1) }() // 危险！
// ✅ Session 隔离
go func() { base.Session(&gorm.Session{NewDB: true}).Find(&list1) }()
```

> Session 配置项、8 种陷阱详见 `references/session.md`

### 13.2 Clause 系统

```go
db.Clauses(clause.Locking{Strength: "UPDATE"}).First(&stock) // FOR UPDATE
db.Clauses(clause.Locking{Strength: "UPDATE", Options: "SKIP LOCKED"}).Find(&tasks) // 任务抢占
db.Clauses(clause.Returning{}).Create(&user) // RETURNING（PostgreSQL）
```

> 完整 Clause 用法、自定义表达式详见 `references/clause.md`

### 13.3 Association 关联操作

```go
db.Preload("Orders", "status = ?", "paid").Find(&users)
db.Preload(clause.Associations).Find(&users)         // 预加载所有关联
db.Omit(clause.Associations).Create(&user)           // 跳过关联写入
db.Model(&user).Association("Orders").Append(&order)  // 添加关联
```

> Preload vs Joins、级联控制、多对多详见 `references/association.md`

### 13.4 Serializer 与自定义类型

```go
type User struct {
    Tags  []string `gorm:"type:json;serializer:json"` // JSON 自动序列化
    Phone string   `gorm:"serializer:encrypted"`      // 自定义加密
}
```

> 完整实现、GormDataType 接口详见 `references/serializer.md`

### 13.5 Error 处理规范（v2）

```go
errors.Is(err, gorm.ErrRecordNotFound) // ✅ v2 正确写法
// ❌ gorm.IsRecordNotFoundError(err) — v1 API，v2 已移除
// 注意：Find 不触发 ErrRecordNotFound；First/Take/Last 触发
```

---

## 14. 进阶参考

详细专题见 `references/` 目录（按需加载，不要全量读入）：

| 文件 | 内容 | 触发时机 |
|------|------|---------|
| `base-model-pattern.md` | BaseModel Bug 修复、游标分页、多租户隔离 | BaseModel、QueryBuilder、分页 |
| `session.md` | Session 机制、goroutine 安全、条件累积 | Session、db 复用、DryRun |
| `clause.md` | Clause 系统（Upsert/FOR UPDATE/RETURNING） | FOR UPDATE、Upsert |
| `association.md` | Preload/Joins、级联控制 | 关联加载、多对多 |
| `serializer.md` | Serializer、自定义类型（枚举/Money/加密） | 字段序列化 |
| `hooks.md` | Hook 执行顺序、性能陷阱 | Hook 使用 |
| `raw-sql.md` | Raw SQL / Scan / Rows | 原生 SQL |
| `indexing.md` | 索引设计、EXPLAIN 验证 | 索引、慢查询 |
| `concurrency.md` | 乐观锁、悲观锁、CAS | 并发冲突、超卖 |
| `testing.md` | sqlmock、SQLite 集成测试 | GORM 测试 |
| `migration.md` | golang-migrate、大表在线 DDL | 数据库迁移 |
| `sharding.md` | 分库分表、分片算法 | 水平拆分 |
| `observability.md` | Prometheus、OTel、Grafana | 监控 |
| `scopes.md` | Scope、分页、多租户 | Scope 用法 |
| `caching.md` | Cache-Aside、防击穿/雪崩/穿透 | Redis 缓存 |
| `soft-delete.md` | 软删除、唯一约束兼容、归档清理 | 软删除 |
| `id-generation.md` | Snowflake/Leaf-Segment/UUID、时钟回拨 | 分布式 ID |
