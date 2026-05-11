# SPACE ID API Reference

## Overview

Decentralized universal name service for BNB Chain `.bnb` domains.

**Base endpoint:**
```
https://open-platform.nodereal.io/{apiKey}/spaceid/domain
```

> **Note:** Use your BSC app API key. The API key is obtained from the MegaNode BSC app.

---

## byOwners -- Retrieve names by owner address

```
POST https://open-platform.nodereal.io/{apiKey}/spaceid/domain/names/byOwners
```

**Request body:**
```json
["0x159bc0357b89301dbfb110bee5e05c42c9db3798"]
```

**Response example:**
```json
{
  "0x159BC0357B89301dbFb110Bee5e05C42C9dB3798": [
    {
      "nodeHash": "0xdb99baace34eab2e2213adcc9940080fdb70bfaa15abdbf28fc61fca28da1b14",
      "bind": "0x159bc0357b89301dbfb110bee5e05c42c9db3798",
      "name": "defichad",
      "expires": "2023-08-24T20:36:26Z"
    },
    {
      "nodeHash": "0xb492a756f29f6030e974b3fda71b255bd20c61e23e3977321d4a895833631628",
      "bind": "0x159bc0357b89301dbfb110bee5e05c42c9db3798",
      "name": "michaelsaylor",
      "expires": "2023-08-24T20:35:59Z"
    }
  ]
}
```

---

## byBinds -- Retrieve names bound to an address

```
POST https://open-platform.nodereal.io/{apiKey}/spaceid/domain/names/byBinds
```

**Request body:**
```json
["0x159bc0357b89301dbfb110bee5e05c42c9db3798"]
```

**Response example:**
```json
{
  "0x159BC0357B89301dbFb110Bee5e05C42C9dB3798": [
    "defichad",
    "michaelsaylor",
    "win"
  ]
}
```

> **Note:** The owner can bind a name to a different address. `byOwners` returns names the address owns; `byBinds` returns names bound to (pointing at) the address.

---

## byNames -- Retrieve address by name

```
POST https://open-platform.nodereal.io/{apiKey}/spaceid/domain/binds/byNames
```

**Request body:**
```json
["win"]
```

**Response example:**
```json
{
  "win": {
    "nodeHash": "0x5431389acdea9db45b4d758954f139eb4d947c4e6293843b51ea0dbcd720620a",
    "bind": "0x159bc0357b89301dbfb110bee5e05c42c9db3798",
    "name": "win",
    "expires": "2023-08-24T20:38:29Z"
  }
}
```

> **Note:** Domain names are passed without the `.bnb` suffix. Add `.bnb` to get the full domain name.

---
