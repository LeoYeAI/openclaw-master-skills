# OpenClaw Odoo ERP Connector

Full-featured Odoo 19 ERP integration for OpenClaw. Control your entire business via natural language chat commands.

[![ClawHub](https://img.shields.io/badge/ClawHub-odoo--erp--connector-blue)](https://clawhub.ai/skills/odoo-erp-connector)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## Features

- **80+ operations** across 13 Odoo modules
- **Smart actions** with fuzzy matching and auto-creation
- **Zero dependencies** — pure Python with built-in XML-RPC
- **100% test coverage** — 73 comprehensive tests
- **Production ready** — Thread-safe, retry logic, error handling

### Supported Modules

- 📊 Sales & CRM (quotations, orders, leads, opportunities)
- 🛒 Purchasing (POs, vendors, receipts)
- 📦 Inventory (products, stock levels, alerts)
- 💰 Invoicing (customer invoices, payments)
- 📋 Projects & Tasks (management, timesheets)
- 👥 HR (employees, departments, expenses, leave)
- 🚗 Fleet (vehicles, odometer, maintenance)
- 🏭 Manufacturing (BOMs, production orders)
- 📅 Calendar (events, meetings)
- 🛍️ eCommerce (website orders, product publishing)

## Quick Install

### Via ClawHub (Recommended)

```bash
npx clawhub install odoo-erp-connector
```

### Manual Install

```bash
# Clone the repository
git clone https://github.com/nullnaveen/openclaw-odoo-skill.git
cd openclaw-odoo-skill

# Windows: Run installer
.\setup.ps1

# OR copy manually to OpenClaw skills directory
# Windows: %APPDATA%\npm\node_modules\openclaw\skills\odoo-erp-connector\
# Mac/Linux: ~/.local/share/openclaw/skills/odoo-erp-connector/
```

## Configuration

Create a file named `config.json` in the skill directory with your Odoo credentials:

```json
{
  "url": "http://your-odoo-server:8069",
  "db": "your_database_name",
  "username": "your_email@company.com",
  "api_key": "your_odoo_api_key"
}
```

**Note:** For local Odoo installations, use `http://localhost:8069` (or your port).
For Odoo.com/SaaS, use `https://yourcompany.odoo.com`.

### Get Your API Key

1. Log in to Odoo
2. Go to **Settings** → **Users & Companies** → **Users**
3. Open your user record
4. Scroll to **Access Tokens**
5. Click **Generate**
6. Copy the key into `config.json`

## Usage Examples

### Sales
```
"Create a quotation for Acme Corp with 10 Widgets at $50 each"
"Confirm sales order SO00042"
"Show me all draft quotations"
```

### CRM
```
"Create a lead for Rocky, email rocky@example.com, potential $50k deal"
"Move lead #47 to Qualified stage"
"Show me the sales pipeline"
```

### Inventory
```
"What's the stock level for Widget X?"
"Show products with stock below 20 units"
"Create a new product: TestWidget, $25 price, min stock 10"
```

### Projects
```
"Create a project called Website Redesign"
"Create task 'Fix login button' in Website Redesign"
"Log 3 hours on task #42"
```

### HR
```
"Create employee John Smith, job title Developer"
"Show me all employees in Engineering"
"Submit expense report for $45.99"
```

[See SKILL.md for complete command reference with 30+ examples]

## Smart Actions

The connector automatically handles missing dependencies with fuzzy matching:

**Example:** "Create quotation for Rocky with 100 Snake Skins at $10 each"

1. Searches for customer "Rocky" (case-insensitive)
2. If not found → creates new customer "Rocky"
3. Searches for product "Snake Skin"
4. If not found → creates product with $10 price
5. Creates quotation linking both
6. Reports: "✅ Created quotation S00059 for Rocky with 100 × Snake Skin at $1,150"

## Technical Details

### Architecture

- **OdooClient** — Low-level XML-RPC wrapper with authentication
- **Model Ops** — 13 business module classes (Sales, CRM, Purchase, HR, etc.)
- **SmartActionHandler** — High-level natural language interface with find-or-create workflows

### Testing

```bash
# Run full test suite
python run_full_test.py

# Test single module
pytest tests/test_partners.py -v
```

73 tests covering all 13 modules with 100% feature coverage.

### Requirements

- Python 3.10+
- Odoo 19.0 (may work with 17-18 with field adjustments)
- OpenClaw 2026.2.0+
- No external Python dependencies

## Project Structure

```
openclaw-odoo-skill/
├── SKILL.md                  # OpenClaw skill definition
├── README.md                 # This file
├── package.json              # Skill metadata
├── config.json.template      # Configuration template
├── setup.ps1                 # Windows installer
├── requirements.txt          # Python dependencies (none)
├── odoo_skill/               # Python connector package
│   ├── client.py            # XML-RPC client
│   ├── config.py            # Configuration loader
│   ├── errors.py            # Custom exceptions
│   ├── smart_actions.py     # Smart action workflows
│   ├── models/              # 13 module operation classes
│   │   ├── partner.py
│   │   ├── sale_order.py
│   │   ├── crm.py
│   │   ├── purchase.py
│   │   ├── invoice.py
│   │   ├── inventory.py
│   │   ├── project.py
│   │   ├── hr.py
│   │   ├── fleet.py
│   │   ├── manufacturing.py
│   │   ├── calendar_ops.py
│   │   └── ecommerce.py
│   ├── sync/                # Real-time sync modules
│   │   ├── poller.py       # Change detection poller
│   │   └── webhook.py      # Webhook server
│   └── utils/               # Helper utilities
└── tests/                   # Test suite (73 tests)
```

## Documentation

- **SKILL.md** — Complete skill definition with 30+ command examples
- **README.md** — Installation guide and quick start (this file)
- **TEST_RESULTS.md** — Test coverage report

## Security Note

The security scan on ClawHub correctly identifies this skill as having powerful capabilities:

- ✅ Full CRUD operations across Odoo modules (required for ERP management)
- ✅ Webhook server for real-time updates (optional feature)
- ✅ Background polling for change detection (optional feature)
- ✅ XML-RPC network access (required for Odoo communication)

**These are legitimate features for an ERP connector.** The skill contains no malicious code — review the source if you have concerns.

## Troubleshooting

### Connection Failed
- Verify Odoo URL and server is running
- Check database name matches exactly
- Regenerate API key if authentication fails

### Module Not Found
- Ensure Python 3.10+ is installed
- No external dependencies needed (uses built-in `xmlrpc.client`)

### Permission Denied
- Check Odoo user has access to required modules
- Some operations require specific permissions (Admin, Sales Manager, etc.)

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Author

**NullNaveen**

- ClawHub: [@NullNaveen](https://clawhub.ai/users/NullNaveen)
- GitHub: [@nullnaveen](https://github.com/nullnaveen)

## Support

- **Issues:** [GitHub Issues](https://github.com/nullnaveen/openclaw-odoo-skill/issues)
- **ClawHub:** [odoo-erp-connector](https://clawhub.ai/skills/odoo-erp-connector)
- **Discord:** [OpenClaw Community](https://discord.com/invite/clawd)

---

**Version:** 1.0.1  
**Last Updated:** 2026-02-09  
**Status:** Production Ready ✅
