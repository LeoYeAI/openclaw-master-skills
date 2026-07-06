/**
 * drpy基础模板
 * 适用于大多数CMS影视站
 */

var rule = {
  // 源类型：影视|听书|漫画|小说
  类型: '影视',
  
  // 源信息
  title: '示例源',
  编码: 'utf-8',
  host: 'https://www.example.com',
  
  // URL模板
  homeUrl: '/',
  url: '/vod/show/id/fyclass/page/fypage.html',
  searchUrl: '/vodsearch/紧箍咒/page/fypage.html',
  
  // 功能开关
  searchable: 1,
  quickSearch: 0,
  filterable: 0,
  
  // 请求配置
  headers: {
    'User-Agent': 'MOBILE_UA',
  },
  timeout: 5000,
  
  // 播放配置
  play_parse: true,
  play_json: [{
    re: '*',
    json: {
      jx: 1,
      parse: 1,
    },
  }],
  
  // 分类配置
  class_name: '电影&电视剧&动漫&综艺',
  class_url: '1&2&3&4',
  
  // 或者使用动态分类获取
  // class_parse: '.navbar li;a&&Text;a&&href;/(\\d+)/',
  
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
  
  // 免嗅解析
  lazy: async function () {
    let {input} = this;
    return {
      url: input,
      parse: 0
    };
  },
};

/**
 * 使用说明：
 * 1. 修改host为实际域名
 * 2. 修改url和searchUrl模板以匹配网站
 * 3. 根据网站结构调整class_parse选择器
 * 4. 实现解析函数或使用字符串简写格式
 * 5. 测试所有功能
 */