---
name: webflow-china-speed
description: >
  Webflow + Cloudflare Worker 中国大陆访问加速专项技能。当用户想要优化 Webflow 网站在中国大陆的访问速度时，必须使用此技能。
  触发场景：用户提到 Webflow 网站速度慢、中国大陆无法访问、CF Worker 反向代理优化、Google 资源被屏蔽、Webflow CDN 加速、
  字体加载慢、视频加载慢、jsdmirror 替换、R2 缓存、ICP 备案合规、EdgeOne 国内节点、双域名双 CDN 架构、DNS 地理分流、
  多项目扩展、Geo-DNS、华为云 DNS、腾讯 EdgeOne、大陆备案最小成本方案等话题。
  即使用户只是问"我的 Webflow 网站在中国大陆很慢怎么办"也要触发。
---

# Webflow 网站中国大陆访问加速

解决 Webflow 网站在中国大陆打不开/极慢的问题。方案基于 Cloudflare Worker 反向代理，涉及多项操作：移除被墙的 Google 资源、jQuery 替换为国内镜像、静态资源缓存到 R2、CSS/视频/字体路径改写等。如需更彻底的加速（延迟降至 50-100ms），则需要 ICP 备案并接入腾讯 EdgeOne 国内节点。

---

## 前置条件确认

在开始前，先了解用户现有架构：
- **域名与 Webflow URL**：用户自定义域名是什么？原始 Webflow URL（*.webflow.io）是什么？
- **是否已有 CF Worker**：如果已有，让用户提供现有 Worker 代码；如果没有，需要从头建
- **是否已有 R2 Bucket**：R2 是持久化静态资源缓存的关键
- **CF Account ID**：部署 Worker 需要
- **网站特殊内容**：有没有视频背景、自定义字体、第三方 JS 库？

---

## 诊断清单：检测哪些资源有问题

在中国大陆，以下资源**必然**被屏蔽或严重降速：

| 资源类型 | 问题根源 | 影响 |
|---------|---------|------|
| Google Fonts (`fonts.googleapis.com`) | GFW 封锁 | 字体加载失败，页面渲染阻塞 |
| Google 相关 preconnect/dns-prefetch | DNS 解析超时 | 每次页面请求额外增加 2-5s |
| Google Analytics / gtag | GFW 封锁 | 统计失效（不阻塞渲染，但浪费连接） |
| WebFont Loader (`webfont.js`) | Google 相关 | 同 Google Fonts |
| Webflow CDN (Fastly + CloudFront) | 无大陆节点 | 静态资源从海外回源，RTT 高 |
| Webflow 注入的 jQuery (d3e54v103j8qbb.cloudfront.net) | CloudFront 无大陆节点 | 每次页面加载阻塞约 500ms-2s |
| 视频文件 (`.mp4`/`.webm`) | 无大陆 CDN 节点 | 视频无法起播，需要完整下载 |

**如何快速诊断**：用 `curl` 从国内 IP 测试关键资源，或让用户在国内打开浏览器 DevTools 的 Network 面板，按耗时排序。

---

## 架构方案

```
用户 (中国大陆)
    ↓
Cloudflare Worker (全球节点，含香港/日本/新加坡)
    ↓ 静态资源命中 R2 → 直接返回 (延迟极低)
    ↓ 静态资源未命中 → 回源 Webflow CDN → 异步写入 R2
    ↓ HTML/动态请求 → 回源 Webflow → HTMLRewriter 改写后返回
    ↓
shenye.webflow.io（原始 Webflow 站点）
```

**关键路径**：
- `/_cdn/{host}/{path}` — 所有 Webflow 静态资源的 R2 缓存路由
- HTMLRewriter — 流式改写 HTML，替换/删除被墙资源链接，无需等待完整 HTML
- R2 Bucket — 永久缓存静态资源（字体、图片、JS、视频），冷启动后无需再回源

---

## 10 项核心优化（已验证）

### [优化 1] HTML 响应加缓存头 + CF 边缘 cacheTtl

**问题**：Webflow 默认返回的 HTML 无缓存头，CF 每次都回源，大陆用户每次都经历完整 RTT。
**方案**：给 HTML 响应加 `cache-control: public, max-age=300, s-maxage=300`，同时在 `fetch()` 里设 `cacheTtl: 300`，让 CF 边缘节点缓存 5 分钟。
**注意**：要 `delete("set-cookie")` 避免带 cookie 的响应被缓存后污染其他用户。

### [优化 2] 移除 Google preconnect / dns-prefetch / gstatic 标签

**问题**：即使不加载 Google Fonts，HTML 里残留的 `<link rel="preconnect" href="fonts.googleapis.com">` 等标签也会让浏览器发起 DNS 查询，在大陆超时后才放弃，消耗 2-5s。
**方案**：用 HTMLRewriter 移除所有 `href` 含 `google` 或 `gstatic` 的 `preconnect`/`dns-prefetch` 标签，以及直接指向 `fonts.googleapis.com`/`fonts.gstatic.com` 的 `<link>` 标签。

### [优化 3] CSS 内 @import fonts.googleapis.com 过滤

**问题**：Webflow 有时会把 Google Fonts 的 `@import` 放进 CSS 文件里（而非 HTML `<link>`），HTMLRewriter 无法处理 CSS 内容。
**方案**：对 `text/css` 响应做文本替换，用正则删除所有 `@import url(...)` 中含 `fonts.googleapis.com` 的行。

### [优化 4] R2 objectKey 包含 query string

**问题**：某些静态资源 URL 带有版本参数（如 `?v=xxx`），如果 R2 key 只用路径，不同版本会映射到同一个 key，导致缓存错乱。
**方案**：objectKey 格式为 `assets/{host}/{path}_{base64(queryString)}`，有 query 时包含编码后的 query 部分。

### [优化 5] jQuery 直接替换为 jsdmirror

**背景**：Webflow 在所有网站的 `</body>` 前自动注入 jQuery 3.5.1，源固定来自 `d3e54v103j8qbb.cloudfront.net`（所有 Webflow 网站共用，URL 中的哈希前缀固定不变）。
**问题**：CloudFront 在大陆没有节点，这个 script 标签会阻塞页面完成渲染。
**方案**：用 HTMLRewriter 将该 `<script src>` 替换为 jsdmirror URL。
**验证**：三个源（CloudFront、cdnjs、jsdmirror）提供的字节完全一致，SHA256 相同，所以标签上原有的 `integrity` SRI 属性仍然能通过校验，无需修改。
```javascript
// HTMLRewriter 里的替换规则
.on('script[src*="d3e54v103j8qbb.cloudfront.net"][src*="jquery"]', {
  element(el) {
    el.setAttribute("src", "https://cdn.jsdmirror.com/npm/jquery@3.5.1/dist/jquery.min.js");
    // crossorigin 属性保留，SRI 跨域校验必须
  }
})
```

### [优化 6] 重写 data-video-urls 属性（背景视频）

**问题**：Webflow 背景视频用 `data-video-urls="url1.mp4,url2.webm"` 属性存储视频地址，这个属性是自定义 attribute，不是标准 `src`，普通的资产 URL 重写（`link/script/img/source`）会遗漏它。
**方案**：单独加一个 HTMLRewriter 规则匹配 `[data-video-urls]`，把属性值按逗号分割后逐个重写到 `/_cdn/` 路径。

### [优化 7] /_cdn/ 支持 HTTP Range 请求

**问题**：视频文件需要 Range 请求才能边加载边播放（206 Partial Content）。如果不处理 Range，R2 会返回整个文件，视频播放器会等待完整下载，首帧延迟高。
**方案**：
- R2 命中时：用 `env.MY_BUCKET.get(key, { range: { offset, length } })` 返回 206
- R2 未命中时：将 Range 头转发给上游，但不缓存分段响应到 R2（只缓存完整 200 响应）

### [优化 8] /_cdn/ CSS 文件缓存前先改写内部 URL

**问题**：`/_cdn/` 处理器默认把资源原样透传并缓存。CSS 文件内部的 `@font-face src: url(https://cdn.prod.website-files.com/...)` 和背景图片等绝对 URL 不会被改写，浏览器加载 CSS 后直接向 Fastly 拉取字体/图片，完全绕过 R2 缓存。这个问题不容易被发现——DevTools 里字体确实是 `.woff2`，但实际走的是 Fastly 而非 R2。
**诊断方法**：`curl` 拉取 `/_cdn/...min.css`，用 `grep -oP 'https?://[^")\\s,]+'` 查找其中所有绝对 URL，看是否仍指向 `cdn.prod.website-files.com`。
**方案**：在 `/_cdn/` 处理器的 R2 未命中回源路径里，对 CSS 文件（`content-type: text/css` 或路径以 `.css` 结尾）先做 URL 改写，再写入 R2 缓存。

### [优化 9] 移除 stylesheet `<link>` 的 SRI integrity 属性

**问题**：Webflow 生成的 HTML 里，CSS `<link>` 标签带有 `integrity="sha384-..."` 属性（Subresource Integrity）。Worker 改写了 CSS 文件内部 URL（优化 8），导致文件内容变化，SHA-384 哈希不再匹配。浏览器会静默拒绝加载该 CSS，**页面彻底失去样式**，且控制台报错容易被忽略。
**方案**：HTMLRewriter 里加一条规则，移除所有 `<link rel="stylesheet">` 上的 `integrity` 属性。
**注意**：jQuery 的 `<script integrity>` 不需要处理，因为我们只是换了 URL 而没有修改文件内容，字节完全一致，SRI 仍然通过。
```javascript
.on('link[rel="stylesheet"][integrity]', {
  element(el) { el.removeAttribute("integrity"); }
})
```
**R2 旧缓存处理**：部署新 Worker 后，R2 里已缓存的 CSS 文件（未经改写的版本）仍然会被命中返回，导致问题持续。需要在 CF Dashboard → R2 → Bucket 里手动删除对应的 CSS 对象，强制下次请求走回源流程重新处理。

### [优化 11] meta og:image / twitter:image 改写到 /_cdn/

**问题**：OG 图片 URL 存在于 `<meta property="og:image" content="...">` 的 `content` 属性里，HTMLRewriter 标准资产选择器 `link[href], script[src], img[src], source[srcset]` **不覆盖 `<meta>` 标签**。

两条路径的后果不同：
- `handleCN`：依赖全文正则兜底改写，属脆弱副作用路径
- `handlePassthrough`（海外爬虫路径）：**完全未处理**——微信/微博/Twitter/Slack 爬虫抓取 OG 图时仍拿到原始 `cdn.prod.website-files.com` 地址，图片不走 R2 缓存

**注意**：不影响浏览器页面加载速度（非阻塞资源），但影响社交分享缩略图抓取速度和成功率。

**方案**：`handleCN` 和 `handlePassthrough` 两条路径的 HTMLRewriter 均需新增规则：

```javascript
.on('meta[property="og:image"], meta[property="og:image:secure_url"], meta[name="twitter:image"], meta[itemprop="image"]', {
  element(el) {
    const v = el.getAttribute("content");
    if (v) el.setAttribute("content", rewriteAsset(v));
  }
})
```

修复后社交爬虫打到 `/_cdn/...` 路径，Worker 代理图片并写入 R2，二次抓取直接命中缓存。

**诊断命令**：`curl -s https://your-domain.com/ | grep -i "og:image"`，确认 `content` 属性已改写为 `/_cdn/cdn.prod.website-files.com/...`。

---

### [优化 10] 补全视频 poster 及 `<source src>` 的改写

**问题**：Webflow 背景视频在 HTML 里同时存在三条并行路径，[优化 6] 只处理了其中一条：

| 属性 | 谁读取 | 优化 6 前 |
|------|-------|---------|
| `data-video-urls` | Webflow JS 运行时 | ✅ 已改写 |
| `<source src>` | 浏览器原生回退 | ❌ 漏网 |
| `data-poster-url` | Webflow JS 设置海报帧 | ❌ 漏网 |
| `<video style="background-image:url(...)">` | 浏览器直接渲染海报 | ❌ 漏网 |

前三条会导致视频/海报仍从 Fastly 加载；`video[style]` 是最隐蔽的——poster 作为内联 CSS 背景图注入，不走任何 src 属性，普通属性扫描完全看不到。

**诊断方法**：`curl` 拉 HTML，搜索 `data-poster-url` 和 `video[style]`，看是否仍有 `https://cdn.prod.website-files.com` 地址。

**方案**：
- 将 `source[srcset]` 改为 `source[src], source[srcset]`，同时覆盖视频源和图片多分辨率
- 新增 `[data-poster-url]` handler 改写 poster URL
- 新增 `video[style]` handler，用正则替换 `background-image:url(...)` 里的绝对地址

---

## 字体优化建议

字体是另一个重要的加速点，与 Worker 改动独立：

1. **格式**：TTF 未压缩，WOFF2 约小 40-60%。在 Webflow Project Settings → Fonts 里，删除 TTF 字体文件，重新上传同一字体的 WOFF2 版本。（转换工具：`woff2_compress` 命令行，或在线工具）
2. **排查无用字体**：在 Webflow 里上传了字体不一定实际用到了。先用 `curl` 拉取网站 HTML，搜索每个字体名，确认实际有被 CSS `font-family` 或 Webflow 样式引用后再保留。未使用的字体是纯负担（169KB/字体的典型值），直接删除。
3. **Adobe Fonts**：Webflow 有 Adobe Fonts 集成入口，但只要没有实际激活的 Kit，不会产生任何网络请求，不需要处理。

---

## 第三方 JS 库注意事项

### 使用 jsdmirror 的正确姿势

jsdmirror (`cdn.jsdmirror.com`) 是 jsDelivr 的镜像，由腾讯 EdgeOne 提供大陆 CDN 节点。URL 格式：
```
https://cdn.jsdmirror.com/npm/{package}@{version}/dist/{file}.min.js
```

**必须**指定版本号和具体文件路径，否则 URL 无效。例：
- ✅ `https://cdn.jsdmirror.com/npm/lenis@1.0.27/dist/lenis.min.js`
- ❌ `https://cdn.jsdmirror.com/npm/lenis`（缺版本和路径，404）

### Lenis 平滑滚动（特别注意）

Webflow 社区流行的 Lenis 集成方案通常是一个**定制 bundle**，包含：
- Lenis 核心库（特定版本）
- Webflow 专属初始化层：读取 `[data-id-scroll]` 元素上的 `data-*` 属性作为配置
- 全局 `window.SScroll` 实例化
- `useAnchor`、`useOverscroll`、`useControls` 等扩展功能

这个定制 bundle **不在 npm 上**，因此 jsdmirror 没有它。如果用户在 Webflow 里自托管了这个 bundle（`.txt` 文件），正确做法是继续使用原有的 Webflow CDN URL——该 URL 属于 `cdn.prod.website-files.com`，Worker 会自动将其重写到 `/_cdn/` 路径并缓存到 R2，无需手动迁移。

**诊断方法**：检查 `.txt` 文件内容，看是否含有 `window.SScroll`、`I("[data-id-scroll]"` 等 Webflow 专属代码，如果有，就不能用 npm 版替换。

---

## Worker 代码模板

完整的可直接部署的 Worker 代码见 `references/worker-template.js`。

使用前需要替换的变量：
- `WEBFLOW_HOST` → 用户的 Webflow 内部 URL（如 `mysite.webflow.io`）
- `R2_PUBLIC_BASE` → R2 Bucket 的公开访问 URL（如 `https://pub-xxxx.r2.dev`）
- `MY_BUCKET` → Worker 绑定的 R2 Bucket 名称（在 wrangler.toml 里配置）

其余代码可直接使用，10 项优化已内置。

---

## 常见"坑"汇总

| 坑 | 说明 |
|----|------|
| `new URL(u, "https://dummy.base")` | 用假域名作 base 是为了让 `new URL()` 能解析相对路径而不报错；对绝对 URL 没有影响 |
| jQuery SRI integrity 属性 | 替换 src 后不需要修改 integrity；三源字节完全相同，SHA256 一致 |
| CloudFront 哈希前缀 | `d3e54v103j8qbb` 对所有 Webflow 网站都是固定的，不是每个项目唯一 |
| R2 缓存残片 | 只缓存完整 200 响应，Range 请求（206）不写 R2，避免缓存片段数据 |
| CSS @import 位置 | Google Fonts 可能在 `<link>` 里也可能在 CSS `@import` 里，两处都要处理 |
| data-video-urls | 背景视频不走 `src` 属性，单独用 HTMLRewriter 规则处理 |
| Lenis 定制 bundle | npm 版 Lenis 没有 Webflow 自动初始化层，不能直接用 jsdmirror 替换 |
| set-cookie 与 HTML 缓存 | 给 HTML 加缓存时必须删 set-cookie 头，否则有 cookie 的响应被缓存后会污染其他用户 |
| CSS 内绝对 URL 绕过 R2 | `/_cdn/` 处理器默认透传原始内容，CSS 里的 `@font-face`/背景图等绝对地址不会被自动改写，需在写入 R2 前先处理 |
| CSS SRI 校验导致无样式 | 改写 CSS 内容后文件哈希变化，HTML 里的 `integrity` 属性会导致浏览器静默拒绝 CSS，页面失去所有样式；需用 HTMLRewriter 移除 stylesheet link 的 integrity 属性 |
| R2 旧缓存需手动清除 | Worker 逻辑更新后，R2 里已缓存的旧版本不会自动失效；若修改了 CSS/JS 的处理逻辑，需在 CF Dashboard 手动删除对应 R2 对象 |
| video[style] 里的 poster | Webflow 把 poster 写成 `style="background-image:url(...)"` 内联样式，不走任何 src 属性，必须单独用 `video[style]` handler + 正则处理 |
| `<source src>` 被标记 data-wf-ignore | Webflow 在 `<source>` 上加 `data-wf-ignore="true"` 表示 JS 会接管，但浏览器在 JS 加载前仍会读取这些标签作为回退，必须改写 |
| meta og:image 在 content 属性里 | `<meta property="og:image" content="...">` 不是 `src`/`href`，HTMLRewriter 标准资产选择器不覆盖它。`handleCN` 依赖全文正则兜底可以 work，但 `handlePassthrough` 完全未处理，社交平台爬虫拿到原始 `cdn.prod` 地址。两条路径均需显式新增 `meta[property="og:image"]` 等 HTMLRewriter 规则 |
| ICP 备案 | 如需使用腾讯 EdgeOne 国内节点（更低延迟），需要 ICP 备案；CF Worker 本身无需备案 |

---

## 进阶：双 CDN + 大陆节点架构

> 适用场景：现有 CF Worker 方案跑通后，进一步降低大陆延迟，解锁境内 CDN 节点。

### 核心原则

CF Worker 本质是"境外加速"——跨境路径无法绕过。要做到质变，需要接入**中国境内 CDN 节点**，前提是 ICP 备案。

**两套系统各自独立**，共同回源同一个 Webflow 源站：

```
DNS 分流（按地区）
  大陆 IP → 大陆域名（备案域名） → 腾讯 EdgeOne 国内节点
  境外 IP → 主域名              → CF Worker（现有方案不动）

两套 CDN 各自缓存，均回源 Webflow 同一源站
```

EdgeOne 侧需要自建的能力：
- 边缘函数（对应 CF Worker，做 HTMLRewriter 资源替换）
- COS 对象存储（对应 CF R2，作静态资源缓存）
- **不要** 让 EdgeOne 从 CF R2 拉取资源——两套商业网络走公网，比直接回源 Webflow 更慢

---

### DNS 分流方案选择

#### 方案 A：主域名在 Cloudflare（推荐，无需迁移 NS）

**实现方式**：CF Worker Route 或 Transform Rules 检测来源地区

```javascript
// Worker 最前面加地区检测
if (request.cf?.country === 'CN') {
  return Response.redirect('https://examplezh.cn' + url.pathname + url.search, 301);
}
// 非 CN 继续走原有加速逻辑
```

或 CF Transform Rules（仪表盘配置，无需改代码）：
```
条件：ip.geoip.country == "CN"
动作：redirect → https://examplezh.cn${uri.path}
```

**优缺点**：
- ✅ 无需迁移 DNS，所有配置在 CF 控制台完成
- ✅ 免费版 Worker 内 `cf.country` 完全可用
- ⚠️ 大陆用户 URL 会跳转到大陆域名（地址栏变化，对大多数场景可接受）
- ❌ CF 免费版不支持 DNS 层 Geo 解析（企业版功能）

#### 方案 B：主域名迁移到支持 Geo-IP 的第三方 DNS

支持的服务商：华为云 DNS、DNSPod、阿里云 DNS

```
# 华为云 / DNSPod 解析规则示例
example.com
  线路：中国大陆 → CNAME → examplezh.cn（→ EdgeOne）
  线路：境外默认 → CNAME → CF 分配的 CNAME 值

examplezh.cn → CNAME → EdgeOne 分配的 CNAME 值
```

**优缺点**：
- ✅ DNS 层透明分流，大陆用户 URL 始终是 example.com，无跳转
- ✅ CF Worker 完整保留，境外流量继续走
- ⚠️ 需要将 NS 从 CF 迁出，迁移期间有短暂 DNS 波动风险
- ⚠️ 迁出 CF 后失去部分 CF 安全防护功能（可降级为 CF CNAME 接入保留部分功能）

| 对比项 | CF DNS + Worker 跳转 | 第三方 Geo-DNS |
|--------|---------------------|--------------|
| DNS 迁移 | 无需 | 需要将 NS 从 CF 迁出 |
| 大陆用户 URL | 跳转到大陆域名 | 透明，始终显示主域名 |
| 实现难度 | 低 | 中 |
| CF Worker 保留 | ✅ | ✅ |
| 适合场景 | 已在 CF，优先最小变动 | SEO/品牌一致性优先 |

---

### ICP 备案：最小成本路径

**触发条件**：域名解析指向中国境内服务器并开通 Web 服务时才需备案。

**最低成本方案**（¥99–120/年，仅用于解锁备案资质）：

1. 腾讯云购买最小规格国内轻量 ECS（1核1G，¥99–120/年）
2. ECS 跑 Nginx，返回一个带 ICP 备案号的简单页面（备案通过前，先用这台 ECS 作接入点）
3. 通过腾讯云 ICP 备案系统提交备案（腾讯云是接入商）
4. 备案过审后，在腾讯云 EdgeOne 添加该域名（同属腾讯云体系，无需重新换接入商）
5. DNS 切换：将大陆域名 CNAME 指向 EdgeOne 分配的地址
6. ECS 保留作合规兜底节点（实际流量全走 EdgeOne）

**ICP 备案持续合规要求**：
- 网站底部展示备案号（EdgeOne 边缘函数注入，见下方代码）
- 域名持续解析到境内 IP（不能切回境外 IP，否则接入商撤销备案）
- 网站实际内容与备案信息一致（主体、域名、内容性质）
- 公安联网备案（备案通过后 30 日内，[beian.gov.cn](https://beian.gov.cn)）

**EdgeOne 边缘函数注入 ICP 备案号**：

```javascript
new HTMLRewriter()
  .on('body', {
    element(el) {
      el.append(
        `<div style="text-align:center;font-size:12px;color:#999;padding:10px 0">
          <a href="https://beian.miit.gov.cn" target="_blank" rel="noopener">
            粤ICP备XXXXXXXX号
          </a>
        </div>`,
        { html: true }
      );
    }
  })
```

**关于在同一台 ECS 上同时运行其他服务**：

一台 ECS 可以同时作为 ICP 备案接入节点 + 运行个人自用服务（如 n8n、Docker 容器等），完全合法，不影响备案。合规边界在于：
- **不影响**：ICP 备案的合规要求只看这台 ECS 是否持续作为该域名的接入节点（即备案 IP 对应），ECS 上跑其他服务不影响
- **注意**：若其他服务也对外提供 Web 访问，那些服务对应的域名也需要完成备案，否则技术上违规
- **安全隔离**：建议 Docker 容器仅绑定 localhost，通过 SSH 隧道或内网访问，不对外暴露端口

---

### 多项目 / 多客户扩展方案

#### 方案 A：自有多个项目（推荐）

备案主域名 `example.cn` 后，旗下子域名无需重新备案（同一主体）：

```
example.cn          → 备案主体
project-a.example.cn → 直接复用，EdgeOne 独立边缘函数 → 回源 Webflow 项目 A
project-b.example.cn → 直接复用，EdgeOne 独立边缘函数 → 回源 Webflow 项目 B
```

一台 ¥99/年 ECS 覆盖所有项目。

#### 方案 B：服务客户（各自独立备案）

| 情形 | 风险 | 建议 |
|------|------|------|
| 用自己的子域名给客户 | ⚠️ 高：你是法律内容责任方 | 不建议 |
| 客户用自己的域名备案，你的 ECS IP 作接入商节点 | ✅ 合规 | 客户以自己主体申请备案 |
| 帮客户代办备案 | 需客户提供营业执照，你仅作技术方 | 明确合同责任 |

**重要**：服务方不可用自己的备案主体替客户申请，这意味着你要对客户网站的全部内容承担法律责任。

---

### 实施优先级

| 阶段 | 操作 | 成本 | 效果 |
|------|------|------|------|
| 立即（无需 ICP） | 开启 CF Argo Smart Routing | $5/月 | 边际改善，跨境路径优化 |
| 中期（需 ICP） | 购买 ECS + 申请 ICP + 接入 EdgeOne 国内节点 | ¥99/年 ECS + EdgeOne 按流量 | 质变，延迟降至 50-100ms |
| 完整方案 | 双域名 + 双 CDN + 多语言路由 + ICP 合规维持 | 同上 + 维护精力 | 最优架构 |
