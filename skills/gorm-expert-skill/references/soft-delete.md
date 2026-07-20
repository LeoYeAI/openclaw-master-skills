# 软删除（Soft Delete）完整指南

## 1. 基本用法

```go
// 使用 gorm.Model 自动获得 DeletedAt 字段
type User struct {
    gorm.Model
    Name string
}

// 或手动声明（更灵活）
type User struct {
    ID        uint           `gorm:"primaryKey"`
    Name      string
    DeletedAt gorm.DeletedAt `gorm:"index"` // 必须加索引
}
```

### 1.1 Delete = 软删除

```go
db.Delete(&user)
// UPDATE users SET deleted_at='2024-01-01 12:00:00' WHERE id = 1

// 硬删除
db.Unscoped().Delete(&user)
// DELETE FROM users WHERE id = 1
```

### 1.2 查询自动排除已删除

```go
db.Find(&users)
// SELECT * FROM users WHERE deleted_at IS NULL

// 包含已删除的数据
db.Unscoped().Find(&users)
// SELECT * FROM users
```

---

## 2. 软删除 + 唯一约束（经典坑）

### 问题
用户被软删除后，用相同 email 注册会报 `Duplicate entry`：

```go
// users 表有 UNIQUE(email)
db.Delete(&user1)                       // 软删除 email=a@test.com
db.Create(&User{Email: "a@test.com"})  // ❌ Duplicate entry!
```

### 解决方案：复合唯一索引包含 deleted_at

```go
type User struct {
    gorm.Model
    Email     string         `gorm:"size:100;not null"`
    DeletedAt gorm.DeletedAt `gorm:"index"`
}

// 手动建复合唯一索引（AutoMigrate 不支持此功能）
// MySQL:
//   CREATE UNIQUE INDEX uk_users_email ON users(email, deleted_at);
//   -- 注意：MySQL InnoDB 中 NULL 值在唯一索引中不冲突，
//   -- 所以 deleted_at IS NULL 的记录可以保持 email 唯一性
//
// PostgreSQL:
//   CREATE UNIQUE INDEX uk_users_email ON users(email) WHERE deleted_at IS NULL;
//   -- 部分索引，更精确
```

### 替代方案：软删除时修改唯一字段

```go
// Hook: 软删除时给唯一字段追加删除标记
func (u *User) BeforeDelete(tx *gorm.DB) error {
    return tx.Model(u).Update("email",
        fmt.Sprintf("%s__deleted_%d", u.Email, time.Now().UnixNano())).Error
}
```

---

## 3. 软删除 + Preload

```go
// 默认: Preload 也会自动排除已软删除的关联
db.Preload("Orders").Find(&users)
// Orders 中已删除的订单不会加载

// 包含已软删除的关联
db.Preload("Orders", func(db *gorm.DB) *gorm.DB {
    return db.Unscoped()
}).Find(&users)
```

---

## 4. 使用 Unix 时间戳作为软删除标记

```go
import "gorm.io/plugin/soft_delete"

type User struct {
    ID        uint
    Name      string
    DeletedAt soft_delete.DeletedAt `gorm:"softDelete:milli"` // 毫秒时间戳
    // DeletedAt soft_delete.DeletedAt                        // 秒时间戳
}
// 未删除: deleted_at = 0
// 已删除: deleted_at = 1704067200000

// 使用 flag 模式（0/1）
type User struct {
    ID      uint
    IsDel   soft_delete.DeletedAt `gorm:"softDelete:flag"`
}
// 未删除: is_del = 0，已删除: is_del = 1
```

### 时间戳模式 vs DeletedAt 的优势

| 特性 | gorm.DeletedAt (NULL) | soft_delete (时间戳/flag) |
|------|----------------------|--------------------------|
| 唯一约束兼容 | MySQL 需要复合索引 | 天然兼容（0 值唯一） |
| 索引效率 | IS NULL 条件 | 等值条件（= 0） |
| 分区表兼容 | 不友好 | 友好 |

---

## 5. 测试中的软删除陷阱

```go
// ❌ 测试中忘记 Unscoped，导致断言失败
db.Delete(&user)
var found User
err := db.First(&found, user.ID).Error
// err = gorm.ErrRecordNotFound（符合预期，但容易迷惑）

// ✅ 测试验证软删除是否生效
db.Delete(&user)
var found User
err := db.Unscoped().First(&found, user.ID).Error
assert.NoError(t, err)
assert.NotNil(t, found.DeletedAt)
```

---

## 6. 性能注意事项

1. **必须给 deleted_at 加索引**：所有查询都会自动加 `WHERE deleted_at IS NULL`
2. **大量软删除数据时**：考虑定期清理（归档到历史表 + 硬删除）
3. **COUNT 查询**：软删除数据越多，`COUNT` 越慢（需扫描更多行判断 IS NULL）

```go
// 定期归档清理（建议通过定时任务执行）
// 1. 将 30 天前软删除的数据归档
db.Unscoped().Where("deleted_at < ?", time.Now().AddDate(0, 0, -30)).
    FindInBatches(&batch, 500, func(tx *gorm.DB, n int) error {
        archiveDB.Create(&batch)  // 写入归档表
        return nil
    })
// 2. 硬删除已归档数据
db.Unscoped().Where("deleted_at < ?", time.Now().AddDate(0, 0, -30)).
    Delete(&User{})
```
