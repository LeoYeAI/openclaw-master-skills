#!/usr/bin/env python3
"""
drpy源网站结构分析工具
用于快速分析影视网站的HTML结构，生成drpy源配置建议

使用方法:
    python analyze_site.py https://www.example.com

输出信息:
    - 网站基本信息
    - 视频列表容器class
    - 关键选择器检测结果
    - drpy源配置建议
"""

import requests
import re
import sys
from bs4 import BeautifulSoup

def analyze_site(url):
    """分析网站结构"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': url
    }
    
    print(f'\n{"="*60}')
    print(f'正在分析: {url}')
    print(f'{"="*60}\n')
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        html = resp.text
        soup = BeautifulSoup(html, 'html.parser')
        
        # 基本信息
        print('【基本信息】')
        print(f'  状态码: {resp.status_code}')
        print(f'  HTML长度: {len(html)} 字符')
        
        # 查找标题
        title = soup.find('title')
        if title:
            print(f'  网站标题: {title.get_text(strip=True)}')
        
        # 查找视频列表相关class
        print('\n【视频列表分析】')
        
        # 常见的视频列表class
        common_list_classes = [
            'vod-list', 'video-list', 'movie-list', 'film-list',
            'hl-vod-list', 'module-list', 'list-item',
            'stui-vodlist', 'myui-vodlist', 'fed-vodlist'
        ]
        
        found_lists = []
        for cls in common_list_classes:
            if soup.find(class_=re.compile(cls)):
                found_lists.append(cls)
        
        if found_lists:
            print(f'  找到的视频列表class: {", ".join(found_lists)}')
        else:
            print('  未找到常见视频列表class，建议手动查找')
        
        # 查找视频链接
        vod_links = soup.find_all('a', href=re.compile(r'/vod/|/video/|/movie/|/detail/'))
        print(f'  视频链接数量: {len(vod_links)}')
        
        if vod_links:
            # 分析第一个视频项的结构
            first_link = vod_links[0]
            print(f'\n【视频项结构分析】')
            print(f'  示例链接: {first_link.get("href")}')
            print(f'  标题: {first_link.get_text(strip=True)[:50]}')
            
            # 向上查找父元素
            parent = first_link.find_parent()
            for i in range(3):
                if parent:
                    cls = parent.get('class')
                    print(f'  父元素{i+1}: {parent.name} class={cls}')
                    
                    # 查找图片
                    img = parent.find('img')
                    if img:
                        data_src = img.get('data-original') or img.get('data-src')
                        src = img.get('src')
                        print(f'    图片data-original: {data_src[:80] if data_src else "无"}')
                        print(f'    图片src: {src[:80] if src else "无"}')
                    
                    parent = parent.parent
        
        # 检查关键选择器
        print('\n【关键选择器检测】')
        selectors = {
            '列表容器': ['.hl-vod-list', '.vod-list', '.video-list', '.module-list'],
            '列表项': ['.hl-list-item', '.list-item', '.vod-item', '.video-item'],
            '标题': ['a&&title', 'h3&&Text', '.title&&Text'],
            '图片': ['img&&data-original', 'img&&data-src', 'img&&src'],
            '状态/备注': ['.remarks&&Text', '.pic-text&&Text', '.item-status&&Text'],
        }
        
        for name, patterns in selectors.items():
            found = False
            for pattern in patterns:
                # 简化的检测
                cls = pattern.replace('&&Text', '').replace('a&&', '').replace('img&&', '').replace('h3&&', '').replace('.', '')
                if soup.find(class_=re.compile(cls)):
                    print(f'  ✓ {name}: {pattern} 可能存在')
                    found = True
                    break
            if not found:
                print(f'  ✗ {name}: 未找到常见模式')
        
        # 检查分类
        print('\n【分类分析】')
        type_links = soup.find_all('a', href=re.compile(r'/type/|/class/|/category/'))
        if type_links:
            print(f'  找到 {len(type_links)} 个分类链接')
            for link in type_links[:5]:
                print(f'    - {link.get_text(strip=True)}: {link.get("href")}')
        
        # 检查搜索
        print('\n【搜索功能分析】')
        search_forms = soup.find_all('form', action=re.compile('search'))
        if search_forms:
            for form in search_forms:
                action = form.get('action', '')
                print(f'  搜索表单action: {action}')
                
                # 测试搜索是否需要验证码
                test_search = requests.get(url + action, headers=headers, timeout=5)
                if '验证码' in test_search.text or 'verify' in test_search.text:
                    print('  ⚠ 搜索需要验证码')
                else:
                    print('  ✓ 搜索可能可用')
        else:
            print('  未找到搜索表单')
        
        # 生成建议配置
        print('\n【drpy源配置建议】')
        print('-' * 60)
        
        # 提取域名
        from urllib.parse import urlparse
        parsed = urlparse(url)
        host = f'{parsed.scheme}://{parsed.netloc}'
        
        print(f'''var rule = {{
  title: '{title.get_text(strip=True) if title else "影视源"}',
  host: '{host}',
  url: '/type/fyclass/',
  
  // 根据分析结果调整选择器
  class_name: '分类1&分类2&分类3',
  class_url: '1&2&3',
  
  // 推荐选择器（需要根据实际HTML调整）
  推荐: '.hl-vod-list;li;a&&title;a&&data-original;;a&&href',
  
  // 一级选择器
  一级: '.hl-vod-list&&.hl-list-item;a&&title;a&&data-original;;a&&href',
  
  // 二级选择器（需要查看详情页确认）
  二级: '*',
  
  // 搜索（根据分析结果决定是否启用）
  searchable: 0,
  
  lazy: ''
}};''')
        
        print('-' * 60)
        print('\n【下一步建议】')
        print('1. 访问网站首页，查看视频列表的HTML结构')
        print('2. 确认class名称，特别是列表容器和列表项')
        print('3. 检查图片是在data-original还是src属性中')
        print('4. 访问详情页，确认播放列表的选择器')
        print('5. 测试搜索功能，确认是否需要验证码')
        
    except Exception as e:
        print(f'分析出错: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python analyze_site.py <网站URL>')
        print('示例: python analyze_site.py https://www.pitv.cc/')
        sys.exit(1)
    
    url = sys.argv[1]
    if not url.startswith('http'):
        url = 'https://' + url
    
    analyze_site(url)