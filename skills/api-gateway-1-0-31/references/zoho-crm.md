# Zoho CRM Routing Reference

**App name:** `zoho-crm`
**Base URL proxied:** `www.zohoapis.com`

## API Path Pattern

```
/zoho-crm/crm/v8/{resource}
```

## Common Endpoints

### Records

```bash
# List records (fields required)
GET /zoho-crm/crm/v8/{module_api_name}?fields={field1},{field2}

# Get record
GET /zoho-crm/crm/v8/{module_api_name}/{record_id}

# Create records
POST /zoho-crm/crm/v8/{module_api_name}
Content-Type: application/json

{
  "data": [
    {
      "field_api_name": "value"
    }
  ]
}

# Update records
PUT /zoho-crm/crm/v8/{module_api_name}
Content-Type: application/json

{
  "data": [
    {
      "id": "record_id",
      "field_api_name": "updated_value"
    }
  ]
}

# Delete records
DELETE /zoho-crm/crm/v8/{module_api_name}?ids={id1},{id2}
```

### Search

```bash
# Search by criteria
GET /zoho-crm/crm/v8/{module_api_name}/search?criteria=(Last_Name:equals:Smith)

# Search by email
GET /zoho-crm/crm/v8/{module_api_name}/search?email=user@example.com

# Search by phone
GET /zoho-crm/crm/v8/{module_api_name}/search?phone=555-1234

# Global text search
GET /zoho-crm/crm/v8/{module_api_name}/search?word=searchterm
```

## Available Modules

| Module | API Name | Description |
|--------|----------|-------------|
| Leads | `Leads` | Potential customers |
| Contacts | `Contacts` | Individual people |
| Accounts | `Accounts` | Organizations/companies |
| Deals | `Deals` | Sales opportunities |
| Campaigns | `Campaigns` | Marketing campaigns |
| Tasks | `Tasks` | To-do items |
| Calls | `Calls` | Phone call logs |
| Events | `Events` | Calendar appointments |
| Products | `Products` | Items for sale |

## Mandatory Fields

| Module | Required Fields |
|--------|-----------------|
| Leads | `Last_Name` |
| Contacts | `Last_Name` |
| Accounts | `Account_Name` |
| Deals | `Deal_Name`, `Stage` |
| Tasks | `Subject` |

## Search Operators

- Text: `equals`, `not_equal`, `starts_with`, `in`
- Date/Number: `equals`, `not_equal`, `greater_than`, `less_than`, `between`, `in`
- Boolean: `equals`, `not_equal`

## Notes

- The `fields` parameter is **required** for list operations (max 50 fields)
- Module API names are case-sensitive (e.g., `Leads`, not `leads`)
- Maximum 100 records per create/update/delete request
- Maximum 200 records returned per GET request
- Use `page_token` for >2,000 records (expires after 24 hours)
- Some modules require additional OAuth scopes (Tasks, Events, Calls, Products)
- Empty datasets return HTTP 204 (No Content)

## Resources

- [Zoho CRM API v8 Documentation](https://www.zoho.com/crm/developer/docs/api/v8/)
- [Get Records API](https://www.zoho.com/crm/developer/docs/api/v8/get-records.html)
- [Search Records API](https://www.zoho.com/crm/developer/docs/api/v8/search-records.html)
