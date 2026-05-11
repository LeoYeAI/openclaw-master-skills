# 音色管理 API

## 目录

- [获取音色标签列表](#获取音色标签列表)
- [获取音色详情](#获取音色详情)

---

## 获取音色标签列表

获取音色分类标签。

### 请求

```
GET /service/timbre/tabList
```

### 响应

```json
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "name": "豆包配音",
      "type": 1,
      "provider": 4
    },
    {
      "name": "MINIMAX配音",
      "type": 1,
      "provider": 3
    },
    {
      "name": "克隆音色",
      "type": 2
    }
  ]
}
```

### 响应字段

| 字段 | 说明 |
|------|------|
| name | 标签名称 |
| type | 类型：`1`=系统音色，`2`=克隆音色 |
| provider | 提供商ID |

---

## 获取音色详情

获取单个音色的详细信息及试听音频。

### 请求

```
GET /service/timbre/detail/{voiceId}
```

### 路径参数

| 参数 | 说明 |
|------|------|
| voiceId | 音色ID |

### 响应

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": 12345,
    "name": "活力小哥",
    "provider": 4,
    "type": 1,
    "sex": 1,
    "sexLabel": "男",
    "age": 3,
    "ageLabel": "青年",
    "tags": "男,青年",
    "avatar": "https://img.ibidian.com/...",
    "audios": [
      {
        "speed": "0.8",
        "audioUrl": "https://fengfan-fx.oss-cn-beijing.aliyuncs.com/..."
      },
      {
        "speed": "1.0",
        "audioUrl": "https://fengfan-fx.oss-cn-beijing.aliyuncs.com/..."
      },
      {
        "speed": "1.2",
        "audioUrl": "https://fengfan-fx.oss-cn-beijing.aliyuncs.com/..."
      },
      {
        "speed": "1.3",
        "audioUrl": "https://fengfan-fx.oss-cn-beijing.aliyuncs.com/..."
      },
      {
        "speed": "1.4",
        "audioUrl": "https://fengfan-fx.oss-cn-beijing.aliyuncs.com/..."
      },
      {
        "speed": "1.5",
        "audioUrl": "https://fengfan-fx.oss-cn-beijing.aliyuncs.com/..."
      },
      {
        "speed": "1.6",
        "audioUrl": "https://fengfan-fx.oss-cn-beijing.aliyuncs.com/..."
      }
    ],
    "status": 1,
    "statusMsg": "",
    "created": 1756184949
  }
}
```

### 响应字段

| 字段 | 说明 |
|------|------|
| id | 音色ID |
| name | 音色名称 |
| provider | 提供商ID |
| type | 类型 |
| sex | 性别：`1`=男，`2`=女 |
| sexLabel | 性别标签 |
| age | 年龄段ID |
| ageLabel | 年龄段标签 |
| tags | 标签 |
| avatar | 音色头像 |
| audios | 试听音频列表 |
| audios[].speed | 语速倍率 |
| audios[].audioUrl | 音频URL |
| status | 状态：`1`=可用 |

---

## 提供商说明

| provider | 名称 | 特点 |
|----------|------|------|
| 3 | MINIMAX | 音色丰富，情感表现力强 |
| 4 | 豆包配音 | 稳定性好，性价比高 |

---

## 性别与年龄段

### 性别

| sex | 说明 |
|-----|------|
| 1 | 男 |
| 2 | 女 |

### 年龄段

| age | 说明 |
|-----|------|
| 1 | 儿童 |
| 2 | 少年 |
| 3 | 青年 |
| 4 | 中年 |
| 5 | 老年 |

---

## 语速设置

### 可用语速

| 倍率 | 适用场景 |
|------|----------|
| 0.8 | 抒情、缓慢场景 |
| 1.0 | 正常对话 |
| 1.2 | 标准语速（默认） |
| 1.3 | 稍快 |
| 1.4 | 较快 |
| 1.5 | 紧张场景 |
| 1.6 | 快速场景 |

---

## 音色选择建议

### 按角色类型

| 角色类型 | 推荐音色特征 |
|----------|--------------|
| 男主角 | 中青年男声，温暖有磁性 |
| 女主角 | 中青年女声，甜美或知性 |
| 老人 | 老年男/女声，沉稳 |
| 儿童 | 童声，活泼可爱 |
| 旁白/解说 | 中性声音，清晰有力 |

### 按场景类型

| 场景类型 | 推荐音色特征 |
|----------|--------------|
| 悬疑/惊悚 | 低沉、紧张感强 |
| 爱情/浪漫 | 温柔、情感丰富 |
| 喜剧/轻松 | 活泼、有感染力 |
| 历史/古装 | 端庄、有韵味 |
| 现代/都市 | 自然、贴近生活 |

---

## 工作流中的音色配置

在项目工作流的 `novel_extract_roles` 步骤中，需要为角色配置音色。

> **最重要的规则**
>
> `tts` 输入里的 `value` 不能硬编码。
>
> 真实流程必须先调用：
>
> `GET /service/workflow/comic/roles/{presetResourceId}`
>
> 然后直接复用返回的 `data.voiceInputs[0]` 或 `data.roles[0].inputs[0]`。

### 配置方式

音色配置在工作流步骤的 `inputs` 中：

```json
{
  "step": "novel_extract_roles",
  "inputs": [
    {
      "label": "选择音色",
      "name": "tts",
      "type": "voice-clone-select",
      "required": true,
      "options": [
        {"label": "推荐音色", "value": "1"},
        {"label": "我的克隆音色", "value": "2"}
      ],
      "props": {
        "speed": {
          "max": 2,
          "options": [0.8, 1, 1.2, 1.5, 1.8, 2],
          "value": 1.2,
          "min": 0.8
        }
      },
      "value": 12345
    }
  ]
}
```

### 参数说明

| 字段 | 说明 |
|------|------|
| name | 固定值 `tts` |
| type | 固定值 `voice-clone-select` |
| value | 音色ID。**必须使用 live 接口返回值，不要写死示例值** |
| props.speed.value | 默认语速 |
