# Nginx 配置模板集合

> DevOps Agent 部署命令使用的 Nginx 配置模板。
> 所有模板使用 `{{变量名}}` 占位符，由 Agent 在部署时替换。

---

## 1. 静态站点

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name {{DOMAIN}};

    root {{STATIC_DIR}};
    index index.html index.htm;

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript image/svg+xml;
    gzip_min_length 1000;
    gzip_vary on;

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # SPA 路由支持（React/Vue/Angular）
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 禁止访问隐藏文件
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    access_log /var/log/nginx/{{DOMAIN}}_access.log;
    error_log /var/log/nginx/{{DOMAIN}}_error.log;
}
```

---

## 2. 反向代理（通用 HTTP 后端）

```nginx
upstream {{APP_NAME}}_backend {
    server 127.0.0.1:{{PORT}};
    keepalive 32;
}

server {
    listen 80;
    listen [::]:80;
    server_name {{DOMAIN}};

    # 请求体大小限制
    client_max_body_size {{MAX_BODY_SIZE:-50m}};

    # 代理超时
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    location / {
        proxy_pass http://{{APP_NAME}}_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Request-ID $request_id;

        # 缓冲设置
        proxy_buffering on;
        proxy_buffer_size 8k;
        proxy_buffers 8 8k;
    }

    # 健康检查端点（不记录日志）
    location /health {
        proxy_pass http://{{APP_NAME}}_backend;
        access_log off;
    }

    # 禁止访问隐藏文件
    location ~ /\. {
        deny all;
    }

    access_log /var/log/nginx/{{DOMAIN}}_access.log;
    error_log /var/log/nginx/{{DOMAIN}}_error.log;
}
```

---

## 3. WebSocket 支持

在反向代理基础上添加 WebSocket 升级支持：

```nginx
upstream {{APP_NAME}}_backend {
    server 127.0.0.1:{{PORT}};
    keepalive 32;
}

map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

server {
    listen 80;
    listen [::]:80;
    server_name {{DOMAIN}};

    client_max_body_size {{MAX_BODY_SIZE:-50m}};

    # 普通 HTTP 请求
    location / {
        proxy_pass http://{{APP_NAME}}_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket 端点
    location {{WS_PATH:-/ws}} {
        proxy_pass http://{{APP_NAME}}_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 超时（保持长连接）
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }

    access_log /var/log/nginx/{{DOMAIN}}_access.log;
    error_log /var/log/nginx/{{DOMAIN}}_error.log;
}
```

---

## 4. 负载均衡（多实例）

```nginx
upstream {{APP_NAME}}_cluster {
    # 负载均衡策略：
    # - 默认轮询（round-robin）
    # - least_conn: 最少连接
    # - ip_hash: IP 哈希（会话保持）
    {{LB_METHOD:-least_conn}};

    server 127.0.0.1:{{PORT_1}} weight=3;
    server 127.0.0.1:{{PORT_2}} weight=3;
    server 127.0.0.1:{{PORT_3}} weight=3 backup;

    keepalive 64;
}

server {
    listen 80;
    listen [::]:80;
    server_name {{DOMAIN}};

    client_max_body_size {{MAX_BODY_SIZE:-50m}};

    location / {
        proxy_pass http://{{APP_NAME}}_cluster;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 失败重试
        proxy_next_upstream error timeout http_502 http_503;
        proxy_next_upstream_tries 3;
        proxy_next_upstream_timeout 10s;
    }

    access_log /var/log/nginx/{{DOMAIN}}_access.log;
    error_log /var/log/nginx/{{DOMAIN}}_error.log;
}
```

---

## 5. SSL 配置片段（certbot 自动添加，或手动使用）

```nginx
# 在 certbot 成功后，server block 会自动添加以下内容。
# 如需手动配置，可使用此模板：

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name {{DOMAIN}};

    ssl_certificate /etc/letsencrypt/live/{{DOMAIN}}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{{DOMAIN}}/privkey.pem;

    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/{{DOMAIN}}/chain.pem;

    # ... 其他 location 配置同上 ...
}

# HTTP → HTTPS 重定向
server {
    listen 80;
    listen [::]:80;
    server_name {{DOMAIN}};
    return 301 https://$host$request_uri;
}
```

---

## 6. API 网关模式（路径路由到多个后端）

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name {{DOMAIN}};

    # API v1 → 后端服务 A
    location /api/v1/ {
        proxy_pass http://127.0.0.1:{{PORT_API_V1}}/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API v2 → 后端服务 B
    location /api/v2/ {
        proxy_pass http://127.0.0.1:{{PORT_API_V2}}/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态前端
    location / {
        root {{STATIC_DIR}};
        try_files $uri $uri/ /index.html;
    }

    # 速率限制（API 保护）
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:{{PORT_API_V1}}/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    access_log /var/log/nginx/{{DOMAIN}}_access.log;
    error_log /var/log/nginx/{{DOMAIN}}_error.log;
}
```

---

## 变量说明

| 变量 | 说明 | 示例 |
|------|------|------|
| `{{DOMAIN}}` | 域名 | `example.com` |
| `{{APP_NAME}}` | 应用名称 | `my-api` |
| `{{PORT}}` | 后端端口 | `3000` |
| `{{STATIC_DIR}}` | 静态文件目录 | `/var/www/html` |
| `{{MAX_BODY_SIZE}}` | 最大请求体 | `50m` |
| `{{WS_PATH}}` | WebSocket 路径 | `/ws` |
| `{{LB_METHOD}}` | 负载均衡策略 | `least_conn` |
