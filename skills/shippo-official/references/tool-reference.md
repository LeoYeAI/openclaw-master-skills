# Shippo MCP Tool Reference

Complete list of MCP tools provided by the Shippo server, grouped by category. Includes required/optional parameters, data types, and async behavior.

**Data type note:** Dimensions (length, width, height) and weight values must be passed as **strings**, not numbers (e.g., `"12"` not `12`). This applies to parcels, customs items, and all weight/dimension fields.

---

## Addresses

### `addresses-create-v2` (preferred)
Create and validate a new address using v2 field names. Returns validation results.
- **Required:** `name` (string), `address_line_1` (string), `city_locality` (string), `country_code` (string, ISO 3166-1 alpha-2)
- **Optional:** `address_line_2` (string), `address_line_3` (string), `state_province` (string), `postal_code` (string), `phone` (string), `email` (string), `company` (string), `is_residential` (boolean)

### `addresses-validate-v2`
Validate an existing address by object ID using v2 validation.
- **Required:** `address_id` (string)

### `addresses-parse`
Parse a freeform address string into structured components. Returns v2 field names (no country).
- **Required:** `address_string` (string, freeform address text)

### `addresses-create-v1` (legacy)
Create an address without automatic validation. Uses v1 field names.
- **Required:** `name` (string), `street1` (string), `city` (string), `country` (string, ISO 3166-1 alpha-2)
- **Optional:** `street2` (string), `street3` (string), `state` (string), `zip` (string), `phone` (string), `email` (string), `company` (string), `is_residential` (boolean), `validate` (boolean), `metadata` (string)

### `addresses-validate-existing` (legacy)
Validate an existing address by object ID using v1 validation.
- **Required:** `address_id` (string)

### `addresses-get`
Retrieve a previously created address by ID.
- **Required:** `address_id` (string)

### `addresses-list`
List all stored addresses. Supports pagination.
- **Optional:** `page` (integer), `results` (integer, page size)

---

## Shipments

### `shipments-create`
Create a new shipment and retrieve available rates. **Async:** if `async` is true (default), returns immediately and rates must be polled via `shipments-get` or `shipments-list-rates`.
- **Required:** `address_from` (object or string ID, v1 field names for inline), `address_to` (object or string ID, v1 field names for inline), `parcels` (array of parcel objects or string IDs)
- **Optional:** `customs_declaration` (string, object ID), `extra` (object, for signature, insurance, etc.), `metadata` (string), `async` (boolean, default true), `carrier_accounts` (array of carrier account IDs to filter rates)
- **Note:** Inline address objects use v1 names: `name`, `street1`, `city`, `state`, `zip`, `country`

### `shipments-get`
Retrieve a shipment by ID. Use to poll for rates after async creation.
- **Required:** `shipment_id` (string)

### `shipments-list`
List all shipments. Supports pagination.
- **Optional:** `page` (integer), `results` (integer, page size)

### `shipments-list-rates`
Retrieve rates for an existing shipment by ID.
- **Required:** `shipment_id` (string)

---

## Rates

### `rates-get`
Retrieve a specific rate by ID.
- **Required:** `rate_id` (string)

### `rates-list-by-currency-code`
Retrieve shipment rates filtered to a specific currency.
- **Required:** `shipment_id` (string), `currency_code` (string, ISO 4217 e.g., `USD`)
- **Optional:** `page` (integer), `results` (integer)

### `rates-at-checkout-create`
Generate live rates for a checkout flow with line items and address.
- **Required:** `address_to` (object), `line_items` (array), `parcel` (object or template)
- **Optional:** `address_from` (object), `carrier_accounts` (array)

### `rates-at-checkout-get-default-parcel-template`
Show the current default parcel template for checkout rates. No parameters.

### `rates-at-checkout-delete-default-parcel-template`
Clear the current default parcel template. No parameters.

### `rates-at-checkout-update-parcel-template`
Update the default parcel template for checkout rates.
- **Required:** `object_id` (string, parcel template ID)

---

## Transactions (Labels)

### `transactions-create`
Purchase a shipping label from an existing rate. **Async:** returns immediately with status `QUEUED`; poll via `transactions-get` until status is `SUCCESS` or `ERROR`.
- **Required:** `rate` (string, rate object_id)
- **Optional:** `label_file_type` (string, e.g., `PDF_4x6`, `PNG`, `ZPLII`), `async` (boolean, default true), `metadata` (string)
- **Response includes:** `label_url`, `tracking_number`, `tracking_url_provider` when status is `SUCCESS`

### `transactions-get`
Retrieve a transaction (label) by ID. Use to poll async label purchases.
- **Required:** `transaction_id` (string)

### `transactions-list`
List all transactions. Supports filtering and pagination.
- **Optional:** `page` (integer), `results` (integer), `object_status` (string), `tracking_status` (string)

---

## Tracking

### `tracking-status-get`
Get current tracking status for a carrier + tracking number.
- **Required:** `carrier` (string, carrier token e.g., `usps`, `ups`, `fedex`, `dhl_express`), `tracking_number` (string)

### `tracking-status-create`
Register a shipment for tracking webhook notifications.
- **Required:** `carrier` (string), `tracking_number` (string)
- **Optional:** `metadata` (string)

---

## Batches

### `batches-create`
Create a new batch of shipments. **Async:** returns immediately with status `VALIDATING`; poll via `batches-get` until status is `VALID` or `INVALID`.
- **Required:** `default_carrier_account` (string, carrier account ID), `default_servicelevel_token` (string), `batch_shipments` (array of batch shipment objects)
- **Optional:** `label_filetype` (string), `metadata` (string), `label_size` (string)
- **Each batch shipment object requires:** `shipment` (object with `address_from`, `address_to`, `parcels`, and optionally `customs_declaration`)

### `batches-get`
Retrieve a batch by ID. Includes status and per-shipment results.
- **Required:** `batch_id` (string)

### `batches-purchase`
Purchase labels for all valid shipments in a batch. **Async:** triggers purchase; poll `batches-get` until status is `PURCHASED`.
- **Required:** `batch_id` (string)

### `batches-add-shipments`
Add shipments to an existing batch (before purchase only).
- **Required:** `batch_id` (string), `body` (array of batch shipment objects)

### `batches-remove-shipments`
Remove shipments from an existing batch (before purchase only).
- **Required:** `batch_id` (string), `shipment_ids` (array of string IDs)

---

## Customs

### `customs-declarations-create`
Create a customs declaration for international shipments.
- **Required:** `certify` (boolean, must be true), `certify_signer` (string), `contents_type` (string), `non_delivery_option` (string), `items` (array of customs item object_ids)
- **Optional:** `contents_explanation` (string, required if contents_type is OTHER), `exporter_reference` (string), `importer_reference` (string), `invoice` (string), `license` (string), `certificate` (string), `notes` (string), `eel_pfc` (string), `incoterm` (string), `b13a_filing_option` (string), `metadata` (string)

### `customs-declarations-get`
Retrieve a customs declaration by ID.
- **Required:** `customs_declaration_id` (string)

### `customs-declarations-list`
List all customs declarations. Supports pagination.
- **Optional:** `page` (integer), `results` (integer)

### `customs-items-create`
Create a customs item (individual line item within a declaration).
- **Required:** `description` (string), `quantity` (integer), `net_weight` (string), `mass_unit` (string), `value_amount` (string), `value_currency` (string), `origin_country` (string)
- **Optional:** `tariff_number` (string), `sku_code` (string), `eccn_ear99` (string), `metadata` (string)

### `customs-items-get`
Retrieve a customs item by ID.
- **Required:** `customs_item_id` (string)

### `customs-items-list`
List all customs items. Supports pagination.
- **Optional:** `page` (integer), `results` (integer)

---

## Manifests

### `manifests-create`
Create an end-of-day manifest (SCAN form) for carrier pickup. **Async:** returns with status `QUEUED`; poll via `manifests-get`.
- **Required:** `carrier_account` (string, carrier account ID), `shipment_date` (string, ISO 8601 date), `address_from` (object or string ID)
- **Optional:** `transactions` (array of transaction IDs; if omitted, includes all eligible), `async` (boolean)

### `manifests-get`
Retrieve a manifest by ID.
- **Required:** `manifest_id` (string)

### `manifests-list`
List all manifests. Supports pagination.
- **Optional:** `page` (integer), `results` (integer)

---

## Parcels

### `parcels-create`
Create a new parcel object.
- **Required:** `length` (string), `width` (string), `height` (string), `distance_unit` (string: `in`, `cm`, `ft`, `m`, `mm`, `yd`), `weight` (string), `mass_unit` (string: `lb`, `kg`, `g`, `oz`)
- **Optional:** `template` (string, carrier parcel template token), `metadata` (string)

### `parcels-get`
Retrieve an existing parcel by ID.
- **Required:** `parcel_id` (string)

### `parcels-list`
List all parcels. Supports pagination.
- **Optional:** `page` (integer), `results` (integer)

---

## Parcel Templates

### `carrier-parcel-templates-list`
List all carrier-provided parcel templates (e.g., USPS Flat Rate). Filterable by carrier.
- **Optional:** `carrier` (string, carrier token), `include` (string)

### `carrier-parcel-templates-get`
Retrieve a specific carrier parcel template.
- **Required:** `carrier_parcel_template_id` (string)

### `user-parcel-templates-list`
List all user-created parcel templates. No required parameters.

### `user-parcel-templates-create`
Create a new user parcel template.
- **Required:** `name` (string), `length` (string), `width` (string), `height` (string), `distance_unit` (string), `weight` (string), `mass_unit` (string)
- **Optional:** `template` (string)

### `user-parcel-templates-get`
Retrieve a user parcel template by ID.
- **Required:** `user_parcel_template_id` (string)

### `user-parcel-templates-update`
Update an existing user parcel template.
- **Required:** `user_parcel_template_id` (string)
- **Optional:** Same fields as create

### `user-parcel-templates-delete`
Delete a user parcel template.
- **Required:** `user_parcel_template_id` (string)

---

## Carrier Accounts

### `carrier-accounts-list`
List all carrier accounts. Supports pagination and filtering.
- **Optional:** `page` (integer), `results` (integer), `carrier` (string), `account_id` (string)

### `carrier-accounts-create`
Create a new carrier account.
- **Required:** `carrier` (string), `account_id` (string), `parameters` (object, carrier-specific)

### `carrier-accounts-get`
Retrieve a carrier account by ID.
- **Required:** `carrier_account_id` (string)

### `carrier-accounts-update`
Update a carrier account.
- **Required:** `carrier_account_id` (string)
- **Optional:** `account_id` (string), `parameters` (object)

### `carrier-accounts-register`
Add a Shippo carrier account (e.g., Shippo's USPS managed account).
- **Required:** `carrier` (string)

### `carrier-accounts-get-registration-status`
Get carrier registration status.
- **Required:** `carrier` (string)

### `carrier-accounts-initiate-oauth2-signin`
Connect a carrier account using OAuth 2.0.
- **Required:** `carrier_account_id` (string), `redirect_url` (string)

---

## Orders

### `orders-create`
Create a new order.
- **Required:** `to_address` (object), `line_items` (array), `placed_at` (string, ISO 8601), `order_number` (string), `order_status` (string), `shipping_cost` (string), `shipping_cost_currency` (string)
- **Optional:** `from_address` (object), `weight` (string), `weight_unit` (string), `notes` (string), `shipping_method` (string)

### `orders-get`
Retrieve an order by ID.
- **Required:** `order_id` (string)

### `orders-list`
List all orders. Supports pagination.
- **Optional:** `page` (integer), `results` (integer), `order_status` (array of strings), `shop_app` (string)

### `orders-get-packing-slip`
Get a packing slip for an order.
- **Required:** `order_id` (string)

---

## Refunds

### `refunds-create`
Create a refund (void a label). Must be requested within 30 days of purchase for most carriers.
- **Required:** `transaction` (string, transaction object_id)
- **Optional:** `async` (boolean)

### `refunds-get`
Retrieve a refund by ID.
- **Required:** `refund_id` (string)

### `refunds-list`
List all refunds. Supports pagination.
- **Optional:** `page` (integer), `results` (integer)

---

## Pickups

### `pickups-create`
Schedule a carrier pickup.
- **Required:** `carrier_account` (string), `location` (object with address and building info), `transactions` (array of transaction IDs), `requested_start_time` (string, ISO 8601), `requested_end_time` (string, ISO 8601)
- **Optional:** `is_test` (boolean)

---

## Service Groups

### `service-groups-list`
List all service groups. No required parameters.

### `service-groups-create`
Create a new service group.
- **Required:** `name` (string), `description` (string), `flat_rate` (string), `flat_rate_currency` (string), `service_levels` (array)

### `service-groups-update`
Update an existing service group.
- **Required:** `service_group_id` (string)
- **Optional:** Same fields as create

### `service-groups-delete`
Delete a service group.
- **Required:** `service_group_id` (string)

---

## Webhooks

### `webhooks-create`
Create a new webhook subscription.
- **Required:** `url` (string), `event` (string, e.g., `track_updated`, `transaction_created`, `batch_created`)
- **Optional:** `is_test` (boolean), `active` (boolean)

### `webhooks-get`
Retrieve a specific webhook.
- **Required:** `webhook_id` (string)

### `webhooks-list`
List all webhooks. No required parameters.

### `webhooks-update`
Update an existing webhook.
- **Required:** `webhook_id` (string)
- **Optional:** `url` (string), `event` (string), `is_test` (boolean), `active` (boolean)

### `webhooks-delete`
Delete a webhook.
- **Required:** `webhook_id` (string)

---

## Shippo Accounts

### `shippo-accounts-list`
List all Shippo accounts. Supports pagination.
- **Optional:** `page` (integer), `results` (integer)

### `shippo-accounts-create`
Create a Shippo account.
- **Required:** `email` (string), `first_name` (string), `last_name` (string), `company_name` (string)

### `shippo-accounts-get`
Retrieve a Shippo account.
- **Required:** `shippo_account_id` (string)

### `shippo-accounts-update`
Update a Shippo account.
- **Required:** `shippo_account_id` (string)
- **Optional:** `email` (string), `first_name` (string), `last_name` (string), `company_name` (string)

---

## Async Tools Summary

These tools return immediately and require polling to get final results:

| Tool | Initial Status | Poll With | Final Status |
|---|---|---|---|
| `shipments-create` (async=true) | `QUEUED` | `shipments-get` | rates populated |
| `transactions-create` | `QUEUED` | `transactions-get` | `SUCCESS` or `ERROR` |
| `batches-create` | `VALIDATING` | `batches-get` | `VALID` or `INVALID` |
| `batches-purchase` | `PURCHASING` | `batches-get` | `PURCHASED` |
| `manifests-create` | `QUEUED` | `manifests-get` | `SUCCESS` or `ERROR` |
| `refunds-create` (async=true) | `QUEUED` | `refunds-get` | `SUCCESS` or `ERROR` |
