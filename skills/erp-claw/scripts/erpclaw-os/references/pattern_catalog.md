# ERPClaw OS Pattern Catalog

Reusable patterns extracted from the existing 44-module codebase. Each pattern documents a common business entity type with schema, action, and test templates. Used by `generate_module.py` to map natural-language business descriptions to code templates.

**Source of truth:** `pattern_library.py` defines the machine-readable version. This document is the human-readable reference.

---

## 1. CRUD Entity

**Description:** The foundational pattern. A persistent business entity with create, read, update, and list operations. No financial posting, no lifecycle transitions beyond active/inactive.

**Source modules:** legalclaw (`legalclaw_client_ext`), healthclaw-vet (`healthclaw_animal_patient`), automotiveclaw (`automotiveclaw_customer_ext`), nonprofitclaw (`nonprofitclaw_donor_ext`)

**When to use:**
- Any entity that needs to be stored and queried (clients, pets, vehicles, properties, employees, locations)
- Master data tables that other records reference
- Extension tables that augment core ERP entities (customer, item, employee)

**Schema pattern:**
```sql
CREATE TABLE IF NOT EXISTS {prefix}_entity (
    id          TEXT PRIMARY KEY,            -- UUID4
    company_id  TEXT NOT NULL REFERENCES company(id),
    name        TEXT NOT NULL,
    status      TEXT DEFAULT 'active'
                CHECK(status IN ('active','inactive','archived')),
    notes       TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_{prefix}_entity_company
    ON {prefix}_entity(company_id);
```

For **extension tables** that link to a core entity:
```sql
CREATE TABLE IF NOT EXISTS {prefix}_customer_ext (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT DEFAULT '{PREFIX}-',
    customer_id     TEXT NOT NULL REFERENCES customer(id),
    -- domain-specific fields here --
    is_active       INTEGER DEFAULT 1,
    company_id      TEXT NOT NULL REFERENCES company(id),
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_{prefix}_customer_ext_customer
    ON {prefix}_customer_ext(customer_id);
```

**Action pattern:**
```python
def handle_add_entity(args, conn):
    entity_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO {prefix}_entity (id, company_id, name) VALUES (?, ?, ?)",
        (entity_id, args.company_id, args.name)
    )
    conn.commit()
    ok({"message": "Entity added", "id": entity_id})

def handle_update_entity(args, conn):
    conn.execute(
        "UPDATE {prefix}_entity SET name = ?, updated_at = datetime('now') WHERE id = ? AND company_id = ?",
        (args.name, args.id, args.company_id)
    )
    conn.commit()
    ok({"message": "Entity updated"})

def handle_get_entity(args, conn):
    row = conn.execute(
        "SELECT * FROM {prefix}_entity WHERE id = ? AND company_id = ?",
        (args.id, args.company_id)
    ).fetchone()
    if not row:
        return err("Entity not found")
    ok(dict(row))

def handle_list_entities(args, conn):
    rows = conn.execute(
        "SELECT * FROM {prefix}_entity WHERE company_id = ? ORDER BY created_at DESC",
        (args.company_id,)
    ).fetchall()
    ok({"entities": [dict(r) for r in rows], "count": len(rows)})
```

**Test pattern:**
```python
def test_add_entity(db_conn, company_id):
    result = run_action("add-entity", name="Test", company_id=company_id)
    assert result["id"]
    row = db_conn.execute("SELECT * FROM {prefix}_entity WHERE id = ?", (result["id"],)).fetchone()
    assert row["name"] == "Test"

def test_list_entities_empty(db_conn, company_id):
    result = run_action("list-entities", company_id=company_id)
    assert result["count"] == 0

def test_update_entity(db_conn, company_id):
    add_result = run_action("add-entity", name="Old", company_id=company_id)
    run_action("update-entity", id=add_result["id"], name="New", company_id=company_id)
    row = db_conn.execute("SELECT name FROM {prefix}_entity WHERE id = ?", (add_result["id"],)).fetchone()
    assert row["name"] == "New"
```

---

## 2. Appointment/Booking

**Description:** A scheduled event with date/time, status lifecycle (scheduled -> confirmed -> in_progress -> completed | cancelled), and association to both a service provider and a client/patient/pet.

**Source modules:** healthclaw (`healthclaw_appointment`), healthclaw-vet (via healthclaw appointments), groomingclaw (`groomingclaw_appointment`)

**When to use:**
- Any business that schedules time-bound events (medical visits, grooming sessions, inspections, consultations)
- When you need to track appointment status transitions and prevent double-booking

**Schema pattern:**
```sql
CREATE TABLE IF NOT EXISTS {prefix}_appointment (
    id              TEXT PRIMARY KEY,
    company_id      TEXT NOT NULL REFERENCES company(id),
    customer_id     TEXT NOT NULL REFERENCES customer(id),
    -- optional link to domain entity (pet, patient, vehicle, property) --
    entity_id       TEXT REFERENCES {prefix}_entity(id),
    provider_id     TEXT,                   -- staff/practitioner ID
    date            TEXT NOT NULL,           -- ISO-8601 date
    start_time      TEXT,                    -- HH:MM
    end_time        TEXT,                    -- HH:MM
    appointment_type TEXT,
    status          TEXT NOT NULL DEFAULT 'scheduled'
                    CHECK(status IN ('scheduled','confirmed','in_progress',
                                     'completed','cancelled','no_show')),
    notes           TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_{prefix}_appointment_company
    ON {prefix}_appointment(company_id);
CREATE INDEX IF NOT EXISTS idx_{prefix}_appointment_date
    ON {prefix}_appointment(date);
CREATE INDEX IF NOT EXISTS idx_{prefix}_appointment_status
    ON {prefix}_appointment(status);
```

**Action pattern:**
```python
def handle_add_appointment(args, conn):
    appt_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO {prefix}_appointment
           (id, company_id, customer_id, date, start_time, status)
           VALUES (?, ?, ?, ?, ?, 'scheduled')""",
        (appt_id, args.company_id, args.customer_id, args.date, args.start_time)
    )
    conn.commit()
    ok({"message": "Appointment scheduled", "id": appt_id})

def handle_update_appointment(args, conn):
    # Only allow updates when status is 'scheduled' or 'confirmed'
    row = conn.execute(
        "SELECT status FROM {prefix}_appointment WHERE id = ? AND company_id = ?",
        (args.id, args.company_id)
    ).fetchone()
    if not row:
        return err("Appointment not found")
    if row["status"] not in ("scheduled", "confirmed"):
        return err(f"Cannot update appointment in '{row['status']}' status")
    # ... perform update ...
```

**Test pattern:**
```python
def test_add_appointment(db_conn, company_id, customer_id):
    result = run_action("add-appointment", company_id=company_id,
                        customer_id=customer_id, date="2026-04-01")
    assert result["id"]
    row = db_conn.execute("SELECT status FROM {prefix}_appointment WHERE id = ?",
                          (result["id"],)).fetchone()
    assert row["status"] == "scheduled"

def test_cannot_update_completed_appointment(db_conn, company_id):
    # Setup: create and complete an appointment
    # Assert: update attempt returns error
```

---

## 3. Service Record

**Description:** A record of work performed, linked to an entity (patient, pet, vehicle) and optionally to an appointment. Captures service type, description, and amount charged.

**Source modules:** healthclaw-vet (via treatment records), automotiveclaw (service records), groomingclaw (grooming records)

**When to use:**
- When work is performed and needs to be documented (treatments, repairs, inspections, cleanings)
- Often linked to both an appointment and an entity being serviced

**Schema pattern:**
```sql
CREATE TABLE IF NOT EXISTS {prefix}_service_record (
    id              TEXT PRIMARY KEY,
    company_id      TEXT NOT NULL REFERENCES company(id),
    entity_id       TEXT NOT NULL REFERENCES {prefix}_entity(id),
    appointment_id  TEXT REFERENCES {prefix}_appointment(id),
    service_type    TEXT NOT NULL,
    description     TEXT,
    amount          TEXT DEFAULT '0',       -- TEXT for Decimal precision
    performed_by    TEXT,                    -- staff/practitioner
    performed_date  TEXT NOT NULL DEFAULT (date('now')),
    notes           TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
```

**Action pattern:**
```python
def handle_add_service_record(args, conn):
    record_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO {prefix}_service_record
           (id, company_id, entity_id, service_type, amount, description)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (record_id, args.company_id, args.entity_id,
         args.service_type, args.amount or "0", args.description)
    )
    conn.commit()
    ok({"message": "Service record added", "id": record_id})
```

**Test pattern:**
```python
def test_add_service_record(db_conn, company_id, entity_id):
    result = run_action("add-service-record", company_id=company_id,
                        entity_id=entity_id, service_type="bath",
                        amount="45.00")
    assert result["id"]
    row = db_conn.execute("SELECT amount FROM {prefix}_service_record WHERE id = ?",
                          (result["id"],)).fetchone()
    assert Decimal(row["amount"]) == Decimal("45.00")
```

---

## 4. Invoice Delegation (cross_skill Billing)

**Description:** The correct way for non-core modules to create financial documents. Uses `cross_skill.create_invoice()` or `cross_skill.call_skill_action()` to delegate to the core billing engine. Never directly writes to `gl_entry`, `sales_invoice`, or `payment_entry`.

**Source modules:** groomingclaw, tattooclaw, storageclaw (all PoC modules use this pattern)

**When to use:**
- Any time a vertical module needs to generate an invoice, process a payment, or trigger GL postings
- Constitution Article 6 mandates this: no direct GL writes allowed

**Schema pattern:**
No additional tables needed -- the module creates line items in its own tables and delegates the invoice creation to core ERP.

**Action pattern:**
```python
from erpclaw_lib.cross_skill import create_invoice

def handle_create_invoice(args, conn):
    # 1. Gather billable items from module's own tables
    records = conn.execute(
        "SELECT * FROM {prefix}_service_record WHERE appointment_id = ? AND status = 'completed'",
        (args.appointment_id,)
    ).fetchall()

    if not records:
        return err("No billable records found")

    # 2. Build invoice lines
    items = []
    for r in records:
        items.append({
            "description": r["service_type"],
            "qty": 1,
            "rate": r["amount"],
        })

    # 3. Delegate to core billing via cross_skill
    invoice_result = create_invoice(
        conn=conn,
        company_id=args.company_id,
        customer_id=args.customer_id,
        items=items,
        posting_date=date.today().isoformat(),
    )

    ok({"message": "Invoice created", "invoice_id": invoice_result["id"]})
```

**Test pattern:**
```python
def test_create_invoice_delegates(db_conn, company_id, customer_id, mocker):
    mock_create = mocker.patch("erpclaw_lib.cross_skill.create_invoice",
                                return_value={"id": "inv-001"})
    result = run_action("create-invoice", company_id=company_id,
                        customer_id=customer_id, appointment_id="apt-1")
    mock_create.assert_called_once()
    assert result["invoice_id"] == "inv-001"
```

---

## 5. Compliance/Licensing

**Description:** Tracks certifications, licenses, inspections, and compliance records with expiry dates and renewal workflows. Commonly paired with alerts for upcoming expirations.

**Source modules:** legalclaw (`legalclaw_bar_admission`, `legalclaw_cle_record`), tattooclaw (health inspections), constructclaw (permits, certifications)

**When to use:**
- Any business that requires professional licenses (legal, medical, construction)
- Regulatory compliance tracking (inspections, audits, certifications)
- When expiry dates trigger renewal workflows

**Schema pattern:**
```sql
CREATE TABLE IF NOT EXISTS {prefix}_license (
    id              TEXT PRIMARY KEY,
    company_id      TEXT NOT NULL REFERENCES company(id),
    holder_id       TEXT NOT NULL,           -- employee, practitioner, or entity
    license_type    TEXT NOT NULL,
    license_number  TEXT,
    jurisdiction    TEXT,
    issue_date      TEXT NOT NULL,
    expiry_date     TEXT,
    status          TEXT DEFAULT 'active'
                    CHECK(status IN ('active','expired','suspended','revoked','pending')),
    notes           TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_{prefix}_license_expiry
    ON {prefix}_license(expiry_date);
CREATE INDEX IF NOT EXISTS idx_{prefix}_license_status
    ON {prefix}_license(status);
```

**Action pattern:**
```python
def handle_add_license(args, conn):
    license_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO {prefix}_license
           (id, company_id, holder_id, license_type, license_number,
            issue_date, expiry_date)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (license_id, args.company_id, args.holder_id, args.license_type,
         args.license_number, args.issue_date, args.expiry_date)
    )
    conn.commit()
    ok({"message": "License added", "id": license_id})

def handle_check_expiring(args, conn):
    """List licenses expiring within N days."""
    rows = conn.execute(
        """SELECT * FROM {prefix}_license
           WHERE company_id = ? AND status = 'active'
             AND expiry_date <= date('now', '+' || ? || ' days')
           ORDER BY expiry_date""",
        (args.company_id, args.days or 30)
    ).fetchall()
    ok({"expiring": [dict(r) for r in rows], "count": len(rows)})
```

**Test pattern:**
```python
def test_add_license(db_conn, company_id):
    result = run_action("add-license", company_id=company_id,
                        holder_id="emp-1", license_type="bar_admission",
                        issue_date="2025-01-01", expiry_date="2027-01-01")
    assert result["id"]

def test_check_expiring_finds_upcoming(db_conn, company_id):
    # Add a license expiring in 10 days
    run_action("add-license", ..., expiry_date=ten_days_from_now)
    result = run_action("check-expiring", company_id=company_id, days=30)
    assert result["count"] >= 1
```

---

## 6. Prepaid Package (Credit Balance)

**Description:** A bundle of prepaid sessions or credits that a customer purchases upfront and uses over time. Tracks total sessions, used sessions, and remaining balance. Packages expire or become exhausted.

**Source modules:** groomingclaw (`groomingclaw_package`, `groomingclaw_package_usage`), erpclaw-billing (prepaid credits)

**When to use:**
- Prepaid service bundles (10-pack of sessions, monthly retainer hours)
- Gift cards or service credits
- Membership tiers with included services

**Schema pattern:**
```sql
CREATE TABLE IF NOT EXISTS {prefix}_package (
    id              TEXT PRIMARY KEY,
    company_id      TEXT NOT NULL REFERENCES company(id),
    customer_id     TEXT NOT NULL REFERENCES customer(id),
    package_type    TEXT NOT NULL,
    total_sessions  INTEGER NOT NULL,
    used_sessions   INTEGER NOT NULL DEFAULT 0,
    amount          TEXT DEFAULT '0',        -- purchase price
    purchase_date   TEXT DEFAULT (date('now')),
    expiry_date     TEXT,
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK(status IN ('active','exhausted','expired','cancelled')),
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS {prefix}_package_usage (
    id              TEXT PRIMARY KEY,
    package_id      TEXT NOT NULL REFERENCES {prefix}_package(id),
    used_date       TEXT NOT NULL DEFAULT (date('now')),
    notes           TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
```

**Action pattern:**
```python
def handle_use_session(args, conn):
    pkg = conn.execute(
        "SELECT * FROM {prefix}_package WHERE id = ? AND company_id = ?",
        (args.package_id, args.company_id)
    ).fetchone()
    if not pkg:
        return err("Package not found")
    if pkg["status"] != "active":
        return err(f"Package is {pkg['status']}")
    if pkg["used_sessions"] >= pkg["total_sessions"]:
        return err("Package exhausted")

    new_used = pkg["used_sessions"] + 1
    new_status = "exhausted" if new_used >= pkg["total_sessions"] else "active"

    conn.execute("BEGIN")
    conn.execute(
        "UPDATE {prefix}_package SET used_sessions = ?, status = ?, updated_at = datetime('now') WHERE id = ?",
        (new_used, new_status, args.package_id)
    )
    usage_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO {prefix}_package_usage (id, package_id) VALUES (?, ?)",
        (usage_id, args.package_id)
    )
    conn.execute("COMMIT")
    ok({"remaining": pkg["total_sessions"] - new_used, "status": new_status})
```

**Test pattern:**
```python
def test_use_session_decrements(db_conn, package_id, company_id):
    result = run_action("use-session", package_id=package_id, company_id=company_id)
    assert result["remaining"] == 9  # if total was 10

def test_use_session_exhausts_package(db_conn, company_id):
    # Create package with 1 session, use it
    pkg = run_action("add-package", total_sessions=1, ...)
    result = run_action("use-session", package_id=pkg["id"], ...)
    assert result["status"] == "exhausted"

def test_use_session_on_exhausted_fails(db_conn, exhausted_package_id, company_id):
    result = run_action("use-session", package_id=exhausted_package_id, ...)
    assert "error" in result
```

---

## 7. Recurring Billing (Monthly Charges)

**Description:** Generates invoices on a recurring schedule (monthly, quarterly, annually). Handles proration, late fees, and delinquency tracking. Uses invoice delegation (Pattern 4) for actual GL posting.

**Source modules:** storageclaw (`storageclaw_rental`, billing cycle), propertyclaw (`propertyclaw_lease`, rent charges)

**When to use:**
- Subscription or lease-based businesses (storage, property, SaaS, memberships)
- Any scenario with periodic billing cycles
- When late fees and delinquency tracking are needed

**Schema pattern:**
```sql
CREATE TABLE IF NOT EXISTS {prefix}_billing_cycle (
    id              TEXT PRIMARY KEY,
    company_id      TEXT NOT NULL REFERENCES company(id),
    entity_id       TEXT NOT NULL,           -- rental, lease, subscription
    billing_date    TEXT NOT NULL,            -- next billing date
    amount          TEXT NOT NULL DEFAULT '0',
    frequency       TEXT NOT NULL DEFAULT 'monthly'
                    CHECK(frequency IN ('weekly','monthly','quarterly','annually')),
    status          TEXT NOT NULL DEFAULT 'pending'
                    CHECK(status IN ('pending','invoiced','paid','overdue','delinquent')),
    late_fee_amount TEXT DEFAULT '0',
    days_overdue    INTEGER DEFAULT 0,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
```

**Action pattern:**
```python
from erpclaw_lib.cross_skill import create_invoice

def handle_generate_invoices(args, conn):
    """Generate invoices for all billing cycles due on or before today."""
    today = date.today().isoformat()
    due_cycles = conn.execute(
        """SELECT * FROM {prefix}_billing_cycle
           WHERE company_id = ? AND status = 'pending' AND billing_date <= ?""",
        (args.company_id, today)
    ).fetchall()

    created = 0
    for cycle in due_cycles:
        invoice = create_invoice(conn=conn, company_id=args.company_id,
                                  customer_id=cycle["customer_id"],
                                  items=[{"description": "Monthly charge", "qty": 1,
                                          "rate": cycle["amount"]}],
                                  posting_date=today)
        conn.execute(
            "UPDATE {prefix}_billing_cycle SET status = 'invoiced', updated_at = datetime('now') WHERE id = ?",
            (cycle["id"],)
        )
        created += 1
    conn.commit()
    ok({"invoices_created": created})

def handle_apply_late_fees(args, conn):
    """Apply late fees to overdue billing cycles."""
    # ... find overdue cycles, calculate late fees, update records ...
```

**Test pattern:**
```python
def test_generate_invoices_creates_for_due(db_conn, company_id, mocker):
    # Setup: create a billing cycle due today
    mock_invoice = mocker.patch("erpclaw_lib.cross_skill.create_invoice",
                                 return_value={"id": "inv-1"})
    result = run_action("generate-invoices", company_id=company_id)
    assert result["invoices_created"] == 1
    mock_invoice.assert_called_once()

def test_generate_invoices_skips_future(db_conn, company_id):
    # Setup: create a billing cycle due next month
    result = run_action("generate-invoices", company_id=company_id)
    assert result["invoices_created"] == 0
```

---

## 8. Inventory Tracking

**Description:** Items with stock levels in warehouses. Uses the core ERP item and warehouse tables via READ access, and delegates stock movements via `cross_skill` or the core selling/buying workflows.

**Source modules:** retailclaw (`retailclaw_price_list` extends core item), automotiveclaw (`automotiveclaw_vehicle` is inventory)

**When to use:**
- When the module has physical goods to track (retail products, vehicle inventory, parts)
- For domain-specific item extensions (retail pricing, vehicle VINs)
- Always reads from core `item` and `warehouse_stock` tables; never writes directly

**Schema pattern:**
```sql
-- Extension table for domain-specific item attributes
CREATE TABLE IF NOT EXISTS {prefix}_item_ext (
    id              TEXT PRIMARY KEY,
    item_id         TEXT NOT NULL REFERENCES item(id),
    company_id      TEXT NOT NULL REFERENCES company(id),
    -- domain-specific fields --
    category        TEXT,
    sku_override    TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
```

**Action pattern:**
```python
def handle_list_inventory(args, conn):
    """List inventory with domain-specific attributes joined to core item data."""
    rows = conn.execute(
        """SELECT i.id, i.item_name, i.item_group, ext.category,
                  COALESCE(ws.actual_qty, '0') as qty_on_hand
           FROM item i
           LEFT JOIN {prefix}_item_ext ext ON i.id = ext.item_id
           LEFT JOIN warehouse_stock ws ON i.id = ws.item_id
           WHERE i.company_id = ?
           ORDER BY i.item_name""",
        (args.company_id,)
    ).fetchall()
    ok({"items": [dict(r) for r in rows], "count": len(rows)})
```

**Test pattern:**
```python
def test_list_inventory_joins_extension(db_conn, company_id, item_id):
    # Setup: core item exists + extension record
    result = run_action("list-inventory", company_id=company_id)
    assert result["count"] >= 1
    assert "category" in result["items"][0]
```

---

## 9. Employee/Staff Management

**Description:** Domain-specific staff roles and assignments. Extends the core ERP employee table with profession-specific fields (practitioner type, specializations, certifications).

**Source modules:** healthclaw (`healthclaw_practitioner`), legalclaw (attorney profiles), constructclaw (crew assignments)

**When to use:**
- When staff have domain-specific attributes not in core employee (specialization, license, department assignment)
- Professional credentials tracking

**Schema pattern:**
```sql
CREATE TABLE IF NOT EXISTS {prefix}_staff_ext (
    id              TEXT PRIMARY KEY,
    employee_id     TEXT NOT NULL REFERENCES employee(id),
    company_id      TEXT NOT NULL REFERENCES company(id),
    role            TEXT NOT NULL,
    specialization  TEXT,
    license_number  TEXT,
    is_active       INTEGER DEFAULT 1,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_{prefix}_staff_ext_employee
    ON {prefix}_staff_ext(employee_id);
```

**Action pattern:**
```python
def handle_add_staff(args, conn):
    staff_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO {prefix}_staff_ext
           (id, employee_id, company_id, role, specialization)
           VALUES (?, ?, ?, ?, ?)""",
        (staff_id, args.employee_id, args.company_id, args.role, args.specialization)
    )
    conn.commit()
    ok({"message": "Staff profile created", "id": staff_id})
```

**Test pattern:**
```python
def test_add_staff_creates_profile(db_conn, company_id, employee_id):
    result = run_action("add-staff", employee_id=employee_id,
                        company_id=company_id, role="attorney")
    assert result["id"]
    row = db_conn.execute("SELECT role FROM {prefix}_staff_ext WHERE id = ?",
                          (result["id"],)).fetchone()
    assert row["role"] == "attorney"
```

---

## 10. Customer Management (Core + Extension)

**Description:** The standard pattern for customer data in vertical modules. Core customer fields (name, email, phone, address) live in the core `customer` table. The vertical adds an extension table for domain-specific attributes (donor level, client type, pet owner preferences).

**Source modules:** legalclaw (`legalclaw_client_ext`), automotiveclaw (`automotiveclaw_customer_ext`), nonprofitclaw (`nonprofitclaw_donor_ext`), groomingclaw (via core customer FK)

**When to use:**
- Every vertical module that has customers/clients/patients/donors
- When you need domain-specific customer attributes beyond what core provides
- When migrating from a standalone customer table to the extension pattern

**Schema pattern:**
```sql
CREATE TABLE IF NOT EXISTS {prefix}_customer_ext (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT DEFAULT '{PREFIX}-',
    customer_id     TEXT NOT NULL REFERENCES customer(id),
    -- Domain-specific fields (examples): --
    customer_type   TEXT DEFAULT 'individual'
                    CHECK(customer_type IN ('individual','business','government')),
    domain_field_1  TEXT,
    domain_field_2  TEXT,
    is_active       INTEGER DEFAULT 1,
    company_id      TEXT NOT NULL REFERENCES company(id),
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_{prefix}_customer_ext_company
    ON {prefix}_customer_ext(company_id);
CREATE INDEX IF NOT EXISTS idx_{prefix}_customer_ext_customer
    ON {prefix}_customer_ext(customer_id);
```

**Action pattern:**
```python
def handle_add_client(args, conn):
    """Add a domain client by creating core customer + extension record in one transaction."""
    conn.execute("BEGIN")
    # 1. Create core customer (via cross_skill or direct if module is allowed)
    from erpclaw_lib.cross_skill import call_skill_action
    core_result = call_skill_action("erpclaw", "add-customer",
                                     name=args.name, company_id=args.company_id)
    customer_id = core_result["id"]

    # 2. Create extension record
    ext_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO {prefix}_customer_ext
           (id, customer_id, company_id, customer_type)
           VALUES (?, ?, ?, ?)""",
        (ext_id, customer_id, args.company_id, args.customer_type or "individual")
    )
    conn.execute("COMMIT")
    ok({"message": "Client added", "id": ext_id, "customer_id": customer_id})

def handle_get_client(args, conn):
    """Get client with joined core customer data."""
    row = conn.execute(
        """SELECT ext.*, c.customer_name, c.email, c.phone
           FROM {prefix}_customer_ext ext
           JOIN customer c ON ext.customer_id = c.id
           WHERE ext.id = ? AND ext.company_id = ?""",
        (args.id, args.company_id)
    ).fetchone()
    if not row:
        return err("Client not found")
    ok(dict(row))
```

**Test pattern:**
```python
def test_add_client_creates_extension(db_conn, company_id, mocker):
    mock_core = mocker.patch("erpclaw_lib.cross_skill.call_skill_action",
                              return_value={"id": "cust-1"})
    result = run_action("add-client", name="Jane Doe", company_id=company_id)
    assert result["customer_id"] == "cust-1"
    ext = db_conn.execute("SELECT * FROM {prefix}_customer_ext WHERE id = ?",
                          (result["id"],)).fetchone()
    assert ext["customer_id"] == "cust-1"

def test_get_client_joins_core_data(db_conn, company_id, client_id):
    result = run_action("get-client", id=client_id, company_id=company_id)
    assert "customer_name" in result  # from core customer table
    assert "customer_type" in result  # from extension table
```

---

## Pattern Selection Guide

| Business Need | Pattern | Example Modules |
|---------------|---------|-----------------|
| Store and query entities | 1. CRUD Entity | All modules |
| Schedule time-bound events | 2. Appointment/Booking | healthclaw, groomingclaw |
| Document work performed | 3. Service Record | healthclaw-vet, automotiveclaw |
| Create invoices/payments | 4. Invoice Delegation | groomingclaw, tattooclaw, storageclaw |
| Track licenses/certifications | 5. Compliance/Licensing | legalclaw, constructclaw |
| Sell prepaid session bundles | 6. Prepaid Package | groomingclaw |
| Bill on recurring schedule | 7. Recurring Billing | storageclaw, propertyclaw |
| Manage physical goods | 8. Inventory Tracking | retailclaw, automotiveclaw |
| Extend employee profiles | 9. Employee/Staff Management | healthclaw, legalclaw |
| Extend customer profiles | 10. Customer Management | All verticals |

Most modules use 3-5 of these patterns combined. For example, a veterinary clinic module uses: CRUD Entity (pets), Appointment/Booking (visits), Service Record (treatments), Invoice Delegation (billing), and Customer Management (pet owners via core customer extension).
