#!/usr/bin/env python3
"""Generate videos using Topview Common Task APIs.

## AGENT INSTRUCTIONS — READ FIRST
- Default workflow: ALWAYS use `run` (submit + auto-poll).
  Do NOT ask the user to run query manually.
- Only use `query` when `run` has already timed out and a taskId exists,
  or when the user explicitly provides a taskId to resume.
- When using `query`, keep polling (default timeout=600s) until
  status is 'success' or 'fail'. Do NOT stop after a single check.
- Never hand a pending taskId back to the user and say "check it later".
  Always poll to completion within the timeout window.

Supported task types:
    i2v   Image-to-Video V2   — generate video from a first/end frame image
    t2v   Text-to-Video       — generate video from a text prompt
    omni  Omni Reference      — generate video from reference images/videos + prompt

Subcommands:
    run     Submit task AND poll until done — DEFAULT, use this first
    submit  Submit only, print taskId, exit — use for parallel batch jobs
    query   Poll an existing taskId until done (or timeout) — use for recovery

Usage:
    python video_gen.py run  --type i2v  --first-frame <fileId|path> --prompt "..." [options]
    python video_gen.py run  --type t2v  --model "Seedance 1.5 Pro" --prompt "..." [options]
    python video_gen.py run  --type omni --model "Standard" --prompt "..." [options]
    python video_gen.py submit --type <i2v|t2v|omni> [task-specific options]
    python video_gen.py query  --type <i2v|t2v|omni> --task-id <taskId> [options]
"""

import argparse
import json as json_mod
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from shared.client import TopviewClient, TopviewError
from shared.upload import resolve_local_file

TASK_TYPES = ("i2v", "t2v", "omni")

ENDPOINTS = {
    "i2v": {
        "submit": "/v2/common_task/image2video/task/submit",
        "query": "/v2/common_task/image2video/task/query",
    },
    "t2v": {
        "submit": "/v1/common_task/text2video/task/submit",
        "query": "/v1/common_task/text2video/task/query",
    },
    "omni": {
        "submit": "/v1/common_task/omni_reference/task/submit",
        "query": "/v1/common_task/omni_reference/task/query",
    },
}

DEFAULT_TIMEOUT = 600
DEFAULT_INTERVAL = 5

# ---------------------------------------------------------------------------
# Model constraints — `model` must use display names, NOT code names.
# Each entry: { "aspectRatio": list|None, "resolution": list|None, "duration": str }
#   None = not supported / do not send
# ---------------------------------------------------------------------------

I2V_MODELS = {
    "Standard":                      {"aspectRatio": None,                                          "resolution": [480, 720],        "duration": "4-15",   "nativeAudio": True,  "inputMode": "first_end"},
    "Fast":                          {"aspectRatio": None,                                          "resolution": [480, 720],        "duration": "4-15",   "nativeAudio": True,  "inputMode": "first_end"},
    "Seedance 1.5 Pro":             {"aspectRatio": None,                                          "resolution": [720, 1080],       "duration": "4-12",   "nativeAudio": True,  "inputMode": "first_end"},
    "Seedance 1.0 Pro Fast":        {"aspectRatio": None,                                          "resolution": [720, 1080],       "duration": "5,10,12","nativeAudio": False, "inputMode": "single"},
    "Seedance 1.0 Pro":             {"aspectRatio": None,                                          "resolution": [720, 1080],       "duration": "5,10,12","nativeAudio": False, "inputMode": "first_end"},
    "Kling V3":                     {"aspectRatio": None,                                          "resolution": [720, 1080],       "duration": "3-15",   "nativeAudio": True,  "inputMode": "first_end"},
    "Kling V3 Reference Video":     {"aspectRatio": ["9:16", "1:1", "16:9"],                       "resolution": [720, 1080],       "duration": "3-15",   "nativeAudio": True,  "inputMode": "multi_ref"},
    "Kling O3":                     {"aspectRatio": None,                                          "resolution": [720, 1080],       "duration": "3-15",   "nativeAudio": True,  "inputMode": "first_end"},
    "Kling O3 Reference-to-Video":  {"aspectRatio": ["9:16", "1:1", "16:9"],                       "resolution": [720, 1080],       "duration": "3-15",   "nativeAudio": True,  "inputMode": "multi_ref"},
    "Kling 2.6":                    {"aspectRatio": None,                                          "resolution": None,              "duration": "5,10",   "nativeAudio": True,  "inputMode": "single"},
    "Kling O1 Reference-to-Video":  {"aspectRatio": ["9:16", "1:1", "16:9"],                       "resolution": [1080],            "duration": "3-10",   "nativeAudio": False, "inputMode": "multi_ref"},
    "Kling 2.5 Turbo Pro":          {"aspectRatio": None,                                          "resolution": [1080],            "duration": "5,10",   "nativeAudio": False, "inputMode": "first_end"},
    "Kling 2.5 Turbo Std":          {"aspectRatio": None,                                          "resolution": [1080],            "duration": "5,10",   "nativeAudio": False, "inputMode": "single"},
    "Sora 2":                       {"aspectRatio": ["9:16", "16:9"],                              "resolution": None,              "duration": "4,8,12", "nativeAudio": False, "inputMode": "single"},
    "Sora 2 Pro":                   {"aspectRatio": ["9:16", "16:9"],                              "resolution": [720, 1080],       "duration": "4,8,12", "nativeAudio": False, "inputMode": "single"},
    "Veo 3.1":                      {"aspectRatio": ["9:16", "16:9"],                              "resolution": [720, 1080, 2160], "duration": "4,6,8",  "nativeAudio": True,  "inputMode": "first_end"},
    "Veo 3.1 Reference to video":   {"aspectRatio": ["9:16", "16:9"],                              "resolution": [720, 1080, 2160], "duration": "8",      "nativeAudio": True,  "inputMode": "multi_ref"},
    "Veo 3.1 Fast":                 {"aspectRatio": ["9:16", "16:9"],                              "resolution": [720, 1080, 2160], "duration": "4,6,8",  "nativeAudio": True,  "inputMode": "first_end"},
    "Veo 3.1 Fast Reference to video": {"aspectRatio": ["9:16", "16:9"],                           "resolution": [720, 1080, 2160], "duration": "8",      "nativeAudio": True,  "inputMode": "multi_ref"},
    "MiniMax-Hailuo-02":            {"aspectRatio": None,                                          "resolution": [768, 1080],       "duration": "6,10",   "nativeAudio": False, "inputMode": "first_end"},
    "MiniMax-Hailuo-2.3":           {"aspectRatio": None,                                          "resolution": [768, 1080],       "duration": "6,10",   "nativeAudio": False, "inputMode": "single"},
    "MiniMax-Hailuo-2.3-Fast":      {"aspectRatio": None,                                          "resolution": [768, 1080],       "duration": "6,10",   "nativeAudio": False, "inputMode": "single"},
    "Vidu Q3 Pro":                  {"aspectRatio": ["9:16", "3:4", "1:1", "4:3", "16:9"],         "resolution": [540, 720, 1080],  "duration": "1-16",   "nativeAudio": True,  "inputMode": "single"},
    "Vidu Q2 Reference to Video":   {"aspectRatio": ["9:16", "3:4", "1:1", "4:3", "16:9"],         "resolution": [1080],            "duration": "2-10",   "nativeAudio": False, "inputMode": "multi_ref"},
    "Wan 2.6":                      {"aspectRatio": None,                                          "resolution": [720, 1080],       "duration": "5,10,15","nativeAudio": True,  "inputMode": "single"},
    "Topview Lite":                 {"aspectRatio": ["9:16", "3:4", "1:1", "4:3", "16:9"],         "resolution": None,              "duration": "5,10",   "nativeAudio": False, "inputMode": "single"},
    "Topview Pro":                  {"aspectRatio": ["9:16", "3:4", "1:1", "4:3", "16:9"],         "resolution": None,              "duration": "5,10",   "nativeAudio": False, "inputMode": "single"},
    "Topview Plus":                 {"aspectRatio": ["9:16", "1:1", "16:9"],                       "resolution": None,              "duration": "5,10",   "nativeAudio": False, "inputMode": "single"},
    "Topview Best":                 {"aspectRatio": ["9:16", "1:1", "16:9"],                       "resolution": None,              "duration": "5,10",   "nativeAudio": False, "inputMode": "single"},
}

T2V_MODELS = {
    "Standard":                      {"aspectRatio": ["9:16", "3:4", "1:1", "4:3", "16:9", "21:9"], "resolution": [480, 720],        "duration": "4-15",   "nativeAudio": True},
    "Fast":                          {"aspectRatio": ["9:16", "3:4", "1:1", "4:3", "16:9", "21:9"], "resolution": [480, 720],        "duration": "4-15",   "nativeAudio": True},
    "Seedance 1.5 Pro":             {"aspectRatio": ["9:16", "3:4", "1:1", "4:3", "16:9"],         "resolution": [720, 1080],       "duration": "4-12",   "nativeAudio": True},
    "Seedance 1.0 Pro Fast":        {"aspectRatio": ["9:16", "3:4", "1:1", "4:3", "16:9"],         "resolution": [720, 1080],       "duration": "5,10,12","nativeAudio": False},
    "Seedance 1.0 Pro":             {"aspectRatio": ["9:16", "3:4", "1:1", "4:3", "16:9"],         "resolution": [720, 1080],       "duration": "5,10,12","nativeAudio": False},
    "Kling O3":                     {"aspectRatio": ["9:16", "1:1", "16:9"],                       "resolution": [720, 1080],       "duration": "3-15",   "nativeAudio": True},
    "Kling V3":                     {"aspectRatio": ["9:16", "1:1", "16:9"],                       "resolution": [720, 1080],       "duration": "3-15",   "nativeAudio": True},
    "Kling 2.6":                    {"aspectRatio": ["9:16", "1:1", "16:9"],                       "resolution": None,              "duration": "5,10",   "nativeAudio": True},
    "Kling 2.5 Turbo Pro":          {"aspectRatio": ["9:16", "1:1", "16:9"],                       "resolution": [1080],            "duration": "5,10",   "nativeAudio": False},
    "Kling 2.5 Turbo Std":          {"aspectRatio": ["9:16", "1:1", "16:9"],                       "resolution": [1080],            "duration": "5,10",   "nativeAudio": False},
    "Sora 2":                       {"aspectRatio": ["9:16", "16:9"],                              "resolution": None,              "duration": "4,8,12", "nativeAudio": False},
    "Sora 2 Pro":                   {"aspectRatio": ["9:16", "16:9"],                              "resolution": [720, 1080],       "duration": "4,8,12", "nativeAudio": False},
    "Veo 3.1":                      {"aspectRatio": ["9:16", "16:9"],                              "resolution": [720, 1080, 2160], "duration": "4,6,8",  "nativeAudio": True},
    "Veo 3.1 Fast":                 {"aspectRatio": ["9:16", "16:9"],                              "resolution": [720, 1080, 2160], "duration": "4,6,8",  "nativeAudio": True},
    "MiniMax-Hailuo-02":            {"aspectRatio": None,                                          "resolution": [768, 1080],       "duration": "6,10",   "nativeAudio": False},
    "MiniMax-Hailuo-2.3":           {"aspectRatio": None,                                          "resolution": [768, 1080],       "duration": "6,10",   "nativeAudio": False},
    "Vidu Q3 Pro":                  {"aspectRatio": ["9:16", "3:4", "1:1", "4:3", "16:9"],         "resolution": [540, 720, 1080],  "duration": "1-16",   "nativeAudio": True},
    "Vidu Q2":                      {"aspectRatio": ["9:16", "3:4", "1:1", "4:3", "16:9"],         "resolution": [1080],            "duration": "2-10",   "nativeAudio": False},
    "Wan 2.6":                      {"aspectRatio": ["9:16", "3:4", "1:1", "4:3", "16:9"],         "resolution": [720, 1080],       "duration": "5,10,15","nativeAudio": True},
    "Topview Lite":                 {"aspectRatio": ["9:16", "3:4", "1:1", "4:3", "16:9"],         "resolution": None,              "duration": "5,10",   "nativeAudio": False},
    "Topview Pro":                  {"aspectRatio": ["9:16", "3:4", "1:1", "4:3", "16:9"],         "resolution": None,              "duration": "5,10",   "nativeAudio": False},
    "Topview Plus":                 {"aspectRatio": ["9:16", "1:1", "16:9"],                       "resolution": None,              "duration": "5,10",   "nativeAudio": False},
    "Topview Best":                 {"aspectRatio": ["9:16", "1:1", "16:9"],                       "resolution": None,              "duration": "5,10",   "nativeAudio": False},
}

OMNI_MODELS = {
    "Standard":              {"aspectRatio": ["9:16", "3:4", "1:1", "4:3", "16:9", "21:9"], "resolution": [480, 720],  "duration": "4-15",  "internetSearch": True,  "nativeAudio": True},
    "Fast":                  {"aspectRatio": ["9:16", "3:4", "1:1", "4:3", "16:9", "21:9"], "resolution": [480, 720],  "duration": "4-15",  "internetSearch": True,  "nativeAudio": True},
    "Kling O3 Video-Edit":   {"aspectRatio": None,                                          "resolution": [720, 1080], "duration": "3-10",  "internetSearch": False, "nativeAudio": False},
    "Kling O1 Video-Edit":   {"aspectRatio": None,                                          "resolution": [1080],      "duration": "3-10",  "internetSearch": False, "nativeAudio": False},
}

MODEL_REGISTRY = {"i2v": I2V_MODELS, "t2v": T2V_MODELS, "omni": OMNI_MODELS}

# ---------------------------------------------------------------------------
# Per-second pricing rates (credits, generatingCount=1).
# Key: (resolution_or_0, sound_on_or_None). 0 = resolution-independent, None = sound irrelevant.
# totalCost = rate * duration * generatingCount
# See references/api-docs.md for full pricing tables.
# ---------------------------------------------------------------------------

_RATE = {
    "Standard":                {(0, None): 1.0},
    "Fast":                    {(0, None): 1.0},
    "Seedance 1.5 Pro":        {(720, False): 0.12, (720, True): 0.25, (1080, False): 0.28, (1080, True): 0.55},
    "Seedance 1.0 Pro Fast":   {(720, None): 0.07, (1080, None): 0.15},
    "Seedance 1.0 Pro":        {(720, None): 0.20, (1080, None): 0.45},
    "Kling V3":                {(720, False): 0.50, (720, True): 0.80, (1080, False): 0.80, (1080, True): 1.00},
    "Kling V3 Reference Video":{(720, False): 0.50, (720, True): 0.80, (1080, False): 0.80, (1080, True): 1.00},
    "Kling O3":                {(720, False): 0.50, (720, True): 0.60, (1080, False): 0.80, (1080, True): 0.90},
    "Kling O3 Reference-to-Video": {(720, False): 0.50, (720, True): 0.60, (1080, False): 0.80, (1080, True): 0.90},
    "Kling 2.6":               {(0, False): 0.31, (0, True): 0.65},
    "Kling O1 Reference-to-Video": {(1080, None): 0.50},
    "Kling 2.5 Turbo Pro":     {(1080, None): 0.31},
    "Kling 2.5 Turbo Std":     {(1080, None): 0.20},
    "Sora 2":                  {(0, None): 0.56},
    "Sora 2 Pro":              {(720, None): 1.68, (1080, None): 2.80},
    "Veo 3.1":                 {(720, False): 1.10, (720, True): 2.20, (1080, False): 1.10, (1080, True): 2.20, (2160, False): 2.20, (2160, True): 3.30},
    "Veo 3.1 Reference to video": {(720, False): 1.10, (720, True): 2.20, (1080, False): 1.10, (1080, True): 2.20, (2160, False): 2.20, (2160, True): 3.30},
    "Veo 3.1 Fast":            {(720, False): 0.60, (720, True): 0.90, (1080, False): 0.60, (1080, True): 0.90, (2160, False): 1.70, (2160, True): 2.00},
    "Veo 3.1 Fast Reference to video": {(720, False): 0.60, (720, True): 0.90, (1080, False): 0.60, (1080, True): 0.90, (2160, False): 1.70, (2160, True): 2.00},
    "MiniMax-Hailuo-02":       {(768, None): 0.32, (1080, None): 0.47},
    "MiniMax-Hailuo-2.3":      {(768, None): 0.32, (1080, None): 0.47},
    "MiniMax-Hailuo-2.3-Fast": {(768, None): 0.18, (1080, None): 0.30},
    "Vidu Q3 Pro":             {(540, None): 0.40, (720, None): 0.90, (1080, None): 1.00},
    "Vidu Q2":                 {(1080, None): 0.28},
    "Vidu Q2 Reference to Video": {(1080, None): 0.56},
    "Wan 2.6":                 {(720, None): 0.46, (1080, None): 0.77},
    "Topview Lite":            {(0, None): 0.10},
    "Topview Pro":             {(0, None): 0.20},
    "Topview Plus":            {(0, None): 0.54},
    "Topview Best":            {(0, None): 1.55},
    "Standard":                {(0, None): 1.0},
    "Fast":                    {(0, None): 1.0},
    "Kling O3 Video-Edit":     {(720, None): 1.70, (1080, None): 2.00},
    "Kling O1 Video-Edit":     {(0, None): 0.80},
}


def estimate_cost(model: str, resolution: int | None, duration: int,
                  sound_on: bool = False, count: int = 1) -> float | None:
    """Return estimated total cost in credits, or None if model/params unknown."""
    rates = _RATE.get(model)
    if not rates:
        return None
    res = resolution or 0
    for key in [(res, sound_on), (res, None), (0, sound_on), (0, None)]:
        if key in rates:
            return round(rates[key] * duration * count, 2)
    return None


def _parse_duration_spec(spec: str) -> str:
    """Convert duration spec to human-readable hint for error messages."""
    if "," in spec:
        return f"one of [{spec}]s"
    if "-" in spec:
        lo, hi = spec.split("-")
        return f"{lo}–{hi}s"
    return f"{spec}s"


def validate_model_params(task_type: str, model: str, aspect_ratio: str | None,
                          resolution: int | None, duration: int | None,
                          quiet: bool) -> None:
    """Warn on stderr if parameters are incompatible with model constraints."""
    registry = MODEL_REGISTRY.get(task_type, {})
    if model not in registry:
        if not quiet:
            known = ", ".join(sorted(registry.keys()))
            print(
                f"Warning: unknown model '{model}' for {task_type}. "
                f"Known models: {known}",
                file=sys.stderr,
            )
        return

    spec = registry[model]

    if aspect_ratio and spec["aspectRatio"] is None:
        if not quiet:
            print(
                f"Warning: model '{model}' does not support aspectRatio "
                f"(got '{aspect_ratio}'). Parameter will be ignored by the API.",
                file=sys.stderr,
            )
    elif aspect_ratio and spec["aspectRatio"] and aspect_ratio not in spec["aspectRatio"]:
        if not quiet:
            print(
                f"Warning: model '{model}' supports aspectRatio "
                f"{spec['aspectRatio']}, got '{aspect_ratio}'.",
                file=sys.stderr,
            )

    if resolution and spec["resolution"] is None:
        if not quiet:
            print(
                f"Warning: model '{model}' does not support resolution "
                f"(got {resolution}). Parameter will be ignored by the API.",
                file=sys.stderr,
            )
    elif resolution and spec["resolution"] and resolution not in spec["resolution"]:
        if not quiet:
            print(
                f"Warning: model '{model}' supports resolution "
                f"{spec['resolution']}, got {resolution}.",
                file=sys.stderr,
            )

    if duration and spec["duration"]:
        dur_str = spec["duration"]
        valid = True
        if "," in dur_str:
            valid = duration in [int(x) for x in dur_str.split(",")]
        elif "-" in dur_str:
            lo, hi = [int(x) for x in dur_str.split("-")]
            valid = lo <= duration <= hi
        else:
            valid = duration == int(dur_str)
        if not valid and not quiet:
            print(
                f"Warning: model '{model}' supports duration "
                f"{_parse_duration_spec(dur_str)}, got {duration}s.",
                file=sys.stderr,
            )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def resolve_file(client: TopviewClient, file_ref: str, quiet: bool) -> str:
    """If file_ref looks like a local path, upload it and return fileId."""
    return resolve_local_file(file_ref, quiet=quiet, client=client)


def build_i2v_body(args, client: TopviewClient) -> dict:
    """Build request body for Image-to-Video V2."""
    body = {}
    if args.model:
        body["model"] = args.model
    if args.first_frame:
        body["firstFrameFileId"] = resolve_file(client, args.first_frame, args.quiet)
    if args.end_frame:
        body["endFrameFileId"] = resolve_file(client, args.end_frame, args.quiet)
    if args.ref_images:
        body["referenceImageFileIds"] = [
            resolve_file(client, ref, args.quiet) for ref in args.ref_images
        ]
    if args.prompt:
        body["prompt"] = args.prompt
    if args.aspect_ratio:
        body["aspectRatio"] = args.aspect_ratio
    if args.resolution:
        body["resolution"] = args.resolution
    if args.duration:
        body["duration"] = args.duration
    if args.sound:
        body["sound"] = args.sound
    if args.count:
        body["generatingCount"] = args.count
    if args.board_id:
        body["boardId"] = args.board_id
    return body


def build_t2v_body(args) -> dict:
    """Build request body for Text-to-Video."""
    body = {
        "model": args.model,
        "prompt": args.prompt,
    }
    if args.aspect_ratio:
        body["aspectRatio"] = args.aspect_ratio
    if args.resolution:
        body["resolution"] = args.resolution
    if args.duration:
        body["duration"] = args.duration
    if args.sound:
        body["sound"] = args.sound
    if args.count:
        body["generatingCount"] = args.count
    if args.board_id:
        body["boardId"] = args.board_id
    return body


def build_omni_body(args, client: TopviewClient) -> dict:
    """Build request body for Omni Reference."""
    body = {
        "model": args.model,
        "prompt": args.prompt,
    }
    if args.input_images:
        images = json_mod.loads(args.input_images)
        for img in images:
            if "fileId" in img and os.path.isfile(img["fileId"]):
                img["fileId"] = resolve_file(client, img["fileId"], args.quiet)
        body["inputImages"] = images
    if args.input_videos:
        videos = json_mod.loads(args.input_videos)
        for vid in videos:
            if "fileId" in vid and os.path.isfile(vid["fileId"]):
                vid["fileId"] = resolve_file(client, vid["fileId"], args.quiet)
        body["inputVideos"] = videos
    if args.aspect_ratio:
        body["aspectRatio"] = args.aspect_ratio
    if args.resolution:
        body["resolution"] = args.resolution
    if args.duration:
        body["duration"] = args.duration
    if args.count:
        body["generatingCount"] = args.count
    if args.internet_search:
        body["internetSearch"] = True
    if args.board_id:
        body["boardId"] = args.board_id
    return body


def build_body(args, client: TopviewClient) -> dict:
    """Dispatch to the type-specific body builder, with model constraint checks."""
    if args.model:
        validate_model_params(
            args.type, args.model,
            getattr(args, "aspect_ratio", None),
            getattr(args, "resolution", None),
            getattr(args, "duration", None),
            args.quiet,
        )
    if args.type == "i2v":
        return build_i2v_body(args, client)
    elif args.type == "t2v":
        return build_t2v_body(args)
    elif args.type == "omni":
        return build_omni_body(args, client)
    raise ValueError(f"Unknown type: {args.type}")


def do_submit(client: TopviewClient, task_type: str, body: dict, quiet: bool) -> str:
    """POST submit task, return taskId."""
    path = ENDPOINTS[task_type]["submit"]
    label = {"i2v": "image-to-video", "t2v": "text-to-video", "omni": "omni-reference"}
    if not quiet:
        print(f"Submitting {label[task_type]} task...", file=sys.stderr)
    result = client.post(path, json=body)
    task_id = result["taskId"]
    if not quiet:
        print(f"Task submitted. taskId: {task_id}", file=sys.stderr)
    return task_id


def do_poll(client: TopviewClient, task_type: str, task_id: str,
            timeout: float, interval: float, quiet: bool) -> dict:
    """Poll until status is terminal or timeout is exceeded."""
    path = ENDPOINTS[task_type]["query"]
    if not quiet:
        print(
            f"Polling task {task_id} (timeout={timeout}s, interval={interval}s)...",
            file=sys.stderr,
        )
    return client.poll_task(
        path,
        task_id,
        interval=interval,
        timeout=timeout,
        verbose=not quiet,
    )


def download_video(url: str, output: str, quiet: bool) -> None:
    """Download a video from URL to a local file."""
    import requests as req

    if not quiet:
        print(f"Downloading video to {output}...", file=sys.stderr)

    resp = req.get(url, stream=True)
    resp.raise_for_status()

    with open(output, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    if not quiet:
        size_mb = os.path.getsize(output) / (1024 * 1024)
        print(f"Downloaded: {output} ({size_mb:.1f} MB)", file=sys.stderr)


def print_result(result: dict, args) -> None:
    """Print final result: video URLs by default, full JSON with --json."""
    videos = result.get("videos", [])

    if args.output_dir and videos:
        os.makedirs(args.output_dir, exist_ok=True)
        for i, v in enumerate(videos):
            if v.get("status") == "success" and v.get("filePath"):
                ext = "mp4"
                out_path = os.path.join(args.output_dir, f"video_{i+1}.{ext}")
                download_video(v["filePath"], out_path, args.quiet)

    if args.json:
        print(json_mod.dumps(result, indent=2, ensure_ascii=False))
    else:
        cost = result.get("costCredit", "N/A")
        print(f"status: {result.get('status')}  cost: {cost} credits")
        for i, v in enumerate(videos):
            status = v.get("status", "unknown")
            url = v.get("filePath", "")
            err = v.get("errorMsg", "")
            if status == "success":
                print(f"  [{i+1}] {url}")
            else:
                print(f"  [{i+1}] {status}: {err}")
    board_task_id = result.get("boardTaskId", "")
    board_id = result.get("boardId", "") or getattr(args, "board_id", "") or ""
    if board_task_id and board_id:
        print(f"  edit: https://www.topview.ai/board/{board_id}?boardResultId={board_task_id}")


# ---------------------------------------------------------------------------
# Argument definitions
# ---------------------------------------------------------------------------

def add_common_args(p):
    """Add arguments shared by all task types."""
    p.add_argument("--type", required=True, choices=TASK_TYPES,
                   help="Task type: i2v (image-to-video), t2v (text-to-video), omni (omni reference)")
    p.add_argument("--model", default=None,
                   help="Model name/ID (required for t2v and omni)")
    p.add_argument("--prompt", default=None,
                   help="Text prompt (required for t2v and omni)")
    p.add_argument("--aspect-ratio", default=None,
                   help='Aspect ratio, e.g. "16:9", "9:16", "1:1"')
    p.add_argument("--resolution", type=int, default=None, choices=[480, 540, 720, 768, 1080, 2160],
                   help="Resolution (model-dependent): 480, 540, 720, 768, 1080, or 2160")
    p.add_argument("--duration", type=int, default=None,
                   help="Video duration in seconds")
    p.add_argument("--count", type=int, default=None,
                   help="Number of videos to generate (1-4)")
    p.add_argument("--board-id", default=None,
                   help="Board ID for task organization")
    p.add_argument("--sound", default=None, choices=["on", "off"],
                   help='Native audio: "on"/"off". Only models with nativeAudio=True support this; may affect cost')


def add_i2v_args(p):
    """Add image-to-video specific arguments."""
    p.add_argument("--first-frame", default=None,
                   help="First frame image fileId or local path")
    p.add_argument("--end-frame", default=None,
                   help="End frame image fileId or local path")
    p.add_argument("--ref-images", nargs="+", default=None,
                   help="Reference image fileIds or local paths (multi-image mode, >=2)")


def add_omni_args(p):
    """Add omni-reference specific arguments."""
    p.add_argument("--input-images", default=None,
                   help='JSON array of input images, e.g. \'[{"fileId":"xxx","name":"Image1"}]\'')
    p.add_argument("--input-videos", default=None,
                   help='JSON array of input videos, e.g. \'[{"fileId":"xxx","name":"Video1"}]\'')
    p.add_argument("--internet-search", action="store_true",
                   help="Enable internet search for omni reference")


def add_poll_args(p):
    """Add polling control arguments."""
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                   help=f"Max polling time in seconds (default: {DEFAULT_TIMEOUT})")
    p.add_argument("--interval", type=float, default=DEFAULT_INTERVAL,
                   help=f"Polling interval in seconds (default: {DEFAULT_INTERVAL})")


def add_output_args(p):
    """Add output/download arguments."""
    p.add_argument("--output-dir", default=None,
                   help="Download result videos to this directory")
    p.add_argument("--json", action="store_true",
                   help="Output full JSON response")
    p.add_argument("-q", "--quiet", action="store_true",
                   help="Suppress status messages on stderr")


def validate_args(args, parser):
    """Validate type-specific required arguments."""
    if args.type == "t2v":
        if not args.model:
            parser.error("--model is required for text-to-video (t2v)")
        if not args.prompt:
            parser.error("--prompt is required for text-to-video (t2v)")
    elif args.type == "omni":
        if not args.model:
            parser.error("--model is required for omni reference")
        if not args.prompt:
            parser.error("--prompt is required for omni reference")
    elif args.type == "i2v":
        if not args.first_frame and not args.ref_images:
            parser.error("--first-frame or --ref-images is required for image-to-video (i2v)")


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------

def cmd_list_models(args, parser):
    """Print supported models and their parameter constraints."""
    task_type = args.type
    registry = MODEL_REGISTRY.get(task_type, {})
    if not registry:
        print(f"No models registered for type '{task_type}'.")
        return

    if args.json:
        print(json_mod.dumps(registry, indent=2, ensure_ascii=False))
        return

    type_label = {"i2v": "Image-to-Video", "t2v": "Text-to-Video", "omni": "Omni Reference"}
    print(f"\n{type_label.get(task_type, task_type)} — Supported Models\n")
    print(f"{'Model':<35} {'Aspect Ratio':<35} {'Resolution':<18} {'Duration':<12} {'Audio'}")
    print("-" * 120)
    for name, spec in registry.items():
        ar = ", ".join(spec["aspectRatio"]) if spec["aspectRatio"] else "by image" if task_type == "i2v" else "N/A"
        res = ", ".join(str(r) for r in spec["resolution"]) if spec["resolution"] else "N/A"
        dur = _parse_duration_spec(spec["duration"])
        audio = "Yes" if spec.get("nativeAudio") else "No"
        print(f"{name:<35} {ar:<35} {res:<18} {dur:<12} {audio}")
    print()


def cmd_estimate_cost(args, parser):
    """Print estimated cost for a given model + parameters."""
    sound_on = args.sound == "on" if args.sound else False
    cost = estimate_cost(args.model, args.resolution, args.duration, sound_on, args.count or 1)
    if cost is None:
        print(f"Cannot estimate cost for model '{args.model}' with given parameters.", file=sys.stderr)
        print("Use list-models to see available models, or check references/api-docs.md.", file=sys.stderr)
        sys.exit(1)
    count = args.count or 1
    unit = round(cost / count, 2)
    if args.json:
        print(json_mod.dumps({"model": args.model, "resolution": args.resolution,
                               "duration": args.duration, "sound": args.sound or "off",
                               "count": count, "unitCost": unit, "totalCost": cost}))
    else:
        print(f"model: {args.model}  resolution: {args.resolution or 'default'}  "
              f"duration: {args.duration}s  sound: {args.sound or 'off'}  count: {count}")
        print(f"estimated unit cost: {unit} credits")
        print(f"estimated total cost: {cost} credits")


def cmd_run(args, parser):
    """Submit task then poll until done — full flow (default)."""
    validate_args(args, parser)
    client = TopviewClient()
    body = build_body(args, client)
    task_id = do_submit(client, args.type, body, args.quiet)
    result = do_poll(client, args.type, task_id, args.timeout, args.interval, args.quiet)
    print_result(result, args)


def cmd_submit(args, parser):
    """Submit task only — print taskId and exit immediately."""
    validate_args(args, parser)
    client = TopviewClient()
    body = build_body(args, client)
    task_id = do_submit(client, args.type, body, args.quiet)
    print(task_id)


def cmd_query(args, parser):
    """Poll an existing task by taskId until done or timeout."""
    client = TopviewClient()
    try:
        result = do_poll(
            client, args.type, args.task_id,
            args.timeout, args.interval, args.quiet,
        )
        print_result(result, args)
    except TimeoutError as e:
        if not args.quiet:
            print(f"Timeout reached: {e}", file=sys.stderr)
            print("Fetching last known status...", file=sys.stderr)
        path = ENDPOINTS[args.type]["query"]
        last = client.get(path, params={"taskId": args.task_id})
        status = last.get("status", "unknown")
        task_id = last.get("taskId", args.task_id)
        if args.json:
            print(json_mod.dumps(last, indent=2, ensure_ascii=False))
        else:
            print(f"status: {status}  taskId: {task_id}", file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Topview Video Generation — i2v / t2v / omni reference.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
AGENT WORKFLOW RULES:
  1. ALWAYS start with `run` — it submits and polls automatically.
  2. Only use `query` if `run` timed out and you have a taskId to resume.
  3. `query` polls continuously (not once) until done or --timeout.
  4. NEVER hand a pending taskId back to the user — always poll to completion.

Task types:
  i2v   Image-to-Video V2  (first/end frame + prompt)
  t2v   Text-to-Video       (model + prompt, no image needed)
  omni  Omni Reference      (reference images/videos + prompt)

Examples:
  # List available models for a task type
  python video_gen.py list-models --type t2v

  # Image-to-video with first frame
  python video_gen.py run --type i2v --model "Seedance 1.5 Pro" \\
      --first-frame photo.png --prompt "A rotating product" --resolution 1080

  # Text-to-video
  python video_gen.py run --type t2v --model "Seedance 1.5 Pro" \\
      --prompt "A futuristic city" --aspect-ratio "16:9" --duration 5

  # Omni reference with image
  python video_gen.py run --type omni --model "Standard" \\
      --prompt "Transform <<<Image1>>> into watercolor animation" \\
      --input-images '[{"fileId":"file_abc","name":"Image1"}]'

  # Estimate cost before running
  python video_gen.py estimate-cost --model "Seedance 1.5 Pro" \\
      --resolution 1080 --duration 5 --sound on --count 2

  # Query a timed-out task
  python video_gen.py query --type i2v --task-id <taskId>
""",
    )

    sub = parser.add_subparsers(dest="subcommand")
    sub.required = True

    # -- run (default full flow) --
    p_run = sub.add_parser("run", help="[DEFAULT] Submit task and poll until done")
    add_common_args(p_run)
    add_i2v_args(p_run)
    add_omni_args(p_run)
    add_poll_args(p_run)
    add_output_args(p_run)

    # -- submit only --
    p_submit = sub.add_parser("submit", help="Submit task only, print taskId and exit")
    add_common_args(p_submit)
    add_i2v_args(p_submit)
    add_omni_args(p_submit)
    add_output_args(p_submit)

    # -- query / poll existing task --
    p_query = sub.add_parser("query", help="Poll existing taskId until done or timeout")
    p_query.add_argument("--type", required=True, choices=TASK_TYPES,
                         help="Task type (needed to select correct query endpoint)")
    p_query.add_argument("--task-id", required=True,
                         help="taskId returned by 'submit' or a previous 'run'")
    add_poll_args(p_query)
    add_output_args(p_query)

    # -- list-models --
    p_list = sub.add_parser("list-models", help="Show supported models and parameter constraints")
    p_list.add_argument("--type", required=True, choices=TASK_TYPES,
                        help="Task type to list models for")
    p_list.add_argument("--json", action="store_true",
                        help="Output as JSON")

    # -- estimate-cost --
    p_cost = sub.add_parser("estimate-cost", help="Estimate credit cost before running a task")
    p_cost.add_argument("--model", required=True, help="Model display name")
    p_cost.add_argument("--resolution", type=int, required=True, default="720", help="Resolution")
    p_cost.add_argument("--duration", type=int, required=True, help="Duration in seconds")
    p_cost.add_argument("--sound", default=None, choices=["on", "off"], help="Sound on/off")
    p_cost.add_argument("--count", type=int, required=True, default=1, help="generatingCount (1-4)")
    p_cost.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.subcommand == "run":
        cmd_run(args, p_run)
    elif args.subcommand == "submit":
        cmd_submit(args, p_submit)
    elif args.subcommand == "query":
        cmd_query(args, p_query)
    elif args.subcommand == "list-models":
        cmd_list_models(args, p_list)
    elif args.subcommand == "estimate-cost":
        cmd_estimate_cost(args, p_cost)


if __name__ == "__main__":
    main()