# SmartQA — 腾讯云智能客服问答

## Overview

通过 Andon 智能客服接口进行自然语言问答，支持多轮对话。

## 调用方式

### 单次提问

```bash
python3 {baseDir}/scripts/smartqa-api.py -q "轻量应用服务器如何登录"
```

### 多轮对话

首次调用后，使用返回的 sessionId 和 agentSessionId 继续追问：

```bash
python3 {baseDir}/scripts/smartqa-api.py -q "那怎么重置密码" \
  --session-id DHAUGF5WUZ40 \
  --agent-session-id 1002076214
```

### Dry Run

```bash
python3 {baseDir}/scripts/smartqa-api.py -q "测试" -n
```

## 接口映射

| 字段 | 来源 | 默认值 |
|---|---|---|
| question | 用户输入（自动编码） | 必填 |
| sessionId | 自动生成或 `--session-id` | 12位随机ID |
| agentSessionId | create/session 返回或 `--agent-session-id` | 自动获取 |
| model | 固定 | D-v3 |
| client | 固定 | offical-smarty-v2 |
| uin/skey | 默认为空 | 空字符串 |

## 展示规则

1. `answer` 字段可能包含 markdown 格式，直接透传给用户
2. 如果 `recommendQuestions` 不为空，以列表形式附带展示
3. 多轮对话时，在回答后附带 sessionId 和 agentSessionId 供继续追问
4. 如果 `partial` 为 true，提示用户回答可能不完整

## 错误码

| Code | 含义 | 解决方案 |
|---|---|---|
| NetworkError | 网络不通 | 检查网络连接 |
| ConnectionTimeout | 连接超时 | 重试 |
| ReadTimeout | 读取超时 | 问题可能过于复杂，重试 |
| HttpError | HTTP 错误 | 查看错误详情 |
| ParseError | 响应解析失败 | 重试 |
| SessionCreateFailed | 会话创建失败 | 重试 |
| EmptyResponse | 未获得回答 | 换个问法重试 |
| StreamInterrupted | SSE 流中断 | 部分回答可能已返回 |
| InvalidParameter | 参数错误 | 检查问题是否为空 |
