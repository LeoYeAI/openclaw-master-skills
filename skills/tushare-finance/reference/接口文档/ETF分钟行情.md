# ETF分钟行情

**文档ID**: 387
**原始链接**: https://tushare.pro/document/2?doc_id=387

---

## ETF历史分钟行情

接口：stk_mins描述：获取ETF分钟数据，支持1min/5min/15min/30min/60min行情，提供Python SDK和 http Restful API两种方式限量：单次最大8000行数据，可以通过股票代码和时间循环获取，本接口可以提供超过10年ETF历史分钟数据权限：正式权限请参阅权限说明

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
<td>Y</td>
<td>ETF代码，e.g. 159001.SZ</td>
</tr>
<tr>
<td>freq</td>
<td>str</td>
<td>Y</td>
<td>分钟频度（1min/5min/15min/30min/60min）</td>
</tr>
<tr>
<td>start_date</td>
<td>datetime</td>
<td>N</td>
<td>开始日期 格式：2025-06-01 09:00:00</td>
</tr>
<tr>
<td>end_date</td>
<td>datetime</td>
<td>N</td>
<td>结束时间 格式：2025-06-20 19:00:00</td>
</tr>
</tbody></table>
freq参数说明

<table>
<thead>
<tr>
<th>freq</th>
<th>说明</th>
</tr>
</thead>
<tbody><tr>
<td>1min</td>
<td>1分钟</td>
</tr>
<tr>
<td>5min</td>
<td>5分钟</td>
</tr>
<tr>
<td>15min</td>
<td>15分钟</td>
</tr>
<tr>
<td>30min</td>
<td>30分钟</td>
</tr>
<tr>
<td>60min</td>
<td>60分钟</td>
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
<td>ts_code</td>
<td>str</td>
<td>Y</td>
<td>ETF代码</td>
</tr>
<tr>
<td>trade_time</td>
<td>str</td>
<td>Y</td>
<td>交易时间</td>
</tr>
<tr>
<td>open</td>
<td>float</td>
<td>Y</td>
<td>开盘价</td>
</tr>
<tr>
<td>close</td>
<td>float</td>
<td>Y</td>
<td>收盘价</td>
</tr>
<tr>
<td>high</td>
<td>float</td>
<td>Y</td>
<td>最高价</td>
</tr>
<tr>
<td>low</td>
<td>float</td>
<td>Y</td>
<td>最低价</td>
</tr>
<tr>
<td>vol</td>
<td>int</td>
<td>Y</td>
<td>成交量</td>
</tr>
<tr>
<td>amount</td>
<td>float</td>
<td>Y</td>
<td>成交金额</td>
</tr>
</tbody></table>
接口用法

```

pro = ts.pro_api()

#获取沪深300ETF华夏510330.SH的历史分钟数据
df = pro.stk_mins(ts_code='510330.SH', freq='1min', start_date='2025-06-20 09:00:00', end_date='2025-06-20 19:00:00')

```

数据样例

```
       ts_code           trade_time  close   open   high    low        vol      amount
0    510330.SH  2025-06-20 15:00:00  3.991  3.991  3.992  3.990   800600.0   3194805.0
1    510330.SH  2025-06-20 14:59:00  3.991  3.990  3.991  3.989   182500.0    728177.0
2    510330.SH  2025-06-20 14:58:00  3.990  3.992  3.992  3.990   113700.0    453763.0
3    510330.SH  2025-06-20 14:57:00  3.992  3.992  3.992  3.991    17400.0     69460.0
4    510330.SH  2025-06-20 14:56:00  3.992  3.992  3.992  3.991   447500.0   1786373.0
..         ...                  ...    ...    ...    ...    ...        ...         ...
236  510330.SH  2025-06-20 09:34:00  3.994  3.994  3.995  3.994  2528100.0  10097818.0
237  510330.SH  2025-06-20 09:33:00  3.994  3.991  3.994  3.991   143300.0    572084.0
238  510330.SH  2025-06-20 09:32:00  3.992  3.990  3.993  3.990  1118500.0   4463264.0
239  510330.SH  2025-06-20 09:31:00  3.988  3.984  3.992  3.984  1176100.0   4691600.0
240  510330.SH  2025-06-20 09:30:00  3.983  3.983  3.983  3.983    20700.0     82448.0

```
