--------------------------0aa845c205f28859
Content-Disposition: form-data; name="file"; filename="SKILL.md"
Content-Type: application/octet-stream

---
name: go-install
version: 1.0.0
description: Install Go compiler on Linux for Go project compilation and testing
---

# Go Compiler Installation

Install Go compiler on Linux for Go project development, compilation, and testing.

## Use Cases

- Go project development
- Running unit tests
- Compiling Go programs

## Installation Steps

### 1. Check System Architecture

```bash
uname -m
# x86_64 = amd64
# aarch64 = arm64
```

### 2. Download and Install

**amd64 (x86_64):**
```bash
cd /tmp
curl -LO https://go.dev/dl/go1.22.0.linux-amd64.tar.gz
tar -xzf go1.22.0.linux-amd64.tar.gz
mv go ~/go-sdk
rm go1.22.0.linux-amd64.tar.gz
```

**arm64 (aarch64):**
```bash
cd /tmp
curl -LO https://go.dev/dl/go1.22.0.linux-arm64.tar.gz
tar -xzf go1.22.0.linux-arm64.tar.gz
mv go ~/go-sdk
rm go1.22.0.linux-arm64.tar.gz
```

### 3. Configure Environment Variables

```bash
export PATH=$PATH:~/go-sdk/bin
export GOPATH=~/go
export GOROOT=~/go-sdk
```

### 4. Persist Configuration

Add to `~/.bashrc` or `~/.profile`:

```bash
echo 'export PATH=$PATH:~/go-sdk/bin' >> ~/.bashrc
echo 'export GOPATH=~/go' >> ~/.bashrc
echo 'export GOROOT=~/go-sdk' >> ~/.bashrc
```

### 5. Verify Installation

```bash
go version
go env GOPATH GOROOT
```

## Common Commands

```bash
# Run tests
go test ./...

# Run tests with verbose output
go test ./... -v

# Build project
go build -o <output> ./cmd/<entry>

# Download dependencies
go mod download

# Tidy dependencies
go mod tidy
```

## Resource Requirements

| Item | Value |
|------|-------|
| Download Size | ~65MB |
| Extracted Size | ~300MB |
| Memory | 512MB minimum |
| CPU | Single core sufficient |

## Notes

1. Go has no runtime dependencies, single binary
2. Extremely fast compilation, ideal for CI/CD
3. Recommended to use LTS version (e.g., 1.22.x)
4. GOPATH directory is auto-created

## Version Selection

| Version | Description |
|---------|-------------|
| go1.22.x | LTS stable (recommended) |
| go1.21.x | Previous stable |
| go1.23.x | Latest |

Download: https://go.dev/dl/
--------------------------0aa845c205f28859--
