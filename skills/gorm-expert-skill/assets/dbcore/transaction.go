// Package dbcore 提供数据库操作的核心功能
// 本文件实现事务管理功能，支持嵌套事务和事务传播
package dbcore

import (
	"context"

	"gorm.io/gorm"
)

// ==================== 类型定义 ====================

type (
	// Transaction 事务管理接口
	Transaction interface {
		ExecTx(context.Context, func(ctx context.Context) error) error
	}

	txDB struct {
		db *gorm.DB
	}

	// contextTxKey 事务上下文键，使用空结构体避免与其他包键冲突
	contextTxKey struct{}
)

// NewTransaction 创建事务管理器
//
// 使用示例:
//
//	tx := dbcore.NewTransaction(db)
//	err := tx.ExecTx(ctx, func(ctx context.Context) error {
//	    return userModel.Insert(ctx, user)
//	})
func NewTransaction(db *gorm.DB) Transaction {
	return &txDB{db: db}
}

// ExecTx 执行事务
//
// 支持嵌套调用，GORM 自动通过 SavePoint 实现嵌套事务：
//   - 业务函数返回 nil → 自动 COMMIT
//   - 业务函数返回 error / panic → 自动 ROLLBACK
//   - 嵌套调用 → 自动创建 SavePoint，支持局部回滚
//
// 使用示例:
//
//	// 基本事务
//	err := tx.ExecTx(ctx, func(ctx context.Context) error {
//	    if err := orderModel.Insert(ctx, order); err != nil {
//	        return err
//	    }
//	    return stockModel.Decrease(ctx, order.ProductID, order.Qty)
//	})
//
//	// 嵌套事务
//	err := tx.ExecTx(ctx, func(ctx context.Context) error {
//	    userModel.Insert(ctx, user)
//	    return tx.ExecTx(ctx, func(ctx context.Context) error {
//	        return logModel.Insert(ctx, log) // SavePoint 保护
//	    })
//	})
func (t *txDB) ExecTx(ctx context.Context, f func(ctx context.Context) error) error {
	// 已在事务中（嵌套场景）：复用现有事务，GORM 自动创建 SavePoint
	if tx, ok := ctx.Value(contextTxKey{}).(*gorm.DB); ok {
		return tx.Transaction(func(nestedTx *gorm.DB) error {
			return f(context.WithValue(ctx, contextTxKey{}, nestedTx))
		})
	}
	// 首次开启事务
	return t.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		return f(context.WithValue(ctx, contextTxKey{}, tx))
	})
}

// ==================== 辅助函数 ====================

// GetDB 获取数据库连接
//
// 优先从 ctx 中取事务连接（保证操作在同一事务内），
// 非事务时用 NewDB Session 创建干净会话，避免条件累积。
func GetDB(ctx context.Context, db *gorm.DB) *gorm.DB {
	if tx, ok := ctx.Value(contextTxKey{}).(*gorm.DB); ok {
		return tx
	}
	return db.Session(&gorm.Session{NewDB: true})
}

// InTransaction 判断当前是否在事务中
//
// 使用场景: 需要根据是否在事务中采取不同策略时
//
//	if dbcore.InTransaction(ctx) {
//	    return service.DoSomething(ctx)
//	} else {
//	    return tx.ExecTx(ctx, func(ctx context.Context) error {
//	        return service.DoSomething(ctx)
//	    })
//	}
func InTransaction(ctx context.Context) bool {
	_, ok := ctx.Value(contextTxKey{}).(*gorm.DB)
	return ok
}
