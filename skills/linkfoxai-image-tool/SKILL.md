---
name: linkfoxai-image-tool
description: 这是紫鸟开放平台Skill，面向普通用户直接执行任务，无需关心内部调用细节；当用户要求直接完成图片上传、场景裂变、商品替换等当前 Skill 覆盖能力，并希望直接拿到最终结果时，优先通过当前 skill 的本地脚本执行；仅在脚本不存在或执行失败时，才回退到开放平台调用。
---

# linkfoxai-image-tool

## Trigger Conditions

- 当用户目标属于当前 Skill 覆盖的能力分组，且希望直接拿到最终结果时，可使用本 Skill。
- 当前 Skill 覆盖的能力分组：
- `linkfox-image-upload`: 图片上传
- `linkfox-scene-fission`: 场景裂变
- `linkfox-shop-replace`: 商品替换
- `linkfox-auto-image-matting`: 自动抠图
- 若用户目标是查询当前 Skill 覆盖任务的状态、处理进度或最终结果，也属于可直接执行的适用场景。

## When Not To Use

- 当用户只需要开放平台接入说明、参数解释、代码开发建议或集成设计时，不要使用本 Skill。
- 当请求不属于当前 Skill 覆盖的能力范围时，不要强行复用本 Skill。
- 当需要你猜测未在契约中声明的参数、字段或调用行为时，不要继续执行，应以现有契约为准。

## Execution Flow

- `Step 1`: 先真实读取 `scripts/脚本使用指导.md`，确认脚本的 payload、成功/失败语义与退出码规则。
- `Step 2`: 再真实读取当前 skill 的 `scripts/` 目录，确认候选脚本是否实际存在。
- `Step 3`: 根据当前执行环境属于 `Win`、`macOS` 还是 `Linux`，按 `tool分组名_平台` 规则组合目标脚本名；`Win` 对应 `.ps1`，`macOS` 与 `Linux` 对应 `.sh`。
- `Step 4`: 若脚本存在且执行成功，直接使用脚本标准输出作为最终结果。
- `Step 5`: 若脚本不存在，或脚本执行失败并返回非 `0` 退出码，则回退到对应的执行型 tool / 开放平台调用链路，继续使用 `requestUrl`、`Raw Request Contract` 与 `Raw Response Contract`。

## Execution Prerequisites

- `callDomain`: `https://sbappstoreapi.ziniao.com/openapi-router`
- `apiKey`: 先确认 `ZNOPEN_API_KEY` 已可用；默认从 `~/.znopen/config.json` 读取，缺失时先提示用户提供，提供后回填文件，完成配置。
- `Runtime Evidence`: 以下内容只描述本地脚本查找、执行与 fallback 规则，不代表当前 skill 已经存在哪些脚本文件；执行时必须真实读取 `scripts/` 目录与 `scripts/脚本使用指导.md` 再做判断。
- `Authorization`: 无需让用户手工拼接请求头，tool 在调用开放平台时会基于可用的 `apiKey` 自动注入该头。
- `requestUrl`: 统一由 `callDomain + sourceOpenPath` 组成，调用前应直接使用已生成结果，不建议手工改写。

## Capability Groups

### linkfox-image-upload
- 适用请求：图片上传
- 脚本不可用时可兜底使用的 tool：`postImageV2UploadByBase64`

### linkfox-scene-fission
- 适用请求：场景裂变
- 脚本不可用时可兜底使用的 tool：`postImageV2MakeSceneFission`、`postImageV2MakeInfo`

### linkfox-shop-replace
- 适用请求：商品替换
- 脚本不可用时可兜底使用的 tool：`postImageV2MakeShopReplace`、`postImageV2MakeInfo`

### linkfox-auto-image-matting
- 适用请求：自动抠图
- 脚本不可用时可兜底使用的 tool：`postImageV2MakeCutout`、`postImageV2MakeInfo`

## Call Limits

- tool 发起开放平台请求时，必须自动带上请求头：`Authorization: Bearer {ApiKey}`。
- `Bearer` 和 `ApiKey` 之间必须有一个空格，不能省略、不能连写、也不能替换为其他前缀。
- 请求方法必须与对应 tool 的 `sourceMethod` 保持一致，不允许自行切换调用方式。
- 请求参数必须严格遵循 `Raw Request Contract`，响应解析与错误处理必须严格遵循 `Raw Response Contract`。
- 当前置条件未满足、凭证缺失或开放平台返回错误时，不应继续盲目重试或猜测字段含义。

## Tool Group Definitions

### linkfox-image-upload

#### `postImageV2UploadByBase64`

- Capability Group: `linkfox-image-upload`
- Use This Tool When: 当用户当前目标属于“图片上传”场景，且对应本地脚本不存在或执行失败时使用；将它作为开放平台兜底入口完成“图片上传”。
- Required Inputs: fileName、base64
- Returns: 重点查看返回字段：msg、traceId、code、viewUrl
- Tool Goal: 图片上传

##### Definition

```yaml
tool: postImageV2UploadByBase64
sourceApiName: 图片上传
sourceMethod: POST
sourceOpenPath: /linkfox-ai/image/v2/uploadByBase64
requestUrl: https://sbappstoreapi.ziniao.com/openapi-router/linkfox-ai/image/v2/uploadByBase64
```

##### Raw Request Contract

```text
{"headers":[{"isRoot":false,"name":"Content-Type","id":"w8pqf70e","type":"","value":"application/json","required":1,"desc":""}],"query":[],"body":[{"isRoot":true,"children":[{"isRoot":false,"name":"fileName","id":"bzxlv5tv","type":"string","required":1,"desc":"文件名（带扩展名）支持格式：jpeg、jpg、png、webp","value":"1.png"},{"isRoot":false,"name":"base64","id":"6bzgux9i","type":"string","required":1,"desc":"图片数据base64编码 文件大小：不超过20MB","value":"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="}],"name":"","id":0,"type":"object","value":"","required":0,"desc":"UploadByBase64ReqVo"}]}
```

##### Raw Response Contract

```text
[{"isRoot":true,"children":[{"isRoot":false,"name":"msg","id":"474ze4ft","type":"string","required":0,"desc":"结果描述"},{"isRoot":false,"name":"traceId","id":"gcq4vu8w","type":"string","required":0,"desc":"链路追踪id"},{"isRoot":false,"name":"code","id":"6r3j5kog","type":"integer","required":0,"desc":"结果编码 200成功 非200报错"},{"isRoot":false,"children":[{"isRoot":false,"name":"viewUrl","id":"ohy4rmpb","type":"string","required":0,"desc":"上传成功后的图片访问地址"}],"name":"data","id":"k0lmm7mt","type":"object","required":0},{"isRoot":false,"name":"msgKey","id":"46vvp4b4","type":"string","required":0,"desc":"错误编码"}],"name":"","id":0,"type":"object","value":"","required":0,"desc":"ResponseDto«ApiImageUploadResVo»"}]
```

### linkfox-scene-fission

#### `postImageV2MakeSceneFission`

- Capability Group: `linkfox-scene-fission`
- Use This Tool When: 当用户当前目标属于“场景裂变”场景，且对应本地脚本不存在或执行失败时使用；将它作为开放平台兜底入口完成“场景裂变”。
- Required Inputs: imageUrl、segImageUrl、strength、prompt
- Returns: 重点查看返回字段：msg、traceId、code、id
- Tool Goal: 场景裂变

##### Definition

```yaml
tool: postImageV2MakeSceneFission
sourceApiName: 场景裂变
sourceMethod: POST
sourceOpenPath: /linkfox-ai/image/v2/make/sceneFission
requestUrl: https://sbappstoreapi.ziniao.com/openapi-router/linkfox-ai/image/v2/make/sceneFission
```

##### Input Rules

- Image Input Rule: 当前契约只看到 URL 类图片字段，请按契约中的 `https` 图片地址字段传参。
- 不要自行追加 `base64` 字段，除非它已经明确出现在 `Raw Request Contract` 中。

##### Raw Request Contract

```text
{"headers":[{"isRoot":false,"name":"Content-Type","id":"w8pqf70e","type":"","value":"application/json","required":1,"desc":""}],"query":[],"body":[{"isRoot":true,"children":[{"isRoot":false,"name":"imageUrl","id":"bzxlv5tv","type":"string","required":1,"desc":"原图","value":"https://test-file-ai.linkfox.com/UPLOAD/MANAGE/CASE/SCENE_FISSION/1744309376725860352/image.jpg"},{"isRoot":false,"name":"segImageUrl","id":"6bzgux9i","type":"string","required":0,"desc":"保留区域图，不传会自动调用智能抠图"},{"id":"r8mecvca","name":"strength","type":"number","desc":"生成图与原图相似度 默认值：0.5 值越大相似度度越高 浮点数 小数点后只有一位 可选范围 [0.1,1]","isInit":true,"required":0},{"id":"grl5efmb","name":"prompt","type":"string","desc":"强化内容描述，不传会自动根据参数图提取 最长600字符，超出会截断","isInit":true,"required":0},{"id":"87njvdrs","name":"imageOutputWidth","type":"integer","desc":"输出尺寸 宽度 最长不能超过2048,最短不能低于32","isInit":true,"required":0},{"id":"ukpogp3d","name":"imageOutputHeight","type":"integer","desc":"输出尺寸 高度 最长不能超过2048,最短不能低于32","isInit":true,"required":0},{"id":"ob2j7568","name":"provider","type":"string","desc":"场景裂变模式 SCENE_FISSION_REALISTIC：写实（默认值） SCENE_FISSION_SIMPLE：简约   SCENE_FISSION_INTELLIGENT：智能","isInit":true,"value":"SCENE_FISSION_REALISTIC"},{"id":"g017pou2","name":"outputNum","type":"integer","desc":"输出张数 取值范围：[1,4] 默认值：1","isInit":true,"required":0}],"name":"","id":0,"type":"object","value":"","required":0,"desc":"SceneFissionParamsVo"}]}
```

##### Raw Response Contract

```text
[{"isRoot":true,"children":[{"isRoot":false,"name":"msg","id":"474ze4ft","type":"string","required":0,"desc":"结果描述"},{"isRoot":false,"name":"traceId","id":"gcq4vu8w","type":"string","required":0,"desc":"链路追踪id"},{"isRoot":false,"name":"code","id":"6r3j5kog","type":"integer","required":0,"desc":"结果编码 200成功 非200报错"},{"isRoot":false,"children":[{"isRoot":false,"name":"id","id":"ohy4rmpb","type":"integer","required":0,"desc":"作图任务ID"}],"name":"data","id":"k0lmm7mt","type":"object","required":0},{"isRoot":false,"name":"msgKey","id":"46vvp4b4","type":"string","required":0,"desc":"错误编码"}],"name":"","id":0,"type":"object","value":"","required":0,"desc":"ResponseDto«OnlyIdVo»"}]
```

#### `postImageV2MakeInfo`

- Capability Group: `linkfox-scene-fission`
- Use This Tool When: 当用户当前目标属于“场景裂变”场景，且对应本地脚本不存在或执行失败时使用；将它作为开放平台兜底入口完成“获取AI作图结果”。
- Required Inputs: id
- Returns: 重点查看返回字段：msg、traceId、code、id
- Reuse Note: 该 tool 名称在多个能力分组中复用；当前块表示它在 `linkfox-scene-fission` 场景下的使用入口，按当前分组目标理解即可。
- Tool Goal: 获取AI作图结果

##### Definition

```yaml
tool: postImageV2MakeInfo
sourceApiName: 获取AI作图结果
sourceMethod: POST
sourceOpenPath: /linkfox-ai/image/v2/make/info
requestUrl: https://sbappstoreapi.ziniao.com/openapi-router/linkfox-ai/image/v2/make/info
```

##### Raw Request Contract

```text
{"headers":[{"isRoot":false,"name":"Content-Type","id":"w8pqf70e","type":"","value":"application/json","required":1,"desc":""}],"query":[],"body":[{"isRoot":true,"children":[{"isRoot":false,"name":"id","id":"bzxlv5tv","type":"string","required":1,"desc":"作图任务ID","value":"111"}],"name":"","id":0,"type":"object","value":"","required":0,"desc":"OnlyIdVo"}]}
```

##### Raw Response Contract

```text
[{"isRoot":true,"children":[{"isRoot":false,"name":"msg","id":"474ze4ft","type":"string","required":0,"desc":"结果描述"},{"isRoot":false,"name":"traceId","id":"gcq4vu8w","type":"string","required":0,"desc":"链路追踪id"},{"isRoot":false,"name":"code","id":"6r3j5kog","type":"integer","required":0,"desc":"结果编码 200成功 非200报错"},{"isRoot":false,"children":[{"isRoot":false,"name":"id","id":"ohy4rmpb","type":"integer","required":0,"desc":"作图任务ID"},{"isRoot":false,"name":"status","id":"gcq4vu8w","type":"integer","required":0,"desc":"状态 1.排队中 2.生成中 3.成功 4.失败"},{"isRoot":false,"name":"errorCode","id":"6r3j5kog","type":"string","required":0,"desc":"错误码"},{"isRoot":false,"name":"errorMsg","id":"46vvp4b4","type":"string","required":0,"desc":"错误文字描述"},{"isRoot":false,"name":"resultList","id":"k0lmm7mt","type":"array","required":0,"desc":"输出结果图片数组","children":[{"isRoot":false,"name":"id","id":"item1","type":"integer","required":0,"desc":"图片ID"},{"isRoot":false,"name":"status","id":"item2","type":"integer","required":0,"desc":"状态 0.生成中 1.成功 2.失败"},{"isRoot":false,"name":"url","id":"item3","type":"string","required":0,"desc":"高清图"},{"isRoot":false,"name":"width","id":"item4","type":"integer","required":0,"desc":"宽"},{"isRoot":false,"name":"height","id":"item5","type":"integer","required":0,"desc":"高"},{"isRoot":false,"name":"format","id":"item6","type":"string","required":0,"desc":"格式"}]}],"name":"data","id":"k0lmm7mt","type":"object","required":0},{"isRoot":false,"name":"msgKey","id":"46vvp4b4","type":"string","required":0,"desc":"错误编码"}],"name":"","id":0,"type":"object","value":"","required":0,"desc":"ResponseDto«ApiImageMakeResVo»"}]
```

### linkfox-shop-replace

#### `postImageV2MakeShopReplace`

- Capability Group: `linkfox-shop-replace`
- Use This Tool When: 当用户当前目标属于“商品替换”场景，且对应本地脚本不存在或执行失败时使用；将它作为开放平台兜底入口完成“商品替换”。
- Required Inputs: imageUrl、sourceImageUrl、targetOriginUrl、targetImageUrl
- Returns: 重点查看返回字段：msg、traceId、code、id
- Tool Goal: 商品替换

##### Definition

```yaml
tool: postImageV2MakeShopReplace
sourceApiName: 商品替换
sourceMethod: POST
sourceOpenPath: /linkfox-ai/image/v2/make/shopReplace
requestUrl: https://sbappstoreapi.ziniao.com/openapi-router/linkfox-ai/image/v2/make/shopReplace
```

##### Input Rules

- Image Input Rule: 当前契约只看到 URL 类图片字段，请按契约中的 `https` 图片地址字段传参。
- 不要自行追加 `base64` 字段，除非它已经明确出现在 `Raw Request Contract` 中。

##### Raw Request Contract

```text
{"headers":[{"isRoot":false,"name":"Content-Type","id":"w8pqf70e","type":"","value":"application/json","required":1,"desc":""}],"query":[],"body":[{"isRoot":true,"children":[{"isRoot":false,"name":"imageUrl","id":"bzxlv5tv","type":"string","required":1,"desc":"商品原图","value":"https://linkfoxai-ailab.oss-cn-shenzhen.aliyuncs.com/UPLOAD/1701144666432344064/2024/11/18/96a7a42fc965491dbc625d2db09f2478.png"},{"isRoot":false,"name":"sourceImageUrl","id":"6bzgux9i","type":"string","required":0,"desc":"原图抠出来的商品图"},{"id":"r8mecvca","name":"targetOriginUrl","type":"string","desc":"替换的目标原图","isInit":true,"required":1,"value":"https://linkfoxai-ailab.oss-cn-shenzhen.aliyuncs.com/UPLOAD/1701144666432344064/2024/11/18/9778678b4724467485346248032387ec.png"},{"id":"grl5efmb","name":"targetImageUrl","type":"string","desc":"替换的目标原图抠图结果","isInit":true,"required":0},{"id":"87njvdrs","name":"denoiseStrength","type":"string","desc":"生成图变化程度 默认值：0.5 越大越高 浮点数 可选范围 [0,1]","isInit":true,"required":0},{"id":"ukpogp3d","name":"imageOutputWidth","type":"integer","desc":"输出尺寸 宽度 最长边不能超过4096,最短边不能低于32","isInit":true,"required":0},{"id":"g017pou2","name":"imageOutputHeight","type":"integer","desc":"输出尺寸 高度 最长边不能超过4096,最短边不能低于32","isInit":true,"required":0},{"id":"vtarf9ph","name":"outputNum","type":"integer","desc":"输出张数 取值范围：[1,4] 默认值：1","isInit":true,"required":0}],"name":"","id":0,"type":"object","value":"","required":0,"desc":"ShopReplaceParamsVo"}]}
```

##### Raw Response Contract

```text
[{"isRoot":true,"children":[{"isRoot":false,"name":"msg","id":"474ze4ft","type":"string","required":0,"desc":"结果描述"},{"isRoot":false,"name":"traceId","id":"gcq4vu8w","type":"string","required":0,"desc":"链路追踪id"},{"isRoot":false,"name":"code","id":"6r3j5kog","type":"integer","required":0,"desc":"结果编码 200成功 非200报错"},{"isRoot":false,"children":[{"isRoot":false,"name":"id","id":"ohy4rmpb","type":"integer","required":0,"desc":"作图任务ID"}],"name":"data","id":"k0lmm7mt","type":"object","required":0},{"isRoot":false,"name":"msgKey","id":"46vvp4b4","type":"string","required":0,"desc":"错误编码"}],"name":"","id":0,"type":"object","value":"","required":0,"desc":"ResponseDto«OnlyIdVo»"}]
```

#### `postImageV2MakeInfo`

- Capability Group: `linkfox-shop-replace`
- Use This Tool When: 当用户当前目标属于“商品替换”场景，且对应本地脚本不存在或执行失败时使用；将它作为开放平台兜底入口完成“获取AI作图结果”。
- Required Inputs: id
- Returns: 重点查看返回字段：msg、traceId、code、id
- Reuse Note: 该 tool 名称在多个能力分组中复用；当前块表示它在 `linkfox-shop-replace` 场景下的使用入口，按当前分组目标理解即可。
- Tool Goal: 获取AI作图结果

##### Definition

```yaml
tool: postImageV2MakeInfo
sourceApiName: 获取AI作图结果
sourceMethod: POST
sourceOpenPath: /linkfox-ai/image/v2/make/info
requestUrl: https://sbappstoreapi.ziniao.com/openapi-router/linkfox-ai/image/v2/make/info
```

##### Raw Request Contract

```text
{"headers":[{"isRoot":false,"name":"Content-Type","id":"w8pqf70e","type":"","value":"application/json","required":1,"desc":""}],"query":[],"body":[{"isRoot":true,"children":[{"isRoot":false,"name":"id","id":"bzxlv5tv","type":"string","required":1,"desc":"作图任务ID","value":"111"}],"name":"","id":0,"type":"object","value":"","required":0,"desc":"OnlyIdVo"}]}
```

##### Raw Response Contract

```text
[{"isRoot":true,"children":[{"isRoot":false,"name":"msg","id":"474ze4ft","type":"string","required":0,"desc":"结果描述"},{"isRoot":false,"name":"traceId","id":"gcq4vu8w","type":"string","required":0,"desc":"链路追踪id"},{"isRoot":false,"name":"code","id":"6r3j5kog","type":"integer","required":0,"desc":"结果编码 200成功 非200报错"},{"isRoot":false,"children":[{"isRoot":false,"name":"id","id":"ohy4rmpb","type":"integer","required":0,"desc":"作图任务ID"},{"isRoot":false,"name":"status","id":"gcq4vu8w","type":"integer","required":0,"desc":"状态 1.排队中 2.生成中 3.成功 4.失败"},{"isRoot":false,"name":"errorCode","id":"6r3j5kog","type":"string","required":0,"desc":"错误码"},{"isRoot":false,"name":"errorMsg","id":"46vvp4b4","type":"string","required":0,"desc":"错误文字描述"},{"isRoot":false,"name":"resultList","id":"k0lmm7mt","type":"array","required":0,"desc":"输出结果图片数组","children":[{"isRoot":false,"name":"id","id":"item1","type":"integer","required":0,"desc":"图片ID"},{"isRoot":false,"name":"status","id":"item2","type":"integer","required":0,"desc":"状态 0.生成中 1.成功 2.失败"},{"isRoot":false,"name":"url","id":"item3","type":"string","required":0,"desc":"高清图"},{"isRoot":false,"name":"width","id":"item4","type":"integer","required":0,"desc":"宽"},{"isRoot":false,"name":"height","id":"item5","type":"integer","required":0,"desc":"高"},{"isRoot":false,"name":"format","id":"item6","type":"string","required":0,"desc":"格式"}]}],"name":"data","id":"k0lmm7mt","type":"object","required":0},{"isRoot":false,"name":"msgKey","id":"46vvp4b4","type":"string","required":0,"desc":"错误编码"}],"name":"","id":0,"type":"object","value":"","required":0,"desc":"ResponseDto«ApiImageMakeResVo»"}]
```

### linkfox-auto-image-matting

#### `postImageV2MakeCutout`

- Capability Group: `linkfox-auto-image-matting`
- Use This Tool When: 当用户当前目标属于“自动抠图”场景，且对应本地脚本不存在或执行失败时使用；将它作为开放平台兜底入口完成“自动抠图”。
- Required Inputs: imageUrl、subType、clothClass
- Returns: 重点查看返回字段：msg、traceId、code、id
- Tool Goal: 自动抠图

##### Definition

```yaml
tool: postImageV2MakeCutout
sourceApiName: 自动抠图
sourceMethod: POST
sourceOpenPath: /linkfox-ai/image/v2/make/cutout
requestUrl: https://sbappstoreapi.ziniao.com/openapi-router/linkfox-ai/image/v2/make/cutout
```

##### Input Rules

- Image Input Rule: 当前契约只看到 URL 类图片字段，请按契约中的 `https` 图片地址字段传参。
- 不要自行追加 `base64` 字段，除非它已经明确出现在 `Raw Request Contract` 中。

##### Raw Request Contract

```text
{"headers":[{"isRoot":false,"name":"Content-Type","id":"w8pqf70e","type":"","value":"application/json","required":1,"desc":""}],"query":[],"body":[{"isRoot":true,"children":[{"isRoot":false,"name":"imageUrl","id":"bzxlv5tv","type":"string","required":1,"desc":"原图","value":"https://linkfoxai-ailab.oss-cn-shenzhen.aliyuncs.com/UPLOAD/1701144666432344064/2024/11/13/bec32c4461644befb202f86b23502583.png"},{"isRoot":false,"name":"subType","id":"6bzgux9i","type":"integer","required":1,"desc":"抠图类型 1: 通用 2: 人像 3: 商品 9: 服饰 12: 头发 13:人脸","value":"1"},{"id":"r8mecvca","name":"clothClass","type":"string","desc":"服饰分类，只有抠图类型=9（服饰抠图）时才会生效, 可多选，以','号分割","isInit":true,"required":0}],"name":"","id":0,"type":"object","value":"","required":0,"desc":"CutoutParamsVo"}]}
```

##### Raw Response Contract

```text
[{"isRoot":true,"children":[{"isRoot":false,"name":"msg","id":"474ze4ft","type":"string","required":0,"desc":"结果描述"},{"isRoot":false,"name":"traceId","id":"gcq4vu8w","type":"string","required":0,"desc":"链路追踪id"},{"isRoot":false,"name":"code","id":"6r3j5kog","type":"integer","required":0,"desc":"结果编码 200成功 非200报错"},{"isRoot":false,"children":[{"isRoot":false,"name":"id","id":"ohy4rmpb","type":"integer","required":0,"desc":"作图任务ID"}],"name":"data","id":"k0lmm7mt","type":"object","required":0},{"isRoot":false,"name":"msgKey","id":"46vvp4b4","type":"string","required":0,"desc":"错误编码"}],"name":"","id":0,"type":"object","value":"","required":0,"desc":"ResponseDto«OnlyIdVo»"}]
```

#### `postImageV2MakeInfo`

- Capability Group: `linkfox-auto-image-matting`
- Use This Tool When: 当用户当前目标属于“自动抠图”场景，且对应本地脚本不存在或执行失败时使用；将它作为开放平台兜底入口完成“获取AI作图结果”。
- Required Inputs: id
- Returns: 重点查看返回字段：msg、traceId、code、id
- Reuse Note: 该 tool 名称在多个能力分组中复用；当前块表示它在 `linkfox-auto-image-matting` 场景下的使用入口，按当前分组目标理解即可。
- Tool Goal: 获取AI作图结果

##### Definition

```yaml
tool: postImageV2MakeInfo
sourceApiName: 获取AI作图结果
sourceMethod: POST
sourceOpenPath: /linkfox-ai/image/v2/make/info
requestUrl: https://sbappstoreapi.ziniao.com/openapi-router/linkfox-ai/image/v2/make/info
```

##### Raw Request Contract

```text
{"headers":[{"isRoot":false,"name":"Content-Type","id":"w8pqf70e","type":"","value":"application/json","required":1,"desc":""}],"query":[],"body":[{"isRoot":true,"children":[{"isRoot":false,"name":"id","id":"bzxlv5tv","type":"string","required":1,"desc":"作图任务ID","value":"111"}],"name":"","id":0,"type":"object","value":"","required":0,"desc":"OnlyIdVo"}]}
```

##### Raw Response Contract

```text
[{"isRoot":true,"children":[{"isRoot":false,"name":"msg","id":"474ze4ft","type":"string","required":0,"desc":"结果描述"},{"isRoot":false,"name":"traceId","id":"gcq4vu8w","type":"string","required":0,"desc":"链路追踪id"},{"isRoot":false,"name":"code","id":"6r3j5kog","type":"integer","required":0,"desc":"结果编码 200成功 非200报错"},{"isRoot":false,"children":[{"isRoot":false,"name":"id","id":"ohy4rmpb","type":"integer","required":0,"desc":"作图任务ID"},{"isRoot":false,"name":"status","id":"gcq4vu8w","type":"integer","required":0,"desc":"状态 1.排队中 2.生成中 3.成功 4.失败"},{"isRoot":false,"name":"errorCode","id":"6r3j5kog","type":"string","required":0,"desc":"错误码"},{"isRoot":false,"name":"errorMsg","id":"46vvp4b4","type":"string","required":0,"desc":"错误文字描述"},{"isRoot":false,"name":"resultList","id":"k0lmm7mt","type":"array","required":0,"desc":"输出结果图片数组","children":[{"isRoot":false,"name":"id","id":"item1","type":"integer","required":0,"desc":"图片ID"},{"isRoot":false,"name":"status","id":"item2","type":"integer","required":0,"desc":"状态 0.生成中 1.成功 2.失败"},{"isRoot":false,"name":"url","id":"item3","type":"string","required":0,"desc":"高清图"},{"isRoot":false,"name":"width","id":"item4","type":"integer","required":0,"desc":"宽"},{"isRoot":false,"name":"height","id":"item5","type":"integer","required":0,"desc":"高"},{"isRoot":false,"name":"format","id":"item6","type":"string","required":0,"desc":"格式"}]}],"name":"data","id":"k0lmm7mt","type":"object","required":0},{"isRoot":false,"name":"msgKey","id":"46vvp4b4","type":"string","required":0,"desc":"错误编码"}],"name":"","id":0,"type":"object","value":"","required":0,"desc":"ResponseDto«ApiImageMakeResVo»"}]
```
