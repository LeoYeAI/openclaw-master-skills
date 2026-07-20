# GORM 单元测试 / 集成测试规范

## 1. sqlmock 单元测试（无需真实 DB）

```bash
go get github.com/DATA-DOG/go-sqlmock
```

### 基础写法

```go
import (
    "testing"
    "github.com/DATA-DOG/go-sqlmock"
    "gorm.io/driver/mysql"
    "gorm.io/gorm"
)

func setupMockDB(t *testing.T) (*gorm.DB, sqlmock.Sqlmock) {
    t.Helper()
    sqlDB, mock, err := sqlmock.New()
    require.NoError(t, err)

    db, err := gorm.Open(mysql.New(mysql.Config{
        Conn: sqlDB,
    }), &gorm.Config{})
    require.NoError(t, err)

    t.Cleanup(func() {
        sqlDB.Close()
        // 验证所有期望都被满足
        require.NoError(t, mock.ExpectationsWereMet())
    })
    return db, mock
}
```

### 测试查询

```go
func TestGetUserByID(t *testing.T) {
    db, mock := setupMockDB(t)

    rows := sqlmock.NewRows([]string{"id", "name", "email"}).
        AddRow(1, "张三", "zhangsan@example.com")

    mock.ExpectQuery(`SELECT \* FROM \`users\` WHERE id = \? .* LIMIT 1`).
        WithArgs(1).
        WillReturnRows(rows)

    user, err := GetUserByID(db, 1)
    assert.NoError(t, err)
    assert.Equal(t, "张三", user.Name)
}
```

### 测试事务

```go
func TestTransfer(t *testing.T) {
    db, mock := setupMockDB(t)

    mock.ExpectBegin()
    mock.ExpectQuery(`SELECT .* FROM \`accounts\` WHERE id = \?.*FOR UPDATE`).
        WithArgs(1).WillReturnRows(sqlmock.NewRows([]string{"id","balance"}).AddRow(1, 1000))
    mock.ExpectQuery(`SELECT .* FROM \`accounts\` WHERE id = \?.*FOR UPDATE`).
        WithArgs(2).WillReturnRows(sqlmock.NewRows([]string{"id","balance"}).AddRow(2, 500))
    mock.ExpectExec(`UPDATE \`accounts\``).WillReturnResult(sqlmock.NewResult(1, 1))
    mock.ExpectExec(`UPDATE \`accounts\``).WillReturnResult(sqlmock.NewResult(1, 1))
    mock.ExpectCommit()

    err := Transfer(db, 1, 2, 100)
    assert.NoError(t, err)
}

// 测试失败路径
func TestTransfer_InsufficientBalance(t *testing.T) {
    db, mock := setupMockDB(t)

    mock.ExpectBegin()
    mock.ExpectQuery(`SELECT .* FROM \`accounts\`.*FOR UPDATE`).
        WithArgs(sqlmock.AnyArg()).
        WillReturnRows(sqlmock.NewRows([]string{"id","balance"}).AddRow(1, 10)) // 余额不足
    mock.ExpectRollback()

    err := Transfer(db, 1, 2, 100)
    assert.ErrorContains(t, err, "insufficient balance")
}
```

---

## 2. 集成测试（SQLite 内存库）

适合不关心 MySQL 方言差异的业务逻辑测试，速度极快。

```bash
go get gorm.io/driver/sqlite
```

```go
func SetupTestDB(t *testing.T) *gorm.DB {
    t.Helper()
    db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{
        Logger: logger.Default.LogMode(logger.Silent),
    })
    require.NoError(t, err)

    // 自动建表
    require.NoError(t, db.AutoMigrate(&User{}, &Order{}))

    t.Cleanup(func() {
        sqlDB, _ := db.DB()
        sqlDB.Close()
    })
    return db
}

func TestCreateOrder(t *testing.T) {
    db := SetupTestDB(t)

    user := User{Name: "测试用户"}
    db.Create(&user)

    order := Order{UserID: user.ID, Amount: 100}
    err := CreateOrder(db, &order)

    assert.NoError(t, err)
    assert.NotZero(t, order.ID)

    // 验证数据库状态
    var count int64
    db.Model(&Order{}).Where("user_id = ?", user.ID).Count(&count)
    assert.Equal(t, int64(1), count)
}
```

---

## 3. 测试隔离（事务回滚模式）

每个测试用例在独立事务中运行，测试结束后回滚，**不污染数据**：

```go
func SetupTestDBWithRollback(t *testing.T, realDB *gorm.DB) *gorm.DB {
    t.Helper()
    tx := realDB.Begin()
    require.NoError(t, tx.Error)

    t.Cleanup(func() {
        tx.Rollback() // 测试结束一律回滚
    })
    return tx
}

// 集成测试套件（共享连接，每个用例独立回滚）
func TestSuite(t *testing.T) {
    db := connectRealTestDB(t) // 连接测试环境 DB

    t.Run("创建订单", func(t *testing.T) {
        txDB := SetupTestDBWithRollback(t, db)
        // 用 txDB 操作，测试后自动回滚
    })

    t.Run("扣减库存", func(t *testing.T) {
        txDB := SetupTestDBWithRollback(t, db)
        // 完全隔离，互不影响
    })
}
```

---

## 4. 常用断言模式

```go
// 验证行数
var count int64
db.Model(&User{}).Count(&count)
assert.Equal(t, int64(1), count)

// 验证软删除
db.Delete(&user)
var found User
result := db.First(&found, user.ID)
assert.ErrorIs(t, result.Error, gorm.ErrRecordNotFound) // 软删除后查不到

// 验证 Unscoped 能查到
db.Unscoped().First(&found, user.ID)
assert.NotNil(t, found.DeletedAt)

// 验证字段值
db.First(&updated, user.ID)
assert.Equal(t, "new_name", updated.Name)
```

---

## 5. 选型建议

| 场景 | 方案 |
|------|------|
| 纯业务逻辑，不含 DB 方言特性 | SQLite 内存库（最快） |
| 需要验证 SQL 精确性 / 错误路径 | sqlmock |
| 需要验证 MySQL 特定行为（JSON、全文索引等） | Docker + testcontainers-go |
| CI 环境集成测试 | 事务回滚模式 + 真实测试库 |

---

## 6. 软删除 + Unique 约束冲突（经典坑）

**问题**：Model 含 `DeletedAt` 时，软删除记录的唯一字段仍占用约束，再次插入相同值会报 `Duplicate entry`。

```go
type User struct {
    gorm.Model
    Email string `gorm:"uniqueIndex"` // ← 坑在这里
}

db.Create(&User{Email: "a@test.com"}) // OK
db.Delete(&User{}, 1)                 // 软删除，email 仍在表中
db.Create(&User{Email: "a@test.com"}) // ❌ Duplicate entry!
```

**解决方案一：唯一索引包含 deleted_at（MySQL 推荐）**

```go
// 用 composite uniqueIndex 包含 deleted_at，NULL 不参与唯一性判断
type User struct {
    gorm.Model
    Email     string         `gorm:"uniqueIndex:idx_email_del"`
    DeletedAt gorm.DeletedAt `gorm:"index;uniqueIndex:idx_email_del"`
}
// 软删除后 deleted_at = timestamp，不与 NULL 冲突，可以再次插入相同 email
```

**解决方案二：使用 deleted_at = 0 代替 NULL（PostgreSQL 兼容）**

```go
import "gorm.io/plugin/soft_delete"

type User struct {
    ID        uint
    Email     string                `gorm:"uniqueIndex:idx_email_del"`
    DeletedAt soft_delete.DeletedAt `gorm:"softDelete:milli;uniqueIndex:idx_email_del"`
    // deleted_at 用毫秒时间戳，0 表示未删除
}
```

**测试中如何覆盖这个场景**：

```go
func TestSoftDeleteUniqueConflict(t *testing.T) {
    db := setupTestDB(t) // SQLite 内存库

    // 插入 → 软删除 → 再插入，期望成功
    u1 := User{Email: "dup@test.com"}
    require.NoError(t, db.Create(&u1).Error)
    require.NoError(t, db.Delete(&u1).Error)

    u2 := User{Email: "dup@test.com"}
    err := db.Create(&u2).Error
    // 如果没有正确配置复合唯一索引，这里会报错
    assert.NoError(t, err, "软删除后应可重新插入相同 email")
}
```
