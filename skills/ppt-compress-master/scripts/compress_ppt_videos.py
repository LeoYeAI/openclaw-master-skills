#!/usr/bin/env python3
"""
PPT Compressor - Compress videos and large images embedded in PowerPoint files.

Workflow:
  1. Copy the .pptx file and rename to .zip
  2. Extract the zip archive
  3. Find all video files under ppt/media/ and compress with ffmpeg
  4. Find all image files > 1MB under ppt/media/ and compress with Pillow
  5. Replace originals with compressed versions (only if smaller)
  6. Repackage into a new .pptx file

Usage:
    python compress_ppt_videos.py <input.pptx> [--output <output.pptx>] [--crf <value>] [--preset <preset>] [--max-height <pixels>]

Arguments:
    input.pptx          Path to the input PowerPoint file
    --output, -o        Path for the output compressed file (default: <input>_compressed.pptx)
    --crf               CRF (Constant Rate Factor) value for quality control (default: 28, range: 0-51, higher = smaller file)
    --preset            FFmpeg encoding preset (default: medium, options: ultrafast/superfast/veryfast/faster/fast/medium/slow/slower/veryslow)
    --max-height        Maximum video height in pixels for downscaling (default: 720, set 0 to disable)
    --audio-bitrate     Audio bitrate (default: 128k)
    --image-quality     JPEG quality for image compression (default: 80, range: 1-95)
    --image-max-dim     Maximum dimension (width or height) for image downscaling (default: 1920, set 0 to disable)
    --image-threshold   Image file size threshold in bytes for compression (default: 1048576 = 1MB)
    --no-images         Skip image compression
    --no-videos         Skip video compression
    --dry-run           Show what would be done without actually compressing

Dependencies:
    - Python 3.7+
    - Pillow (pip install Pillow) - for image compression
    - ffmpeg - bundled in scripts/bin/ or system PATH
"""

import sys
import os
import shutil
import zipfile
import subprocess
import argparse
import tempfile
import json
from pathlib import Path

# Supported file extensions
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.wmv', '.m4v', '.mkv', '.webm', '.flv', '.mpeg', '.mpg'}
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.webp'}

# Default image compression threshold: 1MB
DEFAULT_IMAGE_THRESHOLD = 1 * 1024 * 1024  # 1MB


def get_bundled_bin_dir():
    """Get the path to the bundled bin directory containing ffmpeg."""
    script_dir = Path(__file__).parent.resolve()
    return script_dir / 'bin'


def find_ffmpeg():
    """
    Find ffmpeg executable. Priority:
    1. Bundled version in scripts/bin/
    2. System PATH
    
    Returns:
        tuple: (ffmpeg_path, ffprobe_path) or (None, None) if not found
    """
    bin_dir = get_bundled_bin_dir()
    
    # Check bundled version first
    if sys.platform == 'win32':
        ffmpeg_bundled = bin_dir / 'ffmpeg.exe'
        ffprobe_bundled = bin_dir / 'ffprobe.exe'
    else:
        ffmpeg_bundled = bin_dir / 'ffmpeg'
        ffprobe_bundled = bin_dir / 'ffprobe'
    
    if ffmpeg_bundled.exists() and ffprobe_bundled.exists():
        print(f"[INFO] Using bundled ffmpeg from: {bin_dir}")
        return str(ffmpeg_bundled), str(ffprobe_bundled)
    
    # Fall back to system PATH
    ffmpeg_name = 'ffmpeg.exe' if sys.platform == 'win32' else 'ffmpeg'
    ffprobe_name = 'ffprobe.exe' if sys.platform == 'win32' else 'ffprobe'
    
    ffmpeg_sys = shutil.which(ffmpeg_name)
    ffprobe_sys = shutil.which(ffprobe_name)
    
    if ffmpeg_sys and ffprobe_sys:
        print(f"[INFO] Using system ffmpeg from PATH")
        return ffmpeg_sys, ffprobe_sys
    
    return None, None


def check_ffmpeg(ffmpeg_path):
    """Verify that ffmpeg is accessible and working."""
    try:
        result = subprocess.run(
            [ffmpeg_path, '-version'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"[INFO] ffmpeg version: {version_line}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return False


def ensure_pillow():
    """Ensure Pillow is installed, install if missing."""
    try:
        from PIL import Image
        return True
    except ImportError:
        print("[INFO] Pillow not found. Installing...")
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', 'Pillow', '-q'],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                print("[INFO] Pillow installed successfully.")
                return True
            else:
                print(f"[WARN] Failed to install Pillow: {result.stderr}")
                return False
        except Exception as e:
            print(f"[WARN] Failed to install Pillow: {e}")
            return False


def get_video_info(ffprobe_path, video_path):
    """Get video file information using ffprobe."""
    try:
        result = subprocess.run(
            [
                ffprobe_path, '-v', 'quiet',
                '-print_format', 'json',
                '-show_format', '-show_streams',
                str(video_path)
            ],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return None


def format_size(size_bytes):
    """Format byte size to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def compress_video(ffmpeg_path, ffprobe_path, input_path, output_path,
                   crf=28, preset='medium', max_height=720, audio_bitrate='128k'):
    """
    Compress a video file using ffmpeg with H.264 codec.

    Returns:
        True if compression succeeded, False otherwise
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    # Build ffmpeg command
    cmd = [
        ffmpeg_path, '-y',        # Overwrite output without asking
        '-i', str(input_path),    # Input file
    ]

    # Video codec: H.264 for maximum compatibility with PowerPoint
    video_filters = []

    # Add scale filter if max_height is set and video is larger
    if max_height > 0:
        info = get_video_info(ffprobe_path, input_path)
        if info:
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'video':
                    height = stream.get('height', 0)
                    if height > max_height:
                        video_filters.append(f"scale=-2:{max_height}")
                    break

    cmd.extend([
        '-c:v', 'libx264',        # H.264 codec (best PPT compatibility)
        '-crf', str(crf),         # Quality factor
        '-preset', preset,        # Encoding speed/compression tradeoff
        '-profile:v', 'high',     # H.264 profile for good quality
        '-level', '4.1',          # Compatibility level
        '-pix_fmt', 'yuv420p',    # Pixel format for maximum compatibility
    ])

    if video_filters:
        cmd.extend(['-vf', ','.join(video_filters)])

    # Audio settings: AAC for best compatibility
    cmd.extend([
        '-c:a', 'aac',            # AAC audio codec
        '-b:a', audio_bitrate,    # Audio bitrate
        '-ar', '44100',           # Sample rate
    ])

    cmd.extend([
        '-movflags', '+faststart',
    ])

    cmd.append(str(output_path))

    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=600
        )
        if result.returncode == 0:
            return True
        else:
            print(f"[ERROR] ffmpeg failed for {input_path.name}:")
            stderr_lines = result.stderr.strip().split('\n')
            for line in stderr_lines[-5:]:
                print(f"        {line}")
            return False
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Compression timed out for {input_path.name}")
        return False


def compress_image(input_path, output_path, quality=80, max_dim=1920):
    """
    Compress an image file using Pillow.

    Parameters:
        input_path:     Path to the source image
        output_path:    Path for the compressed output
        quality:        JPEG quality (1-95, default: 80)
        max_dim:        Max dimension (width or height), 0 to disable (default: 1920)

    Returns:
        True if compression succeeded, False otherwise
    """
    try:
        from PIL import Image
    except ImportError:
        print(f"[WARN] Pillow not available, skipping image compression for {input_path}")
        return False

    try:
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        img = Image.open(str(input_path))
        original_format = img.format  # e.g. 'PNG', 'JPEG', 'BMP'
        original_mode = img.mode
        
        # Resize if larger than max_dim
        if max_dim > 0:
            w, h = img.size
            if w > max_dim or h > max_dim:
                ratio = min(max_dim / w, max_dim / h)
                new_w = int(w * ratio)
                new_h = int(h * ratio)
                img = img.resize((new_w, new_h), Image.LANCZOS)
                print(f"    Resized: {w}x{h} -> {new_w}x{new_h}")
        
        # Determine output format based on original extension
        suffix = input_path.suffix.lower()
        
        if suffix in ('.jpg', '.jpeg'):
            # Save as JPEG
            if original_mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGB')
            img.save(str(output_path), 'JPEG', quality=quality, optimize=True)
        elif suffix == '.png':
            # For PNG: try saving as optimized PNG
            # If has alpha, keep as PNG; otherwise convert to JPEG for better compression
            if original_mode in ('RGBA', 'LA', 'PA'):
                # Has transparency - keep as PNG with optimization
                img.save(str(output_path), 'PNG', optimize=True)
            else:
                # No transparency - save as optimized PNG
                img.save(str(output_path), 'PNG', optimize=True)
        elif suffix in ('.bmp', '.tiff', '.tif'):
            # Convert BMP/TIFF to JPEG (much smaller), keep same extension for PPT compatibility
            if original_mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGB')
            # Save as JPEG but with original extension for PPTX compatibility
            # Actually, we need to keep the format compatible. Save as PNG for better compatibility
            img.save(str(output_path), 'PNG', optimize=True)
            # Rename to match original extension
            final_path = output_path.with_suffix(suffix)
            if final_path != output_path:
                output_path.rename(final_path)
                return True
        elif suffix == '.webp':
            img.save(str(output_path), 'WEBP', quality=quality, method=6)
        else:
            # Fallback: save as JPEG
            if original_mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGB')
            img.save(str(output_path), 'JPEG', quality=quality, optimize=True)
        
        return True
    except Exception as e:
        print(f"[ERROR] Image compression failed for {input_path}: {e}")
        return False


def extract_pptx(pptx_path, extract_dir):
    """Extract .pptx file (which is a zip archive) to a directory."""
    try:
        with zipfile.ZipFile(str(pptx_path), 'r') as zf:
            zf.extractall(str(extract_dir))
        return True
    except zipfile.BadZipFile:
        print(f"[ERROR] {pptx_path} is not a valid .pptx file (bad zip archive)")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to extract {pptx_path}: {e}")
        return False


def repackage_pptx(source_dir, output_path):
    """
    Repackage extracted directory back into a .pptx file.
    Use deflated compression and preserve directory structure.
    """
    source_dir = Path(source_dir)
    output_path = Path(output_path)

    try:
        with zipfile.ZipFile(str(output_path), 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in sorted(source_dir.rglob('*')):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir)
                    zf.write(str(file_path), str(arcname))
        return True
    except Exception as e:
        print(f"[ERROR] Failed to repackage .pptx: {e}")
        return False


def find_videos(media_dir):
    """Find all video files in the media directory."""
    media_path = Path(media_dir)
    if not media_path.exists():
        return []

    videos = []
    for f in media_path.iterdir():
        if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS:
            videos.append(f)

    return sorted(videos)


def find_large_images(media_dir, threshold=DEFAULT_IMAGE_THRESHOLD):
    """Find all image files larger than threshold in the media directory."""
    media_path = Path(media_dir)
    if not media_path.exists():
        return []

    images = []
    for f in media_path.iterdir():
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS:
            if f.stat().st_size > threshold:
                images.append(f)

    return sorted(images)


def compress_pptx(input_pptx, output_pptx=None, crf=28, preset='medium',
                  max_height=720, audio_bitrate='128k',
                  image_quality=80, image_max_dim=1920,
                  image_threshold=DEFAULT_IMAGE_THRESHOLD,
                  skip_images=False, skip_videos=False, dry_run=False):
    """
    Main function: Compress all videos and large images in a .pptx file.

    Returns:
        True if successful, False otherwise
    """
    input_pptx = Path(input_pptx).resolve()

    if not input_pptx.exists():
        print(f"[ERROR] File not found: {input_pptx}")
        return False

    if input_pptx.suffix.lower() != '.pptx':
        print(f"[ERROR] File is not a .pptx file: {input_pptx}")
        return False

    # Generate output path if not provided
    if output_pptx is None:
        output_pptx = input_pptx.parent / f"{input_pptx.stem}_compressed.pptx"
    else:
        output_pptx = Path(output_pptx).resolve()

    original_size = input_pptx.stat().st_size
    print(f"[INFO] Input:  {input_pptx}")
    print(f"[INFO] Output: {output_pptx}")
    print(f"[INFO] Original size: {format_size(original_size)}")
    print()

    # Find ffmpeg if video compression is needed
    ffmpeg_path, ffprobe_path = None, None
    if not skip_videos:
        ffmpeg_path, ffprobe_path = find_ffmpeg()
        if ffmpeg_path is None:
            print("[WARN] ffmpeg not found (not bundled and not in PATH).")
            print("[WARN] Video compression will be skipped.")
            print("[WARN] To enable video compression, run: python {SKILL_DIR}/scripts/download_ffmpeg.py")
            skip_videos = True
        elif not dry_run:
            if not check_ffmpeg(ffmpeg_path):
                print("[WARN] ffmpeg found but not working. Video compression will be skipped.")
                skip_videos = True

    # Check Pillow for image compression
    has_pillow = False
    if not skip_images:
        has_pillow = ensure_pillow()
        if not has_pillow:
            print("[WARN] Pillow not available. Image compression will be skipped.")
            skip_images = True

    if not skip_videos:
        print(f"[INFO] Video settings: CRF={crf}, preset={preset}, max_height={max_height}px, audio={audio_bitrate}")
    if not skip_images:
        print(f"[INFO] Image settings: quality={image_quality}, max_dim={image_max_dim}px, threshold={format_size(image_threshold)}")
    print()

    # Create a temporary working directory
    with tempfile.TemporaryDirectory(prefix='ppt_compress_') as tmp_dir:
        tmp_path = Path(tmp_dir)
        extract_dir = tmp_path / 'extracted'

        # Step 1: Extract the .pptx archive
        print("[STEP 1/5] Extracting .pptx archive...")
        if not extract_pptx(input_pptx, extract_dir):
            return False

        media_dir = extract_dir / 'ppt' / 'media'
        
        # Step 2: Find and compress videos
        videos = find_videos(media_dir) if not skip_videos else []
        total_video_saved = 0

        if videos:
            print(f"\n[STEP 2/5] Found {len(videos)} video file(s):")
            total_video_size = 0
            for v in videos:
                size = v.stat().st_size
                total_video_size += size
                print(f"         - {v.name} ({format_size(size)})")
            print(f"         Total video size: {format_size(total_video_size)}")
            print()

            if dry_run:
                print("[DRY-RUN] Would compress the above videos with these settings:")
                print(f"          CRF: {crf}, Preset: {preset}, Max Height: {max_height}px")
            else:
                print("  Compressing videos with ffmpeg...")
                compressed_dir = tmp_path / 'compressed_videos'
                compressed_dir.mkdir()

                success_count = 0
                for i, video in enumerate(videos, 1):
                    print(f"  [{i}/{len(videos)}] Compressing {video.name}...", end=' ', flush=True)

                    original_video_size = video.stat().st_size
                    compressed_path = compressed_dir / video.name
                    
                    if compress_video(ffmpeg_path, ffprobe_path, video, compressed_path,
                                      crf, preset, max_height, audio_bitrate):
                        compressed_size = compressed_path.stat().st_size
                        saved = original_video_size - compressed_size
                        ratio = (1 - compressed_size / original_video_size) * 100 if original_video_size > 0 else 0

                        if compressed_size < original_video_size:
                            shutil.copy2(str(compressed_path), str(video))
                            total_video_saved += saved
                            print(f"OK ({format_size(original_video_size)} -> {format_size(compressed_size)}, saved {ratio:.1f}%)")
                        else:
                            print(f"SKIP (compressed file is larger, keeping original)")

                        success_count += 1
                    else:
                        print("FAILED (keeping original)")

                print(f"\n  Video compression: {success_count}/{len(videos)} processed")
                print(f"  Total saved from videos: {format_size(total_video_saved)}")
        else:
            if not skip_videos:
                print("[STEP 2/5] No video files found in ppt/media/.")
            else:
                print("[STEP 2/5] Video compression skipped.")

        # Step 3: Find and compress large images
        large_images = find_large_images(media_dir, image_threshold) if not skip_images else []
        total_image_saved = 0

        if large_images:
            print(f"\n[STEP 3/5] Found {len(large_images)} image(s) larger than {format_size(image_threshold)}:")
            total_image_size = 0
            for img in large_images:
                size = img.stat().st_size
                total_image_size += size
                print(f"         - {img.name} ({format_size(size)})")
            print(f"         Total large image size: {format_size(total_image_size)}")
            print()

            if dry_run:
                print("[DRY-RUN] Would compress the above images with these settings:")
                print(f"          Quality: {image_quality}, Max Dimension: {image_max_dim}px")
            else:
                print("  Compressing images with Pillow...")
                compressed_img_dir = tmp_path / 'compressed_images'
                compressed_img_dir.mkdir()

                success_count = 0
                for i, img_file in enumerate(large_images, 1):
                    print(f"  [{i}/{len(large_images)}] Compressing {img_file.name}...", end=' ', flush=True)

                    original_img_size = img_file.stat().st_size
                    compressed_path = compressed_img_dir / img_file.name
                    
                    if compress_image(img_file, compressed_path, image_quality, image_max_dim):
                        if compressed_path.exists():
                            compressed_size = compressed_path.stat().st_size
                            saved = original_img_size - compressed_size
                            ratio = (1 - compressed_size / original_img_size) * 100 if original_img_size > 0 else 0

                            if compressed_size < original_img_size:
                                shutil.copy2(str(compressed_path), str(img_file))
                                total_image_saved += saved
                                print(f"OK ({format_size(original_img_size)} -> {format_size(compressed_size)}, saved {ratio:.1f}%)")
                            else:
                                print(f"SKIP (compressed file is larger, keeping original)")
                        else:
                            print("SKIP (output file not created)")

                        success_count += 1
                    else:
                        print("FAILED (keeping original)")

                print(f"\n  Image compression: {success_count}/{len(large_images)} processed")
                print(f"  Total saved from images: {format_size(total_image_saved)}")
        else:
            if not skip_images:
                print(f"\n[STEP 3/5] No images larger than {format_size(image_threshold)} found.")
            else:
                print("\n[STEP 3/5] Image compression skipped.")

        # Check if anything was done
        if not videos and not large_images:
            print("\n[INFO] No compressible media found. Copying original file.")
            shutil.copy2(str(input_pptx), str(output_pptx))
            print(f"[INFO] Copied original file to {output_pptx}")
            return True

        if dry_run:
            print("\n[DRY-RUN] No actual compression performed.")
            return True

        # Step 4: Repackage into .pptx
        print("\n[STEP 4/5] Repackaging into .pptx...")
        if not repackage_pptx(extract_dir, output_pptx):
            return False

    # Step 5: Show final results
    final_size = output_pptx.stat().st_size
    total_reduction = original_size - final_size
    total_ratio = (1 - final_size / original_size) * 100 if original_size > 0 else 0

    print()
    print("=" * 60)
    print(f"  Compression Complete!")
    print(f"  Original:           {format_size(original_size)}")
    print(f"  Compressed:         {format_size(final_size)}")
    if total_video_saved > 0:
        print(f"  Saved (videos):     {format_size(total_video_saved)}")
    if total_image_saved > 0:
        print(f"  Saved (images):     {format_size(total_image_saved)}")
    print(f"  Total Saved:        {format_size(total_reduction)} ({total_ratio:.1f}%)")
    print(f"  Output:             {output_pptx}")
    print("=" * 60)

    return True


def run(input_path, output_path=None, **kwargs):
    """
    Simple function to compress a PPT file. This is the recommended way to call
    the compressor from Python code or agent scripts.
    
    Parameters:
        input_path:     Path to the input .pptx file (can be string or Path)
        output_path:    Optional path for the output file (default: <input>_compressed.pptx)
        **kwargs:       Additional options:
            - crf (int): Video quality factor, 0-51 (default: 28)
            - preset (str): Encoding speed preset (default: 'medium')
            - max_height (int): Max video height in pixels (default: 720)
            - audio_bitrate (str): Audio bitrate (default: '128k')
            - image_quality (int): JPEG quality, 1-95 (default: 80)
            - image_max_dim (int): Max image dimension (default: 1920)
            - image_threshold (int): Size threshold for image compression (default: 1MB)
            - skip_images (bool): Skip image compression (default: False)
            - skip_videos (bool): Skip video compression (default: False)
            - dry_run (bool): Preview without compressing (default: False)
    
    Returns:
        bool: True if compression succeeded, False otherwise
    
    Example:
        from compress_ppt_videos import run
        run(r"C:/Users/user/Desktop/presentation.pptx")
        run(r"C:/path/to.pptx", crf=32, image_quality=70)
    """
    return compress_pptx(
        input_pptx=input_path,
        output_pptx=output_path,
        crf=kwargs.get('crf', 28),
        preset=kwargs.get('preset', 'medium'),
        max_height=kwargs.get('max_height', 720),
        audio_bitrate=kwargs.get('audio_bitrate', '128k'),
        image_quality=kwargs.get('image_quality', 80),
        image_max_dim=kwargs.get('image_max_dim', 1920),
        image_threshold=kwargs.get('image_threshold', DEFAULT_IMAGE_THRESHOLD),
        skip_images=kwargs.get('skip_images', False),
        skip_videos=kwargs.get('skip_videos', False),
        dry_run=kwargs.get('dry_run', False)
    )


def main(argv=None):
    """
    Main entry point with command-line argument parsing.
    
    Parameters:
        argv: Optional list of arguments. If None, uses sys.argv.
              This allows programmatic calling: main(['input.pptx', '--crf', '32'])
    """
    parser = argparse.ArgumentParser(
        description='Compress videos and large images in PowerPoint (.pptx) files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s presentation.pptx
  %(prog)s presentation.pptx -o compressed.pptx
  %(prog)s presentation.pptx --crf 32 --preset fast
  %(prog)s presentation.pptx --max-height 480
  %(prog)s presentation.pptx --image-quality 70 --image-max-dim 1280
  %(prog)s presentation.pptx --no-videos   # Only compress images
  %(prog)s presentation.pptx --no-images   # Only compress videos
  %(prog)s presentation.pptx --dry-run
        """
    )

    parser.add_argument('input', help='Path to the input .pptx file')
    parser.add_argument('-o', '--output', help='Path for the output compressed .pptx file')

    # Video compression options
    video_group = parser.add_argument_group('Video Compression Options')
    video_group.add_argument('--crf', type=int, default=28,
                             help='CRF value for quality (0-51, default: 28, higher = smaller)')
    video_group.add_argument('--preset', default='medium',
                             choices=['ultrafast', 'superfast', 'veryfast', 'faster',
                                      'fast', 'medium', 'slow', 'slower', 'veryslow'],
                             help='FFmpeg encoding preset (default: medium)')
    video_group.add_argument('--max-height', type=int, default=720,
                             help='Max video height in pixels, 0 to disable (default: 720)')
    video_group.add_argument('--audio-bitrate', default='128k',
                             help='Audio bitrate (default: 128k)')

    # Image compression options
    image_group = parser.add_argument_group('Image Compression Options')
    image_group.add_argument('--image-quality', type=int, default=80,
                             help='JPEG quality for image compression (1-95, default: 80)')
    image_group.add_argument('--image-max-dim', type=int, default=1920,
                             help='Max image dimension in pixels, 0 to disable (default: 1920)')
    image_group.add_argument('--image-threshold', type=int, default=DEFAULT_IMAGE_THRESHOLD,
                             help='Image file size threshold in bytes (default: 1048576 = 1MB)')

    # Flags
    parser.add_argument('--no-images', action='store_true',
                        help='Skip image compression')
    parser.add_argument('--no-videos', action='store_true',
                        help='Skip video compression')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without compressing')

    # Parse arguments - use provided argv or sys.argv
    args = parser.parse_args(argv)

    # Validate CRF range
    if not 0 <= args.crf <= 51:
        parser.error("CRF must be between 0 and 51")

    # Validate image quality range
    if not 1 <= args.image_quality <= 95:
        parser.error("Image quality must be between 1 and 95")

    # Run compression
    success = compress_pptx(
        input_pptx=args.input,
        output_pptx=args.output,
        crf=args.crf,
        preset=args.preset,
        max_height=args.max_height,
        audio_bitrate=args.audio_bitrate,
        image_quality=args.image_quality,
        image_max_dim=args.image_max_dim,
        image_threshold=args.image_threshold,
        skip_images=args.no_images,
        skip_videos=args.no_videos,
        dry_run=args.dry_run
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
