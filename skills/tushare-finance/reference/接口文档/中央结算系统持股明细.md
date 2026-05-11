# 中央结算系统持股明细

**文档ID**: 274
**原始链接**: https://tushare.pro/document/2?doc_id=274

---

## 中央结算系统持股明细

接口：ccass_hold_detail描述：获取中央结算系统机构席位持股明细，数据覆盖全历史，根据交易所披露时间，当日数据在下一交易日早上9点前完成限量：单次最大返回6000条数据，可以循环或分页提取积分：用户积8000积分可调取，每分钟可以请求300次

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
<td>股票代码 (e.g. 605009.SH)</td>
</tr>
<tr>
<td>hk_code</td>
<td>str</td>
<td>N</td>
<td>港交所代码 （e.g. 95009）</td>
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
<td>trade_date</td>
<td>str</td>
<td>Y</td>
<td>交易日期</td>
</tr>
<tr>
<td>ts_code</td>
<td>str</td>
<td>Y</td>
<td>股票代号</td>
</tr>
<tr>
<td>name</td>
<td>str</td>
<td>Y</td>
<td>股票名称</td>
</tr>
<tr>
<td>col_participant_id</td>
<td>str</td>
<td>Y</td>
<td>参与者编号</td>
</tr>
<tr>
<td>col_participant_name</td>
<td>str</td>
<td>Y</td>
<td>机构名称</td>
</tr>
<tr>
<td>col_shareholding</td>
<td>str</td>
<td>Y</td>
<td>持股量(股)</td>
</tr>
<tr>
<td>col_shareholding_percent</td>
<td>str</td>
<td>Y</td>
<td>占已发行股份/权证/单位百分比(%)</td>
</tr>
</tbody></table>
接口用法

```

pro = ts.pro_api()

df = pro.ccass_hold_detail(ts_code='00960.HK', trade_date='20211101', fields='trade_date,ts_code,col_participant_id,col_participant_name,col_shareholding')

```

数据样例

```
    trade_date   ts_code col_participant_id       col_participant_name         col_shareholding
0     20211101  00960.HK             B01777         大和资本市场香港有限公司             3000
1     20211101  00960.HK             B01977             中财证券有限公司             3000
2     20211101  00960.HK             B02068             勤丰证券有限公司             3000
3     20211101  00960.HK             B01413       京华山一国际(香港)有限公司             2500
4     20211101  00960.HK             B02120           利弗莫尔证券有限公司             2500
..         ...       ...                ...                  ...              ...
164   20211101  00960.HK             B01459         奕丰证券(香港)有限公司             3000
165   20211101  00960.HK             B01508       西证(香港)证券经纪有限公司             3000
166   20211101  00960.HK             B01511             达利证券有限公司             3000
167   20211101  00960.HK             B01657         日盛嘉富证券国际有限公司             3000
168   20211101  00960.HK             B01712             华生证券有限公司             3000

```
