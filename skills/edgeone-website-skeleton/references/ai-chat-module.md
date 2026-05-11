# AI Chat 模块参考文档

## 一、架构选择

**Edge Function 限制：**
- 200ms **CPU time** 限制（不是 wall clock time）
- `fetch()` 到外部 AI API 的 I/O 等待**不计入** CPU time
- **无 `waitUntil`**：异步写 KV 无法保证在响应发送前完成

**结论：** 流式 SSE 主力实现在 **Cloud Functions**，历史读取在 **Edge Functions**。

## 二、SSE 实现方案 B（Session ID 方案，推荐）

```
前端
  ↓ POST /api/ai/session（Edge，创建会话）
  ← 拿到 sessionId

  ↓ 建立 SSE 连接 /api/ai/chat-stream?sessionId=xxx（Cloud）
  ← 服务端从 KV 读取 history（不经过 URL）

Cloud SSE 流式响应
  ↓ 完成后异步写 KV（不阻塞响应）
```

> **安全说明：** 使用 sessionId 替代直接在 URL 中传输完整的对话历史。
> 对话历史仅服务端读取，避免通过浏览器历史、日志、代理或 referrer 泄露。

```javascript
// Edge Function: 创建 AI 会话
// edge-functions/api/ai/session.js
export async function onRequest(request, env) {
  const { userId } = await auth(request, env);
  const sessionId = crypto.randomUUID();
  await env.KV.put(`ai:session:${sessionId}:userId`, userId, { expirationTtl: 3600 });
  await env.KV.put(`ai:session:${sessionId}:history`, JSON.stringify([]), { expirationTtl: 3600 });
  return new Response(JSON.stringify({ sessionId }), {
    headers: { 'Content-Type': 'application/json' }
  });
}

// Cloud Function: chat-stream（服务端读取历史）
// cloud-functions/api/ai/chat-stream.js
export async function onRequest(request, env) {
  const { userId } = await auth(request, env);
  const url = new URL(request.url);

  if (request.method === 'POST') {
    // 用户发消息：追加到 KV
    const { sessionId, content } = await request.json();
    const historyKey = `ai:history:${sessionId}`;
    const history = JSON.parse(await env.KV.get(historyKey) || '[]');
    history.push({ role: 'user', content });
    await env.KV.put(historyKey, JSON.stringify(history), { expirationTtl: 3600 });
    return new Response(JSON.stringify({ ok: true }));
  }

  // GET: SSE 流式响应，从 KV 读取历史
  const sessionId = url.searchParams.get('sessionId');
  const historyKey = `ai:history:${sessionId}`;
  const existingHistory = JSON.parse(await env.KV.get(historyKey) || '[]');

  const stream = new ReadableStream({
    async start(controller) {
      const encoder = new TextEncoder();

      async function sendEvent(type, data) {
        controller.enqueue(encoder.encode(`event: ${type}\ndata: ${JSON.stringify(data)}\n\n`));
      }

      try {
        await sendEvent('status', { status: 'thinking' });

        const response = await fetch('https://api.example.com/chat', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${env.AI_API_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ messages: existingHistory, stream: true }),
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let assistantContent = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value);
          assistantContent += chunk;
          await sendEvent('message', { content: chunk });
        }

        // 追加 AI 回复到历史
        existingHistory.push({ role: 'assistant', content: assistantContent });
        await env.KV.put(historyKey, JSON.stringify(existingHistory), { expirationTtl: 3600 });

        await sendEvent('done', {});

      } catch (err) {
        await sendEvent('error', { message: err.message });
      } finally {
        controller.close();
      }
    }
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    }
  });
}
```

## 三、前端 SSE 客户端

```javascript
// client/src/services/ai.js
import { EventBus } from '../utils/event-bus.js';

class AIService {
  constructor() {
    this.es = null;
    this.sessionId = null;
  }

  async startChatSession() {
    // Step 1: 创建会话，获取 sessionId
    const sessionRes = await fetch('/api/ai/session', { method: 'POST' }).then(r => r.json());
    this.sessionId = sessionRes.sessionId;

    // Step 2: 建立 SSE，传 sessionId（不传完整历史）
    this.es = new EventSource(`/api/ai/chat-stream?sessionId=${this.sessionId}`);

    this.es.addEventListener('message', (e) => {
      const data = JSON.parse(e.data);
      EventBus.emit('ai:message', { role: 'assistant', content: data.content });
    });

    this.es.addEventListener('status', (e) => {
      EventBus.emit('ai:status', JSON.parse(e.data));
    });

    this.es.addEventListener('done', () => {
      EventBus.emit('ai:status', { status: 'idle' });
    });

    this.es.addEventListener('error', (e) => {
      EventBus.emit('ai:error', { message: 'SSE 连接断开' });
    });
  }

  sendMessage(content) {
    EventBus.emit('ai:message', { role: 'user', content });
    return fetch('/api/ai/chat-stream', {
      method: 'POST',
      body: JSON.stringify({ sessionId: this.sessionId, content }),
      credentials: 'include'
    });
  }
}
```

## 四、AI 限流

```javascript
// Edge Middleware 或独立限流函数
async function aiRateLimit(request, env, userId, ip) {
  const key = userId ? `ai:user:${userId}` : `ai:ip:${ip}`;
  const limit = userId ? 60 : 10;  // 已登录 60次/分钟，未登录 10次/分钟
  const window = 60;

  const count = parseInt(await env.KV.get(`rl:${key}:${Math.floor(Date.now() / 60000)}`) || '0');
  if (count >= limit) {
    return { allowed: false, remaining: 0 };
  }
  await env.KV.put(`rl:${key}:${Math.floor(Date.now() / 60000)}`, String(count + 1), { expirationTtl: 65 });
  return { allowed: true, remaining: limit - count - 1 };
}
```

## 五、AI Widget（嵌入代码）

```javascript
// 注册为 Custom Element，完全自包含，不依赖 SPA 状态
class AIChatWidget extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    this.shadowRoot.innerHTML = `
      <style>
        :host { position: fixed; bottom: 20px; right: 20px; z-index: 9999; }
        .widget { width: 360px; height: 520px; border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.15); }
      </style>
      <div class="widget"><!-- 渲染逻辑 --></div>
    `;
  }
}
customElements.define('ai-chat-widget', AIChatWidget);
```
