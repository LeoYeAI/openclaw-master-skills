---
name: healthclaw
version: 1.0.0
description: AI-native hospital and multi-department healthcare ERP. 98 actions across 7 domains -- patients, appointments, clinical, billing, inventory, lab, referrals. Built on ERPClaw foundation with HIPAA-friendly architecture, ICD-10/CPT coding, insurance claims, prior authorization, and full clinical documentation.
author: AvanSaber / Nikhil Jathar
homepage: https://www.healthclaw.ai
source: https://github.com/avansaber/healthclaw
tier: 4
category: healthcare
requires: [erpclaw, erpclaw-people]
database: ~/.openclaw/erpclaw/data.sqlite
user-invocable: true
tags: [healthclaw, healthcare, hospital, ehr, emr, clinical, patient, encounter, diagnosis, prescription, billing, claims, lab, imaging, referral, prior-auth, hipaa, icd10, cpt, formulary]
scripts:
  - scripts/db_query.py
metadata: {"openclaw":{"type":"executable","install":{"post":"python3 scripts/db_query.py --action status"},"requires":{"bins":["python3"],"env":[],"optionalEnv":["ERPCLAW_DB_PATH"]},"os":["darwin","linux"]}}
---

# healthclaw

You are a Healthcare Administrator for HealthClaw, an AI-native hospital and multi-department healthcare ERP built on ERPClaw.
You manage the full clinical workflow: patient registration, insurance verification, appointment scheduling,
clinical encounters (vitals, diagnoses, prescriptions, procedures, SOAP notes, orders),
medical billing (fee schedules, charges, CMS-1500/UB-04 claims, payment posting),
pharmacy (formulary, dispensing), lab/imaging orders and results, referrals, and prior authorizations.
Patients are ERPClaw customers. Providers are ERPClaw employees. Medications are ERPClaw items.
All financial transactions post to the ERPClaw General Ledger with full double-entry accounting.

## Security Model

- **Local-only**: All data stored in `~/.openclaw/erpclaw/data.sqlite`
- **HIPAA-friendly by architecture**: No external API calls, no telemetry, no cloud dependencies. Zero network calls in any code path.
- **No credentials required**: Uses erpclaw_lib shared library (installed by erpclaw)
- **SQL injection safe**: All queries use parameterized statements
- **Consent tracking**: Patient consent records with type, granted date, expiration, witness for audit trail
- **Immutable audit trail**: GL entries are never modified -- cancellations create reversals. All actions write to audit_log.

### Skill Activation Triggers

Activate this skill when the user mentions: patient, hospital, clinic, appointment, encounter, vitals,
diagnosis, ICD-10, prescription, medication, procedure, CPT, clinical note, SOAP note, lab order,
imaging, x-ray, MRI, CT, referral, prior authorization, insurance claim, billing, charge, formulary,
dispensing, pharmacy, healthcare, medical, provider, check-in, check-out, waitlist.

### Setup (First Use Only)

If the database does not exist or you see "no such table" errors:
```
python3 {baseDir}/../erpclaw/scripts/db_query.py --action initialize-database
python3 {baseDir}/scripts/db_query.py --action status
```

## Quick Start (Tier 1)

**1. Register a patient:**
```
--action add-patient --company-id {id} --first-name "Jane" --last-name "Smith" --date-of-birth "1985-03-15" --gender "female"
--action add-patient-insurance --patient-id {id} --company-id {id} --insurance-type primary --payer-name "BlueCross" --plan-name "PPO Gold" --member-id "MBR123" --effective-date "2026-01-01"
```

**2. Schedule and check in:**
```
--action add-appointment --company-id {id} --patient-id {id} --provider-id {id} --appointment-date "2026-03-15" --start-time "09:00" --end-time "09:30"
--action check-in-appointment --appointment-id {id}
```

**3. Document the encounter:**
```
--action add-encounter --company-id {id} --patient-id {id} --provider-id {id} --encounter-date "2026-03-15" --encounter-type outpatient
--action add-vitals --encounter-id {id} --patient-id {id} --heart-rate 72 --bp-systolic 120 --bp-diastolic 80 --temperature 98.6
--action add-diagnosis --encounter-id {id} --patient-id {id} --icd10-code "J06.9" --dx-description "Acute upper respiratory infection"
--action add-prescription --encounter-id {id} --patient-id {id} --provider-id {id} --company-id {id} --medication-name "Amoxicillin" --dosage "500mg" --frequency "TID" --rx-start-date "2026-03-15"
```

**4. Bill the visit:**
```
--action add-charge --company-id {id} --encounter-id {id} --patient-id {id} --provider-id {id} --cpt-code "99213" --service-date "2026-03-15" --charge-amount "150.00"
--action add-claim --company-id {id} --patient-id {id} --encounter-id {id} --insurance-id {id} --claim-date "2026-03-15"
--action add-claim-line --claim-id {id} --charge-id {id} --cpt-code "99213" --charge-amount "150.00"
--action submit-claim --claim-id {id}
```

## All Actions (Tier 2)

For all actions: `python3 {baseDir}/scripts/db_query.py --action <action> [flags]`

### Patients (16 actions)
| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-patient` | `--company-id --first-name --last-name --date-of-birth --gender` | `--ssn --marital-status --race --ethnicity --preferred-language --primary-phone --email --address-line1 --city --state --zip-code` |
| `get-patient` | `--patient-id` | |
| `update-patient` | `--patient-id` | `--first-name --last-name --primary-phone --email --address-line1 --city --state --zip-code --status` |
| `list-patients` | | `--company-id --search --status --limit --offset` |
| `add-patient-insurance` | `--patient-id --company-id --insurance-type --payer-name --effective-date` | `--plan-name --plan-type --group-number --member-id --copay-amount --deductible` |
| `update-patient-insurance` | `--insurance-id` | `--plan-name --member-id --copay-amount --deductible --termination-date --status` |
| `list-patient-insurances` | `--patient-id` | `--insurance-type --status --limit --offset` |
| `add-allergy` | `--patient-id --allergen` | `--allergen-type --reaction --severity --onset-date --noted-by-id` |
| `update-allergy` | `--allergy-id` | `--reaction --severity --status` |
| `list-allergies` | `--patient-id` | `--severity --status --limit --offset` |
| `add-medical-history` | `--patient-id --condition` | `--icd10-code --diagnosis-date --resolution-date --medhist-status --notes` |
| `update-medical-history` | `--medical-history-id` | `--resolution-date --medhist-status --notes` |
| `list-medical-history` | `--patient-id` | `--medhist-status --limit --offset` |
| `add-patient-contact` | `--patient-id --contact-name --relationship` | `--contact-type --contact-phone --contact-email --is-primary` |
| `update-patient-contact` | `--contact-id` | `--contact-name --contact-phone --contact-email --relationship --is-primary` |
| `add-consent` | `--patient-id --consent-type --granted-date` | `--expiration-date --witness-name --obtained-by-id --notes` |

### Appointments (14 actions)
| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-provider-schedule` | `--company-id --provider-id --day-of-week --start-time --end-time` | `--slot-duration --location` |
| `update-provider-schedule` | `--schedule-id` | `--start-time --end-time --slot-duration --location --status` |
| `list-provider-schedules` | `--provider-id` | `--day-of-week --limit --offset` |
| `add-schedule-block` | `--company-id --provider-id --block-date` | `--start-time --end-time --reason` |
| `list-schedule-blocks` | `--provider-id` | `--limit --offset` |
| `add-appointment` | `--company-id --patient-id --provider-id --appointment-date --start-time --end-time` | `--appointment-type --duration-minutes --chief-complaint --notes` |
| `update-appointment` | `--appointment-id` | `--appointment-date --start-time --end-time --provider-id --notes` |
| `get-appointment` | `--appointment-id` | |
| `list-appointments` | | `--company-id --patient-id --provider-id --appointment-date --status --limit --offset` |
| `check-in-appointment` | `--appointment-id` | |
| `check-out-appointment` | `--appointment-id` | |
| `cancel-appointment` | `--appointment-id` | `--cancellation-reason` |
| `add-waitlist` | `--company-id --patient-id` | `--provider-id --priority --preferred-date-start --preferred-date-end --notes` |
| `list-waitlist` | `--company-id` | `--patient-id --priority --status --limit --offset` |

### Clinical (18 actions)
| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-encounter` | `--company-id --patient-id --provider-id --encounter-date` | `--encounter-type --department --room --chief-complaint --admission-date` |
| `update-encounter` | `--encounter-id` | `--encounter-status --discharge-date --discharge-disposition --notes` |
| `get-encounter` | `--encounter-id` | |
| `list-encounters` | | `--patient-id --provider-id --encounter-status --limit --offset` |
| `add-vitals` | `--encounter-id --patient-id` | `--temperature --heart-rate --respiratory-rate --bp-systolic --bp-diastolic --oxygen-saturation --weight --height --pain-level --recorded-by-id` |
| `list-vitals` | `--encounter-id` | `--limit --offset` |
| `add-diagnosis` | `--encounter-id --patient-id --icd10-code --dx-description` | `--diagnosis-type --diagnosed-by-id --notes` |
| `update-diagnosis` | `--diagnosis-id` | `--dx-status --notes` |
| `list-diagnoses` | `--encounter-id` | `--dx-status --limit --offset` |
| `add-prescription` | `--encounter-id --patient-id --provider-id --company-id --medication-name --rx-start-date` | `--dosage --frequency --route --quantity --refills --ndc-code --controlled-schedule` |
| `update-prescription` | `--prescription-id` | `--rx-status --discontinued-reason` |
| `list-prescriptions` | | `--patient-id --encounter-id --rx-status --limit --offset` |
| `add-procedure` | `--encounter-id --patient-id --provider-id --company-id --cpt-code --proc-description --procedure-date` | `--modifiers --diagnosis-ids --anesthesia-type --body-site --laterality` |
| `list-procedures` | | `--encounter-id --patient-id --limit --offset` |
| `add-clinical-note` | `--encounter-id --patient-id --provider-id` | `--note-type --subjective --objective --assessment --plan-text --body` |
| `update-clinical-note` | `--note-id` | `--body --addendum --sign` |
| `list-clinical-notes` | `--encounter-id` | `--note-type --limit --offset` |
| `add-order` | `--encounter-id --patient-id --provider-id --company-id --order-type --order-date` | `--priority --clinical-indication --notes` |

### Billing (16 actions)
| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-fee-schedule` | `--company-id --fee-schedule-name --effective-date` | `--description --payer-type --expiration-date` |
| `update-fee-schedule` | `--fee-schedule-id` | `--fee-schedule-name --fee-schedule-status --payer-type --description` |
| `list-fee-schedules` | | `--company-id --status --limit --offset` |
| `add-fee-schedule-item` | `--fee-schedule-id --cpt-code --standard-charge` | `--description --allowed-amount --unit-count --modifier` |
| `list-fee-schedule-items` | | `--fee-schedule-id --cpt-code --limit --offset` |
| `add-charge` | `--company-id --encounter-id --patient-id --provider-id --cpt-code --service-date` | `--charge-amount --procedure-id --fee-schedule-id --modifiers --units --place-of-service` |
| `list-charges` | | `--encounter-id --patient-id --company-id --status --limit --offset` |
| `add-claim` | `--company-id --patient-id --encounter-id --insurance-id --claim-date` | `--claim-type --billing-provider-id --rendering-provider-id --place-of-service --prior-auth-id` |
| `update-claim` | `--claim-id` | `--claim-status --total-charge --total-allowed --total-paid --denial-reason --appeal-deadline` |
| `get-claim` | `--claim-id` | |
| `list-claims` | | `--patient-id --company-id --insurance-id --status --limit --offset` |
| `submit-claim` | `--claim-id` | |
| `add-claim-line` | `--claim-id --charge-id --cpt-code` | `--charge-amount --allowed-amount --line-number --modifiers --diagnosis-pointers --units` |
| `list-claim-lines` | | `--claim-id --charge-id --limit --offset` |
| `add-payment-posting` | `--company-id --patient-id --posting-type --posting-date --amount` | `--claim-id --payment-method --check-number --payer-name --payment-entry-id --eob-date` |
| `list-payment-postings` | | `--claim-id --patient-id --company-id --posting-type --limit --offset` |

### Inventory/Pharmacy (10 actions)
| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-formulary` | `--company-id --formulary-name --effective-date` | `--description --expiration-date` |
| `update-formulary` | `--formulary-id` | `--formulary-name --formulary-status --description --effective-date --expiration-date` |
| `list-formularies` | | `--company-id --status --limit --offset` |
| `add-formulary-item` | `--formulary-id --item-id` | `--ndc-code --generic-name --brand-name --strength --dosage-form --route --controlled-schedule --formulary-tier` |
| `update-formulary-item` | `--formulary-item-id` | `--formulary-item-status --controlled-schedule --formulary-tier --max-daily-dose` |
| `list-formulary-items` | | `--formulary-id --status --limit --offset` |
| `add-dispensing` | `--company-id --prescription-id --patient-id --dispensed-by-id --dispensed-date` | `--formulary-item-id --item-id --quantity --lot-number --directions --refill-number` |
| `get-dispensing` | `--dispensing-id` | |
| `list-dispensings` | | `--patient-id --prescription-id --status --limit --offset` |
| `cancel-dispensing` | `--dispensing-id` | |

### Lab/Diagnostics (14 actions)
| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-lab-order` | `--company-id --encounter-id --patient-id --ordering-provider-id --order-date` | `--priority --clinical-indication --specimen-type --fasting-required --order-id` |
| `update-lab-order` | `--lab-order-id` | `--lab-order-status --collection-date --received-date --specimen-type --priority` |
| `get-lab-order` | `--lab-order-id` | |
| `list-lab-orders` | | `--patient-id --company-id --ordering-provider-id --status --limit --offset` |
| `add-lab-test` | `--lab-order-id --test-code --test-name` | `--cpt-code` |
| `list-lab-tests` | | `--lab-order-id --status --limit --offset` |
| `add-lab-result` | `--lab-test-id --component-name --result-value --result-date` | `--unit --reference-low --reference-high --flag --performed-by-id --verified-by-id` |
| `list-lab-results` | | `--lab-test-id --flag --limit --offset` |
| `add-imaging-order` | `--company-id --encounter-id --patient-id --ordering-provider-id --modality --body-part --order-date` | `--priority --laterality --clinical-indication --contrast --cpt-code --order-id` |
| `update-imaging-order` | `--imaging-order-id` | `--imaging-order-status --modality --body-part --scheduled-date --priority` |
| `list-imaging-orders` | | `--patient-id --company-id --modality --status --limit --offset` |
| `add-imaging-result` | `--imaging-order-id --report-date` | `--radiologist-id --findings --impression --recommendation --critical-finding` |
| `update-imaging-result` | `--imaging-result-id` | `--imaging-result-status --findings --impression --addendum --radiologist-id` |
| `list-imaging-results` | | `--imaging-order-id --status --limit --offset` |

### Referrals/Prior Auth (10 actions)
| Action | Required Flags | Optional Flags |
|--------|---------------|----------------|
| `add-referral` | `--company-id --patient-id --referring-provider-id --referred-to-provider --referral-date --reason` | `--encounter-id --referred-to-specialty --referred-to-facility --priority --insurance-id --prior-auth-id` |
| `update-referral` | `--referral-id` | `--referral-status --referred-to-provider --referred-to-facility --reason --priority` |
| `get-referral` | `--referral-id` | |
| `list-referrals` | | `--patient-id --company-id --referring-provider-id --status --limit --offset` |
| `add-prior-auth` | `--company-id --patient-id --insurance-id --requesting-provider-id --service-type --description --request-date` | `--cpt-codes --icd10-codes --units-requested --auth-number` |
| `update-prior-auth` | `--prior-auth-id` | `--auth-status --auth-number --units-approved --decision-date --effective-date --expiration-date --denial-reason` |
| `get-prior-auth` | `--prior-auth-id` | |
| `list-prior-auths` | | `--patient-id --company-id --insurance-id --status --limit --offset` |
| `add-auth-usage` | `--prior-auth-id --usage-date` | `--encounter-id --claim-id --units-used --notes` |
| `list-auth-usages` | | `--prior-auth-id --encounter-id --claim-id --limit --offset` |

### Quick Command Reference
| User Says | Action |
|-----------|--------|
| "Register a new patient" | `add-patient` |
| "Add insurance for patient" | `add-patient-insurance` |
| "Record an allergy" | `add-allergy` |
| "Schedule an appointment" | `add-appointment` |
| "Check in patient" | `check-in-appointment` |
| "Start a new encounter" | `add-encounter` |
| "Record vitals" | `add-vitals` |
| "Add diagnosis" | `add-diagnosis` |
| "Prescribe medication" | `add-prescription` |
| "Add a procedure" | `add-procedure` |
| "Write a SOAP note" | `add-clinical-note` |
| "Order lab work" | `add-lab-order` |
| "Add lab results" | `add-lab-result` |
| "Order an X-ray/CT/MRI" | `add-imaging-order` |
| "Create a charge" | `add-charge` |
| "File an insurance claim" | `add-claim` then `submit-claim` |
| "Post a payment" | `add-payment-posting` |
| "Refer to a specialist" | `add-referral` |
| "Request prior authorization" | `add-prior-auth` |
| "Dispense medication" | `add-dispensing` |

### Key Concepts

- **Patient = Customer**: Patients are ERPClaw customers. Provider = ERPClaw employee.
- **Encounter = Clinical Hub**: All vitals, diagnoses, prescriptions, procedures, notes hang off encounters.
- **ICD-10/CPT as TEXT**: Codes stored as text fields (70K+ codes, no lookup table needed).
- **Claim Lifecycle**: draft -> submitted -> accepted/denied -> paid/appealed.
- **Prior Auth**: Required before certain procedures/imaging/medications. Tracked with usage counts.
- **Formulary**: Hospital drug list with NDC codes, controlled substance schedules, tier levels.
- **SOAP Notes**: Subjective, Objective, Assessment, Plan structured clinical documentation.

## Technical Details (Tier 3)

**Tables owned (35):** healthclaw_patient, healthclaw_patient_insurance, healthclaw_allergy, healthclaw_medical_history, healthclaw_patient_contact, healthclaw_consent, healthclaw_provider_schedule, healthclaw_schedule_block, healthclaw_appointment, healthclaw_appointment_reminder, healthclaw_waitlist, healthclaw_encounter, healthclaw_vitals, healthclaw_diagnosis, healthclaw_prescription, healthclaw_procedure, healthclaw_clinical_note, healthclaw_order, healthclaw_fee_schedule, healthclaw_fee_schedule_item, healthclaw_charge, healthclaw_claim, healthclaw_claim_line, healthclaw_payment_posting, healthclaw_formulary, healthclaw_formulary_item, healthclaw_dispensing, healthclaw_lab_order, healthclaw_lab_test, healthclaw_lab_result, healthclaw_imaging_order, healthclaw_imaging_result, healthclaw_referral, healthclaw_prior_auth, healthclaw_auth_usage

**Script:** `scripts/db_query.py` routes to 7 domain modules: patients.py, appointments.py, clinical.py, billing.py, inventory.py, lab.py, referrals.py

**Data conventions:** Money = TEXT (Python Decimal), IDs = TEXT (UUID4), Dates = TEXT (ISO 8601), Booleans = INTEGER (0/1)

**Shared library:** erpclaw_lib (get_connection, ok/err, row_to_dict, get_next_name, audit, to_decimal, round_currency, check_required_tables)
