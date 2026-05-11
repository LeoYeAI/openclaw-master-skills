#!/usr/bin/env python3
"""evaluate-upgrade.py — Telnyx professional upgrade evaluation via GitHub or LinkedIn.

Supports two verification methods:
  --github-token <token>  Submit GitHub token directly (automated, no browser)
  --linkedin              Start LinkedIn OAuth flow (requires browser)

Polls for results, caches the outcome, and outputs structured JSON.

Also supports --poll-only to re-check an existing evaluation by ID
(used by cron jobs for PASS_TO_HUMAN follow-up).

Uses Python stdlib only (no third-party dependencies).

Usage:
    # GitHub: submit token + poll:
    python3 evaluate-upgrade.py --github-token <token> --api-key <telnyx_api_key>

    # LinkedIn: start OAuth flow + poll:
    python3 evaluate-upgrade.py --linkedin --api-key <telnyx_api_key>

    # Poll-only (re-check existing evaluation):
    python3 evaluate-upgrade.py --poll-only --evaluation-id <id> --api-key <telnyx_api_key>
"""

import argparse
import json
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request

DEFAULT_API_BASE = "https://api.telnyx.com"
DEFAULT_TIMEOUT = 120
DEFAULT_POLL_INTERVAL = 5
CACHE_PATH = Path.home() / ".telnyx" / "upgrade.json"
TELNYX_CONFIG_PATH = Path.home() / ".config" / "telnyx" / "config.json"
MAX_RETRIES = 3
RETRY_BACKOFF = [1, 2, 4]


def resolve_api_key(cli_value):
    """Resolve Telnyx API key: CLI arg > env var > ~/.config/telnyx/config.json."""
    if cli_value:
        return cli_value
    env_key = os.environ.get("TELNYX_API_KEY")
    if env_key:
        return env_key
    if TELNYX_CONFIG_PATH.exists():
        try:
            with open(TELNYX_CONFIG_PATH) as f:
                config = json.load(f)
            key = config.get("api_key", "")
            if key:
                return key
        except (json.JSONDecodeError, OSError):
            pass
    return None


def make_request(url, method="GET", data=None, headers=None, timeout=30):
    """Make an HTTP request using urllib. Returns (status_code, response_dict)."""
    if headers is None:
        headers = {}

    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(
        url, data=body, headers=headers, method=method
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp_body = resp.read().decode("utf-8")
            return resp.status, json.loads(resp_body) if resp_body else {}
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8") if e.fp else ""
        try:
            resp_data = json.loads(resp_body) if resp_body else {}
        except json.JSONDecodeError:
            resp_data = {"detail": resp_body}
        return e.code, resp_data
    except urllib.error.URLError as e:
        return 0, {"detail": str(e.reason)}


def make_request_with_retry(
    url, method="GET", data=None, headers=None, timeout=30
):
    """Make an HTTP request with retry and exponential backoff."""
    last_status = 0
    last_resp = {}

    for attempt in range(MAX_RETRIES):
        status, resp = make_request(url, method, data, headers, timeout)

        # Success or client error (don't retry 4xx)
        if 200 <= status < 500:
            return status, resp

        last_status = status
        last_resp = resp

        if attempt < MAX_RETRIES - 1:
            backoff = (
                RETRY_BACKOFF[attempt] if attempt < len(RETRY_BACKOFF) else 4
            )
            time.sleep(backoff)

    return last_status, last_resp


def submit_evaluation(api_base, api_key, github_token):
    """Submit GitHub token for evaluation. Returns (success, data)."""
    url = f"{api_base}/v2/account/upgrade/github"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }
    data = {"github_token": github_token}

    status, resp = make_request_with_retry(
        url, method="POST", data=data, headers=headers
    )

    if status == 201:
        return True, resp
    else:
        return False, {
            "status_code": status,
            "detail": resp.get("detail", resp.get("message", str(resp))),
        }


def submit_linkedin_evaluation(api_base, api_key):
    """Start LinkedIn OAuth flow for evaluation. Returns (success, data)."""
    url = f"{api_base}/v2/account/upgrade/linkedin"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    status, resp = make_request_with_retry(
        url, method="POST", headers=headers
    )

    if status == 200:
        return True, resp
    else:
        return False, {
            "status_code": status,
            "detail": resp.get("detail", resp.get("message", str(resp))),
        }


def poll_latest_evaluation(
    api_base, api_key, user_id, timeout, poll_interval
):
    """Poll latest evaluation for a user until a linkedin_oauth evaluation appears.

    Returns (evaluation_id, status_resp) or (None, error_resp) on timeout.
    """
    url = f"{api_base}/v2/account/user/{user_id}/latest-upgrade-request"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    start = time.time()

    while time.time() - start < timeout:
        status, resp = make_request(url, headers=headers)

        if status == 200 and resp:
            # Check if this is a linkedin_oauth evaluation that's being processed
            used_methods = resp.get("used_methods", [])
            eval_status = resp.get("status", "")
            evaluation_id = resp.get("evaluation_id")
            if (
                evaluation_id
                and "linkedin_oauth" in used_methods
                and eval_status in ("pending", "processing", "completed", "failed")
            ):
                return evaluation_id, resp

        time.sleep(poll_interval)

    return None, {"status": "polling_timeout"}


def poll_status(api_base, api_key, evaluation_id, timeout, poll_interval):
    """Poll for evaluation status. Returns the final status response."""
    url = f"{api_base}/v2/account/upgrade-request-status/{evaluation_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    start = time.time()

    while time.time() - start < timeout:
        status, resp = make_request(url, headers=headers)

        if status != 200:
            # Transient error — keep polling
            time.sleep(poll_interval)
            continue

        eval_status = resp.get("status", "")

        if eval_status in ("completed", "failed"):
            return resp

        time.sleep(poll_interval)

    # Timed out
    return {
        "status": "polling_timeout",
        "request_id": evaluation_id,
    }


def save_cache(data):
    """Save evaluation result to local cache."""
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def build_output(evaluation_id, status_resp):
    """Build the structured output from a status response."""
    status = status_resp.get("status", "unknown")
    decision = status_resp.get("decision")
    used_methods = status_resp.get("used_methods", [])

    # Build contextual message and next_steps
    if status == "completed" and decision == "APPROVED":
        message = "Professional upgrade approved. Account upgraded to professional tier."
        next_steps = "Retry the blocked operation. You may need to refresh your API key."
    elif status == "completed" and decision == "REJECTED":
        message = "Professional upgrade not approved."
        github_used = "github_oauth" in used_methods
        linkedin_used = "linkedin_oauth" in used_methods
        if github_used and not linkedin_used:
            next_steps = (
                "Try LinkedIn verification: "
                "python3 evaluate-upgrade.py --linkedin"
            )
        elif linkedin_used and not github_used:
            next_steps = (
                "Try GitHub verification: "
                "python3 evaluate-upgrade.py --github-token <TOKEN>"
            )
        elif github_used and linkedin_used:
            next_steps = (
                "All verification methods have been used. "
                "Contact support at https://support.telnyx.com"
            )
        else:
            next_steps = (
                "Try GitHub verification or LinkedIn verification."
            )
    elif status == "completed" and decision == "PASS_TO_HUMAN":
        message = "Upgrade application is under manual review."
        next_steps = "A support ticket has been created. Check back later."
    elif status == "failed":
        message = "Evaluation failed due to an error."
        next_steps = (
            "This may be temporary. Try again later or contact support."
        )
    elif status == "polling_timeout":
        message = (
            "Evaluation is still processing. Timed out waiting for result."
        )
        next_steps = (
            "The evaluation is still running server-side. Check back later."
        )
    else:
        message = f"Evaluation status: {status}"
        next_steps = "Continue polling for updates."

    return {
        "evaluation_id": evaluation_id,
        "status": status,
        "decision": decision,
        "used_methods": used_methods,
        "message": message,
        "next_steps": next_steps,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Telnyx professional upgrade evaluation via GitHub or LinkedIn"
    )
    method_group = parser.add_mutually_exclusive_group()
    method_group.add_argument(
        "--github-token",
        help="GitHub OAuth access token (submit directly)",
    )
    method_group.add_argument(
        "--linkedin",
        action="store_true",
        help="Start LinkedIn OAuth flow (requires browser)",
    )
    method_group.add_argument(
        "--poll-only",
        action="store_true",
        help="Skip submission, only poll an existing evaluation",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Telnyx API key (also reads TELNYX_API_KEY env or ~/.config/telnyx/config.json)",
    )
    parser.add_argument(
        "--api-base",
        default=os.environ.get("TELNYX_API_BASE", DEFAULT_API_BASE),
        help=f"Telnyx API base URL (default: {DEFAULT_API_BASE})",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=int(os.environ.get("UPGRADE_POLL_TIMEOUT", DEFAULT_TIMEOUT)),
        help=f"Max seconds to wait for evaluation (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=int(
            os.environ.get("UPGRADE_POLL_INTERVAL", DEFAULT_POLL_INTERVAL)
        ),
        help=f"Seconds between status polls (default: {DEFAULT_POLL_INTERVAL})",
    )
    parser.add_argument(
        "--evaluation-id",
        help="Evaluation ID to poll (required with --poll-only)",
    )
    parser.add_argument(
        "--user-id",
        help="Telnyx user ID (for LinkedIn flow polling; normally returned by endpoint)",
    )
    args = parser.parse_args()

    # Resolve API key from CLI arg, env var, or config file
    api_key = resolve_api_key(args.api_key)
    if not api_key:
        output = {
            "evaluation_id": None,
            "status": "failed",
            "decision": None,
            "used_methods": [],
            "message": "No Telnyx API key found. Set TELNYX_API_KEY env var, pass --api-key, or run 'telnyx auth setup'.",
            "next_steps": "Configure a Telnyx API key.",
        }
        print(json.dumps(output, indent=2))
        sys.exit(1)
    args.api_key = api_key

    # Poll-only mode: skip submission, just check status
    if args.poll_only:
        evaluation_id = args.evaluation_id
        if not evaluation_id:
            # Try reading from cache
            if CACHE_PATH.exists():
                with open(CACHE_PATH) as f:
                    cached = json.load(f)
                evaluation_id = cached.get("evaluation_id")
            if not evaluation_id:
                output = {
                    "evaluation_id": None,
                    "status": "failed",
                    "decision": None,
                    "used_methods": [],
                    "message": "No evaluation_id provided and none found in cache.",
                    "next_steps": "Submit a new evaluation or provide --evaluation-id.",
                }
                print(json.dumps(output, indent=2))
                sys.exit(1)

        # Single status check (no long polling loop)
        url = f"{args.api_base}/v2/account/upgrade-request-status/{evaluation_id}"
        headers = {
            "Authorization": f"Bearer {args.api_key}",
            "Accept": "application/json",
        }
        status_code, status_resp = make_request_with_retry(
            url, headers=headers
        )

        if status_code != 200:
            output = {
                "evaluation_id": evaluation_id,
                "status": "failed",
                "decision": None,
                "used_methods": [],
                "message": f"Status check failed ({status_code}): {status_resp.get('detail', '')}",
                "next_steps": "Retry later.",
            }
            print(json.dumps(output, indent=2))
            sys.exit(1)

        output = build_output(evaluation_id, status_resp)
        if output["status"] != "failed":
            cache_data = {
                "evaluation_id": evaluation_id,
                "status": output["status"],
                "decision": output["decision"],
                "used_methods": output["used_methods"],
                "timestamp": time.strftime(
                    "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                ),
            }
            save_cache(cache_data)

        print(json.dumps(output, indent=2))
        sys.exit(0 if output.get("decision") == "APPROVED" else 1)

    # LinkedIn flow: start OAuth → present URL → poll for evaluation
    if args.linkedin:
        # Step 1: Start LinkedIn OAuth flow
        success, submit_resp = submit_linkedin_evaluation(
            args.api_base, args.api_key
        )

        if not success:
            status_code = submit_resp.get("status_code", 0)
            detail = submit_resp.get("detail", "Unknown error")
            output = {
                "evaluation_id": None,
                "status": "failed",
                "decision": None,
                "used_methods": [],
                "message": f"LinkedIn submission failed ({status_code}): {detail}",
                "next_steps": "Check your API key, then try again.",
            }
            print(json.dumps(output, indent=2))
            sys.exit(1)

        authorization_url = submit_resp.get("authorization_url", "")
        user_id = args.user_id or submit_resp.get("user_id", "")

        if not authorization_url:
            output = {
                "evaluation_id": None,
                "status": "failed",
                "decision": None,
                "used_methods": [],
                "message": "No authorization URL returned.",
                "next_steps": "Contact support.",
            }
            print(json.dumps(output, indent=2))
            sys.exit(1)

        # Step 2: Output the URL for the bot to present to the user (stderr
        # to keep stdout reserved for the single final JSON result)
        url_output = {
            "action": "open_url",
            "url": authorization_url,
            "message": submit_resp.get("message", "Open this URL to verify with LinkedIn."),
        }
        print(json.dumps(url_output, indent=2), file=sys.stderr)

        if not user_id:
            output = {
                "evaluation_id": None,
                "status": "failed",
                "decision": None,
                "used_methods": [],
                "message": "No user_id available for polling. Pass --user-id.",
                "next_steps": "Provide --user-id and try again.",
            }
            print(json.dumps(output, indent=2))
            sys.exit(1)

        # Step 3: Poll for the linkedin_oauth evaluation to appear
        poll_start = time.time()
        evaluation_id, latest_resp = poll_latest_evaluation(
            args.api_base,
            args.api_key,
            user_id,
            args.timeout,
            args.poll_interval,
        )

        if not evaluation_id:
            output = {
                "evaluation_id": None,
                "status": "polling_timeout",
                "decision": None,
                "used_methods": [],
                "message": (
                    "Timed out waiting for LinkedIn verification to complete. "
                    "The user may not have opened the URL yet."
                ),
                "next_steps": (
                    "The authorization URL is still valid for 10 minutes. "
                    "Once the user completes OAuth, re-run with --poll-only."
                ),
            }
            print(json.dumps(output, indent=2))
            sys.exit(1)

        # Step 4: If evaluation already completed, use that; otherwise poll status
        # Deduct time spent waiting for the evaluation to appear
        elapsed = time.time() - poll_start
        remaining_timeout = max(10, args.timeout - int(elapsed))
        eval_status = latest_resp.get("status", "")
        if eval_status in ("completed", "failed"):
            status_resp = latest_resp
        else:
            status_resp = poll_status(
                args.api_base,
                args.api_key,
                evaluation_id,
                remaining_timeout,
                args.poll_interval,
            )

        # Step 5: Build output, cache, print
        output = build_output(evaluation_id, status_resp)

        if output["status"] != "failed":
            cache_data = {
                "evaluation_id": evaluation_id,
                "status": output["status"],
                "decision": output["decision"],
                "used_methods": output["used_methods"],
                "timestamp": time.strftime(
                    "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                ),
            }
            save_cache(cache_data)

        print(json.dumps(output, indent=2))
        sys.exit(0 if output.get("decision") == "APPROVED" else 1)

    # GitHub flow: submit token + poll
    if not args.github_token:
        parser.error(
            "one of --github-token, --linkedin, or --poll-only is required"
        )

    # Step 1: Submit evaluation
    success, submit_resp = submit_evaluation(
        args.api_base, args.api_key, args.github_token
    )

    if not success:
        status_code = submit_resp.get("status_code", 0)
        detail = submit_resp.get("detail", "Unknown error")
        output = {
            "evaluation_id": None,
            "status": "failed",
            "decision": None,
            "used_methods": [],
            "message": f"Submission failed ({status_code}): {detail}",
            "next_steps": "Check your API key and GitHub token, then try again.",
        }
        print(json.dumps(output, indent=2))
        sys.exit(1)

    evaluation_id = submit_resp.get("evaluation_id", "")
    if not evaluation_id:
        output = {
            "evaluation_id": None,
            "status": "failed",
            "decision": None,
            "used_methods": [],
            "message": "Submission succeeded but no evaluation_id returned.",
            "next_steps": "Contact support.",
        }
        print(json.dumps(output, indent=2))
        sys.exit(1)

    # Step 2: Poll for result
    status_resp = poll_status(
        args.api_base,
        args.api_key,
        evaluation_id,
        args.timeout,
        args.poll_interval,
    )

    # Step 3: Build output
    output = build_output(evaluation_id, status_resp)

    # Step 4: Cache result (skip caching failures to allow retry)
    if output["status"] != "failed":
        cache_data = {
            "evaluation_id": evaluation_id,
            "status": output["status"],
            "decision": output["decision"],
            "used_methods": output["used_methods"],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        save_cache(cache_data)

    # Step 5: Output result
    print(json.dumps(output, indent=2))

    # Exit with non-zero if not approved
    if output.get("decision") != "APPROVED":
        sys.exit(1)


if __name__ == "__main__":
    main()
