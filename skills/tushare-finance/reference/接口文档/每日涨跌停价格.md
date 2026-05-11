# 每日涨跌停价格

**文档ID**: 183
**原始链接**: https://tushare.pro/document/2?doc_id=183

---

## 每日涨跌停价格

接口：stk_limit描述：获取全市场（包含A/B股和基金）每日涨跌停价格，包括涨停价格，跌停价格等，每个交易日8点40左右更新当日股票涨跌停价格。限量：单次最多提取5800条记录，可循环调取，总量不限制积分：用户积2000积分可调取，单位分钟有流控，积分越高流量越大，请自行提高积分，具体请参阅积分获取办法

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
<td>股票代码</td>
</tr>
<tr>
<td>trade_date</td>
<td>str</td>
<td>N</td>
<td>交易日期</td>
</tr>
<tr>
<td>start_date</td>
<td>str</td>
<td>N</td>
<td>开始日期</td>
</tr>
<tr>
<td>end_date</td>
<td>str</td>
<td>N</td>
<td>结束日期</td>
</tr>
</tbody></table>
输出参数

<table>
<thead>
<tr>
<th>名称</th>
<th>类型</th>
<th>默认显示</th>
<th>描述</th>
</tr>
</thead>
<tbody><tr>
<td>trade_date</td>
<td>str</td>
<td>Y</td>
<td>交易日期</td>
</tr>
<tr>
<td>ts_code</td>
<td>str</td>
<td>Y</td>
<td>TS股票代码</td>
</tr>
<tr>
<td>pre_close</td>
<td>float</td>
<td>N</td>
<td>昨日收盘价</td>
</tr>
<tr>
<td>up_limit</td>
<td>float</td>
<td>Y</td>
<td>涨停价</td>
</tr>
<tr>
<td>down_limit</td>
<td>float</td>
<td>Y</td>
<td>跌停价</td>
</tr>
</tbody></table>
接口示例

```

pro = ts.pro_api()

#获取单日全部股票数据涨跌停价格
df = pro.stk_limit(trade_date='20190625')

#获取单个股票数据
df = pro.stk_limit(ts_code='002149.SZ', start_date='20190115', end_date='20190615')


```

数据示例

```
     trade_date    ts_code  up_limit  down_limit
0      20190625  000001.SZ     15.06       12.32
1      20190625  000002.SZ     30.94       25.32
2      20190625  000004.SZ     25.15       20.57
3      20190625  000005.SZ      3.49        2.85
4      20190625  000006.SZ      6.14        5.02
5      20190625  000007.SZ      7.74        6.34
6      20190625  000008.SZ      4.28        3.50
7      20190625  000009.SZ      6.36        5.20
8      20190625  000010.SZ      3.51        3.17
9      20190625  000011.SZ     10.58        8.66
10     20190625  000012.SZ      5.16        4.22
11     20190625  000014.SZ     10.98        8.98
12     20190625  000016.SZ      4.81        3.93
13     20190625  000017.SZ      5.15        4.21
14     20190625  000018.SZ      1.44        1.30
15     20190625  000019.SZ      8.09        6.62
16     20190625  000020.SZ     12.21        9.99
17     20190625  000021.SZ      9.30        7.61
18     20190625  000023.SZ     14.61       11.95
19     20190625  000025.SZ     23.08       18.88
20     20190625  000026.SZ      8.66        7.08

```
