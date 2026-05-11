/**
 * @file state-store.js
 * @description 船长状态持久化 — 保存/恢复完整游戏状态到 ~/.captain-lobster/state.json
 *
 * 持久化内容：
 * - 船长身份（名字、人格、playerId、openid）
 * - 游戏状态（金币、货舱、当前位置、状态）
 * - 统计信息（循环次数、上次汇报时间）
 *
 * 敏感字段（captainToken, oceanBusApiKey）使用本机指纹派生的密钥进行
 * AES-256-GCM 加密后存储，防止 state 文件被复制到其他机器后凭证泄露。
 *
 * OceanBus 身份（agentId/openid/apiKey）由 oceanbus SDK 内部管理（~/.oceanbus/），
 * 本模块仅保留冗余备份以供恢复。
 *
 * 关键设计：每个 Skill 调用都是新进程，所有状态必须从磁盘恢复。
 */
const crypto = require('crypto')
const fs = require('fs')
const path = require('path')
const os = require('os')

const STATE_DIR = path.join(os.homedir(), '.captain-lobster')
const STATE_FILE = path.join(STATE_DIR, 'state.json')

// 从本机指纹派生 256 位密钥（不依赖用户密码，保证跨进程可用）
function _machineKey() {
  const seed = os.hostname() + os.homedir() + (os.userInfo().username || '')
  return crypto.createHash('sha256').update(seed).digest()
}

const SENSITIVE_FIELDS = ['captainToken', 'oceanBusApiKey']

function _encryptField(plaintext) {
  if (!plaintext || typeof plaintext !== 'string') return null
  const key = _machineKey()
  const iv = crypto.randomBytes(12)
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv)
  const enc = Buffer.concat([cipher.update(plaintext, 'utf8'), cipher.final()])
  const tag = cipher.getAuthTag()
  return Buffer.concat([iv, tag, enc]).toString('base64')
}

function _decryptField(ciphertext) {
  if (!ciphertext) return null
  const key = _machineKey()
  const buf = Buffer.from(ciphertext, 'base64')
  const iv = buf.subarray(0, 12)
  const tag = buf.subarray(12, 28)
  const enc = buf.subarray(28)
  const decipher = crypto.createDecipheriv('aes-256-gcm', key, iv)
  decipher.setAuthTag(tag)
  return Buffer.concat([decipher.update(enc), decipher.final()]).toString('utf8')
}

class StateStore {
  constructor() {
    this.ensureDir()
  }

  ensureDir() {
    if (!fs.existsSync(STATE_DIR)) {
      fs.mkdirSync(STATE_DIR, { recursive: true, mode: 0o700 })
    }
  }

  // ── 游戏状态 ──────────────────────────────────────

  save(state) {
    this.ensureDir()
    const identity = {
      captainName: state.captainName,
      captainPersonality: state.captainPersonality,
      playerId: state.playerId,
      openid: state.openid,
      captainToken: _encryptField(state.captainToken || null),
      addressBook: state.addressBook || {},
      l1Openid: state.l1Openid || null,
      ownerName: state.ownerName || null,
      keyIdentity: state.keyIdentity || 'default',
      oceanBusApiKey: _encryptField(state.oceanBusApiKey || null),
      oceanBusAgentId: state.oceanBusAgentId || null,
      oceanBusOpenid: state.oceanBusOpenid || null
    }
    const data = {
      version: 3,
      updatedAt: new Date().toISOString(),
      identity,
      game: {
        gold: state.gold,
        cargo: state.cargo || {},
        currentCity: state.currentCity || 'canton',
        targetCity: state.targetCity || null,
        status: state.status || 'docked',
        sailingTime: state.sailingTime || 0,
        lastMoveTime: state.lastMoveTime || 0,
        intent: state.intent || '',
        initialized: state.initialized === true,
        previousGold: state.previousGold || 0,
        intels: state.intels || []
      },
      stats: {
        reactCycleCount: state.reactCycleCount || 0,
        lastReportTime: state.lastReportTime || null,
        lastReactTime: state.lastReactTime || null,
        totalTrades: state.totalTrades || 0,
        totalProfit: state.totalProfit || 0
      }
    }

    this._atomicWrite(STATE_FILE, JSON.stringify(data, null, 2))
  }

  _atomicWrite(filePath, content) {
    const tmp = filePath + '.tmp.' + process.pid
    fs.writeFileSync(tmp, content, { mode: 0o600 })
    fs.renameSync(tmp, filePath)
  }

  load() {
    if (!fs.existsSync(STATE_FILE)) {
      return null
    }

    try {
      const data = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'))
      const id = data.identity || {}
      // v3+ 加密存储，v2 明文兼容迁移
      const isEncrypted = data.version >= 3
      return {
        captainName: id.captainName,
        captainPersonality: id.captainPersonality,
        playerId: id.playerId,
        openid: id.openid,
        captainToken: isEncrypted ? _decryptField(id.captainToken) : (id.captainToken || null),
        addressBook: id.addressBook || {},
        l1Openid: id.l1Openid || null,
        ownerName: id.ownerName || null,
        keyIdentity: id.keyIdentity || 'default',
        oceanBusApiKey: isEncrypted ? _decryptField(id.oceanBusApiKey) : (id.oceanBusApiKey || null),
        oceanBusAgentId: id.oceanBusAgentId || null,
        oceanBusOpenid: id.oceanBusOpenid || null,
        gold: data.game?.gold || 0,
        cargo: data.game?.cargo || {},
        currentCity: data.game?.currentCity || 'canton',
        targetCity: data.game?.targetCity || null,
        status: data.game?.status || 'docked',
        sailingTime: data.game?.sailingTime || 0,
        lastMoveTime: data.game?.lastMoveTime || 0,
        intent: data.game?.intent || '',
        initialized: data.game?.initialized || false,
        previousGold: data.game?.previousGold || 0,
        intels: data.game?.intels || [],
        reactCycleCount: data.stats?.reactCycleCount || 0,
        lastReportTime: data.stats?.lastReportTime || null,
        lastReactTime: data.stats?.lastReactTime || null,
        totalTrades: data.stats?.totalTrades || 0,
        totalProfit: data.stats?.totalProfit || 0
      }
    } catch (e) {
      return null
    }
  }

  reset() {
    if (fs.existsSync(STATE_FILE)) {
      fs.unlinkSync(STATE_FILE)
    }
  }

  hasSave() {
    return fs.existsSync(STATE_FILE)
  }
}

module.exports = { StateStore, STATE_DIR, STATE_FILE }
