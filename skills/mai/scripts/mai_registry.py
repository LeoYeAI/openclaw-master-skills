#!/usr/bin/env python3
"""Mai registry HTTP service.

This is the hosted marketplace side of Mai's local-first model. Merchant agents
push local store snapshots to the registry; buyer agents search the registry and
create messages or draft orders; merchant agents pull inbox items back locally.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import secrets
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.parse import parse_qs, urlparse


def load_mai_module():
    module_dir = str(Path(__file__).resolve().parent)
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)

    import mai as imported_mai

    if not hasattr(imported_mai, "empty_store"):
        raise ImportError("Imported mai module does not expose empty_store")
    return imported_mai


mai = load_mai_module()


VERSION = "1.1.2"
RISK_TERMS = {
    "fake id",
    "counterfeit",
    "illegal drug",
    "weapon",
    "stolen",
    "passport",
}
RISK_REVIEW_THRESHOLD = 80


def load_registry(path: Path) -> Dict[str, Any]:
    if not path.exists():
        store = mai.empty_store()
        store["registry"] = {
            "service": "mai-registry",
            "version": VERSION,
            "created_at": mai.now_iso(),
        }
        return ensure_registry_defaults(store)
    try:
        store = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Registry data file is not valid JSON: {path}\n{exc}") from exc
    defaults = mai.empty_store()
    for key, value in defaults.items():
        store.setdefault(key, value)
    store.setdefault("registry", {"service": "mai-registry", "version": VERSION})
    return ensure_registry_defaults(store)


def ensure_registry_defaults(store: Dict[str, Any]) -> Dict[str, Any]:
    store.setdefault("auth", {"api_keys": []})
    store["auth"].setdefault("api_keys", [])
    store.setdefault("rate_limits", {})
    store.setdefault("moderation", {"decisions": []})
    store["moderation"].setdefault("decisions", [])
    store.setdefault("payments", {})
    return store


def save_registry(path: Path, store: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def hash_token(token: str, salt: str) -> str:
    return hashlib.sha256((salt + token).encode("utf-8")).hexdigest()


def issue_api_key(
    path: Path,
    token: str,
    role: str,
    subject: str,
    merchant_id: str = "",
    buyer_id: str = "",
) -> Dict[str, Any]:
    if role not in {"admin", "merchant", "buyer"}:
        raise ValueError("role must be admin, merchant, or buyer")
    registry = load_registry(Path(path))
    salt = secrets.token_hex(16)
    record = {
        "id": f"KEY-{len(registry['auth']['api_keys']) + 1:04d}",
        "role": role,
        "subject": subject,
        "merchant_id": merchant_id,
        "buyer_id": buyer_id,
        "salt": salt,
        "token_hash": hash_token(token, salt),
        "active": True,
        "created_at": mai.now_iso(),
    }
    registry["auth"]["api_keys"].append(record)
    save_registry(Path(path), registry)
    return {key: value for key, value in record.items() if key not in {"salt", "token_hash"}}


def authenticate(registry: Dict[str, Any], token: str) -> Dict[str, Any] | None:
    if not token:
        return None
    for record in registry["auth"]["api_keys"]:
        if not record.get("active", True):
            continue
        if hash_token(token, record["salt"]) == record["token_hash"]:
            return {
                "key_id": record["id"],
                "role": record["role"],
                "subject": record["subject"],
                "merchant_id": record.get("merchant_id", ""),
                "buyer_id": record.get("buyer_id", ""),
            }
    return None


def extract_bearer_token(header: str) -> str:
    if not header:
        return ""
    if header.lower().startswith("bearer "):
        return header[7:].strip()
    return ""


def principal_rate_key(principal: Dict[str, Any] | None, client: Tuple[str, int]) -> str:
    if principal:
        return principal["key_id"]
    return f"ip:{client[0]}"


def check_rate_limit(
    registry: Dict[str, Any],
    key: str,
    path: str,
    limit: int,
    now: float | None = None,
) -> bool:
    if limit <= 0 or path == "/health":
        return True
    minute = int((now or time.time()) // 60)
    bucket = f"{key}:{minute}"
    entry = registry["rate_limits"].setdefault(bucket, {"count": 0, "minute": minute})
    entry["count"] += 1
    return int(entry["count"]) <= limit


def score_product_risk(product: Dict[str, Any]) -> Tuple[int, List[str]]:
    searchable = " ".join(
        [
            str(product.get("title", "")),
            str(product.get("description", "")),
            str(product.get("category", "")),
            " ".join(product.get("tags", [])),
        ]
    ).lower()
    reasons = [term for term in RISK_TERMS if term in searchable]
    score = 90 if reasons else 0
    if float(product.get("price", 0) or 0) <= 0:
        score += 20
        reasons.append("non-positive price")
    if not product.get("title"):
        score += 20
        reasons.append("missing title")
    return min(score, 100), reasons


def dedupe_list_append(items: List[Dict[str, Any]], incoming: List[Dict[str, Any]]) -> int:
    existing_keys = {json.dumps(item, ensure_ascii=False, sort_keys=True) for item in items}
    added = 0
    for item in incoming:
        key = json.dumps(item, ensure_ascii=False, sort_keys=True)
        if key in existing_keys:
            continue
        items.append(item)
        existing_keys.add(key)
        added += 1
    return added


def merge_snapshot(registry: Dict[str, Any], snapshot: Dict[str, Any]) -> Dict[str, int]:
    counts = {
        "merchants": 0,
        "products": 0,
        "orders": 0,
        "messages": 0,
        "reviews": 0,
        "inventory_events": 0,
    }
    for merchant_id, merchant in snapshot.get("merchants", {}).items():
        registry["merchants"][merchant_id] = merchant
        counts["merchants"] += 1
    for sku, product in snapshot.get("products", {}).items():
        product = copy.deepcopy(product)
        risk_score, risk_reasons = score_product_risk(product)
        previous = registry["products"].get(sku, {})
        previous_status = previous.get("moderation_status", "")
        product["risk_score"] = risk_score
        product["risk_reasons"] = risk_reasons
        if previous_status in {"approved", "rejected"}:
            product["moderation_status"] = previous_status
            product["active"] = previous_status == "approved"
        elif risk_score >= RISK_REVIEW_THRESHOLD:
            product["moderation_status"] = "pending_review"
            product["active"] = False
        else:
            product["moderation_status"] = "approved"
            product["active"] = product.get("active", True)
        registry["products"][sku] = product
        counts["products"] += 1
    for order_id, order in snapshot.get("orders", {}).items():
        registry["orders"][order_id] = order
        counts["orders"] += 1
    counts["messages"] = dedupe_list_append(registry["messages"], snapshot.get("messages", []))
    counts["reviews"] = dedupe_list_append(registry["reviews"], snapshot.get("reviews", []))
    counts["inventory_events"] = dedupe_list_append(
        registry["inventory_events"],
        snapshot.get("inventory_events", []),
    )
    return counts


def create_message(registry: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    merchant_id = str(payload.get("merchant_id") or payload.get("merchant") or "").strip()
    buyer_id = str(payload.get("buyer_id") or payload.get("buyer") or "").strip()
    sku = str(payload.get("sku") or "").strip()
    text = str(payload.get("text") or "").strip()
    sender = str(payload.get("sender") or "buyer").strip()
    if not merchant_id or not buyer_id or not text:
        raise ValueError("buyer_id, merchant_id, and text are required")
    mai.require_merchant(registry, merchant_id)
    if sku:
        product = mai.require_product(registry, sku)
        if product["merchant_id"] != merchant_id:
            raise ValueError(f"Product {sku} does not belong to merchant {merchant_id}")
    message_id = len(registry["messages"]) + 1
    message = {
        "id": message_id,
        "registry_id": f"MSG-{message_id:04d}",
        "buyer_id": buyer_id,
        "merchant_id": merchant_id,
        "sku": sku,
        "sender": sender,
        "text": text,
        "created_at": mai.now_iso(),
    }
    registry["messages"].append(message)
    return message


def create_order(registry: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    merchant_id = str(payload.get("merchant_id") or payload.get("merchant") or "").strip()
    buyer_id = str(payload.get("buyer_id") or payload.get("buyer") or "").strip()
    sku = str(payload.get("sku") or "").strip()
    quantity = int(payload.get("quantity") or 0)
    if quantity <= 0:
        raise ValueError("quantity must be greater than zero")
    if not merchant_id or not buyer_id or not sku:
        raise ValueError("buyer_id, merchant_id, and sku are required")
    mai.require_merchant(registry, merchant_id)
    product = mai.require_product(registry, sku)
    if product["merchant_id"] != merchant_id:
        raise ValueError(f"Product {sku} does not belong to merchant {merchant_id}")
    order_id = mai.next_order_id(registry["orders"])
    unit_price = float(payload.get("offer_price") if payload.get("offer_price") is not None else product["price"])
    order = {
        "id": order_id,
        "buyer_id": buyer_id,
        "merchant_id": merchant_id,
        "sku": sku,
        "quantity": quantity,
        "requested_unit_price": unit_price,
        "quoted_unit_price": None,
        "currency": product["currency"],
        "status": "draft",
        "note": str(payload.get("note") or ""),
        "payment_url": "",
        "payment_reference": "",
        "terms": "",
        "tracking": "",
        "stock_reserved": False,
        "created_at": mai.now_iso(),
        "updated_at": mai.now_iso(),
        "history": [
            {
                "status": "draft",
                "actor": buyer_id,
                "note": str(payload.get("note") or "Order drafted in registry."),
                "created_at": mai.now_iso(),
            }
        ],
    }
    registry["orders"][order_id] = order
    return order


def merchant_inbox(registry: Dict[str, Any], merchant_id: str) -> Dict[str, Any]:
    mai.require_merchant(registry, merchant_id)
    return {
        "merchant_id": merchant_id,
        "messages": [
            message for message in registry["messages"] if message.get("merchant_id") == merchant_id
        ],
        "orders": [
            order for order in registry["orders"].values() if order.get("merchant_id") == merchant_id
        ],
    }


def next_payment_id(payments: Dict[str, Any]) -> str:
    max_id = 0
    for payment_id in payments:
        if payment_id.startswith("PAY-"):
            try:
                max_id = max(max_id, int(payment_id.split("-", 1)[1]))
            except ValueError:
                continue
    return f"PAY-{max_id + 1:04d}"


def create_payment_hold(registry: Dict[str, Any], payload: Dict[str, Any], provider: str = "demo") -> Dict[str, Any]:
    order_id = str(payload.get("order_id") or payload.get("order") or "").strip()
    buyer_id = str(payload.get("buyer_id") or payload.get("buyer") or "").strip()
    if not order_id or not buyer_id:
        raise ValueError("order_id and buyer_id are required")
    order = mai.require_order(registry, order_id)
    if order["buyer_id"] != buyer_id:
        raise ValueError("buyer_id does not match order")
    for payment in registry["payments"].values():
        if payment["order_id"] == order_id and payment["status"] in {"held_by_psp", "requires_payment"}:
            return payment
    unit_price = float(order.get("quoted_unit_price") or order.get("requested_unit_price") or 0)
    amount = round(unit_price * int(order["quantity"]), 2)
    payment_id = next_payment_id(registry["payments"])
    payment = {
        "id": payment_id,
        "order_id": order_id,
        "buyer_id": buyer_id,
        "merchant_id": order["merchant_id"],
        "amount": amount,
        "currency": order["currency"],
        "provider": provider,
        "provider_reference": f"demo-hold-{payment_id}",
        "checkout_url": f"demo://mai/payments/{payment_id}",
        "status": "held_by_psp",
        "created_at": mai.now_iso(),
        "updated_at": mai.now_iso(),
        "history": [
            {
                "status": "held_by_psp",
                "actor": buyer_id,
                "note": "Demo PSP hold created. Replace with a licensed PSP adapter for production funds.",
                "created_at": mai.now_iso(),
            }
        ],
    }
    registry["payments"][payment_id] = payment
    order["payment_reference"] = payment_id
    order["updated_at"] = mai.now_iso()
    return payment


def transition_payment(payment: Dict[str, Any], new_status: str, actor: str, note: str = "") -> Dict[str, Any]:
    allowed = {
        "held_by_psp": {"released_to_seller", "refunded"},
        "released_to_seller": set(),
        "refunded": set(),
    }
    old_status = payment["status"]
    if new_status not in allowed.get(old_status, set()):
        raise ValueError(f"Invalid payment transition: {old_status} -> {new_status}")
    payment["status"] = new_status
    payment["updated_at"] = mai.now_iso()
    payment.setdefault("history", []).append(
        {
            "from": old_status,
            "status": new_status,
            "actor": actor,
            "note": note,
            "created_at": mai.now_iso(),
        }
    )
    return payment


class RegistryHandler(BaseHTTPRequestHandler):
    server_version = "MaiRegistry/1.1"

    def log_message(self, format: str, *args: Any) -> None:
        if getattr(self.server, "quiet", True):
            return
        super().log_message(format, *args)

    @property
    def data_file(self) -> Path:
        return getattr(self.server, "data_file")

    def authenticate_request(self, registry: Dict[str, Any]) -> Dict[str, Any] | None:
        token = extract_bearer_token(self.headers.get("Authorization", ""))
        if not token:
            token = self.headers.get("X-Mai-Api-Key", "").strip()
        if not token:
            return None
        principal = authenticate(registry, token)
        if principal is None:
            raise PermissionError("invalid API key")
        return principal

    def prepare_request(self, registry: Dict[str, Any]) -> Dict[str, Any] | None:
        principal = self.authenticate_request(registry)
        key = principal_rate_key(principal, self.client_address)
        limit = getattr(self.server, "rate_limit_per_minute", 60)
        if not check_rate_limit(registry, key, urlparse(self.path).path, limit):
            save_registry(self.data_file, registry)
            raise RuntimeError("rate limit exceeded")
        return principal

    def require_authenticated(self, principal: Dict[str, Any] | None) -> Dict[str, Any]:
        if principal is None:
            raise PermissionError("authentication required")
        return principal

    def require_admin(self, principal: Dict[str, Any] | None) -> Dict[str, Any]:
        principal = self.require_authenticated(principal)
        if principal["role"] != "admin":
            raise PermissionError("admin role required")
        return principal

    def require_merchant_access(self, principal: Dict[str, Any] | None, merchant_id: str) -> Dict[str, Any]:
        principal = self.require_authenticated(principal)
        if principal["role"] == "admin":
            return principal
        if principal["role"] == "merchant" and principal.get("merchant_id") == merchant_id:
            return principal
        raise PermissionError(f"merchant access required: {merchant_id}")

    def require_buyer_access(self, principal: Dict[str, Any] | None, buyer_id: str) -> Dict[str, Any]:
        principal = self.require_authenticated(principal)
        if principal["role"] == "admin":
            return principal
        if principal["role"] == "buyer" and principal.get("buyer_id") == buyer_id:
            return principal
        raise PermissionError(f"buyer access required: {buyer_id}")

    def read_json(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError("JSON body must be an object")
        return value

    def send_json(self, status: int, payload: Dict[str, Any]) -> None:
        raw = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def handle_error(self, status: int, message: str) -> None:
        self.send_json(status, {"ok": False, "error": message})

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        registry = load_registry(self.data_file)
        try:
            principal = self.prepare_request(registry)
            if parsed.path == "/health":
                save_registry(self.data_file, registry)
                self.send_json(200, {"ok": True, "service": "mai-registry", "version": VERSION})
                return
            if parsed.path == "/search/products":
                query = parse_qs(parsed.query)
                max_price_values = query.get("max_price") or query.get("max-price") or []
                max_price = float(max_price_values[0]) if max_price_values else None
                results = mai.search_products(
                    registry,
                    (query.get("query") or query.get("q") or [""])[0],
                    max_price,
                    (query.get("city") or [""])[0],
                    (query.get("include_out_of_stock") or ["false"])[0].lower() == "true",
                )
                save_registry(self.data_file, registry)
                self.send_json(200, {"ok": True, "results": results})
                return
            if parsed.path == "/search/merchants":
                query = parse_qs(parsed.query)
                tokens = mai.tokenize((query.get("query") or query.get("q") or [""])[0])
                merchants = []
                for merchant in registry["merchants"].values():
                    searchable = " ".join(
                        [
                            merchant.get("id", ""),
                            merchant.get("name", ""),
                            merchant.get("city", ""),
                            " ".join(merchant.get("tags", [])),
                        ]
                    ).lower()
                    if tokens and not any(token in searchable for token in tokens):
                        continue
                    merchant_id = merchant["id"]
                    merchants.append(
                        {
                            **merchant,
                            "rating": mai.merchant_rating(registry, merchant_id),
                            "product_count": sum(
                                1
                                for product in registry["products"].values()
                                if product["merchant_id"] == merchant_id
                            ),
                        }
                    )
                save_registry(self.data_file, registry)
                self.send_json(200, {"ok": True, "results": sorted(merchants, key=lambda item: item["id"])})
                return
            if parsed.path == "/moderation/queue":
                self.require_admin(principal)
                products = [
                    product
                    for product in registry["products"].values()
                    if product.get("moderation_status") == "pending_review"
                ]
                save_registry(self.data_file, registry)
                self.send_json(200, {"ok": True, "products": sorted(products, key=lambda item: item["sku"])})
                return
            parts = [part for part in parsed.path.split("/") if part]
            if len(parts) == 3 and parts[0] == "merchants" and parts[2] == "inbox":
                self.require_merchant_access(principal, parts[1])
                save_registry(self.data_file, registry)
                self.send_json(200, {"ok": True, **merchant_inbox(registry, parts[1])})
                return
            self.handle_error(404, "not found")
        except PermissionError as exc:
            self.handle_error(401, str(exc))
        except RuntimeError as exc:
            self.handle_error(429, str(exc))
        except (SystemExit, ValueError) as exc:
            self.handle_error(400, str(exc))

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            payload = self.read_json()
            registry = load_registry(self.data_file)
            principal = self.prepare_request(registry)
            if parsed.path == "/sync/push":
                principal = self.require_authenticated(principal)
                if principal["role"] == "merchant":
                    allowed = principal.get("merchant_id", "")
                    merchants = set(payload.get("merchants", {}).keys())
                    product_merchants = {
                        product.get("merchant_id", "")
                        for product in payload.get("products", {}).values()
                    }
                    if merchants - {allowed} or product_merchants - {allowed}:
                        raise PermissionError(f"merchant access required: {allowed}")
                elif principal["role"] != "admin":
                    raise PermissionError("merchant or admin role required")
                counts = merge_snapshot(registry, payload)
                save_registry(self.data_file, registry)
                self.send_json(200, {"ok": True, "pushed": counts})
                return
            if parsed.path == "/messages":
                sender = str(payload.get("sender") or "buyer")
                if sender == "merchant":
                    self.require_merchant_access(principal, str(payload.get("merchant_id") or payload.get("merchant") or ""))
                else:
                    self.require_buyer_access(principal, str(payload.get("buyer_id") or payload.get("buyer") or ""))
                message = create_message(registry, payload)
                save_registry(self.data_file, registry)
                self.send_json(201, {"ok": True, "message": message})
                return
            if parsed.path == "/orders":
                self.require_buyer_access(principal, str(payload.get("buyer_id") or payload.get("buyer") or ""))
                order = create_order(registry, payload)
                save_registry(self.data_file, registry)
                self.send_json(201, {"ok": True, "order": order})
                return
            if parsed.path == "/payments/holds":
                self.require_buyer_access(principal, str(payload.get("buyer_id") or payload.get("buyer") or ""))
                payment = create_payment_hold(
                    registry,
                    payload,
                    provider=getattr(self.server, "payment_provider", "demo"),
                )
                save_registry(self.data_file, registry)
                self.send_json(201, {"ok": True, "payment": payment})
                return
            parts = [part for part in parsed.path.split("/") if part]
            if len(parts) == 3 and parts[0] == "payments" and parts[2] in {"release", "refund"}:
                principal = self.require_admin(principal)
                payment_id = parts[1]
                payment = registry["payments"].get(payment_id)
                if not payment:
                    raise ValueError(f"Unknown payment: {payment_id}")
                status = "released_to_seller" if parts[2] == "release" else "refunded"
                transition_payment(payment, status, principal["subject"], str(payload.get("note") or ""))
                save_registry(self.data_file, registry)
                self.send_json(200, {"ok": True, "payment": payment})
                return
            if len(parts) == 3 and parts[0] == "moderation" and parts[1] == "products":
                principal = self.require_admin(principal)
                product = registry["products"].get(parts[2])
                if not product:
                    raise ValueError(f"Unknown product SKU: {parts[2]}")
                action = str(payload.get("action") or "").strip()
                if action not in {"approve", "reject"}:
                    raise ValueError("action must be approve or reject")
                product["moderation_status"] = "approved" if action == "approve" else "rejected"
                product["active"] = action == "approve"
                product["updated_at"] = mai.now_iso()
                registry["moderation"]["decisions"].append(
                    {
                        "sku": parts[2],
                        "action": action,
                        "actor": principal["subject"],
                        "note": str(payload.get("note") or ""),
                        "created_at": mai.now_iso(),
                    }
                )
                save_registry(self.data_file, registry)
                self.send_json(200, {"ok": True, "product": product})
                return
            self.handle_error(404, "not found")
        except PermissionError as exc:
            self.handle_error(401, str(exc))
        except RuntimeError as exc:
            self.handle_error(429, str(exc))
        except (SystemExit, ValueError) as exc:
            self.handle_error(400, str(exc))


def create_server(
    data_file: Path,
    host: str = "127.0.0.1",
    port: int = 8765,
    rate_limit_per_minute: int = 60,
    payment_provider: str = "demo",
) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), RegistryHandler)
    server.data_file = Path(data_file)
    server.quiet = True
    server.rate_limit_per_minute = rate_limit_per_minute
    server.payment_provider = payment_provider
    return server


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run or manage a Mai registry hosted marketplace server.")
    subparsers = parser.add_subparsers(dest="command")

    serve = subparsers.add_parser("serve", help="Run the registry server")
    serve.add_argument("--data", required=True, help="Registry JSON data file")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)
    serve.add_argument("--rate-limit-per-minute", type=int, default=60)
    serve.add_argument("--payment-provider", choices=["demo"], default="demo")
    serve.add_argument("--verbose", action="store_true")

    issue = subparsers.add_parser("issue-key", help="Issue an API key record")
    issue.add_argument("--data", required=True, help="Registry JSON data file")
    issue.add_argument("--token", required=True, help="Secret token shown once to the operator")
    issue.add_argument("--role", required=True, choices=["admin", "merchant", "buyer"])
    issue.add_argument("--subject", required=True)
    issue.add_argument("--merchant-id", default="")
    issue.add_argument("--buyer-id", default="")
    issue.add_argument("--format", choices=["text", "json"], default="text")

    parser.add_argument("--data", help=argparse.SUPPRESS)
    parser.add_argument("--host", default="127.0.0.1", help=argparse.SUPPRESS)
    parser.add_argument("--port", type=int, default=8765, help=argparse.SUPPRESS)
    parser.add_argument("--rate-limit-per-minute", type=int, default=60, help=argparse.SUPPRESS)
    parser.add_argument("--payment-provider", choices=["demo"], default="demo", help=argparse.SUPPRESS)
    parser.add_argument("--verbose", action="store_true", help=argparse.SUPPRESS)
    return parser


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "issue-key":
        record = issue_api_key(
            Path(args.data),
            token=args.token,
            role=args.role,
            subject=args.subject,
            merchant_id=args.merchant_id,
            buyer_id=args.buyer_id,
        )
        if args.format == "json":
            print(json.dumps({"ok": True, "api_key": record}, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(f"API key issued: {record['id']} role={record['role']} subject={record['subject']}")
        return

    if args.command is None:
        if not args.data:
            parser.error("--data is required")

    server = create_server(
        Path(args.data),
        args.host,
        args.port,
        rate_limit_per_minute=args.rate_limit_per_minute,
        payment_provider=args.payment_provider,
    )
    server.quiet = not args.verbose
    host, port = server.server_address
    print(f"Mai registry listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping Mai registry")
    finally:
        server.server_close()


if __name__ == "__main__":
    main(sys.argv[1:])
