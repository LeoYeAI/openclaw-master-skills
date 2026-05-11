# 可转债转股结果

**文档ID**: 247
**原始链接**: https://tushare.pro/document/2?doc_id=247

---

## 可转债转股结果

接口：cb_share描述：获取可转债转股结果限量：单次最大2000，总量不限制权限：用户需要至少2000积分才可以调取，但有流量控制，5000积分以上频次相对较高，积分越多权限越大，具体请参阅积分获取办法

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
<td>转债代码，支持多值输入</td>
</tr>
<tr>
<td>ann_date</td>
<td>str</td>
<td>Y</td>
<td>公告日期（YYYYMMDD格式，下同）</td>
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
<td>债券代码</td>
</tr>
<tr>
<td>bond_short_name</td>
<td>str</td>
<td>Y</td>
<td>债券简称</td>
</tr>
<tr>
<td>publish_date</td>
<td>str</td>
<td>Y</td>
<td>公告日期</td>
</tr>
<tr>
<td>end_date</td>
<td>str</td>
<td>Y</td>
<td>统计截止日期</td>
</tr>
<tr>
<td>issue_size</td>
<td>float</td>
<td>Y</td>
<td>可转债发行总额</td>
</tr>
<tr>
<td>convert_price_initial</td>
<td>float</td>
<td>Y</td>
<td>初始转换价格</td>
</tr>
<tr>
<td>convert_price</td>
<td>float</td>
<td>Y</td>
<td>本次转换价格</td>
</tr>
<tr>
<td>convert_val</td>
<td>float</td>
<td>Y</td>
<td>本次转股金额</td>
</tr>
<tr>
<td>convert_vol</td>
<td>float</td>
<td>Y</td>
<td>本次转股数量</td>
</tr>
<tr>
<td>convert_ratio</td>
<td>float</td>
<td>Y</td>
<td>本次转股比例</td>
</tr>
<tr>
<td>acc_convert_val</td>
<td>float</td>
<td>Y</td>
<td>累计转股金额</td>
</tr>
<tr>
<td>acc_convert_vol</td>
<td>float</td>
<td>Y</td>
<td>累计转股数量</td>
</tr>
<tr>
<td>acc_convert_ratio</td>
<td>float</td>
<td>Y</td>
<td>累计转股比例</td>
</tr>
<tr>
<td>remain_size</td>
<td>float</td>
<td>Y</td>
<td>可转债剩余金额</td>
</tr>
<tr>
<td>total_shares</td>
<td>float</td>
<td>Y</td>
<td>转股后总股本</td>
</tr>
</tbody></table>
接口示例

```

pro = ts.pro_api(your token)
#获取可转债转股结果
df = pro.cb_share(ts_code="113001.SH,110027.SH",fields="ts_code,end_date,convert_price,convert_val,convert_ratio,acc_convert_ratio")

```

数据示例

```
        ts_code    end_date convert_price   convert_val convert_ratio acc_convert_ratio
0    110027.SH  2015-02-16       12.0000  117572928.00      2.939323           99.9126
1    110027.SH  2015-02-13       12.0000  521211288.00     13.030282           96.9733
2    110027.SH  2015-02-12       12.0000  486077580.00     12.151940           83.9430
3    110027.SH  2015-02-11       12.0000  304362204.00      7.609055           71.7910
4    110027.SH  2015-02-10       12.0000  334752476.00      8.368812           64.1820
..         ...         ...           ...           ...           ...               ...
244  113001.SH  2010-12-10        3.7800       5998.86      0.000015            0.0002
245  113001.SH  2010-12-09        3.7800       5998.86      0.000015            0.0002
246  113001.SH  2010-12-06        3.7800      18994.50      0.000047            0.0002
247  113001.SH  2010-12-03        3.7800      12991.86      0.000032            0.0001
248  113001.SH  2010-12-02        3.7800      33982.20      0.000085            0.0001

```
