#!/usr/bin/env node
/**
 * wemp-ops 共享工具库：配置管理、数据存储、微信公众号 API (70个)
 */
import { readFileSync, writeFileSync, existsSync, mkdirSync, createReadStream } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { homedir } from 'node:os';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
export const SKILL_ROOT = join(__dirname, '..', '..');

// ============ 配置管理 ============

export function loadConfig() {
  const configPath = join(SKILL_ROOT, 'config', 'default.json');
  if (!existsSync(configPath)) return {};
  return JSON.parse(readFileSync(configPath, 'utf-8'));
}

function getWempAccount() {
  // 优先从 skill 自己的 config/default.json 读取
  const skillConfig = loadConfig();
  if (skillConfig?.weixin?.appId && skillConfig?.weixin?.appSecret) {
    return { appId: skillConfig.weixin.appId, appSecret: skillConfig.weixin.appSecret };
  }
  // ⚠️ 不要往 openclaw.json 的 channels 里写 wemp 配置！
  // channels 只接受 OpenClaw 内置支持的渠道类型，写错会导致 gateway 崩溃。
  throw new Error('未找到公众号配置。请在 config/default.json 的 weixin 字段配置 appId + appSecret');
}

// ============ 数据存储 ============

export function getDataPath(filename) {
  const dataDir = join(SKILL_ROOT, 'data');
  if (!existsSync(dataDir)) mkdirSync(dataDir, { recursive: true });
  return join(dataDir, filename);
}

export function readData(filename, defaultValue = {}) {
  const p = getDataPath(filename);
  if (!existsSync(p)) return defaultValue;
  try { return JSON.parse(readFileSync(p, 'utf-8')); } catch { return defaultValue; }
}

export function writeData(filename, data) {
  writeFileSync(getDataPath(filename), JSON.stringify(data, null, 2));
}

// ============ 工具函数 ============

export function output(success, data) {
  console.log(JSON.stringify({ success, data }, null, 2));
}

export function outputError(error) {
  console.error(`[错误] ${error.message}`);
  console.log(JSON.stringify({ success: false, error: error.message }));
  process.exit(1);
}

export function parseArgs() {
  const args = {};
  const argv = process.argv.slice(2);
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2).replace(/-([a-z])/g, (_, c) => c.toUpperCase());
      const next = argv[i + 1];
      if (!next || next.startsWith('--')) { args[key] = true; }
      else { args[key] = next; i++; }
    }
  }
  return args;
}

export function formatDate(d) {
  const date = d ? new Date(d) : new Date();
  return date.toISOString().slice(0, 10);
}

export function getYesterday() {
  const d = new Date(); d.setDate(d.getDate() - 1);
  return formatDate(d);
}

export function getDaysAgo(n) {
  const d = new Date(); d.setDate(d.getDate() - n);
  return formatDate(d);
}

export function calcChangeRate(current, previous) {
  if (!previous || previous === 0) return '-';
  const rate = ((current - previous) / Math.abs(previous) * 100).toFixed(1);
  return rate > 0 ? `↑${rate}%` : rate < 0 ? `↓${Math.abs(rate)}%` : '→0%';
}

// ============ 微信 API 基础 ============

let tokenCache = null;

async function getAccessToken() {
  if (tokenCache && tokenCache.expiresAt > Date.now()) return tokenCache.token;
  const account = getWempAccount();
  const url = `https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=${account.appId}&secret=${account.appSecret}`;
  const resp = await fetch(url);
  const data = await resp.json();
  if (data.errcode) throw new Error(`获取 Token 失败: ${data.errcode} - ${data.errmsg}`);
  tokenCache = { token: data.access_token, expiresAt: Date.now() + (data.expires_in - 300) * 1000 };
  return tokenCache.token;
}

async function wechatApi(path, body = null, method) {
  const token = await getAccessToken();
  const sep = path.includes('?') ? '&' : '?';
  const url = `https://api.weixin.qq.com${path}${sep}access_token=${token}`;
  const m = method || (body ? 'POST' : 'GET');
  const options = { method: m };
  if (body) { options.headers = { 'Content-Type': 'application/json' }; options.body = JSON.stringify(body); }
  const resp = await fetch(url, options);
  const data = await resp.json();
  if (data.errcode && data.errcode !== 0) throw new Error(`微信API错误: ${data.errcode} - ${data.errmsg}`);
  return data;
}

// 上传文件（multipart/form-data）
async function wechatUpload(path, filePath, fieldName = 'media') {
  const token = await getAccessToken();
  const sep = path.includes('?') ? '&' : '?';
  const url = `https://api.weixin.qq.com${path}${sep}access_token=${token}`;
  const { basename: bn } = await import('node:path');
  const { readFileSync: rfs } = await import('node:fs');
  const fileName = bn(filePath);
  const fileData = rfs(filePath);
  const boundary = '----WempOps' + Date.now();
  const ext = fileName.split('.').pop().toLowerCase();
  const mimeMap = { jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png', gif: 'image/gif', bmp: 'image/bmp', mp3: 'audio/mp3', amr: 'audio/amr', mp4: 'video/mp4' };
  const mime = mimeMap[ext] || 'application/octet-stream';
  const header = `--${boundary}\r\nContent-Disposition: form-data; name="${fieldName}"; filename="${fileName}"\r\nContent-Type: ${mime}\r\n\r\n`;
  const footer = `\r\n--${boundary}--\r\n`;
  const headerBuf = Buffer.from(header);
  const footerBuf = Buffer.from(footer);
  const body = Buffer.concat([headerBuf, fileData, footerBuf]);
  const resp = await fetch(url, { method: 'POST', headers: { 'Content-Type': `multipart/form-data; boundary=${boundary}` }, body });
  const data = await resp.json();
  if (data.errcode && data.errcode !== 0) throw new Error(`上传失败: ${data.errcode} - ${data.errmsg}`);
  return data;
}

// ============ 统计 API (8) ============

export async function getUserSummary(date) {
  return wechatApi('/datacube/getusersummary', { begin_date: date, end_date: date });
}
export async function getUserCumulate(beginDate, endDate) {
  return wechatApi('/datacube/getusercumulate', { begin_date: beginDate, end_date: endDate || beginDate });
}
export async function getArticleSummary(date) {
  return wechatApi('/datacube/getarticlesummary', { begin_date: date, end_date: date });
}
export async function getArticleTotal(date) {
  return wechatApi('/datacube/getarticletotal', { begin_date: date, end_date: date });
}
export async function getUserRead(date) {
  return wechatApi('/datacube/getuserread', { begin_date: date, end_date: date });
}
export async function getUserShare(date) {
  return wechatApi('/datacube/getusershare', { begin_date: date, end_date: date });
}
export async function getUpstreamMsg(date) {
  return wechatApi('/datacube/getupstreammsg', { begin_date: date, end_date: date });
}
export async function getUpstreamMsgHour(date) {
  return wechatApi('/datacube/getupstreammsghour', { begin_date: date, end_date: date });
}

// ============ 草稿 API (6) ============

export async function addDraft(articles) {
  return wechatApi('/cgi-bin/draft/add', { articles });
}
export async function updateDraft(mediaId, index, article) {
  return wechatApi('/cgi-bin/draft/update', { media_id: mediaId, index, articles: article });
}
export async function getDraft(mediaId) {
  return wechatApi('/cgi-bin/draft/get', { media_id: mediaId });
}
export async function listDrafts(offset = 0, count = 20) {
  return wechatApi('/cgi-bin/draft/batchget', { offset, count, no_content: 0 });
}
export async function deleteDraft(mediaId) {
  return wechatApi('/cgi-bin/draft/delete', { media_id: mediaId });
}
export async function getDraftCount() {
  return wechatApi('/cgi-bin/draft/count', {});
}

// ============ 发布 API (5) ============

export async function publishDraft(mediaId) {
  return wechatApi('/cgi-bin/freepublish/submit', { media_id: mediaId });
}
export async function getPublishStatus(publishId) {
  return wechatApi('/cgi-bin/freepublish/get', { publish_id: publishId });
}
export async function listPublished(offset = 0, count = 20) {
  return wechatApi('/cgi-bin/freepublish/batchget', { offset, count, no_content: 1 });
}
export async function getPublishedArticle(articleId) {
  return wechatApi('/cgi-bin/freepublish/getarticle', { article_id: articleId });
}
export async function deletePublished(articleId, index = 0) {
  return wechatApi('/cgi-bin/freepublish/delete', { article_id: articleId, index });
}

// ============ 评论 API (8) ============

export async function listComments(msgDataId, index = 0, begin = 0, count = 50, type = 0) {
  return wechatApi('/cgi-bin/comment/list', { msg_data_id: msgDataId, index, begin, count, type });
}
export async function replyComment(msgDataId, index, userCommentId, content) {
  return wechatApi('/cgi-bin/comment/reply/add', { msg_data_id: msgDataId, index, user_comment_id: userCommentId, content });
}
export async function deleteCommentReply(msgDataId, index, userCommentId) {
  return wechatApi('/cgi-bin/comment/reply/delete', { msg_data_id: msgDataId, index, user_comment_id: userCommentId });
}
export async function electComment(msgDataId, index, userCommentId) {
  return wechatApi('/cgi-bin/comment/markelect', { msg_data_id: msgDataId, index, user_comment_id: userCommentId });
}
export async function unelectComment(msgDataId, index, userCommentId) {
  return wechatApi('/cgi-bin/comment/unmarkelect', { msg_data_id: msgDataId, index, user_comment_id: userCommentId });
}
export async function deleteComment(msgDataId, index, userCommentId) {
  return wechatApi('/cgi-bin/comment/delete', { msg_data_id: msgDataId, index, user_comment_id: userCommentId });
}
export async function openComment(msgDataId, index = 0) {
  return wechatApi('/cgi-bin/comment/open', { msg_data_id: msgDataId, index });
}
export async function closeComment(msgDataId, index = 0) {
  return wechatApi('/cgi-bin/comment/close', { msg_data_id: msgDataId, index });
}

// ============ 用户 API (7) ============

export async function getUserInfo(openId) {
  return wechatApi(`/cgi-bin/user/info?openid=${openId}&lang=zh_CN`, null, 'GET');
}
export async function batchGetUserInfo(openIds) {
  const userList = openIds.map(openid => ({ openid, lang: 'zh_CN' }));
  return wechatApi('/cgi-bin/user/info/batchget', { user_list: userList });
}
export async function getFollowers(nextOpenId = '') {
  return wechatApi(`/cgi-bin/user/get?next_openid=${nextOpenId}`, null, 'GET');
}
export async function setUserRemark(openId, remark) {
  return wechatApi('/cgi-bin/user/info/updateremark', { openid: openId, remark });
}
export async function getBlacklist(beginOpenId = '') {
  return wechatApi('/cgi-bin/tags/members/getblacklist', { begin_openid: beginOpenId });
}
export async function batchBlacklistUsers(openIds) {
  return wechatApi('/cgi-bin/tags/members/batchblacklist', { openid_list: openIds });
}
export async function batchUnblacklistUsers(openIds) {
  return wechatApi('/cgi-bin/tags/members/batchunblacklist', { openid_list: openIds });
}

// ============ 标签 API (8) ============

export async function createTag(name) {
  return wechatApi('/cgi-bin/tags/create', { tag: { name } });
}
export async function getTags() {
  return wechatApi('/cgi-bin/tags/get', null, 'GET');
}
export async function updateTag(id, name) {
  return wechatApi('/cgi-bin/tags/update', { tag: { id, name } });
}
export async function deleteTag(id) {
  return wechatApi('/cgi-bin/tags/delete', { tag: { id } });
}
export async function batchTagUsers(openIds, tagId) {
  return wechatApi('/cgi-bin/tags/members/batchtagging', { openid_list: openIds, tagid: tagId });
}
export async function batchUntagUsers(openIds, tagId) {
  return wechatApi('/cgi-bin/tags/members/batchuntagging', { openid_list: openIds, tagid: tagId });
}
export async function getUserTags(openId) {
  return wechatApi('/cgi-bin/tags/getidlist', { openid: openId });
}
export async function getTagUsers(tagId, nextOpenId = '') {
  return wechatApi('/cgi-bin/user/tag/get', { tagid: tagId, next_openid: nextOpenId });
}

// ============ 模板消息 API (5) ============

export async function getTemplates() {
  return wechatApi('/cgi-bin/template/get_all_private_template', null, 'GET');
}
export async function addTemplate(templateIdShort) {
  return wechatApi('/cgi-bin/template/api_add_template', { template_id_short: templateIdShort });
}
export async function deleteTemplate(templateId) {
  return wechatApi('/cgi-bin/template/del_private_template', { template_id: templateId });
}
export async function sendTemplateMessage(toUser, templateId, data, url = '', miniprogram = null) {
  const body = { touser: toUser, template_id: templateId, data };
  if (url) body.url = url;
  if (miniprogram) body.miniprogram = miniprogram;
  return wechatApi('/cgi-bin/message/template/send', body);
}
export async function getIndustry() {
  return wechatApi('/cgi-bin/template/get_industry', null, 'GET');
}

// ============ 素材 API (6) ============

export async function uploadTempMedia(filePath, type = 'image') {
  return wechatUpload(`/cgi-bin/media/upload?type=${type}`, filePath);
}
export async function uploadPermanentMedia(filePath, type = 'image') {
  return wechatUpload(`/cgi-bin/material/add_material?type=${type}`, filePath);
}
export async function uploadArticleImage(filePath) {
  return wechatUpload('/cgi-bin/media/uploadimg', filePath);
}
export async function getMaterialCount() {
  return wechatApi('/cgi-bin/material/get_materialcount', null, 'GET');
}
export async function getMaterialList(type = 'image', offset = 0, count = 20) {
  return wechatApi('/cgi-bin/material/batchget_material', { type, offset, count });
}
export async function deleteMaterial(mediaId) {
  return wechatApi('/cgi-bin/material/del_material', { media_id: mediaId });
}

// ============ 客服消息 API (7) ============

async function sendCustomMessage(toUser, msgtype, content) {
  return wechatApi('/cgi-bin/message/custom/send', { touser: toUser, msgtype, ...content });
}
export async function sendTextMessage(toUser, text) {
  return sendCustomMessage(toUser, 'text', { text: { content: text } });
}
export async function sendImageMessage(toUser, mediaId) {
  return sendCustomMessage(toUser, 'image', { image: { media_id: mediaId } });
}
export async function sendVoiceMessage(toUser, mediaId) {
  return sendCustomMessage(toUser, 'voice', { voice: { media_id: mediaId } });
}
export async function sendVideoMessage(toUser, mediaId, thumbMediaId, title = '', description = '') {
  return sendCustomMessage(toUser, 'video', { video: { media_id: mediaId, thumb_media_id: thumbMediaId, title, description } });
}
export async function sendNewsMessage(toUser, articles) {
  return sendCustomMessage(toUser, 'news', { news: { articles } });
}
export async function sendMpNewsMessage(toUser, mediaId) {
  return sendCustomMessage(toUser, 'mpnews', { mpnews: { media_id: mediaId } });
}
export async function sendTypingStatus(toUser) {
  return wechatApi('/cgi-bin/message/custom/typing', { touser: toUser, command: 'Typing' });
}

// ============ 菜单 API (4) ============

export async function createMenu(buttons) {
  return wechatApi('/cgi-bin/menu/create', { button: buttons });
}
export async function getMenu() {
  return wechatApi('/cgi-bin/menu/get', null, 'GET');
}
export async function deleteMenu() {
  return wechatApi('/cgi-bin/menu/delete', null, 'GET');
}
export async function getCurrentMenuInfo() {
  return wechatApi('/cgi-bin/get_current_selfmenu_info', null, 'GET');
}

// ============ 二维码 API (2) ============

export async function createQRCode(sceneStr, expireSeconds = 2592000) {
  const isTemp = expireSeconds > 0;
  const body = isTemp
    ? { expire_seconds: expireSeconds, action_name: 'QR_STR_SCENE', action_info: { scene: { scene_str: sceneStr } } }
    : { action_name: 'QR_LIMIT_STR_SCENE', action_info: { scene: { scene_str: sceneStr } } };
  return wechatApi('/cgi-bin/qrcode/create', body);
}
export function getQRCodeImageUrl(ticket) {
  return `https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=${encodeURIComponent(ticket)}`;
}

// ============ 群发 API (5) ============

export async function massSendByTag(tagId, mpnewsMediaId) {
  return wechatApi('/cgi-bin/message/mass/sendall', {
    filter: { is_to_all: tagId === 0, tag_id: tagId },
    mpnews: { media_id: mpnewsMediaId }, msgtype: 'mpnews', send_ignore_reprint: 0
  });
}
export async function massSendByOpenIds(openIds, mpnewsMediaId) {
  return wechatApi('/cgi-bin/message/mass/send', {
    touser: openIds, mpnews: { media_id: mpnewsMediaId }, msgtype: 'mpnews', send_ignore_reprint: 0
  });
}
export async function previewMassMessage(toUser, mpnewsMediaId) {
  return wechatApi('/cgi-bin/message/mass/preview', {
    touser: toUser, mpnews: { media_id: mpnewsMediaId }, msgtype: 'mpnews'
  });
}
export async function getMassMessageStatus(msgId) {
  return wechatApi('/cgi-bin/message/mass/get', { msg_id: msgId });
}
export async function deleteMassMessage(msgId, articleIdx = 0) {
  return wechatApi('/cgi-bin/message/mass/delete', { msg_id: msgId, article_idx: articleIdx });
}
