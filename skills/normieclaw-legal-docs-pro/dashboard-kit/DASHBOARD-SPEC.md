# Legal Docs Pro — Dashboard Integration Spec

## Overview

Legal Docs Pro integrates with the NormieClaw dashboard to provide a visual overview of document activity, contract risk, and upcoming renewals. The agent populates dashboard tables after each document generation or contract review.

## Table Prefix

All tables use the `ld_` prefix to avoid collisions with other skills.

## Route

Dashboard view is accessible at `/legal-docs` within the NormieClaw dashboard.

## Icon

⚖️ (scales of justice)

## Data Flow

### Document Generation
When the agent generates a legal document:
1. Save the document to `data/documents/` as a markdown file
2. Insert a row into `ld_documents` with: type, title, parties, jurisdiction, status (draft), value, dates, file path
3. If the document has an expiration or renewal date, insert a row into `ld_renewals`
4. For each non-standard clause used, update `ld_clauses` usage count

### Contract Review
When the agent reviews a contract:
1. Optionally save the source to `data/reviews/`
2. Insert a row into `ld_reviews` with: type, title, parties, risk level, flag counts, top concerns, recommendation
3. If renewal tracking is relevant, insert into `ld_renewals`

### Clause Tracking
The `ld_clauses` table tracks which clauses are used most frequently. When the agent uses a clause from the library (standard, protective, or aggressive), it increments the usage count. Custom clauses created for specific deals are also stored here.

## Dashboard Views

### 1. Overview (Default)
Four stat widgets at the top:
- Documents Generated (total count from `ld_documents`)
- Contracts Reviewed (total count from `ld_reviews`)
- High Risk Reviews (count where `overall_risk = "high"`)
- Upcoming Renewals (count where `status = "upcoming"`)

### 2. Document History
Chronological table view of `ld_documents`:
- Columns: Date, Type, Title, Parties, Value, Status
- Sortable by any column
- Filterable by document type and status
- Click to view the full document (opens the markdown file)

### 3. Review Summaries
Table view of `ld_reviews`:
- Columns: Date, Type, Counterparty, Overall Risk, 🟢/🟡/🔴 Flags, Recommendation
- Color-coded risk badges (green/yellow/red)
- Expandable rows showing top concerns and missing protections
- Sortable by risk level and date

### 4. Renewal Calendar
Calendar or list view of `ld_renewals`:
- Shows upcoming renewal and expiration dates
- Color-coded by urgency: green (30+ days), yellow (7-30 days), red (< 7 days or overdue)
- Alert indicator for auto-renewing contracts
- Status toggle: active / upcoming / expired / renewed

### 5. Clause Risk Heatmap
Aggregated view across all reviewed contracts:
- Categories: Indemnification, Liability, IP, Non-Compete, Termination, Confidentiality, Payment, Insurance, Governing Law, Other
- For each category, show distribution of risk flags (how many 🟢, 🟡, 🔴 across all reviews)
- Highlights which clause categories are most frequently flagged as risky
- Helps identify patterns (e.g., "indemnification clauses are flagged 🔴 in 60% of reviewed contracts")

## Agent Responsibilities

The agent is responsible for:
1. Writing to dashboard tables after each generation or review
2. Generating unique IDs for each row (format: `ld_[type]_[timestamp]_[random4]`)
3. Updating renewal statuses when dates pass
4. Incrementing clause usage counts
5. Keeping `updated_at` timestamps current

## Storage

Dashboard data is stored locally alongside the skill's data directory. The dashboard reads from `ld_*` tables via the NormieClaw dashboard framework. No external database or API is required.

---

*See `manifest.json` for the complete table schema and widget definitions.*
