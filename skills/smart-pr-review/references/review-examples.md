# 高质量 Review 评论范例

作为 few-shot 示例，帮助 AI 生成高质量、有立场的 review 评论。

---

## 范例 1: 发现严重安全问题的 PR

```markdown
## 🔍 Code Review: PR #247 — Add user search API endpoint

### Summary
新增用户搜索 API，支持按名称和邮箱模糊查询。**整体方案有安全风险**：搜索接口未做鉴权，且存在 SQL 注入漏洞。必须修复后才能合并。

---

### 🚨 MUST FIX (2 issues)

**[MF-1] SQL 注入漏洞**
📍 `src/routes/users.ts:45`
```typescript
const results = await db.query(
  `SELECT * FROM users WHERE name LIKE '%${req.query.q}%'`
);
```
**问题**: 直接将用户输入拼接到 SQL 语句中，攻击者可以通过构造 `q=%'; DROP TABLE users; --` 删除整张表。
**影响**: 数据库被任意读取或破坏，属于 P0 级安全漏洞。
**建议修复**:
```typescript
const results = await db.query(
  "SELECT id, name, email FROM users WHERE name LIKE $1",
  [`%${req.query.q}%`]
);
```

**[MF-2] 搜索接口未鉴权**
📍 `src/routes/users.ts:38`
```typescript
router.get("/api/users/search", async (req, res) => {
```
**问题**: 该端点未使用 `authMiddleware`，任何人都可以搜索用户信息（包括邮箱）。
**影响**: 用户隐私泄露，可能违反 GDPR。
**建议修复**:
```typescript
router.get("/api/users/search", authMiddleware, async (req, res) => {
```

---

### ⚠️ SHOULD FIX (2 issues)

**[SF-1] 返回了不必要的用户字段**
📍 `src/routes/users.ts:45`
**问题**: `SELECT *` 返回了所有字段，包括 `password_hash`、`reset_token` 等敏感信息。
**建议**: 明确列出需要返回的字段 `SELECT id, name, email, avatar_url FROM users`

**[SF-2] 缺少分页，大数据量下会 OOM**
📍 `src/routes/users.ts:45-48`
**问题**: 搜索结果没有 LIMIT，如果匹配用户过多会返回全量数据。
**建议**: 添加分页参数 `LIMIT $2 OFFSET $3`，默认返回 20 条。

---

### 💡 SUGGESTION (1 issue)

**[SG-1] 搜索关键词建议做最小长度限制**
📍 `src/routes/users.ts:40`
**建议**: 添加 `if (q.length < 2) return res.status(400)...`，防止单字符搜索导致过多结果。

---

### ✅ What's Good
- 路由组织清晰，遵循了项目现有的 `src/routes/` 模式
- 使用了 async/await 而非回调，代码可读性好

---

### 📊 Verdict

**[x] REQUEST CHANGES** — Must fix critical issues

> 存在 SQL 注入漏洞和鉴权缺失两个 P0 级安全问题，必须修复后才能合并。
```

---

## 范例 2: 性能问题的 PR

```markdown
## 🔍 Code Review: PR #389 — 订单列表页添加用户信息展示

### Summary
在订单列表页展示每个订单的下单用户信息。功能正确，但存在典型的 N+1 查询问题，在订单量大时会严重影响性能。

---

### 🚨 MUST FIX (1 issue)

**[MF-1] N+1 查询：循环中逐个查询用户信息**
📍 `src/services/orderService.ts:67-72`
```typescript
const orders = await Order.findAll({ where: { status: "active" } });
for (const order of orders) {
  order.user = await User.findByPk(order.userId);
}
```
**问题**: 如果有 1000 个订单，就会发起 1001 次数据库查询（1 次查订单 + 1000 次查用户）。数据库连接池会被耗尽，页面加载时间可能超过 10 秒。
**影响**: 生产环境订单量超过 100 后，页面响应时间线性增长，超过 500 时基本不可用。
**建议修复**:
```typescript
const orders = await Order.findAll({
  where: { status: "active" },
  include: [{ model: User, attributes: ["id", "name", "avatar"] }],
});
// 或手动批量查询
const orders = await Order.findAll({ where: { status: "active" } });
const userIds = [...new Set(orders.map(o => o.userId))];
const users = await User.findAll({ where: { id: userIds } });
const userMap = new Map(users.map(u => [u.id, u]));
for (const order of orders) {
  order.user = userMap.get(order.userId);
}
```

---

### ⚠️ SHOULD FIX (1 issue)

**[SF-1] 缺少分页**
📍 `src/controllers/orderController.ts:23`
**问题**: 一次性加载所有 active 订单，数据量大时内存占用过高。
**建议**: 添加 `page` 和 `pageSize` 参数，默认每页 20 条。

---

### 💡 SUGGESTION (1 issue)

**[SG-1] User 信息可以考虑缓存**
📍 `src/services/orderService.ts`
**建议**: 用户基本信息变更频率低，可以用 Redis 缓存，TTL 设 5 分钟，减少数据库压力。

---

### ✅ What's Good
- 正确使用了 TypeScript 类型，订单和用户类型定义清晰
- 前端展示组件的 props 设计合理，解耦了数据获取和渲染

---

### 📊 Verdict

**[x] REQUEST CHANGES** — Must fix critical issues

> N+1 查询在生产环境会导致严重性能问题，建议使用 JOIN 查询或批量查询修复后再合并。
```

---

## 范例 3: 整体方向有问题的 PR

```markdown
## 🔍 Code Review: PR #512 — 自定义 JWT 实现替换 jsonwebtoken 库

### Summary
用自定义代码替换了 `jsonwebtoken` 库的 JWT 签名和验证逻辑。**这个 PR 的方向有问题** — 自行实现加密相关功能是安全反模式，强烈建议继续使用经过审计的第三方库。

> ⚠️ **方向性问题**：密码学相关的功能不应自行实现。`jsonwebtoken` 是经过广泛使用和安全审计的库，自定义实现很可能引入漏洞。如果是因为性能原因，建议评估 `jose` 库作为替代。

---

### 🚨 MUST FIX (3 issues)

**[MF-1] 不应自行实现 JWT**
📍 `src/utils/jwt.ts:1-120`（整个文件）
**问题**: 自行实现的 JWT 缺少：时序安全的签名比较、算法混淆攻击防护、JWK 轮换支持。这些都是已知攻击向量，第三方库已经处理了。
**影响**: 认证系统被绕过，任何人可以伪造 token。
**建议**: 撤回此 PR，继续使用 `jsonwebtoken`。如需更好的性能，迁移到 `jose` 库。

**[MF-2] 签名比较不是时序安全的**
📍 `src/utils/jwt.ts:87`
```typescript
if (computedSignature === providedSignature) {
```
**问题**: 字符串 `===` 比较会泄露签名长度信息（时序攻击）。
**建议修复**:
```typescript
import { timingSafeEqual } from "crypto";
if (timingSafeEqual(Buffer.from(computedSignature), Buffer.from(providedSignature))) {
```

**[MF-3] 未校验 JWT header 中的 alg 字段**
📍 `src/utils/jwt.ts:34-40`
**问题**: 未验证 `alg` 字段，攻击者可以将 `alg` 设为 `none` 绕过签名验证。

---

### 📊 Verdict

**[x] REQUEST CHANGES** — Must fix critical issues

> 强烈建议关闭此 PR。自行实现密码学功能违反安全最佳实践。如果对现有库有具体的性能或功能需求，请先开 issue 讨论替代方案。
```

---

## 范例 4: 代码质量良好的 PR（APPROVE）

```markdown
## 🔍 Code Review: PR #601 — 重构通知服务，支持多渠道发送

### Summary
将通知发送逻辑从硬编码的邮件发送重构为策略模式，支持邮件、Slack、Webhook 三种渠道。重构设计合理，测试覆盖充分。

---

### 🚨 MUST FIX (0 issues)

无

---

### ⚠️ SHOULD FIX (1 issue)

**[SF-1] 缺少渠道发送失败的降级策略**
📍 `src/services/notification/notifier.ts:45`
**问题**: 如果 Slack API 暂时不可用，通知直接丢失。建议添加重试队列或降级到其他渠道。
**建议**: 考虑使用 Bull/BullMQ 添加重试机制，或实现 fallback 链（Slack → Email → 日志）。

---

### 💡 SUGGESTION (2 issues)

**[SG-1] NotificationChannel 接口可以加 `isAvailable()` 方法**
📍 `src/services/notification/types.ts:8`
**建议**: 添加健康检查方法，在发送前检测渠道是否可用，避免无效请求。

**[SG-2] 测试中的 mock 可以使用 `satisfies` 增强类型安全**
📍 `src/services/notification/__tests__/notifier.test.ts:15`
**建议**: `const mockChannel = { send: vi.fn() } satisfies NotificationChannel;`

---

### ✅ What's Good
- 策略模式的应用恰到好处，没有过度设计
- 每个渠道实现都有独立的单元测试，覆盖了成功和失败场景
- `NotificationChannel` 接口简洁（只有 `send` 方法），符合接口隔离原则
- 渠道注册使用了 Map 而非 switch-case，易于扩展
- 类型定义完整，没有 `any`

---

### 📊 Verdict

**[x] APPROVE** — Ready to merge

> 重构设计合理，代码质量高。SF-1 的降级策略建议可以作为后续迭代处理，不阻塞合并。
```

---

## 写好 Review 评论的原则

1. **先说结论**：Summary 里一句话说清楚是否可以合并
2. **问题要具体**：引用文件名、行号、代码片段
3. **给方案不给废话**：每个 MUST FIX 都附带可执行的代码
4. **严重程度要准确**：安全漏洞是 MUST FIX，不是 SUGGESTION
5. **也要肯定好的部分**：好的 review 不只找问题
6. **方向性问题开头就说**：不要把"这个 PR 不应该存在"藏在最后
