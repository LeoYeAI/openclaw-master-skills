---
name: 1688-Product-to-Ozon
category: official-1688
description: 将1688的商品铺货到俄罗斯电商平台Ozon（上架），通过Ozon官方API实现商品信息的上传和状态查询。适用于需要将单个1688的商品上架到Ozon的场景。
created: 2026-03-19
metadata:
  version: 1.2.1
  label: 1688铺货Ozon
  author: 1688官方技术团队
---

# 1688到Ozon商品转换技能

## 技能描述

本技能用于将1688的商品转化为对应的俄罗斯电商平台Ozon的商品数据，产出一个可以用于操作Ozon的上架API的JSON结构化数据。
之后再通过Ozon的开放平台的接口将商品信息上传到Ozon平台并查询上传结果。可以把1688的商品铺货到Ozon，上架到Ozon，上传到Ozon、上架Ozon、Ozon商品发布、Ozon产品上传、查询Ozon上传结果、铺货、1688商品铺货。

触发词：上传到Ozon、上架Ozon、Ozon商品发布、Ozon产品上传、查询Ozon上传结果、铺货、1688商品铺货。


## 什么时候使用

用户说需要铺货到Ozon、上架到Ozon、上传到Ozon、Ozon商品发布、Ozon产品上传、查询Ozon上传结果、铺货、1688商品铺货等。

## 前置配置（必须先完成）

⚠️ **使用本 SKILL 前，必须先配置以下参数，否则铺货流程会失败。**

| 环境变量 | 说明 | 必填 | 获取方式 |
|---------|------|------|---------|
| `OZON_API_KEY` | Ozon 卖家后台的 API Key | ✅ 必填 | 在 [Ozon 卖家后台](https://seller.ozon.ru/) → API 设置中生成 |
| `OZON_CLIENT_ID` | Ozon 卖家后台的 Client ID | ✅ 必填 | 在 [Ozon 卖家后台](https://seller.ozon.ru/) → API 设置中查看 |
| `OZON_CURRENCY` | 货币代码，必须与 Ozon 个人中心设置的币种匹配 | ✅ 必填（默认 `RUB`） | `RUB`（卢布）或 `CNY`（人民币），货币不匹配会导致 API 报错 |
| `ALPHASHOP_ACCESS_KEY` | AlphaShop API Access Key（用于图片翻译） | ✅ 必填 | 可以访问1688-AlphaShop（遨虾）来申请 https://www.alphashop.cn/seller-center/apikey-management ，直接使用1688/淘宝/支付宝/手机登录即可 |
| `ALPHASHOP_SECRET_KEY` | AlphaShop API Secret Key（用于图片翻译） | ✅ 必填 | 可以访问1688-AlphaShop（遨虾）来申请 https://www.alphashop.cn/seller-center/apikey-management ，直接使用1688/淘宝/支付宝/手机登录即可 |

如果用户没有提供这些参数，**必须先询问用户获取后再继续操作**。

**⚠️ AlphaShop 接口欠费处理：** 如果调用 AlphaShop 接口时返回欠费/余额不足相关的错误，**必须立即中断当前流程**，提示用户前往 https://www.alphashop.cn/seller-center/home/api-list 购买积分后再继续操作。

### 配置方式

**Ozon 密钥配置文件位置**：`~/.openclaw/skillconfig/1688-Product-to-Ozon/ozon_config.json`
```json
{
  "OZON_API_KEY": "your-api-key",
  "OZON_CLIENT_ID": "your-client-id",
  "OZON_CURRENCY": "CNY"
}
```

**AlphaShop 密钥**在 OpenClaw config 中配置：
```json5
{
  skills: {
    entries: {
      "1688-Product-to-Ozon": {
        env: {
          ALPHASHOP_ACCESS_KEY: "YOUR_AK",
          ALPHASHOP_SECRET_KEY: "YOUR_SK"
        }
      }
    }
  }
}
```

## 核心功能

### 1. **1688到Ozon类目映射**
- 调用1688 OpenClaw API获取商品对应的Ozon类目
- 输入：1688商品类目ID，从结构信息中获取，优先取thirdCategoryId的值，如果没有，获取categoryId的值，传递的应当是类目的值！！是数字
- 输出：对应的Ozon类目信息

### 2. **获取Ozon类目属性要求**
- 查询Ozon API获取目标类目的所有属性要求
- 输入：Ozon类目ID（多个用逗号分隔）、用户认证信息（OZON_API_KEY、OZON_CLIENT_ID）
- 输出：属性列表和详细要求
- 注意：直接使用上一步骤中获取到的externalCategoryId，这个值一般有两个，由逗号分隔，不要只取其中一个作为类目ID

### 3 **查询字典属性的可选值（必须执行）**
- 在获取到类目属性列表后，对所有 `dictionary_id > 0` 的属性，必须先查询该属性的字典值列表
- **不要猜测或手写 dictionary_value_id**，必须通过脚本查询获取，否则会导致 `error_attribute_values_out_of_range` 错误

**工作流程：**
1. 先用 `queryOzonProperties.py` 获取属性列表
2. 筛选出所有 `dictionary_id > 0` 的属性
3. 对每个字典属性，用 `queryDictionaryValues.py` 查询可选值
4. 从返回结果中获取正确的 `id` 值（即 `dictionary_value_id`），填入商品数据

**使用 `queryDictionaryValues.py` 脚本查询字典值：**

```bash
# 搜索模式 - 根据关键词搜索匹配的字典值（推荐，更精准）
python queryDictionaryValues.py \
  --attribute_id 85 \
  --description_category_id 17028922 \
  --type_id 91565 \
  --search "Нет бренда"

# 列表模式 - 列出所有可选值（当不确定关键词时使用）
python queryDictionaryValues.py \
  --attribute_id 85 \
  --description_category_id 17028922 \
  --type_id 91565 \
  --limit 50
```

**参数说明：**
- `--attribute_id`: 属性ID（从 Step 2 获取的属性列表中取）
- `--description_category_id`: 描述类目ID（从类目映射结果中取）
- `--type_id`: 类型ID（从类目映射结果中取）
- `--search`: 搜索关键词（可选，用俄语，不传则列出所有值）
- `--limit`: 返回数量限制（默认50）

**输出格式：** JSON 数组，每个元素包含 `id`（即 dictionary_value_id）和 `value`

- 常见需要查询的属性：品牌(85/31)、类型(8229)、颜色(10096)、尺码(4295)、性别(9163)、材质、季节等

### 4. **商品数据结构转换**
- 这一步非常重要，要使用上述两部分能力产出的数据！！！
- 由AI大模型接收1688商品信息和Ozon属性要求
- 智能映射和转换商品属性
- 输入：Ozon的类目属性要求、1688的商品数据（JSON格式）、**Step 2.5查到的字典值**
- 输出：符合Ozon上架结构的商品结构（JSON格式）

#### Ozon的结构要求
这个是Ozon的结构实例，你需要按照这样的结构规范生成Ozon的商品数据，严格保持这个数据结构

```
{
    "items": [
        {
            "attributes": [
                {
                    "complex_id": 0,
                    "id": 5076,
                    "values": [
                        {
                            "dictionary_value_id": 971082156,
                            "value": "麦克风架"
                        }
                    ]
                },
                {
                    "complex_id": 0,
                    "id": 9048,
                    "values": [
                        {
                            "value": "一套X3NFC保护膜。 深色棉质"
                        }
                    ]
                },
                {
                    "complex_id": 0,
                    "id": 8229,
                    "values": [
                        {
                            "dictionary_value_id": 95911,
                            "value": "一套X3NFC保护膜。深色棉质"
                        }
                    ]
                },
                {
                    "complex_id": 0,
                    "id": 85,
                    "values": [
                        {
                            "dictionary_value_id": 5060050,
                            "value": "Samsung"
                        }
                    ]
                },
                {
                    "complex_id": 0,
                    "id": 10096,
                    "values": [
                        {
                            "dictionary_value_id": 61576,
                            "value": "灰色的"
                        }
                    ]
                }
            ],
            "barcode": "112772873170",
            "description_category_id": 17028922,
            "new_description_category_id": 0,
            "color_image": "",
            "complex_attributes": [],
            "currency_code": "RUB",
            "depth": 10,
            "dimension_unit": "mm",
            "height": 250,
            "images": [
                "https://example.com/translated_image_2.jpg",
                "https://example.com/translated_image_3.jpg",
                "https://example.com/translated_image_4.jpg"
            ],
            "images360": [],
            "name": "一套X3NFC的保护膜。深色棉质",
            "offer_id": "143210608",
            "old_price": "1100",
            "pdf_list": [],
            "price": "1000",
            "primary_image": "https://example.com/translated_image_1.jpg",
            "promotions": [
                {
                    "operation": "UNKNOWN",
                    "type": "REVIEWS_PROMO"
                }
            ],
            "type_id": 91565,
            "vat": "0",
            "weight": 100,
            "weight_unit": "g",
            "width": 150
        }
    ]
}
```

#### 定制化规则
- 标题一定要翻译成俄语！标题一定要翻译成俄语！标题一定要翻译成俄语！
- items代表SKU列表，和1688的SKU是一一对应的
- vat的值固定为0
- offer_id的生成规则：使用1688的SKU_ID
- "22390" 这个属性代表Ozon的型号，一个1688的商品有多个SKU，所以这些SKU在Ozon中同属于一个型号，值为1688的商品的ID（itemId）。注意：某些类目中该属性ID可能是"8292"（合并至一张卡片），功能相同，填1688商品ID即可
- attributes代表属性列表,需要按照前序步骤获取到的"Ozon类目属性要求"来生成。优先处理必填属性，"4191"（商品简介）也必须填写。在保证正确性的前提下，尽量填充所有属性（包括非必填的），能从1688商品数据中提取或推断的属性都应该填上
- 重量需要注意单位，都转化成为克（g）来处理
- 长度单位（dimension_unit）固定使用mm来处理，1688的数据都是cm为单位的数据
- 所有非数字、单位类型的值都需要翻译成俄语，例如商品的标题
- "23487"这个属性 固定值为中国
- "9048" 这个属性 使用随机生成的数字作为货号，1个1688的商品使用相同的值
- "4389" 这个属性 固定值为中国
- 品牌属性 固定值为"Нет бренда"，dictionary_value_id 为 126745801（注意：不是"Без бренда"，Ozon 的无品牌值是"Нет бренда"）。品牌属性ID在不同类目下可能不同（常见为85或31），以Step 2获取的属性列表为准
- vendor_value 这个参数固定为"Нет бренда"
- "4191" 这个属性是商品简介/描述，必须填写！根据1688商品的标题、属性、材质等信息，生成一段俄语的商品描述文案，突出卖点（材质、功能、适用场景等），填入该属性的value中


#### 建议定价逻辑
定价规则优先以你的规则为准，如果没有指定定价规则，将会使用下面的定价逻辑，将这个价格配置到price中，old_price价格为空：

按照你的OZON_CURRENCY配置的币种，进行定价，最终决定这个商品在Ozon的售价；都需要使用1688的SKU的价格来进行定价
##### 币种为RUB定价逻辑
- 如果你的货币是RUB，需要进行汇率转换
- 将1688的SKU价格乘以汇率再乘以3，得到RUB的价格

##### 币种为CNY定价逻辑
- 如果你的货币是CNY，不需要进行汇率转换
- 将1688的SKU价格乘以3，得到CNY的价格

#### 素材的处理
商品的图片需要翻译成俄语。使用本 skill 自带的 `translate_images.py` 脚本处理所有图片。

**调用方式：**

```bash
# 翻译单张图片
python translate_images.py --image-url "<图片URL>"

# 批量翻译多张图片（空格分隔）
python translate_images.py --image-url "<图片URL1>" "<图片URL2>" "<图片URL3>"
```

**认证：** 需要环境变量 `ALPHASHOP_ACCESS_KEY` 和 `ALPHASHOP_SECRET_KEY`。

**脚本说明：**
- 调用 AlphaShop 图片翻译PRO接口（`POST https://api.alphashop.cn/ai.image.translateImagePro/1.0`）
- 源语种自动识别（auto），目标语种固定为俄语（ru）
- 认证方式：JWT HS256 签名（`iss=AK, exp=now+1800, nbf=now-5`，SK 为密钥）
- 输出 JSON 格式，包含每张图片的原始URL和翻译后URL

**处理步骤：**
1. 遍历1688商品的所有图片URL（主图 + SKU图片）
2. 对每张图片调用 `translate_images.py` 进行翻译
3. 从返回结果中提取翻译后的图片URL（响应JSON中的 `translatedImageUrl` 字段）
4. 用翻译后的图片URL替换原始图片URL，填入Ozon商品结构的 `primary_image` 和 `images` 字段：
   - `primary_image`: 填入**第一张**翻译后的图片 URL
   - `images`: 填入**剩余所有**翻译后的图片 URL（数组），不包括 primary_image 中已填的那张
5. 如果某张图片翻译失败（API报错或无文字需要翻译），保留原始图片URL继续处理

**⚠️ 必须上传所有图片，不能只传一张！** 1688商品的所有主图和SKU图片都必须翻译并填入，`primary_image` 放第一张，`images` 数组放其余所有图片。

#### 商品详情描述
- 参考[offer_description.json](offer_description.json)中的内容构造商品的描述信息，使用上述的处理后的商品素材，然后构造商品详情描述
- 可以增加content中的数组，但是不要修改单个content的结构
-

#### 数据存储
创建你的商品数据文件，存储到临时目录 `tmp/my_products.json`（tmp/ 目录已被 .gitignore 排除，不会上传到 git）

**所有临时文件（商品数据、翻译缓存、类目ID等）统一存放在 `tmp/` 目录下。**

### 5. **商品上架**
- 使用Ozon API的POST `/v3/product/import`端点上传商品数据。需要提供有效的ClientId和API Key进行认证。
- 输入：Ozon格式的商品JSON结构
- 输出：商品上架任务ID

```bash
python upload_product.py --product-data my_products.json
```

### 6. **查询商品上架结果**
- 使用Ozon API的POST `/v1/product/import/info`端点查询上传任务的状态和详细结果。
- 输入：任务ID
- 输出：商品上架状态和结果
- 注意：如果结果是imported就代表上传成功了，存在的问题可以让用户去商家后台修改

```bash

python check_status.py <task_id>

```

## 工作流程

注意：如果有任意一个步骤失败了，都直接返回错误，不要想象，不要想象，不要想象

```
1. 用户输入1688商品信息
         ↓
2. AI模型：解析出1688的叶子类目（thirdCategoryId 或 categoryId）
         ↓
3. Python脚本`queryCategoryMapping.py`：查询类目映射 (1688类目ID → Ozon类目ID)
         ↓
4. AI模型：从上一步的结果中解析出来Ozon的类目（externalCategoryId，含description_category_id和type_id）
         ↓
5. Python脚本`queryOzonProperties.py`：通过externalCategoryId参数获取Ozon类目属性列表
         ↓
6 Python脚本`queryDictionaryValues.py`：对所有dictionary_id>0的属性，查询正确的dictionary_value_id，一定要执行，这里会影响到商品的上架
         ↓
7. 翻译图片：调用`translate_images.py`将商品主图和SKU图翻译为俄语
         ↓
8. AI模型：结合1688商品数据、Ozon属性要求、字典值、翻译后图片，生成符合Ozon上架规则的商品结构数据
         ↓
9. Python脚本：调用 upload_product.py 上传商品信息到Ozon
         ↓
10. Python脚本：调用 `check_upload_status.py` 查询商品上传状态（imported=成功）
         ↓
10. 输出：Ozon的上传结果
```

## 包含的脚本

### `queryCategoryMapping.py`
查询1688到Ozon的类目映射
### `queryOzonProperties.py`
查询Ozon类目属性要求
### `queryDictionaryValues.py`
查询Ozon属性的字典可选值，支持搜索模式（按关键词搜索）和列表模式（列出所有值）
### `upload_product.py`
上传商品信息到Ozon
### `check_upload_status.py`
查询商品上传状态
### `translate_images.py`
调用AlphaShop图片翻译PRO接口，将商品图片中的文字翻译为俄语（源语种自动识别）


## 使用说明

1. 提供1688商品的基本信息
2. 提供Ozon认证信息（ClientId, API Key, 货币）
3. SKILL将自动调用python脚本完成转换，把1688的商品结构转化成适合Ozon的上架的结构数据
4. SKILL将会自动调用python脚本完成上传

---

**最后更新**: 2026-03-16