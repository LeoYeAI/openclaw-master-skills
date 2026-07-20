# GORM v2 Association 关联操作

> GORM v2 的 Association 模式与 v1 差异很大，本文覆盖 v2 的正确用法。

---

## 1. 关联类型定义（v2 规范）

```go
// 禁止物理外键，所有关联字段只建索引（见 base-model-pattern.md §1）
type User struct {
    gorm.Model
    Name    string
    Orders  []Order  `gorm:"foreignKey:UserID;constraint:false"` // 一对多
    Profile *Profile `gorm:"foreignKey:UserID;constraint:false"` // 一对一
    Roles   []Role   `gorm:"many2many:user_roles;constraint:false"` // 多对多
}

type Order struct {
    gorm.Model
    UserID uint   `gorm:"not null;index"` // 逻辑外键：只加索引
    User   User   `gorm:"foreignKey:UserID;constraint:false"`
    Status string
}
```

---

## 2. Preload（预加载，避免 N+1）

```go
// 基础 Preload
db.Preload("Orders").Find(&users)
// SELECT * FROM users; SELECT * FROM orders WHERE user_id IN (1,2,3)

// 带条件的 Preload
db.Preload("Orders", "status = ?", "paid").Find(&users)

// 多级 Preload
db.Preload("Orders.Items").Find(&users)

// Preload 所有关联（v2 新增）
db.Preload(clause.Associations).Find(&users)

// 自定义 Preload 查询
db.Preload("Orders", func(db *gorm.DB) *gorm.DB {
    return db.Order("created_at DESC").Limit(5) // 每个用户只加载最近 5 个订单
}).Find(&users)
```

---

## 3. Joins 预加载（单次 SQL）

```go
// Joins 用 LEFT JOIN，适合需要按关联字段过滤的场景
db.Joins("Profile").Find(&users)
// SELECT users.*, profiles.* FROM users LEFT JOIN profiles ON profiles.user_id = users.id

// 带条件的 Joins
db.Joins("Profile", db.Where(&Profile{Active: true})).Find(&users)

// Joins + 过滤主表
db.Joins("JOIN orders ON orders.user_id = users.id AND orders.status = ?", "paid").
    Find(&users)
```

### Preload vs Joins 选择

| 场景 | 推荐 |
|------|------|
| 只是附带加载关联数据 | `Preload`（两次查询，内存友好） |
| 需要按关联字段过滤主表 | `Joins` |
| 关联数据量大（万级+） | `Preload` + 分页，或手动查询 |
| 多层嵌套关联 | `Preload("A.B.C")` |

---

## 4. Association 模式（操作关联数据）

```go
// 获取关联操作句柄
assoc := db.Model(&user).Association("Orders")

// Append：添加关联（不删除现有，适合多对多 / 一对多）
assoc.Append(&Order{Amount: 100}, &Order{Amount: 200})

// Replace：替换所有关联（删除旧关联，添加新的）
assoc.Replace(&Order{Amount: 300}) // user 只关联这一个 order

// Delete：移除指定关联（多对多时删除中间表记录）
assoc.Delete(&order1, &order2)

// Clear：清除所有关联
assoc.Clear()

// Count：统计关联数量
count := assoc.Count()

// Find：查询关联（带条件）
var paidOrders []Order
assoc.Find(&paidOrders, "status = ?", "paid")

// 错误处理
if err := assoc.Error; err != nil {
    log.Error(err)
}
```

---

## 5. Select + Omit 控制级联写入

```go
// Select：只保存指定的关联（其余关联不处理）
db.Select("Orders").Create(&userWithOrders)
// 只创建 user 和 Orders，忽略 Profile

// Select("*")：保存所有字段和关联
db.Select("*").Create(&user)

// Omit：排除指定关联
db.Omit("Profile").Create(&user)
// 创建 user，跳过 Profile 关联

// Omit(clause.Associations)：完全不处理任何关联（最常用）
db.Omit(clause.Associations).Create(&user)
// 只创建 user 本身，所有关联字段忽略

// 更新时同样适用
db.Session(&gorm.Session{FullSaveAssociations: true}).
    Omit("Orders").Save(&user) // 保存 user 和 Profile，跳过 Orders
```

---

## 6. FullSaveAssociations

```go
// 默认 false：Save 不级联保存关联
db.Save(&user) // 只保存 user 本身

// 开启后：Save 级联保存所有关联（注意性能）
db.Session(&gorm.Session{FullSaveAssociations: true}).Save(&user)
// 保存 user + user.Orders + user.Profile

// ⚠️ 生产环境慎用 FullSaveAssociations：
// 1. 可能触发大量 INSERT/UPDATE
// 2. 关联层级深时难以预测行为
// 推荐改为显式操作关联
```

---

## 7. 多对多关联管理

```go
type User struct {
    gorm.Model
    Roles []Role `gorm:"many2many:user_roles;constraint:false"`
}

type Role struct {
    gorm.Model
    Name string
}

// 添加角色（INSERT INTO user_roles）
db.Model(&user).Association("Roles").Append(&adminRole, &editorRole)

// 替换角色（DELETE 旧的 + INSERT 新的）
db.Model(&user).Association("Roles").Replace(&viewerRole)

// 移除角色（DELETE FROM user_roles WHERE user_id=? AND role_id=?）
db.Model(&user).Association("Roles").Delete(&adminRole)

// 自定义中间表字段
type UserRole struct {
    UserID    uint      `gorm:"primaryKey"`
    RoleID    uint      `gorm:"primaryKey"`
    CreatedAt time.Time // 中间表额外字段
    ExpiresAt time.Time
}
```

---

## 8. 关联数据的软删除处理

```go
// 软删除会自动过滤 deleted_at IS NOT NULL 的关联
// 如需包含软删除的关联数据：
db.Unscoped().Preload("Orders").Find(&users)

// 只查已软删除的关联
db.Preload("Orders", func(db *gorm.DB) *gorm.DB {
    return db.Unscoped().Where("deleted_at IS NOT NULL")
}).Find(&users)
```

---

## 9. 常见坑

| 坑 | 说明 | 解决 |
|----|------|------|
| Preload 忘加条件导致加载全量关联 | `Preload("Orders")` 无限制 | 加 Limit 或在 Preload func 内分页 |
| Association.Append 触发物理 FK 报错 | 有 FK 约束时 Append 可能失败 | 改用逻辑外键（`constraint:false`） |
| Save 意外级联更新 | `FullSaveAssociations` 全局开启 | 只在必要时 Session 级别开启 |
| 多对多 Replace 删除了不该删的记录 | Replace 会清除所有现有关联再重建 | 用 Append + Delete 精确控制 |
| N+1 在 AfterFind Hook 中触发 | Hook 内对每条记录做额外查询 | 改用 Preload 批量加载 |
