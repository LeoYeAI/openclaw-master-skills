package dbcore

// auto_id.go — 可插拔的分布式 ID 生成器
//
// 支持三种策略（通过 SetIDGenerator 切换）：
//   - Snowflake（默认）：趋势递增，无外部依赖，适合中小规模
//   - Leaf-Segment：号段模式，严格递增，依赖 MySQL，适合高并发
//   - UUID：全局唯一，无外部依赖，不可排序
//
// 使用方式：
//   // 默认使用 Snowflake
//   dbcore.SetIDGenerator(dbcore.NewSnowflakeGenerator(1))
//
//   // 切换为 Leaf-Segment
//   dbcore.SetIDGenerator(dbcore.NewLeafSegmentGenerator(db, "order"))
//
//   // 切换为 UUID
//   dbcore.SetIDGenerator(dbcore.NewUUIDGenerator())
//
// 磁盘写入：无（纯内存操作）

import (
	"context"
	"crypto/rand"
	"fmt"
	"reflect"
	"strconv"
	"sync"
	"sync/atomic"
	"time"

	"gorm.io/gorm"
	"gorm.io/gorm/clause"
)

// ==================== ID 生成器接口 ====================

// IDGenerator 分布式 ID 生成器接口
// 所有实现必须是并发安全的
type IDGenerator interface {
	// GenerateID 生成一个全局唯一 ID（string 格式）
	GenerateID() string
}

// 全局默认生成器（默认 Snowflake nodeID=1）
var globalIDGenerator atomic.Value

func init() {
	// 默认使用内置简易 Snowflake，无需外部依赖
	globalIDGenerator.Store(IDGenerator(newBuiltinSnowflake(1)))
}

// SetIDGenerator 设置全局 ID 生成器
//
// 建议在 main() 或 init() 中调用，应用启动后不要更换。
//
//	// Snowflake（推荐从环境变量读取 nodeID）
//	nodeID, _ := strconv.ParseInt(os.Getenv("SNOWFLAKE_NODE_ID"), 10, 64)
//	dbcore.SetIDGenerator(dbcore.NewSnowflakeGenerator(nodeID))
//
//	// Leaf-Segment（需先建表，见 references/id-generation.md）
//	dbcore.SetIDGenerator(dbcore.NewLeafSegmentGenerator(db, "order"))
//
//	// UUID
//	dbcore.SetIDGenerator(dbcore.NewUUIDGenerator())
func SetIDGenerator(gen IDGenerator) {
	if gen == nil {
		panic("dbcore: IDGenerator must not be nil")
	}
	globalIDGenerator.Store(gen)
}

// GenerateID 使用全局生成器生成 ID
func GenerateID() string {
	return globalIDGenerator.Load().(IDGenerator).GenerateID()
}

// ==================== Snowflake 实现（内置简易版） ====================

// builtinSnowflake 内置简易雪花算法，无需外部依赖
// 结构：1 bit 符号 | 41 bit 时间戳 | 10 bit nodeID | 12 bit 序列号
// 支持：每毫秒每节点 4096 个 ID，时间范围 ~69 年
type builtinSnowflake struct {
	mu        sync.Mutex
	epoch     int64 // 起始时间戳（毫秒），默认 2020-01-01
	nodeID    int64 // 节点 ID（0-1023）
	sequence  int64 // 当前毫秒内序列号
	lastStamp int64 // 上次生成 ID 的时间戳
}

const (
	sfEpoch          = 1577836800000 // 2020-01-01 00:00:00 UTC（毫秒）
	sfNodeBits       = 10
	sfSequenceBits   = 12
	sfMaxNodeID      = (1 << sfNodeBits) - 1   // 1023
	sfMaxSequence    = (1 << sfSequenceBits) - 1 // 4095
	sfNodeShift      = sfSequenceBits
	sfTimestampShift = sfNodeBits + sfSequenceBits
)

func newBuiltinSnowflake(nodeID int64) *builtinSnowflake {
	if nodeID < 0 || nodeID > sfMaxNodeID {
		panic(fmt.Sprintf("dbcore: snowflake nodeID must be 0-%d, got %d", sfMaxNodeID, nodeID))
	}
	return &builtinSnowflake{
		epoch:  sfEpoch,
		nodeID: nodeID,
	}
}

func (s *builtinSnowflake) GenerateID() string {
	s.mu.Lock()
	defer s.mu.Unlock()

	now := time.Now().UnixMilli()

	// 时钟回拨保护：等待直到时钟追上
	if now < s.lastStamp {
		diff := s.lastStamp - now
		if diff > 5000 { // 回拨超过 5 秒，拒绝生成
			panic(fmt.Sprintf("dbcore: clock moved backwards by %dms, refusing to generate ID", diff))
		}
		// 小幅回拨（≤5s），等待追上
		time.Sleep(time.Duration(diff) * time.Millisecond)
		now = time.Now().UnixMilli()
	}

	if now == s.lastStamp {
		s.sequence = (s.sequence + 1) & sfMaxSequence
		if s.sequence == 0 {
			// 当前毫秒序列号用尽，等待下一毫秒
			for now <= s.lastStamp {
				now = time.Now().UnixMilli()
			}
		}
	} else {
		s.sequence = 0
	}

	s.lastStamp = now

	id := ((now - s.epoch) << sfTimestampShift) |
		(s.nodeID << sfNodeShift) |
		s.sequence

	return strconv.FormatInt(id, 10)
}

// NewSnowflakeGenerator 创建 Snowflake ID 生成器
//
// nodeID 范围 0-1023，多实例部署时必须保证每个实例 nodeID 不同。
// 推荐从环境变量或配置中心读取。
//
// 时钟回拨保护：
//   - ≤5s 回拨：自动等待追上
//   - >5s 回拨：panic（需人工介入）
//
// K8s 场景获取 nodeID 的方式：
//   - StatefulSet: 从 Pod 名称提取序号（my-app-0 → 0）
//   - Deployment: 从环境变量注入，或用 Redis INCR 原子自增分配
func NewSnowflakeGenerator(nodeID int64) IDGenerator {
	return newBuiltinSnowflake(nodeID)
}

// ==================== Leaf-Segment 实现（号段模式） ====================

// LeafSegmentGenerator 美团 Leaf 号段模式 ID 生成器
//
// 原理：从 DB 预分配一个号段（如 1-1000），本地发号用完再取下一段。
// 双 Buffer 异步预加载，避免号段切换时的 RT 毛刺。
//
// 需要的表结构（自动创建）：
//
//	CREATE TABLE leaf_alloc (
//	    biz_tag     VARCHAR(128) NOT NULL COMMENT '业务标识',
//	    max_id      BIGINT       NOT NULL DEFAULT 1 COMMENT '当前已分配的最大 ID',
//	    step        INT          NOT NULL DEFAULT 1000 COMMENT '每次分配的号段长度',
//	    description VARCHAR(256) DEFAULT '' COMMENT '描述',
//	    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
//	    PRIMARY KEY (biz_tag)
//	) ENGINE=InnoDB;
//
//	INSERT INTO leaf_alloc(biz_tag, max_id, step, description)
//	VALUES ('order', 1, 1000, '订单ID');
type LeafSegmentGenerator struct {
	db     *gorm.DB
	bizTag string

	mu      sync.Mutex
	current *segment // 当前使用的号段
	next    *segment // 预加载的下一个号段
	loading int32    // 是否正在加载下一段（CAS 标志）
}

// segment 号段
type segment struct {
	cursor int64 // 当前游标（下一个要发出的 ID）
	maxID  int64 // 号段上限（cursor > maxID 时号段用完）
	step   int64 // 本号段的 step（从 DB 读取，用于计算使用率）
}

// LeafAlloc 号段分配表 ORM 模型
type LeafAlloc struct {
	BizTag      string    `gorm:"column:biz_tag;primaryKey;size:128"`
	MaxID       int64     `gorm:"column:max_id;not null;default:1"`
	Step        int       `gorm:"column:step;not null;default:1000"`
	Description string    `gorm:"column:description;size:256"`
	UpdatedAt   time.Time `gorm:"column:updated_at;autoUpdateTime"`
}

func (LeafAlloc) TableName() string { return "leaf_alloc" }

// NewLeafSegmentGenerator 创建 Leaf 号段模式 ID 生成器
//
// 参数：
//   - db: GORM 数据库连接（会自动建表）
//   - bizTag: 业务标识（如 "order"、"user"），不同业务使用独立号段
//
// 可选配置：
//   - 默认 step=1000，可通过修改 leaf_alloc 表的 step 字段调整
//   - step 越大，DB 访问频率越低，但故障时浪费的 ID 越多
func NewLeafSegmentGenerator(db *gorm.DB, bizTag string) IDGenerator {
	gen := &LeafSegmentGenerator{
		db:     db,
		bizTag: bizTag,
	}
	// 自动建表
	if err := db.AutoMigrate(&LeafAlloc{}); err != nil {
		panic(fmt.Sprintf("dbcore: leaf_alloc table migrate failed: %v", err))
	}
	// 确保 bizTag 记录存在
	db.Where("biz_tag = ?", bizTag).FirstOrCreate(&LeafAlloc{
		BizTag: bizTag,
		MaxID:  0,
		Step:   1000,
	})
	// 预加载第一个号段
	seg, err := gen.allocSegment()
	if err != nil {
		panic(fmt.Sprintf("dbcore: leaf first segment alloc failed: %v", err))
	}
	gen.current = seg
	return gen
}

// allocSegment 从 DB 分配一个新号段（事务安全）
func (g *LeafSegmentGenerator) allocSegment() (*segment, error) {
	var seg *segment
	err := g.db.Transaction(func(tx *gorm.DB) error {
		var alloc LeafAlloc
		// SELECT ... FOR UPDATE（行锁，使用 GORM v2 Clause API）
		if err := tx.Clauses(clause.Locking{Strength: "UPDATE"}).
			Where("biz_tag = ?", g.bizTag).First(&alloc).Error; err != nil {
			return fmt.Errorf("leaf_alloc record not found for biz_tag=%s: %w", g.bizTag, err)
		}
		// 更新 max_id
		newMaxID := alloc.MaxID + int64(alloc.Step)
		if err := tx.Model(&alloc).Update("max_id", newMaxID).Error; err != nil {
			return err
		}
		seg = &segment{
			cursor: alloc.MaxID + 1,
			maxID:  newMaxID,
			step:   int64(alloc.Step), // 使用 DB 中实际的 step
		}
		return nil
	})
	return seg, err
}

// asyncLoadNext 异步加载下一个号段（双 Buffer）
func (g *LeafSegmentGenerator) asyncLoadNext() {
	if !atomic.CompareAndSwapInt32(&g.loading, 0, 1) {
		return // 已有加载任务在执行
	}
	go func() {
		defer atomic.StoreInt32(&g.loading, 0)
		seg, err := g.allocSegment()
		if err != nil {
			return // 加载失败，下次发号时重试
		}
		g.mu.Lock()
		g.next = seg
		g.mu.Unlock()
	}()
}

func (g *LeafSegmentGenerator) GenerateID() string {
	g.mu.Lock()
	defer g.mu.Unlock()

	// 当前号段还有余量
	if g.current.cursor <= g.current.maxID {
		id := g.current.cursor
		g.current.cursor++

		// 使用量超过 80% 时，异步预加载下一段
		// 使用号段自身的 step 计算，确保与 DB 配置一致
		segStart := g.current.maxID - g.current.step + 1
		used := float64(id-segStart+1) / float64(g.current.step)
		if used > 0.8 && g.next == nil {
			g.asyncLoadNext()
		}
		return strconv.FormatInt(id, 10)
	}

	// 当前号段用尽，切换到下一段
	if g.next != nil {
		g.current = g.next
		g.next = nil
		id := g.current.cursor
		g.current.cursor++
		return strconv.FormatInt(id, 10)
	}

	// 下一段也没准备好（极端情况），同步分配
	seg, err := g.allocSegment()
	if err != nil {
		panic(fmt.Sprintf("dbcore: leaf segment alloc failed: %v", err))
	}
	g.current = seg
	id := g.current.cursor
	g.current.cursor++
	return strconv.FormatInt(id, 10)
}

// ==================== UUID 实现 ====================

// uuidGenerator 基于 crypto/rand 的 UUID v4 生成器
// 无外部依赖，无需协调，但不可排序、较长（36 字符）
type uuidGenerator struct{}

// NewUUIDGenerator 创建 UUID v4 ID 生成器
//
// 特点：
//   - 使用 crypto/rand 生成，密码学安全
//   - 全局唯一，碰撞概率极低（2^122 空间）
//   - 不可排序，不适合需要趋势递增的场景
//   - 36 字符长度，占用存储空间较大
//   - 作为主键时 B-Tree 索引分裂严重，写入性能差
//
// 适用场景：对排序无要求、数据量不大、不想引入外部依赖
func NewUUIDGenerator() IDGenerator {
	return &uuidGenerator{}
}

func (u *uuidGenerator) GenerateID() string {
	var uuid [16]byte
	if _, err := rand.Read(uuid[:]); err != nil {
		panic(fmt.Sprintf("dbcore: crypto/rand.Read failed: %v", err))
	}
	uuid[6] = (uuid[6] & 0x0f) | 0x40 // version 4
	uuid[8] = (uuid[8] & 0x3f) | 0x80 // variant 10
	return fmt.Sprintf("%08x-%04x-%04x-%04x-%012x",
		uuid[0:4], uuid[4:6], uuid[6:8], uuid[8:10], uuid[10:16])
}

// ==================== 自动填充 ====================

// autoFillID 用反射检查 v 的 ID 字段，若为空则自动填充
// 支持 string 和 int64/uint64 类型的 ID 字段
func autoFillID(v any) {
	if v == nil {
		return
	}
	rv := reflect.ValueOf(v)
	if rv.Kind() == reflect.Ptr {
		rv = rv.Elem()
	}
	if rv.Kind() != reflect.Struct {
		return
	}
	idField := rv.FieldByName("ID")
	if !idField.IsValid() || !idField.CanSet() {
		return
	}

	switch idField.Kind() {
	case reflect.String:
		if idField.String() == "" {
			idField.SetString(GenerateID())
		}
	case reflect.Int64:
		if idField.Int() == 0 {
			id := GenerateID()
			if n, err := strconv.ParseInt(id, 10, 64); err == nil {
				idField.SetInt(n)
			}
		}
	case reflect.Uint64:
		if idField.Uint() == 0 {
			id := GenerateID()
			if n, err := strconv.ParseUint(id, 10, 64); err == nil {
				idField.SetUint(n)
			}
		}
	}
}

// autoFillIDBatch 批量填充 ID
func autoFillIDBatch[T any](v []*T) {
	for _, item := range v {
		autoFillID(item)
	}
}

// ==================== 工具函数 ====================

// ctxIDGenKey context 级别 ID 生成器的键
type ctxIDGenKey struct{}

// WithIDGenerator 将 ID 生成器注入 context
// 用于测试或多租户场景下使用不同的 ID 策略
func WithIDGenerator(ctx context.Context, gen IDGenerator) context.Context {
	return context.WithValue(ctx, ctxIDGenKey{}, gen)
}

// IDGeneratorFromContext 从 context 获取 ID 生成器，不存在时返回全局生成器
func IDGeneratorFromContext(ctx context.Context) IDGenerator {
	if gen, ok := ctx.Value(ctxIDGenKey{}).(IDGenerator); ok {
		return gen
	}
	return globalIDGenerator.Load().(IDGenerator)
}
