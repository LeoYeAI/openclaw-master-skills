#!/usr/bin/env python3
"""Video overlay V2: High-performance FFmpeg-native compositing.

Uses FFmpeg filter_complex to perform stacking/overlaying, keeping video
data out of Python. Python only generates the 10fps graph sequence.
"""
import os
os.environ.setdefault('PYTHONNOUSERSITE', '1')

import sys

# Re-exec with clean env if user-site packages are active (same as v7)
if 'site' in sys.modules:
    import site
    if getattr(site, 'ENABLE_USER_SITE', False) and os.environ.get('_OVERLAY_REEXEC') != '1':
        env = os.environ.copy()
        env['PYTHONNOUSERSITE'] = '1'
        env['_OVERLAY_REEXEC'] = '1'
        os.execvpe(sys.executable, [sys.executable] + sys.argv, env)

# Prevent v7 module-level re-exec when imported
os.environ['_GAGGIUINO_GRAPH_REEXEC'] = '1'

import argparse
import json
import math
import shutil
import subprocess
from typing import Any, Dict

import numpy as np

# Import graph renderer from same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_shot_graph import ContextRenderer, load_shot_from_id, load_shot_from_file

import matplotlib.pyplot as plt


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_video_info(path: str) -> Dict[str, Any]:
    """Get video metadata via ffprobe."""
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json',
           '-show_streams', '-show_format', path]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    for stream in data['streams']:
        if stream['codec_type'] == 'video':
            w = int(stream['width'])
            h = int(stream['height'])
            
            # Rotation detection (FFmpeg auto-rotates by default in filters)
            rotation = 0
            for side_data in stream.get('side_data_list', []):
                if 'rotation' in side_data:
                    rotation = int(side_data['rotation'])
            
            # Fallback for older ffprobe
            if not rotation:
                rotation = int(stream.get('tags', {}).get('rotate', 0))
                
            if abs(rotation) in (90, 270):
                # FFmpeg will display it as rotated, so we swap for layout logic
                w, h = h, w
                
            parts = stream['r_frame_rate'].split('/')
            num, den = int(parts[0]), int(parts[1]) if len(parts) > 1 else 1
            fps = num / den if den else 30.0
            dur = float(stream.get('duration', 0)) or float(data['format'].get('duration', 0))
            return {'width': w, 'height': h, 'fps': fps, 'duration': dur}
    raise RuntimeError(f'No video stream found in {path}')


def _even(n: int) -> int:
    """Round down to nearest even integer."""
    return n - (n % 2)


# ─── Main pipeline ───────────────────────────────────────────────────────────

def render_overlay_v2(shot: Dict[str, Any], video_path: str, out_path: str,
                    offset: float = 0.0, alpha: float = 0.65,
                    position: str = 'top', graph_fps: int = 10) -> Dict[str, Any]:
    """Composite graph animation onto user video using FFmpeg filters.

    Python only outputs the 10fps graph sequence. FFmpeg handles the heavy lifting.
    """
    if not shutil.which('ffmpeg'):
        raise RuntimeError('ffmpeg not found in PATH')
    if not shutil.which('ffprobe'):
        raise RuntimeError('ffprobe not found in PATH')

    # ── Video info ──
    vinfo = get_video_info(video_path)
    vid_w = _even(vinfo['width'])
    vid_h = _even(vinfo['height'])
    vid_fps = vinfo['fps']
    vid_duration = vinfo['duration']
    is_landscape = vid_w >= vid_h

    # ── Graph renderer ──
    renderer = ContextRenderer(shot)
    graph_w, graph_h = renderer.out_w, renderer.out_h
    graph_duration = renderer.duration
    
    # Calc scaled graph height for filter string
    scaled_graph_h = _even(int(graph_h * (vid_w / graph_w))) if graph_w else 0

    # ── Timing & Padding ──
    # Total frames to output from Python at graph_fps
    # We must match the full video duration
    total_output_frames = max(1, int(vid_duration * graph_fps))
    
    # ── Start encoder with complex filter ──
    # [0:v] is the 10fps pipe, [1:v] is the original video
    # ── Start encoder with complex filter ──
    # [0:v] is the 10fps rawvideo pipe from Python
    # [1:v] is the original user video (source)
    # Both are forced to vid_fps (Constant Frame Rate) to avoid sync-drift
    
    if is_landscape:
        # vstack: Scale graph to vid_w, move to target fps and format.
        filter_complex = (
            f'[0:v]scale={vid_w}:{scaled_graph_h},fps=fps={vid_fps},format=yuv420p[g];'
            f'[1:v]fps=fps={vid_fps},format=yuv420p[v];'
            f'[g][v]vstack'
        )
    else:
        # overlay: Scale graph to vid_w, set alpha, and overlay at top or bottom.
        y_pos = 0 if position == 'top' else vid_h - scaled_graph_h
        filter_complex = (
            f'[0:v]scale={vid_w}:{scaled_graph_h},fps=fps={vid_fps},format=rgba,colorchannelmixer=aa={alpha}[g];'
            f'[1:v]fps=fps={vid_fps},format=yuv420p[v];'
            f'[v][g]overlay=x=0:y={y_pos}'
        )

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    encode_cmd = [
        'ffmpeg', '-y',
        '-f', 'rawvideo', '-vcodec', 'rawvideo',
        '-s', f'{graph_w}x{graph_h}', '-pix_fmt', 'rgb24',
        '-r', str(graph_fps), '-i', 'pipe:0',
        '-i', video_path,
        '-filter_complex', filter_complex,
        '-map', 'a?',  # Try to grab audio from video_path input
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-c:a', 'copy',
        '-preset', 'fast', '-crf', '23',
        '-movflags', '+faststart',
        '-shortest',
        out_path,
    ]
    
    print(f'V2 Architecture: Filter-based compositing', file=sys.stderr)
    print(f'Video:  {vid_w}x{vid_h} @ {vid_fps:.1f}fps, {vid_duration:.1f}s', file=sys.stderr)
    print(f'Graph:  {graph_w}x{graph_h} (10fps) → scaled to {vid_w}', file=sys.stderr)
    print(f'Output: {"landscape-stack" if is_landscape else "portrait-overlay"}', file=sys.stderr)

    encoder = subprocess.Popen(encode_cmd, stdin=subprocess.PIPE,
                               stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    # ── Pre-render padding frames ──
    renderer.update(0.0)
    first_frame = renderer.get_frame()
    
    renderer.update(graph_duration)
    renderer.graph_ctx['v_cursor'].set_visible(False)
    last_frame = renderer.get_frame()

    # ── Frame loop (Only 10 steps per second!) ──
    frames_written = 0
    try:
        for i in range(total_output_frames):
            t_video = i / graph_fps
            t_graph = t_video - offset
            
            if t_graph <= 0:
                frame_rgb = first_frame
            elif t_graph >= graph_duration:
                frame_rgb = last_frame
            else:
                renderer.update(t_graph)
                frame_rgb = renderer.get_frame()
            
            encoder.stdin.write(frame_rgb)
            frames_written += 1
            
            if frames_written % 20 == 0:
                print(f'  Graph Progress: {frames_written}/{total_output_frames}', file=sys.stderr)

    except BrokenPipeError:
        pass
    finally:
        if encoder.stdin:
            encoder.stdin.close()
        rc = encoder.wait()
        plt.close(renderer.fig)

        if rc != 0:
            err = (encoder.stderr.read().decode('utf-8', errors='replace')
                   if encoder.stderr else '')
            raise RuntimeError(f'Encoder ffmpeg exited {rc}: {err[-500:]}')

    return {
        'ok': True,
        'mode': 'V2-filter-based',
        'out': os.path.abspath(out_path),
        'frames': frames_written,
        'fps_python': graph_fps,
        'offset': offset,
    }


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description='Overlay Gaggiuino shot graph animation onto user video (V2 Accelerator)')
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument('--shot-id', type=int)
    src.add_argument('--input')
    parser.add_argument('--video', required=True)
    parser.add_argument('--out', help='Output file path (default: standard archive dir with shot ID)')
    parser.add_argument('--offset', type=float, default=0.0)
    parser.add_argument('--alpha', type=float, default=0.65)
    parser.add_argument('--position', choices=['top', 'bottom'], default='top')
    parser.add_argument('--graph-fps', type=int, default=10)
    args = parser.parse_args()

    # ── Default output and naming logic ──
    if not args.out:
        base_dir = os.path.expanduser('~/.openclaw/workspace/gaggiuino-output')
        os.makedirs(base_dir, exist_ok=True)
        
        # Get video info early to determine naming suffix
        vinfo = get_video_info(args.video)
        layout_suffix = 'landscape' if vinfo['width'] >= vinfo['height'] else 'portrait'
        
        name_part = f'shot{args.shot_id}' if args.shot_id else 'shot'
        args.out = os.path.join(base_dir, f'{name_part}_overlay_{layout_suffix}.mp4')
    else:
        args.out = os.path.expanduser(args.out)
    
    # Ensure parents exist for custom paths
    out_dir = os.path.dirname(os.path.abspath(args.out))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    try:
        shot = (load_shot_from_id(args.shot_id) if args.shot_id is not None
                else load_shot_from_file(args.input))
        result = render_overlay_v2(
            shot, args.video, args.out,
            offset=args.offset,
            alpha=args.alpha,
            position=args.position,
            graph_fps=args.graph_fps,
        )
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception as e:
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
