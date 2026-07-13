#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json

# 读取帽子搜索结果
with open('帽子.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('帽子供应商列表:')
for i, item in enumerate(data, 1):
    name = item.get('name', 'Unknown')[:40]
    price = item.get('price', 'Unknown')
    link = item.get('link', '')[:60]
    print(f'{i}. {name}...')
    print(f'   价格: {price}')
    print(f'   链接: {link}...')
    print()
