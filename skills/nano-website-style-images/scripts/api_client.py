"""NANO-BANANA API client for async image generation."""

import base64
import logging
import os
import time
from dataclasses import dataclass

import requests

logger = logging.getLogger(__name__)


@dataclass
class TaskResult:
    task_id: str
    status: str
    image_url: str | None


class NanoBananaClient:
    """Client for the NANO-BANANA async image generation API."""

    PENDING_STATUSES = {"SUBMITTED", "SUBMITED", "RUNNING"}
    SUCCESS_STATUS = "FINISHED"
    FAILED_STATUS = "FAILED"

    def __init__(self, config: dict):
        api_cfg = config["api"]
        self.submit_url = api_cfg["submit_url"]
        self.status_url_template = api_cfg["status_url"]
        self.headers = {k: v for k, v in api_cfg["headers"].items()}
        self.headers["Content-Type"] = "application/json"
        self.model = api_cfg["model"]
        self.poll_interval = api_cfg.get("poll_interval_seconds", 5)
        self.max_poll_attempts = api_cfg.get("max_poll_attempts", 120)

    def submit(self, prompt: str, reference_image_url: str | None = None) -> str:
        """Submit an image generation task. Returns task_id."""
        parts = [{"text": prompt}]
        if reference_image_url:
            if os.path.isfile(reference_image_url):
                with open(reference_image_url, "rb") as img_file:
                    b64_data = base64.b64encode(img_file.read()).decode("utf-8")
                mime = "image/png" if reference_image_url.lower().endswith(".png") else "image/jpeg"
                parts.append({"inlineData": {"mimeType": mime, "data": b64_data}})
                logger.info("Using local reference image: %s (base64, %s)", reference_image_url, mime)
            else:
                parts.append({"inlineData": {"data": reference_image_url}})

        payload = {
            "model": self.model,
            "contents": [{"parts": parts}],
        }

        logger.debug("Submitting task with prompt: %s...", prompt[:80])
        resp = requests.post(self.submit_url, json=payload, headers=self.headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status_code") != 0:
            raise RuntimeError(f"Submit failed: {data.get('error_message') or data.get('status_msg')}")

        task_id = data["data"]["result"]
        logger.info("Task submitted: %s", task_id)
        return task_id

    def poll(self, task_id: str) -> TaskResult:
        """Poll for task completion. Blocks until finished or failed."""
        status_url = self.status_url_template.format(task_id=task_id)
        get_headers = {k: v for k, v in self.headers.items() if k != "Content-Type"}

        interval = self.poll_interval
        for attempt in range(1, self.max_poll_attempts + 1):
            resp = requests.get(status_url, headers=get_headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            status = data["data"]["status"]
            logger.debug("Poll #%d for %s: status=%s", attempt, task_id, status)

            if status == self.SUCCESS_STATUS:
                image_url = data["data"]["result"]
                logger.info("Task %s finished: %s", task_id, image_url)
                return TaskResult(task_id=task_id, status=status, image_url=image_url)

            if status == self.FAILED_STATUS:
                logger.error("Task %s failed", task_id)
                return TaskResult(task_id=task_id, status=status, image_url=None)

            if status not in self.PENDING_STATUSES:
                logger.warning("Unknown status '%s' for task %s, treating as pending", status, task_id)

            time.sleep(interval)
            interval = min(interval * 1.2, 15)

        logger.error("Task %s timed out after %d attempts", task_id, self.max_poll_attempts)
        return TaskResult(task_id=task_id, status="TIMEOUT", image_url=None)

    def submit_and_wait(self, prompt: str, reference_image_url: str | None = None,
                        max_retries: int = 3) -> TaskResult:
        """Submit a task and wait for completion, with retry on failure."""
        result = None
        for attempt in range(1, max_retries + 1):
            task_id = self.submit(prompt, reference_image_url)
            result = self.poll(task_id)
            if result.status == self.SUCCESS_STATUS:
                return result
            if attempt < max_retries:
                wait = 2 ** attempt
                logger.warning("Attempt %d/%d failed (status: %s), retrying in %ds...",
                               attempt, max_retries, result.status, wait)
                time.sleep(wait)
            else:
                logger.error("All %d attempts failed for task", max_retries)
        return result

    def download_image(self, image_url: str, output_path: str) -> str:
        """Download an image from URL to local path."""
        logger.info("Downloading image to %s", output_path)
        resp = requests.get(image_url, timeout=60)
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(resp.content)
        return output_path
