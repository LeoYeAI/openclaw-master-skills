#!/usr/bin/env node
/**
 * 公众号草稿发布工具
 *
 * 创建草稿: node publisher.mjs --title "标题" --content article.html [--cover cover.png] [--author "作者"] [--digest "摘要"]
 * 从 Markdown: node publisher.mjs --markdown article.md --title "标题" [--cover cover.png] [--author "作者"] [--digest "摘要"]
 * 发布草稿: node publisher.mjs --publish --media-id <id>
 * 列出草稿: node publisher.mjs --list [--count 10]
 * 删除草稿: node publisher.mjs --delete --media-id <id>
 */
import { readFileSync, existsSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import {
  output, outputError, parseArgs,
  uploadPermanentMedia, uploadArticleImage,
  addDraft, getDraft, listDrafts, deleteDraft,
  publishDraft, getPublishStatus
} from './lib/utils.mjs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

function convertMarkdownToHtml(mdPath) {
  const scriptPath = resolve(__dirname, 'markdown_to_html.py');
  const absPath = resolve(mdPath);
  if (!existsSync(absPath)) throw new Error(`Markdown 文件不存在: ${absPath}`);

  console.error(`[发布] 转换 Markdown: ${absPath}`);
  const stdout = execFileSync(
    'python3',
    [scriptPath, '--input', absPath, '--upload', '--body-only'],
    { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'inherit'] }
  );

  const json = JSON.parse(stdout.trim());
  if (!json.success) throw new Error('Markdown 转换失败');

  const htmlPath = resolve(json.output);
  const content = readFileSync(htmlPath, 'utf-8');
  console.error(`[发布] HTML 就绪: ${htmlPath} (${content.length} 字符)`);
  return content;
}

async function cleanupOldDrafts(title) {
  console.error(`[清理] 检查同标题草稿: "${title}"`);
  const result = await listDrafts(0, 20);
  const items = result.item || [];
  let cleaned = 0;

  for (const item of items) {
    const draftTitle = item.content?.news_item?.[0]?.title;
    if (draftTitle === title) {
      console.error(`[清理] 删除旧草稿: ${item.media_id}`);
      await deleteDraft(item.media_id);
      cleaned++;
    }
  }

  if (cleaned > 0) {
    console.error(`[清理] 已删除 ${cleaned} 个同标题旧草稿`);
  } else {
    console.error(`[清理] 无同标题旧草稿`);
  }
}

async function createDraft(args) {
  const title = args.title;

  let content;
  if (args.markdown) {
    content = convertMarkdownToHtml(args.markdown);
  } else {
    const contentPath = resolve(args.content);
    if (!existsSync(contentPath)) throw new Error(`内容文件不存在: ${contentPath}`);
    content = readFileSync(contentPath, 'utf-8');
  }

  console.error(`[发布] 标题: ${title}`);
  console.error(`[发布] 内容: ${content.length} 字符`);

  if (!args.noCleanup) {
    await cleanupOldDrafts(title);
  }

  let thumbMediaId = '';
  if (args.cover) {
    const coverPath = resolve(args.cover);
    if (!existsSync(coverPath)) throw new Error(`封面图不存在: ${coverPath}`);
    console.error(`[发布] 上传封面图: ${coverPath}`);
    const uploadResult = await uploadPermanentMedia(coverPath, 'image');
    thumbMediaId = uploadResult.media_id;
    console.error(`[发布] 封面图 media_id: ${thumbMediaId}`);
  }

  const article = {
    title,
    content,
    content_source_url: '',
    thumb_media_id: thumbMediaId,
    author: args.author || '',
    digest: args.digest || '',
    show_cover_pic: thumbMediaId ? 1 : 0,
    need_open_comment: 1,
    only_fans_can_comment: 0,
  };

  console.error('[发布] 创建草稿...');
  const result = await addDraft([article]);
  const mediaId = result.media_id;
  console.error(`\n✅ 草稿创建成功！`);
  console.error(`   media_id: ${mediaId}`);
  console.error(`   发布: node publisher.mjs --publish --media-id ${mediaId}`);
  console.error(`   删除: node publisher.mjs --delete --media-id ${mediaId}`);

  return { mediaId, title };
}

async function publish(args) {
  const mediaId = args.mediaId;
  if (!mediaId) throw new Error('请指定 --media-id');

  console.error(`[发布] 发布草稿: ${mediaId}`);
  const result = await publishDraft(mediaId);
  console.error(`\n✅ 发布请求已提交！`);
  console.error(`   publish_id: ${result.publish_id}`);

  await new Promise(r => setTimeout(r, 3000));
  try {
    const status = await getPublishStatus(result.publish_id);
    console.error(`   发布状态: ${JSON.stringify(status)}`);
    return { publishId: result.publish_id, status };
  } catch (e) {
    console.error(`   查询状态失败（可能仍在处理中）: ${e.message}`);
    return { publishId: result.publish_id };
  }
}

async function list(args) {
  const count = parseInt(args.count) || 10;
  console.error(`[草稿] 列出最近 ${count} 个草稿...\n`);
  const result = await listDrafts(0, count);
  const items = result.item || [];

  for (const item of items) {
    const news = item.content?.news_item?.[0];
    const title = news?.title || '未知标题';
    const updateTime = item.update_time ? new Date(item.update_time * 1000).toLocaleString('zh-CN') : '';
    console.error(`  📝 ${title}`);
    console.error(`     media_id: ${item.media_id}`);
    console.error(`     更新时间: ${updateTime}\n`);
  }
  console.error(`共 ${result.total_count || items.length} 个草稿`);

  return { total: result.total_count, items: items.map(i => ({
    mediaId: i.media_id,
    title: i.content?.news_item?.[0]?.title || '',
    updateTime: i.update_time
  }))};
}

async function remove(args) {
  const mediaId = args.mediaId;
  if (!mediaId) throw new Error('请指定 --media-id');

  console.error(`[草稿] 删除: ${mediaId}`);
  await deleteDraft(mediaId);
  console.error('✅ 删除成功');
  return { deleted: mediaId };
}

async function main() {
  const args = parseArgs();
  try {
    let result;
    if (args.publish) {
      result = await publish(args);
    } else if (args.list) {
      result = await list(args);
    } else if (args.delete) {
      result = await remove(args);
    } else {
      if (!args.title) throw new Error('请指定 --title');
      if (!args.content && !args.markdown) throw new Error('请指定 --content (HTML文件路径) 或 --markdown (Markdown文件路径)');
      result = await createDraft(args);
    }
    output(true, result);
  } catch (error) {
    outputError(error);
  }
}

main();
