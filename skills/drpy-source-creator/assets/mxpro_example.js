/**
 * MX影视Pro模板继承示例
 * 适用于大多数CMS影视站
 */

// 方法1：Object.assign方式（传统）
var rule = Object.assign(muban.mxpro, {
  title: '鸭奈飞',
  host: 'https://yanetflix.com',
  url: '/index.php/vod/show/id/fyclass/page/fypage.html',
  class_parse: `.navbar-items li:gt(1):lt(6);a&&Text;a&&href;.*/(.*?).html`,
});

/**
 * 方法2：模板属性方式（新）
 */
// var rule = {
//   title: '鸭奈飞',
//   模板: 'mxpro',
//   host: 'https://yanetflix.com',
//   url: '/index.php/vod/show/id/fyclass/page/fypage.html',
//   class_parse: `.navbar-items li:gt(1):lt(6);a&&Text;a&&href;.*/(.*?).html`,
// };

/**
 * 方法3：自动匹配模板
 */
// var rule = {
//   模板: '自动',
//   模板修改: $js.toString(() => {
//     // 可根据需要修改模板配置
//     Object.assign(muban.自动.二级, {
//       tab_text: 'div.small&&Text',
//     });
//   }),
//   title: '示例源[自动]',
//   host: 'https://www.example.com',
//   url: '/vodshow/id/fyclass/page/fypage.html',
//   searchUrl: '/vodsearch**/page/fypage.html',
//   class_parse: '.navbar-items li:gt(2):lt(8);a&&Text;a&&href;.*/(.*?)\.html',
// };

/**
 * 带详细注释的完整示例
 */
var rule_detailed = Object.assign(muban.mxpro, {
  // 基本信息
  title: '完整示例源',
  编码: 'utf-8',
  host: 'https://www.example.com',
  
  // URL配置
  homeUrl: '/',
  url: '/vod/show/id/fyclass/page/fypage.html',
  searchUrl: '/vodsearch/紧箍咒/page/fypage.html',
  
  // 动态分类获取（覆盖模板的静态分类）
  class_parse: '#side-menu li;a&&Text;a&&href;/(\\d+)/',
  
  // 自定义headers（合并到模板headers中）
  headers: {
    'User-Agent': 'MOBILE_UA',
    'Referer': 'https://www.example.com/',
  },
  
  // 自定义解析函数（可选）
  推荐: async function () {
    let html = await request(this.homeUrl);
    // 自定义推荐解析逻辑
    return [
      {
        vod_name: '自定义推荐影片',
        vod_pic: 'https://example.com/pic.jpg',
        vod_remarks: '更新至10集',
      }
    ];
  },
  
  // 二级详情定制
  二级: async function () {
    // 先执行模板的二级函数
    let baseResult = await muban.mxpro.二级.call(this);
    
    // 添加自定义数据
    baseResult.vod_content = baseResult.vod_content + '\n\n自定义内容';
    
    return baseResult;
  },
});

/**
 * 使用注意事项：
 * 1. 优先使用模板继承，减少重复代码
 * 2. 只覆盖需要修改的属性，保留模板默认配置
 * 3. 测试时先验证模板本身是否适合目标网站
 * 4. 注意属性覆盖顺序，后定义的覆盖先定义的
 */