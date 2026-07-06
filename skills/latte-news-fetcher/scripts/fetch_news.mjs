#!/usr/bin/env node

/**
 * News Fetcher - 新闻获取工具 v2
 * 
 * 用法:
 *   node fetch_news.mjs <url>
 *   node fetch_news.mjs <url> --method smry
 *   node fetch_news.mjs <url> --method jina
 *   node fetch_news.mjs <url> --search "关键词"
 *   node fetch_news.mjs <url> --all
 */

import fetch from 'node-fetch';

const TAVILY_API_KEY = process.env.TAVILY_API_KEY;

const args = process.argv.slice(2);
const url = args.find(a => !a.startsWith('--'));
const methodIndex = args.indexOf('--method');
const method = methodIndex > -1 ? args[methodIndex + 1] : 'auto';
const searchIndex = args.indexOf('--search');
const searchQuery = searchIndex > -1 ? args[searchIndex + 1] : null;
const useAll = args.includes('--all');

if (!url && !searchQuery) {
  console.log('News Fetcher v2 - 新闻获取工具\n');
  console.log('用法:');
  console.log('  node fetch_news.mjs <url>');
  console.log('  node fetch_news.mjs <url> --method smry|jina|12ft|direct');
  console.log('  node fetch_news.mjs <url> --search "关键词"');
  console.log('  node fetch_news.mjs <url> --all  # 尝试所有方法');
  console.log('\n方法说明:');
  console.log('  smry  - smry.ai（推荐）');
  console.log('  jina   - r.jina.ai（文本提取）');
  console.log('  12ft   - 12ft.io');
  console.log('  direct - 直接访问');
  process.exit(1);
}

// 工具 URL 构建器
const tools = {
  smry: (url) => `https://smry.ai/${url}`,
  jina: (url) => `https://r.jina.ai/http://${url}`,
  '12ft': (url) => `https://12ft.io/${url}`,
  removepaywalls: (url) => `https://removepaywalls.com/${url}`,
  direct: (url) => url
};

// 使用 Tavily extract
async function extractWithTavily(targetUrl) {
  if (!TAVILY_API_KEY) {
    throw new Error('需要设置 TAVILY_API_KEY 环境变量');
  }

  const response = await fetch('https://api.tavily.com/extract', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${TAVILY_API_KEY}`
    },
    body: JSON.stringify({
      urls: [targetUrl],
      extract_depth: 'advanced'
    })
  });

  const data = await response.json();
  
  if (data.results && data.results.length > 0) {
    return data.results[0];
  }
  
  throw new Error(data.error || '提取失败');
}

// 直接获取
async function fetchDirect(targetUrl) {
  const response = await fetch(targetUrl, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  const text = await response.text();
  return { raw_content: text };
}

// 搜索替代文章
async function searchAlternatives(query) {
  if (!TAVILY_API_KEY) {
    throw new Error('需要设置 TAVILY_API_KEY 环境变量');
  }

  const response = await fetch('https://api.tavily.com/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${TAVILY_API_KEY}`
    },
    body: JSON.stringify({
      query: `${query} (site:bbc.com OR site:reuters.com OR site:apnews.com OR site:aljazeera.com)`,
      max_results: 10
    })
  });

  const data = await response.json();
  return data.results || [];
}

// 尝试单个方法
async function tryMethod(originalUrl, methodName) {
  const targetUrl = tools[methodName](originalUrl);
  
  console.log(`  尝试 ${methodName}: ${targetUrl.substring(0, 60)}...`);
  
  try {
    let result;
    
    if (methodName === 'direct') {
      result = await fetchDirect(targetUrl);
    } else if (methodName === 'jina') {
      const response = await fetch(targetUrl);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const text = await response.text();
      result = { raw_content: text };
    } else {
      result = await extractWithTavily(targetUrl);
    }
    
    if (result.raw_content && result.raw_content.length > 300) {
      return {
        success: true,
        method: methodName,
        content: result.raw_content,
        length: result.raw_content.length
      };
    }
    
    return { success: false, reason: '内容不足' };
  } catch (err) {
    return { success: false, reason: err.message };
  }
}

// 主函数
async function main() {
  console.log('━'.repeat(50));
  console.log('📰 News Fetcher v2');
  console.log('━'.repeat(50) + '\n');

  // 搜索模式
  if (searchQuery) {
    console.log(`🔍 搜索替代文章: "${searchQuery}"\n`);
    const results = await searchAlternatives(searchQuery);
    
    if (results.length === 0) {
      console.log('❌ 未找到替代文章');
      return;
    }
    
    console.log(`✓ 找到 ${results.length} 篇相关文章:\n`);
    results.forEach((r, i) => {
      console.log(`${i + 1}. ${r.title || '无标题'}`);
      console.log(`   📎 ${r.url}`);
      if (r.content) {
        console.log(`   📝 ${r.content.substring(0, 100)}...`);
      }
      console.log('');
    });
    return;
  }

  // 获取模式
  console.log(`🔗 原始链接: ${url}`);
  console.log(`🎯 方法: ${method}\n`);

  // 确定要尝试的方法
  const methodsToTry = useAll 
    ? ['smry', 'jina', '12ft', 'direct'] 
    : (method === 'auto' ? ['smry', 'jina', '12ft'] : [method]);

  // 尝试每个方法
  for (const m of methodsToTry) {
    const result = await tryMethod(url, m);
    
    if (result.success) {
      console.log(`\n✅ 成功获取 (${result.method})`);
      console.log(`   📊 ${result.length} 字符\n`);
      console.log('─'.repeat(50));
      console.log('📄 文章内容:\n');
      console.log(result.content);
      return;
    }
    
    console.log(`   ❌ ${result.reason}`);
  }

  // 全部失败
  console.log('\n' + '─'.repeat(50));
  console.log('❌ 所有方法都失败了\n');
  console.log('💡 建议:');
  console.log('   1. 搜索替代信源（BBC/Reuters/AP）');
  console.log('   2. 使用浏览器扩展 Bypass Paywalls Clean');
  console.log('   3. 尝试禁用 JavaScript');
  console.log('   4. 换用 r.jina.ai/http://链接');
}

main().catch(err => {
  console.error('\n❌ 错误:', err.message);
  process.exit(1);
});
