# Zx Configuration Reference

All configuration lives on the `$` object. See `$.defaults` for initial values.

## Core Options

### `$.shell`
Specifies the shell binary. Default: `which bash`.

```js
$.shell = '/usr/bin/bash'
```

CLI: `--shell=/bin/bash` | Env: `ZX_SHELL=/bin/bash`

### `$.prefix`
Command prepended to every execution. Default: `set -euo pipefail;`.

```js
$.prefix = 'set -e;'
```

CLI: `--prefix='set -e;'`

### `$.postfix`
Appended to the end of every command.

```js
$.postfix = '; exit $LastExitCode'  // For PowerShell
```

CLI: `--postfix='...'`

### `$.quote`
Function for escaping special characters during command substitution.

```js
import { quotePowerShell } from 'zx'
$.quote = quotePowerShell
```

## Output Control

### `$.verbose`
Print all executed commands alongside their outputs. Default: `false`.

```js
$.verbose = true
```

CLI: `--verbose` | Env: `ZX_VERBOSE=true`

### `$.quiet`
Suppress all output. Default: `false`.

```js
$.quiet = true
```

CLI: `--quiet` | Env: `ZX_QUIET=true`

## Environment & Directory

### `$.env`
Environment variables map. Defaults to `process.env`.

```js
$.env = { ...process.env, NODE_ENV: 'production' }
```

### `$.cwd`
Current working directory for all processes created with `$`.

```js
$.cwd = '/tmp'
```

CLI: `--cwd=/foo/bar`

## Execution Control

### `$.timeout`
Default timeout for command execution. Accepts duration strings like `'30s'`, `'5m'`.

```js
$.timeout = '1s'
$.timeoutSignal = 'SIGKILL'
```

### `$.nothrow`
When `true`, non-zero exit codes don't throw. Sets the `ok` boolean on the result.

```js
$.nothrow = true
```

### `$.detached`
Run processes in detached mode.

```js
$.detached = true
```

### `$.halt`
When `true`, processes won't start automatically — call `.run()` manually.

```js
const p = $({ halt: true })`command`
// ... setup
const o = await p.run()
```

## Process Control

### `$.preferLocal`
Prefer locally installed packages (from `node_modules/.bin`) over globally installed ones.

```js
$.preferLocal = true

// Or specify directory:
$.preferLocal = '/path/to/bin'
$.preferLocal = ['/path/to/bin', '/another/path/bin']
```

CLI: `--prefer-local` (alias `-l`)

### `$.spawn` / `$.spawnSync`
Override the spawn API. Default: `child_process.spawn`.

### `$.kill`
Override the kill function for process trees.

```js
import treekill from 'tree-kill'

$.kill = (pid, signal = 'SIGTERM') => {
  return new Promise((resolve, reject) => {
    treekill(pid, signal, (err) => {
      if (err) reject(err)
      else resolve()
    })
  })
}
```

### `$.killSignal`
Signal sent to kill a process. Default: `'SIGTERM'`.

### `$.timeoutSignal`
Signal used when timeout fires. Default: `'SIGTERM'`.

### `$.delimiter`
Delimiter for splitting command output into lines. Default: `/\r?\n/`.

```js
$.delimiter = /\0/  // null character
```

## Logging

### `$.log`
Custom logging function.

```ts
import { LogEntry, log } from 'zx/core'

$.log = (entry: LogEntry) => {
  switch (entry.kind) {
    case 'cmd':
      process.stderr.write(masker(entry.cmd))
      break
    default:
      log(entry)
  }
}
```

### `$.log.output`
Change the output stream. Default uses `process.stderr`.

```ts
$.log.output = process.stdout
```

### `$.log.formatters`
Customize log entry formatting:

```ts
$.log.formatters = {
  cmd: (entry: LogEntry) => `CMD: ${entry.cmd}`,
  fetch: (entry: LogEntry) => `FETCH: ${entry.url}`
}
```

## Defaults

```ts
$.defaults = {
  cwd:            process.cwd(),
  env:            process.env,
  verbose:        false,
  quiet:          false,
  sync:           false,
  shell:          true,
  prefix:         'set -euo pipefail;',   // for bash
  postfix:        '; exit $LastExitCode', // for powershell
  nothrow:        false,
  stdio:          'pipe',
  detached:       false,
  preferLocal:    false,
  spawn:          childProcess.spawn,
  spawnSync:      childProcess.spawnSync,
  log:            $.log,
  kill:           $.kill,
  killSignal:     'SIGTERM',
  timeoutSignal:  'SIGTERM',
  delimiter:      /\r?\n/,
}
```

## Environment Variables

All CLI options can be set via `ZX_`-prefixed environment variables:

```bash
# Set directly
ZX_VERBOSE=true ZX_SHELL='/bin/bash' zx script.mjs

# Via env file
zx --env=/path/to/.env script.mjs
```
