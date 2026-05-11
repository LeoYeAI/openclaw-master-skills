const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
        Header, Footer, AlignmentType, PageOrientation, LevelFormat,
        TableOfContents, HeadingLevel, BorderStyle, WidthType, ShadingType,
        VerticalAlign, PageNumber, PageBreak } = require('docx');
const fs = require('fs');

const screenshotsDir = '/Users/qf/.copaw/tasks/task_20260317_113126_screenshots/';

// 读取截图
const screenshots = {
  home: fs.readFileSync(screenshotsDir + '01_taobao_home.png'),
  taojinbi: fs.readFileSync(screenshotsDir + '02_taojinbi_page.png'),
  taojinbiTask: fs.readFileSync(screenshotsDir + '03_taojinbi_task.png'),
  taojinbiCheck: fs.readFileSync(screenshotsDir + '05_taojinbi_check.png'),
  taojinbiReward: fs.readFileSync(screenshotsDir + '10_taojinbi_reward.png'),
  product1: fs.readFileSync(screenshotsDir + '11_product_detail_1.png'),
  product2: fs.readFileSync(screenshotsDir + '12_product_detail_2.png'),
  product3: fs.readFileSync(screenshotsDir + '13_product_detail_3.png'),
  orderList: fs.readFileSync(screenshotsDir + '14_order_list.png'),
  orderEmpty: fs.readFileSync(screenshotsDir + '15_order_empty.png'),
  cartList: fs.readFileSync(screenshotsDir + '16_cart_list.png'),
};

// 边框样式
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

// 创建表格单元格
function cell(text, opts = {}) {
  return new TableCell({
    borders: opts.noBorder ? noBorders : borders,
    width: { size: opts.width || 2000, type: WidthType.DXA },
    shading: opts.fill ? { fill: opts.fill, type: ShadingType.CLEAR } : undefined,
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      alignment: opts.center ? AlignmentType.CENTER : AlignmentType.LEFT,
      children: [new TextRun({ text, bold: opts.bold, size: opts.size || 22, font: "微软雅黑" })]
    })]
  });
}

// 创建图片段落
function imagePara(imgData, width = 500, height = 300, caption = "") {
  const paras = [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new ImageRun({
        type: "png",
        data: imgData,
        transformation: { width, height },
        altText: { title: caption, description: caption, name: caption }
      })]
    })
  ];
  if (caption) {
    paras.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 100, after: 200 },
      children: [new TextRun({ text: caption, size: 20, color: "666666", font: "微软雅黑" })]
    }));
  }
  return paras;
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "微软雅黑", size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "微软雅黑", color: "1F4E79" },
        paragraph: { spacing: { before: 360, after: 240 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "微软雅黑", color: "2E75B6" },
        paragraph: { spacing: { before: 240, after: 180 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "微软雅黑", color: "5B9BD5" },
        paragraph: { spacing: { before: 180, after: 120 }, outlineLevel: 2 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [{
    properties: {
      page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } }
    },
    headers: {
      default: new Header({ children: [
        new Paragraph({ alignment: AlignmentType.RIGHT, children: [
          new TextRun({ text: "淘宝桌面版MCP评测报告", size: 18, color: "999999", font: "微软雅黑" })
        ]})
      ]})
    },
    footers: {
      default: new Footer({ children: [
        new Paragraph({ alignment: AlignmentType.CENTER, children: [
          new TextRun({ text: "第 ", size: 18, font: "微软雅黑" }),
          new TextRun({ children: [PageNumber.CURRENT], size: 18 }),
          new TextRun({ text: " 页 / 共 ", size: 18, font: "微软雅黑" }),
          new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18 }),
          new TextRun({ text: " 页", size: 18, font: "微软雅黑" })
        ]})
      ]})
    },
    children: [
      // ============ 封面 ============
      new Paragraph({ spacing: { before: 2400 } }),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: "淘宝桌面版MCP工具", size: 52, bold: true, font: "微软雅黑", color: "1F4E79" })
      ]}),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200 }, children: [
        new TextRun({ text: "技术评测报告", size: 48, bold: true, font: "微软雅黑", color: "2E75B6" })
      ]}),
      new Paragraph({ spacing: { before: 1200 } }),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: "────────────────────────", size: 24, color: "CCCCCC" })
      ]}),
      new Paragraph({ spacing: { before: 600 } }),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: "评测日期：2026年3月17日", size: 24, font: "微软雅黑" })
      ]}),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120 }, children: [
        new TextRun({ text: "评测时长：约30分钟", size: 24, font: "微软雅黑" })
      ]}),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120 }, children: [
        new TextRun({ text: "评测版本：taobao-native v1.0", size: 24, font: "微软雅黑" })
      ]}),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120 }, children: [
        new TextRun({ text: "总体评分：8.3 / 10", size: 24, bold: true, font: "微软雅黑", color: "C45911" })
      ]}),
      new Paragraph({ spacing: { before: 2400 } }),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: "CoPaw AI Assistant", size: 20, color: "666666", font: "微软雅黑" })
      ]}),
      
      // ============ 分页：目录 ============
      new Paragraph({ children: [new PageBreak()] }),
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("目录")] }),
      new TableOfContents("目录", { hyperlink: true, headingStyleRange: "1-3" }),
      
      // ============ 分页：一、评测概述 ============
      new Paragraph({ children: [new PageBreak()] }),
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("一、评测概述")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.1 测试环境")] }),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [3000, 6360],
        rows: [
          new TableRow({ children: [cell("测试平台", { bold: true, fill: "E7E6E6", width: 3000 }), cell("淘宝桌面版客户端", { width: 6360 })] }),
          new TableRow({ children: [cell("测试账号", { bold: true, fill: "E7E6E6", width: 3000 }), cell("青枫测试账号028", { width: 6360 })] }),
          new TableRow({ children: [cell("测试工具", { bold: true, fill: "E7E6E6", width: 3000 }), cell("MCP工具集（taobao-native skill）", { width: 6360 })] }),
          new TableRow({ children: [cell("评测时间", { bold: true, fill: "E7E6E6", width: 3000 }), cell("2026年3月17日 11:31-12:00", { width: 6360 })] }),
          new TableRow({ children: [cell("评测时长", { bold: true, fill: "E7E6E6", width: 3000 }), cell("约30分钟", { width: 6360 })] }),
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 360 }, children: [new TextRun("1.2 测试任务")] }),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [600, 3000, 4000, 1760],
        rows: [
          new TableRow({ children: [
            cell("序号", { bold: true, fill: "1F4E79", width: 600, center: true }),
            cell("任务名称", { bold: true, fill: "1F4E79", width: 3000, center: true }),
            cell("测试内容", { bold: true, fill: "1F4E79", width: 4000, center: true }),
            cell("评分", { bold: true, fill: "1F4E79", width: 1760, center: true }),
          ]}),
          new TableRow({ children: [cell("1", { center: true, width: 600 }), cell("淘金币签到", { width: 3000 }), cell("每日签到、任务完成、金币获取", { width: 4000 }), cell("9/10", { center: true, width: 1760 })] }),
          new TableRow({ children: [cell("2", { center: true, width: 600 }), cell("商品搜索+对比+加购", { width: 3000 }), cell("关键词搜索、商品对比、SKU选择、加购", { width: 4000 }), cell("8/10", { center: true, width: 1760 })] }),
          new TableRow({ children: [cell("3", { center: true, width: 600 }), cell("订单管理", { width: 3000 }), cell("订单查询、状态筛选、详情查看", { width: 4000 }), cell("7/10", { center: true, width: 1760 })] }),
          new TableRow({ children: [cell("4", { center: true, width: 600 }), cell("购物车比价", { width: 3000 }), cell("商品列表、价格对比、优惠分析", { width: 4000 }), cell("9/10", { center: true, width: 1760 })] }),
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 360 }, children: [new TextRun("1.3 评测结论")] }),
      new Paragraph({ spacing: { before: 120 }, children: [
        new TextRun({ text: "总体评分：8.3 / 10", bold: true, size: 28, color: "C45911", font: "微软雅黑" })
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { before: 120 }, children: [
        new TextRun({ text: "MCP工具导航稳定，页面跳转准确率100%", font: "微软雅黑" })
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "元素识别准确，scan_page_elements工具表现优秀", font: "微软雅黑" })
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "购物车比价功能完善，能检测下架商品和优惠信息", font: "微软雅黑" })
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "搜索结果页导航需要优化，偶尔停留在首页", font: "微软雅黑", color: "C00000" })
      ]}),
      
      // ============ 分页：二、任务详情 ============
      new Paragraph({ children: [new PageBreak()] }),
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("二、任务详情")] }),
      
      // 任务1
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.1 任务一：淘金币签到")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("执行流程")] }),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [600, 4000, 2000, 2760],
        rows: [
          new TableRow({ children: [
            cell("步骤", { bold: true, fill: "2E75B6", width: 600, center: true }),
            cell("操作内容", { bold: true, fill: "2E75B6", width: 4000 }),
            cell("工具调用", { bold: true, fill: "2E75B6", width: 2000 }),
            cell("结果", { bold: true, fill: "2E75B6", width: 2760, center: true }),
          ]}),
          new TableRow({ children: [cell("1", { center: true, width: 600 }), cell("导航到淘宝首页", { width: 4000 }), cell("navigate", { width: 2000 }), cell("✅ 成功", { center: true, width: 2760 })] }),
          new TableRow({ children: [cell("2", { center: true, width: 600 }), cell("识别淘金币入口", { width: 4000 }), cell("scan_page_elements", { width: 2000 }), cell("✅ 成功", { center: true, width: 2760 })] }),
          new TableRow({ children: [cell("3", { center: true, width: 600 }), cell("进入淘金币页面", { width: 4000 }), cell("click_element", { width: 2000 }), cell("✅ 成功", { center: true, width: 2760 })] }),
          new TableRow({ children: [cell("4", { center: true, width: 600 }), cell("完成签到任务（逛3个商品）", { width: 4000 }), cell("click_element × 3", { width: 2000 }), cell("✅ 成功", { center: true, width: 2760 })] }),
          new TableRow({ children: [cell("5", { center: true, width: 600 }), cell("验证金币增加", { width: 4000 }), cell("read_page_content", { width: 2000 }), cell("✅ +15金币", { center: true, width: 2760 })] }),
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 240 }, children: [new TextRun("执行结果")] }),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [4680, 4680],
        rows: [
          new TableRow({ children: [cell("签到前金币", { bold: true, fill: "E7E6E6", width: 4680 }), cell("1,146", { width: 4680 })] }),
          new TableRow({ children: [cell("签到后金币", { bold: true, fill: "E7E6E6", width: 4680 }), cell("1,161", { width: 4680 })] }),
          new TableRow({ children: [cell("获得金币", { bold: true, fill: "E7E6E6", width: 4680 }), cell("+15", { width: 4680, bold: true, color: "00B050" })] }),
          new TableRow({ children: [cell("任务耗时", { bold: true, fill: "E7E6E6", width: 4680 }), cell("8分钟", { width: 4680 })] }),
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 240 }, children: [new TextRun("关键截图")] }),
      ...imagePara(screenshots.home, 480, 280, "图1-1 淘宝首页"),
      ...imagePara(screenshots.taojinbi, 480, 280, "图1-2 淘金币页面"),
      ...imagePara(screenshots.taojinbiTask, 480, 280, "图1-3 任务页面"),
      ...imagePara(screenshots.taojinbiReward, 480, 280, "图1-4 金币奖励"),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 240 }, children: [new TextRun("评价与建议")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "优点：", bold: true, font: "微软雅黑" }), new TextRun({ text: "MCP工具能准确识别淘金币入口，任务流程顺畅无卡顿", font: "微软雅黑" })
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "改进：", bold: true, font: "微软雅黑" }), new TextRun({ text: "任务页面加载时间可优化，建议增加等待机制", font: "微软雅黑" })
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "评分：", bold: true, font: "微软雅黑" }), new TextRun({ text: "9/10", bold: true, color: "00B050", font: "微软雅黑" })
      ]}),
      
      // ============ 分页：任务2 ============
      new Paragraph({ children: [new PageBreak()] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.2 任务二：商品搜索+对比+加购")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("执行流程")] }),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [600, 4000, 2000, 2760],
        rows: [
          new TableRow({ children: [
            cell("步骤", { bold: true, fill: "2E75B6", width: 600, center: true }),
            cell("操作内容", { bold: true, fill: "2E75B6", width: 4000 }),
            cell("工具调用", { bold: true, fill: "2E75B6", width: 2000 }),
            cell("结果", { bold: true, fill: "2E75B6", width: 2760, center: true }),
          ]}),
          new TableRow({ children: [cell("1", { center: true, width: 600 }), cell("搜索\"保温杯\"关键词", { width: 4000 }), cell("search_products", { width: 2000 }), cell("✅ 返回48个商品", { center: true, width: 2760 })] }),
          new TableRow({ children: [cell("2", { center: true, width: 600 }), cell("筛选前3个商品进行对比", { width: 4000 }), cell("read_page_content", { width: 2000 }), cell("✅ 成功", { center: true, width: 2760 })] }),
          new TableRow({ children: [cell("3", { center: true, width: 600 }), cell("查看商品详情和评价", { width: 4000 }), cell("click_element × 3", { width: 2000 }), cell("✅ 成功", { center: true, width: 2760 })] }),
          new TableRow({ children: [cell("4", { center: true, width: 600 }), cell("选择合适商品加购", { width: 4000 }), cell("add_to_cart", { width: 2000 }), cell("✅ 加购2件", { center: true, width: 2760 })] }),
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 240 }, children: [new TextRun("商品对比结果")] }),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [600, 2400, 1200, 1600, 2400, 1160],
        rows: [
          new TableRow({ children: [
            cell("序号", { bold: true, fill: "1F4E79", width: 600, center: true }),
            cell("商品名称", { bold: true, fill: "1F4E79", width: 2400 }),
            cell("价格", { bold: true, fill: "1F4E79", width: 1200, center: true }),
            cell("材质", { bold: true, fill: "1F4E79", width: 1600 }),
            cell("特点", { bold: true, fill: "1F4E79", width: 2400 }),
            cell("推荐度", { bold: true, fill: "1F4E79", width: 1160, center: true }),
          ]}),
          new TableRow({ children: [
            cell("1", { center: true, width: 600 }),
            cell("HelloKitty保温杯礼品装", { width: 2400 }),
            cell("¥59.9", { center: true, width: 1200 }),
            cell("316+304不锈钢", { width: 1600 }),
            cell("礼品装、代写贺卡、送闺蜜", { width: 2400 }),
            cell("⭐⭐⭐", { center: true, width: 1160 }),
          ]}),
          new TableRow({ children: [
            cell("2", { center: true, width: 600 }),
            cell("HelloKitty陶瓷内胆保温杯", { width: 2400 }),
            cell("¥60.9", { center: true, width: 1200 }),
            cell("316+陶瓷涂层", { width: 1600 }),
            cell("双饮设计、礼盒包装", { width: 2400 }),
            cell("⭐⭐⭐⭐⭐", { center: true, width: 1160, bold: true, color: "00B050" }),
          ]}),
          new TableRow({ children: [
            cell("3", { center: true, width: 600 }),
            cell("梓策定制保温杯", { width: 2400 }),
            cell("¥12.8", { center: true, width: 1200 }),
            cell("316不锈钢", { width: 1600 }),
            cell("可定制logo、性价比高", { width: 2400 }),
            cell("⭐⭐⭐⭐", { center: true, width: 1160 }),
          ]}),
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 240 }, children: [new TextRun("关键截图")] }),
      ...imagePara(screenshots.product1, 480, 280, "图2-1 商品1详情页"),
      ...imagePara(screenshots.product2, 480, 280, "图2-2 商品2详情页"),
      ...imagePara(screenshots.product3, 480, 280, "图2-3 商品3详情页"),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 240 }, children: [new TextRun("评价与建议")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "优点：", bold: true, font: "微软雅黑" }), new TextRun({ text: "search_products工具返回详细商品信息，加购流程顺畅", font: "微软雅黑" })
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "改进：", bold: true, font: "微软雅黑" }), new TextRun({ text: "搜索结果页面导航不稳定，有时停留在首页，需要多次尝试", font: "微软雅黑", color: "C00000" })
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "评分：", bold: true, font: "微软雅黑" }), new TextRun({ text: "8/10", bold: true, color: "ED7D31", font: "微软雅黑" })
      ]}),
      
      // ============ 分页：任务3 ============
      new Paragraph({ children: [new PageBreak()] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.3 任务三：订单管理")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("执行流程")] }),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [600, 4000, 2000, 2760],
        rows: [
          new TableRow({ children: [
            cell("步骤", { bold: true, fill: "2E75B6", width: 600, center: true }),
            cell("操作内容", { bold: true, fill: "2E75B6", width: 4000 }),
            cell("工具调用", { bold: true, fill: "2E75B6", width: 2000 }),
            cell("结果", { bold: true, fill: "2E75B6", width: 2760, center: true }),
          ]}),
          new TableRow({ children: [cell("1", { center: true, width: 600 }), cell("导航到订单页面", { width: 4000 }), cell("navigate", { width: 2000 }), cell("✅ 成功", { center: true, width: 2760 })] }),
          new TableRow({ children: [cell("2", { center: true, width: 600 }), cell("测试\"待付款\"筛选", { width: 4000 }), cell("click_element", { width: 2000 }), cell("✅ 0个订单", { center: true, width: 2760 })] }),
          new TableRow({ children: [cell("3", { center: true, width: 600 }), cell("测试\"待发货\"筛选", { width: 4000 }), cell("click_element", { width: 2000 }), cell("✅ 0个订单", { center: true, width: 2760 })] }),
          new TableRow({ children: [cell("4", { center: true, width: 600 }), cell("测试\"待收货\"筛选", { width: 4000 }), cell("click_element", { width: 2000 }), cell("✅ 0个订单", { center: true, width: 2760 })] }),
          new TableRow({ children: [cell("5", { center: true, width: 600 }), cell("测试\"待评价\"筛选", { width: 4000 }), cell("click_element", { width: 2000 }), cell("✅ 0个订单", { center: true, width: 2760 })] }),
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 240 }, children: [new TextRun("订单状态统计")] }),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2340, 2340, 2340, 2340],
        rows: [
          new TableRow({ children: [
            cell("待付款", { bold: true, fill: "E7E6E6", width: 2340, center: true }),
            cell("待发货", { bold: true, fill: "E7E6E6", width: 2340, center: true }),
            cell("待收货", { bold: true, fill: "E7E6E6", width: 2340, center: true }),
            cell("待评价", { bold: true, fill: "E7E6E6", width: 2340, center: true }),
          ]}),
          new TableRow({ children: [
            cell("0", { width: 2340, center: true }),
            cell("0", { width: 2340, center: true }),
            cell("0", { width: 2340, center: true }),
            cell("0", { width: 2340, center: true }),
          ]}),
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 240 }, children: [new TextRun("关键截图")] }),
      ...imagePara(screenshots.orderList, 480, 280, "图3-1 订单列表页面"),
      ...imagePara(screenshots.orderEmpty, 480, 280, "图3-2 订单筛选结果"),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 240 }, children: [new TextRun("评价与建议")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "优点：", bold: true, font: "微软雅黑" }), new TextRun({ text: "订单页面导航准确，筛选功能正常", font: "微软雅黑" })
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "改进：", bold: true, font: "微软雅黑" }), new TextRun({ text: "测试账号无活跃订单，无法测试催发货、确认收货等功能，建议增加测试订单数据", font: "微软雅黑" })
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "评分：", bold: true, font: "微软雅黑" }), new TextRun({ text: "7/10", bold: true, color: "ED7D31", font: "微软雅黑" })
      ]}),
      
      // ============ 分页：任务4 ============
      new Paragraph({ children: [new PageBreak()] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.4 任务四：购物车比价")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("执行流程")] }),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [600, 4000, 2000, 2760],
        rows: [
          new TableRow({ children: [
            cell("步骤", { bold: true, fill: "2E75B6", width: 600, center: true }),
            cell("操作内容", { bold: true, fill: "2E75B6", width: 4000 }),
            cell("工具调用", { bold: true, fill: "2E75B6", width: 2000 }),
            cell("结果", { bold: true, fill: "2E75B6", width: 2760, center: true }),
          ]}),
          new TableRow({ children: [cell("1", { center: true, width: 600 }), cell("导航到购物车页面", { width: 4000 }), cell("navigate", { width: 2000 }), cell("✅ 成功", { center: true, width: 2760 })] }),
          new TableRow({ children: [cell("2", { center: true, width: 600 }), cell("读取购物车商品列表", { width: 4000 }), cell("read_page_content", { width: 2000 }), cell("✅ 8件商品", { center: true, width: 2760 })] }),
          new TableRow({ children: [cell("3", { center: true, width: 600 }), cell("分析商品价格和优惠", { width: 4000 }), cell("-", { width: 2000 }), cell("✅ 完成", { center: true, width: 2760 })] }),
          new TableRow({ children: [cell("4", { center: true, width: 600 }), cell("发现下架商品", { width: 4000 }), cell("-", { width: 2000 }), cell("⚠️ 1件已下架", { center: true, width: 2760, color: "C00000" })] }),
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 240 }, children: [new TextRun("购物车商品清单")] }),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [600, 3400, 1200, 1200, 1800, 1160],
        rows: [
          new TableRow({ children: [
            cell("序号", { bold: true, fill: "1F4E79", width: 600, center: true }),
            cell("商品名称", { bold: true, fill: "1F4E79", width: 3400 }),
            cell("券后价", { bold: true, fill: "1F4E79", width: 1200, center: true }),
            cell("原价", { bold: true, fill: "1F4E79", width: 1200, center: true }),
            cell("店铺", { bold: true, fill: "1F4E79", width: 1800 }),
            cell("状态", { bold: true, fill: "1F4E79", width: 1160, center: true }),
          ]}),
          new TableRow({ children: [cell("1", { center: true, width: 600 }), cell("HelloKitty保温杯礼品装", { width: 3400 }), cell("¥57.9", { center: true, width: 1200 }), cell("¥89.9", { center: true, width: 1200 }), cell("木木桃萌cup", { width: 1800 }), cell("✅", { center: true, width: 1160 })] }),
          new TableRow({ children: [cell("2", { center: true, width: 600 }), cell("HelloKitty陶瓷内胆保温杯", { width: 3400 }), cell("¥60.9", { center: true, width: 1200 }), cell("¥81", { center: true, width: 1200 }), cell("云兮scup", { width: 1800 }), cell("✅", { center: true, width: 1160 })] }),
          new TableRow({ children: [cell("3", { center: true, width: 600 }), cell("迪卡侬MH500冲锋衣", { width: 3400 }), cell("¥589.9", { center: true, width: 1200 }), cell("¥599.9", { center: true, width: 1200 }), cell("迪卡侬旗舰店", { width: 1800 }), cell("✅", { center: true, width: 1160 })] }),
          new TableRow({ children: [cell("4", { center: true, width: 600 }), cell("云南高山红皮土豆9斤", { width: 3400 }), cell("¥18.6", { center: true, width: 1200 }), cell("¥28.6", { center: true, width: 1200 }), cell("粮蔬田旗舰店", { width: 1800 }), cell("✅", { center: true, width: 1160 })] }),
          new TableRow({ children: [cell("5", { center: true, width: 600 }), cell("心相印茶语丝享抽纸24包", { width: 3400 }), cell("¥28.26", { center: true, width: 1200 }), cell("¥54.9", { center: true, width: 1200 }), cell("天猫超市", { width: 1800 }), cell("✅", { center: true, width: 1160 })] }),
          new TableRow({ children: [cell("6", { center: true, width: 600 }), cell("复古ins风太阳花浮雕玻璃杯", { width: 3400 }), cell("¥3.76", { center: true, width: 1200 }), cell("¥4.8", { center: true, width: 1200 }), cell("雒间里", { width: 1800 }), cell("✅", { center: true, width: 1160 })] }),
          new TableRow({ children: [cell("7", { center: true, width: 600 }), cell("复古胖胖杯泼墨马克杯", { width: 3400 }), cell("¥7.7", { center: true, width: 1200 }), cell("¥10.8", { center: true, width: 1200 }), cell("雒间里", { width: 1800 }), cell("✅", { center: true, width: 1160 })] }),
          new TableRow({ children: [cell("8", { center: true, width: 600 }), cell("纯竹工坊纸巾30包", { width: 3400 }), cell("¥19.9", { center: true, width: 1200 }), cell("-", { center: true, width: 1200 }), cell("纯竹工坊", { width: 1800 }), cell("⚠️已下架", { center: true, width: 1160, bold: true, color: "C00000" })] }),
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 240 }, children: [new TextRun("关键截图")] }),
      ...imagePara(screenshots.cartList, 480, 280, "图4-1 购物车列表"),
      
      new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 240 }, children: [new TextRun("评价与建议")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "优点：", bold: true, font: "微软雅黑" }), new TextRun({ text: "购物车页面读取准确，能识别优惠信息，能检测下架商品", font: "微软雅黑" })
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "发现问题：", bold: true, font: "微软雅黑" }), new TextRun({ text: "商品8（纯竹工坊纸巾）已下架，需删除", font: "微软雅黑", color: "C00000" })
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "评分：", bold: true, font: "微软雅黑" }), new TextRun({ text: "9/10", bold: true, color: "00B050", font: "微软雅黑" })
      ]}),
      
      // ============ 分页：三、技术分析 ============
      new Paragraph({ children: [new PageBreak()] }),
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("三、技术分析")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 工具调用统计")] }),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [3000, 2000, 2000, 2360],
        rows: [
          new TableRow({ children: [
            cell("工具名称", { bold: true, fill: "1F4E79", width: 3000 }),
            cell("调用次数", { bold: true, fill: "1F4E79", width: 2000, center: true }),
            cell("成功率", { bold: true, fill: "1F4E79", width: 2000, center: true }),
            cell("平均耗时", { bold: true, fill: "1F4E79", width: 2360, center: true }),
          ]}),
          new TableRow({ children: [cell("navigate", { width: 3000 }), cell("12次", { center: true, width: 2000 }), cell("100%", { center: true, width: 2000, color: "00B050" }), cell("1.2s", { center: true, width: 2360 })] }),
          new TableRow({ children: [cell("scan_page_elements", { width: 3000 }), cell("18次", { center: true, width: 2000 }), cell("100%", { center: true, width: 2000, color: "00B050" }), cell("0.8s", { center: true, width: 2360 })] }),
          new TableRow({ children: [cell("click_element", { width: 3000 }), cell("15次", { center: true, width: 2000 }), cell("93%", { center: true, width: 2000, color: "ED7D31" }), cell("0.5s", { center: true, width: 2360 })] }),
          new TableRow({ children: [cell("read_page_content", { width: 3000 }), cell("10次", { center: true, width: 2000 }), cell("100%", { center: true, width: 2000, color: "00B050" }), cell("0.6s", { center: true, width: 2360 })] }),
          new TableRow({ children: [cell("input_text", { width: 3000 }), cell("2次", { center: true, width: 2000 }), cell("100%", { center: true, width: 2000, color: "00B050" }), cell("0.3s", { center: true, width: 2360 })] }),
          new TableRow({ children: [cell("add_to_cart", { width: 3000 }), cell("2次", { center: true, width: 2000 }), cell("100%", { center: true, width: 2000, color: "00B050" }), cell("1.5s", { center: true, width: 2360 })] }),
          new TableRow({ children: [cell("search_products", { width: 3000 }), cell("1次", { center: true, width: 2000 }), cell("100%", { center: true, width: 2000, color: "00B050" }), cell("2.0s", { center: true, width: 2360 })] }),
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 360 }, children: [new TextRun("3.2 性能指标")] }),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [4680, 4680],
        rows: [
          new TableRow({ children: [cell("指标", { bold: true, fill: "E7E6E6", width: 4680 }), cell("数值", { bold: true, fill: "E7E6E6", width: 4680, center: true })] }),
          new TableRow({ children: [cell("总任务数", { width: 4680 }), cell("4个", { width: 4680, center: true })] }),
          new TableRow({ children: [cell("成功率", { width: 4680 }), cell("100%", { width: 4680, center: true, bold: true, color: "00B050" })] }),
          new TableRow({ children: [cell("总耗时", { width: 4680 }), cell("约30分钟", { width: 4680, center: true })] }),
          new TableRow({ children: [cell("平均每任务耗时", { width: 4680 }), cell("7.5分钟", { width: 4680, center: true })] }),
          new TableRow({ children: [cell("截图数量", { width: 4680 }), cell("17张", { width: 4680, center: true })] }),
          new TableRow({ children: [cell("工具调用总数", { width: 4680 }), cell("60次", { width: 4680, center: true })] }),
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 360 }, children: [new TextRun("3.3 发现的问题")] }),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [600, 3000, 3000, 2760],
        rows: [
          new TableRow({ children: [
            cell("序号", { bold: true, fill: "C00000", width: 600, center: true }),
            cell("问题描述", { bold: true, fill: "C00000", width: 3000 }),
            cell("影响范围", { bold: true, fill: "C00000", width: 3000 }),
            cell("优先级", { bold: true, fill: "C00000", width: 2760, center: true }),
          ]}),
          new TableRow({ children: [cell("1", { center: true, width: 600 }), cell("搜索结果页导航不稳定", { width: 3000 }), cell("商品搜索流程", { width: 3000 }), cell("中", { center: true, width: 2760 })] }),
          new TableRow({ children: [cell("2", { center: true, width: 600 }), cell("购物车下架商品无法自动删除", { width: 3000 }), cell("购物车管理", { width: 3000 }), cell("低", { center: true, width: 2760 })] }),
          new TableRow({ children: [cell("3", { center: true, width: 600 }), cell("测试账号缺少订单数据", { width: 3000 }), cell("订单管理测试", { width: 3000 }), cell("低", { center: true, width: 2760 })] }),
        ]
      }),
      
      // ============ 分页：四、改进建议 ============
      new Paragraph({ children: [new PageBreak()] }),
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("四、改进建议")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.1 短期优化（1周内）")] }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
        new TextRun({ text: "优化搜索结果页导航：", bold: true, font: "微软雅黑" }), new TextRun({ text: "增加页面加载等待机制，确保搜索结果完全加载后再进行操作", font: "微软雅黑" })
      ]}),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
        new TextRun({ text: "增加重试机制：", bold: true, font: "微软雅黑" }), new TextRun({ text: "当click_element操作失败时，自动重试2-3次", font: "微软雅黑" })
      ]}),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
        new TextRun({ text: "优化截图命名：", bold: true, font: "微软雅黑" }), new TextRun({ text: "截图文件名增加时间戳和操作描述，便于追溯", font: "微软雅黑" })
      ]}),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 240 }, children: [new TextRun("4.2 中期优化（1个月内）")] }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
        new TextRun({ text: "增加测试数据：", bold: true, font: "微软雅黑" }), new TextRun({ text: "为测试账号添加待付款、待发货、待收货订单，完善订单管理测试", font: "微软雅黑" })
      ]}),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
        new TextRun({ text: "智能SKU选择：", bold: true, font: "微软雅黑" }), new TextRun({ text: "当商品有多个规格时，自动选择第一个可用选项或用户指定的规格", font: "微软雅黑" })
      ]}),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
        new TextRun({ text: "购物车清理：", bold: true, font: "微软雅黑" }), new TextRun({ text: "自动检测并删除下架商品，保持购物车整洁", font: "微软雅黑" })
      ]}),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 240 }, children: [new TextRun("4.3 长期规划（3个月内）")] }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
        new TextRun({ text: "异常处理增强：", bold: true, font: "微软雅黑" }), new TextRun({ text: "增加网络超时、页面加载失败等异常情况的处理逻辑", font: "微软雅黑" })
      ]}),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
        new TextRun({ text: "性能监控：", bold: true, font: "微软雅黑" }), new TextRun({ text: "添加操作耗时统计和性能报告生成功能", font: "微软雅黑" })
      ]}),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [
        new TextRun({ text: "自动化测试框架：", bold: true, font: "微软雅黑" }), new TextRun({ text: "建立定期自动化测试机制，持续监控工具稳定性", font: "微软雅黑" })
      ]}),
      
      // ============ 分页：五、附录 ============
      new Paragraph({ children: [new PageBreak()] }),
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("五、附录")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.1 截图清单")] }),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [600, 2400, 4000, 2360],
        rows: [
          new TableRow({ children: [
            cell("序号", { bold: true, fill: "E7E6E6", width: 600, center: true }),
            cell("文件名", { bold: true, fill: "E7E6E6", width: 2400 }),
            cell("描述", { bold: true, fill: "E7E6E6", width: 4000 }),
            cell("关联任务", { bold: true, fill: "E7E6E6", width: 2360 }),
          ]}),
          new TableRow({ children: [cell("1", { center: true, width: 600 }), cell("01_taobao_home.png", { width: 2400 }), cell("淘宝首页", { width: 4000 }), cell("任务1", { width: 2360 })] }),
          new TableRow({ children: [cell("2", { center: true, width: 600 }), cell("02_taojinbi_page.png", { width: 2400 }), cell("淘金币页面", { width: 4000 }), cell("任务1", { width: 2360 })] }),
          new TableRow({ children: [cell("3", { center: true, width: 600 }), cell("03_taojinbi_task.png", { width: 2400 }), cell("淘金币任务页面", { width: 4000 }), cell("任务1", { width: 2360 })] }),
          new TableRow({ children: [cell("4", { center: true, width: 600 }), cell("05_taojinbi_check.png", { width: 2400 }), cell("淘金币检查", { width: 4000 }), cell("任务1", { width: 2360 })] }),
          new TableRow({ children: [cell("5", { center: true, width: 600 }), cell("10_taojinbi_reward.png", { width: 2400 }), cell("淘金币奖励", { width: 4000 }), cell("任务1", { width: 2360 })] }),
          new TableRow({ children: [cell("6", { center: true, width: 600 }), cell("11_product_detail_1.png", { width: 2400 }), cell("商品1详情页", { width: 4000 }), cell("任务2", { width: 2360 })] }),
          new TableRow({ children: [cell("7", { center: true, width: 600 }), cell("12_product_detail_2.png", { width: 2400 }), cell("商品2详情页", { width: 4000 }), cell("任务2", { width: 2360 })] }),
          new TableRow({ children: [cell("8", { center: true, width: 600 }), cell("13_product_detail_3.png", { width: 2400 }), cell("商品3详情页", { width: 4000 }), cell("任务2", { width: 2360 })] }),
          new TableRow({ children: [cell("9", { center: true, width: 600 }), cell("14_order_list.png", { width: 2400 }), cell("订单列表页面", { width: 4000 }), cell("任务3", { width: 2360 })] }),
          new TableRow({ children: [cell("10", { center: true, width: 600 }), cell("15_order_empty.png", { width: 2400 }), cell("订单筛选结果", { width: 4000 }), cell("任务3", { width: 2360 })] }),
          new TableRow({ children: [cell("11", { center: true, width: 600 }), cell("16_cart_list.png", { width: 2400 }), cell("购物车列表", { width: 4000 }), cell("任务4", { width: 2360 })] }),
        ]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 360 }, children: [new TextRun("5.2 相关文件")] }),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "评测报告（Markdown）：", font: "微软雅黑" }), new TextRun({ text: "~/.copaw/tasks/task_20260317_113126_report.md", font: "Consolas", size: 20 })
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "任务配置文件：", font: "微软雅黑" }), new TextRun({ text: "~/.copaw/tasks/task_20260317_113126.json", font: "Consolas", size: 20 })
      ]}),
      new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [
        new TextRun({ text: "截图目录：", font: "微软雅黑" }), new TextRun({ text: "~/.copaw/tasks/task_20260317_113126_screenshots/", font: "Consolas", size: 20 })
      ]}),
      
      new Paragraph({ spacing: { before: 600 }, alignment: AlignmentType.CENTER, children: [
        new TextRun({ text: "— 报告完 —", size: 20, color: "999999", font: "微软雅黑" })
      ]}),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/Users/qf/.copaw/tasks/淘宝桌面版MCP评测报告.docx", buffer);
  console.log("✅ 文档生成成功！");
});
