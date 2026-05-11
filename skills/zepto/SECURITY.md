# Security & Privacy

## Overview

This skill automates grocery ordering on Zepto.com through browser automation. It operates entirely within your local OpenClaw environment.

## What This Skill Does

- ✅ **Browser automation** on zepto.com (your local browser, your authenticated session)
- ✅ **Local order history** stored in `{SKILL_DIR}/order-history.json` to remember frequently ordered items
- ✅ **Payment link generation** via Zepto's Juspay gateway (sent to your WhatsApp)
- ✅ **Address confirmation** required before every order
- ✅ **Authentication** through Zepto's official Phone + OTP flow

## What This Skill Does NOT Do

- ❌ **No automatic payments** - You must manually click payment links and complete transactions
- ❌ **No external data transmission** - All data stays local except interactions with Zepto.com and your WhatsApp
- ❌ **No credential storage** - OTPs and passwords are never stored
- ❌ **No payment info access** - Skill only generates payment links, never handles payment details
- ❌ **No background jobs by default** - Optional one-time order status check only with explicit user approval

## Data Storage

### Local Files
- **`{SKILL_DIR}/order-history.json`** - Stores item names and order frequency for "usuals" recommendations
  - Format: `{ "item_name": order_count }`
  - Example: `{ "Milk": 5, "Bread": 3 }`
  - **Contains:** Product names and frequencies only
  - **Does NOT contain:** Prices, addresses, payment info, phone numbers

### Browser Session
- Managed by OpenClaw's browser profile
- Standard Chrome/Chromium data location
- Session cookies persist login between orders

## User Control

- ✅ You initiate all orders explicitly
- ✅ You approve each payment link before paying
- ✅ Address confirmation required before shopping
- ✅ Order history file can be deleted anytime (`rm order-history.json`)
- ✅ All browser actions visible in your profile
- ✅ No actions happen without your commands

## Permissions Required

- **Browser control** - Required for zepto.com automation
- **WhatsApp messaging** (optional) - For sending payment links
- **File write** - For storing order-history.json locally

## Privacy Best Practices

Before publishing or sharing this skill:
1. Delete or sanitize `order-history.json` if it contains personal shopping patterns
2. Review SKILL.md for any example addresses or personal data
3. Clear browser session if needed

## Threat Model

**Low Risk:**
- Skill operates locally within your OpenClaw environment
- No external API calls except Zepto.com (which you already use)
- No credential or payment data handling

**User Responsibilities:**
- Keep your OpenClaw environment secure
- Review payment links before clicking
- Monitor order confirmations from Zepto

## Questions or Concerns?

File an issue on ClawHub or contact the skill author.
