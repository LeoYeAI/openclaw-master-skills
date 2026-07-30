# MCP Transport Patterns

## stdio Transport

Spawns a local process and communicates via stdin/stdout using JSON-RPC.

**When to use:** Local tools, CLI wrappers, file access, database connections.

### npx (Node.js packages)

```json
{
  "server-name": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@scope/package-name"],
    "env": {
      "API_TOKEN": "${API_TOKEN}"
    }
  }
}
```

The `-y` flag auto-confirms npx download prompts. First run downloads the package; subsequent runs use the cached version.

### uvx (Python packages)

```json
{
  "server-name": {
    "type": "stdio",
    "command": "uvx",
    "args": ["package-name", "--db-path", "${DB_PATH}"]
  }
}
```

No `-y` flag needed. uvx resolves and runs Python packages in isolated environments.

### npm global install

```json
{
  "server-name": {
    "type": "stdio",
    "command": "package-name",
    "args": ["--flag", "value"]
  }
}
```

Requires prior `npm install -g package-name`. The command is the package's binary name.

### pip module

```json
{
  "server-name": {
    "type": "stdio",
    "command": "python3",
    "args": ["-m", "module_name"]
  }
}
```

Requires prior `pip install package-name`. Module name is typically the package name with hyphens replaced by underscores.

## HTTP Transport

Connects to a remote MCP server over HTTP POST.

**When to use:** Cloud-hosted services, shared team servers, SaaS integrations.

### Bearer token auth

```json
{
  "server-name": {
    "type": "http",
    "url": "https://api.example.com/mcp",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}"
    }
  }
}
```

### No auth (public endpoints)

```json
{
  "server-name": {
    "type": "http",
    "url": "https://public.example.com/mcp"
  }
}
```

## Docker Transport

Runs an MCP server inside a Docker container, communicating via stdin/stdout.

**When to use:** Servers that need isolated environments, specific OS dependencies, or complex runtime setups.

### Basic Docker server

```json
{
  "server-name": {
    "type": "stdio",
    "command": "docker",
    "args": ["run", "-i", "--rm", "image-name:tag"]
  }
}
```

The `-i` flag keeps stdin open for JSON-RPC communication. `--rm` cleans up the container when the server exits.

### Docker with volume mounts

```json
{
  "server-name": {
    "type": "stdio",
    "command": "docker",
    "args": ["run", "-i", "--rm", "-v", "/host/path:/container/path", "image-name:tag"]
  }
}
```

### Docker with port mapping

```json
{
  "server-name": {
    "type": "stdio",
    "command": "docker",
    "args": ["run", "-i", "--rm", "-p", "8080:8080", "image-name:tag"]
  }
}
```

Requires `docker` to be installed and running. First run pulls the image if not cached locally.

## Environment Variable References

Config files use `${VAR_NAME}` syntax for secrets. These are resolved at server startup from the shell environment.

**Setting env vars:**

```bash
# Temporary (current session only)
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# Persistent (add to shell profile)
echo 'export GITHUB_TOKEN=ghp_xxxxxxxxxxxx' >> ~/.zshrc
source ~/.zshrc
```

**Security model:**
- Config files store references (`${VAR_NAME}`), never raw secrets
- Actual values live in the shell environment or `.env` files
- Config files are safe to commit to version control (no secrets exposed)
- Each MCP client resolves `${VAR}` references at server startup time
