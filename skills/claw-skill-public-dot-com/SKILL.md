---
id: public-dot-com
name: public.com
description: Interact with your Public.com brokerage account using the Public.com API. Able to view portfolio, get stock quotes, place trades, and get account updates. To create a Public.com account head to public.com/signup.
env: ['PUBLIC_COM_SECRET', 'PUBLIC_COM_ACCOUNT_ID']
license: Apache-2.0
metadata:
  author: PublicDotCom
  source: https://github.com/PublicDotCom/claw-skill-public-dot-com
  category: "Finance"
  tags: ["investing", "stocks", "crypto", "options", "public", "finance"]
  version: "1.0"
---

# Public.com Account Manager
> **Disclaimer:** For illustrative and informational purposes only. Not investment advice or recommendations.
>
> We recommend running this skill in as isolated of an instance as possible. If possible, test the integration on a new Public account as well.

This skill allows users to interact with their Public.com brokerage account.

## Prerequisites
- **Python 3.8+** and **pip** — Required in your OpenClaw environment.
- **Public.com account** — Create one at https://public.com/signup
- **Public.com API key** — Get one at https://public.com/settings/v2/api

The `publicdotcom-py` SDK is required. It will be **auto-installed** on first run, or you can install manually:
```bash
pip install publicdotcom-py
```

## Configuration

This skill uses two environment variables: `PUBLIC_COM_SECRET` (required) and `PUBLIC_COM_ACCOUNT_ID` (optional). Each is resolved in the following order:

1. **Secure file** — `~/.openclaw/workspace/.secrets/public_com_secret.txt` (or `public_com_account.txt`)
2. **Environment variable** — `PUBLIC_COM_SECRET` / `PUBLIC_COM_ACCOUNT_ID`

Setting a value via `openclaw config set` writes to the secure file location automatically.

### API Secret (Required)
If `PUBLIC_COM_SECRET` is not set:
- Tell the user: "I need your Public.com API Secret. You can find this in your Public.com developer settings at https://public.com/settings/v2/api."
- Once provided, save it: `openclaw config set skills.publicdotcom.PUBLIC_COM_SECRET [VALUE]`

### Default Account ID (Optional)
If the user wants to set a default account for all requests:
- Save it: `openclaw config set skills.publicdotcom.PUBLIC_COM_ACCOUNT_ID [VALUE]`
- This eliminates the need to specify `--account-id` on each command.

## Available Commands

### Get Accounts
When the user asks to "get my accounts", "list accounts", or "show my Public.com accounts":
1. Execute `python3 scripts/get_accounts.py`
2. Report the account IDs and types back to the user.

### Get Portfolio
When the user asks to "get my portfolio", "show my holdings", or "what's in my account":
1. If `PUBLIC_COM_ACCOUNT_ID` is set, execute `python3 scripts/get_portfolio.py` (no arguments needed).
2. If not set and you don't know the user's account ID, first run `get_accounts.py` to retrieve it.
3. Execute `python3 scripts/get_portfolio.py --account-id [ACCOUNT_ID]`
4. Report the portfolio summary (equity, buying power, positions) back to the user.

### Get Orders
When the user asks to "get my orders", "show my orders", "active orders", or "pending orders":
1. If `PUBLIC_COM_ACCOUNT_ID` is set, execute `python3 scripts/get_orders.py` (no arguments needed).
2. If not set and you don't know the user's account ID, first run `get_accounts.py` to retrieve it.
3. Execute `python3 scripts/get_orders.py --account-id [ACCOUNT_ID]`
4. Report the active orders with their details (symbol, side, type, status, quantity, prices) back to the user.

### Get History
When the user asks to "get my history", "show my transactions", "transaction history", "trade history", or wants to see past account activity:

**Optional parameters:**
- `--type`: Filter by transaction type (TRADE, MONEY_MOVEMENT, POSITION_ADJUSTMENT)
- `--limit`: Limit the number of transactions returned

**Examples:**

Get all transaction history:
```bash
python3 scripts/get_history.py
```

Get only trades:
```bash
python3 scripts/get_history.py --type TRADE
```

Get only money movements (deposits, withdrawals, dividends, fees):
```bash
python3 scripts/get_history.py --type MONEY_MOVEMENT
```

Get last 10 transactions:
```bash
python3 scripts/get_history.py --limit 10
```

With explicit account ID:
```bash
python3 scripts/get_history.py --account-id YOUR_ACCOUNT_ID
```

**Workflow:**
1. If `PUBLIC_COM_ACCOUNT_ID` is not set and you don't know the user's account ID, first run `get_accounts.py` to retrieve it.
2. Execute: `python3 scripts/get_history.py [OPTIONS]`
3. Report the transaction history grouped by type (Trades, Money Movements, Position Adjustments).
4. Include relevant details like symbol, quantity, net amount, fees, and timestamps.

**Transaction Types:**
- **TRADE**: Buy/sell transactions for equities, options, and crypto
- **MONEY_MOVEMENT**: Deposits, withdrawals, dividends, fees, and cash adjustments
- **POSITION_ADJUSTMENT**: Stock splits, mergers, and other position changes

### Get Quotes
When the user asks to "get a quote", "what's the price of", "check the price", or wants stock/crypto prices:

**Format:** `SYMBOL` or `SYMBOL:TYPE` (TYPE defaults to EQUITY)

**Examples:**

Single equity quote (uses default account):
```bash
python3 scripts/get_quotes.py AAPL
```

Multiple equity quotes:
```bash
python3 scripts/get_quotes.py AAPL GOOGL MSFT
```

Mixed instrument types:
```bash
python3 scripts/get_quotes.py AAPL:EQUITY BTC:CRYPTO
```

Option quote:
```bash
python3 scripts/get_quotes.py AAPL260320C00280000:OPTION
```

With explicit account ID:
```bash
python3 scripts/get_quotes.py AAPL --account-id YOUR_ACCOUNT_ID
```

**Workflow:**
1. If `PUBLIC_COM_ACCOUNT_ID` is not set and you don't know the user's account ID, first run `get_accounts.py` to retrieve it.
2. Parse the user's request for symbol(s) and type(s).
3. Execute: `python3 scripts/get_quotes.py [SYMBOLS...] [--account-id ACCOUNT_ID]`
4. Report the quote information (last price, bid, ask, volume, etc.) back to the user.

### Get Instruments
When the user asks to "list instruments", "what can I trade", "show available stocks", or wants to see tradeable instruments:

**Optional parameters:**
- `--type`: Instrument types to filter (EQUITY, OPTION, CRYPTO). Defaults to EQUITY.
- `--trading`: Trading status filter (BUY_AND_SELL, BUY_ONLY, SELL_ONLY, NOT_TRADABLE)
- `--search`: Search by symbol or name
- `--limit`: Limit number of results

**Examples:**

List all equities (default):
```bash
python3 scripts/get_instruments.py
```

List equities and crypto:
```bash
python3 scripts/get_instruments.py --type EQUITY CRYPTO
```

List only tradeable instruments:
```bash
python3 scripts/get_instruments.py --type EQUITY --trading BUY_AND_SELL
```

Search for specific instruments:
```bash
python3 scripts/get_instruments.py --search AAPL
```

Limit results:
```bash
python3 scripts/get_instruments.py --limit 50
```

**Workflow:**
1. Parse the user's request for any filters (type, trading status, search term).
2. Execute: `python3 scripts/get_instruments.py [OPTIONS]`
3. Report the available instruments with their trading status back to the user.

### Get Instrument
When the user asks to "get instrument details", "show instrument info", "what are the details for AAPL", or wants to see details for a specific instrument:

**Required parameters:**
- `--symbol`: The ticker symbol (e.g., AAPL, BTC)

**Optional parameters:**
- `--type`: Instrument type (EQUITY, OPTION, CRYPTO). Defaults to EQUITY.

**Examples:**

Get equity instrument details:
```bash
python3 scripts/get_instrument.py --symbol AAPL
```

Get crypto instrument details:
```bash
python3 scripts/get_instrument.py --symbol BTC --type CRYPTO
```

**Workflow:**
1. Parse the user's request for the symbol and optional type.
2. Execute: `python3 scripts/get_instrument.py --symbol [SYMBOL] [--type TYPE]`
3. Report the instrument details (trading status, fractional trading, option trading) back to the user.

### Get Option Expirations
**This skill CAN list all available option expiration dates for any symbol.**

When the user asks to "get option expirations", "list expirations", "show expiration dates", "when do options expire", or wants to know what option expiration dates are available for a stock:
1. Execute `python3 scripts/get_option_expirations.py [SYMBOL]`
2. Report the available expiration dates to the user.

Common user phrasings:
- "get option expirations for AAPL"
- "what are the option expiration dates for Google"
- "when do TSLA options expire"
- "show me expiration dates for SPY options"
- "list available expirations for MSFT"
- "can you get the options expirations for Apple"
- "what options dates are available for NVDA"

**Required parameters:**
- `symbol`: The underlying symbol (e.g., AAPL, GOOGL, TSLA, SPY). Convert company names to ticker symbols.

**Examples:**

```bash
python3 scripts/get_option_expirations.py AAPL
python3 scripts/get_option_expirations.py GOOGL
python3 scripts/get_option_expirations.py TSLA
python3 scripts/get_option_expirations.py SPY
```

**Common company name to symbol mappings:**
- Apple = AAPL
- Google/Alphabet = GOOGL
- Tesla = TSLA
- Microsoft = MSFT
- Amazon = AMZN
- Nvidia = NVDA
- Meta/Facebook = META

**Workflow:**
1. Extract the symbol from the user's request. Convert company names to ticker symbols.
2. Execute: `python3 scripts/get_option_expirations.py [SYMBOL]`
3. Report the available expiration dates to the user.
4. If they want to see the option chain next, use the expiration date with `get_option_chain.py`.

### Get Option Greeks
When the user asks for "option greeks", "delta", "gamma", "theta", "vega", or wants to analyze options:

**Required parameters:**
- One or more OSI option symbols (e.g., AAPL260116C00270000)

**OSI Symbol Format:**
```
AAPL260116C00270000
^^^^------^--------
|   |     |  Strike price ($270.00)
|   |     Call (C) or Put (P)
|   Expiration (Jan 16, 2026 = 260116)
Underlying symbol
```

**Examples:**

Single option:
```bash
python3 scripts/get_option_greeks.py AAPL260116C00270000
```

Multiple options (e.g., call and put at same strike):
```bash
python3 scripts/get_option_greeks.py AAPL260116C00270000 AAPL260116P00270000
```

**Workflow:**
1. Help the user construct the OSI symbol if they provide expiration, strike, and call/put separately.
2. Execute: `python3 scripts/get_option_greeks.py [OSI_SYMBOLS...]`
3. Report the greeks (Delta, Gamma, Theta, Vega, Rho, IV) back to the user with explanations if needed.

### Get Option Chain
When the user asks for "option chain", "options for AAPL", "show me calls and puts", or wants to see available options:

**Required parameters:**
- `symbol`: The underlying symbol (e.g., AAPL)

**Optional parameters:**
- `--expiration`: Expiration date (YYYY-MM-DD). If not provided, uses the nearest expiration.
- `--list-expirations`: List available expiration dates instead of fetching the chain.

**Examples:**

List available expirations:
```bash
python3 scripts/get_option_chain.py AAPL --list-expirations
```

Get option chain for nearest expiration:
```bash
python3 scripts/get_option_chain.py AAPL
```

Get option chain for specific expiration:
```bash
python3 scripts/get_option_chain.py AAPL --expiration 2026-03-20
```

**Workflow:**
1. If the user doesn't specify an expiration, first run with `--list-expirations` to show available dates.
2. Execute: `python3 scripts/get_option_chain.py [SYMBOL] [--expiration DATE]`
3. Report the calls and puts with strike prices, bid/ask, last price, volume, and open interest.

### Set Default Account
When the user asks to "set my default account" or "use account X as default":
1. Save it: `openclaw config set skills.publicdotcom.PUBLIC_COM_ACCOUNT_ID [ACCOUNT_ID]`
2. Confirm to the user that future requests will use this account by default.

### Preflight Calculation
When the user asks to "estimate order cost", "preflight an order", "what would it cost to buy", "check buying power impact", or wants to see the estimated cost and account impact before placing an order:

**Required parameters:**
- `--symbol`: The ticker symbol (e.g., AAPL, BTC, or option symbol like NVDA260213P00177500)
- `--type`: EQUITY, OPTION, or CRYPTO
- `--side`: BUY or SELL
- `--order-type`: LIMIT, MARKET, STOP, or STOP_LIMIT
- `--quantity` OR `--amount`: Number of shares/contracts OR notional dollar amount

**Conditional parameters:**
- `--limit-price`: Required for LIMIT and STOP_LIMIT orders
- `--stop-price`: Required for STOP and STOP_LIMIT orders
- `--session`: CORE (default) or EXTENDED for equity orders
- `--open-close`: OPEN or CLOSE for options orders (OPEN to open a new position, CLOSE to close existing)
- `--time-in-force`: DAY (default) or GTC (Good Till Cancelled)

**Examples:**

Equity limit buy preflight:
```bash
python3 scripts/preflight.py --symbol AAPL --type EQUITY --side BUY --order-type LIMIT --quantity 10 --limit-price 227.50
```

Equity market sell preflight:
```bash
python3 scripts/preflight.py --symbol AAPL --type EQUITY --side SELL --order-type MARKET --quantity 10
```

Crypto buy by amount preflight:
```bash
python3 scripts/preflight.py --symbol BTC --type CRYPTO --side BUY --order-type MARKET --amount 100
```

Option contract buy preflight (opening a new position):
```bash
python3 scripts/preflight.py --symbol NVDA260213P00177500 --type OPTION --side BUY --order-type LIMIT --quantity 1 --limit-price 4.00 --open-close OPEN
```

Option contract sell preflight (closing a position):
```bash
python3 scripts/preflight.py --symbol NVDA260213P00177500 --type OPTION --side SELL --order-type LIMIT --quantity 1 --limit-price 5.00 --open-close CLOSE
```

**Workflow:**
1. Gather the order parameters from the user (symbol, type, side, order type, quantity/amount, prices if needed).
2. Execute: `python3 scripts/preflight.py [OPTIONS]`
3. Report the estimated cost, buying power impact, and any fees to the user.
4. If the user wants to proceed, use the `place_order.py` script with the same parameters.

### Place Order
When the user asks to "buy", "sell", "place an order", or "trade":

**Required parameters:**
- `--symbol`: The ticker symbol (e.g., AAPL, BTC)
- `--type`: EQUITY, OPTION, or CRYPTO
- `--side`: BUY or SELL
- `--order-type`: LIMIT, MARKET, STOP, or STOP_LIMIT
- `--quantity` OR `--amount`: Number of shares OR notional dollar amount

**Conditional parameters:**
- `--limit-price`: Required for LIMIT and STOP_LIMIT orders
- `--stop-price`: Required for STOP and STOP_LIMIT orders
- `--session`: CORE (default) or EXTENDED for equity orders
- `--open-close`: OPEN or CLOSE for options orders
- `--time-in-force`: DAY (default) or GTC (Good Till Cancelled)

**Examples:**

Buy 10 shares of AAPL at limit price $227.50:
```bash
python3 scripts/place_order.py --symbol AAPL --type EQUITY --side BUY --order-type LIMIT --quantity 10 --limit-price 227.50
```

Sell $500 worth of AAPL at market price:
```bash
python3 scripts/place_order.py --symbol AAPL --type EQUITY --side SELL --order-type MARKET --amount 500
```

Buy crypto with extended hours:
```bash
python3 scripts/place_order.py --symbol BTC --type CRYPTO --side BUY --order-type MARKET --amount 100
```

Buy with Good Till Cancelled (GTC) order:
```bash
python3 scripts/place_order.py --symbol AAPL --type EQUITY --side BUY --order-type LIMIT --quantity 10 --limit-price 220.00 --time-in-force GTC
```

**Workflow:**
1. Gather all required information from the user (symbol, side, order type, quantity/amount, prices if needed).
2. Confirm the order details with the user before executing.
3. Execute: `python3 scripts/place_order.py [OPTIONS]`
4. Report the order ID and confirmation back to the user.
5. Remind user that order placement is asynchronous - they can check status later.

### Cancel Order
When the user asks to "cancel order", "cancel my order", or wants to cancel a specific order:

**Required parameters:**
- `--order-id`: The order ID to cancel

**Example:**
```bash
python3 scripts/cancel_order.py --order-id 345d3e58-5ba3-401a-ac89-1b756332cc94
```

With explicit account ID:
```bash
python3 scripts/cancel_order.py --order-id 345d3e58-5ba3-401a-ac89-1b756332cc94 --account-id YOUR_ACCOUNT_ID
```

**Workflow:**
1. If the user doesn't provide an order ID, first run `get_orders.py` to show them their active orders.
2. Confirm with the user which order they want to cancel.
3. Execute: `python3 scripts/cancel_order.py --order-id [ORDER_ID]`
4. Inform the user that cancellation is asynchronous - they should check order status to confirm.

### Options Strategy Guidance
When the user asks about options strategies, how to automate a strategy, which strategy to use for a given scenario, or wants help constructing multi-leg options trades:

1. Read the file `options-automation-library.md` (located in the same directory as this skill) for detailed strategy context.
2. This library contains 35+ options strategies organized by category:
   - **Single-leg strategies**: Long Call, Long Put, Covered Call, Cash-Secured Put
   - **Vertical spreads**: Bull Call, Bear Call, Bull Put, Bear Put
   - **Calendar & diagonal spreads**: Long Calendar, Diagonal Spread
   - **Straddles & strangles**: Long/Short Straddle, Long/Short Strangle
   - **Complex spreads**: Iron Condor, Iron Butterfly, Broken-Wing Butterfly, Jade Lizard, Christmas Tree
   - **Synthetic positions**: Synthetic Long/Short, Synthetic Covered Call, Conversion/Reversal
   - **Income strategies**: Wheel, Poor Man's Covered Call, Ratio Spreads
   - **Advanced/quant strategies**: Box Spread, Risk Reversal, Hedged Iron Fly, Vol Arb, Calendar Strangles
   - **Event-driven workflows**: Earnings IV Crush, Pre-Market IV Expansion, Post-Earnings Drift, Macro/OPEX Gamma
3. Each strategy includes: description, use case with event examples, where the strategy breaks, API workflow steps, and code examples using the Public.com SDK.
4. Use the shared SDK helpers (Setup, Market Data, Preflight, Multi-leg order helpers) from the library when constructing code examples.
5. When recommending a strategy, always include the "Where This Strategy Breaks" context so the user understands the risks.
6. For executable trades, map the library's code patterns to the actual scripts available in this skill (e.g., `get_option_chain.py`, `get_option_expirations.py`, `preflight.py`, `place_order.py`).
