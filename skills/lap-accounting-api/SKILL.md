---
name: lap-accounting-api
description: "Accounting API skill. Use when working with Accounting for companies. Covers 135 endpoints."
version: 1.0.0
generator: lapsh
metadata:
  openclaw:
    requires:
      env:
        - ACCOUNTING_API_KEY
---

# Accounting API
API version: 3.0.0

## Auth
ApiKey Authorization in header

## Base URL
https://api.codat.io

## Setup
1. Set your API key in the appropriate header
2. GET /companies/{companyId}/connections/{connectionId}/data/accountTransactions -- verify access
3. POST /companies/{companyId}/connections/{connectionId}/push/accounts -- create first accounts

## Endpoints

135 endpoints across 1 groups. See references/api-spec.lap for full details.

### companies
| Method | Path | Description |
|--------|------|-------------|
| GET | /companies/{companyId}/connections/{connectionId}/data/accountTransactions | List account transactions |
| GET | /companies/{companyId}/connections/{connectionId}/data/accountTransactions/{accountTransactionId} | Get account transaction |
| GET | /companies/{companyId}/data/accounts | List accounts |
| GET | /companies/{companyId}/data/accounts/{accountId} | Get account |
| GET | /companies/{companyId}/connections/{connectionId}/options/chartOfAccounts | Get create account model |
| POST | /companies/{companyId}/connections/{connectionId}/push/accounts | Create account |
| GET | /companies/{companyId}/data/billCreditNotes | List bill credit notes |
| GET | /companies/{companyId}/data/billCreditNotes/{billCreditNoteId} | Get bill credit note |
| GET | /companies/{companyId}/connections/{connectionId}/options/billCreditNotes | Get create/update bill credit note model |
| POST | /companies/{companyId}/connections/{connectionId}/push/billCreditNotes | Create bill credit note |
| PUT | /companies/{companyId}/connections/{connectionId}/push/billCreditNotes/{billCreditNoteId} | Update bill credit note |
| POST | /companies/{companyId}/connections/{connectionId}/push/billCreditNotes/{billCreditNoteId}/attachment | Upload bill credit note attachment |
| GET | /companies/{companyId}/data/billPayments | List bill payments |
| GET | /companies/{companyId}/data/billPayments/{billPaymentId} | Get bill payment |
| POST | /companies/{companyId}/connections/{connectionId}/push/billPayments | Create bill payments |
| GET | /companies/{companyId}/connections/{connectionId}/options/billPayments | Get create bill payment model |
| DELETE | /companies/{companyId}/connections/{connectionId}/push/billPayments/{billPaymentId} | Delete bill payment |
| GET | /companies/{companyId}/data/bills | List bills |
| GET | /companies/{companyId}/data/bills/{billId} | Get bill |
| GET | /companies/{companyId}/connections/{connectionId}/options/bills | Get create/update bill model |
| POST | /companies/{companyId}/connections/{connectionId}/push/bills | Create bill |
| PUT | /companies/{companyId}/connections/{connectionId}/push/bills/{billId} | Update bill |
| DELETE | /companies/{companyId}/connections/{connectionId}/push/bills/{billId} | Delete bill |
| GET | /companies/{companyId}/connections/{connectionId}/data/bills/{billId}/attachments | List bill attachments |
| GET | /companies/{companyId}/connections/{connectionId}/data/bills/{billId}/attachments/{attachmentId} | Get bill attachment |
| GET | /companies/{companyId}/connections/{connectionId}/data/bills/{billId}/attachments/{attachmentId}/download | Download bill attachment |
| POST | /companies/{companyId}/connections/{connectionId}/push/bills/{billId}/attachments | Upload bill attachment |
| GET | /companies/{companyId}/data/creditNotes | List credit notes |
| GET | /companies/{companyId}/data/creditNotes/{creditNoteId} | Get credit note |
| GET | /companies/{companyId}/connections/{connectionId}/options/creditNotes | Get create/update credit note model |
| POST | /companies/{companyId}/connections/{connectionId}/push/creditNotes | Create credit note |
| PUT | /companies/{companyId}/connections/{connectionId}/push/creditNotes/{creditNoteId} | Update credit note |
| GET | /companies/{companyId}/data/customers | List customers |
| GET | /companies/{companyId}/data/customers/{customerId} | Get customer |
| GET | /companies/{companyId}/connections/{connectionId}/options/customers | Get create/update customer model |
| POST | /companies/{companyId}/connections/{connectionId}/push/customers | Create customer |
| PUT | /companies/{companyId}/connections/{connectionId}/push/customers/{customerId} | Update customer |
| GET | /companies/{companyId}/connections/{connectionId}/data/customers/{customerId}/attachments | List customer attachments |
| GET | /companies/{companyId}/connections/{connectionId}/data/customers/{customerId}/attachments/{attachmentId} | Get customer attachment |
| GET | /companies/{companyId}/connections/{connectionId}/data/customers/{customerId}/attachments/{attachmentId}/download | Download customer attachment |
| GET | /companies/{companyId}/connections/{connectionId}/data/directCosts | List direct costs |
| GET | /companies/{companyId}/connections/{connectionId}/data/directCosts/{directCostId} | Get direct cost |
| GET | /companies/{companyId}/connections/{connectionId}/options/directCosts | Get create direct cost model |
| POST | /companies/{companyId}/connections/{connectionId}/push/directCosts | Create direct cost |
| DELETE | /companies/{companyId}/connections/{connectionId}/push/directCosts/{directCostId} | Delete direct cost |
| POST | /companies/{companyId}/connections/{connectionId}/push/directCosts/{directCostId}/attachment | Upload direct cost attachment |
| GET | /companies/{companyId}/connections/{connectionId}/data/directCosts/{directCostId}/attachments/{attachmentId} | Get direct cost attachment |
| GET | /companies/{companyId}/connections/{connectionId}/data/directCosts/{directCostId}/attachments/{attachmentId}/download | Download direct cost attachment |
| GET | /companies/{companyId}/connections/{connectionId}/data/directCosts/{directCostId}/attachments | List direct cost attachments |
| GET | /companies/{companyId}/connections/{connectionId}/data/directIncomes | List direct incomes |
| GET | /companies/{companyId}/connections/{connectionId}/data/directIncomes/{directIncomeId} | Get direct income |
| GET | /companies/{companyId}/connections/{connectionId}/options/directIncomes | Get create direct income model |
| POST | /companies/{companyId}/connections/{connectionId}/push/directIncomes | Create direct income |
| POST | /companies/{companyId}/connections/{connectionId}/push/directIncomes/{directIncomeId}/attachment | Create direct income attachment |
| GET | /companies/{companyId}/connections/{connectionId}/data/directIncomes/{directIncomeId}/attachments/{attachmentId} | Get direct income attachment |
| GET | /companies/{companyId}/connections/{connectionId}/data/directIncomes/{directIncomeId}/attachments/{attachmentId}/download | Download direct income attachment |
| GET | /companies/{companyId}/connections/{connectionId}/data/directIncomes/{directIncomeId}/attachments | List direct income attachments |
| GET | /companies/{companyId}/data/financials/balanceSheet | Get balance sheet |
| GET | /companies/{companyId}/data/financials/profitAndLoss | Get profit and loss |
| GET | /companies/{companyId}/data/financials/cashFlowStatement | Get cash flow statement |
| GET | /companies/{companyId}/data/info | Get company info |
| POST | /companies/{companyId}/data/info | Refresh company info |
| GET | /companies/{companyId}/data/invoices | List invoices |
| GET | /companies/{companyId}/data/invoices/{invoiceId} | Get invoice |
| GET | /companies/{companyId}/data/invoices/{invoiceId}/pdf | Get invoice as PDF |
| GET | /companies/{companyId}/connections/{connectionId}/data/invoices/{invoiceId}/attachments | List invoice attachments |
| GET | /companies/{companyId}/connections/{connectionId}/data/invoices/{invoiceId}/attachments/{attachmentId} | Get invoice attachment |
| GET | /companies/{companyId}/connections/{connectionId}/data/invoices/{invoiceId}/attachments/{attachmentId}/download | Download invoice attachment |
| GET | /companies/{companyId}/connections/{connectionId}/options/invoices | Get create/update invoice model |
| POST | /companies/{companyId}/connections/{connectionId}/push/invoices | Create invoice |
| PUT | /companies/{companyId}/connections/{connectionId}/push/invoices/{invoiceId} | Update invoice |
| DELETE | /companies/{companyId}/connections/{connectionId}/push/invoices/{invoiceId} | Delete invoice |
| POST | /companies/{companyId}/connections/{connectionId}/push/invoices/{invoiceId}/attachment | Upload invoice attachment |
| GET | /companies/{companyId}/connections/{connectionId}/data/itemReceipts | List item receipts |
| GET | /companies/{companyId}/connections/{connectionId}/data/itemReceipts/{itemReceiptId} | Get item receipt |
| GET | /companies/{companyId}/data/items | List items |
| GET | /companies/{companyId}/data/items/{itemId} | Get item |
| GET | /companies/{companyId}/connections/{connectionId}/options/items | Get create item model |
| POST | /companies/{companyId}/connections/{connectionId}/push/items | Create item |
| GET | /companies/{companyId}/data/journalEntries | List journal entries |
| GET | /companies/{companyId}/data/journalEntries/{journalEntryId} | Get journal entry |
| GET | /companies/{companyId}/connections/{connectionId}/options/journalEntries | Get create journal entry model |
| POST | /companies/{companyId}/connections/{connectionId}/push/journalEntries | Create journal entry |
| DELETE | /companies/{companyId}/connections/{connectionId}/push/journalEntries/{journalEntryId} | Delete journal entry |
| GET | /companies/{companyId}/data/journals | List journals |
| GET | /companies/{companyId}/data/journals/{journalId} | Get journal |
| GET | /companies/{companyId}/connections/{connectionId}/options/journals | Get create journal model |
| POST | /companies/{companyId}/connections/{connectionId}/push/journals | Create journal |
| GET | /companies/{companyId}/data/paymentMethods | List payment methods |
| GET | /companies/{companyId}/data/paymentMethods/{paymentMethodId} | Get payment method |
| GET | /companies/{companyId}/data/payments | List payments |
| GET | /companies/{companyId}/data/payments/{paymentId} | Get payment |
| GET | /companies/{companyId}/connections/{connectionId}/data/payments | List payments |
| GET | /companies/{companyId}/connections/{connectionId}/options/payments | Get create payment model |
| POST | /companies/{companyId}/connections/{connectionId}/push/payments | Create payment |
| GET | /companies/{companyId}/data/purchaseOrders | List purchase orders |
| GET | /companies/{companyId}/data/purchaseOrders/{purchaseOrderId} | Get purchase order |
| GET | /companies/{companyId}/connections/{connectionId}/options/purchaseOrders | Get create/update purchase order model |
| POST | /companies/{companyId}/connections/{connectionId}/push/purchaseOrders | Create purchase order |
| PUT | /companies/{companyId}/connections/{connectionId}/push/purchaseOrders/{purchaseOrderId} | Update purchase order |
| GET | /companies/{companyId}/data/purchaseOrders/{purchaseOrderId}/pdf | Download purchase order as PDF |
| GET | /companies/{companyId}/connections/{connectionId}/data/purchaseOrders/{purchaseOrderId}/attachments | List purchase order attachments |
| GET | /companies/{companyId}/connections/{connectionId}/data/purchaseOrders/{purchaseOrderId}/attachments/{attachmentId} | Get purchase order attachment |
| GET | /companies/{companyId}/connections/{connectionId}/data/purchaseOrders/{purchaseOrderId}/attachments/{attachmentId}/download | Download purchase order attachment |
| GET | /companies/{companyId}/data/salesOrders | List sales orders |
| GET | /companies/{companyId}/data/salesOrders/{salesOrderId} | Get sales order |
| GET | /companies/{companyId}/data/suppliers | List suppliers |
| GET | /companies/{companyId}/data/suppliers/{supplierId} | Get supplier |
| GET | /companies/{companyId}/connections/{connectionId}/options/suppliers | Get create/update supplier model |
| POST | /companies/{companyId}/connections/{connectionId}/push/suppliers | Create supplier |
| PUT | /companies/{companyId}/connections/{connectionId}/push/suppliers/{supplierId} | Update supplier |
| GET | /companies/{companyId}/connections/{connectionId}/data/suppliers/{supplierId}/attachments | List supplier attachments |
| GET | /companies/{companyId}/connections/{connectionId}/data/suppliers/{supplierId}/attachments/{attachmentId} | Get supplier attachment |
| GET | /companies/{companyId}/connections/{connectionId}/data/suppliers/{supplierId}/attachments/{attachmentId}/download | Download supplier attachment |
| GET | /companies/{companyId}/data/taxRates | List all tax rates |
| GET | /companies/{companyId}/data/taxRates/{taxRateId} | Get tax rate |
| GET | /companies/{companyId}/data/trackingCategories | List tracking categories |
| GET | /companies/{companyId}/data/trackingCategories/{trackingCategoryId} | Get tracking categories |
| GET | /companies/{companyId}/connections/{connectionId}/data/transfers | List transfers |
| POST | /companies/{companyId}/connections/{connectionId}/push/transfers/{transferId}/attachment | Upload transfer attachment |
| GET | /companies/{companyId}/connections/{connectionId}/data/transfers/{transferId} | Get transfer |
| GET | /companies/{companyId}/connections/{connectionId}/options/transfers | Get create transfer model |
| POST | /companies/{companyId}/connections/{connectionId}/push/transfers | Create transfer |
| GET | /companies/{companyId}/connections/{connectionId}/data/bankAccounts | List bank accounts |
| GET | /companies/{companyId}/connections/{connectionId}/data/bankAccounts/{accountId} | Get bank account |
| GET | /companies/{companyId}/connections/{connectionId}/options/bankAccounts | Get create/update bank account model |
| POST | /companies/{companyId}/connections/{connectionId}/push/bankAccounts | Create bank account |
| PUT | /companies/{companyId}/connections/{connectionId}/push/bankAccounts/{bankAccountId} | Update bank account |
| GET | /companies/{companyId}/connections/{connectionId}/data/bankAccounts/{accountId}/bankTransactions | List bank account transactions |
| GET | /companies/{companyId}/connections/{connectionId}/options/bankAccounts/{accountId}/bankTransactions | Get create bank account transactions model |
| POST | /companies/{companyId}/connections/{connectionId}/push/bankAccounts/{accountId}/bankTransactions | Create bank account transactions |
| GET | /companies/{companyId}/reports/agedDebtor/available | Aged debtors report available |
| GET | /companies/{companyId}/reports/agedDebtor | Aged debtors report |
| GET | /companies/{companyId}/reports/agedCreditor/available | Aged creditors report available |
| GET | /companies/{companyId}/reports/agedCreditor | Aged creditors report |

## Common Questions

Match user requests to endpoints in references/api-spec.lap. Key patterns:
- "Search accountTransactions?" -> GET /companies/{companyId}/connections/{connectionId}/data/accountTransactions
- "Get accountTransaction details?" -> GET /companies/{companyId}/connections/{connectionId}/data/accountTransactions/{accountTransactionId}
- "Search accounts?" -> GET /companies/{companyId}/data/accounts
- "Get account details?" -> GET /companies/{companyId}/data/accounts/{accountId}
- "List all chartOfAccounts?" -> GET /companies/{companyId}/connections/{connectionId}/options/chartOfAccounts
- "Create a account?" -> POST /companies/{companyId}/connections/{connectionId}/push/accounts
- "Search billCreditNotes?" -> GET /companies/{companyId}/data/billCreditNotes
- "Get billCreditNote details?" -> GET /companies/{companyId}/data/billCreditNotes/{billCreditNoteId}
- "List all billCreditNotes?" -> GET /companies/{companyId}/connections/{connectionId}/options/billCreditNotes
- "Create a billCreditNote?" -> POST /companies/{companyId}/connections/{connectionId}/push/billCreditNotes
- "Update a billCreditNote?" -> PUT /companies/{companyId}/connections/{connectionId}/push/billCreditNotes/{billCreditNoteId}
- "Create a attachment?" -> POST /companies/{companyId}/connections/{connectionId}/push/billCreditNotes/{billCreditNoteId}/attachment
- "Search billPayments?" -> GET /companies/{companyId}/data/billPayments
- "Get billPayment details?" -> GET /companies/{companyId}/data/billPayments/{billPaymentId}
- "Create a billPayment?" -> POST /companies/{companyId}/connections/{connectionId}/push/billPayments
- "List all billPayments?" -> GET /companies/{companyId}/connections/{connectionId}/options/billPayments
- "Delete a billPayment?" -> DELETE /companies/{companyId}/connections/{connectionId}/push/billPayments/{billPaymentId}
- "Search bills?" -> GET /companies/{companyId}/data/bills
- "Get bill details?" -> GET /companies/{companyId}/data/bills/{billId}
- "List all bills?" -> GET /companies/{companyId}/connections/{connectionId}/options/bills
- "Create a bill?" -> POST /companies/{companyId}/connections/{connectionId}/push/bills
- "Update a bill?" -> PUT /companies/{companyId}/connections/{connectionId}/push/bills/{billId}
- "Delete a bill?" -> DELETE /companies/{companyId}/connections/{connectionId}/push/bills/{billId}
- "List all attachments?" -> GET /companies/{companyId}/connections/{connectionId}/data/bills/{billId}/attachments
- "Get attachment details?" -> GET /companies/{companyId}/connections/{connectionId}/data/bills/{billId}/attachments/{attachmentId}
- "List all download?" -> GET /companies/{companyId}/connections/{connectionId}/data/bills/{billId}/attachments/{attachmentId}/download
- "Create a attachment?" -> POST /companies/{companyId}/connections/{connectionId}/push/bills/{billId}/attachments
- "Search creditNotes?" -> GET /companies/{companyId}/data/creditNotes
- "Get creditNote details?" -> GET /companies/{companyId}/data/creditNotes/{creditNoteId}
- "List all creditNotes?" -> GET /companies/{companyId}/connections/{connectionId}/options/creditNotes
- "Create a creditNote?" -> POST /companies/{companyId}/connections/{connectionId}/push/creditNotes
- "Update a creditNote?" -> PUT /companies/{companyId}/connections/{connectionId}/push/creditNotes/{creditNoteId}
- "Search customers?" -> GET /companies/{companyId}/data/customers
- "Get customer details?" -> GET /companies/{companyId}/data/customers/{customerId}
- "List all customers?" -> GET /companies/{companyId}/connections/{connectionId}/options/customers
- "Create a customer?" -> POST /companies/{companyId}/connections/{connectionId}/push/customers
- "Update a customer?" -> PUT /companies/{companyId}/connections/{connectionId}/push/customers/{customerId}
- "List all attachments?" -> GET /companies/{companyId}/connections/{connectionId}/data/customers/{customerId}/attachments
- "Get attachment details?" -> GET /companies/{companyId}/connections/{connectionId}/data/customers/{customerId}/attachments/{attachmentId}
- "List all download?" -> GET /companies/{companyId}/connections/{connectionId}/data/customers/{customerId}/attachments/{attachmentId}/download
- "Search directCosts?" -> GET /companies/{companyId}/connections/{connectionId}/data/directCosts
- "Get directCost details?" -> GET /companies/{companyId}/connections/{connectionId}/data/directCosts/{directCostId}
- "List all directCosts?" -> GET /companies/{companyId}/connections/{connectionId}/options/directCosts
- "Create a directCost?" -> POST /companies/{companyId}/connections/{connectionId}/push/directCosts
- "Delete a directCost?" -> DELETE /companies/{companyId}/connections/{connectionId}/push/directCosts/{directCostId}
- "Create a attachment?" -> POST /companies/{companyId}/connections/{connectionId}/push/directCosts/{directCostId}/attachment
- "Get attachment details?" -> GET /companies/{companyId}/connections/{connectionId}/data/directCosts/{directCostId}/attachments/{attachmentId}
- "List all download?" -> GET /companies/{companyId}/connections/{connectionId}/data/directCosts/{directCostId}/attachments/{attachmentId}/download
- "List all attachments?" -> GET /companies/{companyId}/connections/{connectionId}/data/directCosts/{directCostId}/attachments
- "Search directIncomes?" -> GET /companies/{companyId}/connections/{connectionId}/data/directIncomes
- "Get directIncome details?" -> GET /companies/{companyId}/connections/{connectionId}/data/directIncomes/{directIncomeId}
- "List all directIncomes?" -> GET /companies/{companyId}/connections/{connectionId}/options/directIncomes
- "Create a directIncome?" -> POST /companies/{companyId}/connections/{connectionId}/push/directIncomes
- "Create a attachment?" -> POST /companies/{companyId}/connections/{connectionId}/push/directIncomes/{directIncomeId}/attachment
- "Get attachment details?" -> GET /companies/{companyId}/connections/{connectionId}/data/directIncomes/{directIncomeId}/attachments/{attachmentId}
- "List all download?" -> GET /companies/{companyId}/connections/{connectionId}/data/directIncomes/{directIncomeId}/attachments/{attachmentId}/download
- "List all attachments?" -> GET /companies/{companyId}/connections/{connectionId}/data/directIncomes/{directIncomeId}/attachments
- "List all balanceSheet?" -> GET /companies/{companyId}/data/financials/balanceSheet
- "List all profitAndLoss?" -> GET /companies/{companyId}/data/financials/profitAndLoss
- "List all cashFlowStatement?" -> GET /companies/{companyId}/data/financials/cashFlowStatement
- "List all info?" -> GET /companies/{companyId}/data/info
- "Create a info?" -> POST /companies/{companyId}/data/info
- "Search invoices?" -> GET /companies/{companyId}/data/invoices
- "Get invoice details?" -> GET /companies/{companyId}/data/invoices/{invoiceId}
- "List all pdf?" -> GET /companies/{companyId}/data/invoices/{invoiceId}/pdf
- "List all attachments?" -> GET /companies/{companyId}/connections/{connectionId}/data/invoices/{invoiceId}/attachments
- "Get attachment details?" -> GET /companies/{companyId}/connections/{connectionId}/data/invoices/{invoiceId}/attachments/{attachmentId}
- "List all download?" -> GET /companies/{companyId}/connections/{connectionId}/data/invoices/{invoiceId}/attachments/{attachmentId}/download
- "List all invoices?" -> GET /companies/{companyId}/connections/{connectionId}/options/invoices
- "Create a invoice?" -> POST /companies/{companyId}/connections/{connectionId}/push/invoices
- "Update a invoice?" -> PUT /companies/{companyId}/connections/{connectionId}/push/invoices/{invoiceId}
- "Delete a invoice?" -> DELETE /companies/{companyId}/connections/{connectionId}/push/invoices/{invoiceId}
- "Create a attachment?" -> POST /companies/{companyId}/connections/{connectionId}/push/invoices/{invoiceId}/attachment
- "Search itemReceipts?" -> GET /companies/{companyId}/connections/{connectionId}/data/itemReceipts
- "Get itemReceipt details?" -> GET /companies/{companyId}/connections/{connectionId}/data/itemReceipts/{itemReceiptId}
- "Search items?" -> GET /companies/{companyId}/data/items
- "Get item details?" -> GET /companies/{companyId}/data/items/{itemId}
- "List all items?" -> GET /companies/{companyId}/connections/{connectionId}/options/items
- "Create a item?" -> POST /companies/{companyId}/connections/{connectionId}/push/items
- "Search journalEntries?" -> GET /companies/{companyId}/data/journalEntries
- "Get journalEntry details?" -> GET /companies/{companyId}/data/journalEntries/{journalEntryId}
- "List all journalEntries?" -> GET /companies/{companyId}/connections/{connectionId}/options/journalEntries
- "Create a journalEntry?" -> POST /companies/{companyId}/connections/{connectionId}/push/journalEntries
- "Delete a journalEntry?" -> DELETE /companies/{companyId}/connections/{connectionId}/push/journalEntries/{journalEntryId}
- "Search journals?" -> GET /companies/{companyId}/data/journals
- "Get journal details?" -> GET /companies/{companyId}/data/journals/{journalId}
- "List all journals?" -> GET /companies/{companyId}/connections/{connectionId}/options/journals
- "Create a journal?" -> POST /companies/{companyId}/connections/{connectionId}/push/journals
- "Search paymentMethods?" -> GET /companies/{companyId}/data/paymentMethods
- "Get paymentMethod details?" -> GET /companies/{companyId}/data/paymentMethods/{paymentMethodId}
- "Search payments?" -> GET /companies/{companyId}/data/payments
- "Get payment details?" -> GET /companies/{companyId}/data/payments/{paymentId}
- "Search payments?" -> GET /companies/{companyId}/connections/{connectionId}/data/payments
- "List all payments?" -> GET /companies/{companyId}/connections/{connectionId}/options/payments
- "Create a payment?" -> POST /companies/{companyId}/connections/{connectionId}/push/payments
- "Search purchaseOrders?" -> GET /companies/{companyId}/data/purchaseOrders
- "Get purchaseOrder details?" -> GET /companies/{companyId}/data/purchaseOrders/{purchaseOrderId}
- "List all purchaseOrders?" -> GET /companies/{companyId}/connections/{connectionId}/options/purchaseOrders
- "Create a purchaseOrder?" -> POST /companies/{companyId}/connections/{connectionId}/push/purchaseOrders
- "Update a purchaseOrder?" -> PUT /companies/{companyId}/connections/{connectionId}/push/purchaseOrders/{purchaseOrderId}
- "List all pdf?" -> GET /companies/{companyId}/data/purchaseOrders/{purchaseOrderId}/pdf
- "List all attachments?" -> GET /companies/{companyId}/connections/{connectionId}/data/purchaseOrders/{purchaseOrderId}/attachments
- "Get attachment details?" -> GET /companies/{companyId}/connections/{connectionId}/data/purchaseOrders/{purchaseOrderId}/attachments/{attachmentId}
- "List all download?" -> GET /companies/{companyId}/connections/{connectionId}/data/purchaseOrders/{purchaseOrderId}/attachments/{attachmentId}/download
- "Search salesOrders?" -> GET /companies/{companyId}/data/salesOrders
- "Get salesOrder details?" -> GET /companies/{companyId}/data/salesOrders/{salesOrderId}
- "Search suppliers?" -> GET /companies/{companyId}/data/suppliers
- "Get supplier details?" -> GET /companies/{companyId}/data/suppliers/{supplierId}
- "List all suppliers?" -> GET /companies/{companyId}/connections/{connectionId}/options/suppliers
- "Create a supplier?" -> POST /companies/{companyId}/connections/{connectionId}/push/suppliers
- "Update a supplier?" -> PUT /companies/{companyId}/connections/{connectionId}/push/suppliers/{supplierId}
- "List all attachments?" -> GET /companies/{companyId}/connections/{connectionId}/data/suppliers/{supplierId}/attachments
- "Get attachment details?" -> GET /companies/{companyId}/connections/{connectionId}/data/suppliers/{supplierId}/attachments/{attachmentId}
- "List all download?" -> GET /companies/{companyId}/connections/{connectionId}/data/suppliers/{supplierId}/attachments/{attachmentId}/download
- "Search taxRates?" -> GET /companies/{companyId}/data/taxRates
- "Get taxRate details?" -> GET /companies/{companyId}/data/taxRates/{taxRateId}
- "Search trackingCategories?" -> GET /companies/{companyId}/data/trackingCategories
- "Get trackingCategory details?" -> GET /companies/{companyId}/data/trackingCategories/{trackingCategoryId}
- "Search transfers?" -> GET /companies/{companyId}/connections/{connectionId}/data/transfers
- "Create a attachment?" -> POST /companies/{companyId}/connections/{connectionId}/push/transfers/{transferId}/attachment
- "Get transfer details?" -> GET /companies/{companyId}/connections/{connectionId}/data/transfers/{transferId}
- "List all transfers?" -> GET /companies/{companyId}/connections/{connectionId}/options/transfers
- "Create a transfer?" -> POST /companies/{companyId}/connections/{connectionId}/push/transfers
- "Search bankAccounts?" -> GET /companies/{companyId}/connections/{connectionId}/data/bankAccounts
- "Get bankAccount details?" -> GET /companies/{companyId}/connections/{connectionId}/data/bankAccounts/{accountId}
- "List all bankAccounts?" -> GET /companies/{companyId}/connections/{connectionId}/options/bankAccounts
- "Create a bankAccount?" -> POST /companies/{companyId}/connections/{connectionId}/push/bankAccounts
- "Update a bankAccount?" -> PUT /companies/{companyId}/connections/{connectionId}/push/bankAccounts/{bankAccountId}
- "Search bankTransactions?" -> GET /companies/{companyId}/connections/{connectionId}/data/bankAccounts/{accountId}/bankTransactions
- "List all bankTransactions?" -> GET /companies/{companyId}/connections/{connectionId}/options/bankAccounts/{accountId}/bankTransactions
- "Create a bankTransaction?" -> POST /companies/{companyId}/connections/{connectionId}/push/bankAccounts/{accountId}/bankTransactions
- "List all available?" -> GET /companies/{companyId}/reports/agedDebtor/available
- "List all agedDebtor?" -> GET /companies/{companyId}/reports/agedDebtor
- "List all available?" -> GET /companies/{companyId}/reports/agedCreditor/available
- "List all agedCreditor?" -> GET /companies/{companyId}/reports/agedCreditor
- "How to authenticate?" -> See Auth section

## Response Tips
- Check response schemas in references/api-spec.lap for field details
- List endpoints may support pagination; check for limit, offset, or cursor params
- Create/update endpoints typically return the created/updated object

## CLI

```bash
# Update this spec to the latest version
npx @lap-platform/lapsh get accounting-api -o references/api-spec.lap

# Search for related APIs
npx @lap-platform/lapsh search accounting-api
```

## References
- Full spec: See references/api-spec.lap for complete endpoint details, parameter tables, and response schemas

> Generated from the official API spec by [LAP](https://lap.sh)
