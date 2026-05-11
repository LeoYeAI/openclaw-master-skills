/**
 * i18n — 核心工具函数
 *
 * Phase 3 L2-2 实现
 *
 * 使用方式：
 *   import { t, setLang, getLang } from './i18n.js';
 *
 *   // 在组件中
 *   <button>{t('nav.home')}</button>
 *
 *   // 切换语言
 *   setLang('en-US');
 *
 *   // 读取当前语言
 *   const lang = getLang();
 */

import { zhCN } from './zh-CN.js';
import { enUS } from './en-US.js';

export const SUPPORTED_LANGS = ['zh-CN', 'en-US'];
export const DEFAULT_LANG = 'zh-CN';

const translations = {
  'zh-CN': zhCN,
  'en-US': enUS,
};

/**
 * 当前语言（客户端状态，SSR 时 fallback 到 DEFAULT_LANG）
 */
let currentLang = DEFAULT_LANG;

/**
 * 获取当前语言
 */
export function getLang() {
  return currentLang;
}

/**
 * 设置当前语言
 * @param {string} lang - 'zh-CN' | 'en-US'
 */
export function setLang(lang) {
  if (SUPPORTED_LANGS.includes(lang)) {
    currentLang = lang;
    // 持久化到 localStorage
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('i18n:lang', lang);
    }
  }
}

/**
 * 初始化语言（从 localStorage 恢复）
 */
export function initLang() {
  if (typeof localStorage !== 'undefined') {
    const saved = localStorage.getItem('i18n:lang');
    if (saved && SUPPORTED_LANGS.includes(saved)) {
      currentLang = saved;
    } else {
      // 自动检测浏览器语言
      const browserLang = navigator.language || '';
      if (browserLang.startsWith('en')) {
        currentLang = 'en-US';
      }
    }
  }
  return currentLang;
}

/**
 * 翻译函数
 * @param {string} key - 点分隔路径，如 'nav.home' 或 'order.status.PENDING'
 * @param {string} [lang] - 语言，默认为 currentLang
 * @param {Object} [params] - 插值参数，如 { name: 'John' } → 'Hello, John'
 * @returns {string} 翻译结果，未找到时返回 key
 *
 * @example
 *   t('nav.home')                              → '首页'
 *   t('order.status.PENDING', 'en-US')         → 'Pending Payment'
 *   t('greeting', 'zh-CN', { name: '刘博' })    → '你好，刘博'
 */
export function t(key, lang, params) {
  const targetLang = lang || currentLang;
  const dict = translations[targetLang] || translations[DEFAULT_LANG];

  // 按点号拆解路径
  const keys = key.split('.');
  let value = dict;

  for (const k of keys) {
    value = value?.[k];
    if (value === undefined) break;
  }

  // 未找到，返回 key（开发时容易发现问题）
  if (value === undefined) {
    console.warn(`[i18n] Missing translation: "${key}" (lang: ${targetLang})`);
    return key;
  }

  // 插值处理
  if (typeof value === 'string' && params) {
    return value.replace(/\{(\w+)\}/g, (_, k) => params[k] !== undefined ? params[k] : `{${k}}`);
  }

  return value;
}

/**
 * 获取订单状态标签
 * @param {string} status - 状态码
 * @param {string} [lang]
 */
export function tOrderStatus(status, lang) {
  return t(`order.status.${status}`, lang);
}

/**
 * 格式化货币
 * @param {number} amount
 * @param {string} [lang]
 */
export function formatCurrency(amount, lang) {
  if (lang === 'en-US') {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount / 7.2); // 简化的 CNY→USD
  }
  return new Intl.NumberFormat('zh-CN', { style: 'currency', currency: 'CNY' }).format(amount);
}

/**
 * 格式化日期
 * @param {string|Date} date
 * @param {string} [lang]
 */
export function formatDate(date, lang) {
  const d = typeof date === 'string' ? new Date(date) : date;
  const targetLang = lang || currentLang;
  return new Intl.DateTimeFormat(targetLang === 'en-US' ? 'en-US' : 'zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(d);
}
