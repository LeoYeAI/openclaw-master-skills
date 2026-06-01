---
name: auth-tool-cloudbase
description: Use CloudBase Auth tool to configure and manage authentication providers for web applications - enable/disable login methods (SMS, Email, WeChat Open Platform, Google, Anonymous, Username/password, OAuth, SAML, CAS, Dingding, etc.) and configure provider settings via MCP tools `callCloudApi`.
alwaysApply: false
---

## Overview

Configure CloudBase authentication providers: Anonymous, Username/Password, SMS, Email, WeChat, Google, and more.

**Prerequisites**: CloudBase environment ID (`env`)

---


## Authentication Scenarios

### 1. Get Login Strategy

Query current login configuration:
```js
{
    "params": { "EnvId": `env` },
    "service": "lowcode",
    "action": "DescribeLoginStrategy"
}
```
Returns `LoginStrategy` object or `false` if not configured.

---

### 2. Anonymous Login

1. Get `LoginStrategy` (see Scenario 1)
2. Set `LoginStrategy.AnonymousLogin = true` (on) or `false` (off)
3. Update:
```js
{
    "params": { "EnvId": `env`, ...LoginStrategy },
    "service": "lowcode",
    "action": "ModifyLoginStrategy"
}
```

---

### 3. Username/Password Login

1. Get `LoginStrategy` (see Scenario 1)
2. Set `LoginStrategy.UserNameLogin = true` (on) or `false` (off)
3. Update:
```js
{
    "params": { "EnvId": `env`, ...LoginStrategy },
    "service": "lowcode",
    "action": "ModifyLoginStrategy"
}
```

---

### 4. SMS Login

1. Get `LoginStrategy` (see Scenario 1)
2. Modify:
   - **Turn on**: `LoginStrategy.PhoneNumberLogin = true`
   - **Turn off**: `LoginStrategy.PhoneNumberLogin = false`
   - **Config** (optional):
     ```js
     LoginStrategy.SmsVerificationConfig = {
         Type: 'default',      // 'default' or 'apis'
         Method: 'methodName',
         SmsDayLimit: 30       // -1 = unlimited
     }
     ```
3. Update:
```js
{
    "params": { "EnvId": `env`, ...LoginStrategy },
    "service": "lowcode",
    "action": "ModifyLoginStrategy"
}
```

---

### 5. Email Login

**Turn on (Tencent Cloud email)**:
```js
{
    "params": {
        "EnvId": `env`,
        "Id": "email",
        "On": "TRUE",
        "EmailConfig": { "On": "TRUE", "SmtpConfig": {} }
    },
    "service": "tcb",
    "action": "ModifyProvider"
}
```

**Turn off**:
```js
{
    "params": { "EnvId": `env`, "Id": "email", "On": "FALSE" },
    "service": "tcb",
    "action": "ModifyProvider"
}
```

**Turn on (custom SMTP)**:
```js
{
    "params": {
        "EnvId": `env`,
        "Id": "email",
        "On": "TRUE",
        "EmailConfig": {
            "On": "FALSE",
            "SmtpConfig": {
                "AccountPassword": "password",
                "AccountUsername": "username",
                "SecurityMode": "SSL",
                "SenderAddress": "sender@example.com",
                "ServerHost": "smtp.qq.com",
                "ServerPort": 465
            }
        }
    },
    "service": "tcb",
    "action": "ModifyProvider"
}
```

---

### 6. WeChat Login

1. Get WeChat config:
```js
{
    "params": { "EnvId": `env` },
    "service": "tcb",
    "action": "GetProviders"
}
```
Filter by `Id == "wx_open"`, save as `WeChatProvider`.

2. Get credentials from [WeChat Open Platform](https://open.weixin.qq.com/cgi-bin/readtemplate?t=regist/regist_tmpl):
   - `AppID`
   - `AppSecret`

3. Update:
```js
{
    "params": {
        "EnvId": `env`,
        "Id": "wx_open",
        "On": "TRUE",  // "FALSE" to disable
        "Config": {
            ...WeChatProvider.Config,
            ClientId: `AppID`,
            ClientSecret: `AppSecret`
        }
    },
    "service": "tcb",
    "action": "ModifyProvider"
}
```

---

### 7. Google Login

1. Get redirect URI:
```js
{
    "params": { "EnvId": `env` },
    "service": "lowcode",
    "action": "DescribeStaticDomain"
}
```
Save `result.Data.StaticDomain` as `staticDomain`.

2. Configure at [Google Cloud Console](https://console.cloud.google.com/apis/credentials):
   - Create OAuth 2.0 Client ID
   - Set redirect URI: `https://{staticDomain}/__auth/`
   - Get `Client ID` and `Client Secret`

3. Enable:
```js
{
    "params": {
        "EnvId": `env`,
        "ProviderType": "OAUTH",
        "Id": "google",
        "On": "TRUE",  // "FALSE" to disable
        "Name": { "Message": "Google" },
        "Description": { "Message": "" },
        "Config": {
            "ClientId": `Client ID`,
            "ClientSecret": `Client Secret`,
            "Scope": "email openid profile",
            "AuthorizationEndpoint": "https://accounts.google.com/o/oauth2/v2/auth",
            "TokenEndpoint": "https://oauth2.googleapis.com/token",
            "UserinfoEndpoint": "https://www.googleapis.com/oauth2/v3/userinfo",
            "TokenEndpointAuthMethod": "CLIENT_SECRET_BASIC",
            "RequestParametersMap": {
                "RegisterUserSyncScope": "syncEveryLogin",
                "IsGoogle": "TRUE"
            }
        },
        "Picture": "https://qcloudimg.tencent-cloud.cn/raw/f9131c00dcbcbccd5899a449d68da3ba.png",
        "TransparentMode": "FALSE",
        "ReuseUserId": "TRUE",
        "AutoSignUpWithProviderUser": "TRUE"
    },
    "service": "tcb",
    "action": "ModifyProvider"
}
```

### 8. Get Publishable Key

**Query existing key**:
```js
{
    "params": { "EnvId": `env`, "KeyType": "publish_key", "PageNumber": 1, "PageSize": 10 },
    "service": "lowcode",
    "action": "DescribeApiKeyTokens"
}
```
Return `PublishableKey.ApiKey` if exists (filter by `Name == "publish_key"`).

**Create new key** (if not exists):
```js
{
    "params": { "EnvId": `env`, "KeyType": "publish_key", "KeyName": "publish_key" },
    "service": "lowcode",
    "action": "CreateApiKeyToken"
}
```
If creation fails, direct user to: "https://tcb.cloud.tencent.com/dev?envId=`env`#/env/apikey"