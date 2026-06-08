# Build Registration — team-projects plugin

When adding this plugin to an OpenClaw source tree, register it in these 4 build files:

## 1. `tsdown.config.ts`

Add `"team-projects"` to the `pluginSdkEntrypoints` array.

## 2. `src/plugins/loader.ts`

Add to the `pluginSdkScopedAliasEntries` array:

```typescript
{
  subpath: "team-projects",
  srcFile: "team-projects.ts",
  distFile: "team-projects.js",
},
```

## 3. `scripts/write-plugin-sdk-entry-dts.ts`

Add `"team-projects"` to the entrypoints array.

## 4. `package.json`

Add to the `exports` map:

```json
"./plugin-sdk/team-projects": {
  "types": "./dist/plugin-sdk/team-projects.d.ts",
  "default": "./dist/plugin-sdk/team-projects.js"
},
```

## Why all 4?

| Registration Point | What happens if missing |
|---|---|
| `tsdown.config.ts` | `dist/plugin-sdk/team-projects.js` not generated — runtime can't find compiled SDK |
| `loader.ts` aliases | Jiti can't resolve `openclaw/plugin-sdk/team-projects` — "Cannot find module" error |
| `write-plugin-sdk-entry-dts.ts` | `dist/plugin-sdk/team-projects.d.ts` not generated — TypeScript types missing |
| `package.json` exports | External consumers can't import the SDK subpath |

## Config

Enable the plugin in `openclaw.json`:

```json
{
  "plugins": {
    "allow": ["telegram", "discord", "team-projects"],
    "entries": {
      "team-projects": { "enabled": true }
    }
  }
}
```
