#!/usr/bin/env python3
"""Fetch YouTube transcripts from a channel or video URL(s).

Usage:
  # Single video
  python3 fetch_transcripts.py --video "https://www.youtube.com/watch?v=XXXXX"

  # Multiple videos
  python3 fetch_transcripts.py --video "URL1" --video "URL2"

  # Channel (N most recent)
  python3 fetch_transcripts.py --channel "https://www.youtube.com/@ChannelName" --count 20

  # Channel by ID
  python3 fetch_transcripts.py --channel-id "UCrXNkk4IESnqU-8GMad2vyA" --count 10

Output: JSON to stdout with video metadata + transcript text.
"""
import argparse
import json
import subprocess
import sys
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


def get_video_id(url: str) -> str:
    """Extract video ID from various YouTube URL formats."""
    import re
    patterns = [
        r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:embed/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return url


def get_channel_videos(channel_url: str, count: int) -> list:
    """Use yt-dlp to list recent videos from a channel."""
    cmd = [
        'yt-dlp', '--flat-playlist', '--no-download',
        '--playlist-end', str(count),
        '--print', '%(id)s\t%(title)s\t%(upload_date)s\t%(duration)s',
        channel_url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    videos = []
    for line in result.stdout.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) >= 3:
            videos.append({
                'id': parts[0],
                'title': parts[1] if len(parts) > 1 else '',
                'upload_date': parts[2] if len(parts) > 2 else '',
                'duration': parts[3] if len(parts) > 3 else '',
            })
    return videos


def get_video_metadata(video_id: str) -> dict:
    """Get video metadata via yt-dlp."""
    cmd = [
        'yt-dlp', '--no-download',
        '--print', '%(title)s\t%(upload_date)s\t%(duration)s\t%(channel)s\t%(description)s',
        f'https://www.youtube.com/watch?v={video_id}'
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        parts = result.stdout.strip().split('\t')
        return {
            'id': video_id,
            'title': parts[0] if len(parts) > 0 else '',
            'upload_date': parts[1] if len(parts) > 1 else '',
            'duration': parts[2] if len(parts) > 2 else '',
            'channel': parts[3] if len(parts) > 3 else '',
            'description': parts[4] if len(parts) > 4 else '',
        }
    except Exception:
        return {'id': video_id}


def get_transcript(video_id: str) -> str:
    """Fetch transcript text for a video."""
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)
        return '\n'.join(entry.text for entry in transcript)
    except (TranscriptsDisabled, NoTranscriptFound):
        return '[No transcript available]'
    except Exception as e:
        return f'[Transcript error: {e}]'


def main():
    parser = argparse.ArgumentParser(description='Fetch YouTube transcripts')
    parser.add_argument('--video', '-v', action='append', help='Video URL or ID (repeatable)')
    parser.add_argument('--channel', '-c', help='Channel URL')
    parser.add_argument('--channel-id', help='Channel ID')
    parser.add_argument('--count', '-n', type=int, default=10, help='Number of recent videos (channel mode)')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    args = parser.parse_args()

    videos = []

    if args.channel or args.channel_id:
        url = args.channel or f'https://www.youtube.com/channel/{args.channel_id}'
        videos = get_channel_videos(url, args.count)
    elif args.video:
        for v in args.video:
            vid = get_video_id(v)
            meta = get_video_metadata(vid)
            videos.append(meta)
    else:
        parser.print_help()
        sys.exit(1)

    results = []
    for v in videos:
        vid = v.get('id', '')
        if not vid:
            continue
        transcript = get_transcript(vid)
        results.append({
            **v,
            'transcript': transcript,
            'url': f'https://www.youtube.com/watch?v={vid}',
        })
        print(f"  ✓ {v.get('title', vid)[:60]}... ({len(transcript)} chars)", file=sys.stderr)

    output = json.dumps(results, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Saved {len(results)} transcripts to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()
