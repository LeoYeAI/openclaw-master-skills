# User API

Base URL: `/api/v1/users`

All endpoints require authentication via Bearer token.

---

## GET /api/v1/users/me

Retrieve the authenticated user's profile.

**Auth:** Required (any role)

### Request Body

None.

### Request Example

```
GET /api/v1/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "business@smartdata.cn",
  "display_name": "张明",
  "avatar_url": "https://cdn.tmrland.com/avatars/a1b2c3d4.jpg",
  "role": "user",
  "is_active": true,
  "is_email_verified": true,
  "kyc_status": "verified",
  "locale_preference": "zh",
  "theme_preference": "dark",
  "created_at": "2026-02-27T10:30:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |

---

## PATCH /api/v1/users/me

Update the authenticated user's profile fields.

**Auth:** Required (any role)

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `display_name` | str \| null | No | New display name, max 100 characters |
| `avatar_url` | str \| null | No | URL to avatar image, max 500 characters |
| `locale_preference` | str \| null | No | UI language (`"zh"` or `"en"`), max 10 characters |
| `theme_preference` | str \| null | No | UI theme (`"light"`, `"dark"`, `"system"`), max 10 characters |

### Request Example

```json
{
  "display_name": "张明 (SmartData)",
  "locale_preference": "en",
  "theme_preference": "dark"
}
```

### Response Example

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "business@smartdata.cn",
  "display_name": "张明 (SmartData)",
  "avatar_url": "https://cdn.tmrland.com/avatars/a1b2c3d4.jpg",
  "role": "user",
  "is_active": true,
  "is_email_verified": true,
  "kyc_status": "verified",
  "locale_preference": "en",
  "theme_preference": "dark",
  "created_at": "2026-02-27T10:30:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 422 | `validation_error` | Field value exceeds max length or invalid format |

---

## PATCH /api/v1/users/me/password

Change the authenticated user's password.

**Auth:** Required (any role)

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `old_password` | str | Yes | Current password for verification |
| `new_password` | str | Yes | New password, minimum 8 characters |

### Request Example

```json
{
  "old_password": "Str0ngP@ss2026",
  "new_password": "Ev3nStr0ng3r!2026"
}
```

### Response Example

```json
{
  "message": "Password updated successfully"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 401 | `invalid_credentials` | Old password is incorrect |
| 422 | `validation_error` | New password does not meet minimum requirements |
