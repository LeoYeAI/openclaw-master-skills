#!/usr/bin/env python3
"""
腾讯云COS技能使用示例
"""

import os
import sys
from pathlib import Path

# 添加技能脚本路径
skill_dir = Path(__file__).parent.parent
sys.path.insert(0, str(skill_dir / 'scripts'))

from cos_wrapper import TencentCOSWrapper

def setup_environment():
    """设置环境变量示例"""
    # 在实际使用中，这些应该从安全的地方加载
    os.environ['TENCENT_COS_REGION'] = 'ap-guangzhou'
    os.environ['TENCENT_COS_BUCKET'] = 'example-bucket-123456'
    os.environ['TENCENT_COS_SECRET_ID'] = 'AKIDxxxxxxxxxxxxxxxxxxxxxxxx'
    os.environ['TENCENT_COS_SECRET_KEY'] = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    
    print("环境变量已设置")

def example_upload_download():
    """示例1: 文件上传和下载"""
    print("\n=== 示例1: 文件上传和下载 ===")
    
    # 初始化COS包装器
    cos = TencentCOSWrapper()
    
    # 创建测试文件
    test_file = 'test_upload.txt'
    with open(test_file, 'w') as f:
        f.write('这是测试文件内容\n' * 10)
    
    print(f"创建测试文件: {test_file}")
    
    # 上传文件
    print(f"上传文件到COS...")
    result = cos.upload_file(test_file, 'test-folder/test_upload.txt')
    
    if result.get('success'):
        print(f"✓ 上传成功: {result.get('data', {}).get('url', 'N/A')}")
    else:
        print(f"✗ 上传失败: {result.get('error', '未知错误')}")
    
    # 下载文件
    print(f"\n从COS下载文件...")
    download_path = 'test_download.txt'
    result = cos.download_file('test-folder/test_upload.txt', download_path)
    
    if result.get('success'):
        print(f"✓ 下载成功: {download_path}")
        
        # 验证文件内容
        with open(download_path, 'r') as f:
            content = f.read()
        print(f"  文件大小: {len(content)} 字节")
    else:
        print(f"✗ 下载失败: {result.get('error', '未知错误')}")
    
    # 清理
    for file in [test_file, download_path]:
        if os.path.exists(file):
            os.remove(file)
            print(f"清理文件: {file}")

def example_list_files():
    """示例2: 列出文件"""
    print("\n=== 示例2: 列出COS文件 ===")
    
    cos = TencentCOSWrapper()
    
    print("列出COS中的文件...")
    result = cos.list_files(prefix='test-folder/', max_keys=10)
    
    if result.get('success'):
        files = result.get('data', {}).get('files', [])
        if files:
            print(f"找到 {len(files)} 个文件:")
            for file in files:
                print(f"  - {file.get('Key')} ({file.get('Size')} 字节)")
        else:
            print("没有找到文件")
    else:
        print(f"✗ 列出文件失败: {result.get('error', '未知错误')}")

def example_image_processing():
    """示例3: 图片处理"""
    print("\n=== 示例3: 图片处理 ===")
    
    cos = TencentCOSWrapper()
    
    # 假设有一个图片在COS中
    test_image = 'example.jpg'
    
    print("1. 评估图片质量...")
    result = cos.assess_image_quality(test_image)
    if result.get('success'):
        print(f"✓ 质量评估完成")
        # 这里可以解析具体的质量分数
    
    print("\n2. 提升图片分辨率...")
    result = cos.enhance_image_resolution(test_image)
    if result.get('success'):
        print(f"✓ 超分辨率处理完成")
    
    print("\n3. 去除图片背景...")
    result = cos.remove_image_background(test_image)
    if result.get('success'):
        print(f"✓ 背景去除完成")
    
    print("\n4. 添加文字水印...")
    result = cos.add_text_watermark(test_image, 'Sample Watermark')
    if result.get('success'):
        print(f"✓ 水印添加完成")

def example_search():
    """示例4: 智能搜索"""
    print("\n=== 示例4: 智能搜索 ===")
    
    cos = TencentCOSWrapper()
    
    print("1. 文本搜索图片...")
    result = cos.search_by_text('风景照片')
    if result.get('success'):
        print(f"✓ 文本搜索完成")
        # 这里可以解析搜索结果
    
    print("\n2. 以图搜图...")
    result = cos.search_by_image('reference.jpg')
    if result.get('success'):
        print(f"✓ 图片搜索完成")

def example_document_processing():
    """示例5: 文档处理"""
    print("\n=== 示例5: 文档处理 ===")
    
    cos = TencentCOSWrapper()
    
    print("1. 文档转PDF...")
    result = cos.convert_to_pdf('document.docx')
    if result.get('success'):
        print(f"✓ 文档转换完成")
    
    print("\n2. 生成视频封面...")
    result = cos.generate_video_cover('video.mp4')
    if result.get('success'):
        print(f"✓ 视频封面生成完成")

def example_batch_operations():
    """示例6: 批量操作"""
    print("\n=== 示例6: 批量操作 ===")
    
    cos = TencentCOSWrapper()
    
    # 批量上传多个文件
    files_to_upload = ['file1.txt', 'file2.txt', 'file3.txt']
    
    print(f"批量上传 {len(files_to_upload)} 个文件...")
    for file in files_to_upload:
        # 创建测试文件
        with open(file, 'w') as f:
            f.write(f'这是 {file} 的内容\n')
        
        result = cos.upload_file(file, f'batch-upload/{file}')
        if result.get('success'):
            print(f"  ✓ {file} 上传成功")
        else:
            print(f"  ✗ {file} 上传失败: {result.get('error', '未知错误')}")
        
        # 清理
        if os.path.exists(file):
            os.remove(file)
    
    print("\n批量操作完成")

def main():
    """主函数"""
    print("腾讯云COS技能使用示例")
    print("=" * 50)
    
    # 设置环境变量（在实际使用中应该从配置文件加载）
    setup_environment()
    
    # 运行各个示例
    example_upload_download()
    example_list_files()
    example_image_processing()
    example_search()
    example_document_processing()
    example_batch_operations()
    
    print("\n" + "=" * 50)
    print("所有示例完成！")

if __name__ == '__main__':
    main()