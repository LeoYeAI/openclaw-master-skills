#!/usr/bin/env node  
  
import fs from 'fs'  
import path from 'path'  
import { fileURLToPath } from 'url'  
import { unified } from 'unified'  
import remarkParse from 'remark-parse'  
import remarkMath from 'remark-math'  
import remarkGfm from 'remark-gfm'  
  
// ============ ESM 下的 __dirname ============  
const __filename = fileURLToPath(import.meta.url)  
const __dirname = path.dirname(__filename)  
const SKILL_DIR = path.resolve(__dirname, '..')  
  
// ============ 配置解析 ============  
function parseConfigValue(raw) {  
  const value = raw.trim()  
  
  if (/^(true|false)$/i.test(value)) {  
    return value.toLowerCase() === 'true'  
  }  
  
  if (/^\d+$/.test(value)) {  
    return Number(value)  
  }  
  
  return value  
}  
  
function parseExtendConfig(skillDir) {  
  const candidates = [  
    path.join(process.cwd(), '.claude/skills/format-markdown/EXTEND.md'),  
    path.join(process.env.HOME || '', '.claude/skills/format-markdown/EXTEND.md'),  
    path.join(skillDir, 'EXTEND.md'),  
  ]  
  
  for (const cfgPath of candidates) {  
    if (fs.existsSync(cfgPath)) {  
      const content = fs.readFileSync(cfgPath, 'utf8')  
      const config = {}  
  
      content.split('\n').forEach(line => {  
        const match = line.match(/^([\w-]+):\s*(.+)$/)  
        if (match) {  
          config[match[1]] = parseConfigValue(match[2])  
        }  
      })  
  
      return config  
    }  
  }  
  
  return {}  
}  
  
function getBooleanConfig(config, key, defaultValue) {  
  if (!(key in config)) return defaultValue  
  return Boolean(config[key])  
}  
  
// ============ 工具函数 ============  
function normalizeLineEndings(content) {  
  return content.replace(/\r\n/g, '\n')  
}  
  
function isEmpty(line) {  
  return line.trim() === ''  
}  
  
function parseMarkdown(content) {  
  return unified()  
    .use(remarkParse)  
    .use(remarkMath)  
    .use(remarkGfm)  
    .parse(content)  
}  
  
// ============ fenced code block 感知工具 ============  
function isFenceStart(line) {  
  const m = line.match(/^(\s*)(`{3,}|~{3,})/)  
  if (!m) return null  
  return {  
    marker: m[2][0],  
    size: m[2].length,  
  }  
}  
  
function isFenceEnd(line, marker, size) {  
  const re = new RegExp(`^\\s*\\${marker}{${size},}\\s*$`)  
  return re.test(line)  
}  
  
// ============ 阶段1：AST 识别块级结构并补前后空行 ============  
function ensureBlankLinesAroundBlocks(content, rules) {  
  content = normalizeLineEndings(content)  
  const lines = content.split('\n')  
  const tree = parseMarkdown(content)  
  
  const needBlankBefore = new Set()  
  const needBlankAfter = new Set()  
  
  const stats = {  
    mathBlocks: 0,  
    listBlocks: 0,  
    tableBlocks: 0,  
    emptyLinesAdded: 0,  
  }  
  
  const blocks = tree.children || []  
  
  for (const node of blocks) {  
    if (!node.position) continue  
  
    const isMath = rules.fixMathBlocks && node.type === 'math'  
    const isList = rules.fixListBlocks && node.type === 'list'  
    const isTable = rules.fixTableBlocks && node.type === 'table'  
  
    if (!isMath && !isList && !isTable) continue  
  
    const startLine = node.position.start.line - 1  
    const endLine = node.position.end.line - 1  
  
    if (isMath) stats.mathBlocks++  
    if (isList) stats.listBlocks++  
    if (isTable) stats.tableBlocks++  
  
    if (startLine > 0 && !isEmpty(lines[startLine - 1])) {  
      needBlankBefore.add(startLine)  
    }  
  
    if (endLine < lines.length - 1 && !isEmpty(lines[endLine + 1])) {  
      needBlankAfter.add(endLine)  
    }  
  }  
  
  const out = []  
  
  for (let i = 0; i < lines.length; i++) {  
    if (  
      needBlankBefore.has(i) &&  
      out.length > 0 &&  
      !isEmpty(out[out.length - 1])  
    ) {  
      out.push('')  
      stats.emptyLinesAdded++  
    }  
  
    out.push(lines[i])  
  
    if (  
      needBlankAfter.has(i) &&  
      i < lines.length - 1 &&  
      !isEmpty(lines[i + 1])  
    ) {  
      out.push('')  
      stats.emptyLinesAdded++  
    }  
  }  
  
  return {  
    content: out.join('\n'),  
    stats,  
  }  
}  
  
// ============ 阶段2：清理多行数学块内部空行 ============  
function normalizeMathBlockInnerSpacing(content) {  
  content = normalizeLineEndings(content)  
  const lines = content.split('\n')  
  const out = []  
  
  let inFence = false  
  let fenceMarker = null  
  let fenceSize = 0  
  
  let inMathBlock = false  
  let mathBuffer = []  
  
  let removed = 0  
  
  function isMathOpenLine(line) {  
    const t = line.trim()  
    return t === '$$' || t === '\\['  
  }  
  
  function isMathCloseLine(line) {  
    const t = line.trim()  
    return t === '$$' || t === '\\]'  
  }  
  
  function flushMathBuffer() {  
    if (mathBuffer.length < 2) {  
      out.push(...mathBuffer)  
      mathBuffer = []  
      return  
    }  
  
    const open = mathBuffer[0]  
    const close = mathBuffer[mathBuffer.length - 1]  
    const middle = mathBuffer.slice(1, -1)  
  
    while (middle.length > 0 && isEmpty(middle[0])) {  
      middle.shift()  
      removed++  
    }  
  
    while (middle.length > 0 && isEmpty(middle[middle.length - 1])) {  
      middle.pop()  
      removed++  
    }  
  
    out.push(open, ...middle, close)  
    mathBuffer = []  
  }  
  
  for (let i = 0; i < lines.length; i++) {  
    const line = lines[i]  
  
    if (!inMathBlock) {  
      const fence = isFenceStart(line)  
  
      if (!inFence && fence) {  
        inFence = true  
        fenceMarker = fence.marker  
        fenceSize = fence.size  
        out.push(line)  
        continue  
      }  
  
      if (inFence) {  
        out.push(line)  
        if (isFenceEnd(line, fenceMarker, fenceSize)) {  
          inFence = false  
          fenceMarker = null  
          fenceSize = 0  
        }  
        continue  
      }  
    }  
  
    if (!inFence) {  
      if (!inMathBlock && isMathOpenLine(line)) {  
        inMathBlock = true  
        mathBuffer = [line]  
        continue  
      }  
  
      if (inMathBlock) {  
        mathBuffer.push(line)  
        if (isMathCloseLine(line)) {  
          flushMathBuffer()  
          inMathBlock = false  
        }  
        continue  
      }  
    }  
  
    out.push(line)  
  }  
  
  if (mathBuffer.length > 0) {  
    out.push(...mathBuffer)  
  }  
  
  return {  
    content: out.join('\n'),  
    removedInnerBlankLines: removed,  
  }  
}  
  
// ============ 阶段3：兜底处理“独占一行的单行 $$...$$” ============  
function ensureBlankLinesAroundStandaloneSingleLineMath(content, enabled) {  
  if (!enabled) {  
    return {  
      content,  
      added: 0,  
      singleLineMathBlocks: 0,  
    }  
  }  
  
  content = normalizeLineEndings(content)  
  const lines = content.split('\n')  
  const out = []  
  
  let inFence = false  
  let fenceMarker = null  
  let fenceSize = 0  
  
  let added = 0  
  let singleLineMathBlocks = 0  
  
  function isStandaloneSingleLineMath(line) {  
    const t = line.trim()  
    return /^\$\$.*\$\$$/.test(t) && t !== '$$'  
  }  
  
  for (let i = 0; i < lines.length; i++) {  
    const line = lines[i]  
  
    const fence = isFenceStart(line)  
  
    if (!inFence && fence) {  
      inFence = true  
      fenceMarker = fence.marker  
      fenceSize = fence.size  
      out.push(line)  
      continue  
    }  
  
    if (inFence) {  
      out.push(line)  
      if (isFenceEnd(line, fenceMarker, fenceSize)) {  
        inFence = false  
        fenceMarker = null  
        fenceSize = 0  
      }  
      continue  
    }  
  
    if (isStandaloneSingleLineMath(line)) {  
      singleLineMathBlocks++  
  
      if (out.length > 0 && !isEmpty(out[out.length - 1])) {  
        out.push('')  
        added++  
      }  
  
      out.push(line)  
  
      if (i < lines.length - 1 && !isEmpty(lines[i + 1])) {  
        out.push('')  
        added++  
      }  
  
      continue  
    }  
  
    out.push(line)  
  }  
  
  return {  
    content: out.join('\n'),  
    added,  
    singleLineMathBlocks,  
  }  
}  
  
// ============ 总调度 ============  
function normalizeMarkdownForMaterial(content, config = {}) {  
  const rules = {  
    fixMathBlocks: getBooleanConfig(config, 'fix_math_blocks', true),  
    fixListBlocks: getBooleanConfig(config, 'fix_list_blocks', true),  
    fixTableBlocks: getBooleanConfig(config, 'fix_table_blocks', true),  
    trimMathInnerBlankLines: getBooleanConfig(config, 'trim_math_inner_blank_lines', true),  
  }  
  
  let working = content  
  
  const step1 = ensureBlankLinesAroundBlocks(working, rules)  
  working = step1.content  
  
  let step2 = {  
    content: working,  
    removedInnerBlankLines: 0,  
  }  
  
  if (rules.trimMathInnerBlankLines) {  
    step2 = normalizeMathBlockInnerSpacing(working)  
    working = step2.content  
  }  
  
  const step3 = ensureBlankLinesAroundStandaloneSingleLineMath(  
    working,  
    rules.fixMathBlocks  
  )  
  working = step3.content  
  
  return {  
    content: working,  
    stats: {  
      mathBlocks: step1.stats.mathBlocks + step3.singleLineMathBlocks,  
      listBlocks: step1.stats.listBlocks,  
      tableBlocks: step1.stats.tableBlocks,  
      emptyLinesAdded: step1.stats.emptyLinesAdded + step3.added,  
      mathInnerBlankLinesRemoved: step2.removedInnerBlankLines,  
    },  
    rules,  
  }  
}  
  
// ============ 备份逻辑 ============  
function backupFile(filePath) {  
  if (!fs.existsSync(filePath)) return null  
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)  
  const backupPath = `${filePath}.backup-${timestamp}.md`  
  fs.copyFileSync(filePath, backupPath)  
  return backupPath  
}  
  
// ============ CLI 参数解析 ============  
function parseArgs(args) {  
  const options = {  
    output: null,  
    dryRun: false,  
    skipBackup: false,  
  }  
  
  const files = []  
  
  for (let i = 0; i < args.length; i++) {  
    const arg = args[i]  
  
    if (arg === '--output' || arg === '-o') {  
      options.output = args[++i]  
    } else if (arg === '--dry-run' || arg === '-n') {  
      options.dryRun = true  
    } else if (arg === '--no-backup') {  
      options.skipBackup = true  
    } else if (!arg.startsWith('-')) {  
      files.push(arg)  
    }  
  }  
  
  return { files, options }  
}  
  
// ============ 核心处理函数 ============  
function fixFile(filePath, outputPath, config = {}, options = {}) {  
  const content = fs.readFileSync(filePath, 'utf8')  
  const { content: result, stats, rules } = normalizeMarkdownForMaterial(content, config)  
  
  let backupPath = null  
  
  if (!options.dryRun) {  
    if (!options.skipBackup && fs.existsSync(outputPath)) {  
      backupPath = backupFile(outputPath)  
    }  
    fs.writeFileSync(outputPath, result, 'utf8')  
  }  
  
  return {  
    ...stats,  
    rules,  
    backupPath,  
  }  
}  
  
// ============ 主入口 ============  
function main() {  
  const args = process.argv.slice(2)  
  const { files, options } = parseArgs(args)  
  const config = parseExtendConfig(SKILL_DIR)  
  
  if (files.length === 0) {  
    console.error('Usage: node scripts/format-structure.mjs <file.md> [options]')  
    process.exit(1)  
  }  
  
  if (options.output && files.length > 1) {  
    console.error('[ERROR] --output can only be used with a single input file.')  
    process.exit(1)  
  }  
  
  for (const file of files) {  
    const inputPath = path.resolve(file)  
    const outputPath = options.output  
      ? path.resolve(options.output)  
      : inputPath  
  
    if (!fs.existsSync(inputPath)) {  
      console.error(`[ERROR] File not found: ${inputPath}`)  
      continue  
    }  
  
    const stats = fixFile(inputPath, outputPath, config, options)  
  
    if (options.dryRun) {  
      console.log(`[DRY RUN] Would process: ${inputPath}`)  
      console.log(`  ├─ Output: ${outputPath}`)  
      console.log(`  ├─ Math blocks: ${stats.mathBlocks}`)  
      console.log(`  ├─ List blocks: ${stats.listBlocks}`)  
      console.log(`  ├─ Table blocks: ${stats.tableBlocks}`)  
      console.log(`  ├─ Empty lines added: ${stats.emptyLinesAdded}`)  
      console.log(`  ├─ Math inner blank lines removed: ${stats.mathInnerBlankLinesRemoved}`)  
      console.log(`  └─ Rules: ${JSON.stringify(stats.rules)}`)  
      continue  
    }  
  
    console.log(`[SUCCESS] Processed: ${outputPath}`)  
    console.log(`  ├─ Math blocks: ${stats.mathBlocks}`)  
    console.log(`  ├─ List blocks: ${stats.listBlocks}`)  
    console.log(`  ├─ Table blocks: ${stats.tableBlocks}`)  
    console.log(`  ├─ Empty lines added: ${stats.emptyLinesAdded}`)  
    console.log(`  ├─ Math inner blank lines removed: ${stats.mathInnerBlankLinesRemoved}`)  
    console.log(`  ├─ Rules: ${JSON.stringify(stats.rules)}`)  
    console.log(`  └─ Backup created: ${stats.backupPath ? stats.backupPath : 'no'}`)  
  }  
}  
  
main()  
