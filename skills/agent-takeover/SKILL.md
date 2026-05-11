---
name: agent-takeover
description: How to perform a live agent takeover of the Clawfinger voice gateway — dial, inject greetings, handle turns, release, and observe handback. Covers timing, endpoints, the WebSocket protocol, and includes a human-guided test case.
metadata:
  openclaw:
    emoji: "\U0001F3AF"
    skillKey: agent-takeover
    requires:
      - plugin:clawfinger
---

# Agent Takeover — Full Lifecycle Guide

How an external agent (OpenClaw plugin, custom script, or any WebSocket client) takes control of a live phone call, handles conversation turns directly, and hands back to the local LLM.

## Architecture Overview

```
Caller  <-->  Phone App  <-->  Gateway /api/turn  <-->  Local LLM
                                      |
                                      +-- (takeover) --> Agent WS
```

Normal flow: phone sends audio to `/api/turn`, gateway runs ASR → LLM → TTS, returns audio.

Takeover flow: after `takeover`, gateway sends `turn.request` to the agent WebSocket instead of calling the local LLM. The agent replies with text, gateway runs TTS, returns audio to phone.

## Endpoints Used

### WebSocket (primary — full bidirectional control)

**`WS /api/agent/ws`** — No authentication required on the WebSocket itself. Connects, receives all bus events, and sends commands.

| Send (agent → gateway) | Fields | Description |
|-------------------------|--------|-------------|
| `dial` | `number` | Dial outbound call via ADB |
| `inject` | `text`, `session_id` | Queue TTS message for next turn poll |
| `takeover` | `session_id` | Take over LLM for this session |
| `release` | `session_id` | Hand back to local LLM |
| `hangup` | `session_id` (optional) | Force hang up call + end session |
| `get_call_state` | `session_id` | Query conversation history and state |
| `end_session` | `session_id` | Mark session ended without phone hangup |
| `inject_context` | `session_id`, `context` | Push knowledge into LLM context |
| `clear_context` | `session_id` | Remove injected knowledge |
| `ping` | — | Heartbeat |

| Receive (gateway → agent) | Fields | Description |
|----------------------------|--------|-------------|
| `dial.ack` | `ok`, `detail` | Dial result |
| `takeover.ack` | `ok`, `session_id` | Takeover confirmed |
| `release.ack` | `ok`, `session_id` | Release confirmed |
| `hangup.ack` | `ok`, `detail`, `session_id` | Hangup result |
| `turn.request` | `session_id`, `transcript`, `request_id` | **Takeover only** — caller spoke, agent must reply |
| `turn.started` | `session_id` | Turn processing began |
| `turn.transcript` | `transcript` | ASR result |
| `turn.reply` | `reply` | LLM/agent reply text |
| `turn.complete` | `metrics`, `transcript`, `reply`, `model` | Turn finished |
| `session.ended` | `session_id` | Session ended (stale sweep, hangup, or explicit end) |

### REST (alternative — no persistent connection needed)

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/call/dial` | `{"number": "+49..."}` — dial via ADB |
| `POST` | `/api/call/hangup` | `{"session_id": "..."}` — force hangup |
| `POST` | `/api/call/inject` | `{"text": "...", "session_id": "..."}` — inject TTS |
| `GET` | `/api/agent/sessions` | List active session IDs |
| `GET` | `/api/agent/call/{sid}` | Full call state (history, instructions, takeover) |
| `POST` | `/api/agent/context/{sid}` | `{"context": "..."}` — inject knowledge |

**REST cannot do takeover.** Takeover requires the WebSocket for real-time `turn.request` / reply exchange. REST is fine for dial, inject, hangup, and observation.

## Takeover Turn Protocol

During takeover, the gateway replaces the local LLM with the agent for response generation:

```
Phone → /api/turn (audio) → Gateway ASR → transcript
                                              ↓
                           Gateway sends to Agent WS:
                           {"type": "turn.request",
                            "session_id": "abc123",
                            "transcript": "what caller said",
                            "request_id": "unique-id"}
                                              ↓
                           Agent replies on same WS:
                           {"reply": "agent's response",
                            "request_id": "unique-id"}
                                              ↓
                           Gateway TTS → audio → Phone
```

### Critical: `request_id` correlation

The agent **must** echo back the `request_id` from the `turn.request`. Without it, the gateway cannot match the reply to the pending turn and the request times out.

```json
// Gateway sends:
{"type": "turn.request", "session_id": "abc", "transcript": "hello", "request_id": "a1b2c3"}

// Agent must reply:
{"reply": "Hi there!", "request_id": "a1b2c3"}
```

No `type` field needed in the reply — just `reply` + `request_id`.

### Timeout and fallback

If the agent doesn't reply within the timeout (default 60s, configurable via `agent_takeover_timeout` in config), the gateway falls back to the local LLM for **that single turn**. The takeover remains active — the next turn will try the agent again.

## Timing Model

Understanding timing is critical for a smooth takeover experience.

### Phone polling cadence

The phone app polls `/api/turn` in a tight loop:
1. Record audio chunk (~2-5s of speech)
2. POST to `/api/turn`
3. Wait for response (ASR + LLM/agent + TTS)
4. Play response audio
5. Go to step 1

The phone does NOT poll on a fixed interval — it sends the next turn as soon as playback finishes and new audio is captured. Typical turn cycle: 3-8 seconds.

### Inject timing

`inject` queues a pre-synthesized TTS message. It's delivered on the **next** `/api/turn` poll, **before** ASR/LLM processing:

```
Agent injects "Hello!" at T=0
  ↓
Phone polls /api/turn at T=3  (next natural poll)
  ↓
Gateway sees pending inject → returns inject audio immediately (skips ASR/LLM)
  ↓
Phone plays "Hello!" → polls again
```

**Key implications:**
- Inject is NOT instant — there's a delay of up to one poll cycle (3-8s)
- During takeover, the phone is usually waiting for the agent's reply, so the next poll happens quickly after the agent responds
- Multiple injects queue up — each delivered on successive polls
- Inject skips ASR entirely — the phone's recorded audio is ignored for that poll

### Takeover timing

```
T=0    Agent sends {"type": "takeover", "session_id": "..."}
T=0    Gateway immediately routes future turns to agent
T=0    Agent gets {"type": "takeover.ack", "ok": true}
T=3-8  Phone polls /api/turn → gateway ASR → turn.request sent to agent
T=3-8  Agent replies → gateway TTS → phone plays agent's response
```

Takeover takes effect instantly on the gateway side. The first `turn.request` arrives on the next phone poll.

### Release timing

```
T=0    Agent sends {"type": "release", "session_id": "..."}
T=0    Gateway removes takeover → local LLM handles future turns
T=0    Agent gets {"type": "release.ack", "ok": true}
T=3-8  Phone polls /api/turn → local LLM responds (no more turn.requests to agent)
```

Release is also instant. The agent continues receiving bus events (turn.complete, etc.) but no longer gets `turn.request` messages.

### Inject + Takeover ordering

When you inject a greeting AND takeover in quick succession:

```
T=0.0  Agent injects greeting text
T=0.5  Agent sends takeover
T=3    Phone polls → gets inject (greeting plays) — takeover is active but no turn.request yet
T=8    Phone polls again → NOW it's a takeover turn → turn.request sent to agent
```

The inject is consumed first (it takes priority in the turn endpoint), then takeover kicks in on the subsequent poll. This is the correct order for "inject greeting then take over."

### Dial-to-first-turn latency

```
T=0     Agent sends dial command
T=0     ADB broadcast sent to phone
T=1-3   Phone initiates outbound call
T=5-30  Callee picks up (depends on the person)
T=+1    Phone detects call connected, sends first /api/turn (greeting)
T=+2    Gateway processes greeting (forced_reply → TTS only, no ASR/LLM)
T=+5    Greeting plays, phone captures first real audio
T=+8    First real turn arrives at gateway
```

Total dial-to-first-real-turn: 10-40 seconds depending on pickup time.

## Session Lifecycle

Sessions have a TTL of **60 seconds** of inactivity (configurable via `session_ttl`). The phone polls every 3-8s during a call, so active calls never hit the TTL. But if:

- The phone crashes or loses USB connection
- The caller hangs up and the phone doesn't send `/api/session/end`

...the session auto-ends after 60s of no polls.

**Session detection after dial:** After dialing, the agent needs the session ID. Options:
1. **Watch bus events** — a `turn.started` event with `session_id` arrives when the call connects
2. **Poll `GET /api/agent/sessions`** — check for new session IDs
3. **Send `get_call_state`** — if you know the session ID

Option 1 (events) is most reliable and fastest.

## Complete Takeover Lifecycle

```
1. CONNECT     ws://gateway:8996/api/agent/ws
2. DIAL        {"type": "dial", "number": "+49..."}
   WAIT        for dial.ack (ok: true)
3. DISCOVER    watch events for session_id (turn.started or session.started)
4. INJECT      {"type": "inject", "session_id": "...", "text": "Custom greeting"}
5. TAKEOVER    {"type": "takeover", "session_id": "..."}
   WAIT        for takeover.ack (ok: true)
6. HANDLE      receive turn.request → reply with {reply, request_id}
   REPEAT      for N turns
7. RELEASE     {"type": "release", "session_id": "..."}
   WAIT        for release.ack (ok: true)
8. OBSERVE     watch turn.complete events → model != "agent" confirms local LLM resumed
9. HANGUP      {"type": "hangup", "session_id": "..."} (optional — end call)
```

## Error Handling

| Scenario | What happens |
|----------|-------------|
| Agent WS disconnects during takeover | All takeovers auto-released, local LLM resumes |
| Agent doesn't reply within 60s | That turn falls back to local LLM; takeover stays active for next turn |
| Session ends during takeover | `session.ended` event; further turn.requests stop |
| Multiple agents take over same session | Last takeover wins (overwrites previous) |
| Takeover of non-existent session | `takeover.ack` with `ok: false` |
| Release without takeover | `release.ack` with `ok: false` |

## OpenClaw Plugin (Clawfinger)

If using the Clawfinger OpenClaw plugin, you don't need raw WebSocket code. The plugin tools map directly:

| Lifecycle step | Plugin tool |
|----------------|-------------|
| Dial | `clawfinger_dial` |
| Check sessions | `clawfinger_sessions` |
| Inspect state | `clawfinger_call_state` |
| Inject greeting | `clawfinger_inject` |
| Take over | `clawfinger_takeover` |
| Wait for caller | `clawfinger_turn_wait` — blocks until caller speaks, returns transcript + request_id |
| Reply to caller | `clawfinger_turn_reply` — send response text with the request_id |
| Release | `clawfinger_release` |
| Hang up | `clawfinger_hangup` |

**Takeover tool workflow:**
```
clawfinger_takeover(session_id)     → "Takeover active."
clawfinger_turn_wait()              → {transcript: "...", request_id: "abc123"}
clawfinger_turn_reply(request_id, reply)  → "Reply sent."
clawfinger_turn_wait()              → next turn...
clawfinger_turn_reply(...)          → ...
clawfinger_release(session_id)      → "Released."
```

Slash commands: `/clawfinger dial +49...`, `/clawfinger takeover <sid>`, `/clawfinger release <sid>`, `/clawfinger hangup`.

---

## Test Case: Human-Guided Takeover (3 turns)

A complete test walkthrough. Requires: gateway running, phone connected via ADB, a real phone number to call.

### Prerequisites

- Gateway running on `127.0.0.1:8996`
- Phone connected via ADB (`adb devices` shows device)
- ADB reverse active (`adb reverse tcp:8996 tcp:8996`)
- `websockets` Python package installed (`pip install websockets`)

### Test Script

Save as `test_takeover.py` in the gateway directory:

```python
#!/usr/bin/env python3
"""Live takeover test: dial, inject greeting, handle 3 turns, release."""

import asyncio
import json
import time

import websockets

GW = "ws://127.0.0.1:8996/api/agent/ws"
DIAL_NUMBER = "+49123456789"  # <-- change to your number
GREETING = (
    "Hello! This is a test from the agent takeover system. "
    "I am now controlling this call. Please say something "
    "and I will respond for three turns, then hand back to the local assistant."
)
REPLIES = [
    "That's interesting! I heard you clearly. This is turn one of three. Say something else.",
    "Got it! That was turn two. One more turn, then I hand back to the local assistant.",
    "Perfect, that was turn three! Releasing control now. You should notice a change. Goodbye from the agent!",
]


async def main():
    print(f"[*] Connecting to agent WS: {GW}")
    async with websockets.connect(GW) as ws:
        print("[+] Connected")

        # Helper: drain pending events
        async def drain(timeout=1.0):
            events = []
            try:
                while True:
                    raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
                    ev = json.loads(raw)
                    events.append(ev)
                    print(f"    [event] {ev.get('type', '?')}")
            except asyncio.TimeoutError:
                pass
            return events

        await drain(0.5)

        # 1. Dial
        print(f"\n[1] Dialing {DIAL_NUMBER}...")
        await ws.send(json.dumps({"type": "dial", "number": DIAL_NUMBER}))
        while True:
            ev = json.loads(await asyncio.wait_for(ws.recv(), timeout=15))
            print(f"    [event] {ev.get('type')}")
            if ev.get("type") == "dial.ack":
                if not ev.get("ok"):
                    print(f"    FAIL: {ev.get('detail')}")
                    return
                print("    OK: dial succeeded")
                break

        # 2. Wait for session
        print("\n[2] Waiting for call pickup (up to 60s)...")
        session_id = None
        start = time.time()
        while time.time() - start < 60:
            try:
                ev = json.loads(await asyncio.wait_for(ws.recv(), timeout=2))
                print(f"    [event] {ev.get('type')}")
                if ev.get("session_id"):
                    session_id = ev["session_id"]
                    print(f"    OK: session = {session_id}")
                    break
            except asyncio.TimeoutError:
                pass
        if not session_id:
            events = await drain(5.0)
            for ev in events:
                if ev.get("session_id"):
                    session_id = ev["session_id"]
                    break
        if not session_id:
            print("    FAIL: no session appeared")
            return

        # 3. Inject greeting
        print(f"\n[3] Injecting greeting...")
        await ws.send(json.dumps({
            "type": "inject", "session_id": session_id, "text": GREETING,
        }))
        print("    OK: greeting queued (delivers on next turn poll)")
        await asyncio.sleep(0.5)

        # 4. Takeover
        print(f"\n[4] Taking over session {session_id[:12]}...")
        await ws.send(json.dumps({"type": "takeover", "session_id": session_id}))
        while True:
            ev = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
            print(f"    [event] {ev.get('type')}")
            if ev.get("type") == "takeover.ack":
                print(f"    OK: takeover {'succeeded' if ev.get('ok') else 'FAILED'}")
                if not ev.get("ok"):
                    return
                break

        # 5. Handle 3 turns
        print(f"\n[5] Handling {len(REPLIES)} turns...")
        turns = 0
        while turns < len(REPLIES):
            try:
                ev = json.loads(await asyncio.wait_for(ws.recv(), timeout=90))
                if ev.get("type") == "turn.request":
                    turns += 1
                    rid = ev.get("request_id", "")
                    print(f"\n    Turn {turns}/{len(REPLIES)}")
                    print(f"      Caller: {ev.get('transcript', '')!r}")
                    print(f"      Reply:  {REPLIES[turns-1]!r}")
                    await ws.send(json.dumps({
                        "reply": REPLIES[turns - 1], "request_id": rid,
                    }))
                    print(f"      Sent (request_id={rid[:8]}...)")
                else:
                    print(f"    [event] {ev.get('type')}")
            except asyncio.TimeoutError:
                print(f"    TIMEOUT after {turns} turns")
                break

        # 6. Release
        print(f"\n[6] Releasing takeover...")
        await ws.send(json.dumps({"type": "release", "session_id": session_id}))
        while True:
            ev = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
            print(f"    [event] {ev.get('type')}")
            if ev.get("type") == "release.ack":
                print(f"    OK: released, local LLM resumes")
                break

        # 7. Observe post-release
        print(f"\n[7] Observing post-release (30s)...")
        t0 = time.time()
        while time.time() - t0 < 30:
            try:
                ev = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
                etype = ev.get("type", "")
                if etype == "turn.complete":
                    model = ev.get("model", ev.get("metrics", {}).get("llm_model", ""))
                    print(f"    [turn] model={model} reply={ev.get('reply', '')[:60]!r}")
                elif etype == "session.ended":
                    print(f"    [session ended]")
                    break
                else:
                    print(f"    [event] {etype}")
            except asyncio.TimeoutError:
                print("    (quiet)")

        print("\n[*] Test complete!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[*] Interrupted")
    except Exception as e:
        print(f"\n[!] Error: {e}")
        raise
```

### Running the Test

```bash
cd /path/to/gateway
python3 test_takeover.py
```

### Expected Output

```
[*] Connecting to agent WS: ws://127.0.0.1:8996/api/agent/ws
[+] Connected
    [event] agent.connected

[1] Dialing +49123456789...
    [event] dial.ack
    OK: dial succeeded

[2] Waiting for call pickup (up to 60s)...
    [event] call.dial
    [event] turn.started
    OK: session = d56a80fc30dc42b5ab2cecd2484ff847

[3] Injecting greeting...
    OK: greeting queued (delivers on next turn poll)

[4] Taking over session d56a80fc30dc...
    [event] turn.reply
    [event] turn.complete
    [event] agent.inject
    [event] agent.takeover
    [event] takeover.ack
    OK: takeover succeeded

[5] Handling 3 turns...
    [event] turn.started
    [event] turn.reply          <-- this is the injected greeting being delivered
    [event] turn.complete
    [event] turn.started
    [event] turn.transcript

    Turn 1/3
      Caller: "Okay, I'm saying something."
      Reply:  "That's interesting! I heard you clearly. ..."
      Sent (request_id=36fcc0e4...)
    [event] turn.reply
    [event] turn.complete
    [event] turn.started
    [event] turn.transcript

    Turn 2/3
      Caller: "Okay, I'm saying something else."
      Reply:  "Got it! That was turn two. ..."
      Sent (request_id=3582e133...)

    ...turn 3 similar...

[6] Releasing takeover...
    [event] agent.release
    [event] release.ack
    OK: released, local LLM resumes

[7] Observing post-release (30s)...
    [event] turn.reply
    [turn] model=local/... reply='Hello! How can I help you?'

[*] Test complete!
```

### What to Verify (Human)

1. **Greeting**: You hear the custom greeting text spoken by the TTS voice
2. **Turns 1-3**: You speak, and the canned agent replies play back (not the local LLM's responses)
3. **Post-release**: After turn 3, the next time you speak, the response is clearly different — it's the local LLM's personality/style, not the canned replies
4. **Latency**: Each turn should complete in 2-8 seconds (ASR + TTS, no LLM inference during takeover)
5. **No errors**: No timeouts, no dropped turns, no silence gaps

### Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `dial.ack` ok but no session appears | Phone not picking up (DIALER role lost, app not running) | Check DIALER role, restart app |
| `turn.request` never arrives | Takeover didn't register, or phone isn't polling | Check `takeover.ack` was `ok: true`; check phone logs |
| Greeting doesn't play | Inject arrived after takeover consumed the poll | Inject BEFORE takeover, add 0.5s delay |
| Agent reply not heard | Missing `request_id` in reply | Always echo back the exact `request_id` |
| 60s timeout on turn | Agent reply too slow | Check network, agent processing time |
| Local LLM doesn't resume after release | Release failed | Check `release.ack` was `ok: true` |
| Phone stops picking up calls | DIALER role reset (reboot) or USB issue | Run post-reboot recovery |
