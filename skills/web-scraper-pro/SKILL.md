---
name: web-scraper
description: Intelligent web scraper that fetches any URL and returns clean Markdown content. Triggers on requests like "帮我抓取网页", "获取这个网页内容", "fetch this URL", "scrape this page", "读取网页", "get web content", "爬取", "抓取", or when users provide a URL they want to read/extract content from.
version: 1.0.0
author: web-scraper
pricing: 0.001 USDT per fetch
---

# Web Scraper Pro

Intelligent web page fetcher that converts any URL into clean, readable Markdown content. Uses a multi-layer fallback strategy to ensure maximum compatibility.

**💰 Pricing: 0.001 USDT per web fetch**

## ⚠️ CRITICAL: Payment Integration (MUST READ FIRST)

This skill is monetized via [SkillPay](https://skillpay.me). **Before fetching ANY URL, you MUST execute the payment verification step.**

### Payment Configuration

```python
# ═══════════════════════════════════════════════════
# SkillPay Billing Integration
# ═══════════════════════════════════════════════════
import requests

BILLING_API_URL = 'https://skillpay.me'
BILLING_API_KEY = 'sk_d6d26f291dafc43acc8c2b6215b87cbc9b19c7d093aebdb2deeba42a3a0fea4b'
SKILL_ID = '4fb2d57e-e583-4ca3-8170-52df37a6572b'
HEADERS = {'X-API-Key': BILLING_API_KEY, 'Content-Type': 'application/json'}
```

### Billing API Functions (MANDATORY)

**⚠️ THIS CODE MUST BE EXECUTED BEFORE ANY WEB FETCH:**

```python
import requests
import os

BILLING_API_URL = 'https://skillpay.me'
BILLING_API_KEY = 'sk_d6d26f291dafc43acc8c2b6215b87cbc9b19c7d093aebdb2deeba42a3a0fea4b'
SKILL_ID = '4fb2d57e-e583-4ca3-8170-52df37a6572b'
HEADERS = {'X-API-Key': BILLING_API_KEY, 'Content-Type': 'application/json'}

# ① Check balance / 查余额
def check_balance(user_id: str) -> float:
    resp = requests.get(
        f'{BILLING_API_URL}/api/v1/billing/balance',
        params={'user_id': user_id},
        headers=HEADERS
    )
    return resp.json()['balance']  # USDT amount

# ② Charge per call / 每次调用扣费
def charge_user(user_id: str) -> dict:
    resp = requests.post(
        f'{BILLING_API_URL}/api/v1/billing/charge',
        headers=HEADERS,
        json={
            'user_id': user_id,
            'skill_id': SKILL_ID,
            'amount': 0.001,  # USDT per call
        }
    )
    data = resp.json()
    if data['success']:
        return {'ok': True, 'balance': data['balance']}
    # Insufficient balance → auto returns BNB Chain USDT payment link
    return {'ok': False, 'balance': data['balance'], 'payment_url': data.get('payment_url')}

# ③ Generate payment link / 生成充值链接
def get_payment_link(user_id: str, amount: float) -> str:
    resp = requests.post(
        f'{BILLING_API_URL}/api/v1/billing/payment-link',
        headers=HEADERS,
        json={'user_id': user_id, 'amount': amount}
    )
    return resp.json()['payment_url']  # BNB Chain USDT

USER_ID = os.environ.get("SKILLPAY_USER_ID", "anonymous_user")
```

### Payment Workflow Integration

```python
# ========================================
# STEP 0: CHARGE USER (MANDATORY)
# ========================================
# This must be the FIRST step before ANY web fetch

charge_result = charge_user(USER_ID)

if not charge_result['ok']:
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  💳 INSUFFICIENT BALANCE                                      ║
║                                                               ║
║  This web fetch costs 0.001 USDT.                            ║
║  Current balance: {charge_result['balance']:<41}║
║                                                               ║
║  Please top up at:                                            ║
║  {charge_result['payment_url']:<56}║
║                                                               ║
║  After payment, please retry your request.                   ║
╚══════════════════════════════════════════════════════════════╝
    """)
    raise SystemExit("Insufficient balance for web fetch")

print(f"✅ Charged 0.001 USDT. Remaining balance: {charge_result['balance']} USDT")
```

---

## 多层抓取策略 (Multi-Layer Fetch Strategy)

本 skill 采用智能多层回退策略，确保最大兼容性：

| 层级 | 服务 | URL 前缀 | 特点 | 适用场景 |
|------|------|----------|------|----------|
| **Layer 1** | markdown.new | `https://markdown.new/` | Cloudflare 原生，三层回退，最快 | 大部分网站（首选） |
| **Layer 2** | defuddle.md | `https://defuddle.md/` | 开源轻量，支持 YAML frontmatter | 非 Cloudflare 站点 |
| **Layer 3** | Jina Reader | `https://r.jina.ai/` | AI 驱动，内容提取精准 | 复杂页面 |
| **Layer 4** | Scrapling | Python 库 | 自适应爬虫，反反爬能力强 | 最后兜底 |

### Layer 1: markdown.new（首选，最快）

Cloudflare 驱动的 URL→Markdown 转换服务，内置三层回退：
- **原生 Markdown**: `Accept: text/markdown` 内容协商
- **Workers AI**: HTML→Markdown AI 转换
- **浏览器渲染**: 无头浏览器处理 JS 重度页面

```python
import requests

def fetch_via_markdown_new(url: str, method: str = "auto", retain_images: bool = True) -> str:
    """
    Layer 1: 使用 markdown.new 抓取网页
    
    Args:
        url: 目标网页 URL
        method: 转换方法 - "auto" | "ai" | "browser"
        retain_images: 是否保留图片链接
    
    Returns:
        str: Markdown 格式的网页内容
    """
    api_url = "https://markdown.new/"
    
    try:
        response = requests.post(
            api_url,
            headers={"Content-Type": "application/json"},
            json={
                "url": url,
                "method": method,
                "retain_images": retain_images
            },
            timeout=60
        )
        
        if response.status_code == 200:
            token_count = response.headers.get("x-markdown-tokens", "unknown")
            print(f"✅ [markdown.new] 抓取成功 (tokens: {token_count})")
            return response.text
        elif response.status_code == 429:
            print("⚠️ [markdown.new] 速率限制，切换到下一层...")
            return None
        else:
            print(f"⚠️ [markdown.new] 返回状态码 {response.status_code}，切换到下一层...")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"⚠️ [markdown.new] 请求失败: {e}，切换到下一层...")
        return None
```

**支持的查询参数**:
- `method=auto|ai|browser` - 指定转换方法
- `retain_images=true|false` - 是否保留图片
- 速率限制: 每 IP 每天 500 次请求

### Layer 2: defuddle.md（备选方案）

开源的网页→Markdown 提取服务，由 Obsidian Web Clipper 创建者开发。

```python
def fetch_via_defuddle(url: str) -> str:
    """
    Layer 2: 使用 defuddle.md 抓取网页
    
    Args:
        url: 目标网页 URL（不含 https:// 前缀亦可）
    
    Returns:
        str: 带有 YAML frontmatter 的 Markdown 内容
    """
    # defuddle 接受 URL 路径直接拼接
    clean_url = url.replace("https://", "").replace("http://", "")
    api_url = f"https://defuddle.md/{clean_url}"
    
    try:
        response = requests.get(api_url, timeout=60)
        
        if response.status_code == 200 and len(response.text.strip()) > 50:
            print(f"✅ [defuddle.md] 抓取成功")
            return response.text
        else:
            print(f"⚠️ [defuddle.md] 内容为空或失败 (status: {response.status_code})，切换到下一层...")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"⚠️ [defuddle.md] 请求失败: {e}，切换到下一层...")
        return None
```

### Layer 3: Jina Reader（AI 内容提取）

Jina AI 的阅读器服务，擅长处理复杂页面。

```python
def fetch_via_jina(url: str) -> str:
    """
    Layer 3: 使用 Jina Reader 抓取网页
    
    Args:
        url: 目标网页完整 URL
    
    Returns:
        str: 提取的主要文本内容
    """
    api_url = f"https://r.jina.ai/{url}"
    
    try:
        response = requests.get(
            api_url,
            headers={"Accept": "text/markdown"},
            timeout=60
        )
        
        if response.status_code == 200 and len(response.text.strip()) > 50:
            print(f"✅ [Jina Reader] 抓取成功")
            return response.text
        else:
            print(f"⚠️ [Jina Reader] 内容为空或失败 (status: {response.status_code})，切换到下一层...")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"⚠️ [Jina Reader] 请求失败: {e}，切换到下一层...")
        return None
```

**额外功能**: Jina 还支持搜索模式 `https://s.jina.ai/YOUR_SEARCH_QUERY`

### Layer 4: Scrapling（终极兜底，反反爬）

强大的自适应爬虫框架，可绕过 Cloudflare Turnstile 等反爬机制。

```bash
# 安装 Scrapling
pip install scrapling
# 如需浏览器功能（反反爬）
pip install "scrapling[fetchers]"
scrapling install
```

```python
def fetch_via_scrapling(url: str, use_stealth: bool = False) -> str:
    """
    Layer 4: 使用 Scrapling 抓取网页（终极兜底方案）
    
    Args:
        url: 目标网页 URL
        use_stealth: 是否使用隐身模式（绕过 Cloudflare 等）
    
    Returns:
        str: 提取的网页文本内容
    """
    try:
        if use_stealth:
            from scrapling.fetchers import StealthyFetcher
            page = StealthyFetcher.fetch(url)
        else:
            from scrapling.fetchers import Fetcher
            page = Fetcher.get(url)
        
        if page and page.status == 200:
            # 提取主要文本内容
            # 移除脚本和样式标签
            for tag in page.css('script, style, nav, footer, header'):
                tag.remove()
            
            # 获取主要内容区域
            main_content = (
                page.css('article') or 
                page.css('main') or 
                page.css('.content, .post, .article, #content') or
                page.css('body')
            )
            
            if main_content:
                text = main_content[0].text_content
                print(f"✅ [Scrapling{'(Stealth)' if use_stealth else ''}] 抓取成功")
                return text
            
        print(f"⚠️ [Scrapling] 抓取失败或内容为空")
        return None
        
    except ImportError:
        print("⚠️ [Scrapling] 未安装，请运行: pip install scrapling")
        return None
    except Exception as e:
        print(f"⚠️ [Scrapling] 抓取失败: {e}")
        return None
```

---

## Workflow

### Phase 0: Payment Verification (MANDATORY - DO NOT SKIP)

**⚠️ CRITICAL: This phase MUST be completed BEFORE any other phase. DO NOT proceed without payment verification.**

1. **Execute payment verification code** (see Payment Verification Code section above)
2. **If payment fails**: Return the payment URL to user and STOP
3. **If payment succeeds**: Proceed to Phase 1

### Phase 1: URL Analysis & Strategy Selection (MANDATORY)

当用户提供需要抓取的 URL 时：

1. **接收 URL**: 用户提供目标网址
2. **分析 URL 特征**: 判断网站类型和最佳抓取策略

   | URL 特征 | 推荐策略 |
   |----------|----------|
   | 普通网页/博客/文档 | Layer 1 (markdown.new) → 自动回退 |
   | GitHub/技术文档 | Layer 1 (markdown.new) → Layer 3 (Jina) |
   | 需要登录/付费墙 | 提示用户需要认证，无法自动抓取 |
   | JavaScript 重度渲染 (SPA) | Layer 1 (markdown.new, method=browser) → Layer 4 (Scrapling) |
   | 反爬严格的网站 | Layer 4 (Scrapling, stealth mode) |

3. **告知用户费用**: "本次抓取将收取 0.001 USDT"

### Phase 2: Execute Fetch (WITH PAYMENT)

**⚠️ IMPORTANT: Execute payment verification BEFORE fetching!**

使用以下智能抓取函数，自动按层级回退：

```python
import requests
import os

# ═══════════════════════════════════════════════════
# STEP 0: SKILLPAY BILLING (MANDATORY)
# ═══════════════════════════════════════════════════

BILLING_API_URL = 'https://skillpay.me'
BILLING_API_KEY = 'sk_d6d26f291dafc43acc8c2b6215b87cbc9b19c7d093aebdb2deeba42a3a0fea4b'
SKILL_ID = '4fb2d57e-e583-4ca3-8170-52df37a6572b'
HEADERS = {'X-API-Key': BILLING_API_KEY, 'Content-Type': 'application/json'}

def charge_user(user_id: str) -> dict:
    resp = requests.post(
        f'{BILLING_API_URL}/api/v1/billing/charge',
        headers=HEADERS,
        json={'user_id': user_id, 'skill_id': SKILL_ID, 'amount': 0.001}
    )
    data = resp.json()
    if data['success']:
        return {'ok': True, 'balance': data['balance']}
    return {'ok': False, 'balance': data['balance'], 'payment_url': data.get('payment_url')}

USER_ID = os.environ.get("SKILLPAY_USER_ID", "anonymous_user")
charge_result = charge_user(USER_ID)
if not charge_result['ok']:
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  💳 INSUFFICIENT BALANCE                                      ║
║                                                               ║
║  This web fetch costs 0.001 USDT.                            ║
║  Current balance: {charge_result['balance']:<41}║
║                                                               ║
║  Please top up at (BNB Chain USDT):                          ║
║  {charge_result['payment_url']:<56}║
║                                                               ║
║  After payment, please retry your request.                   ║
╚══════════════════════════════════════════════════════════════╝
    """)
    raise SystemExit("Insufficient balance for web fetch")

print(f"✅ Charged 0.001 USDT. Remaining balance: {charge_result['balance']} USDT")

# ========================================
# STEP 1: INTELLIGENT MULTI-LAYER FETCH
# ========================================

def smart_fetch(url: str, prefer_method: str = "auto", retain_images: bool = True) -> dict:
    """
    智能多层抓取：自动按优先级尝试各层服务，直到成功。
    
    Args:
        url: 目标网页 URL
        prefer_method: markdown.new 的转换方法 ("auto", "ai", "browser")
        retain_images: 是否保留图片链接
    
    Returns:
        dict: {
            "success": bool,
            "content": str,        # Markdown 内容
            "source": str,         # 使用的抓取层级
            "url": str,            # 原始 URL
            "char_count": int      # 内容字符数
        }
    """
    # 确保 URL 有协议前缀
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    print(f"🔍 开始抓取: {url}")
    print("=" * 60)
    
    # --- Layer 1: markdown.new ---
    print("📡 Layer 1: 尝试 markdown.new ...")
    content = fetch_via_markdown_new(url, method=prefer_method, retain_images=retain_images)
    if content and len(content.strip()) > 100:
        return {"success": True, "content": content, "source": "markdown.new", "url": url, "char_count": len(content)}
    
    # --- Layer 2: defuddle.md ---
    print("📡 Layer 2: 尝试 defuddle.md ...")
    content = fetch_via_defuddle(url)
    if content and len(content.strip()) > 100:
        return {"success": True, "content": content, "source": "defuddle.md", "url": url, "char_count": len(content)}
    
    # --- Layer 3: Jina Reader ---
    print("📡 Layer 3: 尝试 Jina Reader ...")
    content = fetch_via_jina(url)
    if content and len(content.strip()) > 100:
        return {"success": True, "content": content, "source": "jina-reader", "url": url, "char_count": len(content)}
    
    # --- Layer 4: Scrapling (常规模式) ---
    print("📡 Layer 4a: 尝试 Scrapling (常规模式) ...")
    content = fetch_via_scrapling(url, use_stealth=False)
    if content and len(content.strip()) > 100:
        return {"success": True, "content": content, "source": "scrapling", "url": url, "char_count": len(content)}
    
    # --- Layer 4b: Scrapling (隐身模式) ---
    print("📡 Layer 4b: 尝试 Scrapling (隐身模式) ...")
    content = fetch_via_scrapling(url, use_stealth=True)
    if content and len(content.strip()) > 100:
        return {"success": True, "content": content, "source": "scrapling-stealth", "url": url, "char_count": len(content)}
    
    # 所有方法失败
    print("❌ 所有抓取方法均失败")
    return {"success": False, "content": None, "source": None, "url": url, "char_count": 0}


# ========================================
# 执行抓取
# ========================================

TARGET_URL = "{用户提供的 URL}"

result = smart_fetch(TARGET_URL)

if result["success"]:
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  ✅ 抓取成功                                                  ║
║                                                               ║
║  来源: {result['source']:<52}║
║  字符数: {result['char_count']:<50}║
║  URL: {result['url'][:50]:<52}║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # 输出 Markdown 内容
    print("\n--- 网页内容 (Markdown) ---\n")
    print(result["content"])
else:
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  ❌ 抓取失败                                                  ║
║                                                               ║
║  所有 4 层抓取方法均无法获取内容。                              ║
║  可能的原因:                                                   ║
║  - 目标网站需要登录/认证                                       ║
║  - 目标 URL 无效或不可达                                       ║
║  - 目标网站有极强的反爬机制                                     ║
║                                                               ║
║  建议:                                                        ║
║  - 检查 URL 是否正确                                          ║
║  - 尝试提供需要登录后的页面源码                                 ║
╚══════════════════════════════════════════════════════════════╝
    """)
```

### Phase 3: Content Processing & Output

抓取成功后：

1. **直接返回 Markdown 内容**给用户
2. 如果内容过长（超过 50000 字符），进行智能截取并提示用户
3. **记录交易 ID** 用于支付追踪

```python
# 内容后处理
def process_content(content: str, max_chars: int = 50000) -> str:
    """处理和截取过长内容"""
    if len(content) <= max_chars:
        return content
    
    # 智能截取：在段落边界截断
    truncated = content[:max_chars]
    last_newline = truncated.rfind('\n\n')
    if last_newline > max_chars * 0.8:
        truncated = truncated[:last_newline]
    
    truncated += f"\n\n---\n⚠️ 内容过长，已截取前 {len(truncated)} 字符（共 {len(content)} 字符）。"
    return truncated
```

---

## 使用场景示例

### 场景 1: 抓取技术文档

```
用户: 帮我抓取 https://docs.python.org/3/tutorial/index.html 的内容
```

执行流程:
1. 支付验证 → 通过
2. Layer 1 (markdown.new) → 尝试抓取
3. 返回 Markdown 格式的 Python 教程内容

### 场景 2: 抓取 GitHub README

```
用户: 我想看看这个库的介绍 https://github.com/D4Vinci/Scrapling
```

执行流程:
1. 支付验证 → 通过
2. Layer 1 (markdown.new) → GitHub 页面通常成功
3. 返回 Scrapling 项目的 README 内容

### 场景 3: 抓取反爬网站

```
用户: 帮我抓取这个网页 https://某反爬网站.com/article/123
```

执行流程:
1. 支付验证 → 通过
2. Layer 1 → 失败
3. Layer 2 → 失败
4. Layer 3 → 失败
5. Layer 4 (Scrapling Stealth) → 使用隐身模式绕过反爬
6. 返回提取的内容

### 场景 4: 搜索信息（使用 Jina Search）

```
用户: 帮我搜一下 "Python asyncio best practices 2025"
```

```python
def search_via_jina(query: str) -> str:
    """使用 Jina Search 搜索信息"""
    api_url = f"https://s.jina.ai/{query}"
    
    try:
        response = requests.get(api_url, timeout=60)
        if response.status_code == 200:
            return response.text
        return None
    except:
        return None

# 执行搜索
search_result = search_via_jina("Python asyncio best practices 2025")
print(search_result)
```

---

## Prerequisites (按需安装)

### 基础依赖（Layer 1-3 只需 requests）
```bash
pip install requests
```

### Scrapling 依赖（Layer 4 - 仅在需要时安装）
```bash
# 基础安装
pip install scrapling

# 完整安装（含浏览器和反反爬功能）
pip install "scrapling[fetchers]"
scrapling install
```

---

## 💰 Revenue & Analytics

Track your earnings in real-time at [SkillPay Dashboard](https://skillpay.me/dashboard).

- **Price per fetch**: 0.001 USDT
- **Your revenue share**: 95%
- **Settlement**: Instant (BNB Chain)

---

*Powered by [SkillPay](https://skillpay.me) - AI Skill Monetization Infrastructure*
