# 错误码说明

## HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误或步骤条件不满足 |
| 401 | 未授权或 Token 过期 |
| 403 | 无权限访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 常见业务错误

| code / msg | 说明 | 处理方式 |
|------------|------|----------|
| `401` / `未登录或登陆状态已失效` | Token 无效、过期，或 token 格式错误（例如错误加入了 `Bearer ` 前缀） | 重新获取 Token，并确认请求头使用 `authorization: <token>` |
| `400` / `该步骤不可执行` | 当前步骤未准备好或参数不完整 | 检查 `currentStep` 与前置状态 |
| `400` / `请选择章节` | 缺少 `chapterNum` | 正确传入 `chapterNum:number` |
| `400` / `角色 [xxx] 图片未完成` | 角色图还未生成完成 | 先检查 `GET /comic/roles/{presetResourceId}` |
| `400` / `该章节提取分镜场景任务未完成，请稍后再试` | `sceneCaptionsTaskStatus` 还没完成 | 先等章节隐藏任务成功 |
| `400` / `该章节分镜图任务未完成，请稍后再试` | `sceneTaskStatus` 还没完成 | 先等章节隐藏任务成功 |
| `400` / `章节序号无效` | 回退或章节相关操作缺少正确的 `chapterNum` | 显式传入正确的 `chapterNum:number` |
| `400` / `请选择封面` | `saveVideoComposeConfig` 缺少封面字段 | 补齐 `coverList/selectCover/selectCoverUrl` |
| `400` / `分镜场景资源不存在` | `sceneId` 格式错误 | 使用完整 ObjectId 格式 `sceneId` |
| `400` / `参数校验异常: must not be blank` | `prepareVideoComposite` 请求体用了错误字段，缺少真正必填项 | 改用 `{projectId, chapterNum}` |
| `407` / `内容包含敏感词` | 文案触发敏感词 | 修改或替换敏感内容 |
| `5001` / `余额不足` | 梦想值不足 | 提示用户充值或调整策略 |

---

## 敏感词错误 (407)

典型响应：

```json
{
  "code": 407,
  "msg": "内容包含敏感词",
  "data": {
    "sensitiveWords": ["敏感词1", "敏感词2"]
  }
}
```

处理建议：

1. 告诉用户触发了敏感词
2. 指出需要修改的内容
3. 修改后重新提交

---

## 排查顺序建议

当看到 400 类错误时，优先按这个顺序排查：

1. `GET /project/{projectId}` 看 `workflow.currentStep`
2. `GET /comic/roles/{presetResourceId}` 看角色图是否 ready
3. `GET /resource/comicPreset/{presetResourceId}` 看章节隐藏任务字段
4. 检查 `chapterNum`、`imgGenTypeRef`、`tts`、`coverList` 等输入是否完整

## 关于“非法参数 / 请求参数非法”的排查提醒

如果未来遇到这类报错，优先排查：

1. JSON 是否由安全的 JSON builder 构造，而不是字符串拼接
2. `sceneId` 是否是完整 ObjectId，而不是 `sceneUuid`
3. `firstImage` 是否是完整 URL；如果是长签名 URL，不能截断查询参数
4. `imageId` 是否与当前 scene 的 image 资源对应
5. 是否把 `/resource/{storyboardId}` 误读成 `.data.scenes`，或把 `scene/{sceneId}/resources` 误读成 `.data.images[]`

不要把“用了角色图”直接等同于“后端一定会报非法参数”。

live 测试表明，角色图可能被后端接受并返回 `200 success`，只是生成结果语义错误。
