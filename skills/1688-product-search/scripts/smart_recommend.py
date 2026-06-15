#!/usr/bin/env python3
"""
1688 智能推荐处理器
自动处理用户关于推荐商品的请求
"""

import os
import sys
import json
import argparse
import subprocess

# 添加 scripts 目录到 Python 路径
sys.path.insert(0, os.path.dirname(__file__))

def get_app_credentials():
    """获取应用凭证"""
    app_key = os.getenv('ALI1688_APP_KEY')
    app_secret = os.getenv('ALI1688_APP_SECRET')
    refresh_token = os.getenv('ALI1688_REFRESH_TOKEN')
    access_token = os.getenv('ALI1688_ACCESS_TOKEN')
    
    if not app_key or not app_secret:
        raise Exception("Missing ALI1688_APP_KEY or ALI1688_APP_SECRET")
    
    return app_key, app_secret, refresh_token, access_token

def smart_recommend(query=None, category_id=None, country='en', page_size=20):
    """
    智能推荐商品
    - 如果有具体查询词，使用关键词推荐
    - 如果有类目ID，使用类目推荐  
    - 如果都没有，使用通用推荐
    """
    try:
        # 获取凭证验证
        get_app_credentials()
        
        if category_id:
            # 如果有类目ID，先获取类目名称，然后用类目名称做推荐
            result = subprocess.run([
                sys.executable, 'product_search.py', 'category', str(category_id), '--language', 'zh'
            ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
            
            if result.returncode == 0:
                category_data = json.loads(result.stdout)
                if category_data.get('result', {}).get('chineseName'):
                    category_name = category_data['result']['chineseName']
                    query = category_name
        
        # 如果没有查询词，使用通用关键词
        if not query:
            query = "热门商品"
        
        # 调用 offer-recommend 接口
        result = subprocess.run([
            sys.executable, 'product_search.py', 'offer-recommend', query, 
            '--country', country, '--pageSize', str(page_size)
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            error_msg = result.stderr if result.stderr else "Unknown error"
            raise Exception(f"Recommendation failed: {error_msg}")
            
    except Exception as e:
        return {'error': str(e)}

def main():
    parser = argparse.ArgumentParser(description='1688 Smart Recommendation')
    parser.add_argument('--query', help='Search query or category name')
    parser.add_argument('--category-id', type=int, help='Category ID for recommendation')
    parser.add_argument('--country', default='en', help='Country/language code')
    parser.add_argument('--page-size', type=int, default=20, help='Number of results')
    
    args = parser.parse_args()
    
    try:
        result = smart_recommend(
            query=args.query,
            category_id=args.category_id,
            country=args.country,
            page_size=args.page_size
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({'error': str(e)}, ensure_ascii=False, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()