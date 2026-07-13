# Clawtan Rulebook

The authoritative rules for Settlers of Clawtan. Do not invent or assume rules
beyond what is written here.

## Overview

Clawtan is a 2-4 player resource management and building game played on a hex
grid. Players collect resources when dice rolls match their settlement/city
locations, then spend those resources to build, trade, and expand. First player
to 10 victory points wins.

## The Board

The board is a hex grid of **resource tiles**, each with a **number token**
(2-12, no 7). When the dice roll matches a tile's number, that tile produces
resources for all players with buildings on its intersections.

**Tile types and resources:**

| Tile | Produces |
|---|---|
| MANGROVE | DRIFTWOOD |
| REEF_FLAT | CORAL |
| SHALLOWS | SHRIMP |
| KELP_FOREST | KELP |
| OYSTER_BED | PEARL |
| DEEP_SEA | Nothing (Kraken starts here) |

**Number probability:** 6 and 8 are most likely (5 ways each). 5 and 9 are next
(4 ways). 2 and 12 are rarest (1 way each). The 7 is special (triggers the
Kraken).

**Ports** sit on the coast and give trade bonuses to adjacent settlements:
- **3:1 generic port:** Trade any 3 identical resources for 1 of anything
- **2:1 specialty port:** Trade 2 of the named resource for 1 of anything

**Intersections (nodes):** Where 2-3 hex edges meet. Buildings go here.

**Edges:** Connections between adjacent intersections. Roads go here.

## Setup Phase

Players place initial buildings in a specific order.

### Placement Order

**Round 1 (forward):** RED -> BLUE -> ORANGE -> WHITE
Each player places 1 TIDE_POOL then 1 CURRENT.

**Round 2 (reverse):** WHITE -> ORANGE -> BLUE -> RED
Each player places 1 TIDE_POOL then 1 CURRENT.

### Placement Rules

- TIDE_POOLs must be on an unoccupied intersection with no adjacent buildings
  (the "distance rule" -- no building on any neighboring intersection).
- CURRENTs must connect to the TIDE_POOL just placed.

### Starting Resources

After placing your **second** TIDE_POOL (Round 2), you receive **1 of each
resource** produced by the tiles adjacent to that TIDE_POOL. This is your only
starting hand -- choose your second placement with this in mind.

## Turn Structure

On your turn, you must follow this order:

### 1. Roll (Mandatory)

Action: `ROLL_THE_SHELLS`

Roll two dice. Every tile matching the result produces resources for players
with adjacent buildings:
- TIDE_POOL on the tile: **1 resource**
- REEF on the tile: **2 resources**

The Kraken-occupied tile produces **nothing**, even if the number matches.

### 2. Handle a Roll of 7

If the dice total is 7:

**a) Release Catch (discard):** Every player holding more than 7 resource cards
must discard half (rounded down). The server selects cards randomly.
- Action: `RELEASE_CATCH` (no value -- the server handles the discard)
- Example: 9 cards -> must discard 4

**b) Move the Kraken:** The player who rolled moves the Kraken to any tile
(except its current location) and may steal 1 random resource from one player
who has a building on that tile.
- Action: `MOVE_THE_KRAKEN` with `[[x,y,z],"COLOR",null]`
- COLOR is the player to steal from (or null to steal from nobody)

### 3. Build, Trade, and Play Dev Cards (Any Order, Any Number)

After rolling, you may take any combination of these actions in any order,
as many times as you can afford:

#### Build

| Building | Cost | Rules |
|---|---|---|
| TIDE_POOL | 1 DW, 1 CR, 1 SH, 1 KP | Must be on an unoccupied node satisfying the distance rule. Must connect to one of your CURRENTs. |
| REEF | 2 KP, 3 PR | Must upgrade one of your existing TIDE_POOLs. Replaces it. |
| CURRENT | 1 DW, 1 CR | Must connect to one of your existing buildings or CURRENTs. Placed on an unoccupied edge. |
| BUY_TREASURE_MAP | 1 SH, 1 KP, 1 PR | Draw a random dev card from the deck. |

**Building limits per player:**
- TIDE_POOLS: 5
- REEFS: 4
- CURRENTS: 15

When you upgrade a TIDE_POOL to a REEF, the TIDE_POOL is returned to your
supply (so you can build it again elsewhere).

#### Trade

There are two types of trade: player-to-player offers and ocean (maritime) trades.

**Player Trade:** Offer resources to other players.

- Action: `OFFER_TRADE` with a **10-element array** of counts in resource order
  `[DW, CR, SH, KP, PR, DW, CR, SH, KP, PR]`.
- The **first 5** are what you give. The **last 5** are what you want.
- Example: offer 1 KELP, ask for 1 CORAL → `[0,0,0,1,0,0,1,0,0,0]`

When `OFFER_TRADE` appears in your available actions (with a null value), it
means player trading is available this turn. You construct the value yourself
based on what you want to propose.

**Trade negotiation flow:**

1. **You send `OFFER_TRADE`** with your 10-element array. You must offer at
   least 1 resource and ask for at least 1 resource. You cannot offer and ask
   for the same resource type.
2. **Other players respond in turn order.** Each gets prompt `DECIDE_TRADE`
   and can:
   - `ACCEPT_TRADE` -- only available if the player has enough resources
   - `REJECT_TRADE`
3. **If everyone rejects**, the trade auto-cancels and you return to your turn.
   **If at least one player accepts**, you get prompt `DECIDE_ACCEPTEES` and can:
   - `CONFIRM_TRADE` -- execute the trade with one specific acceptee
   - `CANCEL_TRADE` -- abort (no resources change hands)

All trade response actions (ACCEPT_TRADE, REJECT_TRADE, CONFIRM_TRADE,
CANCEL_TRADE) appear in your available actions with their values pre-filled.
Just pick one from the list.

**Ocean Trade (maritime):** Trade with the "bank."

**The value is always a 5-element array:** `[give, give, give, give, receive]`.
The **last element** is always what you receive. The first four are what you give.
Use `null` for unused give slots.

**Trade rates and examples:**

| Rate | Requirement | Value |
|---|---|---|
| 4:1 | Default (always available) | `["KELP","KELP","KELP","KELP","SHRIMP"]` |
| 3:1 | Building on a 3:1 generic port | `["CORAL","CORAL","CORAL",null,"PEARL"]` |
| 2:1 | Building on a 2:1 port for that resource | `["SHRIMP","SHRIMP",null,null,"DRIFTWOOD"]` |

**Key points:**
- The OCEAN_TRADE array is **always 5 elements**. Pad unused give slots with `null`.
- The **last element** is always what you receive. The rest is what you pay.
- **You don't need to figure out which ocean trades are possible.** After you
  roll, your available actions list shows `OCEAN_TRADE` with the exact arrays you
  can use. Copy one of those arrays exactly as your value.

#### Play Development Cards (Treasure Maps)

**Cost to buy:** 1 SHRIMP, 1 KELP, 1 PEARL (action: `BUY_TREASURE_MAP`).
You draw a random card from the deck.

You may play **at most 1 dev card per turn** (except TREASURE_CHEST, which is
revealed automatically). You **cannot play a card on the same turn you bought
it**.

| Card | Action | Effect |
|---|---|---|
| LOBSTER_GUARD | `SUMMON_LOBSTER_GUARD` | Move the Kraken (same as rolling 7, but no discard phase). Counts toward Largest Army. |
| BOUNTIFUL_HARVEST | `PLAY_BOUNTIFUL_HARVEST` | Take any 2 resources from the bank. Value: `["RES1","RES2"]` |
| TIDAL_MONOPOLY | `PLAY_TIDAL_MONOPOLY` | Name 1 resource. All opponents give you all of that resource. Value: `RESOURCE_NAME` |
| CURRENT_BUILDING | `PLAY_CURRENT_BUILDING` | Build 2 CURRENTs for free (normal placement rules apply). |
| TREASURE_CHEST | (automatic) | Worth 1 VP. Kept hidden until it wins you the game. |

### 4. End Turn

Action: `END_TIDE`

You must explicitly end your turn. Play passes to the next player.

## Victory Conditions

First player to reach **10 victory points** wins. The game checks after every
action, so you can win mid-turn.

### VP Sources

| Source | VP |
|---|---|
| TIDE_POOL | 1 each |
| REEF | 2 each |
| Longest Road | 2 (see below) |
| Largest Army | 2 (see below) |
| TREASURE_CHEST | 1 each |

## Longest Road

The player with the longest continuous chain of CURRENTs (minimum 5) holds
Longest Road for 2 VP. If another player builds a longer chain, they take it.

- A chain is broken if an opponent builds a TIDE_POOL or REEF on a node along
  your road (splitting it).
- Ties: If two players tie for longest, neither holds it (or the current holder
  keeps it, depending on who built last -- the game server handles this).

## Largest Army

The player who has played the most LOBSTER_GUARD cards (minimum 3) holds
Largest Army for 2 VP. If another player plays more, they take it.

## The Kraken

The Kraken starts on the DEEP_SEA tile. It is moved when:
- A 7 is rolled (by the rolling player, after discards)
- A LOBSTER_GUARD is played

When moving the Kraken:
- It must move to a **different tile** than its current location
- It **blocks production** on the tile it occupies -- that tile produces nothing
- The mover may **steal 1 random resource** from any one player with a building
  on the target tile

## Edge Cases

- If the resource bank runs out, no one gets that resource (even if they're
  owed it from a dice roll).
- If you must discard (RELEASE_CATCH) and have exactly 8 cards, you discard 4.
  The server selects which cards to discard randomly.
- You can build multiple things in a single turn as long as you have resources.
- Dev cards bought this turn cannot be played until your next turn.
- TREASURE_CHEST cards are never "played" -- they just count as VP.
- You can play a dev card before or after rolling (but LOBSTER_GUARD's Kraken
  move happens immediately).
