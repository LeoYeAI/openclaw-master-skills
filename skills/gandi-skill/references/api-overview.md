# Gandi API Overview

General documentation for Gandi's v5 Public API.

## Introduction

Gandi provides remote RESTful APIs over HTTPS, making it easy to manage your products and build third-party applications.

**Base Endpoint:** `https://api.gandi.net/v5/`

All connections must be issued over HTTPS.

## RESTful Interface

### Stateless
Gandi's API does not maintain sessions. A request does not depend on previous requests, only its arguments. It only provides object descriptions.

### Rate Limit
- **1000 requests per minute** from the same IP address
- Exceeding this limit will result in rate limiting responses

### Content-Type Header
POST, PUT and PATCH requests must contain the following HTTP header:
```
Content-Type: application/json
```

## Sharing ID

You can pass one of your organization IDs with the `sharing_id` query string parameter for some requests.

**Purpose:**
- **GET requests:** Acts as a filter on returned data
- **POST, PATCH, PUT requests:** Indicates the organization that will pay for the ordered product

Retrieve your organization list using the [Organization API](https://api.gandi.net/docs/organization/#get-v5-organization-organizations)

## Sandbox API

A Sandbox API is available for testing:
- **URL:** https://api.sandbox.gandi.net/docs/
- Use for testing without affecting production data
- Requires separate sandbox account activation

## Available APIs

Gandi's v5 API provides the following modules:

| API | Description |
|-----|-------------|
| **Domain API** | Domain registration, renewal, transfer, management |
| **LiveDNS API** | DNS zone and record management |
| **Certificate API** | SSL/TLS certificate management |
| **Email/Mailbox API** | Email forwarding and mailbox configuration |
| **Billing API** | Billing information and history |
| **Organization API** | Organization and sharing management |
| **Web Hosting API** | Simple hosting management |
| **GandiCloud VPS API** | VPS management |
| **Template API** | Configuration template management |
| **Linked Zone API** | Linked zone management |
| **Comment API** | Product comment management |

## Response Format

All API responses follow standard HTTP status codes:

| Code | Meaning |
|------|---------|
| 200 | OK - Successful request |
| 201 | Created - Resource created successfully |
| 204 | No Content - Successful deletion |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid/missing authentication |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 422 | Unprocessable Entity - Validation failed |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

## Error Response Format

```json
{
  "cause": "Error description",
  "code": 403,
  "message": "Human-readable error message",
  "object": "resource_type"
}
```

## Best Practices

1. **Use Personal Access Tokens** - More secure and auditable than API keys
2. **Implement rate limiting** - Stay under 1000 requests/minute
3. **Handle errors gracefully** - Check status codes and parse error responses
4. **Use HTTPS only** - All API calls must use HTTPS
5. **Cache when possible** - Reduce API calls for frequently accessed data
6. **Implement retry logic** - Handle transient failures with exponential backoff
7. **Set proper Content-Type** - Always include `Content-Type: application/json` for POST/PUT/PATCH

## Further Reading

- [Authentication](./authentication.md)
- [Domain Management](./domains.md)
- [DNS Management](./livedns.md)
- [Official API Documentation](https://api.gandi.net/docs/)
