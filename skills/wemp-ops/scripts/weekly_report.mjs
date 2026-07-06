#!/usr/bin/env node
/**
 * 公众号周报
 */
import {
  loadConfig, output, outputError, parseArgs, formatDate, getDaysAgo, calcChangeRate,
  readData, writeData,
  getUserSummary, getUserCumulate, getArticleSummary, listPublished
} from './lib/utils.mjs';

async function generateWeeklyReport() {
  const config = loadConfig();
  console.error('[周报] 生成本周周报...');

  const endDate = getDaysAgo(1);
  const startDate = getDaysAgo(7);
  console.error(`[周报] 统计范围: ${startDate} ~ ${endDate}`);

  let totalNew = 0, totalCancel = 0, totalRead = 0, totalShare = 0;
  const dailyData = [];

  for (let i = 7; i >= 1; i--) {
    const date = getDaysAgo(i);
    let dayNew = 0, dayCancel = 0, dayRead = 0, dayShare = 0;
    try {
      const u = await getUserSummary(date);
      for (const item of (u.list || [])) { dayNew += item.new_user || 0; dayCancel += item.cancel_user || 0; }
    } catch {}
    try {
      const a = await getArticleSummary(date);
      for (const item of (a.list || [])) { dayRead += item.int_page_read_count || 0; dayShare += item.share_count || 0; }
    } catch {}
    totalNew += dayNew; totalCancel += dayCancel; totalRead += dayRead; totalShare += dayShare;
    dailyData.push({ date, newUsers: dayNew, cancelUsers: dayCancel, netGrowth: dayNew - dayCancel, read: dayRead, share: dayShare });
  }

  const netGrowth = totalNew - totalCancel;

  // 累计用户
  let totalUsers = 0;
  try {
    const r = await getUserCumulate(endDate, endDate);
    if (r.list?.length) totalUsers = r.list[0].cumulate_user || 0;
  } catch {}

  // 上周对比
  const history = readData('weekly-history.json', { reports: [] });
  const last = history.reports?.length ? history.reports[history.reports.length - 1] : null;
  const growthRate = last ? calcChangeRate(netGrowth, last.netGrowth) : '-';
  const readChange = last ? calcChangeRate(totalRead, last.totalRead) : '-';

  // 日均
  const avgNew = (totalNew / 7).toFixed(1);
  const avgRead = (totalRead / 7).toFixed(0);

  // 最佳/最差日
  const bestDay = [...dailyData].sort((a, b) => b.netGrowth - a.netGrowth)[0];
  const worstDay = [...dailyData].sort((a, b) => a.netGrowth - b.netGrowth)[0];

  // 已发布文章
  let topArticles = [];
  try {
    const r = await listPublished(0, 10);
    topArticles = (r.item || []).slice(0, 5).map((item, idx) => ({
      rank: idx + 1, title: item.content?.news_item?.[0]?.title || '未知标题'
    }));
  } catch {}

  // 洞察
  let insight = '';
  if (netGrowth > 50) insight = `本周净增 ${netGrowth} 粉丝，增长强劲！继续保持内容输出节奏。`;
  else if (netGrowth > 0) insight = `本周净增 ${netGrowth} 粉丝，稳步增长。可以尝试增加推送频次。`;
  else insight = `本周净流失 ${Math.abs(netGrowth)} 粉丝，建议复盘内容方向和推送时间。`;

  const reportData = { startDate, endDate, totalNew, totalCancel, netGrowth, growthRate, totalUsers, totalRead, totalShare, readChange, avgNew, avgRead, bestDay, worstDay, topArticles, dailyData, insight };

  // 保存历史
  if (!history.reports) history.reports = [];
  history.reports.push({ startDate, endDate, netGrowth, totalRead, totalUsers, generatedAt: new Date().toISOString() });
  if (history.reports.length > 12) history.reports = history.reports.slice(-12);
  writeData('weekly-history.json', history);

  // 生成报告
  const lines = [
    `📊 **公众号周报** (${startDate} ~ ${endDate})`, `━━━━━━━━━━━━━━━━━━━━━━━━━━━━`, '',
    `**👥 用户数据**`,
    `• 新增关注: +${totalNew} (日均 ${avgNew})`,
    `• 取消关注: -${totalCancel}`,
    `• 净增长: ${netGrowth >= 0 ? '+' : ''}${netGrowth} (${growthRate})`,
    `• 累计粉丝: ${totalUsers.toLocaleString()}`, '',
    `**📖 阅读数据**`,
    `• 总阅读: ${totalRead.toLocaleString()} 次 (${readChange})`,
    `• 总分享: ${totalShare} 次`,
    `• 日均阅读: ${avgRead} 次`, '',
    `**📈 每日趋势**`,
  ];
  dailyData.forEach(d => {
    const g = d.netGrowth >= 0 ? `+${d.netGrowth}` : `${d.netGrowth}`;
    lines.push(`  ${d.date}: 粉丝${g}, 阅读${d.read}`);
  });
  lines.push('', `**🏆 表现**`,
    `• 最佳: ${bestDay.date} (净增 ${bestDay.netGrowth})`,
    `• 最差: ${worstDay.date} (净增 ${worstDay.netGrowth})`);
  if (topArticles.length) {
    lines.push('', `**🔥 本周文章**`);
    topArticles.forEach(a => lines.push(`${a.rank}. 《${a.title}》`));
  }
  lines.push('', `**💡 AI 洞察**`, insight, '', `━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);

  return { report: lines.join('\n'), data: reportData };
}

async function main() {
  try {
    const { report, data } = await generateWeeklyReport();
    console.error('\n' + report);
    output(true, { report, data });
  } catch (error) { outputError(error); }
}

main();
