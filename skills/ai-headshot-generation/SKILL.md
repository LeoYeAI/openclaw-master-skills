---
name: ai-headshot-generation
description: Generate professional AI headshots from casual photos using each::sense AI. Create corporate portraits, LinkedIn photos, executive headshots, team photos, and more with consistent, professional quality.
metadata:
  author: eachlabs
  version: "1.0"
---

# AI Headshot Generation

Generate professional AI headshots from casual photos or text descriptions using each::sense. This skill creates polished, professional portraits suitable for corporate use, social media profiles, resumes, and marketing materials.

## Features

- **Corporate Headshots**: Professional portraits for company websites and directories
- **LinkedIn Photos**: Optimized headshots for professional networking
- **Executive Portraits**: Premium headshots for C-suite and leadership
- **Team Photos**: Consistent style across multiple team members
- **Background Options**: Office, studio, gradient, or custom backgrounds
- **Outfit Changes**: Transform casual attire to professional business wear
- **Expression Variations**: Generate multiple expressions from same source
- **Multi-Platform**: Optimized for various aspect ratios and use cases

## Quick Start

```bash
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Create a professional corporate headshot from this casual photo. Clean background, professional lighting, business appropriate appearance.",
    "mode": "max",
    "image_urls": ["https://example.com/casual-photo.jpg"]
  }'
```

## Headshot Formats & Sizes

| Use Case | Aspect Ratio | Recommended Size | Notes |
|----------|--------------|------------------|-------|
| LinkedIn | 1:1 | 400x400 to 800x800 | Square crop, head-and-shoulders |
| Corporate Website | 3:4 | 600x800 | Standard portrait orientation |
| Resume/CV | 1:1 or 3:4 | 300x300 or 300x400 | Clean, minimal background |
| Email Signature | 1:1 | 150x150 to 300x300 | Small but recognizable |
| Speaker Profile | 1:1 or 16:9 | 800x800 or 1920x1080 | Conference/event use |
| Team Page | 1:1 | 500x500 | Consistent across team |

## Use Case Examples

### 1. Corporate Headshot from Casual Photo

Transform a casual selfie or personal photo into a polished corporate headshot.

```bash
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Transform this casual photo into a professional corporate headshot. Use a clean neutral gray background, soft professional studio lighting, and ensure the subject looks polished and approachable. Keep the likeness accurate.",
    "mode": "max",
    "image_urls": ["https://example.com/casual-selfie.jpg"]
  }'
```

### 2. LinkedIn Profile Headshot

Create an optimized headshot specifically for LinkedIn that conveys professionalism and approachability.

```bash
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Create a LinkedIn-optimized professional headshot from this photo. Square 1:1 format, friendly but professional expression, clean blurred office background, warm natural lighting. The subject should appear confident and approachable.",
    "mode": "max",
    "image_urls": ["https://example.com/source-photo.jpg"]
  }'
```

### 3. Executive Headshot

Premium quality headshot for C-suite executives, board members, and senior leadership.

```bash
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Create a premium executive headshot from this photo. Dark sophisticated background with subtle gradient, dramatic professional lighting, formal business attire appearance. The subject should convey authority, confidence, and leadership. Magazine cover quality.",
    "mode": "max",
    "image_urls": ["https://example.com/ceo-casual.jpg"]
  }'
```

### 4. Team Headshots (Consistent Style)

Generate matching headshots for team members to ensure visual consistency across your organization.

```bash
# First team member - establish the style
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Create a professional team headshot with these specifications: light gray background, soft diffused lighting from the left, 1:1 square format, head and shoulders framing. Professional but friendly expression. This will be the template style for our entire team.",
    "session_id": "team-headshots-2024",
    "mode": "max",
    "image_urls": ["https://example.com/team-member-1.jpg"]
  }'

# Second team member - maintain consistency
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Create a headshot for this team member using the exact same style as the previous one - same background, lighting, framing, and overall aesthetic.",
    "session_id": "team-headshots-2024",
    "mode": "max",
    "image_urls": ["https://example.com/team-member-2.jpg"]
  }'

# Third team member
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Create a headshot for this team member matching our established team style.",
    "session_id": "team-headshots-2024",
    "mode": "max",
    "image_urls": ["https://example.com/team-member-3.jpg"]
  }'
```

### 5. Headshot with Different Backgrounds

Generate the same headshot with various background options.

```bash
# Office background
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Create a professional headshot with a blurred modern office background. Glass windows, city view visible but out of focus. Natural daylight feel.",
    "session_id": "background-variations",
    "mode": "max",
    "image_urls": ["https://example.com/source-photo.jpg"]
  }'

# Studio gradient background
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Now create the same headshot but with a classic studio gradient background - deep blue fading to lighter blue. Keep the same professional lighting on the subject.",
    "session_id": "background-variations",
    "mode": "max"
  }'

# Nature/outdoor background
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Create another variation with a natural outdoor background - soft green foliage, blurred bokeh effect, golden hour lighting. More relaxed professional vibe.",
    "session_id": "background-variations",
    "mode": "max"
  }'
```

### 6. Headshot with Different Outfits

Transform the subject's appearance with professional attire options.

```bash
# Navy suit
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Create a professional headshot from this casual photo. Dress the subject in a classic navy blue business suit with a white dress shirt and subtle tie. Clean gray background, professional studio lighting.",
    "session_id": "outfit-variations",
    "mode": "max",
    "image_urls": ["https://example.com/casual-photo.jpg"]
  }'

# Business casual
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Create another version with business casual attire - a blazer over a smart polo shirt or open-collar dress shirt. Same background and lighting as before.",
    "session_id": "outfit-variations",
    "mode": "max"
  }'

# Creative professional
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Create a version for creative industry - stylish but professional, perhaps a dark turtleneck or modern collarless jacket. Contemporary creative professional look.",
    "session_id": "outfit-variations",
    "mode": "max"
  }'
```

### 7. Resume/CV Headshot

Clean, professional headshot optimized for job applications and CVs.

```bash
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Create a clean, professional headshot suitable for a resume or CV. Simple solid light background (white or very light gray), professional attire, friendly and confident expression. The photo should be conservative and appropriate for any industry. Square format, head and shoulders framing.",
    "mode": "max",
    "image_urls": ["https://example.com/applicant-photo.jpg"]
  }'
```

### 8. Speaker/Author Headshot

Dynamic headshot for conference speakers, authors, and thought leaders.

```bash
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Create a compelling speaker/author headshot. The subject should appear engaging, confident, and dynamic. Use dramatic lighting with a dark background to create visual impact. Slight smile, eyes that connect with the viewer. This should work well on book covers, conference websites, and keynote slides. High contrast, memorable, professional.",
    "mode": "max",
    "image_urls": ["https://example.com/author-source.jpg"]
  }'
```

### 9. Real Estate Agent Headshot

Approachable, trustworthy headshot for real estate professionals.

```bash
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Create a real estate agent headshot. The subject should appear trustworthy, friendly, and professional. Warm lighting, genuine smile, approachable expression. Background should be a subtle blurred interior of an upscale home or modern building. Professional but not stiff - someone you would trust to help you buy a home.",
    "mode": "max",
    "image_urls": ["https://example.com/agent-photo.jpg"]
  }'
```

### 10. Multiple Expression Variations

Generate several expression options from the same source photo.

```bash
# Confident/serious
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Create a professional headshot with a confident, serious expression. Professional and authoritative, suitable for a law firm or financial services. Neutral gray background, classic professional lighting.",
    "session_id": "expression-variations",
    "mode": "max",
    "image_urls": ["https://example.com/source-photo.jpg"]
  }'

# Friendly/approachable
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Now create a variation with a warm, friendly smile. Approachable and welcoming, suitable for customer-facing roles or consulting. Same background and lighting setup.",
    "session_id": "expression-variations",
    "mode": "max"
  }'

# Thoughtful/engaged
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Create another variation with a thoughtful, engaged expression - slight smile, intelligent and curious look. Good for tech industry or academia. Same background and lighting.",
    "session_id": "expression-variations",
    "mode": "max"
  }'
```

## Best Practices

### Photo Input Guidelines
- **Face Visibility**: Ensure the face is clearly visible, well-lit, and not obscured
- **Resolution**: Use source photos of at least 512x512 pixels for best results
- **Angle**: Front-facing or slight angle (3/4 view) works best
- **Lighting**: Avoid harsh shadows or extreme backlighting in source
- **Expression**: Neutral or natural expression in source produces best transformations

### Professional Headshot Standards
- **Framing**: Head and shoulders, with face occupying 60-70% of vertical space
- **Eye Contact**: Subject should appear to look at the viewer
- **Background**: Clean, non-distracting, complements the subject
- **Lighting**: Soft, flattering light that minimizes harsh shadows
- **Attire**: Appropriate for the industry and role

### Industry-Specific Recommendations

| Industry | Style | Background | Attire |
|----------|-------|------------|--------|
| Finance/Legal | Conservative, formal | Neutral gray/blue | Dark suit, traditional |
| Tech | Modern, approachable | Clean gradient or office | Smart casual to business |
| Creative | Dynamic, distinctive | Bold or artistic | Contemporary, stylish |
| Healthcare | Trustworthy, warm | Light, clinical or neutral | Professional, white coat optional |
| Real Estate | Friendly, trustworthy | Home interior blur | Business professional |
| Academia | Thoughtful, credible | Library or neutral | Business casual to formal |

## Mode Selection

Ask your users before generating:

**"Do you want fast & cheap, or high quality?"**

| Mode | Best For | Speed | Quality |
|------|----------|-------|---------|
| `max` | Final headshots, client deliverables, executive portraits | Slower | Highest |
| `eco` | Quick previews, testing styles, bulk drafts | Faster | Good |

## Multi-Turn Headshot Refinement

Use `session_id` to iterate and perfect headshots:

```bash
# Initial generation
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Create a professional headshot from this photo with a blue gradient background",
    "session_id": "headshot-refinement",
    "mode": "max",
    "image_urls": ["https://example.com/source.jpg"]
  }'

# Refine based on feedback
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Make the lighting warmer and the expression slightly more friendly. Keep the same background.",
    "session_id": "headshot-refinement",
    "mode": "max"
  }'

# Final adjustments
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Perfect. Now generate 2 more slight variations of this final result.",
    "session_id": "headshot-refinement",
    "mode": "max"
  }'
```

## Batch Generation for Teams

Generate consistent headshots for entire teams efficiently:

```bash
# Define team style first
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "I need to create headshots for a team of 10 people. Our brand colors are navy blue and white. We want: 1:1 square format, light gray background, soft professional lighting, business casual attire, friendly but professional expressions. First, create a headshot for this team member to establish the style.",
    "session_id": "acme-corp-team",
    "mode": "max",
    "image_urls": ["https://example.com/team/person-1.jpg"]
  }'

# Continue with remaining team members using same session
curl -X POST https://sense.eachlabs.run/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Create headshot for next team member, matching established style",
    "session_id": "acme-corp-team",
    "mode": "eco",
    "image_urls": ["https://example.com/team/person-2.jpg"]
  }'
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Failed to create prediction: HTTP 422` | Insufficient balance | Top up at eachlabs.ai |
| No face detected | Face not visible in source | Use a clearer photo with visible face |
| Poor likeness | Low quality source image | Use higher resolution source (512x512+) |
| Timeout | Complex generation | Set client timeout to minimum 10 minutes |

## Related Skills

- `each-sense` - Core API documentation
- `product-photo-generation` - E-commerce product photography
- `meta-ad-creative-generation` - Social media ad creatives
