#!/usr/bin/env node
/**
 * 评论回复 + 精选
 * 
 * 回复: node reply_comment.mjs --article-id <id> --comment-id <id> --content "回复内容"
 * 精选: node reply_comment.mjs --article-id <id> --comment-id <id> --elect
 * 同时: node reply_comment.mjs --article-id <id> --comment-id <id> --content "回复内容" --elect
 */
import {
  output, outputError, parseArgs,
  replyComment, electComment, unelectComment
} from './lib/utils.mjs';

async function main() {
  const args = parseArgs();
  const articleId = args.articleId;
  const commentId = args.commentId ? parseInt(args.commentId) : null;

  if (!articleId) { outputError(new Error('请指定 --article-id')); return; }
  if (!commentId) { outputError(new Error('请指定 --comment-id')); return; }

  const results = {};

  try {
    // 回复
    if (args.content) {
      console.error(`[评论] 回复评论 ${commentId}: ${args.content}`);
      await replyComment(articleId, 0, commentId, args.content);
      results.replied = true;
      console.error('✅ 回复成功');
    }

    // 精选
    if (args.elect) {
      console.error(`[评论] 精选评论 ${commentId}`);
      await electComment(articleId, 0, commentId);
      results.elected = true;
      console.error('✅ 精选成功');
    }

    // 取消精选
    if (args.unelect) {
      console.error(`[评论] 取消精选 ${commentId}`);
      await unelectComment(articleId, 0, commentId);
      results.unelected = true;
      console.error('✅ 取消精选成功');
    }

    output(true, { articleId, commentId, ...results });
  } catch (error) { outputError(error); }
}

main();
