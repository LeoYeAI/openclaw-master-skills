#!/usr/bin/env python3
"""ERPClaw Billing Skill — db_query.py

Usage-based and metered billing: meters, readings, usage events, rate plans,
billing periods, bill runs, prepaid credits.

Usage: python3 db_query.py --action <action-name> [--flags ...]
Output: JSON to stdout, exit 0 on success, exit 1 on error.
"""
import argparse
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP

# ---------------------------------------------------------------------------
# Shared library
# ---------------------------------------------------------------------------
try:
    sys.path.insert(0, os.path.expanduser("~/.openclaw/erpclaw/lib"))
    from erpclaw_lib.db import get_connection, ensure_db_exists, DEFAULT_DB_PATH  # noqa: E402
    from erpclaw_lib.decimal_utils import to_decimal, round_currency  # noqa: E402
    from erpclaw_lib.naming import get_next_name  # noqa: E402
    from erpclaw_lib.validation import check_input_lengths  # noqa: E402
    from erpclaw_lib.response import ok, err, row_to_dict
    from erpclaw_lib.audit import audit
    from erpclaw_lib.dependencies import check_required_tables
    from erpclaw_lib.query import Q, P, Table, Field, fn, Order, DecimalSum
    from erpclaw_lib.args import SafeArgumentParser, check_unknown_args
    from erpclaw_lib.vendor.pypika.terms import ValueWrapper
except ImportError:
    import json as _json
    print(_json.dumps({"status": "error", "error": "ERPClaw foundation not installed. Install erpclaw first: clawhub install erpclaw", "suggestion": "clawhub install erpclaw"}))
    sys.exit(1)

REQUIRED_TABLES = ["company"]

# ---------------------------------------------------------------------------
# PyPika table aliases
# ---------------------------------------------------------------------------
T_meter = Table("meter")
T_meter_reading = Table("meter_reading")
T_usage_event = Table("usage_event")
T_rate_plan = Table("rate_plan")
T_rate_tier = Table("rate_tier")
T_billing_period = Table("billing_period")
T_billing_adjustment = Table("billing_adjustment")
T_prepaid = Table("prepaid_credit_balance")
T_customer = Table("customer")
T_company = Table("company")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
VALID_SERVICE_TYPES = (
    "electricity", "water", "gas", "telecom", "saas",
    "parking", "rental", "waste", "custom",
)
VALID_METER_STATUSES = ("active", "disconnected", "removed", "suspended")
VALID_READING_TYPES = ("actual", "estimated", "adjusted", "rollover")
VALID_READING_SOURCES = ("manual", "smart_meter", "api", "import", "estimated")
VALID_PLAN_TYPES = (
    "flat", "tiered", "time_of_use", "demand",
    "volume_discount", "prepaid_credit", "hybrid",
)
VALID_SUPPORTED_PLAN_TYPES = ("flat", "tiered", "volume_discount")
VALID_BASE_CHARGE_PERIODS = ("monthly", "quarterly", "annually")
VALID_BILLING_PERIOD_STATUSES = (
    "open", "rated", "invoiced", "paid", "disputed", "void",
)
VALID_ADJUSTMENT_TYPES = (
    "credit", "late_fee", "deposit", "refund",
    "proration", "discount", "penalty", "write_off",
)
VALID_PREPAID_STATUSES = ("active", "exhausted", "expired")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _parse_json_arg(value, name):
    if not value:
        err(f"--{name} is required")
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        err(f"--{name} must be valid JSON")


def _resolve_company_from_customer(conn, customer_id):
    q = Q.from_(T_customer).select(T_customer.company_id).where(T_customer.id == P())
    row = conn.execute(q.get_sql(), (customer_id,)).fetchone()
    if not row:
        err(f"Customer not found: {customer_id}",
             suggestion="Use 'list customers' in the selling skill to see available customers.")
    return row["company_id"]


# =========================================================================
# METERS (actions 1-4)
# =========================================================================

def add_meter(conn, args):
    """Register a new meter for a customer."""
    if not args.customer_id:
        err("--customer-id is required")
    if not args.meter_type:
        err("--meter-type is required")

    service_type = args.meter_type
    if service_type not in VALID_SERVICE_TYPES:
        err(f"Invalid meter-type: {service_type}. "
             f"Must be one of: {', '.join(VALID_SERVICE_TYPES)}")

    q = Q.from_(T_customer).select(T_customer.id, T_customer.company_id).where(T_customer.id == P())
    cust = conn.execute(q.get_sql(), (args.customer_id,)).fetchone()
    if not cust:
        err(f"Customer not found: {args.customer_id}")

    if args.rate_plan_id:
        q = Q.from_(T_rate_plan).select(T_rate_plan.id).where(T_rate_plan.id == P())
        rp = conn.execute(q.get_sql(), (args.rate_plan_id,)).fetchone()
        if not rp:
            err(f"Rate plan not found: {args.rate_plan_id}")

    company_id = cust["company_id"]
    conn.company_id = company_id
    meter_number = get_next_name(conn, "meter")

    meter_id = str(uuid.uuid4())
    metadata = json.dumps({"uom": args.unit}) if args.unit else None
    now = _now()

    q = (Q.into(T_meter)
         .columns("id", "meter_number", "customer_id", "service_type",
                  "service_point_id", "service_point_address", "rate_plan_id",
                  "install_date", "status", "metadata", "created_at", "updated_at")
         .insert(P(), P(), P(), P(), P(), P(), P(), P(),
                 ValueWrapper("active"), P(), P(), P()))
    conn.execute(q.get_sql(),
        (meter_id, meter_number, args.customer_id, service_type,
         args.name, args.address, args.rate_plan_id, args.install_date,
         metadata, now, now))
    conn.commit()
    audit(conn, "erpclaw-billing", "add-meter", "meter", meter_id,
           new_values={"meter_number": meter_number, "service_type": service_type})

    q = Q.from_(T_meter).select(T_meter.star).where(T_meter.id == P())
    meter = row_to_dict(conn.execute(q.get_sql(), (meter_id,)).fetchone())
    ok({"meter": meter})


def update_meter(conn, args):
    """Update meter configuration."""
    if not args.meter_id:
        err("--meter-id is required")

    q = Q.from_(T_meter).select(T_meter.star).where(T_meter.id == P())
    meter = conn.execute(q.get_sql(), (args.meter_id,)).fetchone()
    if not meter:
        err(f"Meter not found: {args.meter_id}")

    set_data, params, old_values = {}, [], {}

    if args.name is not None:
        old_values["service_point_id"] = meter["service_point_id"]
        set_data["service_point_id"] = P()
        params.append(args.name)

    if args.status is not None:
        if args.status not in VALID_METER_STATUSES:
            err(f"Invalid status: {args.status}. "
                 f"Must be one of: {', '.join(VALID_METER_STATUSES)}")
        old_values["status"] = meter["status"]
        set_data["status"] = P()
        params.append(args.status)

    if args.rate_plan_id is not None:
        rp_q = Q.from_(T_rate_plan).select(T_rate_plan.id).where(T_rate_plan.id == P())
        rp = conn.execute(rp_q.get_sql(), (args.rate_plan_id,)).fetchone()
        if not rp:
            err(f"Rate plan not found: {args.rate_plan_id}")
        old_values["rate_plan_id"] = meter["rate_plan_id"]
        set_data["rate_plan_id"] = P()
        params.append(args.rate_plan_id)

    if not set_data:
        err("No fields to update. Provide --name, --status, or --rate-plan-id")

    set_data["updated_at"] = P()
    params.append(_now())
    params.append(args.meter_id)

    q = Q.update(T_meter)
    for col, val in set_data.items():
        q = q.set(Field(col), val)
    q = q.where(T_meter.id == P())
    conn.execute(q.get_sql(), params)
    conn.commit()
    audit(conn, "erpclaw-billing", "update-meter", "meter", args.meter_id, old_values=old_values)

    q = Q.from_(T_meter).select(T_meter.star).where(T_meter.id == P())
    meter = row_to_dict(conn.execute(q.get_sql(), (args.meter_id,)).fetchone())
    ok({"meter": meter})


def get_meter(conn, args):
    """Get meter with latest reading."""
    if not args.meter_id:
        err("--meter-id is required")

    q = Q.from_(T_meter).select(T_meter.star).where(T_meter.id == P())
    meter = conn.execute(q.get_sql(), (args.meter_id,)).fetchone()
    if not meter:
        err(f"Meter not found: {args.meter_id}")

    result = row_to_dict(meter)

    q = (Q.from_(T_meter_reading).select(T_meter_reading.star)
         .where(T_meter_reading.meter_id == P())
         .orderby(T_meter_reading.reading_date, order=Order.desc)
         .limit(1))
    latest = conn.execute(q.get_sql(), (args.meter_id,)).fetchone()
    result["latest_reading"] = row_to_dict(latest) if latest else None

    q = (Q.from_(T_meter_reading)
         .select(fn.Count("*").as_("cnt"))
         .where(T_meter_reading.meter_id == P()))
    count = conn.execute(q.get_sql(), (args.meter_id,)).fetchone()
    result["reading_count"] = count["cnt"]
    ok({"meter": result})


def list_meters(conn, args):
    """List meters with optional filters."""
    m = Table("meter")
    c = Table("customer")
    limit = int(args.limit or 20)
    offset = int(args.offset or 0)
    params = []

    # Build count query
    count_q = Q.from_(m).select(fn.Count("*").as_("cnt"))
    # Build data query
    data_q = (Q.from_(m).select(m.star, c.name.as_("customer_name"))
              .left_join(c).on(m.customer_id == c.id))

    if args.customer_id:
        count_q = count_q.where(m.customer_id == P())
        data_q = data_q.where(m.customer_id == P())
        params.append(args.customer_id)
    if args.meter_type:
        count_q = count_q.where(m.service_type == P())
        data_q = data_q.where(m.service_type == P())
        params.append(args.meter_type)
    if args.status:
        count_q = count_q.where(m.status == P())
        data_q = data_q.where(m.status == P())
        params.append(args.status)

    total_count = conn.execute(count_q.get_sql(), params).fetchone()["cnt"]

    data_q = data_q.orderby(m.created_at, order=Order.desc).limit(P()).offset(P())
    rows = conn.execute(data_q.get_sql(), params + [limit, offset]).fetchall()
    ok({"meters": [dict(r) for r in rows], "total_count": total_count,
         "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


# =========================================================================
# METER READINGS (actions 5-6)
# =========================================================================

def add_meter_reading(conn, args):
    """Record a meter reading with auto-consumption calculation."""
    if not args.meter_id:
        err("--meter-id is required")
    if not args.reading_date:
        err("--reading-date is required")
    if not args.reading_value:
        err("--reading-value is required")

    q = Q.from_(T_meter).select(T_meter.star).where(T_meter.id == P())
    meter = conn.execute(q.get_sql(), (args.meter_id,)).fetchone()
    if not meter:
        err(f"Meter not found: {args.meter_id}")

    reading_type = args.reading_type or "actual"
    if reading_type not in VALID_READING_TYPES:
        err(f"Invalid reading-type: {reading_type}. "
             f"Must be one of: {', '.join(VALID_READING_TYPES)}")

    source = args.source or "manual"
    if source not in VALID_READING_SOURCES:
        err(f"Invalid source: {source}. "
             f"Must be one of: {', '.join(VALID_READING_SOURCES)}")

    reading_value = to_decimal(args.reading_value)
    previous_reading_value = None
    consumption = None

    if meter["last_reading_value"] is not None:
        previous_reading_value = to_decimal(meter["last_reading_value"])
        diff = reading_value - previous_reading_value
        if diff < 0:
            consumption = reading_value
            if reading_type == "actual":
                reading_type = "rollover"
        else:
            consumption = diff

    # Resolve UOM
    uom = args.uom
    if not uom and meter["metadata"]:
        try:
            uom = json.loads(meter["metadata"]).get("uom")
        except (json.JSONDecodeError, TypeError):
            pass

    reading_id = str(uuid.uuid4())
    now = _now()
    q = (Q.into(T_meter_reading)
         .columns("id", "meter_id", "reading_date", "reading_value",
                  "previous_reading_value", "consumption", "reading_type",
                  "uom", "source", "validated", "created_at")
         .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(),
                 ValueWrapper(0), P()))
    conn.execute(q.get_sql(),
        (reading_id, args.meter_id, args.reading_date,
         str(reading_value),
         str(previous_reading_value) if previous_reading_value is not None else None,
         str(consumption) if consumption is not None else None,
         reading_type, uom, source, now))

    q = (Q.update(T_meter)
         .set(T_meter.last_reading_date, P())
         .set(T_meter.last_reading_value, P())
         .set(T_meter.updated_at, P())
         .where(T_meter.id == P()))
    conn.execute(q.get_sql(),
        (args.reading_date, str(reading_value), now, args.meter_id))
    conn.commit()
    audit(conn, "erpclaw-billing", "add-meter-reading", "meter_reading", reading_id,
           new_values={"reading_value": str(reading_value),
                       "consumption": str(consumption) if consumption else None})

    q = Q.from_(T_meter_reading).select(T_meter_reading.star).where(T_meter_reading.id == P())
    reading = row_to_dict(conn.execute(q.get_sql(), (reading_id,)).fetchone())
    ok({"reading": reading})


def list_meter_readings(conn, args):
    """List meter readings with optional date filters."""
    if not args.meter_id:
        err("--meter-id is required")

    mr = Table("meter_reading")
    params = [args.meter_id]
    limit = int(args.limit or 20)
    offset = int(args.offset or 0)

    count_q = Q.from_(mr).select(fn.Count("*").as_("cnt")).where(mr.meter_id == P())
    data_q = Q.from_(mr).select(mr.star).where(mr.meter_id == P())

    if args.from_date:
        count_q = count_q.where(mr.reading_date >= P())
        data_q = data_q.where(mr.reading_date >= P())
        params.append(args.from_date)
    if args.to_date:
        count_q = count_q.where(mr.reading_date <= P())
        data_q = data_q.where(mr.reading_date <= P())
        params.append(args.to_date)

    total_count = conn.execute(count_q.get_sql(), params).fetchone()["cnt"]

    data_q = data_q.orderby(mr.reading_date, order=Order.desc).limit(P()).offset(P())
    rows = conn.execute(data_q.get_sql(), params + [limit, offset]).fetchall()
    ok({"readings": [dict(r) for r in rows], "total_count": total_count,
         "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


# =========================================================================
# USAGE EVENTS (actions 7-8)
# =========================================================================

def add_usage_event(conn, args):
    """Record a single usage event."""
    if not args.meter_id:
        err("--meter-id is required")
    if not args.event_date:
        err("--event-date is required")
    if not args.quantity:
        err("--quantity is required")

    q = Q.from_(T_meter).select(T_meter.id, T_meter.customer_id).where(T_meter.id == P())
    meter = conn.execute(q.get_sql(), (args.meter_id,)).fetchone()
    if not meter:
        err(f"Meter not found: {args.meter_id}")

    if args.idempotency_key:
        q = Q.from_(T_usage_event).select(T_usage_event.id).where(T_usage_event.idempotency_key == P())
        existing = conn.execute(q.get_sql(), (args.idempotency_key,)).fetchone()
        if existing:
            q = Q.from_(T_usage_event).select(T_usage_event.star).where(T_usage_event.id == P())
            evt = row_to_dict(conn.execute(q.get_sql(), (existing["id"],)).fetchone())
            ok({"usage_event": evt, "deduplicated": True})

    event_id = str(uuid.uuid4())
    event_type = args.event_type or "usage"

    q = (Q.into(T_usage_event)
         .columns("id", "customer_id", "meter_id", "event_type",
                  "quantity", "timestamp", "metadata", "idempotency_key",
                  "processed", "created_at")
         .insert(P(), P(), P(), P(), P(), P(), P(), P(),
                 ValueWrapper(0), P()))
    conn.execute(q.get_sql(),
        (event_id, meter["customer_id"], args.meter_id, event_type,
         args.quantity, args.event_date, args.properties, args.idempotency_key,
         _now()))
    conn.commit()
    audit(conn, "erpclaw-billing", "add-usage-event", "usage_event", event_id,
           new_values={"quantity": args.quantity, "event_type": event_type})

    q = Q.from_(T_usage_event).select(T_usage_event.star).where(T_usage_event.id == P())
    evt = row_to_dict(conn.execute(q.get_sql(), (event_id,)).fetchone())
    ok({"usage_event": evt})


def add_usage_events_batch(conn, args):
    """Bulk ingest usage events."""
    events_data = _parse_json_arg(args.events, "events")
    if not isinstance(events_data, list):
        err("--events must be a JSON array")
    if not events_data:
        err("--events array is empty")

    inserted = 0
    duplicates = 0
    errors = []

    for i, evt in enumerate(events_data):
        meter_id = evt.get("meter_id")
        event_date = evt.get("event_date")
        quantity = evt.get("quantity")
        event_type = evt.get("event_type", "usage")
        idempotency_key = evt.get("idempotency_key")
        metadata = json.dumps(evt.get("properties")) if evt.get("properties") else None

        if not meter_id or not event_date or not quantity:
            errors.append({"index": i, "error": "Missing meter_id, event_date, or quantity"})
            continue

        mq = Q.from_(T_meter).select(T_meter.id, T_meter.customer_id).where(T_meter.id == P())
        meter = conn.execute(mq.get_sql(), (meter_id,)).fetchone()
        if not meter:
            errors.append({"index": i, "error": f"Meter not found: {meter_id}"})
            continue

        if idempotency_key:
            iq = Q.from_(T_usage_event).select(T_usage_event.id).where(T_usage_event.idempotency_key == P())
            existing = conn.execute(iq.get_sql(), (idempotency_key,)).fetchone()
            if existing:
                duplicates += 1
                continue

        event_id = str(uuid.uuid4())
        ins_q = (Q.into(T_usage_event)
                 .columns("id", "customer_id", "meter_id", "event_type",
                          "quantity", "timestamp", "metadata", "idempotency_key",
                          "processed", "created_at")
                 .insert(P(), P(), P(), P(), P(), P(), P(), P(),
                         ValueWrapper(0), P()))
        conn.execute(ins_q.get_sql(),
            (event_id, meter["customer_id"], meter_id, event_type,
             str(quantity), event_date, metadata, idempotency_key, _now()))
        inserted += 1

    conn.commit()
    ok({
        "inserted": inserted,
        "duplicates": duplicates,
        "errors": errors,
        "total_processed": len(events_data),
    })


# =========================================================================
# RATE PLANS (actions 9-12)
# =========================================================================

def add_rate_plan(conn, args):
    """Create a rate/pricing plan with optional tiers."""
    if not args.name:
        err("--name is required")
    if not args.billing_model:
        err("--billing-model is required")

    plan_type = args.billing_model
    if plan_type not in VALID_PLAN_TYPES:
        err(f"Invalid billing-model: {plan_type}. "
             f"Must be one of: {', '.join(VALID_PLAN_TYPES)}")

    effective_from = args.effective_from or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if args.base_charge_period and args.base_charge_period not in VALID_BASE_CHARGE_PERIODS:
        err(f"Invalid base-charge-period: {args.base_charge_period}. "
             f"Must be one of: {', '.join(VALID_BASE_CHARGE_PERIODS)}")

    plan_id = str(uuid.uuid4())
    now = _now()
    q = (Q.into(T_rate_plan)
         .columns("id", "name", "service_type", "plan_type",
                  "base_charge", "base_charge_period", "currency", "effective_from",
                  "effective_to", "minimum_charge", "minimum_commitment", "overage_rate",
                  "metadata", "created_at", "updated_at")
         .insert(P(), P(), P(), P(), P(), P(), ValueWrapper("USD"), P(),
                 P(), P(), P(), P(), None, P(), P()))
    conn.execute(q.get_sql(),
        (plan_id, args.name, args.service_type, plan_type,
         args.base_charge, args.base_charge_period,
         effective_from, args.effective_to,
         args.minimum_charge, args.minimum_commitment, args.overage_rate,
         now, now))

    if args.tiers:
        tiers_data = _parse_json_arg(args.tiers, "tiers")
        if not isinstance(tiers_data, list):
            err("--tiers must be a JSON array")
        for i, tier in enumerate(tiers_data):
            tier_id = str(uuid.uuid4())
            tq = (Q.into(T_rate_tier)
                  .columns("id", "rate_plan_id", "tier_start", "tier_end",
                           "rate", "fixed_charge", "time_of_use_period",
                           "time_of_use_hours", "demand_type", "sort_order")
                  .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P()))
            conn.execute(tq.get_sql(),
                (tier_id, plan_id,
                 tier.get("tier_start", "0"), tier.get("tier_end"),
                 tier.get("rate", "0"), tier.get("fixed_charge"),
                 tier.get("time_of_use_period"), tier.get("time_of_use_hours"),
                 tier.get("demand_type"), i))

    conn.commit()
    audit(conn, "erpclaw-billing", "add-rate-plan", "rate_plan", plan_id,
           new_values={"name": args.name, "plan_type": plan_type})

    q = Q.from_(T_rate_plan).select(T_rate_plan.star).where(T_rate_plan.id == P())
    plan = row_to_dict(conn.execute(q.get_sql(), (plan_id,)).fetchone())
    q = (Q.from_(T_rate_tier).select(T_rate_tier.star)
         .where(T_rate_tier.rate_plan_id == P())
         .orderby(T_rate_tier.sort_order))
    tiers = [dict(r) for r in conn.execute(q.get_sql(), (plan_id,)).fetchall()]
    plan["tiers"] = tiers
    ok({"rate_plan": plan})


def update_rate_plan(conn, args):
    """Update rate plan configuration and/or tiers."""
    if not args.rate_plan_id:
        err("--rate-plan-id is required")

    q = Q.from_(T_rate_plan).select(T_rate_plan.star).where(T_rate_plan.id == P())
    plan = conn.execute(q.get_sql(), (args.rate_plan_id,)).fetchone()
    if not plan:
        err(f"Rate plan not found: {args.rate_plan_id}")

    set_data, params, old_values = {}, [], {}

    for field, col in [("name", "name"), ("base_charge", "base_charge"),
                       ("effective_to", "effective_to"),
                       ("minimum_charge", "minimum_charge"),
                       ("overage_rate", "overage_rate")]:
        val = getattr(args, field, None)
        if val is not None:
            old_values[col] = plan[col]
            set_data[col] = P()
            params.append(val)

    if set_data:
        set_data["updated_at"] = P()
        params.append(_now())
        params.append(args.rate_plan_id)
        uq = Q.update(T_rate_plan)
        for col, val in set_data.items():
            uq = uq.set(Field(col), val)
        uq = uq.where(T_rate_plan.id == P())
        conn.execute(uq.get_sql(), params)

    if args.tiers:
        tiers_data = _parse_json_arg(args.tiers, "tiers")
        if not isinstance(tiers_data, list):
            err("--tiers must be a JSON array")
        dq = Q.from_(T_rate_tier).delete().where(T_rate_tier.rate_plan_id == P())
        conn.execute(dq.get_sql(), (args.rate_plan_id,))
        for i, tier in enumerate(tiers_data):
            tier_id = str(uuid.uuid4())
            tq = (Q.into(T_rate_tier)
                  .columns("id", "rate_plan_id", "tier_start", "tier_end",
                           "rate", "fixed_charge", "time_of_use_period",
                           "time_of_use_hours", "demand_type", "sort_order")
                  .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(), P()))
            conn.execute(tq.get_sql(),
                (tier_id, args.rate_plan_id,
                 tier.get("tier_start", "0"), tier.get("tier_end"),
                 tier.get("rate", "0"), tier.get("fixed_charge"),
                 tier.get("time_of_use_period"), tier.get("time_of_use_hours"),
                 tier.get("demand_type"), i))

    if not set_data and not args.tiers:
        err("No fields to update")

    conn.commit()
    audit(conn, "erpclaw-billing", "update-rate-plan", "rate_plan", args.rate_plan_id,
           old_values=old_values)

    q = Q.from_(T_rate_plan).select(T_rate_plan.star).where(T_rate_plan.id == P())
    plan = row_to_dict(conn.execute(q.get_sql(), (args.rate_plan_id,)).fetchone())
    q = (Q.from_(T_rate_tier).select(T_rate_tier.star)
         .where(T_rate_tier.rate_plan_id == P())
         .orderby(T_rate_tier.sort_order))
    tiers = [dict(r) for r in conn.execute(q.get_sql(), (args.rate_plan_id,)).fetchall()]
    plan["tiers"] = tiers
    ok({"rate_plan": plan})


def get_rate_plan(conn, args):
    """Get rate plan with tiers."""
    if not args.rate_plan_id:
        err("--rate-plan-id is required")

    q = Q.from_(T_rate_plan).select(T_rate_plan.star).where(T_rate_plan.id == P())
    plan = conn.execute(q.get_sql(), (args.rate_plan_id,)).fetchone()
    if not plan:
        err(f"Rate plan not found: {args.rate_plan_id}")

    result = row_to_dict(plan)
    q = (Q.from_(T_rate_tier).select(T_rate_tier.star)
         .where(T_rate_tier.rate_plan_id == P())
         .orderby(T_rate_tier.sort_order))
    tiers = [dict(r) for r in conn.execute(q.get_sql(), (args.rate_plan_id,)).fetchall()]
    result["tiers"] = tiers
    ok({"rate_plan": result})


def list_rate_plans(conn, args):
    """List rate plans with optional filters."""
    params = []
    limit = int(args.limit or 20)
    offset = int(args.offset or 0)

    count_q = Q.from_(T_rate_plan).select(fn.Count("*").as_("cnt"))
    data_q = Q.from_(T_rate_plan).select(T_rate_plan.star)

    if args.service_type:
        count_q = count_q.where(T_rate_plan.service_type == P())
        data_q = data_q.where(T_rate_plan.service_type == P())
        params.append(args.service_type)

    total_count = conn.execute(count_q.get_sql(), params).fetchone()["cnt"]

    data_q = data_q.orderby(T_rate_plan.created_at, order=Order.desc).limit(P()).offset(P())
    rows = conn.execute(data_q.get_sql(), params + [limit, offset]).fetchall()
    ok({"rate_plans": [dict(r) for r in rows], "total_count": total_count,
         "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


# ---------------------------------------------------------------------------
# Internal: rate calculation engine
# ---------------------------------------------------------------------------

def _calculate_charge(plan_type, tiers, consumption, base_charge="0",
                      minimum_charge=None):
    """Pure function: calculate charges for a given consumption amount."""
    consumption = to_decimal(consumption)
    base = to_decimal(base_charge or "0")
    breakdown = []

    if plan_type == "flat":
        if not tiers:
            err("Flat rate plan requires at least one tier")
        rate = to_decimal(tiers[0].get("rate", "0"))
        usage_charge = round_currency(consumption * rate)
        breakdown.append({
            "tier": "flat", "consumption": str(consumption),
            "rate": str(rate), "charge": str(usage_charge),
        })

    elif plan_type == "tiered":
        usage_charge = Decimal("0")
        remaining = consumption
        sorted_tiers = sorted(tiers,
                              key=lambda t: to_decimal(t.get("tier_start", "0")))
        for tier in sorted_tiers:
            if remaining <= 0:
                break
            tier_start = to_decimal(tier.get("tier_start", "0"))
            tier_end_val = tier.get("tier_end")
            tier_end = to_decimal(tier_end_val) if tier_end_val else None
            rate = to_decimal(tier.get("rate", "0"))

            band_width = (tier_end - tier_start) if tier_end else remaining
            applicable = min(remaining, band_width)
            charge = round_currency(applicable * rate)
            usage_charge += charge
            remaining -= applicable
            breakdown.append({
                "tier_start": str(tier_start),
                "tier_end": str(tier_end) if tier_end else None,
                "consumption": str(applicable),
                "rate": str(rate), "charge": str(charge),
            })

    elif plan_type == "volume_discount":
        applicable_rate = Decimal("0")
        matched_tier = None
        sorted_tiers = sorted(tiers,
                              key=lambda t: to_decimal(t.get("tier_start", "0")))
        for tier in sorted_tiers:
            tier_start = to_decimal(tier.get("tier_start", "0"))
            tier_end_val = tier.get("tier_end")
            tier_end = to_decimal(tier_end_val) if tier_end_val else None
            if consumption >= tier_start and (tier_end is None or consumption < tier_end):
                applicable_rate = to_decimal(tier.get("rate", "0"))
                matched_tier = tier
                break

        usage_charge = round_currency(consumption * applicable_rate)
        breakdown.append({
            "tier": "volume_discount", "consumption": str(consumption),
            "rate": str(applicable_rate), "charge": str(usage_charge),
            "matched_tier_start": str(to_decimal(
                matched_tier.get("tier_start", "0"))) if matched_tier else None,
        })
    else:
        err(f"Rating for plan_type '{plan_type}' is not yet supported. "
             f"Supported: flat, tiered, volume_discount")

    total = round_currency(base + usage_charge)
    if minimum_charge:
        min_charge = to_decimal(minimum_charge)
        if total < min_charge:
            total = min_charge

    return {
        "usage_charge": str(usage_charge),
        "base_charge": str(base),
        "total_charge": str(total),
        "breakdown": breakdown,
    }


def rate_consumption(conn, args):
    """Pure function: calculate charges for consumption against a rate plan."""
    if not args.rate_plan_id:
        err("--rate-plan-id is required")
    if not args.consumption:
        err("--consumption is required")

    q = Q.from_(T_rate_plan).select(T_rate_plan.star).where(T_rate_plan.id == P())
    plan = conn.execute(q.get_sql(), (args.rate_plan_id,)).fetchone()
    if not plan:
        err(f"Rate plan not found: {args.rate_plan_id}")

    plan_type = plan["plan_type"]
    if plan_type not in VALID_SUPPORTED_PLAN_TYPES:
        err(f"Rating for plan_type '{plan_type}' is not yet supported. "
             f"Supported: {', '.join(VALID_SUPPORTED_PLAN_TYPES)}")

    q = (Q.from_(T_rate_tier).select(T_rate_tier.star)
         .where(T_rate_tier.rate_plan_id == P())
         .orderby(T_rate_tier.sort_order))
    tiers = [dict(r) for r in conn.execute(q.get_sql(), (args.rate_plan_id,)).fetchall()]

    result = _calculate_charge(
        plan_type, tiers, args.consumption,
        base_charge=plan["base_charge"],
        minimum_charge=plan["minimum_charge"],
    )
    result["rate_plan_name"] = plan["name"]
    result["plan_type"] = plan_type
    result["consumption"] = args.consumption
    ok({"calculation": result})


# =========================================================================
# BILLING PERIODS (actions 14-19)
# =========================================================================

def create_billing_period(conn, args):
    """Create a billing period for a customer/meter."""
    if not args.customer_id:
        err("--customer-id is required")
    if not args.meter_id:
        err("--meter-id is required")
    if not args.from_date:
        err("--from-date is required")
    if not args.to_date:
        err("--to-date is required")

    q = Q.from_(T_customer).select(T_customer.id).where(T_customer.id == P())
    cust = conn.execute(q.get_sql(), (args.customer_id,)).fetchone()
    if not cust:
        err(f"Customer not found: {args.customer_id}")

    q = Q.from_(T_meter).select(T_meter.star).where(T_meter.id == P())
    meter = conn.execute(q.get_sql(), (args.meter_id,)).fetchone()
    if not meter:
        err(f"Meter not found: {args.meter_id}")

    rate_plan_id = args.rate_plan_id or meter["rate_plan_id"]
    if not rate_plan_id:
        err("No rate plan specified. Provide --rate-plan-id or assign one to the meter")

    q = Q.from_(T_rate_plan).select(T_rate_plan.id).where(T_rate_plan.id == P())
    rp = conn.execute(q.get_sql(), (rate_plan_id,)).fetchone()
    if not rp:
        err(f"Rate plan not found: {rate_plan_id}")

    # Check for overlapping period
    q = (Q.from_(T_billing_period).select(T_billing_period.id)
         .where(T_billing_period.meter_id == P())
         .where(T_billing_period.status != ValueWrapper("void"))
         .where(T_billing_period.period_start <= P())
         .where(T_billing_period.period_end >= P()))
    overlap = conn.execute(q.get_sql(),
        (args.meter_id, args.to_date, args.from_date)).fetchone()
    if overlap:
        err(f"Overlapping billing period exists: {overlap['id']}")

    period_id = str(uuid.uuid4())
    now = _now()
    q = (Q.into(T_billing_period)
         .columns("id", "customer_id", "meter_id", "rate_plan_id",
                  "period_start", "period_end", "total_consumption", "base_charge",
                  "usage_charge", "adjustments_total", "subtotal", "tax_amount",
                  "grand_total", "status", "created_at", "updated_at")
         .insert(P(), P(), P(), P(), P(), P(),
                 ValueWrapper("0"), ValueWrapper("0"), ValueWrapper("0"),
                 ValueWrapper("0"), ValueWrapper("0"), ValueWrapper("0"),
                 ValueWrapper("0"), ValueWrapper("open"), P(), P()))
    conn.execute(q.get_sql(),
        (period_id, args.customer_id, args.meter_id, rate_plan_id,
         args.from_date, args.to_date, now, now))
    conn.commit()
    audit(conn, "erpclaw-billing", "create-billing-period", "billing_period", period_id,
           new_values={"period_start": args.from_date, "period_end": args.to_date})

    q = Q.from_(T_billing_period).select(T_billing_period.star).where(T_billing_period.id == P())
    bp = row_to_dict(conn.execute(q.get_sql(), (period_id,)).fetchone())
    ok({"billing_period": bp})


def run_billing(conn, args):
    """Execute bill run: aggregate usage, rate consumption, create periods."""
    if not args.company_id:
        err("--company-id is required")
    if not args.billing_date:
        err("--billing-date is required")

    q = Q.from_(T_company).select(T_company.id).where(T_company.id == P())
    company = conn.execute(q.get_sql(), (args.company_id,)).fetchone()
    if not company:
        err(f"Company not found: {args.company_id}")

    billing_date = args.billing_date
    from_date = args.from_date
    to_date = args.to_date or billing_date

    if not from_date:
        bd = datetime.strptime(billing_date, "%Y-%m-%d")
        from_date = (bd - timedelta(days=30)).strftime("%Y-%m-%d")

    # Find all customers for this company
    q = Q.from_(T_customer).select(T_customer.id).where(T_customer.company_id == P())
    customers = conn.execute(q.get_sql(), (args.company_id,)).fetchall()
    if not customers:
        ok({"periods_created": 0, "total_billed": "0.00",
             "message": "No customers found for this company"})

    customer_ids = [c["id"] for c in customers]
    placeholders = ",".join("?" * len(customer_ids))

    # Find active meters with rate plans
    meters = conn.execute(
        f"""SELECT m.* FROM meter m
            WHERE m.customer_id IN ({placeholders})
            AND m.status = 'active' AND m.rate_plan_id IS NOT NULL""",
        customer_ids).fetchall()

    if not meters:
        ok({"periods_created": 0, "total_billed": "0.00",
             "message": "No active meters with rate plans found"})

    created_periods = []
    total_billed = Decimal("0")

    for meter in meters:
        meter_id = meter["id"]
        rate_plan_id = meter["rate_plan_id"]

        # Skip if already billed for this period
        existing = conn.execute(
            """SELECT id, status FROM billing_period
               WHERE meter_id = ? AND period_start = ? AND period_end = ?
               AND status NOT IN ('void')""",
            (meter_id, from_date, to_date)).fetchone()
        if existing and existing["status"] in ("rated", "invoiced", "paid"):
            continue

        # Load rate plan + tiers
        pq = Q.from_(T_rate_plan).select(T_rate_plan.star).where(T_rate_plan.id == P())
        plan = conn.execute(pq.get_sql(), (rate_plan_id,)).fetchone()
        if not plan:
            continue

        plan_type = plan["plan_type"]
        if plan_type not in VALID_SUPPORTED_PLAN_TYPES:
            continue

        tq = (Q.from_(T_rate_tier).select(T_rate_tier.star)
              .where(T_rate_tier.rate_plan_id == P())
              .orderby(T_rate_tier.sort_order))
        tiers = [dict(r) for r in conn.execute(tq.get_sql(), (rate_plan_id,)).fetchall()]

        # Aggregate consumption from readings
        rq = (Q.from_(T_meter_reading)
              .select(fn.Coalesce(fn.Sum(T_meter_reading.consumption), 0).as_("total"))
              .where(T_meter_reading.meter_id == P())
              .where(T_meter_reading.reading_date >= P())
              .where(T_meter_reading.reading_date <= P())
              .where(T_meter_reading.consumption.isnotnull()))
        readings_row = conn.execute(rq.get_sql(), (meter_id, from_date, to_date)).fetchone()
        readings_consumption = to_decimal(str(readings_row["total"]))

        # Aggregate from unprocessed usage events
        eq = (Q.from_(T_usage_event)
              .select(fn.Coalesce(fn.Sum(T_usage_event.quantity), 0).as_("total"))
              .where(T_usage_event.meter_id == P())
              .where(T_usage_event.processed == ValueWrapper(0))
              .where(T_usage_event.timestamp >= P())
              .where(T_usage_event.timestamp <= P()))
        events_row = conn.execute(eq.get_sql(), (meter_id, from_date, to_date)).fetchone()
        events_consumption = to_decimal(str(events_row["total"]))

        total_consumption = readings_consumption + events_consumption

        # Rate the consumption
        charges = _calculate_charge(
            plan_type, tiers, str(total_consumption),
            base_charge=plan["base_charge"],
            minimum_charge=plan["minimum_charge"],
        )

        usage_charge = charges["usage_charge"]
        base_charge = charges["base_charge"]
        total_charge = charges["total_charge"]
        subtotal = total_charge  # Before adjustments

        # Create or update billing period
        now = _now()
        if existing and existing["status"] == "open":
            period_id = existing["id"]
            uq = (Q.update(T_billing_period)
                  .set(T_billing_period.total_consumption, P())
                  .set(T_billing_period.base_charge, P())
                  .set(T_billing_period.usage_charge, P())
                  .set(T_billing_period.subtotal, P())
                  .set(T_billing_period.grand_total, P())
                  .set(T_billing_period.status, ValueWrapper("rated"))
                  .set(T_billing_period.rated_at, P())
                  .set(T_billing_period.updated_at, P())
                  .where(T_billing_period.id == P()))
            conn.execute(uq.get_sql(),
                (str(total_consumption), base_charge, usage_charge,
                 subtotal, total_charge, now, now, period_id))
        else:
            period_id = str(uuid.uuid4())
            iq = (Q.into(T_billing_period)
                  .columns("id", "customer_id", "meter_id", "rate_plan_id",
                           "period_start", "period_end", "total_consumption",
                           "base_charge", "usage_charge", "adjustments_total",
                           "subtotal", "tax_amount", "grand_total", "status",
                           "rated_at", "created_at", "updated_at")
                  .insert(P(), P(), P(), P(), P(), P(), P(), P(), P(),
                          ValueWrapper("0"), P(), ValueWrapper("0"), P(),
                          ValueWrapper("rated"), P(), P(), P()))
            conn.execute(iq.get_sql(),
                (period_id, meter["customer_id"], meter_id, rate_plan_id,
                 from_date, to_date, str(total_consumption),
                 base_charge, usage_charge, subtotal, total_charge,
                 now, now, now))

        # Mark usage events as processed
        muq = (Q.update(T_usage_event)
               .set(T_usage_event.processed, ValueWrapper(1))
               .set(T_usage_event.billing_period_id, P())
               .where(T_usage_event.meter_id == P())
               .where(T_usage_event.processed == ValueWrapper(0))
               .where(T_usage_event.timestamp >= P())
               .where(T_usage_event.timestamp <= P()))
        conn.execute(muq.get_sql(), (period_id, meter_id, from_date, to_date))

        total_billed += to_decimal(total_charge)
        created_periods.append(period_id)

    conn.commit()
    audit(conn, "erpclaw-billing", "run-billing", "billing_period", ",".join(created_periods),
           new_values={"periods": len(created_periods),
                       "total_billed": str(round_currency(total_billed))})

    ok({
        "periods_created": len(created_periods),
        "period_ids": created_periods,
        "total_billed": str(round_currency(total_billed)),
    })


def generate_invoices(conn, args):
    """Create sales invoices from rated billing periods."""
    bp_ids = _parse_json_arg(args.billing_period_ids, "billing-period-ids")
    if not isinstance(bp_ids, list):
        err("--billing-period-ids must be a JSON array")

    # Try to find selling script (optional — invoice creation skipped if unavailable)
    from erpclaw_lib.dependencies import resolve_skill_script, table_exists
    from erpclaw_lib.args import SafeArgumentParser, check_unknown_args
    selling_script = resolve_skill_script("erpclaw") if table_exists(conn, "sales_invoice") else None

    results = []
    for bp_id in bp_ids:
        bq = Q.from_(T_billing_period).select(T_billing_period.star).where(T_billing_period.id == P())
        bp = conn.execute(bq.get_sql(), (bp_id,)).fetchone()
        if not bp:
            results.append({"billing_period_id": bp_id, "error": "Not found"})
            continue
        if bp["status"] != "rated":
            results.append({"billing_period_id": bp_id,
                            "error": f"Status is '{bp['status']}', expected 'rated'"})
            continue

        invoice_id = None
        if selling_script:
            try:
                cmd = [
                    "python3", selling_script,
                    "--action", "add-sales-invoice",
                    "--customer-id", bp["customer_id"],
                    "--items", json.dumps([{
                        "description": (f"Billing period "
                                        f"{bp['period_start']} to {bp['period_end']}"),
                        "qty": "1",
                        "rate": bp["grand_total"],
                    }]),
                ]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if proc.returncode == 0:
                    inv_result = json.loads(proc.stdout)
                    if inv_result.get("status") == "ok":
                        invoice_id = inv_result.get("sales_invoice", {}).get("id")
            except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
                pass

        inv_now = _now()
        uq = (Q.update(T_billing_period)
              .set(T_billing_period.status, ValueWrapper("invoiced"))
              .set(T_billing_period.invoiced_at, P())
              .set(T_billing_period.invoice_id, P())
              .set(T_billing_period.updated_at, P())
              .where(T_billing_period.id == P()))
        conn.execute(uq.get_sql(), (inv_now, invoice_id, inv_now, bp_id))
        results.append({
            "billing_period_id": bp_id,
            "invoice_id": invoice_id,
            "status": "invoiced",
        })

    conn.commit()
    invoiced_count = sum(1 for r in results if r.get("status") == "invoiced")
    ok({"invoiced": invoiced_count, "results": results})


def add_billing_adjustment(conn, args):
    """Add an adjustment (credit, late fee, etc.) to a billing period."""
    if not args.billing_period_id:
        err("--billing-period-id is required")
    if not args.amount:
        err("--amount is required")
    if not args.adjustment_type:
        err("--adjustment-type is required")

    if args.adjustment_type not in VALID_ADJUSTMENT_TYPES:
        err(f"Invalid adjustment-type: {args.adjustment_type}. "
             f"Must be one of: {', '.join(VALID_ADJUSTMENT_TYPES)}")

    q = Q.from_(T_billing_period).select(T_billing_period.star).where(T_billing_period.id == P())
    bp = conn.execute(q.get_sql(), (args.billing_period_id,)).fetchone()
    if not bp:
        err(f"Billing period not found: {args.billing_period_id}")

    adj_id = str(uuid.uuid4())
    q = (Q.into(T_billing_adjustment)
         .columns("id", "billing_period_id", "adjustment_type",
                  "amount", "reason", "approved_by", "created_at")
         .insert(P(), P(), P(), P(), P(), P(), P()))
    conn.execute(q.get_sql(),
        (adj_id, args.billing_period_id, args.adjustment_type,
         args.amount, args.reason, args.approved_by, _now()))

    # Recalculate totals (uses custom decimal_sum aggregate — keep DecimalSum)
    q = (Q.from_(T_billing_adjustment)
         .select(fn.Coalesce(DecimalSum(T_billing_adjustment.amount), ValueWrapper("0")).as_("total"))
         .where(T_billing_adjustment.billing_period_id == P()))
    adj_total_row = conn.execute(q.get_sql(), (args.billing_period_id,)).fetchone()
    adj_total = round_currency(to_decimal(str(adj_total_row["total"])))

    base = to_decimal(bp["base_charge"] or "0")
    usage = to_decimal(bp["usage_charge"] or "0")
    tax = to_decimal(bp["tax_amount"] or "0")
    subtotal = round_currency(base + usage + adj_total)
    grand_total = round_currency(subtotal + tax)

    now = _now()
    q = (Q.update(T_billing_period)
         .set(T_billing_period.adjustments_total, P())
         .set(T_billing_period.subtotal, P())
         .set(T_billing_period.grand_total, P())
         .set(T_billing_period.updated_at, P())
         .where(T_billing_period.id == P()))
    conn.execute(q.get_sql(),
        (str(adj_total), str(subtotal), str(grand_total), now, args.billing_period_id))
    conn.commit()

    audit(conn, "erpclaw-billing", "add-billing-adjustment", "billing_adjustment", adj_id,
           new_values={"amount": args.amount, "type": args.adjustment_type})

    q = Q.from_(T_billing_adjustment).select(T_billing_adjustment.star).where(T_billing_adjustment.id == P())
    adj = row_to_dict(conn.execute(q.get_sql(), (adj_id,)).fetchone())
    adj["updated_grand_total"] = str(grand_total)
    ok({"adjustment": adj})


def list_billing_periods(conn, args):
    """List billing periods with optional filters."""
    bp = Table("billing_period")
    c = Table("customer")
    m = Table("meter")
    params = []
    limit = int(args.limit or 20)
    offset = int(args.offset or 0)

    count_q = Q.from_(bp).select(fn.Count("*").as_("cnt"))
    data_q = (Q.from_(bp)
              .select(bp.star, c.name.as_("customer_name"), m.meter_number)
              .left_join(c).on(bp.customer_id == c.id)
              .left_join(m).on(bp.meter_id == m.id))

    if args.customer_id:
        count_q = count_q.where(bp.customer_id == P())
        data_q = data_q.where(bp.customer_id == P())
        params.append(args.customer_id)
    if args.meter_id:
        count_q = count_q.where(bp.meter_id == P())
        data_q = data_q.where(bp.meter_id == P())
        params.append(args.meter_id)
    if args.status:
        count_q = count_q.where(bp.status == P())
        data_q = data_q.where(bp.status == P())
        params.append(args.status)
    if args.from_date:
        count_q = count_q.where(bp.period_start >= P())
        data_q = data_q.where(bp.period_start >= P())
        params.append(args.from_date)
    if args.to_date:
        count_q = count_q.where(bp.period_end <= P())
        data_q = data_q.where(bp.period_end <= P())
        params.append(args.to_date)

    total_count = conn.execute(count_q.get_sql(), params).fetchone()["cnt"]

    data_q = data_q.orderby(bp.created_at, order=Order.desc).limit(P()).offset(P())
    rows = conn.execute(data_q.get_sql(), params + [limit, offset]).fetchall()
    ok({"billing_periods": [dict(r) for r in rows], "total_count": total_count,
         "limit": limit, "offset": offset,
         "has_more": offset + limit < total_count})


def get_billing_period(conn, args):
    """Get billing period with adjustments."""
    if not args.billing_period_id:
        err("--billing-period-id is required")

    bpt = Table("billing_period")
    c = Table("customer")
    m = Table("meter")
    rp = Table("rate_plan")
    q = (Q.from_(bpt)
         .select(bpt.star, c.name.as_("customer_name"),
                 m.meter_number, rp.name.as_("rate_plan_name"))
         .left_join(c).on(bpt.customer_id == c.id)
         .left_join(m).on(bpt.meter_id == m.id)
         .left_join(rp).on(bpt.rate_plan_id == rp.id)
         .where(bpt.id == P()))
    bp = conn.execute(q.get_sql(), (args.billing_period_id,)).fetchone()
    if not bp:
        err(f"Billing period not found: {args.billing_period_id}")

    result = row_to_dict(bp)
    q = (Q.from_(T_billing_adjustment).select(T_billing_adjustment.star)
         .where(T_billing_adjustment.billing_period_id == P())
         .orderby(T_billing_adjustment.created_at))
    adjustments = [dict(r) for r in conn.execute(q.get_sql(), (args.billing_period_id,)).fetchall()]
    result["adjustments"] = adjustments
    ok({"billing_period": result})


# =========================================================================
# PREPAID CREDITS (actions 20-21)
# =========================================================================

def add_prepaid_credit(conn, args):
    """Record a prepaid commitment."""
    if not args.customer_id:
        err("--customer-id is required")
    if not args.amount:
        err("--amount is required")
    if not args.valid_until:
        err("--valid-until is required")

    q = Q.from_(T_customer).select(T_customer.id).where(T_customer.id == P())
    cust = conn.execute(q.get_sql(), (args.customer_id,)).fetchone()
    if not cust:
        err(f"Customer not found: {args.customer_id}")

    rate_plan_id = args.rate_plan_id
    if rate_plan_id:
        q = Q.from_(T_rate_plan).select(T_rate_plan.id).where(T_rate_plan.id == P())
        rp = conn.execute(q.get_sql(), (rate_plan_id,)).fetchone()
        if not rp:
            err(f"Rate plan not found: {rate_plan_id}")
    else:
        # Find any rate plan with type prepaid_credit, or use first available
        q = (Q.from_(T_rate_plan).select(T_rate_plan.id)
             .where(T_rate_plan.plan_type == ValueWrapper("prepaid_credit"))
             .limit(1))
        rp = conn.execute(q.get_sql()).fetchone()
        if not rp:
            q = Q.from_(T_rate_plan).select(T_rate_plan.id).limit(1)
            rp = conn.execute(q.get_sql()).fetchone()
        if not rp:
            err("No rate plan available. Create one first")
        rate_plan_id = rp["id"]

    period_start = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    amount = args.amount
    now = _now()

    credit_id = str(uuid.uuid4())
    q = (Q.into(T_prepaid)
         .columns("id", "customer_id", "rate_plan_id", "original_amount",
                  "remaining_amount", "period_start", "period_end",
                  "overage_amount", "status", "created_at", "updated_at")
         .insert(P(), P(), P(), P(), P(), P(), P(),
                 ValueWrapper("0"), ValueWrapper("active"), P(), P()))
    conn.execute(q.get_sql(),
        (credit_id, args.customer_id, rate_plan_id,
         amount, amount, period_start, args.valid_until, now, now))
    conn.commit()
    audit(conn, "erpclaw-billing", "add-prepaid-credit", "prepaid_credit_balance", credit_id,
           new_values={"amount": amount, "valid_until": args.valid_until})

    q = Q.from_(T_prepaid).select(T_prepaid.star).where(T_prepaid.id == P())
    credit = row_to_dict(conn.execute(q.get_sql(), (credit_id,)).fetchone())
    ok({"prepaid_credit": credit})


def get_prepaid_balance(conn, args):
    """Check remaining prepaid credits for a customer."""
    if not args.customer_id:
        err("--customer-id is required")

    q = (Q.from_(T_prepaid).select(T_prepaid.star)
         .where(T_prepaid.customer_id == P())
         .orderby(T_prepaid.created_at, order=Order.desc))
    rows = conn.execute(q.get_sql(), (args.customer_id,)).fetchall()

    balances = [dict(r) for r in rows]
    total_remaining = Decimal("0")
    active_count = 0
    for b in balances:
        if b["status"] == "active":
            total_remaining += to_decimal(b["remaining_amount"] or "0")
            active_count += 1

    ok({
        "customer_id": args.customer_id,
        "active_credits": active_count,
        "total_remaining": str(round_currency(total_remaining)),
        "balances": balances,
    })


# =========================================================================
# STATUS (action 22)
# =========================================================================

def status_action(conn, args):
    """Billing summary."""
    # Dynamic IN clauses — keep as raw SQL for variable-length placeholders
    where = ""
    params = []
    cust_where = ""

    if args.company_id:
        q = Q.from_(T_company).select(T_company.id).where(T_company.id == P())
        company = conn.execute(q.get_sql(), (args.company_id,)).fetchone()
        if not company:
            err(f"Company not found: {args.company_id}")
        cq = Q.from_(T_customer).select(T_customer.id).where(T_customer.company_id == P())
        cust_ids = [r["id"] for r in conn.execute(cq.get_sql(), (args.company_id,)).fetchall()]
        if cust_ids:
            placeholders = ",".join("?" * len(cust_ids))
            where = f"WHERE customer_id IN ({placeholders})"
            params = cust_ids
            cust_where = where

    # Meter counts by status (dynamic IN — raw SQL)
    meter_q = f"SELECT status, COUNT(*) as cnt FROM meter {where} GROUP BY status"
    meter_counts = {}
    for row in conn.execute(meter_q, params).fetchall():
        meter_counts[row["status"]] = row["cnt"]

    # Billing period counts by status (dynamic IN — raw SQL)
    bp_q = f"SELECT status, COUNT(*) as cnt FROM billing_period {cust_where} GROUP BY status"
    bp_counts = {}
    for row in conn.execute(bp_q, params).fetchall():
        bp_counts[row["status"]] = row["cnt"]

    # Unprocessed usage events (dynamic IN — raw SQL)
    evt_q = "SELECT COUNT(*) as cnt FROM usage_event WHERE processed = 0"
    if params:
        evt_q += f" AND customer_id IN ({','.join('?' * len(params))})"
    unprocessed = conn.execute(evt_q, params).fetchone()["cnt"]

    # Rate plans count
    rp_q = Q.from_(T_rate_plan).select(fn.Count("*").as_("cnt"))
    rp_count = conn.execute(rp_q.get_sql()).fetchone()["cnt"]

    # Prepaid balance count (dynamic IN — raw SQL)
    prepaid_q = f"SELECT COUNT(*) as cnt FROM prepaid_credit_balance {cust_where}"
    prepaid_count = conn.execute(prepaid_q, params).fetchone()["cnt"]

    ok({
        "meters": meter_counts,
        "meters_total": sum(meter_counts.values()),
        "billing_periods": bp_counts,
        "billing_periods_total": sum(bp_counts.values()),
        "rate_plans_total": rp_count,
        "unprocessed_events": unprocessed,
        "prepaid_balances": prepaid_count,
    })


# =========================================================================
# Action registry + main
# =========================================================================

ACTIONS = {
    "add-meter": add_meter,
    "update-meter": update_meter,
    "get-meter": get_meter,
    "list-meters": list_meters,
    "add-meter-reading": add_meter_reading,
    "list-meter-readings": list_meter_readings,
    "add-usage-event": add_usage_event,
    "add-usage-events-batch": add_usage_events_batch,
    "add-rate-plan": add_rate_plan,
    "update-rate-plan": update_rate_plan,
    "get-rate-plan": get_rate_plan,
    "list-rate-plans": list_rate_plans,
    "rate-consumption": rate_consumption,
    "create-billing-period": create_billing_period,
    "run-billing": run_billing,
    "generate-invoices": generate_invoices,
    "add-billing-adjustment": add_billing_adjustment,
    "list-billing-periods": list_billing_periods,
    "get-billing-period": get_billing_period,
    "add-prepaid-credit": add_prepaid_credit,
    "get-prepaid-balance": get_prepaid_balance,
    "status": status_action,
}


def main():
    parser = SafeArgumentParser(description="ERPClaw Billing")
    parser.add_argument("--action", required=True, choices=list(ACTIONS.keys()))
    parser.add_argument("--db-path", default=None)
    # Entity IDs
    parser.add_argument("--meter-id")
    parser.add_argument("--rate-plan-id")
    parser.add_argument("--billing-period-id")
    parser.add_argument("--customer-id")
    parser.add_argument("--company-id")
    parser.add_argument("--item-id")
    parser.add_argument("--serial-number-id")
    # Meter fields
    parser.add_argument("--name")
    parser.add_argument("--meter-type")
    parser.add_argument("--unit")
    parser.add_argument("--install-date")
    parser.add_argument("--address")
    parser.add_argument("--status")
    # Reading fields
    parser.add_argument("--reading-date")
    parser.add_argument("--reading-value")
    parser.add_argument("--reading-type")
    parser.add_argument("--source")
    parser.add_argument("--uom")
    parser.add_argument("--estimated-reason")
    # Usage event fields
    parser.add_argument("--event-date")
    parser.add_argument("--event-type")
    parser.add_argument("--quantity")
    parser.add_argument("--properties")
    parser.add_argument("--idempotency-key")
    parser.add_argument("--events")
    # Rate plan fields
    parser.add_argument("--billing-model")
    parser.add_argument("--tiers")
    parser.add_argument("--base-charge")
    parser.add_argument("--base-charge-period")
    parser.add_argument("--effective-from")
    parser.add_argument("--effective-to")
    parser.add_argument("--minimum-charge")
    parser.add_argument("--minimum-commitment")
    parser.add_argument("--overage-rate")
    parser.add_argument("--service-type")
    parser.add_argument("--consumption")
    # Billing fields
    parser.add_argument("--from-date")
    parser.add_argument("--to-date")
    parser.add_argument("--billing-date")
    parser.add_argument("--billing-period-ids")
    # Adjustment fields
    parser.add_argument("--amount")
    parser.add_argument("--adjustment-type")
    parser.add_argument("--reason")
    parser.add_argument("--approved-by")
    # Prepaid fields
    parser.add_argument("--valid-until")
    # Filters
    parser.add_argument("--limit", default="20")
    parser.add_argument("--offset", default="0")

    args, unknown = parser.parse_known_args()
    check_unknown_args(parser, unknown)
    check_input_lengths(args)

    db_path = args.db_path
    if db_path:
        os.environ["ERPCLAW_DB_PATH"] = db_path

    ensure_db_exists()
    conn = get_connection()

    # Dependency check
    _dep = check_required_tables(conn, REQUIRED_TABLES)
    if _dep:
        _dep["suggestion"] = "clawhub install " + " ".join(_dep.get("missing_skills", []))
        print(json.dumps(_dep, indent=2))
        conn.close()
        sys.exit(1)

    try:
        ACTIONS[args.action](conn, args)
    except SystemExit:
        raise
    except Exception as e:
        sys.stderr.write(f"[erpclaw-billing] {e}\n")
        err("An unexpected error occurred")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
