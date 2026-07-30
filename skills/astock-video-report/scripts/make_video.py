#!/usr/bin/env python3
"""
astock-video-report / make_video.py
合成幻灯片视频 + BGM + 封面图

依赖:
  - ffmpeg（系统命令）: brew install ffmpeg / apt install ffmpeg
  - pillow: pip install pillow

用法:
  python3 make_video.py \
    --slides-dir ~/astock-output/slides \
    --outdir ~/astock-output \
    --date 2026-03-16

BGM 默认使用 skill 自带的 assets/bgm/eliveta-technology-474054.mp3
也可通过 --bgm 指定其他文件。
"""
import argparse, os, sys, subprocess, shutil
from pathlib import Path

# 确保同目录下的模块可导入（从任意工作目录执行时）
sys.path.insert(0, str(Path(__file__).parent))

def check_ffmpeg():
    if not shutil.which('ffmpeg'):
        print("❌ 未找到 ffmpeg，请先安装：")
        print("   macOS:  brew install ffmpeg")
        print("   Linux:  apt install ffmpeg  /  yum install ffmpeg")
        print("   Windows: https://ffmpeg.org/download.html")
        sys.exit(1)

def run(cmd, label=''):
    print(f'  ▶ {label}...')
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f'  ❌ 失败:\n{r.stderr[-500:]}')
        sys.exit(1)
    print('  ✅')

def default_bgm():
    """默认 BGM：skill assets 目录下，不存在则尝试自动下载"""
    skill_root = Path(__file__).parent.parent
    bgm = skill_root / 'assets' / 'bgm' / 'eliveta-technology-474054.mp3'
    if bgm.exists():
        return str(bgm)
    # 尝试自动下载
    try:
        from ensure_assets import ensure_bgm
        downloaded = ensure_bgm()
        if downloaded:
            return downloaded
    except ImportError:
        pass
    return None

def main():
    check_ffmpeg()

    p = argparse.ArgumentParser(description='合成 A 股复盘视频')
    p.add_argument('--slides-dir', required=True, help='幻灯片目录（make_slides.py 的输出）')
    p.add_argument('--outdir',     required=True, help='视频输出目录')
    p.add_argument('--date',       required=True, help='交易日期标签，用于文件命名（必填，如 2026-03-16）')
    p.add_argument('--bgm',        default=None, help='BGM 文件路径（默认使用 skill 自带）')
    p.add_argument('--dur',        type=float, default=5.0, help='每张幻灯片展示秒数（默认5）')
    p.add_argument('--bgm-start',  type=float, default=10.0, help='BGM 起始秒数（默认10）')
    args = p.parse_args()

    slides_dir = os.path.expanduser(args.slides_dir)
    outdir     = os.path.expanduser(args.outdir)
    os.makedirs(outdir, exist_ok=True)

    # BGM 优先用参数，否则用 skill 自带
    bgm_path = args.bgm or default_bgm()
    if not bgm_path or not os.path.exists(bgm_path):
        print("❌ 未找到 BGM 文件，请通过 --bgm 指定，或确认 skill assets/bgm/ 目录存在")
        sys.exit(1)

    slides = sorted(f for f in os.listdir(slides_dir) if f.endswith('.png'))
    if not slides:
        print('❌ 没有找到幻灯片 PNG，请先运行 make_slides.py')
        sys.exit(1)

    date_str   = args.date
    video_out  = os.path.join(outdir, f'{date_str}-复盘.mp4')
    cover_out  = os.path.join(outdir, f'{date_str}-封面.jpg')
    tmpdir     = os.path.join(outdir, '.tmp')
    os.makedirs(tmpdir, exist_ok=True)

    FPS = 30
    DUR = args.dur
    FADE = 0.4
    fi = int(FPS * FADE)
    total_f = int(DUR * FPS)
    total_dur = DUR * len(slides)

    print(f'\n[1/4] 生成各幻灯片片段 ({len(slides)} 张 × {DUR}s)...')
    clips = []
    for i, slide in enumerate(slides):
        out = os.path.join(tmpdir, f'clip_{i:02d}.mp4')
        # 封面（第一张）不淡入，直接亮起
        if i == 0:
            vf = (f'scale=1920:1080:force_original_aspect_ratio=decrease,'
                  f'pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,'
                  f'fade=out:{total_f-fi}:{fi}:color=black')
        else:
            vf = (f'scale=1920:1080:force_original_aspect_ratio=decrease,'
                  f'pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,'
                  f'fade=in:0:{fi}:color=black,'
                  f'fade=out:{total_f-fi}:{fi}:color=black')
        run(['ffmpeg', '-y', '-loop', '1', '-framerate', str(FPS),
             '-i', os.path.join(slides_dir, slide),
             '-vf', vf, '-t', str(DUR),
             '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
             '-pix_fmt', 'yuv420p', '-r', str(FPS), out],
            f'{i+1}/{len(slides)}: {slide}')
        clips.append(out)

    print('\n[2/4] 拼接片段...')
    filelist = os.path.join(tmpdir, 'concat.txt')
    with open(filelist, 'w') as f:
        for c in clips: f.write(f"file '{c}'\n")
    no_audio = os.path.join(tmpdir, 'no_audio.mp4')
    run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', filelist,
         '-c', 'copy', no_audio], '拼接')

    print('\n[3/4] 处理 BGM...')
    bgm_cut = os.path.join(tmpdir, 'bgm_cut.mp3')
    run(['ffmpeg', '-y', '-ss', str(args.bgm_start), '-i', bgm_path,
         '-t', str(total_dur + 1),
         '-af', f'afade=in:st=0:d=1,afade=out:st={total_dur-2}:d=2,volume=0.75',
         bgm_cut], f'截取 BGM（从 {args.bgm_start}s 起，共 {total_dur:.0f}s）')

    print('\n[4/4] 合成最终视频...')
    run(['ffmpeg', '-y', '-i', no_audio, '-i', bgm_cut,
         '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
         '-map', '0:v:0', '-map', '1:a:0', '-shortest', video_out],
        '合成视频 + BGM')

    # 导出封面 JPG
    try:
        from PIL import Image
        img = Image.open(os.path.join(slides_dir, slides[0])).convert('RGB')
        img.save(cover_out, 'JPEG', quality=95)
        print(f'  ✅ 封面图: {cover_out}')
    except ImportError:
        print('  ⚠️  pillow 未安装，跳过封面图生成')

    # 清理临时文件
    import shutil as _shutil
    _shutil.rmtree(tmpdir, ignore_errors=True)

    size_mb = os.path.getsize(video_out) / 1024 / 1024
    print(f'\n🎬 完成！')
    print(f'   视频: {video_out}  ({size_mb:.1f} MB)')
    print(f'   封面: {cover_out}')
    print(f'   规格: 1920x1080 横屏 · {FPS}fps · {total_dur:.0f}s')
    print(f'\n   上传视频号时，封面请手动选择封面图文件')
    print(f'   推荐话题: #AI量化 #A股复盘 #非凸科技 #OpenClaw')

if __name__ == '__main__':
    main()
