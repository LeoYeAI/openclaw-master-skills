#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render.py - 将 parse_docx.py 输出的 JSON 渲染为 thuthesis LaTeX 项目
用法: python3 render.py <parsed.json> <output_dir>
"""

import json
import os
import sys
import shutil
import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# ── MBA 论文常见缩略语词典（兜底用） ────────────────────────────────────────
MBA_ABBREV_DICT = {
    'AI':    '人工智能（Artificial Intelligence）',
    'AWS':   '亚马逊云服务（Amazon Web Services）',
    'BCG':   '波士顿咨询集团（Boston Consulting Group）',
    'CAGE':  '文化-行政-地理-经济距离框架（Cultural-Administrative-Geographic-Economic）',
    'CEO':   '首席执行官（Chief Executive Officer）',
    'CFO':   '首席财务官（Chief Financial Officer）',
    'CTO':   '首席技术官（Chief Technology Officer）',
    'COO':   '首席运营官（Chief Operating Officer）',
    'CSR':   '企业社会责任（Corporate Social Responsibility）',
    'CVC':   '企业风险投资（Corporate Venture Capital）',
    'DC':    '动态能力（Dynamic Capabilities）',
    'DCS':   '分散控制系统（Distributed Control System）',
    'ERP':   '企业资源计划（Enterprise Resource Planning）',
    'ESG':   '环境、社会和治理（Environmental, Social and Governance）',
    'FDI':   '对外直接投资（Foreign Direct Investment）',
    'GDP':   '国内生产总值（Gross Domestic Product）',
    'IoT':   '物联网（Internet of Things）',
    'IP':    '知识产权（Intellectual Property）',
    'IPO':   '首次公开募股（Initial Public Offering）',
    'KPI':   '关键绩效指标（Key Performance Indicator）',
    'MAD':   '试验数据互认（Mutual Acceptance of Data）',
    'MBA':   '工商管理硕士（Master of Business Administration）',
    'MES':   '制造执行系统（Manufacturing Execution System）',
    'ML':    '机器学习（Machine Learning）',
    'MNC':   '跨国公司（Multinational Corporation）',
    'MNE':   '跨国企业（Multinational Enterprise）',
    'NPD':   '新产品开发（New Product Development）',
    'OLI':   '所有权-区位-内部化范式（Ownership-Location-Internalization Paradigm）',
    'PEST':  '政治、经济、社会、技术分析法（Political-Economic-Social-Technological）',
    'PLC':   '可编程逻辑控制器（Programmable Logic Controller）',
    'R&D':   '研究与开发（Research and Development）',
    'ROE':   '净资产收益率（Return on Equity）',
    'ROI':   '投资回报率（Return on Investment）',
    'SaaS':  '软件即服务（Software as a Service）',
    'SBU':   '战略业务单元（Strategic Business Unit）',
    'SCM':   '供应链管理（Supply Chain Management）',
    'SIS':   '安全仪表系统（Safety Instrumented System）',
    'SME':   '中小企业（Small and Medium-sized Enterprise）',
    'SWOT':  '优势、劣势、机会、威胁分析法（Strengths-Weaknesses-Opportunities-Threats）',
    'VUCA':  '易变性、不确定性、复杂性、模糊性（Volatility, Uncertainty, Complexity, Ambiguity）',
    'VRIO':  '价值、稀缺、难以模仿、组织支撑框架（Value, Rarity, Inimitability, Organization）',
}

def extract_abbreviations(data: dict) -> dict:
    """
    从论文 JSON 数据中自动提取缩略语，返回 {缩写: 解释} 字典。
    策略：
      1. 扫描全文，匹配 "XXX（全称）" 和 "全称（XXX）" 两种模式
      2. 用 MBA_ABBREV_DICT 兜底：凡是全文出现过的缩写，补充其解释
    """
    # 收集全文
    texts = []
    texts.append(data.get('abstract_cn', ''))
    texts.append(data.get('abstract_en', ''))
    for ch in data.get('chapters', []):
        for item in ch.get('content', []):
            if item.get('type') == 'text':
                texts.append(item.get('content', ''))
            elif item.get('type') == 'section':
                texts.append(item.get('title', ''))
    full_text = ' '.join(texts)

    found = {}

    # 模式1: 英文缩写（2-8位大写）+ 括号中文解释
    # 要求括号内是中文主导（至少含2个汉字），限制长度避免截入上下文
    for m in re.finditer(
        r'\b([A-Z][A-Z0-9&]{1,7})\s*[（(]([\u4e00-\u9fff][^）)]{2,30})[）)]',
        full_text
    ):
        abbr, expansion = m.group(1), m.group(2).strip()
        if abbr not in found:
            found[abbr] = expansion

    # 模式2: 中文名称（纯中文，4-20字）+ 括号英文缩写（反向定义）
    for m in re.finditer(
        r'([\u4e00-\u9fff]{2,15})\s*[（(]([A-Z][A-Z0-9&]{1,7})[）)]',
        full_text
    ):
        expansion, abbr = m.group(1).strip(), m.group(2)
        if abbr not in found:
            found[abbr] = expansion

    # 模式3: 英文全称（首字母大写，3个以上单词）+ 括号英文缩写
    for m in re.finditer(
        r'([A-Z][a-z]+(?:\s+[A-Za-z]+){2,8})\s*\(([A-Z][A-Z0-9&]{1,7})\)',
        full_text
    ):
        expansion, abbr = m.group(1).strip(), m.group(2)
        # 校验：缩写应与全称首字母对应（简单校验）
        words = expansion.split()
        initials = ''.join(w[0].upper() for w in words if w[0].isupper())
        if abbr not in found and (abbr in initials or len(abbr) <= 3):
            found[abbr] = expansion

    # 兜底：词典中有，且全文出现过的缩写；词典解释优先覆盖正则提取结果
    for abbr, explanation in MBA_ABBREV_DICT.items():
        pattern = r'\b' + re.escape(abbr) + r'\b'
        if re.search(pattern, full_text):
            found[abbr] = explanation  # 词典优先，直接覆盖

    # 过滤：去掉解释为纯中文但不像解释的条目（如 "PEST" 解释成 "宏观环境分析"）
    # 保留词典里的原始解释，不被错误解析覆盖
    filtered = {}
    for k, v in found.items():
        if len(k) < 2 or k.isdigit():
            continue
        # 如果解释太短（少于3个字符），跳过
        if len(v) < 3:
            continue
        filtered[k] = v

    return dict(sorted(filtered.items()))


# 排除列表：太短、太通用、不是缩略语的大写词
_ABBREV_STOPWORDS = {
    'A', 'I', 'IT', 'OK', 'NO', 'IS', 'OR', 'AND', 'THE', 'FOR',
    'BUT', 'IN', 'ON', 'AT', 'BY', 'TO', 'AS', 'OF', 'DO', 'IF',
    'BE', 'US', 'AN', 'SO', 'UP',
}

def fix_orphan_abbrevs(data: dict) -> tuple:
    """
    检测正文中"孤儿缩略语"（出现≥2次但从未给出解释的缩略语），
    在其**第一次出现处**插入 "XXX（待补充全称）"，并加入缩略语表。

    返回: (updated_data, all_abbrevs)
      - updated_data: 正文已补写括号注释的 data（深拷贝）
      - all_abbrevs:  完整缩略语字典（已知 + 孤儿）
    """
    import copy
    data = copy.deepcopy(data)

    # 1. 先提取已识别缩略语
    known = extract_abbreviations(data)

    # 2. 收集全文，统计大写词频次
    def iter_text_items(data):
        """遍历所有文本段落，yield (chapter_idx, item_idx, text)"""
        for ci, ch in enumerate(data.get('chapters', [])):
            for ii, item in enumerate(ch.get('content', [])):
                if item.get('type') == 'text':
                    yield ci, ii, item.get('content', '')

    full_text = ' '.join(t for _, _, t in iter_text_items(data))
    full_text += ' ' + data.get('abstract_cn', '') + ' ' + data.get('abstract_en', '')

    # 统计所有大写词频次
    upper_words = re.findall(r'\b([A-Z][A-Z0-9&]{1,7})\b', full_text)
    from collections import Counter
    freq = Counter(upper_words)

    # 3. 找孤儿：出现≥2次，不在已知，不在词典，不在停用词
    all_known_keys = set(known.keys()) | set(MBA_ABBREV_DICT.keys())
    orphans = {
        w for w, cnt in freq.items()
        if cnt >= 2
        and w not in all_known_keys
        and w not in _ABBREV_STOPWORDS
        and len(w) >= 2
    }

    if orphans:
        print(f'   发现 {len(orphans)} 个孤儿缩略语: {sorted(orphans)}')

    # 4. 对每个孤儿，在正文第一次出现处插入括号说明
    inserted = set()
    for ci, ch in enumerate(data.get('chapters', [])):
        for ii, item in enumerate(ch['content']):
            if item.get('type') != 'text':
                continue
            text = item['content']
            modified = text
            for abbr in sorted(orphans):  # 排序保证处理顺序确定
                if abbr in inserted:
                    continue
                # 检查此段落是否含该缩略语（词边界）
                pat = r'\b' + re.escape(abbr) + r'\b'
                if re.search(pat, modified):
                    # 第一次出现：替换为 "XXX（待补充全称）"
                    replacement = f'{abbr}（待补充全称）'
                    modified = re.sub(pat, replacement, modified, count=1)
                    inserted.add(abbr)
            item['content'] = modified

    # 5. 合并孤儿到缩略语字典（标记为待补充）
    orphan_abbrevs = {
        abbr: '待补充全称'
        for abbr in sorted(orphans)
    }
    all_abbrevs = dict(sorted({**known, **orphan_abbrevs}.items()))

    return data, all_abbrevs


# ── LaTeX 特殊字符转义 ──────────────────────────────────────────────────────
LATEX_ESCAPE = [
    ('\\', r'\textbackslash{}'),
    ('&',  r'\&'),
    ('%',  r'\%'),
    ('$',  r'\$'),
    ('#',  r'\#'),
    ('_',  r'\_'),
    ('{',  r'\{'),
    ('}',  r'\}'),
    ('~',  r'\textasciitilde{}'),
    ('^',  r'\textasciicircum{}'),
]

def escape_latex(text: str) -> str:
    """转义 LaTeX 特殊字符，保留已有的 LaTeX 命令"""
    if not text:
        return ''
    # 先处理反斜杠（避免二次转义）
    result = text.replace('\\', r'\textbackslash{}')
    for char, replacement in LATEX_ESCAPE[1:]:
        result = result.replace(char, replacement)
    return result

def clean_caption(text: str) -> str:
    """去掉 caption 里的图/表编号前缀，如'图1-1 '、'表4-1 '，让 thuthesis 自动编号"""
    return re.sub(r'^[图表]\s*\d+[-–—]\d+\s*', '', text.strip())

def convert_citations(text: str, mapping: dict = None, ay_lookup: dict = None) -> str:
    """把正文中的引用标记转换为 LaTeX \\cite{key}

    支持两种引用格式：
    1. 数字引用 [N] / [N,M] / [N-M]
       mapping: {编号(int): bibtex_key}，若为 None 则用 refNNN 格式（向后兼容）
         [10]        → \\cite{key10}
         [1,2,3]     → \\cite{key1,key2,key3}
         [1-3]       → \\cite{key1,key2,key3}（展开范围）
       不转换：[图X] [表X] 等非纯数字方括号内容

    2. Author-year 行文引用（文献综述常见，如 曹玉（2025）/ Smith (2023)）
       ay_lookup: {(surname_lower, year): bibtex_key}
       匹配后在年份括号后插入 \\cite{key}，保留原文作者名
       例：曹玉（2025）分析了... → 曹玉（2025）\\cite{cao2025...}分析了...
    """
    def _expand(m):
        inner = m.group(1).strip()
        # 跳过含中文或字母的方括号（如[图1]、[附录A]）
        if re.search(r'[^\d,\-\s]', inner):
            return m.group(0)
        # 范围展开：1-3 → 1,2,3
        range_m = re.match(r'^(\d+)\s*[-–]\s*(\d+)$', inner)
        if range_m:
            start, end = int(range_m.group(1)), int(range_m.group(2))
            nums = list(range(start, end + 1))
        else:
            nums = [int(n.strip()) for n in re.split(r'[,，]', inner) if n.strip().isdigit()]
        if not nums:
            return m.group(0)
        if mapping:
            keys = ','.join(mapping.get(n, f'ref{n:03d}') for n in nums)
        else:
            keys = ','.join(f'ref{n:03d}' for n in nums)
        return f'\\cite{{{keys}}}'

    # Step 1: 数字引用 [N]
    text = re.sub(r'\[([^\[\]]+)\]', _expand, text)

    # Step 2: Author-year 行文引用
    if ay_lookup:
        text = _convert_author_year_citations(text, ay_lookup)

    return text


# 拼音姓氏表（用于 author-year lookup key 生成）
_PINYIN_MAP = {
    '赵': 'zhao', '钱': 'qian', '孙': 'sun', '李': 'li', '周': 'zhou',
    '吴': 'wu', '郑': 'zheng', '王': 'wang', '冯': 'feng', '陈': 'chen',
    '褚': 'chu', '卫': 'wei', '蒋': 'jiang', '沈': 'shen', '韩': 'han',
    '杨': 'yang', '朱': 'zhu', '秦': 'qin', '尤': 'you', '许': 'xu',
    '何': 'he', '吕': 'lv', '施': 'shi', '张': 'zhang', '孔': 'kong',
    '曹': 'cao', '严': 'yan', '华': 'hua', '金': 'jin', '魏': 'wei',
    '陶': 'tao', '姜': 'jiang', '戚': 'qi', '谢': 'xie', '邹': 'zou',
    '喻': 'yu', '柏': 'bai', '水': 'shui', '窦': 'dou', '章': 'zhang',
    '云': 'yun', '苏': 'su', '潘': 'pan', '葛': 'ge', '奚': 'xi',
    '范': 'fan', '彭': 'peng', '郎': 'lang', '鲁': 'lu', '韦': 'wei',
    '昌': 'chang', '马': 'ma', '苗': 'miao', '凤': 'feng', '花': 'hua',
    '方': 'fang', '俞': 'yu', '任': 'ren', '袁': 'yuan', '柳': 'liu',
    '鲍': 'bao', '史': 'shi', '唐': 'tang', '费': 'fei', '薛': 'xue',
    '雷': 'lei', '贺': 'he', '倪': 'ni', '汤': 'tang', '滕': 'teng',
    '殷': 'yin', '罗': 'luo', '毕': 'bi', '郝': 'hao', '安': 'an',
    '常': 'chang', '于': 'yu', '时': 'shi', '傅': 'fu', '皮': 'pi',
    '卞': 'bian', '齐': 'qi', '康': 'kang', '伍': 'wu', '余': 'yu',
    '黄': 'huang', '穆': 'mu', '萧': 'xiao', '尹': 'yin', '姚': 'yao',
    '邵': 'shao', '汪': 'wang', '祁': 'qi', '毛': 'mao', '贝': 'bei',
    '明': 'ming', '计': 'ji', '成': 'cheng', '戴': 'dai', '谈': 'tan',
    '宋': 'song', '庞': 'pang', '熊': 'xiong', '纪': 'ji', '舒': 'shu',
    '屈': 'qu', '项': 'xiang', '祝': 'zhu', '董': 'dong', '梁': 'liang',
    '杜': 'du', '阮': 'ruan', '蓝': 'lan', '闵': 'min', '席': 'xi',
    '季': 'ji', '麻': 'ma', '强': 'qiang', '贾': 'jia', '路': 'lu',
    '江': 'jiang', '童': 'tong', '颜': 'yan', '郭': 'guo', '梅': 'mei',
    '盛': 'sheng', '林': 'lin', '钟': 'zhong', '徐': 'xu', '邱': 'qiu',
    '骆': 'luo', '高': 'gao', '夏': 'xia', '蔡': 'cai', '田': 'tian',
    '樊': 'fan', '胡': 'hu', '凌': 'ling', '霍': 'huo', '万': 'wan',
    '柯': 'ke', '管': 'guan', '卢': 'lu', '莫': 'mo', '房': 'fang',
    '干': 'gan', '解': 'xie', '宗': 'zong', '丁': 'ding', '宣': 'xuan',
    '邓': 'deng', '郁': 'yu', '单': 'shan', '杭': 'hang', '洪': 'hong',
    '包': 'bao', '诸': 'zhu', '左': 'zuo', '石': 'shi', '崔': 'cui',
    '吉': 'ji', '龚': 'gong', '翟': 'zhai', '付': 'fu', '葛': 'ge',
    '耿': 'geng', '高': 'gao', '刘': 'liu', '欧': 'ou', '肖': 'xiao',
    '陆': 'lu', '魏': 'wei', '吴': 'wu', '程': 'cheng', '谢': 'xie',
    '赖': 'lai', '钱': 'qian', '武': 'wu', '韩': 'han', '谭': 'tan',
}


def _surname_to_pinyin(surname: str) -> str:
    """把中文姓（单字或双字复姓）转换为拼音（小写），用于 ay_lookup key"""
    if not surname:
        return ''
    # 双字复姓
    two = _PINYIN_MAP.get(surname[:2], '')
    if two:
        return two
    return _PINYIN_MAP.get(surname[0], surname[0].lower())


def _convert_author_year_citations(text: str, ay_lookup: dict) -> str:
    """把正文中的 author-year 行文引用替换为 author\\cite{key}year 格式。

    支持的格式：
    - 中文作者全角括号：曹玉（2025）/ 葛文婕和任海全（2025）/ 杜盼盼和张倩妹（2025）
    - 英文作者半角括号：Smith (2023) / BiyuTang (2023)
    - CamelCase 拼音名：BiyuTang（2023）→ 提取最后一个词作为姓
    - 多作者：第一作者等（2025）/ Smith et al. (2023)

    替换策略：保留原始文字，在右括号后紧接插入 \\cite{key}
    例：曹玉（2025）→ 曹玉（2025）\\cite{cao2025aigcnews}
    """
    result = []
    pos = 0

    # 匹配 author-year 模式：
    # Group 1: 作者文字部分（中文/英文/CamelCase拼音）
    # Group 2: 左括号（全角/半角）
    # Group 3: 年份 4位数字
    # Group 5: 右括号（全角/半角）
    pattern = re.compile(
        r'((?:[\u4e00-\u9fff]{1,6}(?:[和与及、][\u4e00-\u9fff]{1,4})*(?:等)?)'  # 中文作者(含多作者和"等")
        r'|(?:[A-Z][a-z]+(?:[A-Z][a-z]+)+)'              # CamelCase 拼音名（如 BiyuTang）
        r'|(?:[A-Z][a-zA-Z]+(?:\s+(?:et\s+al\.?|and\s+[A-Z][a-zA-Z]+))*)'  # 普通英文作者
        r')'
        r'([（(])'     # 左括号
        r'((19|20)\d{2})'  # 年份
        r'([）)])'     # 右括号
    )

    for m in pattern.finditer(text):
        author_text = m.group(1)
        year = m.group(3)
        full_match = m.group(0)
        match_end = m.end()

        # 提取第一作者姓氏用于查找
        zh_m = re.match(r'^([\u4e00-\u9fff]{1,3})', author_text)
        camel_m = re.match(r'^([A-Z][a-z]+(?:[A-Z][a-z]+)+)$', author_text)
        en_m = re.match(r'^([A-Z][a-zA-Z]+)', author_text)

        key = None
        if zh_m:
            # 中文：取姓（第一个字）→ 拼音查
            surname = zh_m.group(1)[0]
            pinyin = _surname_to_pinyin(surname)
            key = ay_lookup.get((pinyin, year)) or ay_lookup.get((surname, year))
        elif camel_m:
            # CamelCase 拼音名（如 BiyuTang）：
            # 先尝试最后一个词（姓），再尝试第一个词（名，用于"名在前"格式如 Biyu Tang）
            words = re.findall(r'[A-Z][a-z]+', author_text)
            if words:
                # 尝试最后一个词作姓
                key = ay_lookup.get((words[-1].lower(), year))
                if not key and len(words) > 1:
                    # 尝试第一个词（名前置情况：Biyu Tang → biyu）
                    key = ay_lookup.get((words[0].lower(), year))
                if not key:
                    # 尝试所有词
                    for w in words:
                        key = ay_lookup.get((w.lower(), year))
                        if key:
                            break
        elif en_m:
            # 普通英文：第一个词（姓）
            en_name = en_m.group(1).lower()
            en_name = re.sub(r'[^a-z]', '', en_name)
            key = ay_lookup.get((en_name, year))

        # 追加原文，若找到 key 则在右括号后插入 \cite
        result.append(text[pos:m.start()])
        if key:
            result.append(full_match + f'\\cite{{{key}}}')
        else:
            result.append(full_match)
        pos = match_end

    result.append(text[pos:])
    return ''.join(result)

def escape_meta(text: str) -> str:
    """元数据字段的轻量转义（标题、姓名等，保留中文标点）"""
    if not text:
        return ''
    # 只转义 & % # _ 等，不转义括号（中文括号无需转义）
    for char, replacement in [('&', r'\&'), ('%', r'\%'), ('#', r'\#')]:
        text = text.replace(char, replacement)
    return text


def strip_section_number(title: str) -> str:
    """剔除节标题里的原始章节编号前缀，避免 LaTeX 自动编号与原文编号叠加。

    例：
        '3.1信托行业...'      → '信托行业...'
        '4.2.1运营体系搭建'   → '运营体系搭建'
        '3.2.1运营类模式'     → '运营类模式'
        '4.5.2.1公司层面优化' → '公司层面优化'
        '图4.2 W信托...'      → '图4.2 W信托...'  （图题不处理）
        'W信托基本情况'       → 'W信托基本情况'    （无前缀，不变）
    """
    if not title:
        return title
    # 匹配形如 "3." / "3.1" / "3.1.1" / "3.1.1.1" 开头的编号（仅数字+点）
    # 后面必须跟非数字字符（汉字、字母等），避免把"3.14..."这类误删
    m = re.match(r'^(\d+(?:\.\d+)*)\s*(?=[^\d\s.])', title)
    if m:
        return title[m.end():]
    return title

# ── BibTeX 生成 ─────────────────────────────────────────────────────────────

def _make_bib_key(ref_text: str, idx: int, used_keys: set) -> str:
    """从参考文献原文生成 BibTeX key，格式：作者姓年份关键词"""
    text = re.sub(r'^\[\d+\]\s*', '', ref_text.strip())

    # 提取年份
    year_m = re.search(r'\b(19|20)\d{2}\b', text)
    year = year_m.group(0) if year_m else 'nodate'

    # 提取第一作者姓（英文：取逗号前 / 中文：取前2字）
    # 英文模式：Lastname, F. 或 Lastname F.
    en_m = re.match(r'([A-Z][a-zA-ZÀ-ÿ\-]+),?\s+[A-Z]', text)
    # 中文模式：开头是中文字符
    zh_m = re.match(r'^([\u4e00-\u9fff]{2,3})[、，,\s（(]', text)
    # 机构名（全大写英文单词）
    org_m = re.match(r'^([A-Z]{2,})[.\s]', text)

    if zh_m:
        # 中文作者：转拼音首字母（简单方案：直接用字符unicode位置做hash，或保留汉字）
        author_part = zh_m.group(1).lower()
        # 简单拼音映射（常见姓）
        pinyin_map = {
            '赵': 'zhao', '钱': 'qian', '孙': 'sun', '李': 'li', '周': 'zhou',
            '吴': 'wu', '郑': 'zheng', '王': 'wang', '冯': 'feng', '陈': 'chen',
            '褚': 'chu', '卫': 'wei', '蒋': 'jiang', '沈': 'shen', '韩': 'han',
            '杨': 'yang', '朱': 'zhu', '秦': 'qin', '尤': 'you', '许': 'xu',
            '何': 'he', '吕': 'lv', '施': 'shi', '张': 'zhang', '孔': 'kong',
            '曹': 'cao', '严': 'yan', '华': 'hua', '金': 'jin', '魏': 'wei',
            '陶': 'tao', '姜': 'jiang', '戚': 'qi', '谢': 'xie', '邹': 'zou',
            '喻': 'yu', '柏': 'bai', '水': 'shui', '窦': 'dou', '章': 'zhang',
            '云': 'yun', '苏': 'su', '潘': 'pan', '葛': 'ge', '奚': 'xi',
            '范': 'fan', '彭': 'peng', '郎': 'lang', '鲁': 'lu', '韦': 'wei',
            '昌': 'chang', '马': 'ma', '苗': 'miao', '凤': 'feng', '花': 'hua',
            '方': 'fang', '俞': 'yu', '任': 'ren', '袁': 'yuan', '柳': 'liu',
            '酆': 'feng', '鲍': 'bao', '史': 'shi', '唐': 'tang', '费': 'fei',
            '廉': 'lian', '岑': 'cen', '薛': 'xue', '雷': 'lei', '贺': 'he',
            '倪': 'ni', '汤': 'tang', '滕': 'teng', '殷': 'yin', '罗': 'luo',
            '毕': 'bi', '郝': 'hao', '邬': 'wu', '安': 'an', '常': 'chang',
            '乐': 'le', '于': 'yu', '时': 'shi', '傅': 'fu', '皮': 'pi',
            '卞': 'bian', '齐': 'qi', '康': 'kang', '伍': 'wu', '余': 'yu',
            '元': 'yuan', '卜': 'bu', '顾': 'gu', '孟': 'meng', '平': 'ping',
            '黄': 'huang', '和': 'he', '穆': 'mu', '萧': 'xiao', '尹': 'yin',
            '姚': 'yao', '邵': 'shao', '湛': 'zhan', '汪': 'wang', '祁': 'qi',
            '毛': 'mao', '禹': 'yu', '狄': 'di', '米': 'mi', '贝': 'bei',
            '明': 'ming', '臧': 'zang', '计': 'ji', '伏': 'fu', '成': 'cheng',
            '戴': 'dai', '谈': 'tan', '宋': 'song', '茅': 'mao', '庞': 'pang',
            '熊': 'xiong', '纪': 'ji', '舒': 'shu', '屈': 'qu', '项': 'xiang',
            '祝': 'zhu', '董': 'dong', '梁': 'liang', '杜': 'du', '阮': 'ruan',
            '蓝': 'lan', '闵': 'min', '席': 'xi', '季': 'ji', '麻': 'ma',
            '强': 'qiang', '贾': 'jia', '路': 'lu', '娄': 'lou', '危': 'wei',
            '江': 'jiang', '童': 'tong', '颜': 'yan', '郭': 'guo', '梅': 'mei',
            '盛': 'sheng', '林': 'lin', '刁': 'diao', '钟': 'zhong', '徐': 'xu',
            '邱': 'qiu', '骆': 'luo', '高': 'gao', '夏': 'xia', '蔡': 'cai',
            '田': 'tian', '樊': 'fan', '胡': 'hu', '凌': 'ling', '霍': 'huo',
            '虞': 'yu', '万': 'wan', '支': 'zhi', '柯': 'ke', '昝': 'zan',
            '管': 'guan', '卢': 'lu', '莫': 'mo', '经': 'jing', '房': 'fang',
            '裘': 'qiu', '缪': 'miao', '干': 'gan', '解': 'xie', '应': 'ying',
            '宗': 'zong', '丁': 'ding', '宣': 'xuan', '贲': 'ben', '邓': 'deng',
            '郁': 'yu', '单': 'shan', '杭': 'hang', '洪': 'hong', '包': 'bao',
            '诸': 'zhu', '左': 'zuo', '石': 'shi', '崔': 'cui', '吉': 'ji',
            '钮': 'niu', '龚': 'gong',
        }
        surname = zh_m.group(1)[0]
        author_part = pinyin_map.get(surname, 'zh')
        # 只取姓的拼音，不保留剩余中文字符
    elif en_m:
        author_part = en_m.group(1).lower()
        # 去除特殊字符
        author_part = re.sub(r'[^a-z]', '', author_part)
    elif org_m:
        author_part = org_m.group(1).lower()
    else:
        author_part = f'ref{idx:03d}'

    # 提取标题关键词（前2个英文词或前3个中文字）
    # 去掉作者和年份后取标题
    title_part = re.sub(r'^[^a-zA-Z\u4e00-\u9fff]*', '', text)
    title_part = re.sub(r'\b(19|20)\d{2}\b', '', title_part)
    en_words = re.findall(r'[a-zA-Z]+', title_part)
    # 取第一个有意义的词（跳过介词/连词）
    stopwords = {'a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'for',
                 'and', 'or', 'but', 'with', 'from', 'by', 'how', 'what',
                 'its', 'as', 'is', 'are', 'be', 'an'}
    kw = next((w.lower() for w in en_words if w.lower() not in stopwords and len(w) > 2), '')
    if not kw:
        zh_words = re.findall(r'[\u4e00-\u9fff]{2,4}', title_part)
        kw = zh_words[0] if zh_words else ''

    key = f'{author_part}{year}{kw}'
    # BibTeX key 只允许 ASCII 字母数字，中文字符全部剥除
    key = re.sub(r'[^a-zA-Z0-9]', '', key)[:40]

    # 保证唯一性
    base_key = key
    suffix = 2
    while key in used_keys:
        key = f'{base_key}{suffix}'
        suffix += 1
    used_keys.add(key)
    return key


def _parse_ref_to_bibtex(ref_text: str, key: str) -> str:
    """把一条参考文献原文解析为 BibTeX 条目（规则based）"""
    text = re.sub(r'^\[\d+\]\s*', '', ref_text.strip())
    text = text.replace(r'\&', '&').replace(r'\%', '%')

    # ── 优先检测 APA 机构引用格式：机构名. (Year). Title. ──
    # 例：高力国际. (2025). 2025 年酒店业展望报告.
    #     美国旅游协会（U.S. Travel Association）. (2024). U.S. Travel & Tourism Statistics
    #     Washington State University Carson College of Business. (2024). Hospitality...
    #     德勤. (2024). 2024 年假期旅游调查.
    m_org_apa = re.match(r'^(.+?)\.\s*\((19|20\d{2})\)\.\s*(.+)', text.strip())
    if m_org_apa:
        org_candidate = m_org_apa.group(1).strip()
        year_org = m_org_apa.group(2)
        title_raw_org = m_org_apa.group(3).strip().rstrip('.')
        # 判断是否机构名（不是个人名）：
        # 个人名特征 = 含逗号 + 较短（如 "Verma, Y" "Quach, T"）
        # 机构名特征 = 无逗号，或纯汉字机构，或多词英文机构
        has_comma = ',' in org_candidate
        is_short_personal = has_comma and len(org_candidate) < 25
        is_org = not is_short_personal
        if is_org:
            def _esc(s):
                return s.replace('&', r'\&').replace('%', r'\%')
            # 截取标题到第一个句点
            title_end_m = re.search(r'\.\s*(Retrieved|Available|http|DOI|doi|\[)', title_raw_org)
            title_org = title_raw_org[:title_end_m.start()].strip() if title_end_m else title_raw_org
            title_org = title_org.rstrip('.,。')
            return (
                f'@misc{{{key},\n'
                f'  author    = {{{{{_esc(org_candidate)}}}}},\n'
                f'  title     = {{{_esc(title_org)}}},\n'
                f'  year      = {{{year_org}}}\n'
                f'}}'
            )

    # 判断是否中文条目（首字符是汉字）
    is_zh = bool(re.match(r'^[\u4e00-\u9fff]', text))

    # 全角标点规范化（Word 导出常见问题）
    text_norm = text
    if is_zh:
        # 中文条目：全角逗号/冒号 → 半角
        text_norm = text.replace('，', ',').replace('：', ':')
        text_norm = re.sub(r'["\u201c\u201d]', '"', text_norm)
    else:
        # 英文条目：全角逗号 → ", "（保持 ". " 不变）
        text_norm = text.replace('，', ', ').replace('：', ': ')
        text_norm = re.sub(r'["\u201c\u201d]', '"', text_norm)

    has_journal_marker = bool(re.search(r'\[J\]|\[j\]', text_norm))
    has_book_marker = bool(re.search(r'\[M\]|\[m\]|《|》|出版社|Press\b|McGraw|Harvard Business Press', text_norm))
    has_online_marker = bool(re.search(r'\[EB/OL\]|\[eb/ol\]|EB/OL', text_norm))
    has_volume = bool(re.search(r',\s*\d+\s*\(\d+\)', text_norm))

    if has_online_marker:
        entry_type = 'misc'
    elif has_book_marker and not has_journal_marker and not has_volume:
        entry_type = 'book'
    else:
        entry_type = 'article'

    year_m = re.search(r'\b(19|20)(\d{2})\b', text_norm)
    year = year_m.group(0) if year_m else ''

    # ── 提取作者和标题 ─────────────────────────────────────────────
    def _split_author_title(txt: str, zh: bool):
        """返回 (author_raw, rest_after_separator)"""
        if zh:
            # 模式0（最高优先级）: 标准中文学术引用格式 "作者. 标题[J/M/C/R/N/Z]."
            # 格式：中文姓名（逗号分隔）+ ". " + 标题（通常接[文献类型标识]或汉字）
            # 例: "李卫华, 王雪. 药品价格...[J]."
            # 例: "国家医疗保障局. 2023年医疗保障事业..."（标题含数字开头）
            # 特征："." 后接汉字、数字+汉字、方括号、书名号
            m_std = re.match(
                r'^([\u4e00-\u9fff\w·，,、\s（）()]+?)'  # 作者部分
                r'\.\s*'                                  # 英文句点（可带空格）
                r'(?=[\u4e00-\u9fff"「《〔\[0-9])',       # 后面是汉字/引号/方括号/数字
                txt
            )
            if m_std:
                author_candidate = m_std.group(1).strip()
                rest = txt[m_std.end():].strip()
                # 验证作者部分：必须含汉字，不能太长（>50字符通常是标题混入了）
                if re.search(r'[\u4e00-\u9fff]', author_candidate) and len(author_candidate) <= 50:
                    return author_candidate, rest

            # 模式1a: 作者,"标题" 格式（半角引号，如 吴芳,"标题",）
            m0 = re.match(r'^([^,""《]{1,20}),\s*"(.+?)"', txt)
            if m0:
                return m0.group(1).strip(), m0.group(2).strip()

            # 模式1b: 作者，"标题" 格式（全角逗号+全角引号，如 谢伟，"技术学习..."）
            m0b = re.match(r'^([\u4e00-\u9fff]{1,10}(?:[，,、]\s*[\u4e00-\u9fff]{1,10})*)\s*[，,]\s*[""「]', txt)
            if m0b:
                sep_pos = m0b.end() - 1
                return m0b.group(1).strip(), txt[sep_pos:].strip()

            # 模式2: 作者(年) 格式（如 赵敏,宁振波 (2020),《书名》）
            m1 = re.match(r'^([\u4e00-\u9fff\s,、·]+?)\s*[(（]\d{4}[)）]', txt)
            if m1:
                return m1.group(1).strip(), txt[m1.end():].lstrip(',、。. ')

            # 模式3: 中文句号分隔（全角）
            zh_dot = txt.find('。')
            if zh_dot > 0:
                return txt[:zh_dot].strip(), txt[zh_dot+1:].strip()

            # 模式4: 英文句点后面直接跟汉字或引号（无空格，如 "唐未兵.战略转型" 或 '."标题"'）
            for m2 in re.finditer(r'\.(?=[\u4e00-\u9fff""「])', txt):
                pos = m2.start()
                return txt[:pos].strip(), txt[pos+1:].strip()

            # 模式5: ". " 后跟大写字母（英文句号+空格，后跟大写）
            for m3 in re.finditer(r'\. ', txt):
                pos = m3.start()
                after = txt[pos+2:pos+3]
                if after and after[0].isupper():
                    return txt[:pos].strip(), txt[pos+2:].strip()

            # 模式6: 全角逗号后接《书名》（如 谢伟，《战略管理》）
            m6 = re.match(r'^([\u4e00-\u9fff]{1,10}(?:[，,]\s*[\u4e00-\u9fff]{1,10})*)\s*[，,]\s*[《]', txt)
            if m6:
                return m6.group(1).strip(), txt[m6.end()-1:].strip()

            return '', txt
        else:
            # 英文格式：先尝试匹配 "作者列表 (年). 标题" 模式
            # 这样能一步拿到完整 author（含年份括号前）和 title
            year_pattern = re.search(r'\((19|20)\d{2}\)\. ', txt)
            if year_pattern:
                # author = 年份括号前的内容，rest = 年份括号后的 ". 标题..."
                # 找年份括号开始位置
                yp_start = year_pattern.start()
                author_part = txt[:yp_start].strip().rstrip(',.')
                rest_part = txt[year_pattern.end():].strip()
                return author_part, rest_part

            # 模式2："作者.标题" 格式（无空格，如 "Biyu Tang.Analysis of..."）
            # 匹配：点前是英文姓名（姓名格式），点后是大写字母
            for m in re.finditer(r'\.(?=[A-Z])', txt):
                pos = m.start()
                before = txt[:pos]
                after = txt[pos+1:]
                # 确认点前是英文姓名（最后一个词是大写开头的姓，如 "Tang"）
                before_words = before.strip().split()
                if before_words and re.match(r'^[A-Z][a-z]+$', before_words[-1]):
                    # 不是缩写（缩写通常只有1-2个字符，如 "J." "M."）
                    if len(before_words[-1]) > 2:
                        return before.strip(), after.strip()

            # 兜底：找 ". " 后面是大写字母（跳过缩写 K. M. J. A. 等）
            for m in re.finditer(r'\. ', txt):
                pos = m.start()
                after = txt[pos+2:pos+25]
                if not after:
                    continue
                first = after[0]
                if first.islower():
                    continue
                if re.match(r'^[A-Z]\. ', after):
                    continue
                if first.isdigit():
                    continue
                if re.match(r'^[A-Z][a-z]?\.,', after):
                    continue
                return txt[:pos].strip(), txt[pos+2:].strip()
            return '', txt

    author_raw, rest = _split_author_title(text_norm, is_zh)

    # 格式化 author
    if author_raw:
        if is_zh:
            parts = re.split(r'[、,]+', author_raw)
            author = ' and '.join(f'{{{p.strip()}}}' for p in parts if p.strip())
        else:
            author_raw = re.sub(r'\s*[&]\s*', ' and ', author_raw)
            author_raw = re.sub(r'[.,;(（\s]+$', '', author_raw)
            parts = re.split(r'\s+and\s+', author_raw, flags=re.IGNORECASE)
            author = ' and '.join(f'{{{p.strip()}}}' for p in parts if p.strip())
    else:
        author = ''

    # 提取标题
    type_marker = re.search(r'\[[A-Z/]+\]', rest)
    if type_marker:
        title = rest[:type_marker.start()].strip().rstrip('.,。，')
    else:
        first_dot = re.search(r'[.。]', rest)
        title = rest[:first_dot.start()].strip() if first_dot else rest[:100].strip()
    title = re.sub(r'[《》]', '', title).strip()

    # 期刊名、卷期页
    journal, volume, number, pages = '', '', '', ''
    if entry_type == 'article':
        vol_m = re.search(r',?\s*(\d+)\s*[（(](\d+[-–]\d+|\d+)[）)],?\s*([\d–-]+)', text_norm)
        if vol_m:
            volume = vol_m.group(1)
            number = vol_m.group(2)
            pages = re.sub(r'[-–]', '--', vol_m.group(3))
            j_start = text_norm.rfind('.', 0, vol_m.start())
            if j_start >= 0:
                journal = text_norm[j_start+1:vol_m.start()].strip().rstrip(',. ')

    publisher, address = '', ''
    if entry_type == 'book':
        pub_m = re.search(r'[:：]\s*([^,.]+(?:Press|出版社|Publisher)[^,.]*)', text_norm)
        if pub_m:
            publisher = pub_m.group(1).strip()
        addr_m = re.search(r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s*[:：]', text_norm)
        if addr_m:
            address = addr_m.group(1).strip()

    def _bib_escape(s: str) -> str:
        return s.replace('&', r'\&') if s else s

    fields = []
    if author:
        fields.append(f'  author    = {{{_bib_escape(author)}}}')
    if title:
        fields.append(f'  title     = {{{_bib_escape(title)}}}')
    if journal:
        fields.append(f'  journal   = {{{_bib_escape(journal)}}}')
    if volume:
        fields.append(f'  volume    = {{{volume}}}')
    if number:
        fields.append(f'  number    = {{{number}}}')
    if pages:
        fields.append(f'  pages     = {{{pages}}}')
    if year:
        fields.append(f'  year      = {{{year}}}')
    if publisher:
        fields.append(f'  publisher = {{{_bib_escape(publisher)}}}')
    if address:
        fields.append(f'  address   = {{{address}}}')
    if entry_type == 'misc':
        fields.append(f'  note      = {{[EB/OL]}}')

    body = ',\n'.join(fields)
    return f'@{entry_type}{{{key},\n{body}\n}}'

def generate_bibtex(refs: list, output_dir: Path) -> tuple:
    """把参考文献列表生成 ref/refs.bib，返回 (编号→key 映射字典, author-year lookup 字典)

    返回：
      mapping:   {编号(int): bibtex_key}
      ay_lookup: {(surname_pinyin_or_lower, year_str): bibtex_key}
                 用于正文中 author-year 行文引用的匹配
    """
    ref_dir = output_dir / 'ref'
    ref_dir.mkdir(exist_ok=True)

    used_keys: set = set()
    mapping = {}    # {编号(int): key}
    ay_lookup = {}  # {(surname, year): key}
    entries = []

    for i, ref in enumerate(refs, start=1):
        key = _make_bib_key(ref, i, used_keys)
        mapping[i] = key
        entry = _parse_ref_to_bibtex(ref, key)
        entries.append(entry)

        # 构建 author-year lookup
        # 从 ref 原文提取：所有作者姓 + 年份（多作者情况都注册，以防正文引用非第一作者）
        text_clean = re.sub(r'^\[\d+\]\s*', '', ref.strip())
        year_m = re.search(r'\b(19|20)\d{2}\b', text_clean)
        if year_m:
            year = year_m.group(0)
            # 提取作者段：截止到第一个 ". " 或 "。"（句点+空格，排除姓名缩写中的点）
            # 中文格式：曹玉,肖华.标题  英文格式：Smith J, Tang B. Title
            author_segment = re.split(r'\.\s+[^\d]|[.。]\s', text_clean)[0]
            # 中文作者：仅匹配2-4字的姓名（避免把标题词当作者）
            zh_authors = re.findall(r'[\u4e00-\u9fff]{2,4}(?=\s*[,，、和与&以]|\s*$|\s*等)', author_segment)
            if not zh_authors:
                # 兜底：取首字段（逗号或顿号前）的中文词
                first_author_seg = re.split(r'[,，、和与&]', author_segment)[0].strip()
                zh_authors = re.findall(r'[\u4e00-\u9fff]{2,4}', first_author_seg)
            if zh_authors:
                for zh_name in zh_authors[:4]:  # 最多取前4个作者
                    surname_char = zh_name[0]
                    pinyin = _surname_to_pinyin(surname_char)
                    if (pinyin, year) not in ay_lookup:
                        ay_lookup[(pinyin, year)] = key
                    if (surname_char, year) not in ay_lookup:
                        ay_lookup[(surname_char, year)] = key
            else:
                # 英文/拼音作者（单词序列，逗号分隔）
                # 支持：Biyu Tang, Smith J, BiyuTang 等格式
                en_authors = re.findall(r'[A-Z][a-zA-ZÀ-ÿ\-]+', author_segment)
                for en_name in en_authors[:4]:  # 最多取前4个作者
                    name_lower = re.sub(r'[^a-z]', '', en_name.lower())
                    if name_lower and (name_lower, year) not in ay_lookup:
                        ay_lookup[(name_lower, year)] = key

    # 映射注释表
    map_lines = ['% ' + '=' * 58,
                 '% 参考文献映射表（原编号 → BibTeX key）',
                 '% ' + '=' * 58]
    for i, key in mapping.items():
        map_lines.append(f'% [{i:2d}] → {key}')
    map_lines.append('% ' + '=' * 58)
    map_lines.append('')

    bib_content = '\n'.join(map_lines) + '\n\n'.join(entries) + '\n'
    (ref_dir / 'refs.bib').write_text(bib_content, encoding='utf-8')
    return mapping, ay_lookup


# ── 章节渲染 ────────────────────────────────────────────────────────────────
CMD_MAP = {1: 'chapter', 2: 'section', 3: 'subsection', 4: 'subsubsection'}

def render_content_items(items: list, cite_mapping: dict = None, ay_lookup: dict = None) -> str:
    """把章节的 content 列表渲染成 LaTeX 代码"""
    lines = []
    for item in items:
        t = item.get('type', '')
        if t == 'section':
            lvl = item.get('level', 2)
            cmd = CMD_MAP.get(lvl, 'paragraph')
            title = escape_meta(strip_section_number(item.get('title', '')))
            lines.append(f'\n\\{cmd}{{{title}}}\n')
        elif t == 'text':
            content = item.get('content', '').strip()
            if content:
                lines.append(convert_citations(escape_latex(content), cite_mapping, ay_lookup) + '\n')
        elif t == 'table':
            lines.append(render_table(item))
        elif t == 'list_item':
            content = convert_citations(escape_latex(item.get('content', '')), cite_mapping, ay_lookup)
            lines.append(f'\\item {content}')
        elif t == 'list_start':
            lines.append('\\begin{itemize}')
        elif t == 'list_end':
            lines.append('\\end{itemize}\n')
    return '\n'.join(lines)

def render_table(item: dict) -> str:
    """把表格数据渲染为 thuthesis 标准三线表（booktabs + tabularx，无竖线）

    列宽策略：
    - 分析各列最大内容长度（字符数），按比例分配 tabularx X 列宽
    - 短列（序号、日期等）用 l（左对齐固定宽）；长列用 X（自动拉伸）
    - 至少有一列为 X（tabularx 要求）
    """
    rows = item.get('rows', [])
    if not rows:
        return ''
    caption = escape_latex(item.get('caption', '').strip())
    ncols = max(len(r) for r in rows)

    # 计算每列最大内容长度
    col_max_lens = []
    for ci in range(ncols):
        max_len = 0
        for row in rows:
            if ci < len(row):
                cell_text = str(row[ci])
                # 汉字算2个字符宽度
                char_width = sum(2 if '\u4e00' <= c <= '\u9fff' else 1 for c in cell_text)
                max_len = max(max_len, char_width)
        col_max_lens.append(max(max_len, 1))

    # 判断哪些列用固定宽（l），哪些用 X（自动拉伸）
    # 规则：列最大宽度 <= 12 字符等效 → 固定宽；其余用 X
    SHORT_THRESHOLD = 12
    x_count = sum(1 for l in col_max_lens if l > SHORT_THRESHOLD)
    if x_count == 0:
        # 全是短列，最长那列改为 X
        x_count = 1
        max_idx = col_max_lens.index(max(col_max_lens))
        col_specs = ['l'] * ncols
        col_specs[max_idx] = 'X'
    else:
        col_specs = ['X' if l > SHORT_THRESHOLD else 'l' for l in col_max_lens]

    col_spec = ' '.join(col_specs)

    lines = ['']
    if caption:
        lines += [
            '\\begin{table}[htbp]',
            f'  \\caption{{{caption}}}',
            '  \\label{tab:auto}',
            f'  \\begin{{tabularx}}{{\\linewidth}}{{{col_spec}}}',
            '    \\toprule',
        ]
    else:
        lines += [
            '\\begin{table}[htbp]',
            f'  \\begin{{tabularx}}{{\\linewidth}}{{{col_spec}}}',
            '    \\toprule',
        ]
    for i, row in enumerate(rows):
        cells = [escape_latex(str(c)) for c in row]
        while len(cells) < ncols:
            cells.append('')
        lines.append('    ' + ' & '.join(cells) + r' \\')
        if i == 0:  # 表头后加 midrule
            lines.append('    \\midrule')
    lines += [
        '    \\bottomrule',
        '  \\end{tabularx}',
        '\\end{table}',
        '',
    ]
    return '\n'.join(lines)

# ── 主渲染逻辑 ───────────────────────────────────────────────────────────────
def render_project(json_path: str, output_dir: str):
    # 1. 加载 JSON
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 2. 从 thuthesis 源目录复制类文件和基础资源
    # 查找顺序：
    #   1. 环境变量 THUTHESIS_DIR
    #   2. setup.sh 拉取的位置 /tmp/thuthesis-latest
    #   3. 脚本同目录下的 thuthesis/（本地开发用）
    _candidates = [
        os.environ.get('THUTHESIS_DIR', ''),
        '/tmp/thuthesis-latest',
        str(Path(__file__).parent.parent / 'thuthesis'),
    ]
    src_base = None
    for _c in _candidates:
        if _c and Path(_c).is_dir() and (Path(_c) / 'thuthesis.cls').exists():
            src_base = Path(_c)
            break
    if src_base is None:
        print("❌ 找不到 thuthesis 源文件！请先运行：")
        print("   bash <skill目录>/scripts/setup.sh <skill目录>")
        print("   或设置环境变量 THUTHESIS_DIR 指向 thuthesis 目录")
        sys.exit(1)
    cls_files = [
        'thuthesis.cls', 'thuthesis.dtx', 'thuthesis.ins',
        'thuthesis-numeric.bst', 'thuthesis-author-year.bst', 'thuthesis-bachelor.bst',
        'thuthesis-numeric.bbx', 'thuthesis-author-year.bbx', 'thuthesis-bachelor.bbx',
        'thuthesis-numeric.cbx', 'thuthesis-author-year.cbx', 'thuthesis-bachelor.cbx',
        'thuthesis-inline.cbx',
        'thu-fig-logo.pdf', 'thu-text-logo.pdf',
        'dtx-style.sty',
    ]
    for f in cls_files:
        src = src_base / f
        if src.exists():
            shutil.copy2(src, output_dir / f)

    # 3. 创建子目录
    for d in ['data', 'figures', 'ref']:
        (output_dir / d).mkdir(exist_ok=True)

    # 复制提取出的图片到 LaTeX 项目的 figures/ 目录
    src_figures = Path(json_path).parent / 'figures'  # output/figures/
    dst_figures = output_dir / 'figures'
    dst_figures.mkdir(exist_ok=True)
    if src_figures.exists():
        copied = 0
        for img in src_figures.iterdir():
            if img.is_file():
                shutil.copy2(img, dst_figures / img.name)
                copied += 1
        print(f'✅ figures/  ({copied} 张图片)')

    # 4. 初始化 Jinja2 环境
    # 模板目录查找顺序：
    #   1. scripts/../templates/         （docx2thu 开发目录结构）
    #   2. scripts/../assets/templates/  （skill 安装目录结构）
    _script_dir = Path(__file__).parent
    _templates_candidates = [
        _script_dir.parent / 'templates',
        _script_dir.parent / 'assets' / 'templates',
    ]
    templates_dir = next((p for p in _templates_candidates if p.is_dir()), None)
    if templates_dir is None:
        print("❌ 找不到模板目录！期望路径：")
        for p in _templates_candidates:
            print(f"   {p}")
        sys.exit(1)
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    # 注册转义过滤器
    env.filters['escape_latex'] = escape_latex
    env.filters['escape_meta'] = escape_meta

    meta = data.get('meta', {})

    # title_en 超过200字符说明把摘要误当标题了，截断保护
    if meta.get('title_en') and len(meta['title_en']) > 200:
        # 取第一句（到第一个句号）
        first_sentence = meta['title_en'].split('.')[0].strip()
        meta['title_en'] = first_sentence if len(first_sentence) > 10 else meta['title_en'][:200]

    # 补全日期为 ISO 格式：
    #   "2025-11" → "2025-11-01"
    #   "25-11"   → 补全年份前缀（当前世纪）→ "2025-11-01"
    #   "二○二六年四月" → "2026-04-01"（build_parsed 已处理，此处双重兜底）
    date_str = meta.get('date', '')
    CN_DIGITS_R = {'○': '0', '〇': '0', '一': '1', '二': '2', '三': '3', '四': '4',
                   '五': '5', '六': '6', '七': '7', '八': '8', '九': '9'}
    if date_str and re.search(r'[\u4e00-\u9fff○〇]', date_str):
        # 含中文字符，先处理复合月份再转阿拉伯数字
        d_pre = re.sub(r'十二月', '#12月', date_str)
        d_pre = re.sub(r'十一月', '#11月', d_pre)
        d_pre = re.sub(r'十月', '#10月', d_pre)
        d_arabic = ''.join(CN_DIGITS_R.get(c, c) for c in d_pre).replace('#', '')
        m = re.search(r'(\d{4})\s*年\s*(\d{1,2})\s*月', d_arabic)
        if m:
            date_str = f"{m.group(1)}-{int(m.group(2)):02d}"
            meta['date'] = date_str
    if date_str:
        parts = date_str.split('-')
        if len(parts) == 2:
            yr, mo = parts
            if len(yr) == 2:  # "25" → "2025"
                yr = '20' + yr
            meta['date'] = f"{yr}-{mo}-01"
        elif len(parts) == 1 and len(date_str) <= 4:
            meta['date'] = ''  # 无效日期清空

    # 日期兜底：如果为空，用当前年月
    if not meta.get('date'):
        import datetime
        today = datetime.date.today()
        meta['date'] = f"{today.year}-{today.month:02d}-01"
        print(f'   ℹ️  封面日期为空，使用当前年月：{meta["date"]}')

    # 5. 渲染 thusetup.tex
    tmpl = env.get_template('thusetup.tex.j2')
    (output_dir / 'thusetup.tex').write_text(
        tmpl.render(meta=meta), encoding='utf-8'
    )
    print('✅ thusetup.tex')

    # 6. 渲染 abstract.tex
    # 修复：如果 keywords_en 是逐词拆散的（含停用词），从 abstract_en 末尾重新提取
    _EN_STOPWORDS = {'and', 'of', 'for', 'the', 'a', 'an', 'in', 'on', 'at',
                     'to', 'with', 'by', 'from', 'or', 'but', 'nor', 'as'}
    keywords_en = data.get('keywords_en', [])
    if keywords_en and any(w.lower() in _EN_STOPWORDS for w in keywords_en):
        # 检测到逐词拆散，尝试从 abstract_en 重新提取
        abstract_en_text = data.get('abstract_en', '')
        m_kw = re.search(r'[Kk]ey\s*[Ww]ords[：:\s]*(.+)$', abstract_en_text.strip())
        if m_kw:
            kw_text = m_kw.group(1).strip()
            keywords_en = [k.strip() for k in re.split(r'[；;，,]+', kw_text) if k.strip()]
            print(f'   ℹ️  英文关键词已从 abstract 重新提取: {keywords_en}')

    tmpl = env.get_template('abstract.tex.j2')
    (output_dir / 'data' / 'abstract.tex').write_text(
        tmpl.render(
            abstract_cn=escape_latex(data.get('abstract_cn', '')),
            keywords_cn=[escape_latex(k) for k in data.get('keywords_cn', [])],
            abstract_en=escape_latex(data.get('abstract_en', '')),
            keywords_en=[escape_latex(k) for k in keywords_en],
        ), encoding='utf-8'
    )
    print('✅ data/abstract.tex')

    # 7. 孤儿缩略语检测 + 正文补写（必须在章节渲染之前，保证 data 只修改一次）
    data, abbrevs = fix_orphan_abbrevs(data)

    # 7b. 生成 BibTeX 映射（提前，章节渲染时用于 \cite 替换）
    refs = data.get('references', [])
    cite_mapping, ay_lookup = generate_bibtex(refs, output_dir)
    print(f'✅ ref/refs.bib  ({len(refs)} 条参考文献，author-year lookup: {len(ay_lookup)} 条)')

    # 8. 渲染每个章节（使用补写后的 data 和 cite_mapping）
    chapters_info = []
    for i, chap in enumerate(data.get('chapters', []), start=1):
        filename = f'chap{i:02d}'
        title = escape_meta(chap.get('title', ''))
        blocks = []
        for item in chap.get('content', []):
            t = item.get('type', '')
            if t == 'section':
                blocks.append({
                    'type': 'heading',
                    'level': item.get('level', 2),
                    'title': escape_meta(strip_section_number(item.get('title', ''))),
                })
            elif t == 'text':
                content = item.get('content', '').strip()
                # 跳过独立的图题/表题行（已被收入 figure/table 的 caption，避免重复）
                if re.match(r'^[图表]\s*\d+[-–—]\d+', content):
                    continue
                content = convert_citations(escape_latex(content), cite_mapping, ay_lookup)
                if content:
                    blocks.append({'type': 'paragraph', 'text': content})
            elif t == 'figure':
                embed = item.get('embed', '')
                caption = item.get('caption', '')
                # ★ 优先从 item 自身的 path 字段获取文件名（parse_docx 新格式）
                # 兼容旧格式：从 data['figures'] 字典中查找
                fig_filename = ''
                if item.get('path'):
                    fig_filename = Path(item['path']).name  # 去掉 'figures/' 前缀
                else:
                    fig_info = data.get('figures', {}).get(embed, {})
                    fig_filename = fig_info.get('filename', '')
                    if not caption:
                        caption = fig_info.get('caption', '')
                if fig_filename:
                    # 跳过 SVG（依赖 inkscape，可能不可用），只处理 PNG/JPG/PDF
                    ext = Path(fig_filename).suffix.lower()
                    if ext == '.svg':
                        print(f'   ⚠️  跳过 SVG 图片: {fig_filename}（LaTeX 不直接支持，请手动转换）')
                    else:
                        cap_clean = clean_caption(caption)
                        label_raw = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '-', cap_clean)[:30]
                        label = re.sub(r'-+', '-', label_raw).strip('-')
                        blocks.append({
                            'type': 'figure',
                            'path': fig_filename,
                            'caption': escape_meta(cap_clean),
                            'label': label,
                        })
            elif t == 'table':
                rows = item.get('rows', [])
                caption = clean_caption(item.get('caption', ''))
                if not rows or item.get('caption', '').startswith('图'):
                    continue
                # 直接用 render_table 生成完整 LaTeX，避免模板列数推断问题
                table_item = {
                    'rows': rows,
                    'caption': caption,
                }
                raw_tex = render_table(table_item)
                if raw_tex.strip():
                    blocks.append({
                        'type': 'raw_latex',
                        'content': raw_tex,
                    })
        tmpl = env.get_template('chapter.tex.j2')
        # 从章编号提取章序号，用于设置 LaTeX counter（保留原文章号）
        # number 字段可能是 "第3章"、"3"、"" 等形式
        raw_num = chap.get('number', '')
        chap_counter = None
        m_num = re.search(r'(\d+)', raw_num)
        if m_num:
            n = int(m_num.group(1))
            chap_counter = n - 1  # \setcounter{chapter}{N-1} 使下一个 \chapter 编为第N章
        chapter_obj = {
            'level': 1,
            'title': title,
            'number': raw_num,
            'chap_counter': chap_counter,
            'content': blocks,
        }
        tex = tmpl.render(chapter=chapter_obj)
        (output_dir / 'data' / f'{filename}.tex').write_text(tex, encoding='utf-8')
        chapters_info.append({'filename': filename, 'title': title})
        print(f'✅ data/{filename}.tex  ({title})')

    # 统计实际渲染出的图片和表格数量（用于控制是否生成插图/附表清单）
    actual_has_figures = any(
        b.get('type') == 'figure'
        for ci in chapters_info
        for tex_path in [output_dir / 'data' / f'{ci["filename"]}.tex']
        if False  # 占位：由下面的 blocks 实时统计
    )
    # 更可靠：直接扫描已生成的 .tex 文件
    has_figures_real = False
    has_tables_real = False
    for ci in chapters_info:
        tex_path = output_dir / 'data' / f'{ci["filename"]}.tex'
        if tex_path.exists():
            tex_content = tex_path.read_text(encoding='utf-8')
            if r'\begin{figure}' in tex_content:
                has_figures_real = True
            if r'\begin{table}' in tex_content or r'\begin{tabularx}' in tex_content:
                has_tables_real = True

    # 8. 渲染 acknowledgements.tex（每行独立段落：单\n → \n\n）
    ack = data.get('acknowledgements', '')
    ack_paragraphs = '\n\n'.join(
        escape_latex(line.strip()) for line in ack.split('\n') if line.strip()
    )
    tmpl = env.get_template('acknowledgements.tex.j2')
    (output_dir / 'data' / 'acknowledgements.tex').write_text(
        tmpl.render(acknowledgements=ack_paragraphs), encoding='utf-8'
    )
    print('✅ data/acknowledgements.tex')

    # 9. 渲染 resume.tex（每行独立段落：单\n → \n\n 让 LaTeX 产生段间距）
    resume = data.get('resume', '')
    resume_paragraphs = '\n\n'.join(
        escape_latex(line.strip()) for line in resume.split('\n') if line.strip()
    )
    tmpl = env.get_template('resume.tex.j2')
    (output_dir / 'data' / 'resume.tex').write_text(
        tmpl.render(resume_text=resume_paragraphs), encoding='utf-8'
    )
    print('✅ data/resume.tex')

    # 11. 生成占位 committee.tex（答辩委员会，通常需要手工填写）
    committee_tex = r"""% !TeX root = ../thesis.tex
% 答辩委员会名单 - 请手工填写

\begin{committee}[name={学位论文指导小组、公开评阅人和答辩委员会名单}]

  \newcolumntype{C}[1]{@{}>{\centering\arraybackslash}p{#1}}

  \section*{指导小组名单}

  \begin{center}
    \begin{tabular}{C{3cm}C{3cm}C{9cm}@{}}
      % 请填写 \\
    \end{tabular}
  \end{center}

\end{committee}
"""
    (output_dir / 'data' / 'committee.tex').write_text(committee_tex, encoding='utf-8')
    print('✅ data/committee.tex  (占位，请手工填写)')

    # 12. 生成 denotation.tex（abbrevs 已由步骤 7 的 fix_orphan_abbrevs 生成）
    deno_lines = [
        '% !TeX root = ../thesis.tex',
        '% 符号和缩略语说明（由转换脚本自动提取，请人工核查）',
        '% 标注 "← 请人工填写" 的条目为正文中出现但未给出解释的缩略语',
        '',
        r'\begin{denotation}[3cm]',
    ]
    for abbr, explanation in abbrevs.items():
        abbr_esc = escape_meta(abbr)
        exp_esc = escape_latex(explanation)
        if explanation == '待补充全称':
            deno_lines.append(f'  \\item[{abbr_esc}] {exp_esc}  % ← 请人工填写完整解释')
        else:
            deno_lines.append(f'  \\item[{abbr_esc}] {exp_esc}')
    deno_lines.append(r'\end{denotation}')
    (output_dir / 'data' / 'denotation.tex').write_text(
        '\n'.join(deno_lines), encoding='utf-8'
    )
    orphan_count = sum(1 for v in abbrevs.values() if v == '待补充全称')
    print(f'✅ data/denotation.tex  ({len(abbrevs)} 个缩略语，其中 {orphan_count} 个待人工补充)')

    # 13. 生成占位 comments.tex 和 resolution.tex
    (output_dir / 'data' / 'comments.tex').write_text(
        '% 指导教师评语（答辩后手工填写或插入扫描件）\n', encoding='utf-8')
    (output_dir / 'data' / 'resolution.tex').write_text(
        '% 答辩委员会决议书（答辩后手工填写或插入扫描件）\n', encoding='utf-8')
    print('✅ data/comments.tex + resolution.tex  (占位，答辩后填写)')

    # 12. 渲染主文件 thesis.tex
    tmpl = env.get_template('main.tex.j2')
    (output_dir / 'thesis.tex').write_text(
        tmpl.render(
            meta=meta,
            chapters=chapters_info,
            has_resume=bool(resume),
            has_acknowledgements=bool(ack),
            has_figures_list=has_figures_real,
            has_tables_list=has_tables_real,
        ), encoding='utf-8'
    )
    print('✅ thesis.tex')

    print(f'\n📁 LaTeX 项目已生成到: {output_dir}')
    print('下一步: 运行 compile.sh 编译 PDF')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('用法: python3 render.py <parsed.json> <output_dir>')
        sys.exit(1)
    render_project(sys.argv[1], sys.argv[2])
