"""
Human Resources operations for Odoo.

Covers ``hr.employee``, ``hr.department``, ``hr.leave``, and ``hr.expense``.
Provides employee management, leave requests, and expense tracking.
"""

import logging
from typing import Any, Optional

from ..client import OdooClient

logger = logging.getLogger("odoo_skill")

_EMPLOYEE_LIST_FIELDS = [
    "id", "name", "job_title", "department_id",
    "work_email", "work_phone", "parent_id",
    "company_id", "active",
]

_EMPLOYEE_DETAIL_FIELDS = _EMPLOYEE_LIST_FIELDS + [
    "job_id", "coach_id", "address_id",
    "work_location_id", "resource_calendar_id",
    "employee_type", "marital", "birthday",
]

_DEPARTMENT_FIELDS = [
    "id", "name", "parent_id", "manager_id",
    "company_id", "member_ids",
]

_LEAVE_LIST_FIELDS = [
    "id", "employee_id", "holiday_status_id", "state",
    "date_from", "date_to", "number_of_days", "name",
]

_EXPENSE_LIST_FIELDS = [
    "id", "name", "employee_id", "product_id",
    "total_amount", "currency_id", "state",
    "date", "company_id",
]

_EXPENSE_DETAIL_FIELDS = _EXPENSE_LIST_FIELDS + [
    "description", "quantity", "price_unit",
    "payment_mode", "account_id",
]


class HROps:
    """High-level HR operations for Odoo.

    Manages employees, departments, leave requests, and expenses.

    Args:
        client: An authenticated :class:`OdooClient` instance.
    """

    EMPLOYEE_MODEL = "hr.employee"
    DEPARTMENT_MODEL = "hr.department"
    LEAVE_MODEL = "hr.leave"
    LEAVE_TYPE_MODEL = "hr.leave.type"
    EXPENSE_MODEL = "hr.expense"

    def __init__(self, client: OdooClient) -> None:
        self.client = client

    # ── Employee CRUD ────────────────────────────────────────────────

    def create_employee(
        self,
        name: str,
        job_title: Optional[str] = None,
        department_id: Optional[int] = None,
        work_email: Optional[str] = None,
        work_phone: Optional[str] = None,
        parent_id: Optional[int] = None,
        **extra: Any,
    ) -> dict:
        """Create a new employee record.

        Args:
            name: Employee's full name.
            job_title: Job title/position.
            department_id: Department ID to assign to.
            work_email: Work email address.
            work_phone: Work phone number.
            parent_id: Manager's employee ID.
            **extra: Additional ``hr.employee`` field values.

        Returns:
            The newly created employee record.
        """
        values: dict[str, Any] = {"name": name}
        if job_title:
            values["job_title"] = job_title
        if department_id:
            values["department_id"] = department_id
        if work_email:
            values["work_email"] = work_email
        if work_phone:
            values["work_phone"] = work_phone
        if parent_id:
            values["parent_id"] = parent_id
        values.update(extra)

        emp_id = self.client.create(self.EMPLOYEE_MODEL, values)
        logger.info("Created employee %r → id=%d", name, emp_id)
        return self._read_employee(emp_id)

    def get_employee(self, employee_id: int) -> dict:
        """Get full details of an employee.

        Args:
            employee_id: The employee ID.

        Returns:
            Employee record dict, or empty dict if not found.
        """
        return self._read_employee(employee_id)

    def search_employees(
        self,
        query: Optional[str] = None,
        department_id: Optional[int] = None,
        limit: int = 50,
    ) -> list[dict]:
        """Search employees by name or department.

        Args:
            query: Text to search in employee name.
            department_id: Filter by department.
            limit: Max results.

        Returns:
            List of matching employee records.
        """
        domain: list = [["active", "=", True]]
        if query:
            domain.append(["name", "ilike", query])
        if department_id:
            domain.append(["department_id", "=", department_id])

        return self.client.search_read(
            self.EMPLOYEE_MODEL, domain,
            fields=_EMPLOYEE_LIST_FIELDS, limit=limit,
            order="name asc",
        )

    def update_employee(self, employee_id: int, **values: Any) -> dict:
        """Update an employee's fields.

        Args:
            employee_id: The employee ID.
            **values: Field values to update.

        Returns:
            The updated employee record.
        """
        self.client.write(self.EMPLOYEE_MODEL, employee_id, values)
        logger.info("Updated employee id=%d: %s", employee_id, list(values.keys()))
        return self._read_employee(employee_id)

    # ── Departments ──────────────────────────────────────────────────

    def get_departments(self, limit: int = 100) -> list[dict]:
        """Get all departments.

        Args:
            limit: Max results.

        Returns:
            List of department records.
        """
        return self.client.search_read(
            self.DEPARTMENT_MODEL, [],
            fields=_DEPARTMENT_FIELDS, limit=limit,
            order="name asc",
        )

    def create_department(
        self,
        name: str,
        parent_id: Optional[int] = None,
        manager_id: Optional[int] = None,
        **extra: Any,
    ) -> dict:
        """Create a new department.

        Args:
            name: Department name.
            parent_id: Parent department ID for hierarchical org.
            manager_id: Department manager's employee ID.
            **extra: Additional ``hr.department`` field values.

        Returns:
            The newly created department record.
        """
        values: dict[str, Any] = {"name": name}
        if parent_id:
            values["parent_id"] = parent_id
        if manager_id:
            values["manager_id"] = manager_id
        values.update(extra)

        dept_id = self.client.create(self.DEPARTMENT_MODEL, values)
        logger.info("Created department %r → id=%d", name, dept_id)
        records = self.client.read(self.DEPARTMENT_MODEL, dept_id, fields=_DEPARTMENT_FIELDS)
        return records[0] if records else {}

    # ── Leave Requests (Time Off) ────────────────────────────────────

    def create_leave_request(
        self,
        employee_id: int,
        leave_type_id: int,
        date_from: str,
        date_to: str,
        name: Optional[str] = None,
        **extra: Any,
    ) -> dict:
        """Create a leave (time off) request for an employee.

        Args:
            employee_id: The employee requesting leave.
            leave_type_id: The leave type ID (e.g. sick, vacation).
            date_from: Start datetime as ``YYYY-MM-DD HH:MM:SS``.
            date_to: End datetime as ``YYYY-MM-DD HH:MM:SS``.
            name: Optional description/reason for the leave.
            **extra: Additional ``hr.leave`` field values.

        Returns:
            The newly created leave request record.
        """
        values: dict[str, Any] = {
            "employee_id": employee_id,
            "holiday_status_id": leave_type_id,
            "date_from": date_from,
            "date_to": date_to,
        }
        if name:
            values["name"] = name
        values.update(extra)

        leave_id = self.client.create(self.LEAVE_MODEL, values)
        logger.info("Created leave request for employee=%d → id=%d", employee_id, leave_id)
        records = self.client.read(self.LEAVE_MODEL, leave_id, fields=_LEAVE_LIST_FIELDS)
        return records[0] if records else {}

    def get_leaves(
        self,
        employee_id: Optional[int] = None,
        state: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict]:
        """Get leave requests with optional filters.

        Args:
            employee_id: Filter by employee.
            state: Filter by state (``draft``, ``confirm``, ``validate``,
                ``refuse``).
            limit: Max results.

        Returns:
            List of leave request records.
        """
        domain: list = []
        if employee_id:
            domain.append(["employee_id", "=", employee_id])
        if state:
            domain.append(["state", "=", state])

        return self.client.search_read(
            self.LEAVE_MODEL, domain,
            fields=_LEAVE_LIST_FIELDS, limit=limit,
            order="date_from desc",
        )

    def approve_leave(self, leave_id: int) -> dict:
        """Approve a pending leave request.

        Args:
            leave_id: The leave request ID.

        Returns:
            The updated leave record.
        """
        self.client.execute(self.LEAVE_MODEL, "action_approve", [leave_id])
        logger.info("Approved leave request id=%d", leave_id)
        records = self.client.read(self.LEAVE_MODEL, leave_id, fields=_LEAVE_LIST_FIELDS)
        return records[0] if records else {}

    def get_leave_types(self) -> list[dict]:
        """Get all available leave types.

        Returns:
            List of leave type records.
        """
        return self.client.search_read(
            self.LEAVE_TYPE_MODEL, [],
            fields=["id", "name", "requires_allocation"],
            order="name asc",
        )

    # ── Expenses ─────────────────────────────────────────────────────

    def create_expense(
        self,
        name: str,
        employee_id: int,
        total_amount: float,
        product_id: Optional[int] = None,
        date: Optional[str] = None,
        description: Optional[str] = None,
        **extra: Any,
    ) -> dict:
        """Create an expense record for an employee.

        Args:
            name: Expense description/title.
            employee_id: The employee submitting the expense.
            total_amount: Total expense amount.
            product_id: Expense category (product) ID.
            date: Expense date as ``YYYY-MM-DD``.
            description: Additional notes.
            **extra: Additional ``hr.expense`` field values.

        Returns:
            The newly created expense record.
        """
        values: dict[str, Any] = {
            "name": name,
            "employee_id": employee_id,
            "total_amount": total_amount,
        }
        if product_id:
            values["product_id"] = product_id
        if date:
            values["date"] = date
        if description:
            values["description"] = description
        values.update(extra)

        expense_id = self.client.create(self.EXPENSE_MODEL, values)
        logger.info("Created expense %r for employee=%d → id=%d", name, employee_id, expense_id)
        records = self.client.read(self.EXPENSE_MODEL, expense_id, fields=_EXPENSE_DETAIL_FIELDS)
        return records[0] if records else {}

    def get_expenses(
        self,
        employee_id: Optional[int] = None,
        state: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict]:
        """Get expenses with optional filters.

        Args:
            employee_id: Filter by employee.
            state: Filter by state (``draft``, ``reported``, ``approved``,
                ``done``, ``refused``).
            limit: Max results.

        Returns:
            List of expense records.
        """
        domain: list = []
        if employee_id:
            domain.append(["employee_id", "=", employee_id])
        if state:
            domain.append(["state", "=", state])

        return self.client.search_read(
            self.EXPENSE_MODEL, domain,
            fields=_EXPENSE_LIST_FIELDS, limit=limit,
            order="date desc",
        )

    def submit_expense(self, expense_ids: list[int]) -> list[dict]:
        """Submit expenses for approval.

        In Odoo 19+, expenses are submitted directly (no expense sheets).
        Calls ``action_submit`` on the expense records.

        Args:
            expense_ids: List of expense IDs to submit.

        Returns:
            List of updated expense records.
        """
        if not expense_ids:
            raise ValueError("At least one expense ID is required")

        self.client.execute(self.EXPENSE_MODEL, "action_submit", expense_ids)
        logger.info("Submitted %d expense(s) for approval", len(expense_ids))
        return self.client.read(
            self.EXPENSE_MODEL, expense_ids,
            fields=_EXPENSE_DETAIL_FIELDS,
        )

    # ── Internal helpers ─────────────────────────────────────────────

    def _read_employee(self, employee_id: int) -> dict:
        """Read a single employee by ID."""
        records = self.client.read(
            self.EMPLOYEE_MODEL, employee_id, fields=_EMPLOYEE_DETAIL_FIELDS,
        )
        return records[0] if records else {}
