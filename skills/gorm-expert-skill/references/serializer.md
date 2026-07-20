# GORM v2 Serializer 与自定义数据类型

> GORM v2 提供两种机制将 Go 类型映射到数据库字段：
> Serializer（JSON/Gob/自定义序列化）和 Scanner/Valuer 接口（自定义数据类型）。

---

## 1. 内置 Serializer

### 1.1 JSON Serializer

```go
// gorm:"serializer:json" → 自动 JSON 序列化/反序列化
type User struct {
    gorm.Model
    // ✅ 推荐：直接用 serializer，比 string/datatypes.JSON 更简洁
    Tags      []string          `gorm:"column:tags;type:json;serializer:json"`
    Config    map[string]string `gorm:"column:config;type:json;serializer:json"`
    Address   Address           `gorm:"column:address;type:json;serializer:json"`
}

type Address struct {
    Province string `json:"province"`
    City     string `json:"city"`
    Street   string `json:"street"`
}

// 存储：{"province":"广东","city":"深圳","street":"科技园"}
// 读取：自动反序列化为 Address struct
```

### 1.2 Gob Serializer（二进制，更紧凑）

```go
type Session struct {
    gorm.Model
    // Gob 编码比 JSON 更紧凑，但不可读，适合内部存储
    Data map[string]interface{} `gorm:"column:data;type:blob;serializer:gob"`
}
```

### 1.3 UnixTime Serializer

```go
type Event struct {
    gorm.Model
    // 数据库存 int64 Unix 时间戳，Go 层自动转换为 time.Time
    StartAt time.Time `gorm:"column:start_at;type:bigint;serializer:unixtime"`
    EndAt   time.Time `gorm:"column:end_at;type:bigint;serializer:unixtime"`
}
```

---

## 2. 自定义 Serializer

实现 `schema.SerializerInterface` 接口：

```go
import "gorm.io/gorm/schema"

// 手机号加密 Serializer（存储时加密，读取时解密）
type EncryptedSerializer struct{}

func (EncryptedSerializer) Scan(ctx context.Context, field *schema.Field,
    dst reflect.Value, dbValue interface{}) error {
    // dbValue 是从数据库读到的值（已加密的字符串）
    if encrypted, ok := dbValue.(string); ok {
        decrypted, err := decrypt(encrypted)
        if err != nil {
            return err
        }
        field.ReflectValueOf(ctx, dst).SetString(decrypted)
    }
    return nil
}

func (EncryptedSerializer) Value(ctx context.Context, field *schema.Field,
    dst reflect.Value, fieldValue interface{}) (interface{}, error) {
    // fieldValue 是 Go 层的原始值，加密后存入 DB
    plaintext, ok := fieldValue.(string)
    if !ok || plaintext == "" {
        return plaintext, nil
    }
    return encrypt(plaintext)
}

// 注册到 GORM
func init() {
    schema.RegisterSerializer("encrypted", EncryptedSerializer{})
}

// 使用
type User struct {
    gorm.Model
    Phone  string `gorm:"column:phone;type:varchar(128);serializer:encrypted"`
    IdCard string `gorm:"column:id_card;type:varchar(256);serializer:encrypted"`
}
```

---

## 3. 自定义数据类型（Scanner / Valuer）

实现 `sql.Scanner` 和 `driver.Valuer` 接口，让自定义类型直接映射数据库字段。

### 3.1 枚举类型

```go
// 比 int/string 更类型安全的枚举
type OrderStatus int8

const (
    OrderStatusPending   OrderStatus = 0
    OrderStatusPaid      OrderStatus = 1
    OrderStatusCancelled OrderStatus = 2
)

// driver.Valuer：Go → DB
func (s OrderStatus) Value() (driver.Value, error) {
    return int64(s), nil
}

// sql.Scanner：DB → Go
func (s *OrderStatus) Scan(value interface{}) error {
    if v, ok := value.(int64); ok {
        *s = OrderStatus(v)
        return nil
    }
    return fmt.Errorf("cannot scan %T into OrderStatus", value)
}

// 使用
type Order struct {
    gorm.Model
    Status OrderStatus `gorm:"column:status;type:tinyint;default:0"`
}
// 查询时自动转换为 OrderStatus，无需手动类型断言
```

### 3.2 Money 类型（分→元自动转换）

```go
// 数据库存分（int64），Go 层用浮点表示元
type Money int64 // 单位：分

func (m Money) Yuan() float64 { return float64(m) / 100 }
func (m Money) String() string { return fmt.Sprintf("¥%.2f", m.Yuan()) }

func (m Money) Value() (driver.Value, error) {
    return int64(m), nil
}

func (m *Money) Scan(value interface{}) error {
    if v, ok := value.(int64); ok {
        *m = Money(v)
        return nil
    }
    return fmt.Errorf("cannot scan %T into Money", value)
}

// JSON 序列化为元（方便前端）
func (m Money) MarshalJSON() ([]byte, error) {
    return json.Marshal(m.Yuan())
}

type Order struct {
    gorm.Model
    TotalAmount Money `gorm:"column:total_amount;type:bigint;default:0"`
    // 数据库: 9900  Go: 9900 (分)  JSON: 99.00 (元)
}
```

### 3.3 JSON 字段（替代 datatypes.JSON）

```go
// 比 datatypes.JSON 更类型安全的 JSON 字段
type ExtData struct {
    Source   string `json:"source"`
    Channel  string `json:"channel"`
    Platform string `json:"platform"`
}

func (e ExtData) Value() (driver.Value, error) {
    return json.Marshal(e)
}

func (e *ExtData) Scan(value interface{}) error {
    var data []byte
    switch v := value.(type) {
    case []byte:
        data = v
    case string:
        data = []byte(v)
    default:
        return fmt.Errorf("cannot scan %T into ExtData", value)
    }
    return json.Unmarshal(data, e)
}

type Order struct {
    gorm.Model
    ExtData ExtData `gorm:"column:ext_data;type:json"`
    // 直接访问 order.ExtData.Source，无需 JSON 解析
}
```

---

## 4. GormDataType 接口（自定义列类型）

```go
// 实现 schema.GormDataTypeInterface 让 AutoMigrate 自动使用正确的数据库类型
type JSONArray []string

func (JSONArray) GormDataType() string {
    return "json"
}

func (j JSONArray) Value() (driver.Value, error) {
    return json.Marshal(j)
}

func (j *JSONArray) Scan(value interface{}) error {
    // ...
}

type Tag struct {
    gorm.Model
    Names JSONArray `gorm:"column:names"` // AutoMigrate 自动建 json 类型列
}
```

---

## 5. 选型建议

| 需求 | 推荐方案 |
|------|---------|
| struct/map 存 JSON 列 | `serializer:json` Tag |
| 需要 JSON 字段级查询（JSONQuery） | `datatypes.JSON` |
| 敏感字段加密存储 | 自定义 Serializer |
| 枚举类型映射 | 实现 `Scanner/Valuer` |
| 金额、特殊数值类型 | 实现 `Scanner/Valuer` + `MarshalJSON` |
| 二进制紧凑存储 | `serializer:gob` |
| 时间戳 ↔ time.Time | `serializer:unixtime` 或 `autoCreateTime`/`autoUpdateTime` |
