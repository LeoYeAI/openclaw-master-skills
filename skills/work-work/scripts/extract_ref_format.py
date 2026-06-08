# -*- coding: utf-8 -*-
"""
解压Word文档并提取文本内容
"""

import zipfile
import xml.etree.ElementTree as ET

# 解压Word文档
with zipfile.ZipFile('参考文献格式.docx', 'r') as docx:
    # 读取document.xml
    with docx.open('word/document.xml') as f:
        xml_content = f.read()
    
    # 解析XML
    root = ET.fromstring(xml_content)
    
    # 提取所有文本
    # Word文档的文本在w:t元素中
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    
    texts = []
    for elem in root.iter():
        if elem.tag == '{' + ns['w'] + '}t':
            if elem.text:
                texts.append(elem.text)
    
    # 输出文本
    full_text = ''.join(texts)
    print("=" * 80)
    print("参考文献格式文档内容:")
    print("=" * 80)
    print(full_text)
    print("=" * 80)
