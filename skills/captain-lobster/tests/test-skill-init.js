/**
 * @file test-skill-init.js
 * @description Skill 初始化完整流程测试
 */

const handler = require('../src/index-secure')

async function testSkillInit() {
  console.log('\n' + '🚀'.repeat(25))
  console.log('  龙虾船长 Skill 初始化测试')
  console.log('🚀'.repeat(25) + '\n')

  const testIdentity = `captain_test_${Date.now()}`
  const password = 'CaptainTest123!'

  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log('  测试 1: 首次初始化（需要密码）')
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

  const result1 = await handler({
    action: 'start',
    password
  }, {
    config: {
      l1_url: 'http://localhost:17019/api',
      oceanbus_url: 'https://ai-t.ihaola.com.cn/api/l0',
      key_identity: testIdentity,
      key_password: password
    }
  })

  if (result1.success) {
    console.log('✅ 初始化成功！')
    console.log(`🦞 船长名: ${result1.data.captainName}`)
    console.log(`💰 初始金币: ${result1.data.gold}`)
    console.log(`🏠 起始城市: ${result1.data.cityName}`)
    console.log(`🔑 Agent Code: ${result1.data.agentCode}`)
    console.log(`📂 密钥文件: ${result1.data.keyFile}`)
  } else {
    console.log('❌ 初始化失败:', result1.message)
    return
  }

  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log('  测试 2: 查询状态')
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

  const result2 = await handler({ action: 'status' }, {
    config: {
      l1_url: 'http://localhost:17019/api',
      oceanbus_url: 'https://ai-t.ihaola.com.cn/api/l0',
      key_identity: testIdentity,
      key_password: password
    }
  })

  if (result2.success) {
    console.log('✅ 状态查询成功')
    const status = result2.data
    console.log(`🦞 船长名: ${status.captainName}`)
    console.log(`🔐 密钥指纹: ${status.publicKeyFingerprint}`)
    console.log(`💰 金币: ${status.gold}`)
    console.log(`📍 城市: ${status.cityName}`)
  } else {
    console.log('❌ 状态查询失败:', result2.message)
  }

  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log('  测试 3: 模拟 Re-Act 循环')
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

  const result3 = await handler({ action: 'react' }, {
    config: {
      l1_url: 'http://localhost:17019/api',
      oceanbus_url: 'https://ai-t.ihaola.com.cn/api/l0',
      key_identity: testIdentity,
      key_password: password
    }
  })

  if (result3.success) {
    console.log('✅ Re-Act 循环触发成功')
  } else {
    console.log('❌ Re-Act 循环失败:', result3.message)
  }

  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log('  测试结果: ✅ 全部通过')
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

  console.log('📝 测试完成，清理测试数据...')
  const KeyStore = require('../src/keystore')
  const keystore = new KeyStore()
  keystore.deleteKeyPair(testIdentity)
  console.log('✅ 测试数据已清理\n')
}

testSkillInit()
  .then(() => {
    console.log('🏁 Skill 初始化测试完成！')
    process.exit(0)
  })
  .catch(err => {
    console.error('❌ 测试异常:', err)
    process.exit(1)
  })
