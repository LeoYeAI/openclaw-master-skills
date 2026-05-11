/**
 * KV Key 命名规范 — 多租户前缀支持
 *
 * Phase 3 L3-1 实现
 *
 * Phase 3: Key 前缀占位符 = "default"（向后兼容）
 * Phase 4: Key 前缀从 JWT payload.tenant 动态读取
 *
 * 使用方式：
 *   import { makeKey, getTenant } from './kv-keys.js';
 *
 *   // 当前租户
 *   const tenant = getTenant(payload); // 从 JWT 读取，默认 "default"
 *
 *   // Session key
 *   kv.get(makeKey(tenant, 'session', sessionId));
 *
 *   // Refresh Token key
 *   kv.get(makeKey(tenant, 'rt', userId, 'meta'));
 */

// ===================== 常量 =====================

/**
 * Phase 3 默认租户（向后兼容）
 * Phase 4 中替换为 JWT payload.tenant
 */
export const DEFAULT_TENANT = 'default';

/**
 * Key 前缀名称（用于 KV 命名约定）
 */
export const KEY_PREFIXES = {
  SESSION:         'session',
  REFRESH_TOKEN:   'rt',
  CART:            'cart',
  AI_SESSION:      'ai',
  IDEMPOTENCY:     'pay:idempotency',
  RATE_LIMIT:      'rl',
  ANALYTICS:       'analytics',
  PRODUCT_CACHE:   'product',
};

/**
 * Key TTL 定义（秒）
 */
export const KEY_TTL = {
  SESSION:         86400,     // 24h
  REFRESH_TOKEN:    604800,   // 7d
  CART:             2592000,  // 30d
  AI_SESSION:       86400,    // 24h
  IDEMPOTENCY:      86400,    // 24h（微信重试窗口内）
  RATE_LIMIT:       120,      // 2min（略超窗口宽）
  PRODUCT_CACHE:    300,      // 5min
  ANALYTICS:        7776000,  // 90d
};

// ===================== Key 生成 =====================

/**
 * 生成带租户前缀的 KV Key
 * @param {string} tenant - 租户 ID（从 JWT payload.tenant 获取）
 * @param {...string} parts - Key 组成部分
 * @returns {string} 完整 key，如 "default:session:abc123"
 */
export function makeKey(tenant, ...parts) {
  return [tenant, ...parts].join(':');
}

/**
 * 从 JWT payload 中提取租户 ID
 * @param {Object} payload - JWT payload
 * @returns {string} 租户 ID，未设置时返回 DEFAULT_TENANT
 */
export function getTenant(payload) {
  return payload?.tenant || DEFAULT_TENANT;
}

// ===================== 便捷函数 =====================

/**
 * Session Key
 */
export function sessionKey(tenant, sessionId) {
  return makeKey(tenant, KEY_PREFIXES.SESSION, sessionId);
}

/**
 * Refresh Token Meta Key
 */
export function rtMetaKey(tenant, userId) {
  return makeKey(tenant, KEY_PREFIXES.REFRESH_TOKEN, String(userId), 'meta');
}

/**
 * Cart Key
 */
export function cartKey(tenant, userId) {
  return makeKey(tenant, KEY_PREFIXES.CART, String(userId));
}

/**
 * AI Session Key
 */
export function aiSessionKey(tenant, userId, sessionId) {
  return makeKey(tenant, KEY_PREFIXES.AI_SESSION, String(userId), sessionId);
}

/**
 * 支付幂等 Key
 */
export function idempotencyKey(tenant, outTradeNo) {
  return makeKey(tenant, KEY_PREFIXES.IDEMPOTENCY, outTradeNo);
}

/**
 * 限流 Key
 */
export function rateLimitKey(tenant, identifier, windowKey) {
  return makeKey(tenant, KEY_PREFIXES.RATE_LIMIT, identifier, windowKey);
}

/**
 * 产品缓存 Key
 */
export function productCacheKey(tenant, productId) {
  return makeKey(tenant, KEY_PREFIXES.PRODUCT_CACHE, String(productId));
}

// ===================== 导出 makeKey（默认） =====================
export { makeKey as key };
