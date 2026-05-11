# Gandi Skill Scripts Reference

Complete documentation of all scripts, their behaviors, network operations, and security implications.

## Quick Reference

| Script | Type | Network | Description |
|--------|------|---------|-------------|
| test-auth.js | ✅ Read-only | Yes | Verify API authentication |
| list-domains.js | ✅ Read-only | Yes | List all domains in account |
| list-dns.js | ✅ Read-only | Yes | Show DNS records for domain |
| check-domain.js | ✅ Read-only | Yes | Check domain availability + pricing |
| suggest-domains.js | ✅ Read-only | Yes | Smart domain suggestions |
| check-ssl.js | ✅ Read-only | Yes | Check SSL certificate status |
| list-snapshots.js | ✅ Read-only | Yes | List DNS zone snapshots |
| list-email-forwards.js | ✅ Read-only | Yes | List email forwards |
| view-contact.js | ✅ Read-only | No | View saved contact info (local file) |
| add-dns-record.js | ⚠️ Destructive | Yes | Add or update DNS record |
| delete-dns-record.js | ⚠️ Destructive | Yes | Delete DNS record |
| update-dns-bulk.js | ⚠️ Destructive | Yes | Replace ALL DNS records |
| create-snapshot.js | ✅ Safe | Yes | Create DNS zone backup |
| restore-snapshot.js | ⚠️ Destructive | Yes | Restore DNS from snapshot |
| add-email-forward.js | ⚠️ Destructive | Yes | Create email forward |
| update-email-forward.js | ⚠️ Destructive | Yes | Update email forward destinations |
| delete-email-forward.js | ⚠️ Destructive | Yes | Delete email forward |
| setup-contact.js | ✅ Safe | No | Save contact info (local file) |
| delete-contact.js | ✅ Safe | No | Delete contact info (local file) |

---

## Script Details

### Read-Only Scripts (Safe)

#### test-auth.js
- **Purpose:** Verify API token authentication
- **Network calls:** GET /v5/organizations (Gandi API)
- **Side effects:** None
- **Usage:** `node test-auth.js`
- **What it does:**
  1. Reads token from ~/.config/gandi/api_token
  2. Calls Gandi API to list organizations
  3. Displays organization names and types
  4. No modifications made

#### list-domains.js
- **Purpose:** List all domains in your account
- **Network calls:** GET /v5/domain/domains (Gandi API)
- **Side effects:** None
- **Usage:** `node list-domains.js`
- **What it does:**
  1. Fetches all domains for authenticated user
  2. Displays domain names, expiration dates, auto-renewal status
  3. Shows active services (LiveDNS, Email, etc.)
  4. No modifications made

#### list-dns.js
- **Purpose:** Show DNS records for a domain
- **Network calls:** GET /v5/livedns/domains/{domain}/records (Gandi API)
- **Side effects:** None
- **Usage:** `node list-dns.js example.com`
- **What it does:**
  1. Fetches all DNS records for specified domain
  2. Groups by record type (A, CNAME, MX, etc.)
  3. Displays names, values, TTLs
  4. Shows nameservers
  5. No modifications made

#### check-domain.js
- **Purpose:** Check if domain is available for registration
- **Network calls:** GET /v5/domain/check (Gandi API)
- **Side effects:** None
- **Usage:** `node check-domain.js example.com`
- **What it does:**
  1. Queries Gandi for domain availability
  2. Shows pricing (registration, renewal, transfer)
  3. Lists supported features (DNSSEC, LiveDNS)
  4. Displays TLD information
  5. No modifications or registrations made

#### suggest-domains.js
- **Purpose:** Find available domain alternatives
- **Network calls:** Multiple GET /v5/domain/check calls (Gandi API)
- **Side effects:** None
- **Usage:** `node suggest-domains.js example [--tlds com,net]`
- **What it does:**
  1. Checks configured TLDs for availability
  2. Generates name variations (hyphenated, abbreviated, prefixes, suffixes)
  3. Queries availability for each
  4. Displays available options with pricing
  5. No registrations or modifications made

#### check-ssl.js
- **Purpose:** Check SSL certificate status for all domains
- **Network calls:** GET /v5/domain/domains (Gandi API)
- **Side effects:** None
- **Usage:** `node check-ssl.js`
- **What it does:**
  1. Fetches all domains
  2. Displays SSL/TLS certificate status
  3. No modifications made

#### list-snapshots.js
- **Purpose:** List DNS zone snapshots for a domain
- **Network calls:** GET /v5/livedns/domains/{domain}/snapshots (Gandi API)
- **Side effects:** None
- **Usage:** `node list-snapshots.js example.com`
- **What it does:**
  1. Fetches all snapshots for domain
  2. Displays snapshot IDs, names, creation dates
  3. No modifications made

#### list-email-forwards.js
- **Purpose:** List email forwards for a domain
- **Network calls:** GET /v5/email/forwards/{domain} (Gandi API)
- **Side effects:** None
- **Usage:** `node list-email-forwards.js example.com`
- **What it does:**
  1. Fetches all email forwards
  2. Displays mailbox → destination mappings
  3. Shows catch-all forwards
  4. No modifications made

#### view-contact.js
- **Purpose:** View locally saved contact information
- **Network calls:** None (local file only)
- **Side effects:** None
- **Usage:** `node view-contact.js`
- **What it does:**
  1. Reads ~/.config/gandi/contact.json
  2. Displays contact information
  3. No network calls or modifications

---

### Destructive Scripts (Caution Required)

#### add-dns-record.js
- **Purpose:** Add or update a DNS record
- **Network calls:** POST /v5/livedns/domains/{domain}/records/{name}/{type} (Gandi API)
- **Side effects:** ⚠️ **MODIFIES DNS** - can break websites/email if misconfigured
- **Usage:** `node add-dns-record.js example.com @ A 192.168.1.1 [ttl]`
- **What it does:**
  1. Creates or updates specified DNS record
  2. If record exists, replaces it
  3. Changes propagate immediately to nameservers
  4. Can break services if incorrect
- **Undo:** Delete the record or change it back manually

#### delete-dns-record.js
- **Purpose:** Delete a DNS record
- **Network calls:** DELETE /v5/livedns/domains/{domain}/records/{name}/{type} (Gandi API)
- **Side effects:** ⚠️ **DELETES DNS RECORD** - can break websites/email
- **Usage:** `node delete-dns-record.js example.com old A [--force]`
- **What it does:**
  1. Permanently deletes specified DNS record
  2. Prompts for confirmation unless --force
  3. Cannot be undone except via snapshot restore
- **Undo:** Manually re-create the record or restore from snapshot

#### update-dns-bulk.js
- **Purpose:** Replace ALL DNS records for a domain
- **Network calls:** PUT /v5/livedns/domains/{domain}/records (Gandi API)
- **Side effects:** ⚠️ **REPLACES ALL DNS** - extremely destructive
- **Usage:** `node update-dns-bulk.js example.com records.json [--no-snapshot] [--force]`
- **What it does:**
  1. **Automatically creates snapshot** (unless --no-snapshot)
  2. Deletes ALL existing DNS records
  3. Creates new records from JSON file
  4. Prompts for confirmation unless --force
  5. Can completely break domain if JSON is incorrect
- **Undo:** Restore from snapshot (restore-snapshot.js)

#### restore-snapshot.js
- **Purpose:** Restore DNS from a snapshot
- **Network calls:** POST /v5/livedns/domains/{domain}/snapshots/{id}/restore (Gandi API)
- **Side effects:** ⚠️ **REPLACES CURRENT DNS** with snapshot state
- **Usage:** `node restore-snapshot.js example.com snapshot-id [--force]`
- **What it does:**
  1. Deletes ALL current DNS records
  2. Restores records from specified snapshot
  3. Prompts for confirmation unless --force
  4. Overwrites any changes made since snapshot
- **Undo:** Create snapshot before restoring, then restore that

#### add-email-forward.js
- **Purpose:** Create email forward
- **Network calls:** POST /v5/email/forwards/{domain} (Gandi API)
- **Side effects:** ⚠️ **CREATES EMAIL FORWARD** - can intercept emails
- **Usage:** `node add-email-forward.js example.com mailbox dest@example.com`
- **What it does:**
  1. Creates email forward from mailbox to destination(s)
  2. Supports multiple destinations
  3. Supports catch-all (@)
  4. Emails start forwarding immediately
- **Undo:** Delete the forward (delete-email-forward.js)

#### update-email-forward.js
- **Purpose:** Update email forward destinations
- **Network calls:** PUT /v5/email/forwards/{domain}/{mailbox} (Gandi API)
- **Side effects:** ⚠️ **CHANGES EMAIL ROUTING** - can break email delivery
- **Usage:** `node update-email-forward.js example.com mailbox new@example.com`
- **What it does:**
  1. Replaces ALL destinations for mailbox
  2. Old destinations no longer receive emails
  3. Changes take effect immediately
- **Undo:** Update again with original destinations

#### delete-email-forward.js
- **Purpose:** Delete email forward
- **Network calls:** DELETE /v5/email/forwards/{domain}/{mailbox} (Gandi API)
- **Side effects:** ⚠️ **STOPS EMAIL FORWARDING** - emails will bounce
- **Usage:** `node delete-email-forward.js example.com mailbox [--force]`
- **What it does:**
  1. Permanently deletes email forward
  2. Emails to that address will bounce
  3. Prompts for confirmation unless --force
- **Undo:** Recreate forward manually (add-email-forward.js)

---

### Safe Scripts (Local Operations)

#### create-snapshot.js
- **Purpose:** Create DNS zone backup
- **Network calls:** POST /v5/livedns/domains/{domain}/snapshots (Gandi API)
- **Side effects:** ✅ **SAFE** - only creates backup, no modifications
- **Usage:** `node create-snapshot.js example.com "Backup before migration"`
- **What it does:**
  1. Creates snapshot of current DNS state
  2. Snapshots stored on Gandi servers
  3. Can be restored later
  4. Does not modify current DNS

#### setup-contact.js
- **Purpose:** Save contact information for domain registration
- **Network calls:** None (local file only)
- **Side effects:** ✅ **SAFE** - only writes local file
- **Usage:** `node setup-contact.js`
- **What it does:**
  1. Prompts for contact details (name, email, address, etc.)
  2. Saves to ~/.config/gandi/contact.json
  3. Sets file permissions to 600
  4. No network calls or Gandi API modifications

#### delete-contact.js
- **Purpose:** Delete locally saved contact information
- **Network calls:** None (local file only)
- **Side effects:** ✅ **SAFE** - only deletes local file
- **Usage:** `node delete-contact.js [--force]`
- **What it does:**
  1. Deletes ~/.config/gandi/contact.json
  2. Prompts for confirmation unless --force
  3. No network calls or Gandi API modifications

---

## Security Best Practices

### Before Running ANY Script:

1. **Review the code:** All scripts are JavaScript - open and read them
2. **Understand the operation:** Use this document to see what will happen
3. **Use read-only tokens:** For list/check/view operations
4. **Create snapshots:** Before ANY DNS modifications
5. **Test on non-production:** Use test domains first
6. **Verify parameters:** Double-check domain names and values
7. **Have backups:** Know how to undo changes

### Audit Workflow:

```bash
# 1. Review what the script does
cat scripts/add-dns-record.js

# 2. Check this documentation
cat SCRIPTS.md | grep -A 20 "add-dns-record.js"

# 3. Create backup if destructive
node scripts/create-snapshot.js example.com "Before adding A record"

# 4. Run with appropriate token (read or write)
node scripts/add-dns-record.js example.com @ A 192.168.1.1

# 5. Verify the change
node scripts/list-dns.js example.com

# 6. Restore if needed
node scripts/restore-snapshot.js example.com snapshot-id
```

### Token Scope Recommendations:

**For these scripts, use READ-ONLY tokens:**
- All test-*, list-*, check-*, view-* scripts
- Never need write permissions

**For these scripts, use WRITE tokens:**
- add-*, delete-*, update-*, restore-* scripts
- Require LiveDNS:write or Email:write

**Keep separate tokens:**
- Read-only token for daily use
- Write token only when making changes
- Rotate both regularly

---

## Network Operations Summary

**All network calls go to:**
- `https://api.gandi.net/v5/*` (Gandi API)
- HTTPS only (encrypted)
- Authenticated with Personal Access Token

**No other external services:**
- No analytics
- No telemetry
- No third-party APIs

**API Rate Limits:**
- Gandi allows 1000 requests/minute
- Scripts implement 200ms delay between requests
- suggest-domains.js limits concurrent requests to 3

---

## File System Operations

**Reads from:**
- `~/.config/gandi/api_token` (API token)
- `~/.config/gandi/contact.json` (contact info, optional)
- `~/.config/gandi/api_url` (API URL override, optional)

**Writes to:**
- `~/.config/gandi/contact.json` (setup-contact.js only)

**Permissions:**
- api_token: 600 (owner read-only)
- contact.json: 600 (owner read-write)

**Never writes to:**
- System directories
- Other users' files
- Outside ~/.config/gandi/

---

## Troubleshooting

**"Error: ENOENT ~/.config/gandi/api_token"**
- Run setup (Step 2 in SKILL.md)
- Verify file exists and is readable

**"Error: 401 Unauthorized"**
- Token is invalid or expired
- Create new token at Gandi Admin

**"Error: 403 Forbidden"**
- Token doesn't have required scopes
- Add LiveDNS:write or Email:write

**"Error: MODULE_NOT_FOUND"**
- Run `npm install` in scripts/ directory
- See Step 3 in SKILL.md

**"Error: Domain not using LiveDNS"**
- Domain must have LiveDNS service attached
- Enable in Gandi Admin → Domain → LiveDNS

---

## Emergency Recovery

**Accidentally deleted DNS records:**
```bash
# List available snapshots
node scripts/list-snapshots.js example.com

# Restore from most recent
node scripts/restore-snapshot.js example.com <snapshot-id>
```

**Broke email forwarding:**
```bash
# List current forwards
node scripts/list-email-forwards.js example.com

# Delete broken forward
node scripts/delete-email-forward.js example.com mailbox --force

# Recreate correctly
node scripts/add-email-forward.js example.com mailbox correct@example.com
```

**Need to revert everything:**
1. Check git history for previous DNS state
2. Restore from snapshot (if available)
3. Contact Gandi support (they have backups)

---

**Last Updated:** February 10, 2026  
**Skill Version:** v0.3.0
