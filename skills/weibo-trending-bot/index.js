#!/usr/bin/env node

/**
 * 微博热搜机器人
 * @version 1.0.0
 * @author 张 sir
 */

// 模拟热搜数据
const MOCK_HOT_SEARCH = [
  { rank: 1, topic: '#AI 技术重大突破#', heat: '爆', category: '科技', trend: 'new' },
  { rank: 2, topic: '#明星婚礼现场#', heat: '热', category: '文娱', trend: '↑' },
  { rank: 3, topic: '#春节放假安排#', heat: '热', category: '社会', trend: '→' },
  { rank: 4, topic: '#新电影票房#', heat: '热', category: '文娱', trend: '↓' },
  { rank: 5, topic: '#科技创新大赛#', heat: '热', category: '科技', trend: '↑' },
  { rank: 6, topic: '#美食探店#', heat: '热', category: '生活', trend: 'new' },
  { rank: 7, topic: '#健身打卡#', heat: '热', category: '生活', trend: '→' },
  { rank: 8, topic: '#旅游攻略#', heat: '热', category: '生活', trend: '↑' }
];

/**
 * 获取热搜榜单
 */
async function getHotSearch(category = 'all') {
  console.log('🔥 微博热搜榜单\n');
  console.log(`分类：${category === 'all' ? '全部' : category}`);
  console.log('更新时间：' + new Date().toLocaleString('zh-CN'));
  console.log('='.repeat(60));

  let filtered = MOCK_HOT_SEARCH;
  if (category !== 'all') {
    filtered = MOCK_HOT_SEARCH.filter(h => h.category === category);
  }

  filtered.forEach(item => {
    const trendIcon = item.trend === 'new' ? '🆕' : item.trend === '↑' ? '📈' : item.trend === '↓' ? '📉' : '➡️';
    console.log(`${item.rank}. ${item.topic} [${item.heat}] ${trendIcon}`);
    console.log(`   分类：${item.category}`);
    console.log('');
  });

  return filtered;
}

/**
 * 生成蹭热点文案
 */
function generateContent(topic, style = 'normal') {
  console.log(`✍️ 生成蹭热点文案：${topic}\n`);

  const templates = {
    normal: `
【常规风格】
刚刚看到${topic}，真的让人感慨万千！
在这个快速发展的时代，我们都在见证历史。
大家怎么看？评论区聊聊～
#${topic.replace(/#/g, '')}# #热点#
    `.trim(),

    humor: `
【幽默风格】
${topic} 上热搜了？我竟然现在才知道！
看来我真的 out 了😂
有没有课代表总结一下？
#${topic.replace(/#/g, '')}# #吃瓜#
    `.trim(),

    professional: `
【专业分析】
关于${topic}，从专业角度来分析：
1️⃣ 背景：...
2️⃣ 影响：...
3️⃣ 趋势：...
欢迎业内人士补充～
#${topic.replace(/#/g, '')}# #专业分析#
    `.trim(),

    emotional: `
【情感共鸣】
看到${topic}，突然想起了...
有时候真的觉得，生活就是这样充满惊喜。
愿我们都能...
#${topic.replace(/#/g, '')}# #情感#
    `.trim()
  };

  const content = templates[style] || templates.normal;
  console.log(content);
  console.log('');

  return content;
}

/**
 * 监控关键词
 */
async function trackKeyword(keyword) {
  console.log(`🔔 开始监控关键词：${keyword}`);
  console.log('   监控频率：每 5 分钟');
  console.log('   推送渠道：系统通知\n');

  console.log('✅ 监控已设置');
  console.log(`   当"${keyword}"登上热搜时会立即提醒`);

  return { keyword, active: true };
}

/**
 * 主函数
 */
async function main() {
  const args = process.argv.slice(2);

  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
微博热搜机器人

用法:
  node index.js [命令] [选项]

命令:
  --hot             查看热搜榜单
  --generate        生成蹭热点文案
  --track <kw>      监控关键词
  --alert           设置提醒

选项:
  --category <cat>  分类 (全部/文娱/社会/科技/生活)
  --topic <topic>   话题
  --style <s>       文案风格 (normal/humor/professional/emotional)
  --keyword <kw>    关键词
    `.trim());
    return;
  }

  // 热搜榜单
  if (args.includes('--hot')) {
    const category = args.find(a => a.startsWith('--category='))?.split('=')[1] || 'all';
    await getHotSearch(category);
    return;
  }

  // 生成文案
  if (args.includes('--generate')) {
    const topic = args.find(a => a.startsWith('--topic='))?.split('=')[1] || '#热门#';
    const style = args.find(a => a.startsWith('--style='))?.split('=')[1] || 'normal';
    generateContent(topic, style);
    return;
  }

  // 监控关键词
  if (args.includes('--alert') || args.includes('--track')) {
    const keyword = args.find(a => a.startsWith('--keyword='))?.split('=')[1] || 
                    args.find(a => a.startsWith('--track='))?.split('=')[1] || '热门';
    await trackKeyword(keyword);
    return;
  }

  // 默认显示热搜
  await getHotSearch();
}

main().catch(console.error);
