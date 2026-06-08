#!/opt/anaconda3/bin/python3
"""
批量转换文档为 Markdown
支持 xlsx, xls, pptx, ppt, docx, pdf 等格式
"""

import argparse
import sys
from pathlib import Path

try:
    from markitdown import MarkItDown
except ImportError:
    print("错误: markitdown 未安装")
    print("请运行: pip install 'markitdown[xlsx,pptx]'")
    sys.exit(1)


def convert_directory(input_dir: str, output_dir: str, formats: list = None):
    """批量转换目录下的文档"""
    input_path = Path(input_dir).expanduser().resolve()
    output_path = Path(output_dir).expanduser().resolve()
    
    if not input_path.exists():
        print(f"错误: 输入目录不存在 - {input_dir}")
        sys.exit(1)
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 默认支持的格式
    if formats is None:
        formats = ['.xlsx', '.xls', '.pptx', '.ppt', '.docx', '.pdf', '.html']
    
    target_formats = set(formats)
    
    md = MarkItDown()
    
    converted = 0
    failed = 0
    
    print(f"输入目录: {input_path}")
    print(f"输出目录: {output_path}")
    print(f"目标格式: {', '.join(formats)}")
    print("-" * 50)
    
    for file_path in input_path.rglob("*"):
        if file_path.suffix.lower() in target_formats:
            try:
                result = md.convert(file_path)
                
                # 保持目录结构
                rel_path = file_path.relative_to(input_path)
                output_file = output_path / f"{rel_path}.md"
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                output_file.write_text(result.text_content, encoding="utf-8")
                print(f"✓ {file_path.name} -> {output_file.name}")
                converted += 1
                
            except Exception as e:
                print(f"✗ {file_path.name}: {e}")
                failed += 1
    
    print("-" * 50)
    print(f"完成: 转换 {converted} 个文件, 失败 {failed} 个")


def main():
    parser = argparse.ArgumentParser(
        description="批量转换文档为 Markdown"
    )
    parser.add_argument(
        "input_dir",
        help="输入目录路径"
    )
    parser.add_argument(
        "-o", "--output",
        default="~/Documents/converted_md",
        help="输出目录路径 (默认: ~/Documents/converted_md)"
    )
    parser.add_argument(
        "-f", "--formats",
        nargs="+",
        default=['.xlsx', '.xls', '.pptx', '.ppt', '.docx', '.pdf'],
        help="要转换的文件格式 (默认: xlsx xls pptx ppt docx pdf)"
    )
    
    args = parser.parse_args()
    
    convert_directory(args.input_dir, args.output, args.formats)


if __name__ == "__main__":
    main()