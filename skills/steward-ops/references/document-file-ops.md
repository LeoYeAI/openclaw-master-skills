# Document & File Operations

## Purpose
Digital file management is the unsexy backbone of operational excellence. When files are organized,
named consistently, and easy to find, everything moves faster. When they're scattered, duplicated,
or poorly named, time is wasted every single day searching for things. Steward maintains a clean,
logical, and sustainable file organization system.

---

## File Organization Framework

### The Hierarchy Principle
All files live in a logical hierarchy that maps to how the principal thinks about their work,
not how systems organize by default.

**Top-level structure:**
```
/Business/
  /[Brand or Business Name]/
    /Products/
      /[Product Name]/
        /Listings/
        /Assets/
        /Analytics/
    /Marketing/
      /Campaigns/
      /Templates/
      /Assets/
    /Finance/
      /Invoices/
      /Receipts/
      /Tax/
      /Reports/
    /Operations/
      /SOPs/
      /Checklists/
      /Templates/
    /Legal/
      /Contracts/
      /Compliance/
      /Policies/
    /Communications/
      /Email Templates/
      /Outreach/

/Personal/
  /Finance/
  /Insurance/
  /Medical/
  /Legal/
  /Home/
```

### Naming Conventions
**Files:**
`YYYY-MM-DD_[Category]_[Descriptive-Name]_v[X].[ext]`
Examples:
- `2026-03-21_Invoice_Acme-Corp_March_v1.pdf`
- `2026-03-15_SOP_KDP-Listing-Update_v3.md`
- `2026-Q1_Revenue-Report_v2.xlsx`

**Folders:**
- Use Title Case
- No special characters except hyphens
- Keep names under 30 characters
- Use date prefixes for time-series folders (e.g., `2026-Q1/`)

### Version Control
For documents that go through revisions:
- Always include version number in filename (`_v1`, `_v2`, etc.)
- Keep previous versions in a `/_Archive/` subfolder
- Current version lives in the main folder
- When a document is finalized, rename to `_FINAL` and archive all drafts

---

## File Lifecycle Management

### Retention Policies
| File Type | Retention Period | Archive After | Delete After |
|-----------|-----------------|---------------|-------------|
| Tax documents | 7 years minimum | After filing | Never (7yr legal requirement) |
| Contracts | Duration + 3 years | After expiration | 3 years post-expiration |
| Invoices (paid) | 3 years | After payment | 3 years |
| Receipts | 3 years (tax) | End of tax year | 3 years |
| SOPs | Until superseded | When replaced | 1 year after replacement |
| Marketing assets | Until campaign ends | After campaign | 1 year |
| Analytics reports | 2 years | End of quarter | 2 years |
| Personal documents | Varies | N/A | Never (unless obsolete) |

### Archive Protocol
When archiving files:
1. Move to the `/_Archive/` subfolder within the same directory
2. Add archive date to the filename: `_archived-2026-03-21`
3. Compress if the archive folder exceeds 1 GB
4. Log the archive action for audit trail
5. Verify the file is accessible before removing from active location

### Cleanup Schedule
- **Weekly**: Clear downloads folder, process inbox attachments
- **Monthly**: Review active files for items to archive
- **Quarterly**: Full file audit — check for duplicates, orphans, misplaced files
- **Annually**: Review retention policies, purge expired archives

---

## File Discovery & Search

### When the Principal Asks "Where is...?"
Steward should be able to locate any file by:
1. Searching by name or partial name
2. Searching by content type
3. Searching by date range
4. Searching by category/folder
5. Searching by related project or product
6. Checking recent files and downloads

### File Index Maintenance
Maintain a searchable index of key files:
```
File: [name]
Location: [path]
Type: [document | spreadsheet | image | PDF | presentation | other]
Category: [business | personal | finance | legal | marketing | product]
Related To: [project, product, or context]
Created: [date]
Last Modified: [date]
Status: [active | archived | draft | final]
Tags: [searchable keywords]
```

---

## Backup & Redundancy

### Critical File Identification
Flag files that would cause significant damage if lost:
- Active contracts and agreements
- Tax records and financial documents
- Product source files and assets
- Customer/client data
- Business credentials and access information
- Legal documents and compliance records
- SOPs and operational playbooks

### Backup Verification
Periodically verify that backup systems are working:
- [ ] Cloud backup is active and current
- [ ] Last backup completed successfully on [date]
- [ ] Critical files are included in the backup set
- [ ] Backup can be restored (periodic test)
- [ ] Multiple backup copies exist (3-2-1 rule: 3 copies, 2 media, 1 offsite)

---

## Access & Permission Management

### File Access Audit
Periodically review who has access to what:
- Shared documents: Who has view/edit access? Is it still appropriate?
- Shared folders: Are permissions correctly scoped?
- External sharing: Are any files shared outside the organization?
- Expired sharing: Are there old share links that should be revoked?

### Sensitive File Handling
Files containing sensitive information need extra care:
- Financial records: Restricted access, encrypted storage
- Client data: Access logged, sharing restricted
- Credentials: Never stored in plain text, use a password manager
- Legal documents: Access restricted, version controlled
- Personal information: Segregated from business files

---

## Document Creation & Management Templates

### Standard Document Types and Their Homes
| Document Type | Template Location | Save To | Naming Pattern |
|--------------|------------------|---------|----------------|
| Invoice | /Templates/invoice-template | /Finance/Invoices/[Year]/ | YYYY-MM-DD_Invoice_[Client] |
| Contract | /Templates/contract-template | /Legal/Contracts/ | YYYY-MM-DD_Contract_[Party] |
| SOP | /Templates/sop-template | /Operations/SOPs/ | SOP_[Process-Name]_v[X] |
| Report | /Templates/report-template | /[Relevant folder]/ | YYYY-MM_Report_[Topic] |
| Meeting notes | /Templates/meeting-template | /Operations/Meetings/ | YYYY-MM-DD_Meeting_[Topic] |
