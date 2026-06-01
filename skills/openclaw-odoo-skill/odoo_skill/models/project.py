"""
Project and Task management operations for Odoo ``project.project``,
``project.task``, and ``account.analytic.line`` (timesheets).
"""

import logging
from typing import Any, Optional

from ..client import OdooClient

logger = logging.getLogger("odoo_skill")

_PROJECT_LIST_FIELDS = [
    "id", "name", "user_id", "partner_id", "date_start",
    "date", "task_count", "active", "company_id",
]

_PROJECT_DETAIL_FIELDS = _PROJECT_LIST_FIELDS + [
    "description", "tag_ids", "type_ids",
    "allow_timesheets", "allow_billable",
]

_TASK_LIST_FIELDS = [
    "id", "name", "project_id", "user_ids", "stage_id",
    "priority", "date_deadline",
    "tag_ids", "active",
]

_TASK_DETAIL_FIELDS = _TASK_LIST_FIELDS + [
    "description", "parent_id", "child_ids",
    "date_assign", "create_date", "write_date",
    "partner_id",
]

_TIMESHEET_FIELDS = [
    "id", "name", "project_id", "task_id",
    "unit_amount", "date", "user_id", "employee_id",
]


class ProjectOps:
    """High-level operations for Odoo projects and tasks.

    Args:
        client: An authenticated :class:`OdooClient` instance.
    """

    PROJECT_MODEL = "project.project"
    TASK_MODEL = "project.task"
    STAGE_MODEL = "project.task.type"
    TIMESHEET_MODEL = "account.analytic.line"

    def __init__(self, client: OdooClient) -> None:
        self.client = client

    # ── Project CRUD ─────────────────────────────────────────────────

    def create_project(
        self,
        name: str,
        partner_id: Optional[int] = None,
        description: Optional[str] = None,
        allow_timesheets: bool = True,
        **extra: Any,
    ) -> dict:
        """Create a new project.

        Args:
            name: Project name.
            partner_id: Customer associated with the project.
            description: Project description.
            allow_timesheets: Whether timesheets are enabled.
            **extra: Additional ``project.project`` field values.

        Returns:
            The newly created project record.
        """
        values: dict[str, Any] = {
            "name": name,
            "allow_timesheets": allow_timesheets,
        }
        if partner_id:
            values["partner_id"] = partner_id
        if description:
            values["description"] = description
        values.update(extra)

        project_id = self.client.create(self.PROJECT_MODEL, values)
        logger.info("Created project %r → id=%d", name, project_id)
        return self._read_project(project_id)

    def get_project(self, project_id: int) -> dict:
        """Get full details of a project.

        Args:
            project_id: The project ID.

        Returns:
            Project record dict, or empty dict if not found.
        """
        return self._read_project(project_id)

    def search_projects(
        self,
        query: Optional[str] = None,
        partner_id: Optional[int] = None,
        limit: int = 20,
    ) -> list[dict]:
        """Search projects by name or customer.

        Args:
            query: Text to search in project name.
            partner_id: Filter by associated customer.
            limit: Max results.

        Returns:
            List of project records.
        """
        domain: list = [["active", "=", True]]
        if query:
            domain.append(["name", "ilike", query])
        if partner_id:
            domain.append(["partner_id", "=", partner_id])

        return self.client.search_read(
            self.PROJECT_MODEL, domain,
            fields=_PROJECT_LIST_FIELDS, limit=limit,
            order="name asc",
        )

    # ── Task CRUD ────────────────────────────────────────────────────

    def create_task(
        self,
        project_id: int,
        name: str,
        user_ids: Optional[list[int]] = None,
        description: Optional[str] = None,
        date_deadline: Optional[str] = None,
        priority: Optional[str] = None,
        **extra: Any,
    ) -> dict:
        """Create a task within a project.

        Args:
            project_id: The project to create the task in.
            name: Task name/title.
            user_ids: List of assigned user IDs.
            description: Task description (HTML supported).
            date_deadline: Due date as ``YYYY-MM-DD``.
            priority: Priority level (``'0'`` = normal, ``'1'`` = urgent).
            **extra: Additional ``project.task`` field values.

        Returns:
            The newly created task record.
        """
        values: dict[str, Any] = {
            "project_id": project_id,
            "name": name,
        }
        if user_ids:
            values["user_ids"] = [(6, 0, user_ids)]
        if description:
            values["description"] = description
        if date_deadline:
            values["date_deadline"] = date_deadline
        if priority:
            values["priority"] = priority
        values.update(extra)

        task_id = self.client.create(self.TASK_MODEL, values)
        logger.info("Created task %r in project %d → id=%d", name, project_id, task_id)
        return self._read_task(task_id)

    def update_task(self, task_id: int, **values: Any) -> dict:
        """Update a task's fields.

        Args:
            task_id: The task ID.
            **values: Field values to update.

        Returns:
            The updated task record.
        """
        self.client.write(self.TASK_MODEL, task_id, values)
        logger.info("Updated task id=%d: %s", task_id, list(values.keys()))
        return self._read_task(task_id)

    def assign_task(self, task_id: int, user_ids: list[int]) -> dict:
        """Assign users to a task.

        Args:
            task_id: The task ID.
            user_ids: List of user IDs to assign.

        Returns:
            The updated task record.
        """
        self.client.write(self.TASK_MODEL, task_id, {
            "user_ids": [(6, 0, user_ids)],
        })
        logger.info("Assigned users %s to task id=%d", user_ids, task_id)
        return self._read_task(task_id)

    def set_task_stage(self, task_id: int, stage_id: int) -> dict:
        """Move a task to a different stage.

        Args:
            task_id: The task ID.
            stage_id: Target ``project.task.type`` ID.

        Returns:
            The updated task record.
        """
        self.client.write(self.TASK_MODEL, task_id, {"stage_id": stage_id})
        logger.info("Moved task id=%d to stage_id=%d", task_id, stage_id)
        return self._read_task(task_id)

    def search_tasks(
        self,
        project_id: Optional[int] = None,
        query: Optional[str] = None,
        user_id: Optional[int] = None,
        stage_id: Optional[int] = None,
        limit: int = 50,
    ) -> list[dict]:
        """Search tasks with optional filters.

        Args:
            project_id: Filter by project.
            query: Text to search in task name.
            user_id: Filter by assigned user.
            stage_id: Filter by stage.
            limit: Max results.

        Returns:
            List of matching task records.
        """
        domain: list = [["active", "=", True]]
        if project_id:
            domain.append(["project_id", "=", project_id])
        if query:
            domain.append(["name", "ilike", query])
        if user_id:
            domain.append(["user_ids", "in", [user_id]])
        if stage_id:
            domain.append(["stage_id", "=", stage_id])

        return self.client.search_read(
            self.TASK_MODEL, domain,
            fields=_TASK_LIST_FIELDS, limit=limit,
            order="priority desc, date_deadline asc",
        )

    def get_project_stages(self, project_id: Optional[int] = None) -> list[dict]:
        """Get all task stages, optionally filtered by project.

        Args:
            project_id: If given, return stages associated with this project.

        Returns:
            List of stage records, ordered by sequence.
        """
        domain: list = []
        if project_id:
            domain.append(["project_ids", "in", [project_id]])

        return self.client.search_read(
            self.STAGE_MODEL, domain,
            fields=["id", "name", "sequence", "fold"],
            order="sequence asc",
        )

    # ── Timesheets ───────────────────────────────────────────────────

    def log_timesheet(
        self,
        project_id: int,
        task_id: int,
        hours: float,
        description: str = "",
        date: Optional[str] = None,
        employee_id: Optional[int] = None,
        **extra: Any,
    ) -> dict:
        """Log a timesheet entry for a task.

        Args:
            project_id: The project ID.
            task_id: The task ID.
            hours: Number of hours worked.
            description: Work description.
            date: Date of the work (``YYYY-MM-DD``). Defaults to today.
            employee_id: Employee who performed the work.
            **extra: Additional ``account.analytic.line`` field values.

        Returns:
            The newly created timesheet entry.
        """
        values: dict[str, Any] = {
            "project_id": project_id,
            "task_id": task_id,
            "unit_amount": hours,
            "name": description or "/",
        }
        if date:
            values["date"] = date
        if employee_id:
            values["employee_id"] = employee_id
        values.update(extra)

        ts_id = self.client.create(self.TIMESHEET_MODEL, values)
        logger.info("Logged %.1fh timesheet on task %d → id=%d", hours, task_id, ts_id)
        records = self.client.read(self.TIMESHEET_MODEL, ts_id, fields=_TIMESHEET_FIELDS)
        return records[0] if records else {}

    # ── Internal helpers ─────────────────────────────────────────────

    def _read_project(self, project_id: int) -> dict:
        """Read a single project by ID."""
        records = self.client.read(
            self.PROJECT_MODEL, project_id, fields=_PROJECT_DETAIL_FIELDS,
        )
        return records[0] if records else {}

    def _read_task(self, task_id: int) -> dict:
        """Read a single task by ID."""
        records = self.client.read(
            self.TASK_MODEL, task_id, fields=_TASK_DETAIL_FIELDS,
        )
        return records[0] if records else {}
