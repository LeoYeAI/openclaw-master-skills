# Streaming & Chunking

> Source: https://docs.openclaw.ai/concepts/streaming

## Block Streaming (Channel Messages)

- Assistant deltas are streamed from pi-agent-core.
- Block streaming emits partial replies to the chat channel as separate message "blocks".
- Controlled by `agents.defaults.blockStreamingDefault` (default: `"off"`).
- Break points: `text_end` or `message_end`.

## Chunking Algorithm (Low/High Bounds)

- Messages are split into chunks based on configurable low/high character bounds.
- `agents.defaults.blockStreamingChunk` controls chunk size parameters.
- Long replies are automatically split to stay within channel message limits.

## Coalescing (Merge Streamed Blocks)

- `agents.defaults.blockStreamingCoalesce`: merge multiple streamed blocks back into a single message after completion.
- Reduces notification noise while preserving progressive display during streaming.

## Human-Like Pacing Between Blocks

- Configurable delay between streamed blocks for a more natural chat experience.
- Typing indicators fire during delays.

## "Stream Chunks or Everything"

- When block streaming is off, the full reply is sent as a single message after completion.
- When on, partial chunks are sent progressively as they become available.

## Preview Streaming Modes

### Channel Mapping

Different channels support different preview modes:

| Channel | Preview Support |
|---|---|
| WebChat / Control UI | Full streaming preview |
| Telegram | Draft bubble editing |
| WhatsApp | No preview (blocks only) |
| Discord | Message editing |

### Runtime Behavior

- Streaming deltas are emitted as `assistant` events on the WS protocol.
- Clients choose whether to display real-time deltas or wait for blocks.
- Channel adapters handle the translation to channel-specific UX.
