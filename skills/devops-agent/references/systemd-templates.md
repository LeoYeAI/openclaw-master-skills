# Systemd Service 文件模板集合

> DevOps Agent 部署命令使用的 systemd unit file 模板。
> 所有模板使用 `{{变量名}}` 占位符，由 Agent 在部署时替换。

---

## 1. Node.js 应用

```ini
[Unit]
Description={{APP_NAME}} - Node.js Application
Documentation=https://github.com/{{REPO_OWNER}}/{{APP_NAME}}
After=network.target
Wants=network-online.target

[Service]
Type=simple
User={{SERVICE_USER:-www-data}}
Group={{SERVICE_GROUP:-www-data}}
WorkingDirectory={{DEPLOY_DIR}}

# 环境变量
Environment=NODE_ENV=production
Environment=PORT={{PORT:-3000}}
EnvironmentFile=-{{DEPLOY_DIR}}/.env

# 启动命令
ExecStart=/usr/bin/node {{ENTRY_POINT:-dist/index.js}}

# 重启策略
Restart=always
RestartSec=5
StartLimitBurst=5
StartLimitIntervalSec=60

# 安全加固
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths={{DEPLOY_DIR}}/logs {{DEPLOY_DIR}}/uploads
PrivateTmp=true

# 资源限制
MemoryMax={{MEMORY_LIMIT:-512M}}
CPUQuota={{CPU_QUOTA:-100%}}
LimitNOFILE=65535

# 日志
StandardOutput=journal
StandardError=journal
SyslogIdentifier={{APP_NAME}}

[Install]
WantedBy=multi-user.target
```

---

## 2. Python 应用（Gunicorn / Uvicorn）

### Gunicorn（Django / Flask）

```ini
[Unit]
Description={{APP_NAME}} - Python Gunicorn Application
After=network.target

[Service]
Type=notify
User={{SERVICE_USER:-www-data}}
Group={{SERVICE_GROUP:-www-data}}
WorkingDirectory={{DEPLOY_DIR}}

EnvironmentFile=-{{DEPLOY_DIR}}/.env

# Gunicorn 启动
ExecStart={{DEPLOY_DIR}}/.venv/bin/gunicorn \
    --workers {{WORKERS:-4}} \
    --worker-class {{WORKER_CLASS:-gthread}} \
    --threads {{THREADS:-2}} \
    --bind 127.0.0.1:{{PORT:-8000}} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    {{WSGI_APP:-app:app}}

ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=30

Restart=always
RestartSec=5

# 安全加固
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths={{DEPLOY_DIR}}/logs {{DEPLOY_DIR}}/media
PrivateTmp=true

MemoryMax={{MEMORY_LIMIT:-1G}}
LimitNOFILE=65535

StandardOutput=journal
StandardError=journal
SyslogIdentifier={{APP_NAME}}

[Install]
WantedBy=multi-user.target
```

### Uvicorn（FastAPI / Starlette）

```ini
[Unit]
Description={{APP_NAME}} - Python Uvicorn Application
After=network.target

[Service]
Type=simple
User={{SERVICE_USER:-www-data}}
Group={{SERVICE_GROUP:-www-data}}
WorkingDirectory={{DEPLOY_DIR}}

EnvironmentFile=-{{DEPLOY_DIR}}/.env

ExecStart={{DEPLOY_DIR}}/.venv/bin/uvicorn \
    --host 127.0.0.1 \
    --port {{PORT:-8000}} \
    --workers {{WORKERS:-4}} \
    --loop uvloop \
    --http httptools \
    --access-log \
    {{ASGI_APP:-app.main:app}}

Restart=always
RestartSec=5

NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths={{DEPLOY_DIR}}/logs
PrivateTmp=true

MemoryMax={{MEMORY_LIMIT:-1G}}
LimitNOFILE=65535

StandardOutput=journal
StandardError=journal
SyslogIdentifier={{APP_NAME}}

[Install]
WantedBy=multi-user.target
```

---

## 3. Go 应用

```ini
[Unit]
Description={{APP_NAME}} - Go Application
After=network.target

[Service]
Type=simple
User={{SERVICE_USER:-www-data}}
Group={{SERVICE_GROUP:-www-data}}
WorkingDirectory={{DEPLOY_DIR}}

EnvironmentFile=-{{DEPLOY_DIR}}/.env

ExecStart={{DEPLOY_DIR}}/{{BINARY_NAME:-app}}

Restart=always
RestartSec=5
StartLimitBurst=5
StartLimitIntervalSec=60

# Go 应用通常编译为静态二进制，安全加固更严格
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths={{DEPLOY_DIR}}/data {{DEPLOY_DIR}}/logs
PrivateTmp=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true

MemoryMax={{MEMORY_LIMIT:-256M}}
LimitNOFILE=65535

StandardOutput=journal
StandardError=journal
SyslogIdentifier={{APP_NAME}}

[Install]
WantedBy=multi-user.target
```

---

## 4. Rust 应用

```ini
[Unit]
Description={{APP_NAME}} - Rust Application
After=network.target

[Service]
Type=simple
User={{SERVICE_USER:-www-data}}
Group={{SERVICE_GROUP:-www-data}}
WorkingDirectory={{DEPLOY_DIR}}

EnvironmentFile=-{{DEPLOY_DIR}}/.env
Environment=RUST_LOG={{RUST_LOG:-info}}

ExecStart={{DEPLOY_DIR}}/target/release/{{BINARY_NAME:-app}}

Restart=always
RestartSec=5

NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths={{DEPLOY_DIR}}/data {{DEPLOY_DIR}}/logs
PrivateTmp=true
ProtectKernelTunables=true
ProtectKernelModules=true

MemoryMax={{MEMORY_LIMIT:-256M}}
LimitNOFILE=65535

StandardOutput=journal
StandardError=journal
SyslogIdentifier={{APP_NAME}}

[Install]
WantedBy=multi-user.target
```

---

## 5. 通用后台服务（任意语言）

```ini
[Unit]
Description={{APP_NAME}} Service
After=network.target
{{AFTER_DEPS}}

[Service]
Type={{SERVICE_TYPE:-simple}}
User={{SERVICE_USER:-www-data}}
Group={{SERVICE_GROUP:-www-data}}
WorkingDirectory={{DEPLOY_DIR}}

EnvironmentFile=-{{DEPLOY_DIR}}/.env

ExecStartPre={{PRE_START_CMD}}
ExecStart={{START_CMD}}
ExecStartPost={{POST_START_CMD}}
ExecStop={{STOP_CMD:-/bin/kill -s TERM $MAINPID}}
ExecReload=/bin/kill -s HUP $MAINPID

Restart=always
RestartSec=5
TimeoutStartSec=30
TimeoutStopSec=30

NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths={{DEPLOY_DIR}}
PrivateTmp=true

MemoryMax={{MEMORY_LIMIT:-512M}}
CPUQuota={{CPU_QUOTA:-100%}}
LimitNOFILE=65535

StandardOutput=journal
StandardError=journal
SyslogIdentifier={{APP_NAME}}

[Install]
WantedBy=multi-user.target
```

---

## 6. Prometheus

```ini
[Unit]
Description=Prometheus Monitoring System
Documentation=https://prometheus.io/docs/
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=prometheus
Group=prometheus
WorkingDirectory=/var/lib/prometheus

ExecStart=/usr/local/bin/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/var/lib/prometheus/data \
    --storage.tsdb.retention.time={{RETENTION:-15d}} \
    --web.listen-address=0.0.0.0:9090 \
    --web.enable-lifecycle

ExecReload=/bin/kill -s HUP $MAINPID
TimeoutStopSec=30

Restart=always
RestartSec=5

NoNewPrivileges=true
ProtectSystem=full
ProtectHome=true
ReadWritePaths=/var/lib/prometheus
LimitNOFILE=65535

StandardOutput=journal
StandardError=journal
SyslogIdentifier=prometheus

[Install]
WantedBy=multi-user.target
```

---

## 7. node_exporter

```ini
[Unit]
Description=Prometheus Node Exporter
After=network.target

[Service]
Type=simple
User=node_exporter
Group=node_exporter

ExecStart=/usr/local/bin/node_exporter \
    --collector.systemd \
    --collector.processes \
    --web.listen-address=:9100

Restart=always
RestartSec=5

NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true

StandardOutput=journal
StandardError=journal
SyslogIdentifier=node_exporter

[Install]
WantedBy=multi-user.target
```

---

## 常用管理命令

```bash
# 部署后启用并启动服务
sudo systemctl daemon-reload
sudo systemctl enable {{APP_NAME}}
sudo systemctl start {{APP_NAME}}

# 查看状态
sudo systemctl status {{APP_NAME}}

# 查看日志
sudo journalctl -u {{APP_NAME}} -f              # 实时跟踪
sudo journalctl -u {{APP_NAME}} --since today    # 今日日志
sudo journalctl -u {{APP_NAME}} -n 100           # 最近 100 行

# 重启/重载
sudo systemctl restart {{APP_NAME}}
sudo systemctl reload {{APP_NAME}}    # 仅支持 Type=notify 或有 ExecReload

# 停止并禁用
sudo systemctl stop {{APP_NAME}}
sudo systemctl disable {{APP_NAME}}
```

---

## 变量说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `{{APP_NAME}}` | 应用/服务名称 | - |
| `{{DEPLOY_DIR}}` | 部署目录 | - |
| `{{PORT}}` | 监听端口 | 各模板不同 |
| `{{SERVICE_USER}}` | 运行用户 | `www-data` |
| `{{SERVICE_GROUP}}` | 运行组 | `www-data` |
| `{{MEMORY_LIMIT}}` | 内存限制 | 各模板不同 |
| `{{CPU_QUOTA}}` | CPU 配额 | `100%` |
| `{{WORKERS}}` | 工作进程数 | `4` |
| `{{ENTRY_POINT}}` | 入口文件 | 各模板不同 |
| `{{BINARY_NAME}}` | 二进制名称 | `app` |
