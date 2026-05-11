---
name: zx
description: Comprehensive guide for writing shell scripts with Google zx — a tool for writing better scripts using JavaScript/TypeScript. Use when writing, debugging, or refactoring zx scripts (.mjs, .js, .ts files using zx), executing shell commands from JavaScript, working with ProcessPromise/ProcessOutput APIs, piping streams, configuring zx options, or using zx CLI.  Do NOT use for general Node.js questions unrelated to shell scripting.
---

# Zx — Write Better Shell Scripts with JavaScript

## Overview

zx is Google's tool for writing shell scripts in JavaScript/TypeScript. It wraps `child_process`, auto-escapes arguments, and provides sensible defaults — giving you the power of the JavaScript ecosystem in your scripts.

```js
#!/usr/bin/env zx

await $`cat package.json | grep name`

const branch = await $`git branch --show-current`
await $`dep deploy --branch=${branch}`

const name = 'foo & bar'
await $`mkdir /tmp/${name}`  // No quotes needed — auto-escaped
```

Bash is great for simple tasks, but when scripts grow complex, a full programming language helps. zx adds helpful wrappers around `child_process`, escapes arguments, and gives sensible defaults. **Think: bash + JavaScript in one script.**

## Triggers

Also triggers when users ask about running shell commands in JavaScript, converting bash scripts to zx, executing remote scripts, Markdown scripts, or TypeScript shell scripts.

## Quick Start

```bash
npm install zx
```

Write scripts as `.mjs` files (supports top-level `await`). Add `#!/usr/bin/env zx` shebang or run via CLI:

```bash
zx ./script.mjs           # Direct execution
npx zx ./script.mjs       # Via npx
node --import zx/globals  # As Node.js loader
```

All functions (`$`, `cd`, `fetch`, etc.) are globally available in zx scripts without imports. For explicit imports (better VS Code autocomplete):

```js
import 'zx/globals'
```

## Core Concepts

### `` $`command` `` — Execute Shell Commands

The tagged template literal is the heart of zx. Everything in `${...}` is auto-escaped and quoted.

```js
// Async (standard) — returns ProcessPromise
const output = await $`ls -la`

// Sync variant — returns ProcessOutput directly
const dir = $.sync`pwd`

// Arrays are flattened
const flags = ['--oneline', '--decorate', '--color']
await $`git log ${flags}`

// Non-zero exit codes throw ProcessOutput
try {
  await $`exit 1`
} catch (p) {
  console.log(`Exit: ${p.exitCode}, Error: ${p.stderr}`)
}
```

### Preset Configuration with `$({...})`

Create custom `$` instances with preset options — chainable and composable:

```js
const $$ = $({ verbose: false, env: { NODE_ENV: 'production' } })
const pwd = $$.sync`pwd`

// Presets are chainable
const $1 = $({ nothrow: true })
const $2 = $1({ sync: true })  // Both nothrow + sync applied
```

### ProcessPromise & ProcessOutput

```
$`cmd`              ProcessPromise (extends Promise)
  ├── .pipe()       Stream piping
  ├── .kill()       Terminate process
  ├── .text()       Output as string
  ├── .json()       Output as parsed JSON
  ├── .lines()      Output split by lines
  ├── .nothrow()    Suppress errors for this command
  ├── .quiet()      Suppress output for this command
  ├── .timeout()    Auto-kill after duration
  ├── .stdio()      Configure I/O
  ├── .exitCode     Promise<exit code>
  ├── .stdout       Readable stream
  ├── .stderr       Readable stream
  ├── .stdin        Writable stream
  ├── .pid / .cmd   Process metadata
  └── await → ProcessOutput
                ├── .stdout    string
                ├── .stderr    string
                ├── .exitCode  number
                ├── .signal    string|null
                ├── .text() / .json() / .lines() / .buffer() / .blob()
                └── .ok        boolean (when nothrow)
```

## Decision Tree

When writing zx scripts, use this decision tree:

| Goal | Approach |
|------|----------|
| Run a command | `` await $`cmd` `` |
| Run synchronously | `` $.sync`cmd` `` |
| Pipe output | `` .pipe($`next`) `` / `` .pipe('file.txt') `` |
| Handle errors gracefully | `` $({nothrow: true}) `` / `` .nothrow() `` |
| Set timeout | `` $({timeout: '30s'}) `` / `` .timeout('30s') `` |
| Parse JSON output | `` (await $`cmd`).json() `` |
| Real-time streaming | `` for await (const line of $`cmd`) `` |
| Retry on failure | `` retry(5, () => $`cmd`) `` |
| User prompt | `` question('Name: ') `` |
| Progress indicator | `` await spinner('Working...', () => $`cmd`) `` |
| Change directory | `` cd('/path') `` or `` within(() => { $.cwd = '/tmp' }) `` |
| Temp files/dirs | `` tmpfile() `` / `` tmpdir() `` |
| Parse CLI args | `` argv.flag `` or `` minimist(process.argv.slice(2)) `` |
| Load .env file | `` dotenv.config('.env') `` |

## Writing Effective zx Scripts

### Parallel Execution

```js
const results = await Promise.all([
  $`sleep 1; echo 1`,
  $`sleep 2; echo 2`,
  $`sleep 3; echo 3`,
])
```

### Error Handling with nothrow

```js
$.nothrow = true

const repos = ['zx', 'webpod']
const clones = repos.map(n => $`git clone https://github.com/google/${n}`)

const results = await Promise.all(clones)
const errors = results.filter(o => !o.ok).map(o => o.stderr.trim())
console.log('Errors:', errors.join('\n'))
```

### Stream Piping

```js
// Chain commands like bash pipes
const greeting = await $`printf "hello"`
  .pipe($`awk '{printf $1", world!"}'`)
  .pipe($`tr '[a-z]' '[A-Z]'`)

// Pipe to file
await $`echo "Hello!"`.pipe('/tmp/output.txt')

// Real-time output to terminal
await $`echo 1; sleep 1; echo 2; sleep 1; echo 3`.pipe(process.stdout)
```

### Stream Splitting & Merging

```js
// Split one source to multiple consumers
const p = $`some-command`
const [o1, o2] = await Promise.all([
  p.pipe`log`,
  p.pipe`extract`,
])

// Merge multiple sources
const $h = $({ halt: true })
const p1 = $`echo foo`
const p2 = $h`echo a && sleep 0.1 && echo b`
const p3 = $h`echo c && sleep 0.1 && echo d`
const cat = $h`cat`
p1.pipe(cat); p2.pipe(cat); p3.pipe(cat)
await cat.run()
```

### Output Formatters

```js
const p = $`echo '{"foo":"bar"}\nline2'`

await p.json()    // { foo: 'bar' }
await p.lines()   // ['{"foo":"bar"}', 'line2']
await p.text()    // '{"foo":"bar"}\nline2\n'
```

### Async Iteration

```js
for await (const line of $`git log --oneline --max-count=5`) {
  console.log(line)
}
```

## Shell Configuration

zx defaults to bash. Switch shells as needed:

```js
import { useBash, usePowerShell, usePwsh } from 'zx'

usePowerShell()  // PowerShell.exe
usePwsh()        // PowerShell v7+
useBash()        // Back to bash

// Manual override
$.shell = '/bin/zsh'
```

On Windows, consider using WSL or Git Bash for bash support, or switch to PowerShell via `usePowerShell()`.

## Built-in Helpers Summary

| Helper | Purpose | Example |
|--------|---------|---------|
| `cd()` | Change directory | `cd('/tmp')` |
| `fetch()` | HTTP requests, supports `.pipe()` | `fetch('https://api.example.com')` |
| `question()` | Interactive user input | `question('Name: ')` |
| `sleep()` | Delay execution | `await sleep(1000)` |
| `echo()` | Print to stdout | `` echo`Status: ${p}` `` |
| `stdin()` | Read stdin | `JSON.parse(await stdin())` |
| `within()` | Isolated async config context | `within(() => { $.cwd = '/tmp' })` |
| `retry()` | Retry with delay/backoff | `retry(5, () => $`curl url`)` |
| `spinner()` | CLI progress indicator | `await spinner(() => $`long-cmd`)` |
| `glob()` | File glob matching (globby) | `glob('**/*.js')` |
| `which()` | Find executable path | `await which('node')` |
| `ps` | Cross-platform process list | `ps.lookup({ command: 'node' })` |
| `tmpdir()` | Temp directory | `tmpdir('sub')` |
| `tmpfile()` | Temp file | `tmpfile('f.txt', 'content')` |
| `argv` | Parsed CLI arguments | `argv.verbose` |
| `dotenv` | .env file loading | `dotenv.config('.env')` |

**Exposed npm packages:** `chalk` (colors), `fs` (fs-extra), `os`, `path`, `YAML` (yaml), `minimist`.

## Resources

- **[references/api.md](references/api.md)** — Full API reference: `$` options, `cd()`, `fetch()`, `question()`, `sleep()`, `echo()`, `stdin()`, `within()`, `retry()`, `spinner()`, `glob()`, `which()`, `ps`, `kill()`, `tmpdir()`, `tmpfile()`, `minimist`, `argv`, `chalk`, `fs`, `os`, `path`, `YAML`, `dotenv`, `quote()`, `useBash()`, `usePowerShell()`, `usePwsh()`
- **[references/configuration.md](references/configuration.md)** — All `$.options`: `shell`, `prefix`, `postfix`, `quote`, `verbose`, `quiet`, `env`, `cwd`, `timeout`, `nothrow`, `detached`, `preferLocal`, `spawn`, `kill`, `log`, `input`, `signal`, `stdio`, `halt`, `delimiter`, `defaults`
- **[references/cli.md](references/cli.md)** — CLI usage: flags, env vars, Markdown scripts, remote scripts, stdin execution, REPL mode
- **[references/process.md](references/process.md)** — ProcessPromise/ProcessOutput lifecycle, piping, killing, aborting, output formatters, stream handling
