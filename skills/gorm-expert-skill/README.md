# gorm-expert-skill

> 适用于 Claude 的 GORM v2 使用与性能优化专项 Skill（v1.5.0）

## 功能覆盖

### 代码质量与安全

| 场景 | 说明 |
|------|------|
| 代码审查 / 静态分析 | 26 条反模式检测规则（R1–R26），支持 `--format json` CI 集成 |
| SQL 注入防护 | Where/Raw 字符串拼接检测（R13/R22）、QueryBuilder 字段名校验 |
| Error 处理规范 | v2 `errors.Is(err, gorm.ErrRecordNotFound)` 规范、RowsAffected 检查 |

### 性能优化

| 场景 | 说明 |
|------|------|
| 慢查询 / N+1 / 全表扫描 | 索引设计、EXPLAIN 分析、Preload/Joins 选型 |
| 连接池配置 | Little's Law 计算推荐值 + 健康检查代码生成 |
| 批量操作 | CreateInBatches、FindInBatches、游标分页 |
| 查询投影 | Select 字段选择、Scan 到 DTO、ScanRows 流式读取 |
| 缓存集成 | Redis Cache-Aside、singleflight 防击穿、TTL 抖动防雪崩 |

### 数据操作与事务

| 场景 | 说明 |
|------|------|
| 事务管理 | 标准/嵌套事务、Savepoint、乐观锁、悲观锁（FOR UPDATE）、CAS |
| 写操作 | Updates(map) 避免零值丢失、Upsert（OnConflict）、RowsAffected 检查 |
| 软删除 | 唯一约束兼容方案、时间戳/flag 模式、归档清理 |
| 读写分离 | dbresolver 插件配置 |

### 架构与扩展

| 场景 | 说明 |
|------|------|
| 分库分表（Sharding） | gorm.io/sharding 配置、分片算法、双写迁移 |
| Scopes 与多租户 | 可复用查询条件、行级租户隔离、Scope 自动生成 |
| 监控与可观测性 | Prometheus 指标、慢查询告警、OpenTelemetry 链路追踪 |
| 物理外键禁用 | 强制逻辑外键规范、AutoMigrate 禁止 FK 约束 |

### 开发工具

| 场景 | 说明 |
|------|------|
| SQL → GORM struct | CREATE TABLE 转 Go Model，支持 MySQL / PostgreSQL |
| 数据库迁移 | struct diff → ALTER TABLE SQL，支持 ALGORITHM=INSTANT |
| Benchmark / pprof | 5 种预设场景 + 自定义函数签名 |
| 项目脚手架 | 一键生成 BaseModel + QueryBuilder + Transaction 基础包 |

---

## 目录结构

```
gorm-expert-skill/
├── SKILL.md                          # 主技能文件（14 节快速参考）
├── CHANGELOG.md                      # 版本变更记录
├── README.md
│
├── scripts/                          # 8 个 Python 工具脚本
│   ├── analyze_gorm.py               # 🔍 静态分析（R1–R26，支持 --format json）
│   ├── gen_model.py                  # 🔍 SQL → GORM struct（MySQL / PostgreSQL）
│   ├── pool_advisor.py               # 🔍 连接池参数计算 + 健康检查代码
│   ├── query_explain.py              # 🔍 SQL 性能分析（11 条规则）
│   ├── migration_gen.py              # 🔍 struct diff → ALTER TABLE SQL
│   ├── bench_template.py             # 📝 Benchmark + pprof 代码生成
│   ├── scope_gen.py                  # 🔍 Scope 函数自动生成
│   └── init_project.py               # 📝 dbcore 脚手架生成（--dry-run 预览）
│
├── references/                       # 17 篇专题参考文档
│   ├── README.md                     # 索引（按主题分组 + 快速选择指南）
│   │
│   │  # 基础设施
│   ├── base-model-pattern.md         # 泛型 BaseModel 设计规范与 Bug 修复
│   ├── migration.md                  # golang-migrate 规范、大表在线 DDL
│   ├── testing.md                    # sqlmock / SQLite / 软删除唯一约束
│   │
│   │  # 性能优化
│   ├── indexing.md                   # 覆盖索引、前缀索引、函数索引、EXPLAIN
│   ├── concurrency.md               # 乐观锁、悲观锁、CAS 原子更新
│   ├── sharding.md                   # 分库分表、分片算法、双写迁移
│   ├── caching.md                    # Redis Cache-Aside、防击穿/雪崩/穿透
│   │
│   │  # GORM v2 核心机制
│   ├── session.md                    # Session 配置、goroutine 安全、条件累积
│   ├── clause.md                     # Clause 系统（Upsert/FOR UPDATE/RETURNING）
│   ├── association.md                # Preload/Joins 选型、级联控制
│   ├── serializer.md                 # Serializer + 自定义数据类型（枚举/Money/加密）
│   │
│   │  # 模式与扩展
│   ├── scopes.md                     # 可复用 Scope、分页、多租户隔离
│   ├── hooks.md                      # Hook 执行顺序与性能陷阱
│   ├── raw-sql.md                    # Raw SQL / Scan / Rows、v2 Error 处理
│   ├── observability.md              # Prometheus / OpenTelemetry / Grafana
│   │
│   │  # 数据安全与 ID 生成
│   ├── soft-delete.md                # 软删除完整指南（唯一约束、时间戳模式、归档）
│   └── id-generation.md              # 分布式 ID 策略（Snowflake/Leaf-Segment/UUID）
│
└── assets/dbcore/                    # 生产就绪的 Go 基础包
    ├── base_model.go                 # 泛型 BaseModel（17 个方法 + 游标分页）
    ├── query_builder.go              # 链式查询构建器（含 SQL 注入防护）
    ├── transaction.go                # 事务管理器（嵌套事务 + context 传播）
    ├── auto_id.go                    # 可插拔 ID 生成器（Snowflake/Leaf-Segment/UUID）
    └── example_order_model.go        # 完整 OrderModel 示例（多租户 + 软删除）
```

---

## 脚本使用指南

> 所有脚本仅依赖 Python 3.8+，不调用任何外部 API 或凭证。
> 🔍 只读（stdin/stdout）  📝 写磁盘（需 `--output`，支持 `--dry-run`）

### analyze_gorm.py — GORM 代码静态分析

```bash
# 分析文件
python3 scripts/analyze_gorm.py repository.go

# 分析 stdin
cat main.go | python3 scripts/analyze_gorm.py -

# JSON 输出（CI 集成）
python3 scripts/analyze_gorm.py --format json repository.go

# CI pipeline 中使用（ERROR 级别返回退出码 1）
python3 scripts/analyze_gorm.py --format json src/ || exit 1
```

### gen_model.py — SQL → GORM struct

```bash
# MySQL（默认）
echo "CREATE TABLE users (...) ENGINE=InnoDB;" | python3 scripts/gen_model.py -

# PostgreSQL
python3 scripts/gen_model.py schema.sql --dialect pg

# 快速模式（无需完整 SQL）
python3 scripts/gen_model.py --table users --fields "id:bigint,name:varchar(100),created_at:datetime"
```

### pool_advisor.py — 连接池参数计算

```bash
python3 scripts/pool_advisor.py \
  --qps 500 \
  --avg-latency-ms 20 \
  --db-max-conn 200 \
  --app-instances 4 \
  --db-type mysql
```

输出：可直接粘贴的 Go 代码 + Little's Law 计算过程 + 健康检查函数。

### query_explain.py — SQL 性能分析

```bash
python3 scripts/query_explain.py "SELECT * FROM users WHERE name LIKE '%foo%' ORDER BY created_at LIMIT 20"
```

输出：复杂度评估 + 问题列表 + 改写建议 + EXPLAIN 验证命令。

### migration_gen.py — 迁移 SQL 生成

```bash
# 对比两个版本的 struct 文件
python3 scripts/migration_gen.py old_model.go new_model.go --table users

# 内联模式
python3 scripts/migration_gen.py \
  --old-struct "Name string; Age int" \
  --new-struct "Name string; Age int; Email string" \
  --table users
```

输出：UP（迁移）+ DOWN（回滚）SQL，含 ALGORITHM=INSTANT 提示。

### bench_template.py — Benchmark 代码生成

```bash
# 自定义函数
python3 scripts/bench_template.py --func "GetUserByID(db *gorm.DB, id uint) (*User, error)"

# 预设场景：bulk_insert / pagination / query_by_id / query_with_preload / update_compare
python3 scripts/bench_template.py --scenario pagination

# 写入文件
python3 scripts/bench_template.py --scenario bulk_insert --output bench_test.go
```

### scope_gen.py — Scope 函数自动生成

```bash
# 基础生成
python3 scripts/scope_gen.py model.go

# 含多租户 + 分页 Scope
python3 scripts/scope_gen.py model.go --tenant --paginate
```

### init_project.py — 项目脚手架

```bash
# 预览（不写盘）
python3 scripts/init_project.py --output ./internal/dbcore --dry-run

# 写入
python3 scripts/init_project.py --output ./internal/dbcore

# 含示例 + 自定义包名
python3 scripts/init_project.py --output ./pkg/db --package mydb --example

# 强制覆盖已有文件
python3 scripts/init_project.py --output ./internal/dbcore --force
```

---

## analyze_gorm.py 检测规则一览（R1–R26）

架构：逐行规则（per-line loop）+ 全文件规则（full-file check），去重按行号排序。

### 逐行检测（Per-Line Rules）

| 规则 | 级别 | 说明 |
|------|------|------|
| R1: SELECT_STAR | WARN | Find/First 未指定 Select 字段 |
| R2: LARGE_OFFSET / DYNAMIC_OFFSET | ERROR/WARN | 大/动态 Offset 分页，建议游标分页 |
| R3: N_PLUS_1 | ERROR | for-range 循环内 DB 操作 |
| R4: STRUCT_UPDATES_ZERO_VALUE | WARN | `Updates(struct{})` 零值字段被忽略 |
| R5: NO_CONTEXT | INFO | 未传 `WithContext(ctx)` |
| R6: UNCHECKED_ERROR | WARN | DB 操作后未检查 `.Error` |
| R7: FIND_ALL_NO_LIMIT | WARN | Find 无 Where/Limit，可能全表扫描 |
| R8: SLOW_OP_IN_TX | ERROR | 事务内调用 HTTP/gRPC/Sleep |
| R9: LEADING_WILDCARD_LIKE | WARN | `LIKE '%xxx%'` 前导通配符无法走索引 |
| R10: LOOP_CREATE | ERROR | 循环内逐条 Create（应 CreateInBatches） |
| R13: SQL_INJECTION_RISK | ERROR | Raw/Exec 中字符串拼接或 fmt.Sprintf |
| R14: PLUCK_MULTI_COLUMN | WARN | Pluck 只支持单列，多列应用 Select+Scan |
| R16: SOFT_DELETE_REMINDER | INFO | Delete 提醒：含 DeletedAt 的 Model 是软删除 |
| R17: DB_IN_TX_BLOCK | ERROR | 事务块内使用全局 `db` 而非 `tx` |
| R18a: PHYSICAL_FOREIGN_KEY | ERROR | foreignKey tag 未加 `constraint:false` |
| R19: GOROUTINE_DB_UNSAFE | WARN | goroutine 内共享 `*gorm.DB` 未用 Session 隔离 |
| R20: DB_CONDITION_ACCUMULATION | INFO | 复用 `*gorm.DB` 导致 WHERE 条件累积 |
| R21: V1_NOT_FOUND_API | ERROR | 使用 v1 的 `gorm.IsRecordNotFoundError` |
| R22: WHERE_SQL_INJECTION | ERROR | Where 中字符串拼接（SQL 注入风险） |
| R23: UNCHECKED_ROWS_AFFECTED | INFO | Update/Delete 后未检查 RowsAffected |
| R24: SAVE_FULL_UPDATE | INFO | `db.Save()` 全量更新所有字段 |
| R25: AUTO_MIGRATE_IN_BUSINESS | WARN | AutoMigrate 出现在非 init/main/setup 函数中 |

### 全文件检测（Full-File Rules）

| 规则 | 级别 | 说明 |
|------|------|------|
| R11: MISSING_PREPARE_STMT | INFO | gorm.Config 缺少 `PrepareStmt: true` |
| R12: MISSING_SKIP_DEFAULT_TX | INFO | 缺少 `SkipDefaultTransaction: true` |
| R15: MISSING_POOL_CONFIG | WARN | 未设置 `SetMaxOpenConns` 等连接池参数 |
| R18b: FK_MIGRATION_NOT_DISABLED | WARN | 未设置 `DisableForeignKeyConstraintWhenMigrating` |

---

## assets/dbcore 基础包

生产就绪的泛型数据库操作基础包，通过 `init_project.py` 脚手架到目标项目。

### BaseModel — 17 个通用方法

| 分类 | 方法 | 说明 |
|------|------|------|
| 插入 | `Insert`, `InsertBatch` | 自动填充雪花 ID，批量插入指定 batchSize |
| 更新 | `Update`, `UpdateBy`, `Save` | map 更新避免零值丢失，条件更新 |
| 删除 | `Delete`, `DeleteByIds`, `DeleteBy` | 软删除兼容，空 ID/条件保护 |
| 查询 | `Find`, `First` | Find 用 Take（无排序开销），First 用 ORDER BY id |
| 列表 | `ListByIds`, `List`, `ListAll` | ListAll 有 10,000 条软上限防 OOM |
| 分页 | `Page`, `PageAfter` | OFFSET 分页 + 游标分页，baseDB Session 隔离 |
| 统计 | `Exist`, `Count` | Limit(1) 优化 Exist |

### QueryBuilder — 链式查询构建

```go
query, args := dbcore.NewQueryBuilder().
    Like("name", "张").
    Eq("status", 1).
    Gte("age", 18).
    OrGroup(
        dbcore.NewQueryBuilder().Eq("type", "vip"),
        dbcore.NewQueryBuilder().Eq("type", "admin"),
    ).
    Build()
// query: "name LIKE ? AND status = ? AND age >= ? AND ((type = ?) OR (type = ?))"
// args:  ["%张%", 1, 18, "vip", "admin"]
```

安全特性：所有 field 参数经 `safeField()` 校验，仅允许 `[a-zA-Z0-9_.]`，防止 SQL 注入。

### Transaction — 事务管理

```go
tx := dbcore.NewTransaction(db)
err := tx.ExecTx(ctx, func(ctx context.Context) error {
    if err := orderModel.Insert(ctx, order); err != nil {
        return err
    }
    // 嵌套事务（自动 SavePoint）
    return tx.ExecTx(ctx, func(ctx context.Context) error {
        return logModel.Insert(ctx, auditLog)
    })
})
```

---

## 版本历史

| 版本 | 主要变更 |
|------|---------|
| **v1.5.0** | auto_id.go 重写为可插拔 ID 生成器（Snowflake/Leaf-Segment/UUID）；新增 `references/id-generation.md` + `soft-delete.md`；修复 gen_model.py/QueryBuilder OrGroup/pool_advisor.py Bug；新增 R22–R25 检测规则 + `--format json`；SQL 注入防护 |
| v1.4.0 | SKILL.md 精简至 ~500 行；新增 auto_id.go 雪花算法；references/README.md 索引；安全 frontmatter |
| v1.3.0 | GORM v2 核心机制全覆盖：session/clause/association/serializer/raw-sql；R19–R21 规则 |
| v1.2.1 | 新增 example_order_model.go 完整示例 |
| v1.2.0 | init_project.py 脚手架；assets/dbcore 基础包 |
| v1.1.1 | base-model-pattern.md；QueryBuilder args Bug 修复；游标分页 |
| v1.1.0 | Scopes/多租户/缓存章节；scope_gen.py；PostgreSQL 支持 |
| v1.0.x | 初始发布 + 分库分表 + 监控可观测性 |

详细变更记录见 [CHANGELOG.md](./CHANGELOG.md)。

## 运行要求

- Python >= 3.8（脚本工具）
- 无需外部 API 凭证
- 无需网络访问

## License

MIT
