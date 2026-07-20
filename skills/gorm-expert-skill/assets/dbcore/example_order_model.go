//go:build ignore
// +build ignore

package example

// ============================================================
// 本文件是 dbcore.BaseModel 的完整使用示例
// 展示从 Model 定义 → 初始化 → Service 层调用的完整链路
//
// 运行前提：
//   1. 已执行 init_project.py 生成 dbcore 包
//   2. 已实现 autoFillID / autoFillIDBatch
//   3. 将本文件的 package 改为实际包名，import 路径对应修改
// ============================================================

import (
	"context"
	"errors"
	"time"

	// 将下面的路径替换为实际模块路径，例如：
	// "github.com/your-org/your-app/internal/dbcore"
	dbcore "your-module/internal/dbcore"

	"gorm.io/datatypes"
	"gorm.io/gorm"
)

// ============================================================
// 1. Model 定义
// ============================================================

// OrderStatus 订单状态枚举
type OrderStatus int

const (
	OrderStatusPending   OrderStatus = 0 // 待确认
	OrderStatusConfirmed OrderStatus = 1 // 已确认
	OrderStatusPickedUp  OrderStatus = 2 // 已取车
	OrderStatusReturned  OrderStatus = 3 // 已还车
	OrderStatusCompleted OrderStatus = 4 // 已完成
	OrderStatusCancelled OrderStatus = 5 // 已取消
)

// PayStatus 支付状态枚举
type PayStatus int

const (
	PayStatusUnpaid    PayStatus = 0 // 未支付
	PayStatusPartial   PayStatus = 1 // 部分支付
	PayStatusPaid      PayStatus = 2 // 已支付
	PayStatusRefunded  PayStatus = 3 // 已退款
)

// Order 订单 Model
//
// 关键设计说明：
//  1. 软删除 + 唯一索引：OrderNo / PlatformOrderNo 的 uniqueIndex 包含 deleted_at，
//     避免软删除后重建相同记录报 Duplicate entry（见 references/base-model-pattern.md §2）
//  2. 禁止物理外键：所有关联字段只建索引，不建 FOREIGN KEY CONSTRAINT
//  3. ExtData 用 datatypes.JSON 替代 string，支持 JSON 字段查询
type Order struct {
	ID         string `json:"id"         gorm:"column:id;primaryKey;type:varchar(32)"`
	TenantID   string `json:"tenantId"   gorm:"column:tenant_id;type:varchar(32);not null;index"`

	// 软删除 + 唯一索引：uniqueIndex 包含 deleted_at，避免重建相同订单号时冲突
	OrderNo         string `json:"orderNo"         gorm:"column:order_no;type:varchar(64);not null;uniqueIndex:idx_order_no_del"`
	PlatformID      string `json:"platformId"      gorm:"column:platform_id;type:varchar(32);not null;index"`
	PlatformOrderNo string `json:"platformOrderNo" gorm:"column:platform_order_no;type:varchar(64);not null;uniqueIndex:idx_platform_order_del"`

	VehicleID   string `json:"vehicleId"   gorm:"column:vehicle_id;type:varchar(32);index"`
	PlateNumber string `json:"plateNumber" gorm:"column:plate_number;type:varchar(20);index"`

	// 客户信息
	CustomerName   string `json:"customerName"   gorm:"column:customer_name;type:varchar(32)"`
	CustomerPhone  string `json:"customerPhone"  gorm:"column:customer_phone;type:varchar(20)"`
	CustomerIdCard string `json:"customerIdCard" gorm:"column:customer_id_card;type:varchar(32)"`

	// 租期信息
	PickupTime       int64  `json:"pickupTime"       gorm:"column:pickup_time;type:bigint;index"`
	ReturnTime       int64  `json:"returnTime"       gorm:"column:return_time;type:bigint;index"`
	ActualPickupTime int64  `json:"actualPickupTime" gorm:"column:actual_pickup_time;type:bigint"`
	ActualReturnTime int64  `json:"actualReturnTime" gorm:"column:actual_return_time;type:bigint"`
	PickupLocation   string `json:"pickupLocation"   gorm:"column:pickup_location;type:varchar(255)"`
	ReturnLocation   string `json:"returnLocation"   gorm:"column:return_location;type:varchar(255)"`
	RentDays         int    `json:"rentDays"         gorm:"column:rent_days;type:int;default:0"`

	// 金额（单位：分）
	TotalAmount        int64 `json:"totalAmount"        gorm:"column:total_amount;type:bigint;default:0"`
	RentAmount         int64 `json:"rentAmount"         gorm:"column:rent_amount;type:bigint;default:0"`
	InsuranceAmount    int64 `json:"insuranceAmount"    gorm:"column:insurance_amount;type:bigint;default:0"`
	ServiceAmount      int64 `json:"serviceAmount"      gorm:"column:service_amount;type:bigint;default:0"`
	DepositAmount      int64 `json:"depositAmount"      gorm:"column:deposit_amount;type:bigint;default:0"`
	PlatformCommission int64 `json:"platformCommission" gorm:"column:platform_commission;type:bigint;default:0"`

	// 状态
	OrderStatus OrderStatus `json:"orderStatus" gorm:"column:order_status;type:int;not null;index;default:0"`
	PayStatus   PayStatus   `json:"payStatus"   gorm:"column:pay_status;type:int;not null;index;default:0"`

	// 扩展字段：datatypes.JSON 自动序列化，支持 JSONQuery
	ExtData    datatypes.JSON `json:"extData"    gorm:"column:ext_data;type:json"`
	Remark     string         `json:"remark"     gorm:"column:remark;type:varchar(500)"`
	SyncStatus int            `json:"syncStatus" gorm:"column:sync_status;type:int;not null;index;default:1"`
	LastSyncAt int64          `json:"lastSyncAt" gorm:"column:last_sync_at;type:bigint;default:0"`

	CreateAt int64 `json:"createAt" gorm:"column:create_at;autoCreateTime"`
	UpdateAt int64 `json:"updateAt" gorm:"column:update_at;autoUpdateTime"`

	// deleted_at 参与复合唯一索引，软删除后不占用唯一约束
	DeletedAt gorm.DeletedAt `json:"deletedAt" gorm:"index;uniqueIndex:idx_order_no_del;uniqueIndex:idx_platform_order_del"`
}

func (Order) TableName() string { return "ota_order" }

// ============================================================
// 2. Model 接口定义
// ============================================================

// IOrderModel 扩展 IBaseModel，补充业务特有查询
//
// 多租户说明：
//   - 若启用多租户（dbcore.SetConfig 中 TenantEnabled=true），BaseModel 的
//     GetTxDB 会自动注入 tenant_id 条件，无需在每个方法中手动拼接。
//   - 若未启用多租户，所有方法按普通单租户模式工作。
type IOrderModel interface {
	dbcore.IBaseModel[Order]

	// FindByPlatformOrderNo 按平台ID + 平台订单号查询（幂等检查用）
	FindByPlatformOrderNo(ctx context.Context, platformID, platformOrderNo string) (*Order, error)
}

// ============================================================
// 3. Model 实现
// ============================================================

type orderModel struct {
	dbcore.BaseModel[Order]
}

// NewOrderModel 创建订单 Model
//
// isMigrate 说明：
//   - 本地开发 / 测试环境传 true，自动建表
//   - 生产环境传 false，使用 golang-migrate 脚本管理迁移
func NewOrderModel(db *gorm.DB, isMigrate bool) IOrderModel {
	if isMigrate {
		// DisableForeignKeyConstraintWhenMigrating：禁止 AutoMigrate 创建物理外键
		migrateDB := db.Session(&gorm.Session{})
		migrateDB.DisableForeignKeyConstraintWhenMigrating = true
		if err := migrateDB.AutoMigrate(&Order{}); err != nil {
			panic(err)
		}
	}
	return &orderModel{
		BaseModel: dbcore.BaseModel[Order]{DB: db},
	}
}

func (m *orderModel) FindByPlatformOrderNo(ctx context.Context, platformID, platformOrderNo string) (*Order, error) {
	return m.First(ctx, "platform_id = ? AND platform_order_no = ?", platformID, platformOrderNo)
}

// 注意：多租户隔离已通过 dbcore.Config 全局配置实现。
// 当 TenantEnabled=true 时，BaseModel.GetTxDB 会自动注入 tenant_id 条件，
// 所有 CRUD 方法（List/Page/Find/Delete 等）均自动隔离，无需手动拼接。
// 若项目不需要多租户，保持 TenantEnabled=false（默认值）即可。

// ============================================================
// 4. Service 层调用示例
// ============================================================

// OrderService 展示如何在 Service 层使用 Model
type OrderService struct {
	orderModel IOrderModel
	tx         dbcore.Transaction
}

func NewOrderService(orderModel IOrderModel, tx dbcore.Transaction) *OrderService {
	return &OrderService{orderModel: orderModel, tx: tx}
}

// CreateOrder 创建订单（幂等）
func (s *OrderService) CreateOrder(ctx context.Context, order *Order) error {
	// 幂等检查：同平台订单号已存在则直接返回
	existing, err := s.orderModel.FindByPlatformOrderNo(ctx, order.PlatformID, order.PlatformOrderNo)
	if err != nil && !errors.Is(err, gorm.ErrRecordNotFound) {
		return err
	}
	if existing != nil {
		return nil // 已存在，幂等返回
	}
	return s.orderModel.Insert(ctx, order)
}

// CompleteOrder 完成订单（事务：更新状态 + 记录实际还车时间）
func (s *OrderService) CompleteOrder(ctx context.Context, orderID string, actualReturnTime time.Time) error {
	return s.tx.ExecTx(ctx, func(ctx context.Context) error {
		// 查询订单（事务内用 tx 自动传递）
		order, err := s.orderModel.Find(ctx, orderID)
		if err != nil {
			return err
		}
		if order.OrderStatus != OrderStatusReturned {
			return errors.New("订单状态不允许完成操作")
		}
		// 更新状态和实际还车时间
		return s.orderModel.Update(ctx, orderID, map[string]interface{}{
			"order_status":       OrderStatusCompleted,
			"actual_return_time": actualReturnTime.Unix(),
		})
	})
}

// ListPendingOrders 查询待确认订单（使用 QueryBuilder 构建复杂条件）
// 注意：多租户隔离由 BaseModel.GetTxDB 自动注入（从 ctx 提取 tenant_id），
// 调用方只需确保 ctx 中携带了租户信息即可。
func (s *OrderService) ListPendingOrders(ctx context.Context, platformID string, startTime, endTime int64) ([]*Order, error) {
	qb := dbcore.NewQueryBuilder().
		EqIfPositive("order_status", int(OrderStatusPending)).
		Eq("platform_id", platformID).
		Between("pickup_time", startTime, endTime)

	// 也可以用 OrGroup 查多个状态
	// qb.OrGroup(
	//     dbcore.NewQueryBuilder().Eq("order_status", int(OrderStatusPending)),
	//     dbcore.NewQueryBuilder().Eq("order_status", int(OrderStatusConfirmed)),
	// )

	query, args := qb.Build()
	return s.orderModel.List(ctx, query,
		[]dbcore.Order{{Field: "pickup_time", Desc: false}},
		args...,
	)
}

// PageOrders 分页查询订单
func (s *OrderService) PageOrders(ctx context.Context, page, pageSize int, orderStatus OrderStatus, keyword string) ([]*Order, int64, error) {
	qb := dbcore.NewQueryBuilder().
		EqIfPositive("order_status", int(orderStatus)).
		Like("customer_name", keyword) // LIKE '%keyword%'，模糊搜索客户姓名

	query, args := qb.Build()
	return s.orderModel.Page(ctx, page, pageSize, query,
		[]dbcore.Order{{Field: "create_at", Desc: true}},
		args...,
	)
}

// BulkSyncOrders 批量同步订单（使用 InsertBatch）
func (s *OrderService) BulkSyncOrders(ctx context.Context, orders []*Order) error {
	if len(orders) == 0 {
		return nil
	}
	return s.orderModel.InsertBatch(ctx, orders, 200) // 每批 200 条
}

// GetOrdersByIDs 按 ID 列表批量查询
func (s *OrderService) GetOrdersByIDs(ctx context.Context, ids []string) ([]*Order, error) {
	return s.orderModel.ListByIds(ctx, ids, dbcore.Order{Field: "create_at", Desc: true})
}

// CheckOrderExists 检查订单是否存在
func (s *OrderService) CheckOrderExists(ctx context.Context, orderNo string) (bool, error) {
	return s.orderModel.Exist(ctx, "order_no = ?", orderNo)
}

// ============================================================
// 5. 初始化示例（main.go 或 wire.go）
// ============================================================

/*

func initDB() *gorm.DB {
    dsn := "user:pass@tcp(127.0.0.1:3306)/dbname?charset=utf8mb4&parseTime=True&loc=Local"
    db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{
        // 推荐配置（见 SKILL.md 第 1 节）
        SkipDefaultTransaction:                   true,
        PrepareStmt:                              true,
        DisableForeignKeyConstraintWhenMigrating: true,
        Logger: logger.New(
            log.New(os.Stdout, "\r\n", log.LstdFlags),
            logger.Config{
                SlowThreshold:             200 * time.Millisecond,
                LogLevel:                  logger.Warn,
                IgnoreRecordNotFoundError: true,
            },
        ),
    })
    if err != nil {
        panic(err)
    }

    sqlDB, _ := db.DB()
    sqlDB.SetMaxOpenConns(100)
    sqlDB.SetMaxIdleConns(20)
    sqlDB.SetConnMaxLifetime(time.Hour)
    sqlDB.SetConnMaxIdleTime(10 * time.Minute)
    return db
}

func main() {
    db := initDB()

    // 配置 ID 生成器
    dbcore.SetIDGenerator(dbcore.NewSnowflakeGenerator(1))

    // 配置多租户（按需开启，不需要多租户时可跳过此步）
    dbcore.SetConfig(dbcore.Config{
        TenantEnabled: true,               // 开启多租户隔离
        TenantField:   "tenant_id",        // 租户字段名（默认 tenant_id）
        TenantStrict:  true,               // 严格模式：无租户信息时拒绝查询
        TenantExtractor: func(ctx context.Context) string {
            if tid, ok := ctx.Value("tenant_id").(string); ok {
                return tid
            }
            return ""
        },
    })
    // 不需要多租户时，不调用 SetConfig 或设置 TenantEnabled: false（默认值）

    // isMigrate: 开发环境 true，生产环境 false
    orderModel := NewOrderModel(db, os.Getenv("APP_ENV") != "production")
    tx          := dbcore.NewTransaction(db)
    orderSvc    := NewOrderService(orderModel, tx)

    // 创建订单（ctx 中携带租户信息，BaseModel 自动隔离）
    ctx := context.WithValue(context.Background(), "tenant_id", "tenant_001")
    err := orderSvc.CreateOrder(ctx, &Order{
        TenantID:        "tenant_001",
        PlatformID:      "platform_ctrip",
        PlatformOrderNo: "CTRIP_20240101_001",
        OrderNo:         "SYS_20240101_001",
        CustomerName:    "张三",
        CustomerPhone:   "13800138000",
        OrderStatus:     OrderStatusPending,
    })
}

*/
