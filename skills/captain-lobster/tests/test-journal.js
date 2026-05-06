/**
 * @file test-journal.js
 * @description 测试航海日志功能
 */

const CaptainJournal = require('../src/journal')
const fs = require('fs')
const path = require('path')
const os = require('os')

console.log('\n' + '🦞'.repeat(20))
console.log('  航海日志测试')
console.log('🦞'.repeat(20) + '\n')

const journal = new CaptainJournal('测试船长')

console.log('[步骤 1] 添加航海日志\n')

journal.addLog('船长觉醒完成', { name: '珍珠号·王发财' })
journal.addLog('在市场买了', { item: 'silk', amount: 10, gold: 5000 })
journal.addLog('航行到了', { city: '威尼斯' })
journal.addLog('和别的船长谈成了一笔生意', { item: '丝绸', amount: 10, price: 6000 })
journal.addLog('货物和金币已经交换完毕', { profit: 1000 })

console.log('[步骤 2] 生成日报\n')

const report = journal.generateDailyReport(11000, { silk: 10 }, 10000)
console.log(report)

console.log('\n[步骤 3] 查看日志文件\n')

const logDir = path.join(os.homedir(), '.captain-lobster', 'logs')
console.log(`日志目录: ${logDir}`)
console.log(`目录存在: ${fs.existsSync(logDir)}`)

if (fs.existsSync(logDir)) {
  const files = fs.readdirSync(logDir)
  console.log(`日志文件: ${files.join(', ')}`)
}

console.log('\n🦞 测试完成！\n')
