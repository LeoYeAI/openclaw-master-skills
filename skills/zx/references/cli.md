# Zx CLI Reference

## Basic Usage

```bash
zx script.mjs                  # Run a script
npx zx script.mjs              # Via npx (no install needed)
npx zx@8.6.0 script.mjs        # Pin to specific version
node -r zx/globals script.mjs  # As Node.js preload
node --import zx/globals script.mjs  # As Node.js import loader
```

## CLI Flags

### `--eval`
Evaluate the following argument as a script.

```bash
cat package.json | zx --eval 'const v = JSON.parse(await stdin()).version; echo(v)'
```

### `--install`
Auto-install missing dependencies before running.

```bash
zx --install script.mjs
```

Specify version via import comment:

```js
import sh from 'tinysh' // @^1
```

### `--registry`
Custom npm registry for dependency resolution.

```bash
zx --registry=https://registry.yarnpkg.com script.mjs
```

### `--quiet`
Suppress any outputs.

```bash
zx --quiet script.mjs
```

### `--verbose`
Print executed commands alongside their outputs.

```bash
zx --verbose script.mjs
```

### `--shell`
Specify a custom shell binary path. Default: `bash`.

```bash
zx --shell=/bin/zsh script.mjs
```

### `--prefer-local` / `-l`
Prefer locally installed packages and binaries.

```bash
zx --prefer-local=/external/node_modules script.mjs
```

### `--prefix` & `--postfix`
Attach commands to the beginning/end of every execution.

```bash
zx --prefix='echo foo;' --postfix='; echo bar' script.mjs
```

### `--cwd`
Set current working directory.

```bash
zx --cwd=/foo/bar script.mjs
```

### `--env`
Specify an env file.

```bash
zx --env=/path/to/.env script.mjs

# Relative to cwd:
zx --cwd='/foo/bar' --env='../.env'  # => /foo/.env
```

### `--ext`
Override the default script extension (`.mjs`).

```bash
zx --ext=js script.zx  # Treat .zx file as .js
```

### `--version` / `-v`
Print current zx version.

### `--help` / `-h`
Print help notes.

### `--repl`
Start zx in interactive REPL mode.

```bash
zx --repl
```

## Running Markdown Scripts

zx interprets `js`, `ts`, `typescript`, `sh`, `shell`, `bash` code blocks from Markdown files. Other code blocks are ignored.

```bash
zx docs/markdown.md
```

```md
# My Script
Here's what this does:
```js
const { stdout } = await $`ls -l`
console.log(stdout)
```

This part runs in bash:
```bash
ls -l | grep name
```
```

The `__filename` inside Markdown points to the `.md` file.

## Remote Scripts

Scripts starting with `https://` are downloaded and executed.

```bash
zx https://raw.githubusercontent.com/google/zx/refs/heads/main/examples/hello.mjs
```

> ⚠️ Make sure you trust the remote source.

## Scripts from stdin

```bash
zx << 'EOF'
await $`pwd`
EOF
```

## File Extension Handling

- Files without extensions (like `.git/hooks/pre-commit`) are treated as ESM by default.
- Non-standard extensions need `--ext`:

```bash
zx script.zx           # Error: Unknown file extension
zx --ext=mjs script.zx # OK
```

## Environment Variables

All CLI options can be set via `ZX_`-prefixed environment variables:

```bash
ZX_VERBOSE=true ZX_SHELL='/bin/bash' zx script.mjs
```

Examples of available env vars:

| Env var | Effect |
|---------|--------|
| `ZX_VERBOSE` | Set verbose mode (`true`/`false`) |
| `ZX_QUIET` | Suppress output (`true`/`false`) |
| `ZX_SHELL` | Custom shell path |
| `ZX_CWD` | Working directory |
| `ZX_ENV` | Path to env file |
| `ZX_PREFIX` | Command prefix |
| `ZX_POSTFIX` | Command postfix |
| `ZX_EXT` | Default extension |
| `ZX_REGISTRY` | npm registry URL |

## `__filename` & `__dirname`

Available in `.mjs` files when using `zx` executable (not present in standard ESM).

```js
console.log(__filename)
console.log(__dirname)
```

## `require()`

Available in `.mjs` files when using `zx` executable (re-added from CJS).

```js
const { version } = require('./package.json')
```
