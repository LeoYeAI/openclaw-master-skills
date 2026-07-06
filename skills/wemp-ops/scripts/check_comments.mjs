#!/usr/bin/env node
/**
 * 评论检查 - 扫描最近文章的新评论
 */
import {
  output, outputError, parseArgs,
  listPublished, listComments
} from './lib/utils.mjs';

async function checkComments(articleCount = 5) {
  console.error(`[评论] 检查最近 ${articleCount} 篇文章的评论...\n`);

  // 获取已发布文章
  const published = await listPublished(0, articleCount);
  const articles = published.item || [];
  if (!articles.length) {
    console.error('没有已发布的文章。');
    return { articles: [], totalComments: 0, unreplied: 0 };
  }

  const results = [];
  let totalComments = 0;
  let unreplied = 0;

  for (const article of articles) {
    const newsItem = article.content?.news_item?.[0];
    const title = newsItem?.title || '未知标题';
    const msgDataId = article.article_id;

    if (!msgDataId) continue;

    try {
      const commentsData = await listComments(msgDataId, 0, 0, 50, 0);
      const comments = commentsData.comment || [];
      const total = commentsData.total || comments.length;

      const commentList = comments.map(c => ({
        id: c.user_comment_id,
        content: c.content,
        user: c.nick_name || '匿名',
        time: c.create_time ? new Date(c.create_time * 1000).toLocaleString('zh-CN') : '',
        isElected: !!c.is_elected,
        hasReply: !!(c.reply?.content),
        replyContent: c.reply?.content || '',
      }));

      const unrepliedComments = commentList.filter(c => !c.hasReply);
      totalComments += total;
      unreplied += unrepliedComments.length;

      results.push({
        articleId: msgDataId,
        title,
        totalComments: total,
        unrepliedCount: unrepliedComments.length,
        comments: commentList,
      });

      // 输出摘要
      console.error(`📝 《${title}》`);
      console.error(`   评论: ${total} 条, 未回复: ${unrepliedComments.length} 条`);
      if (unrepliedComments.length) {
        for (const c of unrepliedComments.slice(0, 3)) {
          console.error(`   💬 ${c.user}: ${c.content.slice(0, 50)}${c.content.length > 50 ? '...' : ''}`);
        }
      }
      console.error('');
    } catch (e) {
      console.error(`   ⚠️ 《${title}》评论获取失败: ${e.message}\n`);
    }
  }

  console.error(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.error(`总计: ${totalComments} 条评论, ${unreplied} 条未回复`);

  return { articles: results, totalComments, unreplied };
}

async function main() {
  const args = parseArgs();
  const count = parseInt(args.count) || 5;
  try {
    const result = await checkComments(count);
    output(true, result);
  } catch (error) { outputError(error); }
}

main();
