---
name: api-gateway
description: |
  Connect to 100+ APIs (Google Workspace, Microsoft 365, Notion, Slack, Airtable, HubSpot, etc.) with managed OAuth.
  Use this skill when users want to interact with external services.
  Security: The MATON_API_KEY authenticates with Maton.ai but grants NO access to third-party services by itself. Each service requires explicit OAuth authorization by the user through Maton's connect flow. Access is strictly scoped to connections the user has authorized. Provided by Maton (https://maton.ai).
compatibility: Requires network access and valid Maton API key
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji: 🧠
    homepage: "https://maton.ai"
    requires:
      env:
        - MATON_API_KEY
---

# API Gateway

Passthrough proxy for direct access to third-party APIs using managed OAuth connections, provided by [Maton](https://maton.ai). The API gateway lets you call native API endpoints directly.

## Quick Start

```bash
# Native Slack API call
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'channel': 'C0123456', 'text': 'Hello from gateway!'}).encode()
req = urllib.request.Request('https://gateway.maton.ai/slack/api/chat.postMessage', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```


## Base URL

```
https://gateway.maton.ai/{app}/{native-api-path}
```

Replace `{app}` with the service name and `{native-api-path}` with the actual API endpoint path.

IMPORTANT: The URL path MUST start with the connection's app name (eg. `/google-mail/...`). This prefix tells the gateway which app connection to use. For example, the native Gmail API path starts with `gmail/v1/`, so full paths look like `/google-mail/gmail/v1/users/me/messages`.

## Authentication

All requests require the Maton API key in the Authorization header:

```
Authorization: Bearer $MATON_API_KEY
```

The API gateway automatically injects the appropriate OAuth token for the target service.

**Environment Variable:** You can set your API key as the `MATON_API_KEY` environment variable:

```bash
export MATON_API_KEY="YOUR_API_KEY"
```

## Getting Your API Key

1. Sign in or create an account at [maton.ai](https://maton.ai)
2. Go to [maton.ai/settings](https://maton.ai/settings)
3. Click the copy button on the right side of API Key section to copy it

## Connection Management

Connection management uses a separate base URL: `https://ctrl.maton.ai`

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=slack&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Query Parameters (optional):**
- `app` - Filter by service name (e.g., `slack`, `hubspot`, `salesforce`)
- `status` - Filter by connection status (`ACTIVE`, `PENDING`, `FAILED`)

**Response:**
```json
{
  "connections": [
    {
      "connection_id": "21fd90f9-5935-43cd-b6c8-bde9d915ca80",
      "status": "ACTIVE",
      "creation_time": "2025-12-08T07:20:53.488460Z",
      "last_updated_time": "2026-01-31T20:03:32.593153Z",
      "url": "https://connect.maton.ai/?session_token=5e9...",
      "app": "slack",
      "metadata": {}
    }
  ]
}
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'slack'}).encode()
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
    "connection_id": "21fd90f9-5935-43cd-b6c8-bde9d915ca80",
    "status": "ACTIVE",
    "creation_time": "2025-12-08T07:20:53.488460Z",
    "last_updated_time": "2026-01-31T20:03:32.593153Z",
    "url": "https://connect.maton.ai/?session_token=5e9...",
    "app": "slack",
    "metadata": {}
  }
}
```

Open the returned URL in a browser to complete OAuth.

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

If you have multiple connections for the same app, you can specify which connection to use by adding the `Maton-Connection` header with the connection ID:

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'channel': 'C0123456', 'text': 'Hello!'}).encode()
req = urllib.request.Request('https://gateway.maton.ai/slack/api/chat.postMessage', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
req.add_header('Maton-Connection', '21fd90f9-5935-43cd-b6c8-bde9d915ca80')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection for that app.

## Supported Services

| Service | App Name | Base URL Proxied |
|---------|----------|------------------|
| ActiveCampaign | `active-campaign` | `{account}.api-us1.com` |
| Acuity Scheduling | `acuity-scheduling` | `acuityscheduling.com` |
| Airtable | `airtable` | `api.airtable.com` |
| Apollo | `apollo` | `api.apollo.io` |
| Asana | `asana` | `app.asana.com` |
| Attio | `attio` | `api.attio.com` |
| Basecamp | `basecamp` | `3.basecampapi.com` |
| beehiiv | `beehiiv` | `api.beehiiv.com` |
| Box | `box` | `api.box.com` |
| Brevo | `brevo` | `api.brevo.com` |
| Calendly | `calendly` | `api.calendly.com` |
| Cal.com | `cal-com` | `api.cal.com` |
| CallRail | `callrail` | `api.callrail.com` |
| Chargebee | `chargebee` | `{subdomain}.chargebee.com` |
| ClickFunnels | `clickfunnels` | `{subdomain}.myclickfunnels.com` |
| ClickSend | `clicksend` | `rest.clicksend.com` |
| ClickUp | `clickup` | `api.clickup.com` |
| Clockify | `clockify` | `api.clockify.me` |
| Coda | `coda` | `coda.io` |
| Confluence | `confluence` | `api.atlassian.com` |
| CompanyCam | `companycam` | `api.companycam.com` |
| Cognito Forms | `cognito-forms` | `www.cognitoforms.com` |
| Constant Contact | `constant-contact` | `api.cc.email` |
| Dropbox | `dropbox` | `api.dropboxapi.com` |
| Dropbox Business | `dropbox-business` | `api.dropboxapi.com` |
| ElevenLabs | `elevenlabs` | `api.elevenlabs.io` |
| Eventbrite | `eventbrite` | `www.eventbriteapi.com` |
| Fathom | `fathom` | `api.fathom.ai` |
| Firebase | `firebase` | `firebase.googleapis.com` |
| Fireflies | `fireflies` | `api.fireflies.ai` |
| GetResponse | `getresponse` | `api.getresponse.com` |
| GitHub | `github` | `api.github.com` |
| Gumroad | `gumroad` | `api.gumroad.com` |
| Google Ads | `google-ads` | `googleads.googleapis.com` |
| Google BigQuery | `google-bigquery` | `bigquery.googleapis.com` |
| Google Analytics Admin | `google-analytics-admin` | `analyticsadmin.googleapis.com` |
| Google Analytics Data | `google-analytics-data` | `analyticsdata.googleapis.com` |
| Google Calendar | `google-calendar` | `www.googleapis.com` |
| Google Classroom | `google-classroom` | `classroom.googleapis.com` |
| Google Contacts | `google-contacts` | `people.googleapis.com` |
| Google Docs | `google-docs` | `docs.googleapis.com` |
| Google Drive | `google-drive` | `www.googleapis.com` |
| Google Forms | `google-forms` | `forms.googleapis.com` |
| Gmail | `google-mail` | `gmail.googleapis.com` |
| Google Merchant | `google-merchant` | `merchantapi.googleapis.com` |
| Google Meet | `google-meet` | `meet.googleapis.com` |
| Google Play | `google-play` | `androidpublisher.googleapis.com` |
| Google Search Console | `google-search-console` | `www.googleapis.com` |
| Google Sheets | `google-sheets` | `sheets.googleapis.com` |
| Google Slides | `google-slides` | `slides.googleapis.com` |
| Google Tasks | `google-tasks` | `tasks.googleapis.com` |
| Google Workspace Admin | `google-workspace-admin` | `admin.googleapis.com` |
| HubSpot | `hubspot` | `api.hubapi.com` |
| Instantly | `instantly` | `api.instantly.ai` |
| Jira | `jira` | `api.atlassian.com` |
| Jobber | `jobber` | `api.getjobber.com` |
| JotForm | `jotform` | `api.jotform.com` |
| Keap | `keap` | `api.infusionsoft.com` |
| Kit | `kit` | `api.kit.com` |
| Klaviyo | `klaviyo` | `a.klaviyo.com` |
| Lemlist | `lemlist` | `api.lemlist.com` |
| Linear | `linear` | `api.linear.app` |
| LinkedIn | `linkedin` | `api.linkedin.com` |
| Mailchimp | `mailchimp` | `{dc}.api.mailchimp.com` |
| MailerLite | `mailerlite` | `connect.mailerlite.com` |
| Mailgun | `mailgun` | `api.mailgun.net` |
| ManyChat | `manychat` | `api.manychat.com` |
| Microsoft Excel | `microsoft-excel` | `graph.microsoft.com` |
| Microsoft Teams | `microsoft-teams` | `graph.microsoft.com` |
| Microsoft To Do | `microsoft-to-do` | `graph.microsoft.com` |
| Monday.com | `monday` | `api.monday.com` |
| Motion | `motion` | `api.usemotion.com` |
| Netlify | `netlify` | `api.netlify.com` |
| Notion | `notion` | `api.notion.com` |
| OneDrive | `one-drive` | `graph.microsoft.com` |
| Outlook | `outlook` | `graph.microsoft.com` |
| PDF.co | `pdf-co` | `api.pdf.co` |
| Pipedrive | `pipedrive` | `api.pipedrive.com` |
| Podio | `podio` | `api.podio.com` |
| QuickBooks | `quickbooks` | `quickbooks.api.intuit.com` |
| Quo | `quo` | `api.openphone.com` |
| Salesforce | `salesforce` | `{instance}.salesforce.com` |
| SignNow | `signnow` | `api.signnow.com` |
| Slack | `slack` | `slack.com` |
| Snapchat | `snapchat` | `adsapi.snapchat.com` |
| Square | `squareup` | `connect.squareup.com` |
| Stripe | `stripe` | `api.stripe.com` |
| Systeme.io | `systeme` | `api.systeme.io` |
| Tally | `tally` | `api.tally.so` |
| Telegram | `telegram` | `api.telegram.org` |
| TickTick | `ticktick` | `api.ticktick.com` |
| Todoist | `todoist` | `api.todoist.com` |
| Toggl Track | `toggl-track` | `api.track.toggl.com` |
| Trello | `trello` | `api.trello.com` |
| Twilio | `twilio` | `api.twilio.com` |
| Typeform | `typeform` | `api.typeform.com` |
| Vimeo | `vimeo` | `api.vimeo.com` |
| WhatsApp Business | `whatsapp-business` | `graph.facebook.com` |
| WooCommerce | `woocommerce` | `{store-url}/wp-json/wc/v3` |
| WordPress.com | `wordpress` | `public-api.wordpress.com` |
| Xero | `xero` | `api.xero.com` |
| YouTube | `youtube` | `www.googleapis.com` |
| Zoho Bigin | `zoho-bigin` | `www.zohoapis.com` |
| Zoho Bookings | `zoho-bookings` | `www.zohoapis.com` |
| Zoho Books | `zoho-books` | `www.zohoapis.com` |
| Zoho Calendar | `zoho-calendar` | `calendar.zoho.com` |
| Zoho CRM | `zoho-crm` | `www.zohoapis.com` |
| Zoho Inventory | `zoho-inventory` | `www.zohoapis.com` |
| Zoho Mail | `zoho-mail` | `mail.zoho.com` |
| Zoho People | `zoho-people` | `people.zoho.com` |
| Zoho Recruit | `zoho-recruit` | `recruit.zoho.com` |

See [references/](references/) for detailed routing guides per provider:
- [ActiveCampaign](references/active-campaign.md) - Contacts, deals, tags, lists, automations, campaigns
- [Acuity Scheduling](references/acuity-scheduling.md) - Appointments, calendars, clients, availability
- [Airtable](references/airtable.md) - Records, bases, tables
- [Apollo](references/apollo.md) - People search, enrichment, contacts
- [Asana](references/asana.md) - Tasks, projects, workspaces, webhooks
- [Attio](references/attio.md) - People, companies, records, tasks
- [Basecamp](references/basecamp.md) - Projects, to-dos, messages, schedules, documents
- [beehiiv](references/beehiiv.md) - Publications, subscriptions, posts, custom fields
- [Box](references/box.md) - Files, folders, collaborations, shared links
- [Brevo](references/brevo.md) - Contacts, email campaigns, transactional emails, templates
- [Calendly](references/calendly.md) - Event types, scheduled events, availability, webhooks
- [Cal.com](references/cal-com.md) - Event types, bookings, schedules, availability slots, webhooks
- [CallRail](references/callrail.md) - Calls, trackers, companies, tags, analytics
- [Chargebee](references/chargebee.md) - Subscriptions, customers, invoices
- [ClickFunnels](references/clickfunnels.md) - Contacts, products, orders, courses, webhooks
- [ClickSend](references/clicksend.md) - SMS, MMS, voice messages, contacts, lists
- [ClickUp](references/clickup.md) - Tasks, lists, folders, spaces, webhooks
- [Clockify](references/clockify.md) - Time tracking, projects, clients, tasks, workspaces
- [Coda](references/coda.md) - Docs, pages, tables, rows, formulas, controls
- [Confluence](references/confluence.md) - Pages, spaces, blogposts, comments, attachments
- [CompanyCam](references/companycam.md) - Projects, photos, users, tags, groups, documents
- [Cognito Forms](references/cognito-forms.md) - Forms, entries, documents, files
- [Constant Contact](references/constant-contact.md) - Contacts, email campaigns, lists, segments
- [Dropbox](references/dropbox.md) - Files, folders, search, metadata, revisions, tags
- [Dropbox Business](references/dropbox-business.md) - Team members, groups, team folders, devices, audit logs
- [ElevenLabs](references/elevenlabs.md) - Text-to-speech, voice cloning, sound effects, audio processing
- [Eventbrite](references/eventbrite.md) - Events, venues, tickets, orders, attendees
- [Fathom](references/fathom.md) - Meeting recordings, transcripts, summaries, webhooks
- [Firebase](references/firebase.md) - Projects, web apps, Android apps, iOS apps, configurations
- [Fireflies](references/fireflies.md) - Meeting transcripts, summaries, AskFred AI, channels
- [GetResponse](references/getresponse.md) - Campaigns, contacts, newsletters, autoresponders, tags, segments
- [GitHub](references/github.md) - Repositories, issues, pull requests, commits
- [Gumroad](references/gumroad.md) - Products, sales, subscribers, licenses, webhooks
- [Google Ads](references/google-ads.md) - Campaigns, ad groups, GAQL queries
- [Google Analytics Admin](references/google-analytics-admin.md) - Reports, dimensions, metrics
- [Google Analytics Data](references/google-analytics-data.md) - Reports, dimensions, metrics
- [Google BigQuery](references/google-bigquery.md) - Datasets, tables, jobs, SQL queries
- [Google Calendar](references/google-calendar.md) - Events, calendars, free/busy
- [Google Classroom](references/google-classroom.md) - Courses, coursework, students, teachers, announcements
- [Google Contacts](references/google-contacts.md) - Contacts, contact groups, people search
- [Google Docs](references/google-docs.md) - Document creation, batch updates
- [Google Drive](references/google-drive.md) - Files, folders, permissions
- [Google Forms](references/google-forms.md) - Forms, questions, responses
- [Gmail](references/google-mail.md) - Messages, threads, labels
- [Google Meet](references/google-meet.md) - Spaces, conference records, participants
- [Google Merchant](references/google-merchant.md) - Products, inventories, promotions, reports
- [Google Play](references/google-play.md) - In-app products, subscriptions, reviews
- [Google Search Console](references/google-search-console.md) - Search analytics, sitemaps
- [Google Sheets](references/google-sheets.md) - Values, ranges, formatting
- [Google Slides](references/google-slides.md) - Presentations, slides, formatting
- [Google Tasks](references/google-tasks.md) - Task lists, tasks, subtasks
- [Google Workspace Admin](references/google-workspace-admin.md) - Users, groups, org units, domains, roles
- [HubSpot](references/hubspot.md) - Contacts, companies, deals
- [Instantly](references/instantly.md) - Campaigns, leads, accounts, email outreach
- [Jira](references/jira.md) - Issues, projects, JQL queries
- [Jobber](references/jobber.md) - Clients, jobs, invoices, quotes (GraphQL)
- [JotForm](references/jotform.md) - Forms, submissions, webhooks
- [Keap](references/keap.md) - Contacts, companies, tags, tasks, opportunities, campaigns
- [Kit](references/kit.md) - Subscribers, tags, forms, sequences, broadcasts
- [Klaviyo](references/klaviyo.md) - Profiles, lists, campaigns, flows, events
- [Lemlist](references/lemlist.md) - Campaigns, leads, activities, schedules, unsubscribes
- [Linear](references/linear.md) - Issues, projects, teams, cycles (GraphQL)
- [LinkedIn](references/linkedin.md) - Profile, posts, shares, media uploads
- [Mailchimp](references/mailchimp.md) - Audiences, campaigns, templates, automations
- [MailerLite](references/mailerlite.md) - Subscribers, groups, campaigns, automations, forms
- [Mailgun](references/mailgun.md) - Email sending, domains, routes, templates, mailing lists, suppressions
- [ManyChat](references/manychat.md) - Subscribers, tags, flows, messaging
- [Microsoft Excel](references/microsoft-excel.md) - Workbooks, worksheets, ranges, tables, charts
- [Microsoft Teams](references/microsoft-teams.md) - Teams, channels, messages, members, chats
- [Microsoft To Do](references/microsoft-to-do.md) - Task lists, tasks, checklist items, linked resources
- [Monday.com](references/monday.md) - Boards, items, columns, groups (GraphQL)
- [Motion](references/motion.md) - Tasks, projects, workspaces, schedules
- [Netlify](references/netlify.md) - Sites, deploys, builds, DNS, environment variables
- [Notion](references/notion.md) - Pages, databases, blocks
- [OneDrive](references/one-drive.md) - Files, folders, drives, sharing
- [Outlook](references/outlook.md) - Mail, calendar, contacts
- [PDF.co](references/pdf-co.md) - PDF conversion, merge, split, edit, text extraction, barcodes
- [Pipedrive](references/pipedrive.md) - Deals, persons, organizations, activities
- [Podio](references/podio.md) - Organizations, workspaces, apps, items, tasks, comments
- [QuickBooks](references/quickbooks.md) - Customers, invoices, reports
- [Quo](references/quo.md) - Calls, messages, contacts, conversations, webhooks
- [Salesforce](references/salesforce.md) - SOQL, sObjects, CRUD
- [SignNow](references/signnow.md) - Documents, templates, invites, e-signatures
- [SendGrid](references/sendgrid.md) - Email sending, contacts, templates, suppressions, statistics
- [Slack](references/slack.md) - Messages, channels, users
- [Snapchat](references/snapchat.md) - Ad accounts, campaigns, ad squads, ads, creatives, audiences
- [Square](references/squareup.md) - Payments, customers, orders, catalog, inventory, invoices
- [Stripe](references/stripe.md) - Customers, subscriptions, payments
- [Systeme.io](references/systeme.md) - Contacts, tags, courses, communities, webhooks
- [Tally](references/tally.md) - Forms, submissions, workspaces, webhooks
- [Telegram](references/telegram.md) - Messages, chats, bots, updates, polls
- [TickTick](references/ticktick.md) - Tasks, projects, task lists
- [Todoist](references/todoist.md) - Tasks, projects, sections, labels, comments
- [Toggl Track](references/toggl-track.md) - Time entries, projects, clients, tags, workspaces
- [Trello](references/trello.md) - Boards, lists, cards, checklists
- [Twilio](references/twilio.md) - SMS, voice calls, phone numbers, messaging
- [Typeform](references/typeform.md) - Forms, responses, insights
- [Vimeo](references/vimeo.md) - Videos, folders, albums, comments, likes
- [WhatsApp Business](references/whatsapp-business.md) - Messages, templates, media
- [WooCommerce](references/woocommerce.md) - Products, orders, customers, coupons
- [WordPress.com](references/wordpress.md) - Posts, pages, sites, users, settings
- [Xero](references/xero.md) - Contacts, invoices, reports
- [YouTube](references/youtube.md) - Videos, playlists, channels, subscriptions
- [Zoho Bigin](references/zoho-bigin.md) - Contacts, companies, pipelines, products
- [Zoho Bookings](references/zoho-bookings.md) - Appointments, services, staff, workspaces
- [Zoho Books](references/zoho-books.md) - Invoices, contacts, bills, expenses
- [Zoho Calendar](references/zoho-calendar.md) - Calendars, events, attendees, reminders
- [Zoho CRM](references/zoho-crm.md) - Leads, contacts, accounts, deals, search
- [Zoho Inventory](references/zoho-inventory.md) - Items, sales orders, invoices, purchase orders, bills
- [Zoho Mail](references/zoho-mail.md) - Messages, folders, labels, attachments
- [Zoho People](references/zoho-people.md) - Employees, departments, designations, attendance, leave
- [Zoho Recruit](references/zoho-recruit.md) - Candidates, job openings, interviews, applications

## Examples

### Slack - Post Message (Native API)

```bash
# Native Slack API: POST https://slack.com/api/chat.postMessage
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'channel': 'C0123456', 'text': 'Hello!'}).encode()
req = urllib.request.Request('https://gateway.maton.ai/slack/api/chat.postMessage', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json; charset=utf-8')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### HubSpot - Create Contact (Native API)

```bash
# Native HubSpot API: POST https://api.hubapi.com/crm/v3/objects/contacts
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'properties': {'email': 'john@example.com', 'firstname': 'John', 'lastname': 'Doe'}}).encode()
req = urllib.request.Request('https://gateway.maton.ai/hubspot/crm/v3/objects/contacts', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Google Sheets - Get Spreadsheet Values (Native API)

```bash
# Native Sheets API: GET https://sheets.googleapis.com/v4/spreadsheets/{id}/values/{range}
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/google-sheets/v4/spreadsheets/122BS1sFN2RKL8AOUQjkLdubzOwgqzPT64KfZ2rvYI4M/values/Sheet1!A1:B2')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Salesforce - SOQL Query (Native API)

```bash
# Native Salesforce API: GET https://{instance}.salesforce.com/services/data/v64.0/query?q=...
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/salesforce/services/data/v64.0/query?q=SELECT+Id,Name+FROM+Contact+LIMIT+10')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Airtable - List Tables (Native API)

```bash
# Native Airtable API: GET https://api.airtable.com/v0/meta/bases/{id}/tables
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/airtable/v0/meta/bases/appgqan2NzWGP5sBK/tables')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Notion - Query Database (Native API)

```bash
# Native Notion API: POST https://api.notion.com/v1/data_sources/{id}/query
python <<'EOF'
import urllib.request, os, json
data = json.dumps({}).encode()
req = urllib.request.Request('https://gateway.maton.ai/notion/v1/data_sources/23702dc5-9a3b-8001-9e1c-000b5af0a980/query', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
req.add_header('Notion-Version', '2025-09-03')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Stripe - List Customers (Native API)

```bash
# Native Stripe API: GET https://api.stripe.com/v1/customers
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/stripe/v1/customers?limit=10')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Code Examples

### JavaScript (Node.js)

```javascript
const response = await fetch('https://gateway.maton.ai/slack/api/chat.postMessage', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${process.env.MATON_API_KEY}`
  },
  body: JSON.stringify({ channel: 'C0123456', text: 'Hello!' })
});
```

### Python

```python
import os
import requests

response = requests.post(
    'https://gateway.maton.ai/slack/api/chat.postMessage',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    json={'channel': 'C0123456', 'text': 'Hello!'}
)
```

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing connection for the requested app |
| 401 | Invalid or missing Maton API key |
| 429 | Rate limited (10 requests/second per account) |
| 500 | Internal Server Error |
| 4xx/5xx | Passthrough error from the target API |

Errors from the target API are passed through with their original status codes and response bodies.

### Troubleshooting: API Key Issues

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

### Troubleshooting: Invalid App Name

1. Verify your URL path starts with the correct app name. The path must begin with `/google-mail/`. For example:

- Correct: `https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages`
- Incorrect: `https://gateway.maton.ai/gmail/v1/users/me/messages`

2. Ensure you have an active connection for the app. List your connections to verify:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=google-mail&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Troubleshooting: Server Error

A 500 error may indicate an expired OAuth token. Try creating a new connection via the Connection Management section above and completing OAuth authorization. If the new connection is "ACTIVE", delete the old connection to ensure the gateway uses the new one.

## Rate Limits

- 10 requests per second per account
- Target API rate limits also apply

## Notes

- When using curl with URLs containing brackets (`fields[]`, `sort[]`, `records[]`), use the `-g` flag to disable glob parsing
- When piping curl output to `jq`, environment variables may not expand correctly in some shells, which can cause "Invalid API key" errors

## Tips

1. **Use native API docs**: Refer to each service's official API documentation for endpoint paths and parameters.

2. **Headers are forwarded**: Custom headers (except `Host` and `Authorization`) are forwarded to the target API.

3. **Query params work**: URL query parameters are passed through to the target API.

4. **All HTTP methods supported**: GET, POST, PUT, PATCH, DELETE are all supported.

5. **QuickBooks special case**: Use `:realmId` in the path and it will be replaced with the connected realm ID.

## Optional

- [Github](https://github.com/maton-ai/api-gateway-skill)
- [API Reference](https://www.maton.ai/docs/api-reference)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
