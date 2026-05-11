# 🚀 批量发布快速指南

## 一键启动

```bash
./start_publish.sh
```

这个脚本会：
1. 自动切换到 nvm 20
2. 显示当前发布记录
3. 询问是否继续
4. 开始批量发布

## 常用命令

### 查看发布记录
```bash
python3 view_publish_log.py
```
显示：
- ✅ 已成功发布的技能
- ❌ 发布失败的技能（可重试）
- 📊 总体统计

### 清空记录重新开始
```bash
python3 clear_publish_log.py
```
会自动备份现有记录到 `publish_log_backup_xxx.json`

### 直接运行发布
```bash
python3 batch_publish.py
```

## 发布记录说明

`publish_log.json` 文件结构：
```json
{
  "skills": {
    "cloud-architecture-visualization": {
      "name": "Cloud Architecture Visualization",
      "token_index": 0,
      "status": "success",
      "timestamp": "2026-03-24T10:30:00",
      "error": null
    },
    "some-failed-skill": {
      "name": "Some Failed Skill",
      "token_index": 1,
      "status": "failed",
      "timestamp": "2026-03-24T10:35:00",
      "error": "Rate limit exceeded..."
    }
  },
  "stats": {
    "success": 10,
    "fail": 2,
    "total": 12
  }
}
```

## 关键特性

✅ **自动断点续传** - 重启脚本自动跳过已成功的技能
✅ **失败自动重试** - 失败的技能会在下次运行时重试
✅ **Token 使用记录** - 记录每个技能使用的 token
✅ **详细错误日志** - 记录失败原因便于排查
✅ **防反垃圾优化** - 45秒间隔 + 批次休息机制

## 预计时间

- **单批（5个技能）**: 约 14 分钟
- **全部（80个技能）**: 约 3.7 小时
- **建议**: 分 2-3 天完成

## 故障排查

### 问题：Rate Limit Exceeded
**解决**: 等待 1 小时后重试，或切换到其他 token

### 问题：Template Spam
**解决**: 已优化发布频率和内容差异，如仍遇到：
1. 延长 `PUBLISH_INTERVAL` 到 60-90 秒
2. 延长 `BATCH_REST` 到 15-20 分钟
3. 联系 ClawHub 官方申请白名单

### 问题：部分技能失败
**解决**: 直接重新运行脚本，会自动重试失败的技能

## 文件说明

- `batch_publish.py` - 主发布脚本（已优化）
- `view_publish_log.py` - 查看发布记录
- `clear_publish_log.py` - 清空记录重新开始
- `start_publish.sh` - 一键启动脚本
- `publish_log.json` - 发布记录文件（自动生成）
- `PUBLISH_GUIDE.md` - 详细发布指南
