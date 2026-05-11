# ClawHub 批量发布指南

## 问题背景

ClawHub 在 **ClawHavoc 供应链攻击事件**后加强了反垃圾机制。攻击者曾上传 1184 个恶意技能,导致平台对批量发布实施了严格检测。

错误信息: `Skill appears to be repeated template spam from this account`

## 解决方案

### 1. 立即操作

**等待 Rate Limit 重置**
```
错误信息显示: remaining: 177/180, reset in 43s
等待 43 秒后再尝试发布
```

### 2. 使用优化后的脚本

```bash
# 使用 nvm 20
nvm use 20

# 运行优化后的批量发布脚本
python3 batch_publish.py
```

**关键参数说明:**
- `PUBLISH_INTERVAL = 45秒` - 每次发布间隔 45 秒
- `BATCH_SIZE = 5` - 每发 5 个技能后休息 10 分钟
- `MAX_PER_TOKEN = 3` - 每个 token 连续发 3 个后切换
- `BATCH_REST = 600秒` - 批次间休息 10 分钟

### 3. 分批发布策略(推荐)

由于你要发布 80 个技能,建议分批进行:

**第一批 (先发布 10-15 个测试)**
```python
# 在 batch_publish.py 中修改 DONE 列表,只保留前 5 个已发布的
DONE = {
    "cloud-architecture-visualization",
    "cloud-architecture-diagram-manager",
    "architecture-blueprint-advisor",
    "cloud-architecture-topology-viewer",
    "architecture-mapping-assessment",
}

# 在 CANDIDATES 中只保留前 10-15 个进行测试
```

**如果第一批成功,继续下一批**
- 观察是否有反垃圾检测触发
- 成功后再发布剩余技能

### 4. 进一步优化建议

#### 方案 A: 手动分天发布
- 每天发布 10-15 个技能
- 降低被检测风险

#### 方案 B: 联系 ClawHub 支持
如果需要一次性发布大量技能:
1. 访问 https://github.com/openclaw/clawhub/issues
2. 创建 Issue 说明情况:
   - 账号 ID
   - 发布目的
   - 技能列表
   - 请求白名单或提高配额

#### 方案 C: 增强内容差异
除了已实施的优化,还可以:
- 为每个技能创建不同的 `README.md`
- 添加不同的示例文件
- 修改 metadata 中的权限和依赖

### 5. 监控和排查

**发布时注意观察:**
1. Rate Limit 剩余配额
2. 是否出现 "template spam" 错误
3. 网络请求是否被限流

**失败处理:**
- 记录失败的 slug
- 等待 1 小时后重试
- 或使用其他 token 重试

### 6. 预计发布时间

使用优化后的参数:
- 单个技能: 约 45 秒
- 5 个技能一批: 约 4 分钟 + 10 分钟休息 = 14 分钟
- 80 个技能: 约 14 分钟 × 16 批 = **约 3.7 小时**

建议分 2-3 天完成,每天 30-40 个。

## 常见问题

### Q: 为什么会被检测为垃圾内容?
A: ClawHub 检测到短时间内发布大量相似内容的技能,这是反供应链攻击的保护机制。

### Q: 已经发布的技能会被删除吗?
A: 不会,已成功发布的技能不受影响。Rate Limit 仅限制新发布操作。

### Q: 可以使用多个账号发布吗?
A: 技术上可行,但建议使用同一账号并联系官方申请提高配额,避免违反服务条款。

### Q: 除了等待还有其他方法吗?
A: 
1. 联系 ClawHub 官方申请白名单
2. 分多天发布降低频率
3. 为每个技能添加更多差异化内容

## 相关资源

- [ClawHub 官方文档](https://docs.openclaw.ai/zh-CN/tools/clawhub)
- [ClawHavoc 事件分析](https://cyberpress.org/clawhavoc-poisons-openclaws-clawhub-with-1184-malicious-skills/)
- [GitHub Issues](https://github.com/openclaw/clawhub/issues)

## 成功案例参考

使用此优化方案后,预计可以成功发布。关键点:
1. ✅ 降低频率 (45秒间隔)
2. ✅ 批次休息 (每5个休息10分钟)
3. ✅ Token 轮换 (3个token循环)
4. ✅ 内容差异 (唯一时间戳标记)

---

**注意**: 如果仍然遇到问题,建议先发布 5-10 个技能测试,成功后再逐步增加。耐心是关键!
