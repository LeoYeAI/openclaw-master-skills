/**
 * SEO 工具 — JSON-LD + Meta Tags 生成
 *
 * Phase 3 L2-1 实现
 *
 * 使用方式：
 *   import { generateProductJsonLd, generateWebsiteJsonLd, generateMetaTags } from './seo.js';
 *
 *   // 产品页
 *   const jsonLd = generateProductJsonLd(product);
 *   <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
 *
 *   // 首页
 *   const websiteLd = generateWebsiteJsonLd({ name: '极客商城', url: 'https://...' });
 *   const meta = generateMetaTags({ title: '...', description: '...' });
 */

import { BASE_URL } from './constants.js';

// ===================== JSON-LD 生成器 =====================

/**
 * 网站基础信息（用于首页）
 */
export function generateWebsiteJsonLd({ name, description, url }) {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name,
    description,
    url,
    potentialAction: {
      '@type': 'SearchAction',
      target: {
        '@type': 'EntryPoint',
        urlTemplate: `${url}/search?q={search_term_string}`
      },
      'query-input': 'required name=search_term_string'
    },
    sameAs: []
  };
}

/**
 * 产品详情页 JSON-LD
 */
export function generateProductJsonLd(product) {
  const offers = {
    '@type': 'Offer',
    price: product.price,
    priceCurrency: 'CNY',
    availability: product.stock > 0
      ? 'https://schema.org/InStock'
      : 'https://schema.org/OutOfStock',
    seller: {
      '@type': 'Organization',
      name: product.seller || '极客商城'
    }
  };

  return {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.name,
    description: product.description || `${product.name}，正品保证`,
    image: product.image ? [product.image] : [],
    sku: product.id,
    category: product.category,
    offers,
    ...(product.brand && { brand: { '@type': 'Brand', name: product.brand } }),
    ...(product.rating && {
      aggregateRating: {
        '@type': 'AggregateRating',
        ratingValue: product.rating,
        reviewCount: product.reviewCount || 1
      }
    })
  };
}

/**
 * 商品列表页 JSON-LD（BreadcrumbList）
 */
export function generateBreadcrumbJsonLd(items) {
  // items: [{ name, item }]
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      item: item.item ? `${BASE_URL}${item.item}` : undefined
    }))
  };
}

/**
 * Organization JSON-LD（首页底部）
 */
export function generateOrganizationJsonLd({ name, logo, url }) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name,
    logo,
    url,
    contactPoint: {
      '@type': 'ContactPoint',
      telephone: '+86-400-XXX-XXXX',
      contactType: 'customer service',
      availableLanguage: ['Chinese', 'English']
    }
  };
}

// ===================== Meta Tags 生成 =====================

/**
 * 生成 <head> Meta 标签字符串
 * @param {Object} opts
 * @param {string} opts.title - 页面标题
 * @param {string} opts.description - 页面描述
 * @param {string} opts.image - 分享图片 URL
 * @param {string} opts.url - 页面 URL
 * @param {string} opts.type - og:type (website/product/article)
 * @param {string} opts.locale - 语言，默认 zh-CN
 */
export function generateMetaTags({
  title,
  description,
  image = `${BASE_URL}/og-default.png`,
  url,
  type = 'website',
  locale = 'zh_CN'
}) {
  const siteName = '极客商城';
  const fullTitle = title ? `${title} - ${siteName}` : siteName;
  const canonical = url ? `${BASE_URL}${url}` : BASE_URL;

  return {
    title: fullTitle,
    meta: {
      description,
      keywords: '', // 可按需填写
      author: siteName,
      // Open Graph
      'og:title': fullTitle,
      'og:description': description,
      'og:image': image,
      'og:url': canonical,
      'og:type': type,
      'og:site_name': siteName,
      'og:locale': locale,
      // Twitter Card
      'twitter:card': 'summary_large_image',
      'twitter:title': fullTitle,
      'twitter:description': description,
      'twitter:image': image,
      // Robots
      robots: 'index, follow'
    },
    link: {
      canonical
    }
  };
}

// ===================== Sitemap URL 生成 =====================

/**
 * 生成 Sitemap XML
 * @param {Object[]} urls - [{ loc, lastmod, changefreq, priority }]
 */
export function generateSitemapXml(urls) {
  const baseXml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`;

  const urlEntries = urls.map(u => {
    const lastmod = u.lastmod
      ? `\n    <lastmod>${new Date(u.lastmod).toISOString().split('T')[0]}</lastmod>`
      : '';
    const changefreq = u.changefreq
      ? `\n    <changefreq>${u.changefreq}</changefreq>`
      : '';
    const priority = u.priority !== undefined
      ? `\n    <priority>${u.priority}</priority>`
      : '';
    return `  <url>${lastmod}${changefreq}${priority}
    <loc>${escapeXml(u.loc)}</loc>
  </url>`;
  }).join('\n');

  return `${baseXml}\n${urlEntries}\n</urlset>`;
}

function escapeXml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

// ===================== Robots.txt =====================

export function generateRobotsTxt({ sitemapUrl }) {
  return [
    'User-agent: *',
    'Allow: /',
    `Sitemap: ${sitemapUrl}`,
    ''
  ].join('\n');
}
