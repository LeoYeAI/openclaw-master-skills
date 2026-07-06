#!/usr/bin/env python3
"""
热点新闻采集 - 20+ 数据源，纯 stdlib，无需 pip install
"""
import json, sys, argparse, re, time
from urllib.request import urlopen, Request
from urllib.parse import quote, urlencode
from urllib.error import URLError, HTTPError

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

def fetch(url, headers=None, timeout=10):
    h = {**HEADERS, **(headers or {})}
    req = Request(url, headers=h)
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.read().decode('utf-8')
    except (URLError, HTTPError) as e:
        sys.stderr.write(f"请求失败 {url}: {e}\n")
        return None

def fetch_json(url, headers=None, timeout=10):
    data = fetch(url, headers, timeout)
    if data:
        try: return json.loads(data)
        except json.JSONDecodeError: return None
    return None

def post_json(url, body, headers=None, timeout=10):
    h = {**HEADERS, "Content-Type": "application/json", **(headers or {})}
    req = Request(url, data=json.dumps(body).encode(), headers=h, method='POST')
    try:
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        sys.stderr.write(f"POST失败 {url}: {e}\n")
        return None

def filt(items, keyword=None):
    if not keyword: return items
    keywords = [k.lower() for k in keyword.split(',')]
    return [i for i in items if any(k in (i.get('title','')+ i.get('content','')).lower() for k in keywords)]

# ---- 数据源实现 ----

def fetch_hackernews(limit=20, keyword=None):
    ids = fetch_json("https://hacker-news.firebaseio.com/v0/topstories.json")
    if not ids: return []
    items = []
    for iid in ids[:min(limit*2, 50)]:
        item = fetch_json(f"https://hacker-news.firebaseio.com/v0/item/{iid}.json")
        if item and item.get('title'):
            items.append({"source":"Hacker News","title":item['title'],"url":item.get('url') or f"https://news.ycombinator.com/item?id={iid}","score":f"{item.get('score',0)} pts","time":""})
    return filt(items, keyword)[:limit]

def fetch_github(limit=20, keyword=None):
    html = fetch("https://github.com/trending?since=daily")
    if not html: return []
    items = []
    for m in re.finditer(r'<h2[^>]*lh-condensed[^>]*>.*?href="(/[^"]+)"', html.replace('\n',' ')):
        repo = m.group(1).strip('/')
        items.append({"source":"GitHub Trending","title":repo,"url":f"https://github.com/{repo}","score":"trending","time":"today"})
    return filt(items, keyword)[:limit]

def fetch_v2ex(limit=20, keyword=None):
    data = fetch_json("https://www.v2ex.com/api/topics/hot.json")
    if not data: return []
    items = [{"source":"V2EX","title":i.get('title',''),"url":i.get('url',''),"score":f"{i.get('replies',0)} replies","time":"Hot"} for i in data]
    return filt(items, keyword)[:limit]

def fetch_weibo(limit=20, keyword=None):
    html = fetch("https://s.weibo.com/top/summary?cate=realtimehot", {"Referer":"https://s.weibo.com/top/summary"})
    if not html: return []
    items = []
    for m in re.finditer(r'<td class="td-02">\s*<a href="([^"]+)"[^>]*>([^<]+)</a>', html):
        href, title = m.group(1), m.group(2).strip()
        if 'javascript:' in href: continue
        items.append({"source":"微博热搜","title":title,"url":f"https://s.weibo.com{href}","score":"","time":"实时"})
    return filt(items, keyword)[:limit]

def fetch_zhihu(limit=20, keyword=None):
    data = fetch_json("https://www.zhihu.com/api/v3/feed/topstory/hot-list-web?limit=50&desktop=true")
    if not data or 'data' not in data: return []
    items = []
    for i in data['data']:
        t = i.get('target',{})
        items.append({"source":"知乎热榜","title":t.get('title_area',{}).get('text',''),"url":t.get('link',{}).get('url',''),"score":t.get('metrics_area',{}).get('text',''),"time":"热榜"})
    return filt(items, keyword)[:limit]

def fetch_36kr(limit=20, keyword=None):
    data = post_json("https://gateway.36kr.com/api/mis/nav/newsflash/flow", {"pageSize":limit*2,"pageEvent":0})
    if not data: return []
    items_list = data.get('data',{}).get('itemList',[]) or []
    items = []
    for i in items_list:
        items.append({"source":"36氪","title":i.get('templateMaterial',{}).get('widgetTitle',''),"url":f"https://36kr.com/newsflashes/{i.get('itemId','')}","score":"","time":i.get('templateMaterial',{}).get('publishTime','')})
    return filt(items, keyword)[:limit]

def fetch_baidu(limit=20, keyword=None):
    html = fetch("https://top.baidu.com/board?tab=realtime")
    if not html: return []
    items = []
    for m in re.finditer(r'"word":"([^"]+)".*?"desc":"([^"]*)".*?"hotScore":"?(\d+)', html.replace('\n','')):
        items.append({"source":"百度热搜","title":m.group(1),"url":f"https://www.baidu.com/s?wd={quote(m.group(1))}","score":m.group(3),"time":"实时"})
    return filt(items, keyword)[:limit]

def fetch_juejin(limit=20, keyword=None):
    data = post_json("https://api.juejin.cn/recommend_api/v1/article/recommend_all_feed",{"id_type":2,"sort_type":200,"cursor":"0","limit":limit*2})
    if not data: return []
    items = []
    for i in (data.get('data',[]) or []):
        info = i.get('article_info',{})
        if not info.get('title'): continue
        items.append({"source":"掘金","title":info['title'],"url":f"https://juejin.cn/post/{info.get('article_id','')}","score":f"{info.get('digg_count',0)} 赞","time":""})
    return filt(items, keyword)[:limit]

def fetch_sspai(limit=20, keyword=None):
    data = fetch_json("https://sspai.com/api/v1/article/index/page/get?limit=20&offset=0&created_at=0")
    if not data: return []
    items = [{"source":"少数派","title":i.get('title',''),"url":f"https://sspai.com/post/{i.get('id','')}","score":f"{i.get('like_count',0)} 赞","time":""} for i in data.get('data',[])]
    return filt(items, keyword)[:limit]

def fetch_ithome(limit=20, keyword=None):
    html = fetch("https://www.ithome.com/")
    if not html: return []
    items = []
    for m in re.finditer(r'<a[^>]*href="(https://www\.ithome\.com/\d+/\d+/\d+/\d+\.htm)"[^>]*>([^<]+)</a>', html):
        items.append({"source":"IT之家","title":m.group(2).strip(),"url":m.group(1),"score":"","time":""})
    return filt(items, keyword)[:limit]

def fetch_producthunt(limit=20, keyword=None):
    html = fetch("https://www.producthunt.com/")
    if not html: return []
    items = []
    for m in re.finditer(r'data-test="post-name-([^"]*)"[^>]*>([^<]+)', html):
        items.append({"source":"Product Hunt","title":m.group(2).strip(),"url":f"https://www.producthunt.com/posts/{m.group(1)}","score":"","time":"today"})
    return filt(items, keyword)[:limit]

def fetch_bilibili(limit=20, keyword=None):
    data = fetch_json("https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all")
    if not data or data.get('code')!=0: return []
    items = [{"source":"B站热门","title":i.get('title',''),"url":i.get('short_link','') or f"https://www.bilibili.com/video/{i.get('bvid','')}","score":f"{i.get('stat',{}).get('view',0)} 播放","time":""} for i in data.get('data',{}).get('list',[])]
    return filt(items, keyword)[:limit]

def fetch_douyin(limit=20, keyword=None):
    data = fetch_json("https://www.douyin.com/aweme/v1/web/hot/search/list/", {"Referer":"https://www.douyin.com/"})
    if not data: return []
    items = []
    for i in (data.get('data',{}).get('word_list',[]) or []):
        items.append({"source":"抖音热搜","title":i.get('word',''),"url":f"https://www.douyin.com/search/{quote(i.get('word',''))}","score":str(i.get('hot_value','')),"time":"实时"})
    return filt(items, keyword)[:limit]

def fetch_toutiao(limit=20, keyword=None):
    data = fetch_json("https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc")
    if not data: return []
    items = [{"source":"今日头条","title":i.get('Title',''),"url":i.get('Url',''),"score":str(i.get('HotValue','')),"time":""} for i in data.get('data',[])]
    return filt(items, keyword)[:limit]

def fetch_tencent(limit=20, keyword=None):
    data = fetch_json("https://r.inews.qq.com/gw/event/hot_ranking_list?page_size=50")
    if not data: return []
    items = [{"source":"腾讯新闻","title":i.get('title',''),"url":i.get('url',''),"score":str(i.get('hotScore','')),"time":""} for i in data.get('idlist',[{}])[0].get('newslist',[])[1:]]
    return filt(items, keyword)[:limit]

def fetch_thepaper(limit=20, keyword=None):
    data = fetch_json("https://cache.thepaper.cn/contentapi/wwwIndex/rightSidebar")
    if not data: return []
    items = [{"source":"澎湃新闻","title":i.get('name',''),"url":f"https://www.thepaper.cn/newsDetail_forward_{i.get('contId','')}","score":"","time":""} for i in data.get('data',{}).get('hotNews',[])]
    return filt(items, keyword)[:limit]

def fetch_hupu(limit=20, keyword=None):
    html = fetch("https://bbs.hupu.com/all-gambia")
    if not html: return []
    items = []
    for m in re.finditer(r'<a[^>]*href="(/\d+\.html)"[^>]*class="[^"]*textSpan[^"]*"[^>]*>([^<]+)', html):
        items.append({"source":"虎扑","title":m.group(2).strip(),"url":f"https://bbs.hupu.com{m.group(1)}","score":"","time":""})
    return filt(items, keyword)[:limit]

def fetch_wallstreetcn(limit=20, keyword=None):
    data = fetch_json("https://api-one-wscn.awtmt.com/apiv1/content/lives?channel=global-channel&limit=30")
    if not data: return []
    items = [{"source":"华尔街见闻","title":i.get('title','') or i.get('content_text','')[:60],"url":f"https://wallstreetcn.com/live/{i.get('id','')}","score":"","time":i.get('display_time','')} for i in data.get('data',{}).get('items',[])]
    return filt(items, keyword)[:limit]

def fetch_cls(limit=20, keyword=None):
    data = fetch_json(f"https://www.cls.cn/nodeapi/updateTelegraphList?app=CailianpressWeb&os=web&rn={limit*2}")
    if not data: return []
    items = []
    for i in data.get('data',{}).get('roll_data',[]):
        title = i.get('title','') or re.sub(r'<[^>]+>','',i.get('content',''))[:80]
        items.append({"source":"财联社","title":title,"url":f"https://www.cls.cn/detail/{i.get('id','')}","score":"","time":""})
    return filt(items, keyword)[:limit]

# ---- 数据源注册 ----

SOURCES = {
    "hackernews": fetch_hackernews, "github": fetch_github, "v2ex": fetch_v2ex,
    "weibo": fetch_weibo, "zhihu": fetch_zhihu, "36kr": fetch_36kr,
    "baidu": fetch_baidu, "juejin": fetch_juejin, "sspai": fetch_sspai,
    "ithome": fetch_ithome, "producthunt": fetch_producthunt,
    "bilibili": fetch_bilibili, "douyin": fetch_douyin, "toutiao": fetch_toutiao,
    "tencent": fetch_tencent, "thepaper": fetch_thepaper, "hupu": fetch_hupu,
    "wallstreetcn": fetch_wallstreetcn, "cls": fetch_cls,
}

GROUPS = {
    "tech": ["hackernews","github","v2ex","sspai","juejin","ithome","producthunt"],
    "china": ["weibo","zhihu","baidu","douyin","bilibili","toutiao","tencent","thepaper","hupu"],
    "finance": ["36kr","wallstreetcn","cls"],
    "all": list(SOURCES.keys()),
}

def main():
    parser = argparse.ArgumentParser(description='热点新闻采集')
    parser.add_argument('--source', required=True, help='数据源名称或分组(tech/china/finance/all)')
    parser.add_argument('--limit', type=int, default=20)
    parser.add_argument('--keyword', help='逗号分隔的关键词过滤')
    parser.add_argument('--deep', action='store_true', help='深度抓取(预留)')
    parser.add_argument('--list-sources', action='store_true', help='列出所有数据源')
    args = parser.parse_args()

    if args.list_sources:
        for name in sorted(SOURCES.keys()):
            print(name)
        return

    source = args.source.lower()
    if source in GROUPS:
        sources = GROUPS[source]
    elif source in SOURCES:
        sources = [source]
    else:
        sys.stderr.write(f"未知数据源: {source}\n可用: {', '.join(sorted(SOURCES.keys()))}\n分组: {', '.join(GROUPS.keys())}\n")
        sys.exit(1)

    all_items = []
    for s in sources:
        sys.stderr.write(f"[采集] {s}...\n")
        try:
            items = SOURCES[s](args.limit, args.keyword)
            sys.stderr.write(f"[采集] {s} → {len(items)} 条\n")
            all_items.extend(items)
        except Exception as e:
            sys.stderr.write(f"[采集] {s} 失败: {e}\n")

    print(json.dumps(all_items, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
