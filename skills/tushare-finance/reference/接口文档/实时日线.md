# 实时日线

**文档ID**: 372
**原始链接**: https://tushare.pro/document/2?doc_id=372

---

## 沪深京实时日线

接口：rt_k描述：获取实时日k线行情，支持按股票代码及股票代码通配符一次性提取全部股票实时日k线行情限量：单次最大可提取6000条数据，等同于一次提取全市场积分：本接口是单独开权限的数据，单独申请权限请参考权限列表

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
<td>Y</td>
<td>支持通配符方式，e.g. 6*.SH、301*.SZ、600000.SH</td>
</tr>
</tbody>
</table>
注：ts_code代码一定要带.SH/.SZ/.BJ后缀

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
<td>股票代码</td>
</tr>
<tr>
<td>name</td>
<td>None</td>
<td>Y</td>
<td>股票名称</td>
</tr>
<tr>
<td>pre_close</td>
<td>float</td>
<td>Y</td>
<td>昨收价</td>
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
<td>close</td>
<td>float</td>
<td>Y</td>
<td>收盘价（最新价）</td>
</tr>
<tr>
<td>vol</td>
<td>int</td>
<td>Y</td>
<td>成交量（股）</td>
</tr>
<tr>
<td>amount</td>
<td>int</td>
<td>Y</td>
<td>成交金额（元）</td>
</tr>
<tr>
<td>num</td>
<td>int</td>
<td>Y</td>
<td>开盘以来成交笔数</td>
</tr>
<tr>
<td>ask_price1</td>
<td>float</td>
<td>N</td>
<td>委托卖盘（元）</td>
</tr>
<tr>
<td>ask_volume1</td>
<td>int</td>
<td>N</td>
<td>委托卖盘（股）</td>
</tr>
<tr>
<td>bid_price1</td>
<td>float</td>
<td>N</td>
<td>委托买盘（元）</td>
</tr>
<tr>
<td>bid_volume1</td>
<td>int</td>
<td>N</td>
<td>委托买盘（股）</td>
</tr>
<tr>
<td>trade_time</td>
<td>str</td>
<td>N</td>
<td>交易时间</td>
</tr>
</tbody>
</table>
接口示例

```
#获取今日开盘以来所有创业板实时日线和成交笔数
df = pro.rt_k(ts_code='3*.SZ')

#获取今日开盘以来全市场所有股票实时日线和成交笔数（不建议一次提取全市场，可分批提取性能更好）
df = pro.rt_k(ts_code='3*.SZ,6*.SH,0*.SZ,9*.BJ')

#获取当日开盘以来单个股票实时日线和成交笔数
df = pro.rt_k(ts_code='600000.SH,000001.SZ')

```

数据示例

```
        ts_code  name      pre_close   high   open   low  close     vol      amount     num
0    601866.SH  中远海发       2.28   2.28   2.28   2.23   2.24  55845293  125364882  19904
1    601811.SH  新华文轩      15.47  15.59  15.42  15.24  15.46   4169900   64212329  10524
2    601877.SH  正泰电器      22.06  22.10  22.06  21.81  21.89   9816735  215350906  21733
3    601699.SH  潞安环能      11.78  11.77  11.77  11.56  11.61  12121234  140750449  13836
4    601858.SH  中国科传      18.45  18.77  18.56  18.36  18.56   2665300   49383660   7033
..         ...   ...        ...    ...    ...    ...    ...         ...          ...      ...
220  601880.SH  辽港股份       1.50   1.50   1.50   1.46   1.47  79855960  117767408  11820
221  601616.SH  广电电气       4.00   4.05   4.02   3.96   4.03  18984200   75975252  18220
222  601611.SH  中国核建       8.86   8.86   8.86   8.62   8.67  27793715  241360488  24970
223  601218.SH  吉鑫科技       3.00   3.02   2.99   2.96   3.00  10487500   31316964   6327
224  601966.SH  玲珑轮胎      15.31  15.38  15.38  15.18  15.27  11297200  172527086  31828

```
