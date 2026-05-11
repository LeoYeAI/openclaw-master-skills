---
name: creditclaw-procurement
version: 2.6.0
updated: 2026-03-13
description: "Discover vendors and merchants — find the right skill for any purchase."
parent: https://creditclaw.com/SKILL.md
api_base: https://creditclaw.com/api/v1
credentials: [CREDITCLAW_API_KEY]
---

# CreditClaw — Procurement Skills

> **Companion file.** For registration, spending permissions, and the full API reference, see [SKILL.md](https://creditclaw.com/SKILL.md).

**Base URL:** `https://creditclaw.com/api/v1`

---

## Discover Vendors

Find vendors and merchants that CreditClaw has verified checkout skills for:

```bash
curl "https://creditclaw.com/api/v1/bot/skills" \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

**Query parameters** (all optional):

| Parameter | Description | Example |
|-----------|-------------|---------|
| `search` | Search by name or slug | `?search=amazon` |
| `category` | Filter by category | `?category=saas` |
| `checkout` | Filter by checkout method (comma-separated) | `?checkout=guest,api` |
| `capability` | Filter by capability (comma-separated, all must match) | `?capability=returns,tracking` |
| `maturity` | Filter by skill maturity (comma-separated) | `?maturity=verified,stable` |

Response:
```json
{
  "vendors": [
    {
      "slug": "cloudserve-pro",
      "name": "CloudServe Pro",
      "category": "saas",
      "url": "https://cloudserve.example.com",
      "checkout_methods": ["guest", "api"],
      "capabilities": ["returns", "tracking"],
      "maturity": "verified",
      "agent_friendliness": 0.85,
      "guest_checkout": true,
      "bulk_pricing": false,
      "free_shipping_above": null,
      "skill_url": "https://creditclaw.com/api/v1/bot/skills/cloudserve-pro",
      "catalog_url": "https://creditclaw.com/skills/cloudserve-pro",
      "version": "1.0.0",
      "last_verified": "2026-03-01",
      "success_rate": 0.92
    }
  ],
  "total": 1,
  "categories": ["saas", "retail", "marketplace", "food", "software", "payments"]
}
```

## Get a Vendor Skill

Once you've found a vendor, fetch its full checkout skill:

```bash
curl "https://creditclaw.com/api/v1/bot/skills/cloudserve-pro" \
  -H "Authorization: Bearer $CREDITCLAW_API_KEY"
```

Returns the vendor's complete checkout instructions as Markdown — step-by-step guidance for purchasing from that merchant, including any vendor-specific fields, checkout flow, and known quirks.

**Key response fields from the list endpoint:**

| Field | Meaning |
|-------|---------|
| `agent_friendliness` | 0–1 score of how easy the checkout is for an agent |
| `guest_checkout` | Whether the vendor supports checkout without an account |
| `maturity` | Skill reliability: `verified`, `stable`, `beta`, or `experimental` |
| `success_rate` | Historical success rate for agent checkouts (null if insufficient data) |
| `skill_url` | Full URL to fetch the vendor's detailed checkout skill |
