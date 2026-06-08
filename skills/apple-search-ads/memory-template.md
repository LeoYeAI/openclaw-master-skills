# Memory Template — Apple Search Ads

Create `~/apple-search-ads/memory.md` with this structure:

```markdown
# Apple Search Ads Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | done | declined

## Apps

<!-- Add each app being advertised -->
### App Name
- Adam ID: 123456789
- Category: Health & Fitness
- Target CPA: $5.00
- LTV estimate: $30
- Countries: US, UK, CA

## Active Campaigns

<!-- Track campaign structure -->
### [App] - US - Brand
- Status: Active
- Daily budget: $50
- CPA (7d): $3.20
- Notes: Performing well

### [App] - US - Category  
- Status: Active
- Daily budget: $100
- CPA (7d): $8.50
- Notes: Need to add negatives

## Learnings

<!-- What's working, what's not -->
- Brand keywords: CPA consistently under $4
- Generic keywords: Only "meditation app" profitable
- Competitor keywords: Not working, paused
- Search Match: Found 3 good keywords this month

## Optimization Log

<!-- Track changes and results -->
### YYYY-MM-DD
- Action: Added 15 negative keywords
- Result: CPA dropped 20% in 3 days

### YYYY-MM-DD
- Action: Increased brand bid from $2 to $3
- Result: Impression share increased 15%

## Preferences

<!-- User's preferences for how I help -->
- Reporting cadence: Weekly
- Proactive suggestions: Yes
- Budget alerts: When spend > 120% daily

## Notes

<!-- Internal observations -->
- User prefers high-level strategy over API details
- App has good ASO, screenshots are strong
- Main competitor is [X], they bid aggressively

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning their setup | Gather context, suggest improvements |
| `complete` | Know their full setup | Focus on optimization |
| `paused` | User said "not now" | Don't ask for more context |

## Credentials Template

Create `~/apple-search-ads/credentials.md`:

```markdown
# Apple Search Ads Credentials

⚠️ NEVER store actual secrets here. Use environment variables.

## Required Credentials

Get these from: https://app.searchads.apple.com/cm/app/settings/apicertificates

| Variable | Description | Where to Get |
|----------|-------------|--------------|
| `ASA_CLIENT_ID` | API client ID | API settings page |
| `ASA_TEAM_ID` | Your team ID | API settings page |
| `ASA_KEY_ID` | Key identifier | API settings page |
| `ASA_PRIVATE_KEY` | Private key (PEM) | Downloaded when created |
| `ASA_ORG_ID` | Organization ID | Account settings |

## Setting Environment Variables

```bash
# Add to ~/.zshrc or ~/.bashrc
export ASA_CLIENT_ID="your-client-id"
export ASA_TEAM_ID="your-team-id"
export ASA_KEY_ID="your-key-id"
export ASA_ORG_ID="your-org-id"

# For private key, reference a file
export ASA_PRIVATE_KEY="$(cat ~/.secrets/asa-private-key.pem)"
```

## Testing Connection

```bash
# After setting variables, test with:
source ~/apple-search-ads/scripts/get-token.sh
```
```

## Key Principles

- **No config keys visible** — use natural language, not "targetCPA: 5.00"
- **Learn from results** — track what optimizations worked
- **Most accounts stay `ongoing`** — always optimizing, that's fine
- Update `last` on each interaction
