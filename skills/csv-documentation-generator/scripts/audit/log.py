"""Audit Log module for CSV Documentation Generator

Maintains audit trail of all actions and exports to PDF for compliance.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class AuditEntry:
    """Represents a single audit log entry"""

    timestamp: str
    action: str
    mode: str  # autonomous, interactive
    user: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None


class AuditLogger:
    """Maintain audit trail for compliance"""

    def __init__(self, project_path: Optional[Path] = None):
        self.project_path = project_path or Path.cwd()
        self.audit_log = self._load_audit_log()

    def _load_audit_log(self) -> List[Dict[str, Any]]:
        """Load audit log from file"""
        log_path = self.project_path / "audit-log.json"
        if log_path.exists():
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def _save_audit_log(self):
        """Save audit log to file"""
        log_path = self.project_path / "audit-log.json"
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(self.audit_log, f, indent=2, ensure_ascii=False)

    def log(
        self,
        action: str,
        mode: str,
        details: Dict[str, Any] = None,
        entity_type: str = None,
        entity_id: str = None,
        user: str = None,
    ) -> AuditEntry:
        """Add an audit log entry"""
        entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            action=action,
            mode=mode,
            user=user,
            details=details or {},
            entity_type=entity_type,
            entity_id=entity_id,
        )

        self.audit_log.append(asdict(entry))
        self._save_audit_log()

        return entry

    def log_requirement_added(self, requirement_id: str, description: str, mode: str):
        """Log requirement added"""
        self.log(
            action="requirement_added",
            mode=mode,
            details={"id": requirement_id, "description": description},
            entity_type="requirement",
            entity_id=requirement_id,
        )

    def log_requirement_updated(self, requirement_id: str, changes: Dict, mode: str):
        """Log requirement updated"""
        self.log(
            action="requirement_updated",
            mode=mode,
            details={"id": requirement_id, "changes": changes},
            entity_type="requirement",
            entity_id=requirement_id,
        )

    def log_risk_assessed(self, risk_id: str, rpn: int, level: str, mode: str):
        """Log risk assessment"""
        self.log(
            action="risk_assessed",
            mode=mode,
            details={"id": risk_id, "rpn": rpn, "level": level},
            entity_type="risk",
            entity_id=risk_id,
        )

    def log_test_result_added(self, test_id: str, status: str, mode: str):
        """Log test result"""
        self.log(
            action="test_result_added",
            mode=mode,
            details={"id": test_id, "status": status},
            entity_type="test_result",
            entity_id=test_id,
        )

    def log_commit_linked(self, commit_hash: str, requirements: List[str], mode: str):
        """Log commit linked to requirements"""
        self.log(
            action="commit_linked",
            mode=mode,
            details={"commit": commit_hash, "requirements": requirements},
            entity_type="commit",
            entity_id=commit_hash[:8],
        )

    def log_document_generated(self, doc_type: str, auto_filled: bool, mode: str):
        """Log document generation"""
        self.log(
            action="document_generated",
            mode=mode,
            details={"doc_type": doc_type, "auto_filled": auto_filled},
            entity_type="document",
            entity_id=doc_type,
        )

    def get_entries(
        self,
        action: str = None,
        entity_type: str = None,
        entity_id: str = None,
        start_date: str = None,
        end_date: str = None,
    ) -> List[AuditEntry]:
        """Get audit entries with optional filters"""
        entries = [AuditEntry(**e) for e in self.audit_log]

        if action:
            entries = [e for e in entries if e.action == action]

        if entity_type:
            entries = [e for e in entries if e.entity_type == entity_type]

        if entity_id:
            entries = [e for e in entries if e.entity_id == entity_id]

        if start_date:
            entries = [e for e in entries if e.timestamp >= start_date]

        if end_date:
            entries = [e for e in entries if e.timestamp <= end_date]

        return entries

    def get_summary(self) -> Dict[str, Any]:
        """Get audit log summary"""
        total = len(self.audit_log)

        by_action = {}
        by_mode = {}

        for entry in self.audit_log:
            action = entry.get("action", "unknown")
            mode = entry.get("mode", "unknown")

            by_action[action] = by_action.get(action, 0) + 1
            by_mode[mode] = by_mode.get(mode, 0) + 1

        return {
            "total_entries": total,
            "by_action": by_action,
            "by_mode": by_mode,
            "first_entry": self.audit_log[0]["timestamp"] if self.audit_log else None,
            "last_entry": self.audit_log[-1]["timestamp"] if self.audit_log else None,
        }

    def export_to_pdf(self, output_path: Path = None) -> Path:
        """Export audit log to PDF for compliance

        This is a placeholder - actual PDF generation would require
        a library like reportlab or weasyprint.
        """
        if output_path is None:
            output_path = (
                self.project_path / f"audit-log-{datetime.now().strftime('%Y%m%d')}.pdf"
            )

        # For now, export as formatted text
        txt_path = output_path.with_suffix(".txt")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("CSV DOCUMENTATION GENERATOR - AUDIT LOG\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")

            for entry in self.audit_log:
                f.write(f"Timestamp: {entry['timestamp']}\n")
                f.write(f"Action: {entry['action']}\n")
                f.write(f"Mode: {entry['mode']}\n")
                if entry.get("user"):
                    f.write(f"User: {entry['user']}\n")
                if entry.get("entity_type"):
                    f.write(
                        f"Entity: {entry['entity_type']} / {entry.get('entity_id')}\n"
                    )
                if entry.get("details"):
                    f.write(
                        f"Details: {json.dumps(entry['details'], ensure_ascii=False)}\n"
                    )
                f.write("-" * 40 + "\n")

            f.write(f"\nTotal Entries: {len(self.audit_log)}\n")

        return txt_path

    def clear_old_entries(self, days: int = 90) -> int:
        """Clear entries older than specified days

        Note: For compliance, you may want to archive rather than delete.
        """
        from datetime import timedelta

        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        initial_count = len(self.audit_log)

        self.audit_log = [e for e in self.audit_log if e.get("timestamp", "") >= cutoff]

        removed = initial_count - len(self.audit_log)
        self._save_audit_log()

        return removed
