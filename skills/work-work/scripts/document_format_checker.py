#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文档格式规范检查脚本
Document Format Checker Script

功能:
1. 检查文档结构完整性
2. 检查章节编号规范性
3. 检查标题层级规范性
4. 生成检查报告

使用方法:
python document_format_checker.py <input_file>
"""

import re
import sys
import os
from datetime import datetime
from typing import List, Dict


class DocumentFormatChecker:
    """文档格式规范检查器"""

    def __init__(self):
        """初始化检查器"""
        self.content = ""
        self.issues = []

    def load_content(self, file_path: str) -> None:
        """加载文档内容"""
        with open(file_path, 'r', encoding='utf-8') as f:
            self.content = f.read()
        print(f"[加载] 文档: {file_path}")
        print(f"[信息] 文档长度: {len(self.content)} 字符")

    def check_main_title(self) -> List[Dict]:
        """检查主标题"""
        issues = []

        print("  [检查] 主标题...")

        # 检查是否有主标题(一级标题 #)
        main_titles = re.findall(r'^#\s+(.+)$', self.content, re.MULTILINE)

        if not main_titles:
            issues.append({
                'type': 'missing_title',
                'message': '文档缺少主标题(一级标题 # 标题)'
            })
        elif len(main_titles) > 1:
            issues.append({
                'type': 'multiple_titles',
                'message': f'文档有 {len(main_titles)} 个主标题,建议只有一个',
                'titles': main_titles[:3]  # 只显示前3个
            })
        else:
            print(f"  [信息] 主标题: {main_titles[0]}")

        return issues

    def check_abstract(self) -> List[Dict]:
        """检查摘要"""
        issues = []

        print("  [检查] 摘要...")

        # 检查是否有摘要
        if '摘要' not in self.content and 'Abstract' not in self.content:
            issues.append({
                'type': 'missing_abstract',
                'message': '文档缺少摘要部分'
            })
        else:
            # 检查摘要位置(应该在前部)
            lines = self.content.split('\n')
            abstract_line = -1
            for i, line in enumerate(lines):
                if '摘要' in line or 'Abstract' in line:
                    abstract_line = i
                    break

            if abstract_line > 50:  # 摘要在50行之后
                issues.append({
                    'type': 'abstract_position',
                    'message': f'摘要位于第 {abstract_line + 1} 行,建议放在文档开头'
                })
            else:
                print(f"  [信息] 摘要位置: 第 {abstract_line + 1} 行")

        # 检查关键词
        if '关键词' not in self.content and 'Key words' not in self.content:
            issues.append({
                'type': 'missing_keywords',
                'message': '文档缺少关键词部分'
            })

        return issues

    def check_section_structure(self) -> List[Dict]:
        """检查章节结构"""
        issues = []

        print("  [检查] 章节结构...")

        # 检查是否有二级标题
        second_level_titles = re.findall(r'^##\s+(.+)$', self.content, re.MULTILINE)

        if not second_level_titles:
            issues.append({
                'type': 'missing_sections',
                'message': '文档缺少二级标题(## 标题)'
            })
        else:
            print(f"  [信息] 二级标题数量: {len(second_level_titles)}")

        # 检查是否有三级标题
        third_level_titles = re.findall(r'^###\s+(.+)$', self.content, re.MULTILINE)
        print(f"  [信息] 三级标题数量: {len(third_level_titles)}")

        return issues

    def check_chapter_numbering(self) -> List[Dict]:
        """检查章节编号(中文编号)"""
        issues = []

        print("  [检查] 章节编号...")

        # 检查中文章节编号
        chapter_pattern = r'^##\s*([一二三四五六七八九十]+)\、(.+)$'
        chapters = re.findall(chapter_pattern, self.content, re.MULTILINE)

        if chapters:
            print(f"  [信息] 中文章节: {len(chapters)} 个")

            # 检查编号连续性
            chapter_nums = [ch[0] for ch in chapters]
            expected_chapters = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                               '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八']

            # 找出缺失的章节
            present_set = set(chapter_nums)
            missing_chapters = [ch for ch in expected_chapters if ch not in present_set]

            if missing_chapters:
                issues.append({
                    'type': 'missing_chapters',
                    'message': f'章节编号不连续,缺失: {", ".join(missing_chapters)}',
                    'missing': missing_chapters
                })

            # 检查重复章节
            chapter_counts = {}
            for num in chapter_nums:
                chapter_counts[num] = chapter_counts.get(num, 0) + 1

            duplicate_chapters = {num: count for num, count in chapter_counts.items() if count > 1}

            if duplicate_chapters:
                issues.append({
                    'type': 'duplicate_chapters',
                    'message': f'发现重复的章节编号: {duplicate_chapters}'
                })
        else:
            print("  [信息] 未使用中文章节编号")

        return issues

    def check_reference_section(self) -> List[Dict]:
        """检查参考文献部分"""
        issues = []

        print("  [检查] 参考文献部分...")

        # 检查是否有参考文献部分
        if '## 参考文献' not in self.content and '## 参考文献' not in self.content:
            issues.append({
                'type': 'missing_references',
                'message': '文档缺少参考文献部分'
            })
        else:
            # 检查参考文献格式
            ref_section = re.search(r'## 参考文献\n([\s\S]+)$', self.content)

            if ref_section:
                ref_content = ref_section.group(1)
                ref_lines = [line.strip() for line in ref_content.split('\n') if line.strip()]

                # 检查文献数量
                ref_pattern = r'^\[\d+\]\s+'
                valid_refs = [line for line in ref_lines if re.match(ref_pattern, line)]

                print(f"  [信息] 参考文献数量: {len(valid_refs)}")

                if len(valid_refs) < 5:
                    issues.append({
                        'type': 'too_few_references',
                        'message': f'参考文献数量较少({len(valid_refs)} 篇),建议增加文献引用'
                    })
            else:
                issues.append({
                    'type': 'invalid_reference_format',
                    'message': '参考文献部分格式不规范'
                })

        return issues

    def check_paragraph_format(self) -> List[Dict]:
        """检查段落格式"""
        issues = []

        print("  [检查] 段落格式...")

        lines = self.content.split('\n')

        # 检查空行(段落之间应该有空行)
        for i in range(len(lines) - 1):
            current = lines[i].strip()
            next_line = lines[i + 1].strip()

            # 如果两行都不是标题,且都没有空行分隔,可能需要添加空行
            if current and next_line and not current.startswith('#') and not next_line.startswith('#'):
                # 检查是否是标题后的第一段(不需要空行)
                if i > 0 and not lines[i - 1].strip().startswith('#'):
                    # 如果当前行以句号结尾,下一行不是标题,建议添加空行
                    if current.endswith('。') and not next_line.startswith('#'):
                        # 这只是建议,不是错误
                        pass

        # 检查段落长度(过长的段落)
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('#'):
                # 计算段落长度(包含后续行直到空行或标题)
                para_length = len(line.strip())
                j = i + 1
                while j < len(lines) and lines[j].strip() and not lines[j].strip().startswith('#'):
                    para_length += len(lines[j].strip())
                    j += 1

                # 如果段落超过500字,建议分段
                if para_length > 500:
                    issues.append({
                        'type': 'long_paragraph',
                        'message': f'第 {i + 1} 行的段落过长(约{para_length}字),建议适当分段',
                        'length': para_length
                    })

        return issues

    def check_heading_hierarchy(self) -> List[Dict]:
        """检查标题层级"""
        issues = []

        print("  [检查] 标题层级...")

        lines = self.content.split('\n')

        # 记录标题层级
        previous_level = 0

        for i, line in enumerate(lines):
            if line.startswith('#'):
                # 提取标题级别
                level = 0
                while level < len(line) and line[level] == '#':
                    level += 1

                # 检查标题层级是否跳跃
                if previous_level > 0 and level > previous_level + 1:
                    issues.append({
                        'type': 'heading_jump',
                        'message': f'第 {i + 1} 行: 标题层级从 {previous_level} 跳跃到 {level},建议逐级递进',
                        'from': previous_level,
                        'to': level
                    })

                previous_level = level

        return issues

    def check_list_format(self) -> List[Dict]:
        """检查列表格式"""
        issues = []

        print("  [检查] 列表格式...")

        # 检查无序列表
        unordered_lists = re.findall(r'^[-*+]\s+', self.content, re.MULTILINE)
        print(f"  [信息] 无序列表项: {len(unordered_lists)}")

        # 检查有序列表
        ordered_lists = re.findall(r'^\d+\.\s+', self.content, re.MULTILINE)
        print(f"  [信息] 有序列表项: {len(ordered_lists)}")

        # 检查列表缩进一致性(简单检查)
        lines = self.content.split('\n')
        in_list = False
        list_indent = None

        for i, line in enumerate(lines):
            if re.match(r'^[-*+]\s+', line) or re.match(r'^\d+\.\s+', line):
                current_indent = len(line) - len(line.lstrip())

                if not in_list:
                    in_list = True
                    list_indent = current_indent
                elif list_indent != current_indent:
                    issues.append({
                        'type': 'list_indent_inconsistent',
                        'message': f'第 {i + 1} 行: 列表缩进不一致',
                        'line': line.strip()
                    })
            else:
                if line.strip():
                    in_list = False
                    list_indent = None

        return issues

    def check_document_structure(self) -> List[Dict]:
        """检查文档整体结构"""
        issues = []

        print("  [检查] 文档整体结构...")

        # 检查是否包含主要部分
        required_sections = ['摘要', '关键词', '参考文献']
        missing_sections = []

        for section in required_sections:
            if section not in self.content:
                missing_sections.append(section)

        if missing_sections:
            issues.append({
                'type': 'missing_sections',
                'message': f'文档缺少必要部分: {", ".join(missing_sections)}',
                'sections': missing_sections
            })

        # 检查文档长度
        char_count = len(self.content)
        word_count = len(self.content.replace('\n', '').replace(' ', ''))

        print(f"  [信息] 字符数: {char_count}")
        print(f"  [信息] 中文字数: {word_count}")

        if word_count < 1000:
            issues.append({
                'type': 'document_too_short',
                'message': f'文档较短({word_count}字),建议增加内容'
            })

        return issues

    def run_all_checks(self) -> List[Dict]:
        """运行所有检查"""
        print("\n[开始] 文档格式规范检查...")
        print("="*60)

        # 1. 检查主标题
        self.issues.extend(self.check_main_title())

        # 2. 检查摘要
        self.issues.extend(self.check_abstract())

        # 3. 检查章节结构
        self.issues.extend(self.check_section_structure())

        # 4. 检查章节编号
        self.issues.extend(self.check_chapter_numbering())

        # 5. 检查参考文献部分
        self.issues.extend(self.check_reference_section())

        # 6. 检查段落格式
        self.issues.extend(self.check_paragraph_format())

        # 7. 检查标题层级
        self.issues.extend(self.check_heading_hierarchy())

        # 8. 检查列表格式
        self.issues.extend(self.check_list_format())

        # 9. 检查文档整体结构
        self.issues.extend(self.check_document_structure())

        print("="*60)
        print(f"\n[完成] 共发现 {len(self.issues)} 个问题\n")
        return self.issues

    def generate_report(self) -> str:
        """生成检查报告"""
        report = []
        report.append("# 文档格式规范检查报告\n")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 统计问题类型
        issue_types = {}
        for issue in self.issues:
            issue_type = issue['type']
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1

        report.append("## 问题统计\n")
        type_names = {
            'missing_title': '缺少主标题',
            'multiple_titles': '多个主标题',
            'missing_abstract': '缺少摘要',
            'abstract_position': '摘要位置',
            'missing_keywords': '缺少关键词',
            'missing_sections': '缺少章节',
            'missing_chapters': '缺失章节',
            'duplicate_chapters': '重复章节',
            'missing_references': '缺少参考文献',
            'too_few_references': '参考文献过少',
            'invalid_reference_format': '参考文献格式不规范',
            'long_paragraph': '段落过长',
            'heading_jump': '标题层级跳跃',
            'list_indent_inconsistent': '列表缩进不一致',
            'document_too_short': '文档过短'
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

        type_order = ['missing_title', 'multiple_titles', 'missing_abstract', 'abstract_position',
                      'missing_keywords', 'missing_sections', 'missing_chapters', 'duplicate_chapters',
                      'missing_references', 'too_few_references', 'invalid_reference_format',
                      'long_paragraph', 'heading_jump', 'list_indent_inconsistent', 'document_too_short']

        has_issues = False

        for issue_type in type_order:
            if issue_type in grouped_issues:
                has_issues = True
                type_names = {
                    'missing_title': '### 主标题问题',
                    'multiple_titles': '### 主标题问题',
                    'missing_abstract': '### 摘要问题',
                    'abstract_position': '### 摘要问题',
                    'missing_keywords': '### 关键词问题',
                    'missing_sections': '### 章节结构问题',
                    'missing_chapters': '### 章节编号问题',
                    'duplicate_chapters': '### 章节编号问题',
                    'missing_references': '### 参考文献问题',
                    'too_few_references': '### 参考文献问题',
                    'invalid_reference_format': '### 参考文献问题',
                    'long_paragraph': '### 段落格式问题',
                    'heading_jump': '### 标题层级问题',
                    'list_indent_inconsistent': '### 列表格式问题',
                    'document_too_short': '### 文档结构问题'
                }
                report.append(f"{type_names.get(issue_type, f'### {issue_type}')}\n\n")

                for i, issue in enumerate(grouped_issues[issue_type], 1):
                    report.append(f"{i}. {issue['message']}\n")
                    if 'titles' in issue:
                        report.append(f"   - 标题列表: {issue['titles']}\n")
                    if 'missing' in issue:
                        report.append(f"   - 缺失章节: {issue['missing']}\n")
                    if 'length' in issue:
                        report.append(f"   - 段落长度: {issue['length']} 字\n")
                    if 'from' in issue and 'to' in issue:
                        report.append(f"   - 层级: {issue['from']} → {issue['to']}\n")
                    if 'line' in issue:
                        report.append(f"   - 内容: {issue['line']}\n")
                    report.append("\n")

        # 检查结果总结
        if not has_issues:
            report.append("\n## 检查结果\n")
            report.append("✅ 文档格式规范符合要求!\n")
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
        print("文档格式规范检查工具")
        print("="*60)

        # 加载内容
        self.load_content(input_file)

        # 运行所有检查
        issues = self.run_all_checks()

        # 生成报告
        if output_report is None:
            output_report = input_file.rsplit('.', 1)[0] + '_document_format_report.md'

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
        print("  python document_format_checker.py <input_file>")
        print("\n示例:")
        print("  python document_format_checker.py review.md")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"[错误] 输入文件不存在: {input_file}")
        sys.exit(1)

    # 创建检查器并处理
    checker = DocumentFormatChecker()
    checker.process(input_file)


if __name__ == '__main__':
    main()
