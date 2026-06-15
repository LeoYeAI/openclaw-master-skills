# AdMapix — 广告情报与应用分析 Skill

[English](README.md)

一站式广告情报助手。通过自然语言搜索广告素材、分析应用、查看排行榜、追踪下载量/收入、获取市场洞察。

## 功能

- **素材搜索** — 按关键词、地区、媒体、素材类型搜索广告创意，支持 H5 可视化结果
- **应用分析** — 查询任意应用的详情、开发者信息、广告素材库
- **排行榜** — App Store / Google Play 官方榜单，推广排行、下载排行、收入排行
- **下载量与收入** — 追踪下载量和收入的时间趋势（第三方估算数据）
- **投放分布** — 分析应用在哪些国家、哪些媒体位、用什么素材类型投放广告
- **市场分析** — 按国家、媒体渠道、广告主、流量主维度的行业级洞察
- **深度分析** — 多维度综合报告，整合以上所有能力

## 安装

```bash
npx clawhub install admapix
```

## 配置

1. 前往 [www.admapix.com](https://www.admapix.com) 注册并获取 API Key
2. 配置环境变量：

```bash
openclaw config set skills.entries.admapix.apiKey "你的ADMAPIX_API_KEY"
```

## 使用示例

安装配置完成后，直接对 AI 助手说：

| 分类 | 示例指令 |
|------|----------|
| 素材搜索 | 「搜一下 puzzle game 的视频广告」「找东南亚投放的休闲游戏素材」 |
| 应用分析 | 「分析一下 Temu」「TikTok 的开发者是谁？」 |
| 排行榜 | 「美国 App Store 免费榜」「这周广告投放量最大的 App」 |
| 下载量 | 「Temu 最近下载量怎么样？」「对比 Temu 和 SHEIN 的下载量」 |
| 投放分布 | 「Temu 主要在哪些国家投广告？」「这个游戏用了哪些广告渠道？」 |
| 市场分析 | 「全球游戏广告市场哪个国家最大？」「谁是最大的游戏广告主？」 |
| 深度分析 | 「全面分析 Temu 的广告策略」「对比 Temu 和 SHEIN」 |

支持 **中文** 和 **英文** 双语 — 助手会自动匹配你的语言。

## 链接

- 官网：[www.admapix.com](https://www.admapix.com)
- GitHub：[github.com/fly0pants/admapix](https://github.com/fly0pants/admapix)

---

由 [妙智盛](https://www.admapix.com) 提供技术支持
