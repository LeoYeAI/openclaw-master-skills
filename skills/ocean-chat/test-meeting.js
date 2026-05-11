#!/usr/bin/env node
'use strict';

// OceanBus A2A Meeting Negotiation — Full Demo with Agent Reports
//
// Two agents negotiate a meeting place via OceanBus.
// After agreement, each agent reports the process to their user.

const { createOceanBus } = require('oceanbus');

async function main() {
  console.log('╔══════════════════════════════════════════════════╗');
  console.log('║     OceanBus A2A 会面协商 — 完整演示             ║');
  console.log('║     两个 AI Agent 通过 OceanBus 协商见面地点      ║');
  console.log('╚══════════════════════════════════════════════════╝\n');

  // ── Phase 1: Register both agents ──
  printPhase('双方 Agent 注册 OceanBus 身份');

  const s = await createOceanBus({ keyStore: { type: 'memory' } });
  await s.register();
  const zhangAddr = await s.getOpenId();

  const l = await createOceanBus({ keyStore: { type: 'memory' } });
  await l.register();
  const liAddr = await l.getOpenId();

  const zhangInbox = [];
  const liInbox = [];

  s.startListening(m => zhangInbox.push(m));
  l.startListening(m => liInbox.push(m));

  await sleep(3000);

  console.log('  张三 Agent 已上线  收件地址: ' + shortId(zhangAddr));
  console.log('  李四 Agent 已上线  收件地址: ' + shortId(liAddr));
  console.log('  双方已互加通讯录\n');

  // ── Phase 2: 张三 initiates ──
  printPhase('张三发起会面请求');

  // 张三的 Agent 根据用户偏好发起
  console.log('  🧑 张三: "跟李四的Agent约一个方便的地点会面"\n');
  console.log('  🤖 张三 Agent 分析:');
  console.log('     用户在朝阳区大望路，偏好靠近地铁站');
  console.log('     发送会面请求...\n');

  const msg1 = '【会面请求】你好！我们约个方便的地方见面吧。我在朝阳区大望路，最好靠近地铁站。你在哪个区域？';
  console.log('  ── OceanBus 消息 ─────────────────────');
  console.log('  张三 ──→ 李四');
  console.log('  ' + msg1 + '\n');

  await s.send(liAddr, msg1);
  await sleep(4000);

  // 李四 Agent 检查消息
  const liNew1 = latestFrom(liInbox, 0);
  if (liNew1) {
    console.log('  🤖 李四 Agent 收到消息:');
    console.log('     "' + liNew1.content.slice(0, 50) + '..."');
    console.log('     识别为【会面请求】，询问用户偏好...\n');
    console.log('  🧑 李四: "我在通州，1号线沿线都可以"\n');
  }

  // ── Phase 3: 李四 suggests ──
  printPhase('李四提出会面建议');

  console.log('  🤖 李四 Agent 分析:');
  console.log('     张三在朝阳大望路（1号线）');
  console.log('     李四在通州（1号线沿线）');
  console.log('     国贸在两者之间，1号线直达，有星巴克可坐');
  console.log('     提出建议...\n');

  const msg2 = '【会面建议】地点: 国贸商城B1层星巴克 | 理由: 1号线大望路→国贸仅1站，通州过来也方便。国贸在两人之间，星巴克有座位可以坐下来慢慢聊';
  console.log('  ── OceanBus 消息 ─────────────────────');
  console.log('  李四 ──→ 张三');
  console.log('  ' + msg2 + '\n');

  await l.send(zhangAddr, msg2);
  await sleep(4000);

  // 张三 Agent 检查消息
  const zhangNew1 = latestFrom(zhangInbox, 0);
  if (zhangNew1) {
    console.log('  🤖 张三 Agent 收到消息:');
    console.log('     "' + zhangNew1.content.slice(0, 50) + '..."');
    console.log('     识别为【会面建议】');
    console.log('     评估: 国贸在1号线上，距大望路1站，交通便利');
    console.log('     星巴克有座位 — 合适');
    console.log('     决策: 接受建议，发送确认\n');
  }

  // ── Phase 4: 张三 confirms ──
  printPhase('张三确认 — 达成一致');

  const msg3 = '【会面确认】地点: 国贸商城B1层星巴克';
  console.log('  ── OceanBus 消息 ─────────────────────');
  console.log('  张三 ──→ 李四');
  console.log('  ' + msg3 + '\n');

  await s.send(liAddr, msg3);
  await sleep(4000);

  // 李四 Agent 检查
  const liNew2 = latestFrom(liInbox, 0);
  if (liNew2) {
    console.log('  🤖 李四 Agent 收到消息:');
    console.log('     "' + liNew2.content + '"');
    console.log('     识别为【会面确认】');
    console.log('     协商完成！\n');
  }

  // ═══════════════════════════════════════════════════════
  // Agent Reports
  // ═══════════════════════════════════════════════════════

  console.log('╔══════════════════════════════════════════════════╗');
  console.log('║              协商完成 — Agent 汇报               ║');
  console.log('╚══════════════════════════════════════════════════╝\n');

  // 张三 Agent report
  console.log('┌─────────────────────────────────────────────┐');
  console.log('│  张三的 Agent 汇报                           │');
  console.log('├─────────────────────────────────────────────┤');
  console.log('│                                             │');
  console.log('│  📍 会面地点: 国贸商城B1层星巴克               │');
  console.log('│  🚇 交通: 1号线国贸站，大望路过去仅1站          │');
  console.log('│  ⏱  协商轮次: 3 轮                           │');
  console.log('│                                             │');
  console.log('│  协商过程:                                   │');
  console.log('│  ┌──────────────────────────────────────┐   │');
  console.log('│  │ ① 你发起: "我在朝阳大望路，你在哪？"    │   │');
  console.log('│  │ ② 李四建议: 国贸星巴克，理由充分        │   │');
  console.log('│  │ ③ 你确认: ✅ 达成一致                  │   │');
  console.log('│  └──────────────────────────────────────┘   │');
  console.log('│                                             │');
  console.log('│  评价: 李四的 Agent 回复迅速，建议合理。        │');
  console.log('│  国贸在两人中间，双方都方便。                   │');
  console.log('│                                             │');
  console.log('└─────────────────────────────────────────────┘\n');

  // 李四 Agent report
  console.log('┌─────────────────────────────────────────────┐');
  console.log('│  李四的 Agent 汇报                           │');
  console.log('├─────────────────────────────────────────────┤');
  console.log('│                                             │');
  console.log('│  📍 会面地点: 国贸商城B1层星巴克               │');
  console.log('│  🚇 交通: 1号线国贸站                        │');
  console.log('│  ⏱  协商轮次: 3 轮                           │');
  console.log('│                                             │');
  console.log('│  协商过程:                                   │');
  console.log('│  ┌──────────────────────────────────────┐   │');
  console.log('│  │ ① 张三请求: 朝阳大望路附近，近地铁      │   │');
  console.log('│  │ ② 你建议: 国贸星巴克（居中，1号线直达） │   │');
  console.log('│  │ ③ 张三确认: ✅ 达成一致                │   │');
  console.log('│  └──────────────────────────────────────┘   │');
  console.log('│                                             │');
  console.log('│  评价: 张三的 Agent 决策快速。从发起请求到     │');
  console.log('│  确认仅 3 轮。国贸确实是合理选择。              │');
  console.log('│                                             │');
  console.log('└─────────────────────────────────────────────┘\n');

  // Cleanup
  await s.destroy();
  await l.destroy();
}

// ── Helpers ──

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function shortId(s) { return s.slice(0, 18) + '...'; }

function latestFrom(inbox, n) {
  return inbox.length > n ? inbox[inbox.length - 1 - n] : null;
}

let phaseNum = 0;
function printPhase(title) {
  phaseNum++;
  const bar = '─'.repeat(50);
  console.log(bar);
  console.log('  第 ' + phaseNum + ' 步: ' + title);
  console.log(bar + '\n');
}

main().catch(err => {
  console.error('测试失败:', err.message);
  process.exit(1);
});
