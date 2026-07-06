# drpy模板继承与修改

## 模板系统概述

drpy支持模板继承机制，允许新源继承现有模板的配置，只需覆盖或添加特定属性。这大大简化了源创建过程，特别是对于结构相似的网站。

## 可用模板

### 常用模板列表

| 模板名 | 描述 | 适用网站类型 |
|--------|------|-------------|
| mxpro | MX影视Pro模板 | 通用CMS影视站 |
| mxone | MX影视One模板 | 另一类CMS站 |
| 海螺 | 海螺影视模板 | 类似MX的CMS站 |
| 首图 | 首图模板 | 特殊布局网站 |
| 短视 | 短视频模板 | 短视频网站 |
| 采集 | 采集站模板 | 采集/聚合站 |
| 自动 | 自动适配模板 | CMS类站（自动检测） |

## 模板继承方法

### 方法一：Object.assign（传统方式）

```javascript
var rule = Object.assign(muban.mxpro, {
  // 覆盖的属性
  title: '鸭奈飞',
  host: 'https://yanetflix.com',
  
  // 添加的属性
  url: '/index.php/vod/show/id/fyclass/page/fypage.html',
  class_parse: `.navbar-items li:gt(1):lt(6);a&&Text;a&&href;.*/(.*?).html`,
  
  // 可以覆盖模板的函数
  推荐: async function () {
    let {input} = this;
    // 自定义推荐逻辑
    return [];
  },
});
```

### 方法二：模板属性（新方式）

```javascript
var rule = {
  title: 'cokemv',
  模板: 'mxpro',  // 指定继承的模板
  host: 'https://cokemv.me',
  
  // 覆盖的属性
  class_parse: `.navbar-items li:gt(1):lt(7);a&&Text;a&&href;/(\\d+).html`,
  
  // 添加的属性
  searchUrl: '/vodsearch/紧箍咒/page/fypage.html',
};
```

### 方法三：自动匹配模板

```javascript
var rule = {
  模板: '自动',  // 自动选择最匹配的模板
  模板修改: $js.toString(() => {
    // 修改模板的局部配置
    Object.assign(muban.自动.二级, {
      tab_text: 'div.small&&Text',  // 修改二级选项卡文本选择器
      list_url: 'a.data-src&&href', // 修改列表链接选择器
    });
  }),
  
  // 源配置
  title: '剧圈圈[自动]',
  host: 'https://www.jqqzx.cc/',
  
  // 必须提供的配置（用于自动匹配）
  url: '/vodshow/id/fyclass/page/fypage.html',
  searchUrl: '/vodsearch**/page/fypage.html',
  class_parse: '.navbar-items li:gt(2):lt(8);a&&Text;a&&href;.*/(.*?)\.html',
  cate_exclude: '今日更新|热榜',
};
```

**注意**：自动匹配只支持能从HOST获取分类的CMS模板站，采集站、短视频站等API模板无法自动匹配。

## 模板修改

### 修改模板函数

```javascript
// 修改特定模板的函数
模板修改: $js.toString(() => {
  // 修改一级列表解析
  Object.assign(muban.mxpro.一级, {
    // 更改选择器
    selector: '.video-item',
    title: 'h3&&Text',
    image: 'img&&data-src',
    desc: '.info&&Text',
    link: 'a&&href',
  });
  
  // 修改二级详情解析
  Object.assign(muban.mxpro.二级, {
    tab_text: '.play-source&&Text',
    list_text: '.play-list-item&&Text',
    list_url: 'a&&data-play',
  });
  
  // 添加自定义函数
  muban.mxpro.自定义函数 = async function () {
    // 自定义逻辑
    return result;
  };
}),
```

### 批量修改多个模板

```javascript
模板修改: $js.toString(() => {
  // 修改多个模板的通用配置
  const templates = ['mxpro', 'mxone', '海螺'];
  
  templates.forEach(templateName => {
    if (muban[templateName]) {
      // 统一修改headers
      muban[templateName].headers = {
        'User-Agent': 'MOBILE_UA',
        'Referer': HOST,
      };
      
      // 统一修改超时
      muban[templateName].timeout = 8000;
    }
  });
}),
```

## 模板组合

### 继承多个模板

```javascript
// 先继承一个模板，再混入另一个模板的部分配置
var baseTemplate = Object.assign({}, muban.mxpro);
var combinedTemplate = Object.assign(baseTemplate, {
  // mxpro的配置
  ...muban.mxpro,
  // 混入首图模板的某些特性
  推荐: muban.首图.推荐,
  一级: muban.首图.一级,
  
  // 自定义配置
  title: '混合模板源',
  host: 'https://example.com',
});
```

### 创建自定义模板

```javascript
// 定义自定义模板（可存储在单独的JS文件中）
var myCustomTemplate = {
  // 基础配置
  type: '影视',
  searchable: 1,
  quickSearch: 0,
  filterable: 0,
  headers: {
    'User-Agent': 'MOBILE_UA',
  },
  timeout: 5000,
  
  // 解析函数
  推荐: async function () {
    let {input} = this;
    return [];
  },
  
  一级: async function () {
    let {input} = this;
    return [];
  },
  
  二级: async function () {
    let {input} = this;
    return {};
  },
  
  搜索: async function () {
    let {input} = this;
    return [];
  },
};

// 在源中使用自定义模板
var rule = Object.assign(myCustomTemplate, {
  title: '使用自定义模板',
  host: 'https://example.com',
  url: '/fyclass/fypage.html',
});
```

## 模板查看与调试

### 查看模板内容

```javascript
// 在浏览器控制台查看模板
console.log(muban.mxpro);  // 查看mxpro模板完整结构
console.log(muban.mxpro.一级);  // 查看一级函数
console.log(muban.mxpro.headers);  // 查看headers配置
```

### 调试模板继承

```javascript
// 创建调试函数查看最终合并的规则
var rule = Object.assign(muban.mxpro, {
  title: '调试源',
  host: 'https://debug.com',
});

// 打印最终规则（开发时使用）
console.log('最终规则:', JSON.stringify(rule, null, 2));
```

## 最佳实践

### 1. 选择合适的模板
- **CMS影视站** → mxpro、mxone
- **短视频站** → 短视
- **采集聚合站** → 采集
- **不确定类型** → 自动（CMS站优先）

### 2. 最小化修改
```javascript
// 推荐：只修改必要的属性
var rule = {
  模板: 'mxpro',
  title: '源名称',
  host: 'https://example.com',
  // 只修改class_parse以适配网站分类结构
  class_parse: '.menu li;a&&Text;a&&href;/(\\d+)/',
};

// 不推荐：过度修改
var rule = Object.assign(muban.mxpro, {
  title: '源名称',
  host: 'https://example.com',
  // 修改大量函数（除非必要）
  推荐: function() { /* 完全重写 */ },
  一级: function() { /* 完全重写 */ },
  二级: function() { /* 完全重写 */ },
  搜索: function() { /* 完全重写 */ },
});
```

### 3. 保留模板默认值
除非有特殊需求，否则保留模板的默认配置：
- headers
- timeout  
- play_parse
- double等布局参数

### 4. 验证模板兼容性
创建源后，测试：
- 分类获取是否正确
- 一级列表是否能正常显示
- 二级详情是否完整
- 搜索功能是否正常
- 播放是否可用

## 常见问题

### Q: 模板继承后某些功能不工作
A: 检查是否意外覆盖了模板的关键函数或属性。

### Q: 自动模板不匹配
A: 确保网站是标准CMS结构，并提供`url`、`searchUrl`、`class_parse`等必要配置。

### Q: 如何知道模板有哪些可配置项？
A: 使用`console.log(muban.模板名)`查看模板结构，或参考现有成功源的配置。

### Q: 可以继承多个模板吗？
A: 不能直接继承多个，但可以通过`Object.assign`组合多个模板的配置。

### Q: 模板修改不生效
A: 确保`模板修改`函数正确使用`$js.toString()`包装，并在函数内正确修改模板对象。