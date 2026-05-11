# Green Zone Reference (Platform Safe Areas)

The Green Zone is where NO platform UI overlaps your content. **ALL text MUST be placed here.**

## Universal Green Zone (safe on ALL platforms — DEFAULT)

```
Canvas:     1080 x 1920 px
Top:        210 px from top
Bottom:     440 px from bottom (safe Y ends at 1480)
Left:       60 px from left
Right:      120 px from right  (safe X ends at 960)

Safe area:  900 x 1270 px
            X: 60 to 960
            Y: 210 to 1480
```

```
+-------------------------------------+
|           TOP MARGIN (210px)        | <- Username, follow, sound label
|  +-----------------------------+    |
|  |                             | R  |
|  |       GREEN ZONE            | I  |
|  |    (900 x 1270 px)         | G  |
|  |    All text goes here       | H  |
|  |                             | T  |
|  |                             |    |
|  +-----------------------------+    |
|           BOTTOM MARGIN (440px)     | <- Captions, CTA, hashtags
+-------------------------------------+
```

## Text Position Presets

| Position | Y Value | X Formula | Best For |
|----------|---------|-----------|----------|
| **Upper GZ** | `280-340` | `x=(60+(900-text_w)/2)` | Hook text (line 1) |
| **Upper-mid** | `360-440` | same | Hook text (lines 2-3) |
| **Center GZ** | `(210+(1270-text_h)/2)` | same | Big statements |
| **Lower-mid GZ** | `1100` | same | Supporting text |
| **Lower GZ** | `1380` | same | CTA text |

**Horizontal centering formula (always use this):**
```
x=(60+(900-text_w)/2)
```

## Text Style Presets (TikTok Sans)

**Font paths:**
- macOS: `$HOME/Library/Fonts/TikTokSans*.ttf`
- Linux: `$HOME/.local/share/fonts/TikTokSans*.ttf`

**"Hook" — Upper green zone, attention-grabbing:**
```
fontfile=$HOME/Library/Fonts/TikTokSansDisplayBold.ttf:fontsize=64:fontcolor=white:borderw=4:bordercolor=black:x=(60+(900-text_w)/2):y=310
```

**"Hook with Box" — With semi-transparent background:**
```
fontfile=$HOME/Library/Fonts/TikTokSansDisplayBold.ttf:fontsize=64:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=20:x=(60+(900-text_w)/2):y=310
```

**"CTA" — Lower green zone, call to action:**
```
fontfile=$HOME/Library/Fonts/TikTokSansDisplayBold.ttf:fontsize=52:fontcolor=white:borderw=3:bordercolor=black:x=(60+(900-text_w)/2):y=1380
```

**"Subtitle" — Lower green zone with background:**
```
fontfile=$HOME/Library/Fonts/TikTokSansTextMedium.ttf:fontsize=48:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=15:x=(60+(900-text_w)/2):y=1350
```

## Font Weights

| Weight | File | Use For |
|--------|------|---------|
| **Display Bold** | `TikTokSansDisplayBold.ttf` | Hook text, CTAs (DEFAULT) |
| **Display Black** | `TikTokSansDisplayBlack.ttf` | Extra bold impact |
| **Display Medium** | `TikTokSansDisplayMedium.ttf` | Secondary hooks |
| **Text Bold** | `TikTokSansTextBold.ttf` | Bold captions |
| **Text Medium** | `TikTokSansTextMedium.ttf` | Body text, subtitles |

## Platform-Specific Green Zones

Use these only when targeting a single platform.

**TikTok:**
```
X: 60 to 960, Y: 150 to 1480
Safe area: 900 x 1330 px
GZ_CENTER_X=510  GZ_CENTER_Y=815
```

**Instagram Reels:**
```
X: 44 to 996, Y: 210 to 1610
Safe area: 952 x 1400 px
GZ_CENTER_X=520  GZ_CENTER_Y=910
```

**YouTube Shorts:**
```
X: 60 to 984, Y: 170 to 1530
Safe area: 924 x 1360 px
GZ_CENTER_X=522  GZ_CENTER_Y=850
```

## Why Each Zone Exists

| Zone | What Covers It |
|------|---------------|
| **Top** | Username, follow button, sound label, "Sponsored" tag |
| **Right** | Like, comment, share, bookmark buttons, profile avatar |
| **Bottom** | Caption text, hashtags, CTA buttons, sound ticker |
| **Left** | Generally clear, small margin for safety |

## NEVER Use These Positions

These fall OUTSIDE the green zone and will be covered by platform UI:
- `y < 210` -> covered by top UI
- `y > 1480` -> covered by bottom caption/CTA
- `x > 960` -> covered by right-side engagement buttons
