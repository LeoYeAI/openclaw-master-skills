# Virality Scoring — Gemini Video Analysis

Score reels before publishing using Gemini's video understanding. Upload the video, get a 0-100 virality score with detailed breakdowns. **Only publish reels scoring 70+.**

## Virality Prompt

Write this to `/tmp/virality_prompt.txt` before scoring:

```
You are a short-form video virality expert who has analyzed millions of TikTok and Instagram Reels. Analyze this video and score it on a 0-100 virality scale.

Scoring criteria:
- hook_strength: How strong is the opening 1-3 seconds at stopping the scroll?
- emotional_impact: Does it trigger an emotional response (relatability, shock, humor, empathy)?
- pacing_flow: Is the pacing tight with no dead time? Does it feel snappy?
- text_readability: Is text clear, well-positioned, high-contrast, and scannable?
- scroll_stop_power: Would this make someone stop mid-scroll in the first frame?
- completion_likelihood: Will viewers watch to the end? Is it short enough?
- shareability: Would someone send this to a friend or repost it?

Return ONLY valid JSON:
{"overall_score": <0-100>,"hook_strength": {"score": <0-100>, "reason": "<1 sentence>"},"emotional_impact": {"score": <0-100>, "reason": "<1 sentence>"},"pacing_flow": {"score": <0-100>, "reason": "<1 sentence>"},"text_readability": {"score": <0-100>, "reason": "<1 sentence>"},"scroll_stop_power": {"score": <0-100>, "reason": "<1 sentence>"},"completion_likelihood": {"score": <0-100>, "reason": "<1 sentence>"},"shareability": {"score": <0-100>, "reason": "<1 sentence>"},"top_strength": "<1 sentence>","top_weakness": "<1 sentence>","improvement_tip": "<1 sentence>"}
```

## Single Video Scoring

```bash
# 1. Upload video to Gemini File API
FILE_URI=$(curl -s -X POST \
  "https://generativelanguage.googleapis.com/upload/v1beta/files?key=$GEMINI_API_KEY" \
  -H "X-Goog-Upload-Command: start, upload, finalize" \
  -H "X-Goog-Upload-Header-Content-Type: video/mp4" \
  -H "Content-Type: video/mp4" \
  --data-binary @"reel-final.mp4" | python3 -c "import sys,json; print(json.load(sys.stdin)['file']['uri'])")

# 2. Wait for processing
sleep 4

# 3. Score with Gemini
VIRALITY_PROMPT=$(cat /tmp/virality_prompt.txt)
curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key=$GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"contents\": [{
      \"parts\": [
        {\"text\": \"$VIRALITY_PROMPT\"},
        {\"file_data\": {\"file_uri\": \"$FILE_URI\", \"mime_type\": \"video/mp4\"}}
      ]
    }],
    \"generationConfig\": {\"temperature\": 0.3, \"response_mime_type\": \"application/json\"}
  }"
```

## Batch Scoring (Python)

For scoring multiple reels, use a Python script for reliable JSON handling and rate-limit management:

```python
import sys, json, subprocess, time, os

gemini_key = os.environ["GEMINI_API_KEY"]
finals_dir = sys.argv[1]
prompt_text = open("/tmp/virality_prompt.txt").read()
videos = sorted([f for f in os.listdir(finals_dir) if f.endswith(".mp4")])
results = []

for i, vid in enumerate(videos):
    path = os.path.join(finals_dir, vid)
    print(f"[{i+1}/{len(videos)}] {vid}...", end=" ", flush=True)

    # Upload
    try:
        upload = subprocess.run([
            "curl", "-s", "-X", "POST",
            f"https://generativelanguage.googleapis.com/upload/v1beta/files?key={gemini_key}",
            "-H", "X-Goog-Upload-Command: start, upload, finalize",
            "-H", "X-Goog-Upload-Header-Content-Type: video/mp4",
            "-H", "Content-Type: video/mp4",
            "--data-binary", f"@{path}"
        ], capture_output=True, text=True, timeout=60)
        uri = json.loads(upload.stdout)["file"]["uri"]
    except Exception as e:
        print(f"UPLOAD ERR: {e}")
        continue

    time.sleep(5)  # Wait for video processing + rate limit buffer

    # Score
    try:
        payload = json.dumps({
            "contents": [{"parts": [
                {"text": prompt_text},
                {"file_data": {"file_uri": uri, "mime_type": "video/mp4"}}
            ]}],
            "generationConfig": {"temperature": 0.3, "response_mime_type": "application/json"}
        })
        score_resp = subprocess.run([
            "curl", "-s",
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key={gemini_key}",
            "-H", "Content-Type: application/json",
            "-d", payload
        ], capture_output=True, text=True, timeout=60)

        r = json.loads(score_resp.stdout)
        if "candidates" not in r:
            print(f"API ERR: {r.get('error', {}).get('message', 'unknown')[:60]}")
            time.sleep(8)
            continue
        d = json.loads(r["candidates"][0]["content"]["parts"][0]["text"])
        results.append((vid, d))
        print(f"Score: {d['overall_score']}")
    except Exception as e:
        print(f"SCORE ERR: {e}")
        continue

# Print ranked scorecard
ranked = sorted(results, key=lambda x: x[1]["overall_score"], reverse=True)
print(f"\n{'=' * 90}")
print(f"  VIRALITY SCORECARD — {time.strftime('%Y-%m-%d')}")
print(f"{'=' * 90}")
for vid, d in ranked:
    s = d["overall_score"]
    status = "P" if s >= 70 else "X"
    print(f"  {status} {s:>3}  {vid:<40} Hook:{d['hook_strength']['score']} Em:{d['emotional_impact']['score']} Pace:{d['pacing_flow']['score']} Text:{d['text_readability']['score']} Stop:{d['scroll_stop_power']['score']} Comp:{d['completion_likelihood']['score']} Share:{d['shareability']['score']}")
print(f"{'=' * 90}")
pub = sum(1 for _,d in results if d["overall_score"] >= 70)
print(f"  {len(results)}/{len(videos)} scored | {pub} publish-ready | {len(results)-pub} need rework")
```

**Rate limit note:** Gemini Flash Lite has ~10 RPM on free tier. The script adds 5-second delays. For 20+ videos, expect ~3 minutes.

## Score Thresholds

| Score | Verdict | Action |
|-------|---------|--------|
| **85-100** | Excellent | Publish immediately, prioritize for best account |
| **70-84** | Good | Publish — minor tweaks optional |
| **55-69** | Needs work | Rework hook or pacing before publishing |
| **0-54** | Weak | Re-edit significantly or discard |

## Using Scores to Improve Reels

When a reel scores below 70, check which sub-score is dragging it down:

- **Low hook_strength (<70):** Change the opening UGC clip or text hook — needs more emotional punch
- **Low emotional_impact (<70):** The UGC reaction doesn't match the text emotion — try a different clip
- **Low pacing_flow (<70):** Too much dead time — tighten cuts, speed up transitions
- **Low text_readability (<70):** Text too small, bad positioning, or low contrast — recheck Green Zone placement
- **Low scroll_stop_power (<70):** First frame is weak — use a more expressive face or bolder text
- **Low completion_likelihood (<70):** Video too long or loses interest — trim to under 10s
- **Low shareability (<70):** Content isn't relatable enough — try a more universal hook
