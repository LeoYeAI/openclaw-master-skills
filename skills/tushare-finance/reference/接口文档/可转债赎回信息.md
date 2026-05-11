# 可转债赎回信息

**文档ID**: 269
**原始链接**: https://tushare.pro/document/2?doc_id=269

---

## 可转债赎回信息

接口：cb_call，可以通过数据工具调试和查看数据。描述：获取可转债到期赎回、强制赎回等信息。数据来源于公开披露渠道，供个人和机构研究使用，请不要用于数据商业目的。限量：单次最大2000条数据，可以根据日期循环提取，本接口需5000积分。

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
<td>转债代码，支持多值输入</td>
</tr>
<tr>
<td>ann_date</td>
<td>str</td>
<td>N</td>
<td>公告日期(YYYYMMDD格式，下同)</td>
</tr>
<tr>
<td>start_date</td>
<td>str</td>
<td>N</td>
<td>公告开始日期</td>
</tr>
<tr>
<td>end_date</td>
<td>str</td>
<td>N</td>
<td>公告结束日期</td>
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
<td>转债代码</td>
</tr>
<tr>
<td>call_type</td>
<td>str</td>
<td>Y</td>
<td>赎回类型：到赎、强赎</td>
</tr>
<tr>
<td>is_call</td>
<td>str</td>
<td>Y</td>
<td>是否赎回：已满足强赎条件、公告提示强赎、公告实施强赎、公告到期赎回、公告不强赎</td>
</tr>
<tr>
<td>ann_date</td>
<td>str</td>
<td>Y</td>
<td>公告/提示日期</td>
</tr>
<tr>
<td>call_date</td>
<td>str</td>
<td>Y</td>
<td>赎回日期</td>
</tr>
<tr>
<td>call_price</td>
<td>float</td>
<td>Y</td>
<td>赎回价格(含税，元/张)</td>
</tr>
<tr>
<td>call_price_tax</td>
<td>float</td>
<td>Y</td>
<td>赎回价格(扣税，元/张)</td>
</tr>
<tr>
<td>call_vol</td>
<td>float</td>
<td>Y</td>
<td>赎回债券数量(张)</td>
</tr>
<tr>
<td>call_amount</td>
<td>float</td>
<td>Y</td>
<td>赎回金额(万元)</td>
</tr>
<tr>
<td>payment_date</td>
<td>str</td>
<td>Y</td>
<td>行权后款项到账日</td>
</tr>
<tr>
<td>call_reg_date</td>
<td>str</td>
<td>Y</td>
<td>赎回登记日</td>
</tr>
</tbody></table>
接口示例

```

pro = ts.pro_api('your token')

#获取可转债行情
df = pro.cb_call(fields='ts_code,call_type,is_call,ann_date,call_date,call_price')

```

数据示例

```
    ts_code call_type is_call  ann_date call_date call_price
0    123069.SZ        强赎   公告不强赎  20210821      None       None
1    113621.SH        强赎   公告不强赎  20210821      None       None
2    113528.SH        强赎   公告不强赎  20210821      None       None
3    113012.SH        强赎    公告强赎  20210818  20210903   100.6700
4    128113.SZ        强赎   公告不强赎  20210818      None       None
..         ...       ...     ...       ...       ...        ...
466  125069.SZ        强赎    公告强赎  20050429  20050422   101.8000
467  125630.SZ        强赎   公告不强赎  20040624      None       None
468  100009.SH        强赎    公告强赎  20040511  20040423   100.1300
469  125002.SZ        强赎    公告强赎  20040430  20040423   101.5000
470  125629.SZ        强赎    公告强赎  20040414  20040406   105.0000

```
