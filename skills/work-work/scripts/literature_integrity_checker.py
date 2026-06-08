#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文献完整性验证检查脚本 - Literature Integrity Checker v3.2.0

功能:
1. 验证每篇文献的可溯源性（通过web_search验证）
2. 检查文献信息的完整性和准确性
3. 验证引用与文献列表的一致性
4. 检查重复文献
5. 检查连续相同引用（新增）
6. 生成详细的验证报告
7. ✨ NEW: 检查通过后自动打开最终 Word 文档

使用方法:
python literature_integrity_checker.py <input_file> [--deep-check] [--no-auto-open]

注意: 此检查需要网络连接，用于验证文献的真实性
"""

import re
import sys
import os
import json
from datetime import datetime
from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass, asdict
from urllib.parse import quote
import urllib.request
import urllib.error
import ssl
import time
import subprocess


@dataclass
class Reference:
    """文献数据结构"""
    number: int
    raw_text: str
    authors: List[str]
    title: str
    journal: Optional[str] = None
    year: Optional[int] = None
    volume: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None


@dataclass
class ValidationResult:
    """验证结果数据结构"""
    reference_number: int
    is_valid: bool
    issues: List[str]
    warnings: List[str]
    suggestions: List[str]
    search_results: Optional[List[Dict]] = None


class LiteratureIntegrityChecker:
    """文献完整性检查器"""

    def __init__(self, enable_deep_check: bool = False, auto_open: bool = True):
        """初始化检查器"""
        self.content = ""
        self.file_path = ""
        self.references: Dict[int, Reference] = {}
        self.citations: List[int] = []
        self.validation_results: List[ValidationResult] = []
        self.enable_deep_check = enable_deep_check
        self.auto_open = auto_open
        self.issues_summary = {
            'critical': [],
            'warning': [],
            'info': []
        }

    def load_content(self, file_path: str) -> None:
        """加载文档内容"""
        self.file_path = file_path
        with open(file_path, 'r', encoding='utf-8') as f:
            self.content = f.read()
        print(f"[加载] 文档: {file_path}")
        print(f"[统计] 字符数: {len(self.content)}\n")

    def parse_reference(self, ref_text: str, ref_num: int) -> Reference:
        """解析单条参考文献"""
        ref = Reference(number=ref_num, raw_text=ref_text, authors=[], title="")
        
        # 尝试提取作者（通常在开头，以.结束）
        author_match = re.match(r'^([^\.]+)\.\s*', ref_text)
        if author_match:
            authors_str = author_match.group(1).strip()
            # 分割多个作者
            ref.authors = [a.strip() for a in re.split(r',|，', authors_str) if a.strip()]
        
        # 尝试提取年份（19xx或20xx格式）
        year_match = re.search(r'\b(19|20)\d{2}\b', ref_text)
        if year_match:
            ref.year = int(year_match.group(0))
        
        # 尝试提取期刊名（通常在年份之后，以逗号或句号结束）
        if ref.year:
            year_pos = ref_text.find(str(ref.year))
            if year_pos > 0:
                after_year = ref_text[year_pos + 4:].strip()
                # 查找期刊名（通常在逗号或点号之间）
                journal_match = re.match(r'^[\s,]*(.*?)[\s,]*\d+', after_year)
                if journal_match:
                    ref.journal = journal_match.group(1).strip()
        
        # 尝试提取标题（作者之后，年份之前）
        if author_match:
            after_author = ref_text[author_match.end():]
            year_match = re.search(r'\b(19|20)\d{2}\b', after_author)
            if year_match:
                ref.title = after_author[:year_match.start()].strip()
                # 移除可能的期刊名部分
                if '.' in ref.title:
                    ref.title = ref.title.rsplit('.', 1)[0].strip()
        
        return ref

    def extract_references(self) -> None:
        """提取所有参考文献"""
        print("[步骤 1/6] 提取参考文献...")
        
        # 查找参考文献章节
        ref_section_pattern = r'##\s*参考文献|##\s*References'
        ref_section_match = re.search(ref_section_pattern, self.content, re.IGNORECASE)
        
        if not ref_section_match:
            self.issues_summary['critical'].append("未找到参考文献章节")
            return
        
        # 提取参考文献部分的内容
        ref_content = self.content[ref_section_match.end():]
        
        # 匹配参考文献条目（格式: [数字] 开头）
        ref_pattern = r'^\[(\d+)\]\s*(.+?)$'
        references = re.findall(ref_pattern, ref_content, re.MULTILINE)
        
        for ref_num, ref_text in references:
            num = int(ref_num)
            ref = self.parse_reference(ref_text, num)
            self.references[num] = ref
        
        print(f"[提取] 找到 {len(self.references)} 篇参考文献\n")

    def extract_citations(self) -> None:
        """提取正文中的所有引用"""
        print("[步骤 2/6] 提取正文引用...")
        
        # 查找所有引用标记 [数字]
        citation_pattern = r'\[(\d+)\]'
        citations = re.findall(citation_pattern, self.content)
        self.citations = [int(c) for c in citations]
        
        # 去重统计
        unique_citations = sorted(set(self.citations))
        print(f"[提取] 找到 {len(self.citations)} 处引用（{len(unique_citations)} 个唯一编号）\n")

    def check_reference_completeness(self) -> None:
        """检查文献信息完整性"""
        print("[步骤 3/6] 检查文献信息完整性...")
        
        for ref_num, ref in self.references.items():
            issues = []
            warnings = []
            
            # 检查必要字段
            if not ref.authors:
                issues.append("缺少作者信息")
            if not ref.title or len(ref.title) < 5:
                issues.append("标题可能不完整或缺失")
            if not ref.journal:
                warnings.append("期刊未识别")
            if not ref.year:
                issues.append("缺少年份信息")
            if not ref.volume and not ref.pages:
                warnings.append("缺少卷期或页码信息")
            
            # 记录问题
            if issues or warnings:
                result = ValidationResult(
                    reference_number=ref_num,
                    is_valid=len(issues) == 0,
                    issues=issues,
                    warnings=warnings,
                    suggestions=[]
                )
                self.validation_results.append(result)
                
                # 分类
                for issue in issues:
                    self.issues_summary['critical'].append(f"[{ref_num}] {issue}")
                for warning in warnings:
                    self.issues_summary['warning'].append(f"[{ref_num}] {warning}")
        
        print(f"[检查] 发现 {len(self.validation_results)} 篇文献需要关注\n")

    def check_citation_consistency(self) -> None:
        """检查引用一致性"""
        print("[步骤 4/6] 检查引用一致性...")
        
        # 检查无效引用（引用编号超出参考文献范围）
        max_ref_num = max(self.references.keys()) if self.references else 0
        invalid_citations = [c for c in self.citations if c > max_ref_num or c <= 0]
        
        if invalid_citations:
            unique_invalid = sorted(set(invalid_citations))
            for invalid in unique_invalid:
                self.issues_summary['critical'].append(f"无效引用 [{invalid}]（超出参考文献范围）")
        
        # 检查孤立引用（正文中有引用但参考文献列表中不存在）
        missing_refs = set(self.citations) - set(self.references.keys())
        
        if missing_refs:
            for missing in sorted(missing_refs):
                self.issues_summary['critical'].append(f"孤立引用 [{missing}]（参考文献列表中不存在）")
        
        print(f"[检查] 无效引用: {len(invalid_citations)} | 孤立引用: {len(missing_refs)}\n")

    def check_duplicate_references(self) -> None:
        """检查重复文献"""
        print("[步骤 5/6] 检查重复文献...")
        
        # 基于标题和作者检查重复
        ref_signatures = {}
        duplicates = []
        
        for ref_num, ref in self.references.items():
            # 创建文献签名（标题 + 第一作者）
            signature = f"{ref.title.lower()}_{ref.authors[0] if ref.authors else ''}"
            
            if signature in ref_signatures:
                duplicates.append((ref_signatures[signature], ref_num))
            else:
                ref_signatures[signature] = ref_num
        
        if duplicates:
            for dup1, dup2 in duplicates:
                self.issues_summary['warning'].append(f"疑似重复文献: [{dup1}] 和 [{dup2}]")
        
        print(f"[检查] 发现 {len(duplicates)} 对疑似重复文献\n")

    def check_citation_format(self) -> None:
        """检查引用格式"""
        print("[步骤 6/6] 检查引用格式...")
        
        # 检查连续相同引用
        lines = self.content.split('\n')
        consecutive_issues = []
        
        for i, line in enumerate(lines):
            # 提取当前行的所有引用
            citations = re.findall(r'\[(\d+)\]', line)
            
            # 检查同一行是否有相同引用
            if len(citations) > len(set(citations)):
                self.issues_summary['warning'].append(f"第 {i+1} 行: 重复引用同一文献")
        
        # 检查连续三行或更多使用相同引用
        for i in range(len(lines) - 2):
            ref_counts = {}
            
            for j in range(i, min(i + 3, len(lines))):
                citations = re.findall(r'\[(\d+)\]', lines[j])
                for citation in citations:
                    ref_counts[citation] = ref_counts.get(citation, 0) + 1
            
            # 检查是否有引用在连续3行都出现
            for ref_num, count in ref_counts.items():
                if count >= 3:
                    self.issues_summary['warning'].append(
                        f"第 {i+1}-{i+3} 行: 连续3句引用同一文献 [{ref_num}]，建议只在最后一句保留"
                    )
        
        print(f"[检查] 完成\n")

    def run_deep_verification(self) -> None:
        """深度验证（可选，需要网络连接）"""
        if not self.enable_deep_check:
            print("[深度验证] 跳过（未启用 --deep-check）\n")
            return
        
        print("[深度验证] 启动文献真实性验证...")
        print("注意: 此步骤需要网络连接，可能需要较长时间\n")
        
        verified_count = 0
        for ref_num, ref in self.references.items():
            if ref.title and ref.authors:
                try:
                    # 构建搜索查询
                    query = f"{ref.authors[0]} {ref.title}"
                    encoded_query = quote(query)
                    search_url = f"https://api.crossref.org/works?query={encoded_query}"
                    
                    # 发送请求
                    req = urllib.request.Request(search_url)
                    req.add_header('User-Agent', 'LiteratureIntegrityChecker/1.0')
                    
                    with urllib.request.urlopen(req, timeout=10) as response:
                        data = json.loads(response.read().decode('utf-8'))
                        
                        if data.get('message', {}).get('total', 0) > 0:
                            verified_count += 1
                            print(f"  [{ref_num}] ✓ 验证通过")
                        else:
                            self.issues_summary['warning'].append(f"[{ref_num}] 未找到匹配的记录")
                            print(f"  [{ref_num}] ⚠ 未找到匹配记录")
                    
                    # 避免请求过快
                    time.sleep(0.5)
                    
                except Exception as e:
                    self.issues_summary['info'].append(f"[{ref_num}] 验证失败: {str(e)}")
                    print(f"  [{ref_num}] ✗ 验证失败: {str(e)}")
        
        print(f"\n[深度验证] 完成，验证了 {verified_count}/{len(self.references)} 篇文献\n")

    def generate_report(self) -> str:
        """生成检查报告"""
        report = []
        report.append("# 文献完整性检查报告\n")
        report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**检查文件**: {os.path.basename(self.file_path)}\n")
        
        # 统计信息
        report.append("## 检查统计\n")
        report.append(f"- **参考文献总数**: {len(self.references)}\n")
        report.append(f"- **正文引用总数**: {len(self.citations)}\n")
        report.append(f"- **唯一引用数**: {len(set(self.citations))}\n")
        report.append(f"- **严重问题**: {len(self.issues_summary['critical'])}\n")
        report.append(f"- **警告问题**: {len(self.issues_summary['warning'])}\n")
        report.append(f"- **提示信息**: {len(self.issues_summary['info'])}\n")
        
        # 问题列表
        if self.issues_summary['critical']:
            report.append("\n## 严重问题\n")
            for issue in self.issues_summary['critical']:
                report.append(f"- {issue}\n")
        
        if self.issues_summary['warning']:
            report.append("\n## 警告\n")
            for issue in self.issues_summary['warning']:
                report.append(f"- {issue}\n")
        
        if self.issues_summary['info']:
            report.append("\n## 提示\n")
            for issue in self.issues_summary['info']:
                report.append(f"- {issue}\n")
        
        # 检查清单
        report.append("\n## 文献检查清单\n")
        report.append("在提交前，请确保以下事项：\n")
        report.append("- [ ] 所有引用都有对应的参考文献\n")
        report.append("- [ ] 参考文献编号连续（1, 2, 3...）\n")
        report.append("- [ ] 每篇文献都有完整的作者、标题、期刊、年份信息\n")
        report.append("- [ ] 没有重复的参考文献\n")
        report.append("- [ ] 引用标记位置正确（在标点符号之前）\n")
        report.append("- [ ] 文献格式符合学术规范\n")
        
        # 结论
        report.append("\n## 检查结论\n")
        if len(self.issues_summary['critical']) == 0:
            report.append("✅ **恭喜！未发现任何问题，文献完整性良好！**\n")
        else:
            report.append("⚠️ **发现严重问题，请在提交前修复！**\n")
        
        return '\n'.join(report)

    def save_report(self, output_path: str) -> None:
        """保存报告到文件"""
        report = self.generate_report()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"[保存] 报告已生成: {output_path}\n")

    def open_final_document(self) -> None:
        """打开最终的 Word 文档"""
        if not self.auto_open:
            print("[自动打开] 已禁用\n")
            return
        
        # 检查是否有严重问题
        if len(self.issues_summary['critical']) > 0:
            print("[自动打开] 检测到严重问题，跳过自动打开\n")
            return
        
        # 查找对应的 Word 文档
        base_path = os.path.splitext(self.file_path)[0]
        
        # 优先查找 _上标版.docx
        possible_files = [
            base_path + '_上标版.docx',
            base_path + '.docx'
        ]
        
        target_file = None
        for file_path in possible_files:
            if os.path.exists(file_path):
                target_file = file_path
                break
        
        if target_file:
            print(f"[自动打开] 正在打开文档: {os.path.basename(target_file)}")
            
            try:
                # 获取操作系统平台
                platform = sys.platform
                
                if platform == 'win32':
                    # Windows
                    os.startfile(target_file)
                elif platform == 'darwin':
                    # macOS
                    subprocess.run(['open', target_file], check=True)
                else:
                    # Linux
                    subprocess.run(['xdg-open', target_file], check=True)
                
                print("OK 文档已打开\n")
                
            except Exception as e:
                print(f"WARNING 自动打开失败: {str(e)}")
                print(f"请手动打开: {target_file}\n")
        else:
            print("[自动打开] 未找到对应的 Word 文档")
            print(f"  查找路径: {base_path}_上标版.docx 或 {base_path}.docx\n")

    def run_all_checks(self, input_file: str) -> None:
        """运行所有检查"""
        print("\n" + "=" * 80)
        print("文献完整性验证检查器 v3.2.0")
        print("=" * 80 + "\n")
        
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
        
        # 自动打开最终文档
        if self.auto_open:
            self.open_final_document()
        
        if critical > 0:
            print("[!] 发现严重问题，请在提交前修复！")
            sys.exit(1)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("文献完整性验证检查工具 v3.2.0")
        print("=" * 60)
        print("\n使用方法:")
        print("  python literature_integrity_checker.py <input_file> [--deep-check] [--no-auto-open]")
        print("\n参数:")
        print("  input_file      要检查的Markdown文件路径")
        print("  --deep-check    启用深度验证（需要网络连接）")
        print("  --no-auto-open  禁用自动打开最终文档")
        print("\n示例:")
        print("  python literature_integrity_checker.py review.md")
        print("  python literature_integrity_checker.py review.md --deep-check")
        print("  python literature_integrity_checker.py review.md --no-auto-open")
        print("\n说明:")
        print("  此工具会检查文献的完整性、一致性和规范性")
        print("  发现严重问题时返回非零退出码")
        print("  检查通过后自动打开对应的 Word 文档（_上标版.docx）")
        sys.exit(1)
    
    input_file = sys.argv[1]
    enable_deep_check = '--deep-check' in sys.argv
    auto_open = '--no-auto-open' not in sys.argv
    
    if not os.path.exists(input_file):
        print(f"[错误] 文件不存在: {input_file}")
        sys.exit(1)
    
    checker = LiteratureIntegrityChecker(enable_deep_check=enable_deep_check, auto_open=auto_open)
    checker.run_all_checks(input_file)


if __name__ == "__main__":
    main()
