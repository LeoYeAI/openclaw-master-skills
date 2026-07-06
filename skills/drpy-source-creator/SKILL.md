---
name: drpy-source-creator
description: drpy视频源创建与调试技能。当用户需要创建、修改、调试drpy视频源（用于TVBox、海阔视界、ZYPlayer等播放器）时使用此技能。包括drpy源属性配置、模板继承、正则表达式编写、本地代理设置、不同类型源（影视/听书/漫画/小说）支持。
---

# drpy视频源创建与调试

## 概述

drpy源是一种用于TVBox、海阔视界、ZYPlayer等播放器的视频源格式，使用JavaScript编写，支持动态内容抓取和解析。本技能提供完整的drpy源创建指南，包含属性配置、模板继承、正则表达式编写、常见问题调试等。

## 快速开始

以下是基础的drpy源模板：

```javascript
var rule = {
  // 影视|听书|漫画|小说
  类型: '影视',
  // 规则标题
  title: '示例源',
  // 网页的域名根
  host: 'https://www.example.com',
  // 网站的首页链接
  homeUrl: '/latest/',
  // 分类页面链接
  url: '/fyclass/fypage.html',
  // 搜索链接
  searchUrl: '/vodsearch/紧箍咒/page/fypage.html',
  // 是否启用全局搜索
  searchable: 1,
  // 是否启用快速搜索  
  quickSearch: 0,
  // 是否启用筛选
  filterable: 0,
  // 请求头
  headers: {
    'User-Agent': 'MOBILE_UA',
  },
  // 请求超时(毫秒)
  timeout: 5000,
  // 是否需要调用免嗅lazy函数
  play_parse: true,
  // 静态分类名称
  class_name: '电影&电视剧&动漫&综艺',
  // 静态分类标识
  class_url: '1&2&3&4',
}
```

## 实战案例分析：皮皮影视

### 分析步骤

**第一步：获取网站源码**
```python
import requests
headers = {'User-Agent': 'Mozilla/5.0...'}
resp = requests.get('https://www.pitv.cc/', headers=headers)
html = resp.text
```

**第二步：确认关键选择器**
```
✓ .hl-vod-list - 列表容器存在
✓ .hl-list-item - 列表项存在  
✓ a&&title - 标题属性存在
✓ a&&data-original - 图片属性存在
✗ .remarks - 状态class不存在（实际是.hl-pic-text span）
```

**第三步：修正选择器**
```javascript
// 错误（参考代码）
推荐: '.hl-vod-list;li;a&&title;a&&data-original;.remarks&&Text;a&&href',

// 正确（实际HTML结构）
推荐: '.hl-vod-list;li;a&&title;a&&data-original;.hl-pic-text span&&Text;a&&href',
```

**第四步：验证搜索功能**
- 测试发现搜索需要验证码
- 结论：searchable应设为0

**第五步：最终可用配置**
```javascript
var rule = {
  title: '皮皮影视',
  host: 'https://www.pitv.cc',
  url: '/show/fyclassfyfilter/page/fypage/',
  searchable: 0,  // 搜索需要验证码，禁用
  class_name: '剧集&电影&动漫',
  class_url: '1&2&3',
  推荐: '.hl-vod-list;li;a&&title;a&&data-original;.hl-pic-text span&&Text;a&&href',
  一级: '.hl-vod-list&&.hl-list-item;a&&title;a&&data-original;.hl-pic-text span&&Text;a&&href',
  二级: {
    title: 'h1&&Text',
    img: '.hl-lazy&&data-original',
    tabs: '.hl-plays-from&&a',
    lists: '.hl-plays-list:eq(#id)&&a',
  },
}
```

## drpy源属性详解

### 核心属性

| 属性 | 类型 | 说明 | 示例 |
|------|------|------|------|
| 类型 | string | 源类型：'影视'、'听书'、'漫画'、'小说' | '影视' |
| title | string | 规则标题，在播放器中显示的名称 | '鸭奈飞' |
| host | string | 网站域名根，包含http/https协议 | 'https://yanetflix.com' |
| homeUrl | string | 网站首页链接，用于获取分类和推荐 | '/latest/' |
| url | string | 分类页面链接模板 | '/vod/show/id/fyclass/page/fypage.html' |
| searchUrl | string | 搜索链接模板 | '/vodsearch/紧箍咒/page/fypage.html' |
| searchable | number | 是否启用全局搜索 | 1（启用）或0（禁用） |
| quickSearch | number | 是否启用快速搜索 | 1（启用）或0（禁用） |
| filterable | number | 是否启用筛选 | 1（启用）或0（禁用） |

### 分类相关属性

```javascript
// 静态分类配置
class_name: '电影&电视剧&动漫&综艺',
class_url: '1&2&3&4',

// 动态分类获取（推荐）
class_parse: '#side-menu:lt(1) li;a&&Text;a&&href;com/(.*?)/',
// 格式：列表选择器;标题选择器;链接选择器;正则提取（可选）
```

### 请求配置

```javascript
// 请求头配置
headers: {
  'User-Agent': 'MOBILE_UA',
  'Cookie': 'searchneed=ok',
  'Referer': 'https://www.example.com/'
},

// 超时设置（毫秒）
timeout: 5000,

// 动态获取host（优先级最高）
hostJs: async function () {
  let {HOST} = this;
  return HOST
},

// 预处理（初始化时执行一次）
预处理: async function () {
  let {HOST} = this;
  return HOST
},
```

### 解析函数

drpy源的核心解析函数，用于获取不同页面的内容：

```javascript
// 推荐内容获取
推荐: async function () {
  let {input} = this;
  // input为homeUrl的内容
  return []
},

// 一级列表获取
一级: async function () {
  let {input} = this;
  // input为url模板填入后的链接
  return []
},

// 二级详情获取
二级: async function () {
  let {input} = this;
  // input为一级返回的链接
  return {}
},

// 搜索内容获取
搜索: async function () {
  let {input} = this;
  // input为searchUrl模板填入后的链接
  return []
},
```

### 播放相关

```javascript
// 免嗅播放解析
play_parse: true,

// lazy函数处理播放地址
lazy: async function () {
  let {input} = this;
  return {
    url: input,
    parse: 0
  }
},

// 辅助嗅探规则
sniffer: 1,
isVideo: "http((?!http).){26,}\\.(m3u8|mp4|flv|avi|mkv|wmv|mpg|mpeg|mov|ts|3gp|rm|rmvb|asf|m4a|mp3|wma)",
```

## 模板继承

### 方法一：Object.assign

```javascript
var rule = Object.assign(muban.mxpro, {
  title: '鸭奈飞',
  host: 'https://yanetflix.com',
  url: '/index.php/vod/show/id/fyclass/page/fypage.html',
  class_parse: `.navbar-items li:gt(1):lt(6);a&&Text;a&&href;.*/(.*?).html`,
});
```

### 方法二：模板属性（新）

```javascript
var rule = {
  title: 'cokemv',
  模板: 'mxpro',
  host: 'https://cokemv.me',
  class_parse: `.navbar-items li:gt(1):lt(7);a&&Text;a&&href;/(\\d+).html`,
}
```

### 方法三：自动匹配模板

```javascript
var rule = {
  模板: '自动',
  模板修改: $js.toString(() => {
    Object.assign(muban.自动.二级, {
      tab_text: 'div--small&&Text',
    });
  }),
  title: '剧圈圈[自动]',
  host: 'https://www.jqqzx.cc/',
  url: '/vodshow/id/fyclass/page/fypage.html',
  searchUrl: '/vodsearch**/page/fypage.html',
  class_parse: '.navbar-items li:gt(2):lt(8);a&&Text;a&&href;.*/(.*?)\.html',
  cate_exclude: '今日更新|热榜',
}
```

## 不同类型源支持

### 影视源（默认）
标准的视频源，支持电影、电视剧、动漫等内容。

### 听书源
用法与影视源一致，播放音频内容。

### 漫画源
需要在`lazy`函数处理后返回`pics://`协议：
```javascript
lazy: async function () {
  return "pics://图片链接1,图片链接2,图片链接3";
}
```

### 小说源  
需要在`lazy`函数处理后返回`novel://`协议：
```javascript
lazy: async function () {
  return 'novel://{"title":"章节名称","content":"章节内容"}';
}
```

## 正则表达式写法

在字符串属性（如`class_parse`）中使用正则表达式时需要注意转义：

| 需求 | JavaScript正则 | drpy字符串写法 |
|------|---------------|----------------|
| 数字 | `/(\d+)/` | `(\\d+)` |
| 任意字符 | `/.*/` | `.*` |
| 非贪婪匹配 | `/(.*?)/` | `(.*?)` |
| 多个分组 | `/(\d+)-(\w+)/` | `(\\d+)-(\\w+)` |

## 本地代理设置

```javascript
proxy_rule: `js:
  log(input);
  input = [200,'text;plain','hello drpy']
`,
```

本地代理的`input`参数格式为三元素数组：
`[status_code, content_type, data]`

示例：
```javascript
// 返回M3U8文件
input = [200,'application/vnd.apple.mpegurl', m3u8_content];

// 返回文本
input = [200,'text/plain', 'hello world'];
```

## 常见问题排查

### 1. 连接超时
- 检查`host`是否正确
- 调整`timeout`值（默认5000毫秒）
- 检查网络连接

### 2. 解析失败
- 确认选择器是否正确
- 使用`log()`函数调试输出
- 检查网页结构是否变化

### 3. 播放失败
- 检查`play_parse`设置
- 确认`lazy`函数返回正确格式
- 验证`sniffer`规则是否匹配视频链接

### 4. 分类获取失败
- 确认`class_parse`格式正确
- 检查正则表达式转义
- 验证分类页面是否可访问

## 工具和资源

### 代码格式化
```bash
# 安装uglify-js
npm install uglify-js -g

# 压缩JS文件
uglifyjs source.js -o source.min.js
```

### WebStorm配置
1. 获取uglifyjs路径：`where uglifyjs`
2. 配置外部工具：
   - 程序: `C:\Users\username\AppData\Roaming\npm\uglifyjs.cmd`
   - 参数: `$FileName$ -o $FileNameWithoutExtension$.min.js`
   - 工作目录: `$FileDir$`

### 调试技巧
1. 使用`log()`函数输出调试信息
2. 分步测试各个解析函数
3. 验证模板继承是否正确
4. 检查属性拼写和格式

## 进阶功能

### RSA加解密
```javascript
// 加密
RSA.encode(data, key, option);

// 解密  
RSA.decode(data, key, option);
```

### 动态线路管理
```javascript
// 线路顺序
tab_order: ['lzm3u8', 'wjm3u8', '1080zyk'],

// 线路名替换
tab_rename: {
  'lzm3u8': '量子资源',
  '1080zyk': '1080看',
},

// 移除线路
tab_remove: ['tkm3u8'],
```

### 图片处理
```javascript
// 图片替换
图片替换: 'https://old-domain.com/=>https://new-domain.com/',

// 图片来源（添加referer）
图片来源: '@Referer=http://www.example.com@User-Agent=custom-ua',
```

---

## Action与按钮

在drpy源的二级详情或其他交互页面中，可以通过返回`action`对象来定义按钮行为：

```javascript
二级: async function () {
  return {
    // 视频详情信息
    vod_name: "影片名称",
    vod_play_from: "播放来源",
    vod_play_url: "第1集$播放地址",
    
    // Action配置
    action: {
      button: 2,  // 按钮类型：0-关闭, 1-取消, 2-确定和取消, 3-确定/取消/重置, 4-确定/取消/重置/预览
      // 其他action属性...
    },
  };
},
```

### 按钮类型说明
| 值 | 按钮组合 | 适用场景 |
|----|----------|----------|
| 0 | 关闭按钮 | 只提供关闭功能 |
| 1 | 取消按钮 | 简单确认场景 |
| 2 | 确定和取消 | 需要用户确认的操作 |
| 3 | 确定、取消、重置 | 表单或设置页面 |
| 4 | 确定、取消、重置、预览 | 复杂的编辑页面 |

### 自定义Action
除了按钮，action还可以包含其他指令：
```javascript
action: {
  button: 2,
  message: "操作提示信息",
  redirect: "目标URL",
  // 其他自定义属性
},
```

## 工具与格式化

### 代码压缩
drpy源可以通过压缩减少文件大小：
```bash
# 安装uglify-js
npm install uglify-js -g

# 压缩JS文件
uglifyjs source.js -o source.min.js

# 推荐配置
uglifyjs source.js -o source.min.js -c -m --comments '/@license|@preserve/'
```

### WebStorm配置
1. 获取uglifyjs路径：`where uglifyjs`
2. 配置外部工具：
   - 程序: `C:\Users\username\AppData\Roaming\npm\uglifyjs.cmd`
   - 参数: `$FileName$ -o $FileNameWithoutExtension$.min.js`
   - 工作目录: `$FileDir$`

详细格式化指南见：[formatting.md](references/formatting.md)

## 常见错误与排查

### 错误1：首页/分类空白（选择器不匹配）

**症状**：分类能显示，但点击后列表为空

**原因**：参考代码的选择器与实际HTML不符

**排查方法**：
```python
import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0...'}
html = requests.get('https://example.com/', headers=headers).text
soup = BeautifulSoup(html, 'html.parser')

# 检查选择器是否存在
print('hl-vod-list:', bool(soup.find(class_='hl-vod-list')))
print('hl-list-item:', bool(soup.find(class_='hl-list-item')))
print('remarks:', bool(soup.find(class_='remarks')))  # 可能不存在

# 查找实际的class名
for elem in soup.find_all(class_=True):
    if 'pic' in str(elem.get('class')) or 'text' in str(elem.get('class')):
        print(elem.name, elem.get('class'))
```

**解决方案**：
```javascript
// 错误
推荐: '.hl-vod-list;li;a&&title;a&&data-original;.remarks&&Text;a&&href',

// 正确（根据实际HTML调整）
推荐: '.hl-vod-list;li;a&&title;a&&data-original;.hl-pic-text span&&Text;a&&href',
```

### 错误2：搜索功能异常

**症状**：搜索返回空结果或报错

**排查方法**：
```python
# 测试搜索URL
search_resp = requests.get('https://example.com/search/关键词/', headers=headers)
print('状态码:', search_resp.status_code)
print('是否包含验证码:', '验证码' in search_resp.text)
print('是否包含结果:', 'hl-vod-list' in search_resp.text)
```

**常见情况**：
1. **需要验证码** → 设置 `searchable: 0` 禁用搜索
2. **URL格式错误** → 检查实际的搜索表单action
3. **需要登录/Cookie** → 添加Cookie到headers

### 错误3：二级详情页空白

**症状**：能进入详情页，但无播放列表

**排查方法**：
```python
# 获取详情页HTML
detail_html = requests.get('https://example.com/vod/123/', headers=headers).text

# 检查关键元素
print('h1:', 'h1' in detail_html)
print('hl-plays-list:', 'hl-plays-list' in detail_html)
print('hl-plays-from:', 'hl-plays-from' in detail_html)
```

**解决方案**：
```javascript
// 根据实际HTML调整二级选择器
二级: {
  title: 'h1&&Text',  // 使用h1而不是.hl-dc-title
  img: '.hl-lazy&&data-original',
  tabs: '.hl-plays-from&&a',  // 播放源
  lists: '.hl-plays-list:eq(#id)&&a',  // 剧集列表
}
```

### 错误4：URL模板错误

**症状**：分类点击后跳转错误页面

**排查方法**：
```python
# 测试URL模板
# 参考代码: /show/fyclassfyfilter/page/fypage/
# 实际测试
for cls in ['1', '2', '3']:
    url = f'https://example.com/show/{cls}--------/page/1/'
    resp = requests.get(url, headers=headers)
    print(f'{url} -> {resp.status_code}')
```

**解决方案**：
```javascript
// 确认URL格式
url: '/show/fyclassfyfilter/page/fypage/',  // fyclass和fyfilter连在一起
// 或
url: '/type/fyclass/',  // 简单的分类格式
```

## 调试技巧

### 1. 添加日志输出
```javascript
推荐: `js:
  let html = request(input);
  log('首页HTML长度:', html.length);
  log('是否包含视频列表:', html.includes('hl-vod-list'));
  
  let items = pdfa(html, '.hl-vod-list li');
  log('提取到视频数量:', items.length);
  
  // 继续解析...
`,
```

### 2. 使用极简版本测试
```javascript
// 先测试基础功能
var rule = {
  title: '测试源',
  host: 'https://example.com',
  url: '/type/fyclass/',
  class_name: '分类1&分类2',
  class_url: '1&2',
  推荐: 'a;a&&Text;;;a&&href',  // 只取标题和链接
  一级: 'a;a&&Text;;;a&&href',
  二级: '*',
  lazy: ''
};
```

### 3. 分步验证
1. **分类** → 是否能正常显示
2. **一级** → 点击分类后是否有列表
3. **二级** → 点击进入详情页是否正常
4. **播放** → 点击播放是否能正常解析

## 扩展阅读

### 详细参考资料
- **[属性详解](references/attributes.md)** - 所有属性的完整说明和示例
- **[模板继承](references/templates.md)** - 模板系统的详细使用方法  
- **[解析函数](references/parsing.md)** - 选择器语法和解析函数编写指南
- **[问题排查](references/troubleshooting.md)** - 常见问题解决方案
- **[代码格式化](references/formatting.md)** - 代码压缩和格式化工具使用

### 实用模板文件
- **[基础模板](assets/basic_template.js)** - 适用于大多数CMS站的基础模板
- **[MXPro示例](assets/mxpro_example.js)** - MXPro模板继承完整示例
- **[皮皮影视实战](assets/pitv_example.js)** - 皮皮影视完整配置（含注释）

### 辅助脚本
- **[minify_drpy.js](scripts/minify_drpy.js)** - drpy源压缩脚本
- **[validate_drpy.js](scripts/validate_drpy.js)** - drpy源格式验证脚本
- **[analyze_site.py](scripts/analyze_site.py)** - 网站结构分析脚本

## 快速查找

| 任务 | 参考文档 |
|------|----------|
| 新建一个drpy源 | [基础模板](assets/basic_template.js) |
| 了解所有属性含义 | [属性详解](references/attributes.md) |
| 使用模板继承 | [模板继承](references/templates.md) |
| 编写解析函数 | [解析函数](references/parsing.md) |
| 调试源问题 | [问题排查](references/troubleshooting.md) |
| 压缩源代码 | [代码格式化](references/formatting.md) |
| 分析网站结构 | [analyze_site.py](scripts/analyze_site.py) |

**核心原则**：
1. **先验证，再编写** - 用Python获取HTML确认选择器存在
2. **从简到繁** - 先用极简版本测试，再逐步完善
3. **实际测试** - 不要完全相信参考代码，每个网站结构不同
4. **记录问题** - 遇到的选择器不匹配问题要记录，避免重复踩坑

**提示**：创建drpy源时，建议先使用简单的模板测试基础功能，再逐步添加高级功能。使用模板继承可以大大简化开发过程。