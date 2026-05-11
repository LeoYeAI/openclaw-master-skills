# Legal Docs Pro

**AI-powered legal document generation and contract review for freelancers, solopreneurs, and small businesses.**

Part of the [NormieClaw](https://normieclaw.ai) tool ecosystem. $9.99 standalone or included in The Full Stack ($49).

---

## What It Does

- **Generates legal documents** from a conversation — describe the deal, answer a few questions, get a complete document
- **Reviews contracts** with multi-pass analysis — identifies risky clauses, missing protections, and one-sided terms
- **Explains everything in plain English** — every clause gets a "what this actually means" translation
- **Remembers your business details** — name, address, EIN, standard terms auto-populate into every document
- **Zero per-document fees** — generate and review unlimited documents

## Supported Documents

| Generate | Review |
|----------|--------|
| NDAs (mutual/unilateral) | Any contract or agreement |
| Freelance/Contractor agreements | Commercial leases |
| Consulting agreements | Employment agreements |
| Privacy policies | Terms of service |
| Terms of service | Vendor/supplier contracts |
| Partnership agreements | Client contracts |
| Demand letters | NDAs |
| Cease and desist letters | Partnership agreements |

## Install

```bash
cp -r legal-docs-pro/ ~/.openclaw/workspace/.agents/skills/legal-docs-pro/
cd ~/.openclaw/workspace/.agents/skills/legal-docs-pro/
chmod 700 scripts/*.sh
bash scripts/setup.sh
```

Then reload OpenClaw skills.

## Quick Start

```
You: "I need an NDA for a meeting with Acme Corp"
Agent: reads your profile, asks 2-3 questions, generates the full NDA

You: "Review this contract" + paste text
Agent: identifies parties, flags risks, explains each clause, gives a summary

You: "Someone owes me $4,500 and won't pay"
Agent: asks for details, generates a professional demand letter
```

## Compatibility

- **OpenClaw:** v1.0+
- **OS:** macOS, Linux, Windows (WSL)
- **PDF export:** Requires `pandoc` (optional — markdown export works without it)
- **Dashboard:** Compatible with NormieClaw dashboard kit

## File Structure

```
legal-docs-pro/
├── SKILL.md              # Agent skill definition
├── SETUP-PROMPT.md       # Setup walkthrough
├── README.md             # This file
├── SECURITY.md           # Security posture
├── config/
│   └── settings.json     # Your business profile
├── scripts/
│   ├── setup.sh          # First-time setup
│   ├── export-doc.sh     # Export documents
│   └── contract-scan.sh  # Quick contract risk scan
├── examples/
│   ├── example-nda-generation.md
│   ├── example-contract-review.md
│   └── example-freelance-agreement.md
└── dashboard-kit/
    ├── manifest.json
    └── DASHBOARD-SPEC.md
```

## Disclaimer

This tool provides legal document templates and analysis for informational purposes. It is not a substitute for professional legal advice. Consult a licensed attorney for complex, high-value, or jurisdiction-specific matters.

---

Built by [NormieClaw](https://normieclaw.ai) · Replaces ~$600/yr in legal document subscriptions
