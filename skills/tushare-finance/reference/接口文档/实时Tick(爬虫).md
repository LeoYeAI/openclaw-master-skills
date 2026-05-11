# 实时Tick（爬虫）

**文档ID**: 315
**原始链接**: https://tushare.pro/document/2?doc_id=315

---

## 实时盘口TICK快照(爬虫版)

接口：realtime_quote，A股实时行情描述：本接口是tushare org版实时接口的顺延，数据来自网络，且不进入tushare服务器，属于爬虫接口，请将tushare升级到1.3.3版本以上。权限：0积分完全开放，但需要有tushare账号，如果没有账号请先注册。说明：由于该接口是纯爬虫程序，跟tushare服务器无关，因此tushare不对数据内容和质量负责。数据主要用于研究和学习使用，如做商业目的，请自行解决合规问题。

输入参数

<table>
<thead>
<tr>
<th>名称</th>
<th>类型</th>
<th>必选</th>
<th>描述</th>
</tr>
</thead>
<tbody><tr>
<td>ts_code</td>
<td>str</td>
<td>N</td>
<td>股票代码，需按tushare<a href="https://tushare.pro/document/2?doc_id=14">股票和指数标准</a>代码输入，比如：000001.SZ表示平安银行，000001.SH表示上证指数</td>
</tr>
<tr>
<td>src</td>
<td>str</td>
<td>N</td>
<td>数据源 （sina-新浪 dc-东方财富，默认sina）</td>
</tr>
</tbody></table>
<table>
<thead>
<tr>
<th>src源</th>
<th>说明</th>
<th>描述</th>
</tr>
</thead>
<tbody><tr>
<td>sina</td>
<td>新浪财经</td>
<td>支持多个多个股票同时输入，举例：ts_code='600000.SH,000001.SZ'），一次最多不能超过50个股票</td>
</tr>
<tr>
<td>dc</td>
<td>东方财富</td>
<td>只支持单个股票提取</td>
</tr>
</tbody></table>
输出参数

<table>
<thead>
<tr>
<th>名称</th>
<th>类型</th>
<th>描述</th>
</tr>
</thead>
<tbody><tr>
<td>name</td>
<td>str</td>
<td>股票名称</td>
</tr>
<tr>
<td>ts_code</td>
<td>str</td>
<td>股票代码</td>
</tr>
<tr>
<td>date</td>
<td>str</td>
<td>交易日期</td>
</tr>
<tr>
<td>time</td>
<td>str</td>
<td>交易时间</td>
</tr>
<tr>
<td>open</td>
<td>float</td>
<td>开盘价</td>
</tr>
<tr>
<td>pre_close</td>
<td>float</td>
<td>昨收价</td>
</tr>
<tr>
<td>price</td>
<td>float</td>
<td>现价</td>
</tr>
<tr>
<td>high</td>
<td>float</td>
<td>今日最高价</td>
</tr>
<tr>
<td>low</td>
<td>float</td>
<td>今日最低价</td>
</tr>
<tr>
<td>bid</td>
<td>float</td>
<td>竞买价，即“买一”报价（元）</td>
</tr>
<tr>
<td>ask</td>
<td>float</td>
<td>竞卖价，即“卖一”报价（元）</td>
</tr>
<tr>
<td>volume</td>
<td>int</td>
<td>成交量（src=sina时是股，src=dc时是手）</td>
</tr>
<tr>
<td>amount</td>
<td>float</td>
<td>成交金额（元 CNY）</td>
</tr>
<tr>
<td>b1_v</td>
<td>float</td>
<td>委买一（量，单位：手，下同）</td>
</tr>
<tr>
<td>b1_p</td>
<td>float</td>
<td>委买一（价，单位：元，下同）</td>
</tr>
<tr>
<td>b2_v</td>
<td>float</td>
<td>委买二（量）</td>
</tr>
<tr>
<td>b2_p</td>
<td>float</td>
<td>委买二（价）</td>
</tr>
<tr>
<td>b3_v</td>
<td>float</td>
<td>委买三（量）</td>
</tr>
<tr>
<td>b3_p</td>
<td>float</td>
<td>委买三（价）</td>
</tr>
<tr>
<td>b4_v</td>
<td>float</td>
<td>委买四（量）</td>
</tr>
<tr>
<td>b4_p</td>
<td>float</td>
<td>委买四（价）</td>
</tr>
<tr>
<td>b5_v</td>
<td>float</td>
<td>委买五（量）</td>
</tr>
<tr>
<td>b5_p</td>
<td>float</td>
<td>委买五（价）</td>
</tr>
<tr>
<td>a1_v</td>
<td>float</td>
<td>委卖一（量，单位：手，下同）</td>
</tr>
<tr>
<td>a1_p</td>
<td>float</td>
<td>委卖一（价，单位：元，下同）</td>
</tr>
<tr>
<td>a2_v</td>
<td>float</td>
<td>委卖二（量）</td>
</tr>
<tr>
<td>a2_p</td>
<td>float</td>
<td>委卖二（价）</td>
</tr>
<tr>
<td>a3_v</td>
<td>float</td>
<td>委卖三（量）</td>
</tr>
<tr>
<td>a3_p</td>
<td>float</td>
<td>委卖三（价）</td>
</tr>
<tr>
<td>a4_v</td>
<td>float</td>
<td>委卖四（量）</td>
</tr>
<tr>
<td>a4_p</td>
<td>float</td>
<td>委卖四（价）</td>
</tr>
<tr>
<td>a5_v</td>
<td>float</td>
<td>委卖五（量）</td>
</tr>
<tr>
<td>a5_p</td>
<td>float</td>
<td>委卖五（价）</td>
</tr>
</tbody></table>
接口用法

```

import tushare as ts

#设置你的token，登录tushare在个人用户中心里拷贝
ts.set_token('你的token')

#sina数据
df = ts.realtime_quote(ts_code='600000.SH,000001.SZ,000001.SH')


#东财数据
df = ts.realtime_quote(ts_code='600000.SH', src='dc')

```

数据样例

```
     NAME    TS_CODE      DATE      TIME       OPEN  PRE_CLOSE      PRICE  ...   A2_P  A3_V   A3_P  A4_V   A4_P  A5_V   A5_P
0  浦发银行  600000.SH  20231222  15:00:00      6.570      6.570      6.580  ...  6.590  1834  6.600  4107  6.610  2684  6.620
1  平安银行  000001.SH  20231222  15:00:00      9.190      9.170      9.200  ...  9.210  2177  9.220  2568  9.230  2319  9.240
2  上证指数  000001.SH  20231222  15:30:39  2919.2879  2918.7149  2914.7752  ...      0            0            0            0

```
