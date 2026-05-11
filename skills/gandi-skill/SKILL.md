---
name: gandi
description: "Comprehensive Gandi domain registrar integration for domain and DNS management. Register and manage domains, create/update/delete DNS records (A, AAAA, CNAME, MX, TXT, SRV, and more), configure email forwarding and aliases, check SSL certificate status, create DNS snapshots for safe rollback, bulk update zone files, and monitor domain expiration. Supports multi-domain management, zone file import/export, and automated DNS backups. Includes both read-only and destructive operations with safety controls."
disable-model-invocation: true
metadata: {"openclaw":{"version":"0.2.7","disable-model-invocation":true,"capabilities":["dns-modification","email-management","domain-registration","destructive-operations"],"credentials":{"type":"file","location":"~/.config/gandi/api_token","description":"Gandi Personal Access Token (PAT)","permissions":600},"requires":{"bins":["node","npm"],"env":["GANDI_API_TOKEN"]},"primaryEnv":"GANDI_API_TOKEN"}}
---

# Gandi Domain Registrar Skill

Comprehensive Gandi domain registrar integration for Moltbot.

**Status:** ✅ Phase 2 Complete - DNS modification & snapshots functional

## ⚠️ Security Warning

**This skill can perform DESTRUCTIVE operations on your Gandi account:**

- **DNS Modification:** Add, update, or delete DNS records (can break websites/email)
- **Email Management:** Create, modify, or delete email forwards (can intercept emails)
- **Domain Registration:** Register domains (creates financial transactions)
- **Bulk Operations:** Replace all DNS records at once (cannot be undone except via snapshots)

**Before running ANY script:**
1. Review the script code to understand what it does
2. Create DNS snapshots before bulk changes (`create-snapshot.js`)
3. Use read-only Personal Access Tokens where possible
4. Test on non-production domains first
5. Understand that some operations cannot be undone

**Destructive scripts** (⚠️ modify or delete data):
- `add-dns-record.js`, `delete-dns-record.js`, `update-dns-bulk.js`
- `add-email-forward.js`, `update-email-forward.js`, `delete-email-forward.js`
- `restore-snapshot.js` (replaces current DNS)

**Read-only scripts** (✅ safe, no modifications):
- `list-domains.js`, `list-dns.js`, `list-snapshots.js`
- `list-email-forwards.js`, `check-domain.js`, `check-ssl.js`

📖 **For complete script documentation:** See [SCRIPTS.md](SCRIPTS.md) for detailed information about:
- What each script does
- Network operations and API calls
- Security implications
- Undo/recovery procedures
- Audit workflow recommendations

## Current Capabilities

### Phase 1 (Complete)
- ✅ Personal Access Token authentication
- ✅ List domains in your account
- ✅ Get domain details (expiration, status, services)
- ✅ List DNS records for domains
- ✅ View domain and DNS information
- ✅ **Domain availability checking** ([#4](https://github.com/chrisagiddings/moltbot-gandi-skill/issues/4))
- ✅ **Smart domain suggestions with variations** ([#4](https://github.com/chrisagiddings/moltbot-gandi-skill/issues/4))
- ✅ SSL certificate status checker
- ✅ Error handling and validation

### Phase 2 (Complete)
- ✅ **Add/update DNS records** (A, AAAA, CNAME, MX, TXT, NS, SRV, CAA, PTR)
- ✅ **Delete DNS records**
- ✅ **Bulk DNS operations** (replace all records at once)
- ✅ **DNS zone snapshots** (create, list, restore)
- ✅ **Email forwarding** (create, list, update, delete forwards including catch-all)
- ✅ **Record validation** (automatic validation for each record type)
- ✅ **Safety features** (automatic snapshots before bulk changes, confirmation prompts)

## Coming Soon (Phase 3+)

- Domain registration
- Multi-organization support ([#1](https://github.com/chrisagiddings/moltbot-gandi-skill/issues/1))
- Gateway Console configuration ([#3](https://github.com/chrisagiddings/moltbot-gandi-skill/issues/3))
- Domain renewal management
- DNSSEC configuration
- Certificate management
- Email mailbox management (beyond forwarding)

## Setup

### Step 1: Create Personal Access Token

**⚠️ Security Recommendation:** Use the **minimum required scopes** for your use case.

1. Go to [Gandi Admin → Personal Access Tokens](https://admin.gandi.net/organizations/account/pat)
2. Click **"Create a token"**
3. Select your organization
4. Choose scopes:
   
   **Read-Only (Recommended for viewing only):**
   - ✅ Domain: read (required for listing domains)
   - ✅ LiveDNS: read (required for viewing DNS records)
   - ✅ Email: read (required for viewing email forwards)
   
   **Write Access (Required for modifications - use with caution):**
   - ⚠️ LiveDNS: write (enables DNS modification, deletion, bulk operations)
   - ⚠️ Email: write (enables email forward creation, updates, deletions)

5. Copy the token (you won't see it again!)

**Security Best Practices:**
- Create separate tokens for read-only vs. write operations
- Use read-only tokens for routine checks/monitoring
- Only use write tokens when actively making changes
- Rotate tokens regularly (every 90 days recommended)
- Delete unused tokens immediately
- **Never share or commit tokens to version control**

### Step 2: Store Token

Scripts check for credentials in priority order:
1. **`GANDI_API_TOKEN` environment variable** (checked first)
2. **`~/.config/gandi/api_token` file** (fallback if env var not set)

**Choose the method that fits your workflow:**

#### Option A: Environment Variable (Recommended for CI/CD)

```bash
# Set environment variable (replace YOUR_PAT with actual token)
export GANDI_API_TOKEN="YOUR_PERSONAL_ACCESS_TOKEN"

# Add to shell profile for persistence (~/.bashrc, ~/.zshrc, etc.)
echo 'export GANDI_API_TOKEN="YOUR_PERSONAL_ACCESS_TOKEN"' >> ~/.bashrc
```

**Benefits:**
- ✅ CI/CD friendly (standard pattern for automation)
- ✅ Container-ready (no file mounts needed)
- ✅ Works with secret management tools (1Password, Vault, etc.)
- ✅ Easy to switch between multiple tokens

#### Option B: File-based (Recommended for local development)

```bash
# Create config directory
mkdir -p ~/.config/gandi

# Store your token (replace YOUR_PAT with actual token)
echo "YOUR_PERSONAL_ACCESS_TOKEN" > ~/.config/gandi/api_token

# Secure the file (owner read-only)
chmod 600 ~/.config/gandi/api_token
```

**Benefits:**
- ✅ Token persists across shell sessions
- ✅ Secure file permissions (0600 = owner read-only)
- ✅ No risk of exposing token in process list
- ✅ Works offline (no external dependencies)

### Step 3: Install Dependencies

**Required:** Node.js >= 18.0.0

```bash
cd gandi-skill/scripts

# Install npm dependencies
npm install

# Verify installation
npm list --depth=0
```

**Expected packages:**
- axios (HTTP client for Gandi API)
- Any other dependencies listed in package.json

**Troubleshooting:**
- If `node` or `npm` not found: Install Node.js from [nodejs.org](https://nodejs.org/)
- If permission errors: Don't use `sudo` - fix npm permissions or use nvm
- If package errors: Delete `node_modules/` and `package-lock.json`, then `npm install` again

### Step 4: Test Authentication

```bash
cd gandi-skill/scripts
node test-auth.js
```

Expected output:
```
✅ Authentication successful!

Your organizations:
  1. Personal Account (uuid-here)
     Type: individual

🎉 You're ready to use the Gandi skill!
```

### Step 5: Setup Contact Information (Optional, for Domain Registration)

If you plan to register domains, save your contact information once for reuse:

```bash
cd gandi-skill/scripts
node setup-contact.js
```

**The script will prompt for:**
- Name (first and last)
- Email address
- Phone number (international format: +1.5551234567)
- Street address
- City
- State/Province (for US: 2-letter code like OH, automatically formatted to US-OH)
- ZIP/Postal code
- Country (2-letter code: US, FR, etc.)
- Type (individual or company)
- **Privacy preference:** Retain or auto-purge contact after registration

**Contact information is saved to:**
- `~/.config/gandi/contact.json`
- Permissions: 600 (owner read-write only)
- Outside the skill directory (never committed to git)

**Privacy Options:**

1. **RETAIN (default):** Keep contact saved for future registrations
   - Best for frequent domain registrations
   - Setup once, use forever
   - Delete manually anytime with `delete-contact.js`

2. **PURGE:** Auto-delete contact after each registration
   - Best for privacy-conscious users
   - Contact info only exists during registration
   - Must re-enter for next registration

**Managing saved contact:**
```bash
# View current contact
node view-contact.js

# Update contact info or privacy preference
node setup-contact.js

# Delete saved contact manually
node delete-contact.js

# Delete without confirmation
node delete-contact.js --force
```

**One-time purge override:**
```bash
# Register and delete contact (even if preference is "retain")
node register-domain.js example.com --purge-contact
```

## Usage Examples

### List Your Domains

```bash
node list-domains.js
```

Output shows:
- Domain names
- Expiration dates
- Auto-renewal status
- Services (LiveDNS, Email, etc.)
- Organization ownership

### List DNS Records

```bash
node list-dns.js example.com
```

Output shows:
- All DNS records grouped by type
- TTL values
- Record names and values
- Nameservers

### Using from Moltbot

Once configured, you can use natural language:

> "List my Gandi domains"

> "Show DNS records for example.com"

> "When does example.com expire?"

> "Is auto-renewal enabled for example.com?"

## Domain Availability Checking

### Check Single Domain

Check if a specific domain is available for registration:

```bash
node check-domain.js example.com
```

**Features:**
- Shows availability status (available/unavailable/pending/error)
- Displays pricing information (registration, renewal, transfer)
- Lists supported features (DNSSEC, LiveDNS, etc.)
- Shows TLD information

**Example Output:**
```
🔍 Checking availability for: example.com

Domain: example.com

✅ Status: AVAILABLE

💰 Pricing:
  1 year: 12.00 EUR (+ 2.40 tax)
  2 years: 24.00 EUR (+ 4.80 tax)

📋 Supported Features:
  • create
  • dnssec
  • livedns

🌐 TLD Information:
  Extension: com
```

### Smart Domain Suggestions

Find available alternatives with TLD variations and name modifications:

```bash
# Check all configured TLDs + variations
node suggest-domains.js example

# Check specific TLDs only
node suggest-domains.js example --tlds com,net,io

# Skip name variations (only check TLDs)
node suggest-domains.js example --no-variations

# Output as JSON
node suggest-domains.js example --json
```

**Name Variation Patterns:**
1. **Hyphenated**: Adds hyphens between word boundaries (`example` → `ex-ample`)
2. **Abbreviated**: Removes vowels (`example` → `exmpl`)
3. **Prefix**: Adds common prefixes (`example` → `get-example`, `my-example`)
4. **Suffix**: Adds common suffixes (`example` → `example-app`, `example-hub`)
5. **Numbers**: Appends numbers (`example` → `example2`, `example3`)

**Example Output:**
```
🔍 Checking availability for: example

📊 Checking 13 TLDs and generating variations...

═══════════════════════════════════════════════════════
📋 EXACT MATCHES (Different TLDs)
═══════════════════════════════════════════════════════

✅ Available:

  example.net                    12.00 EUR
  example.io                     39.00 EUR
  example.dev                    15.00 EUR

❌ Unavailable:

  example.com                    (unavailable)
  example.org                    (unavailable)

═══════════════════════════════════════════════════════
🎨 NAME VARIATIONS
═══════════════════════════════════════════════════════

Hyphenated:

  ✅ ex-ample.com                12.00 EUR

Prefix:

  ✅ get-example.com             12.00 EUR
  ✅ my-example.com              12.00 EUR

Suffix:

  ✅ example-app.com             12.00 EUR
  ✅ example-io.com              12.00 EUR

═══════════════════════════════════════════════════════
📊 SUMMARY: 8 available domains found
═══════════════════════════════════════════════════════
```

### Configuration

Domain checker configuration is stored in `gandi-skill/config/domain-checker-defaults.json`.

**Structure:**
```json
{
  "tlds": {
    "mode": "extend",
    "defaults": ["com", "net", "org", "info", "io", "dev", "app", "ai", "tech"],
    "custom": []
  },
  "variations": {
    "enabled": true,
    "patterns": ["hyphenated", "abbreviated", "prefix", "suffix", "numbers"],
    "prefixes": ["get", "my", "the", "try"],
    "suffixes": ["app", "hub", "io", "ly", "ai", "hq"],
    "maxNumbers": 3
  },
  "rateLimit": {
    "maxConcurrent": 3,
    "delayMs": 200,
    "maxRequestsPerMinute": 100
  },
  "limits": {
    "maxTlds": 5,
    "maxVariations": 10
  }
}
```

**Rate Limiting & Limits:**
- **maxConcurrent**: Maximum concurrent API requests (default: 3)
- **delayMs**: Delay between requests in milliseconds (default: 200ms)
- **maxRequestsPerMinute**: Hard limit on requests per minute (default: 100, Gandi allows 1000)
- **maxTlds**: Maximum TLDs to check in suggest-domains.js (default: 5)
- **maxVariations**: Maximum name variations to generate (default: 10)

These limits ensure good API citizenship and prevent overwhelming Gandi's API.

**TLD Modes:**
- `"extend"`: Use defaults + custom TLDs (merged list)
- `"replace"`: Use only custom TLDs (ignore defaults)

**Gateway Console Integration:**

When Gateway Console support is added ([#3](https://github.com/chrisagiddings/moltbot-gandi-skill/issues/3)), configuration will be available at:

```yaml
skills:
  entries:
    gandi:
      config:
        domainChecker:
          tlds:
            mode: extend
            defaults: [...]
            custom: [...]
          variations:
            enabled: true
            patterns: [...]
```

See `docs/gateway-config-design.md` for complete configuration architecture.

## DNS Management (Phase 2)

### Add or Update DNS Records

Create or update individual DNS records:

```bash
# Add an A record for root domain
node add-dns-record.js example.com @ A 192.168.1.1

# Add www subdomain pointing to root
node add-dns-record.js example.com www CNAME @

# Add MX record for email
node add-dns-record.js example.com @ MX "10 mail.example.com."

# Add TXT record for SPF
node add-dns-record.js example.com @ TXT "v=spf1 include:_spf.google.com ~all"

# Add with custom TTL (5 minutes)
node add-dns-record.js example.com api A 192.168.1.10 300
```

**Supported record types:** A, AAAA, CNAME, MX, TXT, NS, SRV, CAA, PTR

### Delete DNS Records

Remove specific DNS records:

```bash
# Delete old A record
node delete-dns-record.js example.com old A

# Delete with confirmation prompt
node delete-dns-record.js example.com test CNAME

# Delete without confirmation
node delete-dns-record.js example.com old A --force
```

### Bulk DNS Operations

Replace all DNS records at once:

```bash
# From JSON file
node update-dns-bulk.js example.com new-records.json

# From stdin
cat records.json | node update-dns-bulk.js example.com

# Skip automatic snapshot
node update-dns-bulk.js example.com records.json --no-snapshot

# Skip confirmation
node update-dns-bulk.js example.com records.json --force
```

**JSON format:**
```json
[
  {
    "rrset_name": "@",
    "rrset_type": "A",
    "rrset_ttl": 10800,
    "rrset_values": ["192.168.1.1"]
  },
  {
    "rrset_name": "www",
    "rrset_type": "CNAME",
    "rrset_ttl": 10800,
    "rrset_values": ["@"]
  },
  {
    "rrset_name": "@",
    "rrset_type": "MX",
    "rrset_ttl": 10800,
    "rrset_values": ["10 mail.example.com.", "20 mail2.example.com."]
  }
]
```

### DNS Zone Snapshots

Create safety backups before making changes:

```bash
# Create a snapshot
node create-snapshot.js example.com "Before migration"

# List all snapshots
node list-snapshots.js example.com

# Restore from a snapshot
node restore-snapshot.js example.com abc123-def456-ghi789

# Restore without confirmation
node restore-snapshot.js example.com abc123-def456-ghi789 --force
```

**Automatic snapshots:**
- Bulk updates automatically create snapshots (unless `--no-snapshot`)
- Snapshots are named with timestamp
- Use snapshots for easy rollback

### Common DNS Configuration Examples

#### Basic Website Setup
```bash
# Root domain
node add-dns-record.js example.com @ A 192.168.1.1

# WWW subdomain
node add-dns-record.js example.com www CNAME @
```

#### Email Configuration (Google Workspace)
```bash
# MX records
node add-dns-record.js example.com @ MX "1 ASPMX.L.GOOGLE.COM."
node add-dns-record.js example.com @ MX "5 ALT1.ASPMX.L.GOOGLE.COM."
node add-dns-record.js example.com @ MX "5 ALT2.ASPMX.L.GOOGLE.COM."

# SPF record
node add-dns-record.js example.com @ TXT "v=spf1 include:_spf.google.com ~all"
```

#### Domain Redirect Setup
To redirect one domain to another:

```bash
# Point root domain to same server
node add-dns-record.js old-domain.com @ A 192.168.1.1

# Point www to same CNAME
node add-dns-record.js old-domain.com www CNAME @
```

Then configure HTTP 301 redirect at the server level.

#### Subdomain Setup
```bash
# API subdomain
node add-dns-record.js example.com api A 192.168.1.10

# Staging subdomain
node add-dns-record.js example.com staging A 192.168.1.20

# Wildcard subdomain
node add-dns-record.js example.com "*" A 192.168.1.100
```

## Email Forwarding (Phase 2)

### List Email Forwards

See all email forwards configured for a domain:

```bash
node list-email-forwards.js example.com
```

### Create Email Forwards

Forward emails to one or more destinations:

```bash
# Simple forward
node add-email-forward.js example.com hello you@personal.com

# Forward to multiple destinations
node add-email-forward.js example.com support team1@example.com team2@example.com

# Catch-all forward (forwards all unmatched emails)
node add-email-forward.js example.com @ catchall@example.com
```

### Update Email Forwards

Change the destination(s) for an existing forward:

```bash
# Update single destination
node update-email-forward.js example.com hello newemail@personal.com

# Update to multiple destinations
node update-email-forward.js example.com support new1@example.com new2@example.com
```

**Note:** This replaces all existing destinations with the new ones.

### Delete Email Forwards

Remove email forwards:

```bash
# Delete with confirmation prompt
node delete-email-forward.js example.com old

# Delete without confirmation
node delete-email-forward.js example.com old --force

# Delete catch-all forward
node delete-email-forward.js example.com @ --force
```

### Common Email Forwarding Use Cases

#### Basic Email Forwarding
```bash
# Forward contact@ to your personal email
node add-email-forward.js example.com contact you@gmail.com

# Forward sales@ to team
node add-email-forward.js example.com sales team@example.com
```

#### Domain Migration Email Forwarding
```bash
# Forward all email from old domain to new domain
# Preserves the local part (username before @)

# First, list existing forwards on old domain
node list-email-forwards.js old-domain.com

# Then create matching forwards on new domain
node add-email-forward.js old-domain.com contact contact@new-domain.com
node add-email-forward.js old-domain.com support support@new-domain.com

# Or use catch-all to forward everything
node add-email-forward.js old-domain.com @ admin@new-domain.com
```

#### Team Distribution Lists
```bash
# Forward to entire team
node add-email-forward.js example.com team alice@example.com bob@example.com charlie@example.com

# Update team members
node update-email-forward.js example.com team alice@example.com dave@example.com
```

#### Catch-All Configuration
```bash
# Forward all unmatched emails to one address
node add-email-forward.js example.com @ catchall@example.com

# Forward all unmatched emails to multiple addresses
node add-email-forward.js example.com @ admin1@example.com admin2@example.com
```

**Note:** Catch-all forwards only apply to email addresses that don't have specific forwards configured.

### Email Forward Management Tips

1. **Test after creating:** Send a test email to verify forwarding works
2. **Use specific forwards over catch-all:** More control and easier to manage
3. **Multiple destinations:** Email is sent to all destinations (not round-robin)
4. **Order doesn't matter:** Gandi processes most specific match first
5. **Check spam folders:** Forwarded emails may be filtered by recipient's spam filter

### Example: Complete Domain Email Setup

```bash
# 1. Set up MX records (if not already done)
node add-dns-record.js example.com @ MX "10 spool.mail.gandi.net."
node add-dns-record.js example.com @ MX "50 fb.mail.gandi.net."

# 2. Create specific forwards
node add-email-forward.js example.com hello you@personal.com
node add-email-forward.js example.com support team@example.com
node add-email-forward.js example.com sales sales-team@example.com

# 3. Set up catch-all for everything else
node add-email-forward.js example.com @ admin@example.com

# 4. List all forwards to verify
node list-email-forwards.js example.com
```

## Helper Scripts

All scripts are in `gandi-skill/scripts/`:

### Authentication & Setup
| Script | Purpose |
|--------|---------|
| `test-auth.js` | Verify authentication works |
| `setup-contact.js` | Save contact info for domain registration (run once) |
| `view-contact.js` | View saved contact information |
| `delete-contact.js` | Delete saved contact (with optional --force) |

### Domain & DNS Viewing
| Script | Purpose |
|--------|---------|
| `list-domains.js` | Show all domains in account |
| `list-dns.js <domain>` | Show DNS records for domain |
| `check-domain.js <domain>` | Check single domain availability + pricing |
| `suggest-domains.js <name>` | Smart domain suggestions with variations |
| `check-ssl.js` | Check SSL certificate status for all domains |

### DNS Modification (Phase 2)
| Script | Purpose |
|--------|---------|
| `add-dns-record.js <domain> <name> <type> <value> [ttl]` | Add or update a DNS record |
| `delete-dns-record.js <domain> <name> <type> [--force]` | Delete a DNS record |
| `update-dns-bulk.js <domain> <records.json> [--no-snapshot] [--force]` | Bulk update all DNS records |
| `list-snapshots.js <domain>` | List DNS zone snapshots |
| `create-snapshot.js <domain> [name]` | Create a DNS zone snapshot |
| `restore-snapshot.js <domain> <snapshot-id> [--force]` | Restore DNS zone from snapshot |

### Email Forwarding (Phase 2)
| Script | Purpose |
|--------|---------|
| `list-email-forwards.js <domain>` | List all email forwards for a domain |
| `add-email-forward.js <domain> <mailbox> <destination> [dest2...]` | Create email forward (use @ for catch-all) |
| `update-email-forward.js <domain> <mailbox> <destination> [dest2...]` | Update email forward destinations |
| `delete-email-forward.js <domain> <mailbox> [--force]` | Delete email forward |

### Core Library
| Script | Purpose |
|--------|---------|
| `gandi-api.js` | Core API client (importable) |

## Configuration

### Default Configuration

- **Token file:** `~/.config/gandi/api_token` (API authentication)
- **Contact file:** `~/.config/gandi/contact.json` (domain registration info, optional)
- **API URL:** `https://api.gandi.net` (production)

### Sandbox Testing

To use Gandi's sandbox environment:

```bash
# Create sandbox token at: https://admin.sandbox.gandi.net
echo "YOUR_SANDBOX_TOKEN" > ~/.config/gandi/api_token
echo "https://api.sandbox.gandi.net" > ~/.config/gandi/api_url
```

## Troubleshooting

### Token Not Found

```bash
# Verify file exists
ls -la ~/.config/gandi/api_token

# Should show: -rw------- (600 permissions)
```

### Authentication Failed (401)

- Token is incorrect or expired
- Create new token at Gandi Admin
- Update stored token file

### Permission Denied (403)

- Token doesn't have required scopes
- Create new token with Domain:read and LiveDNS:read
- Verify organization membership

### Domain Not Using LiveDNS

If you get "not using Gandi LiveDNS" error:
1. Log in to Gandi Admin
2. Go to domain management
3. Attach LiveDNS service to the domain

### Rate Limit (429)

Gandi allows 1000 requests/minute. If exceeded:
- Wait 60 seconds
- Reduce frequency of API calls

## API Reference

The skill provides importable functions:

```javascript
import { 
  testAuth,
  listDomains,
  getDomain,
  listDnsRecords,
  getDnsRecord,
  checkAvailability
} from './gandi-api.js';

// Test authentication
const auth = await testAuth();

// List domains
const domains = await listDomains();

// Get domain info
const domain = await getDomain('example.com');

// List DNS records
const records = await listDnsRecords('example.com');

// Get specific DNS record
const record = await getDnsRecord('example.com', '@', 'A');

// Check availability
const available = await checkAvailability(['example.com', 'example.net']);
```

## Security

### Token Storage

✅ **DO:**
- Store at `~/.config/gandi/api_token`
- Use 600 permissions (owner read-only)
- Rotate tokens regularly
- Use minimal required scopes

❌ **DON'T:**
- Commit tokens to repositories
- Share tokens between users
- Give tokens unnecessary permissions
- Store tokens in scripts

### Token Scopes

**Phase 1 (current):**
- Domain: read
- LiveDNS: read

**Phase 2+ (future):**
- Domain: read, write (for registration, renewal)
- LiveDNS: read, write (for DNS modifications)
- Certificate: read (optional, for SSL certs)
- Email: read, write (optional, for email config)

## Architecture

```
gandi-skill/
├── SKILL.md                 # This file
├── references/              # API documentation
│   ├── api-overview.md
│   ├── authentication.md
│   ├── domains.md
│   ├── livedns.md
│   └── setup.md
└── scripts/                 # Helper utilities
    ├── package.json
    ├── gandi-api.js         # Core API client
    ├── test-auth.js         # Test authentication
    ├── list-domains.js      # List domains
    └── list-dns.js          # List DNS records
```

## Development Roadmap

**Phase 1: Read Operations** (✅ Current)
- Authentication with PAT
- List domains
- Get domain details
- List DNS records
- Basic error handling

**Phase 2: DNS Modifications**
- Add DNS records
- Update DNS records
- Delete DNS records
- Bulk DNS operations

**Phase 3: Domain Management**
- Domain registration
- Domain renewal
- Auto-renewal configuration
- Nameserver management

**Phase 4: Multi-Organization** ([#1](https://github.com/chrisagiddings/moltbot-gandi-skill/issues/1))
- Profile-based token management
- Organization selection
- Multiple token support

**Phase 5: Advanced Features**
- DNSSEC management
- Certificate management
- Email/mailbox configuration
- Domain transfer operations

## Contributing

See [Contributing Guide](../../README.md#contributing) in the main README.

## Support

- **Issues:** [GitHub Issues](https://github.com/chrisagiddings/moltbot-gandi-skill/issues)
- **Documentation:** [Reference Guides](./references/)
- **Gandi Support:** [help.gandi.net](https://help.gandi.net/)

## License

MIT License - See [LICENSE](../../LICENSE)
