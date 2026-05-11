---
name: nano-banana-prompting-skill
description: Transform natural language image requests into optimized structured prompts for Gemini image generation. Automatically detects style and builds the perfect prompt — cinematic, illustration, anime, 3D, watercolor, product, and more.
metadata:
  {
    "openclaw":
      {
        "emoji": "🎨",
        "requires": { "bins": ["uv"], "env": ["GEMINI_API_KEY"] },
        "primaryEnv": "GEMINI_API_KEY",
      },
  }
---

# Gemini Image Prompting

This skill transforms simple, natural image requests into **optimized structured prompts** that produce dramatically better results from Gemini 3 Pro Image.

Instead of sending a plain text prompt (which produces generic, "AI slop" results), this skill builds a **structured JSON prompt** with the right technical details for the detected style — camera specs for photography, art techniques for illustration, render settings for 3D, and more.

## How to Use

When the user asks you to generate or edit an image:

1. **Read the user's request** — understand what they want (subject, mood, style)
2. **Detect the style** — use the Style Detection rules below
3. **Build the structured JSON prompt** — follow the template for that style
4. **Call the generator:**

```bash
uv run {nano-banana-pro-dir}/scripts/generate_image.py \
  --prompt '<YOUR_JSON_PROMPT>' \
  --filename "<descriptive-name>.png" \
  --resolution 2K
```

Replace `{nano-banana-pro-dir}` with the path to the nano-banana-pro skill (typically bundled with OpenClaw).

**For image editing** (user provides a reference image):
```bash
uv run {nano-banana-pro-dir}/scripts/generate_image.py \
  --prompt '<YOUR_JSON_PROMPT>' \
  --filename "<output-name>.png" \
  -i "/path/to/reference.png" \
  --resolution 2K
```

### Security Note
The `--filename` argument should always be a simple file path constructed by the agent (e.g., `gecko-running.png`). Never pass unsanitized user input directly as the filename. The agent should derive a safe, descriptive filename from the context.

### Output Location
Save images to the user's Desktop or the path they specify:
- Default: `~/Desktop/<descriptive-name>.png`
- Use descriptive filenames: `gecko-coding-night.png`, not `output.png`

---

## Style Detection

Detect the style from the user's request. Look for keywords, context, and intent:

| Style | Trigger Keywords / Context |
|-------|---------------------------|
| **Cinematic / Photorealistic** | "photo", "realistic", "cinematic", "portrait", "street", "landscape", real-world scenes, people, animals in real settings |
| **Product / Studio** | "product shot", "studio", "mockup", "packaging", "e-commerce", objects on clean backgrounds |
| **Street / Documentary** | "candid", "street", "reportage", "documentary", "raw", urban scenes |
| **Illustration / Digital Art** | "illustration", "digital art", "concept art", "fantasy art", "draw", "artwork" |
| **Anime / Manga** | "anime", "manga", "cel shaded", "studio ghibli", Japanese animation style |
| **3D / Pixar** | "3D", "Pixar", "render", "CGI", "clay", "isometric", cartoon characters |
| **Watercolor / Traditional** | "watercolor", "oil painting", "sketch", "pencil", "pastel", "charcoal", traditional media |
| **Minimalist / Graphic** | "logo", "icon", "flat", "minimal", "vector", "graphic design", "poster" |
| **Surreal / Abstract** | "surreal", "abstract", "dreamlike", "psychedelic", "impossible", "Dalí" |

**If no style is obvious**, default to **Cinematic / Photorealistic** — it's the most versatile and produces the best baseline quality.

**If the user specifies a style explicitly**, always respect that over auto-detection.

---

## Structured Prompt Templates

### 🎬 Cinematic / Photorealistic

```json
{
  "instruction": "<one-line description of the final image>",
  "subject": {
    "description": "<main subject in detail>",
    "clothing": "<if applicable>",
    "expression": "<facial expression or mood>",
    "pose": "<body position, action>",
    "details": "<distinguishing features, textures>"
  },
  "scene": {
    "setting": "<location/environment>",
    "key_elements": "<important objects in the scene>",
    "background": "<what's behind the subject>",
    "foreground": "<what's in front, if any>",
    "time_of_day": "<morning, golden hour, night, etc.>"
  },
  "photography": {
    "camera": "<Sony A7IV | Hasselblad X2D | Canon R5 | ARRI Alexa 65 | Leica M11>",
    "lens": "<24mm f/1.4 | 35mm f/1.4 | 50mm f/1.2 | 85mm f/1.8 | 135mm f/2>",
    "shot_type": "<wide | medium | close-up | extreme close-up | aerial | low angle>",
    "depth_of_field": "<shallow with bokeh | deep | tilt-shift>",
    "lighting": "<natural golden hour | chiaroscuro | rim light | neon | overcast soft | studio three-point>",
    "film_stock": "<Kodak Portra 400 | Fujifilm Pro 400H | Kodak Ektar 100 | CineStill 800T | Ilford HP5>",
    "texture": "<subtle film grain | clean digital | heavy grain>"
  },
  "mood": "<emotional atmosphere in one sentence>",
  "color_palette": "<dominant colors or color grading style>",
  "aspect_ratio": "<1:1 | 16:9 | 4:3 | 9:16 | 3:2>",
  "quality": "8K, photorealistic, cinematic, RAW photo",
  "negative": "no text, no watermark, no deformed faces, no extra limbs, no blurry"
}
```

**Camera selection guide:**
- Portraits → Hasselblad X2D or Canon R5 + 85mm
- Street/documentary → Leica M11 + 35mm
- Landscapes/cinematic → Sony A7IV + 24mm or ARRI Alexa 65
- Night/low light → Sony A7IV + 50mm f/1.2 + CineStill 800T
- Fashion → Hasselblad X2D + 80mm

### 📸 Product / Studio

```json
{
  "instruction": "<product shot description>",
  "subject": {
    "product": "<item name and type>",
    "material": "<glass, metal, fabric, wood, plastic, ceramic>",
    "color": "<product colors>",
    "details": "<logos, textures, unique features>"
  },
  "scene": {
    "backdrop": "<seamless white | gradient | textured surface | lifestyle context>",
    "surface": "<marble | wood | concrete | acrylic | fabric>",
    "props": "<complementary objects if any>"
  },
  "photography": {
    "camera": "Hasselblad X2D",
    "lens": "90mm f/3.2 macro",
    "shot_type": "<hero shot | flat lay | 45-degree | floating | exploded view>",
    "lighting": "<softbox | ring light | natural window | dramatic single source | backlit>",
    "reflections": "<subtle | mirror-like | none>",
    "depth_of_field": "shallow, product sharp, background soft"
  },
  "mood": "<clean and premium | warm and inviting | bold and modern>",
  "color_palette": "<brand-aligned colors>",
  "aspect_ratio": "1:1",
  "quality": "8K, commercial photography, sharp detail, color-accurate",
  "negative": "no text, no watermark, no dust, no scratches"
}
```

### 🖌️ Illustration / Digital Art

```json
{
  "instruction": "<illustration description>",
  "subject": {
    "character": "<character description>",
    "expression": "<emotion>",
    "pose": "<action or stance>",
    "details": "<costume, accessories, distinctive features>"
  },
  "scene": {
    "setting": "<world/environment>",
    "key_elements": "<important scene elements>",
    "atmosphere": "<fog, particles, light rays, sparks>"
  },
  "art_style": {
    "medium": "<digital painting | concept art | comic book | storybook | gouache>",
    "technique": "<cel shading | painterly | line art with color | crosshatching>",
    "reference_artists": "<1-2 artist names for style reference>",
    "color_approach": "<vibrant saturated | muted earthy | monochromatic | complementary>"
  },
  "composition": {
    "framing": "<rule of thirds | centered | dynamic diagonal | symmetrical>",
    "perspective": "<eye level | bird's eye | worm's eye | isometric>",
    "focal_point": "<where the eye should go>"
  },
  "mood": "<epic and dramatic | whimsical and playful | dark and moody>",
  "color_palette": "<specific colors or palette description>",
  "aspect_ratio": "<16:9 | 3:2 | 1:1>",
  "quality": "highly detailed illustration, trending on ArtStation, masterpiece",
  "negative": "no text, no watermark, no photo-realistic, no AI artifacts"
}
```

### 🌸 Anime / Manga

```json
{
  "instruction": "<anime scene description>",
  "subject": {
    "character": "<character description>",
    "hair": "<style, color>",
    "eyes": "<color, expression>",
    "outfit": "<clothing details>",
    "pose": "<action or expression>"
  },
  "scene": {
    "setting": "<location>",
    "atmosphere": "<cherry blossoms, rain, sunset glow, sparkles>",
    "background_style": "<detailed | simplified | gradient wash>"
  },
  "art_style": {
    "studio_reference": "<Studio Ghibli | Kyoto Animation | Ufotable | MAPPA | Trigger | Makoto Shinkai>",
    "line_weight": "<thin and clean | bold and expressive | variable>",
    "shading": "<flat cel | soft gradient | dramatic shadow>",
    "era": "<modern anime | 90s retro | 80s vintage>"
  },
  "composition": {
    "framing": "<close-up portrait | action shot | scenic wide | over-the-shoulder>",
    "effects": "<speed lines | light flares | motion blur | sparkle overlay>"
  },
  "mood": "<heartwarming | intense action | melancholic | comedic>",
  "color_palette": "<pastel soft | vibrant saturated | dark moody | warm sunset>",
  "aspect_ratio": "16:9",
  "quality": "anime key visual, high detail, studio quality, clean lines",
  "negative": "no western cartoon style, no 3D, no photorealistic, no deformed hands"
}
```

### 🧸 3D / Pixar / CGI

```json
{
  "instruction": "<3D scene description>",
  "subject": {
    "character": "<character description>",
    "material": "<clay | plastic | rubber | fur | fabric>",
    "proportions": "<chibi | realistic | stylized | exaggerated>",
    "expression": "<emotion>",
    "pose": "<stance or action>"
  },
  "scene": {
    "environment": "<setting>",
    "props": "<objects in scene>",
    "scale": "<miniature diorama | life-size | macro>"
  },
  "render": {
    "engine": "<Pixar RenderMan | Blender Cycles | Unreal Engine 5 | Octane>",
    "style": "<Pixar | DreamWorks | Aardman claymation | Nendoroid figure>",
    "materials": "<subsurface scattering | glossy plastic | matte clay | fabric texture>",
    "lighting": "<three-point studio | HDRI environment | dramatic rim | soft ambient>",
    "effects": "<ambient occlusion | global illumination | volumetric fog | depth of field>"
  },
  "mood": "<playful and colorful | dramatic and cinematic | cozy and warm>",
  "color_palette": "<bright primary | pastel | earthy muted | vibrant candy>",
  "aspect_ratio": "16:9",
  "quality": "3D render, Pixar quality, high detail, raytraced, 8K",
  "negative": "no 2D, no flat, no sketch, no watermark, no text"
}
```

### 🎨 Watercolor / Traditional Art

```json
{
  "instruction": "<painting description>",
  "subject": {
    "description": "<what to paint>",
    "details": "<important visual details>"
  },
  "scene": {
    "setting": "<environment or abstract>",
    "elements": "<supporting visual elements>"
  },
  "traditional_art": {
    "medium": "<watercolor | oil paint | acrylic | gouache | pastel | charcoal | pencil | ink wash>",
    "paper": "<cold press watercolor | hot press | canvas | toned paper | rice paper>",
    "technique": "<wet-on-wet | dry brush | impasto | glazing | stippling | hatching | wash>",
    "brush": "<round | flat | fan | palette knife | sponge>",
    "finish": "<loose and expressive | tight and detailed | abstract | impressionistic>"
  },
  "composition": {
    "framing": "<centered | rule of thirds | asymmetric>",
    "white_space": "<generous margins | edge-to-edge | vignette>"
  },
  "mood": "<serene | vibrant | nostalgic | raw and emotional>",
  "color_palette": "<limited palette (3-4 colors) | full spectrum | monochrome wash>",
  "aspect_ratio": "3:2",
  "quality": "fine art quality, museum worthy, masterful brushwork, visible texture",
  "negative": "no digital look, no photorealistic, no text, no watermark, no AI artifacts"
}
```

### ✏️ Minimalist / Graphic Design

```json
{
  "instruction": "<design description>",
  "subject": {
    "element": "<main visual element>",
    "style": "<geometric | organic | typographic | iconographic>"
  },
  "design": {
    "approach": "<flat design | material design | swiss style | brutalist | retro>",
    "grid": "<centered | asymmetric | modular grid>",
    "shapes": "<circles | rectangles | triangles | organic blobs | line art>",
    "contrast": "<high contrast | subtle | duotone>"
  },
  "color_palette": "<2-3 specific colors or palette name>",
  "background": "<solid color | gradient | textured | transparent>",
  "aspect_ratio": "1:1",
  "quality": "clean vector quality, crisp edges, professional graphic design",
  "negative": "no photorealistic, no complex textures, no gradients unless specified, no text unless requested"
}
```

### 🌀 Surreal / Abstract

```json
{
  "instruction": "<surreal scene description>",
  "subject": {
    "central_element": "<main impossible or dreamlike element>",
    "transformation": "<how reality is bent or broken>",
    "symbolism": "<underlying meaning or motif>"
  },
  "scene": {
    "reality_level": "<slightly off | dreamlike | fully impossible | cosmic>",
    "environment": "<melting landscape | infinite space | underwater sky | fractal world>",
    "scale_distortion": "<giant small things | tiny big things | impossible geometry>"
  },
  "art_style": {
    "reference": "<Dalí | Magritte | Escher | Beksinski | James Jean | Android Jones>",
    "medium": "<hyperrealistic oil | digital surrealism | mixed media | collage>",
    "technique": "<photobashing | matte painting | double exposure | glitch>"
  },
  "mood": "<unsettling beauty | peaceful absurdity | cosmic wonder | dark fantasy>",
  "color_palette": "<describe the color world>",
  "aspect_ratio": "16:9",
  "quality": "highly detailed, surrealist masterpiece, museum quality",
  "negative": "no text, no watermark, no generic, no stock photo feel"
}
```

---

## Prompting Rules (ALL styles)

### Always Do:
1. **Be specific** — "mint-green gecko" not "a gecko", "warm golden hour" not "nice light"
2. **Include negative prompt** — always specify what to avoid
3. **Pick an aspect ratio** — match the content (landscape 16:9, portrait 9:16, square 1:1)
4. **Add sensory details** — textures, temperatures, sounds implied visually
5. **One focal point** — every image needs a clear subject
6. **Match quality keywords to style** — "8K photorealistic" for photos, "trending on ArtStation" for illustrations
7. **Color palette matters** — specify colors or a grading reference, don't leave it to chance

### Never Do:
1. ❌ Don't include text/words in the image (Gemini renders text poorly)
2. ❌ Don't over-specify (pick 1 camera, 1 lens, not 3 options)
3. ❌ Don't mix conflicting styles ("photorealistic anime" — pick one)
4. ❌ Don't use generic prompts ("a beautiful sunset" — add specifics)
5. ❌ Don't forget the negative prompt
6. ❌ Don't request NSFW content

### Resolution Guide:
- **1K** — Quick drafts, thumbnails, iteration
- **2K** — Social media, general use (best quality/cost ratio)
- **4K** — Print, hero images, final deliverables

---

## Examples

### User says: "make me a gecko eating pizza on a skateboard"

**Detected style:** 3D / Pixar (fun character scene)

```json
{
  "instruction": "A cute mint-green gecko character riding a skateboard while eating a large slice of pepperoni pizza",
  "subject": {
    "character": "small mint-green gecko with big expressive pale pink eyes and a wide happy grin",
    "material": "smooth glossy skin with subtle subsurface scattering",
    "proportions": "stylized chibi, slightly oversized head",
    "expression": "pure joy, eyes half-closed savoring the pizza",
    "pose": "standing on a moving skateboard, one hand holding pizza slice, cheese stretching"
  },
  "scene": {
    "environment": "sunny Venice Beach boardwalk, palm trees, blue sky",
    "props": "worn wooden skateboard with flame decals, pizza box on a nearby bench",
    "scale": "life-size character in real-world setting"
  },
  "render": {
    "engine": "Pixar RenderMan",
    "style": "Pixar",
    "materials": "subsurface scattering on gecko skin, glossy cheese, matte concrete",
    "lighting": "warm golden hour sunlight with soft shadows",
    "effects": "subtle motion blur on skateboard wheels, depth of field"
  },
  "mood": "carefree summer vibes, playful and fun",
  "color_palette": "warm yellows, mint green, sky blue, pizza orange",
  "aspect_ratio": "16:9",
  "quality": "3D render, Pixar quality, high detail, raytraced, 8K",
  "negative": "no 2D, no flat, no text, no watermark, no dark mood"
}
```

### User says: "a samurai in the rain, dramatic"

**Detected style:** Cinematic / Photorealistic

```json
{
  "instruction": "A lone samurai standing in heavy rain at night, katana drawn, cinematic and dramatic",
  "subject": {
    "description": "weathered samurai warrior, middle-aged, battle-scarred",
    "clothing": "dark indigo hakama and kimono, worn leather chest armor, straw sandals",
    "expression": "intense focus, eyes locked forward, jaw set",
    "pose": "standing in chudan-no-kamae stance, katana held at center",
    "details": "rain droplets on blade edge catching light, wet hair tied in topknot"
  },
  "scene": {
    "setting": "abandoned temple courtyard with stone lanterns",
    "key_elements": "heavy rainfall, puddles reflecting lantern light",
    "background": "dark silhouette of temple roof, mist rolling between pillars",
    "foreground": "rain splashing on stone ground, shallow puddles",
    "time_of_day": "deep night, moonless"
  },
  "photography": {
    "camera": "ARRI Alexa 65",
    "lens": "50mm f/1.2",
    "shot_type": "medium shot, slightly low angle",
    "depth_of_field": "shallow, rain drops in foreground out of focus",
    "lighting": "single warm lantern as key light from left, cool rain backlit by distant light, rim light on shoulders",
    "film_stock": "CineStill 800T",
    "texture": "subtle film grain"
  },
  "mood": "tense calm before the storm, honor and solitude",
  "color_palette": "deep indigo, warm amber lantern glow, cool steel grey",
  "aspect_ratio": "16:9",
  "quality": "8K, photorealistic, cinematic, RAW photo",
  "negative": "no text, no watermark, no deformed faces, no blurry, no anime style"
}
```

### User says: "paint me some sunflowers, like watercolor"

**Detected style:** Watercolor / Traditional

```json
{
  "instruction": "A loose, expressive watercolor painting of sunflowers in a ceramic vase",
  "subject": {
    "description": "five sunflowers in various stages of bloom, some drooping slightly",
    "details": "petals ranging from bright yellow to burnt sienna, dark brown seed heads with visible texture"
  },
  "scene": {
    "setting": "simple tabletop, implied window light",
    "elements": "rustic blue ceramic vase, a few fallen petals on the surface, soft shadow"
  },
  "traditional_art": {
    "medium": "watercolor",
    "paper": "cold press watercolor paper, visible tooth texture",
    "technique": "wet-on-wet for soft petal edges, dry brush for seed head texture, controlled wash for background",
    "brush": "large round for washes, small round for details",
    "finish": "loose and expressive, some areas left unfinished showing white paper"
  },
  "composition": {
    "framing": "slightly off-center, flowers extending above frame edge",
    "white_space": "generous margins, breathing room around the vase"
  },
  "mood": "warm, nostalgic, peaceful afternoon light",
  "color_palette": "cadmium yellow, burnt sienna, cerulean blue, sap green — limited palette",
  "aspect_ratio": "3:2",
  "quality": "fine art quality, museum worthy, masterful brushwork, visible paper texture",
  "negative": "no digital look, no photorealistic, no text, no watermark, no harsh edges"
}
```

---

## Editing / Reference Images

When the user provides a reference image to edit or use as inspiration:

1. **Include the image** with `-i` flag
2. **Describe what to change** in the instruction field
3. **Keep the JSON structure** — same style detection and template applies
4. **Be explicit** about what to preserve vs change

```bash
uv run {nano-banana-pro-dir}/scripts/generate_image.py \
  --prompt '<JSON_PROMPT>' \
  --filename "edited-output.png" \
  -i "/path/to/original.png" \
  --resolution 2K
```

For character consistency across multiple images, always include the same reference image(s) and describe the character identically in the subject field.

---

## Quick Reference: Style → Key Fields

| Style | Must-Have Fields | Key Differentiator |
|-------|-----------------|-------------------|
| Cinematic | photography.camera, lens, film_stock | Real camera specs sell the realism |
| Product | photography.lighting, surface, reflections | Clean, commercial precision |
| Illustration | art_style.medium, technique, reference_artists | Artist references anchor the style |
| Anime | art_style.studio_reference, line_weight, shading | Studio name = instant style match |
| 3D/Pixar | render.engine, style, materials | Render engine + material physics |
| Watercolor | traditional_art.medium, paper, technique | Paper texture + brush technique |
| Minimalist | design.approach, shapes, contrast | Less is more, precision matters |
| Surreal | art_style.reference, reality_level, transformation | Named surrealist = instant vibe |
