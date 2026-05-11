# KV Storage 参考文档

## 一、KV 命名空间设计

EdgeOne Pages 提供两个 KV Namespace：
- `auth_ns`：认证数据（user、session、refresh_token）
- `kv_ns`：业务数据（cart、order、product、ai_session）

Node Functions 必须单独绑定 auth_ns。

## 二、Key 命名规范（含租户前缀占位）

```typescript
// sharing/kv-keys.ts
// Phase 1 填固定值 "default"，Phase 3 替换为动态 tenantId

export const kvKey = {
  user: (tenantId, userId) => `${tenantId}:user:${userId}`,
  session: (tenantId, sessionId) => `${tenantId}:session:${sessionId}`,
  rtMeta: (tenantId, userId) => `${tenantId}:rt:${userId}:meta`,
  product: (tenantId, productId) => `${tenantId}:product:${productId}`,
  productList: (tenantId) => `${tenantId}:products:list`,
  cart: (tenantId, userId) => `${tenantId}:cart:${userId}`,
  order: (tenantId, orderId) => `${tenantId}:order:${orderId}`,
  orderByUser: (tenantId, userId) => `${tenantId}:orders:user:${userId}`,
  aiSession: (tenantId, userId, sessionId) => `${tenantId}:ai:${userId}:${sessionId}`,
  idempotency: (tradeNo) => `pay:idempotency:${tradeNo}`,
  rateLimit: (key, window) => `rl:${key}:${Math.floor(Date.now() / (window * 1000))}`,
};
```

## 三、分层查询策略

| 场景 | 实现 | 原因 |
|------|------|------|
| 单商品读取 | KV 缓存 | kv.get 极快 |
| 商品列表（首页，无筛选） | KV 第1页缓存 | 首页访问量最大 |
| 分类+价格筛选 | Cloud MySQL | KV 不支持复合条件 |
| 关键词搜索 | Cloud MySQL FULLTEXT | KV 不支持 LIKE |
| AI 会话历史 | KV list | kv.list('ai:${userId}:') |
| 订单统计（多条件聚合） | Cloud MySQL | KV 不支持聚合 |

## 四、索引 KV 模式

```javascript
// 写入订单时同步写入索引
await kv.put(`order:${orderId}`, JSON.stringify(order));
await kv.put(`idx:order:date:${dateStr}:${orderId}`, '1');
await kv.put(`idx:order:status:${status}:${orderId}`, '1');
await kv.put(`idx:order:user:${userId}:${orderId}`, '1');

// 查询"今日所有 PAID 订单"
const keys = await kv.list({ prefix: `idx:order:date:${today}:` });
const orderIds = keys.map(k => k.name.split(':').pop());
const orders = await Promise.all(orderIds.map(id => kv.get(`order:${id}`)));
```

## 五、数据过期策略

```javascript
kv.put(`session:${sessionId}`, data, { expirationTtl: 86400 });      // 24h
kv.put(`order:${orderId}`, data, { expirationTtl: 7776000 });          // 90d
kv.put(`ai_session:${userId}:${sessionId}`, data, { expirationTtl: 2592000 }); // 30d
kv.putIfNotExists(`pay:idempotency:${tradeNo}`, id, { expirationTtl: 86400 }); // 24h
```
