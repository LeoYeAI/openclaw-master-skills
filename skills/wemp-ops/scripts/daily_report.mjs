#!/usr/bin/env node
/**
 * 公众号日报
 */
import {
  loadConfig, output, outputError, parseArgs, formatDate, getYesterday, calcChangeRate,
  readData, writeData,
  getUserSummary, getUserCumulate, getArticleSummary, getUpstreamMsg, listPublished
} from './lib/utils.mjs';

async function generateDailyReport(date) {
  const config = loadConfig();
  const reportDate = date || getYesterday();
  console.error(`[日报] 生成 ${reportDate} 的日报...`);

  // 用户数据
  let newUsers = 0, cancelUsers = 0;
  try {
    const r = await getUserSummary(reportDate);
    for (const i of (r.list || [])) { newUsers += i.new_user || 0; cancelUsers += i.cancel_user || 0; }
  } catch (e) { console.error(`[日报] 用户数据失败: ${e.message}`); }
  const netGrowth = newUsers - cancelUsers;

  // 累计用户
  let totalUsers = 0;
  try {
    const r = await getUserCumulate(reportDate, reportDate);
    if (r.list?.length) totalUsers = r.list[0].cumulate_user || 0;
  } catch (e) { console.error(`[日报] 累计用户失败: ${e.message}`); }

  // 文章数据
  let totalRead = 0, totalShare = 0;
  try {
    const r = await getArticleSummary(reportDate);
    for (const i of (r.list || [])) { totalRead += i.int_page_read_count || 0; totalShare += i.share_count || 0; }
  } catch (e) { console.error(`[日报] 文章数据失败: ${e.message}`); }

  // 消息数据
  let newMessages = 0;
  try {
    const r = await getUpstreamMsg(reportDate);
    for (const i of (r.list || [])) { newMessages += i.msg_count || 0; }
  } catch (e) { console.error(`[日报] 消息数据失败: ${e.message}`); }

  // 已发布文章
  let topArticles = [];
  try {
    const r = await listPublished(0, 10);
    topArticles = (r.item || []).slice(0, config.analytics?.topArticles || 5).map((item, idx) => ({
      rank: idx + 1, title: item.content?.news_item?.[0]?.title || '未知标题'
    }));
  } catch (e) { console.error(`[日报] 已发布文章失败: ${e.message}`); }

  // 历史对比
  const history = readData('daily-history.json', { reports: [] });
  const last = history.reports?.length ? history.reports[history.reports.length - 1] : null;
  const growthRate = last ? calcChangeRate(netGrowth, last.netGrowth) : '-';
  const readChange = last ? calcChangeRate(totalRead, last.totalRead) : '-';

  // AI 洞察
  let insight = '数据平稳，建议持续优化内容策略。';
  if (netGrowth > 10) insight = `今日净增 ${netGrowth} 位粉丝，增长势头强劲！`;
  else if (netGrowth > 0) insight = `今日净增 ${netGrowth} 位粉丝，保持良好增长。`;
  else if (netGrowth < 0) insight = `今日净流失 ${Math.abs(netGrowth)} 位粉丝，建议关注内容质量和推送时间。`;

  const reportData = { date: reportDate, newUsers, cancelUsers, netGrowth, growthRate, totalUsers, totalRead, totalShare, readChange, topArticles, newMessages, insight };

  // 保存历史
  if (!history.reports) history.reports = [];
  history.reports.push({ date: reportDate, netGrowth, totalRead, totalUsers, generatedAt: new Date().toISOString() });
  if (history.reports.length > 30) history.reports = history.reports.slice(-30);
  writeData('daily-history.json', history);

  // 生成报告文本
  const lines = [
    `📊 **公众号日报** (${reportData.date})`, `━━━━━━━━━━━━━━━━━━━━━━━━━━━━`, '',
    `**👥 用户数据**`,
    `• 新增关注: +${newUsers}`, `• 取消关注: -${cancelUsers}`,
    `• 净增长: ${netGrowth >= 0 ? '+' : ''}${netGrowth} (${growthRate})`,
    `• 累计粉丝: ${totalUsers.toLocaleString()}`, '',
    `**📖 阅读数据**`,
    `• 总阅读: ${totalRead.toLocaleString()} 次 (${readChange})`,
    `• 总分享: ${totalShare} 次`,
  ];
  if (topArticles.length) {
    lines.push('', `**🔥 热门文章**`);
    topArticles.forEach(a => lines.push(`${a.rank}. 《${a.title}》`));
  }
  lines.push('', `**💬 互动数据**`, `• 新消息: ${newMessages} 条`, '', `**💡 AI 洞察**`, insight, '', `━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);

  return { report: lines.join('\n'), data: reportData };
}

async function main() {
  const args = parseArgs();
  try {
    const { report, data } = await generateDailyReport(args.date);
    console.error('\n' + report);
    output(true, { report, data });
  } catch (error) { outputError(error); }
}

main();
