#!/usr/bin/env python3
"""
一键成片确定性渲染：TTS（含 audio_task_state）→ 切段 → 数字人 / AI 并行 poll →
以首条数字人轨 ffprobe 为参照封装 → ffmpeg 拼接。

通过子进程调用 chan-skills 内 chanjing-tts / chanjing-video-compose / chanjing-ai-creation
脚本；不调用 list_tasks。渲染规则以同技能包 templates/render_rules.md 为准；ref_prompt 见 templates/storyboard_prompt.md 与 history_storyboard_prompt.md（SKILL.md §4.2）；分镜字段见 storyboard_prompt.md；字段契约见 SKILL.md §5。
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable, Optional

_DEFAULT_OPENAPI_BASE = "https://open-api.chanjing.cc"


def openapi_base_url() -> str:
    return (
        os.environ.get("CHANJING_OPENAPI_BASE_URL")
        or os.environ.get("CHANJING_API_BASE")
        or _DEFAULT_OPENAPI_BASE
    ).rstrip("/")


def one_click_skills_repository_root() -> str:
    for key in (
        "SKILLS_DIR",
        "CHANJING_ONE_CLICK_VIDEO_SKILLS_ROOT",
        "CHAN_SKILLS_DIR",
    ):
        v = os.environ.get(key, "").strip()
        if v:
            return v
    return ""


def one_click_ref_prompt_max_chars() -> int:
    raw = os.environ.get("CHANJING_ONE_CLICK_VIDEO_REF_PROMPT_MAX_CHARS") or os.environ.get(
        "AI_VIDEO_PROMPT_MAX_CHARS", "8000"
    )
    return int(raw)


def one_click_ai_creation_model_code() -> Optional[str]:
    v = (
        os.environ.get("CHANJING_ONE_CLICK_VIDEO_CREATION_MODEL_CODE")
        or os.environ.get("AI_VIDEO_MODEL")
        or ""
    ).strip()
    return v or None


# 分镜连续合并为 TTS 批时的字符上限（低于接口 ~4000 字）；见 render_rules.md §3·C.4；编排见 SKILL.md §5、§9
TTS_BATCH_MAX = 3900
API_BASE = openapi_base_url()
DOWNLOAD_SEM = threading.BoundedSemaphore(2)


def norm_text(s: str) -> str:
    if not s:
        return ""
    return "".join(s.replace("\r", "").split())


def _ai_segment_direction(seg_index: int, seg_total: int) -> str:
    """
    同镜多段时：每段在内容取舍、视觉重点、运镜上与前后段区分；表述与题材无关，
    仅约束景别/叙事节奏层次，具体人、物、场景一律服从上层 base ref_prompt（英文）。
    seg_index 为 0-based。

    与 **`templates/storyboard_prompt.md`·D.1b**（易幻觉）冲突时以 **D.1b 与 base ref_prompt 为准**：
    本函数不得诱导可读界面/正文、精细指尖操作或强表演式面部特写。
    """
    if seg_total <= 1:
        return ""
    k = seg_index + 1
    n = seg_total
    blocks = [
        (
            f"[SHOT {k}/{n} — OPENING] CONTENT: Interpret the **base prompt** as a **wide contextual layer** — "
            "setting, space, time-of-day, palette, and overall situation; keep main subjects readable but **avoid** "
            "tight hero close-ups reserved for later clips. "
            "EMPHASIS: scale, environment, and \"where we are\"; must not copy tighter framings from later segments. "
            "CAMERA/LENS: extreme-wide or wide; stable tripod or very slow dolly-in; clear horizon / spatial depth; "
            "different screen direction than the next clip."
        ),
        (
            f"[SHOT {k}/{n} — PRIMARY ACTION] CONTENT: **Same world as the base prompt**, but show the **core activity** — "
            "interaction between people or with objects, movement through space, or the main beat the narration implies; "
            "**do not** repeat the opening clip's master composition or identical geography/blocking. "
            "EMPHASIS: readable mid-story information, relationships, or product-in-use style coverage (as fits the base prompt). "
            "CAMERA/LENS: medium and medium-wide; two-shots, over-shoulder, or following action; lateral move, gentle arc, "
            "or pan with movement; natural focal length for human scale (not macro)."
        ),
        (
            f"[SHOT {k}/{n} — DETAIL] CONTENT: **Inserts** implied by the base prompt — material textures, hands working "
            "on objects, mid-scale props and surfaces; **avoid** readable UI/screens/signage and readable documents; "
            "**not** another wide master like clip 1 or a repeat of clip 2's blocking. "
            "EMPHASIS: tactile clarity and simple filmable gestures; shallow focus where it helps; **avoid** extreme "
            "ECU on faces, micro-expressions, or fingertip-precision actions — if the base prompt already forbids these "
            "per project rules, **follow the base**. "
            "CAMERA/LENS: medium-close or close; slow micro-dolly or locked frame; slight high or low angle only if motivated; "
            "rack focus optional."
        ),
    ]
    if seg_index < len(blocks):
        return blocks[seg_index]
    return (
        f"[SHOT {k}/{n} — CONTRAST OUT] CONTENT: A **deliberately different** beat from earlier clips while staying "
        "faithful to the base prompt — e.g. negative space, quieter moment, opposite lighting direction, new axis, "
        "or summary image; must read as a **new chapter**, not a resized duplicate of a prior shot. "
        "EMPHASIS: mood shift or closing punctuation. "
        "CAMERA/LENS: return to wider coverage **only** on a new angle or location vs clip 1; slow pull-back, "
        "descending move, or long hold; Dutch angle only if still coherent with the base prompt."
    )


def build_ai_segment_prompt(base: str, seg_index: int, seg_total: int) -> str:
    """
    同镜多条文生视频：在 Agent 的 base ref_prompt 上，按段叠加**题材通用**的景别/节奏/运镜分层；
    具体人、物、时代、场景仅来自 base，不与某一类文案绑定。单段时仅用 base。
    追加层与 **`storyboard_prompt.md`·D.1b** 抵触时以 D.1b 与 base 为准。
    """
    base = (base or "").strip()
    max_total = one_click_ref_prompt_max_chars()
    extra = _ai_segment_direction(seg_index, seg_total)
    if not extra:
        return base[:max_total]
    sep = " || "
    room = max_total - len(extra) - len(sep) - 5
    if room < 120:
        trimmed = base[: max(0, max_total - len(extra) - len(sep))].rstrip()
    else:
        trimmed = base[:room].rstrip()
    out = trimmed + sep + extra
    return out[:max_total]


def repo_root_from_script() -> Path:
    # 仅当布局为 …/<repo>/skills/chanjing-one-click-video-creation/scripts/run_render.py 时，
    # 向上四级为 <repo>（与 SKILLS_DIR / CHANJING_ONE_CLICK_VIDEO_SKILLS_ROOT / CHAN_SKILLS_DIR 指向的根一致）。
    return Path(__file__).resolve().parent.parent.parent.parent


def normalize_chan_skills_repo_root(p: Path) -> Path:
    """
    环境变量语义易混：SKILLS_DIR 既可能被设为「仓库根」（…/chan-skills），也可能被设为
    「skills 子目录」（…/chan-skills/skills）。script_path() 需要前者。若检测到后者则上溯一级。
    """
    p = p.expanduser().resolve()
    marker = p / "skills" / "chanjing-tts" / "scripts"
    if marker.is_dir() or (p / "skills" / "chanjing-tts").is_dir():
        return p
    if p.name == "skills" and (p / "chanjing-tts" / "scripts").is_dir():
        return p.parent
    return p


def resolve_chan_skills_dir() -> Path:
    env = one_click_skills_repository_root()
    if env:
        return normalize_chan_skills_repo_root(Path(env))
    return repo_root_from_script()


def script_path(root: Path, skill: str, name: str) -> Path:
    return root / "skills" / skill / "scripts" / name


def require_bin(name: str) -> None:
    from shutil import which

    if not which(name):
        raise SystemExit(f"缺少可执行文件: {name}（请安装并加入 PATH）")


def run_subprocess(
    argv: list[str], *, timeout: int = 900, env: Optional[dict] = None
) -> str:
    r = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, **(env or {})},
    )
    if r.returncode != 0:
        msg = (r.stderr or r.stdout or "").strip() or f"exit {r.returncode}"
        raise RuntimeError(msg)
    return (r.stdout or "").strip()


def with_retry(fn: Callable[[], Any], retries: int) -> Any:
    last: Optional[Exception] = None
    for _ in range(max(0, retries) + 1):
        try:
            return fn()
        except Exception as e:
            last = e
            time.sleep(1.0)
    assert last is not None
    raise last


def import_tts_get_token(root: Path):
    p = str(script_path(root, "chanjing-tts", "_auth.py").parent)
    if p not in sys.path:
        sys.path.insert(0, p)
    from _auth import get_token  # type: ignore

    return get_token


def fetch_audio_task_state(token: str, task_id: str) -> dict[str, Any]:
    url = f"{API_BASE}/open/v1/audio_task_state"
    body = json.dumps({"task_id": task_id}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"access_token": token, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def poll_tts_state(
    get_token, task_id: str, interval: int = 3
) -> dict[str, Any]:
    while True:
        token, err = get_token()
        if err:
            raise RuntimeError(err)
        res = fetch_audio_task_state(token, task_id)
        if res.get("code") != 0:
            raise RuntimeError(res.get("msg", str(res)))
        data = res.get("data") or {}
        status = data.get("status")
        if status == 9:
            return data
        if status not in (1, None):
            raise RuntimeError(
                data.get("errMsg") or data.get("errReason") or f"TTS status={status}"
            )
        time.sleep(interval)


def download_url(url: str, dest: Path) -> None:
    with DOWNLOAD_SEM:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=300) as resp:
            dest.write_bytes(resp.read())


def ffprobe_duration(path: Path) -> float:
    out = run_subprocess(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        timeout=120,
    )
    return float(out.strip())


def ffprobe_json(path: Path) -> dict[str, Any]:
    out = run_subprocess(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,r_frame_rate,avg_frame_rate,pix_fmt,codec_name",
            "-show_entries",
            "stream_tags=rotate",
            "-of",
            "json",
            str(path),
        ],
        timeout=120,
    )
    return json.loads(out)


# 与 chanjing-ai-creation submit_task --aspect-ratio 说明一致（过宽则映射失败）
API_VIDEO_ASPECT_RATIOS: dict[str, float] = {
    "9:16": 9 / 16,
    "16:9": 16 / 9,
    "1:1": 1.0,
    "3:4": 3 / 4,
    "4:3": 4 / 3,
}


def display_size_from_stream(st: dict[str, Any]) -> tuple[int, int]:
    """编码宽高 + 常见 rotate 元数据 → 观众看到的宽高（竖屏以 h>w 为常态）。"""
    w = int(st.get("width") or 1080)
    h = int(st.get("height") or 1920)
    tags = st.get("tags") or {}
    rot = tags.get("rotate")
    if rot is None:
        return w, h
    try:
        ang = int(str(rot).strip())
    except ValueError:
        return w, h
    if ang % 180 == 90:
        return h, w
    return w, h


def ref_to_ai_submit_params(ref: dict[str, Any]) -> tuple[str, int]:
    """
    由数字人参照轨的显示宽高映射文生视频 API 的 aspect_ratio、clarity，
    避免横竖与清晰度与数字人不一致导致后期旋转/强裁。
    """
    w0, h0 = int(ref["width"]), int(ref["height"])
    w, h = min(w0, h0), max(w0, h0)
    r = w / h if h else 9 / 16
    best_label, best_val = min(
        API_VIDEO_ASPECT_RATIOS.items(), key=lambda kv: abs(kv[1] - r)
    )
    if abs(best_val - r) > 0.04:
        raise SystemExit(
            "数字人显示宽高比与文生 API 支持的 aspect_ratio 偏差过大（"
            f"显示约 {w0}×{h0}，比例≈{r:.4f}）；请确认公共数字人成片或换用支持的画幅。"
        )
    short = w
    if short >= 1000:
        clarity = 1080
    elif short >= 660:
        clarity = 720
    else:
        raise SystemExit(
            f"数字人短边 {short}px 无法映射到文生 clarity 720/1080；请换形象或联系接口文档。"
        )
    return best_label, clarity


def parse_fps(frac: str) -> float:
    if not frac or frac == "0/0":
        return 30.0
    if "/" in frac:
        a, b = frac.split("/", 1)
        return float(a) / float(b) if float(b) else 30.0
    return float(frac)


def default_ref() -> dict[str, Any]:
    return {
        "width": 1080,
        "height": 1920,
        "fps": 30.0,
        "pix_fmt": "yuv420p",
        "a_rate": 48000,
    }


def probe_ref_video(path: Path) -> dict[str, Any]:
    data = ffprobe_json(path)
    streams = data.get("streams") or []
    if not streams:
        return default_ref()
    st = streams[0]
    w, h = display_size_from_stream(st)
    fps = parse_fps(st.get("r_frame_rate") or st.get("avg_frame_rate") or "30/1")
    pix = st.get("pix_fmt") or "yuv420p"
    return {"width": w, "height": h, "fps": fps, "pix_fmt": pix, "a_rate": 48000}


def _infer_subtitle_scale(subs: list[dict], audio_duration: float) -> float:
    if not subs or audio_duration <= 0:
        return 1.0
    max_end = max(float(s.get("end_time", 0)) for s in subs)
    if max_end > audio_duration * 2.0 and max_end > 2000:
        return 0.001
    return 1.0


def merge_subtitles_with_offset(
    subs: list[dict], offset_sec: float, scale: float
) -> list[dict]:
    out = []
    for s in subs:
        out.append(
            {
                "start_time": float(s.get("start_time", 0)) * scale + offset_sec,
                "end_time": float(s.get("end_time", 0)) * scale + offset_sec,
                "subtitle": s.get("subtitle", "") or "",
            }
        )
    return out


def compute_scene_times(
    scenes: list[dict],
    full_script: str,
    subtitles: list[dict],
    total_duration: float,
) -> tuple[list[tuple[float, float]], str]:
    """返回每镜 (t_start, t_end) 与 align_quality：high | low_prop。"""
    scenes = sorted(scenes, key=lambda x: int(x["scene_id"]))
    full_n = norm_text(full_script)
    subs_sorted = sorted(subtitles, key=lambda x: float(x["start_time"]))
    sub_blob = norm_text("".join(s.get("subtitle", "") for s in subs_sorted))
    total_chars = sum(max(1, len(norm_text(s["voiceover"]))) for s in scenes)

    def proportional() -> tuple[list[tuple[float, float]], str]:
        times = []
        t = 0.0
        for sc in scenes:
            w = max(1, len(norm_text(sc["voiceover"])))
            seg = total_duration * (w / total_chars) if total_chars else total_duration / len(scenes)
            times.append((t, min(t + seg, total_duration)))
            t += seg
        if times:
            times[-1] = (times[-1][0], total_duration)
        return times, "low_prop"

    if not full_n or total_duration <= 0:
        return proportional()

    if sub_blob != full_n:
        return proportional()

    # merge_subtitles_with_offset 已将时间转为秒
    char_times: list[float] = []
    for sub in subs_sorted:
        st = float(sub["start_time"])
        et = float(sub["end_time"])
        txt = norm_text(sub.get("subtitle", ""))
        if not txt:
            continue
        L = len(txt)
        for i in range(L):
            if L <= 1:
                char_times.append((st + et) / 2.0)
            else:
                char_times.append(st + (et - st) * i / (L - 1))
    if len(char_times) != len(sub_blob):
        return proportional()

    times: list[tuple[float, float]] = []
    pos = 0
    for sc in scenes:
        v = norm_text(sc["voiceover"])
        Lv = len(v)
        if Lv == 0:
            if not char_times:
                times.append((0.0, 0.0))
            else:
                idx = min(pos, len(char_times) - 1)
                tt = char_times[idx]
                times.append((tt, tt))
            continue
        if pos + Lv > len(char_times):
            return proportional()
        t0 = char_times[pos]
        t1 = char_times[pos + Lv - 1]
        times.append((max(0.0, t0), min(total_duration, t1 + 0.05)))
        pos += Lv
    if pos != len(char_times):
        return proportional()
    return times, "high"


def group_scene_batches(scenes_sorted: list[dict]) -> list[list[dict]]:
    batches: list[list[dict]] = []
    cur: list[dict] = []
    cur_len = 0
    for sc in scenes_sorted:
        v = sc.get("voiceover") or ""
        if cur_len + len(v) > TTS_BATCH_MAX and cur:
            batches.append(cur)
            cur = []
            cur_len = 0
        cur.append(sc)
        cur_len += len(v)
    if cur:
        batches.append(cur)
    return batches


def ffmpeg_concat_audio_files(paths: list[Path], out: Path) -> None:
    lst = out.parent / f"{out.stem}_audio_concat.txt"
    lines = []
    for p in paths:
        lines.append(f"file '{p.resolve()}'")
    lst.write_text("\n".join(lines), encoding="utf-8")
    run_subprocess(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(lst),
            "-c",
            "copy",
            str(out),
        ],
        timeout=600,
    )


def ffmpeg_cut_audio(src: Path, t0: float, t1: float, out_wav: Path) -> None:
    dur = max(0.01, t1 - t0)
    run_subprocess(
        [
            "ffmpeg",
            "-y",
            "-ss",
            str(t0),
            "-i",
            str(src),
            "-t",
            str(dur),
            "-ac",
            "1",
            "-ar",
            "24000",
            "-sample_fmt",
            "s16",
            str(out_wav),
        ],
        timeout=300,
    )


def h264_args() -> list[str]:
    if sys.platform == "darwin":
        return ["-c:v", "h264_videotoolbox", "-b:v", "8M"]
    return ["-c:v", "libx264", "-crf", "23", "-preset", "medium"]


def normalize_video_to_ref(
    src: Path,
    dst: Path,
    ref: dict[str, Any],
    *,
    with_audio: bool,
) -> None:
    w, h = ref["width"], ref["height"]
    fps = ref["fps"]
    vf = (
        f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
        f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps},format=yuv420p"
    )
    cmd = ["ffmpeg", "-y", "-i", str(src), "-vf", vf, *h264_args()]
    if with_audio:
        cmd.extend(
            ["-c:a", "aac", "-ar", str(ref["a_rate"]), "-ac", "2", str(dst)]
        )
    else:
        cmd.extend(["-an", str(dst)])
    run_subprocess(cmd, timeout=900)


def concat_videos_reencode(inputs: list[Path], out: Path) -> None:
    lst = out.parent / f"{out.stem}_vconcat.txt"
    lst.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in inputs), encoding="utf-8"
    )
    run_subprocess(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(lst),
            *h264_args(),
            "-an",
            str(out),
        ],
        timeout=900,
    )


def mux_video_audio(video: Path, audio: Path, out: Path, ref: dict[str, Any]) -> None:
    """
    将无音轨文生片段与当镜口播 wav 合成。禁止 -shortest：平台返回的视频时长常短于口播，
    否则会截断该镜 narration，拼接后表现为「话没说完就断」。
    视频长于音频时按口播时长裁切；短于音频时用末帧垫长到与口播一致。
    """
    v_dur = ffprobe_duration(video)
    a_dur = ffprobe_duration(audio)
    ar = str(ref["a_rate"])
    eps = 0.08
    if v_dur + eps >= a_dur:
        run_subprocess(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(video),
                "-i",
                str(audio),
                "-t",
                str(a_dur),
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-ar",
                ar,
                "-ac",
                "2",
                str(out),
            ],
            timeout=600,
        )
        return
    pad = max(0.05, a_dur - v_dur + 0.02)
    fc = f"[0:v]tpad=stop_mode=clone:stop_duration={pad:.3f}[v]"
    cmd: list[str] = [
        "ffmpeg",
        "-y",
        "-i",
        str(video),
        "-i",
        str(audio),
        "-filter_complex",
        fc,
        "-map",
        "[v]",
        "-map",
        "1:a:0",
        "-t",
        str(a_dur),
    ]
    cmd.extend(h264_args())
    cmd.extend(
        [
            "-c:a",
            "aac",
            "-ar",
            ar,
            "-ac",
            "2",
            str(out),
        ]
    )
    run_subprocess(cmd, timeout=600)


def run_tts_pipeline(
    root: Path,
    batches: list[list[dict]],
    audio_man: str,
    speed: float,
    pitch: float,
    retries: int,
    work: Path,
) -> tuple[Path, list[dict], list[str]]:
    tts_create = script_path(root, "chanjing-tts", "create_task.py")
    get_token = import_tts_get_token(root)
    mp3_parts: list[Path] = []
    merged_subs: list[dict] = []
    offset = 0.0
    task_ids: list[str] = []
    batch_states: list[dict[str, Any]] = []

    for bi, batch_scenes in enumerate(batches):
        text = "".join(s.get("voiceover", "") for s in batch_scenes)
        if len(text) > 4000:
            raise ValueError(f"TTS 批次 {bi} 超过 4000 字，请调整分镜合并")

        def _create() -> str:
            return run_subprocess(
                [
                    sys.executable,
                    str(tts_create),
                    "--audio-man",
                    audio_man,
                    "--text",
                    text,
                    "--speed",
                    str(speed),
                    "--pitch",
                    str(pitch),
                ]
            )

        task_id = with_retry(_create, retries)
        task_ids.append(task_id)
        data = with_retry(lambda: poll_tts_state(get_token, task_id), retries)
        batch_states.append(dict(data))
        full = data.get("full") or {}
        url = full.get("url")
        if not url:
            raise RuntimeError("TTS 完成但无 full.url")
        raw = work / f"tts_batch_{bi}.mp3"
        download_url(url, raw)
        dur = ffprobe_duration(raw)
        subs = data.get("subtitles") or []
        scale = _infer_subtitle_scale(subs, dur)
        merged_subs.extend(merge_subtitles_with_offset(subs, offset, scale))
        offset += dur
        mp3_parts.append(raw)

    merged_mp3 = work / "tts_merged.mp3"
    if len(mp3_parts) == 1:
        merged_mp3.write_bytes(mp3_parts[0].read_bytes())
    else:
        ffmpeg_concat_audio_files(mp3_parts, merged_mp3)

    state_path = work / "tts_state.json"
    state_path.write_text(
        json.dumps(
            {
                "task_ids": task_ids,
                "subtitles": merged_subs,
                "batches_audio_task_state": batch_states,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return merged_mp3, merged_subs, task_ids


def poll_compose(root: Path, video_id: str) -> str:
    poll = script_path(root, "chanjing-video-compose", "poll_task.py")
    return run_subprocess(
        [sys.executable, str(poll), "--id", video_id, "--interval", "10"],
        timeout=3600,
    )


def poll_ai(root: Path, uid: str) -> str:
    poll = script_path(root, "chanjing-ai-creation", "poll_task.py")
    return run_subprocess(
        [sys.executable, str(poll), "--unique-id", uid, "--interval", "10"],
        timeout=3600,
    )


def run_dh_create_job(
    upload: Path,
    compose_create: Path,
    person_id: str,
    figure_type: Optional[str],
    wav_path: Path,
    retries: int,
    subtitle: str = "hide",
    subtitle_color: Optional[str] = None,
    subtitle_stroke_color: Optional[str] = None,
    subtitle_stroke_width: Optional[int] = None,
) -> str:
    """上传切段音频并创建数字人视频任务，返回 video 任务 id（stdout）。"""

    def _up() -> str:
        return run_subprocess(
            [
                sys.executable,
                str(upload),
                "--service",
                "make_video_audio",
                "--file",
                str(wav_path),
            ]
        )

    fid = with_retry(_up, retries)
    sub = "show" if subtitle == "show" else "hide"
    cargs = [
        sys.executable,
        str(compose_create),
        "--person-id",
        person_id,
        "--audio-file-id",
        fid,
        "--subtitle",
        sub,
    ]
    if figure_type:
        cargs.extend(["--figure-type", figure_type])
    if sub == "show":
        if subtitle_color:
            cargs.extend(["--subtitle-color", subtitle_color])
        if subtitle_stroke_color:
            cargs.extend(["--subtitle-stroke-color", subtitle_stroke_color])
        if subtitle_stroke_width is not None:
            cargs.extend(["--subtitle-stroke-width", str(subtitle_stroke_width)])

    def _ct() -> str:
        return run_subprocess(cargs)

    return with_retry(_ct, retries)


def main() -> None:
    parser = argparse.ArgumentParser(description="chanjing-one-click-video-creation 确定性成片")
    parser.add_argument("--input", required=True, help="workflow JSON 路径")
    parser.add_argument("--output-dir", required=True, help="输出目录")
    args = parser.parse_args()

    require_bin("ffmpeg")
    require_bin("ffprobe")

    root = resolve_chan_skills_dir()
    inp = Path(args.input).resolve()
    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    work = out_dir / "work"
    work.mkdir(parents=True, exist_ok=True)

    data = json.loads(inp.read_text(encoding="utf-8"))
    full_script = (data.get("full_script") or "").strip()
    if not full_script:
        for k in ("script", "copy_text", "input_script", "content"):
            v = data.get(k)
            if v:
                full_script = str(v).strip()
                break
    scenes = data.get("scenes")
    if not full_script or not isinstance(scenes, list) or not scenes:
        raise SystemExit("输入 JSON 须含 full_script 与 scenes[]")

    scenes_sorted = sorted(scenes, key=lambda x: int(x["scene_id"]))
    joined = "".join(s.get("voiceover", "") for s in scenes_sorted)
    if norm_text(joined) != norm_text(full_script):
        raise SystemExit("各镜 voiceover 拼接后与 full_script 在 norm 意义下须一致")

    audio_man = (data.get("audio_man") or "").strip()
    if not audio_man:
        raise SystemExit("缺少 audio_man")
    person_id = (data.get("person_id") or data.get("avatar_id") or "").strip()
    figure_type = (data.get("figure_type") or "").strip() or None
    speed = float(data.get("speed", 1))
    pitch = float(data.get("pitch", 1))
    retries = int(data.get("max_retry_per_step", 1))
    ai_seg = int(data.get("ai_video_duration_sec", 10))
    if ai_seg not in (5, 10):
        ai_seg = 10
    model_code = (
        data.get("model_code")
        or one_click_ai_creation_model_code()
        or "Doubao-Seedance-1.0-pro"
    )

    dh_subtitle = "show" if data.get("subtitle_required") else "hide"
    sub_color = (data.get("subtitle_color") or "").strip() or None
    sub_stroke_color = (data.get("subtitle_stroke_color") or "").strip() or None
    _sw = data.get("subtitle_stroke_width")
    sub_stroke_width = int(_sw) if _sw is not None and str(_sw).strip() != "" else None

    need_dh = any(s.get("use_avatar") for s in scenes_sorted)
    if need_dh and not person_id:
        raise SystemExit("存在数字人镜时须提供 person_id 或 avatar_id")

    for s in scenes_sorted:
        if not s.get("use_avatar") and not (s.get("ref_prompt") or "").strip():
            raise SystemExit(f"scene {s.get('scene_id')} 为 AI 镜但缺少 ref_prompt")

    result: dict[str, Any] = {
        "status": "failed",
        "align_quality": None,
        "render_result": {"video_file": None, "scene_video_urls": {}},
        "debug": {
            "tts_task_ids": [],
            "dh_video_ids": {},
            "ai_unique_ids": {},
            "intermediate_paths": {},
        },
    }

    try:
        batches = group_scene_batches(scenes_sorted)
        merged_mp3, merged_subs, tts_ids = run_tts_pipeline(
            root, batches, audio_man, speed, pitch, retries, work
        )
        result["debug"]["tts_task_ids"] = tts_ids
        result["debug"]["intermediate_paths"]["tts_merged_mp3"] = str(merged_mp3)
        result["debug"]["intermediate_paths"]["tts_state_json"] = str(
            work / "tts_state.json"
        )

        total_dur = ffprobe_duration(merged_mp3)
        scene_times, align_q = compute_scene_times(
            scenes_sorted, full_script, merged_subs, total_dur
        )
        result["align_quality"] = align_q
        st_path = work / "scene_times.json"
        st_path.write_text(
            json.dumps(
                [
                    {
                        "scene_id": int(sc["scene_id"]),
                        "t_start": scene_times[i][0],
                        "t_end": scene_times[i][1],
                    }
                    for i, sc in enumerate(scenes_sorted)
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        result["debug"]["intermediate_paths"]["scene_times_json"] = str(st_path)

        # 切段 wav
        scene_wavs: dict[int, Path] = {}
        for i, sc in enumerate(scenes_sorted):
            sid = int(sc["scene_id"])
            t0, t1 = scene_times[i]
            wav = work / f"scene{sid:02d}_drive.wav"
            ffmpeg_cut_audio(merged_mp3, t0, t1, wav)
            scene_wavs[sid] = wav

        upload = script_path(root, "chanjing-video-compose", "upload_file.py")
        compose_create = script_path(root, "chanjing-video-compose", "create_task.py")
        ai_submit = script_path(root, "chanjing-ai-creation", "submit_task.py")

        first_dh_sid: Optional[int] = next(
            (int(s["scene_id"]) for s in scenes_sorted if s.get("use_avatar")),
            None,
        )
        has_ai = any(not s.get("use_avatar") for s in scenes_sorted)

        url_dh: dict[int, str] = {}
        dh_files: dict[int, Path] = {}
        ref_for_normalize: Optional[dict[str, Any]] = None

        # 有 AI 镜时：先完成首条数字人 → ffprobe（含 rotate）→ 再提交文生，使 API 画幅与公共数字人一致
        if has_ai and first_dh_sid is not None:
            wav0 = scene_wavs[first_dh_sid]
            vid0 = run_dh_create_job(
                upload,
                compose_create,
                person_id,
                figure_type,
                wav0,
                retries,
                dh_subtitle,
                subtitle_color=sub_color,
                subtitle_stroke_color=sub_stroke_color,
                subtitle_stroke_width=sub_stroke_width,
            )
            result["debug"]["dh_video_ids"][str(first_dh_sid)] = vid0
            u0 = with_retry(lambda: poll_compose(root, vid0), retries)
            url_dh[first_dh_sid] = u0
            result["render_result"]["scene_video_urls"][f"dh_{first_dh_sid}"] = u0
            p0 = work / f"scene{first_dh_sid:02d}_dh_raw.mp4"
            download_url(u0, p0)
            dh_files[first_dh_sid] = p0
            ref_for_normalize = probe_ref_video(p0)
        elif has_ai:
            ref_for_normalize = default_ref()

        if has_ai:
            assert ref_for_normalize is not None
            ai_aspect_ratio, ai_clarity = ref_to_ai_submit_params(ref_for_normalize)
        else:
            ai_aspect_ratio, ai_clarity = "9:16", 1080

        result["debug"]["ai_video_submit_params"] = {
            "aspect_ratio": ai_aspect_ratio,
            "clarity": ai_clarity,
            "ref_width": ref_for_normalize["width"] if ref_for_normalize else None,
            "ref_height": ref_for_normalize["height"] if ref_for_normalize else None,
        }

        dh_jobs: dict[int, str] = {}
        ai_jobs: dict[tuple[int, int], str] = {}

        for i, sc in enumerate(scenes_sorted):
            sid = int(sc["scene_id"])
            if sc.get("use_avatar"):
                if has_ai and sid == first_dh_sid:
                    continue
                vid = run_dh_create_job(
                    upload,
                    compose_create,
                    person_id,
                    figure_type,
                    scene_wavs[sid],
                    retries,
                    dh_subtitle,
                    subtitle_color=sub_color,
                    subtitle_stroke_color=sub_stroke_color,
                    subtitle_stroke_width=sub_stroke_width,
                )
                dh_jobs[sid] = vid
                result["debug"]["dh_video_ids"][str(sid)] = vid
            else:
                t0, t1 = scene_times[i]
                dur = max(0.1, t1 - t0)
                n = max(1, math.ceil(dur / ai_seg))
                prompt = (sc.get("ref_prompt") or "").strip()
                for k in range(n):
                    ptext = build_ai_segment_prompt(prompt, k, n)

                    def _sub(ptext=ptext) -> str:
                        return run_subprocess(
                            [
                                sys.executable,
                                str(ai_submit),
                                "--creation-type",
                                "4",
                                "--model-code",
                                str(model_code),
                                "--prompt",
                                ptext,
                                "--aspect-ratio",
                                ai_aspect_ratio,
                                "--clarity",
                                str(ai_clarity),
                                "--video-duration",
                                str(ai_seg),
                            ]
                        )

                    uid = with_retry(_sub, retries)
                    ai_jobs[(sid, k)] = uid
                    result["debug"]["ai_unique_ids"][f"{sid}_{k}"] = uid

        # 并行 poll（首条数字人已在上方单独 poll）
        url_ai: dict[tuple[int, int], str] = {}

        def run_polls() -> None:
            futs = []
            with ThreadPoolExecutor(max_workers=4) as ex:
                for sid, vid in dh_jobs.items():
                    futs.append(
                        (("dh", sid), ex.submit(poll_compose, root, vid))
                    )
                for key, uid in ai_jobs.items():
                    futs.append((("ai", key), ex.submit(poll_ai, root, uid)))
                for tag, fut in futs:
                    u = fut.result()
                    if tag[0] == "dh":
                        url_dh[int(tag[1])] = u
                    else:
                        url_ai[tag[1]] = u

        with_retry(run_polls, retries)

        for sid, u in url_dh.items():
            result["render_result"]["scene_video_urls"][f"dh_{sid}"] = u
        for (sid, k), u in url_ai.items():
            result["render_result"]["scene_video_urls"][f"ai_{sid}_{k}"] = u

        # 下载（首条数字人已落盘）
        ai_files: dict[tuple[int, int], Path] = {}

        for sid, u in sorted(url_dh.items()):
            if sid in dh_files:
                continue
            p = work / f"scene{sid:02d}_dh_raw.mp4"
            download_url(u, p)
            dh_files[sid] = p

        ref: dict[str, Any]
        if ref_for_normalize is not None:
            ref = ref_for_normalize
        else:
            ref = None
            for sid in sorted(dh_files.keys()):
                ref = probe_ref_video(dh_files[sid])
                break
            if ref is None:
                ref = default_ref()

        for (sid, k), u in sorted(url_ai.items()):
            p = work / f"scene{sid:02d}_ai_part{k}.mp4"
            download_url(u, p)
            ai_files[(sid, k)] = p

        norm_segments: list[Path] = []

        for sc in scenes_sorted:
            sid = int(sc["scene_id"])
            if sc.get("use_avatar"):
                src = dh_files[sid]
                dst = work / f"scene{sid:02d}_dh_norm.mp4"
                normalize_video_to_ref(src, dst, ref, with_audio=True)
                norm_segments.append(dst)
            else:
                keys = sorted(
                    (x for x in ai_files if x[0] == sid), key=lambda x: x[1]
                )
                parts_norm = []
                for kk, key in enumerate(keys):
                    raw = ai_files[key]
                    pn = work / f"scene{sid:02d}_ai_p{kk}_norm.mp4"
                    normalize_video_to_ref(raw, pn, ref, with_audio=False)
                    parts_norm.append(pn)
                concat_noa = work / f"scene{sid:02d}_ai_t2v_concat_noaudio.mp4"
                concat_videos_reencode(parts_norm, concat_noa)
                muxed = work / f"scene{sid:02d}_ai_mux.mp4"
                mux_video_audio(concat_noa, scene_wavs[sid], muxed, ref)
                norm_seg = work / f"scene{sid:02d}_ai_final_norm.mp4"
                normalize_video_to_ref(muxed, norm_seg, ref, with_audio=True)
                norm_segments.append(norm_seg)

        final_list = work / "final_concat.txt"
        final_list.write_text(
            "\n".join(f"file '{p.resolve()}'" for p in norm_segments),
            encoding="utf-8",
        )
        final_mp4 = out_dir / "final_one_click.mp4"
        run_subprocess(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(final_list),
                *h264_args(),
                "-c:a",
                "aac",
                "-ar",
                str(ref["a_rate"]),
                str(final_mp4),
            ],
            timeout=3600,
        )

        result["status"] = "success"
        result["render_result"]["video_file"] = str(final_mp4)
        result["debug"]["intermediate_paths"]["final_concat_list"] = str(final_list)

    except BaseException as exc:
        result["status"] = "partial"
        result["error"] = str(exc)

    out_json = out_dir / "workflow_result.json"
    out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if result["status"] != "success":
        raise SystemExit(result.get("error") or "成片失败，见 workflow_result.json")


if __name__ == "__main__":
    main()
