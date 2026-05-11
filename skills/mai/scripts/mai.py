#!/usr/bin/env python3
"""Mai shopping matchmaking CLI.

Mai is a local-first helper for OpenClaw/Hermes shopping agents. It keeps the
deterministic marketplace state in JSON while the host agent handles natural
language intake, negotiation, and user-facing explanations.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


APP_NAME = "mai"
VERSION = "1.1.2"
HOME_DATA_PATH = Path.home() / ".local" / "share" / APP_NAME / "mai.json"
DATA_PATH_OVERRIDE: Optional[Path] = None

ORDER_STATUSES = {
    "draft",
    "quoted",
    "confirmed",
    "payment_pending",
    "paid_external",
    "fulfilled",
    "completed",
    "disputed",
    "resolved",
    "refunded",
    "cancelled",
}

ORDER_TRANSITIONS = {
    "draft": {"quoted", "confirmed", "cancelled"},
    "quoted": {"confirmed", "cancelled", "disputed"},
    "confirmed": {"payment_pending", "paid_external", "cancelled", "disputed"},
    "payment_pending": {"paid_external", "cancelled", "disputed"},
    "paid_external": {"fulfilled", "disputed", "refunded"},
    "fulfilled": {"completed", "disputed"},
    "disputed": {"resolved", "refunded", "cancelled"},
    "resolved": {"completed", "refunded"},
    "completed": set(),
    "refunded": set(),
    "cancelled": set(),
}


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def data_path() -> Path:
    return (DATA_PATH_OVERRIDE or HOME_DATA_PATH).expanduser()


def empty_store() -> Dict[str, Any]:
    return {
        "version": VERSION,
        "created_at": now_iso(),
        "sync": {
            "mode": "local-first",
            "schema_version": VERSION,
            "remote_marketplace_url": "",
            "pending_events": [],
        },
        "merchants": {},
        "products": {},
        "orders": {},
        "messages": [],
        "reviews": [],
        "inventory_events": [],
    }


def load_store() -> Dict[str, Any]:
    path = data_path()
    if not path.exists():
        return empty_store()
    try:
        store = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Data file is not valid JSON: {path}\n{exc}") from exc
    defaults = empty_store()
    for key, value in defaults.items():
        store.setdefault(key, value)
    store["sync"].setdefault("mode", "local-first")
    store["sync"].setdefault("schema_version", VERSION)
    store["sync"].setdefault("remote_marketplace_url", "")
    store["sync"].setdefault("pending_events", [])
    return store


def save_store(store: Dict[str, Any]) -> None:
    path = data_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def emit_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def registry_request(
    base_url: str,
    method: str,
    path: str,
    payload: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    url = base_url.rstrip("/") + path
    if query:
        filtered = {key: value for key, value in query.items() if value not in (None, "")}
        if filtered:
            url += "?" + urlencode(filtered)
    data = None
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    request = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=10) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        body = exc.read().decode("utf-8")
        exc.close()
        raise SystemExit(f"Registry request failed: HTTP {exc.code} {body}") from exc
    except URLError as exc:
        raise SystemExit(f"Registry request failed: {exc}") from exc
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Registry returned invalid JSON: {raw}") from exc
    if not result.get("ok", False):
        raise SystemExit(f"Registry request failed: {result.get('error', 'unknown error')}")
    return result


def parse_tags(value: Optional[str]) -> List[str]:
    if not value:
        return []
    parts = re.split(r"[,;，；、\n]+", value)
    return [part.strip() for part in parts if part.strip()]


def tokenize(value: str) -> List[str]:
    return [token.lower() for token in re.findall(r"[\w\u4e00-\u9fff]+", value)]


def require_merchant(store: Dict[str, Any], merchant_id: str) -> Dict[str, Any]:
    merchant = store["merchants"].get(merchant_id)
    if not merchant:
        raise SystemExit(f"Unknown merchant: {merchant_id}")
    return merchant


def require_product(store: Dict[str, Any], sku: str) -> Dict[str, Any]:
    product = store["products"].get(sku)
    if not product:
        raise SystemExit(f"Unknown product SKU: {sku}")
    return product


def require_order(store: Dict[str, Any], order_id: str) -> Dict[str, Any]:
    order = store["orders"].get(order_id)
    if not order:
        raise SystemExit(f"Unknown order: {order_id}")
    return order


def next_order_id(orders: Dict[str, Any]) -> str:
    max_id = 0
    for order_id in orders:
        match = re.fullmatch(r"ORD-(\d+)", order_id)
        if match:
            max_id = max(max_id, int(match.group(1)))
    return f"ORD-{max_id + 1:04d}"


def append_event(store: Dict[str, Any], event_type: str, payload: Dict[str, Any]) -> None:
    event = {
        "id": len(store["sync"]["pending_events"]) + 1,
        "type": event_type,
        "created_at": now_iso(),
        "payload": payload,
    }
    store["sync"]["pending_events"].append(event)


def merchant_rating(store: Dict[str, Any], merchant_id: str) -> Optional[float]:
    ratings = [
        float(review["rating"])
        for review in store["reviews"]
        if review.get("merchant_id") == merchant_id
    ]
    if not ratings:
        return None
    return round(sum(ratings) / len(ratings), 2)


def product_review_count(store: Dict[str, Any], sku: str) -> int:
    return sum(1 for review in store["reviews"] if review.get("sku") == sku)


def product_warnings(store: Dict[str, Any], product: Dict[str, Any]) -> List[str]:
    warnings: List[str] = []
    if product["stock"] <= 0:
        warnings.append("out of stock")
    elif product["stock"] <= 2:
        warnings.append("low stock")
    if product_review_count(store, product["sku"]) == 0:
        warnings.append("no reviews yet")
    merchant = store["merchants"].get(product["merchant_id"], {})
    if not merchant.get("contact"):
        warnings.append("merchant contact missing")
    return warnings


def product_reasons(store: Dict[str, Any], product: Dict[str, Any], query_tokens: List[str]) -> List[str]:
    reasons: List[str] = []
    if product["stock"] > 0:
        reasons.append("in stock")
    rating = merchant_rating(store, product["merchant_id"])
    if rating is not None and rating >= 4.5:
        reasons.append(f"high merchant rating {rating:.1f}")
    searchable = product_search_text(store, product).lower()
    matched = [token for token in query_tokens if token in searchable]
    if matched:
        reasons.append("matches " + ", ".join(matched[:3]))
    return reasons


def product_search_text(store: Dict[str, Any], product: Dict[str, Any]) -> str:
    merchant = store["merchants"].get(product["merchant_id"], {})
    fields = [
        product.get("sku", ""),
        product.get("title", ""),
        product.get("description", ""),
        product.get("category", ""),
        " ".join(product.get("tags", [])),
        merchant.get("name", ""),
        merchant.get("city", ""),
        " ".join(merchant.get("tags", [])),
    ]
    return " ".join(fields)


def product_match_score(store: Dict[str, Any], product: Dict[str, Any], query_tokens: List[str]) -> float:
    searchable = product_search_text(store, product).lower()
    score = 0.0
    for token in query_tokens:
        if token in searchable:
            score += 10
    if product["stock"] > 0:
        score += 5
    rating = merchant_rating(store, product["merchant_id"])
    if rating is not None:
        score += rating
    if product_review_count(store, product["sku"]) > 0:
        score += 2
    score -= float(product["price"]) / 1000
    return round(score, 4)


def product_summary(store: Dict[str, Any], product: Dict[str, Any], query_tokens: Optional[List[str]] = None) -> Dict[str, Any]:
    merchant = store["merchants"].get(product["merchant_id"], {})
    tokens = query_tokens or []
    rating = merchant_rating(store, product["merchant_id"])
    return {
        "sku": product["sku"],
        "title": product["title"],
        "price": product["price"],
        "currency": product["currency"],
        "stock": product["stock"],
        "category": product.get("category", ""),
        "tags": product.get("tags", []),
        "shipping": product.get("shipping", ""),
        "merchant": {
            "id": product["merchant_id"],
            "name": merchant.get("name", ""),
            "city": merchant.get("city", ""),
            "rating": rating,
            "review_count": sum(
                1 for review in store["reviews"] if review.get("merchant_id") == product["merchant_id"]
            ),
        },
        "reasons": product_reasons(store, product, tokens),
        "warnings": product_warnings(store, product),
    }


def search_products(
    store: Dict[str, Any],
    query: str,
    max_price: Optional[float],
    city: Optional[str],
    include_out_of_stock: bool,
) -> List[Dict[str, Any]]:
    query_tokens = tokenize(query)
    results: List[Dict[str, Any]] = []
    for product in store["products"].values():
        merchant = store["merchants"].get(product["merchant_id"], {})
        if not product.get("active", True):
            continue
        if product.get("moderation_status", "approved") not in {"", "approved"}:
            continue
        if max_price is not None and float(product["price"]) > max_price:
            continue
        if city and merchant.get("city", "").lower() != city.lower():
            continue
        if not include_out_of_stock and int(product["stock"]) <= 0:
            continue
        if query_tokens and not any(token in product_search_text(store, product).lower() for token in query_tokens):
            continue
        summary = product_summary(store, product, query_tokens)
        summary["match_score"] = product_match_score(store, product, query_tokens)
        results.append(summary)
    return sorted(results, key=lambda item: (-item["match_score"], item["price"], item["sku"]))


def cmd_merchant_create(args: argparse.Namespace) -> None:
    store = load_store()
    if args.id in store["merchants"]:
        raise SystemExit(f"Merchant already exists: {args.id}")
    store["merchants"][args.id] = {
        "id": args.id,
        "name": args.name,
        "city": args.city or "",
        "contact": args.contact or "",
        "tags": parse_tags(args.tags),
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    append_event(store, "merchant.created", {"merchant_id": args.id})
    save_store(store)
    print(f"Merchant created: {args.id}")


def cmd_merchant_list(args: argparse.Namespace) -> None:
    store = load_store()
    merchants = []
    query_tokens = tokenize(args.query or "")
    for merchant in store["merchants"].values():
        searchable = " ".join(
            [merchant.get("id", ""), merchant.get("name", ""), merchant.get("city", ""), " ".join(merchant.get("tags", []))]
        ).lower()
        if query_tokens and not any(token in searchable for token in query_tokens):
            continue
        merchant_id = merchant["id"]
        merchants.append(
            {
                **merchant,
                "rating": merchant_rating(store, merchant_id),
                "product_count": sum(1 for product in store["products"].values() if product["merchant_id"] == merchant_id),
            }
        )
    merchants = sorted(merchants, key=lambda item: (item["name"], item["id"]))
    if args.format == "json":
        emit_json({"results": merchants})
    else:
        for merchant in merchants:
            print(f"{merchant['id']}: {merchant['name']} ({merchant.get('city', '')})")


def cmd_product_add(args: argparse.Namespace) -> None:
    if args.price < 0:
        raise SystemExit("--price must be non-negative")
    if args.stock < 0:
        raise SystemExit("--stock must be non-negative")
    store = load_store()
    require_merchant(store, args.merchant)
    if args.sku in store["products"]:
        raise SystemExit(f"Product already exists: {args.sku}")
    store["products"][args.sku] = {
        "sku": args.sku,
        "merchant_id": args.merchant,
        "title": args.title,
        "description": args.description or "",
        "category": args.category or "",
        "tags": parse_tags(args.tags),
        "price": float(args.price),
        "currency": args.currency,
        "stock": int(args.stock),
        "shipping": args.shipping or "",
        "active": True,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    store["inventory_events"].append(
        {
            "sku": args.sku,
            "delta": int(args.stock),
            "reason": "initial stock",
            "created_at": now_iso(),
        }
    )
    append_event(store, "product.created", {"sku": args.sku, "merchant_id": args.merchant})
    save_store(store)
    print(f"Product added: {args.sku}")


def cmd_product_stock(args: argparse.Namespace) -> None:
    store = load_store()
    product = require_product(store, args.sku)
    if args.merchant and product["merchant_id"] != args.merchant:
        raise SystemExit(f"Product {args.sku} does not belong to merchant {args.merchant}")
    new_stock = int(product["stock"]) + int(args.adjust)
    if new_stock < 0:
        raise SystemExit("stock cannot go below zero")
    product["stock"] = new_stock
    product["updated_at"] = now_iso()
    store["inventory_events"].append(
        {
            "sku": args.sku,
            "delta": int(args.adjust),
            "reason": args.reason or "manual adjustment",
            "created_at": now_iso(),
        }
    )
    append_event(store, "inventory.adjusted", {"sku": args.sku, "delta": int(args.adjust)})
    save_store(store)
    print(f"Stock updated: {args.sku} -> {new_stock}")


def cmd_product_list(args: argparse.Namespace) -> None:
    store = load_store()
    products = list(store["products"].values())
    if args.merchant:
        products = [product for product in products if product["merchant_id"] == args.merchant]
    summaries = [product_summary(store, product) for product in products]
    summaries = sorted(summaries, key=lambda item: (item["merchant"]["id"], item["sku"]))
    if args.format == "json":
        emit_json({"results": summaries})
    else:
        for product in summaries:
            print(f"{product['sku']}: {product['title']} {product['price']:.2f} {product['currency']} stock={product['stock']}")


def cmd_search_products(args: argparse.Namespace) -> None:
    store = load_store()
    results = search_products(store, args.query or "", args.max_price, args.city, args.include_out_of_stock)
    if args.format == "json":
        emit_json({"query": args.query or "", "results": results})
    else:
        for item in results:
            print(
                f"{item['sku']}: {item['title']} - {item['price']:.2f} {item['currency']} "
                f"from {item['merchant']['name']} stock={item['stock']}"
            )


def cmd_search_merchants(args: argparse.Namespace) -> None:
    args.format = args.format
    cmd_merchant_list(args)


def cmd_compare(args: argparse.Namespace) -> None:
    store = load_store()
    skus = [sku.strip() for sku in args.skus.split(",") if sku.strip()]
    if len(skus) < 2:
        raise SystemExit("compare requires at least two SKUs")
    items = []
    for sku in skus:
        product = require_product(store, sku)
        items.append(product_summary(store, product))
    items = sorted(items, key=lambda item: (item["price"], -item["stock"], item["sku"]))
    min_price = items[0]["price"]
    for item in items:
        item["price_delta"] = round(float(item["price"]) - float(min_price), 2)
    comparison = {
        "items": items,
        "best_value": items[0],
        "tradeoffs": [
            "Mai ranks best_value by available price first, then stock depth. The host agent should still explain merchant rating, shipping, and review tradeoffs.",
            "Payment is tracked as an external reference in this local-first version; do not claim funds are escrowed.",
        ],
    }
    if args.format == "json":
        emit_json(comparison)
    else:
        for item in items:
            print(f"{item['sku']}: {item['price']:.2f} delta={item['price_delta']:.2f}")


def cmd_review_add(args: argparse.Namespace) -> None:
    if args.rating < 1 or args.rating > 5:
        raise SystemExit("--rating must be between 1 and 5")
    store = load_store()
    require_merchant(store, args.merchant)
    if args.sku:
        product = require_product(store, args.sku)
        if product["merchant_id"] != args.merchant:
            raise SystemExit(f"Product {args.sku} does not belong to merchant {args.merchant}")
    review = {
        "id": len(store["reviews"]) + 1,
        "buyer_id": args.buyer,
        "merchant_id": args.merchant,
        "sku": args.sku or "",
        "rating": int(args.rating),
        "comment": args.comment or "",
        "created_at": now_iso(),
    }
    store["reviews"].append(review)
    append_event(store, "review.created", {"review_id": review["id"], "merchant_id": args.merchant, "sku": args.sku or ""})
    save_store(store)
    print(f"Review added: {review['id']}")


def cmd_review_list(args: argparse.Namespace) -> None:
    store = load_store()
    reviews = store["reviews"]
    if args.merchant:
        reviews = [review for review in reviews if review["merchant_id"] == args.merchant]
    if args.sku:
        reviews = [review for review in reviews if review.get("sku") == args.sku]
    if args.format == "json":
        emit_json({"results": reviews})
    else:
        for review in reviews:
            print(f"#{review['id']} {review['rating']}/5 {review['merchant_id']} {review.get('sku', '')}: {review['comment']}")


def cmd_message_add(args: argparse.Namespace) -> None:
    store = load_store()
    require_merchant(store, args.merchant)
    if args.sku:
        product = require_product(store, args.sku)
        if product["merchant_id"] != args.merchant:
            raise SystemExit(f"Product {args.sku} does not belong to merchant {args.merchant}")
    message = {
        "id": len(store["messages"]) + 1,
        "buyer_id": args.buyer,
        "merchant_id": args.merchant,
        "sku": args.sku or "",
        "sender": args.sender,
        "text": args.text,
        "created_at": now_iso(),
    }
    store["messages"].append(message)
    append_event(store, "message.created", {"message_id": message["id"], "merchant_id": args.merchant, "sku": args.sku or ""})
    save_store(store)
    print(f"Message added: {message['id']}")


def cmd_message_list(args: argparse.Namespace) -> None:
    store = load_store()
    messages = store["messages"]
    if args.buyer:
        messages = [message for message in messages if message["buyer_id"] == args.buyer]
    if args.merchant:
        messages = [message for message in messages if message["merchant_id"] == args.merchant]
    if args.sku:
        messages = [message for message in messages if message.get("sku") == args.sku]
    if args.format == "json":
        emit_json({"results": messages})
    else:
        for message in messages:
            print(f"#{message['id']} {message['sender']} {message['merchant_id']} {message.get('sku', '')}: {message['text']}")


def cmd_order_create(args: argparse.Namespace) -> None:
    if args.quantity <= 0:
        raise SystemExit("--quantity must be greater than zero")
    store = load_store()
    require_merchant(store, args.merchant)
    product = require_product(store, args.sku)
    if product["merchant_id"] != args.merchant:
        raise SystemExit(f"Product {args.sku} does not belong to merchant {args.merchant}")
    order_id = next_order_id(store["orders"])
    unit_price = float(args.offer_price) if args.offer_price is not None else float(product["price"])
    order = {
        "id": order_id,
        "buyer_id": args.buyer,
        "merchant_id": args.merchant,
        "sku": args.sku,
        "quantity": int(args.quantity),
        "requested_unit_price": unit_price,
        "quoted_unit_price": None,
        "currency": product["currency"],
        "status": "draft",
        "note": args.note or "",
        "payment_url": "",
        "payment_reference": "",
        "terms": "",
        "tracking": "",
        "stock_reserved": False,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "history": [
            {
                "status": "draft",
                "actor": args.buyer,
                "note": args.note or "Order drafted.",
                "created_at": now_iso(),
            }
        ],
    }
    store["orders"][order_id] = order
    append_event(store, "order.created", {"order_id": order_id, "merchant_id": args.merchant, "sku": args.sku})
    save_store(store)
    print(f"Order created: {order_id}")


def reserve_stock_for_order(store: Dict[str, Any], order: Dict[str, Any]) -> None:
    if order.get("stock_reserved"):
        return
    product = require_product(store, order["sku"])
    quantity = int(order["quantity"])
    if int(product["stock"]) < quantity:
        raise SystemExit(
            f"Insufficient stock for {order['sku']}: need {quantity}, available {product['stock']}"
        )
    product["stock"] = int(product["stock"]) - quantity
    product["updated_at"] = now_iso()
    order["stock_reserved"] = True
    store["inventory_events"].append(
        {
            "sku": order["sku"],
            "delta": -quantity,
            "reason": f"reserved for {order['id']}",
            "created_at": now_iso(),
        }
    )


def release_stock_for_order(store: Dict[str, Any], order: Dict[str, Any], reason: str) -> None:
    if not order.get("stock_reserved"):
        return
    product = require_product(store, order["sku"])
    quantity = int(order["quantity"])
    product["stock"] = int(product["stock"]) + quantity
    product["updated_at"] = now_iso()
    order["stock_reserved"] = False
    store["inventory_events"].append(
        {
            "sku": order["sku"],
            "delta": quantity,
            "reason": reason,
            "created_at": now_iso(),
        }
    )


def change_order_status(
    store: Dict[str, Any],
    order: Dict[str, Any],
    new_status: str,
    actor: str,
    note: str = "",
    payment_reference: str = "",
    tracking: str = "",
) -> None:
    if new_status not in ORDER_STATUSES:
        raise SystemExit(f"Unsupported order status: {new_status}")
    old_status = order["status"]
    if new_status == old_status:
        return
    if new_status not in ORDER_TRANSITIONS[old_status]:
        raise SystemExit(f"Invalid order transition: {old_status} -> {new_status}")
    if new_status == "confirmed":
        reserve_stock_for_order(store, order)
    if new_status in {"cancelled", "refunded"}:
        release_stock_for_order(store, order, f"released after {new_status} for {order['id']}")
    if payment_reference:
        order["payment_reference"] = payment_reference
    if tracking:
        order["tracking"] = tracking
    order["status"] = new_status
    order["updated_at"] = now_iso()
    order["history"].append(
        {
            "from": old_status,
            "status": new_status,
            "actor": actor,
            "note": note,
            "payment_reference": payment_reference,
            "tracking": tracking,
            "created_at": now_iso(),
        }
    )
    append_event(store, "order.status_changed", {"order_id": order["id"], "from": old_status, "to": new_status})


def cmd_order_quote(args: argparse.Namespace) -> None:
    if args.unit_price < 0:
        raise SystemExit("--unit-price must be non-negative")
    store = load_store()
    order = require_order(store, args.order)
    if order["merchant_id"] != args.merchant:
        raise SystemExit(f"Order {args.order} does not belong to merchant {args.merchant}")
    if order["status"] == "draft":
        change_order_status(store, order, "quoted", args.merchant, args.terms or "Merchant quoted the order.")
    elif order["status"] != "quoted":
        raise SystemExit(f"Cannot quote order in status {order['status']}")
    order["quoted_unit_price"] = float(args.unit_price)
    order["payment_url"] = args.payment_url or ""
    order["terms"] = args.terms or ""
    order["updated_at"] = now_iso()
    append_event(store, "order.quoted", {"order_id": args.order, "merchant_id": args.merchant})
    save_store(store)
    print(f"Order quoted: {args.order}")


def cmd_order_update(args: argparse.Namespace) -> None:
    store = load_store()
    order = require_order(store, args.order)
    change_order_status(
        store,
        order,
        args.status,
        args.actor,
        args.note or "",
        args.payment_reference or "",
        args.tracking or "",
    )
    save_store(store)
    print(f"Order updated: {args.order} -> {args.status}")


def cmd_order_show(args: argparse.Namespace) -> None:
    store = load_store()
    order = require_order(store, args.order)
    if args.format == "json":
        emit_json(order)
    else:
        print(f"{order['id']}: {order['status']} {order['sku']} x{order['quantity']}")


def cmd_order_list(args: argparse.Namespace) -> None:
    store = load_store()
    orders = list(store["orders"].values())
    if args.buyer:
        orders = [order for order in orders if order["buyer_id"] == args.buyer]
    if args.merchant:
        orders = [order for order in orders if order["merchant_id"] == args.merchant]
    if args.status:
        orders = [order for order in orders if order["status"] == args.status]
    orders = sorted(orders, key=lambda order: order["id"])
    if args.format == "json":
        emit_json({"results": orders})
    else:
        for order in orders:
            print(f"{order['id']}: {order['status']} {order['sku']} x{order['quantity']}")


def cmd_registry_push(args: argparse.Namespace) -> None:
    store = load_store()
    result = registry_request(args.url, "POST", "/sync/push", store, api_key=args.api_key)
    store.setdefault("sync", {})["remote_marketplace_url"] = args.url.rstrip("/")
    save_store(store)
    if args.format == "json":
        emit_json(result)
    else:
        pushed = result["pushed"]
        print(
            "Registry push complete: "
            f"{pushed['merchants']} merchants, {pushed['products']} products, "
            f"{pushed['orders']} orders"
        )


def cmd_registry_search_products(args: argparse.Namespace) -> None:
    result = registry_request(
        args.url,
        "GET",
        "/search/products",
        query={
            "query": args.query,
            "max_price": args.max_price,
            "city": args.city,
            "include_out_of_stock": "true" if args.include_out_of_stock else "",
        },
        api_key=args.api_key,
    )
    if args.format == "json":
        emit_json({"results": result["results"]})
    else:
        for item in result["results"]:
            print(
                f"{item['sku']}: {item['title']} - {item['price']:.2f} {item['currency']} "
                f"from {item['merchant']['name']} stock={item['stock']}"
            )


def cmd_registry_search_merchants(args: argparse.Namespace) -> None:
    result = registry_request(args.url, "GET", "/search/merchants", query={"query": args.query}, api_key=args.api_key)
    if args.format == "json":
        emit_json({"results": result["results"]})
    else:
        for merchant in result["results"]:
            print(f"{merchant['id']}: {merchant['name']} ({merchant.get('city', '')})")


def cmd_registry_message(args: argparse.Namespace) -> None:
    payload = {
        "buyer_id": args.buyer,
        "merchant_id": args.merchant,
        "sku": args.sku,
        "sender": args.sender,
        "text": args.text,
    }
    result = registry_request(args.url, "POST", "/messages", payload, api_key=args.api_key)
    store = load_store()
    store.setdefault("sync", {})["remote_marketplace_url"] = args.url.rstrip("/")
    save_store(store)
    if args.format == "json":
        emit_json(result)
    else:
        print(f"Registry message created: {result['message']['registry_id']}")


def cmd_registry_order(args: argparse.Namespace) -> None:
    payload = {
        "buyer_id": args.buyer,
        "merchant_id": args.merchant,
        "sku": args.sku,
        "quantity": args.quantity,
        "offer_price": args.offer_price,
        "note": args.note,
    }
    result = registry_request(args.url, "POST", "/orders", payload, api_key=args.api_key)
    store = load_store()
    store.setdefault("sync", {})["remote_marketplace_url"] = args.url.rstrip("/")
    save_store(store)
    if args.format == "json":
        emit_json(result)
    else:
        print(f"Registry order created: {result['order']['id']}")


def cmd_registry_pull(args: argparse.Namespace) -> None:
    result = registry_request(args.url, "GET", f"/merchants/{args.merchant}/inbox", api_key=args.api_key)
    store = load_store()
    store.setdefault("sync", {})["remote_marketplace_url"] = args.url.rstrip("/")

    existing_message_keys = {
        message.get("registry_id") or (
            message.get("buyer_id"),
            message.get("merchant_id"),
            message.get("sku"),
            message.get("text"),
            message.get("created_at"),
        )
        for message in store["messages"]
    }
    pulled_messages = 0
    for message in result["messages"]:
        key = message.get("registry_id") or (
            message.get("buyer_id"),
            message.get("merchant_id"),
            message.get("sku"),
            message.get("text"),
            message.get("created_at"),
        )
        if key in existing_message_keys:
            continue
        store["messages"].append(message)
        existing_message_keys.add(key)
        pulled_messages += 1

    pulled_orders = 0
    for order in result["orders"]:
        if order["id"] not in store["orders"]:
            pulled_orders += 1
        store["orders"][order["id"]] = order

    save_store(store)
    output = {
        "ok": True,
        "merchant_id": args.merchant,
        "pulled": {"messages": pulled_messages, "orders": pulled_orders},
    }
    if args.format == "json":
        emit_json(output)
    else:
        print(f"Registry pull complete: {pulled_messages} messages, {pulled_orders} orders")


def cmd_registry_payment_hold(args: argparse.Namespace) -> None:
    result = registry_request(
        args.url,
        "POST",
        "/payments/holds",
        {
            "buyer_id": args.buyer,
            "order_id": args.order,
        },
        api_key=args.api_key,
    )
    if args.format == "json":
        emit_json(result)
    else:
        print(f"Registry payment held: {result['payment']['id']}")


def cmd_registry_payment_release(args: argparse.Namespace) -> None:
    result = registry_request(
        args.url,
        "POST",
        f"/payments/{args.payment}/release",
        {"note": args.note or ""},
        api_key=args.api_key,
    )
    if args.format == "json":
        emit_json(result)
    else:
        print(f"Registry payment released: {result['payment']['id']}")


def cmd_registry_payment_refund(args: argparse.Namespace) -> None:
    result = registry_request(
        args.url,
        "POST",
        f"/payments/{args.payment}/refund",
        {"note": args.note or ""},
        api_key=args.api_key,
    )
    if args.format == "json":
        emit_json(result)
    else:
        print(f"Registry payment refunded: {result['payment']['id']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mai local-first shopping matchmaking agent helper.")
    parser.add_argument("--data", help=f"Path to JSON store. Default: {HOME_DATA_PATH}")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    merchant = subparsers.add_parser("merchant", help="Manage merchants")
    merchant_sub = merchant.add_subparsers(dest="merchant_command", required=True)
    merchant_create = merchant_sub.add_parser("create", help="Create a merchant profile")
    merchant_create.add_argument("--id", required=True)
    merchant_create.add_argument("--name", required=True)
    merchant_create.add_argument("--city", default="")
    merchant_create.add_argument("--contact", default="")
    merchant_create.add_argument("--tags", default="")
    merchant_create.set_defaults(func=cmd_merchant_create)
    merchant_list = merchant_sub.add_parser("list", help="List or discover merchants")
    merchant_list.add_argument("--query", default="")
    merchant_list.add_argument("--format", choices=["text", "json"], default="text")
    merchant_list.set_defaults(func=cmd_merchant_list)

    product = subparsers.add_parser("product", help="Manage products and inventory")
    product_sub = product.add_subparsers(dest="product_command", required=True)
    product_add = product_sub.add_parser("add", help="Publish a product")
    product_add.add_argument("--merchant", required=True)
    product_add.add_argument("--sku", required=True)
    product_add.add_argument("--title", required=True)
    product_add.add_argument("--price", required=True, type=float)
    product_add.add_argument("--stock", required=True, type=int)
    product_add.add_argument("--currency", default="CNY")
    product_add.add_argument("--category", default="")
    product_add.add_argument("--tags", default="")
    product_add.add_argument("--description", default="")
    product_add.add_argument("--shipping", default="")
    product_add.set_defaults(func=cmd_product_add)
    product_stock = product_sub.add_parser("stock", help="Adjust inventory")
    product_stock.add_argument("--sku", required=True)
    product_stock.add_argument("--merchant", default="")
    product_stock.add_argument("--adjust", required=True, type=int)
    product_stock.add_argument("--reason", default="")
    product_stock.set_defaults(func=cmd_product_stock)
    product_list = product_sub.add_parser("list", help="List products")
    product_list.add_argument("--merchant", default="")
    product_list.add_argument("--format", choices=["text", "json"], default="text")
    product_list.set_defaults(func=cmd_product_list)

    search = subparsers.add_parser("search", help="Discover products or merchants")
    search_sub = search.add_subparsers(dest="search_command", required=True)
    search_products_parser = search_sub.add_parser("products", help="Search products")
    search_products_parser.add_argument("--query", default="")
    search_products_parser.add_argument("--max-price", type=float)
    search_products_parser.add_argument("--city", default="")
    search_products_parser.add_argument("--include-out-of-stock", action="store_true")
    search_products_parser.add_argument("--format", choices=["text", "json"], default="text")
    search_products_parser.set_defaults(func=cmd_search_products)
    search_merchants_parser = search_sub.add_parser("merchants", help="Search merchants")
    search_merchants_parser.add_argument("--query", default="")
    search_merchants_parser.add_argument("--format", choices=["text", "json"], default="text")
    search_merchants_parser.set_defaults(func=cmd_search_merchants)

    compare = subparsers.add_parser("compare", help="Compare products by SKU")
    compare.add_argument("--skus", required=True, help="Comma-separated SKUs")
    compare.add_argument("--format", choices=["text", "json"], default="text")
    compare.set_defaults(func=cmd_compare)

    review = subparsers.add_parser("review", help="Manage reviews")
    review_sub = review.add_subparsers(dest="review_command", required=True)
    review_add = review_sub.add_parser("add", help="Add a buyer review")
    review_add.add_argument("--buyer", required=True)
    review_add.add_argument("--merchant", required=True)
    review_add.add_argument("--sku", default="")
    review_add.add_argument("--rating", required=True, type=int)
    review_add.add_argument("--comment", default="")
    review_add.set_defaults(func=cmd_review_add)
    review_list = review_sub.add_parser("list", help="List reviews")
    review_list.add_argument("--merchant", default="")
    review_list.add_argument("--sku", default="")
    review_list.add_argument("--format", choices=["text", "json"], default="text")
    review_list.set_defaults(func=cmd_review_list)

    message = subparsers.add_parser("message", help="Record buyer/merchant discussion")
    message_sub = message.add_subparsers(dest="message_command", required=True)
    message_add = message_sub.add_parser("add", help="Add a message")
    message_add.add_argument("--buyer", required=True)
    message_add.add_argument("--merchant", required=True)
    message_add.add_argument("--sku", default="")
    message_add.add_argument("--sender", choices=["buyer", "merchant", "agent"], default="buyer")
    message_add.add_argument("--text", required=True)
    message_add.set_defaults(func=cmd_message_add)
    message_list = message_sub.add_parser("list", help="List messages")
    message_list.add_argument("--buyer", default="")
    message_list.add_argument("--merchant", default="")
    message_list.add_argument("--sku", default="")
    message_list.add_argument("--format", choices=["text", "json"], default="text")
    message_list.set_defaults(func=cmd_message_list)

    order = subparsers.add_parser("order", help="Create and track orders")
    order_sub = order.add_subparsers(dest="order_command", required=True)
    order_create = order_sub.add_parser("create", help="Create a draft order")
    order_create.add_argument("--buyer", required=True)
    order_create.add_argument("--merchant", required=True)
    order_create.add_argument("--sku", required=True)
    order_create.add_argument("--quantity", required=True, type=int)
    order_create.add_argument("--offer-price", type=float)
    order_create.add_argument("--note", default="")
    order_create.set_defaults(func=cmd_order_create)
    order_quote = order_sub.add_parser("quote", help="Merchant quotes a draft order")
    order_quote.add_argument("--merchant", required=True)
    order_quote.add_argument("--order", required=True)
    order_quote.add_argument("--unit-price", required=True, type=float)
    order_quote.add_argument("--payment-url", default="")
    order_quote.add_argument("--terms", default="")
    order_quote.set_defaults(func=cmd_order_quote)
    order_update = order_sub.add_parser("update", help="Move an order through the transaction state machine")
    order_update.add_argument("--order", required=True)
    order_update.add_argument("--status", required=True, choices=sorted(ORDER_STATUSES))
    order_update.add_argument("--actor", required=True)
    order_update.add_argument("--note", default="")
    order_update.add_argument("--payment-reference", default="")
    order_update.add_argument("--tracking", default="")
    order_update.set_defaults(func=cmd_order_update)
    order_show = order_sub.add_parser("show", help="Show one order")
    order_show.add_argument("--order", required=True)
    order_show.add_argument("--format", choices=["text", "json"], default="text")
    order_show.set_defaults(func=cmd_order_show)
    order_list = order_sub.add_parser("list", help="List orders")
    order_list.add_argument("--buyer", default="")
    order_list.add_argument("--merchant", default="")
    order_list.add_argument("--status", choices=sorted(ORDER_STATUSES))
    order_list.add_argument("--format", choices=["text", "json"], default="text")
    order_list.set_defaults(func=cmd_order_list)

    registry = subparsers.add_parser("registry", help="Sync with a Mai registry marketplace")
    registry_sub = registry.add_subparsers(dest="registry_command", required=True)
    registry_push = registry_sub.add_parser("push", help="Push this local store to a registry")
    registry_push.add_argument("--url", required=True)
    registry_push.add_argument("--api-key", default="")
    registry_push.add_argument("--format", choices=["text", "json"], default="text")
    registry_push.set_defaults(func=cmd_registry_push)
    registry_search_products = registry_sub.add_parser("search-products", help="Search products in a registry")
    registry_search_products.add_argument("--url", required=True)
    registry_search_products.add_argument("--api-key", default="")
    registry_search_products.add_argument("--query", default="")
    registry_search_products.add_argument("--max-price", type=float)
    registry_search_products.add_argument("--city", default="")
    registry_search_products.add_argument("--include-out-of-stock", action="store_true")
    registry_search_products.add_argument("--format", choices=["text", "json"], default="text")
    registry_search_products.set_defaults(func=cmd_registry_search_products)
    registry_search_merchants = registry_sub.add_parser("search-merchants", help="Search merchants in a registry")
    registry_search_merchants.add_argument("--url", required=True)
    registry_search_merchants.add_argument("--api-key", default="")
    registry_search_merchants.add_argument("--query", default="")
    registry_search_merchants.add_argument("--format", choices=["text", "json"], default="text")
    registry_search_merchants.set_defaults(func=cmd_registry_search_merchants)
    registry_message = registry_sub.add_parser("message", help="Create a buyer/merchant message in a registry")
    registry_message.add_argument("--url", required=True)
    registry_message.add_argument("--api-key", default="")
    registry_message.add_argument("--buyer", required=True)
    registry_message.add_argument("--merchant", required=True)
    registry_message.add_argument("--sku", default="")
    registry_message.add_argument("--sender", choices=["buyer", "merchant", "agent"], default="buyer")
    registry_message.add_argument("--text", required=True)
    registry_message.add_argument("--format", choices=["text", "json"], default="text")
    registry_message.set_defaults(func=cmd_registry_message)
    registry_order = registry_sub.add_parser("order", help="Create a draft order in a registry")
    registry_order.add_argument("--url", required=True)
    registry_order.add_argument("--api-key", default="")
    registry_order.add_argument("--buyer", required=True)
    registry_order.add_argument("--merchant", required=True)
    registry_order.add_argument("--sku", required=True)
    registry_order.add_argument("--quantity", required=True, type=int)
    registry_order.add_argument("--offer-price", type=float)
    registry_order.add_argument("--note", default="")
    registry_order.add_argument("--format", choices=["text", "json"], default="text")
    registry_order.set_defaults(func=cmd_registry_order)
    registry_pull = registry_sub.add_parser("pull", help="Pull registry messages and orders for a merchant")
    registry_pull.add_argument("--url", required=True)
    registry_pull.add_argument("--api-key", default="")
    registry_pull.add_argument("--merchant", required=True)
    registry_pull.add_argument("--format", choices=["text", "json"], default="text")
    registry_pull.set_defaults(func=cmd_registry_pull)
    registry_payment_hold = registry_sub.add_parser("payment-hold", help="Create a PSP-backed payment hold for an order")
    registry_payment_hold.add_argument("--url", required=True)
    registry_payment_hold.add_argument("--api-key", default="")
    registry_payment_hold.add_argument("--buyer", required=True)
    registry_payment_hold.add_argument("--order", required=True)
    registry_payment_hold.add_argument("--format", choices=["text", "json"], default="text")
    registry_payment_hold.set_defaults(func=cmd_registry_payment_hold)
    registry_payment_release = registry_sub.add_parser("payment-release", help="Release a held payment to the seller")
    registry_payment_release.add_argument("--url", required=True)
    registry_payment_release.add_argument("--api-key", default="")
    registry_payment_release.add_argument("--payment", required=True)
    registry_payment_release.add_argument("--note", default="")
    registry_payment_release.add_argument("--format", choices=["text", "json"], default="text")
    registry_payment_release.set_defaults(func=cmd_registry_payment_release)
    registry_payment_refund = registry_sub.add_parser("payment-refund", help="Refund a held payment to the buyer")
    registry_payment_refund.add_argument("--url", required=True)
    registry_payment_refund.add_argument("--api-key", default="")
    registry_payment_refund.add_argument("--payment", required=True)
    registry_payment_refund.add_argument("--note", default="")
    registry_payment_refund.add_argument("--format", choices=["text", "json"], default="text")
    registry_payment_refund.set_defaults(func=cmd_registry_payment_refund)

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    global DATA_PATH_OVERRIDE
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.data:
        DATA_PATH_OVERRIDE = Path(args.data)
    args.func(args)


if __name__ == "__main__":
    main(sys.argv[1:])
