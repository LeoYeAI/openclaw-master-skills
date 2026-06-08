const { Document, Packer, Paragraph, TextRun, AlignmentType, convertInchesToTwip } = require('docx');
const fs = require('fs');
const path = require('path');

// 获取输入文件路径
const inputFile = process.argv[2] || 'your_review.md';
const outputFile = inputFile.replace('.md', '_上标版.docx');
const outputPath = path.resolve(outputFile);

// 读取markdown文件
const markdown = fs.readFileSync(inputFile, 'utf-8');

// 按行分割
const lines = markdown.split('\n');

const children = [];
let inReferencesSection = false;

// 字号定义
const FONT_SIZE_BODY = 24;      // 小四 = 12pt = 24 half-points（正文和参考文献）
const FONT_SIZE_SMALL = 20;     // 上标引用（略小）
const FONT_SIZE_H1 = 32;        // 一级标题（小三 = 16pt）
const FONT_SIZE_H2 = 28;        // 二级标题（四号 = 14pt）

// 判断字符是否为中文
function isChinese(char) {
  return /[\u4e00-\u9fa5]/.test(char);
}

// 匹配物种拉丁文名
const SCIENTIFIC_NAME_REGEX = /[A-Z][a-z]+\s+[a-z]+/g;

// 将文本分割为不同片段（处理中文、英文、拉丁文名）
function parseTextWithFormatting(text) {
  const runs = [];
  
  // 匹配引用标记
  const citationRegex = /\[(\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)\]/g;
  
  // 找出所有特殊标记的位置
  const markers = [];
  
  // 查找引用标记
  let match;
  while ((match = citationRegex.exec(text)) !== null) {
    markers.push({
      start: match.index,
      end: match.index + match[0].length,
      type: 'citation',
      text: match[0]
    });
  }
  
  // 查找拉丁文名（但不在引用标记内）
  SCIENTIFIC_NAME_REGEX.lastIndex = 0;
  while ((match = SCIENTIFIC_NAME_REGEX.exec(text)) !== null) {
    // 检查是否与引用标记重叠
    const isOverlapping = markers.some(m => 
      (match.index >= m.start && match.index < m.end) ||
      (match.index + match[0].length > m.start && match.index + match[0].length <= m.end)
    );
    if (!isOverlapping) {
      markers.push({
        start: match.index,
        end: match.index + match[0].length,
        type: 'latin',
        text: match[0]
      });
    }
  }
  
  // 按位置排序
  markers.sort((a, b) => a.start - b.start);
  
  // 处理文本
  let lastIndex = 0;
  for (const marker of markers) {
    // 处理标记前的普通文本
    if (marker.start > lastIndex) {
      const normalText = text.substring(lastIndex, marker.start);
      const segments = splitByLanguage(normalText);
      segments.forEach(segment => {
        runs.push(new TextRun({
          text: segment.text,
          font: segment.isChinese ? '宋体' : 'Times New Roman',
          size: FONT_SIZE_BODY  // 正文小四
        }));
      });
    }
    
    // 处理标记
    if (marker.type === 'citation') {
      runs.push(new TextRun({
        text: marker.text,
        font: 'Times New Roman',
        size: FONT_SIZE_SMALL,
        superScript: true
      }));
    } else if (marker.type === 'latin') {
      runs.push(new TextRun({
        text: marker.text,
        font: 'Times New Roman',
        size: FONT_SIZE_BODY,  // 正文小四
        italics: true
      }));
    }
    
    lastIndex = marker.end;
  }
  
  // 处理剩余文本
  if (lastIndex < text.length) {
    const normalText = text.substring(lastIndex);
    const segments = splitByLanguage(normalText);
    segments.forEach(segment => {
      runs.push(new TextRun({
        text: segment.text,
        font: segment.isChinese ? '宋体' : 'Times New Roman',
        size: FONT_SIZE_BODY  // 正文小四
      }));
    });
  }
  
  return runs.length > 0 ? runs : [new TextRun({
    text: text,
    font: '宋体',
    size: FONT_SIZE_BODY
  })];
}

// 将文本按语言分割（中文 vs 非中文）
function splitByLanguage(text) {
  const segments = [];
  let currentSegment = '';
  let currentIsChinese = null;

  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    const charIsChinese = isChinese(char);

    if (currentIsChinese === null) {
      currentIsChinese = charIsChinese;
      currentSegment = char;
    } else if (currentIsChinese === charIsChinese) {
      currentSegment += char;
    } else {
      segments.push({
        text: currentSegment,
        isChinese: currentIsChinese
      });
      currentIsChinese = charIsChinese;
      currentSegment = char;
    }
  }

  if (currentSegment) {
    segments.push({
      text: currentSegment,
      isChinese: currentIsChinese
    });
  }

  return segments;
}

for (let i = 0; i < lines.length; i++) {
  let line = lines[i].trim();
  
  if (!line) {
    continue;
  }

  // 检测参考文献部分
  if (line === '## 参考文献' || line === '### 参考文献') {
    inReferencesSection = true;
    children.push(new Paragraph({
      children: [new TextRun({
        text: '参考文献',
        font: '黑体',
        size: FONT_SIZE_H2,  // 二级标题字号
        bold: true
      })],
      spacing: {
        before: 160,
        after: 120
      }
    }));
    continue;
  }

  // 一级标题
  if (line.startsWith('# ') && !line.startsWith('## ')) {
    const text = line.replace('# ', '');
    children.push(new Paragraph({
      children: [new TextRun({
        text: text,
        font: '黑体',
        size: FONT_SIZE_H1,  // 一级标题字号
        bold: true
      })],
      alignment: AlignmentType.CENTER,
      spacing: {
        before: 240,
        after: 240
      }
    }));
  }
  // 二级标题
  else if (line.startsWith('## ')) {
    const text = line.replace('## ', '');
    children.push(new Paragraph({
      children: [new TextRun({
        text: text,
        font: '黑体',
        size: FONT_SIZE_H2,  // 二级标题字号
        bold: true
      })],
      spacing: {
        before: 160,
        after: 120
      }
    }));
  }
  // 参考文献条目（小四字号）
  else if (inReferencesSection && line.startsWith('[') && /^\[\d+\]/.test(line)) {
    children.push(new Paragraph({
      children: [new TextRun({
        text: line.trim(),
        font: 'Times New Roman',
        size: FONT_SIZE_BODY  // 参考文献小四
      })],
      spacing: {
        line: 280,
        before: 60,
        after: 60
      },
      indent: {
        firstLine: 0
      }
    }));
  }
  // 关键词行
  else if (line.startsWith('关键词：') || line.startsWith('关键词:')) {
    const runs = parseTextWithFormatting(line);
    runs.forEach(run => {
      if (run.font) {
        run.bold = true;
      }
    });
    children.push(new Paragraph({
      children: runs,
      spacing: {
        line: 360,
        before: 120,
        after: 120
      },
      indent: {
        firstLine: convertInchesToTwip(0.3)
      }
    }));
  }
  // 摘要行
  else if (line.startsWith('摘要：') || line.startsWith('摘要:')) {
    const runs = parseTextWithFormatting(line);
    children.push(new Paragraph({
      children: runs,
      spacing: {
        line: 360,
        before: 120,
        after: 120
      }
    }));
  }
  // 正文段落（小四字号）
  else {
    const runs = parseTextWithFormatting(line);
    children.push(new Paragraph({
      children: runs,
      spacing: {
        line: 360,
        before: 60,
        after: 60
      },
      indent: {
        firstLine: convertInchesToTwip(0.3)
      }
    }));
  }
}

// 创建文档
const doc = new Document({
  sections: [{
    properties: {
      page: {
        margin: {
          top: convertInchesToTwip(1),
          right: convertInchesToTwip(1),
          bottom: convertInchesToTwip(1),
          left: convertInchesToTwip(1)
        },
        size: {
          width: convertInchesToTwip(8.27),
          height: convertInchesToTwip(11.69)
        }
      }
    },
    children: children
  }]
});

// 保存文档
Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(outputPath, buffer);
  console.log('='.repeat(60));
  console.log('✅ Word文档生成成功！');
  console.log('='.repeat(60));
  console.log(`📄 文件路径: ${outputPath}`);
  console.log('');
  console.log('📋 格式说明:');
  console.log('   • 正文和参考文献: 小四 (12pt)');
  console.log('   • 中文字体: 宋体');
  console.log('   • 英文/数字/标点: Times New Roman');
  console.log('   • 物种拉丁文名: Times New Roman 斜体');
  console.log('   • 参考文献引用: 右上标 [n]');
  console.log('   • 一级标题: 小三 (16pt) 黑体');
  console.log('   • 二级标题: 四号 (14pt) 黑体');
  console.log('='.repeat(60));
  console.log('');
  console.log('📝 正在打开文档...');
  console.log('='.repeat(60));
  
  // 自动打开文档
  const { exec } = require('child_process');
  const platform = process.platform;
  
  let command;
  if (platform === 'win32') {
    command = `start "" "${outputPath}"`;
  } else if (platform === 'darwin') {
    command = `open "${outputPath}"`;
  } else {
    command = `xdg-open "${outputPath}"`;
  }
  
  exec(command, (error) => {
    if (error) {
      console.log('⚠️ 自动打开失败，请手动打开文档');
    } else {
      console.log('✅ 文档已打开');
    }
  });
}).catch((err) => {
  console.error('❌ 生成Word文档时出错:', err);
});
