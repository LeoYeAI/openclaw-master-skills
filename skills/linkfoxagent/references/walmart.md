# Walmart前台

共 1 个工具。使用 `@工具中文名` 语法在任务提示词中调用。

### @walmart前端-商品列表

商品列表，精准检索

工具中文名：walmart前端-商品列表
功能说明：获取 walmart 商品列表页数据，支持按关键词、类目、站点等条件检索，返回符合条件的商品列表信息

**Prompt 模板：**

> 获取 walmart，关键词为:{{air fryer}}的,最低价 9.9 美金，次日达，第1-3页的商品

`{{}}` 中的内容为需要替换的参数。

**参数约束：**

- **激活拼写修正，true(默认)包含拼写修正，false不包含**
- **排序方式**: `price_low`=价格从低到高, `price_high`=价格从高到低, `best_seller`=最畅销, `best_match`=最佳匹配
- **商店ID，用于按特定商店筛选产品**: `806`=88001 - 571 Walton Blvd, `4145`=29650 - 805 W Wade Hampton Blvd Ste B, `5023`=91950 - 1200 Highland Ave, National City, CA, `5817`=32277 - 8011 Merrill Rd, `2200`=06340 - 150 Gold Star Hwy, Groton, CT, `1862`=92376 - 1366 S Riverside Ave, `134`=73644 - 210 Regional Dr, Elk City, OK, `3893`=60099 - 4000 Il Route 173, Zion, IL, `3176`=80909 - 1725 N Union Blvd, `4333`=36532 - 10040 County Road 48, Fairhope, AL, `536`=79601 - 1650 State Highway 351, `1455`=76120 - 8401 Anderson Blvd, `507`=40342 - 1000 Bypass N, Lawrenceburg, KY, `590`=76132 - 6300 Oakmont Blvd, `1753`=03038 - 11 Ashleigh Drive, Derry, NH, `2512`=85023 - 1825 W Bell Rd, `3274`=76182 - 9101 N Tarrant Pkwy, `7043`=84065 - 1202 West 12600 South, `1360`=25840 - 204 Town Center Rd, Fayetteville, WV, `2690`=35758 - 8650 Madison Blvd, ...等共100个值
- **仅显示NextDay配送结果，true启用，false(默认)禁用**
- **最低价格**
- **按相关性排序，默认为true。设置为false可禁用按相关性排序**
- **最高价格**
- **页码，用于分页，默认为1，最大值为100**
- **搜索关键词，与cat_id至少提供一个**
- **JSON字段限制器**
- **过滤条件，格式为key:value对，用||分隔**
- **设备类型，可选值：desktop(默认), tablet, mobile**: `desktop`=桌面浏览器, `tablet`=平板浏览器, `mobile`=移动浏览器
- **类目ID，与query至少提供一个。例如：0(默认)表示所有部门，976759_976787表示'Cookies'**

---
