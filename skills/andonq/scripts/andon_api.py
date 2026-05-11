"""
Andon API client — helpers, payload building, TC3-HMAC-SHA256 signing, and HTTP transport.

This module provides:
- Unified success/error response builders
- CreateMCTicket payload construction with safe defaults
- TC3-HMAC-SHA256 request signing (stdlib only: hashlib, hmac)
- HTTP POST transport via urllib
- CLI with argparse (dry-run support)
"""

from __future__ import annotations

import argparse
import base64
import datetime
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Optional

# ──────────────────────────────────────────────
# Constants & defaults
# ──────────────────────────────────────────────

SERVICE = "tandon"
HOST = "tandon.tencentcloudapi.com"
ENDPOINT = f"https://{HOST}"
API_VERSION = "2023-01-04"
CONTENT_TYPE = "application/json; charset=utf-8"
SIGNED_HEADERS = "content-type;host;x-tc-action"

DEFAULT_LEVEL_ID = 0       # placeholder — defer to implementation
DEFAULT_PRIORITY = 0       # placeholder
DEFAULT_TIME_PERIOD = 2    # reasonable default per spec
DEFAULT_SOURCE = 26        # AndonQ source identifier
DEFAULT_TICKET_LIST_PAGE_SIZE = 20


# ──────────────────────────────────────────────
# Time utility
# ──────────────────────────────────────────────

def get_current_time():
    """Return current time info in unified format.

    Provides:
    - now: current datetime string (YYYY-MM-DD HH:MM:SS)
    - today: current date (YYYY-MM-DD)
    - timestamp: Unix timestamp
    - presets: common time ranges (last 7/30/90/365 days)
    """
    now = datetime.datetime.now()
    ts = int(now.timestamp())
    fmt = "%Y-%m-%d %H:%M:%S"
    date_fmt = "%Y-%m-%d"

    presets = {}
    for days in (7, 30, 90, 180, 365):
        start = now - datetime.timedelta(days=days)
        presets[f"last_{days}d"] = {
            "startTime": start.strftime(fmt),
            "endTime": now.strftime(fmt),
        }

    return {
        "now": now.strftime(fmt),
        "today": now.strftime(date_fmt),
        "timestamp": ts,
        "presets": presets,
    }


# ──────────────────────────────────────────────
# Unified response builders
# ──────────────────────────────────────────────

def make_success(action: str, data: dict, request_id: str) -> dict:
    """Build a unified success response."""
    return {
        "success": True,
        "action": action,
        "data": data,
        "requestId": request_id,
    }


def make_error(action: str, code: str, message: str, request_id: str = "") -> dict:
    """Build a unified error response."""
    return {
        "success": False,
        "action": action,
        "error": {
            "code": code,
            "message": message,
        },
        "requestId": request_id,
    }


# ──────────────────────────────────────────────
# Payload building
# ──────────────────────────────────────────────

def build_create_ticket_payload(content: str, category_id: int) -> dict:
    """
    Build a CreateMCTicket request payload with defaults injected.

    category_id maps to the API's LevelId field (third-level category ID
    from GetMCCategoryList).

    Raises ValueError if content is empty or category_id is invalid.
    """
    content = content.strip()
    if not content:
        raise ValueError("Content must be a non-empty string")
    if not isinstance(category_id, int) or category_id <= 0:
        raise ValueError("CategoryId must be a positive integer")

    return {
        "Content": content,
        "LevelId": category_id,
        "Priority": DEFAULT_PRIORITY,
        "TimePeriod": DEFAULT_TIME_PERIOD,
        "Source": DEFAULT_SOURCE,
    }


def build_get_category_list_payload() -> dict:
    """Build a GetMCCategoryList request payload with fixed parameters."""
    return {"RecommendSource": 0, "Area": 2}


def build_get_category_list_by_id_payload(level2_id: int) -> dict:
    """Build a GetMCCategoryListById request payload.

    Fetches third-level categories under the given second-level category.
    Raises ValueError if level2_id is not a positive integer.
    """
    if not isinstance(level2_id, int) or level2_id <= 0:
        raise ValueError("Level2Id must be a positive integer")
    return {"Level2Id": level2_id}


def build_get_ticket_list_payload(
    status_list=None,
    start_time=None,
    end_time=None,
    search=None,
    page=1,
    page_size=DEFAULT_TICKET_LIST_PAGE_SIZE,
    order_field="CreateTime",
    order=1,
    filters=None,
):
    """
    Build a GetMCTicketList request payload with defaults.

    Only includes optional fields when explicitly provided (non-None).
    Order is uint64: 0=asc, 1=desc.
    """
    payload = {
        "Page": page,
        "PageSize": page_size,
        "OrderField": order_field,
        "Order": order,
    }

    if status_list is not None:
        payload["StatusIdList"] = status_list
    if start_time is not None:
        payload["StartTime"] = start_time
    if end_time is not None:
        payload["EndTime"] = end_time
    if search is not None:
        payload["Search"] = search
    if filters is not None:
        payload["Filters"] = filters

    return payload


def build_get_ticket_by_id_payload(
    ticket_id,
    return_cos_url=None,
    is_page=None,
    page=1,
    page_size="20",
    sort="desc",
):
    """
    Build a GetMCTicketById request payload.

    Raises ValueError if ticket_id is empty.
    Note: PageSize is string type per API spec, Page is int.
    """
    ticket_id = str(ticket_id).strip()
    if not ticket_id:
        raise ValueError("TicketId must be a non-empty string")

    payload = {
        "TicketId": ticket_id,
        "Page": page,
        "PageSize": str(page_size),
        "Sort": sort,
    }

    if return_cos_url is not None:
        payload["ReturnCosUrl"] = return_cos_url
    if is_page is not None:
        payload["IsPage"] = is_page

    return payload


def build_describe_ticket_payload(ticket_id):
    """
    Build DescribeTicket request payload.
    TicketId is String type. Raises ValueError if empty.
    Region is handled via header, not in payload.
    UinType is hardcoded to 1 (企业维度).
    """
    ticket_id = str(ticket_id).strip()
    if not ticket_id:
        raise ValueError("TicketId must be a non-empty string")

    payload = {"TicketId": ticket_id, "UinType": 1}

    return payload


def build_describe_ticket_operation_payload(ticket_id, offset=None, limit=None):
    """Build DescribeTicketOperation request payload. TicketId is Integer type. UinType hardcoded to 1."""
    try:
        ticket_id = int(ticket_id)
    except (TypeError, ValueError):
        raise ValueError("TicketId must be a valid integer")
    payload = {"TicketId": ticket_id, "UinType": 1}
    if offset is not None:
        payload["Offset"] = offset
    if limit is not None:
        payload["Limit"] = limit
    return payload


def build_describe_organization_tickets_payload(
    start_time,
    end_time,
    offset,
    limit,
    member_uins=None,
    title=None,
    statues=None,       # Note: API spells it "Statues" not "Statuses"
    channels=None,
    tags=None,
    scene_ids=None,
    ids=None,
    service_rates=None,
):
    """
    Build DescribeOrganizationTickets request payload.
    Raises ValueError for invalid required params.
    UinType is hardcoded to 1 (企业维度).
    """
    if not str(start_time).strip():
        raise ValueError("StartTime must be a non-empty string")
    if not str(end_time).strip():
        raise ValueError("EndTime must be a non-empty string")
    if offset < 0:
        raise ValueError("Offset must be >= 0")
    if limit <= 0 or limit > 50:
        raise ValueError("Limit must be > 0 and <= 50")

    payload = {
        "StartTime": start_time,
        "EndTime": end_time,
        "Offset": offset,
        "Limit": limit,
        "UinType": 1,
    }

    if member_uins is not None:
        payload["MemberUins"] = member_uins
    if title is not None:
        payload["Title"] = title
    if statues is not None:
        payload["Statues"] = statues
    if channels is not None:
        payload["Channels"] = channels
    if tags is not None:
        payload["Tags"] = tags
    if scene_ids is not None:
        payload["SceneIds"] = scene_ids
    if ids is not None:
        payload["Ids"] = ids
    if service_rates is not None:
        payload["ServiceRates"] = service_rates

    return payload


def build_update_ticket_status_payload(ticket_id: str, status: int = 2, source: int = DEFAULT_SOURCE) -> dict:
    """Build an UpdateMCTicketStatus request payload.

    Used to close/resolve a ticket by updating its status.

    Args:
        ticket_id: The ticket ID string (e.g. "202603244502").
        status: Target status (default 2 = 已确认/结单).
        source: Request source identifier (default 26 = AndonQ).

    Raises ValueError if ticket_id is empty.
    """
    if not isinstance(ticket_id, str) or not ticket_id.strip():
        raise ValueError("TicketId must be a non-empty string")

    payload = {
        "TicketId": ticket_id.strip(),
        "Status": status,
        "Source": source,
    }
    return payload


def build_add_comment_payload(ticket_id: str, comment: str) -> dict:
    """Build an AddMCComment request payload.

    Encodes comment as base64 (UTF-8) and sets IsEncodeContent=1.
    Injects fixed defaults: Source, SecretContent.

    Raises ValueError if ticket_id or comment is empty/non-string.
    """
    if not isinstance(ticket_id, str) or not ticket_id.strip():
        raise ValueError("TicketId must be a non-empty string")
    if not isinstance(comment, str) or not comment.strip():
        raise ValueError("Comment must be a non-empty string")

    encoded_comment = base64.b64encode(comment.encode("utf-8")).decode("utf-8")

    return {
        "TicketId": ticket_id.strip(),
        "Comment": encoded_comment,
        "SecretContent": "",
        "Source": DEFAULT_SOURCE,
        "IsEncodeContent": 1,
    }


def build_describe_organization_story_payload(story_id):
    """Build DescribeOrganizationStory request payload. StoryId is Integer type."""
    try:
        story_id = int(story_id)
    except (TypeError, ValueError):
        raise ValueError("StoryId must be a valid integer")
    return {"StoryId": story_id}


def build_describe_organization_stories_payload(
    start_time, end_time, offset, limit,
    title=None, statues=None, member_uins=None,
    scene_ids=None, ids=None,
):
    """Build DescribeOrganizationStories request payload. UinType hardcoded to 1."""
    if not str(start_time).strip():
        raise ValueError("StartTime must be a non-empty string")
    if not str(end_time).strip():
        raise ValueError("EndTime must be a non-empty string")
    if offset < 0:
        raise ValueError("Offset must be >= 0")
    if limit <= 0 or limit > 50:
        raise ValueError("Limit must be > 0 and <= 50")
    payload = {"StartTime": start_time, "EndTime": end_time, "Offset": offset, "Limit": limit, "UinType": 1}
    if title is not None:
        payload["Title"] = title
    if statues is not None:
        payload["Statues"] = statues  # API spelling
    if member_uins is not None:
        payload["MemberUins"] = member_uins
    if scene_ids is not None:
        payload["SceneIds"] = scene_ids
    if ids is not None:
        payload["Ids"] = ids
    return payload


# ──────────────────────────────────────────────
# Credential loading
# ──────────────────────────────────────────────

def load_credentials() -> tuple:
    """
    Load AK/SK from environment variables.

    Returns:
        (secret_id, secret_key) tuple

    Raises:
        EnvironmentError if either variable is missing or empty.
    """
    secret_id = os.environ.get("TENCENTCLOUD_SECRET_ID", "").strip()
    secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY", "").strip()

    missing = []
    if not secret_id:
        missing.append("TENCENTCLOUD_SECRET_ID")
    if not secret_key:
        missing.append("TENCENTCLOUD_SECRET_KEY")

    if missing:
        raise EnvironmentError(
            f"Missing or empty credentials: {', '.join(missing)}"
        )

    return secret_id, secret_key


# ──────────────────────────────────────────────
# TC3-HMAC-SHA256 signing
# ──────────────────────────────────────────────

def _sha256hex(data: str) -> str:
    """SHA-256 hex digest of a UTF-8 string."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _hmac_sha256(key: bytes, msg: str) -> bytes:
    """HMAC-SHA256, returns raw bytes."""
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def build_canonical_request(payload: str, action: str) -> str:
    """
    Build the canonical request string for TC3 signing.

    Format:
        HTTPRequestMethod\n
        CanonicalURI\n
        CanonicalQueryString\n
        CanonicalHeaders\n
        SignedHeaders\n
        HashedRequestPayload
    """
    hashed_payload = _sha256hex(payload)
    canonical_headers = (
        f"content-type:{CONTENT_TYPE}\n"
        f"host:{HOST}\n"
        f"x-tc-action:{action.lower()}\n"
    )
    return (
        f"POST\n"
        f"/\n"
        f"\n"
        f"{canonical_headers}\n"
        f"{SIGNED_HEADERS}\n"
        f"{hashed_payload}"
    )


def build_string_to_sign(
    timestamp: int,
    canonical_request_hash: str,
    date: str,
    service: str,
) -> str:
    """
    Build the StringToSign for TC3-HMAC-SHA256.

    Format:
        Algorithm\n
        RequestTimestamp\n
        CredentialScope\n
        HashedCanonicalRequest
    """
    credential_scope = f"{date}/{service}/tc3_request"
    return (
        f"TC3-HMAC-SHA256\n"
        f"{timestamp}\n"
        f"{credential_scope}\n"
        f"{canonical_request_hash}"
    )


def sign_request(
    secret_key: str,
    date: str,
    service: str,
    string_to_sign: str,
) -> str:
    """
    Derive the TC3-HMAC-SHA256 signature.

    Returns hex-encoded signature string (64 chars).
    """
    secret_date = _hmac_sha256(("TC3" + secret_key).encode("utf-8"), date)
    secret_service = _hmac_sha256(secret_date, service)
    secret_signing = _hmac_sha256(secret_service, "tc3_request")
    signature = hmac.new(
        secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return signature


def build_signed_headers(
    action: str,
    payload: str,
    timestamp: Optional[int] = None,
    region: Optional[str] = None,
) -> dict:
    """
    Build fully signed HTTP headers for a Tencent Cloud API request.

    Loads credentials from env, computes TC3-HMAC-SHA256 signature, and returns
    the complete header dict ready for HTTP POST.
    """
    secret_id, secret_key = load_credentials()

    if timestamp is None:
        timestamp = int(time.time())

    # Date in UTC
    utc_date = datetime.datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")

    # Step 1: canonical request
    canonical_request = build_canonical_request(payload, action)
    canonical_request_hash = _sha256hex(canonical_request)

    # Step 2: string to sign
    string_to_sign = build_string_to_sign(
        timestamp=timestamp,
        canonical_request_hash=canonical_request_hash,
        date=utc_date,
        service=SERVICE,
    )

    # Step 3: signature
    signature = sign_request(
        secret_key=secret_key,
        date=utc_date,
        service=SERVICE,
        string_to_sign=string_to_sign,
    )

    # Step 4: authorization header
    credential_scope = f"{utc_date}/{SERVICE}/tc3_request"
    authorization = (
        f"TC3-HMAC-SHA256 "
        f"Credential={secret_id}/{credential_scope}, "
        f"SignedHeaders={SIGNED_HEADERS}, "
        f"Signature={signature}"
    )

    headers = {
        "Authorization": authorization,
        "Content-Type": CONTENT_TYPE,
        "Host": HOST,
        "X-TC-Action": action,
        "X-TC-Timestamp": str(timestamp),
        "X-TC-Version": API_VERSION,
    }

    if region is not None:
        headers["X-TC-Region"] = region

    return headers


# ──────────────────────────────────────────────
# Response normalization
# ──────────────────────────────────────────────

def normalize_create_ticket_response(raw: dict) -> dict:
    """
    Normalize a raw Tencent Cloud CreateMCTicket API response into a unified shape.

    Handles three cases:
    - Success: Response.Data contains TicketId and other fields
    - API error: Response.Error contains Code and Message
    - Malformed: response shape doesn't match expectations

    Returns a unified dict matching make_success / make_error shape.
    """
    action = "CreateMCTicket"

    response_obj = raw.get("Response") if isinstance(raw, dict) else None

    if response_obj is None or not isinstance(response_obj, dict):
        return make_error(
            action,
            "MalformedResponse",
            "Response envelope missing or not a dict",
        )

    request_id = response_obj.get("RequestId", "")

    # Check for API error
    if "Error" in response_obj:
        error_info = response_obj["Error"]
        return make_error(
            action,
            error_info.get("Code", "UnknownError"),
            error_info.get("Message", "Unknown error"),
            request_id,
        )

    # Check for success data
    data = response_obj.get("Data")
    if data is not None:
        return make_success(action, data, request_id)

    # Fallback: Response exists but no Data and no Error
    return make_error(
        action,
        "MalformedResponse",
        "Response present but missing both Data and Error fields",
        request_id,
    )


def normalize_category_list_response(raw: dict) -> dict:
    """
    Normalize GetMCCategoryList response: flatten tree to leaf-level list.

    Filters out children with Visible=0. Injects parentName for context.
    Only leaf (child) categories are returned — parents are groupings.
    """
    action = "GetMCCategoryList"

    response_obj = raw.get("Response") if isinstance(raw, dict) else None

    if response_obj is None or not isinstance(response_obj, dict):
        return make_error(
            action, "MalformedResponse",
            "Response envelope missing or not a dict",
        )

    request_id = response_obj.get("RequestId", "")

    if "Error" in response_obj:
        error_info = response_obj["Error"]
        return make_error(
            action,
            error_info.get("Code", "UnknownError"),
            error_info.get("Message", "Unknown error"),
            request_id,
        )

    data = response_obj.get("Data")
    if data is None or not isinstance(data, dict):
        return make_error(
            action, "MalformedResponse",
            "Response present but missing Data field",
            request_id,
        )

    categories_tree = data.get("Categories", [])
    flat = []
    for parent in categories_tree:
        parent_id = parent.get("Id", 0)
        parent_cell = parent.get("Cell", {})
        parent_name = parent_cell.get("Name", "")
        for child in parent.get("Children", []):
            child_cell = child.get("Cell", {})
            if child_cell.get("Visible", 0) != 1:
                continue
            flat.append({
                "id": child.get("Id", 0),
                "name": child_cell.get("Name", ""),
                "parentId": parent_id,
                "parentName": parent_name,
            })

    return make_success(action, {"categories": flat}, request_id)


def normalize_category_list_by_id_response(raw: dict) -> dict:
    """
    Normalize GetMCCategoryListById response: extract Level 3 categories.

    Returns level1Name, level2Name for context, and a flat list of
    third-level categories with id and name.
    """
    action = "GetMCCategoryListById"

    response_obj = raw.get("Response") if isinstance(raw, dict) else None

    if response_obj is None or not isinstance(response_obj, dict):
        return make_error(
            action, "MalformedResponse",
            "Response envelope missing or not a dict",
        )

    request_id = response_obj.get("RequestId", "")

    if "Error" in response_obj:
        error_info = response_obj["Error"]
        return make_error(
            action,
            error_info.get("Code", "UnknownError"),
            error_info.get("Message", "Unknown error"),
            request_id,
        )

    data = response_obj.get("Data")
    if data is None or not isinstance(data, dict):
        return make_error(
            action, "MalformedResponse",
            "Response present but missing Data field",
            request_id,
        )

    level1_name = data.get("Level1Name", "")
    level2_name = data.get("Level2Name", "")
    categories_raw = data.get("Categories", [])

    categories = []
    for cat in categories_raw:
        cell = cat.get("Cell", {})
        categories.append({
            "id": cat.get("Id", 0),
            "name": cell.get("Name", ""),
        })

    return make_success(action, {
        "level1Name": level1_name,
        "level2Name": level2_name,
        "categories": categories,
    }, request_id)


def normalize_ticket_list_response(raw):
    """Normalize GetMCTicketList response into unified shape."""
    action = "GetMCTicketList"
    response_obj = raw.get("Response") if isinstance(raw, dict) else None

    if response_obj is None or not isinstance(response_obj, dict):
        return make_error(action, "MalformedResponse",
                         "Response envelope missing or not a dict")

    request_id = response_obj.get("RequestId", "")

    if "Error" in response_obj:
        error_info = response_obj["Error"]
        return make_error(action, error_info.get("Code", "UnknownError"),
                         error_info.get("Message", "Unknown error"), request_id)

    data = response_obj.get("Data")
    if data is None:
        return make_error(action, "MalformedResponse",
                         "Response present but missing Data field", request_id)

    return make_success(action, {
        "tickets": data.get("Data", []),
        "total": data.get("Total", 0),
        "toBeAddCount": data.get("ToBeAddCount", 0),
        "toConfirmCount": data.get("ToConfirmCount", 0),
    }, request_id)


def normalize_ticket_detail_response(raw):
    """Normalize GetMCTicketById response into unified shape."""
    action = "GetMCTicketById"
    response_obj = raw.get("Response") if isinstance(raw, dict) else None

    if response_obj is None or not isinstance(response_obj, dict):
        return make_error(action, "MalformedResponse",
                         "Response envelope missing or not a dict")

    request_id = response_obj.get("RequestId", "")

    if "Error" in response_obj:
        error_info = response_obj["Error"]
        return make_error(action, error_info.get("Code", "UnknownError"),
                         error_info.get("Message", "Unknown error"), request_id)

    data = response_obj.get("Data")
    if data is None:
        return make_error(action, "MalformedResponse",
                         "Response present but missing Data field", request_id)

    return make_success(action, data, request_id)


def normalize_describe_ticket_response(raw):
    """Normalize DescribeTicket response — passthrough Data dict (PascalCase)."""
    action = "DescribeTicket"
    response_obj = raw.get("Response") if isinstance(raw, dict) else None

    if response_obj is None or not isinstance(response_obj, dict):
        return make_error(action, "MalformedResponse",
                         "Response envelope missing or not a dict")

    request_id = response_obj.get("RequestId", "")

    if "Error" in response_obj:
        error_info = response_obj["Error"]
        return make_error(action, error_info.get("Code", "UnknownError"),
                         error_info.get("Message", "Unknown error"), request_id)

    data = response_obj.get("Data")
    if data is None or not isinstance(data, dict):
        return make_error(action, "MalformedResponse",
                         "Response present but Data is missing or null", request_id)

    return make_success(action, data, request_id)


def normalize_ticket_operation_response(raw):
    """Normalize DescribeTicketOperation response — extract operation list (camelCase)."""
    action = "DescribeTicketOperation"
    response_obj = raw.get("Response") if isinstance(raw, dict) else None
    if response_obj is None or not isinstance(response_obj, dict):
        return make_error(action, "MalformedResponse", "Response envelope missing or not a dict")
    request_id = response_obj.get("RequestId", "")
    if "Error" in response_obj:
        error_info = response_obj["Error"]
        return make_error(action, error_info.get("Code", "UnknownError"),
                         error_info.get("Message", "Unknown error"), request_id)
    data = response_obj.get("Data")
    if data is None:
        return make_error(action, "MalformedResponse",
                         "Response present but missing Data field", request_id)
    return make_success(action, {
        "ticketId": data.get("TicketId", ""),
        "total": data.get("Total", 0),
        "operations": data.get("TicketOperationInfoList", []),
    }, request_id)


def normalize_organization_tickets_response(raw):
    """Normalize DescribeOrganizationTickets response into unified shape."""
    action = "DescribeOrganizationTickets"
    response_obj = raw.get("Response") if isinstance(raw, dict) else None

    if response_obj is None or not isinstance(response_obj, dict):
        return make_error(action, "MalformedResponse",
                         "Response envelope missing or not a dict")

    request_id = response_obj.get("RequestId", "")

    if "Error" in response_obj:
        error_info = response_obj["Error"]
        return make_error(action, error_info.get("Code", "UnknownError"),
                         error_info.get("Message", "Unknown error"), request_id)

    data = response_obj.get("Data")
    if data is None:
        return make_error(action, "MalformedResponse",
                         "Response present but missing Data field", request_id)

    return make_success(action, {
        "tickets": data.get("Tickets", []),
        "total": data.get("Total", 0),
    }, request_id)


def normalize_organization_story_response(raw):
    """Normalize DescribeOrganizationStory response — passthrough Data.Story (PascalCase)."""
    action = "DescribeOrganizationStory"
    response_obj = raw.get("Response") if isinstance(raw, dict) else None
    if response_obj is None or not isinstance(response_obj, dict):
        return make_error(action, "MalformedResponse", "Response envelope missing or not a dict")
    request_id = response_obj.get("RequestId", "")
    if "Error" in response_obj:
        error_info = response_obj["Error"]
        return make_error(action, error_info.get("Code", "UnknownError"),
                         error_info.get("Message", "Unknown error"), request_id)
    data = response_obj.get("Data")
    if data is None or not isinstance(data, dict):
        return make_error(action, "MalformedResponse",
                         "Response present but Data is missing or null", request_id)
    story = data.get("Story")
    if story is None or not isinstance(story, dict):
        return make_error(action, "MalformedResponse",
                         "Data present but Story field is missing or null", request_id)
    return make_success(action, story, request_id)


def normalize_add_comment_response(raw: dict) -> dict:
    """Normalize AddMCComment response — extract CommentId from Data."""
    action = "AddMCComment"
    response_obj = raw.get("Response") if isinstance(raw, dict) else None

    if response_obj is None or not isinstance(response_obj, dict):
        return make_error(
            action, "MalformedResponse",
            "Response envelope missing or not a dict",
        )

    request_id = response_obj.get("RequestId", "")

    if "Error" in response_obj:
        error_info = response_obj["Error"]
        return make_error(
            action,
            error_info.get("Code", "UnknownError"),
            error_info.get("Message", "Unknown error"),
            request_id,
        )

    data = response_obj.get("Data")
    if data is None or not isinstance(data, dict):
        return make_error(
            action, "MalformedResponse",
            "Response present but missing Data field",
            request_id,
        )

    return make_success(action, {
        "commentId": data.get("CommentId", 0),
    }, request_id)


def normalize_update_ticket_status_response(raw: dict) -> dict:
    """Normalize UpdateMCTicketStatus response — extract Data array."""
    action = "UpdateMCTicketStatus"
    response_obj = raw.get("Response") if isinstance(raw, dict) else None

    if response_obj is None or not isinstance(response_obj, dict):
        return make_error(
            action, "MalformedResponse",
            "Response envelope missing or not a dict",
        )

    request_id = response_obj.get("RequestId", "")

    if "Error" in response_obj:
        error_info = response_obj["Error"]
        return make_error(
            action,
            error_info.get("Code", "UnknownError"),
            error_info.get("Message", "Unknown error"),
            request_id,
        )

    return make_success(action, {
        "message": "工单状态更新成功",
    }, request_id)


def normalize_organization_stories_response(raw):
    """Normalize DescribeOrganizationStories response (camelCase)."""
    action = "DescribeOrganizationStories"
    response_obj = raw.get("Response") if isinstance(raw, dict) else None
    if response_obj is None or not isinstance(response_obj, dict):
        return make_error(action, "MalformedResponse", "Response envelope missing or not a dict")
    request_id = response_obj.get("RequestId", "")
    if "Error" in response_obj:
        error_info = response_obj["Error"]
        return make_error(action, error_info.get("Code", "UnknownError"),
                         error_info.get("Message", "Unknown error"), request_id)
    data = response_obj.get("Data")
    if data is None:
        return make_error(action, "MalformedResponse",
                         "Response present but missing Data field", request_id)
    return make_success(action, {"stories": data.get("Stories", []), "total": data.get("Total", 0)}, request_id)


# ──────────────────────────────────────────────
# Merged ticket list
# ──────────────────────────────────────────────

def merge_ticket_lists(personal_tickets, org_tickets):
    """Merge two ticket lists, dedup by TicketId (stringified).

    Personal tickets take priority — duplicates from org_tickets are skipped.
    """
    seen = {}
    merged = []
    for t in personal_tickets:
        tid = str(t.get("TicketId", ""))
        if tid and tid not in seen:
            seen[tid] = True
            merged.append(t)
    for t in org_tickets:
        tid = str(t.get("TicketId", ""))
        if tid and tid not in seen:
            seen[tid] = True
            merged.append(t)
    return merged


def query_merged_ticket_list(personal_payload, org_payload):
    """Call both GetMCTicketList and DescribeOrganizationTickets, merge and dedup.

    Graceful degradation: if one API fails, return the other's results.

    Note: send_request() returns make_success(action, response_obj, request_id)
    where response_obj is the raw Response dict. We extract tickets directly
    from the response structure rather than using normalizers (which expect
    the original {"Response": {...}} envelope).
    """
    personal_result = None
    org_result = None

    # Call personal ticket API
    try:
        personal_result = send_request("GetMCTicketList", personal_payload)
    except Exception:
        personal_result = None

    # Call organization ticket API (no region)
    try:
        org_result = send_request("DescribeOrganizationTickets", org_payload)
    except Exception:
        org_result = None

    # Extract tickets from send_request results
    # GetMCTicketList: result["data"]["Data"]["Data"] = ticket list
    personal_tickets = []
    if personal_result and personal_result.get("success"):
        try:
            personal_tickets = personal_result["data"].get("Data", {}).get("Data", [])
        except (AttributeError, TypeError):
            personal_tickets = []

    # DescribeOrganizationTickets: result["data"]["Data"]["Tickets"] = ticket list
    org_tickets = []
    if org_result and org_result.get("success"):
        try:
            org_tickets = org_result["data"].get("Data", {}).get("Tickets", [])
        except (AttributeError, TypeError):
            org_tickets = []

    merged = merge_ticket_lists(personal_tickets, org_tickets)

    request_id = ""
    if personal_result:
        request_id = personal_result.get("requestId", "")
    elif org_result:
        request_id = org_result.get("requestId", "")

    return make_success("GetMCTicketList", {
        "tickets": merged,
        "total": len(merged),
    }, request_id)


# ──────────────────────────────────────────────
# HTTP transport
# ──────────────────────────────────────────────

def send_request(action: str, payload: str, region: Optional[str] = None) -> dict:
    """
    Send a signed HTTP POST to the Andon API and return a unified response.

    Args:
        action: API action name (e.g. "CreateMCTicket")
        payload: JSON-encoded request body

    Returns:
        Unified response dict via make_success or make_error.
    """
    try:
        headers = build_signed_headers(action=action, payload=payload, region=region)
    except EnvironmentError as e:
        return make_error(action, "CredentialError", str(e))

    req = urllib.request.Request(
        ENDPOINT,
        data=payload.encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err_body = json.loads(e.read().decode("utf-8"))
            response_obj = err_body.get("Response", {})
            error_info = response_obj.get("Error", {})
            return make_error(
                action,
                error_info.get("Code", "HttpError"),
                error_info.get("Message", str(e)),
                response_obj.get("RequestId", ""),
            )
        except (json.JSONDecodeError, AttributeError):
            return make_error(action, "HttpError", str(e))
    except urllib.error.URLError as e:
        return make_error(action, "NetworkError", str(e))
    except Exception as e:
        return make_error(action, "UnexpectedError", str(e))

    # Parse standard Tencent Cloud response envelope
    response_obj = body.get("Response", {})
    request_id = response_obj.get("RequestId", "")

    if "Error" in response_obj:
        error_info = response_obj["Error"]
        return make_error(
            action,
            error_info.get("Code", "UnknownError"),
            error_info.get("Message", "Unknown error"),
            request_id,
        )

    return make_success(action, response_obj, request_id)


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def _build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Andon API CLI — send requests to Tencent Cloud Andon service",
    )
    parser.add_argument(
        "-a", "--action",
        required=True,
        help="API action name (e.g. CreateMCTicket)",
    )
    parser.add_argument(
        "-d", "--data",
        required=True,
        help='JSON request body (e.g. \'{"Content":"..."}\')',
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print verbose request details",
    )
    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        help="Print request summary without sending HTTP call",
    )
    return parser


def main(argv=None):
    """CLI entry point."""
    parser = _build_cli_parser()
    args = parser.parse_args(argv)

    # Parse and validate JSON data
    try:
        data = json.loads(args.data)
    except json.JSONDecodeError as e:
        print(json.dumps(make_error(args.action, "InvalidJSON", str(e)), indent=2))
        sys.exit(1)

    # GetCurrentTime — local utility, no API call
    if args.action == "GetCurrentTime":
        result = make_success("GetCurrentTime", get_current_time(), "")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0)

    # GetMCCategoryList — category tree
    if args.action == "GetMCCategoryList":
        payload_dict = build_get_category_list_payload()
        payload_json = json.dumps(payload_dict)

        if args.verbose or args.dry_run:
            print("=" * 60)
            print(f"[DRY RUN] " if args.dry_run else "", end="")
            print(f"Request Summary")
            print("=" * 60)
            print(f"Action:   {args.action}")
            print(f"Endpoint: {ENDPOINT}")
            print(f"Version:  {API_VERSION}")
            print(f"Payload:")
            print(json.dumps(payload_dict, indent=2, ensure_ascii=False))

        if args.dry_run:
            try:
                headers = build_signed_headers(action=args.action, payload=payload_json)
                print(f"\nHeaders:")
                for k, v in sorted(headers.items()):
                    if k == "Authorization":
                        print(f"  {k}: {v[:60]}...")
                    else:
                        print(f"  {k}: {v}")
            except EnvironmentError as e:
                print(f"\n[WARN] Cannot compute headers: {e}")
            print("=" * 60)
            print("[DRY RUN] No HTTP request sent.")
            sys.exit(0)

        result = send_request(args.action, payload_json)
        # Normalize: send_request returns {success, data: Response_obj, ...}
        # We need to wrap it back into {"Response": data} for the normalizer
        if result["success"]:
            normalized = normalize_category_list_response({"Response": result["data"]})
        else:
            normalized = result

        if args.verbose:
            print(f"\nResponse:")
        print(json.dumps(normalized, indent=2, ensure_ascii=False))
        sys.exit(0 if normalized["success"] else 1)

    # GetMCCategoryListById — third-level categories by Level 2 ID
    if args.action == "GetMCCategoryListById":
        level2_id = data.get("Level2Id")
        if level2_id is None:
            print(json.dumps(make_error(args.action, "InvalidParameter",
                             "Level2Id is required"), indent=2))
            sys.exit(1)
        try:
            level2_id = int(level2_id)
        except (TypeError, ValueError):
            print(json.dumps(make_error(args.action, "InvalidParameter",
                             "Level2Id must be an integer"), indent=2))
            sys.exit(1)
        try:
            payload_dict = build_get_category_list_by_id_payload(level2_id)
        except ValueError as e:
            print(json.dumps(make_error(args.action, "InvalidParameter", str(e)), indent=2))
            sys.exit(1)

        payload_json = json.dumps(payload_dict)

        if args.verbose or args.dry_run:
            print("=" * 60)
            print(f"[DRY RUN] " if args.dry_run else "", end="")
            print(f"Request Summary")
            print("=" * 60)
            print(f"Action:   {args.action}")
            print(f"Endpoint: {ENDPOINT}")
            print(f"Version:  {API_VERSION}")
            print(f"Payload:")
            print(json.dumps(payload_dict, indent=2, ensure_ascii=False))

        if args.dry_run:
            try:
                headers = build_signed_headers(action=args.action, payload=payload_json)
                print(f"\nHeaders:")
                for k, v in sorted(headers.items()):
                    if k == "Authorization":
                        print(f"  {k}: {v[:60]}...")
                    else:
                        print(f"  {k}: {v}")
            except EnvironmentError as e:
                print(f"\n[WARN] Cannot compute headers: {e}")
            print("=" * 60)
            print("[DRY RUN] No HTTP request sent.")
            sys.exit(0)

        result = send_request(args.action, payload_json)
        if result["success"]:
            normalized = normalize_category_list_by_id_response({"Response": result["data"]})
        else:
            normalized = result

        if args.verbose:
            print(f"\nResponse:")
        print(json.dumps(normalized, indent=2, ensure_ascii=False))
        sys.exit(0 if normalized["success"] else 1)

    # Action-specific payload building
    if args.action == "GetMCTicketList":
        payload_dict = build_get_ticket_list_payload(
            status_list=data.get("StatusIdList"),
            start_time=data.get("StartTime"),
            end_time=data.get("EndTime"),
            search=data.get("Search"),
            page=data.get("Page", 1),
            page_size=data.get("PageSize", DEFAULT_TICKET_LIST_PAGE_SIZE),
            order_field=data.get("OrderField", "CreateTime"),
            order=data.get("Order", 1),
            filters=data.get("Filters"),
        )
        personal_payload_json = json.dumps(payload_dict)

        # Build org payload — auto-derive time range, default 30 days if not specified
        now = datetime.datetime.now()
        org_start = data.get("StartTime") or (now - datetime.timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        org_end = data.get("EndTime") or now.strftime("%Y-%m-%d %H:%M:%S")
        org_payload_dict = build_describe_organization_tickets_payload(
            start_time=org_start,
            end_time=org_end,
            offset=0,
            limit=50,
        )
        org_payload_json = json.dumps(org_payload_dict)

        if args.verbose or args.dry_run:
            print("=" * 60)
            print(f"[DRY RUN] " if args.dry_run else "", end="")
            print(f"Request Summary (Merged: GetMCTicketList + DescribeOrganizationTickets)")
            print("=" * 60)
            print(f"Action:   {args.action} (merged)")
            print(f"Endpoint: {ENDPOINT}")
            print(f"Version:  {API_VERSION}")
            print(f"Personal Payload:")
            print(json.dumps(payload_dict, indent=2, ensure_ascii=False))
            print(f"Organization Payload:")
            print(json.dumps(org_payload_dict, indent=2, ensure_ascii=False))

        if args.dry_run:
            try:
                headers = build_signed_headers(action="GetMCTicketList", payload=personal_payload_json)
                print(f"\nHeaders (personal):")
                for k, v in sorted(headers.items()):
                    if k == "Authorization":
                        print(f"  {k}: {v[:60]}...")
                    else:
                        print(f"  {k}: {v}")
            except EnvironmentError as e:
                print(f"\n[WARN] Cannot compute headers: {e}")
            print("=" * 60)
            print("[DRY RUN] No HTTP request sent.")
            sys.exit(0)

        # Live merged request
        result = query_merged_ticket_list(personal_payload_json, org_payload_json)

        if args.verbose:
            print(f"\nResponse:")

        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if result["success"] else 1)

    elif args.action == "DescribeOrganizationTickets":
        try:
            payload_dict = build_describe_organization_tickets_payload(
                start_time=data.get("StartTime", ""),
                end_time=data.get("EndTime", ""),
                offset=data.get("Offset", 0),
                limit=data.get("Limit", 10),
                member_uins=data.get("MemberUins"),
                title=data.get("Title"),
                statues=data.get("Statues"),
                channels=data.get("Channels"),
                tags=data.get("Tags"),
                scene_ids=data.get("SceneIds"),
                ids=data.get("Ids"),
                service_rates=data.get("ServiceRates"),
            )
        except ValueError as e:
            print(json.dumps(make_error(args.action, "InvalidParameter", str(e)), indent=2))
            sys.exit(1)

    elif args.action == "DescribeTicket":
        try:
            payload_dict = build_describe_ticket_payload(
                ticket_id=data.get("TicketId", ""),
            )
        except ValueError as e:
            print(json.dumps(make_error(args.action, "InvalidParameter", str(e)), indent=2))
            sys.exit(1)

    elif args.action == "GetMCTicketById":
        ticket_id = data.get("TicketId", "")
        try:
            payload_dict = build_get_ticket_by_id_payload(
                ticket_id=ticket_id,
                return_cos_url=data.get("ReturnCosUrl"),
                is_page=data.get("IsPage"),
                page=data.get("Page", 1),
                page_size=data.get("PageSize", "20"),
                sort=data.get("Sort", "desc"),
            )
        except ValueError as e:
            print(json.dumps(make_error(args.action, "InvalidParameter", str(e)), indent=2))
            sys.exit(1)

    elif args.action == "DescribeOrganizationStory":
        try:
            payload_dict = build_describe_organization_story_payload(
                story_id=data.get("StoryId", 0),
            )
        except ValueError as e:
            print(json.dumps(make_error(args.action, "InvalidParameter", str(e)), indent=2))
            sys.exit(1)

    elif args.action == "DescribeOrganizationStories":
        try:
            payload_dict = build_describe_organization_stories_payload(
                start_time=data.get("StartTime", ""), end_time=data.get("EndTime", ""),
                offset=data.get("Offset", 0), limit=data.get("Limit", 10),
                title=data.get("Title"), statues=data.get("Statues"),
                member_uins=data.get("MemberUins"),
                scene_ids=data.get("SceneIds"), ids=data.get("Ids"),
            )
        except ValueError as e:
            print(json.dumps(make_error(args.action, "InvalidParameter", str(e)), indent=2))
            sys.exit(1)

    elif args.action == "DescribeTicketOperation":
        try:
            payload_dict = build_describe_ticket_operation_payload(
                ticket_id=data.get("TicketId", 0),
                offset=data.get("Offset"),
                limit=data.get("Limit"),
            )
        except ValueError as e:
            print(json.dumps(make_error(args.action, "InvalidParameter", str(e)), indent=2))
            sys.exit(1)

    elif args.action == "CreateMCTicket":
        content = data.get("Content", "")
        category_id = data.get("CategoryId")
        if category_id is None:
            print(json.dumps(make_error(args.action, "InvalidParameter",
                             "CategoryId is required"), indent=2))
            sys.exit(1)
        try:
            category_id = int(category_id)
        except (TypeError, ValueError):
            print(json.dumps(make_error(args.action, "InvalidParameter",
                             "CategoryId must be an integer"), indent=2))
            sys.exit(1)
        try:
            payload_dict = build_create_ticket_payload(content, category_id)
        except ValueError as e:
            print(json.dumps(make_error(args.action, "InvalidParameter", str(e)), indent=2))
            sys.exit(1)

    elif args.action == "AddMCComment":
        ticket_id = data.get("TicketId", "")
        comment = data.get("Comment", "")
        try:
            payload_dict = build_add_comment_payload(ticket_id, comment)
        except ValueError as e:
            print(json.dumps(make_error(args.action, "InvalidParameter", str(e)), indent=2))
            sys.exit(1)

    elif args.action == "UpdateMCTicketStatus":
        ticket_id = data.get("TicketId", "")
        status = data.get("Status", 2)
        source = data.get("Source", DEFAULT_SOURCE)
        try:
            payload_dict = build_update_ticket_status_payload(ticket_id, status, source)
        except ValueError as e:
            print(json.dumps(make_error(args.action, "InvalidParameter", str(e)), indent=2))
            sys.exit(1)

    else:
        payload_dict = data

    payload_json = json.dumps(payload_dict)

    # Determine region for actions that require it
    region = None
    if args.action in ("DescribeTicket", "DescribeTicketOperation"):
        region = "ap-guangzhou"

    if args.verbose or args.dry_run:
        print("=" * 60)
        print(f"[DRY RUN] " if args.dry_run else "", end="")
        print(f"Request Summary")
        print("=" * 60)
        print(f"Action:   {args.action}")
        print(f"Endpoint: {ENDPOINT}")
        print(f"Version:  {API_VERSION}")
        print(f"Payload:")
        print(json.dumps(payload_dict, indent=2, ensure_ascii=False))

    if args.dry_run:
        # Build headers for display but don't send
        try:
            headers = build_signed_headers(
                action=args.action, payload=payload_json, region=region
            )
            print(f"\nHeaders:")
            for k, v in sorted(headers.items()):
                if k == "Authorization":
                    # Truncate auth for readability
                    print(f"  {k}: {v[:60]}...")
                else:
                    print(f"  {k}: {v}")
        except EnvironmentError as e:
            print(f"\n[WARN] Cannot compute headers: {e}")

        print("=" * 60)
        print("[DRY RUN] No HTTP request sent.")
        sys.exit(0)

    # Live request
    result = send_request(args.action, payload_json, region=region)

    # Normalize responses for actions that have custom normalizers
    if args.action == "CreateMCTicket" and result["success"]:
        result = normalize_create_ticket_response({"Response": result["data"]})
    elif args.action == "AddMCComment" and result["success"]:
        result = normalize_add_comment_response({"Response": result["data"]})
    elif args.action == "UpdateMCTicketStatus" and result["success"]:
        result = normalize_update_ticket_status_response({"Response": result["data"]})

    if args.verbose:
        print(f"\nResponse:")

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
