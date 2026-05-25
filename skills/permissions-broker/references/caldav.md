# iCloud CalDAV Templates

Use these as starting points for `body` + `headers` when calling `POST /v1/proxy/request`.

Notes

- Set `method` to a WebDAV method like `PROPFIND` or `REPORT`.
- Include `headers.depth` for `PROPFIND`.
- Use `headers.content-type: application/xml` for DAV XML.
- Use `headers.content-type: text/calendar` for VEVENT/VTODO `.ics` writes.

## 1. PROPFIND: List collections under home-set

Typical purpose: list calendars/task lists under a known home-set URL.

Broker request body example:

```json
{
  "upstream_url": "https://<caldav-host>/<path>/",
  "method": "PROPFIND",
  "headers": {
    "depth": "1",
    "content-type": "application/xml"
  },
  "body": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<D:propfind xmlns:D=\"DAV:\" xmlns:C=\"urn:ietf:params:xml:ns:caldav\">\n  <D:prop>\n    <D:displayname />\n    <D:resourcetype />\n    <C:supported-calendar-component-set />\n  </D:prop>\n</D:propfind>\n",
  "consent_hint": "List my iCloud calendars/task lists"
}
```

## 2. REPORT: Query calendar events (time-range)

Typical purpose: fetch events between two times from a specific calendar collection.

```json
{
  "upstream_url": "https://<caldav-host>/<calendar-collection>/",
  "method": "REPORT",
  "headers": {
    "depth": "1",
    "content-type": "application/xml"
  },
  "body": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<C:calendar-query xmlns:D=\"DAV:\" xmlns:C=\"urn:ietf:params:xml:ns:caldav\">\n  <D:prop>\n    <D:getetag />\n    <C:calendar-data />\n  </D:prop>\n  <C:filter>\n    <C:comp-filter name=\"VCALENDAR\">\n      <C:comp-filter name=\"VEVENT\">\n        <C:time-range start=\"20260213T000000Z\" end=\"20260220T000000Z\" />\n      </C:comp-filter>\n    </C:comp-filter>\n  </C:filter>\n</C:calendar-query>\n",
  "consent_hint": "Query my iCloud calendar events for a specific week"
}
```

## 3. PUT: Create/update an event (VEVENT)

```json
{
  "upstream_url": "https://<caldav-host>/<calendar-collection>/<uid>.ics",
  "method": "PUT",
  "headers": {
    "content-type": "text/calendar; charset=utf-8"
  },
  "body": "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//permissions-broker//EN\nBEGIN:VEVENT\nUID:<uid>\nDTSTAMP:20260213T120000Z\nDTSTART:20260214T090000Z\nDTEND:20260214T093000Z\nSUMMARY:Test event via broker\nEND:VEVENT\nEND:VCALENDAR\n",
  "consent_hint": "Create a new iCloud calendar event"
}
```

## 4. PUT: Create/update a reminder/task (VTODO)

```json
{
  "upstream_url": "https://<caldav-host>/<task-collection>/<uid>.ics",
  "method": "PUT",
  "headers": {
    "content-type": "text/calendar; charset=utf-8"
  },
  "body": "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//permissions-broker//EN\nBEGIN:VTODO\nUID:<uid>\nDTSTAMP:20260213T120000Z\nDUE:20260214T170000Z\nSUMMARY:Test reminder via broker\nSTATUS:NEEDS-ACTION\nEND:VTODO\nEND:VCALENDAR\n",
  "consent_hint": "Create a new iCloud reminder"
}
```

## 5. DELETE: Delete an event/task

```json
{
  "upstream_url": "https://<caldav-host>/<collection>/<uid>.ics",
  "method": "DELETE",
  "consent_hint": "Delete an iCloud calendar object"
}
```
