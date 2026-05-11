# 期货主力与连续合约

**文档ID**: 189
**原始链接**: https://tushare.pro/document/2?doc_id=189

---

## 期货主力与连续合约

接口：fut_mapping描述：获取期货主力（或连续）合约与月合约映射数据限量：单次最大2000条，总量不限制积分：用户需要至少2000积分才可以调取，未来可能调整积分，请尽可能多积累积分。具体请参阅积分获取办法

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
<td>合约代码</td>
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
<td>连续合约代码</td>
</tr>
<tr>
<td>trade_date</td>
<td>str</td>
<td>Y</td>
<td>起始日期</td>
</tr>
<tr>
<td>mapping_ts_code</td>
<td>str</td>
<td>Y</td>
<td>期货合约代码</td>
</tr>
</tbody></table>
接口示例

```

pro = ts.pro_api()

#获取主力合约TF.CFX每日对应的月合约
df = pro.fut_mapping(ts_code='TF.CFX')

```

数据示例

```
     ts_code trade_date mapping_ts_code
0     TF.CFX   20190823      TF1912.CFX
1     TF.CFX   20190822      TF1912.CFX
2     TF.CFX   20190821      TF1912.CFX
3     TF.CFX   20190820      TF1912.CFX
4     TF.CFX   20190819      TF1912.CFX
5     TF.CFX   20190816      TF1912.CFX
6     TF.CFX   20190815      TF1912.CFX
7     TF.CFX   20190814      TF1912.CFX
8     TF.CFX   20190813      TF1912.CFX
9     TF.CFX   20190812      TF1909.CFX
10    TF.CFX   20190809      TF1909.CFX
11    TF.CFX   20190808      TF1909.CFX
12    TF.CFX   20190807      TF1909.CFX
13    TF.CFX   20190806      TF1909.CFX
14    TF.CFX   20190805      TF1909.CFX
15    TF.CFX   20190802      TF1909.CFX
16    TF.CFX   20190801      TF1909.CFX
17    TF.CFX   20190731      TF1909.CFX
18    TF.CFX   20190730      TF1909.CFX
19    TF.CFX   20190729      TF1909.CFX
20    TF.CFX   20190726      TF1909.CFX

```
