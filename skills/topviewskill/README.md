# Topview AI Skill

An AI agent skill that lets you generate professional videos, images, talking avatars, and audio by simply describing what you want in natural language — no manual operations, no learning curve.

This skill follows the [Agent Skills specification](https://agentskills.io/specification) and works with any compatible AI coding assistant (Cursor, Claude Code, etc.).

## What Can You Do With This?

Install the skill, then just tell the AI what you need. Here are some examples:

### One-Sentence Creation

| You say... | You get... |
|------------|------------|
| "Generate 5 product photos in different styles" | 5 AI-generated images, batch-produced in parallel |
| "Make a 10-second video of a cat walking on the beach at sunset" | An AI-generated video clip |
| "Use this photo to create a video of me introducing our new product" | A talking-head avatar video with lip-sync |
| "Put this water bottle on a fashion model" | A composite image of a model holding your product |
| "Read this paragraph in a warm female voice" | A text-to-speech audio file |
| "Clone my voice from this audio sample" | A custom voice ready to use for any future narration |
| "Remove the background from this product photo" | A clean cutout PNG |
| "Change the background of this photo to a tropical beach" | An AI-edited image |
| "Create a new video that mimics the style of this reference clip" | A style-transferred video |

### Combined Workflows

The real power is chaining these capabilities together. Describe a goal and the AI orchestrates the entire pipeline for you:

**E-commerce product launch kit** — "I have a product photo, help me create a full set of marketing materials." The AI will remove the background, generate product-on-model showcase images in multiple poses, create a talking-head avatar video announcing the product, and batch-generate social media banners in different aspect ratios. One conversation, a complete marketing asset library.

**Educational video series** — "Turn this article about climate change into a video series." The AI writes scripts for each segment, generates illustrations for key concepts, creates avatar presenter videos, and produces narration with a chosen voice. Multiple videos from a single article.

**Multilingual content** — "Take this product demo script and create versions in English, Japanese, and Spanish." The AI generates text-to-speech in each language with appropriate voices, then creates avatar videos with the same portrait but different audio tracks. Instant multi-language content from one script.

**Storyboard-to-video** — "I want a 30-second animated ad with these 4 scenes." The AI generates an image for each scene, animates each into a video clip, and delivers a set of sequential clips ready for editing. From text descriptions to motion in one session.

**Brand-consistent content batch** — "Generate 10 social media posts for this week, all in our brand style." The AI creates a reference image establishing the visual style, then batch-produces variations for different topics using the same style. Consistent branding across a whole content calendar.

**Digital spokesperson** — "I want to be the face of my channel without filming every episode." Upload one portrait and clone your voice, then just provide scripts for each episode. The AI generates avatar videos in your likeness and voice, with AI-generated illustrations as B-roll.

**Product demo with narration** — "Walk through the features of this app using these screenshots." The AI generates narration from your feature descriptions, animates each screenshot into video clips, and creates avatar intro/outro segments. A polished demo from static screenshots.

### How It Works

1. **Install** — `npx skills add topviewai/skill`
2. **Log in** — run `python scripts/auth.py login` (one-time setup)
3. **Create** — tell the AI what you want in plain language. It picks the right tools, models, and parameters automatically.

**Your imagination is the only limit** — the examples above are just starting points. You can freely combine image generation, video creation, avatar, voice cloning, background removal, and more into any workflow you can think of. Describe your creative vision in your own words, and the AI will figure out how to make it happen.

## Installation

```bash
npx skills add topviewai/skill
```

## Available Modules

Under the hood, the skill uses these modules. You don't need to call them directly — just describe what you want and the AI agent picks the right tool.

| Module | Script | Description |
|--------|--------|-------------|
| [Avatar4](references/avatar4.md) | `scripts/avatar4.py` | Talking avatar videos from a photo |
| [Video Gen](references/video_gen.md) | `scripts/video_gen.py` | Image-to-video, text-to-video, omni reference video generation |
| [AI Image](references/ai_image.md) | `scripts/ai_image.py` | Text-to-image and AI image editing (10+ models) |
| [Remove BG](references/remove_bg.md) | `scripts/remove_bg.py` | Remove image background |
| [Product Avatar](references/product_avatar.md) | `scripts/product_avatar.py` | Model showcase product image with avatar templates |
| [Text2Voice](references/text2voice.md) | `scripts/text2voice.py` | Text-to-speech audio generation |
| [Voice](references/voice.md) | `scripts/voice.py` | Voice list/search, voice cloning, delete custom voices |
| [Board](references/board.md) | `scripts/board.py` | Board management — organize and view results on web |
| [User](references/user.md) | `scripts/user.py` | Credit balance and usage history |

## Configuration

Requires Python 3.8+ and a Topview AI account. Authenticate via the device flow:

```bash
pip install -r scripts/requirements.txt
python scripts/auth.py login
```

This sets `TOPVIEW_UID` and `TOPVIEW_API_KEY` automatically. You can also set them manually:

```bash
export TOPVIEW_UID="your-uid"
export TOPVIEW_API_KEY="your-api-key"
```

## License

See [LICENSE.txt](LICENSE.txt).
