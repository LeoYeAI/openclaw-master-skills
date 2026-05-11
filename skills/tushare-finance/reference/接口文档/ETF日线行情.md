# ETF日线行情

**文档ID**: 127
**原始链接**: https://tushare.pro/document/2?doc_id=127

---

## ETF日线行情

接口：fund_daily描述：获取ETF行情每日收盘后成交数据，历史超过10年限量：单次最大2000行记录，可以根据ETF代码和日期循环获取历史，总量不限制积分：需要至少5000积分才可以调取，5000积分频次更高，具体请参阅积分获取办法

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
<tbody>
<tr>
<td>ts_code</td>
<td>str</td>
<td>N</td>
<td>基金代码</td>
</tr>
<tr>
<td>trade_date</td>
<td>str</td>
<td>N</td>
<td>交易日期(YYYYMMDD格式，下同)</td>
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
</tbody>
</table>
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
<tbody>
<tr>
<td>ts_code</td>
<td>str</td>
<td>Y</td>
<td>TS代码</td>
</tr>
<tr>
<td>trade_date</td>
<td>str</td>
<td>Y</td>
<td>交易日期</td>
</tr>
<tr>
<td>open</td>
<td>float</td>
<td>Y</td>
<td>开盘价(元)</td>
</tr>
<tr>
<td>high</td>
<td>float</td>
<td>Y</td>
<td>最高价(元)</td>
</tr>
<tr>
<td>low</td>
<td>float</td>
<td>Y</td>
<td>最低价(元)</td>
</tr>
<tr>
<td>close</td>
<td>float</td>
<td>Y</td>
<td>收盘价(元)</td>
</tr>
<tr>
<td>pre_close</td>
<td>float</td>
<td>Y</td>
<td>昨收盘价(元)</td>
</tr>
<tr>
<td>change</td>
<td>float</td>
<td>Y</td>
<td>涨跌额(元)</td>
</tr>
<tr>
<td>pct_chg</td>
<td>float</td>
<td>Y</td>
<td>涨跌幅(%)</td>
</tr>
<tr>
<td>vol</td>
<td>float</td>
<td>Y</td>
<td>成交量(手)</td>
</tr>
<tr>
<td>amount</td>
<td>float</td>
<td>Y</td>
<td>成交额(千元)</td>
</tr>
</tbody>
</table>
接口示例

```
pro = ts.pro_api()

#获取”沪深300ETF华夏”ETF2025年以来的行情，并通过fields参数指定输出了部分字段
df = pro.fund_daily(ts_code='510330.SH', start_date='20250101', end_date='20250618', fields='trade_date,open,high,low,close,vol,amount')

```

数据示例

```
   trade_date   open   high    low  close         vol       amount
0     20250618  4.008  4.024  3.996  4.017   382896.00   153574.446
1     20250617  4.015  4.022  4.000  4.014   440272.04   176617.125
2     20250616  4.000  4.018  3.996  4.015   423526.00   169788.251
3     20250613  4.023  4.028  3.992  4.004  1216787.53   487632.318
4     20250612  4.023  4.039  4.005  4.032   574727.00   231356.321
..         ...    ...    ...    ...    ...         ...          ...
104   20250108  3.971  3.992  3.908  3.963  3200416.00  1267465.456
105   20250107  3.939  3.974  3.929  3.973  2239739.00   885818.954
106   20250106  3.950  3.964  3.917  3.943  1583794.00   624004.760
107   20250103  4.002  4.013  3.944  3.963  2025111.00   805573.289
108   20250102  4.110  4.117  3.973  4.001  1768592.00   714820.885

```
