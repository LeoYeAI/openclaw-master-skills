/**
 * HTML 转 PPTX 转换脚本
 * 
 * 用法: node html-to-pptx.js <htmlPath> <outputPath> [imageBasePath]
 * 
 * 参数:
 *   htmlPath     - HTML 文件路径
 *   outputPath   - 输出 PPTX 文件路径
 *   imageBasePath - 图片基础路径（可选，默认从 HTML 中的路径读取）
 * 
 * 依赖: npm install pptxgenjs
 */

const PptxGenJS = require('pptxgenjs');
const fs = require('fs');
const path = require('path');

// ============================================================================
// 配置
// ============================================================================

const colors = {
  primary: '0d47a1',
  secondary: '1976d2',
  light: '42a5f5',
  text: '333333',
  white: 'FFFFFF',
  bgLight: 'e3f2fd'
};

// ============================================================================
// 核心函数：嵌套 HTML 解析
// ============================================================================

/**
 * 提取所有顶层 slide div
 * ⚠️ 注意：必须使用栈匹配，不能用简单正则
 */
function extractSlides(html) {
  const slides = [];
  // 精确匹配 slide 的开始标签，捕获类型
  const regex = /<div class="slide( cover| end)?"[^>]*>/g;
  let match;
  
  while ((match = regex.exec(html)) !== null) {
    const startPos = match.index;
    const slideType = match[1] ? match[1].trim() : 'content';
    
    // 用栈找到匹配的结束 </div>
    let depth = 1;
    let pos = startPos + match[0].length;
    
    while (depth > 0 && pos < html.length) {
      const openIdx = html.indexOf('<div', pos);
      const closeIdx = html.indexOf('</div>', pos);
      
      if (closeIdx === -1) break;
      
      if (openIdx !== -1 && openIdx < closeIdx) {
        depth++;
        pos = openIdx + 4;
      } else {
        depth--;
        pos = closeIdx + 6;
      }
    }
    
    slides.push({
      html: html.substring(startPos, pos),
      type: slideType
    });
  }
  
  return slides;
}

/**
 * 提取 text-section 内容
 * ⚠️ 注意：text-section 内部有嵌套 div，需要用栈匹配
 */
function extractTextSection(slideHtml) {
  const startMatch = slideHtml.match(/class="text-section"[^>]*>/);
  if (!startMatch) return null;
  
  const startPos = startMatch.index + startMatch[0].length;
  
  let depth = 1;
  let pos = startPos;
  
  while (depth > 0 && pos < slideHtml.length) {
    const openIdx = slideHtml.indexOf('<div', pos);
    const closeIdx = slideHtml.indexOf('</div>', pos);
    
    if (closeIdx === -1) break;
    
    if (openIdx !== -1 && openIdx < closeIdx) {
      depth++;
      pos = openIdx + 4;
    } else {
      depth--;
      pos = closeIdx + 6;
      if (depth === 0) {
        return slideHtml.substring(startPos, closeIdx);
      }
    }
  }
  return null;
}

/**
 * 提取图片路径（排除背景图）
 */
function extractImages(slideHtml) {
  const images = [];
  const regex = /<img[^>]*src="([^"]+)"[^>]*>/g;
  let match;
  
  while ((match = regex.exec(slideHtml)) !== null) {
    if (!match[1].includes('cover_bg') && !match[1].includes('end_bg')) {
      images.push(match[1]);
    }
  }
  return images;
}

/**
 * 清理 HTML 标签
 */
function cleanHtml(text) {
  return text
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/\s+/g, ' ')
    .trim();
}

// ============================================================================
// 幻灯片创建函数
// ============================================================================

/**
 * 创建封面页
 */
function createCoverSlide(slide, slideHtml, imgBasePath) {
  // 1. 背景图
  const bgPath = path.join(imgBasePath, 'cover_bg.png');
  if (fs.existsSync(bgPath)) {
    slide.addImage({ path: bgPath, x: 0, y: 0, w: 10, h: 5.625 });
  }
  
  // 2. 半透明遮罩
  slide.addShape('rect', {
    x: 0, y: 0, w: 10, h: 5.625,
    fill: { color: colors.primary, transparency: 20 }
  });
  
  // 3. h1 标题
  const h1Match = slideHtml.match(/<h1>([\s\S]*?)<\/h1>/);
  if (h1Match) {
    const title = h1Match[1].replace(/<br\s*\/?>/gi, '\n').replace(/<[^>]+>/g, '').trim();
    slide.addText(title, {
      x: 0.5, y: 1.5, w: 9.0, h: 1.5,
      fontSize: 32, bold: true, color: colors.white,
      align: 'center', valign: 'middle'
    });
  }
  
  // 4. 副标题
  const subtitleMatch = slideHtml.match(/class="subtitle"[^>]*>([\s\S]*?)<\/div>/);
  if (subtitleMatch) {
    slide.addText(cleanHtml(subtitleMatch[1]), {
      x: 0.5, y: 3.2, w: 9.0, h: 0.5,
      fontSize: 20, color: colors.white, align: 'center'
    });
  }
  
  // 5. 元信息
  const metaMatch = slideHtml.match(/class="meta"[^>]*>([\s\S]*?)<\/div>/);
  if (metaMatch) {
    const meta = metaMatch[1].replace(/<\/?p>/g, '\n').replace(/<[^>]+>/g, '').trim();
    slide.addText(meta, {
      x: 0.5, y: 4.5, w: 9.0, h: 0.8,
      fontSize: 14, color: colors.white, align: 'center'
    });
  }
}

/**
 * 创建结束页
 */
function createEndSlide(slide, slideHtml, imgBasePath) {
  // 1. 背景图
  const bgPath = path.join(imgBasePath, 'end_bg.png');
  if (fs.existsSync(bgPath)) {
    slide.addImage({ path: bgPath, x: 0, y: 0, w: 10, h: 5.625 });
  }
  
  // 2. 半透明遮罩
  slide.addShape('rect', {
    x: 0, y: 0, w: 10, h: 5.625,
    fill: { color: colors.primary, transparency: 15 }
  });
  
  // 3. 标题
  const h2Match = slideHtml.match(/<h2>([\s\S]*?)<\/h2>/);
  if (h2Match) {
    slide.addText(h2Match[1].trim(), {
      x: 0.5, y: 2.0, w: 9.0, h: 1.0,
      fontSize: 44, bold: true, color: colors.white, align: 'center'
    });
  }
  
  // 4. 段落
  let yPos = 3.2;
  const pRegex = /<p[^>]*>([\s\S]*?)<\/p>/g;
  let pMatch;
  while ((pMatch = pRegex.exec(slideHtml)) !== null) {
    const text = cleanHtml(pMatch[1]);
    if (text) {
      slide.addText(text, {
        x: 0.5, y: yPos, w: 9.0, h: 0.4,
        fontSize: 14, color: colors.white, align: 'center'
      });
      yPos += 0.45;
    }
  }
}

/**
 * 创建内容页
 */
function createContentSlide(slide, slideHtml, pageNum, imgBasePath) {
  // 1. 标题栏
  slide.addShape('rect', {
    x: 0, y: 0, w: 10, h: 0.8,
    fill: { color: colors.primary }
  });
  
  const headerMatch = slideHtml.match(/class="slide-header"[^>]*>([\s\S]*?)<\/div>/);
  if (headerMatch) {
    slide.addText(headerMatch[1].trim(), {
      x: 0.3, y: 0.15, w: 9.4, h: 0.5,
      fontSize: 18, bold: true, color: colors.white
    });
  }
  
  // 2. 提取内容
  const textHtml = extractTextSection(slideHtml);
  const images = extractImages(slideHtml);
  const hasImage = images.length > 0;
  const leftWidth = hasImage ? 4.5 : 9.4;
  
  let yPos = 1.1;
  
  if (textHtml) {
    // === h2 ===
    const h2Match = textHtml.match(/<h2>([\s\S]*?)<\/h2>/);
    if (h2Match) {
      slide.addText(h2Match[1].trim(), {
        x: 0.3, y: yPos, w: leftWidth, h: 0.4,
        fontSize: 16, bold: true, color: colors.primary
      });
      yPos += 0.5;
    }
    
    // === h3 之前的内容 ===
    const beforeH3 = textHtml.split(/<h3>/)[0];
    
    // 段落
    const pRegex = /<p[^>]*>([\s\S]*?)<\/p>/g;
    let pMatch;
    while ((pMatch = pRegex.exec(beforeH3)) !== null) {
      const text = cleanHtml(pMatch[1]);
      if (text) {
        slide.addText(text, {
          x: 0.3, y: yPos, w: leftWidth, h: 0.6,
          fontSize: 12, color: colors.text, valign: 'top'
        });
        yPos += 0.65;
      }
    }
    
    // 列表
    const ulMatch = beforeH3.match(/<ul[^>]*>([\s\S]*?)<\/ul>/);
    if (ulMatch) {
      const liRegex = /<li>([\s\S]*?)<\/li>/g;
      let liMatch;
      while ((liMatch = liRegex.exec(ulMatch[0])) !== null) {
        const text = cleanHtml(liMatch[1]);
        if (text) {
          slide.addText('• ' + text, {
            x: 0.3, y: yPos, w: leftWidth, h: 0.35,
            fontSize: 12, color: colors.text
          });
          yPos += 0.35;
        }
      }
      yPos += 0.2;
    }
    
    // === five-grid ===
    yPos = processFiveGrid(slide, textHtml, yPos, leftWidth);
    
    // === three-grid ===
    yPos = processThreeGrid(slide, textHtml, yPos, leftWidth);
    
    // === four-grid ===
    yPos = processFourGrid(slide, textHtml, yPos, leftWidth);
    
    // === flow-chart ===
    yPos = processFlowChart(slide, textHtml, yPos, leftWidth);
    
    // === h3 部分 ===
    const h3Parts = textHtml.split(/<h3>/);
    for (let i = 1; i < h3Parts.length; i++) {
      const part = h3Parts[i];
      const h3End = part.indexOf('</h3>');
      if (h3End > 0) {
        const h3Title = part.substring(0, h3End).trim();
        const afterH3 = part.substring(h3End + 5);
        
        slide.addText(h3Title, {
          x: 0.3, y: yPos, w: leftWidth, h: 0.35,
          fontSize: 14, bold: true, color: colors.secondary
        });
        yPos += 0.4;
        
        // 段落
        const pRegex2 = /<p[^>]*>([\s\S]*?)<\/p>/g;
        let pMatch2;
        while ((pMatch2 = pRegex2.exec(afterH3)) !== null) {
          const text = cleanHtml(pMatch2[1]);
          if (text) {
            slide.addText(text, {
              x: 0.3, y: yPos, w: leftWidth, h: 0.5,
              fontSize: 12, color: colors.text, valign: 'top'
            });
            yPos += 0.55;
          }
        }
        
        // 列表
        const ulMatch2 = afterH3.match(/<ul[^>]*>([\s\S]*?)<\/ul>/);
        if (ulMatch2) {
          const liRegex2 = /<li>([\s\S]*?)<\/li>/g;
          let liMatch2;
          while ((liMatch2 = liRegex2.exec(ulMatch2[0])) !== null) {
            const text = cleanHtml(liMatch2[1]);
            if (text) {
              slide.addText('• ' + text, {
                x: 0.3, y: yPos, w: leftWidth, h: 0.35,
                fontSize: 12, color: colors.text
              });
              yPos += 0.35;
            }
          }
          yPos += 0.2;
        }
      }
    }
  }
  
  // 图片
  if (hasImage) {
    addImages(slide, images, imgBasePath);
  }
}

// ============================================================================
// 辅助函数：处理各种布局
// ============================================================================

function processFiveGrid(slide, textHtml, yPos, leftWidth) {
  const match = textHtml.match(/class="five-grid"[\s\S]*?<\/div>\s*<\/div>\s*<\/div>\s*<\/div>/);
  if (!match) return yPos;
  
  const itemRegex = /class="five-item"[^>]*>([\s\S]*?)<\/div>\s*<\/div>/g;
  const items = [];
  let itemMatch;
  
  while ((itemMatch = itemRegex.exec(match[0])) !== null) {
    const num = itemMatch[1].match(/class="num"[^>]*>([\s\S]*?)<\/div>/);
    const title = itemMatch[1].match(/class="title"[^>]*>([\s\S]*?)<\/div>/);
    const desc = itemMatch[1].match(/class="desc"[^>]*>([\s\S]*?)<\/div>/);
    items.push({
      num: num ? cleanHtml(num[1]) : '',
      title: title ? cleanHtml(title[1]) : '',
      desc: desc ? cleanHtml(desc[1]) : ''
    });
  }
  
  const itemW = (leftWidth - 0.5) / 5;
  items.forEach((item, i) => {
    slide.addShape('rect', {
      x: 0.3 + i * (itemW + 0.1), y: yPos, w: itemW, h: 0.9,
      fill: { color: colors.bgLight }, line: { color: colors.secondary, width: 0.5 }
    });
    slide.addText(item.num, {
      x: 0.3 + i * (itemW + 0.1), y: yPos + 0.1, w: itemW, h: 0.35,
      fontSize: 20, bold: true, color: colors.primary, align: 'center'
    });
    slide.addText(item.title, {
      x: 0.3 + i * (itemW + 0.1), y: yPos + 0.45, w: itemW, h: 0.2,
      fontSize: 10, bold: true, color: colors.secondary, align: 'center'
    });
    slide.addText(item.desc, {
      x: 0.3 + i * (itemW + 0.1), y: yPos + 0.65, w: itemW, h: 0.2,
      fontSize: 8, color: '666666', align: 'center'
    });
  });
  
  return yPos + 1.1;
}

function processThreeGrid(slide, textHtml, yPos, leftWidth) {
  const match = textHtml.match(/class="three-grid"[\s\S]*?<\/div>\s*<\/div>\s*<\/div>\s*<\/div>/);
  if (!match) return yPos;
  
  const itemRegex = /class="three-item"[^>]*>([\s\S]*?)<\/div>\s*<\/div>/g;
  const items = [];
  let itemMatch;
  
  while ((itemMatch = itemRegex.exec(match[0])) !== null) {
    const num = itemMatch[1].match(/class="num"[^>]*>([\s\S]*?)<\/div>/);
    const title = itemMatch[1].match(/class="title"[^>]*>([\s\S]*?)<\/div>/);
    const desc = itemMatch[1].match(/class="desc"[^>]*>([\s\S]*?)<\/div>/);
    items.push({
      num: num ? cleanHtml(num[1]) : '',
      title: title ? cleanHtml(title[1]) : '',
      desc: desc ? cleanHtml(desc[1]) : ''
    });
  }
  
  const itemW = (leftWidth - 0.3) / 3;
  items.forEach((item, i) => {
    slide.addShape('rect', {
      x: 0.3 + i * (itemW + 0.15), y: yPos, w: itemW, h: 1.0,
      fill: { color: colors.bgLight }, line: { color: colors.secondary, width: 0.5 }
    });
    slide.addText(item.num, {
      x: 0.3 + i * (itemW + 0.15), y: yPos + 0.1, w: itemW, h: 0.35,
      fontSize: 24, bold: true, color: colors.primary, align: 'center'
    });
    slide.addText(item.title, {
      x: 0.3 + i * (itemW + 0.15), y: yPos + 0.45, w: itemW, h: 0.25,
      fontSize: 11, bold: true, color: colors.secondary, align: 'center'
    });
    slide.addText(item.desc, {
      x: 0.3 + i * (itemW + 0.15), y: yPos + 0.7, w: itemW, h: 0.25,
      fontSize: 9, color: '666666', align: 'center'
    });
  });
  
  return yPos + 1.2;
}

function processFourGrid(slide, textHtml, yPos, leftWidth) {
  const regex = /class="four-grid"[\s\S]*?<\/div>\s*<\/div>\s*<\/div>\s*<\/div>/g;
  let match;
  
  while ((match = regex.exec(textHtml)) !== null) {
    const itemRegex = /class="four-item"[^>]*>([\s\S]*?)<\/div>\s*<\/div>/g;
    const items = [];
    let itemMatch;
    
    while ((itemMatch = itemRegex.exec(match[0])) !== null) {
      const h4 = itemMatch[1].match(/<h4>([\s\S]*?)<\/h4>/);
      const p = itemMatch[1].match(/<p[^>]*>([\s\S]*?)<\/p>/);
      items.push({
        title: h4 ? cleanHtml(h4[1]) : '',
        desc: p ? cleanHtml(p[1]) : ''
      });
    }
    
    const itemW = (leftWidth - 0.15) / 2;
    const itemH = 0.7;
    items.forEach((item, i) => {
      const col = i % 2, row = Math.floor(i / 2);
      slide.addShape('rect', {
        x: 0.3 + col * (itemW + 0.15), y: yPos + row * (itemH + 0.1), w: itemW, h: itemH,
        fill: { color: colors.bgLight }, line: { color: colors.secondary, width: 0.5 }
      });
      slide.addText(item.title, {
        x: 0.3 + col * (itemW + 0.15), y: yPos + row * (itemH + 0.1) + 0.1, w: itemW, h: 0.25,
        fontSize: 11, bold: true, color: colors.primary, align: 'center'
      });
      slide.addText(item.desc, {
        x: 0.3 + col * (itemW + 0.15), y: yPos + row * (itemH + 0.1) + 0.35, w: itemW, h: 0.3,
        fontSize: 9, color: '666666', align: 'center'
      });
    });
    
    yPos += Math.ceil(items.length / 2) * (itemH + 0.1) + 0.1;
  }
  
  return yPos;
}

function processFlowChart(slide, textHtml, yPos, leftWidth) {
  const match = textHtml.match(/class="flow-chart"[\s\S]*?<\/div>\s*<\/div>\s*<\/div>/);
  if (!match) return yPos;
  
  const boxRegex = /class="flow-box"[^>]*>([\s\S]*?)<\/div>/g;
  const steps = [];
  let boxMatch;
  
  while ((boxMatch = boxRegex.exec(match[0])) !== null) {
    steps.push(cleanHtml(boxMatch[1]));
  }
  
  if (steps.length > 0) {
    const itemW = 1.5;
    const totalW = steps.length * itemW + (steps.length - 1) * 0.3;
    const startX = (leftWidth - totalW) / 2 + 0.3;
    
    steps.forEach((step, i) => {
      slide.addShape('roundRect', {
        x: startX + i * (itemW + 0.3), y: yPos, w: itemW, h: 0.4,
        fill: { color: colors.secondary }, rectRadius: 0.05
      });
      slide.addText(step, {
        x: startX + i * (itemW + 0.3), y: yPos, w: itemW, h: 0.4,
        fontSize: 10, bold: true, color: colors.white, align: 'center', valign: 'middle'
      });
      if (i < steps.length - 1) {
        slide.addText('→', {
          x: startX + i * (itemW + 0.3) + itemW + 0.05, y: yPos, w: 0.2, h: 0.4,
          fontSize: 14, color: colors.secondary, align: 'center', valign: 'middle'
        });
      }
    });
    
    yPos += 0.5;
  }
  
  return yPos;
}

function addImages(slide, images, imgBasePath) {
  const imgX = 5.0, imgY = 1.1, imgW = 4.7, imgH = 4.0;
  const validImages = images.filter(p => fs.existsSync(p));
  
  if (validImages.length > 0) {
    if (validImages.length === 1) {
      slide.addImage({
        path: validImages[0], x: imgX, y: imgY, w: imgW, h: imgH,
        sizing: { type: 'contain', w: imgW, h: imgH }
      });
    } else {
      const cols = validImages.length > 2 ? 2 : validImages.length;
      const rows = Math.ceil(validImages.length / cols);
      const cellW = (imgW - 0.1 * (cols - 1)) / cols;
      const cellH = (imgH - 0.1 * (rows - 1)) / rows;
      
      validImages.forEach((imgPath, i) => {
        const col = i % cols, row = Math.floor(i / cols);
        slide.addImage({
          path: imgPath,
          x: imgX + col * (cellW + 0.1), y: imgY + row * (cellH + 0.1), w: cellW, h: cellH,
          sizing: { type: 'contain', w: cellW, h: cellH }
        });
      });
    }
  } else {
    // 占位符
    slide.addShape('rect', {
      x: imgX, y: imgY, w: imgW, h: imgH,
      fill: { color: 'f5f5f5' },
      line: { color: 'cccccc', width: 1, dashType: 'dash' }
    });
    slide.addText('图片区域', {
      x: imgX, y: imgY + imgH / 2 - 0.2, w: imgW, h: 0.4,
      fontSize: 14, color: '999999', align: 'center'
    });
  }
}

// ============================================================================
// 主函数
// ============================================================================

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length < 2) {
    console.log('用法: node html-to-pptx.js <htmlPath> <outputPath> [imageBasePath]');
    console.log('');
    console.log('参数:');
    console.log('  htmlPath      - HTML 文件路径');
    console.log('  outputPath    - 输出 PPTX 文件路径');
    console.log('  imageBasePath - 图片基础路径（可选）');
    process.exit(1);
  }
  
  const htmlPath = args[0];
  const outputPath = args[1];
  const imgBasePath = args[2] || path.dirname(htmlPath);
  
  // 读取 HTML
  if (!fs.existsSync(htmlPath)) {
    console.error(`错误: HTML 文件不存在: ${htmlPath}`);
    process.exit(1);
  }
  
  const html = fs.readFileSync(htmlPath, 'utf-8');
  
  // 创建 PPT
  const pptx = new PptxGenJS();
  pptx.layout = 'LAYOUT_16x9';
  
  // 解析幻灯片
  console.log('解析 HTML...');
  const slides = extractSlides(html);
  console.log(`找到 ${slides.length} 张幻灯片\n`);
  
  // 创建每页
  slides.forEach((slideData, i) => {
    const slide = pptx.addSlide();
    const pageNum = i + 1;
    
    if (slideData.type === 'cover') {
      createCoverSlide(slide, slideData.html, imgBasePath);
    } else if (slideData.type === 'end') {
      createEndSlide(slide, slideData.html, imgBasePath);
    } else {
      createContentSlide(slide, slideData.html, pageNum, imgBasePath);
    }
    
    // 页码
    const totalPages = slides.length;
    slide.addText(`${pageNum} / ${totalPages}`, {
      x: 9.0, y: 5.3, w: 0.5, h: 0.3,
      fontSize: 10,
      color: (slideData.type === 'cover' || slideData.type === 'end') ? 'FFFFFF' : '999999',
      align: 'right'
    });
    
    console.log(`第 ${pageNum} 页 [${slideData.type}] - OK`);
  });
  
  // 保存
  await pptx.writeFile({ fileName: outputPath });
  console.log(`\n✅ 完成: ${outputPath}`);
}

main().catch(err => {
  console.error('失败:', err);
  process.exit(1);
});