#!/usr/bin/env python3
"""ERPClaw Advanced Accounting schema extension -- adds ASC 606, ASC 842,
intercompany, and consolidation tables to the shared database.

12 tables: 4 revenue, 3 lease, 2 intercompany, 3 consolidation.

Prerequisite: ERPClaw init_db.py must have run first (creates foundation tables).
Run: python3 init_db.py [db_path]
"""
import os
import sqlite3
import sys

DEFAULT_DB_PATH = os.path.expanduser("~/.openclaw/erpclaw/data.sqlite")
DISPLAY_NAME = "ERPClaw Advanced Accounting"

REQUIRED_FOUNDATION = [
    "company", "naming_series", "audit_log",
]


def create_accounting_adv_tables(db_path=None):
    db_path = db_path or os.environ.get("ERPCLAW_DB_PATH", DEFAULT_DB_PATH)
    conn = sqlite3.connect(db_path)
    from erpclaw_lib.db import setup_pragmas
    setup_pragmas(conn)

    # -- Verify ERPClaw foundation --
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]
    missing = [t for t in REQUIRED_FOUNDATION if t not in tables]
    if missing:
        print(f"ERROR: Foundation tables missing: {', '.join(missing)}")
        print("Run erpclaw-setup first: clawhub install erpclaw-setup")
        conn.close()
        sys.exit(1)

    tables_created = 0
    indexes_created = 0

    # ==================================================================
    # DOMAIN 1: Revenue Recognition (ASC 606) -- 4 tables
    # ==================================================================

    # 1. advacct_revenue_contract
    conn.execute("""
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
        )
    """)
    tables_created += 1
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_rcon_company ON advacct_revenue_contract(company_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_rcon_status ON advacct_revenue_contract(contract_status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_rcon_customer ON advacct_revenue_contract(customer_name)")
    indexes_created += 3

    # 2. advacct_performance_obligation
    conn.execute("""
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
        )
    """)
    tables_created += 1
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_po_contract ON advacct_performance_obligation(contract_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_po_status ON advacct_performance_obligation(obligation_status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_po_company ON advacct_performance_obligation(company_id)")
    indexes_created += 3

    # 3. advacct_variable_consideration
    conn.execute("""
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
        )
    """)
    tables_created += 1
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_vc_contract ON advacct_variable_consideration(contract_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_vc_company ON advacct_variable_consideration(company_id)")
    indexes_created += 2

    # 4. advacct_revenue_schedule
    conn.execute("""
        CREATE TABLE IF NOT EXISTS advacct_revenue_schedule (
            id                  TEXT PRIMARY KEY,
            obligation_id       TEXT NOT NULL REFERENCES advacct_performance_obligation(id) ON DELETE CASCADE,
            period_date         TEXT NOT NULL,
            amount              TEXT NOT NULL DEFAULT '0',
            recognized          INTEGER NOT NULL DEFAULT 0,
            company_id          TEXT NOT NULL REFERENCES company(id),
            created_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    tables_created += 1
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_rs_obligation ON advacct_revenue_schedule(obligation_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_rs_period ON advacct_revenue_schedule(period_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_rs_company ON advacct_revenue_schedule(company_id)")
    indexes_created += 3

    # ==================================================================
    # DOMAIN 2: Lease Accounting (ASC 842) -- 3 tables
    # ==================================================================

    # 5. advacct_lease
    conn.execute("""
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
        )
    """)
    tables_created += 1
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_lease_company ON advacct_lease(company_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_lease_status ON advacct_lease(lease_status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_lease_type ON advacct_lease(lease_type)")
    indexes_created += 3

    # 6. advacct_lease_payment
    conn.execute("""
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
        )
    """)
    tables_created += 1
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_lpay_lease ON advacct_lease_payment(lease_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_lpay_date ON advacct_lease_payment(payment_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_lpay_status ON advacct_lease_payment(payment_status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_lpay_company ON advacct_lease_payment(company_id)")
    indexes_created += 4

    # 7. advacct_amortization_entry
    conn.execute("""
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
        )
    """)
    tables_created += 1
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_amort_lease ON advacct_amortization_entry(lease_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_amort_period ON advacct_amortization_entry(period_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_amort_company ON advacct_amortization_entry(company_id)")
    indexes_created += 3

    # ==================================================================
    # DOMAIN 3: Intercompany Transactions -- 2 tables
    # ==================================================================

    # 8. advacct_ic_transaction
    conn.execute("""
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
        )
    """)
    tables_created += 1
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_ict_from ON advacct_ic_transaction(from_company_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_ict_to ON advacct_ic_transaction(to_company_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_ict_status ON advacct_ic_transaction(ic_status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_ict_type ON advacct_ic_transaction(transaction_type)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_ict_company ON advacct_ic_transaction(company_id)")
    indexes_created += 5

    # 9. advacct_transfer_price_rule
    conn.execute("""
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
        )
    """)
    tables_created += 1
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_tpr_companies ON advacct_transfer_price_rule(from_company_id, to_company_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_tpr_type ON advacct_transfer_price_rule(transaction_type)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_tpr_company ON advacct_transfer_price_rule(company_id)")
    indexes_created += 3

    # ==================================================================
    # DOMAIN 4: Multi-Entity Consolidation -- 3 tables
    # ==================================================================

    # 10. advacct_consolidation_group
    conn.execute("""
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
        )
    """)
    tables_created += 1
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_cgrp_company ON advacct_consolidation_group(company_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_cgrp_status ON advacct_consolidation_group(group_status)")
    indexes_created += 2

    # 11. advacct_group_entity
    conn.execute("""
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
        )
    """)
    tables_created += 1
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_ge_group ON advacct_group_entity(group_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_ge_entity ON advacct_group_entity(entity_company_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_ge_company ON advacct_group_entity(company_id)")
    indexes_created += 3

    # 12. advacct_elimination_entry
    conn.execute("""
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
        )
    """)
    tables_created += 1
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_ee_group ON advacct_elimination_entry(group_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_ee_period ON advacct_elimination_entry(period_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_ee_type ON advacct_elimination_entry(entry_type)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_advacct_ee_company ON advacct_elimination_entry(company_id)")
    indexes_created += 4

    conn.commit()
    conn.close()

    return {
        "database": db_path,
        "tables": tables_created,
        "indexes": indexes_created,
    }


if __name__ == "__main__":
    db = sys.argv[1] if len(sys.argv) > 1 else None
    result = create_accounting_adv_tables(db)
    print(f"{DISPLAY_NAME} schema created in {result['database']}")
    print(f"  Tables: {result['tables']}")
    print(f"  Indexes: {result['indexes']}")
