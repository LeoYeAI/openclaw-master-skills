# Middleware 参考文档

> **版本：** v2.2 · **Phase：** Layer 0（Core）
> **职责：** Platform Middleware（CORS/CSP/轻量认证）+ Edge Middleware（JWT 详细校验）

---

## 一、双层 Middleware 架构

```
┌──────────────────────────────────────────────────────────────┐
│           Platform Middleware（middleware.js）                    │
│  ① CORS 预检（OPTIONS）                                        │
│  ② CSP Header 注入                                             │
│  ③ 轻量 Bearer 检查（公开路径放行）                               │
│  ④ 支付回调 IP 白名单 → 直接 return，不进 Edge Middleware         │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│            Edge Functions Middleware（_middleware.js）              │
│  ⑤ JWT 详细校验（crypto.subtle）                                 │
│  ⑥ KV session 验证                                             │
│  ⑦ KV 限流计数器（滑动窗口）                                      │
└──────────────────────────────────────────────────────────────┘
```

### 为什么需要双层？

| 层级 | 执行时机 | 用途 |
|------|---------|------|
| Platform Middleware | **每个请求**（HTML/静态/API） | 全局安全头、CORS、支付回调 bypass |
| Edge Middleware | 仅 Edge Function 请求 | JWT 详细校验、KV 限流 |

---

## 二、Platform Middleware

```javascript
// middleware.js（项目根目录）

export function onRequest(context) {
  const { request, env, next } = context;
  const url = new URL(request.url);
  const pathname = url.pathname;

  // === ① CORS 预检 ===
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 204,
      headers: {
        'Access-Control-Allow-Origin': env.ALLOWED_ORIGIN || '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Max-Age': '86400'
      }
    });
  }

  // === ② CSP Header 注入（仅 HTML）===
  const contentType = request.headers.get('Content-Type') || '';
  if (contentType.includes('text/html')) {
    const response = next(); // 获取原始响应
    const CSP = [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline'", // Skill 生成代码含内联脚本
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      "font-src 'self' https://fonts.gstatic.com",
      "img-src 'self' data: https:",
      "connect-src 'self' https://api.edgeone.dev https://api.weixin.qq.com https://openapi.alipay.com",
      "frame-ancestors 'none'",
      "base-uri 'self'",
      "form-action 'self'"
    ].join('; ');

    const newHeaders = new Headers(response.headers);
    newHeaders.set('Content-Security-Policy', CSP);
    newHeaders.set('X-Content-Type-Options', 'nosniff');
    newHeaders.set('X-Frame-Options', 'DENY');
    newHeaders.set('Referrer-Policy', 'strict-origin-when-cross-origin');

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: newHeaders
    });
  }

  // === ③ 轻量 Bearer 检查（可选，放行公开 API）===
  const publicApiPrefixes = ['/api/products', '/api/categories'];
  if (publicApiPrefixes.some(p => pathname.startsWith(p))) {
    return next();
  }

  // === ④ 支付回调独立路径（IP 白名单 + 直接 return）===
  if (pathname === '/api/pay/wx-notify' || pathname === '/api/pay/ali-notify') {
    // 微信/支付宝 IP 白名单（可扩展）
    const allowedIps = [
      '101.226.90.0/24', // 微信支付
      '110.42.0.0/16',  // 支付宝
    ];
    const clientIp = request.headers.get('CF-Connecting-IP') ||
                    request.headers.get('X-Real-IP') || '';

    if (!isIpAllowed(clientIp, allowedIps)) {
      console.warn(`[Middleware] Blocked pay callback from IP: ${clientIp}`);
      return new Response('Forbidden', { status: 403 });
    }

    // 直接 return，不继续到 Edge Middleware（回调没有 JWT）
    return next();
  }

  return next();
}

function isIpAllowed(ip, allowedCidrs) {
  // 简化的 CIDR 判断
  return allowedCidrs.some(cidr => {
    const [range, bits] = cidr.split('/');
    return ip.startsWith(range.split('.').slice(0, parseInt(bits) / 8).join('.'));
  });
}
```

---

## 三、Edge Middleware（_middleware.js）

```javascript
// edge-functions/_middleware.js

import { verifyAccessToken, extractToken } from './utils/jwt-helper.js';
import { checkRateLimit } from './utils/rate-limit.js';

export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);

  // === 公开路径放行 ===
  const publicPaths = ['/api/products', '/api/categories'];
  if (publicPaths.some(p => url.pathname.startsWith(p))) {
    return context.next();
  }

  // === Auth 路径放行 ===
  if (url.pathname.startsWith('/api/auth/login') || url.pathname.startsWith('/api/auth/register')) {
    return context.next();
  }

  // === RT 刷新路径放行 ===
  if (url.pathname === '/api/auth/refresh') {
    return context.next();
  }

  // === 提取 + 验证 JWT ===
  const tokenData = extractToken(request);
  if (!tokenData) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), {
      status: 401, headers: { 'Content-Type': 'application/json' }
    });
  }

  const payload = await verifyAccessToken(tokenData.token, env);
  if (!payload) {
    return new Response(JSON.stringify({ error: 'Token expired or invalid' }), {
      status: 401, headers: { 'Content-Type': 'application/json' }
    });
  }

  // === 限流（AI 栈专用）===
  if (url.pathname.startsWith('/api/ai/')) {
    const clientId = payload.sub || request.headers.get('CF-Connecting-IP');
    const limit = payload.role === 'admin' ? 200 : 60; // admin 更高限额
    const { allowed, resetMs } = await checkRateLimit(context, `ai:${clientId}`, limit);
    if (!allowed) {
      return new Response(JSON.stringify({ error: 'Rate limited' }), {
        status: 429,
        headers: { 'Retry-After': String(Math.ceil(resetMs / 1000)) }
      });
    }
  }

  // 注入用户信息到 request.headers（Edge Function 可读取）
  const newRequest = new Request(request, {
    headers: new Headers(request.headers)
  });
  newRequest.headers.set('X-User-Id', payload.sub);
  newRequest.headers.set('X-User-Role', payload.role);

  return context.next();
}
```

---

## 四、响应头汇总

| Header | 值 | 注入位置 |
|--------|-----|---------|
| `Content-Security-Policy` | CSP 指令 | Platform（HTML） |
| `X-Content-Type-Options` | `nosniff` | Platform |
| `X-Frame-Options` | `DENY` | Platform |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Platform |
| `X-User-Id` | 用户 ID | Edge Middleware |
| `X-User-Role` | `user/admin` | Edge Middleware |
| `Access-Control-Allow-Origin` | `*` | Platform（CORS） |
