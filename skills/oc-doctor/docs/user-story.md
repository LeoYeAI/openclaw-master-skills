[English](user-story.en.md) | [中文](user-story.md)

# 一个 OpenClaw 用户的真实经历

## 凌晨 2 点，飞书群炸了

周五深夜，你正准备睡觉。手机突然弹出一连串飞书消息——不是同事发的，是陌生群里的人在疯狂调戏你的 AI 机器人。

你打开配置文件一看：`groupPolicy: "open"`。

也就是说，任何人把你的机器人拉进任何群，它都会响应。你的 API 额度正在以每分钟几十条的速度被消耗。

你慌忙改了配置、重启了 Gateway。但心里清楚：这个配置问题已经存在好几周了，只是一直没人发现。

## 第二天，上下文又溢出了

早上醒来，发现 Telegram 机器人的回复开始变得"失忆"——前几轮对话的内容完全记不住。

你看了下 session，发现 contextTokens 被设成了 272,000，但模型的实际 contextWindow 只有 200,000。多出来的 72k tokens 从来没有被用到，反而让上下文压缩的时机判断出了问题。

这个数字是上个月换模型的时候残留的，你根本不记得改过它。

## 然后，Gateway 又挂了

下午，机器人完全没反应了。

`ps aux | grep openclaw` 一看——两个 Gateway 进程同时在跑，抢同一个端口。大概率是上次手动重启没杀干净旧进程。

你杀掉多余的进程，重启 Gateway。但等等，日志里还有一堆 `Skipping skill path that resolves outside its configured root.` 的报错在刷屏，每 30 分钟一次。这又是什么？

你开始翻文档、搜 GitHub Issues、逐个排查配置文件...

**两个小时过去了。你只修了三个问题，但不确定还有没有其他的坑。**

---

## 后来，我装了 oc-doctor

```
/oc-doctor
```

一条命令，60 秒后：

```
# OpenClaw 诊断报告

## 概览
- 版本：2026.3.7（有新版 2026.3.8）
- Gateway：运行中（端口 18789）
- 整体健康：需要关注

## 发现

### [CRITICAL] 飞书 groupPolicy 为 "open"
- 任何飞书群都可以与机器人交互
- 修复：改为 "allowlist" 并配置 groupAllowFrom

### [WARNING] 3 个 Telegram 会话模型漂移
- 使用 deepseek/chat，但配置默认为 claude-sonnet-4
- 修复：openclaw sessions update --model ...

### [WARNING] 上下文压缩缺少 reserveTokensFloor
- 没有预留缓冲区，上下文可能在压缩触发前就溢出
- 修复：设置 reserveTokensFloor: 20000

### [WARNING] 浏览器缓存 282 MB
- 修复：rm -rf ~/.openclaw/browser/*

### [INFO] 系统指令占上下文 2.6%
- BOOTSTRAP.md 仍在（588 tokens 可回收）
- HEARTBEAT.md 是空模板（67 tokens 可回收）

...共 12 项发现
```

它不只是告诉你哪里有问题——**它告诉你为什么是问题，影响多大，以及确切的修复命令。**

然后它问：

> 需要我帮你修复吗？可以逐个处理，也可以批量修复所有 WARNING 及以下。

你说"全部修复"。

30 秒后：
- 飞书 groupPolicy 改成了 allowlist
- 漂移的会话模型全部对齐
- 压缩配置补齐了预留缓冲
- 浏览器缓存清理完毕
- BOOTSTRAP.md 归档，空的 HEARTBEAT.md 被替换成了一个实用的心跳检查清单

**之前要两个小时手动排查的事，现在 2 分钟搞定。**

---

## 它发现了我从来不知道的问题

最让我意外的是那些"我以为没问题"的地方：

- **12 个已禁用的 cron 任务**一直躺在配置里，我早忘了它们的存在
- **HEARTBEAT.md 是个空壳**——AGENTS.md 里写着"读取 HEARTBEAT.md"，但这个文件只有标题没有内容，agent 每次心跳都在空跑
- **models.json 里有明文 API 密钥**——虽然是本地文件，但万一哪天不小心 `git init` 了呢？
- **4 个 .bak 备份文件**在默默占空间，是几周前调试时留下的

这些都不是"急性病"，但日积月累就会变成性能下降、token 浪费、安全隐患。

## 现在我每周跑一次

```
/oc-doctor
```

就像给 OpenClaw 做体检。大部分时候报告是"健康"，偶尔冒出一两个 WARNING，当场修掉。

再也不用凌晨 2 点被飞书消息炸醒了。

---

**安装只需一行：**

```bash
npx skills add bryant24hao/oc-doctor -g -y
```
