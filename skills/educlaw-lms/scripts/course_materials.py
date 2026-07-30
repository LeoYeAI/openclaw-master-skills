"""EduClaw LMS Integration — course_materials domain module

Actions for SIS-side course document and resource tracking.

Actions (5):
  add-course-material, update-course-material, list-course-materials,
  get-course-material, delete-course-material

Imported by db_query.py (unified router).
"""
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
except ImportError:
    pass

SKILL = "educlaw-lms"
_now_iso = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

VALID_MATERIAL_TYPES = ("syllabus", "reading", "video_link", "assignment_guide", "rubric", "other")
VALID_ACCESS_TYPES = ("url", "file_attachment", "lms_linked")
VALID_MATERIAL_STATUSES = ("active", "archived")


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: add-course-material
# ─────────────────────────────────────────────────────────────────────────────

def add_course_material(conn, args):
    """Create a course material record for a section."""
    section_id = getattr(args, "section_id", None) or None
    name = getattr(args, "name", None) or None
    material_type = getattr(args, "material_type", None) or None
    access_type = getattr(args, "access_type", None) or None
    company_id = getattr(args, "company_id", None) or None

    if not section_id:
        err("--section-id is required")
    if not name:
        err("--name is required")
    if not material_type:
        err("--material-type is required")
    if material_type not in VALID_MATERIAL_TYPES:
        err(f"--material-type must be one of: {', '.join(VALID_MATERIAL_TYPES)}")
    if not access_type:
        err("--access-type is required")
    if access_type not in VALID_ACCESS_TYPES:
        err(f"--access-type must be one of: {', '.join(VALID_ACCESS_TYPES)}")
    if not company_id:
        err("--company-id is required")

    # Validate section exists and is active
    section = conn.execute(
        "SELECT id, status FROM educlaw_section WHERE id = ?", (section_id,)
    ).fetchone()
    if not section:
        err(f"Section {section_id} not found")
    if dict(section).get("status") in ("cancelled",):
        err(f"Section {section_id} is cancelled — cannot add materials")

    # Validate company
    if not conn.execute("SELECT id FROM company WHERE id = ?", (company_id,)).fetchone():
        err(f"Company {company_id} not found")

    # Optional fields
    assessment_id = getattr(args, "assessment_id", None) or None
    external_url = getattr(args, "external_url", None) or ""
    file_path_val = getattr(args, "file_path", None) or ""
    lms_connection_id = getattr(args, "lms_connection_id", None) or None
    is_visible_to_students = int(getattr(args, "is_visible_to_students", None) or 1)
    available_from = getattr(args, "available_from", None) or ""
    available_until = getattr(args, "available_until", None) or ""
    sort_order = int(getattr(args, "sort_order", None) or 0)
    description = getattr(args, "description", None) or ""

    # Validate access_type-specific requirements
    if access_type == "url" and not external_url:
        err("--external-url is required for access_type 'url'")
    if access_type == "file_attachment" and not file_path_val:
        err("--file-path is required for access_type 'file_attachment'")
    if access_type == "lms_linked" and not lms_connection_id:
        err("--lms-connection-id is required for access_type 'lms_linked'")

    # Validate optional FK: assessment_id
    if assessment_id:
        if not conn.execute("SELECT id FROM educlaw_assessment WHERE id = ?", (assessment_id,)).fetchone():
            err(f"Assessment {assessment_id} not found")

    # Validate optional FK: lms_connection_id
    if lms_connection_id:
        if not conn.execute("SELECT id FROM educlaw_lms_connection WHERE id = ?", (lms_connection_id,)).fetchone():
            err(f"LMS connection {lms_connection_id} not found")

    # Validate date range
    if available_from and available_until:
        if available_until < available_from:
            err("--available-until cannot be before --available-from")

    material_id = str(uuid.uuid4())
    now = _now_iso()

    # For lms_linked: fetch LMS file metadata (stub — would call adapter in full implementation)
    lms_file_id = ""
    lms_download_url = ""
    # In production, if access_type == 'lms_linked', we'd call adapter.get_file_metadata(...)

    try:
        conn.execute(
            """INSERT INTO educlaw_lms_course_material
               (id, section_id, assessment_id, name, description, material_type,
                access_type, external_url, file_path, lms_connection_id,
                lms_file_id, lms_download_url, is_visible_to_students,
                available_from, available_until, sort_order,
                status, company_id, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, ?, ?)""",
            (material_id, section_id, assessment_id, name, description,
             material_type, access_type, external_url, file_path_val,
             lms_connection_id, lms_file_id, lms_download_url,
             is_visible_to_students, available_from, available_until,
             sort_order, company_id, now, now,
             getattr(args, "user_id", None) or "")
        )
    except sqlite3.IntegrityError as e:
        err(f"Failed to create course material: {e}")

    try:
        audit(conn, SKILL, "add-course-material", "educlaw_lms_course_material", material_id,
              new_values={"name": name, "material_type": material_type, "access_type": access_type})
    except Exception:
        pass
    conn.commit()
    ok({
        "id": material_id,
        "section_id": section_id,
        "name": name,
        "material_type": material_type,
        "access_type": access_type,
        "material_status": "active",
        "message": "Course material created",
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: update-course-material
# ─────────────────────────────────────────────────────────────────────────────

def update_course_material(conn, args):
    """Update course material metadata."""
    material_id = getattr(args, "material_id", None) or None
    if not material_id:
        err("--material-id is required")

    material = conn.execute(
        "SELECT * FROM educlaw_lms_course_material WHERE id = ?", (material_id,)
    ).fetchone()
    if not material:
        err(f"Course material {material_id} not found")
    material = dict(material)

    if material.get("status") == "archived":
        err("Cannot update an archived course material")

    updates, params = [], []

    # Fields that can be updated (cannot change section_id)
    for field_name, arg_name in [
        ("name", "name"),
        ("description", "description"),
        ("external_url", "external_url"),
        ("file_path", "file_path"),
        ("lms_file_id", "lms_file_id"),
        ("lms_download_url", "lms_download_url"),
        ("available_from", "available_from"),
        ("available_until", "available_until"),
    ]:
        val = getattr(args, arg_name, None)
        if val is not None:
            updates.append(f"{field_name} = ?"); params.append(val)

    # Boolean / integer fields
    is_visible = getattr(args, "is_visible_to_students", None)
    if is_visible is not None:
        updates.append("is_visible_to_students = ?"); params.append(int(is_visible))

    sort_order = getattr(args, "sort_order", None)
    if sort_order is not None:
        updates.append("sort_order = ?"); params.append(int(sort_order))

    # Enum fields with validation
    material_type = getattr(args, "material_type", None)
    if material_type is not None:
        if material_type not in VALID_MATERIAL_TYPES:
            err(f"--material-type must be one of: {', '.join(VALID_MATERIAL_TYPES)}")
        updates.append("material_type = ?"); params.append(material_type)

    access_type = getattr(args, "access_type", None)
    if access_type is not None:
        if access_type not in VALID_ACCESS_TYPES:
            err(f"--access-type must be one of: {', '.join(VALID_ACCESS_TYPES)}")
        updates.append("access_type = ?"); params.append(access_type)

    if not updates:
        err("No fields to update")

    # Validate date range if both provided
    new_from = getattr(args, "available_from", None)
    new_until = getattr(args, "available_until", None)
    check_from = new_from or material.get("available_from", "")
    check_until = new_until or material.get("available_until", "")
    if check_from and check_until and check_until < check_from:
        err("--available-until cannot be before --available-from")

    updates.append("updated_at = ?"); params.append(_now_iso())
    params.append(material_id)

    conn.execute(
        f"UPDATE educlaw_lms_course_material SET {', '.join(updates)} WHERE id = ?",
        params
    )
    try:
        audit(conn, SKILL, "update-course-material", "educlaw_lms_course_material", material_id,
              new_values={"fields_updated": [u.split(" =")[0] for u in updates if "updated_at" not in u]})
    except Exception:
        pass
    conn.commit()
    ok({"id": material_id, "message": "Course material updated"})


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: list-course-materials
# ─────────────────────────────────────────────────────────────────────────────

def list_course_materials(conn, args):
    """List materials for a section."""
    section_id = getattr(args, "section_id", None) or None
    if not section_id:
        err("--section-id is required")

    material_type_filter = getattr(args, "material_type", None) or None
    is_visible_filter = getattr(args, "is_visible_to_students", None)
    include_archived = getattr(args, "include_archived", None) or False

    where = ["section_id = ?"]
    params = [section_id]

    if not include_archived:
        where.append("status = 'active'")

    if material_type_filter:
        if material_type_filter not in VALID_MATERIAL_TYPES:
            err(f"--material-type must be one of: {', '.join(VALID_MATERIAL_TYPES)}")
        where.append("material_type = ?"); params.append(material_type_filter)

    if is_visible_filter is not None:
        where.append("is_visible_to_students = ?"); params.append(int(is_visible_filter))

    rows = conn.execute(
        f"""SELECT id, section_id, assessment_id, name, description, material_type,
                   access_type, external_url, file_path, lms_connection_id,
                   lms_file_id, lms_download_url, is_visible_to_students,
                   available_from, available_until, sort_order, status, created_at
            FROM educlaw_lms_course_material
            WHERE {' AND '.join(where)}
            ORDER BY sort_order ASC, created_at ASC""",
        params
    ).fetchall()

    materials = []
    for r in rows:
        d = dict(r)
        d["material_status"] = d.pop("status")
        materials.append(d)

    ok({"materials": materials, "total": len(materials)})


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: get-course-material
# ─────────────────────────────────────────────────────────────────────────────

def get_course_material(conn, args):
    """Get full course material record."""
    material_id = getattr(args, "material_id", None) or None
    if not material_id:
        err("--material-id is required")

    row = conn.execute(
        "SELECT * FROM educlaw_lms_course_material WHERE id = ?", (material_id,)
    ).fetchone()
    if not row:
        err(f"Course material {material_id} not found")

    d = dict(row)
    d["material_status"] = d.pop("status")
    ok(d)


# ─────────────────────────────────────────────────────────────────────────────
# ACTION: delete-course-material
# ─────────────────────────────────────────────────────────────────────────────

def delete_course_material(conn, args):
    """Archive (soft-delete) a course material."""
    material_id = getattr(args, "material_id", None) or None
    if not material_id:
        err("--material-id is required")

    row = conn.execute(
        "SELECT id, name, status FROM educlaw_lms_course_material WHERE id = ?", (material_id,)
    ).fetchone()
    if not row:
        err(f"Course material {material_id} not found")
    row = dict(row)

    if row.get("status") == "archived":
        ok({
            "id": material_id,
            "material_status": "archived",
            "message": "Course material is already archived",
        })

    conn.execute(
        "UPDATE educlaw_lms_course_material SET status = 'archived', updated_at = ? WHERE id = ?",
        (_now_iso(), material_id)
    )
    try:
        audit(conn, SKILL, "delete-course-material", "educlaw_lms_course_material", material_id,
              new_values={"material_status": "archived"})
    except Exception:
        pass
    conn.commit()
    ok({
        "id": material_id,
        "name": row.get("name", ""),
        "material_status": "archived",
        "message": "Course material archived",
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACTIONS REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

ACTIONS = {
    "add-course-material": add_course_material,
    "update-course-material": update_course_material,
    "list-course-materials": list_course_materials,
    "get-course-material": get_course_material,
    "delete-course-material": delete_course_material,
}
