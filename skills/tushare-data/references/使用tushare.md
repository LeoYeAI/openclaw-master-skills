## 调取pro版数据

------------

下面介绍两种常用的数据调取方式：

-  通过tushare python包
-  使用http协议直接获取

<font color="red">注：pro版数据接口采用语言无关的http协议实现，但也提供了多种语言的[SDK数据获取](https://waditu.com/document/1?doc_id=129 )。</font>

### 前提条件

1、已经注册了tushare社区用户 【[注册用户](https://waditu.com/register)】
2、已经获取到tushare token凭证 【[获取token](https://waditu.com/document/1?doc_id=39)】

### Python SDK

#### 下载SDK

下载并安装最新版tushare SDK 【[安装和升级方法](https://waditu.com/document/1?doc_id=7)】

**导入tushare**

```python
import tushare as ts
```

这里注意， tushare版本需大于1.2.10

**设置token**

```python
ts.set_token('your token here')
```

以上方法只需要在第一次或者token失效后调用，完成调取tushare数据凭证的设置，正常情况下不需要重复设置。也可以忽略此步骤，直接用pro_api('your token')完成初始化


**初始化pro接口**

```python
pro = ts.pro_api()
```

如果上一步骤ts.set_token('your token')无效或不想保存token到本地，也可以在初始化接口里直接设置token:

```python
pro = ts.pro_api('your token')

```


**数据调取**

以获取交易日历信息为例：

```python
df = pro.trade_cal(exchange='', start_date='20180901', end_date='20181001', fields='exchange,cal_date,is_open,pretrade_date', is_open='0')
```

或者

```python
df = pro.query('trade_cal', exchange='', start_date='20180901', end_date='20181001', fields='exchange,cal_date,is_open,pretrade_date', is_open='0')
```

调取结果：
```
    exchange  cal_date    is_open pretrade_date
0          SSE       20180901        0      20180831
1          SSE       20180902        0      20180831
2          SSE       20180908        0      20180907
3          SSE       20180909        0      20180907
4          SSE       20180915        0      20180914
5          SSE       20180916        0      20180914
6          SSE       20180922        0      20180921
7          SSE       20180923        0      20180921
8          SSE       20180924        0      20180921
9          SSE       20180929        0      20180928
10         SSE       20180930        0      20180928
11         SSE       20181001        0      20180928
```

### HTTP协议方式

http restful 采用post方式，通过json body传入接口参数，请求地址为http://api.waditu.com 

#### 输入参数

- api_name，接口名称；
- token，用于识别唯一用户的标识；
- params，接口参数，如daily接口中start_date和end_date；
- fields，字段列表，用于接口获取指定的字段，以逗号分隔，如"open,high,low,close"；

#### 输出参数

- code: 接口返回码，2002表示权限问题。
- msg: 错误信息；
- data: 具体数据，成功的请求包含fields和items字段，fields与items数据一一对齐；

#### 示例

采用命令行工具curl的请求示例如下：

```bash
curl -X POST -d '{"api_name": "trade_cal", "token": "xxxxxxxx", "params": {"exchange":"", "start_date":"20180901", "end_date":"20181001", "is_open":"0"}, "fields": "exchange,cal_date,is_open,pretrade_date"}' http://api.waditu.com
```

返回结果：


	{
			"code":0,
			"msg":null,
			"data":{
					"fields":[
							"exchange",
							"cal_date",
							"is_open",
							"pretrade_date"
					],
					"items":[
							[
									"SSE",
									"20180901",
									0,
									"20180831"
							],
							[
									"SSE",
									"20180902",
									0,
									"20180831"
							],
							[
									"SSE",
									"20180908",
									0,
									"20180907"
							],

				...

							[
									"SSE",
									"20180929",
									0,
									"20180928"
							],
							[
									"SSE",
									"20180930",
									0,
									"20180928"
							],
							[
									"SSE",
									"20181001",
									0,
									"20180928"
							]
					]
			}
	}