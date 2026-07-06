# CSV Batch Format Specification

This document defines the CSV column format for batch shipment processing.

---

## Required Columns

Every row must have non-empty values for all required columns. Rows missing required values should be skipped and reported to the user.

| Column | Description | Example |
|---|---|---|
| `shipment_id` | Unique identifier for the row (user's reference) | `ORD-001` |
| `sender_name` | Sender full name | `Jane Smith` |
| `sender_street1` | Sender street address | `731 Market St` |
| `sender_city` | Sender city | `San Francisco` |
| `sender_state` | Sender state/province | `CA` |
| `sender_zip` | Sender postal code | `94103` |
| `sender_country` | Sender country (ISO 3166-1 alpha-2) | `US` |
| `sender_email` | Sender email (column required; value may be empty for domestic rows but must be non-empty for international) | `jane@example.com` |
| `sender_phone` | Sender phone (column required; value may be empty for domestic rows but must be non-empty for international) | `+1-555-123-4567` |
| `recipient_name` | Recipient full name | `John Doe` |
| `recipient_street1` | Recipient street address | `456 Oak Ave` |
| `recipient_city` | Recipient city | `Portland` |
| `recipient_state` | Recipient state/province | `OR` |
| `recipient_zip` | Recipient postal code | `97201` |
| `recipient_country` | Recipient country (ISO 3166-1 alpha-2) | `US` |
| `package_length` | Parcel length (as a number) | `12` |
| `package_width` | Parcel width (as a number) | `8` |
| `package_height` | Parcel height (as a number) | `6` |
| `package_weight` | Parcel weight (as a number) | `2.5` |
| `weight_unit` | Mass unit: `lb`, `kg`, `g`, or `oz` | `lb` |
| `distance_unit` | Dimension unit: `in`, `cm`, `ft`, `m`, `mm`, or `yd` | `in` |

---

## Optional Columns

When these columns are absent or empty for a row, omit the corresponding fields from the API call. Do not send empty strings.

| Column | Description | Example |
|---|---|---|
| `recipient_email` | Recipient email address | `john@example.com` |
| `recipient_phone` | Recipient phone number | `+1-555-987-6543` |
| `sender_street2` | Sender address line 2 (apt, suite) | `Suite 200` |
| `recipient_street2` | Recipient address line 2 (apt, suite) | `Apt 4B` |
| `package_description` | Item description (used for customs) | `Cotton t-shirts` |
| `declared_value` | Declared value (used for customs/insurance) | `45.00` |
| `customs_contents_type` | Customs contents type per row | `MERCHANDISE` |
| `metadata` | Free-form reference or order number | `PO-20240115` |

---

## Sample CSV

```csv
shipment_id,sender_name,sender_street1,sender_city,sender_state,sender_zip,sender_country,sender_email,sender_phone,recipient_name,recipient_street1,recipient_city,recipient_state,recipient_zip,recipient_country,package_length,package_width,package_height,package_weight,weight_unit,distance_unit,recipient_email,package_description,declared_value
ORD-001,Jane Smith,731 Market St,San Francisco,CA,94103,US,jane@example.com,+1-555-123-4567,John Doe,456 Oak Ave,Portland,OR,97201,US,12,8,6,2.5,lb,in,,Standard package,
ORD-002,Jane Smith,731 Market St,San Francisco,CA,94103,US,jane@example.com,+1-555-123-4567,Alice Brown,789 Elm St,Seattle,WA,98101,US,10,10,10,5,lb,in,alice@example.com,Fragile item,50.00
ORD-003,Jane Smith,731 Market St,San Francisco,CA,94103,US,jane@example.com,+1-555-123-4567,Bob Wilson,22 Rue de Rivoli,Paris,,75004,FR,8,6,4,1.2,lb,in,bob@example.fr,Cotton t-shirts,75.00
```

Notes about the sample:
- Row 1 (ORD-001): Domestic US shipment with minimal optional fields.
- Row 2 (ORD-002): Domestic US shipment with recipient email and declared value.
- Row 3 (ORD-003): International shipment (US to FR). The `state` field is empty for Paris, which is acceptable for countries that do not use state/province. This row triggers customs declaration creation.

---

## Parsing and Validation Rules

### Column Matching
- Match columns by header name (case-insensitive). Trim whitespace from headers.
- Extra columns not in the spec should be ignored.
- If required columns are missing from the header row, report the missing columns and stop processing.

### Row Validation
- Skip empty rows silently.
- For each row, check that all required columns have non-empty values.
- Collect invalid rows (with row number and the specific missing/invalid fields) and report them to the user before proceeding.
- Do not include invalid rows in the batch.

### Data Type Handling
- `package_length`, `package_width`, `package_height`, and `package_weight` should be read as numbers from the CSV, then passed as **strings** to the Shippo API (e.g., CSV value `12` becomes API value `"12"`).
- `country` fields must be 2-letter ISO codes. If a row has a full country name (e.g., "United States"), attempt to map it or flag the row for user correction.
- `weight_unit` must be one of: `lb`, `kg`, `g`, `oz`.
- `distance_unit` must be one of: `in`, `cm`, `ft`, `m`, `mm`, `yd`.

### International Detection
- Compare `sender_country` and `recipient_country` for each row.
- If they differ, the row is international and requires a customs declaration.
- For international rows, `sender_email` and `sender_phone` are mandatory (carriers require them for customs). Flag any international row missing these fields.

### Encoding
- Expect UTF-8 encoding. If parsing fails, ask the user to verify the file is UTF-8 encoded.
- Handle common CSV dialects: comma-delimited, with or without quoted fields.

### Shared Sender Optimization
- If all rows share the same sender address, note this to the user. The sender fields still must be present in every row for the CSV format, but the agent can confirm once and reuse.

### Error Reporting Format
When reporting validation errors, include:
- Row number (1-indexed, not counting the header)
- The shipment_id value (if present)
- The specific field(s) that are missing or invalid
- A summary count: "N of M rows are valid and will be processed"
