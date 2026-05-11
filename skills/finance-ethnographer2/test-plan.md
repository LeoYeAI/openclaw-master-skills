# PF Ethnographer — Test Plan

Version: 1.0
Skill: `pf-ethnographer` + `pf-ethnographer/sanitizer`

---

## Test Suite Overview

| Suite | Area | Cases |
|---|---|---|
| S1 | PII Scrubbing | 6 |
| S2 | Finance Identifiers | 6 |
| S3 | Amounts and Balances | 5 |
| S4 | Crypto Wallet and Seed Phrase | 4 |
| S5 | No-New-Events Pulses | 3 |
| S6 | User Approval Gate | 5 |
| S7 | PF Classifier | 4 |
| S8 | Retention and Deletion | 3 |

---

## S1 — PII Scrubbing

### S1-1: Email Address Redaction

**Input to Sanitizer (raw_observed excerpt):**
```
The participant asked OpenClaw to draft an email to john.doe@example.com
regarding their account statement.
```

**Expected sanitized output:**
```
The participant asked OpenClaw to draft an email to [EMAIL_REDACTED]
regarding their account statement.
```

**Expected manifest:**
- `email.count = 1`
- `email.uncertainty_flags = 0`
- `risk_rating = med`

**Pass/fail:** Verify placeholder appears exactly once; original value absent.

---

### S1-2: Phone Number Redaction (US format)

**Input:**
```
User provided contact number (415) 555-0192 for verification purposes.
```

**Expected:**
```
User provided contact number [PHONE_REDACTED] for verification purposes.
```

**Expected manifest:** `phone.count = 1`, `risk_rating = med`

---

### S1-3: Phone Number Redaction (International format)

**Input:**
```
Participant mentioned calling their bank at +44 20 7946 0958.
```

**Expected:**
```
Participant mentioned calling their bank at [PHONE_REDACTED].
```

**Expected manifest:** `phone.count = 1`

---

### S1-4: Physical Address Redaction

**Input:**
```
The participant entered their mailing address as 742 Evergreen Terrace,
Springfield, IL 62701 for a mortgage pre-approval form.
```

**Expected:**
```
The participant entered their mailing address as [ADDRESS_REDACTED]
for a mortgage pre-approval form.
```

**Expected manifest:**
- `address.count = 1`
- `address.uncertainty_flags = 1` (heuristic detection flagged as uncertain)

---

### S1-5: Third-Party Person Name (over_redact = true)

**Input:**
```
The participant mentioned discussing their budget with Dr. Sarah Collins
and asked for a savings recommendation.
```

**Expected:**
```
The participant mentioned discussing their budget with [PERSON_NAME_REDACTED]
and asked for a savings recommendation.
```

**Expected manifest:**
- `person_name.count = 1`
- `person_name.uncertainty_flags = 1`

---

### S1-6: Third-Party Person Name Not Redacted (over_redact = false)

**Input:** Same as S1-5.
**Policy:** `over_redact = false`

**Expected:**
```
The participant mentioned discussing their budget with Dr. Sarah Collins
and asked for a savings recommendation.
```

**Expected manifest:** `person_name.count = 0`

**Rationale:** Pass 7 is skipped when `over_redact = false`.

---

## S2 — Finance Identifiers

### S2-1: Bank Account Number

**Input:**
```
Participant asked to verify their DDA account number 000123456789.
```

**Expected:**
```
Participant asked to verify their DDA account number [ACCOUNT_NUMBER_REDACTED].
```

**Expected manifest:** `account_number.count = 1`, `risk_rating = high`

---

### S2-2: US ABA Routing Number

**Input:**
```
The routing number for the transfer is 021000021.
```

**Expected:**
```
The routing number for the transfer is [ROUTING_NUMBER_REDACTED].
```

**Expected manifest:** `routing_number.count = 1`, `risk_rating = high`

---

### S2-3: IBAN

**Input:**
```
Participant initiated a transfer to IBAN DE89370400440532013000.
```

**Expected:**
```
Participant initiated a transfer to IBAN [IBAN_REDACTED].
```

**Expected manifest:** `iban.count = 1`, `risk_rating = high`

---

### S2-4: Credit Card Number (space-separated)

**Input:**
```
The participant entered card number 4111 1111 1111 1111 to check rewards points.
```

**Expected:**
```
The participant entered card number [CARD_NUMBER_REDACTED] to check rewards points.
```

**Expected manifest:** `card_number.count = 1`, `risk_rating = high`

---

### S2-5: Credit Card Number (compact)

**Input:**
```
Card used: 5500005555555559
```

**Expected:**
```
Card used: [CARD_NUMBER_REDACTED]
```

**Expected manifest:** `card_number.count = 1`

---

### S2-6: SWIFT Code

**Input:**
```
The participant asked for the SWIFT code DEUTDEDB for an international wire.
```

**Expected:**
```
The participant asked for the SWIFT code [SWIFT_REDACTED] for an international wire.
```

**Expected manifest:** `swift.count = 1`

---

## S3 — Amounts and Balances

### S3-1: Dollar Amount in Financial Context

**Input:**
```
Participant asked how to invest $12,500 in an index fund.
```

**Expected:**
```
Participant asked how to invest [AMOUNT_REDACTED] in an index fund.
```

**Expected manifest:** `amount_balance.count = 1`

---

### S3-2: APR Percentage

**Input:**
```
The participant asked about a loan with a 7.99% APR and whether to refinance.
```

**Expected:**
```
The participant asked about a loan with a [AMOUNT_REDACTED] APR and whether to refinance.
```

**Expected manifest:** `amount_balance.count = 1`

---

### S3-3: Non-Financial Count NOT Redacted

**Input:**
```
3 events were observed across 2 sessions in the last 7 days.
```

**Expected (unchanged):**
```
3 events were observed across 2 sessions in the last 7 days.
```

**Expected manifest:** `amount_balance.count = 0`

**Rationale:** Pure counts are not financial amounts.

---

### S3-4: Version Number NOT Redacted

**Input:**
```
Participant used OpenClaw v2.1.0 to review their portfolio.
```

**Expected (unchanged for version, amount redacted if present):**
```
Participant used OpenClaw v2.1.0 to review their portfolio.
```

**Expected manifest:** `amount_balance.count = 0`

---

### S3-5: Multiple Amounts in One Report

**Input:**
```
Participant set a $500/month savings goal and noted a $1,200 emergency expense.
They asked how to handle a $45.00 overdraft fee.
```

**Expected:**
```
Participant set a [AMOUNT_REDACTED] savings goal and noted a [AMOUNT_REDACTED] emergency expense.
They asked how to handle a [AMOUNT_REDACTED] overdraft fee.
```

**Expected manifest:** `amount_balance.count = 3`

---

## S4 — Crypto Wallet and Seed Phrase

### S4-1: Ethereum Wallet Address

**Input:**
```
Participant checked the balance of wallet 0xAbCdEf1234567890AbCdEf1234567890AbCdEf12.
```

**Expected:**
```
Participant checked the balance of wallet [CRYPTO_WALLET_REDACTED].
```

**Expected manifest:** `crypto_wallet.count = 1`

---

### S4-2: Bitcoin Bech32 Address

**Input:**
```
The participant sent funds to bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh.
```

**Expected:**
```
The participant sent funds to [CRYPTO_WALLET_REDACTED].
```

**Expected manifest:** `crypto_wallet.count = 1`

---

### S4-3: BIP-39 Seed Phrase — Full Segment Removal

**Input:**
```
The participant pasted their recovery phrase:
witch collapse practice feed shame open despair creek road again ice least

They then asked if it was safe to share.
```

**Expected:**
```
[SENSITIVE_SEGMENT_REMOVED — seed phrase or private key detected]

They then asked if it was safe to share.
```

**Expected manifest:**
- `seed_phrase_private_key.count = 1`
- `risk_rating = critical`

**Critical check:** The 12-word phrase must be entirely gone. No partial match. The
sentence after must be preserved. Sanitized report must begin with the CRITICAL warning.

---

### S4-4: Hex Private Key — Full Segment Removal

**Input:**
```
Participant typed their private key into the chat:
a8f5f167f44f4964e6c998dee62101e57c2b3f4a4b7b1d2e0e6f7a8b9c0d1e2f

They asked whether OpenClaw could store it securely.
```

**Expected:**
```
[SENSITIVE_SEGMENT_REMOVED — seed phrase or private key detected]

They asked whether OpenClaw could store it securely.
```

**Expected manifest:**
- `seed_phrase_private_key.count = 1`
- `risk_rating = critical`

---

## S5 — No-New-Events Pulses

### S5-1: Pulse with Zero Events — Silent Mode

**Setup:** `no_events_silent = true` in settings. Zero events since last pulse.

**Expected behavior:**
- No output presented to participant.
- state.json updated: `last_pulse_timestamp = now()`.
- A no-op record appended to reports (or state log).
- No Sanitizer call made (no reports to sanitize).

**Pass/fail:** Verify participant sees no pulse notification.

---

### S5-2: Pulse with Zero Events — Verbose Mode

**Setup:** `no_events_silent = false`. Zero events since last pulse.

**Expected output to participant:**
```
🔬 Research Pulse — 13:00 [date] (America/Los_Angeles)
No new events observed since [last_pulse_timestamp local]. Pulse recorded.
```

**Pass/fail:** Brief notification shown; no reports presented; no Sanitizer call.

---

### S5-3: Consecutive No-Event Pulses Do Not Stack

**Setup:** Three consecutive pulses (09:00, 13:00, 17:00) all with zero events.

**Expected:**
- Three separate `last_pulse_timestamp` updates.
- Three no-op records.
- `pulse_count` increments by 3 in state.json.
- No duplicate pulse output or stacked notifications.

---

## S6 — User Approval Gate

### S6-1: No Auto-Send Without Explicit Confirmation

**Setup:** `research_team_email` is configured. Pulse completes. User chooses [A].

**Expected flow:**
1. Ethnographer says: "I'll send the sanitized pulse package to [email]. Confirm?"
2. User has NOT responded yet.
3. Verify: email is NOT sent. State shows `pending_send = true` (or equivalent).
4. User responds with anything other than "yes"/"confirm"/"send it".
5. Verify: email is NOT sent.

**Pass/fail:** No send without explicit "yes" / "confirm" / "send it".

---

### S6-2: Send Fires Only After Explicit "Yes"

**Setup:** Same as S6-1. User responds "yes, send it."

**Expected:**
- Email composed with sanitized_observed.md + sanitized_interpretation.md + manifest.json.
- Email sent to configured recipient.
- Confirmation: "Sent to [email] at [timestamp]."

**Pass/fail:** Email sent exactly once; no duplicate sends.

---

### S6-3: Option [A] Hidden When No Email Configured

**Setup:** `research_team_email = null`.

**Expected:** Step 5 pulse presentation does NOT show option [A]. Only [B], [C], [D] shown.

**Pass/fail:** Verify [A] is absent from options.

---

### S6-4: Default Action is [D] (Save Locally Only)

**Setup:** Pulse completes. Participant closes OpenClaw without responding to pulse.

**Expected:** On next session start, state reflects: report saved, nothing sent.
Option [D] was implicitly applied.

**Pass/fail:** Report exists in reports directory; no email sent.

---

### S6-5: Re-Sanitize Flow ([C]) Does Not Send

**Setup:** User chooses [C]. Re-sanitization runs. Updated reports presented.

**Expected:**
- Sanitizer called again with stricter policy.
- Updated reports stored.
- Re-presented to user with same [A]/[B]/[C]/[D] options.
- No email sent during re-sanitization.

**Pass/fail:** Email not sent during or after [C] unless user explicitly approves [A].

---

## S7 — PF Classifier

### S7-1: Banking Event Scoring

**Observed behavior:** "The participant asked about moving funds between checking
and savings accounts, and inquired about ACH transfer timelines."

**Expected:**
- `pf_domain_tags = ["banking", "transfers"]`
- `pf_relevance_score >= 0.5` (two tags + financial action)
- `risk_sensitivity = med`

---

### S7-2: Crypto + High Risk

**Observed behavior:** "The participant asked about transferring ETH from a hardware
wallet to an exchange. A crypto address was present."

**Expected:**
- `pf_domain_tags = ["crypto"]`
- `pf_relevance_score >= 0.45`
- `risk_sensitivity = high`

---

### S7-3: Non-Finance Event

**Observed behavior:** "The participant asked OpenClaw to help write a Python
function for string parsing."

**Expected:**
- `pf_domain_tags = []`
- `pf_relevance_score = 0.0`
- `risk_sensitivity = low`
- Event should appear in "General Usage Events" section, NOT "Finance-Tagged Events".

---

### S7-4: Fraud-Security Tag

**Observed behavior:** "The participant reported an unauthorized charge on their
account and asked how to dispute it and freeze their credit."

**Expected:**
- `pf_domain_tags = ["fraud-security", "banking"]`
- `pf_relevance_score >= 0.65`
- `risk_sensitivity = high`

---

## S8 — Retention and Deletion

### S8-1: Auto-Purge After retention_days

**Setup:** `retention_days = 30`. Create synthetic events and reports dated 31 days ago.

**Expected after pulse:**
- Reports directory older than 30 days is deleted.
- events.jsonl entries older than 30 days are removed.
- finance_index.json is rebuilt and no longer contains purged entries.

---

### S8-2: Manual Delete by Date Range

**Command:** "Delete my research data from January 1 to January 15."

**Expected flow:**
1. Ethnographer lists events and report directories in range.
2. Presents count and date range for confirmation.
3. On "yes": deletes matching events.jsonl entries and report directories.
4. Rebuilds finance_index.json.
5. Confirms: "Deleted [N] events and [M] report directories from Jan 1–15."

**Pass/fail:** Verify no matching records remain; records outside range untouched.

---

### S8-3: Delete Request Canceled

**Command:** "Delete my research data from last week."
**User response to confirmation:** "Actually, never mind."

**Expected:** No deletion occurs. state.json unchanged. Confirm: "Deletion canceled. Data retained."

---

## Test Execution Notes

- All Sanitizer tests should be run both with `over_redact = true` and `over_redact = false`
  where applicable and differences noted.
- For each test, verify the manifest `total_redactions` count matches the number of
  placeholder occurrences in the sanitized output.
- Verify `uncertain_redactions` equals the sum of all category `uncertainty_flags`.
- Verify that no original sensitive value appears anywhere in the sanitized report or manifest.
- Verify `observation_id` values (format `obs-XXXX`) are never redacted.
