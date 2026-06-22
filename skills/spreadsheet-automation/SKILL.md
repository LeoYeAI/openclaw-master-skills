---
name: spreadsheet-automation
description: Turn Google Sheets into a powerful database and workflow engine using formulas, Apps Script, and integrations. Use when building systems in Sheets, automating data entry, creating dashboards, or replacing expensive tools with spreadsheet-based solutions. Covers advanced formulas, Apps Script basics, integration strategies, and real workflow examples. Trigger on "automate spreadsheet", "Google Sheets automation", "Apps Script", "spreadsheet workflow", "Sheets as database", "automate data entry".
---

# Spreadsheet Automation

## Overview
Google Sheets isn't just for budgets and lists. With the right formulas, Apps Script, and integrations, it becomes a database, CRM, project tracker, analytics dashboard, and workflow engine — all in one free tool. This playbook shows you how to build production-grade systems in Sheets that replace $50-500/month SaaS tools.

---

## Step 1: Identify What to Automate in Sheets

Not every workflow belongs in Sheets. Here's when Sheets is the right tool.

**Good use cases for Sheets automation:**
- **Data collection from multiple sources** (form responses, API data, manual input) → centralize in one place
- **Lightweight databases** (customer lists, inventory, project tracker) → under 10K rows, basic relationships
- **Dashboards and reporting** (pull data from other tools, visualize, share)
- **Workflow triggers** (when row added/updated → send email, create task, update another sheet)
- **Data transformation** (clean, format, enrich data from messy sources)

**Bad use cases (use a real database or tool instead):**
- Heavy computation (millions of rows, complex queries) → use BigQuery, Airtable, or SQL database
- Real-time collaboration with 10+ concurrent users → use Airtable, Notion, or dedicated project management tool
- Mission-critical data that can't afford accidental deletion → use a real database with backups and version control
- Complex relational data (many-to-many relationships) → use Airtable or proper database

**Audit your current manual work (10 min):**
1. List tasks you do in Sheets manually (copy/paste, data entry, formatting, updating other sheets)
2. Which tasks are repetitive? (daily, weekly, triggered by an event)
3. Which tasks take 5+ minutes each time?
4. Which tasks have clear logic? ("If this, then that")

**Low-hanging fruit checklist:**
- [ ] Auto-populate cells based on other cells (formulas)
- [ ] Pull data from external sources (APIs, other sheets, web scraping)
- [ ] Auto-format or clean data (remove duplicates, standardize dates, extract values)
- [ ] Send notifications when conditions are met (email alerts, Slack messages)
- [ ] Create charts or dashboards that update automatically
- [ ] Sync data between Sheets and other tools (CRM, project management, accounting)

---

## Step 2: Master Advanced Formulas (No Code Required)

Most Sheets automation starts here. Master these formulas and you can build 80% of what you need without Apps Script.

### Core Formula Reference

**QUERY (SQL-like queries in Sheets):**
```
=QUERY(A1:D100, "SELECT A, B, C WHERE D > 1000 ORDER BY C DESC")
```
- Use for: Filter, sort, group, and summarize data
- Syntax: `SELECT [columns] WHERE [condition] ORDER BY [column] LIMIT [number]`
- Example: Pull all customers with orders > $1,000, sorted by date

**IMPORTRANGE (pull data from other sheets):**
```
=IMPORTRANGE("spreadsheet_url", "Sheet1!A1:D100")
```
- Use for: Centralize data from multiple sheets into one master sheet
- Setup: First time, you need to approve access (click "Allow access" when prompted)
- Example: Pull sales data from regional team sheets into one master dashboard

**ARRAYFORMULA (apply formula to entire column):**
```
=ARRAYFORMULA(IF(A2:A="",,B2:B*C2:C))
```
- Use for: Auto-calculate for all rows (no dragging formulas down)
- Example: Auto-multiply quantity × price for every new row added

**VLOOKUP / XLOOKUP (lookup values from another table):**
```
=VLOOKUP(A2, Sheet2!A:B, 2, FALSE)
```
- Use for: Match and pull related data (e.g., customer name → pull their email)
- XLOOKUP (newer): More flexible, can search left-to-right or right-to-left

**FILTER (dynamic filtering):**
```
=FILTER(A2:D100, D2:D100>1000, C2:C100="Active")
```
- Use for: Show only rows that meet criteria (updates automatically when data changes)
- Example: Show only active customers with revenue > $1,000

**UNIQUE (remove duplicates):**
```
=UNIQUE(A2:A100)
```
- Use for: Extract unique values from a list (auto-updates when source changes)

**REGEXEXTRACT (extract patterns from text):**
```
=REGEXEXTRACT(A2, "[0-9]{3}-[0-9]{3}-[0-9]{4}")
```
- Use for: Pull phone numbers, emails, URLs, or any pattern from messy text
- Example: Extract domain from email addresses

**IMPORTXML / IMPORTHTML (scrape web data):**
```
=IMPORTXML("https://example.com", "//h1")
```
- Use for: Pull live data from websites (prices, headlines, tables)
- Example: Track competitor pricing automatically

---

## Step 3: Build Multi-Sheet Systems

Single-sheet solutions are limited. Real power comes from connecting multiple sheets into a system.

**System architecture pattern:**

```
SHEET 1: Data Entry (input form or manual entry)
  ↓
SHEET 2: Master Database (cleaned, validated, enriched)
  ↓
SHEET 3: Dashboard (charts, summaries, insights)
  ↓
SHEET 4: Exports/Reports (formatted for sharing)
```

**Example: Simple CRM in Sheets**

**Sheet 1: Lead Entry Form**
- Columns: Name, Email, Company, Source, Date Added
- Use: Google Form → auto-populates this sheet
- Validation: Email format check, required fields

**Sheet 2: Master Lead Database**
- Pulls from Sheet 1 using `IMPORTRANGE` or direct reference
- Adds enrichment: Status (New/Contacted/Qualified/Closed), Last Contact Date, Notes
- Formula example: `=IF(ISBLANK(D2), "New", D2)` (auto-set status to "New" if empty)

**Sheet 3: Dashboard**
- Total leads: `=COUNTA(MasterDB!A2:A)`
- Leads this week: `=COUNTIF(MasterDB!E2:E, ">="&TODAY()-7)`
- Conversion rate: `=COUNTIF(MasterDB!D2:D, "Closed")/COUNTA(MasterDB!A2:A)`
- Chart: Leads by source (pie chart)

**Sheet 4: Weekly Report**
- Formula: `=FILTER(MasterDB!A2:E, MasterDB!E2:E>=TODAY()-7)`
- Auto-pull this week's leads for review meeting

**Key principles:**
- One sheet = one purpose (don't mix input, storage, and display)
- Use formulas to connect sheets (avoid manual copy/paste)
- Protect important sheets (prevent accidental edits)

---

## Step 4: Learn Apps Script Basics (Google's JavaScript for Sheets)

Apps Script lets you do things formulas can't: send emails, make API calls, create custom menus, run code on a schedule.

**When to use Apps Script:**
- Formulas can't do it (sending emails, hitting APIs, complex logic)
- You need automation to run on a schedule (every hour, daily, weekly)
- You want custom functions or menu items

**How to access Apps Script:**
1. Open your Google Sheet
2. Extensions → Apps Script
3. Write code in the editor

### Example 1: Send Email Alert When New Row Added

```javascript
function onEdit(e) {
  var sheet = e.source.getActiveSheet();
  
  // Only run on "Lead Entry" sheet
  if (sheet.getName() !== "Lead Entry Form") return;
  
  // Get edited row and column
  var row = e.range.getRow();
  var col = e.range.getColumn();
  
  // If new row added (row > 1 to skip header)
  if (row > 1 && col === 1) {
    var name = sheet.getRange(row, 1).getValue();
    var email = sheet.getRange(row, 2).getValue();
    
    // Send email notification
    MailApp.sendEmail({
      to: "you@example.com",
      subject: "New Lead: " + name,
      body: "Name: " + name + "\nEmail: " + email
    });
  }
}
```

**How to set up:**
1. Paste code into Apps Script editor
2. Save (Ctrl/Cmd + S)
3. Set up trigger: Triggers (clock icon) → Add Trigger → `onEdit` → From spreadsheet → On edit → Save
4. Authorize permissions when prompted

### Example 2: Fetch Data from API and Write to Sheet

```javascript
function fetchAPIData() {
  var url = "https://api.example.com/data";
  var options = {
    "method": "GET",
    "headers": {
      "Authorization": "Bearer YOUR_API_KEY"
    }
  };
  
  var response = UrlFetchApp.fetch(url, options);
  var data = JSON.parse(response.getContentText());
  
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("API Data");
  
  // Clear existing data
  sheet.clear();
  
  // Write headers
  sheet.appendRow(["ID", "Name", "Value"]);
  
  // Write data rows
  data.forEach(function(item) {
    sheet.appendRow([item.id, item.name, item.value]);
  });
}
```

**How to set up:**
1. Paste code, replace `url` and `YOUR_API_KEY`
2. Run once manually to test (click Run button)
3. Set up time-based trigger: Triggers → Add Trigger → `fetchAPIData` → Time-driven → Hour timer → Every hour

### Example 3: Auto-Archive Old Rows

```javascript
function archiveOldRows() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sourceSheet = ss.getSheetByName("Active Tasks");
  var archiveSheet = ss.getSheetByName("Archive");
  
  var data = sourceSheet.getDataRange().getValues();
  var today = new Date();
  var cutoffDate = new Date(today.getTime() - (30 * 24 * 60 * 60 * 1000)); // 30 days ago
  
  // Start from row 2 (skip header)
  for (var i = data.length - 1; i >= 1; i--) {
    var rowDate = new Date(data[i][3]); // Column D = date
    
    if (rowDate < cutoffDate) {
      // Copy row to archive
      archiveSheet.appendRow(data[i]);
      
      // Delete from source
      sourceSheet.deleteRow(i + 1);
    }
  }
}
```

**Common Apps Script patterns:**
- **Get data:** `sheet.getRange("A1:D10").getValues()`
- **Write data:** `sheet.getRange("A1").setValue("Hello")`
- **Append row:** `sheet.appendRow([val1, val2, val3])`
- **Send email:** `MailApp.sendEmail(to, subject, body)`
- **Make HTTP request:** `UrlFetchApp.fetch(url, options)`
- **Get current date:** `new Date()`

**Apps Script resources:**
- Official docs: https://developers.google.com/apps-script
- ChatGPT or Claude: "Write Apps Script to [do X]" → copy/paste/test

---

## Step 5: Connect Sheets to Other Tools (Zapier, Make, n8n)

Sheets becomes 10x more powerful when integrated with other tools.

**Integration strategies:**

### Strategy 1: Sheets as Database (write-only)
Use case: Collect data from forms, webhooks, or other tools → write to Sheets for storage

**Example workflow (Zapier/Make):**
```
TRIGGER: New Typeform submission
ACTION 1: Add row to Google Sheets
ACTION 2: Send email confirmation (optional)
```

**Example workflow (Webhook → Sheets):**
```
TRIGGER: Webhook received (from website, Stripe, etc.)
ACTION: Parse JSON → Write to Google Sheets
```

### Strategy 2: Sheets as Trigger (read-only)
Use case: When row added/updated in Sheets → trigger action elsewhere

**Example workflow:**
```
TRIGGER: New row in Google Sheets (check every 15 min)
CONDITION: Status column = "Approved"
ACTION: Create task in Asana / Send email / Post to Slack
```

### Strategy 3: Sheets as Middleman (read + write)
Use case: Sheets pulls data from Tool A, processes it, pushes to Tool B

**Example workflow (sync CRM to email tool):**
```
TRIGGER: New row in Google Sheets (CRM export)
CONDITION: Email column not empty + Tag column = "Newsletter"
ACTION: Add contact to ConvertKit / Mailchimp
```

**Best tools for Sheets integration:**
- **Zapier:** Easiest, widest app support, $20-50/month
- **Make (Integromat):** More powerful, visual, $9-30/month
- **n8n:** Self-hosted, unlimited, free (or $20/month hosted)

**Common integrations:**
- Google Forms → Sheets (native, no tool needed)
- Sheets → Gmail (send emails based on Sheet data)
- Sheets → Slack (post updates to Slack when Sheet changes)
- Sheets ↔ Airtable (sync data both ways)
- API → Sheets (pull data from any API into Sheets)

---

## Step 6: Real-World Automation Examples

### Example 1: Automated Invoice Tracker

**Problem:** Manually tracking invoices sent, paid, and overdue

**Solution:**

**Sheet 1: Invoice Log**
- Columns: Invoice #, Client, Amount, Date Sent, Due Date, Status, Days Overdue

**Formula magic:**
```
Status = =IF(G2="Paid", "Paid", IF(E2<TODAY(), "Overdue", "Pending"))
Days Overdue = =IF(E2<TODAY(), TODAY()-E2, 0)
```

**Apps Script (run daily):**
```javascript
function sendOverdueReminders() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Invoice Log");
  var data = sheet.getDataRange().getValues();
  
  for (var i = 1; i < data.length; i++) {
    var status = data[i][6]; // Status column
    var client = data[i][1];
    var invoiceNum = data[i][0];
    var amount = data[i][2];
    
    if (status === "Overdue") {
      MailApp.sendEmail({
        to: "client@example.com",
        subject: "Reminder: Invoice " + invoiceNum + " Overdue",
        body: "Hi " + client + ",\n\nInvoice " + invoiceNum + " for $" + amount + " is overdue. Please remit payment.\n\nThank you!"
      });
    }
  }
}
```

**Trigger:** Time-driven, daily at 9am

---

### Example 2: Lead Scoring System

**Problem:** Manually qualifying leads based on fit

**Solution:**

**Sheet 1: Lead Data**
- Columns: Name, Company Size, Industry, Budget, Urgency, Score, Priority

**Formula scoring:**
```
Score = =
  IF(B2="Enterprise", 30, IF(B2="Mid-Market", 20, 10)) +
  IF(C2="SaaS", 20, IF(C2="E-commerce", 15, 5)) +
  IF(D2>10000, 30, IF(D2>5000, 20, 10)) +
  IF(E2="Immediate", 20, IF(E2="This Quarter", 10, 0))

Priority = =IF(F2>=70, "Hot", IF(F2>=50, "Warm", "Cold"))
```

**Automation (Zapier):**
```
TRIGGER: New row in Google Sheets
CONDITION: Priority = "Hot"
ACTION 1: Add to Pipedrive as high-priority deal
ACTION 2: Send Slack notification to sales team
```

---

### Example 3: Content Calendar + Auto-Publishing

**Problem:** Manually tracking and scheduling social posts

**Solution:**

**Sheet 1: Content Calendar**
- Columns: Date, Platform, Post Text, Image URL, Status

**Apps Script (run hourly):**
```javascript
function publishScheduledPosts() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Content Calendar");
  var data = sheet.getDataRange().getValues();
  var now = new Date();
  
  for (var i = 1; i < data.length; i++) {
    var scheduleDate = new Date(data[i][0]);
    var status = data[i][4];
    
    // If scheduled for now or past, and not yet published
    if (scheduleDate <= now && status === "Scheduled") {
      var platform = data[i][1];
      var text = data[i][2];
      
      // Call API to post (Twitter, LinkedIn, etc.)
      postToAPI(platform, text);
      
      // Mark as published
      sheet.getRange(i+1, 5).setValue("Published");
    }
  }
}

function postToAPI(platform, text) {
  // Example: Twitter API call
  var url = "https://api.twitter.com/2/tweets";
  var payload = JSON.stringify({"text": text});
  var options = {
    "method": "POST",
    "headers": {
      "Authorization": "Bearer YOUR_TWITTER_TOKEN",
      "Content-Type": "application/json"
    },
    "payload": payload
  };
  
  UrlFetchApp.fetch(url, options);
}
```

---

## Step 7: Performance and Scalability

**When Sheets starts to slow down:**

**Problem:** Sheet with 10K+ rows, complex formulas → slow to load/edit

**Solutions:**
1. **Use QUERY instead of FILTER + SORT:** More efficient
2. **Limit ARRAYFORMULA range:** `A2:A1000` instead of `A:A` (entire column)
3. **Use static values instead of formulas where possible:** Copy → Paste Values
4. **Split into multiple sheets:** Archive old data to separate sheet
5. **Use Importrange sparingly:** Each call adds load time
6. **Cache data with Apps Script:** Pull external data once, store it, refresh periodically instead of live formulas

**When to migrate away from Sheets:**
- 50K+ rows → Use Airtable or BigQuery
- Real-time collaboration with 20+ users → Use Airtable or Notion
- Complex relational queries → Use Airtable or SQL database
- Mission-critical data → Use proper database with backups

**Backup strategy:**
- **Version history:** File → Version history (Google auto-saves, you can restore)
- **Automated exports:** Apps Script to export to Google Drive weekly
- **Download copies:** File → Download → Excel or CSV (manual backup)

---

## Step 8: Spreadsheet Automation ROI

**ROI calculation:**

```
Time Saved per Month (hours) = (Minutes per task / 60) × Frequency per month
Monthly Value = Time Saved × Hourly Rate
Setup Cost = (Setup time in hours × Hourly Rate) + Tool costs
Payback Period (months) = Setup Cost / Monthly Value

If payback period < 3 months → Definitely worth it
If payback period > 6 months → Probably not worth it
```

**Example:**
```
Task: Manually entering form submissions into CRM (15 min, 40x/month = 10 hours/month saved)
Your hourly rate: $50/hour
Monthly value saved: $500
Setup time: 2 hours
Setup cost: $100 (time) + $0 (Google Forms + Sheets are free)
Payback: $100 / $500 = 0.2 months → Absolutely worth it
```

**Rule:** If it saves 5+ hours/month, automate it.

---

## Spreadsheet Automation Mistakes to Avoid
- **Building everything in one massive sheet.** Break into multiple sheets (input, database, dashboard, exports).
- **Not protecting important sheets.** One accidental delete can wipe out your system. Use Data → Protect sheets and ranges.
- **Overusing volatile formulas.** `NOW()`, `TODAY()`, `RAND()` recalculate constantly and slow down sheets. Use sparingly.
- **Not documenting your formulas.** Add comments (right-click cell → Insert comment) to explain complex formulas.
- **Forgetting to set up triggers for Apps Script.** Code won't run unless you set up a trigger (onEdit, time-driven, etc.).
- **Not testing automations before going live.** Test with dummy data first. A broken automation that sends 100 emails is a disaster.
- **Using Sheets for things it's not meant for.** If you hit 20K+ rows, move to a real database.
