# Attio Routing Reference

**App name:** `attio`
**Base URL proxied:** `api.attio.com`

## API Path Pattern

```
/attio/v2/{resource}
```

## Common Endpoints

### List Objects
```bash
GET /attio/v2/objects
```

### Get Object
```bash
GET /attio/v2/objects/{object}
```

### List Attributes
```bash
GET /attio/v2/objects/{object}/attributes
```

### Query Records
```bash
POST /attio/v2/objects/{object}/records/query
Content-Type: application/json

{
  "limit": 50,
  "offset": 0
}
```

### Get Record
```bash
GET /attio/v2/objects/{object}/records/{record_id}
```

### Create Record
```bash
POST /attio/v2/objects/{object}/records
Content-Type: application/json

{
  "data": {
    "values": {
      "name": [{"first_name": "John", "last_name": "Doe", "full_name": "John Doe"}],
      "email_addresses": ["john@example.com"]
    }
  }
}
```

### Update Record
```bash
PATCH /attio/v2/objects/{object}/records/{record_id}
Content-Type: application/json

{
  "data": {
    "values": {
      "job_title": "Engineer"
    }
  }
}
```

### Delete Record
```bash
DELETE /attio/v2/objects/{object}/records/{record_id}
```

### List Tasks
```bash
GET /attio/v2/tasks?limit=50
```

### Create Task
```bash
POST /attio/v2/tasks
Content-Type: application/json

{
  "data": {
    "content": "Task description",
    "format": "plaintext",
    "assignees": [],
    "linked_records": []
  }
}
```

### List Workspace Members
```bash
GET /attio/v2/workspace_members
```

### Identify Self
```bash
GET /attio/v2/self
```

## Notes

- Object slugs are lowercase snake_case (e.g., `people`, `companies`)
- Record IDs are UUIDs
- For personal-name attributes, include `full_name` when creating records
- Task creation requires `format` and `assignees` fields
- Rate limits: 100 read/sec, 25 write/sec
- Pagination uses `limit` and `offset` parameters

## Resources

- [Attio API Overview](https://docs.attio.com/rest-api/overview)
- [Attio API Reference](https://docs.attio.com/rest-api/endpoint-reference)
- [Records API](https://docs.attio.com/rest-api/endpoint-reference/records)
