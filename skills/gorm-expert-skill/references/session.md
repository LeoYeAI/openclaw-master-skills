# GORM v2 Session 机制

> Session 是 GORM v2 最核心的设计之一，理解它能避免最常见的条件累积和并发安全问题。

---

## 1. Session 是什么

GORM v2 中 `*gorm.DB` 是**有状态对象**，每次链式调用都会在原有 `Statement` 上追加条件。`Session` 用于创建一个新的独立会话，隔离查询状态。

```go
// ❌ 危险：复用同一个 db 实例多次调用，条件会累积
db = db.Where("status = ?", 1)
db.Find(&list1) // WHERE status=1
db.Find(&list2) // WHERE status=1 AND status=1 ← 条件重复叠加！

// ✅ 正确：每次查询前用 Session 开启新状态
base := db.Where("status = ?", 1)
base.Session(&gorm.Session{NewDB: true}).Find(&list1)
base.Session(&gorm.Session{NewDB: true}).Find(&list2)
```

---

## 2. Session 配置项详解

```go
db.Session(&gorm.Session{
    // NewDB: true → 清除所有已有条件，从干净状态开始（最常用）
    NewDB: true,

    // DryRun: true → 只生成 SQL，不执行（用于调试、预检查）
    DryRun: true,

    // PrepareStmt: true → 开启 PreparedStatement 缓存（推荐生产使用）
    PrepareStmt: true,

    // SkipHooks: true → 跳过 BeforeCreate/AfterUpdate 等所有 Hook
    SkipHooks: true,

    // SkipDefaultTransaction: true → 跳过单条写操作的隐式事务
    SkipDefaultTransaction: true,

    // AllowGlobalUpdate: true → 允许无 WHERE 条件的全表更新/删除（危险！）
    AllowGlobalUpdate: false, // 默认 false，禁止

    // FullSaveAssociations: true → Save 时级联保存所有关联
    FullSaveAssociations: false,

    // Context: ctx → 绑定 context（WithContext 内部就是用这个）
    Context: ctx,

    // Logger: customLogger → 覆盖当前查询的 Logger
    Logger: logger.Default.LogMode(logger.Info),
})
```

---

## 3. NewDB vs WithContext 的区别

```go
// WithContext：只绑定 context，保留已有 WHERE 条件
db.Where("status = 1").WithContext(ctx).Find(&list)
// 等价于: db.Where("status=1").Session(&gorm.Session{Context: ctx}).Find(&list)

// NewDB：清除所有条件，相当于从 db 重新开始
db.Where("status = 1").Session(&gorm.Session{NewDB: true}).Find(&list)
// WHERE 条件被清除，等价于: db.WithContext(ctx).Find(&list)
```

---

## 4. goroutine 安全问题

`*gorm.DB` **不是** goroutine 安全的，多个 goroutine 共享同一个带有累积条件的 `*gorm.DB` 实例会导致数据竞争。

```go
// ❌ 危险：多个 goroutine 共享同一个有状态的 db 实例
baseDB := db.Where("tenant_id = ?", tenantID) // 有状态

for i := 0; i < 10; i++ {
    go func(id int) {
        baseDB.Where("id = ?", id).Find(&result) // 数据竞争！
    }(i)
}

// ✅ 正确方案一：每个 goroutine 用 Session 隔离
baseDB := db.Where("tenant_id = ?", tenantID)

for i := 0; i < 10; i++ {
    go func(id int) {
        // Session(NewDB) 创建独立副本，goroutine 安全
        baseDB.Session(&gorm.Session{NewDB: true}).
            Where("id = ?", id).Find(&result)
    }(i)
}

// ✅ 正确方案二：goroutine 内直接用原始 db 构建完整查询
for i := 0; i < 10; i++ {
    go func(id int) {
        db.Where("tenant_id = ? AND id = ?", tenantID, id).Find(&result)
    }(i)
}
```

---

## 5. DryRun 调试复杂 SQL

```go
// 生成 SQL 但不执行，用于调试复杂查询
stmt := db.Session(&gorm.Session{DryRun: true}).
    Where("tenant_id = ?", tenantID).
    Preload("Orders", "status = ?", "paid").
    Find(&users).Statement

fmt.Println(stmt.SQL.String()) // 打印完整 SQL
fmt.Println(stmt.Vars)         // 打印参数列表

// 也可以用 ToSQL 快捷方式（GORM v2.0+）
sql := db.ToSQL(func(tx *gorm.DB) *gorm.DB {
    return tx.Where("id > ?", 100).Limit(10).Find(&users)
})
fmt.Println(sql)
```

---

## 6. PrepareStmt Session 缓存

```go
// 全局开启（推荐）
db, _ := gorm.Open(mysql.Open(dsn), &gorm.Config{
    PrepareStmt: true,
})

// 针对特定高频查询开启
stmtDB := db.Session(&gorm.Session{PrepareStmt: true})
for i := 0; i < 10000; i++ {
    stmtDB.Where("id = ?", i).Find(&user) // SQL 只编译一次，后续复用
}

// 清除 PreparedStatement 缓存（schema 变更后使用）
stmtManger, ok := db.ConnPool.(*gorm.PreparedStmtDB)
if ok {
    stmtManger.Reset() // 清除所有缓存的 PreparedStatement
}
```

---

## 7. 在 BaseModel 中正确使用 Session

```go
// GetDB 函数（transaction.go 中）用 NewDB Session 是正确的
func GetDB(ctx context.Context, db *gorm.DB) *gorm.DB {
    if tx, ok := ctx.Value(contextTxKey{}).(*gorm.DB); ok {
        return tx // 事务连接不需要 NewDB，直接复用
    }
    // 非事务：NewDB 保证每次查询状态干净
    return db.Session(&gorm.Session{NewDB: true})
}

// Page 中 COUNT 和 Find 复用 baseDB 时，应 Session 隔离
baseDB := db.Where(query, args...)
baseDB.Session(&gorm.Session{}).Count(&total)   // 独立 session
baseDB.Session(&gorm.Session{}).Find(&list)     // 独立 session
// 不能直接: baseDB.Count(&total); baseDB.Find(&list) ← 条件累积
```

---

## 8. 常见 Session 陷阱汇总

| 陷阱 | 现象 | 解决方案 |
|------|------|----------|
| 全局 db 链式累积 | WHERE 条件越来越多 | 每次查询用 `Session{NewDB:true}` 或直接从 db 重新构建 |
| goroutine 共享有状态 db | 数据竞争、结果混乱 | goroutine 内用 `Session{NewDB:true}` 创建独立副本 |
| Page 中 Count+Find 条件污染 | Count 的 GROUP BY 影响 Find | 每次用 `Session{}` 开新 session |
| PrepareStmt schema 变更后报错 | 旧 SQL 缓存与新 schema 不匹配 | `stmtManager.Reset()` 清除缓存 |
| DryRun 全局开启 | 所有写操作静默失效 | DryRun 只在调试时用，或用 `ToSQL` 替代 |
