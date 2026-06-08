const { Document, Packer, Paragraph, TextRun, PageBreak, AlignmentType, HeadingLevel, convertInchesToTwip } = require('docx');
const fs = require('fs');
const path = require('path');

// 读取markdown文件
const inputFile = process.argv[2];
if (!inputFile) {
  console.error('用法: node create_word_doc_v3.js <your_review.md>');
  process.exit(1);
}
const markdown = fs.readFileSync(inputFile, 'utf-8');

// 按行分割
const lines = markdown.split('\n');

const children = [];
let currentSection = '';

for (let i = 0; i < lines.length; i++) {
  let line = lines[i].trim();
  
  if (!line) {
    // 空行
    continue;
  }

  // 一级标题 (#, ##)
  if (line.startsWith('# ')) {
    const text = line.replace('# ', '');
    children.push(new Paragraph({
      children: [new TextRun({
        text: text,
        font: '黑体',
        size: 32, // 小三 (16pt)
        bold: true
      })],
      alignment: AlignmentType.CENTER,
      spacing: {
        before: 240,
        after: 240
      }
    }));
  }
  // 二级标题 (##)
  else if (line.startsWith('## ')) {
    const text = line.replace('## ', '');
    children.push(new Paragraph({
      children: [new TextRun({
        text: text,
        font: '黑体',
        size: 28, // 四号 (14pt)
        bold: true
      })],
      spacing: {
        before: 160,
        after: 120
      }
    }));
  }
  // 参考文献部分标题
  else if (line === '## 参考文献' || line === '### 参考文献') {
    children.push(new Paragraph({
      children: [new TextRun({
        text: '参考文献',
        font: '黑体',
        size: 28,
        bold: true
      })],
      spacing: {
        before: 160,
        after: 120
      }
    }));
  }
  // 参考文献
  else if (line.startsWith('[1]') || (line.startsWith('[') && line.includes(']'))) {
    children.push(new Paragraph({
      children: [new TextRun({
        text: line.trim(),
        font: 'Times New Roman',
        size: 20.5 // 五号 (10.5pt)
      })],
      spacing: {
        line: 280, // 1.25倍行距
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
    children.push(new Paragraph({
      children: [new TextRun({
        text: line,
        font: '宋体',
        size: 24, // 小四 (12pt)
        bold: true
      })],
      spacing: {
        line: 360, // 1.5倍行距
        before: 120,
        after: 120
      },
      indent: {
        firstLine: convertInchesToTwip(0.3) // 首行缩进约2字符
      }
    }));
  }
  // 摘要行
  else if (line.startsWith('摘要：') || line.startsWith('摘要:')) {
    children.push(new Paragraph({
      children: [new TextRun({
        text: line,
        font: '宋体',
        size: 24 // 小四 (12pt)
      })],
      spacing: {
        line: 360, // 1.5倍行距
        before: 120,
        after: 120
      }
    }));
  }
  // 正文段落
  else {
    children.push(new Paragraph({
      children: [new TextRun({
        text: line,
        font: '宋体',
        size: 24 // 小四 (12pt)
      })],
      spacing: {
        line: 360, // 1.5倍行距
        before: 60,
        after: 60
      },
      indent: {
        firstLine: convertInchesToTwip(0.3) // 首行缩进约2字符
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
          top: convertInchesToTwip(1),    // 2.54cm (1英寸)
          right: convertInchesToTwip(1),  // 2.54cm (1英寸)
          bottom: convertInchesToTwip(1), // 2.54cm (1英寸)
          left: convertInchesToTwip(1)    // 2.54cm (1英寸)
        },
        size: {
          width: convertInchesToTwip(8.27),  // A4 宽度
          height: convertInchesToTwip(11.69) // A4 高度
        }
      }
    },
    children: children
  }]
});

// 保存文档
const outputFile = path.basename(inputFile, path.extname(inputFile)) + '_筛选后.docx';
Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(outputFile, buffer);
  console.log(`Word文档已生成: ${outputFile}`);
}).catch((err) => {
  console.error('生成Word文档时出错:', err);
});
