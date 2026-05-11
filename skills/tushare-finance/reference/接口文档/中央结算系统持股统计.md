# 中央结算系统持股统计

**文档ID**: 295
**原始链接**: https://tushare.pro/document/2?doc_id=295

---

## 中央结算系统持股汇总

接口：ccass_hold描述：获取中央结算系统持股汇总数据，覆盖全部历史数据，根据交易所披露时间，当日数据在下一交易日早上9点前完成入库限量：单次最大5000条数据，可循环或分页提供全部积分：用户120积分可以试用看数据，5000积分每分钟可以请求300次，8000积分以上可以请求500次每分钟，具体请参阅积分获取办法

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
<td>shareholding</td>
<td>str</td>
<td>Y</td>
<td>于中央结算系统的持股量(股)<br/>Shareholding in CCASS</td>
</tr>
<tr>
<td>hold_nums</td>
<td>str</td>
<td>Y</td>
<td>参与者数目（个）</td>
</tr>
<tr>
<td>hold_ratio</td>
<td>str</td>
<td>Y</td>
<td>占于上交所上市及交易的A股总数的百分比（%）<br/>% of the total number of A shares listed and traded on the SSE</td>
</tr>
</tbody></table>
Note:

- The total number of A shares listed and traded on the SSE of the relevant SSE-listed company used for calculating the percentage of shareholding may not have taken into account any change in connection with or as a result of any corporate actions of the relevant company and hence, may not be up-to-date. The percentage of shareholding is for reference only.

- The total number of A shares listed and traded on the SSE of the relevant SSE-listed company used for calculating the percentage of shareholding may not be equal to the actual total number of issued shares of that company.


接口用法

```

pro = ts.pro_api()

df = pro.ccass_hold(ts_code='00960.HK')

```

数据样例

```
    trade_date   ts_code  name       shareholding hold_nums hold_ratio
0     20220519  00960.HK  龍湖集團   4576163843       182      75.30
1     20220518  00960.HK  龍湖集團   4576043843       182      75.30
2     20220517  00960.HK  龍湖集團   4575955343       180      75.30
3     20220516  00960.HK  龍湖集團   4575905343       179      75.30
4     20220513  00960.HK  龍湖集團   4575905343       181      75.30

```
