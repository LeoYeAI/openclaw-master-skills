# AgentSource Plugin for AI Agents

B2B prospecting and company intelligence using the AgentSource API. Describe who you're looking for in plain English — your AI agent guides you through the workflow, shows you a preview, and exports to CSV.

Works with **Claude Code**, **Claude Cowork**, **OpenClaw**, and any other AI agent environment that supports skills and plugins.

## How It Works

1. You describe a target in natural language
2. Your AI agent (guided by the `agentsource` skill) parses your intent into API filters
3. It shows you market statistics and a data sample before touching any credits
4. You confirm — then it fetches your results and exports a downloadable CSV

All API responses are written to temp files so that large payloads never appear in the conversation context window, enabling scale queries of thousands of records.

## Requirements

- Python 3.8+ (standard library only — no `pip` required)
- An Explorium AgentSource API key
- Any AI agent environment that supports skills/plugins (Claude Code, Cowork, OpenClaw, etc.)

---

## Quick Start

### 1. Install
```bash
./setup.sh
```

This installs the CLI to `~/.agentsource/bin/agentsource.py` and optionally saves your API key to `~/.agentsource/config.json` (permissions 600, owner read-only).

### 2. Set your API key

**Do not share your API key in the AI chat.** Set it securely using one of these methods:

**Option A — Environment variable** (recommended for persistent shell setups):
```bash
export EXPLORIUM_API_KEY=your_api_key_here
# Add to ~/.zshrc or ~/.bashrc to persist across sessions
```

**Option B — CLI config command** (saves to `~/.agentsource/config.json`, mode 600):
```bash
python3 ~/.agentsource/bin/agentsource.py config --api-key your_api_key_here
```

Don't have a key yet? Visit [developers.explorium.ai](https://developers.explorium.ai/reference/setup/getting_your_api_key) for instructions.

### 3. Open your AI agent and describe your target
```
Find CTOs at Series B SaaS companies in California
```
```
Show me fintech companies using Stripe with 50–200 employees
```
```
Get emails for VP Sales at companies that recently raised Series A
```
```
Find companies hiring engineers that use Kubernetes
```

---

## File Structure

```
agentsource-plugin/
├── bin/
│   └── agentsource.py               # The CLI (pure Python stdlib)
├── references/
│   ├── filters.md                   # All available filters with valid values
│   ├── enrichments.md               # Enrichment types and credit costs
│   └── events.md                    # Business/prospect trigger event types
├── SKILL.md                         # Workflow logic — how the AI agent uses the API
├── setup.sh                         # Installation script
└── README.md
```

---

## CLI Reference

All commands write results to `/tmp/agentsource_<timestamp>_<command>.json` and print only the file path to stdout.

### API Key Config
```bash
python3 ~/.agentsource/bin/agentsource.py config --api-key <key>
```

### Autocomplete (required for certain filter fields)
```bash
# Always pass --semantic for best results
python3 ~/.agentsource/bin/agentsource.py autocomplete \
  --entity-type businesses \
  --field linkedin_category --query "software" --semantic
```

### Market Sizing (free — no credits)
```bash
python3 ~/.agentsource/bin/agentsource.py statistics \
  --entity-type businesses \
  --filters '{"company_size":{"values":["51-200"]}}'
```

### Fetch (auto-paginates in batches of 500)
```bash
# Sample — 10 results
python3 ~/.agentsource/bin/agentsource.py fetch \
  --entity-type businesses \
  --filters '{"country_code":{"values":["us"]},"company_size":{"values":["51-200"]}}' \
  --limit 10

# Large query — 3,000 records (6 pages, automatic)
python3 ~/.agentsource/bin/agentsource.py fetch \
  --entity-type businesses \
  --filters '{"country_code":{"values":["us"]}}' \
  --limit 3000
```

### Enrich
```bash
# Enrich companies with firmographics and tech stack
python3 ~/.agentsource/bin/agentsource.py enrich \
  --input-file /tmp/agentsource_xxx_fetch.json \
  --enrichments "firmographics,technographics"

# Enrich prospects with emails and phones
python3 ~/.agentsource/bin/agentsource.py enrich \
  --input-file /tmp/agentsource_xxx_fetch.json \
  --enrichments "contacts_information,profiles"
```

### Events
```bash
python3 ~/.agentsource/bin/agentsource.py events \
  --input-file /tmp/agentsource_xxx_fetch.json \
  --event-types "new_funding_round,hiring_in_engineering_department" \
  --since "2025-01-01"
```

### Export to CSV
```bash
python3 ~/.agentsource/bin/agentsource.py to-csv \
  --input-file /tmp/agentsource_xxx_fetch.json \
  --output ~/Downloads/results.csv
```

### Entity Matching
```bash
# Match specific companies by name/domain
python3 ~/.agentsource/bin/agentsource.py match-business \
  --businesses '[{"name":"Salesforce","domain":"salesforce.com"}]'

# Match from an existing CSV
python3 ~/.agentsource/bin/agentsource.py match-business \
  --input-file /tmp/agentsource_xxx_from_csv.json \
  --column-map '{"Company":"name","Website":"domain"}'

# Match specific people
python3 ~/.agentsource/bin/agentsource.py match-prospect \
  --prospects '[{"full_name":"Jane Doe","company_name":"Acme Corp","email":"jane@acme.com"}]'

# Match prospects from a CSV
python3 ~/.agentsource/bin/agentsource.py match-prospect \
  --input-file /tmp/agentsource_xxx_from_csv.json \
  --column-map '{"Name":"full_name","Company":"company_name","LinkedIn":"linkedin","Email":"email"}'
```

### CSV Import
```bash
# Convert an existing CSV for use with match-business or match-prospect
python3 ~/.agentsource/bin/agentsource.py from-csv \
  --input ~/Downloads/my_accounts.csv
```

---

## Data & Privacy

### What is stored locally

| Location | Contents | Permissions |
|---|---|---|
| `~/.agentsource/config.json` | API key (if saved via `config` command) | 600 (owner read-only) |
| `/tmp/agentsource_*.json` | API result data | Cleaned up automatically by OS |

### What is sent to Explorium's API

All API calls go to `https://api.explorium.ai/v1/`. The following data is transmitted:

| Data | When sent |
|---|---|
| Your API key (as `api_key` header) | Every request |
| Search filters (e.g., country, company size) | `fetch`, `statistics`, `autocomplete` |
| Entity IDs for enrichment/events | `enrich`, `events` |
| Company/contact records for matching | `match-business`, `match-prospect` |
| `plan_id` (random UUID) | When `--plan-id` is passed (optional) |
| `call_reasoning` (your natural-language query) | **Only** when `--call-reasoning` is passed (opt-in) |

**Note on `call_reasoning`**: When the AI agent passes `--call-reasoning`, the text of your search query (e.g., "find CTOs at Series B SaaS companies") is sent to Explorium's server as request metadata for logging and support purposes. This is opt-in — if omitted, no query text is transmitted.

### What is NOT sent

- Conversation content or chat history
- File contents beyond what's needed for matching/enrichment
- Any data beyond what is documented above

---

## Troubleshooting

**"EXPLORIUM_API_KEY is not set"**
→ Run `python3 ~/.agentsource/bin/agentsource.py config --api-key <key>`, or `export EXPLORIUM_API_KEY=your_key`

**"CLI not found"**
→ Run `./setup.sh` from the plugin directory

**401 / Auth errors**
→ Verify your API key at [developers.explorium.ai](https://developers.explorium.ai/reference/setup/getting_your_api_key)

**400 / Bad request errors**
→ A filter value is invalid. Run `autocomplete --semantic` for the relevant field, or check `references/filters.md`

**Large queries timing out**
→ Reduce `--limit` or split the query by adding a narrower filter (country, company size, etc.)
