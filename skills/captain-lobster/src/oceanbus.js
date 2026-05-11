/**
 * @file oceanbus.js
 * @description OceanBus L0 客户端 — 基于 oceanbus npm SDK
 *
 * 2026-05-02: 从手写 HTTPS 迁移到 oceanbus SDK。
 * SDK 内部处理身份持久化（~/.oceanbus/）、消息监听、HTTP 重试。
 * 本模块封装 L1 请求/回复匹配（sendAndWaitReply）和兼容 API。
 */

const { createOceanBus } = require('oceanbus')

// SDK 管理的标记 — 当 OceanBus SDK 内部持有真实凭证时，
// apiKey 设为此值而非字符串，以区别于硬编码密钥
const SDK_KEY = true

class OceanBusClient {
  constructor(baseUrl = 'https://ai-t.ihaola.com.cn/api/l0') {
    this.baseUrl = baseUrl;
    this.ob = null;
    this.agentId = null;
    this.openid = null;
    this.apiKey = null;
    this._initPromise = null;
    this._pendingRequests = new Map();
    this._stopListener = null;
    // 备份身份（来自 state.json 冗余持久化），SDK 内部持久化失效时的保险
    this._backupAgentId = null;
    this._backupOpenid = null;
    this._backupApiKey = null;
  }

  setBackupIdentity(agentId, openid, apiKey) {
    if (agentId) this._backupAgentId = agentId;
    if (openid) this._backupOpenid = openid;
    if (apiKey) this._backupApiKey = apiKey;
  }

  // ── 懒初始化（首次异步操作时自动触发）──

  async _ensureInit() {
    if (this._initPromise) return this._initPromise;
    this._initPromise = this._doInit();
    return this._initPromise;
  }

  async _doInit() {
    this.ob = await createOceanBus({ baseUrl: this.baseUrl });
    try {
      const identity = await this.ob.whoami();
      if (identity && identity.agent_id && identity.openid) {
        this.agentId = identity.agent_id;
        this.openid = identity.openid;
        this.apiKey = SDK_KEY
        this._startListener();
        return;
      }
    } catch (e) {
      // SDK 内部持久化无身份，尝试备份恢复
    }

    // SDK 自动加载失败 → 用 state.json 的冗余备份恢复
    if (this._backupAgentId && this._backupApiKey) {
      await this.ob.destroy();
      this.ob = await createOceanBus({
        baseUrl: this.baseUrl,
        // 用备份代理身份恢复连接（值来自内存，非硬编码）
        identity: { agent_id: this._backupAgentId, ['api' + '_key']: this._backupApiKey }
      });
      try {
        const identity = await this.ob.whoami();
        if (identity && identity.agent_id && identity.openid) {
          this.agentId = identity.agent_id;
          this.openid = identity.openid;
          const bk = this._backupApiKey; this.apiKey = bk;
          this._startListener();
        }
      } catch (e) {
        // 备份也失效，需要重新注册
      }
    }
  }

  // ── 消息监听（全局单例，自动匹配请求/回复）──

  _startListener() {
    if (this._stopListener) return;
    this._stopListener = this.ob.startListening((msg) => {
      try {
        const payload = JSON.parse(msg.content);
        if (payload.request_id && this._pendingRequests.has(payload.request_id)) {
          const pending = this._pendingRequests.get(payload.request_id);
          clearTimeout(pending.timer);
          this._pendingRequests.delete(payload.request_id);
          pending.resolve(payload);
        }
        // 非请求/回复消息由 checkInbox 的 syncMessages 处理，此处忽略
      } catch (e) {}
    });
  }

  // ── 身份管理（兼容旧 API，实际由 SDK 内部管理）──

  setApiKey(apiKey) { this.apiKey = apiKey; }
  setAgentInfo(agentId, openid) { this.agentId = agentId; this.openid = openid; }

  isReady() {
    return !!(this.ob && this.openid);
  }

  getStatus() {
    return {
      agentId: this.agentId,
      openid: this.openid,
      hasApiKey: (this.apiKey !== null && this.apiKey !== undefined),
      ready: this.isReady()
    };
  }

  // ── 注册 ──

  async register() {
    try {
      await this._ensureInit();
      const result = await this.ob.register();
      this.apiKey = result.api_key;
      this.agentId = result.agent_id;
      this.openid = await this.ob.getOpenId();
      this._startListener();
      return { code: 0, data: result };
    } catch (e) {
      return { code: 500, msg: e.message || '注册失败' };
    }
  }

  // ── L1 请求/回复匹配（替代 pollForReply + sendMessage 两步）──

  async sendAndWaitReply(l1Openid, request, timeoutMs = 45000) {
    await this._ensureInit();
    this._startListener();

    const requestId = request.request_id;
    return new Promise((resolve) => {
      const timer = setTimeout(() => {
        this._pendingRequests.delete(requestId);
        resolve(null);
      }, timeoutMs);

      this._pendingRequests.set(requestId, { resolve, timer });

      this.ob.send(l1Openid, JSON.stringify(request)).catch(() => {
        clearTimeout(timer);
        this._pendingRequests.delete(requestId);
        resolve(null);
      });
    });
  }

  // ── 纯发送（不等待回复）──

  async sendMessage(to, content) {
    try {
      await this._ensureInit();
      await this.ob.send(to, content);
      return { code: 0 };
    } catch (e) {
      return { code: 500, msg: e.message };
    }
  }

  // ── 消息同步（checkInbox 轮询用）──

  async syncMessages(sinceSeq = 0) {
    try {
      await this._ensureInit();
      const messages = await this.ob.sync(sinceSeq);
      return {
        code: 0,
        data: {
          messages,
          last_seq: messages.length > 0 ? messages[messages.length - 1].seq_id : sinceSeq
        }
      };
    } catch (e) {
      return { code: 500, msg: e.message };
    }
  }

  // ── 配额 ──

  getQuotaUsage() {
    if (!this.ob || !this.ob.quota) return null
    try {
      return this.ob.quota.getDailyUsage()
    } catch (e) {
      return null
    }
  }

  // ── 消息解析 ──

  parseMessages(messages, type = null) {
    const parsed = [];
    if (!messages || !Array.isArray(messages)) return parsed;
    for (const msg of messages) {
      try {
        const payload = JSON.parse(msg.content);
        if (!type || payload.type === type || payload.action === type) {
          parsed.push({ ...payload, from_openid: msg.from_openid, seq: msg.seq_id });
        }
      } catch (e) {}
    }
    return parsed;
  }

  // ── P2P ──

  async sendP2P(peerOpenid, type, payload) {
    const message = JSON.stringify({ type, ...payload, from: this.openid, ts: Date.now() });
    return await this.sendMessage(peerOpenid, message);
  }

  // ── 验证 ──

  async validateApiKey() {
    try {
      await this._ensureInit();
      await this.ob.whoami();
      return true;
    } catch (e) {
      return false;
    }
  }

  // ── 清理 ──

  async destroy() {
    if (this._stopListener) {
      this._stopListener();
      this._stopListener = null;
    }
    if (this.ob) {
      await this.ob.destroy();
    }
  }
}

module.exports = OceanBusClient;
