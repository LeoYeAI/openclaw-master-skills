# ProcessPromise & ProcessOutput Reference

## ProcessPromise

`$` returns a `ProcessPromise` instance that extends native `Promise`. When resolved, it becomes a `ProcessOutput`.

```js
const p = $`command`  // ProcessPromise
const o = await p      // ProcessOutput
```

### Lifecycle Stages

| Stage | Description |
|-------|-------------|
| `initial` | Blank instance, not yet configured |
| `halted` | Awaiting manual `.run()` (when `$.halt = true`) |
| `running` | Process is executing |
| `fulfilled` | Successfully completed |
| `rejected` | Failed (non-zero exit or spawn error) |

```ts
const p = $`echo foo`
p.stage  // 'running'
await p
p.stage  // 'fulfilled'
```

### `pipe()` — Stream Piping

```js
// Pipe to another command
await $`printf "hello"`
  .pipe($`awk '{printf $1", world!"}'`)
  .pipe($`tr '[a-z]' '[A-Z]'`)

// Pipe to file
await $`echo "Hello"`.pipe('/tmp/output.txt')

// Pipe to writable stream
await $`echo "Hello"`.pipe(fs.createWriteStream('/tmp/output.txt'))

// Pipe stderr vs stdout
const p = $`echo foo >&2; echo bar`
const o1 = (await p.pipe.stderr`cat`).toString()  // 'foo\n'
const o2 = (await p.pipe.stdout`cat`).toString()  // 'bar\n'
```

#### Pipe Features:
- **Chained streams become thenables** — you can `await` the pipeline
- **Standard Stream.pipe compatible** — `ProcessPromise` works with Node.js `Stream.pipe()`
- **Time machine mode** — pipe at any phase (before, during, after execution); all chunks are buffered and replayed in order
- **Signal propagation** — abort signals flow through the pipeline
- **Stream splitting** — pipe to multiple destinations simultaneously:

```js
const p = $`some-command`
const [o1, o2] = await Promise.all([
  p.pipe`log`,
  p.pipe`extract`,
])
```

- **Stream merging** — combine multiple sources into one:

```js
const $h = $({ halt: true })
const p1 = $`echo foo`
const p2 = $h`echo a && sleep 0.1 && echo b`
const p3 = $h`echo c && sleep 0.1 && echo d`
const cat = $h`cat`

p1.pipe(cat)
p2.pipe(cat)
p3.pipe(cat)

const { stdout } = await cat.run()
```

### `unpipe()`
Remove a process from the pipeline.

```js
p1.unpipe(p3)  // Detach p3 from p1's output
```

### `kill()`
Kill the process and all children. Signal defaults to `SIGTERM`.

```js
const p = $`sleep 999`
setTimeout(() => p.kill('SIGINT'), 100)
await p
```

> Killing an already-settled process raises an error.

### `abort()`
Terminate via AbortController signal.

```js
const ac = new AbortController()
const p = $({ signal: ac.signal })`sleep 999`

setTimeout(() => ac.abort('reason'), 100)
await p

// Auto-created AbortController accessible via p.signal
const p2 = $`sleep 999`
const { signal } = p2
const res = fetch('https://example.com', { signal })
p2.abort('reason')
```

### `stdio()`
Configure standard I/O for the process. Must be set before the process starts.

```js
const h$ = $({ halt: true })
const p1 = h$`read`.stdio('inherit', 'pipe', null).run()
const p2 = h$`read`.stdio('pipe').run()  // ['pipe', 'pipe', 'pipe']

// Or via preset:
await $({ stdio: ['pipe', 'pipe', 'pipe'] })`read`
```

### `nothrow()`
Suppress errors for this specific command. Equivalent to `$({ nothrow: true })`.

```js
await $`grep something from-file`.nothrow()

// Inside a pipe:
await $`find ./type f -print0`
  .pipe($`xargs -0 grep something`.nothrow())
  .pipe($`wc -l`)

// Disable when global nothrow is set:
$.nothrow = true
await $`echo foo`.nothrow(false)
```

### `quiet()`
Enable/disable suppress mode for a specific command.

```js
await $`grep something from-file`.quiet()

$.quiet = true
await $`echo foo`.quiet(false)  // Disable for one command
```

### `verbose()`
Enable/disable verbose output for a specific command.

```js
await $`grep something from-file`.verbose()

$.verbose = true
await $`echo foo`.verbose(false)  // Turn off once
```

### `timeout()`
Kill the process after a specified duration.

```js
await $`sleep 999`.timeout('5s')
await $`sleep 999`.timeout('5s', 'SIGKILL')  // With specific signal
```

### Output Formatters

```js
const p = $`echo 'foo\nbar'`

await p.text()         // 'foo\nbar\n'
await p.text('hex')    // '666f6f0a6261720a'
await p.buffer()       // Buffer.from('foo\nbar\n')
await p.lines()        // ['foo', 'bar']

// Custom line delimiter
await $`find ./ -type f -print0`.lines('\0')  // Null-delimited

// JSON parsing
await $`echo '{"foo": "bar"}'`.json()  // { foo: 'bar' }
```

### Metadata Getters

```js
const p = $`sleep 1`
p.pid       // Process ID
p.cwd       // Working directory
p.cmd       // Command: "sleep 1"
p.fullCmd   // Full command with prefix/postfix: "set -euo pipefail;sleep 1"
```

### Async Iterator

```js
const p = $`echo "Line1\nLine2\nLine3"`
for await (const line of p) {
  console.log(line)
}

// Custom delimiter
for await (const line of $({ delimiter: '\0' })`find ./ -type f -print0`) {
  console.log(line)
}
```

### stdin/ stdout / stderr Streams

```js
// Write to stdin
const p = $`while read; do echo $REPLY; done`
p.stdin.write('Hello, World!\n')
p.stdin.end()

// Read from stdout
const p = $`npm init`
for await (const chunk of p.stdout) {
  echo(chunk)
}
```

### `exitCode`

Promise that resolves to the process exit code.

```js
if (await $`[[ -d path ]]`.exitCode === 0) {
  // Directory exists
}
```

## ProcessOutput

The resolved result of a `ProcessPromise`.

```ts
interface ProcessOutput extends Error {
  exitCode: number
  signal: NodeJS.Signals | null
  stdout: string
  stderr: string

  ok: boolean               // Only present when nothrow is used
  message: string           // Only present when nothrow is used

  buffer(): Buffer
  json<T = any>(): T
  blob(type?: string): Blob
  text(encoding?: string): string
  lines(delimiter?: string | RegExp): string[]

  toString(): string        // Combined stdout + stderr
  valueOf(): string         // Same as toString() but trimmed
}
```

### When used as argument to another `$`
If `ProcessOutput` is interpolated into another `$` command, zx uses `stdout` with trailing newline trimmed:

```js
const date = await $`date`
await $`echo Current date is ${date}.`
```

### Error behavior
When the exit code is non-zero and `nothrow` is false, `ProcessOutput` is thrown as an error (it extends `Error`).

```js
try {
  await $`exit 1`
} catch (p) {
  console.log(`Exit code: ${p.exitCode}`)
  console.log(`Error: ${p.stderr}`)
}
```
