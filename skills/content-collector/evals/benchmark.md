# Content-Collector Eval Benchmark

> 日期：2026-03-09
> 模型：idealab/claude-opus-4-6

## 总览

| Test Case | With Skill | Without Skill | Delta |
|---|---|---|---|
| blog-url-collection (6 assertions) | 6/6 (100%) | 3/6 (50%) | **+50%** |
| bilibili-video-collection (4 assertions) | 4/4 (100%) | 0/4 (0%) | **+100%** |
| recall-search (3 assertions) | 3/3 (100%) | 2/3 (67%) | **+33%** |
| **总计 (13 assertions)** | **13/13 (100%)** | **5/13 (38%)** | **+62%** |

## Skill 提升倍数：2.6x

## 关键发现

### 1. B站视频场景差距最大（0% → 100%）
Without-skill 完全不知道本地 bilibili 脚本的存在，不知道 Supadata 不支持B站，
无法生成视频专属字段，自己也承认"基本在盲人摸象"。
Skill 提供了完整的工具链和决策路径。

### 2. 博客收藏场景差距显著（50% → 100%）
Without-skill 能完成基本的"抓取+存储"，但：
- 不用 YAML frontmatter（用简单 markdown 列表）
- 不做内容分类（统一放 collections/ 根目录）
- 不提取核心观点和要点摘录
- 不知道 Supadata API

### 3. 检索场景差距中等（67% → 100%）
Without-skill 知道用 grep 搜索，但不知道 tags.md/index.md 索引文件的存在，
搜索效率低且不确定在哪里找。Skill 提供了三层搜索策略。

## 结论
Content-collector Skill 是典型的 **能力增强型(Capability Uplift)** Skill，
基础模型无法独立完成的任务（B站工具链、结构化存储规范、索引体系）
是 Skill 的核心价值。该 Skill 应持续维护和测试。

## 改进建议
1. B站转录无降级方案 — 如果 yt-dlp cookie 过期或 faster-whisper 不可用，没有兜底
2. 搜索策略可以更丰富 — 加入语义搜索能力而非仅靠关键词 grep
