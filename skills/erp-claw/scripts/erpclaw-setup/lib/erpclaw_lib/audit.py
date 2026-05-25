"""Shared audit logging for ERPClaw skill scripts.

Replaces the _audit() function that was duplicated (with only the skill
name differing) across all 24 skill db_query.py files.

Usage:
    from erpclaw_lib.audit import audit
    audit(conn, "erpclaw-selling", "add-customer", "customer", cust_id,
          new_values={"name": "Acme"}, description="Created customer")
"""
import json
import os
import uuid


def audit(conn, skill: str, action: str, entity_type: str, entity_id: str,
          old_values=None, new_values=None, description: str = ""):
    """Write an audit log entry.

    Args:
        conn: Active sqlite3 connection (caller manages the transaction).
        skill: Skill name, e.g. 'erpclaw-selling'.
        action: Action that triggered the audit, e.g. 'add-customer'.
        entity_type: Type of entity affected, e.g. 'customer'.
        entity_id: Primary key of the affected entity.
        old_values: Dict of previous values (optional, JSON-serialized).
        new_values: Dict of new values (optional, JSON-serialized).
        description: Human-readable description of the change.
    """
    conn.execute(
        """INSERT INTO audit_log (id, user_id, skill, action, entity_type, entity_id,
           old_values, new_values, description)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            str(uuid.uuid4()),
            os.environ.get("OPENCLAW_USER"),
            skill,
            action,
            entity_type,
            entity_id,
            json.dumps(old_values) if old_values else None,
            json.dumps(new_values) if new_values else None,
            description,
        ),
    )
