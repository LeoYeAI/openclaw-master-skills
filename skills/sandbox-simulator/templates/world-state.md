# 世界状态

## 基本信息
- 当前轮次: 0
- 时间: {time}
- 地点: {location}
- 环境: {environment}
- 天气: {weather}

## 人物状态速览
| 人物 | 位置 | 心情 | 精力 |
|------|------|------|------|
| {name1} | {location1} | {mood1} | {energy1} |
| {name2} | {location2} | {mood2} | {energy2} |

## 推演配置
- 总轮数: {totalRounds}
- 当前状态: initialized
- 状态值: initialized | running | paused | completed

## 历史压缩配置
- 滑动窗口: 10轮
- 压缩策略: 保留最近10轮详细记录，更早的轮次压缩成摘要

## 待注入事件
<!-- 下一轮需要注入的事件，每条一行 -->
<!-- 格式: - {事件描述} -->

## 场景描述
{sceneDescription}

## 特殊规则
<!-- 可选：场景特有的规则或限制 -->
- {rule1}
- {rule2}

## 统计信息
- 创建时间: {createdAt}
- 最后更新: {updatedAt}
- 已完成轮数: 0
