package dbcore

import (
	"context"
	"fmt"
	"regexp"
	"strings"

	"gorm.io/gorm"
)

// safeOrderField 校验排序字段名，防止 SQL 注入
// 只允许字母、数字、下划线和点号
var safeOrderFieldRe = regexp.MustCompile(`^[a-zA-Z_][a-zA-Z0-9_.]*$`)

// ==================== 全局配置 ====================

// Config BaseModel 全局配置
type Config struct {
	// 多租户配置
	TenantEnabled   bool                             // 是否启用多租户隔离（默认 false）
	TenantField     string                           // 租户字段名（默认 "tenant_id"）
	TenantExtractor func(ctx context.Context) string // 从 context 提取租户 ID
	TenantStrict    bool                             // 严格模式：无租户信息时拒绝查询（默认 true）

	// 查询限制
	MaxListSize    int // List 方法最大返回条数（默认 5000）
	MaxListAllSize int // ListAll 方法最大返回条数（默认 10000）
	MaxInSize      int // IN 子句最大元素数（默认 1000）
	MaxPageSize    int // 分页最大 pageSize（默认 1000）
}

var globalConfig = Config{
	TenantField:    "tenant_id",
	TenantStrict:   true,
	MaxListSize:    5000,
	MaxListAllSize: 10000,
	MaxInSize:      1000,
	MaxPageSize:    1000,
}

// SetConfig 设置全局配置
// 在程序初始化时调用，所有 BaseModel 实例共享此配置
func SetConfig(cfg Config) {
	if cfg.TenantField == "" {
		cfg.TenantField = "tenant_id"
	}
	if cfg.MaxListSize <= 0 {
		cfg.MaxListSize = 5000
	}
	if cfg.MaxListAllSize <= 0 {
		cfg.MaxListAllSize = 10000
	}
	if cfg.MaxInSize <= 0 {
		cfg.MaxInSize = 1000
	}
	if cfg.MaxPageSize <= 0 {
		cfg.MaxPageSize = 1000
	}
	globalConfig = cfg
}

// GetConfig 获取当前全局配置
func GetConfig() Config {
	return globalConfig
}

// IBaseModel 通用数据库操作接口
type IBaseModel[T any] interface {
	// ==================== 插入操作 ====================
	Insert(ctx context.Context, v *T) error
	InsertBatch(ctx context.Context, v []*T, batchSize int) error

	// ==================== 更新操作 ====================
	Update(ctx context.Context, id string, v map[string]interface{}) error
	UpdateBy(ctx context.Context, v map[string]interface{}, query string, args ...interface{}) error
	Save(ctx context.Context, v *T) error

	// ==================== 删除操作 ====================
	Delete(ctx context.Context, id string) error
	DeleteByIds(ctx context.Context, ids []string) error
	DeleteBy(ctx context.Context, query string, args ...interface{}) error

	// ==================== 查询单条 ====================
	Find(ctx context.Context, id string) (*T, error)
	First(ctx context.Context, query string, args ...interface{}) (*T, error)

	// ==================== 查询列表 ====================
	ListByIds(ctx context.Context, ids []string, orders ...Order) ([]*T, error)
	List(ctx context.Context, query string, orders []Order, args ...interface{}) ([]*T, error)
	ListAll(ctx context.Context, orders ...Order) ([]*T, error)

	// ==================== 分页查询 ====================
	Page(ctx context.Context, page, pageSize int, query string, orders []Order, args ...interface{}) ([]*T, int64, error)

	// PageAfter 游标分页（大数据量推荐，避免 OFFSET 性能退化）
	// afterID 为上一页最后一条记录的 ID，首页传空字符串
	PageAfter(ctx context.Context, afterID string, pageSize int, query string, orders []Order, args ...interface{}) ([]*T, error)

	// ==================== 统计操作 ====================
	Exist(ctx context.Context, query string, args ...interface{}) (bool, error)
	Count(ctx context.Context, query string, args ...interface{}) (int64, error)
}

// BaseModel 通用数据库操作基础模型（泛型）
// 使用方式：嵌入到具体 Model 结构体中
//
//	type UserModel struct {
//	    dbcore.BaseModel[User]
//	}
type BaseModel[T any] struct {
	DB *gorm.DB
}

// Order 排序条件
type Order struct {
	Field string // 排序字段，对应数据库列名
	Desc  bool   // true=降序(DESC)，false=升序(ASC)
}

func (o Order) String() string {
	field := strings.TrimSpace(o.Field)
	if !safeOrderFieldRe.MatchString(field) {
		panic(fmt.Sprintf("dbcore: invalid order field %q (only [a-zA-Z0-9_.] allowed)", field))
	}
	if o.Desc {
		return fmt.Sprintf("%s DESC", field)
	}
	return fmt.Sprintf("%s ASC", field)
}

// GetTxDB 获取数据库连接（优先从 ctx 中取事务连接）
// 当 TenantEnabled=true 时，自动注入租户隔离条件
func (m *BaseModel[T]) GetTxDB(ctx context.Context) *gorm.DB {
	db := GetDB(ctx, m.DB).WithContext(ctx)
	if globalConfig.TenantEnabled && globalConfig.TenantExtractor != nil {
		tenantID := globalConfig.TenantExtractor(ctx)
		if tenantID != "" {
			db = db.Where(safeField(globalConfig.TenantField)+" = ?", tenantID)
		} else if globalConfig.TenantStrict {
			// 严格模式：无租户信息时拒绝所有查询，防止数据越权
			db = db.Where("1 = 0")
		}
	}
	return db
}

// ==================== 插入操作 ====================

func (m *BaseModel[T]) Insert(ctx context.Context, v *T) error {
	autoFillID(v)
	return m.GetTxDB(ctx).Create(v).Error
}

func (m *BaseModel[T]) InsertBatch(ctx context.Context, v []*T, batchSize int) error {
	if len(v) == 0 {
		return nil
	}
	autoFillIDBatch(v)
	if batchSize <= 0 {
		batchSize = 100
	}
	return m.GetTxDB(ctx).CreateInBatches(v, batchSize).Error
}

// ==================== 更新操作 ====================

func (m *BaseModel[T]) Update(ctx context.Context, id string, v map[string]interface{}) error {
	if id == "" {
		return gorm.ErrMissingWhereClause
	}
	return m.GetTxDB(ctx).Model(new(T)).Where("id = ?", id).Updates(v).Error
}

func (m *BaseModel[T]) UpdateBy(ctx context.Context, v map[string]interface{}, query string, args ...interface{}) error {
	if query == "" {
		return gorm.ErrMissingWhereClause
	}
	return m.GetTxDB(ctx).Model(new(T)).Where(query, args...).Updates(v).Error
}

func (m *BaseModel[T]) Save(ctx context.Context, v *T) error {
	return m.GetTxDB(ctx).Save(v).Error
}

// ==================== 删除操作 ====================

func (m *BaseModel[T]) Delete(ctx context.Context, id string) error {
	if id == "" {
		return gorm.ErrMissingWhereClause
	}
	return m.GetTxDB(ctx).Where("id = ?", id).Delete(new(T)).Error
}

func (m *BaseModel[T]) DeleteByIds(ctx context.Context, ids []string) error {
	if len(ids) == 0 {
		return nil
	}
	if len(ids) > globalConfig.MaxInSize {
		return fmt.Errorf("dbcore: DeleteByIds count %d exceeds max %d, use DeleteBy instead", len(ids), globalConfig.MaxInSize)
	}
	return m.GetTxDB(ctx).Where("id IN ?", ids).Delete(new(T)).Error
}

func (m *BaseModel[T]) DeleteBy(ctx context.Context, query string, args ...interface{}) error {
	if query == "" {
		return gorm.ErrMissingWhereClause
	}
	return m.GetTxDB(ctx).Where(query, args...).Delete(new(T)).Error
}

// ==================== 查询单条 ====================

// Find 根据主键 ID 查询单条数据
//
// 修复说明: 原版本使用 First()，会隐式追加 ORDER BY id，按主键查单条无需排序。
// 改用 Take() 语义更准确，且无额外排序开销。
func (m *BaseModel[T]) Find(ctx context.Context, id string) (*T, error) {
	var v T
	if err := m.GetTxDB(ctx).Where("id = ?", id).Take(&v).Error; err != nil {
		return nil, err
	}
	return &v, nil
}

func (m *BaseModel[T]) First(ctx context.Context, query string, args ...interface{}) (*T, error) {
	var v T
	db := m.GetTxDB(ctx)
	if query != "" {
		db = db.Where(query, args...)
	}
	if err := db.First(&v).Error; err != nil {
		return nil, err
	}
	return &v, nil
}

// ==================== 查询列表 ====================

func (m *BaseModel[T]) ListByIds(ctx context.Context, ids []string, orders ...Order) ([]*T, error) {
	if len(ids) == 0 {
		return []*T{}, nil
	}
	if len(ids) > globalConfig.MaxInSize {
		return nil, fmt.Errorf("dbcore: ListByIds count %d exceeds max %d, use List with pagination instead", len(ids), globalConfig.MaxInSize)
	}
	var list []*T
	db := applyOrders(m.GetTxDB(ctx).Where("id IN ?", ids), orders)
	return list, db.Find(&list).Error
}

func (m *BaseModel[T]) List(ctx context.Context, query string, orders []Order, args ...interface{}) ([]*T, error) {
	var list []*T
	db := m.GetTxDB(ctx)
	if query != "" {
		db = db.Where(query, args...)
	}
	db = applyOrders(db, orders)
	return list, db.Limit(globalConfig.MaxListSize).Find(&list).Error
}

// ListAll 查询全部数据
//
// 修复说明: 新增 maxListAllSize 软上限（默认 10000 条），防止意外全表加载导致 OOM。
// 如需处理超大数据集，请使用 GORM 的 FindInBatches 替代。
func (m *BaseModel[T]) ListAll(ctx context.Context, orders ...Order) ([]*T, error) {
	var list []*T
	db := applyOrders(m.GetTxDB(ctx), orders)
	return list, db.Limit(globalConfig.MaxListAllSize).Find(&list).Error
}

// ==================== 分页查询 ====================

// Page OFFSET 分页查询
//
// 修复说明: 原版本对 COUNT 和数据查询各自构建了两套完全相同的 WHERE 条件，
// 现提取公共 baseDB，COUNT 和数据查询复用同一条件，消除重复代码。
//
// 注意: OFFSET 分页在大页码（page > 1000 且 pageSize > 20）时性能退化严重，
// 此场景建议切换到 PageAfter 游标分页。
func (m *BaseModel[T]) Page(ctx context.Context, page, pageSize int, query string, orders []Order, args ...interface{}) ([]*T, int64, error) {
	if page <= 0 {
		page = 1
	}
	if pageSize <= 0 {
		pageSize = 20
	} else if pageSize > globalConfig.MaxPageSize {
		pageSize = globalConfig.MaxPageSize
	}

	var total int64

	// 构建公共 base 查询（COUNT 和数据查询复用）
	baseDB := m.GetTxDB(ctx).Model(new(T))
	if query != "" {
		baseDB = baseDB.Where(query, args...)
	}

	// 第一步：COUNT（复用 baseDB，开新 Session 避免条件累积）
	if err := baseDB.Session(&gorm.Session{}).Count(&total).Error; err != nil {
		return nil, 0, err
	}
	if total == 0 {
		return []*T{}, 0, nil
	}

	// 第二步：查询当前页数据（复用 baseDB，开新 Session）
	var list []*T
	offset := (page - 1) * pageSize
	err := applyOrders(baseDB.Session(&gorm.Session{}), orders).
		Offset(offset).Limit(pageSize).Find(&list).Error

	return list, total, err
}

// PageAfter 游标分页
//
// 相比 OFFSET 分页，游标分页无论翻到第几页性能恒定（走主键索引）。
// 适用场景：无限滚动列表、数据导出、大数据量分页。
//
// 参数:
//   - afterID: 上一页最后一条记录的 ID，首页传空字符串 ""
//   - pageSize: 每页条数
//
// 限制: 默认按 id ASC 游标，如需自定义游标字段请在子类覆写。
func (m *BaseModel[T]) PageAfter(ctx context.Context, afterID string, pageSize int, query string, orders []Order, args ...interface{}) ([]*T, error) {
	if pageSize <= 0 {
		pageSize = 20
	} else if pageSize > globalConfig.MaxPageSize {
		pageSize = globalConfig.MaxPageSize
	}

	var list []*T
	db := m.GetTxDB(ctx).Model(new(T))

	if afterID != "" {
		if query != "" {
			query = "id > ? AND (" + query + ")"
			args = append([]interface{}{afterID}, args...)
		} else {
			query = "id > ?"
			args = []interface{}{afterID}
		}
	}
	if query != "" {
		db = db.Where(query, args...)
	}

	// 游标分页默认 ORDER BY id ASC
	if len(orders) == 0 {
		db = db.Order("id ASC")
	} else {
		db = applyOrders(db, orders)
	}

	return list, db.Limit(pageSize).Find(&list).Error
}

// ==================== 统计操作 ====================

func (m *BaseModel[T]) Exist(ctx context.Context, query string, args ...interface{}) (bool, error) {
	var count int64
	db := m.GetTxDB(ctx).Model(new(T))
	if query != "" {
		db = db.Where(query, args...)
	}
	err := db.Limit(1).Count(&count).Error
	return count > 0, err
}

func (m *BaseModel[T]) Count(ctx context.Context, query string, args ...interface{}) (int64, error) {
	var count int64
	db := m.GetTxDB(ctx).Model(new(T))
	if query != "" {
		db = db.Where(query, args...)
	}
	return count, db.Count(&count).Error
}

// ==================== 辅助函数 ====================

func applyOrders(db *gorm.DB, orders []Order) *gorm.DB {
	for _, order := range orders {
		if field := strings.TrimSpace(order.Field); field != "" {
			db = db.Order(order.String())
		}
	}
	return db
}
