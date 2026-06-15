#!/usr/bin/env python3
"""
1688 商品搜索脚本（增强版）
支持9个核心接口：类目查询、关键词搜索、图片搜索、商品详情等
新增功能：当检测到"图搜同款"、"找同款"等命令时，自动调用图片搜索接口
"""

import os
import sys
import json
import argparse
import requests
import base64
import re
from urllib.parse import urlparse

# 添加 scripts 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.auth import get_access_token, sign_request_hmac_sha1
from scripts.image_utils import compress_image_if_needed

# API 基础URL
BASE_URL = "https://gw.open.1688.com/openapi"

def get_app_credentials():
    """获取应用凭证"""
    app_key = os.getenv('ALI1688_APP_KEY')
    app_secret = os.getenv('ALI1688_APP_SECRET')
    refresh_token = os.getenv('ALI1688_REFRESH_TOKEN')
    access_token = os.getenv('ALI1688_ACCESS_TOKEN')
    
    if not app_key or not app_secret:
        raise Exception("Missing ALI1688_APP_KEY or ALI1688_APP_SECRET")
    
    return app_key, app_secret, refresh_token, access_token

def is_image_url(url):
    """检查是否为有效的图片URL"""
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # 检查常见的图片扩展名
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        path_lower = parsed.path.lower()
        return any(path_lower.endswith(ext) for ext in image_extensions)
    except:
        return False

def download_image_from_url(image_url, local_path):
    """从URL下载图片到本地"""
    try:
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # 检查响应内容类型
        content_type = response.headers.get('content-type', '').lower()
        if 'image' not in content_type:
            # 如果没有content-type，尝试通过文件扩展名判断
            if not is_image_url(image_url):
                raise Exception("URL does not appear to be an image")
        
        with open(local_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        raise Exception(f"Failed to download image from URL: {str(e)}")

def upload_image(image_path):
    """上传图片获取imageId（自动压缩大于300KB的图片）"""
    app_key, app_secret, refresh_token, access_token = get_app_credentials()
    token = get_access_token(app_key, app_secret, refresh_token, access_token)
    
    # 检查并压缩图片（如果需要）
    compressed_path, was_compressed = compress_image_if_needed(image_path, max_size_kb=300)
    
    try:
        # 读取（可能已压缩的）图片并转换为base64
        with open(compressed_path, 'rb') as f:
            image_data = f.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
        
        upload_params = {
            'imageBase64': base64_image
        }
        
        params = {
            'uploadImageParam': json.dumps(upload_params, separators=(',', ':')),
            'access_token': token
        }
        
        url_path = f"param2/1/com.alibaba.fenxiao.crossborder/product.image.upload/{app_key}"
        sign = sign_request_hmac_sha1(url_path, params, app_secret)
        params['_aop_signature'] = sign
        
        url = f"{BASE_URL}/{url_path}"
        response = requests.post(url, data=params, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        # 提取imageId
        if 'result' in result and isinstance(result['result'], str):
            return result['result']
        else:
            raise Exception("Failed to get imageId from upload response")
        
    finally:
        # 如果图片被压缩了，清理临时文件
        if was_compressed and os.path.exists(compressed_path):
            try:
                os.remove(compressed_path)
            except OSError:
                pass

def image_search_by_url(image_url, country='en', begin_page=1, page_size=20):
    """通过图片URL进行图片搜索"""
    # 创建临时文件路径
    temp_image_path = "/tmp/1688_search_temp_image.jpg"
    
    try:
        # 下载图片
        download_image_from_url(image_url, temp_image_path)
        
        # 上传图片获取imageId
        image_id = upload_image(temp_image_path)
        
        # 使用imageId进行图片搜索
        app_key, app_secret, refresh_token, access_token = get_app_credentials()
        token = get_access_token(app_key, app_secret, refresh_token, access_token)
        
        search_params = {
            'imageId': image_id,
            'country': country,
            'beginPage': begin_page,
            'pageSize': page_size
        }
        
        params = {
            'offerQueryParam': json.dumps(search_params, separators=(',', ':')),
            'access_token': token
        }
        
        url_path = f"param2/1/com.alibaba.fenxiao.crossborder/product.search.imageQuery/{app_key}"
        sign = sign_request_hmac_sha1(url_path, params, app_secret)
        params['_aop_signature'] = sign
        
        url = f"{BASE_URL}/{url_path}"
        response = requests.post(url, data=params, timeout=15)
        response.raise_for_status()
        return response.json()
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_image_path):
            try:
                os.remove(temp_image_path)
            except OSError:
                pass

def smart_search(query, country='en', begin_page=1, page_size=20):
    """
    智能搜索函数
    - 如果query包含图片URL且包含"图搜同款"、"找同款"等关键词，执行图片搜索
    - 否则执行关键词搜索
    """
    # 定义触发图片搜索的关键词
    image_search_keywords = [
        '图搜同款', '找同款', '图片搜', '以图搜', '图片搜索', 
        '同款', '相似款', '类似款', '找相似', '找类似'
    ]
    
    # 检查是否包含图片搜索关键词
    should_use_image_search = any(keyword in query for keyword in image_search_keywords)
    
    # 检查是否包含图片URL
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, query)
    image_urls = [url for url in urls if is_image_url(url)]
    
    if should_use_image_search and image_urls:
        # 使用第一个有效的图片URL进行图片搜索
        return image_search_by_url(image_urls[0], country, begin_page, page_size)
    else:
        # 执行关键词搜索（移除URL和图片搜索关键词）
        clean_query = query
        for url in urls:
            clean_query = clean_query.replace(url, '')
        for keyword in image_search_keywords:
            clean_query = clean_query.replace(keyword, '')
        clean_query = clean_query.strip()
        
        if not clean_query:
            clean_query = "牛仔夹克"  # 默认关键词
        
        return keyword_search(clean_query, country, begin_page, page_size)

def category_query(cate_id=0, language='en'):
    """类目查询"""
    app_key, app_secret, refresh_token, access_token = get_app_credentials()
    token = get_access_token(app_key, app_secret, refresh_token, access_token)
    
    params = {
        'categoryId': str(cate_id),
        'language': language,
        'access_token': token
    }
    
    url_path = f"param2/1/com.alibaba.fenxiao.crossborder/category.translation.getById/{app_key}"
    sign = sign_request_hmac_sha1(url_path, params, app_secret)
    params['_aop_signature'] = sign
    
    url = f"{BASE_URL}/{url_path}"
    response = requests.post(url, data=params, timeout=15)
    response.raise_for_status()
    return response.json()

def keyword_search(keyword, country='en', begin_page=1, page_size=20, filter_param=None, sort_param=None):
    """多语言关键词搜索"""
    app_key, app_secret, refresh_token, access_token = get_app_credentials()
    token = get_access_token(app_key, app_secret, refresh_token, access_token)
    
    search_params = {
        'keyword': keyword,
        'country': country,
        'beginPage': begin_page,
        'pageSize': page_size
    }
    
    if filter_param:
        search_params['filter'] = filter_param
    if sort_param:
        search_params['sort'] = json.loads(sort_param) if isinstance(sort_param, str) else sort_param
    
    params = {
        'offerQueryParam': json.dumps(search_params, separators=(',', ':')),
        'access_token': token
    }
    
    url_path = f"param2/1/com.alibaba.fenxiao.crossborder/product.search.keywordQuery/{app_key}"
    sign = sign_request_hmac_sha1(url_path, params, app_secret)
    params['_aop_signature'] = sign
    
    url = f"{BASE_URL}/{url_path}"
    response = requests.post(url, data=params, timeout=15)
    response.raise_for_status()
    return response.json()

def image_search(image_id, country='en', begin_page=1, page_size=20):
    """多语言图片搜索"""
    app_key, app_secret, refresh_token, access_token = get_app_credentials()
    token = get_access_token(app_key, app_secret, refresh_token, access_token)
    
    search_params = {
        'imageId': image_id,
        'country': country,
        'beginPage': begin_page,
        'pageSize': page_size
    }
    
    params = {
        'offerQueryParam': json.dumps(search_params, separators=(',', ':')),
        'access_token': token
    }
    
    url_path = f"param2/1/com.alibaba.fenxiao.crossborder/product.search.imageQuery/{app_key}"
    sign = sign_request_hmac_sha1(url_path, params, app_secret)
    params['_aop_signature'] = sign
    
    url = f"{BASE_URL}/{url_path}"
    response = requests.post(url, data=params, timeout=15)
    response.raise_for_status()
    return response.json()

def product_detail(offer_id, country='en', out_member_id="1"):
    """多语言商品详情"""
    app_key, app_secret, refresh_token, access_token = get_app_credentials()
    token = get_access_token(app_key, app_secret, refresh_token, access_token)
    
    detail_params = {
        'offerId': int(offer_id),
        'country': country,
        'outMemberId': out_member_id
    }
    
    params = {
        'offerDetailParam': json.dumps(detail_params, separators=(',', ':')),
        'access_token': token
    }
    
    url_path = f"param2/1/com.alibaba.fenxiao.crossborder/product.search.queryProductDetail/{app_key}"
    sign = sign_request_hmac_sha1(url_path, params, app_secret)
    params['_aop_signature'] = sign
    
    url = f"{BASE_URL}/{url_path}"
    response = requests.post(url, data=params, timeout=15)
    response.raise_for_status()
    return response.json()

def shop_search(seller_open_id, country='en', begin_page=1, page_size=20):
    """多语言商品店铺搜索"""
    app_key, app_secret, refresh_token, access_token = get_app_credentials()
    token = get_access_token(app_key, app_secret, refresh_token, access_token)
    
    search_params = {
        'sellerOpenId': seller_open_id,
        'country': country,
        'beginPage': begin_page,
        'pageSize': page_size
    }
    
    params = {
        'searchParam': json.dumps(search_params, separators=(',', ':')),
        'access_token': token
    }
    
    url_path = f"param2/1/com.alibaba.fenxiao.crossborder/product.search.shopSearch/{app_key}"
    sign = sign_request_hmac_sha1(url_path, params, app_secret)
    params['_aop_signature'] = sign
    
    url = f"{BASE_URL}/{url_path}"
    response = requests.post(url, data=params, timeout=15)
    response.raise_for_status()
    return response.json()

def offer_recommend(keyword, country='en', begin_page=1, page_size=20):
    """多语言商品推荐"""
    app_key, app_secret, refresh_token, access_token = get_app_credentials()
    token = get_access_token(app_key, app_secret, refresh_token, access_token)
    
    recommend_params = {
        'keyword': keyword,
        'country': country,
        'beginPage': begin_page,
        'pageSize': page_size
    }
    
    params = {
        'recommendOfferParam': json.dumps(recommend_params, separators=(',', ':')),
        'access_token': token
    }
    
    url_path = f"param2/1/com.alibaba.fenxiao.crossborder/product.search.offerRecommend/{app_key}"
    sign = sign_request_hmac_sha1(url_path, params, app_secret)
    params['_aop_signature'] = sign
    
    url = f"{BASE_URL}/{url_path}"
    response = requests.post(url, data=params, timeout=15)
    response.raise_for_status()
    return response.json()

def search_navigation(keyword, country='en'):
    """多语言搜索导航"""
    app_key, app_secret, refresh_token, access_token = get_app_credentials()
    token = get_access_token(app_key, app_secret, refresh_token, access_token)
    
    nav_params = {
        'keyword': keyword,
        'country': country
    }
    
    params = {
        'navParam': json.dumps(nav_params, separators=(',', ':')),
        'access_token': token
    }
    
    url_path = f"param2/1/com.alibaba.fenxiao.crossborder/product.search.keywordSNQuery/{app_key}"
    sign = sign_request_hmac_sha1(url_path, params, app_secret)
    params['_aop_signature'] = sign
    
    url = f"{BASE_URL}/{url_path}"
    response = requests.post(url, data=params, timeout=15)
    response.raise_for_status()
    return response.json()

def related_recommend(offer_id, language='zh', page_no=1, page_size=10):
    """相关性商品推荐"""
    app_key, app_secret, refresh_token, access_token = get_app_credentials()
    token = get_access_token(app_key, app_secret, refresh_token, access_token)
    
    related_params = {
        'offerId': str(offer_id),
        'language': language,
        'pageNo': page_no,
        'pageSize': page_size
    }
    
    params = {
        'relatedQueryParams': json.dumps(related_params, separators=(',', ':')),
        'access_token': token
    }
    
    url_path = f"param2/1/com.alibaba.fenxiao.crossborder/product.related.recommend/{app_key}"
    sign = sign_request_hmac_sha1(url_path, params, app_secret)
    params['_aop_signature'] = sign
    
    url = f"{BASE_URL}/{url_path}"
    response = requests.post(url, data=params, timeout=15)
    response.raise_for_status()
    return response.json()

def main():
    parser = argparse.ArgumentParser(description='1688 Product Search Skill (Enhanced)')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # 智能搜索（新增）
    smart_parser = subparsers.add_parser('smart-search', help='Smart search (auto-detect image search vs keyword search)')
    smart_parser.add_argument('query', help='Search query (can include image URL and keywords like "图搜同款")')
    smart_parser.add_argument('--country', default='en')
    smart_parser.add_argument('--beginPage', type=int, default=1)
    smart_parser.add_argument('--pageSize', type=int, default=20)
    
    # 类目查询
    category_parser = subparsers.add_parser('category', help='Category query')
    category_parser.add_argument('cate_id', type=int, nargs='?', default=0)
    category_parser.add_argument('--language', default='en')
    
    # 关键词搜索
    keyword_parser = subparsers.add_parser('keyword-search', help='Keyword search')
    keyword_parser.add_argument('keyword', help='Search keyword')
    keyword_parser.add_argument('--country', default='en')
    keyword_parser.add_argument('--beginPage', type=int, default=1)
    keyword_parser.add_argument('--pageSize', type=int, default=20)
    keyword_parser.add_argument('--filter', help='Filter conditions (comma separated)')
    keyword_parser.add_argument('--sort', help='Sort parameter (JSON string)')
    
    # 图片搜索
    image_parser = subparsers.add_parser('image-search', help='Image search')
    image_parser.add_argument('image_id', help='Image ID')
    image_parser.add_argument('--country', default='en')
    image_parser.add_argument('--beginPage', type=int, default=1)
    image_parser.add_argument('--pageSize', type=int, default=20)
    
    # 图片搜索（通过URL）
    image_url_parser = subparsers.add_parser('image-search-url', help='Image search by URL')
    image_url_parser.add_argument('image_url', help='Image URL')
    image_url_parser.add_argument('--country', default='en')
    image_url_parser.add_argument('--beginPage', type=int, default=1)
    image_url_parser.add_argument('--pageSize', type=int, default=20)
    
    # 商品详情
    detail_parser = subparsers.add_parser('product-detail', help='Product detail')
    detail_parser.add_argument('offer_id', help='Offer ID')
    detail_parser.add_argument('--country', default='en')
    detail_parser.add_argument('--outMemberId', help='Out Member ID (optional)')
    
    # 店铺搜索
    shop_parser = subparsers.add_parser('shop-search', help='Shop search')
    shop_parser.add_argument('seller_open_id', help='Seller Open ID')
    shop_parser.add_argument('--country', default='en')
    shop_parser.add_argument('--beginPage', type=int, default=1)
    shop_parser.add_argument('--pageSize', type=int, default=20)
    
    # 商品推荐
    recommend_parser = subparsers.add_parser('offer-recommend', help='Offer recommend')
    recommend_parser.add_argument('keyword', help='Keyword for recommendation')
    recommend_parser.add_argument('--country', default='en')
    recommend_parser.add_argument('--beginPage', type=int, default=1)
    recommend_parser.add_argument('--pageSize', type=int, default=20)
    
    # 搜索导航
    nav_parser = subparsers.add_parser('search-navigation', help='Search navigation')
    nav_parser.add_argument('keyword', help='Keyword for navigation')
    nav_parser.add_argument('--country', default='en')
    
    # 相关推荐
    related_parser = subparsers.add_parser('related-recommend', help='Related recommend')
    related_parser.add_argument('offer_id', help='Offer ID')
    related_parser.add_argument('--language', default='zh')
    related_parser.add_argument('--pageNo', type=int, default=1)
    related_parser.add_argument('--pageSize', type=int, default=10)
    
    # 图片上传
    upload_parser = subparsers.add_parser('upload-image', help='Upload image to get imageId (auto-compress if >300KB)')
    upload_parser.add_argument('image_path', help='Local image file path')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'smart-search':
            result = smart_search(args.query, args.country, args.beginPage, args.pageSize)
        elif args.command == 'category':
            result = category_query(args.cate_id, args.language)
        elif args.command == 'keyword-search':
            result = keyword_search(
                args.keyword, args.country, args.beginPage, args.pageSize,
                getattr(args, 'filter', None), getattr(args, 'sort', None)
            )
        elif args.command == 'image-search':
            result = image_search(args.image_id, args.country, args.beginPage, args.pageSize)
        elif args.command == 'image-search-url':
            result = image_search_by_url(args.image_url, args.country, args.beginPage, args.pageSize)
        elif args.command == 'product-detail':
            result = product_detail(args.offer_id, args.country, getattr(args, 'outMemberId', None))
        elif args.command == 'shop-search':
            result = shop_search(args.seller_open_id, args.country, args.beginPage, args.pageSize)
        elif args.command == 'offer-recommend':
            result = offer_recommend(args.keyword, args.country, args.beginPage, args.pageSize)
        elif args.command == 'search-navigation':
            result = search_navigation(args.keyword, args.country)
        elif args.command == 'related-recommend':
            result = related_recommend(args.offer_id, args.language, args.pageNo, args.pageSize)
        elif args.command == 'upload-image':
            result = upload_image(args.image_path)
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(json.dumps({'error': str(e)}, ensure_ascii=False, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()