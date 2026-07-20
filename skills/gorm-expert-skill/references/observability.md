# GORM 监控与可观测性

> 覆盖 Prometheus 指标采集、慢查询日志、OpenTelemetry 链路追踪、Grafana 告警

---

## 1. Prometheus 指标采集

### 1.1 安装依赖

```bash
go get gorm.io/plugin/prometheus
go get github.com/prometheus/client_golang/prometheus
go get github.com/prometheus/client_golang/prometheus/promhttp
```

### 1.2 注册插件

```go
import "gorm.io/plugin/prometheus"

db.Use(prometheus.New(prometheus.Config{
    DBName:          "myapp_db",   // 指标标签中的 DB 名称
    RefreshInterval: 15,           // 每 15 秒刷新一次指标
    StartServer:     false,        // 不启动独立 HTTP 服务（使用现有的）
    HTTPServerPort:  0,
    MetricsCollector: []prometheus.MetricsCollector{
        &prometheus.MySQL{
            VariableNames: []string{
                "Threads_running",      // 当前运行线程数
                "Slow_queries",         // 累计慢查询数
                "Innodb_row_lock_waits",// 行锁等待次数
            },
        },
    },
}))

// 在现有 HTTP 服务暴露 /metrics
http.Handle("/metrics", promhttp.Handler())
```

### 1.3 自动暴露的连接池指标

| 指标名 | 说明 |
|--------|------|
| `go_sql_stats_connections_max_open` | 最大连接数 (MaxOpenConns) |
| `go_sql_stats_connections_open` | 当前打开连接数 |
| `go_sql_stats_connections_in_use` | 使用中连接数 |
| `go_sql_stats_connections_idle` | 空闲连接数 |
| `go_sql_stats_connections_wait_total` | 等待连接次数（累计） |
| `go_sql_stats_connections_wait_duration_seconds_total` | 等待连接总时长 |
| `go_sql_stats_connections_max_idle_closed_total` | 因超出 MaxIdle 被关闭的连接数 |
| `go_sql_stats_connections_max_lifetime_closed_total` | 因超出 MaxLifetime 被关闭的连接数 |

---

## 2. 慢查询日志

### 2.1 内置 Logger（快速开启）

```go
import (
    "gorm.io/gorm/logger"
    "log"
    "os"
    "time"
)

slowLogger := logger.New(
    log.New(os.Stdout, "\r\n", log.LstdFlags),
    logger.Config{
        SlowThreshold:             200 * time.Millisecond, // 超过 200ms 打印
        LogLevel:                  logger.Warn,
        IgnoreRecordNotFoundError: true,   // 忽略 ErrRecordNotFound
        Colorful:                  false,  // 生产环境关闭颜色
    },
)

db, _ := gorm.Open(mysql.Open(dsn), &gorm.Config{Logger: slowLogger})
```

### 2.2 自定义慢查询回调（写入告警系统）

```go
db.Callback().Query().After("gorm:query").Register("slow_query_alert", func(db *gorm.DB) {
    if db.Error != nil {
        return
    }
    elapsed := db.Statement.DB.Statement.ConnPool.(*sql.DB) // 从 context 获取耗时
    // 更简洁方式：在自定义 Logger 中实现
})

// 推荐：实现 logger.Interface 接口
type SlackSlowLogger struct {
    logger.Interface
    SlackWebhook string
    Threshold    time.Duration
}

func (l *SlackSlowLogger) Trace(ctx context.Context, begin time.Time,
    fc func() (sql string, rowsAffected int64), err error) {

    elapsed := time.Since(begin)
    sql, rows := fc()

    if elapsed > l.Threshold {
        // 发送告警到 Slack / PagerDuty / 钉钉
        go l.sendAlert(ctx, sql, elapsed, rows)
    }

    // 继续正常日志
    l.Interface.Trace(ctx, begin, fc, err)
}
```

### 2.3 结构化慢查询日志（适配 ELK / Loki）

```go
import "go.uber.org/zap"

type ZapGormLogger struct {
    ZapLogger     *zap.Logger
    SlowThreshold time.Duration
    LogLevel      logger.LogLevel
}

func (l *ZapGormLogger) Trace(ctx context.Context, begin time.Time,
    fc func() (string, int64), err error) {

    elapsed := time.Since(begin)
    sql, rows := fc()

    fields := []zap.Field{
        zap.String("sql", sql),
        zap.Int64("rows", rows),
        zap.Duration("elapsed", elapsed),
    }

    switch {
    case err != nil && !errors.Is(err, gorm.ErrRecordNotFound):
        l.ZapLogger.Error("gorm error", append(fields, zap.Error(err))...)
    case elapsed > l.SlowThreshold:
        l.ZapLogger.Warn("slow query", fields...)
    default:
        l.ZapLogger.Debug("query", fields...)
    }
}
```

---

## 3. OpenTelemetry 链路追踪

### 3.1 安装依赖

```bash
go get github.com/uptrace/opentelemetry-go-extra/otelgorm
go get go.opentelemetry.io/otel
go get go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp
```

### 3.2 初始化 OTel + 注册 GORM 插件

```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"
    "go.opentelemetry.io/otel/sdk/trace"
    "github.com/uptrace/opentelemetry-go-extra/otelgorm"
)

// 初始化 Tracer Provider
func initTracer(ctx context.Context) (*trace.TracerProvider, error) {
    exporter, err := otlptracehttp.New(ctx,
        otlptracehttp.WithEndpoint("otel-collector:4318"),
        otlptracehttp.WithInsecure(),
    )
    if err != nil {
        return nil, err
    }
    tp := trace.NewTracerProvider(
        trace.WithBatcher(exporter),
        trace.WithResource(resource.NewWithAttributes(
            semconv.SchemaURL,
            semconv.ServiceName("myapp"),
        )),
    )
    otel.SetTracerProvider(tp)
    return tp, nil
}

// 注册 GORM 插件
db.Use(otelgorm.NewPlugin(
    otelgorm.WithDBName("myapp"),
    otelgorm.WithAttributes(
        attribute.String("env", "production"),
    ),
))

// 使用时需传入携带 trace context 的 ctx
ctx, span := tracer.Start(ctx, "create-order")
defer span.End()
db.WithContext(ctx).Create(&order) // 自动生成子 span
```

### 3.3 生成的 Span 属性

| 属性 | 示例值 |
|------|--------|
| `db.system` | `mysql` |
| `db.name` | `myapp` |
| `db.statement` | `SELECT * FROM orders WHERE user_id = ?` |
| `db.operation` | `SELECT` |
| `net.peer.name` | `127.0.0.1` |
| `net.peer.port` | `3306` |

---

## 4. Prometheus 告警规则

```yaml
# prometheus/rules/gorm.yml
groups:
  - name: gorm_database
    rules:
      # 慢查询率告警
      - alert: HighSlowQueryRate
        expr: rate(mysql_global_status_slow_queries[5m]) > 10
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "慢查询率过高 ({{ $value }}/s)"

      # 连接池耗尽告警
      - alert: DBConnectionPoolExhausted
        expr: |
          go_sql_stats_connections_in_use /
          go_sql_stats_connections_max_open > 0.9
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "DB 连接池使用率超过 90%"

      # 连接等待时间告警
      - alert: DBConnectionWaitHigh
        expr: |
          rate(go_sql_stats_connections_wait_duration_seconds_total[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "DB 连接等待时间过长"

      # 错误率告警
      - alert: DBErrorRateHigh
        expr: rate(db_errors_total[5m]) > 1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "DB 错误率异常 ({{ $value }}/s)"
```

---

## 5. Grafana 仪表盘配置

推荐使用社区模板 **Dashboard ID: 14057**（Go SQL Stats）。

手动配置核心面板：

```json
// 连接池使用率面板（PromQL）
{
  "title": "DB 连接池使用率",
  "targets": [
    {
      "expr": "go_sql_stats_connections_in_use / go_sql_stats_connections_max_open",
      "legendFormat": "使用率"
    },
    {
      "expr": "go_sql_stats_connections_idle / go_sql_stats_connections_max_open",
      "legendFormat": "空闲率"
    }
  ]
}
```

---

## 6. 连接池健康检查

```go
// 定期检查 DB 连接健康
func dbHealthCheck(db *gorm.DB) error {
    sqlDB, err := db.DB()
    if err != nil {
        return fmt.Errorf("get sql.DB failed: %w", err)
    }
    ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
    defer cancel()
    return sqlDB.PingContext(ctx)
}

// 在 HTTP /health 端点暴露
http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
    if err := dbHealthCheck(db); err != nil {
        w.WriteHeader(http.StatusServiceUnavailable)
        json.NewEncoder(w).Encode(map[string]string{"db": err.Error()})
        return
    }
    w.WriteHeader(http.StatusOK)
    json.NewEncoder(w).Encode(map[string]string{"db": "ok"})
})

// 暴露连接池状态到日志（定时任务）
go func() {
    ticker := time.NewTicker(30 * time.Second)
    for range ticker.C {
        sqlDB, _ := db.DB()
        stats := sqlDB.Stats()
        log.Info("db pool stats",
            "open", stats.OpenConnections,
            "in_use", stats.InUse,
            "idle", stats.Idle,
            "wait_count", stats.WaitCount,
            "wait_duration", stats.WaitDuration,
        )
    }
}()
```

---

## 7. 日志与追踪关联

将 trace_id 注入到 GORM 日志，方便在 ELK / Loki 中关联：

```go
type TraceAwareLogger struct {
    logger.Interface
}

func (l *TraceAwareLogger) Trace(ctx context.Context, begin time.Time,
    fc func() (string, int64), err error) {

    span := trace.SpanFromContext(ctx)
    if span.IsRecording() {
        traceID := span.SpanContext().TraceID().String()
        // 将 traceID 注入日志字段（配合 zap / logrus）
        ctx = context.WithValue(ctx, "trace_id", traceID)
    }
    l.Interface.Trace(ctx, begin, fc, err)
}
```

---

## 8. pprof 性能剖析

```go
import _ "net/http/pprof"

// 启动 pprof HTTP 服务
go http.ListenAndServe(":6060", nil)

// 采集 30s CPU Profile
// curl http://localhost:6060/debug/pprof/profile?seconds=30 > cpu.prof
// go tool pprof -http=:8080 cpu.prof

// 采集堆内存快照
// curl http://localhost:6060/debug/pprof/heap > heap.prof
// go tool pprof -http=:8080 heap.prof

// 查看 Goroutine 泄露
// curl http://localhost:6060/debug/pprof/goroutine?debug=2
```

> 结合 `bench_template.py` 脚本可自动生成 Benchmark + pprof 集成代码。
