"""
MiniMax Voice API - Asynchronous Text-to-Speech Module
Supports long text synthesis, suitable for audiobooks, long articles, etc.

Documentation:
- Create Task: https://platform.minimaxi.com/docs/api-reference/speech-t2a-async-create
- Query Task: https://platform.minimaxi.com/docs/api-reference/speech-t2a-async-query
"""

import time
from typing import Optional, Dict, Any, List, Union
from enum import Enum

from utils import (
    VoiceSetting,
    AudioSetting,
    make_request,
    parse_response,
    download_audio_from_url,
)


class AsyncTaskStatus(Enum):
    """Async task status"""
    PROCESSING = "processing"  # Processing
    SUCCESS = "success"        # Success
    FAILED = "failed"          # Failed
    EXPIRED = "expired"        # Expired


# ============================================================================
# Async Task Creation
# ============================================================================

def create_async_tts_task(
    model: str = "speech-2.6-hd",
    text: Optional[str] = None,
    text_file_id: Optional[str] = None,
    voice_setting: Optional[VoiceSetting] = None,
    audio_setting: Optional[AudioSetting] = None,
    pronunciation_dict: Optional[Dict[str, List[str]]] = None,
    timber_weights: Optional[List[Dict[str, Any]]] = None,
    language_boost: Optional[str] = None,
    voice_modify: Optional[Dict[str, Any]] = None,
    subtitle_enable: bool = False,
    aigc_watermark: bool = False,
    timeout: int = 60,
) -> Dict[str, Any]:
    """
    Create async text-to-speech task
    
    Suitable for long text synthesis, supports up to 1 million characters.
    After creating the task, use query_async_tts_task to check status and get results.
    
    Args:
        model: Model version (speech-2.6-hd, speech-2.6-turbo, etc.)
        text: Text to synthesize, mutually exclusive with text_file_id, max 1M characters
        text_file_id: Uploaded text file ID, mutually exclusive with text
        voice_setting: Voice settings
        audio_setting: Audio settings
        pronunciation_dict: Pronunciation dictionary
        timber_weights: Mixed voice weights
        language_boost: Language boost
        voice_modify: Voice effect settings
        subtitle_enable: Whether to enable subtitles
        aigc_watermark: Whether to add audio rhythm identifier
        timeout: Request timeout in seconds
    
    Returns:
        API response containing:
        - task_id: Task ID for status query
        - file_id: Result file ID (available after task completion)
        - extra_info: Additional information
        - trace_id: Session ID
    
    Raises:
        ValueError: Neither text nor text_file_id provided, or both provided
    
    Example:
        >>> result = create_async_tts_task(
        ...     model="speech-2.6-hd",
        ...     text="This is a very long text..." * 1000,
        ...     voice_setting=VoiceSetting(voice_id="male-qn-qingse"),
        ... )
        >>> task_id = result.get("task_id")
        >>> print(f"Task created, ID: {task_id}")
    """
    # Parameter validation
    if not text and not text_file_id:
        raise ValueError("Must provide either text or text_file_id")
    
    if text and text_file_id:
        raise ValueError("Can only provide one of text or text_file_id")
    
    if not voice_setting:
        voice_setting = VoiceSetting(voice_id="male-qn-qingse")
    
    if not audio_setting:
        audio_setting = AudioSetting()
    
    payload = {
        "model": model,
        "voice_setting": voice_setting.to_dict(),
        "audio_setting": audio_setting.to_dict(),
        "subtitle_enable": subtitle_enable,
        "aigc_watermark": aigc_watermark,
    }
    
    if text:
        payload["text"] = text
    else:
        payload["text_file_id"] = text_file_id
    
    if pronunciation_dict:
        payload["pronunciation_dict"] = pronunciation_dict
    
    if timber_weights:
        payload["timber_weights"] = timber_weights
    
    if language_boost:
        payload["language_boost"] = language_boost
    
    if voice_modify:
        payload["voice_modify"] = voice_modify
    
    response = make_request(
        method="POST",
        endpoint="t2a_async_v2",
        data=payload,
        timeout=timeout,
    )
    
    return parse_response(response)


def upload_text_file(
    file_path: str,
    purpose: str = "t2a_async",
    timeout: int = 60,
) -> str:
    """
    Upload text file for async text-to-speech
    
    Args:
        file_path: Text file path, supports .txt or .zip format
        purpose: File purpose, fixed as "t2a_async"
        timeout: Upload timeout in seconds
    
    Returns:
        file_id: File ID, can be used to create async task
    
    Example:
        >>> file_id = upload_text_file("long_novel.txt")
        >>> result = create_async_tts_task(
        ...     text_file_id=file_id,
        ...     voice_setting=VoiceSetting(voice_id="audiobook_male_1"),
        ... )
    """
    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {"purpose": purpose}
        
        response = make_request(
            method="POST",
            endpoint="files/upload",
            data=data,
            files=files,
            timeout=timeout,
        )
    
    result = parse_response(response)
    return result.get("file", {}).get("file_id")


# ============================================================================
# Async Task Query
# ============================================================================

def query_async_tts_task(task_id: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Query async text-to-speech task status
    
    Args:
        task_id: Task ID
        timeout: Request timeout in seconds
    
    Returns:
        API response containing:
        - status: Task status (processing, success, failed, expired)
        - file_id: Audio file ID (when successful)
        - file: File information including download URL (when successful)
        - extra_info: Additional information
        - trace_id: Session ID
    
    Example:
        >>> result = query_async_tts_task(task_id)
        >>> if result.get("status") == "success":
        ...     audio_url = result.get("file", {}).get("download_url")
        ...     print(f"Download URL: {audio_url}")
    """
    response = make_request(
        method="GET",
        endpoint="query/t2a_async_query_v2",
        params={"task_id": task_id},
        timeout=timeout,
    )
    
    return parse_response(response)


def get_task_status(task_id: str) -> AsyncTaskStatus:
    """
    Get task status enum value
    
    Args:
        task_id: Task ID
    
    Returns:
        AsyncTaskStatus enum value
    """
    result = query_async_tts_task(task_id)
    status_str = result.get("status", "processing")
    return AsyncTaskStatus(status_str)


# ============================================================================
# Convenience Functions
# ============================================================================

def wait_for_task(
    task_id: str,
    polling_interval: float = 5.0,
    max_wait_time: float = 3600,
    on_status_change: Optional[callable] = None,
) -> Dict[str, Any]:
    """
    Wait for async task to complete
    
    Args:
        task_id: Task ID
        polling_interval: Polling interval in seconds
        max_wait_time: Maximum wait time in seconds, default 1 hour
        on_status_change: Status change callback function
    
    Returns:
        Final task query result
    
    Raises:
        TimeoutError: Exceeded maximum wait time
        RuntimeError: Task failed
    
    Example:
        >>> result = wait_for_task(task_id, polling_interval=10)
        >>> audio_url = result.get("file", {}).get("download_url")
    """
    start_time = time.time()
    last_status = None
    
    while True:
        elapsed = time.time() - start_time
        if elapsed > max_wait_time:
            raise TimeoutError(f"Task wait timeout, waited {elapsed:.1f} seconds")
        
        result = query_async_tts_task(task_id)
        current_status = result.get("status")
        
        if current_status != last_status:
            last_status = current_status
            if on_status_change:
                on_status_change(current_status, result)
        
        if current_status == AsyncTaskStatus.SUCCESS.value:
            return result
        
        if current_status == AsyncTaskStatus.FAILED.value:
            error_msg = result.get("base_resp", {}).get("status_msg", "Unknown error")
            raise RuntimeError(f"Task failed: {error_msg}")
        
        if current_status == AsyncTaskStatus.EXPIRED.value:
            raise RuntimeError("Task expired")
        
        time.sleep(polling_interval)


def async_tts_full_flow(
    text: str,
    model: str = "speech-2.6-hd",
    voice_setting: Optional[VoiceSetting] = None,
    audio_setting: Optional[AudioSetting] = None,
    output_path: Optional[str] = None,
    polling_interval: float = 5.0,
    max_wait_time: float = 3600,
    **kwargs
) -> Dict[str, Any]:
    """
    Complete async TTS flow (create task -> wait for completion -> download result)
    
    Args:
        text: Text to synthesize
        model: Model version
        voice_setting: Voice settings
        audio_setting: Audio settings
        output_path: Optional output file path, automatically downloads audio
        polling_interval: Polling interval in seconds
        max_wait_time: Maximum wait time in seconds
        **kwargs: Other parameters passed to create_async_tts_task
    
    Returns:
        Dictionary containing task result and download path:
        - task_id: Task ID
        - status: Final status
        - audio_url: Audio download URL (valid for ~9 hours)
        - output_path: Local save path (if output_path was specified)
    
    Example:
        >>> result = async_tts_full_flow(
        ...     text="This is a very long novel..." * 1000,
        ...     voice_setting=VoiceSetting(voice_id="audiobook_male_1"),
        ...     output_path="novel_audio.mp3",
        ... )
        >>> print(f"Audio saved to: {result['output_path']}")
    """
    # Create task
    create_result = create_async_tts_task(
        model=model,
        text=text,
        voice_setting=voice_setting,
        audio_setting=audio_setting,
        **kwargs
    )
    
    task_id = create_result.get("task_id")
    print(f"Async task created, ID: {task_id}")
    
    # Wait for completion
    def on_status(status, result):
        print(f"Task status: {status}")
    
    final_result = wait_for_task(
        task_id=task_id,
        polling_interval=polling_interval,
        max_wait_time=max_wait_time,
        on_status_change=on_status,
    )
    
    # Get download URL
    audio_url = final_result.get("file", {}).get("download_url")
    
    result = {
        "task_id": task_id,
        "status": final_result.get("status"),
        "audio_url": audio_url,
        "extra_info": final_result.get("extra_info"),
    }
    
    # Download audio
    if output_path and audio_url:
        download_audio_from_url(audio_url, output_path)
        result["output_path"] = output_path
        print(f"Audio downloaded to: {output_path}")
    
    return result


def async_tts_from_file(
    file_path: str,
    model: str = "speech-2.6-hd",
    voice_setting: Optional[VoiceSetting] = None,
    audio_setting: Optional[AudioSetting] = None,
    output_path: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create async TTS task from file
    
    Args:
        file_path: Text file path
        model: Model version
        voice_setting: Voice settings
        audio_setting: Audio settings
        output_path: Optional output file path
        **kwargs: Other parameters
    
    Returns:
        Task result dictionary
    
    Example:
        >>> result = async_tts_from_file(
        ...     "novel.txt",
        ...     voice_setting=VoiceSetting(voice_id="audiobook_male_1"),
        ...     output_path="novel_audio.mp3",
        ... )
    """
    # Upload file
    file_id = upload_text_file(file_path)
    print(f"File uploaded, ID: {file_id}")
    
    # Create task
    create_result = create_async_tts_task(
        model=model,
        text_file_id=file_id,
        voice_setting=voice_setting,
        audio_setting=audio_setting,
        **kwargs
    )
    
    task_id = create_result.get("task_id")
    print(f"Async task created, ID: {task_id}")
    
    # Wait for completion
    final_result = wait_for_task(task_id)
    
    audio_url = final_result.get("file", {}).get("download_url")
    
    result = {
        "task_id": task_id,
        "file_id": file_id,
        "status": final_result.get("status"),
        "audio_url": audio_url,
    }
    
    if output_path and audio_url:
        download_audio_from_url(audio_url, output_path)
        result["output_path"] = output_path
    
    return result
