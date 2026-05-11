/**
 * Analytics Event API — Edge Function
 *
 * Phase 3 L2-3 实现
 *
 * POST /api/analytics/event
 * 接收埋点数据，写入 KV（轻量）或转发到外部分析服务
 *
 * 支持 sendBeacon 和 fetch 两种调用方式
 */

export async function onRequest(context) {
  const { env, request } = context;

  let body;
  try {
    body = await request.json();
  } catch {
    // sendBeacon 发来的是文本，需重试
    try {
      body = JSON.parse(await request.text());
    } catch {
      return new Response('ok', { status: 200 }); // 不影响业务
    }
  }

  const {
    event,
    properties = {},
    userId,
    sessionId,
    url,
    referrer,
    language,
    screenWidth,
    timestamp
  } = body;

  // 基本校验
  if (!event || !timestamp) {
    return new Response('ok', { status: 200 });
  }

  try {
    // === 方式 1：写入 KV（本地存储，支持 Basic Analytics）===
    await writeToKV(env.KV, { event, properties, userId, sessionId, url, timestamp });

    // === 方式 2：转发到外部分析服务（如需要）===
    // if (env.ANALYTICS_ENDPOINT) {
    //   await fetch(env.ANALYTICS_ENDPOINT, {
    //     method: 'POST',
    //     body: JSON.stringify(body),
    //     headers: { 'Content-Type': 'application/json' }
    //   });
    // }

  } catch (err) {
    // 埋点失败不阻塞
    console.warn('[Analytics] Failed to store event:', err.message);
  }

  return new Response('ok', { status: 200 });
}

/**
 * 写入 KV（轻量事件存储）
 */
async function writeToKV(kv, data) {
  const { event, userId, timestamp } = data;

  // 按日期分桶：analytics:{date}:{event}:{count}
  const date = new Date(timestamp).toISOString().split('T')[0];
  const countKey = `analytics:${date}:count:${event}`;

  // 原子递增（近似计数，非精确）
  const current = parseInt(await kv.get(countKey) || '0');
  await kv.put(countKey, String(current + 1), { expirationTtl: 90 * 86400 }); // 90 天 TTL

  // 用户级聚合（最近 7 天活跃）
  if (userId) {
    const userKey = `analytics:user:${userId}:last`;
    await kv.put(userKey, timestamp, { expirationTtl: 7 * 86400 });
  }
}
