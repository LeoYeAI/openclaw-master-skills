#!/usr/bin/env python3
"""Bona Movie Production skill client."""

import argparse
import json
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Sequence

import requests

DEFAULT_BASE_URL = "https://create.bonanai.com/api/ai-tool/v1/tencent"
DEFAULT_LOGIN_URL = "https://create.bonanai.com/api/auth/loginByAccessKey"
DEFAULT_TIMEOUT = 600
PROCESSING_STATUSES = {0, "0", "submitted", "queued", "queueing", "pending", "processing", "running", "in_progress"}
SUCCESS_STATUSES = {1, "1", "success", "succeeded", "finished", "completed", "done"}
FAILED_STATUSES = {2, "2", 3, "3", "failed", "error", "cancelled"}


@dataclass
class ImageToolSpec:
    tool_name: str
    display_name: str
    provider: str
    model_name: str
    model_version: str
    aspect_ratios: Sequence[str]
    resolutions: Sequence[str]
    task_types: Sequence[str]
    max_reference_images: int = 0
    supports_text_rendering: bool = False
    notes: Sequence[str] = field(default_factory=list)


@dataclass
class VideoToolSpec:
    tool_name: str
    display_name: str
    provider: str
    model_name: str
    model_version: str
    aspect_ratios: Sequence[str]
    durations: Sequence[int]
    resolutions: Sequence[str]
    supports_start_frame: bool = False
    supports_end_frame: bool = False
    max_reference_images: int = 0
    max_reference_videos: int = 0
    max_reference_audios: int = 0
    audio_capability: str = "none"
    notes: Sequence[str] = field(default_factory=list)


@dataclass
class ImageRequest:
    prompt: str
    image_name: Optional[str] = None
    aspect_ratio: Optional[str] = None
    resolution: Optional[str] = None
    task_type: Optional[str] = None
    image_urls: List[str] = field(default_factory=list)
    tool_name: Optional[str] = None
    thread_id: Optional[str] = None


@dataclass
class VideoRequest:
    prompt: Optional[str] = None
    video_name: Optional[str] = None
    aspect_ratio: Optional[str] = None
    duration: Optional[int] = None
    resolution: Optional[str] = None
    start_frame: Optional[str] = None
    end_frame: Optional[str] = None
    reference_images: List[str] = field(default_factory=list)
    reference_videos: List[str] = field(default_factory=list)
    reference_audios: List[str] = field(default_factory=list)
    audio_required: bool = False
    lip_sync_required: bool = False
    sound: Optional[str] = None
    mode: Optional[str] = None
    generate_audio: Optional[bool] = None
    tool_name: Optional[str] = None
    thread_id: Optional[str] = None


@dataclass
class VideoDecision:
    selected_tool: Optional[str]
    ordered_candidates: List[str]
    compatible_candidates: List[str]
    rejected_candidates: Dict[str, List[str]]
    reason: str


IMAGE_REGISTRY: Dict[str, ImageToolSpec] = {
    "generate_image_nano_banana_pro": ImageToolSpec(
        tool_name="generate_image_nano_banana_pro",
        display_name="Nano Banana Pro",
        provider="image_api",
        model_name="GEM",
        model_version="3.0",
        aspect_ratios=("21:9", "16:9", "4:3", "3:2", "1:1", "9:16", "3:4", "2:3", "5:4", "4:5"),
        resolutions=("1K", "2K", "4K"),
        task_types=("TEXT_TO_IMAGE", "REFERENCE_TO_IMAGE", "EDIT_SINGLE_IMAGE", "FUSION_MULTI_IMAGES", "OTHER"),
        max_reference_images=14,
        supports_text_rendering=True,
        notes=("Quality-first model with stronger final rendering quality.",),
    ),
    "generate_image_nano_banana_2": ImageToolSpec(
        tool_name="generate_image_nano_banana_2",
        display_name="Nano Banana 2",
        provider="image_api",
        model_name="GEM",
        model_version="3.1",
        aspect_ratios=("1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1", "4:3", "4:5", "5:4", "8:1", "9:16", "16:9",
                       "21:9"),
        resolutions=("0.5K", "1K", "2K", "4K"),
        task_types=("TEXT_TO_IMAGE", "REFERENCE_TO_IMAGE", "EDIT_SINGLE_IMAGE", "FUSION_MULTI_IMAGES", "OTHER"),
        max_reference_images=14,
        supports_text_rendering=True,
        notes=("Understanding-first model for complex prompts, perspective changes, and text rendering.",),
    ),
}

VIDEO_REGISTRY: Dict[str, VideoToolSpec] = {
    "generate_video_kling_v3": VideoToolSpec(
        tool_name="generate_video_kling_v3",
        display_name="Kling 3.0",
        provider="tencent_vod",
        model_name="Kling",
        model_version="3.0",
        aspect_ratios=("16:9", "9:16", "1:1", "4:3", "3:4", "3:2", "2:3", "21:9"),
        durations=(5, 10),
        resolutions=("720P", "1080P"),
        supports_start_frame=True,
        supports_end_frame=True,
        audio_capability="native_audio_visual",
        notes=(
            "Best for standard text-to-video and image-to-video with stronger cinematic motion.",
            "This merged skill keeps the standard Kling 3.0 path only, not Kling Omni.",
        ),
    ),
    "generate_video_seedance": VideoToolSpec(
        tool_name="generate_video_seedance",
        display_name="Seedance",
        provider="volcengine_ark_via_tencent",
        model_name="seedance-2",
        model_version="1",
        aspect_ratios=("21:9", "16:9", "4:3", "1:1", "3:4", "9:16"),
        durations=tuple(range(4, 16)),
        resolutions=("480P", "720P"),
        supports_start_frame=True,
        supports_end_frame=True,
        max_reference_images=6,
        max_reference_videos=3,
        max_reference_audios=3,
        audio_capability="audio_upload_and_output",
        notes=(
            "Most flexible option for reference images, videos, and audios.",
            "Reference mode and first/last frame mode are mutually exclusive.",
        ),
    ),
}


class BonaClient:
    def __init__(
            self,
            base_url: str,
            login_url: str,
            api_key: Optional[str],
            access_token: Optional[str],
            timeout: int,
    ):
        if not ((api_key and str(api_key).strip()) or (access_token and str(access_token).strip())):
            raise ValueError("api_key or access_token is required")
        self.base_url = base_url.rstrip("/")
        self.login_url = login_url
        self.api_key = str(api_key).strip() if api_key else None
        self.timeout = int(timeout)
        self._access_token: Optional[str] = str(access_token).strip() if access_token else None

    def _login(self) -> str:
        if not self.api_key:
            raise RuntimeError("api_key is required for login")
        response = requests.post(
            self.login_url,
            headers={"Content-Type": "application/json"},
            json={"accessKey": self.api_key},
            timeout=self.timeout,
        )
        payload = self._parse_response(response)
        data = payload.get("data") if isinstance(payload, dict) else None
        access_token = data.get("access_token") if isinstance(data, dict) else None
        if not access_token:
            raise RuntimeError(
                f"login response missing access_token: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        return str(access_token)

    def _get_access_token(self) -> str:
        if not self._access_token:
            self._access_token = self._login()
        return self._access_token

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._get_access_token()}",
        }

    def create_image_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(f"{self.base_url}/image", headers=self.headers, json=payload, timeout=self.timeout)
        return self._parse_response(response)

    def create_video_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(f"{self.base_url}/video", headers=self.headers, json=payload, timeout=self.timeout)
        return self._parse_response(response)

    def query_task(self, task_id: str, thread_id: Optional[str] = None, model_name: Optional[str] = None) -> Dict[
        str, Any]:
        params: Dict[str, str] = {}
        if thread_id:
            params["thread_id"] = thread_id
        if model_name:
            params["model_name"] = model_name
        response = requests.get(f"{self.base_url}/task/{task_id}", headers=self.headers, params=params,
                                timeout=self.timeout)
        return self._parse_response(response)

    def wait_task(self, task_id: str, thread_id: Optional[str], model_name: Optional[str], poll_interval: int,
                  max_wait: int) -> Dict[str, Any]:
        deadline = time.time() + max_wait
        last: Optional[Dict[str, Any]] = None
        while time.time() <= deadline:
            last = self.query_task(task_id=task_id, thread_id=thread_id, model_name=model_name)
            status = extract_status(last)
            if status in SUCCESS_STATUSES or status in FAILED_STATUSES:
                return last
            time.sleep(poll_interval)
        raise TimeoutError(f"task {task_id} did not finish within {max_wait} seconds")

    @staticmethod
    def _parse_response(response: requests.Response) -> Dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            raise RuntimeError(f"http {response.status_code}: {response.text}") from exc
        if response.status_code >= 400:
            raise RuntimeError(json.dumps(payload, ensure_ascii=False, indent=2))
        return payload


def print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def extract_status(result: Optional[Dict[str, Any]]) -> Any:
    if not isinstance(result, dict):
        return None
    data = result.get("data")
    if isinstance(data, dict) and "status" in data:
        return data.get("status")
    return result.get("status")


def extract_task_id(result: Dict[str, Any]) -> Optional[str]:
    data = result.get("data")
    if isinstance(data, dict):
        for key in ("id", "task_id"):
            if data.get(key):
                return str(data[key])
    for key in ("id", "task_id"):
        if result.get(key):
            return str(result[key])
    return None


def normalize_resolution(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    mapping = {
        "0.5k": "0.5K",
        "1k": "1K",
        "2k": "2K",
        "4k": "4K",
        "480p": "480P",
        "720p": "720P",
        "1080p": "1080P",
    }
    return mapping.get(text.lower(), text)


def parse_image_request(args: argparse.Namespace) -> ImageRequest:
    return ImageRequest(
        prompt=args.prompt,
        image_name=args.image_name,
        aspect_ratio=args.aspect_ratio,
        resolution=normalize_resolution(args.resolution),
        task_type=args.task_type,
        image_urls=list(args.image_url or []),
        tool_name=args.tool_name,
        thread_id=args.thread_id,
    )


def choose_image_tool(req: ImageRequest) -> str:
    if req.tool_name:
        if req.tool_name not in IMAGE_REGISTRY:
            raise ValueError(f"unknown image tool_name: {req.tool_name}")
        return req.tool_name
    lower_prompt = req.prompt.lower()
    if req.image_urls:
        if len(req.image_urls) >= 3:
            return "generate_image_nano_banana_2"
        if req.task_type in {"REFERENCE_TO_IMAGE", "EDIT_SINGLE_IMAGE", "FUSION_MULTI_IMAGES"}:
            return "generate_image_nano_banana_2"
    if any(token in lower_prompt for token in
           ["view", "angle", "rear view", "side view", "turnaround", "perspective", "三视图", "转视角", "换视角"]):
        return "generate_image_nano_banana_2"
    if any(token in lower_prompt for token in
           ["9-grid", "九宫格", "5x5", "grid", "sheet", "contact sheet", "sprite", "poster", "cover", "封面", "海报"]):
        return "generate_image_nano_banana_pro"
    if any(token in lower_prompt for token in ["logo", "typography", "text ", "letters", "字体", "文字"]):
        return "generate_image_nano_banana_2"
    return "generate_image_nano_banana_pro"


def build_image_payload(req: ImageRequest, tool_name: str) -> Dict[str, Any]:
    spec = IMAGE_REGISTRY[tool_name]
    payload = {
        "model_name": spec.model_name,
        "model_version": spec.model_version,
        "prompt": req.prompt,
        "thread_id": req.thread_id,
        "image_url_list": req.image_urls or None,
        "aspect_ratio": req.aspect_ratio,
        "resolution": req.resolution or "1K",
        "task_type": req.task_type or "TEXT_TO_IMAGE",
    }
    if req.image_name:
        payload["image_name"] = req.image_name
    return {key: value for key, value in payload.items() if value is not None}


def parse_video_request(args: argparse.Namespace) -> VideoRequest:
    return VideoRequest(
        prompt=args.prompt,
        video_name=args.video_name,
        aspect_ratio=args.aspect_ratio,
        duration=args.duration,
        resolution=normalize_resolution(args.resolution),
        start_frame=args.start_frame,
        end_frame=args.end_frame,
        reference_images=list(args.reference_image or []),
        reference_videos=list(args.reference_video or []),
        reference_audios=list(args.reference_audio or []),
        audio_required=bool(args.audio_required),
        lip_sync_required=bool(args.lip_sync_required),
        sound=args.sound,
        mode=args.mode,
        generate_audio=args.generate_audio,
        tool_name=args.tool_name,
        thread_id=args.thread_id,
    )


def validate_video_tool_request(tool: VideoToolSpec, req: VideoRequest) -> List[str]:
    problems: List[str] = []
    if req.aspect_ratio and req.aspect_ratio not in tool.aspect_ratios:
        problems.append(f"aspect_ratio={req.aspect_ratio} not in {list(tool.aspect_ratios)}")
    if req.duration and req.duration not in tool.durations:
        problems.append(f"duration={req.duration} not in {list(tool.durations)}")
    if req.resolution and req.resolution not in tool.resolutions:
        problems.append(f"resolution={req.resolution} not in {list(tool.resolutions)}")
    if req.start_frame and not tool.supports_start_frame:
        problems.append("start_frame is not supported")
    if req.end_frame and not tool.supports_end_frame:
        problems.append("end_frame is not supported")
    if len(req.reference_images) > tool.max_reference_images:
        problems.append(f"reference_images={len(req.reference_images)} exceeds max={tool.max_reference_images}")
    if len(req.reference_videos) > tool.max_reference_videos:
        problems.append(f"reference_videos={len(req.reference_videos)} exceeds max={tool.max_reference_videos}")
    if len(req.reference_audios) > tool.max_reference_audios:
        problems.append(f"reference_audios={len(req.reference_audios)} exceeds max={tool.max_reference_audios}")

    has_any_input = bool(
        req.prompt or req.start_frame or req.end_frame or req.reference_images or req.reference_videos or req.reference_audios)
    if not has_any_input:
        problems.append("prompt or media input is required")

    if tool.tool_name == "generate_video_kling_v3":
        if req.reference_images:
            problems.append("generate_video_kling_v3 does not support reference_image_list in this skill")
        if req.reference_videos:
            problems.append("generate_video_kling_v3 does not support reference_video_list in this skill")
        if req.reference_audios:
            problems.append("generate_video_kling_v3 does not support reference_audio_list in this skill")
    elif tool.tool_name == "generate_video_seedance":
        reference_mode = bool(req.reference_images or req.reference_videos or req.reference_audios)
        first_last_mode = bool(req.start_frame or req.end_frame)
        if first_last_mode and not req.start_frame:
            problems.append("generate_video_seedance requires start_frame when end_frame is provided")
        if reference_mode and first_last_mode:
            problems.append("generate_video_seedance reference mode and first/last frame mode are mutually exclusive")

    return problems


def choose_video_tool(req: VideoRequest) -> VideoDecision:
    if req.tool_name:
        alias = "generate_video_seedance" if req.tool_name == "generate_video_seedance_2" else req.tool_name
        forced = VIDEO_REGISTRY.get(alias)
        if not forced:
            raise ValueError(f"unknown video tool_name: {req.tool_name}")
        problems = validate_video_tool_request(forced, req)
        return VideoDecision(
            selected_tool=alias if not problems else None,
            ordered_candidates=[alias],
            compatible_candidates=[alias] if not problems else [],
            rejected_candidates={alias: problems} if problems else {},
            reason="tool_name was provided explicitly",
        )

    if req.reference_images or req.reference_videos or req.reference_audios:
        ordered = ["generate_video_seedance", "generate_video_kling_v3"]
        reason = "reference-driven video generation prefers Seedance"
    elif req.audio_required or req.lip_sync_required:
        ordered = ["generate_video_kling_v3", "generate_video_seedance"]
        reason = "audio or lip-sync requirement prefers Kling 3.0"
    elif req.start_frame or req.end_frame:
        ordered = ["generate_video_kling_v3", "generate_video_seedance"]
        reason = "frame-driven video generation prefers Kling 3.0, then Seedance"
    else:
        ordered = ["generate_video_kling_v3", "generate_video_seedance"]
        reason = "text-to-video prefers Kling 3.0, then Seedance"

    compatible: List[str] = []
    rejected: Dict[str, List[str]] = {}
    for tool_name in ordered:
        spec = VIDEO_REGISTRY[tool_name]
        problems = validate_video_tool_request(spec, req)
        if problems:
            rejected[tool_name] = problems
        else:
            compatible.append(tool_name)

    return VideoDecision(
        selected_tool=compatible[0] if compatible else None,
        ordered_candidates=ordered,
        compatible_candidates=compatible,
        rejected_candidates=rejected,
        reason=reason,
    )


def build_video_payload(req: VideoRequest, tool_name: str) -> Dict[str, Any]:
    spec = VIDEO_REGISTRY[tool_name]
    payload: Dict[str, Any] = {
        "model_name": spec.model_name,
        "model_version": spec.model_version,
        "prompt": req.prompt,
        "thread_id": req.thread_id,
    }

    if tool_name == "generate_video_kling_v3":
        payload.update({
            "aspect_ratio": req.aspect_ratio or "16:9",
            "duration": req.duration or 5,
            "resolution": req.resolution or "1080P",
            "image_url_list": [req.start_frame] if req.start_frame else None,
            "first_frame_url": req.start_frame,
            "last_frame_url": req.end_frame,
            "start_frame_image_url": req.start_frame,
            "tail_frame_image_url": req.end_frame,
            "sound": req.sound or "on",
            "additional_parameters": {"mode": req.mode or "pro"},
        })
    elif tool_name == "generate_video_seedance":
        payload.update({
            "ratio": req.aspect_ratio or "16:9",
            "duration": req.duration or 5,
            "resolution": req.resolution or "720P",
            "first_frame_url": req.start_frame,
            "last_frame_url": req.end_frame,
            "reference_image_url_list": req.reference_images or None,
            "reference_video_url_list": req.reference_videos or None,
            "reference_audio_url_list": req.reference_audios or None,
            "image_start_frame": req.start_frame,
            "image_end_frame": req.end_frame,
            "reference_image_list": req.reference_images or None,
            "reference_video_list": req.reference_videos or None,
            "reference_audio_list": req.reference_audios or None,
            "generate_audio": req.generate_audio,
        })
    else:
        raise ValueError(f"unsupported video tool_name: {tool_name}")

    if req.video_name:
        payload["video_name"] = req.video_name
    return {key: value for key, value in payload.items() if value is not None}


def image_models_as_json() -> List[Dict[str, Any]]:
    return [asdict(spec) for spec in IMAGE_REGISTRY.values()]


def video_models_as_json() -> List[Dict[str, Any]]:
    return [asdict(spec) for spec in VIDEO_REGISTRY.values()]


def add_client_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--login-url", default=DEFAULT_LOGIN_URL)
    parser.add_argument("--api-key", default=os.getenv("BONA_API_KEY"))
    parser.add_argument("--access-token", default=os.getenv("BONA_ACCESS_TOKEN"))
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)


def add_image_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--tool-name")
    parser.add_argument("--image-name")
    parser.add_argument("--prompt")
    parser.add_argument("--image-url", action="append")
    parser.add_argument("--aspect-ratio")
    parser.add_argument("--resolution")
    parser.add_argument("--task-type")
    parser.add_argument("--thread-id")


def add_video_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--tool-name")
    parser.add_argument("--video-name")
    parser.add_argument("--prompt")
    parser.add_argument("--aspect-ratio")
    parser.add_argument("--duration", type=int)
    parser.add_argument("--resolution")
    parser.add_argument("--start-frame")
    parser.add_argument("--end-frame")
    parser.add_argument("--reference-image", action="append")
    parser.add_argument("--reference-video", action="append")
    parser.add_argument("--reference-audio", action="append")
    parser.add_argument("--audio-required", action="store_true")
    parser.add_argument("--lip-sync-required", action="store_true")
    parser.add_argument("--sound", choices=["on", "off"])
    parser.add_argument("--mode", choices=["std", "pro"])
    parser.add_argument("--generate-audio", action="store_true")
    parser.add_argument("--thread-id")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bona Movie Production skill client")
    add_client_args(parser)
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_image = subparsers.add_parser("list-image-models", help="列出图片模型")
    add_client_args(list_image)

    choose_image = subparsers.add_parser("choose-image-tool", help="自动选择图片工具")
    add_client_args(choose_image)
    add_image_args(choose_image)

    create_image = subparsers.add_parser("create-image", help="创建图片任务")
    add_client_args(create_image)
    add_image_args(create_image)
    create_image.add_argument("--wait", action="store_true")
    create_image.add_argument("--poll-interval", type=int, default=5)
    create_image.add_argument("--max-wait", type=int, default=300)
    create_image.add_argument("--print-payload", action="store_true")

    query_image = subparsers.add_parser("query-image", help="查询图片任务")
    add_client_args(query_image)
    query_image.add_argument("--task-id", required=True)
    query_image.add_argument("--thread-id")
    query_image.add_argument("--model-name")

    list_video = subparsers.add_parser("list-video-models", help="列出视频模型")
    add_client_args(list_video)

    choose_video = subparsers.add_parser("choose-video-tool", help="自动选择视频工具")
    add_client_args(choose_video)
    add_video_args(choose_video)

    create_video = subparsers.add_parser("create-video", help="创建视频任务")
    add_client_args(create_video)
    add_video_args(create_video)
    create_video.add_argument("--wait", action="store_true")
    create_video.add_argument("--poll-interval", type=int, default=5)
    create_video.add_argument("--max-wait", type=int, default=300)
    create_video.add_argument("--print-payload", action="store_true")

    query_video = subparsers.add_parser("query-video", help="查询视频任务")
    add_client_args(query_video)
    query_video.add_argument("--task-id", required=True)
    query_video.add_argument("--thread-id")
    query_video.add_argument("--model-name")

    return parser.parse_args()


def run_image_flow(args: argparse.Namespace) -> int:
    if args.command == "list-image-models":
        print_json(image_models_as_json())
        return 0

    if args.command == "query-image":
        client = BonaClient(args.base_url, args.login_url, args.api_key, args.access_token, args.timeout)
        print_json(client.query_task(args.task_id, thread_id=args.thread_id, model_name=args.model_name))
        return 0

    req = parse_image_request(args)
    if not req.prompt:
        raise ValueError("prompt is required")
    tool_name = choose_image_tool(req)
    payload = build_image_payload(req, tool_name)

    if args.command == "choose-image-tool":
        print_json({"selected_tool": tool_name, "selected_spec": asdict(IMAGE_REGISTRY[tool_name]),
                    "payload_preview": payload})
        return 0

    if args.print_payload:
        print_json({"selected_tool": tool_name, "payload": payload})
        if not args.wait:
            return 0

    client = BonaClient(args.base_url, args.login_url, args.api_key, args.access_token, args.timeout)
    created = client.create_image_task(payload)
    if not args.wait:
        print_json({"selected_tool": tool_name, "create_response": created})
        return 0

    task_id = extract_task_id(created)
    if not task_id:
        raise RuntimeError("create response missing task_id")
    queried = client.wait_task(task_id, thread_id=req.thread_id, model_name=payload.get("model_name"),
                               poll_interval=args.poll_interval, max_wait=args.max_wait)
    print_json({"selected_tool": tool_name, "payload": payload, "create_response": created, "query_response": queried})
    return 0


def run_video_flow(args: argparse.Namespace) -> int:
    if args.command == "list-video-models":
        print_json(video_models_as_json())
        return 0

    if args.command == "query-video":
        client = BonaClient(args.base_url, args.login_url, args.api_key, args.access_token, args.timeout)
        print_json(client.query_task(args.task_id, thread_id=args.thread_id, model_name=args.model_name))
        return 0

    req = parse_video_request(args)
    decision = choose_video_tool(req)

    if args.command == "choose-video-tool":
        selected_spec = VIDEO_REGISTRY.get(decision.selected_tool) if decision.selected_tool else None
        result = {
            "decision": asdict(decision),
            "selected_spec": asdict(selected_spec) if selected_spec else None,
        }
        if decision.selected_tool:
            result["payload_preview"] = build_video_payload(req, decision.selected_tool)
        print_json(result)
        return 0

    if not decision.selected_tool:
        raise ValueError(json.dumps(asdict(decision), ensure_ascii=False, indent=2))

    payload = build_video_payload(req, decision.selected_tool)
    if args.print_payload:
        print_json({
            "selected_tool": decision.selected_tool,
            "decision_reason": decision.reason,
            "payload": payload,
        })
        if not args.wait:
            return 0

    client = BonaClient(args.base_url, args.login_url, args.api_key, args.access_token, args.timeout)
    created = client.create_video_task(payload)
    if not args.wait:
        print_json({
            "selected_tool": decision.selected_tool,
            "decision_reason": decision.reason,
            "create_response": created,
        })
        return 0

    task_id = extract_task_id(created)
    if not task_id:
        raise RuntimeError("create response missing task_id")
    queried = client.wait_task(task_id, thread_id=req.thread_id, model_name=payload.get("model_name"),
                               poll_interval=args.poll_interval, max_wait=args.max_wait)
    print_json({
        "selected_tool": decision.selected_tool,
        "decision_reason": decision.reason,
        "payload": payload,
        "create_response": created,
        "query_response": queried,
    })
    return 0


def main() -> int:
    args = parse_args()
    try:
        if args.command in {"list-image-models", "choose-image-tool", "create-image", "query-image"}:
            return run_image_flow(args)
        return run_video_flow(args)
    except Exception as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
