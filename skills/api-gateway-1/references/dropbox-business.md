# Dropbox Business Routing Reference

**App name:** `dropbox-business`
**Base URL proxied:** `api.dropboxapi.com`

## API Path Pattern

```
/dropbox-business/2/{endpoint}
```

**Note:** Dropbox Business API uses POST for almost all endpoints, including read operations. Request bodies should be JSON (use `null` for endpoints with no parameters).

## Common Endpoints

### Team Information

#### Get Team Info
```bash
POST /dropbox-business/2/team/get_info
Content-Type: application/json

null
```

#### Get Team Features
```bash
POST /dropbox-business/2/team/features/get_values
Content-Type: application/json

{
  "features": [{".tag": "upload_api_rate_limit"}]
}
```

### Team Members

#### List Members
```bash
POST /dropbox-business/2/team/members/list
Content-Type: application/json

{
  "limit": 100
}
```

#### Get Member Info
```bash
POST /dropbox-business/2/team/members/get_info
Content-Type: application/json

{
  "members": [{".tag": "email", "email": "user@company.com"}]
}
```

#### Add Member
```bash
POST /dropbox-business/2/team/members/add
Content-Type: application/json

{
  "new_members": [{
    "member_email": "user@company.com",
    "member_given_name": "John",
    "member_surname": "Doe"
  }]
}
```

### Groups

#### List Groups
```bash
POST /dropbox-business/2/team/groups/list
Content-Type: application/json

{
  "limit": 100
}
```

#### Create Group
```bash
POST /dropbox-business/2/team/groups/create
Content-Type: application/json

{
  "group_name": "Team Name",
  "group_management_type": {".tag": "company_managed"}
}
```

### Team Folders

#### List Team Folders
```bash
POST /dropbox-business/2/team/team_folder/list
Content-Type: application/json

{
  "limit": 100
}
```

#### Create Team Folder
```bash
POST /dropbox-business/2/team/team_folder/create
Content-Type: application/json

{
  "name": "Folder Name"
}
```

### Namespaces

#### List Namespaces
```bash
POST /dropbox-business/2/team/namespaces/list
Content-Type: application/json

{
  "limit": 100
}
```

### Devices

#### List Members' Devices
```bash
POST /dropbox-business/2/team/devices/list_members_devices
Content-Type: application/json

{}
```

### Audit Log

#### Get Events
```bash
POST /dropbox-business/2/team_log/get_events
Content-Type: application/json

{
  "limit": 100
}
```

## Notes

- All endpoints use POST method (even read operations)
- Request bodies must be JSON (use `null` for no-parameter endpoints)
- Many fields use `.tag` format for type indication
- Pagination uses `cursor` and `has_more` fields
- Requires team admin OAuth authorization

## Resources

- [Dropbox Business API Documentation](https://www.dropbox.com/developers/documentation/http/teams)
- [Team Administration Guide](https://developers.dropbox.com/dbx-team-administration-guide)
