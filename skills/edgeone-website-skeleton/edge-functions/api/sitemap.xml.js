/**
 * Sitemap API — Edge Function
 *
 * Phase 3 L2-1 实现
 *
 * GET /api/sitemap.xml
 * 返回：XML Sitemap
 *
 * EdgeOne Pages 缓存：5 分钟 TTL
 */

import { generateSitemapXml } from '../sharing/seo-helpers.js';

export async function onRequest(context) {
  const { env } = context;
  const baseUrl = env.SITE_URL || 'https://example.com';

  try {
    // 从 KV 缓存读取产品列表（TTL 5 分钟）
    const cacheKey = 'sitemap:products';
    const cached = await env.KV.get(cacheKey);

    let productUrls = [];
    if (cached) {
      productUrls = JSON.parse(cached);
    } else {
      // 从 MySQL 读取（通过 Cloud Function 回源）
      // 实际实现中可通过内部 HTTP 调用获取
      productUrls = [];
    }

    // 静态页面
    const staticUrls = [
      { loc: `${baseUrl}/`, changefreq: 'daily', priority: '1.0' },
      { loc: `${baseUrl}/login`, changefreq: 'monthly', priority: '0.3' },
      { loc: `${baseUrl}/register`, changefreq: 'monthly', priority: '0.3' },
      { loc: `${baseUrl}/cart`, changefreq: 'weekly', priority: '0.5' },
      { loc: `${baseUrl}/orders`, changefreq: 'weekly', priority: '0.5' },
    ];

    // 产品页（从产品列表生成）
    const productPageUrls = productUrls.map(p => ({
      loc: `${baseUrl}/products/${p.id}`,
      lastmod: p.updated_at || p.created_at,
      changefreq: 'weekly',
      priority: '0.8'
    }));

    const allUrls = [...staticUrls, ...productPageUrls];
    const xml = generateSitemapXml(allUrls);

    return new Response(xml, {
      status: 200,
      headers: {
        'Content-Type': 'application/xml; charset=utf-8',
        'Cache-Control': 'public, max-age=300, stale-while-revalidate=600' // 5 分钟缓存
      }
    });
  } catch (err) {
    console.error('[Sitemap] Error:', err);
    return new Response('<?xml version="1.0"?><urlset/>', {
      status: 200,
      headers: { 'Content-Type': 'application/xml' }
    });
  }
}
