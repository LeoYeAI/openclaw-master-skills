# Legal Docs Pro — Setup Guide

Welcome to Legal Docs Pro! This guide walks you through setting everything up in about 5 minutes.

## What You'll Need

- **OpenClaw** installed and running on your machine
- **5 minutes** to answer some questions about your business
- That's it. No accounts to create, no API keys, no subscriptions.

## Step 1: Install the Skill

Copy the `legal-docs-pro` folder into your OpenClaw skills directory:

```bash
cp -r legal-docs-pro/ ~/.openclaw/workspace/.agents/skills/legal-docs-pro/
```

Restart OpenClaw or reload skills so the agent picks it up.

## Step 2: Run the Setup Script

Open your terminal and run:

```bash
cd ~/.openclaw/workspace/.agents/skills/legal-docs-pro/
chmod 700 scripts/setup.sh
bash scripts/setup.sh
```

The script creates your data directory and opens your business profile for editing.

## Step 3: Fill In Your Business Profile

The setup script opens `config/settings.json` in your default editor. Fill in your business details:

- **Business name** — Your legal entity name (e.g., "Bright Pixel LLC")
- **Business type** — LLC, S-Corp, Sole Proprietor, C-Corp, etc.
- **Address** — Your principal business address
- **State of formation** — Where your business is registered
- **EIN** — Your Employer Identification Number (leave blank if sole proprietor without one)
- **Owner name and title** — Who signs contracts (e.g., "Jordan Rivera, Managing Member")
- **Email and phone** — Business contact info
- **Default jurisdiction** — Usually your state (e.g., "State of Colorado")
- **Payment terms** — Your standard terms (e.g., "Net 30")
- **Late fee rate** — What you charge for late payments (e.g., "1.5% per month")

Don't worry about getting everything perfect now. You can update any field later by telling the agent "update my business profile" or editing `config/settings.json` directly.

## Step 4: Try It Out

Open a chat with your agent and try these:

**Generate a document:**
> "I need an NDA for a freelance designer who'll be working on our new product designs"

**Review a contract:**
> "Review this contract for me:" then paste the contract text

**Get a quick explanation:**
> "What does an indemnification clause mean?"

**Export a document:**
```bash
bash scripts/export-doc.sh --format pdf --output ~/Documents/nda-acme-corp.pdf
```

## Optional: PDF Export Setup

If you want to export documents as PDFs, you'll need `pandoc` installed:

```bash
# macOS
brew install pandoc

# Linux (Debian/Ubuntu)
sudo apt install pandoc
```

Markdown export works out of the box — no extra tools needed.

## Updating Your Profile Later

Two ways to update your business details:

1. **Tell the agent:** "Update my business name to Rivera Consulting Group"
2. **Edit directly:** Open `config/settings.json` in any text editor

## Need Help?

- Check the `examples/` folder for full conversation examples
- Read the README for feature overview
- Visit normieclaw.ai for support

## ⚠️ Important Reminder

Legal Docs Pro provides legal document templates and analysis for informational purposes. It is not a substitute for professional legal advice. For complex, high-value, or sensitive legal matters, consult a licensed attorney.

---

*Legal Docs Pro is part of the NormieClaw tool ecosystem. More info: normieclaw.ai*
