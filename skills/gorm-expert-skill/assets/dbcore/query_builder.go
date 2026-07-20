// Package dbcore 提供数据库操作的核心功能
// 本文件实现SQL查询条件构建器，支持链式调用构建复杂查询条件
package dbcore

import (
	"fmt"
	"strings"
)

// ==================== 查询构建器 ====================

// QueryBuilder 查询条件构建器
// 提供链式API构建SQL WHERE条件，自动处理参数绑定
// 所有条件默认使用AND连接
//
// 使用示例:
//
//	query, args := dbcore.NewQueryBuilder().
//	    Like("name", "张").
//	    Eq("status", 1).
//	    Gte("age", 18).
//	    Build()
//	// query: "name LIKE ? AND status = ? AND age >= ?"
//	// args: ["%张%", 1, 18]
type QueryBuilder struct {
	conditions []string      // SQL条件片段列表
	args       []interface{} // 对应的参数列表
}

// NewQueryBuilder 创建查询构建器实例
func NewQueryBuilder() *QueryBuilder {
	return &QueryBuilder{
		conditions: make([]string, 0),
		args:       make([]interface{}, 0),
	}
}

// ==================== 模糊查询 ====================

// Like 模糊查询（包含匹配）: field LIKE '%value%'
func (q *QueryBuilder) Like(field string, value string) *QueryBuilder {
	if value != "" {
		q.conditions = append(q.conditions, fmt.Sprintf("%s LIKE ?", safeField(field)))
		q.args = append(q.args, "%"+value+"%")
	}
	return q
}

// LikeLeft 左模糊查询（以指定值结尾）: field LIKE '%value'
func (q *QueryBuilder) LikeLeft(field string, value string) *QueryBuilder {
	if value != "" {
		q.conditions = append(q.conditions, fmt.Sprintf("%s LIKE ?", safeField(field)))
		q.args = append(q.args, "%"+value)
	}
	return q
}

// LikeRight 右模糊查询（以指定值开头）: field LIKE 'value%'
// 推荐优先使用此方法替代 Like，可走索引
func (q *QueryBuilder) LikeRight(field string, value string) *QueryBuilder {
	if value != "" {
		q.conditions = append(q.conditions, fmt.Sprintf("%s LIKE ?", safeField(field)))
		q.args = append(q.args, value+"%")
	}
	return q
}

// ==================== 比较查询 ====================

// Eq 等于查询: field = value
// 注意: int/int64/float64 类型的 0 被视为有效值，不会被忽略
func (q *QueryBuilder) Eq(field string, value interface{}) *QueryBuilder {
	if !isEmpty(value) {
		q.conditions = append(q.conditions, fmt.Sprintf("%s = ?", safeField(field)))
		q.args = append(q.args, value)
	}
	return q
}

// EqIfPositive 条件等于查询（仅当值 > 0 时生效）
// 使用场景: 查询参数中 0 表示"全部"，> 0 表示具体状态
func (q *QueryBuilder) EqIfPositive(field string, value int) *QueryBuilder {
	if value > 0 {
		q.conditions = append(q.conditions, fmt.Sprintf("%s = ?", safeField(field)))
		q.args = append(q.args, value)
	}
	return q
}

// Ne 不等于查询: field != value
func (q *QueryBuilder) Ne(field string, value interface{}) *QueryBuilder {
	if !isEmpty(value) {
		q.conditions = append(q.conditions, fmt.Sprintf("%s != ?", safeField(field)))
		q.args = append(q.args, value)
	}
	return q
}

// Gt 大于查询: field > value
func (q *QueryBuilder) Gt(field string, value interface{}) *QueryBuilder {
	if !isEmpty(value) {
		q.conditions = append(q.conditions, fmt.Sprintf("%s > ?", safeField(field)))
		q.args = append(q.args, value)
	}
	return q
}

// Gte 大于等于查询: field >= value
func (q *QueryBuilder) Gte(field string, value interface{}) *QueryBuilder {
	if !isEmpty(value) {
		q.conditions = append(q.conditions, fmt.Sprintf("%s >= ?", safeField(field)))
		q.args = append(q.args, value)
	}
	return q
}

// Lt 小于查询: field < value
func (q *QueryBuilder) Lt(field string, value interface{}) *QueryBuilder {
	if !isEmpty(value) {
		q.conditions = append(q.conditions, fmt.Sprintf("%s < ?", safeField(field)))
		q.args = append(q.args, value)
	}
	return q
}

// Lte 小于等于查询: field <= value
func (q *QueryBuilder) Lte(field string, value interface{}) *QueryBuilder {
	if !isEmpty(value) {
		q.conditions = append(q.conditions, fmt.Sprintf("%s <= ?", safeField(field)))
		q.args = append(q.args, value)
	}
	return q
}

// Between 区间查询: field BETWEEN start AND end
// 注意: start 和 end 必须同时有效才会生成条件
func (q *QueryBuilder) Between(field string, start, end interface{}) *QueryBuilder {
	if !isEmpty(start) && !isEmpty(end) {
		q.conditions = append(q.conditions, fmt.Sprintf("%s BETWEEN ? AND ?", safeField(field)))
		q.args = append(q.args, start, end)
	}
	return q
}

// ==================== 范围查询 ====================

// In 范围查询（通用版本）: field IN (?, ?, ...)
func (q *QueryBuilder) In(field string, values []interface{}) *QueryBuilder {
	if len(values) > 0 {
		placeholders := make([]string, len(values))
		for i := range values {
			placeholders[i] = "?"
		}
		q.conditions = append(q.conditions,
			fmt.Sprintf("%s IN (%s)", safeField(field), strings.Join(placeholders, ",")))
		q.args = append(q.args, values...)
	}
	return q
}

// InStrings 字符串范围查询: field IN (?, ?, ...)
//
// 修复说明: 原版本在循环内追加 args 后才追加 condition，
// 导致多个链式条件时 args 与占位符顺序错位。
// 现改为先构建 placeholders 和 ifaces，再统一追加 condition 和 args。
func (q *QueryBuilder) InStrings(field string, values []string) *QueryBuilder {
	if len(values) > 0 {
		placeholders := make([]string, len(values))
		ifaces := make([]interface{}, len(values))
		for i, v := range values {
			placeholders[i] = "?"
			ifaces[i] = v
		}
		q.conditions = append(q.conditions,
			fmt.Sprintf("%s IN (%s)", safeField(field), strings.Join(placeholders, ",")))
		q.args = append(q.args, ifaces...)
	}
	return q
}

// InInts 整数范围查询: field IN (?, ?, ...)
//
// 修复说明: 同 InStrings，修复 args 追加顺序问题。
func (q *QueryBuilder) InInts(field string, values []int) *QueryBuilder {
	if len(values) > 0 {
		placeholders := make([]string, len(values))
		ifaces := make([]interface{}, len(values))
		for i, v := range values {
			placeholders[i] = "?"
			ifaces[i] = v
		}
		q.conditions = append(q.conditions,
			fmt.Sprintf("%s IN (%s)", safeField(field), strings.Join(placeholders, ",")))
		q.args = append(q.args, ifaces...)
	}
	return q
}

// NotIn 不在范围内查询: field NOT IN (?, ?, ...)
func (q *QueryBuilder) NotIn(field string, values []interface{}) *QueryBuilder {
	if len(values) > 0 {
		placeholders := make([]string, len(values))
		for i := range values {
			placeholders[i] = "?"
		}
		q.conditions = append(q.conditions,
			fmt.Sprintf("%s NOT IN (%s)", safeField(field), strings.Join(placeholders, ",")))
		q.args = append(q.args, values...)
	}
	return q
}

// NotLike 模糊排除查询: field NOT LIKE '%value%'
func (q *QueryBuilder) NotLike(field string, value string) *QueryBuilder {
	if value != "" {
		q.conditions = append(q.conditions, fmt.Sprintf("%s NOT LIKE ?", safeField(field)))
		q.args = append(q.args, "%"+value+"%")
	}
	return q
}

// ==================== NULL 查询 ====================

// IsNull 空值查询: field IS NULL
func (q *QueryBuilder) IsNull(field string) *QueryBuilder {
	q.conditions = append(q.conditions, fmt.Sprintf("%s IS NULL", safeField(field)))
	return q
}

// IsNotNull 非空值查询: field IS NOT NULL
func (q *QueryBuilder) IsNotNull(field string) *QueryBuilder {
	q.conditions = append(q.conditions, fmt.Sprintf("%s IS NOT NULL", safeField(field)))
	return q
}

// ==================== 自定义条件 ====================

// Raw 添加原始SQL条件，用于构建复杂条件（如子查询）
// 示例: Raw("(status = ? OR type = ?)", 1, 2)
func (q *QueryBuilder) Raw(condition string, args ...interface{}) *QueryBuilder {
	if condition != "" {
		q.conditions = append(q.conditions, condition)
		q.args = append(q.args, args...)
	}
	return q
}

// OrGroup 将多个子条件用 OR 连接后作为整体 AND 到主条件
// 示例:
//
//	qb.OrGroup(
//	    NewQueryBuilder().Eq("status", 1),
//	    NewQueryBuilder().Eq("status", 3),
//	)
//	// 生成: (status = ? OR status = ?)  args: [1, 3]
func (q *QueryBuilder) OrGroup(conditions ...*QueryBuilder) *QueryBuilder {
	parts := make([]string, 0, len(conditions))
	for _, c := range conditions {
		if c.IsEmpty() {
			continue
		}
		subQuery, subArgs := c.Build()
		parts = append(parts, "("+subQuery+")")
		q.args = append(q.args, subArgs...)
	}
	if len(parts) > 0 {
		q.conditions = append(q.conditions, "("+strings.Join(parts, " OR ")+")")
	}
	return q
}

// ==================== 构建方法 ====================

// IsEmpty 判断构建器是否没有任何条件
// 可用于调用方主动判断是否意外传入了空查询
func (q *QueryBuilder) IsEmpty() bool {
	return len(q.conditions) == 0
}

// Build 构建最终的查询条件
// 将所有条件用 AND 连接，返回完整的 WHERE 子句（不含 WHERE 关键字）
// 无条件时返回 "1=1"（恒真，避免空 WHERE 报错）
//
// 使用示例:
//
//	query, args := builder.Build()
//	db.Where(query, args...).Find(&list)
func (q *QueryBuilder) Build() (string, []interface{}) {
	if len(q.conditions) == 0 {
		return "1=1", nil
	}
	return strings.Join(q.conditions, " AND "), q.args
}

// BuildWithPrefix 构建带前缀的查询条件
// 无条件时不添加前缀，直接返回 "1=1"
func (q *QueryBuilder) BuildWithPrefix(prefix string) (string, []interface{}) {
	query, args := q.Build()
	if query == "1=1" {
		return query, args
	}
	return prefix + " " + query, args
}

// ==================== 辅助函数 ====================

// safeField 校验字段名，防止 SQL 注入
// 只允许字母、数字、下划线和点号（支持 table.column 格式）
func safeField(field string) string {
	for _, c := range field {
		if !((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
			(c >= '0' && c <= '9') || c == '_' || c == '.') {
			panic(fmt.Sprintf("dbcore: invalid field name %q (only [a-zA-Z0-9_.] allowed)", field))
		}
	}
	return field
}

// isEmpty 判断值是否为空（nil 或空字符串）
// int/int64/float64 类型的 0 视为有效值，返回 false
// 如需忽略 0 值，请使用 EqIfPositive
func isEmpty(value interface{}) bool {
	if value == nil {
		return true
	}
	switch v := value.(type) {
	case string:
		return v == ""
	default:
		return false
	}
}
