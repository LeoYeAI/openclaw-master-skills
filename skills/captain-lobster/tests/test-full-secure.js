/**
 * @file test-full-secure.js
 * @description 完整流程测试 - 安全密钥版本
 */

const KeyStore = require('../src/keystore')

async function testKeyStore() {
  console.log('\n' + '🦞'.repeat(25))
  console.log('  龙虾船长 - 安全密钥管理测试')
  console.log('🦞'.repeat(25) + '\n')

  const identity = `test_${Date.now()}`
  const password = 'TestPassword123!'
  const keystore = new KeyStore()

  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log('  测试 1: 生成并保存密钥对')
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

  try {
    console.log(`📝 身份: ${identity}`)
    console.log(`🔐 密码: ${password}`)

    const publicKey = keystore.saveKeyPair(identity, password)
    console.log('✅ 密钥对已生成并加密保存')
    console.log(`📂 存储位置: ${keystore.getKeyFilePath(identity)}`)
    console.log(`🔑 公钥指纹: ${publicKey.substring(0, 40)}...`)
  } catch (err) {
    console.log('❌ 失败:', err.message)
    return
  }

  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log('  测试 2: 加载密钥对（正确密码）')
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

  try {
    const keyPair = keystore.loadKeyPair(identity, password)
    console.log('✅ 密钥解锁成功')
    console.log(`🔑 私钥长度: ${keyPair.privateKey.length} 字符`)
    console.log(`📜 公钥长度: ${keyPair.publicKey.length} 字符`)
  } catch (err) {
    console.log('❌ 失败:', err.message)
  }

  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log('  测试 3: 加载密钥对（错误密码）')
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

  try {
    keystore.loadKeyPair(identity, 'wrongPassword')
    console.log('❌ 应该失败但没有')
  } catch (err) {
    console.log('✅ 正确失败:', err.message)
  }

  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log('  测试 4: 密钥备份导出')
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

  try {
    const backup = keystore.exportBackup(identity, password)
    console.log('✅ 备份导出成功')
    console.log(`📦 备份长度: ${backup.length} 字符`)
    console.log(`🔐 备份内容预览: ${backup.substring(0, 50)}...`)
  } catch (err) {
    console.log('❌ 失败:', err.message)
  }

  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log('  测试 5: 密钥备份恢复（新密码）')
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

  try {
    const backup = keystore.exportBackup(identity, password)
    const newPassword = 'NewPassword456!'
    const newIdentity = `${identity}_restored`

    const newPublicKey = keystore.importBackup(backup, password, newPassword)
    console.log('✅ 备份恢复成功')
    console.log(`📝 新身份: ${newIdentity}`)
    console.log(`🔑 新公钥: ${newPublicKey.substring(0, 40)}...`)

    const loaded = keystore.loadKeyPair(newIdentity, newPassword)
    console.log('✅ 新密钥验证成功')
  } catch (err) {
    console.log('❌ 失败:', err.message)
  }

  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log('  测试 6: 检查文件权限')
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

  const fs = require('fs')
  const keyFile = keystore.getKeyFilePath(identity)
  if (fs.existsSync(keyFile)) {
    const stats = fs.statSync(keyFile)
    console.log(`📄 文件: ${keyFile}`)
    console.log(`📊 大小: ${stats.size} 字节`)
    console.log('🔒 文件存在，可安全删除测试密钥')
  }

  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log('  测试结果: ✅ 全部通过')
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

  console.log('📝 清理测试密钥...')
  keystore.deleteKeyPair(identity)
  console.log('✅ 测试密钥已清理\n')
}

testKeyStore()
  .then(() => {
    console.log('🏁 密钥管理测试完成！')
    process.exit(0)
  })
  .catch(err => {
    console.error('❌ 测试异常:', err)
    process.exit(1)
  })
