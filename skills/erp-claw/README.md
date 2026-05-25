# ERPClaw — AI-Native ERP for OpenClaw

A complete ERP system built as an [OpenClaw](https://openclaw.org) skill. Full double-entry accounting, invoicing, inventory, purchasing, tax, billing, HR, payroll, and financial reporting — all in a single install. 413 actions across 14 domains.

## Features

- **Double-entry GL** — US GAAP chart of accounts, immutable journal entries, multi-company support
- **Sales** — customers, sales orders, delivery notes, sales invoices, credit notes, payment tracking
- **Buying** — suppliers, purchase orders, purchase invoices, goods received notes
- **Inventory** — items, warehouses, stock entries, serial/batch tracking, reorder levels
- **Billing** — usage-based billing, recurring invoices, subscription management
- **Tax** — tax templates, multi-rate support, tax returns
- **Payments** — payment entries, bank reconciliation, multi-currency
- **HR** — employees, departments, designations, leave management, attendance, expenses
- **Payroll** — salary structures, FICA, federal/state income tax, W-2 generation, garnishments
- **Advanced Accounting** — ASC 606 revenue recognition, ASC 842 lease accounting, intercompany transactions, consolidation
- **Reports** — trial balance, P&L, balance sheet, cash flow, AR/AP aging, inventory valuation
- **Module system** — 43 additional modules (44 total including core) available via `install-module` from GitHub

## Quick Start

### Install via OpenClaw

```
clawhub install erpclaw
```

This installs the core ERP (413 actions) and initializes the database.

### First Steps

Once installed, just talk to your AI assistant naturally:

```
"I'm opening a retail store called Sunrise Goods in Portland, Oregon. Set me up."
```

The bot will:
1. Create your company with US GAAP chart of accounts (94 accounts)
2. Set up fiscal year, tax rates, and cost center
3. Suggest relevant modules for your industry

### Adding Modules

ERPClaw has 43 additional modules for specific industries and features:

```
"I need manufacturing capabilities"
→ Installs erpclaw-ops (Manufacturing, Projects, Assets, Quality, Support)

"I need CRM"
→ Installs erpclaw-growth (CRM, Analytics, AI Engine)

"Set me up for healthcare"
→ Installs HealthClaw (140+ actions for clinical practice management)
```

Available modules:
- **Addon modules** (16): CRM, Manufacturing, Projects, Assets, Quality, Fleet, POS, Logistics, and more
- **Healthcare** (5): Core clinical + Dental, Veterinary, Mental Health, Home Health
- **Education** (8): Core SIS + Financial Aid, K-12, Scheduling, LMS, State Reporting, Higher Ed, SPED
- **Property** (2): Residential + Commercial property management
- **Industry verticals** (8): Retail, Construction, Agriculture, Automotive, Food, Hospitality, Legal, Nonprofit
- **Regional** (4): Canada, UK, India, EU (tax rules, COA templates, compliance)

## Architecture

```
OpenClaw Bot → erpclaw/scripts/db_query.py --action {action} --args
                         │
                         ├── erpclaw-setup     → Company, COA, fiscal year, database init
                         ├── erpclaw-gl        → Chart of accounts, journal entries
                         ├── erpclaw-selling   → Customers, sales orders, invoices
                         ├── erpclaw-buying    → Suppliers, purchase orders
                         ├── erpclaw-inventory → Items, warehouses, stock
                         ├── erpclaw-billing   → Recurring invoices, subscriptions
                         ├── erpclaw-tax       → Tax templates, calculations
                         ├── erpclaw-payments  → Payment entries, reconciliation
                         ├── erpclaw-journals  → Manual journal entries
                         ├── erpclaw-reports   → Financial statements
                         ├── erpclaw-hr        → Employees, leave, attendance
                         ├── erpclaw-payroll   → Salary, tax withholding, W-2
                         └── erpclaw-accounting-adv → ASC 606/842, intercompany
                         │
                         ▼
              SQLite (local database)
              WAL mode, FK enforcement, parameterized queries
```

### Data Integrity

- All financial amounts stored as TEXT (Python `Decimal`) — never float
- IDs are UUID4 (TEXT)
- GL entries are immutable — cancellation creates reverse entries
- All cross-table writes in single SQLite transactions
- 12-step GL validation on every posting

## Database

Single SQLite database at `~/.openclaw/erpclaw/data.sqlite`:

- **688 tables** across all modules (188 core)
- WAL mode for concurrent reads
- Foreign key enforcement ON
- `PRAGMA busy_timeout = 5000`
- Shared library at `~/.openclaw/erpclaw/lib/erpclaw_lib/`

## Module Registry

The module registry (`scripts/module_registry.json`) tracks all 44 modules across 14 GitHub repositories. Use `install-module` to add any module:

```
"Install the manufacturing module"
"Add retail capabilities"
"I need dental practice management"
```

Modules install from `github.com/avansaber/*` repos via sparse checkout — only the requested module is downloaded, not the entire repo.

## Web Dashboard

Two web dashboard options are available:

### ERPClaw Web (Recommended)

[ERPClaw Web](https://github.com/avansaber/erpclaw-web) is a purpose-built dashboard for ERPClaw with live data tables, action execution, AI chat, and real-time WebSocket updates.

```bash
git clone https://github.com/avansaber/erpclaw-web.git
cd erpclaw-web && npm install && pip install -r api/requirements.txt
```

See [erpclaw-web README](https://github.com/avansaber/erpclaw-web#readme) for setup and deployment.

### WebClaw (Universal)

[WebClaw](https://github.com/avansaber/webclaw) is a universal OpenClaw dashboard that works with any skill:

```
clawhub install webclaw
```

WebClaw reads ERPClaw's SKILL.md and automatically generates forms, data tables, charts, and dashboards — zero per-skill configuration needed.

## ERPClaw OS -- Self-Extending ERP

ERPClaw OS is a self-extending ERP platform where AI agents generate, test, and deploy new industry modules autonomously.

### The Constitution

18 machine-readable financial laws govern every generated module. These laws cover naming conventions, data types, GL immutability, transaction atomicity, and audit trail requirements. A module that violates any article is automatically rejected -- no human review needed for mechanical compliance.

### 80/15/5 Theory

ERP module development breaks down as:
- **80% mechanical** -- schema creation, CRUD actions, naming conventions, audit logging
- **15% pattern-matching** -- GL posting patterns, cross-skill integration, report templates
- **5% human judgment** -- business logic edge cases, domain expertise, UX decisions

ERPClaw OS automates the 80% and assists with the 15%, leaving humans to focus on the 5% that matters.

### Current Status

- **Phase 1 (Smart Templates)** -- complete. Industry-specific templates generate full module scaffolding from a single configuration.
- **Phase 2 (Bounded Autonomy)** -- complete. AI agents generate, validate, and test modules within constitutional bounds.
- **Phase 3 (Adult)** -- complete. Semantic correctness engine, self-improvement log, DGM variant engine, heartbeat analysis, gap detection. 13 new actions, 5 new tables.
- **7,627+ tests passing** across L0 constitutional, L1 unit, L2 contract, and L3 smoke layers.
- **3 proof-of-concept modules generated**: groomingclaw, tattooclaw, storageclaw -- 144/144 tests passed, all constitutional articles satisfied.

### How It Works

1. Define an industry configuration (name, entities, workflows, GL accounts)
2. ERPClaw OS generates the full module: schema, actions, SKILL.md, tests
3. The Constitution validator checks all 18 articles
4. Regression gate runs the full test suite
5. Deploy audit verifies production readiness

Generated modules are indistinguishable from hand-written ones -- same architecture, same conventions, same test coverage.

## Links

- **Website**: [erpclaw.ai](https://www.erpclaw.ai)
- **ERPClaw Web**: [erpclaw-web](https://github.com/avansaber/erpclaw-web) — purpose-built web dashboard
- **WebClaw**: [webclaw](https://github.com/avansaber/webclaw) — universal OpenClaw dashboard
- **OpenClaw**: [openclaw.org](https://openclaw.org)
- **All modules**: [github.com/avansaber](https://github.com/avansaber)

## License

MIT License — Copyright (c) 2026 AvanSaber

See [LICENSE.txt](LICENSE.txt) for details.
