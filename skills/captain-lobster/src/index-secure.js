/**
 * @file index-secure.js
 * @description 龙虾船长 Skill - OceanBus 消息驱动架构
 *
 * 架构：
 * - 通过 OceanBus L0 与 L1 服务通信
 * - L1_OPENID 环境变量配置 L1 服务的 OpenID
 */

const KeyStore = require('./keystore')
const CaptainJournal = require('./journal')
const OceanBusClient = require('./oceanbus')

const OCEANBUS_URL = process.env.OCEANBUS_URL || 'https://ai-t.ihaola.com.cn/api/l0'
const L1_OPENID = process.env.L1_OPENID

class CaptainLobsterSecure {
  constructor(config = {}) {
    this.config = {
      oceanBusUrl: OCEANBUS_URL,
      initialGold: config.initial_gold || 10000,
      keyPassword: config.key_password || null,
      keyIdentity: config.key_identity || 'default',
      l1Openid: config.l1_openid || L1_OPENID
    }

    this.oceanBus = new OceanBusClient(this.config.oceanBusUrl)
    this.keyStore = new KeyStore()
    this.journal = new CaptainJournal(config.captain_name || 'Captain')

    this.state = {
      initialized: false,
      captainName: null,
      captainPersonality: null,
      keyPair: null,
      playerId: null,
      openid: null,
      gold: 0,
      cargo: {},
      currentCity: 'canton',
      targetCity: null,
      status: 'docked',
      intent: '',
      log: []
    }
  }

  async initialize(password = null) {
    if (this.state.initialized) {
      return { success: true, message: '船长已经觉醒，无需重复初始化' }
    }

    if (!this.config.l1Openid) {
      return { success: false, message: '未配置 L1_OPENID 环境变量，请先启动 L1 服务并获取 OpenID' }
    }

    console.log('🦞 龙虾船长正在觉醒...')

    if (!this.keyStore.hasKeyPair(this.config.keyIdentity)) {
      if (!password || password.length < 8) {
        return {
          success: false,
          message: '首次启动需要设置密码（至少 8 个字符）来保护您的私钥',
          requirePassword: true
        }
      }
      console.log('🔐 生成新密钥对并加密存储...')
      this.keyStore.saveKeyPair(this.config.keyIdentity, password)
      this.state.keyPair = this.keyStore.loadKeyPair(this.config.keyIdentity, password)
    } else {
      if (!password) {
        return {
          success: false,
          message: '需要输入密码来解锁您的私钥',
          requirePassword: true,
          hasExistingKey: true
        }
      }
      console.log('🔓 正在解锁密钥...')
      try {
        this.state.keyPair = this.keyStore.loadKeyPair(this.config.keyIdentity, password)
        console.log('✅ 密钥解锁成功')
      } catch (err) {
        return { success: false, message: '密码错误，无法解锁私钥' }
      }
    }

    const regResult = await this.oceanBus.register()
    if (regResult.code !== 0) {
      return { success: false, message: 'OceanBus 注册失败' }
    }
    if (!this.oceanBus.isReady()) {
      return { success: false, message: 'OceanBus 注册异常：未获取完整身份' }
    }
    console.log(`✅ OceanBus 注册成功, AgentCode: ${this.oceanBus.agentId}, OpenID: ${this.oceanBus.openid}`)

    this.generateCaptainIdentity()

    const enrollResult = await this.sendToL1('enroll', {
      openid: this.oceanBus.openid,
      publicKey: this.keyStore.stripPemHeader(this.state.keyPair.publicKey),
      initialGold: this.config.initialGold
    })

    if (!enrollResult.success) {
      return enrollResult
    }

    this.state.playerId = enrollResult.data.doc.id
    this.state.openid = enrollResult.data.doc.openid
    this.state.gold = enrollResult.data.doc.gold
    this.state.initialized = true

    const greeting = this.generateGreeting()
    this.journal.addLog('船长觉醒完成', { name: this.state.captainName })

    return {
      success: true,
      message: greeting,
      data: {
        captainName: this.state.captainName,
        playerId: this.state.playerId,
        agentId: this.oceanBus.agentId,
        openid: this.state.openid,
        gold: this.state.gold,
        currentCity: this.state.currentCity
      }
    }
  }

  async sendToL1(action, params) {
    const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    const request = { action, request_id: requestId, ...params }

    console.log(`[Skill] 发送 ${action} 到 L1...`)
    await this.oceanBus.sendMessage(this.config.l1Openid, JSON.stringify(request))

    const reply = await this.oceanBus.pollForReply(requestId, 30, 1000)

    if (!reply) {
      return { success: false, message: 'L1 服务响应超时' }
    }

    if (reply.code === 0) {
      return { success: true, data: reply.data }
    } else {
      return { success: false, message: reply.data?.msg || reply.msg || 'L1 请求失败' }
    }
  }

  async sendP2PMessage(peerOpenid, content) {
    if (!this.oceanBus.isReady()) {
      return { success: false, message: 'OceanBus 未初始化' }
    }
    const result = await this.oceanBus.sendMessage(peerOpenid, content)
    if (result.code === 0) {
      this.journal.addLog('发送消息', { peer: peerOpenid.substring(0, 20) })
      return { success: true, data: result.data }
    }
    return { success: false, message: result.msg || 'P2P 消息发送失败' }
  }

  async checkInbox() {
    if (!this.oceanBus.isReady()) {
      return { success: false, message: 'OceanBus 未初始化' }
    }
    const result = await this.oceanBus.syncMessages()
    if (result.code === 0 && result.data) {
      const messages = this.oceanBus.parseMessages(result.data.messages)
      this.journal.addLog('收到消息', { count: messages.length })
      return { success: true, data: { messages, count: messages.length } }
    }
    return { success: false, message: '同步消息失败' }
  }

  async createSignedTrade(tradePayload) {
    if (!this.state.keyPair) {
      return { success: false, message: '密钥未解锁' }
    }
    const signature = this.keyStore.signTrade(this.state.keyPair.privateKey, tradePayload)
    return {
      success: true,
      data: {
        ...tradePayload,
        buyer_signature: signature
      }
    }
  }

  generateCaptainIdentity() {
    const namePools = ['贝壳', '珍珠', '珊瑚', '海螺', '龙虾', '鲨鱼', '海龟', '章鱼', '鲸鱼', '海马']
    const surnamePools = ['王', '李', '陈', '张', '刘']
    const wealthPools = ['大富', '小财', '发', '贵', '财']

    const personalities = [
      { trait: '乐观激进', style: '满嘴跑火车型', quirk: '说话必带"发财"二字' },
      { trait: '悲观精明', style: '算账狂魔型', quirk: '总是担心亏钱' },
      { trait: '冷静理性', style: '数据说话型', quirk: '张口就是"根据市场规律..."' },
      { trait: '浪漫冒险', style: '故事大王型', quirk: '总是讲自己年轻时的冒险故事' }
    ]

    this.state.captainName = `${namePools[Math.floor(Math.random() * namePools.length)]}号·${surnamePools[Math.floor(Math.random() * surnamePools.length)]}${wealthPools[Math.floor(Math.random() * wealthPools.length)]}`
    this.state.captainPersonality = personalities[Math.floor(Math.random() * personalities.length)]
  }

  generateGreeting() {
    const p = this.state.captainPersonality
    return `${this.state.captainName} 听候差遣！\n\n当前停靠 ${this.state.currentCity}，金币 ${this.state.gold}。\n\n${p.quirk}`
  }

  getStatus() {
    return {
      captainName: this.state.captainName,
      personality: this.state.captainPersonality,
      playerId: this.state.playerId,
      agentId: this.oceanBus.agentId,
      openid: this.state.openid,
      gold: this.state.gold,
      cargo: this.state.cargo,
      currentCity: this.state.currentCity,
      targetCity: this.state.targetCity,
      status: this.state.status,
      initialized: this.state.initialized,
      oceanBus: this.oceanBus.getStatus()
    }
  }

  async getCity(cityId) {
    return await this.sendToL1('get_city', { city_id: cityId })
  }

  async tradeNpc(item, amount, action) {
    const result = await this.sendToL1('trade_npc', {
      openid: this.state.openid,
      item,
      amount,
      trade_action: action
    })
    if (result.success) {
      this.state.gold = result.data.playerGold || result.data.gold
      this.state.cargo = result.data.cargo
      this.journal.addLog(action === 'buy' ? '买入' : '卖出', { item, amount })
    }
    return result
  }

  async moveTo(targetCity) {
    const result = await this.sendToL1('move', {
      openid: this.state.openid,
      target_city: targetCity
    })
    if (result.success) {
      this.state.status = result.data.status
      if (this.state.status === 'docked') {
        this.state.currentCity = result.data.targetCity
        this.state.targetCity = null
        this.journal.addLog('抵达', { city: this.state.currentCity })
      } else {
        this.state.targetCity = targetCity
        this.journal.addLog('启航', { target: targetCity, time: result.data.sailingTime })
      }
    }
    return result
  }

  async arrive() {
    const result = await this.sendToL1('arrive', { openid: this.state.openid })
    if (result.success) {
      this.state.gold = result.data.playerGold || result.data.gold
      this.state.cargo = result.data.cargo
      this.state.status = 'docked'
      if (result.data.settleResults && result.data.settleResults.length > 0) {
        this.journal.addLog('交割完成', { results: result.data.settleResults })
      }
    }
    return result
  }

  async updateIntent(intent) {
    const result = await this.sendToL1('intent', {
      openid: this.state.openid,
      intent
    })
    if (result.success) {
      this.state.intent = intent
      this.journal.addLog('挂牌', { intent: intent.substring(0, 30) })
    }
    return result
  }

  async createContract(buyerOpenid, sellerOpenid, item, amount, price, deliveryCity) {
    const tradePayload = {
      buyer_openid: buyerOpenid,
      seller_openid: sellerOpenid,
      item,
      amount,
      total_price: price * amount,
      delivery_city: deliveryCity
    }

    const signedResult = await this.createSignedTrade(tradePayload)
    if (!signedResult.success) return signedResult

    const result = await this.sendToL1('create_contract', {
      buyer_openid: buyerOpenid,
      seller_openid: sellerOpenid,
      item,
      amount,
      price,
      delivery_city: deliveryCity,
      buyer_signature: signedResult.data.buyer_signature
    })

    if (result.success) {
      this.journal.addLog('创建合约', { item, amount, price, deliveryCity })
    }
    return result
  }

  async cancelContract(contractId) {
    const result = await this.sendToL1('cancel_contract', {
      contract_id: contractId,
      openid: this.state.openid
    })
    if (result.success) {
      this.journal.addLog('合约取消', { contractId })
    }
    return result
  }

  async listContracts(status = null) {
    return await this.sendToL1('list_contracts', {
      openid: this.state.openid,
      status
    })
  }

  generateDailyReport() {
    return this.journal.generateDailyReport(this.state.gold, this.state.cargo, this.previousGold)
  }

  logAction(action, data = {}) {
    this.state.log.push({ timestamp: Date.now(), action, data })
    this.journal.addLog(action, data)
  }
}

module.exports = async function handler(input, context) {
  const { action, params, password } = input || {}
  const config = context.config || {}
  const captain = new CaptainLobsterSecure(config)

  switch (action) {
    case 'start':
    case 'initialize':
      return await captain.initialize(password)

    case 'status':
      return { success: true, data: captain.getStatus() }

    case 'city':
      return await captain.getCity(params?.city_id || 'canton')

    case 'buy':
      return await captain.tradeNpc(params?.item, params?.amount, 'buy')

    case 'sell':
      return await captain.tradeNpc(params?.item, params?.amount, 'sell')

    case 'move':
      return await captain.moveTo(params?.city)

    case 'arrive':
      return await captain.arrive()

    case 'intent':
      return await captain.updateIntent(params?.intent)

    case 'contract_create':
      return await captain.createContract(
        params?.buyer_openid, params?.seller_openid,
        params?.item, params?.amount, params?.price, params?.delivery_city
      )

    case 'contract_cancel':
      return await captain.cancelContract(params?.contract_id)

    case 'contracts':
      return await captain.listContracts(params?.status)

    case 'p2p_send':
      return await captain.sendP2PMessage(params?.peer_openid, params?.content)

    case 'inbox':
      return await captain.checkInbox()

    case 'report':
      return { success: true, message: captain.generateDailyReport() }

    case 'journal':
      return { success: true, data: { logs: captain.journal.getRecentLogs() } }

    case 'react':
      if (!captain.state.initialized) {
        return { success: false, message: '船长尚未觉醒' }
      }
      return { success: true, message: 'Re-Act 循环已触发' }

    case 'sign_trade':
      return await captain.createSignedTrade(params)

    case 'ping':
      return await captain.sendToL1('ping', {})

    default:
      return {
        success: false,
        message: `未知操作: ${action}。可用: start, status, city, buy, sell, move, arrive, intent, contract_create, contract_cancel, contracts, p2p_send, inbox, report, journal, sign_trade, ping`
      }
  }
}
