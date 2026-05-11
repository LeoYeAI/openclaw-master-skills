#!/usr/bin/env python3
"""
build_parsed.py — 纯 Python 组装器，不调 LLM

用法：
  python3 build_parsed.py raw_xxx.json struct.json [out_dir]

  raw_xxx.json  — extract_raw.py 的输出
  struct.json   — 由 AI（Claude）提供的结构描述，格式见下方 STRUCT_FORMAT

struct.json 格式：
{
  "cover": {
    "title_para": 10,        # 论文标题所在段落 idx（可选，不填则从表格提取）
    "abstract_cn_range": [26, 32],
    "abstract_en_range": [34, 45],
    "keywords_cn_para": 31,
    "keywords_en_para": 44
  },
  "chapters": [
    {
      "number": "1",
      "title": "引言",
      "title_para": 109,        # 章标题段落 idx
      "content_range": [110, 154],
      "sections": [
        {
          "level": 2,
          "number": "1.1",
          "title": "研究背景",
          "title_para": 110
        }
      ]
    }
  ],
  "references_range": [386, 410],
  "acknowledgements_range": [411, 420],
  "resume_range": [421, 445]
}
"""

import json
import re
import sys
import shutil
from pathlib import Path


# ── 封面元信息从表格提取 ──────────────────────────────────────────────────────

def extract_meta_from_tables(tables):
    meta = {k: '' for k in ['title', 'title_en', 'author', 'author_en',
                              'supervisor', 'supervisor_en', 'department',
                              'degree_category', 'degree_category_en',
                              'discipline', 'discipline_en', 'date']}
    BLACKLIST = re.compile(r'评阅|答辩|委员会|授权|声明|使用授权|学位论文公开|保密|版权|清华大学')

    for t in tables[:5]:
        rows = t.get('rows', [])
        cells = []
        for row in rows:
            for cell in row:
                text = str(cell).strip()
                if text:
                    cells.append(text)

        for i, cell in enumerate(cells):
            if (re.search(r'[\u4e00-\u9fff]', cell) and len(cell) > 5
                    and not BLACKLIST.search(cell) and not meta['title']
                    and '申请清华大学' not in cell):
                meta['title'] = cell
            if (re.match(r'^[A-Z]', cell) and len(cell) > 15
                    and not re.search(r'[\u4e00-\u9fff]', cell)
                    and 'University' not in cell and not meta['title_en']):
                meta['title_en'] = cell
            if re.sub(r'\s', '', cell) in ('申请人', '作者') and i + 2 < len(cells):
                meta['author'] = cells[i + 2].strip()
            m = re.search(r'^by\s+([A-Z][A-Za-z\s]+)$', cell)
            if m:
                meta['author_en'] = m.group(1).strip()
            if re.sub(r'\s', '', cell) in ('指导教师', '导师') and i + 2 < len(cells):
                meta['supervisor'] = cells[i + 2].strip()
            if re.sub(r'\s', '', cell) in ('培养单位', '院系', '学院') and i + 2 < len(cells):
                meta['department'] = cells[i + 2].strip()
            if cell in ('学位类别', '申请学位') and i + 2 < len(cells):
                meta['degree_category'] = cells[i + 2].strip()
            CN_DIGITS = {'○': '0', '〇': '0', '一': '1', '二': '2', '三': '3', '四': '4',
                         '五': '5', '六': '6', '七': '7', '八': '8', '九': '9'}
            # 先处理复合月份（十二月/十一月/十月），再逐字转数字
            cell_pre = re.sub(r'十二月', '#12月', cell)
            cell_pre = re.sub(r'十一月', '#11月', cell_pre)
            cell_pre = re.sub(r'十月', '#10月', cell_pre)
            cell_arabic = ''.join(CN_DIGITS.get(c, c) for c in cell_pre).replace('#', '')
            m = re.search(r'(\d{4})\s*年\s*(\d{1,2})\s*月', cell_arabic)
            if m and not meta['date']:
                meta['date'] = f"{m.group(1)}-{int(m.group(2)):02d}"

    return meta


# ── 章节内容组装 ──────────────────────────────────────────────────────────────

def build_chapter_content(chap_struct, paragraphs, next_chap_start,
                           figures_by_para=None, tables_by_para=None,
                           extra_tables=None):
    content = []
    cr = chap_struct.get('content_range', [0, 9999])
    start = int(cr[0]) if cr[0] is not None else 0
    end = int(cr[1]) if (len(cr) > 1 and cr[1] is not None) else next_chap_start - 1

    sec_map = {}
    for sec in chap_struct.get('sections', []):
        sec_map[int(sec['title_para'])] = sec

    fig_map = figures_by_para or {}
    tbl_map = tables_by_para or {}
    para_by_idx = {p['idx']: p for p in paragraphs}

    for p in paragraphs:
        idx = p.get('idx', 0)
        if idx < start or idx > end:
            continue
        text = p.get('text', '').strip()

        # 插入图片块
        for fig in fig_map.get(idx, []):
            fname = fig.get('filename', '')
            ext = Path(fname).suffix.lower()
            if ext == '.svg':
                continue
            caption = ''
            for nidx in [idx, idx + 1, idx + 2]:
                nt = para_by_idx.get(nidx, {}).get('text', '').strip()
                if re.match(r'^图\s*\d', nt):
                    caption = nt
                    break
            content.append({
                "type": "figure",
                "embed": fig.get('rId', ''),
                "path": f"figures/{fname}",
                "caption": caption,
            })

        # 插入表格块（before_para == idx）
        for tbl in tbl_map.get(idx, []):
            rows = tbl.get('rows', [])
            if not rows:
                continue
            caption = ''
            for nidx in [idx, idx + 1, idx + 2]:
                nt = para_by_idx.get(nidx, {}).get('text', '').strip()
                if re.match(r'^表\s*\d', nt):
                    caption = nt
                    break
            content.append({"type": "table", "caption": caption, "rows": rows})

        if not text:
            continue
        if re.match(r'^图\s*\d', text):
            continue
        if re.match(r'^表\s*\d', text):
            continue

        if idx in sec_map:
            sec = sec_map[idx]
            content.append({"type": "section", "level": sec['level'],
                             "number": sec['number'], "title": sec['title']})
        else:
            content.append({"type": "text", "content": text})

    # 追加范围外但属于本章的表格
    for bp, tbl in sorted(extra_tables or [], key=lambda x: x[0]):
        rows = tbl.get('rows', [])
        if rows:
            caption = ''
            for nidx in [bp, bp + 1, bp + 2]:
                nt = para_by_idx.get(nidx, {}).get('text', '').strip()
                if re.match(r'^表\s*\d', nt):
                    caption = nt
                    break
            content.append({"type": "table", "caption": caption, "rows": rows})

    return content


# ── 辅助：提取段落文字 ────────────────────────────────────────────────────────

def paras_in_range(paragraphs, start, end):
    if start is None:
        return []
    return [p for p in paragraphs if start <= p['idx'] <= end]


def paras_text(paragraphs, start, end):
    return '\n'.join(
        p['text'].strip() for p in paras_in_range(paragraphs, start, end)
        if p['text'].strip()
    )


# ── 主流程 ────────────────────────────────────────────────────────────────────

def build_parsed(raw_json_path, struct_json_path, output_dir=None):
    raw_path = Path(raw_json_path).resolve()
    struct_path = Path(struct_json_path).resolve()

    raw = json.loads(raw_path.read_text(encoding='utf-8'))
    struct = json.loads(struct_path.read_text(encoding='utf-8'))

    if output_dir is None:
        output_dir = raw_path.parent
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    paragraphs = raw.get('paragraphs', [])
    tables = raw.get('tables', [])
    figures = raw.get('figures', [])

    print(f"✅ 读取: {len(paragraphs)}段落 {len(tables)}表格 {len(figures)}图片")

    para_by_idx = {p['idx']: p for p in paragraphs}

    # ── meta ──
    meta = extract_meta_from_tables(tables)

    # 摘要
    cover = struct.get('cover', {})
    abs_cn_range = cover.get('abstract_cn_range', [None, None])
    abs_en_range = cover.get('abstract_en_range', [None, None])
    kw_cn_idx = cover.get('keywords_cn_para')
    kw_en_idx = cover.get('keywords_en_para')

    abstract_cn = paras_text(paragraphs, abs_cn_range[0], abs_cn_range[1] if len(abs_cn_range) > 1 else None)
    abstract_en = paras_text(paragraphs, abs_en_range[0], abs_en_range[1] if len(abs_en_range) > 1 else None)

    def parse_keywords(idx, is_english=False):
        if idx is None:
            return []
        p = para_by_idx.get(idx, {})
        t = p.get('text', '')
        t = re.sub(r'^关键词[：:\s]*', '', t)
        t = re.sub(r'^[Kk]ey\s*[Ww]ords[：:\s]*', '', t)
        if is_english:
            # 英文关键词用分号/逗号分隔，不用空格拆分（关键词可能是多词短语）
            return [k.strip() for k in re.split(r'[；;，,]+', t) if k.strip()]
        else:
            return [k.strip() for k in re.split(r'[；;，,、\s]+', t) if k.strip()]

    keywords_cn = parse_keywords(kw_cn_idx, is_english=False)
    keywords_en = parse_keywords(kw_en_idx, is_english=True)

    # ── 图表分配 ──
    figures_by_para = {}
    for fig in figures:
        pid = fig.get('para_idx')
        if pid is not None:
            figures_by_para.setdefault(pid, []).append(fig)

    chap_structs = struct.get('chapters', [])
    chap_ranges = []
    for cs in chap_structs:
        cr = cs.get('content_range', [0, 9999])
        s = int(cr[0]) if cr[0] is not None else 0
        e = int(cr[1]) if (len(cr) > 1 and cr[1] is not None) else 9999
        chap_ranges.append((s, e))

    first_chap_start = chap_ranges[0][0] if chap_ranges else 0

    tables_by_para = {}
    extra_by_chap = {}  # chap_idx → [(before_para, tbl)]

    for tbl in tables:
        bp = tbl.get('before_para')
        if bp is None or bp < first_chap_start:
            continue
        # 找所属章节
        assigned = False
        for ci, (s, e) in enumerate(chap_ranges):
            if s <= bp <= e:
                tables_by_para.setdefault(bp, []).append(tbl)
                assigned = True
                break
        if not assigned:
            # 分配给最近章节
            best_ci = min(range(len(chap_ranges)),
                          key=lambda i: min(abs(bp - chap_ranges[i][0]), abs(bp - chap_ranges[i][1])))
            extra_by_chap.setdefault(best_ci, []).append((bp, tbl))

    # ── 章节 ──
    chapters = []
    for i, cs in enumerate(chap_structs):
        next_start = chap_ranges[i + 1][0] if i + 1 < len(chap_ranges) else 99999
        content = build_chapter_content(
            cs, paragraphs, next_start,
            figures_by_para, tables_by_para,
            extra_tables=extra_by_chap.get(i, [])
        )
        chapters.append({
            "level": 1,
            "number": cs.get('number', ''),
            "title": cs.get('title', ''),
            "content": content
        })

    # ── 参考文献 ──
    ref_range = struct.get('references_range', [None, None])
    references = []
    if ref_range[0]:
        for p in paras_in_range(paragraphs, ref_range[0], ref_range[1] or 99999):
            t = p.get('text', '').strip()
            if t and len(t) > 5:
                references.append(t)

    # ── 致谢 / 简历 ──
    ack_range = struct.get('acknowledgements_range', [None, None])
    res_range = struct.get('resume_range', [None, None])
    acknowledgements = paras_text(paragraphs, ack_range[0], ack_range[1] or 99999) if ack_range[0] else ''
    resume = paras_text(paragraphs, res_range[0], res_range[1] or 99999) if res_range[0] else ''

    # ── 拷贝 figures ──
    src_figures = raw_path.parent / 'figures'
    dst_figures = output_dir / 'figures'
    if src_figures.exists() and src_figures != dst_figures:
        dst_figures.mkdir(parents=True, exist_ok=True)
        for f in src_figures.iterdir():
            shutil.copy2(f, dst_figures / f.name)

    # ── 输出 ──
    stem = raw_path.stem.removeprefix('raw_')
    out_path = output_dir / f"parsed_{stem}.json"
    result = {
        "meta": meta,
        "abstract_cn": abstract_cn,
        "abstract_en": abstract_en,
        "keywords_cn": keywords_cn,
        "keywords_en": keywords_en,
        "chapters": chapters,
        "references": references,
        "acknowledgements": acknowledgements,
        "resume": resume,
    }
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')

    tc = sum(1 for c in chapters for item in c['content'] if item.get('type') == 'table')
    fc = sum(1 for c in chapters for item in c['content'] if item.get('type') == 'figure')
    print(f"✅ 完成 → {out_path}")
    print(f"   章节: {len(chapters)}  参考文献: {len(references)}  表格: {tc}  图片: {fc}")
    for c in chapters:
        n_blocks = len(c['content'])
        print(f"   [{c['number']}] {c['title'][:30]}  ({n_blocks}块)")

    return out_path


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python3 build_parsed.py raw_xxx.json struct.json [out_dir]")
        sys.exit(1)
    raw_p = sys.argv[1]
    struct_p = sys.argv[2]
    out_d = sys.argv[3] if len(sys.argv) > 3 else None
    build_parsed(raw_p, struct_p, out_d)
