"""Tax calculation engine.

Computes tax amounts given a tax template and line items. Used during
invoice/quotation creation (draft stage, no financial writes).

Two main functions:
  - resolve_tax_template(): Determine which tax template applies to a
    transaction by checking party exemptions, tax_rule matches, and
    company defaults.
  - calculate_tax(): Given a tax template ID and a subtotal (or item list),
    compute the cascading tax amounts per template line.

All monetary math uses Python Decimal — NEVER float.
"""

from decimal import Decimal, ROUND_HALF_UP

from erpclaw_lib.decimal_utils import to_decimal, round_currency


# ---------------------------------------------------------------------------
# resolve_tax_template
# ---------------------------------------------------------------------------

def resolve_tax_template(conn, party_type, party_id, company_id,
                         transaction_type=None, shipping_state=None,
                         tax_category_id=None):
    """Determine the applicable tax template for a transaction.

    Resolution order:
      1. Check party exemption flag (customer.exempt_from_sales_tax).
      2. Match tax_rule rows (highest-priority first) against party,
         shipping state, and tax category.
      3. Fall back to the company's default tax template.

    Args:
        conn: SQLite connection (row_factory = sqlite3.Row expected).
        party_type: "customer" or "supplier".
        party_id: UUID of the customer/supplier.
        company_id: UUID of the company.
        transaction_type: "sales" or "purchase". Defaults based on party_type.
        shipping_state: Optional US state code for nexus matching.
        tax_category_id: Optional tax category UUID for rule filtering.

    Returns:
        dict with keys:
            tax_template_id (str|None),
            template_name (str|None),
            is_exempt (bool),
            item_overrides (list of dicts with item_id, tax_template_id).
    """
    if party_type not in ("customer", "supplier"):
        raise ValueError("party_type must be 'customer' or 'supplier'")

    tx_type = transaction_type or ("sales" if party_type == "customer" else "purchase")

    # ------------------------------------------------------------------
    # 1. Check party exemption
    # ------------------------------------------------------------------
    is_exempt = False
    if party_type == "customer":
        party = conn.execute(
            "SELECT id, exempt_from_sales_tax FROM customer WHERE id = ?",
            (party_id,),
        ).fetchone()
        if party and party["exempt_from_sales_tax"]:
            is_exempt = True
    else:
        # Suppliers don't have an exempt flag, but verify they exist
        conn.execute(
            "SELECT id FROM supplier WHERE id = ?",
            (party_id,),
        ).fetchone()

    # ------------------------------------------------------------------
    # 2. Match tax rules (priority ASC = highest priority first)
    # ------------------------------------------------------------------
    rules = conn.execute(
        """SELECT r.*, t.name AS template_name
           FROM tax_rule r
           JOIN tax_template t ON t.id = r.tax_template_id
           WHERE r.company_id = ?
             AND (r.tax_type = ? OR t.tax_type = 'both')
           ORDER BY r.priority ASC""",
        (company_id, tx_type),
    ).fetchall()

    best_template_id = None
    best_template_name = None

    for rule in rules:
        match = True

        # Customer-specific rule
        if rule["customer_id"] and rule["customer_id"] != party_id:
            match = False
        # Customer group rule
        if rule["customer_group"] and party_type == "customer":
            cust = conn.execute(
                "SELECT customer_group FROM customer WHERE id = ?",
                (party_id,),
            ).fetchone()
            if not cust or cust["customer_group"] != rule["customer_group"]:
                match = False
        # Supplier-specific rule
        if rule["supplier_id"] and rule["supplier_id"] != party_id:
            match = False
        # Supplier group rule
        if rule["supplier_group"] and party_type == "supplier":
            sup = conn.execute(
                "SELECT supplier_group FROM supplier WHERE id = ?",
                (party_id,),
            ).fetchone()
            if not sup or sup["supplier_group"] != rule["supplier_group"]:
                match = False
        # Shipping state rule
        if rule["shipping_state"] and rule["shipping_state"] != shipping_state:
            match = False
        # Tax category rule
        if rule["tax_category_id"] and tax_category_id != rule["tax_category_id"]:
            match = False

        if match:
            best_template_id = rule["tax_template_id"]
            best_template_name = rule["template_name"]
            break

    # ------------------------------------------------------------------
    # 3. Fallback to company default
    # ------------------------------------------------------------------
    if not best_template_id:
        default = conn.execute(
            """SELECT id, name FROM tax_template
               WHERE company_id = ? AND is_default = 1
               AND (tax_type = ? OR tax_type = 'both')
               LIMIT 1""",
            (company_id, tx_type),
        ).fetchone()
        if default:
            best_template_id = default["id"]
            best_template_name = default["name"]

    # ------------------------------------------------------------------
    # 4. Gather item-level template overrides
    # ------------------------------------------------------------------
    item_overrides = []
    if best_template_id:
        overrides = conn.execute(
            "SELECT item_id, tax_template_id FROM item_tax_template"
        ).fetchall()
        item_overrides = [
            {"item_id": o["item_id"], "tax_template_id": o["tax_template_id"]}
            for o in overrides
            if o["tax_template_id"] != best_template_id
        ]

    return {
        "tax_template_id": best_template_id,
        "template_name": best_template_name,
        "is_exempt": is_exempt,
        "item_overrides": item_overrides,
    }


# ---------------------------------------------------------------------------
# calculate_tax  (subtotal-based — compatible with selling/buying callers)
# ---------------------------------------------------------------------------

def calculate_tax(conn, tax_template_id, subtotal):
    """Calculate cascading tax from a tax template applied to a subtotal.

    This is the main entry point used by selling and buying skills.
    It queries tax_template_line rows for the given template and applies
    each line's charge_type logic in row_order, supporting cascading
    (on_previous_row_total, on_previous_row_amount).

    Args:
        conn: SQLite connection (row_factory = sqlite3.Row expected).
        tax_template_id: UUID of the tax_template. If falsy, returns zero.
        subtotal: Decimal (or str/int) net total before tax.

    Returns:
        Tuple of (total_tax: Decimal, tax_details: list[dict]).
        Each detail dict has keys:
            tax_account_id, account_name, description, rate, tax_amount,
            charge_type, add_deduct.
        Amounts are Decimal; rate/tax_amount also provided as str for
        JSON serialisation convenience.
    """
    if not tax_template_id:
        return Decimal("0"), []

    subtotal = to_decimal(subtotal)

    lines = conn.execute(
        """SELECT ttl.*, a.name AS account_name
           FROM tax_template_line ttl
           LEFT JOIN account a ON a.id = ttl.tax_account_id
           WHERE ttl.tax_template_id = ?
           ORDER BY ttl.row_order""",
        (tax_template_id,),
    ).fetchall()

    if not lines:
        return Decimal("0"), []

    total_tax = Decimal("0")
    tax_details = []
    cumulative_amount = subtotal          # net_total + taxes so far
    prev_row_amount = Decimal("0")        # tax from the immediately prior line

    for line in lines:
        rate = to_decimal(line["rate"])
        charge_type = line["charge_type"]
        add_deduct = line["add_deduct"]

        # ----- Compute tax_amount based on charge_type -----
        if charge_type == "on_net_total":
            tax_amount = round_currency(subtotal * rate / Decimal("100"))

        elif charge_type == "on_previous_row_total":
            tax_amount = round_currency(cumulative_amount * rate / Decimal("100"))

        elif charge_type == "on_previous_row_amount":
            tax_amount = round_currency(prev_row_amount * rate / Decimal("100"))

        elif charge_type == "actual":
            # For 'actual', the rate field holds the fixed amount itself
            tax_amount = round_currency(rate)

        elif charge_type == "on_item_quantity":
            # Per-unit amount; without individual item qty info, treat
            # rate as the total fixed amount (matches selling behaviour)
            tax_amount = round_currency(rate)

        else:
            # Unknown charge_type — safe fallback to on_net_total
            tax_amount = round_currency(subtotal * rate / Decimal("100"))

        # ----- Apply add/deduct sign -----
        if add_deduct == "deduct":
            tax_amount = -tax_amount

        total_tax += tax_amount
        prev_row_amount = abs(tax_amount)
        cumulative_amount += tax_amount

        tax_details.append({
            "tax_account_id": line["tax_account_id"],
            "account_name": line["account_name"] if line["account_name"] else "",
            "description": line["description"] if line["description"] else "",
            "rate": str(rate),
            "amount": tax_amount,              # Decimal for callers
            "tax_amount": str(tax_amount),      # str for JSON convenience
            "charge_type": charge_type,
            "add_deduct": add_deduct,
        })

    return round_currency(total_tax), tax_details


# ---------------------------------------------------------------------------
# calculate_tax_detailed  (item-level — for erpclaw-tax action handler)
# ---------------------------------------------------------------------------

def calculate_tax_detailed(conn, tax_template_id, items,
                           item_overrides=None):
    """Calculate tax with per-item breakdown and override support.

    This is the richer version used by erpclaw-tax's ``calculate-tax``
    action. It computes the same cascading logic as ``calculate_tax``
    but also distributes each tax line proportionally across items and
    honours item-level template overrides.

    Args:
        conn: SQLite connection.
        tax_template_id: UUID of the tax_template.
        items: list of dicts, each with at least ``item_id``,
               ``net_amount``; optionally ``qty``.
        item_overrides: Optional list of dicts with ``item_id`` and
                        ``override_template_id``.

    Returns:
        dict with keys:
            tax_lines, total_tax, net_total, grand_total, per_item_tax.
    """
    if not tax_template_id:
        raise ValueError("tax_template_id is required")
    if not items or not isinstance(items, list):
        raise ValueError("items must be a non-empty list")

    lines = _fetch_template_lines(conn, tax_template_id)
    if not lines:
        raise ValueError(
            f"No template lines found for template: {tax_template_id}"
        )

    # Build override map
    override_map = {}
    if item_overrides:
        for o in item_overrides:
            override_map[o["item_id"]] = o.get("override_template_id")

    # Calculate net total and initialise per-item accumulators
    net_total = Decimal("0")
    per_item = []
    for item in items:
        net_amt = to_decimal(str(item.get("net_amount", "0")))
        net_total += net_amt
        per_item.append({
            "item_id": item.get("item_id"),
            "net_amount": net_amt,
            "tax_amount": Decimal("0"),
        })

    # Cascade through template lines
    tax_lines = []
    total_tax = Decimal("0")
    prev_row_amount = Decimal("0")
    prev_row_total = Decimal("0")

    for tl in lines:
        rate = to_decimal(tl["rate"])
        charge_type = tl["charge_type"]
        add_deduct = tl["add_deduct"]

        # Determine base amount
        if charge_type == "on_net_total":
            base = net_total
        elif charge_type == "on_previous_row_total":
            base = prev_row_total if prev_row_total else net_total
        elif charge_type == "on_previous_row_amount":
            base = prev_row_amount
        elif charge_type == "actual":
            base = rate      # rate IS the amount for 'actual'
            rate = Decimal("0")
        elif charge_type == "on_item_quantity":
            total_qty = sum(
                to_decimal(str(item.get("qty", "1"))) for item in items
            )
            base = total_qty
        else:
            base = net_total

        # Calculate tax amount
        if charge_type == "actual":
            tax_amount = round_currency(base)
        else:
            tax_amount = round_currency(base * rate / Decimal("100"))

        if add_deduct == "deduct":
            tax_amount = -tax_amount

        # Distribute proportionally to items (skip overridden)
        for pi in per_item:
            if pi["item_id"] in override_map:
                continue
            if net_total > 0:
                item_share = round_currency(
                    tax_amount * pi["net_amount"] / net_total
                )
            else:
                item_share = Decimal("0")
            pi["tax_amount"] += item_share

        tax_lines.append({
            "tax_account_id": tl["tax_account_id"],
            "account_name": tl.get("account_name", ""),
            "description": tl.get("description", ""),
            "rate": str(tl["rate"]),
            "amount": str(round_currency(tax_amount)),
        })

        prev_row_amount = abs(tax_amount)
        total_tax += tax_amount
        prev_row_total = net_total + total_tax

    return {
        "tax_lines": tax_lines,
        "total_tax": str(round_currency(total_tax)),
        "net_total": str(round_currency(net_total)),
        "grand_total": str(round_currency(net_total + total_tax)),
        "per_item_tax": [
            {
                "item_id": pi["item_id"],
                "tax_amount": str(round_currency(pi["tax_amount"])),
            }
            for pi in per_item
        ],
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _fetch_template_lines(conn, template_id):
    """Fetch tax_template_line rows with account names, ordered by row_order.

    Returns a list of dicts (not sqlite3.Row) so callers can use .get().
    """
    rows = conn.execute(
        """SELECT tl.*, a.name AS account_name
           FROM tax_template_line tl
           LEFT JOIN account a ON a.id = tl.tax_account_id
           WHERE tl.tax_template_id = ?
           ORDER BY tl.row_order""",
        (template_id,),
    ).fetchall()
    return [dict(r) for r in rows]
