# Werydance 2.0 Video Generator

Use this package when the task is Seedance video generation on WeryAI.

Preferred entry points:

- `node {baseDir}/scripts/video_gen.js submit-text --json '...'`
- `node {baseDir}/scripts/video_gen.js submit-image --json '...'`
- `node {baseDir}/scripts/video_gen.js submit-multi-image --json '...'`
- `node {baseDir}/scripts/video_gen.js submit-almighty --json '...'`
- `node {baseDir}/scripts/video_gen.js status --task-id <id>`
- `node {baseDir}/scripts/video_gen.js wait --json '...'`
- `node {baseDir}/scripts/video_gen.js models --mode text_to_video`

Route intents this way:

- text prompt only -> `submit-text`
- single `image` -> `submit-image`
- `first_frame` + `last_frame`, or `image` + `last_image` -> ordered `images` then `submit-multi-image`
- `images` -> `submit-multi-image`
- any `videos` or `audios` references -> `submit-almighty`
- existing `taskId` -> `status` query, not a new paid submission

Default operation is two-stage:

1. Submit first and report `taskId` / `batchId`.
2. Poll with `status` until terminal state.

Use `wait` only when one-shot submit+poll is explicitly requested.

Read `SKILL.md` first for trigger language, defaults, and constraints.
Read `references/seedance-prompt-optimization.md` when you need stronger prompt expansion patterns.
