---
name: mantis-manager
description: Manage Mantis Bug Tracker (issues, projects, users, filters, configs) via the official Mantis REST API. Supports full CRUD operations on issues, projects, users, attachments, notes, tags, relationships, and configuration management. Features dynamic instance switching with context-aware base URL and token resolution.
homepage: https://www.mantisbt.org/
metadata: {"openclaw":{"emoji":"🐞","requires":{"env":["MANTIS_BASE_URL","MANTIS_API_TOKEN"]},"primaryEnv":"MANTIS_API_TOKEN"}}
---

# Mantis Manager Skill (Enhanced)

## 🔐 Base URL & Token Resolution

### Base URL Resolution
Base URL precedence (highest to lowest):
1. `temporary_base_url` — one-time use URL for specific operations
2. `user_base_url` — user-defined URL for the current session
3. `MANTIS_BASE_URL` — environment default URL

This allows you to:
- Switch between multiple Mantis instances dynamically
- Test against staging/production environments
- Work with different client instances without changing config

**Example:**
```
// Default: uses MANTIS_BASE_URL from environment
GET {{resolved_base_url}}/issues

// Override for one operation:
temporary_base_url = "https://mantis-staging.example.com/api/rest"
GET {{resolved_base_url}}/issues

// Override for session:
user_base_url = "https://client-mantis.example.com/api/rest"
GET {{resolved_base_url}}/issues
```

### Token Resolution
Token precedence (highest to lowest):
1. `temporary_token` — one-time use token for specific operations
2. `user_token` — user-defined token for the current session
3. `MANTIS_API_TOKEN` — environment default token

Environment variables are handled via standard OpenClaw metadata: `requires.env` declares **required** variables (`MANTIS_BASE_URL`, `MANTIS_API_TOKEN`). Any other environment variables you use for Mantis should be treated as normal process env vars and are not modeled as special OpenClaw metadata fields.

### Authentication Headers
**All API requests must include:**

```
Authorization: Bearer {{resolved_token}}
Content-Type: application/json
```

**Note:** The `{{resolved_base_url}}` and `{{resolved_token}}` are determined at runtime based on the precedence rules above.

---

## 📌 Notation Used in Examples

Throughout this documentation:
- `{{MANTIS_BASE_URL}}` refers to the **resolved base URL** (could be temporary_base_url, user_base_url, or env MANTIS_BASE_URL)
- `{{resolved_token}}` refers to the **resolved token** (could be temporary_token, user_token, or env MANTIS_API_TOKEN)
- All endpoints use the pattern: `{{MANTIS_BASE_URL}}/resource/path`

**Important:** Always use the resolution logic to determine the actual URL and token at runtime.

---

## 🔄 Context Management

> The `temporary_*` and `user_*` names here are **runtime context variables used by the skill logic**, not OpenClaw metadata fields. OpenClaw does **not** define an `optional.context` metadata key; context is resolved dynamically at runtime as described below.

### Setting Temporary Values (One-Time Use)

**User queries:**
- "Use https://staging.mantis.com/api/rest for this request"
- "Connect to production instance for this operation"
- "Use token ABC123 just this once"

**Action:**
```
Set temporary_base_url = "https://staging.mantis.com/api/rest"
Set temporary_token = "ABC123"
... perform operation ...
Clear temporary_base_url
Clear temporary_token
```

**Behavior:** Temporary values are automatically cleared after one use.

### Setting Session Values (Current Session)

**User queries:**
- "Switch to client XYZ's Mantis instance"
- "Use my personal API token for all requests"
- "Connect to staging environment"

**Action:**
```
Set user_base_url = "https://client-xyz.mantis.com/api/rest"
Set user_token = "personal_token_123"
... perform multiple operations ...
// Values persist for the entire session
```

**Behavior:** Session values persist until explicitly cleared or session ends.

### Clearing Context Values

**User queries:**
- "Reset to default Mantis instance"
- "Clear my custom token"
- "Go back to environment defaults"

**Action:**
```
Clear user_base_url
Clear user_token
// Now uses MANTIS_BASE_URL and MANTIS_API_TOKEN from environment
```

### Viewing Current Context

**User queries:**
- "What Mantis instance am I connected to?"
- "Show current API configuration"
- "Which token am I using?"

**Response should show:**
```
Current Context:
- Base URL: https://client-xyz.mantis.com/api/rest (user_base_url)
- Token: user_t***123 (user_token)
- Fallback Base URL: https://default.mantis.com/api/rest (MANTIS_BASE_URL)
- Fallback Token: env_t***789 (MANTIS_API_TOKEN)
```

### Use Cases

#### Multi-Instance Management
```
// Check production issue
Set temporary_base_url = "https://prod.mantis.com/api/rest"
Get issue 123

// Check staging issue  
Set temporary_base_url = "https://staging.mantis.com/api/rest"
Get issue 123

// Compare results
```

#### Client Switching
```
// Switch to Client A
Set user_base_url = "https://clienta.mantis.com/api/rest"
Set user_token = "clienta_token"
List all projects
Get issues for project 5

// Switch to Client B
Set user_base_url = "https://clientb.mantis.com/api/rest"
Set user_token = "clientb_token"
List all projects
Get issues for project 3
```

#### Admin Operations with Impersonation
```
// Connect to main instance as admin
Set user_token = "admin_token"

// Perform operation as specific user
Set temporary header: X-Impersonate-User = "john.doe"
Get user issues

// Back to admin
Clear temporary header
```

---

## 🐞 ISSUES Operations

### List Issues
**User queries:**
- "List all issues"
- "Get issues for project 5"
- "Get issues matching filter 10"
- "Show issues assigned to me"
- "Get unassigned issues"

**Actions:**
```
GET {{MANTIS_BASE_URL}}/issues
```

**Query Parameters:**
- `page_size` — number of issues per page (default: 50)
- `page` — page number (1-indexed)
- `filter_id` — ID of saved filter to apply
- `project_id` — filter by specific project
- `select` — comma-separated fields to return (e.g., "id,summary,status")

**Special endpoints:**
```
GET {{MANTIS_BASE_URL}}/issues?filter_id={{filter_id}}
GET {{MANTIS_BASE_URL}}/projects/{{project_id}}/issues
```

### Get Single Issue
**User queries:**
- "Show issue 123"
- "Get details for bug 456"

**Action:**
```
GET {{MANTIS_BASE_URL}}/issues/{{id}}
```

### Create Issue
**User queries:**
- "Create issue with summary 'Login bug' and description 'Cannot login'"
- "Create bug in project 5 with priority high"
- "Create issue with attachments"

**Action:**
```
POST {{MANTIS_BASE_URL}}/issues
```

**Minimal body:**
```json
{
  "summary": "Issue summary",
  "description": "Detailed description",
  "category": {"name": "General"},
  "project": {"id": 1}
}
```

**Full body (optional fields):**
```json
{
  "summary": "Issue summary",
  "description": "Detailed description",
  "steps_to_reproduce": "1. Do this\n2. Do that",
  "additional_information": "Extra info",
  "category": {"id": 1, "name": "General"},
  "project": {"id": 1},
  "priority": {"id": 30, "name": "normal"},
  "severity": {"id": 50, "name": "minor"},
  "status": {"id": 10, "name": "new"},
  "reproducibility": {"id": 10, "name": "always"},
  "handler": {"id": 5},
  "tags": [{"name": "bug"}, {"name": "ui"}],
  "custom_fields": [{"field": {"id": 1}, "value": "custom value"}],
  "due_date": "2026-12-31T23:59:59+00:00",
  "version": {"name": "1.0"},
  "target_version": {"name": "2.0"}
}
```

**Create with attachments:**
```
POST {{MANTIS_BASE_URL}}/issues
```
Include `files` array in body with base64-encoded content.

### Update Issue
**User queries:**
- "Update issue 123 status to resolved"
- "Change priority of bug 456 to high"
- "Assign issue 789 to user 10"

**Action:**
```
PATCH {{MANTIS_BASE_URL}}/issues/{{id}}
```

**Example body:**
```json
{
  "status": {"name": "resolved"},
  "handler": {"id": 10},
  "priority": {"name": "high"},
  "summary": "Updated summary"
}
```

### Delete Issue
**User queries:**
- "Delete issue 123"
- "Remove bug 456"

**Action:**
```
DELETE {{MANTIS_BASE_URL}}/issues/{{id}}
```

### Monitor/Unmonitor Issue
**User queries:**
- "Monitor issue 123"
- "Stop monitoring bug 456"
- "Add user 10 as monitor on issue 789"

**Actions:**
```
POST   {{MANTIS_BASE_URL}}/issues/{{id}}/monitors
DELETE {{MANTIS_BASE_URL}}/issues/{{id}}/monitors
```

**Body (for specific user):**
```json
{
  "user": {"id": 10}
}
```

### Attach/Detach Tags
**User queries:**
- "Add tag 'critical' to issue 123"
- "Remove tag 'bug' from issue 456"

**Actions:**
```
POST   {{MANTIS_BASE_URL}}/issues/{{id}}/tags
PATCH  {{MANTIS_BASE_URL}}/issues/{{id}}/tags
DELETE {{MANTIS_BASE_URL}}/issues/{{id}}/tags
```

**Body:**
```json
{
  "tags": [
    {"name": "bug"},
    {"name": "critical"}
  ]
}
```

### Add Issue Relationship
**User queries:**
- "Link issue 123 to issue 456 as duplicate"
- "Add parent relationship from 789 to 101"

**Action:**
```
POST {{MANTIS_BASE_URL}}/issues/{{id}}/relationships
```

**Body:**
```json
{
  "type": {"name": "duplicate-of"},
  "target_issue": {"id": 456}
}
```

**Relationship types:**
- `duplicate-of`
- `related-to`
- `parent-of`
- `child-of`
- `has-duplicate`

### Attach Files
**User queries:**
- "Attach file to issue 123"
- "Add screenshot to bug 456"

**Action:**
```
POST {{MANTIS_BASE_URL}}/issues/{{id}}/files
```

**Body:**
```json
{
  "files": [
    {
      "name": "screenshot.png",
      "content": "base64_encoded_content_here"
    }
  ]
}
```

### Delete Attachment
**User queries:**
- "Delete attachment 789 from issue 123"
- "Remove file 101 from bug 456"

**Action:**
```
DELETE {{MANTIS_BASE_URL}}/issues/{{issue_id}}/files/{{file_id}}
```

### Issue Notes

#### Add Note
**User queries:**
- "Add note to issue 123: 'This is fixed now'"
- "Add note with time tracking 2 hours"
- "Add private note to bug 456"

**Action:**
```
POST {{MANTIS_BASE_URL}}/issues/{{id}}/notes
```

**Body:**
```json
{
  "text": "Note content here",
  "view_state": {"name": "public"},
  "time_tracking": "PT2H30M"
}
```

**With attachment:**
```json
{
  "text": "Note with file",
  "files": [
    {
      "name": "log.txt",
      "content": "base64_content"
    }
  ]
}
```

#### Delete Note
**User queries:**
- "Delete note 55 from issue 123"
- "Remove comment 99 from bug 456"

**Action:**
```
DELETE {{MANTIS_BASE_URL}}/issues/{{issue_id}}/notes/{{note_id}}
```

---

## 📁 PROJECTS Operations

### List All Projects
**User queries:**
- "List all projects"
- "Show all projects"
- "Get projects"

**Action:**
```
GET {{MANTIS_BASE_URL}}/projects
```

### Get Project by ID
**User queries:**
- "Show project 5"
- "Get details for project 10"

**Action:**
```
GET {{MANTIS_BASE_URL}}/projects/{{id}}
```

### Create Project
**User queries:**
- "Create project named 'New Product'"
- "Add project with description 'Internal tools'"

**Action:**
```
POST {{MANTIS_BASE_URL}}/projects
```

**Body:**
```json
{
  "name": "Project Name",
  "description": "Project description",
  "enabled": true,
  "inherit_global": true,
  "view_state": {"name": "public"},
  "status": {"name": "development"}
}
```

### Update Project
**User queries:**
- "Update project 5 description"
- "Change project 10 status to stable"

**Action:**
```
PATCH {{MANTIS_BASE_URL}}/projects/{{id}}
```

### Delete Project
**User queries:**
- "Delete project 5"
- "Remove project 10"

**Action:**
```
DELETE {{MANTIS_BASE_URL}}/projects/{{id}}
```

### Sub-Projects

#### Get Sub-Projects
**User queries:**
- "Show sub-projects of project 5"

**Action:**
```
GET {{MANTIS_BASE_URL}}/projects/{{id}}/subprojects
```

#### Create Sub-Project
**User queries:**
- "Create sub-project under project 5"

**Action:**
```
POST {{MANTIS_BASE_URL}}/projects/{{id}}/subprojects
```

**Body:**
```json
{
  "subproject": {"id": 10}
}
```

#### Delete Sub-Project
**Action:**
```
DELETE {{MANTIS_BASE_URL}}/projects/{{id}}/subprojects/{{subproject_id}}
```

### Project Users

#### Get Project Users
**User queries:**
- "Show users in project 5"
- "List members of project 10"

**Action:**
```
GET {{MANTIS_BASE_URL}}/projects/{{id}}/users
```

#### Add User to Project
**User queries:**
- "Add user 20 to project 5 as developer"

**Action:**
```
POST {{MANTIS_BASE_URL}}/projects/{{id}}/users
```

**Body:**
```json
{
  "user": {"id": 20},
  "access_level": {"name": "developer"}
}
```

**Access levels:**
- `viewer` (10)
- `reporter` (25)
- `updater` (40)
- `developer` (55)
- `manager` (70)
- `administrator` (90)

#### Delete User from Project
**Action:**
```
DELETE {{MANTIS_BASE_URL}}/projects/{{project_id}}/users/{{user_id}}
```

### Project Versions

#### Get Versions
**User queries:**
- "Show versions of project 5"
- "List releases for project 10"

**Action:**
```
GET {{MANTIS_BASE_URL}}/projects/{{id}}/versions
```

#### Create Version
**User queries:**
- "Create version 2.0 for project 5"
- "Add release 1.5 to project 10"

**Action:**
```
POST {{MANTIS_BASE_URL}}/projects/{{id}}/versions
```

**Body:**
```json
{
  "name": "2.0",
  "description": "Major release",
  "released": true,
  "obsolete": false,
  "timestamp": "2026-06-01T00:00:00+00:00"
}
```

#### Update Version
**Action:**
```
PATCH {{MANTIS_BASE_URL}}/projects/{{project_id}}/versions/{{version_id}}
```

#### Delete Version
**Action:**
```
DELETE {{MANTIS_BASE_URL}}/projects/{{project_id}}/versions/{{version_id}}
```

---

## 👥 USERS Operations

### Get My User Info
**User queries:**
- "Show my user info"
- "Get my profile"
- "Who am I?"

**Action:**
```
GET {{MANTIS_BASE_URL}}/users/me
```

### Get User by ID
**User queries:**
- "Show user 10"
- "Get info for user 25"

**Action:**
```
GET {{MANTIS_BASE_URL}}/users/{{id}}
```

### Get User by Username
**User queries:**
- "Find user 'john.doe'"
- "Get user with username 'admin'"

**Action:**
```
GET {{MANTIS_BASE_URL}}/users?name={{username}}
```

### Create User
**User queries:**
- "Create user 'jane.smith' with email 'jane@example.com'"
- "Add new user"

**Action:**
```
POST {{MANTIS_BASE_URL}}/users
```

**Minimal body:**
```json
{
  "username": "jane.smith",
  "email": "jane@example.com",
  "access_level": {"name": "reporter"}
}
```

**Full body:**
```json
{
  "username": "jane.smith",
  "password": "SecurePass123!",
  "real_name": "Jane Smith",
  "email": "jane@example.com",
  "access_level": {"name": "developer"},
  "enabled": true,
  "protected": false
}
```

### Update User
**User queries:**
- "Update user 10 email to 'new@example.com'"
- "Change user 25 access level to developer"

**Action:**
```
PATCH {{MANTIS_BASE_URL}}/users/{{id}}
```

**Body:**
```json
{
  "real_name": "Updated Name",
  "email": "new@example.com",
  "access_level": {"name": "developer"},
  "enabled": false
}
```

### Reset User Password
**User queries:**
- "Reset password for user 10"

**Action:**
```
PUT {{MANTIS_BASE_URL}}/users/{{id}}/reset-password
```

**Body:**
```json
{
  "password": "NewSecurePassword123!"
}
```

### Delete User
**User queries:**
- "Delete user 10"
- "Remove user 'john.doe'"

**Action:**
```
DELETE {{MANTIS_BASE_URL}}/users/{{id}}
```

---

## 🔍 FILTERS Operations

### Get All Filters
**User queries:**
- "List all filters"
- "Show my saved filters"

**Action:**
```
GET {{MANTIS_BASE_URL}}/filters
```

### Get Filter by ID
**User queries:**
- "Show filter 5"
- "Get details for filter 10"

**Action:**
```
GET {{MANTIS_BASE_URL}}/filters/{{id}}
```

### Delete Filter
**User queries:**
- "Delete filter 5"
- "Remove saved filter 10"

**Action:**
```
DELETE {{MANTIS_BASE_URL}}/filters/{{id}}
```

---

## 🔐 TOKEN MANAGEMENT

### Create Token for Self
**User queries:**
- "Create my API token"
- "Generate token for me"
- "Create new token named 'automation'"

**Action:**
```
POST {{MANTIS_BASE_URL}}/user_tokens
```

**Body:**
```json
{
  "name": "automation_token",
  "date_expiry": "2027-12-31T23:59:59+00:00"
}
```

### Delete Token for Self
**User queries:**
- "Delete my token"
- "Revoke my API token"

**Action:**
```
DELETE {{MANTIS_BASE_URL}}/user_tokens/{{token_id}}
```

### Create Token for Another User
**User queries:**
- "Create token for user 10"
- "Generate API token for user 'john.doe'"

**Action:**
```
POST {{MANTIS_BASE_URL}}/users/{{user_id}}/tokens
```

**Body:**
```json
{
  "name": "user_token",
  "date_expiry": "2027-12-31T23:59:59+00:00"
}
```

### Delete Token for Another User
**Action:**
```
DELETE {{MANTIS_BASE_URL}}/users/{{user_id}}/tokens/{{token_id}}
```

---

## ⚙️ CONFIG Operations

### Get Single Configuration Option
**User queries:**
- "Get config option 'bug_report_page_fields'"
- "Show configuration for 'default_category_for_moves'"

**Action:**
```
GET {{MANTIS_BASE_URL}}/config/{{option}}
```

### Get Multiple Configuration Options
**User queries:**
- "Get configs for project 5"
- "Show all config options"

**Action:**
```
GET {{MANTIS_BASE_URL}}/config
```

**Query parameters:**
- `option` — specific option name
- `project_id` — filter by project
- `user_id` — filter by user

### Set Configuration Option
**User queries:**
- "Set config 'allow_signup' to true"
- "Update config option"

**Action:**
```
PATCH {{MANTIS_BASE_URL}}/config
```

**Body:**
```json
{
  "configs": [
    {
      "option": "allow_signup",
      "value": "1"
    }
  ]
}
```

---

## 🌍 LOCALIZATION Operations

### Get Localized String
**User queries:**
- "Get localized string 'status_new'"
- "Translate 'priority_high' to French"

**Action:**
```
GET {{MANTIS_BASE_URL}}/lang/{{string}}
```

**Query parameter:**
- `language` — language code (e.g., 'fr', 'en', 'de')

### Get Multiple Localized Strings
**User queries:**
- "Get all status translations"
- "Get localized strings for priorities"

**Action:**
```
GET {{MANTIS_BASE_URL}}/lang
```

**Query parameters:**
- `strings` — comma-separated list of string keys
- `language` — language code

---

## 🔒 IMPERSONATION

### Get User Info with Impersonation
**User queries:**
- "Impersonate user 10 and get their info"
- "Get info as user 'john.doe'"

**Action:**
```
GET {{MANTIS_BASE_URL}}/users/me
```

**Header:**
```
X-Impersonate-User: {{username_or_id}}
```

---

## ⚠️ Error Handling

Handle HTTP errors gracefully:

**401 Unauthorized:**
- Token is invalid or expired
- Action: Inform user to check `MANTIS_API_TOKEN` or provide valid `temporary_token`

**403 Forbidden:**
- User doesn't have permission for this operation
- Action: Inform user about insufficient permissions

**404 Not Found:**
- Resource (issue, project, user, etc.) doesn't exist
- Action: Inform user that the requested resource was not found

**422 Unprocessable Entity:**
- Validation error in request body
- Action: Show validation errors from response and guide user

**500 Internal Server Error:**
- Server-side error
- Action: Inform user of server error and suggest retrying later

**General error response format:**
```json
{
  "message": "Error description",
  "code": 1234,
  "localized": "Localized error message"
}
```

---

## 📋 Best Practices

### Pagination
- Always support `page_size` and `page` parameters for list operations
- Default page size: 50
- Inform user when results are paginated

### Field Selection
- Use `select` parameter to return only needed fields
- Example: `select=id,summary,status,priority`
- Reduces bandwidth and improves performance

### Filtering
- Use `filter_id` to apply saved filters
- Combine with pagination for large datasets
- Consider project-specific filtering with `project_id`

### Attachments
- Files must be base64-encoded
- Include filename and content in request
- Verify file size limits (check Mantis config)

### Time Tracking
- Use ISO 8601 duration format: `PT2H30M` (2 hours 30 minutes)
- Can be added to notes for time tracking

### Date Formats
- Use ISO 8601: `2026-12-31T23:59:59+00:00`
- Include timezone for accuracy

### Custom Fields
- Check project configuration for available custom fields
- Reference by field ID in requests

### Relationships
- Verify relationship types supported by your Mantis version
- Some relationships auto-create reciprocal links

---

## 🚀 Quick Examples

### Create and Monitor Issue
```
1. POST /issues with summary and description
2. POST /issues/{{new_id}}/monitors to monitor
```

### Assign Issue and Add Note
```
1. PATCH /issues/{{id}} with handler
2. POST /issues/{{id}}/notes with assignment comment
```

### Create Project with Version
```
1. POST /projects with project details
2. POST /projects/{{id}}/versions with version info
```

### User Management Flow
```
1. POST /users to create user
2. POST /projects/{{id}}/users to add to project
3. POST /users/{{id}}/tokens to create API token
```

---

## 🎯 Advanced Use Cases

### Bulk Issue Updates
When updating multiple issues:
- Loop through issue IDs
- Use PATCH for each issue
- Collect results and report summary

### Filter-Based Operations
Get all high-priority bugs:
```
1. GET /filters to find priority filter ID
2. GET /issues?filter_id={{filter_id}}&page_size=100
3. Process paginated results
```

### Project Migration
Copy project structure:
```
1. GET /projects/{{source_id}} to get project details
2. GET /projects/{{source_id}}/versions for versions
3. POST /projects to create new project
4. POST /projects/{{new_id}}/versions for each version
```

### User Audit
Track user activity:
```
1. GET /issues?reporter_id={{user_id}}
2. GET /issues?handler_id={{user_id}}
3. GET /issues?monitor_id={{user_id}}
4. Compile activity report
```

### Multi-Instance Management
Work with multiple Mantis instances:
```
// Scenario: Compare issue status across environments

1. Check production:
   Set temporary_base_url = "https://prod.mantis.com/api/rest"
   Set temporary_token = "prod_token"
   GET /issues/123
   Record status

2. Check staging:
   Set temporary_base_url = "https://staging.mantis.com/api/rest"
   Set temporary_token = "staging_token"
   GET /issues/123
   Record status

3. Compare and report differences
```

### Cross-Instance Synchronization
Sync data between instances:
```
// Scenario: Clone project from one instance to another

1. Connect to source instance:
   Set user_base_url = "https://source.mantis.com/api/rest"
   Set user_token = "source_token"
   GET /projects/5 (get project details)
   GET /projects/5/versions (get versions)
   GET /projects/5/users (get users)

2. Connect to target instance:
   Set user_base_url = "https://target.mantis.com/api/rest"
   Set user_token = "target_token"
   POST /projects (create project)
   POST /projects/{{new_id}}/versions (create versions)
   POST /projects/{{new_id}}/users (add users)

3. Report sync results
```

### Client-Specific Operations
Manage multiple client instances:
```
// Scenario: Daily status report for all clients

For each client in [ClientA, ClientB, ClientC]:
  1. Set user_base_url = client.mantis_url
  2. Set user_token = client.api_token
  3. GET /issues?filter_id=1 (get today's issues)
  4. Collect statistics
  5. Clear context

Generate consolidated report
```

---

## 📚 Resources

- **Mantis API Documentation**: Check your Mantis instance at `{{MANTIS_BASE_URL}}/api/rest/swagger.yaml`
- **Issue Statuses**: new, feedback, acknowledged, confirmed, assigned, resolved, closed
- **Priorities**: none, low, normal, high, urgent, immediate
- **Severities**: feature, trivial, text, tweak, minor, major, crash, block
- **Access Levels**: 10=viewer, 25=reporter, 40=updater, 55=developer, 70=manager, 90=administrator

---

## ✅ Skill Capabilities Summary

This skill enables you to:

### Core Operations
- ✅ Full CRUD operations on issues
- ✅ Manage issue relationships, tags, monitors
- ✅ Add notes with time tracking and attachments
- ✅ Full project management (create, update, delete)
- ✅ Manage sub-projects, versions, and project users
- ✅ User management (CRUD, password reset)
- ✅ API token management (create, delete for self and others)
- ✅ Filter management and filtered queries
- ✅ Configuration management
- ✅ Localization support
- ✅ Impersonation capabilities

### Advanced Features
- ✅ **Dynamic instance switching** — Switch between multiple Mantis instances on-the-fly
- ✅ **Context-aware URL resolution** — temporary_base_url → user_base_url → MANTIS_BASE_URL
- ✅ **Context-aware token resolution** — temporary_token → user_token → MANTIS_API_TOKEN
- ✅ **Multi-instance management** — Manage multiple clients/environments simultaneously
- ✅ **Cross-instance operations** — Compare, sync, and migrate data between instances
- ✅ Comprehensive error handling
- ✅ Pagination and field selection
- ✅ Advanced workflows and bulk operations
