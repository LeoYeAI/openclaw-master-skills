# drpy解析函数与选择器指南

## 解析函数概述

drpy的核心是四个解析函数，分别处理不同页面的内容解析：

1. **推荐** - 首页推荐内容
2. **一级** - 分类列表内容  
3. **二级** - 视频详情页面
4. **搜索** - 搜索结果页面

## 函数基本结构

### 标准异步函数格式

```javascript
// 异步函数格式（推荐）
推荐: async function () {
  let {input} = this;
  // input是homeUrl获取的页面内容
  // 返回推荐视频数组
  return [];
},

一级: async function () {
  let {input} = this;
  // input是url模板填入后的分类页面链接
  // 返回分类视频列表数组
  return [];
},

二级: async function () {
  let {input} = this;
  // input是一级返回的详情页链接
  // 返回详情对象
  return {};
},

搜索: async function () {
  let {input} = this;
  // input是searchUrl模板填入后的搜索页面链接
  // 返回搜索结果数组
  return [];
},
```

### 简写字符串格式

对于简单的选择器解析，可以使用分号分隔的字符串格式：

```javascript
一级: '.video-list li;h3&&Text;img&&data-src;.time&&Text;a&&href',
// 格式：列表选择器;标题;图片;描述;链接
```

### 字符串格式详细说明

```
推荐/一级/搜索字符串格式：
列表选择器;标题选择器;图片选择器;描述选择器;链接选择器;详情选择器(可选)

示例：
'.col-md-3;.title&&Text;img&&src;.actor&&Text;a&&href'
```

## 选择器语法

### 基础选择器

| 选择器 | 说明 | 示例 |
|--------|------|------|
| `tag.class` | 选择class为.class的tag元素 | `div.item` |
| `#id` | 选择id为#id的元素 | `#video-list` |
| `tag[attr=value]` | 选择属性匹配的元素 | `a[href*=play]` |
| `tag1 tag2` | 后代选择器 | `div.video-list li` |
| `tag1>tag2` | 子元素选择器 | `ul>li` |

### 特殊选择器

| 选择器 | 说明 | 示例 |
|--------|------|------|
| `&&` | 分隔多个选择器，依次尝试 | `img&&data-src&&src` |
| `:eq(n)` | 选择第n个元素（从0开始） | `li:eq(0)` |
| `:lt(n)` | 选择前n个元素 | `li:lt(5)` |
| `:gt(n)` | 选择第n个之后的元素 | `li:gt(2)` |
| `:contains(text)` | 包含指定文本的元素 | `span:contains("更新")` |
| `:not(selector)` | 排除匹配的元素 | `li:not(.ads)` |

### 属性提取

| 语法 | 说明 | 示例 | 获取结果 |
|------|------|------|----------|
| `tag&&Text` | 获取元素的文本内容 | `h3&&Text` | "影片标题" |
| `tag&&href` | 获取href属性 | `a&&href` | "/vod/123.html" |
| `tag&&data-src` | 获取data-src属性 | `img&&data-src` | "图片URL" |
| `tag&&src` | 获取src属性 | `img&&src` | "图片URL" |
| `tag&&html` | 获取HTML内容 | `div&&html` | "<span>内容</span>" |

## 各函数详细解析

### 推荐函数

**作用**：解析首页推荐内容

**输入**：`input`为`homeUrl`获取的HTML内容

**返回格式**：视频对象数组

```javascript
推荐: async function () {
  let html = await request(this.homeUrl);
  
  return [
    {
      vod_id: "123",           // 视频ID（可选）
      vod_name: "影片名称",     // 必需：视频名称
      vod_pic: "封面图.jpg",    // 必需：封面图URL
      vod_remarks: "更新至10集", // 可选：备注/状态
      vod_year: "2024",        // 可选：年份
      vod_area: "大陆",        // 可选：地区
      vod_actor: "演员列表",    // 可选：主演
      vod_director: "导演",    // 可选：导演
      vod_content: "剧情简介",  // 可选：简介
    },
    // ...更多视频
  ];
},
```

**字符串简写示例**：
```javascript
推荐: '.video-item;.title&&Text;img&&src;.info&&Text;a&&href',
```

### 一级函数

**作用**：解析分类列表页面

**输入**：`input`为分类URL（已替换`fyclass`、`fypage`）

**返回格式**：视频对象数组（同推荐函数）

```javascript
一级: async function () {
  let html = await request(this.input);
  
  const videos = [];
  // 使用cheerio之类的库解析html
  // 这里省略具体解析代码
  
  return videos;
},
```

**字符串简写示例**：
```javascript
一级: '.col-sm-6;h3&&Text;img&&data-src;.date&&Text;a&&href',
```

### 二级函数

**作用**：解析视频详情页，获取播放列表

**输入**：`input`为视频详情页URL

**返回格式**：详情对象

```javascript
二级: async function () {
  let html = await request(this.input);
  
  return {
    // 基本信息
    vod_name: "影片名称",
    vod_pic: "封面图.jpg",
    vod_remarks: "更新至10集",
    vod_year: "2024",
    vod_area: "大陆",
    vod_actor: "张三,李四",
    vod_director: "王五",
    vod_content: "剧情简介...",
    
    // 播放信息（关键！）
    vod_play_from: "播放来源1$$播放来源2",  // 多个来源用$$分隔
    vod_play_url: "第1集$播放地址1#第2集$播放地址2$$第1集$播放地址3#第2集$播放地址4",
    
    // 格式说明：
    // vod_play_from: "来源1$$来源2$$来源3"
    // vod_play_url: "集数1$地址1#集数2$地址2$$集数1$地址3#集数2$地址4"
    // $$分隔不同来源，#分隔同一来源的不同集数，$分隔集数和地址
  };
},
```

**特殊返回值**：
```javascript
// 无二级详情，直接跳到播放
二级: '*',

// 简写格式（同海阔dr二级）
二级: {
  title: 'h1&&Text',
  img: '.poster&&src',
  desc: '.info&&Text',
  content: '.intro&&Text',
  tabs: '.play-source&&Text',
  lists: '.play-list-item&&Text',
  tab_text: 'body&&Text',    // 选项卡文本选择器
  list_text: 'body&&Text',   // 播放列表文本选择器
  list_url: 'a&&href',        // 播放链接选择器
},
```

### 搜索函数

**作用**：解析搜索结果页面

**输入**：`input`为搜索URL（已替换`**`、`fypage`）

**返回格式**：视频对象数组（同推荐函数）

```javascript
搜索: async function () {
  return [];
},

// 简写格式
搜索: '.search-item;.title&&Text;img&&src;.info&&Text;a&&href',
```

**集成一级解析**：
```javascript
搜索: '*',  // 直接使用一级的解析逻辑
```

## 高级解析技巧

### 使用CSS选择器组合

```javascript
一级: async function () {
  let $ = cheerio.load(html);
  
  let videos = [];
  $('.video-list > li:not(.ad)').each((i, elem) => {
    videos.push({
      vod_name: $(elem).find('h3.title').text().trim(),
      vod_pic: $(elem).find('img[data-src]').attr('data-src') || $(elem).find('img').attr('src'),
      vod_remarks: $(elem).find('.update').text().trim(),
      vod_id: $(elem).find('a').attr('href').match(/\/(\d+)\.html/)[1],
    });
  });
  
  return videos;
},
```

### 多级选择器

```javascript
// 复杂的多级选择
二级: {
  title: '.video-info h1&&Text',
  img: '.poster-wrapper img&&src',
  desc: '.video-data&&Text',
  content: '.intro-content&&Text',
  tabs: 'ul.play-tab li&&Text',
  lists: '.play-list li&&Text',
  
  // 更精确的选择
  tab_text: 'ul.play-tab li a&&Text',
  list_text: '.play-list li a&&Text',
  list_url: '.play-list li a&&data-url',
},
```

### 正则表达式提取

```javascript
class_parse: '#nav li;a&&Text;a&&href;vod/(\\d+)/',

一级: async function () {
  let videos = [];
  // 使用正则提取
  let pattern = /<a href="(\/vod\/\d+\.html)" title="([^"]+)"/g;
  let match;
  
  while ((match = pattern.exec(html)) !== null) {
    videos.push({
      vod_name: match[2],
      vod_id: match[1].match(/\/(\d+)\.html/)[1],
      vod_pic: '', // 可能需要另外提取
      vod_remarks: '',
    });
  }
  
  return videos;
},
```

### 动态内容处理

```javascript
二级: async function () {
  // 处理动态加载的内容
  let html = await request(this.input);
  
  // 检查是否有AJAX加载的内容
  if (html.includes('data-player=')) {
    let playerData = html.match(/data-player="([^"]+)"/);
    if (playerData) {
      // 请求AJAX接口获取播放列表
      let playData = await request(playerData[1]);
      // 解析playData...
    }
  }
  
  return result;
},
```

## 调试技巧

### 使用log函数

```javascript
推荐: async function () {
  let html = await request(this.homeUrl);
  log('首页HTML长度:', html.length);  // 输出到日志
  log('HTML前500字符:', html.substring(0, 500));
  
  // 继续解析...
  return [];
},
```

### 分步调试

```javascript
一级: async function () {
  try {
    // 1. 获取页面
    let html = await request(this.input);
    
    // 2. 测试选择器
    let testElements = pdfh(html, '.video-item');
    log('找到元素数量:', testElements.length);
    
    // 3. 提取第一个元素测试
    if (testElements.length > 0) {
      let firstTitle = pdfh(html, '.video-item:eq(0) .title&&Text');
      log('第一个标题:', firstTitle);
    }
    
    // 4. 完整解析
    return parseVideos(html);
  } catch (error) {
    log('解析错误:', error);
    return [];
  }
},
```

### 验证返回值格式

```javascript
// 调试时验证二级返回值
二级: async function () {
  let result = await parseDetail(this.input);
  
  // 验证必要字段
  if (!result.vod_name) {
    log('警告：缺少vod_name');
  }
  if (!result.vod_play_from || !result.vod_play_url) {
    log('警告：缺少播放信息');
  }
  
  log('二级结果:', JSON.stringify(result, null, 2));
  return result;
},
```

## 常见问题解决

### Q: 选择器匹配不到内容
A: 
1. 检查是否有iframe或动态加载内容
2. 尝试更通用的选择器
3. 查看页面是否使用JavaScript渲染
4. 使用`log()`输出HTML片段检查结构

### Q: 图片获取不到
A:
1. 优先尝试`data-src`属性
2. 检查是否需要添加Referer
3. 使用`图片替换`属性处理CDN
4. 设置`图片来源`添加必要请求头

### Q: 播放列表为空
A:
1. 检查二级函数是否正确返回`vod_play_from`和`vod_play_url`
2. 验证播放地址格式是否正确（$$分隔来源，#分隔剧集）
3. 检查是否需要`play_parse`或`lazy`处理
4. 使用`sniffer`功能辅助嗅探

### Q: 编码问题导致乱码
A:
1. 设置`编码: 'gbk'`或`编码: 'gb2312'`
2. 搜索使用独立编码：`搜索编码: 'gbk'`
3. 检查response的Content-Type头