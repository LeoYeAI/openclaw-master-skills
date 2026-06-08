#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
参考文献格式规范化脚本
Reference Format Normalization Script

功能:
1. 检查参考文献引用标注格式
2. 检查参考文献列表格式
3. 生成格式检查报告
4. 根据配置文件执行格式规范化

使用方法:
python reference_formatter.py <input_file> [config_file]
"""

import re
import sys
import yaml
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional


class ReferenceFormatter:
    """参考文献格式规范化器"""

    def __init__(self, config_path: str = "ref_format_default.yml"):
        """初始化格式化器,加载配置文件"""
        self.config = self._load_config(config_path)
        self.issues = []
        self.content = ""
        self.references = {}

    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        if not os.path.exists(config_path):
            print(f"[警告] 配置文件不存在: {config_path}, 使用默认配置")
            return self._get_default_config()

        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            'citation': {
                'style': 'superscript',
                'position_rules': {
                    'before_punctuation': True,
                    'after_quote_in_sentence': True,
                    'before_period': True
                }
            },
            'same_source_format': '[{ref}:{pages}]',
            'figure_table': {
                'move_to_caption': True,
                'inline_notes_format': 'superscript_number'
            },
            'reference_list': {
                'sort_order': 'order_of_appearance',
                'numbering': {
                    'format': '[{num}]',
                    'use_brackets': True
                },
                'authors': {
                    'max_authors': 3,
                    'beyond_limit_suffix': '等',
                    'separator': ', ',
                    'last_separator': ', '
                }
            },
            'format_standard': 'chinese_academic',
            'quality_check': {
                'check_continuity': True,
                'check_duplicates': True,
                'check_invalid_refs': True,
                'check_position': True
            },
            'processing': {
                'mode': 'semi_auto',
                'generate_report': True,
                'backup_original': True
            }
        }

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

    def check_citation_positions(self) -> List[Dict]:
        """检查引用标注位置"""
        issues = []
        citation_pattern = r'\[(\d+)(?::(\d+-\d+))?\]'

        # 检查标点符号之前的引用
        if self.config['citation']['position_rules']['before_punctuation']:
            # 查找标点符号后的引用(不符合规范)
            bad_patterns = [
                (r'[,;]\s*\[(\d+)\]', '逗号或分号之后的引用应在其之前'),
                (r'[,:;]\s*"[^"]*"\s*\[(\d+)\]', '引文后的引用应在标点之前')
            ]

            for pattern, message in bad_patterns:
                matches = re.finditer(pattern, self.content)
                for match in matches:
                    issues.append({
                        'type': 'position',
                        'location': match.start(),
                        'message': message,
                        'content': match.group(0)
                    })

        return issues

    def check_citation_continuity(self) -> List[Dict]:
        """检查引用编号连续性"""
        issues = []
        # 提取正文中的所有引用编号
        citations = re.findall(r'\[(\d+)(?::\d+-\d+)?\]', self.content)
        citation_nums = [int(num) for num in citations]

        if not citation_nums:
            return issues

        # 检查是否有超出范围的引用
        max_ref = max(self.references.keys()) if self.references else 0
        for num in citation_nums:
            if num > max_ref:
                issues.append({
                    'type': 'invalid_ref',
                    'number': num,
                    'message': f'引用编号 [{num}] 超出参考文献范围 (1-{max_ref})'
                })

        # 检查连续性(可选)
        if self.config['quality_check']['check_continuity']:
            sorted_nums = sorted(set(citation_nums))
            if sorted_nums:
                expected = list(range(1, max(sorted_nums) + 1))
                missing = set(expected) - set(sorted_nums)
                if missing:
                    issues.append({
                        'type': 'missing_ref',
                        'numbers': sorted(list(missing)),
                        'message': f'引用编号不连续,缺失: {sorted(list(missing))}'
                    })

        return issues

    def check_duplicate_references(self) -> List[Dict]:
        """检查重复的参考文献编号"""
        issues = []

        # 检查参考文献列表中的重复编号
        ref_nums = list(self.references.keys())
        duplicates = [num for num in ref_nums if ref_nums.count(num) > 1]

        for dup in set(duplicates):
            issues.append({
                'type': 'duplicate_ref',
                'number': dup,
                'message': f'参考文献编号 [{dup}] 重复'
            })

        return issues

    def check_author_format(self) -> List[Dict]:
        """检查作者列表格式"""
        issues = []
        max_authors = self.config['reference_list']['authors']['max_authors']
        suffix = self.config['reference_list']['authors']['beyond_limit_suffix']

        for num, content in self.references.items():
            # 检查作者数量
            author_match = re.match(r'^(.+?)\.', content)
            if author_match:
                authors_str = author_match.group(1)
                authors = [a.strip() for a in authors_str.split(',')]

                # 如果作者数量超过限制,检查是否有"等"
                if len(authors) > max_authors and suffix not in content:
                    issues.append({
                        'type': 'author_format',
                        'reference': num,
                        'message': f'文献 [{num}] 作者数量({len(authors)})超过限制({max_authors}),应添加"{suffix}"'
                    })

        return issues

    def check_figure_table_citations(self) -> List[Dict]:
        """检查图表中的引用标注"""
        issues = []

        # 检查图表标题中的引用(应该在标题中,不在图表内)
        if self.config['figure_table']['move_to_caption']:
            # 查找图表块
            figure_pattern = r'!\[([^\]]*\[?\d+\]?\][^\]]*)\]\([^\)]+\)'
            matches = re.finditer(figure_pattern, self.content)

            for match in matches:
                caption = match.group(1)
                # 如果图表标题中没有引用但图表描述中有,则报告问题
                if '[' not in caption:
                    issues.append({
                        'type': 'figure_citation',
                        'location': match.start(),
                        'message': '图表引用标注应在图名/表名中,不在图表内',
                        'content': match.group(0)[:50] + '...'
                    })

        return issues

    def run_checks(self) -> List[Dict]:
        """运行所有检查"""
        print("\n[开始] 格式检查...")

        # 检查引用位置
        if self.config['quality_check']['check_position']:
            print("  [检查] 引用标注位置...")
            self.issues.extend(self.check_citation_positions())

        # 检查引用连续性
        if self.config['quality_check']['check_continuity']:
            print("  [检查] 引用编号连续性...")
            self.issues.extend(self.check_citation_continuity())

        # 检查重复编号
        if self.config['quality_check']['check_duplicates']:
            print("  [检查] 重复编号...")
            self.issues.extend(self.check_duplicate_references())

        # 检查作者格式
        print("  [检查] 作者列表格式...")
        self.issues.extend(self.check_author_format())

        # 检查图表引用
        print("  [检查] 图表引用...")
        self.issues.extend(self.check_figure_table_citations())

        print(f"\n[完成] 发现 {len(self.issues)} 个问题\n")
        return self.issues

    def generate_report(self) -> str:
        """生成格式检查报告"""
        report = []
        report.append("# 参考文献格式检查报告\n")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 统计问题类型
        issue_types = {}
        for issue in self.issues:
            issue_type = issue['type']
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1

        report.append("## 问题统计\n")
        for issue_type, count in issue_types.items():
            type_names = {
                'position': '引用位置',
                'invalid_ref': '无效引用',
                'missing_ref': '缺失引用',
                'duplicate_ref': '重复编号',
                'author_format': '作者格式',
                'figure_citation': '图表引用'
            }
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

        type_order = ['position', 'invalid_ref', 'missing_ref', 'duplicate_ref',
                      'author_format', 'figure_citation']

        for issue_type in type_order:
            if issue_type in grouped_issues:
                type_names = {
                    'position': '### 引用位置问题',
                    'invalid_ref': '### 无效引用',
                    'missing_ref': '### 缺失引用',
                    'duplicate_ref': '### 重复编号',
                    'author_format': '### 作者格式问题',
                    'figure_citation': '### 图表引用问题'
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
                    report.append("\n")

        # 检查结果总结
        if len(self.issues) == 0:
            report.append("\n## 检查结果\n")
            report.append("✅ 未发现格式问题,文档符合规范!\n")
        else:
            report.append("\n## 检查结果\n")
            report.append(f"⚠️ 发现 {len(self.issues)} 个问题,建议进行修正。\n")

        return ''.join(report)

    def fix_citation_positions(self) -> str:
        """修复引用标注位置"""
        content = self.content
        fixed_count = 0

        # 修复标点符号后的引用(将引用移到标点符号之前)
        if self.config['citation']['position_rules']['before_punctuation']:
            # 修复: , [1] → [1],
            content = re.sub(r',\s*\[(\d+)\]', r'[\1],', content)
            # 修复: ; [1] → [1];
            content = re.sub(r';\s*\[(\d+)\]', r'[\1];', content)
            fixed_count += len(re.findall(r'[,;]\s*\[(\d+)\]', content))

        # 修复引文后的引用位置
        if self.config['citation']['position_rules']['after_quote_in_sentence']:
            # 修复: "...。" [1] → "..."。[1]
            content = re.sub(r'"。"(\s*)\[(\d+)\]', r'"。"[1]', content)
            fixed_count += len(re.findall(r'"。"(\s*)\[(\d+)\]', content))

        self.content = content
        print(f"[修复] 引用位置: {fixed_count} 处")
        return self.content

    def format_reference_authors(self) -> Dict[int, str]:
        """格式化参考文献作者列表"""
        formatted_refs = {}
        max_authors = self.config['reference_list']['authors']['max_authors']
        suffix = self.config['reference_list']['authors']['beyond_limit_suffix']

        for num, content in self.references.items():
            author_match = re.match(r'^(.+?)\.', content)
            if author_match:
                authors_str = author_match.group(1)
                rest = content[author_match.end():]

                authors = [a.strip() for a in authors_str.split(',')]

                # 如果作者数量超过限制,截取前N个并添加后缀
                if len(authors) > max_authors:
                    authors = authors[:max_authors]
                    new_authors_str = ', '.join(authors) + suffix + '.'
                else:
                    new_authors_str = authors_str + '.'

                formatted_refs[num] = new_authors_str + rest
            else:
                formatted_refs[num] = content

        self.references = formatted_refs
        print(f"[格式化] 作者列表: {len(formatted_refs)} 篇")
        return formatted_refs

    def apply_fixes(self, confirmed_issues: List[Dict]) -> None:
        """应用确认的修复"""
        print("\n[开始] 应用修复...")

        fix_count = 0
        for issue in confirmed_issues:
            if issue['type'] == 'position':
                # 修复引用位置
                self.fix_citation_positions()
                fix_count += 1
            elif issue['type'] == 'author_format':
                # 修复作者格式
                self.format_reference_authors()
                fix_count += 1

        print(f"[完成] 已修复 {fix_count} 类问题\n")

    def save_content(self, output_path: str) -> None:
        """保存处理后的内容"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.content)
        print(f"[保存] 输出文件: {output_path}")

    def process(self, input_file: str, output_file: Optional[str] = None) -> None:
        """处理主流程"""
        print("="*60)
        print("参考文献格式规范化工具")
        print("="*60)

        # 加载内容
        self.load_content(input_file)

        # 提取参考文献
        self.extract_references()

        # 运行检查
        issues = self.run_checks()

        # 生成报告
        report = self.generate_report()

        if output_file:
            report_path = output_file.rsplit('.', 1)[0] + '_format_report.md'
        else:
            report_path = input_file.rsplit('.', 1)[0] + '_format_report.md'

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"[报告] 已生成: {report_path}\n")

        # 半自动模式
        if self.config['processing']['mode'] == 'semi_auto':
            if len(issues) > 0:
                print("="*60)
                print("请查看格式检查报告,确认是否需要修复\n")
                print(f"报告文件: {report_path}")
                print("="*60)
            else:
                print("✅ 文档格式检查通过!\n")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python reference_formatter.py <input_file> [config_file]")
        print("\n示例:")
        print("  python reference_formatter.py review.md")
        print("  python reference_formatter.py review.md custom_config.yml")
        sys.exit(1)

    input_file = sys.argv[1]
    config_file = sys.argv[2] if len(sys.argv) > 2 else "ref_format_default.yml"

    if not os.path.exists(input_file):
        print(f"[错误] 输入文件不存在: {input_file}")
        sys.exit(1)

    # 创建格式化器并处理
    formatter = ReferenceFormatter(config_file)
    formatter.process(input_file)


if __name__ == '__main__':
    main()
