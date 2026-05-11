# 东方财富App热榜

**文档ID**: 321
**原始链接**: https://tushare.pro/document/2?doc_id=321

---

## 东方财富热板

接口：dc_hot描述：获取东方财富App热榜数据，包括A股市场、ETF基金、港股市场、美股市场等等，每日盘中提取4次，收盘后4次，最晚22点提取一次。限量：单次最大2000条，可根据日期等参数循环获取全部数据积分：用户积8000积分可调取使用，积分获取办法请参阅积分获取办法注意：本接口只限个人学习和研究使用，如需商业用途，请自行联系东方财富解决数据采购问题。

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
<td>trade_date</td>
<td>str</td>
<td>N</td>
<td>交易日期</td>
</tr>
<tr>
<td>ts_code</td>
<td>str</td>
<td>N</td>
<td>TS代码</td>
</tr>
<tr>
<td>market</td>
<td>str</td>
<td>N</td>
<td>类型(A股市场、ETF基金、港股市场、美股市场)</td>
</tr>
<tr>
<td>hot_type</td>
<td>str</td>
<td>N</td>
<td>热点类型(人气榜、飙升榜)</td>
</tr>
<tr>
<td>is_new</td>
<td>str</td>
<td>N</td>
<td>是否最新（默认Y，如果为N则为盘中和盘后阶段采集，具体时间可参考rank_time字段，状态N每小时更新一次，状态Y更新时间为22：30）</td>
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
<td>data_type</td>
<td>str</td>
<td>Y</td>
<td>数据类型</td>
</tr>
<tr>
<td>ts_code</td>
<td>str</td>
<td>Y</td>
<td>股票代码</td>
</tr>
<tr>
<td>ts_name</td>
<td>str</td>
<td>Y</td>
<td>股票名称</td>
</tr>
<tr>
<td>rank</td>
<td>int</td>
<td>Y</td>
<td>排行或者热度</td>
</tr>
<tr>
<td>pct_change</td>
<td>float</td>
<td>Y</td>
<td>涨跌幅%</td>
</tr>
<tr>
<td>current_price</td>
<td>float</td>
<td>Y</td>
<td>当前价</td>
</tr>
<tr>
<td>rank_time</td>
<td>str</td>
<td>Y</td>
<td>排行榜获取时间</td>
</tr>
</tbody></table>
接口示例

```

#获取查询月份券商金股
df = pro.dc_hot(trade_date='20240415', market='A股市场',hot_type='人气榜',  fields='ts_code,ts_name,rank')

```

数据示例

```
  ts_code   ts_name  rank
0   601099.SH     太平洋     1
1   601995.SH    中金公司     2
2   002235.SZ    安妮股份     3
3   601136.SH    首创证券     4
4   600127.SH    金健米业     5
..        ...     ...   ...
95  300675.SZ     建科院    96
96  601900.SH    南方传媒    97
97  600280.SH    中央商场    98
98  300898.SZ    熊猫乳品    99
99  600519.SH    贵州茅台   100

```

数据来源
