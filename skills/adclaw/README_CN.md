# AdClaw — 广告素材搜索 Skill

通过自然语言搜索竞品广告创意素材，结果以 H5 页面展示。

## 功能

- 关键词搜索广告素材（App 名称、广告文案、品牌等）
- 按素材类型筛选：视频 / 图片 / 试玩广告
- 按投放地区筛选：东南亚、北美、欧洲、日韩、中东等
- 按时间范围、曝光量、投放天数排序
- 搜索结果生成可视化 H5 页面，支持在线预览视频和图片

## 安装

```bash
npx clawhub install adclaw
```

## 配置

1. 前往 [adclaw.miaozhisheng.tech](https://adclaw.miaozhisheng.tech) 注册并获取 API Key
2. 配置环境变量：

```bash
openclaw config set skills.entries.adclaw.apiKey "你的ADCLAW_API_KEY"
```

## 使用示例

安装配置完成后，直接对 AI 助手说：

- 「搜一下 puzzle game 的视频广告」
- 「找东南亚投放的休闲游戏素材」
- 「看看 temu 最近的广告创意」
- 「搜最近一周曝光最多的电商广告」

## 支持的筛选条件

| 筛选项 | 示例 |
|--------|------|
| 关键词 | puzzle game、temu、电商 |
| 素材类型 | 视频、图片、试玩广告 |
| 投放地区 | 东南亚、美国、日韩、欧洲、中东 |
| 时间范围 | 最近一周、最近一个月、自定义日期 |
| 排序方式 | 最新、最热（曝光量）、投放最久 |

## 链接

- 官网：[adclaw.miaozhisheng.tech](https://adclaw.miaozhisheng.tech)
- GitHub：[github.com/fly0pants/adclaw](https://github.com/fly0pants/adclaw)

---

由 [妙智盛](https://adclaw.miaozhisheng.tech) 提供技术支持
