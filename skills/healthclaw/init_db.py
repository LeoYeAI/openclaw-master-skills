#!/usr/bin/env python3
"""HealthClaw schema extension — adds domain tables to the shared database.

AI-native hospital and multi-department healthcare ERP.
35 tables across 7 domains: patients, appointments, clinical, billing,
inventory, lab, referrals.

Prerequisite: ERPClaw init_db.py must have run first (creates foundation tables).
Run: python3 init_db.py [db_path]
"""
import os
import sqlite3
import sys
import uuid


DEFAULT_DB_PATH = os.path.expanduser("~/.openclaw/erpclaw/data.sqlite")
DISPLAY_NAME = "HealthClaw"

# Foundation tables that must exist before HealthClaw can install
REQUIRED_FOUNDATION = [
    "company", "customer", "employee", "item", "account",
    "sales_invoice", "payment_entry", "gl_entry", "naming_series",
]


def create_healthclaw_tables(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON")

    # ── Verify ERPClaw foundation ────────────────────────────────
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]
    missing = [t for t in REQUIRED_FOUNDATION if t not in tables]
    if missing:
        print(f"ERROR: Foundation tables missing: {', '.join(missing)}")
        print("Run erpclaw first: clawhub install erpclaw", file=sys.stderr)
        conn.close()
        sys.exit(1)

    # ── Create all HealthClaw domain tables ──────────────────────
    conn.executescript("""
        -- ==========================================================
        -- HealthClaw Domain Tables
        -- 35 tables, 7 domains, healthclaw_ prefix
        -- Convention: TEXT for IDs (UUID4), TEXT for money (Decimal),
        --             TEXT for dates (ISO-8601)
        -- ==========================================================


        -- ==========================================================
        -- DOMAIN 1: PATIENTS (6 tables)
        -- ==========================================================

        -- Patient demographics — links to foundation customer (individual)
        CREATE TABLE IF NOT EXISTS healthclaw_patient (
            id              TEXT PRIMARY KEY,
            naming_series   TEXT,
            customer_id     TEXT REFERENCES customer(id) ON DELETE RESTRICT,
            first_name      TEXT NOT NULL,
            last_name       TEXT NOT NULL,
            full_name       TEXT NOT NULL,
            date_of_birth   TEXT NOT NULL,
            gender          TEXT NOT NULL CHECK(gender IN ('male','female','other','unknown')),
            ssn             TEXT,                -- encrypted, last-4 for display
            mrn             TEXT,                -- medical record number (auto from naming_series)
            marital_status  TEXT CHECK(marital_status IN ('single','married','divorced','widowed','separated','unknown')),
            race            TEXT,
            ethnicity       TEXT CHECK(ethnicity IN ('hispanic_latino','not_hispanic_latino','unknown')),
            preferred_language TEXT NOT NULL DEFAULT 'English',
            primary_phone   TEXT,
            secondary_phone TEXT,
            email           TEXT,
            address_line1   TEXT,
            address_line2   TEXT,
            city            TEXT,
            state           TEXT,
            zip_code        TEXT,
            primary_provider_id TEXT REFERENCES employee(id) ON DELETE RESTRICT,
            status          TEXT NOT NULL DEFAULT 'active'
                            CHECK(status IN ('active','inactive','deceased')),
            notes           TEXT,
            company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_patient_company
            ON healthclaw_patient(company_id);
        CREATE INDEX IF NOT EXISTS idx_hc_patient_customer
            ON healthclaw_patient(customer_id);
        CREATE INDEX IF NOT EXISTS idx_hc_patient_provider
            ON healthclaw_patient(primary_provider_id);
        CREATE INDEX IF NOT EXISTS idx_hc_patient_status
            ON healthclaw_patient(status);
        CREATE INDEX IF NOT EXISTS idx_hc_patient_dob
            ON healthclaw_patient(date_of_birth);
        CREATE INDEX IF NOT EXISTS idx_hc_patient_name
            ON healthclaw_patient(last_name, first_name);

        -- Patient insurance coverage
        CREATE TABLE IF NOT EXISTS healthclaw_patient_insurance (
            id              TEXT PRIMARY KEY,
            naming_series   TEXT,
            patient_id      TEXT NOT NULL REFERENCES healthclaw_patient(id) ON DELETE RESTRICT,
            insurance_type  TEXT NOT NULL CHECK(insurance_type IN ('primary','secondary','tertiary')),
            payer_name      TEXT NOT NULL,
            payer_id        TEXT,                -- payer identifier / EDI ID
            plan_name       TEXT,
            plan_type       TEXT CHECK(plan_type IN ('hmo','ppo','epo','pos','hdhp','medicare','medicaid','tricare','workers_comp','self_pay','other')),
            group_number    TEXT,
            member_id       TEXT NOT NULL,
            subscriber_name TEXT,
            subscriber_dob  TEXT,
            subscriber_relationship TEXT NOT NULL DEFAULT 'self'
                            CHECK(subscriber_relationship IN ('self','spouse','child','other')),
            copay_amount    TEXT NOT NULL DEFAULT '0',
            deductible      TEXT NOT NULL DEFAULT '0',
            deductible_met  TEXT NOT NULL DEFAULT '0',
            out_of_pocket_max TEXT NOT NULL DEFAULT '0',
            effective_date  TEXT NOT NULL,
            termination_date TEXT,
            preauth_required INTEGER NOT NULL DEFAULT 0 CHECK(preauth_required IN (0,1)),
            status          TEXT NOT NULL DEFAULT 'active'
                            CHECK(status IN ('active','inactive','expired','terminated')),
            company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_ins_patient
            ON healthclaw_patient_insurance(patient_id);
        CREATE INDEX IF NOT EXISTS idx_hc_ins_type
            ON healthclaw_patient_insurance(insurance_type);
        CREATE INDEX IF NOT EXISTS idx_hc_ins_status
            ON healthclaw_patient_insurance(status);

        -- Patient allergies
        CREATE TABLE IF NOT EXISTS healthclaw_allergy (
            id              TEXT PRIMARY KEY,
            patient_id      TEXT NOT NULL REFERENCES healthclaw_patient(id) ON DELETE RESTRICT,
            allergen        TEXT NOT NULL,
            allergen_type   TEXT NOT NULL CHECK(allergen_type IN ('drug','food','environmental','other')),
            reaction        TEXT,
            severity        TEXT NOT NULL DEFAULT 'moderate'
                            CHECK(severity IN ('mild','moderate','severe','life_threatening')),
            onset_date      TEXT,
            status          TEXT NOT NULL DEFAULT 'active'
                            CHECK(status IN ('active','inactive','resolved')),
            noted_by_id     TEXT REFERENCES employee(id) ON DELETE RESTRICT,
            notes           TEXT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_allergy_patient
            ON healthclaw_allergy(patient_id);
        CREATE INDEX IF NOT EXISTS idx_hc_allergy_status
            ON healthclaw_allergy(status);

        -- Patient medical history
        CREATE TABLE IF NOT EXISTS healthclaw_medical_history (
            id              TEXT PRIMARY KEY,
            patient_id      TEXT NOT NULL REFERENCES healthclaw_patient(id) ON DELETE RESTRICT,
            condition       TEXT NOT NULL,
            icd10_code      TEXT,                -- ICD-10 code (text, no lookup table)
            diagnosis_date  TEXT,
            resolution_date TEXT,
            status          TEXT NOT NULL DEFAULT 'active'
                            CHECK(status IN ('active','resolved','chronic')),
            notes           TEXT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_medhist_patient
            ON healthclaw_medical_history(patient_id);
        CREATE INDEX IF NOT EXISTS idx_hc_medhist_status
            ON healthclaw_medical_history(status);

        -- Patient emergency/next-of-kin contacts
        CREATE TABLE IF NOT EXISTS healthclaw_patient_contact (
            id              TEXT PRIMARY KEY,
            patient_id      TEXT NOT NULL REFERENCES healthclaw_patient(id) ON DELETE RESTRICT,
            contact_type    TEXT NOT NULL CHECK(contact_type IN ('emergency','next_of_kin','guardian','power_of_attorney','other')),
            name            TEXT NOT NULL,
            relationship    TEXT,
            phone           TEXT,
            email           TEXT,
            address         TEXT,
            is_primary      INTEGER NOT NULL DEFAULT 0 CHECK(is_primary IN (0,1)),
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_pcontact_patient
            ON healthclaw_patient_contact(patient_id);

        -- HIPAA / treatment consent tracking
        CREATE TABLE IF NOT EXISTS healthclaw_consent (
            id              TEXT PRIMARY KEY,
            patient_id      TEXT NOT NULL REFERENCES healthclaw_patient(id) ON DELETE RESTRICT,
            consent_type    TEXT NOT NULL CHECK(consent_type IN (
                'hipaa_privacy','treatment','surgery','anesthesia',
                'research','telehealth','photo_video','release_of_info','other'
            )),
            description     TEXT,
            granted_date    TEXT NOT NULL,
            expiration_date TEXT,
            revoked_date    TEXT,
            status          TEXT NOT NULL DEFAULT 'active'
                            CHECK(status IN ('active','expired','revoked')),
            witness_name    TEXT,
            obtained_by_id  TEXT REFERENCES employee(id) ON DELETE RESTRICT,
            notes           TEXT,
            company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_consent_patient
            ON healthclaw_consent(patient_id);
        CREATE INDEX IF NOT EXISTS idx_hc_consent_type
            ON healthclaw_consent(consent_type);
        CREATE INDEX IF NOT EXISTS idx_hc_consent_status
            ON healthclaw_consent(status);


        -- ==========================================================
        -- DOMAIN 2: APPOINTMENTS (5 tables)
        -- ==========================================================

        -- Provider weekly availability template
        CREATE TABLE IF NOT EXISTS healthclaw_provider_schedule (
            id              TEXT PRIMARY KEY,
            provider_id     TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
            day_of_week     INTEGER NOT NULL CHECK(day_of_week BETWEEN 0 AND 6),  -- 0=Mon, 6=Sun
            start_time      TEXT NOT NULL,       -- HH:MM (24h)
            end_time        TEXT NOT NULL,        -- HH:MM (24h)
            slot_duration   INTEGER NOT NULL DEFAULT 30,  -- minutes
            location        TEXT,                -- room, office, clinic name
            status          TEXT NOT NULL DEFAULT 'active'
                            CHECK(status IN ('active','inactive')),
            company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_provsched_provider
            ON healthclaw_provider_schedule(provider_id);
        CREATE INDEX IF NOT EXISTS idx_hc_provsched_day
            ON healthclaw_provider_schedule(day_of_week);

        -- Schedule block (vacation, meeting, override to block slots)
        CREATE TABLE IF NOT EXISTS healthclaw_schedule_block (
            id              TEXT PRIMARY KEY,
            provider_id     TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
            block_date      TEXT NOT NULL,
            start_time      TEXT,                -- NULL = all day
            end_time        TEXT,
            reason          TEXT NOT NULL CHECK(reason IN ('vacation','meeting','personal','maintenance','holiday','other')),
            notes           TEXT,
            company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_schedblock_provider
            ON healthclaw_schedule_block(provider_id);
        CREATE INDEX IF NOT EXISTS idx_hc_schedblock_date
            ON healthclaw_schedule_block(block_date);

        -- Appointments
        CREATE TABLE IF NOT EXISTS healthclaw_appointment (
            id              TEXT PRIMARY KEY,
            naming_series   TEXT,
            patient_id      TEXT NOT NULL REFERENCES healthclaw_patient(id) ON DELETE RESTRICT,
            provider_id     TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
            appointment_date TEXT NOT NULL,
            start_time      TEXT NOT NULL,        -- HH:MM
            end_time        TEXT NOT NULL,         -- HH:MM
            duration_minutes INTEGER NOT NULL DEFAULT 30,
            appointment_type TEXT NOT NULL DEFAULT 'follow_up'
                            CHECK(appointment_type IN (
                                'new_patient','follow_up','urgent','walk_in',
                                'telehealth','procedure','physical_exam','consultation'
                            )),
            chief_complaint TEXT,
            location        TEXT,
            status          TEXT NOT NULL DEFAULT 'scheduled'
                            CHECK(status IN ('scheduled','confirmed','checked_in','in_progress',
                                             'completed','cancelled','no_show','rescheduled')),
            cancellation_reason TEXT,
            check_in_time   TEXT,
            check_out_time  TEXT,
            notes           TEXT,
            company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_appt_company
            ON healthclaw_appointment(company_id);
        CREATE INDEX IF NOT EXISTS idx_hc_appt_patient
            ON healthclaw_appointment(patient_id);
        CREATE INDEX IF NOT EXISTS idx_hc_appt_provider
            ON healthclaw_appointment(provider_id);
        CREATE INDEX IF NOT EXISTS idx_hc_appt_date
            ON healthclaw_appointment(appointment_date);
        CREATE INDEX IF NOT EXISTS idx_hc_appt_status
            ON healthclaw_appointment(status);
        CREATE INDEX IF NOT EXISTS idx_hc_appt_type
            ON healthclaw_appointment(appointment_type);

        -- Appointment reminders
        CREATE TABLE IF NOT EXISTS healthclaw_appointment_reminder (
            id              TEXT PRIMARY KEY,
            appointment_id  TEXT NOT NULL REFERENCES healthclaw_appointment(id) ON DELETE RESTRICT,
            reminder_type   TEXT NOT NULL CHECK(reminder_type IN ('sms','email','phone','in_app')),
            scheduled_at    TEXT NOT NULL,
            sent_at         TEXT,
            status          TEXT NOT NULL DEFAULT 'pending'
                            CHECK(status IN ('pending','sent','failed','cancelled')),
            created_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_reminder_appt
            ON healthclaw_appointment_reminder(appointment_id);
        CREATE INDEX IF NOT EXISTS idx_hc_reminder_status
            ON healthclaw_appointment_reminder(status);

        -- Waitlist for appointment slots
        CREATE TABLE IF NOT EXISTS healthclaw_waitlist (
            id              TEXT PRIMARY KEY,
            patient_id      TEXT NOT NULL REFERENCES healthclaw_patient(id) ON DELETE RESTRICT,
            provider_id     TEXT REFERENCES employee(id) ON DELETE RESTRICT,
            preferred_date_start TEXT,
            preferred_date_end   TEXT,
            preferred_time_start TEXT,
            preferred_time_end   TEXT,
            appointment_type TEXT NOT NULL DEFAULT 'follow_up',
            priority        TEXT NOT NULL DEFAULT 'normal'
                            CHECK(priority IN ('low','normal','high','urgent')),
            status          TEXT NOT NULL DEFAULT 'waiting'
                            CHECK(status IN ('waiting','offered','accepted','expired','cancelled')),
            notes           TEXT,
            company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_waitlist_patient
            ON healthclaw_waitlist(patient_id);
        CREATE INDEX IF NOT EXISTS idx_hc_waitlist_provider
            ON healthclaw_waitlist(provider_id);
        CREATE INDEX IF NOT EXISTS idx_hc_waitlist_status
            ON healthclaw_waitlist(status);
        CREATE INDEX IF NOT EXISTS idx_hc_waitlist_priority
            ON healthclaw_waitlist(priority);


        -- ==========================================================
        -- DOMAIN 3: CLINICAL (7 tables)
        -- ==========================================================

        -- Encounter — clinical visit record (hub for all clinical data)
        CREATE TABLE IF NOT EXISTS healthclaw_encounter (
            id              TEXT PRIMARY KEY,
            naming_series   TEXT,
            patient_id      TEXT NOT NULL REFERENCES healthclaw_patient(id) ON DELETE RESTRICT,
            appointment_id  TEXT REFERENCES healthclaw_appointment(id) ON DELETE RESTRICT,
            provider_id     TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
            encounter_date  TEXT NOT NULL,
            encounter_type  TEXT NOT NULL DEFAULT 'outpatient'
                            CHECK(encounter_type IN (
                                'outpatient','inpatient','emergency','observation',
                                'telehealth','home_visit'
                            )),
            chief_complaint TEXT,
            department      TEXT,
            room            TEXT,
            admission_date  TEXT,
            discharge_date  TEXT,
            discharge_disposition TEXT,
            status          TEXT NOT NULL DEFAULT 'open'
                            CHECK(status IN ('open','in_progress','completed','cancelled')),
            notes           TEXT,
            company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_encounter_company
            ON healthclaw_encounter(company_id);
        CREATE INDEX IF NOT EXISTS idx_hc_encounter_patient
            ON healthclaw_encounter(patient_id);
        CREATE INDEX IF NOT EXISTS idx_hc_encounter_appt
            ON healthclaw_encounter(appointment_id);
        CREATE INDEX IF NOT EXISTS idx_hc_encounter_provider
            ON healthclaw_encounter(provider_id);
        CREATE INDEX IF NOT EXISTS idx_hc_encounter_date
            ON healthclaw_encounter(encounter_date);
        CREATE INDEX IF NOT EXISTS idx_hc_encounter_status
            ON healthclaw_encounter(status);
        CREATE INDEX IF NOT EXISTS idx_hc_encounter_type
            ON healthclaw_encounter(encounter_type);

        -- Vital signs recording
        CREATE TABLE IF NOT EXISTS healthclaw_vitals (
            id              TEXT PRIMARY KEY,
            encounter_id    TEXT NOT NULL REFERENCES healthclaw_encounter(id) ON DELETE RESTRICT,
            patient_id      TEXT NOT NULL REFERENCES healthclaw_patient(id) ON DELETE RESTRICT,
            recorded_by_id  TEXT REFERENCES employee(id) ON DELETE RESTRICT,
            recorded_at     TEXT NOT NULL DEFAULT (datetime('now')),
            temperature     TEXT,           -- Fahrenheit
            temperature_site TEXT CHECK(temperature_site IN ('oral','tympanic','axillary','rectal','temporal')),
            heart_rate      INTEGER,        -- bpm
            respiratory_rate INTEGER,       -- breaths/min
            blood_pressure_systolic  INTEGER,
            blood_pressure_diastolic INTEGER,
            oxygen_saturation TEXT,         -- percentage
            weight          TEXT,           -- lbs
            height          TEXT,           -- inches
            bmi             TEXT,           -- calculated
            pain_level      INTEGER CHECK(pain_level BETWEEN 0 AND 10),
            notes           TEXT,
            created_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_vitals_encounter
            ON healthclaw_vitals(encounter_id);
        CREATE INDEX IF NOT EXISTS idx_hc_vitals_patient
            ON healthclaw_vitals(patient_id);

        -- Diagnosis (ICD-10 codes stored as text)
        CREATE TABLE IF NOT EXISTS healthclaw_diagnosis (
            id              TEXT PRIMARY KEY,
            encounter_id    TEXT NOT NULL REFERENCES healthclaw_encounter(id) ON DELETE RESTRICT,
            patient_id      TEXT NOT NULL REFERENCES healthclaw_patient(id) ON DELETE RESTRICT,
            icd10_code      TEXT NOT NULL,
            description     TEXT NOT NULL,
            diagnosis_type  TEXT NOT NULL DEFAULT 'primary'
                            CHECK(diagnosis_type IN ('primary','secondary','admitting','discharge','rule_out')),
            status          TEXT NOT NULL DEFAULT 'active'
                            CHECK(status IN ('active','resolved','chronic','rule_out')),
            onset_date      TEXT,
            diagnosed_by_id TEXT REFERENCES employee(id) ON DELETE RESTRICT,
            notes           TEXT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_dx_encounter
            ON healthclaw_diagnosis(encounter_id);
        CREATE INDEX IF NOT EXISTS idx_hc_dx_patient
            ON healthclaw_diagnosis(patient_id);
        CREATE INDEX IF NOT EXISTS idx_hc_dx_icd10
            ON healthclaw_diagnosis(icd10_code);
        CREATE INDEX IF NOT EXISTS idx_hc_dx_type
            ON healthclaw_diagnosis(diagnosis_type);

        -- Prescription (medication orders)
        CREATE TABLE IF NOT EXISTS healthclaw_prescription (
            id              TEXT PRIMARY KEY,
            naming_series   TEXT,
            encounter_id    TEXT NOT NULL REFERENCES healthclaw_encounter(id) ON DELETE RESTRICT,
            patient_id      TEXT NOT NULL REFERENCES healthclaw_patient(id) ON DELETE RESTRICT,
            prescriber_id   TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
            medication_name TEXT NOT NULL,
            ndc_code        TEXT,            -- National Drug Code
            dosage          TEXT NOT NULL,    -- e.g., "500mg"
            frequency       TEXT NOT NULL,    -- e.g., "BID", "Q8H", "PRN"
            route           TEXT NOT NULL DEFAULT 'oral'
                            CHECK(route IN ('oral','iv','im','subq','topical','inhaled',
                                           'rectal','ophthalmic','otic','nasal','sublingual','transdermal','other')),
            quantity        TEXT NOT NULL DEFAULT '0',
            refills         INTEGER NOT NULL DEFAULT 0,
            daw             INTEGER NOT NULL DEFAULT 0 CHECK(daw IN (0,1)),  -- dispense as written
            start_date      TEXT NOT NULL,
            end_date        TEXT,
            diagnosis_id    TEXT REFERENCES healthclaw_diagnosis(id) ON DELETE RESTRICT,
            controlled_schedule TEXT CHECK(controlled_schedule IN ('II','III','IV','V')),
            pharmacy_notes  TEXT,
            status          TEXT NOT NULL DEFAULT 'active'
                            CHECK(status IN ('active','completed','discontinued','cancelled','on_hold')),
            discontinued_reason TEXT,
            notes           TEXT,
            company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_rx_encounter
            ON healthclaw_prescription(encounter_id);
        CREATE INDEX IF NOT EXISTS idx_hc_rx_patient
            ON healthclaw_prescription(patient_id);
        CREATE INDEX IF NOT EXISTS idx_hc_rx_prescriber
            ON healthclaw_prescription(prescriber_id);
        CREATE INDEX IF NOT EXISTS idx_hc_rx_status
            ON healthclaw_prescription(status);

        -- Procedures performed (CPT codes stored as text)
        CREATE TABLE IF NOT EXISTS healthclaw_procedure (
            id              TEXT PRIMARY KEY,
            naming_series   TEXT,
            encounter_id    TEXT NOT NULL REFERENCES healthclaw_encounter(id) ON DELETE RESTRICT,
            patient_id      TEXT NOT NULL REFERENCES healthclaw_patient(id) ON DELETE RESTRICT,
            provider_id     TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
            cpt_code        TEXT NOT NULL,
            description     TEXT NOT NULL,
            procedure_date  TEXT NOT NULL,
            start_time      TEXT,
            end_time        TEXT,
            modifiers       TEXT,            -- CPT modifiers (e.g., "25,59")
            diagnosis_ids   TEXT,            -- JSON array of diagnosis IDs (linking Dx to procedure)
            anesthesia_type TEXT CHECK(anesthesia_type IN ('none','local','regional','general','sedation')),
            body_site       TEXT,
            laterality      TEXT CHECK(laterality IN ('left','right','bilateral','not_applicable')),
            status          TEXT NOT NULL DEFAULT 'completed'
                            CHECK(status IN ('planned','in_progress','completed','cancelled')),
            notes           TEXT,
            company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_proc_encounter
            ON healthclaw_procedure(encounter_id);
        CREATE INDEX IF NOT EXISTS idx_hc_proc_patient
            ON healthclaw_procedure(patient_id);
        CREATE INDEX IF NOT EXISTS idx_hc_proc_provider
            ON healthclaw_procedure(provider_id);
        CREATE INDEX IF NOT EXISTS idx_hc_proc_cpt
            ON healthclaw_procedure(cpt_code);
        CREATE INDEX IF NOT EXISTS idx_hc_proc_date
            ON healthclaw_procedure(procedure_date);

        -- SOAP / clinical notes
        CREATE TABLE IF NOT EXISTS healthclaw_clinical_note (
            id              TEXT PRIMARY KEY,
            encounter_id    TEXT NOT NULL REFERENCES healthclaw_encounter(id) ON DELETE RESTRICT,
            patient_id      TEXT NOT NULL REFERENCES healthclaw_patient(id) ON DELETE RESTRICT,
            author_id       TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
            note_type       TEXT NOT NULL DEFAULT 'progress'
                            CHECK(note_type IN ('progress','soap','hpi','consultation',
                                               'discharge','operative','procedure','nursing','other')),
            subjective      TEXT,            -- SOAP: S
            objective       TEXT,            -- SOAP: O
            assessment      TEXT,            -- SOAP: A
            plan            TEXT,            -- SOAP: P
            body            TEXT,            -- free-text for non-SOAP notes
            addendum        TEXT,
            signed_at       TEXT,
            cosigner_id     TEXT REFERENCES employee(id) ON DELETE RESTRICT,
            cosigned_at     TEXT,
            status          TEXT NOT NULL DEFAULT 'draft'
                            CHECK(status IN ('draft','signed','cosigned','amended','addended')),
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_note_encounter
            ON healthclaw_clinical_note(encounter_id);
        CREATE INDEX IF NOT EXISTS idx_hc_note_patient
            ON healthclaw_clinical_note(patient_id);
        CREATE INDEX IF NOT EXISTS idx_hc_note_author
            ON healthclaw_clinical_note(author_id);
        CREATE INDEX IF NOT EXISTS idx_hc_note_type
            ON healthclaw_clinical_note(note_type);

        -- Clinical orders (labs, imaging, referrals — generic order hub)
        CREATE TABLE IF NOT EXISTS healthclaw_order (
            id              TEXT PRIMARY KEY,
            naming_series   TEXT,
            encounter_id    TEXT NOT NULL REFERENCES healthclaw_encounter(id) ON DELETE RESTRICT,
            patient_id      TEXT NOT NULL REFERENCES healthclaw_patient(id) ON DELETE RESTRICT,
            ordering_provider_id TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
            order_type      TEXT NOT NULL CHECK(order_type IN ('lab','imaging','referral','procedure','other')),
            order_date      TEXT NOT NULL,
            priority        TEXT NOT NULL DEFAULT 'routine'
                            CHECK(priority IN ('stat','urgent','routine','elective')),
            clinical_indication TEXT,
            diagnosis_id    TEXT REFERENCES healthclaw_diagnosis(id) ON DELETE RESTRICT,
            status          TEXT NOT NULL DEFAULT 'pending'
                            CHECK(status IN ('pending','in_progress','completed','cancelled')),
            notes           TEXT,
            company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_order_encounter
            ON healthclaw_order(encounter_id);
        CREATE INDEX IF NOT EXISTS idx_hc_order_patient
            ON healthclaw_order(patient_id);
        CREATE INDEX IF NOT EXISTS idx_hc_order_provider
            ON healthclaw_order(ordering_provider_id);
        CREATE INDEX IF NOT EXISTS idx_hc_order_type
            ON healthclaw_order(order_type);
        CREATE INDEX IF NOT EXISTS idx_hc_order_status
            ON healthclaw_order(status);
        CREATE INDEX IF NOT EXISTS idx_hc_order_date
            ON healthclaw_order(order_date);


        -- ==========================================================
        -- DOMAIN 4: BILLING (6 tables)
        -- ==========================================================

        -- Fee schedule header (e.g., "Medicare Fee Schedule 2026")
        CREATE TABLE IF NOT EXISTS healthclaw_fee_schedule (
            id              TEXT PRIMARY KEY,
            name            TEXT NOT NULL,
            description     TEXT,
            payer_type      TEXT CHECK(payer_type IN ('commercial','medicare','medicaid','self_pay','workers_comp','other')),
            effective_date  TEXT NOT NULL,
            expiration_date TEXT,
            status          TEXT NOT NULL DEFAULT 'active'
                            CHECK(status IN ('active','inactive','expired')),
            company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_feesched_company
            ON healthclaw_fee_schedule(company_id);
        CREATE INDEX IF NOT EXISTS idx_hc_feesched_status
            ON healthclaw_fee_schedule(status);

        -- Fee schedule line items (CPT code → price)
        CREATE TABLE IF NOT EXISTS healthclaw_fee_schedule_item (
            id              TEXT PRIMARY KEY,
            fee_schedule_id TEXT NOT NULL REFERENCES healthclaw_fee_schedule(id) ON DELETE RESTRICT,
            cpt_code        TEXT NOT NULL,
            description     TEXT,
            standard_charge TEXT NOT NULL DEFAULT '0',
            allowed_amount  TEXT NOT NULL DEFAULT '0',   -- payer's max allowable
            unit_count      INTEGER NOT NULL DEFAULT 1,
            modifier        TEXT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now')),
            UNIQUE(fee_schedule_id, cpt_code, modifier)
        );
        CREATE INDEX IF NOT EXISTS idx_hc_fsitem_schedule
            ON healthclaw_fee_schedule_item(fee_schedule_id);
        CREATE INDEX IF NOT EXISTS idx_hc_fsitem_cpt
            ON healthclaw_fee_schedule_item(cpt_code);

        -- Individual charges (line items billed for services)
        CREATE TABLE IF NOT EXISTS healthclaw_charge (
            id              TEXT PRIMARY KEY,
            naming_series   TEXT,
            encounter_id    TEXT NOT NULL REFERENCES healthclaw_encounter(id) ON DELETE RESTRICT,
            patient_id      TEXT NOT NULL REFERENCES healthclaw_patient(id) ON DELETE RESTRICT,
            procedure_id    TEXT REFERENCES healthclaw_procedure(id) ON DELETE RESTRICT,
            cpt_code        TEXT NOT NULL,
            modifiers       TEXT,
            diagnosis_ids   TEXT,            -- JSON array of ICD-10 pointers
            units           INTEGER NOT NULL DEFAULT 1,
            charge_amount   TEXT NOT NULL DEFAULT '0',
            allowed_amount  TEXT NOT NULL DEFAULT '0',
            fee_schedule_id TEXT REFERENCES healthclaw_fee_schedule(id) ON DELETE RESTRICT,
            service_date    TEXT NOT NULL,
            provider_id     TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
            place_of_service TEXT NOT NULL DEFAULT '11',  -- CMS POS code (11=Office)
            status          TEXT NOT NULL DEFAULT 'unbilled'
                            CHECK(status IN ('unbilled','billed','paid','adjusted','void')),
            notes           TEXT,
            company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_charge_company
            ON healthclaw_charge(company_id);
        CREATE INDEX IF NOT EXISTS idx_hc_charge_encounter
            ON healthclaw_charge(encounter_id);
        CREATE INDEX IF NOT EXISTS idx_hc_charge_patient
            ON healthclaw_charge(patient_id);
        CREATE INDEX IF NOT EXISTS idx_hc_charge_status
            ON healthclaw_charge(status);
        CREATE INDEX IF NOT EXISTS idx_hc_charge_date
            ON healthclaw_charge(service_date);
        CREATE INDEX IF NOT EXISTS idx_hc_charge_cpt
            ON healthclaw_charge(cpt_code);

        -- Insurance claim header
        CREATE TABLE IF NOT EXISTS healthclaw_claim (
            id              TEXT PRIMARY KEY,
            naming_series   TEXT,
            patient_id      TEXT NOT NULL REFERENCES healthclaw_patient(id) ON DELETE RESTRICT,
            insurance_id    TEXT NOT NULL REFERENCES healthclaw_patient_insurance(id) ON DELETE RESTRICT,
            encounter_id    TEXT NOT NULL REFERENCES healthclaw_encounter(id) ON DELETE RESTRICT,
            claim_date      TEXT NOT NULL,
            total_charge    TEXT NOT NULL DEFAULT '0',
            total_allowed   TEXT NOT NULL DEFAULT '0',
            total_paid      TEXT NOT NULL DEFAULT '0',
            patient_responsibility TEXT NOT NULL DEFAULT '0',
            adjustment_amount TEXT NOT NULL DEFAULT '0',
            billing_provider_id TEXT REFERENCES employee(id) ON DELETE RESTRICT,
            rendering_provider_id TEXT REFERENCES employee(id) ON DELETE RESTRICT,
            place_of_service TEXT NOT NULL DEFAULT '11',
            claim_type      TEXT NOT NULL DEFAULT 'professional'
                            CHECK(claim_type IN ('professional','institutional','dental')),
            filing_indicator TEXT,           -- e.g., "CI" for commercial insurance
            prior_auth_id   TEXT REFERENCES healthclaw_prior_auth(id) ON DELETE RESTRICT,
            sales_invoice_id TEXT REFERENCES sales_invoice(id) ON DELETE RESTRICT,
            status          TEXT NOT NULL DEFAULT 'draft'
                            CHECK(status IN ('draft','submitted','accepted','denied',
                                             'partially_paid','paid','appealed','void')),
            denial_reason   TEXT,
            appeal_deadline TEXT,
            notes           TEXT,
            company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_claim_company
            ON healthclaw_claim(company_id);
        CREATE INDEX IF NOT EXISTS idx_hc_claim_patient
            ON healthclaw_claim(patient_id);
        CREATE INDEX IF NOT EXISTS idx_hc_claim_insurance
            ON healthclaw_claim(insurance_id);
        CREATE INDEX IF NOT EXISTS idx_hc_claim_encounter
            ON healthclaw_claim(encounter_id);
        CREATE INDEX IF NOT EXISTS idx_hc_claim_status
            ON healthclaw_claim(status);
        CREATE INDEX IF NOT EXISTS idx_hc_claim_date
            ON healthclaw_claim(claim_date);
        CREATE INDEX IF NOT EXISTS idx_hc_claim_invoice
            ON healthclaw_claim(sales_invoice_id);

        -- Claim line items
        CREATE TABLE IF NOT EXISTS healthclaw_claim_line (
            id              TEXT PRIMARY KEY,
            claim_id        TEXT NOT NULL REFERENCES healthclaw_claim(id) ON DELETE RESTRICT,
            charge_id       TEXT NOT NULL REFERENCES healthclaw_charge(id) ON DELETE RESTRICT,
            line_number     INTEGER NOT NULL,
            cpt_code        TEXT NOT NULL,
            modifiers       TEXT,
            diagnosis_pointers TEXT,         -- e.g., "1,2" referencing claim-level Dx list
            units           INTEGER NOT NULL DEFAULT 1,
            charge_amount   TEXT NOT NULL DEFAULT '0',
            allowed_amount  TEXT NOT NULL DEFAULT '0',
            paid_amount     TEXT NOT NULL DEFAULT '0',
            adjustment_amount TEXT NOT NULL DEFAULT '0',
            patient_amount  TEXT NOT NULL DEFAULT '0',
            denial_reason   TEXT,
            remark_codes    TEXT,            -- ANSI remark codes
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_claimline_claim
            ON healthclaw_claim_line(claim_id);
        CREATE INDEX IF NOT EXISTS idx_hc_claimline_charge
            ON healthclaw_claim_line(charge_id);

        -- Insurance / patient payment posting
        CREATE TABLE IF NOT EXISTS healthclaw_payment_posting (
            id              TEXT PRIMARY KEY,
            claim_id        TEXT REFERENCES healthclaw_claim(id) ON DELETE RESTRICT,
            patient_id      TEXT NOT NULL REFERENCES healthclaw_patient(id) ON DELETE RESTRICT,
            posting_type    TEXT NOT NULL CHECK(posting_type IN ('insurance_payment','patient_payment','adjustment','refund','write_off')),
            posting_date    TEXT NOT NULL,
            amount          TEXT NOT NULL DEFAULT '0',
            check_number    TEXT,
            payer_name      TEXT,
            payment_method  TEXT CHECK(payment_method IN ('check','eft','cash','credit_card','ach','other')),
            payment_entry_id TEXT REFERENCES payment_entry(id) ON DELETE RESTRICT,
            eob_date        TEXT,            -- explanation of benefits date
            notes           TEXT,
            company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_posting_claim
            ON healthclaw_payment_posting(claim_id);
        CREATE INDEX IF NOT EXISTS idx_hc_posting_patient
            ON healthclaw_payment_posting(patient_id);
        CREATE INDEX IF NOT EXISTS idx_hc_posting_type
            ON healthclaw_payment_posting(posting_type);
        CREATE INDEX IF NOT EXISTS idx_hc_posting_date
            ON healthclaw_payment_posting(posting_date);
        CREATE INDEX IF NOT EXISTS idx_hc_posting_payment
            ON healthclaw_payment_posting(payment_entry_id);


        -- ==========================================================
        -- DOMAIN 5: INVENTORY / PHARMACY (3 tables)
        -- ==========================================================

        -- Drug formulary header
        CREATE TABLE IF NOT EXISTS healthclaw_formulary (
            id              TEXT PRIMARY KEY,
            name            TEXT NOT NULL,
            description     TEXT,
            effective_date  TEXT NOT NULL,
            expiration_date TEXT,
            status          TEXT NOT NULL DEFAULT 'active'
                            CHECK(status IN ('active','inactive','expired')),
            company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_formulary_company
            ON healthclaw_formulary(company_id);
        CREATE INDEX IF NOT EXISTS idx_hc_formulary_status
            ON healthclaw_formulary(status);

        -- Formulary items (extends ERPClaw item with NDC, controlled schedule)
        CREATE TABLE IF NOT EXISTS healthclaw_formulary_item (
            id              TEXT PRIMARY KEY,
            formulary_id    TEXT NOT NULL REFERENCES healthclaw_formulary(id) ON DELETE RESTRICT,
            item_id         TEXT NOT NULL REFERENCES item(id) ON DELETE RESTRICT,
            ndc_code        TEXT,            -- National Drug Code
            drug_class      TEXT,
            generic_name    TEXT,
            brand_name      TEXT,
            strength        TEXT,            -- e.g., "500mg"
            dosage_form     TEXT,            -- e.g., "tablet", "capsule", "injection"
            route           TEXT,
            controlled_schedule TEXT CHECK(controlled_schedule IN ('II','III','IV','V')),
            therapeutic_class TEXT,
            formulary_tier  TEXT CHECK(formulary_tier IN ('1','2','3','4','specialty')),
            requires_prior_auth INTEGER NOT NULL DEFAULT 0 CHECK(requires_prior_auth IN (0,1)),
            max_daily_dose  TEXT,
            status          TEXT NOT NULL DEFAULT 'active'
                            CHECK(status IN ('active','inactive','recalled')),
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now')),
            UNIQUE(formulary_id, item_id)
        );
        CREATE INDEX IF NOT EXISTS idx_hc_fitem_formulary
            ON healthclaw_formulary_item(formulary_id);
        CREATE INDEX IF NOT EXISTS idx_hc_fitem_item
            ON healthclaw_formulary_item(item_id);
        CREATE INDEX IF NOT EXISTS idx_hc_fitem_ndc
            ON healthclaw_formulary_item(ndc_code);

        -- Medication dispensing record
        CREATE TABLE IF NOT EXISTS healthclaw_dispensing (
            id              TEXT PRIMARY KEY,
            naming_series   TEXT,
            prescription_id TEXT NOT NULL REFERENCES healthclaw_prescription(id) ON DELETE RESTRICT,
            patient_id      TEXT NOT NULL REFERENCES healthclaw_patient(id) ON DELETE RESTRICT,
            formulary_item_id TEXT REFERENCES healthclaw_formulary_item(id) ON DELETE RESTRICT,
            item_id         TEXT REFERENCES item(id) ON DELETE RESTRICT,
            dispensed_by_id TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
            dispensed_date  TEXT NOT NULL,
            quantity        TEXT NOT NULL DEFAULT '0',
            lot_number      TEXT,
            expiration_date TEXT,
            ndc_code        TEXT,
            directions      TEXT,
            refill_number   INTEGER NOT NULL DEFAULT 0,
            status          TEXT NOT NULL DEFAULT 'dispensed'
                            CHECK(status IN ('dispensed','returned','recalled','voided')),
            notes           TEXT,
            company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_disp_rx
            ON healthclaw_dispensing(prescription_id);
        CREATE INDEX IF NOT EXISTS idx_hc_disp_patient
            ON healthclaw_dispensing(patient_id);
        CREATE INDEX IF NOT EXISTS idx_hc_disp_date
            ON healthclaw_dispensing(dispensed_date);
        CREATE INDEX IF NOT EXISTS idx_hc_disp_item
            ON healthclaw_dispensing(item_id);


        -- ==========================================================
        -- DOMAIN 6: LAB / DIAGNOSTICS (5 tables)
        -- ==========================================================

        -- Lab order header
        CREATE TABLE IF NOT EXISTS healthclaw_lab_order (
            id              TEXT PRIMARY KEY,
            naming_series   TEXT,
            order_id        TEXT REFERENCES healthclaw_order(id) ON DELETE RESTRICT,
            encounter_id    TEXT NOT NULL REFERENCES healthclaw_encounter(id) ON DELETE RESTRICT,
            patient_id      TEXT NOT NULL REFERENCES healthclaw_patient(id) ON DELETE RESTRICT,
            ordering_provider_id TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
            order_date      TEXT NOT NULL,
            priority        TEXT NOT NULL DEFAULT 'routine'
                            CHECK(priority IN ('stat','urgent','routine')),
            fasting_required INTEGER NOT NULL DEFAULT 0 CHECK(fasting_required IN (0,1)),
            clinical_indication TEXT,
            specimen_type   TEXT,            -- e.g., "blood", "urine", "tissue"
            collection_date TEXT,
            received_date   TEXT,
            status          TEXT NOT NULL DEFAULT 'ordered'
                            CHECK(status IN ('ordered','collected','received','in_progress',
                                             'completed','cancelled')),
            notes           TEXT,
            company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_labord_company
            ON healthclaw_lab_order(company_id);
        CREATE INDEX IF NOT EXISTS idx_hc_labord_encounter
            ON healthclaw_lab_order(encounter_id);
        CREATE INDEX IF NOT EXISTS idx_hc_labord_patient
            ON healthclaw_lab_order(patient_id);
        CREATE INDEX IF NOT EXISTS idx_hc_labord_provider
            ON healthclaw_lab_order(ordering_provider_id);
        CREATE INDEX IF NOT EXISTS idx_hc_labord_status
            ON healthclaw_lab_order(status);
        CREATE INDEX IF NOT EXISTS idx_hc_labord_date
            ON healthclaw_lab_order(order_date);

        -- Individual lab tests within an order
        CREATE TABLE IF NOT EXISTS healthclaw_lab_test (
            id              TEXT PRIMARY KEY,
            lab_order_id    TEXT NOT NULL REFERENCES healthclaw_lab_order(id) ON DELETE RESTRICT,
            test_code       TEXT NOT NULL,    -- LOINC or internal code
            test_name       TEXT NOT NULL,
            cpt_code        TEXT,
            status          TEXT NOT NULL DEFAULT 'pending'
                            CHECK(status IN ('pending','in_progress','completed','cancelled')),
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_labtest_order
            ON healthclaw_lab_test(lab_order_id);
        CREATE INDEX IF NOT EXISTS idx_hc_labtest_code
            ON healthclaw_lab_test(test_code);

        -- Lab test results
        CREATE TABLE IF NOT EXISTS healthclaw_lab_result (
            id              TEXT PRIMARY KEY,
            lab_test_id     TEXT NOT NULL REFERENCES healthclaw_lab_test(id) ON DELETE RESTRICT,
            component_name  TEXT NOT NULL,    -- e.g., "Hemoglobin", "WBC"
            value           TEXT NOT NULL,
            unit            TEXT,             -- e.g., "g/dL", "cells/mcL"
            reference_low   TEXT,
            reference_high  TEXT,
            flag            TEXT CHECK(flag IN ('normal','low','high','critical_low','critical_high','abnormal')),
            result_date     TEXT NOT NULL,
            performed_by_id TEXT REFERENCES employee(id) ON DELETE RESTRICT,
            verified_by_id  TEXT REFERENCES employee(id) ON DELETE RESTRICT,
            notes           TEXT,
            created_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_labres_test
            ON healthclaw_lab_result(lab_test_id);
        CREATE INDEX IF NOT EXISTS idx_hc_labres_flag
            ON healthclaw_lab_result(flag);

        -- Imaging / radiology order
        CREATE TABLE IF NOT EXISTS healthclaw_imaging_order (
            id              TEXT PRIMARY KEY,
            naming_series   TEXT,
            order_id        TEXT REFERENCES healthclaw_order(id) ON DELETE RESTRICT,
            encounter_id    TEXT NOT NULL REFERENCES healthclaw_encounter(id) ON DELETE RESTRICT,
            patient_id      TEXT NOT NULL REFERENCES healthclaw_patient(id) ON DELETE RESTRICT,
            ordering_provider_id TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
            modality        TEXT NOT NULL CHECK(modality IN (
                'xray','ct','mri','ultrasound','mammography',
                'fluoroscopy','nuclear','pet','dexa','other'
            )),
            body_part       TEXT NOT NULL,
            laterality      TEXT CHECK(laterality IN ('left','right','bilateral','not_applicable')),
            cpt_code        TEXT,
            order_date      TEXT NOT NULL,
            priority        TEXT NOT NULL DEFAULT 'routine'
                            CHECK(priority IN ('stat','urgent','routine')),
            clinical_indication TEXT,
            contrast        INTEGER NOT NULL DEFAULT 0 CHECK(contrast IN (0,1)),
            status          TEXT NOT NULL DEFAULT 'ordered'
                            CHECK(status IN ('ordered','scheduled','in_progress','completed',
                                             'read','cancelled')),
            scheduled_date  TEXT,
            notes           TEXT,
            company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_imgord_company
            ON healthclaw_imaging_order(company_id);
        CREATE INDEX IF NOT EXISTS idx_hc_imgord_encounter
            ON healthclaw_imaging_order(encounter_id);
        CREATE INDEX IF NOT EXISTS idx_hc_imgord_patient
            ON healthclaw_imaging_order(patient_id);
        CREATE INDEX IF NOT EXISTS idx_hc_imgord_modality
            ON healthclaw_imaging_order(modality);
        CREATE INDEX IF NOT EXISTS idx_hc_imgord_status
            ON healthclaw_imaging_order(status);

        -- Imaging results / radiology report
        CREATE TABLE IF NOT EXISTS healthclaw_imaging_result (
            id              TEXT PRIMARY KEY,
            imaging_order_id TEXT NOT NULL REFERENCES healthclaw_imaging_order(id) ON DELETE RESTRICT,
            radiologist_id  TEXT REFERENCES employee(id) ON DELETE RESTRICT,
            findings        TEXT,
            impression      TEXT,
            recommendation  TEXT,
            critical_finding INTEGER NOT NULL DEFAULT 0 CHECK(critical_finding IN (0,1)),
            report_date     TEXT NOT NULL,
            status          TEXT NOT NULL DEFAULT 'preliminary'
                            CHECK(status IN ('preliminary','final','addended','corrected')),
            addendum        TEXT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_imgres_order
            ON healthclaw_imaging_result(imaging_order_id);
        CREATE INDEX IF NOT EXISTS idx_hc_imgres_radiologist
            ON healthclaw_imaging_result(radiologist_id);
        CREATE INDEX IF NOT EXISTS idx_hc_imgres_status
            ON healthclaw_imaging_result(status);


        -- ==========================================================
        -- DOMAIN 7: REFERRALS / PRIOR AUTH (3 tables)
        -- ==========================================================

        -- Patient referral
        CREATE TABLE IF NOT EXISTS healthclaw_referral (
            id              TEXT PRIMARY KEY,
            naming_series   TEXT,
            patient_id      TEXT NOT NULL REFERENCES healthclaw_patient(id) ON DELETE RESTRICT,
            encounter_id    TEXT REFERENCES healthclaw_encounter(id) ON DELETE RESTRICT,
            referring_provider_id TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
            referred_to_provider TEXT NOT NULL,   -- external provider name (may not be in employee table)
            referred_to_specialty TEXT,
            referred_to_facility TEXT,
            referred_to_phone TEXT,
            referred_to_fax TEXT,
            referral_date   TEXT NOT NULL,
            expiration_date TEXT,
            reason          TEXT NOT NULL,
            diagnosis_id    TEXT REFERENCES healthclaw_diagnosis(id) ON DELETE RESTRICT,
            priority        TEXT NOT NULL DEFAULT 'routine'
                            CHECK(priority IN ('stat','urgent','routine','elective')),
            insurance_id    TEXT REFERENCES healthclaw_patient_insurance(id) ON DELETE RESTRICT,
            prior_auth_required INTEGER NOT NULL DEFAULT 0 CHECK(prior_auth_required IN (0,1)),
            prior_auth_id   TEXT REFERENCES healthclaw_prior_auth(id) ON DELETE RESTRICT,
            status          TEXT NOT NULL DEFAULT 'pending'
                            CHECK(status IN ('pending','sent','accepted','declined',
                                             'completed','expired','cancelled')),
            notes           TEXT,
            company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_ref_company
            ON healthclaw_referral(company_id);
        CREATE INDEX IF NOT EXISTS idx_hc_ref_patient
            ON healthclaw_referral(patient_id);
        CREATE INDEX IF NOT EXISTS idx_hc_ref_encounter
            ON healthclaw_referral(encounter_id);
        CREATE INDEX IF NOT EXISTS idx_hc_ref_referring
            ON healthclaw_referral(referring_provider_id);
        CREATE INDEX IF NOT EXISTS idx_hc_ref_status
            ON healthclaw_referral(status);
        CREATE INDEX IF NOT EXISTS idx_hc_ref_date
            ON healthclaw_referral(referral_date);

        -- Prior authorization request
        CREATE TABLE IF NOT EXISTS healthclaw_prior_auth (
            id              TEXT PRIMARY KEY,
            naming_series   TEXT,
            patient_id      TEXT NOT NULL REFERENCES healthclaw_patient(id) ON DELETE RESTRICT,
            insurance_id    TEXT NOT NULL REFERENCES healthclaw_patient_insurance(id) ON DELETE RESTRICT,
            requesting_provider_id TEXT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
            auth_number     TEXT,            -- payer-assigned auth number
            service_type    TEXT NOT NULL CHECK(service_type IN (
                'procedure','imaging','medication','dme','inpatient',
                'outpatient','referral','therapy','other'
            )),
            cpt_codes       TEXT,            -- JSON array of CPT codes
            icd10_codes     TEXT,            -- JSON array of ICD-10 codes
            description     TEXT NOT NULL,
            units_requested INTEGER NOT NULL DEFAULT 1,
            units_approved  INTEGER,
            request_date    TEXT NOT NULL,
            effective_date  TEXT,
            expiration_date TEXT,
            decision_date   TEXT,
            status          TEXT NOT NULL DEFAULT 'pending'
                            CHECK(status IN ('pending','approved','denied','partially_approved',
                                             'expired','cancelled','appealed')),
            denial_reason   TEXT,
            appeal_deadline TEXT,
            notes           TEXT,
            company_id      TEXT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_auth_company
            ON healthclaw_prior_auth(company_id);
        CREATE INDEX IF NOT EXISTS idx_hc_auth_patient
            ON healthclaw_prior_auth(patient_id);
        CREATE INDEX IF NOT EXISTS idx_hc_auth_insurance
            ON healthclaw_prior_auth(insurance_id);
        CREATE INDEX IF NOT EXISTS idx_hc_auth_status
            ON healthclaw_prior_auth(status);
        CREATE INDEX IF NOT EXISTS idx_hc_auth_number
            ON healthclaw_prior_auth(auth_number);
        CREATE INDEX IF NOT EXISTS idx_hc_auth_dates
            ON healthclaw_prior_auth(effective_date, expiration_date);

        -- Authorization usage tracking (tracks visits/units used against an auth)
        CREATE TABLE IF NOT EXISTS healthclaw_auth_usage (
            id              TEXT PRIMARY KEY,
            prior_auth_id   TEXT NOT NULL REFERENCES healthclaw_prior_auth(id) ON DELETE RESTRICT,
            encounter_id    TEXT REFERENCES healthclaw_encounter(id) ON DELETE RESTRICT,
            claim_id        TEXT REFERENCES healthclaw_claim(id) ON DELETE RESTRICT,
            usage_date      TEXT NOT NULL,
            units_used      INTEGER NOT NULL DEFAULT 1,
            notes           TEXT,
            created_at      TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_hc_authuse_auth
            ON healthclaw_auth_usage(prior_auth_id);
        CREATE INDEX IF NOT EXISTS idx_hc_authuse_encounter
            ON healthclaw_auth_usage(encounter_id);
    """)

    # ── Register naming series for all existing companies ────────
    companies = conn.execute("SELECT id FROM company").fetchall()
    naming_series = [
        ("healthclaw_patient",         "PAT"),
        ("healthclaw_patient_insurance", "INS"),
        ("healthclaw_appointment",     "APPT"),
        ("healthclaw_encounter",       "ENC"),
        ("healthclaw_prescription",    "RX"),
        ("healthclaw_procedure",       "PROC"),
        ("healthclaw_order",           "ORD"),
        ("healthclaw_charge",          "CHG"),
        ("healthclaw_claim",           "CLM"),
        ("healthclaw_dispensing",      "DISP"),
        ("healthclaw_lab_order",       "LAB"),
        ("healthclaw_imaging_order",   "IMG"),
        ("healthclaw_referral",        "REF"),
        ("healthclaw_prior_auth",      "AUTH"),
    ]
    for company_row in companies:
        company_id = company_row[0]
        for entity_type, prefix in naming_series:
            conn.execute(
                "INSERT OR IGNORE INTO naming_series (id, entity_type, prefix, current_value, company_id) "
                "VALUES (?, ?, ?, 0, ?)",
                (str(uuid.uuid4()), entity_type, prefix, company_id)
            )

    conn.commit()

    # ── Verify table creation ────────────────────────────────────
    tables_after = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'healthclaw_%'"
    ).fetchall()]
    indexes_after = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_hc_%'"
    ).fetchall()]

    conn.close()
    print(f"{DISPLAY_NAME} schema created in {db_path}", file=sys.stderr)
    print(f"  Tables: {len(tables_after)}", file=sys.stderr)
    print(f"  Indexes: {len(indexes_after)}", file=sys.stderr)
    print(f"  Naming series: {len(naming_series)} per company ({len(companies)} companies)", file=sys.stderr)


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DB_PATH
    parent = os.path.dirname(db_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    create_healthclaw_tables(db_path)
