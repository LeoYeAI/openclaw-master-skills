"""Cross-skill integration API for ERPClaw verticals.

Provides high-level functions that vertical skills (PropertyClaw, BuildClaw,
LegalClaw, etc.) call to interact with core ERPClaw skills — without
directly importing or writing to tables they don't own.

Each function:
1. Validates inputs
2. Resolves the target skill's db_query.py via dependencies.resolve_skill_script()
3. Calls it via subprocess with the correct --action and args
4. Parses the JSON response
5. Returns a structured result or raises CrossSkillError

Usage:
    from erpclaw_lib.cross_skill import create_invoice, create_payment, call_skill_action

    # High-level: create a sales invoice from a vertical
    result = create_invoice(
        company_id="...",
        customer_id="...",
        items=[{"description": "Monthly rent", "qty": "1", "rate": "2500.00"}],
    )
    invoice_id = result["sales_invoice"]["id"]

    # Low-level: call any action on any skill
    result = call_skill_action("erpclaw", "list-customers",
                               {"--company-id": company_id})
"""
import json
import subprocess
from typing import Optional

from erpclaw_lib.dependencies import resolve_skill_script, check_subprocess_target


class CrossSkillError(Exception):
    """Raised when a cross-skill call fails."""

    def __init__(self, message, skill=None, action=None, raw_output=None):
        super().__init__(message)
        self.skill = skill
        self.action = action
        self.raw_output = raw_output


def call_skill_action(
    skill_name: str,
    action: str,
    args: Optional[dict] = None,
    db_path: Optional[str] = None,
    timeout: int = 30,
) -> dict:
    """Call an action on any installed skill via subprocess.

    This is the low-level building block. Higher-level functions like
    create_invoice() and create_payment() use this internally.

    Args:
        skill_name: e.g. 'erpclaw'
        action: e.g. 'add-sales-invoice'
        args: Dict of CLI arguments. Keys should include '--' prefix.
              e.g. {"--customer-id": "abc", "--items": '[...]'}
        db_path: Optional non-default DB path to pass through.
        timeout: Subprocess timeout in seconds (default 30).

    Returns:
        Parsed JSON dict from the skill's stdout.

    Raises:
        CrossSkillError: If skill not found, subprocess fails, or response invalid.
    """
    script_path = resolve_skill_script(skill_name)
    if not script_path:
        raise CrossSkillError(
            f"{skill_name} is not installed. Install it first.",
            skill=skill_name,
            action=action,
        )

    cmd = ["python3", script_path, "--action", action]

    if args:
        for key, value in args.items():
            cmd.append(key)
            if value is not None:
                cmd.append(str(value))

    if db_path:
        cmd.extend(["--db-path", db_path])

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise CrossSkillError(
            f"{skill_name} {action} timed out after {timeout}s",
            skill=skill_name,
            action=action,
        )

    if result.returncode != 0:
        raw = result.stdout.strip() or result.stderr.strip()
        # Try to extract structured error
        try:
            err_data = json.loads(raw)
            msg = err_data.get("message", err_data.get("error", raw[:500]))
            # Surface module install suggestion if available
            suggested = err_data.get("suggested_module")
            if suggested:
                msg = (f"Action '{action}' requires module '{suggested}' which is not installed. "
                       f"Install it with: install-module --module-name {suggested}")
        except (json.JSONDecodeError, TypeError):
            msg = raw[:500] if raw else "Unknown error (no output)"
        raise CrossSkillError(
            f"{skill_name} {action} failed: {msg}",
            skill=skill_name,
            action=action,
            raw_output=raw,
        )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise CrossSkillError(
            f"Invalid JSON from {skill_name} {action}: {result.stdout[:200]}",
            skill=skill_name,
            action=action,
            raw_output=result.stdout,
        )

    if data.get("status") == "error":
        raise CrossSkillError(
            data.get("message", "Unknown error"),
            skill=skill_name,
            action=action,
            raw_output=result.stdout,
        )

    return data


# ---------------------------------------------------------------------------
# High-level: Invoice creation
# ---------------------------------------------------------------------------

def create_invoice(
    customer_id: str,
    items: list[dict],
    company_id: Optional[str] = None,
    posting_date: Optional[str] = None,
    due_date: Optional[str] = None,
    project_id: Optional[str] = None,
    remarks: Optional[str] = None,
    db_path: Optional[str] = None,
    timeout: int = 30,
) -> dict:
    """Create a Sales Invoice via erpclaw.

    This is the standard way for verticals to generate invoices.
    Creates a draft invoice that can be submitted separately.

    Args:
        customer_id: The customer to invoice.
        items: List of item dicts, each with at minimum:
               {"description": str, "qty": str, "rate": str}
               Optional: {"item_id": str, "uom": str, "warehouse_id": str}
        company_id: Company ID (passed if needed).
        posting_date: Invoice date (YYYY-MM-DD). Defaults to today in skill.
        due_date: Payment due date (YYYY-MM-DD).
        project_id: Link invoice to a project.
        remarks: Free-text remarks on the invoice.
        db_path: Non-default DB path.
        timeout: Subprocess timeout.

    Returns:
        Full response dict from erpclaw, typically:
        {"status": "ok", "sales_invoice": {"id": "...", "name": "INV-..."}}

    Raises:
        CrossSkillError: If selling skill not installed or invoice creation fails.
    """
    args = {
        "--customer-id": customer_id,
        "--items": json.dumps(items),
    }
    if company_id:
        args["--company-id"] = company_id
    if posting_date:
        args["--posting-date"] = posting_date
    if due_date:
        args["--due-date"] = due_date
    if project_id:
        args["--project-id"] = project_id
    if remarks:
        args["--remarks"] = remarks

    return call_skill_action(
        "erpclaw", "add-sales-invoice",
        args=args, db_path=db_path, timeout=timeout,
    )


def submit_invoice(
    invoice_id: str,
    db_path: Optional[str] = None,
    timeout: int = 30,
) -> dict:
    """Submit (finalize) a Sales Invoice via erpclaw.

    This validates the invoice, posts GL entries, and transitions
    the invoice from Draft to Submitted.

    Args:
        invoice_id: The sales_invoice.id to submit.
        db_path: Non-default DB path.
        timeout: Subprocess timeout.

    Returns:
        Response dict from erpclaw.

    Raises:
        CrossSkillError: On failure.
    """
    return call_skill_action(
        "erpclaw", "submit-sales-invoice",
        args={"--invoice-id": invoice_id},
        db_path=db_path, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# High-level: Purchase Invoice creation
# ---------------------------------------------------------------------------

def create_purchase_invoice(
    supplier_id: str,
    items: list[dict],
    company_id: Optional[str] = None,
    posting_date: Optional[str] = None,
    due_date: Optional[str] = None,
    project_id: Optional[str] = None,
    remarks: Optional[str] = None,
    db_path: Optional[str] = None,
    timeout: int = 30,
) -> dict:
    """Create a Purchase Invoice via erpclaw.

    Args:
        supplier_id: The supplier to invoice.
        items: List of item dicts with description, qty, rate.
        company_id: Company ID.
        posting_date: Invoice date.
        due_date: Payment due date.
        project_id: Link to project.
        remarks: Free-text remarks.
        db_path: Non-default DB path.
        timeout: Subprocess timeout.

    Returns:
        Response dict from erpclaw.

    Raises:
        CrossSkillError: On failure.
    """
    args = {
        "--supplier-id": supplier_id,
        "--items": json.dumps(items),
    }
    if company_id:
        args["--company-id"] = company_id
    if posting_date:
        args["--posting-date"] = posting_date
    if due_date:
        args["--due-date"] = due_date
    if project_id:
        args["--project-id"] = project_id
    if remarks:
        args["--remarks"] = remarks

    return call_skill_action(
        "erpclaw", "add-purchase-invoice",
        args=args, db_path=db_path, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# High-level: Payment creation
# ---------------------------------------------------------------------------

def create_payment(
    payment_type: str,
    party_type: str,
    party_id: str,
    paid_amount: str,
    company_id: Optional[str] = None,
    posting_date: Optional[str] = None,
    paid_from: Optional[str] = None,
    paid_to: Optional[str] = None,
    reference_type: Optional[str] = None,
    reference_id: Optional[str] = None,
    payment_method: Optional[str] = None,
    remarks: Optional[str] = None,
    db_path: Optional[str] = None,
    timeout: int = 30,
) -> dict:
    """Create a Payment Entry via erpclaw-payments.

    Args:
        payment_type: 'receive' (from customer) or 'pay' (to supplier/employee).
        party_type: 'customer', 'supplier', or 'employee'.
        party_id: The party's ID.
        paid_amount: Amount as string (Decimal-safe).
        company_id: Company ID.
        posting_date: Payment date.
        paid_from: Source account ID (bank/cash).
        paid_to: Target account ID.
        reference_type: e.g. 'sales_invoice', 'purchase_invoice'.
        reference_id: The referenced document ID.
        payment_method: e.g. 'bank_transfer', 'cash', 'check'.
        remarks: Free-text remarks.
        db_path: Non-default DB path.
        timeout: Subprocess timeout.

    Returns:
        Response dict from erpclaw-payments.

    Raises:
        CrossSkillError: On failure.
    """
    args = {
        "--payment-type": payment_type,
        "--party-type": party_type,
        "--party-id": party_id,
        "--paid-amount": paid_amount,
    }
    if company_id:
        args["--company-id"] = company_id
    if posting_date:
        args["--posting-date"] = posting_date
    if paid_from:
        args["--paid-from"] = paid_from
    if paid_to:
        args["--paid-to"] = paid_to
    if reference_type:
        args["--reference-type"] = reference_type
    if reference_id:
        args["--reference-id"] = reference_id
    if payment_method:
        args["--payment-method"] = payment_method
    if remarks:
        args["--remarks"] = remarks

    return call_skill_action(
        "erpclaw-payments", "add-payment-entry",
        args=args, db_path=db_path, timeout=timeout,
    )


def submit_payment(
    payment_id: str,
    db_path: Optional[str] = None,
    timeout: int = 30,
) -> dict:
    """Submit a Payment Entry via erpclaw-payments.

    Args:
        payment_id: The payment_entry.id to submit.
        db_path: Non-default DB path.
        timeout: Subprocess timeout.

    Returns:
        Response dict from erpclaw-payments.

    Raises:
        CrossSkillError: On failure.
    """
    return call_skill_action(
        "erpclaw-payments", "submit-payment-entry",
        args={"--payment-id": payment_id},
        db_path=db_path, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# High-level: Customer / Supplier creation
# ---------------------------------------------------------------------------

def create_customer(
    customer_name: str,
    company_id: Optional[str] = None,
    customer_type: str = "company",
    email: Optional[str] = None,
    phone: Optional[str] = None,
    db_path: Optional[str] = None,
    timeout: int = 30,
) -> dict:
    """Create a Customer via erpclaw.

    This is the correct way for verticals to create customers.
    DO NOT INSERT directly into the customer table.

    Args:
        customer_name: Customer name.
        company_id: Company ID.
        customer_type: 'company' or 'individual'.
        email: Customer email.
        phone: Customer phone.
        db_path: Non-default DB path.
        timeout: Subprocess timeout.

    Returns:
        Response dict with customer ID.

    Raises:
        CrossSkillError: On failure.
    """
    args = {"--name": customer_name}
    if company_id:
        args["--company-id"] = company_id
    if customer_type:
        args["--customer-type"] = customer_type
    if email:
        args["--email"] = email
    if phone:
        args["--phone"] = phone

    return call_skill_action(
        "erpclaw", "add-customer",
        args=args, db_path=db_path, timeout=timeout,
    )


def create_supplier(
    supplier_name: str,
    company_id: Optional[str] = None,
    supplier_type: str = "company",
    email: Optional[str] = None,
    phone: Optional[str] = None,
    db_path: Optional[str] = None,
    timeout: int = 30,
) -> dict:
    """Create a Supplier via erpclaw.

    Args:
        supplier_name: Supplier name.
        company_id: Company ID.
        supplier_type: 'company' or 'individual'.
        email: Supplier email.
        phone: Supplier phone.
        db_path: Non-default DB path.
        timeout: Subprocess timeout.

    Returns:
        Response dict with supplier ID.

    Raises:
        CrossSkillError: On failure.
    """
    args = {"--name": supplier_name}
    if company_id:
        args["--company-id"] = company_id
    if supplier_type:
        args["--supplier-type"] = supplier_type
    if email:
        args["--email"] = email
    if phone:
        args["--phone"] = phone

    return call_skill_action(
        "erpclaw", "add-supplier",
        args=args, db_path=db_path, timeout=timeout,
    )
