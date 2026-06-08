# 腾讯云 Lighthouse 应用部署指引

你对腾讯云 Lighthouse 实例创建、防火墙配置、镜像查询相关 API 的参数可能已过时。
**执行前请先用 `tccli lighthouse <操作> --help` 确认最新参数。**

> 适用场景：在腾讯云 Lighthouse 上部署任意 Web 应用（Go / Node.js / Python / Java / 静态站点 / Docker / GitHub 项目等）
> 全程通过 `tccli` + SSH 完成，无需登录控制台

---

## 一、总体流程

```
阶段一：创建实例
  1. 查询镜像 → 选择操作系统
  2. 查询套餐 → 选择 CPU/内存/带宽
  3. 创建实例 → 获取实例 ID
  4. 等待实例 RUNNING → 获取公网 IP
  5. 重置密码 → 获取 SSH 登录凭证
  6. 开放防火墙端口

阶段二：部署应用
  7. 准备代码（本地项目 / GitHub clone / Docker 镜像）
  8. 上传或拉取代码到实例
  9. 安装运行环境 + 构建 + 启动
  10. 配置 systemd / pm2 / docker-compose 守护进程

阶段三：验证与优化
  11. 验证服务可访问
  12. （可选）绑定域名 + HTTPS + Nginx 反向代理
```

---

## 二、阶段一：创建实例

### 2.1 凭证配置

```bash
export TENCENTCLOUD_SECRET_ID="<your-secret-id>"
export TENCENTCLOUD_SECRET_KEY="<your-secret-key>"
```

> 所需权限：`QcloudLighthouseFullAccess`

### 2.2 查询镜像

```bash
# 纯系统镜像（推荐 Ubuntu 24.04）
tccli lighthouse DescribeBlueprints --region <region> \
  --cli-unfold-argument \
  --Filters.0.Name blueprint-type \
  --Filters.0.Values PURE_OS

# 应用镜像（WordPress / 宝塔 / Docker CE 等）
tccli lighthouse DescribeBlueprints --region <region> \
  --cli-unfold-argument \
  --Filters.0.Name blueprint-type \
  --Filters.0.Values APP_OS
```

过滤示例（以 Ubuntu 24.04 为例）：
```bash
... | python3 -c "
import json, sys
data = json.load(sys.stdin)
for b in data.get('BlueprintSet', []):
    if 'Ubuntu' in b.get('OsName', '') and '24.04' in b.get('OsName', ''):
        print(f\"BlueprintId: {b['BlueprintId']}  OsName: {b['OsName']}\")
"
```

**镜像选择建议：**

| 部署类型 | 推荐镜像 |
|---------|---------|
| Go / Rust / C++ | Ubuntu 24.04（纯系统，自行编译） |
| Node.js / Python / Ruby | Ubuntu 24.04（纯系统，装运行时）|
| Docker 项目 | Docker CE 应用镜像（预装 Docker） |
| WordPress / CMS | WordPress 应用镜像 |
| 需要面板管理 | 宝塔面板应用镜像 |

### 2.3 查询套餐

```bash
tccli lighthouse DescribeBundles --region <region> \
  --cli-unfold-argument \
  --Filters.0.Name bundle-type \
  --Filters.0.Values GENERAL_BUNDLE
```

**套餐选择建议：**

| 应用类型 | 推荐配置 |
|---------|---------|
| 静态站点 / 轻量 API | 2核 2G |
| Go / Node.js Web 应用 | 2核 4G |
| Java / 数据库 / Docker 多容器 | 4核 8G |

### 2.4 创建实例

```bash
tccli lighthouse CreateInstances --region <region> \
  --cli-unfold-argument \
  --BundleId <bundle-id> \
  --BlueprintId <blueprint-id> \
  --InstanceName "<name>" \
  --InstanceChargePrepaid.Period 1 \
  --LoginConfiguration.AutoGeneratePassword YES \
  --InstanceCount 1 \
  --Zones <zone>
```

> ⚠️ 踩坑点：
> - `--InstanceChargePrepaid.Period` 必填，单位为月
> - `AutoGeneratePassword` 值必须是大写 `YES` 或 `NO`，不是 `True`/`true`/`Yes`

### 2.5 等待实例启动

```bash
# 每 15-30 秒轮询，直到 RUNNING
tccli lighthouse DescribeInstances --region <region> \
  --cli-unfold-argument \
  --InstanceIds <instance-id> 2>&1 | python3 -c "
import json, sys
data = json.load(sys.stdin)
inst = data['InstanceSet'][0]
print(f\"状态: {inst['InstanceState']}\")
pub = inst.get('PublicAddresses', [])
print(f\"公网IP: {pub[0] if pub else '未分配'}\")
"
```

状态流转：`PENDING` → `RUNNING`（约 30–60 秒）

### 2.6 重置密码

```bash
tccli lighthouse ResetInstancesPassword --region <region> \
  --cli-unfold-argument \
  --InstanceIds <instance-id> \
  --Password '<password>' \
  --UserName root
```

> 密码要求：8-30 位，至少包含大写、小写、数字、特殊字符中的三种。
> 重置后等待约 15-20 秒生效。

### 2.7 开放防火墙端口

```bash
# 开放 HTTP 80
tccli lighthouse CreateFirewallRules --region <region> \
  --cli-unfold-argument \
  --InstanceId <instance-id> \
  --FirewallRules.0.Protocol TCP \
  --FirewallRules.0.Port 80 \
  --FirewallRules.0.CidrBlock "0.0.0.0/0" \
  --FirewallRules.0.Action ACCEPT \
  --FirewallRules.0.FirewallRuleDescription "HTTP"
```

> 返回 `InvalidParameter.FirewallRulesExist` 表示规则已存在，可忽略。

常见端口开放：

| 端口 | 用途 |
|------|------|
| 80 | HTTP |
| 443 | HTTPS |
| 8080 | 常见应用端口 |
| 3000 | Node.js / Grafana |
| 5000 | Flask / Registry |
| 8888 | 宝塔面板 |

---

## 三、阶段二：部署应用

以下按不同来源/技术栈分别说明。所有方案的前提是已完成阶段一（实例已 RUNNING、密码已重置、端口已开放）。

定义 SSH 快捷方式供后续使用：
```bash
SSH="sshpass -p '<password>' ssh -o StrictHostKeyChecking=no root@<公网IP>"
SCP="sshpass -p '<password>' scp -o StrictHostKeyChecking=no"
```

---

### 方案 A：部署本地项目（上传代码）

适用：本地已有代码，打包上传到实例。

```bash
# 1. 本地打包
cd /path/to/project
tar czf /tmp/project.tar.gz --exclude='.git' --exclude='node_modules' .

# 2. 上传
$SCP /tmp/project.tar.gz root@<公网IP>:/tmp/

# 3. 远程解压
$SSH 'mkdir -p /opt/app && cd /opt/app && tar xzf /tmp/project.tar.gz'
```

---

### 方案 B：部署 GitHub 项目（直接 clone）

适用：从 GitHub / GitLab / Gitee 拉取开源项目。

```bash
$SSH '
apt update && apt install -y git
cd /opt
git clone https://github.com/<user>/<repo>.git app
cd app
# 如需切换分支或版本
# git checkout v1.0.0
'
```

> 私有仓库需配置 SSH Key 或使用 Personal Access Token：
> `git clone https://<token>@github.com/<user>/<repo>.git`

---

### 方案 C：Docker 部署

适用：项目有 Dockerfile 或 docker-compose.yml。

```bash
$SSH '
# 安装 Docker（如非 Docker CE 镜像）
curl -fsSL https://get.docker.com | sh
systemctl enable docker && systemctl start docker

# 拉取并运行
docker run -d --name app --restart=always -p 80:8080 <image>

# 或使用 docker-compose
cd /opt/app
docker compose up -d
'
```

---

### 各技术栈环境安装 + 构建 + 运行

#### Go 项目

```bash
$SSH '
# 安装 Go
wget -q https://go.dev/dl/go1.22.5.linux-amd64.tar.gz -O /tmp/go.tar.gz
rm -rf /usr/local/go && tar -C /usr/local -xzf /tmp/go.tar.gz
export PATH=$PATH:/usr/local/go/bin

# 构建
cd /opt/app
go build -o server ./cmd/server/
# 或 go build -o server .
'
```

#### Node.js 项目

```bash
$SSH '
# 安装 Node.js（via NodeSource）
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# 安装依赖 & 构建
cd /opt/app
npm install
npm run build  # 如有构建步骤
'
```

#### Python 项目

```bash
$SSH '
apt update && apt install -y python3 python3-pip python3-venv

cd /opt/app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
'
```

#### Java 项目（Spring Boot）

```bash
$SSH '
apt update && apt install -y openjdk-21-jdk-headless

cd /opt/app
# 如有 Maven Wrapper
./mvnw package -DskipTests
# 或直接上传 jar
'
```

#### 纯静态站点（HTML/CSS/JS）

```bash
$SSH '
apt update && apt install -y nginx

# 将静态文件放到 Nginx 默认目录
cp -r /opt/app/* /var/www/html/
systemctl restart nginx
'
```

---

### 配置进程守护（systemd）

适用于 Go / Node.js / Python / Java 等需要常驻运行的应用。

```bash
$SSH 'cat > /etc/systemd/system/app.service <<EOF
[Unit]
Description=Web Application
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/app
ExecStart=<启动命令>
Environment=PORT=80
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable app
systemctl restart app
'
```

**各技术栈的 ExecStart 示例：**

| 技术栈 | ExecStart |
|--------|-----------|
| Go | `/opt/app/server` |
| Node.js | `/usr/bin/node /opt/app/index.js` |
| Python (Gunicorn) | `/opt/app/venv/bin/gunicorn -w 4 -b 0.0.0.0:80 app:app` |
| Python (Uvicorn) | `/opt/app/venv/bin/uvicorn main:app --host 0.0.0.0 --port 80` |
| Java | `/usr/bin/java -jar /opt/app/target/app.jar --server.port=80` |

> Node.js 也可使用 pm2 替代 systemd：
> ```bash
> npm install -g pm2
> cd /opt/app && pm2 start index.js --name app
> pm2 startup && pm2 save
> ```

---

## 四、阶段三：验证与优化

### 4.1 验证服务

```bash
# 检查服务状态
$SSH 'systemctl status app --no-pager'

# HTTP 验证
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://<公网IP>/

# 浏览器访问
http://<公网IP>
```

### 4.2 查看日志

```bash
# systemd 服务日志
$SSH 'journalctl -u app -n 100 --no-pager'

# Docker 日志
$SSH 'docker logs app --tail 100'

# pm2 日志
$SSH 'pm2 logs app --lines 100'
```

### 4.3 绑定域名

```bash
# 添加 DNS A 记录
tccli dnspod CreateRecord \
  --Domain "<domain>" \
  --SubDomain "@" \
  --RecordType "A" \
  --RecordLine "默认" \
  --Value "<公网IP>" \
  --TTL 600

# www 子域名
tccli dnspod CreateRecord \
  --Domain "<domain>" \
  --SubDomain "www" \
  --RecordType "A" \
  --RecordLine "默认" \
  --Value "<公网IP>" \
  --TTL 600
```

> DNS 生效需 5-30 分钟。

### 4.4 HTTPS + Nginx 反向代理

```bash
$SSH '
apt install -y nginx certbot python3-certbot-nginx

# Nginx 反向代理配置
cat > /etc/nginx/sites-available/app <<EOF
server {
    listen 80;
    server_name <domain> www.<domain>;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/app /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# 申请 SSL 证书（需域名已解析到此 IP）
certbot --nginx -d <domain> -d www.<domain> --non-interactive --agree-tos -m <email>
'
```

> 使用 Nginx 反向代理时，应用监听 8080（或其他内部端口），Nginx 监听 80/443。

### 4.5 代码更新

```bash
# 方案 A：本地上传
tar czf /tmp/project.tar.gz --exclude='.git' --exclude='node_modules' .
$SCP /tmp/project.tar.gz root@<公网IP>:/tmp/
$SSH 'cd /opt/app && tar xzf /tmp/project.tar.gz && <rebuild> && systemctl restart app'

# 方案 B：GitHub pull
$SSH 'cd /opt/app && git pull && <rebuild> && systemctl restart app'

# 方案 C：Docker 更新
$SSH 'docker pull <image> && docker stop app && docker rm app && docker run -d --name app --restart=always -p 80:8080 <image>'
```

---

## 五、常见问题

| 问题 | 原因与解决 |
|------|-----------|
| `AutoGeneratePassword` 参数错误 | 值必须是大写字符串 `YES` / `NO` |
| `sshpass: command not found` | `apt install sshpass` |
| SSH 连接被拒绝 | 密码重置后等 15-20 秒；检查 22 端口防火墙 |
| 页面无法访问 | 检查防火墙规则 + 应用监听地址是否为 `0.0.0.0`（不是 `127.0.0.1`） |
| Go 构建失败 | 确认 `go.mod` 存在；检查 `go version` |
| Node.js `npm install` 失败 | 内存不足时加 swap：`fallocate -l 1G /swapfile && mkswap /swapfile && swapon /swapfile` |
| systemd 服务启动失败 | `journalctl -u app -n 50 --no-pager` 查看错误日志 |
| Docker 端口冲突 | `docker ps` 检查端口占用；`netstat -tlnp` 排查 |
| 域名无法访问 | DNS 传播需 5-30 分钟；先用 IP 直连验证服务正常 |
| Let's Encrypt 申请失败 | 确认域名已解析到实例 IP；80 端口可访问 |

---

## 六、API 速查

| 功能 | 服务 | 接口 |
|------|------|------|
| 查询套餐 | lighthouse | `DescribeBundles` |
| 查询镜像 | lighthouse | `DescribeBlueprints` |
| 创建实例 | lighthouse | `CreateInstances` |
| 查询实例 | lighthouse | `DescribeInstances` |
| 重置密码 | lighthouse | `ResetInstancesPassword` |
| 创建防火墙规则 | lighthouse | `CreateFirewallRules` |
| 查询防火墙规则 | lighthouse | `DescribeFirewallRules` |
| 添加 DNS 解析 | dnspod | `CreateRecord` |
| 查询 DNS 解析 | dnspod | `DescribeRecordList` |
| 修改 DNS 解析 | dnspod | `ModifyRecord` |
| 删除 DNS 解析 | dnspod | `DeleteRecord` |

---

## 何时使用

| 场景 | 建议 |
|------|------|
| 用户要部署 Go/Node/Python/Java/Docker 应用 | 按本文档三阶段流程执行 |
| 用户要部署 GitHub 项目 | 参考本文档方案 B |
| 用户要建站（WordPress/宝塔/CMS） | 不使用本文档，用 references/lighthouse-website-setup.md |
| 用户要部署 OpenClaw | 不使用本文档，用 references/lighthouse-openclaw-setup.md |
| 用户要绑定域名和 HTTPS | 参考本文档第四阶段 |
| 用户要做安全检查 | 不使用本文档，用 references/cvm-security-check.md |
