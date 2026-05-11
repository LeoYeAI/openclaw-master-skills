"""Reusable HTTP client for the Topview API with auth and task polling."""

import sys
import time
from typing import Any, Optional

import requests

from .config import load_config

BASE_URL = "https://api.topview.ai"

RESPONSE_CODES = {
    "200": "Success",
    "401": "Unauthorized, need to login again",
    "4000": "Request parameter error",
    "4001": "Request data format does not match",
    "4002": "Request digital signature does not match",
    "4003": "Required parameter cannot be null",
    "4004": "Resource not found",
    "4005": "Name duplicated",
    "4006": "Request refuse",
    "4007": "Exists unfinished task, please wait",
    "4100": "Credit not enough",
    "5000": "Internal server error, please report at https://www.topview.ai with task type and taskId (e.g. 'avatar4 task failed, taskId: abc123')",
    "5001": "Feign invoke error",
    "5003": "Server is busy, please try again later",
    "5004": "I/O error occurred",
    "5005": "Unknown error occurred",
    "6001": "Security problem detect",
}


class TopviewError(Exception):
    """Raised when the Topview API returns a non-200 response code."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


class TopviewClient:
    """Authenticated HTTP client for Topview API endpoints.

    Usage::

        client = TopviewClient()
        resp = client.post("/v1/photo_avatar/task/submit", json={...})
        result = client.poll_task("/v1/photo_avatar/task/query", task_id)
    """

    def __init__(self, uid: Optional[str] = None, api_key: Optional[str] = None):
        if uid and api_key:
            self._uid = uid
            self._api_key = api_key
        else:
            cfg = load_config()
            self._uid = cfg["uid"]
            self._api_key = cfg["api_key"]

    @property
    def headers(self) -> dict:
        return {
            "Topview-Uid": self._uid,
            "Authorization": f"Bearer {self._api_key}",
        }

    def _check(self, data: dict) -> dict:
        code = str(data.get("code", ""))
        if code != "200":
            msg = data.get("message", RESPONSE_CODES.get(code, "Unknown error") + f", response: {data}")
            raise TopviewError(code, msg)
        return data.get("result", data)

    def get(self, path: str, params: Optional[dict] = None, **kwargs) -> dict:
        url = f"{BASE_URL}{path}" if path.startswith("/") else path
        resp = requests.get(url, headers=self.headers, params=params, **kwargs)
        resp.raise_for_status()
        return self._check(resp.json())

    def post(self, path: str, json: Optional[dict] = None, **kwargs) -> dict:
        url = f"{BASE_URL}{path}" if path.startswith("/") else path
        print(f"post url: {url}")
        resp = requests.post(url, headers=self.headers, json=json, **kwargs)
        print(f"post resp: {resp.text}")
        resp.raise_for_status()
        return self._check(resp.json())

    def put(self, path: str, json: Optional[dict] = None, **kwargs) -> dict:
        url = f"{BASE_URL}{path}" if path.startswith("/") else path
        resp = requests.put(url, headers=self.headers, json=json, **kwargs)
        resp.raise_for_status()
        return self._check(resp.json())

    def delete(self, path: str, params: Optional[dict] = None, **kwargs) -> dict:
        url = f"{BASE_URL}{path}" if path.startswith("/") else path
        resp = requests.delete(url, headers=self.headers, params=params, **kwargs)
        resp.raise_for_status()
        return self._check(resp.json())

    def put_file(self, upload_url: str, file_path: str) -> None:
        """PUT a local file to a pre-signed S3 URL (no auth headers)."""
        with open(file_path, "rb") as f:
            resp = requests.put(upload_url, data=f)
        resp.raise_for_status()

    def poll_task(
        self,
        path: str,
        task_id: str,
        *,
        interval: float = 5.0,
        timeout: float = 600.0,
        verbose: bool = True,
    ) -> dict:
        """Poll a task endpoint until status is 'success' or 'failed'.

        Returns the result dict on success; raises TopviewError on failure.
        """
        start = time.time()
        while True:
            elapsed = time.time() - start
            if elapsed > timeout:
                raise TimeoutError(
                    f"Task {task_id} did not complete within {timeout}s"
                )

            result = self.get(path, params={"taskId": task_id})
            status = result.get("status", "")

            if verbose:
                print(
                    f"  [{elapsed:.0f}s] status: {status}",
                    file=sys.stderr,
                )

            if status == "success":
                return result
            if status in ("failed", "fail"):
                raise TopviewError("TASK_FAILED", result.get("errorMsg", "Task failed"))

            time.sleep(interval)
