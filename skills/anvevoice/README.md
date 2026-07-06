# 🎙️ AnveVoice OpenClaw Skill

> Transform your website with AI voice assistants. Engage visitors naturally, automate support, capture leads, and boost conversions — all through voice.

<p align="center">
  <a href="https://anvevoice.com"><img src="https://img.shields.io/badge/Website-anvevoice.com-blue?style=flat-square&logo=google-chrome" alt="Website"></a>
  <a href="https://anvevoice.com/developer"><img src="https://img.shields.io/badge/API-Documentation-green?style=flat-square&logo=readthedocs" alt="API Docs"></a>
  <img src="https://img.shields.io/badge/TypeScript-Ready-blue?style=flat-square&logo=typescript" alt="TypeScript">
  <img src="https://img.shields.io/badge/MCP-Compatible-orange?style=flat-square" alt="MCP">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License">
  <a href="https://www.virustotal.com/gui/file/f3c788a5cfa2a01b67edd6af451ee6748944818f20b7d51203ecf5cf8d4c837b?nocache=1"><img src="https://img.shields.io/badge/VirusTotal-0%2F62%20Clean-brightgreen?style=flat-square&logo=virustotal" alt="VirusTotal"></a>
</p>

<p align="center">
  <b>🤖 Customer Support</b> • 
  <b>🎯 Lead Generation</b> • 
  <b>♿ Accessibility</b> • 
  <b>📈 Engagement</b>
</p>

---

## 📋 Table of Contents

- [What is AnveVoice?](#what-is-anvevoice)
- [Why Choose AnveVoice?](#why-choose-anvevoice)
- [Use Cases](#use-cases)
- [Quick Start Guide](#quick-start-guide)
- [Step-by-Step Integration](#step-by-step-integration)
- [Tool Reference](#tool-reference)
- [Example Workflows](#example-workflows)
- [Pricing](#pricing)
- [Comparison](#comparison)
- [Troubleshooting](#troubleshooting)
- [Support](#support)

---

## What is AnveVoice?

**AnveVoice** is a SaaS platform that adds **AI voice assistants** to your website. Instead of typing, visitors simply talk to your website — and the AI understands, responds, navigates pages, fills forms, captures leads, and completes tasks.

### Key Features

| Feature | Description |
|---------|-------------|
| 🎙️ **Voice-First** | Natural speech conversations, not robotic chat |
| 🌐 **Multilingual** | 22 Indian languages + global languages supported |
| 🤖 **AI-Powered** | GPT-powered understanding and responses |
| 📊 **Analytics** | Deep visitor intelligence and sentiment analysis |
| 🎧 **Recordings** | Full session recordings for quality review |
| 🔧 **No-Code Setup** | Copy-paste embed code, no developers needed |

---

## Why Choose AnveVoice?

### The Problem with Traditional Websites

| Problem | Impact |
|---------|--------|
| ❌ **70% bounce rate** | Visitors leave without engaging |
| ❌ **Text chatbots feel robotic** | Frustrating user experience |
| ❌ **Support tickets pile up** | Repetitive queries overwhelm teams |
| ❌ **Mobile forms are painful** | Tiny keyboards = abandoned forms |
| ❌ **Contact forms = dead leads** | Visitors won't fill them out |

### The AnveVoice Solution

| Solution | Result |
|----------|--------|
| ✅ **Voice captures attention** | **25-40%** reduction in bounce rate |
| ✅ **Natural conversations** | Feels human, not robotic |
| ✅ **AI handles repetitive queries** | **60%** ticket deflection |
| ✅ **Voice input on mobile** | No typing needed |
| ✅ **Conversational lead capture** | **3x** more qualified leads |

---

## Use Cases

### By Function

| Use Case | Benefit |
|----------|---------|
| 🤖 **24/7 Customer Support** | Instant answers, zero wait time |
| 🎯 **Lead Generation** | Capture visitor info naturally in conversation |
| ♿ **Accessibility** | Serve users who can't or prefer not to type |
| 📈 **Engagement** | Interactive voice experiences reduce bounce |
| 📊 **Analytics** | Understand visitor intent and sentiment |

### By Industry

| Industry | Applications |
|----------|--------------|
| **SaaS** | Product demos, onboarding, feature discovery |
| **E-commerce** | Product search, order tracking, returns handling |
| **Healthcare** | Appointment booking, symptom checking, reminders |
| **Education** | Course guidance, doubt resolution, progress tracking |
| **Real Estate** | Property search, virtual tours, visit booking |
| **Finance** | Product recommendations, KYC, balance inquiries |

---

## Quick Start Guide

Get your first voice bot running in **5 minutes**:

### Step 1: Install the Skill (30 seconds)

```bash
openclaw skills install https://github.com/anvevoice/openclaw-skill
```

### Step 2: Get Your API Key (2 minutes)

<details>
<summary>📋 Click to see detailed API key creation steps</summary>

1. **Visit the Developer Portal**
   - Go to [anvevoice.com/developer](https://anvevoice.com/developer)
   - Sign up or log in to your AnveVoice account

2. **Generate API Key**
   - Click the **"Generate API Key"** button
   - Give your key a name (e.g., "My Website Bot")
   - Select permissions (recommended: Full Access)

3. **Copy Your Key**
   - Your key will look like: `anvk_9789b8870397b5f6a3f3a1e3a71ad23c4b2cb64f`
   - ⚠️ **Important:** Copy it immediately — it's shown only once!
   - Store it securely (password manager recommended)

4. **Verify Key Format**
   - Should start with `anvk_`
   - Should be ~50+ characters long
   - Contains letters, numbers, and underscores

</details>

### Step 3: Configure OpenClaw (1 minute)

```bash
# Set your API key
openclaw config set ANVEVOICE_API_KEY anvk_your_key_here

# Verify it's set
echo $ANVEVOICE_API_KEY
```

**Alternative:** Set as environment variable:
```bash
export ANVEVOICE_API_KEY=anvk_your_key_here
```

### Step 4: Test Connection (30 seconds)

```bash
openclaw skills test anvevoice --input "ping"
```

**Expected output:**
```json
{
  "status": "ok",
  "server": "anve-mcp",
  "version": "1.0.0"
}
```

✅ **You're connected!** Now let's create your first bot.

---

## Step-by-Step Integration

### 🚀 Deploy Your First Voice Bot (10 minutes)

#### Step 1: Create a Bot

```javascript
// Create a support bot
const result = await callAnveTool("create_bot", {
  name: "Website Support Assistant",
  system_prompt: `You are a helpful customer support agent for our website. 
    Answer questions about our products, help with common issues, 
    and collect contact information when needed. Be friendly and professional.`,
  welcome_message: "Hi there! 👋 I'm here to help. What can I do for you today?",
  voice_id: "default"
});

// Save this ID — you'll need it for everything else
const botId = result.bot.id;
console.log("Bot created:", botId);
```

#### Step 2: Add Knowledge

```javascript
// Add your FAQ as knowledge
await callAnveTool("add_knowledge_text", {
  bot_id: botId,
  title: "Company FAQ",
  content: `
    Q: What are your business hours?
    A: We're open Monday-Friday, 9 AM to 6 PM IST.
    
    Q: How do I contact sales?
    A: You can reach our sales team at sales@example.com or ask me to schedule a call.
    
    Q: What's your refund policy?
    A: We offer 30-day full refunds, no questions asked.
  `
});

// Add your website as knowledge
await callAnveTool("add_knowledge_url", {
  bot_id: botId,
  url: "https://your-website.com",
  crawl_type: "full_site",
  title: "Website Content"
});
```

#### Step 3: Get Embed Code

```javascript
// Get the code to add to your website
const embed = await callAnveTool("get_embed_code", { bot_id: botId });
console.log(embed.embed_code);
```

**Output:**
```html
<!-- AnveVoice Embed Code -->
<script src="https://anvevoice.com/embed.js" 
        data-bot-id="YOUR_BOT_ID"
        data-position="bottom-right"
        async>
</script>
```

#### Step 4: Add to Your Website

**For HTML/Static Sites:**
Paste the embed code just before the closing `</body>` tag:

```html
<!DOCTYPE html>
<html>
<head>
  <title>My Website</title>
</head>
<body>
  <!-- Your website content -->
  
  <!-- AnveVoice Widget -->
  <script src="https://anvevoice.com/embed.js" 
          data-bot-id="YOUR_BOT_ID"
          data-position="bottom-right"
          async>
  </script>
</body>
</html>
```

**For React/Next.js:**
```jsx
// components/AnveVoiceWidget.jsx
import { useEffect } from 'react';

export default function AnveVoiceWidget({ botId }) {
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://anvevoice.com/embed.js';
    script.async = true;
    script.setAttribute('data-bot-id', botId);
    script.setAttribute('data-position', 'bottom-right');
    document.body.appendChild(script);
    
    return () => {
      document.body.removeChild(script);
    };
  }, [botId]);
  
  return null;
}

// pages/_app.jsx or layout.jsx
import AnveVoiceWidget from '../components/AnveVoiceWidget';

export default function App({ Component, pageProps }) {
  return (
    <>
      <Component {...pageProps} />
      <AnveVoiceWidget botId="YOUR_BOT_ID" />
    </>
  );
}
```

**For WordPress:**
1. Install "Insert Headers and Footers" plugin
2. Go to Settings → Insert Headers and Footers
3. Paste embed code in "Scripts in Footer" section
4. Save

#### Step 5: Verify Deployment

1. Visit your website
2. Look for the voice widget (usually bottom-right corner)
3. Click it and say "Hello!"
4. The AI should respond

✅ **Done!** Your voice assistant is live.

---

## Tool Reference

### 46 MCP Tools Available

| Category | Count | Key Tools |
|----------|-------|-----------|
| **Bot Management** | 8 | `create_bot`, `update_bot`, `clone_bot`, `delete_bot` |
| **Conversations** | 7 | `list_sessions`, `get_session_messages`, `search_conversations` |
| **Intelligence** | 5 | `extract_leads`, `get_visitor_intelligence`, `summarize_session` |
| **Analytics** | 6 | `get_analytics_overview`, `get_sentiment_trends`, `get_conversion_events` |
| **Feedback** | 4 | `list_feedback`, `get_improvement_recommendations` |
| **Knowledge** | 3 | `add_knowledge_url`, `add_knowledge_text` |
| **Recordings** | 2 | `list_session_recordings`, `get_session_recording` |
| **Deployment** | 1 | `get_embed_code` |
| **Billing** | 3 | `get_subscription`, `get_usage_stats` |
| **System** | 2 | `ping`, `list_tools` |

[View complete tool documentation →](./SKILL.md)

---

## Example Workflows

### Workflow 1: 24/7 Support Bot

```javascript
// 1. Create the bot
const { bot } = await callAnveTool("create_bot", {
  name: "24/7 Support",
  system_prompt: "You are a helpful support agent...",
  welcome_message: "Hi! How can I help you today?"
});

// 2. Add knowledge base
await callAnveTool("add_knowledge_url", {
  bot_id: bot.id,
  url: "https://docs.yoursite.com",
  crawl_type: "full_site"
});

// 3. Deploy
const { embed_code } = await callAnveTool("get_embed_code", { 
  bot_id: bot.id 
});
// Paste embed_code into your website

// 4. Monitor (run daily)
const { total_sessions } = await callAnveTool("get_analytics_overview", {
  bot_id: bot.id,
  from_date: "2025-02-01"
});
console.log(`Bot handled ${total_sessions} sessions today`);
```

### Workflow 2: Lead Capture Funnel

```javascript
// 1. Create lead capture bot
const { bot } = await callAnveTool("create_bot", {
  name: "Lead Capture Bot",
  system_prompt: "Engage visitors and capture their contact info..."
});

// 2. Let it run for a week...

// 3. Extract leads (weekly)
const { leads } = await callAnveTool("extract_leads", { 
  bot_id: bot.id 
});

// 4. Send leads to your CRM
for (const lead of leads) {
  console.log(`New lead: ${lead.name} (${lead.email})`);
  // await addToCRM(lead);
}
```

### Workflow 3: Analytics Dashboard

```javascript
// Get comprehensive analytics
const [overview, sentiment, timeline] = await Promise.all([
  callAnveTool("get_analytics_overview", { bot_id, from_date: "2025-02-01" }),
  callAnveTool("get_sentiment_trends", { bot_id, from_date: "2025-02-01" }),
  callAnveTool("get_analytics_timeline", { bot_id, from_date: "2025-02-01" })
]);

// Find what visitors ask about
const pricingQueries = await callAnveTool("search_conversations", {
  bot_id,
  query: "pricing"
});
```

---

## Pricing

| Plan | Monthly Price | Best For | Includes |
|------|--------------|----------|----------|
| **Free** | ₹0 | Testing, side projects | 50K tokens, 1 bot, basic analytics |
| **Growth** ⭐ Popular | ₹2,999 | Small businesses, startups | 2M tokens, 5 bots, advanced analytics |
| **Scale** | ₹9,999 | Growing businesses | 8M tokens, unlimited bots, full features |
| **Enterprise** | Custom | Large organizations | Unlimited, SLA, dedicated support |

🎁 **Launch Special:** 2× tokens if subscribed before March 31, 2026

### Token Usage Guide

| Action | Token Cost |
|--------|-----------|
| 1 minute of conversation | ~3,400 tokens |
| Single FAQ answer | ~500 tokens |
| Full session (4 min avg) | ~13,600 tokens |

---

## Comparison

### AnveVoice vs. Alternatives

| Feature | AnveVoice | Intercom | Drift | Tidio |
|---------|-----------|----------|-------|-------|
| **Voice Interface** | ✅ Native | ❌ No | ❌ No | ❌ No |
| **AI-Powered** | ✅ GPT-4 | ⚠️ Basic | ⚠️ Basic | ⚠️ Basic |
| **22 Indian Languages** | ✅ Yes | ❌ Limited | ❌ Limited | ❌ Limited |
| **Session Recordings** | ✅ Yes | ⚠️ Limited | ❌ No | ❌ No |
| **Deep Analytics** | ✅ Yes | ⚠️ Basic | ⚠️ Basic | ⚠️ Basic |
| **India Pricing** | ✅ ₹2,999/mo | ❌ $74+/mo | ❌ $400+/mo | ❌ $29+/mo |

### Why AnveVoice Wins

- 🎙️ **Only voice-native solution** — competitors are text-only
- 💰 **80% cheaper** than Intercom for Indian businesses
- 🌐 **Built for India** — 22 languages, local pricing, regional support
- 🧠 **Deeper intelligence** — visitor profiles, sentiment, recordings

---

## Troubleshooting

### Common Issues

<details>
<summary>❌ "ANVEVOICE_API_KEY is not set"</summary>

**Cause:** Environment variable not configured

**Fix:**
```bash
# Check if set
echo $ANVEVOICE_API_KEY

# Set it
openclaw config set ANVEVOICE_API_KEY anvk_your_key_here

# Or export
export ANVEVOICE_API_KEY=anvk_your_key_here
```
</details>

<details>
<summary>❌ "Authentication failed" (401)</summary>

**Cause:** Invalid API key

**Fix:**
1. Verify key starts with `anvk_`
2. Check key is complete (no truncation)
3. Generate a new key at anvevoice.com/developer
4. Ensure no extra spaces in the key
</details>

<details>
<summary>❌ "Rate limited" (429)</summary>

**Cause:** Too many requests

**Fix:**
- Wait a few seconds and retry
- The skill has built-in retry logic
- Consider upgrading your plan for higher limits
</details>

<details>
<summary>❌ Widget not appearing on website</summary>

**Fix:**
1. Check embed code is pasted before `</body>`
2. Verify bot_id is correct in the embed code
3. Check browser console for JavaScript errors
4. Ensure no ad-blocker is blocking the script
5. Try hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
</details>

<details>
<summary>❌ Bot not responding to voice</summary>

**Fix:**
1. Check microphone permissions in browser
2. Ensure HTTPS is enabled (required for microphone)
3. Try clicking the microphone icon manually
4. Check if bot status is "active" (not paused)
</details>

### Getting Help

| Channel | Response Time | Best For |
|---------|--------------|----------|
| **Email** | hello@anvevoice.com | General questions, billing |
| **Documentation** | anvevoice.com/help | Self-service guides |
| **Dashboard** | anvevoice.com/dashboard | Bot management, analytics |

---

## Support

- 🌐 **Website:** [anvevoice.com](https://anvevoice.com)
- 📚 **Documentation:** [anvevoice.com/help](https://anvevoice.com/help)
- 🎮 **Dashboard:** [anvevoice.com/dashboard](https://anvevoice.com/dashboard)
- 🔑 **API Keys:** [anvevoice.com/developer](https://anvevoice.com/developer)
- 💬 **Email:** hello@anvevoice.com

---

## 🔒 Security

This skill has been scanned and verified by **VirusTotal** — the industry's leading malware analysis platform.

### VirusTotal Scan Results

| Metric | Result |
|--------|--------|
| **Detection Rate** | **0/62** — Clean |
| **File** | `SKILL.md` (16.63 KB) |
| **Hash** | `f3c788a5cfa2a01b67edd6af451ee6748944818f20b7d51203ecf5cf8d4c837b` |
| **Scan Date** | Feb 21, 2026 |
| **Status** | ✅ **No security vendors flagged this file as malicious** |

### Verified By Leading Security Vendors

✅ Microsoft &nbsp; ✅ Google &nbsp; ✅ Kaspersky &nbsp; ✅ BitDefender &nbsp; ✅ Avast/AVG &nbsp; ✅ McAfee &nbsp; ✅ Symantec &nbsp; ✅ ESET-NOD32 &nbsp; ✅ Malwarebytes &nbsp; ✅ ClamAV &nbsp; **+ 52 others**

**[View Full Scan Report →](https://www.virustotal.com/gui/file/f3c788a5cfa2a01b67edd6af451ee6748944818f20b7d51203ecf5cf8d4c837b?nocache=1)**

---

## License

MIT — see [LICENSE](./LICENSE)

---

<p align="center">
  <b>Ready to add voice AI to your website?</b><br>
  <a href="https://anvevoice.com/developer">Get Started →</a>
</p>
