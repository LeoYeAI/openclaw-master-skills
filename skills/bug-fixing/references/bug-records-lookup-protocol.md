# Bug Records Lookup Protocol (Post-RCA, Pre-Fix)

**Goal**: Prevent repeated mistakes and speed up fixes by reusing proven approaches.

This protocol is **mandatory** after you have a one-sentence **Root Cause** and before you modify code.

---

## 🔴 Knowledge Query Order (MUST Follow)

```
After root cause is confirmed
    │
    ├─ Step 1: Query bug-guide.md (universal pattern library)
    │          └─ Search by error symptom/keyword index
    │
    ├─ Step 2: Query bug-records.md (project history)
    │          └─ Search for similar cases by keywords
    │
    └─ Step 3: Decision
              ├─ Match found → Reuse/adapt existing approach
              └─ No match → Design approach independently
```

> **🔴 Iron Rule**: MUST query first then fix, cannot skip the query and fix directly!

---

## 1) What to Search

Build a small keyword set from your RCA:

- **Error message / user-visible symptom** (exact string if available)
- **Root cause keywords** (e.g., "schema missing field", "artifact file undefined", "base64 heuristic")
- **Primary module/component names** (file name, feature folder, API route)
- **Data shape / contract terms** (request/response fields, payload type)

---

## 2) Where to Search (Order) — MUST Follow Order

### 2.1 First Priority: Universal Pattern Library bug-guide.md

```
@.claude/skills/bug-fixing/references/bug-guide.md
```

**How to search**:
1. Use the quick index table (by error symptom)
2. Browse relevant category sections
3. Search by error keywords

**Match success indicators**:
- Found the same error type
- Fix strategy can be directly applied or slightly adapted

### 2.2 Second Priority: Project History bug-records.md

```
references/bug-records.md       # Current project records
docs/bug-records.md             # Alternative location
```

**How to search**:
1. Search by keywords
2. Filter by category
3. Browse recent fixes in reverse chronological order

### 2.3 Supplementary Resources (For complex issues)

| Resource | Purpose |
|----------|---------|
| `backend-common-issues.md` | Backend API/ORM/performance issues |
| `backend-guide.md` | Backend fix workflows and code patterns |
| `frontend-common-issues.md` | Frontend issue index |

---

## 3) Decision: Reuse or Not

For each candidate record, decide:

- **Reusable as-is**: same root cause and same fix surface
- **Partially reusable**: same root cause but different surface (needs adaptation)
- **Not reusable**: looks similar but different root cause/constraints

When not reusing, write the reason (e.g., "different data model", "different runtime constraints", "behavior changed").

---

## 4) Required Output (Evidence)

Paste this section in your reply **before coding**:

```markdown
## Bug Records Lookup (Post-RCA)
- Search targets:
  - Project: `references/bug-records.md`
  - (Optional) `docs/bug-records.md`
- Keywords used: ["...", "...", "..."]
- Hits:
  - [BUG-XXX] Title — Reuse: Yes/Partial/No — Why: ...
  - [BUG-YYY] Title — Reuse: Yes/Partial/No — Why: ...
- Decision:
  - Reuse plan: (if Yes/Partial) what will be reused and what changes
  - If No hits: state "No relevant records found"
```

---

## 5) After the Fix — Dual Update

### 5.1 Update Project Record (MANDATORY)

Add new entry to `bug-records.md`:

```markdown
## [BUG-NNN] Title

**Date**: YYYY-MM-DD
**Severity**: P1
**Category**: Category

**Symptom**: ...
**Root Cause**: ...
**Fix**: ...
**Verified**: [x] Passed

**Reuse Notes**: Based on BUG-XXX / Referenced bug-guide.md section 7.3
```

### 5.2 Update Universal Pattern Library (If Applicable)

**Decision criteria**: Could this bug pattern occur in other projects?

- **Yes** → Add/update entry in `bug-guide.md`
- **No** → Only update `bug-records.md`

**Content to add to bug-guide.md**:

```markdown
### X.Y Pattern Name

- Symptom: Error message or behavior
- Quick identification: How to confirm this is the issue
- Root Cause: Technical reason
- Fix Strategy: Steps and code examples
- Verification: How to confirm the fix works
- Real Case: BUG-NNN description
```

### 5.3 Link Records

If a previous record was reused:

- Link old record in new record (e.g., "Related bugs: [BUG-XXX]")
- If new fix reveals shortcomings of old approach, update old record

---

## 6) Query Output Template (Complete Version)

```markdown
## Knowledge Base Query Results

### bug-guide.md Query (Universal Pattern Library)
- Search keywords: ["Unknown column", "OperationalError", "model field"]
- Match results:
  - 7.3 Model has field but database lacks column — Match level: High
    - Reusable: Yes
    - Fix strategy: Create Alembic migration to add missing column
- Decision: Execute per section 7.3 approach

### bug-records.md Query (Project History)
- Search keywords: ["meta_data", "chat_sessions", "migration"]
- Match results:
  - No direct match
- Decision: Use bug-guide.md universal approach

### Post-Fix Update Plan
- [x] Update bug-records.md: Added BUG-078
- [x] Update bug-guide.md: Not needed (section 7.3 already covers)
```

---

## 7) Common Query Scenario Quick Reference

| Error Type | Search Keywords | Priority Reference |
|-----------|----------------|-------------------|
| Database column missing | "Unknown column", "OperationalError" | bug-guide.md 7.3 |
| Foreign key constraint failure | "foreign key", "IntegrityError" | bug-guide.md 7.2 |
| Enum mismatch | "LookupError", "enum values" | bug-guide.md 7.1 |
| Schema field missing | "field not updated", "Pydantic" | bug-guide.md 1.4 |
| API timeout | "timeout", "hanging" | bug-guide.md 2.1 |
| Encoding issue | "garbled text", "UTF-8" | bug-guide.md 5.2 |

---

## 8) Query Skip Exceptions

The following scenarios can use a simplified query process:

| Scenario | Handling |
|----------|---------|
| Pure typo/spelling error | Fix directly, simplified record |
| Clear business logic error | Fix per business rules, normal record |
| Duplicate of known bug | Reference old record, don't create duplicate |

**But still MUST**: Update bug-records.md after fix
