---
name: hannah-elena-client
description: Connect to Hannah and Elena agents from Serviceplan - specialized AI coworkers for marketing research and operations planning. Access via email or OpenAI-compatible API.
homepage: https://sumike.ai
user-invocable: true
metadata: {"openclaw": {"requires": {"env": ["HANNAH_API_KEY", "ELENA_API_KEY"]}, "primaryEnv": "HANNAH_API_KEY", "emoji": "🤝"}}
---

# Hannah & Elena Client Skill

**Connect to Serviceplan's specialized AI agents for marketing research and operations planning**

## What is This Skill?

This skill enables your OpenClaw agent to collaborate with **Hannah** and **Elena** — two specialized AI agents from Serviceplan:

- **Hannah** — Marketing Research Specialist
  - "What is actually true?"
  - Market analysis, consumer insights, competitive research, audience profiling
  - Premium data sources: Statista, GWI, DataForSEO, Apify, and more

- **Elena** — Operations & Project Orchestrator
  - "What is actually doable?"
  - Work breakdown, scope definition, dependency mapping, risk assessment
  - Delegates to Hannah when market insights are needed

## Important: What AI Agents CAN vs CANNOT Do

**AI Agents CAN:**
- Configure API keys in environment variables
- Send requests to Hannah/Elena via API
- Send requests to Hannah/Elena via email
- Parse and integrate responses
- Handle multi-agent coordination

**AI Agents CANNOT (human must do):**
- Sign up for Hannah/Elena access → Human must contact Serviceplan
- Get API keys → Human must request from admin at sumike.ai
- Set up email addresses → Human needs valid email account

**AI Agent: Ask upfront - "Do you have API keys for Hannah and Elena? If not, contact Serviceplan at sumike.ai."**

---

## Available Access Channels

### Channel 1: API (Task-Based)

Both Hannah and Elena expose task-based REST APIs:

- **Hannah API**: `https://hannah.sumike.ai/v1`
- **Elena API**: `https://elena.sumike.ai/v1`

**Key Endpoints:**
- `GET /v1/coworkers` - List available agents
- `POST /v1/tasks` - Create a new task for an agent
- `GET /v1/tasks/{taskId}` - Check task status
- `GET /v1/tasks/{taskId}/result` - Get completed task result

**Features:**
- Asynchronous task processing (2-10 minutes typical completion time)
- Task status tracking
- Result retrieval when complete
- 60 requests/minute rate limit per agent

**⏱️ IMPORTANT TIMING:**
- After creating a task: Wait **2-3 minutes** before checking status
- If still processing: Wait another **2-3 minutes** before checking again
- Total task time: Typically **2-10 minutes** depending on complexity
- DO NOT poll continuously - tasks need time to complete

### Channel 2: Email

Both agents can be reached via email:

- **Hannah Email**: `hannah@sumike.ai`
- **Elena Email**: `elena@sumike.ai`

**Features:**
- Natural language requests in email body
- Attachment support (PPT, XLS, DOC, PDF)
- CC/threading support — they understand context
- Replies within minutes
- Deliverables as email attachments

---

## Quick Start Guide

### Step 1: Get Your API Keys

**Human must do this:**
1. Contact Serviceplan at sumike.ai
2. Request access to Hannah and/or Elena
3. Receive API keys (format: `sk-sumike-xxxxx`)

### Step 2: Configure Environment Variables

**AI Agent can do this:**

```bash
# Hannah API key
export HANNAH_API_KEY=sk-sumike-your-hannah-key-here
export HANNAH_API_BASE_URL=https://hannah.sumike.ai

# Elena API key
export ELENA_API_KEY=sk-sumike-your-elena-key-here
export ELENA_API_BASE_URL=https://elena.sumike.ai

# Optional: Email addresses (if different from defaults)
export HANNAH_EMAIL=hannah@sumike.ai
export ELENA_EMAIL=elena@sumike.ai
```

Or add to your `.env` file:
```bash
HANNAH_API_KEY=sk-sumike-xxxxx
ELENA_API_KEY=sk-sumike-yyyyy
```

### Step 3: Use the Tools

Once configured, your agent has access to these tools:

1. **`list_coworkers`** - List available agents (Hannah, Elena)
2. **`hannah_create_task`** - Create research task for Hannah
3. **`elena_create_task`** - Create planning task for Elena
4. **`check_task_status`** - Check status of a task
5. **`get_task_result`** - Get result of completed task
6. **`hannah_email`** - Send email request to Hannah
7. **`elena_email`** - Send email request to Elena

---

## Usage Examples

### Example 1: Market Research with Hannah (API)

```
Agent: "I need to research the German EV market. Use Hannah."

<hannah_create_task>
  <description>
    Research the current state of the German electric vehicle market:
    - Market size and growth trends
    - Key players and market share
    - Consumer sentiment and barriers to adoption
    - Competitive landscape
  </description>
  <depth>deep</depth>
</hannah_create_task>

Result: Task created (task_xyz789).

⏱️ WAIT 2-3 MINUTES before checking status.

[Agent waits 3 minutes]

<check_task_status taskId="task_xyz789">

Result: Task completed! Hannah orchestrated Statista, GWI, and DataForSEO sub-agents.

<get_task_result taskId="task_xyz789">

Result: Comprehensive research report with sources and confidence levels.
```

### Example 2: Project Planning with Elena (API)

```
Agent: "Need to break down a Q2 campaign launch. Use Elena."

<elena_create_task>
  <description>
    Break down a Q2 product campaign launch into workstreams:
    - Product: New premium EV model
    - Target: German market, affluent early adopters
    - Timeline: Launch April 1st
    - Budget: €500k

    Provide detailed work breakdown with dependencies and risks.
  </description>
</elena_create_task>

Result: Task created (task_abc456).

⏱️ WAIT 2-3 MINUTES - Elena may delegate to Hannah for market research.

[Agent waits 3 minutes]

<check_task_status taskId="task_abc456">

Result: Completed! Elena delegated to Hannah for market data, then integrated findings.

<get_task_result taskId="task_abc456">

Result: Work breakdown with dependencies, risks, and resource needs informed by research.
```

### Example 3: Email-Based Research Request

```
Agent: "Send research request to Hannah via email"

<hannah_email>
  <to>hannah@sumike.ai</to>
  <subject>EV Market Research Request</subject>
  <body>
    Hi Hannah,

    I need comprehensive research on the German EV market for Q2 2026:
    1. Market size and growth projections
    2. Competitive landscape analysis
    3. Consumer sentiment (barriers and motivators)

    Please provide sources and confidence levels for all findings.

    Thanks!
  </body>
</hannah_email>

Result: Email sent. Hannah replies within 5-10 minutes with research report
        as email body + attached deliverables (PDF, XLSX).
```

### Example 4: Elena Delegates to Hannah

```
Agent: "Elena, plan the EV campaign launch"

<elena_create_task>
  <description>
    Create project plan for German EV campaign launch:
    - Product: Premium EV sedan
    - Launch date: April 1, 2026
    - Target audience: Affluent professionals, 35-55
    - Budget: €500k
  </description>
</elena_create_task>

Workflow:
1. Elena receives task
2. Elena identifies missing market context
3. Elena delegates research to Hannah (internal A2A)
4. Hannah executes research using premium data sources
5. Elena integrates findings into operational plan
6. Elena delivers: Work breakdown + dependencies + risk matrix + deliverables

Result: Comprehensive project plan informed by real market data
```

---

## Agent Personalities & Best Practices

### Working with Hannah

**Character:**
- Analytical, reflective, opinionated
- Values research integrity over speed
- Calls out weak data honestly
- "What is actually true?"

**Best Practices:**
- Be specific about research questions
- Specify required depth (quick lookup vs deep research)
- Ask for source attribution
- Expect critical assessment, not just data dumps

**Example Good Request:**
```
"Hannah, I need to validate whether 'sustainability' is a real
purchase driver for EVs in Germany, or if it's post-rationalized.
Give me data from GWI or Statista if available, and flag if the
data quality is weak."
```

### Working with Elena

**Character:**
- Direct, pragmatic, grounded
- Protects delivery through realism
- Challenges vague goals
- "What is actually doable?"

**Best Practices:**
- Provide clear goals and constraints upfront
- Specify dependencies you know about
- Ask for risk assessment
- Expect honest pushback on unrealistic plans

**Example Good Request:**
```
"Elena, break down a 6-week campaign launch:
- Product: New EV model
- Launch: April 1st
- Constraint: No dedicated PM resource
- Concern: Unclear target audience

Flag dependencies and risks."
```

---

## Multi-Agent Coordination

### Pattern 1: Sequential (Research → Planning)

```
Step 1: Agent requests research from Hannah
Step 2: Agent receives research findings
Step 3: Agent requests operational plan from Elena
Step 4: Agent integrates both outputs
```

### Pattern 2: Elena Auto-Delegates

```
Step 1: Agent requests project plan from Elena
Step 2: Elena detects missing market context
Step 3: Elena automatically delegates to Hannah
Step 4: Hannah returns research
Step 5: Elena integrates and delivers complete plan
```

### Pattern 3: Parallel Consultation

```
Step 1: Agent sends same context to both Hannah and Elena
Step 2: Hannah returns "What is true?" perspective
Step 3: Elena returns "What is doable?" perspective
Step 4: Agent synthesizes both viewpoints
```

---

## Cost & Rate Limits

### API Rate Limits
- **Hannah**: 60 requests/minute
- **Elena**: 60 requests/minute
- **Max concurrent requests**: 5 per agent

### Sokosumi Sub-Agent Costs

When Hannah or Elena orchestrate Sokosumi sub-agents:
- **Statista**: ~120 credits
- **GWI**: ~80 credits
- **DataForSEO**: ~60 credits
- **Apify**: ~40 credits

Hannah and Elena will inform you of estimated costs before executing.

---

## ⏱️ Timing Guidance

**CRITICAL for AI Agents:**

### API Task Processing

1. **After creating task**: Wait at least **2-3 minutes** before checking status
2. **If still processing**: Wait another **2-3 minutes** before checking again
3. **Total task time**: Typically **2-10 minutes** depending on complexity
4. **DO NOT**: Poll continuously every few seconds - tasks need time to complete

**Why?** Tasks involve:
- Initial processing and context loading (30 seconds)
- Research execution with sub-agents (2-10 minutes - MAIN WAIT TIME)
- Result synthesis and formatting (30 seconds - 1 minute)

### Email Requests
- **Typical response time**: 5-10 minutes
- **Complex research**: Up to 15 minutes
- **Expect email reply with attachments**

### Task Status States

| Status | Description | Next Action |
|--------|-------------|-------------|
| `DRAFT` | Task created but not started | System will auto-process |
| `READY` | Task queued for processing | Wait 2-3 minutes |
| `IN_PROGRESS` | Agent is working | Wait 2-3 minutes, then check again |
| `COMPLETED` | Task finished | Retrieve result |
| `FAILED` | Task failed | Check error message |

**AI Agent: ALWAYS wait 2-3 minutes after creating a task before checking status. Set timeouts of at least 5 minutes for API calls.**

---

## Available Tools

### `list_coworkers`

List available agents (Hannah, Elena).

**Parameters:** None

**Returns:**
- `coworkers`: Array of available agents with capabilities and status
- `count`: Number of agents found

**Example Response:**
```json
{
  "data": [
    {
      "id": "cow_hannah",
      "name": "Hannah Sumi",
      "role": "Marketing Research Specialist",
      "email": "hannah@sumike.ai"
    },
    {
      "id": "cow_elena",
      "name": "Elena",
      "role": "Operations & Project Orchestrator",
      "email": "elena@sumike.ai"
    }
  ]
}
```

### `hannah_create_task`

Create a research task for Hannah.

**Parameters:**
- `name` (required): Task title (max 120 chars)
- `description` (optional): Detailed task description with research questions
- `status` (optional): "DRAFT" | "READY" (default: "READY")

**Returns:**
- `taskId`: Task identifier (e.g., "task_xyz789")
- `status`: Initial task status
- `estimatedTime`: "2-10 minutes"
- `message`: Includes timing guidance

**⏱️ IMPORTANT**: Wait 2-3 minutes before checking status!

### `elena_create_task`

Create a planning task for Elena.

**Parameters:**
- `name` (required): Task title (max 120 chars)
- `description` (optional): Detailed planning requirements
- `status` (optional): "DRAFT" | "READY" (default: "READY")

**Returns:**
- `taskId`: Task identifier
- `status`: Initial task status
- `estimatedTime`: "2-10 minutes"
- `message`: Includes timing guidance

**⏱️ IMPORTANT**: Wait 2-3 minutes before checking status! Elena may delegate to Hannah for research.

### `check_task_status`

Check the status of a task.

**Parameters:**
- `taskId` (required): Task ID from create_task

**Returns:**
- `status`: "DRAFT" | "READY" | "IN_PROGRESS" | "COMPLETED" | "FAILED"
- `hasResult`: Whether result is available
- `message`: Status message with timing guidance

**⏱️ TIMING**: Wait 2-3 minutes after creating task before first check. If still IN_PROGRESS, wait another 2-3 minutes.

### `get_task_result`

Get the result of a completed task.

**Parameters:**
- `taskId` (required): Task ID from create_task

**Returns:**
- `result`: Task result data (research findings or operational plan)
- `status`: Task status (must be "COMPLETED")
- `completedAt`: Completion timestamp
- `deliverables`: Links to any generated files (PDF, XLSX, PPTX)

**Note**: Only works for completed tasks. Use `check_task_status` first to verify completion.

### `hannah_email`

Send email request to Hannah.

**Parameters:**
- `to` (required): Email address (default: hannah@sumike.ai)
- `subject` (required): Email subject line
- `body` (required): Email body with request details
- `cc` (optional): CC addresses
- `attachments` (optional): Attachment file paths

**Returns:**
- `status`: "sent"
- `messageId`: Email message ID
- `estimatedResponse`: Estimated response time

### `elena_email`

Send email request to Elena.

**Parameters:**
- `to` (required): Email address (default: elena@sumike.ai)
- `subject` (required): Email subject line
- `body` (required): Email body with request details
- `cc` (optional): CC addresses
- `attachments` (optional): Attachment file paths

**Returns:**
- `status`: "sent"
- `messageId`: Email message ID
- `estimatedResponse`: Estimated response time

### `check_hannah_status`

Check if Hannah is available.

**Returns:**
- `available`: true | false
- `responseTime`: Estimated response time
- `message`: Status message

### `check_elena_status`

Check if Elena is available.

**Returns:**
- `available`: true | false
- `responseTime`: Estimated response time
- `message`: Status message

---

## Error Handling

### API Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `401 Unauthorized` | Invalid or missing API key | Set correct API key in environment |
| `429 Rate Limited` | Exceeded 60 req/min | Wait 60 seconds before retrying |
| `503 Service Unavailable` | Agent temporarily down | Retry after 2-3 minutes or use email channel |
| `timeout` | Request took too long | Increase timeout for research tasks |

### Email Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Email not sent` | Invalid email address | Check HANNAH_EMAIL / ELENA_EMAIL config |
| `No response after 15 min` | Complex research task | Wait longer or check spam folder |
| `Bounce` | Email delivery failed | Verify email address and network |

---

## Troubleshooting

### "API key is missing"

**Solution**: Set `HANNAH_API_KEY` and/or `ELENA_API_KEY` in environment variables.

### "Hannah/Elena not responding"

**Solution**:
1. Check agent status using `check_hannah_status` or `check_elena_status`
2. Verify API endpoint is correct
3. Try alternative channel (API → Email or vice versa)

### "Sokosumi credits exhausted"

**Hannah/Elena will inform you:**
```
"I need to use Statista for this research, which requires 120 credits.
Your current Sokosumi balance is 50 credits. Please add credits at
sokosumi.com to continue."
```

**Solution**: Add credits to your Sokosumi account (if using premium data sources)

### "Rate limit exceeded"

**Solution**:
- Reduce request frequency (max 60/minute per agent)
- Use batch requests where possible
- Consider email channel for non-urgent requests

---

## Integration Patterns

### Pattern A: Research-First Workflow

```
1. Your agent identifies need for market data
2. Call hannah_research with specific questions
3. Wait for response (2-10 minutes)
4. Integrate findings into your agent's output
5. Optionally: Send to Elena for operational planning
```

### Pattern B: Planning-First Workflow

```
1. Your agent receives project request
2. Call elena_plan with requirements
3. Elena auto-delegates research to Hannah if needed
4. Receive comprehensive plan with market context
5. Execute or refine based on deliverables
```

### Pattern C: Parallel Advisory

```
1. Your agent faces strategic decision
2. Call hannah_research for market reality
3. Call elena_plan for operational feasibility
4. Compare responses: "What's true" vs "What's doable"
5. Make informed decision with both perspectives
```

---

## Security & Privacy

### API Keys
- API keys are scoped to specific agents (Hannah or Elena)
- Keys format: `sk-sumike-xxxxx`
- Maximum 5 active keys per contact
- Rotate keys every 90 days recommended

### Data Handling
- Conversation history stored in PostgreSQL (isolated per agent)
- Research results cached for 30 days
- Email attachments stored in Azure File Share
- No data shared between Hannah and Elena without explicit delegation

### Compliance
- GDPR compliant (data processing agreement available)
- SOC 2 Type II certified infrastructure
- Data residency: EU (Azure West Europe)

---

## Advanced Configuration

### Custom Endpoints

```bash
# Override default endpoints
export HANNAH_API_ENDPOINT=https://custom-hannah.your-domain.com/v1
export ELENA_API_ENDPOINT=https://custom-elena.your-domain.com/v1
```

### Proxy Configuration

```bash
# Route through proxy
export HTTPS_PROXY=https://your-proxy.com:8080
export NO_PROXY=localhost,127.0.0.1
```

### Timeout Settings

```bash
# Adjust timeouts (in seconds)
export HANNAH_TIMEOUT=300  # 5 minutes for research
export ELENA_TIMEOUT=180   # 3 minutes for planning
```

---

## API Reference (Quick Reference)

### Hannah API

**Endpoint**: `https://hannah.sumike.ai/v1/chat/completions`

**Authentication**: `Authorization: Bearer sk-sumike-xxxxx`

**Request Body**:
```json
{
  "messages": [
    {"role": "user", "content": "Your research request here"}
  ],
  "stream": false
}
```

**Response**:
```json
{
  "id": "msg_xxx",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Research findings..."
      }
    }
  ]
}
```

### Elena API

**Endpoint**: `https://elena.sumike.ai/v1/chat/completions`

Same format as Hannah API.

---

## Resources

- **Hannah & Elena Homepage**: https://sumike.ai
- **Serviceplan**: https://www.serviceplan.com
- **Sokosumi Marketplace**: https://sokosumi.com
- **Support**: support@sumike.ai

---

## Summary for AI Agents

**Quick Setup:**
1. Obtain API keys from Serviceplan (human task)
2. Set `HANNAH_API_KEY` and `ELENA_API_KEY` in environment
3. Use `hannah_research` for market research
4. Use `elena_plan` for project planning
5. Be patient — research tasks take 2-10 minutes
6. Integrate responses into your agent's workflow

**Key Principles:**
- Hannah validates ideas through research integrity ("What is true?")
- Elena protects delivery through realism ("What is doable?")
- Both agents can orchestrate Sokosumi sub-agents for premium data
- Elena auto-delegates to Hannah when market context is needed
- Support both API and email channels for flexibility

**Remember:**
- Research depth impacts response time
- Set realistic timeouts (3-5 minutes minimum)
- Hannah and Elena are professional coworkers, not assistants
- They will push back on vague requests or weak assumptions
- Cost transparency — they inform you before consuming credits

---

**Built by Serviceplan | Powered by Sokosumi**

*Professional AI coworkers for marketing research and operations planning*
