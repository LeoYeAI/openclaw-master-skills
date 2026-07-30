# SSE Event Reference

Detailed documentation for all Server-Sent Events (SSE) returned by the each::sense `/chat` endpoint.

## Event Format

Each event follows this format:
```
data: {"type": "event_type", ...fields}\n\n
```

Stream ends with:
```
data: [DONE]\n\n
```

---

## Event Types

### thinking_delta

Claude's reasoning as it streams in real-time. Use this to show users what the AI is thinking.

```json
{
  "type": "thinking_delta",
  "content": "Let me find the best model for portrait generation..."
}
```

| Field | Type | Description |
|-------|------|-------------|
| `content` | string | Incremental thinking text |

---

### status

Current operation being executed. Shows tool usage and parameters.

```json
{
  "type": "status",
  "message": "Searching for image generation models...",
  "tool_name": "search_models",
  "parameters": {"use_case": "text to image portrait"}
}
```

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | Human-readable status message |
| `tool_name` | string | Internal tool being used |
| `parameters` | object | Tool parameters (optional) |

---

### text_response

Text content from the AI (explanations, answers, plans).

```json
{
  "type": "text_response",
  "content": "I'll create a stunning portrait for you with cinematic lighting and a warm mood."
}
```

| Field | Type | Description |
|-------|------|-------------|
| `content` | string | Text response content |

---

### generation_response

Generated media URL (image or video). This is the primary output event.

```json
{
  "type": "generation_response",
  "url": "https://storage.eachlabs.ai/outputs/abc123.png",
  "generations": ["https://storage.eachlabs.ai/outputs/abc123.png"],
  "total": 1,
  "tool_name": "execute_model",
  "model": "nano-banana-pro"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | Primary output URL |
| `generations` | array | All generated URLs |
| `total` | number | Total number of generations |
| `tool_name` | string | Tool that generated output |
| `model` | string | Model used for generation |

---

### clarification_needed

AI needs more information to proceed. Present options to the user.

```json
{
  "type": "clarification_needed",
  "question": "What type of edit would you like to make to this image?",
  "options": [
    "Remove the background",
    "Apply a style transfer",
    "Upscale to higher resolution",
    "Add or modify elements"
  ],
  "context": "I can see you've uploaded an image, but I need to understand what changes you'd like."
}
```

| Field | Type | Description |
|-------|------|-------------|
| `question` | string | The question to ask the user |
| `options` | array | Suggested options (can be displayed as buttons) |
| `context` | string | Additional context about the clarification |

**Handling:** Display the question and options to the user. Send their response in a follow-up request with the same `session_id`.

---

### web_search_query

Web search being executed.

```json
{
  "type": "web_search_query",
  "query": "best AI video generation models 2024",
  "recency": "month"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `query` | string | Search query |
| `recency` | string | Time filter (day, week, month, year) |

---

### web_search_citations

Citations from web search results.

```json
{
  "type": "web_search_citations",
  "citations": [
    "https://example.com/ai-video-comparison",
    "https://techblog.com/veo3-review"
  ],
  "count": 2
}
```

| Field | Type | Description |
|-------|------|-------------|
| `citations` | array | URLs of sources cited |
| `count` | number | Number of citations |

---

### workflow_created

New workflow was created for complex multi-step generation.

```json
{
  "type": "workflow_created",
  "workflow_id": "wf_abc123",
  "version_id": "v1",
  "input_schema": {
    "properties": {
      "character_description": {
        "type": "text",
        "required": true,
        "default_value": ""
      }
    }
  },
  "steps_count": 5
}
```

| Field | Type | Description |
|-------|------|-------------|
| `workflow_id` | string | Unique workflow identifier |
| `version_id` | string | Workflow version |
| `input_schema` | object | Schema for workflow inputs |
| `steps_count` | number | Number of steps in workflow |

---

### workflow_fetched

Existing workflow was loaded (when `workflow_id` is provided in request).

```json
{
  "type": "workflow_fetched",
  "workflow_name": "Product Video Generator",
  "existing_steps": 3,
  "existing_definition": {...}
}
```

| Field | Type | Description |
|-------|------|-------------|
| `workflow_name` | string | Name of the workflow |
| `existing_steps` | number | Number of existing steps |
| `existing_definition` | object | Current workflow definition |

---

### workflow_built

Workflow definition was constructed.

```json
{
  "type": "workflow_built",
  "steps_count": 4,
  "definition": {
    "version": "v1",
    "input_schema": {...},
    "steps": [...]
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `steps_count` | number | Number of steps |
| `definition` | object | Full workflow definition |

---

### workflow_updated

Workflow was pushed to the EachLabs API.

```json
{
  "type": "workflow_updated",
  "success": true,
  "workflow_id": "wf_abc123",
  "version_id": "v1",
  "definition": {...}
}
```

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether update succeeded |
| `workflow_id` | string | Workflow identifier |
| `version_id` | string | Version identifier |
| `definition` | object | Updated definition |

---

### execution_started

Workflow execution has begun.

```json
{
  "type": "execution_started",
  "execution_id": "exec_xyz789",
  "workflow_id": "wf_abc123"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `execution_id` | string | Unique execution identifier |
| `workflow_id` | string | Workflow being executed |

---

### execution_progress

Progress update during workflow execution. Sent approximately every 5 seconds.

```json
{
  "type": "execution_progress",
  "step_id": "step2",
  "step_status": "completed",
  "output": "https://storage.eachlabs.ai/outputs/step2.png",
  "model": "nano-banana-pro",
  "completed_steps": 2,
  "total_steps": 5
}
```

| Field | Type | Description |
|-------|------|-------------|
| `step_id` | string | Current step identifier |
| `step_status` | string | Step status (running, completed, failed) |
| `output` | string | Step output URL (if available) |
| `model` | string | Model used for this step |
| `completed_steps` | number | Steps completed so far |
| `total_steps` | number | Total steps in workflow |

---

### execution_completed

Workflow execution finished successfully.

```json
{
  "type": "execution_completed",
  "execution_id": "exec_xyz789",
  "status": "completed",
  "output": "https://storage.eachlabs.ai/outputs/final.mp4",
  "all_outputs": {
    "step1": "https://storage.eachlabs.ai/outputs/step1.png",
    "step2": "https://storage.eachlabs.ai/outputs/step2.png",
    "step3": "https://storage.eachlabs.ai/outputs/final.mp4"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `execution_id` | string | Execution identifier |
| `status` | string | Final status (completed, failed) |
| `output` | string | Final output URL |
| `all_outputs` | object | All step outputs keyed by step_id |

---

### tool_call

Details of a tool being called. Useful for debugging and transparency.

```json
{
  "type": "tool_call",
  "name": "execute_model",
  "input": {
    "model_name": "nano-banana-pro",
    "inputs": {
      "prompt": "A beautiful woman portrait...",
      "aspect_ratio": "1:1"
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Tool name |
| `input` | object | Tool input parameters |

---

### message

Informational message from the agent.

```json
{
  "type": "message",
  "content": "Your video is being processed. This typically takes 2-3 minutes."
}
```

| Field | Type | Description |
|-------|------|-------------|
| `content` | string | Message content |

---

### complete

Final event with summary. Always sent when stream completes successfully.

```json
{
  "type": "complete",
  "task_id": "chat_1708345678901",
  "status": "ok",
  "tool_calls": [
    {"name": "search_models", "result": "success"},
    {"name": "get_model_details", "result": "success"},
    {"name": "execute_model", "result": "success", "model": "nano-banana-pro"}
  ],
  "generations": ["https://storage.eachlabs.ai/outputs/abc123.png"],
  "model": "nano-banana-pro"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | string | Unique task identifier |
| `status` | string | Final status (ok, awaiting_input, error) |
| `tool_calls` | array | Summary of all tool calls |
| `generations` | array | All generated output URLs |
| `model` | string | Primary model used |

**Status values:**
- `ok` - Completed successfully
- `awaiting_input` - Waiting for user clarification
- `error` - An error occurred

---

### error

An error occurred during processing.

```json
{
  "type": "error",
  "message": "Failed to generate image: Invalid aspect ratio"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | Error message |

---

## Event Flow Examples

### Simple Image Generation

```
thinking_delta → "I'll create a beautiful portrait..."
status → "Searching for models..."
status → "Getting model details..."
status → "Generating with nano-banana-pro..."
generation_response → {url: "https://..."}
complete → {status: "ok", generations: [...]}
[DONE]
```

### Clarification Flow

```
thinking_delta → "I see an image, but need to know what edit..."
clarification_needed → {question: "What edit?", options: [...]}
complete → {status: "awaiting_input"}
[DONE]
```

### Workflow Execution

```
thinking_delta → "Creating a multi-step workflow..."
status → "Searching for models..."
workflow_created → {workflow_id: "wf_123", steps_count: 5}
execution_started → {execution_id: "exec_456"}
execution_progress → {completed_steps: 1, total_steps: 5}
execution_progress → {completed_steps: 2, total_steps: 5}
execution_progress → {completed_steps: 3, total_steps: 5}
execution_progress → {completed_steps: 4, total_steps: 5}
execution_completed → {output: "https://...", all_outputs: {...}}
complete → {status: "ok"}
[DONE]
```

### Web Search

```
thinking_delta → "Let me search for current information..."
web_search_query → {query: "best AI models 2024"}
status → "Searching the web..."
web_search_citations → {citations: [...], count: 3}
text_response → "Based on current information..."
complete → {status: "ok"}
[DONE]
```
