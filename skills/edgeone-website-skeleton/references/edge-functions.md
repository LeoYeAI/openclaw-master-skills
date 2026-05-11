# Edge Functions 参考文档

> **版本：** v2.2 · **Phase：** Layer 0（Core）
> **职责：** Edge Middleware + 读操作 API + KV 访问

---

## 一、Edge Functions 概述

Edge Functions 运行在 **V8 引擎**，无密钥（密钥在 Cloud Functions），响应极快，适合读操作。

### 与 Cloud Functions 的职责划分

| 场景 | Edge Functions（V8 + KV） | Cloud Functions（Node.js） |
|------|--------------------------|---------------------------|
| JWT 校验 | ✅ crypto.subtle | — |
| KV 读写 | ✅ 原生访问 | ❌（通过 HTTP 调用 Edge） |
| Session 读取 | ✅ | — |
| 限流 | ✅ KV 滑动窗口 | — |
| 幂等锁 | ✅ putIfNotExists | — |
| 产品列表（无筛选） | ✅ KV 缓存 | — |
| 商品详情 | ✅ KV 缓存 | — |
| 订单创建 | — | ✅ SELECT FOR UPDATE |
| 用户注册（bcrypt） | — | ✅ |
| 支付回调 | — | ✅ 微信/支付宝 SDK |
| AI SSE 流 | — | ✅ waitUntil |

---

## 二、Edge Middleware（_middleware.js）

Edge Middleware 在**每个 Edge Function 请求**前执行：

```javascript
// edge-functions/_middleware.js

import { verifyAccessToken, extractToken } from './utils/jwt-helper.js';
import { checkRateLimit } from './utils/rate-limit.js';

export async function onRequest(context) {
  const { request, env } = context;

  // === 1. 公开路径放行 ===
  const publicPaths = ['/', '/login', '/register', '/api/products'];
  const url = new URL(request.url);
  if (publicPaths.some(p => url.pathname === p || url.pathname.startsWith(p + '/'))) {
    if (url.pathname.startsWith('/api/') && !url.pathname.startsWith('/api/auth/')) {
      // 公开 API（如产品列表）无需认证
    }
    return context.next(); // 继续到具体 Function
  }

  // === 2. 提取 Token ===
  const tokenData = extractToken(request);
  if (!tokenData) {
    return new Response('Unauthorized', { status: 401 });
  }

  // === 3. JWT 验证 ===
  const payload = await verifyAccessToken(tokenData.token, env);
  if (!payload) {
    return new Response('Invalid token', { status: 401 });
  }

  // === 4. 限流 ===
  const clientId = payload.sub || request.headers.get('CF-Connecting-IP');
  const { allowed } = await checkRateLimit(context, `global:${clientId}`, 100);
  if (!allowed) {
    return new Response('Rate limited', { status: 429, headers: { 'Retry-After': '60' } });
  }

  // === 5. 注入用户信息到 context ===
  // 方式 A：通过 x-user-id / x-user-role 响应头传递给具体 Function
  // 方式 B：Edge Function 直接调用 verifyAccessToken（推荐，减少中间件复杂度）
  return context.next();
}
```

---

## 三、常用 Edge API

### 3.1 获取当前用户

```javascript
// edge-functions/api/auth/me.js
export async function onRequest(context) {
  const { request, env } = context;
  const payload = await verifyAccessToken(extractToken(request)?.token, env);

  if (!payload) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401 });
  }

  // 从 KV 读取 Session 补充信息
  const session = await env.KV.get(`session:${payload.sub}`);
  const user = session ? JSON.parse(session) : { id: payload.sub, email: payload.email };

  return new Response(JSON.stringify(user), {
    headers: { 'Content-Type': 'application/json' }
  });
}
```

### 3.2 产品列表（KV 缓存 + 回源）

```javascript
// edge-functions/api/products/list.js

const CACHE_TTL = 300; // 5 min

export async function onRequest(context) {
  const { env } = context;

  // KV 读取（缓存命中）
  const cached = await env.KV.get('products:list:default');
  if (cached) {
    return new Response(cached, {
      headers: { 'Content-Type': 'application/json', 'X-Cache': 'HIT' }
    });
  }

  // 缓存未命中 → 回源 Cloud MySQL（通过内部 HTTP）
  const products = await fetch(`${env.EDGE_BASE}/internal/products`, {
    headers: { 'X-Internal-Key': env.INTERNAL_KEY }
  }).then(r => r.json());

  // 写入 KV
  await env.KV.put('products:list:default', JSON.stringify(products), {
    expirationTtl: CACHE_TTL
  });

  return new Response(JSON.stringify(products), {
    headers: { 'Content-Type': 'application/json', 'X-Cache': 'MISS' }
  });
}
```

### 3.3 KV 购物车

```javascript
// edge-functions/api/cart/*.js

// GET /api/cart — 读取购物车
export async function onRequest(context) {
  const { request, env } = context;
  const payload = await verifyAccessToken(extractToken(request)?.token, env);
  if (!payload) return new Response('Unauthorized', { status: 401 });

  const cart = await env.KV.get(`cart:${payload.sub}`);
  return new Response(cart || '[]', { headers: { 'Content-Type': 'application/json' } });
}

// POST /api/cart — 添加商品
// Body: { productId, qty }
export async function onRequest(context) {
  const { request, env } = context;
  const payload = await verifyAccessToken(extractToken(request)?.token, env);
  if (!payload) return new Response('Unauthorized', { status: 401 });

  const { productId, qty } = await request.json();
  const cart = JSON.parse(await env.KV.get(`cart:${payload.sub}`) || '[]');

  const existing = cart.find(i => i.productId === productId);
  if (existing) {
    existing.qty += qty;
  } else {
    cart.push({ productId, qty });
  }

  await env.KV.put(`cart:${payload.sub}`, JSON.stringify(cart), {
    expirationTtl: 30 * 86400 // 30 天
  });

  return new Response(JSON.stringify({ ok: true, cart }), {
    headers: { 'Content-Type': 'application/json' }
  });
}
```

---

## 四、KV Helper 封装

```javascript
// edge-functions/utils/kv-helper.js

/**
 * 安全的 KV 读取，返回 null 而不是抛错
 */
export async function kvGet(kv, key) {
  try {
    const value = await kv.get(key);
    return value ? JSON.parse(value) : null;
  } catch {
    return null;
  }
}

/**
 * 原子递增（用于计数器/限流）
 */
export async function kvIncr(kv, key) {
  const current = parseInt(await kv.get(key) || '0');
  await kv.put(key, String(current + 1));
  return current + 1;
}

/**
 * 乐观锁写入（version 字段）
 */
export async function kvUpdateWithVersion(kv, key, updateFn) {
  const data = await kvGet(kv, key);
  if (!data) return null;

  const newData = updateFn({ ...data });
  newData.version = (data.version || 0) + 1;

  // 比较并写入（Cloudflare KV 乐观锁近似实现）
  await kv.put(key, JSON.stringify(newData), { expirationTtl: 86400 });
  return newData;
}
```

---

## 五、环境变量（Edge Functions）

| 变量 | 必填 | 说明 |
|------|------|------|
| `JWT_PRIVATE_KEY` | ✅（Phase 3） | RS256 私钥 |
| `JWT_PUBLIC_KEY` | ✅（Phase 3） | RS256 公钥 |
| `JWT_SECRET` | ✅（兼容） | HS256 密钥（30 天兼容） |
| `EDGE_BASE` | ✅（电商） | Cloud Function 内部网关 |
| `INTERNAL_KEY` | ✅（电商） | 内部调用鉴权 |
| `SITE_URL` | 可选 | 站点 URL（SEO 用） |
