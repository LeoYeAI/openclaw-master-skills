# Target Providers

This file defines a small, explicit contract for different targeting strategies.

## Goal

Allow the system to choose among multiple targeting providers and fall back safely.

## Provider order

Default order for high confidence:

1. accessibility provider
2. OCR or text anchor provider
3. template or image match provider
4. heuristic region provider

## Provider contract

Each provider should output:

- target type
- confidence score
- bounding box (absolute)
- one or more candidate click points
- validation hints

## Implemented scripts

- `scripts/target_resolver.py` orchestrates provider selection and returns a ranked candidate.
- `scripts/ocr_text.py` extracts text boxes and coordinates from screenshots.
- `scripts/template_match.py` matches a template image within a region.

## Notes

- Accessibility is currently a stub and should be implemented per platform.
- OCR and template matching are optional and depend on external packages.
- Heuristic regions remain as the last fallback only.
