"""
ERPClaw Database Initialization
================================
Creates all tables for the ERPClaw system in a single SQLite database.
Tables are grouped by owning skill. Every table uses:
  - id TEXT PRIMARY KEY (UUID stored as hex string)
  - CREATE TABLE IF NOT EXISTS
  - Foreign keys with ON DELETE RESTRICT
  - TEXT for all financial amounts (Python Decimal for calculations)
  - TEXT for dates/timestamps (ISO 8601)
  - INTEGER for booleans with CHECK(field IN (0,1))
  - CHECK constraints for all ENUMs

Usage:
    python init_db.py [--db-path PATH]
    Default path: ~/.openclaw/erpclaw/data.sqlite
"""

import os
import sys
import sqlite3
import argparse
from pathlib import Path


DEFAULT_DB_PATH = os.path.expanduser("~/.openclaw/erpclaw/data.sqlite")


# ---------------------------------------------------------------------------
# SKILL: erpclaw-setup
# Tables: company, currency, exchange_rate, payment_terms, uom,
#         regional_settings, custom_field, property_setter,
#         schema_version, audit_log, erp_user, role, user_role,
#         role_permission, user_permission
# ---------------------------------------------------------------------------

SETUP_TABLES = """
-- =========================================================================
-- SKILL: erpclaw-setup (System Admin)
-- =========================================================================

CREATE TABLE IF NOT EXISTS schema_version (
    module          TEXT NOT NULL,
    version         INTEGER NOT NULL DEFAULT 1,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (module)
);

CREATE TABLE IF NOT EXISTS audit_log (
    id              TEXT PRIMARY KEY,
    timestamp       TEXT DEFAULT CURRENT_TIMESTAMP,
    user_id         TEXT,
    skill           TEXT NOT NULL,
    action          TEXT NOT NULL,
    entity_type     TEXT,
    entity_id       TEXT,
    old_values      TEXT,   -- JSON
    new_values      TEXT,   -- JSON
    description     TEXT
);

CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_skill ON audit_log(skill);

CREATE TABLE IF NOT EXISTS action_call_log (
    id              TEXT PRIMARY KEY,
    timestamp       TEXT DEFAULT CURRENT_TIMESTAMP,
    action_name     TEXT NOT NULL,
    routed_to       TEXT NOT NULL,          -- domain or module name
    route_tier      INTEGER NOT NULL,       -- 0=standalone, 1=alias, 2=core, 3=module
    session_id      TEXT                    -- groups actions within one L2 test scenario
);

CREATE INDEX IF NOT EXISTS idx_action_call_log_ts ON action_call_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_action_call_log_action ON action_call_log(action_name);
CREATE INDEX IF NOT EXISTS idx_action_call_log_session ON action_call_log(session_id);
CREATE INDEX IF NOT EXISTS idx_action_call_log_routed ON action_call_log(routed_to);

CREATE TABLE IF NOT EXISTS company (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    abbr            TEXT NOT NULL UNIQUE,
    default_currency TEXT NOT NULL DEFAULT 'USD',
    country         TEXT NOT NULL DEFAULT 'United States',
    tax_id          TEXT,            -- EIN for US companies
    default_receivable_account_id TEXT,
    default_payable_account_id    TEXT,
    default_income_account_id     TEXT,
    default_expense_account_id    TEXT,
    default_cost_center_id        TEXT,
    default_warehouse_id          TEXT,
    default_bank_account_id       TEXT,
    default_cash_account_id       TEXT,
    round_off_account_id          TEXT,
    exchange_gain_loss_account_id TEXT,
    stock_received_not_billed_account_id TEXT,
    stock_adjustment_account_id   TEXT,
    depreciation_expense_account_id TEXT,
    accumulated_depreciation_account_id TEXT,
    perpetual_inventory           INTEGER NOT NULL DEFAULT 1 CHECK(perpetual_inventory IN (0,1)),
    enable_negative_stock         INTEGER NOT NULL DEFAULT 0 CHECK(enable_negative_stock IN (0,1)),
    accounts_frozen_till_date     TEXT,
    role_allowed_for_frozen_entries TEXT,
    fiscal_year_start_month       INTEGER NOT NULL DEFAULT 1,
    -- 3-way match policy for purchase invoices: strict/tolerant/disabled
    three_way_match_policy        TEXT NOT NULL DEFAULT 'strict'
                    CHECK(three_way_match_policy IN ('strict','tolerant','disabled')),
    -- GRN tolerance: percentage over-receipt allowed (0 = strict, 5 = allow 5% over)
    receipt_tolerance_pct         TEXT NOT NULL DEFAULT '0',
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS currency (
    code            TEXT PRIMARY KEY,  -- ISO 4217: USD, EUR, etc.
    name            TEXT NOT NULL,
    symbol          TEXT,
    decimal_places  INTEGER NOT NULL DEFAULT 2,
    enabled         INTEGER NOT NULL DEFAULT 1 CHECK(enabled IN (0,1))
);

CREATE TABLE IF NOT EXISTS exchange_rate (
    id              TEXT PRIMARY KEY,
    from_currency   TEXT NOT NULL REFERENCES currency(code) ON DELETE RESTRICT,
    to_currency     TEXT NOT NULL REFERENCES currency(code) ON DELETE RESTRICT,
    rate            TEXT NOT NULL,     -- decimal(12,6) stored as TEXT
    effective_date  TEXT NOT NULL,     -- YYYY-MM-DD
    source          TEXT NOT NULL DEFAULT 'manual' CHECK(source IN ('manual','api','bank_feed')),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_exchange_rate_pair_date
    ON exchange_rate(from_currency, to_currency, effective_date);

CREATE TABLE IF NOT EXISTS payment_terms (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    due_days        INTEGER NOT NULL DEFAULT 30,
    discount_percentage TEXT,  -- decimal
    discount_days   INTEGER,
    description     TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS uom (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    must_be_whole_number INTEGER NOT NULL DEFAULT 0 CHECK(must_be_whole_number IN (0,1))
);

CREATE TABLE IF NOT EXISTS uom_conversion (
    id              TEXT PRIMARY KEY,
    from_uom        TEXT NOT NULL REFERENCES uom(id) ON DELETE RESTRICT,
    to_uom          TEXT NOT NULL REFERENCES uom(id) ON DELETE RESTRICT,
    conversion_factor TEXT NOT NULL,  -- decimal
    item_id         TEXT,             -- nullable, for item-specific conversions
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS regional_settings (
    id              TEXT PRIMARY KEY,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    key             TEXT NOT NULL,
    value           TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, key)
);

CREATE TABLE IF NOT EXISTS custom_field (
    id              TEXT PRIMARY KEY,
    table_name      TEXT NOT NULL,
    field_name      TEXT NOT NULL,
    field_type      TEXT NOT NULL,
    field_options   TEXT,   -- JSON: enum values, FK target, etc.
    label           TEXT,
    required        INTEGER NOT NULL DEFAULT 0 CHECK(required IN (0,1)),
    default_value   TEXT,
    insert_after    TEXT,   -- field name to position after
    owner_skill     TEXT NOT NULL,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(table_name, field_name)
);

CREATE TABLE IF NOT EXISTS property_setter (
    id              TEXT PRIMARY KEY,
    table_name      TEXT NOT NULL,
    field_name      TEXT NOT NULL,
    property        TEXT NOT NULL,  -- e.g. 'mandatory', 'hidden', 'default'
    value           TEXT,
    owner_skill     TEXT NOT NULL,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(table_name, field_name, property)
);

-- -------------------------------------------------------------------------
-- RBAC: Role-Based Access Control
-- -------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS erp_user (
    id              TEXT PRIMARY KEY,
    username        TEXT NOT NULL UNIQUE,  -- telegram username or custom
    email           TEXT UNIQUE,
    full_name       TEXT,
    status          TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','disabled','locked')),
    company_ids     TEXT,   -- JSON array of company IDs this user can access
    last_login      TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_erp_user_username ON erp_user(username);
CREATE INDEX IF NOT EXISTS idx_erp_user_status ON erp_user(status);

CREATE TABLE IF NOT EXISTS role (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    description     TEXT,
    is_system       INTEGER NOT NULL DEFAULT 0 CHECK(is_system IN (0,1)),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_role (
    id              TEXT PRIMARY KEY,
    user_id         TEXT NOT NULL REFERENCES erp_user(id) ON DELETE CASCADE,
    role_id         TEXT NOT NULL REFERENCES role(id) ON DELETE CASCADE,
    company_id      TEXT REFERENCES company(id) ON DELETE CASCADE,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, role_id, company_id)
);

CREATE INDEX IF NOT EXISTS idx_user_role_user ON user_role(user_id);
CREATE INDEX IF NOT EXISTS idx_user_role_role ON user_role(role_id);
CREATE INDEX IF NOT EXISTS idx_user_role_company ON user_role(company_id);

CREATE TABLE IF NOT EXISTS role_permission (
    id              TEXT PRIMARY KEY,
    role_id         TEXT NOT NULL REFERENCES role(id) ON DELETE CASCADE,
    skill           TEXT NOT NULL,          -- e.g. 'erpclaw-gl', 'erpclaw-payments'
    action_pattern  TEXT NOT NULL,          -- e.g. 'submit-*', 'list-*', '*'
    allowed         INTEGER NOT NULL DEFAULT 1 CHECK(allowed IN (0,1)),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, skill, action_pattern)
);

CREATE INDEX IF NOT EXISTS idx_role_permission_role ON role_permission(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permission_skill ON role_permission(skill);

CREATE TABLE IF NOT EXISTS user_permission (
    id              TEXT PRIMARY KEY,
    user_id         TEXT NOT NULL REFERENCES erp_user(id) ON DELETE CASCADE,
    entity_type     TEXT NOT NULL,          -- e.g. 'company', 'cost_center', 'warehouse'
    entity_id       TEXT NOT NULL,          -- the specific entity's ID
    can_read        INTEGER NOT NULL DEFAULT 1 CHECK(can_read IN (0,1)),
    can_write       INTEGER NOT NULL DEFAULT 0 CHECK(can_write IN (0,1)),
    can_submit      INTEGER NOT NULL DEFAULT 0 CHECK(can_submit IN (0,1)),
    can_cancel      INTEGER NOT NULL DEFAULT 0 CHECK(can_cancel IN (0,1)),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, entity_type, entity_id)
);

CREATE INDEX IF NOT EXISTS idx_user_permission_user ON user_permission(user_id);
CREATE INDEX IF NOT EXISTS idx_user_permission_entity ON user_permission(entity_type, entity_id);
"""


# ---------------------------------------------------------------------------
# SKILL: erpclaw-gl
# Tables: account, gl_entry, fiscal_year, period_closing_voucher,
#         cost_center, budget, naming_series
# NOTE: elimination_rule, elimination_entry moved to erpclaw-growth
# ---------------------------------------------------------------------------

GL_TABLES = """
-- =========================================================================
-- SKILL: erpclaw-gl (GL Accountant)
-- =========================================================================

CREATE TABLE IF NOT EXISTS account (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    account_number  TEXT,
    parent_id       TEXT REFERENCES account(id) ON DELETE RESTRICT,
    root_type       TEXT NOT NULL CHECK(root_type IN ('asset','liability','equity','income','expense')),
    account_type    TEXT CHECK(account_type IN (
                        'bank','cash','receivable','payable','stock',
                        'fixed_asset','accumulated_depreciation',
                        'cost_of_goods_sold','tax','equity','revenue',
                        'expense','stock_received_not_billed',
                        'stock_adjustment','rounding','exchange_gain_loss',
                        'depreciation','payroll_payable','temporary',
                        'asset_received_not_billed'
                    )),
    currency        TEXT NOT NULL DEFAULT 'USD',
    is_group        INTEGER NOT NULL DEFAULT 0 CHECK(is_group IN (0,1)),
    is_frozen       INTEGER NOT NULL DEFAULT 0 CHECK(is_frozen IN (0,1)),
    disabled        INTEGER NOT NULL DEFAULT 0 CHECK(disabled IN (0,1)),
    balance_direction TEXT NOT NULL DEFAULT 'debit_normal'
                    CHECK(balance_direction IN ('debit_normal','credit_normal')),
    balance_must_be TEXT CHECK(balance_must_be IN ('debit','credit')),
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    depth           INTEGER NOT NULL DEFAULT 0,
    lft             INTEGER,
    rgt             INTEGER,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(account_number, company_id)
);

CREATE INDEX IF NOT EXISTS idx_account_company ON account(company_id);
CREATE INDEX IF NOT EXISTS idx_account_parent ON account(parent_id);
CREATE INDEX IF NOT EXISTS idx_account_root_type ON account(root_type);
CREATE INDEX IF NOT EXISTS idx_account_type ON account(account_type);

CREATE TABLE IF NOT EXISTS gl_entry (
    id              TEXT PRIMARY KEY,
    posting_date    TEXT NOT NULL,     -- YYYY-MM-DD
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    account_id      TEXT NOT NULL REFERENCES account(id) ON DELETE RESTRICT,
    party_type      TEXT CHECK(party_type IN ('customer','supplier','employee')),
    party_id        TEXT,
    debit           TEXT NOT NULL DEFAULT '0',   -- decimal(18,6)
    credit          TEXT NOT NULL DEFAULT '0',   -- decimal(18,6)
    currency        TEXT NOT NULL DEFAULT 'USD',
    debit_base      TEXT NOT NULL DEFAULT '0',   -- decimal(18,6) in company currency
    credit_base     TEXT NOT NULL DEFAULT '0',   -- decimal(18,6) in company currency
    exchange_rate   TEXT NOT NULL DEFAULT '1',    -- decimal(12,6)
    voucher_type    TEXT NOT NULL CHECK(voucher_type IN (
                        'journal_entry','sales_invoice','purchase_invoice',
                        'payment_entry','stock_entry','depreciation_entry',
                        'payroll_entry','period_closing','expense_claim',
                        'asset_disposal','stock_reconciliation',
                        'purchase_receipt','delivery_note',
                        'credit_note','debit_note','work_order',
                        'exchange_rate_revaluation','stock_revaluation',
                        'elimination_entry'
                    )),
    voucher_id      TEXT NOT NULL,
    entry_set       TEXT NOT NULL DEFAULT 'primary',  -- 'primary', 'cogs', 'tax' etc.
    cost_center_id  TEXT REFERENCES cost_center(id) ON DELETE RESTRICT,
    project_id      TEXT,
    remarks         TEXT,
    fiscal_year     TEXT,
    is_cancelled    INTEGER NOT NULL DEFAULT 0 CHECK(is_cancelled IN (0,1)),
    cancelled_by    TEXT,
    sequence        INTEGER,
    gl_checksum     TEXT         -- SHA-256 chain hash for tamper detection
    -- NOTE: gl_entry is immutable — no updated_at column
);

CREATE INDEX IF NOT EXISTS idx_gl_entry_voucher ON gl_entry(voucher_type, voucher_id);
CREATE INDEX IF NOT EXISTS idx_gl_entry_voucher_set ON gl_entry(voucher_type, voucher_id, entry_set);
CREATE INDEX IF NOT EXISTS idx_gl_entry_account_date ON gl_entry(account_id, posting_date);
CREATE INDEX IF NOT EXISTS idx_gl_entry_posting_date ON gl_entry(posting_date);
CREATE INDEX IF NOT EXISTS idx_gl_entry_fiscal_year ON gl_entry(fiscal_year);
CREATE INDEX IF NOT EXISTS idx_gl_entry_party ON gl_entry(party_type, party_id);
CREATE INDEX IF NOT EXISTS idx_gl_entry_cost_center ON gl_entry(cost_center_id);
CREATE INDEX IF NOT EXISTS idx_gl_entry_is_cancelled ON gl_entry(is_cancelled);

CREATE TABLE IF NOT EXISTS fiscal_year (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    start_date      TEXT NOT NULL,
    end_date        TEXT NOT NULL,
    is_closed       INTEGER NOT NULL DEFAULT 0 CHECK(is_closed IN (0,1)),
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fiscal_year_company ON fiscal_year(company_id);
CREATE INDEX IF NOT EXISTS idx_fiscal_year_dates ON fiscal_year(start_date, end_date);

CREATE TABLE IF NOT EXISTS period_closing_voucher (
    id              TEXT PRIMARY KEY,
    fiscal_year_id  TEXT NOT NULL REFERENCES fiscal_year(id) ON DELETE RESTRICT,
    posting_date    TEXT NOT NULL,
    closing_account_id TEXT NOT NULL REFERENCES account(id) ON DELETE RESTRICT,
    net_pl_amount   TEXT NOT NULL DEFAULT '0',  -- decimal(18,6)
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN ('draft','submitted','cancelled')),
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cost_center (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    parent_id       TEXT REFERENCES cost_center(id) ON DELETE RESTRICT,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    is_group        INTEGER NOT NULL DEFAULT 0 CHECK(is_group IN (0,1)),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cost_center_company ON cost_center(company_id);
CREATE INDEX IF NOT EXISTS idx_cost_center_parent ON cost_center(parent_id);

CREATE TABLE IF NOT EXISTS budget (
    id              TEXT PRIMARY KEY,
    fiscal_year_id  TEXT NOT NULL REFERENCES fiscal_year(id) ON DELETE RESTRICT,
    account_id      TEXT REFERENCES account(id) ON DELETE RESTRICT,
    cost_center_id  TEXT REFERENCES cost_center(id) ON DELETE RESTRICT,
    budget_amount   TEXT NOT NULL DEFAULT '0',  -- decimal(18,6)
    actual_amount   TEXT NOT NULL DEFAULT '0',  -- computed from GL
    variance        TEXT NOT NULL DEFAULT '0',  -- computed
    action_if_exceeded TEXT NOT NULL DEFAULT 'warn'
                    CHECK(action_if_exceeded IN ('warn','stop','ignore')),
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_budget_fiscal_year ON budget(fiscal_year_id);
CREATE INDEX IF NOT EXISTS idx_budget_account ON budget(account_id);
CREATE INDEX IF NOT EXISTS idx_budget_cost_center ON budget(cost_center_id);

CREATE TABLE IF NOT EXISTS naming_series (
    id              TEXT PRIMARY KEY,
    entity_type     TEXT NOT NULL,
    prefix          TEXT NOT NULL,
    current_value   INTEGER NOT NULL DEFAULT 0,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    UNIQUE(entity_type, prefix, company_id)
);
"""


# ---------------------------------------------------------------------------
# SKILL: erpclaw-journals
# Tables: journal_entry, journal_entry_line
# ---------------------------------------------------------------------------

JOURNALS_TABLES = """
-- =========================================================================
-- SKILL: erpclaw-journals (Bookkeeper)
-- =========================================================================

CREATE TABLE IF NOT EXISTS journal_entry (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    posting_date    TEXT NOT NULL,
    entry_type      TEXT NOT NULL DEFAULT 'journal'
                    CHECK(entry_type IN (
                        'journal','opening','closing','depreciation',
                        'write_off','exchange_rate_revaluation',
                        'inter_company','credit_note','debit_note'
                    )),
    total_debit     TEXT NOT NULL DEFAULT '0',
    total_credit    TEXT NOT NULL DEFAULT '0',
    currency        TEXT NOT NULL DEFAULT 'USD',
    exchange_rate   TEXT NOT NULL DEFAULT '1',
    remark          TEXT,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN ('draft','submitted','cancelled','amended')),
    amended_from    TEXT REFERENCES journal_entry(id) ON DELETE RESTRICT,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_journal_entry_status ON journal_entry(status);
CREATE INDEX IF NOT EXISTS idx_journal_entry_company ON journal_entry(company_id);
CREATE INDEX IF NOT EXISTS idx_journal_entry_posting_date ON journal_entry(posting_date);

CREATE TABLE IF NOT EXISTS journal_entry_line (
    id              TEXT PRIMARY KEY,
    journal_entry_id TEXT NOT NULL REFERENCES journal_entry(id) ON DELETE RESTRICT,
    account_id      TEXT NOT NULL REFERENCES account(id) ON DELETE RESTRICT,
    party_type      TEXT CHECK(party_type IN ('customer','supplier','employee')),
    party_id        TEXT,
    debit           TEXT NOT NULL DEFAULT '0',
    credit          TEXT NOT NULL DEFAULT '0',
    cost_center_id  TEXT REFERENCES cost_center(id) ON DELETE RESTRICT,
    project_id      TEXT,
    remark          TEXT
);

CREATE INDEX IF NOT EXISTS idx_jel_journal ON journal_entry_line(journal_entry_id);
CREATE INDEX IF NOT EXISTS idx_jel_account ON journal_entry_line(account_id);

CREATE TABLE IF NOT EXISTS recurring_journal_template (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    name            TEXT NOT NULL,
    frequency       TEXT NOT NULL DEFAULT 'monthly'
                    CHECK(frequency IN ('daily','weekly','monthly','quarterly','annual')),
    start_date      TEXT NOT NULL,
    end_date        TEXT,
    next_run_date   TEXT NOT NULL,
    last_generated_date TEXT,
    entry_type      TEXT NOT NULL DEFAULT 'journal'
                    CHECK(entry_type IN (
                        'journal','opening','closing','depreciation',
                        'write_off','exchange_rate_revaluation',
                        'inter_company','credit_note','debit_note'
                    )),
    lines           TEXT NOT NULL,
    auto_submit     INTEGER NOT NULL DEFAULT 0,
    remark          TEXT,
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK(status IN ('active','paused','completed')),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_rjt_company ON recurring_journal_template(company_id);
CREATE INDEX IF NOT EXISTS idx_rjt_status ON recurring_journal_template(status);
CREATE INDEX IF NOT EXISTS idx_rjt_next_run ON recurring_journal_template(next_run_date);
"""


# ---------------------------------------------------------------------------
# SKILL: erpclaw-payments
# Tables: payment_entry, payment_allocation, payment_deduction,
#         payment_ledger_entry
# ---------------------------------------------------------------------------

PAYMENTS_TABLES = """
-- =========================================================================
-- SKILL: erpclaw-payments (AR/AP Clerk)
-- =========================================================================

CREATE TABLE IF NOT EXISTS payment_entry (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    payment_type    TEXT NOT NULL CHECK(payment_type IN ('receive','pay','internal_transfer')),
    posting_date    TEXT NOT NULL,
    party_type      TEXT CHECK(party_type IN ('customer','supplier','employee')),
    party_id        TEXT,
    paid_from_account TEXT NOT NULL REFERENCES account(id) ON DELETE RESTRICT,
    paid_to_account TEXT NOT NULL REFERENCES account(id) ON DELETE RESTRICT,
    paid_amount     TEXT NOT NULL DEFAULT '0',
    received_amount TEXT NOT NULL DEFAULT '0',
    payment_currency TEXT NOT NULL DEFAULT 'USD',
    exchange_rate   TEXT NOT NULL DEFAULT '1',
    reference_number TEXT,
    reference_date  TEXT,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN ('draft','submitted','cancelled')),
    unallocated_amount TEXT NOT NULL DEFAULT '0',
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_payment_entry_status ON payment_entry(status);
CREATE INDEX IF NOT EXISTS idx_payment_entry_company ON payment_entry(company_id);
CREATE INDEX IF NOT EXISTS idx_payment_entry_party ON payment_entry(party_type, party_id);
CREATE INDEX IF NOT EXISTS idx_payment_entry_posting_date ON payment_entry(posting_date);

CREATE TABLE IF NOT EXISTS payment_allocation (
    id              TEXT PRIMARY KEY,
    payment_entry_id TEXT NOT NULL REFERENCES payment_entry(id) ON DELETE RESTRICT,
    voucher_type    TEXT NOT NULL CHECK(voucher_type IN (
                        'sales_invoice','purchase_invoice',
                        'credit_note','debit_note'
                    )),
    voucher_id      TEXT NOT NULL,
    allocated_amount TEXT NOT NULL DEFAULT '0',
    exchange_gain_loss TEXT NOT NULL DEFAULT '0',
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_payment_alloc_payment ON payment_allocation(payment_entry_id);
CREATE INDEX IF NOT EXISTS idx_payment_alloc_voucher ON payment_allocation(voucher_type, voucher_id);

CREATE TABLE IF NOT EXISTS payment_deduction (
    id              TEXT PRIMARY KEY,
    payment_entry_id TEXT NOT NULL REFERENCES payment_entry(id) ON DELETE RESTRICT,
    account_id      TEXT NOT NULL REFERENCES account(id) ON DELETE RESTRICT,
    amount          TEXT NOT NULL DEFAULT '0',
    type            TEXT NOT NULL CHECK(type IN ('tds','commission','early_payment_discount','other')),
    description     TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_payment_deduction_pe ON payment_deduction(payment_entry_id);

CREATE TABLE IF NOT EXISTS payment_ledger_entry (
    id              TEXT PRIMARY KEY,
    posting_date    TEXT NOT NULL,
    account_id      TEXT NOT NULL REFERENCES account(id) ON DELETE RESTRICT,
    party_type      TEXT NOT NULL CHECK(party_type IN ('customer','supplier','employee')),
    party_id        TEXT NOT NULL,
    voucher_type    TEXT NOT NULL,
    voucher_id      TEXT NOT NULL,
    against_voucher_type TEXT,
    against_voucher_id   TEXT,
    amount          TEXT NOT NULL DEFAULT '0',  -- positive = receivable/payable, negative = payment
    amount_in_account_currency TEXT NOT NULL DEFAULT '0',
    currency        TEXT NOT NULL DEFAULT 'USD',
    delinked        INTEGER NOT NULL DEFAULT 0 CHECK(delinked IN (0,1)),
    remarks         TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ple_party ON payment_ledger_entry(party_type, party_id);
CREATE INDEX IF NOT EXISTS idx_ple_voucher ON payment_ledger_entry(voucher_type, voucher_id);
CREATE INDEX IF NOT EXISTS idx_ple_against ON payment_ledger_entry(against_voucher_type, against_voucher_id);
CREATE INDEX IF NOT EXISTS idx_ple_account ON payment_ledger_entry(account_id);
CREATE INDEX IF NOT EXISTS idx_ple_posting_date ON payment_ledger_entry(posting_date);
"""


# ---------------------------------------------------------------------------
# SKILL: erpclaw-tax
# Tables: tax_template, tax_template_line, tax_category, tax_rule,
#         item_tax_template, tax_withholding_category,
#         tax_withholding_entry, tax_withholding_group
# ---------------------------------------------------------------------------

TAX_TABLES = """
-- =========================================================================
-- SKILL: erpclaw-tax (Tax Accountant)
-- =========================================================================

CREATE TABLE IF NOT EXISTS tax_category (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    description     TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tax_template (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    tax_type        TEXT NOT NULL CHECK(tax_type IN ('sales','purchase','both')),
    is_default      INTEGER NOT NULL DEFAULT 0 CHECK(is_default IN (0,1)),
    tax_category_id TEXT REFERENCES tax_category(id) ON DELETE RESTRICT,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, company_id)
);

CREATE INDEX IF NOT EXISTS idx_tax_template_company ON tax_template(company_id);
CREATE INDEX IF NOT EXISTS idx_tax_template_type ON tax_template(tax_type);

CREATE TABLE IF NOT EXISTS tax_template_line (
    id              TEXT PRIMARY KEY,
    tax_template_id TEXT NOT NULL REFERENCES tax_template(id) ON DELETE RESTRICT,
    tax_account_id  TEXT NOT NULL REFERENCES account(id) ON DELETE RESTRICT,
    rate            TEXT NOT NULL DEFAULT '0',  -- percentage
    charge_type     TEXT NOT NULL DEFAULT 'on_net_total'
                    CHECK(charge_type IN (
                        'actual','on_net_total','on_previous_row_amount',
                        'on_previous_row_total','on_item_quantity'
                    )),
    row_order       INTEGER NOT NULL DEFAULT 0,
    add_deduct      TEXT NOT NULL DEFAULT 'add' CHECK(add_deduct IN ('add','deduct')),
    included_in_print_rate INTEGER NOT NULL DEFAULT 0
                    CHECK(included_in_print_rate IN (0,1)),
    description     TEXT,
    dont_recompute_tax INTEGER NOT NULL DEFAULT 0 CHECK(dont_recompute_tax IN (0,1)),
    is_tax_withholding_account INTEGER NOT NULL DEFAULT 0
                    CHECK(is_tax_withholding_account IN (0,1))
);

CREATE INDEX IF NOT EXISTS idx_ttl_template ON tax_template_line(tax_template_id);

CREATE TABLE IF NOT EXISTS tax_rule (
    id              TEXT PRIMARY KEY,
    tax_template_id TEXT NOT NULL REFERENCES tax_template(id) ON DELETE RESTRICT,
    tax_type        TEXT NOT NULL CHECK(tax_type IN ('sales','purchase')),
    customer_id     TEXT,
    supplier_id     TEXT,
    customer_group  TEXT,
    supplier_group  TEXT,
    item_id         TEXT,
    item_group      TEXT,
    billing_state   TEXT,
    shipping_state  TEXT,
    tax_category_id TEXT REFERENCES tax_category(id) ON DELETE RESTRICT,
    priority        INTEGER NOT NULL DEFAULT 0,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tax_rule_company ON tax_rule(company_id);
CREATE INDEX IF NOT EXISTS idx_tax_rule_template ON tax_rule(tax_template_id);

CREATE TABLE IF NOT EXISTS item_tax_template (
    id              TEXT PRIMARY KEY,
    item_id         TEXT NOT NULL,
    tax_template_id TEXT NOT NULL REFERENCES tax_template(id) ON DELETE RESTRICT,
    tax_rate        TEXT,  -- override rate, nullable
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_item_tax_template_item ON item_tax_template(item_id);

CREATE TABLE IF NOT EXISTS tax_withholding_category (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    category_code   TEXT,         -- e.g. '1099-NEC', 'backup_withholding'
    single_threshold TEXT,        -- decimal: single transaction threshold
    cumulative_threshold TEXT,    -- decimal: cumulative per-year threshold
    tax_on_excess_amount INTEGER NOT NULL DEFAULT 0
                    CHECK(tax_on_excess_amount IN (0,1)),
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tax_withholding_group (
    id              TEXT PRIMARY KEY,
    category_id     TEXT NOT NULL REFERENCES tax_withholding_category(id) ON DELETE RESTRICT,
    group_name      TEXT NOT NULL,    -- e.g. 'TIN Provided', 'No TIN'
    rate            TEXT NOT NULL,    -- withholding percentage
    effective_from  TEXT NOT NULL,
    effective_to    TEXT,
    account_id      TEXT NOT NULL REFERENCES account(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_twg_category ON tax_withholding_group(category_id);

CREATE TABLE IF NOT EXISTS tax_withholding_entry (
    id              TEXT PRIMARY KEY,
    party_type      TEXT NOT NULL CHECK(party_type IN ('customer','supplier')),
    party_id        TEXT NOT NULL,
    category_id     TEXT NOT NULL REFERENCES tax_withholding_category(id) ON DELETE RESTRICT,
    fiscal_year     TEXT NOT NULL,
    taxable_amount  TEXT NOT NULL DEFAULT '0',
    withheld_amount TEXT NOT NULL DEFAULT '0',
    taxable_voucher_type TEXT,
    taxable_voucher_id   TEXT,
    withholding_voucher_type TEXT,
    withholding_voucher_id   TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_twe_party ON tax_withholding_entry(party_type, party_id);
CREATE INDEX IF NOT EXISTS idx_twe_fiscal ON tax_withholding_entry(fiscal_year);
CREATE INDEX IF NOT EXISTS idx_twe_category ON tax_withholding_entry(category_id);
"""

# ---------------------------------------------------------------------------
# SKILL: erpclaw-selling
# Tables: customer, quotation, quotation_item, sales_order, sales_order_item,
#         delivery_note, delivery_note_item, sales_invoice, sales_invoice_item,
#         price_list, item_price, pricing_rule, sales_partner, blanket_order,
#         blanket_order_item, recurring_invoice_template, recurring_invoice_template_item
# ---------------------------------------------------------------------------

SELLING_TABLES = """
-- =========================================================================
-- SKILL: erpclaw-selling (Sales Coordinator)
-- =========================================================================

CREATE TABLE IF NOT EXISTS customer (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    name            TEXT NOT NULL,
    customer_type   TEXT NOT NULL DEFAULT 'company'
                    CHECK(customer_type IN ('company','individual')),
    customer_group  TEXT,
    territory       TEXT,
    default_currency TEXT NOT NULL DEFAULT 'USD',
    default_price_list_id TEXT,
    payment_terms_id TEXT REFERENCES payment_terms(id) ON DELETE RESTRICT,
    credit_limit    TEXT,
    tax_id          TEXT,
    exempt_from_sales_tax INTEGER NOT NULL DEFAULT 0
                    CHECK(exempt_from_sales_tax IN (0,1)),
    tax_exemption_certificate TEXT,
    primary_address TEXT,
    primary_contact TEXT,
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK(status IN ('active','inactive','blocked')),
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_customer_status ON customer(status);
CREATE INDEX IF NOT EXISTS idx_customer_company ON customer(company_id);
CREATE INDEX IF NOT EXISTS idx_customer_group ON customer(customer_group);

CREATE TABLE IF NOT EXISTS price_list (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    currency        TEXT NOT NULL DEFAULT 'USD',
    selling         INTEGER NOT NULL DEFAULT 0 CHECK(selling IN (0,1)),
    buying          INTEGER NOT NULL DEFAULT 0 CHECK(buying IN (0,1)),
    enabled         INTEGER NOT NULL DEFAULT 1 CHECK(enabled IN (0,1)),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS item_price (
    id              TEXT PRIMARY KEY,
    item_id         TEXT NOT NULL,
    price_list_id   TEXT NOT NULL REFERENCES price_list(id) ON DELETE RESTRICT,
    rate            TEXT NOT NULL DEFAULT '0',
    min_qty         TEXT NOT NULL DEFAULT '0',
    valid_from      TEXT,
    valid_to        TEXT,
    currency        TEXT NOT NULL DEFAULT 'USD',
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_item_price_item ON item_price(item_id);
CREATE INDEX IF NOT EXISTS idx_item_price_list ON item_price(price_list_id);

CREATE TABLE IF NOT EXISTS pricing_rule (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    applies_to      TEXT NOT NULL CHECK(applies_to IN ('item','item_group','customer','customer_group')),
    entity_id       TEXT,
    discount_percentage TEXT,
    discount_amount TEXT,
    rate            TEXT,
    min_qty         TEXT,
    max_qty         TEXT,
    valid_from      TEXT,
    valid_to        TEXT,
    priority        INTEGER NOT NULL DEFAULT 0,
    active          INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1)),
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quotation (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    customer_id     TEXT NOT NULL REFERENCES customer(id) ON DELETE RESTRICT,
    quotation_date  TEXT NOT NULL,
    valid_until     TEXT,
    currency        TEXT NOT NULL DEFAULT 'USD',
    exchange_rate   TEXT NOT NULL DEFAULT '1',
    total_amount    TEXT NOT NULL DEFAULT '0',
    tax_amount      TEXT NOT NULL DEFAULT '0',
    grand_total     TEXT NOT NULL DEFAULT '0',
    tax_template_id TEXT REFERENCES tax_template(id) ON DELETE RESTRICT,
    payment_terms_id TEXT REFERENCES payment_terms(id) ON DELETE RESTRICT,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN ('draft','open','ordered','expired','cancelled')),
    converted_to    TEXT,
    terms_and_conditions TEXT,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_quotation_status ON quotation(status);
CREATE INDEX IF NOT EXISTS idx_quotation_company ON quotation(company_id);
CREATE INDEX IF NOT EXISTS idx_quotation_customer ON quotation(customer_id);

CREATE TABLE IF NOT EXISTS quotation_item (
    id              TEXT PRIMARY KEY,
    quotation_id    TEXT NOT NULL REFERENCES quotation(id) ON DELETE RESTRICT,
    item_id         TEXT NOT NULL,
    quantity        TEXT NOT NULL DEFAULT '0',
    uom             TEXT,
    rate            TEXT NOT NULL DEFAULT '0',
    amount          TEXT NOT NULL DEFAULT '0',
    discount_percentage TEXT NOT NULL DEFAULT '0',
    net_amount      TEXT NOT NULL DEFAULT '0',
    description     TEXT
);

CREATE INDEX IF NOT EXISTS idx_quotation_item_q ON quotation_item(quotation_id);

CREATE TABLE IF NOT EXISTS sales_order (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    customer_id     TEXT NOT NULL REFERENCES customer(id) ON DELETE RESTRICT,
    order_date      TEXT NOT NULL,
    delivery_date   TEXT,
    currency        TEXT NOT NULL DEFAULT 'USD',
    exchange_rate   TEXT NOT NULL DEFAULT '1',
    total_amount    TEXT NOT NULL DEFAULT '0',
    tax_amount      TEXT NOT NULL DEFAULT '0',
    grand_total     TEXT NOT NULL DEFAULT '0',
    tax_template_id TEXT REFERENCES tax_template(id) ON DELETE RESTRICT,
    payment_terms_id TEXT REFERENCES payment_terms(id) ON DELETE RESTRICT,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN (
                        'draft','confirmed','partially_delivered','fully_delivered',
                        'partially_invoiced','fully_invoiced','closed','cancelled'
                    )),
    per_delivered    TEXT NOT NULL DEFAULT '0',
    per_invoiced     TEXT NOT NULL DEFAULT '0',
    quotation_id    TEXT REFERENCES quotation(id) ON DELETE RESTRICT,
    amended_from    TEXT REFERENCES sales_order(id) ON DELETE RESTRICT,
    close_reason    TEXT,
    closed_by       TEXT,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sales_order_status ON sales_order(status);
CREATE INDEX IF NOT EXISTS idx_sales_order_company ON sales_order(company_id);
CREATE INDEX IF NOT EXISTS idx_sales_order_customer ON sales_order(customer_id);

CREATE TABLE IF NOT EXISTS sales_order_item (
    id              TEXT PRIMARY KEY,
    sales_order_id  TEXT NOT NULL REFERENCES sales_order(id) ON DELETE RESTRICT,
    item_id         TEXT NOT NULL,
    quantity        TEXT NOT NULL DEFAULT '0',
    delivered_qty   TEXT NOT NULL DEFAULT '0',
    invoiced_qty    TEXT NOT NULL DEFAULT '0',
    uom             TEXT,
    rate            TEXT NOT NULL DEFAULT '0',
    amount          TEXT NOT NULL DEFAULT '0',
    discount_percentage TEXT NOT NULL DEFAULT '0',
    net_amount      TEXT NOT NULL DEFAULT '0',
    warehouse_id    TEXT,
    delivery_note_id TEXT,
    is_drop_ship    INTEGER NOT NULL DEFAULT 0 CHECK(is_drop_ship IN (0,1))
);

CREATE INDEX IF NOT EXISTS idx_soi_order ON sales_order_item(sales_order_id);

CREATE TABLE IF NOT EXISTS delivery_note (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    customer_id     TEXT NOT NULL REFERENCES customer(id) ON DELETE RESTRICT,
    posting_date    TEXT NOT NULL,
    sales_order_id  TEXT REFERENCES sales_order(id) ON DELETE RESTRICT,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN ('draft','submitted','cancelled')),
    total_qty       TEXT NOT NULL DEFAULT '0',
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_delivery_note_status ON delivery_note(status);
CREATE INDEX IF NOT EXISTS idx_delivery_note_company ON delivery_note(company_id);

CREATE TABLE IF NOT EXISTS delivery_note_item (
    id              TEXT PRIMARY KEY,
    delivery_note_id TEXT NOT NULL REFERENCES delivery_note(id) ON DELETE RESTRICT,
    item_id         TEXT NOT NULL,
    quantity        TEXT NOT NULL DEFAULT '0',
    uom             TEXT,
    sales_order_item_id TEXT REFERENCES sales_order_item(id) ON DELETE RESTRICT,
    warehouse_id    TEXT,
    batch_id        TEXT,
    serial_numbers  TEXT,
    rate            TEXT NOT NULL DEFAULT '0',
    amount          TEXT NOT NULL DEFAULT '0'
);

CREATE INDEX IF NOT EXISTS idx_dni_note ON delivery_note_item(delivery_note_id);

CREATE TABLE IF NOT EXISTS sales_invoice (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    customer_id     TEXT NOT NULL REFERENCES customer(id) ON DELETE RESTRICT,
    posting_date    TEXT NOT NULL,
    due_date        TEXT,
    currency        TEXT NOT NULL DEFAULT 'USD',
    exchange_rate   TEXT NOT NULL DEFAULT '1',
    total_amount    TEXT NOT NULL DEFAULT '0',
    tax_amount      TEXT NOT NULL DEFAULT '0',
    grand_total     TEXT NOT NULL DEFAULT '0',
    outstanding_amount TEXT NOT NULL DEFAULT '0',
    rounding_adjustment TEXT NOT NULL DEFAULT '0',
    tax_template_id TEXT REFERENCES tax_template(id) ON DELETE RESTRICT,
    payment_terms_id TEXT REFERENCES payment_terms(id) ON DELETE RESTRICT,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN (
                        'draft','submitted','partially_paid','paid',
                        'overdue','cancelled'
                    )),
    sales_order_id  TEXT REFERENCES sales_order(id) ON DELETE RESTRICT,
    delivery_note_id TEXT REFERENCES delivery_note(id) ON DELETE RESTRICT,
    is_return       INTEGER NOT NULL DEFAULT 0 CHECK(is_return IN (0,1)),
    return_against  TEXT,
    update_stock    INTEGER NOT NULL DEFAULT 1 CHECK(update_stock IN (0,1)),
    amended_from    TEXT,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sales_invoice_status ON sales_invoice(status);
CREATE INDEX IF NOT EXISTS idx_sales_invoice_company ON sales_invoice(company_id);
CREATE INDEX IF NOT EXISTS idx_sales_invoice_customer ON sales_invoice(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_invoice_posting_date ON sales_invoice(posting_date);

CREATE TABLE IF NOT EXISTS sales_invoice_item (
    id              TEXT PRIMARY KEY,
    sales_invoice_id TEXT NOT NULL REFERENCES sales_invoice(id) ON DELETE RESTRICT,
    item_id         TEXT NOT NULL,
    quantity        TEXT NOT NULL DEFAULT '0',
    uom             TEXT,
    rate            TEXT NOT NULL DEFAULT '0',
    amount          TEXT NOT NULL DEFAULT '0',
    discount_percentage TEXT NOT NULL DEFAULT '0',
    net_amount      TEXT NOT NULL DEFAULT '0',
    sales_order_item_id TEXT,
    delivery_note_item_id TEXT,
    cost_center_id  TEXT REFERENCES cost_center(id) ON DELETE RESTRICT,
    project_id      TEXT
);

CREATE INDEX IF NOT EXISTS idx_sii_invoice ON sales_invoice_item(sales_invoice_id);

CREATE TABLE IF NOT EXISTS sales_partner (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    commission_rate TEXT NOT NULL DEFAULT '0',
    territory       TEXT,
    contact_info    TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS blanket_order (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    customer_id     TEXT,
    supplier_id     TEXT,
    blanket_order_type TEXT NOT NULL CHECK(blanket_order_type IN ('selling','buying')),
    valid_from      TEXT NOT NULL,
    valid_to        TEXT NOT NULL,
    total_qty       TEXT NOT NULL DEFAULT '0',
    ordered_qty     TEXT NOT NULL DEFAULT '0',
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN ('draft','active','closed','cancelled')),
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS blanket_order_item (
    id              TEXT PRIMARY KEY,
    blanket_order_id TEXT NOT NULL REFERENCES blanket_order(id) ON DELETE RESTRICT,
    item_id         TEXT NOT NULL,
    quantity        TEXT NOT NULL DEFAULT '0',
    ordered_qty     TEXT NOT NULL DEFAULT '0',
    uom             TEXT,
    rate            TEXT NOT NULL DEFAULT '0',
    amount          TEXT NOT NULL DEFAULT '0'
);

CREATE INDEX IF NOT EXISTS idx_boi_order ON blanket_order_item(blanket_order_id);

CREATE TABLE IF NOT EXISTS recurring_invoice_template (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    customer_id     TEXT NOT NULL REFERENCES customer(id) ON DELETE RESTRICT,
    frequency       TEXT NOT NULL CHECK(frequency IN ('weekly','monthly','quarterly','semi_annually','annually')),
    start_date      TEXT NOT NULL,
    end_date        TEXT,
    next_invoice_date TEXT NOT NULL,
    last_invoice_date TEXT,
    tax_template_id TEXT REFERENCES tax_template(id) ON DELETE RESTRICT,
    payment_terms_id TEXT REFERENCES payment_terms(id) ON DELETE RESTRICT,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN ('draft','active','paused','completed','cancelled')),
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recurring_invoice_template_item (
    id              TEXT PRIMARY KEY,
    template_id     TEXT NOT NULL REFERENCES recurring_invoice_template(id) ON DELETE RESTRICT,
    item_id         TEXT NOT NULL,
    quantity        TEXT NOT NULL DEFAULT '0',
    uom             TEXT,
    rate            TEXT NOT NULL DEFAULT '0',
    amount          TEXT NOT NULL DEFAULT '0'
);

CREATE INDEX IF NOT EXISTS idx_rit_customer ON recurring_invoice_template(customer_id);
CREATE INDEX IF NOT EXISTS idx_rit_status ON recurring_invoice_template(status);
CREATE INDEX IF NOT EXISTS idx_rit_next_date ON recurring_invoice_template(next_invoice_date);
CREATE INDEX IF NOT EXISTS idx_riti_template ON recurring_invoice_template_item(template_id);

-- =========================================================================
-- Packing Slip (Sprint 7, Feature #16)
-- =========================================================================

CREATE TABLE IF NOT EXISTS packing_slip (
    id              TEXT PRIMARY KEY,
    delivery_note_id TEXT NOT NULL REFERENCES delivery_note(id) ON DELETE RESTRICT,
    posting_date    TEXT NOT NULL,
    notes           TEXT,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_packing_slip_dn ON packing_slip(delivery_note_id);
CREATE INDEX IF NOT EXISTS idx_packing_slip_company ON packing_slip(company_id);

CREATE TABLE IF NOT EXISTS packing_slip_item (
    id              TEXT PRIMARY KEY,
    packing_slip_id TEXT NOT NULL REFERENCES packing_slip(id) ON DELETE RESTRICT,
    item_id         TEXT NOT NULL,
    delivery_note_item_id TEXT NOT NULL REFERENCES delivery_note_item(id) ON DELETE RESTRICT,
    qty_packed      TEXT NOT NULL DEFAULT '0',
    uom             TEXT,
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS idx_packing_slip_item_slip ON packing_slip_item(packing_slip_id);
"""


# ---------------------------------------------------------------------------
# SKILL: erpclaw-buying
# Tables: supplier, material_request, material_request_item,
#         request_for_quotation, rfq_supplier, rfq_item,
#         supplier_quotation, supplier_quotation_item,
#         purchase_order, purchase_order_item,
#         purchase_receipt, purchase_receipt_item,
#         purchase_invoice, purchase_invoice_item,
#         landed_cost_voucher, landed_cost_item, landed_cost_charge,
#         supplier_score, recurring_bill_template, recurring_bill_template_item
# ---------------------------------------------------------------------------

BUYING_TABLES = """
-- =========================================================================
-- SKILL: erpclaw-buying (Purchasing Agent)
-- =========================================================================

CREATE TABLE IF NOT EXISTS supplier (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    name            TEXT NOT NULL,
    supplier_group  TEXT,
    supplier_type   TEXT NOT NULL DEFAULT 'company'
                    CHECK(supplier_type IN ('company','individual')),
    default_currency TEXT NOT NULL DEFAULT 'USD',
    payment_terms_id TEXT REFERENCES payment_terms(id) ON DELETE RESTRICT,
    tax_id          TEXT,
    is_1099_vendor  INTEGER NOT NULL DEFAULT 0 CHECK(is_1099_vendor IN (0,1)),
    primary_address TEXT,
    primary_contact TEXT,
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK(status IN ('active','inactive','blocked')),
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_supplier_status ON supplier(status);
CREATE INDEX IF NOT EXISTS idx_supplier_company ON supplier(company_id);

CREATE TABLE IF NOT EXISTS material_request (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    request_type    TEXT NOT NULL DEFAULT 'purchase'
                    CHECK(request_type IN ('purchase','material_transfer','material_issue','manufacture')),
    requested_by    TEXT,
    required_date   TEXT,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN ('draft','submitted','partially_ordered','ordered','cancelled')),
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_material_request_status ON material_request(status);

CREATE TABLE IF NOT EXISTS material_request_item (
    id              TEXT PRIMARY KEY,
    material_request_id TEXT NOT NULL REFERENCES material_request(id) ON DELETE RESTRICT,
    item_id         TEXT NOT NULL,
    quantity        TEXT NOT NULL DEFAULT '0',
    uom             TEXT,
    warehouse_id    TEXT,
    required_date   TEXT,
    ordered_qty     TEXT NOT NULL DEFAULT '0'
);

CREATE INDEX IF NOT EXISTS idx_mri_request ON material_request_item(material_request_id);

CREATE TABLE IF NOT EXISTS request_for_quotation (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    rfq_date        TEXT NOT NULL,
    required_date   TEXT,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN ('draft','submitted','quotation_received','cancelled')),
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rfq_supplier (
    id              TEXT PRIMARY KEY,
    rfq_id          TEXT NOT NULL REFERENCES request_for_quotation(id) ON DELETE RESTRICT,
    supplier_id     TEXT NOT NULL REFERENCES supplier(id) ON DELETE RESTRICT,
    sent_date       TEXT,
    response_date   TEXT,
    supplier_quotation_id TEXT
);

CREATE INDEX IF NOT EXISTS idx_rfq_supplier_rfq ON rfq_supplier(rfq_id);

CREATE TABLE IF NOT EXISTS rfq_item (
    id              TEXT PRIMARY KEY,
    rfq_id          TEXT NOT NULL REFERENCES request_for_quotation(id) ON DELETE RESTRICT,
    item_id         TEXT NOT NULL,
    quantity        TEXT NOT NULL DEFAULT '0',
    uom             TEXT,
    required_date   TEXT
);

CREATE INDEX IF NOT EXISTS idx_rfq_item_rfq ON rfq_item(rfq_id);

CREATE TABLE IF NOT EXISTS supplier_quotation (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    supplier_id     TEXT NOT NULL REFERENCES supplier(id) ON DELETE RESTRICT,
    quotation_date  TEXT NOT NULL,
    valid_until     TEXT,
    currency        TEXT NOT NULL DEFAULT 'USD',
    exchange_rate   TEXT NOT NULL DEFAULT '1',
    total_amount    TEXT NOT NULL DEFAULT '0',
    grand_total     TEXT NOT NULL DEFAULT '0',
    rfq_id          TEXT REFERENCES request_for_quotation(id) ON DELETE RESTRICT,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN ('draft','submitted','ordered','expired','cancelled')),
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_supplier_quotation_supplier ON supplier_quotation(supplier_id);
CREATE INDEX IF NOT EXISTS idx_supplier_quotation_status ON supplier_quotation(status);

CREATE TABLE IF NOT EXISTS supplier_quotation_item (
    id              TEXT PRIMARY KEY,
    supplier_quotation_id TEXT NOT NULL REFERENCES supplier_quotation(id) ON DELETE RESTRICT,
    item_id         TEXT NOT NULL,
    quantity        TEXT NOT NULL DEFAULT '0',
    uom             TEXT,
    rate            TEXT NOT NULL DEFAULT '0',
    amount          TEXT NOT NULL DEFAULT '0',
    lead_time_days  INTEGER
);

CREATE INDEX IF NOT EXISTS idx_sqi_quotation ON supplier_quotation_item(supplier_quotation_id);

CREATE TABLE IF NOT EXISTS purchase_order (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    supplier_id     TEXT NOT NULL REFERENCES supplier(id) ON DELETE RESTRICT,
    order_date      TEXT NOT NULL,
    required_date   TEXT,
    currency        TEXT NOT NULL DEFAULT 'USD',
    exchange_rate   TEXT NOT NULL DEFAULT '1',
    total_amount    TEXT NOT NULL DEFAULT '0',
    tax_amount      TEXT NOT NULL DEFAULT '0',
    grand_total     TEXT NOT NULL DEFAULT '0',
    tax_template_id TEXT REFERENCES tax_template(id) ON DELETE RESTRICT,
    payment_terms_id TEXT REFERENCES payment_terms(id) ON DELETE RESTRICT,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN (
                        'draft','confirmed','partially_received','fully_received',
                        'partially_invoiced','fully_invoiced','closed','cancelled'
                    )),
    per_received    TEXT NOT NULL DEFAULT '0',
    per_invoiced    TEXT NOT NULL DEFAULT '0',
    supplier_quotation_id TEXT REFERENCES supplier_quotation(id) ON DELETE RESTRICT,
    close_reason    TEXT,
    closed_by       TEXT,
    delivery_address TEXT,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_purchase_order_status ON purchase_order(status);
CREATE INDEX IF NOT EXISTS idx_purchase_order_company ON purchase_order(company_id);
CREATE INDEX IF NOT EXISTS idx_purchase_order_supplier ON purchase_order(supplier_id);

CREATE TABLE IF NOT EXISTS purchase_order_item (
    id              TEXT PRIMARY KEY,
    purchase_order_id TEXT NOT NULL REFERENCES purchase_order(id) ON DELETE RESTRICT,
    item_id         TEXT NOT NULL,
    quantity        TEXT NOT NULL DEFAULT '0',
    received_qty    TEXT NOT NULL DEFAULT '0',
    invoiced_qty    TEXT NOT NULL DEFAULT '0',
    uom             TEXT,
    rate            TEXT NOT NULL DEFAULT '0',
    amount          TEXT NOT NULL DEFAULT '0',
    discount_percentage TEXT NOT NULL DEFAULT '0',
    net_amount      TEXT NOT NULL DEFAULT '0',
    warehouse_id    TEXT,
    required_date   TEXT,
    stock_uom       TEXT,
    conversion_factor TEXT NOT NULL DEFAULT '1',
    stock_qty       TEXT NOT NULL DEFAULT '0'
);

CREATE INDEX IF NOT EXISTS idx_poi_order ON purchase_order_item(purchase_order_id);

CREATE TABLE IF NOT EXISTS purchase_receipt (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    supplier_id     TEXT NOT NULL REFERENCES supplier(id) ON DELETE RESTRICT,
    posting_date    TEXT NOT NULL,
    purchase_order_id TEXT REFERENCES purchase_order(id) ON DELETE RESTRICT,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN ('draft','submitted','cancelled')),
    total_qty       TEXT NOT NULL DEFAULT '0',
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_purchase_receipt_status ON purchase_receipt(status);
CREATE INDEX IF NOT EXISTS idx_purchase_receipt_company ON purchase_receipt(company_id);

CREATE TABLE IF NOT EXISTS purchase_receipt_item (
    id              TEXT PRIMARY KEY,
    purchase_receipt_id TEXT NOT NULL REFERENCES purchase_receipt(id) ON DELETE RESTRICT,
    item_id         TEXT NOT NULL,
    quantity        TEXT NOT NULL DEFAULT '0',
    uom             TEXT,
    purchase_order_item_id TEXT REFERENCES purchase_order_item(id) ON DELETE RESTRICT,
    warehouse_id    TEXT,
    batch_id        TEXT,
    serial_numbers  TEXT,
    rate            TEXT NOT NULL DEFAULT '0',
    amount          TEXT NOT NULL DEFAULT '0',
    rejected_qty    TEXT NOT NULL DEFAULT '0',
    rejected_warehouse_id TEXT
);

CREATE INDEX IF NOT EXISTS idx_pri_receipt ON purchase_receipt_item(purchase_receipt_id);

CREATE TABLE IF NOT EXISTS purchase_invoice (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    supplier_id     TEXT NOT NULL REFERENCES supplier(id) ON DELETE RESTRICT,
    posting_date    TEXT NOT NULL,
    due_date        TEXT,
    currency        TEXT NOT NULL DEFAULT 'USD',
    exchange_rate   TEXT NOT NULL DEFAULT '1',
    total_amount    TEXT NOT NULL DEFAULT '0',
    tax_amount      TEXT NOT NULL DEFAULT '0',
    grand_total     TEXT NOT NULL DEFAULT '0',
    outstanding_amount TEXT NOT NULL DEFAULT '0',
    rounding_adjustment TEXT NOT NULL DEFAULT '0',
    tax_template_id TEXT REFERENCES tax_template(id) ON DELETE RESTRICT,
    payment_terms_id TEXT REFERENCES payment_terms(id) ON DELETE RESTRICT,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN (
                        'draft','submitted','partially_paid','paid',
                        'overdue','cancelled'
                    )),
    purchase_order_id TEXT REFERENCES purchase_order(id) ON DELETE RESTRICT,
    purchase_receipt_id TEXT REFERENCES purchase_receipt(id) ON DELETE RESTRICT,
    is_return       INTEGER NOT NULL DEFAULT 0 CHECK(is_return IN (0,1)),
    return_against  TEXT,
    update_stock    INTEGER NOT NULL DEFAULT 1 CHECK(update_stock IN (0,1)),
    amended_from    TEXT,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_purchase_invoice_status ON purchase_invoice(status);
CREATE INDEX IF NOT EXISTS idx_purchase_invoice_company ON purchase_invoice(company_id);
CREATE INDEX IF NOT EXISTS idx_purchase_invoice_supplier ON purchase_invoice(supplier_id);
CREATE INDEX IF NOT EXISTS idx_purchase_invoice_posting_date ON purchase_invoice(posting_date);

CREATE TABLE IF NOT EXISTS purchase_invoice_item (
    id              TEXT PRIMARY KEY,
    purchase_invoice_id TEXT NOT NULL REFERENCES purchase_invoice(id) ON DELETE RESTRICT,
    item_id         TEXT NOT NULL,
    quantity        TEXT NOT NULL DEFAULT '0',
    uom             TEXT,
    rate            TEXT NOT NULL DEFAULT '0',
    amount          TEXT NOT NULL DEFAULT '0',
    expense_account_id TEXT REFERENCES account(id) ON DELETE RESTRICT,
    cost_center_id  TEXT REFERENCES cost_center(id) ON DELETE RESTRICT,
    project_id      TEXT,
    purchase_order_item_id TEXT,
    purchase_receipt_item_id TEXT
);

CREATE INDEX IF NOT EXISTS idx_pii_invoice ON purchase_invoice_item(purchase_invoice_id);

CREATE TABLE IF NOT EXISTS landed_cost_voucher (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    posting_date    TEXT NOT NULL,
    total_landed_cost TEXT NOT NULL DEFAULT '0',
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN ('draft','submitted','cancelled')),
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS landed_cost_item (
    id              TEXT PRIMARY KEY,
    landed_cost_voucher_id TEXT NOT NULL REFERENCES landed_cost_voucher(id) ON DELETE RESTRICT,
    purchase_receipt_id TEXT REFERENCES purchase_receipt(id) ON DELETE RESTRICT,
    purchase_receipt_item_id TEXT,
    applicable_charges TEXT NOT NULL DEFAULT '0',
    original_rate   TEXT NOT NULL DEFAULT '0',
    final_rate      TEXT NOT NULL DEFAULT '0'
);

CREATE INDEX IF NOT EXISTS idx_lci_voucher ON landed_cost_item(landed_cost_voucher_id);

CREATE TABLE IF NOT EXISTS landed_cost_charge (
    id              TEXT PRIMARY KEY,
    landed_cost_voucher_id TEXT NOT NULL REFERENCES landed_cost_voucher(id) ON DELETE RESTRICT,
    description     TEXT NOT NULL,
    amount          TEXT NOT NULL DEFAULT '0',
    expense_account_id TEXT REFERENCES account(id) ON DELETE RESTRICT,
    allocation_method TEXT NOT NULL DEFAULT 'by_amount'
                    CHECK(allocation_method IN ('by_qty','by_amount','by_weight'))
);

CREATE INDEX IF NOT EXISTS idx_lcc_voucher ON landed_cost_charge(landed_cost_voucher_id);

CREATE TABLE IF NOT EXISTS supplier_score (
    id              TEXT PRIMARY KEY,
    supplier_id     TEXT NOT NULL REFERENCES supplier(id) ON DELETE RESTRICT,
    score_date      TEXT NOT NULL,
    overall_score   TEXT NOT NULL DEFAULT '0',
    delivery_score  TEXT NOT NULL DEFAULT '0',
    quality_score   TEXT NOT NULL DEFAULT '0',
    price_score     TEXT NOT NULL DEFAULT '0',
    responsiveness_score TEXT NOT NULL DEFAULT '0',
    factors         TEXT,
    auto_computed   INTEGER NOT NULL DEFAULT 1 CHECK(auto_computed IN (0,1)),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_supplier_score_supplier ON supplier_score(supplier_id);

CREATE TABLE IF NOT EXISTS recurring_bill_template (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    supplier_id     TEXT NOT NULL REFERENCES supplier(id) ON DELETE RESTRICT,
    frequency       TEXT NOT NULL CHECK(frequency IN ('weekly','monthly','quarterly','semi_annually','annually')),
    start_date      TEXT NOT NULL,
    end_date        TEXT,
    next_bill_date  TEXT NOT NULL,
    last_bill_date  TEXT,
    tax_template_id TEXT REFERENCES tax_template(id) ON DELETE RESTRICT,
    auto_submit     INTEGER NOT NULL DEFAULT 0 CHECK(auto_submit IN (0,1)),
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN ('draft','active','paused','completed','cancelled')),
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recurring_bill_template_item (
    id              TEXT PRIMARY KEY,
    template_id     TEXT NOT NULL REFERENCES recurring_bill_template(id) ON DELETE RESTRICT,
    item_id         TEXT NOT NULL,
    quantity        TEXT NOT NULL DEFAULT '0',
    uom             TEXT,
    rate            TEXT NOT NULL DEFAULT '0',
    amount          TEXT NOT NULL DEFAULT '0'
);

CREATE INDEX IF NOT EXISTS idx_rbt_supplier ON recurring_bill_template(supplier_id);
CREATE INDEX IF NOT EXISTS idx_rbt_status ON recurring_bill_template(status);
CREATE INDEX IF NOT EXISTS idx_rbt_next_date ON recurring_bill_template(next_bill_date);
CREATE INDEX IF NOT EXISTS idx_rbti_template ON recurring_bill_template_item(template_id);
"""


# ---------------------------------------------------------------------------
# SKILL: erpclaw-inventory
# Tables: item, item_group, item_attribute, warehouse, stock_entry,
#         stock_entry_item, stock_ledger_entry, batch, serial_number,
#         stock_reconciliation, stock_reconciliation_item,
#         product_bundle, product_bundle_item
# ---------------------------------------------------------------------------

INVENTORY_TABLES = """
-- =========================================================================
-- SKILL: erpclaw-inventory (Inventory Manager)
-- =========================================================================

CREATE TABLE IF NOT EXISTS item_group (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    company_id      TEXT REFERENCES company(id),
    parent_id       TEXT REFERENCES item_group(id) ON DELETE RESTRICT,
    is_group        INTEGER NOT NULL DEFAULT 0 CHECK(is_group IN (0,1)),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, company_id)
);

CREATE TABLE IF NOT EXISTS item (
    id              TEXT PRIMARY KEY,
    item_code       TEXT NOT NULL UNIQUE,
    item_name       TEXT NOT NULL,
    item_group_id   TEXT REFERENCES item_group(id) ON DELETE RESTRICT,
    item_type       TEXT NOT NULL DEFAULT 'stock'
                    CHECK(item_type IN ('stock','non_stock','service')),
    stock_uom       TEXT,
    description     TEXT,
    is_purchase_item INTEGER NOT NULL DEFAULT 1 CHECK(is_purchase_item IN (0,1)),
    is_sales_item   INTEGER NOT NULL DEFAULT 1 CHECK(is_sales_item IN (0,1)),
    is_stock_item   INTEGER NOT NULL DEFAULT 1 CHECK(is_stock_item IN (0,1)),
    valuation_method TEXT NOT NULL DEFAULT 'moving_average'
                    CHECK(valuation_method IN ('moving_average','fifo')),
    default_warehouse_id TEXT,
    reorder_level   TEXT,
    reorder_qty     TEXT,
    safety_stock    TEXT,
    lead_time_days  INTEGER,
    shelf_life_days INTEGER,
    has_variants    INTEGER NOT NULL DEFAULT 0 CHECK(has_variants IN (0,1)),
    variant_of      TEXT REFERENCES item(id) ON DELETE RESTRICT,
    has_batch       INTEGER NOT NULL DEFAULT 0 CHECK(has_batch IN (0,1)),
    has_serial      INTEGER NOT NULL DEFAULT 0 CHECK(has_serial IN (0,1)),
    barcode         TEXT,
    weight          TEXT,
    weight_uom      TEXT,
    standard_rate   TEXT NOT NULL DEFAULT '0',
    last_purchase_rate TEXT NOT NULL DEFAULT '0',
    default_procurement_type TEXT NOT NULL DEFAULT 'purchase'
                    CHECK(default_procurement_type IN ('purchase','manufacture','both')),
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK(status IN ('active','disabled')),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_item_code ON item(item_code);
CREATE INDEX IF NOT EXISTS idx_item_group ON item(item_group_id);
CREATE INDEX IF NOT EXISTS idx_item_type ON item(item_type);
CREATE INDEX IF NOT EXISTS idx_item_status ON item(status);

CREATE TABLE IF NOT EXISTS item_attribute (
    id              TEXT PRIMARY KEY,
    item_id         TEXT NOT NULL REFERENCES item(id) ON DELETE RESTRICT,
    attribute_name  TEXT NOT NULL,
    attribute_values TEXT,  -- JSON array
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_item_attribute_item ON item_attribute(item_id);

CREATE TABLE IF NOT EXISTS warehouse (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    parent_id       TEXT REFERENCES warehouse(id) ON DELETE RESTRICT,
    warehouse_type  TEXT NOT NULL DEFAULT 'stores'
                    CHECK(warehouse_type IN ('stores','production','transit','rejected')),
    address         TEXT,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    account_id      TEXT REFERENCES account(id) ON DELETE RESTRICT,
    is_group        INTEGER NOT NULL DEFAULT 0 CHECK(is_group IN (0,1)),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_warehouse_company ON warehouse(company_id);
CREATE INDEX IF NOT EXISTS idx_warehouse_type ON warehouse(warehouse_type);

CREATE TABLE IF NOT EXISTS stock_entry (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    stock_entry_type TEXT NOT NULL CHECK(stock_entry_type IN (
                        'material_receipt','material_issue','material_transfer',
                        'manufacture','repack','send_to_subcontractor',
                        'material_consumption'
                    )),
    posting_date    TEXT NOT NULL,
    posting_time    TEXT,
    from_warehouse_id TEXT REFERENCES warehouse(id) ON DELETE RESTRICT,
    to_warehouse_id TEXT REFERENCES warehouse(id) ON DELETE RESTRICT,
    total_incoming_value TEXT NOT NULL DEFAULT '0',
    total_outgoing_value TEXT NOT NULL DEFAULT '0',
    value_difference TEXT NOT NULL DEFAULT '0',
    purpose_reference_type TEXT,
    purpose_reference_id TEXT,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN ('draft','submitted','cancelled')),
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stock_entry_status ON stock_entry(status);
CREATE INDEX IF NOT EXISTS idx_stock_entry_company ON stock_entry(company_id);
CREATE INDEX IF NOT EXISTS idx_stock_entry_type ON stock_entry(stock_entry_type);

CREATE TABLE IF NOT EXISTS stock_entry_item (
    id              TEXT PRIMARY KEY,
    stock_entry_id  TEXT NOT NULL REFERENCES stock_entry(id) ON DELETE RESTRICT,
    item_id         TEXT NOT NULL REFERENCES item(id) ON DELETE RESTRICT,
    quantity        TEXT NOT NULL DEFAULT '0',
    uom             TEXT,
    from_warehouse_id TEXT REFERENCES warehouse(id) ON DELETE RESTRICT,
    to_warehouse_id TEXT REFERENCES warehouse(id) ON DELETE RESTRICT,
    valuation_rate  TEXT NOT NULL DEFAULT '0',
    amount          TEXT NOT NULL DEFAULT '0',
    batch_id        TEXT,
    serial_numbers  TEXT,
    cost_center_id  TEXT REFERENCES cost_center(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_sei_entry ON stock_entry_item(stock_entry_id);

CREATE TABLE IF NOT EXISTS stock_ledger_entry (
    id              TEXT PRIMARY KEY,
    posting_date    TEXT NOT NULL,
    posting_time    TEXT,
    item_id         TEXT NOT NULL REFERENCES item(id) ON DELETE RESTRICT,
    warehouse_id    TEXT NOT NULL REFERENCES warehouse(id) ON DELETE RESTRICT,
    actual_qty      TEXT NOT NULL DEFAULT '0',
    qty_after_transaction TEXT NOT NULL DEFAULT '0',
    valuation_rate  TEXT NOT NULL DEFAULT '0',
    stock_value     TEXT NOT NULL DEFAULT '0',
    stock_value_difference TEXT NOT NULL DEFAULT '0',
    voucher_type    TEXT NOT NULL CHECK(voucher_type IN (
                        'stock_entry','purchase_receipt','delivery_note',
                        'stock_reconciliation','work_order',
                        'sales_invoice','credit_note','purchase_invoice','debit_note',
                        'stock_revaluation'
                    )),
    voucher_id      TEXT NOT NULL,
    batch_id        TEXT,
    serial_number   TEXT,
    incoming_rate   TEXT NOT NULL DEFAULT '0',
    is_cancelled    INTEGER NOT NULL DEFAULT 0 CHECK(is_cancelled IN (0,1)),
    fiscal_year     TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
    -- NOTE: stock_ledger_entry is immutable — no updated_at column
);

CREATE INDEX IF NOT EXISTS idx_sle_item_warehouse ON stock_ledger_entry(item_id, warehouse_id);
CREATE INDEX IF NOT EXISTS idx_sle_voucher ON stock_ledger_entry(voucher_type, voucher_id);
CREATE INDEX IF NOT EXISTS idx_sle_posting_date ON stock_ledger_entry(posting_date);
CREATE INDEX IF NOT EXISTS idx_sle_item ON stock_ledger_entry(item_id);
CREATE INDEX IF NOT EXISTS idx_sle_is_cancelled ON stock_ledger_entry(is_cancelled);

-- FIFO valuation layers: each incoming stock transaction creates a layer.
-- Outgoing transactions consume layers oldest-first (by posting_date, created_at).
-- remaining_qty tracks how much of each layer is still unconsumed.
CREATE TABLE IF NOT EXISTS stock_fifo_layer (
    id                  TEXT PRIMARY KEY,
    item_id             TEXT NOT NULL REFERENCES item(id) ON DELETE RESTRICT,
    warehouse_id        TEXT NOT NULL REFERENCES warehouse(id) ON DELETE RESTRICT,
    posting_date        TEXT NOT NULL,
    qty                 TEXT NOT NULL DEFAULT '0',
    rate                TEXT NOT NULL DEFAULT '0',
    remaining_qty       TEXT NOT NULL DEFAULT '0',
    source_voucher_type TEXT NOT NULL,
    source_voucher_id   TEXT NOT NULL,
    created_at          TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fifo_item_warehouse ON stock_fifo_layer(item_id, warehouse_id);
CREATE INDEX IF NOT EXISTS idx_fifo_remaining ON stock_fifo_layer(item_id, warehouse_id, remaining_qty);
CREATE INDEX IF NOT EXISTS idx_fifo_date ON stock_fifo_layer(posting_date, created_at);

CREATE TABLE IF NOT EXISTS batch (
    id              TEXT PRIMARY KEY,
    batch_name      TEXT NOT NULL UNIQUE,
    item_id         TEXT NOT NULL REFERENCES item(id) ON DELETE RESTRICT,
    manufacturing_date TEXT,
    expiry_date     TEXT,
    supplier_id     TEXT,
    stock_uom       TEXT,
    reference_doctype TEXT,
    reference_id    TEXT,
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK(status IN ('active','expired')),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_batch_item ON batch(item_id);

CREATE TABLE IF NOT EXISTS serial_number (
    id              TEXT PRIMARY KEY,
    serial_no       TEXT NOT NULL UNIQUE,
    item_id         TEXT NOT NULL REFERENCES item(id) ON DELETE RESTRICT,
    batch_id        TEXT REFERENCES batch(id) ON DELETE RESTRICT,
    warehouse_id    TEXT REFERENCES warehouse(id) ON DELETE RESTRICT,
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK(status IN ('active','delivered','returned','scrapped')),
    purchase_document_type TEXT,
    purchase_document_id TEXT,
    delivery_document_type TEXT,
    delivery_document_id TEXT,
    supplier_id     TEXT,
    customer_id     TEXT,
    warranty_expiry_date TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_serial_item ON serial_number(item_id);
CREATE INDEX IF NOT EXISTS idx_serial_warehouse ON serial_number(warehouse_id);
CREATE INDEX IF NOT EXISTS idx_serial_status ON serial_number(status);

CREATE TABLE IF NOT EXISTS stock_reconciliation (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    posting_date    TEXT NOT NULL,
    purpose         TEXT NOT NULL DEFAULT 'stock_reconciliation'
                    CHECK(purpose IN ('stock_reconciliation','opening_stock')),
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN ('draft','submitted','cancelled')),
    difference_amount TEXT NOT NULL DEFAULT '0',
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stock_reconciliation_item (
    id              TEXT PRIMARY KEY,
    stock_reconciliation_id TEXT NOT NULL REFERENCES stock_reconciliation(id) ON DELETE RESTRICT,
    item_id         TEXT NOT NULL REFERENCES item(id) ON DELETE RESTRICT,
    warehouse_id    TEXT NOT NULL REFERENCES warehouse(id) ON DELETE RESTRICT,
    current_qty     TEXT NOT NULL DEFAULT '0',
    current_valuation_rate TEXT NOT NULL DEFAULT '0',
    qty             TEXT NOT NULL DEFAULT '0',
    valuation_rate  TEXT NOT NULL DEFAULT '0',
    quantity_difference TEXT NOT NULL DEFAULT '0',
    amount_difference TEXT NOT NULL DEFAULT '0',
    batch_id        TEXT,
    serial_no       TEXT
);

CREATE INDEX IF NOT EXISTS idx_sri_recon ON stock_reconciliation_item(stock_reconciliation_id);

CREATE TABLE IF NOT EXISTS product_bundle (
    id              TEXT PRIMARY KEY,
    parent_item_id  TEXT NOT NULL REFERENCES item(id) ON DELETE RESTRICT,
    description     TEXT,
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK(status IN ('active','disabled')),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_bundle_item (
    id              TEXT PRIMARY KEY,
    product_bundle_id TEXT NOT NULL REFERENCES product_bundle(id) ON DELETE RESTRICT,
    item_id         TEXT NOT NULL REFERENCES item(id) ON DELETE RESTRICT,
    quantity        TEXT NOT NULL DEFAULT '0',
    uom             TEXT
);

CREATE INDEX IF NOT EXISTS idx_pbi_bundle ON product_bundle_item(product_bundle_id);

CREATE TABLE IF NOT EXISTS item_supplier (
    id              TEXT PRIMARY KEY,
    item_id         TEXT NOT NULL REFERENCES item(id) ON DELETE RESTRICT,
    supplier_id     TEXT NOT NULL REFERENCES supplier(id) ON DELETE RESTRICT,
    min_order_qty   TEXT NOT NULL DEFAULT '0',
    lead_time_days  INTEGER,
    priority        INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(item_id, supplier_id)
);

CREATE INDEX IF NOT EXISTS idx_item_supplier_item ON item_supplier(item_id);
CREATE INDEX IF NOT EXISTS idx_item_supplier_supplier ON item_supplier(supplier_id);
"""


# ---------------------------------------------------------------------------
# SKILL: erpclaw-billing
# Tables: meter, meter_reading, rate_plan, rate_tier,
#         billing_period, billing_adjustment, prepaid_credit_balance
# ---------------------------------------------------------------------------

BILLING_TABLES = """
-- =========================================================================
-- SKILL: erpclaw-billing (Billing Analyst)
-- =========================================================================

CREATE TABLE IF NOT EXISTS meter (
    id              TEXT PRIMARY KEY,
    meter_number    TEXT NOT NULL UNIQUE,
    customer_id     TEXT NOT NULL REFERENCES customer(id) ON DELETE RESTRICT,
    service_type    TEXT NOT NULL CHECK(service_type IN (
                        'electricity','water','gas','telecom','saas',
                        'parking','rental','waste','custom'
                    )),
    service_point_id TEXT,
    service_point_address TEXT,  -- JSON
    rate_plan_id    TEXT,
    install_date    TEXT,
    last_reading_date TEXT,
    last_reading_value TEXT,
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK(status IN ('active','disconnected','removed','suspended')),
    metadata        TEXT,  -- JSON
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_meter_customer ON meter(customer_id);
CREATE INDEX IF NOT EXISTS idx_meter_status ON meter(status);
CREATE INDEX IF NOT EXISTS idx_meter_service_type ON meter(service_type);

CREATE TABLE IF NOT EXISTS meter_reading (
    id              TEXT PRIMARY KEY,
    meter_id        TEXT NOT NULL REFERENCES meter(id) ON DELETE RESTRICT,
    reading_date    TEXT NOT NULL,
    reading_value   TEXT NOT NULL,
    previous_reading_value TEXT,
    consumption     TEXT,
    reading_type    TEXT NOT NULL DEFAULT 'actual'
                    CHECK(reading_type IN ('actual','estimated','adjusted','rollover')),
    uom             TEXT,
    source          TEXT NOT NULL DEFAULT 'manual'
                    CHECK(source IN ('manual','smart_meter','api','import','estimated')),
    validated       INTEGER NOT NULL DEFAULT 0 CHECK(validated IN (0,1)),
    validation_notes TEXT,
    estimated_reason TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
    -- NOTE: meter_reading is effectively immutable
);

CREATE INDEX IF NOT EXISTS idx_reading_meter ON meter_reading(meter_id);
CREATE INDEX IF NOT EXISTS idx_reading_date ON meter_reading(reading_date);

CREATE TABLE IF NOT EXISTS rate_plan (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    service_type    TEXT,
    plan_type       TEXT NOT NULL CHECK(plan_type IN (
                        'flat','tiered','time_of_use','demand',
                        'volume_discount','prepaid_credit','hybrid'
                    )),
    base_charge     TEXT,
    base_charge_period TEXT CHECK(base_charge_period IN ('monthly','quarterly','annually')),
    currency        TEXT NOT NULL DEFAULT 'USD',
    effective_from  TEXT NOT NULL,
    effective_to    TEXT,
    minimum_charge  TEXT,
    minimum_commitment TEXT,
    overage_rate    TEXT,
    metadata        TEXT,  -- JSON
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rate_tier (
    id              TEXT PRIMARY KEY,
    rate_plan_id    TEXT NOT NULL REFERENCES rate_plan(id) ON DELETE RESTRICT,
    tier_start      TEXT NOT NULL DEFAULT '0',
    tier_end        TEXT,
    rate            TEXT NOT NULL DEFAULT '0',
    fixed_charge    TEXT,
    time_of_use_period TEXT CHECK(time_of_use_period IN ('peak','off_peak','shoulder')),
    time_of_use_hours TEXT,  -- JSON
    demand_type     TEXT CHECK(demand_type IN ('energy','demand','reactive_power')),
    sort_order      INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_rate_tier_plan ON rate_tier(rate_plan_id);

CREATE TABLE IF NOT EXISTS billing_period (
    id              TEXT PRIMARY KEY,
    customer_id     TEXT NOT NULL REFERENCES customer(id) ON DELETE RESTRICT,
    meter_id        TEXT REFERENCES meter(id) ON DELETE RESTRICT,
    rate_plan_id    TEXT NOT NULL REFERENCES rate_plan(id) ON DELETE RESTRICT,
    period_start    TEXT NOT NULL,
    period_end      TEXT NOT NULL,
    total_consumption TEXT NOT NULL DEFAULT '0',
    consumption_uom TEXT,
    peak_demand     TEXT,
    base_charge     TEXT NOT NULL DEFAULT '0',
    usage_charge    TEXT NOT NULL DEFAULT '0',
    demand_charge   TEXT,
    adjustments_total TEXT NOT NULL DEFAULT '0',
    subtotal        TEXT NOT NULL DEFAULT '0',
    tax_amount      TEXT NOT NULL DEFAULT '0',
    grand_total     TEXT NOT NULL DEFAULT '0',
    invoice_id      TEXT,
    status          TEXT NOT NULL DEFAULT 'open'
                    CHECK(status IN ('open','rated','invoiced','paid','disputed','void')),
    rated_at        TEXT,
    invoiced_at     TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_billing_period_customer ON billing_period(customer_id);
CREATE INDEX IF NOT EXISTS idx_billing_period_status ON billing_period(status);
CREATE INDEX IF NOT EXISTS idx_billing_period_meter ON billing_period(meter_id);

CREATE TABLE IF NOT EXISTS billing_adjustment (
    id              TEXT PRIMARY KEY,
    billing_period_id TEXT NOT NULL REFERENCES billing_period(id) ON DELETE RESTRICT,
    adjustment_type TEXT NOT NULL CHECK(adjustment_type IN (
                        'credit','late_fee','deposit','refund',
                        'proration','discount','penalty','write_off'
                    )),
    amount          TEXT NOT NULL DEFAULT '0',
    reason          TEXT,
    approved_by     TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_billing_adj_period ON billing_adjustment(billing_period_id);

CREATE TABLE IF NOT EXISTS prepaid_credit_balance (
    id              TEXT PRIMARY KEY,
    customer_id     TEXT NOT NULL REFERENCES customer(id) ON DELETE RESTRICT,
    rate_plan_id    TEXT NOT NULL REFERENCES rate_plan(id) ON DELETE RESTRICT,
    original_amount TEXT NOT NULL DEFAULT '0',
    remaining_amount TEXT NOT NULL DEFAULT '0',
    period_start    TEXT NOT NULL,
    period_end      TEXT NOT NULL,
    overage_amount  TEXT NOT NULL DEFAULT '0',
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK(status IN ('active','exhausted','expired')),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_prepaid_customer ON prepaid_credit_balance(customer_id);
"""


# ---------------------------------------------------------------------------
# SKILL: erpclaw-manufacturing
# Tables: bom, bom_item, bom_item_substitute, bom_output_item,
#         bom_operation, operation, workstation,
#         routing, routing_operation, work_order, work_order_item,
#         job_card, production_plan, production_plan_item,
#         production_plan_material, subcontracting_order
# ---------------------------------------------------------------------------

MANUFACTURING_TABLES = """
-- =========================================================================
-- SKILL: erpclaw-manufacturing (Production Planner)
-- =========================================================================

CREATE TABLE IF NOT EXISTS operation (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    description     TEXT,
    default_workstation_id TEXT,
    is_active       INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0,1)),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workstation (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    workstation_type TEXT,
    production_capacity TEXT,
    operating_cost_per_hour TEXT NOT NULL DEFAULT '0',
    working_hours_per_day TEXT,
    holiday_list_id TEXT,
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK(status IN ('active','maintenance','offline')),
    description     TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS routing (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    description     TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS routing_operation (
    id              TEXT PRIMARY KEY,
    routing_id      TEXT NOT NULL REFERENCES routing(id) ON DELETE RESTRICT,
    operation_id    TEXT NOT NULL REFERENCES operation(id) ON DELETE RESTRICT,
    workstation_id  TEXT REFERENCES workstation(id) ON DELETE RESTRICT,
    sequence        INTEGER NOT NULL DEFAULT 0,
    time_in_minutes TEXT NOT NULL DEFAULT '0',
    operating_cost  TEXT NOT NULL DEFAULT '0'
);

CREATE INDEX IF NOT EXISTS idx_routing_op_routing ON routing_operation(routing_id);

CREATE TABLE IF NOT EXISTS bom (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    item_id         TEXT NOT NULL REFERENCES item(id) ON DELETE RESTRICT,
    quantity        TEXT NOT NULL DEFAULT '1',
    uom             TEXT,
    is_active       INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0,1)),
    is_default      INTEGER NOT NULL DEFAULT 0 CHECK(is_default IN (0,1)),
    operating_cost  TEXT NOT NULL DEFAULT '0',
    raw_material_cost TEXT NOT NULL DEFAULT '0',
    total_cost      TEXT NOT NULL DEFAULT '0',
    with_operations INTEGER NOT NULL DEFAULT 0 CHECK(with_operations IN (0,1)),
    routing_id      TEXT REFERENCES routing(id) ON DELETE RESTRICT,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bom_item ON bom(item_id);
CREATE INDEX IF NOT EXISTS idx_bom_company ON bom(company_id);

CREATE TABLE IF NOT EXISTS bom_item (
    id              TEXT PRIMARY KEY,
    bom_id          TEXT NOT NULL REFERENCES bom(id) ON DELETE RESTRICT,
    item_id         TEXT NOT NULL REFERENCES item(id) ON DELETE RESTRICT,
    quantity        TEXT NOT NULL DEFAULT '0',
    uom             TEXT,
    rate            TEXT NOT NULL DEFAULT '0',
    amount          TEXT NOT NULL DEFAULT '0',
    source_warehouse_id TEXT REFERENCES warehouse(id) ON DELETE RESTRICT,
    is_sub_assembly INTEGER NOT NULL DEFAULT 0 CHECK(is_sub_assembly IN (0,1)),
    sub_bom_id      TEXT REFERENCES bom(id) ON DELETE RESTRICT,
    scrap_percentage TEXT NOT NULL DEFAULT '0'
);

CREATE INDEX IF NOT EXISTS idx_bom_item_bom ON bom_item(bom_id);

CREATE TABLE IF NOT EXISTS bom_item_substitute (
    id              TEXT PRIMARY KEY,
    bom_item_id     TEXT NOT NULL REFERENCES bom_item(id) ON DELETE RESTRICT,
    substitute_item_id TEXT NOT NULL REFERENCES item(id) ON DELETE RESTRICT,
    conversion_factor TEXT NOT NULL DEFAULT '1',
    priority        INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_bom_item_sub_bom_item ON bom_item_substitute(bom_item_id);

CREATE TABLE IF NOT EXISTS bom_output_item (
    id              TEXT PRIMARY KEY,
    bom_id          TEXT NOT NULL REFERENCES bom(id) ON DELETE RESTRICT,
    item_id         TEXT NOT NULL REFERENCES item(id) ON DELETE RESTRICT,
    qty             TEXT NOT NULL DEFAULT '0',
    is_primary      INTEGER NOT NULL DEFAULT 0 CHECK(is_primary IN (0,1)),
    cost_allocation_pct TEXT NOT NULL DEFAULT '0'
);

CREATE INDEX IF NOT EXISTS idx_bom_output_bom ON bom_output_item(bom_id);

CREATE TABLE IF NOT EXISTS bom_operation (
    id              TEXT PRIMARY KEY,
    bom_id          TEXT NOT NULL REFERENCES bom(id) ON DELETE RESTRICT,
    operation_id    TEXT NOT NULL REFERENCES operation(id) ON DELETE RESTRICT,
    workstation_id  TEXT REFERENCES workstation(id) ON DELETE RESTRICT,
    time_in_minutes TEXT NOT NULL DEFAULT '0',
    operating_cost  TEXT NOT NULL DEFAULT '0',
    sequence        INTEGER NOT NULL DEFAULT 0,
    description     TEXT
);

CREATE INDEX IF NOT EXISTS idx_bom_op_bom ON bom_operation(bom_id);

CREATE TABLE IF NOT EXISTS work_order (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    item_id         TEXT NOT NULL REFERENCES item(id) ON DELETE RESTRICT,
    bom_id          TEXT NOT NULL REFERENCES bom(id) ON DELETE RESTRICT,
    qty             TEXT NOT NULL DEFAULT '0',
    produced_qty    TEXT NOT NULL DEFAULT '0',
    production_plan_id TEXT,
    sales_order_id  TEXT,
    planned_start_date TEXT,
    planned_end_date TEXT,
    actual_start_date TEXT,
    actual_end_date TEXT,
    source_warehouse_id TEXT REFERENCES warehouse(id) ON DELETE RESTRICT,
    target_warehouse_id TEXT REFERENCES warehouse(id) ON DELETE RESTRICT,
    wip_warehouse_id TEXT REFERENCES warehouse(id) ON DELETE RESTRICT,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN (
                        'draft','not_started','in_process','completed',
                        'stopped','cancelled'
                    )),
    material_transferred_for_manufacturing TEXT NOT NULL DEFAULT '0',
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_work_order_status ON work_order(status);
CREATE INDEX IF NOT EXISTS idx_work_order_company ON work_order(company_id);
CREATE INDEX IF NOT EXISTS idx_work_order_item ON work_order(item_id);

CREATE TABLE IF NOT EXISTS work_order_item (
    id              TEXT PRIMARY KEY,
    work_order_id   TEXT NOT NULL REFERENCES work_order(id) ON DELETE RESTRICT,
    item_id         TEXT NOT NULL REFERENCES item(id) ON DELETE RESTRICT,
    required_qty    TEXT NOT NULL DEFAULT '0',
    transferred_qty TEXT NOT NULL DEFAULT '0',
    consumed_qty    TEXT NOT NULL DEFAULT '0',
    source_warehouse_id TEXT REFERENCES warehouse(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_woi_order ON work_order_item(work_order_id);

CREATE TABLE IF NOT EXISTS job_card (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    work_order_id   TEXT NOT NULL REFERENCES work_order(id) ON DELETE RESTRICT,
    operation_id    TEXT NOT NULL REFERENCES operation(id) ON DELETE RESTRICT,
    workstation_id  TEXT REFERENCES workstation(id) ON DELETE RESTRICT,
    for_quantity    TEXT NOT NULL DEFAULT '0',
    completed_qty   TEXT NOT NULL DEFAULT '0',
    time_started    TEXT,
    time_completed  TEXT,
    total_time_in_minutes TEXT NOT NULL DEFAULT '0',
    employee_id     TEXT,
    status          TEXT NOT NULL DEFAULT 'open'
                    CHECK(status IN ('open','in_process','completed','cancelled')),
    remarks         TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_job_card_wo ON job_card(work_order_id);
CREATE INDEX IF NOT EXISTS idx_job_card_status ON job_card(status);

CREATE TABLE IF NOT EXISTS production_plan (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    planning_period_start TEXT NOT NULL,
    planning_period_end TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN ('draft','submitted','material_requested','cancelled')),
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS production_plan_item (
    id              TEXT PRIMARY KEY,
    production_plan_id TEXT NOT NULL REFERENCES production_plan(id) ON DELETE RESTRICT,
    item_id         TEXT NOT NULL REFERENCES item(id) ON DELETE RESTRICT,
    bom_id          TEXT NOT NULL REFERENCES bom(id) ON DELETE RESTRICT,
    planned_qty     TEXT NOT NULL DEFAULT '0',
    produced_qty    TEXT NOT NULL DEFAULT '0',
    ordered_qty     TEXT NOT NULL DEFAULT '0',
    sales_order_id  TEXT,
    work_order_id   TEXT,
    warehouse_id    TEXT REFERENCES warehouse(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_ppi_plan ON production_plan_item(production_plan_id);

CREATE TABLE IF NOT EXISTS production_plan_material (
    id              TEXT PRIMARY KEY,
    production_plan_id TEXT NOT NULL REFERENCES production_plan(id) ON DELETE RESTRICT,
    item_id         TEXT NOT NULL REFERENCES item(id) ON DELETE RESTRICT,
    required_qty    TEXT NOT NULL DEFAULT '0',
    available_qty   TEXT NOT NULL DEFAULT '0',
    on_order_qty    TEXT NOT NULL DEFAULT '0',
    shortfall_qty   TEXT NOT NULL DEFAULT '0',
    purchase_order_id TEXT,
    warehouse_id    TEXT REFERENCES warehouse(id) ON DELETE RESTRICT,
    procurement_type TEXT NOT NULL DEFAULT 'purchase'
                    CHECK(procurement_type IN ('purchase','manufacture','both'))
);

CREATE INDEX IF NOT EXISTS idx_ppm_plan ON production_plan_material(production_plan_id);

CREATE TABLE IF NOT EXISTS subcontracting_order (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    supplier_id     TEXT NOT NULL REFERENCES supplier(id) ON DELETE RESTRICT,
    service_item_id TEXT NOT NULL REFERENCES item(id) ON DELETE RESTRICT,
    finished_item_id TEXT NOT NULL REFERENCES item(id) ON DELETE RESTRICT,
    bom_id          TEXT NOT NULL REFERENCES bom(id) ON DELETE RESTRICT,
    qty             TEXT NOT NULL DEFAULT '0',
    supplier_warehouse_id TEXT REFERENCES warehouse(id) ON DELETE RESTRICT,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN ('draft','submitted','partially_received','completed','cancelled')),
    materials_transferred TEXT NOT NULL DEFAULT '0',
    received_qty    TEXT NOT NULL DEFAULT '0',
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_subcon_supplier ON subcontracting_order(supplier_id);
CREATE INDEX IF NOT EXISTS idx_subcon_status ON subcontracting_order(status);
"""


# ---------------------------------------------------------------------------
# SKILL: erpclaw-hr
# Tables: employee, department, designation, employee_grade,
#         leave_type, leave_allocation, leave_application,
#         attendance, holiday_list, holiday,
#         expense_claim, expense_claim_item, employee_lifecycle_event
# ---------------------------------------------------------------------------

HR_TABLES = """
-- =========================================================================
-- SKILL: erpclaw-hr (HR Generalist)
-- =========================================================================

CREATE TABLE IF NOT EXISTS department (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    parent_id       TEXT REFERENCES department(id) ON DELETE RESTRICT,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    cost_center_id  TEXT REFERENCES cost_center(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_department_company ON department(company_id);

CREATE TABLE IF NOT EXISTS designation (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    description     TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS employee_grade (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    description     TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS holiday_list (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    from_date       TEXT NOT NULL,
    to_date         TEXT NOT NULL,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS holiday (
    id              TEXT PRIMARY KEY,
    holiday_list_id TEXT NOT NULL REFERENCES holiday_list(id) ON DELETE RESTRICT,
    holiday_date    TEXT NOT NULL,
    description     TEXT
);

CREATE INDEX IF NOT EXISTS idx_holiday_list ON holiday(holiday_list_id);

CREATE TABLE IF NOT EXISTS employee (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    first_name      TEXT NOT NULL,
    last_name       TEXT,
    full_name       TEXT NOT NULL,
    date_of_birth   TEXT,
    gender          TEXT CHECK(gender IN ('male','female','other','prefer_not_to_say')),
    date_of_joining TEXT NOT NULL,
    date_of_exit    TEXT,
    employment_type TEXT NOT NULL DEFAULT 'full_time'
                    CHECK(employment_type IN ('full_time','part_time','contract','intern')),
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK(status IN ('active','inactive','suspended','left')),
    department_id   TEXT REFERENCES department(id) ON DELETE RESTRICT,
    designation_id  TEXT REFERENCES designation(id) ON DELETE RESTRICT,
    employee_grade_id TEXT REFERENCES employee_grade(id) ON DELETE RESTRICT,
    branch          TEXT,
    reporting_to    TEXT REFERENCES employee(id) ON DELETE RESTRICT,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    company_email   TEXT,
    personal_email  TEXT,
    cell_phone      TEXT,
    emergency_contact TEXT,  -- JSON
    bank_details    TEXT,    -- JSON
    ssn             TEXT,    -- encrypted
    federal_filing_status TEXT CHECK(federal_filing_status IN (
                        'single','married_jointly','married_separately','head_of_household'
                    )),
    w4_allowances   INTEGER NOT NULL DEFAULT 0,
    w4_additional_withholding TEXT NOT NULL DEFAULT '0',
    state_filing_status TEXT,
    state_withholding_allowances INTEGER NOT NULL DEFAULT 0,
    employee_401k_rate TEXT NOT NULL DEFAULT '0',
    hsa_contribution TEXT NOT NULL DEFAULT '0',
    is_exempt_from_fica INTEGER NOT NULL DEFAULT 0
                    CHECK(is_exempt_from_fica IN (0,1)),
    salary_structure_id TEXT,
    leave_policy_id TEXT,
    shift_id        TEXT,
    holiday_list_id TEXT REFERENCES holiday_list(id) ON DELETE RESTRICT,
    attendance_device_id TEXT,
    payroll_cost_center_id TEXT REFERENCES cost_center(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_employee_status ON employee(status);
CREATE INDEX IF NOT EXISTS idx_employee_company ON employee(company_id);
CREATE INDEX IF NOT EXISTS idx_employee_department ON employee(department_id);

CREATE TABLE IF NOT EXISTS leave_type (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    max_days_allowed TEXT,
    is_carry_forward INTEGER NOT NULL DEFAULT 0 CHECK(is_carry_forward IN (0,1)),
    max_carry_forward_days TEXT,
    is_paid_leave   INTEGER NOT NULL DEFAULT 1 CHECK(is_paid_leave IN (0,1)),
    is_compensatory INTEGER NOT NULL DEFAULT 0 CHECK(is_compensatory IN (0,1)),
    applicable_after_days INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS leave_allocation (
    id              TEXT PRIMARY KEY,
    employee_id     TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    leave_type_id   TEXT NOT NULL REFERENCES leave_type(id) ON DELETE RESTRICT,
    fiscal_year     TEXT NOT NULL,
    total_leaves    TEXT NOT NULL DEFAULT '0',
    used_leaves     TEXT NOT NULL DEFAULT '0',
    remaining_leaves TEXT NOT NULL DEFAULT '0',
    carry_forwarded_from TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_leave_alloc_employee ON leave_allocation(employee_id);

CREATE TABLE IF NOT EXISTS leave_application (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    employee_id     TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    leave_type_id   TEXT NOT NULL REFERENCES leave_type(id) ON DELETE RESTRICT,
    from_date       TEXT NOT NULL,
    to_date         TEXT NOT NULL,
    total_days      TEXT NOT NULL DEFAULT '0',
    half_day        INTEGER NOT NULL DEFAULT 0 CHECK(half_day IN (0,1)),
    half_day_date   TEXT,
    reason          TEXT,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN ('draft','approved','rejected','cancelled')),
    approved_by     TEXT REFERENCES employee(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_leave_app_employee ON leave_application(employee_id);
CREATE INDEX IF NOT EXISTS idx_leave_app_status ON leave_application(status);

CREATE TABLE IF NOT EXISTS attendance (
    id              TEXT PRIMARY KEY,
    employee_id     TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    attendance_date TEXT NOT NULL,
    status          TEXT NOT NULL CHECK(status IN (
                        'present','absent','half_day','on_leave','work_from_home'
                    )),
    shift           TEXT,
    check_in_time   TEXT,
    check_out_time  TEXT,
    working_hours   TEXT,
    late_entry      INTEGER NOT NULL DEFAULT 0 CHECK(late_entry IN (0,1)),
    early_exit      INTEGER NOT NULL DEFAULT 0 CHECK(early_exit IN (0,1)),
    source          TEXT NOT NULL DEFAULT 'manual'
                    CHECK(source IN ('manual','biometric','app')),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employee_id, attendance_date)
);

CREATE INDEX IF NOT EXISTS idx_attendance_employee ON attendance(employee_id);
CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(attendance_date);

CREATE TABLE IF NOT EXISTS expense_claim (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    employee_id     TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    expense_date    TEXT NOT NULL,
    total_amount    TEXT NOT NULL DEFAULT '0',
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN ('draft','submitted','approved','rejected','paid','cancelled')),
    approved_by     TEXT,
    approval_date   TEXT,
    payment_entry_id TEXT,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_expense_claim_employee ON expense_claim(employee_id);
CREATE INDEX IF NOT EXISTS idx_expense_claim_status ON expense_claim(status);

CREATE TABLE IF NOT EXISTS expense_claim_item (
    id              TEXT PRIMARY KEY,
    expense_claim_id TEXT NOT NULL REFERENCES expense_claim(id) ON DELETE RESTRICT,
    expense_type    TEXT NOT NULL CHECK(expense_type IN (
                        'travel','meals','accommodation','supplies','other'
                    )),
    description     TEXT,
    amount          TEXT NOT NULL DEFAULT '0',
    receipt_attached INTEGER NOT NULL DEFAULT 0 CHECK(receipt_attached IN (0,1)),
    account_id      TEXT REFERENCES account(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_eci_claim ON expense_claim_item(expense_claim_id);

CREATE TABLE IF NOT EXISTS employee_lifecycle_event (
    id              TEXT PRIMARY KEY,
    employee_id     TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    event_type      TEXT NOT NULL CHECK(event_type IN (
                        'hiring','confirmation','promotion','transfer',
                        'separation','resignation','retirement'
                    )),
    event_date      TEXT NOT NULL,
    details         TEXT,  -- JSON
    old_values      TEXT,  -- JSON
    new_values      TEXT,  -- JSON
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_lifecycle_employee ON employee_lifecycle_event(employee_id);

-- =========================================================================
-- Shift Management (Sprint 6, Feature #20)
-- =========================================================================

CREATE TABLE IF NOT EXISTS shift_type (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    start_time      TEXT NOT NULL,
    end_time        TEXT NOT NULL,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK(status IN ('active','inactive')),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_shift_type_company ON shift_type(company_id);

CREATE TABLE IF NOT EXISTS shift_assignment (
    id              TEXT PRIMARY KEY,
    employee_id     TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    shift_type_id   TEXT NOT NULL REFERENCES shift_type(id) ON DELETE RESTRICT,
    start_date      TEXT NOT NULL,
    end_date        TEXT,
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK(status IN ('active','inactive')),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_shift_assign_employee ON shift_assignment(employee_id);
CREATE INDEX IF NOT EXISTS idx_shift_assign_shift ON shift_assignment(shift_type_id);

-- =========================================================================
-- Attendance Regularization (Sprint 7, Feature #22f)
-- =========================================================================

CREATE TABLE IF NOT EXISTS attendance_regularization_rule (
    id                      TEXT PRIMARY KEY,
    company_id              TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    late_threshold_minutes  INTEGER NOT NULL,
    action                  TEXT NOT NULL CHECK(action IN ('half_day','deduct_leave','warn')),
    created_at              TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at              TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_att_reg_rule_company ON attendance_regularization_rule(company_id);

-- =========================================================================
-- Employee Documents (Sprint 7, Feature #21)
-- =========================================================================

CREATE TABLE IF NOT EXISTS employee_document (
    id              TEXT PRIMARY KEY,
    employee_id     TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    document_type   TEXT NOT NULL CHECK(document_type IN (
                        'passport','visa','drivers_license','i9','w4',
                        'offer_letter','contract','certificate','other'
                    )),
    document_name   TEXT NOT NULL,
    expiry_date     TEXT,
    notes           TEXT,
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK(status IN ('active','expired','archived')),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_emp_doc_employee ON employee_document(employee_id);
CREATE INDEX IF NOT EXISTS idx_emp_doc_expiry ON employee_document(expiry_date);
CREATE INDEX IF NOT EXISTS idx_emp_doc_type ON employee_document(document_type);
"""


# ---------------------------------------------------------------------------
# SKILL: erpclaw-payroll
# Tables: salary_structure, salary_component, salary_structure_detail,
#         salary_assignment, payroll_run, salary_slip, salary_slip_detail,
#         income_tax_slab, income_tax_slab_rate, fica_config,
#         futa_suta_config, employee_tax_exemption_category,
#         employee_tax_exemption_declaration,
#         state_tax_slab, employee_state_config, overtime_policy,
#         retro_pay_adjustment
# ---------------------------------------------------------------------------

PAYROLL_TABLES = """
-- =========================================================================
-- SKILL: erpclaw-payroll (Payroll Specialist)
-- =========================================================================

CREATE TABLE IF NOT EXISTS salary_structure (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    payroll_frequency TEXT NOT NULL DEFAULT 'monthly'
                    CHECK(payroll_frequency IN ('monthly','biweekly','weekly')),
    currency        TEXT NOT NULL DEFAULT 'USD',
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    is_active       INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0,1)),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS salary_component (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    component_type  TEXT NOT NULL CHECK(component_type IN (
                        'earning','deduction','employer_contribution'
                    )),
    is_tax_applicable INTEGER NOT NULL DEFAULT 1 CHECK(is_tax_applicable IN (0,1)),
    is_statutory    INTEGER NOT NULL DEFAULT 0 CHECK(is_statutory IN (0,1)),
    is_pre_tax      INTEGER NOT NULL DEFAULT 0 CHECK(is_pre_tax IN (0,1)),
    variable_based_on_taxable_salary INTEGER NOT NULL DEFAULT 0
                    CHECK(variable_based_on_taxable_salary IN (0,1)),
    description     TEXT,
    depends_on_payment_days INTEGER NOT NULL DEFAULT 1
                    CHECK(depends_on_payment_days IN (0,1)),
    is_supplemental INTEGER NOT NULL DEFAULT 0
                    CHECK(is_supplemental IN (0,1)),
    gl_account_id   TEXT REFERENCES account(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS salary_structure_detail (
    id              TEXT PRIMARY KEY,
    salary_structure_id TEXT NOT NULL REFERENCES salary_structure(id) ON DELETE RESTRICT,
    salary_component_id TEXT NOT NULL REFERENCES salary_component(id) ON DELETE RESTRICT,
    amount          TEXT,
    percentage      TEXT,
    formula         TEXT,
    base_component_id TEXT REFERENCES salary_component(id) ON DELETE RESTRICT,
    sort_order      INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_ssd_structure ON salary_structure_detail(salary_structure_id);

CREATE TABLE IF NOT EXISTS salary_assignment (
    id              TEXT PRIMARY KEY,
    employee_id     TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    salary_structure_id TEXT NOT NULL REFERENCES salary_structure(id) ON DELETE RESTRICT,
    base_amount     TEXT NOT NULL DEFAULT '0',
    effective_from  TEXT NOT NULL,
    effective_to    TEXT,
    currency        TEXT NOT NULL DEFAULT 'USD',
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_salary_assign_employee ON salary_assignment(employee_id);

CREATE TABLE IF NOT EXISTS payroll_run (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    period_start    TEXT NOT NULL,
    period_end      TEXT NOT NULL,
    payroll_frequency TEXT NOT NULL DEFAULT 'monthly'
                    CHECK(payroll_frequency IN ('monthly','biweekly','weekly')),
    department_id   TEXT REFERENCES department(id) ON DELETE RESTRICT,
    total_gross     TEXT NOT NULL DEFAULT '0',
    total_deductions TEXT NOT NULL DEFAULT '0',
    total_net       TEXT NOT NULL DEFAULT '0',
    employee_count  INTEGER NOT NULL DEFAULT 0,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN ('draft','submitted','paid','cancelled')),
    payment_entry_id TEXT,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_payroll_run_status ON payroll_run(status);
CREATE INDEX IF NOT EXISTS idx_payroll_run_company ON payroll_run(company_id);

CREATE TABLE IF NOT EXISTS salary_slip (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    payroll_run_id  TEXT NOT NULL REFERENCES payroll_run(id) ON DELETE RESTRICT,
    employee_id     TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    period_start    TEXT NOT NULL,
    period_end      TEXT NOT NULL,
    total_working_days TEXT NOT NULL DEFAULT '0',
    payment_days    TEXT NOT NULL DEFAULT '0',
    gross_pay       TEXT NOT NULL DEFAULT '0',
    total_deductions TEXT NOT NULL DEFAULT '0',
    net_pay         TEXT NOT NULL DEFAULT '0',
    bank_account    TEXT,
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN ('draft','submitted','paid','cancelled')),
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_salary_slip_payroll ON salary_slip(payroll_run_id);
CREATE INDEX IF NOT EXISTS idx_salary_slip_employee ON salary_slip(employee_id);
CREATE INDEX IF NOT EXISTS idx_salary_slip_status ON salary_slip(status);

CREATE TABLE IF NOT EXISTS salary_slip_detail (
    id              TEXT PRIMARY KEY,
    salary_slip_id  TEXT NOT NULL REFERENCES salary_slip(id) ON DELETE RESTRICT,
    salary_component_id TEXT NOT NULL REFERENCES salary_component(id) ON DELETE RESTRICT,
    component_type  TEXT NOT NULL CHECK(component_type IN ('earning','deduction')),
    amount          TEXT NOT NULL DEFAULT '0',
    year_to_date    TEXT NOT NULL DEFAULT '0'
);

CREATE INDEX IF NOT EXISTS idx_ssd_slip ON salary_slip_detail(salary_slip_id);

CREATE TABLE IF NOT EXISTS income_tax_slab (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    tax_jurisdiction TEXT NOT NULL CHECK(tax_jurisdiction IN ('federal','state')),
    state_code      TEXT,
    filing_status   TEXT CHECK(filing_status IN (
                        'single','married_jointly','married_separately','head_of_household'
                    )),
    effective_from  TEXT NOT NULL,
    standard_deduction TEXT NOT NULL DEFAULT '0',
    is_active       INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0,1)),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tax_slab_jurisdiction ON income_tax_slab(tax_jurisdiction);
CREATE INDEX IF NOT EXISTS idx_tax_slab_state ON income_tax_slab(state_code);

CREATE TABLE IF NOT EXISTS income_tax_slab_rate (
    id              TEXT PRIMARY KEY,
    slab_id         TEXT NOT NULL REFERENCES income_tax_slab(id) ON DELETE RESTRICT,
    from_amount     TEXT NOT NULL DEFAULT '0',
    to_amount       TEXT,
    rate            TEXT NOT NULL DEFAULT '0'
);

CREATE INDEX IF NOT EXISTS idx_tax_slab_rate_slab ON income_tax_slab_rate(slab_id);

CREATE TABLE IF NOT EXISTS fica_config (
    id              TEXT PRIMARY KEY,
    tax_year        INTEGER NOT NULL UNIQUE,
    ss_wage_base    TEXT NOT NULL,
    ss_employee_rate TEXT NOT NULL,
    ss_employer_rate TEXT NOT NULL,
    medicare_employee_rate TEXT NOT NULL,
    medicare_employer_rate TEXT NOT NULL,
    additional_medicare_threshold TEXT NOT NULL,
    additional_medicare_rate TEXT NOT NULL,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS futa_suta_config (
    id              TEXT PRIMARY KEY,
    tax_year        INTEGER NOT NULL,
    state_code      TEXT,
    wage_base       TEXT NOT NULL,
    rate            TEXT NOT NULL,
    employer_rate_override TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tax_year, state_code)
);

CREATE TABLE IF NOT EXISTS wage_garnishment (
    id              TEXT PRIMARY KEY,
    employee_id     TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    order_number    TEXT NOT NULL,
    creditor_name   TEXT NOT NULL,
    garnishment_type TEXT NOT NULL CHECK(garnishment_type IN
                        ('child_support','tax_levy','student_loan','creditor')),
    amount_or_percentage TEXT NOT NULL DEFAULT '0',
    is_percentage   INTEGER NOT NULL DEFAULT 0 CHECK(is_percentage IN (0,1)),
    max_percentage  TEXT NOT NULL DEFAULT '25',
    priority        INTEGER NOT NULL DEFAULT 4 CHECK(priority BETWEEN 1 AND 4),
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK(status IN ('active','paused','completed','cancelled')),
    cumulative_paid TEXT NOT NULL DEFAULT '0',
    total_owed      TEXT,
    start_date      TEXT NOT NULL,
    end_date        TEXT,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_garnishment_employee ON wage_garnishment(employee_id);
CREATE INDEX IF NOT EXISTS idx_garnishment_status ON wage_garnishment(status);
CREATE INDEX IF NOT EXISTS idx_garnishment_company ON wage_garnishment(company_id);

CREATE TABLE IF NOT EXISTS employee_tax_exemption_category (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    max_exemption_amount TEXT NOT NULL DEFAULT '0',
    parent_category_id TEXT REFERENCES employee_tax_exemption_category(id) ON DELETE RESTRICT,
    description     TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS employee_tax_exemption_declaration (
    id              TEXT PRIMARY KEY,
    employee_id     TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    category_id     TEXT NOT NULL REFERENCES employee_tax_exemption_category(id) ON DELETE RESTRICT,
    fiscal_year     TEXT NOT NULL,
    declared_amount TEXT NOT NULL DEFAULT '0',
    proof_submitted INTEGER NOT NULL DEFAULT 0 CHECK(proof_submitted IN (0,1)),
    approved        INTEGER NOT NULL DEFAULT 0 CHECK(approved IN (0,1)),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_exemption_decl_employee ON employee_tax_exemption_declaration(employee_id);

-- =========================================================================
-- Multi-State Payroll (Sprint 6, Feature #22a)
-- =========================================================================

CREATE TABLE IF NOT EXISTS state_tax_slab (
    id              TEXT PRIMARY KEY,
    state_code      TEXT NOT NULL,
    bracket_start   TEXT NOT NULL DEFAULT '0',
    bracket_end     TEXT,
    rate            TEXT NOT NULL DEFAULT '0',
    filing_status   TEXT DEFAULT 'single'
                    CHECK(filing_status IN ('single','married_jointly','married_separately','head_of_household')),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_state_tax_slab_state ON state_tax_slab(state_code);
CREATE INDEX IF NOT EXISTS idx_state_tax_slab_filing ON state_tax_slab(state_code, filing_status);

CREATE TABLE IF NOT EXISTS employee_state_config (
    id              TEXT PRIMARY KEY,
    employee_id     TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    work_state      TEXT NOT NULL,
    residence_state TEXT NOT NULL,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employee_id)
);

CREATE INDEX IF NOT EXISTS idx_emp_state_config_employee ON employee_state_config(employee_id);

-- =========================================================================
-- Overtime Policy (Sprint 6, Feature #22b)
-- =========================================================================

CREATE TABLE IF NOT EXISTS overtime_policy (
    id                    TEXT PRIMARY KEY,
    company_id            TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    weekly_threshold      TEXT NOT NULL DEFAULT '40',
    daily_threshold       TEXT,
    ot_multiplier         TEXT NOT NULL DEFAULT '1.5',
    double_ot_multiplier  TEXT NOT NULL DEFAULT '2.0',
    created_at            TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at            TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id)
);

-- =========================================================================
-- Retroactive Pay (Sprint 6, Feature #22c)
-- =========================================================================

CREATE TABLE IF NOT EXISTS retro_pay_adjustment (
    id                TEXT PRIMARY KEY,
    employee_id       TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    period_from       TEXT NOT NULL,
    period_to         TEXT NOT NULL,
    old_rate          TEXT NOT NULL DEFAULT '0',
    new_rate          TEXT NOT NULL DEFAULT '0',
    adjustment_amount TEXT NOT NULL DEFAULT '0',
    status            TEXT NOT NULL DEFAULT 'pending'
                      CHECK(status IN ('pending','applied','cancelled')),
    created_at        TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at        TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_retro_pay_employee ON retro_pay_adjustment(employee_id);

-- =========================================================================
-- Employee Bank Accounts (Sprint 7, Feature #22e — NACHA/ACH)
-- =========================================================================

CREATE TABLE IF NOT EXISTS employee_bank_account (
    id              TEXT PRIMARY KEY,
    employee_id     TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    bank_name       TEXT NOT NULL,
    routing_number  TEXT NOT NULL,
    account_number  TEXT NOT NULL,
    account_type    TEXT NOT NULL DEFAULT 'checking'
                    CHECK(account_type IN ('checking','savings')),
    is_primary      INTEGER NOT NULL DEFAULT 1 CHECK(is_primary IN (0,1)),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_emp_bank_acct_employee ON employee_bank_account(employee_id);
"""


# ---------------------------------------------------------------------------
# SKILL: erpclaw-crm
# Tables: lead, lead_source, opportunity, campaign, campaign_lead,
#         crm_activity, communication
# ---------------------------------------------------------------------------

CRM_TABLES = """
-- =========================================================================
-- SKILL: erpclaw-crm (Sales Rep)
-- =========================================================================

CREATE TABLE IF NOT EXISTS lead_source (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    description     TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lead (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    lead_name       TEXT NOT NULL,
    company_name    TEXT,
    email           TEXT,
    phone           TEXT,
    source          TEXT CHECK(source IN (
                        'website','referral','campaign','cold_call',
                        'social_media','trade_show','other'
                    )),
    lead_source_id  TEXT REFERENCES lead_source(id) ON DELETE RESTRICT,
    territory       TEXT,
    industry        TEXT,
    status          TEXT NOT NULL DEFAULT 'new'
                    CHECK(status IN ('new','contacted','qualified','converted','unresponsive','lost')),
    converted_to_customer TEXT,
    converted_to_opportunity TEXT,
    assigned_to     TEXT,
    notes           TEXT,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_lead_status ON lead(status);
CREATE INDEX IF NOT EXISTS idx_lead_company ON lead(company_id);
CREATE INDEX IF NOT EXISTS idx_lead_source ON lead(source);

CREATE TABLE IF NOT EXISTS opportunity (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    opportunity_name TEXT NOT NULL,
    lead_id         TEXT REFERENCES lead(id) ON DELETE RESTRICT,
    customer_id     TEXT REFERENCES customer(id) ON DELETE RESTRICT,
    opportunity_type TEXT NOT NULL DEFAULT 'sales'
                    CHECK(opportunity_type IN ('sales','support','maintenance')),
    source          TEXT,
    expected_closing_date TEXT,
    probability     TEXT NOT NULL DEFAULT '0',
    expected_revenue TEXT NOT NULL DEFAULT '0',
    weighted_revenue TEXT NOT NULL DEFAULT '0',
    stage           TEXT NOT NULL DEFAULT 'new'
                    CHECK(stage IN (
                        'new','contacted','qualified','proposal_sent',
                        'negotiation','won','lost'
                    )),
    lost_reason     TEXT,
    assigned_to     TEXT,
    next_follow_up_date TEXT,
    quotation_id    TEXT,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_opportunity_stage ON opportunity(stage);
CREATE INDEX IF NOT EXISTS idx_opportunity_company ON opportunity(company_id);
CREATE INDEX IF NOT EXISTS idx_opportunity_customer ON opportunity(customer_id);

CREATE TABLE IF NOT EXISTS campaign (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    campaign_type   TEXT CHECK(campaign_type IN ('email','social','event','referral','content')),
    start_date      TEXT,
    end_date        TEXT,
    budget          TEXT NOT NULL DEFAULT '0',
    actual_spend    TEXT NOT NULL DEFAULT '0',
    status          TEXT NOT NULL DEFAULT 'planned'
                    CHECK(status IN ('planned','active','completed')),
    description     TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_campaign_status ON campaign(status);

CREATE TABLE IF NOT EXISTS campaign_lead (
    id              TEXT PRIMARY KEY,
    campaign_id     TEXT NOT NULL REFERENCES campaign(id) ON DELETE RESTRICT,
    lead_id         TEXT NOT NULL REFERENCES lead(id) ON DELETE RESTRICT,
    added_date      TEXT DEFAULT CURRENT_TIMESTAMP,
    converted       INTEGER NOT NULL DEFAULT 0 CHECK(converted IN (0,1))
);

CREATE INDEX IF NOT EXISTS idx_campaign_lead_campaign ON campaign_lead(campaign_id);

CREATE TABLE IF NOT EXISTS crm_activity (
    id              TEXT PRIMARY KEY,
    activity_type   TEXT NOT NULL CHECK(activity_type IN ('call','email','meeting','note','task')),
    subject         TEXT NOT NULL,
    description     TEXT,
    activity_date   TEXT NOT NULL,
    lead_id         TEXT REFERENCES lead(id) ON DELETE RESTRICT,
    opportunity_id  TEXT REFERENCES opportunity(id) ON DELETE RESTRICT,
    customer_id     TEXT REFERENCES customer(id) ON DELETE RESTRICT,
    created_by      TEXT,
    next_action_date TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_crm_activity_lead ON crm_activity(lead_id);
CREATE INDEX IF NOT EXISTS idx_crm_activity_opportunity ON crm_activity(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_crm_activity_customer ON crm_activity(customer_id);

CREATE TABLE IF NOT EXISTS communication (
    id              TEXT PRIMARY KEY,
    communication_type TEXT NOT NULL CHECK(communication_type IN ('email','sms','call','chat')),
    subject         TEXT,
    content         TEXT,
    sender          TEXT,
    recipients      TEXT,
    reference_type  TEXT,
    reference_id    TEXT,
    sent_or_received TEXT NOT NULL DEFAULT 'sent'
                    CHECK(sent_or_received IN ('sent','received')),
    communication_date TEXT NOT NULL,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_communication_ref ON communication(reference_type, reference_id);
"""


# ---------------------------------------------------------------------------
# SKILL: erpclaw-projects
# Tables: project, task, milestone, timesheet, timesheet_detail
# ---------------------------------------------------------------------------

PROJECTS_TABLES = """
-- =========================================================================
-- SKILL: erpclaw-projects (Project Manager)
-- =========================================================================

CREATE TABLE IF NOT EXISTS project (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    project_name    TEXT NOT NULL,
    customer_id     TEXT REFERENCES customer(id) ON DELETE RESTRICT,
    project_type    TEXT NOT NULL DEFAULT 'internal'
                    CHECK(project_type IN ('internal','external','service','product')),
    status          TEXT NOT NULL DEFAULT 'open'
                    CHECK(status IN ('open','in_progress','completed','cancelled','on_hold')),
    priority        TEXT NOT NULL DEFAULT 'medium'
                    CHECK(priority IN ('low','medium','high','critical')),
    start_date      TEXT,
    end_date        TEXT,
    estimated_cost  TEXT NOT NULL DEFAULT '0',
    actual_cost     TEXT NOT NULL DEFAULT '0',
    billing_type    TEXT NOT NULL DEFAULT 'non_billable'
                    CHECK(billing_type IN ('fixed_price','time_and_material','non_billable')),
    total_billed    TEXT NOT NULL DEFAULT '0',
    profit_margin   TEXT NOT NULL DEFAULT '0',
    percent_complete TEXT NOT NULL DEFAULT '0',
    cost_center_id  TEXT REFERENCES cost_center(id) ON DELETE RESTRICT,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_project_status ON project(status);
CREATE INDEX IF NOT EXISTS idx_project_company ON project(company_id);
CREATE INDEX IF NOT EXISTS idx_project_customer ON project(customer_id);

CREATE TABLE IF NOT EXISTS task (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    project_id      TEXT NOT NULL REFERENCES project(id) ON DELETE RESTRICT,
    task_name       TEXT NOT NULL,
    parent_task_id  TEXT REFERENCES task(id) ON DELETE RESTRICT,
    assigned_to     TEXT,
    status          TEXT NOT NULL DEFAULT 'open'
                    CHECK(status IN ('open','in_progress','completed','cancelled','blocked')),
    priority        TEXT NOT NULL DEFAULT 'medium'
                    CHECK(priority IN ('low','medium','high','critical')),
    start_date      TEXT,
    end_date        TEXT,
    estimated_hours TEXT NOT NULL DEFAULT '0',
    actual_hours    TEXT NOT NULL DEFAULT '0',
    depends_on      TEXT,  -- JSON array of task IDs
    description     TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_task_project ON task(project_id);
CREATE INDEX IF NOT EXISTS idx_task_status ON task(status);
CREATE INDEX IF NOT EXISTS idx_task_assigned ON task(assigned_to);

CREATE TABLE IF NOT EXISTS milestone (
    id              TEXT PRIMARY KEY,
    project_id      TEXT NOT NULL REFERENCES project(id) ON DELETE RESTRICT,
    milestone_name  TEXT NOT NULL,
    target_date     TEXT NOT NULL,
    completion_date TEXT,
    status          TEXT NOT NULL DEFAULT 'pending'
                    CHECK(status IN ('pending','completed','missed')),
    description     TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_milestone_project ON milestone(project_id);

CREATE TABLE IF NOT EXISTS timesheet (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    employee_id     TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    start_date      TEXT NOT NULL,
    end_date        TEXT NOT NULL,
    total_hours     TEXT NOT NULL DEFAULT '0',
    total_billable_hours TEXT NOT NULL DEFAULT '0',
    total_billed_hours TEXT NOT NULL DEFAULT '0',
    total_cost      TEXT NOT NULL DEFAULT '0',
    total_billable_amount TEXT NOT NULL DEFAULT '0',
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN ('draft','submitted','billed','cancelled')),
    sales_invoice_id TEXT,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_timesheet_employee ON timesheet(employee_id);
CREATE INDEX IF NOT EXISTS idx_timesheet_status ON timesheet(status);

CREATE TABLE IF NOT EXISTS timesheet_detail (
    id              TEXT PRIMARY KEY,
    timesheet_id    TEXT NOT NULL REFERENCES timesheet(id) ON DELETE RESTRICT,
    project_id      TEXT NOT NULL REFERENCES project(id) ON DELETE RESTRICT,
    task_id         TEXT REFERENCES task(id) ON DELETE RESTRICT,
    activity_type   TEXT CHECK(activity_type IN (
                        'development','design','consulting','support','admin'
                    )),
    hours           TEXT NOT NULL DEFAULT '0',
    billing_rate    TEXT NOT NULL DEFAULT '0',
    billable        INTEGER NOT NULL DEFAULT 1 CHECK(billable IN (0,1)),
    description     TEXT,
    date            TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tsd_timesheet ON timesheet_detail(timesheet_id);
CREATE INDEX IF NOT EXISTS idx_tsd_project ON timesheet_detail(project_id);
"""


# ---------------------------------------------------------------------------
# SKILL: erpclaw-assets
# Tables: asset_category, asset, depreciation_schedule,
#         asset_movement, asset_maintenance, asset_disposal
# ---------------------------------------------------------------------------

ASSETS_TABLES = """
-- =========================================================================
-- SKILL: erpclaw-assets (Asset Controller)
-- =========================================================================

CREATE TABLE IF NOT EXISTS asset_category (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    depreciation_method TEXT NOT NULL DEFAULT 'straight_line'
                    CHECK(depreciation_method IN ('straight_line','written_down_value','double_declining')),
    useful_life_years INTEGER NOT NULL DEFAULT 5,
    asset_account_id TEXT REFERENCES account(id) ON DELETE RESTRICT,
    depreciation_account_id TEXT REFERENCES account(id) ON DELETE RESTRICT,
    accumulated_depreciation_account_id TEXT REFERENCES account(id) ON DELETE RESTRICT,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS asset (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    asset_name      TEXT NOT NULL,
    asset_category_id TEXT NOT NULL REFERENCES asset_category(id) ON DELETE RESTRICT,
    item_id         TEXT REFERENCES item(id) ON DELETE RESTRICT,
    purchase_date   TEXT,
    purchase_invoice_id TEXT,
    gross_value     TEXT NOT NULL DEFAULT '0',
    salvage_value   TEXT NOT NULL DEFAULT '0',
    depreciation_method TEXT CHECK(depreciation_method IN (
                        'straight_line','written_down_value','double_declining'
                    )),
    useful_life_years INTEGER,
    depreciation_start_date TEXT,
    current_book_value TEXT NOT NULL DEFAULT '0',
    accumulated_depreciation TEXT NOT NULL DEFAULT '0',
    status          TEXT NOT NULL DEFAULT 'draft'
                    CHECK(status IN ('draft','submitted','in_use','scrapped','sold')),
    location        TEXT,
    custodian_employee_id TEXT,
    warranty_expiry_date TEXT,
    company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_asset_status ON asset(status);
CREATE INDEX IF NOT EXISTS idx_asset_company ON asset(company_id);
CREATE INDEX IF NOT EXISTS idx_asset_category ON asset(asset_category_id);

CREATE TABLE IF NOT EXISTS depreciation_schedule (
    id              TEXT PRIMARY KEY,
    asset_id        TEXT NOT NULL REFERENCES asset(id) ON DELETE RESTRICT,
    schedule_date   TEXT NOT NULL,
    depreciation_amount TEXT NOT NULL DEFAULT '0',
    accumulated_amount TEXT NOT NULL DEFAULT '0',
    book_value_after TEXT NOT NULL DEFAULT '0',
    journal_entry_id TEXT,
    status          TEXT NOT NULL DEFAULT 'pending'
                    CHECK(status IN ('pending','posted','skipped')),
    fiscal_year     TEXT
);

CREATE INDEX IF NOT EXISTS idx_depr_sched_asset ON depreciation_schedule(asset_id);
CREATE INDEX IF NOT EXISTS idx_depr_sched_status ON depreciation_schedule(status);
CREATE INDEX IF NOT EXISTS idx_depr_sched_date ON depreciation_schedule(schedule_date);

CREATE TABLE IF NOT EXISTS asset_movement (
    id              TEXT PRIMARY KEY,
    asset_id        TEXT NOT NULL REFERENCES asset(id) ON DELETE RESTRICT,
    movement_type   TEXT NOT NULL CHECK(movement_type IN ('transfer','issue','receipt')),
    from_location   TEXT,
    to_location     TEXT,
    from_employee_id TEXT,
    to_employee_id  TEXT,
    movement_date   TEXT NOT NULL,
    reason          TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_asset_movement_asset ON asset_movement(asset_id);

CREATE TABLE IF NOT EXISTS asset_maintenance (
    id              TEXT PRIMARY KEY,
    asset_id        TEXT NOT NULL REFERENCES asset(id) ON DELETE RESTRICT,
    maintenance_type TEXT NOT NULL CHECK(maintenance_type IN ('preventive','corrective')),
    scheduled_date  TEXT,
    actual_date     TEXT,
    description     TEXT,
    cost            TEXT NOT NULL DEFAULT '0',
    performed_by    TEXT,
    status          TEXT NOT NULL DEFAULT 'planned'
                    CHECK(status IN ('planned','overdue','completed')),
    next_due_date   TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_asset_maint_asset ON asset_maintenance(asset_id);
CREATE INDEX IF NOT EXISTS idx_asset_maint_status ON asset_maintenance(status);

CREATE TABLE IF NOT EXISTS asset_disposal (
    id              TEXT PRIMARY KEY,
    asset_id        TEXT NOT NULL REFERENCES asset(id) ON DELETE RESTRICT,
    disposal_date   TEXT NOT NULL,
    disposal_method TEXT NOT NULL CHECK(disposal_method IN ('sale','scrap','write_off')),
    sale_amount     TEXT,
    book_value_at_disposal TEXT NOT NULL DEFAULT '0',
    gain_or_loss    TEXT NOT NULL DEFAULT '0',
    journal_entry_id TEXT,
    buyer_details   TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_asset_disposal_asset ON asset_disposal(asset_id);
"""


# ---------------------------------------------------------------------------
# SKILL: erpclaw-quality
# Tables: quality_inspection_template, quality_inspection_parameter,
#         quality_inspection, quality_inspection_reading,
#         non_conformance, quality_goal
# ---------------------------------------------------------------------------

QUALITY_TABLES = """
-- =========================================================================
-- SKILL: erpclaw-quality (Quality Inspector)
-- =========================================================================

CREATE TABLE IF NOT EXISTS quality_inspection_template (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    item_id         TEXT REFERENCES item(id) ON DELETE RESTRICT,
    inspection_type TEXT NOT NULL CHECK(inspection_type IN ('incoming','outgoing','in_process')),
    description     TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quality_inspection_parameter (
    id              TEXT PRIMARY KEY,
    template_id     TEXT NOT NULL REFERENCES quality_inspection_template(id) ON DELETE RESTRICT,
    parameter_name  TEXT NOT NULL,
    parameter_type  TEXT NOT NULL CHECK(parameter_type IN ('numeric','non_numeric','formula')),
    min_value       TEXT,
    max_value       TEXT,
    acceptance_value TEXT,
    formula         TEXT,
    uom             TEXT,
    sort_order      INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_qip_template ON quality_inspection_parameter(template_id);

CREATE TABLE IF NOT EXISTS quality_inspection (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    inspection_type TEXT NOT NULL CHECK(inspection_type IN ('incoming','outgoing','in_process')),
    item_id         TEXT NOT NULL REFERENCES item(id) ON DELETE RESTRICT,
    batch_id        TEXT REFERENCES batch(id) ON DELETE RESTRICT,
    reference_type  TEXT CHECK(reference_type IN ('purchase_receipt','delivery_note','stock_entry')),
    reference_id    TEXT,
    template_id     TEXT REFERENCES quality_inspection_template(id) ON DELETE RESTRICT,
    inspection_date TEXT NOT NULL,
    inspected_by    TEXT,
    sample_size     INTEGER NOT NULL DEFAULT 1,
    status          TEXT NOT NULL DEFAULT 'accepted'
                    CHECK(status IN ('accepted','rejected','partially_accepted')),
    remarks         TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_qi_item ON quality_inspection(item_id);
CREATE INDEX IF NOT EXISTS idx_qi_status ON quality_inspection(status);
CREATE INDEX IF NOT EXISTS idx_qi_reference ON quality_inspection(reference_type, reference_id);

CREATE TABLE IF NOT EXISTS quality_inspection_reading (
    id              TEXT PRIMARY KEY,
    quality_inspection_id TEXT NOT NULL REFERENCES quality_inspection(id) ON DELETE RESTRICT,
    parameter_id    TEXT NOT NULL REFERENCES quality_inspection_parameter(id) ON DELETE RESTRICT,
    reading_value   TEXT,
    status          TEXT NOT NULL DEFAULT 'accepted'
                    CHECK(status IN ('accepted','rejected')),
    remarks         TEXT
);

CREATE INDEX IF NOT EXISTS idx_qir_inspection ON quality_inspection_reading(quality_inspection_id);

CREATE TABLE IF NOT EXISTS non_conformance (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    quality_inspection_id TEXT REFERENCES quality_inspection(id) ON DELETE RESTRICT,
    item_id         TEXT REFERENCES item(id) ON DELETE RESTRICT,
    batch_id        TEXT,
    description     TEXT NOT NULL,
    severity        TEXT NOT NULL DEFAULT 'minor'
                    CHECK(severity IN ('minor','major','critical')),
    root_cause      TEXT,
    corrective_action TEXT,
    preventive_action TEXT,
    responsible_employee_id TEXT,
    status          TEXT NOT NULL DEFAULT 'open'
                    CHECK(status IN ('open','investigating','resolved','closed')),
    resolution_date TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_nc_status ON non_conformance(status);
CREATE INDEX IF NOT EXISTS idx_nc_item ON non_conformance(item_id);

CREATE TABLE IF NOT EXISTS quality_goal (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    measurable      TEXT,
    current_value   TEXT NOT NULL DEFAULT '0',
    target_value    TEXT NOT NULL DEFAULT '0',
    monitoring_frequency TEXT NOT NULL DEFAULT 'monthly'
                    CHECK(monitoring_frequency IN ('daily','weekly','monthly')),
    status          TEXT NOT NULL DEFAULT 'on_track'
                    CHECK(status IN ('on_track','at_risk','behind')),
    review_date     TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


# ---------------------------------------------------------------------------
# SKILL: erpclaw-support
# Tables: issue, issue_comment, service_level_agreement,
#         warranty_claim
# ---------------------------------------------------------------------------

SUPPORT_TABLES = """
-- =========================================================================
-- SKILL: erpclaw-support (Support Agent)
-- =========================================================================

CREATE TABLE IF NOT EXISTS service_level_agreement (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    priority_response_times TEXT,    -- JSON
    priority_resolution_times TEXT,  -- JSON
    working_hours   TEXT,
    is_default      INTEGER NOT NULL DEFAULT 0 CHECK(is_default IN (0,1)),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS issue (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    subject         TEXT NOT NULL,
    description     TEXT,
    customer_id     TEXT REFERENCES customer(id) ON DELETE RESTRICT,
    item_id         TEXT REFERENCES item(id) ON DELETE RESTRICT,
    serial_number_id TEXT REFERENCES serial_number(id) ON DELETE RESTRICT,
    priority        TEXT NOT NULL DEFAULT 'medium'
                    CHECK(priority IN ('low','medium','high','critical')),
    issue_type      TEXT CHECK(issue_type IN (
                        'bug','feature_request','question','complaint','return'
                    )),
    status          TEXT NOT NULL DEFAULT 'open'
                    CHECK(status IN (
                        'open','in_progress','waiting_on_customer','resolved','closed'
                    )),
    assigned_to     TEXT,
    sla_id          TEXT REFERENCES service_level_agreement(id) ON DELETE RESTRICT,
    response_due    TEXT,
    resolution_due  TEXT,
    first_response_at TEXT,
    resolved_at     TEXT,
    sla_breached    INTEGER NOT NULL DEFAULT 0 CHECK(sla_breached IN (0,1)),
    resolution_notes TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_issue_status ON issue(status);
CREATE INDEX IF NOT EXISTS idx_issue_customer ON issue(customer_id);
CREATE INDEX IF NOT EXISTS idx_issue_priority ON issue(priority);

CREATE TABLE IF NOT EXISTS issue_comment (
    id              TEXT PRIMARY KEY,
    issue_id        TEXT NOT NULL REFERENCES issue(id) ON DELETE RESTRICT,
    comment_by      TEXT NOT NULL CHECK(comment_by IN ('employee','customer')),
    comment_text    TEXT NOT NULL,
    is_internal     INTEGER NOT NULL DEFAULT 0 CHECK(is_internal IN (0,1)),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_issue_comment_issue ON issue_comment(issue_id);

CREATE TABLE IF NOT EXISTS warranty_claim (
    id              TEXT PRIMARY KEY,
    naming_series   TEXT,
    customer_id     TEXT NOT NULL REFERENCES customer(id) ON DELETE RESTRICT,
    item_id         TEXT REFERENCES item(id) ON DELETE RESTRICT,
    serial_number_id TEXT REFERENCES serial_number(id) ON DELETE RESTRICT,
    warranty_expiry_date TEXT,
    complaint_description TEXT NOT NULL,
    resolution      TEXT CHECK(resolution IN ('repair','replace','refund','rejected')),
    resolution_date TEXT,
    cost            TEXT NOT NULL DEFAULT '0',
    status          TEXT NOT NULL DEFAULT 'open'
                    CHECK(status IN ('open','in_progress','resolved','closed')),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_warranty_customer ON warranty_claim(customer_id);
CREATE INDEX IF NOT EXISTS idx_warranty_status ON warranty_claim(status);

"""





# ---------------------------------------------------------------------------
# SKILL: erpclaw-accounting-adv
# Tables: advacct_revenue_contract, advacct_performance_obligation,
#         advacct_variable_consideration, advacct_revenue_schedule,
#         advacct_lease, advacct_lease_payment, advacct_amortization_entry,
#         advacct_ic_transaction, advacct_transfer_price_rule,
#         advacct_consolidation_group, advacct_group_entity,
#         advacct_elimination_entry
# ---------------------------------------------------------------------------

ADVACCT_TABLES = """
-- =========================================================================
-- SKILL: erpclaw-accounting-adv (Advanced Accounting)
-- ASC 606, ASC 842, Intercompany, Consolidation
-- =========================================================================

-- Revenue Recognition (ASC 606) -- 4 tables

CREATE TABLE IF NOT EXISTS advacct_revenue_contract (
    id                  TEXT PRIMARY KEY,
    naming_series       TEXT,
    customer_name       TEXT NOT NULL,
    contract_number     TEXT,
    start_date          TEXT,
    end_date            TEXT,
    total_value         TEXT NOT NULL DEFAULT '0',
    allocated_value     TEXT NOT NULL DEFAULT '0',
    contract_status     TEXT NOT NULL DEFAULT 'active'
                        CHECK(contract_status IN ('draft','active','modified','completed','terminated')),
    modification_count  INTEGER NOT NULL DEFAULT 0,
    company_id          TEXT NOT NULL REFERENCES company(id),
    created_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_advacct_rcon_company ON advacct_revenue_contract(company_id);
CREATE INDEX IF NOT EXISTS idx_advacct_rcon_status ON advacct_revenue_contract(contract_status);
CREATE INDEX IF NOT EXISTS idx_advacct_rcon_customer ON advacct_revenue_contract(customer_name);

CREATE TABLE IF NOT EXISTS advacct_performance_obligation (
    id                  TEXT PRIMARY KEY,
    contract_id         TEXT NOT NULL REFERENCES advacct_revenue_contract(id) ON DELETE CASCADE,
    name                TEXT NOT NULL,
    standalone_price    TEXT NOT NULL DEFAULT '0',
    allocated_price     TEXT NOT NULL DEFAULT '0',
    recognition_method  TEXT NOT NULL DEFAULT 'over_time'
                        CHECK(recognition_method IN ('point_in_time','over_time')),
    recognition_basis   TEXT NOT NULL DEFAULT 'time'
                        CHECK(recognition_basis IN ('output','input','time')),
    pct_complete        TEXT NOT NULL DEFAULT '0',
    obligation_status   TEXT NOT NULL DEFAULT 'unsatisfied'
                        CHECK(obligation_status IN ('unsatisfied','partially_satisfied','satisfied')),
    satisfied_date      TEXT,
    company_id          TEXT NOT NULL REFERENCES company(id),
    created_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_advacct_po_contract ON advacct_performance_obligation(contract_id);
CREATE INDEX IF NOT EXISTS idx_advacct_po_status ON advacct_performance_obligation(obligation_status);
CREATE INDEX IF NOT EXISTS idx_advacct_po_company ON advacct_performance_obligation(company_id);

CREATE TABLE IF NOT EXISTS advacct_variable_consideration (
    id                  TEXT PRIMARY KEY,
    contract_id         TEXT NOT NULL REFERENCES advacct_revenue_contract(id) ON DELETE CASCADE,
    description         TEXT NOT NULL,
    estimated_amount    TEXT NOT NULL DEFAULT '0',
    constraint_amount   TEXT NOT NULL DEFAULT '0',
    method              TEXT NOT NULL DEFAULT 'expected_value'
                        CHECK(method IN ('expected_value','most_likely')),
    probability         TEXT NOT NULL DEFAULT '0',
    company_id          TEXT NOT NULL REFERENCES company(id),
    created_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_advacct_vc_contract ON advacct_variable_consideration(contract_id);
CREATE INDEX IF NOT EXISTS idx_advacct_vc_company ON advacct_variable_consideration(company_id);

CREATE TABLE IF NOT EXISTS advacct_revenue_schedule (
    id                  TEXT PRIMARY KEY,
    obligation_id       TEXT NOT NULL REFERENCES advacct_performance_obligation(id) ON DELETE CASCADE,
    period_date         TEXT NOT NULL,
    amount              TEXT NOT NULL DEFAULT '0',
    recognized          INTEGER NOT NULL DEFAULT 0,
    company_id          TEXT NOT NULL REFERENCES company(id),
    created_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_advacct_rs_obligation ON advacct_revenue_schedule(obligation_id);
CREATE INDEX IF NOT EXISTS idx_advacct_rs_period ON advacct_revenue_schedule(period_date);
CREATE INDEX IF NOT EXISTS idx_advacct_rs_company ON advacct_revenue_schedule(company_id);

-- Lease Accounting (ASC 842) -- 3 tables

CREATE TABLE IF NOT EXISTS advacct_lease (
    id                      TEXT PRIMARY KEY,
    naming_series           TEXT,
    lessee_name             TEXT NOT NULL,
    lessor_name             TEXT NOT NULL,
    asset_description       TEXT,
    lease_type              TEXT NOT NULL DEFAULT 'operating'
                            CHECK(lease_type IN ('operating','finance')),
    start_date              TEXT,
    end_date                TEXT,
    term_months             INTEGER NOT NULL DEFAULT 0,
    monthly_payment         TEXT NOT NULL DEFAULT '0',
    annual_escalation       TEXT NOT NULL DEFAULT '0',
    discount_rate           TEXT NOT NULL DEFAULT '0',
    purchase_option_price   TEXT,
    rou_asset_value         TEXT,
    lease_liability         TEXT,
    lease_status            TEXT NOT NULL DEFAULT 'draft'
                            CHECK(lease_status IN ('draft','active','modified','expired','terminated')),
    company_id              TEXT NOT NULL REFERENCES company(id),
    created_at              TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_advacct_lease_company ON advacct_lease(company_id);
CREATE INDEX IF NOT EXISTS idx_advacct_lease_status ON advacct_lease(lease_status);
CREATE INDEX IF NOT EXISTS idx_advacct_lease_type ON advacct_lease(lease_type);

CREATE TABLE IF NOT EXISTS advacct_lease_payment (
    id                  TEXT PRIMARY KEY,
    lease_id            TEXT NOT NULL REFERENCES advacct_lease(id) ON DELETE CASCADE,
    payment_date        TEXT NOT NULL,
    payment_amount      TEXT NOT NULL DEFAULT '0',
    principal           TEXT NOT NULL DEFAULT '0',
    interest            TEXT NOT NULL DEFAULT '0',
    balance_after       TEXT NOT NULL DEFAULT '0',
    payment_status      TEXT NOT NULL DEFAULT 'scheduled'
                        CHECK(payment_status IN ('scheduled','paid','overdue')),
    company_id          TEXT NOT NULL REFERENCES company(id),
    created_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_advacct_lpay_lease ON advacct_lease_payment(lease_id);
CREATE INDEX IF NOT EXISTS idx_advacct_lpay_date ON advacct_lease_payment(payment_date);
CREATE INDEX IF NOT EXISTS idx_advacct_lpay_status ON advacct_lease_payment(payment_status);
CREATE INDEX IF NOT EXISTS idx_advacct_lpay_company ON advacct_lease_payment(company_id);

CREATE TABLE IF NOT EXISTS advacct_amortization_entry (
    id                  TEXT PRIMARY KEY,
    lease_id            TEXT NOT NULL REFERENCES advacct_lease(id) ON DELETE CASCADE,
    period_date         TEXT NOT NULL,
    opening_balance     TEXT NOT NULL DEFAULT '0',
    payment             TEXT NOT NULL DEFAULT '0',
    interest            TEXT NOT NULL DEFAULT '0',
    principal           TEXT NOT NULL DEFAULT '0',
    closing_balance     TEXT NOT NULL DEFAULT '0',
    company_id          TEXT NOT NULL REFERENCES company(id),
    created_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_advacct_amort_lease ON advacct_amortization_entry(lease_id);
CREATE INDEX IF NOT EXISTS idx_advacct_amort_period ON advacct_amortization_entry(period_date);
CREATE INDEX IF NOT EXISTS idx_advacct_amort_company ON advacct_amortization_entry(company_id);

-- Intercompany Transactions -- 2 tables

CREATE TABLE IF NOT EXISTS advacct_ic_transaction (
    id                      TEXT PRIMARY KEY,
    naming_series           TEXT,
    from_company_id         TEXT NOT NULL,
    to_company_id           TEXT NOT NULL,
    transaction_type        TEXT NOT NULL
                            CHECK(transaction_type IN ('sale','purchase','service','loan','dividend','allocation')),
    description             TEXT,
    amount                  TEXT NOT NULL DEFAULT '0',
    currency                TEXT NOT NULL DEFAULT 'USD',
    transfer_price_method   TEXT
                            CHECK(transfer_price_method IN ('cost_plus','resale_minus','comparable','other')),
    ic_status               TEXT NOT NULL DEFAULT 'draft'
                            CHECK(ic_status IN ('draft','pending_approval','approved','posted','eliminated')),
    posted_date             TEXT,
    company_id              TEXT NOT NULL REFERENCES company(id),
    created_at              TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_advacct_ict_from ON advacct_ic_transaction(from_company_id);
CREATE INDEX IF NOT EXISTS idx_advacct_ict_to ON advacct_ic_transaction(to_company_id);
CREATE INDEX IF NOT EXISTS idx_advacct_ict_status ON advacct_ic_transaction(ic_status);
CREATE INDEX IF NOT EXISTS idx_advacct_ict_type ON advacct_ic_transaction(transaction_type);
CREATE INDEX IF NOT EXISTS idx_advacct_ict_company ON advacct_ic_transaction(company_id);

CREATE TABLE IF NOT EXISTS advacct_transfer_price_rule (
    id                  TEXT PRIMARY KEY,
    from_company_id     TEXT,
    to_company_id       TEXT,
    transaction_type    TEXT
                        CHECK(transaction_type IN ('sale','purchase','service','loan','dividend','allocation')),
    method              TEXT NOT NULL DEFAULT 'cost_plus'
                        CHECK(method IN ('cost_plus','resale_minus','comparable','other')),
    markup_pct          TEXT NOT NULL DEFAULT '0',
    effective_date      TEXT,
    expiry_date         TEXT,
    company_id          TEXT NOT NULL REFERENCES company(id),
    created_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_advacct_tpr_companies ON advacct_transfer_price_rule(from_company_id, to_company_id);
CREATE INDEX IF NOT EXISTS idx_advacct_tpr_type ON advacct_transfer_price_rule(transaction_type);
CREATE INDEX IF NOT EXISTS idx_advacct_tpr_company ON advacct_transfer_price_rule(company_id);

-- Multi-Entity Consolidation -- 3 tables

CREATE TABLE IF NOT EXISTS advacct_consolidation_group (
    id                      TEXT PRIMARY KEY,
    naming_series           TEXT,
    name                    TEXT NOT NULL,
    parent_company_id       TEXT,
    consolidation_currency  TEXT NOT NULL DEFAULT 'USD',
    group_status            TEXT NOT NULL DEFAULT 'active'
                            CHECK(group_status IN ('active','inactive')),
    company_id              TEXT NOT NULL REFERENCES company(id),
    created_at              TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_advacct_cgrp_company ON advacct_consolidation_group(company_id);
CREATE INDEX IF NOT EXISTS idx_advacct_cgrp_status ON advacct_consolidation_group(group_status);

CREATE TABLE IF NOT EXISTS advacct_group_entity (
    id                      TEXT PRIMARY KEY,
    group_id                TEXT NOT NULL REFERENCES advacct_consolidation_group(id) ON DELETE CASCADE,
    entity_company_id       TEXT NOT NULL,
    entity_name             TEXT NOT NULL,
    ownership_pct           TEXT NOT NULL DEFAULT '100',
    functional_currency     TEXT NOT NULL DEFAULT 'USD',
    consolidation_method    TEXT NOT NULL DEFAULT 'full'
                            CHECK(consolidation_method IN ('full','proportional','equity')),
    is_active               INTEGER NOT NULL DEFAULT 1,
    company_id              TEXT NOT NULL REFERENCES company(id),
    created_at              TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_advacct_ge_group ON advacct_group_entity(group_id);
CREATE INDEX IF NOT EXISTS idx_advacct_ge_entity ON advacct_group_entity(entity_company_id);
CREATE INDEX IF NOT EXISTS idx_advacct_ge_company ON advacct_group_entity(company_id);

CREATE TABLE IF NOT EXISTS advacct_elimination_entry (
    id                  TEXT PRIMARY KEY,
    group_id            TEXT NOT NULL REFERENCES advacct_consolidation_group(id) ON DELETE CASCADE,
    period_date         TEXT NOT NULL,
    debit_account       TEXT NOT NULL,
    credit_account      TEXT NOT NULL,
    amount              TEXT NOT NULL DEFAULT '0',
    description         TEXT,
    entry_type          TEXT NOT NULL DEFAULT 'ic_elimination'
                        CHECK(entry_type IN ('ic_elimination','minority_interest','currency_translation','goodwill')),
    company_id          TEXT NOT NULL REFERENCES company(id),
    created_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_advacct_ee_group ON advacct_elimination_entry(group_id);
CREATE INDEX IF NOT EXISTS idx_advacct_ee_period ON advacct_elimination_entry(period_date);
CREATE INDEX IF NOT EXISTS idx_advacct_ee_type ON advacct_elimination_entry(entry_type);
CREATE INDEX IF NOT EXISTS idx_advacct_ee_company ON advacct_elimination_entry(company_id);
"""


# ---------------------------------------------------------------------------
# TYPE REGISTRY TABLES (required by tax, GL validation, and cross-skill refs)
# ---------------------------------------------------------------------------
REGISTRY_TABLES = """
CREATE TABLE IF NOT EXISTS voucher_type_registry (
    voucher_type TEXT NOT NULL,
    skill_name   TEXT NOT NULL,
    label        TEXT NOT NULL,
    target_table TEXT NOT NULL CHECK(target_table IN ('gl_entry','stock_ledger_entry','payment_allocation')),
    PRIMARY KEY (voucher_type, target_table)
);

CREATE TABLE IF NOT EXISTS party_type_registry (
    party_type  TEXT PRIMARY KEY,
    skill_name  TEXT NOT NULL,
    label       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS account_type_registry (
    account_type TEXT PRIMARY KEY,
    skill_name   TEXT NOT NULL,
    label        TEXT NOT NULL
);
"""


# ---------------------------------------------------------------------------
# SKILL: erpclaw-modules (Module Installer System)
# Tables: erpclaw_module, erpclaw_module_action
# ---------------------------------------------------------------------------

MODULE_TABLES = """
-- =========================================================================
-- SKILL: erpclaw-modules (Module Installer System)
-- =========================================================================

CREATE TABLE IF NOT EXISTS erpclaw_module (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    display_name    TEXT NOT NULL,
    version         TEXT NOT NULL DEFAULT '0.0.0',
    category        TEXT NOT NULL DEFAULT 'expansion'
                    CHECK(category IN ('core','expansion','infrastructure','vertical','sub-vertical','regional')),
    github_repo     TEXT NOT NULL DEFAULT '',
    install_path    TEXT NOT NULL DEFAULT '',
    installed_at    TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    install_status  TEXT NOT NULL DEFAULT 'pending'
                    CHECK(install_status IN ('pending','updating','installed','failed','removing')),
    git_commit      TEXT,
    tables_created  INTEGER NOT NULL DEFAULT 0,
    action_count    INTEGER NOT NULL DEFAULT 0,
    is_active       INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0,1)),
    requires_json   TEXT NOT NULL DEFAULT '[]',
    error_log       TEXT
);

CREATE INDEX IF NOT EXISTS idx_erpclaw_module_name ON erpclaw_module(name);
CREATE INDEX IF NOT EXISTS idx_erpclaw_module_category ON erpclaw_module(category);
CREATE INDEX IF NOT EXISTS idx_erpclaw_module_status ON erpclaw_module(install_status);

CREATE TABLE IF NOT EXISTS erpclaw_module_action (
    module_name     TEXT NOT NULL,
    action_name     TEXT NOT NULL,
    PRIMARY KEY (module_name, action_name),
    FOREIGN KEY (module_name) REFERENCES erpclaw_module(name) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_erpclaw_module_action_action ON erpclaw_module_action(action_name);
CREATE INDEX IF NOT EXISTS idx_erpclaw_module_action_module ON erpclaw_module_action(module_name);
"""


# ===========================================================================
# SKILL: erpclaw-os (Module Validation / ERPClaw OS)
# Tables: erpclaw_module_validation, erpclaw_table_ownership
# ===========================================================================

OS_TABLES = """
-- =========================================================================
-- SKILL: erpclaw-os (Module Validation)
-- =========================================================================

CREATE TABLE IF NOT EXISTS erpclaw_module_validation (
    id              TEXT PRIMARY KEY,
    module_name     TEXT NOT NULL,
    module_path     TEXT NOT NULL,
    validation_type TEXT NOT NULL CHECK(validation_type IN ('static', 'runtime', 'full')),
    result          TEXT NOT NULL CHECK(result IN ('pass', 'fail')),
    violations      TEXT,  -- JSON array of violation objects
    article_results TEXT,  -- JSON object: {article_number: pass/fail/skip}
    duration_ms     INTEGER,
    validated_at    TEXT DEFAULT CURRENT_TIMESTAMP,
    validated_by    TEXT  -- 'human' or 'system'
);

CREATE INDEX IF NOT EXISTS idx_erpclaw_module_validation_module
    ON erpclaw_module_validation(module_name);
CREATE INDEX IF NOT EXISTS idx_erpclaw_module_validation_result
    ON erpclaw_module_validation(result);

CREATE TABLE IF NOT EXISTS erpclaw_table_ownership (
    table_name      TEXT PRIMARY KEY,
    module_name     TEXT NOT NULL,
    init_db_path    TEXT NOT NULL,
    discovered_at   TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_erpclaw_table_ownership_module
    ON erpclaw_table_ownership(module_name);

-- Phase 3 (3a): Semantic Correctness Engine
CREATE TABLE IF NOT EXISTS erpclaw_semantic_rule (
    id              TEXT PRIMARY KEY,
    rule_name       TEXT NOT NULL UNIQUE,
    category        TEXT NOT NULL CHECK(category IN ('account_classification', 'posting_pattern', 'period_validation')),
    description     TEXT NOT NULL,
    rule_definition TEXT NOT NULL,
    severity        TEXT NOT NULL CHECK(severity IN ('critical', 'warning', 'info')),
    source_module   TEXT,
    is_active       INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0, 1)),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS erpclaw_semantic_finding (
    id              TEXT PRIMARY KEY,
    module_name     TEXT NOT NULL,
    rule_id         TEXT NOT NULL REFERENCES erpclaw_semantic_rule(id),
    finding_type    TEXT NOT NULL CHECK(finding_type IN ('account_classification', 'posting_pattern', 'period_validation')),
    severity        TEXT NOT NULL CHECK(severity IN ('critical', 'warning', 'info')),
    description     TEXT NOT NULL,
    evidence        TEXT,
    status          TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open', 'acknowledged', 'resolved', 'false_positive')),
    found_at        TEXT DEFAULT CURRENT_TIMESTAMP,
    resolved_at     TEXT,
    resolved_by     TEXT
);

CREATE INDEX IF NOT EXISTS idx_erpclaw_semantic_finding_module
    ON erpclaw_semantic_finding(module_name);
CREATE INDEX IF NOT EXISTS idx_erpclaw_semantic_finding_rule
    ON erpclaw_semantic_finding(rule_id);
CREATE INDEX IF NOT EXISTS idx_erpclaw_semantic_finding_status
    ON erpclaw_semantic_finding(status);

-- Phase 3 (3b): Deploy Audit (must precede improvement_log FK)
CREATE TABLE IF NOT EXISTS erpclaw_deploy_audit (
    id              TEXT PRIMARY KEY,
    module_name     TEXT NOT NULL,
    pipeline_result TEXT NOT NULL CHECK(pipeline_result IN ('deployed', 'queued', 'rejected', 'failed')),
    tier            INTEGER,
    steps           TEXT NOT NULL,
    git_commit      TEXT,
    human_approved  INTEGER CHECK(human_approved IN (0, 1)),
    approved_by     TEXT,
    deployed_at     TEXT DEFAULT CURRENT_TIMESTAMP,
    reasoning       TEXT
);

-- Phase 3 (3b): Self-Improvement Log
CREATE TABLE IF NOT EXISTS erpclaw_improvement_log (
    id              TEXT PRIMARY KEY,
    module_name     TEXT,
    category        TEXT NOT NULL CHECK(category IN ('performance', 'usability', 'coverage', 'semantic', 'structural')),
    description     TEXT NOT NULL,
    evidence        TEXT,
    proposed_diff   TEXT,
    expected_impact TEXT,
    source          TEXT NOT NULL CHECK(source IN ('heartbeat', 'dgm', 'semantic', 'manual', 'gap_detector')),
    status          TEXT NOT NULL DEFAULT 'proposed' CHECK(status IN ('proposed', 'approved', 'rejected', 'deferred', 'deployed')),
    proposed_at     TEXT DEFAULT CURRENT_TIMESTAMP,
    reviewed_at     TEXT,
    reviewed_by     TEXT,
    review_notes    TEXT,
    deploy_audit_id TEXT REFERENCES erpclaw_deploy_audit(id)
);

CREATE INDEX IF NOT EXISTS idx_erpclaw_improvement_log_category
    ON erpclaw_improvement_log(category);
CREATE INDEX IF NOT EXISTS idx_erpclaw_improvement_log_status
    ON erpclaw_improvement_log(status);
CREATE INDEX IF NOT EXISTS idx_erpclaw_improvement_log_source
    ON erpclaw_improvement_log(source);
CREATE INDEX IF NOT EXISTS idx_erpclaw_improvement_log_proposed_at
    ON erpclaw_improvement_log(proposed_at);

-- Phase 3 (3c): DGM Variant Engine
CREATE TABLE IF NOT EXISTS erpclaw_dgm_run (
    id              TEXT PRIMARY KEY,
    module_name     TEXT NOT NULL,
    action_name     TEXT NOT NULL,
    variant_count   INTEGER NOT NULL,
    best_variant_id TEXT,
    current_exec_ms INTEGER,
    best_exec_ms    INTEGER,
    improvement_pct TEXT,
    status          TEXT NOT NULL CHECK(status IN ('running', 'completed', 'failed', 'no_improvement')),
    improvement_id  TEXT REFERENCES erpclaw_improvement_log(id),
    started_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    completed_at    TEXT
);

CREATE INDEX IF NOT EXISTS idx_erpclaw_dgm_run_module
    ON erpclaw_dgm_run(module_name);
CREATE INDEX IF NOT EXISTS idx_erpclaw_dgm_run_status
    ON erpclaw_dgm_run(status);

CREATE TABLE IF NOT EXISTS erpclaw_dgm_variant (
    id              TEXT PRIMARY KEY,
    run_id          TEXT NOT NULL REFERENCES erpclaw_dgm_run(id),
    module_name     TEXT NOT NULL,
    action_name     TEXT NOT NULL,
    variant_number  INTEGER NOT NULL,
    variant_code    TEXT NOT NULL,
    variant_diff    TEXT,
    mutation_type   TEXT NOT NULL CHECK(mutation_type IN ('query_optimization', 'algorithm_change', 'caching', 'parameter_reorder', 'data_structure', 'batch_processing')),
    exec_time_ms    INTEGER,
    memory_kb       INTEGER,
    test_pass_count INTEGER,
    test_total      INTEGER,
    composite_score TEXT,
    is_selected     INTEGER NOT NULL DEFAULT 0 CHECK(is_selected IN (0, 1)),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_erpclaw_dgm_variant_run
    ON erpclaw_dgm_variant(run_id);
CREATE INDEX IF NOT EXISTS idx_erpclaw_dgm_variant_module
    ON erpclaw_dgm_variant(module_name);
CREATE INDEX IF NOT EXISTS idx_erpclaw_dgm_variant_selected
    ON erpclaw_dgm_variant(is_selected);
"""


# ===========================================================================
# DATABASE INITIALIZATION
# ===========================================================================

# Ordered list of all DDL blocks. Order matters for foreign key dependencies.
ALL_DDL_BLOCKS = [
    ("erpclaw-setup",          SETUP_TABLES),
    ("erpclaw-gl",             GL_TABLES),
    ("erpclaw-journals",       JOURNALS_TABLES),
    ("erpclaw-payments",       PAYMENTS_TABLES),
    ("erpclaw-tax",            TAX_TABLES),
    ("erpclaw-selling",        SELLING_TABLES),
    ("erpclaw-buying",         BUYING_TABLES),
    ("erpclaw-inventory",      INVENTORY_TABLES),
    ("erpclaw-billing",        BILLING_TABLES),
    ("erpclaw-manufacturing",  MANUFACTURING_TABLES),
    ("erpclaw-hr",             HR_TABLES),
    ("erpclaw-payroll",        PAYROLL_TABLES),
    ("erpclaw-crm",            CRM_TABLES),
    ("erpclaw-projects",       PROJECTS_TABLES),
    ("erpclaw-assets",         ASSETS_TABLES),
    ("erpclaw-quality",        QUALITY_TABLES),
    ("erpclaw-support",        SUPPORT_TABLES),
    ("erpclaw-accounting-adv", ADVACCT_TABLES),
    ("erpclaw-registries",     REGISTRY_TABLES),
    ("erpclaw-modules",        MODULE_TABLES),
    ("erpclaw-os",             OS_TABLES),
]


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Initialize the ERPClaw database with all tables."""
    # Ensure the directory exists
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        # Enable WAL mode and foreign keys via centralized setup
        try:
            from erpclaw_lib.db import setup_pragmas
            setup_pragmas(conn)
        except ImportError:
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA busy_timeout = 5000")

        # Execute all DDL blocks in order
        for skill_name, ddl_sql in ALL_DDL_BLOCKS:
            conn.executescript(ddl_sql)
            # Register the schema version for each skill (idempotent)
            existing = conn.execute(
                "SELECT 1 FROM schema_version WHERE module = ?", (skill_name,)
            ).fetchone()
            if not existing:
                conn.execute(
                    """INSERT INTO schema_version (module, version, updated_at)
                       VALUES (?, 1, datetime('now'))""",
                    (skill_name,)
                )

        conn.commit()

        # Seed default roles
        import uuid
        DEFAULT_ROLES = [
            ("System Manager", "Full system access across all skills and companies", 1),
            ("Accounts Manager", "Full access to financial modules (GL, journals, payments, tax, reports)", 1),
            ("Accounts User", "Read access to financial modules, submit journal entries and payments", 1),
            ("Stock Manager", "Full access to inventory, buying, selling, manufacturing", 1),
            ("Stock User", "Read access to inventory, create stock entries and orders", 1),
            ("HR Manager", "Full access to HR, payroll, attendance, leave management", 1),
            ("HR User", "Read access to HR, mark attendance, apply for leave", 1),
            ("Sales Manager", "Full access to CRM, selling, customer management", 1),
            ("Sales User", "Read access to CRM and selling, create quotations and orders", 1),
            ("Purchase Manager", "Full access to buying, supplier management", 1),
            ("Purchase User", "Read access to buying, create purchase requests", 1),
            ("Analytics User", "Read-only access to reports, analytics, and dashboards", 1),
        ]
        for role_name, desc, is_sys in DEFAULT_ROLES:
            existing = conn.execute(
                "SELECT 1 FROM role WHERE name = ?", (role_name,)
            ).fetchone()
            if not existing:
                conn.execute(
                    """INSERT INTO role (id, name, description, is_system)
                       VALUES (?, ?, ?, ?)""",
                    (str(uuid.uuid4()), role_name, desc, is_sys)
                )
        conn.commit()

        # Verify: count tables
        cursor = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
        )
        table_count = cursor.fetchone()[0]

        cursor = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='index'"
        )
        index_count = cursor.fetchone()[0]

        print(f"ERPClaw database initialized successfully at: {db_path}", file=sys.stderr)
        print(f"  Tables created: {table_count}", file=sys.stderr)
        print(f"  Indexes created: {index_count}", file=sys.stderr)
        print(f"  Skills registered: {len(ALL_DDL_BLOCKS)}", file=sys.stderr)
        print(f"  Journal mode: WAL", file=sys.stderr)
        print(f"  Foreign keys: ON", file=sys.stderr)

    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize ERPClaw database")
    parser.add_argument(
        "--db-path",
        default=DEFAULT_DB_PATH,
        help=f"Path to SQLite database (default: {DEFAULT_DB_PATH})"
    )
    args = parser.parse_args()
    init_db(args.db_path)
