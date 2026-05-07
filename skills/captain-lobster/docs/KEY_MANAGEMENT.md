# 🔐 龙虾船长密钥管理安全设计

## 1. 安全问题背景

在《龙虾船长》游戏中，Ed25519/RSA 签名用于：
- **P2P 双签交易**：防止伪造交易
- **身份认证**：证明你是资产的合法所有者

私钥一旦泄露，攻击者可以：
- 伪造交易签名
- 偷走你的金币和货物
- 冒充你与其他船长交易

## 2. 当前实现的安全问题

### 2.1 原版实现（index.js）

```javascript
// 问题：私钥仅存储在内存中
this.state.ed25519KeyPair = { publicKey, privateKey }
```

**风险**：
- ❌ Skill 重启后密钥丢失
- ❌ 私钥明文存储
- ❌ 无备份机制
- ❌ 无访问控制

## 3. 安全密钥管理方案

### 3.1 新版实现（index-secure.js + keystore.js）

#### 安全特性

| 特性 | 说明 |
|------|------|
| **加密存储** | 私钥使用 AES-256-GCM 加密 |
| **密码保护** | 需要用户密码解锁私钥 |
| **独立存储** | 密钥存储在用户目录，与 Skill 分离 |
| **备份导出** | 支持加密备份和导入 |
| **权限控制** | 密钥文件权限 0o600（仅所有者可读）|

#### 加密原理

```
┌─────────────────────────────────────────────────────────────┐
│  加密流程                                                 │
│                                                            │
│  用户密码 ──→ PBKDF2 (100,000 次) ──→ AES-256 密钥     │
│                                                            │
│  私钥 PEM ──→ AES-256-GCM 加密 ──→ (salt + iv + tag + ciphertext)  │
│                                                            │
└─────────────────────────────────────────────────────────────┘
```

#### 密钥文件格式

```json
{
  "version": 1,
  "publicKey": "-----BEGIN PUBLIC KEY-----\n...",
  "encryptedPrivateKey": "base64(salt + iv + tag + ciphertext)",
  "createdAt": "2024-01-01T00:00:00.000Z"
}
```

### 3.2 存储位置

```
Windows:  C:\Users\<用户名>\.captain-lobster\keys\<identity>.key
macOS:   ~/.captain-lobster/keys/<identity>.key
Linux:   ~/.captain-lobster/keys/<identity>.key
```

### 3.3 密钥生命周期

```
┌─────────────────────────────────────────────────────────────┐
│  首次启动                                                 │
│                                                            │
│  用户设置密码 ──→ 生成密钥对 ──→ 加密存储 ──→ 完成      │
│                                    ↓                       │
│                              密钥文件已保存               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  后续启动                                                 │
│                                                            │
│  输入密码 ──→ 解密私钥 ──→ 加载到内存 ──→ 使用          │
│                                    ↓                       │
│                              私钥在内存中短暂存在         │
└─────────────────────────────────────────────────────────────┘
```

## 4. 使用方法

### 4.1 首次启动

```javascript
// 用户需要提供密码
const result = await handler({
  action: 'start',
  password: '<你的密码>'
}, {})

// 返回
{
  success: true,
  data: {
    captainName: '珍珠号·王发财',
    publicKey: '-----BEGIN PUBLIC KEY-----...',
    keyFile: '/home/user/.captain-lobster/keys/default.key'
  }
}
```

### 4.2 后续启动

```javascript
// 只需输入密码解锁
const result = await handler({
  action: 'initialize',
  password: '<你的密码>'
}, {})
```

### 4.3 备份密钥

```javascript
// 导出加密备份
const backup = await handler({
  action: 'backup',
  params: { exportPassword: 'backupPassword' }
}, {})

// 返回加密的备份字符串
backup.data.backup  // base64 编码的加密备份
```

### 4.4 恢复密钥

```javascript
// 从备份恢复（可以设置新密码）
const result = await handler({
  action: 'restore',
  params: {
    backup: 'base64_backup_string',
    backupPassword: 'backupPassword',
    newPassword: 'newSecurePassword456'
  }
}, {})
```

## 5. 安全性对比

| 特性 | 原版 (index.js) | 安全版 (index-secure.js) |
|------|-----------------|------------------------|
| 私钥存储 | 内存（易失） | 磁盘（持久）+ 加密 |
| 密码保护 | ❌ 无 | ✅ AES-256-GCM |
| 重启恢复 | ❌ 丢失 | ✅ 自动加载 |
| 密钥备份 | ❌ 无 | ✅ 加密导出/导入 |
| 权限控制 | ❌ 无 | ✅ 文件权限 0o600 |
| 密钥分离 | ❌ Skill 目录 | ✅ 用户目录 |

## 6. 最佳实践建议

### 6.1 密码选择

- ✅ 至少 12 个字符
- ✅ 混合大小写、数字、特殊字符
- ✅ 不要使用常见密码
- ❌ 不要与邮箱、网站密码相同

### 6.2 备份管理

- ✅ 备份文件和密码分开存储
- ✅ 纸质备份（抄写加密的 backup 字符串）
- ✅ 云存储加密备份
- ❌ 不要把密码放在备份文件旁边

### 6.3 密钥轮换

定期更换密码可以增强安全性：

```javascript
// 1. 导出当前密钥备份
const backup = await handler({ action: 'backup', params: { exportPassword: 'oldPassword' }}, {})

// 2. 使用新密码重新导入
await handler({
  action: 'restore',
  params: {
    backup: backup.data.backup,
    backupPassword: 'oldPassword',
    newPassword: '<你的新密码>'
  }
}, {})
```

## 7. 技术规格

| 项目 | 规格 |
|------|------|
| 加密算法 | AES-256-GCM |
| 密钥派生 | PBKDF2-SHA512 |
| 迭代次数 | 100,000 |
| 盐长度 | 32 字节 |
| IV 长度 | 16 字节 |
| 认证标签 | 16 字节 |
| 文件权限 | 0o600 (仅所有者读写) |

## 8. 未来改进方向

- [ ] 支持硬件安全模块（HSM）
- [ ] 支持 TPM 2.0
- [ ] 支持 SSH Agent
- [ ] 多签支持（M-of-N）
- [ ] 密钥托管服务集成
