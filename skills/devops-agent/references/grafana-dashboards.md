# Grafana Dashboard JSON 模板

> DevOps Agent monitor 命令使用的 Grafana dashboard 模板。
> 通过 Grafana API 导入：`POST /api/dashboards/db`

---

## 1. 系统资源概览（node_exporter）

适用于所有服务器，展示 CPU、内存、磁盘、网络核心指标。

```json
{
  "dashboard": {
    "id": null,
    "uid": "system-overview",
    "title": "系统资源概览",
    "tags": ["devops-agent", "system", "node-exporter"],
    "timezone": "browser",
    "refresh": "30s",
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "panels": [
      {
        "id": 1,
        "title": "CPU 使用率",
        "type": "timeseries",
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 },
        "targets": [
          {
            "expr": "100 - (avg by(instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "{{instance}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "max": 100,
            "thresholds": {
              "steps": [
                { "color": "green", "value": null },
                { "color": "yellow", "value": 60 },
                { "color": "red", "value": 80 }
              ]
            }
          }
        }
      },
      {
        "id": 2,
        "title": "内存使用率",
        "type": "timeseries",
        "gridPos": { "h": 8, "w": 12, "x": 12, "y": 0 },
        "targets": [
          {
            "expr": "(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100",
            "legendFormat": "{{instance}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "max": 100,
            "thresholds": {
              "steps": [
                { "color": "green", "value": null },
                { "color": "yellow", "value": 70 },
                { "color": "red", "value": 90 }
              ]
            }
          }
        }
      },
      {
        "id": 3,
        "title": "磁盘使用率",
        "type": "gauge",
        "gridPos": { "h": 8, "w": 8, "x": 0, "y": 8 },
        "targets": [
          {
            "expr": "(1 - node_filesystem_avail_bytes{mountpoint=\"/\"} / node_filesystem_size_bytes{mountpoint=\"/\"}) * 100",
            "legendFormat": "{{mountpoint}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "max": 100,
            "thresholds": {
              "steps": [
                { "color": "green", "value": null },
                { "color": "yellow", "value": 70 },
                { "color": "red", "value": 85 }
              ]
            }
          }
        }
      },
      {
        "id": 4,
        "title": "网络流量",
        "type": "timeseries",
        "gridPos": { "h": 8, "w": 8, "x": 8, "y": 8 },
        "targets": [
          {
            "expr": "rate(node_network_receive_bytes_total{device!~\"lo|veth.*|docker.*|br-.*\"}[5m])",
            "legendFormat": "接收 {{device}}"
          },
          {
            "expr": "rate(node_network_transmit_bytes_total{device!~\"lo|veth.*|docker.*|br-.*\"}[5m])",
            "legendFormat": "发送 {{device}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "Bps"
          }
        }
      },
      {
        "id": 5,
        "title": "系统负载",
        "type": "timeseries",
        "gridPos": { "h": 8, "w": 8, "x": 16, "y": 8 },
        "targets": [
          {
            "expr": "node_load1",
            "legendFormat": "1 分钟"
          },
          {
            "expr": "node_load5",
            "legendFormat": "5 分钟"
          },
          {
            "expr": "node_load15",
            "legendFormat": "15 分钟"
          }
        ]
      },
      {
        "id": 6,
        "title": "磁盘 I/O",
        "type": "timeseries",
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 16 },
        "targets": [
          {
            "expr": "rate(node_disk_read_bytes_total[5m])",
            "legendFormat": "读取 {{device}}"
          },
          {
            "expr": "rate(node_disk_written_bytes_total[5m])",
            "legendFormat": "写入 {{device}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "Bps"
          }
        }
      },
      {
        "id": 7,
        "title": "打开文件数",
        "type": "stat",
        "gridPos": { "h": 4, "w": 6, "x": 12, "y": 16 },
        "targets": [
          {
            "expr": "node_filefd_allocated",
            "legendFormat": "已分配"
          }
        ]
      },
      {
        "id": 8,
        "title": "运行时间",
        "type": "stat",
        "gridPos": { "h": 4, "w": 6, "x": 18, "y": 16 },
        "targets": [
          {
            "expr": "time() - node_boot_time_seconds",
            "legendFormat": "uptime"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "s"
          }
        }
      }
    ]
  },
  "overwrite": true
}
```

---

## 2. Node.js 应用监控（prom-client）

需要应用集成 prom-client 并暴露 `/metrics` 端点。

```json
{
  "dashboard": {
    "id": null,
    "uid": "nodejs-app",
    "title": "Node.js 应用监控",
    "tags": ["devops-agent", "nodejs", "application"],
    "timezone": "browser",
    "refresh": "15s",
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "panels": [
      {
        "id": 1,
        "title": "HTTP 请求速率",
        "type": "timeseries",
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 },
        "targets": [
          {
            "expr": "rate(http_request_duration_seconds_count[5m])",
            "legendFormat": "{{method}} {{route}} {{status_code}}"
          }
        ],
        "fieldConfig": {
          "defaults": { "unit": "reqps" }
        }
      },
      {
        "id": 2,
        "title": "HTTP 请求延迟 (P95)",
        "type": "timeseries",
        "gridPos": { "h": 8, "w": 12, "x": 12, "y": 0 },
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P95"
          },
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P50"
          }
        ],
        "fieldConfig": {
          "defaults": { "unit": "s" }
        }
      },
      {
        "id": 3,
        "title": "Node.js 堆内存",
        "type": "timeseries",
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 8 },
        "targets": [
          {
            "expr": "nodejs_heap_size_used_bytes",
            "legendFormat": "已使用"
          },
          {
            "expr": "nodejs_heap_size_total_bytes",
            "legendFormat": "总量"
          }
        ],
        "fieldConfig": {
          "defaults": { "unit": "bytes" }
        }
      },
      {
        "id": 4,
        "title": "Event Loop 延迟",
        "type": "timeseries",
        "gridPos": { "h": 8, "w": 12, "x": 12, "y": 8 },
        "targets": [
          {
            "expr": "nodejs_eventloop_lag_seconds",
            "legendFormat": "lag"
          }
        ],
        "fieldConfig": {
          "defaults": { "unit": "s" }
        }
      },
      {
        "id": 5,
        "title": "活跃连接数",
        "type": "stat",
        "gridPos": { "h": 4, "w": 6, "x": 0, "y": 16 },
        "targets": [
          {
            "expr": "nodejs_active_handles_total",
            "legendFormat": "handles"
          }
        ]
      },
      {
        "id": 6,
        "title": "GC 暂停时间",
        "type": "timeseries",
        "gridPos": { "h": 8, "w": 12, "x": 6, "y": 16 },
        "targets": [
          {
            "expr": "rate(nodejs_gc_duration_seconds_sum[5m])",
            "legendFormat": "{{kind}}"
          }
        ],
        "fieldConfig": {
          "defaults": { "unit": "s" }
        }
      }
    ]
  },
  "overwrite": true
}
```

---

## 3. PostgreSQL 监控（postgres_exporter）

```json
{
  "dashboard": {
    "id": null,
    "uid": "postgresql-monitor",
    "title": "PostgreSQL 监控",
    "tags": ["devops-agent", "postgresql", "database"],
    "timezone": "browser",
    "refresh": "30s",
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "panels": [
      {
        "id": 1,
        "title": "活跃连接数",
        "type": "timeseries",
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 },
        "targets": [
          {
            "expr": "pg_stat_activity_count",
            "legendFormat": "{{datname}} - {{state}}"
          }
        ]
      },
      {
        "id": 2,
        "title": "数据库大小",
        "type": "bargauge",
        "gridPos": { "h": 8, "w": 12, "x": 12, "y": 0 },
        "targets": [
          {
            "expr": "pg_database_size_bytes",
            "legendFormat": "{{datname}}"
          }
        ],
        "fieldConfig": {
          "defaults": { "unit": "bytes" }
        }
      },
      {
        "id": 3,
        "title": "事务速率",
        "type": "timeseries",
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 8 },
        "targets": [
          {
            "expr": "rate(pg_stat_database_xact_commit{datname!=\"\"}[5m])",
            "legendFormat": "提交 {{datname}}"
          },
          {
            "expr": "rate(pg_stat_database_xact_rollback{datname!=\"\"}[5m])",
            "legendFormat": "回滚 {{datname}}"
          }
        ],
        "fieldConfig": {
          "defaults": { "unit": "ops" }
        }
      },
      {
        "id": 4,
        "title": "缓存命中率",
        "type": "gauge",
        "gridPos": { "h": 8, "w": 12, "x": 12, "y": 8 },
        "targets": [
          {
            "expr": "pg_stat_database_blks_hit{datname!=\"\"} / (pg_stat_database_blks_hit{datname!=\"\"} + pg_stat_database_blks_read{datname!=\"\"}) * 100",
            "legendFormat": "{{datname}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "max": 100,
            "thresholds": {
              "steps": [
                { "color": "red", "value": null },
                { "color": "yellow", "value": 90 },
                { "color": "green", "value": 99 }
              ]
            }
          }
        }
      },
      {
        "id": 5,
        "title": "表膨胀 (Dead Tuples)",
        "type": "timeseries",
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 16 },
        "targets": [
          {
            "expr": "pg_stat_user_tables_n_dead_tup",
            "legendFormat": "{{relname}}"
          }
        ]
      },
      {
        "id": 6,
        "title": "慢查询数",
        "type": "stat",
        "gridPos": { "h": 8, "w": 12, "x": 12, "y": 16 },
        "targets": [
          {
            "expr": "pg_stat_activity_count{state=\"active\"} and on() (pg_stat_activity_max_tx_duration > 5)",
            "legendFormat": "长事务"
          }
        ]
      },
      {
        "id": 7,
        "title": "复制延迟",
        "type": "timeseries",
        "gridPos": { "h": 8, "w": 24, "x": 0, "y": 24 },
        "targets": [
          {
            "expr": "pg_replication_lag",
            "legendFormat": "{{instance}}"
          }
        ],
        "fieldConfig": {
          "defaults": { "unit": "s" }
        }
      }
    ]
  },
  "overwrite": true
}
```

---

## 使用方式

### 通过 Grafana API 导入

```bash
# 将上述 JSON 保存为文件，然后通过 API 导入
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @dashboard.json
```

### 通过 Grafana UI 导入

1. 打开 Grafana → Dashboards → Import
2. 粘贴 JSON 内容
3. 选择 Prometheus 数据源
4. 点击 Import

### 社区 Dashboard 推荐

如果需要更完善的 dashboard，可以从 Grafana 社区导入：

| Dashboard | ID | 说明 |
|-----------|-----|------|
| Node Exporter Full | 1860 | 系统资源全面监控 |
| PostgreSQL Database | 9628 | PostgreSQL 详细监控 |
| MySQL Overview | 7362 | MySQL 概览 |
| MongoDB Overview | 2583 | MongoDB 概览 |
| Nginx | 12708 | Nginx 流量监控 |
| Docker | 893 | Docker 容器监控 |

```bash
# 通过 ID 导入社区 dashboard
curl -X POST http://admin:admin@localhost:3000/api/dashboards/import \
  -H "Content-Type: application/json" \
  -d '{
    "dashboard": { "id": 1860 },
    "overwrite": true,
    "inputs": [{ "name": "DS_PROMETHEUS", "type": "datasource", "pluginId": "prometheus", "value": "Prometheus" }]
  }'
```
