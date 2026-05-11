# 港股实时日线

**文档ID**: 383
**原始链接**: https://tushare.pro/document/2?doc_id=383

---

## 港股实时日线

接口：rt_hk_k描述：获取港股实时日k线行情，支持按股票代码及股票代码通配符一次性提取全部股票实时日k线行情限量：单次最大可提取5000条数据积分：本接口是单独开权限的数据，单独申请权限请参考权限列表

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
<td>支持通配符方式，e.g. 00001.HK、02*.HK</td>
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
<td>股票代码</td>
</tr>
<tr>
<td>pre_close</td>
<td>float</td>
<td>Y</td>
<td>昨收价</td>
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
<td>open</td>
<td>float</td>
<td>Y</td>
<td>开盘价</td>
</tr>
<tr>
<td>low</td>
<td>float</td>
<td>Y</td>
<td>最低价</td>
</tr>
<tr>
<td>vol</td>
<td>float</td>
<td>Y</td>
<td>成交量（股）</td>
</tr>
<tr>
<td>amount</td>
<td>float</td>
<td>Y</td>
<td>成交额(元)</td>
</tr>
</tbody></table>
接口示例

```

#获取特定股票实时日线
df = pro.rt_hk_k(ts_code='00001.HK')

#获取今日开盘以来部分港股实时日线
df = pro.rt_hk_k(ts_code='01*.HK')

```

数据示例

```
       ts_code  pre_close  close   high   open    low            vol       amount
0    01508.HK      1.040  1.030  1.050  1.040  1.030  14971000.0  15564320.00
1    01314.HK      0.210  0.211  0.211  0.210  0.210     40000.0      8420.00
2    01848.HK      3.940  3.910  3.950  3.940  3.890    300500.0   1176380.00
3    01150.HK      0.091  0.103  0.106  0.106  0.100     45000.0      4580.00
4    01875.HK      1.860  1.970  1.970  1.930  1.890    164000.0    316064.00
..        ...        ...    ...    ...    ...    ...         ...          ...
746  01653.HK      0.260  0.000  0.000  0.000  0.000         0.0         0.00
747  01729.HK      5.440  5.790  5.800  5.440  5.380   6778621.0  37845706.87
748  01608.HK      0.290  0.285  0.290  0.290  0.285    142000.0     41170.00
749  01247.HK      1.700  1.700  1.750  1.740  1.700    120400.0    206708.00
750  01878.HK      1.890  1.900  1.950  1.900  1.840    191100.0    362691.00

```
