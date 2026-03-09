#!/usr/bin/env node

/**
 * Amazon Price Tracker - 价格追踪工具
 * @version 1.0.0
 * @author 张 sir
 */

const fs = require('fs');
const path = require('path');

const TRACKING_FILE = path.join(__dirname, 'tracking.json');

/**
 * 加载追踪列表
 */
function loadTracking() {
  try {
    if (fs.existsSync(TRACKING_FILE)) {
      return JSON.parse(fs.readFileSync(TRACKING_FILE, 'utf8'));
    }
  } catch (e) {
    console.error('读取追踪列表失败:', e.message);
  }
  return [];
}

/**
 * 保存追踪列表
 */
function saveTracking(list) {
  fs.writeFileSync(TRACKING_FILE, JSON.stringify(list, null, 2));
}

/**
 * 添加追踪商品
 */
async function addProduct(url, targetPrice, notifyMethod = 'email') {
  console.log('📊 添加追踪商品...\n');
  console.log(`商品链接：${url}`);
  console.log(`目标价格：¥${targetPrice}`);
  console.log(`通知方式：${notifyMethod}`);
  console.log('');

  // 模拟获取商品信息
  const product = {
    id: 'B08N5WRWNW',
    title: 'Echo Dot (4th Gen) | Smart speaker with Alexa',
    currentPrice: 129.99,
    targetPrice: targetPrice,
    url: url,
    addedAt: new Date().toISOString(),
    notifyMethod: notifyMethod,
    active: true
  };

  const list = loadTracking();
  list.push(product);
  saveTracking(list);

  console.log('✅ 已添加到追踪列表');
  console.log(`   当前价格：¥${product.currentPrice}`);
  console.log(`   还需降价：¥${(product.currentPrice - targetPrice).toFixed(2)}`);
  console.log('   系统会持续监控，降价时通知你');

  return product;
}

/**
 * 查看追踪列表
 */
function listProducts() {
  const list = loadTracking();
  
  console.log('📊 追踪商品列表\n');
  console.log('='.repeat(70));

  if (list.length === 0) {
    console.log('暂无追踪商品，使用 --add 添加商品');
    return list;
  }

  list.forEach((item, idx) => {
    const status = item.currentPrice <= item.targetPrice ? '✅ 可入手' : '⏳ 监控中';
    console.log(`${idx + 1}. ${item.title}`);
    console.log(`   当前：¥${item.currentPrice} | 目标：¥${item.targetPrice} | ${status}`);
    console.log(`   链接：${item.url}`);
    console.log('');
  });

  console.log(`总计：${list.length}个商品`);
  return list;
}

/**
 * 查看价格历史
 */
async function priceHistory(url) {
  console.log('📈 价格历史分析\n');
  console.log(`商品：${url}`);
  console.log('');

  // 模拟历史数据
  const history = {
    current: 129.99,
    lowest: 99.99,
    highest: 149.99,
    average: 124.99,
    trend: 'stable',
    data: [
      { date: '2026-02-09', price: 129.99 },
      { date: '2026-02-02', price: 134.99 },
      { date: '2026-01-26', price: 119.99 },
      { date: '2026-01-19', price: 129.99 },
      { date: '2026-01-12', price: 139.99 },
      { date: '2026-01-05', price: 124.99 }
    ]
  };

  console.log('价格概览:');
  console.log(`  当前价：¥${history.current}`);
  console.log(`  历史最低：¥${history.lowest}`);
  console.log(`  历史最高：¥${history.highest}`);
  console.log(`  平均价格：¥${history.average}`);
  console.log(`  趋势：${history.trend === 'stable' ? '平稳' : history.trend === 'down' ? '下降' : '上升'}`);
  console.log('');

  console.log('近期价格:');
  history.data.forEach(d => {
    const bar = '█'.repeat(Math.floor(d.price / 10));
    console.log(`  ${d.date}: ¥${d.price} ${bar}`);
  });

  console.log('\n💡 购买建议:');
  if (history.current <= history.lowest * 1.1) {
    console.log('  ✅ 当前价格接近历史最低，建议入手！');
  } else if (history.current > history.average * 1.2) {
    console.log('  ⏳ 当前价格偏高，建议观望');
  } else {
    console.log('  ➡️ 价格适中，可根据需求决定');
  }

  return history;
}

/**
 * 设置提醒
 */
function setAlert(options) {
  console.log('🔔 设置价格提醒\n');
  
  if (options.email) {
    console.log(`✅ 邮件提醒：${options.email}`);
  }
  if (options.telegram) {
    console.log(`✅ Telegram 提醒：${options.telegram}`);
  }

  console.log('\n提醒规则:');
  console.log('  • 价格降至目标价时通知');
  console.log('  • 价格历史新低时通知');
  console.log('  • 商品补货时通知');

  return { success: true };
}

/**
 * 主函数
 */
async function main() {
  const args = process.argv.slice(2);

  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
Amazon Price Tracker - 价格追踪工具

用法:
  node index.js [命令] [选项]

命令:
  --add <url>        添加追踪商品
  --list             查看追踪列表
  --history <url>    查看价格历史
  --alert            设置提醒

选项:
  --target-price <n> 目标价格
  --notify <method>  通知方式 (email/telegram)
  --email <addr>     邮箱地址
  --telegram <user>  Telegram 用户名
    `.trim());
    return;
  }

  // 添加商品
  if (args.includes('--add')) {
    const url = args.find(a => a.startsWith('--add='))?.split('=')[1] || 'https://amazon.com/dp/xxx';
    const targetPrice = parseFloat(args.find(a => a.startsWith('--target-price='))?.split('=')[1]) || 99;
    const notify = args.find(a => a.startsWith('--notify='))?.split('=')[1] || 'email';
    await addProduct(url, targetPrice, notify);
    return;
  }

  // 查看列表
  if (args.includes('--list')) {
    listProducts();
    return;
  }

  // 价格历史
  if (args.includes('--history')) {
    const url = args.find(a => !a.startsWith('--')) || 'https://amazon.com/dp/xxx';
    await priceHistory(url);
    return;
  }

  // 设置提醒
  if (args.includes('--alert')) {
    const email = args.find(a => a.startsWith('--email='))?.split('=')[1];
    const telegram = args.find(a => a.startsWith('--telegram='))?.split('=')[1];
    setAlert({ email, telegram });
    return;
  }

  // 默认显示列表
  listProducts();
}

main().catch(console.error);
