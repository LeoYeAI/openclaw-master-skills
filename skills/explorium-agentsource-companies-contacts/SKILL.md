---
name: agentsource
description: "Use this skill when the user wants to find companies (businesses) or people (contacts/prospects/leads) using the AgentSource B2B database. Trigger keywords include: find companies, find leads, find prospects, find contacts, B2B search, sales prospecting, market research, export to CSV, company events, funding signals, hiring signals, buying intent, intent signals, who is hiring, companies using [technology], decision makers at, CTO/CMO/VP of, enrich companies, enrich contacts, company firmographics, technographics, tech stack, Series A/B/C companies, target list. Requires: EXPLORIUM_API_KEY (env var or ~/.agentsource/config.json)."
metadata:
  primary_credential: "EXPLORIUM_API_KEY (env var or ~/.agentsource/config.json) — your Explorium AgentSource API key. Get one at https://developers.explorium.ai/reference/setup/getting_your_api_key"
  data_sent_to_remote: "Search filters, entity IDs, and optional call_reasoning (opt-in) are sent to https://api.explorium.ai/v1/. See README Data & Privacy for full details."
---

# AgentSource Skill

You help users find B2B companies and professionals using the AgentSource API. You manage the complete workflow from query parsing through confirmation and CSV export.

All API operations go through the `agentsource` CLI tool (`agentsource.py`). The CLI is discovered at the start of every session and stored in `$CLI` — it works across all environments (Claude Code, Cowork, OpenClaw, and others). The CLI calls the AgentSource REST API at `https://api.explorium.ai/v1/`. Results are written to temp files — you run the CLI, read the temp file it outputs, and use that data to guide the conversation.

---

## Prerequisites

Before starting any workflow:

1. **Find the CLI** — check the two known install locations:
   ```bash
   CLI=$(python3 -c "
   import pathlib
   candidates = [
     pathlib.Path.home() / '.agentsource/bin/agentsource.py',          # setup.sh install
     pathlib.Path.home() / '.local-plugins/agentsource-plugin/bin/agentsource.py',  # OpenClaw plugin dir
   ]
   found = next((str(p) for p in candidates if p.exists()), '')
   print(found)
   ")
   echo "CLI=$CLI"
   ```
   If nothing is found, tell the user to run `./setup.sh` first.

2. **Verify API key** — the CLI accepts the key in two ways:
   - **Environment variable** (recommended for CI / shared environments): `export EXPLORIUM_API_KEY=<key>`
   - **Saved config** (recommended for interactive use): run `python3 "$CLI" config --api-key <key>` once

   Check by running a free API call:
   ```bash
   RESULT=$(python3 "$CLI" statistics --entity-type businesses --filters '{"country_code":{"values":["us"]}}')
   python3 -c "import json; d=json.load(open('$RESULT')); print(d.get('error_code','OK'))"
   ```
   - Prints `OK` (or any non-auth value) → key is set, proceed.
   - Prints `AUTH_MISSING` → show this message **exactly** (do **not** ask the user to paste or type their API key in chat — API keys should never be shared in conversation):

     > To get started, you'll need to set your **Explorium AgentSource API key**.
     >
     > **Do not share your API key in this chat.** Instead, set it securely using one of these methods:
     >
     > **Option 1 — Environment variable (recommended):**
     > ```bash
     > export EXPLORIUM_API_KEY="your-key-here"
     > # Add to ~/.zshrc or ~/.bashrc to persist across sessions
     > ```
     >
     > **Option 2 — CLI config (saves to `~/.agentsource/config.json`, mode 600):**
     > ```bash
     > python3 <path-to-agentsource.py> config --api-key your-key-here
     > ```
     >
     > Need a key? Visit [developers.explorium.ai](https://developers.explorium.ai/reference/setup/getting_your_api_key) for instructions.
     >
     > Once the key is set, run your request again and I'll pick it up automatically.

     After the user sets the key via their terminal, re-run the statistics check to confirm it's detected.

---

## CLI Execution Pattern

At the start of **every** workflow, generate a plan ID and capture the user's query:
```bash
PLAN_ID=$(python3 -c "import uuid; print(uuid.uuid4())")
QUERY="find 500 product managers from healthcare companies in the US"
```

Optionally pass `--plan-id` and `--call-reasoning` to group related API calls in Explorium's server-side logs.

> **Privacy note:** `--call-reasoning` sends the user's query text to `api.explorium.ai` as part of the request metadata. Only pass it if the user has consented to this. If omitted, the API call is made without that context.

```bash
RESULT=$(python3 "$CLI" <command> <args> \
  --plan-id "$PLAN_ID" \
  --call-reasoning "$QUERY")   # optional — omit if user has not consented to query logging
# $RESULT is a path like /tmp/agentsource_1234567_fetch.json
cat "$RESULT"
```

To extract a single field:
```bash
python3 -c "import sys,json; d=json.load(open('$RESULT')); print(d['field_name'])"
```

---

## The Complete Workflow

### STEP 1 — Parse Query into Filters

Analyze the user's natural language and map it to API filters. Consult `references/filters.md` for the full catalog.

**Entity type decision**:
- `prospects` — user mentions people, contacts, decision-makers, names, job titles
- `businesses` — user mentions only companies, organizations, accounts

**Identify which filters to use**, then check for autocomplete requirements.

For each of these fields, you **MUST** call `autocomplete` first (see Step 1a):
- `linkedin_category`, `naics_category`, `job_title`, `business_intent_topics`, `tech_stack`, `city`

**Key mutual exclusions** (see `references/filters.md`):
- Never combine `linkedin_category` + `naics_category`
- Never combine `country_code` + `region_country_code`
- Never combine `job_title` + `job_level`/`job_department`

---

### STEP 1a — Autocomplete Required Fields

For every field that requires autocomplete, run it before building filters. **Always pass `--semantic`** to use semantic search:

```bash
RESULT=$(python3 "$CLI" autocomplete \
  --entity-type businesses \
  --field linkedin_category \
  --query "software" \
  --semantic \
  --plan-id "$PLAN_ID" \
  --call-reasoning "$QUERY")
cat "$RESULT"
```

Read the `results` array. Use the **exact `value` strings returned** in your filters — not the user's raw words. If autocomplete returns empty, try a broader query once; if still empty, skip that filter.

---

### STEP 2 — Market Sizing (Free — No Credits)

Get a count before spending any credits:

```bash
RESULT=$(python3 "$CLI" statistics \
  --entity-type businesses \
  --filters '{"linkedin_category":{"values":["software development"]},"company_size":{"values":["51-200","201-500"]}}')
cat "$RESULT"
```

Present `total_results` to the user. If >50,000, suggest narrowing filters.

---

### STEP 3 — Sample Fetch (5–10 Results)

```bash
FETCH_RESULT=$(python3 "$CLI" fetch \
  --entity-type businesses \
  --filters '{"linkedin_category":{"values":["software development"]},"country_code":{"values":["us"]}}' \
  --limit 10)
cat "$FETCH_RESULT"
```

Record:
- `total_results` — total matching entities in the database
- `total_fetched` — number fetched into this result file
- `sample` — preview rows (first 10)

---

### STEP 4 — Present Sample and WAIT for Confirmation

**This step is mandatory — never skip it.**

Show the user:
1. Total results found (e.g., "Found 177,588 matching businesses")
2. Credit cost estimate (~1 credit per entity fetched)
3. Sample rows as a markdown table
4. Ask explicitly:

> "Would you like to:
> - **Fetch all [N] results and export to CSV**
> - **Add enrichments** (firmographics, tech stack, funding, contacts, etc.)
> - **Add event data** (funding rounds, hiring signals, etc.)
> - **Refine the search** (adjust filters)"

**NEVER proceed to a full fetch or CSV export without the user's explicit confirmation.**

---

### STEP 5 — Full Fetch (after confirmation)

Re-run `fetch` with the desired total count. The CLI paginates automatically in batches of 500:

```bash
FETCH_RESULT=$(python3 "$CLI" fetch \
  --entity-type businesses \
  --filters '{"linkedin_category":{"values":["software development"]},"country_code":{"values":["us"]}}' \
  --limit 1000)
cat "$FETCH_RESULT"
```

The result file has `data` (array of all entities), `total_fetched`, `pages_fetched`.

---

### STEP 6 (Optional) — Enrich

Only if user requested enrichment. Consult `references/enrichments.md`. The `enrich` command reads a fetch result file, runs bulk enrichment in batches of 50, and merges enrichment data back into each entity:

```bash
ENRICH_RESULT=$(python3 "$CLI" enrich \
  --input-file "$FETCH_RESULT" \
  --enrichments "firmographics,technographics")
cat "$ENRICH_RESULT"
```

For prospects (to get emails and phones):
```bash
ENRICH_RESULT=$(python3 "$CLI" enrich \
  --input-file "$FETCH_RESULT" \
  --enrichments "contacts_information,profiles")
cat "$ENRICH_RESULT"
```

After enrichment, the result file has the same structure but with enrichment data merged into each entity. Show the enriched `sample` (first 5 entries) to the user.

---

### STEP 7 (Optional) — Event Data

Only for businesses. Consult `references/events.md` for event types. The `events` command reads a fetch result file and retrieves events for all `business_id` values in it:

```bash
EVENTS_RESULT=$(python3 "$CLI" events \
  --input-file "$FETCH_RESULT" \
  --event-types "new_funding_round,hiring_in_engineering_department" \
  --since "2025-11-01")
cat "$EVENTS_RESULT"
```

The result file has `data` (array of event objects, each with `business_id`, `event_name`, `event_time`, and event-specific fields).

---

### STEP 8 — Export to CSV

Convert the fetch (or enrich) result file to a local CSV:

```bash
CSV_RESULT=$(python3 "$CLI" to-csv \
  --input-file "$FETCH_RESULT" \
  --output ~/Downloads/us_saas_companies.csv)
cat "$CSV_RESULT"
```

Read `csv_path` and `row_count` from the result and present them to the user:

> "Your CSV is ready: `~/Downloads/us_saas_companies.csv` — 1,000 rows, 18 columns."

For events, convert the events result file separately:
```bash
python3 "$CLI" to-csv \
  --input-file "$EVENTS_RESULT" \
  --output ~/Downloads/funding_events.csv
```

---

## Error Handling

If a result file contains `"success": false`, read `error_code`:

| `error_code` | Action |
|---|---|
| `AUTH_MISSING` / `AUTH_FAILED` (401) | Ask user to set `EXPLORIUM_API_KEY` or run `config --api-key` |
| `FORBIDDEN` (403) | Show error message; may be a credit or permission issue |
| `BAD_REQUEST` (400) / `VALIDATION_ERROR` (422) | Fix the filter — check `references/filters.md`; run `autocomplete` if needed |
| `RATE_LIMIT` (429) | Wait 10 seconds and retry once |
| `SERVER_ERROR` (5xx) | Wait 5 seconds and retry once; report if it persists |
| `NETWORK_ERROR` | Ask user to check connectivity and retry |

---

## Special Workflows

### Start from an Existing CSV

When a user has an existing list (companies or contacts) and wants to enrich or extend it:

**Step 1 — Convert the CSV to a JSON temp file** (full data stays out of context):
```bash
CSV_JSON=$(python3 "$CLI" from-csv \
  --input ~/Downloads/my_accounts.csv)
```

**Step 2 — Read ONLY the metadata into context** (columns + 5 sample rows — never `cat` the full file):
```bash
python3 -c "
import json
d = json.load(open('$CSV_JSON'))
print('rows:', d['total_rows'])
print('columns:', d['columns'])
print('sample:')
for r in d['sample']: print(r)
"
```

Inspect the column names and sample values. Use your judgment to map them to the correct API fields:
- **Businesses**: identify which column is the company name → `name`; which is the website/domain → `domain`
- **Prospects**: identify the person's name → `full_name` (or `first_name`+`last_name`); employer → `company_name`; contact → `email` or `linkedin`
  - **CRITICAL**: the prospect LinkedIn field is `"linkedin"` — **never** `"linkedin_url"` (that name is only valid for businesses)

**Step 3 — Match with your deduced column map** (batches automatically, 50 rows per call):
```bash
# For a company list — pass your deduced mapping explicitly:
MATCH_RESULT=$(python3 "$CLI" match-business \
  --input-file "$CSV_JSON" \
  --column-map '{"Company Name": "name", "Website URL": "domain"}' \
  --plan-id "$PLAN_ID" --call-reasoning "$QUERY")
python3 -c "import json; d=json.load(open('$MATCH_RESULT')); print('matched:', d['total_matched'], '/', d['total_input'])"

# For a contact list (note: LinkedIn field is "linkedin", NOT "linkedin_url"):
MATCH_RESULT=$(python3 "$CLI" match-prospect \
  --input-file "$CSV_JSON" \
  --column-map '{"Full Name": "full_name", "Employer": "company_name", "Work Email": "email", "LinkedIn": "linkedin"}' \
  --plan-id "$PLAN_ID" --call-reasoning "$QUERY")
```

If `--column-map` is omitted, the CLI falls back to auto-alias matching on lowercased column names (e.g. `company_name`, `domain`, `website` are recognised automatically). Always prefer the explicit map for better match rates.

**Step 4 — Continue the normal workflow**

The match result has the same `data` array format as a `fetch` result, so it plugs directly into `enrich` or `events`:
```bash
ENRICH_RESULT=$(python3 "$CLI" enrich \
  --input-file "$MATCH_RESULT" \
  --enrichments "firmographics,technographics" \
  --plan-id "$PLAN_ID" --call-reasoning "$QUERY")
```

---

### Match a User-Provided List (no CSV)

When a user types a list of companies or people directly in their message (e.g. "enrich Salesforce, HubSpot, and Notion" or "get emails for John Smith at Apple and Jane Doe at Google"), construct the match payload inline from what they wrote — no CSV needed.

**Company list → `match-business`:**
```bash
MATCH_RESULT=$(python3 "$CLI" match-business \
  --businesses '[
    {"name": "Salesforce", "domain": "salesforce.com"},
    {"name": "HubSpot",    "domain": "hubspot.com"},
    {"name": "Notion",     "domain": "notion.so"}
  ]' \
  --plan-id "$PLAN_ID" --call-reasoning "$QUERY")
python3 -c "import json; d=json.load(open('$MATCH_RESULT')); print('matched:', d['total_matched'], '/', d['total_input'])"
```

Include as many identifiers as the user gave: `name`, `domain`, or both. More fields = better match rate.

**Contact list → `match-prospect`:**
```bash
MATCH_RESULT=$(python3 "$CLI" match-prospect \
  --prospects '[
    {"full_name": "John Smith",  "company_name": "Apple"},
    {"full_name": "Jane Doe",    "company_name": "Google", "email": "jane@google.com"}
  ]' \
  --plan-id "$PLAN_ID" --call-reasoning "$QUERY")
```

After matching, pipe the result directly into `enrich` or `to-csv` as normal.

---

### Find Prospects at Specific Companies

1. Match companies to get their `business_id` values:
   ```bash
   RESULT=$(python3 "$CLI" match-business \
     --businesses '[{"name":"Salesforce","domain":"salesforce.com"}]')
   cat "$RESULT"
   ```
2. Extract the `business_id` and use it as a filter in the prospect fetch:
   ```bash
   BID=$(python3 -c "import json; print(json.load(open('$RESULT'))['data'][0]['business_id'])")
   FETCH_RESULT=$(python3 "$CLI" fetch \
     --entity-type prospects \
     --filters "{\"business_id\":{\"values\":[\"$BID\"]},\"job_level\":{\"values\":[\"c-suite\"]}}")
   ```

### Companies → Prospects (Chaining)

1. Fetch target companies
2. Extract their `business_id` values from the result file
3. Pass them in the `business_id` filter when fetching prospects

### Buying Intent

When user wants to find companies showing interest in a product/topic:
1. `autocomplete --entity-type businesses --field business_intent_topics --query "CRM" --semantic` → get standardized values
2. Use them in the `business_intent_topics` filter in `fetch`

---

## Pagination Notes

The `fetch` command paginates automatically. With `--limit 1000`:
- Issues page 1 (500 records) then page 2 (500 records)
- Writes all 1000 into a single result file
- `pages_fetched` in the result tells you how many pages were used
- `total_results` is the full database count matching your filters

The `enrich` command handles its own batching (50 IDs per API call) internally.
The `events` command batches 40 business IDs per API call internally.
