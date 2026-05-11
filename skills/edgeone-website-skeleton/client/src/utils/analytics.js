/**
 * Analytics — 轻量埋点 SDK
 *
 * Phase 3 L2-3 实现
 *
 * 使用方式：
 *   import { track, trackPageView, trackAddToCart, trackPurchase } from './analytics.js';
 *
 *   // 页面访问
 *   trackPageView();
 *
 *   // 加入购物车
 *   trackAddToCart({ id: 1, name: '键盘', price: 299 });
 *
 *   // 支付成功
 *   trackPurchase({ orderId: 'WX20260426001', amount: 299 });
 */

import { getUserId, getSessionId } from './auth.js';

const ANALYTICS_ENDPOINT = '/api/analytics/event';

/**
 * 基础埋点函数
 * @param {string} event - 事件名
 * @param {Object} properties - 自定义属性
 */
export function track(event, properties = {}) {
  const data = {
    event,
    properties,
    userId: getUserId() || null,
    sessionId: getSessionId() || getAnonymousId(),
    url: typeof location !== 'undefined' ? location.pathname : null,
    referrer: typeof document !== 'undefined' ? document.referrer : null,
    language: typeof navigator !== 'undefined' ? navigator.language : null,
    screenWidth: typeof screen !== 'undefined' ? screen.width : null,
    timestamp: Date.now()
  };

  // sendBeacon：页面卸载时也能发送，不阻塞导航
  if (typeof navigator !== 'undefined' && navigator.sendBeacon) {
    const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
    navigator.sendBeacon(ANALYTICS_ENDPOINT, blob);
  } else if (typeof fetch !== 'undefined') {
    // 兜底：fetch（异步，不阻塞）
    fetch(ANALYTICS_ENDPOINT, {
      method: 'POST',
      body: JSON.stringify(data),
      headers: { 'Content-Type': 'application/json' },
      keepalive: true
    }).catch(() => {}); // 埋点失败不报错
  }
}

/**
 * 页面访问
 */
export function trackPageView() {
  track('page_view', {
    path: typeof location !== 'undefined' ? location.pathname : null,
    title: typeof document !== 'undefined' ? document.title : null
  });
}

/**
 * 加入购物车
 */
export function trackAddToCart(product) {
  track('add_to_cart', {
    product_id: product.id,
    product_name: product.name,
    category: product.category,
    price: product.price,
    quantity: product.qty || 1
  });
}

/**
 * 从购物车移除
 */
export function trackRemoveFromCart(product) {
  track('remove_from_cart', {
    product_id: product.id,
    product_name: product.name,
    price: product.price,
    quantity: product.qty || 1
  });
}

/**
 * 开始结账
 */
export function trackCheckoutStart(cartItems, total) {
  track('checkout_start', {
    item_count: cartItems.length,
    total,
    items: cartItems.map(i => ({ id: i.id, price: i.price, qty: i.qty }))
  });
}

/**
 * 支付成功
 */
export function trackPurchase(order) {
  track('purchase', {
    order_id: order.orderId,
    order_no: order.orderNo,
    amount: order.amount,
    payment_method: order.paymentMethod || 'unknown'
  });
}

/**
 * 注册成功
 */
export function trackSignup(userId) {
  track('signup', { user_id: userId });
}

/**
 * 登录成功
 */
export function trackLogin(userId) {
  track('login', { user_id: userId });
}

/**
 * 搜索
 */
export function trackSearch(query, resultCount) {
  track('search', { query, result_count: resultCount });
}

/**
 * 获取匿名用户 ID（基于 localStorage）
 */
function getAnonymousId() {
  if (typeof localStorage === 'undefined') return null;
  let anonId = localStorage.getItem('analytics:anon_id');
  if (!anonId) {
    anonId = `anon_${Date.now()}_${Math.random().toString(36).slice(2)}`;
    localStorage.setItem('analytics:anon_id', anonId);
  }
  return anonId;
}

// ===================== 自动页面埋点 =====================

/**
 * 初始化页面埋点（页面加载时调用一次）
 */
export function initAnalytics() {
  if (typeof document === 'undefined') return;

  // 首次访问埋点
  trackPageView();

  // SPA 路由变化监听（History API 页面）
  const originalPushState = history.pushState;
  history.pushState = function (...args) {
    originalPushState.apply(this, args);
    trackPageView();
  };
  window.addEventListener('popstate', () => trackPageView());
}
