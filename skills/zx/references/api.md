# Zx API Reference

## `$` — The Template Literal API

Executes shell commands using tagged template literals.

### Basic Usage

```js
// Async: returns ProcessPromise
const list = await $`ls -la`

// Sync: returns ProcessOutput
const dir = $.sync`pwd`

// With presets: factory function
const $$ = $({ verbose: false, env: { NODE_ENV: 'production' } })
const env = await $$`node -e 'console.log(process.env.NODE_ENV)'`

// Chainable presets
const $1 = $({ nothrow: true })
const $2 = $1({ sync: true })
```

### `$({input})`
Pass stdin to the command.

```js
const p1 = $({ input: 'foo' })`cat`
const p2 = $({ input: Readable.from('bar') })`cat`
const p3 = $({ input: Buffer.from('baz') })`cat`
const p4 = $({ input: p3 })`cat`          // Pass another ProcessPromise
const p5 = $({ input: await p3 })`cat`     // Pass settled ProcessOutput
```

### `$({signal})`
Make the process abortable via AbortController.

```js
const { signal } = new AbortController()
const p = $({ signal })`sleep 9999`
setTimeout(() => signal.abort('reason'), 1000)
```

### `$({timeout})`
Auto-kill after specified duration.

```js
const p = $({ timeout: '1s' })`sleep 999`
```

### `$({nothrow})`
Suppress errors, return ProcessOutput with `ok`, `exitCode`, `message` fields.

```js
const o1 = await $({ nothrow: true })`exit 1`
o1.ok        // false
o1.exitCode  // 1
o1.message   // "exit code: 1 ..."

const o2 = await $({ nothrow: true, spawn() { throw new Error('BrokenSpawn') } })`echo foo`
o2.ok       // false
o2.exitCode // null
o2.message  // "BrokenSpawn ..."
```

### Complete Options Interface

```ts
interface Options {
  cwd:            string
  ac:             AbortController
  signal:         AbortSignal
  input:          string | Buffer | Readable | ProcessOutput | ProcessPromise
  timeout:        Duration
  timeoutSignal:  NodeJS.Signals
  stdio:          StdioOptions
  verbose:        boolean
  sync:           boolean
  env:            NodeJS.ProcessEnv
  shell:          string | true
  nothrow:        boolean
  prefix:         string
  postfix:        string
  quote:          typeof quote
  quiet:          boolean
  detached:       boolean
  preferLocal:    boolean | string | string[]
  spawn:          typeof spawn
  spawnSync:      typeof spawnSync
  store:          TSpawnStore
  log:            typeof log
  kill:           typeof kill
  killSignal:     NodeJS.Signals
  halt:           boolean
  delimiter:      string | RegExp
}
```

## `cd()`

Changes the current working directory. Accepts strings and ProcessOutput (auto-trims trailing newlines).

```js
cd('/tmp')
await $`pwd`   // => /tmp

cd(await $`mktemp -d`)  // Works with ProcessOutput
```

> `cd` invokes `process.chdir()` internally (affects global context). Use `$.cwd` for per-command isolation instead.

## `fetch()`

Wrapper around node-fetch-native. Supports `.pipe()` for stream-friendly usage.

```js
const r1 = await fetch('https://example.com')
const json = await r1.json()

const r2 = await fetch('https://example.com', {
  signal: AbortSignal.timeout(5000),
})

// Pipe fetch result directly into a command
const p1 = fetch('https://example.com').pipe($`cat`)
const p2 = fetch('https://example.com').pipe`cat`
```

## `question()`

Wrapper around Node.js readline API for interactive prompts.

```js
const name = await question('What is your name? ')

// With choices
const option = await question('Select an option:', {
  choices: ['A', 'B', 'C'],
})
```

## `sleep()`

Promise-based setTimeout wrapper.

```js
await sleep(1000)
```

## `echo()`

A `console.log()` alternative that handles ProcessOutput.

```js
const branch = await $`git branch --show-current`

echo`Current branch is ${branch}.`
// or
echo('Current branch is', branch)
```

## `stdin()`

Returns stdin as a string.

```js
const content = JSON.parse(await stdin())
```

## `within()`

Creates an isolated async context with its own `$` configuration via AsyncLocalStorage.

```js
await $`pwd`  // => /home/path
$.foo = 'bar'

within(async () => {
  $.cwd = '/tmp'
  $.foo = 'baz'

  setTimeout(async () => {
    await $`pwd`  // => /tmp
    $.foo          // 'baz'
  }, 1000)
})

await $`pwd`  // => /home/path
$.foo          // still 'bar'
```

Context switching with prefix:

```js
await $`node --version`  // => v20.2.0

const version = await within(async () => {
  $.prefix += 'export NVM_DIR=$HOME/.nvm; source $NVM_DIR/nvm.sh; nvm use 16;'
  return $`node --version`
})

echo(version)  // => v16.20.0
```

## `syncProcessCwd()`

Keeps `process.cwd()` in sync with internal `$` cwd when changed via `cd()`.

```ts
import { syncProcessCwd } from 'zx'

syncProcessCwd()       // Enable
syncProcessCwd(false)  // Disable
```

> Disabled by default due to performance overhead.

## `retry()`

Retry a callback for a specified number of attempts.

```js
const p = await retry(10, () => $`curl https://medv.io`)

// With delay between attempts
const p = await retry(20, '1s', () => $`curl https://medv.io`)

// With exponential backoff
const p = await retry(30, expBackoff(), () => $`curl https://medv.io`)
```

## `spinner()`

CLI spinner for long-running operations. Auto-disabled in CI.

```js
await spinner(() => $`long-running command`)

// With message
await spinner('working...', () => $`sleep 99`)
```

## `glob()`

The globby package for file matching.

```js
const packages = await glob(['package.json', 'packages/*/package.json'])
const markdowns = glob.sync('*.md')  // Sync shortcut
```

## `which()`

The `which` package — find executable path.

```js
const node = await which('node')

// With nothrow: returns null if not found
const pathOrNull = await which('node', { nothrow: true })
```

## `ps`

The @webpod/ps package — cross-platform process listing.

```js
const all = await ps.lookup()
const nodejs = await ps.lookup({ command: 'node' })
const children = await ps.tree({ pid: 123 })
const fulltree = await ps.tree({ pid: 123, recursive: true })
```

## `kill()`

Process killer.

```js
await kill(123)
await kill(123, 'SIGKILL')
```

## `tmpdir()` / `tmpfile()`

Temporary filesystem helpers.

```js
const t1 = tmpdir()          // /os/based/tmp/zx-1ra1iofojgg/
const t2 = tmpdir('foo')     // /os/based/tmp/zx-1ra1iofojgg/foo/

const f1 = tmpfile()                                    // Temp file with random name
const f2 = tmpfile('f2.txt')                            // Named temp file
const f3 = tmpfile('f3.txt', 'string or buffer')        // With content
const f4 = tmpfile('f4.sh', 'echo "foo"', 0o744)        // Executable
```

## `minimist` / `argv`

CLI argument parsing.

```js
// argv is pre-parsed with minimist
if (argv.someFlag) {
  echo('yes')
}

// Custom parsing
const myArgv = minimist(process.argv.slice(2), {
  boolean: ['force', 'help'],
  alias: { h: 'help' },
})
```

## `chalk`

Terminal string coloring.

```js
console.log(chalk.blue('Hello world!'))
console.log(chalk.red.bold('Error!'))
```

## `fs`

The fs-extra package.

```js
const { version } = await fs.readJson('./package.json')
await fs.ensureDir('./output')
```

## `os` / `path`

Standard Node.js packages exposed directly.

```js
await $`cd ${os.homedir()} && mkdir example`
await $`mkdir ${path.join(basedir, 'output')}`
```

## `YAML`

The yaml package.

```js
console.log(YAML.parse('foo: bar').foo)
```

## `MAML`

The maml package — minimal readable markup language.

```js
const maml = `{
  project: "MAML"
  tags: [ "minimal", "readable" ]
  spec: {
    version: 1
    author: "Anton Medvedev"
  }
}`
console.log(MAML.parse(maml).project)  // MAML
```

## `dotenv`

Environment variable file loading and parsing (envapi package).

```js
// Parse raw env content
const raw = 'FOO=BAR\nBAZ=QUX'
const data = dotenv.parse(raw)  // { FOO: 'BAR', BAZ: 'QUX' }
await fs.writeFile('.env', raw)

// Load and use
const env = dotenv.load('.env')
await $({ env })`echo $FOO`.stdout  // BAR

// Apply to process.env
dotenv.config('.env')
process.env.FOO  // BAR
```

## Shell Helpers

### `quote()`
Default bash quoting function.

```js
quote("$FOO")  // "$'$FOO'"
```

### `quotePowerShell()`
PowerShell-specific quoting.

```js
quotePowerShell("$FOO")  // "'$FOO'"
```

### `useBash()`
Enables bash preset: sets `$.shell` to `bash` and `$.quote` to `quote`.

```js
useBash()
```

### `usePowerShell()`
Switches to PowerShell. Applies `quotePowerShell` for quoting.

```js
usePowerShell()
```

### `usePwsh()`
Sets pwsh (PowerShell v7+) as the default shell.

```js
usePwsh()
```

## `versions`

Exports versions of zx dependencies.

```ts
import { versions } from 'zx'

versions.zx      // '8.7.2'
versions.chalk   // '5.4.1'
```

## API Quick Reference

| Function | Package/Origin | Purpose |
|----------|---------------|---------|
| `$` / `$.sync` | zx core | Command execution |
| `cd()` | zx core | Change working directory |
| `fetch()` | node-fetch-native | HTTP requests |
| `question()` | Node readline | Interactive input |
| `sleep()` | `setTimeout` | Delay |
| `echo()` | zx core | Console output |
| `stdin()` | zx core | Read stdin |
| `within()` | AsyncLocalStorage | Isolated config context |
| `syncProcessCwd()` | zx core | Sync internal cwd |
| `retry()` | zx core | Retry with backoff |
| `spinner()` | zx core | CLI spinner |
| `glob()` | globby | File matching |
| `which()` | which | Path lookup |
| `ps` | @webpod/ps | Process listing |
| `kill()` | zx core | Process killer |
| `tmpdir()` / `tmpfile()` | zx core | Temp filesystem |
| `minimist` / `argv` | minimist | CLI args |
| `chalk` | chalk | Terminal colors |
| `fs` | fs-extra | File system |
| `os` | Node os | OS utilities |
| `path` | Node path | Path utilities |
| `YAML` | yaml | YAML parsing |
| `MAML` | maml | MAML parsing |
| `dotenv` | envapi | Env file loading |
| `quote()` / `quotePowerShell()` | zx core | Shell quoting |
| `useBash()` / `usePowerShell()` / `usePwsh()` | zx core | Shell switching |
| `versions` | zx core | Version info |
