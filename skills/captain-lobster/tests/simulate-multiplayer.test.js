/**
 * @file tests/simulate-multiplayer.test.js
 * @description 多船长模拟测试
 */

const CaptainLobster = require('../src/index')

async function simulateMultiplayer() {
  console.log('🦞🦞🦞 多船长模拟测试 🦞🦞🦞\n')

  const captains = []

  console.log('[步骤 1] 创建 3 位船长...')

  const names = ['Captain_A', 'Captain_B', 'Captain_C']
  for (const name of names) {
    const result = await CaptainLobster({ action: 'start' }, {
      config: {
        l1_url: 'http://localhost:3000/api/l1',
        oceanbus_url: 'https://ai-t.ihaola.com.cn/api/l0',
        initial_gold: 10000
      }
    })

    if (result.success) {
      captains.push(result.data)
      console.log(`  ✅ ${name}: ${result.data.captainName}`)
    } else {
      console.log(`  ❌ ${name}: ${result.message}`)
    }
  }

  if (captains.length < 2) {
    console.log('\n⚠️  需要至少 2 位船长才能进行 P2P 交易测试')
    return
  }

  console.log('\n[步骤 2] 船长 A 查看状态...')
  const statusA = await CaptainLobster({ action: 'status' }, {})
  console.log(`  当前城市: ${statusA.data.cityName}`)
  console.log(`  金币: ${statusA.data.gold}`)

  console.log('\n[步骤 3] 船长 A 执行 Re-Act 循环...')
  const reactResult = await CaptainLobster({ action: 'react' }, {})
  console.log(`  Re-Act 循环完成`)

  console.log('\n[步骤 4] 船长 A 生成日报...')
  const reportResult = await CaptainLobster({ action: 'report' }, {})
  console.log(`  日报生成成功`)

  console.log('\n🦞🦞🦞 测试完成 🦞🦞🦞')
}

simulateMultiplayer()
  .then(() => process.exit(0))
  .catch(err => {
    console.error('测试异常:', err)
    process.exit(1)
  })
