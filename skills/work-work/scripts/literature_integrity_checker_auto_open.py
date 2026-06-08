#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文献完整性检查器 - 增强版
添加检查完成后打开最终文档的功能
"""

import re
import sys
import os
import subprocess
from datetime import datetime
from typing import List, Dict


class LiteratureIntegrityChecker:
    """文献完整性检查器"""

    def __init__(self, enable_deep_check=False):
        """初始化检查器"""
        self.content = ""
        self.references = []
        self.citations = []
        self.issues_summary = {
            'critical': [],
            'warning': [],
            'info': []
        }
        self.enable_deep_check = enable_deep_check

    def load_content(self, file_path: str) -> None:
        """加载文档内容"""
        with open(file_path, 'r', encoding='utf-8') as f:
            self.content = f.read()
        print(f"[加载] 文档: {file_path}")
        print(f"[统计] 字符数: {len(self.content)}")

    def extract_references(self) -> None:
        """提取参考文献"""
        print("\n" + "=" * 80)
        print("【1】提取参考文献")
        print("=" * 80)
        
        # 匹配参考文献格式: [1] 作者. 标题. 期刊, 年份, 卷(期): 页码.
        ref_pattern = re.compile(
            r'^\[(\d+)\]\s*([^\.]+)\.\s*([^\.]+)\.\s*([^,]+),\s*(\d{4}),\s*(.+)\.\s*$',
            re.MULTILINE
        )
        
        matches = ref_pattern.findall(self.content)
        
        for match in matches:
            ref_num = int(match[0])
            author = match[1].strip()
            title = match[2].strip()
            journal = match[3].strip()
            year = match[4].strip()
            pages = match[5].strip()
            
            self.references.append({
                'number': ref_num,
                'author': author,
                'title': title,
                'journal': journal,
                'year': year,
                'pages': pages
            })
        
        self.references.sort(key=lambda x: x['number'])
        print(f"[完成] 提取到 {len(self.references)} 篇参考文献")

    def extract_citations(self) -> None:
        """提取正文引用"""
        print("\n" + "=" * 80)
        print("【2】提取正文引用")
        print("=" * 80)
        
        # 匹配正文中的引用标记: [1], [2-3], [1,3,5]
        citation_pattern = re.compile(r'\[(\d+)(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*\]')
        matches = citation_pattern.findall(self.content)
        
        unique_citations = set(int(m) for m in matches)
        self.citations = sorted(list(unique_citations))
        
        print(f"[完成] 提取到 {len(matches)} 处引用 ({len(self.citations)} 个唯一引用)")

    def check_reference_completeness(self) -> None:
        """检查文献信息完整性"""
        print("\n" + "=" * 80)
        print("【3】检查文献信息完整性")
        print("=" * 80)
        
        incomplete_refs = []
        for ref in self.references:
            issues = []
            
            if not ref['journal'] or ref['journal'] == '未识别':
                issues.append('缺少期刊名')
            if not ref['pages'] or ref['pages'] == '未识别':
                issues.append('缺少页码信息')
            if not ref['title'] or len(ref['title']) < 10:
                issues.append('标题可能不完整或缺失')
            
            if issues:
                incomplete_refs.append({
                    'number': ref['number'],
                    'issues': issues
                })
        
        print(f"[完成] 发现 {len(incomplete_refs)} 篇文献信息不完整")
        
        for ref in incomplete_refs:
            for issue in ref['issues']:
                self.issues_summary['warning'].append({
                    'type': 'incomplete_reference',
                    'reference': ref['number'],
                    'message': f"文献[{ref['number']}]: {issue}"
                })

    def check_citation_consistency(self) -> None:
        """检查引用一致性"""
        print("\n" + "=" * 80)
        print("【4】检查引用一致性")
        print("=" * 80)
        
        critical_issues = []
        warnings = []
        
        ref_numbers = set(ref['number'] for ref in self.references)
        
        # 检查无效引用
        invalid_citations = [c for c in self.citations if c not in ref_numbers]
        for citation in invalid_citations:
            critical_issues.append(f"引用 [{citation}] 超出参考文献范围")
            self.issues_summary['critical'].append({
                'type': 'invalid_citation',
                'citation': citation,
                'message': f"引用 [{citation}] 超出参考文献范围"
            })
        
        # 检查孤立文献
        orphan_refs = [ref['number'] for ref in self.references if ref['number'] not in self.citations]
        for ref_num in orphan_refs:
            warnings.append(f"文献 [{ref_num}] 未在正文中被引用")
            self.issues_summary['warning'].append({
                'type': 'orphan_reference',
                'reference': ref_num,
                'message': f"文献 [{ref_num}] 未在正文中被引用"
            })
        
        print(f"[完成] 发现 {len(critical_issues)} 个严重问题")
        print(f"[完成] 发现 {len(warnings)} 个提示")

    def check_duplicate_references(self) -> None:
        """检查重复文献"""
        print("\n" + "=" * 80)
        print("【5】检查重复文献")
        print("=" * 80)
        
        # 基于标题和作者检查重复
        seen = {}
        duplicates = []
        
        for ref in self.references:
            key = (ref['title'].lower(), ref['author'].lower())
            if key in seen:
                duplicates.append({
                    'original': seen[key],
                    'duplicate': ref['number']
                })
                self.issues_summary['warning'].append({
                    'type': 'duplicate_reference',
                    'reference': ref['number'],
                    'message': f"文献 [{ref['number']}] 与文献 [{seen[key]}] 可能重复"
                })
            else:
                seen[key] = ref['number']
        
        print(f"[完成] 发现 {len(duplicates)} 篇重复文献")

    def check_citation_format(self) -> None:
        """检查引用格式"""
        print("\n" + "=" * 80)
        print("【6】检查引用格式")
        print("=" * 80)
        
        format_issues = []
        
        # 检查引用位置是否在标点符号前
        lines = self.content.split('\n')
        for i, line in enumerate(lines, 1):
            # 匹配引用在标点符号后的情况
            if re.search(r'[。！？\.,;:]\s*\[\d+', line):
                format_issues.append({
                    'line': i,
                    'message': f'第{i}行: 引用可能位于标点符号后'
                })
        
        print(f"[完成] 发现 {len(format_issues)} 个格式问题")
        
        for issue in format_issues:
            self.issues_summary['info'].append({
                'type': 'citation_position',
                'line': issue['line'],
                'message': issue['message']
            })

    def run_deep_verification(self) -> None:
        """深度验证（需要网络连接）"""
        print("\n" + "=" * 80)
        print("【7】深度验证（已跳过，使用 --deep-check 启用）")
        print("=" * 80)
        print("[提示] 深度验证需要网络连接，用于在线验证文献真实性")
        
        if self.enable_deep_check:
            # TODO: 实现在线验证逻辑
            print("[提示] 深度验证功能待实现")

    def save_report(self, output_file: str) -> None:
        """保存检查报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# 文献完整性验证报告\n\n")
            f.write(f"**检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**检查文件**: {os.path.basename(self.content_file_path) if hasattr(self, 'content_file_path') else 'unknown'}\n\n")
            f.write(f"**深度验证**: {'已启用' if self.enable_deep_check else '未启用'}\n\n")
            
            f.write("## 统计信息\n\n")
            f.write(f"- **参考文献总数**: {len(self.references)}\n")
            f.write(f"- **正文引用总数**: {len(self.citations)}\n")
            f.write(f"- **唯一引用数**: {len(self.citations)}\n\n")
            
            f.write("## 问题汇总\n\n")
            f.write(f"- 🔴 **严重问题**: {len(self.issues_summary['critical'])} 个\n")
            f.write(f"- 🟡 **警告问题**: {len(self.issues_summary['warning'])} 个\n")
            f.write(f"- 🔵 **提示信息**: {len(self.issues_summary['info'])} 个\n\n")
            
            if self.issues_summary['warning']:
                f.write("### 🟡 警告问题（建议修复）\n\n")
                for i, issue in enumerate(self.issues_summary['warning'], 1):
                    f.write(f"{i}. {issue['message']}\n")
                f.write("\n")
            
            f.write("## 文献详情\n\n")
            for ref in self.references:
                title_preview = ref['title'][:50] + '...' if len(ref['title']) > 50 else ref['title']
                f.write(f"### [{ref['number']}] {title_preview}\n\n")
                f.write(f"- **作者**: {ref['author']}\n")
                f.write(f"- **期刊**: {ref['journal']}\n")
                f.write(f"- **年份**: {ref['year']}\n")
                f.write(f"- **卷期**: {ref.get('volume', '未识别')}\n")
                f.write(f"- **页码**: {ref['pages']}\n")
                f.write(f"- **DOI**: {ref.get('doi', '未识别')}\n\n")

    def run_all_checks(self, input_file: str) -> None:
        """运行所有检查"""
        print("\n" + "=" * 80)
        print("开始文献完整性验证")
        print("=" * 80 + "\n")

        self.content_file_path = input_file
        self.load_content(input_file)

        # 1. 提取参考文献
        self.extract_references()

        # 2. 提取正文引用
        self.extract_citations()

        # 3. 检查文献完整性
        self.check_reference_completeness()

        # 4. 检查引用一致性
        self.check_citation_consistency()

        # 5. 检查重复文献
        self.check_duplicate_references()

        # 6. 检查引用格式
        self.check_citation_format()

        # 7. 深度验证（可选）
        self.run_deep_verification()

        # 生成报告
        output_file = input_file.rsplit('.', 1)[0] + '_literature_integrity_report.md'
        self.save_report(output_file)

        # 打印总结
        print("=" * 80)
        print("检查完成!")
        print("=" * 80)
        critical = len(self.issues_summary['critical'])
        warning = len(self.issues_summary['warning'])
        info = len(self.issues_summary['info'])
        print(f"严重问题: {critical} | 警告: {warning} | 提示: {info}")
        print(f"报告路径: {output_file}\n")
        
        if critical == 0:
            print("=" * 80)
            print("检查通过！正在打开最终文档...")
            print("=" * 80)
            
            # 查找最终的 Word 文档
            word_doc = input_file.rsplit('.', 1)[0] + '_上标版.docx'
            
            if os.path.exists(word_doc):
                # 尝试打开 Word 文档
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(word_doc)
                    elif os.name == 'posix':  # macOS/Linux
                        subprocess.call(['open', word_doc] if sys.platform == 'darwin' else ['xdg-open', word_doc])
                    print(f"✓ 已打开文档: {word_doc}")
                except Exception as e:
                    print(f"✗ 自动打开失败: {e}")
                    print(f"  请手动打开文档: {word_doc}")
            else:
                print(f"⚠ 未找到 Word 文档: {word_doc}")
                print(f"  请先生成 Word 文档:")
                print(f"  node scripts/create_word_with_superscript.js {input_file}")
        else:
            print("[!] 发现严重问题，请在提交前修复!")

        return critical > 0


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("文献完整性验证检查工具")
        print("=" * 60)
        print("\n使用方法:")
        print("  python literature_integrity_checker.py <input_file> [--deep-check]")
        print("\n参数:")
        print("  input_file    要检查的Markdown文件路径")
        print("  --deep-check  启用深度验证（需要网络连接）")
        print("\n示例:")
        print("  python literature_integrity_checker.py review.md")
        print("  python literature_integrity_checker.py review.md --deep-check")
        print("\n说明:")
        print("  此工具会检查文献的完整性、一致性和规范性")
        print("  发现严重问题时返回非零退出码")
        print("  检查通过后会自动打开最终生成的 Word 文档")
        sys.exit(1)

    input_file = sys.argv[1]
    enable_deep_check = '--deep-check' in sys.argv

    if not os.path.exists(input_file):
        print(f"[错误] 文件不存在: {input_file}")
        sys.exit(1)

    checker = LiteratureIntegrityChecker(enable_deep_check=enable_deep_check)
    has_errors = checker.run_all_checks(input_file)
    
    if has_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
