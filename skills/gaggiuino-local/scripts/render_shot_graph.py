#!/usr/bin/env python3
import os
# Prefer distro-managed scientific stack over user-site packages.
os.environ.setdefault('PYTHONNOUSERSITE', '1')

import argparse
import json
import math
import multiprocessing
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Tuple
import textwrap

if 'site' in sys.modules:
    import site
    if getattr(site, 'ENABLE_USER_SITE', False) and os.environ.get('_GAGGIUINO_GRAPH_REEXEC') != '1':
        env = os.environ.copy()
        env['PYTHONNOUSERSITE'] = '1'
        env['_GAGGIUINO_GRAPH_REEXEC'] = '1'
        os.execvpe(sys.executable, [sys.executable] + sys.argv, env)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import gridspec
from PIL import Image
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GAGGIUINO_SH = os.path.join(SCRIPT_DIR, 'gaggiuino.sh')
PROFILE_DESCRIPTIONS_MD = os.path.join(SCRIPT_DIR, '..', 'references', 'profile-descriptions.md')

# ─── Layout constants ────────────────────────────────────────────────────────
# Deterministic canvas: 2400×1080 px (2.22:1 aspect ratio).
# Optimised for:
#   - Landscape overlay: scales to 1920×864, stacked above 1080p video
#   - Portrait overlay: scales to 1080×486, covers ~25% of 1920px height
CANVAS_W = 2400
CANVAS_H = 1080
DPI = 150
FIG_W = CANVAS_W / DPI   # 16.0 in
FIG_H = CANVAS_H / DPI   # 7.2 in

MARGIN_LEFT   = 0.04
MARGIN_RIGHT  = 0.98
MARGIN_TOP    = 0.83      # graph area top edge (17% reserved for title)
MARGIN_BOTTOM = 0.06

GS_WIDTH_RATIOS = [1, 1, 1, 1, 0.55]   # narrow info-box column
GS_WSPACE = 0.18
GS_HSPACE = 0.16

TITLE_Y = 0.97
SUBTITLE_Y_SINGLE = 0.88
SUBTITLE_YS_2LINES = [0.895, 0.865]
SUBTITLE_YS_3LINES = [0.91, 0.88, 0.85]

# ─── Colors ───────────────────────────────────────────────────────────────────
BG = '#243447'
PANEL_BG = '#1f2c3d'
GRID = '#d7e3f0'
TEXT = '#eaf2fb'
MUTED = '#b7c7d9'
BLUE = '#14aaf5'
YELLOW = '#ffd428'
GREEN = '#28d35e'
ORANGE = '#ff8e57'
WHITE = '#ddd6df'
RED = '#ff5a5f'
BROWN = '#b78562'
BLUE_BOX = '#1aa0ff'
YELLOW_BOX = '#f4c430'
GREEN_BOX = '#22cc55'
ORANGE_BOX = '#ff8e57'
GREY_BOX = '#8ba2b7'
BROWN_BOX = '#b78562'


# ─── Utility functions ───────────────────────────────────────────────────────

def choose_multiprocess_workers(total_frames: int, requested_workers: int | None = None) -> int:
    if requested_workers is not None:
        return max(1, min(int(requested_workers), total_frames))
    cpu_count = os.cpu_count() or multiprocessing.cpu_count() or 1
    worker_cap = max(1, cpu_count + 1)
    frame_based = max(1, int(math.ceil(total_frames / 80)))
    return max(1, min(total_frames, worker_cap, frame_based))


def load_shot_from_id(shot_id: int) -> Dict[str, Any]:
    result = subprocess.run([GAGGIUINO_SH, 'shot', str(shot_id)], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def load_shot_from_file(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_series(datapoints: List[Dict[str, Any]], key: str, up_to_time: float | None = None) -> Tuple[List[float], List[float]]:
    xs, ys = [], []
    last_x, last_y = None, None
    for dp in datapoints:
        x = dp.get('timeInShot')
        y = dp.get(key)
        if x is None or y is None:
            continue
        x = float(x)
        y = float(y)

        if up_to_time is not None and x > up_to_time:
            if last_x is not None and last_y is not None and x > last_x:
                frac = (up_to_time - last_x) / (x - last_x)
                interp_y = last_y + (y - last_y) * frac
                xs.append(up_to_time)
                ys.append(interp_y)
            break

        xs.append(x)
        ys.append(y)
        last_x, last_y = x, y
    return xs, ys


def get_last_value(datapoints: List[Dict[str, Any]], key: str, default: float | None = None) -> float | None:
    for dp in reversed(datapoints):
        if dp.get(key) is not None:
            return float(dp[key])
    return default


def get_current_flow_reference(datapoints: List[Dict[str, Any]]) -> float | None:
    if not datapoints: return None
    current = datapoints[-1]
    control_mode = current.get('controlMode')
    val = current.get('pumpFlowTarget') if control_mode == 'flow' else current.get('pumpFlowLimit')
    return float(val) if val is not None else None


def get_current_pressure_reference(datapoints: List[Dict[str, Any]]) -> float | None:
    if not datapoints: return None
    current = datapoints[-1]
    control_mode = current.get('controlMode')
    val = current.get('pressureLimit') if control_mode == 'flow' else current.get('pressureTarget')
    return float(val) if val is not None else None


def get_x_axis_range(duration: float, datapoints: List[Dict[str, Any]]) -> Tuple[float, List[int]]:
    max_time = max(duration, float(datapoints[-1]['timeInShot']) if datapoints else duration)
    if max_time < 30:
        x_max = 30
    else:
        if max_time <= 40: ceiling_step = 5
        elif max_time <= 120: ceiling_step = 10
        else: ceiling_step = 20
        x_max = int(math.ceil(max_time / ceiling_step) * ceiling_step)

    ideal_tick = x_max / 8.0
    nice_ticks = [5, 10, 15, 20, 25, 30, 40, 50, 60]
    tick = next((t for t in nice_ticks if t >= ideal_tick), nice_ticks[-1])

    ticks = list(range(0, int(x_max) + 1, int(tick)))
    if ticks[-1] != int(x_max): ticks.append(int(x_max))
    return float(x_max), ticks


def lookup_profile_intent(profile_name: str) -> str | None:
    if not profile_name or not os.path.exists(PROFILE_DESCRIPTIONS_MD): return None
    
    # Normalize: Gaggiuino adds " (imported)" to names synced from files
    def normalize(name: str) -> str:
        return name.replace(' (imported)', '').strip()

    search_name = normalize(profile_name)
    current = None
    try:
        with open(PROFILE_DESCRIPTIONS_MD, 'r', encoding='utf-8') as f:
            for raw_line in f:
                line = raw_line.rstrip('\n')
                if line.startswith('## '):
                    current = normalize(line[3:])
                    continue
                if current == search_name and line.startswith('- **Intent:**'):
                    return line.split(':', 1)[1].strip().replace('**', '')
    except Exception:
        pass
    return None


# ─── Drawing helpers ──────────────────────────────────────────────────────────

def draw_adaptive_subtitle(fig, text: str):
    if not text: return
    wrapped = textwrap.wrap(text, width=110)
    if len(wrapped) == 1:
        line = wrapped[0]
        size = 18 if len(line) <= 92 else 17 if len(line) <= 108 else 16
        fig.text(0.5, SUBTITLE_Y_SINGLE, line, ha='center', va='center', color=MUTED, fontsize=size)
        return
    wrapped = textwrap.wrap(text, width=86)
    lines = wrapped[:3]
    if len(wrapped) > 3 and len(lines[-1]) > 3:
        lines[-1] = lines[-1][:-3].rstrip() + '...'
    
    # Choose coordinate set based on line count
    ys = SUBTITLE_YS_2LINES if len(lines) == 2 else SUBTITLE_YS_3LINES
    size = 17 if len(lines) == 2 else 15
    
    for i, line in enumerate(lines):
        fig.text(0.5, ys[i], line, ha='center', va='center', color=MUTED, fontsize=size)


def draw_main_graph(ax, shot: Dict[str, Any]) -> Dict[str, Any]:
    datapoints = shot['processedShot']['datapoints']
    duration = float(shot['processedShot']['duration'])

    ax.set_facecolor(BG)
    for spine in ax.spines.values():
        spine.set_color(MUTED)
        spine.set_alpha(0.5)

    x_max, x_ticks = get_x_axis_range(duration, datapoints)
    ax.set_xlim(0, x_max)
    ax.set_ylim(0, 12)
    ax.grid(True, color=GRID, linestyle=(0, (2, 3)), linewidth=1.2, alpha=0.9)
    ax.tick_params(axis='x', colors=TEXT, labelsize=10)
    ax.tick_params(axis='y', colors=BLUE, labelsize=12)
    ax.set_xticks(x_ticks)
    ax.set_yticks(list(range(0, 13, 1)))

    ax2 = ax.twinx()
    ax2.set_ylim(0, 120)
    ax2.set_yticks(list(range(0, 121, 10)))
    ax2.tick_params(axis='y', colors=RED, labelsize=12)
    for spine in ax2.spines.values():
        spine.set_visible(False)

    blue_ref_x, blue_ref_y, yellow_ref_x, yellow_ref_y = [], [], [], []
    for dp in datapoints:
        x = dp.get('timeInShot')
        if x is None: continue
        x = float(x)
        blue_val = dp.get('pressureLimit') if dp.get('controlMode') == 'flow' else dp.get('pressureTarget')
        yellow_val = dp.get('pumpFlowTarget') if dp.get('controlMode') == 'flow' else dp.get('pumpFlowLimit')
        blue_ref_x.append(x); blue_ref_y.append(0.0 if blue_val is None else float(blue_val))
        yellow_ref_x.append(x); yellow_ref_y.append(0.0 if yellow_val is None else float(yellow_val))

    ax.plot(blue_ref_x, blue_ref_y, color=BLUE, lw=2.0, alpha=0.75, ls='--')
    ax.plot(yellow_ref_x, yellow_ref_y, color=YELLOW, lw=2.0, alpha=0.8, ls='--')

    l_pressure, = ax.plot([], [], color=BLUE, lw=4.2, solid_capstyle='round')
    l_pump, = ax.plot([], [], color=YELLOW, lw=3.2, solid_capstyle='round')
    l_wf, = ax.plot([], [], color=GREEN, lw=2.6, alpha=0.9, solid_capstyle='round')
    l_weight, = ax2.plot([], [], color=BROWN, lw=3.0, solid_capstyle='round')
    l_temp, = ax2.plot([], [], color=RED, lw=2.2, alpha=0.95)

    x_tt, y_tt = get_series(datapoints, 'targetTemperature')
    ax2.plot(x_tt, y_tt, color=RED, lw=1.8, alpha=0.75, ls='--')

    v_cursor = ax.axvline(0, color=TEXT, lw=1.3, alpha=0.55, visible=False)

    return {
        'ax': ax, 'ax2': ax2,
        'l_pressure': l_pressure, 'l_pump': l_pump, 'l_wf': l_wf,
        'l_weight': l_weight, 'l_temp': l_temp, 'v_cursor': v_cursor
    }


def draw_info_box(ax, title: str, value1: str, value2: str, color: str,
                  value_size: int = 15, compact: bool = False,
                  indicator1: tuple | None = None,
                  indicator2: tuple | None = None) -> Dict[str, Any]:
    ax.set_facecolor(BG)
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values(): spine.set_visible(False)

    rect = plt.Rectangle((0.02, 0.06), 0.96, 0.88,
                          facecolor=PANEL_BG, edgecolor=color, lw=2.6, joinstyle='round')
    ax.add_patch(rect)
    ax.text(0.08, 0.72, title, color=color, fontsize=13, fontweight='bold',
            transform=ax.transAxes, va='center')

    t1 = ax.text(0.10, 0.36 if compact else 0.47, value1, color=TEXT,
                 fontsize=value_size, fontweight='bold', transform=ax.transAxes, va='center')
    t2 = None
    if not compact:
        t2 = ax.text(0.10, 0.21, value2, color=TEXT, fontsize=13, fontweight='bold',
                     transform=ax.transAxes, va='center')

    if indicator1:
        c, s = indicator1
        ls = s if s == '-' else (0, (2, 1))
        ax.plot([0.72, 0.92], [0.36 if compact else 0.47] * 2,
                transform=ax.transAxes, color=c, lw=3.0, ls=ls, solid_capstyle='round')
    if indicator2 and not compact:
        c, s = indicator2
        ax.plot([0.72, 0.92], [0.21, 0.21],
                transform=ax.transAxes, color=c, lw=3.0, ls=(0, (2, 1)), solid_capstyle='round')

    return {'v1': t1, 'v2': t2}


# ─── Core renderer ────────────────────────────────────────────────────────────

class ContextRenderer:
    """Stateful renderer with deterministic canvas layout.

    All output modes (PNG, GIF, MP4) share the same layout and pixel
    dimensions to ensure visual consistency between static and animated output.
    """

    def __init__(self, shot: Dict[str, Any]):
        self.shot = shot
        self.processed = shot['processedShot']
        self.datapoints = self.processed['datapoints']
        self.stats = shot.get('stats', {})
        self.duration = float(self.processed['duration'])

        self.out_w = CANVAS_W
        self.out_h = CANVAS_H
        self.fig = plt.figure(figsize=(FIG_W, FIG_H), dpi=DPI, facecolor=BG)
        self.fig.subplots_adjust(
            left=MARGIN_LEFT, right=MARGIN_RIGHT,
            top=MARGIN_TOP, bottom=MARGIN_BOTTOM)
        self.gs = gridspec.GridSpec(6, 5, figure=self.fig,
            width_ratios=GS_WIDTH_RATIOS,
            wspace=GS_WSPACE, hspace=GS_HSPACE)

        self.graph_ctx = draw_main_graph(self.fig.add_subplot(self.gs[:, :4]), shot)

        self.panel_refs = []
        boxes = [
            ('Timer', '00.00', '', GREY_BOX, 22, True),
            ('Weight', '0.0', '', BROWN_BOX, 22, True),
            ('Pressure', '0.0', '0.0 bar', BLUE_BOX, 15, False),
            ('Pump Flow', '0.0', '0.0 mls', YELLOW_BOX, 15, False),
            ('Weight Flow', '0.0', '--', GREEN_BOX, 15, False),
            ('Temperature', '0.0', '0.0 C', ORANGE_BOX, 15, False),
        ]
        for i, (title, v1, v2, color, size, compact) in enumerate(boxes):
            ax = self.fig.add_subplot(self.gs[i, 4])
            ind1, ind2 = None, None
            if title == 'Pressure': ind1, ind2 = (BLUE, '-'), (BLUE, '--')
            elif title == 'Pump Flow': ind1, ind2 = (YELLOW, '-'), (YELLOW, '--')
            elif title == 'Weight Flow': ind1 = (GREEN, '-')
            elif title == 'Temperature': ind1, ind2 = (RED, '-'), (RED, '--')
            self.panel_refs.append(draw_info_box(ax, title, v1, v2, color, size, compact, ind1, ind2))

        profile_name = self.processed.get('profile', {}).get('name', 'Shot Graph')
        self.fig.suptitle(profile_name, color=TEXT, fontsize=22, fontweight='bold', y=TITLE_Y)
        intent = lookup_profile_intent(profile_name)
        if intent: draw_adaptive_subtitle(self.fig, intent)

        self.fig.canvas.draw()
        self.canvas_w, self.canvas_h = self.fig.canvas.get_width_height()

    def update(self, t: float):
        vals = {}
        for key, attr in [('pressure', 'l_pressure'), ('pumpFlow', 'l_pump'), ('weightFlow', 'l_wf'),
                          ('shotWeight', 'l_weight'), ('temperature', 'l_temp')]:
            x, y = get_series(self.datapoints, key, up_to_time=t)
            self.graph_ctx[attr].set_data(x, y)
            vals[key] = y[-1] if y else 0.0

        self.graph_ctx['v_cursor'].set_xdata([t])
        self.graph_ctx['v_cursor'].set_visible(True)

        ts = int(t)
        info_dp = [dp for dp in self.datapoints if float(dp.get('timeInShot', 0)) <= t] or self.datapoints[:1]

        self.panel_refs[0]['v1'].set_text(f'{ts // 60:02d}.{ts % 60:02d}')
        self.panel_refs[1]['v1'].set_text(f'{vals["shotWeight"]:.1f}')

        p_val = vals['pressure']
        p_ref = get_current_pressure_reference(info_dp)
        self.panel_refs[2]['v1'].set_text(f'{p_val:.1f}')
        self.panel_refs[2]['v2'].set_text(f'{p_ref:.1f} bar' if p_ref is not None else '--')

        f_val = vals['pumpFlow']
        f_ref = get_current_flow_reference(info_dp)
        self.panel_refs[3]['v1'].set_text(f'{f_val:.1f}')
        self.panel_refs[3]['v2'].set_text(f'{f_ref:.1f} mls' if f_ref is not None else '--')

        self.panel_refs[4]['v1'].set_text(f'{vals["weightFlow"]:.1f}')

        t_val = vals['temperature']
        t_ref = get_last_value(info_dp, 'targetTemperature', t_val)
        self.panel_refs[5]['v1'].set_text(f'{t_val:.1f}')
        self.panel_refs[5]['v2'].set_text(f'{t_ref:.1f} C')

        self.fig.canvas.draw()

    def get_frame(self) -> bytes:
        rgba = np.frombuffer(self.fig.canvas.buffer_rgba(), dtype=np.uint8)
        rgb = rgba.reshape(self.canvas_h, self.canvas_w, 4)[:, :, :3]
        return np.ascontiguousarray(rgb).tobytes()


# ─── Multi-process MP4 rendering ─────────────────────────────────────────────

def _render_mp4_fast_segment(shot: Dict[str, Any], out_path: str, fps: int,
                             frame_start: int, frame_end: int) -> None:
    if shot is None: raise RuntimeError('Segment worker requires shot data')

    renderer = ContextRenderer(shot)
    duration = renderer.duration

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-f', 'rawvideo', '-vcodec', 'rawvideo',
        '-s', f'{renderer.out_w}x{renderer.out_h}', '-pix_fmt', 'rgb24',
        '-r', str(fps), '-i', '-',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
        '-x264-params', 'stitchable=1',
        '-preset', 'veryfast', '-threads', '1',
        '-movflags', '+faststart', '-crf', '23',
        out_path
    ]

    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    try:
        for i in range(frame_start, frame_end):
            t = min(duration, i / fps)
            renderer.update(t)
            proc.stdin.write(renderer.get_frame())
    except BrokenPipeError:
        pass
    finally:
        if proc.stdin: proc.stdin.close()
        rc = proc.wait()
        plt.close(renderer.fig)

        if rc != 0:
            err = proc.stderr.read().decode('utf-8', errors='replace') if proc.stderr else ''
            raise RuntimeError(f'Segment ffmpeg exited {rc}: {err}')


def render_mp4_multiprocess(shot: Dict[str, Any], out_path: str, fps: int,
                            workers: int | None = None) -> int:
    if not shutil.which('ffmpeg'): raise RuntimeError('ffmpeg not found in PATH')

    duration = float(shot['processedShot']['duration'])
    total_frames = max(2, int(math.ceil(duration * fps)) + 1)
    workers = choose_multiprocess_workers(total_frames, workers)

    chunk = total_frames // workers
    remainder = total_frames % workers
    segments, start = [], 0
    for i in range(workers):
        seg_len = chunk + (1 if i < remainder else 0)
        segments.append((start, start + seg_len))
        start += seg_len

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, prefix='shot_mp_') as f:
        json.dump(shot, f)
        shot_tmp = f.name

    seg_dir = tempfile.mkdtemp(prefix='gaggiuino-segments-')
    seg_paths = [os.path.join(seg_dir, f'seg-{i:03d}.mp4') for i in range(workers)]

    try:
        worker_script = os.path.abspath(__file__)
        procs: list[subprocess.Popen] = []
        for i, (fs, fe) in enumerate(segments):
            cmd = [
                sys.executable, worker_script, '--_segment',
                '--input', shot_tmp, '--out', seg_paths[i],
                '--fps', str(fps), '--_frame-start', str(fs), '--_frame-end', str(fe)
            ]
            procs.append(subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE))

        errors = []
        for i, p in enumerate(procs):
            _, stderr = p.communicate()
            if p.returncode != 0:
                err_text = stderr.decode('utf-8', errors='replace')[-500:] if stderr else ''
                errors.append(f'Worker {i} exited {p.returncode}: {err_text}')
        if errors: raise RuntimeError('Segment workers failed:\n' + '\n'.join(errors))

        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        concat_list = os.path.join(seg_dir, 'concat.txt')
        with open(concat_list, 'w') as f:
            for p in seg_paths: f.write(f"file '{p}'\n")

        subprocess.run(
            ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_list,
             '-c', 'copy', '-movflags', '+faststart', out_path],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        )
        return workers
    finally:
        os.unlink(shot_tmp)
        shutil.rmtree(seg_dir, ignore_errors=True)


# ─── Static and GIF output ───────────────────────────────────────────────────

def render_static_graph(shot: Dict[str, Any], out_path: str) -> None:
    renderer = ContextRenderer(shot)
    renderer.update(renderer.duration)
    renderer.graph_ctx['v_cursor'].set_visible(False)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    renderer.fig.savefig(out_path, dpi=DPI, facecolor=BG)
    plt.close(renderer.fig)


def render_gif(shot: Dict[str, Any], out_path: str, fps: int) -> None:
    duration = float(shot['processedShot']['duration'])
    effective_fps = min(fps, 8)
    frame_count = max(2, int(math.ceil(duration * effective_fps)) + 1)
    renderer = ContextRenderer(shot)

    images = []
    for i in range(frame_count):
        renderer.update(min(duration, i / effective_fps))
        rgb = renderer.get_frame()
        img = Image.frombuffer('RGB', (renderer.out_w, renderer.out_h), rgb, 'raw', 'RGB', 0, 1)
        images.append(img.convert('P', palette=Image.ADAPTIVE))

    plt.close(renderer.fig)
    if not images: raise RuntimeError('No frames generated for GIF')

    images[0].save(out_path, save_all=True, append_images=images[1:], loop=0,
                   duration=max(30, int(round(1000 / effective_fps))), disposal=2)


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description='Gaggiuino shot graph renderer (v7)')
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument('--shot-id', type=int)
    src.add_argument('--input')
    parser.add_argument('--out', help='Output file path (default: standard archive dir with shot ID)')
    parser.add_argument('--mode', choices=['png', 'gif', 'mp4'], default='png')
    parser.add_argument('--fps', type=int, default=10)
    parser.add_argument('--workers', default='auto')

    # Hidden segment args
    parser.add_argument('--_segment', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--_frame-start', type=int, default=0, help=argparse.SUPPRESS)
    parser.add_argument('--_frame-end', type=int, default=0, help=argparse.SUPPRESS)
    args = parser.parse_args()
    
    # ── Default output and naming logic ──
    if not args.out:
        base_dir = os.path.expanduser('~/.openclaw/workspace/gaggiuino-output')
        os.makedirs(base_dir, exist_ok=True)
        
        name_part = f'shot{args.shot_id}' if args.shot_id else 'shot'
        suffix = '_static' if args.mode == 'png' else '_animated'
        ext = args.mode if args.mode != 'mp4' else 'mp4'
        args.out = os.path.join(base_dir, f'{name_part}{suffix}.{ext}')
    else:
        args.out = os.path.expanduser(args.out)
    
    # Ensure parents exist for custom paths
    out_dir = os.path.dirname(os.path.abspath(args.out))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    if args._segment:
        try:
            shot = load_shot_from_file(args.input)
            _render_mp4_fast_segment(shot, args.out, args.fps, args._frame_start, args._frame_end)
            return 0
        except Exception as e:
            print(f'Segment worker failed: {e}', file=sys.stderr)
            return 1

    try:
        shot = load_shot_from_id(args.shot_id) if args.shot_id is not None else load_shot_from_file(args.input)
        used_workers = None

        if args.mode == 'png':
            render_static_graph(shot, args.out)
        elif args.mode == 'gif':
            render_gif(shot, args.out, fps=args.fps)
        elif args.mode == 'mp4':
            num_workers = args.workers
            if num_workers == 'auto':
                import multiprocessing
                num_workers = max(1, multiprocessing.cpu_count() - 1)
            else:
                num_workers = int(num_workers) if num_workers is not None else 1
            
            used_workers = render_mp4_multiprocess(shot, args.out, fps=args.fps, workers=num_workers)

        payload = {'ok': True, 'mode': args.mode, 'out': os.path.abspath(args.out)}
        if used_workers is not None:
            payload['multiprocess'] = True
            payload['workers'] = used_workers
        else:
            payload['multiprocess'] = False

        print(json.dumps(payload, ensure_ascii=False))
        return 0
    except Exception as e:
        import traceback
        traceback.print_exc(file=sys.stderr)
        print(f'Failed to render graph: {e}', file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
