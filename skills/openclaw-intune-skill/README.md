# 🔧 OpenClaw Intune Skill – Complete Microsoft Intune Management

> **Author:** Mattia Cirillo
> **Website:** [kaffeeundcode.com](https://kaffeeundcode.com)
> **License:** MIT
> **Platform:** [OpenClaw](https://github.com/openclaw/openclaw)

---

## 🌐 About This Project

This skill was built by **Mattia Cirillo**, an IT administrator and automation enthusiast from Germany. It is part of the **[Kaffee & Code](https://kaffeeundcode.com)** project – a platform dedicated to sharing real-world PowerShell scripts, n8n automation workflows, and Microsoft Intune knowledge with the IT community.

### What is this Skill?

The **OpenClaw Intune Skill** is a comprehensive AI skill file that teaches any [OpenClaw](https://github.com/openclaw/openclaw)-compatible AI agent how to **fully manage Microsoft Intune** through the Microsoft Graph API. Instead of manually navigating the Intune admin portal or writing custom scripts for every task, you can simply talk to your AI agent in natural language – and it handles the rest.

### What does it actually do?

Once installed, your AI agent gains the ability to:

- **Query your entire device fleet** – list all managed devices, search by name or user, check compliance status, and generate reports
- **Execute remote actions** – sync, reboot, lock, wipe, retire, rename, or locate any managed device with built-in safety confirmations
- **Manage compliance & configuration policies** – list, create, modify, or delete compliance policies and configuration profiles (including the modern Settings Catalog)
- **Handle app deployment** – view all deployed apps, check assignments, inspect detected apps across your fleet, and assign apps to groups
- **Control endpoint security** – manage security baselines, BitLocker/FileVault encryption, Windows Firewall, Microsoft Defender Antivirus, and Attack Surface Reduction (ASR) rules
- **Automate Windows Autopilot** – list Autopilot devices, manage deployment profiles, assign users, and clean up old device entries
- **Deploy PowerShell scripts** – upload, manage, and monitor the execution of PowerShell scripts and Proactive Remediations (Health Scripts) across your fleet
- **Manage users & groups** – search users, list group memberships, add/remove users from groups, and view all devices per user
- **Generate reports & dashboards** – compliance summaries, OS distribution, stale device reports, non-compliance lists, and export jobs
- **Configure Conditional Access** – list, create, and modify Conditional Access policies, named locations, and authentication strengths
- **Manage network profiles** – WLAN (Wi-Fi), VPN, and certificate profiles (SCEP, PKCS, Trusted Root)
- **Control Windows Updates** – manage update rings, feature updates, quality updates, driver updates, and pause/resume deployments
- **Administer Apple devices** – DEP/ADE enrollment, APNS certificate monitoring, VPP token management, and Activation Lock bypass
- **Manage Android Enterprise** – Managed Google Play, enrollment profiles, binding status, and app protection policies
- **Audit everything** – query Intune audit logs, directory audit events, and sign-in logs to track who changed what and when
- **Search the Settings Catalog** – find out if Intune supports a specific setting and explore GPO migration reports
- **And much more** – Terms & Conditions, notification templates, enrollment restrictions, ESP, Windows Hello for Business, assignment filters, scope tags, and RBAC roles

### Who is this for?

This skill is perfect for:

- **IT administrators** who manage Intune environments and want to speed up their daily workflows with AI
- **MSPs (Managed Service Providers)** who manage multiple tenants and need a fast, conversational interface to Intune
- **DevOps / automation engineers** who want to integrate Intune management into their AI-powered workflows
- **Anyone learning Intune** who wants an intelligent assistant that knows every Graph API endpoint

### Why use this instead of the Intune portal?

| Task | Intune Portal | With this Skill |
|---|---|---|
| Check compliance for 1 device | 5+ clicks, navigate menus | *"Ist MAX-LAPTOP compliant?"* → instant answer |
| Sync 10 devices | Click each one individually | *"Sync alle Geräte von Team Marketing"* → done |
| Find stale devices | Export report, filter in Excel | *"Welche Geräte haben sich seit 30 Tagen nicht gemeldet?"* → table |
| Create a compliance policy | Navigate wizard, 10+ steps | *"Erstell eine Compliance Policy für Windows mit BitLocker-Pflicht"* → draft + confirm |
| Check who changed a policy | Dig through audit logs | *"Wer hat letzte Woche Policies geändert?"* → formatted list |

### Built-in Safety

This skill was designed with **enterprise safety** in mind. Every destructive operation (wipe, retire, delete) requires **explicit double confirmation** from the user before execution. Read-only operations (listing devices, checking compliance) execute instantly without prompts. The agent never dumps raw JSON – it always formats output as readable Markdown.

> 💡 **More scripts, tutorials, and automation workflows:**
> Visit **[kaffeeundcode.com](https://kaffeeundcode.com)** for 150+ PowerShell scripts, n8n workflows, weekly Intune updates, and more.

---

## 🚀 What Can It Do? (22 Categories, 110+ Endpoints)

| # | Category | Capabilities |
|---|---|---|
| 1 | 📱 **Device Management** | List, search, sync, reboot, lock, wipe, retire, rename, locate devices |
| 2 | 📋 **Compliance Policies** | List/create/delete compliance policies, check device status |
| 3 | ⚙️ **Configuration Profiles** | Config profiles, Settings Catalog, assignments |
| 4 | 📦 **App Management** | List apps, assignments, detected apps, app configs |
| 5 | 🔒 **Endpoint Security** | Baselines, BitLocker, Firewall, Defender, ASR rules |
| 6 | 🚀 **Windows Autopilot** | Devices, profiles, assign users, delete |
| 7 | 📜 **PowerShell Scripts** | Upload, manage, execution status, proactive remediations |
| 8 | 👥 **Users & Groups** | Search users, manage group memberships, list devices per user |
| 9 | 📊 **Reporting** | Compliance summary, OS distribution, stale devices, exports |
| 10 | 🏷️ **Device Categories** | Categories, enrollment restrictions |
| 11 | 🔄 **RBAC** | Roles and role assignments |
| 12 | 🛡️ **Conditional Access** | Policies, named locations, authentication strengths |
| 13 | 📶 **WLAN, VPN & Certificates** | Wi-Fi profiles, VPN, SCEP, PKCS, trusted root certs |
| 14 | 🔄 **Windows Updates** | Update rings, feature/quality/driver updates, pause/resume |
| 15 | 🍎 **Apple Management** | DEP/ADE, APNS certificate, VPP tokens, activation lock bypass |
| 16 | 🤖 **Android Enterprise** | Managed Store, enrollment profiles, binding status |
| 17 | 📝 **Audit Logs** | Intune audit events, directory audits, sign-in logs |
| 18 | 🏗️ **Settings Catalog & GPO** | Search settings, GPO migration reports, definition files |
| 19 | 📄 **Terms & Notifications** | Terms & conditions, notification templates, test messages |
| 20 | 🔐 **App Protection (MAM)** | iOS/Android/Windows protection policies, per-user status |
| 21 | 📱 **Enrollment Config** | Platform restrictions, ESP, Windows Hello for Business |
| 22 | 🧮 **Filters & Scope Tags** | Assignment filters, scope tags, filter preview |

## 📦 Installation

```bash
# Copy into your OpenClaw workspace
mkdir -p ~/.openclaw/workspace/skills/intune-graph
cp SKILL.md ~/.openclaw/workspace/skills/intune-graph/
```

## 🔑 Setup

1. Create an **App Registration** in Microsoft Entra ID (Azure AD)
2. Grant the required Microsoft Graph API permissions (see SKILL.md)
3. Set environment variables:
```bash
export INTUNE_TENANT_ID="your-tenant-id"
export INTUNE_CLIENT_ID="your-client-id"
export INTUNE_CLIENT_SECRET="your-client-secret"
```

## 💬 Example Usage

> **You:** "Zeig mir alle Geräte die nicht compliant sind"
> **Agent:** "5 Geräte nicht compliant. 3 Windows (fehlende Updates), 2 iOS (kein Passcode). Soll ich die syncen?"

> **You:** "Sync den Laptop von Max Müller"
> **Agent:** "Done ✅ Sync-Befehl an MAX-LAPTOP gesendet."

> **You:** "Wie viele Geräte haben wir insgesamt?"
> **Agent:** "127 Geräte: 89 Windows, 22 iOS, 12 Android, 4 macOS."

## 🛡️ Safety

- Read operations execute without confirmation
- Sync/Reboot requires simple confirmation
- **Wipe/Retire/Delete** always requires explicit double confirmation
- The agent never dumps raw JSON – always formatted Markdown

## 🔗 Links

- 🌐 [Kaffee & Code](https://kaffeeundcode.com) – Blog, Skripte & Automatisierung
- 🦞 [OpenClaw](https://github.com/openclaw/openclaw)
- 📖 [Microsoft Graph API Docs](https://learn.microsoft.com/en-us/graph/api/resources/intune-graph-overview)

---
Made with ☕ by [Mattia Cirillo](https://kaffeeundcode.com)
