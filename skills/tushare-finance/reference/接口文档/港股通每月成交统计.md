# 港股通每月成交统计

**文档ID**: 197
**原始链接**: https://tushare.pro/document/2?doc_id=197

---

## 港股通每月成交统计

接口：ggt_monthly描述：港股通每月成交信息，数据从2014年开始限量：单次最大1000积分：用户积5000积分可调取，请自行提高积分，具体请参阅积分获取办法

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
<td>month</td>
<td>str</td>
<td>N</td>
<td>月度（格式YYYYMM，下同，支持多个输入）</td>
</tr>
<tr>
<td>start_month</td>
<td>str</td>
<td>N</td>
<td>开始月度</td>
</tr>
<tr>
<td>end_month</td>
<td>str</td>
<td>N</td>
<td>结束月度</td>
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
<td>month</td>
<td>str</td>
<td>Y</td>
<td>交易日期</td>
</tr>
<tr>
<td>day_buy_amt</td>
<td>float</td>
<td>Y</td>
<td>当月日均买入成交金额（亿元）</td>
</tr>
<tr>
<td>day_buy_vol</td>
<td>float</td>
<td>Y</td>
<td>当月日均买入成交笔数（万笔）</td>
</tr>
<tr>
<td>day_sell_amt</td>
<td>float</td>
<td>Y</td>
<td>当月日均卖出成交金额（亿元）</td>
</tr>
<tr>
<td>day_sell_vol</td>
<td>float</td>
<td>Y</td>
<td>当月日均卖出成交笔数（万笔）</td>
</tr>
<tr>
<td>total_buy_amt</td>
<td>float</td>
<td>Y</td>
<td>总买入成交金额（亿元）</td>
</tr>
<tr>
<td>total_buy_vol</td>
<td>float</td>
<td>Y</td>
<td>总买入成交笔数（万笔）</td>
</tr>
<tr>
<td>total_sell_amt</td>
<td>float</td>
<td>Y</td>
<td>总卖出成交金额（亿元）</td>
</tr>
<tr>
<td>total_sell_vol</td>
<td>float</td>
<td>Y</td>
<td>总卖出成交笔数（万笔）</td>
</tr>
</tbody></table>
接口示例

```

pro = ts.pro_api()

#获取单月全部统计
df = pro.ggt_monthly(trade_date='201906')

#获取多月统计信息
df = pro.ggt_monthly(trade_date='201906,201907,201709')

#获取时间段统计信息
df = pro.ggt_monthly(start_date='201809', end_date='201908')
```

数据示例

```
     month  day_buy_amt  ...  total_sell_amt  total_sell_vol
0   201908        37.77  ...          450.97           96.62
1   201907        21.84  ...          382.55           80.20
2   201906        27.45  ...          379.76           84.01
3   201905        32.58  ...          473.15           96.49
4   201904        37.52  ...          574.37          107.81
5   201903        40.92  ...          734.38          137.88
6   201902        34.70  ...          601.37          102.96
7   201901        21.44  ...          481.81          121.27
8   201812        19.56  ...          299.61           65.57
9   201811        20.44  ...          496.59          112.33
10  201810        31.36  ...          453.75           96.50
11  201809        26.58  ...          334.69           66.25
12  201808        25.67  ...          772.85          122.83
13  201807        25.25  ...          569.46           98.26
14  201806        28.27  ...          689.56          119.53
15  201805        29.71  ...          716.09          118.85
16  201804        30.49  ...          502.29           86.25
17  201803        38.74  ...          879.75          141.66
18  201802        75.70  ...          787.44          105.01
```
