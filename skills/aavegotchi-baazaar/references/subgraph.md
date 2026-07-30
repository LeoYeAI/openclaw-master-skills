# Subgraph Queries (Base)

Endpoint:
- `SUBGRAPH_URL=https://api.goldsky.com/api/public/project_cmh3flagm0001r4p25foufjtt/subgraphs/aavegotchi-core-base/prod/gn`

Notes:
- `seller`, `erc721TokenAddress`, `erc1155TokenAddress` are `Bytes` fields; use `0x...` hex strings (lowercase is safest).
- ERC1155 listing "type id" field in the subgraph is `erc1155TypeId` (maps to onchain `itemId` / `typeId`).

## ERC721 Listing By ID
```graphql
query($id: ID!) {
  erc721Listing(id: $id) {
    id
    category
    erc721TokenAddress
    tokenId
    seller
    priceInWei
    cancelled
    timeCreated
    timePurchased
  }
}
```

## ERC1155 Listing By ID
```graphql
query($id: ID!) {
  erc1155Listing(id: $id) {
    id
    category
    erc1155TokenAddress
    erc1155TypeId
    quantity
    seller
    priceInWei
    cancelled
    sold
    timeCreated
  }
}
```

## Find Active Listings

ERC721 (active = not cancelled, never purchased):
```graphql
query($first: Int!) {
  erc721Listings(
    first: $first
    orderBy: timeCreated
    orderDirection: desc
    where: { cancelled: false, timePurchased: "0" }
  ) {
    id
    erc721TokenAddress
    tokenId
    seller
    priceInWei
    timeCreated
  }
}
```

ERC1155 (active = not cancelled, not sold):
```graphql
query($first: Int!) {
  erc1155Listings(
    first: $first
    orderBy: timeCreated
    orderDirection: desc
    where: { cancelled: false, sold: false }
  ) {
    id
    erc1155TokenAddress
    erc1155TypeId
    quantity
    seller
    priceInWei
    timeCreated
  }
}
```

## Find Your Newest Listing (Post-Tx)

After you broadcast a list tx, the simplest approach is to pull your newest listings and match on token/typeId:
```graphql
query($seller: Bytes!, $first: Int!) {
  erc721Listings(
    first: $first
    orderBy: timeCreated
    orderDirection: desc
    where: { seller: $seller }
  ) {
    id
    erc721TokenAddress
    tokenId
    priceInWei
    timeCreated
    cancelled
    timePurchased
  }
}
```

Example curl (seller should be lowercase):
```bash
curl -s "$SUBGRAPH_URL" -H 'content-type: application/json' --data '{
  "query":"query($seller: Bytes!, $first: Int!){ erc721Listings(first: $first, orderBy: timeCreated, orderDirection: desc, where:{seller: $seller}){ id erc721TokenAddress tokenId priceInWei timeCreated cancelled timePurchased } }",
  "variables":{ "seller":"<SELLER_ADDRESS_LOWERCASE>", "first":10 }
}'
```
