# Legal Docs Pro — Security

## Overview

Legal Docs Pro handles sensitive business information: business names, addresses, EINs, contract terms, and potentially confidential agreement details. This document describes the tool's security posture.

## What This Tool Does

- Reads and writes to local configuration files (`config/settings.json`)
- Generates legal documents via AI conversation
- Analyzes contract text provided by the user
- Exports documents to local files

## What This Tool Does NOT Do

- **No cloud sync** — This tool does not transmit your documents or business profile to any server, API, or cloud service on its own
- **No telemetry** — No usage data, analytics, or tracking is collected by Legal Docs Pro
- **No third-party integrations** — No data is shared with LegalZoom, Rocket Lawyer, or any external legal service
- **No account creation** — No user accounts, no login, no credentials stored

## Data Handling

Your business profile and generated documents are stored as local files on your machine. The tool operates within the OpenClaw agent's environment.

**Important:** The AI agent processing your documents operates according to the AI provider's terms and data handling policies. Legal Docs Pro itself does not control how the underlying AI model processes conversation data. Review your AI provider's privacy policy and data retention practices for details on how conversation content is handled.

## Sensitive Data Considerations

- **EIN/Tax ID:** Stored in `config/settings.json` in plain text. Protect this file with appropriate file system permissions. The setup script sets `chmod 700` on the config directory.
- **Contract Content:** When you paste a contract for review, that text is processed as part of the AI conversation. The same data handling considerations apply as any other AI interaction.
- **Generated Documents:** Stored locally. You are responsible for securing, backing up, and managing access to your generated documents.

## Recommendations

1. **File permissions:** Run `chmod 700 config/` to restrict access to your business profile
2. **Backup:** Keep copies of important generated documents outside the skill directory
3. **Sensitive contracts:** For highly confidential agreements (M&A, litigation-related), consider whether AI-assisted review is appropriate for your situation
4. **Regular review:** Periodically review `config/settings.json` to ensure it contains only information you intend to store
5. **Shared machines:** If multiple users share your machine, be aware that anyone with file system access can read your business profile

## No Guarantees

This tool is provided as-is. NormieClaw does not make guarantees about data privacy, security, or confidentiality beyond what is described in this document. The security of your data depends on your environment, your AI provider, and your own practices.

## Questions

For security concerns, contact support@normieclaw.ai.

---

*Last updated: March 2026*
