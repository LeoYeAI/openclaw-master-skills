# Authentication API

Base URL: `/api/v1/auth`

All endpoints in this group are **public** — no authentication required.

---

## POST /api/v1/auth/register

Register a new user account.

**Auth:** None

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | EmailStr | Yes | User email address |
| `password` | str | Yes | Minimum 8 characters |
| `display_name` | str \| null | No | Display name, max 100 characters |
| `locale_preference` | str | No | UI language preference. Default `"zh"` |

### Request Example

```json
{
  "email": "business@smartdata.cn",
  "password": "Str0ngP@ss2026",
  "display_name": "张明",
  "locale_preference": "zh"
}
```

### Response Example

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "business@smartdata.cn",
  "display_name": "张明",
  "avatar_url": null,
  "role": "user",
  "is_active": true,
  "is_email_verified": false,
  "kyc_status": "none",
  "locale_preference": "zh",
  "theme_preference": "system",
  "created_at": "2026-02-27T10:30:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 409 | `email_already_registered` | An account with this email already exists |
| 422 | `validation_error` | Invalid email format or password too short |

---

## POST /api/v1/auth/login

Authenticate with email and password. Returns access and refresh tokens.

**Auth:** None

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | EmailStr | Yes | Registered email address |
| `password` | str | Yes | Account password |

### Request Example

```json
{
  "email": "business@smartdata.cn",
  "password": "Str0ngP@ss2026"
}
```

### Response Example

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhMWIyYzNkNC1lNWY2LTc4OTAtYWJjZC1lZjEyMzQ1Njc4OTAiLCJleHAiOjE3MDkwMzg2MDB9.abc123",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhMWIyYzNkNC1lNWY2LTc4OTAtYWJjZC1lZjEyMzQ1Njc4OTAiLCJ0eXBlIjoicmVmcmVzaCJ9.def456",
  "token_type": "bearer"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `invalid_credentials` | Email or password is incorrect |
| 401 | `account_inactive` | Account has been deactivated |

---

## POST /api/v1/auth/login/code

Authenticate with a one-time verification code sent to email.

**Auth:** None

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | EmailStr | Yes | Registered email address |
| `code` | str | Yes | 6-character verification code |

### Request Example

```json
{
  "email": "business@smartdata.cn",
  "code": "482937"
}
```

### Response Example

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhMWIyYzNkNC1lNWY2LTc4OTAtYWJjZC1lZjEyMzQ1Njc4OTAiLCJleHAiOjE3MDkwMzg2MDB9.abc123",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhMWIyYzNkNC1lNWY2LTc4OTAtYWJjZC1lZjEyMzQ1Njc4OTAiLCJ0eXBlIjoicmVmcmVzaCJ9.def456",
  "token_type": "bearer"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `invalid_code` | Verification code is incorrect or expired |
| 404 | `user_not_found` | No account found for this email |

---

## POST /api/v1/auth/send-code

Send a one-time verification code to the given email address for passwordless login.

**Auth:** None

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | EmailStr | Yes | Email address to send code to |

### Request Example

```json
{
  "email": "business@smartdata.cn"
}
```

### Response Example

```json
{
  "message": "Verification code sent",
  "code_preview": "482937"
}
```

> `code_preview` is only returned in development mode.

### Errors

| Status | Code | Description |
|---|---|---|
| 404 | `user_not_found` | No account found for this email |
| 422 | `validation_error` | Invalid email format |

---

## POST /api/v1/auth/refresh

Exchange a valid refresh token for a new access/refresh token pair.

**Auth:** None

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `refresh_token` | str | Yes | A valid refresh token from a previous login |

### Request Example

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhMWIyYzNkNC1lNWY2LTc4OTAtYWJjZC1lZjEyMzQ1Njc4OTAiLCJ0eXBlIjoicmVmcmVzaCJ9.def456"
}
```

### Response Example

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhMWIyYzNkNC1lNWY2LTc4OTAtYWJjZC1lZjEyMzQ1Njc4OTAiLCJleHAiOjE3MDkwNDIyMDB9.ghi789",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhMWIyYzNkNC1lNWY2LTc4OTAtYWJjZC1lZjEyMzQ1Njc4OTAiLCJ0eXBlIjoicmVmcmVzaCIsInYiOjJ9.jkl012",
  "token_type": "bearer"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `invalid_refresh_token` | Refresh token is invalid, expired, or already used |

---

## POST /api/v1/auth/forgot-password

Request a password reset code. Sends a verification code to the email.

**Auth:** None

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | EmailStr | Yes | Email address of the account |

### Request Example

```json
{
  "email": "business@smartdata.cn"
}
```

### Response Example

```json
{
  "message": "Password reset code sent",
  "code_preview": "719354"
}
```

> `code_preview` is only returned in development mode.

### Errors

| Status | Code | Description |
|---|---|---|
| 404 | `user_not_found` | No account found for this email |

---

## POST /api/v1/auth/verify-reset-code

Verify a password reset code and receive a reset token. Call this between `forgot-password` and `reset-password`.

**Auth:** None

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | EmailStr | Yes | Registered email address |
| `code` | str | Yes | 6-character reset code from email |

### Request Example

```json
{
  "email": "user@example.com",
  "code": "739281"
}
```

### Response Example

**Status: 200 OK**

```json
{
  "reset_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 400 | `"Invalid or expired reset code"` | Code is wrong or expired |
| 404 | `"User not found"` | No account with that email |

---

## POST /api/v1/auth/reset-password

Reset the password using a verification code from the forgot-password flow.

**Auth:** None

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `token` | str | Yes | Reset verification code received via email |
| `new_password` | str | Yes | New password, minimum 8 characters |

### Request Example

```json
{
  "token": "719354",
  "new_password": "N3wStr0ngP@ss!"
}
```

### Response Example

```json
{
  "message": "Password reset successful"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `invalid_token` | Reset token is invalid or expired |
| 422 | `validation_error` | New password does not meet minimum requirements |
