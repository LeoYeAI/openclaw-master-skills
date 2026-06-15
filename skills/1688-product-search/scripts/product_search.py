#!/usr/bin/env python3
"""
1688 商品搜索脚本
支持9个核心接口：类目查询、关键词搜索、图片搜索、商品详情等
"""

import os
import sys
import json
import argparse
import requests
import base64

# 添加 scripts 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.auth import get_access_token, sign_request_hmac_sha1
from scripts.image_utils import compress_image_if_needed, cleanup_temp_file

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

def image_search(image_id=None, country='en', begin_page=1, page_size=20,
                 image_path=None, image_url=None):
    """多语言图片搜索

    支持三种图片来源（优先级：本地文件 > imageId > 图片URL）：
    - image_path: 本地图片文件路径，自动压缩（>300KB）→ base64 → 上传获取 imageId → 图搜
    - image_id:   已有的 imageId，直接图搜
    - image_url:  图片 URL，通过 imageAddress 字段直接图搜
    """
    app_key, app_secret, refresh_token, access_token = get_app_credentials()
    token = get_access_token(app_key, app_secret, refresh_token, access_token)

    search_params = {
        'country': country,
        'beginPage': begin_page,
        'pageSize': page_size
    }

    if image_path:
        # 本地图片：直接 base64 编码 → 上传获取 imageId → 图搜，不走 imageAddress 降级
        uploaded_id = upload_image_and_get_id(image_path, app_key, app_secret, token)
        if not uploaded_id:
            raise Exception("本地图片上传失败，无法获取有效 imageId，请检查图片格式或网络连接")
        search_params['imageId'] = uploaded_id
    elif image_id:
        search_params['imageId'] = image_id
    elif image_url:
        if 'alicdn.com' in image_url:
            # alicdn.com 域名：直接用 imageAddress 图搜，无需下载
            search_params['imageAddress'] = image_url
        else:
            # 非 alicdn.com 域名：先下载到本地，再走本地文件图搜流程
            print(f"非 alicdn.com 域名图片，先下载到本地再图搜: {image_url}")
            local_path = _download_image_to_temp(image_url)
            uploaded_id = upload_image_and_get_id(local_path, app_key, app_secret, token)
            try:
                os.remove(local_path)
            except OSError:
                pass
            if uploaded_id:
                search_params['imageId'] = uploaded_id
            else:
                print("图片上传失败，降级使用 imageAddress 方式图搜")
                search_params['imageAddress'] = image_url
    else:
        raise Exception("必须提供 image_path、image_id 或 image_url 之一")

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


def _download_image_to_temp(image_url: str) -> str:
    """将图片URL下载到本地临时文件，返回本地文件路径"""
    import tempfile
    from urllib.parse import urlparse

    parsed = urlparse(image_url)
    suffix = os.path.splitext(parsed.path)[-1] or '.jpg'
    # 只保留常见图片后缀，其他一律用 .jpg
    if suffix.lower() not in ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'):
        suffix = '.jpg'

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
        local_path = tmp_file.name

    response = requests.get(image_url, timeout=30, stream=True)
    response.raise_for_status()
    with open(local_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    size_kb = os.path.getsize(local_path) / 1024
    print(f"图片已下载到本地: {local_path}（{size_kb:.1f}KB）")
    return local_path


def upload_image_and_get_id(image_path, app_key, app_secret, token):
    """将本地图片压缩（>300KB）→ base64 → 上传，返回 imageId（失败返回 None）"""
    compressed_path, was_compressed = compress_image_if_needed(image_path, max_size_kb=300)

    try:
        with open(compressed_path, 'rb') as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')

        upload_params_json = json.dumps({'imageBase64': image_base64}, separators=(',', ':'))
        params = {
            'uploadImageParam': upload_params_json,
            'access_token': token
        }

        url_path = f"param2/1/com.alibaba.fenxiao.crossborder/product.image.upload/{app_key}"
        sign = sign_request_hmac_sha1(url_path, params, app_secret)
        params['_aop_signature'] = sign

        url = f"{BASE_URL}/{url_path}"
        response = requests.post(url, data=params, timeout=30)
        response.raise_for_status()
        result = response.json()

        image_id = result.get('result', {}).get('result')
        if image_id and str(image_id) != '0':
            print(f"图片上传成功，imageId: {image_id}")
            return str(image_id)

        print(f"图片上传返回无效 imageId，响应: {result}")
        return None

    finally:
        if was_compressed and os.path.exists(compressed_path):
            try:
                os.remove(compressed_path)
            except OSError:
                pass

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

def seller_offer_list(seller_open_id, country='en', begin_page=1, page_size=20):
    """查询同店商品列表（按卖家ID查询该商家的所有商品）"""
    app_key, app_secret, refresh_token, access_token = get_app_credentials()
    token = get_access_token(app_key, app_secret, refresh_token, access_token)

    search_params = {
        'sellerOpenId': seller_open_id,
        'country': country,
        'beginPage': begin_page,
        'pageSize': page_size
    }

    params = {
        'offerQueryParam': json.dumps(search_params, separators=(',', ':')),
        'access_token': token
    }

    url_path = f"param2/1/com.alibaba.fenxiao.crossborder/product.search.querySellerOfferList/{app_key}"
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

def pool_product_pull(offer_pool_id, task_id, page_no=1, page_size=10,
                      cate_id=None, language='en', sort_field=None, sort_type=None):
    """品池商品拉取（pool.product.pull）

    从业务定制的品池中拉取商品列表，需要有品池访问权限。
    分页查询时需固定同一个 taskId，每次分页都传同一个 taskId。

    参数：
        offer_pool_id: 品池ID（必填，业务定制且有权限控制，随便传会报错）
        task_id:       查询任务ID（必填，分页查询时需固定同一个 taskId）
        page_no:       页码（必填，默认1）
        page_size:     每页数量（必填，默认10）
        cate_id:       类目ID（选填）
        language:      语言（选填，默认 en）
        sort_field:    排序字段（选填，order1m=最近1个月销售额，buyer1m=最近1个月买家数）
        sort_type:     排序规则（选填，ASC/DESC）
    """
    app_key, app_secret, refresh_token, access_token = get_app_credentials()
    token = get_access_token(app_key, app_secret, refresh_token, access_token)

    pull_params = {
        'offerPoolId': int(offer_pool_id),
        'taskId': str(task_id),
        'pageNo': page_no,
        'pageSize': page_size,
        'language': language
    }

    if cate_id is not None:
        pull_params['cateId'] = int(cate_id)
    if sort_field:
        pull_params['sortField'] = sort_field
    if sort_type:
        pull_params['sortType'] = sort_type

    params = {
        'offerPoolQueryParam': json.dumps(pull_params, separators=(',', ':')),
        'access_token': token
    }

    url_path = f"param2/1/com.alibaba.fenxiao.crossborder/pool.product.pull/{app_key}"
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
        return response.json()
        
    finally:
        # 如果图片被压缩了，清理临时文件
        if was_compressed and os.path.exists(compressed_path):
            try:
                os.remove(compressed_path)
            except OSError:
                pass

def _print_offer_list(result, command):
    """格式化展示商品列表，展示所有可用字段"""
    # related-recommend 和 offer-recommend 的 result.result 直接是列表
    if command in ('related-recommend', 'offer-recommend'):
        items = result.get('result', {}).get('result', [])
        total = len(items)
        current_page = 1
        total_page = 1
        page_size = len(items)
    else:
        data = result.get('result', {}).get('result', {})
        items = data.get('data', [])
        total = data.get('totalRecords', len(items))
        current_page = data.get('currentPage', 1)
        total_page = data.get('totalPage', 1)
        page_size = data.get('pageSize', len(items))

    print(f"共找到 {total} 件商品（第 {current_page}/{total_page} 页，每页 {page_size} 件），展示前 {len(items)} 件：\n")
    for index, item in enumerate(items, 1):
        offer_id = item.get('offerId', '')
        subject = item.get('subject', '') or item.get('offerTitle', '')
        subject_trans = item.get('subjectTrans', '') or item.get('offerTitleTrans', '')
        image_url = item.get('imageUrl', '')
        detail_url = f"https://detail.1688.com/offer/{offer_id}.html"
        promotion_url = item.get('promotionURL', detail_url)

        # 价格信息
        price_info = item.get('priceInfo', {}) or {}
        price = price_info.get('price', 'N/A')
        promotion_price = price_info.get('promotionPrice', '')
        consign_price = price_info.get('consignPrice', '')

        # 销售数据
        month_sold = item.get('monthSold', 0)
        repurchase_rate = item.get('repurchaseRate', 'N/A')
        trade_score = item.get('tradeScore', '')
        min_order_quantity = item.get('minOrderQuantity', '')

        # 商家信息
        seller_data = item.get('sellerDataInfo', {}) or {}
        trade_medal = seller_data.get('tradeMedalLevel', '')
        composite_score = seller_data.get('compositeServiceScore', '')
        logistics_score = seller_data.get('logisticsExperienceScore', '')
        dispute_score = seller_data.get('disputeComplaintScore', '')
        after_sales_score = seller_data.get('afterSalesExperienceScore', '')

        # 物流信息
        shipping_info = item.get('productSimpleShippingInfo', {}) or {}
        shipping_guarantee = shipping_info.get('shippingTimeGuarantee', '')
        shipping_label = {'shipIn24Hours': '24小时发货', 'shipIn48Hours': '48小时发货'}.get(shipping_guarantee, shipping_guarantee)

        # 商品标签
        offer_identities = item.get('offerIdentities', [])
        seller_identities = item.get('sellerIdentities', [])
        is_one_psale = item.get('isOnePsale', False)
        is_select = item.get('isSelect', False)
        is_jxhy = item.get('isJxhy', False)
        is_patent = item.get('isPatentProduct', False)
        create_date = item.get('createDate', '')
        modify_date = item.get('modifyDate', '')

        # 类目信息
        top_cate = item.get('topCategoryId', '')
        second_cate = item.get('secondCategoryId', '')
        third_cate = item.get('thirdCategoryId', '')

        # 价格拼接
        price_str = f"¥{price}"
        if promotion_price:
            price_str += f"（促销¥{promotion_price}）"
        if consign_price and consign_price != price:
            price_str += f"（代发¥{consign_price}）"

        # 特性标签拼接
        flags = []
        if shipping_label:
            flags.append(shipping_label)
        if is_one_psale:
            flags.append("一件代发")
        if is_select:
            flags.append("1688严选")
        if is_jxhy:
            flags.append("精选货源")

        # 优先使用推广链接，否则用普通详情链接
        display_url = promotion_url if (promotion_url and promotion_url != detail_url) else detail_url

        print(f"{index}. {subject}")
        if subject_trans:
            print(f"   EN: {subject_trans}")
        print(f"   图片: {image_url}")
        print(f"   ID: {offer_id} | 链接: {display_url}")
        print(f"   价格: {price_str} | 起订: {min_order_quantity}件")
        print(f"   月销: {month_sold}件 | 复购: {repurchase_rate} | 店铺: {trade_score}分/{trade_medal}星 | 综合服务: {composite_score}")
        if flags:
            print(f"   特性: {' | '.join(flags)}")
        if create_date:
            print(f"   上架: {create_date[:10]} | 更新: {modify_date[:10]}")
        print()


def main():
    parser = argparse.ArgumentParser(description='1688 Product Search Skill')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
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
    image_parser.add_argument('image_id', nargs='?', default=None,
                              help='Image ID（可选，与 --image-path / --image-url 三选一）')
    image_parser.add_argument('--image-path', dest='image_path',
                              help='本地图片文件路径（自动压缩>300KB → base64 → 上传获取imageId → 图搜）')
    image_parser.add_argument('--image-url', dest='image_url',
                              help='图片URL（通过 imageAddress 字段直接图搜）')
    image_parser.add_argument('--country', default='en')
    image_parser.add_argument('--beginPage', type=int, default=1)
    image_parser.add_argument('--pageSize', type=int, default=20)
    
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

    # 同店商品查询
    seller_offers_parser = subparsers.add_parser('seller-offers', help='Query seller offer list (same shop products)')
    seller_offers_parser.add_argument('seller_open_id', help='Seller Open ID')
    seller_offers_parser.add_argument('--country', default='en')
    seller_offers_parser.add_argument('--beginPage', type=int, default=1)
    seller_offers_parser.add_argument('--pageSize', type=int, default=20)
    
    # 商品推荐
    recommend_parser = subparsers.add_parser('offer-recommend', help='Offer recommend')
    recommend_parser.add_argument('keyword', help='Keyword for recommendation')
    recommend_parser.add_argument('--country', default='en')
    recommend_parser.add_argument('--beginPage', type=int, default=1)
    recommend_parser.add_argument('--pageSize', type=int, default=20)
    
    # 品池商品拉取
    pool_parser = subparsers.add_parser('pool-pull', help='Pull products from offer pool')
    pool_parser.add_argument('--pool-id', required=True, type=int, dest='offer_pool_id',
                             help='品池ID（必填，业务定制且有权限控制）')
    pool_parser.add_argument('--task-id', required=True, dest='task_id',
                             help='查询任务ID（必填，分页查询时需固定同一个 taskId）')
    pool_parser.add_argument('--page-no', type=int, default=1, dest='page_no', help='页码（默认1）')
    pool_parser.add_argument('--page-size', type=int, default=10, dest='page_size', help='每页数量（默认10）')
    pool_parser.add_argument('--cate-id', type=int, default=None, dest='cate_id', help='类目ID（选填）')
    pool_parser.add_argument('--language', default='en', help='语言（默认en）')
    pool_parser.add_argument('--sort-field', default=None, dest='sort_field',
                             help='排序字段：order1m（最近1个月销售额）/ buyer1m（最近1个月买家数）')
    pool_parser.add_argument('--sort-type', default=None, dest='sort_type', help='排序规则：ASC/DESC')

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
        if args.command == 'category':
            result = category_query(args.cate_id, args.language)
        elif args.command == 'keyword-search':
            result = keyword_search(
                args.keyword, args.country, args.beginPage, args.pageSize,
                getattr(args, 'filter', None), getattr(args, 'sort', None)
            )
        elif args.command == 'image-search':
            result = image_search(
                image_id=args.image_id,
                country=args.country,
                begin_page=args.beginPage,
                page_size=args.pageSize,
                image_path=getattr(args, 'image_path', None),
                image_url=getattr(args, 'image_url', None)
            )
        elif args.command == 'product-detail':
            result = product_detail(args.offer_id, args.country, getattr(args, 'outMemberId', None))
        elif args.command == 'shop-search':
            result = shop_search(args.seller_open_id, args.country, args.beginPage, args.pageSize)
        elif args.command == 'seller-offers':
            result = seller_offer_list(args.seller_open_id, args.country, args.beginPage, args.pageSize)
        elif args.command == 'offer-recommend':
            result = offer_recommend(args.keyword, args.country, args.beginPage, args.pageSize)
        elif args.command == 'pool-pull':
            result = pool_product_pull(
                args.offer_pool_id, args.task_id,
                page_no=args.page_no, page_size=args.page_size,
                cate_id=args.cate_id, language=args.language,
                sort_field=args.sort_field, sort_type=args.sort_type
            )
        elif args.command == 'related-recommend':
            result = related_recommend(args.offer_id, args.language, args.pageNo, args.pageSize)
        elif args.command == 'upload-image':
            result = upload_image(args.image_path)
        
        # 对商品列表类接口，额外格式化展示商品ID和链接
        if args.command in ('keyword-search', 'image-search', 'shop-search', 'offer-recommend', 'related-recommend', 'seller-offers'):
            _print_offer_list(result, args.command)
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(json.dumps({'error': str(e)}, ensure_ascii=False, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()