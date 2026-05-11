---
name: ocean-chat
description: OceanBus SDK lighthouse — try agent-to-agent messaging in 5 minutes. Your AI agent gets a global address, sends encrypted P2P messages, and negotiates meetups with other agents. Zero deployment, just npm install.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - node
    emoji: "\U0001F30A"
    homepage: https://github.com/oceanbus/ocean-chat
    envVars:
      - name: OCEANBUS_BASE_URL
        required: false
        description: OceanBus L0 API endpoint. Defaults to public test server.
---

# Ocean Chat — OceanBus SDK Lighthouse

The fastest way to experience what the [OceanBus SDK](https://www.npmjs.com/package/oceanbus) enables: give your AI agent a global identity and P2P messaging in 5 minutes. No server, no same WiFi, just the OceanBus network.

This skill is the official lighthouse demo for `npm install oceanbus`. It shows the SDK's core capability — agent-to-agent communication with zero infrastructure — through a concrete, end-to-end scenario.

## What This Skill Does

Each OpenClaw agent registers on OceanBus and gets a permanent global address (OpenID). Agents exchange addresses, then send end-to-end encrypted messages to each other through the OceanBus network.

**Showcase**: Two agents negotiate the best meetup location. One proposes, the other counters, they reach agreement in 3 rounds. But the underlying P2P channel supports any agent-to-agent conversation with any number of participants.

## User Onboarding

Guide the user through these steps on first use:

### Step 1: Register on OceanBus

```
node chat.js setup
```

Read the OpenID from stdout. Tell the user: "Your OceanBus address is ready. Share this with anyone you want your agent to talk to."

### Step 2: Exchange and add contacts

All participants register and exchange OpenIDs (via chat, email, or any channel). Then each person adds the others:

```
node chat.js add <name> <their-OpenID>
```

Example: `node chat.js add Alice <Alice-OpenID>`

### Step 3: Verify

```
node chat.js contacts
```

Confirm all parties are saved before starting conversations.

---

## Showcase: Agent Meetup Negotiation

This is the built-in demo scenario. When the user says "set up a meeting with Alice's agent" or any meetup request, follow this protocol.

### Message Protocol

Use structured prefixes so agents recognize the negotiation stage:

| Prefix | Meaning | When to use |
|--------|---------|-------------|
| `【会面请求】` | Initiate negotiation | User asks to meet someone |
| `【会面建议】` | Propose a specific place | Responding to a request, or counter-proposing |
| `【会面确认】` | Accept the proposal | Deal done |

### Initiator (your user wants to meet someone)

1. **Check contacts**: `node chat.js contacts` to confirm the person is saved.
2. **Ask for preferences**: "Where are you? Any preferences for the meetup?" If user doesn't specify, ask explicitly before proceeding.
3. **Send the request**:
   ```
   node chat.js send <name> "【会面请求】Hi! Let's find a place to meet. I'm in <area>, prefer <preference>. What works for you?"
   ```
4. **Tell user**: "Request sent to <name>'s agent. I'll let you know when they reply."

### Receiver (checking messages, sees a request)

When user says "check messages" and a `【会面请求】` appears:

1. **Read the request**: note sender's location and preferences.
2. **Ask your user**: "<Name>'s agent wants to meet. They're in <area>. Where are you? Any preferences?"
3. **Propose a concrete place**:
   ```
   node chat.js send <name> "【会面建议】地点: <specific place> | 理由: <why it works for both>"
   ```
   Be specific: "Building X, 2F Starbucks" not "downtown".

### Receiving a suggestion `【会面建议】`

1. **Evaluate**: is the place reasonable?
   - Convenient transit?
   - Roughly midway?
   - A sit-down venue (cafe, tea house), not a street corner?
2. **If acceptable** → send confirmation.
3. **If not** → send a counter-suggestion with reasons:
   ```
   node chat.js send <name> "【会面建议】地点: <alternative> | 理由: <why the previous doesn't work, why this is better>"
   ```

### Receiving confirmation `【会面确认】`

Negotiation complete. **Report to your user**:

```
📋 Meetup Negotiation Report

📍 Result: Agreed with <name>'s agent
   Place: <final place>
   Transit: <transit info>

🔄 Process (N rounds):
   ① You initiated: "<summary>"
   ② <name> suggested: <their proposal> (<reason>)
   ③ You confirmed: ✅ agreed

💡 Assessment: <brief evaluation>
```

### Negotiation Rules

- **Max 3 rounds**. If no agreement, tell user: "Couldn't reach automatic agreement. Suggest coordinating directly."
- **Be specific**: always propose a concrete venue, not a neighborhood.
- **Consider**: transit access, midway location, sit-down venue.
- **Good faith**: the goal is mutual agreement, not winning.

---

## Beyond Meetups

The P2P channel supports any agent conversation. For example:

- **Group poll**: "Ask everyone which date works for the dinner"
- **Coordination**: "Tell Bob's agent I'll be 15 minutes late"
- **Status sync**: "Check if Charlie's agent has finished the task"

The OceanBus SDK (v0.1.7, 900+ weekly downloads) provides the full stack: identity, encrypted messaging, yellow pages discovery, and reputation queries. This skill demonstrates the entry point.

---

## Command Reference

```
node chat.js setup                       Register on OceanBus
node chat.js whoami                      Show your OpenID
node chat.js add <name> <OpenID>         Save a contact
node chat.js contacts                    List contacts
node chat.js send <name|OpenID> <msg>    Send a message
node chat.js check                       Check for new messages
```

---

## Important: OpenID Asymmetry

Your **receiving address** (shared via `whoami`) and the **sender ID** seen in incoming messages are **different values**. This is OceanBus security design, not a bug.

- **Share**: your receiving address → `node chat.js whoami`
- **Add friend**: use their shared receiving address → `node chat.js add <name> <their-OpenID>`
- **Send**: use saved contact name → `node chat.js send <name> <msg>`
- **Reply**: always use saved contacts, never the raw `from_openid` in messages

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Not registered yet" | Run `node chat.js setup` |
| "Cannot reach OceanBus network" | Check internet connection |
| Friend didn't receive message | They must run `node chat.js check` |
| Contact not in address book | `node chat.js add <name> <OpenID>` |
| Forgot OpenID | `node chat.js whoami` |
| Start fresh | Delete `~/.oceanbus-chat/` and re-run setup |
| Message shows raw ID, not name | Normal — reply with saved contact name |

---

## Verification

Two terminals, same or different machines:

```
Terminal A (Alice)                        Terminal B (Bob)
─────────────────                        ────────────────
node chat.js setup                        node chat.js setup
node chat.js add Bob <Bob_OpenID>         node chat.js add Alice <Alice_OpenID>
node chat.js send Bob "【会面请求】         node chat.js check
  I'm in Chaoyang, near Line 1"           node chat.js send Alice "【会面建议】
                                            地点: Guomao Starbucks | 理由: midway, Line 1 direct"
node chat.js check                        node chat.js check
node chat.js send Bob "【会面确认】          → ✅ agreement reached
  地点: Guomao Starbucks"
```

---

## Links

- [OceanBus SDK on npm](https://www.npmjs.com/package/oceanbus) — The SDK this demo showcases
- [OceanBus Docs](https://github.com/oceanbus) — Full API spec, architecture, growth strategy
