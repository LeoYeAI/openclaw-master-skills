---
name: each-sense
description: each::sense is the intelligent layer for generative media. A unified AI agent that generates marketing assets, ads, product images, videos, and creative content. It knows all AI models and automatically selects the best one for your task. Use for any creative content generation request.
metadata:
  author: eachlabs
  version: "1.0"
---

# each::sense - Intelligent Layer for Generative Media

each::sense is a unified AI agent that can generate images, videos, build workflows, search the web, and hold conversational interactions. It uses Claude as the orchestrator with access to 200+ AI models.

**Use each::sense when the user needs:**
- Marketing assets and ad creatives
- Product images and e-commerce visuals
- Video content (ads, UGC, social media)
- Any creative content generation
- Multi-step workflows combining multiple AI models

## Authentication

```
Header: X-API-Key: <your-api-key>
```

Get your API key at [eachlabs.ai](https://eachlabs.ai) → API Keys.

Set the `EACHLABS_API_KEY` environment variable.

## Base URL

```
https://sense.eachlabs.run
```

## Quick Start

```bash
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Generate a portrait of a woman with golden hour lighting",
    "mode": "max"
  }'
```

The endpoint returns Server-Sent Events (SSE) with real-time progress and the final generated output.

## Request Schema

```json
{
  "message": "string (required) - User's request",
  "session_id": "string (optional) - Session ID for conversation history and multi-turn chats",
  "mode": "string (optional, default: 'max') - Quality mode: 'max' or 'eco'",
  "behavior": "string (optional, default: 'agent') - Behavior: 'agent', 'plan', or 'ask'",
  "model": "string (optional, default: 'auto') - Model slug or 'auto' for AI selection",
  "image_urls": "array[string] (optional) - Image URLs for editing/processing",
  "workflow_id": "string (optional) - Enables workflow building mode",
  "version_id": "string (optional) - Required with workflow_id",
  "web_search": "boolean (optional, default: true) - Enable/disable web search",
  "enable_safety_checker": "boolean (optional, default: true) - Set to false to allow NSFW content generation"
}
```

### Parameter Details

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `message` | string | required | Natural language request |
| `session_id` | string | null | Session ID for conversation history. Use to continue previous chats, handle clarifications, and iteratively refine outputs |
| `mode` | string | "max" | `max` = best quality, `eco` = fastest/cheapest |
| `behavior` | string | "agent" | `agent` = auto-execute, `plan` = explain first, `ask` = clarify first |
| `model` | string | "auto" | Specific model slug or "auto" for AI selection |
| `image_urls` | array | null | URLs of images to process/edit |
| `workflow_id` | string | null | Enables workflow building mode |
| `version_id` | string | null | Workflow version, required with workflow_id |
| `web_search` | boolean | true | Allow web search for information |
| `enable_safety_checker` | boolean | true | Set to false to allow NSFW content generation |

## Modes

Agents can ask users to choose between quality and speed/cost before generating content:
- **"Do you want fast & cheap, or high quality?"**
- **"Quick draft or premium output?"**

### MAX Mode (Default)
Uses the highest quality models available. Best for final outputs, client-facing work, and when quality matters most.

```bash
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{"message": "Create a product shot", "mode": "max"}'
```

### ECO Mode
Uses fast, cost-effective models. Best for prototyping, drafts, and high-volume generation.

```bash
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{"message": "Create a product shot", "mode": "eco"}'
```

## Behaviors

### Agent (Default)
Automatically executes the request, selecting the best model and generating output.

```json
{"message": "Generate a sunset video", "behavior": "agent"}
```

### Plan
Explains what it will do before executing. Good for complex requests where you want to review the approach.

```json
{"message": "Create a marketing video for my bakery", "behavior": "plan"}
```

### Ask
Always asks clarifying questions before proceeding. Good when you want maximum control.

```json
{"message": "Generate a portrait", "behavior": "ask"}
```

## Session Management

Use `session_id` to maintain conversation history and context across multiple requests. This enables:

- **Multi-turn conversations**: Follow-up on previous requests without repeating context
- **Iterative refinement**: Ask for modifications to previously generated content
- **Clarification flows**: Respond to `clarification_needed` events and continue the conversation
- **Context awareness**: The AI remembers previous generations, preferences, and instructions

### How It Works

Provide any unique string as `session_id` in your requests. All requests with the same `session_id` share conversation history.

```bash
# Use any unique string as session_id
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Generate a portrait",
    "session_id": "my-chat-session-123"
  }'
```

### Example: Iterative Generation

```bash
# First request - generate initial image
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Generate a logo for a coffee shop called Brew Lab",
    "session_id": "logo-project-001"
  }'

# Follow-up - modify the result (same session_id)
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Make it more minimalist and change the color to dark green",
    "session_id": "logo-project-001"
  }'

# Another follow-up - request variation (same session_id)
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Create 3 variations of this logo",
    "session_id": "logo-project-001"
  }'
```

### Example: Handling Clarifications

```bash
# Ambiguous request - AI will ask for clarification
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Edit this image",
    "session_id": "edit-task-001",
    "image_urls": ["https://example.com/photo.jpg"]
  }'
# Response: clarification_needed event asking what edit to make

# Respond to clarification (same session_id)
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Remove the background and make it transparent",
    "session_id": "edit-task-001",
    "image_urls": ["https://example.com/photo.jpg"]
  }'
```

### Session Persistence

- Sessions are persisted and can be resumed at any time
- Each session maintains full conversation history
- Use sessions to build chat-like experiences with each::sense
- You control the session ID - use any unique string for related requests

## Use Case Examples

### 1. Image Generation

```bash
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Generate a professional headshot of a business executive, studio lighting",
    "mode": "max"
  }'
```

### 2. Video Generation

```bash
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Create a 5 second video of a sunset over the ocean",
    "mode": "max"
  }'
```

### 3. Image Editing (with uploaded image)

```bash
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Remove the background from this image",
    "image_urls": ["https://example.com/my-photo.jpg"]
  }'
```

### 4. Image-to-Video Animation

```bash
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Animate this image with gentle camera movement",
    "image_urls": ["https://example.com/landscape.jpg"]
  }'
```

### 5. Direct Model Execution (skip AI selection)

```bash
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "A cyberpunk city at night with neon lights",
    "model": "flux-2-max"
  }'
```

### 6. Product Photography

```bash
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Generate a product shot of a coffee mug on a wooden table with morning light",
    "mode": "max"
  }'
```

### 7. Marketing Assets

```bash
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Create a social media ad for a fitness app, show someone working out with energetic vibes",
    "mode": "max"
  }'
```

### 8. Multi-Turn Conversation

```bash
# First request with a session_id
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Edit this image",
    "session_id": "user-123-chat",
    "image_urls": ["https://example.com/photo.jpg"]
  }'

# Response includes clarification_needed asking what edit to make
# Follow-up with same session_id
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Remove the background",
    "session_id": "user-123-chat",
    "image_urls": ["https://example.com/photo.jpg"]
  }'
```

### 9. Complex Workflow (UGC Video)

```bash
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Create a 30 second UGC video with a consistent presenter explaining why fitness is important. The presenter is a 30-year-old fit woman with brown hair in workout clothes, gym background.",
    "mode": "max"
  }'
```

## SSE Response Format

The endpoint returns Server-Sent Events (SSE) with `Content-Type: text/event-stream`.

Each event has the format:
```
data: {"type": "event_type", ...fields}\n\n
```

Stream ends with:
```
data: [DONE]\n\n
```

### Event Types

| Event | Description |
|-------|-------------|
| `thinking_delta` | AI reasoning in real-time |
| `status` | Current operation being executed |
| `text_response` | Text content (explanations, answers) |
| `generation_response` | Generated media URL |
| `clarification_needed` | AI needs more information |
| `web_search_query` | Web search being executed |
| `web_search_citations` | Citations from search results |
| `workflow_created` | New workflow was created |
| `workflow_fetched` | Existing workflow was loaded |
| `workflow_built` | Workflow definition constructed |
| `workflow_updated` | Workflow pushed to API |
| `execution_started` | Workflow execution began |
| `execution_progress` | Progress update during execution |
| `execution_completed` | Workflow execution finished |
| `tool_call` | Details of tool being called |
| `message` | Informational message |
| `complete` | Final event with summary |
| `error` | An error occurred |

### Key Event Examples

#### generation_response
Generated media URL (the primary output):
```json
{
  "type": "generation_response",
  "url": "https://storage.eachlabs.ai/outputs/abc123.png",
  "generations": ["https://storage.eachlabs.ai/outputs/abc123.png"],
  "total": 1,
  "model": "nano-banana-pro"
}
```

#### clarification_needed
AI needs more information:
```json
{
  "type": "clarification_needed",
  "question": "What type of edit would you like to make to this image?",
  "options": ["Remove the background", "Apply a style transfer", "Upscale to higher resolution"],
  "context": "I can see your image but need to know the specific edit you want."
}
```

#### complete
Final event with summary:
```json
{
  "type": "complete",
  "task_id": "chat_1708345678901",
  "status": "ok",
  "generations": ["https://storage.eachlabs.ai/outputs/abc123.png"],
  "model": "nano-banana-pro"
}
```

#### error
An error occurred:
```json
{
  "type": "error",
  "message": "Failed to generate image: Invalid aspect ratio"
}
```

## Model Aliases

Common shorthand names that are automatically resolved:

| Alias | Resolves To |
|-------|-------------|
| flux max | flux-2-max |
| flux pro | flux-2-pro |
| gpt image | gpt-image-1-5 |
| nano banana pro | nano-banana-pro |
| seedream | seedream-4-5 |
| gemini imagen | gemini-imagen-4 |
| kling 3 | kling-3-0 |
| veo | veo3-1-text-to-video-fast |
| sora | sora-2 |
| hailuo | hailuo-2-3 |

## Error Handling

### HTTP Errors

| Code | Response | Cause |
|------|----------|-------|
| 401 | `{"detail": "API key is required."}` | Missing or invalid API key |
| 500 | `{"detail": "Error message"}` | Internal server error |
| 503 | `{"detail": "ChatAgent not available"}` | Service temporarily unavailable |

### Streaming Errors

```json
{"type": "error", "message": "Failed to execute model: Invalid parameters"}
```

| Error Message | Cause | Solution |
|--------------|-------|----------|
| `Failed to create prediction: HTTP 422` | Insufficient account balance | Top up at eachlabs.ai |
| `Failed to execute model: Invalid parameters` | Missing/invalid inputs | Check model parameters |
| `Model not found` | Invalid model slug | Use "auto" or valid slug |
| `Workflow execution timed out` | Exceeded 1 hour limit | Split into smaller workflows |

## Timeouts

**Client timeout recommendation:** Set your HTTP client timeout to **minimum 10 minutes**. Complex use cases may require running multiple AI models sequentially (e.g., 10+ model executions for UGC videos), which can take several minutes to complete.

```bash
# curl example with 10 minute timeout
curl --max-time 600 -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{"message": "Create a complex UGC video..."}'
```

**Platform limits:**
- Streaming connections timeout after 1 hour of inactivity
- Workflow executions timeout after 1 hour

## Rate Limits

- Depends on your EachLabs API key tier

## Best Practices

1. **Use session_id** for multi-turn conversations to maintain context
2. **Use ECO mode** for prototyping and cost-sensitive applications
3. **Use specific model** when you know exactly what you want (faster execution)
4. **Handle clarification events** - respond with requested information in the same session
5. **Provide clear prompts** - be specific about style, mood, and composition
6. **Monitor SSE events** - use `thinking_delta` for progress, `generation_response` for output
