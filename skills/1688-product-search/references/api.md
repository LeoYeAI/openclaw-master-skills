# 1688 Product Search API 接口文档

## 类目查询接口

### 请求地址
```
POST https://gw.open.1688.com/openapi/param2/1/com.alibaba.fenxiao.crossborder/category.translation.getById/${APPKEY}
```

### 请求参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| categoryId | string | 是 | 类目ID，0表示获取所有一级类目 |
| language | string | 否 | 语言代码，默认en |
| access_token | string | 是 | 访问令牌 |
| _aop_signature | string | 是 | 签名 |

## 关键词搜索接口

### 请求地址
```
POST https://gw.open.1688.com/openapi/param2/1/com.alibaba.fenxiao.crossborder/product.search.keywordQuery/${APPKEY}
```

### 请求参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchParams | string | 是 | JSON格式的搜索参数 |
| access_token | string | 是 | 访问令牌 |
| _aop_signature | string | 是 | 签名 |

### searchParams 结构
```json
{
  "keyword": "dress",
  "country": "en",
  "pageNo": 1,
  "pageSize": 20,
  "filter": "shipIn48Hours,certifiedFactory",
  "sort": "{\"price\":\"asc\"}"
}
```

## 图片搜索接口

### 请求地址
```
POST https://gw.open.1688.com/openapi/param2/1/com.alibaba.fenxiao.crossborder/product.search.imageQuery/${APPKEY}
```

### searchParams 结构
```json
{
  "imageId": "your_image_id",
  "country": "en", 
  "pageNo": 1,
  "pageSize": 20
}
```

## 商品详情接口

### 请求地址
```
POST https://gw.open.1688.com/openapi/param2/1/com.alibaba.fenxiao.crossborder/product.search.queryProductDetail/${APPKEY}
```

### detailParams 结构
```json
{
  "offerIds": ["offer_id1", "offer_id2"],
  "country": "en"
}
```

## 店铺搜索接口

### 请求地址
```
POST https://gw.open.1688.com/openapi/param2/1/com.alibaba.fenxiao.crossborder/product.search.shopSearch/${APPKEY}
```

### searchParams 结构
```json
{
  "sellerOpenId": "seller_open_id",
  "country": "en",
  "pageNo": 1, 
  "pageSize": 20
}
```

## 商品推荐接口

### 请求地址
```
POST https://gw.open.1688.com/openapi/param2/1/com.alibaba.fenxiao.crossborder/product.search.offerRecommend/${APPKEY}
```

### recommendParams 结构
```json
{
  "keyword": "dress",
  "country": "en",
  "pageNo": 1,
  "pageSize": 20
}
```

## 搜索导航接口

### 请求地址
```
POST https://gw.open.1688.com/openapi/param2/1/com.alibaba.fenxiao.crossborder/product.search.keywordSNQuery/${APPKEY}
```

### navParams 结构
```json
{
  "keyword": "dress", 
  "country": "en"
}
```

## 相关推荐接口

### 请求地址
```
POST https://gw.open.1688.com/openapi/param2/1/com.alibaba.fenxiao.crossborder/product.related.recommend/${APPKEY}
```

### recommendParams 结构
```json
{
  "offerId": "offer_id",
  "country": "en",
  "pageNo": 1,
  "pageSize": 20
}
```

## 图片上传接口

### 请求地址
```
POST https://gw.open.1688.com/openapi/param2/1/com.alibaba.fenxiao.crossborder/product.image.upload/${APPKEY}
```

### uploadParams 结构
```json
{
  "imageBase64": "base64_encoded_image_data"
}
```

## 签名规则

1. 将所有请求参数（除_aop_signature外）按key的字母顺序排序
2. 将排序后的参数拼接成字符串：`key1value1key2value2...`
3. 在拼接字符串前加上URL路径（从param2开始）
4. 对结果进行HMAC-SHA1加密，并转换为大写十六进制

## 错误码

| 错误码 | 说明 |
|--------|------|
| gw.SignatureInvalid | 签名无效 |
| gw.ParamMissing | 参数缺失 |
| 401 | 未授权/Token无效 |
| 400 | 参数错误 |
| 403 | 无权限调用 |