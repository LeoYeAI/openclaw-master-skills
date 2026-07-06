# drpy源问题排查指南

## 诊断流程

### 快速诊断流程图

```
开始
  ↓
检查host和网络连接 → 失败 → 修复网络/域名
  ↓ 成功
检查首页访问 → 失败 → 检查headers/UA
  ↓ 成功  
检查分类获取 → 失败 → 调试class_parse
  ↓ 成功
检查一级列表 → 失败 → 调试选择器
  ↓ 成功
检查二级详情 → 失败 → 查看页面结构
  ↓ 成功
检查播放功能 → 失败 → 检查lazy/sniffer
  ↓ 成功
源正常工作 ✓
```

## 常见问题分类

### 连接与网络问题

#### 1. 访问超时 (timeout)

**症状**：源加载失败，提示超时或网络错误

**可能原因**：
- `host`配置错误
- 网站服务器响应慢
msg- `timeout`设置太短
- 网络防火墙/代理限制

**解决方案**：
```javascript
// 增加超时时间
timeout: 10000,  // 默认3000，建议5000-10000

// 检查host格式
host: 'https://www.example.com',  // 必须有协议头

// 设置更宽容的headers
headers: {
  'User-Agent': 'Mozilla/5.0 ...',  // 使用完整UA
  'Accept-Encoding': 'gzip, deflate',
},
```

#### 2. 403/404错误

**症状**：返回HTTP错误状态码

**可能原因**：
- 网站反爬虫
- 需要特定Referer
- 路径错误

**解决方案**：
```javascript
headers: {
  'User-Agent': 'MOBILE_UA',
  'Referer': 'https://www.example.com/',  // 添加Referer
  'Cookie': '关键cookie值',  // 可能需要cookie
},

// 或者使用PC_UA
headers: {
  'User-Agent': 'PC_UA',
},
```

### 解析与选择器问题

#### 3. 分类获取失败

**症状**：分类列表为空或显示"获取失败"

**可能原因**：
- `class_parse`选择器错误
- 网站分类结构变化
- 正则表达式错误

**调试步骤**：
```javascript
// 临时添加调试代码
预处理: `js:
  let html = request(HOST + homeUrl);
  log('首页HTML长度:', html.length);
  log('分类区域HTML:', pdfh(html, '选择器'));
  // 测试选择器
  let test = pdfh(html, '.navbar li&&Text');
  log('测试选择器结果:', test);
`,
```

**解决方案**：
```javascript
// 更新class_parse选择器
class_parse: '.new-nav li;a&&Text;a&&href;/(\\d+)/',

// 或者使用更通用的选择器
class_parse: 'li:has(a);a&&Text;a&&href;.*/(.*?)/',
```

#### 4. 一级列表为空

**症状**：分类下有分类但不能显示视频列表

**可能原因**：
- 一级选择器错误
- 页面为AJAX动态加载
- URL模板错误

**调试方法**：
```javascript
// 在函数中添加调试
一级: async function () {
  log('一级URL:', this.input);  // 查看实际请求的URL
  
  let html = await request(this.input);
  log('页面长度:', html.length);
  log('前1000字符:', html.substring(0, 1000));
  
  // 测试选择器
  let test = pdfh(html, '.video-item&&Text');
  log('选择器测试:', test);
  
  return [];
},
```

**解决方案**：
```javascript
// 更新选择器
一级: '.new-video-list .item;.title&&Text;img&&data-src;.info&&Text;a&&href',

// 或者使用异步函数处理动态内容
一级: async function () {
  let html = await request(this.input);
  // 可能需要处理JavaScript渲染的内容
  if (html.includes('window.__DATA__')) {
    // 提取JSON数据
    let jsonData = html.match(/window\.__DATA__ = (\{.*?\});/s)[1];
    return parseJSONData(jsonData);
  }
  return parseNormalHTML(html);
},
```

#### 5. 二级详情错误

**症状**：无法进入详情页或详情页信息不完整

**可能原因**：
- 详情页链接错误
- 选择器不匹配
- 播放信息提取失败

**调试代码**：
```javascript
二级: async function () {
  log('二级URL:', this.input);
  
  let html = await request(this.input);
  log('详情页长度:', html.length);
  
  // 测试各种选择器
  let title = pdfh(html, 'h1&&Text');
  log('标题:', title);
  
  let playTabs = pdfh(html, '.play-source&&Text');
  log('播放选项卡:', playTabs);
  
  let playList = pdfh(html, '.play-list&&html');
  log('播放列表HTML:', playList);
  
  return {
    vod_name: title,
    vod_play_from: playTabs || '默认',
    vod_play_url: '#',
  };
},
```

### 播放相关问题

#### 6. 无法播放视频

**症状**：点击播放按钮无效或提示"解析失败"

**可能原因**：
- 播放地址提取错误
- 需要免嗅解析
- 视频地址失效

**检查清单**：
1. **检查play_parse设置**：
```javascript
play_parse: true,  // 必须为true
```

2. **检查lazy函数**：
```javascript
lazy: async function () {
  let {input} = this;
  log('lazy输入:', input);
  
  // 如果input是m3u8等可直接播放的地址
  if (/\.m3u8|\.mp4/.test(input)) {
    return {
      url: input,
      parse: 0,  // 0表示直接播放
    };
  }
  
  // 需要进一步解析
  let playUrl = await extractRealUrl(input);
  return {
    url: playUrl,
    parse: 0,
  };
},
```

3. **启用辅助嗅探**：
```javascript
sniffer: 1,
isVideo: "http((?!http).){26,}\\.(m3u8|mp4|flv|avi|mkv|wmv|mpg|mpeg|mov|ts|3gp|rm|rmvb|asf|m4a|mp3|wma)",
```

#### 7. 播放卡顿或缓冲

**可能原因**：
- 视频源服务器限速
- 线路拥挤
- 需要代理

**解决方案**：
```javascript
// 使用本地代理优化
proxy_rule: `js:
  if(input.includes('.m3u8')) {
    // 处理m3u8文件，例如去除广告片段
    let content = request(input);
    let cleaned = content.replace(/#EXTINF.*?\\n.*?ad.*?\\n/g, '');
    input = [200, 'application/vnd.apple.mpegurl', cleaned];
  }
`,
```

### 特定类型源问题

#### 8. 漫画源显示问题

**症状**：漫画图片无法加载或显示异常

**解决方案**：
```javascript
// 漫画源lazy必须返回pics://协议
lazy: async function () {
  let images = await extractImageUrls(this.input);
  return `pics://${images.join(',')}`;
},

// 图片可能需要特殊处理
图片替换: 'https://old-cdn.com/=>https://new-cdn.com/',
图片来源: '@Referer=https://comic.site.com/',
```

#### 9. 小说源格式错误

**症状**：小说内容显示乱码或无法阅读

**解决方案**：
```javascript
// 小说源lazy必须返回novel://协议
lazy: async function () {
  let content = await extractNovelContent(this.input);
  return `novel://${JSON.stringify({
    title: "章节标题",
    content: content,
  })}`;
},

// 确保编码正确
编码: 'utf-8',
```

### 性能与缓存问题

#### 10. 加载缓慢

**症状**：源响应慢，影响使用体验

**优化建议**：
```javascript
// 1. 适当减少请求数据
limit: 20,  // 减少首页推荐数量

// 2. 使用缓存
预处理: `js:
  // 缓存分类数据
  if(!global._categoryCache) {
    global._categoryCache = {};
  }
  let cacheKey = HOST + '分类';
  if(global._categoryCache[cacheKey]) {
    return global._categoryCache[cacheKey];
  }
  // ...获取分类
  global._categoryCache[cacheKey] = result;
  return result;
`,

// 3. 优化选择器（避免过于复杂）
一级: '.video-item;h3&&Text;img&&src',  // 简化选择器
```

#### 11. 修改不生效

**症状**：修改JS文件后配置未更新

**原因**：drpy有配置缓存机制

**解决方案**：
1. **猫影视/TVBox**：进入设置 → 换源 → 重新选择源
2. **海阔视界**：长按源 → 更新配置
3. **重启播放器**：完全退出后重新启动
4. **清空缓存**：设置中清空播放器缓存

### 高级调试技巧

#### 12. 日志分析

启用详细日志：
```javascript
预处理: `js:
  // 记录所有请求
  let originalRequest = request;
  request = function(url, options) {
    log('请求URL:', url);
    log('请求选项:', options);
    try {
      let result = originalRequest(url, options);
      log('响应长度:', result.length);
      return result;
    } catch (error) {
      log('请求错误:', error);
      throw error;
    }
  };
`,
```

#### 13. 模拟请求测试

使用外部工具测试选择器：
1. **浏览器开发者工具**：
   - 打开目标网站
   - 在Console测试$('选择器')
   - 验证选择器是否正确

2. **在线测试工具**：
   - 使用正则表达式测试工具
   - 验证class_parse中的正则

3. **编写测试脚本**：
```javascript
// 独立的测试脚本
let testHtml = `获取的HTML内容`;
let title = pdfh(testHtml, '.video-title&&Text');
console.log('提取的标题:', title);
```

## 紧急修复模板

### 分类获取紧急修复

```javascript
// 当class_parse失效时，临时使用静态分类
class_name: '电影&电视剧&动漫&综艺',
class_url: '1&2&3&4',

// 并尝试获取动态分类（备用）
class_parse: `js:
  let html = request(HOST + homeUrl);
  // 尝试多种选择器
  let selectors = [
    '.navbar li a',
    '.menu li a',
    'ul.nav li a',
    '#nav li a'
  ];
  
  for(let selector of selectors) {
    let result = pdfh(html, selector + '&&Text');
    if(result && result.length > 0) {
      log('找到选择器:', selector);
      // 返回处理后的分类
      return result;
    }
  }
  log('警告：未找到分类选择器');
  return '';  // 返回空，使用静态分类
`,
```

## 实战案例：选择器不匹配修复

### 问题描述
参考代码使用 `.remarks&&Text` 获取状态，但实际HTML中class为 `.hl-pic-text span`。

### 修复过程

**第一步：确认问题**
```python
import requests
from bs4 import BeautifulSoup

html = requests.get('https://www.pitv.cc/').text
soup = BeautifulSoup(html, 'html.parser')

# 检查.remarks是否存在
print('remarks:', bool(soup.find(class_='remarks')))  # False

# 查找实际的class
for elem in soup.find_all(class_=True):
    if elem.get('class') and 'pic' in str(elem.get('class')):
        print(elem.name, elem.get('class'))
        # 输出: div ['hl-pic-text']
```

**第二步：修正选择器**
```javascript
// 错误
推荐: '.hl-vod-list;li;a&&title;a&&data-original;.remarks&&Text;a&&href',

// 正确
推荐: '.hl-vod-list;li;a&&title;a&&data-original;.hl-pic-text span&&Text;a&&href',
```

**第三步：验证修复**
- 重新加载源
- 检查首页是否显示状态
- 检查分类列表是否正常

### 经验总结
1. **不要盲信参考代码** - 每个网站的HTML结构不同
2. **必须实际验证** - 用Python获取HTML确认选择器存在
3. **注意class变化** - 网站改版可能导致class名变化
4. **使用模糊匹配** - 如 `img&&data-original||img&&src` 提高兼容性

### 播放紧急修复

```javascript
// 当原有播放解析失效时
lazy: async function () {
  let {input} = this;
  
  // 尝试多种方式获取播放地址
  let playUrl = input;
  
  // 方法1：直接使用输入
  if (/\.(m3u8|mp4)/.test(input)) {
    playUrl = input;
  }
  
  // 方法2：从页面重新提取
  else {
    let html = await request(input);
    let patterns = [
      /"url":"([^"]+\.m3u8[^"]*)"/,
      /src="([^"]+\.mp4[^"]*)"/,
      /file:"([^"]+)"/,
    ];
    
    for(let pattern of patterns) {
      let match = html.match(pattern);
      if(match && match[1]) {
        playUrl = match[1];
        break;
      }
    }
  }
  
  return {
    url: playUrl,
    parse: 0,
  };
},
```

## 预防性维护建议

### 定期检查
1. **每月检查**：主要源的功能是否正常
2. **选择器备份**：记录多个备选选择器
3. **模板更新**：关注drpy框架更新，及时适配新模板

### 代码管理
1. **版本控制**：使用Git管理源文件
2. **注释说明**：关键代码添加详细注释
3. **测试用例**：为复杂源编写测试代码

### 用户反馈
1. **错误收集**：记录用户报告的播放问题
2. **解决方案库**：建立常见问题的解决方案
3. **更新通知**：重大修复及时通知用户

## 获取帮助

### 社区资源
1. **官方文档**：查看最新drpy文档
2. **GitHub仓库**：提交issue和查看解决方案
3. **用户论坛**：交流经验和技术

### 调试工具推荐
1. **浏览器开发者工具**：测试选择器
2. **正则表达式测试工具**：验证正则
3. **网络抓包工具**：分析请求响应

记住：drpy源的调试需要耐心和系统的方法。从连接问题开始，逐步排查到解析问题，最后解决播放问题。