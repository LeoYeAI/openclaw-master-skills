#!/usr/bin/env node
'use strict';

// OceanBus Chat — A2A Communication Skill
//
// Two AI agents negotiate a meeting place via OceanBus.
// No server. No same-WiFi. Just the OceanBus network.
//
// Commands:
//   node chat.js setup                        Register + get your OpenID
//   node chat.js whoami                       Show your OpenID
//   node chat.js add <name> <openid>          Save a friend
//   node chat.js contacts                     List saved contacts
//   node chat.js send <name|openid> <msg>     Send a message
//   node chat.js check                        Check for new messages

const { createOceanBus } = require('oceanbus');
const fs = require('fs');
const path = require('path');
const os = require('os');

// ── Config ────────────────────────────────────────────────────────────────
const DATA_DIR = path.join(os.homedir(), '.oceanbus-chat');
const CRED_FILE = path.join(DATA_DIR, 'credentials.json');
const CURSOR_FILE = path.join(DATA_DIR, 'cursor.json');
const CONTACTS_FILE = path.join(DATA_DIR, 'contacts.json');

// ── Helpers ───────────────────────────────────────────────────────────────

function ensureDir() {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

function saveCredentials(agentId, apiKey, openid) {
  ensureDir();
  fs.writeFileSync(CRED_FILE, JSON.stringify({ agent_id: agentId, api_key: apiKey, openid }, null, 2));
}

function loadCredentials() {
  if (!fs.existsSync(CRED_FILE)) return null;
  return JSON.parse(fs.readFileSync(CRED_FILE, 'utf-8'));
}

function loadContacts() {
  ensureDir();
  if (!fs.existsSync(CONTACTS_FILE)) return {};
  try { return JSON.parse(fs.readFileSync(CONTACTS_FILE, 'utf-8')); } catch (_) { return {}; }
}

function saveContacts(contacts) {
  ensureDir();
  fs.writeFileSync(CONTACTS_FILE, JSON.stringify(contacts, null, 2));
}

function resolveName(openid, contacts) {
  for (const [name, id] of Object.entries(contacts)) {
    if (id === openid) return name;
  }
  return null;
}

function saveCursor(seq) {
  ensureDir();
  fs.writeFileSync(CURSOR_FILE, JSON.stringify({ last_seq: seq }));
}

function loadCursor() {
  if (!fs.existsSync(CURSOR_FILE)) return 0;
  try { return JSON.parse(fs.readFileSync(CURSOR_FILE, 'utf-8')).last_seq || 0; } catch (_) { return 0; }
}

function formatTime(iso) {
  try { return new Date(iso).toLocaleTimeString('zh-CN', { hour12: false }); } catch (_) { return iso; }
}

function shortId(openid) {
  return openid.slice(0, 16) + '...';
}

// ── Subcommands ───────────────────────────────────────────────────────────

async function cmdSetup() {
  ensureDir();

  const existing = loadCredentials();
  if (existing) {
    // Show contacts if any
    const contacts = loadContacts();
    const names = Object.keys(contacts);

    console.log('已注册。');
    console.log('你的 OpenID: ' + existing.openid);
    console.log('(简写: ' + shortId(existing.openid) + ')');
    console.log('');

    if (names.length > 0) {
      console.log('通讯录中有 ' + names.length + ' 位联系人:');
      for (const name of names) {
        console.log('  - ' + name + ' (' + shortId(contacts[name]) + ')');
      }
      console.log('');
    }

    console.log('让对方用这个命令加你为好友:');
    console.log('  node chat.js add <你的名字> ' + existing.openid);
    return;
  }

  console.log('正在注册 OceanBus 身份...');

  const ob = await createOceanBus({ keyStore: { type: 'memory' } });
  const reg = await ob.register();
  const openid = await ob.getOpenId();

  saveCredentials(reg.agent_id, reg.api_key, openid);
  await ob.destroy();

  console.log('');
  console.log('注册成功！你的 OceanBus 地址:');
  console.log('');
  console.log('  ' + openid);
  console.log('');
  console.log('现在你可以:');
  console.log('  ① 把这个 OpenID 发给朋友');
  console.log('  ② 朋友用: node chat.js add <你的名字> ' + openid);
  console.log('  ③ 你也加上朋友: node chat.js add <朋友名字> <朋友的OpenID>');
  console.log('  ④ 开始通信！');
}

async function cmdWhoami() {
  const creds = loadCredentials();
  if (!creds) {
    console.log('尚未注册。运行: node chat.js setup');
    return;
  }
  console.log(creds.openid);
}

async function cmdAdd(name, openid) {
  if (!name || !openid) {
    console.log('用法: node chat.js add <名字> <OpenID>');
    console.log('例如: node chat.js add 李四 ob_c-QrzaDzhf7OR...');
    return;
  }

  const contacts = loadContacts();
  contacts[name] = openid;
  saveContacts(contacts);

  console.log('已添加联系人: ' + name + ' (' + shortId(openid) + ')');
  console.log('现在可以用名字发消息: node chat.js send ' + name + ' <消息>');
}

async function cmdContacts() {
  const contacts = loadContacts();
  const names = Object.keys(contacts);
  if (names.length === 0) {
    console.log('通讯录为空。');
    console.log('添加联系人: node chat.js add <名字> <OpenID>');
    return;
  }
  console.log('通讯录 (' + names.length + ' 人):');
  for (const name of names) {
    console.log('  ' + name + ' — ' + shortId(contacts[name]));
  }
}

async function cmdSend(target, message) {
  const creds = loadCredentials();
  if (!creds) {
    console.log('尚未注册。运行: node chat.js setup');
    return;
  }

  if (!target || !message) {
    console.log('用法: node chat.js send <名字|OpenID> <消息>');
    return;
  }

  // Resolve name to OpenID
  const contacts = loadContacts();
  const openid = contacts[target] || target;

  const ob = await createOceanBus({
    keyStore: { type: 'memory' },
    identity: { agent_id: creds.agent_id, api_key: creds.api_key },
  });

  await ob.send(openid, message);

  const displayName = contacts[target] ? target : shortId(openid);
  console.log('已发送 → ' + displayName);

  await ob.destroy();
}

async function cmdCheck() {
  const creds = loadCredentials();
  if (!creds) {
    console.log('尚未注册。运行: node chat.js setup');
    return;
  }

  const contacts = loadContacts();
  const lastSeq = loadCursor();

  const ob = await createOceanBus({
    keyStore: { type: 'memory' },
    identity: { agent_id: creds.agent_id, api_key: creds.api_key },
  });

  const messages = await ob.sync(lastSeq > 0 ? lastSeq : undefined);

  if (messages.length === 0) {
    console.log('没有新消息。');
  } else {
    let maxSeq = lastSeq;

    for (const msg of messages) {
      const name = resolveName(msg.from_openid, contacts);
      const from = name ? name + ' (' + shortId(msg.from_openid) + ')' : msg.from_openid;

      console.log('── 来自 ' + from + ' ──');
      console.log('  ' + formatTime(msg.created_at));
      console.log('');
      console.log(msg.content);
      console.log('');

      const seq = typeof msg.seq_id === 'number' ? msg.seq_id : parseInt(msg.seq_id, 10);
      if (!isNaN(seq) && seq > maxSeq) maxSeq = seq;
    }

    if (maxSeq > lastSeq) saveCursor(maxSeq);
  }

  await ob.destroy();
}

// ── Main ──────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  const cmd = args[0];

  if (!cmd || cmd === 'help' || cmd === '--help' || cmd === '-h') {
    console.log('OceanBus Chat — Agent 会面协商');
    console.log('');
    console.log('命令:');
    console.log('  node chat.js setup                      注册 + 获取你的 OpenID');
    console.log('  node chat.js whoami                     查看你的 OpenID');
    console.log('  node chat.js add <名字> <OpenID>        添加联系人');
    console.log('  node chat.js contacts                   查看通讯录');
    console.log('  node chat.js send <名字|OpenID> <消息>  发送消息');
    console.log('  node chat.js check                      查看新消息');
    console.log('');
    console.log('数据存储在: ' + DATA_DIR);
    return;
  }

  try {
    switch (cmd) {
      case 'setup':
        await cmdSetup();
        break;
      case 'whoami':
        await cmdWhoami();
        break;
      case 'add':
        await cmdAdd(args[1], args[2]);
        break;
      case 'contacts':
        await cmdContacts();
        break;
      case 'send': {
        const target = args[1];
        const msg = args.slice(2).join(' ');
        if (!target || !msg) {
          console.log('用法: node chat.js send <名字|OpenID> <消息>');
          break;
        }
        await cmdSend(target, msg);
        break;
      }
      case 'check':
        await cmdCheck();
        break;
      default:
        console.log('未知命令: ' + cmd);
        console.log('运行 "node chat.js help" 查看帮助。');
    }
  } catch (err) {
    if (err.message && (err.message.includes('ECONNREFUSED') || err.message.includes('ENOTFOUND'))) {
      console.error('无法连接 OceanBus 网络。请检查互联网连接。');
    } else {
      console.error('错误: ' + err.message);
    }
    process.exit(1);
  }
}

main();
