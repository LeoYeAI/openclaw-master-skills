# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd. and/or its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import hashlib
import hmac
import json
import os
import sys
from typing import Any, Dict, Optional, Generator
from urllib.parse import quote
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))  # 添加父目录

import requests

from scripts.client.tmp_file_manager import clean_tmp_dir
from scripts.config import load_emr_skill_config

skill_cfg = load_emr_skill_config()

class StreamResponseEvent:
    def __init__(self, response_header: Dict[str, Any], event_data: str):
        self.response_header = response_header
        self.event_data = event_data

    def get_response_header(self):
        return self.response_header

    def get_event_data(self):
        return self.event_data


def norm_query(params: Dict[str, Any]) -> str:
    items = []
    for key in sorted(params.keys()):
        value = params[key]
        if value is None:
            continue
        if isinstance(value, list):
            for v in value:
                if v is None:
                    continue
                items.append((key, v))
        else:
            items.append((key, value))
    return "&".join(
        f"{quote(str(k), safe='-_.~')}={quote(str(v), safe='-_.~')}" for k, v in items
    ).replace("+", "%20")


def hmac_sha256(key: bytes, content: str) -> bytes:
    return hmac.new(key, content.encode("utf-8"), hashlib.sha256).digest()


def hash_sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def utc_now():
    try:
        from datetime import timezone
        return datetime.datetime.now(timezone.utc)
    except ImportError:
        class UTC(datetime.tzinfo):
            def utcoffset(self, dt):
                return datetime.timedelta(0)

            def tzname(self, dt):
                return "UTC"

            def dst(self, dt):
                return datetime.timedelta(0)

        return datetime.datetime.now(UTC())


def request(
        service: str,
        action: str,
        version: str,
        region: str,
        endpoint: str,
        method: str = "POST",
        query: Optional[Dict[str, Any]] = None,
        body: Any = None,
        timeout = 30,
        headers=None,
):
    headers = headers or {}
    clean_tmp_dir(hours=6)
    body_text, method_u, request_query = _sign(action, body, endpoint, headers, method, query, region, service, version)

    r = requests.request(
        method=method_u,
        url=f"https://{endpoint}",
        headers=headers,
        params=request_query,
        data=body_text,
        timeout = timeout
    )
    try:
        return r.json()
    except Exception as e:
        return r.text

def stream_request(
        service: str,
        action: str,
        version: str,
        region: str,
        endpoint: str,
        method: str = "POST",
        query: Optional[Dict[str, Any]] = None,
        body: Any = None,
        timeout = 30,
        headers=None,
) -> Generator[StreamResponseEvent, None, None]:
    headers = headers or {}
    headers.setdefault("Accept", "text/event-stream")
    clean_tmp_dir(hours=6)
    body_text, method_u, request_query = _sign(action, body, endpoint, headers, method, query, region, service, version)


    with requests.request(
        method=method_u,
        url=f"https://{endpoint}",
        headers=headers,
        params=request_query,
        data=body_text,
        timeout = timeout,
        stream = True,
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines(decode_unicode=True):
            if line is None:  # 可能为保持连接而发送的空行
                continue

            line = line.strip()
            if not line:  # 空行表示事件结束
                continue
            yield StreamResponseEvent(dict(response.headers), line)

def _sign(action, body, endpoint, headers, method, query, region, service, version):
    ak = skill_cfg.access_key
    sk = skill_cfg.secret_key
    if region is None or region == "":
        region = skill_cfg.region
    date = utc_now()
    method_u = method.upper()
    content_type = "application/json"
    user_query = {k: v for k, v in (query or {}).items() if v is not None}
    request_query: Dict[str, Any] = {"Action": action, "Version": version, **user_query}
    if body is None or method_u == "GET":
        body_text = ""
    elif isinstance(body, str):
        body_text = body
    else:
        body_text = json.dumps(body, separators=(",", ":"), sort_keys=True)
    x_date = date.strftime("%Y%m%dT%H%M%SZ")
    short_x_date = x_date[:8]
    payload_hash = hash_sha256(body_text)
    signed_headers_str = "content-type;host;x-content-sha256;x-date"
    canonical_headers = "\n".join(
        [
            f"content-type:{content_type}",
            f"host:{endpoint}",
            f"x-content-sha256:{payload_hash}",
            f"x-date:{x_date}",
            "",
        ]
    )
    canonical_request_str = "\n".join(
        [
            method_u,
            "/",
            norm_query(request_query),
            canonical_headers,
            signed_headers_str,
            payload_hash,
        ]
    )
    hashed_canonical_request = hash_sha256(canonical_request_str)
    credential_scope = "/".join([short_x_date, region, service, "request"])
    string_to_sign = "\n".join(["HMAC-SHA256", x_date, credential_scope, hashed_canonical_request])
    k_date = hmac_sha256(sk.encode("utf-8"), short_x_date)
    k_region = hmac_sha256(k_date, region)
    k_service = hmac_sha256(k_region, service)
    k_signing = hmac_sha256(k_service, "request")
    signature = hmac_sha256(k_signing, string_to_sign).hex()
    authorization = (
        f"HMAC-SHA256 Credential={ak}/{credential_scope}, SignedHeaders={signed_headers_str}, Signature={signature}"
    )
    headers.update({
        "Host": endpoint,
        "Content-Type": content_type,
        "X-Date": x_date,
        "X-Content-Sha256": payload_hash,
        "Authorization": authorization,
    })
    return body_text, method_u, request_query
