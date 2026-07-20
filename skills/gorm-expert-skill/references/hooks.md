# GORM Hooks

> Hook 在 GORM 操作的特定生命周期节点自动执行，定义为 Model 的方法。

---

## 1. Hook 执行顺序

```
Create: BeforeSave → BeforeCreate → [INSERT] → AfterCreate → AfterSave
Update: BeforeSave → BeforeUpdate → [UPDATE] → AfterUpdate → AfterSave
Delete: BeforeDelete → [DELETE/soft] → AfterDelete
Query:  AfterFind
```

---

## 2. 常用 Hook 示例

```go
type User struct {
    gorm.Model
    Name     string
    Password string
    Email    string
}

// BeforeCreate：写入前自动加密密码
func (u *User) BeforeCreate(tx *gorm.DB) error {
    hashed, err := bcrypt.GenerateFromPassword([]byte(u.Password), bcrypt.DefaultCost)
    if err != nil {
        return err
    }
    u.Password = string(hashed)
    return nil
}

// BeforeUpdate：更新前校验
func (u *User) BeforeUpdate(tx *gorm.DB) error {
    if u.Name == "" {
        return errors.New("name cannot be empty")
    }
    return nil
}

// AfterCreate：写入后发送欢迎邮件（注意：不要在 Hook 内做耗时 IO）
func (u *User) AfterCreate(tx *gorm.DB) error {
    // ✅ 异步发送，不阻塞事务
    go sendWelcomeEmail(u.Email)
    return nil
}

// AfterFind：查询后填充计算字段
func (u *User) AfterFind(tx *gorm.DB) error {
    u.DisplayName = fmt.Sprintf("%s (%s)", u.Name, u.Email)
    return nil
}
```

---

## 3. Hook 内访问 DB（正确方式）

```go
// ✅ 用传入的 tx（同一事务内）
func (o *Order) AfterCreate(tx *gorm.DB) error {
    return tx.Model(&Stock{}).
        Where("product_id = ?", o.ProductID).
        Update("qty", gorm.Expr("qty - ?", o.Qty)).Error
}

// ❌ 错误：用全局 db，不在同一事务
func (o *Order) AfterCreate(tx *gorm.DB) error {
    return globalDB.Model(&Stock{})... // 事务外操作！
}
```

---

## 4. ⚠️ Hook 性能陷阱

| 陷阱 | 说明 | 解决方案 |
|------|------|----------|
| Hook 内触发 N+1 | AfterFind 对每条记录做 DB 查询 | 改用 Preload 或 Joins |
| Hook 内同步 IO | AfterCreate 内发邮件/HTTP | 改为 goroutine 异步执行 |
| Hook 内长事务 | BeforeCreate 内大量 DB 操作 | 拆分到 Service 层控制事务粒度 |
| Hook 返回 error 中断批量操作 | CreateInBatches 时某条 Hook 失败 | 在 Hook 内做好容错，非致命错误记录日志不返回 error |

---

## 5. 跳过 Hook

```go
// 跳过所有 Hook（批量数据导入场景）
db.Session(&gorm.Session{SkipHooks: true}).CreateInBatches(&users, 500)
```

---

## 6. 全局回调（Callback）vs Hook

Hook 是 Model 方法，只对单个 Model 生效。全局 Callback 对所有 Model 生效：

```go
// 全局：所有 Create 前自动注入 created_by
db.Callback().Create().Before("gorm:create").Register("set_created_by",
    func(db *gorm.DB) {
        if userID, ok := db.Statement.Context.Value("user_id").(uint); ok {
            db.Statement.SetColumn("created_by", userID)
        }
    })
```
