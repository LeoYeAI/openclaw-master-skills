# VectCut Skill 团队协作规范

## 1. 目标
- 统一新增端点的落地方式，保证多人协作下结构一致、可维护、可回归。
- 所有端点按能力域拆分，不在单文件里平铺。

## 2. 目录职责
- `rules/`：决策规则与异常处理。
- `references/endpoints/`：端点参数契约与请求示例。
- `references/enums/`：本地枚举缓存（用于请求前校验）。
- `prompts/`：路由与请求体生成提示词。
- `scripts/`：curl 请求模板与可复用 shell 脚本。
- `examples/`：基于 curl 的最小闭环示例（用于验收）。

## 3. 新增能力域标准（必须五件套）
以 `<domain>` 表示能力域（如 `filter`、`effect`、`text`）：
- `rules/<domain>_rules.md`
- `references/endpoints/<domain>.md`
- `prompts/<domain>_ops.md`
- `scripts/<domain>_ops.sh`
- `examples/<domain>_ops_demo.sh`

## 4. 命名与边界
- 文件命名统一小写下划线。
- 每个能力域只维护本域端点，不跨域混写。
- 全局规则只放在 `rules/rules.md`，领域细则放在 `<domain>_rules.md`。

## 5. 端点文档规范（references/endpoints）
每个端点必须包含以下小节：
- `Method`
- `Path`
- `用途`
- `请求参数`
- `示例请求`
- `关键响应字段`
- `错误返回`

禁止项：
- 禁止仅写 URL，不写参数语义。
- 禁止把多个能力域混在同一端点文件。

## 6. 枚举文件规范（references/enums）
统一格式：

```json
{
  "source": "GET /cut_jianying/<enum_endpoint>",
  "items": [
    { "name": "xxx" }
  ]
}
```

要求：
- `source` 必填，标记枚举来源接口。
- `items[].name` 必填，作为本地校验唯一字段。
- 同一能力域可拆多个枚举文件（如 `character_effect_types.json`、`scene_effect_types.json`）。

## 7. 脚本规范（scripts）
- 每个能力域默认同时提供 `curl` 与 Python（`requests`）两套请求实现，便于按场景选择。
- 每个端点对应独立请求模板：curl 使用环境变量或 JSON 字符串注入参数，Python 保持同等参数语义。
- 对枚举参数（如 `filter_type`、`effect_type`）必须先做本地校验，再请求接口。
- Python 必须实现错误拦截：HTTP 非 2xx、响应非 JSON、业务 `success=false` 或 `error` 非空、关键字段缺失。
- 若端点文档已定义可识别错误（如 `references/endpoints/effect.md`），Python 必须逐条匹配并给出对应处理策略。
- 失败时保留完整响应体，便于按 `error/Code/Message` 分类处理。

## 8. 规则规范（rules）
- 全局通用异常写入 `rules/rules.md`。
- 领域异常写入 `rules/<domain>_rules.md`。
- 可重试错误最多重试 1 次，禁止无限重试。
- 失败上下文最小集：`endpoint`、`draft_id`、`error`；领域按需补充 `material_id`、`track_name`、`start/end`。

## 9. Prompt 规范（prompts）
- 明确输入、输出要求，输出必须同时包含可直接执行的 curl 命令与 Python 请求示例。
- 明确动作路由范围（如 add/modify/remove）。
- 明确枚举校验规则与冲突错误处理策略。
- Python 输出必须包含错误分支处理逻辑，至少覆盖端点文档中的已知错误返回。

## 10. Example 规范（examples）
- 必须同时提供 curl 与 Python 的最小闭环演示。
- 对可修改型能力，优先提供 `add -> modify -> remove` 链路。
- Python 示例必须展示错误拦截分支（至少覆盖端点文档中的已知错误）。
- 示例必须保留响应输出，便于排错与重试。

## 11. 索引维护
新增或变更能力域后，必须同步更新：
- `references/endpoint_params.md`
- `references/references.md`
- `SKILL.md` 中的能力域索引

## 12. 提交前检查清单
- 是否新增了五件套文件。
- 端点文档是否包含完整小节。
- 枚举是否为 `source + items[].name` 结构。
- 脚本是否同时提供 curl 与 Python，并包含本地枚举校验。
- Python 是否覆盖 HTTP/解析/业务错误与端点文档已知错误分支。
- 示例是否提供 curl + Python 最小闭环并可跑通。
- 索引文件是否已同步.

# Git分支与合并规范
- 禁止直接向 `main` 分支提交代码。
- 所有改动必须从功能分支发起，例如：`feature/effect-endpoints`、`fix/effect-enum-format`。
- 功能分支必须通过 Pull Request 合并到 `main`。
- Pull Request 至少包含：变更说明、影响范围、验证方式。
- Pull Request 合并前必须完成至少 1 次团队成员 Review。
- 未通过 Review 或验证失败的 Pull Request 不得合并。