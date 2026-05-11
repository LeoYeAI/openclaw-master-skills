# Versioning Notes

## Separate Instruction Version From SDK Version

- `metadata.version` is the version of the skill instructions.
- `analyticscli-supported-range` is the SDK package range the instructions are written for.

## Recommended Policy

- Keep `analyticscli-ts-sdk` on the current stable SDK line.
- Widen the supported range only while the public API and event contract remain meaningfully compatible.
- When a future major introduces different bootstrap, storage, or event-contract rules, publish a sibling skill such as `analyticscli-ts-sdk-v1`.
- Keep older major-specific skills published for teams that still run that line in production.

## What To Avoid

- one giant skill that mixes multiple incompatible major-version instructions
- renaming the default skill for every minor release
- encoding version support only in prose with no metadata hint
