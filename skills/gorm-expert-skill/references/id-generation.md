# 分布式 ID 生成策略

## 1. 策略选型

| 特性 | Snowflake | Leaf-Segment | UUID v4 |
|------|-----------|-------------|---------|
| **ID 格式** | int64（19 位数字） | int64（纯递增数字） | string（36 字符） |
| **有序性** | 趋势递增（同节点内严格递增） | 严格递增 | 完全无序 |
| **外部依赖** | 无 | MySQL（号段分配表） | 无 |
| **吞吐量** | 4096/ms/node | 取决于号段 step（默认 1000） | 无上限 |
| **时钟依赖** | 强依赖（回拨会出问题） | 无 | 无 |
| **K8s 友好** | 一般（需管理 nodeID） | 好（无需 nodeID） | 好 |
| **索引友好** | 好（趋势递增，B-Tree 顺序写入） | 最好（严格递增） | 差（随机写入导致页分裂） |
| **信息泄露** | 可推算时间/节点/QPS | 可推算业务量 | 无 |

### 选型建议

```
单体应用 / 中小规模              → Snowflake（简单，零依赖）
高并发 + 需要严格递增             → Leaf-Segment（性能最好）
多租户 + ID 不可推算             → UUID（安全性好）
已有 ZooKeeper / etcd 基础设施   → Leaf-Snowflake 或自研
```

---

## 2. Snowflake（雪花算法）

### 2.1 结构

```
  1 bit    41 bits          10 bits     12 bits
┌──────┬────────────────┬───────────┬────────────┐
│ sign │  timestamp(ms) │  nodeID   │  sequence  │
│  0   │  69 年范围     │  0-1023   │  0-4095    │
└──────┴────────────────┴───────────┴────────────┘
```

- **时间戳**：相对于 epoch（默认 2020-01-01）的毫秒偏移
- **nodeID**：10 bit = 1024 个节点
- **序列号**：12 bit = 每毫秒 4096 个 ID

### 2.2 使用

```go
// 推荐从环境变量读取 nodeID
nodeID, _ := strconv.ParseInt(os.Getenv("SNOWFLAKE_NODE_ID"), 10, 64)
dbcore.SetIDGenerator(dbcore.NewSnowflakeGenerator(nodeID))
```

### 2.3 时钟回拨问题与保护

时钟回拨是 Snowflake 的头号敌人，常见触发场景：

| 场景 | 回拨幅度 | 频率 |
|------|---------|------|
| NTP 时钟同步 | 通常 ≤ 几百 ms | 每天多次 |
| VM 热迁移 | 可达数秒 | 偶发 |
| 闰秒 | 1s | 极少 |
| 手动修改系统时间 | 任意 | 人为操作 |

dbcore 内置保护机制：

```
回拨 ≤ 5s → 自动等待（sleep 到时钟追上）
回拨 > 5s → panic 拒绝生成（需人工介入）
```

**生产环境额外防护建议**：
- 使用 `chrony` 替代 `ntpd`，配置 `makestep 0.1 -1`（仅在偏差 > 100ms 时跳变）
- K8s 中将 `/etc/localtime` 挂载为 hostPath，确保 Pod 时钟与宿主机一致

### 2.4 K8s 场景 nodeID 管理

```go
// 方式 1：StatefulSet Pod 名称提取序号
// Pod 名: my-app-0, my-app-1, my-app-2
func getNodeIDFromPodName() int64 {
    hostname, _ := os.Hostname()
    parts := strings.Split(hostname, "-")
    id, _ := strconv.ParseInt(parts[len(parts)-1], 10, 64)
    return id
}

// 方式 2：Redis 原子自增分配
func getNodeIDFromRedis(rdb *redis.Client) int64 {
    id, _ := rdb.Incr(context.Background(), "snowflake:node_id").Result()
    return id % 1024 // 取模保证范围
}

// 方式 3：环境变量注入（Deployment）
// K8s Deployment YAML:
//   env:
//     - name: SNOWFLAKE_NODE_ID
//       valueFrom:
//         fieldRef:
//           fieldPath: metadata.annotations['node-id']
```

---

## 3. Leaf-Segment（号段模式）

### 3.1 原理

```
                   ┌──────────────────────────┐
                   │    leaf_alloc 表          │
                   │  biz_tag │ max_id │ step  │
                   │  order   │ 3000   │ 1000  │
                   └──────────┬───────────────┘
                              │ SELECT ... FOR UPDATE
                              │ UPDATE max_id = max_id + step
        ┌─────────────────────┴─────────────────────┐
        │                                           │
   ┌────▼────┐                                 ┌────▼────┐
   │ Buffer A │  ← 当前使用 (2001-3000)       │ Buffer B │  ← 异步预加载 (3001-4000)
   │ cursor=2567                               │ 待切换
   └─────────┘                                 └─────────┘
        │
        │ GenerateID() → 2567, 2568, 2569 ...
        ▼
```

1. 启动时从 DB 分配第一个号段（如 1-1000）
2. 本地从号段内顺序发号（内存操作，极快）
3. 使用量超过 80% 时，**异步**预加载下一段（双 Buffer）
4. 当前段用尽，无缝切换到预加载好的下一段

### 3.2 建表与使用

```sql
-- 号段分配表（NewLeafSegmentGenerator 会自动 AutoMigrate）
CREATE TABLE leaf_alloc (
    biz_tag     VARCHAR(128) NOT NULL COMMENT '业务标识',
    max_id      BIGINT       NOT NULL DEFAULT 0 COMMENT '当前已分配的最大 ID',
    step        INT          NOT NULL DEFAULT 1000 COMMENT '每次分配的号段长度',
    description VARCHAR(256) DEFAULT '' COMMENT '描述',
    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (biz_tag)
) ENGINE=InnoDB;

-- 为每个业务注册号段
INSERT INTO leaf_alloc(biz_tag, max_id, step, description) VALUES
('order', 0, 2000, '订单ID'),
('user',  0, 1000, '用户ID'),
('pay',   0, 5000, '支付流水号');
```

```go
// 使用
dbcore.SetIDGenerator(dbcore.NewLeafSegmentGenerator(db, "order"))

// 多业务场景：每个 Model 使用不同的号段
orderIDGen := dbcore.NewLeafSegmentGenerator(db, "order")
userIDGen  := dbcore.NewLeafSegmentGenerator(db, "user")
```

### 3.3 step 调优

| step 值 | DB 访问频率 | 故障浪费 | 适用场景 |
|---------|-----------|---------|---------|
| 100 | 每 100 个 ID 查一次 DB | 最多浪费 100 个 | 低 QPS 业务 |
| 1000 | 每 1000 个 ID 查一次 | 最多浪费 1000 个 | 大部分场景（默认） |
| 5000 | 每 5000 个 ID 查一次 | 最多浪费 5000 个 | 高 QPS（如支付流水） |
| 50000 | 极少访问 DB | 浪费较大 | 超高并发 + 可接受 ID 不连续 |

```sql
-- 动态调整 step（无需重启应用，下次分配生效）
UPDATE leaf_alloc SET step = 5000 WHERE biz_tag = 'order';
```

### 3.4 高可用

号段模式依赖 MySQL，需保证 DB 高可用：

- **MySQL 主从**：leaf_alloc 表跟随主库，Failover 后继续工作
- **双 Buffer**：即使 DB 短暂不可用（几秒），已预加载的号段仍可发号
- **多机房**：可部署多套 leaf_alloc 表，用不同 biz_tag 前缀区分

```
// 容灾策略
DB 正常 → 双 Buffer 平滑发号
DB 故障 ≤ 号段剩余量消耗时间 → 无感知，继续用 Buffer 发号
DB 故障 > 号段剩余量 → 降级到 Snowflake（需预配置降级生成器）
```

---

## 4. UUID

### 4.1 使用

```go
dbcore.SetIDGenerator(dbcore.NewUUIDGenerator())
```

### 4.2 UUID 作为主键的性能问题

UUID v4 是完全随机的，作为 MySQL InnoDB 主键有严重性能问题：

```
有序 ID（Snowflake/Leaf）       UUID v4（随机）
  顺序写入 B-Tree 叶子页           随机插入导致页分裂
  ┌─┬─┬─┬─┬─┬─┐                  ┌─┬─┬─┬─┬─┬─┐
  │1│2│3│4│5│6│ ← 追加写入        │3│ │1│ │5│2│ ← 随机写入
  └─┴─┴─┴─┴─┴─┘                  └─┴─┴─┴─┴─┴─┘
  写入快，索引紧凑                  页分裂 + 碎片 + 空间浪费
```

**实测对比**（100 万行插入，MySQL 8.0，SSD）：

| 主键类型 | 插入耗时 | 索引大小 | 范围查询 |
|---------|---------|---------|---------|
| BIGINT AUTO_INCREMENT | ~30s | 基准 | 快 |
| Snowflake BIGINT | ~35s | +5% | 快 |
| UUID CHAR(36) | ~120s | +200% | 慢 |
| UUID BINARY(16) | ~80s | +50% | 慢 |

### 4.3 UUID 适用场景

- 数据量小（< 100 万行）
- ID 不能暴露业务信息（如公开 API 的资源标识）
- 需要客户端预生成 ID（离线场景）
- 跨系统数据合并（不同来源不会冲突）

### 4.4 优化建议

如果必须用 UUID，优化方案：

```go
// 方案 1：BINARY(16) 存储替代 CHAR(36)，节省 55% 存储
type User struct {
    ID [16]byte `gorm:"type:binary(16);primaryKey"`
}

// 方案 2：UUID v7（时间有序 UUID，Go 1.22+ 或第三方库）
// UUID v7 前 48 bit 是毫秒时间戳，趋势递增，兼顾有序性和唯一性
// import "github.com/google/uuid"
// uuid.SetRand(nil)  // 使用 crypto/rand
// id := uuid.Must(uuid.NewV7())

// 方案 3：用 Snowflake 主键 + UUID 外部标识
type User struct {
    ID         int64  `gorm:"primaryKey"`           // 内部用，有序
    ExternalID string `gorm:"uniqueIndex;size:36"`  // 外部暴露，不可推测
}
```

---

## 5. 高级：自定义 ID 生成器

实现 `IDGenerator` 接口即可接入 dbcore：

```go
type IDGenerator interface {
    GenerateID() string
}
```

### 示例：Redis 自增 ID

```go
type RedisIDGenerator struct {
    rdb *redis.Client
    key string
}

func NewRedisIDGenerator(rdb *redis.Client, key string) dbcore.IDGenerator {
    return &RedisIDGenerator{rdb: rdb, key: key}
}

func (r *RedisIDGenerator) GenerateID() string {
    id, err := r.rdb.Incr(context.Background(), r.key).Result()
    if err != nil {
        panic(fmt.Sprintf("redis id gen failed: %v", err))
    }
    return fmt.Sprintf("%d", id)
}

// 使用
dbcore.SetIDGenerator(NewRedisIDGenerator(rdb, "id:order"))
```

### 示例：ULID（有序 + 随机）

```go
// ULID = 48 bit 时间戳 + 80 bit 随机数，26 字符，可排序
// go get github.com/oklog/ulid/v2
type ULIDGenerator struct {
    entropy io.Reader
    mu      sync.Mutex
}

func NewULIDGenerator() dbcore.IDGenerator {
    return &ULIDGenerator{
        entropy: ulid.Monotonic(rand.New(rand.NewSource(time.Now().UnixNano())), 0),
    }
}

func (u *ULIDGenerator) GenerateID() string {
    u.mu.Lock()
    defer u.mu.Unlock()
    return ulid.MustNew(ulid.Timestamp(time.Now()), u.entropy).String()
}
```

---

## 6. 多业务场景：每个 Model 使用不同策略

全局 `SetIDGenerator` 只能设置一种策略。多业务场景有两种方案：

### 方案 1：Context 注入（推荐）

```go
// 在 Service 层注入不同的 ID 生成器
func (s *OrderService) Create(ctx context.Context, order *Order) error {
    ctx = dbcore.WithIDGenerator(ctx, s.orderIDGen) // Leaf-Segment
    return s.orderModel.Insert(ctx, order)
}

func (s *UserService) Create(ctx context.Context, user *User) error {
    ctx = dbcore.WithIDGenerator(ctx, s.userIDGen) // Snowflake
    return s.userModel.Insert(ctx, user)
}
```

### 方案 2：覆写 Insert 方法

```go
type OrderModel struct {
    dbcore.BaseModel[Order]
    idGen dbcore.IDGenerator
}

func (m *OrderModel) Insert(ctx context.Context, v *Order) error {
    if v.ID == "" {
        v.ID = m.idGen.GenerateID()
    }
    return m.GetTxDB(ctx).Create(v).Error
}
```

---

## 7. 迁移：从 AUTO_INCREMENT 切换到分布式 ID

### 7.1 迁移步骤

```
1. 新增 string/int64 类型的 ID 字段（保留原 auto_increment ID）
2. 数据迁移：为存量数据生成分布式 ID
3. 切换主键：ALTER TABLE 修改主键为新 ID 字段
4. 修改代码：BaseModel 切换到 SetIDGenerator
5. 删除旧 auto_increment 列（确认无依赖后）
```

### 7.2 注意事项

- **外键引用**：所有引用旧主键的外键字段需同步修改
- **游标分页**：使用分布式 ID 后，`WHERE id > lastID` 仍然有效（Snowflake/Leaf 趋势递增）
- **ID 长度**：Snowflake int64 最大 19 位，前端 JavaScript `Number.MAX_SAFE_INTEGER` = 2^53，超过需要用 string 传输
- **索引重建**：切换主键后需要 `OPTIMIZE TABLE` 或在线 DDL 重建聚簇索引
