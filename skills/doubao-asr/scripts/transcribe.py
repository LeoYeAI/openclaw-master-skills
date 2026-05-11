#!/usr/bin/env python3
"""
Doubao (豆包) Seed-ASR 2.0 Standard — audio file transcription.

API docs: https://www.volcengine.com/docs/6561/1354868
Endpoint: https://openspeech.bytedance.com/api/v3/auc/bigmodel/
Auth: x-api-key (single API key from Volcengine Speech console)
Resource-Id: volc.seedasr.auc

Audio upload: The Doubao API requires a publicly accessible URL.
This script uploads audio to Volcengine TOS (object storage) via presigned URL,
keeping data within Volcengine infrastructure. No extra SDK needed.
"""

import argparse
import hashlib
import hmac
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime, timezone
from urllib.parse import quote, urlparse

try:
    import requests
except ImportError:
    sys.exit("requests is required: pip install requests")

SUBMIT_URL = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/submit"
QUERY_URL = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/query"
RESOURCE_ID = "volc.seedasr.auc"

FORMAT_MAP = {
    ".m4a": "m4a",
    ".mp3": "mp3",
    ".mp4": "mp4",
    ".wav": "wav",
    ".ogg": "ogg",
    ".flac": "flac",
}

MIME_MAP = {
    "m4a": "audio/mp4",
    "mp3": "audio/mpeg",
    "mp4": "audio/mp4",
    "wav": "audio/wav",
    "ogg": "audio/ogg",
    "flac": "audio/flac",
}

# --- TOS presigned URL upload (default) ---

TOS_REGION = os.environ.get("VOLCENGINE_TOS_REGION", "cn-beijing")
TOS_BUCKET = os.environ.get("VOLCENGINE_TOS_BUCKET", "")


def _tos_sign_v4(method, url, ak, sk, region, expires=3600):
    """Generate a Volcengine TOS V4 presigned URL (query-string auth)."""
    parsed = urlparse(url)
    now = datetime.now(timezone.utc)
    date_stamp = now.strftime("%Y%m%d")
    amz_date = now.strftime("%Y%m%dT%H%M%SZ")
    credential_scope = f"{date_stamp}/{region}/tos/request"
    signed_headers = "host"
    canonical_headers = f"host:{parsed.hostname}\n"

    query_params = {
        "X-Tos-Algorithm": "TOS4-HMAC-SHA256",
        "X-Tos-Credential": f"{ak}/{credential_scope}",
        "X-Tos-Date": amz_date,
        "X-Tos-Expires": str(expires),
        "X-Tos-SignedHeaders": signed_headers,
    }
    empty = ""
    canonical_qs = "&".join(
        f"{quote(k, safe=empty)}={quote(v, safe=empty)}"
        for k, v in sorted(query_params.items())
    )

    canonical_request = "\n".join([
        method,
        quote(parsed.path, safe="/"),
        canonical_qs,
        canonical_headers,
        signed_headers,
        "UNSIGNED-PAYLOAD",
    ])

    string_to_sign = "\n".join([
        "TOS4-HMAC-SHA256",
        amz_date,
        credential_scope,
        hashlib.sha256(canonical_request.encode()).hexdigest(),
    ])

    def _sign(key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    signing_key = _sign(
        _sign(_sign(_sign(sk.encode("utf-8"), date_stamp), region), "tos"),
        "request",
    )
    signature = hmac.new(
        signing_key, string_to_sign.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    return (
        f"{parsed.scheme}://{parsed.hostname}{parsed.path}"
        f"?{canonical_qs}&X-Tos-Signature={signature}"
    )


def upload_to_tos(filepath, fmt):
    """Upload audio to Volcengine TOS and return a presigned GET URL."""
    ak = os.environ.get("VOLCENGINE_ACCESS_KEY_ID", "")
    sk = os.environ.get("VOLCENGINE_SECRET_ACCESS_KEY", "")
    bucket = TOS_BUCKET

    if not ak or not sk or not bucket:
        missing = []
        if not ak:
            missing.append("VOLCENGINE_ACCESS_KEY_ID")
        if not sk:
            missing.append("VOLCENGINE_SECRET_ACCESS_KEY")
        if not bucket:
            missing.append("VOLCENGINE_TOS_BUCKET")
        sys.exit(
            f"Missing: {', '.join(missing)}\n\n"
            "The Doubao ASR API requires audio via URL. This skill uploads to\n"
            "Volcengine TOS (object storage) — your audio stays within Volcengine.\n\n"
            "Setup (3 steps):\n"
            "  1. Create IAM Access Key: https://console.volcengine.com/iam/keymanage/\n"
            "  2. Create TOS Bucket: https://console.volcengine.com/tos/bucket/create\n"
            "  3. Set env vars:\n"
            "     export VOLCENGINE_ACCESS_KEY_ID='your_ak'\n"
            "     export VOLCENGINE_SECRET_ACCESS_KEY='your_sk'\n"
            "     export VOLCENGINE_TOS_BUCKET='your_bucket_name'"
        )

    # Validate bucket/region to prevent injection
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9._-]{1,62}$', bucket):
        sys.exit(f"Invalid TOS bucket name: {bucket}")
    if not re.match(r'^[a-z0-9-]+$', TOS_REGION):
        sys.exit(f"Invalid TOS region: {TOS_REGION}")

    object_key = f"doubao-asr/{uuid.uuid4()}.{fmt}"
    # Virtual-hosted style URL: bucket.endpoint/key
    url_raw = f"https://{bucket}.tos-{TOS_REGION}.volces.com/{object_key}"
    content_type = MIME_MAP.get(fmt, "application/octet-stream")

    put_url = _tos_sign_v4("PUT", url_raw, ak, sk, TOS_REGION, expires=300)

    # Retry with exponential backoff
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with open(filepath, "rb") as f:
                resp = requests.put(
                    put_url, data=f,
                    headers={"Content-Type": content_type},
                    timeout=120,
                )
            if resp.status_code not in (200, 201):
                sys.exit(f"TOS upload failed ({resp.status_code}): {resp.text[:200]}")
            break
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
            if attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)
                print(f"  TOS upload error, retrying in {wait}s... ({attempt+1}/{max_retries})",
                      file=sys.stderr)
                time.sleep(wait)
            else:
                sys.exit(f"TOS upload failed after {max_retries} attempts: {e}")

    get_url = _tos_sign_v4("GET", url_raw, ak, sk, TOS_REGION, expires=3600)
    return get_url


def upload_audio(filepath, fmt):
    """Upload audio file and return an accessible URL."""
    print("  Uploading to Volcengine TOS...", file=sys.stderr)
    return upload_to_tos(filepath, fmt)


# --- Doubao ASR API ---

def get_headers(request_id, sequence=-1):
    api_key = os.environ.get("VOLCENGINE_API_KEY", "")
    if not api_key:
        sys.exit(
            "Missing VOLCENGINE_API_KEY\n\n"
            "Get your API key from the Volcengine Speech console:\n"
            "  https://console.volcengine.com/speech/new/\n\n"
            "Set: export VOLCENGINE_API_KEY='your_api_key'"
        )
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "X-Api-Resource-Id": RESOURCE_ID,
        "X-Api-Request-Id": request_id,
    }
    if sequence is not None:
        headers["X-Api-Sequence"] = str(sequence)
    return headers


def submit(audio_url, fmt, speakers=True):
    """Submit a transcription task. Returns request_id."""
    request_id = str(uuid.uuid4())
    headers = get_headers(request_id, sequence=-1)
    body = {
        "user": {"uid": "openclaw-doubao-asr"},
        "audio": {"url": audio_url, "format": fmt},
        "request": {
            "model_name": "bigmodel",
            "enable_itn": True,
            "enable_punc": True,
            "enable_ddc": True,
            "show_utterances": True,
            "enable_speaker_info": speakers,
        },
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            resp = requests.post(SUBMIT_URL, headers=headers, json=body, timeout=30)
            status = resp.headers.get("X-Api-Status-Code", "")
            message = resp.headers.get("X-Api-Message", "")
            if status != "20000000":
                sys.exit(f"Submit failed: {status} {message}")
            return request_id
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)
                print(f"  Submit error, retrying in {wait}s... ({attempt+1}/{max_retries})",
                      file=sys.stderr)
                time.sleep(wait)
            else:
                sys.exit(f"Submit failed after {max_retries} attempts: {e}")


def poll(request_id, timeout=600, interval=3):
    """Poll until the task completes. Returns the full result dict."""
    headers = get_headers(request_id, sequence=None)
    elapsed = 0
    net_errors = 0
    max_net_errors = 3
    while elapsed < timeout:
        try:
            resp = requests.post(QUERY_URL, headers=headers, json={}, timeout=30)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            net_errors += 1
            if net_errors >= max_net_errors:
                sys.exit(f"Poll failed after {max_net_errors} consecutive network errors: {e}")
            wait = 2 ** net_errors
            print(f"\n  Poll network error, retrying in {wait}s... ({net_errors}/{max_net_errors})",
                  file=sys.stderr)
            time.sleep(wait)
            elapsed += wait
            continue
        net_errors = 0  # reset on successful request
        status = resp.headers.get("X-Api-Status-Code", "")
        if status == "20000000":
            return resp.json()
        if status in ("20000001", "20000002"):
            print(f"\r  Transcribing... ({elapsed}s)", end="", file=sys.stderr)
            time.sleep(interval)
            elapsed += interval
            continue
        if status == "20000003":
            print("\n  Silent audio, no transcript.", file=sys.stderr)
            return {"result": {"text": "", "utterances": []}}
        message = resp.headers.get("X-Api-Message", "")
        sys.exit(f"Query failed: {status} {message}")
    sys.exit(f"Timeout after {timeout}s")


def main():
    parser = argparse.ArgumentParser(description="Doubao Seed-ASR 2.0 transcription")
    parser.add_argument("audio", help="Path to audio file (or URL)")
    parser.add_argument("--format", dest="fmt", help="Audio format (auto-detected from extension)")
    parser.add_argument("--out", help="Output file path (default: stdout)")
    parser.add_argument("--json", action="store_true", help="Output full JSON result")
    parser.add_argument("--no-speakers", action="store_true", help="Disable speaker diarization (enabled by default)")
    parser.add_argument("--timeout", type=int, default=600, help="Max wait seconds (default: 600)")
    args = parser.parse_args()

    # Support direct URL input (skip upload)
    if args.audio.startswith("http://") or args.audio.startswith("https://"):
        audio_url = args.audio
        fmt = args.fmt
        if not fmt:
            ext = os.path.splitext(urlparse(audio_url).path)[1].lower()
            fmt = FORMAT_MAP.get(ext)
        if not fmt:
            sys.exit("Cannot detect format from URL. Use --format to specify.")
    else:
        if not os.path.isfile(args.audio):
            sys.exit(f"File not found: {args.audio}")
        ext = os.path.splitext(args.audio)[1].lower()
        fmt = args.fmt or FORMAT_MAP.get(ext)
        if not fmt:
            sys.exit(f"Unknown audio format: {ext}. Use --format to specify.")
        audio_url = upload_audio(args.audio, fmt)

    # Submit task
    print("  Submitting transcription task...", file=sys.stderr)
    request_id = submit(audio_url, fmt, speakers=not args.no_speakers)

    # Poll for result
    data = poll(request_id, timeout=args.timeout)
    print("", file=sys.stderr)  # newline after progress

    result = data.get("result", {})
    utterances = result.get("utterances", [])

    # Output
    if args.json:
        output = json.dumps(data, ensure_ascii=False, indent=2)
    elif utterances and any(
        u.get("speaker") is not None or u.get("additions", {}).get("speaker") is not None
        for u in utterances
    ):
        # Format with speaker labels
        lines = []
        prev_speaker = None
        for u in utterances:
            speaker = u.get("speaker") or u.get("additions", {}).get("speaker")
            text = u.get("text", "").strip()
            if not text:
                continue
            if speaker != prev_speaker:
                label = f"Speaker {speaker}" if speaker is not None else "Speaker ?"
                lines.append(f"\n{label}:")
                prev_speaker = speaker
            lines.append(text)
        output = "\n".join(lines).strip()
    else:
        output = result.get("text", "")

    if args.out:
        out_path = os.path.realpath(args.out)
        # Block writes outside /tmp and current working directory
        cwd = os.path.realpath(os.getcwd())
        tmp = os.path.realpath("/tmp")
        if not (out_path.startswith(cwd + os.sep) or out_path.startswith(tmp + os.sep)):
            sys.exit(f"Output path not allowed (must be under working directory or /tmp): {args.out}")
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(output)
        print(args.out)
    else:
        print(output)


if __name__ == "__main__":
    main()
