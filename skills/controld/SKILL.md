---
name: controld
description: "Manage Control D DNS filtering service via API. Use for DNS profile management, device configuration, custom blocking rules, service filtering, analytics settings, and network diagnostics. Triggers when user mentions Control D, DNS filtering, DNS blocking, device DNS setup, or managing DNS profiles."
homepage: https://controld.com
metadata: { "openclaw": { "emoji": "🛡️", "requires": { "bins": ["curl", "jq"] }, "primaryEnv": "CONTROLD_API_TOKEN" } }
---

# Control D DNS Management

Control D is a DNS filtering and privacy service. This skill enables full API access.

## Authentication

Store API token in environment variable or pass directly:
```bash
export CONTROLD_API_TOKEN="your-api-token"
```

Get your API token from: https://controld.com/dashboard (Account Settings > API)

**Token Types:**
- **Read** - View-only access to Profiles, Devices, and Analytics
- **Write** - View and modify data (create/modify/delete)

**Security Tip:** Restrict tokens by allowed IP addresses for automation hosts.

## API Reference

Base URL: `https://api.controld.com`
Auth: `Authorization: Bearer $CONTROLD_API_TOKEN`

### Profiles

DNS filtering profiles define blocking rules, filters, and service controls.

```bash
# List all profiles
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/profiles" | jq '.body.profiles'

# Create profile
curl -s -X POST -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Profile"}' \
  "https://api.controld.com/profiles"

# Clone existing profile
curl -s -X POST -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Cloned Profile","clone_profile_id":"PROFILE_ID"}' \
  "https://api.controld.com/profiles"

# Update profile
curl -s -X PUT -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"New Name"}' \
  "https://api.controld.com/profiles/PROFILE_ID"

# Delete profile
curl -s -X DELETE -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/profiles/PROFILE_ID"
```

### Profile Options

```bash
# List available profile options
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/profiles/options" | jq '.body.options'

# Update profile option (status: 1=enabled, 0=disabled)
curl -s -X PUT -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":1,"value":"some_value"}' \
  "https://api.controld.com/profiles/PROFILE_ID/options/OPTION_NAME"
```

### Devices

Devices are DNS endpoints that use profiles for filtering.

```bash
# List all devices
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/devices" | jq '.body.devices'

# List device types (icons)
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/devices/types" | jq '.body.types'

# Create device
curl -s -X POST -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Home Router","profile_id":"PROFILE_ID","icon":"router"}' \
  "https://api.controld.com/devices"

# Update device
curl -s -X PUT -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"New Name","status":1}' \
  "https://api.controld.com/devices/DEVICE_ID"

# Delete device
curl -s -X DELETE -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/devices/DEVICE_ID"
```

**Device Icons:** `desktop-windows`, `desktop-mac`, `desktop-linux`, `mobile-ios`, `mobile-android`, `browser-chrome`, `browser-firefox`, `browser-edge`, `browser-brave`, `browser-other`, `tv-apple`, `tv-android`, `tv-firetv`, `tv-samsung`, `tv`, `router-asus`, `router-ddwrt`, `router-firewalla`, `router-freshtomato`, `router-glinet`, `router-openwrt`, `router-opnsense`, `router-pfsense`, `router-synology`, `router-ubiquiti`, `router-windows`, `router-linux`, `router`

**Device Status:** `0`=pending, `1`=active, `2`=soft-disabled, `3`=hard-disabled

### Filters

Native and external blocking filters for profiles.

```bash
# List native filters for profile
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/profiles/PROFILE_ID/filters" | jq '.body.filters'

# List external filters
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/profiles/PROFILE_ID/filters/external" | jq '.body.filters'

# Enable/disable filter (status: 1=enabled, 0=disabled)
curl -s -X PUT -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":1}' \
  "https://api.controld.com/profiles/PROFILE_ID/filters/filter/FILTER_ID"
```

### Services

Block, bypass, or redirect specific services (apps/websites).

```bash
# List service categories
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/services/categories" | jq '.body.categories'

# List services in category
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/services/categories/CATEGORY" | jq '.body.services'

# List profile services with their actions
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/profiles/PROFILE_ID/services" | jq '.body.services'

# Set service action (do: 0=block, 1=bypass, 2=spoof)
curl -s -X PUT -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"do":0,"status":1}' \
  "https://api.controld.com/profiles/PROFILE_ID/services/SERVICE_ID"
```

### Custom Rules

Create custom blocking/bypass rules for specific domains.

```bash
# List rule folders
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/profiles/PROFILE_ID/groups" | jq '.body.groups'

# Create rule folder
curl -s -X POST -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Rules","do":0}' \
  "https://api.controld.com/profiles/PROFILE_ID/groups"

# Update rule folder
curl -s -X PUT -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"do":0,"status":1}' \
  "https://api.controld.com/profiles/PROFILE_ID/groups/FOLDER_ID"

# Delete rule folder
curl -s -X DELETE -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/profiles/PROFILE_ID/groups/FOLDER_ID"

# List rules in folder
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/profiles/PROFILE_ID/rules/FOLDER_ID" | jq '.body.rules'

# Create custom rule (do: 0=block, 1=bypass, 2=spoof, 3=redirect)
curl -s -X POST -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"hostnames":["ads.example.com","tracking.example.com"],"do":0,"status":1}' \
  "https://api.controld.com/profiles/PROFILE_ID/rules"

# Delete custom rule
curl -s -X DELETE -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/profiles/PROFILE_ID/rules/HOSTNAME"
```

**Rule Actions (do):** `0`=block, `1`=bypass, `2`=spoof (resolve via proxy), `3`=redirect

### Default Rule

Set default action for unmatched domains.

```bash
# Get default rule
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/profiles/PROFILE_ID/default" | jq '.body.default'

# Set default rule
curl -s -X PUT -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"do":1,"status":1}' \
  "https://api.controld.com/profiles/PROFILE_ID/default"
```

### Proxies

List available proxy locations for traffic redirection (spoofing).

```bash
# List all proxy locations
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/proxies" | jq '.body.proxies'
```

Use proxy PK values with the `via` parameter when setting service/rule actions to `do:2` (spoof).

### IP Access Control

Manage known/allowed IPs for devices.

```bash
# List known IPs for device
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"DEVICE_ID"}' \
  "https://api.controld.com/access" | jq '.body.ips'

# Learn new IPs
curl -s -X POST -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"DEVICE_ID","ips":["1.2.3.4","5.6.7.8"]}' \
  "https://api.controld.com/access"

# Delete learned IPs
curl -s -X DELETE -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"DEVICE_ID","ips":["1.2.3.4"]}' \
  "https://api.controld.com/access"
```

### Analytics

Configure logging and storage settings.

```bash
# List available log levels (0=off, 1=basic, 2=full)
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/analytics/levels" | jq '.body.levels'

# List storage regions
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/analytics/endpoints" | jq '.body.endpoints'

# Get statistics for a device (requires Full analytics level)
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/stats?device_id=DEVICE_ID&start=2024-01-01&end=2024-01-31" | jq '.body'

# Get activity log (requires Full analytics level)
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/queries?device_id=DEVICE_ID&limit=100" | jq '.body.queries'
```

### Account & Network

```bash
# Get account info
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/users" | jq '.body'

# Get current IP info
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/ip" | jq '.body'

# List network/resolver status
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/network" | jq '.body'
```

---

## Organization Management (Business Accounts)

Organization features require a business account. These endpoints manage multi-user access, sub-organizations, and team deployments.

**Note:** Contact [[email protected]](mailto:[email protected]) from a work email to request business account access.

Organization capabilities include:
- Manage large amounts of end user devices or networks
- Quickly onboard hundreds/thousands of devices using RMM
- Grant access to team members with permission levels
- Group Profiles and Endpoints into Sub-Organizations
- Share Profiles between organizations
- Lock resolvers to specific IP addresses

### Organizations

The organization endpoints operate on the organization associated with your API token (no org_id in path).

```bash
# View organization info (your organization context)
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/organizations/organization" | jq '.body'

# Modify organization settings
curl -s -X PUT -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "name=Updated Org Name&twofa_req=1" \
  "https://api.controld.com/organizations"
```

**Modify Organization Parameters (all optional):**
- `name` (string) — Organization name
- `contact_email` (string) — Primary contact email
- `twofa_req` (integer) — Require 2FA/MFA for members (0=no, 1=yes)
- `stats_endpoint` (string) — Storage region PK from `/analytics/endpoints`
- `max_users` (integer) — Max number of User Devices
- `max_routers` (integer) — Max number of Router Devices
- `address` (string) — Physical address
- `website` (string) — Website URL
- `contact_name` (string) — Contact person name
- `contact_phone` (string) — Phone number
- `parent_profile` (string) — Global Profile ID to enforce on all devices

**Note:** Modifying `max_users` and `max_routers` is a billable event.

### Members

View organization membership.

```bash
# List organization members
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/organizations/members" | jq '.body.members'
```

### Sub-Organizations

Sub-organizations compartmentalize profiles and endpoints into logical groups:
- **Departments** - Internal organizational units
- **Physical sites** - Office locations, branches
- **Customer companies** - For MSPs managing multiple clients
- **Any logical grouping** - Based on your needs

Each sub-org has its own Profiles, Endpoints, and optionally a Global Profile that applies to all its Endpoints.

```bash
# List sub-organizations
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/organizations/sub_organizations" | jq '.body.sub_organizations'

# Create sub-organization
curl -s -X POST -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "name=Customer ABC&contact_email=john@example.com&twofa_req=0&stats_endpoint=ENDPOINT_PK&max_users=50&max_routers=10" \
  "https://api.controld.com/organizations/suborg"
```

**Create Sub-Organization Parameters:**

Required:
- `name` (string) — Organization name
- `contact_email` (string) — Primary contact email
- `twofa_req` (integer) — Require 2FA/MFA (0=no, 1=yes)
- `stats_endpoint` (string) — Storage region PK from `/analytics/endpoints`
- `max_users` (integer) — Max number of User Devices
- `max_routers` (integer) — Max number of Router Devices

Optional:
- `address` (string) — Physical address
- `website` (string) — Website URL
- `contact_name` (string) — Contact person name
- `contact_phone` (string) — Phone number
- `parent_profile` (string) — Global Profile ID to enforce on all devices

### Provisioning Codes

Mass deploy ctrld daemon to endpoints using RMM tools.

```bash
# List provisioning codes
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/provision" | jq '.body.codes'

# Create provisioning code
curl -s -X POST -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id":"PROFILE_ID",
    "device_type":"windows",
    "expires_after":"7d",
    "limit":100,
    "prefix":"office-"
  }' \
  "https://api.controld.com/provision"

# Invalidate provisioning code
curl -s -X PUT -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"invalid"}' \
  "https://api.controld.com/provision/CODE_ID"

# Delete provisioning code
curl -s -X DELETE -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/provision/CODE_ID"
```

**Device Types:** `windows`, `mac`, `linux`

**Deployment Commands:**
```bash
# Windows (PowerShell as Admin)
(Invoke-WebRequest -Uri 'https://api.controld.com/dl/rmm' -UseBasicParsing).Content | Set-Content "$env:TEMP\ctrld_install.ps1"; Invoke-Expression "& '$env:TEMP\ctrld_install.ps1' 'CODE'"

# macOS/Linux
sh -c 'sh -c "$(curl -sSL https://api.controld.com/dl/rmm)" -s CODE'
```

---

## Billing

View billing history, subscriptions, and active products.

```bash
# Get payment history
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/billing/payments" | jq '.body'

# Get active and canceled subscriptions
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/billing/subscriptions" | jq '.body'

# Get currently activated products
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/billing/products" | jq '.body'
```

---

## Mobile Config (Apple Devices)

Generate signed Apple DNS profiles (.mobileconfig) for iOS/macOS devices.

```bash
# Generate mobile config profile for a device
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/mobileconfig/DEVICE_ID" -o config.mobileconfig

# With optional parameters
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/mobileconfig/DEVICE_ID?client_id=my-iphone&dont_sign=0" -o config.mobileconfig

# Exclude specific WiFi networks
curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
  "https://api.controld.com/mobileconfig/DEVICE_ID?exclude_wifi[]=HomeNetwork&exclude_wifi[]=OfficeWiFi" -o config.mobileconfig
```

**Path Parameter:**
- `device_id` (required) — Device/Resolver ID

**Query Parameters (all optional):**
- `exclude_wifi[]` (array) — WiFi SSIDs to exclude from using Control D
- `exclude_domain[]` (array) — Domain names to exclude from using Control D
- `dont_sign` (string) — Set to `1` to return unsigned profile
- `exclude_common` (string) — Set to `1` to exclude common captive portal hostnames from WiFi exclusions
- `client_id` (string) — Optional client name

**Note:** This endpoint returns binary data (not JSON) on success. Errors still return JSON.

---

## Helper Script

Use `scripts/controld.sh` for common operations:

```bash
# List profiles
./scripts/controld.sh profiles list

# Create profile
./scripts/controld.sh profiles create "My Profile"

# List devices
./scripts/controld.sh devices list

# Create device
./scripts/controld.sh devices create "Router" PROFILE_ID router

# Block domain
./scripts/controld.sh rules block PROFILE_ID "ads.example.com"

# Bypass domain
./scripts/controld.sh rules bypass PROFILE_ID "trusted.com"

# Enable filter
./scripts/controld.sh filters enable PROFILE_ID FILTER_ID

# Block service (e.g., facebook, tiktok)
./scripts/controld.sh services block PROFILE_ID SERVICE_ID

# List proxies
./scripts/controld.sh proxies list

# Organization management (business accounts)
./scripts/controld.sh orgs info               # View organization info
./scripts/controld.sh orgs members            # List members
./scripts/controld.sh orgs suborgs            # List sub-organizations
./scripts/controld.sh provision list

# Billing
./scripts/controld.sh billing payments        # Payment history
./scripts/controld.sh billing subscriptions   # Subscriptions
./scripts/controld.sh billing products        # Active products

# Mobile Config (Apple devices)
./scripts/controld.sh mobileconfig DEVICE_ID config.mobileconfig
```

## Common Workflows

### Set Up New Device

1. List profiles: `profiles list`
2. Create or select profile
3. Create device with profile: `devices create NAME PROFILE_ID ICON`
4. Note the resolver addresses (DoH/DoT/IPv4) from response
5. Configure device DNS to use resolvers

### Block Social Media

1. List social media services: `curl ... /services/categories/social`
2. Block each service: `services block PROFILE_ID facebook`
3. Or create custom rules for specific domains

### Enable Ad Blocking

1. List filters: `filters list PROFILE_ID`
2. Enable ad-related filters: `filters enable PROFILE_ID ads`
3. Enable malware filters: `filters enable PROFILE_ID malware`

### Redirect Traffic Through Proxy (Geo-Spoofing)

1. List proxies: `./scripts/controld.sh proxies list`
2. Set service to spoof via proxy:
   ```bash
   curl -s -X PUT -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"do":2,"status":1,"via":"PROXY_PK"}' \
     "https://api.controld.com/profiles/PROFILE_ID/services/SERVICE_ID"
   ```

### Mass Deploy to Enterprise Endpoints

1. Create provisioning code: `provision create`
2. Deploy via RMM using the provided command
3. Monitor endpoint registrations in dashboard

## Rate Limiting

API rate limit: ~1200 requests per 5 minutes (4 req/sec average). Exponential backoff on 429 responses.

## Notes

- Organization endpoints require a business account
- Sub-organization members inherit parent org member permissions unless explicitly added
- Global Profile on a sub-org applies to ALL devices in that sub-org
- Analytics data is stored for 1 month (raw logs) or 1 year (stats)
- SSO supported: Okta OIDC and Microsoft EntraID OIDC

## API Documentation Sources

- **Conceptual docs:** https://docs.controld.com/docs/
- **API reference:** https://docs.controld.com/reference/get-started (JS-rendered)
- **API base URL:** https://api.controld.com

**Verified endpoints (from API reference, March 2026):**
- Core: `/profiles`, `/devices`, `/access`, `/proxies`, `/services`, `/filters`
- Organization: `/organizations/organization`, `/organizations/members`, `/organizations/sub_organizations`, `/organizations/suborg`, `/organizations` (PUT)
- Billing: `/billing/payments`, `/billing/subscriptions`, `/billing/products`
- Mobile Config: `/mobileconfig/{device_id}`
- Provisioning: `/provision`

Organization and billing endpoints require a business account.
