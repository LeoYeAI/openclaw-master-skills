/**
 * 皮皮影视实战示例
 * 基于实际HTML结构分析的配置
 * 
 * 分析过程：
 * 1. 获取首页HTML: requests.get('https://www.pitv.cc/')
 * 2. 确认选择器:
 *    - .hl-vod-list ✓ 存在
 *    - .hl-list-item ✓ 存在
 *    - a&&title ✓ 存在
 *    - a&&data-original ✓ 存在
 *    - .remarks ✗ 不存在（实际是.hl-pic-text span）
 * 3. 测试搜索: 需要验证码，禁用搜索功能
 * 4. 验证详情页: .hl-plays-list和.hl-plays-from存在
 */

var rule = {
  // 基本信息
  title: '皮皮影视',
  host: 'https://www.pitv.cc',
  
  // URL模板 - 支持筛选参数
  url: '/show/fyclassfyfilter/page/fypage/',
  filter_url: '{{fl.class}}{{fl.area}}{{fl.year}}{{fl.isend}}{{fl.letter}}',
  
  // 搜索功能需要验证码，禁用
  searchable: 0,
  quickSearch: 0,
  filterable: 1,
  
  // 请求头
  headers: {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://www.pitv.cc/'
  },
  timeout: 5000,
  limit: 40,
  
  // 播放配置
  play_parse: true,
  double: true,
  cate_exclude: '明星|专题|排行',

  // 动态分类和筛选
  class_parse: $js.toString(() => {
    try {
      let classes = [
        { type_id: '1', type_name: '剧集' },
        { type_id: '2', type_name: '电影' },
        { type_id: '3', type_name: '动漫' }
      ];
      let filterObj = {};
      classes.forEach(cls => {
        let html = request(rule.host + '/show/' + cls.type_id + '/', { headers: rule.headers });
        if (!html) return;
        
        const parseFilter = (label, key) => {
          let opts = [{ n: '全部', v: '' }];
          let bReg = new RegExp(`<span>${label}<\/span>[\\s\\S]*?<ul[^>]*>([\\s\\S]*?)<\/ul>`);
          let bMatch = html.match(bReg);
          if (bMatch) {
            let iReg = new RegExp(`\/${key}\/([^/]+)\/">([^<]+)<\/a>`, 'g');
            let im, seen = new Set();
            while ((im = iReg.exec(bMatch[1])) !== null) {
              let v = im[1], n = im[2].replace(/<.*?>/g, "").trim();
              if (n !== '全部' && !seen.has(v)) {
                opts.push({ n: n, v: '/' + key + '/' + v });
                seen.add(v);
              }
            }
          }
          return opts;
        };
        
        let currentFilters = [
          { key: 'class', name: '类型', value: parseFilter('类型', 'class') },
          { key: 'area', name: '地区', value: parseFilter('地区', 'area') },
          { key: 'year', name: '年份', value: parseFilter('年份', 'year') },
          { key: 'isend', name: '状态', value: parseFilter('状态', 'isend') },
          { key: 'letter', name: '字母', value: parseFilter('字母', 'letter') }
        ].filter(f => f.value.length > 1);
        
        filterObj[cls.type_id] = currentFilters;
      });
      
      input = classes;
      homeObj.filter = filterObj;
    } catch (e) {
      // 备用静态分类
      input = [
        { type_id: '1', type_name: '剧集' },
        { type_id: '2', type_name: '电影' },
        { type_id: '3', type_name: '动漫' }
      ];
    }
  }),

  // 播放器解析
  lazy: $js.toString(() => {
    let html = request(input);
    let playerMatch = html.match(/var player_.*?=({.*?})/);
    if (playerMatch) {
      let player = JSON.parse(playerMatch[1]);
      let url = unescape(player.url);
      let from = player.from;
      let playerJs = request(HOST + '/static/player/' + from + '.js');
      let parseApi = '';
      let apiMatch = playerJs.match(/src="([^"]+)"/);
      if (apiMatch) {
        parseApi = apiMatch[1];
      } else {
        parseApi = 'https://api.apiimg.com/show/super.php?id=';
      }
      if (parseApi.startsWith('//')) {
        parseApi = 'https:' + parseApi;
      }
      let finalUrl = parseApi + url;
      if (player.link_next) {
        let nextPath = player.link_next.startsWith('http') ? player.link_next : HOST + player.link_next;
        finalUrl += '&next=' + nextPath;
      }
      input = {
        jx: 0,
        url: finalUrl,
        parse: 1,
        header: rule.headers
      };
    }
  }),

  // 推荐 - 热播剧集
  // 关键修正：.remarks改为.hl-pic-text span
  推荐: '.hl-vod-list;li;a&&title;a&&data-original;.hl-pic-text span&&Text;a&&href',
  
  // 一级 - 分类列表
  // 使用&&连接容器和列表项
  一级: '.hl-vod-list&&.hl-list-item;a&&title;a&&data-original;.hl-pic-text span&&Text;a&&href',
  
  // 二级 - 详情页
  // 关键修正：使用实际存在的class
  二级: {
    title: 'h1&&Text',  // 标题在h1中
    img: '.hl-lazy&&data-original',  // 图片
    desc: '.hl-vod-content&&Text',  // 简介
    content: '.hl-conch-text&&Text',  // 详细内容
    tabs: '.hl-plays-from&&a',  // 播放源
    tab_text: 'a&&Text',
    lists: '.hl-plays-list:eq(#id)&&a',  // 剧集列表
  },
  
  // 搜索 - 禁用（需要验证码）
  搜索: '',
};

/**
 * 常见错误对照表：
 * 
 * 错误选择器（参考代码）        正确选择器（实际HTML）
 * -------------------------    ------------------------
 * .remarks&&Text               .hl-pic-text span&&Text
 * .hl-dc-title&&Text          h1&&Text
 * .hl-dc-content&&Text         .hl-vod-content&&Text
 * .hl-content-text&&Text       .hl-conch-text&&Text
 * .hl-tabs&&a                  .hl-plays-from&&a
 * 
 * 教训：不要直接复制参考代码的选择器，必须根据实际HTML结构调整！
 */