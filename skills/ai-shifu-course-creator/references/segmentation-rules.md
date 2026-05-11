# Segmentation Rules

## Objective

Produce stable lesson-oriented semantic segments from noisy source material while preserving immutable artifacts.

## Core Rules

1. Preserve source order unless explicit ordering hints are provided.
2. Keep code/image/table blocks immutable.
3. Segment by semantic shift, not heading depth alone.
4. Keep each lesson candidate centered on one teachable question.
5. Attach source spans to every segment.

## Segment Types

- `concept`: explanatory statements and definitions.
- `example`: concrete demonstrations and walkthroughs.
- `code`: executable or pseudo-code blocks.
- `image`: visual references and diagrams.
- `exercise`: learner action prompts.
- `transition`: bridge text that links ideas.

## Transfer Signals

Every segment should include transferable signals for downstream script quality:
- learner hook
- evidence type
- visual cue
- concept conflict
- boundary cue
- action cue
- density cue
- quote cue
- visual-text-pair cue
- interaction-intent cue
- compare cue

## Failure Handling

If structure is weak, output a fallback segmentation and mark uncertain spans for focused reruns.
