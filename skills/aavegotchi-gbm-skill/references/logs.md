# Logs / Event Scans (Optional)

You can discover auctions and activity via events, but for day-to-day listing and filtering, prefer the subgraph (`references/subgraph.md`).

If you do use logs:
- Some RPCs restrict `eth_getLogs` to a max block range (commonly 10,000 blocks).
- Some RPCs intermittently 503 on large log queries.
- Chunk your requests.

Constants:
- GBM diamond: `0x80320A0000C7A6a34086E2ACAD6915Ff57FfDA31`
- Deploy block (Base mainnet): `33276452`

## Common Events

- `Auction_Initialized(uint256 indexed _auctionID,uint256 indexed _tokenID,uint256 indexed _tokenAmount,address _contractAddress,bytes4 _tokenKind,uint256 _presetID)`
- `Auction_BidPlaced(uint256 indexed _auctionID,address indexed _bidder,uint256 _bidAmount)`
- `AuctionCancelled(uint256 indexed _auctionId,uint256 _tokenId)`
- `Auction_ItemClaimed(uint256 indexed _auctionID)`

## Example: Fetch Recent Auction_Initialized Logs (Chunked)

```bash
python3 - <<'PY'
import subprocess

rpc = "https://1rpc.io/base"  # override as needed
addr = "0x80320A0000C7A6a34086E2ACAD6915Ff57FfDA31"
event = "Auction_Initialized(uint256,uint256,uint256,address,bytes4,uint256)"

# Keep chunk <= 10k blocks for providers that enforce that limit.
start = 33276452
end = int(subprocess.check_output(["cast", "block-number", "--rpc-url", rpc]).decode().strip())
chunk = 8000

for a in range(start, end + 1, chunk):
    b = min(a + chunk - 1, end)
    cmd = [
        "cast", "logs", event,
        "--from-block", str(a),
        "--to-block", str(b),
        "--address", addr,
        "--rpc-url", rpc,
        "--json",
    ]
    out = subprocess.check_output(cmd)
    if out.strip() not in (b"", b"[]"):
        print(f"range {a}-{b}:", out.decode().strip()[:300], "...")
PY
```
