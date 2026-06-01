# veo-3.1-fast — Video Generation (Google)

Faster version of Veo 3.1. Same quality level with faster generation. Best for rapid iteration.

## Parameters

Same as [veo-3.1.md](veo-3.1.md). All parameters identical.

## Pricing

| | with_audio | without_audio |
|---|---|---|
| Per second | 15 credits | 10 credits |
| 4s video | 60 credits | 40 credits |
| 6s video | 90 credits | 60 credits |
| 8s video | 120 credits | 80 credits |

## Example

```python
gen = pony_flash.video.generate(
    model="veo-3.1-fast",
    prompt="A timelapse of clouds over a cityscape",
    duration=4,
    resolution="720p",
    generate_audio=False,
)
```
