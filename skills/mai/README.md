# Mai

Mai is a local-first AI shopping matchmaking agent for OpenClaw and Hermes. Merchants can publish products and manage inventory; buyers can discover merchants and products, compare prices, discuss with sellers, read reviews, and create trackable orders.

Mai records transactions but does not custody funds directly. Local mode tracks external payment URLs and references. Registry mode records PSP-backed payment holds, releases, and refunds so the agent can support escrow-like workflows without pretending to be a licensed payment processor.

## Discovery Model

Mai now supports two discovery modes:

- Local-first: one agent searches its own `mai.json`.
- Registry-backed: merchants push their local store to a Mai registry; buyers search the registry; buyer messages and draft orders are stored in the registry; merchants pull their inbox back into the local store.

## Install Locally

After ClawHub publication, install the pair:

```bash
clawhub --workdir ~/.openclaw/workspace --dir skills install mai
openclaw plugins install clawhub:mai-plugin
```

`mai` is the workflow skill. `mai-plugin` is the optional lightweight OpenClaw native bridge for tools and `/mai` command support.

Install only the OpenClaw skill:

```bash
clawhub --workdir ~/.openclaw/workspace --dir skills install mai
```

One-command local install for both OpenClaw and Hermes:

```bash
cd /Users/jianghaidong/coding/mai
bash scripts/install.sh --both
```

OpenClaw only:

```bash
cd /Users/jianghaidong/coding/mai
bash scripts/install.sh --openclaw
```

Hermes only:

```bash
cd /Users/jianghaidong/coding/mai
bash scripts/install.sh --hermes
```

Hermes publish:

```bash
hermes skills publish ./mai --to github --repo <owner>/<repo>
```

Manual install paths:

- OpenClaw: `~/.openclaw/workspace/skills/mai`
- Hermes: `~/.hermes/skills/commerce/mai`

After installing, restart OpenClaw/Hermes if the running session does not automatically refresh skills. In Hermes, you can explicitly preload Mai with:

```bash
hermes -s mai
```

## Verify

```bash
cd mai
bash scripts/verify.sh
```

## Quick Start

```bash
python3 scripts/mai.py merchant create --id seller-a --name "West Lake Tea" --city Hangzhou --contact "wechat:westlake" --tags "tea,gift"
python3 scripts/mai.py product add --merchant seller-a --sku tea-a --title "Longjing Gift Box" --price 88 --stock 5 --category tea --tags "longjing,gift"
python3 scripts/mai.py search products --query "longjing tea" --format json
python3 scripts/mai.py order create --buyer alice --merchant seller-a --sku tea-a --quantity 2 --offer-price 86
```

Default data path: `~/.local/share/mai/mai.json`.
Use `--data ./mai-demo.json` to keep a local test database.

## Registry Marketplace

Start a registry service:

```bash
python3 scripts/mai_registry.py issue-key --data ./mai-registry.json --token admin-token --role admin --subject ops-admin
python3 scripts/mai_registry.py issue-key --data ./mai-registry.json --token seller-token --role merchant --subject seller-a --merchant-id seller-a
python3 scripts/mai_registry.py issue-key --data ./mai-registry.json --token buyer-token --role buyer --subject alice --buyer-id alice
python3 scripts/mai_registry.py serve --data ./mai-registry.json --host 127.0.0.1 --port 8765 --rate-limit-per-minute 60
```

Merchant agent publishes to registry:

```bash
python3 scripts/mai.py --data ./seller.json registry push --url http://127.0.0.1:8765 --api-key seller-token
```

Buyer agent searches and contacts the merchant:

```bash
python3 scripts/mai.py --data ./buyer.json registry search-products --url http://127.0.0.1:8765 --query "longjing tea" --format json
python3 scripts/mai.py --data ./buyer.json registry message --url http://127.0.0.1:8765 --api-key buyer-token --buyer alice --merchant seller-a --sku tea-a --text "Can this ship today?"
python3 scripts/mai.py --data ./buyer.json registry order --url http://127.0.0.1:8765 --api-key buyer-token --buyer alice --merchant seller-a --sku tea-a --quantity 2 --offer-price 86
python3 scripts/mai.py --data ./buyer.json registry payment-hold --url http://127.0.0.1:8765 --api-key buyer-token --buyer alice --order ORD-0001
```

Merchant agent pulls new demand:

```bash
python3 scripts/mai.py --data ./seller.json registry pull --url http://127.0.0.1:8765 --api-key seller-token --merchant seller-a
```

Admin releases or refunds held payments after fulfillment or dispute review:

```bash
python3 scripts/mai.py --data ./ops.json registry payment-release --url http://127.0.0.1:8765 --api-key admin-token --payment PAY-0001
python3 scripts/mai.py --data ./ops.json registry payment-refund --url http://127.0.0.1:8765 --api-key admin-token --payment PAY-0001
```

## Public Marketplace Controls

The registry includes the minimum controls needed before a public pilot:

- API keys are stored as salted hashes.
- Merchant keys can only push/pull their own merchant scope.
- Buyer keys can only create buyer-scoped messages, orders, and payment holds.
- Admin keys are required for moderation decisions and payment release/refund.
- Public search is allowed, but every request is rate-limited by API key or client IP.
- Risky products are hidden in `pending_review` until an admin approves them.
- Payment custody uses a PSP-backed state machine. The bundled `demo` provider records holds, releases, and refunds for development only.

For live money movement, replace the demo provider with a licensed payment service provider integration such as Stripe Connect, Adyen for Platforms, or another provider suitable for the operating jurisdiction. Mai must not directly hold customer funds.

## Docker Deployment

```bash
cd mai
docker compose --env-file registry.example.env up --build
```

Then issue initial API keys inside the container:

```bash
docker compose exec mai-registry python3 scripts/mai_registry.py issue-key --data /data/mai-registry.json --token admin-token --role admin --subject ops-admin
docker compose exec mai-registry python3 scripts/mai_registry.py issue-key --data /data/mai-registry.json --token seller-token --role merchant --subject seller-a --merchant-id seller-a
docker compose exec mai-registry python3 scripts/mai_registry.py issue-key --data /data/mai-registry.json --token buyer-token --role buyer --subject alice --buyer-id alice
```

For public traffic, run the container behind HTTPS and store real tokens in a secret manager rather than shell history.

## Transaction Flow

Happy path:

```text
draft -> quoted -> confirmed -> payment_pending -> paid_external -> fulfilled -> completed
```

Dispute path:

```text
disputed -> resolved/refunded/cancelled
```

Inventory is reserved when an order becomes `confirmed`. Mai itself does not hold funds; registry payments are PSP custody records. The bundled demo provider is not real card charging, refunding, or payment authentication.
