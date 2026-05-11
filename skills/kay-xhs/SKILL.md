---
name: kay-xhs
version: 1.0.3
description: |
  小红书全自动内容创作工作流 - 从爆款研究到草稿发布的完整 pipeline。
  使用场景：(1) 研究小红书爆款笔记风格和趋势，(2) 生成 AI 图片/漫画/封面，(3) 自动发布到小红书草稿箱。

  **依赖**: 需要安装 kay-image skill 并配置 KIE_API_KEY
metadata:
  openclaw:
    requires:
      skills:
        - kay-image
      env:
        - KIE_API_KEY
---

# Kay XHS - 小红书全自动创作工作流

一站式小红书内容创作解决方案，从爆款研究到草稿发布。

## ⚠️ 必需依赖

### 1. 安装 kay-image Skill（AI 生图必备）

**必须先安装，否则无法生成图片！**

```bash
# 安装 kay-image skill
clawhub install kay-image

# 配置 API Key
cp skills/kay-image/.env.example skills/kay-image/.env

# 编辑 .env 文件，填入从 https://kie.ai/ 获取的 API Key
nano skills/kay-image/.env
```

**获取 KIE API Key:**
1. 访问 https://kie.ai/
2. 注册并登录账号
3. 进入控制台 → API 管理
4. 创建 API Key 并复制

**验证安装:**
```bash
# 测试生图功能
kay-image -p "测试图片，一只可爱的猫咪" -o test.png --ar 1:1
```

### 2. 浏览器准备（自动发布用）

确保 OpenClaw 浏览器已配置，用于小红书网页操作。

---

**确认以上步骤完成后，再开始创作工作流！**

## 核心能力

1. **爆款研究** - 分析热门笔记风格、构图、文案套路
2. **AI 生图** - 生成封面、漫画、配图（支持 KIE 和 Gemini 双引擎）
3. **自动发布** - 保存到小红书草稿箱

## 完整工作流

### Phase 1: 账号准备

**工具:** `browser` (openclaw profile)

```
1. 打开浏览器访问 https://creator.xiaohongshu.com
2. 检查登录状态（如未登录需短信验证）
3. 确认当前账号名称
```

**关键检查点:**
- 账号是否登录
- 账号名称是否正确
- 网络连接正常

---

### Phase 2: 爆款研究

**工具:** `browser`

提取高点赞笔记的：
-图片
-标题
-作者
-文案
-标签

#### 方法 1: Performance API（⭐ 批量方法）

**原理**: 点击首图预览模式后，从浏览器 Performance API 获取所有已加载的网络资源，不受 DOM 移除影响。

**适用场景**: 需要采集完整图片列表，尤其是 10+ 张图片的笔记

**前提条件**: 
- ✅ **必须打开预览 modal**（点击笔记封面图）
- ✅ 等待 2-3 秒让所有资源加载完成
- ❌ 不需要切换图片（懒加载会移除旧 URL，但 Performance API 保留记录）

**代码**:
```javascript
// 打开预览 modal 后，等待 2-3 秒，然后执行
function extractImagesFromPerformance() {
  const entries = performance.getEntriesByType('resource')
    .filter(e => 
      e.name.includes('xhscdn.com') && 
      (e.name.includes('spectrum') || e.name.includes('notes_pre_post')) &&
      !e.name.includes('imageView2') // 排除缩略图
    );
  
  const urls = [...new Set(entries.map(e => e.name))];
  
  return {
    total: urls.length,
    urls: urls.map((url, i) => ({ index: i+1, url }))
  };
}

// 执行
extractImagesFromPerformance();
```

**优势**:
- ✅ 不需要切换图片，打开预览等待即可
- ✅ 获取所有历史加载记录，包括已移除的 DOM 元素
- ✅ 速度最快，单篇笔记 < 3 秒
- ✅ 可获取 20-30+ 张图片 URL（包含各种尺寸版本）

**劣势**:
- ⚠️ 可能包含重复 URL（不同尺寸版本）
- ⚠️ 需要打开预览 modal 后等待 2-3 秒让资源加载

**实际案例**:
- 笔记 8 (10 张图): 获取 27 个 URL → 筛选出 10 张正文图
- 采集时间：~3 秒
- 完整度：100%

---

#### 方法 2: DOM 全量提取（⭐ 批量方法）

**原理**: 打开预览模式后，提取页面所有 `<img>` 标签，包括头像、评论图等，然后过滤出正文图片。

**适用场景**: Performance API 无效时，或需要快速获取少量图片

**前提条件**: 
- ✅ **必须打开预览 modal**（点击笔记封面图）
- ✅ 等待页面完全加载
- ⚠️ 懒加载图片可能未出现在 DOM 中（需要切换或等预加载）

**代码**:
```javascript
// 打开预览 modal 后执行
function extractImagesFromDOM() {
  const allImgs = document.querySelectorAll('img');
  const urls = [];
  
  allImgs.forEach(img => {
    if (img.src && img.src.includes('xhscdn.com') && img.src.length > 50) {
      const cleanUrl = img.src.split('?')[0]; // 移除查询参数
      if (!urls.includes(cleanUrl)) {
        urls.push(cleanUrl);
      }
    }
  });
  
  // 过滤出正文图片（排除头像、图标等）
  const contentImages = urls.filter(url => 
    url.includes('spectrum') || url.includes('notes_pre_post')
  );
  
  return {
    total: contentImages.length,
    urls: contentImages.map((url, i) => ({ index: i+1, url }))
  };
}

// 执行
extractImagesFromDOM();
```

**优势**:
- ✅ 简单直接，不需要切换图片
- ✅ 可获取 50+ 个图片资源（包含头像、评论图等）
- ✅ 过滤后得到完整正文图片列表

**劣势**:
- ⚠️ 可能包含非正文图片（需要过滤）
- ⚠️ 懒加载图片可能未出现在 DOM 中（小红书会预加载部分图片）

**实际案例**:
- 笔记 9 (5 张图): 获取 52 个 URL → 筛选出 5 张正文图
- 采集时间：~2 秒
- 完整度：100%

---

#### 方法 3: 循环点击切换（保底方法）

**原理**: 手动切换每张图片，强制触发懒加载，确保所有图片 URL 加载到 DOM。

**适用场景**: 批量方法失效时，或需要确保 100% 完整度

**完整操作步骤**:
```
1. 访问搜索页：https://www.xiaohongshu.com/search_result?keyword=关键词&type=51
2. 等待笔记列表加载完成
3. 点击目标笔记的【首图/封面图】（不是标题文字）
   - 这会打开预览 modal，显示笔记完整内容
   - 无需进入详情页，避免反爬虫限制
4. 【关键步骤】循环切换所有图片：
   - 读取图片计数（如 1/13 = 共 13 张）
   - 点击"下一张"按钮 (右侧箭头) 12 次
   - 每次切换后等待 1-2 秒让图片加载
   - 确保所有图片都加载到 DOM 中
5. 提取数据：
   - 使用 JavaScript 提取所有图片 URL
   - 记录文案、标签、点赞/收藏/评论数
   - 采集前 5 条评论
6. 点击 X 或外部区域关闭 preview modal
7. 返回搜索列表，继续下一篇笔记
```

**⚠️ 错误示范（会失败）**:
```javascript
// ❌ 错误：打开 modal 后直接提取，只能拿到 1-3 张
click(firstImage);
extractImages(); // 只返回 3 张！
```

**✅ 正确示范（完整采集）**:
```javascript
// ✅ 正确：循环切换后再提取
click(firstImage); // 打开 modal
for (let i = 0; i < totalImages - 1; i++) {
  click(nextButton); // 点击"下一张"
  await sleep(1500); // 等待加载
}
// 现在所有图片 URL 都加载到 DOM 了
extractImages(); // 返回完整 13 张！
```

**提取图片 URL 的完整代码**:
```javascript
// 在 preview modal 中执行
const extractNoteData = () => {
  // 1. 提取所有图片 URL
  const images = document.querySelectorAll('.swiper-slide img, .note-detail img');
  const imageUrls = Array.from(images).map((img, index) => ({
    index: index + 1,
    url: img.src || img.getAttribute('src')
  })).filter(item => item.url);
  
  // 2. 提取基础信息
  const title = document.querySelector('[class*="title"]')?.textContent?.trim();
  const author = document.querySelector('[class*="author"]')?.textContent?.trim();
  const likes = document.querySelector('[class*="like"]')?.textContent?.trim();
  
  // 3. 提取评论
  const comments = [];
  const commentElements = document.querySelectorAll('[class*="comment"]');
  commentElements.forEach((el, index) => {
    if (index >= 5) return;
    const userEl = el.querySelector('a');
    const contentEl = el.querySelector('p, [class*="content"]');
    if (userEl && contentEl) {
      comments.push({
        user: userEl.textContent?.trim(),
        content: contentEl.textContent?.trim()
      });
    }
  });
  
  return {
    totalImages: imageUrls.length,
    images: imageUrls,
    title,
    author,
    likes,
    comments
  };
};

// 执行提取
extractNoteData();
```

**循环切换图片的完整代码**:
```javascript
// 在 preview modal 中循环切换所有图片
const cycleThroughImages = async (totalImages) => {
  const nextButton = document.querySelector('.swiper-button-next, [class*="next"], [aria-label="下一张"]');
  
  for (let i = 1; i < totalImages; i++) {
    if (nextButton) {
      nextButton.click();
      await new Promise(resolve => setTimeout(resolve, 1500)); // 等待 1.5 秒
    }
  }
  
  console.log(`✅ 已切换 ${totalImages} 张图片，现在可以提取完整 URL 列表`);
};

// 使用示例：
// cycleThroughImages(13).then(() => extractNoteData());
```

**实际采集案例**:
- 笔记："我想拉屎" (2.5 万赞)
- 成功提取：13 张图片 URL
- 数据完整度：100%
- 图片 URL 格式：`https://sns-webpic-qc.xhscdn.com/.../notes_pre_post/...`

**性能参考**:
- 打开搜索页：~2-3 秒
- 点击首图打开 modal: ~1-2 秒
- 浏览全部图片 (13 张): ~10-15 秒
- 提取数据：~1 秒
- 单篇笔记总时间：~15-20 秒

**批量采集策略**:
```
对于 10 篇笔记的批量采集:
1. 搜索关键词，获取结果列表
2. 筛选点赞 1000+ 的笔记
3. 逐一点击首图进入 preview modal
4. 浏览所有图片并提取 URL
5. 关闭 modal，继续下一篇
6. 预计总时间：3-5 分钟
```

**注意事项**:
- ✅ 点击的是【图片】不是【标题文字】
- ✅ **必须循环切换所有图片**才能提取完整 URL 列表（懒加载！）
- ✅ Preview modal 中可以看到图片计数 (如 1/13)
- ✅ 建议间隔 2-3 秒再点击下一篇，模拟正常用户行为
- ⚠️ 不要直接访问笔记详情页（会 404）


**研究维度:**
| 维度 | 分析内容 |
|------|---------|
| 视觉风格 | 色彩、构图、人物/场景类型 |
| 文案结构 | 标题公式、正文套路、互动引导 |
| 话题标签 | 高频标签、组合策略 |
| 发布时间 | 最佳发布时段 |

---

### Phase 3: 内容策划

基于爆款研究，确定：

1. **内容类型**
   - 图文笔记
   - AI 漫画（四格/条漫）
   - 教程分享
   - 情感故事

2. **风格定位**
   - 治愈系
   - 搞笑/吐槽
   - 知识科普
   - 生活美学

3. **图片规划**
   - 数量（1-4 张）
   - 尺寸（3:4 竖版优先）
   - 风格统一性

---

### Phase 4: AI 生图

**工具:** `kay-image` (KIE API)

#### 生图引擎

| 引擎 | 工具 | 配置要求 | 适用场景 |
|------|------|----------|----------|
| **KIE** | `kay-image` | `KIE_API_KEY` | 高质量 4K 输出，角色一致性 |

**配置检查:**
```bash
# 确保已设置 KIE_API_KEY
export KIE_API_KEY="your-api-key"

# 测试生图
kay-image -p "一只可爱的橘猫在草地上玩耍" -o test.png --ar 1:1
```

#### 4.1 封面生成
```bash
kay-image \
  --prompt "描述..." \
  --output cover.jpg \
  --ar 3:4 \
  --resolution 2K
```

#### 4.2 四格漫画生成（关键！）
**必须一次生成，不要分格生成！**

```bash
kay-image \
  --prompt "四格漫画，2x2 网格布局：
第一格（左上）：...，画面下方文字'...'
第二格（右上）：...，画面下方文字'...'
第三格（左下）：...，画面下方文字'...'
第四格（右下）：...，画面下方文字'...'
确保角色形象一致，色调从冷到暖渐变" \
  --output comic_4panel.jpg \
  --ar 3:4 \
  --resolution 2K
```

#### 4.3 图生图（风格迁移）

```bash
kay-image \
  --prompt "转换成...风格" \
  --input /path/to/reference.jpg \
  --output result.jpg
```

#### 4.4 批量生图模式（推荐 ⭐）

**场景**: 需要生成多张图片（如 4 张 2 格漫画）

**优势**:
- ✅ **批量提交**: 一次性提交所有任务
- ✅ **统一轮询**: 每 20 秒检查所有任务状态
- ✅ **并行下载**: 所有完成后同时下载
- ✅ **效率提升**: 4 张图从 8 分钟 → 3 分钟

**使用方法**:

```bash
# 1. 创建批量任务配置文件
cat > comic-tasks.json << 'EOF'
[
  {
    "prompt": "唯美治愈系手绘，2格漫画第一格：女孩独自思考...",
    "output": "comic-01.png",
    "ar": "3:4",
    "resolution": "2K"
  },
  {
    "prompt": "唯美治愈系手绘，2格漫画第二格：女孩自我怀疑...",
    "output": "comic-02.png",
    "ar": "3:4",
    "resolution": "2K"
  },
  {
    "prompt": "唯美治愈系手绘，2格漫画第三格：两人对话领悟...",
    "output": "comic-03.png",
    "ar": "3:4",
    "resolution": "2K"
  },
  {
    "prompt": "唯美治愈系手绘，2格漫画第四格：两人依偎温暖...",
    "output": "comic-04.png",
    "ar": "3:4",
    "resolution": "2K"
  }
]
EOF

# 2. 执行批量生成
kay-image-batch -b comic-tasks.json -o ./xhs-images/2026-03-20-治愈漫画
```

**批量模式参数**:
- `--poll-interval 20`: 轮询间隔 20 秒（默认）
- `--max-attempts 10`: 最多轮询 10 次（默认）
- `--concurrent 4`: 并发下载数（默认）

**执行流程**:
```
1. 批量提交所有任务（不等待）
   [1/4] ✅ TaskId: xxx
   [2/4] ✅ TaskId: yyy
   [3/4] ✅ TaskId: zzz
   [4/4] ✅ TaskId: www

2. 统一轮询（每 20s 检查一次，最多 10 次）
   第 1/10 次... 4 等待中
   第 2/10 次... 2 完成, 2 等待中
   第 3/10 次... 4 完成 ✅

3. 并行下载所有图片
   [1/4] ✅ comic-01.png
   [2/4] ✅ comic-02.png
   [3/4] ✅ comic-03.png
   [4/4] ✅ comic-04.png
```

**生图原则:**
- ✅ 四格漫画 = 一次生成完整布局
- ✅ 明确角色特征确保一致性
- ✅ 色调随情绪变化
- ❌ 不要分开生成单格再拼接
- ✅ **多张图时优先使用批量模式**

---

### 生图引擎

| 特性 | KIE (`kay-image`) |
|------|-------------------|
| **配置难度** | ⭐ 需 API Key |
| **图片质量** | ⭐⭐⭐ 4K 高清 |
| **生成速度** | ⭐⭐ 中等 |
| **角色一致性** | ⭐⭐⭐ 优秀 |
| **批量生成** | ✅ 支持 (`kay-image-batch`) |
| **图生图** | ✅ 支持 |

**配置检查清单:**
```markdown
- [ ] 已设置 `KIE_API_KEY`
- [ ] 已安装 `kay-image` skill
```

---

### Phase 5: 文案创作

**结构模板:**

```markdown
## 标题（20 字以内）
[emoji] 核心卖点｜价值点｜互动引导

示例：
🌱打工人的治愈时刻｜AI 四格漫画

## 正文
[钩子] 一句话吸引注意

[内容] 主体内容（故事/教程/分享）

[互动] 引导评论/点赞/收藏
你最近...？评论区告诉我👇

## 话题标签（5-8 个）
#主话题 #细分话题 #情绪标签 #平台标签
```

---

### Phase 6: 自动发布

**工具:** `browser` (xhs-browser-ops)

#### 6.1 发布流程（browser 工具自动化）

**完整操作步骤**:

```bash
# Step 1: 打开发布页面
browser open --url "https://creator.xiaohongshu.com/publish/publish?from=menu&target=image"

# Step 2: 批量上传图片（支持多文件同时上传）
browser upload --targetId "页面targetId" \
  --paths "/tmp/openclaw/uploads/comic-01.png" \
          "/tmp/openclaw/uploads/comic-02.png" \
          "/tmp/openclaw/uploads/comic-03.png" \
          "/tmp/openclaw/uploads/comic-04.png"

# Step 3: 获取页面 snapshot，查看元素 ref
browser snapshot --targetId "页面targetId" --timeMs 2000

# Step 4: 填写标题（通过 ref 定位输入框）
browser type --targetId "页面targetId" \
  --ref "标题textbox的ref" \
  --text "原来最好的爱情，是陪你从心动到心安"

# Step 5: 填写正文
browser type --targetId "页面targetId" \
  --ref "正文textbox的ref" \
  --text "第1格｜一眼心动 💫\n那个安静的午后..."

# Step 6: 保存到草稿（点击"暂存离开"按钮）
browser click --targetId "页面targetId" \
  --ref "暂存离开按钮的ref"
```

**关键概念**:
- **targetId**: 浏览器页面的唯一标识（通过 browser open 或 browser tabs 获取）
- **ref**: 页面元素的引用标识（通过 browser snapshot 获取，如 `e207`, `e216`）
- **browser upload**: 批量上传文件到文件选择框
- **browser type**: 在文本输入框中填写内容
- **browser click**: 点击按钮或元素
- **browser act**: 执行复合操作（包含 click/type/press 等）

#### 6.2 按钮位置（关键！）

在发布页面底部右侧：
```
[ 暂存离开 ] [ 发布 ]
   ↑ 左         ↑ 右
```

- **暂存离开**: 保存到草稿箱，不发布
- **发布**: 立即发布笔记（需要用户明确确认）

#### 6.3 用户指令对应操作

| 用户指令 | 操作 | 是否需要确认 |
|---------|------|------------|
| "保存到草稿" / "存草稿" / "暂存" | 点击"暂存离开" | ❌ 直接执行 |
| "发布" / "立即发布" / "确认发布" | 点击"发布"按钮 | ✅ 需二次确认 |
| "你看着办" / "随便" | 默认保存草稿 | ❌ 直接执行 |

**⚠️ 重要**: 用户明确说"保存草稿"时，**不要问"要不要发布"**，直接执行保存！

#### 6.4 关键操作详解

**获取 targetId**:
```bash
# 方法1: open 命令返回 targetId
browser open --url "https://..."
# 返回: {"targetId": "ABC123...", ...}

# 方法2: 查看所有 tabs
browser tabs
# 返回所有打开的页面及其 targetId
```

**获取元素 ref**:
```bash
# 获取页面 snapshot，查看所有可交互元素及其 ref
browser snapshot --targetId "ABC123..." --timeMs 2000

# 在返回结果中查找：
# - textbox "填写标题会有更多赞哦" [ref=e207]
# - textbox [ref=e216] （正文输入框）
# - button "暂存离开" [ref=e530]
# - button "发布" [ref=e533]
```

**完整发布代码示例**:
```bash
#!/bin/bash

# 1. 打开发布页面
TARGET=$(browser open --url "https://creator.xiaohongshu.com/publish/publish?from=menu&target=image" | jq -r '.targetId')

# 2. 上传4张图片
browser upload --targetId "$TARGET" \
  --paths "/tmp/comic-01.png" "/tmp/comic-02.png" "/tmp/comic-03.png" "/tmp/comic-04.png"

# 3. 等待上传完成，获取 snapshot
sleep 3
browser snapshot --targetId "$TARGET" --timeMs 2000

# 4. 填写标题（假设 ref=e207）
browser type --targetId "$TARGET" --ref "e207" \
  --text "原来最好的爱情，是陪你从心动到心安"

# 5. 填写正文（假设 ref=e216）
browser type --targetId "$TARGET" --ref "e216" \
  --text "第1格｜一眼心动 💫\n..."

# 6. 保存到草稿（假设 ref=e530）
browser click --targetId "$TARGET" --ref "e530"

echo "✅ 已保存到草稿箱"
```

**常用操作速查**:
| 操作 | 命令 | 示例 |
|------|------|------|
| 打开页面 | `browser open --url "URL"` | 获取 targetId |
| 查看 tabs | `browser tabs` | 列出所有页面 |
| 切换 tab | `browser focus --targetId "ID"` | 切换到指定页面 |
| 上传文件 | `browser upload --paths "file1" "file2"` | 批量上传 |
| 填写文本 | `browser type --ref "e207" --text "内容"` | 在输入框填入文字 |
| 点击按钮 | `browser click --ref "e530"` | 点击指定元素 |
| 获取页面 | `browser snapshot --timeMs 2000` | 查看元素和 ref |
| 复合操作 | `browser act --request '{...}'` | 执行 click/type/press 组合 |

#### 6.5 常见错误

| 错误 | 后果 | 正确做法 |
|------|------|---------|
| **不熟悉 browser 工具** | **不会自动化发布** | **学习 upload/type/click/snapshot 基本用法** |
| 不知道用 `browser upload` | 无法批量上传图片 | 使用 `browser upload --paths file1 file2 ...` |
| 不知道如何定位元素 | 无法填写标题/正文 | 先用 `snapshot` 获取 ref，再用 `type/click` |
| 不知道 targetId 的作用 | 操作失败或错乱 | 每次操作都传入正确的 targetId |
| 用户说"存草稿"却问"要不要发布" | 用户困惑，流程拖沓 | 听清指令，直接执行 |
| 频繁切换tab | 页面状态丢失 | 保持焦点，一次完成 |
| 点击"发布"代替"暂存离开" | 笔记直接发布 | 确认按钮位置，左草稿右发布 |

#### 6.6 学习路径

**新手必学（按顺序）**:
1. **browser open** - 打开页面，获取 targetId
2. **browser tabs** - 查看所有打开的页面
3. **browser snapshot** - 获取页面元素和 ref
4. **browser upload** - 批量上传文件
5. **browser type** - 在输入框填写文本
6. **browser click** - 点击按钮
7. **browser act** - 执行复合操作

**练习任务**:
```markdown
- [ ] 打开小红书创作平台，获取 targetId
- [ ] 使用 snapshot 查看页面元素
- [ ] 找到"上传图片"按钮的 ref
- [ ] 使用 upload 上传一张测试图片
- [ ] 找到标题输入框的 ref，使用 type 填写标题
- [ ] 找到"暂存离开"按钮的 ref，使用 click 点击
```

---

## 工具链整合

| 阶段 | 主要工具 | 辅助工具 |
|------|---------|---------|
| 账号准备 | browser | - |
| 爆款研究 | browser, xiaohongshu-deep-research | web_search |
| 内容策划 | - | memory_search |
| AI 生图 | **kay-image-batch** (批量) | image (分析) |
| AI 生图 | kay-image (单张，高质量) | - |
| 文案创作 | - | memory_get |
| 自动发布 | browser | - |

---

## 最佳实践

### AI 漫画创作
1. **角色一致性** - 每个prompt有一致的详细人物特征描述
2. **图上文字** - 每格配简短文案
3. **批量生成** - 多张图时使用 `kay-image-batch`（轮询 20s/次，最多 10 次）

### 封面设计
1. **3 秒法则** - 一眼抓住注意力
2. **情绪钩子** - 痛点/冲突/好奇
3. **高对比** - 色彩/场景对比
4. **真实感** - 像个人分享

### 文案套路
1. **标题** - emoji+ 卖点 + 互动引导
2. **正文** - 钩子 + 内容 + 互动
3. **标签** - 精准 + 热门组合

---

## 错误避免

| 错误 | 后果 | 正确做法 |
|------|------|---------|
| 分开生成漫画格 | 角色不一致 | 一次生成完整 4 格 |
| 忽略爆款研究 | 风格不对标 | 先研究再创作 |
| 文案过长 | 阅读率低 | 简洁有力 |
| 标签太少 | 曝光不足 | 5-8 个精准标签 |
| **打开 modal 直接提取** | **只能采集 1-3 张** | **优先用 Performance API 或 DOM 全量提取** |
| **不用批量方法** | **效率低** | **优先批量方法，不行再循环点击** |
| **串行生成多张图** | **耗时 8 分钟+** | **使用 kay-image-batch 批量模式（3 分钟）** |
| **误解漫画结构** | **把1组多图当多组单图** | **先查看图片，理解故事线再规划** |
| **发布流程混乱** | **用户要草稿却问是否发布** | **听清指令，直接执行** |
| **未配置生图引擎** | **无法生成图片** | **提前配置 KIE_API_KEY** |

---

## 采集方法对比总结

| 方法 | 速度 | 完整度 | 推荐度 | 适用场景 |
|------|------|--------|--------|---------|
| **Performance API** | ⚡⚡⚡ 最快 (~3 秒) | ✅✅✅ 100% | ⭐⭐⭐ 首选 | 10+ 张大图笔记 |
| **DOM 全量提取** | ⚡⚡ 快 (~2 秒) | ✅✅✅ 100% | ⭐⭐⭐ 首选 | 5-10 张图笔记 |
| **循环点击切换** | 🐌 慢 (~15 秒/篇) | ✅✅✅ 100% | ⭐ 保底 | 批量方法失效时 |

**决策流程**:
```
1. 搜索关键词，打开搜索页
2. 点击笔记【封面图】打开预览 modal（必须！）
3. 等待 2-3 秒让资源加载
4. 尝试 Performance API → 成功？完成 ✅
5. 失败？尝试 DOM 全量提取 → 成功？完成 ✅
6. 还不行？循环点击切换所有图片 → 完成 ✅
```

**关键提醒**:
- ⚠️ **所有方法都需要打开预览 modal** - 不打开无法获取任何图片 URL
- ⚠️ **批量方法不需要切换图片** - 打开等待即可，切换反而可能触发懒加载移除
- ⚠️ **循环点击是保底方案** - 仅当批量方法失效时使用

---

## 漫画结构理解（关键！）

### 常见漫画类型

| 类型 | 结构 | 发布方式 | 示例 |
|------|------|---------|------|
| **四格漫画** | 1张图 = 4格分镜 | 1篇笔记，1张图 | 传统四格，2x2布局 |
| **2格漫画** | 1张图 = 2格分镜 | 1篇笔记，1张图 | 上下/左右分镜 |
| **多图连载** | 多张图，每张2-4格 | 1篇笔记，多张图 | 完整故事分多张呈现 |
| **单图插画** | 1张图 = 1个画面 | 1篇笔记，1张图 | 封面、海报 |

### 关键判断原则

**当用户说"这4张图是放到同一个漫画里"时：**

1. ✅ **立即查看所有图片** - 不要假设，先看内容
2. ✅ **理解每张图的结构** - 是2格？4格？单图？
3. ✅ **理清故事线** - 4张图是否讲述同一个故事？
4. ✅ **确认发布方式** - 1篇笔记含多张图，还是多篇笔记？

### 错误案例分析

**❌ 错误理解：**
```
用户：这4张图是放到同一个漫画里
我（错误）：以为是4组独立漫画，准备发4条笔记
```

**✅ 正确理解：**
```
用户：这4张图是放到同一个漫画里
我（正确）：查看4张图，每张是2格分镜，共8个画面
      图1: 一眼心动（女孩看书→男孩出现）
      图2: 暧昧升温（秋天散步→眼神交汇）
      图3: 低谷陪伴（女孩伤心→男孩递热饮）
      图4: 修成正果（夕阳牵手→樱花树下笑）
      → 这是1篇笔记，4张图，讲述完整爱情故事
```

### 发布前检查清单

```markdown
- [ ] 已查看所有图片内容
- [ ] 已理解每张图的分镜结构（2格/4格/单图）
- [ ] 已理清图片间的逻辑关系（连续故事/独立场景）
- [ ] 已确认发布方式（1篇多图 / 多篇单图）
- [ ] 已撰写配合图片的文案
- [ ] 已确认用户意图（发布/草稿/定时）
```

---

.openclaw/workspace-xhs-manager/memory/prompts_warehouse --优秀prompt仓库

---

## 记忆归档

每次创作后更新：
1. `memory/daily/YYYY-MM-DD.md` - 当日工作日志
2. `memory/lessons/xhs-*.md` - 经验教训
3. `memory/xhs-manage-master.md` - 核心知识库
