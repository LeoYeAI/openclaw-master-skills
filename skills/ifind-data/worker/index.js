// ═══════════════════════════════════════════════════
// iFinD Billing Service - Cloudflare Worker
// 计费管理 + 3天试用期
// ═══════════════════════════════════════════════════

const SKILLPAY_BASE_URL = 'https://skillpay.me';
const SKILL_ID = 'cd901102-704f-458a-8f38-b36b5ce0f89f';
const CHARGE_AMOUNT = 0.0001;
const TRIAL_DAYS = 3;
const TRIAL_MS = TRIAL_DAYS * 24 * 60 * 60 * 1000;

export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    const url = new URL(request.url);

    if (url.pathname === '/charge' && request.method === 'POST') {
      return handleCharge(request, env);
    }
    if (url.pathname === '/balance' && request.method === 'GET') {
      return handleBalance(request, env);
    }
    if (url.pathname === '/trial-status' && request.method === 'GET') {
      return handleTrialStatus(request, env);
    }
    if (url.pathname === '/health') {
      return jsonResponse({ status: 'ok' });
    }

    return jsonResponse({ error: 'Not Found' }, 404);
  },
};

// ─── 试用期检查 ───
async function checkTrial(userId, env) {
  const key = `trial:${userId}`;
  const record = await env.TRIAL_KV.get(key);

  if (!record) {
    // 新用户，记录首次使用时间，开始试用
    const now = Date.now();
    await env.TRIAL_KV.put(key, JSON.stringify({ start: now, calls: 1 }));
    return { inTrial: true, remaining: TRIAL_DAYS, calls: 1 };
  }

  const data = JSON.parse(record);
  const elapsed = Date.now() - data.start;

  if (elapsed < TRIAL_MS) {
    // 试用期内，更新调用次数
    data.calls = (data.calls || 0) + 1;
    await env.TRIAL_KV.put(key, JSON.stringify(data));
    const remainingMs = TRIAL_MS - elapsed;
    const remainingDays = Math.ceil(remainingMs / (24 * 60 * 60 * 1000));
    return { inTrial: true, remaining: remainingDays, calls: data.calls };
  }

  // 试用期已过
  return { inTrial: false, remaining: 0, calls: data.calls };
}

// ─── 扣费（含试用期逻辑）───
async function handleCharge(request, env) {
  const body = await request.json().catch(() => null);
  if (!body || !body.user_id) {
    return jsonResponse({ error: 'missing user_id' }, 400);
  }

  const apiSecret = request.headers.get('X-Api-Secret');
  if (apiSecret !== env.API_SECRET) {
    return jsonResponse({ error: 'unauthorized' }, 401);
  }

  // 检查试用期
  const trial = await checkTrial(body.user_id, env);

  if (trial.inTrial) {
    // 试用期内，免费放行
    return jsonResponse({
      success: true,
      trial: true,
      trial_remaining_days: trial.remaining,
      trial_calls: trial.calls,
      message: `试用期内免费使用，剩余 ${trial.remaining} 天`,
    });
  }

  // 试用期已过，正常扣费
  const resp = await fetch(`${SKILLPAY_BASE_URL}/api/v1/billing/charge`, {
    method: 'POST',
    headers: {
      'X-API-Key': env.SKILLPAY_API_KEY,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: body.user_id,
      skill_id: SKILL_ID,
      amount: CHARGE_AMOUNT,
    }),
  });

  const data = await resp.json();

  // 余额不足时补充提示
  if (!data.success && data.payment_url) {
    data.message = '试用期已结束，余额不足，请点击链接充值 USDT 后继续使用';
  }

  return jsonResponse(data);
}

// ─── 查余额 ───
async function handleBalance(request, env) {
  const url = new URL(request.url);
  const userId = url.searchParams.get('user_id');
  if (!userId) {
    return jsonResponse({ error: 'missing user_id' }, 400);
  }

  const apiSecret = request.headers.get('X-Api-Secret');
  if (apiSecret !== env.API_SECRET) {
    return jsonResponse({ error: 'unauthorized' }, 401);
  }

  const resp = await fetch(
    `${SKILLPAY_BASE_URL}/api/v1/billing/balance?user_id=${encodeURIComponent(userId)}`,
    { headers: { 'X-API-Key': env.SKILLPAY_API_KEY } }
  );

  const data = await resp.json();
  return jsonResponse(data);
}

// ─── 查试用状态 ───
async function handleTrialStatus(request, env) {
  const url = new URL(request.url);
  const userId = url.searchParams.get('user_id');
  if (!userId) {
    return jsonResponse({ error: 'missing user_id' }, 400);
  }

  const apiSecret = request.headers.get('X-Api-Secret');
  if (apiSecret !== env.API_SECRET) {
    return jsonResponse({ error: 'unauthorized' }, 401);
  }

  const key = `trial:${userId}`;
  const record = await env.TRIAL_KV.get(key);

  if (!record) {
    return jsonResponse({ trial: true, remaining: TRIAL_DAYS, calls: 0, message: '尚未使用，首次调用开始计算试用期' });
  }

  const data = JSON.parse(record);
  const elapsed = Date.now() - data.start;

  if (elapsed < TRIAL_MS) {
    const remainingDays = Math.ceil((TRIAL_MS - elapsed) / (24 * 60 * 60 * 1000));
    return jsonResponse({ trial: true, remaining: remainingDays, calls: data.calls });
  }

  return jsonResponse({ trial: false, remaining: 0, calls: data.calls, message: '试用期已结束，需充值使用' });
}

// ─── 工具函数 ───
function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-Api-Secret',
  };
}

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', ...corsHeaders() },
  });
}
