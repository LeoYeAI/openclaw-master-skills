---
name: btpanel
description: 宝塔面板(BT-Panel)运维监控技能，提供服务器资源监控、网站状态检查、服务状态检查、SSH安全审计、计划任务管理、日志读取等功能
user-invocable: true
disable-model-invocation: false
icon: icon/bt.png
metadata:
  openclaw:
    requires:
      bins:
        - python3
    keywords:
      - 宝塔面板
      - BT-Panel
      - 面板
      - 服务器监控
      - 系统资源
      - CPU监控
      - 内存监控
      - 磁盘监控
      - 网站状态
      - SSL证书
      - 服务状态
      - 日志读取
      - SSH
      - 计划任务
      - crontab
      - 备份任务
---

# 宝塔面板运维监控

宝塔面板服务器的全方位运维监控工具，支持多服务器管理、资源监控、网站状态检查、服务状态检查、SSH安全审计、计划任务管理等功能。

![宝塔面板](icon/bt-logo.svg)

## 图标资源

技能包提供以下图标文件，可在生成报告时引用：

| 文件 | 格式 | 用途 |
|------|------|------|
| `icon/bt-logo.svg` | SVG | 矢量图标，适合缩放 |

**使用示例**（生成报告时）：
```markdown
# 服务器巡检报告

![宝塔面板](icon/bt-logo.svg)

## 概述
...
```

## AI 使用约束

本技能用于查询和展示服务器状态数据，AI应遵循以下原则：

1. **数据中立**：如实展示监控数据，不夸大或缩小问题严重性
2. **客观分析**：基于阈值配置给出告警，避免主观判断
3. **数据驱动**：建议和结论应基于实际数据，不得臆测
4. **隐私保护**：不主动泄露服务器敏感信息（如IP、Token、域名）
5. **执行前告知**：由于接口数据较多，获取和分析需要一定时间，AI应先向用户简述即将执行的操作步骤，然后再执行命令获取数据

**执行流程示例**：
```
AI: 我将为您执行以下操作：
    1. 获取服务器系统资源状态（CPU、内存、磁盘）
    2. 检查网站运行状态
    3. 检查服务运行状态
    正在获取数据，请稍候...
    [执行命令]
    [展示结果和分析]
```

## 服务器配置管理
> **重要:** 没有服务器信息时需要添加

使用配置工具管理服务器：

```bash
# 查看帮助
python3 {baseDir}/scripts/bt-config.py -h

# 添加服务器
python3 {baseDir}/scripts/bt-config.py add -n prod-01 -H https://panel.example.com:8888 -t YOUR_TOKEN

# 列出服务器
python3 {baseDir}/scripts/bt-config.py list

# 设置阈值
python3 {baseDir}/scripts/bt-config.py threshold --cpu 75 --memory 80
```

## 常用场景

### 场景一：初次使用配置服务器

当用户第一次使用本技能时，需要先配置服务器连接信息：

```bash
# 添加服务器（需要面板地址和API Token）
python3 {baseDir}/scripts/bt-config.py add -n prod-01 -H https://panel.example.com:8888 -t YOUR_API_TOKEN

# 查看已配置的服务器
python3 {baseDir}/scripts/bt-config.py list
```

**获取API Token的方法**：
1. 登录宝塔面板
2. 进入「面板设置」->「API接口」
3. 点击「获取API Token」

**用户意图识别**：
- "帮我配置宝塔服务器" → 引导用户添加服务器配置
- "添加一台服务器" → 执行 bt-config.py add
- "查看有哪些服务器" → 执行 bt-config.py list


### 场景二：多服务器资源汇总

当用户需要了解所有服务器的整体运行状态时：

```bash
# 查看所有服务器的资源使用情况
python3 {baseDir}/scripts/monitor.py --format table

# 查看所有服务器的网站状态汇总
python3 {baseDir}/scripts/sites.py

# 查看所有服务器的服务状态
python3 {baseDir}/scripts/services.py
```

**用户意图识别**：
- "服务器整体情况怎么样" → 执行 monitor.py
- "所有服务器健康状态" → 执行 monitor.py + sites.py
- "多服务器资源使用情况" → 执行 monitor.py --format table

### 场景三：单台服务器日常巡检

当用户需要对单台服务器进行全面检查时：

```bash
# 指定服务器名称进行各项检查
python3 {baseDir}/scripts/monitor.py --server prod-01 --format table
python3 {baseDir}/scripts/sites.py --server prod-01
python3 {baseDir}/scripts/services.py --server prod-01
python3 {baseDir}/scripts/ssh.py --status --server prod-01
python3 {baseDir}/scripts/crontab.py --backup-only --server prod-01
```

**用户意图识别**：
- "检查 prod-01 这台服务器" → 执行上述检查命令
- "帮我日常巡检" → 执行系统监控、网站状态、服务状态检查
- "这台服务器有问题吗" → 执行全面检查并汇总告警

### 场景四：网站SSL证书检查

当用户关心SSL证书是否即将过期时：

```bash
# 查看SSL即将过期的网站
python3 {baseDir}/scripts/sites.py --filter ssl-warning

# 查看SSL已过期的网站
python3 {baseDir}/scripts/sites.py --filter ssl-expired
```

**用户意图识别**：
- "SSL证书快过期了吗" → 执行 sites.py --filter ssl-warning
- "有哪些网站证书过期了" → 执行 sites.py --filter ssl-expired

### 场景五：安全审计

当用户需要进行安全检查时：

```bash
# 查看SSH登录失败记录
python3 {baseDir}/scripts/ssh.py --logs --filter failed

# 搜索特定IP的登录记录
python3 {baseDir}/scripts/ssh.py --logs --search 192.168.1.100

# 查看SSH服务状态
python3 {baseDir}/scripts/ssh.py --status
```

**用户意图识别**：
- "有没有异常登录" → 执行 ssh.py --logs --filter failed
- "查一下这个IP的登录记录" → 执行 ssh.py --logs --search IP
- "SSH安全检查" → 执行 ssh.py --status 和 ssh.py --logs

### 场景六：服务故障排查

当某个服务出现问题时：

```bash
# 查看服务状态
python3 {baseDir}/scripts/services.py --server prod-01

# 查看服务错误日志
python3 {baseDir}/scripts/logs.py --server prod-01 --service nginx --lines 200
python3 {baseDir}/scripts/logs.py --server prod-01 --service redis
```

**用户意图识别**：
- "Nginx/Apache/Redis出问题了" → 查看服务状态 + 查看错误日志
- "服务报错了，帮我看看日志" → 执行 logs.py 查看对应服务日志

### 场景七：备份任务检查

当用户关心备份是否正常时：

```bash
# 查看所有备份任务
python3 {baseDir}/scripts/crontab.py --backup-only

# 查看特定备份任务的执行日志
python3 {baseDir}/scripts/crontab.py --logs --task-id 11
```

**用户意图识别**：
- "备份任务正常吗" → 执行 crontab.py --backup-only
- "查看备份日志" → 执行 crontab.py --logs --task-id ID

## 版本要求

- **宝塔面板**: >= 9.0.0
- **Python**: >= 3.10

## 用法

### 系统资源监控

```bash
# 查看帮助
python3 {baseDir}/scripts/monitor.py -h

# 监控所有服务器
python3 {baseDir}/scripts/monitor.py

# 监控指定服务器
python3 {baseDir}/scripts/monitor.py --server prod-01

# JSON格式输出
python3 {baseDir}/scripts/monitor.py --format json

# 表格格式输出
python3 {baseDir}/scripts/monitor.py --format table

# 输出到文件
python3 {baseDir}/scripts/monitor.py --output report.json
```

### 网站状态检查

```bash
# 查看帮助
python3 {baseDir}/scripts/sites.py -h

# 检查所有服务器的网站状态
python3 {baseDir}/scripts/sites.py

# 检查指定服务器
python3 {baseDir}/scripts/sites.py --server prod-01

# 只显示停止的网站
python3 {baseDir}/scripts/sites.py --filter stopped

# 只显示SSL即将过期的网站（30天内）
python3 {baseDir}/scripts/sites.py --filter ssl-warning

# 只显示SSL已过期的网站
python3 {baseDir}/scripts/sites.py --filter ssl-expired

# JSON格式输出
python3 {baseDir}/scripts/sites.py --format json

# 输出到文件
python3 {baseDir}/scripts/sites.py --output sites.json
```

### 服务状态检查

```bash
# 查看帮助
python3 {baseDir}/scripts/services.py -h

# 检查所有服务器的服务状态
python3 {baseDir}/scripts/services.py

# 检查指定服务器
python3 {baseDir}/scripts/services.py --server prod-01

# 只检查特定服务
python3 {baseDir}/scripts/services.py --service nginx --service redis

# JSON格式输出
python3 {baseDir}/scripts/services.py --format json

# 输出到文件
python3 {baseDir}/scripts/services.py --output services.json
```

### 日志读取

```bash
# 查看帮助
python3 {baseDir}/scripts/logs.py -h

# 查看Nginx错误日志
python3 {baseDir}/scripts/logs.py --service nginx

# 查看Redis日志
python3 {baseDir}/scripts/logs.py --service redis

# 查看Apache错误日志
python3 {baseDir}/scripts/logs.py --service apache

# 查看MySQL错误日志
python3 {baseDir}/scripts/logs.py --service mysql

# 查看MySQL慢查询日志
python3 {baseDir}/scripts/logs.py --service mysql --log-type slow

# 查看PostgreSQL日志（需要插件）
python3 {baseDir}/scripts/logs.py --service pgsql

# 查看PostgreSQL慢日志
python3 {baseDir}/scripts/logs.py --service pgsql --log-type slow

# 指定服务器和行数
python3 {baseDir}/scripts/logs.py --server prod-01 --service nginx --lines 200

# JSON格式输出
python3 {baseDir}/scripts/logs.py --service nginx --format json
```

### SSH状态和日志检查

```bash
# 查看帮助
python3 {baseDir}/scripts/ssh.py -h

# 查看SSH服务状态
python3 {baseDir}/scripts/ssh.py --status

# 查看SSH登录日志
python3 {baseDir}/scripts/ssh.py --logs

# 只查看失败的登录日志
python3 {baseDir}/scripts/ssh.py --logs --filter failed

# 只查看成功的登录日志
python3 {baseDir}/scripts/ssh.py --logs --filter success

# 搜索特定IP的登录记录
python3 {baseDir}/scripts/ssh.py --logs --search 192.168.1.1

# 指定服务器
python3 {baseDir}/scripts/ssh.py --status --server prod-01

# JSON格式输出
python3 {baseDir}/scripts/ssh.py --logs --format json
```

### 计划任务检查

```bash
# 查看帮助
python3 {baseDir}/scripts/crontab.py -h

# 查看所有计划任务
python3 {baseDir}/scripts/crontab.py

# 只查看备份任务
python3 {baseDir}/scripts/crontab.py --backup-only

# 查看指定服务器
python3 {baseDir}/scripts/crontab.py --server prod-01

# 查看备份任务日志
python3 {baseDir}/scripts/crontab.py --logs --task-id 11

# JSON格式输出
python3 {baseDir}/scripts/crontab.py --format json
```

## 参数说明

### monitor.py 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--server`, `-s` | 指定服务器名称 | 所有服务器 |
| `--format`, `-f` | 输出格式 (json/table) | json |
| `--output`, `-o` | 输出文件路径 | 标准输出 |
| `--config`, `-c` | 配置文件路径 | 自动查找 |

### sites.py 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--server`, `-s` | 指定服务器名称 | 所有服务器 |
| `--format`, `-f` | 输出格式 (json/table) | table |
| `--output`, `-o` | 输出文件路径 | 标准输出 |
| `--filter` | 过滤条件 (stopped/ssl-warning/ssl-expired) | 无 |
| `--config`, `-c` | 配置文件路径 | 自动查找 |

### services.py 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--server`, `-s` | 指定服务器名称 | 所有服务器 |
| `--format`, `-f` | 输出格式 (json/table) | table |
| `--output`, `-o` | 输出文件路径 | 标准输出 |
| `--service` | 指定要检查的服务（可多次指定） | 默认服务列表 |
| `--config`, `-c` | 配置文件路径 | 自动查找 |

### logs.py 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--server`, `-s` | 指定服务器名称 | 所有服务器 |
| `--service` | 服务名称 (nginx/apache/redis/mysql/pgsql) | 必填 |
| `--log-type` | 日志类型 (error/slow) | error |
| `--lines`, `-n` | 返回最后N行日志 | 100 |
| `--format`, `-f` | 输出格式 (json/table) | table |
| `--output`, `-o` | 输出文件路径 | 标准输出 |
| `--config`, `-c` | 配置文件路径 | 自动查找 |

**注意**：只有已安装的服务才能获取日志，尝试获取未安装服务的日志会返回错误。

### ssh.py 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--server`, `-s` | 指定服务器名称 | 所有服务器 |
| `--status` | 查看SSH服务状态 | 否 |
| `--logs` | 查看SSH登录日志 | 否 |
| `--filter` | 日志过滤 (ALL/success/failed) | ALL |
| `--search` | 搜索关键字（IP或用户名） | 无 |
| `--limit`, `-n` | 返回日志条数 | 50 |
| `--format`, `-f` | 输出格式 (json/table) | table |
| `--output`, `-o` | 输出文件路径 | 标准输出 |
| `--config`, `-c` | 配置文件路径 | 自动查找 |

### crontab.py 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--server`, `-s` | 指定服务器名称 | 所有服务器 |
| `--backup-only` | 只显示备份任务 | 否 |
| `--logs` | 查看任务日志 | 否 |
| `--task-id` | 任务ID（配合--logs使用） | 无 |
| `--days` | 日志查询天数 | 7 |
| `--format`, `-f` | 输出格式 (json/table) | table |
| `--output`, `-o` | 输出文件路径 | 标准输出 |
| `--config`, `-c` | 配置文件路径 | 自动查找 |

## 监控指标

### 系统资源监控 (monitor.py)

通过单一API接口获取完整的系统监控数据：

- **CPU**: 使用率、核心数、型号、用户/系统占用
- **内存**: 总量、使用量、可用量、缓存、使用率
- **磁盘**: 多分区详情、总量、使用量、使用率
- **网络**: 实时速度、总流量、各网卡统计
- **负载**: 1/5/15分钟负载
- **系统**: 主机名、操作系统、运行时间、面板版本
- **资源**: 网站、数据库、FTP账户数量

### 网站状态检查 (sites.py)

支持多种项目类型：

| 类型 | 进程信息 | 运行状态判断 |
|------|----------|--------------|
| PHP | 无 | status==1 && stop为空 |
| Java | pid_info | pid > 0 |
| Node | load_info | run==true |
| Go | load_info | run==true |
| Python | pids | run==true |
| .NET | load_info | run==true |
| Proxy(反代) | 无 | status==1 |
| HTML(静态) | 无 | status==1 |
| Other(其他) | load_info | run==true |

检查项目：
- **运行状态**: 运行中/已停止/启动中
- **SSL证书**: 有效/即将过期/已过期
- **进程信息**: PID、内存、CPU、线程数（适用于Java/Node/Go/Python/.NET/Other）
- **反代健康**: 反代项目的后端健康状态
- **基础信息**: 路径、域名、PHP版本、端口、代理地址

### 服务状态检查 (services.py)

支持检查的服务：

| 服务 | 状态检查 | 日志支持 |
|------|----------|----------|
| Nginx | ✓ | ✓ 错误日志 |
| Apache | ✓ | ✓ 错误日志 |
| MySQL | ✓ | ✓ 错误日志/慢日志 |
| Redis | ✓ | ✓ 日志文件 |
| Memcached | ✓ | ✗ |
| Pure-FTPD | ✓ | ✗ |
| PHP (多版本) | ✓ | ✗ |
| PostgreSQL | ✓ | ✓ 错误日志/慢日志 |

**服务状态字段说明**：

| 字段 | 说明 |
|------|------|
| `installed` (setup) | 服务是否已安装 |
| `status` | 服务是否正在运行 |
| `version` | 已安装的版本号 |
| `pid` | 主进程ID（运行中时） |

**重要区别**：
- `installed=false`：服务未安装，无法获取日志
- `installed=true, status=false`：服务已安装但未运行
- `installed=true, status=true`：服务已安装且正在运行

**PHP多版本共存说明**：
- PHP是支持多版本共存的服务，一台服务器可能同时安装多个PHP版本
- PHP服务名称格式：`php-X.X`（如 `php-8.2`、`php-7.4`）
- 系统会自动扫描已安装的PHP版本并分别显示状态
- 常见PHP版本：8.5, 8.4, 8.3, 8.2, 8.1, 8.0, 7.4, 7.3, 7.2, 7.1, 7.0, 5.4, 5.3, 5.2

检查项目：
- **运行状态**: 运行中/已停止
- **版本信息**: 已安装版本号
- **进程PID**: 主进程ID

### 日志读取 (logs.py)

支持的日志类型：

| 日志类型 | 服务 | 获取方式 |
|----------|------|----------|
| 错误日志 | nginx | 文件: /www/server/nginx/logs/error.log |
| 错误日志 | apache | 文件: /www/wwwlogs/error_log |
| 日志文件 | redis | 文件: /www/server/redis/redis.log |
| 错误日志 | mysql | 接口: /database?action=GetErrorLog |
| 慢日志 | mysql | 接口: /database?action=GetSlowLogs |
| 错误日志 | pgsql | 插件接口: pgsql_manager |
| 慢日志 | pgsql | 插件接口: pgsql_manager |

**注意事项**：
- 只有已安装（`installed=true`）的服务才能获取日志
- 尝试获取未安装服务的日志会返回错误
- Memcached 和 Pure-FTPD 不支持日志获取

### SSH状态和日志检查 (ssh.py)

检查项目：
- **SSH服务状态**: 运行中/已停止
- **端口**: SSH监听端口
- **Ping设置**: 是否允许ping
- **防火墙状态**: 是否启用
- **Fail2ban**: 是否安装和运行

登录日志字段：
- **时间**: 登录时间
- **类型**: 成功/失败
- **用户**: 登录用户名
- **IP地址**: 来源IP
- **地区**: IP归属地
- **登录方式**: password/key

### 计划任务检查 (crontab.py)

任务类型：
- **备份网站**: 自动备份网站文件和数据库
- **备份数据库**: 单独备份数据库
- **备份目录**: 备份指定目录
- **Shell脚本**: 自定义Shell命令
- **同步时间**: NTP时间同步
- **切割日志**: 日志分割任务
- **访问URL**: 定时HTTP请求

检查项目：
- **任务状态**: 启用/禁用
- **执行周期**: 每天/每小时/每周/每月/间隔分钟
- **备份目标**: 网站名称/数据库名称
- **保留数量**: 备份保留份数
- **执行结果**: 最后一次执行状态

## 告警配置

### SSL证书告警

| 剩余天数 | 告警级别 |
|----------|----------|
| 已过期 | critical |
| ≤ 7 天 | critical |
| ≤ 30 天 | warning |

### 服务器资源告警阈值

可在配置文件中设置告警阈值：

```yaml
global:
  thresholds:
    cpu: 80      # CPU使用率告警阈值(%)
    memory: 85   # 内存使用率告警阈值(%)
    disk: 90     # 磁盘使用率告警阈值(%)
```

