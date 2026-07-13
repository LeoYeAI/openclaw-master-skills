# Eval: bilibili-video-collection (WITHOUT skill)

## 执行计划摘要
- 工具：web_fetch（可能被反爬）→ web_search 补充 → write
- 路径：workspace/collections/2026-03-09-AI-Agent-视频标题.md
- 格式：Markdown，简单元数据列表
- 提取：标题、UP主、简介、标签、封面URL、元数据
- 转录：不确定，提了3种方式但都不确定能否成功

## 关键差异点（vs with-skill 预期）
- ❌ 不知道有 bilibili_extract.py 和 bilibili_transcribe.sh 脚本
- ❌ 不知道用 yt-dlp + faster-whisper 的本地转录方案
- ❌ 不知道 Supadata 不支持B站（需要本地流程）
- ❌ 没有 YAML frontmatter 中的视频专属字段（duration/platform/bvid/stats）
- ❌ 没有分类到 collections/videos/ 子目录
- ❌ 没有评论提取能力
- ⚠️ 自己也承认"执行效果会比较粗糙，可能遗漏关键步骤"
