# Domain Management API

Gandi Domain Management API for registering, renewing, transferring, and managing domain names.

**Base Endpoint:** `https://api.gandi.net/v5/domain/`

## Core Operations

### List Domains

**GET** `/v5/domain/domains`

Returns list of domains you have access to.

**Query Parameters:**
- `page` - Page number for pagination
- `per_page` - Items per page (default: 25, max: 100)
- `sort_by` - Sort field (e.g., `fqdn`, `dates.registry_ends_at`)
- `sharing_id` - Filter by organization ID

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_PAT" \\
     https://api.gandi.net/v5/domain/domains
```

### Get Domain Details

**GET** `/v5/domain/domains/{domain}`

Returns detailed information about a specific domain.

**Response includes:**
- FQDN (both ASCII and Unicode for IDN)
- Status (clientHold, clientTransferProhibited, etc.)
- Dates (created, expires, renewal dates)
- Contacts (owner, admin, tech, billing)
- Nameservers
- Services attached (gandilivedns, mailboxv2, etc.)
- Auto-renewal settings
- TLD information
- Transfer lock status

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_PAT" \\
     https://api.gandi.net/v5/domain/domains/example.com
```

## Domain Registration

### Check Availability

**GET** `/v5/domain/check`

Check if domain names are available for registration.

**Query Parameters:**
- `name` - Domain name(s) to check (can be repeated)

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_PAT" \\
     "https://api.gandi.net/v5/domain/check?name=example.com&name=example.net"
```

### Register Domain

**POST** `/v5/domain/domains`

Register a new domain name.

**Request Body:**
```json
{
  "fqdn": "example.com",
  "duration": 1,
  "owner": {
    "email": "owner@example.com",
    "given": "John",
    "family": "Doe",
    "streetaddr": "123 Main St",
    "city": "Paris",
    "zip": "75001",
    "country": "FR",
    "phone": "+33.123456789",
    "type": "individual"
  },
  "admin": "owner",
  "tech": "owner",
  "bill": "owner"
}
```

**Contact shortcuts:**
- Use `"admin": "owner"` to use same contact as owner
- Use `"admin": "bill"` to use same contact as billing

## Domain Renewal

### Renew Domain

**POST** `/v5/domain/domains/{domain}/renew`

Renew an existing domain.

**Request Body:**
```json
{
  "duration": 1
}
```

**Duration:** Number of years (typically 1-10, depends on TLD)

### Auto-Renewal

**GET** `/v5/domain/domains/{domain}/autorenew`

Get auto-renewal settings.

**PUT** `/v5/domain/domains/{domain}/autorenew`

Update auto-renewal settings.

**Request Body:**
```json
{
  "enabled": true,
  "duration": 1,
  "org_id": "your-org-id"
}
```

## Domain Transfer

### Transfer In

**POST** `/v5/domain/domains/{domain}/transfer-in`

Initiate transfer of a domain to Gandi.

**Required:**
- Auth code (from current registrar)
- Contact information
- Transfer lock must be disabled at current registrar

### Get Transfer Status

**GET** `/v5/domain/domains/{domain}/transfer-in/{operation_id}`

Check status of an in-progress transfer.

### Cancel Transfer

**DELETE** `/v5/domain/domains/{domain}/transfer-in/{operation_id}`

Cancel a pending incoming transfer.

## Domain Configuration

### Update Nameservers

**PUT** `/v5/domain/domains/{domain}/nameservers`

Update domain nameservers.

**Request Body:**
```json
{
  "nameservers": [
    "ns1.example.com",
    "ns2.example.com",
    "ns3.example.com"
  ]
}
```

**Requirements:**
- Minimum 1 nameserver
- Maximum depends on TLD (usually 13)
- Must be valid nameserver hostnames

### Update Contacts

**PATCH** `/v5/domain/domains/{domain}/contacts`

Update domain contacts (owner, admin, tech, billing).

**Request Body:**
```json
{
  "owner": {
    "email": "newemail@example.com",
    "given": "Jane",
    "family": "Doe",
    ...
  }
}
```

**Note:** Contact changes may trigger validation emails and registry approval processes.

### Domain Lock

**PUT** `/v5/domain/domains/{domain}`

Enable/disable transfer lock (if supported by TLD).

**Request Body:**
```json
{
  "status": ["clientTransferProhibited"]
}
```

**To unlock:**
```json
{
  "status": []
}
```

## Domain Information

### Contact Information Structure

```json
{
  "given": "John",
  "family": "Doe",
  "email": "john@example.com",
  "streetaddr": "123 Main St",
  "city": "Paris",
  "zip": "75001",
  "country": "FR",
  "phone": "+33.123456789",
  "type": "individual",
  "orgname": "Company Name"
}
```

**Contact types:**
- `individual` - Personal
- `company` - Corporation
- `association` - Association/non-profit
- `publicbody` - Public/government entity

**Optional fields:**
- `mobile` - Mobile phone
- `fax` - Fax number
- `state` - State/province code
- `extra_parameters` - TLD-specific requirements

### Domain Status Codes

Common status codes returned in domain information:

| Status | Meaning |
|--------|---------|
| `clientHold` | Domain suspended by owner |
| `clientUpdateProhibited` | Updates locked |
| `clientTransferProhibited` | Transfer locked |
| `clientDeleteProhibited` | Deletion locked |
| `clientRenewProhibited` | Renewal locked |
| `serverHold` | Suspended by registry/Gandi |
| `pendingTransfer` | Transfer in progress |
| `serverTransferProhibited` | Transfer blocked by registry |

See [Gandi domain status documentation](https://docs.gandi.net/en/domain_names/faq/domain_statuses.html) for details.

### Important Dates

Domain response includes lifecycle dates:

```json
{
  "dates": {
    "registry_created_at": "2019-02-13T10:04:18Z",
    "registry_ends_at": "2021-02-13T10:04:18Z",
    "created_at": "2019-02-13T11:04:18Z",
    "updated_at": "2019-02-25T16:20:49Z",
    "renew_begins_at": "2012-01-01T00:00:00Z",
    "hold_begins_at": "2021-02-13T10:04:18Z",
    "hold_ends_at": "2021-03-30T10:04:18Z",
    "deletes_at": "2021-03-30T00:04:18Z",
    "pending_delete_ends_at": "2021-05-04T10:04:18Z",
    "restore_ends_at": "2021-04-29T10:04:18Z",
    "authinfo_expires_at": "2020-02-25T16:20:49Z"
  }
}
```

**Key dates:**
- `registry_ends_at` - Domain expiration date
- `renew_begins_at` - When renewal becomes available
- `hold_begins_at` - When domain enters hold period
- `deletes_at` - When domain is deleted if not renewed
- `restore_ends_at` - Last date for domain restoration

## TLD-Specific Requirements

Some TLDs have additional requirements:

### Example: .FR domains
```json
{
  "extra_parameters": {
    "birth_date": "1990-01-01",
    "birth_city": "Paris",
    "birth_country": "FR"
  }
}
```

### Example: .EU domains
```json
{
  "extra_parameters": {
    "eu_citizen": true
  }
}
```

Consult [Gandi TLD requirements](https://docs.gandi.net/en/domain_names/common_operations/index.html) for specific TLDs.

## Tags

Add custom tags to domains for organization:

**PUT** `/v5/domain/domains/{domain}`

```json
{
  "tags": ["production", "client-abc", "expires-soon"]
}
```

Tags are useful for filtering and organizing large domain portfolios.

## Best Practices

1. **Check availability** before attempting registration
2. **Validate contact info** - Invalid info causes registration failures
3. **Enable auto-renewal** for critical domains
4. **Set transfer lock** when not transferring
5. **Monitor expiration dates** - Set up reminders
6. **Use tags** for portfolio organization
7. **Keep contacts updated** - Important for renewal notices
8. **Test in sandbox** before production operations

## Common Workflows

### Register a domain
1. Check availability
2. Prepare contact information
3. POST registration request
4. Monitor operation status
5. Verify nameservers

### Transfer a domain
1. Get auth code from current registrar
2. Unlock domain at current registrar
3. Initiate transfer at Gandi
4. Approve transfer email
5. Wait for transfer completion (typically 5-7 days)

### Renew expiring domains
1. List domains with expiration filter
2. Check balance/payment method
3. Renew each domain
4. Verify renewal success

## Error Handling

Common errors and solutions:

| Error | Solution |
|-------|----------|
| 400 - Invalid contact info | Verify all required fields are present and valid |
| 403 - Domain locked | Remove transfer lock before transferring |
| 404 - Domain not found | Verify domain name spelling |
| 409 - Domain unavailable | Domain already registered or reserved |
| 422 - Validation failed | Check TLD-specific requirements |

## Further Reading

- [API Overview](./api-overview.md)
- [Authentication](./authentication.md)
- [LiveDNS Management](./livedns.md)
- [Official Domain API Docs](https://api.gandi.net/docs/domains/)
- [Gandi Domain Name Documentation](https://docs.gandi.net/en/domain_names/)
