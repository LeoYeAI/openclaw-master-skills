#!/usr/bin/env node
/**
 * 腾讯云 COS Node.js SDK 操作脚本
 * 作为 cos-mcp MCP 工具不可用时的降级方案
 *
 * 依赖：npm install cos-nodejs-sdk-v5
 * 凭证通过环境变量读取：
 *   TENCENT_COS_SECRET_ID / TENCENT_COS_SECRET_KEY / TENCENT_COS_REGION / TENCENT_COS_BUCKET
 *
 * 用法：node cos_node.mjs <action> [options]
 */

import { createRequire } from 'module';
import { createReadStream, createWriteStream, existsSync } from 'fs';
import { basename, resolve } from 'path';
import { pipeline } from 'stream/promises';

const require = createRequire(import.meta.url);
const COS = require('cos-nodejs-sdk-v5');

// 读取环境变量
const SecretId = process.env.TENCENT_COS_SECRET_ID;
const SecretKey = process.env.TENCENT_COS_SECRET_KEY;
const Region = process.env.TENCENT_COS_REGION;
const Bucket = process.env.TENCENT_COS_BUCKET;

// 可选的自定义域名配置
const Domain = process.env.TENCENT_COS_DOMAIN;
const ServiceDomain = process.env.TENCENT_COS_SERVICE_DOMAIN;
const Protocol = process.env.TENCENT_COS_PROTOCOL;

if (!SecretId || !SecretKey || !Region || !Bucket) {
  console.error(JSON.stringify({
    success: false,
    error: '缺少环境变量，需要：TENCENT_COS_SECRET_ID, TENCENT_COS_SECRET_KEY, TENCENT_COS_REGION, TENCENT_COS_BUCKET',
  }));
  process.exit(1);
}

const cosOptions = { SecretId, SecretKey };

if (Domain) {
  cosOptions.Domain = Domain;
}

if (ServiceDomain) {
  cosOptions.ServiceDomain = ServiceDomain;
}

if (Protocol) {
  cosOptions.Protocol = Protocol;
}

const cos = new COS(cosOptions);

// 解析命令行参数
function parseArgs(args) {
  const result = {};
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith('--')) {
      const key = arg.slice(2);
      const next = args[i + 1];
      if (next && !next.startsWith('--')) {
        result[key] = next;
        i++;
      } else {
        result[key] = true;
      }
    }
  }
  return result;
}

// 输出 JSON 结果
function output(data) {
  console.log(JSON.stringify(data, null, 2));
}

// 封装 COS SDK 回调为 Promise
function cosPromise(method, params) {
  return new Promise((resolve, reject) => {
    cos[method]({ Bucket, Region, ...params }, (err, data) => {
      if (err) {
        reject(err);
      } else {
        resolve(data);
      }
    });
  });
}

// ========== 操作实现 ==========

async function upload(opts) {
  const filePath = opts.file;
  const key = opts.key || basename(filePath);

  if (!filePath) {
    throw new Error('缺少 --file 参数');
  }
  if (!existsSync(filePath)) {
    throw new Error(`文件不存在：${filePath}`);
  }

  const data = await cosPromise('putObject', {
    Key: key,
    Body: createReadStream(filePath),
  });

  output({
    success: true,
    action: 'upload',
    key,
    etag: data.ETag,
    location: data.Location,
    statusCode: data.statusCode,
  });
}

async function putString(opts) {
  const content = opts.content;
  const key = opts.key;
  const contentType = opts['content-type'] || 'text/plain';

  if (!content) {
    throw new Error('缺少 --content 参数');
  }
  if (!key) {
    throw new Error('缺少 --key 参数');
  }

  const data = await cosPromise('putObject', {
    Key: key,
    Body: content,
    ContentType: contentType,
  });

  output({
    success: true,
    action: 'put-string',
    key,
    etag: data.ETag,
    location: data.Location,
    statusCode: data.statusCode,
  });
}

async function download(opts) {
  const key = opts.key;
  const outputPath = opts.output || basename(key);

  if (!key) {
    throw new Error('缺少 --key 参数');
  }

  const data = await cosPromise('getObject', {
    Key: key,
  });

  const resolvedPath = resolve(outputPath);
  const ws = createWriteStream(resolvedPath);

  if (data.Body instanceof Buffer) {
    ws.write(data.Body);
    ws.end();
  } else if (data.Body && typeof data.Body.pipe === 'function') {
    await pipeline(data.Body, ws);
  } else {
    ws.write(String(data.Body));
    ws.end();
  }

  output({
    success: true,
    action: 'download',
    key,
    savedTo: resolvedPath,
    contentLength: data.headers?.['content-length'],
    statusCode: data.statusCode,
  });
}

async function list(opts) {
  const prefix = opts.prefix || '';
  const maxKeys = parseInt(opts['max-keys'], 10) || 100;

  const data = await cosPromise('getBucket', {
    Prefix: prefix,
    MaxKeys: maxKeys,
  });

  const files = (data.Contents || []).map(item => ({
    key: item.Key,
    size: parseInt(item.Size, 10),
    lastModified: item.LastModified,
    etag: item.ETag,
    storageClass: item.StorageClass,
  }));

  output({
    success: true,
    action: 'list',
    prefix,
    count: files.length,
    isTruncated: data.IsTruncated === 'true',
    files,
  });
}

async function signUrl(opts) {
  const key = opts.key;
  const expires = parseInt(opts.expires, 10) || 3600;

  if (!key) {
    throw new Error('缺少 --key 参数');
  }

  const url = await new Promise((resolve, reject) => {
    cos.getObjectUrl({
      Bucket,
      Region,
      Key: key,
      Expires: expires,
      Sign: true,
    }, (err, data) => {
      if (err) {
        reject(err);
      } else {
        resolve(data.Url);
      }
    });
  });

  output({
    success: true,
    action: 'sign-url',
    key,
    expires,
    url,
  });
}

async function deleteObject(opts) {
  const key = opts.key;

  if (!key) {
    throw new Error('缺少 --key 参数');
  }

  const data = await cosPromise('deleteObject', {
    Key: key,
  });

  output({
    success: true,
    action: 'delete',
    key,
    statusCode: data.statusCode,
  });
}

async function head(opts) {
  const key = opts.key;

  if (!key) {
    throw new Error('缺少 --key 参数');
  }

  const data = await cosPromise('headObject', {
    Key: key,
  });

  output({
    success: true,
    action: 'head',
    key,
    contentLength: parseInt(data.headers?.['content-length'], 10),
    contentType: data.headers?.['content-type'],
    etag: data.headers?.etag,
    lastModified: data.headers?.['last-modified'],
    storageClass: data.headers?.['x-cos-storage-class'] || 'STANDARD',
    statusCode: data.statusCode,
  });
}

// ========== 主入口 ==========

const args = process.argv.slice(2);
const action = args[0];
const opts = parseArgs(args.slice(1));

const actions = {
  upload,
  'put-string': putString,
  download,
  list,
  'sign-url': signUrl,
  delete: deleteObject,
  head,
};

if (!action || !actions[action]) {
  output({
    success: false,
    error: `未知操作：${action || '(空)'}`,
    availableActions: Object.keys(actions),
    usage: 'node cos_node.mjs <action> [--option value ...]',
  });
  process.exit(1);
}

try {
  await actions[action](opts);
} catch (err) {
  output({
    success: false,
    action,
    error: err.message || String(err),
    code: err.code,
  });
  process.exit(1);
}
