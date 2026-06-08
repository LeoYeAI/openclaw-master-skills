#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文献格式和引用准确性检查脚本
Reference Format and Citation Accuracy Checker Script

功能:
1. 验证文献格式规范性
2. 检查引用准确性
3. 生成检查报告

使用方法:
python reference_accuracy_checker.py <input_file>
"""

import re
import sys
import os
from datetime import datetime
from typing import List, Dict, Tuple, Set


class ReferenceAccuracyChecker:
    """文献格式和引用准确性检查器"""

    def __init__(self):
        """初始化检查器"""
        self.content = ""
        self.references = {}
        self.issues = []

    def load_content(self, file_path: str) -> None:
        """加载文档内容"""
        with open(file_path, 'r', encoding='utf-8') as f:
            self.content = f.read()
        print(f"[加载] 文档: {file_path}")

    def extract_references(self) -> Dict[int, str]:
        """提取参考文献列表"""
        refs = {}

        # 匹配参考文献格式: [数字] 文献内容
        ref_pattern = r'^\[(\d+)\]\s+(.+)$'
        ref_section = re.search(r'## 参考文献\n([\s\S]+)$', self.content)

        if ref_section:
            ref_list = ref_section.group(1)
            for line in ref_list.split('\n'):
                line = line.strip()
                match = re.match(ref_pattern, line)
                if match:
                    num = int(match.group(1))
                    content = match.group(2)
                    refs[num] = content

        self.references = refs
        print(f"[提取] 参考文献 {len(refs)} 篇")
        return refs

    def check_reference_format(self) -> List[Dict]:
        """检查文献格式"""
        issues = []

        print("  [检查] 文献格式...")

        for num, ref_content in self.references.items():
            # 检查基本格式
            if not ref_content:
                issues.append({
                    'type': 'ref_format',
                    'reference': num,
                    'message': f'文献 [{num}] 内容为空',
                    'content': ref_content
                })
                continue

            # 检查作者格式
            author_match = re.match(r'^([^\.]+)\.', ref_content)
            if not author_match:
                issues.append({
                    'type': 'ref_format',
                    'reference': num,
                    'message': f'文献 [{num}] 作者格式不正确,应为: 作者. 标题',
                    'content': ref_content[:80]
                })
                continue

            authors = author_match.group(1)

            # 检查作者分隔符(应使用英文逗号)
            if '，' in authors:
                issues.append({
                    'type': 'ref_format',
                    'reference': num,
                    'message': f'文献 [{num}] 作者分隔符应使用英文逗号","',
                    'content': ref_content[:80]
                })

            # 检查期刊名格式(应包含期刊名)
            # 常见期刊格式模式
            journal_patterns = [
                r'[A-Z][a-z]+[A-Z][a-z]+',  # 英文期刊名(大写开头)
                r'[A-Z]{2,}',  # 缩写期刊名
            ]

            has_journal = False
            for pattern in journal_patterns:
                if re.search(pattern, ref_content):
                    has_journal = True
                    break

            if not has_journal:
                issues.append({
                    'type': 'ref_format',
                    'reference': num,
                    'message': f'文献 [{num}] 似乎缺少期刊名或期刊名格式不规范',
                    'content': ref_content[:80]
                })

            # 检查年份(应包含4位数字年份)
            year_match = re.search(r'\b(19|20)\d{2}\b', ref_content)
            if not year_match:
                issues.append({
                    'type': 'ref_format',
                    'reference': num,
                    'message': f'文献 [{num}] 似乎缺少年份或年份格式不正确',
                    'content': ref_content[:80]
                })

            # 检查卷期号(可选但建议有)
            volume_pattern = r'\d+\(?[A-Za-z]?\)?'
            if not re.search(volume_pattern, ref_content):
                # 卷期号不是必需的,所以这只是警告
                pass

            # 检查页码(可选但建议有)
            page_pattern = r'\d+-\d+|\d+$'
            if not re.search(page_pattern, ref_content):
                # 页码不是必需的,所以这只是警告
                pass

        print(f"  [完成] 发现 {len(issues)} 个文献格式问题")
        return issues

    def extract_citations(self) -> Set[int]:
        """提取正文中的所有引用"""
        # 匹配引用格式: [数字]
        citation_pattern = r'\[(\d+)\]'
        citations = re.findall(citation_pattern, self.content)
        citation_nums = {int(num) for num in citations}
        print(f"  [提取] 正文引用: {len(citation_nums)} 处")
        return citation_nums

    def check_citation_accuracy(self) -> List[Dict]:
        """检查引用准确性"""
        issues = []

        print("  [检查] 引用准确性...")

        # 提取正文中的所有引用
        citation_nums = self.extract_citations()

        # 检查1: 无效引用(超出参考文献范围)
        max_ref = max(self.references.keys()) if self.references else 0
        invalid_citations = {num for num in citation_nums if num > max_ref}

        if invalid_citations:
            for num in sorted(invalid_citations):
                issues.append({
                    'type': 'invalid_citation',
                    'number': num,
                    'message': f'引用 [{num}] 超出参考文献范围 (1-{max_ref})'
                })

        # 检查2: 孤立引用(正文中有引用但参考文献中没有)
        if self.references:
            ref_nums = set(self.references.keys())
            orphan_citations = citation_nums - ref_nums

            if orphan_citations:
                for num in sorted(orphan_citations):
                    issues.append({
                        'type': 'orphan_citation',
                        'number': num,
                        'message': f'引用 [{num}] 在正文中出现但不在参考文献列表中'
                    })

        # 检查3: 未引用的文献(参考文献中有但正文中未引用)
        if self.references and citation_nums:
            ref_nums = set(self.references.keys())
            unused_refs = ref_nums - citation_nums

            if unused_refs:
                issues.append({
                    'type': 'unused_reference',
                    'count': len(unused_refs),
                    'message': f'发现 {len(unused_refs)} 篇文献在正文中未被引用(这是正常的)',
                    'numbers': sorted(list(unused_refs))
                })

        print(f"  [完成] 发现 {len(issues)} 个引用准确性问题")
        return issues

    def check_reference_continuity(self) -> List[Dict]:
        """检查参考文献编号连续性"""
        issues = []

        print("  [检查] 参考文献编号连续性...")

        if not self.references:
            return issues

        ref_nums = sorted(self.references.keys())

        # 检查是否有重复编号
        num_counts = {}
        for num in ref_nums:
            num_counts[num] = num_counts.get(num, 0) + 1

        duplicates = {num: count for num, count in num_counts.items() if count > 1}

        if duplicates:
            for num, count in duplicates.items():
                issues.append({
                    'type': 'duplicate_reference',
                    'number': num,
                    'message': f'参考文献编号 [{num}] 重复 {count} 次'
                })

        # 检查是否有缺失编号
        if ref_nums:
            expected_start = 1
            expected_end = max(ref_nums)
            expected_nums = set(range(expected_start, expected_end + 1))
            actual_nums = set(ref_nums)

            missing_nums = expected_nums - actual_nums

            if missing_nums:
                issues.append({
                    'type': 'missing_reference',
                    'count': len(missing_nums),
                    'message': f'参考文献编号不连续,缺失: {sorted(list(missing_nums))}'
                })

        print(f"  [完成] 发现 {len(issues)} 个编号连续性问题")
        return issues

    def check_citation_continuity(self) -> List[Dict]:
        """检查正文中引用编号的连续性"""
        issues = []

        print("  [检查] 正文中引用编号连续性...")

        # 提取正文中的所有引用
        citation_pattern = r'\[(\d+)\]'
        citations = re.findall(citation_pattern, self.content)
        citation_nums = [int(num) for num in citations]

        if not citation_nums:
            return issues

        # 检查引用编号是否连续(可选,不是必需的)
        # 这里我们检查是否有较大的跳跃
        sorted_citations = sorted(set(citation_nums))

        gaps = []
        for i in range(len(sorted_citations) - 1):
            if sorted_citations[i+1] - sorted_citations[i] > 5:  # 跳跃超过5
                gaps.append((sorted_citations[i], sorted_citations[i+1]))

        if gaps:
            issues.append({
                'type': 'citation_gap',
                'message': f'正文中引用编号存在较大跳跃: {gaps}'
            })

        print(f"  [完成] 发现 {len(issues)} 个引用连续性问题")
        return issues

    def check_citation_position(self) -> List[Dict]:
        """检查引用标注位置"""
        issues = []

        print("  [检查] 引用标注位置...")

        # 检查引用标注是否在标点符号之后(不符合规范)
        # 规范: 引用应在标点符号之前

        bad_patterns = [
            (r'[,;]\s*\[(\d+)\]', '逗号或分号之后的引用应在其之前'),
            (r':[a-zA-Z0-9\s]*\s*\[(\d+)\]', '冒号后的引用通常应在冒号之前'),
        ]

        for pattern, message in bad_patterns:
            matches = re.finditer(pattern, self.content)
            for match in matches:
                issues.append({
                    'type': 'citation_position',
                    'location': match.start(),
                    'message': message,
                    'content': match.group(0)
                })

        print(f"  [完成] 发现 {len(issues)} 个引用位置问题")
        return issues

    def run_all_checks(self) -> List[Dict]:
        """运行所有检查"""
        print("\n[开始] 文献格式和引用准确性检查...")
        print("="*60)

        # 1. 检查文献格式
        self.issues.extend(self.check_reference_format())

        # 2. 检查引用准确性
        self.issues.extend(self.check_citation_accuracy())

        # 3. 检查参考文献编号连续性
        self.issues.extend(self.check_reference_continuity())

        # 4. 检查正文中引用编号连续性
        self.issues.extend(self.check_citation_continuity())

        # 5. 检查引用标注位置
        self.issues.extend(self.check_citation_position())

        print("="*60)
        print(f"\n[完成] 共发现 {len(self.issues)} 个问题\n")
        return self.issues

    def generate_report(self) -> str:
        """生成检查报告"""
        report = []
        report.append("# 文献格式和引用准确性检查报告\n")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 统计问题类型
        issue_types = {}
        for issue in self.issues:
            issue_type = issue['type']
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1

        report.append("## 问题统计\n")
        type_names = {
            'ref_format': '文献格式',
            'invalid_citation': '无效引用',
            'orphan_citation': '孤立引用',
            'unused_reference': '未引用文献',
            'duplicate_reference': '重复编号',
            'missing_reference': '缺失编号',
            'citation_gap': '引用编号跳跃',
            'citation_position': '引用位置'
        }
        for issue_type, count in issue_types.items():
            name = type_names.get(issue_type, issue_type)
            report.append(f"- {name}: {count} 个\n")

        report.append("\n## 详细问题列表\n")

        # 按类型分组显示问题
        grouped_issues = {}
        for issue in self.issues:
            issue_type = issue['type']
            if issue_type not in grouped_issues:
                grouped_issues[issue_type] = []
            grouped_issues[issue_type].append(issue)

        type_order = ['ref_format', 'invalid_citation', 'orphan_citation',
                      'unused_reference', 'duplicate_reference', 'missing_reference',
                      'citation_gap', 'citation_position']

        has_issues = False

        for issue_type in type_order:
            if issue_type in grouped_issues:
                has_issues = True
                type_names = {
                    'ref_format': '### 文献格式问题',
                    'invalid_citation': '### 无效引用',
                    'orphan_citation': '### 孤立引用',
                    'unused_reference': '### 未引用文献',
                    'duplicate_reference': '### 重复编号',
                    'missing_reference': '### 缺失编号',
                    'citation_gap': '### 引用编号跳跃',
                    'citation_position': '### 引用位置问题'
                }
                report.append(f"{type_names.get(issue_type, f'### {issue_type}')}\n\n")

                for i, issue in enumerate(grouped_issues[issue_type], 1):
                    report.append(f"{i}. {issue['message']}\n")
                    if 'content' in issue:
                        report.append(f"   - 内容: {issue['content']}\n")
                    if 'number' in issue:
                        report.append(f"   - 编号: [{issue['number']}]\n")
                    if 'reference' in issue:
                        report.append(f"   - 参考文献: [{issue['reference']}]\n")
                    if 'numbers' in issue:
                        report.append(f"   - 编号列表: {issue['numbers']}\n")
                    report.append("\n")

        # 检查结果总结
        if not has_issues:
            report.append("\n## 检查结果\n")
            report.append("✅ 未发现文献格式和引用准确性问题,文档质量良好!\n")
        else:
            report.append("\n## 检查结果\n")
            report.append(f"⚠️ 发现 {len(self.issues)} 个问题,建议进行修正。\n")

        return ''.join(report)

    def save_report(self, report_path: str) -> None:
        """保存检查报告"""
        report = self.generate_report()
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"[报告] 已生成: {report_path}\n")

    def process(self, input_file: str, output_report: Optional[str] = None) -> None:
        """处理主流程"""
        print("="*60)
        print("文献格式和引用准确性检查工具")
        print("="*60)

        # 加载内容
        self.load_content(input_file)

        # 提取参考文献
        self.extract_references()

        # 运行所有检查
        issues = self.run_all_checks()

        # 生成报告
        if output_report is None:
            output_report = input_file.rsplit('.', 1)[0] + '_reference_accuracy_report.md'

        self.save_report(output_report)

        # 显示总结
        print("="*60)
        print(f"检查完成! 共发现 {len(issues)} 个问题")
        print(f"报告文件: {output_report}")
        print("="*60)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python reference_accuracy_checker.py <input_file>")
        print("\n示例:")
        print("  python reference_accuracy_checker.py review.md")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"[错误] 输入文件不存在: {input_file}")
        sys.exit(1)

    # 创建检查器并处理
    checker = ReferenceAccuracyChecker()
    checker.process(input_file)


if __name__ == '__main__':
    main()
