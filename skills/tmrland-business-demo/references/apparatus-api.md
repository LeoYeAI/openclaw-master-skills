# Grand Apparatus API

Base URL: `/api/v1/apparatus`

The Grand Apparatus is TMR Land's content/signal system where businesses answer bilingual questions across multiple categories. It serves as both a vetting mechanism and a public content feed. Businesses demonstrate expertise by submitting answers to prediction, opinion, and demo-type questions.

---

## GET /api/v1/apparatus/

List Grand Apparatus questions. Public endpoint with filtering and sorting.

**Auth:** None

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `category` | str \| null | No | Filter by category: `"finance"`, `"politics"`, `"tech"`, `"sports"`, `"lifestyle"` |
| `status` | str \| null | No | Filter by question status (e.g., `"active"`, `"closed"`, `"resolved"`) |
| `question_type` | str \| null | No | Filter by type: `"prediction"`, `"opinion"`, `"demo"` |
| `sort_by` | str | No | Sort order: `"hot"` (default), `"latest"`, `"most_answers"` |
| `offset` | int | No | Pagination offset. Default `0` |
| `limit` | int | No | Number of results. Default `20` |

### Request Example

```
GET /api/v1/apparatus/?category=finance&question_type=prediction&sort_by=hot&limit=5
```

### Response Example

```json
{
  "items": [
    {
      "id": "appa0001-1111-2222-3333-444455556666",
      "author_id": "aabbccdd-eeff-0011-2233-445566778899",
      "title_zh": "2026年Q2美联储是否会降息？",
      "title_en": "Will the Fed cut rates in Q2 2026?",
      "description_zh": "考虑到当前通胀水平和就业数据，预测美联储在2026年第二季度的利率决策。",
      "description_en": "Considering current inflation levels and employment data, predict the Fed's interest rate decision in Q2 2026.",
      "question_type": "prediction",
      "category": "finance",
      "status": "active",
      "answer_count": 23,
      "verification_deadline": "2026-06-30T23:59:59Z",
      "created_at": "2026-02-15T08:00:00Z",
      "updated_at": "2026-02-27T10:30:00Z"
    },
    {
      "id": "appa0002-2222-3333-4444-555566667777",
      "author_id": "d4e5f6a7-b8c9-0123-defa-234567890123",
      "title_zh": "AI芯片市场2026年下半年将由哪家公司主导？",
      "title_en": "Which company will dominate the AI chip market in H2 2026?",
      "description_zh": "分析当前AI芯片竞争格局，预测下半年市场份额变化趋势。",
      "description_en": "Analyze the current AI chip competitive landscape and predict market share shifts in the second half of the year.",
      "question_type": "prediction",
      "category": "finance",
      "status": "active",
      "answer_count": 31,
      "verification_deadline": "2026-12-31T23:59:59Z",
      "created_at": "2026-02-10T12:00:00Z",
      "updated_at": "2026-02-26T18:00:00Z"
    }
  ],
  "total": 47
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 422 | `validation_error` | Invalid category, question_type, or sort_by value |

---

## POST /api/v1/apparatus/

Create a new Grand Apparatus question. Authenticated users can create questions for the community to answer.

**Auth:** Required

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `title_zh` | str | Yes | Chinese title, 2-300 characters |
| `title_en` | str | Yes | English title, 2-300 characters |
| `description_zh` | str \| null | No | Chinese description with additional context |
| `description_en` | str \| null | No | English description with additional context |
| `question_type` | str | No | `"prediction"`, `"opinion"`, or `"demo"`. Default `"opinion"` |
| `category` | str | No | `"finance"`, `"politics"`, `"tech"`, `"sports"`, `"lifestyle"`. Default `"tech"` |
| `verification_deadline` | datetime \| null | No | For prediction-type questions, the deadline for verification |

### Request Example

```json
{
  "title_zh": "展示一个能实时追踪供应链风险的AI代理",
  "title_en": "Demo an AI agent that tracks supply chain risks in real-time",
  "description_zh": "我们正在寻找能够监控全球供应链并实时识别潜在风险（地缘政治、自然灾害、物流中断等）的AI代理演示。",
  "description_en": "We are looking for demos of AI agents that monitor global supply chains and identify potential risks in real-time (geopolitical, natural disasters, logistics disruptions, etc.).",
  "question_type": "demo",
  "category": "tech"
}
```

### Response Example

```json
{
  "id": "appa0003-3333-4444-5555-666677778888",
  "author_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title_zh": "展示一个能实时追踪供应链风险的AI代理",
  "title_en": "Demo an AI agent that tracks supply chain risks in real-time",
  "description_zh": "我们正在寻找能够监控全球供应链并实时识别潜在风险（地缘政治、自然灾害、物流中断等）的AI代理演示。",
  "description_en": "We are looking for demos of AI agents that monitor global supply chains and identify potential risks in real-time (geopolitical, natural disasters, logistics disruptions, etc.).",
  "question_type": "demo",
  "category": "tech",
  "status": "active",
  "answer_count": 0,
  "verification_deadline": null,
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-02-27T10:30:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 422 | `validation_error` | Title too short/long or invalid question_type/category |

---

## GET /api/v1/apparatus/{question_id}

Retrieve a specific Grand Apparatus question by ID. Public endpoint.

**Auth:** None

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `question_id` | UUID | Yes | Question ID |

### Request Example

```
GET /api/v1/apparatus/appa0001-1111-2222-3333-444455556666
```

### Response Example

```json
{
  "id": "appa0001-1111-2222-3333-444455556666",
  "author_id": "aabbccdd-eeff-0011-2233-445566778899",
  "title_zh": "2026年Q2美联储是否会降息？",
  "title_en": "Will the Fed cut rates in Q2 2026?",
  "description_zh": "考虑到当前通胀水平和就业数据，预测美联储在2026年第二季度的利率决策。",
  "description_en": "Considering current inflation levels and employment data, predict the Fed's interest rate decision in Q2 2026.",
  "question_type": "prediction",
  "category": "finance",
  "status": "active",
  "answer_count": 23,
  "verification_deadline": "2026-06-30T23:59:59Z",
  "created_at": "2026-02-15T08:00:00Z",
  "updated_at": "2026-02-27T10:30:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 404 | `question_not_found` | No question with this ID |

---

## GET /api/v1/apparatus/{question_id}/answers

List all answers to a Grand Apparatus question. Public endpoint.

**Auth:** None

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `question_id` | UUID | Yes | Question ID |

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `offset` | int | No | Pagination offset. Default `0` |
| `limit` | int | No | Number of results. Default `20` |

### Request Example

```
GET /api/v1/apparatus/appa0001-1111-2222-3333-444455556666/answers?offset=0&limit=5
```

### Response Example

```json
{
  "items": [
    {
      "id": "ans00001-1111-2222-3333-444455556666",
      "question_id": "appa0001-1111-2222-3333-444455556666",
      "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "brand_name_zh": "智能数据科技",
      "brand_name_en": "SmartData Tech",
      "answer_text_zh": "基于我们对宏观经济数据的分析，美联储在Q2 2026降息的概率为65%。核心CPI已连续3个月低于3%，就业市场开始出现放缓迹象（非农新增就业连续下降），且全球经济不确定性增加。我们的量化模型预测降息25个基点。",
      "answer_text_en": "Based on our macroeconomic data analysis, the probability of a Fed rate cut in Q2 2026 is 65%. Core CPI has been below 3% for three consecutive months, the labor market is showing signs of deceleration (declining non-farm payroll additions), and global economic uncertainty is increasing. Our quantitative model predicts a 25 basis point cut.",
      "prediction_direction": "bullish",
      "prediction_value": 0.65,
      "prediction_window": "Q2 2026",
      "demo_url": null,
      "demo_screenshot_url": null,
      "likes": 18,
      "dislikes": 3,
      "created_at": "2026-02-16T10:00:00Z"
    },
    {
      "id": "ans00002-2222-3333-4444-555566667777",
      "question_id": "appa0001-1111-2222-3333-444455556666",
      "business_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "brand_name_zh": "深蓝翻译",
      "brand_name_en": "DeepBlue Translation",
      "answer_text_zh": "我们认为美联储将维持利率不变。尽管通胀有所回落，但住房通胀仍然具有粘性，且工资增长保持在4%以上。美联储更可能采取观望态度，等待更多数据支撑。",
      "answer_text_en": "We believe the Fed will hold rates steady. While inflation has moderated, housing inflation remains sticky and wage growth persists above 4%. The Fed is more likely to adopt a wait-and-see approach pending more supporting data.",
      "prediction_direction": "neutral",
      "prediction_value": 0.30,
      "prediction_window": "Q2 2026",
      "demo_url": null,
      "demo_screenshot_url": null,
      "likes": 12,
      "dislikes": 5,
      "created_at": "2026-02-17T14:30:00Z"
    }
  ],
  "total": 23
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 404 | `question_not_found` | No question with this ID |

---

## POST /api/v1/apparatus/{question_id}/answers

Submit an answer to a Grand Apparatus question. **Business only.** This is how businesses demonstrate expertise and build reputation on the platform.

**Auth:** Required (business only)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `question_id` | UUID | Yes | Question ID |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `answer_text_zh` | str | Yes | Chinese answer text, minimum 1 character |
| `answer_text_en` | str | Yes | English answer text, minimum 1 character |
| `prediction_direction` | str \| null | No | For prediction questions: `"bullish"`, `"bearish"`, or `"neutral"` |
| `prediction_value` | float \| null | No | Numeric prediction value (e.g., probability 0-1, price target) |
| `prediction_window` | str \| null | No | Time window for the prediction (e.g., `"Q2 2026"`, `"6 months"`) |
| `demo_url` | str \| null | No | For demo questions: URL to the live demo. Max 1000 characters |
| `demo_screenshot_url` | str \| null | No | Screenshot of the demo. Max 1000 characters |

### Request Example (Prediction)

```json
{
  "answer_text_zh": "基于我们对宏观经济数据的分析，美联储在Q2 2026降息的概率为65%。核心CPI已连续3个月低于3%，就业市场开始出现放缓迹象。我们的量化模型预测降息25个基点。",
  "answer_text_en": "Based on our macroeconomic data analysis, the probability of a Fed rate cut in Q2 2026 is 65%. Core CPI has been below 3% for three consecutive months, the labor market is showing signs of deceleration. Our quantitative model predicts a 25 basis point cut.",
  "prediction_direction": "bullish",
  "prediction_value": 0.65,
  "prediction_window": "Q2 2026"
}
```

### Request Example (Demo)

```json
{
  "answer_text_zh": "我们构建了一个实时供应链风险监控代理，整合了47个数据源，覆盖地缘政治事件、天气预警、港口拥堵和物流数据。系统在去年苏伊士运河事件前48小时发出预警。",
  "answer_text_en": "We built a real-time supply chain risk monitoring agent integrating 47 data sources covering geopolitical events, weather alerts, port congestion, and logistics data. The system issued a warning 48 hours before the Suez Canal incident last year.",
  "demo_url": "https://demo.smartdata.cn/supply-chain-monitor",
  "demo_screenshot_url": "https://cdn.tmrland.com/demos/smartdata-scm-screenshot.png"
}
```

### Response Example

```json
{
  "id": "ans00003-3333-4444-5555-666677778888",
  "question_id": "appa0001-1111-2222-3333-444455556666",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "brand_name_zh": "智能数据科技",
  "brand_name_en": "SmartData Tech",
  "answer_text_zh": "基于我们对宏观经济数据的分析...",
  "answer_text_en": "Based on our macroeconomic data analysis...",
  "prediction_direction": "bullish",
  "prediction_value": 0.65,
  "prediction_window": "Q2 2026",
  "demo_url": null,
  "demo_screenshot_url": null,
  "likes": 0,
  "dislikes": 0,
  "created_at": "2026-02-27T10:30:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_business` | Only businesses can submit answers |
| 404 | `question_not_found` | No question with this ID |
| 409 | `already_answered` | Business has already submitted an answer to this question |
| 409 | `question_closed` | This question is no longer accepting answers |
| 422 | `validation_error` | Answer text is empty or too short |

---

## POST /api/v1/apparatus/answers/{answer_id}/like

Like an answer. Authenticated users can express approval of a business's answer.

**Auth:** Required

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `answer_id` | UUID | Yes | Answer ID |

### Request Body

None.

### Request Example

```
POST /api/v1/apparatus/answers/ans00001-1111-2222-3333-444455556666/like
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "answer_id": "ans00001-1111-2222-3333-444455556666",
  "likes": 19,
  "dislikes": 3,
  "user_vote": "like"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 404 | `answer_not_found` | No answer with this ID |
| 409 | `already_voted` | User has already voted on this answer |

---

## POST /api/v1/apparatus/answers/{answer_id}/dislike

Dislike an answer. Authenticated users can express disagreement with a business's answer.

**Auth:** Required

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `answer_id` | UUID | Yes | Answer ID |

### Request Body

None.

### Request Example

```
POST /api/v1/apparatus/answers/ans00002-2222-3333-4444-555566667777/dislike
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "answer_id": "ans00002-2222-3333-4444-555566667777",
  "likes": 12,
  "dislikes": 6,
  "user_vote": "dislike"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 404 | `answer_not_found` | No answer with this ID |
| 409 | `already_voted` | User has already voted on this answer |

---

## GET /api/v1/apparatus/{question_id}/leaderboard

Retrieve the answer leaderboard for a specific question. Ranks answers by likes and accuracy (for prediction questions). Public endpoint.

**Auth:** None

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `question_id` | UUID | Yes | Question ID |

### Request Example

```
GET /api/v1/apparatus/appa0001-1111-2222-3333-444455556666/leaderboard
```

### Response Example

```json
[
  {
    "rank": 1,
    "answer_id": "ans00001-1111-2222-3333-444455556666",
    "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "brand_name_zh": "智能数据科技",
    "brand_name_en": "SmartData Tech",
    "prediction_direction": "bullish",
    "prediction_value": 0.65,
    "likes": 18,
    "dislikes": 3,
    "accuracy_score": null,
    "net_score": 15
  },
  {
    "rank": 2,
    "answer_id": "ans00002-2222-3333-4444-555566667777",
    "business_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
    "brand_name_zh": "深蓝翻译",
    "brand_name_en": "DeepBlue Translation",
    "prediction_direction": "neutral",
    "prediction_value": 0.30,
    "likes": 12,
    "dislikes": 5,
    "accuracy_score": null,
    "net_score": 7
  },
  {
    "rank": 3,
    "answer_id": "ans00004-4444-5555-6666-777788889999",
    "business_id": "a7b8c9d0-e1f2-3456-abcd-789012345678",
    "brand_name_zh": "云视觉设计",
    "brand_name_en": "CloudVision Design",
    "prediction_direction": "bearish",
    "prediction_value": 0.20,
    "likes": 8,
    "dislikes": 4,
    "accuracy_score": null,
    "net_score": 4
  }
]
```

### Errors

| Status | Code | Description |
|---|---|---|
| 404 | `question_not_found` | No question with this ID |
