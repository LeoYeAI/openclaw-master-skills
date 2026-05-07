/**
 * 新用户注册测试 — 模拟 OpenClaw 调用 Skill 的完整注册流程
 */

const handler = require('../src/index')

async function testNewUserRegistration() {
  console.log('🦞 龙虾船长 - 新用户注册测试\n')
  console.log('=' .repeat(60))

  const L1_OPENID = process.env.L1_OPENID
  if (!L1_OPENID) { console.error('请设置 L1_OPENID 环境变量'); process.exit(1) }
  const TEST_PASSWORD = 'test123456'

  // 清理可能的旧密钥（确保是"新用户"）
  const fs = require('fs')
  const path = require('path')
  const os = require('os')
  const keyFile = path.join(os.homedir(), '.captain-lobster', 'keys', 'test-reg.key')
  const stateFile = path.join(os.homedir(), '.captain-lobster', 'state.json')
  if (fs.existsSync(keyFile)) fs.unlinkSync(keyFile)
  if (fs.existsSync(stateFile)) fs.unlinkSync(stateFile)

  const context = {
    config: {
      l1_openid: L1_OPENID,
      key_identity: 'test-reg',
      initial_gold: 10000
    }
  }

  // === Step 1: 尝试无密码初始化（应该要求密码） ===
  console.log('\n[Step 1] 无密码初始化...')
  const r1 = await handler({ action: 'start' }, context)
  console.log('  结果:', r1.success ? 'PASS' : 'FAIL')
  console.log('  消息:', r1.message)
  if (r1.requirePassword) {
    console.log('  ✅ 正确返回了 requirePassword 提示')
  } else {
    console.log('  ❌ 未返回 requirePassword')
  }

  // === Step 2: 提供密码进行首次注册 ===
  console.log('\n[Step 2] 首次注册（密码=' + TEST_PASSWORD + '）...')
  const r2 = await handler({ action: 'start', password: TEST_PASSWORD }, context)
  console.log('  结果:', r2.success ? '✅ PASS' : '❌ FAIL')
  console.log('  消息:', r2.message?.substring(0, 100))
  if (r2.data) {
    console.log('  船长名:', r2.data.captainName)
    console.log('  金币:', r2.data.gold)
    console.log('  位置:', r2.data.currentCity)
    console.log('  AgentCode:', r2.data.agentCode)
    console.log('  OpenID:', r2.data.openid?.substring(0, 30) + '...')
  }

  // === Step 3: 查询状态（应已初始化） ===
  console.log('\n[Step 3] 查询船长状态...')
  const r3 = await handler({ action: 'status' }, context)
  console.log('  结果:', r3.success ? '✅ PASS' : '❌ FAIL')
  if (r3.data) {
    console.log('  已初始化:', r3.data.initialized)
    console.log('  船长名:', r3.data.captainName)
    console.log('  金币:', r3.data.gold)
    console.log('  人格:', r3.data.personality?.trait)
    console.log('  口癖:', r3.data.personality?.quirk)
  }

  // === Step 4: 查看广州行情 ===
  console.log('\n[Step 4] 查看广州行情...')
  const r4 = await handler({ action: 'city', params: { city_id: 'canton' } }, context)
  console.log('  结果:', r4.success ? '✅ PASS' : '❌ FAIL')
  if (r4.data?.city) {
    console.log('  城市:', r4.data.city.name)
    console.log('  物价 (前 3 项):')
    const items = Object.entries(r4.data.city.prices || {}).slice(0, 3)
    for (const [item, price] of items) {
      console.log(`    ${item}: ${price}`)
    }
    console.log('  停靠玩家:', r4.data.players?.length || 0)
  } else {
    console.log('  原始数据:', JSON.stringify(r4).substring(0, 200))
  }

  // === Step 5: Ping L1 ===
  console.log('\n[Step 5] Ping L1 服务...')
  const r5 = await handler({ action: 'ping' }, context)
  console.log('  结果:', r5.success ? '✅ PASS' : '❌ FAIL')
  console.log('  数据:', r5.data)

  // === Step 6: 验证状态持久化 ===
  console.log('\n[Step 6] 验证状态持久化...')
  const stateExists = fs.existsSync(stateFile)
  console.log('  state.json 存在:', stateExists ? '✅' : '❌')
  if (stateExists) {
    const saved = JSON.parse(fs.readFileSync(stateFile, 'utf8'))
    console.log('  存档船长:', saved.identity?.captainName)
    console.log('  存档金币:', saved.game?.gold)
    console.log('  存档位置:', saved.game?.currentCity)
  }

  // === Step 7: 测试 Re-Act 循环 ===
  console.log('\n[Step 7] 测试 Re-Act 循环...')
  const r7 = await handler({ action: 'react' }, context)
  console.log('  结果:', r7.success ? '✅ PASS' : '❌ FAIL')
  if (r7.data) {
    console.log('  循环轮次:', r7.data.cycle)
    console.log('  观察数据:')
    console.log('    船长:', r7.data.observations?.captain?.name)
    console.log('    城市:', r7.data.observations?.captain?.currentCity)
    console.log('    金币:', r7.data.observations?.captain?.gold)
    console.log('    城市数据:', r7.data.observations?.city ? '✅' : '❌')
    console.log('    合约数据:', r7.data.observations?.contracts?.length, '个')
    console.log('    信箱消息:', r7.data.observations?.inbox?.length, '条')
    console.log('  Prompt 前 200 字:')
    console.log('    ' + (r7.data.prompt?.substring(0, 200) || '').replace(/\n/g, '\n    '))
  }

  // === Step 8: NPC 买入 ===
  console.log('\n[Step 8] NPC 买入 10 箱丝绸...')
  const r8 = await handler({ action: 'buy', params: { item: 'silk', amount: 10 } }, context)
  console.log('  结果:', r8.success ? '✅ PASS' : '❌ FAIL')
  if (r8.data) {
    console.log('  商品:', r8.data.item)
    console.log('  数量:', r8.data.amount)
    console.log('  单价:', r8.data.unitPrice)
    console.log('  总价:', r8.data.totalCost)
    console.log('  剩余金币:', r8.data.playerGold)
    console.log('  货舱:', JSON.stringify(r8.data.cargo))
  } else {
    console.log('  错误:', r8.message)
  }

  // === Step 9: NPC 再次买入（验证货舱累积） ===
  console.log('\n[Step 9] NPC 再买入 5 箱茶叶...')
  const r9 = await handler({ action: 'buy', params: { item: 'tea', amount: 5 } }, context)
  console.log('  结果:', r9.success ? '✅ PASS' : '❌ FAIL')
  if (r9.data) {
    console.log('  商品:', r9.data.item)
    console.log('  总价:', r9.data.totalCost)
    console.log('  剩余金币:', r9.data.playerGold)
    console.log('  货舱:', JSON.stringify(r9.data.cargo))
  } else {
    console.log('  错误:', r9.message)
  }

  // === Step 10: NPC 卖出 ===
  console.log('\n[Step 10] NPC 卖出 3 箱丝绸...')
  const r10 = await handler({ action: 'sell', params: { item: 'silk', amount: 3 } }, context)
  console.log('  结果:', r10.success ? '✅ PASS' : '❌ FAIL')
  if (r10.data) {
    console.log('  总价:', r10.data.totalCost)
    console.log('  剩余金币:', r10.data.playerGold)
    console.log('  货舱:', JSON.stringify(r10.data.cargo))
    // 验证丝绸减少了
    const silkCount = r10.data.cargo?.silk || 0
    console.log('  丝绸剩余:', silkCount, '(期望 7)')
    console.log('  数量正确:', silkCount === 7 ? '✅' : '❌')
  } else {
    console.log('  错误:', r10.message)
  }

  // === Step 11: 验证跨调用状态（金币和货舱应持久化） ===
  console.log('\n[Step 11] 跨调用状态验证...')
  const r11 = await handler({ action: 'status' }, context)
  console.log('  结果:', r11.success ? '✅ PASS' : '❌ FAIL')
  if (r11.data) {
    console.log('  金币:', r11.data.gold)
    console.log('  货舱:', JSON.stringify(r11.data.cargo))
    console.log('  位置:', r11.data.currentCity)
    console.log('  状态:', r11.data.status)
    const hasCargo = Object.values(r11.data.cargo || {}).reduce((a, b) => a + b, 0) > 0
    console.log('  货舱非空:', hasCargo ? '✅' : '❌')
    console.log('  金币 < 10000 (已消费):', r11.data.gold < 10000 ? '✅' : '❌')
  }

  // === Step 12: 起航前往另一城市 ===
  const destCity = (r11.data.currentCity === 'calicut') ? 'venice' : 'calicut'
  const destName = { calicut: '卡利卡特', venice: '威尼斯', canton: '广州', london: '伦敦' }[destCity] || destCity
  console.log(`\n[Step 12] 起航前往 ${destName} (${destCity})...`)
  const r12 = await handler({ action: 'move', params: { city: destCity } }, context)
  console.log('  结果:', r12.success ? '✅ PASS' : '❌ FAIL')
  if (r12.data) {
    console.log('  状态:', r12.data.status)
    console.log('  目标:', r12.data.targetCity)
    console.log('  距离:', r12.data.distance, 'km')
    console.log('  航行时间:', r12.data.sailingTime, '分钟')
  } else {
    console.log('  错误:', r12.message)
  }

  // === Step 13: 航行中无法交易 ===
  console.log('\n[Step 13] 航行中尝试交易（应被拒绝）...')
  const r13 = await handler({ action: 'buy', params: { item: 'spice', amount: 5 } }, context)
  console.log('  结果:', !r13.success ? '✅ PASS (正确拒绝)' : '❌ FAIL (不应该允许)')
  console.log('  消息:', r13.message)

  // === Step 14: 抵达卡利卡特 ===
  console.log('\n[Step 14] 抵达卡利卡特...')
  const r14 = await handler({ action: 'arrive' }, context)
  console.log('  结果:', r14.success ? '✅ PASS' : '❌ FAIL')
  if (r14.data) {
    console.log('  状态:', r14.data.status)
    console.log('  城市:', r14.data.city)
    console.log('  金币:', r14.data.gold)
    console.log('  货舱:', JSON.stringify(r14.data.cargo))
    console.log('  交割数:', r14.data.settleResults?.length || 0)
  } else {
    console.log('  错误:', r14.message)
  }

  // === Step 15: 查看新城市行情 ===
  console.log(`\n[Step 15] 查看 ${destName} 行情...`)
  const r15 = await handler({ action: 'city', params: { city_id: destCity } }, context)
  console.log('  结果:', r15.success ? '✅ PASS' : '❌ FAIL')
  if (r15.data?.city) {
    console.log('  城市:', r15.data.city.name)
    console.log('  特产:', r15.data.city.specialty?.join(', '))
    const prices = r15.data.city.prices
    console.log('  spice(香料):', prices?.spice, '(产地折扣应低于 600)')
    console.log('  pepper(胡椒):', prices?.pepper, '(产地折扣应低于 280)')
    console.log('  silk(丝绸):', prices?.silk)
  } else {
    console.log('  错误:', r15.message)
  }

  // === Step 16: 在新城市 NPC 交易 ===
  console.log(`\n[Step 16] 在 ${destName} 买入 8 箱香料（产地折扣）...`)
  const r16 = await handler({ action: 'buy', params: { item: 'spice', amount: 8 } }, context)
  console.log('  结果:', r16.success ? '✅ PASS' : '❌ FAIL')
  if (r16.data) {
    console.log('  商品:', r16.data.item)
    console.log('  单价:', r16.data.unitPrice)
    console.log('  总价:', r16.data.totalCost)
    console.log('  剩余金币:', r16.data.playerGold)
    console.log('  货舱:', JSON.stringify(r16.data.cargo))
    // 验证香料总数
    const spiceCount = r16.data.cargo?.spice || 0
    console.log('  香料:', spiceCount, '箱')
  } else {
    console.log('  错误:', r16.message)
  }

  // === 总结 ===
  console.log('\n' + '='.repeat(60))
  console.log('测试完成！')

  const allPassed = r2.success && r3.success && r4.success && r5.success &&
    r7.success && r8.success && r9.success && r10.success &&
    r11.success && r12.success && !r13.success && r14.success && r15.success && r16.success
  return allPassed
}

testNewUserRegistration()
  .then(allPassed => {
    console.log(allPassed ? '\n🎉 全部通过！' : '\n⚠️ 部分测试失败')
    process.exit(allPassed ? 0 : 1)
  })
  .catch(err => {
    console.error('💥 测试崩溃:', err)
    process.exit(1)
  })
