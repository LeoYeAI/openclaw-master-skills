# 沙箱

共 4 个工具。使用 `@工具中文名` 语法在任务提示词中调用。

### @智能数据查询

智能数据查询

工具中文名：智能数据查询
功能说明：对结构化数据（商品、关键词、细分市场）进行高性能统计分析，支持分组统计、排名筛选、占比分布、市场集中度（CR5/CR10）、多维交叉分析等。

**参数约束：**

- **需要统计或分析的具体内容。格式应该类似：{数据类型（如商品数据、关键词数据、细分市场数据）},{过滤要求-非必要},{统计分析要求}，不要包含数据来源说明和之前数据的查询条件**: 必填, `卖家精灵的商品数据中，按品牌统计月销量、月销售额、月销量占比`=工具名：卖家精灵，支持的统计维度有：品牌(brand)、配送方式(fulfillment)、价格(price)、评分(rating)、上架时间(availableDate)、类目路径(nodeLabelPath)、币种(currency)、尺寸类型(dimensionsType)、包装尺寸类型(packageDimensionType)、amazon choice标识(badgeAmazonChoice)、Best Seller标识(badgeBestSeller)、A+页面(badgeEbc)、视频介绍(badgeVideo)、release标识(badgeNewRelease)。支持的统计指标有：月销量(monthlySalesUnits)、月销售额(monthlySalesRevenue)、BSR排名(bsr)、评分数(ratings)、利润率(profit)、月销量增长率(monthlySalesUnitsGrowthRate)、BSR增长率(bsrGrowthRate)、listing质量得分(listingQualityScore)、fba运费(fba)、留评率(ratingsRate), `店雷达-1688商品榜单的商品数据中，按起批量统计销售件数、预估销售额、销售件数占比`=工具名：店雷达-1688商品榜单，支持的统计维度有：发货时间(deliveryTime)、数据类型(dataType)、起批量(quantityBegin)、商品上架时间(availableDate)、类目层级名称(levelName)、单位(unit)、店铺名称(company)、币种(currency)，支持的统计指标有：销售笔数(salesOrderCount)、预估销售额(estimatedSalesAmount)、代发价(consignPrice)、批发价(price)、销售件数(salesQuantity), `店雷达-1688选品库的商品数据中，按起批量统计销售件数、预估销售额、销售件数占比`=工具名：店雷达-1688选品库，支持的统计维度有：发货时间(deliveryTime)、类目层级名称(levelName)、单位(unit)、店铺名称(company)、币种(currency)、上架时间(availableDate)，支持的统计指标有：销售笔数(salesOrderCount)、起批量(quantityBegin)、预估销售额(estimatedSalesAmount)、代发价(consignPrice)、批发价(price)、销售件数(salesQuantity), `echotik的商品搜索数据中，按商品品类统计销量、销售额、销量占比`=工具名：EchoTik-TikTok商品搜索，支持的统计维度有：商品品类(categoryName)、区域(region)、是否包邮(freeShipping)、是否S店(isSShop)、商品评分(productRating)、上架日期(availableDate)、货币(currency)。支持的统计指标有：总销量(totalSaleCnt)、总销售额(totalSaleGmvAmt)、商品价格(price)、评论数(ratings)、1/7/15/30/60/90天销量、1/7/15/30/60/90天销售额、商品佣金比例(productCommissionRate)、SPU平均价格(spuAvgPrice)。, `echotik的新品榜数据中，按商品分类ID统计销量、销售额、销量占比`=工具名：EchoTik-TikTok新品榜，支持的统计维度有：首次爬取日期(availableDate)、货币(currency)、区域代码(region)、商品评分(productRating)、商品分类ID(categoryId)支持的统计指标有：近30天销量(totalSale30dCnt)、近30天销售额(totalSaleGmv30dAmt)、视频总数(totalVideoCnt)、直播总数(totalLiveCnt)、总达人数(totalIflCnt)、总销售额(totalSaleGmvAmt)、评论数量(reviewCount)、SPU平均价格(price)、总销量(totalSaleCnt)、最低价格(minPrice)、最高价格(maxPrice)、商品佣金比例(productCommissionRate), `亚马逊前端搜索模拟的数据中，按品牌统计月销量、月销售额、月销量占比`=支持的统计维度有：品牌(brand)、评分(rating)、上架时间(availableDate)、币种(currency)、配送信息(fulfillment)。支持的统计指标有：月销量(monthlySalesUnits)、月销售额(monthlySalesRevenue)、价格(price)、评分数(ratings)、月销量增长率(monthlySalesUnitsGrowthRate)、解析后的价格(extractedPrice)、解析后的划线价格(extractedOldPrice), `SIF关键词数据中，按流量来源统计搜索量`=, `亚马逊前端-商品详情中，查询前面所有的数据`=

---

### @excel内容提取并分析

文件-文件内容提取

工具中文名：excel内容提取并分析
功能说明：读取并分析 Excel 文件（通过 URL），支持计算和统计分析，返回文本形式的分析结果。仅支持 Excel 文件，不支持 JSON 数据。
与@智能Excel处理的区别：本工具输出文本分析结果；@智能Excel处理 输出处理后的 Excel 文件 URL。

**参数约束：**

- **Excel文件下载链接**: 必填
- **任务的要求，示例如：分析这个Excel文件，计算销售总额，生成报表等**: 必填

---

### @Python沙箱

用AI生成python代码并在沙箱内执行代码

工具中文名：Python沙箱
功能说明：内置 LLM，凡涉及沙箱执行的任务都使用本工具。处理前序工具返回的结构化 JSON 数据，支持数据计算、筛选、排序，生成 Markdown 表格，导出 CSV 或 Excel 文件，以及使用 LLM 对图片 URL 进行识别（如识别 A+/附图的颜色、构图）。
重要限制：
- 禁止嵌套调用：不支持嵌套调用自身，本工具生成的结果不能再次被自身处理
- 仅限结构化数据：只能处理结构化 JSON 数据，不能处理非结构化的文本或文件内容
- 不支持可视化：不支持绘制图表、生成建议或分析报告

**参数约束：**

- **文件英文名称，仅当用户明确要求生成文件供下载时才传入此参数，如用户要求'导出'、'下载'、'生成文件'等。如：amazon-xxx-data-20250924**
- **文件类型，仅当用户明确要求生成文件供下载时才传入此参数，如用户要求'导出'、'下载'、'生成文件'等。目前仅支持：csv,xlsx**
- **任务的要求，示例如：读取上一步的数据，并计算XXXX的值**: 必填

---

### @智能Excel处理


工具中文名：智能Excel处理
功能说明：分析和处理 Excel/CSV 文件，支持新增计算列、删除列、AI 识别列（如从图片URL提取颜色、从标题提取卖点），返回处理后的 Excel 文件 URL。仅支持 Excel 文件，不支持 JSON 数据。

**参数约束：**

- **Excel文件下载链接**: 必填
- **用户的具体需求**: 必填

---
