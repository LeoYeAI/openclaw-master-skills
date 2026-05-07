/**
 * @file tests/index.test.js
 * @description Captain Lobster Skill 测试
 */

const handler = require('../src/index')

async function runTests() {
  console.log('🦞 Captain Lobster Skill 测试\n')

  let passed = 0
  let failed = 0

  async function test(name, fn) {
    try {
      await fn()
      console.log(`✅ ${name}`)
      passed++
    } catch (err) {
      console.log(`❌ ${name}`)
      console.log(`   错误: ${err.message}`)
      failed++
    }
  }

  async function assertEqual(actual, expected, message = '') {
    if (actual !== expected) {
      throw new Error(`${message} 期望 ${expected}，实际 ${actual}`)
    }
  }

  async function assertTrue(value, message = '') {
    if (!value) {
      throw new Error(message || '期望 truthy，实际 falsy')
    }
  }

  await test('测试未知操作返回错误', async () => {
    const result = await handler({ action: 'unknown' }, {})
    await assertTrue(result.success === false, '应该返回失败')
    await assertTrue(result.message.includes('未知操作'), '应该包含未知操作提示')
  })

  await test('测试状态查询（未初始化）', async () => {
    const result = await handler({ action: 'status' }, {})
    await assertTrue(result.success === true, '应该返回成功')
    await assertTrue(result.data.initialized === false, '应该未初始化')
  })

  console.log(`\n测试完成: ${passed} 通过, ${failed} 失败`)
  return failed === 0
}

runTests()
  .then(success => process.exit(success ? 0 : 1))
  .catch(err => {
    console.error('测试异常:', err)
    process.exit(1)
  })
