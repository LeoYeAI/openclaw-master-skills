# Mai Transaction Model

Mai is transaction tracking plus PSP custody state management. Mai itself is not a payment processor or escrow service.

## Statuses

- `draft`: Buyer has expressed intent. No merchant commitment and no stock reservation.
- `quoted`: Merchant has responded with price, payment URL, or terms.
- `confirmed`: Merchant accepted the order. Mai reserves stock at this point.
- `payment_pending`: Buyer is expected to pay externally.
- `paid_external`: Buyer or merchant recorded an external payment reference.
- `fulfilled`: Merchant shipped, delivered, or otherwise fulfilled the order.
- `completed`: Buyer accepted completion.
- `disputed`: Buyer or merchant reports a problem.
- `resolved`: Dispute is resolved but may still need completion or refund.
- `refunded`: Refund was recorded externally.
- `cancelled`: Order is cancelled. Reserved stock is released.

## Allowed Happy Path

`draft -> quoted -> confirmed -> payment_pending -> paid_external -> fulfilled -> completed`

Mai also allows `draft -> confirmed` for simple orders where the merchant confirms directly, and `confirmed -> paid_external` when payment is recorded without a separate pending step.

## Safety Rules

- Do not say money is held in escrow.
- Do not mark an order paid unless a user supplies a payment reference or clear external evidence.
- Confirming an order reserves inventory.
- Cancelling or refunding an order releases reserved inventory.
- Reject status jumps that skip merchant or buyer commitments.
- Keep payment URLs and references as records only; do not open, authenticate, or execute payment flows unless the host environment explicitly supports that and the user confirms.
- For registry payments, record PSP custody states such as `held_by_psp`, `released_to_seller`, and `refunded`. The bundled `demo` provider is development-only and is not proof of real money movement.

## Disputes

Use `disputed` when the buyer or merchant reports wrong item, missing item, delivery failure, payment mismatch, refund request, or quality issue.

Recommended agent response:

1. Summarize the order, status, payment reference, and shipping/tracking evidence.
2. Ask for the minimum missing evidence.
3. Recommend a next status only after the user confirms the resolution.
4. Record the decision as an order history note.
