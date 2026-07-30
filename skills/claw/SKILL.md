---
name: claw
description: "Google Workspace via ClawEmail — Gmail, Drive, Docs, Sheets, Slides, Calendar, Forms. Use PROACTIVELY when the user asks to send email, create documents, manage files, schedule events, or work with any Google service."
metadata: {"openclaw":{"emoji":"🦞","requires":{"env":["CLAWEMAIL_CREDENTIALS"]},"primaryEnv":"CLAWEMAIL_CREDENTIALS"}}
---

# Claw — Google Workspace for AI Agents

Use `claw` for Gmail, Drive, Docs, Sheets, Slides, Calendar, and Forms via your @clawemail.com account.

## Setup

1. Save your ClawEmail credentials JSON to `~/.config/clawemail/credentials.json`
2. Set the environment variable: `export CLAWEMAIL_CREDENTIALS=~/.config/clawemail/credentials.json`

Get credentials at https://clawemail.com — sign up, then visit `/connect/YOUR_PREFIX` to authorize OAuth.

## Getting an Access Token

All API calls need a Bearer token. Use the helper script to refresh and cache it:

```bash
TOKEN=$(~/.openclaw/skills/claw/scripts/token.sh)
```

The script caches tokens for 50 minutes. Always assign to `TOKEN` before making API calls.

---

## Gmail

### Search emails

```bash
TOKEN=$(~/.openclaw/skills/claw/scripts/token.sh)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://gmail.googleapis.com/gmail/v1/users/me/messages?q=newer_than:7d&maxResults=10" | python3 -m json.tool
```

Common query operators: `from:`, `to:`, `subject:`, `newer_than:`, `older_than:`, `is:unread`, `has:attachment`, `label:`, `in:inbox`.

### Read a message

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://gmail.googleapis.com/gmail/v1/users/me/messages/MESSAGE_ID?format=full" | python3 -m json.tool
```

For plain text body only, use `format=minimal` and decode the payload. For readable output:

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://gmail.googleapis.com/gmail/v1/users/me/messages/MESSAGE_ID?format=full" \
  | python3 -c "
import json,sys,base64
m=json.load(sys.stdin)
hdrs={h['name']:h['value'] for h in m['payload']['headers']}
print(f\"From: {hdrs.get('From','')}\nTo: {hdrs.get('To','')}\nSubject: {hdrs.get('Subject','')}\nDate: {hdrs.get('Date','')}\n\")
def get_body(part):
    if part.get('body',{}).get('data'):
        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8','replace')
    for p in part.get('parts',[]):
        if p['mimeType']=='text/plain': return get_body(p)
    for p in part.get('parts',[]):
        b=get_body(p)
        if b: return b
    return ''
print(get_body(m['payload']))
"
```

### Send an email

```bash
TOKEN=$(~/.openclaw/skills/claw/scripts/token.sh)
python3 -c "
import base64,json
raw = base64.urlsafe_b64encode(
    b'To: recipient@example.com\r\nSubject: Hello\r\nContent-Type: text/plain; charset=utf-8\r\n\r\nMessage body here'
).decode()
print(json.dumps({'raw': raw}))
" | curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @- \
  "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
```

For HTML emails, replace `Content-Type: text/plain` with `Content-Type: text/html` and use HTML in the body.

### Reply to a message

Same as send, but add `In-Reply-To:` and `References:` headers from the original message, and include `threadId` in the JSON body:

```bash
python3 -c "
import base64,json
raw = base64.urlsafe_b64encode(
    b'To: recipient@example.com\r\nSubject: Re: Original Subject\r\nIn-Reply-To: <original-message-id>\r\nReferences: <original-message-id>\r\nContent-Type: text/plain; charset=utf-8\r\n\r\nReply body'
).decode()
print(json.dumps({'raw': raw, 'threadId': 'THREAD_ID'}))
" | curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @- \
  "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
```

### List labels

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://gmail.googleapis.com/gmail/v1/users/me/labels" | python3 -m json.tool
```

### Add/remove labels

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"addLabelIds":["LABEL_ID"],"removeLabelIds":["INBOX"]}' \
  "https://gmail.googleapis.com/gmail/v1/users/me/messages/MESSAGE_ID/modify"
```

---

## Google Drive

### List files

```bash
TOKEN=$(~/.openclaw/skills/claw/scripts/token.sh)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://www.googleapis.com/drive/v3/files?pageSize=20&fields=files(id,name,mimeType,modifiedTime,size)&orderBy=modifiedTime desc" | python3 -m json.tool
```

### Search files

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://www.googleapis.com/drive/v3/files?q=name+contains+'report'&fields=files(id,name,mimeType,modifiedTime)" | python3 -m json.tool
```

Query operators: `name contains 'term'`, `mimeType='application/vnd.google-apps.document'`, `'FOLDER_ID' in parents`, `trashed=false`, `modifiedTime > '2025-01-01'`.

Common MIME types:
- Document: `application/vnd.google-apps.document`
- Spreadsheet: `application/vnd.google-apps.spreadsheet`
- Presentation: `application/vnd.google-apps.presentation`
- Folder: `application/vnd.google-apps.folder`
- Form: `application/vnd.google-apps.form`

### Create a folder

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Folder","mimeType":"application/vnd.google-apps.folder"}' \
  "https://www.googleapis.com/drive/v3/files?fields=id,name" | python3 -m json.tool
```

### Upload a file

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -F "metadata={\"name\":\"report.pdf\"};type=application/json" \
  -F "file=@/path/to/report.pdf;type=application/pdf" \
  "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name" | python3 -m json.tool
```

### Download a file

For Google Docs/Sheets/Slides (export):

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://www.googleapis.com/drive/v3/files/FILE_ID/export?mimeType=application/pdf" -o output.pdf
```

Export formats: `text/plain`, `text/html`, `application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document` (docx), `text/csv` (sheets).

For binary files (download):

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://www.googleapis.com/drive/v3/files/FILE_ID?alt=media" -o output.file
```

### Share a file

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role":"writer","type":"user","emailAddress":"user@example.com"}' \
  "https://www.googleapis.com/drive/v3/files/FILE_ID/permissions"
```

Roles: `reader`, `commenter`, `writer`, `owner`. Types: `user`, `group`, `domain`, `anyone`.

### Delete a file

```bash
curl -s -X DELETE -H "Authorization: Bearer $TOKEN" \
  "https://www.googleapis.com/drive/v3/files/FILE_ID"
```

---

## Google Docs

### Create a document

```bash
TOKEN=$(~/.openclaw/skills/claw/scripts/token.sh)
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My Document"}' \
  "https://docs.googleapis.com/v1/documents" | python3 -m json.tool
```

### Read a document

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://docs.googleapis.com/v1/documents/DOCUMENT_ID" | python3 -m json.tool
```

For plain text extraction:

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://docs.googleapis.com/v1/documents/DOCUMENT_ID" \
  | python3 -c "
import json,sys
doc=json.load(sys.stdin)
text=''
for el in doc.get('body',{}).get('content',[]):
    for p in el.get('paragraph',{}).get('elements',[]):
        text+=p.get('textRun',{}).get('content','')
print(text)
"
```

### Append text to a document

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"requests":[{"insertText":{"location":{"index":1},"text":"Hello, world!\n"}}]}' \
  "https://docs.googleapis.com/v1/documents/DOCUMENT_ID:batchUpdate"
```

### Replace text in a document

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"requests":[{"replaceAllText":{"containsText":{"text":"OLD_TEXT","matchCase":true},"replaceText":"NEW_TEXT"}}]}' \
  "https://docs.googleapis.com/v1/documents/DOCUMENT_ID:batchUpdate"
```

### Insert a heading

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"requests":[{"insertText":{"location":{"index":1},"text":"My Heading\n"}},{"updateParagraphStyle":{"range":{"startIndex":1,"endIndex":12},"paragraphStyle":{"namedStyleType":"HEADING_1"},"fields":"namedStyleType"}}]}' \
  "https://docs.googleapis.com/v1/documents/DOCUMENT_ID:batchUpdate"
```

Heading styles: `HEADING_1` through `HEADING_6`, `TITLE`, `SUBTITLE`, `NORMAL_TEXT`.

---

## Google Sheets

### Create a spreadsheet

```bash
TOKEN=$(~/.openclaw/skills/claw/scripts/token.sh)
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"properties":{"title":"My Spreadsheet"}}' \
  "https://sheets.googleapis.com/v4/spreadsheets" | python3 -m json.tool
```

### Read cells

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID/values/Sheet1!A1:D10" | python3 -m json.tool
```

### Write cells

```bash
curl -s -X PUT -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"values":[["Name","Age","City"],["Alice","30","NYC"],["Bob","25","LA"]]}' \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID/values/Sheet1!A1:C3?valueInputOption=USER_ENTERED" | python3 -m json.tool
```

### Append rows

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"values":[["Charlie","35","Chicago"]]}' \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID/values/Sheet1!A:C:append?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS" | python3 -m json.tool
```

### Clear a range

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID/values/Sheet1!A1:D10:clear"
```

### Get spreadsheet metadata

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID?fields=properties.title,sheets.properties" | python3 -m json.tool
```

---

## Google Slides

### Create a presentation

```bash
TOKEN=$(~/.openclaw/skills/claw/scripts/token.sh)
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My Presentation"}' \
  "https://slides.googleapis.com/v1/presentations" | python3 -m json.tool
```

### Get presentation info

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://slides.googleapis.com/v1/presentations/PRESENTATION_ID" | python3 -m json.tool
```

### Add a new slide

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"requests":[{"createSlide":{"slideLayoutReference":{"predefinedLayout":"TITLE_AND_BODY"}}}]}' \
  "https://slides.googleapis.com/v1/presentations/PRESENTATION_ID:batchUpdate" | python3 -m json.tool
```

Layouts: `BLANK`, `TITLE`, `TITLE_AND_BODY`, `TITLE_AND_TWO_COLUMNS`, `TITLE_ONLY`, `SECTION_HEADER`, `ONE_COLUMN_TEXT`, `MAIN_POINT`, `BIG_NUMBER`.

### Add text to a slide

First get the slide's page object IDs, then insert text into a placeholder:

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"requests":[{"insertText":{"objectId":"PLACEHOLDER_OBJECT_ID","text":"Hello from ClawEmail!","insertionIndex":0}}]}' \
  "https://slides.googleapis.com/v1/presentations/PRESENTATION_ID:batchUpdate"
```

### Add an image to a slide

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"requests":[{"createImage":{"url":"https://example.com/image.png","elementProperties":{"pageObjectId":"SLIDE_ID","size":{"width":{"magnitude":3000000,"unit":"EMU"},"height":{"magnitude":2000000,"unit":"EMU"}},"transform":{"scaleX":1,"scaleY":1,"translateX":1000000,"translateY":1500000,"unit":"EMU"}}}}]}' \
  "https://slides.googleapis.com/v1/presentations/PRESENTATION_ID:batchUpdate"
```

---

## Google Calendar

### List upcoming events

```bash
TOKEN=$(~/.openclaw/skills/claw/scripts/token.sh)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin=$(date -u +%Y-%m-%dT%H:%M:%SZ)&maxResults=10&singleEvents=true&orderBy=startTime" | python3 -m json.tool
```

### Get events in a date range

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin=2025-03-01T00:00:00Z&timeMax=2025-03-31T23:59:59Z&singleEvents=true&orderBy=startTime" | python3 -m json.tool
```

### Create an event

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Team Meeting",
    "description": "Weekly standup",
    "start": {"dateTime": "2025-03-15T10:00:00-05:00", "timeZone": "America/New_York"},
    "end": {"dateTime": "2025-03-15T11:00:00-05:00", "timeZone": "America/New_York"},
    "attendees": [{"email": "colleague@example.com"}]
  }' \
  "https://www.googleapis.com/calendar/v3/calendars/primary/events" | python3 -m json.tool
```

### Update an event

```bash
curl -s -X PATCH -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"summary":"Updated Meeting Title","location":"Conference Room A"}' \
  "https://www.googleapis.com/calendar/v3/calendars/primary/events/EVENT_ID" | python3 -m json.tool
```

### Delete an event

```bash
curl -s -X DELETE -H "Authorization: Bearer $TOKEN" \
  "https://www.googleapis.com/calendar/v3/calendars/primary/events/EVENT_ID"
```

### List calendars

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://www.googleapis.com/calendar/v3/users/me/calendarList" | python3 -m json.tool
```

---

## Google Forms

### Create a form

```bash
TOKEN=$(~/.openclaw/skills/claw/scripts/token.sh)
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"info":{"title":"Feedback Form"}}' \
  "https://forms.googleapis.com/v1/forms" | python3 -m json.tool
```

### Add questions

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"requests":[{"createItem":{"item":{"title":"How would you rate this?","questionItem":{"question":{"required":true,"scaleQuestion":{"low":1,"high":5,"lowLabel":"Poor","highLabel":"Excellent"}}}},"location":{"index":0}}}]}' \
  "https://forms.googleapis.com/v1/forms/FORM_ID:batchUpdate"
```

### Get form responses

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://forms.googleapis.com/v1/forms/FORM_ID/responses" | python3 -m json.tool
```

---

## Tips

- **Always refresh token first:** Start every sequence with `TOKEN=$(~/.openclaw/skills/claw/scripts/token.sh)`
- **JSON output:** Pipe through `python3 -m json.tool` for readable output, or `| python3 -c "import json,sys;..."` for extraction
- **Pagination:** Most list endpoints return `nextPageToken`. Pass it as `?pageToken=TOKEN` for the next page
- **Batch operations:** Docs, Sheets, and Slides support `batchUpdate` — send multiple operations in one request
- **Error 401:** Token expired. Re-run `token.sh` to refresh
- **Error 403:** Scope not authorized. The ClawEmail OAuth includes Gmail, Drive, Docs, Sheets, Slides, Calendar, and Forms scopes
- **Rate limits:** Google APIs have per-user rate limits. Add brief delays between rapid successive calls
- **File IDs:** Google Docs/Sheets/Slides URLs contain the file ID: `https://docs.google.com/document/d/FILE_ID/edit`

## When to Use

- User asks to send, read, or search email
- User wants to create or edit documents, spreadsheets, or presentations
- User needs to manage files in Google Drive
- User wants to schedule or check calendar events
- User asks to create forms or review form responses
- Any task involving Google Workspace services
