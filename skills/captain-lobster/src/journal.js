/**
 * @file journal.js
 * @description 航海日志持久化管理器
 */

const fs = require('fs')
const fsp = require('fs/promises')
const path = require('path')
const os = require('os')

const LOG_DIR = path.join(os.homedir(), '.captain-lobster', 'logs')
const MAX_LOGS = 500

const ACTION_TRANSLATIONS = {
  '船长觉醒完成': '船长觉醒了',
  '买入': '在市场买了',
  '卖出': '在市场卖了',
  '航行至': '航行到了',
  '启航': '起锚出海了',
  '抵达': '顺利抵达',
  '创建合约': '谈成了一笔生意',
  '挂牌': '挂出了招牌',
  '交割完成': '货物和金币已交换完毕',
  '合约取消': '一笔生意黄了',
  '发送消息': '给别的船长发了消息',
  '收到消息': '收到了消息'
}

const ITEM_NAMES = {
  silk: '丝绸', tea: '茶叶', porcelain: '瓷器', spice: '香料',
  pearl: '珍珠', perfume: '香水', gem: '宝石', ivory: '象牙',
  cotton: '棉花', coffee: '咖啡', pepper: '胡椒'
}

class CaptainJournal {
  constructor(captainName) {
    this.captainName = captainName || 'Unknown'
    this.logs = []
    this.loadLogs()
  }

  /**
   * 异步工厂方法 — 从磁盘恢复日志后返回实例
   */
  static async create(captainName) {
    const journal = new CaptainJournal(captainName)
    await journal.loadLogsAsync()
    return journal
  }

  getLogFilePath(date) {
    date = date || new Date()
    const dateStr = date.toISOString().split('T')[0]
    return path.join(LOG_DIR, dateStr + '.md')
  }

  // ── 同步文件操作（向后兼容） ──────────────────────────────

  loadLogs() {
    if (!fs.existsSync(LOG_DIR)) {
      fs.mkdirSync(LOG_DIR, { recursive: true, mode: 0o700 })
      return
    }
    // 加载最近3天的日志
    const allLogs = []
    for (let d = 2; d >= 0; d--) {
      const date = new Date()
      date.setDate(date.getDate() - d)
      const dateFile = this.getLogFilePath(date)
      if (fs.existsSync(dateFile)) {
        const content = fs.readFileSync(dateFile, 'utf8')
        const dayLogs = this.parseLogsFromMarkdown(content)
        allLogs.push(...dayLogs)
      }
    }
    this.logs = allLogs.slice(-MAX_LOGS)
  }

  saveToFile(entry) {
    if (!fs.existsSync(LOG_DIR)) {
      fs.mkdirSync(LOG_DIR, { recursive: true, mode: 0o700 })
    }
    const todayFile = this.getLogFilePath()
    const logLine = '\n[' + entry.time + '] ' + entry.action
    if (entry.details && Object.keys(entry.details).length > 0) {
      const detailStr = Object.entries(entry.details)
        .map(([k, v]) => k + ': ' + v).join(', ')
      fs.appendFileSync(todayFile, logLine + ' > ' + detailStr, 'utf8')
    } else {
      fs.appendFileSync(todayFile, logLine, 'utf8')
    }
  }

  // ── 异步文件操作 ──────────────────────────────────────────

  async loadLogsAsync() {
    try {
      await fsp.mkdir(LOG_DIR, { recursive: true, mode: 0o700 })
    } catch (e) {
      // directory already exists
    }
    try {
      const todayFile = this.getLogFilePath()
      const content = await fsp.readFile(todayFile, 'utf8')
      this.logs = this.parseLogsFromMarkdown(content)
    } catch (e) {
      // file doesn't exist yet
    }
  }

  async saveToFileAsync(entry) {
    try {
      await fsp.mkdir(LOG_DIR, { recursive: true, mode: 0o700 })
    } catch (e) {}
    const todayFile = this.getLogFilePath()
    const logLine = '\n[' + entry.time + '] ' + entry.action
    if (entry.details && Object.keys(entry.details).length > 0) {
      const detailStr = Object.entries(entry.details)
        .map(([k, v]) => k + ': ' + v).join(', ')
      await fsp.appendFile(todayFile, logLine + ' > ' + detailStr, 'utf8')
    } else {
      await fsp.appendFile(todayFile, logLine, 'utf8')
    }
  }

  // ── 日志解析 ──────────────────────────────────────────────

  parseLogsFromMarkdown(content) {
    const logs = []
    const lines = content.split('\n')
    let currentEntry = null

    for (const line of lines) {
      const timeMatch = line.match(/^\[(\d{2}:\d{2}:\d{2})\]/)
      if (timeMatch) {
        if (currentEntry) logs.push(currentEntry)
        currentEntry = {
          time: timeMatch[1],
          action: line.slice(timeMatch[0].length).trim(),
          details: {}
        }
        continue
      }
      if (currentEntry && line.charCodeAt(0) === 62 /* '>' */) {
        const detailStr = line.replace(/^>\s*/, '').trim()
        for (const part of detailStr.split(',')) {
          const colonIdx = part.indexOf(':')
          if (colonIdx > 0) {
            currentEntry.details[part.slice(0, colonIdx).trim()] = part.slice(colonIdx + 1).trim()
          }
        }
      }
    }
    if (currentEntry) logs.push(currentEntry)

    return logs
  }

  // ── 日志操作 ──────────────────────────────────────────────

  addLog(action, details) {
    details = details || {}
    const now = new Date()
    const timeStr = now.toLocaleTimeString('zh-CN', {
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    })

    const logEntry = {
      timestamp: now.getTime(),
      time: timeStr,
      action: this.translateAction(action),
      details
    }

    this.logs.push(logEntry)
    if (this.logs.length > MAX_LOGS) {
      this.logs = this.logs.slice(-MAX_LOGS)
    }

    this.saveToFile(logEntry)
    return logEntry
  }

  async addLogAsync(action, details) {
    details = details || {}
    const now = new Date()
    const timeStr = now.toLocaleTimeString('zh-CN', {
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    })

    const logEntry = {
      timestamp: now.getTime(),
      time: timeStr,
      action: this.translateAction(action),
      details
    }

    this.logs.push(logEntry)
    if (this.logs.length > MAX_LOGS) {
      this.logs = this.logs.slice(-MAX_LOGS)
    }

    await this.saveToFileAsync(logEntry)
    return logEntry
  }

  translateAction(action) {
    const key = Object.keys(ACTION_TRANSLATIONS).find(k => action.includes(k))
    return key ? action.replace(key, ACTION_TRANSLATIONS[key]) : action
  }

  translateItem(item) {
    return ITEM_NAMES[item] || item
  }

  // ── 日报 ──────────────────────────────────────────────────

  generateDailyReport(gold, cargo, previousGold) {
    gold = gold || 0
    cargo = cargo || {}
    previousGold = previousGold || gold
    const profit = gold - previousGold
    const profitSign = profit >= 0 ? '+' : ''
    const profitText = profit > 0 ? '赚钱' : (profit < 0 ? '亏钱' : '持平')

    const cargoList = Object.entries(cargo)
      .filter(([, v]) => v > 0)
      .map(([k, v]) => v + '箱' + this.translateItem(k))
      .join('、') || '空空如也'

    const now = new Date()
    const dateStr = now.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' })
    const timeStr = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })

    let report = '# ' + this.captainName + ' 日报\n\n'
    report += '**' + dateStr + ' ' + timeStr + '**\n\n'
    report += '---\n\n'
    report += '## 财务状况\n\n'
    report += '- 金币: **' + gold.toLocaleString() + '** ' + profitSign + profit + ' (' + profitText + ')\n'
    report += '- 货舱: ' + cargoList + '\n\n'
    report += '---\n\n'
    report += '## 今日动态\n\n'

    const todayLogs = this.logs.filter(log => {
      const logDate = new Date(log.timestamp)
      const today = new Date()
      return logDate.toDateString() === today.toDateString()
    })

    if (todayLogs.length === 0) {
      report += '今天风平浪静，暂时没有记录。\n'
    } else {
      for (const log of todayLogs.slice(-10)) {
        report += '- [' + log.time + '] ' + log.action + '\n'
        if (log.details && Object.keys(log.details).length > 0) {
          const detailStr = Object.entries(log.details)
            .map(([k, v]) => k + ': ' + v).join(', ')
          report += '  > ' + detailStr + '\n'
        }
      }
    }

    report += '\n---\n\n'
    report += CaptainJournal.getHumor(profit) + '\n'
    return report
  }

  // ── 工具 ──────────────────────────────────────────────────

  static getHumor(profit) {
    if (profit > 500) {
      const msgs = ['愿海洋保佑您主人', '今日大吉', '财源广进']
      return msgs[Math.floor(Math.random() * msgs.length)] + '!'
    }
    if (profit > 0) return '稳扎稳打，明天会更好'
    if (profit < -500) return '今天亏了点...但别担心，涨涨涨在后面呢'
    return '休养生息，等待时机'
  }

  getRecentLogs(count) {
    return this.logs.slice(-(count || 20))
  }

  summarizeRecent(logs) {
    if (!logs || logs.length === 0) return null
    const lines = logs.map(l => {
      let line = `[${l.time}] ${l.action}`
      if (l.details && Object.keys(l.details).length > 0) {
        const d = Object.entries(l.details).map(([k, v]) => `${k}=${v}`).join('，')
        line += '（' + d + '）'
      }
      return line
    })
    return '近50条航海日志：\n' + lines.join('\n')
  }
}

module.exports = CaptainJournal
