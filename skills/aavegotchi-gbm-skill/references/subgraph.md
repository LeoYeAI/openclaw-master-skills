# Subgraph Queries (Base GBM Auctions)

Endpoint:
- `GBM_SUBGRAPH_URL=https://api.goldsky.com/api/public/project_cmh3flagm0001r4p25foufjtt/subgraphs/aavegotchi-gbm-baazaar-base/prod/gn`

Notes:
- `Bytes` fields (addresses) are lowercase in responses; when filtering, use lowercase addresses.
- Treat `Auction.id` as the canonical `auctionId` you pass to `cast` methods.
- Goldsky API key is optional for the public endpoint. If you set `GOLDSKY_API_KEY`, add:
  - `-H "Authorization: Bearer $GOLDSKY_API_KEY"`

## Auction By ID
```bash
curl -s "$GBM_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data '{
  "query":"query($id:ID!){ auction(id:$id){ id type contractAddress tokenId quantity seller highestBid highestBidder totalBids lastBidTime startsAt endsAt claimAt claimed cancelled presetId category buyNowPrice startBidPrice bidDecimals stepMin incMin incMax bidMultiplier dueIncentives auctionDebt } }",
  "variables":{"id":"<AUCTION_ID>"}
}'
```

## Active Auctions (Now Between startsAt and endsAt)
```bash
NOW=$(date +%s)
curl -s "$GBM_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data "{
  \"query\":\"query(\$now:BigInt!){ auctions(first:20, orderBy: endsAt, orderDirection: asc, where:{claimed:false, cancelled:false, startsAt_lte:\$now, endsAt_gt:\$now}){ id type contractAddress tokenId quantity highestBid highestBidder totalBids startsAt endsAt claimAt presetId category seller } }\",
  \"variables\":{\"now\":\"$NOW\"}
}"
```

## Your Auctions (seller)
```bash
curl -s "$GBM_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data '{
  "query":"query($seller:Bytes!){ auctions(first:50, orderBy: createdAt, orderDirection: desc, where:{seller:$seller}){ id type contractAddress tokenId quantity highestBid highestBidder totalBids startsAt endsAt claimAt claimed cancelled } }",
  "variables":{"seller":"<FROM_ADDRESS_LOWERCASE>"}
}'
```

## Bids For An Auction
```bash
curl -s "$GBM_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data '{
  "query":"query($aid:String!){ bids(first:50, orderBy: bidTime, orderDirection: desc, where:{auction:$aid}){ id bidder amount bidTime outbid previousBid previousBidder } }",
  "variables":{"aid":"<AUCTION_ID>"}
}'
```

## Your Bids (bidder)
```bash
curl -s "$GBM_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data '{
  "query":"query($bidder:Bytes!){ bids(first:50, orderBy: bidTime, orderDirection: desc, where:{bidder:$bidder}){ id auction { id type contractAddress tokenId quantity endsAt claimAt claimed cancelled } amount bidTime outbid } }",
  "variables":{"bidder":"<FROM_ADDRESS_LOWERCASE>"}
}'
```

## Subgraph Reachability Smoke Test (Introspection)
```bash
curl -s "$GBM_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data '{ "query":"{ __schema { queryType { fields { name } } } }" }' \
  | python3 -c 'import json,sys; f=[x["name"] for x in json.load(sys.stdin)["data"]["__schema"]["queryType"]["fields"]]; print([n for n in f if n in ("auction","auctions","bid","bids")])'
```
