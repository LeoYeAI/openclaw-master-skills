---
name: honeybook
description: This skill should be used when the user asks about HoneyBook client-portal data. Triggers on phrases like "check HoneyBook", "sign contract", "pay invoice", "HoneyBook vendors", "unsigned contracts", "open invoices", or any request involving wedding-vendor contracts, invoices, brochures, proposals, or payments via HoneyBook.
---

# honeybook-mcp

MCP server for HoneyBook's client portal — 8 tools for viewing contracts and invoices across multiple wedding vendors, with magic-link session capture and deep-link fallback for signing and paying.

## Tools

- `use_magic_link` — Capture a session from a vendor magic-link URL
- `list_active_sessions` — Show currently active portal sessions
- `list_workspace_files` — All files one vendor has shared (filter by type)
- `get_workspace_file` — Full detail for one file
- `get_workspace` — Workspace detail + status flags
- `list_payment_methods` — Saved payment methods
- `sign_contract` — Deep link to sign in portal (requires `confirm:true`)
- `pay_invoice` — Deep link to pay in portal (requires `confirm:true`)

## Workflows

- **First time** → user pastes magic-link URL from vendor email → `use_magic_link` → session captured
- **"What contracts haven't I signed?"** → `list_workspace_files` with `file_type=agreement`, filter by `is_file_accepted=false`
- **"Summarize my HB status with Silk Veil"** → `get_workspace` (status flags) + `list_workspace_files`
- **"Send me a link to sign the photographer's contract"** → `list_workspace_files` → `sign_contract` with `confirm:true`
- **"Which invoices are overdue?"** → `list_workspace_files` with `file_type=invoice`, sort by due date

## Notes

- Each vendor = separate session keyed by portal origin (e.g. `https://acme.hbportal.co`)
- Sessions cached in `~/.honeybook-mcp/sessions.json` (mode 0600)
- Write tools (`sign_contract`, `pay_invoice`) return deep links in v2
- Session expires → re-run `use_magic_link` with a fresh URL from the vendor's email
