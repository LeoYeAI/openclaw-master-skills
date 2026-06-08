# 自动审查@你的PR

## 任务说明
定期检查 GitCode 仓库中@你的评论，如果发现新的@，自动审查相关PR。

## 检查流程
1. 扫描配置的仓库（cann/runtime, cann/oam-tools, cann/oam-tools-diag）
2. 检查所有开放PR的评论
3. 查找包含@newstarzj的评论
4. 过滤掉已经处理过的评论
5. 对新发现的@PR执行代码审查

## 执行方式
- **触发**: 定时任务（每10分钟）
- **检查脚本**: check-mentions.sh
- **审查方式**: 调用 cann-review skill 逐个审查PR

## 状态管理
- 状态文件: `.mention-state.json`
- 记录已处理的评论ID，避免重复审查

## 使用方法

### 手动触发检查
```bash
cd ~/.openclaw/workspace/skills/cann-review
./check-mentions.sh
```

### 定时任务配置
通过 OpenClaw cron 配置，每10分钟自动运行一次。
