"""
MiniMax Voice API - Asynchronous TTS Module
Provides async task-based text-to-speech synthesis for long-form content.

Workflow:
  1. create_async_tts_task() — submit text for synthesis
  2. query_async_tts_task()  — poll task status
  3. Download the result audio when ready

Docs: https://platform.minimaxi.com/document/T2A%20Async
"""

import time
from typing import Optional, Dict, Any, List, Union
from enum import Enum

try:
    from .utils import (
        VoiceSetting,
        AudioSetting,
        make_request,
        parse_response,
        download_audio_from_url,
    )
except ImportError:
    from utils import (
        VoiceSetting,
        AudioSetting,
        make_request,
        parse_response,
        download_audio_from_url,
    )


class AsyncTaskStatus(Enum):
    """Status values returned by the async TTS task query endpoint."""
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    EXPIRED = "expired"


def create_async_tts_task(
    model: str = "speech-2.6-hd",
    text: Optional[str] = None,
    text_file_id: Optional[str] = None,
    voice_setting: Optional[VoiceSetting] = None,
    audio_setting: Optional[AudioSetting] = None,
    pronunciation_dict: Optional[Dict[str, Any]] = None,
    timber_weights: Optional[List[Dict[str, Any]]] = None,
    language_boost: Optional[str] = None,
    voice_modify: Optional[Dict[str, Any]] = None,
    subtitle_enable: bool = False,
    aigc_watermark: bool = False,
    timeout: int = 60,
) -> Dict[str, Any]:
    """
    Create an asynchronous TTS task.

    Either ``text`` or ``text_file_id`` must be provided. For very long
    texts, upload the text file first and pass the file ID.

    Args:
        model: TTS model name.
        text: Text to synthesize (mutually exclusive with text_file_id).
        text_file_id: Uploaded text file ID (mutually exclusive with text).
        voice_setting: Voice configuration.
        audio_setting: Audio output configuration.
        pronunciation_dict: Custom pronunciation dictionary.
        timber_weights: Timber weight configuration for voice mixing.
        language_boost: Language to boost for multilingual synthesis.
        voice_modify: Voice modification parameters.
        subtitle_enable: Whether to return subtitle/timing data.
        aigc_watermark: Whether to embed AIGC watermark.
        timeout: Request timeout in seconds.

    Returns:
        Parsed API response containing task_id.

    Raises:
        ValueError: If neither text nor text_file_id is provided, or API error.
    """
    if text is None and text_file_id is None:
        raise ValueError("Either 'text' or 'text_file_id' must be provided")

    if voice_setting is None:
        voice_setting = VoiceSetting(voice_id="male-qn-qingse")

    if audio_setting is None:
        audio_setting = AudioSetting()

    payload: Dict[str, Any] = {
        "model": model,
        "voice_setting": voice_setting.to_dict(),
        "audio_setting": audio_setting.to_dict(),
        "subtitle_enable": subtitle_enable,
        "aigc_watermark": aigc_watermark,
    }

    if text is not None:
        payload["text"] = text

    if text_file_id is not None:
        payload["text_file_id"] = text_file_id

    if pronunciation_dict is not None:
        payload["pronunciation_dict"] = pronunciation_dict

    if timber_weights is not None:
        payload["timber_weights"] = timber_weights

    if language_boost is not None:
        payload["language_boost"] = language_boost

    if voice_modify is not None:
        payload["voice_modify"] = voice_modify

    response = make_request(
        method="POST",
        endpoint="t2a_async",
        data=payload,
        timeout=timeout,
    )

    return parse_response(response)


def query_async_tts_task(
    task_id: str,
    timeout: int = 30,
) -> Dict[str, Any]:
    """
    Query the status of an asynchronous TTS task.

    Args:
        task_id: The task ID returned by create_async_tts_task.
        timeout: Request timeout in seconds.

    Returns:
        Parsed API response with task status and (when complete) result data.

    Raises:
        ValueError: If the API returns an error status.
    """
    response = make_request(
        method="GET",
        endpoint="query/t2a_async",
        params={"task_id": task_id},
        timeout=timeout,
    )

    return parse_response(response)


def wait_for_async_task(
    task_id: str,
    poll_interval: int = 5,
    max_wait: int = 600,
    timeout_per_request: int = 30,
) -> Dict[str, Any]:
    """
    Poll an async TTS task until it completes, fails, or times out.

    Args:
        task_id: The task ID to monitor.
        poll_interval: Seconds between status checks.
        max_wait: Maximum total wait time in seconds.
        timeout_per_request: Timeout for each individual query request.

    Returns:
        Final task result dict.

    Raises:
        TimeoutError: If the task does not complete within max_wait seconds.
        ValueError: If the task fails or expires.
    """
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        if elapsed >= max_wait:
            raise TimeoutError(
                f"Async TTS task {task_id} did not complete within {max_wait}s"
            )

        result = query_async_tts_task(task_id, timeout=timeout_per_request)
        status = result.get("status", "")

        if status == AsyncTaskStatus.SUCCESS.value:
            return result

        if status == AsyncTaskStatus.FAILED.value:
            error_msg = result.get("base_resp", {}).get("status_msg", "Unknown error")
            raise ValueError(f"Async TTS task {task_id} failed: {error_msg}")

        if status == AsyncTaskStatus.EXPIRED.value:
            raise ValueError(f"Async TTS task {task_id} has expired")

        time.sleep(poll_interval)


def async_tts_full(
    text: str,
    model: str = "speech-2.6-hd",
    voice_setting: Optional[VoiceSetting] = None,
    audio_setting: Optional[AudioSetting] = None,
    output_path: Optional[str] = None,
    poll_interval: int = 5,
    max_wait: int = 600,
) -> Dict[str, Any]:
    """
    Full async TTS workflow: create task → poll → download.

    Args:
        text: Text to synthesize.
        model: TTS model name.
        voice_setting: Voice configuration.
        audio_setting: Audio output configuration.
        output_path: If provided, download the resulting audio to this path.
        poll_interval: Seconds between status polls.
        max_wait: Maximum total wait time in seconds.

    Returns:
        Final task result dict. If output_path is given, the audio file is
        saved there and ``result["local_path"]`` is set.

    Raises:
        ValueError: On API errors or task failure.
        TimeoutError: If the task does not finish within max_wait.
    """
    # Step 1: Create the task
    create_result = create_async_tts_task(
        model=model,
        text=text,
        voice_setting=voice_setting,
        audio_setting=audio_setting,
    )

    task_id = create_result.get("task_id")
    if not task_id:
        raise ValueError("No task_id returned from create_async_tts_task")

    # Step 2: Wait for completion
    result = wait_for_async_task(
        task_id=task_id,
        poll_interval=poll_interval,
        max_wait=max_wait,
    )

    # Step 3: Download audio if output_path specified
    if output_path:
        file_url = result.get("file_url") or result.get("audio_file", {}).get("url")
        if file_url:
            download_audio_from_url(file_url, output_path)
            result["local_path"] = output_path
        else:
            raise ValueError("Task completed but no download URL found in result")

    return result
