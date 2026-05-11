---
name: duckduckgo-search
description: Performs web searches using DuckDuckGo to retrieve real-time information from the internet. Use when the user needs to search for current events, documentation, tutorials, or any information that requires web search capabilities.
allowed-tools: Bash(duckduckgo-search:*), Bash(python:*), Bash(pip:*), Bash(uv:*)
---

# DuckDuckGo Web Search Skill

这个技能通过 DuckDuckGo 搜索引擎实现网络搜索功能，帮助获取实时信息。

## 功能特性

- 🔍 基于 DuckDuckGo 的隐私友好型搜索
- 📰 支持新闻搜索
- 🖼️ 支持图片搜索
- 📹 支持视频搜索
- 🌐 无需 API Key，免费使用
- 🔒 保护隐私，不追踪用户

## 安装

```bash
# 使用 uv 安装（推荐）
uv pip install duckduckgo-search

# 或使用 pip 安装
pip install duckduckgo-search
```

## 快速开始

### 命令行方式

```bash
# 基础文本搜索
python -c "
from duckduckgo_search import DDGS

with DDGS() as ddgs:
    results = list(ddgs.text('Python tutorial', max_results=5))
    for r in results:
        print(f\"标题: {r['title']}\")
        print(f\"链接: {r['href']}\")
        print(f\"摘要: {r['body']}\")
        print('---')
"
```

## 搜索类型

### 1. 文本搜索 (Text Search)

最常用的搜索方式，返回网页结果：

```bash
python -c "
from duckduckgo_search import DDGS

query = 'your search query'

with DDGS() as ddgs:
    results = list(ddgs.text(
        query,
        region='cn-zh',      # 地区设置：cn-zh(中国), us-en(美国), wt-wt(全球)
        safesearch='moderate', # 安全搜索：on, moderate, off
        timelimit='m',       # 时间范围：d(天), w(周), m(月), y(年), None(不限)
        max_results=10       # 最大结果数
    ))
    
    for i, r in enumerate(results, 1):
        print(f\"{i}. {r['title']}\")
        print(f\"   URL: {r['href']}\")
        print(f\"   摘要: {r['body'][:100]}...\")
        print()
"
```

### 2. 新闻搜索 (News Search)

搜索最新新闻：

```bash
python -c "
from duckduckgo_search import DDGS

with DDGS() as ddgs:
    results = list(ddgs.news(
        'AI technology',
        region='wt-wt',
        safesearch='moderate',
        timelimit='d',       # d=过去24小时, w=过去一周, m=过去一月
        max_results=10
    ))
    
    for r in results:
        print(f\"📰 {r['title']}\")
        print(f\"   来源: {r['source']}\")
        print(f\"   时间: {r['date']}\")
        print(f\"   链接: {r['url']}\")
        print()
"
```

### 3. 图片搜索 (Image Search)

搜索图片资源：

```bash
python -c "
from duckduckgo_search import DDGS

with DDGS() as ddgs:
    results = list(ddgs.images(
        'cute cats',
        region='wt-wt',
        safesearch='moderate',
        size='Medium',       # Small, Medium, Large, Wallpaper
        type_image='photo',  # photo, clipart, gif, transparent, line
        layout='Square',     # Square, Tall, Wide
        max_results=10
    ))
    
    for r in results:
        print(f\"🖼️ {r['title']}\")
        print(f\"   图片: {r['image']}\")
        print(f\"   缩略图: {r['thumbnail']}\")
        print(f\"   来源: {r['source']}\")
        print()
"
```

### 4. 视频搜索 (Video Search)

搜索视频内容：

```bash
python -c "
from duckduckgo_search import DDGS

with DDGS() as ddgs:
    results = list(ddgs.videos(
        'Python programming',
        region='wt-wt',
        safesearch='moderate',
        timelimit='w',       # d, w, m
        resolution='high',   # high, standard
        duration='medium',   # short, medium, long
        max_results=10
    ))
    
    for r in results:
        print(f\"📹 {r['title']}\")
        print(f\"   时长: {r.get('duration', 'N/A')}\")
        print(f\"   来源: {r['publisher']}\")
        print(f\"   链接: {r['content']}\")
        print()
"
```

### 5. 即时回答 (Instant Answers)

获取 DuckDuckGo 的即时回答：

```bash
python -c "
from duckduckgo_search import DDGS

with DDGS() as ddgs:
    results = ddgs.answers('what is python programming language')
    
    for r in results:
        print(f\"📚 {r['text']}\")
        print(f\"   来源: {r.get('url', 'DuckDuckGo')}\")
"
```

### 6. 建议搜索 (Suggestions)

获取搜索建议：

```bash
python -c "
from duckduckgo_search import DDGS

with DDGS() as ddgs:
    suggestions = list(ddgs.suggestions('python'))
    
    print('🔍 搜索建议:')
    for s in suggestions:
        print(f\"   - {s['phrase']}\")
"
```

### 7. 地图搜索 (Maps Search)

搜索地点信息：

```bash
python -c "
from duckduckgo_search import DDGS

with DDGS() as ddgs:
    results = list(ddgs.maps(
        'coffee shop',
        place='Beijing, China',
        max_results=10
    ))
    
    for r in results:
        print(f\"📍 {r['title']}\")
        print(f\"   地址: {r['address']}\")
        print(f\"   电话: {r.get('phone', 'N/A')}\")
        print(f\"   坐标: {r['latitude']}, {r['longitude']}\")
        print()
"
```

## 实用脚本

### 通用搜索函数

创建一个可复用的搜索脚本：

```bash
python -c "
from duckduckgo_search import DDGS
import json

def web_search(query, search_type='text', max_results=5, region='wt-wt', timelimit=None):
    '''
    执行 DuckDuckGo 搜索
    
    参数:
        query: 搜索关键词
        search_type: 搜索类型 (text, news, images, videos)
        max_results: 最大结果数
        region: 地区 (cn-zh, us-en, wt-wt)
        timelimit: 时间限制 (d, w, m, y)
    '''
    with DDGS() as ddgs:
        if search_type == 'text':
            results = list(ddgs.text(query, region=region, timelimit=timelimit, max_results=max_results))
        elif search_type == 'news':
            results = list(ddgs.news(query, region=region, timelimit=timelimit, max_results=max_results))
        elif search_type == 'images':
            results = list(ddgs.images(query, region=region, max_results=max_results))
        elif search_type == 'videos':
            results = list(ddgs.videos(query, region=region, timelimit=timelimit, max_results=max_results))
        else:
            results = []
    
    return results

# 使用示例
query = 'Python 3.12 new features'
results = web_search(query, search_type='text', max_results=5)

print(f'🔍 搜索: {query}')
print(f'📊 找到 {len(results)} 个结果')
print()

for i, r in enumerate(results, 1):
    print(f\"{i}. {r['title']}\")
    print(f\"   {r['href']}\")
    print(f\"   {r['body'][:150]}...\")
    print()
"
```

### 搜索并保存结果

```bash
python -c "
from duckduckgo_search import DDGS
import json
from datetime import datetime

query = 'latest tech news'
output_file = f'search_results_{datetime.now().strftime(\"%Y%m%d_%H%M%S\")}.json'

with DDGS() as ddgs:
    results = list(ddgs.text(query, max_results=10))

# 保存到 JSON 文件
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'query': query,
        'timestamp': datetime.now().isoformat(),
        'results': results
    }, f, ensure_ascii=False, indent=2)

print(f'✅ 搜索结果已保存到: {output_file}')
print(f'📊 共 {len(results)} 条结果')
"
```

### 多关键词批量搜索

```bash
python -c "
from duckduckgo_search import DDGS
import time

queries = [
    'Python best practices 2024',
    'React vs Vue 2024',
    'AI development tools'
]

all_results = {}

with DDGS() as ddgs:
    for query in queries:
        print(f'🔍 搜索: {query}')
        results = list(ddgs.text(query, max_results=3))
        all_results[query] = results
        print(f'   找到 {len(results)} 个结果')
        time.sleep(1)  # 避免请求过快

print()
print('=' * 50)
print('📊 搜索汇总')
print('=' * 50)

for query, results in all_results.items():
    print(f'\n🔎 {query}:')
    for i, r in enumerate(results, 1):
        print(f\"   {i}. {r['title'][:60]}...\")
"
```

## 参数说明

### 地区代码 (region)

| 代码 | 地区 |
|------|------|
| `cn-zh` | 中国 |
| `us-en` | 美国 |
| `uk-en` | 英国 |
| `jp-jp` | 日本 |
| `kr-kr` | 韩国 |
| `wt-wt` | 全球 (无地区限制) |

### 时间限制 (timelimit)

| 值 | 含义 |
|----|------|
| `d` | 过去 24 小时 |
| `w` | 过去一周 |
| `m` | 过去一月 |
| `y` | 过去一年 |
| `None` | 不限制 |

### 安全搜索 (safesearch)

| 值 | 含义 |
|----|------|
| `on` | 严格过滤 |
| `moderate` | 适度过滤 (默认) |
| `off` | 关闭过滤 |

## 错误处理

```bash
python -c "
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import DuckDuckGoSearchException

try:
    with DDGS() as ddgs:
        results = list(ddgs.text('test query', max_results=5))
        print(f'✅ 搜索成功，找到 {len(results)} 个结果')
except DuckDuckGoSearchException as e:
    print(f'❌ 搜索出错: {e}')
except Exception as e:
    print(f'❌ 未知错误: {e}')
"
```

## 使用代理

如果需要使用代理：

```bash
python -c "
from duckduckgo_search import DDGS

# 设置代理
proxy = 'http://127.0.0.1:7890'  # 替换为你的代理地址

with DDGS(proxy=proxy) as ddgs:
    results = list(ddgs.text('test query', max_results=5))
    print(f'通过代理搜索成功，找到 {len(results)} 个结果')
"
```

## 常见问题

**安装失败？**
```bash
# 确保 pip 是最新版本
pip install --upgrade pip
pip install duckduckgo-search

# 或使用 uv
uv pip install duckduckgo-search
```

**搜索无结果？**
```bash
# 检查网络连接
# 尝试使用代理
# 减少搜索关键词复杂度
# 检查地区设置是否正确
```

**请求被限制？**
```bash
# 在多次搜索之间添加延迟
import time
time.sleep(1)  # 等待 1 秒

# 减少单次请求的结果数量
max_results=5  # 而不是 50
```

## 与其他工具集成

### 结合 browser-use 获取详细内容

```bash
# 1. 先用 DuckDuckGo 搜索
python -c "
from duckduckgo_search import DDGS

with DDGS() as ddgs:
    results = list(ddgs.text('Python async tutorial', max_results=1))
    if results:
        url = results[0]['href']
        print(f'URL: {url}')
"

# 2. 用 browser-use 打开并获取详细内容
browser-use open <url_from_search>
browser-use state
```

## 注意事项

⚠️ **使用建议**：

1. **遵守使用频率限制**：避免短时间内大量请求
2. **合理设置结果数量**：不要一次请求过多结果
3. **添加适当延迟**：批量搜索时在请求之间添加 `time.sleep()`
4. **处理异常情况**：始终添加错误处理代码
5. **尊重版权**：搜索结果仅供参考，注意内容版权
