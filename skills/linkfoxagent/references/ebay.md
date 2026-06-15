# eBay前台

共 1 个工具。使用 `@工具中文名` 语法在任务提示词中调用。

### @ebay前端-商品列表

商品列表，精准检索

工具中文名：ebay前端-商品列表
功能说明：获取 eBay 商品列表页数据，支持按关键词、站点、邮编等条件检索，返回符合条件的商品列表信息

**Prompt 模板：**

> 获取ebay{{美国站}}，关键词为:{{coffee machine}}的第1页的商品

`{{}}` 中的内容为需要替换的参数。

**参数约束：**

- **ZIP或邮政编码，用于按区域筛选配送产品**
- **过滤条件，多个值用逗号分隔。可选值：Complete, Sold, FR, RPA, AS, Savings, SaleItems, Lots, Charity, AV, FS, LPickup**: `Complete`=Complete, `Sold`=Sold, `FR`=FR, `RPA`=RPA, `AS`=AS, `Savings`=Savings, `SaleItems`=SaleItems, `Lots`=Lots
- **最高价格**
- **购买格式，可选值：Auction, BIN, BO**: `Auction`=Auction, `BIN`=BIN, `BO`=BO
- **每页返回的最大结果数，可选值：25, 50(默认), 100, 200**: `25`=25, `50`=50, `100`=100, `200`=200
- **排序方式，默认为'Best Match'**: `12`=Best Match (默认), `1`=Time: ending soonest, `10`=Time: newly listed, `15`=Price + Shipping: lowest first, `16`=Price + Shipping: highest first, `7`=Distance: nearest first, `3`=Price: highest first, `2`=Price: lowest first, `18`=Condition: new first, `19`=Condition: used first
- **最低价格**
- **eBay域名，默认为ebay.com**: `ebay.com.au`=澳大利亚, `ebay.at`=奥地利, `ebay.ca`=加拿大, `ebay.fr`=法国, `ebay.de`=德国, `ebay.com.hk`=中国香港, `ebay.ie`=爱尔兰, `ebay.it`=意大利, `ebay.com.my`=马来西亚, `ebay.nl`=荷兰, `ebay.pl`=波兰, `ebay.com.sg`=新加坡, `ebay.es`=西班牙, `ebay.ch`=瑞士, `ebay.co.uk`=英国, `ebay.com`=美国（默认）
- **是否不使用缓存，默认false**
- **产品所在区域**: `1`=United States, `2`=Canada, `3`=United Kingdom, `4`=Afghanistan, `5`=Albania, `6`=Algeria, `7`=American Samoa, `8`=Andorra, `9`=Angola, `10`=Anguilla, `11`=Antigua and Barbuda, `12`=Argentina, `13`=Armenia, `14`=Aruba, `15`=Australia, `16`=Austria, `17`=Azerbaijan Republic, `18`=Bahamas, `19`=Bahrain, `20`=Bangladesh, ...等共222个值
- **页码，用于分页，默认为1**
- **搜索关键词**
- **首选位置，可选值：Domestic, Regional, Worldwide**: `1`=Domestic (默认), `2`=Regional, `3`=Worldwide
- **类目ID**
- **产品条件，多个ID用|分隔，如：1000|3000**: `1000`=New, `1500`=New other (see details), `1750`=New with defects, `2000`=Certified Refurbished, `2010`=Excellent - Refurbished, `2020`=Very Good - Refurbished, `2030`=Good - Refurbished, `2500`=Seller refurbished， Remanufactured, `2750`=Like New, `2990`=Pre-owned - Excellent, `3000`=Used, Pre-owned, Pre-owned- Good, Open Box/Used, `3010`=Pre-owned - Fair, `4000`=Very Good, `5000`=Good, `6000`=Acceptable, `7000`=For parts or not working

---
