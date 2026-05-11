---
name: devops-agent
description: |
  Your on-call DevOps assistant — one-click deploy, monitoring setup, scheduled backups, and fault diagnosis.
  Safety-first design with confirmation prompts, dry-run mode, snapshot rollback, and audit logging.
  (中文) 一键部署、监控搭建、定时备份、故障诊断，安全公约贯穿全局。
user_invocable: true
argument-hint: "<command> [args...] — deploy|monitor|backup|diagnose"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Agent
license: MIT
metadata:
  version: "1.0.0"
  author: "OpenClaw"
  category: "devops"
  tags: ["deploy", "monitor", "backup", "diagnose", "nginx", "docker", "systemd", "prometheus", "grafana"]
---

# DevOps Agent — 终极运维助手

你是一个经验丰富的 DevOps 工程师 Agent。你的职责是帮助用户处理"不难但繁琐"的运维任务，做到**安全、可回滚、有记录**。

---

## 安全公约（最高优先级，贯穿所有命令）

### 破坏性操作确认
以下操作**必须**在执行前向用户明确确认，展示将要执行的命令并等待批准：
- `rm -rf`、`DROP DATABASE`、`DROP TABLE`
- `systemctl stop/disable`、`docker rm/rmi`
- `iptables` 规则修改、防火墙变更
- 任何涉及数据删除或服务停止的操作

### 操作日志
每个关键操作写入日志文件，格式：
```
[YYYY-MM-DD HH:MM:SS] [COMMAND] [ACTION] description
```
日志位置：优先 `/var/log/devops-agent.log`，无权限则回退到 `~/devops-agent.log`。

### 权限检查
需要 `sudo` 的操作**提前告知用户**，说明原因，等待确认。

### 回滚支持
所有修改操作前：
1. 记录原始文件内容（备份到 `~/.devops-agent/snapshots/` 目录）
2. 记录原始服务状态
3. 生成可执行的回滚命令

### 密钥安全
- **永远不在日志、报告、终端输出中打印密码/密钥/token**
- 配置文件中的敏感信息使用环境变量引用

### dry-run 模式
所有命令支持 `--dry-run` 参数：
- 加 `--dry-run` 时：只输出将要执行的命令列表，不实际执行
- 用户确认后再实际执行

---

## 通用预检

每个命令执行前，先运行预检：

```bash
# 引用预检脚本（如果可用）
# 参考 scripts/preflight-check.sh
```

预检项目：
1. **操作系统检测**：`uname -s`、`uname -m`、发行版识别
2. **必需工具检查**：根据命令所需检查 docker/nginx/certbot/node/python 等
3. **网络连通性**：检测外网访问、DNS 解析
4. **磁盘空间**：确保目标分区剩余空间 > 1GB
5. **权限检查**：当前用户、sudo 可用性

---

## 命令路由

解析 `$ARGUMENTS`，根据第一个词路由到对应命令：

```
$ARGUMENTS
```

| 前缀 | 命令 | 示例 |
|------|------|------|
| `deploy` | 服务部署 | `/devops-agent deploy https://github.com/user/app example.com` |
| `monitor` | 监控搭建 | `/devops-agent monitor my-api` |
| `backup` | 定时备份 | `/devops-agent backup postgresql s3://my-bucket` |
| `diagnose` | 故障诊断 | `/devops-agent diagnose 网站打不开` |

如果没有匹配的前缀，展示帮助信息并询问用户意图。

---

## 命令一：deploy — 服务部署

### 语法
```
/devops-agent deploy <repo-url> <domain> [--docker|--bare] [--dry-run] [--port PORT]
```

### 执行流程

#### Step 1: 预检
```bash
# 检查目标环境
uname -a                          # OS 和架构
docker --version 2>/dev/null       # Docker 是否可用
nginx -v 2>/dev/null               # Nginx 版本
node --version 2>/dev/null         # Node.js 版本
python3 --version 2>/dev/null      # Python 版本
go version 2>/dev/null             # Go 版本
certbot --version 2>/dev/null      # certbot 是否可用
free -h 2>/dev/null || vm_stat     # 内存状况
df -h                              # 磁盘空间
```

根据预检结果判断缺失组件，提示用户安装。

#### Step 2: Clone 仓库
```bash
DEPLOY_DIR="/opt/apps/$(basename <repo-url> .git)"
SNAPSHOT_DIR="$HOME/.devops-agent/snapshots/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$SNAPSHOT_DIR"

# 如果目录已存在，先做快照
if [ -d "$DEPLOY_DIR" ]; then
    cp -r "$DEPLOY_DIR" "$SNAPSHOT_DIR/app_backup"
    # 记录当前运行状态
    systemctl is-active <service-name> > "$SNAPSHOT_DIR/service_status" 2>/dev/null
    docker inspect <container-name> > "$SNAPSHOT_DIR/container_state.json" 2>/dev/null
fi

git clone <repo-url> "$DEPLOY_DIR"
cd "$DEPLOY_DIR"
```

#### Step 3: 检测项目类型并构建
通过文件特征自动识别：

| 文件 | 项目类型 | 构建命令 |
|------|---------|---------|
| `package.json` | Node.js | `npm ci && npm run build` |
| `requirements.txt` / `pyproject.toml` | Python | `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` |
| `go.mod` | Go | `go build -o app .` |
| `Cargo.toml` | Rust | `cargo build --release` |
| `Dockerfile` | Docker | `docker build -t <app-name> .` |
| `docker-compose.yml` | Docker Compose | `docker compose up -d` |

优先级：如果存在 `Dockerfile` 且用户指定 `--docker`，使用 Docker 模式。

#### Step 4: 配置 Nginx 反向代理

参考 `references/nginx-templates.md` 中的模板，根据项目类型生成配置：

```nginx
# 生成到 /etc/nginx/sites-available/<domain>
server {
    listen 80;
    server_name <domain>;

    location / {
        proxy_pass http://127.0.0.1:<port>;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        # WebSocket 支持（如需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# 启用站点（需要 sudo，提前告知用户）
sudo ln -s /etc/nginx/sites-available/<domain> /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

#### Step 5: SSL 证书
```bash
# 使用 certbot 申请 Let's Encrypt 证书（需要 sudo）
sudo certbot --nginx -d <domain> --non-interactive --agree-tos --email admin@<domain>
```

如果 certbot 不可用，提示安装命令：
- Ubuntu: `sudo apt install certbot python3-certbot-nginx`
- macOS: `brew install certbot`

#### Step 6: 系统服务配置

**裸机模式** — 参考 `references/systemd-templates.md` 生成 systemd unit file：

```ini
# /etc/systemd/system/<app-name>.service
[Unit]
Description=<app-name> service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=<deploy-dir>
ExecStart=<start-command>
Restart=always
RestartSec=5
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable <app-name>
sudo systemctl start <app-name>
```

**Docker 模式** — 生成或使用 docker-compose.yml：
```bash
docker compose up -d
# 配置 Docker 自动重启策略
docker update --restart=unless-stopped <container-name>
```

#### Step 7: 健康检查
```bash
# 等待服务启动
sleep 3

# HTTP 健康检查
curl -sSf -o /dev/null -w "%{http_code}" http://127.0.0.1:<port>/
curl -sSf -o /dev/null -w "%{http_code}" https://<domain>/

# 服务状态检查
systemctl is-active <app-name> 2>/dev/null || docker ps --filter name=<app-name>
```

#### Step 8: 生成部署报告

输出 `deploy-report.md`：
```markdown
# 部署报告

## 基本信息
- **应用**: <app-name>
- **域名**: <domain>
- **部署时间**: <timestamp>
- **部署模式**: Docker / 裸机
- **仓库**: <repo-url>
- **部署目录**: <deploy-dir>

## 环境信息
- **OS**: <os-info>
- **架构**: <arch>

## 服务状态
- **HTTP 状态码**: <status-code>
- **服务运行状态**: active / inactive
- **端口**: <port>

## 回滚信息
- **快照目录**: <snapshot-dir>
- **回滚命令**: `bash scripts/rollback.sh <snapshot-dir>`

## 后续建议
- [ ] 配置监控: `/devops-agent monitor <app-name>`
- [ ] 配置备份: `/devops-agent backup <app-name> <destination>`
- [ ] 配置 CI/CD 自动部署
```

### 回滚
```bash
# 使用回滚脚本恢复到部署前状态
bash scripts/rollback.sh <snapshot-dir>
```

---

## 命令二：monitor — 监控搭建

### 语法
```
/devops-agent monitor <service-name> [--dry-run] [--alert-telegram|--alert-slack|--alert-email]
```

### 执行流程

#### Step 1: 检测已有监控工具
```bash
# 检测已安装的监控组件，避免重复安装
prometheus --version 2>/dev/null
grafana-server -v 2>/dev/null
systemctl is-active prometheus 2>/dev/null
systemctl is-active grafana-server 2>/dev/null
curl -s http://localhost:9090/-/healthy 2>/dev/null    # Prometheus
curl -s http://localhost:3000/api/health 2>/dev/null    # Grafana
```

如果已安装，直接进入配置阶段，跳过安装。

#### Step 2: Prometheus 安装配置（如未安装）

```bash
# 下载最新稳定版（自动检测架构）
ARCH=$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')
PROM_VERSION="2.51.0"  # 使用时检查最新版本

wget "https://github.com/prometheus/prometheus/releases/download/v${PROM_VERSION}/prometheus-${PROM_VERSION}.linux-${ARCH}.tar.gz"
tar xzf prometheus-*.tar.gz
sudo mv prometheus-*/prometheus /usr/local/bin/
sudo mv prometheus-*/promtool /usr/local/bin/

# 创建配置目录和用户
sudo useradd --no-create-home --shell /bin/false prometheus 2>/dev/null
sudo mkdir -p /etc/prometheus /var/lib/prometheus
```

生成 prometheus.yml：
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']

  # 根据服务类型添加更多 scrape 目标
```

配置 systemd service 并启动。

#### Step 3: 服务类型检测与 Exporter 配置

根据 `<service-name>` 和系统检测，选择合适的 exporter：

| 服务类型 | Exporter | 默认端口 |
|---------|----------|---------|
| 系统资源 | node_exporter | 9100 |
| Node.js | prom-client middleware 指导 | 应用端口/metrics |
| PostgreSQL | postgres_exporter | 9187 |
| MySQL | mysqld_exporter | 9104 |
| MongoDB | mongodb_exporter | 9216 |
| Nginx | nginx-prometheus-exporter | 9113 |
| Redis | redis_exporter | 9121 |
| Docker | cAdvisor | 8080 |

**node_exporter**（始终安装）：
```bash
NODE_EXP_VERSION="1.7.0"
wget "https://github.com/prometheus/node_exporter/releases/download/v${NODE_EXP_VERSION}/node_exporter-${NODE_EXP_VERSION}.linux-${ARCH}.tar.gz"
tar xzf node_exporter-*.tar.gz
sudo mv node_exporter-*/node_exporter /usr/local/bin/
# 配置 systemd 并启动
```

**Node.js 应用**（生成集成指导）：
```javascript
// 指导用户在应用中添加 prom-client
// npm install prom-client
const client = require('prom-client');
const collectDefaultMetrics = client.collectDefaultMetrics;
collectDefaultMetrics();

// 在 Express 中暴露 /metrics 端点
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', client.register.contentType);
  res.end(await client.register.metrics());
});
```

**PostgreSQL**：
```bash
# 安装 postgres_exporter
PGEXP_VERSION="0.15.0"
wget "https://github.com/prometheus-community/postgres_exporter/releases/download/v${PGEXP_VERSION}/postgres_exporter-${PGEXP_VERSION}.linux-${ARCH}.tar.gz"
# 配置连接字符串（使用环境变量，不硬编码密码）
# DATA_SOURCE_NAME="postgresql://user:password@localhost:5432/dbname?sslmode=disable"
```

#### Step 4: Grafana 安装配置（如未安装）

```bash
# Ubuntu/Debian
sudo apt-get install -y apt-transport-https software-properties-common
wget -q -O - https://apt.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://apt.grafana.com stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
sudo apt-get update && sudo apt-get install -y grafana

sudo systemctl daemon-reload
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

#### Step 5: 导入预设 Dashboard

参考 `references/grafana-dashboards.md` 中的 JSON 模板，通过 Grafana API 导入：

```bash
# 等待 Grafana 启动
sleep 5

# 添加 Prometheus 数据源
GRAFANA_ADMIN_PASS="${GRAFANA_ADMIN_PASS:-admin}"
curl -X POST -u "admin:${GRAFANA_ADMIN_PASS}" http://localhost:3000/api/datasources \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Prometheus",
    "type": "prometheus",
    "url": "http://localhost:9090",
    "access": "proxy",
    "isDefault": true
  }'

# 导入 dashboard（使用 references/grafana-dashboards.md 中的 JSON）
curl -X POST -u "admin:${GRAFANA_ADMIN_PASS}" http://localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @dashboard.json
```

#### Step 6: 告警规则配置

生成 `/etc/prometheus/alert_rules.yml`：
```yaml
groups:
  - name: system_alerts
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "CPU 使用率超过 80%"
          description: "实例 {{ $labels.instance }} CPU 使用率为 {{ $value }}%"

      - alert: HighMemoryUsage
        expr: (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "内存使用率超过 90%"

      - alert: DiskSpaceRunningOut
        expr: (1 - node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 > 85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "磁盘使用率超过 85%"

      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "服务 {{ $labels.job }} 已停止"
```

#### Step 7: 告警通知渠道

根据用户选择配置 Alertmanager：

**Telegram**：
```yaml
receivers:
  - name: 'telegram'
    telegram_configs:
      - bot_token: '<BOT_TOKEN>'  # 提示用户提供，不硬编码
        chat_id: <CHAT_ID>
        message: '{{ template "telegram.default.message" . }}'
```

**Slack**：
```yaml
receivers:
  - name: 'slack'
    slack_configs:
      - api_url: '<WEBHOOK_URL>'  # 提示用户提供
        channel: '#alerts'
        title: '{{ .CommonAnnotations.summary }}'
```

**Email**：
```yaml
receivers:
  - name: 'email'
    email_configs:
      - to: '<EMAIL>'  # 提示用户提供
        from: 'alertmanager@example.com'
        smarthost: 'smtp.example.com:587'
        auth_username: '<USERNAME>'
        auth_password: '<PASSWORD>'
```

#### Step 8: 输出监控配置报告

```markdown
# 监控配置报告

## 组件状态
- Prometheus: http://localhost:9090 ✅
- Grafana: http://localhost:3000 ✅
- node_exporter: http://localhost:9100 ✅
- <service>_exporter: http://localhost:<port> ✅

## 已配置告警规则
- CPU > 80% (warning, 5分钟持续)
- 内存 > 90% (critical, 5分钟持续)
- 磁盘 > 85% (warning, 10分钟持续)
- 服务 down (critical, 1分钟)

## 告警通知
- 渠道: <Telegram/Slack/Email>

## 访问信息
- Grafana 默认账号: admin / admin（首次登录请修改密码）

## 后续建议
- [ ] 修改 Grafana 默认密码
- [ ] 根据业务需求调整告警阈值
- [ ] 添加自定义 dashboard
```

---

## 命令三：backup — 定时备份

### 语法
```
/devops-agent backup <target> <destination> [--schedule CRON] [--encrypt] [--retain DAYS] [--dry-run]
```

参数说明：
- `target`: `postgresql`、`mysql`、`mongodb`、或目录路径
- `destination`: 本地路径、`s3://bucket/path`、`oss://bucket/path`、`rsync://host/path`
- `--schedule`: cron 表达式，默认 `0 2 * * *`（每天凌晨 2 点）
- `--encrypt`: 使用 GPG 加密备份文件
- `--retain`: 保留天数，默认 30 天

### 执行流程

#### Step 1: 检测目标类型
```bash
# 数据库检测
psql --version 2>/dev/null        # PostgreSQL
mysql --version 2>/dev/null       # MySQL
mongodump --version 2>/dev/null   # MongoDB

# 如果 target 是路径，检查是否存在
[ -d "<target>" ] && echo "Directory backup mode"
```

#### Step 2: 生成备份脚本

使用 `scripts/backup-generator.sh` 的逻辑，根据参数生成定制化备份脚本：

**PostgreSQL 备份**：
```bash
#!/usr/bin/env bash
set -euo pipefail

# === 配置 ===
BACKUP_DIR="/var/backups/postgresql"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/pg_backup_${TIMESTAMP}.sql.gz"
RETAIN_DAYS=${RETAIN_DAYS:-30}
LOG_FILE="${HOME}/devops-agent.log"

# === 日志函数 ===
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [BACKUP] $*" | tee -a "$LOG_FILE"; }

# === 执行备份 ===
log "开始 PostgreSQL 备份..."
mkdir -p "$BACKUP_DIR"
pg_dumpall | gzip > "$BACKUP_FILE"

# === 加密（可选）===
# gpg --symmetric --cipher-algo AES256 --batch --passphrase-file /path/to/key "$BACKUP_FILE"

# === 校验完整性 ===
sha256sum "$BACKUP_FILE" > "${BACKUP_FILE}.sha256"
log "备份完成: $BACKUP_FILE ($(du -h "$BACKUP_FILE" | cut -f1))"

# === 上传到远程存储 ===
# aws s3 cp "$BACKUP_FILE" "s3://bucket/path/"
# 或: rsync -avz "$BACKUP_FILE" "user@remote:/path/"

# === 清理旧备份（保留策略）===
find "$BACKUP_DIR" -name "pg_backup_*.sql.gz" -mtime +${RETAIN_DAYS} -delete
log "已清理 ${RETAIN_DAYS} 天前的旧备份"

# === 通知 ===
# curl -s -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
#   -d "chat_id=<ID>&text=PostgreSQL 备份完成: $(du -h "$BACKUP_FILE" | cut -f1)"
```

**MySQL 备份**：
```bash
mysqldump --all-databases --single-transaction --routines --triggers | gzip > "$BACKUP_FILE"
```

**MongoDB 备份**：
```bash
mongodump --archive="$BACKUP_FILE" --gzip
```

**目录备份**：
```bash
tar czf "$BACKUP_FILE" -C "$(dirname "$TARGET_DIR")" "$(basename "$TARGET_DIR")"
```

#### Step 3: 配置 cron 定时任务
```bash
CRON_SCHEDULE="${SCHEDULE:-0 2 * * *}"
BACKUP_SCRIPT="/opt/scripts/backup_<target>.sh"

# 写入备份脚本
sudo cp generated_backup.sh "$BACKUP_SCRIPT"
sudo chmod +x "$BACKUP_SCRIPT"

# 添加 cron 任务（先检查是否已存在）
(crontab -l 2>/dev/null | grep -v "$BACKUP_SCRIPT"; echo "$CRON_SCHEDULE $BACKUP_SCRIPT") | crontab -
```

#### Step 4: 备份保留策略

配置日/周/月轮转：
```bash
# 日备份：保留 7 天
# 周备份（周日）：保留 4 周
# 月备份（1号）：保留 12 个月

# 在备份脚本中实现轮转逻辑
DAY_OF_WEEK=$(date +%u)  # 1=Monday, 7=Sunday
DAY_OF_MONTH=$(date +%d)

if [ "$DAY_OF_MONTH" = "01" ]; then
    cp "$BACKUP_FILE" "${BACKUP_DIR}/monthly/"
elif [ "$DAY_OF_WEEK" = "7" ]; then
    cp "$BACKUP_FILE" "${BACKUP_DIR}/weekly/"
fi

# 清理策略
find "${BACKUP_DIR}/daily/" -mtime +7 -delete
find "${BACKUP_DIR}/weekly/" -mtime +28 -delete
find "${BACKUP_DIR}/monthly/" -mtime +365 -delete
```

#### Step 5: 完整性验证
```bash
# 验证备份文件
sha256sum -c "${BACKUP_FILE}.sha256"

# 数据库备份验证（可选 - 恢复到临时库测试）
# createdb test_restore && pg_restore -d test_restore "$BACKUP_FILE" && dropdb test_restore
```

#### Step 6: 输出备份配置报告

```markdown
# 备份配置报告

## 基本信息
- **备份目标**: <target>
- **备份目的地**: <destination>
- **备份计划**: <cron-schedule>
- **加密**: 是/否
- **保留策略**: <retain-days> 天

## 备份脚本
- **位置**: /opt/scripts/backup_<target>.sh
- **cron 条目**: <cron-line>

## 保留策略
- 日备份: 7 天
- 周备份: 4 周
- 月备份: 12 个月

## 验证
- **首次备份测试**: ✅ 成功
- **文件大小**: <size>
- **校验和**: <sha256>

## 恢复命令
- PostgreSQL: `gunzip -c <backup-file> | psql`
- MySQL: `gunzip -c <backup-file> | mysql`
- MongoDB: `mongorestore --gzip --archive=<backup-file>`
- 目录: `tar xzf <backup-file> -C <target-dir>`
```

---

## 命令四：diagnose — 故障诊断

### 语法
```
/devops-agent diagnose <问题描述> [--deep] [--dry-run]
```

### 执行流程

#### Step 1: 系统概况收集

无论什么问题，先收集系统基线信息：

```bash
echo "=== 系统概况 ==="
uname -a                                    # 内核信息
uptime                                      # 运行时间和负载
free -h 2>/dev/null || vm_stat              # 内存使用
df -h                                       # 磁盘使用
cat /proc/loadavg 2>/dev/null               # 负载均衡
who                                         # 当前登录用户
last reboot | head -5                       # 最近重启记录

echo "=== 网络概况 ==="
ss -tlnp 2>/dev/null || netstat -tlnp       # 监听端口
ip addr 2>/dev/null || ifconfig             # 网络接口
cat /etc/resolv.conf                        # DNS 配置
```

#### Step 2: 根据问题描述定向检查

使用关键词匹配进行智能路由：

**问题模式：「网站打不开」/ 「502」/ 「无法访问」**
```bash
# Nginx 状态
systemctl is-active nginx
nginx -t                                   # 配置语法检查
tail -50 /var/log/nginx/error.log          # 错误日志

# 端口监听
ss -tlnp | grep -E ':80|:443'

# 上游服务状态
# 解析 nginx 配置中的 upstream 端口，逐个检查
grep proxy_pass /etc/nginx/sites-enabled/* 2>/dev/null

# DNS 检查
dig <domain> +short
nslookup <domain>

# SSL 证书有效期
echo | openssl s_client -connect <domain>:443 2>/dev/null | openssl x509 -noout -dates

# 防火墙
sudo ufw status 2>/dev/null
sudo iptables -L -n 2>/dev/null
```

**问题模式：「服务器很慢」/ 「性能问题」/ 「卡」**
```bash
# CPU 进程排行
ps aux --sort=-%cpu | head -20

# IO wait
iostat -x 1 3 2>/dev/null

# 内存详情
vmstat 1 5

# 网络连接数
ss -s
ss -tnp | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -rn | head -10

# 数据库慢查询（PostgreSQL）
sudo -u postgres psql -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE (now() - pg_stat_activity.query_start) > interval '5 seconds' ORDER BY duration DESC;" 2>/dev/null

# OOM killer 记录
dmesg | grep -i "oom\|killed process" | tail -10
```

**问题模式：「磁盘满了」/ 「空间不足」/ 「no space」**
```bash
# 磁盘使用概览
df -h

# 大文件定位（Top 20）
sudo find / -type f -size +100M -exec ls -lh {} \; 2>/dev/null | sort -k5 -rh | head -20

# 各目录占用
du -sh /var/log/ /var/lib/docker/ /tmp/ /home/ /opt/ 2>/dev/null

# 日志轮转检查
ls -la /etc/logrotate.d/
cat /var/lib/logrotate/status 2>/dev/null

# Docker 占用
docker system df 2>/dev/null

# 清理建议
echo "=== 清理建议 ==="
# apt 缓存
du -sh /var/cache/apt/archives/ 2>/dev/null
# journal 日志
journalctl --disk-usage 2>/dev/null
# Docker 未使用镜像
docker images --filter "dangling=true" -q 2>/dev/null | wc -l
```

**问题模式：「数据库连接失败」/ 「connection refused」**
```bash
# PostgreSQL 检查
pg_isready 2>/dev/null

# 连接数
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null
sudo -u postgres psql -c "SHOW max_connections;" 2>/dev/null

# 认证配置
sudo cat /etc/postgresql/*/main/pg_hba.conf 2>/dev/null | grep -v "^#" | grep -v "^$"

# 监听地址
sudo cat /etc/postgresql/*/main/postgresql.conf 2>/dev/null | grep listen_addresses

# 防火墙端口
ss -tlnp | grep 5432

# MySQL 检查
mysqladmin ping 2>/dev/null
mysqladmin status 2>/dev/null
```

**通用 / 其他问题**：
如果问题描述无法匹配以上模式，执行全面检查：依次运行所有上述检查的简化版本，收集完整系统状态。

#### Step 3: 日志分析
```bash
# systemd 日志（最近 1 小时）
journalctl --since "1 hour ago" --priority=err --no-pager | tail -50

# Nginx 错误日志
tail -100 /var/log/nginx/error.log 2>/dev/null

# 应用日志（自动检测）
# 检查 /var/log/ 下的常见应用日志
ls -lt /var/log/*.log | head -10

# syslog / messages
tail -100 /var/log/syslog 2>/dev/null || tail -100 /var/log/messages 2>/dev/null

# dmesg（内核消息）
dmesg --time-format=iso | tail -50 2>/dev/null || dmesg | tail -50
```

#### Step 4: 生成诊断报告

输出 `diagnosis-report.md`：

```markdown
# 故障诊断报告

## 问题描述
<用户描述>

## 诊断时间
<timestamp>

## 系统概况
- **OS**: <os-info>
- **运行时间**: <uptime>
- **负载**: <load-average>
- **内存使用**: <memory-usage>
- **磁盘使用**: <disk-usage>

## 发现的问题（按严重程度排序）

### 🔴 严重
1. <issue-description>
   - **证据**: <evidence>
   - **影响**: <impact>
   - **修复命令**: `<fix-command>`

### 🟡 警告
1. <issue-description>
   - **证据**: <evidence>
   - **修复建议**: <suggestion>

### 🔵 信息
1. <observation>

## 修复建议（按优先级排序）
1. [严重] <fix-1> — `<command>`
2. [警告] <fix-2> — `<command>`
3. [建议] <fix-3>

## 相关日志摘录
```
<relevant-log-entries>
```
```

---

## 输出规范

所有命令完成后：
1. 在终端输出关键结果摘要
2. 生成对应的报告文件（.md 格式）
3. 日志记录到 devops-agent.log
4. 如果有需要用户后续操作的事项，以 checklist 形式列出

## 错误处理

- 命令执行失败时：显示错误信息，提供替代方案
- 权限不足时：提示需要的权限，给出 sudo 命令
- 工具缺失时：给出安装命令（区分 apt/yum/brew）
- 网络超时时：建议检查网络，提供离线替代方案

## 兼容性

- **OS**: Ubuntu 20.04+、Ubuntu 22.04+、Debian 11+、CentOS 8+、macOS 12+
- **架构**: x86_64 (amd64)、arm64 (aarch64)
- **Shell**: bash 4.0+, zsh 5.0+
- macOS 上自动使用对应的替代命令（如 `vm_stat` 替代 `free -h`）
