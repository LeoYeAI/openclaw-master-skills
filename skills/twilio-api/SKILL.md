---
name: twilio
description: |
  Twilio API integration with managed OAuth. SMS, voice calls, phone numbers, and communications.
  Use this skill when users want to send SMS messages, make voice calls, manage phone numbers, or work with Twilio resources.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
  Requires network access and valid Maton API key.
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji: 🧠
    requires:
      env:
        - MATON_API_KEY
---

# Twilio

Access the Twilio API with managed OAuth authentication. Send SMS messages, make voice calls, manage phone numbers, and work with Twilio resources.

## Quick Start

```bash
# List all accounts
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/twilio/2010-04-01/Accounts.json')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/twilio/2010-04-01/Accounts/{AccountSid}/{resource}.json
```

The gateway proxies requests to `api.twilio.com` and automatically injects your OAuth token.

**Important:** Most Twilio endpoints require your Account SID in the path. You can get your Account SID from the `/Accounts.json` endpoint.

## Authentication

All requests require the Maton API key in the Authorization header:

```
Authorization: Bearer $MATON_API_KEY
```

**Environment Variable:** Set your API key as `MATON_API_KEY`:

```bash
export MATON_API_KEY="YOUR_API_KEY"
```

### Getting Your API Key

1. Sign in or create an account at [maton.ai](https://maton.ai)
2. Go to [maton.ai/settings](https://maton.ai/settings)
3. Copy your API key

## Connection Management

Manage your Twilio OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=twilio&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'twilio'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Get Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "connection": {
    "connection_id": "ebe566b1-3eaf-4926-bc92-0d8d47445f12",
    "status": "ACTIVE",
    "creation_time": "2026-02-09T23:18:44.243582Z",
    "last_updated_time": "2026-02-09T23:19:55.176687Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "twilio",
    "metadata": {}
  }
}
```

Open the returned `url` in a browser to complete OAuth authorization.

### Delete Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Specifying Connection

If you have multiple Twilio connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/twilio/2010-04-01/Accounts.json')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', 'ebe566b1-3eaf-4926-bc92-0d8d47445f12')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Accounts

#### List Accounts

```bash
GET /twilio/2010-04-01/Accounts.json
```

**Response:**
```json
{
  "accounts": [
    {
      "sid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
      "friendly_name": "My first Twilio account",
      "status": "active",
      "date_created": "Mon, 09 Feb 2026 20:19:55 +0000",
      "date_updated": "Mon, 09 Feb 2026 20:20:05 +0000"
    }
  ]
}
```

#### Get Account

```bash
GET /twilio/2010-04-01/Accounts/{AccountSid}.json
```

### Messages (SMS/MMS)

#### List Messages

```bash
GET /twilio/2010-04-01/Accounts/{AccountSid}/Messages.json
```

**Query Parameters:**
- `PageSize` - Number of results per page (default: 50)
- `To` - Filter by recipient phone number
- `From` - Filter by sender phone number
- `DateSent` - Filter by date sent

**Response:**
```json
{
  "messages": [
    {
      "sid": "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "body": "Hello!",
      "from": "+15551234567",
      "to": "+15559876543",
      "status": "delivered",
      "date_sent": "Mon, 09 Feb 2026 21:00:00 +0000"
    }
  ],
  "page": 0,
  "page_size": 50
}
```

#### Get Message

```bash
GET /twilio/2010-04-01/Accounts/{AccountSid}/Messages/{MessageSid}.json
```

#### Send Message

```bash
POST /twilio/2010-04-01/Accounts/{AccountSid}/Messages.json
Content-Type: application/x-www-form-urlencoded

To=+15559876543&From=+15551234567&Body=Hello%20from%20Twilio!
```

**Required Parameters:**
- `To` - Recipient phone number (E.164 format)
- `From` - Twilio phone number or messaging service SID
- `Body` - Message text (max 1600 characters)

**Optional Parameters:**
- `MessagingServiceSid` - Use instead of From for message routing
- `MediaUrl` - URL of media to send (MMS)
- `StatusCallback` - Webhook URL for status updates

**Response:**
```json
{
  "sid": "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "body": "Hello from Twilio!",
  "from": "+15551234567",
  "to": "+15559876543",
  "status": "queued",
  "date_created": "Mon, 09 Feb 2026 21:00:00 +0000"
}
```

#### Update Message (Redact)

```bash
POST /twilio/2010-04-01/Accounts/{AccountSid}/Messages/{MessageSid}.json
Content-Type: application/x-www-form-urlencoded

Body=
```

Setting Body to empty string redacts the message content.

#### Delete Message

```bash
DELETE /twilio/2010-04-01/Accounts/{AccountSid}/Messages/{MessageSid}.json
```

Returns 204 No Content on success.

### Calls (Voice)

#### List Calls

```bash
GET /twilio/2010-04-01/Accounts/{AccountSid}/Calls.json
```

**Query Parameters:**
- `PageSize` - Results per page
- `Status` - Filter by status (queued, ringing, in-progress, completed, etc.)
- `To` - Filter by recipient
- `From` - Filter by caller

**Response:**
```json
{
  "calls": [
    {
      "sid": "CAxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "from": "+15551234567",
      "to": "+15559876543",
      "status": "completed",
      "duration": "60",
      "direction": "outbound-api"
    }
  ],
  "page": 0,
  "page_size": 50
}
```

#### Get Call

```bash
GET /twilio/2010-04-01/Accounts/{AccountSid}/Calls/{CallSid}.json
```

#### Make Call

```bash
POST /twilio/2010-04-01/Accounts/{AccountSid}/Calls.json
Content-Type: application/x-www-form-urlencoded

To=+15559876543&From=+15551234567&Url=https://example.com/twiml
```

**Required Parameters:**
- `To` - Recipient phone number
- `From` - Twilio phone number
- `Url` - TwiML application URL

**Optional Parameters:**
- `StatusCallback` - Webhook URL for call status updates
- `StatusCallbackEvent` - Events to receive (initiated, ringing, answered, completed)
- `Timeout` - Seconds to wait for answer (default: 60)
- `Record` - Set to true to record the call

#### Update Call

```bash
POST /twilio/2010-04-01/Accounts/{AccountSid}/Calls/{CallSid}.json
Content-Type: application/x-www-form-urlencoded

Status=completed
```

Use `Status=completed` to end an in-progress call.

#### Delete Call

```bash
DELETE /twilio/2010-04-01/Accounts/{AccountSid}/Calls/{CallSid}.json
```

### Phone Numbers

#### List Incoming Phone Numbers

```bash
GET /twilio/2010-04-01/Accounts/{AccountSid}/IncomingPhoneNumbers.json
```

**Response:**
```json
{
  "incoming_phone_numbers": [
    {
      "sid": "PNxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "phone_number": "+15551234567",
      "friendly_name": "My Number",
      "capabilities": {
        "voice": true,
        "sms": true,
        "mms": true
      }
    }
  ]
}
```

#### Get Phone Number

```bash
GET /twilio/2010-04-01/Accounts/{AccountSid}/IncomingPhoneNumbers/{PhoneNumberSid}.json
```

#### Update Phone Number

```bash
POST /twilio/2010-04-01/Accounts/{AccountSid}/IncomingPhoneNumbers/{PhoneNumberSid}.json
Content-Type: application/x-www-form-urlencoded

FriendlyName=Updated%20Name&VoiceUrl=https://example.com/voice
```

#### Delete Phone Number

```bash
DELETE /twilio/2010-04-01/Accounts/{AccountSid}/IncomingPhoneNumbers/{PhoneNumberSid}.json
```

### Applications

#### List Applications

```bash
GET /twilio/2010-04-01/Accounts/{AccountSid}/Applications.json
```

**Response:**
```json
{
  "applications": [
    {
      "sid": "APxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "friendly_name": "My App",
      "voice_url": "https://example.com/voice",
      "sms_url": "https://example.com/sms"
    }
  ]
}
```

#### Get Application

```bash
GET /twilio/2010-04-01/Accounts/{AccountSid}/Applications/{ApplicationSid}.json
```

#### Create Application

```bash
POST /twilio/2010-04-01/Accounts/{AccountSid}/Applications.json
Content-Type: application/x-www-form-urlencoded

FriendlyName=My%20App&VoiceUrl=https://example.com/voice
```

**Response:**
```json
{
  "sid": "APxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "friendly_name": "My App",
  "voice_url": "https://example.com/voice",
  "date_created": "Tue, 10 Feb 2026 00:20:15 +0000"
}
```

#### Update Application

```bash
POST /twilio/2010-04-01/Accounts/{AccountSid}/Applications/{ApplicationSid}.json
Content-Type: application/x-www-form-urlencoded

FriendlyName=Updated%20App%20Name
```

#### Delete Application

```bash
DELETE /twilio/2010-04-01/Accounts/{AccountSid}/Applications/{ApplicationSid}.json
```

Returns 204 No Content on success.

### Queues

#### List Queues

```bash
GET /twilio/2010-04-01/Accounts/{AccountSid}/Queues.json
```

**Response:**
```json
{
  "queues": [
    {
      "sid": "QUxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "friendly_name": "Support Queue",
      "current_size": 0,
      "max_size": 1000,
      "average_wait_time": 0
    }
  ]
}
```

#### Create Queue

```bash
POST /twilio/2010-04-01/Accounts/{AccountSid}/Queues.json
Content-Type: application/x-www-form-urlencoded

FriendlyName=Support%20Queue&MaxSize=100
```

#### Update Queue

```bash
POST /twilio/2010-04-01/Accounts/{AccountSid}/Queues/{QueueSid}.json
Content-Type: application/x-www-form-urlencoded

FriendlyName=Updated%20Queue%20Name
```

#### Delete Queue

```bash
DELETE /twilio/2010-04-01/Accounts/{AccountSid}/Queues/{QueueSid}.json
```

### Addresses

#### List Addresses

```bash
GET /twilio/2010-04-01/Accounts/{AccountSid}/Addresses.json
```

#### Create Address

```bash
POST /twilio/2010-04-01/Accounts/{AccountSid}/Addresses.json
Content-Type: application/x-www-form-urlencoded

FriendlyName=Office&Street=123%20Main%20St&City=San%20Francisco&Region=CA&PostalCode=94105&IsoCountry=US&CustomerName=Acme%20Inc
```

### Usage Records

#### List Usage Records

```bash
GET /twilio/2010-04-01/Accounts/{AccountSid}/Usage/Records.json
```

**Query Parameters:**
- `Category` - Filter by usage category (calls, sms, etc.)
- `StartDate` - Start date (YYYY-MM-DD)
- `EndDate` - End date (YYYY-MM-DD)

**Response:**
```json
{
  "usage_records": [
    {
      "category": "sms",
      "description": "SMS Messages",
      "count": "100",
      "price": "0.75",
      "start_date": "2026-02-01",
      "end_date": "2026-02-28"
    }
  ]
}
```

## Pagination

Twilio uses page-based pagination:

```bash
GET /twilio/2010-04-01/Accounts/{AccountSid}/Messages.json?PageSize=50&Page=0
```

**Parameters:**
- `PageSize` - Results per page (default: 50)
- `Page` - Page number (0-indexed)

**Response includes:**
```json
{
  "messages": [...],
  "page": 0,
  "page_size": 50,
  "first_page_uri": "/2010-04-01/Accounts/{AccountSid}/Messages.json?PageSize=50&Page=0",
  "next_page_uri": "/2010-04-01/Accounts/{AccountSid}/Messages.json?PageSize=50&Page=1",
  "previous_page_uri": null
}
```

Use `next_page_uri` to fetch the next page of results.

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/twilio/2010-04-01/Accounts.json',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const data = await response.json();
const accountSid = data.accounts[0].sid;
console.log(`Account SID: ${accountSid}`);
```

### Python

```python
import os
import requests

# Get account SID
response = requests.get(
    'https://gateway.maton.ai/twilio/2010-04-01/Accounts.json',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
account_sid = response.json()['accounts'][0]['sid']
print(f"Account SID: {account_sid}")
```

### Python (Send SMS)

```python
import os
import requests

account_sid = 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

response = requests.post(
    f'https://gateway.maton.ai/twilio/2010-04-01/Accounts/{account_sid}/Messages.json',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/x-www-form-urlencoded'
    },
    data={
        'To': '+15559876543',
        'From': '+15551234567',
        'Body': 'Hello from Python!'
    }
)
message = response.json()
print(f"Message SID: {message['sid']}")
print(f"Status: {message['status']}")
```

### Python (Make Call)

```python
import os
import requests

account_sid = 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

response = requests.post(
    f'https://gateway.maton.ai/twilio/2010-04-01/Accounts/{account_sid}/Calls.json',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/x-www-form-urlencoded'
    },
    data={
        'To': '+15559876543',
        'From': '+15551234567',
        'Url': 'https://demo.twilio.com/docs/voice.xml'
    }
)
call = response.json()
print(f"Call SID: {call['sid']}")
print(f"Status: {call['status']}")
```

## Notes

- All endpoints require the `/2010-04-01/` API version prefix
- Most endpoints require your Account SID in the path
- Request bodies use `application/x-www-form-urlencoded` format (not JSON)
- Phone numbers must be in E.164 format (+15551234567)
- SIDs are unique identifiers:
  - Account SIDs start with `AC`
  - Message SIDs start with `SM` (SMS) or `MM` (MMS)
  - Call SIDs start with `CA`
  - Phone Number SIDs start with `PN`
  - Application SIDs start with `AP`
  - Queue SIDs start with `QU`
- POST is used for both creating and updating resources
- DELETE returns 204 No Content on success
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Twilio connection or bad request |
| 401 | Invalid or missing Maton API key |
| 404 | Resource not found |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Twilio API |

Twilio error responses include:
```json
{
  "code": 20404,
  "message": "The requested resource was not found",
  "more_info": "https://www.twilio.com/docs/errors/20404",
  "status": 404
}
```

### Troubleshooting: Invalid API Key

**When you receive an "Invalid API key" error, ALWAYS follow these steps before concluding there is an issue:**

1. Check that the `MATON_API_KEY` environment variable is set:

```bash
echo $MATON_API_KEY
```

2. Verify the API key is valid by listing connections:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Resources

- [Twilio API Overview](https://www.twilio.com/docs/usage/api)
- [Messages API](https://www.twilio.com/docs/messaging/api/message-resource)
- [Calls API](https://www.twilio.com/docs/voice/api/call-resource)
- [Phone Numbers API](https://www.twilio.com/docs/phone-numbers/api/incomingphonenumber-resource)
- [Applications API](https://www.twilio.com/docs/usage/api/applications)
- [Usage Records API](https://www.twilio.com/docs/usage/api/usage-record)
