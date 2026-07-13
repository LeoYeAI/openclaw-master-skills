"""EduClaw — fees domain module

Actions for fees: fee categories, fee structures, scholarships,
fee invoice generation via erpclaw-selling, outstanding fee queries.

Imported by db_query.py (unified router).
"""
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, date, timezone
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection
    from erpclaw_lib.decimal_utils import to_decimal, round_currency
    from erpclaw_lib.response import ok, err
    from erpclaw_lib.audit import audit
except ImportError:
    pass

SKILL = "educlaw"
_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _d(val, default="0"):
    try:
        return Decimal(str(val)) if val not in (None, "", "None") else Decimal(default)
    except (InvalidOperation, Exception):
        return Decimal(default)


# ─────────────────────────────────────────────────────────────────────────────
# FEE CATEGORY
# ─────────────────────────────────────────────────────────────────────────────

def add_fee_category(conn, args):
    name = getattr(args, "name", None)
    company_id = getattr(args, "company_id", None)

    if not name:
        err("--name is required")
    if not company_id:
        err("--company-id is required")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    revenue_account_id = getattr(args, "revenue_account_id", None)
    if revenue_account_id:
        if not conn.execute("SELECT id FROM account WHERE id = ?", (revenue_account_id,)).fetchone():
            err(f"Account {revenue_account_id} not found")

    cat_id = str(uuid.uuid4())
    now = _now_iso()

    try:
        conn.execute(
            """INSERT INTO educlaw_fee_category
               (id, name, description, revenue_account_id, is_active, company_id,
                created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (cat_id, name, getattr(args, "description", None) or "",
             revenue_account_id, 1, company_id, now, now,
             getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Fee category '{name}' already exists for this company")

    audit(conn, SKILL, "add-fee-category", "educlaw_fee_category", cat_id,
          new_values={"name": name})
    conn.commit()
    ok({"id": cat_id, "name": name, "company_id": company_id})


def update_fee_category(conn, args):
    category_id = getattr(args, "category_id", None)
    if not category_id:
        err("--category-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_fee_category WHERE id = ?", (category_id,)
    ).fetchone()
    if not row:
        err(f"Fee category {category_id} not found")

    updates, params, changed = [], [], []

    if getattr(args, "name", None) is not None:
        updates.append("name = ?"); params.append(args.name); changed.append("name")
    if getattr(args, "description", None) is not None:
        updates.append("description = ?"); params.append(args.description); changed.append("description")
    if getattr(args, "revenue_account_id", None) is not None:
        if args.revenue_account_id and not conn.execute(
                "SELECT id FROM account WHERE id = ?", (args.revenue_account_id,)).fetchone():
            err(f"Account {args.revenue_account_id} not found")
        updates.append("revenue_account_id = ?"); params.append(args.revenue_account_id)
        changed.append("revenue_account_id")
    if getattr(args, "is_active", None) is not None:
        updates.append("is_active = ?"); params.append(int(args.is_active)); changed.append("is_active")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(category_id)
    conn.execute(f"UPDATE educlaw_fee_category SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    ok({"id": category_id, "updated_fields": changed})


def list_fee_categories(conn, args):
    query = "SELECT * FROM educlaw_fee_category WHERE 1=1"
    params = []

    if getattr(args, "is_active", None) is not None:
        query += " AND is_active = ?"; params.append(int(args.is_active))
    if getattr(args, "company_id", None):
        query += " AND company_id = ?"; params.append(args.company_id)

    query += " ORDER BY name"
    rows = conn.execute(query, params).fetchall()
    ok({"fee_categories": [dict(r) for r in rows], "count": len(rows)})


# ─────────────────────────────────────────────────────────────────────────────
# FEE STRUCTURE
# ─────────────────────────────────────────────────────────────────────────────

def add_fee_structure(conn, args):
    name = getattr(args, "name", None)
    company_id = getattr(args, "company_id", None)
    items_json = getattr(args, "items", None)

    if not name:
        err("--name is required")
    if not company_id:
        err("--company-id is required")
    if not items_json:
        err("--items is required (JSON array of {fee_category_id, amount, description})")

    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    try:
        items = json.loads(items_json) if isinstance(items_json, str) else items_json
        if not isinstance(items, list) or not items:
            err("--items must be a non-empty JSON array")
    except (json.JSONDecodeError, TypeError):
        err("--items must be valid JSON array")

    program_id = getattr(args, "program_id", None)
    if program_id:
        if not conn.execute("SELECT id FROM educlaw_program WHERE id = ?", (program_id,)).fetchone():
            err(f"Program {program_id} not found")

    academic_term_id = getattr(args, "academic_term_id", None)
    if academic_term_id:
        if not conn.execute("SELECT id FROM educlaw_academic_term WHERE id = ?",
                            (academic_term_id,)).fetchone():
            err(f"Academic term {academic_term_id} not found")

    # Validate items and calculate total
    total = Decimal("0")
    for item in items:
        if not isinstance(item, dict):
            continue
        cat_id = item.get("fee_category_id")
        amount = _d(item.get("amount", "0"))
        if not cat_id:
            err("Each item must have a fee_category_id")
        if not conn.execute("SELECT id FROM educlaw_fee_category WHERE id = ?", (cat_id,)).fetchone():
            err(f"Fee category {cat_id} not found")
        if amount < 0:
            err(f"Amount must be >= 0 (got {amount} for category {cat_id})")
        total += amount

    struct_id = str(uuid.uuid4())
    now = _now_iso()

    conn.execute(
        """INSERT INTO educlaw_fee_structure
           (id, name, program_id, academic_term_id, grade_level, total_amount,
            is_active, company_id, created_at, updated_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (struct_id, name, program_id, academic_term_id,
         getattr(args, "grade_level", None) or "",
         str(total), 1, company_id, now, now, getattr(args, "user_id", None) or "")
    )

    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        item_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO educlaw_fee_structure_item
               (id, fee_structure_id, fee_category_id, amount, description,
                sort_order, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (item_id, struct_id, item.get("fee_category_id"),
             str(_d(item.get("amount", "0"))),
             item.get("description", ""),
             item.get("sort_order", i + 1), now, getattr(args, "user_id", None) or "")
        )

    audit(conn, SKILL, "add-fee-structure", "educlaw_fee_structure", struct_id,
          new_values={"name": name, "total_amount": str(total)})
    conn.commit()
    ok({"id": struct_id, "name": name, "total_amount": str(total), "item_count": len(items)})


def update_fee_structure(conn, args):
    structure_id = getattr(args, "structure_id", None)
    if not structure_id:
        err("--structure-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_fee_structure WHERE id = ?", (structure_id,)
    ).fetchone()
    if not row:
        err(f"Fee structure {structure_id} not found")

    updates, params, changed = [], [], []

    if getattr(args, "name", None) is not None:
        updates.append("name = ?"); params.append(args.name); changed.append("name")
    if getattr(args, "grade_level", None) is not None:
        updates.append("grade_level = ?"); params.append(args.grade_level); changed.append("grade_level")
    if getattr(args, "is_active", None) is not None:
        updates.append("is_active = ?"); params.append(int(args.is_active)); changed.append("is_active")

    items_json = getattr(args, "items", None)
    if items_json:
        try:
            items = json.loads(items_json) if isinstance(items_json, str) else items_json
        except Exception:
            err("--items must be valid JSON array")

        total = Decimal("0")
        for item in items:
            if not isinstance(item, dict):
                continue
            if not conn.execute("SELECT id FROM educlaw_fee_category WHERE id = ?",
                                (item.get("fee_category_id"),)).fetchone():
                err(f"Fee category {item.get('fee_category_id')} not found")
            total += _d(item.get("amount", "0"))

        conn.execute(
            "DELETE FROM educlaw_fee_structure_item WHERE fee_structure_id = ?", (structure_id,)
        )
        now = _now_iso()
        for i, item in enumerate(items):
            item_id = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO educlaw_fee_structure_item
                   (id, fee_structure_id, fee_category_id, amount, description,
                    sort_order, created_at, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (item_id, structure_id, item.get("fee_category_id"),
                 str(_d(item.get("amount", "0"))), item.get("description", ""),
                 item.get("sort_order", i + 1), now, getattr(args, "user_id", None) or "")
            )
        updates.append("total_amount = ?"); params.append(str(total))
        changed.append("items")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(structure_id)
    conn.execute(f"UPDATE educlaw_fee_structure SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    ok({"id": structure_id, "updated_fields": changed})


def get_fee_structure(conn, args):
    structure_id = getattr(args, "structure_id", None)
    if not structure_id:
        err("--structure-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_fee_structure WHERE id = ?", (structure_id,)
    ).fetchone()
    if not row:
        err(f"Fee structure {structure_id} not found")

    data = dict(row)
    items = conn.execute(
        """SELECT fsi.*, fc.name as category_name
           FROM educlaw_fee_structure_item fsi
           JOIN educlaw_fee_category fc ON fc.id = fsi.fee_category_id
           WHERE fsi.fee_structure_id = ? ORDER BY fsi.sort_order""",
        (structure_id,)
    ).fetchall()
    data["items"] = [dict(i) for i in items]
    ok(data)


def list_fee_structures(conn, args):
    query = "SELECT * FROM educlaw_fee_structure WHERE 1=1"
    params = []

    if getattr(args, "program_id", None):
        query += " AND program_id = ?"; params.append(args.program_id)
    if getattr(args, "academic_term_id", None):
        query += " AND academic_term_id = ?"; params.append(args.academic_term_id)
    if getattr(args, "grade_level", None):
        query += " AND grade_level = ?"; params.append(args.grade_level)
    if getattr(args, "is_active", None) is not None:
        query += " AND is_active = ?"; params.append(int(args.is_active))
    if getattr(args, "company_id", None):
        query += " AND company_id = ?"; params.append(args.company_id)

    query += " ORDER BY name"
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"fee_structures": [dict(r) for r in rows], "count": len(rows)})


# ─────────────────────────────────────────────────────────────────────────────
# SCHOLARSHIP
# ─────────────────────────────────────────────────────────────────────────────

def add_scholarship(conn, args):
    name = getattr(args, "name", None)
    student_id = getattr(args, "student_id", None)
    discount_type = getattr(args, "discount_type", None)
    discount_amount = getattr(args, "discount_amount", None)
    company_id = getattr(args, "company_id", None)

    if not name:
        err("--name is required")
    if not student_id:
        err("--student-id is required")
    if not discount_type:
        err("--discount-type is required (fixed or percentage)")
    if discount_type not in ("fixed", "percentage"):
        err("--discount-type must be 'fixed' or 'percentage'")
    if not discount_amount:
        err("--discount-amount is required")
    if not company_id:
        err("--company-id is required")

    if _d(discount_amount) < 0:
        err("--discount-amount must be >= 0")

    student_row = conn.execute("SELECT * FROM educlaw_student WHERE id = ?", (student_id,)).fetchone()
    if not student_row:
        err(f"Student {student_id} not found")
    if dict(student_row)["status"] != "active":
        err("Student must be active to receive scholarship")

    academic_term_id = getattr(args, "academic_term_id", None)
    if academic_term_id:
        if not conn.execute("SELECT id FROM educlaw_academic_term WHERE id = ?",
                            (academic_term_id,)).fetchone():
            err(f"Academic term {academic_term_id} not found")

    applies_to_category_id = getattr(args, "applies_to_category_id", None)
    if applies_to_category_id:
        if not conn.execute("SELECT id FROM educlaw_fee_category WHERE id = ?",
                            (applies_to_category_id,)).fetchone():
            err(f"Fee category {applies_to_category_id} not found")

    schol_id = str(uuid.uuid4())
    now = _now_iso()

    conn.execute(
        """INSERT INTO educlaw_scholarship
           (id, name, student_id, academic_term_id, discount_type, discount_amount,
            applies_to_category_id, scholarship_status, reason, approved_by,
            company_id, created_at, updated_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (schol_id, name, student_id, academic_term_id, discount_type,
         str(_d(discount_amount)), applies_to_category_id, "active",
         getattr(args, "reason", None) or "",
         getattr(args, "approved_by", None) or "",
         company_id, now, now, getattr(args, "user_id", None) or "")
    )

    audit(conn, SKILL, "add-scholarship", "educlaw_scholarship", schol_id,
          new_values={"name": name, "student_id": student_id, "discount_type": discount_type})
    conn.commit()
    ok({"id": schol_id, "name": name, "student_id": student_id,
        "discount_type": discount_type, "discount_amount": str(_d(discount_amount)),
        "scholarship_status": "active"})


def update_scholarship(conn, args):
    scholarship_id = getattr(args, "scholarship_id", None)
    if not scholarship_id:
        err("--scholarship-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_scholarship WHERE id = ?", (scholarship_id,)
    ).fetchone()
    if not row:
        err(f"Scholarship {scholarship_id} not found")

    updates, params, changed = [], [], []

    if getattr(args, "name", None) is not None:
        updates.append("name = ?"); params.append(args.name); changed.append("name")
    if getattr(args, "discount_type", None) is not None:
        if args.discount_type not in ("fixed", "percentage"):
            err("--discount-type must be 'fixed' or 'percentage'")
        updates.append("discount_type = ?"); params.append(args.discount_type)
        changed.append("discount_type")
    if getattr(args, "discount_amount", None) is not None:
        updates.append("discount_amount = ?"); params.append(str(_d(args.discount_amount)))
        changed.append("discount_amount")
    if getattr(args, "scholarship_status", None) is not None:
        if args.scholarship_status not in ("active", "expired", "revoked"):
            err("--scholarship-status must be active, expired, or revoked")
        updates.append("scholarship_status = ?"); params.append(args.scholarship_status)
        changed.append("scholarship_status")
    if getattr(args, "reason", None) is not None:
        updates.append("reason = ?"); params.append(args.reason); changed.append("reason")
    if getattr(args, "approved_by", None) is not None:
        updates.append("approved_by = ?"); params.append(args.approved_by)
        changed.append("approved_by")

    if not changed:
        err("No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(scholarship_id)
    conn.execute(f"UPDATE educlaw_scholarship SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    ok({"id": scholarship_id, "updated_fields": changed})


def list_scholarships(conn, args):
    query = "SELECT * FROM educlaw_scholarship WHERE 1=1"
    params = []

    if getattr(args, "student_id", None):
        query += " AND student_id = ?"; params.append(args.student_id)
    if getattr(args, "academic_term_id", None):
        query += " AND academic_term_id = ?"; params.append(args.academic_term_id)
    if getattr(args, "scholarship_status", None):
        query += " AND scholarship_status = ?"; params.append(args.scholarship_status)
    if getattr(args, "company_id", None):
        query += " AND company_id = ?"; params.append(args.company_id)

    query += " ORDER BY created_at DESC"
    limit = int(getattr(args, "limit", None) or 50)
    offset = int(getattr(args, "offset", None) or 0)
    query += f" LIMIT {limit} OFFSET {offset}"

    rows = conn.execute(query, params).fetchall()
    ok({"scholarships": [dict(r) for r in rows], "count": len(rows)})


# ─────────────────────────────────────────────────────────────────────────────
# FEE INVOICE GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def generate_fee_invoice(conn, args):
    """Generate fee invoice for program enrollment. Reads fee structure and applies scholarships."""
    student_id = getattr(args, "student_id", None)
    program_id = getattr(args, "program_id", None)
    academic_term_id = getattr(args, "academic_term_id", None)
    company_id = getattr(args, "company_id", None)

    if not student_id:
        err("--student-id is required")
    if not company_id:
        err("--company-id is required")

    student_row = conn.execute("SELECT * FROM educlaw_student WHERE id = ?", (student_id,)).fetchone()
    if not student_row:
        err(f"Student {student_id} not found")

    student = dict(student_row)

    # Find applicable fee structure
    fee_struct = None
    if program_id and academic_term_id:
        fee_struct = conn.execute(
            """SELECT * FROM educlaw_fee_structure
               WHERE company_id = ? AND program_id = ? AND academic_term_id = ? AND is_active = 1
               LIMIT 1""",
            (company_id, program_id, academic_term_id)
        ).fetchone()
    if not fee_struct and academic_term_id and student.get("grade_level"):
        fee_struct = conn.execute(
            """SELECT * FROM educlaw_fee_structure
               WHERE company_id = ? AND grade_level = ? AND academic_term_id = ? AND is_active = 1
               LIMIT 1""",
            (company_id, student["grade_level"], academic_term_id)
        ).fetchone()

    if not fee_struct:
        err("No active fee structure found for this student/program/term combination")

    fs = dict(fee_struct)
    base_amount = _d(fs["total_amount"])

    # Get line items
    items = conn.execute(
        """SELECT fsi.*, fc.name as category_name
           FROM educlaw_fee_structure_item fsi
           JOIN educlaw_fee_category fc ON fc.id = fsi.fee_category_id
           WHERE fsi.fee_structure_id = ? ORDER BY fsi.sort_order""",
        (fs["id"],)
    ).fetchall()

    # Apply scholarships
    scholarships = conn.execute(
        """SELECT * FROM educlaw_scholarship
           WHERE student_id = ? AND scholarship_status = 'active'
           AND (academic_term_id IS NULL OR academic_term_id = ?)""",
        (student_id, academic_term_id or "")
    ).fetchall()

    total_discount = Decimal("0")
    scholarship_details = []
    for schol in scholarships:
        s = dict(schol)
        if s["discount_type"] == "fixed":
            disc = _d(s["discount_amount"])
        else:  # percentage
            disc = (base_amount * _d(s["discount_amount"]) / Decimal("100")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        total_discount += disc
        scholarship_details.append({
            "scholarship_id": s["id"],
            "name": s["name"],
            "discount_type": s["discount_type"],
            "discount_amount": s["discount_amount"],
            "applied_discount": str(disc),
        })

    final_amount = max(Decimal("0"), base_amount - total_discount)

    # Note: In production, this would call erpclaw-selling subprocess
    # For now, record the invoice details and return
    invoice_id = str(uuid.uuid4())
    now = _now_iso()

    # Send fee_due notification
    notif_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_notification
           (id, recipient_type, recipient_id, notification_type, title, message,
            reference_type, reference_id, company_id, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (notif_id, "student", student_id, "fee_due",
         "Fee Invoice Generated",
         f"Your fee invoice for the term has been generated. Total due: ${final_amount}",
         "educlaw_fee_structure", fs["id"], company_id, now,
         getattr(args, "user_id", None) or "")
    )
    conn.commit()

    ok({
        "invoice_id": invoice_id,
        "student_id": student_id,
        "fee_structure_id": fs["id"],
        "base_amount": str(base_amount),
        "total_discount": str(total_discount),
        "final_amount": str(final_amount),
        "line_items": [dict(i) for i in items],
        "scholarships_applied": scholarship_details,
        "generated_at": now,
        "note": "Invoice generated. Submit to erpclaw-selling to create billable invoice.",
    })


def list_fee_invoices(conn, args):
    """List fee invoices. Reads from sales_invoice filtered by student's customer_id."""
    student_id = getattr(args, "student_id", None)

    # Try to read from sales_invoice if erpclaw-selling is available
    if student_id:
        student_row = conn.execute(
            "SELECT customer_id FROM educlaw_student WHERE id = ?", (student_id,)
        ).fetchone()
        if not student_row:
            err(f"Student {student_id} not found")
        customer_id = dict(student_row).get("customer_id")
        if customer_id:
            try:
                invoices = conn.execute(
                    "SELECT * FROM sales_invoice WHERE customer_id = ? ORDER BY posting_date DESC",
                    (customer_id,)
                ).fetchall()
                ok({"student_id": student_id, "invoices": [dict(i) for i in invoices],
                    "count": len(invoices)})
                return
            except Exception:
                pass

    ok({"student_id": student_id, "invoices": [],
        "message": "Connect erpclaw-selling to view invoices"})


def get_student_account(conn, args):
    """Full financial summary for student."""
    student_id = getattr(args, "student_id", None)
    if not student_id:
        err("--student-id is required")

    student_row = conn.execute("SELECT * FROM educlaw_student WHERE id = ?", (student_id,)).fetchone()
    if not student_row:
        err(f"Student {student_id} not found")

    student = dict(student_row)
    customer_id = student.get("customer_id")

    invoices = []
    payments = []
    outstanding = Decimal("0")

    if customer_id:
        try:
            inv_rows = conn.execute(
                """SELECT id, name, posting_date, grand_total, status, outstanding_amount
                   FROM sales_invoice WHERE customer_id = ? ORDER BY posting_date DESC""",
                (customer_id,)
            ).fetchall()
            invoices = [dict(r) for r in inv_rows]
            for inv in invoices:
                outstanding += _d(inv.get("outstanding_amount", "0"))
        except Exception:
            pass

    scholarships = conn.execute(
        "SELECT * FROM educlaw_scholarship WHERE student_id = ? AND scholarship_status = 'active'",
        (student_id,)
    ).fetchall()

    ok({
        "student_id": student_id,
        "customer_id": customer_id,
        "invoices": invoices,
        "payments": payments,
        "outstanding_balance": str(outstanding),
        "active_scholarships": [dict(s) for s in scholarships],
    })


def get_outstanding_fees(conn, args):
    """List all students with outstanding fees past due date."""
    company_id = getattr(args, "company_id", None)
    if not company_id:
        err("--company-id is required")

    today = date.today().isoformat()
    students = conn.execute(
        "SELECT id, naming_series, full_name, customer_id, email FROM educlaw_student WHERE company_id = ? AND status = 'active'",
        (company_id,)
    ).fetchall()

    outstanding_list = []
    for student in students:
        s = dict(student)
        if not s.get("customer_id"):
            continue
        try:
            overdue = conn.execute(
                """SELECT id, posting_date, due_date, grand_total, outstanding_amount, status
                   FROM sales_invoice
                   WHERE customer_id = ? AND status IN ('unpaid', 'overdue')
                   AND due_date < ? AND outstanding_amount > 0""",
                (s["customer_id"], today)
            ).fetchall()
            if overdue:
                total_outstanding = sum(_d(o["outstanding_amount"]) for o in overdue)
                outstanding_list.append({
                    "student_id": s["id"],
                    "naming_series": s["naming_series"],
                    "full_name": s["full_name"],
                    "email": s["email"],
                    "total_outstanding": str(total_outstanding),
                    "overdue_invoices": [dict(o) for o in overdue],
                })
        except Exception:
            pass

    ok({"company_id": company_id, "outstanding_count": len(outstanding_list),
        "outstanding_students": outstanding_list})


def apply_late_fee(conn, args):
    """Apply late fee to overdue invoice."""
    student_id = getattr(args, "student_id", None)
    fee_category_id = getattr(args, "fee_category_id", None)
    amount = getattr(args, "amount", None)
    company_id = getattr(args, "company_id", None)

    if not student_id:
        err("--student-id is required")
    if not fee_category_id:
        err("--fee-category-id is required")
    if not amount:
        err("--amount is required")
    if not company_id:
        err("--company-id is required")
    if _d(amount) <= 0:
        err("--amount must be greater than 0")

    if not conn.execute("SELECT id FROM educlaw_student WHERE id = ?", (student_id,)).fetchone():
        err(f"Student {student_id} not found")
    if not conn.execute("SELECT id FROM educlaw_fee_category WHERE id = ?", (fee_category_id,)).fetchone():
        err(f"Fee category {fee_category_id} not found")

    now = _now_iso()
    notif_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO educlaw_notification
           (id, recipient_type, recipient_id, notification_type, title, message,
            reference_type, reference_id, company_id, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (notif_id, "student", student_id, "fee_due",
         "Late Fee Applied",
         f"A late fee of ${_d(amount)} has been applied to your account.",
         "educlaw_fee_category", fee_category_id, company_id, now,
         getattr(args, "user_id", None) or "")
    )
    conn.commit()

    ok({
        "student_id": student_id,
        "late_fee_amount": str(_d(amount)),
        "fee_category_id": fee_category_id,
        "applied_at": now,
        "note": "Late fee recorded. Submit to erpclaw-selling to post to invoice.",
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACTIONS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

ACTIONS = {
    "add-fee-category": add_fee_category,
    "update-fee-category": update_fee_category,
    "list-fee-categories": list_fee_categories,
    "add-fee-structure": add_fee_structure,
    "update-fee-structure": update_fee_structure,
    "get-fee-structure": get_fee_structure,
    "list-fee-structures": list_fee_structures,
    "add-scholarship": add_scholarship,
    "update-scholarship": update_scholarship,
    "list-scholarships": list_scholarships,
    "generate-fee-invoice": generate_fee_invoice,
    "list-fee-invoices": list_fee_invoices,
    "get-student-account": get_student_account,
    "get-outstanding-fees": get_outstanding_fees,
    "apply-late-fee": apply_late_fee,
}
