# China RSS Feed Skill
# 中国RSS订阅技能

## Overview
## 概述

This OpenClaw skill helps users set up an RSS subscription system with Chinese mirror support. It provides step-by-step instructions for installing the feed tool, importing RSS feeds, and aggregating subscription content.

此OpenClaw技能帮助用户在中国网络环境下设置RSS订阅系统，提供安装feed工具、导入RSS订阅源和聚合订阅内容的分步指南。

## Features
## 功能

- Install and configure the feed tool with Chinese mirror
- 安装并配置带有中国镜像支持的feed工具
- Import a comprehensive list of English tech/blog RSS feeds via OPML
- 通过OPML导入全面的英文技术/博客RSS订阅源列表
- Aggregate RSS subscriptions using the rss-digest skill
- 使用rss-digest技能聚合RSS订阅
- Step-by-step instructions tailored for users in China
- 专为中国用户设计的分步指南

## Installation
## 安装

1. Clone or download this skill to your OpenClaw workspace
   将此技能克隆或下载到您的OpenClaw工作区

2. Place the skill in your OpenClaw skills directory (usually `~/.openclaw/workspace/skills/`)
   将技能放在您的OpenClaw技能目录中（通常是 `~/.openclaw/workspace/skills/`）

3. Refresh OpenClaw or restart the gateway to discover the new skill
   刷新OpenClaw或重启网关以发现新技能

## Usage Steps
## 使用步骤

### Step 1: Install the feed tool
### 步骤1：安装feed工具

Run the following commands to install the feed tool with Chinese mirror support:

执行以下命令安装带有中国镜像支持的feed工具：

```bash
# Update apt
sudo apt update
# Install Go
sudo apt install golang-go
# Set Chinese mirror
export GOPROXY=https://goproxy.cn,direct
# Install feed
go install github.com/odysseus0/feed/cmd/feed@latest
```

### Step 2: Install rss-digest skill
### 步骤2：安装rss-digest技能

Use the following prompt to install the rss-digest skill:

使用以下提示词安装rss-digest技能：

```
安装`rss-digest`技能
```

### Step 3: Import RSS feeds
### 步骤3：导入RSS订阅源

![Andrej Karpathy推荐的RSS订阅源](./image2.jpg)
[https://x.com/zodchiii/status/2034924354337714642?s=46](https://x.com/zodchiii/status/2034924354337714642?s=46)

Use the rss-digest skill to import the provided OPML file containing English tech/blog RSS feeds:

使用rss-digest技能导入包含英文技术/博客RSS订阅源的OPML文件：

```
使用`rss-digest`技能导入以下opml，
<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
  <head>
    <title>Blog Feeds</title>
  </head>
  <body>
    <outline text="Blogs" title="Blogs">
      <outline type="rss" text="simonwillison.net" title="simonwillison.net" xmlUrl="https://simonwillison.net/atom/everything/" htmlUrl="https://simonwillison.net"/>
      <outline type="rss" text="jeffgeerling.com" title="jeffgeerling.com" xmlUrl="https://www.jeffgeerling.com/blog.xml" htmlUrl="https://jeffgeerling.com"/>
      <!-- ... more feeds in the complete OPML ... -->
    </outline>
  </body>
</opml>
```

### Step 4: Aggregate RSS subscriptions
### 步骤4：聚合RSS订阅

Use the following prompt to aggregate your RSS subscriptions:

使用以下提示词聚合您的RSS订阅：

```
使用`rss-digest`技能聚合RSS订阅
```

![最终效果](./image1.png)

## Requirements
## 要求

- Linux operating system with apt package manager
- 带有apt包管理器的Linux操作系统
- sudo privileges to install dependencies
- 安装依赖所需的sudo权限
- Internet connection in China
- 中国境内的互联网连接
- OpenClaw agent environment
- OpenClaw代理环境

## Notes
## 注意事项

- This skill is specifically designed for users in China and includes Chinese mirror configuration
- 此技能专为中国用户设计，包含中国镜像配置
- The OPML file contains a comprehensive list of English tech and blog RSS feeds
- OPML文件包含全面的英文技术和博客RSS订阅源列表
- The rss-digest skill must be installed separately
- rss-digest技能需要单独安装
- If you encounter network issues, try using alternative Chinese Go proxies
- 如果遇到网络问题，请尝试使用其他中国Go代理

## License
## 许可证

MIT License
