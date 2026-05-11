---
name: lap-account-api
description: "Account API skill. Use when working with Account for custom_policy, fulfillment_policy, payment_policy. Covers 36 endpoints."
version: 1.0.0
generator: lapsh
metadata:
  openclaw:
    requires:
      env:
        - ACCOUNT_API_KEY
---

# Account API
API version: v1.9.2

## Auth
OAuth2

## Base URL
https://api.ebay.com/sell/account/v1

## Setup
1. Configure auth: OAuth2
2. GET /custom_policy/ -- verify access
3. POST /custom_policy/ -- create first custom_policy

## Endpoints

36 endpoints across 12 groups. See references/api-spec.lap for full details.

### custom_policy
| Method | Path | Description |
|--------|------|-------------|
| GET | /custom_policy/ | This method retrieves the list of custom policies specified by the policy_types query parameter.Note: Custom policies are no longer coupled with a specific eBay marketplace, so the EBAY-C-MARKETPLACE-ID request header is no longer needed or relevant for any of the Custom Policy methods. |
| POST | /custom_policy/ | This method creates a new custom policy in which a seller specifies their terms for complying with local governmental regulations. Two Custom Policy types are supported: Product Compliance (PRODUCT_COMPLIANCE) Takeback (TAKE_BACK)Each Custom Policy targets a policyType. Multiple policies may be created as follows: Product Compliance: a maximum of 60 policies per seller may be created Takeback: a maximum of 18 policies per seller may be createdA successful create policy call returns an HTTP status code of 201 Created with the system-generated policy ID included in the Location response header.Product Compliance PolicyProduct Compliance policies disclose product information as required for regulatory compliance.Note: A maximum of 60 Product Compliance policies per seller may be created.  Takeback PolicyTakeback policies describe the seller's legal obligation to take back a previously purchased item when the buyer purchases a new one.Note: A maximum of 18 Takeback policies per seller may be created.Note: Custom policies are no longer coupled with a specific eBay marketplace, so the EBAY-C-MARKETPLACE-ID request header is no longer needed or relevant for any of the Custom Policy methods. |
| GET | /custom_policy/{custom_policy_id} | This method retrieves the custom policy specified by the custom_policy_id path parameter.Note: Custom policies are no longer coupled with a specific eBay marketplace, so the EBAY-C-MARKETPLACE-ID request header is no longer needed or relevant for any of the Custom Policy methods. |
| PUT | /custom_policy/{custom_policy_id} | This method updates an existing custom policy specified by the custom_policy_id path parameter. This method overwrites the policy's Name, Label, and Description fields. Therefore, the complete, current text of all three policy fields must be included in the request payload even when one or two of these fields will not actually be updated. For example, the value for the Label field is to be updated, but the Name and Description values will remain unchanged. The existing Name and Description values, as they are defined in the current policy, must also be passed in. A successful policy update call returns an HTTP status code of 204 No Content.Note: Custom policies are no longer coupled with a specific eBay marketplace, so the EBAY-C-MARKETPLACE-ID request header is no longer needed or relevant for any of the Custom Policy methods. |

### fulfillment_policy
| Method | Path | Description |
|--------|------|-------------|
| POST | /fulfillment_policy/ | This method creates a new fulfillment policy where the policy encapsulates seller's terms for fulfilling item purchases. Fulfillment policies include the shipment options that the seller offers to buyers.  Each policy targets a specific eBay marketplace and a category group type, and you can create multiple policies for each combination. A successful request returns the getFulfillmentPolicy URI to the new policy in the Location response header and the ID for the new policy is returned in the response payload.  Tip: For details on creating and using the business policies supported by the Account API, see eBay business policies.  Using the eBay standard envelope service (eSE)The eBay standard envelope service (eSE) is a domestic envelope service with tracking through eBay. This service applies to specific sub-categories of Trading Cards, and to coins & paper money, postcards, stamps, patches, and similar eligible categories, and is only available on the US marketplace. To use this service, send envelopes using the USPS mail and set the shippingServiceCode field to US_eBayStandardEnvelope. See Using eBay standard envelope (eSE) service for details. See eBay standard envelope for additional details, restrictions, and an envelope size template. |
| GET | /fulfillment_policy/{fulfillmentPolicyId} | This method retrieves the complete details of a fulfillment policy. Supply the ID of the policy you want to retrieve using the fulfillmentPolicyId path parameter. |
| PUT | /fulfillment_policy/{fulfillmentPolicyId} | This method updates an existing fulfillment policy. Specify the policy you want to update using the fulfillment_policy_id path parameter. Supply a complete policy payload with the updates you want to make; this call overwrites the existing policy with the new details specified in the payload. |
| DELETE | /fulfillment_policy/{fulfillmentPolicyId} | This method deletes a fulfillment policy. Supply the ID of the policy you want to delete in the fulfillmentPolicyId path parameter. |
| GET | /fulfillment_policy | This method retrieves all the fulfillment policies configured for the marketplace you specify using the marketplace_id query parameter.  Marketplaces and locales  Get the correct policies for a marketplace that supports multiple locales using the Content-Language request header. For example, get the policies for the French locale of the Canadian marketplace by specifying fr-CA for the Content-Language header. Likewise, target the Dutch locale of the Belgium marketplace by setting Content-Language: nl-BE. For details on header values, see HTTP request headers. |
| GET | /fulfillment_policy/get_by_policy_name | This method retrieves the details for a specific fulfillment policy. In the request, supply both the policy name and its associated marketplace_id as query parameters.   Marketplaces and locales  Get the correct policy for a marketplace that supports multiple locales using the Content-Language request header. For example, get a policy for the French locale of the Canadian marketplace by specifying fr-CA for the Content-Language header. Likewise, target the Dutch locale of the Belgium marketplace by setting Content-Language: nl-BE. For details on header values, see HTTP request headers. |

### payment_policy
| Method | Path | Description |
|--------|------|-------------|
| GET | /payment_policy | This method retrieves all the payment policies configured for the marketplace you specify using the marketplace_id query parameter.  Marketplaces and locales  Get the correct policies for a marketplace that supports multiple locales using the Content-Language request header. For example, get the policies for the French locale of the Canadian marketplace by specifying fr-CA for the Content-Language header. Likewise, target the Dutch locale of the Belgium marketplace by setting Content-Language: nl-BE. For details on header values, see HTTP request headers. |
| POST | /payment_policy | This method creates a new payment policy where the policy encapsulates seller's terms for order payments.  Each policy targets a specific eBay marketplace and category group, and you can create multiple policies for each combination.  A successful request returns the getPaymentPolicy URI to the new policy in the Location response header and the ID for the new policy is returned in the response payload.  Tip: For details on creating and using the business policies supported by the Account API, see eBay business policies. |
| GET | /payment_policy/{payment_policy_id} | This method retrieves the complete details of a payment policy. Supply the ID of the policy you want to retrieve using the paymentPolicyId path parameter. |
| PUT | /payment_policy/{payment_policy_id} | This method updates an existing payment policy. Specify the policy you want to update using the payment_policy_id path parameter. Supply a complete policy payload with the updates you want to make; this call overwrites the existing policy with the new details specified in the payload. |
| DELETE | /payment_policy/{payment_policy_id} | This method deletes a payment policy. Supply the ID of the policy you want to delete in the paymentPolicyId path parameter. |
| GET | /payment_policy/get_by_policy_name | This method retrieves the details of a specific payment policy. Supply both the policy name and its associated marketplace_id in the request query parameters.   Marketplaces and locales  Get the correct policy for a marketplace that supports multiple locales using the Content-Language request header. For example, get a policy for the French locale of the Canadian marketplace by specifying fr-CA for the Content-Language header. Likewise, target the Dutch locale of the Belgium marketplace by setting Content-Language: nl-BE. For details on header values, see HTTP request headers. |

### payments_program
| Method | Path | Description |
|--------|------|-------------|
| GET | /payments_program/{marketplace_id}/{payments_program_type} | Note: This method is no longer applicable, as all seller accounts globally have been enabled for the new eBay payment and checkout flow.This method returns whether or not the user is opted-in to the specified payments program. Sellers opt-in to payments programs by marketplace and you use the marketplace_id path parameter to specify the marketplace of the status flag you want returned. |
| GET | /payments_program/{marketplace_id}/{payments_program_type}/onboarding | Note: This method is no longer applicable, as all seller accounts globally have been enabled for the new eBay payment and checkout flow.This method retrieves a seller's onboarding status for a payments program for a specified marketplace. The overall onboarding status of the seller and the status of each onboarding step is returned. |

### privilege
| Method | Path | Description |
|--------|------|-------------|
| GET | /privilege | This method retrieves the seller's current set of privileges, including whether or not the seller's eBay registration has been completed, as well as the details of their site-wide sellingLimt (the amount and quantity they can sell on a given day). |

### program
| Method | Path | Description |
|--------|------|-------------|
| GET | /program/get_opted_in_programs | This method gets a list of the seller programs that the seller has opted-in to. |
| POST | /program/opt_in | This method opts the seller in to an eBay seller program. Refer to the Account API overview for information about available eBay seller programs.Note: It can take up to 24-hours for eBay to process your request to opt-in to a Seller Program. Use the getOptedInPrograms call to check the status of your request after the processing period has passed. |
| POST | /program/opt_out | This method opts the seller out of a seller program to which you have previously opted-in to. Get a list of the seller programs you have opted-in to using the getOptedInPrograms call. |

### rate_table
| Method | Path | Description |
|--------|------|-------------|
| GET | /rate_table | This method retrieves a seller's shipping rate tables for the country specified in the country_code query parameter. If you call this method without specifying a country code, the call returns all of the seller's shipping rate tables.  The method's response includes a rateTableId for each table defined by the seller. This rateTableId value is used in add/revise item call or in create/update fulfillment business policy call to specify the shipping rate table to use for that policy's domestic or international shipping options. This call currently supports getting rate tables related to the following marketplaces:EBAY_AU EBAY_CA EBAY_DE EBAY_ES EBAY_FR EBAY_GB EBAY_IT EBAY_US  Note: Rate tables created with the Trading API might not have been assigned a rateTableId at the time of their creation. This method can assign and return rateTableId values for rate tables with missing IDs if you make a request using the country_code where the seller has defined rate tables.  Sellers can define up to 40 shipping rate tables for their account, which lets them set up different rate tables for each of the marketplaces they sell into. Go to Shipping rate tables in  My eBay to create and update rate tables. |

### return_policy
| Method | Path | Description |
|--------|------|-------------|
| GET | /return_policy | This method retrieves all the return policies configured for the marketplace you specify using the marketplace_id query parameter.  Marketplaces and locales  Get the correct policies for a marketplace that supports multiple locales using the Content-Language request header. For example, get the policies for the French locale of the Canadian marketplace by specifying fr-CA for the Content-Language header. Likewise, target the Dutch locale of the Belgium marketplace by setting Content-Language: nl-BE. For details on header values, see HTTP request headers. |
| POST | /return_policy | This method creates a new return policy where the policy encapsulates seller's terms for returning items.  Each policy targets a specific marketplace, and you can create multiple policies for each marketplace. Return policies are not applicable to motor-vehicle listings.A successful request returns the getReturnPolicy URI to the new policy in the Location response header and the ID for the new policy is returned in the response payload.  Tip: For details on creating and using the business policies supported by the Account API, see eBay business policies. |
| GET | /return_policy/{return_policy_id} | This method retrieves the complete details of the return policy specified by the returnPolicyId path parameter. |
| PUT | /return_policy/{return_policy_id} | This method updates an existing return policy. Specify the policy you want to update using the return_policy_id path parameter. Supply a complete policy payload with the updates you want to make; this call overwrites the existing policy with the new details specified in the payload. |
| DELETE | /return_policy/{return_policy_id} | This method deletes a return policy. Supply the ID of the policy you want to delete in the returnPolicyId path parameter. |
| GET | /return_policy/get_by_policy_name | This method retrieves the details of a specific return policy. Supply both the policy name and its associated marketplace_id in the request query parameters.   Marketplaces and locales  Get the correct policy for a marketplace that supports multiple locales using the Content-Language request header. For example, get a policy for the French locale of the Canadian marketplace by specifying fr-CA for the Content-Language header. Likewise, target the Dutch locale of the Belgium marketplace by setting Content-Language: nl-BE. For details on header values, see HTTP request headers. |

### sales_tax
| Method | Path | Description |
|--------|------|-------------|
| GET | /sales_tax/{countryCode}/{jurisdictionId} | This call retrieves the current sales-tax table entry for a specific tax jurisdiction. Specify the jurisdiction to retrieve using the countryCode and jurisdictionId path parameters. All four response fields will be returned if a sales-tax entry exists for the tax jurisdiction. Otherwise, the response will be returned as empty.Note: Sales-tax tables are only available for the US (EBAY_US) and Canada (EBAY_CA) marketplaces.Important! ">Important! In the US, eBay now calculates, collects, and remits sales tax to the proper taxing authorities in all 50 states and Washington, DC. Sellers can no longer specify sales-tax rates for these jurisdictions using a tax table.However, sellers may continue to use a sales-tax table to set rates for the following US territories:American Samoa (AS)Guam (GU)Northern Mariana Islands (MP)Palau (PW)US Virgin Islands (VI)For additional information, refer to Taxes and import charges. |
| PUT | /sales_tax/{countryCode}/{jurisdictionId} | This method creates or updates a sales-tax table entry for a jurisdiction. Specify the tax table entry you want to configure using the two path parameters: countryCode and jurisdictionId.  A tax table entry for a jurisdiction is comprised of two fields: one for the jurisdiction's sales-tax rate and another that's a boolean value indicating whether or not shipping and handling are taxed in the jurisdiction.You can set up sales-tax tables for countries that support different tax jurisdictions.Note: Sales-tax tables are only available for the US (EBAY_US) and Canada (EBAY_CA) marketplaces.Retrieve valid jurisdiction IDs using getSalesTaxJurisdictions in the Metadata API.For details about using this call, refer to Establishing sales-tax tables.Important! ">Important! In the US, eBay now calculates, collects, and remits sales tax to the proper taxing authorities in all 50 states and Washington, DC. Sellers can no longer specify sales-tax rates for these jurisdictions using a tax table.However, sellers may continue to use a sales-tax table to set rates for the following US territories:American Samoa (AS)Guam (GU)Northern Mariana Islands (MP)Palau (PW)US Virgin Islands (VI)For additional information, refer to Taxes and import charges. |
| DELETE | /sales_tax/{countryCode}/{jurisdictionId} | This call deletes a sales-tax table entry for a jurisdiction. Specify the jurisdiction to delete using the countryCode and jurisdictionId path parameters.Note: Sales-tax tables are only available for the US (EBAY_US) and Canada (EBAY_CA) marketplaces. |
| GET | /sales_tax | Use this call to retrieve all sales tax table entries that the seller has defined for a specific country. All four response fields will be returned for each tax jurisdiction that matches the search criteria. Note: Sales-tax tables are only available for the US (EBAY_US) and Canada (EBAY_CA) marketplaces.Important! ">Important! In the US, eBay now calculates, collects, and remits sales tax to the proper taxing authorities in all 50 states and Washington, DC. Sellers can no longer specify sales-tax rates for these jurisdictions using a tax table.However, sellers may continue to use a sales-tax table to set rates for the following US territories:American Samoa (AS)Guam (GU)Northern Mariana Islands (MP)Palau (PW)US Virgin Islands (VI)For additional information, refer to Taxes and import charges. |

### subscription
| Method | Path | Description |
|--------|------|-------------|
| GET | /subscription | This method retrieves a list of subscriptions associated with the seller account. |

### kyc
| Method | Path | Description |
|--------|------|-------------|
| GET | /kyc | Note:This method was originally created to see which onboarding requirements were still pending for sellers being onboarded for eBay managed payments, but now that all seller accounts are onboarded globally, this method should now just returne an empty payload with a 204 No Content HTTP status code. |

### advertising_eligibility
| Method | Path | Description |
|--------|------|-------------|
| GET | /advertising_eligibility | This method allows developers to check the seller eligibility status for eBay advertising programs. |

## Common Questions

Match user requests to endpoints in references/api-spec.lap. Key patterns:
- "List all custom_policy?" -> GET /custom_policy/
- "Create a custom_policy?" -> POST /custom_policy/
- "Get custom_policy details?" -> GET /custom_policy/{custom_policy_id}
- "Update a custom_policy?" -> PUT /custom_policy/{custom_policy_id}
- "Create a fulfillment_policy?" -> POST /fulfillment_policy/
- "Get fulfillment_policy details?" -> GET /fulfillment_policy/{fulfillmentPolicyId}
- "Update a fulfillment_policy?" -> PUT /fulfillment_policy/{fulfillmentPolicyId}
- "Delete a fulfillment_policy?" -> DELETE /fulfillment_policy/{fulfillmentPolicyId}
- "List all fulfillment_policy?" -> GET /fulfillment_policy
- "List all get_by_policy_name?" -> GET /fulfillment_policy/get_by_policy_name
- "List all payment_policy?" -> GET /payment_policy
- "Create a payment_policy?" -> POST /payment_policy
- "Get payment_policy details?" -> GET /payment_policy/{payment_policy_id}
- "Update a payment_policy?" -> PUT /payment_policy/{payment_policy_id}
- "Delete a payment_policy?" -> DELETE /payment_policy/{payment_policy_id}
- "List all get_by_policy_name?" -> GET /payment_policy/get_by_policy_name
- "Get payments_program details?" -> GET /payments_program/{marketplace_id}/{payments_program_type}
- "List all onboarding?" -> GET /payments_program/{marketplace_id}/{payments_program_type}/onboarding
- "List all privilege?" -> GET /privilege
- "List all get_opted_in_programs?" -> GET /program/get_opted_in_programs
- "Create a opt_in?" -> POST /program/opt_in
- "Create a opt_out?" -> POST /program/opt_out
- "List all rate_table?" -> GET /rate_table
- "List all return_policy?" -> GET /return_policy
- "Create a return_policy?" -> POST /return_policy
- "Get return_policy details?" -> GET /return_policy/{return_policy_id}
- "Update a return_policy?" -> PUT /return_policy/{return_policy_id}
- "Delete a return_policy?" -> DELETE /return_policy/{return_policy_id}
- "List all get_by_policy_name?" -> GET /return_policy/get_by_policy_name
- "Get sales_tax details?" -> GET /sales_tax/{countryCode}/{jurisdictionId}
- "Update a sales_tax?" -> PUT /sales_tax/{countryCode}/{jurisdictionId}
- "Delete a sales_tax?" -> DELETE /sales_tax/{countryCode}/{jurisdictionId}
- "List all sales_tax?" -> GET /sales_tax
- "List all subscription?" -> GET /subscription
- "List all kyc?" -> GET /kyc
- "List all advertising_eligibility?" -> GET /advertising_eligibility
- "How to authenticate?" -> See Auth section

## Response Tips
- Check response schemas in references/api-spec.lap for field details
- List endpoints may support pagination; check for limit, offset, or cursor params
- Create/update endpoints typically return the created/updated object

## CLI

```bash
# Update this spec to the latest version
npx @lap-platform/lapsh get account-api -o references/api-spec.lap

# Search for related APIs
npx @lap-platform/lapsh search account-api
```

## References
- Full spec: See references/api-spec.lap for complete endpoint details, parameter tables, and response schemas

> Generated from the official API spec by [LAP](https://lap.sh)
