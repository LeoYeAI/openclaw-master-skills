# OpenSea Stream API (WebSocket)

## Base endpoint
wss://stream.openseabeta.com/socket/websocket?token=YOUR_API_KEY

## Join a collection channel
Send a Phoenix join message:

{"topic":"collection:your-collection-slug","event":"phx_join","payload":{},"ref":1}

Use "collection:*" to subscribe globally.

## Heartbeat
Send every ~30 seconds:

{"topic":"phoenix","event":"heartbeat","payload":{},"ref":0}

## Event types
- item_metadata_updated
- item_listed
- item_sold
- item_transferred
- item_received_bid
- item_cancelled

## Notes
- Stream is WebSocket-based, not HTTP. curl is not suitable.
- Use scripts/opensea-stream-collection.sh (websocat preferred).
