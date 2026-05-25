# Hannah & Elena API Testing Guide

Complete guide for testing and integrating with Hannah and Elena APIs.

## Table of Contents

1. [API Endpoints](#api-endpoints)
2. [Authentication](#authentication)
3. [Basic Request Examples](#basic-request-examples)
4. [Advanced Usage](#advanced-usage)
5. [Streaming Responses](#streaming-responses)
6. [Error Handling](#error-handling)
7. [Troubleshooting](#troubleshooting)

---

## API Endpoints

### Hannah (Marketing Research Specialist)

- **Base URL**: `https://hannah.sumike.ai`
- **List Coworkers**: `GET https://hannah.sumike.ai/v1/coworkers`
- **Create Task**: `POST https://hannah.sumike.ai/v1/tasks`
- **Check Task**: `GET https://hannah.sumike.ai/v1/tasks/{taskId}`
- **Get Result**: `GET https://hannah.sumike.ai/v1/tasks/{taskId}/result`
- **Protocol**: Task-based REST API

### Elena (Operations & Project Orchestrator)

- **Base URL**: `https://elena.sumike.ai`
- **List Coworkers**: `GET https://elena.sumike.ai/v1/coworkers`
- **Create Task**: `POST https://elena.sumike.ai/v1/tasks`
- **Check Task**: `GET https://elena.sumike.ai/v1/tasks/{taskId}`
- **Get Result**: `GET https://elena.sumike.ai/v1/tasks/{taskId}/result`
- **Protocol**: Task-based REST API

---

## Authentication

### API Key Format

Both Hannah and Elena use the same authentication format:

```
Authorization: Bearer sk-sumike-xxxxx
```

**Important:**
- API keys start with `sk-sumike-`
- Keys are scoped to specific agents (Hannah or Elena)
- Maximum 5 active keys per contact
- Keys should be rotated every 90 days

### Getting Your API Key

**Human must do this:**
1. Contact Serviceplan at sumike.ai
2. Request access to Hannah and/or Elena
3. Receive API key via secure channel

---

## Basic Request Examples

### 1. List Available Coworkers

```bash
curl -X GET https://hannah.sumike.ai/v1/coworkers \
  -H "Authorization: Bearer sk-sumike-your-key-here"
```

**Response:**
```json
{
  "data": [
    {
      "id": "cow_hannah",
      "name": "Hannah Sumi",
      "role": "Marketing Research Specialist",
      "email": "hannah@sumike.ai",
      "status": "AVAILABLE"
    },
    {
      "id": "cow_elena",
      "name": "Elena",
      "role": "Operations & Project Orchestrator",
      "email": "elena@sumike.ai",
      "status": "AVAILABLE"
    }
  ],
  "meta": {
    "timestamp": "2026-02-12T10:00:00.000Z",
    "requestId": "req_abc123"
  }
}
```

### 2. Create Research Task (Hannah)

```bash
curl -X POST https://hannah.sumike.ai/v1/tasks \
  -H "Authorization: Bearer sk-sumike-your-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "German EV Market Research",
    "description": "What are the top 3 trends in the German EV market for 2026? Include market data, consumer sentiment, and competitive landscape.",
    "coworkerId": "cow_hannah",
    "status": "READY"
  }'
```

**Response:**
```json
{
  "data": {
    "id": "task_xyz789",
    "name": "German EV Market Research",
    "status": "READY",
    "coworkerId": "cow_hannah",
    "createdAt": "2026-02-12T10:00:00.000Z"
  },
  "meta": {
    "timestamp": "2026-02-12T10:00:00.000Z",
    "requestId": "req_xyz123"
  }
}
```

**⏱️ IMPORTANT: Wait 2-3 minutes before checking status!**

### 3. Check Task Status

```bash
# Wait 2-3 minutes first!
curl -X GET https://hannah.sumike.ai/v1/tasks/task_xyz789 \
  -H "Authorization: Bearer sk-sumike-your-key-here"
```

**Response (In Progress):**
```json
{
  "data": {
    "id": "task_xyz789",
    "name": "German EV Market Research",
    "status": "IN_PROGRESS",
    "coworkerId": "cow_hannah",
    "createdAt": "2026-02-12T10:00:00.000Z",
    "updatedAt": "2026-02-12T10:01:30.000Z"
  }
}
```

**⏱️ If IN_PROGRESS: Wait another 2-3 minutes, then check again**

**Response (Completed):**
```json
{
  "data": {
    "id": "task_xyz789",
    "name": "German EV Market Research",
    "status": "COMPLETED",
    "coworkerId": "cow_hannah",
    "createdAt": "2026-02-12T10:00:00.000Z",
    "completedAt": "2026-02-12T10:05:23.000Z"
  }
}
```

### 4. Get Task Result

```bash
# Only after status is COMPLETED
curl -X GET https://hannah.sumike.ai/v1/tasks/task_xyz789/result \
  -H "Authorization: Bearer sk-sumike-your-key-here"
```

**Response:**
```json
{
  "data": {
    "result": "# German EV Market Research\n\n## Top 3 Trends for 2026\n\n1. **Increased adoption...**\n2. **Infrastructure expansion...**\n3. **Price parity trends...\n\n## Sources\n- Statista: German Automotive Market 2025\n- GWI: Consumer EV Sentiment Q4 2025\n\n## Confidence Level: High",
    "deliverables": [
      {
        "type": "pdf",
        "url": "https://hannah.sumike.ai/files/task_xyz789/research-report.pdf"
      },
      {
        "type": "xlsx",
        "url": "https://hannah.sumike.ai/files/task_xyz789/market-data.xlsx"
      }
    ]
  }
}
```

### 5. Create Planning Task (Elena)

```bash
curl -X POST https://elena.sumike.ai/v1/tasks \
  -H "Authorization: Bearer sk-sumike-your-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Q2 Campaign Launch Planning",
    "description": "Break down a 6-week product launch campaign into workstreams with dependencies. Product: Premium EV. Budget: €500k.",
    "coworkerId": "cow_elena",
    "status": "READY"
  }'
```

**⏱️ IMPORTANT: Elena may delegate to Hannah for market research. Total time: 5-10 minutes.**

---

## Advanced Usage

### Multi-Turn Conversation

Maintain conversation context across multiple requests:

```bash
# First message
curl -X POST https://hannah.sumike.ai/v1/chat/completions \
  -H "Authorization: Bearer sk-sumike-your-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "What is the current German EV market size?"
      }
    ]
  }'

# Follow-up message (include previous context)
curl -X POST https://hannah.sumike.ai/v1/chat/completions \
  -H "Authorization: Bearer sk-sumike-your-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "What is the current German EV market size?"
      },
      {
        "role": "assistant",
        "content": "The German EV market is currently valued at..."
      },
      {
        "role": "user",
        "content": "What are the key growth drivers?"
      }
    ]
  }'
```

### Deep Research Request

Specify research depth and data sources:

```bash
curl -X POST https://hannah.sumike.ai/v1/chat/completions \
  -H "Authorization: Bearer sk-sumike-your-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "I need comprehensive research on German EV market:\n- Market size and growth (Statista)\n- Consumer sentiment (GWI)\n- Competitive landscape (DataForSEO)\n- Social media trends (Apify)\n\nDepth: Deep research with source attribution"
      }
    ],
    "stream": false
  }'
```

### Elena with Market Context

Elena automatically delegates to Hannah when needed:

```bash
curl -X POST https://elena.sumike.ai/v1/chat/completions \
  -H "Authorization: Bearer sk-sumike-your-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Create project plan for German EV campaign:\n- Product: Premium sedan\n- Launch: April 1, 2026\n- Target: Affluent professionals 35-55\n- Budget: €500k\n\nI need work breakdown, dependencies, and risk assessment."
      }
    ],
    "stream": false
  }'
```

**Note:** Elena will detect missing market context and delegate to Hannah automatically. Response time: 5-10 minutes due to sub-agent orchestration.

---

## Streaming Responses

Get real-time progress updates:

```bash
curl -X POST https://hannah.sumike.ai/v1/chat/completions \
  -H "Authorization: Bearer sk-sumike-your-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Research the German EV market"
      }
    ],
    "stream": true
  }'
```

**Streaming Response Format:**

```
data: {"id":"msg_abc","object":"chat.completion.chunk","created":1676543210,"model":"hannah","choices":[{"index":0,"delta":{"role":"assistant"},"finish_reason":null}]}

data: {"id":"msg_abc","object":"chat.completion.chunk","created":1676543210,"model":"hannah","choices":[{"index":0,"delta":{"content":"Let me"},"finish_reason":null}]}

data: {"id":"msg_abc","object":"chat.completion.chunk","created":1676543210,"model":"hannah","choices":[{"index":0,"delta":{"content":" research"},"finish_reason":null}]}

...

data: [DONE]
```

### Processing Streaming Response in JavaScript

```javascript
const response = await fetch('https://hannah.sumike.ai/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer sk-sumike-your-key-here',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    messages: [{ role: 'user', content: 'Research German EV market' }],
    stream: true
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');

  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = line.slice(6);
      if (data === '[DONE]') break;

      const parsed = JSON.parse(data);
      const content = parsed.choices[0]?.delta?.content || '';
      process.stdout.write(content);
    }
  }
}
```

---

## Error Handling

### Common Errors

#### 401 Unauthorized

```bash
curl -X POST https://hannah.sumike.ai/v1/chat/completions \
  -H "Authorization: Bearer invalid-key" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"test"}]}'
```

**Response:**
```json
{
  "error": {
    "message": "Invalid API key",
    "type": "authentication_error",
    "code": "invalid_api_key"
  }
}
```

**Solution:** Verify your API key format and validity.

#### 429 Rate Limited

```json
{
  "error": {
    "message": "Rate limit exceeded. Maximum 60 requests per minute.",
    "type": "rate_limit_error",
    "code": "rate_limit_exceeded"
  }
}
```

**Solution:** Wait 60 seconds before retrying. Implement exponential backoff.

#### 503 Service Unavailable

```json
{
  "error": {
    "message": "Agent temporarily unavailable. Please try again in a few minutes.",
    "type": "service_error",
    "code": "service_unavailable"
  }
}
```

**Solution:**
1. Wait 2-3 minutes
2. Check health endpoint: `curl -I https://hannah.sumike.ai/health`
3. Try alternative channel (email)

#### Request Timeout

If research tasks take longer than expected:

```bash
# Increase timeout
curl -X POST https://hannah.sumike.ai/v1/chat/completions \
  --max-time 600 \
  -H "Authorization: Bearer sk-sumike-your-key-here" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Deep research request"}]}'
```

**Recommended Timeouts:**
- Simple queries: 30 seconds
- Standard research: 5 minutes (300 seconds)
- Deep research: 10 minutes (600 seconds)

---

## Troubleshooting

### Test 1: Verify API Key

```bash
# Store key in variable
export HANNAH_KEY="sk-sumike-your-key-here"

# Test authentication
curl -X POST https://hannah.sumike.ai/v1/chat/completions \
  -H "Authorization: Bearer $HANNAH_KEY" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'

# Expected: Valid JSON response
# If error: Check API key format and validity
```

### Test 2: Check Rate Limits

```bash
# Send 5 requests rapidly
for i in {1..5}; do
  curl -X POST https://hannah.sumike.ai/v1/chat/completions \
    -H "Authorization: Bearer $HANNAH_KEY" \
    -H "Content-Type: application/json" \
    -d '{"messages":[{"role":"user","content":"Test '$i'"}]}'
  echo "Request $i completed"
done

# If you get 429 errors: Rate limit reached (60 req/min)
```

### Test 3: Verify Streaming

```bash
# Test streaming response
curl -N -X POST https://hannah.sumike.ai/v1/chat/completions \
  -H "Authorization: Bearer $HANNAH_KEY" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Quick test"}],"stream":true}'

# Expected: data: {...} chunks followed by data: [DONE]
# If no streaming: Check -N flag (disable buffering)
```

### Test 4: Elena → Hannah Delegation

```bash
# Send request to Elena that requires market research
curl -X POST https://elena.sumike.ai/v1/chat/completions \
  --max-time 600 \
  -H "Authorization: Bearer $ELENA_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Plan a product launch that targets German EV buyers. I need workstreams and risk assessment."
      }
    ]
  }'

# Expected: Elena delegates to Hannah for market context
# Response time: 5-10 minutes
# Response includes both operational plan AND market research findings
```

### Debug Mode

Enable verbose output to see request/response details:

```bash
curl -v -X POST https://hannah.sumike.ai/v1/chat/completions \
  -H "Authorization: Bearer $HANNAH_KEY" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"test"}]}'
```

This shows:
- DNS resolution
- TLS handshake
- Request headers
- Response headers
- Response body
- Connection details

---

## Using with OpenAI SDK

### Python

```python
from openai import OpenAI

# Hannah client
hannah = OpenAI(
    api_key="sk-sumike-your-hannah-key",
    base_url="https://hannah.sumike.ai/v1"
)

response = hannah.chat.completions.create(
    model="hannah-sumike",  # Model name doesn't matter
    messages=[
        {"role": "user", "content": "Research the German EV market"}
    ]
)

print(response.choices[0].message.content)

# Elena client
elena = OpenAI(
    api_key="sk-sumike-your-elena-key",
    base_url="https://elena.sumike.ai/v1"
)

response = elena.chat.completions.create(
    model="elena-sumike",
    messages=[
        {"role": "user", "content": "Plan a 6-week product launch"}
    ]
)

print(response.choices[0].message.content)
```

### TypeScript/JavaScript

```typescript
import OpenAI from 'openai';

const hannah = new OpenAI({
  apiKey: 'sk-sumike-your-hannah-key',
  baseURL: 'https://hannah.sumike.ai/v1'
});

const response = await hannah.chat.completions.create({
  model: 'hannah-sumike',
  messages: [
    { role: 'user', content: 'Research the German EV market' }
  ]
});

console.log(response.choices[0].message.content);
```

---

## Cost Estimation

### API Costs

API calls to Hannah and Elena are included with your subscription. However, if they orchestrate Sokosumi sub-agents, those incur costs:

| Sub-Agent | Typical Cost | Use Case |
|-----------|--------------|----------|
| Statista | ~120 credits | Market statistics and data |
| GWI | ~80 credits | Consumer insights and audience data |
| DataForSEO | ~60 credits | SEO and search trend analysis |
| Apify | ~40 credits | Social media data collection |
| dpa (German Press) | ~50 credits | News research and media monitoring |

**Hannah will inform you BEFORE creating sub-agent jobs:**

```json
{
  "content": "This research will use approximately:\n- Statista: ~120 credits\n- GWI: ~80 credits\n- Total: ~200 credits\n\nYour current balance: 450 credits\n\nShall I proceed?"
}
```

---

## Rate Limits & Quotas

### Per Agent

- **Rate Limit**: 60 requests per minute
- **Concurrent Requests**: 5 maximum
- **Request Timeout**: 10 minutes
- **Max Message Length**: 50,000 characters

### Burst Protection

The API implements token bucket rate limiting:

```
Bucket Capacity: 60 tokens
Refill Rate: 1 token per second
```

If you exceed 60 requests in 60 seconds, you'll get `429 Too Many Requests`.

**Retry Strategy:**

```bash
# Exponential backoff
attempt=1
max_attempts=5

while [ $attempt -le $max_attempts ]; do
  response=$(curl -s -w "%{http_code}" -X POST https://hannah.sumike.ai/v1/chat/completions \
    -H "Authorization: Bearer $HANNAH_KEY" \
    -H "Content-Type: application/json" \
    -d '{"messages":[{"role":"user","content":"test"}]}')

  http_code="${response: -3}"

  if [ "$http_code" == "200" ]; then
    echo "Success"
    break
  elif [ "$http_code" == "429" ]; then
    wait_time=$((2 ** attempt))
    echo "Rate limited. Waiting ${wait_time}s..."
    sleep $wait_time
    ((attempt++))
  else
    echo "Error: $http_code"
    break
  fi
done
```

---

## Support & Resources

- **API Issues**: support@sumike.ai
- **Documentation**: https://sumike.ai/docs
- **Status Page**: https://status.sumike.ai
- **Serviceplan**: https://www.serviceplan.com

---

**Last Updated**: 2026-02-12
**API Version**: v1
**Compatibility**: OpenAI SDK v4.0+
