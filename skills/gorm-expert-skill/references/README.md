# References 目录索引

按主题分组，按需加载，不要全量读入。

---

## 🏗️ 基础设施

| 文件 | 内容摘要 | 触发时机 |
|------|---------|---------|
| [base-model-pattern.md](./base-model-pattern.md) | 泛型 BaseModel 设计规范、QueryBuilder Bug 修复、游标分页、多租户隔离 | BaseModel 使用、QueryBuilder 问题 |
| [migration.md](./migration.md) | golang-migrate 规范、大表在线 DDL、AutoMigrate 生产限制 | 数据库迁移、ALTER TABLE |
| [testing.md](./testing.md) | sqlmock 单测、SQLite 集成测试、软删除唯一约束经典坑 | GORM 代码测试 |

---

## ⚡ 性能优化

| 文件 | 内容摘要 | 触发时机 |
|------|---------|---------|
| [indexing.md](./indexing.md) | 覆盖索引、前缀索引、函数索引、EXPLAIN 验证、失效场景 | 索引设计、慢查询 |
| [concurrency.md](./concurrency.md) | 乐观锁（version/optimisticlock）、悲观锁、CAS 原子更新 | 并发冲突、超卖、转账 |
| [sharding.md](./sharding.md) | 分库分表配置、分片算法、双写迁移、跨分片查询 | 水平拆分、分片键设计 |
| [caching.md](./caching.md) | Redis Cache-Aside、singleflight 防击穿、TTL 抖动防雪崩、布隆过滤器 | GORM + Redis 缓存集成 |

---

## 🔧 GORM v2 核心机制

| 文件 | 内容摘要 | 触发时机 |
|------|---------|---------|
| [session.md](./session.md) | Session 配置项、NewDB vs WithContext、goroutine 安全、条件累积防范 | Session 问题、db 复用、DryRun |
| [clause.md](./clause.md) | OnConflict/Returning/Locking/OrderBy、自定义 Clause 表达式 | FOR UPDATE、Upsert、RETURNING |
| [association.md](./association.md) | Preload/Joins 选型、Append/Replace/Delete、Select+Omit 级联控制 | 关联加载、多对多、级联写入 |
| [serializer.md](./serializer.md) | json/gob/unixtime Serializer、枚举/Money/加密自定义类型 | 字段序列化、自定义类型映射 |

---

## 🛡️ 数据安全与 ID 生成

| 文件 | 内容摘要 | 触发时机 |
|------|---------|---------|
| [soft-delete.md](./soft-delete.md) | 软删除完整指南、唯一约束兼容、时间戳/flag 模式、归档清理 | 软删除、Unscoped、deleted_at 唯一约束 |
| [id-generation.md](./id-generation.md) | Snowflake/Leaf-Segment/UUID 选型、时钟回拨保护、K8s nodeID、号段调优 | ID 生成策略、分布式 ID、自增 ID 迁移 |

---

## 🧩 模式与扩展

| 文件 | 内容摘要 | 触发时机 |
|------|---------|---------|
| [scopes.md](./scopes.md) | 可复用 Scope、分页 Scope、多租户 Scope、软删除 Scope | Scope 用法、多租户设计 |
| [hooks.md](./hooks.md) | Hook 执行顺序、性能陷阱、全局 Callback vs Hook | Hook 使用、AfterFind N+1 |
| [raw-sql.md](./raw-sql.md) | Raw/Exec/Scan/Rows、First/Take/Find 行为差异、v2 Error 处理规范 | 原生 SQL、ErrRecordNotFound |
| [observability.md](./observability.md) | Prometheus 指标、慢查询 Logger、OpenTelemetry 链路追踪、Grafana 仪表盘 | 监控、可观测性 |

---

## 快速选择指南

**遇到性能问题** → 先看 `indexing.md`，再看 `concurrency.md`

**遇到 N+1** → `association.md` §3

**写新 Model** → `base-model-pattern.md` §1–§3 + `testing.md` §6

**配缓存** → `caching.md` §1–§3

**上生产迁移** → `migration.md` §3–§4

**遇到 Session 条件累积** → `session.md` §3 + §8

**软删除问题** → `soft-delete.md`（唯一约束、Preload、归档清理）

**分布式 ID** → `id-generation.md`（Snowflake vs Leaf vs UUID 选型）
