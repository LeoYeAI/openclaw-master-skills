const fs = require('fs')

function extractAfterBracket(text) {
  const m = text.match(/^\s*(?:\[[^\]]+\]\s*)?(.*)$/)
  return (m && m[1] ? m[1] : text).trim()
}

function parseTitle(line) {
  const m = line.match(/^\s*#\s+(.*)$/)
  if (!m) return null
  return extractAfterBracket(m[1])
}

function parseCatalog(line) {
  // 支持 ## 1. 标题 和 ## 1、标题
  const m = line.match(/^\s*##\s*\d+[.、]\s*(.*)$/)
  if (!m) return null
  return extractAfterBracket(m[1])
}

function parseSubCatalog(line) {
  const m = line.match(/^\s*###\s*\d+[.、]\d+\s*(.*)$/)
  if (!m) return null
  return extractAfterBracket(m[1])
}

function parsePoint(line) {
  const m = line.match(/^\s*####\s*\d+[.、]\d+[.、]\d+\s*(.*)$/)
  if (!m) return null
  return extractAfterBracket(m[1])
}

function parseArgumentLine(line) {
  // 更加宽松：支持中文冒号、英文冒号，前面的 - 或 *，甚至直接是文本
  const m = line.match(/^\s*(?:[-*]\s*)?(?:论述内容[：:]\s*)?(.*)$/)
  return m ? m[1].trim() : null
}

function preprocessMarkdown(markdown) {
  if (!markdown) return '';
  return markdown
    .replace(/\r\n/g, '\n') // 统一换行符
    .replace(/\n{3,}/g, '\n\n') // 压缩多余空行
    .replace(/[\u200B-\u200D\uFEFF]/g, '') // 移除零宽字符
    .replace(/[＃]/g, '#') // 处理全角 #
    .replace(/[：]/g, '：') // 统一中文冒号（保持中文冒号，因为后续逻辑有处理）
    .replace(/[。]/g, '。') // 保持中文句号
    .replace(/[“”]/g, '"') // 替换全角引号
    .replace(/[‘’]/g, "'") // 替换全角单引号
    .trim();
}

function parseMarkdownToCustomData(markdown) {
  const processed = preprocessMarkdown(markdown)
  const lines = processed.split(/\n/)

  let title = ''
  const catalogs = []
  const contentsMap = new Map() // key: `${ci}:${si}` -> { catalog_index, sub_catalog_index, content: [] }

  let currentCatalogIndex = -1
  let currentSubIndex = -1
  let currentPoint = null

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const trimmedLine = line.trim()
    if (!trimmedLine && !currentPoint) continue

    // 标题检测
    if (!title) {
      const t = parseTitle(line)
      if (t) {
        title = t
        continue
      }
    }

    // 一级大纲检测
    const cat = parseCatalog(line)
    if (cat) {
      catalogs.push({ catalog: cat, sub_catalog: [] })
      currentCatalogIndex = catalogs.length - 1
      currentSubIndex = -1
      currentPoint = null
      continue
    }

    // 二级大纲检测
    const sub = parseSubCatalog(line)
    if (sub) {
      if (currentCatalogIndex < 0) continue
      catalogs[currentCatalogIndex].sub_catalog.push(sub)
      currentSubIndex = catalogs[currentCatalogIndex].sub_catalog.length - 1
      currentPoint = null
      const key = `${currentCatalogIndex}:${currentSubIndex}`
      if (!contentsMap.has(key)) {
        contentsMap.set(key, {
          catalog_index: currentCatalogIndex,
          sub_catalog_index: currentSubIndex,
          content: []
        })
      }
      continue
    }

    // 三级论点检测 (####)
    const point = parsePoint(line)
    if (point) {
      if (currentCatalogIndex >= 0 && currentSubIndex >= 0) {
        const key = `${currentCatalogIndex}:${currentSubIndex}`
        const obj = contentsMap.get(key)
        currentPoint = { key: point, value: '' }
        obj.content.push(currentPoint)
      }
      continue
    }

    // 如果当前在二级大纲下，但没有进入三级论点 (####)，且是列表项 (- 或 *)
    if (!currentPoint && currentCatalogIndex >= 0 && currentSubIndex >= 0) {
      // 检查是否是列表项
      if (/^\s*[-*]\s+/.test(line)) {
        const contentLine = parseArgumentLine(line)
        if (contentLine) {
          const key = `${currentCatalogIndex}:${currentSubIndex}`
          const obj = contentsMap.get(key)
          obj.content.push(contentLine)
        }
        continue
      }
    }

    // 如果当前在某个论点下，且不是标题，则累加内容
    if (currentPoint && currentCatalogIndex >= 0 && currentSubIndex >= 0) {
      // 检查是否是任何级别的标题，如果是则停止累加
      if (/^\s*#/.test(line)) {
        currentPoint = null
        i-- // 回退一行重新处理
        continue
      }
      
      const contentLine = parseArgumentLine(line)
      if (contentLine !== null) {
        // 只有非空行才累加
        if (contentLine.trim()) {
          if (currentPoint.value) {
            currentPoint.value += '\n' + contentLine
          } else {
            currentPoint.value = contentLine
          }
        }
      }
    }
  }

  // 清理内容：去除多余的空行和首尾空格
  contentsMap.forEach(obj => {
    obj.content = obj.content.map(p => {
      if (typeof p === 'object' && p !== null) {
        if (p.value) p.value = p.value.trim();
        return p;
      }
      return typeof p === 'string' ? p.trim() : p;
    }).filter(p => {
      if (typeof p === 'object' && p !== null) return true;
      return !!p; // 过滤掉空字符串
    });
  })

  const contents = Array.from(contentsMap.values())
  return { 
    title, 
    sub_title: '', 
    author: '', 
    catalogs, 
    contents 
  }
}

function summarizeCatalogs(customData) {
  const lines = []
  lines.push(`# ${customData.title || '未命名PPT'}`)
  customData.catalogs.forEach((c, ci) => {
    lines.push(`## ${ci + 1}. ${c.catalog}`)
    c.sub_catalog.forEach((s, si) => {
      lines.push(`### ${ci + 1}.${si + 1} ${s}`)
    })
  })
  return lines.join('\n')
}

/**
 * 校验 custom_data 是否符合 API 要求
 */
function validateCustomData(data) {
  const errors = [];
  const countChars = (s) => String(s || '').replace(/\s+/g, '').length
  if (!data.title) errors.push('缺失标题 (title)');
  if (!Array.isArray(data.catalogs)) {
    errors.push('catalogs 必须是数组');
  } else {
    data.catalogs.forEach((c, i) => {
      if (!c.catalog) errors.push(`第 ${i + 1} 个章节缺失标题 (catalog)`);
      if (!Array.isArray(c.sub_catalog)) {
        errors.push(`章节 "${c.catalog}" 的 sub_catalog 必须是数组`);
      } else if (c.sub_catalog.length < 2) {
        errors.push(`章节 "${c.catalog}" 的二级标题太少，要求至少包含 2 个二级标题`);
      }
    });
  }

  if (!Array.isArray(data.contents)) {
    errors.push('contents 必须是数组');
  } else {
    data.contents.forEach((cnt, i) => {
      if (typeof cnt.catalog_index !== 'number') errors.push(`第 ${i + 1} 个内容项缺失有效的 catalog_index`);
      if (typeof cnt.sub_catalog_index !== 'number') errors.push(`第 ${i + 1} 个内容项缺失有效的 sub_catalog_index`);
      if (!Array.isArray(cnt.content)) {
        errors.push(`第 ${i + 1} 个内容项缺失 content 数组`);
      } else if (cnt.content.length < 2 || cnt.content.length > 6) {
        const catName = data.catalogs[cnt.catalog_index]?.catalog || '未知章节';
        const subName = data.catalogs[cnt.catalog_index]?.sub_catalog[cnt.sub_catalog_index] || '未知二级标题';
        errors.push(`页面 "${catName} -> ${subName}" 的论点数量不符合要求，需要 2~6 个论点`);
      } else {
        const catName = data.catalogs[cnt.catalog_index]?.catalog || '未知章节';
        const subName = data.catalogs[cnt.catalog_index]?.sub_catalog[cnt.sub_catalog_index] || '未知二级标题';
        cnt.content.forEach((p, pi) => {
          if (typeof p !== 'object' || p === null || Array.isArray(p)) {
            errors.push(`页面 "${catName} -> ${subName}" 第 ${pi + 1} 个论点必须是 {key,value} 对象`)
            return
          }
          if (!p.key || typeof p.key !== 'string') {
            errors.push(`页面 "${catName} -> ${subName}" 第 ${pi + 1} 个论点缺失 key`)
          }
          if (!p.value || typeof p.value !== 'string') {
            errors.push(`页面 "${catName} -> ${subName}" 第 ${pi + 1} 个论点缺失 value`)
          } else if (countChars(p.value) < 80) {
            errors.push(`页面 "${catName} -> ${subName}" 第 ${pi + 1} 个论点论述内容太短，要求 ≥80 字`)
          }
        })
      }
    });
  }

  if (Array.isArray(data.contents)) {
    const counts = data.contents
      .map(c => (Array.isArray(c.content) ? c.content.length : 0))
      .filter(n => n > 0)
    if (counts.length >= 2 && counts.every(n => n === 2)) {
      errors.push('不允许所有二级大纲都只包含 2 个论点')
    }
    if (counts.length >= 3) {
      const unique = new Set(counts)
      if (unique.size < 2) {
        errors.push('论点数量应有变化（如 3 / 4 / 5）')
      }
    }
  }
  return errors;
}

module.exports = {
  parseMarkdownToCustomData,
  summarizeCatalogs,
  validateCustomData
}
