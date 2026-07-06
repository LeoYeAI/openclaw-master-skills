# drpy源属性详解

## 基础属性

### 类型配置
| 属性 | 类型 | 说明 | 示例 |
|------|------|------|------|
| 类型 | string | 源类型：'影视'、'听书'、'漫画'、'小说' | '影视' |
| title | string | 规则标题，播放器中显示的名称 | '鸭奈飞' |
| 编码 | string | 网页编码，默认utf-8 | 'utf-8' |
| 搜索编码 | string | 搜索独立编码，优先于全局编码 | 'gbk' |

### 域名配置
| 属性 | 类型 | 说明 | 示例 |
|------|------|------|------|
| host | string | 网页域名根，包含协议头 | 'https://www.baidu.com' |
| hostJs | string/function | 动态抓取域名的JS代码 | `print(HOST);let html=request(HOST);...` |
| homeUrl | string | 网站首页链接 | '/latest/' |

### URL模板
| 属性 | 类型 | 说明 | 示例 |
|------|------|------|------|
| url | string | 分类页面链接模板 | '/fyclass/fypage.html[/fyclass/]' |
| detailUrl | string | 二级详情拼接链接 | 'https://yanetflix.com/voddetail/fyid.html' |
| searchUrl | string | 搜索链接模板 | '/vodsearch/紧箍咒/page/fypage.html' |

### 功能开关
| 属性 | 类型 | 说明 | 示例 |
|------|------|------|------|
| searchable | number | 是否启用全局搜索 | 1（启用）或0（禁用） |
| quickSearch | number | 是否启用快速搜索 | 1（启用）或0（禁用） |
| filterable | number | 是否启用筛选 | 1（启用）或0（禁用） |
| double | boolean | 是否双层列表定位 | true（双层）或false（单层） |

## 分类相关属性

### 静态分类
```javascript
// 静态分类名称（用&分隔）
class_name: '电影&电视剧&动漫&综艺',

// 静态分类标识（与名称对应）
class_url: '1&2&3&4',
```

### 动态分类
```javascript
// 动态分类获取
class_parse: '#side-menu:lt(1) li;a&&Text;a&&href;com/(.*?)/',
// 格式：列表选择器;标题选择器;链接选择器;正则提取（可选）

// 排除某些分类
cate_exclude: '今日更新|热榜',
```

## 请求配置

### 请求头
```javascript
headers: {
  // 常用User-Agent
  'User-Agent': 'MOBILE_UA',      // 移动端UA
  'User-Agent': 'PC_UA',          // PC端UA  
  'User-Agent': 'okhttp/3.14.9',  // 常用Android UA
  
  // 其他常见头
  'Cookie': 'searchneed=ok',
  'Referer': 'https://www.example.com/',
  'Accept': 'application/json, text/javascript, */*; q=0.01',
  'Accept-Language': 'zh-CN,zh;q=0.9',
  'Accept-Encoding': 'gzip, deflate, br',
  'Cache-Control': 'no-cache',
  'X-Requested-With': 'XMLHttpRequest',
},
```

### 超时和重试
```javascript
// 请求超时（毫秒）
timeout: 5000,  // 默认3000，建议5000

// 服务器解析播放
play_parse: true,

// play_json配置
play_json: [{
  re: '*',
  json: {
    jx: 1,
    parse: 1,
  },
}],
```

## 线路和标签管理

### 线路过滤
```javascript
// 排除某些线路名
tab_exclude: '',

// 移除某个线路及相关选集
tab_remove: ['tkm3u8'],

// 线路顺序（按优先级排序）
tab_order: ['lzm3u8', 'wjm3u8', '1080zyk', 'zuidam3u8', 'snm3u8'],

// 线路名替换（显示名称美化）
tab_rename: {
  'lzm3u8': '量子',
  '1080zyk': '1080看', 
  'zuidam3u8': '最大资源',
  'kuaikan': '快看',
  'bfzym3u8': '暴风',
  'ffm3u8': '非凡',
  'snm3u8': '索尼',
  'tpm3u8': '淘片',
  'tkm3u8': '天空',
},
```

## 筛选功能

### 筛选配置
```javascript
// 筛选条件字典
filter: {
  style: {
    name: '类型',
    value: [
      {n: '全部', v: ''},
      {n: '爱情', v: '爱情'},
      {n: '喜剧', v: '喜剧'},
    ]
  },
  zone: {
    name: '地区', 
    value: [
      {n: '全部', v: ''},
      {n: '大陆', v: '大陆'},
      {n: '香港', v: '香港'},
    ]
  }
},

// 默认筛选条件（不同分类不同默认值）
filter_def: {
  douyu: {
    area: '一起看',
    other: '..'
  },
  huya: {
    area: '影音馆',
    other: '..'
  }
},

// 筛选传参模板
filter_url: 'style={{fl.style}}&zone={{fl.zone}}&year={{fl.year}}&fee={{fl.fee}}&order={{fl.order}}',
```

## 显示和样式

### 列表样式
```javascript
// 海阔一级列表样式
hikerListCol: "avatar",  // 列表显示样式
// 可选值: "avatar"（头像模式）, ""（默认列表）

// 海阔推荐列表样式  
hikerClassListCol: "avatar",

// 首页推荐显示数量
limit: 6,

// 分页控制
pagecount: {"1": 1, "2": 1, "3": 1, "4": 1, "5": 1, "7": 1, "时间表": 1},
```

### 图片处理
```javascript
// 图片来源（添加referer和UA）
图片来源: '@Referer=http://www.jianpianapp.com@User-Agent=jianpian-version350',

// 图片链接替换
图片替换: 'https://www.keke6.app/=>https://vres.a357899.cn/',
```

## JavaScript函数属性

### 动态处理函数
```javascript
// 动态域名获取（优先级最高）
hostJs: async function () {
  let {HOST} = this;
  return HOST
},

// 预处理函数（源初始化时执行一次）
预处理: async function () {
  let {HOST} = this;
  return HOST
},

// 二级访问前处理
二级访问前: `js:
  log(MY_URL);
  let jump=request(MY_URL).match(/href="(.*?)"/)[1];
  log(jump);
  MY_URL=urljoin2(MY_URL,jump)
`,
```

### 解析函数返回值格式

#### 推荐/一级/搜索函数
返回数组，每个元素包含：
```javascript
{
  vod_id: "123",           // 视频ID
  vod_name: "影片名称",     // 视频名称
  vod_pic: "封面图URL",     // 封面图
  vod_remarks: "更新状态",  // 备注/状态
  vod_year: "2024",        // 年份
  vod_area: "大陆",        // 地区
  vod_actor: "演员",       // 主演
  vod_director: "导演",    // 导演
  vod_content: "简介",     // 剧情简介
}
```

#### 二级函数
返回对象包含：
```javascript
{
  vod_name: "影片名称",
  vod_pic: "封面图URL", 
  vod_remarks: "更新状态",
  vod_year: "2024",
  vod_area: "大陆",
  vod_actor: "演员",
  vod_director: "导演",
  vod_content: "简介",
  vod_play_from: "播放来源",  // 如：量子资源
  vod_play_url: "播放链接",    // 如：第1集$播放地址
}
```

## 特殊功能属性

### 本地代理
```javascript
proxy_rule: `js:
  log(input);
  input = [200,'text;plain','hello drpy']
`,
```

### 辅助嗅探
```javascript
// 是否启用辅助嗅探
sniffer: 1,

// 视频链接正则
isVideo: "http((?!http).){26,}\\.(m3u8|mp4|flv|avi|mkv|wmv|mpg|mpeg|mov|ts|3gp|rm|rmvb|asf|m4a|mp3|wma)",

// 自定义嗅探规则
isVideo: `js:
  log(input);
  if(/m3u8/.test(input)){
    input = true
  }else{
    input = false
  }
`,
```

### 免嗅解析
```javascript
// lazy函数处理播放地址
lazy: async function () {
  let {input} = this;
  return {
    url: input,
    parse: 0
  }
},
```

## 注意事项

1. **属性命名**：使用小写或驼峰命名，如`class_name`、`play_parse`
2. **编码设置**：默认UTF-8，GBK网站需要指定`编码`或`搜索编码`
3. **URL模板**：使用`fyclass`、`fypage`、`**`、`fyid`等占位符
4. **正则转义**：字符串中的正则需要双重转义，如`(\\d+)`对应`/(\d+)/`
5. **缓存问题**：修改JS后需要重新加载源配置（猫影视需换源）