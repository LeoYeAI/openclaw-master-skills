# ETF基准指数

**文档ID**: 386
**原始链接**: https://tushare.pro/document/2?doc_id=386

---

## ETF基准指数列表

接口：etf_index描述：获取ETF基准指数列表信息限量：单次请求最大返回5000行数据（当前未超过2000个）权限：用户积累8000积分可调取，具体请参阅积分获取办法

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
<td>指数代码</td>
</tr>
<tr>
<td>pub_date</td>
<td>str</td>
<td>N</td>
<td>发布日期（格式：YYYYMMDD）</td>
</tr>
<tr>
<td>base_date</td>
<td>str</td>
<td>N</td>
<td>指数基期（格式：YYYYMMDD）</td>
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
<td>指数代码</td>
</tr>
<tr>
<td>indx_name</td>
<td>str</td>
<td>Y</td>
<td>指数全称</td>
</tr>
<tr>
<td>indx_csname</td>
<td>str</td>
<td>Y</td>
<td>指数简称</td>
</tr>
<tr>
<td>pub_party_name</td>
<td>str</td>
<td>Y</td>
<td>指数发布机构</td>
</tr>
<tr>
<td>pub_date</td>
<td>str</td>
<td>Y</td>
<td>指数发布日期</td>
</tr>
<tr>
<td>base_date</td>
<td>str</td>
<td>Y</td>
<td>指数基日</td>
</tr>
<tr>
<td>bp</td>
<td>float</td>
<td>Y</td>
<td>指数基点(点)</td>
</tr>
<tr>
<td>adj_circle</td>
<td>str</td>
<td>Y</td>
<td>指数成份证券调整周期</td>
</tr>
</tbody></table>
接口示例

```

#获取当前ETF跟踪的基准指数列表
df = pro.etf_index(fields='ts_code,indx_name,pub_date,bp')


```

数据示例

```
          ts_code        indx_name         pub_date           bp
0        000068.SH         上证自然资源指数  20100528  1000.000000
1        000001.SH           上证综合指数  19910715   100.000000
2        000989.SH       中证全指可选消费指数  20110802  1000.000000
3       000990.CSI       中证全指主要消费指数  20110802  1000.000000
4        000043.SH         上证超级大盘指数  20090423  1000.000000
...            ...              ...       ...          ...
1458    932368.CSI     中证800自由现金流指数  20241211  1000.000000
1460     000680.SH        上证科创板综合指数  20250120  1000.000000
1461     000681.SH      上证科创板综合价格指数  20250120  1000.000000

```
