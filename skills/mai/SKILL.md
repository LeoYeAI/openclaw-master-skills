---
name: mai
description: "AI shopping matchmaking agent for OpenClaw and Hermes. Use when merchants want to publish products, manage stock, answer buyer questions, and handle order requests; or when buyers want to discover merchants and products, compare prices, discuss with sellers, read reviews, and create trackable orders. Supports local-first transaction tracking and registry-backed PSP custody records."
---

# Mai

## Overview

Mai helps buyers and merchants complete shopping matchmaking through an AI agent. It keeps deterministic marketplace state in `scripts/mai.py` while the host model handles natural language, negotiation, summaries, and risk explanations.

Mai can run local-only or registry-backed. Use local-only for one agent's private catalog. Use registry-backed discovery when buyers and merchants are on different machines or agent profiles.

## Operating Principles

- Be neutral between buyer and merchant. Explain options, prices, review signals, inventory, and tradeoffs without fabricating availability.
- Treat payments as external or PSP-backed. Mai never directly holds funds. Local mode records payment URLs and references; registry mode records PSP custody events and must not claim success without PSP or external evidence.
- Confirm before irreversible steps. Ask for buyer confirmation before creating an order and merchant confirmation before reserving stock.
- Preserve negotiation context. Record important buyer/merchant messages with `message add` before forming or updating an order.
- Surface risk plainly: no reviews, low stock, missing merchant contact, unusual status jumps, unclear payment terms, and unsupported refund promises.
- Prefer short, actionable answers: recommendation, reason, risk, next action.

## Quick Start

Use the CLI helper for deterministic state:

```bash
python3 scripts/mai.py merchant create --id seller-a --name "West Lake Tea" --city Hangzhou --contact "wechat:westlake" --tags "tea,gift"
python3 scripts/mai.py product add --merchant seller-a --sku tea-a --title "Longjing Gift Box" --price 88 --stock 5 --category tea --tags "longjing,gift"
python3 scripts/mai.py search products --query "longjing tea" --format json
python3 scripts/mai.py compare --skus tea-a,tea-b --format json
python3 scripts/mai.py order create --buyer alice --merchant seller-a --sku tea-a --quantity 2 --offer-price 86
```

Default data path: `~/.local/share/mai/mai.json`.
Use `--data /path/to/mai.json` for a project-local or test database.

## Installation

Install the published OpenClaw pair:

```bash
clawhub --workdir ~/.openclaw/workspace --dir skills install mai
openclaw plugins install clawhub:mai-plugin
```

`mai` is the skill. `mai-plugin` is an optional lightweight OpenClaw native bridge for tools and `/mai` command support.

Local checkout install:

```bash
cd /Users/jianghaidong/coding/mai
bash scripts/install.sh --both
```

Install only one ecosystem:

```bash
bash scripts/install.sh --openclaw
bash scripts/install.sh --hermes
```

The installer creates symlinks:

- OpenClaw: `~/.openclaw/workspace/skills/mai`
- Hermes: `~/.hermes/skills/commerce/mai`

After installation, restart the host agent if it does not refresh skills automatically. Hermes can preload Mai with `hermes -s mai`.

## Registry Discovery

Run a registry marketplace:

```bash
python3 scripts/mai_registry.py issue-key --data ./mai-registry.json --token admin-token --role admin --subject ops-admin
python3 scripts/mai_registry.py issue-key --data ./mai-registry.json --token seller-token --role merchant --subject seller-a --merchant-id seller-a
python3 scripts/mai_registry.py issue-key --data ./mai-registry.json --token buyer-token --role buyer --subject alice --buyer-id alice
python3 scripts/mai_registry.py serve --data ./mai-registry.json --host 127.0.0.1 --port 8765 --rate-limit-per-minute 60
```

Merchant agents publish local supply:

```bash
python3 scripts/mai.py --data ./seller.json registry push --url http://127.0.0.1:8765 --api-key seller-token
```

Buyer agents discover supply and create demand:

```bash
python3 scripts/mai.py --data ./buyer.json registry search-products --url http://127.0.0.1:8765 --query "longjing tea" --format json
python3 scripts/mai.py --data ./buyer.json registry message --url http://127.0.0.1:8765 --api-key buyer-token --buyer alice --merchant seller-a --sku tea-a --text "Can this ship today?"
python3 scripts/mai.py --data ./buyer.json registry order --url http://127.0.0.1:8765 --api-key buyer-token --buyer alice --merchant seller-a --sku tea-a --quantity 2 --offer-price 86
python3 scripts/mai.py --data ./buyer.json registry payment-hold --url http://127.0.0.1:8765 --api-key buyer-token --buyer alice --order ORD-0001
```

Merchant agents pull buyer messages and draft orders:

```bash
python3 scripts/mai.py --data ./seller.json registry pull --url http://127.0.0.1:8765 --api-key seller-token --merchant seller-a
```

Read `references/registry-api.md` before changing registry integrations.

## Public Marketplace Controls

- Require API keys for merchant push/pull, buyer messages/orders/payment holds, moderation, and payment release/refund.
- Store only salted API key hashes in the registry file.
- Allow public search, but rate-limit every request by API key or client IP.
- Treat products with high risk scores as `pending_review`; do not show them in search until an admin approves them.
- Use `registry payment-hold` only as PSP-backed custody tracking. The bundled `demo` provider is not real money movement.
- Require an admin key for `registry payment-release` and `registry payment-refund`.
- Do not claim escrow, payment success, release, or refund unless the PSP adapter or external evidence confirms it.

## Merchant Workflow

1. Create or identify the merchant profile:
   `python3 scripts/mai.py merchant create --id ID --name NAME --city CITY --contact CONTACT --tags "A,B"`
2. Publish products:
   `python3 scripts/mai.py product add --merchant ID --sku SKU --title TITLE --price N --stock N`
3. Adjust stock after physical changes:
   `python3 scripts/mai.py product stock --sku SKU --merchant ID --adjust N --reason "restock or correction"`
4. Record important buyer questions and seller replies:
   `python3 scripts/mai.py message add --buyer BUYER --merchant ID --sku SKU --sender merchant --text "..."`
5. Quote and confirm orders only when inventory and terms are clear:
   `python3 scripts/mai.py order quote ...`
   `python3 scripts/mai.py order update --order ORD-0001 --status confirmed --actor merchant`

## Buyer Workflow

1. Discover merchants:
   `python3 scripts/mai.py search merchants --query "tea hangzhou" --format json`
2. Search products:
   `python3 scripts/mai.py search products --query "longjing gift" --max-price 100 --format json`
3. Compare shortlisted SKUs:
   `python3 scripts/mai.py compare --skus sku-a,sku-b --format json`
4. Inspect reviews:
   `python3 scripts/mai.py review list --merchant ID --format json`
5. Record discussion before ordering:
   `python3 scripts/mai.py message add --buyer BUYER --merchant ID --sku SKU --text "..."`
6. Create a draft order after buyer confirmation:
   `python3 scripts/mai.py order create --buyer BUYER --merchant ID --sku SKU --quantity N`

## Transaction Model

Mai tracks transactions without custody:

`draft -> quoted -> confirmed -> payment_pending -> paid_external -> fulfilled -> completed`

Disputes can move through:

`disputed -> resolved/refunded/cancelled`

Stock is reserved when an order becomes `confirmed`. Local-only payments are recorded as `payment_url` and `payment_reference`. Registry payments are PSP custody records; the agent must say the bundled `demo` provider is not real escrow or money movement.

Read `references/transaction-model.md` when handling non-happy-path order, refund, dispute, or payment questions.
Read `references/data-schema.md` when integrating Mai with a future hosted marketplace or sync service.

## Output Expectations

For product discovery, answer with:
- best match and why
- price and merchant comparison
- availability and shipping notes
- review/trust signals
- risks or missing facts
- one next action

For merchant operations, answer with:
- action completed or blocked
- changed product/order/inventory identifier
- current stock or status
- next operational step

For order updates, answer with:
- previous status and new status
- whether stock was reserved or released
- payment evidence recorded, if any
- what must happen next

## Verification

Before claiming the package is ready:

- `python3 scripts/mai.py --help`
- `python3 scripts/mai_registry.py --help`
- `bash scripts/install.sh --both --dry-run`
- `python3 -m unittest discover -s tests`
- `bash scripts/verify.sh`
- Confirm `SKILL.md` has no scaffold placeholders.
- Confirm `README.md`, `package.json`, `clawhub.json`, `plugins/mai-plugin/openclaw.plugin.json`, and `agents/openai.yaml` use the `mai` and `mai-plugin` names consistently.
