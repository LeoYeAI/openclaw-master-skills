--------------------------80187b9f2f8945b5
Content-Disposition: form-data; name="file"; filename="SKILL.md"
Content-Type: application/octet-stream

---
name: go-install-zh
version: 1.0.0
description: 在 Linux 环境安装 Go 编译器，用于 Go 项目编译和测试
---

# Go 编译器安装

在 Linux 环境安装 Go 编译器，用于 Go 项目编译和测试。

## 适用场景

- Go 项目开发
- 运行单元测试
- 编译 Go 程序

## 安装步骤

### 1. 确认系统架构

```bash
uname -m
# x86_64 = amd64
# aarch64 = arm64
```

### 2. 下载并安装

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

### 3. 配置环境变量

```bash
export PATH=$PATH:~/go-sdk/bin
export GOPATH=~/go
export GOROOT=~/go-sdk
```

### 4. 持久化配置

添加到 `~/.bashrc` 或 `~/.profile`：

```bash
echo 'export PATH=$PATH:~/go-sdk/bin' >> ~/.bashrc
echo 'export GOPATH=~/go' >> ~/.bashrc
echo 'export GOROOT=~/go-sdk' >> ~/.bashrc
```

### 5. 验证安装

```bash
go version
go env GOPATH GOROOT
```

## 常用命令

```bash
# 运行测试
go test ./...

# 运行测试（详细输出）
go test ./... -v

# 编译项目
go build -o <output> ./cmd/<entry>

# 下载依赖
go mod download

# 整理依赖
go mod tidy
```

## 资源需求

| 项目 | 数值 |
|------|------|
| 安装包大小 | ~65MB |
| 解压后大小 | ~300MB |
| 内存需求 | 最低 512MB |
| CPU 需求 | 单核即可 |

## 注意事项

1. Go 无运行时依赖，单二进制文件
2. 编译速度极快，适合 CI/CD
3. 建议使用 LTS 版本（如 1.22.x）
4. GOPATH 目录会自动创建

## 版本选择

| 版本 | 说明 |
|------|------|
| go1.22.x | LTS 稳定版（推荐） |
| go1.21.x | 旧稳定版 |
| go1.23.x | 最新版 |

下载地址: https://go.dev/dl/
--------------------------80187b9f2f8945b5--
