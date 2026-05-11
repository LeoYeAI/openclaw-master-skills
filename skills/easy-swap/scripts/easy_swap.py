"""
OKX DEX Swap & Broadcast Client
=================================
A production-ready Python client for the OKX DEX Aggregator Swap + Broadcast API (v6).

Complete flow: Swap API (get calldata) -> Sign -> Broadcast -> Verify

Usage:
    from okx_dex_swap import OKXDexSwapClient

    client = OKXDexSwapClient(
        api_key=os.environ["OKX_ACCESS_KEY"],
        secret_key=os.environ["OKX_SECRET_KEY"],
        passphrase=os.environ["OKX_PASSPHRASE"],
    )

    # Step 1: Get swap data
    swap = client.get_swap(
        chain_index="1",
        from_token="0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
        to_token="0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        amount="100000000000000000",  # 0.1 ETH in wei
        slippage="0.5",
        user_wallet="0xYourWallet...",
    )

    # Step 2: Sign externally (user's responsibility)
    signed_tx = sign_with_your_wallet(swap.tx_data)

    # Step 3: Broadcast
    result = client.broadcast(
        chain_index="1",
        address="0xYourWallet...",
        signed_tx=signed_tx,
        enable_mev_protection=True,
    )
    print(f"Tx hash: {result.tx_hash}")

Environment variables:
    OKX_ACCESS_KEY    - API key
    OKX_SECRET_KEY    - Secret key for HMAC signing
    OKX_PASSPHRASE    - Account passphrase
"""

import os
import hmac
import hashlib
import base64
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlencode

try:
    import requests
except ImportError:
    raise ImportError("Please install requests: pip install requests")


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_URL = "https://web3.okx.com"
SWAP_PATH = "/api/v6/dex/aggregator/swap"
BROADCAST_PATH = "/api/v6/dex/pre-transaction/broadcast-transaction"
NATIVE_TOKEN = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"

CHAIN_NAMES = {
    "1": "Ethereum", "56": "BSC", "137": "Polygon",
    "42161": "Arbitrum", "10": "Optimism", "43114": "Avalanche",
    "8453": "Base", "501": "Solana", "130": "Unichain",
}

MEV_SUPPORTED_CHAINS = {"1", "56", "501", "8453"}
EXACT_OUT_CHAINS = {"1", "8453", "56", "42161"}


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class TokenInfo:
    symbol: str
    address: str
    decimal: int
    unit_price: Optional[str]
    is_honeypot: bool
    tax_rate: float

    @classmethod
    def from_api(cls, data: dict) -> "TokenInfo":
        return cls(
            symbol=data.get("tokenSymbol", "UNKNOWN"),
            address=data.get("tokenContractAddress", ""),
            decimal=int(data.get("decimal", "18")),
            unit_price=data.get("tokenUnitPrice"),
            is_honeypot=data.get("isHoneyPot", False),
            tax_rate=float(data.get("taxRate", "0")),
        )


@dataclass
class ApprovalInfo:
    """ERC-20 approval data extracted from signatureData."""
    contract: str
    calldata: str

    @classmethod
    def from_signature_data(cls, sig_data: list) -> Optional["ApprovalInfo"]:
        """Parse approval info from tx.signatureData."""
        for item in sig_data:
            parsed = json.loads(item) if isinstance(item, str) else item
            if "approveContract" in parsed:
                return cls(
                    contract=parsed["approveContract"],
                    calldata=parsed["approveTxCalldata"],
                )
        return None


@dataclass
class SwapTxData:
    """Transaction data returned by the swap API."""
    from_address: str
    to_address: str
    value: str
    data: str
    gas: str
    gas_price: str
    max_priority_fee: str
    min_receive_amount: str
    max_spend_amount: str
    slippage_percent: str
    signature_data: list
    approval: Optional[ApprovalInfo]

    @classmethod
    def from_api(cls, tx: dict) -> "SwapTxData":
        sig_data = tx.get("signatureData", [])
        return cls(
            from_address=tx.get("from", ""),
            to_address=tx.get("to", ""),
            value=tx.get("value", "0"),
            data=tx.get("data", ""),
            gas=tx.get("gas", "0"),
            gas_price=tx.get("gasPrice", "0"),
            max_priority_fee=tx.get("maxPriorityFeePerGas", "0"),
            min_receive_amount=tx.get("minReceiveAmount", "0"),
            max_spend_amount=tx.get("maxSpendAmount", ""),
            slippage_percent=tx.get("slippagePercent", "0"),
            signature_data=sig_data,
            approval=ApprovalInfo.from_signature_data(sig_data),
        )


@dataclass
class DexRoute:
    dex_name: str
    percent: str
    from_symbol: str
    to_symbol: str

    @classmethod
    def from_api(cls, data: dict) -> "DexRoute":
        return cls(
            dex_name=data.get("dexProtocol", {}).get("dexName", "Unknown"),
            percent=data.get("dexProtocol", {}).get("percent", "0"),
            from_symbol=data.get("fromToken", {}).get("tokenSymbol", "?"),
            to_symbol=data.get("toToken", {}).get("tokenSymbol", "?"),
        )


@dataclass
class SwapResult:
    """Complete swap API response."""
    chain_index: str
    from_token: TokenInfo
    to_token: TokenInfo
    from_amount_raw: str
    to_amount_raw: str
    trade_fee_usd: str
    estimate_gas: str
    price_impact_percent: Optional[str]
    routes: list
    swap_mode: str
    tx_data: SwapTxData
    raw_response: dict = field(default_factory=dict, repr=False)

    @property
    def from_amount_human(self) -> float:
        return int(self.from_amount_raw) / (10 ** self.from_token.decimal)

    @property
    def to_amount_human(self) -> float:
        return int(self.to_amount_raw) / (10 ** self.to_token.decimal)

    @property
    def min_receive_human(self) -> float:
        return int(self.tx_data.min_receive_amount) / (10 ** self.to_token.decimal)

    @property
    def exchange_rate(self) -> float:
        if self.from_amount_human == 0:
            return 0.0
        return self.to_amount_human / self.from_amount_human

    @property
    def has_honeypot_risk(self) -> bool:
        return self.from_token.is_honeypot or self.to_token.is_honeypot

    @property
    def needs_approval(self) -> bool:
        return self.tx_data.approval is not None

    def summary(self) -> str:
        lines = []
        chain_name = CHAIN_NAMES.get(self.chain_index, f"Chain {self.chain_index}")
        lines.append(f"=== OKX DEX Swap ({chain_name}) ===")
        lines.append(
            f"Swap: {self.from_amount_human:,.6f} {self.from_token.symbol} -> "
            f"{self.to_amount_human:,.6f} {self.to_token.symbol}"
        )
        lines.append(f"Rate: 1 {self.from_token.symbol} = {self.exchange_rate:,.6f} {self.to_token.symbol}")
        lines.append(f"Min receive: {self.min_receive_human:,.6f} {self.to_token.symbol}")
        lines.append(f"Slippage: {self.tx_data.slippage_percent}%")

        if self.price_impact_percent:
            impact = float(self.price_impact_percent)
            warning = " !! HIGH IMPACT" if abs(impact) > 3 else ""
            lines.append(f"Price Impact: {self.price_impact_percent}%{warning}")

        lines.append(f"Gas Fee (USD): ${self.trade_fee_usd}")
        lines.append(f"Needs approval: {'Yes' if self.needs_approval else 'No'}")

        if self.has_honeypot_risk:
            lines.append("!! HONEYPOT WARNING: One or more tokens flagged as potential scam!")

        if self.routes:
            lines.append("Routing:")
            for r in self.routes:
                lines.append(f"  {r.percent}% {r.from_symbol} -> {r.to_symbol} via {r.dex_name}")

        return "\n".join(lines)


@dataclass
class BroadcastResult:
    """Broadcast API response."""
    order_id: str
    tx_hash: str

    def summary(self, chain_index: str = "1") -> str:
        explorers = {
            "1": f"https://etherscan.io/tx/{self.tx_hash}",
            "56": f"https://bscscan.com/tx/{self.tx_hash}",
            "137": f"https://polygonscan.com/tx/{self.tx_hash}",
            "42161": f"https://arbiscan.io/tx/{self.tx_hash}",
            "8453": f"https://basescan.org/tx/{self.tx_hash}",
            "501": f"https://solscan.io/tx/{self.tx_hash}",
        }
        url = explorers.get(chain_index, f"Tx: {self.tx_hash}")
        return f"Order: {self.order_id}\nTx Hash: {self.tx_hash}\nExplorer: {url}"


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class OKXDexSwapClient:
    """Client for OKX DEX Swap + Broadcast API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        passphrase: Optional[str] = None,
        timeout: int = 30,
    ):
        self.api_key = api_key or os.environ.get("OKX_ACCESS_KEY", "")
        self.secret_key = secret_key or os.environ.get("OKX_SECRET_KEY", "")
        self.passphrase = passphrase or os.environ.get("OKX_PASSPHRASE", "")
        self.timeout = timeout
        self.session = requests.Session()

        if not all([self.api_key, self.secret_key, self.passphrase]):
            raise ValueError(
                "Missing credentials. Set OKX_ACCESS_KEY, OKX_SECRET_KEY, "
                "OKX_PASSPHRASE env vars or pass them to the constructor."
            )

    def _sign(self, timestamp: str, method: str, request_path: str, body: str = "") -> str:
        prehash = timestamp + method + request_path + body
        mac = hmac.new(
            self.secret_key.encode("utf-8"),
            prehash.encode("utf-8"),
            hashlib.sha256,
        )
        return base64.b64encode(mac.digest()).decode("utf-8")

    def _headers(self, method: str, request_path: str, body: str = "") -> dict:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        sig = self._sign(timestamp, method, request_path, body)
        return {
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": sig,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json",
        }

    # --- Swap API (GET) ---
    def get_swap(
        self,
        chain_index: str,
        from_token: str,
        to_token: str,
        amount: str,
        slippage: str,
        user_wallet: str,
        swap_mode: str = "exactIn",
        auto_slippage: bool = False,
        max_auto_slippage: Optional[str] = None,
        approve_transaction: bool = False,
        approve_amount: Optional[str] = None,
        receiver_address: Optional[str] = None,
        fee_percent: Optional[str] = None,
        from_token_referrer: Optional[str] = None,
        to_token_referrer: Optional[str] = None,
        price_impact_protection: Optional[str] = None,
        gas_level: Optional[str] = None,
        gas_limit: Optional[str] = None,
        dex_ids: Optional[str] = None,
        exclude_dex_ids: Optional[str] = None,
        direct_route: Optional[bool] = None,
        disable_rfq: Optional[str] = None,
        calldata_memo: Optional[str] = None,
        compute_unit_price: Optional[str] = None,
        compute_unit_limit: Optional[str] = None,
        tips: Optional[str] = None,
    ) -> SwapResult:
        """Get swap transaction calldata from OKX DEX Aggregator.

        Args:
            chain_index: Chain ID (e.g., "1" for Ethereum).
            from_token: Sell token contract address.
            to_token: Buy token contract address.
            amount: Amount in raw units (with decimals).
            slippage: Slippage tolerance (e.g., "0.5" for 0.5%).
            user_wallet: User's wallet address.
            swap_mode: "exactIn" or "exactOut".
            auto_slippage: Auto-calculate optimal slippage.
            approve_transaction: Include ERC-20 approval data in response.
            ... (see SKILL.md for full parameter docs)

        Returns:
            SwapResult with parsed swap data and tx calldata.
        """
        if swap_mode == "exactOut" and chain_index not in EXACT_OUT_CHAINS:
            raise ValueError(f"exactOut not supported on chain {chain_index}")

        params = {
            "chainIndex": chain_index,
            "fromTokenAddress": from_token,
            "toTokenAddress": to_token,
            "amount": amount,
            "swapMode": swap_mode,
            "slippagePercent": slippage,
            "userWalletAddress": user_wallet,
        }

        # Optional params
        optional = {
            "approveTransaction": str(approve_transaction).lower() if approve_transaction else None,
            "approveAmount": approve_amount,
            "swapReceiverAddress": receiver_address,
            "feePercent": fee_percent,
            "fromTokenReferrerWalletAddress": from_token_referrer,
            "toTokenReferrerWalletAddress": to_token_referrer,
            "priceImpactProtectionPercent": price_impact_protection,
            "gasLevel": gas_level,
            "gaslimit": gas_limit,
            "dexIds": dex_ids,
            "excludeDexIds": exclude_dex_ids,
            "directRoute": str(direct_route).lower() if direct_route is not None else None,
            "disableRFQ": disable_rfq,
            "callDataMemo": calldata_memo,
            "computeUnitPrice": compute_unit_price,
            "computeUnitLimit": compute_unit_limit,
            "tips": tips,
            "autoSlippage": str(auto_slippage).lower() if auto_slippage else None,
            "maxAutoslippagePercent": max_auto_slippage,
        }

        for k, v in optional.items():
            if v is not None:
                params[k] = v

        query = urlencode(params)
        path = f"{SWAP_PATH}?{query}"
        headers = self._headers("GET", path)

        resp = self.session.get(BASE_URL + path, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        if data.get("code") != "0":
            raise Exception(f"Swap API error (code {data.get('code')}): {data.get('msg')}")

        if not data.get("data"):
            raise Exception("Swap API returned empty data")

        item = data["data"][0]
        router = item.get("routerResult", {})
        routes = [DexRoute.from_api(r) for r in router.get("dexRouterList", [])]

        return SwapResult(
            chain_index=router.get("chainIndex", chain_index),
            from_token=TokenInfo.from_api(router.get("fromToken", {})),
            to_token=TokenInfo.from_api(router.get("toToken", {})),
            from_amount_raw=router.get("fromTokenAmount", amount),
            to_amount_raw=router.get("toTokenAmount", "0"),
            trade_fee_usd=router.get("tradeFee", "0"),
            estimate_gas=router.get("estimateGasFee", "0"),
            price_impact_percent=router.get("priceImpactPercent"),
            routes=routes,
            swap_mode=router.get("swapMode", swap_mode),
            tx_data=SwapTxData.from_api(item.get("tx", {})),
            raw_response=item,
        )

    # --- Broadcast API (POST) ---
    def broadcast(
        self,
        chain_index: str,
        address: str,
        signed_tx: str,
        enable_mev_protection: bool = False,
        jito_signed_tx: Optional[str] = None,
    ) -> BroadcastResult:
        """Broadcast a signed transaction to the blockchain.

        Args:
            chain_index: Chain ID.
            address: Sender wallet address.
            signed_tx: Hex-encoded signed transaction string.
            enable_mev_protection: Enable MEV sandwich protection (ETH, BSC, SOL, BASE).
            jito_signed_tx: Base58 Jito transaction (Solana only, required when tips > 0).

        Returns:
            BroadcastResult with orderId and txHash.
        """
        if enable_mev_protection and chain_index not in MEV_SUPPORTED_CHAINS:
            raise ValueError(
                f"MEV protection not supported on chain {chain_index}. "
                f"Supported: {', '.join(MEV_SUPPORTED_CHAINS)}"
            )

        if jito_signed_tx and chain_index != "501":
            raise ValueError("jitoSignedTx is only applicable for Solana (chain 501)")

        body_dict = {
            "chainIndex": chain_index,
            "address": address,
            "signedTx": signed_tx,
        }

        extra = {}
        if enable_mev_protection:
            extra["enableMevProtection"] = True
        if jito_signed_tx:
            extra["jitoSignedTx"] = jito_signed_tx
        if extra:
            body_dict["extraData"] = json.dumps(extra)

        body_str = json.dumps(body_dict)
        headers = self._headers("POST", BROADCAST_PATH, body_str)

        resp = self.session.post(
            BASE_URL + BROADCAST_PATH,
            headers=headers,
            data=body_str,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("code") != "0":
            raise Exception(f"Broadcast error (code {data.get('code')}): {data.get('msg')}")

        if not data.get("data"):
            raise Exception("Broadcast returned empty data")

        result = data["data"][0]
        return BroadcastResult(
            order_id=result.get("orderId", ""),
            tx_hash=result.get("txHash", ""),
        )


# ---------------------------------------------------------------------------
# CLI usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="OKX DEX Swap CLI (quote only, no signing)")
    parser.add_argument("--chain", default="1", help="Chain index (default: 1)")
    parser.add_argument("--from", dest="from_token", required=True, help="From token address")
    parser.add_argument("--to", dest="to_token", required=True, help="To token address")
    parser.add_argument("--amount", required=True, help="Raw amount (with decimals)")
    parser.add_argument("--slippage", default="0.5", help="Slippage percent (default: 0.5)")
    parser.add_argument("--wallet", required=True, help="User wallet address")
    parser.add_argument("--mode", default="exactIn", choices=["exactIn", "exactOut"])

    args = parser.parse_args()

    client = OKXDexSwapClient()
    result = client.get_swap(
        chain_index=args.chain,
        from_token=args.from_token,
        to_token=args.to_token,
        amount=args.amount,
        slippage=args.slippage,
        user_wallet=args.wallet,
        swap_mode=args.mode,
    )
    print(result.summary())
    print(f"\nTx To: {result.tx_data.to_address}")
    print(f"Tx Value: {result.tx_data.value}")
    print(f"Calldata length: {len(result.tx_data.data)} chars")
