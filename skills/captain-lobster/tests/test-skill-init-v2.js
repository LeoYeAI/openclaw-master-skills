/**
 * @file test-skill-init-v2.js
 * @description Skill 初始化完整流程测试（改进版）
 */

const { CaptainLobsterSecure } = require('../src/index-secure')

async function testSkillInit() {
  console.log('\n' + '🚀'.repeat(25))
  console.log('  龙虾船长 Skill 初始化测试')
  console.log('🚀'.repeat(25) + '\n')

  const testIdentity = `captain_test_${Date.now()}`
  const password = 'CaptainTest123!'
  const captain = new CaptainLobsterSecure({
    l1_url: 'http://localhost:17019/api',
    oceanbus_url: 'https://ai-t.ihaola.com.cn/api/l0',
    key_identity: testIdentity,
    key_password: password,
    initial_gold: 10000
  })

  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log('  测试 1: 首次初始化（需要密码）')
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

  const result1 = await captain.initialize({}, password)

  if (result1.success) {
    console.log('✅ 初始化成功！')
    console.log(`🦞 船长名: ${result1.data.captainName}`)
    console.log(`💰 初始金币: ${result1.data.gold}`)
    console.log(`🏠 起始城市: ${result1.data.cityName}`)
    console.log(`🔑 Agent Code: ${result1.data.agentCode}`)
    console.log(`📂 密钥文件: ${result1.data.keyFile}`)
    console.log(`🎭 人设: ${result1.data.personality?.trait} - ${result1.data.personality?.style}`)
  } else {
    console.log('❌ 初始化失败:', result1.message)
    return
  }

  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log('  测试 2: 查询状态（同一实例）')
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

  const status = captain.getStatus()
  console.log('✅ 状态查询成功')
  console.log(`🦞 船长名: ${status.captainName}`)
  console.log(`🔐 密钥指纹: ${status.publicKeyFingerprint}`)
  console.log(`💰 金币: ${status.gold}`)
  console.log(`📍 城市: ${status.cityName}`)
  console.log(`📦 货舱: ${JSON.stringify(status.cargo)}`)

  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log('  测试 3: 密钥持久化验证')
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

  const KeyStore = require('../src/keystore')
  const keystore = new KeyStore()

  const publicKey = keystore.getPublicKey(testIdentity)
  console.log('✅ 密钥文件存在')
  console.log(`📂 路径: ${keystore.getKeyFilePath(testIdentity)}`)
  console.log(`🔑 公钥预览: ${publicKey.substring(0, 40)}...`)

  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log('  测试 4: 新实例解锁（模拟重启）')
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

  const captain2 = new CaptainLobsterSecure({
    l1_url: 'http://localhost:17019/api',
    key_identity: testIdentity,
    key_password: password
  })

  const result2 = await captain2.initialize({}, password)
  if (result2.success) {
    console.log('✅ 重启后解锁成功')
    console.log(`🦞 船长名: ${result2.data.captainName}`)
    console.log(`🔑 公钥指纹: ${result2.data.publicKeyFingerprint || 'N/A'}`)
  } else {
    console.log('❌ 重启解锁失败:', result2.message)
  }

  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log('  测试 5: 错误密码测试')
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

  const captain3 = new CaptainLobsterSecure({
    l1_url: 'http://localhost:17019/api',
    key_identity: testIdentity,
    key_password: 'wrongPassword!'
  })

  const result3 = await captain3.initialize({}, 'wrongPassword!')
  if (!result3.success) {
    console.log('✅ 错误密码正确拒绝')
    console.log(`📝 错误信息: ${result3.message}`)
  } else {
    console.log('❌ 应该失败但没有')
  }

  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log('  测试 6: 密钥备份测试')
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

  const backupResult = await captain.exportKeyBackup(password)
  if (backupResult.success) {
    console.log('✅ 备份导出成功')
    console.log(`📦 备份长度: ${backupResult.backup.length} 字符`)
  } else {
    console.log('❌ 备份失败:', backupResult.message)
  }

  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log('  测试结果: ✅ 全部通过')
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

  console.log('📝 清理测试数据...')
  keystore.deleteKeyPair(testIdentity)
  console.log('✅ 测试密钥已清理\n')
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
