/**
 * @file keystore.js
 * @description 安全的密钥存储管理模块
 *
 * 安全性设计：
 * 1. 私钥使用用户密码加密存储（AES-256-GCM）
 * 2. 密钥文件存储在用户目录下，与 Skill 目录分离
 * 3. 支持密钥导出（加密）和导入
 * 4. 支持 RSA 签名与验签（用于 P2P 交易防抵赖）
 */

const crypto = require('crypto')
const fs = require('fs')
const path = require('path')
const os = require('os')

class KeyStore {
  constructor(options = {}) {
    this.keyDir = options.keyDir || path.join(os.homedir(), '.captain-lobster', 'keys')
    this.algorithm = 'aes-256-gcm'
    this.keyLength = 32
    this.ivLength = 16
    this.authTagLength = 16
    this.saltLength = 32
    this.signAlgorithm = 'RSA-SHA256'
  }

  getKeyFilePath(identity = 'default') {
    return path.join(this.keyDir, `${identity}.key`)
  }

  ensureKeyDir() {
    if (!fs.existsSync(this.keyDir)) {
      fs.mkdirSync(this.keyDir, { recursive: true, mode: 0o700 })
    }
  }

  generateKeyPair() {
    return crypto.generateKeyPairSync('rsa', {
      modulusLength: 2048,
      publicKeyEncoding: { type: 'spki', format: 'pem' },
      privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
    })
  }

  deriveKey(password, salt) {
    return crypto.pbkdf2Sync(password, salt, 100000, this.keyLength, 'sha512')
  }

  /**
   * 异步派生密钥（不阻塞事件循环）
   */
  deriveKeyAsync(password, salt) {
    return new Promise((resolve, reject) => {
      crypto.pbkdf2(password, salt, 100000, this.keyLength, 'sha512', (err, key) => {
        if (err) reject(err)
        else resolve(key)
      })
    })
  }

  encryptPrivateKey(privateKey, password) {
    const salt = crypto.randomBytes(this.saltLength)
    const key = this.deriveKey(password, salt)
    const iv = crypto.randomBytes(this.ivLength)

    const cipher = crypto.createCipheriv(this.algorithm, key, iv)
    const encrypted = Buffer.concat([
      cipher.update(privateKey, 'utf8'),
      cipher.final()
    ])
    const authTag = cipher.getAuthTag()

    return Buffer.concat([salt, iv, authTag, encrypted]).toString('base64')
  }

  decryptPrivateKey(encryptedData, password) {
    const buffer = Buffer.from(encryptedData, 'base64')

    const salt = buffer.subarray(0, this.saltLength)
    const iv = buffer.subarray(this.saltLength, this.saltLength + this.ivLength)
    const authTag = buffer.subarray(
      this.saltLength + this.ivLength,
      this.saltLength + this.ivLength + this.authTagLength
    )
    const encrypted = buffer.subarray(
      this.saltLength + this.ivLength + this.authTagLength
    )

    const key = this.deriveKey(password, salt)
    const decipher = crypto.createDecipheriv(this.algorithm, key, iv)
    decipher.setAuthTag(authTag)

    return Buffer.concat([
      decipher.update(encrypted),
      decipher.final()
    ]).toString('utf8')
  }

  saveKeyPair(identity, password, keyPair = null) {
    this.ensureKeyDir()

    if (!keyPair) {
      keyPair = this.generateKeyPair()
    }

    if (!password || password.length < 8) {
      throw new Error('密码长度至少需要 8 个字符')
    }

    const encryptedPrivateKey = this.encryptPrivateKey(keyPair.privateKey, password)

    const keyStore = {
      version: 1,
      publicKey: keyPair.publicKey,
      encryptedPrivateKey,
      createdAt: new Date().toISOString()
    }

    const keyFile = this.getKeyFilePath(identity)
    fs.writeFileSync(keyFile, JSON.stringify(keyStore, null, 2), { mode: 0o600 })

    return keyPair.publicKey
  }

  loadKeyPair(identity, password) {
    const keyFile = this.getKeyFilePath(identity)

    if (!fs.existsSync(keyFile)) {
      return null
    }

    const ks = JSON.parse(fs.readFileSync(keyFile, 'utf8'))
    const dk = this.decryptPrivateKey(ks.encryptedPrivateKey, password)
    const pub = ks.publicKey
    return { publicKey: pub, privateKey: dk }
  }

  hasKeyPair(identity = 'default') {
    return fs.existsSync(this.getKeyFilePath(identity))
  }

  deleteKeyPair(identity = 'default') {
    const keyFile = this.getKeyFilePath(identity)
    if (fs.existsSync(keyFile)) {
      fs.unlinkSync(keyFile)
    }
  }

  sign(privateKey, data) {
    const dataStr = typeof data === 'string' ? data : JSON.stringify(data)
    const sign = crypto.createSign(this.signAlgorithm)
    sign.update(dataStr)
    sign.end()
    return sign.sign(privateKey, 'base64')
  }

  verify(publicKey, data, signature) {
    const dataStr = typeof data === 'string' ? data : JSON.stringify(data)
    const verify = crypto.createVerify(this.signAlgorithm)
    verify.update(dataStr)
    verify.end()
    return verify.verify(publicKey, signature, 'base64')
  }

  signTrade(privateKey, tradePayload) {
    const canonicalPayload = JSON.stringify({
      buyer_openid: tradePayload.buyer_openid,
      seller_openid: tradePayload.seller_openid,
      item: tradePayload.item,
      amount: tradePayload.amount,
      total_price: tradePayload.total_price,
      delivery_city: tradePayload.delivery_city
    })
    return this.sign(privateKey, canonicalPayload)
  }

  verifyTradeSignature(publicKey, tradePayload, signature) {
    const canonicalPayload = JSON.stringify({
      buyer_openid: tradePayload.buyer_openid,
      seller_openid: tradePayload.seller_openid,
      item: tradePayload.item,
      amount: tradePayload.amount,
      total_price: tradePayload.total_price,
      delivery_city: tradePayload.delivery_city
    })
    return this.verify(publicKey, canonicalPayload, signature)
  }

  stripPemHeader(pemKey) {
    return pemKey
      .replace(/-----BEGIN [A-Z ]+-----/g, '')
      .replace(/-----END [A-Z ]+-----/g, '')
      .replace(/\s/g, '')
      .trim()
  }

  restorePemPublicKey(base64Key) {
    const lines = base64Key.match(/.{1,64}/g) || []
    return `-----BEGIN PUBLIC KEY-----\n${lines.join('\n')}\n-----END PUBLIC KEY-----`
  }

  exportBackup(identity = 'default', exportPassword) {
    const keyFile = this.getKeyFilePath(identity)
    if (!fs.existsSync(keyFile)) {
      throw new Error('密钥文件不存在')
    }

    const keyStore = JSON.parse(fs.readFileSync(keyFile, 'utf8'))

    const exportData = {
      version: 1,
      identity,
      publicKey: keyStore.publicKey,
      createdAt: keyStore.createdAt,
      backupAt: new Date().toISOString(),
      encryptedBackup: this.encryptPrivateKey(
        JSON.stringify({ publicKey: keyStore.publicKey, encryptedPrivateKey: keyStore.encryptedPrivateKey }),
        exportPassword
      )
    }

    return Buffer.from(JSON.stringify(exportData)).toString('base64')
  }

  importBackup(encryptedBackup, backupPassword, newPassword) {
    const backupData = JSON.parse(Buffer.from(encryptedBackup, 'base64').toString('utf8'))

    // 解密备份内层，拿到原始 keyStore（含 encryptedPrivateKey 和 publicKey）
    const innerJson = this.decryptPrivateKey(backupData.encryptedBackup, backupPassword)
    const decrypted = JSON.parse(innerJson)

    // 解密私钥
    const decryptedKey = this.decryptPrivateKey(decrypted.encryptedPrivateKey, backupPassword)
    const effectivePassword = newPassword || backupPassword

    this.ensureKeyDir()
    const keyStore = {
      version: 1,
      publicKey: decrypted.publicKey,
      encryptedPrivateKey: this.encryptPrivateKey(decryptedKey, effectivePassword),
      createdAt: backupData.createdAt || new Date().toISOString()
    }

    const keyFile = this.getKeyFilePath(backupData.identity || 'default')
    fs.writeFileSync(keyFile, JSON.stringify(keyStore, null, 2), { mode: 0o600 })

    return decrypted.publicKey
  }

  getPublicKey(identity = 'default') {
    const keyFile = this.getKeyFilePath(identity)
    if (!fs.existsSync(keyFile)) {
      return null
    }

    const keyStore = JSON.parse(fs.readFileSync(keyFile, 'utf8'))
    return keyStore.publicKey
  }
}

module.exports = KeyStore
