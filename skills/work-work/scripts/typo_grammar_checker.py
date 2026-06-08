#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文字错别字和语法错误检查脚本
Typo and Grammar Checker Script

功能:
1. 检查常见错别字
2. 检查语法错误
3. 生成检查报告

使用方法:
python typo_grammar_checker.py <input_file>
"""

import re
import sys
import os
from datetime import datetime
from typing import List, Dict, Tuple


class TypoGrammarChecker:
    """错别字和语法检查器"""

    def __init__(self):
        """初始化检查器"""
        self.content = ""
        self.issues = []

        # 常见错别字词典
        self.typo_dict = self._load_typo_dict()

        # 语法规则
        self.grammar_rules = self._load_grammar_rules()

    def _load_typo_dict(self) -> Dict[str, str]:
        """加载常见错别字词典"""
        return {
            # 常见错别字
            '做为': '作为',
            '做用': '作用',
            '成份': '成分',
            '其它': '其他',
            '唯一': '唯一',
            '帐号': '账号',
            '帐户': '账户',
            '登陆': '登录',
            '粘稠': '黏稠',
            '成像': '成像',
            '必需': '必须',
            '报导': '报道',
            '反应': '反应',  # 根据上下文判断
            '截止': '截至',
            '包含': '包含',
            '包含': '包括',
            '以致于': '以至于',
            '以至': '以致',
            '以至': '甚至',
            '以至': '以至于',
            '必须': '必须',
            '必须': '必需',
            '反应': '反映',
            '包含': '包括',
            '截止': '截至',
            '帐号': '账号',
            '登陆': '登录',
            '帐户': '账户',

            # 学术论文常见错误
            '研究显示': '研究显示',
            '结果表明': '结果表明',
            '结果提示': '结果提示',
            '研究指出': '研究指出',
            '研究发现': '研究发现',
            '数据显示': '数据显示',
            '统计显示': '统计显示',

            # 英文拼写错误
            'analys': 'analyze',
            'analyse': 'analyze',
            'analyses': 'analyzes',
            'studys': 'studies',
            'researchs': 'researches',
            'datas': 'data',
            'methodolog': 'methodology',
            'referenc': 'reference',
            'conclusion': 'conclusion',
            'discusion': 'discussion',
            'reslut': 'result',
            'resluts': 'results',
            'mircroplastic': 'microplastic',
            'mircroplastics': 'microplastics',
            'microplastic': 'microplastics',  # 复数形式
            'microbe': 'microbe',
            'microbiome': 'microbiome',
            'microbiota': 'microbiota',
        }

    def _load_grammar_rules(self) -> List[Tuple[str, str]]:
        """加载语法规则"""
        return [
            # 标点符号问题
            (r'\.{3,}', '发现连续句号,建议使用省略号'),
            (r'\s{3,}', '发现连续空格'),

            # 括号不匹配
            (r'\([^)]*$', '左括号缺少对应的右括号(在同一行)'),
            (r'\[[^\]]*$', '左方括号缺少对应的右方括号'),

            # 引号问题
            (r'["\"][^"\"]*$', '左引号缺少对应的右引号'),

            # 中文和英文之间缺少空格(建议,不是强制)
            # (r'[\u4e00-\u9fff][a-zA-Z]', '中文和英文之间建议添加空格'),
            # (r'[a-zA-Z][\u4e00-\u9fff]', '英文和中文之间建议添加空格'),

            # 常见语法错误
            (r'因为。所以', '"因为...所以"之间不应使用句号'),
            (r'虽然。但是', '"虽然...但是"之间不应使用句号'),
            (r'不仅。而且', '"不仅...而且"之间不应使用句号'),

            # 重复词语
            (r'\b的的\b', '发现重复的"的"'),
            (r'\b了了\b', '发现重复的"了"'),
            (r'\b是是\b', '发现重复的"是"'),
            (r'\b在在\b', '发现重复的"在"'),

            # 数字格式问题
            (r'[一二三四五六七八九十]+万', '建议使用阿拉伯数字表示数量'),
        ]

    def load_content(self, file_path: str) -> None:
        """加载文档内容"""
        with open(file_path, 'r', encoding='utf-8') as f:
            self.content = f.read()
        print(f"[加载] 文档: {file_path}")
        print(f"[信息] 文档长度: {len(self.content)} 字符")

    def check_typos(self) -> List[Dict]:
        """检查错别字"""
        issues = []

        print("  [检查] 错别字...")

        # 检查常见错别字
        for wrong, correct in self.typo_dict.items():
            if wrong in self.content:
                # 查找所有出现位置
                pattern = re.escape(wrong)
                matches = list(re.finditer(pattern, self.content))

                for match in matches:
                    issues.append({
                        'type': 'typo',
                        'location': match.start(),
                        'message': f'发现疑似错别字: "{wrong}" → "{correct}"',
                        'content': self._get_context(match.start(), 30),
                        'suggestion': correct
                    })

        print(f"  [完成] 发现 {len(issues)} 个疑似错别字")
        return issues

    def check_grammar(self) -> List[Dict]:
        """检查语法错误"""
        issues = []

        print("  [检查] 语法错误...")

        # 检查常见语法问题
        for pattern, message in self.grammar_rules:
            matches = re.finditer(pattern, self.content, re.MULTILINE)
            for match in matches:
                issues.append({
                    'type': 'grammar',
                    'location': match.start(),
                    'message': message,
                    'content': self._get_context(match.start(), 30)
                })

        print(f"  [完成] 发现 {len(issues)} 个语法问题")
        return issues

    def check_punctuation(self) -> List[Dict]:
        """检查标点符号使用"""
        issues = []

        print("  [检查] 标点符号...")

        # 检查标点符号使用规范

        # 1. 检查混用中英文标点
        patterns = [
            (r'[a-zA-Z0-9],[a-zA-Z0-9]', '英文逗号后应加空格'),
            (r'[a-zA-Z0-9]\.[a-zA-Z0-9]', '英文句号后应加空格'),
            (r'[\u4e00-\u9fff],[a-zA-Z0-9]', '中文后使用英文逗号,建议使用中文逗号'),
            (r'[a-zA-Z0-9],[\u4e00-\u9fff]', '中文前使用英文逗号,建议使用中文逗号'),
        ]

        for pattern, message in patterns:
            matches = re.finditer(pattern, self.content)
            for match in matches:
                issues.append({
                    'type': 'punctuation',
                    'location': match.start(),
                    'message': message,
                    'content': self._get_context(match.start(), 20)
                })

        print(f"  [完成] 发现 {len(issues)} 个标点符号问题")
        return issues

    def check_number_format(self) -> List[Dict]:
        """检查数字格式"""
        issues = []

        print("  [检查] 数字格式...")

        # 检查日期格式
        date_patterns = [
            (r'(\d{4})年(\d{1,2})月(\d{1,2})日', '日期格式: {year}年{month}月{day}日'),
        ]

        for pattern, template in date_patterns:
            matches = re.finditer(pattern, self.content)
            for match in matches:
                # 这个是正确的格式,不需要报错
                pass

        # 检查数字与单位之间是否缺少空格
        number_unit_pattern = r'\d+(\.\d+)?(kg|g|mg|ug|ml|l|m|cm|mm|km|m³|cm³|h|min|s)'
        matches = re.finditer(number_unit_pattern, self.content, re.IGNORECASE)
        for match in matches:
            issues.append({
                'type': 'number_format',
                'location': match.start(),
                'message': '数字与单位之间建议添加空格',
                'content': match.group(0),
                'suggestion': f"{match.group(0)[:-len(match.group(2))]} {match.group(2)}"
            })

        print(f"  [完成] 发现 {len(issues)} 个数字格式问题")
        return issues

    def _get_context(self, position: int, length: int = 30) -> str:
        """获取文本上下文"""
        start = max(0, position - length)
        end = min(len(self.content), position + length)
        return self.content[start:end]

    def run_all_checks(self) -> List[Dict]:
        """运行所有检查"""
        print("\n[开始] 文字错别字和语法检查...")
        print("="*60)

        # 1. 检查错别字
        self.issues.extend(self.check_typos())

        # 2. 检查语法错误
        self.issues.extend(self.check_grammar())

        # 3. 检查标点符号
        self.issues.extend(self.check_punctuation())

        # 4. 检查数字格式
        self.issues.extend(self.check_number_format())

        print("="*60)
        print(f"\n[完成] 共发现 {len(self.issues)} 个问题\n")
        return self.issues

    def generate_report(self) -> str:
        """生成检查报告"""
        report = []
        report.append("# 文字错别字和语法检查报告\n")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 统计问题类型
        issue_types = {}
        for issue in self.issues:
            issue_type = issue['type']
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1

        report.append("## 问题统计\n")
        type_names = {
            'typo': '错别字',
            'grammar': '语法错误',
            'punctuation': '标点符号',
            'number_format': '数字格式'
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

        type_order = ['typo', 'grammar', 'punctuation', 'number_format']

        has_issues = False

        for issue_type in type_order:
            if issue_type in grouped_issues:
                has_issues = True
                type_names = {
                    'typo': '### 错别字问题',
                    'grammar': '### 语法错误',
                    'punctuation': '### 标点符号问题',
                    'number_format': '### 数字格式问题'
                }
                report.append(f"{type_names.get(issue_type, f'### {issue_type}')}\n\n")

                for i, issue in enumerate(grouped_issues[issue_type], 1):
                    report.append(f"{i}. {issue['message']}\n")
                    if 'content' in issue:
                        report.append(f"   - 上下文: ...{issue['content']}...\n")
                    if 'suggestion' in issue:
                        report.append(f"   - 建议: {issue['suggestion']}\n")
                    if 'location' in issue:
                        # 计算行号
                        line_num = self.content[:issue['location']].count('\n') + 1
                        report.append(f"   - 位置: 第 {line_num} 行\n")
                    report.append("\n")

        # 检查结果总结
        if not has_issues:
            report.append("\n## 检查结果\n")
            report.append("✅ 未发现明显的错别字和语法错误,文档质量良好!\n")
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
        print("文字错别字和语法检查工具")
        print("="*60)

        # 加载内容
        self.load_content(input_file)

        # 运行所有检查
        issues = self.run_all_checks()

        # 生成报告
        if output_report is None:
            output_report = input_file.rsplit('.', 1)[0] + '_typo_grammar_report.md'

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
        print("  python typo_grammar_checker.py <input_file>")
        print("\n示例:")
        print("  python typo_grammar_checker.py review.md")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"[错误] 输入文件不存在: {input_file}")
        sys.exit(1)

    # 创建检查器并处理
    checker = TypoGrammarChecker()
    checker.process(input_file)


if __name__ == '__main__':
    main()
