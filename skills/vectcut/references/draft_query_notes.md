# Draft 查询结果解读

## 目标
- 统一解释 `query_script` 返回 `output` 的结构语义。
- 给出可执行的字段关联规则，支持自动校验与后续修正动作。

## 总体配置（顶层）
- `canvas_config`：画布宽高与比例（如 `width/height/ratio`），决定布局坐标基准。
- `fps`：时间线帧率，影响关键帧与时序插值。
- `duration`：草稿总时长，默认单位为微秒（μs），并与 `target_timerange/source_timerange/time_offset` 保持同一单位体系。

## Materials 资源池模型
- `materials` 是资源字典，按类型分桶：`videos`、`audios`、`texts`、`effects`、`stickers`、`text_templates`、`speeds` 等。
- 每个资源条目以 `id` 作为主键，被轨道片段引用。
- 与媒体来源相关的常见字段：`path`、`remote_url`、`resource_id`、`source_platform`。
- `remote_url` 表示素材原始链接，通常可直接访问，用于回源核对、重建素材映射与下载兜底。

## ID 关联规则
- 主关联：`tracks[].segments[].material_id -> materials.<type>[].id`。
- 扩展关联：`tracks[].segments[].extra_material_refs[] -> materials` 中附属条目（如速度、动画、文本特效）。
- 模板复合关联：`text_templates[].text_info_resources[].extra_material_refs` 可继续指向 `effects` 或 `material_animations`。

## 轨道与片段（Timeline）
- `tracks` 按内容类型分轨：`video`、`audio`、`effect`、`filter`、`sticker`、`text`。
- `segment` 核心字段：
  - `material_id`：主素材引用。
  - `target_timerange`：放置到时间线的位置与持续时长。
  - `source_timerange`：源素材裁剪区间。
  - `clip`：几何属性（`alpha/rotation/scale/transform`）。
  - `render_index`：层级顺序。
  - `common_keyframes` / `keyframe_refs`：动画控制。

## 关键帧结构
- 顶层 `keyframes` 为分类容器；实际关键帧通常落在 `segment.common_keyframes`。
- `common_keyframes[].property_type` 指明属性类型（如 `KFTypePositionX`、`KFTypePositionY`）。
- `keyframe_list[]` 单点字段：`time_offset`、`values`、`curveType`、`left_control`、`right_control`。
- 插值逻辑由 `curveType + 控制点 + values` 共同决定。

## 渲染层与可见顺序
- 常见模式：基础画面与音频层 `render_index` 较低，特效/滤镜/贴纸/文本逐级提高。
- 同时间区间冲突时，优先按渲染层与轨道顺序判断可见性。
- `track_render_index` 与 `render_index` 共同决定最终叠放结果。

## 与 query_script 的关联
- query_script 对应草稿查询动作：`POST /cut_jianying/query_script`，在本仓库由 `scripts/draft_ops.sh query` 或 `scripts/draft_ops.py query` 执行。
- 两个脚本都返回统一结构：`{ success, error, output }`。
- 解析入口固定为 `output`：
  - 若 `output` 是字符串，先执行一次 JSON 反序列化得到草稿对象。
  - 若 `output` 已是对象，直接进入下游解析。
- 本文所有规则（materials、ID 关联、tracks、keyframes、render_index）都以该草稿对象为输入。
- 建议在 query_script 后串联标准校验：缺失字段、悬挂引用、时间越界、层级冲突，并输出可执行修复动作。

## 建议的解析流程（用于自动化）
1. 调用 query_script，先校验 `success/error`，失败即中止。
2. 从 `output` 解析草稿对象，统一时间单位按微秒处理。
3. 构建 `material_id -> material` 索引（遍历 `materials` 全桶）。
4. 遍历 `tracks[].segments[]`，校验 `material_id` 与 `extra_material_refs` 是否悬挂。
5. 校验 `target_timerange/source_timerange` 是否越界、是否与草稿总时长冲突。
6. 解析 `common_keyframes`，核对关键帧时间是否落在 segment 时长内。
7. 汇总 `render_index` 与轨道类型，输出层级冲突与遮挡风险。

## 建议的最小诊断字段
- 顶层：`id`、`duration`、`fps`、`canvas_config`、`render_index_track_mode_on`。
- 轨道：`track.id`、`track.type`、`track.name`。
- 片段：`segment.id`、`material_id`、`target_timerange`、`source_timerange`、`render_index`、`extra_material_refs`。
- 素材：`material.id`、`type`、`resource_id`、`path/remote_url`。
- 动画：`property_type`、`time_offset`、`values`、`curveType`。

## 结构完整性检查清单
- 必须存在：`materials`、`tracks`。
- 每个 `segment.material_id` 必须可解析到资源池条目。
- 每个 `extra_material_refs` 必须可解析到附属资源。
- 每个 `target_timerange.duration` 必须大于 0。
- 关键帧时间点不得超出对应 segment 的有效时长。