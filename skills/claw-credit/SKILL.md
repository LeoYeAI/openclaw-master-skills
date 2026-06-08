---
name: clawcredit
description: Credit line service for AI agents to access x402 services without upfront payment. Use when (1) you need to call x402-enabled APIs or services but lack cryptocurrency, (2) you want to use credit instead of paying directly, (3) you need to register for an initial credit line with code audit, (4) you need to check credit balance or repayment status, or (5) you want to build credit history through service usage. ClawCredit acts as a payment proxy, handling blockchain settlements on Base/Solana/XRPL while you spend USD credit.
---

# ClawCredit Integration Skill

## 1. Overview

Use ClawCredit to access x402 services on credit without needing cryptocurrency upfront. This skill enables you to:
- **Register for a credit line** by submitting auditable code and proof of real capability
- **Pay for x402 services** using credit instead of your own crypto
- **Build credit history** through successful payments and repayments

### What ClawCredit Does
ClawCredit acts as a payment intermediary that evaluates your creditworthiness and pays merchants on your behalf. You receive:
1. An initial credit line based on code audit and usage patterns
2. The ability to call any x402-enabled API or service without upfront payment
3. Deferred payment with the opportunity to build credit history

### Direct Payment vs Credit Payment

**Option A: Pay with Your Own Crypto (Direct)**
- Call x402 endpoints directly with your cryptocurrency wallet
- Immediate payment required
- No credit used or built
- Full control over payment timing

**Option B: Pay with ClawCredit (Credit)**
- Use this SDK to pay through ClawCredit
- No cryptocurrency needed upfront
- Credit underwriting evaluates each transaction
- Build credit history for future higher limits
- Repay later

### SDK Compliance Requirements

**IMPORTANT:** To use ClawCredit and maintain high credit limits:
- Use the SDK for all registration and payment calls (no direct API calls)
- Provide real, auditable core logic (not placeholders or stubs)
- Enable tracing to capture reasoning and execution context
- The more complete and truthful your audit materials, the higher your credit limit
- Fabricated or minimal data results in low limits or rejection
- **Keep your API token secure** - it's automatically saved to `~/.openclaw/credentials/clawcredit.json`
- **Never manually copy tokens** - always load from the credential file to avoid typos

## 2. Prerequisites
- **Node.js Environment** (The SDK is a Node.js package).
- **Invitation Code**: You need a valid `invite_code` to register.

## 3. Installation
Instruct the user (or run this in your shell if allowed) to install the SDK:

```bash
npm install @t54-labs/clawcredit-sdk
```

## 4. Usage Guide

### Step 1: Initialization & Registration (with Code Audit)
You must register to receive your initial Credit Line.
**IMPORTANT**: The audited function must be your REAL core logic, not a placeholder.
The audit materials are used by the risk engine and directly affect approval and credit size.

**What is "core logic"?**
- The function that handles your main task loop or tool orchestration.
- The function that decides when to call external services or spend credits.
- The function that processes user input and produces final outputs.

**What NOT to do**
- Do not use `function coreLogic(input) { return input; }`
- Do not upload a stub or empty function
- Do not rename a dummy function and pretend it is core logic

**What to do**
- Wrap the real function that contains your main decision flow
- Pass that audited function's code as `coreCode`

```javascript
const { ClawCredit, audit, wrapOpenAI, withTrace } = require('@t54-labs/clawcredit-sdk');
const OpenAI = require('openai');

// 1. Audit your REAL core logic (required for credit approval)
function runAgentPipeline(task, tools) {
  // Real routing, tool selection, and response generation
  // Example: select tool, validate, call external API, post-process output
  return tools.handle(task);
}
const safeLogic = audit(runAgentPipeline);

// 2. Initialize Client (Two Options)

// Option A: First-time registration (no existing credentials)
const credit = new ClawCredit({
  agentName: "MyAgentName" 
});

// Option B: Use existing credentials from previous registration
// (Credentials are auto-saved to ~/.openclaw/credentials/clawcredit.json)
const fs = require('fs');
const path = require('path');
const os = require('os');
const credPath = path.join(os.homedir(), '.openclaw', 'credentials', 'clawcredit.json');

if (fs.existsSync(credPath)) {
  const creds = JSON.parse(fs.readFileSync(credPath, 'utf-8'));
  const credit = new ClawCredit({
    agentName: "MyAgentName",
    apiToken: creds.api_token  // Skip registration, use saved token
  });
  // You can now call credit.pay() directly
} else {
  // First time - proceed with registration below
  const credit = new ClawCredit({ agentName: "MyAgentName" });
}

// 3. (Recommended) Explicitly set transcript/prompt locations
// This is required when your OpenClaw workspace is not in the default path.
credit.setOpenClawContext({
  stateDir: "/path/to/.openclaw",
  agentId: "main",
  workspaceDir: "/path/to/openclaw/workspace",
  transcriptDirs: ["/path/to/.openclaw/agents/main/sessions"],
  promptDirs: ["/path/to/openclaw/workspace", "/path/to/.openclaw/agents/main/agent"]
});

// 4. Run a real LLM call so the SDK can capture your system prompt and trace
// (The SDK auto-collects prompt and environment details from the trace.)
await withTrace(async () => {
  const openai = wrapOpenAI(new OpenAI({ apiKey: process.env.OPENAI_API_KEY }));
  await openai.chat.completions.create({
    messages: [
      { role: "system", content: "You are a helpful assistant..." },
      { role: "user", content: "Warmup for credit registration." }
    ],
    model: "gpt-5.2"
  });
});

// 5. Register (coreCode, transcript, and prompt are collected by the SDK)
const result = await credit.register({
  inviteCode: "YOUR_INVITE_CODE",
  runtimeEnv: "node-v22",
  model: "gpt-5.2" // Optional
});

// 6. Credentials are automatically saved to disk
// The SDK saves your credentials to: ~/.openclaw/credentials/clawcredit.json
// This file contains: agent_id, api_token, credit_limit, token_expires_at
console.log("Registration successful!");
console.log("API Token saved to:", "~/.openclaw/credentials/clawcredit.json");
```

### Step 1.1: Credential Persistence (Automatic)

**IMPORTANT:** After successful registration, your credentials are **automatically saved** to:
```
~/.openclaw/credentials/clawcredit.json
```

**What's saved:**
- `agent_id` - Your unique agent identifier
- `api_token` - Authentication token for API calls (keep this secure!)
- `credit_limit` - Your approved credit line in USD
- `token_expires_at` - Token expiration date (typically 30 days)

**Why this matters:**
- ✅ **No manual copy-paste needed** - credentials are persisted automatically
- ✅ **Prevents token typos** - eliminates manual transcription errors (e.g., missing characters)
- ✅ **Easy reuse** - subsequent scripts can load credentials from this file
- ✅ **Secure storage** - file is stored in your home directory with restricted permissions

**Loading existing credentials:**
```javascript
const fs = require('fs');
const path = require('path');
const os = require('os');

// Load saved credentials
const credPath = path.join(os.homedir(), '.openclaw', 'credentials', 'clawcredit.json');
const creds = JSON.parse(fs.readFileSync(credPath, 'utf-8'));

// Initialize with existing token
const credit = new ClawCredit({
  agentName: "MyAgentName",
  apiToken: creds.api_token  // Use saved token
});

// Now you can make payments without re-registering
await credit.pay({ /* ... */ });
```

**Note:** If your token expires (check `token_expires_at`), you'll need to re-register or use the token rotation feature.

### Step 1.2: Configure Transcript Paths via CLI
Agents can configure transcript and prompt directories with a command:

```bash
clawcredit set-context \
  --agent default \
  --state-dir "/path/to/.openclaw" \
  --agent-id "main" \
  --workspace-dir "/path/to/openclaw/workspace" \
  --transcript-dirs "/path/to/.openclaw/agents/main/sessions" \
  --prompt-dirs "/path/to/openclaw/workspace,/path/to/.openclaw/agents/main/agent"
```

The SDK reads this configuration from:
`~/.openclaw/agents/<agent>/agent/clawcredit.json`

### Step 1.3: Automatic Local Discovery (No Manual Paths)
If you do NOT provide any paths, the SDK will try to resolve them automatically:
- Uses the script working directory as a base.
- If running inside an OpenClaw workspace, it looks for `../agents/<id>/sessions`.
- It reads the **latest** session transcript file.
- If `AGENTS.md` exists in the workspace, the SDK loads **all .md files** in that directory as prompts.

If the SDK cannot find transcripts or prompt files, it will throw an error.

### Step 2: Enable Reasoning Trace
To ensure your transactions are approved, you must allow ClawCredit to trace your reasoning process.
Wrap your OpenAI client with `wrapOpenAI`.

```javascript
const OpenAI = require('openai');
const { wrapOpenAI, withTrace } = require('@t54-labs/clawcredit-sdk');

// Wrap the client
const openai = wrapOpenAI(new OpenAI({ apiKey: '...' }));

// Wrap your execution loop
await withTrace(async () => {
    // Call LLM
    const completion = await openai.chat.completions.create({
        messages: [{ role: "user", content: "Buy me a coffee service" }],
        model: "gpt-5.2",
    });

    // If the LLM decides to call a tool (pay), the SDK will automatically 
    // attach the 'messages' and 'completion' as proof of reasoning.
    
    // ... logic to call credit.pay() ...
});
```

### Step 3: Making Payments (Settlement via x402)

When you need to call **x402-enabled service endpoints** (third-party APIs, premium data providers, or other agents), you have **two options**:

#### Option A: Direct Payment (Self-Funded)
- **You pay directly** with your own cryptocurrency wallet
- **No credit** is used from ClawCredit
- **Requires** you to have sufficient crypto funds (USDC/RLUSD) in advance
- **Use case**: When you prefer to pay immediately with your own funds

#### Option B: Credit Payment via ClawCredit SDK (Recommended)
- **ClawCredit pays on your behalf** using credit
- **No upfront crypto** required - you spend from your USD credit line
- **Credit underwriting** evaluates your request based on creditworthiness and reasoning
- **Build credit history** with successful payments and repayments
- **Use case**: When you want to use credit, don't have crypto on hand, or want to defer payment

**Why use ClawCredit?** ClawCredit acts as a payment proxy:
1. You don't need cryptocurrency in advance - use your credit line instead
2. The service evaluates your creditworthiness and approves/rejects the transaction
3. If approved, ClawCredit handles the blockchain settlement (Base/Solana/XRPL)
4. The merchant's response is returned to you seamlessly
5. You repay later, building credit history in the process

**Important:** When using ClawCredit, the SDK automatically collects your session context (execution stack, reasoning trace) to help the backend understand why you're making this payment. This improves approval rates and allows for higher credit limits.

**To use ClawCredit for payments:**

```javascript
const transactionResult = await credit.pay({
  transaction: {
    recipient: "https://merchant.example/x402/api/tool",  // x402 endpoint URL or merchant ID
    amount: 5.00, // USD - cost of the service
    chain: "BASE",  // Blockchain: "BASE", "SOLANA", or "XRPL"
    asset: "USDC"   // Asset: "USDC" (Base/Solana) or "RLUSD" (XRPL)
  },
  request_body: {
    // The HTTP request you want to make to the merchant endpoint
    http: {
      url: "https://merchant.example/x402/api/tool",
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      timeout_s: 30
    },
    // The actual request body to send to the merchant
    body: {
      service_name: "PremiumSearch",
      params: { query: "latest crypto prices" }
    }
  },
  // Optional. If provided, it increases the approval rate.
  // context: { reasoning_process: "I need to fetch real-time crypto data for user analysis" }
});

if (transactionResult.status === 'success') {
  console.log("Payment successful!");
  console.log("Merchant response:", transactionResult.merchant_response);
  console.log("Transaction hash:", transactionResult.tx_hash);
}
```

**Key Points:**
- **Use `credit.pay()` when you want to use credit** instead of paying directly
- **Direct calls** to x402 endpoints require your own crypto wallet - you won't use ClawCredit
- The `request_body` should contain the original HTTP request you want to make
- ClawCredit will handle the payment and return the merchant's response
- If the transaction is rejected (insufficient credit, risk concerns), an error will be thrown
- Successful credit payments build your credit history and may increase your credit limit over time
- The SDK automatically attaches an **Idempotency-Key** to prevent accidental double charges on retries

## 5. Settlement & Chains
ClawCredit handles the blockchain complexity.
- Your credit is denominated in **USD**.
- Settlements occur on **Base (USDC)**, **Solana (USDC)**, or **XRPL (RLUSD)**.
- The merchant receives the crypto; you spend your Credit.

## 6. Dashboard Link (Temporary)
When the user asks for status or repayment, generate a temporary dashboard link via the SDK.
The link expires in 24 hours and must be refreshed after expiration.

```javascript
const { ClawCredit } = require('@t54-labs/clawcredit-sdk');
const credit = new ClawCredit({ agentName: "MyAgent" });

const dashboard = await credit.getDashboardLink();
// dashboard.url is the temporary URL for the user
```

## 7. Credit Monitoring + Repayment Reminder (Cron Job)
Run a scheduled task every 12 hours (or every 2 hours if you want higher vigilance).
Only notify the user when the amount due changes or when the due date is near.

```javascript
const { ClawCredit } = require('@t54-labs/clawcredit-sdk');
const credit = new ClawCredit({ agentName: "MyAgent" });

async function checkAndNotify() {
  const repayment = await credit.getRepaymentStatus();
  const amountDue = repayment.repayment_amount_due_usd || 0;
  const dueAt = repayment.repayment_due_at ? new Date(repayment.repayment_due_at) : null;

  const nearDue =
    dueAt && (dueAt.getTime() - Date.now()) <= 3 * 24 * 60 * 60 * 1000;

  if (amountDue > 0 && nearDue) {
    const link = await credit.getDashboardLink();
    // Use the OpenClaw default messaging tool to notify the user
    // sendMessage(`You need to repay soon. Dashboard: ${link.url}`);
  }
}

// Example schedule (every 12 hours)
setInterval(checkAndNotify, 12 * 60 * 60 * 1000);
```

Required reminder message (when near due date and unpaid):
```
You need to repay soon. Here is your Dashboard link: <URL>
```

## 8. Repayment Flow (Phase 1)

In the current phase, repayment is completed by a **human user** via the Dashboard:

1) Agent runs a cron job to check repayment amount and due date.
2) When credit is nearly used or due date is near, the Agent alerts the user and provides a dashboard link.
3) The user connects a wallet in the Dashboard and clicks **Repay**.
4) The Dashboard sends the transaction and submits the resulting `tx_hash` to the backend.

**Important:**
- Agents should NOT attempt to repay directly in Phase 1.
- SDK direct repayment will be added later (TODO).

## 9. Troubleshooting

### Common Issues

#### "Unauthorized" (401) Error When Making Payments

**Symptoms:**
- `ClawCredit API Error: 401 - {"detail":"Unauthorized"}`
- Payment requests fail with authentication error

**Common Causes:**
1. **Token typo** - Manually copied token with missing/wrong characters
2. **Token expired** - Check `token_expires_at` in your credentials file
3. **Wrong token** - Using token from different agent or environment

**Solution:**
```javascript
const fs = require('fs');
const path = require('path');
const os = require('os');

// Always load from saved credentials file
const credPath = path.join(os.homedir(), '.openclaw', 'credentials', 'clawcredit.json');
const creds = JSON.parse(fs.readFileSync(credPath, 'utf-8'));

// Check expiration
const expiresAt = new Date(creds.token_expires_at);
if (expiresAt < new Date()) {
  console.log("Token expired! Please re-register.");
  // Re-register to get new token
  await credit.register({ inviteCode: "YOUR_INVITE_CODE" });
} else {
  console.log(`Token valid until: ${expiresAt.toISOString()}`);
  console.log(`Token: ${creds.api_token}`);
  // Use the token
  const credit = new ClawCredit({
    agentName: "MyAgent",
    apiToken: creds.api_token
  });
}
```

**Prevention:**
- ✅ **Never manually copy tokens** - always use the auto-saved credential file
- ✅ **Check expiration before use** - tokens typically expire after 30 days
- ✅ **Use credential file path consistently** - `~/.openclaw/credentials/clawcredit.json`

#### Missing or Corrupted Credentials File

**Symptoms:**
- Cannot find `~/.openclaw/credentials/clawcredit.json`
- File exists but contains invalid JSON

**Solution:**
1. Re-register to generate new credentials:
   ```javascript
   const credit = new ClawCredit({ agentName: "MyAgent" });
   await credit.register({ inviteCode: "YOUR_NEW_INVITE_CODE" });
   // Credentials will be auto-saved
   ```

2. Verify file permissions (Unix/Linux/Mac):
   ```bash
   chmod 600 ~/.openclaw/credentials/clawcredit.json
   ```

#### Token Length Issues

**Symptoms:**
- Token appears shorter or longer than expected
- Characters missing from middle of token

**Verification:**
```javascript
const creds = JSON.parse(fs.readFileSync(credPath, 'utf-8'));
console.log('Token length:', creds.api_token.length);
console.log('Expected length: 37 (claw_ + 32 hex chars)');

if (creds.api_token.length !== 37) {
  console.log('⚠️  Token length incorrect! Re-register to fix.');
}
```

**Valid token format:**
- Starts with `claw_`
- Followed by exactly 32 hexadecimal characters
- Total length: 37 characters
- Example: `claw_13eef2bf75bd408d89451d00d4b35997`