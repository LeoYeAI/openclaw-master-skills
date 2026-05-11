# LiveDNS Management API

Gandi LiveDNS API for managing DNS zones and records.

**Base Endpoint:** `https://api.gandi.net/v5/livedns/`

## Overview

LiveDNS is Gandi's modern DNS hosting service. The API allows you to:
- Manage DNS zones and records
- Create and update DNS records (A, AAAA, CNAME, MX, TXT, etc.)
- Configure DNSSEC
- Set up zone sharing and AXFR
- Manage DNS snapshots

## Domains & Zones

### List Domains

**GET** `/v5/livedns/domains`

List all domains using Gandi LiveDNS.

**Query Parameters:**
- `per_page` - Items per page (default: 25, max: 100)
- `page` - Page number
- `sharing_id` - Filter by organization

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_PAT" \\
     https://api.gandi.net/v5/livedns/domains
```

### Get Domain Info

**GET** `/v5/livedns/domains/{fqdn}`

Get DNS information for a specific domain.

**Response includes:**
- Zone UUID
- Nameservers
- DNSSEC status
- Automatic snapshots settings

### Attach Domain to Zone

**POST** `/v5/livedns/domains/{fqdn}`

Attach a domain to use Gandi LiveDNS.

**Example:**
```bash
curl -X POST \\
     -H "Authorization: Bearer YOUR_PAT" \\
     -H "Content-Type: application/json" \\
     https://api.gandi.net/v5/livedns/domains/example.com
```

### Detach Domain

**DELETE** `/v5/livedns/domains/{fqdn}`

Detach a domain from LiveDNS (reverts to parked nameservers).

## DNS Records

### List All Records

**GET** `/v5/livedns/domains/{fqdn}/records`

Get all DNS records for a domain.

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_PAT" \\
     https://api.gandi.net/v5/livedns/domains/example.com/records
```

**Response:**
```json
[
  {
    "rrset_type": "A",
    "rrset_name": "@",
    "rrset_ttl": 10800,
    "rrset_values": ["192.168.1.1"]
  },
  {
    "rrset_type": "CNAME",
    "rrset_name": "www",
    "rrset_ttl": 10800,
    "rrset_values": ["@"]
  }
]
```

### Get Records by Type

**GET** `/v5/livedns/domains/{fqdn}/records/{name}/{type}`

Get specific DNS records by name and type.

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_PAT" \\
     https://api.gandi.net/v5/livedns/domains/example.com/records/@/A
```

### Create/Update Records

**PUT** `/v5/livedns/domains/{fqdn}/records/{name}/{type}`

Create or replace DNS records.

**Request Body:**
```json
{
  "rrset_ttl": 10800,
  "rrset_values": ["192.168.1.1", "192.168.1.2"]
}
```

**Example - Add A record:**
```bash
curl -X PUT \\
     -H "Authorization: Bearer YOUR_PAT" \\
     -H "Content-Type: application/json" \\
     -d '{"rrset_ttl": 10800, "rrset_values": ["192.168.1.1"]}' \\
     https://api.gandi.net/v5/livedns/domains/example.com/records/@/A
```

**Example - Add subdomain:**
```bash
curl -X PUT \\
     -H "Authorization: Bearer YOUR_PAT" \\
     -H "Content-Type: application/json" \\
     -d '{"rrset_ttl": 10800, "rrset_values": ["192.168.1.10"]}' \\
     https://api.gandi.net/v5/livedns/domains/example.com/records/blog/A
```

### Update All Records

**PUT** `/v5/livedns/domains/{fqdn}/records`

Replace all DNS records at once (useful for bulk updates).

**Request Body:**
```json
{
  "items": [
    {
      "rrset_type": "A",
      "rrset_name": "@",
      "rrset_ttl": 10800,
      "rrset_values": ["192.168.1.1"]
    },
    {
      "rrset_type": "CNAME",
      "rrset_name": "www",
      "rrset_ttl": 10800,
      "rrset_values": ["@"]
    }
  ]
}
```

### Delete Records

**DELETE** `/v5/livedns/domains/{fqdn}/records/{name}/{type}`

Delete specific DNS records.

**Example:**
```bash
curl -X DELETE \\
     -H "Authorization: Bearer YOUR_PAT" \\
     https://api.gandi.net/v5/livedns/domains/example.com/records/old/A
```

## Record Types

Supported DNS record types:

| Type | Description | Example Value |
|------|-------------|---------------|
| **A** | IPv4 address | `192.168.1.1` |
| **AAAA** | IPv6 address | `2001:db8::1` |
| **CNAME** | Canonical name | `example.com.` |
| **MX** | Mail exchange | `10 mail.example.com.` |
| **TXT** | Text record | `"v=spf1 include:_spf.google.com ~all"` |
| **NS** | Nameserver | `ns1.example.com.` |
| **SRV** | Service locator | `10 20 5060 sipserver.example.com.` |
| **CAA** | Certificate authority | `0 issue "letsencrypt.org"` |
| **PTR** | Pointer | `example.com.` |
| **SPF** | Sender policy | `"v=spf1 ..."` (use TXT instead) |

### Record Name Conventions

- `@` - Root domain (example.com)
- `www` - Subdomain (www.example.com)
- `*` - Wildcard (*.example.com)
- `_service._proto` - Service records (e.g., `_http._tcp`)

### TTL (Time To Live)

- Measured in seconds
- Default: 10800 (3 hours)
- Minimum: 300 (5 minutes)
- Maximum: 2592000 (30 days)
- Lower TTL = faster propagation, more DNS queries
- Higher TTL = slower propagation, fewer DNS queries

## Common Record Examples

### Basic Website Setup

```json
{
  "items": [
    {
      "rrset_type": "A",
      "rrset_name": "@",
      "rrset_ttl": 10800,
      "rrset_values": ["192.168.1.1"]
    },
    {
      "rrset_type": "CNAME",
      "rrset_name": "www",
      "rrset_ttl": 10800,
      "rrset_values": ["@"]
    }
  ]
}
```

### Email Configuration (Google Workspace)

```json
{
  "items": [
    {
      "rrset_type": "MX",
      "rrset_name": "@",
      "rrset_ttl": 10800,
      "rrset_values": [
        "1 ASPMX.L.GOOGLE.COM.",
        "5 ALT1.ASPMX.L.GOOGLE.COM.",
        "5 ALT2.ASPMX.L.GOOGLE.COM.",
        "10 ALT3.ASPMX.L.GOOGLE.COM.",
        "10 ALT4.ASPMX.L.GOOGLE.COM."
      ]
    },
    {
      "rrset_type": "TXT",
      "rrset_name": "@",
      "rrset_ttl": 10800,
      "rrset_values": [
        "v=spf1 include:_spf.google.com ~all"
      ]
    }
  ]
}
```

### DKIM Record

```json
{
  "rrset_type": "TXT",
  "rrset_name": "default._domainkey",
  "rrset_ttl": 10800,
  "rrset_values": [
    "v=DKIM1; k=rsa; p=MIGfMA0GCS..."
  ]
}
```

### CAA Records (Let's Encrypt)

```json
{
  "rrset_type": "CAA",
  "rrset_name": "@",
  "rrset_ttl": 10800,
  "rrset_values": [
    "0 issue \"letsencrypt.org\"",
    "0 issuewild \"letsencrypt.org\""
  ]
}
```

## Snapshots

LiveDNS supports automatic snapshots of your DNS zone configuration.

### List Snapshots

**GET** `/v5/livedns/domains/{fqdn}/snapshots`

Get list of available snapshots.

### Create Snapshot

**POST** `/v5/livedns/domains/{fqdn}/snapshots`

Create a manual snapshot.

**Request Body:**
```json
{
  "name": "Before migration"
}
```

### Restore Snapshot

**POST** `/v5/livedns/domains/{fqdn}/snapshots/{snapshot_id}`

Restore DNS zone from a snapshot.

### Delete Snapshot

**DELETE** `/v5/livedns/domains/{fqdn}/snapshots/{snapshot_id}`

Delete a snapshot.

## DNSSEC

### Get DNSSEC Keys

**GET** `/v5/livedns/domains/{fqdn}/dnskeys`

Get DNSSEC public keys for the domain.

### Enable DNSSEC

**PUT** `/v5/livedns/domains/{fqdn}/dnskeys`

Enable DNSSEC for the domain.

**Note:** DNSSEC must be supported by your TLD and enabled at the registry level.

## AXFR & Zone Transfer

### TSIG Keys

For secure zone transfers, you can create TSIG (Transaction Signature) keys.

### List TSIG Keys

**GET** `/v5/livedns/axfr/tsig`

List your TSIG keys.

### Create TSIG Key

**POST** `/v5/livedns/axfr/tsig`

Create a new TSIG key for zone transfers.

### Get TSIG Key

**GET** `/v5/livedns/axfr/tsig/{id}`

Get details of a specific TSIG key, including configuration samples for:
- BIND
- Knot
- NSD
- PowerDNS

## Best Practices

1. **Use appropriate TTL values**
   - Lower (300s) for testing/migration
   - Higher (10800s+) for stable production

2. **Always test changes**
   - Use `dig` or `nslookup` to verify
   - Wait for TTL to expire before expecting full propagation

3. **Create snapshots before major changes**
   - Easy rollback if something goes wrong

4. **Use DNSSEC when possible**
   - Enhanced security against DNS spoofing

5. **Organize with subdomains**
   - `api.example.com`, `staging.example.com`, etc.

6. **Implement SPF, DKIM, DMARC**
   - Improve email deliverability

7. **Use CAA records**
   - Restrict which CAs can issue certificates

8. **Monitor DNS changes**
   - Keep audit logs of who changed what

## DNS Propagation

After making DNS changes:

1. **Local DNS cache:** ~5 minutes
2. **ISP DNS cache:** Based on TTL
3. **Global propagation:** 24-48 hours (worst case)

**Speed up propagation:**
- Lower TTL before making changes
- Wait for old TTL to expire
- Make your changes
- Raise TTL back to normal

## Troubleshooting

### Changes not visible

1. Check TTL - may need to wait
2. Clear local DNS cache:
   - macOS: `sudo dscacheutil -flushcache`
   - Windows: `ipconfig /flushdns`
   - Linux: `sudo systemd-resolve --flush-caches`
3. Query Gandi's nameservers directly:
   ```bash
   dig @ns1.gandi.net example.com
   ```

### Record validation errors

- Ensure proper formatting
- Include trailing dots for FQDNs (e.g., `mail.example.com.`)
- Check MX priority syntax
- Validate TXT record quotes

### Zone transfer issues

- Verify TSIG key configuration
- Check firewall rules (port 53 TCP)
- Ensure secondary nameserver is authorized

## Further Reading

- [API Overview](./api-overview.md)
- [Authentication](./authentication.md)
- [Domain Management](./domains.md)
- [Official LiveDNS Docs](https://api.gandi.net/docs/livedns/)
- [Gandi DNS Documentation](https://docs.gandi.net/en/domain_names/common_operations/dns_records.html)
