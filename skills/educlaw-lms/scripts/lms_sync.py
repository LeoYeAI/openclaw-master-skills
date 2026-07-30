"""EduClaw LMS Integration — lms_sync domain module

Actions for LMS connection management, roster push, sync audit logging,
and conflict resolution.

Actions (9):
  add-lms-connection, update-lms-connection, get-lms-connection,
  list-lms-connections, activate-lms-connection, apply-course-sync,
  list-sync-logs, get-sync-log, apply-sync-resolution

Imported by db_query.py (unified router).
"""
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone

try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit
    from erpclaw_lib.crypto import encrypt_field, decrypt_field
except ImportError:
    pass

SKILL = "educlaw-lms"
_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

VALID_LMS_TYPES = ("canvas", "moodle", "google_classroom", "oneroster_csv")
VALID_GRADE_DIRECTIONS = ("lms_to_sis", "sis_to_lms", "manual")
VALID_CONN_STATUSES = ("draft", "active", "inactive", "error")
VALID_SYNC_TYPES = ("roster_push", "grade_pull", "assignment_push", "full_sync", "oneroster_export")
VALID_SYNC_STATUSES = ("pending", "running", "completed", "completed_with_errors", "failed")
VALID_ENTITY_TYPES = ("user", "course")
VALID_RESOLUTIONS = ("sis_wins", "lms_wins", "dismiss")
VALID_USER_MAP_STATUSES = ("synced", "pending", "error", "invited")


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _get_encryption_key():
    """Return 32-byte encryption key from env var, or None if not set."""
    import hashlib
    key_str = os.environ.get("EDUCLAW_LMS_ENCRYPTION_KEY", "")
    if not key_str:
        return None
    return hashlib.sha256(key_str.encode()).digest()


def _encrypt_cred(value, key):
    """Encrypt credential value if key is available; otherwise return as-is."""
    if not value or not key:
        return value or ""
    try:
        return encrypt_field(value, key)
    except Exception:
        return value or ""


def _decrypt_cred(value, key):
    """Decrypt credential value if it's encrypted."""
    if not value or not key:
        return value or ""
    try:
        return decrypt_field(value, key)
    except Exception:
        return value or ""


def _mask_cred(value):
    """Return last 4 chars of credential with asterisk masking."""
    if not value or value == "":
        return ""
    clean = value
    if clean.startswith("enc:"):
        clean = clean[4:]
    if len(clean) <= 4:
        return "****"
    return f"{'*' * (len(clean) - 4)}{clean[-4:]}"


def _next_lms_series(conn, entity_type, prefix, company_id, use_year=False):
    """Generate next sequential naming series for LMS entities.

    Bypasses ENTITY_PREFIXES restriction by directly using naming_series table.
    """
    year = datetime.now(timezone.utc).year
    full_prefix = f"{prefix}{year}-" if use_year else prefix
    entry_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO naming_series (id, entity_type, prefix, current_value, company_id)
           VALUES (?, ?, ?, 1, ?)
           ON CONFLICT(entity_type, prefix, company_id)
           DO UPDATE SET current_value = current_value + 1""",
        (entry_id, entity_type, full_prefix, company_id)
    )
    row = conn.execute(
        "SELECT current_value FROM naming_series WHERE entity_type = ? AND prefix = ? AND company_id = ?",
        (entity_type, full_prefix, company_id)
    ).fetchone()
    seq = row[0] if row else 1
    return f"{full_prefix}{seq:05d}"


def _log_ferpa_access(conn, student_id, company_id, access_reason, triggered_by="system"):
    """Write a FERPA data access log entry (uses 'api' as access_type — constraint-safe)."""
    log_id = str(uuid.uuid4())
    try:
        conn.execute(
            """INSERT INTO educlaw_data_access_log
               (id, user_id, student_id, data_category, access_type, access_reason,
                is_emergency_access, ip_address, company_id, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (log_id, triggered_by, student_id, "demographics", "api",
             access_reason, 0, "", company_id, _now_iso(), triggered_by)
        )
    except Exception:
        pass  # Never fail the main operation due to logging


def _get_adapter(conn_row, key=None):
    """Return the appropriate LMS adapter for the connection's lms_type."""
    # Import adapters relative to this script's directory
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    lms_type = conn_row.get("lms_type") or conn_row["lms_type"]
    decrypted_creds = {
        "client_secret": _decrypt_cred(conn_row.get("client_secret_encrypted", ""), key),
        "site_token": _decrypt_cred(conn_row.get("site_token_encrypted", ""), key),
        "google_credentials": _decrypt_cred(conn_row.get("google_credentials_encrypted", ""), key),
    }

    if lms_type == "canvas":
        from adapters.canvas import CanvasAdapter
        return CanvasAdapter(conn_row, decrypted_creds)
    elif lms_type == "moodle":
        from adapters.moodle import MoodleAdapter
        return MoodleAdapter(conn_row, decrypted_creds)
    elif lms_type == "google_classroom":
        from adapters.google_classroom import GoogleClassroomAdapter
        return GoogleClassroomAdapter(conn_row, decrypted_creds)
    elif lms_type == "oneroster_csv":
        # OneRoster CSV has no live API; return None (handled by caller)
        return None
    else:
        raise ValueError(f"Unknown lms_type: {lms_type}")


def _check_dpa(conn_row):
    """Return error string if DPA is not signed, else None."""
    if not int(conn_row.get("has_dpa_signed", 0) or 0):
        return "E_DPA_REQUIRED: Data Processing Agreement must be signed before sync operations"
    return None


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: add-lms-connection
# ─────────────────────────────────────────────────────────────────────────────

def add_lms_connection(conn, args):
    """Create a new LMS connection in draft status."""
    lms_type = getattr(args, "lms_type", None) or None
    display_name = getattr(args, "display_name", None) or None
    company_id = getattr(args, "company_id", None) or None

    if not lms_type:
        err("--lms-type is required")
    if lms_type not in VALID_LMS_TYPES:
        err(f"--lms-type must be one of: {', '.join(VALID_LMS_TYPES)}")
    if not display_name:
        err("--display-name is required")
    if not company_id:
        err("--company-id is required")

    # Validate company
    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    # Validate endpoint_url required for non-oneroster
    endpoint_url = getattr(args, "endpoint_url", None) or ""
    if lms_type in ("canvas", "moodle") and not endpoint_url:
        err(f"--endpoint-url is required for lms_type '{lms_type}'")

    key = _get_encryption_key()
    client_id = getattr(args, "client_id", None) or ""
    client_secret_raw = getattr(args, "client_secret", None) or ""
    site_token_raw = getattr(args, "site_token", None) or ""
    google_creds_raw = getattr(args, "google_credentials", None) or ""

    grade_direction = getattr(args, "grade_direction", None) or "lms_to_sis"
    if grade_direction not in VALID_GRADE_DIRECTIONS:
        err(f"--grade-direction must be one of: {', '.join(VALID_GRADE_DIRECTIONS)}")

    has_dpa_signed = int(getattr(args, "has_dpa_signed", None) or 0)
    dpa_signed_date = getattr(args, "dpa_signed_date", None) or ""
    is_coppa_verified = int(getattr(args, "is_coppa_verified", None) or 0)
    coppa_cert_url = getattr(args, "coppa_cert_url", None) or ""
    auto_push_assignments = int(getattr(args, "auto_push_assignments", None) or 0)
    default_course_prefix = getattr(args, "default_course_prefix", None) or ""
    allowed_data_fields = getattr(args, "allowed_data_fields", None) or "[]"

    # Validate allowed_data_fields JSON
    try:
        json.loads(allowed_data_fields)
    except (json.JSONDecodeError, TypeError):
        err("--allowed-data-fields must be valid JSON array")

    conn_id = str(uuid.uuid4())
    now = _now_iso()

    # Generate naming series: LMS-00001 format
    naming_series = _next_lms_series(
        conn, "educlaw_lms_connection", "LMS-", company_id, use_year=False
    )

    try:
        conn.execute(
            """INSERT INTO educlaw_lms_connection
               (id, naming_series, display_name, lms_type, endpoint_url,
                client_id, client_secret_encrypted, site_token_encrypted,
                google_credentials_encrypted, grade_direction,
                auto_push_assignments, has_dpa_signed, dpa_signed_date,
                is_coppa_verified, coppa_cert_url, allowed_data_fields,
                default_course_prefix, status, company_id, created_at, updated_at,
                created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (conn_id, naming_series, display_name, lms_type, endpoint_url,
             client_id,
             _encrypt_cred(client_secret_raw, key),
             _encrypt_cred(site_token_raw, key),
             _encrypt_cred(google_creds_raw, key),
             grade_direction,
             auto_push_assignments, has_dpa_signed, dpa_signed_date,
             is_coppa_verified, coppa_cert_url, allowed_data_fields,
             default_course_prefix, "draft", company_id, now, now,
             getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"LMS connection creation failed: {e}")

    try:
        audit(conn, SKILL, "add-lms-connection", "educlaw_lms_connection", conn_id,
              new_values={"display_name": display_name, "lms_type": lms_type,
                          "connection_status": "draft"})
    except Exception:
        pass
    conn.commit()
    ok({
        "id": conn_id,
        "naming_series": naming_series,
        "display_name": display_name,
        "lms_type": lms_type,
        "connection_status": "draft",
        "has_dpa_signed": has_dpa_signed,
        "message": "LMS connection created",
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: update-lms-connection
# ─────────────────────────────────────────────────────────────────────────────

def update_lms_connection(conn, args):
    """Update LMS connection settings."""
    conn_id = getattr(args, "connection_id", None) or None
    if not conn_id:
        err("--connection-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_lms_connection WHERE id = ?", (conn_id,)
    ).fetchone()
    if not row:
        err(f"LMS connection {conn_id} not found")
    row = dict(row)

    if row.get("status") == "closed":
        err("Cannot update a closed LMS connection")

    key = _get_encryption_key()
    updates, params = [], []

    display_name = getattr(args, "display_name", None)
    if display_name is not None:
        updates.append("display_name = ?"); params.append(display_name)

    endpoint_url = getattr(args, "endpoint_url", None)
    if endpoint_url is not None:
        updates.append("endpoint_url = ?"); params.append(endpoint_url)

    client_id = getattr(args, "client_id", None)
    if client_id is not None:
        updates.append("client_id = ?"); params.append(client_id)

    client_secret = getattr(args, "client_secret", None)
    if client_secret is not None:
        updates.append("client_secret_encrypted = ?")
        params.append(_encrypt_cred(client_secret, key))

    site_token = getattr(args, "site_token", None)
    if site_token is not None:
        updates.append("site_token_encrypted = ?")
        params.append(_encrypt_cred(site_token, key))

    google_credentials = getattr(args, "google_credentials", None)
    if google_credentials is not None:
        updates.append("google_credentials_encrypted = ?")
        params.append(_encrypt_cred(google_credentials, key))

    grade_direction = getattr(args, "grade_direction", None)
    if grade_direction is not None:
        if grade_direction not in VALID_GRADE_DIRECTIONS:
            err(f"--grade-direction must be one of: {', '.join(VALID_GRADE_DIRECTIONS)}")
        updates.append("grade_direction = ?"); params.append(grade_direction)

    has_dpa_signed = getattr(args, "has_dpa_signed", None)
    if has_dpa_signed is not None:
        updates.append("has_dpa_signed = ?"); params.append(int(has_dpa_signed))

    dpa_signed_date = getattr(args, "dpa_signed_date", None)
    if dpa_signed_date is not None:
        updates.append("dpa_signed_date = ?"); params.append(dpa_signed_date)

    is_coppa_verified = getattr(args, "is_coppa_verified", None)
    if is_coppa_verified is not None:
        updates.append("is_coppa_verified = ?"); params.append(int(is_coppa_verified))

    coppa_cert_url = getattr(args, "coppa_cert_url", None)
    if coppa_cert_url is not None:
        updates.append("coppa_cert_url = ?"); params.append(coppa_cert_url)

    default_course_prefix = getattr(args, "default_course_prefix", None)
    if default_course_prefix is not None:
        updates.append("default_course_prefix = ?"); params.append(default_course_prefix)

    auto_push_assignments = getattr(args, "auto_push_assignments", None)
    if auto_push_assignments is not None:
        updates.append("auto_push_assignments = ?"); params.append(int(auto_push_assignments))

    connection_status = getattr(args, "connection_status", None)
    if connection_status is not None:
        if connection_status not in VALID_CONN_STATUSES:
            err(f"--connection-status must be one of: {', '.join(VALID_CONN_STATUSES)}")
        updates.append("status = ?"); params.append(connection_status)

    if not updates:
        err("No fields to update — provide at least one updatable field")

    updates.append("updated_at = ?"); params.append(_now_iso())
    params.append(conn_id)

    conn.execute(
        f"UPDATE educlaw_lms_connection SET {', '.join(updates)} WHERE id = ?",
        params
    )
    try:
        audit(conn, SKILL, "update-lms-connection", "educlaw_lms_connection", conn_id,
              new_values={"fields_updated": [u.split(" =")[0] for u in updates if "updated_at" not in u]})
    except Exception:
        pass
    conn.commit()
    ok({"id": conn_id, "message": "LMS connection updated"})


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: get-lms-connection
# ─────────────────────────────────────────────────────────────────────────────

def get_lms_connection(conn, args):
    """Get full LMS connection details with masked credentials."""
    conn_id = getattr(args, "connection_id", None) or None
    if not conn_id:
        err("--connection-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_lms_connection WHERE id = ?", (conn_id,)
    ).fetchone()
    if not row:
        err(f"LMS connection {conn_id} not found")

    d = dict(row)
    key = _get_encryption_key()

    # Mask credentials — return only last 4 chars
    d["client_secret_masked"] = _mask_cred(_decrypt_cred(d.get("client_secret_encrypted", ""), key))
    d["site_token_masked"] = _mask_cred(_decrypt_cred(d.get("site_token_encrypted", ""), key))
    d["google_credentials_masked"] = _mask_cred(_decrypt_cred(d.get("google_credentials_encrypted", ""), key))

    # Remove raw encrypted values from response
    d.pop("client_secret_encrypted", None)
    d.pop("site_token_encrypted", None)
    d.pop("google_credentials_encrypted", None)

    # Rename status to avoid ok() collision
    d["connection_status"] = d.pop("status", "draft")

    ok(d)


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: list-lms-connections
# ─────────────────────────────────────────────────────────────────────────────

def list_lms_connections(conn, args):
    """List all LMS connections for a company."""
    company_id = getattr(args, "company_id", None) or None
    if not company_id:
        err("--company-id is required")

    lms_type_filter = getattr(args, "lms_type", None) or None
    status_filter = getattr(args, "connection_status", None) or None

    where = ["company_id = ?"]
    params = [company_id]

    if lms_type_filter:
        if lms_type_filter not in VALID_LMS_TYPES:
            err(f"--lms-type must be one of: {', '.join(VALID_LMS_TYPES)}")
        where.append("lms_type = ?"); params.append(lms_type_filter)

    if status_filter:
        if status_filter not in VALID_CONN_STATUSES:
            err(f"--connection-status must be one of: {', '.join(VALID_CONN_STATUSES)}")
        where.append("status = ?"); params.append(status_filter)

    rows = conn.execute(
        f"""SELECT id, naming_series, display_name, lms_type, status,
                   last_sync_at, has_dpa_signed, is_coppa_verified,
                   grade_direction, auto_push_assignments, created_at
            FROM educlaw_lms_connection
            WHERE {' AND '.join(where)}
            ORDER BY created_at DESC""",
        params
    ).fetchall()

    connections = []
    for r in rows:
        d = dict(r)
        d["connection_status"] = d.pop("status")
        connections.append(d)

    ok({"connections": connections, "total": len(connections)})


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: activate-lms-connection
# ─────────────────────────────────────────────────────────────────────────────

def test_lms_connection(conn, args):
    """Test LMS connection credentials via API call."""
    conn_id = getattr(args, "connection_id", None) or None
    if not conn_id:
        err("--connection-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_lms_connection WHERE id = ?", (conn_id,)
    ).fetchone()
    if not row:
        err(f"LMS connection {conn_id} not found")
    row = dict(row)

    # oneroster_csv has no live API to test
    if row.get("lms_type") == "oneroster_csv":
        # Mark as active if DPA is signed, otherwise draft
        dpa_check = _check_dpa(row)
        new_status = "active" if not dpa_check else "draft"
        conn.execute(
            "UPDATE educlaw_lms_connection SET status = ?, lms_site_name = ?, lms_version = ?, updated_at = ? WHERE id = ?",
            (new_status, "OneRoster CSV Export", "1.1", _now_iso(), conn_id)
        )
        conn.commit()
        ok({
            "id": conn_id,
            "connection_status": new_status,
            "site_name": "OneRoster CSV Export",
            "version": "OneRoster 1.1",
            "message": "OneRoster CSV adapter requires no live connection test",
        })

    key = _get_encryption_key()
    try:
        adapter = _get_adapter(row, key)
    except Exception as e:
        err(f"Failed to initialize adapter: {e}")

    result = adapter.test_connection()

    if result.get("success"):
        # Check DPA before marking active
        dpa_err = _check_dpa(row)
        new_status = "active" if not dpa_err else "draft"
        dpa_note = dpa_err or ""

        conn.execute(
            """UPDATE educlaw_lms_connection
               SET status = ?, lms_site_name = ?, lms_version = ?, updated_at = ?
               WHERE id = ?""",
            (new_status, result.get("site_name", ""), result.get("version", ""),
             _now_iso(), conn_id)
        )
        try:
            audit(conn, SKILL, "activate-lms-connection", "educlaw_lms_connection", conn_id,
                  new_values={"connection_status": new_status,
                              "site_name": result.get("site_name", "")})
        except Exception:
            pass
        conn.commit()
        ok({
            "id": conn_id,
            "connection_status": new_status,
            "site_name": result.get("site_name", ""),
            "version": result.get("version", ""),
            "message": "Connection test successful" + (f" — {dpa_note}" if dpa_note else ""),
        })
    else:
        conn.execute(
            "UPDATE educlaw_lms_connection SET status = ?, updated_at = ? WHERE id = ?",
            ("error", _now_iso(), conn_id)
        )
        conn.commit()
        ok({
            "id": conn_id,
            "connection_status": "error",
            "error": result.get("error", "Connection test failed"),
            "message": "Connection test failed — status set to error",
        })


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: apply-course-sync
# ─────────────────────────────────────────────────────────────────────────────

def sync_courses(conn, args):
    """Full roster push for an academic term to the LMS."""
    conn_id = getattr(args, "connection_id", None) or None
    academic_term_id = getattr(args, "academic_term_id", None) or None
    company_id = getattr(args, "company_id", None) or None
    section_id_filter = getattr(args, "section_id", None) or None
    triggered_by = getattr(args, "user_id", None) or "system"

    if not conn_id:
        err("--connection-id is required")
    if not academic_term_id:
        err("--academic-term-id is required")
    if not company_id:
        err("--company-id is required")

    # Load connection
    lms_conn = conn.execute(
        "SELECT * FROM educlaw_lms_connection WHERE id = ?", (conn_id,)
    ).fetchone()
    if not lms_conn:
        err(f"LMS connection {conn_id} not found")
    lms_conn = dict(lms_conn)

    # DPA hard gate
    dpa_err = _check_dpa(lms_conn)
    if dpa_err:
        err(dpa_err)

    # Connection must be active
    if lms_conn.get("status") not in ("active",):
        err(f"LMS connection must be 'active' before syncing (current: {lms_conn.get('status')}). Run activate-lms-connection first.")

    # Validate academic term
    term = conn.execute(
        "SELECT * FROM educlaw_academic_term WHERE id = ? AND company_id = ?",
        (academic_term_id, company_id)
    ).fetchone()
    if not term:
        err(f"Academic term {academic_term_id} not found for company {company_id}")
    term = dict(term)

    # Block concurrent sync runs
    existing_run = conn.execute(
        "SELECT id FROM educlaw_lms_sync_log WHERE lms_connection_id = ? AND status = 'running'",
        (conn_id,)
    ).fetchone()
    if existing_run:
        err(f"A sync run is already in progress (log_id={existing_run[0]}). Wait for it to complete.")

    # Create sync log entry
    log_id = str(uuid.uuid4())
    log_naming = _next_lms_series(
        conn, "educlaw_lms_sync_log", "SYN-", company_id, use_year=True
    )
    now = _now_iso()
    conn.execute(
        """INSERT INTO educlaw_lms_sync_log
           (id, naming_series, lms_connection_id, sync_type, academic_term_id,
            section_id, triggered_by, status, started_at, company_id, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (log_id, log_naming, conn_id, "roster_push", academic_term_id,
         section_id_filter, triggered_by, "running", now, company_id, now, triggered_by)
    )
    conn.commit()

    # Initialize counters and error tracking
    sections_synced = 0
    students_synced = 0
    errors_count = 0
    error_summary = []

    key = _get_encryption_key()
    is_oneroster = lms_conn.get("lms_type") == "oneroster_csv"

    try:
        adapter = None if is_oneroster else _get_adapter(lms_conn, key)
    except Exception as e:
        _finalize_sync_log(conn, log_id, "failed", 0, 0, 0, 0, 0, 1,
                           [{"entity_type": "connection", "entity_id": conn_id,
                             "error_message": str(e)}])
        err(f"Failed to initialize LMS adapter: {e}")

    # Sync academic term/session
    lms_term_id = ""
    if adapter:
        try:
            term_result = adapter.sync_term(term)
            lms_term_id = term_result.get("lms_term_id", "")
        except Exception as e:
            error_summary.append({"entity_type": "term", "entity_id": academic_term_id,
                                  "error_message": str(e)})
            errors_count += 1

    # Load sections
    section_where = "s.academic_term_id = ? AND s.company_id = ?"
    section_params = [academic_term_id, company_id]
    if section_id_filter:
        section_where += " AND s.id = ?"
        section_params.append(section_id_filter)

    sections = conn.execute(
        f"""SELECT s.*, c.course_code, c.name as course_name, c.description as course_desc,
                   c.credit_hours, c.grade_level
            FROM educlaw_section s
            JOIN educlaw_course c ON c.id = s.course_id
            WHERE {section_where} AND s.status NOT IN ('cancelled')""",
        section_params
    ).fetchall()
    sections = [dict(r) for r in sections]

    # ── Sync sections → LMS courses ──────────────────────────────────────────
    section_lms_map = {}  # section_id → lms_course_id
    for section in sections:
        sec_id = section["id"]
        try:
            if adapter:
                course_result = adapter.sync_course(section, {"lms_term_id": lms_term_id}, lms_conn)
                lms_course_id = course_result.get("lms_course_id", "")
                lms_course_url = course_result.get("lms_course_url", "")
            else:
                lms_course_id = f"oneroster_{sec_id[:8]}"
                lms_course_url = ""

            # Insert or update course mapping
            existing_mapping = conn.execute(
                """SELECT id FROM educlaw_lms_course_mapping
                   WHERE lms_connection_id = ? AND section_id = ? AND sync_status != 'closed'""",
                (conn_id, sec_id)
            ).fetchone()

            if existing_mapping:
                # Course mapping already exists — mark as synced
                conn.execute(
                    """UPDATE educlaw_lms_course_mapping
                       SET lms_course_id = ?, lms_course_url = ?, lms_term_id = ?,
                           sync_status = 'synced', last_synced_at = ?, sync_error = ''
                       WHERE id = ?""",
                    (lms_course_id, lms_course_url, lms_term_id, _now_iso(), existing_mapping[0])
                )
            else:
                mapping_id = str(uuid.uuid4())
                try:
                    conn.execute(
                        """INSERT INTO educlaw_lms_course_mapping
                           (id, lms_connection_id, section_id, lms_course_id,
                            lms_course_url, lms_term_id, sync_status, last_synced_at,
                            created_at, created_by)
                           VALUES (?, ?, ?, ?, ?, ?, 'synced', ?, ?, ?)""",
                        (mapping_id, conn_id, sec_id, lms_course_id,
                         lms_course_url, lms_term_id, _now_iso(), _now_iso(), triggered_by)
                    )
                except sqlite3.IntegrityError:
                    # Mapping exists (race condition) — update instead
                    conn.execute(
                        """UPDATE educlaw_lms_course_mapping
                           SET lms_course_id = ?, sync_status = 'synced', last_synced_at = ?
                           WHERE lms_connection_id = ? AND section_id = ?""",
                        (lms_course_id, _now_iso(), conn_id, sec_id)
                    )

            section_lms_map[sec_id] = lms_course_id
            sections_synced += 1
            conn.commit()

        except Exception as e:
            errors_count += 1
            error_summary.append({
                "entity_type": "section",
                "entity_id": sec_id,
                "error_message": str(e),
            })
            # Update mapping with error status
            conn.execute(
                """UPDATE educlaw_lms_course_mapping
                   SET sync_status = 'error', sync_error = ?
                   WHERE lms_connection_id = ? AND section_id = ?""",
                (str(e)[:500], conn_id, sec_id)
            )
            conn.commit()

    # ── Sync students and instructors ────────────────────────────────────────
    is_coppa_lms_verified = int(lms_conn.get("is_coppa_verified", 0) or 0)
    processed_users = set()

    for section in sections:
        sec_id = section["id"]
        lms_course_id = section_lms_map.get(sec_id, "")

        # Load enrolled students for this section
        enrollments = conn.execute(
            """SELECT ce.*, st.first_name, st.last_name, st.is_coppa_applicable,
                      st.directory_info_opt_out, st.customer_id,
                      cust.email as student_email
               FROM educlaw_course_enrollment ce
               JOIN educlaw_student st ON st.id = ce.student_id
               LEFT JOIN customer cust ON cust.id = st.customer_id
               WHERE ce.section_id = ? AND ce.enrollment_status IN ('enrolled', 'completed')""",
            (sec_id,)
        ).fetchall()
        enrollments = [dict(r) for r in enrollments]

        for enr in enrollments:
            student_id = enr["student_id"]
            is_coppa = int(enr.get("is_coppa_applicable", 0) or 0)
            is_dir_restricted = int(enr.get("directory_info_opt_out", 0) or 0)

            # COPPA hard gate
            if is_coppa and not is_coppa_lms_verified:
                errors_count += 1
                error_summary.append({
                    "entity_type": "student",
                    "entity_id": student_id,
                    "error_message": "E_COPPA_UNVERIFIED: Student skipped (is_coppa_applicable=1, connection is_coppa_verified=0)",
                })
                continue

            # Sync user (only once per connection)
            user_key = (conn_id, student_id, "student")
            if user_key not in processed_users:
                try:
                    user_data = {
                        "sis_user_id": student_id,
                        "email": enr.get("student_email", "") or "",
                        "first_name": enr.get("first_name", "") or "",
                        "last_name": enr.get("last_name", "") or "",
                    }
                    if adapter:
                        user_result = adapter.sync_user(user_data, "student", lms_conn)
                        lms_user_id = user_result.get("lms_user_id", "")
                        lms_username = user_result.get("lms_username", "")
                        lms_login_email = user_result.get("lms_login_email", "")
                        user_sync_status = user_result.get("sync_status", "synced")
                    else:
                        lms_user_id = f"oneroster_stu_{student_id[:8]}"
                        lms_username = (enr.get("student_email", "") or student_id)
                        lms_login_email = enr.get("student_email", "") or ""
                        user_sync_status = "synced"

                    # Insert or update user mapping
                    existing_um = conn.execute(
                        """SELECT id FROM educlaw_lms_user_mapping
                           WHERE lms_connection_id = ? AND sis_user_type = 'student' AND sis_user_id = ?""",
                        (conn_id, student_id)
                    ).fetchone()
                    if existing_um:
                        conn.execute(
                            """UPDATE educlaw_lms_user_mapping
                               SET lms_user_id = ?, lms_username = ?, lms_login_email = ?,
                                   is_coppa_restricted = ?, is_directory_restricted = ?,
                                   sync_status = ?, last_synced_at = ?, sync_error = ''
                               WHERE id = ?""",
                            (lms_user_id, lms_username, lms_login_email,
                             is_coppa, is_dir_restricted,
                             user_sync_status, _now_iso(), existing_um[0])
                        )
                    else:
                        um_id = str(uuid.uuid4())
                        try:
                            conn.execute(
                                """INSERT INTO educlaw_lms_user_mapping
                                   (id, lms_connection_id, sis_user_type, sis_user_id,
                                    lms_user_id, lms_username, lms_login_email,
                                    is_coppa_restricted, is_directory_restricted,
                                    sync_status, last_synced_at, created_at, created_by)
                                   VALUES (?, ?, 'student', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                (um_id, conn_id, student_id, lms_user_id,
                                 lms_username, lms_login_email,
                                 is_coppa, is_dir_restricted,
                                 user_sync_status, _now_iso(), _now_iso(), triggered_by)
                            )
                        except sqlite3.IntegrityError:
                            pass  # Already exists

                    processed_users.add(user_key)
                    students_synced += 1

                    # FERPA disclosure log
                    _log_ferpa_access(
                        conn, student_id, company_id,
                        f"LMS roster disclosure to {lms_conn.get('display_name', 'LMS')}",
                        triggered_by
                    )
                    conn.commit()

                except Exception as e:
                    errors_count += 1
                    error_summary.append({
                        "entity_type": "student",
                        "entity_id": student_id,
                        "error_message": str(e),
                    })

            # Sync enrollment
            if lms_course_id and adapter:
                existing_um = conn.execute(
                    """SELECT lms_user_id FROM educlaw_lms_user_mapping
                       WHERE lms_connection_id = ? AND sis_user_type = 'student' AND sis_user_id = ?""",
                    (conn_id, student_id)
                ).fetchone()
                if existing_um:
                    try:
                        is_google = lms_conn.get("lms_type") == "google_classroom"
                        role = "STUDENT" if is_google else "StudentEnrollment"
                        enr_result = adapter.sync_enrollment({
                            "lms_course_id": lms_course_id,
                            "lms_user_id": existing_um[0],
                            "role": role,
                        }, lms_conn)
                        # Update user mapping sync_status for Google invited state
                        if is_google and enr_result.get("enrollment_status") == "invited":
                            conn.execute(
                                """UPDATE educlaw_lms_user_mapping
                                   SET sync_status = 'invited'
                                   WHERE lms_connection_id = ? AND sis_user_type = 'student' AND sis_user_id = ?""",
                                (conn_id, student_id)
                            )
                        conn.commit()
                    except Exception as e:
                        errors_count += 1
                        error_summary.append({
                            "entity_type": "enrollment",
                            "entity_id": f"{student_id}:{sec_id}",
                            "error_message": str(e),
                        })

        # Sync instructor
        instructor_id = section.get("instructor_id")
        if instructor_id:
            instr_row = conn.execute(
                """SELECT i.id, e.first_name, e.last_name, e.work_email
                   FROM educlaw_instructor i
                   JOIN employee e ON e.id = i.employee_id
                   WHERE i.id = ?""",
                (instructor_id,)
            ).fetchone()
            if instr_row:
                instr_row = dict(instr_row)
                instr_key = (conn_id, instructor_id, "instructor")
                if instr_key not in processed_users:
                    try:
                        user_data = {
                            "sis_user_id": instructor_id,
                            "email": instr_row.get("work_email", "") or "",
                            "first_name": instr_row.get("first_name", "") or "",
                            "last_name": instr_row.get("last_name", "") or "",
                        }
                        if adapter:
                            ur = adapter.sync_user(user_data, "instructor", lms_conn)
                            lms_uid = ur.get("lms_user_id", "")
                            lms_uname = ur.get("lms_username", "")
                            lms_lemail = ur.get("lms_login_email", "")
                        else:
                            lms_uid = f"oneroster_instr_{instructor_id[:8]}"
                            lms_uname = instr_row.get("work_email", "") or instructor_id
                            lms_lemail = instr_row.get("work_email", "") or ""

                        existing_ium = conn.execute(
                            """SELECT id FROM educlaw_lms_user_mapping
                               WHERE lms_connection_id = ? AND sis_user_type = 'instructor' AND sis_user_id = ?""",
                            (conn_id, instructor_id)
                        ).fetchone()
                        if existing_ium:
                            conn.execute(
                                """UPDATE educlaw_lms_user_mapping
                                   SET lms_user_id = ?, lms_username = ?, lms_login_email = ?,
                                       sync_status = 'synced', last_synced_at = ?
                                   WHERE id = ?""",
                                (lms_uid, lms_uname, lms_lemail, _now_iso(), existing_ium[0])
                            )
                        else:
                            iim_id = str(uuid.uuid4())
                            try:
                                conn.execute(
                                    """INSERT INTO educlaw_lms_user_mapping
                                       (id, lms_connection_id, sis_user_type, sis_user_id,
                                        lms_user_id, lms_username, lms_login_email,
                                        is_coppa_restricted, is_directory_restricted,
                                        sync_status, last_synced_at, created_at, created_by)
                                       VALUES (?, ?, 'instructor', ?, ?, ?, ?, 0, 0, 'synced', ?, ?, ?)""",
                                    (iim_id, conn_id, instructor_id, lms_uid,
                                     lms_uname, lms_lemail, _now_iso(), _now_iso(), triggered_by)
                                )
                            except sqlite3.IntegrityError:
                                pass

                        processed_users.add(instr_key)

                        # Sync instructor enrollment
                        if lms_course_id and adapter:
                            is_google = lms_conn.get("lms_type") == "google_classroom"
                            role = "TEACHER" if is_google else "TeacherEnrollment"
                            adapter.sync_enrollment({
                                "lms_course_id": lms_course_id,
                                "lms_user_id": lms_uid,
                                "role": role,
                            }, lms_conn)
                        conn.commit()
                    except Exception as e:
                        errors_count += 1
                        error_summary.append({
                            "entity_type": "instructor",
                            "entity_id": instructor_id,
                            "error_message": str(e),
                        })

    # Determine final status
    if errors_count == 0:
        final_status = "completed"
    elif sections_synced > 0 or students_synced > 0:
        final_status = "completed_with_errors"
    else:
        final_status = "failed"

    completed_at = _now_iso()
    _finalize_sync_log(
        conn, log_id, final_status,
        sections_synced, students_synced, 0, 0, 0, errors_count, error_summary,
        completed_at
    )

    # Update last_sync_at on connection
    conn.execute(
        "UPDATE educlaw_lms_connection SET last_sync_at = ?, updated_at = ? WHERE id = ?",
        (_now_iso(), _now_iso(), conn_id)
    )
    conn.commit()

    ok({
        "sync_log_id": log_id,
        "naming_series": log_naming,
        "sync_status": final_status,
        "sections_synced": sections_synced,
        "students_synced": students_synced,
        "errors_count": errors_count,
        "error_summary": error_summary[:10],  # Return first 10 errors
        "message": f"Roster sync {final_status}",
    })


def _finalize_sync_log(conn, log_id, final_status,
                        sections_synced, students_synced,
                        grades_pulled, grades_applied, conflicts_flagged,
                        errors_count, error_summary, completed_at=None):
    """Update sync log record with final counts and status."""
    completed_at = completed_at or _now_iso()
    conn.execute(
        """UPDATE educlaw_lms_sync_log
           SET status = ?, sections_synced = ?, students_synced = ?,
               grades_pulled = ?, grades_applied = ?, conflicts_flagged = ?,
               errors_count = ?, error_summary = ?, completed_at = ?
           WHERE id = ?""",
        (final_status, sections_synced, students_synced,
         grades_pulled, grades_applied, conflicts_flagged,
         errors_count, json.dumps(error_summary), completed_at, log_id)
    )
    conn.commit()


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: list-sync-logs
# ─────────────────────────────────────────────────────────────────────────────

def list_sync_logs(conn, args):
    """List sync run history with optional filters."""
    conn_id = getattr(args, "connection_id", None) or None
    if not conn_id:
        err("--connection-id is required")

    sync_type_filter = getattr(args, "sync_type", None) or None
    sync_status_filter = getattr(args, "sync_status", None) or None
    from_date = getattr(args, "from_date", None) or None
    to_date = getattr(args, "to_date", None) or None
    limit = int(getattr(args, "limit", None) or 50)

    where = ["lms_connection_id = ?"]
    params = [conn_id]

    if sync_type_filter:
        if sync_type_filter not in VALID_SYNC_TYPES:
            err(f"--sync-type must be one of: {', '.join(VALID_SYNC_TYPES)}")
        where.append("sync_type = ?"); params.append(sync_type_filter)

    if sync_status_filter:
        if sync_status_filter not in VALID_SYNC_STATUSES:
            err(f"--sync-status must be one of: {', '.join(VALID_SYNC_STATUSES)}")
        where.append("status = ?"); params.append(sync_status_filter)

    if from_date:
        where.append("created_at >= ?"); params.append(from_date)
    if to_date:
        where.append("created_at <= ?"); params.append(to_date)

    rows = conn.execute(
        f"""SELECT id, naming_series, sync_type, status, academic_term_id,
                   section_id, triggered_by, sections_synced, students_synced,
                   grades_pulled, grades_applied, conflicts_flagged, errors_count,
                   started_at, completed_at, duration_seconds, created_at
            FROM educlaw_lms_sync_log
            WHERE {' AND '.join(where)}
            ORDER BY created_at DESC
            LIMIT ?""",
        params + [limit]
    ).fetchall()

    logs = []
    for r in rows:
        d = dict(r)
        d["sync_status"] = d.pop("status")
        logs.append(d)

    ok({"sync_logs": logs, "total": len(logs)})


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: get-sync-log
# ─────────────────────────────────────────────────────────────────────────────

def get_sync_log(conn, args):
    """Get full sync run details including error_summary."""
    log_id = getattr(args, "sync_log_id", None) or None
    if not log_id:
        err("--sync-log-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_lms_sync_log WHERE id = ?", (log_id,)
    ).fetchone()
    if not row:
        err(f"Sync log {log_id} not found")

    d = dict(row)
    # Parse error_summary JSON
    try:
        d["error_summary"] = json.loads(d.get("error_summary", "[]") or "[]")
    except (json.JSONDecodeError, TypeError):
        d["error_summary"] = []
    d["sync_status"] = d.pop("status")
    ok(d)


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: apply-sync-resolution
# ─────────────────────────────────────────────────────────────────────────────

def resolve_sync_conflict(conn, args):
    """Resolve a user mapping or enrollment conflict."""
    conn_id = getattr(args, "connection_id", None) or None
    entity_type = getattr(args, "entity_type", None) or None
    entity_id = getattr(args, "entity_id", None) or None
    resolution = getattr(args, "resolution", None) or None

    if not conn_id:
        err("--connection-id is required")
    if not entity_type or entity_type not in VALID_ENTITY_TYPES:
        err(f"--entity-type must be one of: {', '.join(VALID_ENTITY_TYPES)}")
    if not entity_id:
        err("--entity-id is required")
    if not resolution or resolution not in VALID_RESOLUTIONS:
        err(f"--resolution must be one of: {', '.join(VALID_RESOLUTIONS)}")

    now = _now_iso()

    if entity_type == "user":
        # entity_id is the sis_user_id (or user_mapping id)
        row = conn.execute(
            """SELECT * FROM educlaw_lms_user_mapping
               WHERE lms_connection_id = ? AND (id = ? OR sis_user_id = ?)""",
            (conn_id, entity_id, entity_id)
        ).fetchone()
        if not row:
            err(f"User mapping not found for entity_id={entity_id} on connection {conn_id}")
        row = dict(row)

        new_status = "synced"
        if resolution == "dismiss":
            new_status = "synced"
        elif resolution == "sis_wins":
            new_status = "pending"  # Will be re-pushed on next sync
        elif resolution == "lms_wins":
            new_status = "synced"

        conn.execute(
            "UPDATE educlaw_lms_user_mapping SET sync_status = ?, sync_error = '', last_synced_at = ? WHERE id = ?",
            (new_status, now, row["id"])
        )
        try:
            audit(conn, SKILL, "apply-sync-resolution", "educlaw_lms_user_mapping", row["id"],
                  new_values={"resolution": resolution, "sync_status": new_status})
        except Exception:
            pass
        conn.commit()
        ok({
            "entity_type": "user",
            "entity_id": entity_id,
            "resolution": resolution,
            "sync_status": new_status,
            "message": f"User mapping conflict resolved: {resolution}",
        })

    elif entity_type == "course":
        # entity_id is the section_id or course_mapping id
        row = conn.execute(
            """SELECT * FROM educlaw_lms_course_mapping
               WHERE lms_connection_id = ? AND (id = ? OR section_id = ?)
               AND sync_status != 'closed'""",
            (conn_id, entity_id, entity_id)
        ).fetchone()
        if not row:
            err(f"Course mapping not found for entity_id={entity_id} on connection {conn_id}")
        row = dict(row)

        new_status = "synced"
        if resolution == "dismiss":
            new_status = "synced"
        elif resolution == "sis_wins":
            new_status = "pending"  # Mark for re-sync
        elif resolution == "lms_wins":
            new_status = "synced"

        conn.execute(
            "UPDATE educlaw_lms_course_mapping SET sync_status = ?, sync_error = '', last_synced_at = ? WHERE id = ?",
            (new_status, now, row["id"])
        )
        try:
            audit(conn, SKILL, "apply-sync-resolution", "educlaw_lms_course_mapping", row["id"],
                  new_values={"resolution": resolution, "sync_status": new_status})
        except Exception:
            pass
        conn.commit()
        ok({
            "entity_type": "course",
            "entity_id": entity_id,
            "resolution": resolution,
            "sync_status": new_status,
            "message": f"Course mapping conflict resolved: {resolution}",
        })


# ─────────────────────────────────────────────────────────────────────────────
# ACTIONS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

ACTIONS = {
    "add-lms-connection": add_lms_connection,
    "update-lms-connection": update_lms_connection,
    "get-lms-connection": get_lms_connection,
    "list-lms-connections": list_lms_connections,
    "activate-lms-connection": test_lms_connection,
    "apply-course-sync": sync_courses,
    "list-sync-logs": list_sync_logs,
    "get-sync-log": get_sync_log,
    "apply-sync-resolution": resolve_sync_conflict,
}
