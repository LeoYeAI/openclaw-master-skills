# Prompt Templates

Use these as starting points, then replace bracketed placeholders.

## Product Shot

`Clean [camera angle] product photo of [subject], [material/details], [lighting], [background], premium commercial look, sharp focus, no text, no watermark`

## Character Illustration

`Stylized character illustration of [subject], [pose/action], [art style], [color palette], [background], highly readable silhouette, no extra limbs, no text`

## Marketing Hero Image

`Website hero image for [brand/use case], [subject], [visual style], [composition], [lighting], leave negative space on [left/right] for headline, no typography baked into the image`

## Editorial Photography

`Editorial photograph of [subject], shot on [lens/look], [lighting], [composition], realistic texture, natural color grading, high detail`

## Interior Scene

`Interior design render of [room], [design style], [materials], [time of day], [camera angle], photorealistic, uncluttered, no people`

## Iteration Heuristics

- If the image is generic, add more constraints about lens, lighting, and composition.
- If the image is messy, reduce subject count and describe one focal point.
- If the output feels off-brand, specify color palette and mood explicitly.
- If the model inserts text, repeat `no text, no lettering, no watermark`.

## Edit Prompt Template

`Edit the supplied image. Keep [unchanged elements] exactly the same. Change only [target area] so that it becomes [desired result]. Preserve the original composition, subject identity, camera angle, and lighting unless explicitly changed.`

## Masked Edit Template

`Edit only the masked area. Replace [masked content] with [desired result]. Do not modify unmasked regions. Match perspective, lighting, and color grading to the original image.`

## Attachment-Only Translation Template

`Recreate the attached [diagram/poster/screenshot] with the same composition, icon placement, arrow flow, spacing, and visual style. Replace every visible English label with natural Simplified Chinese. Keep the structure unchanged. The label mapping is: [label mapping].`

## Attachment-Only High-Fidelity Template

`Use the attached image as a visual reference and recreate it as faithfully as possible. Preserve layout, proportions, colors, and style. Rewrite only the text content as follows: [label mapping]. Do not add new elements. Do not omit any arrows, boxes, icons, or callouts.`
