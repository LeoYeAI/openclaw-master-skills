# Thinking Levels & Verbose Directives

> Source: https://docs.openclaw.ai/tools/thinking

## Thinking Levels

### What It Does

Inline directive in any inbound body: `/t <level>`, `/think:<level>`, or `/thinking <level>`.

### Levels

| Level | Mapped To | Notes |
|---|---|---|
| `off` | Disable thinking | — |
| `minimal` | "think" | — |
| `low` | "think hard" | — |
| `medium` | "think harder" | — |
| `high` | "ultrathink" (max budget) | — |
| `xhigh` | "ultrathink+" | GPT-5.2 + Codex models only |
| `adaptive` | Provider-managed adaptive budget | Supported for Anthropic Claude 4.6 |

Aliases: `x-high`, `x_high`, `extra-high`, `extra high`, `extra_high` → `xhigh`. `highest`, `max` → `high`.

### Provider Notes

- **Anthropic Claude 4.6**: defaults to `adaptive` when no explicit thinking level is set.
- **Z.AI** (`zai/*`): only supports binary thinking (on/off). Any non-off level treated as `on` (mapped to `low`).
- **Moonshot** (`moonshot/*`): maps `/think off` to `thinking: { type: "disabled" }` and any non-off level to `thinking: { type: "enabled" }`. When thinking is enabled, Moonshot only accepts `tool_choice auto|none`; OpenClaw normalizes incompatible values to `auto`.

### Resolution Order

1. Inline directive on the message (applies only to that message).
2. Session override (set by sending a directive-only message).
3. Global default (`agents.defaults.thinkingDefault` in config).
4. Fallback: `adaptive` for Anthropic Claude 4.6, `low` for other reasoning-capable models, `off` otherwise.

### Setting a Session Default

- Send a message that is only the directive: `/think:medium` or `/t high`.
- Sticks for the current session; cleared by `/think:off` or session idle reset.
- Confirmation reply is sent ("Thinking level set to high." / "Thinking disabled.").
- Invalid levels are rejected with a hint.
- Send `/think` (no argument) to see the current level.

---

## Verbose Directives

**Commands**: `/verbose` or `/v`

### Levels

| Level | Behavior |
|---|---|
| `on` (minimal) | Tool call names/args shown as separate bubbles when started |
| `full` | Tool outputs also forwarded after completion (truncated) |
| `off` (default) | Only tool failure summaries visible |

- `/verbose off` stores explicit session override; clear via Sessions UI by choosing `inherit`.
- Inline directive affects only that message.
- Send `/verbose` (no argument) to see current level.
- Toggling `/verbose on|full|off` while a run is in-flight applies to subsequent tool bubbles.

---

## Reasoning Visibility

**Commands**: `/reasoning` or `/reason`

### Levels

| Level | Behavior |
|---|---|
| `on` | Reasoning sent as separate message prefixed with "Reasoning:" |
| `off` | Reasoning hidden |
| `stream` | Telegram only: streams reasoning into draft bubble while generating |

- Send `/reasoning` (no argument) to see current level.
