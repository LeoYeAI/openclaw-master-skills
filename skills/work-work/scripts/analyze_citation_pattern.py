# -*- coding: utf-8 -*-
"""
专项检查：一整段引用参考文献被拆开逐句标注的问题
规则：同一段落内，同一参考文献编号在连续多个句子中重复出现，应合并为段末一次引用
"""
import re
import sys

def extract_paragraphs(text):
    """提取正文段落（非标题、非参考文献列表）"""
    lines = text.split('\n')
    paragraphs = []
    in_refs = False
    current_para = []
    
    for line in lines:
        line = line.rstrip()
        # 检测是否进入参考文献区
        if re.match(r'^#{1,3}\s*[一二三四五六七八九十参考文献]', line):
            if '参考文献' in line:
                in_refs = True
            if current_para:
                paragraphs.append('\n'.join(current_para))
                current_para = []
            continue
        
        if in_refs:
            continue
        
        # 跳过标题、空行
        if line.startswith('#') or not line.strip():
            if current_para:
                paragraphs.append('\n'.join(current_para))
                current_para = []
            continue
        
        current_para.append(line)
    
    if current_para:
        paragraphs.append('\n'.join(current_para))
    
    return paragraphs


def split_sentences(paragraph):
    """将段落分割为句子（按中文句号、叹号、问号）"""
    # 匹配中文句子终止符（保留引用标记）
    sentences = re.split(r'(?<=[。！？])', paragraph)
    return [s.strip() for s in sentences if s.strip()]


def find_citations(sentence):
    """提取句子中的所有引用编号"""
    # 匹配 [1], [1-3], [1,2,3], [46] 等格式
    pattern = r'\[(\d+(?:[,-]\d+)*)\]'
    matches = re.findall(pattern, sentence)
    cited = set()
    for m in matches:
        # 处理范围 [1-3] -> {1,2,3}
        parts = re.split(r'[,，]', m)
        for part in parts:
            if '-' in part:
                a, b = part.split('-', 1)
                try:
                    for i in range(int(a), int(b)+1):
                        cited.add(i)
                except:
                    pass
            else:
                try:
                    cited.add(int(part))
                except:
                    pass
    return cited


def analyze_paragraph_citations(paragraph, para_idx):
    """分析一个段落中的引用重复模式"""
    sentences = split_sentences(paragraph)
    if len(sentences) < 2:
        return []
    
    issues = []
    
    # 统计每个引用在哪些句子中出现
    citation_positions = {}  # ref_num -> [sentence_indices]
    for i, sent in enumerate(sentences):
        cited = find_citations(sent)
        for ref in cited:
            if ref not in citation_positions:
                citation_positions[ref] = []
            citation_positions[ref].append(i)
    
    # 找出在多个连续句子中重复的引用
    for ref, positions in citation_positions.items():
        if len(positions) < 2:
            continue
        
        # 检查是否有连续位置
        consecutive_groups = []
        current_group = [positions[0]]
        
        for i in range(1, len(positions)):
            if positions[i] == positions[i-1] + 1:
                current_group.append(positions[i])
            else:
                if len(current_group) >= 2:
                    consecutive_groups.append(current_group)
                current_group = [positions[i]]
        
        if len(current_group) >= 2:
            consecutive_groups.append(current_group)
        
        for group in consecutive_groups:
            n = len(group)
            severity = "严重" if n >= 3 else "警告"
            # 提取相关句子
            relevant_sents = [sentences[idx] for idx in group]
            issue = {
                'para_idx': para_idx,
                'ref': ref,
                'positions': group,
                'count': n,
                'severity': severity,
                'sentences': relevant_sents
            }
            issues.append(issue)
    
    return issues


def main():
    if len(sys.argv) < 2:
        print("用法: python analyze_citation_pattern.py <your_review.md>")
        sys.exit(1)
    input_file = sys.argv[1]
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"文件未找到: {input_file}")
        sys.exit(1)
    
    paragraphs = extract_paragraphs(text)
    
    print("=" * 70)
    print("专项分析：整段引用被拆分逐句标注的问题")
    print("=" * 70)
    print(f"共分析 {len(paragraphs)} 个段落\n")
    
    all_issues = []
    
    for para_idx, para in enumerate(paragraphs):
        issues = analyze_paragraph_citations(para, para_idx)
        all_issues.extend(issues)
    
    if not all_issues:
        print("未发现整段引用被拆分逐句标注的问题！")
    else:
        print(f"共发现 {len(all_issues)} 个问题：\n")
        
        # 按严重程度排序
        serious = [i for i in all_issues if i['severity'] == '严重']
        warnings = [i for i in all_issues if i['severity'] == '警告']
        
        print(f"  严重（连续3句以上）: {len(serious)} 个")
        print(f"  警告（连续2句）: {len(warnings)} 个")
        print()
        
        for idx, issue in enumerate(all_issues, 1):
            print(f"【问题 {idx}】{issue['severity']} - 参考文献 [{issue['ref']}]")
            print(f"  连续 {issue['count']} 个句子中重复引用")
            print(f"  句子位置: {[i+1 for i in issue['positions']]}（段落中第几句）")
            print(f"  原文句子:")
            for s_idx, sent in enumerate(issue['sentences']):
                # 截断过长的句子
                display = sent[:100] + '...' if len(sent) > 100 else sent
                print(f"    [{s_idx+1}] {display}")
            print()
    
    # 生成修复建议
    print("=" * 70)
    print("修复建议")
    print("=" * 70)
    print()
    print("对于[连续多个句子引用同一文献]的情况，学术规范建议：")
    print("  1. 如果整段内容均来自同一文献，只需在段末最后一句保留引用")
    print("  2. 如果段落首句引入文献，之后均是对该文献内容的描述，")
    print("     可在首句保留引用，后续句子中删除重复引用")
    print("  3. 避免每句话都重复标注同一引用编号")
    print()
    
    # 保存报告
    output_file = input_file.replace('.md', '_citation_pattern_report.md')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 引用模式分析报告\n\n")
        f.write(f"**分析文件**: {input_file}\n\n")
        f.write(f"**发现问题总数**: {len(all_issues)}\n\n")
        
        if all_issues:
            f.write("## 问题详情\n\n")
            for idx, issue in enumerate(all_issues, 1):
                f.write(f"### 问题 {idx}：{issue['severity']} - 参考文献 [{issue['ref']}]\n\n")
                f.write(f"- **连续句子数**: {issue['count']}\n")
                f.write(f"- **句子位置**: {[i+1 for i in issue['positions']]}（段落中第几句）\n\n")
                f.write("**原文句子**:\n\n")
                for s_idx, sent in enumerate(issue['sentences']):
                    f.write(f"> {s_idx+1}. {sent}\n\n")
                f.write("**修复建议**: 删除中间句子中的重复引用，只保留首句或末句的引用\n\n")
                f.write("---\n\n")
        
        f.write("## 修复原则\n\n")
        f.write("1. 整段内容来自同一文献 → 只在段末保留一次引用\n")
        f.write("2. 段落首句引入文献 → 首句保留，后续删除重复\n")
        f.write("3. 避免每句重复标注同一引用编号\n")
    
    print(f"报告已保存至: {output_file}")
    return len([i for i in all_issues if i['severity'] == '严重'])


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
