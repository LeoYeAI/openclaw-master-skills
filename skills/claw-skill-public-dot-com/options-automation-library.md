# Options Automation Playbook 

Example library for high-volume options traders on how strategies and event-driven workflows can be automated using our API/SDK. The goal is to provide actionable clarity on accelerating activation and translating existing strategies into execution on the API.

Code examples use API order construction, with illustrative helper functions that reflect common trader-side logic layered on top of the API.

Standard structure

1. Description  
2. Use case (includes event examples)  
3. Where the strategy breaks  
4. API workflow  
5. Code example (SDK code, using shared helpers)

---

# Shared SDK helpers (all strategies)

### A) Setup

```py
import os
import uuid
from datetime import datetime, date
from decimal import Decimal

from public_api_sdk import (
    PublicApiClient,
    PublicApiClientConfiguration,
    OrderInstrument,
    InstrumentType,
    OptionExpirationsRequest,
    OptionChainRequest,
    OrderRequest,
    MultilegOrderRequest,
    PreflightRequest,
    PreflightMultiLegRequest,
    OrderExpiration,
    TimeInForce,
    OrderType,
    OrderSide,
    OpenCloseIndicator,
    OrderLegRequest,
    LegInstrument,
    LegInstrumentType,
)
from public_api_sdk.auth_config import ApiKeyAuthConfig


def init_client() -> PublicApiClient:
    return PublicApiClient(
        ApiKeyAuthConfig(api_secret_key=os.environ["PUBLIC_API_SECRET_KEY"]),
        config=PublicApiClientConfiguration(
            default_account_number=os.environ["PUBLIC_DEFAULT_ACCOUNT_NUMBER"],
        ),
    )


client = init_client()
```

### B) Market data helpers

```py
def get_expirations(symbol: str) -> list[str]:
    resp = client.get_option_expirations(
        OptionExpirationsRequest(
            instrument=OrderInstrument(symbol=symbol, type=InstrumentType.EQUITY)
        )
    )
    return list(resp.expirations)


def choose_expiry_min_days_out(symbol: str, min_days_out: int) -> str:
    expirations = get_expirations(symbol)
    today = date.today()

    def days_out(exp: str) -> int:
        return (date.fromisoformat(exp) - today).days

    candidates = [e for e in expirations if days_out(e) >= min_days_out]
    return candidates[0] if candidates else expirations[-1]


def get_chain(symbol: str, expiry: str):
    return client.get_option_chain(
        OptionChainRequest(
            instrument=OrderInstrument(symbol=symbol, type=InstrumentType.EQUITY),
            expiration_date=expiry,
        )
    )


def pick_call_by_strike(chain, strike: float):
    calls = chain.calls
    return min(calls, key=lambda c: abs(float(c.option_details.strike_price) - strike))


def pick_put_by_strike(chain, strike: float):
    puts = chain.puts
    return min(puts, key=lambda p: abs(float(p.option_details.strike_price) - strike))
```

### C) Preflight \+ order helpers (single-leg)

```py
def preflight_single_leg(
    option_osi: str,
    side: OrderSide,
    qty: int,
    limit_price: Decimal,
    open_close: OpenCloseIndicator = OpenCloseIndicator.OPEN,
):
    req = PreflightRequest(
        instrument=OrderInstrument(symbol=option_osi, type=InstrumentType.OPTION),
        order_side=side,
        order_type=OrderType.LIMIT,
        expiration=OrderExpiration(time_in_force=TimeInForce.DAY),
        quantity=str(qty),
        limit_price=str(limit_price),
        open_close_indicator=open_close,
    )
    return client.perform_preflight_calculation(req)


def place_single_leg_limit(
    option_osi: str,
    side: OrderSide,
    qty: int,
    limit_price: Decimal,
    open_close: OpenCloseIndicator = OpenCloseIndicator.OPEN,
):
    req = OrderRequest(
        order_id=str(uuid.uuid4()),
        instrument=OrderInstrument(symbol=option_osi, type=InstrumentType.OPTION),
        order_side=side,
        order_type=OrderType.LIMIT,
        expiration=OrderExpiration(time_in_force=TimeInForce.DAY),
        quantity=str(qty),
        limit_price=str(limit_price),
        open_close_indicator=open_close,
    )
    return client.place_order(req)
```

### D) Preflight \+ order helpers (multi-leg)

```py
def preflight_multi_leg(
    base_symbol: str,
    legs: list[OrderLegRequest],
    qty: int,
    limit_price: Decimal,
):
    req = PreflightMultiLegRequest(
        order_type=OrderType.LIMIT,
        expiration=OrderExpiration(time_in_force=TimeInForce.DAY),
        quantity=str(qty),
        limit_price=str(limit_price),
        legs=legs,
    )
    return client.perform_multi_leg_preflight_calculation(req)


def place_multi_leg_limit(
    legs: list[OrderLegRequest],
    qty: int,
    limit_price: Decimal,
):
    req = MultilegOrderRequest(
        order_id=str(uuid.uuid4()),
        quantity=str(qty),
        type=OrderType.LIMIT,
        limit_price=str(limit_price),
        expiration=OrderExpiration(time_in_force=TimeInForce.DAY),
        legs=legs,
    )
    return client.place_multileg_order(req)


def leg(option_osi: str, side: OrderSide, ratio_qty: int = 1, open_close: OpenCloseIndicator = OpenCloseIndicator.OPEN):
    return OrderLegRequest(
        instrument=LegInstrument(symbol=option_osi, type=LegInstrumentType.OPTION),
        side=side,
        open_close_indicator=open_close,
        ratio_quantity=str(ratio_qty),
    )
```

### E) Rebate visibility (standard print pattern)

```py
def print_preflight_summary(pf):
    # Preflight responses include estimated costs + strategy details; surface rebates consistently.
    print("Estimated cost:", getattr(pf, "estimated_cost", None))
    print("Buying power:", getattr(pf, "buying_power_requirement", None))
    est_rebate = getattr(getattr(pf, "estimated_order_rebate", None), "estimated_option_rebate", None)
    print("Estimated option rebate:", est_rebate)
```

Note: Multi-leg strategies should always run multi-leg preflight first.

---

# SINGLE-LEG STRATEGIES

## **1\. Long Call**

**Description:** Buy a call option to express a bullish directional view with defined risk (maximum loss is premium paid).

**Use case & event examples:** This strategy offers defined downside risk and convex exposure, deployed for expected significant upward momentum. It is typically used after positive events like strong earnings, major announcements, or technical breakouts, suggesting probable sustained follow-through. 

**Where This Strategy Breaks:** Long calls fail when price stagnation allows time decay to erode value, volatility compresses post-entry, or if entered prematurely or too near expiration. The primary failure is paying for unrealized convexity. 

**API workflow**

1. Select symbol and target expiry (e.g., 7–30 days out).  
2. Pull the options chain for that symbol/expiry.  
3. Filter calls by target delta (e.g., 0.40–0.60) or by moneyness (ATM/near-ATM).  
4. Apply entry conditions (signal, event, risk filters).  
5. Place a buy-to-open limit order.  
6. Monitor position P\&L, time-to-expiry, and exit conditions.

**Code example**

```py
symbol = "AAPL"
expiry = choose_expiry(days_out=14)

chain = client.get_chain(symbol, expiry)
call = pick_delta(chain, kind="call", min_delta=0.4, max_delta=0.6)

if entry_signal(symbol):
    order = client.place_order(
        option_symbol=call.symbol,
        side="buy_to_open",
        qty=10,
        order_type="limit",
        limit_price=call.ask,
    )
    client.monitor_single_leg(
        option_symbol=call.symbol,
        take_profit_pct=0.5,
        max_loss_pct=0.5,
        max_holding_days=7,
    )
```

---

## **2\. Long Put**

**Description:** Buy a put option to express a bearish view or to hedge downside risk.

**Use case & event example:** Deployed when a trader anticipates sharp downside or seeks short-term market protection. Common uses include pre-CPI, FOMC, or earnings releases due to asymmetric downside risk, or following a breakdown of key support.

**Where This Strategy Breaks:** Long puts fail if downside is slow or absent. Sideways/grinding markets cause premium drain via time decay. Volatility contraction also pressures the position. Trades often fail when downside is anticipated too early or after the move has passed.

**API workflow**

1. Choose index/ETF or single-name symbol and expiry.  
2. Pull options chain.  
3. Filter puts by target delta (e.g., −0.30 to −0.50).  
4. Confirm bearish/macro risk signal.  
5. Place buy-to-open limit order.  
6. Manage exit before event or by P\&L/time.

**Code example**

```py
symbol = "SPY"
expiry = choose_expiry_around_event("CPI")

chain = client.get_chain(symbol, expiry)
put = pick_delta(chain, kind="put", min_delta=-0.5, max_delta=-0.3)

if macro_risk_model(symbol) == "downside":
    client.place_order(
        option_symbol=put.symbol,
        side="buy_to_open",
        qty=20,
        order_type="limit",
        limit_price=put.ask,
    )
    client.monitor_single_leg(
        option_symbol=put.symbol,
        take_profit_pct=1.0,
        max_loss_pct=0.5,
        exit_before_event=True,
        event_time=get_event_time("CPI"),
    )
```

---

## **3\. Covered Call**

**Description:** Sell call options against owned shares to collect premium, typically sacrificing upside above the call strike.

**Use case & event example:** Used by a share-owner anticipating sideways or modestly higher price movement. Often implemented after earnings, when uncertainty has decreased and upside is capped, this strategy monetizes elevated implied volatility through premium collection.

**Where This Strategy Breaks:** Covered calls fail in strong uptrends when the price decisively surpasses the short strike, often due to news or earnings gap-ups, leading to missed upside. Issues also stem from selling calls too close to the spot price or emotional attachment to holding the shares.

**API workflow**

1. Read share position (quantity and cost basis).  
2. Determine maximum number of covered calls (shares // 100).  
3. Pull options chain for target expiry.  
4. Select OTM call by target delta (e.g., 0.15–0.30) or target yield.  
5. Place sell-to-open order for that number of contracts.  
6. Monitor for roll/close triggers (e.g., % of premium captured, days to expiry, underlying price vs strike).

**Code example**

```py
symbol = "MSFT"
shares = client.get_share_position(symbol).quantity
contracts = shares // 100

if contracts > 0:
    expiry = choose_expiry(days_out=30)
    chain = client.get_chain(symbol, expiry)
    short_call = pick_delta(chain, kind="call", min_delta=0.15, max_delta=0.30)

    client.place_order(
        option_symbol=short_call.symbol,
        side="sell_to_open",
        qty=contracts,
        order_type="limit",
        limit_price=short_call.bid,
    )

    client.manage_covered_call(
        short_call_symbol=short_call.symbol,
        take_profit_pct=0.7,       # capture ~70% of premium
        roll_days_before_expiry=5,
        roll_up_if_price_above=short_call.strike,
    )
```

---

## **4\. Cash-Secured Put**

**Description:** Sell a put option while holding enough cash to buy the underlying if assigned. Functions as a limit order to buy stock, plus premium.

**Use case & event example:** Traders use this strategy to accumulate shares cheaply, getting paid while they wait. It is often used during market drops, like selloffs or risk-off days, when volatility is high but long-term confidence in the stock remains.

**Where This Strategy Break:** Cash-secured puts fail when price gaps sharply below the strike, volatility expands post-entry, or if used aggressively in weak markets. Overconcentration is a frequent cause of failure.

**API workflow**

1. Check available cash / buying power.  
2. Pull options chain for target expiry.  
3. Select put strike near desired entry price (via valuation model or support level).  
4. Calculate maximum contracts allowed by cash.  
5. Place sell-to-open order.  
6. Monitor for: profit target, roll opportunity, or assignment; on assignment, hand off to covered call workflow.

**Code example**

```py
symbol = "NVDA"
expiry = choose_expiry(days_out=21)

account = client.get_account()
available_cash = account.cash

chain = client.get_chain(symbol, expiry)

entry_price = fair_value_model(symbol)
short_put = pick_strike_near(chain, kind="put", target_price=entry_price)

contract_notional = short_put.strike * 100
max_contracts = int(available_cash // contract_notional)

if max_contracts > 0 and support_confirmed(symbol, short_put.strike):
    client.place_order(
        option_symbol=short_put.symbol,
        side="sell_to_open",
        qty=max_contracts,
        order_type="limit",
        limit_price=short_put.bid,
    )

    client.monitor_cash_secured_put(
        option_symbol=short_put.symbol,
        take_profit_pct=0.5,
        max_loss_multiple=2.0,
        on_assignment=lambda: client.start_wheel_cycle(symbol),
    )
```

---

# VERTICAL SPREADS

## **5\. Bull Call Spread**

**Description:** Buy a call and sell a higher-strike call in the same expiry to express a bullish view with reduced cost and capped upside.

**Use case & event example:** Used when a trader expects defined upside within a range, this strategy offers cheaper exposure than a naked call. It's common ahead of events like earnings or CPI when high implied volatility makes outright calls expensive.

**Where This Strategy Breaks:** Bull call spreads break when upside stalls below the short strike. Volatility compression can reduce the value of both legs, limiting gains even if price moves higher. These trades also fail when the move happens slower than expected. Short expirations leave little room for recovery.

**API workflow**

1. Select symbol and expiry.  
2. Pull options chain.  
3. Choose long call near ATM or desired delta.  
4. Choose short call at higher strike (spread width based on risk/return preference).  
5. Submit multi-leg debit order.  
6. Manage based on P\&L, time, and event timing.

**Code example**

```py
symbol = "NFLX"
expiry = choose_expiry_around_event(symbol, event="earnings")

chain = client.get_chain(symbol, expiry)

long_call = pick_delta(chain, kind="call", min_delta=0.35, max_delta=0.55)
short_call = pick_above(long_call, width=20)

legs = [
    {"symbol": long_call.symbol,  "side": "buy_to_open",  "qty": 1},
    {"symbol": short_call.symbol, "side": "sell_to_open", "qty": 1},
]

net_debit = estimate_debit(legs)
client.place_multi_leg_order(symbol, legs, net_price=net_debit)
client.monitor_spread(
    legs=legs,
    take_profit_fraction=0.7,
    max_loss_fraction=0.5,
    exit_before_event=True,
    event_time=get_event_time(symbol, "earnings"),
)
```

---

## **6\. Bear Call Spread**

**Description:** Sell a call and buy a higher-strike call in the same expiry to express a neutral-to-bearish view for a net credit with defined risk.

**Use case & event example:** Used when a trader anticipates a stall or reversal after sharp rallies, failed breakouts, or overextended post-earnings pops, especially in high implied volatility (IV) environments, seeking defined-risk premium collection.

**Where This Strategy Breaks:**  Bear call spreads break in strong upside momentum environments. Volatility expansion can pressure short calls faster than expected. These trades also struggle when resistance levels fail decisively. Tight strike selection leaves little margin for error.

**API workflow**

1. Select symbol/expiry.  
2. Pull options chain.  
3. Select short call in target delta band (e.g., 0.20–0.35).  
4. Select long call at higher strike.  
5. Place multi-leg credit order.  
6. Monitor risk relative to short strike and manage/roll if breached.

**Code example**

```py
symbol = "TSLA"
expiry = choose_expiry(days_out=21)

chain = client.get_chain(symbol, expiry)

short_call = pick_delta(chain, kind="call", min_delta=0.2, max_delta=0.35)
long_call = pick_above(short_call, width=10)

legs = [
    {"symbol": short_call.symbol, "side": "sell_to_open", "qty": 1},
    {"symbol": long_call.symbol,  "side": "buy_to_open",  "qty": 1},
]

net_credit = estimate_credit(legs)
client.place_multi_leg_order(symbol, legs, net_price=net_credit)

client.monitor_credit_spread(
    legs=legs,
    take_profit_fraction=0.5,
    max_loss_multiple=2.0,
    roll_if_price_above=short_call.strike,
)
```

---

## **7\. Bull Put Spread**

**Description:** Sell a put and buy a lower-strike put in the same expiry, creating a bullish/neutral credit spread with defined downside.

**Use case & event example:** Used when a trader anticipates the price will hold above support, aiming to collect premium with limited downside. Often follows CPI or FOMC results that reduce downside risk, leading to relief rallies without guaranteeing explosive gains.

**Where This Strategy Breaks:** Bull put spreads fail when support breaks and downside accelerates. Rapid drawdowns occur with volatility expansion, especially before macro data or earnings. Selling strikes too close for the market regime is the primary error.

**API workflow**

1. Choose symbol and expiry.  
2. Pull chain.  
3. Select short put with target delta (e.g., −0.35 to −0.20).  
4. Select long put at lower strike.  
5. Place multi-leg credit order.  
6. Monitor price relative to short strike; manage or roll as needed.

**Code example**

```py
symbol = "SPY"
expiry = choose_expiry(days_out=30)

chain = client.get_chain(symbol, expiry)

short_put = pick_delta(chain, kind="put", min_delta=-0.35, max_delta=-0.2)
long_put = pick_below(short_put, width=5)

legs = [
    {"symbol": short_put.symbol, "side": "sell_to_open", "qty": 1},
    {"symbol": long_put.symbol,  "side": "buy_to_open",  "qty": 1},
]

net_credit = estimate_credit(legs)
client.place_multi_leg_order(symbol, legs, net_price=net_credit)

client.monitor_credit_spread(
    legs=legs,
    take_profit_fraction=0.5,
    max_loss_multiple=2.0,
    watch_level=short_put.strike,
)
```

---

## **8\. Bear Put Spread**

**Description:** Buy a put and sell a lower-strike put in the same expiry to express a bearish view with limited premium outlay and capped profit.

**Use case & event example:** Used for expected, controlled downside (not a crash). Often deployed ahead of earnings with negative sentiment, guidance risk, or sector weakness, when puts are expensive but downside conviction is high.

**Where This Strategy Breaks:** Bear put spreads fail if downside momentum stalls or price stabilizes. Volatility contraction limits early gains. Entering after the selloff has largely passed hurts performance. Timing is the main risk.

**API workflow**

1. Select symbol and expiry.  
2. Pull chain.  
3. Choose long put near ATM or target delta.  
4. Choose short put at lower strike (spread width sets payoff profile).  
5. Place multi-leg debit order.  
6. Monitor P\&L/time and exit before/after event.

**Code example**

```py
symbol = "QQQ"
expiry = choose_expiry_around_event(symbol, event="earnings_season")

chain = client.get_chain(symbol, expiry)

long_put = pick_delta(chain, kind="put", min_delta=-0.5, max_delta=-0.35)
short_put = pick_below(long_put, width=5)

legs = [
    {"symbol": long_put.symbol,  "side": "buy_to_open", "qty": 1},
    {"symbol": short_put.symbol, "side": "sell_to_open","qty": 1},
]

net_debit = estimate_debit(legs)
client.place_multi_leg_order(symbol, legs, net_price=net_debit)

client.monitor_spread(
    legs=legs,
    max_profit_fraction=0.7,
    max_loss_fraction=0.5,
    exit_on_event_pass=True,
    event_time=get_event_time(symbol, "macro_window"),
)
```

---

# CALENDAR & DIAGONAL SPREADS

## **9\. Long Calendar Spread**

**Description:** Sell a short-term option and buy a longer-term option at the same strike. Profits from short-term time decay and certain volatility dynamics.

**Use case & event example:** Used when near-term implied volatility is high and the price is expected to hold a specific level. Often deployed before earnings, the strategy involves selling the near-dated option and owning longer-dated exposure to profit from IV crush.

**Where This Strategy Breaks:** Long calendar spreads fail due to aggressive early price movement that outpaces front-month decay, large directional moves distorting volatility exposure, or unexpected shifts in volatility term structure (especially back-month IV compression). Entering too close to expiration also minimizes adjustment room.

**API workflow**

1. Select symbol and two expiries (near and far).  
2. Pull chains for both expiries.  
3. Choose common strike (often ATM).  
4. Short near-term option, long further-dated option.  
5. Place multi-leg order.  
6. Manage by rolling/closing the short leg around the event; manage long leg separately.

**Code example**

```py
symbol = "AMZN"
near_expiry = choose_expiry(days_out=7)
far_expiry = choose_expiry(days_out=45)

near_chain = client.get_chain(symbol, near_expiry)
far_chain = client.get_chain(symbol, far_expiry)

strike = estimate_atm_strike(symbol)
short_near = pick_strike(near_chain, kind="call", strike=strike)
long_far   = pick_strike(far_chain, kind="call", strike=strike)

legs = [
    {"symbol": short_near.symbol, "side": "sell_to_open", "qty": 1},
    {"symbol": long_far.symbol,   "side": "buy_to_open",  "qty": 1},
]

client.place_multi_leg_order(symbol, legs, net_price=estimate_debit(legs))
client.manage_calendar(
    short_symbol=short_near.symbol,
    long_symbol=long_far.symbol,
    roll_short_days_before_expiry=2,
)
```

---

## **10\. Diagonal Spread**

**Description:** Calendar-style spread using different strikes and expiries, adding directional bias (e.g., bullish diagonal with higher short strike).

**Use case & event example:** Used for a medium-term directional view, financed by selling short-dated options. Common post-earnings when longer-term direction is clearer but short-term premium is high.

**Where This Strategy Breaks:** Diagonal spreads fail when rapid price movement toward the short strike reduces time decay advantage, or when a sudden directional move overwhelms the longer-dated option before the front-month decays. Uneven volatility shifts across expirations are also problematic. Misaligned strike placement relative to trend strength is the primary cause of failure.

**API workflow**

1. Select long-dated expiry and shorter-term expiry.  
2. Pull both chains.  
3. Choose long option (often ITM/ATM) in far expiry.  
4. Choose short option (OTM) in near expiry with smaller delta.  
5. Place multi-leg order.  
6. Roll short leg over time; treat long leg as core position.

**Code example**

```py
symbol = "META"
long_expiry = choose_expiry(days_out=120)
short_expiry = choose_expiry(days_out=30)

long_chain = client.get_chain(symbol, long_expiry)
short_chain = client.get_chain(symbol, short_expiry)

long_call = pick_delta(long_chain, kind="call", min_delta=0.6, max_delta=0.8)
short_call = pick_delta(short_chain, kind="call", min_delta=0.2, max_delta=0.3)

legs = [
    {"symbol": long_call.symbol,  "side": "buy_to_open",  "qty": 1},
    {"symbol": short_call.symbol, "side": "sell_to_open", "qty": 1},
]

client.place_multi_leg_order(symbol, legs, net_price=estimate_debit(legs))
client.manage_diagonal(
    long_symbol=long_call.symbol,
    short_symbol=short_call.symbol,
    roll_short_on_expiry=True,
)
```

---

# STRADDLES & STRANGLES

## **11\. Long Straddle**

**Description:** Buy an ATM call and an ATM put with the same strike and expiry to profit from large moves in either direction.

**Use case & event example:** Used when a trader expects a large move but is unsure of direction. Classic use case is pre-earnings, FDA decisions, merger announcements, or major macro events, where volatility expansion outweighs directional uncertainty.

**Where This Strategy Breaks:** Long straddles fail when actual price movement is less than the implied volatility at entry. Post-event volatility collapse and price pinning near the strike can erode premium. Entering late into a volatility expansion is the main failure cause.

**API workflow**

1. Select symbol and expiry just beyond event date.  
2. Pull chain.  
3. Identify ATM strike.  
4. Buy call and put at that strike.  
5. Monitor underlying price, IV, and event outcome; exit on move or after event.

**Code example**

```py
symbol = "TSLA"
expiry = choose_expiry_around_event(symbol, "earnings")

chain = client.get_chain(symbol, expiry)
strike = estimate_atm_strike(symbol)

call = pick_strike(chain, kind="call", strike=strike)
put  = pick_strike(chain, kind="put",  strike=strike)

legs = [
    {"symbol": call.symbol, "side": "buy_to_open", "qty": 1},
    {"symbol": put.symbol,  "side": "buy_to_open", "qty": 1},
]

client.place_multi_leg_order(symbol, legs, net_price=call.ask + put.ask)
client.manage_long_straddle(
    call_symbol=call.symbol,
    put_symbol=put.symbol,
    min_move_pct=0.05,
    exit_after_event=True,
)
```

---

## **12\. Short Straddle**

**Description:** Sell an ATM call and an ATM put at the same strike and expiry to collect premium, betting on limited price movement; risk is large if price moves significantly.

**Use case & event example:** Used by experienced traders expecting minimal movement and volatility collapse, typically deployed after earnings when the implied move has resolved and price is expected to consolidate near a key level.

**Where This Strategy Breaks:** Short straddles fail due to large directional moves or sudden volatility shifts, leading to rapid losses as the price moves from the strike. They are highly vulnerable to unexpected news or macro events. Oversizing and inadequate risk limits are the primary causes of failure.

**API workflow**

1. Select symbol and expiry.  
2. Pull chain and determine ATM strike.  
3. Sell ATM call and ATM put.  
4. Monitor P\&L, delta, and underlying price; optionally hedge or convert to iron fly by adding wings.

**Code example**

```py
symbol = "SPY"
expiry = choose_expiry(days_out=10)

chain = client.get_chain(symbol, expiry)
strike = estimate_atm_strike(symbol)

atm_call = pick_strike(chain, kind="call", strike=strike)
atm_put  = pick_strike(chain, kind="put",  strike=strike)

legs = [
    {"symbol": atm_call.symbol, "side": "sell_to_open", "qty": 1},
    {"symbol": atm_put.symbol,  "side": "sell_to_open", "qty": 1},
]

client.place_multi_leg_order(symbol, legs, net_price=estimate_credit(legs))
client.manage_short_straddle(
    call_symbol=atm_call.symbol,
    put_symbol=atm_put.symbol,
    max_loss_multiple=3.0,
    convert_to_iron_fly_if_breached=True,
)
```

---

## **13\. Long Strangle**

**Description:** Buy an OTM call and an OTM put with the same expiry but different strikes, seeking convex payoff with lower cost than a straddle.

**Use case & event example:** Traders use this for potential large moves with lower cost than a straddle, often around macro events (like CPI or FOMC) where tail moves are possible but direction is uncertain.

**Where This Strategy Breaks:** Long strangles fail when price stays range-bound, failing to reach the strikes and recoup the premium paid. Losses are compounded by post-entry volatility compression. The most common failures result from strikes being set too far OTM or entering late into a volatility expansion.

**API workflow**

1. Select symbol and expiry.  
2. Pull chain.  
3. Select OTM call in low positive delta band (e.g., 0.10–0.20).  
4. Select OTM put in low negative delta band (e.g., −0.20 to −0.10).  
5. Place multi-leg debit order.  
6. Manage using staged profit targets as price moves.

**Code example**

```py
symbol = "IWM"
expiry = choose_expiry_around_event(symbol, "FOMC")

chain = client.get_chain(symbol, expiry)

call = pick_delta(chain, kind="call", min_delta=0.1, max_delta=0.2)
put  = pick_delta(chain, kind="put",  min_delta=-0.2, max_delta=-0.1)

legs = [
    {"symbol": call.symbol, "side": "buy_to_open", "qty": 1},
    {"symbol": put.symbol,  "side": "buy_to_open", "qty": 1},
]

client.place_multi_leg_order(symbol, legs, net_price=call.ask + put.ask)
client.manage_long_strangle(
    call_symbol=call.symbol,
    put_symbol=put.symbol,
    profit_targets=[0.5, 1.0, 2.0],
)
```

---

## **14\. Short Strangle**

**Description:** Sell an OTM call and an OTM put with same expiry, collecting premium while betting price stays within a range; risk is large beyond the short strikes.

**Use case & event example:** Used when a trader expects the price to remain widely range-bound. Common post-earnings or during quiet macro weeks, especially when implied volatility is high relative to realized movement.

**Where This Strategy Breaks:** Short strangles fail during strong directional trends and volatility spikes, especially around macro events or earnings. Common causes of failure are oversizing and over-reliance on historical ranges.

**API workflow**

1. Choose symbol/expiry.  
2. Pull chain.  
3. Select OTM call and put at chosen deltas (e.g., ±0.10–0.20).  
4. Place multi-leg credit order.  
5. Monitor P\&L, underlying price bands, and volatility; hedge, adjust, or convert to iron condor as needed.

**Code example**

```py
symbol = "XLF"
expiry = choose_expiry(days_out=30)

chain = client.get_chain(symbol, expiry)

short_call = pick_delta(chain, kind="call", min_delta=0.1, max_delta=0.2)
short_put  = pick_delta(chain, kind="put",  min_delta=-0.2, max_delta=-0.1)

legs = [
    {"symbol": short_call.symbol, "side": "sell_to_open", "qty": 1},
    {"symbol": short_put.symbol,  "side": "sell_to_open", "qty": 1},
]

client.place_multi_leg_order(symbol, legs, net_price=estimate_credit(legs))
client.manage_short_strangle(
    call_symbol=short_call.symbol,
    put_symbol=short_put.symbol,
    price_band=calculate_band(symbol),
    add_wings_if_vol_spikes=True,
)
```

---

# CONDORS, BUTTERFLIES & COMPLEX SPREADS

## **15\. Iron Condor**

**Description:** A combination of a short put spread and a short call spread (four legs) to collect premium while defining risk on both sides.

**Use case & event example:** Used when a trader expects price to range with contracting volatility, typically immediately after earnings or leading into OPEX, when price pinning and IV decay are likely.

**Where This Strategy Breaks:** Iron condors fail when the market leaves a range-bound environment for a sustained directional move. Volatility spikes, often from macro or earnings events, can quickly breach short strikes. Failures are also common when wings are too narrow or position sizing is overly aggressive, essentially from holding the structure through unsuitable conditions. 

**API workflow**

1. Select symbol and expiry.  
2. Pull chain.  
3. Select short put (downside) and long put below it.  
4. Select short call (upside) and long call above it.  
5. Place 4-leg credit order.  
6. Monitor each side separately for adjustments.

**Code example**

```py
symbol = "SPY"
expiry = choose_expiry(days_out=30)
chain = client.get_chain(symbol, expiry)

short_put  = pick_delta(chain, kind="put",  min_delta=-0.2, max_delta=-0.1)
long_put   = pick_below(short_put, width=5)

short_call = pick_delta(chain, kind="call", min_delta=0.1, max_delta=0.2)
long_call  = pick_above(short_call, width=5)

legs = [
    {"symbol": short_put.symbol,  "side": "sell_to_open", "qty": 1},
    {"symbol": long_put.symbol,   "side": "buy_to_open",  "qty": 1},
    {"symbol": short_call.symbol, "side": "sell_to_open", "qty": 1},
    {"symbol": long_call.symbol,  "side": "buy_to_open",  "qty": 1},
]

client.place_multi_leg_order(symbol, legs, net_price=estimate_credit(legs))
client.manage_iron_condor(
    short_put_symbol=short_put.symbol,
    short_call_symbol=short_call.symbol,
    take_profit_fraction=0.5,
    max_loss_multiple=2.0,
)
```

---

## **16\. Iron Butterfly**

**Description:** Sell an ATM straddle (ATM call \+ ATM put) and buy OTM wings (call and put) to define risk while concentrating premium around a central strike.

**Use case & event example:** Used when a trader expects strong price pinning around a strike. Often placed near expiration or OPEX, when dealer gamma and positioning suggest price gravitates toward a central level.

**Where This Strategy Breaks:** Iron butterflies break when price moves away from the center strike early in the trade. Volatility expansion can increase losses on both sides before decay has time to work. These structures are especially sensitive to timing and strike placement. Narrow wings leave little room for error once price starts to move.

**API workflow**

1. Pick symbol, expiry, and central strike (often ATM).  
2. Sell ATM call and ATM put.  
3. Buy further OTM call and put as wings.  
4. Place 4-leg credit order.  
5. Manage around central strike and gamma risk.

**Code example**

```py
symbol = "AAPL"
expiry = choose_expiry(days_out=14)
chain = client.get_chain(symbol, expiry)

strike = estimate_atm_strike(symbol)
short_call = pick_strike(chain, kind="call", strike=strike)
short_put  = pick_strike(chain, kind="put",  strike=strike)

long_call  = pick_strike(chain, kind="call", strike=strike + 10)
long_put   = pick_strike(chain, kind="put",  strike=strike - 10)

legs = [
    {"symbol": short_call.symbol, "side": "sell_to_open", "qty": 1},
    {"symbol": short_put.symbol,  "side": "sell_to_open", "qty": 1},
    {"symbol": long_call.symbol,  "side": "buy_to_open",  "qty": 1},
    {"symbol": long_put.symbol,   "side": "buy_to_open",  "qty": 1},
]

client.place_multi_leg_order(symbol, legs, net_price=estimate_credit(legs))
client.manage_iron_fly(
    center_strike=strike,
    take_profit_fraction=0.5,
)
```

---

## **17\. Broken-Wing Butterfly**

**Description:** A butterfly spread where one wing is further away than the other, skewing risk/reward to one side.

**Use case & event example:** Used by traders with a directional bias seeking low-cost or credit exposure. Common during earnings when skew favors asymmetric structures.

**Where This Strategy Breaks:** Broken wing butterflies fail when price moves sharply toward the unprotected side, with volatility expansion potentially amplifying losses. Failure often stems from misjudged strike placement, directional bias, and concentrating risk on the wrong side.

**API workflow**

1. Choose symbol/expiry and target center strike.  
2. Construct butterfly with unequal wing distances.  
3. Place 3- or 4-leg order depending on construction.  
4. Monitor around target area and manage if price moves into risk zone.

**Code example**

```py
symbol = "QQQ"
expiry = choose_expiry(days_out=30)
chain = client.get_chain(symbol, expiry)

center = choose_target_price(symbol)

lower = center - 5
upper = center + 15

long_call_lower = pick_strike(chain, kind="call", strike=lower)
short_call_mid1 = pick_strike(chain, kind="call", strike=center)
short_call_mid2 = short_call_mid1  # quantity 2
long_call_upper = pick_strike(chain, kind="call", strike=upper)

legs = [
    {"symbol": long_call_lower.symbol, "side": "buy_to_open",  "qty": 1},
    {"symbol": short_call_mid1.symbol, "side": "sell_to_open", "qty": 2},
    {"symbol": long_call_upper.symbol, "side": "buy_to_open",  "qty": 1},
]

client.place_multi_leg_order(symbol, legs, net_price=estimate_combo_price(legs))
```

---

## **18\. Jade Lizard**

**Description:** A strategy combining a short put and a short call spread designed so there is no risk on one side if premiums are structured properly.

**Use case & event example:** This strategy seeks short-premium exposure without upside risk. It suits bullish or neutral markets after volatility spikes, especially when upside potential is capped.

**Where This Strategy Breaks:** Jade Lizards fail when strong upside momentum challenges the short call, leading to rapid losses. Though downside risk is capped, rapid upside moves and volatility expansion threaten the position. Selling calls too close to the current price or entering before major events like earnings also causes issues. The main risk is underestimating upside speed.

**API workflow**

1. Select symbol/expiry.  
2. Pull chain.  
3. Sell OTM put.  
4. Sell OTM call and buy further OTM call to cap risk.  
5. Ensure total credit \> width of call spread (for no upside risk construction).  
6. Place 3-leg order.

**Code example**

```py
symbol = "SPY"
expiry = choose_expiry(days_out=30)
chain = client.get_chain(symbol, expiry)

short_put  = pick_delta(chain, kind="put",  min_delta=-0.25, max_delta=-0.15)
short_call = pick_delta(chain, kind="call", min_delta=0.2,   max_delta=0.3)
long_call  = pick_above(short_call, width=5)

legs = [
    {"symbol": short_put.symbol,  "side": "sell_to_open", "qty": 1},
    {"symbol": short_call.symbol, "side": "sell_to_open", "qty": 1},
    {"symbol": long_call.symbol,  "side": "buy_to_open",  "qty": 1},
]

net_credit = estimate_credit(legs)
assert net_credit > (long_call.strike - short_call.strike) * 100

client.place_multi_leg_order(symbol, legs, net_price=net_credit)
```

---

## **19\. Christmas Tree / Skip-Strike Butterfly**

**Description:** Multi-strike structures that create asymmetric payoff profiles using three or more strikes, often concentrated near a target level with limited tail risk.

**Use case & event example**: Used when a trader seeks a precise price target or narrow expected range, typically near price magnets like round numbers or high open-interest strikes pre-expiration.

**Where This Strategy Breaks:** Christmas Tree Skip Butterflies fail when sharp early price movement exits the profit zone. These structures are sensitive to strike spacing; large directional moves overwhelm the payoff, and volatility expansion distorts expected risk asymmetry. The most common failure is misjudging the likelihood of price pinning near the target strike.

**API workflow**

1. Select symbol, expiry, and desired price range.  
2. Design strikes around target zone.  
3. Build legs according to specific Christmas tree/skip-strike rules.  
4. Place multi-leg order.  
5. Monitor as with other range-focused structures.

**Code example**

```py
symbol = "SPY"
expiry = choose_expiry(days_out=30)
chain = client.get_chain(symbol, expiry)

strikes = design_christmas_tree_strikes(chain, target_range=(low, high))
legs = build_christmas_tree_legs(chain, strikes)

client.place_multi_leg_order(symbol, legs, net_price=estimate_combo_price(legs))
```

---

# SYNTHETIC POSITIONS

## **20\. Synthetic Long**

**Description:** Replicate long stock using long call \+ short put at the same strike and expiry.

**Use case & event example**: Used as a stock replacement for favorable options margin treatment, often around corporate actions, index rebalances, or tax-sensitive periods when direct stock ownership is undesirable.

**Where This Strategy Breaks:** Synthetic longs fail when volatility drops or execution costs increase, making them less efficient than holding shares. Unexpected behavior can occur around dividends, corporate actions, or early assignment. Risks like slippage and margin requirements, often subtle at entry, can compound due to small, consistent operational inefficiencies.

**API workflow**

1. Select symbol/expiry.  
2. Pull chain.  
3. Choose ATM strike.  
4. Buy ATM call, sell ATM put.  
5. Place 2-leg order.

**Code example**

```py
symbol = "AAPL"
expiry = choose_expiry(days_out=60)
chain = client.get_chain(symbol, expiry)

strike = estimate_atm_strike(symbol)
call = pick_strike(chain, kind="call", strike=strike)
put  = pick_strike(chain, kind="put",  strike=strike)

legs = [
    {"symbol": call.symbol, "side": "buy_to_open",  "qty": 1},
    {"symbol": put.symbol,  "side": "sell_to_open", "qty": 1},
]

client.place_multi_leg_order(symbol, legs, net_price=estimate_combo_price(legs))
```

---

## **21\. Synthetic Short**

**Description:** Replicate short stock using short call \+ long put at the same strike and expiry.

**Use case & event example**: Replicates short stock exposure using options. Typically employed before earnings with strong bearish conviction or when shorting shares is restricted.

**Where This Strategy Breaks:** Synthetic shorts fail during rapid upside moves due to quick loss acceleration. Volatility increases margin requirements and drawdowns. They are also sensitive to assignment risk and execution issues. Sudden reversals are the most common cause of failure.

**API workflow**

1. Select symbol/expiry.  
2. Pull chain.  
3. Choose ATM strike.  
4. Sell ATM call, buy ATM put.  
5. Place 2-leg order.

**Code example**

```py
symbol = "MSFT"
expiry = choose_expiry(days_out=45)
chain = client.get_chain(symbol, expiry)

strike = estimate_atm_strike(symbol)
call = pick_strike(chain, kind="call", strike=strike)
put  = pick_strike(chain, kind="put",  strike=strike)

legs = [
    {"symbol": call.symbol, "side": "sell_to_open", "qty": 1},
    {"symbol": put.symbol,  "side": "buy_to_open",  "qty": 1},
]

client.place_multi_leg_order(symbol, legs, net_price=estimate_combo_price(legs))
```

---

## **22\. Synthetic Covered Call**

**Description:** Synthetic long position (call \+ short put) plus a short call, creating a payoff similar to a covered call using options only.

**Use case & event example**: Generates income without outright stock ownership. Often employed for high-priced stocks after earnings, prioritizing capital efficiency.

**Where This Strategy Breaks:** Synthetic covered calls are vulnerable when the underlying surges past the short call strike, quickly capping gains. Volatility compression hurts the long option's effectiveness and limits short call premium. High execution costs and assignment risk are also factors. The strategy's main struggle is its tendency to behave like outright short call exposure in rapid markets.

**API workflow**

1. Build synthetic long as above.  
2. Add OTM short call.  
3. Place combined 3-leg order.

**Code example**

```py
# Assuming call, put from synthetic long
otm_call = pick_above(call, width=5)

legs = [
    {"symbol": call.symbol,    "side": "buy_to_open",  "qty": 1},
    {"symbol": put.symbol,     "side": "sell_to_open", "qty": 1},
    {"symbol": otm_call.symbol,"side": "sell_to_open", "qty": 1},
]

client.place_multi_leg_order(symbol, legs, net_price=estimate_combo_price(legs))
```

---

## **23\. Conversion / Reversal**

**Description:** Arbitrage-style structures using stock \+ options to exploit put-call parity mispricings (conversions and reversals).

**Use case & event example**: Advanced traders use this to exploit pricing inefficiencies, often occurring around dividends, funding dislocations, or hard-to-borrow stock situations.

**Where This Strategy Breaks:** Conversions and reversals fail when execution costs, slippage, or funding exceed the theoretical edge. Mispricings vanish fast, especially in volatile or illiquid markets, and trades are sensitive to dividends, interest rates, and early assignment. The main failure point is assuming frictionless execution where it doesn't exist.

**API workflow**

1. Detect mispricing vs theoretical parity.  
2. Construct appropriate legs (stock \+ call \+ put).  
3. Place all legs as a coordinated strategy.

**Code example**

```py
symbol = "SPY"
mispricing = detect_parity_mispricing(symbol)

if mispricing:
    legs = build_conversion_or_reversal_legs(symbol, mispricing)
    client.place_multi_leg_order(symbol, legs, net_price=estimate_combo_price(legs))
```

---

# INCOME / PREMIUM STRATEGIES

## **24\. Wheel Strategy**

**Description:** A cycle of selling cash-secured puts to acquire shares and then selling covered calls against those shares; repeated over time.

**Use case & event example**: Used for systematic income and accumulation. Commonly run in sideways or gently trending markets, rotating between CSPs and covered calls as volatility ebbs and flows.

**Where This Strategy Breaks:** The wheel strategy fails due to: sustained downtrends causing repeated assignments and concentrated risk; volatility spikes creating poor entries and reducing flexibility; poor position sizing; and, most commonly, passive management instead of active exposure control.

**API workflow**

1. If no shares → run cash-secured put logic.  
2. If assigned → start covered call logic.  
3. Loop per symbol with risk filters.

**Code example**

```py
def run_wheel(symbol: str):
    while True:
        if not client.has_shares(symbol):
            open_csp(symbol)
            wait_for_profit_or_assignment(symbol)
        else:
            open_covered_calls(symbol)
            wait_for_calls_to_resolve(symbol)
```

---

## **25\. Poor Man’s Covered Call (PMCC)**

**Description:** Use a long-dated deep ITM call (LEAP) instead of stock, and sell shorter-dated OTM calls against it.

**Use case & event example**: Used to replicate covered calls with less capital. Often deployed after pullbacks in high-quality names, using long-dated calls paired with short-term premium sales.

**Where This Strategy Breaks:** Poor Man's Covered Calls fail when the underlying stock is choppy instead of trending, causing the long call to decay or suffer volatility compression. Aggressive short call sales can limit upside, and poor selection of the long call's delta or expiration also contributes to failure. The most common issue is a mismatch between the long-term exposure and short-term income.

**API workflow**

1. Select long-dated expiry and deep ITM call (high delta).  
2. Select near-term expiry OTM call to sell.  
3. Place 2-leg order or sequential orders.  
4. Roll short calls over time.

**Code example**

```py
symbol = "AAPL"
long_expiry = choose_expiry(days_out=365)
short_expiry = choose_expiry(days_out=30)

long_chain = client.get_chain(symbol, long_expiry)
short_chain = client.get_chain(symbol, short_expiry)

leap_call = pick_delta(long_chain, kind="call", min_delta=0.8, max_delta=0.95)
short_call = pick_delta(short_chain, kind="call", min_delta=0.2, max_delta=0.3)

client.place_order(leap_call.symbol, side="buy_to_open", qty=1)
client.place_order(short_call.symbol, side="sell_to_open", qty=1)
```

---

## **26\. Ratio Spreads**

**Description:** Buy 1 option and sell 2 or more options at a different strike to shape convexity and risk, often initiated for a small debit or credit.

**Use case & event example**: Used when traders want cheap convexity with conditional risk. Often placed around earnings, when skew allows favorable ratios that benefit from moderate moves.

**Where This Strategy Breaks:** Ratio spreads fail when price sharply moves toward the uncovered short options, with volatility expansion quickly amplifying losses due to the extra short exposure. Sharp directional moves and gaps pose the biggest threat. Failure commonly stems from underestimating tail risk and over-reliance on mean reversion.

**API workflow**

1. Select symbol/expiry.  
2. Pull chain.  
3. Choose long option at one strike.  
4. Choose short options at another strike with higher/lower level, ratio \> 1\.  
5. Place multi-leg order with defined quantities.

**Code example**

```py
symbol = "SPY"
expiry = choose_expiry(days_out=30)
chain = client.get_chain(symbol, expiry)

long_call = pick_delta(chain, kind="call", min_delta=0.25, max_delta=0.35)
short_call = pick_above(long_call, width=5)

legs = [
    {"symbol": long_call.symbol,  "side": "buy_to_open",  "qty": 1},
    {"symbol": short_call.symbol, "side": "sell_to_open", "qty": 2},
]

client.place_multi_leg_order(symbol, legs, net_price=estimate_combo_price(legs))
```

---

# ADVANCED / QUANT STRATEGIES

## **27\. Box Spread**

**Description:** A combination of a bull call spread and a bear put spread with the same strikes and expiry, synthetically creating a fixed payoff.

**Use case & event example**: Used to create synthetic financing when pricing deviates from theory. Typically appears during rate dislocations or stressed funding environments.

**Where This Strategy Breaks:** Box spreads fail when execution costs (commissions, slippage, financing, margin) negate the theoretical payoff. They are highly sensitive to early assignment, interest rate changes, and liquidity. The main risk is treating the trade as risk-free when operational factors dominate.

**API workflow**

1. Detect pricing suitable for box construction.  
2. Construct 4-leg box.  
3. Place multi-leg order.

**Code example**

```py
symbol = "SPY"
expiry = choose_expiry(days_out=180)
chain = client.get_chain(symbol, expiry)

legs = build_box_spread_legs(chain)
client.place_multi_leg_order(symbol, legs, net_price=estimate_combo_price(legs))
```

---

## **28\. Risk Reversal**

**Description:** Buy an OTM call and sell an OTM put (bullish) or the reverse (bearish); expresses directional view and skew usage.

**Use case & event example**: Used to express directional conviction while leveraging skew. Often deployed after earnings surprises, when traders want upside exposure while accepting downside assignment risk.

**Where This Strategy Breaks:** Risk reversals fail when the underlying asset moves sharply against the trade's bias. Volatility changes can unevenly reprice the legs, skewing exposure. Gaps, earnings, or macro events causing asymmetric moves pose high vulnerability. The most frequent failure is underestimating the rapid acceleration of losses on the short option.

**API workflow**

1. Select symbol/expiry.  
2. Pull chain.  
3. Pick OTM put and OTM call in desired deltas.  
4. Place multi-leg order with appropriate sides.

**Code example**

```py
symbol = "XOM"
expiry = choose_expiry(days_out=45)
chain = client.get_chain(symbol, expiry)

short_put = pick_delta(chain, kind="put",  min_delta=-0.25, max_delta=-0.15)
long_call = pick_delta(chain, kind="call", min_delta=0.2,   max_delta=0.3)

legs = [
    {"symbol": short_put.symbol, "side": "sell_to_open", "qty": 1},
    {"symbol": long_call.symbol, "side": "buy_to_open",  "qty": 1},
]

client.place_multi_leg_order(symbol, legs, net_price=estimate_combo_price(legs))
```

---

## **29\. Hedged Iron Fly Variants**

**Description:** Iron fly structures with additional tail hedges (e.g., extra OTM options) to better control extreme moves.

**Use case & event example**: Used when traders want premium capture with extra tail protection. Often placed around macro weeks, where unexpected volatility spikes remain possible.

**Where This Strategy Breaks:** Hedged iron fly variants fail when price moves sharply away from the center strike before hedges can offset exposure. Volatility spikes may overwhelm the structure, reducing protection. These trades are highly sensitive to timing, and small misalignments increase risk. Operational complexity and execution friction are the most common causes of failure.

**API workflow**

1. Build base iron fly.  
2. Add extra tail hedges.  
3. Place combined multi-leg order.

**Code example**

```py
symbol = "SPY"
base_legs = build_iron_fly_legs(symbol)
tail_hedges = build_tail_hedge_legs(symbol)

legs = base_legs + tail_hedges
client.place_multi_leg_order(symbol, legs, net_price=estimate_combo_price(legs))
```

---

## **30\. Volatility Arbitrage (IV vs HV)**

**Description:** Strategies that go long or short options based on discrepancies between implied volatility (IV) and realized/historical volatility (HV).

**Use case & event example**: Used when implied volatility diverges meaningfully from realized volatility. Common during earnings season or regime shifts, when IV lags actual movement.

**Where This Strategy Breaks:** IV vs. HV arbitrage fails when realized volatility differs from expectation, or when implied volatility shifts unexpectedly during market changes or events. The trade also breaks down if execution costs, hedging slippage, or mistiming negate the theoretical advantage. Over-relying on persistent historical volatility relationships is the main risk.

**API workflow**

1. Compute HV for each symbol.  
2. Compare HV vs IV per strike/expiry.  
3. Build candidate lists for long/short vol.  
4. Place option baskets accordingly.

**Code example**

```py
universe = ["SPY", "QQQ", "IWM"]

for symbol in universe:
    iv_surface = get_iv_surface(symbol)
    hv = compute_realized_vol(symbol)
    candidates = screen_iv_vs_hv(iv_surface, hv)

    for c in candidates:
        legs = build_vol_arb_legs(c)
        client.place_multi_leg_order(symbol, legs, net_price=estimate_combo_price(legs))
```

---

## **31\. Calendar Strangles / Diagonal Condors**

**Description:** Hybrids that mix calendar and condor logic: different expiries plus multiple strikes to shape term-structure and range views.

**Use case & event example**: Used to express views on both price range and volatility term structure. Often deployed around earnings cycles, selling near-term volatility while holding longer-dated exposure.

### **Where This Strategy Breaks:** Calendar strangles and diagonal condors fail when early, large directional moves overwhelm longer-dated legs before front-month decay can help. Volatility term structure shifts, particularly unexpected back-month IV compression, also distort exposure. These event-sensitive strategies demand precise strike placement; complexity and leg misalignment are the main failure causes.

**API workflow**

1. Select near and far expiries.  
2. Pull both chains.  
3. Build legs across expiries and strikes.  
4. Place multi-leg order.

**Code example**

```py
symbol = "SPY"
near_exp = choose_expiry(days_out=7)
far_exp  = choose_expiry(days_out=45)

near_chain = client.get_chain(symbol, near_exp)
far_chain  = client.get_chain(symbol, far_exp)

legs = build_calendar_condor_legs(near_chain, far_chain)
client.place_multi_leg_order(symbol, legs, net_price=estimate_combo_price(legs))
```

---

# EVENT-DRIVEN WORKFLOWS

## **32\. Earnings IV Crush Engine**

**Description:** A framework for pre- and post-earnings strategies based on implied move, IV levels, and historical behavior.

**Use case & event example**: Used to systematically trade volatility expansion before earnings and contraction after. Triggered by scheduled earnings releases with historically overstated implied moves.

**Where This Strategy Breaks:** Earnings IV crush trades fail when the actual post-earnings move is larger than implied volatility anticipated. Big gaps or sustained trends can overcome short premium before volatility contraction helps. Trades are also vulnerable when earnings guidance signals a regime change. The most common failure is misjudging the balance of expected move versus tail risk.

**API workflow**

1. Ingest earnings calendar.   
2. For each symbol, detect pre-event and post-event windows.  
3. In pre-window, consider long straddles/strangles or defined-risk plays.  
4. In post-window, evaluate short premium or directional spreads.

**Code example**

```py
def earnings_engine(symbols):
    for symbol in symbols:
        event = get_next_earnings(symbol)
        if not event:
            continue

        if in_pre_event_window(event):
            open_pre_earnings_long_vol(symbol, event)
        elif in_post_event_window(event):
            open_post_earnings_premium_or_trend(symbol, event)
```

---

## **33\. Pre-Market IV Expansion**

**Description:** Workflow to react to overnight IV changes and news.

**Use case & event example**: Used to react to overnight news and volatility repricing. Common after earnings, guidance updates, or geopolitical headlines that shift pre-market option pricing.

**Where This Strategy Breaks:** Pre-market IV expansion trades fail when expected catalysts don't sustain price movement post-open. Rapid volatility compression after the open can quickly erode premium. Low pre-market liquidity causes false signals, and misjudging pre-open risk is the most frequent failure.

**API workflow**

1. Monitor overnight IV and price gaps.  
2. Flag symbols exceeding thresholds.  
3. Open appropriate long/short vol strategies at or near the open.

**Code example**

```py
def premarket_iv_engine(symbols):
    for symbol in symbols:
        iv_change = measure_overnight_iv_change(symbol)
        gap = measure_overnight_gap(symbol)
        if iv_change > threshold or abs(gap) > gap_threshold:
            execute_premarket_strategy(symbol, iv_change, gap)
```

---

## **34\. Post-Earnings Drift Automation**

**Description:** Systematic workflow to trade the tendency of stocks to drift in the direction of the earnings surprise over subsequent days.

**Use case & event example**: Used to capture directional follow-through after earnings surprises. Often applied in growth or momentum stocks, where price trends persist beyond the initial reaction.

**Where This Strategy Breaks:** Post-earnings drift automation fails when initial reactions fully price in information, momentum doesn't follow through, or broader market moves (especially risk-off) overwhelm the single stock. Liquidity dry-up after the event causes slippage. The most common failure is entering too late after the initial reaction.

**API workflow**

1. After earnings, read surprise (EPS, revenue, guidance).  
2. Map surprise to directional bias.  
3. Choose directional strategy (single-leg or spread).  
4. Size and place orders.

**Code example**

```py
def post_earnings_drift_engine(symbols):
    for symbol in symbols:
        if not had_earnings_recently(symbol):
            continue
        surprise = get_earnings_surprise(symbol)
        direction = map_surprise_to_direction(surprise)
        strategy = select_directional_structure(direction)
        execute_directional_trade(symbol, strategy)
```

---

## **35\. Macro Events & OPEX / Gamma Workflows**

**Description:** Frameworks for trading around macro prints (CPI, FOMC, NFP) and options expiration (OPEX) where gamma and positioning can impact price.

**Use case & event example:** Used to trade around positioning-driven price behavior. Common around CPI, FOMC, NFP, and monthly OPEX, when dealer gamma and open interest materially affect price action.

**Where This Strategy Breaks:** Macro and OPEX gamma workflows fail when price action is erratic, not directional or pinned. Sudden liquidity shifts, dealer repositioning, or unexpected macro headlines quickly invalidate gamma assumptions. Timing is crucial; entering too early or late in the OPEX cycle distorts outcomes. Overconfidence in pinning without accounting for regime shifts is the primary failure point.

**API workflow**

1. Ingest macro calendar and OPEX dates.  
2. Classify market regime (high/low vol, positioning, gamma levels).  
3. Select strategy template per event/ regime.  
4. Execute with risk limits.

**Code example**

```py
def macro_and_opex_engine(events):
    for event in events:
        symbols = event.related_symbols
        regime = classify_regime(event)

        for symbol in symbols:
            strategy = pick_strategy_for_event(symbol, event, regime)
            execute_event_strategy(symbol, strategy)
```

---

