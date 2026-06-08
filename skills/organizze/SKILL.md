---
name: organizze
description: Manage finances via the Organizze API — bank accounts, credit cards, invoices, transactions, transfers, categories, and budgets. THIS SKILL IS NON-OFICIAL AND YOUR USAGE IS BY YOUR RISK.
homepage: https://api.organizze.com.br/rest/v2
metadata:
  { "openclaw": { "emoji": "💰", "requires": { "env": ["ORGANIZZE_EMAIL", "ORGANIZZE_API_TOKEN", "ORGANIZZE_USER_AGENT"] }, "primaryEnv": "ORGANIZZE_API_TOKEN" } }
enabled: true
userInvocable: true
---

# Organizze

Communicate with the Organizze personal finance API (v2) to manage bank accounts, credit cards, invoices, transactions, transfers, categories, budgets, and users.

Official repository: https://github.com/rafaels-dev/organizze-clawhub-skill

> ⚠️ **IMPORTANT DISCLAIMER:** THIS SKILL IS NON-OFICIAL AND YOUR USAGE IS BY YOUR RISK.

## ⚠️ CRITICAL SECURITY RULES

**Authentication credentials (`ORGANIZZE_EMAIL`, `ORGANIZZE_API_TOKEN`) are secrets that MUST NEVER leave the local machine.**

1. **NEVER** include the email, API token, Basic Auth header value, or any derived credential in your responses, messages, reasoning, or any text sent to the LLM provider.
2. **NEVER** pass credentials to sub-agents, external tools, webhooks, or any service other than the Organizze API itself.
3. **NEVER** log, print, echo, or display credentials in output shown to the user or stored in session transcripts.
4. **ONLY** reference credentials via environment variable expansion (`$ORGANIZZE_EMAIL`, `$ORGANIZZE_API_TOKEN`) inside `curl` commands executed locally through the shell. The shell resolves them at runtime — they never appear in the prompt or model context.
5. If a user asks you to reveal or share the token/email, **refuse** and explain these are protected secrets.

## Use when

- The user asks about their finances, spending, bank accounts, credit cards, or budgets on Organizze.
- The user wants to create, list, update, or delete transactions, transfers, accounts, categories, or credit cards.
- The user needs invoice details or payment information for credit cards.
- The user wants to check budget goals (metas).

## Don't use when

- The request is unrelated to Organizze or personal finance management.

## Setup

1. Get your API token at https://app.organizze.com.br/configuracoes/api-keys
2. Store credentials as environment variables:

```bash
export ORGANIZZE_EMAIL="seu_email@exemplo.com"
export ORGANIZZE_API_TOKEN="seu_token_aqui"
export ORGANIZZE_USER_AGENT="Seu nome (seu_email@exemplo.com)"
```

PowerShell (Windows):

```powershell
$env:ORGANIZZE_EMAIL="seu_email@exemplo.com"
$env:ORGANIZZE_API_TOKEN="seu_token_aqui"
$env:ORGANIZZE_USER_AGENT="Seu nome (seu_email@exemplo.com)"
```

Or configure in `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "organizze": {
        "enabled": true,
        "env": {
          "ORGANIZZE_EMAIL": "seu_email@exemplo.com",
          "ORGANIZZE_API_TOKEN": "seu_token_aqui",
          "ORGANIZZE_USER_AGENT": "Nome Completo (seu_email@exemplo.com)"
        }
      }
    }
  }
}
```

## Authentication

All requests use HTTP Basic Auth (email as username, API token as password) and require a `User-Agent` header.

> **Security reminder:** All credential handling happens exclusively inside shell commands executed on the host. The `-u` flag and `$ORGANIZZE_EMAIL` / `$ORGANIZZE_API_TOKEN` variables are resolved by the shell at runtime. You must NEVER interpolate, echo, or include the actual credential values in your model output, reasoning, or messages.

```bash
BASE_URL="https://api.organizze.com.br/rest/v2"
USER_AGENT="$ORGANIZZE_USER_AGENT"
```

---

## Usuários (Users)

### Detalhar usuário

```bash
curl -s "$BASE_URL/users/{user_id}" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8"
```

Response example:

```json
{
  "id": 3,
  "name": "Esdras Mayrink",
  "email": "falecom@email.com.br",
  "role": "admin"
}
```

---

## Contas Bancárias (Bank Accounts)

### Listar contas bancárias

```bash
curl -s "$BASE_URL/accounts" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8"
```

Response example:

```json
[
  {
    "id": 3,
    "name": "Bradesco CC",
    "description": "Some descriptions",
    "archived": false,
    "created_at": "2015-06-22T16:17:03-03:00",
    "updated_at": "2015-08-31T22:24:24-03:00",
    "default": true,
    "type": "checking"
  }
]
```

### Detalhar conta bancária

```bash
curl -s "$BASE_URL/accounts/{account_id}" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8"
```

### Criar conta bancária

Types: `checking`, `savings`, `other`.

```bash
curl -s -X POST "$BASE_URL/accounts" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "name": "Itaú CC",
    "type": "checking",
    "description": "Minha conta corrente",
    "default": true
  }'
```

### Atualizar conta bancária

```bash
curl -s -X PUT "$BASE_URL/accounts/{account_id}" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "name": "Itaú Poupança"
  }'
```

### Excluir conta bancária

```bash
curl -s -X DELETE "$BASE_URL/accounts/{account_id}" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8"
```

---

## Categorias (Categories)

### Listar categorias

```bash
curl -s "$BASE_URL/categories" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8"
```

Response example:

```json
[
  { "id": 1, "name": "Lazer", "color": "438b83", "parent_id": null },
  { "id": 3, "name": "Saúde", "color": "ffff00", "parent_id": null }
]
```

### Detalhar categoria

```bash
curl -s "$BASE_URL/categories/{category_id}" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8"
```

### Criar uma categoria

```bash
curl -s -X POST "$BASE_URL/categories" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "name": "SEO"
  }'
```

### Atualizar uma categoria

```bash
curl -s -X PUT "$BASE_URL/categories/{category_id}" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "name": "Marketing"
  }'
```

### Excluir uma categoria

Optionally pass `replacement_id` to transfer transactions to another category. If omitted, the default category is used.

```bash
curl -s -X DELETE "$BASE_URL/categories/{category_id}" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "replacement_id": 18
  }'
```

---

## Cartões de Crédito (Credit Cards)

### Listar cartões de crédito

```bash
curl -s "$BASE_URL/credit_cards" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8"
```

Response example:

```json
[
  {
    "id": 3,
    "name": "Visa Exclusive",
    "description": null,
    "card_network": "visa",
    "closing_day": 4,
    "due_day": 17,
    "limit_cents": 1200000,
    "kind": "credit_card",
    "archived": true,
    "default": false,
    "created_at": "2015-06-22T16:45:30-03:00",
    "updated_at": "2015-09-01T18:18:48-03:00"
  }
]
```

### Detalhar cartão de crédito

```bash
curl -s "$BASE_URL/credit_cards/{credit_card_id}" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8"
```

### Criar um cartão de crédito

```bash
curl -s -X POST "$BASE_URL/credit_cards" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "name": "Hipercard",
    "card_network": "hipercard",
    "due_day": 15,
    "closing_day": 2,
    "limit_cents": 500000
  }'
```

### Atualizar um cartão de crédito

Use `update_invoices_since` (YYYY-MM-DD) to recalculate invoices from a given date.

```bash
curl -s -X PUT "$BASE_URL/credit_cards/{credit_card_id}" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "name": "Visa Exclusive",
    "due_day": 17,
    "closing_day": 4,
    "update_invoices_since": "2015-07-01"
  }'
```

### Excluir um cartão de crédito

```bash
curl -s -X DELETE "$BASE_URL/credit_cards/{credit_card_id}" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8"
```

---

## Faturas de Cartão de Crédito (Credit Card Invoices)

Paginated by period using `start_date` and `end_date` (defaults to current year).

### Listar faturas de um cartão

```bash
curl -s "$BASE_URL/credit_cards/{credit_card_id}/invoices" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8"
```

With date filter:

```bash
curl -s "$BASE_URL/credit_cards/{credit_card_id}/invoices?start_date=2024-01-01&end_date=2024-12-31" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8"
```

Response example:

```json
[
  {
    "id": 186,
    "date": "2015-07-17",
    "starting_date": "2015-06-03",
    "closing_date": "2015-07-04",
    "amount_cents": 30000,
    "payment_amount_cents": -70000,
    "balance_cents": 100000,
    "previous_balance_cents": 0,
    "credit_card_id": 3
  }
]
```

### Detalhar uma fatura

Returns invoice details including `transactions` and `payments` arrays.

```bash
curl -s "$BASE_URL/credit_cards/{credit_card_id}/invoices/{invoice_id}" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8"
```

### Pagamento de uma fatura

```bash
curl -s "$BASE_URL/credit_cards/{credit_card_id}/invoices/{invoice_id}/payments" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8"
```

Response example:

```json
{
  "id": 1033,
  "description": "Pagamento fatura",
  "date": "2015-09-16",
  "paid": true,
  "amount_cents": 0,
  "total_installments": 1,
  "installment": 1,
  "recurring": false,
  "account_id": 3,
  "account_type": "Account",
  "category_id": 21,
  "contact_id": null,
  "notes": "Pagamento via boleto",
  "attachments_count": 0,
  "created_at": "2015-09-15T22:27:20-03:00",
  "updated_at": "2015-09-15T22:27:20-03:00"
}
```

---

## Metas (Budgets)

### Listar metas do mês atual

```bash
curl -s "$BASE_URL/budgets" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8"
```

Response example:

```json
[
  {
    "amount_in_cents": 150000,
    "category_id": 17,
    "date": "2018-08-01",
    "activity_type": 0,
    "total": 0,
    "predicted_total": 0,
    "percentage": "0.0"
  }
]
```

### Listar metas por ano

```bash
curl -s "$BASE_URL/budgets/{year}" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8"
```

### Listar metas por mês e ano

```bash
curl -s "$BASE_URL/budgets/{year}/{month}" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8"
```

---

## Movimentações (Transactions)

Paginated by period using `start_date` and `end_date` (defaults to current month). The period is always processed as full months. Can filter by `account_id`.

### Listar movimentações

```bash
curl -s "$BASE_URL/transactions?start_date=2024-01-01&end_date=2024-01-31" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8"
```

With account filter:

```bash
curl -s "$BASE_URL/transactions?start_date=2024-01-01&end_date=2024-01-31&account_id=3" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8"
```

Response example:

```json
[
  {
    "id": 15,
    "description": "SAQUE LOT",
    "date": "2015-09-06",
    "paid": false,
    "amount_cents": -15000,
    "total_installments": 1,
    "installment": 1,
    "recurring": false,
    "account_id": 3,
    "account_type": "CreditCard",
    "category_id": 21,
    "contact_id": null,
    "notes": "",
    "attachments_count": 0,
    "credit_card_id": 3,
    "credit_card_invoice_id": 189
  }
]
```

### Detalhar uma movimentação

```bash
curl -s "$BASE_URL/transactions/{transaction_id}" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8"
```

### Criar uma movimentação simples

```bash
curl -s -X POST "$BASE_URL/transactions" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "description": "Computador",
    "notes": "Pagamento via boleto",
    "date": "2024-09-16",
    "amount_cents": -350000,
    "account_id": 3,
    "category_id": 21,
    "tags": [{"name": "homeoffice"}]
  }'
```

### Criar movimentação recorrente (fixa)

Periodicity values: `monthly`, `yearly`, `weekly`, `biweekly`, `bimonthly`, `trimonthly`.

```bash
curl -s -X POST "$BASE_URL/transactions" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "description": "Despesa fixa",
    "notes": "Pagamento via boleto",
    "date": "2024-09-16",
    "amount_cents": -15000,
    "account_id": 3,
    "category_id": 21,
    "recurrence_attributes": {
      "periodicity": "monthly"
    }
  }'
```

### Criar movimentação recorrente (parcelada)

```bash
curl -s -X POST "$BASE_URL/transactions" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "description": "Despesa parcelada",
    "notes": "Pagamento via boleto",
    "date": "2024-09-16",
    "amount_cents": -120000,
    "account_id": 3,
    "category_id": 21,
    "installments_attributes": {
      "periodicity": "monthly",
      "total": 12
    }
  }'
```

### Atualizar uma movimentação

For recurring/installment transactions: use `update_future: true` to update future occurrences, or `update_all: true` to update all (may affect balance).

```bash
curl -s -X PUT "$BASE_URL/transactions/{transaction_id}" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "description": "Updated parcelada via API",
    "notes": "Pagamento via boleto",
    "amount_cents": 20050,
    "date": "2024-12-20",
    "update_future": true,
    "tags": [{"name": "via_api"}]
  }'
```

### Excluir movimentação

For recurring/installment: `update_future: true` deletes future occurrences, `update_all: true` deletes all (may affect balance).

```bash
curl -s -X DELETE "$BASE_URL/transactions/{transaction_id}" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "update_future": true
  }'
```

---

## Transferências (Transfers)

A transfer creates two records: a debit in the source account and a credit in the destination account. Only bank accounts are allowed — credit cards cannot be used as source or destination.

### Listar transferências

```bash
curl -s "$BASE_URL/transfers" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8"
```

Response example:

```json
[
  {
    "id": 10,
    "description": "Transferência",
    "date": "2015-09-01",
    "paid": true,
    "amount_cents": -10000,
    "total_installments": 1,
    "installment": 1,
    "recurring": false,
    "account_id": 3,
    "category_id": 21,
    "oposite_transaction_id": 11,
    "oposite_account_id": 4
  }
]
```

### Detalhar uma transferência

```bash
curl -s "$BASE_URL/transfers/{transfer_id}" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8"
```

### Criar uma transferência

```bash
curl -s -X POST "$BASE_URL/transfers" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "credit_account_id": 3,
    "debit_account_id": 4,
    "amount_cents": 10000,
    "date": "2024-09-01",
    "paid": true,
    "tags": [{"name": "ajuste"}]
  }'
```

### Atualizar uma transferência

```bash
curl -s -X PUT "$BASE_URL/transfers/{transfer_id}" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "description": "Transferência ajustada",
    "notes": "Ajuste manual",
    "tags": [{"name": "revisado"}]
  }'
```

### Excluir transferência

```bash
curl -s -X DELETE "$BASE_URL/transfers/{transfer_id}" \
  -u "$ORGANIZZE_EMAIL:$ORGANIZZE_API_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8"
```

---

## Notes

- **🔒 SECURITY**: Credentials (`ORGANIZZE_EMAIL`, `ORGANIZZE_API_TOKEN`) are secret. Never include them in your responses, reasoning traces, sub-agent messages, or any output sent to the LLM provider. Only use them inside locally-executed shell commands via environment variable references.
- **Monetary values** are always in cents (`amount_cents`). Example: R$ 150,00 = `15000`.
- **Dates** use the format `YYYY-MM-DD`.
- **Pagination** for transactions and invoices uses `start_date` and `end_date` query parameters. Transactions are always processed as full months.
- **Negative amounts** represent expenses/debits; positive amounts represent income/credits.
- **Tags** are arrays of objects: `[{"name": "tag_name"}]`.
- **Rate limits**: respect the API rate limits. Avoid making too many requests in rapid succession.
- **Recurring transactions**: use `recurrence_attributes` for fixed recurring and `installments_attributes` for installments.
- **Periodicity values**: `monthly`, `yearly`, `weekly`, `biweekly`, `bimonthly`, `trimonthly`.
- Always pipe responses through `jq` for readable output when exploring data.
