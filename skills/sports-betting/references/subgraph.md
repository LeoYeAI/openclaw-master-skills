# Data-feed (subgraph) reference

**URL (Polygon):** `https://thegraph-1.onchainfeed.org/subgraphs/name/azuro-protocol/azuro-data-feed-polygon`  
**Header:** `Content-Type: application/json`.  
**Body:** JSON with `query` (string) and `variables` (object).  
**Game state:** `state` = `"Prematch"` | `"Live"` | `"Stopped"` | `"Finished"`. Only use conditions with `state: "Active"`.

## Canonical query

```graphql
query Games($first: Int!, $where: Game_filter!, $orderBy: Game_orderBy!, $orderDirection: OrderDirection!) {
  games(first: $first, where: $where, orderBy: $orderBy, orderDirection: $orderDirection) {
    gameId
    title
    state
    startsAt
    league { name }
    country { name }
    sport { name }
    participants { name }
    conditions {
      conditionId
      state
      outcomes { outcomeId currentOdds }
    }
  }
}
```

## Example variables

**Prematch (turnover desc):**  
`{ "first": 20, "where": { "state": "Prematch" }, "orderBy": "turnover", "orderDirection": "desc" }`

**Live (turnover desc):**  
`{ "first": 20, "where": { "state": "Live" }, "orderBy": "turnover", "orderDirection": "desc" }`

## Filtering and ordering

**Filtering (optional):** `sport_: { slug: "football" }`, `country_: { slug: "germany" }`, `league_: { slug: "bundesliga" }`, `startsAt_gt` (Unix seconds).

**Ordering:** `orderBy`: `turnover` | `startsAt`; `orderDirection`: `asc` | `desc`.

## Response shape

`data.games` = array of games. Each game: `gameId`, `title`, `state`, `startsAt`, `league.name`, `country.name`, `sport.name`, `participants[]` (each `name`), `conditions[]` with `conditionId`, `state`, `outcomes[]` with `outcomeId`, `currentOdds`.
