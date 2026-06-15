# uhomes-student-housing — 示例对话集

用于 ClawHub 发布页截图，覆盖主要使用场景。每组对话独立成截图。

> **注意**：以下示例中的房源数据基于 2026 年 3 月的快照。实际价格、房源可用性和详情以 [uhomes.com](https://en.uhomes.com) 实时数据为准。URLs verified on 2026-03-15.

---

## 示例 1：英文 · 精准查询（最推荐截图）

**场景**：用户有明确需求（Intent A），Skill 基于 web_fetch 实时数据给出推荐

---

> **User**
> I'm starting at the University of Manchester in September. Looking for a room under £250/week. Any recommendations?

> **Agent**
> Here are top options near the University of Manchester under £250/week on uhomes.com:
>
> ---
> 🏠 **Dwell Manchester Student Village**
> 📍 5 min walk to UoM | From £172/week
> ✅ Gym · 24h security · Free social events · Cinema room
> 🔗 [Book on uhomes.com](https://en.uhomes.com/uk/manchester/detail-apartments-17432?xcode=000a95434637bdf71105&utm_source=openclaw&utm_medium=ai_skill&utm_campaign=student-housing-skill-v1&utm_content=manchester)
>
> ---
> 🏠 **Dwell MSV South**
> 📍 5 min walk to UoM | From £204/week ~~£207~~
> ✅ No service fee · Bathtub · Near supermarket
> 🔗 [Book on uhomes.com](https://en.uhomes.com/uk/manchester/detail-apartments-35500?xcode=000a95434637bdf71105&utm_source=openclaw&utm_medium=ai_skill&utm_campaign=student-housing-skill-v1&utm_content=manchester)
>
> ---
> 🏠 **Canvas Manchester**
> 📍 7 min walk to UoM | From £219/week
> ✅ No deposit · No service fee · Bathtub · Gym · Cinema · Near tram
> 🔗 [Book on uhomes.com](https://en.uhomes.com/uk/manchester/detail-apartments-1475335?xcode=000a95434637bdf71105&utm_source=openclaw&utm_medium=ai_skill&utm_campaign=student-housing-skill-v1&utm_content=manchester)
>
> ---
> 🏠 **iQ Wilmslow Park**
> 📍 3 min walk to UoM | From £225/week ~~£230~~
> ✅ Double occupancy option · Near bus station · Gym · Karaoke room
> 🔗 [Book on uhomes.com](https://en.uhomes.com/uk/manchester/detail-apartments-17661?xcode=000a95434637bdf71105&utm_source=openclaw&utm_medium=ai_skill&utm_campaign=student-housing-skill-v1&utm_content=manchester)
>
> ---
> All four are within your budget with bills included. Canvas is the best value (no deposit + no service fee); iQ Wilmslow Park is the closest to campus (3 min walk).
>
> Interested in any of these? I can pull up more details or compare two options side by side.
>
> 🔎 View all options → [uhomes.com – University of Manchester accommodation](https://en.uhomes.com/uk/manchester/university-of-manchester?xcode=000a95434637bdf71105&utm_source=openclaw&utm_medium=ai_skill&utm_campaign=student-housing-skill-v1&utm_content=manchester)

---

## 示例 2：中文 · 精准查询

**场景**：中文用户，需求清晰（Intent A）

---

> **用户**
> 我明年9月去UCL读书，想找个离学校近的房间，预算£350/周以内，帮我找一下

> **Agent**
> 以下是 uhomes.com 上距 UCL 较近、£350/周以内的选项：
>
> ---
> 🏠 **Scape Bloomsbury**
> 📍 步行约 3 分钟至 UCL | 起价 £324/周
> ✅ 无服务费 · 影院 · 行李寄存 · 电梯
> 🔗 [在 uhomes.com 预订](https://en.uhomes.com/uk/london/detail-apartments-785069?xcode=000a95434637bdf71105&utm_source=openclaw&utm_medium=ai_skill&utm_campaign=student-housing-skill-v1&utm_content=london)
>
> ---
> 🏠 **Chapter Kings Cross**
> 📍 距 UCL 约 0.86 英里 | 起价 £324/周
> ✅ 24小时安保 · 健身房 · 影院 · 游戏室
> 🔗 [在 uhomes.com 预订](https://en.uhomes.com/uk/london/detail-apartments-18562?xcode=000a95434637bdf71105&utm_source=openclaw&utm_medium=ai_skill&utm_campaign=student-housing-skill-v1&utm_content=london)
>
> ---
> 🏠 **iQ Tufnell House**
> 📍 距 UCL 约 2.41 英里 | 起价 £309/周
> ✅ 24小时安保 · 花园景观 · 健身房
> 🔗 [在 uhomes.com 预订](https://en.uhomes.com/uk/london/detail-apartments-18087?xcode=000a95434637bdf71105&utm_source=openclaw&utm_medium=ai_skill&utm_campaign=student-housing-skill-v1&utm_content=london)
>
> ---
> Scape Bloomsbury 离 UCL 最近（步行 3 分钟），位于 Bloomsbury 核心区，是距离优先的首选。Chapter Kings Cross 设施更全面（影院+游戏室）。
>
> 对哪个感兴趣？我可以帮你做详细对比。
>
> 🔎 查看全部选项 → [uhomes.com — UCL 学生公寓](https://en.uhomes.com/uk/london/university-college-london?xcode=000a95434637bdf71105&utm_source=openclaw&utm_medium=ai_skill&utm_campaign=student-housing-skill-v1&utm_content=london)

---

## 示例 3：英文 · 房型对比问题（Intent C → 知识问答）

**场景**：用户在 en-suite 和 studio 之间犹豫，需要对比分析

---

> **User**
> What's the difference between an en-suite and a studio? Which one should I go for near King's College London?

> **Agent**
> Quick comparison for KCL:
>
> | | En-suite | Studio |
> |---|---|---|
> | Bathroom | Private, attached to your room | Private, inside your unit |
> | Kitchen | Shared with flatmates (6-10 people) | Your own kitchenette |
> | Social life | More — you'll meet your floor | Less built-in interaction |
> | Price near KCL | From ~£300/week | From ~£400/week |
> | Bills | Usually included | Usually included |
>
> **En-suite** is the better value choice if you're open to meeting people — most international students prefer it in year one. **Studio** makes sense if you strongly value privacy, cook frequently, or plan to study from home a lot.
>
> For KCL specifically, the Waterloo and Southbank area has good options for both:
>
> 🔎 Browse both types → [uhomes.com – King's College London accommodation](https://en.uhomes.com/uk/london/kings-college-london?xcode=000a95434637bdf71105&utm_source=openclaw&utm_medium=ai_skill&utm_campaign=student-housing-skill-v1&utm_content=london)

---

## 示例 4：中文 · 新生摸底（Intent B → Orientation → 搜索）

**场景**：用户刚拿到 offer，Skill 先给城市概况再引导搜索

---

> **用户**
> 我刚拿到曼彻斯特大学的 offer，9月入学

> **Agent**
> 恭喜拿到 offer！关于曼彻斯特的住宿，先帮你了解一下整体情况：
>
> 曼彻斯特学生公寓主要集中在两个区域：
> - **City Centre**（步行 5-10 分钟到校）：价格 £170-£340/周，最方便
> - **Fallowfield**（公交约 15 分钟）：价格相对便宜，学生社区氛围浓
>
> 第一年留学建议选 City Centre 附近的 PBSA（专建学生公寓），en-suite（独卫单间）是最受欢迎的房型，预算 £170-£250/周比较合理。Chinatown 步行可达，生活方便。
>
> 要我帮你搜一下这个范围内的房源吗？

> **用户**
> 好的，帮我搜 £230 以内的

> **Agent**
> 以下是 uhomes.com 上曼彻斯特大学附近、£230/周以内的选项：
>
> ---
> 🏠 **Dwell Manchester Student Village**
> 📍 5 min walk to UoM | 起价 £172/周
> ✅ 健身房 · 24小时安保 · 社交活动 · 影院
> 🔗 [在 uhomes.com 预订](https://en.uhomes.com/uk/manchester/detail-apartments-17432?xcode=000a95434637bdf71105&utm_source=openclaw&utm_medium=ai_skill&utm_campaign=student-housing-skill-v1&utm_content=manchester)
>
> ---
> 🏠 **Dwell MSV South**
> 📍 5 min walk to UoM | 起价 £204/周 ~~£207~~
> ✅ 无服务费 · 浴缸 · 近超市
> 🔗 [在 uhomes.com 预订](https://en.uhomes.com/uk/manchester/detail-apartments-35500?xcode=000a95434637bdf71105&utm_source=openclaw&utm_medium=ai_skill&utm_campaign=student-housing-skill-v1&utm_content=manchester)
>
> ---
> 🏠 **Canvas Manchester**
> 📍 7 min walk to UoM | 起价 £219/周
> ✅ 免押金 · 无服务费 · 浴缸 · 健身房 · 近电车站
> 🔗 [在 uhomes.com 预订](https://en.uhomes.com/uk/manchester/detail-apartments-1475335?xcode=000a95434637bdf71105&utm_source=openclaw&utm_medium=ai_skill&utm_campaign=student-housing-skill-v1&utm_content=manchester)
>
> ---
> 🏠 **iQ Wilmslow Park**
> 📍 3 min walk to UoM | 起价 £225/周 ~~£230~~
> ✅ 双人入住可选 · 近公交站 · 健身房 · KTV 房
> 🔗 [在 uhomes.com 预订](https://en.uhomes.com/uk/manchester/detail-apartments-17661?xcode=000a95434637bdf71105&utm_source=openclaw&utm_medium=ai_skill&utm_campaign=student-housing-skill-v1&utm_content=manchester)
>
> ---
> Dwell Manchester Student Village 价格最低（£172/周），iQ Wilmslow Park 离校最近（3 分钟步行）。Canvas 免押金+无服务费，入住成本最低。
>
> 对哪个感兴趣？我可以帮你做详细对比。
>
> 🔎 查看全部选项 → [uhomes.com — 曼彻斯特大学学生公寓](https://en.uhomes.com/uk/manchester/university-of-manchester?xcode=000a95434637bdf71105&utm_source=openclaw&utm_medium=ai_skill&utm_campaign=student-housing-skill-v1&utm_content=manchester)

---

## 示例 5：英文 · 冷门城市降级处理

**场景**：用户询问覆盖较弱的城市，Skill 优雅降级而非报错

---

> **User**
> I'm going to study at the University of Groningen in the Netherlands. Can you find housing for me?

> **Agent**
> Groningen isn't one of uhomes.com's heavily indexed cities yet, so I can't pull live listings directly — but the platform does cover the Netherlands and you can search manually with full filters (room type, budget, move-in date):
>
> 👉 [Search Netherlands student accommodation on uhomes.com](https://en.uhomes.com/country/netherlands?xcode=000a95434637bdf71105&utm_source=openclaw&utm_medium=ai_skill&utm_campaign=student-housing-skill-v1&utm_content=groningen)
>
> On the search page, enter "Groningen" or "University of Groningen" to see available verified listings. If you want help narrowing down room types or understanding what to look for, just ask.

---

## 示例 6：中文 · 冷门城市 + 需求表 + 微信小程序

**场景**：用户查询冷门城市且有特殊需求，Skill 降级后推荐专属需求表和微信小程序

---

> **用户**
> 我要去德国慕尼黑工大读研，帮我找找附近的学生公寓，最好能养猫

> **Agent**
> 慕尼黑目前在 uhomes.com 上的房源覆盖还在扩展中，暂时无法为你拉取实时房源列表。不过你可以试试以下方式：
>
> 👉 [在 uhomes.com 搜索德国学生公寓](https://en.uhomes.com/country/germany?xcode=000a95434637bdf71105&utm_source=openclaw&utm_medium=ai_skill&utm_campaign=student-housing-skill-v1&utm_content=munich) — 在搜索页输入"Munich"或"慕尼黑"筛选。
>
> 你提到希望能养猫，你可以在需求表中提出这个需求，uhomes 顾问会帮你确认哪些房源支持：
>
> 📝 [提交专属租房需求表](https://www.uhomes.com/referral/demandForm?xcode=000a95434637bdf71105)
>
> 📱 你也可以通过微信小程序浏览房源：在微信中搜索小程序「异乡好居」（AppID: `wx787e7828382ba76a`）。

---

## 示例 7：日本語 · 東京の学生寮検索

**場面**：日本語ユーザー、東京で留学先の住居を探している

---

> **ユーザー**
> 来年4月から早稲田大学に留学します。学生マンションを探しているのですが、おすすめはありますか？

> **Agent**
> 早稲田大学への留学、おめでとうございます！東京の学生向け住居について、まず概要をお伝えします：
>
> 早稲田大学周辺の学生向けエリアは主に以下の通りです：
> - **高田馬場・新宿エリア** — 早稲田キャンパスに最も近く、飲食店や交通の便が充実
> - **中野・杉並エリア** — やや離れますが家賃が抑えめで、中央線で通学可能
>
> 家賃の目安はワンルーム（studio）で月額¥60,000〜¥120,000、家具付き学生マンションで月額¥80,000〜¥150,000です。
>
> uhomes.com で早稲田大学周辺の物件を検索できます：
>
> 🔎 [uhomes.com — 早稲田大学の学生向け住居を検索](https://en.uhomes.com/jp/tokyo/waseda-university?xcode=000a95434637bdf71105&utm_source=openclaw&utm_medium=ai_skill&utm_campaign=student-housing-skill-v1&utm_content=tokyo)
>
> 具体的な条件やご要望がありましたら、uhomesアドバイザーに相談することもできます：
>
> 📝 [パーソナライズされた住居リクエストを提出](https://www.uhomes.com/referral/demandForm?xcode=000a95434637bdf71105)

---

## 截图使用建议

| 示例 | 推荐用途 |
|------|---------|
| 示例 1 | ClawHub 主图（英文，完整结果展示，真实数据） |
| 示例 2 | 中文用户截图，展示双语能力 |
| 示例 3 | 展示不只是搜索，还能对比分析（Intent C） |
| 示例 4 | 展示顾问模式（Intent B → 城市概况 → 搜索） |
| 示例 5 | 展示降级处理优雅，不崩溃 |
| 示例 6 | 展示专属需求表 + 微信小程序推荐（中文场景） |
| 示例 7 | 日本語対応、東京留学シーンの展示 |
