#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统一检查脚本 - 一次性完成所有检查
Unified Checker Script

功能:
1. 参考文献格式检查
2. 引用准确性检查
3. 文字错别字和语法检查
4. 文档格式规范检查
5. 生成统一报告

使用方法:
python unified_checker.py <input_file>
"""

import re
import sys
import os
from datetime import datetime
from typing import List, Dict, Tuple, Set


class UnifiedChecker:
    """统一检查器 - 整合所有检查功能"""

    def __init__(self):
        """初始化检查器"""
        self.content = ""
        self.file_path = ""
        self.issues = {
            'reference_format': [],
            'citation_accuracy': [],
            'typo_grammar': [],
            'document_format': []
        }
        self.references = {}
        self.citations = []

    def load_content(self, file_path: str) -> None:
        """加载文档内容"""
        self.file_path = file_path
        with open(file_path, 'r', encoding='utf-8') as f:
            self.content = f.read()
        print(f"[加载] 文档: {file_path}")
        print(f"[统计] 字符数: {len(self.content)}\n")

    def check_reference_format(self) -> List[Dict]:
        """检查参考文献格式"""
        print("=" * 80)
        print("【1】参考文献格式检查")
        print("=" * 80)

        issues = []

        # 提取参考文献
        ref_pattern = r'^\[(\d+)\]\s+(.+)$'
        ref_section = re.search(r'## 参考文献\n([\s\S]+)$', self.content)

        if not ref_section:
            issues.append({
                'type': 'reference_format',
                'severity': 'critical',
                'message': '未找到参考文献部分',
                'location': '文档末尾'
            })
            return issues

        ref_list = ref_section.group(1)
        for line in ref_list.split('\n'):
            line = line.strip()
            match = re.match(ref_pattern, line)
            if match:
                num = int(match.group(1))
                ref_content = match.group(2)
                self.references[num] = ref_content

                # 检查作者格式
                if '. ' in ref_content:
                    authors_part = ref_content.split('. ')[0]
                    if '，' in authors_part:
                        issues.append({
                            'type': 'reference_format',
                            'severity': 'warning',
                            'message': f'文献 [{num}] 作者分隔符应使用英文逗号","',
                            'location': f'[{num}]',
                            'content': ref_content[:80]
                        })

        # 检查编号连续性
        if self.references:
            max_num = max(self.references.keys())
            missing_nums = []
            for i in range(1, max_num + 1):
                if i not in self.references:
                    missing_nums.append(i)

            if missing_nums:
                issues.append({
                    'type': 'reference_format',
                    'severity': 'critical',
                    'message': f'参考文献编号不连续,缺失: {missing_nums}',
                    'location': '参考文献列表'
                })

        # 检查重复编号
        num_count = {}
        for line in ref_list.split('\n'):
            match = re.match(r'^\[(\d+)\]', line.strip())
            if match:
                num = int(match.group(1))
                num_count[num] = num_count.get(num, 0) + 1

        duplicates = {k: v for k, v in num_count.items() if v > 1}
        if duplicates:
            issues.append({
                'type': 'reference_format',
                'severity': 'critical',
                'message': f'发现重复编号: {duplicates}',
                'location': '参考文献列表'
            })

        self.issues['reference_format'] = issues
        print(f"[完成] 发现 {len(issues)} 个格式问题\n")
        return issues

    def check_citation_accuracy(self) -> List[Dict]:
        """检查引用准确性"""
        print("=" * 80)
        print("【2】引用准确性检查")
        print("=" * 80)

        issues = []

        # 提取正文中的引用
        # 排除参考文献部分的引用
        main_content = self.content.split('## 参考文献')[0]
        citation_pattern = r'\[(\d+)\]'
        citations = [int(num) for num in re.findall(citation_pattern, main_content)]
        self.citations = citations

        # 检查无效引用
        max_ref_num = max(self.references.keys()) if self.references else 0
        invalid_refs = [num for num in citations if num > max_ref_num]

        if invalid_refs:
            issues.append({
                'type': 'citation_accuracy',
                'severity': 'critical',
                'message': f'发现 {len(set(invalid_refs))} 个超出范围的引用: {sorted(set(invalid_refs))}',
                'location': '正文'
            })

        # 检查孤立引用(存在文献但未被引用)
        if self.references:
            all_cited = set(citations)
            isolated_refs = []
            for num in self.references.keys():
                if num not in all_cited:
                    isolated_refs.append(num)

            if isolated_refs:
                issues.append({
                    'type': 'citation_accuracy',
                    'severity': 'warning',
                    'message': f'发现 {len(isolated_refs)} 个未被引用的文献: {isolated_refs[:10]}...',
                    'location': '参考文献列表'
                })

        # 检查引用编号连续性
        if citations:
            missing_in_citations = []
            for i in range(1, max(citations) + 1):
                if i not in citations and i <= max_ref_num:
                    missing_in_citations.append(i)

            if missing_in_citations:
                issues.append({
                    'type': 'citation_accuracy',
                    'severity': 'info',
                    'message': f'正文中存在跳跃引用: {missing_in_citations[:10]}...',
                    'location': '正文'
                })

        self.issues['citation_accuracy'] = issues
        print(f"[完成] 发现 {len(issues)} 个引用问题\n")
        return issues

    def check_typo_grammar(self) -> List[Dict]:
        """检查错别字和语法错误"""
        print("=" * 80)
        print("【3】错别字和语法检查")
        print("=" * 80)

        issues = []

        # 常见错别字字典
        typos = {
            '的的': '的',
            '的的的': '的',
            '是是': '是',
            '不不': '不',
            '在在': '在',
            '和和': '和',
            '的的的': '的',
            '，，': '，',
            '。。': '。',
            '？？': '？',
            '！！': '！',
        }

        # 检查常见错别字
        for typo, correction in typos.items():
            if typo in self.content:
                count = self.content.count(typo)
                issues.append({
                    'type': 'typo_grammar',
                    'severity': 'warning',
                    'message': f'发现重复字符"{typo}"(应为"{correction}")',
                    'location': f'出现{count}次',
                    'count': count
                })

        # 检查引号不匹配
        single_quotes = self.content.count('\'')
        double_quotes = self.content.count('"')
        chinese_left_quotes = self.content.count('"')
        chinese_right_quotes = self.content.count('"')
        book_left_quotes = self.content.count('《')
        book_right_quotes = self.content.count('》')

        if chinese_left_quotes != chinese_right_quotes:
            issues.append({
                'type': 'typo_grammar',
                'severity': 'critical',
                'message': f'中文引号不匹配: 左{chinese_left_quotes}个, 右{chinese_right_quotes}个',
                'location': '全文'
            })

        if book_left_quotes != book_right_quotes:
            issues.append({
                'type': 'typo_grammar',
                'severity': 'critical',
                'message': f'书名号不匹配: 左{book_left_quotes}个, 右{book_right_quotes}个',
                'location': '全文'
            })

        # 检查括号不匹配
        brackets = {
            '(': ')',
            '[': ']',
            '{': '}',
            '（': '）',
            '【': '】',
            '《': '》'
        }

        for left, right in brackets.items():
            left_count = self.content.count(left)
            right_count = self.content.count(right)
            if left_count != right_count:
                issues.append({
                    'type': 'typo_grammar',
                    'severity': 'critical',
                    'message': f'括号{left}{right}不匹配: 左{left_count}个, 右{right_count}个',
                    'location': '全文'
                })

        self.issues['typo_grammar'] = issues
        print(f"[完成] 发现 {len(issues)} 个错别字/语法问题\n")
        return issues

    def check_document_format(self) -> List[Dict]:
        """检查文档格式规范"""
        print("=" * 80)
        print("【4】文档格式规范检查")
        print("=" * 80)

        issues = []
        lines = self.content.split('\n')

        # 检查标题
        has_title = any(line.strip().startswith('# ') for line in lines)
        if not has_title:
            issues.append({
                'type': 'document_format',
                'severity': 'critical',
                'message': '文档缺少一级标题',
                'location': '文档开头'
            })

        # 检查摘要
        has_abstract = '## 摘要' in self.content or '### 摘要' in self.content
        if not has_abstract:
            issues.append({
                'type': 'document_format',
                'severity': 'warning',
                'message': '文档缺少摘要部分',
                'location': '文档开头'
            })

        # 检查参考文献部分
        has_references = '## 参考文献' in self.content
        if not has_references:
            issues.append({
                'type': 'document_format',
                'severity': 'critical',
                'message': '文档缺少参考文献部分',
                'location': '文档末尾'
            })

        # 检查章节编号
        sections = re.findall(r'^##+\s*(\d+\.?\d*\.?\d*\.?\d*)', self.content, re.MULTILINE)
        section_nums = [float(s) for s in sections]

        if section_nums:
            # 检查是否连续
            missing_sections = []
            expected_next = 1
            for num in sorted(section_nums):
                if num != expected_next:
                    missing_sections.append(expected_next)
                expected_next += 1

            if missing_sections:
                issues.append({
                    'type': 'document_format',
                    'severity': 'warning',
                    'message': f'章节编号可能不连续,缺失: {missing_sections}',
                    'location': '章节标题'
                })

        # 检查空段落
        empty_lines = 0
        for i, line in enumerate(lines):
            if line.strip() == '' and i > 0 and i < len(lines) - 1:
                empty_lines += 1

        if empty_lines > len(lines) * 0.1:
            issues.append({
                'type': 'document_format',
                'severity': 'info',
                'message': f'空段落过多({empty_lines}个),可能影响可读性',
                'location': '全文'
            })

        self.issues['document_format'] = issues
        print(f"[完成] 发现 {len(issues)} 个格式问题\n")
        return issues

    def generate_report(self) -> str:
        """生成统一检查报告"""
        report = []
        report.append("# 统一检查报告\n")
        report.append(f"**检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**检查文件**: {self.file_path}\n")
        report.append(f"**字符总数**: {len(self.content)}\n")
        report.append(f"**参考文献数**: {len(self.references)}\n")
        report.append(f"**引用总数**: {len(self.citations)}\n\n")

        # 统计问题
        total_issues = sum(len(v) for v in self.issues.values())
        critical_issues = sum(1 for v in self.issues.values() for issue in v if issue.get('severity') == 'critical')
        warning_issues = sum(1 for v in self.issues.values() for issue in v if issue.get('severity') == 'warning')

        report.append("## 问题统计\n")
        report.append(f"- **总问题数**: {total_issues}")
        report.append(f"- **严重问题**: {critical_issues} (必须修复)")
        report.append(f"- **警告问题**: {warning_issues} (建议修复)\n\n")

        # 详细问题
        for check_type, issues in self.issues.items():
            if issues:
                type_name = {
                    'reference_format': '参考文献格式',
                    'citation_accuracy': '引用准确性',
                    'typo_grammar': '错别字和语法',
                    'document_format': '文档格式'
                }.get(check_type, check_type)

                report.append(f"## {type_name} ({len(issues)}个)\n")

                for i, issue in enumerate(issues, 1):
                    severity = issue.get('severity', 'info')
                    severity_icon = {'critical': '🔴', 'warning': '🟡', 'info': '🔵'}.get(severity, '⚪')

                    report.append(f"\n### {severity_icon} 问题 {i}\n")
                    report.append(f"**类型**: {severity}\n")
                    report.append(f"**位置**: {issue.get('location', '未知')}\n")
                    report.append(f"**描述**: {issue.get('message', '')}\n")

                    if 'content' in issue:
                        report.append(f"**内容**: `{issue['content']}`\n")

                report.append("\n---\n")

        # 建议
        report.append("\n## 修复建议\n")
        if critical_issues > 0:
            report.append("1. **优先修复严重问题** 🔴\n")
            report.append("   - 这些问题可能导致文档无法正常使用\n")
        if warning_issues > 0:
            report.append("2. **建议修复警告问题** 🟡\n")
            report.append("   - 这些问题影响文档质量\n")
        if total_issues == 0:
            report.append("[OK] **恭喜!未发现任何问题!** 文档质量良好!\n")

        return '\n'.join(report)

    def save_report(self, output_path: str) -> None:
        """保存报告到文件"""
        report = self.generate_report()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"[保存] 报告已生成: {output_path}")

    def run_all_checks(self, input_file: str) -> None:
        """运行所有检查"""
        print("\n" + "=" * 80)
        print("开始统一检查")
        print("=" * 80 + "\n")

        self.load_content(input_file)

        # 运行所有检查
        self.check_reference_format()
        self.check_citation_accuracy()
        self.check_typo_grammar()
        self.check_document_format()

        # 生成报告
        output_file = input_file.rsplit('.', 1)[0] + '_unified_report.md'
        self.save_report(output_file)

        # 打印总结
        print("\n" + "=" * 80)
        print("检查完成!")
        print("=" * 80)
        print(f"总问题数: {sum(len(v) for v in self.issues.values())}")
        print(f"报告路径: {output_file}\n")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python unified_checker.py <input_file>")
        print("示例: python unified_checker.py review.md")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"错误: 文件不存在: {input_file}")
        sys.exit(1)

    checker = UnifiedChecker()
    checker.run_all_checks(input_file)


if __name__ == "__main__":
    main()
