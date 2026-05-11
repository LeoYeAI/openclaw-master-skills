# Workflows

## 1) Diagnose wrong-profile selection

1. run the summary script
2. inspect saved preference or helper-selected profile
3. inspect `order.openai-codex`
4. inspect current session `authProfileOverride`
5. inspect the effective runtime profile or active slot if the setup has one
6. determine whether runtime selected the wrong profile or performed expected failover
7. patch only the inconsistent layer

## 2) Diagnose helper switch that does not affect `/status`

1. reproduce with the real helper command if the setup has one
2. inspect whether the helper changed only the active slot or also the current session override
3. inspect how the helper identifies the current chat/session
4. inspect whether command invocation is missing chat/session env
5. inspect whether the platform keeps companion session entries that also need syncing
6. patch helper-side session resolution or sync logic

## 3) Diagnose `/status` usage mismatch

1. confirm `/status` oauth id for the current chat
2. confirm current session `authProfileOverride`
3. compare live usage for candidate profiles if needed
4. inspect whether the usage loader resolves auth from generic provider order instead of the current session profile
5. patch the runtime usage path so it can prefer the intended session-selected profile
6. re-test `/status`

## 4) Restore correct display semantics

1. decide whether the surface should show preferred profile, effective runtime profile, or usage source profile
2. verify the displayed id comes from the intended state layer
3. verify email/workspace labels come from metadata, not a second hidden truth source
4. remove any accidental duplication of current-profile state
5. re-test the display surface

## 5) Repair a broken active-slot / repo mismatch

1. inspect the external repo entry, if one exists
2. inspect the active slot copy in `auth-profiles.json`
3. compare profile signatures such as `accountId`, workspace, and tokens
4. restore only the broken entry or re-activate the intended repo profile
5. re-run summary and smoke-test switching

## 6) Recover from a broken single profile entry

1. back up the auth store and any external repo first
2. identify the damaged profile by `accountId` before email when possible
3. restore only that profile entry
4. avoid rewriting unrelated profiles
5. re-test switching, status, and usage

## Rollback rule

Before any runtime patch:
- back up the file you change
- keep the patch minimal
- verify syntax or import validity before restart
- re-test one scenario at a time
