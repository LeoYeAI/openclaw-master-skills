#!/usr/bin/env python3
"""
pool_advisor.py — 根据业务参数计算推荐的 GORM / database/sql 连接池配置
用法:
  python3 pool_advisor.py \
    --qps 500 \
    --avg-latency-ms 20 \
    --db-max-conn 200 \
    --app-instances 4 \
    --db-type mysql

输出: 直接可粘贴的 Go 配置代码 + 参数说明
"""

import argparse
import math
import sys

def calculate_pool(
    qps: float,
    avg_latency_ms: float,
    db_max_conn: int,
    app_instances: int,
    db_type: str,
    peak_multiplier: float,
    idle_ratio: float,
    conn_lifetime_min: int,
) -> dict:
    """
    核心公式:
      - 理论最小连接数 = QPS × (avg_latency_ms / 1000)  — Little's Law
      - 考虑峰值 × peak_multiplier
      - 每实例最大连接 = min(理论值, db_max_conn / app_instances × 0.8)
      - 空闲连接 = MaxOpen × idle_ratio
    """
    # 基于 Little's Law 的理论值
    theoretical_min = qps * (avg_latency_ms / 1000.0)
    theoretical_with_peak = theoretical_min * peak_multiplier

    # DB 侧每实例允许的上限（留 20% 给管理连接 / 其他工具）
    db_limit_per_instance = math.floor((db_max_conn * 0.8) / app_instances)

    # 最终推荐值
    recommended_max = min(math.ceil(theoretical_with_peak), db_limit_per_instance)
    recommended_max = max(recommended_max, 5)  # 最少 5

    recommended_idle = max(math.ceil(recommended_max * idle_ratio), 2)

    # 连接存活时间：MySQL 默认 8h wait_timeout，建议设置为 < wait_timeout 的 80%
    lifetime_s = conn_lifetime_min * 60
    idle_time_s = max(lifetime_s // 6, 60)  # 空闲连接更激进回收

    return {
        "max_open": recommended_max,
        "max_idle": recommended_idle,
        "conn_lifetime_s": lifetime_s,
        "conn_idle_timeout_s": idle_time_s,
        "theoretical_min": round(theoretical_min, 1),
        "theoretical_peak": round(theoretical_with_peak, 1),
        "db_limit_per_instance": db_limit_per_instance,
        "db_type": db_type,
    }


def render_go_code(r: dict, args) -> str:
    """生成可直接使用的 Go 配置代码"""
    code = f'''// ── GORM 连接池推荐配置 ─────────────────────────────────────────────────────
// 输入参数:
//   QPS: {args.qps}  |  平均延迟: {args.avg_latency_ms}ms
//   DB最大连接: {args.db_max_conn}  |  应用实例数: {args.app_instances}
//   峰值倍数: {args.peak_multiplier}x  |  DB类型: {args.db_type}
//
// 计算过程:
//   理论最小 (Little's Law): {r["theoretical_min"]} 个连接
//   峰值估算 ({args.peak_multiplier}x):  {r["theoretical_peak"]} 个连接
//   DB侧每实例上限:         {r["db_limit_per_instance"]} 个连接
// ─────────────────────────────────────────────────────────────────────────────

sqlDB, err := db.DB()
if err != nil {{
    panic(err)
}}

sqlDB.SetMaxOpenConns({r["max_open"]})                                  // 最大连接数
sqlDB.SetMaxIdleConns({r["max_idle"]})                                   // 空闲连接池 (~{round(args.idle_ratio*100)}% of MaxOpen)
sqlDB.SetConnMaxLifetime({r["conn_lifetime_s"]} * time.Second)          // 连接存活 {args.conn_lifetime_min}min，防 DB 侧主动断开
sqlDB.SetConnMaxIdleTime({r["conn_idle_timeout_s"]} * time.Second)      // 空闲连接 {r["conn_idle_timeout_s"]//60}min 后回收
'''

    # 特定数据库建议
    warnings = []
    if args.db_type == "mysql":
        code += f'''
// MySQL 额外建议:
// 1. 确认 wait_timeout >= {args.conn_lifetime_min * 60 + 300}s (比 ConnMaxLifetime 多 5min)
//    SHOW VARIABLES LIKE 'wait_timeout';
//    SET GLOBAL wait_timeout = {max(args.conn_lifetime_min * 60 + 300, 3600)};
// 2. 开启 interpolateParams=true 减少 round-trip (简单场景):
//    dsn += "&interpolateParams=true"
// 3. 连接串加超时保护:
//    dsn += "&timeout=5s&readTimeout=30s&writeTimeout=30s"
'''
    elif args.db_type == "postgres":
        code += f'''
// PostgreSQL 额外建议:
// 1. pg 默认 max_connections=100，确认: SHOW max_connections;
// 2. 使用 pgBouncer 做连接池代理可大幅提升连接复用率
// 3. DSN 加超时: "connect_timeout=5 statement_timeout=30000"
'''
    elif args.db_type == "sqlite":
        code += '''
// SQLite 注意:
// SQLite 是单写模式，MaxOpenConns 应设为 1（写）+ N（读，WAL模式下）
// WAL 模式下读写可并行:
//   db.Exec("PRAGMA journal_mode=WAL")
sqlDB.SetMaxOpenConns(1)   // 覆盖上面的值，SQLite 写操作串行
'''

    # 健康检查代码
    code += '''
// 连接池健康监控（可接入 Prometheus）
go func() {
    ticker := time.NewTicker(30 * time.Second)
    for range ticker.C {
        stats := sqlDB.Stats()
        log.Printf("DB pool: open=%d idle=%d inUse=%d waitCount=%d",
            stats.OpenConnections,
            stats.Idle,
            stats.InUse,
            stats.WaitCount,
        )
        // 告警条件: InUse 持续接近 MaxOpenConns
        if stats.InUse >= stats.MaxOpenConnections*9/10 {
            log.Warn("DB connection pool near capacity!")
        }
    }
}()
'''

    # 调优建议
    tips = []
    if r["max_open"] == r["db_limit_per_instance"]:
        tips.append(f"⚠️  连接数受 DB 侧限制（{r['db_limit_per_instance']}），理论需求更高。建议扩容 DB max_connections 或增加只读副本")
    if r["theoretical_peak"] > r["db_limit_per_instance"] * 1.5:
        tips.append(f"🔴 峰值需求 ({r['theoretical_peak']}) 远超 DB 侧限制，强烈建议添加读写分离 + 缓存层")
    if args.avg_latency_ms > 100:
        tips.append(f"🟡 平均延迟 {args.avg_latency_ms}ms 偏高，先排查慢 SQL（开启 SlowThreshold=100ms 日志），再做连接池调优")
    if args.app_instances == 1:
        tips.append("ℹ️  当前单实例部署，上线后水平扩展时需同步调小每实例 MaxOpenConns")

    if tips:
        code += "\n// ── 调优建议 ──────────────────────────────────────────────\n"
        for tip in tips:
            code += f"// {tip}\n"

    return code



def render_health_check(result: dict) -> str:
    """生成连接池健康检查代码模板"""
    return f"""
// ── 连接池健康检查（自动生成）──────────────────────────────────────
// 建议将以下代码集成到 /health 端点和定时监控任务中

func DBHealthCheck(db *gorm.DB) error {{
\tsqlDB, err := db.DB()
\tif err != nil {{
\t\treturn fmt.Errorf("get sql.DB failed: %w", err)
\t}}
\tctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
\tdefer cancel()
\treturn sqlDB.PingContext(ctx)
}}

// 定时打印连接池指标（建议每 30s 执行一次）
func StartPoolMonitor(db *gorm.DB, interval time.Duration) {{
\tgo func() {{
\t\tticker := time.NewTicker(interval)
\t\tfor range ticker.C {{
\t\t\tsqlDB, _ := db.DB()
\t\t\tstats := sqlDB.Stats()
\t\t\t// 连接池使用率告警阈值: {int(result['max_open'] * 0.9)} (90% of MaxOpen={result['max_open']})
\t\t\tif stats.InUse >= {int(result['max_open'] * 0.9)} {{
\t\t\t\tlog.Warn("db pool near exhaustion",
\t\t\t\t\t"in_use", stats.InUse, "max_open", {result['max_open']})
\t\t\t}}
\t\t\tlog.Debug("db pool stats",
\t\t\t\t"open", stats.OpenConnections,
\t\t\t\t"in_use", stats.InUse,
\t\t\t\t"idle", stats.Idle,
\t\t\t\t"wait_count", stats.WaitCount,
\t\t\t\t"wait_duration", stats.WaitDuration,
\t\t\t)
\t\t}}
\t}}()
}}
"""

def main():
    parser = argparse.ArgumentParser(description="GORM 连接池参数顾问")
    parser.add_argument("--qps", type=float, required=True, help="目标 QPS（数据库操作次数/秒）")
    parser.add_argument("--avg-latency-ms", type=float, default=20, help="平均 DB 操作延迟 ms（默认 20）")
    parser.add_argument("--db-max-conn", type=int, default=200, help="DB 服务器最大连接数（默认 200）")
    parser.add_argument("--app-instances", type=int, default=1, help="应用实例数（默认 1）")
    parser.add_argument("--db-type", choices=["mysql", "postgres", "sqlite"], default="mysql")
    parser.add_argument("--peak-multiplier", type=float, default=2.0, help="峰值倍数（默认 2x）")
    parser.add_argument("--idle-ratio", type=float, default=0.25, help="空闲连接比例（默认 0.25）")
    parser.add_argument("--conn-lifetime-min", type=int, default=60, help="连接最大存活分钟数（默认 60）")

    args = parser.parse_args()

    if args.qps <= 0:
        print("❌ QPS 必须大于 0", file=sys.stderr)
        sys.exit(1)
    if args.avg_latency_ms <= 0:
        print("❌ avg-latency-ms 必须大于 0", file=sys.stderr)
        sys.exit(1)

    result = calculate_pool(
        qps=args.qps,
        avg_latency_ms=args.avg_latency_ms,
        db_max_conn=args.db_max_conn,
        app_instances=args.app_instances,
        db_type=args.db_type,
        peak_multiplier=args.peak_multiplier,
        idle_ratio=args.idle_ratio,
        conn_lifetime_min=args.conn_lifetime_min,
    )

    print(render_go_code(result, args))
    print(render_health_check(result))

    # 打印摘要表
    print("// ── 参数摘要 ───────────────────────────────────────────────")
    print(f"// MaxOpenConns      = {result['max_open']}")
    print(f"// MaxIdleConns      = {result['max_idle']}")
    print(f"// ConnMaxLifetime   = {result['conn_lifetime_s']}s")
    print(f"// ConnMaxIdleTime   = {result['conn_idle_timeout_s']}s")


if __name__ == "__main__":
    main()
