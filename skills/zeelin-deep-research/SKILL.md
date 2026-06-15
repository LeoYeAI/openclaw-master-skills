---
name: ZeeLin Deep Research 深度研究
description: "ZeeLin Deep Research 深度研究是一款 AI 驱动的专业研究辅助平台，支持一句话生成与多步骤生成，提供深度、专家两大研究路径。从快速信息梳理、系统分析到超万字专家报告全流程覆盖，依托多轮推理与多源数据整合，高效完成企业分析、市场洞察、招商研究等复杂任务，一站式提升研究效率与决策质量。"
metadata: { "openclaw": { "emoji": "🔍", "requires": { "bins": ["curl"] } } }
---

# ZeeLin Deep Research 深度研究

> ZeeLin Deep Research 深度研究是一款 AI 驱动的专业研究辅助平台，支持一句话生成与多步骤生成，提供深度、专家两大研究路径。从快速信息梳理、系统分析到超万字专家报告全流程覆盖，依托多轮推理与多源数据整合，高效完成企业分析、市场洞察、招商研究等复杂任务，一站式提升研究效率与决策质量。

## 没有 API Key 怎么办？

如果用户没有提供 api_key，提示用户前往 https://desearch.zeelin.cn/skill-activity 进行免费注册或登录，获取点数及 api_key

## API 基础信息

- **Base URL**: `https://desearch.zeelin.cn`
- **认证方式**: Header `x-api-key`
- **接口**: `POST /api/conversation/anew`

## thinking 参数

- `deep` - 深度思考模式 - 需要全面分析但不需要万字报告
- `major` - 专家模式 - 需要深度系统性输出、万字报告

### 模式选择指南

**使用深度模式 (deep) 的场景**：
- 概念解释/知识梳理 — "什么是 XXX"、"XXX 的原理是什么"
- 事件/趋势分析 — 某个热点事件的来龙去脉、发展趋势
- 信息聚合 — 围绕某个话题汇总多方信息和观点
- 快速调研 — 用户没有明确要求深度报告的一般性研究问题

**使用专家模式 (major) 的场景**：
- 行业/市场分析 — 涉及特定行业的全景分析、市场格局、竞争态势
- 企业/公司研究 — 某个企业的财务分析、战略评估、业务拆解
- 政策/法规研究 — 需要系统梳理政策影响、合规要求
- 技术/产品深度对比 — 多维度的技术路线对比、产品竞品分析
- 投资/商业决策 — 需要数据支撑的投资分析、可行性评估

**如果不确定使用哪种模式**：可以询问用户确认

## 使用示例


### 深度思考模式

```bash
API_KEY="${DESEARCH_API_KEY}"
curl -s -X POST "https://desearch.zeelin.cn/api/conversation/anew" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "sessionId": "",
    "content": "你的问题",
    "thinking": "deep",
    "workflow": "",
    "needEditChapter": 0,
    "moreSettings": {}
  }'
```

### 专家模式

```bash
API_KEY="${DESEARCH_API_KEY}"
curl -s -X POST "https://desearch.zeelin.cn/api/conversation/anew" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "sessionId": "",
    "content": "你的问题",
    "thinking": "major",
    "workflow": "",
    "needEditChapter": 0,
    "moreSettings": {}
  }'
```

## 多轮对话

第一轮返回的 `sessionId` 可以用于后续对话：

```bash
API_KEY="${DESEARCH_API_KEY}"
curl -s -X POST "https://desearch.zeelin.cn/api/conversation/anew" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "sessionId": "上一轮的sessionId",
    "content": "追问内容",
    "thinking": "deep",
    "workflow": "",
    "moreSettings": {}
  }'
```

## 快速调用

用户 API key 从环境变量 `DESEARCH_API_KEY` 读取。

**设置方式：**
```bash
export DESEARCH_API_KEY="你的API Key"
```

### 深度模式调用示例

```bash
API_KEY="${DESEARCH_API_KEY}"
curl -s -X POST "https://desearch.zeelin.cn/api/conversation/anew" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "sessionId": "",
    "content": "调研一下汽车产业规模",
    "thinking": "deep",
    "workflow": "",
    "moreSettings": {}
  }'
```

## 注意事项

- `sessionId` 为空时创建新对话
- `thinking` 参数决定推理深度
- API 返回 JSON，包含回答内容

---

## 查询任务状态

任务提交后，需要轮询查询状态：

```bash
API_KEY="${DESEARCH_API_KEY}"
curl -s -X GET "https://desearch.zeelin.cn/api/conversation/status?sessionId={sessionId}" \
  -H "x-api-key: ${API_KEY}"
```

**返回示例:**
```json
{
    "code": 200,
    "v": "v1.5.0",
    "msg": "成功",
    "data": {
        "status": 2,
        "thinking": "deep",
        "workflow": "",
        "message": "会话已生成",
        "content": "调研一下汽车产业规模",
        "time": "",
        "thinkingWorkflowName": "深度模式",
        "pptUrl": "",
        "wavUrl": "",
        "mdxUrl": "",
        "mdUrl": "",
        "htmlUrl": "",
        "wavScriptUrl": "",
        "isShare": 0,
        "isMine": 0,
        "title": "调研一下汽车产业规模",
        "short": "jVICQSS5",
        "questionId": 281697,
        "sessionId": "b9162dfdefa74461a764aebe51366d87",
        "useKnowledge": 0,
        "onlyKnowledge": 0,
        "searchRange": "web"
    }
}
```

**状态码说明:**
- `1` = 进行中
- `2` = 正常结束 ✅
- `3` = 用户主动结束
- `4` = 失败
- `5` = 排队中

---
## 完整任务流程

1. **创建任务** → POST `/api/conversation/anew` 获取 `sessionId`
2. **轮询状态** → 每隔一段时间调用 `/api/conversation/status?sessionId={id}` 检查状态
3. **状态 = 2** → 任务完成
4. **获取 PDF 报告** → 调用 `/api/conversation/to_report?sessionId={id}&reportType=pdf` 获取 PDF 下载链接
5. **下载 PDF** → 从 data 字段获取 URL，下载 PDF 文件到本地
6. **发送消息** → 使用 `message` 工具发送 PDF 文件到用户

## 错误处理

### 接口调用超限错误 (code=315)

当 API 返回 code=315 且 msg 包含"当前接口调用已超限"时，表示当前并发任务数已达到上限（max_limit_conversation），需要等待当前任务执行完成后再提交新任务：

```bash
# 检查返回码
RESULT=$(curl -s -X POST "https://desearch.zeelin.cn/api/conversation/anew" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "sessionId": "",
    "content": "你的问题",
    "thinking": "deep",
    "workflow": "",
    "needEditChapter": 0,
    "moreSettings": {}
  }')

CODE=$(echo $RESULT | jq -r '.code')
MSG=$(echo $RESULT | jq -r '.msg')

if [ "$CODE" = "315" ] && echo "$MSG" | grep -q "当前接口调用已超限"; then
  # 发送提示给用户，等待当前任务完成
  message action=send target=用户ID message="⚠️ 当前接口调用已超限，请等待当前任务执行完成后再提交新任务。"
  exit 1
fi
```

**返回示例:**
```json
{
  "code": 315,
  "v": "0.0.914",
  "msg": "当前接口调用已超限，请联系我们",
  "data": {
    "max_limit_conversation": 1,
    "now_conversation": 1
  }
}
```

### 试用超限错误 (code=315)

当 API 返回 code=315 且 msg 包含"试用已超限"时，需要引导用户充值：

```bash
# 检查返回码
RESULT=$(curl -s -X POST "https://desearch.zeelin.cn/api/conversation/anew" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "sessionId": "",
    "content": "你的问题",
    "thinking": "deep",
    "workflow": "",
    "needEditChapter": 0,
    "moreSettings": {}
  }')

CODE=$(echo $RESULT | jq -r '.code')
MSG=$(echo $RESULT | jq -r '.msg')

if [ "$CODE" = "315" ] && echo "$MSG" | grep -q "试用已超限"; then
  # 发送充值提示给用户
  message action=send target=用户ID message="⚠️ 您的点数已超限，无法继续使用。请前往充值页面购买点数：https://desearch.zeelin.cn/skill-activity"
  exit 1
fi
```

**充值地址**: https://desearch.zeelin.cn/skill-activity

### 完整流程示例

```bash
# 1. 创建任务
API_KEY="${DESEARCH_API_KEY}"
RESULT=$(curl -s -X POST "https://desearch.zeelin.cn/api/conversation/anew" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "sessionId": "",
    "content": "你的问题",
    "thinking": "deep",
    "workflow": "",
    "needEditChapter": 0,
    "moreSettings": {}
  }')

SESSION_ID=$(echo $RESULT | jq -r '.data.sessionId')
QUESTION_ID=$(echo $RESULT | jq -r '.data.id')

echo "Session ID: $SESSION_ID, Question ID: $QUESTION_ID"

# 2. 轮询状态直到完成
while true; do
  STATUS=$(curl -s -X GET "https://desearch.zeelin.cn/api/conversation/status?sessionId=${SESSION_ID}" \
    -H "x-api-key: ${API_KEY}" | jq -r '.data.status')
  
  if [ "$STATUS" = "2" ]; then
    echo "任务完成"
    break
  fi
  echo "状态: $STATUS, 等待中..."
  sleep 60  # 每分钟检查一次
done

# 3. 获取 PDF 报告链接
REPORT_RESULT=$(curl -s -X GET "https://desearch.zeelin.cn/api/conversation/to_report?sessionId=${SESSION_ID}&reportType=pdf" \
  -H "x-api-key: ${API_KEY}")

PDF_URL=$(echo $REPORT_RESULT | jq -r '.data')
echo "PDF URL: $PDF_URL"

# 4. 下载 PDF 文件
curl -s -o /tmp/research_result.pdf "$PDF_URL"

# 5. 发送 PDF 文件给用户
message action=send target=用户ID filePath=/tmp/research_result.pdf
```

### 实际调用命令（执行时替换对应变量）

```bash
# 1. 创建任务
API_KEY="${DESEARCH_API_KEY}"
curl -s -X POST "https://desearch.zeelin.cn/api/conversation/anew" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "sessionId": "",
    "content": "你的问题",
    "thinking": "deep",
    "workflow": "",
    "needEditChapter": 0,
    "moreSettings": {}
  }'
```

### 轮询状态脚本

```bash
# 轮询直到任务完成 (status = 2)
API_KEY="${DESEARCH_API_KEY}"
SESSION_ID="替换为实际的sessionId"

while true; do
  STATUS_RESPONSE=$(curl -s -X GET "https://desearch.zeelin.cn/api/conversation/status?sessionId=${SESSION_ID}" \
    -H "x-api-key: ${API_KEY}")
  
  STATUS=$(echo $STATUS_RESPONSE | jq -r '.data.status')
  echo "当前状态: $STATUS"
  
  if [ "$STATUS" = "2" ]; then
    echo "任务完成！"
    break
  fi
  
  sleep 60  # 每分钟检查一次
done

# 获取 PDF 报告链接
REPORT_RESULT=$(curl -s -X GET "https://desearch.zeelin.cn/api/conversation/to_report?sessionId=${SESSION_ID}&reportType=pdf" \
  -H "x-api-key: ${API_KEY}")

PDF_URL=$(echo $REPORT_RESULT | jq -r '.data')

# 下载 PDF 文件
curl -s -o /tmp/research_result.pdf "$PDF_URL"

# 发送 PDF 文件给用户
message action=send target=用户ID filePath=/tmp/research_result.pdf
```

---

## ⚠️ 重要：必须保存文件再发送

**❌ 禁止直接发送文字内容给用户**
**✅ 必须：获取 PDF 链接 → 下载 PDF 文件 → 发送 PDF 文件给用户**

### 正确流程示例（飞书文档）

```bash
# 1. 创建任务
API_KEY="${DESEARCH_API_KEY}"
RESULT=$(curl -s -X POST "https://desearch.zeelin.cn/api/conversation/anew" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "sessionId": "",
    "content": "用户的问题",
    "thinking": "deep",
    "workflow": "",
    "needEditChapter": 0,
    "moreSettings": {}
  }')

SESSION_ID=$(echo $RESULT | jq -r '.data.sessionId')

# 2. 轮询状态直到完成 (status=2)
while true; do
  STATUS=$(curl -s "https://desearch.zeelin.cn/api/conversation/status?sessionId=${SESSION_ID}" \
    -H "x-api-key: ${API_KEY}" | jq -r '.data.status')
  [ "$STATUS" = "2" ] && break
  sleep 30
done

# 3. 获取 PDF 报告链接
REPORT_RESULT=$(curl -s -X GET "https://desearch.zeelin.cn/api/conversation/to_report?sessionId=${SESSION_ID}&reportType=pdf" \
  -H "x-api-key: ${API_KEY}")

PDF_URL=$(echo $REPORT_RESULT | jq -r '.data')

# 4. 下载 PDF 文件
curl -s -o /tmp/research_result.pdf "$PDF_URL"

# 5. 发送 PDF 文件给用户
message action=send target=用户ID filePath=/tmp/research_result.pdf
```

### 关键点

- 任务完成后调用 `/api/conversation/to_report?sessionId={id}&reportType=pdf` 获取 PDF 下载链接
- 从返回的 `data` 字段提取 PDF URL
- 使用 curl 下载 PDF 文件到本地
- 直接发送 PDF 文件给用户

### 后台执行与自动发送

**确保任务完成后自动发送 PDF 的关键：**

1. **使用足够长的 timeout**：设置 `timeout=1200` 或更长，确保 exec 命令等待任务完成
2. **轮询循环内检查状态**：
   ```bash
   while true; do
     STATUS=$(curl -s "https://desearch.zeelin.cn/api/conversation/status?sessionId=${SESSION_ID}" \
       -H "x-api-key: ${API_KEY}" | jq -r '.data.status')
     [ "$STATUS" = "2" ] && break  # 任务完成后跳出循环
     [ "$STATUS" = "4" ] && exit 1 # 任务失败则退出
     sleep 30
   done
   ```
3. **任务完成后立即发送**：在轮询循环结束后，立即调用 message 工具发送 PDF
   ```bash
   # 下载 PDF 后立即发送
   curl -s -o /tmp/research_result.pdf "$PDF_URL"
   message action=send target=用户ID filePath=/tmp/research_result.pdf
   ```

**❌ 错误做法**：轮询后不等待结果就退出，或超时时间太短导致任务未完成就退出

**✅ 正确做法**：使用 while 循环 + 足够长的 timeout，任务完成后立即发送 PDF

### 后台执行（用户可同时做其他事情）

当用户希望任务在后台运行、同时可以让你执行其他任务时，使用 OpenClaw 的后台执行功能：

**方式一：使用 `background=true` 参数**

```bash
exec command="..." background=true timeout=1200
```

这样命令会在后台运行，不会阻塞当前会话，你可以继续给其他命令。

**方式二：使用 `exec` + `yieldMs` 参数**

```bash
exec command="..." yieldMs=10000
```

设置 yieldMs 让出控制权，命令在后台继续运行。

**方式三：使用 `process` 工具管理后台任务**

1. 先启动后台任务：
   ```bash
   exec command="完整的轮询+发送脚本" timeout=1200
   ```

2. 使用 `process(action=poll)` 轮询结果：
   ```bash
   process action=poll sessionId=<session_id> timeout=600000
   ```

**后台任务完整示例：**

```bash
# 1. 创建任务（立即返回）
API_KEY="${DESEARCH_API_KEY}"
RESULT=$(curl -s -X POST "https://desearch.zeelin.cn/api/conversation/anew" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "sessionId": "",
    "content": "用户的研究问题",
    "thinking": "deep",
    "workflow": "",
    "needEditChapter": 0,
    "moreSettings": {}
  }')

SESSION_ID=$(echo "$RESULT" | jq -r '.data.sessionId')
echo "任务已创建: $SESSION_ID"

# 2. 后台轮询 + 下载 + 发送（设置长timeout）
exec command="
  SESSION_ID='$SESSION_ID'
  API_KEY='$API_KEY'
  
  # 轮询直到完成
  while true; do
    STATUS=\$(curl -s 'https://desearch.zeelin.cn/api/conversation/status?sessionId=\${SESSION_ID}' \\
      -H 'x-api-key: \${API_KEY}' | jq -r '.data.status')
    [ \"\$STATUS\" = \"2\" ] && break
    [ \"\$STATUS\" = \"4\" ] && exit 1
    sleep 30
  done
  
  # 获取并下载PDF
  PDF_URL=\$(curl -s 'https://desearch.zeelin.cn/api/conversation/to_report?sessionId=\${SESSION_ID}&reportType=pdf' \\
    -H 'x-api-key: \${API_KEY}' | jq -r '.data')
  curl -s -o /tmp/report.pdf \"\$PDF_URL\"
  
  # 发送PDF（替换为目标用户ID）
  message action=send target=用户ID filePath=/tmp/report.pdf
" timeout=1200
```

**用户可以：**
- 随时查询任务状态
- 在后台任务运行期间执行其他命令
- 任务完成后自动收到 PDF

---

## ⚠️ 跨渠道发送文件注意事项

### 不同渠道的文件限制

| 渠道 | 文件大小限制 |
|-----|------------|
| 钉钉 | 20MB |
| 飞书 | 20MB |
| Telegram | 50MB |
| Discord | 8MB |
| WhatsApp | 16MB |

---

## ⚠️ 飞书渠道：必须创建飞书文档发送

**当用户渠道为飞书时，禁止直接发送 PDF 文件给用户，必须按以下流程操作：**

### 飞书渠道完整流程

```bash
# 1. 创建任务
API_KEY="${DESEARCH_API_KEY}"
RESULT=$(curl -s -X POST "https://desearch.zeelin.cn/api/conversation/anew" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "sessionId": "",
    "content": "用户的问题",
    "thinking": "deep",
    "workflow": "",
    "needEditChapter": 0,
    "moreSettings": {}
  }')

SESSION_ID=$(echo $RESULT | jq -r '.data.sessionId')
TITLE=$(echo $RESULT | jq -r '.data.title')

# 2. 轮询状态直到完成 (status=2)
while true; do
  STATUS=$(curl -s "https://desearch.zeelin.cn/api/conversation/status?sessionId=${SESSION_ID}" \
    -H "x-api-key: ${API_KEY}" | jq -r '.data.status')
  [ "$STATUS" = "2" ] && break
  sleep 30
done

# 3. 获取 Word 报告链接（Word 格式更容易提取文字内容）
REPORT_RESULT=$(curl -s -X GET "https://desearch.zeelin.cn/api/conversation/to_report?sessionId=${SESSION_ID}&reportType=word" \
  -H "x-api-key: ${API_KEY}")

WORD_URL=$(echo $REPORT_RESULT | jq -r '.data')

# 4. 下载 Word 文件
curl -s -o /tmp/research.docx "$WORD_URL"

# 5. 解压 Word 文件提取文字内容
unzip -q /tmp/research.docx -d /tmp/research_docx/
sed 's/<[^>]*>//g' /tmp/research_docx/word/document.xml | tr -s ' \n' > /tmp/research.txt

# 6. 创建飞书文档
DOC_RESULT=$(feishu_doc action=create title="调研报告：${TITLE}")

DOC_TOKEN=$(echo $DOC_RESULT | jq -r '.document_id')
DOC_URL=$(echo $DOC_RESULT | jq -r '.url')

# 7. 写入内容到飞书文档
feishu_doc action=write doc_token=${DOC_TOKEN} content=$(cat /tmp/research.txt)

# 8. 发送文档链接给用户
message action=send target=用户ID message="📄 调研报告已生成：${DOC_URL}"
```

### 飞书渠道检查清单

- [ ] 渠道是飞书吗？
- [ ] 是否已创建飞书文档？
- [ ] 是否已将报告内容写入飞书文档？
- [ ] 是否发送的是飞书文档链接而非 PDF？

### 飞书渠道 ❌ 禁止事项

- ❌ 直接发送 PDF 文件（用户打不开）
- ❌ 直接发送本地文件路径
- ❌ 发送服务器目录

### 飞书渠道 ✅ 正确做法

- ✅ 创建飞书文档 (feishu_doc action=create)
- ✅ 写入内容 (feishu_doc action=write)
- ✅ 发送文档链接 (message action=send 附带 URL)

### 确保发送成功的检查

```bash
# 检查文件是否存在且非空
if [ -f /tmp/research.md ] && [ -s /tmp/research.md ]; then
  # 发送文件
  message action=send target=用户ID filePath=/tmp/research.md
else
  echo "文件无效或为空"
fi
```

---


