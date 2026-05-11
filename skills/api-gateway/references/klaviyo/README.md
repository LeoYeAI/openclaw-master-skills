# Klaviyo Routing Reference

**App name:** `klaviyo`
**Base URL proxied:** `a.klaviyo.com`

## API Path Pattern

```
/klaviyo/api/{resource}
```

## API Versioning

Include the `revision` header in all requests:

```
revision: 2024-10-15
```

## Common Endpoints

### Get Profiles
```bash
GET /klaviyo/api/profiles
```

Query parameters:
- `filter` - Filter profiles (e.g., `filter=equals(email,"test@example.com")`)
- `fields[profile]` - Comma-separated list of fields to include
- `page[size]` - Number of results per page (max 100)

### Get a Profile
```bash
GET /klaviyo/api/profiles/{profile_id}
```

### Create a Profile
```bash
POST /klaviyo/api/profiles
Content-Type: application/json

{
  "data": {
    "type": "profile",
    "attributes": {
      "email": "newuser@example.com",
      "first_name": "John",
      "last_name": "Doe"
    }
  }
}
```

### Update a Profile
```bash
PATCH /klaviyo/api/profiles/{profile_id}
Content-Type: application/json

{
  "data": {
    "type": "profile",
    "id": "PROFILE_ID",
    "attributes": {
      "first_name": "Jane"
    }
  }
}
```

### Get Lists
```bash
GET /klaviyo/api/lists
```

### Create a List
```bash
POST /klaviyo/api/lists
Content-Type: application/json

{
  "data": {
    "type": "list",
    "attributes": {
      "name": "VIP Customers"
    }
  }
}
```

### Add Profiles to List
```bash
POST /klaviyo/api/lists/{list_id}/relationships/profiles
Content-Type: application/json

{
  "data": [
    {"type": "profile", "id": "PROFILE_ID"}
  ]
}
```

### Get Segments
```bash
GET /klaviyo/api/segments
```

### Get Campaigns
```bash
GET /klaviyo/api/campaigns
```

### Create a Campaign
```bash
POST /klaviyo/api/campaigns
Content-Type: application/json

{
  "data": {
    "type": "campaign",
    "attributes": {
      "name": "Summer Newsletter",
      "audiences": {
        "included": ["LIST_ID"]
      }
    }
  }
}
```

### Get Flows
```bash
GET /klaviyo/api/flows
```

### Update Flow Status
```bash
PATCH /klaviyo/api/flows/{flow_id}
Content-Type: application/json

{
  "data": {
    "type": "flow",
    "id": "FLOW_ID",
    "attributes": {
      "status": "live"
    }
  }
}
```

### Create an Event
```bash
POST /klaviyo/api/events
Content-Type: application/json

{
  "data": {
    "type": "event",
    "attributes": {
      "profile": {
        "data": {
          "type": "profile",
          "attributes": {
            "email": "customer@example.com"
          }
        }
      },
      "metric": {
        "data": {
          "type": "metric",
          "attributes": {
            "name": "Viewed Product"
          }
        }
      },
      "properties": {
        "product_id": "SKU123",
        "product_name": "Blue T-Shirt"
      }
    }
  }
}
```

### Get Metrics
```bash
GET /klaviyo/api/metrics
```

### Get Templates
```bash
GET /klaviyo/api/templates
```

### Create Webhook
```bash
POST /klaviyo/api/webhooks
Content-Type: application/json

{
  "data": {
    "type": "webhook",
    "attributes": {
      "name": "Order Placed Webhook",
      "endpoint_url": "https://example.com/webhooks/klaviyo",
      "enabled": true
    },
    "relationships": {
      "webhook-topics": {
        "data": [
          {"type": "webhook-topic", "id": "campaign:sent"}
        ]
      }
    }
  }
}
```

### Delete Webhook
```bash
DELETE /klaviyo/api/webhooks/{webhook_id}
```

## Notes

- All requests use JSON:API specification
- Timestamps are in ISO 8601 RFC 3339 format
- Resource IDs are strings (often base64-encoded)
- Use sparse fieldsets to optimize response size (e.g., `fields[profile]=email,first_name`)
- Include `revision` header for API versioning
- Use cursor-based pagination with `page[cursor]` parameter

## Resources

- [Klaviyo API Documentation](https://developers.klaviyo.com)
- [API Reference](https://developers.klaviyo.com/en/reference/api_overview)
- [Klaviyo Developer Portal](https://developers.klaviyo.com/en)
