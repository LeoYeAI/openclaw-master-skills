#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1688 图片处理工具
- 支持图片压缩（大于300KB时自动压缩）
- 支持多种图片格式转换
"""

import os
import io
from PIL import Image


def compress_image_if_needed(image_path, max_size_kb=300):
    """
    如果图片大于指定大小，则进行压缩
    
    Args:
        image_path: 原始图片路径
        max_size_kb: 最大大小（KB），默认300KB
        
    Returns:
        处理后的图片路径（可能是原文件，也可能是压缩后的临时文件）
    """
    # 获取文件大小（KB）
    file_size_kb = os.path.getsize(image_path) / 1024
    
    # 如果小于等于300KB，直接返回原路径
    if file_size_kb <= max_size_kb:
        return image_path, False
    
    # 需要压缩
    print(f"图片大小 {file_size_kb:.1f}KB > {max_size_kb}KB，开始压缩...")
    
    # 打开图片
    with Image.open(image_path) as img:
        # 转换为RGB模式（处理RGBA、P等模式）
        if img.mode in ('RGBA', 'LA', 'P'):
            # 创建白色背景
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 计算压缩质量
        quality = 85
        while quality >= 10:
            # 创建内存缓冲区
            buffer = io.BytesIO()
            # 保存图片到缓冲区
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
            
            # 检查压缩后大小
            if buffer.tell() <= max_size_kb * 1024:
                break
            quality -= 10
        
        # 如果quality降到10以下还是太大，强制使用quality=10
        if quality < 10:
            quality = 10
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
        
        # 创建临时文件路径
        temp_path = image_path + '.compressed.jpg'
        with open(temp_path, 'wb') as f:
            f.write(buffer.getvalue())
        
        compressed_size_kb = os.path.getsize(temp_path) / 1024
        print(f"压缩完成！原大小: {file_size_kb:.1f}KB -> 压缩后: {compressed_size_kb:.1f}KB (质量: {quality})")
        
        return temp_path, True


def cleanup_temp_file(temp_path, original_path):
    """
    清理临时文件（如果不是原文件的话）
    """
    if temp_path != original_path and os.path.exists(temp_path):
        try:
            os.remove(temp_path)
        except OSError:
            pass