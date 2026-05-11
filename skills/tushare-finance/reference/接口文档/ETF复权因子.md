# ETF复权因子

**文档ID**: 199
**原始链接**: https://tushare.pro/document/2?doc_id=199

---

## 基金复权因子

接口：fund_adj描述：获取基金复权因子，用于计算基金复权行情限量：单次最大提取2000行记录，可循环提取，数据总量不限制积分：用户积600积分可调取，超过5000积分以上频次相对较高。具体请参阅积分获取办法

复权行情实现参考：

后复权 = 当日最新价 × 当日复权因子前复权 = 当日最新价 ÷ 最新复权因子

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
<td>TS基金代码（支持多只基金输入）</td>
</tr>
<tr>
<td>trade_date</td>
<td>str</td>
<td>N</td>
<td>交易日期（格式：yyyymmdd，下同）</td>
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
<tr>
<td>offset</td>
<td>str</td>
<td>N</td>
<td>开始行数</td>
</tr>
<tr>
<td>limit</td>
<td>str</td>
<td>N</td>
<td>最大行数</td>
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
<td>ts基金代码</td>
</tr>
<tr>
<td>trade_date</td>
<td>str</td>
<td>Y</td>
<td>交易日期</td>
</tr>
<tr>
<td>adj_factor</td>
<td>float</td>
<td>Y</td>
<td>复权因子</td>
</tr>
</tbody></table>
接口使用

```

pro = ts.pro_api()

df = pro.fund_adj(ts_code='513100.SH', start_date='20190101', end_date='20190926')

```

数据示例

```
     ts_code    trade_date  adj_factor
0    513100.SH   20190926         1.0
1    513100.SH   20190925         1.0
2    513100.SH   20190924         1.0
3    513100.SH   20190923         1.0
4    513100.SH   20190920         1.0
5    513100.SH   20190919         1.0
6    513100.SH   20190918         1.0
7    513100.SH   20190917         1.0
8    513100.SH   20190916         1.0
9    513100.SH   20190912         1.0
10   513100.SH   20190911         1.0
11   513100.SH   20190910         1.0
12   513100.SH   20190909         1.0
13   513100.SH   20190906         1.0
14   513100.SH   20190905         1.0
15   513100.SH   20190904         1.0
16   513100.SH   20190903         1.0
17   513100.SH   20190902         1.0
18   513100.SH   20190830         1.0
19   513100.SH   20190829         1.0
20   513100.SH   20190828         1.0

```
