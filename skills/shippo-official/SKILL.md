---
name: shippo-official
description: >
  Ship packages with Shippo. Multi-carrier rate shopping, label generation,
  package tracking, address validation, customs declarations, and batch
  processing from CSV files.
version: 1.0.1
metadata:
  openclaw:
    requires:
      env:
        - SHIPPO_API_KEY
    primaryEnv: SHIPPO_API_KEY
    emoji: "📦"
    homepage: https://github.com/goshippo/shippo-clawhub-skill
---

# Shippo Shipping Skill

## Setup

**MCP server:** `https://app.getgram.ai/mcp/shippo-mcp-beta` with header `Mcp-Shippo-Merged-Api-Key-Header` set to the `SHIPPO_API_KEY` environment variable.

**Prerequisites:** A valid Shippo API key and at least one carrier account (Shippo provides managed accounts for USPS, UPS, FedEx, DHL Express by default). See `references/tool-reference.md` for the full tool catalog.

**Test vs live mode** -- check the API key prefix before any purchase workflow:
- **`shippo_test_*`**: Labels are free. No real charges. Tracking uses mock numbers only.
- **`shippo_live_*`**: Real charges. Inform the user which mode they are in.

Test and live mode have completely separate data and object IDs.

---

## Address Validation

### Address Field Format

The Shippo API uses **v1 field names** for address components in most endpoints (including `shipments-create`). Always use:

| Field | Description | Example |
|---|---|---|
| `name` | Full name | `Jane Smith` |
| `street1` | Street address line 1 | `731 Market St` |
| `street2` | Street address line 2 (optional) | `Suite 200` |
| `city` | City | `San Francisco` |
| `state` | State or province | `CA` |
| `zip` | Postal code | `94103` |
| `country` | ISO 3166-1 alpha-2 country code | `US` |
| `email` | Email (required for international senders) | `jane@example.com` |
| `phone` | Phone (required for international senders) | `+1-555-123-4567` |

Note: The v2 address endpoints (`addresses-create-v2`, `addresses-validate-v2`) use different field names (`address_line_1`, `city_locality`, `state_province`, `postal_code`), but when passing addresses inline to `shipments-create`, you must use the v1 names above.

### Validate a Structured Address

1. Collect at minimum: `street1`, `city`, `state`, `zip`, `country` (ISO 3166-1 alpha-2).
2. Call `addresses-create-v2` with the address fields (creates the address, returns object ID).
3. Call `addresses-validate-v2` with the same fields as query parameters (not object ID).
4. Check `analysis.validation_result.value`: `"valid"`, `"invalid"`, or `"partially_valid"`. Check `reasons` for details.
5. Report the standardized address. Highlight corrected fields (`changed_attributes`). Note `analysis.address_type` (`"residential"`, `"commercial"`, `"unknown"`) -- affects carrier surcharges.
6. If invalid: relay reasons. Present `recommended_address` if returned.
7. If `partially_valid`: show corrections and ask user to confirm.

### Parse a Freeform Address

1. Call `addresses-parse` with the raw string. Response uses v2 field names: `address_line_1`, `city_locality`, `state_province`, `postal_code`.
2. The parse response does not include `country`. Ask the user or infer it, then add it.
3. Validate the parsed result by following the structured address workflow above from step 2.

### International Addresses

- Always require the `country` field. Do not guess.
- Pass non-Latin characters as-is; the API handles encoding.
- Validation depth varies by country. US, CA, GB, AU, and major EU countries have deep validation. Others may only confirm structural completeness. Inform the user.

### Bulk Address Validation

No batch endpoint. Call `addresses-create-v2` per address. Track results and report a summary. For 50+ addresses, set expectations about processing time.

---

## Rate Shopping

### Get Rates for a Shipment

1. Collect: origin address, destination address, parcel (length, width, height, distance_unit, weight, mass_unit). All values must be **strings** (e.g., `"10"` not `10`).
2. Optionally validate addresses (see Address Validation above).
3. Call `shipments-create` with `address_from`, `address_to` (inline v1 field names), and `parcels`.
4. Present the `rates` array as a table: carrier, service level, price, estimated days. Deduplicate by carrier/service combination.

### Dimensional Weight

Carriers charge based on the greater of actual weight and dimensional weight:

```
dim_weight = (length x width x height) / divisor
```

| Carrier | Divisor (inches) | Divisor (cm) |
|---|---|---|
| USPS | 166 | 5000 |
| UPS | 139 | 5000 |
| FedEx | 139 | 5000 |
| DHL Express | 139 | 5000 |

If a package is large but light, dimensional weight will exceed actual weight and the carrier charges the higher rate. When rates seem surprisingly high, check if dimensional weight is the cause.

### Flat Rate

USPS flat-rate options charge a fixed price regardless of weight (up to 70 lbs). Set the parcel `template` to a flat-rate token (e.g., `USPS_SmallFlatRateBox`) instead of custom dimensions. Flat rate wins for heavy or long-distance shipments; custom dimensions win for light, nearby packages.

### Filter by Speed

Map user requests: "overnight" = estimated_days 1, "2-day" = estimated_days <= 2, "within N days" = estimated_days <= N. Filter the rates array accordingly. If nothing matches, show the fastest available.

### International Rates

Some carriers require a customs declaration or phone number on the destination address for international rates. If no rates are returned, try attaching a customs declaration. See `references/customs-guide.md` for customs details.

### Checkout Rates (Line Items)

Call `rates-at-checkout-create` instead of `shipments-create`. Accepts `address_from`, `address_to`, and `line_items` (each with title, quantity, total_price, currency, weight, weight_unit).

### Recommendation

Identify the cheapest (lowest `amount`), fastest (lowest `estimated_days`), and best-value options. Compute by sorting -- these are not API fields. State the trade-off: "Option A is $X cheaper but takes Y more days."

### Troubleshooting: No Rates

- Verify both addresses passed validation (most common cause).
- Confirm parcel dimensions are reasonable (not zero, not exceeding carrier limits).
- Shippo provides managed carrier accounts by default. Missing rates usually mean address issues, unsupported routes, or bad dimensions. Verify with `carrier-accounts-list` if needed.

---

## Label Purchase

### Purchase Confirmation Gate

Before every `transactions-create`, summarize carrier/service, cost, delivery time, and origin/destination. **Do not proceed without explicit user confirmation.**

### Domestic Label

1. Optionally validate both addresses (see Address Validation above).
2. Call `shipments-create` with `address_from`, `address_to` (inline v1 field names), `parcels`, `async: false`.
3. Present rates. Let user choose. **Confirm purchase** (see gate above).
4. Call `transactions-create` with `rate` (object_id), `label_file_type` (default `PDF_4x6`), `async: false`.
5. Check `status`:
   - `SUCCESS`: return `tracking_number`, `label_url` (complete URL), `tracking_url_provider`.
   - `QUEUED`/`WAITING`: poll `transactions-get` until resolved.
   - `ERROR`: report `messages` array.

### International Label

All domestic steps apply, plus customs before shipment creation. See `references/customs-guide.md`.

1. Validate addresses. Sender must include `email` and `phone`. Ask if missing.
2. Create customs items via `customs-items-create` per item, or pass inline objects in step 3.
3. Call `customs-declarations-create` with contents_type, non_delivery_option, certify: true, certify_signer, and items.
4. Call `shipments-create` with standard fields plus `customs_declaration` (object_id).
5. Present rates, **confirm purchase**, purchase label, return results.

### Contents Type Decision Tree

| Scenario | Value |
|---|---|
| Commercial sale | `MERCHANDISE` |
| Free gift | `GIFT` |
| Product sample | `SAMPLE` |
| Paper documents only | `DOCUMENTS` |
| Customer returning item | `RETURN_MERCHANDISE` |
| Charitable donation | `HUMANITARIAN_DONATION` |
| None of the above | `OTHER` (requires `contents_explanation`) |

### Incoterms Decision Logic

- **B2C / e-commerce (default):** Use `DDU` (Delivered Duty Unpaid) -- recipient pays duties.
- **Seller prepays duties:** Use `DDP` (Delivered Duty Paid) -- seller covers duties/taxes.
- **FedEx/DHL only:** `FCA` (Free Carrier) for advanced trade scenarios.

Default to `DDU` if the user does not specify.

### Label Format Options

Default to `PDF_4x6` unless the user specifies otherwise.

| Format | Dimensions | Use Case |
|---|---|---|
| `PDF_4x6` | 4" x 6" | **Default.** Standard thermal label. |
| `PDF_4x8` | 4" x 8" | Extended label for UPS/FedEx |
| `PDF_A4` | 8.27" x 11.69" | Standard office printer |
| `PDF_A5` | 5.83" x 8.27" | Half-sheet label |
| `PDF_A6` | 4.13" x 5.83" | Quarter-sheet label |
| `PDF` | Varies | Generic PDF, carrier-determined size |
| `PDF_2.3x7.5` | 2.3" x 7.5" | Narrow format label printers |
| `PNG` | Varies | Image format for web display |
| `PNG_2.3x7.5` | 2.3" x 7.5" | Narrow PNG format |
| `ZPLII` | N/A | Zebra thermal printers only |

### Label Customization Options

Set these on the shipment's `extra` field:
- **Signature confirmation** (`signature_confirmation`): `STANDARD`, `ADULT`, `CERTIFIED`, `INDIRECT`, `CARRIER_CONFIRMATION`.
- **Insurance** (`insurance`): with `amount`, `currency`, `provider`.
- **Saturday delivery** (`saturday_delivery`): `true`. Only certain carriers/service levels.
- **Reference fields**: pass `metadata` on the transaction for order numbers.

### Return Labels

Swap `address_from` and `address_to` so the original recipient becomes the sender. All other steps remain the same.

### Voiding a Label

Call `refunds-create` with the transaction object_id. Eligibility depends on carrier and timing. If it fails, advise the user to contact Shippo support.

### Orders and Packing Slips

1. Call `orders-create` with shipping address, line items, and order details.
2. Use the order data to call `shipments-create`, then follow the standard label purchase flow.
3. After purchasing, call `orders-get-packing-slip` for a PDF packing slip.

---

## Tracking

### Track by Number

1. Determine carrier (lowercase Shippo token: `usps`, `ups`, `fedex`, `dhl_express`) and tracking number. See `references/carrier-guide.md` for format hints. If uncertain, ask the user.
2. Call `tracking-status-get` with `carrier` and `tracking_number`.
3. Key fields: `tracking_status` (status, status_details, status_date, location), `tracking_history`, `eta`. Each event includes a `substatus` with `code`, `text`, `action_required`.
4. Present: current status, location, ETA, substatus details, chronological history (most recent first).

### Status Values

| Status | Meaning |
|---|---|
| PRE_TRANSIT | Label created, carrier has not received the package |
| TRANSIT | Package is in transit |
| DELIVERED | Delivered |
| RETURNED | Being returned or returned to sender |
| FAILURE | Delivery failed |
| UNKNOWN | No tracking information from carrier |

### Test Mode Tracking

In test mode, use `shippo` as the carrier token with these mock tracking numbers:

| Tracking Number | Simulated Status |
|---|---|
| `SHIPPO_PRE_TRANSIT` | Label created, not yet with carrier |
| `SHIPPO_TRANSIT` | Package in transit |
| `SHIPPO_DELIVERED` | Package delivered |
| `SHIPPO_RETURNED` | Package returned to sender |
| `SHIPPO_FAILURE` | Delivery failed |
| `SHIPPO_UNKNOWN` | Status unknown |

Example: `tracking-status-get carrier="shippo" tracking_number="SHIPPO_DELIVERED"`

### Find Trackable Packages

Call `transactions-list`. Filter for `object_status: SUCCESS`. Each successful transaction has `tracking_number` and carrier info. Then call `tracking-status-get` for selected items.

### Register a Tracking Webhook

1. Call `webhooks-create` with the user's HTTPS `url` and `event: track_updated`.
2. Optionally call `tracking-status-create` with carrier and tracking number to register a shipment for push updates.

---

## Batch Shipping

### Purchase Confirmation Gate

Before every `batches-purchase`, summarize total shipments, carrier/service, estimated total cost, and domestic vs international count. **Do not proceed without explicit user confirmation.**

### CSV Batch Processing

See `references/csv-format.md` for column spec. See `references/customs-guide.md` for international rows.

1. Parse CSV. Validate required columns. Report row count and any invalid rows.
2. Detect international rows (sender_country != recipient_country). Create customs declarations for those. Use correct enum values: `RETURN_MERCHANDISE` (not `RETURN`), `HUMANITARIAN_DONATION` (not `HUMANITARIAN`).
3. Build `batch_shipments` array with inline address and parcel objects per row.
4. Call `batches-create`. Poll `batches-get` until status is `VALID`.
5. Review per-shipment validation. Report failures before proceeding.
6. **Confirm purchase** (see gate above).
7. Call `batches-purchase`. Poll `batches-get` until `PURCHASED`.
8. Report: total attempted, succeeded, failed. For successes: tracking_number and label_url (complete URL). For failures: error messages.

### Polling and Batch Size

- Under 100 shipments: poll every 3-5 seconds. 100+: poll every 5-10 seconds.
- Report progress every 30 seconds. Stop after 60 retries and suggest checking back with `batches-get`.
- For batches over 500 shipments, split into multiple batches.

### Batch with Rate Shopping

1. Call `shipments-create` per shipment for rate quotes (see Rate Shopping above).
2. User picks a service level rule (e.g., "cheapest for each"). Build `batch_shipments` with `servicelevel_token` per item.
3. Create, validate, **confirm purchase**, purchase, report as above.

### Managing an Existing Batch

- **Add**: `batches-add-shipments` (before purchase only). Adding an invalid shipment changes entire batch to `INVALID`.
- **Remove**: `batches-remove-shipments` (before purchase only).

### End-of-Day Manifest

1. Collect: `carrier_account` (object_id), `shipment_date` (YYYY-MM-DD), `address_from`, and optionally specific transaction object_ids.
2. Call `manifests-create`. Poll `manifests-get` until `SUCCESS` or `ERROR`.
3. Return the manifest PDF URL(s) and shipment count.

---

## Shipping Analysis

### Geographic Cost Analysis

1. Confirm origin, destination list (or representative cities), and parcel details.
2. Call `carrier-accounts-list` to see configured carriers.
3. Call `shipments-create` per destination to collect rates. Shipment creation is free; only `transactions-create` costs money.
4. Write results to `analysis/` directory (markdown + CSV). Columns: Route, Destination, Carrier, Service, Cost, Currency, EstimatedDays, Zone.

### Package Optimization

1. Confirm the route and define dimension profiles to test.
2. Check `carrier-parcel-templates-list` and `user-parcel-templates-list` for flat-rate and saved templates.
3. Call `shipments-create` per profile on the same route.
4. Compare: cheapest, fastest, and best-value per profile. Note where flat-rate beats custom dimensions and where dimensional weight causes price jumps. See `references/carrier-guide.md` for carrier limits.

### Carrier Comparison

1. Call `shipments-create` for the route. Group the `rates` array by `provider`.
2. Per carrier: cheapest service, fastest service, number of service levels, price range.

### Historical Cost Optimization

1. Call `shipments-list` and `transactions-list` to get past activity.
2. Cross-reference what the user paid vs. alternatives available.
3. Identify patterns: carrier concentration, service-level mismatch, consistent overpayment.
4. For a sample, call `tracking-status-get` to check actual vs. estimated delivery times.
5. If fewer than 5 successful transactions exist, redirect to forward-looking analysis.

### Output Conventions

Write reports to the `analysis/` directory (create if needed). Include markdown (with timestamp and input parameters) and CSV (with header row).

---

## Error Handling

- **Never guess** parcel dimensions, weight, customs values, HS codes, or signer names. Ask the user.
- **Do not auto-retry** transport, auth, or rate-limit errors. Report to user and stop.
- Parcel dimensions and weight must be **strings** (e.g., `"10"` not `10`).
- Label URLs are S3 signed URLs. **Always display the complete URL** -- truncating breaks the signature.
- Rates expire after 7 days. Create a new shipment for fresh rates.
- No rates? Validate addresses first, then check dimensions, then `carrier-accounts-list`.
- "Not found" errors: verify API key mode matches the data -- test and live have separate object IDs.

---

## Security & Data Transparency

- All data is sent to Shippo's API via the MCP server hosted at `app.getgram.ai/mcp/shippo-mcp-beta`.
- The `SHIPPO_API_KEY` environment variable is sent as a header (`Mcp-Shippo-Merged-Api-Key-Header`) to authenticate requests.
- No data is stored by the skill itself; all persistence is handled by Shippo's API.
- Label and tracking data are subject to Shippo's data retention policies.
